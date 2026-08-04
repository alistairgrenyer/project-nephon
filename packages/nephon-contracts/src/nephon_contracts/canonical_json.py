from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from typing import Any


def _assert_no_invalid_floats_or_bytes(obj: Any) -> None:
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        raise ValueError("NEPHON_CANONICAL_JSON_V1 rejects NaN and Infinity values.")
    if isinstance(obj, bytes):
        raise TypeError("NEPHON_CANONICAL_JSON_V1 rejects raw bytes. Use hex or base64url encoding.")
    if isinstance(obj, dict):
        for k, v in obj.items():
            if not isinstance(k, str):
                raise TypeError("NEPHON_CANONICAL_JSON_V1 requires string keys in dictionaries.")
            _assert_no_invalid_floats_or_bytes(v)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            _assert_no_invalid_floats_or_bytes(item)


def compute_nephon_canonical_json_v1(data: Any) -> str:
    """
    NEPHON_CANONICAL_JSON_V1:
    1. UTF-8 string encoding.
    2. Dict keys sorted alphabetically (sort_keys=True).
    3. Compact separators (",", ":") without whitespace.
    4. Key types must be strings exclusively.
    5. Rejects NaN, Infinity, non-string dict keys, and binary byte objects.
    6. Datetime objects converted to UTC ISO 8601 string representation.
    """
    _assert_no_invalid_floats_or_bytes(data)

    def _default(obj: Any) -> Any:
        if isinstance(obj, datetime):
            if obj.tzinfo is None:
                obj = obj.replace(tzinfo=timezone.utc)
            return obj.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    normalized = json.dumps(
        data,
        default=_default,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return normalized


def compute_request_hash(
    capability_id: str,
    capability_version: str,
    target: str,
    parameters: dict[str, Any],
) -> str:
    """
    Computes a deterministic SHA-256 hash of a capability request using NEPHON_CANONICAL_JSON_V1.
    Target and parameter string values preserve exact case sensitivity.
    """
    canonical_dict = {
        "capability_id": capability_id,
        "capability_version": capability_version,
        "target": target,  # Case PRESERVED (file paths, container IDs, env keys)
        "parameters": parameters,
    }
    canonical_str = compute_nephon_canonical_json_v1(canonical_dict)
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
