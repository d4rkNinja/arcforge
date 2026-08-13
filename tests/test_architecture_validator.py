from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills" / "architecture-review-gate" / "scripts" / "score_architecture.py"


class ArchitectureValidatorTests(unittest.TestCase):
    def test_good_fixture_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(ROOT / "tests/fixtures/good-architecture.md"), "--format", "json"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        report = json.loads(result.stdout)
        self.assertGreaterEqual(report["score"], 85)
        self.assertEqual("PASS", report["verdict"])
        self.assertEqual([], report["critical_findings"])

    def test_bad_fixture_is_blocked(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(ROOT / "tests/fixtures/bad-architecture.md"), "--format", "json"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(0, result.returncode)
        report = json.loads(result.stdout)
        self.assertLess(report["score"], 60)
        self.assertEqual("BLOCK", report["verdict"])
        self.assertGreaterEqual(len(report["critical_findings"]), 5)


if __name__ == "__main__":
    unittest.main()
