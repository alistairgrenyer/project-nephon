from __future__ import annotations

from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Entity(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    entity_type: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    attributes: dict[str, str] = Field(default_factory=dict)
