from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal, Union
from uuid import UUID
from pydantic import BaseModel, Field


class SourceKind(str, Enum):
    EXPRESSION = "expression"
    DOCUMENT = "document"
    EXTERNAL = "external"


class SourceLeaf(BaseModel):
    node_type: Literal["source"] = "source"
    kind: SourceKind
    ref_id: str


class ClaimLeaf(BaseModel):
    node_type: Literal["claim"] = "claim"
    claim_id: UUID


class AllNode(BaseModel):
    node_type: Literal["all"] = "all"
    children: tuple[ProvenanceNode, ...]


class AnyNode(BaseModel):
    node_type: Literal["any"] = "any"
    children: tuple[ProvenanceNode, ...]


class RuleNode(BaseModel):
    node_type: Literal["rule"] = "rule"
    rule_id: str
    rule_version: str
    premises: tuple[ClaimLeaf, ...]


ProvenanceNode = Annotated[
    Union[SourceLeaf, ClaimLeaf, AllNode, AnyNode, RuleNode],
    Field(discriminator="node_type"),
]

# Update forward refs for recursive types
AllNode.model_rebuild()
AnyNode.model_rebuild()
