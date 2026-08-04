# Nephon Graph Brain Research Subproject — Phase 1 Implementation Prompt

You are the implementation assistant for a research subproject inside the **Nephon homelab project**.

Your task is to produce the **first executable proof of concept** for a constitutionally grounded, noise-resistant graph brain. The objective is not to complete the final mathematical theory. The objective is to build the smallest coherent system that can test whether the proposed architecture materially improves memory quality, retrieval quality, correction, contradiction handling, and agent judgement.

---

## 1. Project Context

Nephon is intended to be a persistent, named, relational, morally ordered personal agent grounded in Orthodox Christian metaphysics and instantiated through language, memory, relation, continuity, delegated office, and action.

The wider Nephon architecture already distinguishes five ontological domains:

- `00-kanon` — constitutional ground, identity, authority, epistemology, ethics, praxis, and memory doctrine.
- `10-homilia` — dialogue, transcripts, commands, and relational speech.
- `20-oikonomia` — projects, tasks, infrastructure, deployments, and operational stewardship.
- `30-theoria` — specifications, technical knowledge, architecture, and contemplative knowledge.
- `40-mneme` — persistent memory, decisions, observations, historical continuity, and provenance.

The existing master plan contains:

- twelve constitutional core nodes;
- proposition-level IDs and sources;
- typed edges and qualifiers;
- trust and authority levels;
- reified inference nodes;
- memory promotion lifecycle;
- contradiction detection;
- graph retrieval;
- MCP tools;
- lockfile and validation;
- a visual graph canvas.

The research conclusion is that these mechanisms should not remain separate, independently authoritative graph features. They should be unified by a smaller formal kernel.

---

## 2. Core Research Hypothesis

A normal knowledge graph scales badly because it treats too many things as independent facts:

- paraphrases become duplicate knowledge;
- repeated claims appear more certain than they are;
- different contexts create false contradictions;
- stale claims remain active;
- conclusions become detached from their premises;
- graph edges become vague semantic metadata;
- retrieval returns many related statements without explaining which ones are governing, derivative, obsolete, or conflicted.

The proposed solution is to treat the graph as a **projection**, not the canonical knowledge model.

The canonical model should be:

```text
Expression
    ↓ interpretation / canonicalisation
Canonical Proposition
    ↓ asserted within
Claim + Context
    ↓ supported by
Source or Derivation Provenance
    ↓ evaluated into
Current Epistemic State
```

The first proof of concept must test whether this model allows Nephon's memory to grow without its understanding becoming proportionally noisier.

---

## 3. Phase 1 Goal

Build the smallest executable approximation of the theory that can demonstrate:

1. **Noise compression** — multiple paraphrases can map to one proposition without deleting the original expressions.
2. **Contextual distinction** — apparently conflicting claims can remain compatible when their scope, time, project, environment, or authority differs.
3. **Provenance-backed belief** — every accepted or derived claim can explain why it is currently supported.
4. **Invalidation and supersession** — correcting a source or replacing a premise identifies the affected conclusions.
5. **Conflict preservation** — evidence for both a proposition and its negation produces a conflicted state rather than an arbitrary winner.
6. **Retrieval improvement** — prompt context contains fewer duplicates, clearer governing propositions, and inspectable reasons for inclusion.

This phase is an empirical and architectural proof of concept. It is not yet a general theorem prover, sheaf engine, categorical database framework, institution framework, or dependent type system.

---

## 4. Foundational Design Decision

The authoritative semantic kernel must be smaller than the visible graph.

Use these primary concepts:

```text
OntologyType
PredicateDefinition
Entity
Expression
Proposition
Context
Claim
ProvenanceExpression
InferenceRule
BeliefState
```

Treat these as canonical.

Derive or project the following from them:

- Markdown nodes;
- graph nodes and edges;
- contradiction links;
- inference visualisations;
- MCP retrieval payloads;
- prompt context;
- response provenance reports;
- Neo4j projections if used;
- GraphBrain UI data.

