from __future__ import annotations

from uuid import UUID
from nephon_graph.core.claims import Claim
from nephon_graph.core.events import KnowledgeEvent
from nephon_graph.core.propositions import PropositionAtom
from nephon_graph.storage.base import ConcurrencyError, EventIntegrityError


class InMemoryEventStore:
    """
    In-memory monotonic event store with full-envelope idempotency,
    strict aggregate versioning, and rebuildable materialized state index.
    """

    def __init__(self) -> None:
        self._events: list[KnowledgeEvent] = []
        self._events_by_id: dict[UUID, KnowledgeEvent] = {}
        self._aggregate_versions: dict[str, int] = {}
        self._sequence_counter: int = 0

        # Materialized indexes
        self._atoms: dict[UUID, PropositionAtom] = {}
        self._claims: dict[UUID, Claim] = {}
        self._active_claim_ids: set[UUID] = set()
        self._claims_by_atom: dict[UUID, list[UUID]] = {}

    def register_atom(self, atom: PropositionAtom) -> None:
        self._atoms[atom.id] = atom

    def get_atom(self, atom_id: UUID) -> PropositionAtom | None:
        return self._atoms.get(atom_id)

    def register_claim(self, claim: Claim) -> None:
        """Register a claim object so materialized indexes can dereference it by ID."""
        self._claims[claim.id] = claim
        if claim.proposition_id not in self._claims_by_atom:
            self._claims_by_atom[claim.proposition_id] = []
        if claim.id not in self._claims_by_atom[claim.proposition_id]:
            self._claims_by_atom[claim.proposition_id].append(claim.id)

    def get_claim(self, claim_id: UUID) -> Claim | None:
        return self._claims.get(claim_id)

    def get_claims_for_atom(self, proposition_id: UUID) -> list[Claim]:
        claim_ids = self._claims_by_atom.get(proposition_id, [])
        return [self._claims[cid] for cid in claim_ids if cid in self._claims]

    def is_claim_active(self, claim_id: UUID) -> bool:
        return claim_id in self._active_claim_ids

    def append(self, event: KnowledgeEvent) -> KnowledgeEvent:
        """
        Appends a KnowledgeEvent enforcing:
        1. Full-envelope idempotency check for duplicate event_id.
        2. Strict aggregate version increment.
        3. Monotonic sequence counter.
        """
        # 1. Idempotency & Envelope Integrity Check
        if event.event_id in self._events_by_id:
            existing = self._events_by_id[event.event_id]
            # Compare complete full envelope fields (ignoring sequence assigned by store)
            if (
                existing.event_type == event.event_type
                and existing.aggregate_id == event.aggregate_id
                and existing.aggregate_version == event.aggregate_version
                and existing.occurred_at == event.occurred_at
                and existing.causation_id == event.causation_id
                and existing.correlation_id == event.correlation_id
                and existing.payload == event.payload
            ):
                return existing  # Idempotent no-op
            else:
                raise EventIntegrityError(
                    f"Event ID {event.event_id} already exists with different envelope fields."
                )

        # 2. Sequential Aggregate Versioning Check
        current_version = self._aggregate_versions.get(event.aggregate_id, 0)
        if event.aggregate_version != current_version + 1:
            raise ConcurrencyError(
                f"Aggregate '{event.aggregate_id}' expected version {current_version + 1}, "
                f"got {event.aggregate_version}."
            )

        # 3. Assign sequence & append
        self._sequence_counter += 1
        stamped_event = event.model_copy(update={"sequence": self._sequence_counter})

        self._events.append(stamped_event)
        self._events_by_id[stamped_event.event_id] = stamped_event
        self._aggregate_versions[stamped_event.aggregate_id] = stamped_event.aggregate_version

        # 4. Apply to materialized index
        self._apply_event_to_materialized_index(stamped_event)

        return stamped_event

    def get_events(self, aggregate_id: str | None = None) -> list[KnowledgeEvent]:
        if aggregate_id is None:
            return list(self._events)
        return [e for e in self._events if e.aggregate_id == aggregate_id]

    def _apply_event_to_materialized_index(self, event: KnowledgeEvent) -> None:
        """Apply a single event to active materialized state indexes."""
        if event.event_type == "ClaimCreated":
            pass  # Claim registration is handled via register_claim
        elif event.event_type == "ClaimActivated":
            claim_id_str = event.payload.get("claim_id") or event.aggregate_id
            try:
                cid = UUID(claim_id_str)
                self._active_claim_ids.add(cid)
            except ValueError:
                pass
        elif event.event_type in ("ClaimRetracted", "ClaimSuperseded", "ClaimExpired"):
            claim_id_str = event.payload.get("claim_id") or event.aggregate_id
            try:
                cid = UUID(claim_id_str)
                self._active_claim_ids.discard(cid)
            except ValueError:
                pass

    def rebuild_materialized_index(self) -> None:
        """Rebuild materialized indexes from scratch by replaying the event stream."""
        self._active_claim_ids.clear()
        for event in self._events:
            self._apply_event_to_materialized_index(event)

    def fork(self) -> InMemoryEventStore:
        """Create an independent snapshot by replaying events into a new store."""
        forked = InMemoryEventStore()
        for event in self._events:
            forked._events.append(event)
            forked._events_by_id[event.event_id] = event
            forked._aggregate_versions[event.aggregate_id] = event.aggregate_version
            forked._sequence_counter = max(forked._sequence_counter, event.sequence)
        for atom_id, atom in self._atoms.items():
            forked._atoms[atom_id] = atom
        for claim_id, claim in self._claims.items():
            forked._claims[claim_id] = claim
        for atom_id, claim_ids in self._claims_by_atom.items():
            forked._claims_by_atom[atom_id] = list(claim_ids)
        forked._active_claim_ids = set(self._active_claim_ids)
        return forked

