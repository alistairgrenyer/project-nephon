from __future__ import annotations

from pydantic import BaseModel, Field


class InferenceRule(BaseModel):
    """
    Versioned transformation rule from premise proposition patterns to conclusion proposition pattern.
    """
    rule_id: str
    version: str
    description: str = ""
    premise_predicates: list[str] = Field(default_factory=list)
    conclusion_predicate: str
