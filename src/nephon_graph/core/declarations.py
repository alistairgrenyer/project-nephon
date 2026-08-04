from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel
from nephon_graph.core.claims import AuthorityLevel, EpistemicMode
from nephon_graph.core.propositions import PropositionAtom


class PropositionDeclaration(BaseModel):
    """
    Pathway A: Authored constitutional declaration mapping directly to canonical PropositionAtom and Claim.
    Does not depend on LLM text interpretation.
    """
    proposition_id: str  # e.g., "GRD-01", "AUT-04"
    expression_id: UUID
    declared_atom: PropositionAtom
    declared_by: str
    authority_level: AuthorityLevel
    epistemic_mode: EpistemicMode
