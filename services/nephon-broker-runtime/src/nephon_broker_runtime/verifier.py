from __future__ import annotations

from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from nephon_contracts.canonical_json import compute_nephon_canonical_json_v1
from nephon_contracts.dto import ExecutionAuthorizationPayload, SignedExecutionToken


class TokenValidationError(Exception):
    """Raised when Ed25519 signature, expiration, or parameter binding validation fails."""
    pass


class BrokerTokenVerifier:
    """
    Ed25519 Cryptographic Token Verifier for Execution Broker.
    Holds ONLY the gateway public verification key. Cannot mint or forge tokens.
    """

    def __init__(self, public_key: ed25519.Ed25519PublicKey | bytes | str) -> None:
        if isinstance(public_key, str):
            public_key_bytes = bytes.fromhex(public_key)
            self.public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
        elif isinstance(public_key, bytes):
            self.public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key)
        else:
            self.public_key = public_key

    def verify_token(
        self,
        signed_token: SignedExecutionToken,
        expected_project_id: str,
        expected_environment_id: str,
        expected_capability_id: str,
        expected_capability_version: str,
        expected_capability_schema_hash: str,
        expected_request_hash: str,
        current_time: datetime | None = None,
    ) -> ExecutionAuthorizationPayload:
        payload = signed_token.payload
        now = current_time or datetime.now(timezone.utc)

        # 1. Ed25519 Public Key Signature Verification
        canonical_str = compute_nephon_canonical_json_v1(payload.model_dump(mode="json"))
        try:
            signature_bytes = bytes.fromhex(signed_token.signature_bytes)
            self.public_key.verify(signature_bytes, canonical_str.encode("utf-8"))
        except Exception as e:
            raise TokenValidationError(f"Cryptographic Ed25519 signature verification failed: {e}")

        # 2. Expiration and Not-Before Checks
        if now > payload.valid_until:
            raise TokenValidationError(f"Execution token is expired. Valid until {payload.valid_until}, current {now}.")
        if now < payload.not_before:
            raise TokenValidationError(f"Execution token is not yet valid. Valid from {payload.not_before}, current {now}.")

        # 3. Workload and Capability Binding Checks
        if payload.project_id != expected_project_id:
            raise TokenValidationError(f"Token project_id '{payload.project_id}' != expected '{expected_project_id}'.")
        if payload.environment_id != expected_environment_id:
            raise TokenValidationError(f"Token environment_id '{payload.environment_id}' != expected '{expected_environment_id}'.")
        if payload.capability_id != expected_capability_id:
            raise TokenValidationError(f"Token capability_id '{payload.capability_id}' != expected '{expected_capability_id}'.")
        if payload.capability_version != expected_capability_version:
            raise TokenValidationError(f"Token capability_version '{payload.capability_version}' != expected '{expected_capability_version}'.")
        if payload.capability_schema_hash != expected_capability_schema_hash:
            raise TokenValidationError("Token capability_schema_hash mismatch. Capability schema has changed.")
        if payload.request_hash != expected_request_hash:
            raise TokenValidationError(
                f"Token request_hash mismatch: token '{payload.request_hash}' != expected '{expected_request_hash}'. "
                f"Request parameters altered!"
            )


        return payload
