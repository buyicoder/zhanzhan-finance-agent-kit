#!/usr/bin/env python3
"""Build a deterministic zip containing only the publishable Aily skill."""

from __future__ import annotations

import hashlib
import json
import zipfile
import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", default="finance-four-flow-audit")
    args = parser.parse_args()
    skill = ROOT / "skills" / args.skill
    if not skill.is_dir():
        raise SystemExit(f"skill directory does not exist: {skill}")
    archive = DIST / f"{args.skill}.aily-skill.zip"

    DIST.mkdir(exist_ok=True)
    files = sorted(
        path
        for path in skill.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            info = zipfile.ZipInfo(str(Path(skill.name) / path.relative_to(skill)))
            info.date_time = (2026, 1, 1, 0, 0, 0)
            info.external_attr = (0o755 if path.suffix == ".py" else 0o644) << 16
            bundle.writestr(info, path.read_bytes())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    manifest = {
        "archive": archive.name,
        "sha256": digest,
        "files": len(files),
        "entrypoint": f"{args.skill}/SKILL.md",
    }
    (DIST / f"{args.skill}.aily-skill.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
