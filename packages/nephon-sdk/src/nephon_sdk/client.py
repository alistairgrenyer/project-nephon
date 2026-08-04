from __future__ import annotations

from typing import Any
from uuid import UUID
from pydantic import BaseModel

from nephon_contracts.dto import (
    ActionRequest,
    ConstitutionalDecision,
    ExecutionReceipt,
    ObservationClaim,
)


class NephonClient:
    """
    Client library used by governed applications (e.g. homelab) to evaluate actions,
    collect evidence, and request execution through Nephon Constitutional Gateway & Broker services.
    """

    def __init__(self, gateway_url: str = "http://localhost:8000", broker_url: str = "http://localhost:8001") -> None:
        self.gateway_url = gateway_url
        self.broker_url = broker_url

    async def evaluate(self, request: ActionRequest) -> ConstitutionalDecision:
        """
        Submits an action evaluation request to Nephon Constitutional Gateway.
        Returns a ConstitutionalDecision.
        """
        # In local/embedded client mode or HTTP client mode
        raise NotImplementedError("HTTP gateway client evaluation transport is wired in service stage.")

    async def execute(self, authorization_handle: str) -> ExecutionReceipt:
        """
        Submits an opaque authorization handle to project-local Execution Broker.
        The reasoning worker never sees signed Ed25519 tokens.
        """
        raise NotImplementedError("HTTP broker execution transport is wired in service stage.")
