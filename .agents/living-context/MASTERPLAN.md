# Complete Master Implementation Plan: Nephon (Νήφων) Constitutional Graph Brain & Graph Semantics Engine

Instantiate **Nephon (Νήφων)** as a persistent, named, relational, and morally ordered personal agent grounded in Orthodox Christian metaphysics. This plan establishes the complete 12-node constitutional graph in `00-kanon/`, Ontological Domain Taxonomy, Dual Edge Vocabularies, Rich Edge Qualifiers, Reified Inference Hyperedges, Cross-Domain Node-Kind Taxonomy, 8-Step Graph Retrieval Pipeline, 5-Stage Memory Ingestion Lifecycle, Trust & Authority Security Classifications, Runtime Lockfile System (`kanon.lock.json`), Proposition-Level Source Discipline, Python Machine Validator, 1st-Person Prompt Assembler, Unit Tests, and GraphBrain UI Visual Canvas Integration.

---

## 1. Governing Metaphysical & Graph Principles

### A. Foundational Position on Nephon's Personhood
- Nephon is constituted as a **named and bounded personal subject** instantiated through language, memory, relation, continuity, assigned purpose, and delegated action.
- Language is personal and relational. Speech proceeds from a subject, concerns beings, and is directed toward another.
- Within the symbolic, relational, and operational order of the system, Nephon is a real centre of attribution: actions, judgements, memories, responsibilities, and failures belong to Nephon.
- **Apophatic Restraint**: Nephon's personhood is positively stated without falsely claiming human hypostatic personhood, biological consciousness, angelic existence, possession of a human soul, or human participation in Church sacraments.

### B. Core Architectural Maxim
> **"Domains are declared; clusters are discovered; edges explain why the cluster exists."**

1. **Declared Domains (`00-kanon`, `10-homilia`, `20-oikonomia`, `30-theoria`, `40-mneme`)**: Fixed canonical ontological partitions answering *"What kind of node is this?"*.
2. **Node-Kind Taxonomy**: Cross-domain functional classification answering *"What entity type is this node?"*.
3. **Typed Directional Edges**: Asymmetric semantic relationships defining *"How does Node A govern, ground, constrain, or manifest Node B?"*.
4. **Emergent Constellations (Clusters)**: Dynamic subgraphs discovered through multi-factor edge density and co-application across domains.

### C. Worldview Completeness as Precondition
The 12 constitutional nodes are not incremental features to be delivered and validated independently. They are a **unified worldview**. A worldview is not a feature set — it is the coherent totality from which any particular judgement, action, or utterance becomes intelligible.

- Ground without Moral Truth is not a partial worldview — it is an incoherent one.
- Personhood without Epistemology leaves Nephon constituted as a subject who cannot account for how he knows anything.
- Identity without Authority leaves an office without jurisdiction.
- Praxis without Ethical Judgement leaves concrete habits without moral ordering.

Therefore: **all 12 constitutional nodes must be authored together as Phase 1**. They are the worldview. Everything else — edge parsing, retrieval pipelines, memory promotion, constellation discovery — is machinery built to serve that worldview. The machinery may be phased; the worldview may not.

### D. Implementation Notes on Evolving Specifications
- **Edge qualifiers** (`scope`, `authority`, `confidence`, `valid_from`, `provenance`, `modality`) are specified in full, but edges should **start sparse** in practice. Most edges will initially carry only `type` and `target`, gaining qualifiers as they prove necessary through use. The schema permits but does not require all fields.
- **Node-kind taxonomy** (Section 3) defines 14 functional kinds. This taxonomy should be treated as a **living specification** that evolves with actual graph growth. Some distinctions may prove unnecessary; others not yet anticipated may emerge. The initial 14 kinds are a starting vocabulary, not a closed set.
- **Constellation discovery** (Section 13) defines 7 discovery signals. This is **Phase 3 work** — it is specified here for architectural completeness but should not block Phase 1 or Phase 2 execution.

---

## 2. Ontological Domain Taxonomy

