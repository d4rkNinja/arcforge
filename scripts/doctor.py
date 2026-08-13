#!/usr/bin/env python3
"""Run deterministic health checks for the architecture skills and harness."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "architecture-review-gate" / "scripts" / "score_architecture.py"
GOOD = ROOT / "tests" / "fixtures" / "good-architecture.md"
BAD = ROOT / "tests" / "fixtures" / "bad-architecture.md"


def run(command: list[str], *, expect: int = 0) -> subprocess.CompletedProcess[str]:
    print("$", " ".join(command))
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    if result.returncode != expect:
        raise RuntimeError(
            f"command returned {result.returncode}; expected {expect}: {' '.join(command)}"
        )
    return result


def verify_scanner() -> None:
    good_result = run(
        [sys.executable, str(VALIDATOR), str(GOOD), "--format", "json"],
        expect=0,
    )
    good = json.loads(good_result.stdout)
    if good["verdict"] != "PASS" or good["score"] < 85 or good["critical_findings"]:
        raise RuntimeError("positive architecture fixture did not satisfy the review gate")

    bad_result = run(
        [sys.executable, str(VALIDATOR), str(BAD), "--format", "json"],
        expect=2,
    )
    bad = json.loads(bad_result.stdout)
    if bad["verdict"] != "BLOCK" or bad["score"] >= 60 or len(bad["critical_findings"]) < 5:
        raise RuntimeError("negative architecture fixture was not blocked strongly enough")


def optional_external_checks(use_skills_cli: bool, use_harness_cli: bool) -> None:
    if use_skills_cli:
        if shutil.which("npx") is None:
            raise RuntimeError("npx is not installed")
        run(["npx", "--yes", "skills", "add", ".", "--list"], expect=0)
    else:
        print("SKIP Skills CLI discovery; pass --skills-cli to run it")

    if use_harness_cli:
        if shutil.which("harness") is None:
            raise RuntimeError("AI Harness CLI is not installed")
        run(["harness", "validate"], expect=0)
    else:
        print("SKIP native harness validation; pass --harness-cli to run it")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-cli", action="store_true", help="run Skills CLI discovery")
    parser.add_argument("--harness-cli", action="store_true", help="run native AI Harness validation")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-p",
                "test_*.py",
                "-v",
            ],
            expect=0,
        )
        verify_scanner()
        optional_external_checks(args.skills_cli, args.harness_cli)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"DOCTOR FAILED: {exc}", file=sys.stderr)
        return 1
    print("DOCTOR PASS: repository contracts and deterministic fixtures are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
