from __future__ import annotations

import re
from pathlib import Path
from typing import Any
import yaml
from pydantic import BaseModel, Field


class ParsedPropositionBlock(BaseModel):
    declaration_id: str
    claim_text: str
    revision: int = 1
    predicate: str
    arguments: dict[str, Any]
    epistemic_mode: str
    authority_level: str
    sources: list[str] = Field(default_factory=list)
    raw_dict: dict[str, Any]


class ParsedMarkdownDocument(BaseModel):
    file_path: str
    document_version: str = "1.0"
    propositions: list[ParsedPropositionBlock] = Field(default_factory=list)


class MarkdownLoader:
    """
    Parses authored Kanon Markdown files containing YAML proposition declaration blocks.
    """

    @classmethod
    def parse_file(cls, file_path: str | Path) -> ParsedMarkdownDocument:
        path = Path(file_path)
        content = path.read_text(encoding="utf-8")

        # Find all ```yaml ... ``` blocks
        pattern = re.compile(r"```yaml\s*\n(.*?)\n```", re.DOTALL)
        matches = pattern.findall(content)

        blocks: list[ParsedPropositionBlock] = []

        for match in matches:
            parsed = yaml.safe_load(match)
            if not isinstance(parsed, dict) or "propositions" not in parsed:
                continue

            for prop in parsed["propositions"]:
                p_id = prop["id"]
                claim_text = prop["claim"]
                rev = prop.get("revision", 1)
                atom_spec = prop["atom"]
                predicate = atom_spec["predicate"]
                args = atom_spec.get("arguments", {})
                e_mode = prop.get("epistemic_mode", "constitutional_judgement")
                auth_level = prop.get("authority_level", "constitutional")
                sources = prop.get("sources", [])

                blocks.append(
                    ParsedPropositionBlock(
                        declaration_id=p_id,
                        claim_text=claim_text,
                        revision=rev,
                        predicate=predicate,
                        arguments=args,
                        epistemic_mode=e_mode,
                        authority_level=auth_level,
                        sources=sources,
                        raw_dict=prop,
                    )
                )

        return ParsedMarkdownDocument(file_path=str(path), propositions=blocks)
