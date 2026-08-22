---
paper_number: 39
title: "Quotas"
layer: primitives
domain_profile: cache
corpus_version: 1.0.0
verified_through: 2026-08-17
canonical_source: "original/Pasted text.txt"
subtopic_count: 12
status: production-engineering-reference
---

# 039. Quotas

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Quotas** exists to trade freshness and operational complexity for latency, throughput, and dependency isolation without changing correctness silently. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

A quota is an enforceable capacity contract between the platform and its consumers. The owning domain defines the consumption unit, scope (tenant/key/endpoint), window semantics, reset behavior, and what happens at exhaustion. Never let best-effort counting decide commitments that need atomic enforcement.

The most important evidence base for this paper includes [S042](#s042) [S055](#s055) [S053](#s053). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- A cache is a derived copy with an explicit source of truth, staleness budget, invalidation mechanism, and failure mode.
- Cache keys are part of the security boundary and must include tenant, principal, locale, version, and policy context when those affect the value.
- TTL is not invalidation; it is only an upper bound on staleness under some conditions.
- Quota exhaustion cliffs, period-boundary reset bursts, and uneven tenant consumption dominate production behavior.
- Correctness must survive cache loss, partial outage, and eviction unless the cache is deliberately authoritative.

## 2. Scope and terminology map

The canonical topic list requires this paper to cover the following concerns. They are grouped only to expose relationships; no listed subtopic is omitted.

### Persistence and integrity

**Storage quotas**.

### Concurrency and distributed behavior

**Soft limits**, **Hard limits**, **Overage**, **Reset windows**, **Concurrent usage**.

### Operations and observability

**Request quotas**, **Compute quotas**, **Resource quotas**, **Daily/monthly quotas**, **Tenant quotas**, **Quota reservation**.

### Boundary of the paper

This paper treats **Quotas** as a production subsystem or reusable reasoning primitive. It covers semantics, ownership, persistence, APIs, security, concurrency, distributed behavior, operations, evolution, and verification. Framework syntax and large implementation listings are intentionally excluded.

## 3. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S042](#s042) [S055](#s055) [S053](#s053)

1. **Invariant 1:** A cache is a derived copy with an explicit source of truth, staleness budget, invalidation mechanism, and failure mode.
2. **Invariant 2:** Cache keys are part of the security boundary and must include tenant, principal, locale, version, and policy context when those affect the value.
3. **Invariant 3:** TTL is not invalidation; it is only an upper bound on staleness under some conditions.
4. **Invariant 4:** Quota consumption is enforced atomically against authoritative counters; approximate local counts never authorize commitments that require global accuracy.
5. **Invariant 5:** Correctness must survive cache loss, partial outage, and eviction unless the cache is deliberately authoritative.

Additional topic-specific invariants:

- **SHOULD — Request quotas:** Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **SHOULD — Compute quotas:** Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **SHOULD — Daily/monthly quotas:** Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **SHOULD — Overage:** Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **MUST — Tenant quotas:** Derive tenant context from an authenticated, authorized binding; propagate it explicitly through queries, caches, jobs, events, files, metrics, and audit records. Make unscoped access difficult or impossible.
- **SHOULD — Concurrent usage:** Use barriers/hooks to force the critical interleaving, repeat across real database isolation, and assert the invariant rather than timing or one response.

## 4. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Cache-aside vs read-through | Cache-aside is explicit and portable; read-through centralizes loading but can hide expensive misses. | Use the model that preserves ownership and observability. |
| Write-through vs invalidate-on-write | Write-through reduces miss windows but couples writes to cache; invalidation is simpler but races with concurrent fills. | Use versions or compare-and-set when stale repopulation matters. |
| Local vs distributed cache | Local caches are fast but inconsistent across instances; distributed caches coordinate state but add network dependency. | Use local caches for immutable/versioned data and distributed caches for shared mutable state. |
| Fail-open vs fail-closed | Fail-open protects availability but may violate security/freshness; fail-closed preserves policy but can become an outage multiplier. | Decide per data class; authorization and revocation caches usually require bounded stale behavior. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 5. Ownership, state, and lifecycle

Entries move through `absent → loading → fresh → stale → refreshing|evicted`, with expiration, invalidation, and version changes racing. Locks or single-flight controls need their own expiry and ownership. Warmup and bulk invalidation are operational states, not invisible implementation details.

```mermaid
stateDiagram-v2
    absent --> loading --> fresh --> stale
    stale --> refreshing --> fresh
    fresh --> invalidated --> absent
    loading --> failed --> origin_fallback
    stale --> evicted --> absent
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 6. Data model and API implications

Specify key construction, maximum value size, TTL distribution, stale allowance, negative-cache semantics, eviction expectations, and behavior when the cache is unavailable or inconsistent. A cached response must preserve authorization, locale, version, and content-negotiation dimensions.

A production representation commonly needs the following fields or equivalent evidence:

- versioned key namespace including tenant, authorization, locale, environment, and schema dimensions as applicable.
- value version/provenance and source version.
- created/fresh-until/stale-until/absolute-expiry timestamps.
- negative-entry and refresh ownership state.
- generation/invalidation sequence and safe lock/lease metadata when used.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 7. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### 7.1. Request quotas

- **SHOULD — engineering rule:** Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **Production failure mode:** Parallel operations overspend quota or failed work never releases reservations.
- **Existing-codebase evidence:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.

### 7.2. Storage quotas

- **SHOULD — engineering rule:** Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **Production failure mode:** Parallel operations overspend quota or failed work never releases reservations.
- **Existing-codebase evidence:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.

### 7.3. Compute quotas

- **SHOULD — engineering rule:** Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **Production failure mode:** Parallel operations overspend quota or failed work never releases reservations.
- **Existing-codebase evidence:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.

### 7.4. Resource quotas

- **SHOULD — engineering rule:** Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **Production failure mode:** Parallel operations overspend quota or failed work never releases reservations.
- **Existing-codebase evidence:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.

### 7.5. Daily/monthly quotas

- **SHOULD — engineering rule:** Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **Production failure mode:** Parallel operations overspend quota or failed work never releases reservations.
- **Existing-codebase evidence:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.

### 7.6. Soft limits

- **SHOULD — engineering rule:** Define the exact semantics of **Soft limits** within Quotas: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for soft limits is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for soft limits, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.7. Hard limits

- **SHOULD — engineering rule:** Define the exact semantics of **Hard limits** within Quotas: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for hard limits is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for hard limits, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.8. Overage

- **SHOULD — engineering rule:** Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **Production failure mode:** Parallel operations overspend quota or failed work never releases reservations.
- **Existing-codebase evidence:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.

### 7.9. Reset windows

- **SHOULD — engineering rule:** Define the exact semantics of **Reset windows** within Quotas: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for reset windows is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for reset windows, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.10. Tenant quotas

- **MUST — engineering rule:** Derive tenant context from an authenticated, authorized binding; propagate it explicitly through queries, caches, jobs, events, files, metrics, and audit records. Make unscoped access difficult or impossible.
- **Production failure mode:** A missing filter, reused cache key, delayed job, or admin path reads or writes another tenant's data.
- **Existing-codebase evidence:** Search for data-access methods that accept no tenant scope; run mutation and property tests that swap tenant identifiers at every boundary.

### 7.11. Quota reservation

- **SHOULD — engineering rule:** Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **Production failure mode:** Parallel operations overspend quota or failed work never releases reservations.
- **Existing-codebase evidence:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.

### 7.12. Concurrent usage

- **SHOULD — engineering rule:** Use barriers/hooks to force the critical interleaving, repeat across real database isolation, and assert the invariant rather than timing or one response.
- **Production failure mode:** A probabilistic sleep-based test passes while the actual race remains reachable.
- **Existing-codebase evidence:** Instrument the exact read/check/write or lease boundary and run deterministic competing operations.

## 8. Concurrency, transactions, idempotency, and consistency

Quota accounting races show up as overspend: two requests both read remaining=1 and both proceed. Atomic check-and-decrement (conditional update or Lua-style script), reservation with release on failure, and per-scope serialization bound the error. Define whether slight over-admission is acceptable or hard stops are mandatory — that decision drives every mechanism choice.

### Required reasoning sequence

1. State the invariant in business/domain terms.
2. Identify all concurrent writers, including jobs, webhooks, imports, administrators, retries, and old binaries.
3. Choose the narrowest authoritative enforcement: unique/check/foreign-key constraint, atomic conditional update, transaction/isolation, version compare-and-swap, lock with fencing, or durable workflow.
4. Define the commit point and the observable result for losers, duplicates, conflicts, timeouts, and ambiguous outcomes.
5. Add reconciliation for every invariant that spans independent systems or derived stores.

### Idempotency

- Scope keys by operation, actor/tenant, and target; bind them to a canonical request fingerprint.
- Atomically reserve or create the idempotency record with the domain effect. Concurrent duplicates must converge on one result.
- Distinguish a retryable pre-commit failure from an ambiguous or committed first attempt. Replaying a stored failure forever is not always correct.
- Set retention from the maximum retry/redelivery horizon and business risk, not a convenient cache TTL.

## 9. Security, authorization, privacy, and abuse resistance

Map trust boundaries, assets, attackers, privileges, data flows, and failure modes before selecting controls. Enforce least privilege in the component that owns the resource; edge filtering, WAFs, and gateways are supplementary. Treat every external, model-generated, cached, imported, or administrator-supplied value as untrusted at its use context.

- **MUST** authenticate the actual caller or workload and re-authorize the final action against authoritative tenant, ownership, resource state, and policy context.
- **MUST** reject mass assignment and unknown privileged fields; server-controlled identity, role, tenant, status, price, owner, and audit fields cannot come from an untrusted DTO.
- **MUST** classify and minimize sensitive data; redact logs/traces/errors, restrict exports and support tooling, propagate deletion, and account for backups and derived indexes.
- **SHOULD** combine rate limits with resource budgets, concurrency caps, payload/complexity limits, and detection. IP-only limiting is not an identity or abuse strategy.
- **AVOID** fail-open behavior for high-impact actions when policy, key, revocation, or tenant context is unavailable.

## 10. Distributed failure, retries, timeouts, and recovery

Plan for cold start, eviction storm, hot key, network partition, failover data loss, stale replica, oversized value, serialization mismatch, and cache latency worse than origin. Fail-open versus fail-closed depends on whether the cache accelerates data or enforces a security/resource control.

### Failure matrix

| Failure point | Required question | Safe pattern |
|---|---|---|
| Before durable write | Can the caller retry without creating a duplicate? | Validate early; reserve idempotency/identity atomically. |
| During local transaction | Can the whole transaction be retried from a fresh snapshot? | Roll back; retry only classified conflicts/deadlocks with bounded jitter. |
| After commit, before response | How can the outcome be discovered? | Replay by idempotency key or query a stable operation/resource ID. |
| Between database and message/provider | Which side is authoritative? | Durable outbox/intent plus reconciliation; never assume dual writes are atomic. |
| Worker/provider timeout | Could work still finish? | Treat outcome as ambiguous; deduplicate effect and reconcile before retrying. |
| Cache/index/replica lag | What staleness is acceptable? | Read authoritative state for critical decisions; expose or bound freshness. |
| Process/region failure | Who resumes ownership and how is the old owner fenced? | Leases with fencing, idempotent resume, replay, and runbook validation. |

## 11. Persistence, constraints, indexes, and caching

- Put race-sensitive invariants in the database or authoritative store. Application checks remain useful for error quality but are not the final guard.
- Design indexes from real query predicates, tenant scope, ordering, soft-delete conditions, and production cardinality. Verify plans and write amplification.
- Keep transactions bounded in time and rows; avoid network/provider calls while locks are held.
- Treat caches, search indexes, analytics, and replicas as derived unless explicitly authoritative. Version them and provide rebuild/reconciliation.
- Retention and cleanup must include references, uniqueness, tombstones, legal hold, audit, external copies, and interrupted-job recovery.

## 12. Observability, audit, and operational control

Measure hit/miss by logical operation, origin load, freshness age, evictions, memory fragmentation, hot-key concentration, lock contention, fill latency, invalidation failures, and fallback rate. Avoid raw user/tenant IDs as metric labels. Trace cache result and key class, not sensitive key contents.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 13. Compatibility, schema evolution, migration, deployment, and rollback

Version serialized values and key formats. During deployment, readers should tolerate old values or use a new generation; do not rely on synchronized cache flushes. Rollback must know whether old code can parse values written by new code. Retire generations with bounded cleanup.

### Safe change sequence

1. Inventory deployed clients, consumers, workers, schemas, flags, and retained messages/jobs.
2. Add tolerant readers and additive storage/contracts.
3. Deploy writers capable of old and new representations, with explicit authority and observability.
4. Backfill in resumable, idempotent, rate-limited chunks without overwriting newer mutations.
5. Verify semantic invariants and compare old/new behavior before switching authority.
6. Observe through the rollback window; reconcile divergence.
7. Remove legacy reads/writes only after usage is zero and rollback no longer needs them.

**Rollback warning:** code rollback does not undo committed data, messages, provider calls, emails, files, or user-visible side effects. For irreversible changes, define a forward-fix and compensation strategy.

## 14. Cross-cutting implementation matrix

| Concern | Required production decision |
|---|---|
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Quotas path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Request quotas`, `Resource quotas`, `Hard limits`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Fixed-window vs rolling-window quotas | Calendar resets are simple and predictable but create demand cliffs; rolling windows smooth consumption at higher counter cost. | Pick by product fairness semantics, size counter storage for the tenant count, and alert on reset-time load spikes. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Quotas; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 15. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Quotas** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Request quotas**: Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **MUST** — For **Compute quotas**: Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **MUST** — For **Daily/monthly quotas**: Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.
- **MUST** — For **Overage**: Separate rate from accumulated entitlement. Define unit, scope, reset/calendar semantics, reservation/commit/release flow, concurrent usage, soft versus hard limit, and reconciliation.

### SHOULD

- **SHOULD** — A cache is a derived copy with an explicit source of truth, staleness budget, invalidation mechanism, and failure mode.
- **SHOULD** — Cache keys are part of the security boundary and must include tenant, principal, locale, version, and policy context when those affect the value.
- **SHOULD** — TTL is not invalidation; it is only an upper bound on staleness under some conditions.
- Quota exhaustion cliffs, period-boundary reset bursts, and uneven tenant consumption dominate production behavior.
- **SHOULD** — Correctness must survive cache loss, partial outage, and eviction unless the cache is deliberately authoritative.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Adopt the **Cache-aside vs read-through** option that fits the workload and ownership boundary; Use the model that preserves ownership and observability.
- **MAY** — Adopt the **Write-through vs invalidate-on-write** option that fits the workload and ownership boundary; Use versions or compare-and-set when stale repopulation matters.
- **MAY** — Adopt the **Local vs distributed cache** option that fits the workload and ownership boundary; Use local caches for immutable/versioned data and distributed caches for shared mutable state.

### AVOID

- **AVOID** — Cross-tenant cache key collision.
- **AVOID** — Stale value resurrected after invalidation.
- **AVOID** — Stampede after common expiry.
- **AVOID** — Unbounded cache cardinality from user input.
- **AVOID** — Cache outage taking down the source database.
- **AVOID** — Using cache as authority accidentally.
- **AVOID** — Omitting tenant/auth/version dimensions from keys.
- **AVOID** — Flushing globally as deployment strategy.

### NEVER

- **NEVER** — Never put cross-tenant or authorization-dependent data behind an under-scoped cache key.
- **NEVER** — Never require a cache flush for correctness during every deploy.
- **NEVER** — Never use a best-effort cache as the sole durable record.

## 16. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Run cold-cache, eviction-storm, cache-down, slow-cache, partition, failover, and serialization-version scenarios.
- Synchronize concurrent consumption against resets and verify reservation races, carryover semantics, and tenant
- [ ] Test hot keys, negative caching, TTL jitter, lock expiry, and origin overload at production concurrency.
- [ ] Roll old and new key/value formats together without a global flush; verify rollback parsing.
- [ ] Inject stale authorization or quota data and prove the documented fail-open/fail-closed behavior.
- [ ] **Request quotas:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.
- [ ] **Compute quotas:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.
- [ ] **Daily/monthly quotas:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.
- [ ] **Overage:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.
- [ ] **Tenant quotas:** Search for data-access methods that accept no tenant scope; run mutation and property tests that swap tenant identifiers at every boundary.
- [ ] **Concurrent usage:** Instrument the exact read/check/write or lease boundary and run deterministic competing operations.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 17. Common production bugs and incorrect implementations

- Cross-tenant cache key collision.
- Stale value resurrected after invalidation.
- Reset bursts where all tenants refire simultaneously at the period boundary overwhelm downstream capacity.
- Unbounded cache cardinality from user input.
- Cache outage taking down the source database.
- **Request quotas:** Parallel operations overspend quota or failed work never releases reservations.
- **Compute quotas:** Parallel operations overspend quota or failed work never releases reservations.
- **Daily/monthly quotas:** Parallel operations overspend quota or failed work never releases reservations.
- **Hard limits:** A framework or provider default for hard limits is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Overage:** Parallel operations overspend quota or failed work never releases reservations.
- **Tenant quotas:** A missing filter, reused cache key, delayed job, or admin path reads or writes another tenant's data.
- **Concurrent usage:** A probabilistic sleep-based test passes while the actual race remains reachable.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Using cache as authority accidentally.
- Omitting tenant/auth/version dimensions from keys.
- Flushing globally as deployment strategy.
- Adding a lock without lease/fencing/single-flight bounds.
- Failing open for security controls without analysis.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Quotas** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- For **Request quotas**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Parallel operations overspend quota or failed work never releases reservations.
- For **Compute quotas**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Parallel operations overspend quota or failed work never releases reservations.
- For **Daily/monthly quotas**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Parallel operations overspend quota or failed work never releases reservations.
- For **Overage**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Parallel operations overspend quota or failed work never releases reservations.
- For **Tenant quotas**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A missing filter, reused cache key, delayed job, or admin path reads or writes another tenant's data.
- How stale may each value be, and what happens when invalidation, fill, or the cache itself fails?

## 20. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Quotas**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] **Request quotas:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.
- [ ] **Compute quotas:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.
- [ ] **Daily/monthly quotas:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.
- [ ] **Hard limits:** Locate every implementation path for hard limits, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Overage:** Run concurrent reserve/commit/cancel tests and compare authoritative usage to metering events after failures.
- [ ] **Tenant quotas:** Search for data-access methods that accept no tenant scope; run mutation and property tests that swap tenant identifiers at every boundary.
- [ ] **Concurrent usage:** Instrument the exact read/check/write or lease boundary and run deterministic competing operations.
- [ ] Enumerate key builders and invalidation publishers; compare tenant, locale, auth, schema, and environment dimensions.

## 21. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [038. Rate Limiting](../cross-cutting/038-rate-limiting.md) — layer: `cross-cutting`; profile: `cache`.
- [037. Caching](../systems/037-caching.md) — layer: `systems`; profile: `cache`.
- [096. Scalability](../cross-cutting/096-scalability.md) — layer: `cross-cutting`; profile: `performance`.
- [131. Distributed Cache Coordination](../cross-cutting/131-distributed-cache-coordination.md) — layer: `cross-cutting`; profile: `cache`.
- [036. Idempotency](036-idempotency.md) — layer: `primitives`; profile: `transactions`.
- [010. Multi-Tenancy](../systems/010-multi-tenancy.md) — layer: `systems`; profile: `authorization`.
- [028. Query Design](../systems/028-query-design.md) — layer: `systems`; profile: `data_model`.
- [125. Cleanup Jobs](../cross-cutting/125-cleanup-jobs.md) — layer: `cross-cutting`; profile: `data_ops`.
- [057. Metrics](../cross-cutting/057-metrics.md) — layer: `cross-cutting`; profile: `observability`.
- [146. Cross-Cutting Implementation Checklist](../cross-cutting/146-cross-cutting-implementation-checklist.md) — layer: `cross-cutting`; profile: `checklist`.
- [053. Timeout Engineering](053-timeout-engineering.md) — layer: `primitives`; profile: `resilience`.
- [027. Indexing](../systems/027-indexing.md) — layer: `systems`; profile: `data_model`.

## 22. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s026"></a> **[S026] HTTP Caching.** IETF; 2022; RFC 9111. [https://www.rfc-editor.org/rfc/rfc9111.html](https://www.rfc-editor.org/rfc/rfc9111.html) — Tags: http, caching, api.
- <a id="s040"></a> **[S040] PostgreSQL Documentation.** PostgreSQL Global Development Group; 2026; 18 current. [https://www.postgresql.org/docs/18/](https://www.postgresql.org/docs/18/) — Tags: database, sql, transactions, indexes, concurrency, backup.
- <a id="s042"></a> **[S042] Redis Documentation.** Redis; 2026; Current. [https://redis.io/docs/latest/](https://redis.io/docs/latest/) — Tags: cache, rate-limiting, locks, streams, queues.
- <a id="s043"></a> **[S043] Designing Data-Intensive Applications, Second Edition.** Martin Kleppmann and Chris Riccomini / O'Reilly; 2025; 2nd edition. [https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/) — Tags: distributed-systems, databases, consistency, streams.
- <a id="s053"></a> **[S053] Site Reliability Engineering.** Google; 2016; Online book. [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/) — Tags: reliability, operations, monitoring, capacity.
- <a id="s055"></a> **[S055] Timeouts, Retries, and Backoff with Jitter.** AWS Builders' Library; 2026; Current article. [https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) — Tags: retries, timeouts, jitter, resilience.
- <a id="s137"></a> **[S137] ACM Queue: Idempotence Is Not a Medical Condition.** Pat Helland / ACM; 2012; ACM Queue. [https://queue.acm.org/detail.cfm?id=2187821](https://queue.acm.org/detail.cfm?id=2187821) — Tags: idempotency, distributed-systems, retries.
- <a id="s139"></a> **[S139] Redis distributed locks with Redis.** Redis; 2026; Current documentation. [https://redis.io/docs/latest/develop/use/patterns/distributed-locks/](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/) — Tags: distributed-locks, redis, leases.

---

**Paper metadata:** canonical subtopics: 12; layer: `primitives`; domain profile: `cache`; verified through: `2026-08-17`.
