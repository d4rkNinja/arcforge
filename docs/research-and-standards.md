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
- every skill keeps its primary instructions in `SKILL.md` and loads deeper material progressively from `references/`, `assets/`, or `examples/`;
- only `SKILL.md` is required by the specification; ArcForge deliberately uses the optional reference and asset pattern without bundled executable logic;
- primary instructions stay below the specification's recommended 500-line limit, while focused resources remain one link away where practical;
- the repository grouping is declared in `skills.sh.json`;
- no skill requires a particular vendor, model provider, native harness CLI, or root runtime configuration for basic use.

This structure follows the specification's three-stage loading model: metadata for discovery, full `SKILL.md` on activation, and supporting resources only when the task needs them. Worked examples are included as on-demand calibration context rather than executable evaluators.

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

## Research mode and complexity accounting

Research mode is a decision-support workflow, not a literature-summary mode. Material
conclusions are recorded as atomic claims with a source class, stable citation or
repository location, supported finding, applicable context, failure context,
limitations or counter-evidence, qualitative confidence with a rationale, a
conditional architecture implication, and a next validation step. This keeps the
source's finding separate from the local inference and prevents correlation from being
presented as causation or a single case from being generalized universally.

Each mechanism that adds a process, network hop, datastore, queue, protocol, state
machine, trust boundary, deployment unit, or specialist operating practice gets a
dimensional Complexity Ledger entry. The ledger keeps concepts/state/protocols,
operational responsibility, failure modes and blast radius, knowledge and coordination,
dependencies, performance and scale, security/privacy, cost and sustainability,
reversibility/migration, and expected lifetime visible as separate consequences. It
does not collapse them into a synthetic architecture score; recommendations remain
conditional on requirements, evidence, ownership, and validation.

The reusable forms are the [Architecture Evidence Map](../skills/system-architecture-harness/assets/architecture-evidence-map-template.md),
[Complexity Ledger](../skills/system-architecture-harness/assets/complexity-ledger-template.md),
[evidence and complexity reference](../skills/system-architecture-harness/references/15-evidence-complexity-and-research.md),
and [worked complexity example](../skills/system-architecture-harness/examples/complexity-ledger-example.md).
The empirical source and its scope limits are recorded in the [source map](../skills/system-architecture-harness/references/14-source-map.md).

## Supplied architecture manuscript integration

The August 2026 user-supplied manuscript is a broad architecture evidence synthesis.
The supplied text did not include independently verifiable author, title, publisher,
or repository metadata, so ArcForge records it as research input rather than treating
the manuscript itself as a peer-reviewed or authoritative publication. Its individual
citations may still be verified and used according to their own source class and scope.

The manuscript materially expanded the portable skills in these areas:

- [code, runtime, and assurance decisions](../skills/system-architecture-harness/references/16-code-runtime-and-assurance.md), including behavioral contracts, unknown outcomes, bounded concurrency, language/runtime choice, and proportionate assurance;
- [client and platform architecture](../skills/system-architecture-harness/references/17-client-platform-architecture.md), including browser rendering, mobile/desktop lifecycle, offline/local-first authority, synchronization, conflicts, real-time catch-up, and search lifecycle;
- [platform, governance, economics, and evolution](../skills/system-architecture-harness/references/18-platform-governance-and-evolution.md), including paved-road exceptions, repository/build topology, ownership, TCO, debt, rewrite gates, migration sequencing, and governed metric vectors;
- [classical and AI control obligations](../skills/ai-agent-system-architecture/references/06-classical-and-ai-control-obligations.md), including state/invariant ownership, queue/cache/recovery semantics, gateway isolation, non-authoritative memory, multi-agent value evidence, delegated authority attenuation, and critical risk floors; and
- [fitness gates, incident causality, and metric governance](../skills/architecture-review-gate/references/05-fitness-gates-incidents-and-metrics.md), which makes review vector-first and separates incident triggers from structural enabling conditions.

The resulting method deliberately avoids a universal architecture score. Evidence state,
critical blockers, complexity obligations, reversibility, and metric vectors remain
separate so that strength in one dimension cannot conceal failure in another.
