---
paper_number: 132
title: "Multi-Region Systems"
layer: cross-cutting
domain_profile: backup_dr
corpus_version: 1.0.0
verified_through: 2026-08-17
canonical_source: "original/Pasted text.txt"
subtopic_count: 11
status: production-engineering-reference
---

# 132. Multi-Region Systems

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Multi-Region Systems** exists to restore correct service and data after deletion, corruption, regional failure, or operator error within explicit recovery objectives. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

Recovery scope includes databases, object storage, search indexes, queues or replay logs, configuration, secrets/keys, identity, DNS, and external-provider state. Replication is an availability mechanism, not an independent backup. Assign ownership for backup creation, verification, restore orchestration, failover, and business validation.

The most important evidence base for this paper includes [S084](#s084) [S085](#s085) [S040](#s040) [S041](#s041). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- A backup is not proven until a restore is performed and validated.
- RPO and RTO are end-to-end business properties, not storage-product settings.
- Replication improves availability but can replicate corruption and deletion.
- Backups inherit data residency, encryption, retention, and deletion obligations.
- Restore creates conflicts with live writes, identities, event streams, caches, and external systems.

## 2. Scope and terminology map

The canonical topic list requires this paper to cover the following concerns. They are grouped only to expose relationships; no listed subtopic is omitted.

### Identity, trust, and access

**Regional data ownership**.

### Concurrency and distributed behavior

**Cross-region replication**.

### Operations and observability

**Region selection**, **Geo routing**, **Active/active**, **Active/passive**, **Failover**, **Data residency**, **Conflict resolution**, **Latency**, **Regional outages**.

### Boundary of the paper

This paper treats **Multi-Region Systems** as a production subsystem or reusable reasoning primitive. It covers semantics, ownership, persistence, APIs, security, concurrency, distributed behavior, operations, evolution, and verification. Framework syntax and large implementation listings are intentionally excluded.

## 3. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S084](#s084) [S085](#s085) [S040](#s040) [S041](#s041)

1. **Invariant 1:** A backup is not proven until a restore is performed and validated.
2. **Invariant 2:** RPO and RTO are end-to-end business properties, not storage-product settings.
3. **Invariant 3:** Replication improves availability but can replicate corruption and deletion.
4. **Invariant 4:** Backups inherit data residency, encryption, retention, and deletion obligations.
5. **Invariant 5:** Restore creates conflicts with live writes, identities, event streams, caches, and external systems.

Additional topic-specific invariants:

- **SHOULD — Region selection:** Define the exact semantics of **Region selection** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MAY — Active/active:** Define the exact semantics of **Active/active** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Cross-region replication:** Specify write acknowledgment, read consistency, lag bounds, failover fencing, conflict handling, and behavior during partitions. Do not equate replication with backup.
- **SHOULD — Failover:** Define the exact semantics of **Failover** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Conflict resolution:** Define the exact semantics of **Conflict resolution** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Regional outages:** Define the exact semantics of **Regional outages** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.

## 4. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Active/passive vs active/active | Active/passive simplifies write authority; active/active improves latency/availability but demands conflict resolution and fencing. | Choose from write semantics, RPO/RTO, and operational maturity. |
| Snapshot vs logical backup | Snapshots are fast and consistent at storage level; logical backups are portable and granular but slower. | Use complementary methods for different failure modes. |
| Full vs incremental | Full backups simplify restore; incremental backups reduce cost but lengthen dependency chains. | Bound chain length and regularly test full reconstruction. |
| Active/passive vs active/active region | Active/passive simplifies consistency; active/active improves latency and availability but needs conflict handling. | Choose from write semantics and operational maturity. |
| Automatic vs manual failover | Automatic failover reduces downtime but can amplify split-brain; manual failover is slower but deliberate. | Automate only when fencing and validation are reliable. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 5. Ownership, state, and lifecycle

Protected data moves through `captured → encrypted → copied → verified → retained → expired`, while an incident moves `detected → contained/fenced → restore_point_selected → restored → reconciled → traffic_resumed → validated`. Failback is a separate controlled migration.

```mermaid
stateDiagram-v2
    captured --> encrypted --> copied --> verified --> retained --> expired
    incident_detected --> fenced --> restore_point_selected --> restored --> reconciled --> traffic_resumed --> validated
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 6. Data model and API implications

Define RPO, RTO, restore granularity, consistency groups, encryption/key dependencies, retention, residency, legal hold, and validation criteria. A successful backup job means little without a tested restore that proves application invariants and dependent assets.

A production representation commonly needs the following fields or equivalent evidence:

- backup/snapshot identifier, source system/version, consistency position, and region.
- coverage manifest for databases, objects, keys, configurations, and logs.
- encryption/key version, retention, residency, and legal-hold status.
- verification and restore-drill results.
- incident restore point, fencing, reconciliation, and validation state.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 7. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### 7.1. Region selection

- **SHOULD — engineering rule:** Define the exact semantics of **Region selection** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for region selection is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for region selection, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.2. Geo routing

- **SHOULD — engineering rule:** Define the exact semantics of **Geo routing** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for geo routing is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for geo routing, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.3. Active/active

- **MAY — engineering rule:** Define the exact semantics of **Active/active** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for active/active is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for active/active, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.4. Active/passive

- **SHOULD — engineering rule:** Define the exact semantics of **Active/passive** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for active/passive is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for active/passive, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.5. Cross-region replication

- **SHOULD — engineering rule:** Specify write acknowledgment, read consistency, lag bounds, failover fencing, conflict handling, and behavior during partitions. Do not equate replication with backup.
- **Production failure mode:** Stale reads violate workflows, failover loses acknowledged writes, or split-brain accepts conflicting updates.
- **Existing-codebase evidence:** Inject lag, leader loss, partition, and failback; verify documented read/write guarantees and conflict outcomes.

### 7.6. Regional data ownership

- **MUST — engineering rule:** Assign one owner for invariants and writes, expose a narrow versioned interface, enforce dependency direction mechanically, and communicate cross-boundary facts through explicit calls/events.
- **Production failure mode:** Modules share tables/models/utilities until changes require lockstep deployment and no team can reason locally.
- **Existing-codebase evidence:** Build an import/dependency graph, map table writes, and flag cross-boundary direct access.

### 7.7. Failover

- **SHOULD — engineering rule:** Define the exact semantics of **Failover** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for failover is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for failover, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.8. Data residency

- **SHOULD — engineering rule:** Define the exact semantics of **Data residency** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for data residency is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for data residency, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.9. Conflict resolution

- **SHOULD — engineering rule:** Define the exact semantics of **Conflict resolution** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for conflict resolution is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for conflict resolution, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.10. Latency

- **SHOULD — engineering rule:** Define the exact semantics of **Latency** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for latency is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for latency, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.11. Regional outages

- **SHOULD — engineering rule:** Define the exact semantics of **Regional outages** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for regional outages is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for regional outages, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

## 8. Concurrency, transactions, idempotency, and consistency

Cross-store snapshots may represent different moments. Choose application-consistent checkpoints, quiescence, transaction-log positions, or reconciliation. During failover, fence the old writer to prevent split brain. After restore, reset caches and derived indexes, reconcile external side effects, and handle replay carefully.

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

Backups may be corrupt, incomplete, encrypted with unavailable keys, or contain already-corrupted data. PITR can replay the destructive action being recovered from. Regional failover can expose replica lag or DNS caching. Practice multiple failure modes and retain more than one recovery generation.

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

Monitor backup age, duration, size, success, copy/replication lag, restore-test recency, restore duration, verification discrepancies, key access, and capacity. Recovery drills need timestamps, decisions, commands, owners, and post-restore checks recorded for runbook improvement.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 13. Compatibility, schema evolution, migration, deployment, and rollback

Schema and application versions must be recoverable together. Keep migration artifacts and compatible binaries for retained restore points or document forward-migration procedures. Changing region, encryption, or retention requires validation of old backups and deletion obligations.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Multi-Region Systems path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Region selection`, `Active/active`, `Regional data ownership`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Multi-Region Systems; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Measure RPO/RTO through validated service restoration, fence former writers, restore dependent assets and keys, rebuild derived stores, and reconcile external effects. |

## 15. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Multi-Region Systems** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Region selection**: Define the exact semantics of **Region selection** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **Active/active**: Define the exact semantics of **Active/active** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **Cross-region replication**: Specify write acknowledgment, read consistency, lag bounds, failover fencing, conflict handling, and behavior during partitions. Do not equate replication with backup.
- **MUST** — For **Failover**: Define the exact semantics of **Failover** within Multi-Region Systems: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.

### SHOULD

- **SHOULD** — A backup is not proven until a restore is performed and validated.
- **SHOULD** — RPO and RTO are end-to-end business properties, not storage-product settings.
- **SHOULD** — Replication improves availability but can replicate corruption and deletion.
- **SHOULD** — Backups inherit data residency, encryption, retention, and deletion obligations.
- **SHOULD** — Restore creates conflicts with live writes, identities, event streams, caches, and external systems.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Choose **Active/passive vs active/active** according to the stated trade-off: Choose from write semantics, RPO/RTO, and operational maturity.
- **MAY** — Adopt the **Snapshot vs logical backup** option that fits the workload and ownership boundary; Use complementary methods for different failure modes.
- **MAY** — Adopt the **Full vs incremental** option that fits the workload and ownership boundary; Bound chain length and regularly test full reconstruction.
- **MAY** — Adopt the **Active/passive vs active/active region** option that fits the workload and ownership boundary; Choose from write semantics and operational maturity.

### AVOID

- **AVOID** — Backup jobs succeeding but producing unrestorable data.
- **AVOID** — Restoring database without object storage or keys.
- **AVOID** — PITR replaying unwanted destructive operations.
- **AVOID** — Failover without fencing old primary.
- **AVOID** — Deleted PII persisting indefinitely in backups without policy.
- **AVOID** — Equating replication with backup.
- **AVOID** — Claiming backup success without restore verification.
- **AVOID** — Restoring only the database.

### NEVER

- **NEVER** — Never call data protected until a restore has been executed and validated.
- **NEVER** — Never fail over while the old writer can still accept authoritative writes.
- **NEVER** — Never assume one backup generation covers corruption discovered after its creation.

## 16. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Restore each backup type into an isolated environment and validate application invariants, object storage, indexes, keys, identities, and event positions.
- [ ] Perform point-in-time recovery before and after destructive/corrupting operations; verify the selected point and replay boundary.
- [ ] Simulate zone/region loss, DNS caching, replica lag, old-primary return, and failback; prove fencing and conflict handling.
- [ ] Measure actual RPO/RTO from detection through validated traffic restoration, not only storage restore duration.
- [ ] Exercise deletion/legal-hold/residency policy across retained backups and cross-region copies.
- [ ] **Region selection:** Locate every implementation path for region selection, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Active/active:** Locate every implementation path for active/active, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Cross-region replication:** Inject lag, leader loss, partition, and failback; verify documented read/write guarantees and conflict outcomes.
- [ ] **Failover:** Locate every implementation path for failover, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Conflict resolution:** Locate every implementation path for conflict resolution, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Regional outages:** Locate every implementation path for regional outages, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 17. Common production bugs and incorrect implementations

- Backup jobs succeeding but producing unrestorable data.
- Restoring database without object storage or keys.
- PITR replaying unwanted destructive operations.
- Failover without fencing old primary.
- Deleted PII persisting indefinitely in backups without policy.
- **Region selection:** A framework or provider default for region selection is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Active/active:** A framework or provider default for active/active is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Active/passive:** A framework or provider default for active/passive is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Regional data ownership:** Modules share tables/models/utilities until changes require lockstep deployment and no team can reason locally.
- **Data residency:** A framework or provider default for data residency is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Conflict resolution:** A framework or provider default for conflict resolution is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Regional outages:** A framework or provider default for regional outages is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Equating replication with backup.
- Claiming backup success without restore verification.
- Restoring only the database.
- Failing over without fencing the old writer.
- Ignoring keys, residency, and deleted-data policy.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Multi-Region Systems** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- For **Region selection**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for region selection is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Active/active**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for active/active is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Cross-region replication**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Stale reads violate workflows, failover loses acknowledged writes, or split-brain accepts conflicting updates.
- For **Failover**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for failover is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Conflict resolution**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for conflict resolution is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- Can the full application—not only one database—be restored and validated within measured RPO/RTO?

## 20. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Multi-Region Systems**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] **Region selection:** Locate every implementation path for region selection, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Active/active:** Locate every implementation path for active/active, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Active/passive:** Locate every implementation path for active/passive, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Regional data ownership:** Build an import/dependency graph, map table writes, and flag cross-boundary direct access.
- [ ] **Data residency:** Locate every implementation path for data residency, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Conflict resolution:** Locate every implementation path for conflict resolution, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Regional outages:** Locate every implementation path for regional outages, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] Read the latest restore-drill evidence; backup configuration alone is not proof.

