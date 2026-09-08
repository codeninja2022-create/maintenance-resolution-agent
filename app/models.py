"""Core domain models for the Maintenance Resolution Intelligence Agent.

Phase 1 scope only: the shape of an incoming issue, and the shape of the
structured classification output. No vendor, retrieval, or workflow models
yet — those arrive in later phases (see ROADMAP.md).
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Urgency(str, Enum):
    EMERGENCY = "emergency"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class IssueCategory(str, Enum):
    WATER_LEAK = "water_leak"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    HVAC = "hvac"
    APPLIANCE = "appliance"
    STRUCTURAL = "structural"
    PEST = "pest"
    ACCESS_LOCK = "access_lock"
    GAS = "gas"
    OTHER = "other"
    # Not a maintenance request at all (noise complaint, billing question, etc.).
    # Distinct from OTHER, which is an unclear *maintenance* issue. See
    # DECISIONS.md 2026-09-08.
    NOT_MAINTENANCE = "not_maintenance"


class Issue(BaseModel):
    """An incoming, possibly unclear, tenant maintenance complaint."""

    description: str = Field(..., min_length=1, description="Free-text complaint as submitted by the tenant.")
    property: str = Field(..., description="Property identifier or address.")
    unit: str = Field(..., description="Unit identifier within the property.")
    attachments: List[str] = Field(default_factory=list, description="Attachment references (e.g. photo URLs/IDs), if any.")
    reporter: str = Field(..., description="Who submitted this — e.g. 'tenant' or 'manager'. No PII beyond this role label.")


class ClassificationTrace(BaseModel):
    """Basic cost/trace fields, captured from Day 3 onward.

    Not full tracing (Braintrust/Langfuse) — just enough structured metadata
    to reason about cost and latency before a real tracing tool is introduced.
    """

    request_id: str
    model_name: str
    latency_ms: float
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    estimated_cost: Optional[float] = None


class ClassificationResult(BaseModel):
    """The structured output returned for a given Issue.

    `urgency` is the final urgency after the deterministic emergency-override
    policy (app/policy.py) has run. `llm_urgency` is what the model returned
    before the policy. When they differ, `emergency_override_applied` is True.
    `matched_emergency_rule` names the rule that engaged, if any — it can be set
    even when no override was needed (the model and the policy agreed).
    """

    category: IssueCategory
    urgency: Urgency
    llm_urgency: Urgency
    missing_information: List[str] = Field(default_factory=list)
    recommended_action: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    emergency_override_applied: bool = False
    matched_emergency_rule: Optional[str] = None
    trace: Optional[ClassificationTrace] = None
