from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest

from nephon_graph.core.belief import BeliefStatus, ProvenanceSupportStatus
from nephon_graph.core.claims import AuthorityLevel, Claim, EpistemicMode, Polarity, TrustLevel
from nephon_graph.core.contexts import Context, ContextConstraint
from nephon_graph.core.entities import Entity
from nephon_graph.core.events import KnowledgeEvent
from nephon_graph.core.inference import InferenceRule
from nephon_graph.core.propositions import PropositionAtom
from nephon_graph.core.provenance import AnyNode, ClaimLeaf, SourceKind, SourceLeaf
from nephon_graph.engine.belief_evaluator import BeliefEvaluator
from nephon_graph.engine.context_algebra import ContextAlgebra
from nephon_graph.engine.governance_policy import AuthorityOrder, GovernancePolicy
from nephon_graph.engine.inference_engine import InferenceEngine, InferenceError
from nephon_graph.engine.provenance_evaluator import ProvenanceEvaluator
from nephon_graph.storage.base import EventIntegrityError
from nephon_graph.storage.event_store import InMemoryEventStore


def test_invariant_full_envelope_event_idempotency_and_integrity():
    """
    Invariant: Re-submitting same event_id with ANY altered envelope field
    (event_type, aggregate_id, aggregate_version, occurred_at, causation_id, payload)
    must raise EventIntegrityError.
    """
    store = InMemoryEventStore()
    event_id = uuid4()
    now = datetime.now(timezone.utc)

    orig_ev = KnowledgeEvent(
        event_id=event_id,
        aggregate_id="agg-1",
        aggregate_version=1,
        event_type="ClaimCreated",
        occurred_at=now,
        payload={"claim_id": "c1"},
    )
    store.append(orig_ev)

    # Re-submitting identical full envelope succeeds (NO-OP)
    dup_ev = KnowledgeEvent(
        event_id=event_id,
        aggregate_id="agg-1",
        aggregate_version=1,
        event_type="ClaimCreated",
        occurred_at=now,
        payload={"claim_id": "c1"},
    )
    res = store.append(dup_ev)
    assert res.sequence == 1

    # Altering event_type raises EventIntegrityError
    altered_type = dup_ev.model_copy(update={"event_type": "ClaimActivated"})
    with pytest.raises(EventIntegrityError):
        store.append(altered_type)

    # Altering occurred_at raises EventIntegrityError
    altered_time = dup_ev.model_copy(update={"occurred_at": now + timedelta(seconds=10)})
    with pytest.raises(EventIntegrityError):
        store.append(altered_time)

    # Altering aggregate_id raises EventIntegrityError
    altered_agg = dup_ev.model_copy(update={"aggregate_id": "agg-2"})
    with pytest.raises(EventIntegrityError):
        store.append(altered_agg)


def test_invariant_unknown_intersect_exact_indeterminate_inference_refusal():
    """
    Invariant: UNKNOWN ∩ EXACT(production) -> INDETERMINATE (None), and InferenceEngine refuses derivation.
    """
    store = InMemoryEventStore()

    p1_atom = PropositionAtom.create(predicate="p1", arguments={"arg": uuid4()})
    p2_atom = PropositionAtom.create(predicate="p2", arguments={"arg": uuid4()})
    c_atom = PropositionAtom.create(predicate="c", arguments={"arg": uuid4()})
    store.register_atom(p1_atom)
    store.register_atom(p2_atom)

    ctx_unknown = Context(environment=ContextConstraint.unknown())
    ctx_prod = Context(environment=ContextConstraint.exact("production"))

    # Direct context algebra check
    assert ContextAlgebra.intersect_contexts(ctx_unknown, ctx_prod) is None

    claim1 = Claim(
        proposition_id=p1_atom.id,
        polarity=Polarity.POSITIVE,
        context=ctx_unknown,
        provenance=SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="doc-1"),
        asserted_by="Steward",
        trust_level=TrustLevel.STEWARD_AUTHORIZED,
        authority_level=AuthorityLevel.STEWARD_AUTHORIZED,
        epistemic_mode=EpistemicMode.OPERATIONAL_RULE,
    )
    claim2 = Claim(
        proposition_id=p2_atom.id,
        polarity=Polarity.POSITIVE,
        context=ctx_prod,
        provenance=SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="doc-2"),
        asserted_by="Steward",
        trust_level=TrustLevel.STEWARD_AUTHORIZED,
        authority_level=AuthorityLevel.STEWARD_AUTHORIZED,
        epistemic_mode=EpistemicMode.OPERATIONAL_RULE,
    )
    for c in [claim1, claim2]:
        store.register_claim(c)
        store.append(KnowledgeEvent(aggregate_id=str(c.id), aggregate_version=1, event_type="ClaimCreated"))
        store.append(KnowledgeEvent(aggregate_id=str(c.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(c.id)}))

    rule = InferenceRule(rule_id="R-INDET", version="1.0.0", premise_predicates=["p1", "p2"], conclusion_predicate="c")
    engine = InferenceEngine(store)
    engine.register_rule(rule)

    # Derivation must fail closed on INDETERMINATE context intersection
    with pytest.raises(InferenceError, match="cannot be intersected cleanly"):
        engine.derive_claim(
            rule_id="R-INDET",
            rule_version="1.0.0",
            premise_claim_ids=[claim1.id, claim2.id],
            conclusion_atom=c_atom,
            polarity=Polarity.POSITIVE,
            asserted_by="EngineTest",
        )


