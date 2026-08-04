from __future__ import annotations

from pydantic import BaseModel, Field


class OntologyType(BaseModel):
    name: str
    parents: list[str] = Field(default_factory=list)


class RoleDefinition(BaseModel):
    role_name: str
    allowed_types: list[str] = Field(default_factory=list)


class PredicateDefinition(BaseModel):
    name: str
    description: str = ""
    roles: list[RoleDefinition] = Field(default_factory=list)
