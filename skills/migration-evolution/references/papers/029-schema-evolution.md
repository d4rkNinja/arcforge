# 029. Schema Evolution

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Schema Evolution** exists to change schemas, data, contracts, or implementations while old and new versions coexist and rollback remains possible. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

Migration ownership includes schema, data, API/event contracts, caches, indexes, jobs, and operational verification. Separate reversible deployment steps from irreversible data transformations. The migration controller must be restartable and observable; application requests should not become the hidden migration engine.

The most important evidence base for this paper includes [S040](#s040) [S041](#s041) [S061](#s061) [S128](#s128). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Deployment and migration are separate state machines whose ordering must tolerate mixed versions.
- Destructive changes are safe only after every reader and writer has stopped depending on the old representation.
- Backfills are production workloads with checkpointing, throttling, idempotency, and observability requirements.
- Dual-write creates two possible truths unless conflict resolution and reconciliation are explicit.
- Rollback may mean rolling application code forward with a fix rather than reversing an irreversible data transformation.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Schema Evolution** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- At every phase, which representation is authoritative and can old code safely read/write the new state?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Schema Evolution**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Inspect migration history and fleet version distribution; a 'removed' field may still be written by old jobs or clients.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S040](#s040) [S041](#s041) [S061](#s061) [S128](#s128)

1. **Invariant 1:** Deployment and migration are separate state machines whose ordering must tolerate mixed versions.
2. **Invariant 2:** Destructive changes are safe only after every reader and writer has stopped depending on the old representation.
3. **Invariant 3:** Backfills are production workloads with checkpointing, throttling, idempotency, and observability requirements.
4. **Invariant 4:** Dual-write creates two possible truths unless conflict resolution and reconciliation are explicit.
5. **Invariant 5:** Rollback may mean rolling application code forward with a fix rather than reversing an irreversible data transformation.

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Expand-and-contract vs maintenance window | Expand-and-contract preserves availability but takes more steps; maintenance windows simplify coordination but impose downtime. | Use expand-and-contract for continuously available systems and rehearse maintenance fallback. |
| Dual-read vs read-new-with-fallback | Dual-read enables comparison but doubles load and can hide divergence; fallback reduces risk but may retain old dependencies indefinitely. | Define a finite observation period and removal criteria. |
| Online backfill vs offline migration | Online backfills preserve service but contend with live traffic; offline migration is deterministic but requires downtime. | Choose from data volume, RTO, and write rate. |
| Rollback migration vs forward fix | Down migrations can destroy new data or be impossible; forward fixes retain history. | Prefer forward-compatible, forward-only schema changes unless a reversal is proven safe. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

Use `plan → expand → deploy compatible readers/writers → backfill → verify → switch authority → observe → contract`. Pauses and rollbacks are valid states. Do not contract until old binaries, clients, events, and rollback paths no longer require the legacy representation.

```mermaid
stateDiagram-v2
    planned --> expanded --> compatible_code_deployed --> backfilling --> verified --> authority_switched --> observed --> contracted
    backfilling --> paused
    verified --> rollback_window
    rollback_window --> compatible_code_deployed
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Define source of truth during every phase, dual-read/write precedence, conflict handling, progress cursor, batch limits, retry semantics, and completion criteria. Backfill writes need a version or predicate so they cannot overwrite newer online mutations.

A production representation commonly needs the following fields or equivalent evidence:

- migration/version identifier and immutable plan/configuration.
- range/cursor, batch identity, attempts, and per-unit result.
- source/target versions and authority phase.
- verification counts, discrepancies, and samples.
- pause/abort/rollback/forward-fix state and operator audit.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **Additive changes**
- **Column changes**
- **Default changes**
- **Expand-and-contract**
- **Old-client compatibility**

### 8.2. Destructive changes

- **SHOULD — engineering rule:** Use expand-and-contract: add the new representation, deploy compatible readers/writers, backfill and verify, switch reads, stop old writes, then remove after the compatibility horizon.
- **Production failure mode:** Mixed versions lose data, defaults change meaning, or rollback becomes impossible.
- **Existing-codebase evidence:** Record per-stage invariants and gates; inspect telemetry proving old reads/writes have ceased before contraction.

### 8.4. Field renaming

- **SHOULD — engineering rule:** Use expand-and-contract: add the new representation, deploy compatible readers/writers, backfill and verify, switch reads, stop old writes, then remove after the compatibility horizon.
- **Production failure mode:** Mixed versions lose data, defaults change meaning, or rollback becomes impossible.
- **Existing-codebase evidence:** Record per-stage invariants and gates; inspect telemetry proving old reads/writes have ceased before contraction.

### 8.5. Type changes

- **SHOULD — engineering rule:** Use expand-and-contract: add the new representation, deploy compatible readers/writers, backfill and verify, switch reads, stop old writes, then remove after the compatibility horizon.
- **Production failure mode:** Mixed versions lose data, defaults change meaning, or rollback becomes impossible.
- **Existing-codebase evidence:** Record per-stage invariants and gates; inspect telemetry proving old reads/writes have ceased before contraction.

### 8.7. Nullable → required

- **SHOULD — engineering rule:** Use expand-and-contract: add the new representation, deploy compatible readers/writers, backfill and verify, switch reads, stop old writes, then remove after the compatibility horizon.
- **Production failure mode:** Mixed versions lose data, defaults change meaning, or rollback becomes impossible.
- **Existing-codebase evidence:** Record per-stage invariants and gates; inspect telemetry proving old reads/writes have ceased before contraction.

### 8.9. Dual-read

- **SHOULD — engineering rule:** Assign a canonical truth, stable operation ID/version, ordering and conflict rules, compare outcomes, reconcile divergence, and define a finite exit criterion.
- **Production failure mode:** Two stores diverge after partial failure and operators cannot tell which copy is correct.
- **Existing-codebase evidence:** Inject failure on each side and verify repair, metrics, replay, and rollback without duplicate side effects.

### 8.10. Dual-write

- **SHOULD — engineering rule:** Assign a canonical truth, stable operation ID/version, ordering and conflict rules, compare outcomes, reconcile divergence, and define a finite exit criterion.
- **Production failure mode:** Two stores diverge after partial failure and operators cannot tell which copy is correct.
- **Existing-codebase evidence:** Inject failure on each side and verify repair, metrics, replay, and rollback without duplicate side effects.

### 8.11. Backward compatibility

- **SHOULD — engineering rule:** Define a compatibility window in which old and new readers/writers coexist. Make changes additive first, preserve unknown fields where required, and test both deployment orders.
- **Production failure mode:** A new writer emits data an old reader cannot parse, or rollback code cannot read records created during the failed release.
- **Existing-codebase evidence:** Run an N/N+1 matrix for requests, stored data, events, queues, caches, and rollback.

## 9. Concurrency, transactions, idempotency, and consistency

Dual writes are not atomic across independent systems; expect divergence and reconcile it. Online schema operations can lock tables or saturate replicas even when documented as concurrent. Throttle by database health, use resumable chunks, and verify counts plus semantic invariants.

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

Deploy rollback may be safe while data rollback is not. Workers can crash mid-batch, cursors can advance prematurely, and old writers can recreate legacy state. Record per-range progress, make each unit idempotent, and retain a forward-fix path for irreversible steps.

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

Expose processed/succeeded/skipped/failed counts, throughput, lag, conflict rate, database load, replica lag, lock waits, and verification discrepancies. Preserve samples and deterministic queries for audit. Provide pause, resume, rate adjustment, and safe abort controls.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

The whole topic is evolution: compatibility must be proven in a matrix of old/new readers and writers. Feature flags should control authority, not mask incompatible storage. Contract removal requires usage evidence and an explicit sunset, not an assumption that every client upgraded.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Schema Evolution path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Additive changes`, `Field renaming`, `Nullable → required`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Schema Evolution; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Schema Evolution** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Type changes**: Use expand-and-contract: add the new representation, deploy compatible readers/writers, backfill and verify, switch reads, stop old writes, then remove after the compatibility horizon.

### SHOULD

- **SHOULD** — Deployment and migration are separate state machines whose ordering must tolerate mixed versions.
- **SHOULD** — Destructive changes are safe only after every reader and writer has stopped depending on the old representation.
- **SHOULD** — Backfills are production workloads with checkpointing, throttling, idempotency, and observability requirements.
- **SHOULD** — Dual-write creates two possible truths unless conflict resolution and reconciliation are explicit.
- **SHOULD** — Rollback may mean rolling application code forward with a fix rather than reversing an irreversible data transformation.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Adopt the **Expand-and-contract vs maintenance window** option that fits the workload and ownership boundary; Use expand-and-contract for continuously available systems and rehearse maintenance fallback.
- **MAY** — Adopt the **Dual-read vs read-new-with-fallback** option that fits the workload and ownership boundary; Define a finite observation period and removal criteria.
- **MAY** — Adopt the **Online backfill vs offline migration** option that fits the workload and ownership boundary; Choose from data volume, RTO, and write rate.

### AVOID

- **AVOID** — Dropping a column while old pods still write it.
- **AVOID** — Backfill restarting from zero after failure.
- **AVOID** — Dual-write divergence without detection.
- **AVOID** — Index build saturating I/O.
- **AVOID** — Rollback code unable to read newly written data.
- **AVOID** — Backfilling in request handlers.
- **AVOID** — Advancing progress before effects commit.
- **AVOID** — Dual-writing without divergence detection.

### NEVER

- **NEVER** — Never perform an incompatible destructive change before compatible code is fully deployed and rollback is retired.
- **NEVER** — Never let a backfill overwrite a newer online update without a version/predicate.
- **NEVER** — Never declare migration complete from row count alone; verify domain invariants and consumers.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Exercise every old/new reader-writer combination through expand, backfill, switch, rollback, and contract phases.
- [ ] Kill and restart the migrator at every batch boundary; prove cursor correctness, idempotency, and no overwrite of newer online writes.
- [ ] Throttle and pause under lock waits, replica lag, queue lag, cache pressure, and production-like load.
- [ ] Compare counts, hashes/samples, constraints, and domain invariants before authority switch and after cleanup.
- [ ] Rollback application versions after new schema/data/events exist; prove old code remains safe or is explicitly blocked.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Contracting before old code and rollback are gone.
- Overwriting newer online data with stale backfill values.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [134. Zero-Downtime Changes](134-zero-downtime-changes.md)
- [070. API / Event Schema Evolution](070-api-event-schema-evolution.md)
- [135. Feature Migration](135-feature-migration.md)
- 015. API Versioning & Compatibility — in the `api-contracts` skill.
- [030. Database Migrations](030-database-migrations.md)
- [136. Legacy-System Integration](136-legacy-system-integration.md)
- [031. Data Migrations & Backfills](031-data-migrations-and-backfills.md)
- [071. Backward Compatibility](071-backward-compatibility.md)
- [073. Change Data Capture](073-change-data-capture.md)
- [072. Data Synchronization](072-data-synchronization.md)
- 106. Deployment Safety — in the `runtime-delivery` skill.
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s028"></a> **[S028] OpenAPI Specification.** OpenAPI Initiative; 2025; 3.2.0. [https://spec.openapis.org/oas/v3.2.0.html](https://spec.openapis.org/oas/v3.2.0.html) — Tags: api, schema, compatibility, documentation.
- <a id="s031"></a> **[S031] Protocol Buffers Programming Guides.** Google; 2026; Current documentation. [https://protobuf.dev/programming-guides/](https://protobuf.dev/programming-guides/) — Tags: protobuf, serialization, schema-evolution.
- <a id="s032"></a> **[S032] AsyncAPI Specification.** AsyncAPI Initiative; 2026; 3.1.0. [https://www.asyncapi.com/docs/reference/specification/v3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0) — Tags: events, messaging, schema, api.
- <a id="s040"></a> **[S040] PostgreSQL Documentation.** PostgreSQL Global Development Group; 2026; 18 current. [https://www.postgresql.org/docs/18/](https://www.postgresql.org/docs/18/) — Tags: database, sql, transactions, indexes, concurrency, backup.
- <a id="s041"></a> **[S041] MongoDB Manual.** MongoDB; 2026; 8.0. [https://www.mongodb.com/docs/v8.0/](https://www.mongodb.com/docs/v8.0/) — Tags: database, documents, transactions, indexes, sharding.
- <a id="s043"></a> **[S043] Designing Data-Intensive Applications, Second Edition.** Martin Kleppmann and Chris Riccomini / O'Reilly; 2025; 2nd edition. [https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/) — Tags: distributed-systems, databases, consistency, streams.
- <a id="s061"></a> **[S061] Debezium Documentation.** Red Hat / Debezium; 2026; Current. [https://debezium.io/documentation/](https://debezium.io/documentation/) — Tags: cdc, outbox, events, database.
- <a id="s070"></a> **[S070] Kubernetes Documentation.** Cloud Native Computing Foundation; 2026; Current. [https://kubernetes.io/docs/](https://kubernetes.io/docs/) — Tags: deployment, containers, health, shutdown, autoscaling.
- <a id="s128"></a> **[S128] Kubernetes Deployments.** Kubernetes; 2026; Current. [https://kubernetes.io/docs/concepts/workloads/controllers/deployment/](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) — Tags: deployment, rolling-update, rollback.
