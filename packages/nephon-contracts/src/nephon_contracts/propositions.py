from __future__ import annotations

import unicodedata
import uuid
from uuid import UUID
from pydantic import BaseModel

# PERMANENT — Nephon project-specific atom namespace UUIDv4
NEPHON_ATOM_NAMESPACE: UUID = UUID("c5f8b9e2-412d-4b8a-93e1-7890a2b3c4d5")


def compute_atom_id(predicate: str, arguments: dict[str, UUID]) -> UUID:
    """
    Computes a deterministic UUIDv5 for an unsigned proposition atom.
    Both predicate and argument role names undergo NFC Unicode normalization, trimming, and lowercasing.
    Arguments are sorted alphabetically by role name.
    """
    norm_pred = unicodedata.normalize("NFC", predicate.strip().lower())
    norm_args = {
        unicodedata.normalize("NFC", r.strip().lower()): v
        for r, v in arguments.items()
    }
    sorted_roles = sorted(norm_args.keys())
    formatted = "|".join(f"{r}:{str(norm_args[r]).lower()}" for r in sorted_roles)
    canonical_str = f"{norm_pred}|{formatted}"
    return uuid.uuid5(NEPHON_ATOM_NAMESPACE, canonical_str)


class PropositionAtom(BaseModel):
    """
    Unsigned canonical proposition atom.
    Contains no polarity. Positive and negative assertions share the exact same PropositionAtom.
    """
    id: UUID
    predicate: str
    arguments: dict[str, UUID]

    @classmethod
    def create(cls, predicate: str, arguments: dict[str, UUID]) -> PropositionAtom:
        atom_id = compute_atom_id(predicate, arguments)
        norm_pred = unicodedata.normalize("NFC", predicate.strip().lower())
        norm_args = {
            unicodedata.normalize("NFC", r.strip().lower()): v
            for r, v in arguments.items()
        }
        return cls(id=atom_id, predicate=norm_pred, arguments=norm_args)
