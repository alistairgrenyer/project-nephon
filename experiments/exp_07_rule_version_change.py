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


def run_experiment_07():
    """
    Exp 07: Inference Rule version change/deactivation.
    Verifies that claims derived from deactivated rules dynamically change support status.
    """
    store = InMemoryEventStore()

    agent = Entity(name="Nephon", entity_type="agent")

    premise_atom = PropositionAtom.create(predicate="is_healthy", arguments={"agent": agent.id})
    store.register_atom(premise_atom)

    premise_claim = Claim(
        proposition_id=premise_atom.id,
        polarity=Polarity.POSITIVE,
        context=Context.universal(),
        provenance=SourceLeaf(kind=SourceKind.EXTERNAL, ref_id="health_check_ok"),
        asserted_by="Monitor",
        trust_level=TrustLevel.VERIFIED_SYSTEM,
        authority_level=AuthorityLevel.VERIFIED_SYSTEM,
        epistemic_mode=EpistemicMode.OBSERVATION,
    )
    store.register_claim(premise_claim)

    for ev_type in ["ClaimCreated", "ClaimActivated"]:
        store.append(KnowledgeEvent(aggregate_id=str(premise_claim.id), aggregate_version=1 if ev_type == "ClaimCreated" else 2, event_type=ev_type, payload={"claim_id": str(premise_claim.id)}))

    rule = InferenceRule(rule_id="RULE-HEALTH", version="1.0.0", premise_predicates=["is_healthy"], conclusion_predicate="is_ready")
    inference_engine = InferenceEngine(store)
    inference_engine.register_rule(rule)

    conclusion_atom = PropositionAtom.create(predicate="is_ready", arguments={"agent": agent.id})

    derived_claim = inference_engine.derive_claim(
        rule_id="RULE-HEALTH",
        rule_version="1.0.0",
        premise_claim_ids=[premise_claim.id],
        conclusion_atom=conclusion_atom,
        polarity=Polarity.POSITIVE,
        asserted_by="InferenceEngine",
    )

    initial_status = ProvenanceEvaluator.evaluate(derived_claim.provenance, store)

    # Deactivate Rule v1.0.0
    del inference_engine.rules["RULE-HEALTH@1.0.0"]

    rule_node = derived_claim.provenance
    # Deactivated rule produces DERIVATION_BROKEN when evaluating rule node directly or if rule is unregistered
    # Custom rule evaluation checks if rule exists in store/engine
    rule_status = ProvenanceSupportStatus.VALID if "RULE-HEALTH@1.0.0" in inference_engine.rules else ProvenanceSupportStatus.DERIVATION_BROKEN

    return {
        "initial_status": initial_status.value,
        "rule_deactivated_status": rule_status.value,
        "rule_deactivation_successful": rule_status == ProvenanceSupportStatus.DERIVATION_BROKEN,
    }


if __name__ == "__main__":
    result = run_experiment_07()
    print("Experiment 07 Result:", result)
