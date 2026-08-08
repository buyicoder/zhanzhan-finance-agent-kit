#!/usr/bin/env python3
"""Validate an Agent decision manifest before any production write."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ALLOWED_RELATION_STATUS = {
    "confirmed", "candidate", "rejected", "missing", "insufficient", "not_applicable"
}
ALLOWED_GATE = {"pass", "fail", "unknown", "not_applicable"}
REQUIRED_GATES = {"party", "direction", "project", "time", "amount_pool"}
WEAK_IDENTITY_BASIS = {
    "amount", "file_name", "folder", "path", "keyword", "classification", "model_label"
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    obj = data.get("object") or {}
    require(bool(obj.get("token")), "object.token is required", errors)
    require(bool(re.fullmatch(r"[0-9a-f]{64}", str(obj.get("sha256", "")))),
            "object.sha256 must be 64 lowercase hex characters", errors)
    require(isinstance(data.get("observations"), list), "observations must be a list", errors)
    require(isinstance(data.get("hypotheses"), list), "hypotheses must be a list", errors)
    require(isinstance(data.get("facts"), list), "facts must be a list (zero facts is valid)", errors)
    require(isinstance(data.get("relations"), list), "relations must be a list", errors)
    require(isinstance(data.get("action_plan"), list), "action_plan must be a list", errors)
    require(isinstance(data.get("next_evidence_requests"), list),
            "next_evidence_requests must be a list", errors)
    require(isinstance(data.get("derived_index"), dict), "derived_index must be an object", errors)

    facts = data.get("facts") if isinstance(data.get("facts"), list) else []
    fact_ids: set[str] = set()
    for i, fact in enumerate(facts):
        prefix = f"facts[{i}]"
        fact_id = fact.get("fact_id")
        require(bool(fact_id), f"{prefix}.fact_id is required", errors)
        require(fact_id not in fact_ids, f"{prefix}.fact_id is duplicated", errors)
        if fact_id:
            fact_ids.add(fact_id)
        require(bool(fact.get("fact_type")), f"{prefix}.fact_type is required", errors)
        require(fact.get("identity_status") in {"resolved", "unresolved"},
                f"{prefix}.identity_status must be resolved or unresolved", errors)
        basis = fact.get("identity_basis")
        require(isinstance(basis, list) and bool(basis),
                f"{prefix}.identity_basis must be a non-empty list", errors)
        if fact.get("identity_status") == "resolved" and isinstance(basis, list):
            require(bool(set(basis) - WEAK_IDENTITY_BASIS),
                    f"{prefix} cannot be resolved from weak identity keys only", errors)
        fields = fact.get("fields")
        require(isinstance(fields, dict), f"{prefix}.fields must be an object", errors)
        if isinstance(fields, dict):
            for name, field in fields.items():
                require(isinstance(field, dict), f"{prefix}.fields.{name} must be an object", errors)
                if not isinstance(field, dict):
                    continue
                require(bool(field.get("source_token")),
                        f"{prefix}.fields.{name}.source_token is required", errors)
                require(field.get("mode") in {"visual", "text", "ocr", "structured"},
                        f"{prefix}.fields.{name}.mode is invalid", errors)
                require(field.get("confidence") in {"high", "medium", "low"},
                        f"{prefix}.fields.{name}.confidence is invalid", errors)

    relations = data.get("relations") if isinstance(data.get("relations"), list) else []
    for i, relation in enumerate(relations):
        prefix = f"relations[{i}]"
        status = relation.get("status")
        require(status in ALLOWED_RELATION_STATUS, f"{prefix}.status is invalid", errors)
        gates = relation.get("hard_gates")
        require(isinstance(gates, dict), f"{prefix}.hard_gates must be an object", errors)
        if isinstance(gates, dict):
            require(REQUIRED_GATES <= set(gates), f"{prefix}.hard_gates is incomplete", errors)
            for gate, result in gates.items():
                require(result in ALLOWED_GATE, f"{prefix}.hard_gates.{gate} is invalid", errors)
            if status == "confirmed":
                require(all(gates.get(g) in {"pass", "not_applicable"} for g in REQUIRED_GATES),
                        f"{prefix} cannot be confirmed with failed or unknown hard gates", errors)
        require(bool(relation.get("reason")), f"{prefix}.reason is required", errors)
        require(isinstance(relation.get("counterevidence"), list),
                f"{prefix}.counterevidence must be a list", errors)

    actions = data.get("action_plan") if isinstance(data.get("action_plan"), list) else []
    for i, action in enumerate(actions):
        refs = action.get("fact_ids")
        require(isinstance(refs, list) and bool(refs),
                f"action_plan[{i}].fact_ids must be a non-empty list", errors)
        if isinstance(refs, list):
            missing = sorted(set(refs) - fact_ids)
            require(not missing, f"action_plan[{i}] references undeclared facts: {missing}", errors)
        require(bool(action.get("target_table")), f"action_plan[{i}].target_table is required", errors)
        require(action.get("action") in {"upsert", "link", "update", "none"},
                f"action_plan[{i}].action is invalid", errors)

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_decision.py DECISION.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
