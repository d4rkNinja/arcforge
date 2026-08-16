#!/usr/bin/env python3
"""Validate the backend engineering knowledge-base corpus without third-party dependencies."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
CANONICAL = ROOT / "original" / "Pasted text.txt"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def parse_canonical(text: str):
    matches = list(re.finditer(r"^# (\d+)\. (.+?)\s*$", text, re.M))
    topics = []
    for i, match in enumerate(matches):
        n = int(match.group(1))
        end = matches[i + 1].start() if i + 1 < len(matches) else text.find(
            "## The important structural change", match.end()
        )
        if end < 0:
            end = len(text)
        segment = text[match.end():end]
        subtopics = [
            line.strip()[2:].strip()
            for line in segment.splitlines()
            if line.strip().startswith("* ")
        ]
        topics.append({"number": n, "title": match.group(2).strip(), "subtopics": subtopics})
    return topics

def fail(message: str, errors: list[str]) -> None:
    errors.append(message)

def main() -> int:
    errors: list[str] = []
    if not MANIFEST.exists():
        print("manifest.json is missing", file=sys.stderr)
        return 1
    if not CANONICAL.exists():
        print("canonical source is missing", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    canonical = parse_canonical(CANONICAL.read_text(encoding="utf-8"))
    papers = manifest.get("papers", [])
    sources = {s["id"] for s in manifest.get("sources", [])}
    numbers = {p["number"] for p in papers}

    if len(canonical) != 146:
        fail(f"canonical topic count is {len(canonical)}, expected 146", errors)
    if [t["number"] for t in canonical] != list(range(1, 147)):
        fail("canonical topic numbers are not exactly 1..146", errors)
    if len(papers) != 146:
        fail(f"manifest paper count is {len(papers)}, expected 146", errors)
    if numbers != set(range(1, 147)):
        fail("manifest paper numbers are not exactly 1..146", errors)

    canonical_by_num = {t["number"]: t for t in canonical}
    paper_paths = []
    total_words = 0

    for paper in papers:
        n = paper["number"]
        expected = canonical_by_num.get(n)
        if not expected:
            fail(f"paper {n}: missing canonical topic", errors)
            continue
        if paper["title"] != expected["title"]:
            fail(f"paper {n}: title mismatch", errors)
        if paper["subtopics"] != expected["subtopics"]:
            fail(f"paper {n}: canonical subtopic list mismatch", errors)
        path = ROOT / paper["path"]
        paper_paths.append(path)
        if not path.exists():
            fail(f"paper {n}: file missing: {paper['path']}", errors)
            continue
        if path.stat().st_size == 0:
            fail(f"paper {n}: file is empty", errors)
            continue
        content = path.read_text(encoding="utf-8")
        digest = sha256(path)
        if digest != paper["sha256"]:
            fail(f"paper {n}: SHA-256 mismatch", errors)
        words = len(content.split())
        total_words += words
        if words != paper["word_count"]:
            fail(f"paper {n}: word_count mismatch ({words} != {paper['word_count']})", errors)
        expected_header = f"# {n:03d}. {expected['title']}"
        if expected_header not in content:
            fail(f"paper {n}: main heading missing", errors)
        for idx, subtopic in enumerate(expected["subtopics"], start=1):
            heading = f"### 7.{idx}. {subtopic}"
            if heading not in content:
                fail(f"paper {n}: subtopic section missing: {subtopic}", errors)
        for rel in paper.get("relationships", []):
            if rel not in numbers:
                fail(f"paper {n}: unknown relationship target {rel}", errors)
        for sid in paper.get("source_ids", []):
            if sid not in sources:
                fail(f"paper {n}: unknown source id {sid}", errors)
            if f"**[{sid}]" not in content:
                fail(f"paper {n}: bibliography entry missing for {sid}", errors)
        for marker in ("### MUST", "### SHOULD", "### MAY", "### AVOID", "### NEVER"):
            if marker not in content:
                fail(f"paper {n}: normative section missing {marker}", errors)

    actual_papers = sorted((ROOT / "papers").rglob("*.md"))
    if len(actual_papers) != 146:
        fail(f"filesystem contains {len(actual_papers)} paper Markdown files, expected 146", errors)
    if set(actual_papers) != set(paper_paths):
        fail("filesystem paper paths and manifest paper paths differ", errors)

    declared_words = manifest.get("corpus", {}).get("paper_word_count")
    if declared_words != total_words:
        fail(f"corpus paper_word_count mismatch ({total_words} != {declared_words})", errors)

    required_root = [
        "README.md", "ONTOLOGY.md", "RESEARCH-METHOD.md", "SOURCES.md",
        "manifest.json", "knowledge-graph.json", "original/Pasted text.txt"
    ]
    for rel in required_root:
        if not (ROOT / rel).exists():
            fail(f"required file missing: {rel}", errors)

    if errors:
        print(f"FAILED: {len(errors)} validation error(s)", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"OK: 146 papers, {sum(len(t['subtopics']) for t in canonical)} canonical subtopics, "
        f"{total_words:,} paper words, all hashes/links/source IDs validated."
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