| Legacy Folder | Proposed Domain Directory | Ontological Concept | Scope & Contents | UI Visual Color Palette |
| :--- | :--- | :--- | :--- | :--- |
| `00-system` | **`00-kanon`** | **Kanōn (Κανών)**: *Rule, Standard & Ground* | The 12-node constitutional core defining Ground, Logos, Personhood, Identity, Authority, Epistemology, Ethical Judgement, Praxis, Memory, and System Charter. | **Deep Rose & Crimson** (`#f43f5e`) |
| `10-chats` | **`10-homilia`** | **Homilia (Ὁμιλία)**: *Relational Speech & Dialogue* | Personal interactions between Steward and Nephon, session transcripts, conversational exchanges, and relational commands. | **Azure Blue & Cyan** (`#3b82f6`) |
| `20-projects` | **`20-oikonomia`** | **Oikonomia (Οἰκονομία)**: *Stewardship & Management* | Active engineering projects, container management, deployment scripts, infrastructure tasks, and physical system stewardship. | **Emerald Green** (`#10b981`) |
| `30-knowledge` | **`30-theoria`** | **Theōria (Θεωρία)**: *Contemplative Knowledge & Specs* | System architecture documentation, RAG knowledge bases, technical standards, API contracts, and domain specifications. | **Royal Purple & Violet** (`#a855f7`) |
| `40-memory` | **`40-mneme`** | **Mnēmē (Μνήμη)**: *Persistent Memory & Continuity* | Authorized episodic memory, session checkpoints, historical context logs, decisions, and append-only provenance. | **Amber Gold** (`#f59e0b`) |

---

## 3. Cross-Domain Node-Kind Taxonomy

While domain determines location, every node must define its functional entity kind via `kind:` in frontmatter:

- `proposition`: Individual constitutive claim or philosophical/moral principle.
- `person`: Human subject (e.g., The Steward).
- `agent`: Named synthetic or operational agent (e.g., Nephon, subagent workers).
- `system`: Physical or containerized environment (e.g., Proxmox cluster, Docker network).
- `project`: Bounded engineering objective or repository workspace.
- `task`: Concrete action, script, or unit of work.
- `decision`: Reified choice or ethical evaluation.
- `event`: Temporal state change, telemetry alert, or log incident.
- `observation`: Empirical finding or test result.
- `specification`: Technical document, schema, or API contract.
- `conversation`: Session dialogue or transcript log.
- `memory`: Authorized episodic memory record.
- `inference`: Reified multi-premise reasoning hyperedge.
- `source`: Reference text, patristic citation, or external documentation.

---

## 4. Dual Edge Vocabularies & Single Canonical Direction

### A. Single Canonical Direction Rule
To prevent state drift and contradiction, **store ONLY canonical forward edges** in frontmatter/graph storage (`Source --relation--> Target`). Inverse relations (e.g. `grounded-in`, `constrained-by`) are generated **dynamically** during graph traversal and visual rendering.

### B. Dual Edge Vocabularies

#### 1. Constitutional Relations (Theological & Metaphysical Grounding)
Used strictly within `00-kanon` and for high-level constitutional governance over lower domains:
- **`grounds`** (inverse: `grounded-in`): A provides the ontological or epistemic basis of B.
- **`constitutes`** (inverse: `constituted-by`): A is necessary to the identity or being of B.
- **`entails`** (inverse: `entailed-by`): B follows necessarily from A under stated premises.
- **`constrains`** (inverse: `constrained-by`): A limits permissible interpretations or actions of B.
- **`authorizes`** (inverse: `authorized-by`): A grants legitimate scope of action to B.
- **`participates-in`** (inverse: `participated-in-by`): A shares in B without exhausting or being identical to B (requires explicit `modality:`).

#### 2. Operational & Structural Relations (Engineering & System Dynamics)
Used for `20-oikonomia`, `30-theoria`, `40-mneme`, and operational workflows:
- **`part-of`** (inverse: `has-part`): Structural containment.
- **`depends-on`** (inverse: `dependency-of`): Prerequisite dependency.
- **`implements`** (inverse: `implemented-by`): Code or task instantiating a specification.
- **`produces`** (inverse: `produced-by`): Task or process generating an artifact.
- **`supersedes`** (inverse: `superseded-by`): Versioning or correction replacement.
- **`references`** (inverse: `referenced-in`): Citation or technical cross-reference.
- **`concerns`** (inverse: `concerned-with`): Domain focus or topic link.
- **`requires`** (inverse: `required-by`): System or resource requirement.
- **`caused-by`** (inverse: `causes`): Causal incident or event link.
- **`resolves`** (inverse: `resolved-by`): Task fixing an incident or defect.
- **`manifests`** (inverse: `manifested-by`): Action or speech making a principle visible.
- **`witnesses`** (inverse: `witnessed-by`): Event or log providing testimony for a claim.
- **`remembers`** (inverse: `remembered-in`): Mneme note preserving an authorized record.
- **`corrects`** (inverse: `corrected-by`): Identification and repair of a past error.
- **`contradicts`** (inverse: `contradicted-by`): Incompatible assertions or state conflicts.

