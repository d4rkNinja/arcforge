---
name: quality-release
description: "Use when thinking through, reviewing, changing, or verifying quality and release readiness: test strategy, test data, concurrency and failure testing, load and performance evidence, scalability, resource management, compression, or cross-cutting release checks. For independent architecture approval use architecture-review-gate; for SLO design use system-architecture-harness; for runbooks use production-operations."
---

# Think Through Quality & Release Readiness

## Overview

Production guidance for verification. Each reference paper captures the gap between "tests pass" and "production-safe": races that only appear under real isolation, failures that only appear when dependencies die, load targets with no workload model, and releases that never walked the cross-cutting checklist.

**Core principle:** Evidence, not assertion. Every quality or performance claim needs a test, measurement, or drill that would have failed if the claim were false — including the failure paths users and operators will actually hit.

## Domain Law

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
- walking the cross-cutting pre-release checklist;
- reviewing whether a change is actually production-ready.

## When Not to Use

- Independent architecture review of a proposal: use `architecture-review-gate`.
- SLO/error-budget definition and SLI selection: use `system-architecture-harness` / `production-operations` (057).
- Runbooks and incident process: use `production-operations` (138, 139).
- Architecture-level capacity modeling: use `system-architecture-harness`.

## Select the Operating Mode

| Mode | Use when | Required result |
|---|---|---|
| **Think** | The safe decision is not settled | requirements, constraints, invariants, risks, alternatives, decision, and validation path |
| **Review** | An artifact, repository, diff, or operating state already exists | evidence separated from assumptions, prioritized findings, and blockers |
| **Change** | Decisions are approved and repository changes are requested | the smallest safe change, compatibility notes, and verification still required |
| **Verify** | A claim needs proof | tests or measurements run, observed evidence, and residual risks |

If the user names a mode, use it. Otherwise infer the mode from intent and state the inference in one sentence. For a combined request, run **Think → Review → Change → Verify** and preserve the trace between phases. Think may stop with a decision; Review may stop with findings. Change must not claim completion before Verify. Verify must never turn a planned or unavailable check into evidence.

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

Use the domain workflow as shared gates, then branch by the selected mode:

- **Think:** answer the questions and stop with a reasoned decision and validation path; do not edit by default.
- **Review:** inspect the available artifact or repository and stop with evidence-backed findings; do not claim changes.
- **Change:** apply only approved decisions, then continue to Verify before claiming completion.
- **Verify:** run the relevant checks, report observed results, and label every unavailable or unrun check.

1. Identify what must be demonstrated before release: correctness, concurrency safety, failure behavior, performance, or scale.
2. Select and read the primary papers; for any release, paper 146 is mandatory as the final gate.
3. Answer the paper's pre-implementation questions; write the workload/failure model the tests will use.
4. Review existing tests with the existing-codebase checks: what interleaving, outage, or load shape is currently never exercised?
5. Convert each MUST/SHOULD/AVOID/NEVER into concrete tests, measurements, or drills with pass/fail criteria tied to the claim being made.
6. Apply the active mode: stop at a verification strategy in Think; stop at evidence gaps in Review; add approved tests or gates in Change; run the suite in Verify and state unavailable checks as untested claims.
7. Before claiming completion, walk paper 146 for the changed surface and stop if any applicable item lacks evidence or a documented exception.

## Companion Skills and Standalone Safety

| Type | When | Companion | Missing companion behavior |
|---|---|---|---|
| **Required** | Concurrency invariants, duplicate effects, or ambiguous outcomes are tested | `transactions-consistency` | Preserve the invariant and require forced interleavings; do not invent expected semantics. |
| **Recommended** | Queue or worker failure drills are in scope | `async-messaging` | State the required delivery scenarios and label domain depth missing. |
| **Recommended** | Outage, degradation, or overload claims are in scope | `resilience-flow-control` | Require measured bounds and label control depth missing. |
| **Handoff** | An independent architecture approval is requested | `architecture-review-gate` | Report verification evidence without self-approving the architecture. |

If a companion is unavailable, complete only the safe local quality decision, name the missing domain depth, and recommend the exact technical ID or relevant installation group. Never claim unavailable material or an unrun test was used, and never weaken a blocker because coverage is missing.

## Output Contract

The selected mode is authoritative. Include only applicable fields below; a planned check is a validation path, not verification evidence.

Scale the output to the active mode: Think returns a verification strategy; Review returns evidence gaps and findings; Change returns test or release-gate changes plus pending proof; Verify returns only observed results and explicitly labels every unrun check. A combined flow preserves all four phases.

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
