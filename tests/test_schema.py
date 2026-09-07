"""Schema-contract tests for ClassificationResult (Day 5).

These pin the output shape so a later change to the model or the prompt can't
silently break the contract the endpoint promises.
"""

import pytest
from pydantic import ValidationError

from app.models import ClassificationResult, IssueCategory, Urgency

MINIMAL = dict(
    category="plumbing",
    urgency="normal",
    llm_urgency="normal",
    recommended_action="Dispatch a plumber.",
    confidence=0.7,
)


def test_minimal_valid_result():
    r = ClassificationResult(**MINIMAL)
    assert r.category is IssueCategory.PLUMBING
    assert r.urgency is Urgency.NORMAL
    assert r.missing_information == []
    assert r.emergency_override_applied is False
    assert r.matched_emergency_rule is None
    assert r.trace is None


@pytest.mark.parametrize("bad_confidence", [-0.1, 1.1, 2.0])
def test_confidence_must_be_a_probability(bad_confidence):
    with pytest.raises(ValidationError):
        ClassificationResult(**{**MINIMAL, "confidence": bad_confidence})


def test_category_must_be_in_the_enum():
    with pytest.raises(ValidationError):
        ClassificationResult(**{**MINIMAL, "category": "flooding"})


def test_urgency_must_be_in_the_enum():
    with pytest.raises(ValidationError):
        ClassificationResult(**{**MINIMAL, "urgency": "critical"})


def test_json_round_trip_is_stable():
    r = ClassificationResult(**MINIMAL)
    assert ClassificationResult.model_validate_json(r.model_dump_json()) == r


def test_output_json_keys_are_the_documented_contract():
    keys = set(ClassificationResult(**MINIMAL).model_dump().keys())
    assert keys == {
        "category",
        "urgency",
        "llm_urgency",
        "missing_information",
        "recommended_action",
        "confidence",
        "emergency_override_applied",
        "matched_emergency_rule",
        "trace",
    }
