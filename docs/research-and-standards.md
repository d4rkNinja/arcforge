# Research and Standards Map

This repository is a portable Agent Skills distribution. It does not depend on a native AI Harness runtime or a provider-specific orchestration file.

## Agent Skills format

Primary sources:

- [Agent Skills specification](https://agentskills.io/specification)
- [Agent Skills best practices](https://agentskills.io/skill-creation/best-practices)
- [Skills CLI](https://github.com/vercel-labs/skills)
- [Skills.sh documentation](https://www.skills.sh/docs)

Applied decisions:

- each installable capability lives in `skills/<slug>/SKILL.md`;
- portable `SKILL.md` frontmatter uses only stable `name` and concrete `description` fields;
- optional Codex UI metadata lives in `skills/<slug>/agents/openai.yaml` and is not required by Claude Code;
- every skill keeps its primary instructions in `SKILL.md` and loads deeper material progressively from `references/`, `assets/`, `examples/`, or its own optional `scripts/` directory;
- the repository grouping is declared in `skills.sh.json`;
- no skill requires a particular vendor, model provider, native harness CLI, or root runtime configuration for basic use.

## Agent discovery and installation

The installation and discovery guidance follows the current agent documentation:

- [Claude Code skills](https://code.claude.com/docs/en/slash-commands) loads project skills from `.claude/skills/<skill-name>/SKILL.md` and personal skills from `~/.claude/skills/<skill-name>/SKILL.md`.
- [Codex skills](https://developers.openai.com/codex/skills/) loads repository skills from `.agents/skills` and user skills from `~/.agents/skills`.
- [Skills CLI agent paths and options](https://github.com/vercel-labs/skills#readme) supports explicit `--agent`, `--global`, `--copy`, `--skill`, and `--yes` flags.

The README therefore recommends explicit per-agent installation instead of relying on auto-detection:

```bash
npx skills add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -y
```

Run that command from the target project for project-scoped installation. Use `-g` when the skills should be available across projects, then verify with `npx skills ls -g -a claude-code -a codex`.

## Architecture knowledge

The production architecture references were derived from the earlier architecture package built from the `d4rkNinja/system-design-notes` request and expanded with production requirements, C4 views, consistency, overload, SLOs, disaster recovery, security, privacy, migrations, operations, economics, and AI-system governance.

Source mapping and coverage notes remain in:

- `skills/system-architecture-harness/references/13-repo-coverage-and-gap-analysis.md`
- `skills/system-architecture-harness/references/14-source-map.md`

The exact fork-specific GitHub contents should be re-audited whenever the source repository changes. This repository does not silently claim that a moving upstream source has remained unchanged.