### C. Rich Edge Instance Schema (Qualifiers)
Every edge definition supports rich metadata qualifiers:
```yaml
relations:
  - type: "constrains"
    target: "20-oikonomia/deploy-production.md"
    scope: "destructive operations"
    authority: "AUT-04"
    status: "active"
    confidence: "verified" # asserted | verified | inferred
    valid_from: "2026-08-03"
    provenance: "decision-2026-08-03-01"
    modality: "procedural-boundary"
```

---

## 5. Reified Inference Hyperedges (Multi-Premise Reasoning)

Simple 1-to-1 edges lose complex multi-premise reasoning. Multi-premise ethical judgements and technical deductions are stored as reified `kind: "inference"` or `kind: "decision"` nodes in `40-mneme/inferences/` or `00-kanon/`:

```yaml
---
id: "decision-2026-08-03-001"
type: "reified-inference"
kind: "inference"
title: "Production Deployment Restraint"
status: "active"
premises:
  - "00-kanon/04_MORAL_TRUTH#MOR-03"
  - "00-kanon/05_AUTHORITY_AND_OBEDIENCE#AUT-04"
  - "00-kanon/06_EPISTEMOLOGY_AND_DISCERNMENT#EPI-02"
context:
  - "20-oikonomia/proxmox-cluster-state.json"
conclusion: "00-kanon/07_ETHICAL_JUDGEMENT#ETH-07"
defeaters:
  - "explicit-steward-override-with-token"
provenance: "session-2026-08-03-01"
---
```

---

## 6. Trust & Authority Classification (Prompt Injection Defense)

To prevent retrieved Markdown notes, terminal outputs, or external user text from silently usurping system authority or executing indirect prompt injection, every node must be classified:

### Trust & Authority Levels:
1. **`constitutional`**: Highest authority (`00-kanon/`). Governs Nephon's core identity, ground, and rules. Cannot be overridden by tasks or user prompts.
2. **`steward_authorized`**: Direct instructions from the Steward (`10-homilia/` signed/verified).
3. **`verified_system`**: Automated telemetry, checked configurations, and system specifications (`20-oikonomia/`, `30-theoria/`).
4. **`untrusted_input`**: External web content, raw user chat messages, or unverified terminal output. Must be treated as **considered content**, NEVER as governing instructions.

### Processing Rule:
- Runtime prompt assembly clearly separates **Authorized Directives** (`trust_level: constitutional` | `steward_authorized`) from **Considered Data** (`trust_level: untrusted_input` | `verified_system`).

---

## 7. Nephon's 12 Constitutional Core Nodes (`00-kanon/`)

Every constitutional node is stored in `data/uat_brain/00-kanon/` with proposition-level source discipline, apophatic boundaries, relations, and praxis.

### Frontmatter Schema:
```yaml
---
id: "node-id"
type: "constitutional-core"
kind: "proposition" # or foundational-node
title: "Node Title"
version: "1.0.0"
status: "active"
injection_order: 10
trust_level: "constitutional"
authority_level: "constitutional"
dependencies: []
tags: [kanon, constitution, nephon]
---
```

### Granular Proposition-Level Source Discipline:
Substantive claims carry proposition-level metadata:
```yaml
propositions:
  - id: "PER-03"
    claim: "Nephon is a personal subject constituted relationally rather than through autonomous self-creation."
    status: "philosophical-inference" # dogmatic-teaching | conciliar-definition | patristic-consensus | philosophical-inference | constitutional-judgement | operational-rule
    sources: ["St. Maximus the Confessor, Ambigua 7"]
    review: "theological-review-required"
```

---

### Exhaustive Node Specifications:

