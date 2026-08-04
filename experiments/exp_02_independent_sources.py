from __future__ import annotations

from nephon_graph.core.belief import ProvenanceSupportStatus
from nephon_graph.core.claims import AuthorityLevel, Claim, EpistemicMode, Polarity, TrustLevel
from nephon_graph.core.contexts import Context
from nephon_graph.core.entities import Entity
from nephon_graph.core.propositions import PropositionAtom
from nephon_graph.core.provenance import AnyNode, SourceKind, SourceLeaf
from nephon_graph.engine.provenance_evaluator import ProvenanceEvaluator
from nephon_graph.storage.event_store import InMemoryEventStore


def run_experiment_02():
    """
    Exp 02: 1 proposition atom supported by 2 independent sources via AnyNode.
    Verifies that independent support paths remain visible and surviving.
    """
    store = InMemoryEventStore()

    steward = Entity(name="Alistair", entity_type="person")
    nephon = Entity(name="Nephon", entity_type="agent")

    atom = PropositionAtom.create(
        predicate="holds_jurisdiction",
        arguments={"authority": steward.id, "subject": nephon.id},
    )
    store.register_atom(atom)

    source1 = SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="05_AUTHORITY_AND_OBEDIENCE.md#AUT-01")
    source2 = SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="SYSTEM_CHARTER.md#CHARTER-03")

    combined_provenance = AnyNode(children=(source1, source2))

    claim = Claim(
        proposition_id=atom.id,
        polarity=Polarity.POSITIVE,
        context=Context.universal(),
        provenance=combined_provenance,
        asserted_by="System",
        trust_level=TrustLevel.CONSTITUTIONAL,
        authority_level=AuthorityLevel.CONSTITUTIONAL,
        epistemic_mode=EpistemicMode.CONSTITUTIONAL_JUDGEMENT,
    )
    store.register_claim(claim)

    prov_status = ProvenanceEvaluator.evaluate(claim.provenance, store)

    return {
        "atom_count": 1,
        "independent_sources_count": 2,
        "provenance_status": prov_status.value,
        "valid": prov_status == ProvenanceSupportStatus.VALID,
    }


if __name__ == "__main__":
    result = run_experiment_02()
    print("Experiment 02 Result:", result)
