from __future__ import annotations

import hashlib
import json
import unicodedata
import uuid
from uuid import UUID
from pathlib import Path
from pydantic import BaseModel, Field

from nephon_graph.core.claims import AuthorityLevel, Claim, EpistemicMode, Polarity, TrustLevel
from nephon_graph.core.contexts import Context
from nephon_graph.core.events import KnowledgeEvent
from nephon_graph.core.propositions import PropositionAtom
from nephon_graph.core.provenance import SourceKind, SourceLeaf
from nephon_graph.compiler.markdown_loader import MarkdownLoader, ParsedMarkdownDocument, ParsedPropositionBlock
from nephon_graph.storage.base import EventStore

# PERMANENT random UUIDv4 namespaces committed in Phase 1C
NEPHON_ENTITY_NAMESPACE = UUID("e9a6a585-ff13-41f4-bf73-ccdf365ec5fe")
NEPHON_COMPILER_NAMESPACE = UUID("f573f3ef-29f4-48d3-84c6-9b6d5e2549ce")


class CompilerIntegrityError(Exception):
    """Raised when compilation violates revision monotonicity or content hash integrity."""
    pass


def compute_entity_id(entity_type: str, canonical_name: str) -> UUID:
    """Computes a deterministic UUIDv5 for an entity with NFC normalization."""
    norm_type = unicodedata.normalize("NFC", entity_type.strip().lower())
    norm_name = unicodedata.normalize("NFC", canonical_name.strip().lower())
    canonical = f"{norm_type}:{norm_name}"
    return uuid.uuid5(NEPHON_ENTITY_NAMESPACE, canonical)


def compute_declaration_content_hash(declaration: dict) -> str:
    """SHA-256 over NFC-normalized canonical JSON of the parsed declaration."""
    normalized = unicodedata.normalize("NFC", json.dumps(declaration, sort_keys=True, separators=(",", ":")))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_compiler_event_id(
    declaration_id: str, declaration_revision: int, content_hash: str, event_type: str
) -> UUID:
    """Computes deterministic UUIDv5 event ID based on declaration revision and content hash."""
    key = f"{declaration_id}|rev{declaration_revision}|{content_hash}|{event_type}"
    return uuid.uuid5(NEPHON_COMPILER_NAMESPACE, key)


class CompilationResult(BaseModel):
    declaration_claim_ids: dict[str, UUID] = Field(default_factory=dict)
    compiled_atoms: dict[str, PropositionAtom] = Field(default_factory=dict)
    events_emitted: list[KnowledgeEvent] = Field(default_factory=list)