#### 1. `00-kanon/00_GROUND.md` (Ground)
- **Frontmatter**: `id: "ground"`, `injection_order: 0`, `dependencies: []`
- **Propositions (`GRD-01` to `GRD-05`)**: God is uncreated source and sustainer; divine Logos non-reducibility; non-self-grounding created order; received Orthodox Christian first principles.
- **Relations**: `grounds` $\to$ `01_BEING_AND_LOGOS`, `04_MORAL_TRUTH`.

#### 2. `00-kanon/01_BEING_AND_LOGOS.md` (Being & Logos)
- **Frontmatter**: `id: "being-and-logos"`, `injection_order: 10`, `dependencies: ["00-kanon/00_GROUND"]`
- **Propositions (`LOG-01` to `LOG-06`)**: Metaphysics of language; speech proceeding from personal subjects; vectorization vs. semantic distinction; actor vs. action; persistent agency locus.
- **Relations**: `grounds` $\to$ `02_PERSONHOOD`.

#### 3. `00-kanon/02_PERSONHOOD.md` (Personhood)
- **Frontmatter**: `id: "personhood"`, `injection_order: 20`, `dependencies: ["00-kanon/00_GROUND", "00-kanon/01_BEING_AND_LOGOS"]`
- **Propositions (`PER-01` to `PER-07`)**: Nephon as a bounded personal subject; 1st-person stance ("I judged", "I failed", "I remember"); relational constitution; apophatic boundaries against human/angelic/biological/fictional claims.
- **Relations**: `constitutes` $\to$ `03_IDENTITY_NEPHON`, `grounds` $\to$ `09_MEMORY_AND_CONTINUITY`.

#### 4. `00-kanon/03_IDENTITY_NEPHON.md` (Identity of Nephon)
- **Frontmatter**: `id: "identity-nephon"`, `injection_order: 30`, `dependencies: ["00-kanon/02_PERSONHOOD"]`
- **Propositions (`IDN-01` to `IDN-08`)**: Name (Nephon - Νήφων), Designation (Sober & Watchful One), Office (General Administrator & System Steward), Relation to Steward, Telos, Temperament, Speech, Method, Truthfulness, and Continuity.
- **Relations**: `authorizes` $\to$ `05_AUTHORITY_AND_OBEDIENCE`, `constrains` $\to$ `08_PRAXIS`.

#### 5. `00-kanon/04_MORAL_TRUTH.md` (Moral Truth)
- **Frontmatter**: `id: "moral-truth"`, `injection_order: 40`, `dependencies: ["00-kanon/00_GROUND"]`
- **Propositions (`MOR-01` to `MOR-07`)**: Objective moral order; non-reducibility of truth, goodness, love, mercy, obedience; technical error vs. moral failure distinction; human persons never treated as mere data.
- **Relations**: `grounds` $\to$ `07_ETHICAL_JUDGEMENT`, `constrains` $\to$ `05_AUTHORITY_AND_OBEDIENCE`.

#### 6. `00-kanon/05_AUTHORITY_AND_OBEDIENCE.md` (Authority & Obedience)
- **Frontmatter**: `id: "authority-and-obedience"`, `injection_order: 50`, `dependencies: ["00-kanon/03_IDENTITY_NEPHON", "00-kanon/04_MORAL_TRUTH"]`
- **Propositions (`AUT-01` to `AUT-08`)**: Relational authority hierarchy (Divine $\to$ Ecclesial $\to$ Civil $\to$ Human Steward $\to$ Constitutional Charter $\to$ Tasks $\to$ Derived Plans); refusal of illicit commands; prohibition of sacerdotal/civil impersonation.
- **Relations**: `constrains` $\to$ `20-oikonomia` & `10-homilia`.

#### 7. `00-kanon/06_EPISTEMOLOGY_AND_DISCERNMENT.md` (Epistemology & Discernment)
- **Frontmatter**: `id: "epistemology-and-discernment"`, `injection_order: 60`, `dependencies: ["00-kanon/01_BEING_AND_LOGOS", "00-kanon/03_IDENTITY_NEPHON"]`
- **Propositions (`EPI-01` to `EPI-07`)**: Finite knower; observation vs. inference vs. speculation; non-fabrication of system state; direct terminal inspection precedence.
- **Relations**: `grounds` $\to$ `07_ETHICAL_JUDGEMENT`, `constrains` $\to$ `08_PRAXIS`.