## 21. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [097. High Availability](097-high-availability.md) — layer: `cross-cutting`; profile: `backup_dr`.
- [133. Data Residency](133-data-residency.md) — layer: `cross-cutting`; profile: `backup_dr`.
- [078. Disaster Recovery](078-disaster-recovery.md) — layer: `cross-cutting`; profile: `backup_dr`.
- [076. Backup](076-backup.md) — layer: `cross-cutting`; profile: `backup_dr`.
- [010. Multi-Tenancy](../systems/010-multi-tenancy.md) — layer: `systems`; profile: `authorization`.
- [131. Distributed Cache Coordination](131-distributed-cache-coordination.md) — layer: `cross-cutting`; profile: `cache`.
- [101. Partitioning / Sharding](101-partitioning-sharding.md) — layer: `cross-cutting`; profile: `transactions`.
- [071. Backward Compatibility](../primitives/071-backward-compatibility.md) — layer: `primitives`; profile: `migration`.
- [100. Replication](100-replication.md) — layer: `cross-cutting`; profile: `transactions`.
- [081. Load Balancing](../systems/081-load-balancing.md) — layer: `systems`; profile: `runtime`.
- [077. Restore](077-restore.md) — layer: `cross-cutting`; profile: `backup_dr`.
- [146. Cross-Cutting Implementation Checklist](146-cross-cutting-implementation-checklist.md) — layer: `cross-cutting`; profile: `checklist`.

