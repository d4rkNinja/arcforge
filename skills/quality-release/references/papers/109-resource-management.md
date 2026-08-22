# 109. Resource Management

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Resource Management** exists to meet latency, throughput, and cost objectives by understanding workload shape, resource saturation, and algorithmic behavior. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

Performance is an end-to-end property across admission, queues, CPU, memory, storage, network, serialization, pools, dependencies, and clients. Define a workload model and service objectives before tuning. The component causing saturation—not the most visible latency—owns the bottleneck.

The most important evidence base for this paper includes [S053](#s053) [S054](#s054) [S056](#s056) [S043](#s043). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Average latency hides queueing and tail behavior; percentiles must be paired with throughput and error rate.
- Optimization without a workload model often moves cost or contention elsewhere.
- Connection pools, worker pools, and queues are coupled; oversizing one can overwhelm the next dependency.
- Caching and batching change consistency, memory, and failure semantics.
- Capacity plans require headroom for retries, failover, deployments, and skew—not only steady-state averages.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Resource Management** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- Which resource saturates first under representative skew and failover headroom?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Resource Management**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Collect real query plans, profiles, pool waits, queue depth, tails, and data skew before optimization.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S053](#s053) [S054](#s054) [S056](#s056) [S043](#s043)

1. **Invariant 1:** Average latency hides queueing and tail behavior; percentiles must be paired with throughput and error rate.
2. **Invariant 2:** Optimization without a workload model often moves cost or contention elsewhere.
3. **Invariant 3:** Connection pools, worker pools, and queues are coupled; oversizing one can overwhelm the next dependency.
4. **Invariant 4:** Caching and batching change consistency, memory, and failure semantics.
5. **Invariant 5:** Capacity plans require headroom for retries, failover, deployments, and skew—not only steady-state averages.

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Vertical vs horizontal scaling | Vertical scaling is simple but bounded; horizontal scaling requires partitionable state and coordination. | Use vertical headroom first while designing stateful bottlenecks for partitioning. |
| Batching vs per-item processing | Batching amortizes overhead but raises latency, memory, and partial-failure complexity. | Bound batch size by latency and resource budgets. |
| Precompute vs compute on read | Precompute shifts cost to writes and requires invalidation; read-time compute stays fresh but may be expensive. | Choose based on read/write ratio and staleness tolerance. |
| Compression vs CPU | Compression saves bandwidth and storage but adds CPU and latency and can amplify bombs. | Apply thresholds and size limits with measurements. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

Requests move through `arrival → admission → queue → service → dependency waits → serialization → response`; overload increases queueing nonlinearly. Capacity work moves `measure baseline → profile → hypothesize → change → compare → soak → roll out`. Regressions require rollback criteria.

```mermaid
stateDiagram-v2
    arrival --> admission --> queue --> service --> dependencies --> serialization --> response
    queue --> shed_or_timeout
    service --> saturation
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Specify throughput, concurrency, payload/data distribution, p50/p95/p99 latency, error limits, resource ceilings, and headroom for failover/retries. Pool and queue sizes are contracts with downstream capacity. Compression, caching, batching, and asynchronous work change semantics as well as speed.

A production representation commonly needs the following fields or equivalent evidence:

- workload scenario, data distribution/skew, concurrency, and offered load.
- latency distribution, throughput, errors, queueing, and saturation.
- CPU/memory/allocation/GC/disk/network and dependency resource use.
- configuration/build/schema/query-plan/cache state.
- cost and headroom under retry, failover, and deployment overlap.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **Disk**
- **Network**
- **File descriptors**
- **Connections**
- **Thread pools**
- **Worker pools**
- **Goroutines/coroutines**
- **Queue sizes**
- **Resource leaks**
- **Resource limits**

### 8.1. CPU

- **SHOULD — engineering rule:** Measure under representative load before changing code; correlate profiles with request classes, queueing, GC pauses, I/O, and tail latency. Preserve correctness and observability while optimizing.
- **Production failure mode:** A micro-optimization shifts pressure to memory, database, or network and worsens production tails.
- **Existing-codebase evidence:** Capture before/after profiles and end-to-end metrics with equivalent workloads and statistical confidence.

### 8.2. Memory

- **SHOULD — engineering rule:** Measure under representative load before changing code; correlate profiles with request classes, queueing, GC pauses, I/O, and tail latency. Preserve correctness and observability while optimizing.
- **Production failure mode:** A micro-optimization shifts pressure to memory, database, or network and worsens production tails.
- **Existing-codebase evidence:** Capture before/after profiles and end-to-end metrics with equivalent workloads and statistical confidence.

## 9. Concurrency, transactions, idempotency, and consistency

Optimization can trade freshness, ordering, atomicity, or duplicate behavior. Batching needs per-item outcomes and bounded memory. Read replicas may be stale; caches may violate read-your-writes. Document each trade and preserve correctness invariants under load.

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

Hot keys/shards, connection exhaustion, GC pressure, N+1 queries, unbounded queues, retry storms, large payloads, and noisy neighbors dominate production. Measure tail latency and saturation; averages hide collapse. Protect with admission control and bounded concurrency before autoscaling.

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

Monitor utilization, saturation, queueing, allocations/GC, pool wait, query plan/latency, cache effectiveness, network bytes, dependency tails, throttling, and cost per operation. Profiles and traces must be captured under representative load and compared to a baseline.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

Performance changes need canary measurement against real workload shape. New indexes, pool sizes, compression, or batching can hurt another workload and may not roll back instantly. Preserve schema/query compatibility and account for warmup/cold-cache behavior.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Resource Management path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `CPU`, `Network`, `Thread pools`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Resource Management; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Resource Management** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **CPU**: Measure under representative load before changing code; correlate profiles with request classes, queueing, GC pauses, I/O, and tail latency. Preserve correctness and observability while optimizing.

### SHOULD

- **SHOULD** — Average latency hides queueing and tail behavior; percentiles must be paired with throughput and error rate.
- **SHOULD** — Optimization without a workload model often moves cost or contention elsewhere.
- **SHOULD** — Connection pools, worker pools, and queues are coupled; oversizing one can overwhelm the next dependency.
- **SHOULD** — Caching and batching change consistency, memory, and failure semantics.
- **SHOULD** — Capacity plans require headroom for retries, failover, deployments, and skew—not only steady-state averages.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Adopt the **Vertical vs horizontal scaling** option that fits the workload and ownership boundary; Use vertical headroom first while designing stateful bottlenecks for partitioning.
- **MAY** — Adopt the **Batching vs per-item processing** option that fits the workload and ownership boundary; Bound batch size by latency and resource budgets.
- **MAY** — Adopt the **Precompute vs compute on read** option that fits the workload and ownership boundary; Choose based on read/write ratio and staleness tolerance.

### AVOID

- **AVOID** — Unbounded queues hiding overload until OOM.
- **AVOID** — N+1 queries.
- **AVOID** — Pool size larger than database capacity.
- **AVOID** — Hot partition from poor key choice.
- **AVOID** — Autoscaling on lagging metrics after saturation.
- **AVOID** — Optimizing averages rather than tails and saturation.
- **AVOID** — Increasing pool sizes beyond dependency capacity.
- **AVOID** — Adding unbounded concurrency.

### NEVER

- **NEVER** — Never optimize without measuring a representative workload and correctness impact.
- **NEVER** — Never use an unbounded queue or concurrency setting as a scalability mechanism.
- **NEVER** — Never size client pools independently of downstream capacity.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Define and replay realistic payload, cardinality, skew, read/write mix, concurrency, burst, and background-work distributions.
- [ ] Measure p50/p95/p99, throughput, errors, queueing, saturation, resource use, and cost together through ramp, spike, soak, and failover.
- [ ] Profile CPU, allocation/GC, I/O, queries, locks, pools, and network under load; compare before/after against a baseline.
- [ ] Exercise cold caches, cold processes, deployment overlap, replica lag, hot keys/shards, and retry amplification.
- [ ] Verify correctness and cancellation under load; no optimization may silently weaken consistency or drop work.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Caching or batching without correctness analysis.
- Benchmarking toy uniform data.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [095. Performance Engineering](095-performance-engineering.md)
- [117. Compression](117-compression.md)
- 108. Infrastructure Configuration — in the `runtime-delivery` skill.
- 079. Connection Management — in the `runtime-delivery` skill.
- 118. Batch Processing — in the `async-messaging` skill.
- 104. Backpressure — in the `resilience-flow-control` skill.
- 039. Quotas — in the `resilience-flow-control` skill.
- [096. Scalability](096-scalability.md)
- 053. Timeout Engineering — in the `resilience-flow-control` skill.
- 081. Load Balancing — in the `runtime-delivery` skill.
- 028. Query Design — in the `data-storage` skill.
- [146. Cross-Cutting Implementation Checklist](146-cross-cutting-implementation-checklist.md)

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s040"></a> **[S040] PostgreSQL Documentation.** PostgreSQL Global Development Group; 2026; 18 current. [https://www.postgresql.org/docs/18/](https://www.postgresql.org/docs/18/) — Tags: database, sql, transactions, indexes, concurrency, backup.
- <a id="s041"></a> **[S041] MongoDB Manual.** MongoDB; 2026; 8.0. [https://www.mongodb.com/docs/v8.0/](https://www.mongodb.com/docs/v8.0/) — Tags: database, documents, transactions, indexes, sharding.
- <a id="s042"></a> **[S042] Redis Documentation.** Redis; 2026; Current. [https://redis.io/docs/latest/](https://redis.io/docs/latest/) — Tags: cache, rate-limiting, locks, streams, queues.
- <a id="s043"></a> **[S043] Designing Data-Intensive Applications, Second Edition.** Martin Kleppmann and Chris Riccomini / O'Reilly; 2025; 2nd edition. [https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/) — Tags: distributed-systems, databases, consistency, streams.
- <a id="s053"></a> **[S053] Site Reliability Engineering.** Google; 2016; Online book. [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/) — Tags: reliability, operations, monitoring, capacity.
- <a id="s054"></a> **[S054] The Site Reliability Workbook.** Google; 2018; Online book. [https://sre.google/workbook/table-of-contents/](https://sre.google/workbook/table-of-contents/) — Tags: reliability, operations, slo, testing.
- <a id="s056"></a> **[S056] The Tail at Scale.** Google Research; 2013; Communications of the ACM. [https://research.google/pubs/the-tail-at-scale/](https://research.google/pubs/the-tail-at-scale/) — Tags: latency, hedging, performance.
- <a id="s068"></a> **[S068] Prometheus Documentation.** Prometheus; 2026; Current. [https://prometheus.io/docs/](https://prometheus.io/docs/) — Tags: metrics, monitoring, alerting.
- <a id="s129"></a> **[S129] Kubernetes Resource Management for Pods and Containers.** Kubernetes; 2026; Current. [https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) — Tags: resources, containers, capacity.
- <a id="s070"></a> **[S070] Kubernetes Documentation.** Cloud Native Computing Foundation; 2026; Current. [https://kubernetes.io/docs/](https://kubernetes.io/docs/) — Tags: deployment, containers, health, shutdown, autoscaling.
- <a id="s071"></a> **[S071] Pod Lifecycle and Container Lifecycle Hooks.** Kubernetes; 2026; Current. [https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) — Tags: lifecycle, health, shutdown, deployment.
- <a id="s128"></a> **[S128] Kubernetes Deployments.** Kubernetes; 2026; Current. [https://kubernetes.io/docs/concepts/workloads/controllers/deployment/](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) — Tags: deployment, rolling-update, rollback.
- <a id="s073"></a> **[S073] Supply-chain Levels for Software Artifacts.** OpenSSF; 2026; SLSA v1.1. [https://slsa.dev/spec/v1.1/](https://slsa.dev/spec/v1.1/) — Tags: supply-chain, builds, provenance, ci-cd.
- <a id="s074"></a> **[S074] Sigstore Documentation.** OpenSSF; 2026; Current. [https://docs.sigstore.dev/](https://docs.sigstore.dev/) — Tags: signing, supply-chain, artifacts.
- <a id="s075"></a> **[S075] SPDX Specification.** Linux Foundation; 2026; 3.0. [https://spdx.github.io/spdx-spec/v3.0/](https://spdx.github.io/spdx-spec/v3.0/) — Tags: sbom, licenses, supply-chain.
- <a id="s076"></a> **[S076] CycloneDX Specification.** OWASP; 2026; Current. [https://cyclonedx.org/specification/overview/](https://cyclonedx.org/specification/overview/) — Tags: sbom, supply-chain, dependencies.
