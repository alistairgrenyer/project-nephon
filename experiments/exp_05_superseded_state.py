from __future__ import annotations

from nephon_graph.core.belief import BeliefStatus
from nephon_graph.core.claims import AuthorityLevel, Claim, EpistemicMode, Polarity, TrustLevel
from nephon_graph.core.contexts import Context
from nephon_graph.core.entities import Entity
from nephon_graph.core.events import KnowledgeEvent
from nephon_graph.core.propositions import PropositionAtom
from nephon_graph.core.provenance import SourceKind, SourceLeaf
from nephon_graph.engine.belief_evaluator import BeliefEvaluator
from nephon_graph.storage.event_store import InMemoryEventStore


def run_experiment_05():
    """
    Exp 05: Claim 1 (offline) superseded by Claim 2 (online).
    Verifies present state evaluates to SUPPORTED online while historical event log remains intact.
    """
    store = InMemoryEventStore()

    node = Entity(name="node-01", entity_type="system")

    atom = PropositionAtom.create(
        predicate="node_status_online",
        arguments={"node": node.id},
    )
    store.register_atom(atom)

    context = Context.universal()

    # Claim 1: Node offline (Negative claim at 10:00)
    claim1 = Claim(
        proposition_id=atom.id,
        polarity=Polarity.NEGATIVE,
        context=context,
        provenance=SourceLeaf(kind=SourceKind.EXTERNAL, ref_id="ping_10_00_failed"),
        asserted_by="Monitor",
        trust_level=TrustLevel.VERIFIED_SYSTEM,
        authority_level=AuthorityLevel.VERIFIED_SYSTEM,
        epistemic_mode=EpistemicMode.OBSERVATION,
    )
    store.register_claim(claim1)

    store.append(KnowledgeEvent(aggregate_id=str(claim1.id), aggregate_version=1, event_type="ClaimCreated"))
    store.append(KnowledgeEvent(aggregate_id=str(claim1.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(claim1.id)}))

    initial_belief = BeliefEvaluator.evaluate(atom.id, context, store)

    # Claim 2: Node online (Positive claim at 10:05 supersedes Claim 1)
    claim2 = Claim(
        proposition_id=atom.id,
        polarity=Polarity.POSITIVE,
        context=context,
        provenance=SourceLeaf(kind=SourceKind.EXTERNAL, ref_id="ping_10_05_success"),
        asserted_by="Monitor",
        trust_level=TrustLevel.VERIFIED_SYSTEM,
        authority_level=AuthorityLevel.VERIFIED_SYSTEM,
        epistemic_mode=EpistemicMode.OBSERVATION,
    )
    store.register_claim(claim2)

    store.append(KnowledgeEvent(aggregate_id=str(claim2.id), aggregate_version=1, event_type="ClaimCreated"))
    store.append(KnowledgeEvent(aggregate_id=str(claim2.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(claim2.id)}))
    # Retract/supersede claim1
    store.append(KnowledgeEvent(aggregate_id=str(claim1.id), aggregate_version=3, event_type="ClaimSuperseded", payload={"claim_id": str(claim1.id), "superseded_by": str(claim2.id)}))

    updated_belief = BeliefEvaluator.evaluate(atom.id, context, store)

    return {
        "initial_status": initial_belief.status.value,
        "updated_status": updated_belief.status.value,
        "claim1_active": store.is_claim_active(claim1.id),
        "claim2_active": store.is_claim_active(claim2.id),
        "total_events_in_history": len(store.get_events()),
    }


if __name__ == "__main__":
    result = run_experiment_05()
    print("Experiment 05 Result:", result)
