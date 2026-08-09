"""Execute an Agent-authored bank-receipt split plan, then verify artifacts.

The Agent owns semantic boundary decisions. This module only validates a
normalized plan, crops/assembles PDF pages, renders previews, and emits an
idempotent evidence manifest.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

import fitz


TOOL_VERSION = "zhanzhan-receipt-split/1"
SAFE_NAME = re.compile(r"[^A-Za-z0-9._\-\u4e00-\u9fff]+")


class SplitPlanError(ValueError):
    """The Agent-authored plan is invalid or cannot be executed safely."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _safe_filename(value: str, fallback: str) -> str:
    name = SAFE_NAME.sub("_", value.strip()).strip("._") or fallback
    return name[:160]


def _normalize_plan(plan: dict[str, Any], page_count: int) -> dict[str, Any]:
    if not isinstance(plan, dict) or not isinstance(plan.get("receipts"), list):
        raise SplitPlanError("plan.receipts must be an array")
    if not plan["receipts"]:
        raise SplitPlanError("plan must contain at least one receipt")

    normalized_receipts: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for receipt_index, receipt in enumerate(plan["receipts"], 1):
        if not isinstance(receipt, dict):
            raise SplitPlanError(f"receipt {receipt_index} must be an object")
        receipt_id = str(receipt.get("receipt_id", "")).strip()
        if not receipt_id or receipt_id in seen_ids:
            raise SplitPlanError(f"receipt {receipt_index} has a missing or duplicate receipt_id")
        seen_ids.add(receipt_id)
        filename = _safe_filename(str(receipt.get("filename", "")), f"receipt-{receipt_index:03d}")
        if filename in seen_names:
            raise SplitPlanError(f"duplicate output filename: {filename}")
        seen_names.add(filename)
        segments = receipt.get("segments")
        if not isinstance(segments, list) or not segments:
            raise SplitPlanError(f"receipt {receipt_id} must contain segments")

        normalized_segments: list[dict[str, Any]] = []
        for segment_index, segment in enumerate(segments, 1):
            if not isinstance(segment, dict):
                raise SplitPlanError(f"receipt {receipt_id} segment {segment_index} is invalid")
            page = segment.get("page")
            if not isinstance(page, int) or isinstance(page, bool) or not 1 <= page <= page_count:
                raise SplitPlanError(f"receipt {receipt_id} references invalid page {page}")
            bbox = segment.get("bbox", [0.0, 0.0, 1.0, 1.0])
            if (
                not isinstance(bbox, list)
                or len(bbox) != 4
                or any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in bbox)
            ):
                raise SplitPlanError(f"receipt {receipt_id} segment {segment_index} has invalid bbox")
            x0, y0, x1, y1 = (float(value) for value in bbox)
            if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
                raise SplitPlanError(f"receipt {receipt_id} segment {segment_index} bbox is out of range")
            normalized_segments.append({"page": page, "bbox": [x0, y0, x1, y1]})
        normalized_receipts.append(
            {"receipt_id": receipt_id, "filename": filename, "segments": normalized_segments}
        )

    return {
        "plan_version": str(plan.get("plan_version", "receipt-split-plan/1")),
        "parent_object_id": str(plan.get("parent_object_id", "")).strip(),
        "receipts": normalized_receipts,
    }


def _clip(page: fitz.Page, bbox: list[float]) -> fitz.Rect:
    x0, y0, x1, y1 = bbox
    bounds = page.rect
    return fitz.Rect(
        bounds.x0 + x0 * bounds.width,
        bounds.y0 + y0 * bounds.height,
        bounds.x0 + x1 * bounds.width,
        bounds.y0 + y1 * bounds.height,
    )


def _write_receipt(source: fitz.Document, receipt: dict[str, Any], pdf_path: Path) -> None:
    output = fitz.open()
    try:
        for segment in receipt["segments"]:
            source_page = source[segment["page"] - 1]
            clip = _clip(source_page, segment["bbox"])
            target = output.new_page(width=clip.width, height=clip.height)
            target.show_pdf_page(target.rect, source, source_page.number, clip=clip)
        output.save(pdf_path, garbage=4, deflate=True)
    finally:
        output.close()


