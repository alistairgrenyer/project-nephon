from __future__ import annotations

from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from nephon_contracts.enums import AuthorityLevel, EpistemicMode, Polarity, TrustLevel
from nephon_graph.core.contexts import Context
from nephon_graph.core.provenance import ProvenanceNode



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
