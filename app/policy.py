"""Deterministic emergency-override policy.

See DECISIONS.md (2026-09-07): the LLM classifies, but a hardcoded Python
policy layer can override its urgency on safety-critical cases. If a complaint
matches one of the five categories below, urgency is forced to `emergency`
regardless of what the model returned — a missed gas leak is not an acceptable
failure mode, and we are not willing to let a probabilistic model be the only
thing standing between a tenant and that outcome.

The five categories (locked in the Day 2 fixtures and DAILY_PLAN.md):
  1. Gas leak / gas smell
  2. Fire, sparks, burning smell from electrical
  3. Active flooding / water pouring in
  4. No heat during freezing weather
  5. Structural collapse (ceiling, floor, wall)

Matching is intentionally keyword-based and conservative-to-fire (favouring
false positives): a human reviews every emergency anyway, so the cost of an
over-trigger is low and the cost of a miss is high. This is a Phase 1
stopgap — a real system would want something less brittle, tracked for later.
"""

import re
from dataclasses import dataclass
from typing import List, Optional

from app.models import Urgency


@dataclass(frozen=True)
class EmergencyRule:
    name: str
    # Any one pattern matching triggers the rule.
    patterns: List[re.Pattern]

    def matches(self, text: str) -> bool:
        return any(p.search(text) for p in self.patterns)


def _p(*words: str) -> List[re.Pattern]:
    return [re.compile(w, re.IGNORECASE) for w in words]


EMERGENCY_RULES: List[EmergencyRule] = [
    EmergencyRule(
        name="gas_leak",
        patterns=_p(
            r"\bgas\b.{0,30}\b(leak|smell|odou?r)\b",
            r"\b(smell|smelling|odou?r)\b.{0,30}\bgas\b",
            r"\bnatural gas\b",
            r"\brotten egg\b",
        ),
    ),
    EmergencyRule(
        name="fire_or_sparks",
        patterns=_p(
            r"\bspark(s|ing|ed)?\b",
            r"\bfire\b",
            r"\bflame(s)?\b",
            r"\bsmoke\b(?!\s*detector)",
            r"\bburning smell\b",
            r"\bsmell(s|ing)?\s+(of\s+)?burning\b",
            r"\boutlet\b.{0,30}\b(hot|melt|burn)",
        ),
    ),
    EmergencyRule(
        name="active_flooding",
        patterns=_p(
            r"\bflood(ing|ed)?\b",
            r"\bwater\b.{0,30}\b(pouring|gushing|pooling fast|spreading fast)\b",
            r"\bpouring\b.{0,30}\bwater\b",
            r"\bceiling\b.{0,30}\b(pouring|gushing)\b",
        ),
    ),
    EmergencyRule(
        name="no_heat_freezing",
        patterns=_p(
            r"\bno heat\b.{0,60}\b(freezing|below freezing|frigid|winter|snow|ice|cold)\b",
            r"\b(freezing|below freezing|frigid)\b.{0,60}\bno heat\b",
            r"\bheat(ing)?\b.{0,20}\b(is )?(not working|broken|out|off)\b.{0,60}\b(freezing|below freezing)\b",
        ),
    ),
    EmergencyRule(
        name="structural_collapse",
        patterns=_p(
            r"\b(ceiling|floor|wall|balcony|staircase|stairs)\b.{0,30}\b(collaps\w*|cav(e|ed|ing)\s+in|fell|caved|giving way|gave way)\b",
            r"\bcollaps\w*\b.{0,30}\b(ceiling|floor|wall)\b",
            r"\bhole\b.{0,20}\b(in|above)\b.{0,20}\b(ceiling|floor)\b",
        ),
    ),
]


@dataclass(frozen=True)
class PolicyDecision:
    """Outcome of running the emergency-override policy against a complaint."""

    override_applied: bool
    urgency: Urgency
    matched_rule: Optional[str] = None


def apply_emergency_override(description: str, llm_urgency: Urgency) -> PolicyDecision:
    """Force urgency to EMERGENCY if the description matches an emergency rule.

    Returns the (possibly unchanged) urgency plus whether an override fired and
    which rule matched, so callers can surface it in the trace / output.
    """
    for rule in EMERGENCY_RULES:
        if rule.matches(description):
            return PolicyDecision(
                override_applied=llm_urgency != Urgency.EMERGENCY,
                urgency=Urgency.EMERGENCY,
                matched_rule=rule.name,
            )
    return PolicyDecision(override_applied=False, urgency=llm_urgency, matched_rule=None)
