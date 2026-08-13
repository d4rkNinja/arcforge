# Contributing

## Change Process

1. Open an issue or change description identifying the observed failure, missing architecture case, or standards update.
2. Add a failing repository test or a behavioral case under `evals/`.
3. Make the smallest skill, reference, harness, hook, agent, or validator change that addresses the failure.
4. Run `python scripts/doctor.py`.
5. Describe evidence, compatibility impact, and any runtime checks that were not executed.

## Skill Requirements

- Directory and frontmatter `name` match.
- `description` begins with `Use when` and contains concrete activation signals.
- `license: MIT` and semantic `metadata.version` remain present.
- Primary `SKILL.md` remains at 500 lines or fewer.
- Local links resolve from the file that contains them.
- Deep reference material remains one link away from the primary skill when practical.
- New executable helpers use standard-library dependencies unless the requirement justifies more.

## Harness Requirements

- Native sub-agent identity comes from the filename; do not add a frontmatter `name` field.
- Every sub-agent defines a bounded deliverable and boundaries.
- Hooks keep executable Starlark in frontmatter and reviewer documentation in the body.
- Delegation, tool authority, and destructive actions remain explicitly governed.

## Review Standard

A contribution is not complete merely because tests pass. Review requirement coverage, critical blockers, compatibility, documentation, and whether the new test can detect the intended failure.
