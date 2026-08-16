---
paper_number: 57
title: "Metrics"
layer: cross-cutting
domain_profile: observability
corpus_version: 1.0.0
verified_through: 2026-08-17
canonical_source: "original/Pasted text.txt"
subtopic_count: 13
status: production-engineering-reference
---

# 057. Metrics

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Metrics** exists to make system behavior, causality, saturation, and security-relevant actions reconstructable without leaking sensitive data. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

Logs, metrics, traces, and audits serve different guarantees. Application observability explains health and causality; audit records support accountability and often require stronger integrity and retention. Instrument at ownership boundaries and propagate correlation across HTTP, database, cache, queue, worker, and provider calls.

The most important evidence base for this paper includes [S066](#s066) [S067](#s067) [S068](#s068) [S135](#s135). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Logs, metrics, traces, and audit records serve different queries and should share correlation identifiers without becoming the same data stream.
- High-cardinality labels can make telemetry pipelines expensive or unusable.
- Sampling must preserve rare failures and security events; uniform sampling alone often discards the evidence needed most.
- Async boundaries require explicit propagation of trace, message, job, tenant, and causation identifiers.
- Observability is part of the interface: operators need version, configuration, dependency, and state-transition visibility.

## 2. Scope and terminology map

The canonical topic list requires this paper to cover the following concerns. They are grouped only to expose relationships; no listed subtopic is omitted.

### Concurrency and distributed behavior

**Queue depth**.

### Operations and observability

**Counters**, **Gauges**, **Histograms**, **Latency**, **Throughput**, **Error rate**, **DB pool usage**, **Cache hit ratio**, **External dependency metrics**, **Business-neutral operational metrics**, **High-cardinality labels**, **Metric cardinality control**.

### Boundary of the paper

This paper treats **Metrics** as a production subsystem or reusable reasoning primitive. It covers semantics, ownership, persistence, APIs, security, concurrency, distributed behavior, operations, evolution, and verification. Framework syntax and large implementation listings are intentionally excluded.

## 3. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S066](#s066) [S067](#s067) [S068](#s068) [S135](#s135)

1. **Invariant 1:** Logs, metrics, traces, and audit records serve different queries and should share correlation identifiers without becoming the same data stream.
2. **Invariant 2:** High-cardinality labels can make telemetry pipelines expensive or unusable.
3. **Invariant 3:** Sampling must preserve rare failures and security events; uniform sampling alone often discards the evidence needed most.
4. **Invariant 4:** Async boundaries require explicit propagation of trace, message, job, tenant, and causation identifiers.
5. **Invariant 5:** Observability is part of the interface: operators need version, configuration, dependency, and state-transition visibility.

Additional topic-specific invariants:

- **SHOULD — Counters:** Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.
- **SHOULD — Histograms:** Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.
- **SHOULD — Error rate:** Define the exact semantics of **Error rate** within Metrics: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — DB pool usage:** Define the exact semantics of **DB pool usage** within Metrics: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Business-neutral operational metrics:** Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.
- **SHOULD — Metric cardinality control:** Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.

## 4. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Counters/gauges vs histograms | Counters and gauges describe totals/state; histograms support latency distributions but require bucket/cardinality design. | Instrument semantics and units before dashboarding; avoid high-cardinality labels. |
| Structured logs vs free text | Structured logs support search and automation; free text is flexible but brittle. | Use structured events with bounded schemas and human-readable messages. |
| Head vs tail sampling | Head sampling is cheap but blind to outcomes; tail sampling can retain errors and latency outliers but costs buffering. | Combine policies based on volume and forensic needs. |
| Metrics vs logs for alerts | Metrics are efficient and aggregatable; log alerts are expressive but costly and noisy. | Alert on metrics/SLOs and use logs/traces for diagnosis. |
| Application audit log vs database audit | Application logs know intent and actor; database logs see writes but not business meaning. | Use application-level audit with tamper-resistant storage, optionally augmented by database auditing. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 5. Ownership, state, and lifecycle

A signal is `generated → enriched → sampled/aggregated → exported → stored → queried/alerted → retained/deleted`. Each step can drop, delay, duplicate, or expose data. Telemetry backpressure must never consume unbounded application resources.

```mermaid
stateDiagram-v2
    generated --> enriched --> sampled_or_aggregated --> exported --> stored --> queried_or_alerted --> retained_or_deleted
    exported --> dropped_or_retried
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 6. Data model and API implications

Define stable event names, severity, semantic attributes, units, cardinality budgets, sampling, redaction, retention, and access policy. Request IDs are useful locally; trace context preserves distributed causality. Audit events require actor, action, target, result, time, and provenance.

A production representation commonly needs the following fields or equivalent evidence:

- stable event/metric/span name and semantic version.
- timestamp, severity/status, service/build/environment, trace/request/workflow context.
- bounded actor/tenant/resource identifiers according to privacy policy.
- duration, units, outcome/error classification, and dependency metadata.
- redaction, sampling, retention, and audit-integrity metadata.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 7. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### 7.1. Counters

- **SHOULD — engineering rule:** Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.
- **Production failure mode:** Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- **Existing-codebase evidence:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.

### 7.2. Gauges

- **SHOULD — engineering rule:** Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.
- **Production failure mode:** Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- **Existing-codebase evidence:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.

### 7.3. Histograms

- **SHOULD — engineering rule:** Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.
- **Production failure mode:** Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- **Existing-codebase evidence:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.

### 7.4. Latency

- **SHOULD — engineering rule:** Define the exact semantics of **Latency** within Metrics: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for latency is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for latency, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.5. Throughput

- **SHOULD — engineering rule:** Define the exact semantics of **Throughput** within Metrics: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for throughput is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for throughput, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.6. Error rate

- **SHOULD — engineering rule:** Define the exact semantics of **Error rate** within Metrics: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for error rate is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for error rate, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.7. Queue depth

- **SHOULD — engineering rule:** Define the exact semantics of **Queue depth** within Metrics: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for queue depth is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for queue depth, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.8. DB pool usage

- **SHOULD — engineering rule:** Define the exact semantics of **DB pool usage** within Metrics: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for db pool usage is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for db pool usage, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.9. Cache hit ratio

- **SHOULD — engineering rule:** Define the exact semantics of **Cache hit ratio** within Metrics: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for cache hit ratio is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for cache hit ratio, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.10. External dependency metrics

- **SHOULD — engineering rule:** Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.
- **Production failure mode:** Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- **Existing-codebase evidence:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.

### 7.11. Business-neutral operational metrics

- **SHOULD — engineering rule:** Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.
- **Production failure mode:** Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- **Existing-codebase evidence:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.

### 7.12. High-cardinality labels

- **SHOULD — engineering rule:** Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.
- **Production failure mode:** Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- **Existing-codebase evidence:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.

### 7.13. Metric cardinality control

- **SHOULD — engineering rule:** Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.
- **Production failure mode:** Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- **Existing-codebase evidence:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.

## 8. Concurrency, transactions, idempotency, and consistency

Telemetry is usually eventually delivered and may be sampled; it cannot be the sole source of domain truth. Audit intent that must survive a crash should be coupled durably to the state change. Clock skew and async export complicate ordering, so use causation IDs and authoritative timestamps.

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

Collectors, log sinks, and metric backends can be slow or unavailable. Use bounded buffers and drop policies appropriate to signal type; never block critical paths indefinitely. Redaction failure, cardinality explosion, recursive logging, and missing async context are common incidents.

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

Monitor the observability pipeline itself: dropped spans/logs, export failures, queue depth, sampling rate, cardinality, ingestion cost, clock skew, and audit-write failures. Dashboards should connect user-visible symptoms to saturation and dependencies, and runbooks should point to exact queries.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 13. Compatibility, schema evolution, migration, deployment, and rollback

Telemetry schemas are contracts consumed by dashboards, alerts, detectors, and compliance exports. Add fields before removing or renaming, version high-value events, and test redaction rules. Deploy alert changes with code changes so new failure modes are visible immediately.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Metrics path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Counters`, `Latency`, `Queue depth`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Metrics; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 15. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Metrics** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Counters**: Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.
- **MUST** — For **Histograms**: Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.
- **MUST** — For **Error rate**: Define the exact semantics of **Error rate** within Metrics: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **DB pool usage**: Define the exact semantics of **DB pool usage** within Metrics: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.

### SHOULD

- **SHOULD** — Logs, metrics, traces, and audit records serve different queries and should share correlation identifiers without becoming the same data stream.
- **SHOULD** — High-cardinality labels can make telemetry pipelines expensive or unusable.
- **SHOULD** — Sampling must preserve rare failures and security events; uniform sampling alone often discards the evidence needed most.
- **SHOULD** — Async boundaries require explicit propagation of trace, message, job, tenant, and causation identifiers.
- **SHOULD** — Observability is part of the interface: operators need version, configuration, dependency, and state-transition visibility.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Choose **Counters/gauges vs histograms** according to the stated trade-off: Instrument semantics and units before dashboarding; avoid high-cardinality labels.
- **MAY** — Adopt the **Structured logs vs free text** option that fits the workload and ownership boundary; Use structured events with bounded schemas and human-readable messages.
- **MAY** — Adopt the **Head vs tail sampling** option that fits the workload and ownership boundary; Combine policies based on volume and forensic needs.
- **MAY** — Adopt the **Metrics vs logs for alerts** option that fits the workload and ownership boundary; Alert on metrics/SLOs and use logs/traces for diagnosis.

### AVOID

- **AVOID** — Passwords/tokens/PII in logs.
- **AVOID** — Trace context lost across queue.
- **AVOID** — User ID as unbounded metric label.
- **AVOID** — Health check causing dependency overload.
- **AVOID** — Audit event written outside the transaction and lost.
- **AVOID** — Logging entire request/response bodies.
- **AVOID** — Using user IDs as unbounded metric labels.
- **AVOID** — Confusing audit logs with sampled application logs.

### NEVER

- **NEVER** — Never log secrets, credentials, raw authentication tokens, or unrestricted sensitive payloads.
- **NEVER** — Never use sampled telemetry as the sole audit or domain record.
- **NEVER** — Never allow telemetry backpressure to consume unbounded application memory.

## 16. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Drop, delay, duplicate, and backpressure telemetry exports; the application must remain bounded and critical audit intent must survive as designed.
- [ ] Verify trace/context propagation across HTTP, queue, scheduled jobs, retries, caches, databases, and providers.
- [ ] Fuzz logs and attributes with secrets, PII, newlines, huge values, and attacker-controlled strings; redaction and size/cardinality limits must hold.
- [ ] Exercise alert conditions and runbooks in staging/chaos drills; prove alerts identify the owning failure rather than only symptoms.
- [ ] Run schema compatibility tests for dashboards, detectors, audit exports, and retained historical events.
- [ ] **Counters:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.
- [ ] **Histograms:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.
- [ ] **Error rate:** Locate every implementation path for error rate, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **DB pool usage:** Locate every implementation path for db pool usage, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Business-neutral operational metrics:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.
- [ ] **Metric cardinality control:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 17. Common production bugs and incorrect implementations

- Passwords/tokens/PII in logs.
- Trace context lost across queue.
- User ID as unbounded metric label.
- Health check causing dependency overload.
- Audit event written outside the transaction and lost.
- **Counters:** Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- **Histograms:** Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- **Throughput:** A framework or provider default for throughput is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Queue depth:** A framework or provider default for queue depth is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Cache hit ratio:** A framework or provider default for cache hit ratio is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Business-neutral operational metrics:** Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- **Metric cardinality control:** Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Logging entire request/response bodies.
- Using user IDs as unbounded metric labels.
- Confusing audit logs with sampled application logs.
- Dropping async trace context.
- Adding alerts without owner or runbook.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Metrics** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- For **Counters**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- For **Histograms**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- For **Error rate**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for error rate is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **DB pool usage**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for db pool usage is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Business-neutral operational metrics**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- Which signals are best-effort versus durable audit evidence, and what happens when the telemetry pipeline is unavailable?

## 20. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Metrics**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] **Counters:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.
- [ ] **Histograms:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.
- [ ] **Throughput:** Locate every implementation path for throughput, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Queue depth:** Locate every implementation path for queue depth, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Cache hit ratio:** Locate every implementation path for cache hit ratio, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Business-neutral operational metrics:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.
- [ ] **Metric cardinality control:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.
- [ ] Inspect sampling, redaction, cardinality, retention, and access policy in the real telemetry pipeline.

## 21. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [058. Distributed Tracing](058-distributed-tracing.md) — layer: `cross-cutting`; profile: `observability`.
- [056. Logging](056-logging.md) — layer: `cross-cutting`; profile: `observability`.
- [137. Observability for Async Systems](137-observability-for-async-systems.md) — layer: `cross-cutting`; profile: `observability`.
- [138. Operational Runbooks](138-operational-runbooks.md) — layer: `cross-cutting`; profile: `observability`.
- [139. Incident Readiness](139-incident-readiness.md) — layer: `cross-cutting`; profile: `observability`.
- [146. Cross-Cutting Implementation Checklist](146-cross-cutting-implementation-checklist.md) — layer: `cross-cutting`; profile: `checklist`.
- [094. Load & Performance Testing](094-load-and-performance-testing.md) — layer: `cross-cutting`; profile: `testing`.
- [059. Health Checks](059-health-checks.md) — layer: `cross-cutting`; profile: `observability`.
- [011. Request Lifecycle](../primitives/011-request-lifecycle.md) — layer: `primitives`; profile: `api`.
- [095. Performance Engineering](095-performance-engineering.md) — layer: `cross-cutting`; profile: `performance`.
- [060. Audit Logging](060-audit-logging.md) — layer: `cross-cutting`; profile: `observability`.
- [053. Timeout Engineering](../primitives/053-timeout-engineering.md) — layer: `primitives`; profile: `resilience`.

## 22. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s053"></a> **[S053] Site Reliability Engineering.** Google; 2016; Online book. [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/) — Tags: reliability, operations, monitoring, capacity.
- <a id="s054"></a> **[S054] The Site Reliability Workbook.** Google; 2018; Online book. [https://sre.google/workbook/table-of-contents/](https://sre.google/workbook/table-of-contents/) — Tags: reliability, operations, slo, testing.
- <a id="s066"></a> **[S066] OpenTelemetry Specification.** Cloud Native Computing Foundation; 2026; 1.59.0. [https://opentelemetry.io/docs/specs/otel/](https://opentelemetry.io/docs/specs/otel/) — Tags: observability, tracing, metrics, logs.
- <a id="s067"></a> **[S067] Trace Context.** W3C; 2021; Recommendation. [https://www.w3.org/TR/trace-context/](https://www.w3.org/TR/trace-context/) — Tags: tracing, context-propagation.
- <a id="s068"></a> **[S068] Prometheus Documentation.** Prometheus; 2026; Current. [https://prometheus.io/docs/](https://prometheus.io/docs/) — Tags: metrics, monitoring, alerting.
- <a id="s069"></a> **[S069] OpenMetrics Specification.** Cloud Native Computing Foundation; 2023; 1.0.0. [https://openmetrics.io/](https://openmetrics.io/) — Tags: metrics, exposition, interoperability.
- <a id="s070"></a> **[S070] Kubernetes Documentation.** Cloud Native Computing Foundation; 2026; Current. [https://kubernetes.io/docs/](https://kubernetes.io/docs/) — Tags: deployment, containers, health, shutdown, autoscaling.
- <a id="s135"></a> **[S135] Logging Cheat Sheet.** OWASP; 2026; Living document. [https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) — Tags: logging, security, audit, privacy.
- <a id="s136"></a> **[S136] Guide to Computer Security Log Management.** NIST; 2006; SP 800-92. [https://csrc.nist.gov/pubs/sp/800/92/final](https://csrc.nist.gov/pubs/sp/800/92/final) — Tags: logging, retention, operations.

---

**Paper metadata:** canonical subtopics: 13; layer: `cross-cutting`; domain profile: `observability`; verified through: `2026-08-17`.
