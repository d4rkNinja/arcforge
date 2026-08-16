# 144. Untrusted Code Execution

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Untrusted Code Execution** exists to operate probabilistic model and agent capabilities within deterministic budgets, permissions, data boundaries, and recovery mechanisms. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

The deterministic application owns permissions, budgets, validation, side effects, and durable state; the model proposes text or actions. Treat prompts, retrieved context, tool output, and model output as untrusted data crossing distinct trust boundaries. Provider fallback must not silently change data residency, capability, or safety policy.

The most important evidence base for this paper includes [S103](#s103) [S104](#s104) [S105](#s105) [S106](#s106). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Model output is untrusted input even when structured-output features are enabled.
- Provider requests are network calls with rate limits, changing model behavior, ambiguous timeouts, and cost side effects.
- Prompts, tools, retrieval indexes, model versions, and policy are independently versioned dependencies.
- Agent loops need hard limits on time, steps, cost, tool scope, and side effects.
- Memory and RAG must enforce the same authorization, deletion, provenance, and tenant boundaries as the source data.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Untrusted Code Execution** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- Which decisions and tool effects remain deterministic and authorized outside the model?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Untrusted Code Execution**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Inventory provider/model/prompt/tool/index versions, data routes, permissions, budgets, and replay metadata.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S103](#s103) [S104](#s104) [S105](#s105) [S106](#s106)

1. **Invariant 1:** Model output is untrusted input even when structured-output features are enabled.
2. **Invariant 2:** Provider requests are network calls with rate limits, changing model behavior, ambiguous timeouts, and cost side effects.
3. **Invariant 3:** Prompts, tools, retrieval indexes, model versions, and policy are independently versioned dependencies.
4. **Invariant 4:** Agent loops need hard limits on time, steps, cost, tool scope, and side effects.
5. **Invariant 5:** Memory and RAG must enforce the same authorization, deletion, provenance, and tenant boundaries as the source data.

Additional topic-specific invariants:

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Container isolation vs microVM/sandbox runtime | Containers are lightweight but share a kernel; microVMs or specialized sandboxes increase isolation with startup and operations cost. | Match boundary strength to adversarial risk and layer network, filesystem, syscall, secret, and resource controls. |
| Single provider vs routing/fallback | A single provider simplifies behavior; routing improves resilience/cost but introduces semantic drift and data-governance differences. | Use capability-based routing with conformance tests and explicit fallback limits. |
| Synchronous vs streaming generation | Streaming improves perceived latency but commits partial output and complicates moderation, cancellation, and retries. | Treat streamed output as provisional and define interruption semantics. |
| Free-form vs structured output | Structured output improves parsing but does not guarantee semantic validity. | Validate against schema and domain invariants and reject unknown/unsafe actions. |
| Embedded agent vs isolated executor | Embedded execution is simple but shares secrets and privileges; isolation limits blast radius at operational cost. | Isolate untrusted code and high-impact tools with least privilege and approval gates. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

An invocation is `admit → authorize/budget → build versioned context → call/stream → validate output → execute approved tools → persist result → audit`, with loops bounded by steps, time, tokens, and cost. Memory, embeddings, indexes, prompts, and tool grants each have version, expiry, and deletion states.

```mermaid
stateDiagram-v2
    admitted --> policy_and_budget --> context_built --> model_call --> output_validated --> tool_or_result --> persisted --> audited
    model_call --> retry_or_fallback
    output_validated --> rejected
    tool_or_result --> approval_required --> tool_or_result
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Record model/provider/version, prompt/template version, tool schema/version, sampling/configuration, context provenance, output schema, safety decision, budget, and trace identifiers. Structured output reduces parsing ambiguity but remains semantically untrusted. Tool calls require independent authorization and idempotency.

A production representation commonly needs the following fields or equivalent evidence:

- provider/model/version, routing policy, prompt/template and tool schema versions.
- input/context provenance, tenant/subject permissions, retrieval/index versions.
- execution/run/step/tool IDs, budgets, approvals, and idempotency state.
- validated structured result, safety decision, and side-effect references.
- token/cost/latency accounting, memory retention/deletion linkage, and audit context.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **Containers**
- **Disk limits**
- **Cleanup**

### 8.1. Process isolation

- **MUST — engineering rule:** Select isolation by anomaly analysis, not name familiarity. Account for database-specific semantics and retry complete transactions on serialization failure.
- **Production failure mode:** Lost updates, write skew, or phantoms violate invariants despite all statements being inside a transaction.
- **Existing-codebase evidence:** Construct concurrent schedules that would violate the invariant and verify the chosen isolation/locking rejects one participant.

### 8.3. Sandboxing

- **SHOULD — engineering rule:** Assume code is hostile: combine a strong isolation boundary with least-privilege filesystem/network/secret access, syscall/device restrictions, cgroup quotas, wall-clock kill, ephemeral state, and post-run cleanup.
- **Production failure mode:** Container escape, metadata-service access, fork bomb, disk fill, or secret inheritance compromises the host or other tenants.
- **Existing-codebase evidence:** Run adversarial workloads for escape, network exfiltration, resource exhaustion, persistence, signal handling, and cleanup.

### 8.4. Network isolation

- **MUST — engineering rule:** Select isolation by anomaly analysis, not name familiarity. Account for database-specific semantics and retry complete transactions on serialization failure.
- **Production failure mode:** Lost updates, write skew, or phantoms violate invariants despite all statements being inside a transaction.
- **Existing-codebase evidence:** Construct concurrent schedules that would violate the invariant and verify the chosen isolation/locking rejects one participant.

### 8.5. Filesystem isolation

- **MUST — engineering rule:** Select isolation by anomaly analysis, not name familiarity. Account for database-specific semantics and retry complete transactions on serialization failure.
- **Production failure mode:** Lost updates, write skew, or phantoms violate invariants despite all statements being inside a transaction.
- **Existing-codebase evidence:** Construct concurrent schedules that would violate the invariant and verify the chosen isolation/locking rejects one participant.

### 8.6. CPU limits

- **SHOULD — engineering rule:** Measure under representative load before changing code; correlate profiles with request classes, queueing, GC pauses, I/O, and tail latency. Preserve correctness and observability while optimizing.
- **Production failure mode:** A micro-optimization shifts pressure to memory, database, or network and worsens production tails.
- **Existing-codebase evidence:** Capture before/after profiles and end-to-end metrics with equivalent workloads and statistical confidence.

### 8.7. Memory limits

- **SHOULD — engineering rule:** Measure under representative load before changing code; correlate profiles with request classes, queueing, GC pauses, I/O, and tail latency. Preserve correctness and observability while optimizing.
- **Production failure mode:** A micro-optimization shifts pressure to memory, database, or network and worsens production tails.
- **Existing-codebase evidence:** Capture before/after profiles and end-to-end metrics with equivalent workloads and statistical confidence.

### 8.9. Timeouts

- **MUST — engineering rule:** Establish an end-to-end deadline, allocate smaller downstream budgets, propagate cancellation, and stop expensive or side-effecting work when the result is no longer useful unless explicitly designed otherwise.
- **Production failure mode:** Requests wait indefinitely, downstream work continues after callers leave, or nested timeouts exceed the original budget.
- **Existing-codebase evidence:** Inject slow dependencies at each hop and verify cancellation reaches database, network calls, streams, and workers.

### 8.10. Syscall restrictions

- **SHOULD — engineering rule:** Assume code is hostile: combine a strong isolation boundary with least-privilege filesystem/network/secret access, syscall/device restrictions, cgroup quotas, wall-clock kill, ephemeral state, and post-run cleanup.
- **Production failure mode:** Container escape, metadata-service access, fork bomb, disk fill, or secret inheritance compromises the host or other tenants.
- **Existing-codebase evidence:** Run adversarial workloads for escape, network exfiltration, resource exhaustion, persistence, signal handling, and cleanup.

### 8.11. Secret isolation

- **MUST — engineering rule:** Select isolation by anomaly analysis, not name familiarity. Account for database-specific semantics and retry complete transactions on serialization failure.
- **Production failure mode:** Lost updates, write skew, or phantoms violate invariants despite all statements being inside a transaction.
- **Existing-codebase evidence:** Construct concurrent schedules that would violate the invariant and verify the chosen isolation/locking rejects one participant.

## 9. Concurrency, transactions, idempotency, and consistency

A timed-out generation or tool call may still complete and incur cost/effects. Agent retries can duplicate actions. Persist execution state and idempotency before irreversible tools. RAG and memory must apply current tenant/resource permissions at ingestion and retrieval, and propagate deletions to derived indexes.

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

Plan for rate limits, model deprecation, context overflow, malformed structured output, provider semantic drift, prompt injection, retrieval poisoning, tool timeout, loop nontermination, and partial streamed output. Fallback only when the alternate model satisfies the same contract or explicitly downgrade behavior.

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

Measure requests, tokens, cost, latency to first/last token, rate-limit/retry, provider/model mix, schema-validation failures, tool calls/effects, loop steps, retrieval quality proxies, safety blocks, and budget exhaustion. Logs must redact prompts/context according to data classification and consent.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

Prompts, models, embeddings, chunkers, tools, and policies are independently versioned. Evaluate and canary changes on representative cases, preserve replay metadata, and support rollback. Reindexing or memory-policy changes require dual-version handling, deletion reconciliation, and compatibility with in-flight agent runs.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Untrusted Code Execution path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Process isolation`, `Network isolation`, `Memory limits`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Treat prompt, retrieval, model output, and tool output as untrusted. Re-authorize tools deterministically, enforce sandbox/data boundaries, and cap steps, time, tokens, and cost. |
| Privacy / retention | Classify data produced or touched by Untrusted Code Execution; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Untrusted Code Execution** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Process isolation**: Select isolation by anomaly analysis, not name familiarity. Account for database-specific semantics and retry complete transactions on serialization failure.
- **MUST** — For **Sandboxing**: Assume code is hostile: combine a strong isolation boundary with least-privilege filesystem/network/secret access, syscall/device restrictions, cgroup quotas, wall-clock kill, ephemeral state, and post-run cleanup.

### SHOULD

- **SHOULD** — Model output is untrusted input even when structured-output features are enabled.
- **SHOULD** — Provider requests are network calls with rate limits, changing model behavior, ambiguous timeouts, and cost side effects.
- **SHOULD** — Prompts, tools, retrieval indexes, model versions, and policy are independently versioned dependencies.
- **SHOULD** — Agent loops need hard limits on time, steps, cost, tool scope, and side effects.
- **SHOULD** — Memory and RAG must enforce the same authorization, deletion, provenance, and tenant boundaries as the source data.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Choose **Container isolation vs microVM/sandbox runtime** according to the stated trade-off: Match boundary strength to adversarial risk and layer network, filesystem, syscall, secret, and resource controls.
- **MAY** — Adopt the **Single provider vs routing/fallback** option that fits the workload and ownership boundary; Use capability-based routing with conformance tests and explicit fallback limits.
- **MAY** — Adopt the **Synchronous vs streaming generation** option that fits the workload and ownership boundary; Treat streamed output as provisional and define interruption semantics.
- **MAY** — Adopt the **Free-form vs structured output** option that fits the workload and ownership boundary; Validate against schema and domain invariants and reject unknown/unsafe actions.

### AVOID

- **AVOID** — Tool call executed twice after retry.
- **AVOID** — Prompt injection exfiltrating retrieved secrets.
- **AVOID** — Cross-tenant vector search.
- **AVOID** — Fallback model violating context or output contract.
- **AVOID** — Agent loop consuming unbounded cost.
- **AVOID** — Trusting structured model output without domain validation.
- **AVOID** — Letting the model authorize tools.
- **AVOID** — Retrying agent/tool loops without durable execution state.

### NEVER

- **NEVER** — Never treat model output as trusted instructions or authorization.
- **NEVER** — Never expose high-impact tools with ambient application privileges.
- **NEVER** — Never persist memory or embeddings outside source-data permission, deletion, and residency rules.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Replay representative and adversarial prompts against pinned model/prompt/tool versions; validate semantic invariants beyond JSON schema.
- [ ] Inject prompt injection and poisoned retrieval content; tools and data access must remain independently authorized.
- [ ] Timeout and retry before/after model response and every tool side effect; verify execution-state idempotency and cost accounting.
- [ ] Run provider fallback, model deprecation, context overflow, rate limits, malformed streaming, and tool failure.
- [ ] Test cross-tenant memory/RAG, deletion propagation, provenance, permission changes, and reindexing under mixed versions.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Retrieving across tenant/permission boundaries.
- Falling back to a model with incompatible safety/context semantics.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [145. Plugin / Extension Architecture](145-plugin-extension-architecture.md)
- [141. Agent Execution](141-agent-execution.md)
- 062. Web/API Security — in the `security-privacy` skill.
- 109. Resource Management — in the `quality-release` skill.
- 108. Infrastructure Configuration — in the `runtime-delivery` skill.
- [142. AI Memory](142-ai-memory.md)
- [140. AI/LLM Backend Fundamentals](140-ai-llm-backend-fundamentals.md)
- [143. RAG Infrastructure](143-rag-infrastructure.md)
- 095. Performance Engineering — in the `quality-release` skill.
- 011. Request Lifecycle — in the `api-contracts` skill.
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.
- 120. Deduplication — in the `async-messaging` skill.

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s033"></a> **[S033] JSON Schema.** JSON Schema; 2022; Draft 2020-12. [https://json-schema.org/draft/2020-12](https://json-schema.org/draft/2020-12) — Tags: json, validation, schema.
- <a id="s066"></a> **[S066] OpenTelemetry Specification.** Cloud Native Computing Foundation; 2026; 1.59.0. [https://opentelemetry.io/docs/specs/otel/](https://opentelemetry.io/docs/specs/otel/) — Tags: observability, tracing, metrics, logs.
- <a id="s081"></a> **[S081] Privacy Framework.** NIST; 2020; 1.0. [https://www.nist.gov/privacy-framework](https://www.nist.gov/privacy-framework) — Tags: privacy, pii, risk.
- <a id="s082"></a> **[S082] General Data Protection Regulation.** European Union; 2016; Regulation (EU) 2016/679. [https://eur-lex.europa.eu/eli/reg/2016/679/oj](https://eur-lex.europa.eu/eli/reg/2016/679/oj) — Tags: privacy, retention, deletion, consent.
- <a id="s103"></a> **[S103] AI Risk Management Framework.** NIST; 2023; AI RMF 1.0. [https://www.nist.gov/itl/ai-risk-management-framework](https://www.nist.gov/itl/ai-risk-management-framework) — Tags: ai, risk, governance.
- <a id="s104"></a> **[S104] Artificial Intelligence Risk Management Framework: Generative AI Profile.** NIST; 2024; NIST AI 600-1. [https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) — Tags: ai, generative-ai, risk.
- <a id="s105"></a> **[S105] OWASP GenAI Security Project.** OWASP; 2026; Current. [https://genai.owasp.org/](https://genai.owasp.org/) — Tags: ai, llm, security, agents.
- <a id="s106"></a> **[S106] Model Context Protocol Specification.** Model Context Protocol; 2026; Current. [https://modelcontextprotocol.io/specification/](https://modelcontextprotocol.io/specification/) — Tags: agents, tools, plugins, protocol.
- <a id="s107"></a> **[S107] Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.** Meta AI / NeurIPS; 2020; NeurIPS 2020. [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401) — Tags: rag, retrieval, ai.
- <a id="s108"></a> **[S108] gVisor Documentation.** Google; 2026; Current. [https://gvisor.dev/docs/](https://gvisor.dev/docs/) — Tags: sandboxing, untrusted-code, containers.
- <a id="s109"></a> **[S109] Firecracker Documentation.** AWS; 2026; Current. [https://firecracker-microvm.github.io/](https://firecracker-microvm.github.io/) — Tags: sandboxing, microvm, untrusted-code.
- <a id="s110"></a> **[S110] Linux seccomp(2) Manual.** Linux man-pages project; 2026; Current. [https://man7.org/linux/man-pages/man2/seccomp.2.html](https://man7.org/linux/man-pages/man2/seccomp.2.html) — Tags: sandboxing, syscalls, security.
- <a id="s111"></a> **[S111] WebAssembly System Interface.** Bytecode Alliance; 2026; Current. [https://wasi.dev/](https://wasi.dev/) — Tags: plugins, sandboxing, extensions.
- <a id="s133"></a> **[S133] OpenAI API Documentation.** OpenAI; 2026; Current. [https://platform.openai.com/docs/](https://platform.openai.com/docs/) — Tags: ai, llm, streaming, tools, structured-output.
- <a id="s134"></a> **[S134] Anthropic API Documentation.** Anthropic; 2026; Current. [https://docs.anthropic.com/](https://docs.anthropic.com/) — Tags: ai, llm, streaming, tools.
- <a id="s072"></a> **[S072] Open Container Initiative Runtime Specification.** Open Container Initiative; 2026; Current. [https://github.com/opencontainers/runtime-spec](https://github.com/opencontainers/runtime-spec) — Tags: containers, runtime, isolation.
