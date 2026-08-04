from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field

from nephon_contracts.enums import ExecutionState


class TokenReplayError(Exception):
    """Raised when an authorization token nonce is re-submitted or double-redeemed."""
    pass


class ExecutionRecord(BaseModel):
    token_nonce: UUID
    decision_id: UUID
    capability_id: str
    request_hash: str
    state: ExecutionState
    claimed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    result_summary: dict[str, Any] | None = None
    error_message: str | None = None


class DurableNonceManager:
    """
    Durable Nonce State Manager for Execution Broker.
    Enforces atomic compare-and-swap nonce redemption to prevent token replay attacks.
    Maintains durable records across execution lifecycle states.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._records: dict[UUID, ExecutionRecord] = {}

    def claim_nonce(self, nonce: UUID, decision_id: UUID, capability_id: str, request_hash: str) -> ExecutionRecord:
        """
        Atomic compare-and-swap transition: AUTHORIZED -> CLAIMED.
        Raises TokenReplayError if nonce has already been redeemed.
        """
        with self._lock:
            if nonce in self._records:
                existing = self._records[nonce]
                raise TokenReplayError(
                    f"Token nonce {nonce} has already been redeemed. Current state: '{existing.state.value}'."
                )

            record = ExecutionRecord(
                token_nonce=nonce,
                decision_id=decision_id,
                capability_id=capability_id,
                request_hash=request_hash,
                state=ExecutionState.CLAIMED,
            )
            self._records[nonce] = record
            return record

    def mark_executing(self, nonce: UUID) -> None:
        with self._lock:
            if nonce in self._records:
                self._records[nonce].state = ExecutionState.EXECUTING

    def mark_succeeded(self, nonce: UUID, result_summary: dict[str, Any] | None = None) -> None:
        with self._lock:
            if nonce in self._records:
                rec = self._records[nonce]
                rec.state = ExecutionState.SUCCEEDED
                rec.completed_at = datetime.now(timezone.utc)
                rec.result_summary = result_summary

    def mark_failed(self, nonce: UUID, error_message: str) -> None:
        with self._lock:
            if nonce in self._records:
                rec = self._records[nonce]
                rec.state = ExecutionState.FAILED
                rec.completed_at = datetime.now(timezone.utc)
                rec.error_message = error_message

    def mark_requires_reconciliation(self, nonce: UUID, reason: str) -> None:
        with self._lock:
            if nonce in self._records:
                rec = self._records[nonce]
                rec.state = ExecutionState.REQUIRES_RECONCILIATION
                rec.error_message = reason

    def get_record(self, nonce: UUID) -> ExecutionRecord | None:
        with self._lock:
            return self._records.get(nonce)

    def get_unreconciled_records(self) -> list[ExecutionRecord]:
        with self._lock:
            return [r for r in self._records.values() if r.state == ExecutionState.EXECUTING]
