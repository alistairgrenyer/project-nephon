from __future__ import annotations

import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from nephon_contracts.canonical_json import compute_nephon_canonical_json_v1
from nephon_contracts.dto import ExecutionAuthorizationPayload, SignedExecutionToken


class GatewaySigner:
    """
    Ed25519 Cryptographic Gateway Signer.
    Holds private key and signs ExecutionAuthorizationPayload instances.
    Broker holds ONLY the public key and cannot mint authorization tokens.
    """

    def __init__(self, private_key: ed25519.Ed25519PrivateKey | None = None, key_id: str = "gateway-ed25519-v1") -> None:
        self.private_key = private_key or ed25519.Ed25519PrivateKey.generate()
        self.key_id = key_id

    @classmethod
    def generate(cls, key_id: str = "gateway-ed25519-v1") -> GatewaySigner:
        return cls(private_key=ed25519.Ed25519PrivateKey.generate(), key_id=key_id)

    def get_public_key_bytes(self) -> bytes:
        return self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def get_public_key_hex(self) -> str:
        return self.get_public_key_bytes().hex()

    def get_public_key(self) -> ed25519.Ed25519PublicKey:
        return self.private_key.public_key()

    def sign_payload(self, payload: ExecutionAuthorizationPayload) -> SignedExecutionToken:
        """
        Computes NEPHON_CANONICAL_JSON_V1 over payload dict and signs UTF-8 bytes using Ed25519.
        """
        payload_dict = payload.model_dump(mode="json")
        canonical_str = compute_nephon_canonical_json_v1(payload_dict)
        signature = self.private_key.sign(canonical_str.encode("utf-8"))
        signature_hex = signature.hex()
        return SignedExecutionToken(payload=payload, signature_bytes=signature_hex)
