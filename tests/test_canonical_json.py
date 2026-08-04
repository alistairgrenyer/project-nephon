from __future__ import annotations

from datetime import datetime, timezone
import pytest
from nephon_contracts.canonical_json import compute_nephon_canonical_json_v1, compute_request_hash


def test_canonical_json_basic_normalization():
    data = {
        "z_param": 123,
        "a_param": "hello",
        "nested": {"b": 2, "a": 1},
    }
    canonical = compute_nephon_canonical_json_v1(data)
    assert canonical == '{"a_param":"hello","nested":{"a":1,"b":2},"z_param":123}'


def test_canonical_json_datetime_utc_serialization():
    dt = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)
    data = {"timestamp": dt}
    canonical = compute_nephon_canonical_json_v1(data)
    assert canonical == '{"timestamp":"2026-08-05T12:00:00Z"}'


def test_canonical_json_rejects_nan_and_infinity():
    with pytest.raises(ValueError, match="rejects NaN and Infinity"):
        compute_nephon_canonical_json_v1({"val": float("nan")})

    with pytest.raises(ValueError, match="rejects NaN and Infinity"):
        compute_nephon_canonical_json_v1({"val": float("inf")})


def test_canonical_json_rejects_raw_bytes():
    with pytest.raises(TypeError, match="rejects raw bytes"):
        compute_nephon_canonical_json_v1({"val": b"raw_binary_bytes"})


def test_request_hash_preserves_target_case():
    hash1 = compute_request_hash("restart_container", "1.0", "Container_X", {"timeout": 30})
    hash2 = compute_request_hash("restart_container", "1.0", "container_x", {"timeout": 30})
    assert hash1 != hash2, "Target string must be case preserved (file paths, container IDs, env keys)"
