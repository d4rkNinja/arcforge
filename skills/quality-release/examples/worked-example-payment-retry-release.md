# Worked example: "tests pass" is not "production-ready"

> Calibration artifact: this shows the shape and depth a run of the `quality-release` skill should produce. It is illustrative, not exhaustive; the papers remain authoritative.

**Request (as a user would phrase it):**

> The payment retry handler passes its unit tests. Mark it production-ready.

## Papers consulted

- [090 Testing Foundations](../references/papers/090-testing-foundations.md) — what tests prove and cannot prove
- [092 Concurrency Testing](../references/papers/092-concurrency-testing.md) — forced interleavings
- [093 Failure Testing](../references/papers/093-failure-testing.md) — crash and dependency failure injection
- [094 Load & Performance Testing](../references/papers/094-load-and-performance-testing.md) — workload-shaped load
- [146 Cross-Cutting Implementation Checklist](../references/papers/146-cross-cutting-implementation-checklist.md) — the release gate

## Assumptions (labeled)

- **A1 (assumption):** "unit tests pass" means the happy path and two error branches. *If richer evidence exists,* the gap analysis shrinks but the checklist walk still applies.
- **A2 (assumption):** the handler can charge real money; the cost of a duplicate charge exceeds the cost of a dropped retry. *If false:* the evidence priorities shift toward delivery guarantees rather than suppression.

## Pre-implementation questions answered

- **What is claimed?** "Retry handling is correct and safe in production." Evidence required: duplicate suppression under concurrent retries, ambiguous-timeout handling, provider outage behavior, bounded backlog, and observability of retry outcomes (papers 090, 092, 093).
- **What do the unit tests actually prove?** Single-threaded, single-dependency, deterministic paths — none of the four failure classes that dominate production incidents (paper 090).
- **What must be forced, not hoped for?** Barrier-synchronized duplicate requests at the real DB isolation level; timeout-after-commit; provider 5xx/429 sequences; queue backlog drain (papers 092, 093).
- **What does the checklist add?** Walks paper 146 for the changed surface: idempotency scope, limits, rollback path, audit events, alerts, runbook — each item evidenced or explicitly deferred with an owner.

## Rule-to-decision map

| Rule (level) | Decision | Enforcement point | Verification |
|---|---|---|---|
| Claims need evidence paths (MUST) | Claims-to-evidence table produced | Review artifact | Every claim maps to inspected output or an honest non-executed state |
| Forced interleavings (MUST) | Barrier tests at production isolation | Concurrency test suite | Required; not run from the supplied request |
| Failure injection (MUST) | Timeout-after-commit, provider outage, DLQ overflow scenarios | Failure harness | Required; not run from the supplied request |
| Load shape (SHOULD) | Peak × 2 retry storm profile | Load test plan | Planned; not current evidence |
| Checklist gate (MUST) | Paper 146 walked for this surface | Release checklist artifact | Partial review only; runtime evidence unavailable |

## Failure modes addressed

- Duplicate charge under concurrent retry — forced-interleaving test.
- Infinite retry on permanent provider rejection — failure-class routing test.
- Retry storm amplifying an outage — load profile with jitter verification.
- Silent success without audit — checklist item requires audit-event assertion.

## Evidence states

| Evidence | State | Reason |
|---|---|---|
| Unit-test result | **claimed** | The requester says it passed; no command, output, revision, or artifact was supplied. |
| Concurrency suite | **planned** | The required forced-interleaving test has not been run. |
| Failure suite | **planned** | Timeout-after-commit and provider-outage scenarios have not been run. |
| Load run | **planned** | The workload profile exists only as a proposal. |
| Audit assertion, DLQ alert, runbook | **unavailable** | Their implementation and runtime evidence were not supplied. |

No executed result may be invented from this request. The verdict is **INSUFFICIENT EVIDENCE**, not production-ready. If inspection confirms a missing critical control or a failing required test, the verdict becomes **BLOCKED**.

## Boundary closure

| Boundary | Sibling skill | Owner / enforcement point | Evidence state | Unresolved condition |
|---|---|---|---|---|
| Payment state and idempotency | `transactions-consistency` | Payment service and authoritative transaction/idempotency record | **unavailable** | Atomic reservation, terminal outcome, and ambiguous-timeout reconciliation are not demonstrated. |
| Queue delivery and acknowledgment | `async-messaging` | Retry worker and durable queue/DLQ policy | **planned** | Crash windows, duplicate delivery, poison handling, and replay have not been exercised. |
| Retry/deadline policy | `resilience-flow-control` | Provider adapter and end-to-end operation budget | **planned** | Attempts, backoff, jitter, pushback, and timeout budgets have not been tested. |
| Audit, alerting, and recovery | `production-operations` | Operations owner, telemetry, reconciliation, and runbook | **unavailable** | No inspected alert, audit, reconciliation, rollback, or recovery drill exists. |

No boundary is `not applicable`: the real payment, queue, provider, and recovery paths must be traced before any such conclusion.

## Stop-condition check

The stop conditions for declaring readiness from happy-path unit tests and for treating planned checks as evidence were triggered. The result remains **INSUFFICIENT EVIDENCE** until the required suites run against the exact release subject and their output is inspected.

## Deliverable summary

A claims-to-evidence map, three required test suites, one load profile, and a cross-skill checklist remain to be executed. The honest deliverable is "not yet," with the shortest evidence path to a defensible verdict—never fabricated pass results.
