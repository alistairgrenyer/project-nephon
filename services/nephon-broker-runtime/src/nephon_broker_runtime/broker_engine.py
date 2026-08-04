from __future__ import annotations

import asyncio
import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, ValidationError

from nephon_contracts.canonical_json import compute_nephon_canonical_json_v1, compute_request_hash
from nephon_contracts.dto import ExecutionReceipt, SignedExecutionToken
from nephon_contracts.enums import ExecutionState

from nephon_broker_runtime.adapter_protocol import CapabilityAdapter
from nephon_broker_runtime.nonce_manager import DurableNonceManager, TokenReplayError
from nephon_broker_runtime.verifier import BrokerTokenVerifier, TokenValidationError


class BrokerEngineError(Exception):
    """Raised when broker engine initialization or execution encounters an unrecoverable failure."""
    pass


def compute_schema_hash(model_class: type[BaseModel]) -> str:
    """Computes SHA-256 hash over deterministic JSON schema of Pydantic request model."""
    schema_dict = model_class.model_json_schema()
    canonical_schema = compute_nephon_canonical_json_v1(schema_dict)
    return hashlib.sha256(canonical_schema.encode("utf-8")).hexdigest()


class ExecutionBrokerEngine:
    """
    Nephon Reusable Execution Broker Engine (Policy Enforcement Point - PEP).
    Holds verification key and mutation credentials. Enforces Ed25519 token verification,
    schema hash binding, target case preservation, atomic nonce redemption, and crash reconciliation.
    """

    def __init__(
        self,
        verifier: BrokerTokenVerifier,
        project_id: str,
        environment_id: str,
        broker_id: str = "default-broker",
        nonce_manager: DurableNonceManager | None = None,
        allowlisted_capability_ids: set[str] | None = None,
    ) -> None:
        self.verifier = verifier
        self.project_id = project_id
        self.environment_id = environment_id
        self.broker_id = broker_id
        self.nonce_manager = nonce_manager or DurableNonceManager()
        self.allowlisted_capability_ids = allowlisted_capability_ids
        self.adapters: dict[str, CapabilityAdapter] = {}
        self.adapter_hashes: dict[str, str] = {}

    def register_adapter(self, adapter: CapabilityAdapter) -> None:
        """
        Registers a trusted CapabilityAdapter into the broker.
        Enforces allowlist check and duplicate capability ID prevention.
        """
        cap_id = adapter.capability_id
        if self.allowlisted_capability_ids is not None and cap_id not in self.allowlisted_capability_ids:
            raise BrokerEngineError(f"Capability ID '{cap_id}' is not in the pinned broker allowlist.")
        if cap_id in self.adapters:
            raise BrokerEngineError(f"Duplicate capability ID '{cap_id}' registration attempt rejected.")

        self.adapters[cap_id] = adapter
        self.adapter_hashes[cap_id] = compute_schema_hash(adapter.request_model)

    async def execute_authorized_action(
        self,
        signed_token: SignedExecutionToken,
        target: str,
        parameters: dict[str, Any],
    ) -> ExecutionReceipt:
        """
        Executes a state-changing action backed by a signed Ed25519 token.
        Enforces token signature, expiry, request parameter hash, schema hash, and atomic nonce redemption.
        """
        payload = signed_token.payload
        cap_id = payload.capability_id

        # 1. Lookup Adapter
        if cap_id not in self.adapters:
            raise BrokerEngineError(f"No capability adapter registered for capability_id '{cap_id}'.")
        adapter = self.adapters[cap_id]

        # 2. Validate Request Parameters against Adapter Schema
        try:
            full_params = {"target": target, **parameters} if "target" not in parameters else parameters
            request_obj = adapter.request_model.model_validate(full_params)
        except ValidationError as ve:
            raise BrokerEngineError(f"Request parameters failed schema validation for '{cap_id}': {ve}")

        # 3. Compute Request Hash and Schema Hash
        schema_hash = self.adapter_hashes[cap_id]
        req_hash = compute_request_hash(
            adapter.capability_id,
            adapter.capability_version,
            target,
            parameters,
        )

        # 4. Verify Cryptographic Token
        self.verifier.verify_token(
            signed_token=signed_token,
            expected_project_id=self.project_id,
            expected_environment_id=self.environment_id,
            expected_capability_id=adapter.capability_id,
            expected_capability_version=adapter.capability_version,
            expected_capability_schema_hash=schema_hash,
            expected_request_hash=req_hash,
        )

        # 5. Atomic Nonce Redemption (AUTHORIZED -> CLAIMED)
        record = self.nonce_manager.claim_nonce(
            nonce=payload.nonce,
            decision_id=payload.decision_id,
            capability_id=cap_id,
            request_hash=req_hash,
        )

        execution_id = uuid4()
        started_at = datetime.now(timezone.utc)
        self.nonce_manager.mark_executing(payload.nonce)

        # 6. Execute Adapter Mutation
        try:
            result_summary = await adapter.execute(request_obj, execution_id)
            completed_at = datetime.now(timezone.utc)
            self.nonce_manager.mark_succeeded(payload.nonce, result_summary=result_summary)

            return ExecutionReceipt(
                execution_id=execution_id,
                decision_id=payload.decision_id,
                capability_id=cap_id,
                state=ExecutionState.SUCCEEDED,
                started_at=started_at,
                completed_at=completed_at,
                result_summary=result_summary,
            )
        except Exception as exc:
            completed_at = datetime.now(timezone.utc)
            self.nonce_manager.mark_failed(payload.nonce, error_message=str(exc))

            return ExecutionReceipt(
                execution_id=execution_id,
                decision_id=payload.decision_id,
                capability_id=cap_id,
                state=ExecutionState.FAILED,
                started_at=started_at,
                completed_at=completed_at,
                result_summary={"error": str(exc)},
            )

    async def reconcile_crashed_executions(self) -> list[ExecutionReceipt]:
        """
        Reconciles any execution records left in EXECUTING state due to a broker crash.
        Invokes adapter.reconcile() to verify postconditions cleanly.
        """
        receipts: list[ExecutionReceipt] = []
        unreconciled = self.nonce_manager.get_unreconciled_records()

        for rec in unreconciled:
            if rec.capability_id in self.adapters:
                adapter = self.adapters[rec.capability_id]
                try:
                    # Attempt reconciliation
                    rec_result = await adapter.reconcile(rec.token_nonce, adapter.request_model.model_construct())
                    self.nonce_manager.mark_succeeded(rec.token_nonce, result_summary=rec_result)
                    receipts.append(
                        ExecutionReceipt(
                            execution_id=uuid4(),
                            decision_id=rec.decision_id,
                            capability_id=rec.capability_id,
                            state=ExecutionState.SUCCEEDED,
                            started_at=rec.claimed_at,
                            completed_at=datetime.now(timezone.utc),
                            result_summary=rec_result,
                        )
                    )
                except Exception as e:
                    self.nonce_manager.mark_requires_reconciliation(rec.token_nonce, reason=str(e))

        return receipts
