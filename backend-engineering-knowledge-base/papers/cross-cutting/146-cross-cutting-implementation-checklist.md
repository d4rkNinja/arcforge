---
paper_number: 146
title: "Cross-Cutting Implementation Checklist"
layer: cross-cutting
domain_profile: checklist
corpus_version: 1.0.0
verified_through: 2026-08-17
canonical_source: "original/Pasted text.txt"
subtopic_count: 42
status: production-engineering-reference
---

# 146. Cross-Cutting Implementation Checklist

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## Canonical scope note

> Every feature paper should force the AI to consider:

## 1. Executive engineering summary

**Cross-Cutting Implementation Checklist** exists to force cross-cutting production reasoning before code changes and prevent apparently local features from violating system-wide contracts. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

The checklist is a release-control interface across product, domain, security, data, platform, and operations owners. It does not replace topic-specific design; it forces evidence that hidden cross-cutting contracts were considered. Tailor depth by risk while keeping a universal baseline.

The most important evidence base for this paper includes [S001](#s001) [S002](#s002) [S021](#s021) [S053](#s053). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Every feature changes at least one trust boundary, state transition, persistence rule, or operational burden.
- The absence of an explicit decision is still a decision—usually an unsafe framework default.
- Existing codebase behavior and compatibility obligations take precedence over greenfield elegance.
- Verification must cover concurrent, duplicate, timed-out, unauthorized, stale, partial, and rollback paths.
- A checklist is effective only when items produce evidence, owners, and release gates.

## 2. Scope and terminology map

The canonical topic list requires this paper to cover the following concerns. They are grouped only to expose relationships; no listed subtopic is omitted.

### Identity, trust, and access

**Authentication**, **Authorization**, **Tenant isolation**, **Data ownership**.

### State and lifecycle

**State transitions**, **Cleanup**, **Retention**, **Failure recovery**.

### Contracts and validation

**Validation**, **Concurrency**, **Duplicate requests**, **Retries**, **External failures**, **Partial failures**, **Caching**, **Pagination**, **Large datasets**, **Tracing**, **Error behavior**.

### Persistence and integrity

**Constraints**, **Transactions**, **Indexing**.

### Concurrency and distributed behavior

**Race conditions**, **Idempotency**, **Timeouts**, **Data consistency**.

### Security, privacy, and abuse

**Abuse prevention**, **Security**, **Privacy**, **Audit logs**.

### Operations and observability

**Rate limiting**, **Logging**, **Metrics**, **Deployment**, **Rollback**, **Scalability**, **Performance**, **Operational cost**.

### Testing and evolution

**Backward compatibility**, **Database migration**, **Data migration**, **Testing**.

### Boundary of the paper

This paper treats **Cross-Cutting Implementation Checklist** as a production subsystem or reusable reasoning primitive. It covers semantics, ownership, persistence, APIs, security, concurrency, distributed behavior, operations, evolution, and verification. Framework syntax and large implementation listings are intentionally excluded.

## 3. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S001](#s001) [S002](#s002) [S021](#s021) [S053](#s053)

1. **Invariant 1:** Every feature changes at least one trust boundary, state transition, persistence rule, or operational burden.
2. **Invariant 2:** The absence of an explicit decision is still a decision—usually an unsafe framework default.
3. **Invariant 3:** Existing codebase behavior and compatibility obligations take precedence over greenfield elegance.
4. **Invariant 4:** Verification must cover concurrent, duplicate, timed-out, unauthorized, stale, partial, and rollback paths.
5. **Invariant 5:** A checklist is effective only when items produce evidence, owners, and release gates.

Additional topic-specific invariants:

- **MUST — Authentication:** Define the exact semantics of **Authentication** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Concurrency:** Define the exact semantics of **Concurrency** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Data consistency:** Define the exact semantics of **Data consistency** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Logging:** Define the exact semantics of **Logging** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST — Cleanup:** Define the exact semantics of **Cleanup** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Operational cost:** Define the exact semantics of **Operational cost** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.

## 4. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Universal checklist vs risk-tiered checklist | Universal checks improve consistency but create noise; risk tiers focus effort but can misclassify work. | Use a universal baseline plus additional gates triggered by data, privilege, money, external side effects, or scale. |
| Manual review vs automated policy | Manual review catches context; automation enforces repeatable facts. | Automate mechanical checks and require human reasoning for invariants and trade-offs. |
| Pre-merge vs pre-release verification | Pre-merge catches defects early; pre-release validates integration and operations. | Use both with different evidence. |
| Blocking gate vs advisory signal | Blocking gates prevent known risk but can be bypassed under pressure; advisory signals are easier to ignore. | Block high-confidence correctness/security requirements and track exceptions explicitly. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 5. Ownership, state, and lifecycle

Apply it at `discovery → design → implementation → review → pre-deploy → rollout → post-deploy → cleanup`. Every unresolved item needs an owner, rationale, due date, and explicit risk acceptance. Re-run affected checks when scope or implementation changes.

```mermaid
stateDiagram-v2
    discovery --> risk_classified --> decisions_recorded --> implementation --> verification --> release --> observation --> cleanup
    verification --> blocked_or_exception
    release --> rollback_or_forward_fix
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 6. Data model and API implications

Each item should produce a decision or artifact: invariant, threat model, state machine, schema, migration plan, load model, test, dashboard, alert, runbook, or rollback criterion. Yes/no boxes without evidence become ritual rather than control.

A production representation commonly needs the following fields or equivalent evidence:

- change identifier, scope, risk tier, owner, and reviewer.
- decision/evidence link for each applicable concern.
- exception rationale, approver, expiry, and compensating control.
- deployment/rollback/recovery gates and observed outcome.
- cleanup tasks, due dates, and post-release verification.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 7. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### 7.1. Authentication

- **MUST — engineering rule:** Define the exact semantics of **Authentication** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for authentication is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for authentication, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.2. Authorization

- **MUST — engineering rule:** Define the exact semantics of **Authorization** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for authorization is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for authorization, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.3. Validation

- **MUST — engineering rule:** Define the exact semantics of **Validation** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for validation is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for validation, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.4. Tenant isolation

- **MUST — engineering rule:** Derive tenant context from an authenticated, authorized binding; propagate it explicitly through queries, caches, jobs, events, files, metrics, and audit records. Make unscoped access difficult or impossible.
- **Production failure mode:** A missing filter, reused cache key, delayed job, or admin path reads or writes another tenant's data.
- **Existing-codebase evidence:** Search for data-access methods that accept no tenant scope; run mutation and property tests that swap tenant identifiers at every boundary.

### 7.5. Data ownership

- **MUST — engineering rule:** Assign one owner for invariants and writes, expose a narrow versioned interface, enforce dependency direction mechanically, and communicate cross-boundary facts through explicit calls/events.
- **Production failure mode:** Modules share tables/models/utilities until changes require lockstep deployment and no team can reason locally.
- **Existing-codebase evidence:** Build an import/dependency graph, map table writes, and flag cross-boundary direct access.

### 7.6. Constraints

- **MUST — engineering rule:** Define the exact semantics of **Constraints** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for constraints is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for constraints, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.7. Transactions

- **MUST — engineering rule:** Define the exact semantics of **Transactions** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for transactions is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for transactions, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.8. Race conditions

- **SHOULD — engineering rule:** Use barriers/hooks to force the critical interleaving, repeat across real database isolation, and assert the invariant rather than timing or one response.
- **Production failure mode:** A probabilistic sleep-based test passes while the actual race remains reachable.
- **Existing-codebase evidence:** Instrument the exact read/check/write or lease boundary and run deterministic competing operations.

### 7.9. Concurrency

- **SHOULD — engineering rule:** Define the exact semantics of **Concurrency** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for concurrency is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for concurrency, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.10. Idempotency

- **MUST — engineering rule:** Scope keys to caller and operation, bind them to a canonical request fingerprint, reserve atomically, persist terminal outcome, and distinguish in-progress, succeeded, retryable-failed, and permanently-failed states.
- **Production failure mode:** Two concurrent requests both execute, or the same key is reused with different parameters and returns the wrong result.
- **Existing-codebase evidence:** Synchronize duplicate requests before first commit; test timeout-after-commit, key mismatch, expiry, and response replay.

### 7.11. Duplicate requests

- **SHOULD — engineering rule:** Define the exact semantics of **Duplicate requests** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for duplicate requests is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for duplicate requests, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.12. Retries

- **SHOULD — engineering rule:** Define the exact semantics of **Retries** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for retries is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for retries, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.13. Timeouts

- **MUST — engineering rule:** Establish an end-to-end deadline, allocate smaller downstream budgets, propagate cancellation, and stop expensive or side-effecting work when the result is no longer useful unless explicitly designed otherwise.
- **Production failure mode:** Requests wait indefinitely, downstream work continues after callers leave, or nested timeouts exceed the original budget.
- **Existing-codebase evidence:** Inject slow dependencies at each hop and verify cancellation reaches database, network calls, streams, and workers.

### 7.14. External failures

- **SHOULD — engineering rule:** Define the exact semantics of **External failures** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for external failures is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for external failures, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.15. Partial failures

- **SHOULD — engineering rule:** Define the exact semantics of **Partial failures** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for partial failures is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for partial failures, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.16. State transitions

- **MUST — engineering rule:** Model transitions as commands with expected current state/version, guard evaluation, atomic state/history update, and idempotent side-effect triggering.
- **Production failure mode:** Generic updates skip guards, concurrent transitions both succeed, or terminal records are silently reopened.
- **Existing-codebase evidence:** Generate the state-transition matrix and test every allowed/forbidden pair plus simultaneous conflicting commands.

### 7.17. Data consistency

- **SHOULD — engineering rule:** Define the exact semantics of **Data consistency** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for data consistency is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for data consistency, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.18. Caching

- **SHOULD — engineering rule:** Define the exact semantics of **Caching** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for caching is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for caching, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.19. Indexing

- **SHOULD — engineering rule:** Design indexes from concrete query predicates and ordering, considering equality/range order, selectivity, write amplification, storage, uniqueness, tenant prefixing, and online build behavior.
- **Production failure mode:** An index exists but cannot support the actual predicate/order, low-selectivity indexes waste writes, or an online build saturates I/O and replication.
- **Existing-codebase evidence:** Capture explain plans and latency for representative cardinalities; rehearse create/drop/rebuild on production-like data.

### 7.20. Pagination

- **SHOULD — engineering rule:** Use a total deterministic order with a unique tie-breaker; encode cursor position and query shape opaquely; validate limits and preserve authorization/filter semantics across pages.
- **Production failure mode:** Concurrent inserts/updates cause duplicates or omissions, cursors are tampered with, or deep offsets exhaust the database.
- **Existing-codebase evidence:** Paginate while mutating boundary rows and verify every eligible record appears at most once under the documented consistency model.

### 7.21. Large datasets

- **SHOULD — engineering rule:** Define the exact semantics of **Large datasets** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for large datasets is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for large datasets, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.22. Rate limiting

- **SHOULD — engineering rule:** Choose identity/scope, algorithm, burst capacity, window clock, atomic update, distributed consistency, response headers, and fail behavior according to the abuse and availability threat.
- **Production failure mode:** Window-boundary bursts, racey counters, NAT collateral damage, or fail-open behavior allow abuse; fail-closed can create an outage.
- **Existing-codebase evidence:** Test simultaneous requests across nodes, clock skew, key eviction, backend failure, IPv6/proxy identity, and Retry-After semantics.

### 7.23. Abuse prevention

- **SHOULD — engineering rule:** Layer per-account, credential, device, IP/network, tenant, and global controls; normalize identifiers before counting; avoid revealing existence; collect signals with privacy limits and provide recovery from false positives.
- **Production failure mode:** Attackers distribute attempts across keys, weaponize lockouts, or infer valid accounts from timing and error differences.
- **Existing-codebase evidence:** Replay distributed attack patterns and compare status, body, timing, notification, and recovery behavior for existing/non-existing targets.

### 7.24. Security

- **MUST — engineering rule:** Define the exact semantics of **Security** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for security is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for security, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.25. Privacy

- **MUST — engineering rule:** Define the exact semantics of **Privacy** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for privacy is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for privacy, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.26. Logging

- **SHOULD — engineering rule:** Define the exact semantics of **Logging** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for logging is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for logging, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.27. Metrics

- **SHOULD — engineering rule:** Define metric type, unit, monotonicity, aggregation, label allowlist, and ownership. Use histograms suitable for required percentiles and keep user/resource IDs out of labels.
- **Production failure mode:** Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- **Existing-codebase evidence:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.

### 7.28. Tracing

- **SHOULD — engineering rule:** Define the exact semantics of **Tracing** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for tracing is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for tracing, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.29. Audit logs

- **MUST — engineering rule:** Record real actor, effective actor, action, resource, tenant, timestamp, request/trace, policy context, outcome, and appropriately minimized change details in tamper-resistant storage.
- **Production failure mode:** Security-sensitive changes cannot be attributed, audit data leaks secrets, or failed attempts vanish.
- **Existing-codebase evidence:** Exercise successful/failed/admin/impersonated/bulk actions and verify atomicity, retention, search, export, and access controls.

### 7.30. Error behavior

- **SHOULD — engineering rule:** Define the exact semantics of **Error behavior** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for error behavior is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for error behavior, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.31. Backward compatibility

- **SHOULD — engineering rule:** Define a compatibility window in which old and new readers/writers coexist. Make changes additive first, preserve unknown fields where required, and test both deployment orders.
- **Production failure mode:** A new writer emits data an old reader cannot parse, or rollback code cannot read records created during the failed release.
- **Existing-codebase evidence:** Run an N/N+1 matrix for requests, stored data, events, queues, caches, and rollback.

### 7.32. Database migration

- **SHOULD — engineering rule:** Define the exact semantics of **Database migration** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for database migration is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for database migration, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.33. Data migration

- **SHOULD — engineering rule:** Define the exact semantics of **Data migration** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for data migration is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for data migration, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.34. Cleanup

- **MUST — engineering rule:** Define the exact semantics of **Cleanup** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for cleanup is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for cleanup, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.35. Retention

- **MUST — engineering rule:** Define the exact semantics of **Retention** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for retention is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for retention, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.36. Failure recovery

- **MUST — engineering rule:** Define the exact semantics of **Failure recovery** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for failure recovery is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for failure recovery, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.37. Testing

- **SHOULD — engineering rule:** Define the exact semantics of **Testing** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for testing is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for testing, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.38. Deployment

- **SHOULD — engineering rule:** Define the exact semantics of **Deployment** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for deployment is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for deployment, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.39. Rollback

- **SHOULD — engineering rule:** Define what can be reversed, what requires compensation or forward repair, and how data written by the new version remains readable. Rehearse the exact control-plane and data-plane sequence.
- **Production failure mode:** Code rolls back while schema/data/side effects do not, creating a second outage or corruption.
- **Existing-codebase evidence:** Perform a production-like rollback drill after generating new-version data and partially completed work.

### 7.40. Scalability

- **SHOULD — engineering rule:** Define the exact semantics of **Scalability** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for scalability is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for scalability, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.41. Performance

- **SHOULD — engineering rule:** Define the exact semantics of **Performance** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for performance is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for performance, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.42. Operational cost

- **SHOULD — engineering rule:** Define the exact semantics of **Operational cost** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for operational cost is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for operational cost, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

## 8. Concurrency, transactions, idempotency, and consistency

Cross-cutting decisions must agree: an API idempotency promise needs a database constraint; a retry policy needs duplicate-safe effects; deletion needs cache/index/backup handling; authorization needs tenant-scoped queries and jobs. Contradictions are release blockers.

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

Common failure is declaring a concern 'not applicable' without tracing data and side effects. Other failures include relying on framework defaults, testing only the happy path, forgetting mixed versions, and calling rollback a plan when external effects cannot be undone.

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

Store checklist evidence with the change, automate mechanical gates, and monitor exception age, escaped defects, rollback readiness, and post-release cleanup. Use incident findings to strengthen questions rather than merely add more generic boxes.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 13. Compatibility, schema evolution, migration, deployment, and rollback

Version the checklist and map changes to policy or incident evidence. Keep old completed records interpretable. Remove low-signal items, add risk-triggered modules, and avoid making every change satisfy the heaviest possible process.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Cross-Cutting Implementation Checklist path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Authentication`, `Duplicate requests`, `Large datasets`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Cross-Cutting Implementation Checklist; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 15. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Cross-Cutting Implementation Checklist** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Authentication**: Define the exact semantics of **Authentication** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **Concurrency**: Define the exact semantics of **Concurrency** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **Data consistency**: Define the exact semantics of **Data consistency** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **Logging**: Define the exact semantics of **Logging** within Cross-Cutting Implementation Checklist: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.

### SHOULD

- **SHOULD** — Every feature changes at least one trust boundary, state transition, persistence rule, or operational burden.
- **SHOULD** — The absence of an explicit decision is still a decision—usually an unsafe framework default.
- **SHOULD** — Existing codebase behavior and compatibility obligations take precedence over greenfield elegance.
- **SHOULD** — Verification must cover concurrent, duplicate, timed-out, unauthorized, stale, partial, and rollback paths.
- **SHOULD** — A checklist is effective only when items produce evidence, owners, and release gates.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Adopt the **Universal checklist vs risk-tiered checklist** option that fits the workload and ownership boundary; Use a universal baseline plus additional gates triggered by data, privilege, money, external side effects, or scale.
- **MAY** — Adopt the **Manual review vs automated policy** option that fits the workload and ownership boundary; Automate mechanical checks and require human reasoning for invariants and trade-offs.
- **MAY** — Adopt the **Pre-merge vs pre-release verification** option that fits the workload and ownership boundary; Use both with different evidence.

### AVOID

- **AVOID** — Checking authentication but not object authorization.
- **AVOID** — Testing happy path only.
- **AVOID** — Shipping schema change before mixed-version compatibility.
- **AVOID** — No owner for cleanup/reconciliation.
- **AVOID** — Rollback plan that cannot undo side effects.
- **AVOID** — Checking boxes without evidence.
- **AVOID** — Marking concerns inapplicable without tracing effects.
- **AVOID** — Treating review as substitute for database/runtime controls.

### NEVER

- **NEVER** — Never accept 'not applicable' without an inspected data/side-effect path.
- **NEVER** — Never approve a change whose rollback and recovery assumptions contradict committed side effects.
- **NEVER** — Never allow checklist completion to substitute for executable controls and tests.

## 16. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Apply the checklist to representative low-, medium-, and high-risk changes and verify the expected evidence and gates differ appropriately.
- [ ] Seed contradictions—retry without idempotency, delete without index cleanup, role cache without revocation—and ensure review catches them.
- [ ] Audit 'not applicable' decisions for traced data flows and side effects.
- [ ] Simulate rollback, partial deployment, and incident response using the produced artifacts.
- [ ] Measure exception age and escaped defects; refine items from evidence rather than expanding ritualistically.
- [ ] **Authentication:** Locate every implementation path for authentication, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Concurrency:** Locate every implementation path for concurrency, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Data consistency:** Locate every implementation path for data consistency, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Logging:** Locate every implementation path for logging, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Cleanup:** Locate every implementation path for cleanup, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Operational cost:** Locate every implementation path for operational cost, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 17. Common production bugs and incorrect implementations

- Checking authentication but not object authorization.
- Testing happy path only.
- Shipping schema change before mixed-version compatibility.
- No owner for cleanup/reconciliation.
- Rollback plan that cannot undo side effects.
- **Authentication:** A framework or provider default for authentication is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Race conditions:** A probabilistic sleep-based test passes while the actual race remains reachable.
- **Partial failures:** A framework or provider default for partial failures is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Large datasets:** A framework or provider default for large datasets is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Tracing:** A framework or provider default for tracing is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Retention:** A framework or provider default for retention is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Operational cost:** A framework or provider default for operational cost is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Checking boxes without evidence.
- Marking concerns inapplicable without tracing effects.
- Treating review as substitute for database/runtime controls.
- Omitting post-deploy cleanup and ownership.
- Accepting a rollback plan that cannot address committed external effects.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Cross-Cutting Implementation Checklist** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- For **Authentication**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for authentication is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Concurrency**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for concurrency is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Data consistency**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for data consistency is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Logging**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for logging is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Cleanup**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for cleanup is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- What evidence, owner, and release gate correspond to every applicable item?

## 20. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Cross-Cutting Implementation Checklist**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] **Authentication:** Locate every implementation path for authentication, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Race conditions:** Instrument the exact read/check/write or lease boundary and run deterministic competing operations.
- [ ] **Partial failures:** Locate every implementation path for partial failures, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Large datasets:** Locate every implementation path for large datasets, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Tracing:** Locate every implementation path for tracing, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Retention:** Locate every implementation path for retention, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Operational cost:** Locate every implementation path for operational cost, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] Compare the change against incidents, exceptions, and cleanup debt; do not rely on the checklist template alone.

