# Research and Standards Map

This repository was structured from current primary and ecosystem sources reviewed on 2026-08-13.

## Portable Agent Skills

- Skills.sh documentation: https://www.skills.sh/docs
- Skills CLI source and usage: https://github.com/vercel-labs/skills
- Agent Skills specification: https://agentskills.io/specification
- Agent Skills progressive disclosure: https://agentskills.io/skill-creation/best-practices
- Reference validator: https://github.com/agentskills/agentskills/tree/main/skills-ref
- Skills.sh page grouping schema: https://skills.sh/schemas/skills.sh.schema.json

Applied decisions:

- each installable capability lives in `skills/<slug>/SKILL.md`;
- frontmatter has stable `name`, concrete `description`, license, compatibility, and metadata;
- detailed knowledge is loaded from `references/`, reusable forms from `assets/`, and deterministic helpers from `scripts/`;
- repository grouping is declared in `skills.sh.json`;
- portable skills do not depend on one vendor-specific runtime.

## Harness Engineering

- Skills.sh harness-engineering skill: https://www.skills.sh/github/awesome-copilot/harness-engineering
- Harness Skills workflow documentation: https://developer.harness.io/docs/platform/harness-ai/harness-skills/

Applied formula:

```text
Harness = Instructions + Constraints + Feedback + Memory + Evaluation + Governance
```

The repository therefore includes durable instructions, deterministic checks, failure memory through eval cases, CI drift checks, explicit governance, and an adoption/installation guide rather than only three prompt files.

## Native AI Harness

- AI Harness introduction: https://htekdev.github.io/ai-harness/
- `harness.md` frontmatter: https://htekdev.github.io/ai-harness/reference/harness-md.html
- Hook artifact schema: https://htekdev.github.io/ai-harness/reference/hook-artifact.html
- Sub-agent artifact schema: https://htekdev.github.io/ai-harness/reference/sub-agent-artifact.html

Applied decisions:

- root `harness.md` combines runtime frontmatter with the orchestrator system prompt;
- `.harness/agents/*.md` uses filename-derived identity and bounded role prompts;
- `.harness/hooks/command-guard.md` uses a `tool.pre` decision hook;
- tool policy and delegation budgets are in the execution configuration;
- native artifacts complement portable skills rather than replacing them.

## System Architecture Knowledge

The production architecture references were derived from the earlier architecture package built from the `d4rkNinja/system-design-notes` request and expanded with production requirements, C4 views, consistency, overload, SLOs, disaster recovery, security, privacy, migrations, operations, economics, and AI-system governance.

Source mapping and coverage notes remain in:

- `skills/system-architecture-harness/references/13-repo-coverage-and-gap-analysis.md`
- `skills/system-architecture-harness/references/14-source-map.md`

The exact fork-specific GitHub contents should be re-audited whenever the source repository changes. This repository does not silently claim that a moving upstream source has remained unchanged.
