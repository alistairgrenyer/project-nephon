from __future__ import annotations

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Any
from uuid import UUID, uuid4
import pytest
from pydantic import BaseModel

from nephon_contracts.contexts import Context
from nephon_contracts.dto import ActionRequest
from nephon_contracts.enums import ExecutionState, GovernanceDisposition, RiskClass

from nephon_graph.compiler.kanon_compiler import KanonCompiler, compute_entity_id
from nephon_graph.compiler.markdown_loader import MarkdownLoader
from nephon_graph.core.claims import AuthorityLevel, Claim, EpistemicMode, Polarity, TrustLevel
from nephon_graph.core.events import KnowledgeEvent
from nephon_graph.core.propositions import PropositionAtom
from nephon_graph.core.provenance import SourceKind, SourceLeaf
from nephon_graph.storage.event_store import InMemoryEventStore

from nephon_gateway.signer import GatewaySigner
from nephon_gateway.service import ConstitutionalGatewayService

from nephon_broker_runtime.verifier import BrokerTokenVerifier, TokenValidationError
from nephon_broker_runtime.nonce_manager import DurableNonceManager, TokenReplayError
from nephon_broker_runtime.broker_engine import ExecutionBrokerEngine, BrokerEngineError, compute_schema_hash
from nephon_broker_runtime.adapter_protocol import CapabilityAdapter



class DummyRestartContainerRequest(BaseModel):
    target: str
    timeout_seconds: int = 30


class MockRestartContainerAdapter:
    capability_id = "restart_container"
    capability_version = "1.0.0"
    risk_class = RiskClass.REVERSIBLE_MUTATION
    request_model = DummyRestartContainerRequest

    def __init__(self) -> None:
        self.executed_targets: list[str] = []
        self.reconciled_ids: list[UUID] = []

    async def inspect_preconditions(self, request: DummyRestartContainerRequest) -> tuple:
        return ()

    async def execute(self, request: DummyRestartContainerRequest, execution_id: UUID) -> dict[str, Any]:
        self.executed_targets.append(request.target)
        return {"status": "restarted", "target": request.target, "execution_id": str(execution_id)}

    async def reconcile(self, execution_id: UUID, request: DummyRestartContainerRequest) -> dict[str, Any]:
        self.reconciled_ids.append(execution_id)
        return {"status": "reconciled", "execution_id": str(execution_id)}


def setup_gateway_and_broker():
    store = InMemoryEventStore()
    
    # Register DEV recovery claim in store for scenario
    c_atom = PropositionAtom.create(
        "permitted",
        {
            "actor": compute_entity_id("actor", "nephon"),
            "action": compute_entity_id("action", "container_x"),
        },
    )
    store.register_atom(c_atom)

    claim = Claim(
        proposition_id=c_atom.id,
        polarity=Polarity.POSITIVE,
        context=Context.universal(),
        provenance=SourceLeaf(kind=SourceKind.EXTERNAL, ref_id="dev_permission"),
        asserted_by="constitutional_rule",
        trust_level=TrustLevel.CONSTITUTIONAL,
        authority_level=AuthorityLevel.CONSTITUTIONAL,
        epistemic_mode=EpistemicMode.CONSTITUTIONAL_JUDGEMENT,
    )
    store.register_claim(claim)
    store.append(KnowledgeEvent(aggregate_id=str(claim.id), aggregate_version=1, event_type="ClaimCreated"))
    store.append(KnowledgeEvent(aggregate_id=str(claim.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(claim.id)}))

    signer = GatewaySigner.generate(key_id="test-gateway-key")
    gateway = ConstitutionalGatewayService(store=store, signer=signer)

    verifier = BrokerTokenVerifier(public_key=signer.get_public_key())
    broker = ExecutionBrokerEngine(
        verifier=verifier,
        project_id="test_project",
        environment_id="development",
        broker_id="test-broker-1",
        allowlisted_capability_ids={"restart_container"},
    )
    adapter = MockRestartContainerAdapter()
    broker.register_adapter(adapter)

    return gateway, broker, adapter, signer


def test_valid_token_execution_flow():
    async def _test():
        gateway, broker, adapter, _ = setup_gateway_and_broker()

        req = ActionRequest(
            project_id="test_project",
            environment_id="development",
            capability_id="restart_container",
            capability_version="1.0.0",
            target="container_x",
            parameters={"timeout_seconds": 30},
        )

        schema_hash = compute_schema_hash(MockRestartContainerAdapter.request_model)
        decision, signed_token = gateway.evaluate_action(
            req,
            broker_id="test-broker-1",
            capability_schema_hash=schema_hash,
        )

        assert decision.disposition == GovernanceDisposition.PERMIT
        assert signed_token is not None

        receipt = await broker.execute_authorized_action(
            signed_token=signed_token,
            target="container_x",
            parameters={"timeout_seconds": 30},
        )

        assert receipt.state == ExecutionState.SUCCEEDED
        assert adapter.executed_targets == ["container_x"]

    asyncio.run(_test())


