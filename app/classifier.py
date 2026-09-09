"""Classifier abstraction.

Lets the API depend on an interface, not a specific model provider, so the
underlying model can change later without touching the endpoint.

    Classifier
      ├── MockClassifier      (Day 1 — deterministic, no API calls, for fast tests)
      └── AnthropicClassifier (Day 3 — real LLM-backed implementation)

Only one real implementation is planned for Phase 1 (locked stack: "one
hosted LLM"). This abstraction exists so that swap is cheap later, not to
support multiple providers now — see DECISIONS.md re: LiteLLM being deferred.
"""

import os
import time
import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

import anthropic
from pydantic import BaseModel, Field, ValidationError

from app.models import (
    ClassificationResult,
    ClassificationTrace,
    IssueCategory,
    Issue,
    Urgency,
)
from app.policy import apply_emergency_override
from app.prompt import SYSTEM_PROMPT, build_user_message
from app.redaction import redact_all, redact_text

DEFAULT_MODEL = os.environ.get("RESOLVLY_CLASSIFIER_MODEL", "claude-opus-5")

# USD per 1M tokens (input, output). Used for a rough cost estimate in the
# trace — not billing-accurate (ignores cache tiers). Update when prices change.
_PRICING = {
    "claude-opus-5": (5.0, 25.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-opus-4-7": (5.0, 25.0),
    "claude-sonnet-5": (2.0, 10.0),
    "claude-haiku-4-5": (1.0, 5.0),
}


class Classifier(ABC):
    """Interface every classifier implementation must satisfy."""

    @abstractmethod
    def classify(self, issue: Issue) -> ClassificationResult:
        """Given an Issue, return a structured ClassificationResult."""
        raise NotImplementedError


class MockClassifier(Classifier):
    """Deterministic, no-API-call classifier for fast unit tests.

    Returns a fixed, valid ClassificationResult regardless of input, purely
    so the rest of the system (endpoint, schema validation, tests) can be
    built and tested before a real LLM call is wired in on Day 3.
    """

    def classify(self, issue: Issue) -> ClassificationResult:
        return ClassificationResult(
            category="other",
            urgency="low",
            llm_urgency="low",
            urgency_rationale="Mock classifier — fixed low urgency, no real assessment.",
            missing_information=[],
            recommended_action="Mock response — no real classification performed.",
            confidence=0.5,
            trace=None,
        )


class _LLMClassification(BaseModel):
    """Exactly what we ask the model to return — no trace, no policy output.

    Kept separate from ClassificationResult so the model's job stays small and
    the fields it must not touch (trace, emergency-override) are added by us.
    """

    category: IssueCategory
    urgency: Urgency
    urgency_rationale: str  # one line, always populated
    missing_information: List[str]  # empty list when the complaint is already actionable
    recommended_action: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class ClassifierError(RuntimeError):
    """Raised when the model could not produce a valid classification."""


class AnthropicClassifier(Classifier):
    """Real LLM-backed classifier.

    Flow: prompt the model for a `_LLMClassification` (structured output, with a
    bounded retry on malformed responses) → apply the deterministic emergency
    override → redact PII from returned text → attach trace/cost fields.
    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        client: Optional[anthropic.Anthropic] = None,
        max_attempts: int = 3,
        max_tokens: int = 2000,
    ):
        # anthropic.Anthropic() reads ANTHROPIC_API_KEY from the environment.
        self._client = client or anthropic.Anthropic()
        self._model = model
        self._max_attempts = max_attempts
        self._max_tokens = max_tokens

    def classify(self, issue: Issue) -> ClassificationResult:
        started = time.perf_counter()
        llm_result, response = self._call_model_with_retry(issue)
        latency_ms = (time.perf_counter() - started) * 1000

        # Deterministic safety layer: may force urgency to emergency.
        decision = apply_emergency_override(issue.description, llm_result.urgency)

        trace = self._build_trace(response, latency_ms)

        return ClassificationResult(
            category=llm_result.category,
            urgency=decision.urgency,
            llm_urgency=llm_result.urgency,
            urgency_rationale=redact_text(llm_result.urgency_rationale),
            missing_information=redact_all(llm_result.missing_information),
            recommended_action=redact_text(llm_result.recommended_action),
            confidence=llm_result.confidence,
            emergency_override_applied=decision.override_applied,
            matched_emergency_rule=decision.matched_rule,
            trace=trace,
        )

    # -- internals ---------------------------------------------------------

    def _call_model_with_retry(self, issue: Issue):
        user_message = build_user_message(issue)
        messages = [{"role": "user", "content": user_message}]
        last_error: Optional[Exception] = None

        for attempt in range(1, self._max_attempts + 1):
            try:
                response = self._client.messages.parse(
                    model=self._model,
                    max_tokens=self._max_tokens,
                    system=SYSTEM_PROMPT,
                    messages=messages,
                    output_format=_LLMClassification,
                )
            except anthropic.APIStatusError as e:
                # 4xx (bad request, auth, not found) won't fix themselves.
                if e.status_code and e.status_code < 500 and e.status_code != 429:
                    raise ClassifierError(f"API error {e.status_code}: {e.message}") from e
                last_error = e
                continue
            except ValidationError as e:
                # messages.parse raises this when the model's JSON doesn't match
                # the schema — the case the retry exists for.
                last_error = e
                messages = _retry_messages(user_message, "(output did not match schema)")
                continue

            parsed = response.parsed_output
            if parsed is not None:
                return parsed, response

            # Parsed to nothing: feed it back and ask for a clean retry.
            last_error = ClassifierError("model returned output that did not match the schema")
            messages = _retry_messages(user_message, _first_text(response) or "(no output)")

        raise ClassifierError(
            f"Model did not return a valid classification after {self._max_attempts} attempts"
        ) from last_error

    def _build_trace(self, response, latency_ms: float) -> ClassificationTrace:
        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "input_tokens", None)
        output_tokens = getattr(usage, "output_tokens", None)
        request_id = getattr(response, "_request_id", None) or f"local-{uuid.uuid4()}"

        return ClassificationTrace(
            request_id=request_id,
            model_name=getattr(response, "model", self._model),
            latency_ms=round(latency_ms, 1),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost=_estimate_cost(self._model, input_tokens, output_tokens),
        )


def _retry_messages(user_message: str, prior_output: str) -> list:
    """Conversation to send after a bad response — show it back, ask for a fix."""
    return [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": prior_output},
        {
            "role": "user",
            "content": (
                "That response did not match the required schema. "
                "Return only the structured classification, nothing else."
            ),
        },
    ]


def _first_text(response) -> Optional[str]:
    for block in getattr(response, "content", []) or []:
        if getattr(block, "type", None) == "text":
            return block.text
    return None


def _estimate_cost(model: str, input_tokens, output_tokens) -> Optional[float]:
    if input_tokens is None or output_tokens is None:
        return None
    prices = _PRICING.get(model)
    if prices is None:
        return None
    in_price, out_price = prices
    cost = (input_tokens * in_price + output_tokens * out_price) / 1_000_000
    return round(cost, 6)
