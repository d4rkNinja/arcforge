#!/usr/bin/env python3
"""Create a reproducible ZIP, SHA-256 checksum, and source manifest."""

from __future__ import annotations

import argparse
import hashlib
import os
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {"__pycache__", ".git", ".venv"}
EXCLUDED_NAMES = {"MANIFEST.sha256"}
EXCLUDED_SUFFIXES = {".pyc", ".zip", ".sha256"}


def included_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if path.name in EXCLUDED_NAMES or path.suffix in EXCLUDED_SUFFIXES:
            continue
        files.append(path)
    return sorted(files, key=lambda value: value.as_posix())


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def write_manifest(files: list[Path]) -> Path:
    target = ROOT / "MANIFEST.sha256"
    lines = [f"{digest(path)}  {path.relative_to(ROOT).as_posix()}" for path in files]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def build_zip(target: Path, files: list[Path], manifest: Path) -> None:
    all_files = sorted([*files, manifest], key=lambda value: value.as_posix())
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in all_files:
            relative = Path(ROOT.name) / path.relative_to(ROOT)
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(2026, 8, 13, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if os.access(path, os.X_OK) else 0o644) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT.parent / f"{ROOT.name}.zip",
        help="ZIP output path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    files = included_files()
    manifest = write_manifest(files)
    build_zip(args.output, files, manifest)
    checksum_path = args.output.with_suffix(args.output.suffix + ".sha256")
    checksum_path.write_text(f"{digest(args.output)}  {args.output.name}\n", encoding="utf-8")
    print(f"files={len(files) + 1}")
    print(f"zip={args.output}")
    print(f"sha256={checksum_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
