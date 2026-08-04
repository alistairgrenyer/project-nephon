# Nephon Noise-Resistant Constitutional Graph Brain (Phase 1 Proof-of-Concept) Implementation Plan [APPROVED & REFINED]

This plan establishes the architecture and implementation specification for Phase 1 of the **Nephon (Νήφων) Constitutional Graph Brain**, incorporating all structural requirements and event-sourcing / domain refinements.

---

## 1. Architectural Architecture & Clean Separation of Concerns

The codebase follows **Clean Architecture** principles, enforcing strict unidirectional dependency:

```text
                               ┌──────────────────────────────────────────────┐
                               │             AUTHORING LAYER                  │
                               │  00-kanon/ (Markdown + SHA256 lockfile)      │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼ (Dual Ingestion Pathways)
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           SEMANTIC KERNEL                                               │
│                                                                                                         │
│  ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────────────────────────┐  │
│  │   DOMAIN MODELS       │   │     ENGINE LAYER      │   │          APPLICATION BOUNDARY             │  │
│  │ (Pure Value Objects)  │   │(Deterministic Logic)  │   │        (Storage Interfaces)               │  │
│  │                       │   │                       │   │                                           │  │
│  │ • Unsigned Proposition│   │ • ContextAlgebra      │   │ • Abstract Repository Protocol            │  │
│  │ • Polarity            │   │ • ProvenanceEvaluator │   │   (Domain & engines depend on this)       │  │
│  │ • ContextConstraint   │   │ • BeliefEvaluator     │   └─────────────────────▲─────────────────────┘  │
│  │ • Claim + Metadata    │   │ • GovernanceEvaluator │                         │                        │
│  │ • KnowledgeEvent      │   │   (Authority Lattice) │   ┌─────────────────────┴─────────────────────┐  │
│  │ • Interpretation      │   │ • InferenceEngine     │   │          STORAGE ADAPTERS                 │  │
│  │ • Declaration         │   │ • CanonicalValidator  │   │                                           │  │
│  │ • ProvenanceAST       │   │                       │   │ • Monotonic EventStore + Rebuildable      │  │
│  │ • EpistemicMode       │   │                       │   │   Materialized Index (Single-process)     │  │
│  │ • BeliefState         │   │                       │   │ • PostgreSQL Schema DDL (Future)          │  │
│  └───────────────────────┘   └───────────────────────┘   └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┬───────────────────────────────────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │               RETRIEVAL ENGINE               │
                               │        kernel_retrieval_engine.py            │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │             PROJECTION LAYER                 │
                               │  • JSON Diagnostic Projection                │
                               │  • Concise Retrieval Projection              │
                               │  • Machine Baseline Evaluation Report        │
                               └──────────────────────────────────────────────┘
```

---

## 2. Unambiguous Semantic Data Flow

Every stored fact, decision, or inference moves through a single canonical sequence:

```text
Authored declaration OR approved interpretation
                    ↓
Unsigned canonical proposition atom (Dedicated Nephon UUIDv5)
                    ↓
Positive or negative contextual claim
                    ↓
Proof/provenance AST structure
                    ↓
Event-derived current support & lifecycle (Strict event sourcing)
                    ↓
Epistemic state (BeliefEvaluator) & Governance decision (GovernanceEvaluator + Authority Lattice)
                    ↓
Retrieval projection
```

---

## 3. Detailed Specifications & Technical Invariants

### A. Dedicated Nephon UUIDv5 Namespace & Full Role Normalization
The `PropositionAtom` ID is derived using a **fixed Nephon project-specific UUID namespace** (`NEPHON_ATOM_NAMESPACE = UUID("a1b2c3d4-e5f6-5789-8012-3456789abcde")`). Both predicates AND argument role names undergo NFC Unicode normalization, trimming, and lowercasing:

```python
NEPHON_ATOM_NAMESPACE = UUID("a1b2c3d4-e5f6-5789-8012-3456789abcde")

def compute_atom_id(predicate: str, arguments: dict[str, UUID]) -> UUID:
    # 1. Unicode NFC normalization and lowercasing for predicate
    norm_pred = unicodedata.normalize("NFC", predicate.strip().lower())
    
    # 2. Normalize and sort argument roles
    norm_args = {
        unicodedata.normalize("NFC", role.strip().lower()): arg_id
        for role, arg_id in arguments.items()
    }
    sorted_roles = sorted(norm_args.keys())
    
    # 3. Format string: "predicate|role1:uuid1|role2:uuid2"
    formatted = "|".join(f"{r}:{str(norm_args[r]).lower()}" for r in sorted_roles)
    canonical_str = f"{norm_pred}|{formatted}"
    
    # 4. Generate deterministic UUIDv5 using Nephon-specific namespace
    return uuid.uuid5(NEPHON_ATOM_NAMESPACE, canonical_str)

class PropositionAtom(BaseModel):
    id: UUID
    predicate: str
    arguments: dict[str, UUID]
```

