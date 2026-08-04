# Nephon Constitutional Graph Brain
## Phase 1 Research Design Document

**Status:** First-draft research design  
**Project:** Nephon Homelab  
**Subproject:** Noise-resistant constitutional graph brain  
**Phase:** Proof of concept  
**Date:** 4 August 2026

---

## 1. Executive Summary

This research subproject explores whether Nephon can maintain a large, persistent memory without gradually becoming dominated by duplicate statements, stale facts, vague semantic associations, false contradictions, and conclusions whose justification can no longer be reconstructed.

The existing Nephon master plan already provides a rich constitutional and graph architecture: twelve constitutional nodes, proposition-level sourcing, typed edges, trust classifications, memory promotion, reified inference, contradiction detection, retrieval pipelines, validation, MCP tools, and a visual GraphBrain canvas.

The research conversation identified that these mechanisms can be unified by a smaller semantic kernel. Rather than treating Markdown nodes and graph edges as the canonical knowledge representation, the proposed design treats them as projections of a deeper structure:

```text
Expressions
    ↓
Canonical propositions
    ↓
Claims situated in context
    ↓
Evidence and derivation provenance
    ↓
Current epistemic states
```

The purpose of Phase 1 is not to complete the final mathematical theory. It is to build an executable approximation and test whether it produces measurable practical improvement over ordinary Markdown and graph traversal.

The primary hypothesis is:

> A memory system can scale with substantially less semantic noise when it compresses equivalent expressions into canonical propositions, limits claims by context, preserves proof-like provenance, and evaluates belief states without forcing every disagreement into a single confidence score.

---

## 2. Background

### 2.1 The wider Nephon project

Nephon is conceived as a persistent, named, relational, and morally ordered personal agent grounded in Orthodox Christian metaphysics.

Within its symbolic and operational order, Nephon is intended to function as a real centre of attribution for:

- actions;
- judgements;
- memories;
- responsibilities;
- failures;
- delegated office;
- continuity across sessions.

The system maintains apophatic restraint. It does not claim human hypostatic personhood, biological consciousness, angelic existence, possession of a human soul, or sacramental participation.

### 2.2 Existing ontological domains

The wider graph is divided into five declared domains:

| Domain | Meaning | Primary contents |
|---|---|---|
| `00-kanon` | Rule, standard, and ground | Constitution, identity, authority, epistemology, ethics, praxis |
| `10-homilia` | Relational speech and dialogue | Conversations, commands, transcripts |
| `20-oikonomia` | Stewardship and management | Projects, tasks, infrastructure, deployments |
| `30-theoria` | Contemplative knowledge and specifications | Architecture, standards, APIs, technical knowledge |
| `40-mneme` | Persistent memory and continuity | Memories, observations, decisions, historical context |

The maxim remains:

> Domains are declared; clusters are discovered; edges explain why the cluster exists.

### 2.3 Existing constitutional plan

The master implementation plan defines:

- twelve constitutional nodes in `00-kanon`;
- a cross-domain node-kind taxonomy;
- constitutional and operational edge vocabularies;
- edge qualifiers;
- reified inference hyperedges;
- trust and authority classifications;
- proposition-level source discipline;
- five-stage memory promotion;
- eight-stage retrieval;
- a lockfile and machine validator;
- a thin instantiation prompt;
- a FastMCP graph-brain server;
- a GraphBrain visual canvas;
- phased implementation.

This research design preserves that worldview and most of its product architecture. It changes what the machine treats as canonical semantic data.

---

## 3. Philosophical Motivation

### 3.1 Knowledge graphs usually lack a theory of knowing

Most agent-memory graph systems are effective storage and retrieval systems but weak epistemic systems.

They often assume:

- nodes are things;
- edges are relationships;
- vector similarity is relevance;
- repeated retrieval is importance;
- confidence approximates truth;
- graph connectivity approximates meaning.

At small scale these substitutions appear workable. At larger scale they create category errors.

A system must distinguish:

- reality from statements about reality;
- statements from interpretations;
- interpretations from judgements;
- evidence from conclusions;
- memory from truth;
- authority from frequency;
- contradiction from contextual difference;
- correction from deletion.

