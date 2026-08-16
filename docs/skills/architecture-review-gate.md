# Review Software Architecture (`architecture-review-gate`)

An independent, adversarial review of a design that already exists. It reconstructs the system from evidence, challenges the riskiest decisions, and blocks approval when something critical is missing — without rewriting the architecture for you.

## What it covers

- RFC, ADR, diagram, migration plan, and production-readiness reviews;
- five evidence gates: problem/fitness, state/boundaries, failure/assurance, delivery/operation, economics/complexity/evolution;
- requirement-to-decision tracing and complexity-ledger inspection;
- correctness, data, workflow, scale, recovery, security, tenancy, and operations findings;
- separating **defects** from **evidence gaps**, **risks**, and **preferences** — not every disagreement is a redesign;
- post-incident structural review (initiating trigger vs enabling conditions, without operator blame);
- architecture-metric review that keeps measures a governed vector, never a ranking of engineers.

## When to use

- before approving an RFC, ADR, migration, or scaling plan;
- production-readiness and launch gates;
- due diligence on a system you inherited or are buying into;
- after an incident, to find the structural cause rather than the nearest operator.

Review mode is independent: it does not rewrite the design or implement fixes unless you explicitly ask for that next step.

## What a run produces

A review report: frozen review frame and evidence gates, critical and high/medium findings, evidence gaps with what would close them, incident causality (when applicable), confidence and model disclosure, a clear verdict, blockers, and explicit approval conditions. Optional numeric summaries exist but can never waive a blocker.

## How it works

The reviewer reads evidence before conclusions, reconstructs critical flows independently, treats claims and benchmarks as untrusted until corroborated, and runs an adversarial second pass. Critical correctness, security, tenancy, recovery, overload, migration, and AI-authority failures are non-waivable.

## Works well with

- `system-architecture-harness` and `ai-agent-system-architecture` — designs produced by those skills can be reviewed here;
- `quality-release` — the code-level sibling for verifying an implementation rather than a design.

## Try it

~~~text
Review this architecture RFC for production readiness. Reconstruct the data
and trust boundaries, challenge the capacity and recovery claims, and return
blockers, evidence gaps, and approval conditions. Use architecture-review-gate.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/architecture-review-gate/SKILL.md)
- Templates: review report, review checklist, post-incident review — under `skills/architecture-review-gate/assets/`
- Calibration inputs and worked reviews — under `skills/architecture-review-gate/examples/`