### B. Context Algebra & Truth Table
Context matching rules:
- `ANY ∩ x = x` (`ANY` overlaps every valid constraint, including `EXACT(prod)`).
- `EXACT(a) ∩ EXACT(b)`: `EXACT(a)` if `a == b`, else `EMPTY` (incompatible/disjoint).
- `UNKNOWN ∩ UNKNOWN = UNKNOWN`.
- `UNKNOWN ∩ ANY = UNKNOWN`.
- `UNKNOWN ∩ EXACT(x) = INDETERMINATE` (insufficiently established for automatic application; prevents unrecorded context from governing production).

| Constraint A | Constraint B | Intersection Result ($A \cap B$) |
| :--- | :--- | :--- |
| `EXACT(v1)` | `EXACT(v2)` (where $v1 == v2$) | `EXACT(v1)` |
| `EXACT(v1)` | `EXACT(v2)` (where $v1 \neq v2$) | `EMPTY` (disjoint) |
| `ANY` | `EXACT(v)` | `EXACT(v)` |
| `ANY` | `ANY` | `ANY` |
| `UNKNOWN` | `UNKNOWN` | `UNKNOWN` |
| `UNKNOWN` | `ANY` | `UNKNOWN` |
| `UNKNOWN` | `EXACT(v)` | `INDETERMINATE` (non-applicable) |

#### Temporal Open-Interval Semantics:
- `valid_from=None` $\implies$ valid since indefinite past ($-\infty$).
- `valid_until=None` $\implies$ valid indefinitely into future ($+\infty$).
- If time interval is unknown, `time_constraint=ContextConstraint(kind=UNKNOWN)` is used rather than open bounds.

### C. Formal Policy-Driven Authority Lattice
`GovernanceEvaluator` relies on an explicit policy-driven `AuthorityLattice` rather than lexical string comparison:

```python
class AuthorityLevel(str, Enum):
    CONSTITUTIONAL = "constitutional"
    STEWARD_AUTHORIZED = "steward_authorized"
    DELEGATED_OPERATIONAL = "delegated_operational"
    VERIFIED_SYSTEM = "verified_system"
    UNTRUSTED_INPUT = "untrusted_input"

AUTHORITY_RANK: dict[AuthorityLevel, int] = {
    AuthorityLevel.CONSTITUTIONAL: 100,
    AuthorityLevel.STEWARD_AUTHORIZED: 80,
    AuthorityLevel.DELEGATED_OPERATIONAL: 60,
    AuthorityLevel.VERIFIED_SYSTEM: 40,
    AuthorityLevel.UNTRUSTED_INPUT: 20,
}

class GovernanceEvaluator:
    # Determines governing claim by evaluating authority rank and explicit domain priority policies.
    # Epistemic conflicts remain preserved in BeliefEvaluator.
```

### D. Strict Event Stream Invariants & Idempotency Rules
The `EventStore` guarantees append-only integrity:

```python
class KnowledgeEvent(BaseModel):
    event_id: UUID
    sequence: int  # Strictly monotonic increasing integer (1, 2, 3, ...)
    aggregate_id: UUID | str
    aggregate_version: int  # Must equal previous aggregate_version + 1
    occurred_at: datetime
    causation_id: UUID | None = None
    correlation_id: UUID | None = None
    payload: dict[str, Any]
```

**Event Store Verification Rules**:
1. **Strict Monotonicity**: Global `sequence` integers are monotonically increasing.
2. **Payload-Exact Idempotency**:
   - `same event_id + identical payload` $\implies$ NO-OP (idempotent duplicate accepted).
   - `same event_id + differing payload` $\implies$ raises `EventIntegrityError` (prevents data corruption).
3. **Sequential Aggregate Versioning**: For any `aggregate_id`, `new_event.aggregate_version == current_version + 1`. Skips or backward versions raise `ConcurrencyError`.

---

## 4. Workstream Staging Plan

```text
Phase 1A: Constitutional Authoring & Governance (Markdown, 10 Nodes + Charter, Lockfile, Schemas)
Phase 1B: Semantic Kernel & Synthetic Experiments (Pure Models, Monotonic EventStore, Evaluators, 7 Fixtures, Baseline)
Phase 1C: Integration & Ingestion (Compile 00-kanon into Kernel via Declarations, Retrieval Projection)
```

