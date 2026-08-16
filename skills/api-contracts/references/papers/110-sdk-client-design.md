# 110. SDK / Client Design

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**SDK / Client Design** exists to provide predictable, safe interaction with backend contracts across networks, versions, and user environments. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

A client library or CLI translates transport into a stable caller-facing contract. It owns safe defaults for base URL, authentication, timeout, retry, pagination, cancellation, serialization, telemetry, and error mapping, while leaving business policy and irreversible retries under caller control.

The most important evidence base for this paper includes [S025](#s025) [S027](#s027) [S028](#s028) [S055](#s055). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Client defaults for timeout, retry, base URL, and authentication become system-wide behavior.
- SDKs must preserve server error semantics rather than collapsing everything into generic exceptions.
- Pagination, streaming, cancellation, and backpressure need first-class APIs.
- Telemetry and user-agent metadata must avoid sensitive data while enabling compatibility diagnosis.
- Long-lived and mobile clients make backward compatibility and deprecation windows operational requirements.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **SDK / Client Design** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- Which automatic behavior could duplicate writes, leak credentials, or break long-lived callers?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **SDK / Client Design**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Inventory supported client/runtime versions and default timeout/retry behavior already shipped.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S025](#s025) [S027](#s027) [S028](#s028) [S055](#s055)

1. **Invariant 1:** Client defaults for timeout, retry, base URL, and authentication become system-wide behavior.
2. **Invariant 2:** SDKs must preserve server error semantics rather than collapsing everything into generic exceptions.
3. **Invariant 3:** Pagination, streaming, cancellation, and backpressure need first-class APIs.
4. **Invariant 4:** Telemetry and user-agent metadata must avoid sensitive data while enabling compatibility diagnosis.
5. **Invariant 5:** Long-lived and mobile clients make backward compatibility and deprecation windows operational requirements.

Additional topic-specific invariants:

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Generated vs hand-written SDK | Generation tracks schema and consistency; hand-written clients provide idiomatic behavior but can drift. | Generate low-level models/transports and handcraft stable ergonomic layers. |
| Automatic vs caller-controlled retries | Automatic retries simplify use but can duplicate writes and hide latency; caller control is safer but inconsistent. | Retry only known-safe operations and expose policy controls. |
| Interactive vs machine-readable CLI output | Interactive output helps humans; machine output needs stable schemas and exit codes. | Keep stdout data stable and route diagnostics to stderr. |
| Credential file vs OS key store/workload identity | Files are portable but easy to leak; platform stores and workload identities reduce secret handling. | Prefer platform identity and secure stores, with explicit local-dev fallback. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

A call is `configure → authenticate → build → send → receive → decode → return|retry|cancel`; streaming adds open, incremental consume, backpressure, cancel, and close. Credentials and cached configuration have rotation/expiry lifecycles. CLI commands additionally map outcomes to stable exit codes and stdout/stderr.

```mermaid
stateDiagram-v2
    configured --> authenticated --> request_built --> sent --> response_received --> decoded --> returned
    sent --> retry_wait --> sent
    sent --> cancelled
    response_received --> stream_consuming --> closed
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Expose typed or clearly documented requests/responses, structured errors, idempotency controls, deadlines, page iteration, streaming cancellation, and version/user-agent metadata. Defaults must be finite and conservative. Machine-readable CLI output requires a versioned schema independent of decorative human text.

A production representation commonly needs the following fields or equivalent evidence:

- client/SDK/CLI version, runtime, and API compatibility target.
- base endpoint/environment and finite timeout/retry policy.
- credential reference/expiry without raw secret telemetry.
- idempotency/correlation/request metadata and pagination/stream state.
- structured server error and machine-output schema version.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **Authentication**
- **Configuration**
- **Base URL**
- **Retries**
- **Errors**
- **Versioning**
- **Streaming**
- **Telemetry**
- **User-agent metadata**

### 8.4. Timeouts

- **MUST — engineering rule:** Establish an end-to-end deadline, allocate smaller downstream budgets, propagate cancellation, and stop expensive or side-effecting work when the result is no longer useful unless explicitly designed otherwise.
- **Production failure mode:** Requests wait indefinitely, downstream work continues after callers leave, or nested timeouts exceed the original budget.
- **Existing-codebase evidence:** Inject slow dependencies at each hop and verify cancellation reaches database, network calls, streams, and workers.

### 8.6. Pagination

- **SHOULD — engineering rule:** Use a total deterministic order with a unique tie-breaker; encode cursor position and query shape opaquely; validate limits and preserve authorization/filter semantics across pages.
- **Production failure mode:** Concurrent inserts/updates cause duplicates or omissions, cursors are tampered with, or deep offsets exhaust the database.
- **Existing-codebase evidence:** Paginate while mutating boundary rows and verify every eligible record appears at most once under the documented consistency model.

### 8.8. Idempotency

- **MUST — engineering rule:** Scope keys to caller and operation, bind them to a canonical request fingerprint, reserve atomically, persist terminal outcome, and distinguish in-progress, succeeded, retryable-failed, and permanently-failed states.
- **Production failure mode:** Two concurrent requests both execute, or the same key is reused with different parameters and returns the wrong result.
- **Existing-codebase evidence:** Synchronize duplicate requests before first commit; test timeout-after-commit, key mismatch, expiry, and response replay.

### 8.11. Backward compatibility

- **SHOULD — engineering rule:** Define a compatibility window in which old and new readers/writers coexist. Make changes additive first, preserve unknown fields where required, and test both deployment orders.
- **Production failure mode:** A new writer emits data an old reader cannot parse, or rollback code cannot read records created during the failed release.
- **Existing-codebase evidence:** Run an N/N+1 matrix for requests, stored data, events, queues, caches, and rollback.

## 9. Concurrency, transactions, idempotency, and consistency

Automatic retries are safe only for operations known to be idempotent or supplied with an idempotency key. Pagination iterators must preserve cursors and stable order. Credential refresh must serialize or tolerate concurrent callers without producing invalid token races.

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

Expect DNS/connect/read timeout, partial response, malformed server data, rate limit, authentication expiry, lost response after commit, and server version skew. Preserve enough error detail for callers to decide while redacting secrets. Cancellation must release sockets and stream resources.

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

Emit opt-out or policy-compliant telemetry for SDK version, runtime, endpoint template, latency, retry count, and error class—not request bodies or credentials. Support diagnostic hooks and correlation IDs. Monitor incompatible client versions and deprecation usage server-side.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

Additive server fields and enum values must not break clients. Generated layers need reproducible versioning; hand-written ergonomics should preserve source/binary compatibility according to language norms. Coordinate deprecation with long-lived mobile, CLI, and embedded clients.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every SDK / Client Design path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Authentication`, `Timeouts`, `Errors`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by SDK / Client Design; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **SDK / Client Design** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Pagination**: Use a total deterministic order with a unique tie-breaker; encode cursor position and query shape opaquely; validate limits and preserve authorization/filter semantics across pages.
- **MUST** — For **Idempotency**: Scope keys to caller and operation, bind them to a canonical request fingerprint, reserve atomically, persist terminal outcome, and distinguish in-progress, succeeded, retryable-failed, and permanently-failed states.

### SHOULD

- **SHOULD** — Client defaults for timeout, retry, base URL, and authentication become system-wide behavior.
- **SHOULD** — SDKs must preserve server error semantics rather than collapsing everything into generic exceptions.
- **SHOULD** — Pagination, streaming, cancellation, and backpressure need first-class APIs.
- **SHOULD** — Telemetry and user-agent metadata must avoid sensitive data while enabling compatibility diagnosis.
- **SHOULD** — Long-lived and mobile clients make backward compatibility and deprecation windows operational requirements.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Adopt the **Generated vs hand-written SDK** option that fits the workload and ownership boundary; Generate low-level models/transports and handcraft stable ergonomic layers.
- **MAY** — Adopt the **Automatic vs caller-controlled retries** option that fits the workload and ownership boundary; Retry only known-safe operations and expose policy controls.
- **MAY** — Adopt the **Interactive vs machine-readable CLI output** option that fits the workload and ownership boundary; Keep stdout data stable and route diagnostics to stderr.

### AVOID

- **AVOID** — Infinite default timeout.
- **AVOID** — Retrying POST without idempotency.
- **AVOID** — Breaking scripts by changing CLI text.
- **AVOID** — Logging access tokens at debug level.
- **AVOID** — SDK unable to tolerate additive server fields.
- **AVOID** — Using infinite timeouts.
- **AVOID** — Automatically retrying every method.
- **AVOID** — Collapsing structured server errors.

### NEVER

- **NEVER** — Never retry every request automatically.
- **NEVER** — Never emit credentials or sensitive payloads through debug logs or telemetry.
- **NEVER** — Never change machine-readable CLI output without versioned compatibility.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Test every timeout/retry phase, cancellation, partial response, rate limit, authentication refresh, and ambiguous write outcome.
- [ ] Run client compatibility against additive fields/enums, old/new server versions, and unknown error details.
- [ ] Exercise concurrent token refresh, pagination resume, streaming backpressure/close, and resource cleanup.
- [ ] Verify stdout/stderr and exit codes for CLI automation; human formatting changes must not break machine mode.
- [ ] Scan debug logs, telemetry, error strings, and user-agent metadata for credentials and sensitive payloads.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Breaking CLI machine output.
- Logging authentication headers.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [111. CLI Backend Interaction](111-cli-backend-interaction.md)
- [116. Data Serialization](116-data-serialization.md)
- [014. API Design](014-api-design.md)
- [015. API Versioning & Compatibility](015-api-versioning-and-compatibility.md)
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.
- 071. Backward Compatibility — in the `migration-evolution` skill.
- 052. Retry Engineering — in the `resilience-flow-control` skill.
- [011. Request Lifecycle](011-request-lifecycle.md)
- [013. Error Architecture](013-error-architecture.md)
- 113. Machine-to-Machine Authentication — in the `auth-access` skill.
- 070. API / Event Schema Evolution — in the `migration-evolution` skill.
- 038. Rate Limiting — in the `resilience-flow-control` skill.

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s025"></a> **[S025] HTTP Semantics.** IETF; 2022; RFC 9110 / STD 97. [https://www.rfc-editor.org/rfc/rfc9110.html](https://www.rfc-editor.org/rfc/rfc9110.html) — Tags: http, api, methods, status-codes.
- <a id="s027"></a> **[S027] Problem Details for HTTP APIs.** IETF; 2023; RFC 9457. [https://www.rfc-editor.org/rfc/rfc9457.html](https://www.rfc-editor.org/rfc/rfc9457.html) — Tags: api, errors, http.
- <a id="s028"></a> **[S028] OpenAPI Specification.** OpenAPI Initiative; 2025; 3.2.0. [https://spec.openapis.org/oas/v3.2.0.html](https://spec.openapis.org/oas/v3.2.0.html) — Tags: api, schema, compatibility, documentation.
- <a id="s029"></a> **[S029] GraphQL Specification.** GraphQL Foundation; 2025; September 2025. [https://spec.graphql.org/September2025/](https://spec.graphql.org/September2025/) — Tags: graphql, api, schema, compatibility.
- <a id="s030"></a> **[S030] gRPC Guides.** Cloud Native Computing Foundation; 2026; Current documentation. [https://grpc.io/docs/guides/](https://grpc.io/docs/guides/) — Tags: grpc, rpc, retries, timeouts, streaming.
- <a id="s031"></a> **[S031] Protocol Buffers Programming Guides.** Google; 2026; Current documentation. [https://protobuf.dev/programming-guides/](https://protobuf.dev/programming-guides/) — Tags: protobuf, serialization, schema-evolution.
- <a id="s033"></a> **[S033] JSON Schema.** JSON Schema; 2022; Draft 2020-12. [https://json-schema.org/draft/2020-12](https://json-schema.org/draft/2020-12) — Tags: json, validation, schema.
- <a id="s055"></a> **[S055] Timeouts, Retries, and Backoff with Jitter.** AWS Builders' Library; 2026; Current article. [https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) — Tags: retries, timeouts, jitter, resilience.
- <a id="s114"></a> **[S114] Google API Improvement Proposals.** Google; 2026; Current. [https://google.aip.dev/](https://google.aip.dev/) — Tags: api, pagination, versioning, resource-design.
- <a id="s115"></a> **[S115] Microsoft REST API Guidelines.** Microsoft; 2026; Current. [https://github.com/microsoft/api-guidelines](https://github.com/microsoft/api-guidelines) — Tags: api, compatibility, pagination.
- <a id="s026"></a> **[S026] HTTP Caching.** IETF; 2022; RFC 9111. [https://www.rfc-editor.org/rfc/rfc9111.html](https://www.rfc-editor.org/rfc/rfc9111.html) — Tags: http, caching, api.
- <a id="s032"></a> **[S032] AsyncAPI Specification.** AsyncAPI Initiative; 2026; 3.1.0. [https://www.asyncapi.com/docs/reference/specification/v3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0) — Tags: events, messaging, schema, api.
- <a id="s021"></a> **[S021] Application Security Verification Standard.** OWASP; 2025; ASVS 5.0.0. [https://owasp.org/www-project-application-security-verification-standard/](https://owasp.org/www-project-application-security-verification-standard/) — Tags: security, authentication, authorization, validation, logging.
- <a id="s023"></a> **[S023] OWASP API Security Top 10.** OWASP; 2023; 2023. [https://owasp.org/API-Security/editions/2023/en/0x11-t10/](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) — Tags: api, security, authorization, abuse.
