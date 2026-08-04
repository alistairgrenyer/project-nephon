from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from nephon_contracts.contexts import Context
from nephon_contracts.enums import BeliefStatus, ExecutionState, GovernanceDisposition, RiskClass


class ActionRequest(BaseModel):
    contract_version: str = "1.0"
    project_id: str
    environment_id: str
    session_id: UUID = Field(default_factory=uuid4)

    capability_id: str
    capability_version: str
    target: str
    parameters: dict[str, Any] = Field(default_factory=dict)

    context: Context = Field(default_factory=Context.universal)
    evidence_refs: tuple[UUID, ...] = ()


class ConstitutionalDecision(BaseModel):
    decision_id: UUID = Field(default_factory=uuid4)
    disposition: GovernanceDisposition
    belief_status: BeliefStatus
    governing_declarations: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    rationale: str = ""
    # Note: authorization_handle is kept server-side inside NephonHarness, NEVER sent to worker


class ExecutionReceipt(BaseModel):
    execution_id: UUID = Field(default_factory=uuid4)
    decision_id: UUID
    capability_id: str
    state: ExecutionState
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    result_summary: dict[str, Any] | None = None


class ExecutionAuthorizationPayload(BaseModel):
    token_version: int = 1
    issuer: str = "nephon_constitutional_gateway"
    audience: str = "nephon_execution_broker"
    key_id: str = "gateway-ed25519-v1"

    project_id: str
    environment_id: str
    broker_id: str

    decision_id: UUID
    capability_id: str
    capability_version: str
    capability_schema_hash: str  # Hash of registered Pydantic request model schema
    request_hash: str             # NEPHON_CANONICAL_JSON_V1 hash over validated target & parameters

    context_hash: str
    evidence_snapshot_hash: str
    policy_version: str

    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    not_before: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: datetime
    nonce: UUID = Field(default_factory=uuid4)


class SignedExecutionToken(BaseModel):
    payload: ExecutionAuthorizationPayload
    signature_bytes: str  # Ed25519 signature over UTF-8 NEPHON_CANONICAL_JSON_V1 of payload


class ObservationClaim(BaseModel):
    observation_id: UUID = Field(default_factory=uuid4)
    predicate: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provenance_ref: str
