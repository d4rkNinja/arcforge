# ArcForge

> Evidence-backed architecture skills for production systems and AI agents.

ArcForge is a focused collection of instruction-first Agent Skills for designing, challenging, and governing software architecture. It helps an agent turn requirements and evidence into explicit decisions, trade-offs, validation plans, and reviewable implementation work.

| | |
|---|---|
| Release | `0.1.0` |
| License | [MIT](LICENSE) |
| Repository | [`d4rkNinja/arcforge`](https://github.com/d4rkNinja/arcforge) |
| Skill format | Portable `SKILL.md` packages |

## Install

Install the complete collection into the current project with the [Skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills@latest add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -y
```

Install globally by adding `-g`:

```bash
npx skills@latest add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -g -y
```

Install a single skill when a focused workflow is all you need:

```bash
npx skills@latest add d4rkNinja/arcforge --skill architecture-review-gate -a claude-code -a codex --copy -y
```

The Skills CLI can also list the available packages before installation:

```bash
npx skills@latest add d4rkNinja/arcforge --list
```

After installation, select a skill by its name or let the agent activate it when the task matches its description. For example:

```text
Claude Code: /system-architecture-harness
Codex:       $system-architecture-harness
```

## Why use ArcForge?

Architecture work becomes unreliable when decisions are detached from requirements, workload, ownership, or evidence. ArcForge gives agents a disciplined way to:

- establish scope, assumptions, constraints, and quality targets;
- quantify workload, capacity, latency, availability, recovery, and cost;
- model data ownership, invariants, state transitions, and interface contracts;
- compare viable options with explicit consequences and decision horizons;
- challenge failure modes, security boundaries, privacy, abuse, and operations; and
- record validation, rollout, observability, rollback, and unresolved evidence.

The result is architecture that can be discussed, tested, operated, and changed, not only diagrammed.

## Skills

Choose the workflow that matches the work:

| Skill | Use it for | Produces |
|---|---|---|
| [`system-architecture-harness`](skills/system-architecture-harness/SKILL.md) | New or changing production systems, decomposition, migrations, scaling, reliability, security, data, APIs, and operations | An evidence-backed architecture with decisions, alternatives, trade-offs, risks, validation, and implementation slices |
| [`ai-agent-system-architecture`](skills/ai-agent-system-architecture/SKILL.md) | LLM products, RAG, memory, model routing, tools, autonomous or multi-agent workflows, evaluation, safety, latency, cost, and rollout | A governed AI-system design with control boundaries, tool contracts, budgets, evaluation, and release gates |
| [`architecture-review-gate`](skills/architecture-review-gate/SKILL.md) | Independent review of RFCs, ADRs, diagrams, migrations, production-readiness proposals, and AI architectures | Adversarial findings, evidence gaps, critical blockers, score, verdict, and approval conditions |

## Working model

ArcForge treats architecture as a chain of decisions under constraints:

```text
DISCOVER -> FRAME -> QUANTIFY -> MODEL -> COMPARE -> DESIGN -> CHALLENGE -> VERIFY -> RECORD
```

Each workflow adapts to the task, but decisions should remain traceable to:

- a requirement, invariant, risk, or constraint;
- an owner and decision horizon;
- a measurable validation method; and
- a reversal, rollout, or containment trigger.

The review workflow separates critical blockers from numeric scoring. A score never overrides a correctness, security, recovery, or evidence blocker.

## Design principles

- Evidence before confidence.
- Durable truth has an explicit owner.
- Resources, retries, fan-out, concurrency, and spend are bounded.
- Authorization is enforced at the action boundary.
- Failure, recovery, observability, and rollback are designed up front.
- AI proposals remain separate from policy, permissions, durable state, verification, and approval.

## Package structure

Each package has a `SKILL.md` entrypoint and may include supporting material loaded when the task needs it:

```text
<skill-name>/
|-- SKILL.md
|-- agents/openai.yaml       # optional agent display metadata
|-- references/               # detailed guidance
|-- assets/                   # reusable templates
`-- examples/                 # worked examples
```

The three primary skills are kept small and navigable. Detailed patterns, templates, examples, and supporting references live beside the entrypoint so an agent can load only what the task requires.

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before changing a skill. Keep frontmatter valid, preserve the stable skill names, maintain progressive disclosure, and update references or examples when the workflow changes.

## Standards and documentation

- [Agent Skills specification](https://agentskills.io/specification)
- [Agent Skills best practices](https://agentskills.io/skill-creation/best-practices)
- [Skills CLI](https://github.com/vercel-labs/skills)
- [Claude Code skills documentation](https://code.claude.com/docs/en/slash-commands)
- [Codex skills documentation](https://developers.openai.com/codex/skills/)

## License

ArcForge is released under the [MIT License](LICENSE).