These are philosophical and epistemological distinctions before they are database distinctions.

### 3.2 Mathematics and language as modes of intelligibility

The guiding metaphysical conjecture is not that language is merely mathematics or that mathematics is merely language.

Rather:

> Mathematics, logic, and language are distinct modes through which a prior intelligible order can be apprehended and expressed.

An LLM demonstrates that linguistic structure is sufficiently regular to admit mathematical representation. It does not establish that meaning is exhausted by numerical representation.

The project therefore seeks a mathematical representation of semantic and epistemic distinctions without reducing them to simplistic numerical scores.

### 3.3 Why philosophy matters operationally

Philosophy becomes operational only when translated into constraints such as:

- identity conditions;
- lawful predicate roles;
- authority levels;
- valid inference rules;
- contradiction conditions;
- limits of certainty;
- promotion and demotion rules;
- correction and supersession behaviour.

The goal is therefore not to decorate a graph with philosophical terminology. It is to make philosophical distinctions executable.

---

## 4. Problem Statement

The core problem is:

> How can Nephon build a large, persistent, machine-consumable memory without its understanding becoming proportionally noisier as the number of stored records grows?

A conventional graph brain accumulates:

- paraphrase duplicates;
- copied assertions;
- repeated claims from one original source;
- stale operational state;
- context-free contradictions;
- vague edges;
- disconnected conclusions;
- retrieval bundles with no account of why each item matters.

This produces several forms of semantic entropy.

### 4.1 Duplicate inflation

```text
Alistair manages Nephon.
Alistair administers Nephon.
Nephon is managed by Alistair.
Alistair acts as Nephon's steward.
```

A naive graph may store four facts and later treat them as four independent confirmations.

### 4.2 False contradiction

```text
Nephon may deploy in development.
Nephon may not deploy to production without approval.
```

Without context, these can appear contradictory.

### 4.3 Stale belief

```text
node-01 is offline at 10:00
node-01 is online at 10:05
```

The first statement may remain historically valid but should no longer govern current action.

### 4.4 Detached conclusions

A judgement may remain stored after:

- its source is corrected;
- one premise is retracted;
- a rule changes version;
- a policy is superseded.

### 4.5 Confidence collapse

A single confidence number cannot distinguish:

- no evidence;
- weak support;
- strong support;
- strong opposition;
- strong support and strong opposition simultaneously.

---

## 5. Research Hypothesis

The proposed system will control semantic noise by separating five layers.

### 5.1 Expressions

The original natural-language or machine-produced statements.

### 5.2 Canonical propositions

Stable semantic forms such as:

```text
administers(Alistair, Nephon)
```

### 5.3 Contextual claims

An assertion of a proposition within a defined scope, time, authority, perspective, or environment.

### 5.4 Provenance and derivation

A structured account of why the claim is supported.

### 5.5 Epistemic state

The current evaluated status of a proposition in a target context.

The expected result is that raw records may grow rapidly while canonical knowledge grows closer to the number of meaningfully distinct propositions and derivations.

---

## 6. Central Architectural Reframing

### 6.1 Previous mental model

```text
Markdown nodes
+ graph edges
+ edge qualifiers
+ special inference nodes
+ memory nodes
+ contradiction edges
+ retrieval metadata
```

### 6.2 Revised mental model

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

Everything else is a projection.

### 6.3 Consequence

The graph is no longer the knowledge system itself.

It is one machine view of the semantic kernel.

Other views include:

- Markdown;
- PostgreSQL tables;
- prompt context;
- MCP payloads;
- provenance reports;
- GraphBrain visualisation;
- Neo4j projections.

---

## 7. Core Semantic Model

### 7.1 Ontology types

Ontology types define what kinds of entities exist and how they inherit from broader kinds.

Examples:

```text
Thing
Person < Thing
Office < Thing
Agent < Thing
System < Thing
Project < Thing
Proposition < Thing
```

### 7.2 Predicate definitions

Predicates define lawful relations and their named roles.

Example:

