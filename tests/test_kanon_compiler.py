from pathlib import Path
import pytest
from uuid import UUID

from nephon_graph.compiler.markdown_loader import MarkdownLoader
from nephon_graph.compiler.kanon_compiler import (
    KanonCompiler,
    CompilerIntegrityError,
    compute_entity_id,
    compute_declaration_content_hash,
    NEPHON_ENTITY_NAMESPACE,
    NEPHON_COMPILER_NAMESPACE,
)
from nephon_graph.storage.event_store import InMemoryEventStore


def test_markdown_loader_parses_kanon_file(tmp_path: Path):
    md_content = """# 05 AUTHORITY AND OBEDIENCE

## AUT-04

Refusal of illicit commands.

```yaml
propositions:
  - id: "AUT-04"
    claim: "I refuse unapproved or illicit destructive commands in production scope."
    revision: 1
    atom:
      predicate: "requires_approval"
      arguments:
        actor: "nephon"
        action: "destructive_action"
        scope: "production"
    epistemic_mode: "constitutional_judgement"
    authority_level: "constitutional"
    sources:
      - "05_AUTHORITY_AND_OBEDIENCE.md#AUT-04"
```
"""
    f = tmp_path / "05_AUTHORITY_AND_OBEDIENCE.md"
    f.write_text(md_content, encoding="utf-8")

    doc = MarkdownLoader.parse_file(f)
    assert len(doc.propositions) == 1
    p = doc.propositions[0]
    assert p.declaration_id == "AUT-04"
    assert p.revision == 1
    assert p.predicate == "requires_approval"
    assert p.arguments["actor"] == "nephon"
    assert p.authority_level == "constitutional"


def test_compiler_compiles_document_and_registers_claims(tmp_path: Path):
    md_content = """# 08 PRAXIS

## PRX-01

Inspect state before modifying.

```yaml
propositions:
  - id: "PRX-01"
    claim: "I inspect relevant system state before modifying it."
    revision: 1
    atom:
      predicate: "requires_before"
      arguments:
        actor: "nephon"
        prerequisite: "inspect_state"
        action: "modify_system"
    epistemic_mode: "constitutional_judgement"
    authority_level: "constitutional"
    sources:
      - "08_PRAXIS.md#PRX-01"
```
"""
    f = tmp_path / "08_PRAXIS.md"
    f.write_text(md_content, encoding="utf-8")

    store = InMemoryEventStore()
    compiler = KanonCompiler(store)

    doc = MarkdownLoader.parse_file(f)
    result = compiler.compile_document(doc)

    assert "PRX-01" in result.declaration_claim_ids
    claim_id = result.declaration_claim_ids["PRX-01"]
    assert isinstance(claim_id, UUID)

    claim = store.get_claim(claim_id)
    assert claim is not None
    assert store.is_claim_active(claim_id) is True
    assert claim.asserted_by == "kanon_compiler"


def test_compiler_idempotency_same_declaration_returns_noop(tmp_path: Path):
    md_content = """# 08 PRAXIS

## PRX-02

Reversibility requirement.

```yaml
propositions:
  - id: "PRX-02"
    claim: "I prefer reversible actions."
    revision: 1
    atom:
      predicate: "requires_property"
      arguments:
        actor: "nephon"
        property: "reversibility"
        action: "operational_action"
    epistemic_mode: "constitutional_judgement"
    authority_level: "constitutional"
```
"""
    f = tmp_path / "08_PRAXIS.md"
    f.write_text(md_content, encoding="utf-8")

    store = InMemoryEventStore()
    compiler = KanonCompiler(store)

    doc = MarkdownLoader.parse_file(f)
    res1 = compiler.compile_document(doc)

    # Re-compile exact same document
    res2 = compiler.compile_document(doc)

    assert res1.declaration_claim_ids["PRX-02"] == res2.declaration_claim_ids["PRX-02"]
    assert len(res2.events_emitted) == 0  # Idempotent NO-OP


def test_compiler_supersedes_prior_claim_on_new_revision(tmp_path: Path):
    v1_content = """# 05 AUTHORITY AND OBEDIENCE

```yaml
propositions:
  - id: "AUT-04"
    claim: "Initial claim version."
    revision: 1
    atom:
      predicate: "requires_approval"
      arguments:
        actor: "nephon"
        action: "destructive_action"
    epistemic_mode: "constitutional_judgement"
    authority_level: "constitutional"
```
"""
    f1 = tmp_path / "05_AUT.md"
    f1.write_text(v1_content, encoding="utf-8")

    store = InMemoryEventStore()
    compiler = KanonCompiler(store)

    doc1 = MarkdownLoader.parse_file(f1)
    res1 = compiler.compile_document(doc1)
    claim1_id = res1.declaration_claim_ids["AUT-04"]

    assert store.is_claim_active(claim1_id) is True

    # Version 2 with higher revision number
    v2_content = """# 05 AUTHORITY AND OBEDIENCE

```yaml
propositions:
  - id: "AUT-04"
    claim: "Updated claim text with revision 2."
    revision: 2
    atom:
      predicate: "requires_approval"
      arguments:
        actor: "nephon"
        action: "destructive_action"
    epistemic_mode: "constitutional_judgement"
    authority_level: "constitutional"
```
"""
    f2 = tmp_path / "05_AUT.md"
    f2.write_text(v2_content, encoding="utf-8")

    doc2 = MarkdownLoader.parse_file(f2)
    res2 = compiler.compile_document(doc2)
    claim2_id = res2.declaration_claim_ids["AUT-04"]

    assert claim1_id != claim2_id
    assert store.is_claim_active(claim1_id) is False  # Prior claim superseded
    assert store.is_claim_active(claim2_id) is True   # New claim active


def test_compiler_rejects_changed_content_reusing_revision(tmp_path: Path):
    v1_content = """# 05 AUTHORITY

```yaml
propositions:
  - id: "AUT-04"
    claim: "Original text."
    revision: 1
    atom:
      predicate: "requires_approval"
      arguments:
        actor: "nephon"
    epistemic_mode: "constitutional_judgement"
    authority_level: "constitutional"
```
"""
    f = tmp_path / "05_AUT.md"
    f.write_text(v1_content, encoding="utf-8")

    store = InMemoryEventStore()
    compiler = KanonCompiler(store)

    doc1 = MarkdownLoader.parse_file(f)
    compiler.compile_document(doc1)

    # Reusing revision 1 with altered claim text
    v2_content = """# 05 AUTHORITY

```yaml
propositions:
  - id: "AUT-04"
    claim: "Altered text reusing revision 1."
    revision: 1
    atom:
      predicate: "requires_approval"
      arguments:
        actor: "nephon"
    epistemic_mode: "constitutional_judgement"
    authority_level: "constitutional"
```
"""
    f.write_text(v2_content, encoding="utf-8")
    doc2 = MarkdownLoader.parse_file(f)

    with pytest.raises(CompilerIntegrityError, match="revision 1 reused with different content hash"):
        compiler.compile_document(doc2)
