# 008. Authorization

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Authorization** exists to decide whether a verified principal may perform a specific action on a specific resource in a specific context. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

The resource-owning service or module owns the final authorization decision. Gateways may authenticate and apply coarse policy, but they cannot replace object-, field-, row-, state-, or tenant-aware checks. Model a decision over principal, action, resource, and context; preserve the policy version and reason for high-impact operations.

The most important evidence base for this paper includes [S019](#s019) [S020](#s020) [S112](#s112) [S113](#s113). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Authentication identifies a principal; authorization must still be evaluated for every protected action and resource.
- Endpoint-level roles are insufficient when ownership, tenant, relationship, field, row, or state affects access.
- Policy inputs and cached decisions have freshness and provenance requirements.
- Default deny must include unknown actions, unknown resource types, missing attributes, policy errors, and timeout behavior.
- Administrative impersonation is delegated authority with explicit scope, expiry, attribution, and audit—not a hidden identity swap.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Authorization** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- Can the final data query or mutation enforce tenant, ownership, state, and policy predicates together?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Authorization**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Trace authorization for list/search/export/bulk/background/admin paths, not only controller middleware.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S019](#s019) [S020](#s020) [S112](#s112) [S113](#s113)

1. **Invariant 1:** Authentication identifies a principal; authorization must still be evaluated for every protected action and resource.
2. **Invariant 2:** Endpoint-level roles are insufficient when ownership, tenant, relationship, field, row, or state affects access.
3. **Invariant 3:** Policy inputs and cached decisions have freshness and provenance requirements.
4. **Invariant 4:** Default deny must include unknown actions, unknown resource types, missing attributes, policy errors, and timeout behavior.
5. **Invariant 5:** Administrative impersonation is delegated authority with explicit scope, expiry, attribution, and audit—not a hidden identity swap.

Additional topic-specific invariants:

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| RBAC vs ABAC/ReBAC | RBAC is explainable and operationally simple; attribute/relationship policies express context but add data freshness and policy complexity. | Use the simplest model that represents required decisions, often combining coarse roles with resource relationships. |
| RBAC vs ABAC vs ReBAC | RBAC is explainable but role-heavy; ABAC handles context but can become opaque; ReBAC models relationships but needs graph consistency and scalable evaluation. | Combine models deliberately and keep a single decision contract. |
| Embedded checks vs centralized policy decision point | Embedded checks are fast and local but drift; centralized policy improves consistency but adds latency and availability dependencies. | Centralize policy semantics while allowing carefully versioned local enforcement where necessary. |
| Pre-filtering vs post-filtering | Post-filtering risks data leakage and pagination/count errors; pre-filtering can be hard for complex policies. | Push authorization into the query or data access boundary whenever possible. |
| Fail-open vs fail-closed | Fail-open preserves availability but leaks privilege; fail-closed can block critical operations. | Fail closed for access decisions; separately design emergency access with stronger audit. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

Policies, roles, grants, delegations, and impersonation sessions have creation, activation, modification, expiry, revocation, and deletion states. Authorization evaluation itself is `resolve_principal → load_resource/context → evaluate → enforce → audit`. Denial must occur before sensitive data is fetched or serialized whenever possible.

```mermaid
stateDiagram-v2
    inputs_resolved --> policy_evaluated --> allowed
    policy_evaluated --> denied
    allowed --> operation_enforced --> audited
    denied --> audited
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Define stable action names and resource types rather than coupling policy to route strings. State whether absence means deny, how inheritance works, which attributes are authoritative, and how temporary/delegated access expires. Bulk and list APIs need per-item and query-level enforcement; filtering after retrieval is not a safe substitute.

A production representation commonly needs the following fields or equivalent evidence:

- principal, action/resource namespace, scope/tenant, effect, conditions, and policy version.
- role/grant/delegation lifecycle with issuer, expiry, revocation, and provenance.
- resource ownership/relationship data at the authoritative store.
- security-version or invalidation token for bounded decision caching.
- real actor and effective actor for impersonation/delegation.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **Temporary access**
- **Delegated access**
- **Service-to-service authorization**

### 8.1. Permissions

- **MUST — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.2. Roles

- **SHOULD — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.3. RBAC

- **SHOULD — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.4. ABAC

- **SHOULD — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.5. ReBAC

- **SHOULD — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.6. ACLs

- **SHOULD — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.7. Policy-based authorization

- **MUST — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.8. Ownership checks

- **MUST — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.9. Resource-level authorization

- **MUST — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.10. Field-level authorization

- **MUST — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.11. Row-level authorization

- **MUST — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.12. Hierarchical permissions

- **MUST — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.13. Permission inheritance

- **MUST — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.14. Role inheritance

- **SHOULD — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.15. Custom roles

- **MAY — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.16. System roles

- **SHOULD — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.17. Scoped roles

- **SHOULD — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 8.20. Impersonation

- **SHOULD — engineering rule:** Represent impersonation as a scoped, time-bounded delegation retaining both real actor and effective subject. Require elevated approval for sensitive actions and emit immutable audit events.
- **Production failure mode:** Logs attribute actions to the impersonated user, support staff silently gain unrestricted power, or tokens remain usable after impersonation ends.
- **Existing-codebase evidence:** Verify dual identity appears in authorization context, audit records, notifications, and downstream service calls.

### 8.22. Default-deny

- **SHOULD — engineering rule:** Reject unknown resources, actions, attributes, policy versions, evaluation errors, and timeouts unless a separately documented emergency mechanism applies.
- **Production failure mode:** A newly added endpoint or malformed policy input becomes implicitly allowed.
- **Existing-codebase evidence:** Add tests for absent policy, unknown enum values, policy engine outage, stale cache, and new routes without annotations.

### 8.23. Permission cache invalidation

- **MUST — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

## 9. Concurrency, transactions, idempotency, and consistency

Role changes and revocations race with in-flight requests and cached decisions. Define the maximum acceptable staleness, invalidate by policy/security version, and use transactionally consistent ownership checks for state-changing operations. Prevent time-of-check/time-of-use gaps by enforcing predicates in the same database statement or transaction that mutates the resource.

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

Policy service, directory, or cache failure needs an explicit fail-open/fail-closed decision per action. Security-sensitive operations normally fail closed; low-risk reads may use bounded stale policy only when documented. Missing resource context, unknown action, unknown role, or malformed policy should default to denial and emit diagnosable telemetry.

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

Audit policy changes, role assignment, permission denial, administrative elevation, delegated access, and impersonation with real and effective actor. Monitor denial-rate changes, policy evaluation latency/errors, stale-cache age, orphan grants, wildcard use, and high-privilege membership. Avoid user-controlled or PII-heavy metric labels.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

Authorization changes are compatibility changes: renaming actions, splitting resources, or changing inheritance can silently grant or deny access. Introduce new policy inputs with safe defaults, shadow-evaluate before enforcement, compare decisions, and retain rollback capability. Migrations must include caches, tokens, support tooling, and background workers.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Authorization path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Model `(principal, action, resource, context)` and enforce default-deny in the owner. Preserve real/effective actor for delegation and impersonation. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Permissions`, `Policy-based authorization`, `Hierarchical permissions`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Authorization; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Authorization** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Permissions**: Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.

### SHOULD

- **SHOULD** — Authentication identifies a principal; authorization must still be evaluated for every protected action and resource.
- **SHOULD** — Endpoint-level roles are insufficient when ownership, tenant, relationship, field, row, or state affects access.
- **SHOULD** — Policy inputs and cached decisions have freshness and provenance requirements.
- **SHOULD** — Default deny must include unknown actions, unknown resource types, missing attributes, policy errors, and timeout behavior.
- **SHOULD** — Administrative impersonation is delegated authority with explicit scope, expiry, attribution, and audit—not a hidden identity swap.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Choose **RBAC vs ABAC/ReBAC** according to the stated trade-off: Use the simplest model that represents required decisions, often combining coarse roles with resource relationships.
- **MAY** — Adopt the **RBAC vs ABAC vs ReBAC** option that fits the workload and ownership boundary; Combine models deliberately and keep a single decision contract.
- **MAY** — Adopt the **Embedded checks vs centralized policy decision point** option that fits the workload and ownership boundary; Centralize policy semantics while allowing carefully versioned local enforcement where necessary.
- **MAY** — Adopt the **Pre-filtering vs post-filtering** option that fits the workload and ownership boundary; Push authorization into the query or data access boundary whenever possible.

### AVOID

- **AVOID** — IDOR/BOLA through unscoped resource lookup.
- **AVOID** — Stale permission caches after role removal.
- **AVOID** — Field-level data leakage in serializers.
- **AVOID** — Confused-deputy service calls.
- **AVOID** — Tenant admin privileges escaping tenant scope.
- **AVOID** — Checking route role but not object/field/tenant ownership.
- **AVOID** — Fetching and serializing before authorization.
- **AVOID** — Treating missing policy context as allow.

### NEVER

- **NEVER** — Never treat authentication as authorization.
- **NEVER** — Never trust a client-supplied tenant, role, ownership, or policy decision without authoritative verification.
- **NEVER** — Never default to allow when action/resource/policy context is missing or unknown.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Build a principal/action/resource/context decision matrix including anonymous, suspended, stale-role, cross-tenant, owner, delegated, impersonated, and administrator cases.
- [ ] Swap every externally supplied resource and tenant identifier to another authorized principal's object; assert no content, existence, timing, or mutation leak.
- [ ] Race grant/revoke or ownership transfer with reads and writes; verify the documented staleness bound and final predicate enforcement.
- [ ] Test list, search, export, bulk, background-job, cache, and field-serialization paths—not only single-resource endpoints.
- [ ] Inject policy/cache/directory failure and prove fail-open/fail-closed behavior per action.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Caching decisions without revocation/version semantics.
- Losing the real actor during impersonation.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [010. Multi-Tenancy](010-multi-tenancy.md)
- [112. Internal Admin Operations](112-internal-admin-operations.md)
- 060. Audit Logging — in the `production-operations` skill.
- 061. Security Fundamentals — in the `security-privacy` skill.
- 011. Request Lifecycle — in the `api-contracts` skill.
- [009. Users & Account Lifecycle](009-users-and-account-lifecycle.md)
- [003. Identity](003-identity.md)
- [113. Machine-to-Machine Authentication](113-machine-to-machine-authentication.md)
- [004. Authentication](004-authentication.md)
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.
- 066. Privacy & Sensitive Data — in the `security-privacy` skill.
- 062. Web/API Security — in the `security-privacy` skill.

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s019"></a> **[S019] Guide to Attribute Based Access Control Definition and Considerations.** NIST; 2014; SP 800-162. [https://csrc.nist.gov/pubs/sp/800/162/upd2/final](https://csrc.nist.gov/pubs/sp/800/162/upd2/final) — Tags: authorization, abac, policy.
- <a id="s020"></a> **[S020] Zanzibar: Google's Consistent, Global Authorization System.** Google Research; 2019; USENIX ATC 2019. [https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/](https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/) — Tags: authorization, rebac, distributed-systems.
- <a id="s021"></a> **[S021] Application Security Verification Standard.** OWASP; 2025; ASVS 5.0.0. [https://owasp.org/www-project-application-security-verification-standard/](https://owasp.org/www-project-application-security-verification-standard/) — Tags: security, authentication, authorization, validation, logging.
- <a id="s023"></a> **[S023] OWASP API Security Top 10.** OWASP; 2023; 2023. [https://owasp.org/API-Security/editions/2023/en/0x11-t10/](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) — Tags: api, security, authorization, abuse.
- <a id="s100"></a> **[S100] Zero Trust Architecture.** NIST; 2020; SP 800-207. [https://csrc.nist.gov/pubs/sp/800/207/final](https://csrc.nist.gov/pubs/sp/800/207/final) — Tags: zero-trust, service-auth, authorization.
- <a id="s112"></a> **[S112] Open Policy Agent Documentation.** Cloud Native Computing Foundation; 2026; Current. [https://www.openpolicyagent.org/docs/latest/](https://www.openpolicyagent.org/docs/latest/) — Tags: authorization, policy, service-auth.
- <a id="s113"></a> **[S113] Cedar Policy Language Reference.** Cedar Policy; 2026; Current. [https://docs.cedarpolicy.com/](https://docs.cedarpolicy.com/) — Tags: authorization, policy, abac, rebac.
- <a id="s130"></a> **[S130] PostgreSQL Row Security Policies.** PostgreSQL Global Development Group; 2026; 18. [https://www.postgresql.org/docs/18/ddl-rowsecurity.html](https://www.postgresql.org/docs/18/ddl-rowsecurity.html) — Tags: multi-tenancy, authorization, database.