## 21. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [012. Input Validation](../primitives/012-input-validation.md) — layer: `primitives`; profile: `api`.
- [022. Database Constraints](../primitives/022-database-constraints.md) — layer: `primitives`; profile: `data_model`.
- [023. Database Transactions](../primitives/023-database-transactions.md) — layer: `primitives`; profile: `transactions`.
- [024. Concurrency Anomalies](../primitives/024-concurrency-anomalies.md) — layer: `primitives`; profile: `transactions`.
- [025. Concurrency Control](../primitives/025-concurrency-control.md) — layer: `primitives`; profile: `transactions`.
- [035. State Machines](../primitives/035-state-machines.md) — layer: `primitives`; profile: `transactions`.
- [036. Idempotency](../primitives/036-idempotency.md) — layer: `primitives`; profile: `transactions`.
- [052. Retry Engineering](../primitives/052-retry-engineering.md) — layer: `primitives`; profile: `resilience`.
- [053. Timeout Engineering](../primitives/053-timeout-engineering.md) — layer: `primitives`; profile: `resilience`.
- [055. Resilience](055-resilience.md) — layer: `cross-cutting`; profile: `resilience`.
- [061. Security Fundamentals](061-security-fundamentals.md) — layer: `cross-cutting`; profile: `security`.
- [090. Testing Foundations](090-testing-foundations.md) — layer: `cross-cutting`; profile: `testing`.
- [093. Failure Testing](093-failure-testing.md) — layer: `cross-cutting`; profile: `testing`.
- [105. Graceful Shutdown](105-graceful-shutdown.md) — layer: `cross-cutting`; profile: `runtime`.

