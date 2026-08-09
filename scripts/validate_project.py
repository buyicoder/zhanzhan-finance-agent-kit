#!/usr/bin/env python3
"""Validate the public onboarding package without contacting customer systems."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main() -> None:
    manifest = load_yaml(ROOT / "manifest.yaml")
    entrypoint = ROOT / manifest["entrypoint"]
    if not entrypoint.is_file():
        raise SystemExit(f"missing entrypoint: {entrypoint}")

    schema_path = ROOT / "schemas" / "tenant-config.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)

    split_schema = json.loads(
        (ROOT / "schemas" / "receipt-split-plan.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(split_schema)

    example = load_yaml(ROOT / "examples" / "tenant-config.example.yaml")
    errors = sorted(
        Draft202012Validator(schema).iter_errors(example),
        key=lambda error: list(error.path),
    )
    if errors:
        details = "\n".join(f"- {error.json_path}: {error.message}" for error in errors)
        raise SystemExit(f"invalid tenant example:\n{details}")

    required_paths = [
        ROOT / "onboarding" / "01-capability-audit.md",
        ROOT / "protocols" / "filename-mapping.md",
        ROOT / "protocols" / "controlled-write.md",
        ROOT / "reference-implementation" / "base-manifest.example.yaml",
        ROOT / "reference-implementation" / "schema-snapshot.yaml",
        ROOT / "reference-implementation" / "view-snapshot.yaml",
        ROOT / "skills" / "finance-four-flow-audit" / "SKILL.md",
        ROOT / "skills" / "domain-manuals" / "README.md",
        ROOT / "wiki" / "home-template.md",
        ROOT / "tools" / "receipt_splitter.py",
        ROOT / "scripts" / "receipt_split.py",
        ROOT / "examples" / "receipt-split-plan.example.json",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.is_file()]
    if missing:
        raise SystemExit("missing required files: " + ", ".join(missing))

    print(
        f"OK project={manifest['project']} version={manifest['version']} "
        f"sources={len(example['sources'])}"
    )


if __name__ == "__main__":
    main()
