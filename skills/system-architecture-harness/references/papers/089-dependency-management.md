# 089. Dependency Management

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Dependency Management** exists to create ownership and dependency boundaries that allow local reasoning, independent change, and controlled failure. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

A boundary is credible only when ownership, dependency direction, data authority, and public contracts are enforced by code and tooling. Organize around coherent invariants and change ownership, not arbitrary technical layers. Shared databases, DTOs, and utility packages can erase boundaries even when repositories are separate.

The most important evidence base for this paper includes [S043](#s043) [S053](#s053) [S112](#s112) [S113](#s113). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- A boundary is real only when dependency direction, data ownership, and public contracts are enforced.
- Shared libraries and shared databases can couple services more tightly than synchronous calls.
- Extraction readiness is not a reason to pay distributed-systems costs before a boundary needs independent deployment.
- Composition roots should make infrastructure choices visible and testable.
- Abstractions should encode stable policy or variability, not conceal every framework primitive.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Dependency Management** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- Which invariants, data, and deployment ownership justify this boundary rather than a simpler module?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Dependency Management**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Use dependency and ownership graphs from code/runtime, not only architecture documents.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S043](#s043) [S053](#s053) [S112](#s112) [S113](#s113)

1. **Invariant 1:** A boundary is real only when dependency direction, data ownership, and public contracts are enforced.
2. **Invariant 2:** Shared libraries and shared databases can couple services more tightly than synchronous calls.
3. **Invariant 3:** Extraction readiness is not a reason to pay distributed-systems costs before a boundary needs independent deployment.
4. **Invariant 4:** Composition roots should make infrastructure choices visible and testable.
5. **Invariant 5:** Abstractions should encode stable policy or variability, not conceal every framework primitive.

Additional topic-specific invariants:

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Modular monolith vs microservices | A modular monolith minimizes operations and distributed failure; microservices enable independent ownership/scaling at substantial coordination cost. | Start with enforced modules unless independent deployment is a demonstrated requirement. |
| Shared database vs database per service | Shared data simplifies joins and transactions but weakens ownership; separate data preserves autonomy but requires events and reconciliation. | Align data ownership with transactional invariants. |
| Direct calls vs domain events | Calls provide immediate outcomes; events decouple time and consumers but introduce eventual consistency. | Use calls for required synchronous decisions and events for facts after commit. |
| Framework abstraction vs direct use | Wrappers can stabilize interfaces but often hide behavior and lag features. | Wrap only where the application owns a durable policy. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

Architecture evolves through `current map → pressure/evidence → boundary decision → compatibility plan → incremental change → verification → cleanup`. Extraction or consolidation is a migration, not a rewrite event. Preserve a working system through each intermediate state.

```mermaid
stateDiagram-v2
    current_map --> pressure_evidence --> boundary_decision --> compatibility_plan --> incremental_change --> verified --> cleanup
    incremental_change --> rollback_or_forward_fix
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Modules and services expose small, domain-oriented interfaces and events. Internal models remain private; callers should not depend on storage layout. Composition roots select adapters and transactions. Dependency rules, API compatibility, and data ownership should be machine-checkable where possible.

A production representation commonly needs the following fields or equivalent evidence:

- component/module owner and authoritative data.
- public interfaces/events and compatibility version.
- allowed dependency directions and runtime dependencies.
- transaction/consistency boundary and failure policy.
- deployment, SLO, security, backup, and operational ownership metadata.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **Direct dependencies**
- **Transitive dependencies**
- **Version pinning**
- **Lock files**
- **Updates**
- **Vulnerabilities**
- **Abandoned libraries**
- **License concerns**
- **Supply-chain risk**
- **Dependency replacement**
- **Minimal dependency strategy**

## 9. Concurrency, transactions, idempotency, and consistency

Keep invariants within one owner and one transaction whenever feasible. Crossing a boundary introduces latency, partial failure, versioning, idempotency, and reconciliation. Do not split a transactionally coupled domain merely to achieve aesthetic service count.

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

Distributed monoliths combine network failure with lockstep deployment; giant monoliths hide ownership and blast radius. Circular dependencies, shared mutable libraries, chatty calls, and generic abstractions are warning signs. Prefer explicit duplication over coupling when concepts only look similar.

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

Track dependency graphs, change coupling, deployment frequency/failure, service-level objectives, ownership, incident blast radius, and unsupported contracts. Architecture documentation must match runtime topology and data flows, not only desired diagrams.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

Use strangler, adapters, events, and expand-contract to move boundaries gradually. New services must prove independent deployment and operations. Rollback must account for data/events already produced by the new owner; dual ownership without authority rules creates corruption.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Dependency Management path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Direct dependencies`, `Version pinning`, `Vulnerabilities`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Dependency Management; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Dependency Management** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.

### SHOULD

- **SHOULD** — A boundary is real only when dependency direction, data ownership, and public contracts are enforced.
- **SHOULD** — Shared libraries and shared databases can couple services more tightly than synchronous calls.
- **SHOULD** — Extraction readiness is not a reason to pay distributed-systems costs before a boundary needs independent deployment.
- **SHOULD** — Composition roots should make infrastructure choices visible and testable.
- **SHOULD** — Abstractions should encode stable policy or variability, not conceal every framework primitive.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Adopt the **Modular monolith vs microservices** option that fits the workload and ownership boundary; Start with enforced modules unless independent deployment is a demonstrated requirement.
- **MAY** — Adopt the **Shared database vs database per service** option that fits the workload and ownership boundary; Align data ownership with transactional invariants.
- **MAY** — Adopt the **Direct calls vs domain events** option that fits the workload and ownership boundary; Use calls for required synchronous decisions and events for facts after commit.

### AVOID

- **AVOID** — Circular module dependencies.
- **AVOID** — Generic repository hiding query semantics.
- **AVOID** — Shared DTO becoming de facto cross-service database schema.
- **AVOID** — Distributed monolith with lockstep deployments.
- **AVOID** — Business transaction spread across controller hooks.
- **AVOID** — Creating interfaces for every class without a variability boundary.
- **AVOID** — Splitting services around CRUD entities instead of invariants.
- **AVOID** — Sharing database tables across claimed owners.

### NEVER

- **NEVER** — Never let two components believe they are authoritative for the same mutable fact without a conflict protocol.
- **NEVER** — Never split an invariant across services merely for organizational aesthetics.
- **NEVER** — Never make internal storage models a de facto public contract.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Enforce dependency direction and public/internal interfaces with static checks and build boundaries.
- [ ] Run architecture tests for cross-module database access, shared DTO leakage, circular dependencies, and forbidden imports.
- [ ] Exercise failure, latency, and version skew across every proposed remote boundary before extracting it.
- [ ] Test mixed ownership during strangler migration, including duplicate events, rollback, and source-of-truth conflicts.
- [ ] Validate operational ownership: deploy, observe, scale, secure, back up, and restore each independently owned component.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Creating a generic repository that hides important queries.
- Performing a rewrite instead of an incremental compatibility migration.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [086. Dependency Boundaries](086-dependency-boundaries.md)
- [088. Abstraction Design](088-abstraction-design.md)
- 107. CI/CD — in the `runtime-delivery` skill.
- 145. Plugin / Extension Architecture — in the `ai-agent-system-architecture` skill.
- 063. Secrets Management — in the `security-privacy` skill.
- [087. Code-Level Architecture](087-code-level-architecture.md)
- [084. Modular Monolith Architecture](084-modular-monolith-architecture.md)
- [085. Microservice Architecture](085-microservice-architecture.md)
- 023. Database Transactions — in the `transactions-consistency` skill.
- 051. External Integrations — in the `resilience-flow-control` skill.
- 001. Project & Runtime Foundations — in the `runtime-delivery` skill.
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s043"></a> **[S043] Designing Data-Intensive Applications, Second Edition.** Martin Kleppmann and Chris Riccomini / O'Reilly; 2025; 2nd edition. [https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/) — Tags: distributed-systems, databases, consistency, streams.
- <a id="s053"></a> **[S053] Site Reliability Engineering.** Google; 2016; Online book. [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/) — Tags: reliability, operations, monitoring, capacity.
- <a id="s054"></a> **[S054] The Site Reliability Workbook.** Google; 2018; Online book. [https://sre.google/workbook/table-of-contents/](https://sre.google/workbook/table-of-contents/) — Tags: reliability, operations, slo, testing.
- <a id="s070"></a> **[S070] Kubernetes Documentation.** Cloud Native Computing Foundation; 2026; Current. [https://kubernetes.io/docs/](https://kubernetes.io/docs/) — Tags: deployment, containers, health, shutdown, autoscaling.
- <a id="s100"></a> **[S100] Zero Trust Architecture.** NIST; 2020; SP 800-207. [https://csrc.nist.gov/pubs/sp/800/207/final](https://csrc.nist.gov/pubs/sp/800/207/final) — Tags: zero-trust, service-auth, authorization.
- <a id="s112"></a> **[S112] Open Policy Agent Documentation.** Cloud Native Computing Foundation; 2026; Current. [https://www.openpolicyagent.org/docs/latest/](https://www.openpolicyagent.org/docs/latest/) — Tags: authorization, policy, service-auth.
- <a id="s113"></a> **[S113] Cedar Policy Language Reference.** Cedar Policy; 2026; Current. [https://docs.cedarpolicy.com/](https://docs.cedarpolicy.com/) — Tags: authorization, policy, abac, rebac.
- <a id="s122"></a> **[S122] The Twelve-Factor App.** Heroku; 2017; Current. [https://12factor.net/](https://12factor.net/) — Tags: runtime, configuration, deployment, processes.
- <a id="s130"></a> **[S130] PostgreSQL Row Security Policies.** PostgreSQL Global Development Group; 2026; 18. [https://www.postgresql.org/docs/18/ddl-rowsecurity.html](https://www.postgresql.org/docs/18/ddl-rowsecurity.html) — Tags: multi-tenancy, authorization, database.
- <a id="s131"></a> **[S131] AWS Well-Architected SaaS Lens.** AWS; 2026; Current. [https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/saas-lens.html](https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/saas-lens.html) — Tags: multi-tenancy, saas, operations.
- <a id="s132"></a> **[S132] Architecture approaches for storage and data in multitenant solutions.** Microsoft Azure; 2026; Current. [https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/storage-data](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/storage-data) — Tags: multi-tenancy, database, isolation.
