# Contributing

## Change process

1. Open an issue or change description identifying the observed activation failure, missing architecture case, or standards update.
2. Add or update a behavioral case under `evals/` before changing skill behavior.
3. Run the affected case with an approved target model and retain the complete baseline and skill-assisted outputs.
4. Make the smallest focused change to a skill, reference, example, asset, or documentation.
5. Re-run the affected model cases and compare activation, blocker recall, evidence discipline, and output completeness.
6. Verify frontmatter, required headings, line limits, local links, and Skills CLI discovery.
7. Describe evidence, model/runtime identity, compatibility impact, and checks that were not executed.

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
- Behavioral examples expose enough context, expected reasoning, and failure boundaries to calibrate an AI reviewer.

## Portable runtime requirements

- Do not depend on `harness.md`, `.harness/`, a native harness CLI, or one vendor's configuration for core activation.
- Keep shared frontmatter valid for the Agent Skills specification.
- If a runtime-specific enhancement is useful, isolate it as optional metadata or documentation and preserve the basic skill path.

## Review standard

A contribution is not complete merely because one model gives a favorable answer. Review activation paths, frontmatter, compatibility, documentation, critical architecture blockers, repeated-run variance, and whether the changed behavioral case detects the intended failure.
