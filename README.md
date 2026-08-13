# ArcForge

> Portable, evidence-backed architecture skills for Claude Code, Codex, and compatible Agent Skills runtimes.

ArcForge is an instruction-first collection of reusable skills for designing, reviewing, scaling, migrating, and governing production software systems.

| | |
|---|---|
| Release | `0.1.0` |
| Repository | [`d4rkNinja/arcforge`](https://github.com/d4rkNinja/arcforge) |
| License | [MIT](LICENSE) |
| Format | Portable `SKILL.md` packages |
| Install | [Skills CLI](https://github.com/vercel-labs/skills) |

## What this repository contains

Each capability is a self-contained Agent Skill under `skills/<skill-name>/`. A skill has a portable `SKILL.md` entrypoint and may include references, templates, examples, deterministic helpers, and optional Codex display metadata.

ArcForge is deliberately portable. Normal installation and use do not require:

- a native AI Harness runtime;
- a root `harness.md` file or `.harness/` directory;
- a provider API key; or
- Python.

All three installed skills operate through natural-language instructions. They inspect supplied evidence, apply their decision rules and scorecards, and produce the required artifact without invoking Python, shell commands, JavaScript, or another programming-language runtime.

The word `harness` in `system-architecture-harness` is part of the stable skill identifier. It does not indicate a required runtime configuration.

## Included skills

Install all three, or select only the skill that matches the task.

| Skill | Use it for | What it produces |
|---|---|---|
| [`system-architecture-harness`](skills/system-architecture-harness/SKILL.md) | Greenfield systems, scaling, modernization, migrations, reliability, security, data, APIs, operations, and incident-driven redesign | Evidence-backed production architecture with decisions, trade-offs, risks, validation, and implementation slices |
| [`ai-agent-system-architecture`](skills/ai-agent-system-architecture/SKILL.md) | LLM, RAG, memory, model routing, tools, autonomous agents, multi-agent workflows, evaluation, safety, latency, and inference economics | Governed AI-system architecture with control boundaries, tool contracts, budgets, evaluation, and rollout gates |
| [`architecture-review-gate`](skills/architecture-review-gate/SKILL.md) | Independent review of RFCs, ADRs, diagrams, migrations, production-readiness proposals, and AI architectures | Adversarial findings, evidence gaps, blockers, score, verdict, and approval conditions |

Use the first skill for general architecture design, the second for AI-first systems, and the third when an existing proposal needs an independent challenge.

## Quick start

### Install for Claude Code and Codex in the current project

Run this one-line command from the project where the skills should be available:

```bash
npx skills add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -y
```

This command:

- downloads the source through the Skills CLI;
- installs every ArcForge skill;
- explicitly targets Claude Code and Codex; and
- copies files instead of relying on symlink permissions.

The project-scoped destinations are:

```text
your-project/
|-- .claude/
|   `-- skills/
|       |-- system-architecture-harness/
|       |-- ai-agent-system-architecture/
|       `-- architecture-review-gate/
`-- .agents/
    `-- skills/
        |-- system-architecture-harness/
        |-- ai-agent-system-architecture/
        `-- architecture-review-gate/
```

### Install globally

Use `-g` when the skills should be available across projects:

```bash
npx skills add d4rkNinja/arcforge --skill '*' -a claude-code -a codex -g --copy -y
```

### Install one skill

For example, to install only the independent review gate:

```bash
npx skills add d4rkNinja/arcforge --skill architecture-review-gate -a claude-code -a codex -g --copy -y
```

### List without installing

This is a discovery command only:

```bash
npx skills add d4rkNinja/arcforge --list
```

`--list` prints the available source skills. It does not place anything in Claude Code or Codex directories.

## Verify and use an installation

List installed skills for both agents:

```bash
npx skills ls -a claude-code -a codex
```

You can also inspect the entrypoints directly:

| Agent | Project scope | User/global scope |
|---|---|---|
| Claude Code | `.claude/skills/<skill-name>/SKILL.md` | `~/.claude/skills/<skill-name>/SKILL.md` |
| Codex | `.agents/skills/<skill-name>/SKILL.md` | `~/.agents/skills/<skill-name>/SKILL.md` |

Invoke a skill explicitly when you want a deterministic starting point:

```text
Claude Code: /system-architecture-harness
Codex:       $system-architecture-harness
```

Both agents can also activate a skill implicitly when the task matches its description. If a newly installed skill does not appear in an already-running agent, restart that agent after verifying the directory and `SKILL.md` entrypoint.

## Why a skill may not appear

| Cause | What to do |
|---|---|
| You ran `--list` | Run the install command without `--list`. |
| Automatic agent detection chose the wrong target | Specify `-a claude-code -a codex` explicitly. |
| The install was project-scoped in another directory | Run the command from the intended project, or add `-g` for global scope. |
| You checked the source package instead of the installed copy | Confirm the skill under `.claude/skills/` and/or `.agents/skills/`. |
| The agent was already running | Restart it after adding a new top-level skill directory. |
| The package is incomplete or renamed | Confirm `<skill-name>/SKILL.md` exists and its frontmatter `name` matches the directory name. |

The complete installed skill folder must be copied. Do not copy only `SKILL.md` when that skill references other bundled files.

## Manual installation fallback

If the Skills CLI cannot write to the target directory, copy the complete skill folder manually:

```text
Claude Code project: <project>/.claude/skills/<skill-name>/
Codex project:       <project>/.agents/skills/<skill-name>/
```

Each destination must contain `SKILL.md` and, when present, the skill's `agents/openai.yaml`, `references/`, `assets/`, `examples/`, and `scripts/` contents.

## How the packages are structured

Every installable skill follows the shared Agent Skills layout:

```text
<skill-name>/
|-- SKILL.md              # required portable instructions and metadata
|-- agents/
|   `-- openai.yaml       # optional Codex display metadata
|-- references/           # optional detailed knowledge
|-- assets/               # optional templates and resources
|-- examples/             # optional worked examples
`-- scripts/              # optional deterministic helpers
```

The primary `SKILL.md` files use minimal YAML frontmatter with a matching lowercase `name` and a concrete `description`. Codex-facing display metadata lives in the optional `agents/openai.yaml`; other compatible runtimes can ignore it. Detailed material is loaded progressively so the initial skill list stays small.

## Architecture approach

ArcForge treats architecture as a chain of explicit decisions under constraints, not as a diagram or technology list. Significant decisions should identify:

- the requirement, invariant, risk, or constraint that motivates the decision;
- a realistic alternative;
- the trade-off and consequence;
- an owner and decision horizon; and
- a validation method and reversal trigger.

The skills use an evidence-first workflow and can move backward when new evidence invalidates an assumption:

```text
DISCOVER -> FRAME -> QUANTIFY -> MODEL -> OPTIONS -> DESIGN
                                                     |
                                                     v
                                           CHALLENGE -> VERIFY -> RECORD
```

They are intentionally strict about common production failure modes:

- floating-point money or unprotected business invariants;
- uncoordinated database-plus-broker dual writes;
- unbounded queues, retries, fan-out, concurrency, or spend;
- caches or search indexes becoming durable authority by accident;
- active-active writes without conflict, ownership, fencing, and recovery semantics;
- gateway-only authorization or implicit internal trust; and
- backup claims without restore rehearsal and stated RTO/RPO.

A numeric score never waives a critical correctness, security, recovery, or evidence blocker.

### AI-system guardrails

The AI skill treats an AI product as governed software rather than a prompt wrapped around an API. It separates the probabilistic model from deterministic boundaries for:

- identity, tenant, intent, risk, quota, and privacy;
- context, retrieval, provenance, freshness, and memory;
- policy, model routing, structured outputs, fallbacks, and budgets;
- capability-scoped tools with authorization, deadlines, idempotency, audit, and approval;
- bounded orchestration with finite depth, concurrency, iterations, tokens, duration, and spend;
- verification, human review, safe degraded modes, rollback, and kill switches; and
- evaluation data, traces, versions, cost, safety, and resulting state.

## Maintainer checks

Users do not need Python for installation. Maintainers can run the repository's deterministic checks with the development dependencies:

```bash
python -m pip install -r requirements-dev.txt
python scripts/doctor.py
```

To include a real Skills CLI discovery and temporary Claude Code/Codex installation check:

```bash
python scripts/doctor.py --skills-cli
```

The doctor validates frontmatter, Codex metadata, resource navigation, links, line limits, instruction-only skill workflows, portable-only layout, evaluation cases, and positive/negative architecture fixtures. The optional CLI check confirms that all three source skills are discoverable and install into temporary `.claude/skills` and `.agents/skills` directories.

The architecture skills perform scoring and verification directly from their written instructions and referenced scorecards. Bundled scripts are retained only for deterministic repository maintenance and fixture testing; installed skill workflows do not ask users or agents to execute them. Repository checks do not certify correctness, security, compliance, scalability, recovery, or operational readiness.

## Behavioral evaluation

[`evals/cases.json`](evals/cases.json) contains pressure cases for technology-first design, overload, financial correctness, multi-region writes, authorization, RAG isolation, unsafe tools, unbounded agent loops, model fallback, and deadline pressure.

For each approved agent and model, compare a no-skill baseline with the named skill enabled. Use fresh-context trials, score expected and forbidden behaviors, inspect flagged outputs, and report activation, instruction adherence, blocker recall, false-positive rate, completeness, latency, and cost. A deterministic repository pass does not prove real-agent behavioral uplift.

## Repository layout

```text
.
|-- skills/
|   |-- system-architecture-harness/
|   |   |-- SKILL.md
|   |   |-- agents/openai.yaml
|   |   |-- references/
|   |   |-- assets/
|   |   |-- examples/
|   |   `-- scripts/
|   |-- ai-agent-system-architecture/
|   |   |-- SKILL.md
|   |   |-- agents/openai.yaml
|   |   |-- references/
|   |   |-- assets/
|   |   `-- examples/
|   `-- architecture-review-gate/
|       |-- SKILL.md
|       |-- agents/openai.yaml
|       |-- references/
|       |-- assets/
|       `-- scripts/
|-- docs/
|-- evals/
|-- tests/
|-- scripts/                  # maintainer-only validation helpers
|-- skills.sh.json
|-- VERSION
|-- CONTRIBUTING.md
|-- SECURITY.md
`-- LICENSE
```

There is deliberately no root `harness.md`, `.harness/` directory, native delegate configuration, or required provider runtime.

## Contributing and security

Read [`AGENTS.md`](AGENTS.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md) before changing the repository. Preserve portable frontmatter, progressive disclosure, the exact `## Output Contract` and `## Stop Conditions` headings, and the stable skill identifiers.

Review skill source before installation, pin trusted commits for production use, run optional validators in a sandboxed environment, keep credentials in secret bindings, and apply least privilege to every agent runtime. See [`SECURITY.md`](SECURITY.md).

## Standards and source documentation

- [Agent Skills specification](https://agentskills.io/specification)
- [Agent Skills best practices](https://agentskills.io/skill-creation/best-practices)
- [Skills CLI](https://github.com/vercel-labs/skills)
- [Claude Code skills documentation](https://code.claude.com/docs/en/slash-commands)
- [Codex skills documentation](https://developers.openai.com/codex/skills/)
- [Research and standards map](docs/research-and-standards.md)
- [Release history](CHANGELOG.md)

## License

ArcForge is released under the [MIT License](LICENSE).
