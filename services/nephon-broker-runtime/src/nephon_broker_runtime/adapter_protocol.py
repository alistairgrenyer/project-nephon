from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID
from pydantic import BaseModel

from nephon_contracts.dto import ObservationClaim
from nephon_contracts.enums import RiskClass


class CapabilityAdapter(Protocol):
    """
    Project-Specific Capability Adapter Protocol.
    Implemented by governed projects (e.g. homelab) and loaded into project-local Execution Broker.
    """

    capability_id: str
    capability_version: str
    risk_class: RiskClass
    request_model: type[BaseModel]

    async def inspect_preconditions(
        self,
        request: BaseModel,
    ) -> tuple[ObservationClaim, ...]:
        """Inspects read-only preconditions before action execution."""
        ...

    async def execute(
        self,
        request: BaseModel,
        execution_id: UUID,
    ) -> dict[str, Any]:
        """Performs authorized state-changing mutation using broker credentials."""
        ...

    async def reconcile(
        self,
        execution_id: UUID,
        request: BaseModel,
    ) -> dict[str, Any]:
        """Post-crash reconciliation handler verifying postconditions."""
        ...
