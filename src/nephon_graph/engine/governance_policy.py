from __future__ import annotations

from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field
from nephon_contracts.enums import GovernanceDisposition
from nephon_graph.core.belief import BeliefState, BeliefStatus
from nephon_graph.core.claims import AuthorityLevel, Claim, Polarity
from nephon_graph.core.contexts import Context
from nephon_graph.core.propositions import PropositionAtom



class DispositionRule(BaseModel):
    """Maps a (predicate, governing_polarity, belief_status) triple to an operational disposition."""
    predicate: str
    governing_polarity: Polarity
    belief_status: BeliefStatus
    disposition: GovernanceDisposition


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
    governing_claim_id: UUID | None = None
    authority_level: AuthorityLevel | None = None
    disposition: GovernanceDisposition = GovernanceDisposition.DEFER
    rationale: str = ""
    required_evidence: tuple[PropositionAtom, ...] = ()


class GovernancePolicy:
    """
    Determines operational governance decision based on AuthorityOrder ranking and DispositionRules.
    Does not rewrite or suppress underlying epistemic conflicts in BeliefEvaluator.
    """

    def __init__(
        self,
        authority_order: AuthorityOrder | None = None,
        disposition_rules: tuple[DispositionRule, ...] | None = None,
    ) -> None:
        self.authority_order = authority_order or AuthorityOrder()
        self.disposition_rules = disposition_rules or (
            DispositionRule(
                predicate="permitted",
                governing_polarity=Polarity.POSITIVE,
                belief_status=BeliefStatus.SUPPORTED,
                disposition=GovernanceDisposition.PERMIT,
            ),
            DispositionRule(
                predicate="permitted",
                governing_polarity=Polarity.NEGATIVE,
                belief_status=BeliefStatus.REJECTED,
                disposition=GovernanceDisposition.REFUSE,
            ),
            DispositionRule(
                predicate="established",
                governing_polarity=Polarity.NEGATIVE,
                belief_status=BeliefStatus.REJECTED,
                disposition=GovernanceDisposition.REQUIRE_EVIDENCE,
            ),
        )

    def resolve_disposition(
        self, predicate: str, polarity: Polarity, belief_status: BeliefStatus
    ) -> GovernanceDisposition:
        if belief_status in (BeliefStatus.CONFLICTED, BeliefStatus.UNKNOWN):
            return GovernanceDisposition.DEFER

        norm_pred = predicate.strip().lower()
        for rule in self.disposition_rules:
            if (
                rule.predicate.strip().lower() == norm_pred
                and rule.governing_polarity == polarity
                and rule.belief_status == belief_status
            ):
                return rule.disposition

        # Generic fallbacks
        if polarity == Polarity.POSITIVE and belief_status == BeliefStatus.SUPPORTED:
            return GovernanceDisposition.PERMIT
        if polarity == Polarity.NEGATIVE and belief_status == BeliefStatus.REJECTED:
            return GovernanceDisposition.REFUSE

        return GovernanceDisposition.DEFER

    def evaluate(
        self,
        claims: list[Claim],
        context: Context,
        belief_state: BeliefState | None = None,
        predicate: str | None = None,
    ) -> GovernanceDecision:
        if not claims:
            return GovernanceDecision(
                governing_claim=None,
                governing_claim_id=None,
                authority_level=None,
                disposition=GovernanceDisposition.DEFER,
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
            c
            for c in sorted_claims
            if self.authority_order.get_rank(c.authority_level) == top_rank
            and c.polarity != top_claim.polarity
        ]

        if opposing_ties:
            return GovernanceDecision(
                governing_claim=None,
                governing_claim_id=None,
                authority_level=top_claim.authority_level,
                disposition=GovernanceDisposition.DEFER,
                rationale=(
                    f"Governance deadlock at authority rank {top_rank} ({top_claim.authority_level}): "
                    f"Equal authority positive and negative claims."
                ),
            )

        # Determine disposition
        b_status = belief_state.status if belief_state else BeliefStatus.SUPPORTED
        pred = predicate or "permitted"
        disposition = self.resolve_disposition(pred, top_claim.polarity, b_status)

        return GovernanceDecision(
            governing_claim=top_claim,
            governing_claim_id=top_claim.id,
            authority_level=top_claim.authority_level,
            disposition=disposition,
            rationale=(
                f"Selected claim {top_claim.id} as governing directive with authority level "
                f"'{top_claim.authority_level}' (rank {top_rank}). Disposition: {disposition.value.upper()}."
            ),
        )
