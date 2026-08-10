#!/usr/bin/env python3
"""Build a deterministic zip containing only the publishable Aily skill."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "finance-four-flow-audit"
DIST = ROOT / "dist"
ARCHIVE = DIST / "finance-four-flow-audit.aily-skill.zip"


def main() -> None:
    DIST.mkdir(exist_ok=True)
    files = sorted(
        path
        for path in SKILL.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            info = zipfile.ZipInfo(str(Path(SKILL.name) / path.relative_to(SKILL)))
            info.date_time = (2026, 1, 1, 0, 0, 0)
            info.external_attr = (0o755 if path.suffix == ".py" else 0o644) << 16
            bundle.writestr(info, path.read_bytes())
    digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    manifest = {
        "archive": ARCHIVE.name,
        "sha256": digest,
        "files": len(files),
        "entrypoint": "finance-four-flow-audit/SKILL.md",
    }
    (DIST / "finance-four-flow-audit.aily-skill.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