## 22. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s003"></a> **[S003] Digital Identity Guidelines.** NIST; 2025; SP 800-63-4. [https://pages.nist.gov/800-63-4/sp800-63.html](https://pages.nist.gov/800-63-4/sp800-63.html) — Tags: identity, authentication, federation, privacy.
- <a id="s007"></a> **[S007] Best Current Practice for OAuth 2.0 Security.** IETF; 2025; RFC 9700 / BCP 240. [https://www.rfc-editor.org/rfc/rfc9700.html](https://www.rfc-editor.org/rfc/rfc9700.html) — Tags: oauth, security, tokens, redirects.
- <a id="s021"></a> **[S021] Application Security Verification Standard.** OWASP; 2025; ASVS 5.0.0. [https://owasp.org/www-project-application-security-verification-standard/](https://owasp.org/www-project-application-security-verification-standard/) — Tags: security, authentication, authorization, validation, logging.
- <a id="s022"></a> **[S022] OWASP Top 10:2025.** OWASP; 2025; 2025. [https://owasp.org/Top10/](https://owasp.org/Top10/) — Tags: security, web, risks.
- <a id="s023"></a> **[S023] OWASP API Security Top 10.** OWASP; 2023; 2023. [https://owasp.org/API-Security/editions/2023/en/0x11-t10/](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) — Tags: api, security, authorization, abuse.
- <a id="s025"></a> **[S025] HTTP Semantics.** IETF; 2022; RFC 9110 / STD 97. [https://www.rfc-editor.org/rfc/rfc9110.html](https://www.rfc-editor.org/rfc/rfc9110.html) — Tags: http, api, methods, status-codes.
- <a id="s027"></a> **[S027] Problem Details for HTTP APIs.** IETF; 2023; RFC 9457. [https://www.rfc-editor.org/rfc/rfc9457.html](https://www.rfc-editor.org/rfc/rfc9457.html) — Tags: api, errors, http.
- <a id="s040"></a> **[S040] PostgreSQL Documentation.** PostgreSQL Global Development Group; 2026; 18 current. [https://www.postgresql.org/docs/18/](https://www.postgresql.org/docs/18/) — Tags: database, sql, transactions, indexes, concurrency, backup.
- <a id="s043"></a> **[S043] Designing Data-Intensive Applications, Second Edition.** Martin Kleppmann and Chris Riccomini / O'Reilly; 2025; 2nd edition. [https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/) — Tags: distributed-systems, databases, consistency, streams.
- <a id="s053"></a> **[S053] Site Reliability Engineering.** Google; 2016; Online book. [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/) — Tags: reliability, operations, monitoring, capacity.
- <a id="s055"></a> **[S055] Timeouts, Retries, and Backoff with Jitter.** AWS Builders' Library; 2026; Current article. [https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) — Tags: retries, timeouts, jitter, resilience.
- <a id="s066"></a> **[S066] OpenTelemetry Specification.** Cloud Native Computing Foundation; 2026; 1.59.0. [https://opentelemetry.io/docs/specs/otel/](https://opentelemetry.io/docs/specs/otel/) — Tags: observability, tracing, metrics, logs.
- <a id="s070"></a> **[S070] Kubernetes Documentation.** Cloud Native Computing Foundation; 2026; Current. [https://kubernetes.io/docs/](https://kubernetes.io/docs/) — Tags: deployment, containers, health, shutdown, autoscaling.
- <a id="s077"></a> **[S077] Secure Software Development Framework.** NIST; 2022; SP 800-218 v1.1. [https://csrc.nist.gov/pubs/sp/800/218/final](https://csrc.nist.gov/pubs/sp/800/218/final) — Tags: secure-development, ci-cd, supply-chain.
- <a id="s101"></a> **[S101] Computer Security Incident Handling Guide.** NIST; 2025; SP 800-61 Rev. 3. [https://csrc.nist.gov/pubs/sp/800/61/r3/final](https://csrc.nist.gov/pubs/sp/800/61/r3/final) — Tags: incidents, operations, recovery.
- <a id="s103"></a> **[S103] AI Risk Management Framework.** NIST; 2023; AI RMF 1.0. [https://www.nist.gov/itl/ai-risk-management-framework](https://www.nist.gov/itl/ai-risk-management-framework) — Tags: ai, risk, governance.

---

**Paper metadata:** canonical subtopics: 42; layer: `cross-cutting`; domain profile: `checklist`; verified through: `2026-08-17`.
