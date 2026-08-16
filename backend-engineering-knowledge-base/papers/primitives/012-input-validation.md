---
paper_number: 12
title: "Input Validation"
layer: primitives
domain_profile: api
corpus_version: 1.0.0
verified_through: 2026-08-17
canonical_source: "original/Pasted text.txt"
subtopic_count: 22
status: production-engineering-reference
---

# 012. Input Validation

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Input Validation** exists to define stable, observable, secure contracts between independently evolving producers and consumers. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

An API contract includes syntax, semantics, authentication, authorization, idempotency, ordering, error behavior, limits, deadlines, and compatibility—not only a schema. The owning service must validate and enforce invariants at the boundary while keeping transport DTOs separate from persistence and domain models.

The most important evidence base for this paper includes [S025](#s025) [S027](#s027) [S028](#s028) [S114](#s114). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- An API contract includes semantics, errors, retries, timeouts, pagination, authorization, idempotency, and compatibility—not only JSON shapes.
- HTTP method and status semantics matter because clients, caches, gateways, and monitoring act on them.
- Unknown fields, enum growth, nullability, ordering, and partial success are compatibility decisions.
- Bulk and asynchronous operations need per-item or job-level state rather than pretending all work is synchronous and atomic.
- Public error detail must help callers recover without exposing internals or sensitive state.

## 2. Scope and terminology map

The canonical topic list requires this paper to cover the following concerns. They are grouped only to expose relationships; no listed subtopic is omitted.

### Contracts and validation

**Required fields**, **Optional fields**, **Null handling**, **Empty strings**, **Whitespace**, **Length limits**, **Numeric ranges**, **Enum validation**, **Date validation**, **Time validation**, **URL validation**, **Email validation**, **Phone validation**, **UUID/ID validation**, **Nested validation**, **Cross-field validation**, **Conditional validation**, **Business invariants**, **Unknown fields**, **Type coercion**, **Unicode handling**, **Malformed payloads**.

### Boundary of the paper

This paper treats **Input Validation** as a production subsystem or reusable reasoning primitive. It covers semantics, ownership, persistence, APIs, security, concurrency, distributed behavior, operations, evolution, and verification. Framework syntax and large implementation listings are intentionally excluded.

## 3. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S025](#s025) [S027](#s027) [S028](#s028) [S114](#s114)

1. **Invariant 1:** An API contract includes semantics, errors, retries, timeouts, pagination, authorization, idempotency, and compatibility—not only JSON shapes.
2. **Invariant 2:** HTTP method and status semantics matter because clients, caches, gateways, and monitoring act on them.
3. **Invariant 3:** Unknown fields, enum growth, nullability, ordering, and partial success are compatibility decisions.
4. **Invariant 4:** Bulk and asynchronous operations need per-item or job-level state rather than pretending all work is synchronous and atomic.
5. **Invariant 5:** Public error detail must help callers recover without exposing internals or sensitive state.

Additional topic-specific invariants:

- **SHOULD — Required fields:** Specify presence, null, empty, whitespace-only, default, and unknown-field semantics separately for create, replace, and partial update.
- **SHOULD — Whitespace:** Define the exact semantics of **Whitespace** within Input Validation: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST — Date validation:** Use a standards-aware parser and validate only constraints the application truly requires. Separate syntactic validity from ownership, reachability, authorization, and business eligibility.
- **MUST — UUID/ID validation:** Use a standards-aware parser and validate only constraints the application truly requires. Separate syntactic validity from ownership, reachability, authorization, and business eligibility.
- **SHOULD — Business invariants:** Validate invariants on the complete command and re-check race-sensitive invariants inside the transaction against authoritative state.
- **SHOULD — Malformed payloads:** Define the exact semantics of **Malformed payloads** within Input Validation: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.

## 4. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Resource-oriented REST vs command/RPC | Resource APIs align with HTTP and caching; command APIs express workflows and invariants more directly. | Use resources for durable nouns and explicit commands for state transitions that do not map cleanly to CRUD. |
| Synchronous vs asynchronous response | Synchronous APIs are simple but tie latency and reliability to downstream work; async APIs require job state and polling/events. | Use async when work exceeds request deadlines, has variable duration, or needs independent retry. |
| PUT vs PATCH | PUT replaces a representation and can be naturally idempotent; PATCH is efficient but needs explicit patch semantics and concurrency control. | Document absent/null/remove behavior and use conditional requests or versions. |
| Version in URL vs compatible evolution | Versioned URLs isolate breaking contracts but multiply surfaces; additive evolution reduces churn but requires discipline. | Prefer compatible evolution and introduce a new major surface for unavoidable semantic breaks. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 5. Ownership, state, and lifecycle

A request typically moves through `admitted → parsed → validated → authenticated → authorized → executed → committed → serialized`, with cancellation and timeout possible at every stage. Response loss after commit is a distinct outcome: the client may observe failure while the server has succeeded, which drives idempotency and reconciliation requirements.

```mermaid
stateDiagram-v2
    admitted --> parsed --> validated --> authenticated --> authorized --> executed --> committed --> serialized
    admitted --> rejected
    validated --> rejected
    authorized --> denied
    executed --> rolled_back
    committed --> response_lost
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 6. Data model and API implications

Specify required/optional/null/absent semantics, unknown-field policy, canonical encodings, error codes, pagination order, filter operators, size/complexity limits, and conditional request behavior. Use machine-readable schemas but supplement them with invariants and state-transition rules that schemas cannot express.

A production representation commonly needs the following fields or equivalent evidence:

- stable public resource identifiers separate from internal storage IDs where needed.
- request/idempotency identity and fingerprint for replay-sensitive operations.
- resource version/ETag or transition version for concurrency.
- canonical timestamps, null/absent semantics, and schema version.
- public error code and correlation metadata without internal sensitive details.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 7. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### 7.1. Required fields

- **SHOULD — engineering rule:** Specify presence, null, empty, whitespace-only, default, and unknown-field semantics separately for create, replace, and partial update.
- **Production failure mode:** Clients cannot clear a field, defaults overwrite explicit values, or silent unknown fields hide typos and compatibility bugs.
- **Existing-codebase evidence:** Build a contract matrix for omitted/null/empty/zero/false/unknown values and verify serialization round trips.

### 7.2. Optional fields

- **SHOULD — engineering rule:** Specify presence, null, empty, whitespace-only, default, and unknown-field semantics separately for create, replace, and partial update.
- **Production failure mode:** Clients cannot clear a field, defaults overwrite explicit values, or silent unknown fields hide typos and compatibility bugs.
- **Existing-codebase evidence:** Build a contract matrix for omitted/null/empty/zero/false/unknown values and verify serialization round trips.

### 7.3. Null handling

- **SHOULD — engineering rule:** Specify presence, null, empty, whitespace-only, default, and unknown-field semantics separately for create, replace, and partial update.
- **Production failure mode:** Clients cannot clear a field, defaults overwrite explicit values, or silent unknown fields hide typos and compatibility bugs.
- **Existing-codebase evidence:** Build a contract matrix for omitted/null/empty/zero/false/unknown values and verify serialization round trips.

### 7.4. Empty strings

- **SHOULD — engineering rule:** Specify presence, null, empty, whitespace-only, default, and unknown-field semantics separately for create, replace, and partial update.
- **Production failure mode:** Clients cannot clear a field, defaults overwrite explicit values, or silent unknown fields hide typos and compatibility bugs.
- **Existing-codebase evidence:** Build a contract matrix for omitted/null/empty/zero/false/unknown values and verify serialization round trips.

### 7.5. Whitespace

- **SHOULD — engineering rule:** Define the exact semantics of **Whitespace** within Input Validation: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for whitespace is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for whitespace, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.6. Length limits

- **SHOULD — engineering rule:** Define the exact semantics of **Length limits** within Input Validation: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for length limits is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for length limits, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.7. Numeric ranges

- **SHOULD — engineering rule:** Define the exact semantics of **Numeric ranges** within Input Validation: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for numeric ranges is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for numeric ranges, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.8. Enum validation

- **MUST — engineering rule:** Define the exact semantics of **Enum validation** within Input Validation: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for enum validation is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for enum validation, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.9. Date validation

- **MUST — engineering rule:** Use a standards-aware parser and validate only constraints the application truly requires. Separate syntactic validity from ownership, reachability, authorization, and business eligibility.
- **Production failure mode:** Overly strict regexes reject valid values while permissive parsing accepts ambiguous or dangerous forms; validation is mistaken for verification.
- **Existing-codebase evidence:** Maintain positive/negative conformance fixtures and test normalization, international forms, boundary lengths, and parser differentials.

### 7.10. Time validation

- **MUST — engineering rule:** Use a standards-aware parser and validate only constraints the application truly requires. Separate syntactic validity from ownership, reachability, authorization, and business eligibility.
- **Production failure mode:** Overly strict regexes reject valid values while permissive parsing accepts ambiguous or dangerous forms; validation is mistaken for verification.
- **Existing-codebase evidence:** Maintain positive/negative conformance fixtures and test normalization, international forms, boundary lengths, and parser differentials.

### 7.11. URL validation

- **MUST — engineering rule:** Use a standards-aware parser and validate only constraints the application truly requires. Separate syntactic validity from ownership, reachability, authorization, and business eligibility.
- **Production failure mode:** Overly strict regexes reject valid values while permissive parsing accepts ambiguous or dangerous forms; validation is mistaken for verification.
- **Existing-codebase evidence:** Maintain positive/negative conformance fixtures and test normalization, international forms, boundary lengths, and parser differentials.

### 7.12. Email validation

- **MUST — engineering rule:** Use a standards-aware parser and validate only constraints the application truly requires. Separate syntactic validity from ownership, reachability, authorization, and business eligibility.
- **Production failure mode:** Overly strict regexes reject valid values while permissive parsing accepts ambiguous or dangerous forms; validation is mistaken for verification.
- **Existing-codebase evidence:** Maintain positive/negative conformance fixtures and test normalization, international forms, boundary lengths, and parser differentials.

### 7.13. Phone validation

- **MUST — engineering rule:** Use a standards-aware parser and validate only constraints the application truly requires. Separate syntactic validity from ownership, reachability, authorization, and business eligibility.
- **Production failure mode:** Overly strict regexes reject valid values while permissive parsing accepts ambiguous or dangerous forms; validation is mistaken for verification.
- **Existing-codebase evidence:** Maintain positive/negative conformance fixtures and test normalization, international forms, boundary lengths, and parser differentials.

### 7.14. UUID/ID validation

- **MUST — engineering rule:** Use a standards-aware parser and validate only constraints the application truly requires. Separate syntactic validity from ownership, reachability, authorization, and business eligibility.
- **Production failure mode:** Overly strict regexes reject valid values while permissive parsing accepts ambiguous or dangerous forms; validation is mistaken for verification.
- **Existing-codebase evidence:** Maintain positive/negative conformance fixtures and test normalization, international forms, boundary lengths, and parser differentials.

### 7.15. Nested validation

- **MUST — engineering rule:** Define the exact semantics of **Nested validation** within Input Validation: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for nested validation is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for nested validation, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.16. Cross-field validation

- **MUST — engineering rule:** Validate invariants on the complete command and re-check race-sensitive invariants inside the transaction against authoritative state.
- **Production failure mode:** Each field is individually valid while the combination is impossible, stale, or forbidden by current resource state.
- **Existing-codebase evidence:** Create a decision table of field combinations and run concurrent tests where referenced state changes between validation and commit.

### 7.17. Conditional validation

- **MUST — engineering rule:** Validate invariants on the complete command and re-check race-sensitive invariants inside the transaction against authoritative state.
- **Production failure mode:** Each field is individually valid while the combination is impossible, stale, or forbidden by current resource state.
- **Existing-codebase evidence:** Create a decision table of field combinations and run concurrent tests where referenced state changes between validation and commit.

### 7.18. Business invariants

- **SHOULD — engineering rule:** Validate invariants on the complete command and re-check race-sensitive invariants inside the transaction against authoritative state.
- **Production failure mode:** Each field is individually valid while the combination is impossible, stale, or forbidden by current resource state.
- **Existing-codebase evidence:** Create a decision table of field combinations and run concurrent tests where referenced state changes between validation and commit.

### 7.19. Unknown fields

- **SHOULD — engineering rule:** Specify presence, null, empty, whitespace-only, default, and unknown-field semantics separately for create, replace, and partial update.
- **Production failure mode:** Clients cannot clear a field, defaults overwrite explicit values, or silent unknown fields hide typos and compatibility bugs.
- **Existing-codebase evidence:** Build a contract matrix for omitted/null/empty/zero/false/unknown values and verify serialization round trips.

### 7.20. Type coercion

- **SHOULD — engineering rule:** Define the exact semantics of **Type coercion** within Input Validation: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for type coercion is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for type coercion, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.21. Unicode handling

- **SHOULD — engineering rule:** Choose normalization and comparison rules per field; validate by Unicode scalar/code point/grapheme as appropriate, and preserve original text when normalization would change meaning.
- **Production failure mode:** Visually equivalent or confusable strings bypass uniqueness, length limits, moderation, or authorization identifiers.
- **Existing-codebase evidence:** Test composed/decomposed forms, combining marks, confusables, bidirectional controls, invalid encodings, and grapheme-length boundaries.

### 7.22. Malformed payloads

- **SHOULD — engineering rule:** Define the exact semantics of **Malformed payloads** within Input Validation: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for malformed payloads is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for malformed payloads, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

## 8. Concurrency, transactions, idempotency, and consistency

State-changing endpoints need a declared atomicity boundary and concurrency policy. Use unique constraints, conditional writes, versions, and idempotency keys rather than preflight existence checks. Pagination and bulk operations must define behavior under concurrent writes, partial success, and retries.

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

Separate invalid input, authentication/authorization denial, conflict, rate limit, dependency failure, timeout, and unknown internal error. Do not leak internals or return a successful status for failed work. Honor cancellation where safe, but once a commit boundary is crossed return or replay the committed result rather than attempting compensating guesses.

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

Log request/trace IDs, route template, principal/tenant identifiers in controlled form, outcome class, latency, bytes, retry/idempotency status, and dependency spans. Monitor per-endpoint rate, error class, p50/p95/p99 latency, saturation, payload rejection, pagination depth, and compatibility/deprecation usage.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 13. Compatibility, schema evolution, migration, deployment, and rollback

Prefer additive changes, tolerant readers, optional fields, and explicit deprecation windows. Mixed-version clients make enum additions, required fields, default changes, and semantic reinterpretation dangerous. Contract tests should exercise old clients against new servers and new clients against old or staged servers where relevant.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Input Validation path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Required fields`, `Length limits`, `URL validation`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Input Validation; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 15. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Input Validation** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Required fields**: Specify presence, null, empty, whitespace-only, default, and unknown-field semantics separately for create, replace, and partial update.
- **MUST** — For **Whitespace**: Define the exact semantics of **Whitespace** within Input Validation: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **Date validation**: Use a standards-aware parser and validate only constraints the application truly requires. Separate syntactic validity from ownership, reachability, authorization, and business eligibility.
- **MUST** — For **UUID/ID validation**: Use a standards-aware parser and validate only constraints the application truly requires. Separate syntactic validity from ownership, reachability, authorization, and business eligibility.

### SHOULD

- **SHOULD** — An API contract includes semantics, errors, retries, timeouts, pagination, authorization, idempotency, and compatibility—not only JSON shapes.
- **SHOULD** — HTTP method and status semantics matter because clients, caches, gateways, and monitoring act on them.
- **SHOULD** — Unknown fields, enum growth, nullability, ordering, and partial success are compatibility decisions.
- **SHOULD** — Bulk and asynchronous operations need per-item or job-level state rather than pretending all work is synchronous and atomic.
- **SHOULD** — Public error detail must help callers recover without exposing internals or sensitive state.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Adopt the **Resource-oriented REST vs command/RPC** option that fits the workload and ownership boundary; Use resources for durable nouns and explicit commands for state transitions that do not map cleanly to CRUD.
- **MAY** — Adopt the **Synchronous vs asynchronous response** option that fits the workload and ownership boundary; Use async when work exceeds request deadlines, has variable duration, or needs independent retry.
- **MAY** — Adopt the **PUT vs PATCH** option that fits the workload and ownership boundary; Document absent/null/remove behavior and use conditional requests or versions.

### AVOID

- **AVOID** — Using 200 for failed operations with hidden error fields.
- **AVOID** — Unstable pagination under concurrent writes.
- **AVOID** — Silent coercion of malformed inputs.
- **AVOID** — Breaking clients by adding enum values they cannot parse.
- **AVOID** — Retries duplicating non-idempotent mutations.
- **AVOID** — Mapping database structs directly to public contracts.
- **AVOID** — Treating schema validation as complete business validation.
- **AVOID** — Retrying writes without idempotency.

### NEVER

- **NEVER** — Never expose internal stack traces, secrets, or database errors as public error detail.
- **NEVER** — Never promise idempotency, atomicity, ordering, or compatibility that storage and concurrency controls do not enforce.
- **NEVER** — Never paginate without a deterministic ordering and cursor/offset semantics.

## 16. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Generate malformed, oversized, deeply nested, duplicate-key, unknown-field, invalid Unicode, wrong content-type, and semantically inconsistent inputs.
- [ ] Replay state-changing requests before, during, and after commit with identical and mismatched idempotency fingerprints.
- [ ] Test cancellation and timeout before commit, during dependency calls, after commit, and during response serialization.
- [ ] Run compatibility suites for old/new clients, additive fields/enums, null/absent behavior, pagination cursors, and error schemas.
- [ ] Exercise object authorization, tenant scope, rate limits, bulk partial success, and stable ordering under concurrent writes.
- [ ] **Required fields:** Build a contract matrix for omitted/null/empty/zero/false/unknown values and verify serialization round trips.
- [ ] **Whitespace:** Locate every implementation path for whitespace, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Date validation:** Maintain positive/negative conformance fixtures and test normalization, international forms, boundary lengths, and parser differentials.
- [ ] **UUID/ID validation:** Maintain positive/negative conformance fixtures and test normalization, international forms, boundary lengths, and parser differentials.
- [ ] **Business invariants:** Create a decision table of field combinations and run concurrent tests where referenced state changes between validation and commit.
- [ ] **Malformed payloads:** Locate every implementation path for malformed payloads, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 17. Common production bugs and incorrect implementations

- Using 200 for failed operations with hidden error fields.
- Unstable pagination under concurrent writes.
- Silent coercion of malformed inputs.
- Breaking clients by adding enum values they cannot parse.
- Retries duplicating non-idempotent mutations.
- **Required fields:** Clients cannot clear a field, defaults overwrite explicit values, or silent unknown fields hide typos and compatibility bugs.
- **Whitespace:** A framework or provider default for whitespace is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Enum validation:** A framework or provider default for enum validation is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **URL validation:** Overly strict regexes reject valid values while permissive parsing accepts ambiguous or dangerous forms; validation is mistaken for verification.
- **Nested validation:** A framework or provider default for nested validation is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Unknown fields:** Clients cannot clear a field, defaults overwrite explicit values, or silent unknown fields hide typos and compatibility bugs.
- **Malformed payloads:** A framework or provider default for malformed payloads is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Mapping database structs directly to public contracts.
- Treating schema validation as complete business validation.
- Retrying writes without idempotency.
- Using unstable pagination order.
- Breaking clients through required fields or enum assumptions.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Input Validation** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- For **Required fields**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Clients cannot clear a field, defaults overwrite explicit values, or silent unknown fields hide typos and compatibility bugs.
- For **Whitespace**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for whitespace is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Date validation**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Overly strict regexes reject valid values while permissive parsing accepts ambiguous or dangerous forms; validation is mistaken for verification.
- For **UUID/ID validation**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Overly strict regexes reject valid values while permissive parsing accepts ambiguous or dangerous forms; validation is mistaken for verification.
- For **Business invariants**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Each field is individually valid while the combination is impossible, stale, or forbidden by current resource state.
- What does the client observe when the server commits but the response is lost?

## 20. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Input Validation**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] **Required fields:** Build a contract matrix for omitted/null/empty/zero/false/unknown values and verify serialization round trips.
- [ ] **Whitespace:** Locate every implementation path for whitespace, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Enum validation:** Locate every implementation path for enum validation, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **URL validation:** Maintain positive/negative conformance fixtures and test normalization, international forms, boundary lengths, and parser differentials.
- [ ] **Nested validation:** Locate every implementation path for nested validation, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Unknown fields:** Build a contract matrix for omitted/null/empty/zero/false/unknown values and verify serialization round trips.
- [ ] **Malformed payloads:** Locate every implementation path for malformed payloads, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] Capture actual wire examples and error behavior from deployed clients; generated documentation may not match runtime.

