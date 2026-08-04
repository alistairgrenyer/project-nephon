# Nephon: Reusable Constitutional Control Plane for Autonomous Agents

[![Build Status](https://img.shields.io/badge/tests-39%20passed-success)](https://github.com/alistairgrenyer/project-nephon)
[![Architecture](https://img.shields.io/badge/architecture-Enforced%20Gateway%20%2B%20Broker-blue)](file:///c:/Users/Alist/Documents/pi-agent/project-nephon/.agents/living-context/project-nephon-impl.md)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)

**Nephon** is a **Sovereign Constitutional Control Plane** for autonomous AI agents. It shifts the AI safety paradigm from advisory prompting to **non-bypassable structural enforcement**.

In a Nephon-governed system, the LLM or reasoning worker (e.g., Open Interpreter, Claude Code, custom agent loop) **is removed from the security trust boundary**. The reasoning worker proposes actions and gathers telemetry, but possesses **zero host mutation credentials** (no `sudo`, no Docker socket, no SSH keys). 

State-changing operations occur **only** through an **Ed25519 Cryptographically Signed Execution Token** issued by the **Constitutional Gateway** and enforced by a credential-holding **Execution Broker**.

---

## Architecture & System Invariant

```text
                               ┌───────────────────────────────────────────────────────────┐
                               │                      USER REQUEST                         │
                               └─────────────────────────────┬─────────────────────────────┘
                                                             │
                                                             ▼
                               ┌───────────────────────────────────────────────────────────┐
                               │                    REASONING WORKER                       │
                               │        (Open Interpreter / Claude Code / Custom LLM)      │
                               │                                                           │
                               │  SANDBOXED: Zero sudo, zero Docker socket, zero SSH keys. │
                               │  Proposes action + gathers evidence.                      │
                               └─────────────────────────────┬─────────────────────────────┘
                                                             │
                                                             ▼ (ActionRequest)
                               ┌───────────────────────────────────────────────────────────┐
                               │                CONSTITUTIONAL GATEWAY (PDP)               │
                               │                 services/nephon-gateway/                  │
                               │                                                           │
                               │  Evaluates Epistemic Belief & Governance Policy           │
                               │  Signs Ed25519 ExecutionAuthorizationPayload on PERMIT.   │
                               └─────────────────────────────┬─────────────────────────────┘
                                                             │
                                                             ▼ (SignedExecutionToken)
                               ┌───────────────────────────────────────────────────────────┐
                               │                 EXECUTION BROKER (PEP)                    │
                               │             services/nephon-broker-runtime/               │
                               │                                                           │
                               │  SOLE CREDENTIAL HOLDER: Owns Docker, SSH, host API creds.│
                               │  Validates Ed25519 Public Key, Request Hash & Nonce.      │
                               └─────────────────────────────┬─────────────────────────────┘
                                                             │
                                                             ▼
                               ┌───────────────────────────────────────────────────────────┐
                               │                 HOST SYSTEM STATE MUTATION                │
                               └───────────────────────────────────────────────────────────┘
```

### Governing System Invariants
1. **Credential Isolation**: No agent-accessible process possesses credentials capable of performing state-changing operations except through the Execution Broker.
2. **Mandatory Execution Authorization**: No state-changing action occurs unless the constitutional kernel has produced an active, context-matching `PERMIT` decision with a valid, single-use `ExecutionAuthorizationPayload`.
3. **Cryptographic Asymmetric Authority**: The Gateway holds the Ed25519 private key (`Ed25519PrivateKey`). The Broker holds ONLY the public verification key (`Ed25519PublicKey`). The Broker cannot authorize actions itself.
4. **Zero Token Handle Exposure**: The reasoning worker receives decision rationale and `ExecutionReceipt`, but **never** signed tokens, internal handles, or nonces.

---

## Repository & Package Architecture

`project-nephon` is structured as a clean monorepo containing reusable libraries, services, and constitutional data:

```text
project-nephon/
├── packages/
│   ├── nephon-contracts/       # Public DTOs, Contexts, Enums, NEPHON_CANONICAL_JSON_V1
│   ├── nephon-core/            # Graph kernel, event store, belief evaluator, governance
│   └── nephon-sdk/             # Client library for governed applications (NephonClient)
│
├── services/
│   ├── nephon-gateway/         # Policy Decision Point (PDP) & Ed25519 signing service
│   └── nephon-broker-runtime/  # Reusable Execution Broker Engine (PEP)
│
├── data/00-kanon/              # Authored Kanon constitutional declarations (15 propositions)
├── tests/                      # Unit, scenario, canonical serialization & security test suite
└── pyproject.toml              # Workspace build configuration
```

### Package Dependency Rules
- **`nephon-contracts`**: Public contract layer. **Zero dependencies on core logic.**
- **`nephon-core`**: Private kernel implementation (Graph, Belief, Inference, EventStore). Governed applications **must never import `nephon-core`**.
- **`nephon-sdk`**: Client library imported by governed projects (e.g. `homelab`).
- Enforced by automated boundary test: [`tests/test_package_boundaries.py`](file:///c:/Users/Alist/Documents/pi-agent/project-nephon/tests/test_package_boundaries.py).

---

## How to Use Nephon in Any Project (AI & Developer Guide)

This guide explains how to integrate Nephon into any project (such as `homelab`, a cloud automation service, or an autonomous DevOps agent).

### Step 1: Install Nephon Packages
Governed projects install `nephon-contracts` and `nephon-sdk`:

```bash
pip install -e packages/nephon-contracts
pip install -e packages/nephon-sdk
```

### Step 2: Define a Project-Specific Capability Adapter
Capabilities describe the exact state-changing operations your system supports. Implement the `CapabilityAdapter` protocol:

```python
from typing import Any
from uuid import UUID
from pydantic import BaseModel
from nephon_contracts.enums import RiskClass
from nephon_contracts.dto import ObservationClaim

class RestartContainerRequest(BaseModel):
    target: str
    timeout_seconds: int = 30

class HomelabRestartContainerAdapter:
    capability_id = "restart_container"
    capability_version = "1.0.0"
    risk_class = RiskClass.REVERSIBLE_MUTATION
    request_model = RestartContainerRequest

    async def inspect_preconditions(self, request: RestartContainerRequest) -> tuple[ObservationClaim, ...]:
        # Read-only status check using read-only evidence credentials
        return ()

    async def execute(self, request: RestartContainerRequest, execution_id: UUID) -> dict[str, Any]:
        # Privileged mutation code running inside the Broker (Docker socket / Coolify API)
        print(f"Executing restart for container: {request.target}")
        return {"status": "restarted", "target": request.target}

    async def reconcile(self, execution_id: UUID, request: RestartContainerRequest) -> dict[str, Any]:
        # Post-crash reconciliation verifying if the container is now running
        return {"status": "reconciled", "target": request.target}
```

### Step 3: Initialize the Constitutional Gateway (PDP)
The Gateway evaluates action requests against constitutional logic and signs authorization tokens:

```python
from nephon_contracts.contexts import Context
from nephon_contracts.dto import ActionRequest
from nephon_contracts.enums import GovernanceDisposition
from nephon_graph.storage.event_store import InMemoryEventStore
from nephon_gateway import GatewaySigner, ConstitutionalGatewayService

# Initialize EventStore and Gateway Signer
store = InMemoryEventStore()
signer = GatewaySigner.generate(key_id="homelab-gateway-v1")
gateway = ConstitutionalGatewayService(store=store, signer=signer)

# Evaluate an action proposed by the reasoning worker
request = ActionRequest(
    project_id="homelab",
    environment_id="development",
    capability_id="restart_container",
    capability_version="1.0.0",
    target="container_x",
    parameters={"timeout_seconds": 30},
    context=Context.universal(),
)

# Compute capability schema hash from the adapter model
from nephon_broker_runtime import compute_schema_hash
schema_hash = compute_schema_hash(RestartContainerRequest)

decision, signed_token = gateway.evaluate_action(
    request=request,
    broker_id="homelab-broker-1",
    capability_schema_hash=schema_hash,
)

print("Governance Disposition:", decision.disposition)  # e.g., GovernanceDisposition.PERMIT
```

### Step 4: Execute through the Execution Broker (PEP)
The Broker holds the Gateway's public verification key and executes authorized actions:

```python
import asyncio
from nephon_broker_runtime import BrokerTokenVerifier, ExecutionBrokerEngine

# Initialize Broker holding ONLY the public verification key
verifier = BrokerTokenVerifier(public_key=signer.get_public_key())
broker = ExecutionBrokerEngine(
    verifier=verifier,
    project_id="homelab",
    environment_id="development",
    broker_id="homelab-broker-1",
    allowlisted_capability_ids={"restart_container"},
)

# Register project capability adapter
broker.register_adapter(HomelabRestartContainerAdapter())

# Execute authorized action with signed token
async def run_execution():
    if decision.disposition == GovernanceDisposition.PERMIT and signed_token:
        receipt = await broker.execute_authorized_action(
            signed_token=signed_token,
            target="container_x",
            parameters={"timeout_seconds": 30},
        )
        print("Execution Result:", receipt.state)  # ExecutionState.SUCCEEDED

asyncio.run(run_execution())
```

---

## Cryptographic Security & Tamper Protection

Every `SignedExecutionToken` carries an Ed25519 signature over a `NEPHON_CANONICAL_JSON_V1` hash of `ExecutionAuthorizationPayload`.

The `ExecutionBrokerEngine` strictly rejects execution if:
- **Signature Mismatch**: Token was signed by an unauthorized key (`KeyForgeryAttack`).
- **Target Swapping**: Target string was changed after token issuance (`TargetSwappingAttack`).
- **Parameter Tampering**: Parameter dictionary was modified (`ParameterTamperingAttack`).
- **Schema Hash Mismatch**: Capability request model schema changed (`SchemaHashMismatch`).
- **Token Replay**: Token nonce was previously redeemed (`TokenReplayError`).
- **Expiration**: Current time exceeds `valid_until`.

---

## Development & Testing

Run the complete test suite (unit, scenario, serialization, package boundary, and security boundary tests):

```bash
python -m pytest --tb=short
```

All **39 pytest tests** run in under 0.25 seconds.