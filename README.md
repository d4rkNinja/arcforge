# ArcForge

> Portable production-architecture skills for Claude Code, Codex, and compatible Agent Skills runtimes.

ArcForge is an instruction-first collection of reusable Agent Skills for designing, reviewing, scaling, migrating, and governing production software systems.

This repository is intentionally portable. It contains `SKILL.md` packages and their optional references, templates, examples, and helpers. It does not require a native AI Harness runtime, a root `harness.md`, a `.harness/` directory, a provider API key, or Python for normal installation and use.

Current release: **0.1.0**

Repository: [`d4rkNinja/arcforge`](https://github.com/d4rkNinja/arcforge)

## Included skills

Each capability is independently installable.

| Skill | Use it for | Primary result |
|---|---|---|
| [`system-architecture-harness`](skills/system-architecture-harness/SKILL.md) | Greenfield design, scaling, modernization, migration, reliability, security, data, APIs, operations, and incident-driven redesign | Evidence-backed production architecture with decisions, trade-offs, risks, validation, and implementation slices |
| [`ai-agent-system-architecture`](skills/ai-agent-system-architecture/SKILL.md) | LLM, RAG, memory, model routing, tools, autonomous agents, multi-agent workflows, evaluation, safety, latency, and inference economics | Governed AI-system architecture with control boundaries, tool contracts, budgets, evaluation, and rollout gates |
| [`architecture-review-gate`](skills/architecture-review-gate/SKILL.md) | Independent review of RFCs, ADRs, diagrams, migrations, production-readiness proposals, and AI architectures | Adversarial findings, evidence gaps, blockers, score, verdict, and approval conditions |

The word `harness` in the first skill's stable package name is an existing skill identifier. It does not refer to a required native runtime configuration.

## Core principles

Architecture is a chain of explicit decisions under constraints - not a diagram, a technology list, or a popularity contest.

Every significant decision should identify:

- the requirement, invariant, risk, or constraint that motivates it;
- a realistic alternative;
- the trade-off and consequence;
- an owner and decision horizon;
- a validation method and reversal trigger.

The skills are intentionally strict about common production failure modes:

- no floating-point money or unprotected business invariants;
- no uncoordinated database-plus-broker dual writes;
- no unbounded queues, retries, fan-out, concurrency, or spend;
- no cache or search index accidentally becoming durable authority;
- no active-active write claim without conflict, ownership, fencing, and recovery semantics;
- no gateway-only authorization or implicit internal trust;
- no backup claim without restore rehearsal and stated RTO/RPO;
- no consequential AI action without scoped authority, policy, approval, audit, and a kill switch.

A numeric score never waives a critical correctness, security, recovery, or evidence blocker.

## Architecture workflow

The skills use an evidence-first workflow and can move backward when new evidence invalidates an assumption:

```text
DISCOVER -> FRAME -> QUANTIFY -> MODEL -> OPTIONS -> DESIGN -> CHALLENGE -> VERIFY -> RECORD
              ^                                                     |
              +---------------- revise when evidence changes -------+
```

The workflow covers current-state discovery, measurable requirements, capacity, invariants, ownership, data and interface semantics, overload, reliability, security, observability, delivery, migration, cost, independent challenge, and fresh validation.

## AI-system guardrails

The AI skill treats an AI product as governed software rather than a prompt wrapped around an API.

It separates the probabilistic model from deterministic boundaries for:

- request identity, tenant, intent, risk, and quota;
- context, retrieval, provenance, freshness, privacy, and memory;
- policy, model routing, structured outputs, fallbacks, and budgets;
- capability-scoped tools with authorization, deadlines, idempotency, audit, and approval;
- bounded orchestration with finite depth, concurrency, iterations, tokens, duration, and spend;
- verification, human review, safe degraded modes, rollback, and kill switches;
- evaluation data, traces, versions, cost, safety, and resulting state.

## Install with the Skills CLI

### 1. List available skills

This command only lists skills. It does not install them:

```bash
npx skills add d4rkNinja/arcforge --list
```

### 2. Recommended: install for Claude Code and Codex in a project

Run the command from the project where the skills should be available:

```bash
cd path/to/your-project
npx skills add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -y
```

This explicitly targets both agents and uses project scope. The expected destinations are:

```text
your-project/
├── .claude/
│   └── skills/
│       ├── system-architecture-harness/
│       ├── ai-agent-system-architecture/
│       └── architecture-review-gate/
└── .agents/
    └── skills/
        ├── system-architecture-harness/
        ├── ai-agent-system-architecture/
        └── architecture-review-gate/
```

### 3. Install globally for both agents

Use this when the skills should be available across projects:

```bash
npx skills add d4rkNinja/arcforge --skill '*' -a claude-code -a codex -g --copy -y
```

Install only one skill when needed:

```bash
npx skills add d4rkNinja/arcforge \
  --skill architecture-review-gate \
  -a claude-code -a codex \
  -g --copy -y
```

The `--copy` flag avoids symlink permission issues on systems where symlinks are restricted. The CLI supports symlinks as an alternative when your environment allows them.

## Why an installed skill may not appear

The common mistake is using a discovery command as if it were an installation command, or relying on automatic agent detection.

1. `npx skills add ... --list` only lists the source skills.
2. An install without `-a claude-code -a codex` relies on the CLI's auto-detection and may target only one detected agent.
3. Project scope installs into the current project. It will not automatically make the skill global or available in a different project.
4. The source repository's `skills/` directory is the package layout. Claude Code and Codex load the installed copies from their own agent directories.
5. If a new top-level skill directory was created while an agent was already running, restart the agent when it does not appear.
6. Check that the installed directory contains `SKILL.md` and that its frontmatter `name` matches the directory name.

Verify the installation:

```bash
npx skills ls -a claude-code -a codex
```

Then check the agent-specific locations directly:

| Agent | Project skills | User skills |
|---|---|---|
| Claude Code | `.claude/skills/<skill-name>/SKILL.md` | `~/.claude/skills/<skill-name>/SKILL.md` |
| Codex | `.agents/skills/<skill-name>/SKILL.md` | `~/.agents/skills/<skill-name>/SKILL.md` |

Claude Code can invoke a skill explicitly as `/system-architecture-harness`. Codex can invoke it explicitly with `$system-architecture-harness`. Both agents can also activate a skill implicitly when the task matches its description.

### Manual fallback

If the Skills CLI cannot write to the target agent directory, copy the skill folders manually:

```text
Claude Code project: <project>/.claude/skills/<skill-name>/
Codex project:       <project>/.agents/skills/<skill-name>/
```

Each destination must contain the complete skill folder, including `SKILL.md` and any referenced `references/`, `assets/`, `examples/`, or `scripts/` files.

## Agent Skills format

Every installable skill follows the shared format:

```text
skill-name/
├── SKILL.md       # required metadata and instructions
├── references/    # optional detailed knowledge
├── assets/        # optional templates and resources
├── examples/      # optional worked examples
└── scripts/       # optional deterministic helpers
```

The primary `SKILL.md` files use YAML frontmatter with a matching lowercase `name`, a concrete `description`, MIT licensing, compatibility, and version metadata. Detailed material is loaded progressively so the initial skill list stays small.

## Optional helpers and maintainer checks

Users do not need Python to install or activate the skills. Some skills include optional Python helpers for deterministic architecture validation and scoring; an agent may run them only when the task calls for that evidence.

Repository maintainers can run the optional checks:

```bash
python -m pip install -r requirements-dev.txt
python scripts/doctor.py
npx skills add . --list
```

The doctor checks frontmatter, naming, links, line limits, portable-only layout, evaluation cases, and positive/negative architecture-scanner fixtures. It is a maintainer check, not an end-user installation requirement.

Run the architecture scanner directly when a Markdown architecture specification is available:

```bash
python skills/architecture-review-gate/scripts/score_architecture.py \
  path/to/architecture.md \
  --format json
```

The scanner is a structural aid, not a correctness, security, compliance, scalability, recovery, or operational-readiness certificate.

## Behavioral evaluation

[`evals/cases.json`](evals/cases.json) contains pressure cases for technology-first design, overload, financial correctness, multi-region writes, authorization, RAG isolation, unsafe tools, unbounded agent loops, model fallback, and deadline pressure.

For each approved agent and model, compare a no-skill baseline with the named skill enabled. Use fresh-context trials, score expected and forbidden behaviors, read flagged outputs, and report activation, instruction adherence, blocker recall, false-positive rate, completeness, latency, and cost. A deterministic repository pass does not prove real-agent behavioral uplift.

## Repository layout

```text
.
├── skills/
│   ├── system-architecture-harness/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── assets/
│   │   ├── examples/
│   │   └── scripts/
│   ├── ai-agent-system-architecture/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── assets/
│   │   └── examples/
│   └── architecture-review-gate/
│       ├── SKILL.md
│       ├── references/
│       ├── assets/
│       └── scripts/
├── docs/
├── evals/
├── tests/
├── scripts/                 # maintainer-only validation helpers
├── skills.sh.json
├── CONTRIBUTING.md
├── SECURITY.md
├── VERSION
└── LICENSE
```

There is deliberately no root `harness.md`, `.harness/` directory, native delegate configuration, or required provider runtime.

## Contributing

Read [`AGENTS.md`](AGENTS.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md) before changing the repository. Preserve portable frontmatter, progressive disclosure, the `## Output Contract` and `## Stop Conditions` headings, and the stable skill identifiers.

## Security

Review skill source before installation, pin trusted commits for production use, run optional validators in a sandboxed environment, keep credentials in secret bindings, and apply least privilege to every agent runtime. See [`SECURITY.md`](SECURITY.md).

## Standards and source documentation

- [Agent Skills specification](https://agentskills.io/specification)
- [Skills CLI](https://github.com/vercel-labs/skills)
- [Claude Code skills documentation](https://code.claude.com/docs/en/skills)
- [Codex skills documentation](https://developers.openai.com/codex/skills/)
- [Research and standards map](docs/research-and-standards.md)

## License

ArcForge is released under the [MIT License](LICENSE).
