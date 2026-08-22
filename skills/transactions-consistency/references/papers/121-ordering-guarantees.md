# 121. Ordering Guarantees

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Ordering Guarantees** exists to preserve invariants when multiple operations, requests, or workers interact concurrently and failures can happen at any point. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

Choose transaction boundaries from business invariants and ownership, not controller call stacks. A local database transaction cannot make a remote API, message broker, cache, or second independently owned database atomic. When work crosses boundaries, use durable intent, outbox/inbox, saga, compensation, or reconciliation.

The most important evidence base for this paper includes [S040](#s040) [S044](#s044) [S045](#s045) [S137](#s137). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Atomicity does not mean isolation, and a transaction does not automatically prevent lost updates or write skew.
- The correct boundary is defined by invariants, not by repository or HTTP-handler boundaries.
- Serialization failures and deadlocks are expected outcomes under strong isolation and require whole-transaction retries.
- Network calls inside database transactions extend lock time and create outcomes that cannot be atomically rolled back.
- Distributed locks without fencing cannot prevent a paused or partitioned former owner from writing after lease expiry.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Ordering Guarantees** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- Which anomaly would violate the invariant under the deployed database isolation level?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Ordering Guarantees**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Confirm the deployed database engine/version/isolation and whether framework transaction helpers retry or nest as assumed.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S040](#s040) [S044](#s044) [S045](#s045) [S137](#s137)

1. **Invariant 1:** Atomicity does not mean isolation, and a transaction does not automatically prevent lost updates or write skew.
2. **Invariant 2:** The correct boundary is defined by invariants, not by repository or HTTP-handler boundaries.
3. **Invariant 3:** Serialization failures and deadlocks are expected outcomes under strong isolation and require whole-transaction retries.
4. **Invariant 4:** Network calls inside database transactions extend lock time and create outcomes that cannot be atomically rolled back.
5. **Invariant 5:** Distributed locks without fencing cannot prevent a paused or partitioned former owner from writing after lease expiry.

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Optimistic vs pessimistic concurrency | Optimistic control scales when conflicts are rare; pessimistic locking simplifies hot contention but increases blocking and deadlock risk. | Measure contention and choose per invariant. |
| Read committed vs repeatable read vs serializable | Weaker isolation has higher concurrency but permits more anomalies; serializable simplifies reasoning but can abort transactions. | Use the weakest level that still proves the invariant, with explicit tests. |
| Database transaction vs saga | A local transaction is atomic inside one database; a saga coordinates independently committed steps with compensation. | Keep strong consistency inside one ownership boundary; use sagas when boundaries cannot be collapsed. |
| Lock vs compare-and-swap | Locks serialize access; CAS rejects stale writers without holding locks. | Prefer conditional atomic updates for simple state transitions and versioned aggregates. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

A transaction is `begin → read/write set → validate/lock → commit|rollback`; conflicts and ambiguous connection loss may require retry or outcome lookup. Distributed workflows add `accepted → local_commit → effects_pending → effects_complete|compensation_required → reconciled`. Every transition needs an owner and durable evidence.

```mermaid
stateDiagram-v2
    begun --> reads_writes --> validating_locks --> committed
    validating_locks --> rolled_back
    validating_locks --> conflict --> retry_wait --> begun
    committed --> effects_pending --> reconciled
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Document isolation assumptions, retry conditions, lock order, timeout, maximum duration, idempotency scope, and what clients observe after ambiguous failure. State machines should encode allowed source state in the update predicate. External side effects must occur after durable intent, not inside an open transaction.

A production representation commonly needs the following fields or equivalent evidence:

- transaction/workflow/idempotency identity.
- current state plus expected version/source state for conditional transitions.
- durable intent/outbox and consumer inbox/dedupe records for cross-boundary effects.
- attempt, timeout/deadline, last error, compensation, and reconciliation status.
- fencing/lease generation where external exclusion is used.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### 8.1. Database ordering

- **SHOULD — engineering rule:** State the ordering scope, assign monotonic per-aggregate/version metadata where needed, and make consumers reject, buffer, or reconcile stale/out-of-order items.
- **Production failure mode:** Parallel partitions or retries apply an older event after a newer one and regress state.
- **Existing-codebase evidence:** Deliver permutations, duplicates, gaps, and partition rebalances; verify deterministic final state.

### 8.2. Message ordering

- **SHOULD — engineering rule:** State the ordering scope, assign monotonic per-aggregate/version metadata where needed, and make consumers reject, buffer, or reconcile stale/out-of-order items.
- **Production failure mode:** Parallel partitions or retries apply an older event after a newer one and regress state.
- **Existing-codebase evidence:** Deliver permutations, duplicates, gaps, and partition rebalances; verify deterministic final state.

### 8.3. Event ordering

- **SHOULD — engineering rule:** State the ordering scope, assign monotonic per-aggregate/version metadata where needed, and make consumers reject, buffer, or reconcile stale/out-of-order items.
- **Production failure mode:** Parallel partitions or retries apply an older event after a newer one and regress state.
- **Existing-codebase evidence:** Deliver permutations, duplicates, gaps, and partition rebalances; verify deterministic final state.

### 8.4. Per-key ordering

- **SHOULD — engineering rule:** State the ordering scope, assign monotonic per-aggregate/version metadata where needed, and make consumers reject, buffer, or reconcile stale/out-of-order items.
- **Production failure mode:** Parallel partitions or retries apply an older event after a newer one and regress state.
- **Existing-codebase evidence:** Deliver permutations, duplicates, gaps, and partition rebalances; verify deterministic final state.

### 8.5. Global ordering

- **SHOULD — engineering rule:** State the ordering scope, assign monotonic per-aggregate/version metadata where needed, and make consumers reject, buffer, or reconcile stale/out-of-order items.
- **Production failure mode:** Parallel partitions or retries apply an older event after a newer one and regress state.
- **Existing-codebase evidence:** Deliver permutations, duplicates, gaps, and partition rebalances; verify deterministic final state.

### 8.6. Sequence numbers

- **SHOULD — engineering rule:** State the ordering scope, assign monotonic per-aggregate/version metadata where needed, and make consumers reject, buffer, or reconcile stale/out-of-order items.
- **Production failure mode:** Parallel partitions or retries apply an older event after a newer one and regress state.
- **Existing-codebase evidence:** Deliver permutations, duplicates, gaps, and partition rebalances; verify deterministic final state.

### 8.7. Out-of-order handling

- **SHOULD — engineering rule:** State the ordering scope, assign monotonic per-aggregate/version metadata where needed, and make consumers reject, buffer, or reconcile stale/out-of-order items.
- **Production failure mode:** Parallel partitions or retries apply an older event after a newer one and regress state.
- **Existing-codebase evidence:** Deliver permutations, duplicates, gaps, and partition rebalances; verify deterministic final state.

### 8.8. Reordering buffers

- **SHOULD — engineering rule:** State the ordering scope, assign monotonic per-aggregate/version metadata where needed, and make consumers reject, buffer, or reconcile stale/out-of-order items.
- **Production failure mode:** Parallel partitions or retries apply an older event after a newer one and regress state.
- **Existing-codebase evidence:** Deliver permutations, duplicates, gaps, and partition rebalances; verify deterministic final state.

### 8.9. Ordering vs scalability

- **SHOULD — engineering rule:** State the ordering scope, assign monotonic per-aggregate/version metadata where needed, and make consumers reject, buffer, or reconcile stale/out-of-order items.
- **Production failure mode:** Parallel partitions or retries apply an older event after a newer one and regress state.
- **Existing-codebase evidence:** Deliver permutations, duplicates, gaps, and partition rebalances; verify deterministic final state.

## 9. Concurrency, transactions, idempotency, and consistency

Isolation levels prevent different anomaly sets; names alone are not portable guarantees. Protect invariants with unique/check/foreign-key constraints, serializable execution, explicit locks, or compare-and-swap as appropriate. Distributed locks require leases and fencing tokens when stale holders could still write.

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

Deadlocks, serialization failures, lock timeouts, client disconnects after commit, duplicate messages, and compensation failure are expected. Retry the entire transaction closure with a fresh transaction only when side effects are safe. Keep transactions short and avoid user/network waits while locks are held.

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

Measure conflicts, deadlocks, retries, lock wait/hold duration, transaction age, abort reasons, outbox lag, saga age, compensation failures, and reconciliation backlog. Include transaction/workflow IDs in logs and traces without exposing sensitive payloads.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

Schema and workflow changes must preserve invariants across mixed versions. Add states and columns before emitting them; keep old workers able to ignore or safely reject new events. Avoid rollback plans that reintroduce writers incapable of understanding already-committed states.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Ordering Guarantees path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Database ordering`, `Event ordering`, `Global ordering`. |
| Constraints / atomicity | State the invariant, isolation/lock mechanism, commit point, retry scope, and cross-system consistency mechanism. A local transaction never makes a remote side effect atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Ordering Guarantees; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Ordering Guarantees** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Database ordering**: State the ordering scope, assign monotonic per-aggregate/version metadata where needed, and make consumers reject, buffer, or reconcile stale/out-of-order items.

### SHOULD

- **SHOULD** — Atomicity does not mean isolation, and a transaction does not automatically prevent lost updates or write skew.
- **SHOULD** — The correct boundary is defined by invariants, not by repository or HTTP-handler boundaries.
- **SHOULD** — Serialization failures and deadlocks are expected outcomes under strong isolation and require whole-transaction retries.
- **SHOULD** — Network calls inside database transactions extend lock time and create outcomes that cannot be atomically rolled back.
- **SHOULD** — Distributed locks without fencing cannot prevent a paused or partitioned former owner from writing after lease expiry.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Adopt the **Optimistic vs pessimistic concurrency** option that fits the workload and ownership boundary; Measure contention and choose per invariant.
- **MAY** — Adopt the **Read committed vs repeatable read vs serializable** option that fits the workload and ownership boundary; Use the weakest level that still proves the invariant, with explicit tests.
- **MAY** — Adopt the **Database transaction vs saga** option that fits the workload and ownership boundary; Keep strong consistency inside one ownership boundary; use sagas when boundaries cannot be collapsed.

### AVOID

- **AVOID** — Lost updates from read-modify-write.
- **AVOID** — Write skew across rows.
- **AVOID** — Deadlocks retried at statement rather than transaction level.
- **AVOID** — Side effect sent before commit then transaction rolls back.
- **AVOID** — Expired lease holder continuing to write.
- **AVOID** — Holding a transaction open across network calls.
- **AVOID** — Retrying only the failed statement instead of the transaction.
- **AVOID** — Assuming timeout means rollback.

### NEVER

- **NEVER** — Never hold database locks while waiting for humans or uncontrolled network services.
- **NEVER** — Never assume a timeout proves that no commit or side effect occurred.
- **NEVER** — Never use a lease-based distributed lock as a correctness boundary without fencing or an equivalent stale-writer defense.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Force lost-update, write-skew, duplicate-create, check-then-act, concurrent transition, deadlock, and serialization-conflict schedules with barriers.
- [ ] Disconnect the client immediately before and after commit; verify outcome lookup/idempotent replay rather than guessing.
- [ ] Crash between database commit, outbox publication, consumer effect, acknowledgment, and compensation; reconcile to one valid outcome.
- [ ] Test lock lease expiry and stale holder writes; fencing must reject stale actors where correctness depends on exclusion.
- [ ] Run the same transaction under the actual database isolation/configuration and verify retry logic re-executes a fresh, side-effect-safe closure.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Using a distributed lock without fencing.
- Calling a saga exactly-once or fully atomic.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- 045. Messaging / Queues — in the `async-messaging` skill.
- 046. Event Systems — in the `async-messaging` skill.
- [035. State Machines](035-state-machines.md)
- 120. Deduplication — in the `async-messaging` skill.
- [103. Distributed Locks](103-distributed-locks.md)
- [098. Distributed Systems Fundamentals](098-distributed-systems-fundamentals.md)
- [036. Idempotency](036-idempotency.md)
- [023. Database Transactions](023-database-transactions.md)
- [102. Distributed Consensus](102-distributed-consensus.md)
- [101. Partitioning / Sharding](101-partitioning-sharding.md)
- [100. Replication](100-replication.md)
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s040"></a> **[S040] PostgreSQL Documentation.** PostgreSQL Global Development Group; 2026; 18 current. [https://www.postgresql.org/docs/18/](https://www.postgresql.org/docs/18/) — Tags: database, sql, transactions, indexes, concurrency, backup.
- <a id="s041"></a> **[S041] MongoDB Manual.** MongoDB; 2026; 8.0. [https://www.mongodb.com/docs/v8.0/](https://www.mongodb.com/docs/v8.0/) — Tags: database, documents, transactions, indexes, sharding.
- <a id="s043"></a> **[S043] Designing Data-Intensive Applications, Second Edition.** Martin Kleppmann and Chris Riccomini / O'Reilly; 2025; 2nd edition. [https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/) — Tags: distributed-systems, databases, consistency, streams.
- <a id="s044"></a> **[S044] A Critique of ANSI SQL Isolation Levels.** Microsoft Research; 1995; SIGMOD 1995. [https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/](https://www.microsoft.com/en-us/research/publication/a-critique-of-ansi-sql-isolation-levels/) — Tags: transactions, isolation, concurrency.
- <a id="s045"></a> **[S045] Serializable Snapshot Isolation in PostgreSQL.** ACM / PostgreSQL authors; 2012; VLDB 2012. [https://drkp.net/papers/ssi-vldb12.pdf](https://drkp.net/papers/ssi-vldb12.pdf) — Tags: transactions, isolation, postgresql.
- <a id="s046"></a> **[S046] Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.** ACM; 2002; SIGACT News. [https://users.ece.cmu.edu/~adrian/731-sp04/readings/GL-cap.pdf](https://users.ece.cmu.edu/~adrian/731-sp04/readings/GL-cap.pdf) — Tags: cap, consistency, availability, partitions.
- <a id="s047"></a> **[S047] In Search of an Understandable Consensus Algorithm (Raft).** USENIX; 2014; USENIX ATC. [https://raft.github.io/raft.pdf](https://raft.github.io/raft.pdf) — Tags: consensus, replication, leader-election.
- <a id="s048"></a> **[S048] Paxos Made Simple.** Leslie Lamport; 2001; ACM SIGACT News. [https://lamport.azurewebsites.net/pubs/paxos-simple.pdf](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf) — Tags: consensus, distributed-systems.
- <a id="s049"></a> **[S049] Dynamo: Amazon's Highly Available Key-value Store.** Amazon; 2007; SOSP 2007. [https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) — Tags: replication, partitioning, eventual-consistency.
- <a id="s050"></a> **[S050] Spanner: Google's Globally-Distributed Database.** Google Research; 2012; OSDI 2012. [https://research.google/pubs/spanner-googles-globally-distributed-database/](https://research.google/pubs/spanner-googles-globally-distributed-database/) — Tags: database, replication, transactions, time.
- <a id="s051"></a> **[S051] The Chubby Lock Service for Loosely-Coupled Distributed Systems.** Google Research; 2006; OSDI 2006. [https://research.google/pubs/the-chubby-lock-service-for-loosely-coupled-distributed-systems/](https://research.google/pubs/the-chubby-lock-service-for-loosely-coupled-distributed-systems/) — Tags: locks, consensus, coordination.
- <a id="s052"></a> **[S052] Jepsen Analyses.** Jepsen; 2026; Living collection. [https://jepsen.io/analyses](https://jepsen.io/analyses) — Tags: consistency, distributed-systems, testing, failures.
- <a id="s137"></a> **[S137] ACM Queue: Idempotence Is Not a Medical Condition.** Pat Helland / ACM; 2012; ACM Queue. [https://queue.acm.org/detail.cfm?id=2187821](https://queue.acm.org/detail.cfm?id=2187821) — Tags: idempotency, distributed-systems, retries.
- <a id="s138"></a> **[S138] Fencing off zombies.** Martin Kleppmann; 2016; Blog / distributed locking notes. [https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) — Tags: distributed-locks, fencing, leases.
- <a id="s139"></a> **[S139] Redis distributed locks with Redis.** Redis; 2026; Current documentation. [https://redis.io/docs/latest/develop/use/patterns/distributed-locks/](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/) — Tags: distributed-locks, redis, leases.
- <a id="s057"></a> **[S057] Apache Kafka Documentation.** Apache Software Foundation; 2026; Current. [https://kafka.apache.org/documentation/](https://kafka.apache.org/documentation/) — Tags: messaging, streams, ordering, transactions.