## 21. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [011. Request Lifecycle](011-request-lifecycle.md) — layer: `primitives`; profile: `api`.
- [014. API Design](../systems/014-api-design.md) — layer: `systems`; profile: `api`.
- [013. Error Architecture](013-error-architecture.md) — layer: `primitives`; profile: `api`.
- [061. Security Fundamentals](../cross-cutting/061-security-fundamentals.md) — layer: `cross-cutting`; profile: `security`.
- [022. Database Constraints](022-database-constraints.md) — layer: `primitives`; profile: `data_model`.
- [146. Cross-Cutting Implementation Checklist](../cross-cutting/146-cross-cutting-implementation-checklist.md) — layer: `cross-cutting`; profile: `checklist`.
- [116. Data Serialization](116-data-serialization.md) — layer: `primitives`; profile: `api`.
- [062. Web/API Security](../cross-cutting/062-web-api-security.md) — layer: `cross-cutting`; profile: `security`.
- [017. Filtering / Sorting / Query APIs](017-filtering-sorting-query-apis.md) — layer: `primitives`; profile: `api`.
- [070. API / Event Schema Evolution](070-api-event-schema-evolution.md) — layer: `primitives`; profile: `migration`.
- [015. API Versioning & Compatibility](../systems/015-api-versioning-and-compatibility.md) — layer: `systems`; profile: `api`.
- [049. Webhooks](../systems/049-webhooks.md) — layer: `systems`; profile: `api`.