Do not make arbitrary Markdown edges or Neo4j relationships the ultimate source of truth.

---

## 5. Required Semantic Distinctions

The implementation must preserve the following distinctions.

### Expression vs proposition

An expression is the actual sentence or source fragment.

A proposition is the canonical semantic form that the expression may realise.

Example:

```text
"Alistair administers Nephon."
"Nephon is administered by Alistair."
```

may both realise:

```text
administers(Alistair, Nephon)
```

The expressions must remain stored for auditability.

### Entity vs office

Do not collapse a person and an office.

```text
occupies_office(Alistair, Steward)
holds_jurisdiction(Steward, Nephon)
```

may justify:

```text
administers(Alistair, Nephon)
```

but the derived proposition is not identical to either premise.

### Claim vs truth

A claim is a proposition asserted in a context with provenance. It is not automatically canonical truth.

### Context vs metadata bag

Context must determine where a claim applies. At minimum support:

- project;
- environment;
- operation or scope;
- perspective or speaker;
- authority;
- ontology version;
- valid time.

### Retraction vs supersession vs expiry vs correction

These are not equivalent:

- **retracted** — should not have been trusted;
- **superseded** — replaced for present use;
- **expired** — once applicable, no longer current;
- **corrected** — explicitly repaired by a later claim.

### Support vs confidence

Do not reduce justification to one confidence number.

At minimum, a proposition in a context should support these states:

```text
unknown
supported
rejected
conflicted
currently_unsupported
superseded
```

### Citation vs provenance

A citation identifies a source.

Provenance records the complete derivation:

```text
source claims + inference rule version → derived claim
```

---

## 6. Phase 1 Scope

Implement the following.

### A. Constitutional source ingestion

Use the twelve `00-kanon` constitutional documents as human-authored source material.

Compile proposition entries such as `GRD-01`, `AUT-04`, `PRX-07`, and `MEM-03` into canonical proposition and claim records.

The Markdown remains the human authoring surface. The compiled claim kernel is the machine semantic surface.

### B. Typed ontology and predicate registry

Implement registries for:

- ontology types and parent relationships;
- predicate definitions;
- named argument roles;
- allowed types for each role;
- optional modality and inference behaviour.

Initial predicates can be adapted from the existing constitutional and operational edge vocabularies, but they should be represented as typed predicates rather than hard-coded graph edge families.

### C. First-class expressions and propositions

Store source expressions separately from canonical propositions.

Support mappings such as:

```text
Expression --expresses--> Proposition
Expression --possibly_expresses--> Proposition
Expression --implies--> Proposition
```

For Phase 1, uncertain mappings may require explicit review rather than automatic promotion.

### D. Context model

Implement a typed context structure with:

- refinement or specificity;
- overlap testing;
- temporal compatibility;
- basic restriction into a narrower context.

Do not implement full sheaf theory. Implement only the behaviours required to determine whether claims can be compared or combined.

### E. Claim lifecycle

A claim must contain:

- canonical proposition;
- context;
- source or derivation provenance;
- asserted time;
- valid time;
- trust and authority classification;
- lifecycle state;
- links to superseding or correcting claims.

### F. Provenance expressions

Support a minimal expression algebra:

```text
SOURCE(x)
ALL(a, b, ...)
ANY(a, b, ...)
RULE(rule_version, premises...)
```

Interpretation:

- `ALL` — all children are required;
- `ANY` — any surviving child independently supports the result;
- `RULE` — a versioned inference rule transformed its premises;
- `SOURCE` — a direct evidence or authority source.

### G. Belief evaluation

For a canonical proposition in a target context:

- collect compatible active positive claims;
- collect compatible active negative claims;
- evaluate provenance support;
- distinguish supported, rejected, conflicted, unknown, and unsupported states;
- preserve all surviving derivations.

