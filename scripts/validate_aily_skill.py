#!/usr/bin/env python3
"""Validate that the Aily skill is self-contained and publishable."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "finance-four-flow-audit"
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    skill_md = SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md is missing YAML frontmatter")
    _, frontmatter, _ = text.split("---", 2)
    metadata = yaml.safe_load(frontmatter)
    if metadata.get("name") != "finance-four-flow-audit":
        fail("unexpected skill name")
    if not metadata.get("description"):
        fail("skill description is required")

    markdown_files = [skill_md, *sorted((SKILL / "references").glob("*.md"))]
    missing_links: list[str] = []
    for markdown in markdown_files:
        for link in LINK_RE.findall(markdown.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = (markdown.parent / link.split("#", 1)[0]).resolve()
            if not target.exists():
                missing_links.append(f"{markdown.relative_to(SKILL)} -> {link}")
    if missing_links:
        fail("missing local links:\n" + "\n".join(missing_links))

    coverage = (SKILL / "references" / "rule-coverage.md").read_text(encoding="utf-8")
    missing_rules = [number for number in range(1, 19) if f"| {number} |" not in coverage]
    if missing_rules:
        fail(f"rule coverage is incomplete: {missing_rules}")

    required = [
        SKILL / "agents" / "openai.yaml",
        SKILL / "requirements.txt",
        SKILL / "scripts" / "validate_decision.py",
        SKILL / "scripts" / "receipt_split.py",
        SKILL / "scripts" / "receipt_splitter.py",
        SKILL / "references" / "receipt-split-plan.schema.json",
        SKILL / "references" / "receipt-split-plan.example.json",
    ]
    missing = [str(path.relative_to(SKILL)) for path in required if not path.is_file()]
    if missing:
        fail("missing bundled resources: " + ", ".join(missing))
    print(
        f"OK skill={metadata['name']} references={len(markdown_files) - 1} "
        "rules=18 tools=2"
    )


if __name__ == "__main__":
    main()
