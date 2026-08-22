---
paper_number: 52
title: "Retry Engineering"
layer: primitives
domain_profile: resilience
corpus_version: 1.0.0
verified_through: 2026-08-17
canonical_source: "original/Pasted text.txt"
subtopic_count: 11
status: production-engineering-reference
---

# 052. Retry Engineering

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Retry Engineering** exists to bound the blast radius and resource cost of partial failure while preserving useful service. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

Resilience policy belongs at each dependency boundary and at the end-to-end request budget. A library default cannot know whether an operation is retryable, idempotent, latency-sensitive, or safety-critical. Coordinate retries, timeouts, circuit breakers, bulkheads, admission control, and fallbacks so one layer does not defeat another.

The most important evidence base for this paper includes [S053](#s053) [S054](#s054) [S055](#s055) [S056](#s056). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Timeouts, retries, concurrency limits, backpressure, and circuit breakers must be designed together.
- A timeout is an ambiguous outcome: the remote side may have completed the operation.
- Retries are load multipliers and must be budgeted across call layers.
- Fallbacks can return stale or lower-quality data, but they must not weaken security or silently corrupt state.
- Graceful degradation requires a predefined reduced contract, not ad hoc exception swallowing.

## 2. Scope and terminology map

The canonical topic list requires this paper to cover the following concerns. They are grouped only to expose relationships; no listed subtopic is omitted.

### Concurrency and distributed behavior

**Retryable operations**, **Non-retryable operations**, **Retry count**, **Exponential backoff**, **Retry budgets**, **Retry storms**, **Retry-after handling**.

### Operations and observability

**Jitter**, **Duplicate side effects**, **Nested retries**, **Client + server retries**.

### Boundary of the paper

This paper treats **Retry Engineering** as a production subsystem or reusable reasoning primitive. It covers semantics, ownership, persistence, APIs, security, concurrency, distributed behavior, operations, evolution, and verification. Framework syntax and large implementation listings are intentionally excluded.

## 3. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S053](#s053) [S054](#s054) [S055](#s055) [S056](#s056)

1. **Invariant 1:** Timeouts, retries, concurrency limits, backpressure, and circuit breakers must be designed together.
2. **Invariant 2:** A timeout is an ambiguous outcome: the remote side may have completed the operation.
3. **Invariant 3:** Retries are load multipliers and must be budgeted across call layers.
4. **Invariant 4:** Fallbacks can return stale or lower-quality data, but they must not weaken security or silently corrupt state.
5. **Invariant 5:** Graceful degradation requires a predefined reduced contract, not ad hoc exception swallowing.

Additional topic-specific invariants:

- **SHOULD — Retryable operations:** Classify retryable outcomes, cap attempts and elapsed time, use exponential backoff with jitter, honor provider pushback, and make side effects idempotent or detect ambiguous completion.
- **SHOULD — Retry count:** Classify retryable outcomes, cap attempts and elapsed time, use exponential backoff with jitter, honor provider pushback, and make side effects idempotent or detect ambiguous completion.
- **SHOULD — Jitter:** Classify retryable outcomes, cap attempts and elapsed time, use exponential backoff with jitter, honor provider pushback, and make side effects idempotent or detect ambiguous completion.
- **SHOULD — Duplicate side effects:** Define the exact semantics of **Duplicate side effects** within Retry Engineering: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Nested retries:** Define the exact semantics of **Nested retries** within Retry Engineering: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Retry-after handling:** Classify retryable outcomes, cap attempts and elapsed time, use exponential backoff with jitter, honor provider pushback, and make side effects idempotent or detect ambiguous completion.

## 4. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Deterministic backoff vs jittered backoff | Deterministic retries synchronize clients; jitter spreads recovery load but changes latency variance. | Use bounded exponential backoff with jitter and a total retry budget. |
| Retry vs fail fast | Retry can mask transient failures but amplifies overload and duplicates side effects. | Retry only classified transient failures within a deadline and budget. |
| Client vs service-mesh retry | Client retries know operation semantics; mesh retries are uniform but may not know idempotency. | Keep semantic retry policy with the caller and use infrastructure retries narrowly. |
| Circuit breaker vs concurrency limiter | Breakers react to failure rate; limiters prevent overload before failure. | Use both when appropriate and monitor their states. |
| Fallback vs explicit degradation | Fallback may hide stale or incomplete results; explicit degradation preserves transparency. | Expose degradation in response metadata, health, and metrics when it affects behavior. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 5. Ownership, state, and lifecycle

A call consumes a finite deadline across admission, queueing, connect, write, server processing, read, retries, and fallback. Circuit breakers move `closed → open → half_open → closed|open`; queued work moves toward success, rejection, expiry, or shedding. State changes must be observable and bounded.

```mermaid
stateDiagram-v2
    admitted --> attempt --> success
    attempt --> retryable_failure --> backoff --> attempt
    attempt --> nonretryable_failure
    attempt --> deadline_exhausted
    closed_breaker --> open_breaker --> half_open --> closed_breaker
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 6. Data model and API implications

Classify errors by retryability and outcome certainty. Define per-attempt timeout, overall deadline, maximum attempts, backoff/jitter, retry budget, concurrency limit, fallback semantics, and cancellation propagation. A fallback must be a valid degraded product behavior, not stale or fabricated success.

A production representation commonly needs the following fields or equivalent evidence:

- logical operation ID and attempt number.
- overall deadline and per-attempt phase timings.
- retry classification, budget, backoff, and outcome certainty.
- circuit/bulkhead/admission state and fallback decision.
- idempotency or outcome-reconciliation reference for side-effecting calls.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 7. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### 7.1. Retryable operations

- **MUST — engineering rule:** Classify outcomes before any retry logic exists: connection-refused and pre-send failures are retryable; a timeout after the request was sent is an AMBIGUOUS outcome (the operation may have succeeded), so retrying it requires an idempotency mechanism ([036. Idempotency](036-idempotency.md)); HTTP 5xx is generally retryable except non-idempotent side effects without idempotency keys; 408 is retryable; 429 is retried only while honoring Retry-After; every other 4xx is non-retryable; DNS/network-unreachable is retryable with an attempt cap.
- **Production failure mode:** A blanket retry-on-any-error path loops forever on validation and authorization failures, and a timeout treated as plain failure duplicates a payment that actually committed.
- **Existing-codebase evidence:** Extract the error classes each client maps today (connect, TLS, timeout, 5xx, 429, 408, other 4xx) and inject one of each; verify every class lands in an explicit retryable/ambiguous/non-retryable terminal path.

### 7.2. Non-retryable operations

- **MUST — engineering rule:** Fail fast on non-retryable classes — all 4xx except 408 and 429, authentication/authorization rejections, validation failures, and business-rule refusals — routing them to the caller or dead-letter path on the first attempt; never map them onto a backoff schedule because a client error repeats identically.
- **Production failure mode:** Retrying a 403/422 burns the attempt budget and the deadline, delays the real error to the caller, and multiplies load against a dependency that answered correctly the first time.
- **Existing-codebase evidence:** List the exception types and status codes each retry wrapper treats as retryable; confirm non-retryable classes short-circuit before any sleep and that no broad catch-all re-enqueues them.

### 7.3. Retry count

- **MUST — engineering rule:** Cap attempts (typically 2-3 retries after the initial try) and total elapsed time; on exhaustion, surface the final error with full context (attempt count, last outcome class, correlation ID); park asynchronous work in a DLQ/dead-letter state; alert on retry-rate spikes and exhaustion counters; never swallow-and-continue silently.
- **Production failure mode:** Uncapped retry loops pin threads, connections, and in-flight money-moving operations, while the final failure is logged at DEBUG or swallowed after the last attempt, so nothing alerts and orders silently disappear.
- **Existing-codebase evidence:** Find retry loops without caps (bare while loops, recursive self-invocation, default library policies); confirm an exhaustion metric and alert exist and the surfaced error preserves root cause and attempt metadata.

### 7.4. Exponential backoff

- **SHOULD — engineering rule:** Space attempts with sleep = min(cap, base * 2^attempt); choose base and cap from the dependency's realistic recovery horizon and keep the total retry window inside the caller's remaining deadline.
- **Production failure mode:** Plain exponential backoff WITHOUT jitter synchronizes failed callers into waves (thundering herd): everyone fails together, sleeps on the identical schedule, and reconnects together, repeatedly re-overloading the recovering service.
- **Existing-codebase evidence:** Recompute the delay sequence from configured base and cap and confirm doubling, capping, and deadline fit; flag any fixed-interval retry schedule.

### 7.5. Jitter

- **SHOULD — engineering rule:** Randomize every backoff sleep. Full jitter — sleep = random_between(0, min(cap, base * 2^attempt)) — is the AWS-recommended default with the best tail behavior ([S055](#s055)); equal jitter — min(cap, base * 2^attempt)/2 + random(0, min(cap, base * 2^attempt)/2) — when the delay needs a floor; decorrelated jitter — sleep = min(cap, random(base, prev_sleep * 3)) — when fleets restart in waves.
- **Production failure mode:** Missing jitter reproduces synchronized retry waves with growing amplitude: thousands of clients hit the dependency in lockstep each interval and recovery never converges despite backoff.
- **Existing-codebase evidence:** Locate the delay computation and verify a per-attempt random component exists (many generated clients ship deterministic backoff by default); simulate N concurrently failed callers and measure retry arrival spread.

### 7.6. Retry budgets

- **SHOULD — engineering rule:** Cap total retries as a share of traffic with a token bucket (for example, retries <= 10% of requests per minute window); when the budget is empty, fail fast instead of retrying; track the retry ratio as an SLO signal because a rising ratio marks the transition from partial outage toward total outage.
- **Production failure mode:** Unbudgeted retries multiply a 20% dependency failure rate into multiples of the original load; retry traffic crowds out fresh successful work so the dependency never drains and recovers.
- **Existing-codebase evidence:** Check for a per-dependency retry-budget/token-bucket setting (hand-rolled loops almost never have one); export retry attempts separately from first attempts so monitoring can compute the ratio.

### 7.7. Duplicate side effects

- **MUST — engineering rule:** Idempotency precondition: non-idempotent operations (payment POST, resource creation, message publish) need idempotency keys issued and durably stored BEFORE any retry logic exists; retries reuse the same key so replays converge on the first outcome (paper 036).
- **Production failure mode:** A lost response after commit triggers a keyless retry; the provider charges twice or the message publishes twice, and reconciliation finds the duplicate days later.
- **Existing-codebase evidence:** Search for retries around non-idempotent calls without keys (charge APIs, POST submits, publishes); verify one key per logical operation — generated once and reused across attempts, not one per attempt.

### 7.8. Retry storms

- **MUST — engineering rule:** Bound amplification by construction: 3 layers x 3 attempts each = up to 27 calls per user action; assign exactly one retry owner per layer, propagate deadlines so child retries cannot outlive the parent deadline, and gate aggregate retries behind the retry budget.
- **Production failure mode:** During a dependency outage every layer retries independently; multiplicative amplification stacks synchronized waves on top of each other and turns a brownout into a total outage.
- **Existing-codebase evidence:** Draw the call graph and multiply retry counts and deadlines across client, gateway, service, SDK, and worker layers; flag any path whose worst-case attempts exceed the parent deadline or that lacks a single retry owner.

### 7.9. Nested retries

- **MUST — engineering rule:** Never stack invisible retry policies: an inner SDK retry inside an outer service retry multiplies attempts; pin inner/library defaults to zero or one retry, keep semantic policy at one layer, and make any deliberate nesting explicit and deadline-aware.
- **Production failure mode:** A library default (often 3 attempts, no jitter) hides beneath the outer policy; measured p99 explodes and the outage amplifies by the hidden multiplier exactly when the dependency is weakest.
- **Existing-codebase evidence:** Grep for nested retry configurations across client/gateway/service layers (SDK defaults, mesh retry policy, database driver retry, HTTP middleware) and reconcile them under one declared owner.

### 7.10. Client + server retries

- **SHOULD — engineering rule:** Assign ownership explicitly: the client owns operation-semantics retries (idempotent replay with keys); server and mesh retries handle only transport-level, provably-safe classes; when both exist, combine budgets so the same failure is never retried independently by both sides.
- **Production failure mode:** The server retries successfully after the client already gave up; the client retries again, so one logical operation executes twice against a non-idempotent endpoint.
- **Existing-codebase evidence:** Inventory mesh/gateway retry policies alongside client-library policies for the same route; verify combined worst-case attempts stay inside budget and response-lost-after-commit resolves via idempotency/outcome lookup rather than blind retry.

### 7.11. Retry-after handling

- **MUST — engineering rule:** Retry-After precedence: a server-provided delay (delta-seconds or HTTP-date on 429/503) overrides the locally computed backoff; if the header is absent on 429/503, fall back to exponential backoff with jitter anyway; clamp the honored delay to the remaining deadline and budget, and scope it to the affected credential, not the whole process.
- **Production failure mode:** Ignoring Retry-After converts temporary throttling into bans and blacklists; honoring it process-wide freezes unrelated background work that merely shares the scheduler with the throttled endpoint.
- **Existing-codebase evidence:** Check the 429/503 handler reads Retry-After before computing a local delay; verify both header forms parse, values are clamped to deadline/budget, and ignored-or-clamped events are counted.

## 8. Concurrency, transactions, idempotency, and consistency

Retries can duplicate side effects; timeouts do not cancel already-committed work. Use idempotency and outcome lookup for ambiguous writes. Bulkheads and bounded queues preserve resources; unbounded retries and queues convert transient dependency failures into system-wide overload.

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

Expect slow success, partial response, connection reset after commit, synchronized client retry, breaker oscillation, stale health data, and fallback overload. Shed early before exhausting pools. Prefer explicit unavailable/degraded responses over silent corruption.

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

Measure attempts per logical operation, deadline budget consumed, timeout phase, breaker state, rejection/shed count, retry-budget exhaustion, fallback use, queue depth, saturation, and dependency-tail latency. Alert on correlated symptoms rather than every individual failure.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 13. Compatibility, schema evolution, migration, deployment, and rollback

Policy changes alter traffic and failure behavior, so roll them out progressively. Mixed versions with different retry counts can multiply load. Keep emergency kill switches for retries/fallbacks and verify rollback against requests already in flight.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Retry Engineering path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Retryable operations`, `Retry count`, `Retry budgets`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Retry Engineering; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 15. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Retry Engineering** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Retryable operations**: Classify retryable outcomes, cap attempts and elapsed time, use exponential backoff with jitter, honor provider pushback, and make side effects idempotent or detect ambiguous completion.
- **MUST** — For **Retry count**: Classify retryable outcomes, cap attempts and elapsed time, use exponential backoff with jitter, honor provider pushback, and make side effects idempotent or detect ambiguous completion.
- **MUST** — For **Jitter**: Classify retryable outcomes, cap attempts and elapsed time, use exponential backoff with jitter, honor provider pushback, and make side effects idempotent or detect ambiguous completion.
- **MUST** — For **Duplicate side effects**: Define the exact semantics of **Duplicate side effects** within Retry Engineering: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.

### SHOULD

- **SHOULD** — Timeouts, retries, concurrency limits, backpressure, and circuit breakers must be designed together.
- **SHOULD** — A timeout is an ambiguous outcome: the remote side may have completed the operation.
- **SHOULD** — Retries are load multipliers and must be budgeted across call layers.
- **SHOULD** — Fallbacks can return stale or lower-quality data, but they must not weaken security or silently corrupt state.
- **SHOULD** — Graceful degradation requires a predefined reduced contract, not ad hoc exception swallowing.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Choose **Deterministic backoff vs jittered backoff** according to the stated trade-off: Use bounded exponential backoff with jitter and a total retry budget.
- **MAY** — Adopt the **Retry vs fail fast** option that fits the workload and ownership boundary; Retry only classified transient failures within a deadline and budget.
- **MAY** — Adopt the **Client vs service-mesh retry** option that fits the workload and ownership boundary; Keep semantic retry policy with the caller and use infrastructure retries narrowly.
- **MAY** — Adopt the **Circuit breaker vs concurrency limiter** option that fits the workload and ownership boundary; Use both when appropriate and monitor their states.

### AVOID

- **AVOID** — Retry storm during dependency outage.
- **AVOID** — Nested retries exceeding request deadline.
- **AVOID** — Circuit breaker shared across unrelated tenants/endpoints.
- **AVOID** — Timeout without canceling downstream work.
- **AVOID** — Fallback bypassing authorization.
- **AVOID** — Stacking retries in every layer.
- **AVOID** — Using infinite/default timeouts.
- **AVOID** — Retrying ambiguous writes without keys.

### NEVER

- **NEVER** — Never use infinite timeouts or unbounded retries/queues.
- **NEVER** — Never retry an ambiguous side-effecting operation without idempotency or outcome reconciliation.
- **NEVER** — Never let fallback invent a successful authoritative result.

## 16. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Inject connect, TLS, write, first-byte, mid-body, and slow-success failures; verify phase-specific timeout and outcome handling.
- [ ] Run retry storms from multiple client/server layers and prove retry budgets, jitter, admission control, and idempotency bound amplification.
- [ ] Exercise breaker thresholds, half-open probes, oscillation, dependency recovery, and stale distributed state.
- [ ] Saturate each pool/queue independently and together; verify bounded memory, load shedding, and useful degraded behavior.
- [ ] Cancel requests at each stage and confirm resource release and no unsafe duplicate side effect.
- [ ] **Retryable operations:** Inject each error class and verify attempt count, schedule, deadline budget, duplicate behavior, and terminal routing.
- [ ] **Retry count:** Inject each error class and verify attempt count, schedule, deadline budget, duplicate behavior, and terminal routing.
- [ ] **Jitter:** Inject each error class and verify attempt count, schedule, deadline budget, duplicate behavior, and terminal routing.
- [ ] **Duplicate side effects:** Locate every implementation path for duplicate side effects, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Nested retries:** Locate every implementation path for nested retries, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Retry-after handling:** Inject each error class and verify attempt count, schedule, deadline budget, duplicate behavior, and terminal routing.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 17. Common production bugs and incorrect implementations

- Retry storm during dependency outage.
- Nested retries exceeding request deadline.
- Circuit breaker shared across unrelated tenants/endpoints.
- Timeout without canceling downstream work.
- Fallback bypassing authorization.
- **Retryable operations:** Permanent failures loop forever, retries synchronize into a storm, or a timed-out successful operation is duplicated.
- **Retry count:** Permanent failures loop forever, retries synchronize into a storm, or a timed-out successful operation is duplicated.
- **Exponential backoff:** Permanent failures loop forever, retries synchronize into a storm, or a timed-out successful operation is duplicated.
- **Retry budgets:** Permanent failures loop forever, retries synchronize into a storm, or a timed-out successful operation is duplicated.
- **Retry storms:** Permanent failures loop forever, retries synchronize into a storm, or a timed-out successful operation is duplicated.
- **Nested retries:** A framework or provider default for nested retries is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Retry-after handling:** Permanent failures loop forever, retries synchronize into a storm, or a timed-out successful operation is duplicated.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Stacking retries in every layer.
- Using infinite/default timeouts.
- Retrying ambiguous writes without keys.
- Adding unbounded queues to hide overload.
- Returning stale fallback as successful truth.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Retry Engineering** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- For **Retryable operations**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Permanent failures loop forever, retries synchronize into a storm, or a timed-out successful operation is duplicated.
- For **Retry count**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Permanent failures loop forever, retries synchronize into a storm, or a timed-out successful operation is duplicated.
- For **Jitter**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Permanent failures loop forever, retries synchronize into a storm, or a timed-out successful operation is duplicated.
- For **Duplicate side effects**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for duplicate side effects is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Nested retries**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for nested retries is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- How many total attempts can one user request trigger across every layer during an outage?

## 20. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Retry Engineering**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] **Retryable operations:** Inject each error class and verify attempt count, schedule, deadline budget, duplicate behavior, and terminal routing.
- [ ] **Retry count:** Inject each error class and verify attempt count, schedule, deadline budget, duplicate behavior, and terminal routing.
- [ ] **Exponential backoff:** Inject each error class and verify attempt count, schedule, deadline budget, duplicate behavior, and terminal routing.
- [ ] **Retry budgets:** Inject each error class and verify attempt count, schedule, deadline budget, duplicate behavior, and terminal routing.
- [ ] **Retry storms:** Inject each error class and verify attempt count, schedule, deadline budget, duplicate behavior, and terminal routing.
- [ ] **Nested retries:** Locate every implementation path for nested retries, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Retry-after handling:** Inject each error class and verify attempt count, schedule, deadline budget, duplicate behavior, and terminal routing.
- [ ] Draw the full call graph and multiply retry counts/deadlines across client, proxy, service, SDK, and worker layers.

## 21. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [051. External Integrations](../systems/051-external-integrations.md) — layer: `systems`; profile: `resilience`.
- [053. Timeout Engineering](053-timeout-engineering.md) — layer: `primitives`; profile: `resilience`.
- [104. Backpressure](../cross-cutting/104-backpressure.md) — layer: `cross-cutting`; profile: `resilience`.
- [055. Resilience](../cross-cutting/055-resilience.md) — layer: `cross-cutting`; profile: `resilience`.
- [054. Circuit Breakers](054-circuit-breakers.md) — layer: `primitives`; profile: `resilience`.
- [043. Background Jobs](../systems/043-background-jobs.md) — layer: `systems`; profile: `async`.
- [146. Cross-Cutting Implementation Checklist](../cross-cutting/146-cross-cutting-implementation-checklist.md) — layer: `cross-cutting`; profile: `checklist`.
- [093. Failure Testing](../cross-cutting/093-failure-testing.md) — layer: `cross-cutting`; profile: `testing`.
- [056. Logging](../cross-cutting/056-logging.md) — layer: `cross-cutting`; profile: `observability`.
- [057. Metrics](../cross-cutting/057-metrics.md) — layer: `cross-cutting`; profile: `observability`.
- [045. Messaging / Queues](../systems/045-messaging-queues.md) — layer: `systems`; profile: `async`.
- [094. Load & Performance Testing](../cross-cutting/094-load-and-performance-testing.md) — layer: `cross-cutting`; profile: `testing`.

## 22. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s030"></a> **[S030] gRPC Guides.** Cloud Native Computing Foundation; 2026; Current documentation. [https://grpc.io/docs/guides/](https://grpc.io/docs/guides/) — Tags: grpc, rpc, retries, timeouts, streaming.
- <a id="s043"></a> **[S043] Designing Data-Intensive Applications, Second Edition.** Martin Kleppmann and Chris Riccomini / O'Reilly; 2025; 2nd edition. [https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/) — Tags: distributed-systems, databases, consistency, streams.
- <a id="s053"></a> **[S053] Site Reliability Engineering.** Google; 2016; Online book. [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/) — Tags: reliability, operations, monitoring, capacity.
- <a id="s054"></a> **[S054] The Site Reliability Workbook.** Google; 2018; Online book. [https://sre.google/workbook/table-of-contents/](https://sre.google/workbook/table-of-contents/) — Tags: reliability, operations, slo, testing.
- <a id="s055"></a> **[S055] Timeouts, Retries, and Backoff with Jitter.** AWS Builders' Library; 2026; Current article. [https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) — Tags: retries, timeouts, jitter, resilience.
- <a id="s056"></a> **[S056] The Tail at Scale.** Google Research; 2013; Communications of the ACM. [https://research.google/pubs/the-tail-at-scale/](https://research.google/pubs/the-tail-at-scale/) — Tags: latency, hedging, performance.
- <a id="s070"></a> **[S070] Kubernetes Documentation.** Cloud Native Computing Foundation; 2026; Current. [https://kubernetes.io/docs/](https://kubernetes.io/docs/) — Tags: deployment, containers, health, shutdown, autoscaling.

---

**Paper metadata:** canonical subtopics: 11; layer: `primitives`; domain profile: `resilience`; verified through: `2026-08-17`.
