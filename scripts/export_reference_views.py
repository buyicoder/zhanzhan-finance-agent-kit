#!/usr/bin/env python3
"""Export tenant-free view behavior from a Feishu Base via lark-cli."""

from __future__ import annotations

import argparse
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml


def call(base_token: str, command: str, table_id: str, view_id: str | None = None):
    args = [
        "lark-cli",
        "base",
        command,
        "--base-token",
        base_token,
        "--table-id",
        table_id,
        "--as",
        "user",
        "--format",
        "json",
    ]
    if view_id:
        args.extend(["--view-id", view_id])
    completed = subprocess.run(args, check=True, capture_output=True, text=True)
    payload = json.loads(completed.stdout)
    if not payload.get("ok"):
        raise RuntimeError(payload)
    return payload.get("data", {})


def export_view(base_token: str, table_id: str, view: dict):
    view_id = view["id"]
    commands = {
        "filter": "+view-get-filter",
        "sort": "+view-get-sort",
        "group": "+view-get-group",
        "visible_fields": "+view-get-visible-fields",
    }
    result = {"name": view["name"], "type": view["type"]}
    for key, command in commands.items():
        try:
            result[key] = call(base_token, command, table_id, view_id).get(key)
        except (subprocess.CalledProcessError, RuntimeError, json.JSONDecodeError) as exc:
            result[key] = {"status": "unknown", "reason": type(exc).__name__}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-token", required=True)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    table_views = []
    completed_names = set()
    if args.output.exists():
        existing = yaml.safe_load(args.output.read_text(encoding="utf-8")) or {}
        table_views = existing.get("tables", [])
        completed_names = {table["table"] for table in table_views}
    for table in schema.get("tables", []):
        if table["table_name"] in completed_names:
            continue
        table_id = table["table_id"]
        listed = call(args.base_token, "+view-list", table_id).get("views", [])
        with ThreadPoolExecutor(max_workers=1) as executor:
            views = list(
                executor.map(
                    lambda view: export_view(args.base_token, table_id, view), listed
                )
            )
        table_views.append({"table": table["table_name"], "views": views})
        print(f"exported table={table['table_name']} views={len(views)}", flush=True)
        partial = {
            "name": "占占四流一致索引中心（AI直做）",
            "snapshot_kind": "sanitized-view-reference",
            "tables": table_views,
        }
        temporary = args.output.with_suffix(args.output.suffix + ".tmp")
        temporary.write_text(
            yaml.safe_dump(partial, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        temporary.replace(args.output)

    output = {
        "name": "占占四流一致索引中心（AI直做）",
        "snapshot_kind": "sanitized-view-reference",
        "tables": table_views,
    }
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(
        yaml.safe_dump(output, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    temporary.replace(args.output)
    count = sum(len(table["views"]) for table in table_views)
    print(f"exported {count} views to {args.output}")


if __name__ == "__main__":
    main()