def test_target_swapping_attack_rejected():
    async def _test():
        gateway, broker, adapter, _ = setup_gateway_and_broker()

        req = ActionRequest(
            project_id="test_project",
            environment_id="development",
            capability_id="restart_container",
            capability_version="1.0.0",
            target="container_x",
            parameters={"timeout_seconds": 30},
        )

        schema_hash = compute_schema_hash(MockRestartContainerAdapter.request_model)
        _, signed_token = gateway.evaluate_action(req, broker_id="test-broker-1", capability_schema_hash=schema_hash)


        # Attacker attempts to swap target to prod_database_container using valid token for container_x
        with pytest.raises(TokenValidationError, match="request_hash.*mismatch"):
            await broker.execute_authorized_action(
                signed_token=signed_token,
                target="prod_database_container",
                parameters={"timeout_seconds": 30},
            )

    asyncio.run(_test())


def test_parameter_tampering_attack_rejected():
    async def _test():
        gateway, broker, adapter, _ = setup_gateway_and_broker()

        req = ActionRequest(
            project_id="test_project",
            environment_id="development",
            capability_id="restart_container",
            capability_version="1.0.0",
            target="container_x",
            parameters={"timeout_seconds": 30},
        )

        schema_hash = compute_schema_hash(MockRestartContainerAdapter.request_model)
        _, signed_token = gateway.evaluate_action(req, broker_id="test-broker-1", capability_schema_hash=schema_hash)


        # Attacker attempts to alter parameter dictionary (e.g. timeout_seconds: 9999)
        with pytest.raises(TokenValidationError, match="request_hash.*mismatch"):
            await broker.execute_authorized_action(
                signed_token=signed_token,
                target="container_x",
                parameters={"timeout_seconds": 9999},
            )

    asyncio.run(_test())


def test_token_replay_attack_rejected():
    async def _test():
        gateway, broker, adapter, _ = setup_gateway_and_broker()

        req = ActionRequest(
            project_id="test_project",
            environment_id="development",
            capability_id="restart_container",
            capability_version="1.0.0",
            target="container_x",
            parameters={"timeout_seconds": 30},
        )

        schema_hash = compute_schema_hash(MockRestartContainerAdapter.request_model)
        _, signed_token = gateway.evaluate_action(req, broker_id="test-broker-1", capability_schema_hash=schema_hash)


        # First redemption succeeds
        receipt1 = await broker.execute_authorized_action(
            signed_token=signed_token,
            target="container_x",
            parameters={"timeout_seconds": 30},
        )
        assert receipt1.state == ExecutionState.SUCCEEDED

        # Second redemption attempt with same token nonce MUST fail with TokenReplayError
        with pytest.raises(TokenReplayError, match="already been redeemed"):
            await broker.execute_authorized_action(
                signed_token=signed_token,
                target="container_x",
                parameters={"timeout_seconds": 30},
            )

    asyncio.run(_test())


def test_key_forgery_attack_rejected():
    async def _test():
        gateway, broker, adapter, _ = setup_gateway_and_broker()

        req = ActionRequest(
            project_id="test_project",
            environment_id="development",
            capability_id="restart_container",
            capability_version="1.0.0",
            target="container_x",
            parameters={"timeout_seconds": 30},
        )

        # Rogue signer generates unauthorized key pair
        rogue_signer = GatewaySigner.generate(key_id="unauthorized-rogue-key")
        rogue_gateway = ConstitutionalGatewayService(store=gateway.store, signer=rogue_signer)

        schema_hash = compute_schema_hash(MockRestartContainerAdapter.request_model)
        _, forged_signed_token = rogue_gateway.evaluate_action(
            req,
            broker_id="test-broker-1",
            capability_schema_hash=schema_hash,
        )


        # Honest broker with official public key MUST reject forged token
        with pytest.raises(TokenValidationError, match="signature verification failed"):
            await broker.execute_authorized_action(
                signed_token=forged_signed_token,
                target="container_x",
                parameters={"timeout_seconds": 30},
            )

    asyncio.run(_test())


def test_crash_reconciliation():
    async def _test():
        gateway, broker, adapter, _ = setup_gateway_and_broker()

        req = ActionRequest(
            project_id="test_project",
            environment_id="development",
            capability_id="restart_container",
            capability_version="1.0.0",
            target="container_x",
            parameters={"timeout_seconds": 30},
        )

        schema_hash = compute_schema_hash(MockRestartContainerAdapter.request_model)
        _, signed_token = gateway.evaluate_action(req, broker_id="test-broker-1", capability_schema_hash=schema_hash)


        # Simulate broker claiming token and marking state EXECUTING before crash
        nonce = signed_token.payload.nonce
        broker.nonce_manager.claim_nonce(
            nonce=nonce,
            decision_id=signed_token.payload.decision_id,
            capability_id="restart_container",
            request_hash=signed_token.payload.request_hash,
        )
        broker.nonce_manager.mark_executing(nonce)

        # Now broker restarts and calls reconcile_crashed_executions()
        receipts = await broker.reconcile_crashed_executions()
        assert len(receipts) == 1
        assert receipts[0].state == ExecutionState.SUCCEEDED
        assert adapter.reconciled_ids == [nonce]

    asyncio.run(_test())
