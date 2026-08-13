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
            self.assertEqual({"name", "description"}, set(metadata), name)
            self.assertEqual(name, metadata.get("name"))
            self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            description = metadata.get("description", "")
            self.assertTrue(description.startswith("Use when"), (name, description))
            self.assertLessEqual(len(description), 1024)
            line_count = len((skill_dir / "SKILL.md").read_text(encoding="utf-8").splitlines())
            self.assertLessEqual(line_count, 500, f"{name} SKILL.md is too long")
            self.assertIn("## Output Contract", body)
            self.assertIn("## Stop Conditions", body)

    def test_codex_interface_metadata_is_present_and_valid(self) -> None:
        for name in EXPECTED_SKILLS:
            metadata_path = ROOT / "skills" / name / "agents" / "openai.yaml"
            self.assertTrue(metadata_path.is_file(), name)
            metadata = yaml.safe_load(metadata_path.read_text(encoding="utf-8")) or {}
            self.assertEqual({"interface"}, set(metadata), name)
            interface = metadata["interface"]
            self.assertEqual(
                {"display_name", "short_description", "default_prompt"},
                set(interface),
                name,
            )
            self.assertTrue(interface["display_name"].strip(), name)
            self.assertGreaterEqual(len(interface["short_description"]), 25, name)
            self.assertLessEqual(len(interface["short_description"]), 64, name)
            self.assertIn(f"${name}", interface["default_prompt"], name)

    def test_all_bundled_resources_are_named_by_the_skill(self) -> None:
        resource_dirs = {"assets", "examples", "references", "scripts"}
        for skill_dir in (ROOT / "skills").iterdir():
            if not skill_dir.is_dir():
                continue
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            for resource in skill_dir.rglob("*"):
                if not resource.is_file() or resource.parent.name not in resource_dirs:
                    continue
                relative = resource.relative_to(skill_dir).as_posix()
                self.assertIn(relative, skill_text, f"Unlisted skill resource: {relative}")

    def test_skill_path_references_resolve(self) -> None:
        path_pattern = re.compile(
            r"(?:assets|examples|references|scripts|tests)/[A-Za-z0-9_.-]+"
            r"(?:/[A-Za-z0-9_.-]+)*"
        )
        for skill_dir in (ROOT / "skills").iterdir():
            if not skill_dir.is_dir():
                continue
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            for target in sorted(set(path_pattern.findall(skill_text))):
                resolved = skill_dir / Path(target)
                self.assertTrue(resolved.is_file(), f"Broken skill path: {target}")

    def test_long_references_have_a_contents_section(self) -> None:
        for reference in (ROOT / "skills").glob("*/references/*.md"):
            if len(reference.read_text(encoding="utf-8").splitlines()) <= 100:
                continue
            self.assertIn("## Contents", reference.read_text(encoding="utf-8"), reference)

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

    def test_native_harness_artifacts_are_absent(self) -> None:
        self.assertFalse((ROOT / "harness.md").exists())
        self.assertFalse((ROOT / ".harness").exists())

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
            "skills.sh.json",
            "LICENSE",
        ]:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_no_placeholders_or_secret_values(self) -> None:
        placeholder_words = ["T" + "BD", "TO" + "DO", "FIX" + "ME", "CHANGE" + "ME"]
        banned = re.compile(r"\b(" + "|".join(placeholder_words) + r")\b|sk-[A-Za-z0-9]{12,}")
        ignored = {
            ROOT / "tests" / "test_repository.py",
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