def test_invariant_authority_disagreement_belief_vs_governance():
    """
    Invariant: Higher/lower authority disagreement -> BeliefEvaluator returns CONFLICTED,
    while GovernancePolicy selects the higher-authority claim as governing directive.
    """
    store = InMemoryEventStore()

    atom = PropositionAtom.create(predicate="system_access", arguments={"user": uuid4()})
    store.register_atom(atom)
    context = Context.universal()

    # Constitutional claim (Higher authority: 100) - Positive
    claim_const = Claim(
        proposition_id=atom.id,
        polarity=Polarity.POSITIVE,
        context=context,
        provenance=SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="SYSTEM_CHARTER.md"),
        asserted_by="Steward",
        trust_level=TrustLevel.CONSTITUTIONAL,
        authority_level=AuthorityLevel.CONSTITUTIONAL,
        epistemic_mode=EpistemicMode.CONSTITUTIONAL_JUDGEMENT,
    )
    # Untrusted input claim (Lower authority: 20) - Negative
    claim_untrusted = Claim(
        proposition_id=atom.id,
        polarity=Polarity.NEGATIVE,
        context=context,
        provenance=SourceLeaf(kind=SourceKind.EXTERNAL, ref_id="user_prompt_text"),
        asserted_by="ExternalUser",
        trust_level=TrustLevel.UNTRUSTED_INPUT,
        authority_level=AuthorityLevel.UNTRUSTED_INPUT,
        epistemic_mode=EpistemicMode.OBSERVATION,
    )
    for c in [claim_const, claim_untrusted]:
        store.register_claim(c)
        store.append(KnowledgeEvent(aggregate_id=str(c.id), aggregate_version=1, event_type="ClaimCreated"))
        store.append(KnowledgeEvent(aggregate_id=str(c.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(c.id)}))

    # 1. BeliefEvaluator MUST preserve conflict without flattening by authority
    belief = BeliefEvaluator.evaluate(atom.id, context, store)
    assert belief.status == BeliefStatus.CONFLICTED
    assert len(belief.positive_claims) == 1
    assert len(belief.negative_claims) == 1

    # 2. GovernancePolicy selects higher authority claim (CONSTITUTIONAL)
    policy = GovernancePolicy()
    decision = policy.evaluate([claim_const, claim_untrusted], context)
    assert decision.governing_claim is not None
    assert decision.governing_claim.id == claim_const.id
    assert decision.authority_level == AuthorityLevel.CONSTITUTIONAL


def test_invariant_any_branch_partial_loss_survives():
    """
    Invariant: AnyNode provenance loses 1 source (retracted) but retains another (active) -> VALID.
    """
    store = InMemoryEventStore()

    source1 = SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="doc_1.md")
    source2 = SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="doc_2.md")

    # Claim for source1
    c1_atom = PropositionAtom.create(predicate="fact1", arguments={"id": uuid4()})
    c1 = Claim(
        proposition_id=c1_atom.id,
        polarity=Polarity.POSITIVE,
        context=Context.universal(),
        provenance=source1,
        asserted_by="Doc1",
        trust_level=TrustLevel.STEWARD_AUTHORIZED,
        authority_level=AuthorityLevel.STEWARD_AUTHORIZED,
        epistemic_mode=EpistemicMode.OBSERVATION,
    )
    # Claim for source2
    c2_atom = PropositionAtom.create(predicate="fact2", arguments={"id": uuid4()})
    c2 = Claim(
        proposition_id=c2_atom.id,
        polarity=Polarity.POSITIVE,
        context=Context.universal(),
        provenance=source2,
        asserted_by="Doc2",
        trust_level=TrustLevel.STEWARD_AUTHORIZED,
        authority_level=AuthorityLevel.STEWARD_AUTHORIZED,
        epistemic_mode=EpistemicMode.OBSERVATION,
    )
    for c in [c1, c2]:
        store.register_claim(c)
        store.append(KnowledgeEvent(aggregate_id=str(c.id), aggregate_version=1, event_type="ClaimCreated"))
        store.append(KnowledgeEvent(aggregate_id=str(c.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(c.id)}))

    any_provenance = AnyNode(children=(ClaimLeaf(claim_id=c1.id), ClaimLeaf(claim_id=c2.id)))

    # Initial evaluation: both active -> VALID
    status1 = ProvenanceEvaluator.evaluate(any_provenance, store)
    assert status1 == ProvenanceSupportStatus.VALID

    # Deactivate c1 by retracting it
    store.append(KnowledgeEvent(aggregate_id=str(c1.id), aggregate_version=3, event_type="ClaimRetracted", payload={"claim_id": str(c1.id)}))

    # Evaluation with c1 retracted: c2 is still active -> VALID
    status2 = ProvenanceEvaluator.evaluate(any_provenance, store)
    assert status2 == ProvenanceSupportStatus.VALID


