from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {
    "system-architecture-harness",
    "ai-agent-system-architecture",
    "architecture-review-gate",
}
EXPECTED_AGENTS = {
    "requirements-capacity-analyst.md",
    "domain-data-architect.md",
    "distributed-systems-architect.md",
    "reliability-operations-architect.md",
    "security-privacy-architect.md",
    "ai-agent-architect.md",
    "migration-delivery-architect.md",
    "architecture-critic.md",
    "evidence-verifier.md",
}


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path} must begin with YAML frontmatter")
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        raise AssertionError(f"{path} frontmatter is not closed")
    return yaml.safe_load(parts[1]) or {}, parts[2]


class RepositoryContractTests(unittest.TestCase):
    def test_expected_skills_exist(self) -> None:
        skills_dir = ROOT / "skills"
        found = {p.name for p in skills_dir.iterdir() if p.is_dir()}
        self.assertEqual(EXPECTED_SKILLS, found)
        for name in EXPECTED_SKILLS:
            self.assertTrue((skills_dir / name / "SKILL.md").is_file())

    def test_skill_frontmatter_and_progressive_disclosure(self) -> None:
        for name in EXPECTED_SKILLS:
            skill_dir = ROOT / "skills" / name
            metadata, body = parse_frontmatter(skill_dir / "SKILL.md")
            self.assertEqual(name, metadata.get("name"))
            description = metadata.get("description", "")
            self.assertTrue(description.startswith("Use when"), (name, description))
            self.assertLessEqual(len(description), 1024)
            self.assertEqual("MIT", metadata.get("license"))
            self.assertIsInstance(metadata.get("metadata"), dict)
            self.assertRegex(metadata["metadata"].get("version", ""), r"^\d+\.\d+\.\d+$")
            line_count = len((skill_dir / "SKILL.md").read_text(encoding="utf-8").splitlines())
            self.assertLessEqual(line_count, 500, f"{name} SKILL.md is too long")
            self.assertIn("## Output Contract", body)
            self.assertIn("## Stop Conditions", body)

    def test_all_markdown_links_inside_skills_resolve(self) -> None:
        link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for skill_dir in (ROOT / "skills").iterdir():
            if not skill_dir.is_dir():
                continue
            for path in skill_dir.rglob("*.md"):
                text = path.read_text(encoding="utf-8")
                for target in link_pattern.findall(text):
                    if target.startswith(("http://", "https://", "#", "mailto:")):
                        continue
                    clean = target.split("#", 1)[0]
                    if not clean:
                        continue
                    resolved = (path.parent / clean).resolve()
                    self.assertTrue(resolved.exists(), f"Broken link in {path}: {target}")

    def test_harness_has_governance_and_delegate_budget(self) -> None:
        metadata, body = parse_frontmatter(ROOT / "harness.md")
        delegation = metadata.get("delegation", {})
        self.assertGreaterEqual(delegation.get("max_depth", 0), 1)
        self.assertGreaterEqual(delegation.get("max_concurrent", 0), 2)
        self.assertIn("tools_policy", metadata)
        self.assertIn("Architecture Harness State Machine", body)
        self.assertIn("Evidence before approval", body)
        self.assertIn("Specialist Routing", body)

    def test_native_harness_agents_are_complete(self) -> None:
        agents_dir = ROOT / ".harness" / "agents"
        found = {p.name for p in agents_dir.glob("*.md")}
        self.assertEqual(EXPECTED_AGENTS, found)
        for path in agents_dir.glob("*.md"):
            metadata, body = parse_frontmatter(path)
            self.assertTrue(metadata.get("description"), path)
            self.assertNotIn("name", metadata, f"AI Harness agent names come from filenames: {path}")
            self.assertIn("## Deliverable", body)
            self.assertIn("## Boundaries", body)

    def test_command_guard_is_present(self) -> None:
        path = ROOT / ".harness" / "hooks" / "command-guard.md"
        metadata, body = parse_frontmatter(path)
        self.assertEqual("tool.pre", metadata.get("event"))
        self.assertIn("script", metadata)
        self.assertIn("destructive", body.lower())

    def test_skills_sh_configuration_groups_all_skills(self) -> None:
        config = json.loads((ROOT / "skills.sh.json").read_text(encoding="utf-8"))
        self.assertEqual("https://skills.sh/schemas/skills.sh.schema.json", config.get("$schema"))
        grouped = {
            slug
            for group in config.get("groupings", [])
            for slug in group.get("skills", [])
        }
        self.assertEqual(EXPECTED_SKILLS, grouped)

    def test_repo_entrypoints_and_ci_exist(self) -> None:
        for relative in [
            "README.md",
            "AGENTS.md",
            "CLAUDE.md",
            ".github/copilot-instructions.md",
            ".github/workflows/validate.yml",
            "scripts/doctor.py",
            "LICENSE",
        ]:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_no_placeholders_or_secret_values(self) -> None:
        placeholder_words = ["T" + "BD", "TO" + "DO", "FIX" + "ME", "CHANGE" + "ME"]
        banned = re.compile(r"\b(" + "|".join(placeholder_words) + r")\b|sk-[A-Za-z0-9]{12,}")
        ignored = {
            ROOT / "tests" / "test_repository.py",
            ROOT / "tests" / "baseline-red.txt",
        }
        for path in ROOT.rglob("*"):
            if path in ignored or not path.is_file() or ".zip" in path.suffixes:
                continue
            if path.suffix not in {".md", ".py", ".json", ".yml", ".yaml", ".txt"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            self.assertIsNone(banned.search(text), f"Placeholder or secret-like value in {path}")


if __name__ == "__main__":
    unittest.main()