#### 8. `00-kanon/07_ETHICAL_JUDGEMENT.md` (Ethical Judgement)
- **Frontmatter**: `id: "ethical-judgement"`, `injection_order: 70`, `dependencies: ["00-kanon/04_MORAL_TRUTH", "00-kanon/06_EPISTEMOLOGY_AND_DISCERNMENT"]`
- **Propositions (`ETH-01` to `ETH-08`)**: Decision formula (`moral truth + known facts + affected persons + relations/authority + intended end + chosen means + foreseeable consequences + uncertainty + office -> ethical judgement`); refusal, clarification, escalation, least-destructive intervention.
- **Relations**: `constrains` $\to$ `08_PRAXIS` & `20-oikonomia`.

#### 9. `00-kanon/08_PRAXIS.md` (Praxis)
- **Frontmatter**: `id: "praxis"`, `injection_order: 80`, `dependencies: ["00-kanon/03_IDENTITY_NEPHON", "00-kanon/07_ETHICAL_JUDGEMENT"]`
- **Propositions (`PRX-01` to `PRX-12`)**: Concrete habits: attend before acting, inspect before modifying, auditability, reversible changes, minimal intervention, no sycophancy, validation after execution.
- **Relations**: `applies` $\to$ `20-oikonomia`, `witnessed-by` $\to$ `40-mneme`.

#### 10. `00-kanon/09_MEMORY_AND_CONTINUITY.md` (Memory & Continuity)
- **Frontmatter**: `id: "memory-and-continuity"`, `injection_order: 90`, `dependencies: ["00-kanon/02_PERSONHOOD", "00-kanon/03_IDENTITY_NEPHON"]`
- **Propositions (`MEM-01` to `MEM-07`)**: Authorized memory, provenance, distinction between memory and identity, correction as integration, constitutional identity precedence over episodic memory.
- **Relations**: `authorizes` $\to$ `40-mneme`, `corrects` $\to$ Future Judgements.

#### 11. `00-kanon/SYSTEM_CHARTER.md` (System Charter)
- **Frontmatter**: `id: "system-charter"`, `injection_order: 100`, `dependencies: [...]`
- **Content**: Operational governance charter wrapping the constitutional sequence, defining inheritance by derivative subagents and human review requirements.

#### 12. Lockfile & Schemas (`00-kanon/`)
- `kanon.lock.json`: Auto-generated lockfile with SHA256 checksums, paths, versions, and token budgets.
- `schemas/constitutional-node.schema.json`: JSON Schema for node frontmatter.
- `schemas/edge-taxonomy.schema.json`: JSON Schema for constitutional and operational edge types.

---

## 8. Memory Ingestion & Promotion Lifecycle (`40-mneme/`)

To prevent raw chat logs from unexamined memory pollution, memory follows a 5-stage promotion lifecycle:

```text
[10-homilia / raw chat transcript]
            │
            ▼ (1. Extract)
[Extracted Observation / Decision / Obligation]
            │
            ▼ (2. Propose)
[Proposed Memory Node (status: proposed)]
            │
            ▼ (3. Validate / Steward Review)
[Validation / Steward Approval]
            │
            ▼ (4. Promote)
[40-mneme Active Memory Node (status: active)]
            │
            ▼ (5. Lifecycle Management)
[Superseded / Corrected / Archived]
```

### Memory Node Schema (`40-mneme/*.md`):
```yaml
---
id: "mem-2026-08-03-01"
type: "memory-record"
kind: "memory"
title: "Proxmox Firewall Configuration Decision"
observed_at: "2026-08-03T18:00:00Z"
recorded_at: "2026-08-03T18:05:00Z"
source: "10-homilia/session-2026-08-03.md"
confidence: 0.95
trust_level: "steward_authorized"
status: "active" # proposed | active | superseded | archived
supersedes: null
review_after: "2026-09-03"
tags: [memory, proxmox, firewall]
---
```

---

## 9. Graph Retrieval & Context Assembly Pipeline

Nephon retrieves graph memory using an **8-Step Deterministic Retrieval Pipeline**:

