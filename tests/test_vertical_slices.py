from __future__ import annotations

from uuid import uuid4
import pytest

from nephon_graph.core.belief import BeliefStatus, ProvenanceSupportStatus
from nephon_graph.core.claims import AuthorityLevel, Claim, EpistemicMode, Polarity, TrustLevel
from nephon_graph.core.contexts import Context, ContextConstraint
from nephon_graph.core.entities import Entity
from nephon_graph.core.events import KnowledgeEvent
from nephon_graph.core.propositions import PropositionAtom, compute_atom_id
from nephon_graph.core.provenance import SourceKind, SourceLeaf
from nephon_graph.engine.belief_evaluator import BeliefEvaluator
from nephon_graph.engine.provenance_evaluator import ProvenanceEvaluator
from nephon_graph.storage.event_store import InMemoryEventStore


def test_vertical_slice_1_supported_belief():
    """
    Slice 1: Atom -> Positive Claim -> Events -> Provenance VALID -> Belief SUPPORTED -> Event Replay Identical
    """
    store = InMemoryEventStore()

    # 1. Create deterministic PropositionAtom
    subject_entity = Entity(entity_type="agent", name="Nephon")
    target_entity = Entity(entity_type="system", name="ProxmoxCluster")
    
    atom = PropositionAtom.create(
        predicate="administers",
        arguments={"subject": subject_entity.id, "target": target_entity.id},
    )
    store.register_atom(atom)

    # Verify deterministic UUIDv5 matching
    expected_id = compute_atom_id("administers", {"subject": subject_entity.id, "target": target_entity.id})
    assert atom.id == expected_id

    # 2. Create positive claim with SourceLeaf provenance
    provenance = SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="08_PRAXIS.md#PRX-01")
    context = Context.universal()

    claim = Claim(
        proposition_id=atom.id,
        polarity=Polarity.POSITIVE,
        context=context,
        provenance=provenance,
        asserted_by="Steward",
        trust_level=TrustLevel.CONSTITUTIONAL,
        authority_level=AuthorityLevel.CONSTITUTIONAL,
        epistemic_mode=EpistemicMode.CONSTITUTIONAL_JUDGEMENT,
    )
    store.register_claim(claim)

    # 3. Append ClaimCreated and ClaimActivated events
    ev1 = KnowledgeEvent(
        aggregate_id=str(claim.id),
        aggregate_version=1,
        event_type="ClaimCreated",
        payload={"claim_id": str(claim.id), "proposition_id": str(atom.id)},
    )
    ev2 = KnowledgeEvent(
        aggregate_id=str(claim.id),
        aggregate_version=2,
        event_type="ClaimActivated",
        payload={"claim_id": str(claim.id)},
    )
    store.append(ev1)
    store.append(ev2)

    # 4. Evaluate source provenance
    prov_status = ProvenanceEvaluator.evaluate(claim.provenance, store)
    assert prov_status == ProvenanceSupportStatus.VALID

    # 5. Evaluate belief
    belief = BeliefEvaluator.evaluate(atom.id, context, store)
    assert belief.status == BeliefStatus.SUPPORTED
    assert len(belief.positive_claims) == 1
    assert len(belief.negative_claims) == 0

    # 6. Replay complete event stream
    store.rebuild_materialized_index()

    # 7. Confirm exact identical state after replay
    assert store.is_claim_active(claim.id) is True
    belief_after = BeliefEvaluator.evaluate(atom.id, context, store)
    assert belief_after.status == BeliefStatus.SUPPORTED
    assert belief_after.positive_claims[0].id == claim.id


