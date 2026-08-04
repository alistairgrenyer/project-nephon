"""
Nephon Contracts Package — Public DTOs, Enums, Contexts, and Serialization.
This package has zero internal dependencies on nephon-core or private modules.
"""

from nephon_contracts.canonical_json import compute_nephon_canonical_json_v1, compute_request_hash
from nephon_contracts.contexts import Context, ContextConstraint, ContextConstraintKind
from nephon_contracts.dto import (
    ActionRequest,
    ConstitutionalDecision,
    ExecutionAuthorizationPayload,
    ExecutionReceipt,
    ObservationClaim,
    SignedExecutionToken,
)
from nephon_contracts.enums import (
    AuthorityLevel,
    BeliefStatus,
    EpistemicMode,
    ExecutionState,
    GovernanceDisposition,
    Polarity,
    ProvenanceSupportStatus,
    RiskClass,
    TrustLevel,
)
from nephon_contracts.propositions import NEPHON_ATOM_NAMESPACE, PropositionAtom, compute_atom_id

__all__ = [
    "compute_nephon_canonical_json_v1",
    "compute_request_hash",
    "ContextConstraintKind",
    "ContextConstraint",
    "Context",
    "ActionRequest",
    "ConstitutionalDecision",
    "ExecutionReceipt",
    "ExecutionAuthorizationPayload",
    "SignedExecutionToken",
    "ObservationClaim",
    "Polarity",
    "TrustLevel",
    "AuthorityLevel",
    "EpistemicMode",
    "BeliefStatus",
    "ProvenanceSupportStatus",
    "GovernanceDisposition",
    "ExecutionState",
    "RiskClass",
    "NEPHON_ATOM_NAMESPACE",
    "PropositionAtom",
    "compute_atom_id",
]
