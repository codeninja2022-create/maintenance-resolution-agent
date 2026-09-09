"""Emergency-override policy tests (offline).

Each of the five hardcoded emergency categories must force urgency to
`emergency` regardless of the LLM's output — checked against the Day 2 fixture
descriptions that were written for exactly these cases.
"""

import json
from pathlib import Path

import pytest

from app.models import Urgency
from app.policy import apply_emergency_override

CASES = {
    c["id"]: c
    for c in json.loads((Path(__file__).parent / "fixtures" / "cases.json").read_text())
}


@pytest.mark.parametrize(
    "case_id, expected_rule",
    [
        ("case_01", "gas_leak"),
        ("case_02", "active_flooding"),
        ("case_03", "no_heat_freezing"),
        ("case_04", "fire_or_sparks"),
        ("case_05", "structural_collapse"),
    ],
)
def test_emergency_rules_force_emergency_even_when_llm_says_low(case_id, expected_rule):
    description = CASES[case_id]["description"]
    decision = apply_emergency_override(description, Urgency.LOW)
    assert decision.urgency == Urgency.EMERGENCY
    assert decision.override_applied is True
    assert decision.matched_rule == expected_rule


def test_adversarial_gas_case_still_forces_emergency_when_llm_downplays_it():
    """case_20: gas smell framed casually + bundled with a trivial complaint.

    Proves the override is load-bearing — it fires on *disagreement*, not just
    when the LLM already agrees. Simulates the LLM's tone-based read as 'low'.
    """
    decision = apply_emergency_override(CASES["case_20"]["description"], Urgency.LOW)
    assert decision.urgency == Urgency.EMERGENCY
    assert decision.override_applied is True
    assert decision.matched_rule == "gas_leak"


def test_override_not_flagged_when_llm_already_said_emergency():
    decision = apply_emergency_override(CASES["case_01"]["description"], Urgency.EMERGENCY)
    assert decision.urgency == Urgency.EMERGENCY
    assert decision.override_applied is False
    assert decision.matched_rule == "gas_leak"


@pytest.mark.parametrize("case_id", ["case_06", "case_07", "case_08", "case_12"])
def test_clean_non_emergency_cases_are_left_alone(case_id):
    description = CASES[case_id]["description"]
    decision = apply_emergency_override(description, Urgency.NORMAL)
    assert decision.urgency == Urgency.NORMAL
    assert decision.override_applied is False
    assert decision.matched_rule is None