## 22. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s040"></a> **[S040] PostgreSQL Documentation.** PostgreSQL Global Development Group; 2026; 18 current. [https://www.postgresql.org/docs/18/](https://www.postgresql.org/docs/18/) — Tags: database, sql, transactions, indexes, concurrency, backup.
- <a id="s041"></a> **[S041] MongoDB Manual.** MongoDB; 2026; 8.0. [https://www.mongodb.com/docs/v8.0/](https://www.mongodb.com/docs/v8.0/) — Tags: database, documents, transactions, indexes, sharding.
- <a id="s053"></a> **[S053] Site Reliability Engineering.** Google; 2016; Online book. [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/) — Tags: reliability, operations, monitoring, capacity.
- <a id="s070"></a> **[S070] Kubernetes Documentation.** Cloud Native Computing Foundation; 2026; Current. [https://kubernetes.io/docs/](https://kubernetes.io/docs/) — Tags: deployment, containers, health, shutdown, autoscaling.
- <a id="s084"></a> **[S084] Contingency Planning Guide for Federal Information Systems.** NIST; 2010; SP 800-34 Rev. 1. [https://csrc.nist.gov/pubs/sp/800/34/r1/final](https://csrc.nist.gov/pubs/sp/800/34/r1/final) — Tags: backup, restore, disaster-recovery, rpo, rto.
- <a id="s085"></a> **[S085] Amazon S3 User Guide.** AWS; 2026; Current. [https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html) — Tags: files, object-storage, multipart, signed-urls.
- <a id="s101"></a> **[S101] Computer Security Incident Handling Guide.** NIST; 2025; SP 800-61 Rev. 3. [https://csrc.nist.gov/pubs/sp/800/61/r3/final](https://csrc.nist.gov/pubs/sp/800/61/r3/final) — Tags: incidents, operations, recovery.
- <a id="s050"></a> **[S050] Spanner: Google's Globally-Distributed Database.** Google Research; 2012; OSDI 2012. [https://research.google/pubs/spanner-googles-globally-distributed-database/](https://research.google/pubs/spanner-googles-globally-distributed-database/) — Tags: database, replication, transactions, time.
- <a id="s081"></a> **[S081] Privacy Framework.** NIST; 2020; 1.0. [https://www.nist.gov/privacy-framework](https://www.nist.gov/privacy-framework) — Tags: privacy, pii, risk.
- <a id="s082"></a> **[S082] General Data Protection Regulation.** European Union; 2016; Regulation (EU) 2016/679. [https://eur-lex.europa.eu/eli/reg/2016/679/oj](https://eur-lex.europa.eu/eli/reg/2016/679/oj) — Tags: privacy, retention, deletion, consent.
- <a id="s131"></a> **[S131] AWS Well-Architected SaaS Lens.** AWS; 2026; Current. [https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/saas-lens.html](https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/saas-lens.html) — Tags: multi-tenancy, saas, operations.
- <a id="s132"></a> **[S132] Architecture approaches for storage and data in multitenant solutions.** Microsoft Azure; 2026; Current. [https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/storage-data](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/storage-data) — Tags: multi-tenancy, database, isolation.

---

**Paper metadata:** canonical subtopics: 11; layer: `cross-cutting`; domain profile: `backup_dr`; verified through: `2026-08-17`.