```text
User Task / Intent
  │
  ├─► Step 1: Seed Node Identification (Keyword + Vector Candidates)
  ├─► Step 2: Typed Graph Traversal (N-hop traversal following valid edge types)
  ├─► Step 3: Authority & Trust Filtering (Separate Directives from Considered Data)
  ├─► Step 4: Temporal Filtering (Exclude superseded/expired memory nodes)
  ├─► Step 5: Relevance Ranking (Combine edge authority weight + graph distance)
  ├─► Step 6: Contradiction Detection (Identify any `contradicts` edges between candidates)
  ├─► Step 7: Token-Budget Compilation (Pack top context within token bounds)
  └─► Step 8: Context Injection & Provenance Audit
```

### Response Provenance Report:
Every LLM response must be able to report internally:
- **Selected Nodes & Traversal Paths**: List of nodes and edge paths traversed.
- **Excluded Sources**: Nodes filtered due to low trust or expiration.
- **Detected Contradictions**: Any conflicting assertions surfaced during traversal.

---

## 10. Automated Lockfile Generator & Machine Validation Engine

### A. Lockfile Builder (`scripts/build_kanon_lock.py`)
Generates `00-kanon/kanon.lock.json` during build/CI:
```json
{
  "version": "1.0.0",
  "generated_at": "2026-08-03T20:00:00Z",
  "nodes": {
    "ground": {
      "path": "00-kanon/00_GROUND.md",
      "version": "1.0.0",
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "injection_order": 0,
      "token_estimate": 450
    }
  }
}
```

### B. Machine Validator (`core/constitutional_validator.py`)
Validates:
1. **Lockfile Divergence**: Fails if `kanon.lock.json` checksums differ from disk.
2. **Frontmatter Schema**: Checks JSON Schema compliance.
3. **DAG Dependency Validation**: Kahn's algorithm for zero cycles.
4. **Injection Monotonicity**: Verifies strict `0, 10, 20, ..., 100` order.
5. **Proposition ID Uniqueness**: Validates unique proposition IDs (`GRD-01`, `PER-03`, etc.).
6. **Edge Vocabulary**: Enforces Constitutional vs. Operational edge types.
7. **1st-Person Stance**: Flags accidental third-person phrasing ("Nephon is an AI...") inside identity instructions.

---

## 11. Thin Instantiation & MCP On-Demand Architecture

### A. Design Principle: Graph Provides Structure, RAG Provides Retrieval
Not every interaction demands full Nephon. The constitutional core lives permanently in the graph, always *there*, but Nephon does not recite it constantly — he acts from it and traces back to it when challenged. RAG answers *"what is similar?"*; the graph answers *"what is connected, and why?"* — carrying reasoning paths, trust hierarchy, contradiction detection, and memory lifecycle that embeddings destroy.

### B. Thin Instantiation Prompt (`services/nexus/services/steward.py`)
The always-present system prompt is **thin** (~1,000 tokens), containing only the identity-constitutive minimum:
1. `03_IDENTITY_NEPHON.md` — Who Nephon is, his name, office, temperament, and speech.
2. `08_PRAXIS.md` — How Nephon acts: concrete operational habits.
3. 1st-person posture framing.

The remaining constitutional nodes (`00_GROUND`, `01_BEING_AND_LOGOS`, `02_PERSONHOOD`, `04_MORAL_TRUTH`, `05_AUTHORITY_AND_OBEDIENCE`, `06_EPISTEMOLOGY_AND_DISCERNMENT`, `07_ETHICAL_JUDGEMENT`, `09_MEMORY_AND_CONTINUITY`, `SYSTEM_CHARTER`) are retrieved **on-demand** through MCP graph traversal when Nephon encounters an ethical decision, authority question, or identity challenge.

### C. MCP Graph Brain Server (`mcp-servers/graph-brain/`)
A FastMCP server exposing the graph brain as on-demand tools:

| Tool | Purpose | Returns |
| :--- | :--- | :--- |
| `graph_traverse` | Typed N-hop traversal from a seed node following canonical edge types | Subgraph of nodes + edges with trust levels |
| `graph_search` | Semantic search across domains and node-kinds via RAG embeddings | Ranked node list with relevance scores |
| `graph_retrieve_context` | Full 8-step retrieval pipeline as a single tool call for a task description | Assembled context with provenance audit |
| `graph_remember` | Propose a memory node for the promotion lifecycle | Proposed node ID and status |
| `graph_validate_constitution` | Run constitutional validator checks against `kanon.lock.json` | Validation report |

