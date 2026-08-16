# 055. Resilience

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Resilience** exists to bound the blast radius and resource cost of partial failure while preserving useful service. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

Resilience policy belongs at each dependency boundary and at the end-to-end request budget. A library default cannot know whether an operation is retryable, idempotent, latency-sensitive, or safety-critical. Coordinate retries, timeouts, circuit breakers, bulkheads, admission control, and fallbacks so one layer does not defeat another.

The most important evidence base for this paper includes [S053](#s053) [S054](#s054) [S055](#s055) [S056](#s056). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Timeouts, retries, concurrency limits, backpressure, and circuit breakers must be designed together.
- A timeout is an ambiguous outcome: the remote side may have completed the operation.
- Retries are load multipliers and must be budgeted across call layers.
- Fallbacks can return stale or lower-quality data, but they must not weaken security or silently corrupt state.
- Graceful degradation requires a predefined reduced contract, not ad hoc exception swallowing.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Resilience** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- How many total attempts can one user request trigger across every layer during an outage?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Resilience**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Draw the full call graph and multiply retry counts/deadlines across client, proxy, service, SDK, and worker layers.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S053](#s053) [S054](#s054) [S055](#s055) [S056](#s056)

1. **Invariant 1:** Timeouts, retries, concurrency limits, backpressure, and circuit breakers must be designed together.
2. **Invariant 2:** A timeout is an ambiguous outcome: the remote side may have completed the operation.
3. **Invariant 3:** Retries are load multipliers and must be budgeted across call layers.
4. **Invariant 4:** Fallbacks can return stale or lower-quality data, but they must not weaken security or silently corrupt state.
5. **Invariant 5:** Graceful degradation requires a predefined reduced contract, not ad hoc exception swallowing.

Additional topic-specific invariants:

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Retry vs fail fast | Retry can mask transient failures but amplifies overload and duplicates side effects. | Retry only classified transient failures within a deadline and budget. |
| Client vs service-mesh retry | Client retries know operation semantics; mesh retries are uniform but may not know idempotency. | Keep semantic retry policy with the caller and use infrastructure retries narrowly. |
| Circuit breaker vs concurrency limiter | Breakers react to failure rate; limiters prevent overload before failure. | Use both when appropriate and monitor their states. |
| Fallback vs explicit degradation | Fallback may hide stale or incomplete results; explicit degradation preserves transparency. | Expose degradation in response metadata, health, and metrics when it affects behavior. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

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

## 7. Data model and API implications

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

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **Partial failure**
- **Fallbacks**
- **Bulkheads**
- **Load shedding**
- **Backpressure**
- **Brownout modes**
- **Emergency switches**

### 8.2. Graceful degradation

- **SHOULD — engineering rule:** Use barriers/hooks to force the critical interleaving, repeat across real database isolation, and assert the invariant rather than timing or one response.
- **Production failure mode:** A probabilistic sleep-based test passes while the actual race remains reachable.
- **Existing-codebase evidence:** Instrument the exact read/check/write or lease boundary and run deterministic competing operations.

### 8.7. Failure isolation

- **MUST — engineering rule:** Select isolation by anomaly analysis, not name familiarity. Account for database-specific semantics and retry complete transactions on serialization failure.
- **Production failure mode:** Lost updates, write skew, or phantoms violate invariants despite all statements being inside a transaction.
- **Existing-codebase evidence:** Construct concurrent schedules that would violate the invariant and verify the chosen isolation/locking rejects one participant.

### 8.8. Dependency isolation

- **MUST — engineering rule:** Select isolation by anomaly analysis, not name familiarity. Account for database-specific semantics and retry complete transactions on serialization failure.
- **Production failure mode:** Lost updates, write skew, or phantoms violate invariants despite all statements being inside a transaction.
- **Existing-codebase evidence:** Construct concurrent schedules that would violate the invariant and verify the chosen isolation/locking rejects one participant.

### 8.9. Retry control

- **SHOULD — engineering rule:** Classify retryable outcomes, cap attempts and elapsed time, use exponential backoff with jitter, honor provider pushback, and make side effects idempotent or detect ambiguous completion.
- **Production failure mode:** Permanent failures loop forever, retries synchronize into a storm, or a timed-out successful operation is duplicated.
- **Existing-codebase evidence:** Inject each error class and verify attempt count, schedule, deadline budget, duplicate behavior, and terminal routing.

### 8.10. Timeout control

- **MUST — engineering rule:** Establish an end-to-end deadline, allocate smaller downstream budgets, propagate cancellation, and stop expensive or side-effecting work when the result is no longer useful unless explicitly designed otherwise.
- **Production failure mode:** Requests wait indefinitely, downstream work continues after callers leave, or nested timeouts exceed the original budget.
- **Existing-codebase evidence:** Inject slow dependencies at each hop and verify cancellation reaches database, network calls, streams, and workers.

## 9. Concurrency, transactions, idempotency, and consistency

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

## 10. Security, authorization, privacy, and abuse resistance

Map trust boundaries, assets, attackers, privileges, data flows, and failure modes before selecting controls. Enforce least privilege in the component that owns the resource; edge filtering, WAFs, and gateways are supplementary. Treat every external, model-generated, cached, imported, or administrator-supplied value as untrusted at its use context.

- **MUST** authenticate the actual caller or workload and re-authorize the final action against authoritative tenant, ownership, resource state, and policy context.
- **MUST** reject mass assignment and unknown privileged fields; server-controlled identity, role, tenant, status, price, owner, and audit fields cannot come from an untrusted DTO.
- **MUST** classify and minimize sensitive data; redact logs/traces/errors, restrict exports and support tooling, propagate deletion, and account for backups and derived indexes.
- **SHOULD** combine rate limits with resource budgets, concurrency caps, payload/complexity limits, and detection. IP-only limiting is not an identity or abuse strategy.
- **AVOID** fail-open behavior for high-impact actions when policy, key, revocation, or tenant context is unavailable.

## 11. Distributed failure, retries, timeouts, and recovery

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

## 12. Persistence, constraints, indexes, and caching

- Put race-sensitive invariants in the database or authoritative store. Application checks remain useful for error quality but are not the final guard.
- Design indexes from real query predicates, tenant scope, ordering, soft-delete conditions, and production cardinality. Verify plans and write amplification.
- Keep transactions bounded in time and rows; avoid network/provider calls while locks are held.
- Treat caches, search indexes, analytics, and replicas as derived unless explicitly authoritative. Version them and provide rebuild/reconciliation.
- Retention and cleanup must include references, uniqueness, tombstones, legal hold, audit, external copies, and interrupted-job recovery.

## 13. Observability, audit, and operational control

Measure attempts per logical operation, deadline budget consumed, timeout phase, breaker state, rejection/shed count, retry-budget exhaustion, fallback use, queue depth, saturation, and dependency-tail latency. Alert on correlated symptoms rather than every individual failure.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

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

## 15. Cross-cutting implementation matrix

| Concern | Required production decision |
|---|---|
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Resilience path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Partial failure`, `Bulkheads`, `Failure isolation`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Resilience; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Resilience** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Dependency isolation**: Select isolation by anomaly analysis, not name familiarity. Account for database-specific semantics and retry complete transactions on serialization failure.

### SHOULD

- **SHOULD** — Timeouts, retries, concurrency limits, backpressure, and circuit breakers must be designed together.
- **SHOULD** — A timeout is an ambiguous outcome: the remote side may have completed the operation.
- **SHOULD** — Retries are load multipliers and must be budgeted across call layers.
- **SHOULD** — Fallbacks can return stale or lower-quality data, but they must not weaken security or silently corrupt state.
- **SHOULD** — Graceful degradation requires a predefined reduced contract, not ad hoc exception swallowing.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

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

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Inject connect, TLS, write, first-byte, mid-body, and slow-success failures; verify phase-specific timeout and outcome handling.
- [ ] Run retry storms from multiple client/server layers and prove retry budgets, jitter, admission control, and idempotency bound amplification.
- [ ] Exercise breaker thresholds, half-open probes, oscillation, dependency recovery, and stale distributed state.
- [ ] Saturate each pool/queue independently and together; verify bounded memory, load shedding, and useful degraded behavior.
- [ ] Cancel requests at each stage and confirm resource release and no unsafe duplicate side effect.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Adding unbounded queues to hide overload.
- Returning stale fallback as successful truth.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [104. Backpressure](104-backpressure.md)
- [053. Timeout Engineering](053-timeout-engineering.md)
- [054. Circuit Breakers](054-circuit-breakers.md)
- [052. Retry Engineering](052-retry-engineering.md)
- [051. External Integrations](051-external-integrations.md)
- 093. Failure Testing — in the `quality-release` skill.
- 079. Connection Management — in the `runtime-delivery` skill.
- 043. Background Jobs — in the `async-messaging` skill.
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.
- 138. Operational Runbooks — in the `production-operations` skill.
- 059. Health Checks — in the `production-operations` skill.
- 094. Load & Performance Testing — in the `quality-release` skill.

## 20. Sources and further research

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
