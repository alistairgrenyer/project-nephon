from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class KnowledgeEvent(BaseModel):
    """
    Append-only knowledge event with full-envelope tracking.
    """
    event_id: UUID = Field(default_factory=uuid4)
    sequence: int = 0  # Monotonically increasing sequence index assigned by EventStore
    aggregate_id: str
    aggregate_version: int
    event_type: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    causation_id: UUID | None = None
    correlation_id: UUID | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
