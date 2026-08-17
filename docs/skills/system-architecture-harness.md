# Think Through Production Systems (`system-architecture-harness`)

Turns an idea, requirement set, existing codebase, or migration goal into an evidence-backed architecture that can be changed, operated, and challenged — not a diagram with fashionable boxes.

## Modes

- **Think** clarifies requirements, invariants, risks, alternatives, decisions, and validation paths.
- **Review** inspects an existing artifact, repository, diff, or operating state and returns evidence-backed findings.
- **Change** applies approved decisions and keeps verification outstanding until proof is gathered.
- **Verify** reports tests, measurements, operational evidence, and residual risks without inventing missing proof.

If no mode is named, the skill infers one and states it. Combined work proceeds **Think → Review → Change → Verify**.

## What it covers

- requirements, constraints, and measurable architecturally significant requirements;
- workload and capacity estimation (traffic, storage, fan-out, cost at 1×/10×/100×);
- invariants, state machines, consistency, and data ownership;
- architecture style choices: modular monolith (the default), services, event-driven, serverless, edge;
- APIs, events, workflows, and their failure and compatibility semantics;
- scaling, overload control, latency budgets, and cost;
- failure engineering, disaster recovery, RTO/RPO, and restore evidence;
- security, privacy, tenancy, and abuse modeling;
- observability, SLOs, rollout, rollback, and operations;
- alternatives, ADRs, risks, validation plans, and safe change slices.

It also carries deeper guidance for code/module boundaries, language and runtime choices, client/offline architecture, platform engineering, and technical-debt/rewrite decisions.

## When to use

- starting a new production system or major subsystem;
- changing storage, consistency, or service boundaries;
- planning scale, reliability, migration, or production readiness;
- deciding whether distribution, multi-region, or a rewrite is actually justified.

Use `ai-agent-system-architecture` for LLM-powered systems and `architecture-review-gate` to review a design that already exists.

## What a run produces

The output follows the active mode: Think returns decisions and open questions; Review returns findings without claiming changes; Change records the approved work and pending proof; Verify returns observed evidence and explicitly labels unrun checks.

A complete architecture specification when Think needs that depth: decision summary, requirements and ASRs, workload model, invariants and ownership, container architecture, data and API design, failure matrix, security model, operations and rollout plan, cost, rejected alternatives with reversal triggers, risks, validation plan, and the smallest safe change slices. Research, scale, migration, and incident analysis are Think-mode specializations, not extra top-level modes.

## How it works

Eleven phases with hard gates — for example: no decision without a motivating requirement and an alternative; no "scales to X" without a capacity model; no invariant without an enforcement point; replication is not backup; a modular monolith stays the default until distribution is justified.

## Works well with

- domain skills — the specification hands off to `auth-access`, `data-storage`, `transactions-consistency`, and friends for focused decisions and changes;
- `architecture-review-gate` — independent review of the resulting design;
- `ai-agent-system-architecture` — when the system includes an AI subsystem.

## Try it

~~~text
Design a multi-tenant order platform with finite inventory, prepaid checkout,
and a regional recovery target. Compare a modular monolith with distributed
alternatives. Use system-architecture-harness.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/system-architecture-harness/SKILL.md)
- Templates: architecture spec, ADR, SLO, threat model, risk register, failure matrix, complexity ledger — under `skills/system-architecture-harness/assets/`
- Worked examples: order platform, contextual architecture comparison, complexity ledger — under `skills/system-architecture-harness/examples/`