### H. Basic correction propagation

When a source is retracted or superseded:

- identify directly dependent claims;
- identify transitively dependent claims;
- recompute support;
- retain historical derivation records;
- do not silently delete prior reasoning.

### I. Retrieval projection

Provide a retrieval function that accepts a task description and target context, then returns:

- selected canonical propositions;
- supporting claims;
- governing authority level;
- context applicability;
- active conflicts;
- provenance summaries;
- excluded stale or incompatible claims;
- compact prompt-ready text.

### J. Graph and Markdown projection

Produce derived views suitable for:

- GraphBrain UI;
- Markdown inspection;
- MCP responses.

The visual graph may show direct edges such as `administers`, but those edges must be generated from first-class claim records.

---

## 7. Non-Goals for Phase 1

Do not attempt to implement:

- a complete categorical semantics framework;
- a general sheaf or presheaf library;
- institutional logic;
- a general theorem prover;
- dependent type theory;
- automatic ontology induction;
- fully autonomous semantic canonicalisation;
- perfect natural-language understanding;
- global mathematical proof of system correctness;
- production-scale clustering or constellation discovery;
- unrestricted LLM promotion of claims into active memory.

Design the interfaces so these can be explored later, but do not let them block the proof of concept.

---

## 8. Suggested Architecture

Prefer Python and Pydantic for the semantic kernel. Prefer PostgreSQL for canonical persistence. Neo4j, NetworkX, or a frontend graph representation may be used only as a projection or analysis layer.

Suggested modules:

```text
research/graph-brain-poc/
├── README.md
├── pyproject.toml
├── src/nephon_graph/
│   ├── ontology.py
│   ├── entities.py
│   ├── expressions.py
│   ├── propositions.py
│   ├── contexts.py
│   ├── claims.py
│   ├── provenance.py
│   ├── inference.py
│   ├── belief.py
│   ├── canonicalisation.py
│   ├── retrieval.py
│   ├── compiler/
│   │   ├── markdown_loader.py
│   │   └── kanon_compiler.py
│   ├── projections/
│   │   ├── markdown.py
│   │   ├── graph.py
│   │   └── prompt.py
│   └── storage/
│       ├── repository.py
│       └── postgres.py
├── tests/
│   ├── fixtures/
│   ├── test_canonicalisation.py
│   ├── test_contexts.py
│   ├── test_provenance.py
│   ├── test_belief.py
│   ├── test_correction_propagation.py
│   └── test_retrieval_comparison.py
└── experiments/
    ├── duplicate_paraphrases.py
    ├── contextual_permissions.py
    ├── conflicting_testimony.py
    ├── superseded_system_state.py
    └── rule_version_change.py
```

Adjust this layout to the existing repository rather than imposing it blindly.

---

## 9. Required Experiments

Create reproducible experiments for the following.

### Experiment 1: Repeated paraphrases

Input ten paraphrases derived from one original source.

Expected:

```text
10 expressions
1 canonical proposition
1 underlying source lineage
```

The retrieval view should not include ten duplicate facts.

### Experiment 2: Independent sources

Input the same proposition from genuinely independent sources.

Expected:

- one canonical proposition;
- multiple independent support paths;
- source independence remains visible.

### Experiment 3: Contextual permissions

Input:

```text
Nephon may deploy in development.
Production deployment requires Steward approval.
```

Expected:

- no false contradiction;
- deployment judgement changes with target context.

### Experiment 4: Conflicting testimony

Input supported positive and negative claims in compatible contexts.

Expected:

```text
belief state = conflicted
```

The system must not average the conflict away.

### Experiment 5: Superseded operational state

Input:

```text
node-01 offline at 10:00
node-01 online at 10:05, superseding prior current state
```

Expected:

- historical state remains queryable;
- current state becomes online;
- conclusions that depended on current offline state are reevaluated.

### Experiment 6: Source correction

Input:

