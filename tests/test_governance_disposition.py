import pytest
from nephon_graph.core.belief import BeliefStatus, BeliefState
from nephon_graph.core.claims import AuthorityLevel, Claim, Polarity, EpistemicMode, TrustLevel
from nephon_graph.core.contexts import Context
from nephon_graph.core.provenance import SourceKind, SourceLeaf
from nephon_graph.engine.governance_policy import (
    GovernancePolicy,
    GovernanceDisposition,
    DispositionRule,
)


def test_governance_disposition_resolution_rules():
    policy = GovernancePolicy()

    # Rule 1: permitted + POSITIVE + SUPPORTED -> PERMIT
    disp1 = policy.resolve_disposition("permitted", Polarity.POSITIVE, BeliefStatus.SUPPORTED)
    assert disp1 == GovernanceDisposition.PERMIT

    # Rule 2: permitted + NEGATIVE + REJECTED -> REFUSE
    disp2 = policy.resolve_disposition("permitted", Polarity.NEGATIVE, BeliefStatus.REJECTED)
    assert disp2 == GovernanceDisposition.REFUSE

    # Rule 3: established + NEGATIVE + REJECTED -> REQUIRE_EVIDENCE
    disp3 = policy.resolve_disposition("established", Polarity.NEGATIVE, BeliefStatus.REJECTED)
    assert disp3 == GovernanceDisposition.REQUIRE_EVIDENCE

    # Rule 4: CONFLICTED or UNKNOWN -> DEFER
    disp4 = policy.resolve_disposition("permitted", Polarity.POSITIVE, BeliefStatus.CONFLICTED)
    assert disp4 == GovernanceDisposition.DEFER

    disp5 = policy.resolve_disposition("permitted", Polarity.POSITIVE, BeliefStatus.UNKNOWN)
    assert disp5 == GovernanceDisposition.DEFER


def test_governance_policy_evaluates_disposition():
    policy = GovernancePolicy()
    context = Context.universal()

    claim = Claim(
        proposition_id=Claim.model_fields["id"].default_factory(),
        polarity=Polarity.NEGATIVE,
        context=context,
        provenance=SourceLeaf(kind=SourceKind.DOCUMENT, ref_id="doc1"),
        asserted_by="steward",
        trust_level=TrustLevel.CONSTITUTIONAL,
        authority_level=AuthorityLevel.CONSTITUTIONAL,
        epistemic_mode=EpistemicMode.CONSTITUTIONAL_JUDGEMENT,
    )

    belief = BeliefState(
        proposition_id=claim.proposition_id,
        status=BeliefStatus.REJECTED,
        positive_claims=[],
        negative_claims=[claim],
        explanation="Rejected by negative claim",
    )

    decision = policy.evaluate(
        claims=[claim],
        context=context,
        belief_state=belief,
        predicate="permitted",
    )

    assert decision.governing_claim == claim
    assert decision.disposition == GovernanceDisposition.REFUSE
    assert "REFUSE" in decision.rationale
