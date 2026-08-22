# 090. Testing Foundations

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Testing Foundations** exists to produce evidence that observable behavior and invariants survive realistic inputs, concurrency, failures, and change. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

Tests provide evidence at the layer where a risk exists. Pure units prove local logic; integration tests prove real database, serialization, protocol, and provider behavior; end-to-end tests prove wiring and user-visible flows. Do not mock away the boundary whose semantics are under review.

The most important evidence base for this paper includes [S052](#s052) [S125](#s125) [S126](#s126) [S127](#s127). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- A test suite must prove invariants at the layer where they can fail; mocks cannot prove database isolation or provider compatibility.
- Determinism requires control of time, randomness, concurrency, external dependencies, and cleanup.
- Race, retry, duplicate, and partial-failure tests need synchronized interleavings rather than repeated hope-based execution.
- Performance tests are capacity experiments with workload models and saturation signals, not single latency numbers.
- Production-like data must preserve distribution and shape without exposing real PII.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Testing Foundations** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- Which real infrastructure or interleaving must be used because a mock cannot reproduce the risk?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Testing Foundations**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Classify tests by fidelity and invariant; identify mocks that replace the behavior under review.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S052](#s052) [S125](#s125) [S126](#s126) [S127](#s127)

1. **Invariant 1:** A test suite must prove invariants at the layer where they can fail; mocks cannot prove database isolation or provider compatibility.
2. **Invariant 2:** Determinism requires control of time, randomness, concurrency, external dependencies, and cleanup.
3. **Invariant 3:** Race, retry, duplicate, and partial-failure tests need synchronized interleavings rather than repeated hope-based execution.
4. **Invariant 4:** Performance tests are capacity experiments with workload models and saturation signals, not single latency numbers.
5. **Invariant 5:** Production-like data must preserve distribution and shape without exposing real PII.

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Unit vs integration test | Unit tests isolate logic quickly; integration tests prove real infrastructure and protocol semantics. | Place each invariant at the lowest layer that faithfully reproduces its failure mode. |
| Unit vs integration | Unit tests localize logic quickly; integration tests prove contracts with real infrastructure. | Use both and place each invariant at the lowest faithful layer. |
| Fixture vs factory | Fixtures are stable but rigid; factories express intent but can hide invalid defaults. | Use minimal factories with explicit relevant fields and schema-valid baselines. |
| Deterministic schedule vs stress race test | Controlled schedules reproduce specific anomalies; stress tests discover unknown interleavings but can be flaky. | Use targeted deterministic tests plus bounded stress runs. |
| Synthetic vs production-derived data | Synthetic data is safe and controllable; production-derived shape is realistic but requires strong anonymization. | Generate representative distributions and separately validate against sanitized samples. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

A test asset moves through `requirement/invariant → scenario/interleaving → controlled setup → execution → assertion → cleanup → diagnosis`. Failing cases must be reproducible with captured seeds, clock, versions, and fault schedule. Test data has its own creation and destruction lifecycle.

```mermaid
stateDiagram-v2
    invariant --> scenario --> controlled_setup --> execution --> assertion --> cleanup
    assertion --> diagnostic_artifacts
    failure --> reproducible_case
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Define observable outcomes, invariants, timing bounds, side effects, and allowed nondeterminism before implementation. Each test should state why its layer is faithful. Contract and compatibility suites should be executable by both producers and consumers.

A production representation commonly needs the following fields or equivalent evidence:

- test invariant, risk, layer/fidelity, and expected observable outcome.
- fixture/factory/schema version and controlled clock/random seed.
- fault/interleaving schedule and infrastructure versions.
- result, diagnostics, traces/query plans/artifacts, and cleanup status.
- regression/incident reference and release gate.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **API tests**
- **Database tests**
- **Property-based tests**
- **Fuzz tests**
- **Mutation tests**
- **Performance tests**
- **Security tests**
- **Chaos tests**

### 8.1. Unit tests

- **SHOULD — engineering rule:** Place each invariant at the lowest test layer that faithfully includes the mechanism that can violate it; use real databases/protocols for constraints, isolation, serialization, and provider contracts.
- **Production failure mode:** Mocks confirm implementation assumptions rather than real behavior and regressions escape at integration boundaries.
- **Existing-codebase evidence:** Map each production failure mode to at least one faithful test and identify which dependencies are real versus simulated.

### 8.2. Integration tests

- **SHOULD — engineering rule:** Place each invariant at the lowest test layer that faithfully includes the mechanism that can violate it; use real databases/protocols for constraints, isolation, serialization, and provider contracts.
- **Production failure mode:** Mocks confirm implementation assumptions rather than real behavior and regressions escape at integration boundaries.
- **Existing-codebase evidence:** Map each production failure mode to at least one faithful test and identify which dependencies are real versus simulated.

### 8.5. Contract tests

- **SHOULD — engineering rule:** Place each invariant at the lowest test layer that faithfully includes the mechanism that can violate it; use real databases/protocols for constraints, isolation, serialization, and provider contracts.
- **Production failure mode:** Mocks confirm implementation assumptions rather than real behavior and regressions escape at integration boundaries.
- **Existing-codebase evidence:** Map each production failure mode to at least one faithful test and identify which dependencies are real versus simulated.

### 8.6. End-to-end tests

- **SHOULD — engineering rule:** Place each invariant at the lowest test layer that faithfully includes the mechanism that can violate it; use real databases/protocols for constraints, isolation, serialization, and provider contracts.
- **Production failure mode:** Mocks confirm implementation assumptions rather than real behavior and regressions escape at integration boundaries.
- **Existing-codebase evidence:** Map each production failure mode to at least one faithful test and identify which dependencies are real versus simulated.

## 9. Concurrency, transactions, idempotency, and consistency

Concurrency tests need barriers or hooks to force conflicting operations into the critical window. Failure tests inject faults between durable steps, not only before the call. Property and model-based tests explore sequences while database constraints remain the final oracle.

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

Flaky sleep-based tests, shared fixtures, leaked resources, unrealistic mocks, and assertions on internal call order create false confidence. A passing happy path says nothing about duplicate, stale, timeout, unauthorized, or partial-success behavior.

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

Track suite duration, flake rate, retry masking, mutation score where used, coverage of critical invariants, failure-injection coverage, load-test saturation, and escaped defects. Preserve diagnostics—logs, traces, query plans, seeds, and artifacts—without test secrets or PII.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

Tests must cover rolling compatibility and migrations, not only the final schema. Retain regression cases for incidents. Remove obsolete tests only when the contract is deliberately retired; otherwise refactors can silently weaken evidence.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Testing Foundations path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Unit tests`, `Database tests`, `Property-based tests`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Testing Foundations; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Testing Foundations** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Unit tests**: Place each invariant at the lowest test layer that faithfully includes the mechanism that can violate it; use real databases/protocols for constraints, isolation, serialization, and provider contracts.

### SHOULD

- **SHOULD** — A test suite must prove invariants at the layer where they can fail; mocks cannot prove database isolation or provider compatibility.
- **SHOULD** — Determinism requires control of time, randomness, concurrency, external dependencies, and cleanup.
- **SHOULD** — Race, retry, duplicate, and partial-failure tests need synchronized interleavings rather than repeated hope-based execution.
- **SHOULD** — Performance tests are capacity experiments with workload models and saturation signals, not single latency numbers.
- **SHOULD** — Production-like data must preserve distribution and shape without exposing real PII.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Choose **Unit vs integration test** according to the stated trade-off: Place each invariant at the lowest layer that faithfully reproduces its failure mode.
- **MAY** — Adopt the **Unit vs integration** option that fits the workload and ownership boundary; Use both and place each invariant at the lowest faithful layer.
- **MAY** — Adopt the **Fixture vs factory** option that fits the workload and ownership boundary; Use minimal factories with explicit relevant fields and schema-valid baselines.
- **MAY** — Adopt the **Deterministic schedule vs stress race test** option that fits the workload and ownership boundary; Use targeted deterministic tests plus bounded stress runs.

### AVOID

- **AVOID** — Tests passing against mocks but failing under real isolation.
- **AVOID** — Sleep-based async tests.
- **AVOID** — Shared test data causing order dependence.
- **AVOID** — Load test missing tail latency and saturation.
- **AVOID** — Failure injection after rather than during the critical window.
- **AVOID** — Mocking the behavior being tested.
- **AVOID** — Using sleeps for concurrency.
- **AVOID** — Asserting implementation call order instead of outcomes.

### NEVER

- **NEVER** — Never use production PII or secrets as convenient test fixtures.
- **NEVER** — Never accept retries as a fix for flaky tests without identifying nondeterminism.
- **NEVER** — Never claim concurrency safety from sequential tests.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Intentionally mutate or break each critical invariant and prove at least one faithful test fails for the correct reason.
- [ ] Repeat tests with controlled time, randomness, scheduling, network faults, and database conflicts; no sleep-based success assumptions.
- [ ] Run tests independently, reordered, and in parallel; fixtures and cleanup must not leak state.
- [ ] Compare mocks/fakes with real provider and infrastructure contracts, including error and limit behavior.
- [ ] Preserve seeds, traces, logs, query plans, and artifacts for reproducibility while removing secrets/PII.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Sharing mutable fixtures across tests.
- Calling a benchmark a capacity test without workload/saturation data.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [094. Load & Performance Testing](094-load-and-performance-testing.md)
- [092. Concurrency Testing](092-concurrency-testing.md)
- [091. Test Data](091-test-data.md)
- [093. Failure Testing](093-failure-testing.md)
- [146. Cross-Cutting Implementation Checklist](146-cross-cutting-implementation-checklist.md)
- 053. Timeout Engineering — in the `resilience-flow-control` skill.
- [095. Performance Engineering](095-performance-engineering.md)
- 022. Database Constraints — in the `data-storage` skill.
- 036. Idempotency — in the `transactions-consistency` skill.
- 023. Database Transactions — in the `transactions-consistency` skill.
- 062. Web/API Security — in the `security-privacy` skill.
- 106. Deployment Safety — in the `runtime-delivery` skill.

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s021"></a> **[S021] Application Security Verification Standard.** OWASP; 2025; ASVS 5.0.0. [https://owasp.org/www-project-application-security-verification-standard/](https://owasp.org/www-project-application-security-verification-standard/) — Tags: security, authentication, authorization, validation, logging.
- <a id="s022"></a> **[S022] OWASP Top 10:2025.** OWASP; 2025; 2025. [https://owasp.org/Top10/](https://owasp.org/Top10/) — Tags: security, web, risks.
- <a id="s023"></a> **[S023] OWASP API Security Top 10.** OWASP; 2023; 2023. [https://owasp.org/API-Security/editions/2023/en/0x11-t10/](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) — Tags: api, security, authorization, abuse.
- <a id="s040"></a> **[S040] PostgreSQL Documentation.** PostgreSQL Global Development Group; 2026; 18 current. [https://www.postgresql.org/docs/18/](https://www.postgresql.org/docs/18/) — Tags: database, sql, transactions, indexes, concurrency, backup.
- <a id="s041"></a> **[S041] MongoDB Manual.** MongoDB; 2026; 8.0. [https://www.mongodb.com/docs/v8.0/](https://www.mongodb.com/docs/v8.0/) — Tags: database, documents, transactions, indexes, sharding.
- <a id="s052"></a> **[S052] Jepsen Analyses.** Jepsen; 2026; Living collection. [https://jepsen.io/analyses](https://jepsen.io/analyses) — Tags: consistency, distributed-systems, testing, failures.
- <a id="s054"></a> **[S054] The Site Reliability Workbook.** Google; 2018; Online book. [https://sre.google/workbook/table-of-contents/](https://sre.google/workbook/table-of-contents/) — Tags: reliability, operations, slo, testing.
- <a id="s125"></a> **[S125] Principles of Chaos Engineering.** Chaos Engineering community; 2026; Current. [https://principlesofchaos.org/](https://principlesofchaos.org/) — Tags: chaos-testing, resilience, failures.
- <a id="s126"></a> **[S126] QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs.** Chalmers University; 2000; ICFP 2000. [https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf](https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf) — Tags: testing, property-based-testing.
- <a id="s127"></a> **[S127] OSS-Fuzz Documentation.** Google; 2026; Current. [https://google.github.io/oss-fuzz/](https://google.github.io/oss-fuzz/) — Tags: fuzzing, testing, security.