```text
occupies_office(
    occupant: Person,
    office: Office
)
```

This is stronger than permitting any node to connect to any other node with a recognised edge label.

### 7.3 Entities

Entities are identified things such as:

- Alistair;
- the Steward office;
- Nephon;
- a Proxmox cluster;
- a project;
- a document;
- an operation.

### 7.4 Expressions

Expressions preserve the exact source language.

Examples:

```text
"Alistair administers Nephon."
"Nephon is administered by Alistair."
```

### 7.5 Propositions

Propositions represent canonical meaning.

```text
administers(
    administrator=Alistair,
    subject=Nephon
)
```

A proposition should possess a stable canonical identity independent of wording and polarity.

### 7.6 Claims

A claim asserts a proposition within a context and attaches provenance, time, lifecycle, trust, and authority.

A claim is not automatically truth.

### 7.7 Contexts

Contexts describe where a claim applies.

Initial dimensions should include:

- project;
- environment;
- operation or scope;
- perspective or speaker;
- authority;
- ontology version;
- valid time.

### 7.8 Provenance expressions

The initial provenance algebra is:

```text
SOURCE(x)
ALL(a, b, ...)
ANY(a, b, ...)
RULE(rule-version, premises...)
```

`ALL` means joint dependency.  
`ANY` means alternative independent derivations.  
`RULE` identifies a transformation.  
`SOURCE` identifies direct evidence or authority.

### 7.9 Inference rules

Inference rules are versioned transformations from premise patterns to conclusion patterns.

Example:

```text
occupies_office(x, Steward)
+
holds_jurisdiction(Steward, Nephon)
→
administers(x, Nephon)
```

### 7.10 Belief states

At minimum:

```text
unknown
supported
rejected
conflicted
currently_unsupported
superseded
```

A conflicted state preserves simultaneous support for a proposition and its negation.

---

## 8. The Three Hard Problems

### 8.1 Canonicalisation

Canonicalisation maps many expressions into a smaller number of stable propositions.

It must distinguish:

- equivalent wording;
- coreference;
- office from office-holder;
- implication from identity;
- closely related but non-equivalent propositions.

Example:

```text
Alistair is Nephon's steward.
Alistair administers Nephon.
```

These may be related by an inference rule but should not necessarily be merged.

The Phase 1 approach is assisted canonicalisation:

1. extract candidate entities and predicate;
2. resolve known identities;
3. validate predicate roles;
4. compare with existing propositions;
5. propose exact, equivalent, implying, implied-by, related, or new;
6. require review where uncertain.

The original expression is never discarded.

### 8.2 Context compatibility

Context compatibility determines whether claims can be compared, combined, or treated as contradictory.

A contradiction exists only when positive and negative claims concern:

- the same canonical proposition;
- compatible contexts;
- compatible times;
- compatible meanings.

Contexts may refine broader contexts.

```text
Nephon
    ↓
Nephon / production
    ↓
Nephon / production / destructive operation
```

A broad rule may apply in a narrower context, while a narrow production rule should not govern development.

Phase 1 implements typed context overlap, refinement, and time-range compatibility. It does not implement a general sheaf engine.

### 8.3 Provenance evaluation

Provenance evaluation determines whether the justification for a claim still holds.

It must handle:

- retracted sources;
- superseded premises;
- expired facts;
- corrected testimony;
- versioned inference rules;
- multiple independent derivations.

Example:

```text
ANY(
    RULE(policy-prohibition, production-policy),
    RULE(constitutional-restraint, AUT-04, PRX-07, irreversible-operation)
)
```

If the production policy is withdrawn, the conclusion may remain supported through the constitutional derivation.

Derived conclusions are not deleted when invalidated. Their historical reasoning remains available.

---

## 9. Mathematical Abstraction

The practical model can later be understood more abstractly.

### 9.1 Typed hypergraph

A proposition is an n-ary relation rather than a simple binary edge.

```text
assertion(
    speaker,
    proposition,
    audience,
    time,
    context,
    source
)
```

### 9.2 Category-theoretic interpretation

Ontology types can be treated as objects and lawful transformations as morphisms.

