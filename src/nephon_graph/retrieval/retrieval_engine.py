from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, Field
from nephon_graph.core.belief import BeliefState, BeliefStatus
from nephon_graph.core.claims import Claim
from nephon_graph.core.contexts import Context
from nephon_graph.core.provenance import RuleNode, SourceLeaf, ClaimLeaf
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

    def _format_provenance(self, claim: Claim, indent: str = "    ") -> list[str]:
        lines: list[str] = []
        prov = claim.provenance

        if isinstance(prov, RuleNode):
            lines.append(f"{indent}Rule Provenance: {prov.rule_id} (v{prov.rule_version})")
            lines.append(f"{indent}Premises:")
            for p_leaf in prov.premises:
                p_claim = self.store.get_claim(p_leaf.claim_id)
                if p_claim:
                    atom = self.store.get_atom(p_claim.proposition_id)
                    pred = atom.predicate if atom else "unknown"
                    ref = p_claim.provenance.ref_id if isinstance(p_claim.provenance, SourceLeaf) else str(p_claim.id)
                    lines.append(
                        f"{indent}  - Premise Claim: {pred} (Polarity: {p_claim.polarity.value}, Mode: {p_claim.epistemic_mode.value}, Source: {ref})"
                    )
        elif isinstance(prov, SourceLeaf):
            lines.append(f"{indent}Source Leaf: {prov.kind.value} ({prov.ref_id})")

        return lines

    def retrieve_for_context(
        self, target_context: Context, proposition_ids: list[UUID] | None = None
    ) -> ContextRetrievalPayload:
        if proposition_ids is None:
            # Query all registered proposition atoms
            proposition_ids = self.store.list_atom_ids()


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
            gov_decision = self.governance_policy.evaluate(
                all_active, target_context, belief_state=belief, predicate=atom.predicate
            )

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
            prompt_lines.append(f"  Operational Disposition: {gov_decision.disposition.value.upper()}")
            if gov_decision.governing_claim:
                gc = gov_decision.governing_claim
                prompt_lines.append(
                    f"  Governing Claim: {gc.polarity.value.upper()} (Authority: {gc.authority_level.value}, Mode: {gc.epistemic_mode.value})"
                )
                prompt_lines.extend(self._format_provenance(gc, indent="  "))
            prompt_lines.append(f"  Explanation: {belief.explanation}")

        prompt_text = "\n".join(prompt_lines)

        return ContextRetrievalPayload(
            target_context=target_context,
            retrieved_results=results,
            prompt_context_text=prompt_text,
        )
