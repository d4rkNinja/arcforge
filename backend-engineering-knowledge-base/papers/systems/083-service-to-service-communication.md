---
paper_number: 83
title: "Service-to-Service Communication"
layer: systems
domain_profile: runtime
corpus_version: 1.0.0
verified_through: 2026-08-17
canonical_source: "original/Pasted text.txt"
subtopic_count: 13
status: production-engineering-reference
---

# 083. Service-to-Service Communication

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Service-to-Service Communication** exists to make process startup, steady-state execution, and termination deterministic across environments and orchestrators. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

The composition root owns configuration parsing, dependency construction, lifecycle registration, and process-wide policy. Feature modules should receive validated dependencies rather than read environment variables, create clients, or register signal handlers themselves. Startup readiness is a contract with the orchestrator: a process may be alive while still unready, and it may be draining while health endpoints continue to answer.

The most important evidence base for this paper includes [S122](#s122) [S123](#s123) [S124](#s124) [S070](#s070). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- The process is not ready merely because its socket is listening; readiness requires every dependency needed for the advertised request class to be usable.
- Initialization order is a dependency graph, not a convenient list. Cycles and hidden lazy initialization create startup-only incidents.
- Shutdown is a protocol: stop admission, drain work, finish or abandon with explicit semantics, then release resources.
- Build identity and configuration identity are operational data. Without them, mixed-version and rollback failures are hard to diagnose.
- Development conveniences must not silently change security or durability semantics in production.

## 2. Scope and terminology map

The canonical topic list requires this paper to cover the following concerns. They are grouped only to expose relationships; no listed subtopic is omitted.

### Identity, trust, and access

**Authentication**, **Authorization**.

### Concurrency and distributed behavior

**Timeouts**.

### Security, privacy, and abuse

**mTLS**.

### Operations and observability

**REST**, **gRPC**, **Messaging**, **Retries**, **Service discovery**, **Load balancing**, **Observability**.

### Testing and evolution

**Schema evolution**, **Contract compatibility**.

### Boundary of the paper

This paper treats **Service-to-Service Communication** as a production subsystem or reusable reasoning primitive. It covers semantics, ownership, persistence, APIs, security, concurrency, distributed behavior, operations, evolution, and verification. Framework syntax and large implementation listings are intentionally excluded.

## 3. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S122](#s122) [S123](#s123) [S124](#s124) [S070](#s070)

1. **Invariant 1:** The process is not ready merely because its socket is listening; readiness requires every dependency needed for the advertised request class to be usable.
2. **Invariant 2:** Initialization order is a dependency graph, not a convenient list. Cycles and hidden lazy initialization create startup-only incidents.
3. **Invariant 3:** Shutdown is a protocol: stop admission, drain work, finish or abandon with explicit semantics, then release resources.
4. **Invariant 4:** Build identity and configuration identity are operational data. Without them, mixed-version and rollback failures are hard to diagnose.
5. **Invariant 5:** Development conveniences must not silently change security or durability semantics in production.

Additional topic-specific invariants:

- **SHOULD — REST:** Define the exact semantics of **REST** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Messaging:** Define the exact semantics of **Messaging** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — mTLS:** Define the exact semantics of **mTLS** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST — Timeouts:** Establish an end-to-end deadline, allocate smaller downstream budgets, propagate cancellation, and stop expensive or side-effecting work when the result is no longer useful unless explicitly designed otherwise.
- **SHOULD — Service discovery:** Respect TTL and resolver caching behavior, handle multiple addresses and endpoint churn, drain removed instances, and avoid assuming a DNS lookup is a permanent binding.
- **SHOULD — Observability:** Define the exact semantics of **Observability** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.

## 4. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| REST vs gRPC | REST is broadly interoperable; gRPC provides typed streaming and efficient binary transport but tighter tooling/proxy coupling. | Select per client ecosystem and failure/compatibility needs; do not expose storage models in either. |
| Eager vs lazy initialization | Eager initialization fails fast and proves readiness; lazy initialization shortens startup but moves failures into live traffic. | Prefer eager initialization for mandatory dependencies; use lazy loading only for optional or high-cost capabilities with explicit degraded behavior. |
| Single process vs separate workers | A single binary simplifies deployment but couples failure and scaling domains; separate workers isolate resources but add orchestration and versioning. | Split when workload, scaling, privilege, or failure characteristics differ materially. |
| Strict startup vs degraded startup | Strict startup avoids serving incomplete behavior; degraded startup preserves availability when optional dependencies fail. | Define dependency classes and expose degraded state in readiness and metrics. |
| Framework-owned vs application-owned lifecycle | Framework defaults are convenient but often hide cancellation, ordering, and timeout semantics. | Own the composition root and lifecycle even when using framework hooks. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 5. Ownership, state, and lifecycle

Model the process explicitly as `created → configuration_validated → dependencies_initializing → ready → draining → stopped`, with `failed_startup` reachable from every initialization stage. Initialization must be ordered by real dependencies, not incidental file import order. Shutdown reverses ownership: stop admission first, then drain requests and workers, then close producers/consumers, flush bounded telemetry, and finally release pools and files.

```mermaid
stateDiagram-v2
    created --> config_validated --> initializing --> ready --> draining --> stopped
    initializing --> failed_startup
    ready --> failed_runtime
    draining --> forced_stop
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 6. Data model and API implications

Configuration and runtime metadata form a versioned input contract. Validate types, ranges, mutual exclusions, required secrets, endpoint formats, and environment-specific prohibitions before opening traffic. Expose build/version metadata without secrets, define exactly what readiness means, and make process exit codes and signal behavior observable to supervisors.

A production representation commonly needs the following fields or equivalent evidence:

- `configuration_version` and validated environment identity.
- `build_version`, commit/build time, and deployment instance identity.
- dependency initialization state and ownership.
- readiness/drain state and shutdown reason.
- bounded lifecycle timestamps and failure classification.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 7. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### 7.1. REST

- **SHOULD — engineering rule:** Define the exact semantics of **REST** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for rest is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for rest, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.2. gRPC

- **SHOULD — engineering rule:** Define the exact semantics of **gRPC** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for grpc is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for grpc, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.3. Messaging

- **SHOULD — engineering rule:** Define the exact semantics of **Messaging** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for messaging is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for messaging, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.4. Authentication

- **MUST — engineering rule:** Define the exact semantics of **Authentication** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for authentication is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for authentication, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.5. Authorization

- **MUST — engineering rule:** Define the exact semantics of **Authorization** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for authorization is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for authorization, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.6. mTLS

- **SHOULD — engineering rule:** Define the exact semantics of **mTLS** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for mtls is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for mtls, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.7. Retries

- **SHOULD — engineering rule:** Define the exact semantics of **Retries** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for retries is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for retries, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.8. Timeouts

- **MUST — engineering rule:** Establish an end-to-end deadline, allocate smaller downstream budgets, propagate cancellation, and stop expensive or side-effecting work when the result is no longer useful unless explicitly designed otherwise.
- **Production failure mode:** Requests wait indefinitely, downstream work continues after callers leave, or nested timeouts exceed the original budget.
- **Existing-codebase evidence:** Inject slow dependencies at each hop and verify cancellation reaches database, network calls, streams, and workers.

### 7.9. Schema evolution

- **SHOULD — engineering rule:** Define the exact semantics of **Schema evolution** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for schema evolution is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for schema evolution, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.10. Contract compatibility

- **SHOULD — engineering rule:** Define the exact semantics of **Contract compatibility** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for contract compatibility is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for contract compatibility, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.11. Service discovery

- **SHOULD — engineering rule:** Respect TTL and resolver caching behavior, handle multiple addresses and endpoint churn, drain removed instances, and avoid assuming a DNS lookup is a permanent binding.
- **Production failure mode:** Clients pin dead addresses, failover waits for hidden caches, or stale endpoints receive writes after removal.
- **Existing-codebase evidence:** Rotate endpoints under long-lived connections and test TTL, negative caching, partial DNS failure, and drain.

### 7.12. Load balancing

- **SHOULD — engineering rule:** Choose routing from connection duration, state locality, health, skew, and failure behavior. Ensure draining and retries do not duplicate unsafe work.
- **Production failure mode:** Sticky keys create hot instances, unhealthy connections persist, or retry routes a completed write to another backend.
- **Existing-codebase evidence:** Remove/add instances under load, create skewed keys, and verify drain, failover, and session/state behavior.

### 7.13. Observability

- **SHOULD — engineering rule:** Define the exact semantics of **Observability** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for observability is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for observability, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

## 8. Concurrency, transactions, idempotency, and consistency

Startup and shutdown are concurrent workflows. A dependency may connect while cancellation arrives; two shutdown signals may race; workers may publish or acknowledge while drain begins. Use one-way state transitions, idempotent cleanup, bounded waits, and ownership-aware cancellation. Never close a shared resource while work that can still use it remains admitted.

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

Classify dependency failures as fatal-at-start, degraded-but-ready, or dynamically recoverable. Avoid making readiness depend on optional remote services, but do not report ready when a required store cannot preserve correctness. Bound retries during startup; otherwise rollouts hang and amplify provider outages. On termination, prefer a controlled incomplete shutdown with explicit recovery semantics over an unbounded wait.

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

Emit structured lifecycle events with build ID, configuration version, environment, dependency name, elapsed initialization time, and shutdown reason. Track startup latency, readiness flaps, active work during drain, forced terminations, cleanup failures, pool utilization, and process resource limits. Runbooks must distinguish crash loops, readiness failures, dependency exhaustion, and termination deadline overruns.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 13. Compatibility, schema evolution, migration, deployment, and rollback

Runtime changes must work during rolling deployments where old and new processes coexist. Treat configuration schema, probes, signal grace periods, ports, and dependency initialization as compatibility surfaces. Deploy additive configuration first, then code that consumes it; remove old variables only after every workload has moved. Rollback must not depend on resources already destructively migrated.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Service-to-Service Communication path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `REST`, `Authentication`, `Retries`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Service-to-Service Communication; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 15. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Service-to-Service Communication** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **REST**: Define the exact semantics of **REST** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **Messaging**: Define the exact semantics of **Messaging** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **mTLS**: Define the exact semantics of **mTLS** within Service-to-Service Communication: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **Timeouts**: Establish an end-to-end deadline, allocate smaller downstream budgets, propagate cancellation, and stop expensive or side-effecting work when the result is no longer useful unless explicitly designed otherwise.

### SHOULD

- **SHOULD** — The process is not ready merely because its socket is listening; readiness requires every dependency needed for the advertised request class to be usable.
- **SHOULD** — Initialization order is a dependency graph, not a convenient list. Cycles and hidden lazy initialization create startup-only incidents.
- **SHOULD** — Shutdown is a protocol: stop admission, drain work, finish or abandon with explicit semantics, then release resources.
- **SHOULD** — Build identity and configuration identity are operational data. Without them, mixed-version and rollback failures are hard to diagnose.
- **SHOULD** — Development conveniences must not silently change security or durability semantics in production.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Choose **REST vs gRPC** according to the stated trade-off: Select per client ecosystem and failure/compatibility needs; do not expose storage models in either.
- **MAY** — Adopt the **Eager vs lazy initialization** option that fits the workload and ownership boundary; Prefer eager initialization for mandatory dependencies; use lazy loading only for optional or high-cost capabilities with explicit degraded behavior.
- **MAY** — Adopt the **Single process vs separate workers** option that fits the workload and ownership boundary; Split when workload, scaling, privilege, or failure characteristics differ materially.
- **MAY** — Adopt the **Strict startup vs degraded startup** option that fits the workload and ownership boundary; Define dependency classes and expose degraded state in readiness and metrics.

### AVOID

- **AVOID** — Accepting traffic before migrations/config/dependencies are ready.
- **AVOID** — Hanging on termination because background tasks ignore cancellation.
- **AVOID** — Double-starting workers after reload or fork.
- **AVOID** — Leaking pooled connections on failed startup.
- **AVOID** — Different defaults between local and production.
- **AVOID** — Adding another global singleton instead of using the composition root.
- **AVOID** — Reading environment variables inside handlers or packages.
- **AVOID** — Reporting ready before migrations/dependencies are usable.

### NEVER

- **NEVER** — Never report readiness before required correctness dependencies and configuration are usable.
- **NEVER** — Never let termination wait forever; every drain and flush needs a bounded deadline.
- **NEVER** — Never allow feature modules to create untracked process-wide resources.

## 16. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Start with every required configuration value missing, malformed, out of range, and mutually inconsistent; assert a deterministic non-zero exit before readiness.
- [ ] Inject failure and delay at each dependency-initialization step; prove already-created resources close exactly once and startup retry is bounded.
- [ ] Send one and multiple termination signals while requests, streams, workers, and transactions are active; verify admission stops, work drains or is safely abandoned, and the process exits within the platform grace period.
- [ ] Run mixed-version rolling deployment tests for probes, configuration, ports, worker ownership, and shutdown behavior.
- [ ] Exercise pool exhaustion, file-descriptor limits, disk pressure, and telemetry sink failure without deadlock or misleading readiness.
- [ ] **REST:** Locate every implementation path for rest, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Messaging:** Locate every implementation path for messaging, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **mTLS:** Locate every implementation path for mtls, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Timeouts:** Inject slow dependencies at each hop and verify cancellation reaches database, network calls, streams, and workers.
- [ ] **Service discovery:** Rotate endpoints under long-lived connections and test TTL, negative caching, partial DNS failure, and drain.
- [ ] **Observability:** Locate every implementation path for observability, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 17. Common production bugs and incorrect implementations

- Accepting traffic before migrations/config/dependencies are ready.
- Hanging on termination because background tasks ignore cancellation.
- Double-starting workers after reload or fork.
- Leaking pooled connections on failed startup.
- Different defaults between local and production.
- **REST:** A framework or provider default for rest is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Messaging:** A framework or provider default for messaging is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Authorization:** A framework or provider default for authorization is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Retries:** A framework or provider default for retries is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Schema evolution:** A framework or provider default for schema evolution is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Service discovery:** Clients pin dead addresses, failover waits for hidden caches, or stale endpoints receive writes after removal.
- **Observability:** A framework or provider default for observability is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Adding another global singleton instead of using the composition root.
- Reading environment variables inside handlers or packages.
- Reporting ready before migrations/dependencies are usable.
- Closing shared clients while workers still run.
- Using unbounded startup or shutdown retries.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Service-to-Service Communication** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- For **REST**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for rest is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Messaging**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for messaging is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **mTLS**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for mtls is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Timeouts**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Requests wait indefinitely, downstream work continues after callers leave, or nested timeouts exceed the original budget.
- For **Service discovery**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Clients pin dead addresses, failover waits for hidden caches, or stale endpoints receive writes after removal.
- Which dependencies are fatal for startup/readiness, which are degradable, and who owns their cleanup during partial initialization?

## 20. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Service-to-Service Communication**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] **REST:** Locate every implementation path for rest, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Messaging:** Locate every implementation path for messaging, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Authorization:** Locate every implementation path for authorization, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Retries:** Locate every implementation path for retries, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Schema evolution:** Locate every implementation path for schema evolution, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Service discovery:** Rotate endpoints under long-lived connections and test TTL, negative caching, partial DNS failure, and drain.
- [ ] **Observability:** Locate every implementation path for observability, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] Locate every process-wide goroutine/thread/task, client, listener, file, and signal handler; prove ownership and cleanup ordering.

## 21. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [082. Service Discovery](082-service-discovery.md) — layer: `systems`; profile: `runtime`.
- [085. Microservice Architecture](085-microservice-architecture.md) — layer: `systems`; profile: `architecture`.
- [080. Networking Basics for Backend](080-networking-basics-for-backend.md) — layer: `systems`; profile: `runtime`.
- [079. Connection Management](079-connection-management.md) — layer: `systems`; profile: `runtime`.
- [081. Load Balancing](081-load-balancing.md) — layer: `systems`; profile: `runtime`.
- [106. Deployment Safety](../cross-cutting/106-deployment-safety.md) — layer: `cross-cutting`; profile: `runtime`.
- [011. Request Lifecycle](../primitives/011-request-lifecycle.md) — layer: `primitives`; profile: `api`.
- [002. Configuration Management](002-configuration-management.md) — layer: `systems`; profile: `runtime`.
- [105. Graceful Shutdown](../cross-cutting/105-graceful-shutdown.md) — layer: `cross-cutting`; profile: `runtime`.
- [108. Infrastructure Configuration](../cross-cutting/108-infrastructure-configuration.md) — layer: `cross-cutting`; profile: `runtime`.
- [146. Cross-Cutting Implementation Checklist](../cross-cutting/146-cross-cutting-implementation-checklist.md) — layer: `cross-cutting`; profile: `checklist`.
- [001. Project & Runtime Foundations](001-project-and-runtime-foundations.md) — layer: `systems`; profile: `runtime`.

## 22. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s122"></a> **[S122] The Twelve-Factor App.** Heroku; 2017; Current. [https://12factor.net/](https://12factor.net/) — Tags: runtime, configuration, deployment, processes.
- <a id="s123"></a> **[S123] The Twelve-Factor App: Config.** Heroku; 2017; Current. [https://12factor.net/config](https://12factor.net/config) — Tags: configuration, secrets, environment.
- <a id="s124"></a> **[S124] Linux signal(7) Manual.** Linux man-pages project; 2026; Current. [https://man7.org/linux/man-pages/man7/signal.7.html](https://man7.org/linux/man-pages/man7/signal.7.html) — Tags: signals, shutdown, processes.
- <a id="s070"></a> **[S070] Kubernetes Documentation.** Cloud Native Computing Foundation; 2026; Current. [https://kubernetes.io/docs/](https://kubernetes.io/docs/) — Tags: deployment, containers, health, shutdown, autoscaling.
- <a id="s071"></a> **[S071] Pod Lifecycle and Container Lifecycle Hooks.** Kubernetes; 2026; Current. [https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) — Tags: lifecycle, health, shutdown, deployment.
- <a id="s053"></a> **[S053] Site Reliability Engineering.** Google; 2016; Online book. [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/) — Tags: reliability, operations, monitoring, capacity.
- <a id="s077"></a> **[S077] Secure Software Development Framework.** NIST; 2022; SP 800-218 v1.1. [https://csrc.nist.gov/pubs/sp/800/218/final](https://csrc.nist.gov/pubs/sp/800/218/final) — Tags: secure-development, ci-cd, supply-chain.
- <a id="s094"></a> **[S094] HTTP/2.** IETF; 2022; RFC 9113. [https://www.rfc-editor.org/rfc/rfc9113.html](https://www.rfc-editor.org/rfc/rfc9113.html) — Tags: http2, networking, grpc.
- <a id="s095"></a> **[S095] HTTP/3.** IETF; 2022; RFC 9114. [https://www.rfc-editor.org/rfc/rfc9114.html](https://www.rfc-editor.org/rfc/rfc9114.html) — Tags: http3, quic, networking.
- <a id="s096"></a> **[S096] QUIC: A UDP-Based Multiplexed and Secure Transport.** IETF; 2021; RFC 9000. [https://www.rfc-editor.org/rfc/rfc9000.html](https://www.rfc-editor.org/rfc/rfc9000.html) — Tags: quic, networking, http3.
- <a id="s100"></a> **[S100] Zero Trust Architecture.** NIST; 2020; SP 800-207. [https://csrc.nist.gov/pubs/sp/800/207/final](https://csrc.nist.gov/pubs/sp/800/207/final) — Tags: zero-trust, service-auth, authorization.

---

**Paper metadata:** canonical subtopics: 13; layer: `systems`; domain profile: `runtime`; verified through: `2026-08-17`.
