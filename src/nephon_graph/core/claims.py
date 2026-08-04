from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from nephon_graph.core.contexts import Context
from nephon_graph.core.provenance import ProvenanceNode


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


class Claim(BaseModel):
    """
    Asserted claim in a context with provenance and authority metadata.
    Immutable value object. Lifecycle state is derived dynamically from events.
    """
    id: UUID = Field(default_factory=uuid4)
    proposition_id: UUID
    polarity: Polarity
    context: Context
    provenance: ProvenanceNode
    asserted_by: str
    trust_level: TrustLevel
    authority_level: AuthorityLevel
    epistemic_mode: EpistemicMode