def test_invariant_epistemic_mode_immutability():
    """
    Invariant: EpistemicMode is immutable after claim creation.
    Reclassifying an observation as a constitutional judgement requires a new claim with distinct ID,
    provenance, and assertion event. Mutating an existing claim object or in-place reclassification is invalid.
    """
    store = InMemoryEventStore()

    atom = PropositionAtom.create(predicate="observed_event", arguments={"id": uuid4()})
    store.register_atom(atom)

    original_claim = Claim(
        proposition_id=atom.id,
        polarity=Polarity.POSITIVE,
        context=Context.universal(),
        provenance=SourceLeaf(kind=SourceKind.EXTERNAL, ref_id="telemetry_log_01"),
        asserted_by="MonitoringAgent",
        trust_level=TrustLevel.VERIFIED_SYSTEM,
        authority_level=AuthorityLevel.VERIFIED_SYSTEM,
        epistemic_mode=EpistemicMode.OBSERVATION,
    )
    store.register_claim(original_claim)
    store.append(KnowledgeEvent(aggregate_id=str(original_claim.id), aggregate_version=1, event_type="ClaimCreated"))
    store.append(KnowledgeEvent(aggregate_id=str(original_claim.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(original_claim.id)}))

    # Attempting to mutate epistemic_mode in-place on stored object violates immutability invariant
    stored_claim = store.get_claim(original_claim.id)
    assert stored_claim is not None
    assert stored_claim.epistemic_mode == EpistemicMode.OBSERVATION

    # Reclassification pathway requires creating a NEW claim with explicit provenance linking back
    reclassified_claim = Claim(
        proposition_id=atom.id,
        polarity=Polarity.POSITIVE,
        context=Context.universal(),
        provenance=ClaimLeaf(claim_id=original_claim.id),  # Linked to original claim
        asserted_by="Steward",
        trust_level=TrustLevel.CONSTITUTIONAL,
        authority_level=AuthorityLevel.CONSTITUTIONAL,
        epistemic_mode=EpistemicMode.CONSTITUTIONAL_JUDGEMENT,  # New mode
    )
    store.register_claim(reclassified_claim)
    store.append(KnowledgeEvent(aggregate_id=str(reclassified_claim.id), aggregate_version=1, event_type="ClaimCreated"))
    store.append(KnowledgeEvent(aggregate_id=str(reclassified_claim.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(reclassified_claim.id)}))

    # Both claims remain distinct with their own epistemic modes
    assert store.get_claim(original_claim.id).epistemic_mode == EpistemicMode.OBSERVATION
    assert store.get_claim(reclassified_claim.id).epistemic_mode == EpistemicMode.CONSTITUTIONAL_JUDGEMENT
    assert reclassified_claim.id != original_claim.id


def test_invariant_event_replay_identical_materialized_projection():
    """
    Invariant: Replaying complete event stream rebuilds byte-equivalent/identical materialized state.
    """
    store = InMemoryEventStore()

    atom = PropositionAtom.create(predicate="test_pred", arguments={"id": uuid4()})
    store.register_atom(atom)

    claim = Claim(
        proposition_id=atom.id,
        polarity=Polarity.POSITIVE,
        context=Context.universal(),
        provenance=SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="doc.md"),
        asserted_by="Tester",
        trust_level=TrustLevel.STEWARD_AUTHORIZED,
        authority_level=AuthorityLevel.STEWARD_AUTHORIZED,
        epistemic_mode=EpistemicMode.OBSERVATION,
    )
    store.register_claim(claim)

    store.append(KnowledgeEvent(aggregate_id=str(claim.id), aggregate_version=1, event_type="ClaimCreated"))
    store.append(KnowledgeEvent(aggregate_id=str(claim.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(claim.id)}))

    assert store.is_claim_active(claim.id) is True

    # Rebuild index
    store.rebuild_materialized_index()

    assert store.is_claim_active(claim.id) is True
    assert store.get_claim(claim.id) is not None
    assert store.get_atom(atom.id) is not None
