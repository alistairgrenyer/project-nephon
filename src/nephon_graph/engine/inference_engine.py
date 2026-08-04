from __future__ import annotations

from uuid import UUID, uuid4
from nephon_graph.core.belief import ProvenanceSupportStatus
from nephon_graph.core.claims import AuthorityLevel, Claim, EpistemicMode, Polarity, TrustLevel
from nephon_graph.core.contexts import Context
from nephon_graph.core.events import KnowledgeEvent
from nephon_graph.core.inference import InferenceRule
from nephon_graph.core.propositions import PropositionAtom
from nephon_graph.core.provenance import ClaimLeaf, RuleNode
from nephon_graph.engine.context_algebra import ContextAlgebra
from nephon_graph.engine.provenance_evaluator import ProvenanceEvaluator
from nephon_graph.storage.base import EventStore


class InferenceError(Exception):
    """Raised when an inference derivation fails validation."""
    pass


class InferenceEngine:
    """
    Deterministic inference engine executing versioned InferenceRules to produce derived claims.
    Enforces premise activation, valid context intersection, and DAG cycle prevention.
    """

    def __init__(self, store: EventStore) -> None:
        self.store = store
        self.rules: dict[str, InferenceRule] = {}

    def register_rule(self, rule: InferenceRule) -> None:
        key = f"{rule.rule_id}@{rule.version}"
        self.rules[key] = rule

    def derive_claim(
        self,
        rule_id: str,
        rule_version: str,
        premise_claim_ids: list[UUID],
        conclusion_atom: PropositionAtom,
        polarity: Polarity,
        asserted_by: str,
        trust_level: TrustLevel = TrustLevel.DELEGATED_OPERATIONAL,
        authority_level: AuthorityLevel = AuthorityLevel.DELEGATED_OPERATIONAL,
        epistemic_mode: EpistemicMode = EpistemicMode.DERIVED_INFERENCE,
    ) -> Claim:
        key = f"{rule_id}@{rule_version}"
        if key not in self.rules:
            raise InferenceError(f"Rule '{key}' is not registered.")

        rule = self.rules[key]

        # 1. Validate premises exist, are active, and have valid provenance
        premise_claims: list[Claim] = []
        for cid in premise_claim_ids:
            claim = self.store.get_claim(cid)
            if claim is None:
                raise InferenceError(f"Premise claim '{cid}' does not exist.")
            if not self.store.is_claim_active(cid):
                raise InferenceError(f"Premise claim '{cid}' is not currently active.")
            if ProvenanceEvaluator.evaluate(claim.provenance, self.store) != ProvenanceSupportStatus.VALID:
                raise InferenceError(f"Premise claim '{cid}' provenance is not VALID.")
            premise_claims.append(claim)

        # 1b. Validate premise predicates match rule signature
        if rule.premise_predicates:
            if len(premise_claim_ids) != len(rule.premise_predicates):
                raise InferenceError(
                    f"Rule '{rule.rule_id}' expects {len(rule.premise_predicates)} premises, "
                    f"got {len(premise_claim_ids)}."
                )
            for idx, (cid, claim) in enumerate(zip(premise_claim_ids, premise_claims)):
                expected_pred = rule.premise_predicates[idx].strip().lower()
                atom = self.store.get_atom(claim.proposition_id)
                if atom is None:
                    raise InferenceError(f"Premise claim '{cid}' proposition atom does not exist.")
                if atom.predicate.strip().lower() != expected_pred:
                    raise InferenceError(
                        f"Premise claim at index {idx} has predicate '{atom.predicate}', "
                        f"rule '{rule.rule_id}' expects '{expected_pred}'."
                    )


        # 2. Intersect premise contexts
        current_context = premise_claims[0].context
        for claim in premise_claims[1:]:
            intersected = ContextAlgebra.intersect_contexts(current_context, claim.context)
            if intersected is None:
                raise InferenceError(
                    f"Premise contexts cannot be intersected cleanly (INDETERMINATE or EMPTY)."
                )
            current_context = intersected

        # 3. Create derived claim ID and RuleNode provenance
        derived_claim_id = uuid4()
        rule_provenance = RuleNode(
            rule_id=rule.rule_id,
            rule_version=rule.version,
            premises=tuple(ClaimLeaf(claim_id=cid) for cid in premise_claim_ids),
        )

        # 4. Check for Provenance DAG cycle
        # Ensure derived_claim_id does not appear in recursive provenance evaluation of premises
        for claim in premise_claims:
            visited: set[UUID] = {derived_claim_id}
            if ProvenanceEvaluator.evaluate(claim.provenance, self.store, visited) == ProvenanceSupportStatus.DERIVATION_BROKEN:
                raise InferenceError("Provenance cycle detected in inference derivation.")

        # 5. Create derived Claim
        derived_claim = Claim(
            id=derived_claim_id,
            proposition_id=conclusion_atom.id,
            polarity=polarity,
            context=current_context,
            provenance=rule_provenance,
            asserted_by=asserted_by,
            trust_level=trust_level,
            authority_level=authority_level,
            epistemic_mode=epistemic_mode,
        )

        # 6. Register claim and append events
        self.store.register_atom(conclusion_atom)
        self.store.register_claim(derived_claim)

        self.store.append(
            KnowledgeEvent(
                aggregate_id=str(derived_claim.id),
                aggregate_version=1,
                event_type="ClaimCreated",
                payload={
                    "claim_id": str(derived_claim.id),
                    "rule_id": rule_id,
                    "rule_version": rule_version,
                },
            )
        )
        self.store.append(
            KnowledgeEvent(
                aggregate_id=str(derived_claim.id),
                aggregate_version=2,
                event_type="ClaimActivated",
                payload={"claim_id": str(derived_claim.id)},
            )
        )

        return derived_claim
