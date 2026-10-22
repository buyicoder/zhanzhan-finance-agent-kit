#!/usr/bin/env python3
"""Validate that the Aily skill is self-contained and publishable."""

from __future__ import annotations

import re
import sys
import argparse
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", default="finance-four-flow-audit")
    args = parser.parse_args()
    skill = ROOT / "skills" / args.skill
    if not skill.is_dir():
        fail(f"skill directory does not exist: {skill}")

    skill_md = skill / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md is missing YAML frontmatter")
    _, frontmatter, _ = text.split("---", 2)
    metadata = yaml.safe_load(frontmatter)
    if metadata.get("name") != args.skill:
        fail("unexpected skill name")
    if not metadata.get("description"):
        fail("skill description is required")

    markdown_files = [skill_md, *sorted((skill / "references").glob("*.md"))]
    missing_links: list[str] = []
    for markdown in markdown_files:
        for link in LINK_RE.findall(markdown.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = (markdown.parent / link.split("#", 1)[0]).resolve()
            if not target.exists():
                missing_links.append(f"{markdown.relative_to(skill)} -> {link}")
    if missing_links:
        fail("missing local links:\n" + "\n".join(missing_links))

    required = [skill / "agents" / "openai.yaml"]
    if args.skill == "finance-four-flow-audit":
        coverage = (skill / "references" / "rule-coverage.md").read_text(encoding="utf-8")
        missing_rules = [number for number in range(1, 19) if f"| {number} |" not in coverage]
        if missing_rules:
            fail(f"rule coverage is incomplete: {missing_rules}")
        required.extend(
            [
                skill / "requirements.txt",
                skill / "scripts" / "validate_decision.py",
                skill / "scripts" / "receipt_split.py",
                skill / "scripts" / "receipt_splitter.py",
                skill / "references" / "receipt-split-plan.schema.json",
                skill / "references" / "receipt-split-plan.example.json",
            ]
        )
    missing = [str(path.relative_to(skill)) for path in required if not path.is_file()]
    if missing:
        fail("missing bundled resources: " + ", ".join(missing))
    print(
        f"OK skill={metadata['name']} references={len(markdown_files) - 1}"
    )


if __name__ == "__main__":
    main()
