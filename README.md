# ArcForge

**Skills for System Architects and AI Engineers**

For engineers and agents who design production systems, build AI systems, and review architecture before it ships.

Good architecture is more than a diagram. It makes requirements, ownership, failure behavior, recovery, security, and cost clear. ArcForge helps agents work through those decisions.

Each skill gives an agent a repeatable workflow, with references and examples that make the result easier to review and validate.

## Install

```bash
npx skills@latest add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -y
```

## Why use it?

**Agents can write convincing architecture quickly.**

They can name services, choose technologies, and draw a plausible diagram. They can also miss an unowned decision, an unbounded retry, a backup with no restore evidence, or an AI tool crossing a policy boundary.

ArcForge puts those questions in the workflow: requirements, invariants, data ownership, bounded resources, failure and recovery, authorization, cost, validation, and rollout.

The result is clearer decisions, visible risks, and architecture that is easier to review and change.

## Reference

- [**system-architecture-harness**](https://github.com/d4rkNinja/arcforge/blob/main/skills/system-architecture-harness/SKILL.md) - Design or change production software architecture across requirements, workload, data, boundaries, APIs, reliability, security, operations, and cost.
- [**ai-agent-system-architecture**](https://github.com/d4rkNinja/arcforge/blob/main/skills/ai-agent-system-architecture/SKILL.md) - Design AI and agent systems with clear boundaries for retrieval, memory, tools, policy, verification, evaluation, safety, and rollout.
- [**architecture-review-gate**](https://github.com/d4rkNinja/arcforge/blob/main/skills/architecture-review-gate/SKILL.md) - Independently review RFCs, ADRs, diagrams, migrations, production-readiness proposals, and AI architectures; separate evidence gaps and critical blockers from the score.

## About

ArcForge `0.1.0` - [MIT License](LICENSE)

- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Agent Skills specification](https://agentskills.io/specification)
- [Skills CLI](https://github.com/vercel-labs/skills)