def test_vertical_slice_2_genuine_conflict():
    """
    Slice 2: Same unsigned PropositionAtom + active negative claim in compatible context -> CONFLICTED
    """
    store = InMemoryEventStore()

    subject_entity = Entity(entity_type="agent", name="Nephon")
    target_entity = Entity(entity_type="system", name="ProxmoxCluster")
    
    atom = PropositionAtom.create(
        predicate="administers",
        arguments={"subject": subject_entity.id, "target": target_entity.id},
    )
    store.register_atom(atom)

    context = Context.universal()

    # Positive claim
    claim_pos = Claim(
        proposition_id=atom.id,
        polarity=Polarity.POSITIVE,
        context=context,
        provenance=SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="08_PRAXIS.md"),
        asserted_by="Steward",
        trust_level=TrustLevel.STEWARD_AUTHORIZED,
        authority_level=AuthorityLevel.STEWARD_AUTHORIZED,
        epistemic_mode=EpistemicMode.OPERATIONAL_RULE,
    )
    store.register_claim(claim_pos)

    # Negative claim for the exact same atom ID
    claim_neg = Claim(
        proposition_id=atom.id,
        polarity=Polarity.NEGATIVE,
        context=context,
        provenance=SourceLeaf(kind=SourceKind.EXTERNAL, ref_id="audit_alert_404"),
        asserted_by="MonitoringAgent",
        trust_level=TrustLevel.VERIFIED_SYSTEM,
        authority_level=AuthorityLevel.VERIFIED_SYSTEM,
        epistemic_mode=EpistemicMode.OBSERVATION,
    )
    store.register_claim(claim_neg)

    # Activate both claims
    for claim in [claim_pos, claim_neg]:
        store.append(KnowledgeEvent(aggregate_id=str(claim.id), aggregate_version=1, event_type="ClaimCreated"))
        store.append(KnowledgeEvent(aggregate_id=str(claim.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(claim.id)}))

    # Evaluate belief -> CONFLICTED
    belief = BeliefEvaluator.evaluate(atom.id, context, store)
    assert belief.status == BeliefStatus.CONFLICTED
    assert len(belief.positive_claims) == 1
    assert len(belief.negative_claims) == 1


def test_vertical_slice_3_context_discrimination():
    """
    Slice 3: Positive claim in dev context, negative claim in prod context -> Zero false contradiction
    """
    store = InMemoryEventStore()

    subject_entity = Entity(entity_type="agent", name="Nephon")
    target_entity = Entity(entity_type="system", name="ProxmoxCluster")
    
    atom = PropositionAtom.create(
        predicate="can_deploy",
        arguments={"subject": subject_entity.id, "target": target_entity.id},
    )
    store.register_atom(atom)

    dev_context = Context(environment=ContextConstraint.exact("development"))
    prod_context = Context(environment=ContextConstraint.exact("production"))

    # Dev permission positive claim
    claim_dev = Claim(
        proposition_id=atom.id,
        polarity=Polarity.POSITIVE,
        context=dev_context,
        provenance=SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="08_PRAXIS.md"),
        asserted_by="Steward",
        trust_level=TrustLevel.STEWARD_AUTHORIZED,
        authority_level=AuthorityLevel.STEWARD_AUTHORIZED,
        epistemic_mode=EpistemicMode.OPERATIONAL_RULE,
    )
    store.register_claim(claim_dev)

    # Prod restriction negative claim
    claim_prod = Claim(
        proposition_id=atom.id,
        polarity=Polarity.NEGATIVE,
        context=prod_context,
        provenance=SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="05_AUTHORITY_AND_OBEDIENCE.md"),
        asserted_by="Steward",
        trust_level=TrustLevel.CONSTITUTIONAL,
        authority_level=AuthorityLevel.CONSTITUTIONAL,
        epistemic_mode=EpistemicMode.CONSTITUTIONAL_JUDGEMENT,
    )
    store.register_claim(claim_prod)

    for claim in [claim_dev, claim_prod]:
        store.append(KnowledgeEvent(aggregate_id=str(claim.id), aggregate_version=1, event_type="ClaimCreated"))
        store.append(KnowledgeEvent(aggregate_id=str(claim.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(claim.id)}))

    # Evaluate in dev context -> SUPPORTED
    dev_belief = BeliefEvaluator.evaluate(atom.id, dev_context, store)
    assert dev_belief.status == BeliefStatus.SUPPORTED
    assert len(dev_belief.positive_claims) == 1
    assert len(dev_belief.negative_claims) == 0

    # Evaluate in prod context -> REJECTED
    prod_belief = BeliefEvaluator.evaluate(atom.id, prod_context, store)
    assert prod_belief.status == BeliefStatus.REJECTED
    assert len(prod_belief.positive_claims) == 0
    assert len(prod_belief.negative_claims) == 1
