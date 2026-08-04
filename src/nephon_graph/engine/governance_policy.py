from __future__ import annotations

from pydantic import BaseModel, Field
from nephon_graph.core.claims import AuthorityLevel, Claim
from nephon_graph.core.contexts import Context


class AuthorityOrder(BaseModel):
    ranks: dict[AuthorityLevel, int] = Field(
        default_factory=lambda: {
            AuthorityLevel.CONSTITUTIONAL: 100,
            AuthorityLevel.STEWARD_AUTHORIZED: 80,
            AuthorityLevel.DELEGATED_OPERATIONAL: 60,
            AuthorityLevel.VERIFIED_SYSTEM: 40,
            AuthorityLevel.UNTRUSTED_INPUT: 20,
        }
    )

    def get_rank(self, level: AuthorityLevel) -> int:
        return self.ranks.get(level, 0)


class GovernanceDecision(BaseModel):
    governing_claim: Claim | None = None
    authority_level: AuthorityLevel | None = None
    rationale: str = ""


class GovernancePolicy:
    """
    Determines operational governance decision based on AuthorityOrder ranking and policies.
    Does not rewrite or suppress underlying epistemic conflicts in BeliefEvaluator.
    """

    def __init__(self, authority_order: AuthorityOrder | None = None) -> None:
        self.authority_order = authority_order or AuthorityOrder()

    def evaluate(self, claims: list[Claim], context: Context) -> GovernanceDecision:
        if not claims:
            return GovernanceDecision(
                governing_claim=None,
                authority_level=None,
                rationale="No claims available for governance evaluation.",
            )

        # Sort claims descending by authority rank
        sorted_claims = sorted(
            claims,
            key=lambda c: self.authority_order.get_rank(c.authority_level),
            reverse=True,
        )

        top_claim = sorted_claims[0]
        top_rank = self.authority_order.get_rank(top_claim.authority_level)

        # Check if there is a tied claim with opposing polarity at the highest authority rank
        opposing_ties = [
            c for c in sorted_claims
            if self.authority_order.get_rank(c.authority_level) == top_rank
            and c.polarity != top_claim.polarity
        ]

        if opposing_ties:
            return GovernanceDecision(
                governing_claim=None,
                authority_level=top_claim.authority_level,
                rationale=(
                    f"Governance deadlock at authority rank {top_rank} ({top_claim.authority_level}): "
                    f"Equal authority positive and negative claims."
                ),
            )

        return GovernanceDecision(
            governing_claim=top_claim,
            authority_level=top_claim.authority_level,
            rationale=(
                f"Selected claim {top_claim.id} as governing directive with authority level "
                f"'{top_claim.authority_level}' (rank {top_rank})."
            ),
        )
