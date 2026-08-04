from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ContextConstraintKind(str, Enum):
    ANY = "any"          # Deliberately universal across this dimension
    EXACT = "exact"      # Specific required value
    UNKNOWN = "unknown"  # Not established by source (restricts automatic application)


class ContextConstraint(BaseModel):
    kind: ContextConstraintKind
    value: str | None = None

    @classmethod
    def any(cls) -> ContextConstraint:
        return cls(kind=ContextConstraintKind.ANY)

    @classmethod
    def exact(cls, value: str) -> ContextConstraint:
        return cls(kind=ContextConstraintKind.EXACT, value=value)

    @classmethod
    def unknown(cls) -> ContextConstraint:
        return cls(kind=ContextConstraintKind.UNKNOWN)


class Context(BaseModel):
    project: ContextConstraint = Field(default_factory=ContextConstraint.any)
    environment: ContextConstraint = Field(default_factory=ContextConstraint.any)
    operation: ContextConstraint = Field(default_factory=ContextConstraint.any)
    perspective: ContextConstraint = Field(default_factory=ContextConstraint.any)
    authority: ContextConstraint = Field(default_factory=ContextConstraint.any)
    ontology_version: ContextConstraint = Field(default_factory=ContextConstraint.any)
    valid_from: datetime | None = None  # None = -infinity
    valid_until: datetime | None = None  # None = +infinity

    @classmethod
    def universal(cls) -> Context:
        return cls(
            project=ContextConstraint.any(),
            environment=ContextConstraint.any(),
            operation=ContextConstraint.any(),
            perspective=ContextConstraint.any(),
            authority=ContextConstraint.any(),
            ontology_version=ContextConstraint.any(),
            valid_from=None,
            valid_until=None,
        )
