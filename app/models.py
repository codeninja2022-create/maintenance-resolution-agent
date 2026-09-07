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
    """The structured output returned for a given Issue."""

    category: IssueCategory
    urgency: Urgency
    missing_information: List[str] = Field(default_factory=list)
    recommended_action: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    trace: Optional[ClassificationTrace] = None
