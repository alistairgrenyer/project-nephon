from __future__ import annotations

from uuid import uuid4
import pytest

from nephon_graph.core.claims import AuthorityLevel, Claim, EpistemicMode, Polarity, TrustLevel
from nephon_graph.core.contexts import Context, ContextConstraint
from nephon_graph.core.events import KnowledgeEvent
from nephon_graph.core.inference import InferenceRule
from nephon_graph.core.propositions import PropositionAtom
from nephon_graph.core.provenance import SourceKind, SourceLeaf
from nephon_graph.engine.inference_engine import InferenceEngine, InferenceError
from nephon_graph.storage.event_store import InMemoryEventStore


def test_inference_engine_derivation_and_cycle_prevention():
    store = InMemoryEventStore()

    p_atom = PropositionAtom.create(predicate="premise_pred", arguments={"arg": uuid4()})
    c_atom = PropositionAtom.create(predicate="conclusion_pred", arguments={"arg": uuid4()})
    store.register_atom(p_atom)

    premise_claim = Claim(
        proposition_id=p_atom.id,
        polarity=Polarity.POSITIVE,
        context=Context.universal(),
        provenance=SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="doc-1"),
        asserted_by="Steward",
        trust_level=TrustLevel.STEWARD_AUTHORIZED,
        authority_level=AuthorityLevel.STEWARD_AUTHORIZED,
        epistemic_mode=EpistemicMode.OPERATIONAL_RULE,
    )
    store.register_claim(premise_claim)
    store.append(KnowledgeEvent(aggregate_id=str(premise_claim.id), aggregate_version=1, event_type="ClaimCreated"))
    store.append(KnowledgeEvent(aggregate_id=str(premise_claim.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(premise_claim.id)}))

    rule = InferenceRule(rule_id="R-TEST", version="1.0.0", premise_predicates=["premise_pred"], conclusion_predicate="conclusion_pred")
    engine = InferenceEngine(store)
    engine.register_rule(rule)

    derived = engine.derive_claim(
        rule_id="R-TEST",
        rule_version="1.0.0",
        premise_claim_ids=[premise_claim.id],
        conclusion_atom=c_atom,
        polarity=Polarity.POSITIVE,
        asserted_by="EngineTest",
    )

    assert store.is_claim_active(derived.id) is True
    assert derived.proposition_id == c_atom.id


def test_inference_engine_context_intersection_failure():
    store = InMemoryEventStore()

    p1_atom = PropositionAtom.create(predicate="p1", arguments={"arg": uuid4()})
    p2_atom = PropositionAtom.create(predicate="p2", arguments={"arg": uuid4()})
    c_atom = PropositionAtom.create(predicate="c", arguments={"arg": uuid4()})
    store.register_atom(p1_atom)
    store.register_atom(p2_atom)

    claim1 = Claim(
        proposition_id=p1_atom.id,
        polarity=Polarity.POSITIVE,
        context=Context(environment=ContextConstraint.exact("dev")),
        provenance=SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="doc-1"),
        asserted_by="Steward",
        trust_level=TrustLevel.STEWARD_AUTHORIZED,
        authority_level=AuthorityLevel.STEWARD_AUTHORIZED,
        epistemic_mode=EpistemicMode.OPERATIONAL_RULE,
    )
    claim2 = Claim(
        proposition_id=p2_atom.id,
        polarity=Polarity.POSITIVE,
        context=Context(environment=ContextConstraint.exact("prod")),
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

    rule = InferenceRule(rule_id="R-DISJOINT", version="1.0.0", premise_predicates=["p1", "p2"], conclusion_predicate="c")
    engine = InferenceEngine(store)
    engine.register_rule(rule)

    # Deriving with incompatible premise contexts MUST fail closed
    with pytest.raises(InferenceError):
        engine.derive_claim(
            rule_id="R-DISJOINT",
            rule_version="1.0.0",
            premise_claim_ids=[claim1.id, claim2.id],
            conclusion_atom=c_atom,
            polarity=Polarity.POSITIVE,
            asserted_by="EngineTest",
        )
