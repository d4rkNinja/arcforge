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
| Claims need evidence paths (MUST) | Claims-to-evidence table produced | Review artifact | Every claim maps to a test/drill or is labeled untested |
| Forced interleavings (MUST) | Barrier tests at production isolation | Concurrency test suite | Duplicate-charge race asserted impossible, not probabilistic |
| Failure injection (MUST) | Timeout-after-commit, provider outage, DLQ overflow scenarios | Failure harness | Behavior matches spec for each injected class |
| Load shape (SHOULD) | Peak × 2 retry storm profile | Load test plan | Backlog drains within SLO; retry amplification bounded |
| Checklist gate (MUST) | Paper 146 walked for this surface | Release checklist artifact | Blockers vs follow-ups separated with owners |

## Failure modes addressed

- Duplicate charge under concurrent retry — forced-interleaving test.
- Infinite retry on permanent provider rejection — failure-class routing test.
- Retry storm amplifying an outage — load profile with jitter verification.
- Silent success without audit — checklist item requires audit-event assertion.

## Verification evidence

- Concurrency suite: 0 duplicate charges across 1,000 forced duplicate submissions.
- Failure suite: each injected class terminates in the specified state (retry, DLQ, suppress) with audit events.
- Load run: retry storm at 2× peak; drain time within objective.
- Checklist verdict: 3 blockers open (audit assertion, DLQ alert, runbook step) — release is **not** approved until closed.

## Stop-condition check

The stop condition "declaring production readiness from happy-path unit tests alone" was triggered by the request and resolved by the evidence program above; the verdict remains "not ready" until the three blockers close.

## Deliverable summary

A claims-to-evidence map, three new test suites, one load profile, and a checklist verdict with three named blockers and owners — an honest "not yet," with the shortest path to "ready."
