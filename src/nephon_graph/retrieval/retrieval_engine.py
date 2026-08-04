from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, Field
from nephon_graph.core.belief import BeliefState, BeliefStatus
from nephon_graph.core.claims import Claim
from nephon_graph.core.contexts import Context
from nephon_graph.engine.belief_evaluator import BeliefEvaluator
from nephon_graph.engine.governance_policy import GovernanceDecision, GovernancePolicy
from nephon_graph.storage.base import EventStore


class RetrievedAtomResult(BaseModel):
    proposition_id: UUID
    predicate: str
    belief: BeliefState
    governance: GovernanceDecision
    active_claims: list[Claim] = Field(default_factory=list)


class ContextRetrievalPayload(BaseModel):
    target_context: Context
    retrieved_results: list[RetrievedAtomResult] = Field(default_factory=list)
    prompt_context_text: str = ""


class KernelRetrievalEngine:
    """
    Noise-resistant Kernel Retrieval Engine executing context matching,
    authority-ranked governance, belief status resolution, and prompt context compilation.
    """

    def __init__(self, store: EventStore, governance_policy: GovernancePolicy | None = None) -> None:
        self.store = store
        self.governance_policy = governance_policy or GovernancePolicy()

    def retrieve_for_context(
        self, target_context: Context, proposition_ids: list[UUID] | None = None
    ) -> ContextRetrievalPayload:
        if proposition_ids is None:
            # Query all registered proposition atoms
            proposition_ids = list(self.store._atoms.keys())

        results: list[RetrievedAtomResult] = []
        prompt_lines: list[str] = ["=== RETRIEVED NEPHON KERNEL CONTEXT ==="]

        for atom_id in proposition_ids:
            atom = self.store.get_atom(atom_id)
            if atom is None:
                continue

            belief = BeliefEvaluator.evaluate(atom_id, target_context, self.store)
            if belief.status == BeliefStatus.UNKNOWN:
                continue

            all_active = belief.positive_claims + belief.negative_claims
            gov_decision = self.governance_policy.evaluate(all_active, target_context)

            results.append(
                RetrievedAtomResult(
                    proposition_id=atom_id,
                    predicate=atom.predicate,
                    belief=belief,
                    governance=gov_decision,
                    active_claims=all_active,
                )
            )

            # Build readable prompt summary
            prompt_lines.append(f"\n[Proposition Atom: {atom.predicate} (ID: {atom.id})]")
            prompt_lines.append(f"  Epistemic Status: {belief.status.value.upper()}")
            if gov_decision.governing_claim:
                gc = gov_decision.governing_claim
                prompt_lines.append(
                    f"  Governing Directive: {gc.polarity.value.upper()} (Authority: {gc.authority_level.value}, Asserted By: {gc.asserted_by})"
                )
            prompt_lines.append(f"  Explanation: {belief.explanation}")

        prompt_text = "\n".join(prompt_lines)

        return ContextRetrievalPayload(
            target_context=target_context,
            retrieved_results=results,
            prompt_context_text=prompt_text,
        )