def _validate_and_render(pdf_path: Path, preview_dir: Path) -> tuple[list[dict[str, Any]], int]:
    previews: list[dict[str, Any]] = []
    with fitz.open(pdf_path) as document:
        if document.page_count == 0:
            raise SplitPlanError(f"empty output PDF: {pdf_path.name}")
        for index, page in enumerate(document):
            pixmap = page.get_pixmap(matrix=fitz.Matrix(144 / 72, 144 / 72), alpha=False)
            if pixmap.width < 20 or pixmap.height < 20:
                raise SplitPlanError(f"invalid output dimensions: {pdf_path.name} page {index + 1}")
            samples = bytes(pixmap.samples)
            if samples and min(samples) >= 250:
                raise SplitPlanError(f"blank output render: {pdf_path.name} page {index + 1}")
            preview_path = preview_dir / f"{pdf_path.stem}-p{index + 1:03d}.png"
            pixmap.save(preview_path)
            previews.append(
                {
                    "page": index + 1,
                    "path": str(preview_path.relative_to(preview_dir.parent)),
                    "sha256": sha256_file(preview_path),
                    "width": pixmap.width,
                    "height": pixmap.height,
                }
            )
        return previews, document.page_count


def execute_split_plan(source: Path | str, plan: dict[str, Any], output_dir: Path | str) -> dict[str, Any]:
    source = Path(source).resolve()
    output_dir = Path(output_dir).resolve()
    if not source.is_file() or source.suffix.lower() != ".pdf":
        raise SplitPlanError("source must be an existing PDF")
    if source == output_dir or source in output_dir.parents:
        raise SplitPlanError("output directory cannot contain the source")

    source_sha256 = sha256_file(source)
    with fitz.open(source) as document:
        if document.page_count == 0:
            raise SplitPlanError("source PDF has no pages")
        normalized = _normalize_plan(plan, document.page_count)
        expected_sha = str(plan.get("source_sha256", "")).lower().strip()
        if expected_sha and expected_sha != source_sha256:
            raise SplitPlanError("source_sha256 does not match the source PDF")
        plan_hash = stable_digest(normalized)
        idempotency_key = stable_digest(
            {"tool_version": TOOL_VERSION, "source_sha256": source_sha256, "plan_hash": plan_hash}
        )

        manifest_path = output_dir / "receipt-split-manifest.json"
        if manifest_path.is_file():
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
            if existing.get("idempotency_key") != idempotency_key:
                raise SplitPlanError("output directory belongs to a different split plan")
            for artifact in existing.get("artifacts", []):
                path = output_dir / artifact["pdf_path"]
                if not path.is_file() or sha256_file(path) != artifact["pdf_sha256"]:
                    raise SplitPlanError("existing idempotent output failed integrity verification")
            return {**existing, "idempotent_reuse": True}
        if output_dir.exists():
            raise SplitPlanError("refusing to replace a non-empty or unverified output directory")

        output_dir.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}-", dir=output_dir.parent))
        artifacts_dir = staging / "artifacts"
        previews_dir = staging / "previews"
        artifacts_dir.mkdir()
        previews_dir.mkdir()
        artifacts: list[dict[str, Any]] = []
        try:
            for receipt in normalized["receipts"]:
                pdf_path = artifacts_dir / f"{receipt['filename']}.pdf"
                _write_receipt(document, receipt, pdf_path)
                previews, page_count = _validate_and_render(pdf_path, previews_dir)
                artifacts.append(
                    {
                        "receipt_id": receipt["receipt_id"],
                        "pdf_path": str(pdf_path.relative_to(staging)),
                        "pdf_sha256": sha256_file(pdf_path),
                        "page_count": page_count,
                        "segments": receipt["segments"],
                        "previews": previews,
                    }
                )
            manifest = {
                "tool_version": TOOL_VERSION,
                "source_path": source.name,
                "source_sha256": source_sha256,
                "parent_object_id": normalized["parent_object_id"],
                "plan_hash": plan_hash,
                "idempotency_key": idempotency_key,
                "artifact_count": len(artifacts),
                "artifacts": artifacts,
                "validated": True,
                "production_write_authorized": False,
                "idempotent_reuse": False,
            }
            (staging / manifest_path.name).write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
            )
            os.replace(staging, output_dir)
            return manifest
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise
