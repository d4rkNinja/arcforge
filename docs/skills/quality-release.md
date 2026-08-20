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
- evidence states and exact release-subject binding, so plans and prior claims are not presented as current proof;
- cross-skill boundary closure and governed release exceptions;
- the cross-cutting pre-release checklist that gates any backend change.

## When to use

Before calling any backend change done; when planning tests for a feature; when someone claims "unit tests pass, ship it"; and as the final gate before release.

## What a run produces

The output follows the active mode: Think returns decisions and open questions; Review returns findings without claiming changes; Change records the approved work and pending proof; Verify returns observed evidence and explicitly labels unrun checks.

A release verdict and claims-to-evidence map: every claim is classified as executed, planned, claimed, unavailable, or contradicted and tied to the exact release subject. The run also closes applicable sibling-skill boundaries, records any governed exceptions without changing the evidence, and separates blockers from bounded follow-ups.

## Works well with

- `transactions-consistency` for the invariants behind concurrency tests;
- `async-messaging` for queue and job failure drills;
- `resilience-flow-control` for outage and degradation expectations;
- `auth-access`, `api-contracts`, `data-storage`, and `security-privacy` for identity, contracts, persistence, and trust boundaries;
- `production-operations` for restore and recovery drills;
- `migration-evolution` and `runtime-delivery` for compatibility and release-subject integrity;
- `git-workflows` for candidate refs, immutable release tags, and source-to-artifact identity;
- `architecture-review-gate` for the formal approval decision itself.

## Try it

~~~text
The payment retry handler passes its unit tests. Mark it production-ready.
Use quality-release.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/quality-release/SKILL.md)
- Worked example: [an honest release verdict for a payment retry handler](../../skills/quality-release/examples/worked-example-payment-retry-release.md)
