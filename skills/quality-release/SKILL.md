---
name: quality-release
description: "Use when planning or reviewing verification and release readiness for a backend feature: test strategy and pyramid, test data management, concurrency testing with forced interleavings, failure and chaos testing, load and performance testing with realistic targets, performance engineering, scalability validation, resource-management and leak checks, compression trade-offs, and the cross-cutting pre-release implementation checklist. Loads production implementation papers with MUST/SHOULD/AVOID/NEVER rules, failure modes, and verification checklists to apply before claiming done. For architecture-level acceptance gates and review use architecture-review-gate; for SLO definition use system-architecture-harness; for runbooks and incident readiness use production-operations."
---

# Quality & Release Readiness Implementation

## Overview

Implementation intelligence for verification. Each reference paper captures the gap between "tests pass" and "production-safe": races that only appear under real isolation, failures that only appear when dependencies die, load targets with no workload model, and releases that never walked the cross-cutting checklist.

**Core principle:** Evidence, not assertion. Every quality or performance claim needs a test, measurement, or drill that would have failed if the claim were false — including the failure paths users and operators will actually hit.

## Implementation Law

```text
NO 'DONE' CLAIM WITHOUT:
1. the primary paper(s) for the verification type read in full first;
2. a named workload, failure, or interleaving the tests must force;
3. the pre-release checklist walked for the changed surface;
4. every gap between claimed and demonstrated behavior reported —
   never silently waived.
```

## When to Use

Use this skill when:

- planning tests for a backend feature and choosing the test pyramid shape;
- building test data that respects constraints, tenancy, and privacy;
- writing concurrency tests that force real interleavings with barriers;
- designing failure tests: crashes between steps, dependency outages, malformed inputs;
- defining load/performance tests with realistic targets, sustained soak, and burst;
- investigating or preventing performance regressions;
- validating scaling behavior and limit assumptions;
- checking resource management: pools, file descriptors, memory, cleanup;
- evaluating compression trade-offs for payloads and storage;
- walking the cross-cutting implementation checklist before release;
- reviewing whether a change is actually production-ready.

## When Not to Use

- Independent architecture review of a proposal: use `architecture-review-gate`.
- SLO/error-budget definition and SLI selection: use `system-architecture-harness` / `production-operations` (057).
- Runbooks and incident process: use `production-operations` (138, 139).
- Architecture-level capacity modeling: use `system-architecture-harness`.

## Required Context Loading

| Situation | Papers |
|---|---|
| Test strategy, pyramid, coverage meaning | [090 Testing Foundations](references/papers/090-testing-foundations.md) |
| Fixtures, tenancy, privacy of test data | [091 Test Data](references/papers/091-test-data.md) |
| Barrier-forced interleavings, real isolation | [092 Concurrency Testing](references/papers/092-concurrency-testing.md) |
| Crash injection, dependency failure, malformed input | [093 Failure Testing](references/papers/093-failure-testing.md) |
| Load models, soak, burst, targets | [094 Load & Performance Testing](references/papers/094-load-and-performance-testing.md) |
| Bottleneck analysis, latency work | [095 Performance Engineering](references/papers/095-performance-engineering.md) |
| Scaling limit validation | [096 Scalability](references/papers/096-scalability.md) |
| Pools, descriptors, memory, cleanup, leaks | [109 Resource Management](references/papers/109-resource-management.md) |
| Payload/storage compression trade-offs | [117 Compression](references/papers/117-compression.md) |
| Final pre-release gate for any backend change | [146 Cross-Cutting Implementation Checklist](references/papers/146-cross-cutting-implementation-checklist.md) |

## Workflow

1. Identify what must be demonstrated before release: correctness, concurrency safety, failure behavior, performance, or scale.
2. Select and read the primary papers; for any release, paper 146 is mandatory as the final gate.
3. Answer the paper's pre-implementation questions; write the workload/failure model the tests will use.
4. Review existing tests with the existing-codebase checks: what interleaving, outage, or load shape is currently never exercised?
5. Convert each MUST/SHOULD/AVOID/NEVER into concrete tests, measurements, or drills with pass/fail criteria tied to the claim being made.
6. Run or specify the suite; where the environment cannot exercise something (provider outage, region loss), state it as an untested claim with a plan.
7. Before claiming completion, walk paper 146 for the changed surface and stop if any applicable item lacks evidence or a documented exception.

## Boundary Map

| If the task also involves | Also use |
|---|---|
| The invariant being concurrency-tested | `transactions-consistency` (023–025, 036) |
| Queue/job failure drills | `async-messaging` (043, 045) |
| Outage/degradation expectations | `resilience-flow-control` (051–055) |
| Restore/recovery drills | `production-operations` (077, 078) |
| Compatibility of old/new versions | `migration-evolution` (070, 071, 134) |
| Release approval decision | `architecture-review-gate` |

## Output Contract

1. **Papers consulted** — numbers and the sections relied on.
2. **Claims and evidence map** — each quality/performance claim → test, drill, or measurement that proves it, or an explicit untested label.
3. **Workload/failure model** — shapes, targets, and interleavings the tests force.
4. **Rule-to-decision map** — each applicable MUST → test or gate with pass/fail criteria.
5. **Gaps honestly reported** — what was not exercised and why, with follow-up plan.
6. **Checklist verdict** — paper 146 walked for the changed surface; blockers vs follow-ups separated.

## Stop Conditions

Stop and revise when any of these appears:

- a "done" or "production-ready" claim with no evidence path behind it;
- concurrency tests that rely on sleeps instead of forced interleavings at real isolation;
- no failure test for any new external dependency or crash window;
- load tests with no workload model, targets, or sustained/burst distinction;
- performance claims without measurements, units, or a comparison baseline;
- resource pools, connections, or cleanup paths never exercised to their limits;
- test data that violates tenancy, constraints, or privacy rules;
- compatibility of old clients/versions never exercised before a release;
- the cross-cutting checklist skipped or its failures waived without owners;
- quality MUSTs downgraded to TODOs without documented exceptions.

## References

Ten production papers under `references/papers/`: 090 Testing Foundations, 091 Test Data, 092 Concurrency Testing, 093 Failure Testing, 094 Load & Performance Testing, 095 Performance Engineering, 096 Scalability, 109 Resource Management, 117 Compression, 146 Cross-Cutting Implementation Checklist. Cross-domain pointers inside the papers name the sibling skill to activate.

Worked example: [an honest release verdict for a payment retry handler](examples/worked-example-payment-retry-release.md).
