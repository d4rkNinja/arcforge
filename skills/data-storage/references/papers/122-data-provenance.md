# 122. Data Provenance

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Data Provenance** exists to encode domain facts and invariants so valid states are easy to represent and invalid states are difficult to persist. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

The model should express domain ownership and invariants, not mirror a UI form or external provider payload. Decide which component is the source of truth, which fields are derived, how references are scoped, and whether history is mutable, versioned, or append-only. Keep tenant and security boundaries visible in keys and access paths.

The most important evidence base for this paper includes [S040](#s040) [S041](#s041) [S043](#s043) [S033](#s033). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Schema design is an executable consistency model, not merely a serialization format.
- Application validation improves feedback; database constraints provide the final race-safe guard for invariants the database owns.
- Denormalization trades read simplicity for write coordination and repair obligations.
- Optionality, deletion semantics, history, and ownership must be explicit because they affect every query and migration.
- Derived fields need a source of truth, recomputation rule, and divergence detection.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Data Provenance** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- Which invalid states must the database reject even when all application validation is bypassed?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Data Provenance**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Run constraint and index introspection against the real production schema, including partial/sparse/tenant conditions.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S040](#s040) [S041](#s041) [S043](#s043) [S033](#s033)

1. **Invariant 1:** Schema design is an executable consistency model, not merely a serialization format.
2. **Invariant 2:** Application validation improves feedback; database constraints provide the final race-safe guard for invariants the database owns.
3. **Invariant 3:** Denormalization trades read simplicity for write coordination and repair obligations.
4. **Invariant 4:** Optionality, deletion semantics, history, and ownership must be explicit because they affect every query and migration.
5. **Invariant 5:** Derived fields need a source of truth, recomputation rule, and divergence detection.

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Normalize vs denormalize | Normalization reduces anomalies; denormalization reduces joins and cross-partition reads but duplicates facts. | Denormalize only with an explicit propagation and reconciliation mechanism. |
| Embed vs reference | Embedding gives locality and atomicity; references support independent lifecycle and large fanout. | Embed data that shares ownership, lifecycle, and bounded size. |
| Database-generated vs application-generated identifiers | Database generation is simple but couples creation to one store; application generation supports offline/distributed creation but requires collision and ordering analysis. | Choose based on creation topology and exposure requirements. |
| Hard constraint vs application-only rule | Application-only checks race under concurrency; hard constraints may be difficult for cross-row or distributed invariants. | Put local invariants in the database and use transactions/repair for wider invariants. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

Records move through explicit creation, active mutation, domain states, archival, soft deletion, restoration, and purge. Derived fields and indexes have separate freshness lifecycles. For immutable facts, corrections append a new record or version rather than rewriting history.

```mermaid
stateDiagram-v2
    proposed --> validated --> persisted --> active
    active --> versioned
    active --> archived
    archived --> restored
    active --> soft_deleted
    soft_deleted --> restored
    soft_deleted --> purged
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Define null versus absent, defaults, numeric and temporal precision, identifier namespace, normalization, uniqueness scope, and reference behavior. Application validation improves errors; database constraints provide the final race-safe guard. Serialization contracts must preserve precision and tolerate schema evolution.

A production representation commonly needs the following fields or equivalent evidence:

- stable identifier, tenant/owner scope, lifecycle state, and optimistic version.
- created/updated/effective timestamps with explicit time semantics.
- source/provenance and authoritative versus derived field markers.
- uniqueness/foreign-key/check invariants represented in the database.
- soft-delete/retention/legal-hold and history/correction metadata where applicable.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **Source of data**
- **Creator**
- **Import source**
- **External provider**
- **Transformation history**
- **Source timestamps**
- **Confidence**

### 8.6. Derived data

- **SHOULD — engineering rule:** Name the canonical source, update path, acceptable staleness, version, rebuild algorithm, and reconciliation signal for every duplicated or derived value.
- **Production failure mode:** Partial writes or event loss cause durable divergence that no component owns.
- **Existing-codebase evidence:** Introduce missed/out-of-order updates and verify periodic comparison and deterministic rebuild.

### 8.9. Auditability

- **MUST — engineering rule:** Record real actor, effective actor, action, resource, tenant, timestamp, request/trace, policy context, outcome, and appropriately minimized change details in tamper-resistant storage.
- **Production failure mode:** Security-sensitive changes cannot be attributed, audit data leaks secrets, or failed attempts vanish.
- **Existing-codebase evidence:** Exercise successful/failed/admin/impersonated/bulk actions and verify atomicity, retention, search, export, and access controls.

## 9. Concurrency, transactions, idempotency, and consistency

Multi-record invariants require transactions, conditional writes, or a reconciliation design. Denormalized copies need a source version and repair path. Concurrent create/update/delete must not rely on read-then-write logic; use unique constraints, versions, and atomic predicates.

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

Partial writes, orphan references, stale derived values, and duplicate natural keys are ordinary production failure modes. Make repair safe and idempotent, record provenance, and distinguish transient incompleteness from corruption. Never delete the only source needed to rebuild a derived representation.

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

Track constraint violations, duplicate attempts, orphan counts, model-version distribution, backfill progress, stale derived data, index size/usage, slow queries, and cleanup backlog. Audit sensitive lifecycle changes and redact protected fields from logs and change streams.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

Use expand-and-contract for field additions, renames, type changes, and stronger nullability. New code must read old rows; old code must survive new rows during rolling deployment. Backfills should be chunked, resumable, idempotent, rate-limited, and verified against invariants before contraction.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Data Provenance path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Source of data`, `Import source`, `Transformation history`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Data Provenance; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Data Provenance** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Derived data**: Name the canonical source, update path, acceptable staleness, version, rebuild algorithm, and reconciliation signal for every duplicated or derived value.

### SHOULD

- **SHOULD** — Schema design is an executable consistency model, not merely a serialization format.
- **SHOULD** — Application validation improves feedback; database constraints provide the final race-safe guard for invariants the database owns.
- **SHOULD** — Denormalization trades read simplicity for write coordination and repair obligations.
- **SHOULD** — Optionality, deletion semantics, history, and ownership must be explicit because they affect every query and migration.
- **SHOULD** — Derived fields need a source of truth, recomputation rule, and divergence detection.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Adopt the **Normalize vs denormalize** option that fits the workload and ownership boundary; Denormalize only with an explicit propagation and reconciliation mechanism.
- **MAY** — Adopt the **Embed vs reference** option that fits the workload and ownership boundary; Embed data that shares ownership, lifecycle, and bounded size.
- **MAY** — Adopt the **Database-generated vs application-generated identifiers** option that fits the workload and ownership boundary; Choose based on creation topology and exposure requirements.

### AVOID

- **AVOID** — Nullable fields used as implicit state.
- **AVOID** — Orphaned records after partial delete.
- **AVOID** — Duplicate rows from check-then-insert.
- **AVOID** — Derived totals drifting from source rows.
- **AVOID** — Schema that makes tenant filtering optional.
- **AVOID** — Relying on application checks instead of database constraints.
- **AVOID** — Using nullable/default fields without semantic meaning.
- **AVOID** — Denormalizing without provenance/version/rebuild path.

### NEVER

- **NEVER** — Never rely on read-then-insert as the final uniqueness control.
- **NEVER** — Never store monetary/precision-sensitive values in binary floating point without an explicit, validated reason.
- **NEVER** — Never remove the only authoritative data needed to rebuild a derived copy.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Attempt every invalid invariant directly at the database, bypassing application validation; constraints must reject race-safe violations.
- [ ] Synchronize duplicate creation, stale update, delete/update, restore/create, and derived-field rebuild operations.
- [ ] Round-trip identifiers, decimals, timestamps, Unicode, null/absent values, and maximum-size records through API and storage.
- [ ] Delete, archive, restore, and purge records with all reference patterns; verify orphan, uniqueness, audit, and privacy behavior.
- [ ] Run query plans and index tests on production-shaped cardinality/skew, including soft-deleted and tenant-scoped data.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Forgetting tenant scope in unique keys and indexes.
- Performing destructive schema changes in one deployment.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [123. Source of Truth](123-source-of-truth.md)
- [069. Data Versioning](069-data-versioning.md)
- [034. Immutable Data](034-immutable-data.md)
- [124. Data Reconciliation](124-data-reconciliation.md)
- [021. Database Modeling](021-database-modeling.md)
- [032. Soft Delete / Hard Delete](032-soft-delete-hard-delete.md)
- [026. Data Integrity](026-data-integrity.md)
- [019. Time & Date Handling](019-time-and-date-handling.md)
- [028. Query Design](028-query-design.md)
- [027. Indexing](027-indexing.md)
- [033. Data Lifecycle](033-data-lifecycle.md)
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s033"></a> **[S033] JSON Schema.** JSON Schema; 2022; Draft 2020-12. [https://json-schema.org/draft/2020-12](https://json-schema.org/draft/2020-12) — Tags: json, validation, schema.
- <a id="s034"></a> **[S034] Universally Unique IDentifiers (UUIDs).** IETF; 2024; RFC 9562. [https://www.rfc-editor.org/rfc/rfc9562.html](https://www.rfc-editor.org/rfc/rfc9562.html) — Tags: identifiers, uuid, ordering.
- <a id="s035"></a> **[S035] Date and Time on the Internet: Timestamps.** IETF; 2002; RFC 3339. [https://www.rfc-editor.org/rfc/rfc3339.html](https://www.rfc-editor.org/rfc/rfc3339.html) — Tags: time, date, serialization.
- <a id="s037"></a> **[S037] Unicode Normalization Forms.** Unicode Consortium; 2025; UAX #15, Unicode 17.0. [https://www.unicode.org/reports/tr15/](https://www.unicode.org/reports/tr15/) — Tags: unicode, validation, text.
- <a id="s038"></a> **[S038] IEEE Standard for Floating-Point Arithmetic.** IEEE; 2019; IEEE 754-2019. [https://standards.ieee.org/standard/754-2019.html](https://standards.ieee.org/standard/754-2019.html) — Tags: numeric, floating-point, precision.
- <a id="s039"></a> **[S039] General Decimal Arithmetic Specification.** Mike Cowlishaw / Speleotrove; 2009; 1.70. [https://speleotrove.com/decimal/decarith.html](https://speleotrove.com/decimal/decarith.html) — Tags: decimal, money, precision, rounding.
- <a id="s040"></a> **[S040] PostgreSQL Documentation.** PostgreSQL Global Development Group; 2026; 18 current. [https://www.postgresql.org/docs/18/](https://www.postgresql.org/docs/18/) — Tags: database, sql, transactions, indexes, concurrency, backup.
- <a id="s041"></a> **[S041] MongoDB Manual.** MongoDB; 2026; 8.0. [https://www.mongodb.com/docs/v8.0/](https://www.mongodb.com/docs/v8.0/) — Tags: database, documents, transactions, indexes, sharding.
- <a id="s043"></a> **[S043] Designing Data-Intensive Applications, Second Edition.** Martin Kleppmann and Chris Riccomini / O'Reilly; 2025; 2nd edition. [https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/) — Tags: distributed-systems, databases, consistency, streams.
- <a id="s044"></a> **[S044] A Critique of ANSI SQL Isolation Levels.** Microsoft Research; 1995; SIGMOD 1995. [https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/](https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/) — Tags: transactions, isolation, concurrency.
- <a id="s082"></a> **[S082] General Data Protection Regulation.** European Union; 2016; Regulation (EU) 2016/679. [https://eur-lex.europa.eu/eli/reg/2016/679/oj](https://eur-lex.europa.eu/eli/reg/2016/679/oj) — Tags: privacy, retention, deletion, consent.
- <a id="s137"></a> **[S137] ACM Queue: Idempotence Is Not a Medical Condition.** Pat Helland / ACM; 2012; ACM Queue. [https://queue.acm.org/detail.cfm?id=2187821](https://queue.acm.org/detail.cfm?id=2187821) — Tags: idempotency, distributed-systems, retries.
