from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Expression(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    text: str
    source_uri: str | None = None
    speaker_or_author: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

