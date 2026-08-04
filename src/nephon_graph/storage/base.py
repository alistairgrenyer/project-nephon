from __future__ import annotations

from typing import Protocol
from uuid import UUID
from nephon_graph.core.claims import Claim
from nephon_graph.core.events import KnowledgeEvent
from nephon_graph.core.propositions import PropositionAtom


class EventIntegrityError(Exception):
    """Raised when an event ID is reused with a different envelope or payload."""
    pass


class ConcurrencyError(Exception):
    """Raised when an aggregate version is skipped, repeated, or out of sequence."""
    pass


class EventStore(Protocol):
    def append(self, event: KnowledgeEvent) -> KnowledgeEvent:
        ...

    def get_events(self, aggregate_id: str | None = None) -> list[KnowledgeEvent]:
        ...

    def register_atom(self, atom: PropositionAtom) -> None:
        ...

    def get_atom(self, atom_id: UUID) -> PropositionAtom | None:
        ...

    def register_claim(self, claim: Claim) -> None:
        ...

    def get_claim(self, claim_id: UUID) -> Claim | None:
        ...

    def get_claims_for_atom(self, proposition_id: UUID) -> list[Claim]:
        ...

    def is_claim_active(self, claim_id: UUID) -> bool:
        ...

    def rebuild_materialized_index(self) -> None:
        ...
