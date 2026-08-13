from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EvaluationContractTests(unittest.TestCase):
    def test_behavior_suite_is_well_formed(self) -> None:
        data = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
        self.assertEqual("1.0", data.get("schema_version"))
        cases = data.get("cases", [])
        self.assertGreaterEqual(len(cases), 12)
        identifiers = [case.get("id") for case in cases]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        allowed_skills = {
            "system-architecture-harness",
            "ai-agent-system-architecture",
            "architecture-review-gate",
        }
        for case in cases:
            self.assertIn(case.get("skill"), allowed_skills)
            self.assertTrue(case.get("prompt"))
            self.assertGreaterEqual(len(case.get("expected_behaviors", [])), 1)
            self.assertGreaterEqual(len(case.get("forbidden_behaviors", [])), 1)


if __name__ == "__main__":
    unittest.main()
