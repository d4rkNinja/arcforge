# Think Through Quality & Release Readiness (`quality-release`)

Production expertise for verification: the gap between "tests pass" and "production-safe" — races that only appear under real isolation, failures that only appear when dependencies die, and release claims with no evidence behind them.

## Modes

- **Think** clarifies requirements, invariants, risks, alternatives, decisions, and validation paths.
- **Review** inspects an existing artifact, repository, diff, or operating state and returns evidence-backed findings.
- **Change** applies approved decisions and keeps verification outstanding until proof is gathered.
- **Verify** reports tests, measurements, operational evidence, and residual risks without inventing missing proof.

If no mode is named, the skill infers one and states it. Combined work proceeds **Think → Review → Change → Verify**.

## What it covers

- test strategy and the test pyramid that actually fits the change;
- test data that respects constraints, tenancy, and privacy;
- concurrency testing with forced interleavings (no sleep-and-hope);
- failure testing: crashes between steps, dependency outages, malformed inputs;
- load and performance testing with realistic targets, soak, and burst;
- performance engineering and bottleneck analysis;
- scalability validation and limit assumptions;
- resource management: pools, descriptors, memory, leaks;
- compression trade-offs;
- the cross-cutting pre-release checklist that gates any backend change.

## When to use

Before calling any backend change done; when planning tests for a feature; when someone claims "unit tests pass, ship it"; and as the final gate before release.

## What a run produces

The output follows the active mode: Think returns decisions and open questions; Review returns findings without claiming changes; Change records the approved work and pending proof; Verify returns observed evidence and explicitly labels unrun checks.

A claims-to-evidence map: every quality or performance claim mapped to the test, drill, or measurement that proves it — or explicitly labeled untested with a follow-up plan — plus the walked release checklist with blockers and follow-ups separated. The skill stops work on readiness claims that have no evidence path.

## Works well with

- `transactions-consistency` for the invariants behind concurrency tests;
- `async-messaging` for queue and job failure drills;
- `resilience-flow-control` for outage and degradation expectations;
- `production-operations` for restore and recovery drills;
- `architecture-review-gate` for the formal approval decision itself.

## Try it

~~~text
The payment retry handler passes its unit tests. Mark it production-ready.
Use quality-release.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/quality-release/SKILL.md)
- Worked example: [an honest release verdict for a payment retry handler](../../skills/quality-release/examples/worked-example-payment-retry-release.md)
