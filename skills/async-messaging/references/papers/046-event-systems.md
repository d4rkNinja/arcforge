# 046. Event Systems

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Event Systems** exists to execute work independently of the initiating request while preserving delivery, ordering, ownership, and recovery semantics. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

A durable queue or stream transports work; it does not own domain truth. Producers own atomic intent, consumers own idempotent effects, and the domain store records authoritative state. Define message schema, identity, ordering key, delivery policy, retention, security context, and redrive ownership.

The most important evidence base for this paper includes [S057](#s057) [S058](#s058) [S059](#s059) [S140](#s140). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- At-least-once delivery means duplicate execution is normal, not exceptional.
- Acknowledgment timing defines whether work can be lost or duplicated after worker failure.
- A queue transports intent; it does not automatically provide transactionality with the database that produced the message.
- Ordering is usually scoped to a partition/key and conflicts with parallelism.
- Poison messages require bounded retries, quarantine, diagnosis, and replay tooling.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Event Systems** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- Where is producer intent made durable, where is consumer effect deduplicated, and when is acknowledgement safe?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Event Systems**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Inspect broker retention, acknowledgment mode, visibility timeout/lease, redrive policy, partition key, and consumer concurrency.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S057](#s057) [S058](#s058) [S059](#s059) [S140](#s140)

1. **Invariant 1:** At-least-once delivery means duplicate execution is normal, not exceptional.
2. **Invariant 2:** Acknowledgment timing defines whether work can be lost or duplicated after worker failure.
3. **Invariant 3:** A queue transports intent; it does not automatically provide transactionality with the database that produced the message.
4. **Invariant 4:** Ordering is usually scoped to a partition/key and conflicts with parallelism.
5. **Invariant 5:** Poison messages require bounded retries, quarantine, diagnosis, and replay tooling.

Additional topic-specific invariants:

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Queue vs log/stream | Queues distribute independent work; logs preserve ordered history for multiple consumers and replay. | Use queues for tasks and logs for durable event histories, while recognizing products can overlap. |
| Push vs pull consumers | Push reduces client complexity but can overwhelm endpoints; pull exposes backpressure and batching controls. | Choose based on workload control and network topology. |
| Ack before vs after processing | Ack-before risks loss; ack-after risks duplicates. | Ack after durable side effects and make handlers idempotent. |
| Global vs per-key ordering | Global ordering limits throughput and availability; per-key ordering scales but requires key design. | Request only the narrowest ordering guarantee the domain needs. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

A job/message commonly moves through `created → durably_published → available → leased/delivered → executing → acknowledged`, with branches to `retry_wait`, `dead_letter`, `cancelled`, and `expired`. Lost acknowledgments and lease expiry mean successful work can be redelivered.

```mermaid
stateDiagram-v2
    created --> durably_published --> available --> leased --> executing --> acknowledged
    executing --> retry_wait --> available
    executing --> dead_letter
    leased --> lease_expired --> available
    available --> cancelled
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Payloads should carry stable IDs and references, not mutable secrets or entire domain objects by default. Specify attempt number, creation time, causation/correlation, schema version, tenant, deadline, and dedupe identity. Consumers must validate authorization-relevant context against current authoritative state.

A production representation commonly needs the following fields or equivalent evidence:

- stable job/message/event ID, type, schema version, tenant, and causation/correlation.
- payload reference and integrity metadata rather than unrestricted mutable snapshots.
- created/available/deadline timestamps, priority, ordering/partition key.
- attempt, lease/visibility, acknowledgment, result, and dead-letter state.
- producer outbox and consumer idempotency/inbox evidence.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **Domain events**
- **Integration events**
- **Event schemas**
- **Event metadata**
- **Event IDs**
- **Event versioning**
- **Event deduplication**
- **Event replay**
- **Event storage**
- **Event delivery**
- **Eventual consistency**
- **Event consumers**
- **Handler failures**
- **Event fanout**

### 8.7. Event ordering

- **SHOULD — engineering rule:** State the ordering scope, assign monotonic per-aggregate/version metadata where needed, and make consumers reject, buffer, or reconcile stale/out-of-order items.
- **Production failure mode:** Parallel partitions or retries apply an older event after a newer one and regress state.
- **Existing-codebase evidence:** Deliver permutations, duplicates, gaps, and partition rebalances; verify deterministic final state.

## 9. Concurrency, transactions, idempotency, and consistency

Publishing after a database commit can be lost; publishing before commit can expose uncommitted state. Use transactional outbox/CDC or equivalent durable coupling. Acknowledgment occurs only after the intended durable effect. Ordering is normally per partition/key, not global, and retries can reorder messages.

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

Worker crash, timeout after effect, poison payload, broker partition, duplicate delivery, out-of-order delivery, and retry storm are baseline cases. Bound attempts and age, apply exponential backoff with jitter, isolate poison work, and make manual redrive safe.

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

Track queue age, enqueue-to-start latency, processing latency, attempts, success/failure class, lease expirations, consumer lag, partition skew, dead-letter depth, redrive outcome, and end-to-end correlation. Dashboards should distinguish producer failure, broker delay, consumer saturation, and downstream failure.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

Deploy consumers that understand a new schema before producers emit it. Keep tolerant readers and explicit version handling; never repurpose a field semantically. During rollback, new messages may already exist, so old consumers must ignore, quarantine, or safely process them.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Event Systems path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Domain events`, `Event IDs`, `Event deduplication`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Assume redelivery, duplicate publication, lease expiry, concurrent consumers, and reordering. Deduplicate at the effect boundary and acknowledge only after durable success. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Event Systems; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Event Systems** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Event ordering**: State the ordering scope, assign monotonic per-aggregate/version metadata where needed, and make consumers reject, buffer, or reconcile stale/out-of-order items.

### SHOULD

- **SHOULD** — At-least-once delivery means duplicate execution is normal, not exceptional.
- **SHOULD** — Acknowledgment timing defines whether work can be lost or duplicated after worker failure.
- **SHOULD** — A queue transports intent; it does not automatically provide transactionality with the database that produced the message.
- **SHOULD** — Ordering is usually scoped to a partition/key and conflicts with parallelism.
- **SHOULD** — Poison messages require bounded retries, quarantine, diagnosis, and replay tooling.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Adopt the **Queue vs log/stream** option that fits the workload and ownership boundary; Use queues for tasks and logs for durable event histories, while recognizing products can overlap.
- **MAY** — Adopt the **Push vs pull consumers** option that fits the workload and ownership boundary; Choose based on workload control and network topology.
- **MAY** — Adopt the **Ack before vs after processing** option that fits the workload and ownership boundary; Ack after durable side effects and make handlers idempotent.

### AVOID

- **AVOID** — Acknowledging before commit.
- **AVOID** — Retrying a poison message forever.
- **AVOID** — Assuming exactly-once end-to-end.
- **AVOID** — Losing tenant context in job payload.
- **AVOID** — Consumer lag causing stale decisions.
- **AVOID** — Acknowledging before durable effect.
- **AVOID** — Assuming one delivery or global ordering.
- **AVOID** — Publishing outside the commit boundary without outbox/reconciliation.

### NEVER

- **NEVER** — Never assume a message is delivered exactly once merely because a platform markets an exactly-once feature.
- **NEVER** — Never acknowledge work before the required durable effect is committed.
- **NEVER** — Never retry indefinitely without age/attempt limits and poison isolation.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Crash workers before effect, after effect, before acknowledgment, and during retry scheduling; final durable effect must satisfy the delivery contract.
- [ ] Deliver duplicates, out-of-order messages, old schema versions, poison payloads, expired messages, and partition-skewed bursts.
- [ ] Fail publication before/after domain commit and verify outbox/CDC recovery and inbox dedupe.
- [ ] Test cancellation, lease expiry, redrive, dead-letter retention, and manual replay with current authorization and tenant state.
- [ ] Run producer/consumer mixed versions and rollback while new message versions remain in the broker.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Retrying poison work forever.
- Putting secrets and mutable snapshots in payloads.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [047. Transactional Outbox / Inbox](047-transactional-outbox-inbox.md)
- [045. Messaging / Queues](045-messaging-queues.md)
- 073. Change Data Capture — in the `migration-evolution` skill.
- [043. Background Jobs](043-background-jobs.md)
- 069. Data Versioning — in the `data-storage` skill.
- 121. Ordering Guarantees — in the `transactions-consistency` skill.
- 048. Distributed Transactions — in the `transactions-consistency` skill.
- 070. API / Event Schema Evolution — in the `migration-evolution` skill.
- 137. Observability for Async Systems — in the `production-operations` skill.
- 035. State Machines — in the `transactions-consistency` skill.
- [129. Notification Infrastructure](129-notification-infrastructure.md)
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s032"></a> **[S032] AsyncAPI Specification.** AsyncAPI Initiative; 2026; 3.1.0. [https://www.asyncapi.com/docs/reference/specification/v3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0) — Tags: events, messaging, schema, api.
- <a id="s043"></a> **[S043] Designing Data-Intensive Applications, Second Edition.** Martin Kleppmann and Chris Riccomini / O'Reilly; 2025; 2nd edition. [https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/) — Tags: distributed-systems, databases, consistency, streams.
- <a id="s055"></a> **[S055] Timeouts, Retries, and Backoff with Jitter.** AWS Builders' Library; 2026; Current article. [https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) — Tags: retries, timeouts, jitter, resilience.
- <a id="s057"></a> **[S057] Apache Kafka Documentation.** Apache Software Foundation; 2026; Current. [https://kafka.apache.org/documentation/](https://kafka.apache.org/documentation/) — Tags: messaging, streams, ordering, transactions.
- <a id="s058"></a> **[S058] RabbitMQ Documentation.** Broadcom / RabbitMQ; 2026; Current. [https://www.rabbitmq.com/docs](https://www.rabbitmq.com/docs) — Tags: messaging, queues, acknowledgments, retries.
- <a id="s059"></a> **[S059] Amazon SQS Developer Guide.** AWS; 2026; Current. [https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html) — Tags: queues, messaging, deduplication, visibility-timeout.
- <a id="s060"></a> **[S060] CloudEvents Specification.** Cloud Native Computing Foundation; 2022; 1.0.2. [https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md) — Tags: events, metadata, schema.
- <a id="s061"></a> **[S061] Debezium Documentation.** Red Hat / Debezium; 2026; Current. [https://debezium.io/documentation/](https://debezium.io/documentation/) — Tags: cdc, outbox, events, database.
- <a id="s062"></a> **[S062] Sagas.** ACM; 1987; SIGMOD 1987. [https://dl.acm.org/doi/10.1145/38713.38742](https://dl.acm.org/doi/10.1145/38713.38742) — Tags: sagas, distributed-transactions, compensation.
- <a id="s063"></a> **[S063] The WebSocket Protocol.** IETF; 2011; RFC 6455. [https://www.rfc-editor.org/rfc/rfc6455.html](https://www.rfc-editor.org/rfc/rfc6455.html) — Tags: websocket, realtime, networking.
- <a id="s064"></a> **[S064] Server-sent events.** WHATWG; 2026; HTML Living Standard. [https://html.spec.whatwg.org/multipage/server-sent-events.html](https://html.spec.whatwg.org/multipage/server-sent-events.html) — Tags: sse, realtime, streaming.
- <a id="s065"></a> **[S065] Standard Webhooks Specification.** Standard Webhooks; 2026; Current. [https://www.standardwebhooks.com/](https://www.standardwebhooks.com/) — Tags: webhooks, signing, replay, delivery.
- <a id="s137"></a> **[S137] ACM Queue: Idempotence Is Not a Medical Condition.** Pat Helland / ACM; 2012; ACM Queue. [https://queue.acm.org/detail.cfm?id=2187821](https://queue.acm.org/detail.cfm?id=2187821) — Tags: idempotency, distributed-systems, retries.
- <a id="s140"></a> **[S140] Transactional Outbox Pattern.** Chris Richardson / microservices.io; 2026; Current pattern write-up. [https://microservices.io/patterns/data/transactional-outbox.html](https://microservices.io/patterns/data/transactional-outbox.html) — Tags: outbox, events, transactions.