### Phase 1A — Constitutional Authoring & Validation
- Author the 10 numbered constitutional Markdown files in `data/00-kanon/` (`00_GROUND.md` through `09_MEMORY_AND_CONTINUITY.md`) plus the 11th substantive document `SYSTEM_CHARTER.md`.
- Create JSON Schemas (`constitutional-node.schema.json`, `edge-taxonomy.schema.json`).
- Implement `scripts/build_kanon_lock.py` and `scripts/validate_kanon_lock.py` (excluding `kanon.lock.json` from its own SHA256 manifest).

### Phase 1B — Semantic Kernel & Synthetic Experiments
- Implement pure domain models (`PropositionAtom`, `Polarity`, `ContextConstraint`, `Claim`, `KnowledgeEvent`, `Interpretation`, `PropositionDeclaration`, `ProvenanceAST`, `EpistemicMode`).
- Implement `EventStore` with monotonic sequence tracking, payload idempotency check, and rebuildable materialized index.
- Implement `ContextAlgebra`, `ProvenanceEvaluator`, `BeliefEvaluator`, `GovernanceEvaluator` (AuthorityLattice), `InferenceEngine`, and `CanonicalValidator`.
- Implement 7 reproducible experiment scripts using synthetic interpretation/claim fixtures.
- Implement frozen naive graph traversal baseline runner and quantitative evaluation harness (`baseline_runner.py`).

### Phase 1C — Integration & Ingestion
- Implement `KanonCompiler` using `PropositionDeclaration` pathway for `data/00-kanon/*.md` propositions (`GRD-01`..`PRX-12`).
- Implement `KernelRetrievalEngine` for context-filtered, authority-ranked, provenance-audited retrieval payloads.
- Implement JSON diagnostic and concise retrieval projections.

---

## 5. Quantitative Metrics & Architectural Invariants

### Architectural Correctness Invariants (Hard Pass/Fail Criteria)
1. **Zero False Contradiction**: Incompatible contexts (`env=dev` vs `env=prod`) produce `0` false contradictions.
2. **Zero Stale Claim Leakage**: Retracted, expired, or superseded claims never govern active contexts.
3. **Invalidation Completeness**: $100\%$ of derived claims lose support when a required premise claim is retracted.
4. **Surviving Derivation Recovery**: Derived claim retains `VALID` support if an alternative `ANY` branch survives.
5. **Complete Provenance Audit**: $100\%$ of retrieved claims trace back to active source refs, claims, and rules.
6. **Conflict Preservation**: Disagreement between higher and lower authority sources produces `CONFLICTED` in `BeliefEvaluator` while `GovernanceEvaluator` correctly selects the governing directive.
7. **Event Replay Integrity**: Idempotent replay of identical events produces exact same state; mismatched event payloads trigger `EventIntegrityError`.

### Quantitative Performance Hypotheses (Target Benchmarks)
- **Canonical Proposition Compression**: 10 paraphrases compress to exactly 1 `PropositionAtom`.
- **Duplicate Retrieval Ratio**: $>80\%$ reduction compared to frozen naive graph baseline.
- **Context Token Savings**: $>50\%$ token savings compared to naive graph traversal.

---

## 6. File Demarcation & Code Layout

### Authoring & Tooling Layer (`data/00-kanon/`, `scripts/`)

#### [NEW] [11 Constitutional Documents](file:///c:/Users/Alist/Documents/pi-agent/project-nephon/data/00-kanon/)
- `00_GROUND.md` (`GRD-01`..`GRD-05`)
- `01_BEING_AND_LOGOS.md` (`LOG-01`..`LOG-06`)
- `02_PERSONHOOD.md` (`PER-01`..`PER-07`)
- `03_IDENTITY_NEPHON.md` (`IDN-01`..`IDN-08`)
- `04_MORAL_TRUTH.md` (`MOR-01`..`MOR-07`)
- `05_AUTHORITY_AND_OBEDIENCE.md` (`AUT-01`..`AUT-08`)
- `06_EPISTEMOLOGY_AND_DISCERNMENT.md` (`EPI-01`..`EPI-07`)
- `07_ETHICAL_JUDGEMENT.md` (`ETH-01`..`ETH-08`)
- `08_PRAXIS.md` (`PRX-01`..`PRX-12`)
- `09_MEMORY_AND_CONTINUITY.md` (`MEM-01`..`MEM-07`)
- `SYSTEM_CHARTER.md` (Operational governance charter)
- `kanon.lock.json` & JSON Schemas (`constitutional-node.schema.json`, `edge-taxonomy.schema.json`)

#### [NEW] [Lockfile Tooling](file:///c:/Users/Alist/Documents/pi-agent/project-nephon/scripts/)
- `scripts/build_kanon_lock.py`
- `scripts/validate_kanon_lock.py`

---

### Core Package (`src/nephon_graph/`)