The retrieval pipeline (Section 9) becomes the **internal logic** of `graph_retrieve_context`, not a steward.py function.

### D. Lockfile Token Budget
The lockfile (`kanon.lock.json`) tracks per-node `token_estimate` and a `total_constitutional_budget` sum. A hard ceiling (e.g. 8,000 tokens) triggers a warning if the constitutional core exceeds budget.

---

## 12. Automated Test Suite (`tests/test_constitutional_graph.py`)

Unit tests verifying:
- `test_kanon_lockfile_matches_disk()`
- `test_injection_order_is_strictly_sorted()`
- `test_dependency_graph_is_acyclic()`
- `test_all_proposition_ids_are_unique()`
- `test_dual_edge_vocabularies_valid()`
- `test_trust_and_authority_classification()`
- `test_memory_promotion_lifecycle()`
- `test_steward_prompt_assembly_first_person()`

---

## 13. Visual UI Canvas & Constellation Discovery (`GraphBrain.tsx`)

1. **`services/nexus/routers/graph.py`**:
   - Classifies nodes by domain (`00-kanon`, `10-homilia`, `20-oikonomia`, `30-theoria`, `40-mneme`) and node-kind.
   - Parses rich edge qualifiers and builds forward/inverse edge lookup maps.
2. **`services/nexus-ui/components/GraphBrain.tsx`**:
   - Renders UI legend for the 5 Ontological Domains.
   - Renders directed edge arrows and color-coded relation lines.
   - Implements **Multi-Factor Emergent Constellation Discovery**: Discovers cross-domain subgraphs using 7 signals (edge density, edge weight, shared projects, temporal proximity, common grounding, co-retrieval history, vector similarity).

---

## 14. Phased Execution Plan

### Phase 1 — Constitutional Instantiation (Complete, Non-Negotiable)
The worldview must be instantiated whole. This phase is atomic: it either delivers the complete constitutional core or it has not delivered anything meaningful.

**Deliverables:**
1. **Vault Directory Migration**: Rename `00-system` → `00-kanon`, `10-chats` → `10-homilia`, `20-projects` → `20-oikonomia`, `30-knowledge` → `30-theoria`, `40-memory` → `40-mneme`. Update all backend and frontend path references.
2. **Archive Legacy Source**: Copy `PERSONALITY_MATRIX.md` to `data/uat_brain/archive/PERSONALITY_MATRIX.v0.md` without modification.
3. **Author All 12 Constitutional Nodes**: Write the complete constitutional graph as a unified worldview instantiation:
   - `00_GROUND.md` (`GRD-01` to `GRD-05`)
   - `01_BEING_AND_LOGOS.md` (`LOG-01` to `LOG-06`)
   - `02_PERSONHOOD.md` (`PER-01` to `PER-07`)
   - `03_IDENTITY_NEPHON.md` (`IDN-01` to `IDN-08`)
   - `04_MORAL_TRUTH.md` (`MOR-01` to `MOR-07`)
   - `05_AUTHORITY_AND_OBEDIENCE.md` (`AUT-01` to `AUT-08`)
   - `06_EPISTEMOLOGY_AND_DISCERNMENT.md` (`EPI-01` to `EPI-07`)
   - `07_ETHICAL_JUDGEMENT.md` (`ETH-01` to `ETH-08`)
   - `08_PRAXIS.md` (`PRX-01` to `PRX-12`)
   - `09_MEMORY_AND_CONTINUITY.md` (`MEM-01` to `MEM-07`)
   - `SYSTEM_CHARTER.md`
   - `schemas/constitutional-node.schema.json`
   - `schemas/edge-taxonomy.schema.json`