## 22. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s025"></a> **[S025] HTTP Semantics.** IETF; 2022; RFC 9110 / STD 97. [https://www.rfc-editor.org/rfc/rfc9110.html](https://www.rfc-editor.org/rfc/rfc9110.html) — Tags: http, api, methods, status-codes.
- <a id="s026"></a> **[S026] HTTP Caching.** IETF; 2022; RFC 9111. [https://www.rfc-editor.org/rfc/rfc9111.html](https://www.rfc-editor.org/rfc/rfc9111.html) — Tags: http, caching, api.
- <a id="s027"></a> **[S027] Problem Details for HTTP APIs.** IETF; 2023; RFC 9457. [https://www.rfc-editor.org/rfc/rfc9457.html](https://www.rfc-editor.org/rfc/rfc9457.html) — Tags: api, errors, http.
- <a id="s028"></a> **[S028] OpenAPI Specification.** OpenAPI Initiative; 2025; 3.2.0. [https://spec.openapis.org/oas/v3.2.0.html](https://spec.openapis.org/oas/v3.2.0.html) — Tags: api, schema, compatibility, documentation.
- <a id="s029"></a> **[S029] GraphQL Specification.** GraphQL Foundation; 2025; September 2025. [https://spec.graphql.org/September2025/](https://spec.graphql.org/September2025/) — Tags: graphql, api, schema, compatibility.
- <a id="s030"></a> **[S030] gRPC Guides.** Cloud Native Computing Foundation; 2026; Current documentation. [https://grpc.io/docs/guides/](https://grpc.io/docs/guides/) — Tags: grpc, rpc, retries, timeouts, streaming.
- <a id="s031"></a> **[S031] Protocol Buffers Programming Guides.** Google; 2026; Current documentation. [https://protobuf.dev/programming-guides/](https://protobuf.dev/programming-guides/) — Tags: protobuf, serialization, schema-evolution.
- <a id="s032"></a> **[S032] AsyncAPI Specification.** AsyncAPI Initiative; 2026; 3.1.0. [https://www.asyncapi.com/docs/reference/specification/v3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0) — Tags: events, messaging, schema, api.
- <a id="s033"></a> **[S033] JSON Schema.** JSON Schema; 2022; Draft 2020-12. [https://json-schema.org/draft/2020-12](https://json-schema.org/draft/2020-12) — Tags: json, validation, schema.
- <a id="s114"></a> **[S114] Google API Improvement Proposals.** Google; 2026; Current. [https://google.aip.dev/](https://google.aip.dev/) — Tags: api, pagination, versioning, resource-design.
- <a id="s115"></a> **[S115] Microsoft REST API Guidelines.** Microsoft; 2026; Current. [https://github.com/microsoft/api-guidelines](https://github.com/microsoft/api-guidelines) — Tags: api, compatibility, pagination.
- <a id="s021"></a> **[S021] Application Security Verification Standard.** OWASP; 2025; ASVS 5.0.0. [https://owasp.org/www-project-application-security-verification-standard/](https://owasp.org/www-project-application-security-verification-standard/) — Tags: security, authentication, authorization, validation, logging.
- <a id="s023"></a> **[S023] OWASP API Security Top 10.** OWASP; 2023; 2023. [https://owasp.org/API-Security/editions/2023/en/0x11-t10/](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) — Tags: api, security, authorization, abuse.
- <a id="s034"></a> **[S034] Universally Unique IDentifiers (UUIDs).** IETF; 2024; RFC 9562. [https://www.rfc-editor.org/rfc/rfc9562.html](https://www.rfc-editor.org/rfc/rfc9562.html) — Tags: identifiers, uuid, ordering.
- <a id="s035"></a> **[S035] Date and Time on the Internet: Timestamps.** IETF; 2002; RFC 3339. [https://www.rfc-editor.org/rfc/rfc3339.html](https://www.rfc-editor.org/rfc/rfc3339.html) — Tags: time, date, serialization.
- <a id="s037"></a> **[S037] Unicode Normalization Forms.** Unicode Consortium; 2025; UAX #15, Unicode 17.0. [https://www.unicode.org/reports/tr15/](https://www.unicode.org/reports/tr15/) — Tags: unicode, validation, text.
- <a id="s038"></a> **[S038] IEEE Standard for Floating-Point Arithmetic.** IEEE; 2019; IEEE 754-2019. [https://standards.ieee.org/standard/754-2019.html](https://standards.ieee.org/standard/754-2019.html) — Tags: numeric, floating-point, precision.
- <a id="s039"></a> **[S039] General Decimal Arithmetic Specification.** Mike Cowlishaw / Speleotrove; 2009; 1.70. [https://speleotrove.com/decimal/decarith.html](https://speleotrove.com/decimal/decarith.html) — Tags: decimal, money, precision, rounding.

---

**Paper metadata:** canonical subtopics: 22; layer: `primitives`; domain profile: `api`; verified through: `2026-08-17`.