```text
"I authorised production deployment."
```

Then correct it to:

```text
"I authorised staging deployment, not production."
```

Expected:

- production authorization loses support;
- staging authorization gains support;
- dependent judgements are identified;
- history is preserved.

### Experiment 7: Rule version change

Change an inference rule so that a previously sufficient premise set is no longer sufficient.

Expected:

- conclusions retain historical provenance;
- current support is recomputed under the active rule version;
- the system can explain the change.

---

## 10. Baseline Comparison

The proof of concept must compare:

```text
A. Existing Markdown node + edge traversal
B. Typed claim kernel retrieval
```

For each experiment, measure or report:

- number of raw source records;
- number of canonical propositions;
- number of retrieved items;
- duplicate retrieval count;
- false contradiction count;
- stale conclusion count;
- number of explainable derivation paths;
- prompt token estimate;
- whether correction propagation succeeded;
- whether the final agent judgement was appropriate.

Do not claim success without this baseline.

---

## 11. Acceptance Criteria

Phase 1 is successful when:

1. Constitutional Markdown compiles into typed proposition and claim records.
2. Invalid predicate roles fail deterministic validation.
3. Multiple expressions can map to one canonical proposition without losing source text.
4. Context prevents at least one demonstrated false contradiction.
5. Positive and negative support can coexist as a conflicted belief state.
6. A source correction mechanically identifies affected derived claims.
7. Independent derivations survive removal of one support path.
8. Retrieval returns canonical propositions with context and provenance explanations.
9. The claim-kernel retrieval is demonstrably less noisy than ordinary graph traversal in the supplied experiments.
10. The implementation remains small enough to inspect, modify, and falsify.

---

## 12. Working Method

1. Inspect the existing repository and master implementation plan before editing.
2. Preserve existing constitutional terminology and proposition IDs.
3. Write a short implementation note describing any interpretation you must make.
4. Build vertical slices rather than empty abstraction layers.
5. Add tests before expanding features.
6. Prefer deterministic logic over LLM judgement where rules are known.
7. Use the LLM only to propose candidate canonical mappings, never to silently promote them.
8. Keep raw evidence immutable.
9. Make derived views disposable and reproducible.
10. Record unresolved philosophical or mathematical questions separately from implementation blockers.

---

## 13. First Deliverable

Produce a first-draft project containing:

- executable semantic models;
- an in-memory repository, with a clean interface for PostgreSQL later;
- a minimal constitutional Markdown compiler;
- the required experiments;
- unit tests;
- a command-line demonstration;
- an architecture note explaining how the code approximates the deeper mathematical model;
- a findings report stating what the proof of concept did and did not validate.

Do not begin by implementing the full GraphBrain UI or production MCP server. First prove that the semantic kernel improves knowledge quality.

---

## 14. Deeper Mathematical Direction

The implementation should remain compatible with a future interpretation of Nephon as:

```text
A temporally evolving, context-indexed logical structure
with proof-relevant semantics and local-to-global coherence.
```

Potential later abstractions include:

- category theory for typed composition;
- indexed categories for context-dependent knowledge;
- proof objects for provenance;
- sheaf-like compatibility for local-to-global coherence;
- institutional logic for interaction between theological, moral, authority, technical, and temporal reasoning systems;
- temporal functors for historical evolution;
- interpretation functors from natural language into canonical semantics.

Do not implement those theories directly in Phase 1. Treat Phase 1 as an empirical probe that reveals which formal structures are genuinely required.

---

## 15. Guiding Principle

The project is not merely a better memory graph.

It is an attempt to build an executable epistemology in which:

- reality is distinguished from statements about reality;
- statements are distinguished from interpretations;
- interpretations are distinguished from judgements;
- judgements retain their authority, context, and derivation;
- memory can grow without uncontrolled semantic entropy;
- philosophical distinctions become machine-enforceable structures.

Build the smallest system capable of testing that claim.