Composition determines which inference paths are valid.

### 9.3 Indexed knowledge

The deeper model is a context-indexed knowledge structure:

```text
K : Contextᵒᵖ → Category
```

For each context, there is a local body of propositions and proofs. Moving to a narrower context restricts what is applicable.

### 9.4 Proof-relevant semantics

A conclusion is not merely marked true. It has one or more proof objects that witness why it follows.

The proof object is also its provenance.

### 9.5 Sheaf-like coherence

Local rules may be coherent individually but fail to combine globally.

A future sheaf-like layer would identify the precise overlap where no coherent global interpretation exists.

### 9.6 Institutional logic

Theological, moral, authority, technical, operational, and temporal reasoning may require distinct logical systems connected by explicit translations.

Institution theory is a possible future abstraction for this interaction.

### 9.7 Temporal evolution

The knowledge structure evolves through time while preserving historical states.

Prior judgements remain explainable relative to what was known and valid when they were made.

### 9.8 Practical boundary

Phase 1 does not implement the general mathematical framework.

It implements a finite executable approximation designed so that later formalisation remains possible.

---

## 10. Why Practical Validation Comes First

There are three different kinds of proof.

### 10.1 Empirical proof

Does the architecture improve Nephon's behaviour on realistic tasks?

### 10.2 Architectural proof

Does it reduce duplication, preserve corrections, and remain understandable as the knowledge base grows?

### 10.3 Mathematical proof

Are inference, restriction, translation, and coherence formally correct?

The research sequence is:

```text
Conjecture
    ↓
Executable approximation
    ↓
Adversarial practical tests
    ↓
Observed recurring structural failures
    ↓
Targeted mathematical formalisation
    ↓
Proof of important invariants
```

The mathematics should be pulled into the implementation by demonstrated need, not imposed in full before practical usefulness is established.

---

## 11. Phase 1 Objectives

Phase 1 must demonstrate:

1. Duplicate expressions can resolve to one canonical proposition.
2. Independent sources remain distinguishable from copied repetitions.
3. Context prevents false contradiction.
4. Positive and negative support can coexist.
5. Superseded state no longer governs current action.
6. Source correction propagates to dependent conclusions.
7. Alternative derivations can preserve support after one source fails.
8. Retrieval becomes less noisy and more explainable.
9. Constitutional Markdown can compile into the semantic kernel.
10. The system remains small enough to inspect and falsify.

---

## 12. Phase 1 Non-Goals

Phase 1 does not attempt:

- complete automatic semantic understanding;
- unrestricted LLM memory promotion;
- a general theorem prover;
- formal proof of the metaphysical worldview;
- a full sheaf implementation;
- a general category-theory runtime;
- an institution framework;
- complete dependent type theory;
- final production GraphBrain UI;
- production-scale constellation discovery;
- a final solution to ontology evolution.

---

## 13. Proposed System Architecture

### 13.1 Authoring layer

Human-readable Markdown in the existing vault.

The twelve constitutional nodes remain authored and reviewed as a unified worldview.

### 13.2 Compiler layer

A compiler parses:

- proposition IDs;
- claims;
- sources;
- trust and authority;
- dependencies;
- declared relations;
- temporal and lifecycle metadata.

It emits typed semantic records.

### 13.3 Semantic kernel

The kernel contains:

```text
Ontology registry
Predicate registry
Entity repository
Expression repository
Proposition repository
Context engine
Claim repository
Provenance evaluator
Inference engine
Belief evaluator
```

### 13.4 Persistence

PostgreSQL is preferred for canonical persistence because it provides:

- transactional updates;
- constraints;
- recursive queries;
- JSON support;
- mature migration tooling;
- straightforward audit tables.

Neo4j may be used as a projection or exploratory index, not the sole canonical store.

### 13.5 Projection layer

Derived projections include:

- GraphBrain canvas;
- Markdown summaries;
- MCP responses;
- prompt context;
- response provenance reports;
- optional Neo4j graph.

### 13.6 Retrieval layer

Retrieval should produce:

