# Nephon Reusable Constitutional Control Plane — Living Implementation Context

## 1. Architectural Overview & Boundaries

`project-nephon` is the **reusable constitutional control plane**. It provides core graph structures, event sourcing, belief evaluation, governance policy, Ed25519 signing gateway, execution broker runtime, and client SDKs.

Governed projects (such as `homelab`) integrate through stable library packages (`nephon-contracts`, `nephon-sdk`) and implement project-specific **Capability Adapters** deployed inside project-local broker images.

```text
                               ┌───────────────────────────────────────────────┐
                               │           NEPHON CONTROL PLANE                │
                               │             (project-nephon)                  │
                               │                                               │
                               │  • nephon-contracts (Public DTOs, Context)    │
                               │  • nephon-core      (Graph, Belief, Governance)│
                               │  • nephon-gateway   (Ed25519 PDP Service)     │
                               │  • nephon-sdk       (Client Library)          │
                               │  • nephon-broker-runtime (PEP Broker Runtime) │
                               └───────────────────────┬───────────────────────┘
                                                       │
                                 ┌─────────────────────┴─────────────────────┐
                                 │                                           │
                                 ▼                                           ▼
                 ┌───────────────────────────────┐           ┌───────────────────────────────┐
                 │        HOMELAB PROJECT        │           │        FUTURE PROJECT         │
                 │      (homelab repo)           │           │     (website/finance repo)    │
                 │                               │           │                               │
                 │  • homelab-broker (Image)     │           │  • project-broker (Image)     │
                 │  • Homelab Credentials        │           │  • Project Credentials        │
                 │  • Homelab Adapters:          │           │  • Project Adapters:          │
                 │    - inspect_service          │           │    - publish_article         │
                 │    - restart_container        │           │    - update_dns_record       │
                 └───────────────────────────────┘           └───────────────────────────────┘
```

---

## 2. Monorepo Package Structure

```text
project-nephon/
├── packages/
│   ├── nephon-contracts/       # Public DTOs, Context, Enums, NEPHON_CANONICAL_JSON_V1
│   ├── nephon-core/            # Graph, event store, context algebra, provenance, belief, governance
│   ├── nephon-sdk/             # Client used by governed projects (NephonClient)
│   └── nephon-runtime-oi/      # Sandboxed Open Interpreter AgentRuntime adapter
│
├── services/
│   ├── nephon-gateway/         # Policy Decision Point (PDP) & Ed25519 signing service
│   ├── nephon-broker-runtime/  # Reusable Execution Broker Runtime
│   └── nephon-evidence/        # Read-only evidence collection service
│
├── data/00-kanon/              # 15 Authored constitutional declarations
├── pyproject.toml              # Workspace / monorepo configuration
└── tests/
```

### Strict Directional Package Dependencies

```text
nephon-contracts (Public DTOs, Context, Enums — NO imports from nephon-core)
       │
       ├──► nephon-core (Graph, EventStore, Provenance, Belief, Governance, Inference)
       │       │
       │       └──► nephon-gateway (Ed25519 PDP Service)
       │
       ├──► nephon-sdk (Client Library)
       │
       └──► nephon-broker-runtime (PEP Engine)

nephon-contracts + nephon-sdk
       │
       └──► homelab (Governed project — NEVER imports nephon-core)
```

---

## 3. Core Technical Invariants & Security Contracts

1. **Credential Isolation**: Mutation credentials (Docker socket, SSH keys, Coolify API tokens) exist ONLY inside project-local Execution Brokers (`homelab-broker`). Sandboxed reasoning workers (`OpenInterpreterRuntime`) have zero mutation credentials.
2. **Ed25519 Asymmetric Signing**: Gateway holds `Ed25519PrivateKey`. Broker holds `Ed25519PublicKey`. Broker cannot mint tokens.
3. **`NEPHON_CANONICAL_JSON_V1` Hashing**: UTF-8 encoding, sorted keys, compact separators, string-only dict keys, UTC ISO 8601 timestamps. Target strings preserve case.
4. **Schema Hash Binding**: `ExecutionAuthorizationPayload` binds `capability_schema_hash`, `request_hash`, `project_id`, `environment_id`, and `broker_id`.
5. **Durable Atomic Nonce Redemption**: Nonce redemption (`AUTHORIZED` -> `CLAIMED`) is an atomic compare-and-swap on durable storage.
6. **Zero Handle Exposure**: Reasoning worker receives decision rationale and `ExecutionReceipt`, but NEVER signed tokens, handles, or nonces.
7. **Read-Only Evidence Service**: `nephon-evidence` runs read-only observation adapters (`inspect_service`) separately from privileged mutation brokers.
