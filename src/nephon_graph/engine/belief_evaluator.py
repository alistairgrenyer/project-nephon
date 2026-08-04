from __future__ import annotations

from uuid import UUID
from nephon_graph.core.belief import BeliefState, BeliefStatus, ProvenanceSupportStatus
from nephon_graph.core.claims import Claim, Polarity
from nephon_graph.core.contexts import Context
from nephon_graph.engine.context_algebra import ContextAlgebra
from nephon_graph.engine.provenance_evaluator import ProvenanceEvaluator
from nephon_graph.storage.base import EventStore


class BeliefEvaluator:
    """
    Evaluates epistemic belief status (SUPPORTED, REJECTED, CONFLICTED, UNKNOWN)
    for a canonical proposition atom within a target context.
    Preserves underlying epistemic conflicts regardless of authority.
    """

    @classmethod
    def evaluate(
        cls,
        proposition_id: UUID,
        target_context: Context,
        store: EventStore,
    ) -> BeliefState:
        all_claims = store.get_claims_for_atom(proposition_id)

        valid_positive_claims: list[Claim] = []
        valid_negative_claims: list[Claim] = []

        for claim in all_claims:
            # 1. Active lifecycle check
            if not store.is_claim_active(claim.id):
                continue

            # 2. Context compatibility check
            if not ContextAlgebra.are_compatible(claim.context, target_context):
                continue

            # 3. Provenance validation check
            provenance_status = ProvenanceEvaluator.evaluate(claim.provenance, store)
            if provenance_status != ProvenanceSupportStatus.VALID:
                continue

            # Classify by polarity
            if claim.polarity == Polarity.POSITIVE:
                valid_positive_claims.append(claim)
            elif claim.polarity == Polarity.NEGATIVE:
                valid_negative_claims.append(claim)

        # Determine status
        if len(valid_positive_claims) > 0 and len(valid_negative_claims) > 0:
            status = BeliefStatus.CONFLICTED
            explanation = (
                f"Conflicting testimony in target context: {len(valid_positive_claims)} positive "
                f"and {len(valid_negative_claims)} negative claims."
            )
        elif len(valid_positive_claims) > 0:
            status = BeliefStatus.SUPPORTED
            explanation = f"Supported by {len(valid_positive_claims)} valid positive claims."
        elif len(valid_negative_claims) > 0:
            status = BeliefStatus.REJECTED
            explanation = f"Rejected by {len(valid_negative_claims)} valid negative claims."
        else:
            status = BeliefStatus.UNKNOWN
            explanation = "No valid claims found for proposition in target context."

        return BeliefState(
            proposition_id=proposition_id,
            status=status,
            positive_claims=valid_positive_claims,
            negative_claims=valid_negative_claims,
            explanation=explanation,
        )