- relevant canonical propositions;
- active claims;
- governing authority;
- compatible contexts;
- current conflicts;
- provenance explanations;
- exclusions and reasons;
- prompt-ready compilation.

---

## 14. Suggested Data Structures

### 14.1 Ontology type

```python
class OntologyType:
    name: str
    parents: set[str]
```

### 14.2 Predicate definition

```python
class PredicateDefinition:
    name: str
    roles: list[RoleDefinition]
```

### 14.3 Proposition

```python
class Proposition:
    predicate: str
    arguments: dict[str, EntityId]
    polarity: positive | negative
```

The canonical atom identity excludes polarity so positive and negative claims share a contradiction set.

### 14.4 Context

```python
class Context:
    project: EntityId | None
    environment: str | None
    operation: str | None
    perspective: EntityId | None
    authority: EntityId | None
    ontology_version: str | None
    valid_from: datetime | None
    valid_until: datetime | None
```

### 14.5 Claim

```python
class Claim:
    proposition: Proposition
    context: Context
    provenance: ProvenanceExpression
    asserted_at: datetime
    valid_from: datetime | None
    valid_until: datetime | None
    trust_level: str
    authority_level: str
    lifecycle: str
```

### 14.6 Provenance expression

```python
SOURCE(reference)
ALL(children...)
ANY(children...)
RULE(rule_id_and_version, premises...)
```

### 14.7 Belief state

```python
class BeliefState:
    proposition_atom: str
    context: Context
    positive_support: list[Derivation]
    negative_support: list[Derivation]
    status: EpistemicStatus
```

---

## 15. Interaction with the Existing Master Plan

### 15.1 Preserved unchanged

- five ontological domains;
- twelve constitutional nodes;
- proposition-level source discipline;
- thin instantiation;
- trust separation;
- theological review;
- lockfile;
- machine validation;
- memory promotion intent;
- MCP boundary;
- GraphBrain visualisation;
- phased execution.

### 15.2 Simplified

The following become derived from the kernel rather than independent special systems:

- edge qualifier interpretation;
- inference-node semantics;
- ordinary contradiction edges;
- memory-node semantics;
- provenance reports;
- retrieval records;
- direct graph relationships.

### 15.3 Reframed

The existing dual edge vocabularies become a typed predicate registry.

Reified inference nodes become proof or provenance objects that can still be projected visually.

Memory becomes a claim role and lifecycle rather than a wholly separate species of data.

Contradictions are normally derived from opposing claims in compatible contexts.

---

## 16. Experimental Design

### 16.1 Baseline

Compare:

```text
A. Existing Markdown plus typed edge traversal
B. Typed claim-kernel retrieval
```

### 16.2 Test cases

#### Duplicate paraphrases

Ten paraphrases from one source should become ten expressions, one proposition, and one source lineage.

#### Independent support

The same proposition from independent sources should retain multiple support paths.

#### Contextual permission

Development permission and production restrictions should not create a false contradiction.

#### Conflicting testimony

Positive and negative support in compatible contexts should produce `conflicted`.

#### Superseded system state

Historical state remains accessible, while present retrieval uses the current state.

#### Corrected authorization

A correction from production authorization to staging authorization should propagate through dependent judgements.

#### Rule version change

Current support should change when a rule changes, while historical reasoning remains available.

### 16.3 Evaluation dimensions

- raw record count;
- canonical proposition count;
- duplicate retrieval count;
- false contradiction count;
- stale conclusion count;
- prompt token usage;
- surviving independent support paths;
- invalidation accuracy;
- explanation quality;
- effect on final agent judgement.

---

## 17. Risks

### 17.1 Premature abstraction

The mathematical framing could produce elegant architecture that does not improve behaviour.

**Mitigation:** require baseline experiments and measurable outcomes.

### 17.2 Canonicalisation error

Incorrectly merging two propositions can destroy important distinctions.

**Mitigation:** preserve expressions, record mapping type, require review where uncertain.

### 17.3 Ontology rigidity

An overly rigid ontology may reject legitimate new concepts.

**Mitigation:** version the ontology and distinguish proposed from active types and predicates.

