---
paper_number: 38
title: "Rate Limiting"
layer: cross-cutting
domain_profile: cache
corpus_version: 1.0.0
verified_through: 2026-08-17
canonical_source: "original/Pasted text.txt"
subtopic_count: 15
status: production-engineering-reference
---

# 038. Rate Limiting

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Rate Limiting** exists to trade freshness and operational complexity for latency, throughput, and dependency isolation without changing correctness silently. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

A cache is a derived, disposable representation unless explicitly designed as a durable system of record. The owning domain defines key namespace, tenant scope, freshness, negative entries, serialization version, and fallback behavior. Never let cache reachability decide authorization without a bounded, secure source of truth.

The most important evidence base for this paper includes [S042](#s042) [S055](#s055) [S053](#s053). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- A cache is a derived copy with an explicit source of truth, staleness budget, invalidation mechanism, and failure mode.
- Cache keys are part of the security boundary and must include tenant, principal, locale, version, and policy context when those affect the value.
- TTL is not invalidation; it is only an upper bound on staleness under some conditions.
A saturated limiter store, clock drift between enforcer nodes, and bursty tenants dominate production behavior.
- Correctness must survive cache loss, partial outage, and eviction unless the cache is deliberately authoritative.

## 2. Scope and terminology map

The canonical topic list requires this paper to cover the following concerns. They are grouped only to expose relationships; no listed subtopic is omitted.

### Identity, trust, and access

**User limits**, **Token limits**, **Tenant limits**, **Token bucket**.

### Concurrency and distributed behavior

**IP limits**, **Endpoint limits**, **Global limits**, **Fixed window**, **Sliding window**, **Leaky bucket**, **Burst handling**, **Retry-after**, **Fail-open vs fail-closed**.

### Operations and observability

**Distributed rate limiting**, **Rate-limit headers**.

### Boundary of the paper

This paper treats **Rate Limiting** as a production subsystem or reusable reasoning primitive. It covers semantics, ownership, persistence, APIs, security, concurrency, distributed behavior, operations, evolution, and verification. Framework syntax and large implementation listings are intentionally excluded.

## 3. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S042](#s042) [S055](#s055) [S053](#s053)

1. **Invariant 1:** A cache is a derived copy with an explicit source of truth, staleness budget, invalidation mechanism, and failure mode.
2. **Invariant 2:** Cache keys are part of the security boundary and must include tenant, principal, locale, version, and policy context when those affect the value.
3. **Invariant 3:** TTL is not invalidation; it is only an upper bound on staleness under some conditions.
4. **Invariant 4:** A saturated limiter store, clock drift between enforcer nodes, and bursty tenants dominate production behavior.
5. **Invariant 5:** Correctness must survive cache loss, partial outage, and eviction unless the cache is deliberately authoritative.

Additional topic-specific invariants:

- **SHOULD — IP limits:** Define the exact semantics of **IP limits** within Rate Limiting: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST — Tenant limits:** Derive the tenant limit key from an authenticated, authorized binding; enforce tenant fairness quotas with burst allowances at shared infrastructure (edge/gateway/central limiter), not per-service best-effort. Make unscoped access to shared capacity difficult or impossible.
- **SHOULD — Fixed window:** Choose identity/scope, algorithm, burst capacity, window clock, atomic update, distributed consistency, response headers, and fail behavior according to the abuse and availability threat.
- **SHOULD — Token bucket:** Choose identity/scope, algorithm, burst capacity, window clock, atomic update, distributed consistency, response headers, and fail behavior according to the abuse and availability threat.
- **SHOULD — Burst handling:** Define the exact semantics of **Burst handling** within Rate Limiting: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Fail-open vs fail-closed:** Define the exact semantics of **Fail-open vs fail-closed** within Rate Limiting: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.

## 4. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Fixed/sliding window vs token bucket | Window algorithms differ in burst accuracy, state cost, and distributed atomicity; token buckets model sustained rate plus burst. | Choose by abuse model and fairness; document partition/fail-open behavior. |
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

### 7.1. IP limits

- **SHOULD — engineering rule:** Treat IP as a coarse, secondary dimension only: CGNAT/NAT shares thousands of users behind one address and mobile handoffs rotate IPs, so apply coarse IP tiers to anonymous abuse surfaces while authenticated traffic gets identity-based limits; fix IPv6 granularity (/64 vs host) and trusted-proxy extraction before trusting any IP key.
- **Production failure mode:** A strict per-IP cap locks out an entire office or carrier block behind NAT while a bot farm on rotating residential IPs stays under threshold.
- **Existing-codebase evidence:** Locate where the client IP is extracted (trusted proxy chain? spoofable X-Forwarded-For?) and whether anonymous endpoints get IP tiers distinct from identity limits.

### 7.2. User limits

- **MUST — engineering rule:** Key primary limits on the authenticated principal derived after authentication/authorization — never from client-supplied headers, query parameters, or body fields; bound per-principal limiter state with TTL/eviction so key cardinality cannot be weaponized.
- **Production failure mode:** Limits keyed on unverified `user_id` parameters let attackers rotate fake identities for unlimited budget while a spoofed victim inherits their consumption.
- **Existing-codebase evidence:** Trace each limit-key construction back to the verified session/token claim; flag keys built from request-controlled values.

### 7.3. Token limits

- **MUST — engineering rule:** For API-key/token credentials, scope limits per credential AND per owning account (aggregate ceiling across all of an account's keys) with separate tiers for machine traffic; revocation and expiry must invalidate limiter participation promptly.
- **Production failure mode:** Per-key limits without an account ceiling let one customer mint hundreds of keys, each legitimately under its cap, multiplying real consumption.
- **Existing-codebase evidence:** Check whether limiter keys embed account/tenant alongside the credential; test that a revoked key stops consuming budget immediately.

### 7.4. Tenant limits

- **MUST — engineering rule:** Derive the limit key from authenticated tenant identity; the purpose is fairness — stop one tenant from consuming shared capacity (noisy neighbor) — via per-tier quotas with burst allowances enforced at shared infrastructure (edge/gateway/central limiter), not per-service best-effort.
- **Production failure mode:** One tenant's bulk import degrades latency for every tenant because per-service caps never observe aggregate cross-endpoint consumption.
- **Existing-codebase evidence:** Identify where tenant quotas are enforced and whether they cover aggregates across endpoints; burst one tenant to quota while measuring neighboring tenants' latency and confirming their budgets stay untouched.

### 7.5. Endpoint limits

- **SHOULD — engineering rule:** Price endpoints differently — expensive search is not a cheap GET: assign cost tiers or weights per route (requests consume proportional token cost) so heavy routes get stricter budgets without strangling light ones.
- **Production failure mode:** Uniform per-route limits either starve a cheap high-QPS read path or let one expensive aggregation consume the resources of hundreds of cheap calls.
- **Existing-codebase evidence:** Compare configured per-route limits against measured per-route cost (CPU/database time); flag routes where limit and cost diverge by orders of magnitude.

### 7.6. Global limits

- **MUST — engineering rule:** Keep a global ceiling protecting shared infrastructure (total requests/sec, total concurrent expensive operations) beneath all per-identity limits; global state requires atomic distributed counters, so decide its accuracy and availability budget explicitly.
- **Production failure mode:** Every per-user limit passes while aggregate demand exceeds capacity; the origin collapses without any individual limit ever tripping.
- **Existing-codebase evidence:** Verify a global guard exists upstream of per-identity checks; load-test aggregate-at-limit conditions and record which layer sheds first.

### 7.7. Fixed window

- **SHOULD — engineering rule:** Count requests per (key, window start) with an atomic increment-and-check; simple and memory-cheap, but it allows 2x limit at window boundaries — a client can spend its full quota in the last seconds of window N and again immediately in N+1.
- **Production failure mode:** Boundary bursts double instantaneous load exactly at rollover; cron-like traffic aligned to wall-clock windows amplifies the spike.
- **Existing-codebase evidence:** Drive burst-then-sustained load across a boundary and record accepted counts; verify increments are atomic under concurrency (no read-modify-write races).

### 7.8. Sliding window

- **SHOULD — engineering rule:** Sliding window LOG stores per-request timestamps — exact but O(requests) memory per key; sliding window COUNTER approximates with a weighted blend of current + previous window (weight = elapsed fraction) — memory-cheap, but the uniformity assumption makes it overcount (under-admit) when previous-window traffic clustered early in its window and undercount (over-admit) when clustered at the boundary, with worst-case overshoot approaching the fixed-window 2x spike under adversarial end-of-window clustering.
- **Production failure mode:** Log variants leak memory on high-cardinality keys when timestamp lists go unpruned; counter variants quietly over-admit under skewed, bursty traffic patterns.
- **Existing-codebase evidence:** Identify which sliding variant ships; measure memory per active key and pruning behavior; compare accepted counts against an exact reference under bursty traces.

### 7.9. Token bucket

- **SHOULD — engineering rule:** Bucket capacity b, refill rate r tokens/sec; each request consumes token(s); refill computes tokens = min(b, tokens + r * dt) atomically at check time; allows burst b with a sustained rate r — the most common choice for API limiting.
- **Production failure mode:** Non-atomic read-compute-write on tokens loses refills under concurrency (two requests both see full buckets); b and r copied from defaults mismatch real endpoint cost.
- **Existing-codebase evidence:** Confirm refill-and-consume is a single atomic operation per key (Lua script, compare-and-set, or mutex); verify b and r per tier against documented quotas.

### 7.10. Leaky bucket

- **SHOULD — engineering rule:** Distinguish the two shapes consciously: leaky bucket AS METER (constant outflow equivalent to a token bucket; smooths observed rate) vs AS QUEUE (buffers requests in a bounded FIFO drained at constant rate — adds queuing latency and can mask overload by hiding demand behind the queue).
- **Production failure mode:** Queue-mode absorbs an overload attack as growing latency instead of rejecting; queues fill memory while dashboards look healthy and every served request is late.
- **Existing-codebase evidence:** Determine whether the implementation rejects immediately or buffers; if buffering, find the queue bound, overflow behavior, and the added p99 latency.

### 7.11. Distributed rate limiting

- **SHOULD — engineering rule:** A centralized atomic counter store (Redis Lua check-and-decrement) gives exactness at the cost of a round-trip per request and makes the store's availability yours; periodic-sync local approximate counters avoid the hot path but over-admit between syncs — bound the error (sync interval x drift) and document it; sticky routing trades rebalancing pain for locally atomic counters.
- **Production failure mode:** The counter store becomes a write hotspot; when it slows, either every request queues behind it (a synchronous dependency you built yourself) or fail-open silently disables all limits.
- **Existing-codebase evidence:** Identify limiter placement (edge/gateway/service) and store topology; measure limiter-store p99, compute worst-case between-sync over-admission, and confirm the documented store-outage fail mode.

### 7.12. Burst handling

- **SHOULD — engineering rule:** Model bursts explicitly: size burst capacity (bucket depth or window headroom) above legitimate client concurrency (page loads fire parallel requests), with sustained rate below it; absorb micro-bursts and reject sustained excess rather than punishing every parallel page-load.
- **Production failure mode:** A zero-burst window limiter rejects legitimate concurrent first-page fan-out (auth + profile + preferences in one sweep), producing mystery 429s on login.
- **Existing-codebase evidence:** Replay realistic client startup bursts against the limiter; tune burst capacity until legitimate fan-out passes while sustained abuse still trips.

### 7.13. Retry-after

- **MUST — engineering rule:** Response contract: rejections return 429 + Retry-After (delta-seconds or HTTP-date) computed from the key's refill time — when enough budget regenerates — not a constant; the limiter emits it and clients honor it; forwarding an upstream provider's Retry-After unchanged is a separate passthrough path.
- **Production failure mode:** Constant or absent Retry-After turns throttling into hammering (clients poll on their own cadence) or freezes clients far longer than the actual refill horizon.
- **Existing-codebase evidence:** Verify every 429 carries Retry-After consistent with the key's refill math; check clients parse delta-seconds AND HTTP-date forms and clamp honored delays to their deadlines.

### 7.14. Rate-limit headers

- **SHOULD — engineering rule:** Expose remaining-budget headers consistently (standardized RateLimit-/Retry-After family or documented legacy X-RateLimit-*): limit, remaining, reset — on BOTH successes and 429s so well-behaved clients self-throttle before hitting the wall; document header semantics publicly and keep them stable across gateways.
- **Production failure mode:** Headers emitted only on 429 give clients no proactive signal; inconsistent names across gateways force parsing hacks that break silently on rename.
- **Existing-codebase evidence:** Snapshot emitted headers per route and status; confirm remaining/reset update correctly mid-window and documentation matches the wire format.

### 7.15. Fail-open vs fail-closed

- **MUST — engineering rule:** When the limiter store is down, behavior must be documented PER ENDPOINT CLASS: auth/login endpoints usually fail closed (brute-force protection must not vanish); general read paths often fail open with alerting; record the decision matrix in reviewable configuration and monitor both paths.
- **Production failure mode:** Default-fail-open middleware silently disables login throttling during a cache outage, handing attackers a brute-force window exactly when defenses are down.
- **Existing-codebase evidence:** Simulate a limiter-store outage per endpoint class and observe the documented fail mode; confirm alerts fire on fail-open decisions and the decision matrix exists.

## 8. Concurrency, transactions, idempotency, and consistency

Cache-aside has windows after writes and on failed invalidation. Versioned or generational keys avoid some delete races; write-through/write-behind introduce their own commit ordering. Stampede protection must prevent stale lock holders and bound waiting. Quotas and rate limits need atomic distributed operations when global accuracy matters.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Rate Limiting path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `IP limits`, `Endpoint limits`, `Sliding window`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Centralized vs local counters | A shared store gives one truth but adds a round-trip and a new failure point; local approximate counters over-admit between syncs. | Bound the over-admission error, document the fail-open/fail-closed decision per endpoint class, and monitor counter-store latency as a dependency. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Rate Limiting; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 15. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Rate Limiting** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **IP limits**: Define the exact semantics of **IP limits** within Rate Limiting: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **Tenant limits**: Derive the limit key from authenticated tenant identity and enforce per-tier quotas with burst allowances at shared infrastructure so one noisy tenant cannot consume shared capacity at the expense of others.
- **MUST** — For **Fixed window**: Choose identity/scope, algorithm, burst capacity, window clock, atomic update, distributed consistency, response headers, and fail behavior according to the abuse and availability threat.
- **MUST** — For **Token bucket**: Choose identity/scope, algorithm, burst capacity, window clock, atomic update, distributed consistency, response headers, and fail behavior according to the abuse and availability threat.

### SHOULD

- **SHOULD** — A cache is a derived copy with an explicit source of truth, staleness budget, invalidation mechanism, and failure mode.
- **SHOULD** — Cache keys are part of the security boundary and must include tenant, principal, locale, version, and policy context when those affect the value.
- **SHOULD** — TTL is not invalidation; it is only an upper bound on staleness under some conditions.
A saturated limiter store, clock drift between enforcer nodes, and bursty tenants dominate production behavior.
- **SHOULD** — Correctness must survive cache loss, partial outage, and eviction unless the cache is deliberately authoritative.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Choose **Fixed/sliding window vs token bucket** according to the stated trade-off: Choose by abuse model and fairness; document partition/fail-open behavior.
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
Synchronize concurrent limiter decisions and verify fail-mode behavior, budget accounting under races, and tenant
- [ ] Test hot keys, negative caching, TTL jitter, lock expiry, and origin overload at production concurrency.
- [ ] Roll old and new key/value formats together without a global flush; verify rollback parsing.
- [ ] Inject stale authorization or quota data and prove the documented fail-open/fail-closed behavior.
- [ ] **IP limits:** Locate every implementation path for ip limits, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Tenant limits:** Identify limiter placement (edge/gateway/service); drive one tenant from burst into sustained load until throttled and verify neighboring tenants keep full budgets, unaffected latency, and 429s carrying Retry-After.
- [ ] **Fixed window:** Test simultaneous requests across nodes, clock skew, key eviction, backend failure, IPv6/proxy identity, and Retry-After semantics.
- [ ] **Token bucket:** Test simultaneous requests across nodes, clock skew, key eviction, backend failure, IPv6/proxy identity, and Retry-After semantics.
- [ ] **Burst handling:** Locate every implementation path for burst handling, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Fail-open vs fail-closed:** Locate every implementation path for fail-open vs fail-closed, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 17. Common production bugs and incorrect implementations

- Cross-tenant cache key collision.
- Stale value resurrected after invalidation.
- Stampede after common expiry.
- Unbounded cache cardinality from user input.
- Cache outage taking down the source database.
- **IP limits:** A framework or provider default for ip limits is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Token limits:** A framework or provider default for token limits is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Global limits:** A framework or provider default for global limits is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Sliding window:** Window-boundary bursts, racey counters, NAT collateral damage, or fail-open behavior allow abuse; fail-closed can create an outage.
- **Leaky bucket:** Window-boundary bursts, racey counters, NAT collateral damage, or fail-open behavior allow abuse; fail-closed can create an outage.
- **Retry-after:** Throttled clients ignore Retry-After and hammer the limiter, converting soft throttling into sustained overload; or emitted Retry-After values are unrelated to the actual refill time of the key.
- **Fail-open vs fail-closed:** A framework or provider default for fail-open vs fail-closed is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.

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

- What exact invariant or user/system promise makes **Rate Limiting** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- For **IP limits**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for ip limits is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Tenant limits**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: One tenant consumes shared capacity until neighbors are throttled or degraded because enforcement is per-service best-effort instead of shared infrastructure.
- For **Fixed window**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Window-boundary bursts, racey counters, NAT collateral damage, or fail-open behavior allow abuse; fail-closed can create an outage.
- For **Token bucket**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Window-boundary bursts, racey counters, NAT collateral damage, or fail-open behavior allow abuse; fail-closed can create an outage.
- For **Burst handling**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for burst handling is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- How stale may each value be, and what happens when invalidation, fill, or the cache itself fails?

## 20. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Rate Limiting**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] **IP limits:** Locate every implementation path for ip limits, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Token limits:** Locate every implementation path for token limits, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Global limits:** Locate every implementation path for global limits, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Sliding window:** Test simultaneous requests across nodes, clock skew, key eviction, backend failure, IPv6/proxy identity, and Retry-After semantics.
- [ ] **Leaky bucket:** Test simultaneous requests across nodes, clock skew, key eviction, backend failure, IPv6/proxy identity, and Retry-After semantics.
- [ ] **Retry-after:** Verify every 429 response carries a Retry-After derived from the key refill time and that documented client/SDK behavior honors it instead of polling.
- [ ] **Fail-open vs fail-closed:** Locate every implementation path for fail-open vs fail-closed, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] Enumerate key builders and invalidation publishers; compare tenant, locale, auth, schema, and environment dimensions.

## 21. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [039. Quotas](../primitives/039-quotas.md) — layer: `primitives`; profile: `cache`.
- [037. Caching](../systems/037-caching.md) — layer: `systems`; profile: `cache`.
- [067. Abuse Protection](067-abuse-protection.md) — layer: `cross-cutting`; profile: `security`.
- [146. Cross-Cutting Implementation Checklist](146-cross-cutting-implementation-checklist.md) — layer: `cross-cutting`; profile: `checklist`.
- [096. Scalability](096-scalability.md) — layer: `cross-cutting`; profile: `performance`.
- [131. Distributed Cache Coordination](131-distributed-cache-coordination.md) — layer: `cross-cutting`; profile: `cache`.
- [052. Retry Engineering](../primitives/052-retry-engineering.md) — layer: `primitives`; profile: `resilience`.
- [036. Idempotency](../primitives/036-idempotency.md) — layer: `primitives`; profile: `transactions`.
- [028. Query Design](../systems/028-query-design.md) — layer: `systems`; profile: `data_model`.
- [010. Multi-Tenancy](../systems/010-multi-tenancy.md) — layer: `systems`; profile: `authorization`.
- [104. Backpressure](104-backpressure.md) — layer: `cross-cutting`; profile: `resilience`.
- [055. Resilience](055-resilience.md) — layer: `cross-cutting`; profile: `resilience`.

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

**Paper metadata:** canonical subtopics: 15; layer: `cross-cutting`; domain profile: `cache`; verified through: `2026-08-17`.
