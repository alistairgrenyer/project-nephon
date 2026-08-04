from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, Field
from nephon_contracts.enums import BeliefStatus, ProvenanceSupportStatus
from nephon_graph.core.claims import Claim

__all__ = [
    "BeliefStatus",
    "ProvenanceSupportStatus",
    "BeliefState",
]


class BeliefState(BaseModel):
    """
    Evaluated belief status for a canonical proposition atom within a target context.
    """
    proposition_id: UUID
    status: BeliefStatus
    positive_claims: list[Claim] = Field(default_factory=list)
    negative_claims: list[Claim] = Field(default_factory=list)
    explanation: str = ""

