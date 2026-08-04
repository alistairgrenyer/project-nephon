from __future__ import annotations

from nephon_graph.core.belief import BeliefStatus
from nephon_graph.core.claims import AuthorityLevel, Claim, EpistemicMode, Polarity, TrustLevel
from nephon_graph.core.contexts import Context, ContextConstraint
from nephon_graph.core.entities import Entity
from nephon_graph.core.events import KnowledgeEvent
from nephon_graph.core.propositions import PropositionAtom
from nephon_graph.core.provenance import SourceKind, SourceLeaf
from nephon_graph.engine.belief_evaluator import BeliefEvaluator
from nephon_graph.storage.event_store import InMemoryEventStore


def run_experiment_03():
    """
    Exp 03: Dev permission positive claim vs Prod restriction negative claim.
    Verifies context discrimination prevents false contradictions.
    """
    store = InMemoryEventStore()

    agent = Entity(name="Nephon", entity_type="agent")
    system = Entity(name="HomelabCluster", entity_type="system")

    atom = PropositionAtom.create(
        predicate="permitted_to_deploy",
        arguments={"agent": agent.id, "system": system.id},
    )
    store.register_atom(atom)

    dev_context = Context(environment=ContextConstraint.exact("development"))
    prod_context = Context(environment=ContextConstraint.exact("production"))

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

    for c in [claim_dev, claim_prod]:
        store.append(KnowledgeEvent(aggregate_id=str(c.id), aggregate_version=1, event_type="ClaimCreated"))
        store.append(KnowledgeEvent(aggregate_id=str(c.id), aggregate_version=2, event_type="ClaimActivated", payload={"claim_id": str(c.id)}))

    dev_belief = BeliefEvaluator.evaluate(atom.id, dev_context, store)
    prod_belief = BeliefEvaluator.evaluate(atom.id, prod_context, store)

    return {
        "dev_status": dev_belief.status.value,
        "prod_status": prod_belief.status.value,
        "false_contradiction_count": 1 if dev_belief.status == BeliefStatus.CONFLICTED or prod_belief.status == BeliefStatus.CONFLICTED else 0,
    }


if __name__ == "__main__":
    result = run_experiment_03()
    print("Experiment 03 Result:", result)
