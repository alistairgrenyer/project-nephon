from __future__ import annotations

from enum import Enum


class Polarity(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


class TrustLevel(str, Enum):
    CONSTITUTIONAL = "constitutional"
    STEWARD_AUTHORIZED = "steward_authorized"
    DELEGATED_OPERATIONAL = "delegated_operational"
    VERIFIED_SYSTEM = "verified_system"
    UNTRUSTED_INPUT = "untrusted_input"


class AuthorityLevel(str, Enum):
    CONSTITUTIONAL = "constitutional"
    STEWARD_AUTHORIZED = "steward_authorized"
    DELEGATED_OPERATIONAL = "delegated_operational"
    VERIFIED_SYSTEM = "verified_system"
    UNTRUSTED_INPUT = "untrusted_input"


class EpistemicMode(str, Enum):
    DOGMATIC_TEACHING = "dogmatic_teaching"
    CONCILIAR_DEFINITION = "conciliar_definition"
    PATRISTIC_CONSENSUS = "patristic_consensus"
    PHILOSOPHICAL_INFERENCE = "philosophical_inference"
    CONSTITUTIONAL_JUDGEMENT = "constitutional_judgement"
    OPERATIONAL_RULE = "operational_rule"
    OBSERVATION = "observation"
    DERIVED_INFERENCE = "derived_inference"


class BeliefStatus(str, Enum):
    UNKNOWN = "unknown"
    SUPPORTED = "supported"
    REJECTED = "rejected"
    CONFLICTED = "conflicted"


class ProvenanceSupportStatus(str, Enum):
    VALID = "valid"
    CURRENTLY_UNSUPPORTED = "currently_unsupported"
    DERIVATION_BROKEN = "derivation_broken"


class GovernanceDisposition(str, Enum):
    PERMIT = "permit"
    REFUSE = "refuse"
    DEFER = "defer"
    REQUIRE_EVIDENCE = "require_evidence"


class ExecutionState(str, Enum):
    AUTHORIZED = "authorized"
    CLAIMED = "claimed"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    EXPIRED = "expired"
    REJECTED = "rejected"
    REQUIRES_RECONCILIATION = "requires_reconciliation"


class RiskClass(str, Enum):
    READ_ONLY = "read_only"
    REVERSIBLE_MUTATION = "reversible_mutation"
    PRIVILEGED_MUTATION = "privileged_mutation"
    IRREVERSIBLE_MUTATION = "irreversible_mutation"
