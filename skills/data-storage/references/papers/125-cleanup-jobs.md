# 125. Cleanup Jobs

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Cleanup Jobs** exists to move, reconcile, version, deduplicate, and retire data without losing provenance or violating ownership and consistency. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

Data movement and cleanup workflows must name a canonical source, ownership scope, provenance, conflict policy, and completion evidence. Imports, exports, batch edits, dedupe, reconciliation, and cleanup are production write paths, not maintenance scripts exempt from security and correctness controls.

The most important evidence base for this paper includes [S040](#s040) [S041](#s041) [S043](#s043) [S061](#s061). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Bulk and batch work must expose per-item outcome or define true atomicity; 'success' cannot hide partial failure.
- Every derived or synchronized copy needs a canonical owner, version or change token, and deletion semantics.
- Deduplication requires a stable identity or fingerprint plus a scope and retention window.
- Cleanup is a correctness process with retention, legal hold, references, and retry behavior—not a periodic delete-all query.
- Temporary data is security-sensitive because its short lifetime often encourages weak storage and validation.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Cleanup Jobs** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- How does a crashed run resume without replaying already-successful items or advancing a cursor early?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Cleanup Jobs**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Inspect previously interrupted jobs, dedupe records, cursors, quarantine tables, and cleanup ownership.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S040](#s040) [S041](#s041) [S043](#s043) [S061](#s061)

1. **Invariant 1:** Bulk and batch work must expose per-item outcome or define true atomicity; 'success' cannot hide partial failure.
2. **Invariant 2:** Every derived or synchronized copy needs a canonical owner, version or change token, and deletion semantics.
3. **Invariant 3:** Deduplication requires a stable identity or fingerprint plus a scope and retention window.
4. **Invariant 4:** Cleanup is a correctness process with retention, legal hold, references, and retry behavior—not a periodic delete-all query.
5. **Invariant 5:** Temporary data is security-sensitive because its short lifetime often encourages weak storage and validation.

Additional topic-specific invariants:

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Atomic batch vs partial success | Atomic batches simplify consistency but hit transaction and size limits; partial success scales but needs item-level state. | Choose explicitly and make retries resume only failed items. |
| Full vs incremental sync | Full sync is simple and self-healing but expensive; incremental sync is efficient but depends on durable cursors/tombstones. | Use periodic full reconciliation around incremental sync. |
| Natural key vs fingerprint dedupe | Natural keys are explainable but may change; fingerprints work without identifiers but have collision and normalization risks. | Prefer stable domain keys and version fingerprints carefully. |
| Delete vs tombstone | Hard delete frees storage; tombstones preserve propagation and audit. | Retain tombstones until every replica/consumer has crossed the deletion horizon. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

Use `discovered/received → validated → staged → applied → reconciled → finalized`, with per-item `failed`, `quarantined`, `skipped`, and `retryable` states. Cursors, temporary objects, tombstones, and dedupe records need retention and cleanup lifecycles.

```mermaid
stateDiagram-v2
    received_or_discovered --> validated --> staged --> applied --> reconciled --> finalized
    validated --> quarantined
    applied --> partial_failure --> resumable
    finalized --> retained_or_cleaned
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Define file/schema version, mapping, validation severity, duplicate identity, atomic versus partial success, batch size, progress cursor, resume token, and per-item result format. Exports must define snapshot consistency, permission point-in-time, sensitive-field filtering, and download expiry.

A production representation commonly needs the following fields or equivalent evidence:

- operation/run ID, source, schema/mapping version, tenant/owner, and actor.
- item stable identity/fingerprint and per-item state/result.
- cursor/range/batch, attempts, progress, and resume token.
- provenance, source/target versions, conflicts, and repair decisions.
- temporary artifact, retention, quarantine, export permission, and cleanup state.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **Expired sessions**
- **Expired tokens**
- **Old logs**
- **Soft-deleted data**
- **Stale locks**
- **Dead jobs**
- **Temporary records**
- **Retention enforcement**

### 8.3. Orphan files

- **SHOULD — engineering rule:** Define ownership and delete/update behavior explicitly. Use database enforcement where relationships share a transactional store; otherwise maintain tombstones, events, and reconciliation.
- **Production failure mode:** Partial failure or deletion leaves references that crash reads, leak data, or prevent retention enforcement.
- **Existing-codebase evidence:** Delete and restore principals/resources under concurrent writes, then run integrity queries for every relationship.

### 8.9. Old idempotency keys

- **MUST — engineering rule:** Scope keys to caller and operation, bind them to a canonical request fingerprint, reserve atomically, persist terminal outcome, and distinguish in-progress, succeeded, retryable-failed, and permanently-failed states.
- **Production failure mode:** Two concurrent requests both execute, or the same key is reused with different parameters and returns the wrong result.
- **Existing-codebase evidence:** Synchronize duplicate requests before first commit; test timeout-after-commit, key mismatch, expiry, and response replay.

## 9. Concurrency, transactions, idempotency, and consistency

Advance cursors only in the same durable boundary as effects or record replay-safe intent. Use stable item identities and conditional writes to avoid duplicates. Reconciliation compares canonical versions and repairs idempotently; automated repair needs bounds and audit.

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

Large files, malformed rows, mid-batch crash, duplicate upload, changed source during export, expired credentials, and partial downstream success are normal. Quarantine rather than silently coerce ambiguous data. Never retry an entire partially successful batch without item-level dedupe.

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

Track total/validated/applied/skipped/failed items, bytes, throughput, lag, cursor, duplicates, conflicts, repair actions, cleanup age, and storage usage. Provide pause/resume/cancel, downloadable error reports with access control, and immutable audit of bulk changes.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

Version import/export schemas and mapping rules. Old jobs may resume after a deployment, so executors must understand their recorded version. Retain compatibility or migrate job state explicitly. Cleanup of old artifacts must honor audit, legal hold, and replay windows.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Cleanup Jobs path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Expired sessions`, `Orphan files`, `Soft-deleted data`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Cleanup Jobs; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Cleanup Jobs** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Orphan files**: Define ownership and delete/update behavior explicitly. Use database enforcement where relationships share a transactional store; otherwise maintain tombstones, events, and reconciliation.

### SHOULD

- **SHOULD** — Bulk and batch work must expose per-item outcome or define true atomicity; 'success' cannot hide partial failure.
- **SHOULD** — Every derived or synchronized copy needs a canonical owner, version or change token, and deletion semantics.
- **SHOULD** — Deduplication requires a stable identity or fingerprint plus a scope and retention window.
- **SHOULD** — Cleanup is a correctness process with retention, legal hold, references, and retry behavior—not a periodic delete-all query.
- **SHOULD** — Temporary data is security-sensitive because its short lifetime often encourages weak storage and validation.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Adopt the **Atomic batch vs partial success** option that fits the workload and ownership boundary; Choose explicitly and make retries resume only failed items.
- **MAY** — Adopt the **Full vs incremental sync** option that fits the workload and ownership boundary; Use periodic full reconciliation around incremental sync.
- **MAY** — Adopt the **Natural key vs fingerprint dedupe** option that fits the workload and ownership boundary; Prefer stable domain keys and version fingerprints carefully.

### AVOID

- **AVOID** — Retrying whole import and duplicating successful rows.
- **AVOID** — Sync cursor advanced before effects commit.
- **AVOID** — Cleanup deleting live referenced data.
- **AVOID** — Dedupe key shared across tenants.
- **AVOID** — Temporary token left valid after use.
- **AVOID** — Retrying the whole partially successful batch.
- **AVOID** — Using row number as durable identity.
- **AVOID** — Advancing sync cursor early.

### NEVER

- **NEVER** — Never advance a durable cursor before corresponding effects are committed or replay-safe.
- **NEVER** — Never retry an entire partially successful operation without item-level deduplication.
- **NEVER** — Never purge data without checking retention, legal hold, references, replicas, and derived copies.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Kill and resume every batch/import/export/cleanup phase; item outcomes and cursors must remain correct.
- [ ] Upload or schedule duplicates with changed ordering, formatting, and normalization; dedupe scope must be stable and tenant-aware.
- [ ] Inject malformed records, partial provider success, expired downloads, source mutation, and insufficient permissions.
- [ ] Reconcile canonical and derived stores with missing, duplicate, stale, and conflicting records; repairs must be bounded and idempotent.
- [ ] Run at production-shaped size while monitoring locks, lag, disk, memory, and impact on foreground traffic.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Hard-deleting before tombstones propagate.
- Running cleanup without legal hold/reference checks.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- 126. Temporary Data — in the `security-privacy` skill.
- [032. Soft Delete / Hard Delete](032-soft-delete-hard-delete.md)
- [124. Data Reconciliation](124-data-reconciliation.md)
- [033. Data Lifecycle](033-data-lifecycle.md)
- 037. Caching — in the `resilience-flow-control` skill.
- 120. Deduplication — in the `async-messaging` skill.
- [026. Data Integrity](026-data-integrity.md)
- 066. Privacy & Sensitive Data — in the `security-privacy` skill.
- 127. Randomness & Token Generation — in the `security-privacy` skill.
- [034. Immutable Data](034-immutable-data.md)
- 043. Background Jobs — in the `async-messaging` skill.
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s033"></a> **[S033] JSON Schema.** JSON Schema; 2022; Draft 2020-12. [https://json-schema.org/draft/2020-12](https://json-schema.org/draft/2020-12) — Tags: json, validation, schema.
- <a id="s040"></a> **[S040] PostgreSQL Documentation.** PostgreSQL Global Development Group; 2026; 18 current. [https://www.postgresql.org/docs/18/](https://www.postgresql.org/docs/18/) — Tags: database, sql, transactions, indexes, concurrency, backup.
- <a id="s041"></a> **[S041] MongoDB Manual.** MongoDB; 2026; 8.0. [https://www.mongodb.com/docs/v8.0/](https://www.mongodb.com/docs/v8.0/) — Tags: database, documents, transactions, indexes, sharding.
- <a id="s043"></a> **[S043] Designing Data-Intensive Applications, Second Edition.** Martin Kleppmann and Chris Riccomini / O'Reilly; 2025; 2nd edition. [https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/) — Tags: distributed-systems, databases, consistency, streams.
- <a id="s061"></a> **[S061] Debezium Documentation.** Red Hat / Debezium; 2026; Current. [https://debezium.io/documentation/](https://debezium.io/documentation/) — Tags: cdc, outbox, events, database.
- <a id="s082"></a> **[S082] General Data Protection Regulation.** European Union; 2016; Regulation (EU) 2016/679. [https://eur-lex.europa.eu/eli/reg/2016/679/oj](https://eur-lex.europa.eu/eli/reg/2016/679/oj) — Tags: privacy, retention, deletion, consent.
- <a id="s114"></a> **[S114] Google API Improvement Proposals.** Google; 2026; Current. [https://google.aip.dev/](https://google.aip.dev/) — Tags: api, pagination, versioning, resource-design.
- <a id="s137"></a> **[S137] ACM Queue: Idempotence Is Not a Medical Condition.** Pat Helland / ACM; 2012; ACM Queue. [https://queue.acm.org/detail.cfm?id=2187821](https://queue.acm.org/detail.cfm?id=2187821) — Tags: idempotency, distributed-systems, retries.
- <a id="s034"></a> **[S034] Universally Unique IDentifiers (UUIDs).** IETF; 2024; RFC 9562. [https://www.rfc-editor.org/rfc/rfc9562.html](https://www.rfc-editor.org/rfc/rfc9562.html) — Tags: identifiers, uuid, ordering.
- <a id="s035"></a> **[S035] Date and Time on the Internet: Timestamps.** IETF; 2002; RFC 3339. [https://www.rfc-editor.org/rfc/rfc3339.html](https://www.rfc-editor.org/rfc/rfc3339.html) — Tags: time, date, serialization.
- <a id="s037"></a> **[S037] Unicode Normalization Forms.** Unicode Consortium; 2025; UAX #15, Unicode 17.0. [https://www.unicode.org/reports/tr15/](https://www.unicode.org/reports/tr15/) — Tags: unicode, validation, text.
