from __future__ import annotations

import hashlib
import unicodedata
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any
from uuid import UUID, uuid4

from nephon_contracts.canonical_json import compute_nephon_canonical_json_v1, compute_request_hash
from nephon_contracts.contexts import Context
from nephon_contracts.dto import (
    ActionRequest,
    ConstitutionalDecision,
    ExecutionAuthorizationPayload,
    SignedExecutionToken,
)
from nephon_contracts.enums import BeliefStatus, GovernanceDisposition, Polarity

from nephon_graph.compiler.kanon_compiler import NEPHON_ENTITY_NAMESPACE, compute_entity_id
from nephon_graph.core.claims import AuthorityLevel, Claim, EpistemicMode, TrustLevel
from nephon_graph.core.propositions import PropositionAtom, compute_atom_id
from nephon_graph.engine.belief_evaluator import BeliefEvaluator
from nephon_graph.engine.governance_policy import GovernancePolicy
from nephon_graph.storage.base import EventStore
from nephon_gateway.signer import GatewaySigner


class ConstitutionalGatewayService:
    """
    Nephon Constitutional Gateway Service (Policy Decision Point - PDP).
    Evaluates action requests against active event store belief and governance policy.
    Issues signed Ed25519 ExecutionAuthorizationTokens on PERMIT.
    """

    def __init__(
        self,
        store: EventStore,
        governance_policy: GovernancePolicy | None = None,
        signer: GatewaySigner | None = None,
        policy_version: str = "1.0.0",
    ) -> None:
        self.store = store
        self.governance_policy = governance_policy or GovernancePolicy()
        self.signer = signer or GatewaySigner.generate()
        self.policy_version = policy_version

    def evaluate_action(
        self,
        request: ActionRequest,
        broker_id: str = "default-broker",
        capability_schema_hash: str = "0000000000000000000000000000000000000000000000000000000000000000",
        token_ttl_seconds: int = 60,
    ) -> tuple[ConstitutionalDecision, SignedExecutionToken | None]:
        """
        Evaluates an ActionRequest against the constitutional store.
        Returns a tuple of (ConstitutionalDecision, SignedExecutionToken | None).
        Token is issued ONLY if disposition is PERMIT.
        """
        req_hash = compute_request_hash(
            request.capability_id,
            request.capability_version,
            request.target,
            request.parameters,
        )

        # Lookup canonical decision atom: permitted(actor: nephon, action: target)
        actor_id = compute_entity_id("actor", "nephon")
        action_id = compute_entity_id("action", request.target)
        atom = PropositionAtom.create(
            "permitted",
            {
                "actor": actor_id,
                "action": action_id,
            },
        )
        atom_id = atom.id
        
        # Evaluate belief state
        belief = BeliefEvaluator.evaluate(atom_id, request.context, self.store)
        claims = self.store.get_claims_for_atom(atom_id)
        active_claims = [c for c in claims if self.store.is_claim_active(c.id)]

        gov_decision = self.governance_policy.evaluate(
            active_claims,
            request.context,
            belief_state=belief,
            predicate="permitted",
        )

        # Extract governing declaration IDs
        gov_declarations: list[str] = []
        if gov_decision.governing_claim:
            gc = gov_decision.governing_claim
            gov_declarations.append(f"{gc.polarity.value}:{gc.authority_level.value}:{gc.id}")

        decision = ConstitutionalDecision(
            decision_id=uuid4(),
            disposition=gov_decision.disposition,
            belief_status=belief.status,
            governing_declarations=tuple(gov_declarations),
            missing_evidence=(),
            rationale=gov_decision.rationale,
        )

        if gov_decision.disposition != GovernanceDisposition.PERMIT:
            return decision, None

        # Issue signed Ed25519 token on PERMIT
        now = datetime.now(timezone.utc)
        valid_until = now + timedelta(seconds=token_ttl_seconds)

        context_hash = hashlib.sha256(
            compute_nephon_canonical_json_v1(request.context.model_dump(mode="json")).encode("utf-8")
        ).hexdigest()

        evidence_hash = hashlib.sha256(
            compute_nephon_canonical_json_v1([str(r) for r in request.evidence_refs]).encode("utf-8")
        ).hexdigest()

        payload = ExecutionAuthorizationPayload(
            token_version=1,
            issuer="nephon_constitutional_gateway",
            audience="nephon_execution_broker",
            key_id=self.signer.key_id,
            project_id=request.project_id,
            environment_id=request.environment_id,
            broker_id=broker_id,
            decision_id=decision.decision_id,
            capability_id=request.capability_id,
            capability_version=request.capability_version,
            capability_schema_hash=capability_schema_hash,
            request_hash=req_hash,
            context_hash=context_hash,
            evidence_snapshot_hash=evidence_hash,
            policy_version=self.policy_version,
            issued_at=now,
            not_before=now,
            valid_until=valid_until,
            nonce=uuid4(),
        )

        signed_token = self.signer.sign_payload(payload)
        return decision, signed_token
