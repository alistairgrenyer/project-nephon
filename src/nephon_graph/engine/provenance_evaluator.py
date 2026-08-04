from __future__ import annotations

from uuid import UUID
from nephon_graph.core.belief import ProvenanceSupportStatus
from nephon_graph.core.provenance import (
    AllNode,
    AnyNode,
    ClaimLeaf,
    ProvenanceNode,
    RuleNode,
    SourceLeaf,
)
from nephon_graph.storage.base import EventStore


class ProvenanceEvaluator:
    """
    Evaluates dynamic ProvenanceNode AST support status against active event store state.
    """

    @classmethod
    def evaluate(cls, node: ProvenanceNode, store: EventStore, visited_claims: set[UUID] | None = None) -> ProvenanceSupportStatus:
        if visited_claims is None:
            visited_claims = set()

        if isinstance(node, SourceLeaf):
            if not node.ref_id:
                return ProvenanceSupportStatus.DERIVATION_BROKEN
            return ProvenanceSupportStatus.VALID

        elif isinstance(node, ClaimLeaf):
            if node.claim_id in visited_claims:
                # Cycle detected!
                return ProvenanceSupportStatus.DERIVATION_BROKEN
            visited_claims.add(node.claim_id)

            claim = store.get_claim(node.claim_id)
            if claim is None:
                return ProvenanceSupportStatus.DERIVATION_BROKEN

            if not store.is_claim_active(node.claim_id):
                return ProvenanceSupportStatus.CURRENTLY_UNSUPPORTED

            # Recursively evaluate the claim's own provenance
            return cls.evaluate(claim.provenance, store, visited_claims)

        elif isinstance(node, AllNode):
            statuses = [cls.evaluate(child, store, set(visited_claims)) for child in node.children]
            if any(s == ProvenanceSupportStatus.DERIVATION_BROKEN for s in statuses):
                return ProvenanceSupportStatus.DERIVATION_BROKEN
            if any(s == ProvenanceSupportStatus.CURRENTLY_UNSUPPORTED for s in statuses):
                return ProvenanceSupportStatus.CURRENTLY_UNSUPPORTED
            return ProvenanceSupportStatus.VALID

        elif isinstance(node, AnyNode):
            statuses = [cls.evaluate(child, store, set(visited_claims)) for child in node.children]
            if any(s == ProvenanceSupportStatus.VALID for s in statuses):
                return ProvenanceSupportStatus.VALID
            if any(s == ProvenanceSupportStatus.CURRENTLY_UNSUPPORTED for s in statuses):
                return ProvenanceSupportStatus.CURRENTLY_UNSUPPORTED
            return ProvenanceSupportStatus.DERIVATION_BROKEN

        elif isinstance(node, RuleNode):
            if not node.rule_id or not node.rule_version:
                return ProvenanceSupportStatus.DERIVATION_BROKEN
            statuses = [cls.evaluate(premise, store, set(visited_claims)) for premise in node.premises]
            if any(s == ProvenanceSupportStatus.DERIVATION_BROKEN for s in statuses):
                return ProvenanceSupportStatus.DERIVATION_BROKEN
            if any(s == ProvenanceSupportStatus.CURRENTLY_UNSUPPORTED for s in statuses):
                return ProvenanceSupportStatus.CURRENTLY_UNSUPPORTED
            return ProvenanceSupportStatus.VALID

        return ProvenanceSupportStatus.DERIVATION_BROKEN