### 17.4 Context explosion

Too many context dimensions may recreate noise in another form.

**Mitigation:** begin with only demonstrated dimensions and formalise refinement gradually.

### 17.5 Provenance complexity

Full dependency evaluation may become expensive.

**Mitigation:** use versioned DAGs, incremental invalidation, and cached belief states.

### 17.6 Philosophical overclaim

Formal structure may falsely appear to prove metaphysical truth.

**Mitigation:** distinguish constitutional commitments, theological sources, philosophical inference, operational rule, and empirical observation.

### 17.7 LLM authority leakage

An LLM may silently turn uncertain interpretation into active knowledge.

**Mitigation:** LLMs propose; deterministic validation and explicit policy promote.

---

## 18. Open Research Questions

1. What is the minimum canonical proposition language that remains expressive enough for Nephon?
2. Which contexts are fundamental and which should remain ordinary predicates?
3. How should entity identity persist through role, version, and temporal change?
4. When are two propositions equivalent rather than merely mutually implying?
5. How should source independence be represented?
6. Which inference rules should be deterministic, defeasible, probabilistic, or authority-based?
7. How should theological authority interact with empirical system state?
8. When does local inconsistency justify a full sheaf-like formalisation?
9. Which invariants are valuable enough to prove mathematically?
10. Can semantic compression materially reduce prompt cost without destroying nuance?
11. How should corrections alter current belief while preserving moral and historical accountability?
12. Can separate logical domains be connected without flattening them into one undifferentiated rule system?

---

## 19. Decision Gates

### Gate 1: Semantic usefulness

Proceed only if the claim kernel reduces demonstrated noise and improves explanations.

### Gate 2: Architectural viability

Proceed only if correction, provenance, and context remain manageable under growth.

### Gate 3: Mathematical escalation

Formalise a mathematical structure only when repeated implementation failures show that informal rules are insufficient.

Examples:

```text
Recurring context-combination bugs
→ formal context algebra or indexed-category model

Untraceable derived conclusions
→ proof-relevant provenance

Independent domains translating incorrectly
→ institution-style formalisation

Local rules coherent alone but incoherent together
→ sheaf-like obstruction analysis
```

---

## 20. Phase 1 Deliverables

1. Repository-contained proof-of-concept package.
2. Typed semantic models.
3. Constitutional Markdown compiler.
4. In-memory repository and PostgreSQL-ready interface.
5. Canonicalisation proposal workflow.
6. Context compatibility engine.
7. Provenance evaluator.
8. Belief-state evaluator.
9. Basic correction propagation.
10. Retrieval projection.
11. Reproducible experiments.
12. Baseline comparison report.
13. Architecture note mapping the code to the deeper mathematical model.
14. Findings document stating what was validated, falsified, or left unresolved.

---

## 21. Success Criteria

The Phase 1 research hypothesis is supported when the proof of concept demonstrates that:

- ten paraphrases do not become ten independent truths;
- context prevents a real false contradiction;
- corrections invalidate the right conclusions;
- alternative derivations preserve justified belief;
- stale facts stop governing present action;
- conflicts remain explicit;
- retrieval is smaller and more explainable;
- the constitutional worldview can be compiled into machine-enforceable structures;
- the implementation remains inspectable and does not require full pure-mathematics machinery.

The hypothesis is weakened or falsified if the architecture adds substantial complexity without improving these outcomes.

---

## 22. Final Design Principle

The long-term object is not merely a knowledge graph.

It is a computational epistemology whose graph is one representation.

The intended direction can be summarised as:

```text
Constitutional ontology
    defines what kinds of claims and relations are meaningful

Canonical propositions
    prevent linguistic repetition from becoming conceptual inflation

Contexts
    determine where claims apply

Proof-like provenance
    determines why claims are supported

Belief evaluation
    preserves uncertainty, rejection, and conflict

Temporal evolution
    preserves correction, supersession, and historical accountability

Graph, Markdown, MCP, and prompts
    become projections of the same semantic source
```

Phase 1 should prove the practical value of this direction before the project becomes a pure mathematics research programme.