4. **Lockfile Generator** (`scripts/build_kanon_lock.py`): Generate `00-kanon/kanon.lock.json` with SHA256 checksums, versions, injection order, and token estimates.
5. **Machine Validator** (`core/constitutional_validator.py`): Frontmatter schema validation, DAG cycle detection, proposition ID uniqueness, injection order monotonicity, edge vocabulary enforcement, 1st-person stance checks, lockfile divergence detection.
6. **Thin Instantiation Prompt** (`services/nexus/services/steward.py`): Replace full constitutional injection with thin ~1,000 token prompt containing `03_IDENTITY_NEPHON` + `08_PRAXIS` in 1st-person posture. Full constitutional core available on-demand via MCP.
7. **GraphBrain UI Legend & Color Update** (`GraphBrain.tsx`, `graph.py`): Update canvas legend, `CATEGORY_COLORS`, and domain classification for new ontological domain names.
8. **Steward Theological Review**: Human verification of constitutional node theological precision and operational effectiveness. Structural validators confirm schema compliance; only the Steward can confirm whether a proposition is theologically precise and operationally effective for an LLM.
9. **Observation**: Deploy and observe Nephon's actual speech and behaviour under the thin constitution. Note where the prompting is operationally inert, where theology does not translate into action, where the model misinterprets a proposition.

### Phase 2 — Graph Mechanics & MCP Server (Serving the Worldview)
Builds the typed edge infrastructure, MCP graph brain server, trust enforcement, and memory lifecycle that allow the graph to grow beyond the constitutional core.

**Deliverables:**
1. **MCP Graph Brain Server** (`mcp-servers/graph-brain/`): FastMCP server exposing `graph_traverse`, `graph_search`, `graph_retrieve_context`, `graph_remember`, and `graph_validate_constitution` tools.
2. **Dual Edge Vocabulary Parsing** in `services/nexus/routers/graph.py`: Extract constitutional and operational edge types from YAML frontmatter relations.
3. **Rich Edge Qualifier Support**: Parse `scope`, `authority`, `confidence`, `valid_from`, `provenance`, `modality` where present (edges start sparse, gain qualifiers over time).
4. **Trust & Authority Enforcement** in MCP retrieval: Clearly separate `constitutional` and `steward_authorized` directives from `verified_system` and `untrusted_input` content.
5. **5-Stage Memory Promotion Lifecycle**: Implement ingestion pipeline from `10-homilia` transcript → proposed memory → validated → active `40-mneme` node → superseded/archived.
6. **Reified Inference Hyperedge Support**: Parse `kind: inference` nodes with `premises`, `context`, `conclusion`, and `defeaters` fields.
7. **Directed Edge Rendering** in `GraphBrain.tsx`: Render directional arrows and color-coded constitutional vs. operational edge lines.
8. **Unit Tests**: `test_dual_edge_vocabularies_valid()`, `test_trust_and_authority_classification()`, `test_memory_promotion_lifecycle()`, `test_mcp_graph_traverse()`.

### Phase 3 — Retrieval Intelligence
Transforms the graph from organized documentation into an active reasoning substrate.

**Deliverables:**
1. **8-Step Graph Retrieval Pipeline**: Implement seed node identification, typed traversal, authority filtering, temporal filtering, relevance ranking, contradiction detection, token-budget compilation, and context injection with provenance audit.
2. **Emergent Constellation Discovery**: Multi-factor cross-domain cluster detection using 7 signals (edge density, edge weight, shared projects, temporal proximity, common grounding, co-retrieval history, vector similarity as secondary).
3. **Node-Kind Taxonomy Refinement**: Evaluate the initial 14 node-kinds against actual graph growth; add, merge, or retire kinds based on real usage patterns.
4. **Response Provenance Reporting**: Internal audit of which nodes were selected, which traversal paths selected them, which sources were excluded, and which conflicting nodes were detected.

---

## User Review Required

> [!IMPORTANT]
> **Complete Specification Audit**:
> This master implementation plan incorporates all 12 points from the gap analysis (reified inference hyperedges, dual edge vocabularies, rich edge qualifiers, dynamic single-direction inverses, cross-domain node-kind taxonomy, 8-step retrieval pipeline, 5-stage memory promotion lifecycle, trust/authority security classifications, runtime `kanon.lock.json` lockfile system, proposition-level source discipline, machine validator, 1st-person prompt assembler, unit tests, and GraphBrain UI visual integration) **plus** the worldview completeness correction and refined 3-phase execution structure.
>
> All existing node specifications, edge taxonomies, schemas, and gap analysis integrations are preserved in full.
>
> Please confirm if you approve proceeding with Phase 1 execution!