class KanonCompiler:
    """
    Ingestion compiler compiling authored Kanon Markdown proposition blocks into
    deterministic PropositionAtoms, Claims, and append-only KnowledgeEvents on an EventStore.
    """

    def __init__(self, store: EventStore) -> None:
        self.store = store
        # Tracks declaration history per declaration_id: revision -> content_hash
        self._declaration_revisions: dict[str, dict[int, str]] = {}
        # Tracks active claim UUID per declaration_id
        self._declaration_active_claims: dict[str, UUID] = {}

    def compile_document(self, doc: ParsedMarkdownDocument) -> CompilationResult:
        result = CompilationResult()

        for prop in doc.propositions:
            content_hash = compute_declaration_content_hash(prop.raw_dict)
            dec_id = prop.declaration_id
            rev = prop.revision

            if dec_id not in self._declaration_revisions:
                self._declaration_revisions[dec_id] = {}

            rev_history = self._declaration_revisions[dec_id]

            # Integrity check: changed content reusing existing revision
            if rev in rev_history and rev_history[rev] != content_hash:
                raise CompilerIntegrityError(
                    f"Declaration '{dec_id}' revision {rev} reused with different content hash."
                )

            # Idempotency check: unchanged declaration (same rev, same hash)
            if rev in rev_history and rev_history[rev] == content_hash:
                # Existing compiled claim ID
                if dec_id in self._declaration_active_claims:
                    result.declaration_claim_ids[dec_id] = self._declaration_active_claims[dec_id]
                continue

            # Check revision monotonicity
            max_rev = max(rev_history.keys()) if rev_history else 0
            if rev <= max_rev:
                raise CompilerIntegrityError(
                    f"Declaration '{dec_id}' revision {rev} is not strictly greater than current max revision {max_rev}."
                )

            # Supersede prior claim if one exists
            if dec_id in self._declaration_active_claims:
                prior_claim_id = self._declaration_active_claims[dec_id]
                sup_event_id = compute_compiler_event_id(dec_id, rev, content_hash, "ClaimSuperseded")
                sup_event = KnowledgeEvent(
                    event_id=sup_event_id,
                    aggregate_id=str(prior_claim_id),
                    aggregate_version=3,  # Aggregate v1 Created, v2 Activated, v3 Superseded
                    event_type="ClaimSuperseded",
                    payload={"claim_id": str(prior_claim_id), "superseded_by_revision": rev},
                )
                self.store.append(sup_event)
                result.events_emitted.append(sup_event)

            # Build argument entity UUIDs
            arg_uuids: dict[str, UUID] = {}
            for role_name, raw_val in prop.arguments.items():
                arg_uuids[role_name] = compute_entity_id(role_name, str(raw_val))

            atom = PropositionAtom.create(prop.predicate, arg_uuids)
            self.store.register_atom(atom)
            result.compiled_atoms[dec_id] = atom

            # Deterministic Claim UUID
            claim_uuid = uuid.uuid5(
                NEPHON_COMPILER_NAMESPACE, f"claim|{dec_id}|rev{rev}|{content_hash}"
            )

            provenance = SourceLeaf(
                kind=SourceKind.DOCUMENT,
                ref_id=f"{Path(doc.file_path).name}#{dec_id}",
            )

            claim = Claim(
                id=claim_uuid,
                proposition_id=atom.id,
                polarity=Polarity.POSITIVE,
                context=Context.universal(),
                provenance=provenance,
                asserted_by="kanon_compiler",
                trust_level=TrustLevel.CONSTITUTIONAL,
                authority_level=AuthorityLevel(prop.authority_level),
                epistemic_mode=EpistemicMode(prop.epistemic_mode),
            )

            self.store.register_claim(claim)

            # Emit ClaimCreated and ClaimActivated events
            created_event_id = compute_compiler_event_id(dec_id, rev, content_hash, "ClaimCreated")
            created_event = KnowledgeEvent(
                event_id=created_event_id,
                aggregate_id=str(claim.id),
                aggregate_version=1,
                event_type="ClaimCreated",
                payload={
                    "claim_id": str(claim.id),
                    "declaration_id": dec_id,
                    "declaration_revision": rev,
                    "content_hash": content_hash,
                    "markdown_path": doc.file_path,
                },
            )
            self.store.append(created_event)
            result.events_emitted.append(created_event)

            activated_event_id = compute_compiler_event_id(dec_id, rev, content_hash, "ClaimActivated")
            activated_event = KnowledgeEvent(
                event_id=activated_event_id,
                aggregate_id=str(claim.id),
                aggregate_version=2,
                event_type="ClaimActivated",
                payload={"claim_id": str(claim.id)},
            )
            self.store.append(activated_event)
            result.events_emitted.append(activated_event)

            # Update compiler state
            self._declaration_revisions[dec_id][rev] = content_hash
            self._declaration_active_claims[dec_id] = claim.id
            result.declaration_claim_ids[dec_id] = claim.id

        return result

    def compile_directory(self, dir_path: str | Path) -> CompilationResult:
        combined = CompilationResult()
        path = Path(dir_path)

        for file_path in sorted(path.glob("*.md")):
            doc = MarkdownLoader.parse_file(file_path)
            res = self.compile_document(doc)
            combined.declaration_claim_ids.update(res.declaration_claim_ids)
            combined.compiled_atoms.update(res.compiled_atoms)
            combined.events_emitted.extend(res.events_emitted)

        return combined
