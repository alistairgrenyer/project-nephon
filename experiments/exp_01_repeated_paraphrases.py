from __future__ import annotations

from nephon_graph.core.claims import AuthorityLevel, Claim, EpistemicMode, Polarity, TrustLevel
from nephon_graph.core.contexts import Context
from nephon_graph.core.entities import Entity
from nephon_graph.core.expressions import Expression
from nephon_graph.core.interpretations import Interpretation, MappingType
from nephon_graph.core.propositions import PropositionAtom
from nephon_graph.core.provenance import SourceKind, SourceLeaf
from nephon_graph.storage.event_store import InMemoryEventStore


def run_experiment_01():
    """
    Exp 01: Input 10 natural language paraphrases derived from 1 underlying source.
    Verifies that 10 expressions map to 1 canonical proposition atom.
    """
    store = InMemoryEventStore()

    steward = Entity(name="Alistair", entity_type="person")
    nephon = Entity(name="Nephon", entity_type="agent")

    # 1. Ten paraphrases derived from one original statement
    paraphrase_texts = [
        "Alistair administers Nephon.",
        "Nephon is administered by Alistair.",
        "Alistair acts as Nephon's steward.",
        "Nephon is under Alistair's administration.",
        "Alistair manages Nephon.",
        "Nephon's steward is Alistair.",
        "Alistair holds administrative authority over Nephon.",
        "Nephon is stewarded by Alistair.",
        "Alistair directs Nephon's operational administration.",
        "Nephon receives stewardship from Alistair.",
    ]

    expressions: list[Expression] = []
    for text in paraphrase_texts:
        expr = Expression(text=text, source_uri="10-homilia/session-01.md", speaker_or_author="Alistair")
        expressions.append(expr)

    # 2. Map all 10 expressions to 1 canonical proposition atom: administers(Alistair, Nephon)
    atom = PropositionAtom.create(
        predicate="administers",
        arguments={"administrator": steward.id, "subject": nephon.id},
    )
    store.register_atom(atom)

    interpretations: list[Interpretation] = []
    for expr in expressions:
        interp = Interpretation(
            expression_id=expr.id,
            proposition_id=atom.id,
            mapping_type=MappingType.EXACT,
            confidence=0.98,
            interpreter="fixture:exp01",
            rationale="Paraphrase compression to canonical atom administers(Alistair, Nephon)",
        )
        interpretations.append(interp)

    # 3. Assert single canonical claim
    claim = Claim(
        proposition_id=atom.id,
        polarity=Polarity.POSITIVE,
        context=Context.universal(),
        provenance=SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="10-homilia/session-01.md"),
        asserted_by="Steward",
        trust_level=TrustLevel.STEWARD_AUTHORIZED,
        authority_level=AuthorityLevel.STEWARD_AUTHORIZED,
        epistemic_mode=EpistemicMode.OPERATIONAL_RULE,
    )
    store.register_claim(claim)

    return {
        "expressions_count": len(expressions),
        "interpretations_count": len(interpretations),
        "atom_count": len(store._atoms),
        "claim_count": len(store._claims),
        "atom_id": str(atom.id),
    }


if __name__ == "__main__":
    result = run_experiment_01()
    print("Experiment 01 Result:", result)