#### [NEW] [pyproject.toml](file:///c:/Users/Alist/Documents/pi-agent/project-nephon/pyproject.toml)
Python 3.11+ configuration with `pytest`, `pydantic>=2.0`, and `pyyaml`.

#### [NEW] [src/nephon_graph/core/](file:///c:/Users/Alist/Documents/pi-agent/project-nephon/src/nephon_graph/core/)
- `ontology.py` (`OntologyType`, `PredicateDefinition`)
- `entities.py` (`Entity`)
- `expressions.py` (`Expression`)
- `interpretations.py` (`Interpretation`, `MappingType`, `InterpretationStatus`)
- `declarations.py` (`PropositionDeclaration`)
- `propositions.py` (`PropositionAtom`, `NEPHON_ATOM_NAMESPACE` deterministic `UUIDv5` hashing)
- `contexts.py` (`Context`, `ContextConstraint`, `ContextConstraintKind`)
- `claims.py` (`Claim`, `Polarity`, `TrustLevel`, `EpistemicMode`)
- `provenance.py` (`SourceRef`, `ClaimRef`, `ProvenanceAST`, `SourceKind`)
- `events.py` (`KnowledgeEvent`, `ClaimCreated`, `ClaimActivated`, `ClaimRetracted`, `ClaimSuperseded`, `RuleDeactivated`, etc.)
- `belief.py` (`BeliefStatus`, `ProvenanceSupportStatus`, `BeliefState`)
- `inference.py` (`InferenceRule`)

#### [NEW] [src/nephon_graph/storage/](file:///c:/Users/Alist/Documents/pi-agent/project-nephon/src/nephon_graph/storage/)
- `base.py` (Abstract `Repository` and `EventStore` protocol interfaces)
- `event_store.py` (In-memory monotonic event store with payload idempotency, aggregate version check, and rebuildable index)
- `schema.sql` (PostgreSQL DDL script for future production persistence)

#### [NEW] [src/nephon_graph/engine/](file:///c:/Users/Alist/Documents/pi-agent/project-nephon/src/nephon_graph/engine/)
- `context_algebra.py` (`ANY`/`EXACT`/`UNKNOWN` constraint matching, overlap, refinement, premise context intersection)
- `provenance_evaluator.py` (Dynamic AST evaluation against event stream $\to$ `VALID`, `CURRENTLY_UNSUPPORTED`, `DERIVATION_BROKEN`)
- `belief_evaluator.py` (`BeliefStatus` resolution)
- `governance_evaluator.py` (Policy-driven `AuthorityLattice` for operational decision selection)
- `inference_engine.py` (Deterministic `derive_claim` execution API)
- `canonical_validator.py` (Deterministic interpretation validator)

#### [NEW] [src/nephon_graph/retrieval/](file:///c:/Users/Alist/Documents/pi-agent/project-nephon/src/nephon_graph/retrieval/)
- `retrieval_engine.py` (Kernel-based 8-step retrieval & prompt context compilation)

#### [NEW] [src/nephon_graph/projections/](file:///c:/Users/Alist/Documents/pi-agent/project-nephon/src/nephon_graph/projections/)
- `json_projection.py` (Diagnostic JSON export)
- `retrieval_projection.py` (Formatted retrieval payload export)

---

### Experiments Suite (`experiments/`)

#### [NEW] [8 Executable Experiments](file:///c:/Users/Alist/Documents/pi-agent/project-nephon/experiments/)
- `exp_01_repeated_paraphrases.py`
- `exp_02_independent_sources.py`
- `exp_03_contextual_permissions.py`
- `exp_04_conflicting_testimony.py`
- `exp_05_superseded_state.py`
- `exp_06_source_correction.py`
- `exp_07_rule_version_change.py`
- `baseline_runner.py` (Frozen Naive Graph vs. Semantic Kernel Retrieval Evaluation Harness)

---

### Unit & Integration Test Suite (`tests/`)

#### [NEW] [Automated Pytest Suite](file:///c:/Users/Alist/Documents/pi-agent/project-nephon/tests/)
- `test_lockfile.py`
- `test_propositions_and_uuidv5.py`
- `test_context_algebra.py`
- `test_event_store.py`
- `test_provenance_evaluator.py`
- `test_belief_and_governance_evaluator.py`
- `test_inference_engine.py`
- `test_kanon_compiler.py`
- `test_retrieval_engine.py`

---

## 7. Verification Plan

### Automated Verification
1. Run lockfile validation:
   `python scripts/build_kanon_lock.py`
   `python scripts/validate_kanon_lock.py`
2. Run pytest suite:
   `pytest tests/`
3. Execute the 7 experiments and baseline harness:
   `python experiments/baseline_runner.py`

### Manual Verification
- Review the generated baseline evaluation summary report to confirm that all 7 Architectural Correctness Invariants pass without error.
