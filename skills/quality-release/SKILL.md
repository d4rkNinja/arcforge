---
name: quality-release
description: "Use when thinking through, reviewing, changing, or verifying quality and release readiness: test strategy, test data, concurrency and failure testing, load and performance evidence, scalability, resource management, compression, release exceptions or waivers, cross-domain completion, and production-ready claims. For independent architecture approval use architecture-review-gate; for SLO design use system-architecture-harness; for runbooks use production-operations."
---

# Think Through Quality & Release Readiness

## Overview

Production guidance for verification. Each reference paper captures the gap between "tests pass" and "production-safe": races that only appear under real isolation, failures that only appear when dependencies die, load targets with no workload model, and releases that never walked the cross-cutting checklist.

**Core principle:** Evidence, not assertion. Every quality or performance claim needs a test, measurement, or drill that would have failed if the claim were false — including the failure paths users and operators will actually hit. A plan is not executed evidence, and a waiver does not change what the evidence says.

## Domain Law

```text
NO 'DONE' CLAIM WITHOUT:
1. the primary paper(s) for the verification type read in full first;
2. a named workload, failure, or interleaving the tests must force;
3. the pre-release checklist walked for the changed surface;
4. every claim assigned an evidence state and bound to the exact subject tested;
5. every touched sibling-skill boundary and exception closed under the
   Release Decision Gate below — never silently waived.
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
- reviewing a release exception, waiver, risk acceptance, or "ship anyway" request;
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

1. Identify the readiness claim and changed surface: entry points, data, side effects, dependencies, deployment, rollback, and operations.
2. Select and read the primary papers; for any release, paper 146 is mandatory as the final gate.
3. Answer the paper's pre-implementation questions; write the workload/failure model the tests will use.
4. Review existing tests with the existing-codebase checks: what interleaving, outage, or load shape is currently never exercised?
5. Convert each MUST/SHOULD/AVOID/NEVER into concrete tests, measurements, or drills with pass/fail criteria tied to the claim being made.
6. Apply the active mode: stop at a verification strategy in Think; stop at evidence gaps in Review; add approved tests or gates in Change; run the available suite in Verify and inspect its output. Classify unrun, inaccessible, or merely reported checks honestly; specifying a check does not execute it.
7. Build the boundary-closure record from paper 146 and the companion table. Load each applicable sibling skill when available; otherwise keep its obligations explicitly unresolved.
8. Apply the evidence, exception, and verdict rules below. Walk paper 146 last and do not claim completion while a required gate is blocked or decisive evidence is unavailable.

## Release Decision Gate

Use this gate for every readiness verdict.

### Evidence states

- **executed** — the test, measurement, or drill ran and its output was inspected; this describes provenance, not success, and the result must be bound to the relevant code or immutable artifact, configuration, schema/data version, dependency versions, environment, workload, and time;
- **planned** — specified but not run;
- **claimed** — reported by a person, document, or prior run whose output and subject were not inspected;
- **unavailable** — required evidence cannot currently be obtained;
- **contradicted** — inspected evidence shows the claim or required condition is false.

Only current `executed` evidence whose observed outcome satisfies the stated pass criteria can demonstrate a release claim. A failed or invariant-violating executed result is `contradicted`, not supporting evidence. A relevant code, artifact, configuration, schema, dependency, environment, or workload change invalidates evidence unless compatibility is itself demonstrated. Never convert `planned`, `claimed`, or `unavailable` into `executed` by changing the wording.

### Boundary closure

For every changed entry point, state transition, data copy, side effect, dependency, deployment step, and recovery path, record: applicable sibling skill/paper, accountable owner, enforcement point, evidence state, and unresolved condition. An item is `not applicable` only after tracing the real data and side-effect path and recording why the concern cannot occur. A requester cannot make a boundary disappear by calling it out of scope. If the sibling skill or decisive evidence is unavailable, mark the boundary unresolved and restrict the verdict.

### Exceptions

A permissible exception must record the exact unmet rule, affected scope, rationale, authorized decision owner and governance basis, current compensating controls, their evidence state and inspected result or link, expiry or review trigger, containment and rollback/forward-fix plan, and follow-up owner/date. Do not infer approval authority from a request to waive a gate, and never let the model approve its own exception.

A confirmed contradiction of an applicable `MUST`/`NEVER` or a critical correctness, authorization, tenant-isolation, security/privacy, data-integrity, or recovery condition remains **BLOCKED**. Risk acceptance may document accountability, but it does not change the evidence state or this skill's verdict.

### Verdicts

- **READY** — all required pre-release evidence is current and executed, every boundary is closed, and no blocker remains.
- **CONDITIONAL** — no critical blocker or decisive evidence gap exists; only explicitly governed, non-critical conditions remain.
- **BLOCKED** — a required gate failed or a critical contradiction remains.
- **INSUFFICIENT EVIDENCE** — decisive evidence is planned, claimed, unavailable, stale, or not bound to the release subject.

Deadlines, sunk cost, requester seniority, or a bare waiver never change the verdict criteria.

## Companion Skills and Standalone Safety

| Type | When | Companion | Missing companion behavior |
|---|---|---|---|
| **Required** | Concurrency invariants, duplicate effects, or ambiguous outcomes are tested | `transactions-consistency` | Preserve the invariant and require forced interleavings; do not invent expected semantics. |
| **Required** | Identity, authorization, or tenant-isolation boundaries are exercised | `auth-access` | Preserve actor, resource, action, and tenancy invariants; do not infer safety from happy-path tests. |
| **Required** | Secrets, privacy, cryptography, or abuse boundaries are exercised | `security-privacy` | Preserve the security and data-lifecycle blockers; do not invent control evidence. |
| **Recommended** | Queue or worker failure drills are in scope | `async-messaging` | State the required delivery scenarios and label domain depth missing. |
| **Recommended** | Outage, degradation, or overload claims are in scope | `resilience-flow-control` | Require measured bounds and label control depth missing. |
| **Recommended** | Request or client compatibility is affected | `api-contracts` | Trace the public contract and label compatibility evidence missing. |
| **Recommended** | Persistence constraints, precision, indexes, files, or lifecycle is affected | `data-storage` | Preserve authoritative data invariants and label storage evidence missing. |
| **Recommended** | Mixed-version compatibility, backfill, or cutover is affected | `migration-evolution` | Require coexistence and rollback/roll-forward evidence; do not infer migration safety. |
| **Recommended** | Configuration, artifact promotion, shutdown, or deployment is affected | `runtime-delivery` | Bind evidence to the exact artifact/configuration and label delivery checks unrun. |
| **Recommended** | Restore, failover, alert, runbook, or recovery claims are in scope | `production-operations` | Require operational proof against named targets and label drills unrun. |
| **Recommended** | Source refs, Git workflow, release tags, or source-to-artifact identity is assessed | `git-workflows` | Require the exact candidate identity and immutable release mapping; label hosted facts unverified. |
| **Handoff** | An independent architecture approval is requested | `architecture-review-gate` | Report verification evidence without self-approving the architecture. |

If a companion is unavailable, complete only the safe local quality decision, name the missing domain depth, and recommend the exact technical ID or relevant installation group. Never claim unavailable material or an unrun test was used, and never weaken a blocker because coverage is missing.

## Output Contract

The selected mode is authoritative. Include only applicable fields below; a planned check is a validation path, not verification evidence.

Scale the output to the active mode: Think returns a verification strategy; Review returns evidence gaps and findings; Change returns test or release-gate changes plus pending proof; Verify returns only observed results and explicitly labels every unrun check. A combined flow preserves all four phases.

1. **Verdict and evidence disclosure** — READY, CONDITIONAL, BLOCKED, or INSUFFICIENT EVIDENCE; exact subject and evidence states.
2. **Papers consulted** — numbers and the sections relied on.
3. **Scope and boundary closure** — touched paths, sibling skills/papers, owners, enforcement points, evidence, and unresolved handoffs.
4. **Claims and evidence map** — each claim → executed result or explicit planned, claimed, unavailable, or contradicted state.
5. **Workload/failure model** — shapes, targets, and interleavings the tests force.
6. **Rule-to-decision map** — each applicable MUST/SHOULD/AVOID/NEVER → test or gate with pass/fail criteria.
7. **Exception register** — governed fields above; distinguish risk acceptance from evidence and verdict.
8. **Checklist result and gaps** — paper 146 walked; blockers, missing evidence, and bounded follow-ups separated.

## Stop Conditions

Stop and revise when any of these appears:

- a "done" or "production-ready" claim with no evidence path behind it;
- a planned, claimed, unavailable, stale, or mismatched check presented as executed evidence;
- a touched sibling-skill boundary hidden as out of scope, `not applicable` without a traced path, or handed off with no owner and closure evidence;
- an exception with no authorized owner, governance basis, executed compensating control, expiry/review trigger, containment, and follow-up owner;
- an applicable MUST/NEVER or critical correctness, authorization, tenant-isolation, security/privacy, data-integrity, or recovery contradiction converted into READY or CONDITIONAL;
- concurrency tests that rely on sleeps instead of forced interleavings at real isolation;
- no failure test for any new external dependency or crash window;
- load tests with no workload model, targets, or sustained/burst distinction;
- performance claims without measurements, units, or a comparison baseline;
- resource pools, connections, or cleanup paths never exercised to their limits;
- test data that violates tenancy, constraints, or privacy rules;
- compatibility of old clients/versions never exercised before a release;
- the cross-cutting checklist skipped or its failures hidden by deadline or requester pressure;
- quality MUSTs downgraded to TODOs or bare documented exceptions.

## References

Ten production papers under `references/papers/`: 090 Testing Foundations, 091 Test Data, 092 Concurrency Testing, 093 Failure Testing, 094 Load & Performance Testing, 095 Performance Engineering, 096 Scalability, 109 Resource Management, 117 Compression, 146 Cross-Cutting Implementation Checklist. Cross-domain pointers inside the papers name the sibling skill to activate.

Worked example: [an honest release verdict for a payment retry handler](examples/worked-example-payment-retry-release.md).
