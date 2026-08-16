---
name: resilience-flow-control
description: "Use when implementing or changing resilience and traffic-control code: caching and invalidation, cache stampede and hot keys, rate limiting (fixed/sliding window, token bucket, distributed), quotas and usage limits, distributed cache coordination, external API integrations and provider failure, retry engineering with backoff and jitter, timeout engineering, circuit breakers, bulkheads, graceful degradation, and backpressure/admission control. Loads production implementation papers with MUST/SHOULD/AVOID/NEVER rules, failure modes, and verification checklists to read before writing code. For queue and event delivery semantics use async-messaging; for transaction and locking internals use transactions-consistency; for whole-system overload architecture use system-architecture-harness."
---

# Resilience & Flow Control Implementation

## Overview

Implementation intelligence for surviving load and dependency failure. Each reference paper captures the mechanics that separate resilient systems from hopeful ones: retry storms, synchronized expiry, thundering herds, timeouts that compose incorrectly, circuit breakers without fallbacks, and rate limits that fail open exactly when they matter.

**Core principle:** Every dependency fails, every cache goes stale, and every retry amplifies load. Controls must have explicit semantics (window, scope, fail-open/closed) and the system must stay bounded while capacity is unavailable.

## Implementation Law

```text
NO RESILIENCE IMPLEMENTATION WITHOUT:
1. the primary paper(s) for the control read in full first;
2. the failure being defended against named (timeout, overload, staleness,
   provider outage) before choosing a mechanism;
3. "Existing-codebase checks" run when changing existing controls;
4. every applicable MUST mapped to a bounded decision, a test that
   injects the failure, or a documented exception.
```

## When to Use

Use this skill when implementing or changing:

- caches: placement, TTL, eviction, invalidation, warming, negative caching, stampede protection;
- distributed cache coordination and hot-key handling;
- rate limiting by IP/user/tenant/endpoint, window algorithms, distributed limiting, fail-open/closed policy;
- quotas: soft/hard limits, reservation, reset windows, overage;
- external integrations: provider contracts, outages, degradation, replacement risk;
- retries: classification, caps, budgets, exponential backoff with jitter, honoring provider pushback;
- timeouts: per-hop and end-to-end deadlines, cancellation propagation;
- circuit breakers: trip thresholds, half-open probing, fallback behavior;
- bulkheads and concurrency limits;
- graceful degradation and load shedding;
- backpressure and admission control for queues and workers.

## When Not to Use

- Queue/job/event delivery semantics: use `async-messaging`.
- Transaction, lock, and consistency internals: use `transactions-consistency` (023, 103).
- Auth throttling policy ownership: `auth-access` (004) defines the goal; this skill supplies the mechanism.
- Whole-system overload and capacity architecture: use `system-architecture-harness`.

## Required Context Loading

| Situation | Papers |
|---|---|
| Cache-aside/read-through/write-through, TTL, stampede, hot keys | [037 Caching](references/papers/037-caching.md) |
| Cache coordination across instances | [131 Distributed Cache Coordination](references/papers/131-distributed-cache-coordination.md) |
| Limit algorithms, scopes, distributed state, fail policy | [038 Rate Limiting](references/papers/038-rate-limiting.md) |
| Quota reservation, soft/hard limits, reset | [039 Quotas](references/papers/039-quotas.md) |
| Provider contracts, outages, degraded modes, exit risk | [051 External Integrations](references/papers/051-external-integrations.md) |
| Retry classification, caps, budgets, jitter | [052 Retry Engineering](references/papers/052-retry-engineering.md) |
| Deadline budgeting, timeout composition, cancellation | [053 Timeout Engineering](references/papers/053-timeout-engineering.md) |
| Breaker states, thresholds, fallbacks | [054 Circuit Breakers](references/papers/054-circuit-breakers.md) |
| Degradation modes, bulkheads, containment | [055 Resilience](references/papers/055-resilience.md) |
| Queue/worker backpressure, shedding, admission control | [104 Backpressure](references/papers/104-backpressure.md) |

## Workflow

1. Name the failure being defended against and the user journey it protects; select primary papers (a third-party checkout call touches 051 + 053 + 052 + 054).
2. Read the primary papers fully, including failure matrices and common bugs.
3. Answer the paper's pre-implementation questions; label autonomous assumptions and their impact.
4. For existing controls, run the existing-codebase checks: measure actual call patterns, current limits, and what happens today when the dependency is down.
5. Convert each MUST/SHOULD/AVOID/NEVER into bounded decisions with explicit semantics (window, scope, thresholds, fail-open/closed) and failure-injection tests.
6. Implement the smallest safe slice; carry the paper's verification checklist (outage simulation, stampede, synchronized expiry, retry storms) into the test plan.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Boundary Map

| If the task also involves | Also use |
|---|---|
| Idempotent effects under retry | `transactions-consistency` (036) |
| Queue depth/lag and worker bounds | `async-messaging` (043, 104 paths) |
| Capacity model and autoscaling limits | `system-architecture-harness` |
| Dependency latency budgets | `quality-release` (094, 095) |
| Rate-limit response codes and headers | `api-contracts` (013, 014) |
| Dependency health signals and alerts | `production-operations` (059, 139) |

## Output Contract

1. **Papers consulted** — numbers and the sections relied on.
2. **Defense map** — each named failure → mechanism, bounds, and fallback behavior.
3. **Assumptions and unanswered questions** — labeled, with their design impact.
4. **Rule-to-decision map** — each applicable MUST/SHOULD → control parameters, enforcement point, and failure-injection test.
5. **Failure modes addressed** — retry storms, stampedes, synchronized expiry, provider outage, unbounded backlog.
6. **Verification evidence** — outage drills, overload tests, and degradation-mode checks.

## Stop Conditions

Stop and revise when any of these appears:

- code is written before the defended failure is named;
- a retry without a cap, deadline, backoff with jitter, and idempotent effects;
- a remote call without a timeout, or timeouts that do not compose into an end-to-end deadline;
- a circuit breaker with no fallback or degraded mode behind it;
- a cache with no named source of truth, TTL/invalidation policy, stampede protection, or loss behavior;
- cache treated as authoritative state with no rebuild path;
- a rate limiter with no stated fail-open/fail-closed decision or distributed-awareness analysis;
- quotas enforced only client-side or without reservation for concurrent use;
- synchronized expiry or lockstep refresh with no jitter;
- unbounded concurrency, queue depth, or fan-out defended only by autoscaling;
- degradation that silently changes correctness or authorization semantics;
- any resilience MUST downgraded to a TODO without a documented exception.

## References

Ten production papers under `references/papers/`: 037 Caching, 038 Rate Limiting, 039 Quotas, 051 External Integrations, 052 Retry Engineering, 053 Timeout Engineering, 054 Circuit Breakers, 055 Resilience, 104 Backpressure, 131 Distributed Cache Coordination. Cross-domain pointers inside the papers name the sibling skill to activate.

Worked example: [caching, stampede defense, and rate limiting for a hot endpoint](examples/worked-example-hot-endpoint-protection.md).
