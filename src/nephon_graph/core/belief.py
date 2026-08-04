from __future__ import annotations

from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field
from nephon_graph.core.claims import Claim


class BeliefStatus(str, Enum):
    UNKNOWN = "unknown"
    SUPPORTED = "supported"
    REJECTED = "rejected"
    CONFLICTED = "conflicted"


class ProvenanceSupportStatus(str, Enum):
    VALID = "valid"
    CURRENTLY_UNSUPPORTED = "currently_unsupported"
    DERIVATION_BROKEN = "derivation_broken"


class BeliefState(BaseModel):
    """
    Evaluated belief status for a canonical proposition atom within a target context.
    """
    proposition_id: UUID
    status: BeliefStatus
    positive_claims: list[Claim] = Field(default_factory=list)
    negative_claims: list[Claim] = Field(default_factory=list)
    explanation: str = ""
