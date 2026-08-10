#!/usr/bin/env python3
"""CLI for the deterministic Agent-authored receipt split tool."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from receipt_splitter import SplitPlanError, execute_split_plan  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute and verify an Agent-authored receipt split plan")
    parser.add_argument("source", type=Path, help="source receipt-collection PDF")
    parser.add_argument("plan", type=Path, help="JSON split plan authored after visual inspection")
    parser.add_argument("output", type=Path, help="new output directory")
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        result = execute_split_plan(args.source, plan, args.output)
    except (OSError, json.JSONDecodeError, SplitPlanError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
