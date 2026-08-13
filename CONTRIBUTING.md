# Contributing

## Change process

1. Open an issue or change description identifying the observed activation failure, missing architecture case, or standards update.
2. Add a failing repository test or behavioral case under `tests/` or `evals/` before changing behavior.
3. Make the smallest focused change to a skill, reference, asset, optional helper, validator, or documentation.
4. Run `python scripts/doctor.py`; when network access is available, also run `python scripts/doctor.py --skills-cli`.
5. Describe evidence, compatibility impact, and any agent-specific checks that were not executed.

## Skill requirements

- Directory and frontmatter `name` match.
- `description` begins with `Use when` and contains concrete activation signals.
- Primary frontmatter stays portable: use only `name` and `description`.
- Each skill includes `agents/openai.yaml` with valid Codex display metadata; keep it optional to other runtimes.
- Keep the repository-level MIT license and `VERSION` as the source of legal and release metadata.
- Primary `SKILL.md` remains at 500 lines or fewer.
- Local links resolve from the file that contains them.
- Long reference files include a contents section and every bundled resource is named from `SKILL.md`.
- Deep reference material remains one link away from the primary skill when practical.
- Optional helpers document their dependencies and fail with useful messages.

## Portable runtime requirements

- Do not depend on `harness.md`, `.harness/`, a native harness CLI, or one vendor's configuration for core activation.
- Keep shared frontmatter valid for the Agent Skills specification.
- If a runtime-specific enhancement is useful, isolate it as optional metadata or documentation and preserve the basic skill path.

## Review standard

A contribution is not complete merely because tests pass. Review activation paths, frontmatter, compatibility, documentation, critical architecture blockers, and whether the new test can detect the intended failure.
