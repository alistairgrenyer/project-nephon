from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class MappingType(str, Enum):
    EXACT = "exact"
    EQUIVALENT = "equivalent"
    IMPLIES = "implies"
    RELATED = "related"
    NEW = "new"


class InterpretationStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"


class Interpretation(BaseModel):
    """
    First-class model capturing natural language expression interpretation into canonical proposition atom.
    Prevents invisible raw sentence -> proposition mutations.
    """
    id: UUID = Field(default_factory=uuid4)
    expression_id: UUID
    proposition_id: UUID
    mapping_type: MappingType
    confidence: float | None = None
    interpreter: str  # e.g. "fixture:exp1", "llm:gemini-3.5-pro"
    rationale: str
