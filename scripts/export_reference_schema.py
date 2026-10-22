#!/usr/bin/env python3
"""Export a tenant-free semantic schema from an EDI/Base schema snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


SENSITIVE_KEYS = {
    "base_token",
    "table_id",
    "id",
    "bidirectional_link_field_id",
    "link_table",
}


def sanitize(value):
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {}
    for key, item in value.items():
        if key in SENSITIVE_KEYS:
            continue
        if key == "options":
            result[key] = [
                {"name": option.get("name", "")}
                for option in item
                if option.get("name")
            ]
            continue
        result[key] = sanitize(item)
    return result


def normalize(snapshot):
    tables = []
    id_to_name = {
        table.get("table_id"): table.get("table_name")
        for table in snapshot.get("tables", [])
    }
    for table in snapshot.get("tables", []):
        fields = []
        for field in table.get("fields", []):
            clean = sanitize(field)
            link_table = field.get("link_table")
            if link_table:
                clean["link_table_name"] = id_to_name.get(link_table, "unknown")
            fields.append(clean)
        tables.append(
            {
                "name": table.get("table_name"),
                "field_count": len(fields),
                "fields": fields,
            }
        )
    return {
        "name": "占占四流一致索引中心（AI直做）",
        "snapshot_kind": "sanitized-semantic-reference",
        "source_fetched_at": snapshot.get("fetched_at"),
        "table_count": len(tables),
        "tables": tables,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    snapshot = json.loads(args.source.read_text(encoding="utf-8"))
    exported = normalize(snapshot)
    args.output.write_text(
        yaml.safe_dump(exported, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print(f"exported {exported['table_count']} tables to {args.output}")


if __name__ == "__main__":
    main()

