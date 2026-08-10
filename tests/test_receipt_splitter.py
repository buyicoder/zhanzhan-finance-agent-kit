from __future__ import annotations

import hashlib
import json
from pathlib import Path

import fitz
import pytest

from tools.receipt_splitter import SplitPlanError, execute_split_plan


def make_source(path: Path) -> Path:
    document = fitz.open()
    first = document.new_page(width=600, height=800)
    first.insert_text((40, 80), "RECEIPT ONE 100.00")
    first.insert_text((40, 480), "RECEIPT TWO 200.00")
    second = document.new_page(width=600, height=800)
    second.insert_text((40, 80), "RECEIPT TWO APPENDIX")
    document.save(path)
    document.close()
    return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan_for(source: Path) -> dict:
    return {
        "plan_version": "receipt-split-plan/1",
        "parent_object_id": "file-token-1",
        "source_sha256": digest(source),
        "receipts": [
            {
                "receipt_id": "one",
                "filename": "receipt-one",
                "segments": [{"page": 1, "bbox": [0, 0, 1, 0.5]}],
            },
            {
                "receipt_id": "two",
                "filename": "receipt-two",
                "segments": [
                    {"page": 1, "bbox": [0, 0.5, 1, 1]},
                    {"page": 2, "bbox": [0, 0, 1, 1]},
                ],
            },
        ],
    }


def test_executes_same_page_and_cross_page_plan(tmp_path: Path):
    source = make_source(tmp_path / "source.pdf")
    result = execute_split_plan(source, plan_for(source), tmp_path / "out")
    assert result["validated"] is True
    assert result["artifact_count"] == 2
    assert [artifact["page_count"] for artifact in result["artifacts"]] == [1, 2]
    with fitz.open(tmp_path / "out" / "artifacts" / "receipt-two.pdf") as output:
        assert "RECEIPT TWO" in "".join(page.get_text() for page in output)


def test_identical_rerun_reuses_verified_outputs(tmp_path: Path):
    source = make_source(tmp_path / "source.pdf")
    plan = plan_for(source)
    output = tmp_path / "out"
    execute_split_plan(source, plan, output)
    result = execute_split_plan(source, plan, output)
    assert result["idempotent_reuse"] is True


def test_source_hash_mismatch_fails_before_output(tmp_path: Path):
    source = make_source(tmp_path / "source.pdf")
    plan = plan_for(source)
    plan["source_sha256"] = "0" * 64
    with pytest.raises(SplitPlanError, match="source_sha256"):
        execute_split_plan(source, plan, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_invalid_bbox_and_changed_plan_fail_closed(tmp_path: Path):
    source = make_source(tmp_path / "source.pdf")
    plan = plan_for(source)
    output = tmp_path / "out"
    execute_split_plan(source, plan, output)
    changed = json.loads(json.dumps(plan))
    changed["receipts"][0]["segments"][0]["bbox"] = [0, 0, 1, 0.4]
    with pytest.raises(SplitPlanError, match="different split plan"):
        execute_split_plan(source, changed, output)

    invalid = plan_for(source)
    invalid["receipts"][0]["segments"][0]["bbox"] = [0, 0.8, 1, 0.2]
    with pytest.raises(SplitPlanError, match="out of range"):
        execute_split_plan(source, invalid, tmp_path / "invalid")


def test_identity_fields_are_mandatory(tmp_path: Path):
    source = make_source(tmp_path / "source.pdf")
    missing_hash = plan_for(source)
    missing_hash.pop("source_sha256")
    with pytest.raises(SplitPlanError, match="source_sha256 is required"):
        execute_split_plan(source, missing_hash, tmp_path / "missing-hash")

    missing_parent = plan_for(source)
    missing_parent["parent_object_id"] = ""
    with pytest.raises(SplitPlanError, match="parent_object_id is required"):
        execute_split_plan(source, missing_parent, tmp_path / "missing-parent")


def test_idempotent_reuse_verifies_preview_integrity(tmp_path: Path):
    source = make_source(tmp_path / "source.pdf")
    plan = plan_for(source)
    output = tmp_path / "out"
    result = execute_split_plan(source, plan, output)
    preview = output / result["artifacts"][0]["previews"][0]["path"]
    preview.write_bytes(b"tampered")
    with pytest.raises(SplitPlanError, match="preview failed integrity"):
        execute_split_plan(source, plan, output)
