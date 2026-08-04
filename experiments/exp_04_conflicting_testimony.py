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


def run_experiment_04():
    """
    Exp 04: Positive and negative claims in the same universal context.
    Verifies that BeliefEvaluator yields CONFLICTED status.
    """
    store = InMemoryEventStore()

    agent = Entity(name="Nephon", entity_type="agent")
    service = Entity(name="PostgresContainer", entity_type="system")

    atom = PropositionAtom.create(
        predicate="service_online",
        arguments={"agent": agent.id, "service": service.id},
    )
    store.register_atom(atom)

    context = Context.universal()

    pos_claim = Claim(
        proposition_id=atom.id,
        polarity=Polarity.POSITIVE,
        context=context,
        provenance=SourceLeaf(kind=SourceKind.EXTERNAL, ref_id="telemetry_ping_ok"),
        asserted_by="TelemetryAgent",
        trust_level=TrustLevel.VERIFIED_SYSTEM,
        authority_level=AuthorityLevel.VERIFIED_SYSTEM,
        epistemic_mode=EpistemicMode.OBSERVATION,
    )
    store.register_claim(pos_claim)

    neg_claim = Claim(
        proposition_id=atom.id,
        polarity=Polarity.NEGATIVE,
        context=context,
        provenance=SourceLeaf(kind=SourceKind.EXTERNAL, ref_id="error_log_500"),
        asserted_by="MonitoringAgent",
        trust_level=TrustLevel.VERIFIED_SYSTEM,
        authority_level=AuthorityLevel.VERIFIED_SYSTEM,
        epistemic_mode=EpistemicMode.OBSERVATION,
    )
    store.register_claim(neg_claim)

    for c in [pos_claim, neg_claim]:
        store.append(KnowledgeEvent(aggregate_id=str(c.id), aggregate_version=1, event_type="ClaimCreated"))
        store.append(KnowledgeEvent(aggregate_id=str(c.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(c.id)}))

    belief = BeliefEvaluator.evaluate(atom.id, context, store)

    return {
        "status": belief.status.value,
        "is_conflicted": belief.status == BeliefStatus.CONFLICTED,
        "positive_claims_count": len(belief.positive_claims),
        "negative_claims_count": len(belief.negative_claims),
    }


if __name__ == "__main__":
    result = run_experiment_04()
    print("Experiment 04 Result:", result)
