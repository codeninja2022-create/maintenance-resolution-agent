"""AnthropicClassifier tests with a fake client — no network, no API key.

Covers the parts that are ours, not the model's: emergency override wiring,
PII redaction of returned text, trace/cost population, and the malformed-output
retry.
"""

import pytest
from pydantic import ValidationError

from app.classifier import AnthropicClassifier, ClassifierError, _LLMClassification
from app.models import Issue, Urgency


class FakeUsage:
    def __init__(self, input_tokens=1200, output_tokens=80):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class FakeTextBlock:
    type = "text"

    def __init__(self, text):
        self.text = text


class FakeParsedResponse:
    """Mimics the shape AnthropicClassifier reads off a messages.parse result."""

    def __init__(self, parsed_output, *, model="claude-opus-5", raw_text="{}"):
        self.parsed_output = parsed_output
        self.usage = FakeUsage()
        self.model = model
        self._request_id = "req_fake_123"
        self.content = [FakeTextBlock(raw_text)]


class FakeMessages:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = 0

    def parse(self, **kwargs):
        self.calls += 1
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class FakeClient:
    def __init__(self, responses):
        self.messages = FakeMessages(responses)


def make_issue(description: str) -> Issue:
    return Issue(
        description=description,
        property="12 Maple St",
        unit="3B",
        attachments=[],
        reporter="tenant",
    )


def test_emergency_override_beats_the_model():
    llm = _LLMClassification(
        category="gas",
        urgency="low",  # model got it wrong
        missing_information=[],
        recommended_action="Schedule a routine visit.",
        confidence=0.4,
    )
    clf = AnthropicClassifier(client=FakeClient([FakeParsedResponse(llm)]))
    result = clf.classify(make_issue("I smell gas near the stove, getting stronger."))

    assert result.urgency == Urgency.EMERGENCY
    assert result.emergency_override_applied is True
    assert result.matched_emergency_rule == "gas_leak"


def test_pii_is_redacted_from_returned_text():
    llm = _LLMClassification(
        category="plumbing",
        urgency="normal",
        missing_information=["Confirm callback number 555-123-4567"],
        recommended_action="Call the tenant at (555) 987-6543 or tenant@example.com.",
        confidence=0.7,
    )
    clf = AnthropicClassifier(client=FakeClient([FakeParsedResponse(llm)]))
    result = clf.classify(make_issue("Sink drips slowly."))

    assert "555" not in result.recommended_action
    assert "@" not in result.recommended_action
    assert "555-123-4567" not in result.missing_information[0]


def test_trace_and_cost_are_populated():
    llm = _LLMClassification(
        category="appliance",
        urgency="normal",
        missing_information=[],
        recommended_action="Dispatch an appliance technician.",
        confidence=0.8,
    )
    clf = AnthropicClassifier(client=FakeClient([FakeParsedResponse(llm)]))
    result = clf.classify(make_issue("Dishwasher won't drain."))

    assert result.trace is not None
    assert result.trace.request_id == "req_fake_123"
    assert result.trace.model_name == "claude-opus-5"
    assert result.trace.latency_ms >= 0
    assert result.trace.input_tokens == 1200
    assert result.trace.output_tokens == 80
    # (1200 * 5 + 80 * 25) / 1e6
    assert result.trace.estimated_cost == pytest.approx(0.008)


def test_retry_on_malformed_then_success():
    good = _LLMClassification(
        category="hvac",
        urgency="normal",
        missing_information=[],
        recommended_action="Send HVAC tech to inspect the unit.",
        confidence=0.75,
    )
    client = FakeClient(
        [
            FakeParsedResponse(None, raw_text="not json"),  # malformed
            FakeParsedResponse(good),
        ]
    )
    clf = AnthropicClassifier(client=client)
    result = clf.classify(make_issue("AC rattling loudly."))

    assert client.messages.calls == 2
    assert result.category.value == "hvac"


def test_retry_when_parse_raises_validation_error():
    good = _LLMClassification(
        category="pest",
        urgency="normal",
        missing_information=[],
        recommended_action="Schedule pest control.",
        confidence=0.9,
    )
    bad = ValidationError.from_exception_data("_LLMClassification", [])
    client = FakeClient([bad, FakeParsedResponse(good)])
    clf = AnthropicClassifier(client=client)
    result = clf.classify(make_issue("Mouse droppings in the cabinet."))

    assert client.messages.calls == 2
    assert result.category.value == "pest"


def test_gives_up_after_max_attempts():
    client = FakeClient([FakeParsedResponse(None) for _ in range(3)])
    clf = AnthropicClassifier(client=client, max_attempts=3)
    with pytest.raises(ClassifierError):
        clf.classify(make_issue("Something vague."))
    assert client.messages.calls == 3
