from __future__ import annotations

from nephon_graph.core.belief import ProvenanceSupportStatus
from nephon_graph.core.claims import AuthorityLevel, Claim, EpistemicMode, Polarity, TrustLevel
from nephon_graph.core.contexts import Context
from nephon_graph.core.entities import Entity
from nephon_graph.core.events import KnowledgeEvent
from nephon_graph.core.inference import InferenceRule
from nephon_graph.core.propositions import PropositionAtom
from nephon_graph.core.provenance import SourceKind, SourceLeaf
from nephon_graph.engine.inference_engine import InferenceEngine
from nephon_graph.engine.provenance_evaluator import ProvenanceEvaluator
from nephon_graph.storage.event_store import InMemoryEventStore


def run_experiment_06():
    """
    Exp 06: Source claim retracted -> derived claim provenance becomes CURRENTLY_UNSUPPORTED.
    Verifies automatic invalidation propagation without mutative engine overwrites.
    """
    store = InMemoryEventStore()

    steward = Entity(name="Alistair", entity_type="person")
    nephon = Entity(name="Nephon", entity_type="agent")

    # Premise atom: authorized_by_steward(Alistair, Nephon)
    premise_atom = PropositionAtom.create(
        predicate="authorized_by_steward",
        arguments={"steward": steward.id, "subject": nephon.id},
    )
    store.register_atom(premise_atom)

    premise_claim = Claim(
        proposition_id=premise_atom.id,
        polarity=Polarity.POSITIVE,
        context=Context.universal(),
        provenance=SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="05_AUTHORITY_AND_OBEDIENCE.md"),
        asserted_by="Steward",
        trust_level=TrustLevel.STEWARD_AUTHORIZED,
        authority_level=AuthorityLevel.STEWARD_AUTHORIZED,
        epistemic_mode=EpistemicMode.OPERATIONAL_RULE,
    )
    store.register_claim(premise_claim)

    store.append(KnowledgeEvent(aggregate_id=str(premise_claim.id), aggregate_version=1, event_type="ClaimCreated"))
    store.append(KnowledgeEvent(aggregate_id=str(premise_claim.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(premise_claim.id)}))

    # Inference Rule: authorized_by_steward -> can_execute_action
    rule = InferenceRule(
        rule_id="R-01",
        version="1.0.0",
        description="Steward authority implies permission",
        premise_predicates=["authorized_by_steward"],
        conclusion_predicate="can_execute_action",
    )

    inference_engine = InferenceEngine(store)
    inference_engine.register_rule(rule)

    conclusion_atom = PropositionAtom.create(
        predicate="can_execute_action",
        arguments={"subject": nephon.id},
    )

    derived_claim = inference_engine.derive_claim(
        rule_id="R-01",
        rule_version="1.0.0",
        premise_claim_ids=[premise_claim.id],
        conclusion_atom=conclusion_atom,
        polarity=Polarity.POSITIVE,
        asserted_by="InferenceEngine",
    )

    initial_derived_status = ProvenanceEvaluator.evaluate(derived_claim.provenance, store)

    # NOW: Retract premise_claim!
    store.append(
        KnowledgeEvent(
            aggregate_id=str(premise_claim.id),
            aggregate_version=3,
            event_type="ClaimRetracted",
            payload={"claim_id": str(premise_claim.id), "reason": "Correction by Steward"},
        )
    )

    updated_derived_status = ProvenanceEvaluator.evaluate(derived_claim.provenance, store)

    return {
        "initial_status": initial_derived_status.value,
        "updated_status": updated_derived_status.value,
        "invalidation_successful": updated_derived_status == ProvenanceSupportStatus.CURRENTLY_UNSUPPORTED,
    }


if __name__ == "__main__":
    result = run_experiment_06()
    print("Experiment 06 Result:", result)
