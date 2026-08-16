---
paper_number: 141
title: "Agent Execution"
layer: systems
domain_profile: ai
corpus_version: 1.0.0
verified_through: 2026-08-17
canonical_source: "original/Pasted text.txt"
subtopic_count: 14
status: production-engineering-reference
---

# 141. Agent Execution

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Agent Execution** exists to operate probabilistic model and agent capabilities within deterministic budgets, permissions, data boundaries, and recovery mechanisms. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

The deterministic application owns permissions, budgets, validation, side effects, and durable state; the model proposes text or actions. Treat prompts, retrieved context, tool output, and model output as untrusted data crossing distinct trust boundaries. Provider fallback must not silently change data residency, capability, or safety policy.

The most important evidence base for this paper includes [S103](#s103) [S104](#s104) [S105](#s105) [S106](#s106). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Model output is untrusted input even when structured-output features are enabled.
- Provider requests are network calls with rate limits, changing model behavior, ambiguous timeouts, and cost side effects.
- Prompts, tools, retrieval indexes, model versions, and policy are independently versioned dependencies.
- Agent loops need hard limits on time, steps, cost, tool scope, and side effects.
- Memory and RAG must enforce the same authorization, deletion, provenance, and tenant boundaries as the source data.

## 2. Scope and terminology map

The canonical topic list requires this paper to cover the following concerns. They are grouped only to expose relationships; no listed subtopic is omitted.

### Identity, trust, and access

**Tool permissions**.

### State and lifecycle

**Agent state**, **State persistence**.

### Concurrency and distributed behavior

**Idempotency**.

### Security, privacy, and abuse

**Execution loops**, **Maximum iterations**, **Termination**, **Retries**, **Tool failures**, **Human approval**, **Sandboxing**, **Time budgets**, **Context limits**.

### Operations and observability

**Cost budgets**.

### Boundary of the paper

This paper treats **Agent Execution** as a production subsystem or reusable reasoning primitive. It covers semantics, ownership, persistence, APIs, security, concurrency, distributed behavior, operations, evolution, and verification. Framework syntax and large implementation listings are intentionally excluded.

## 3. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S103](#s103) [S104](#s104) [S105](#s105) [S106](#s106)

1. **Invariant 1:** Model output is untrusted input even when structured-output features are enabled.
2. **Invariant 2:** Provider requests are network calls with rate limits, changing model behavior, ambiguous timeouts, and cost side effects.
3. **Invariant 3:** Prompts, tools, retrieval indexes, model versions, and policy are independently versioned dependencies.
4. **Invariant 4:** Agent loops need hard limits on time, steps, cost, tool scope, and side effects.
5. **Invariant 5:** Memory and RAG must enforce the same authorization, deletion, provenance, and tenant boundaries as the source data.

Additional topic-specific invariants:

- **SHOULD — Agent state:** Persist an explicit execution state machine with step IDs, budgets, tool results, approvals, and terminal reasons. Make each side-effecting step idempotent and resumable after crash.
- **SHOULD — Maximum iterations:** Persist an explicit execution state machine with step IDs, budgets, tool results, approvals, and terminal reasons. Make each side-effecting step idempotent and resumable after crash.
- **SHOULD — Retries:** Define the exact semantics of **Retries** within Agent Execution: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Sandboxing:** Assume code is hostile: combine a strong isolation boundary with least-privilege filesystem/network/secret access, syscall/device restrictions, cgroup quotas, wall-clock kill, ephemeral state, and post-run cleanup.
- **SHOULD — Time budgets:** Define the exact semantics of **Time budgets** within Agent Execution: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST — Idempotency:** Scope keys to caller and operation, bind them to a canonical request fingerprint, reserve atomically, persist terminal outcome, and distinguish in-progress, succeeded, retryable-failed, and permanently-failed states.

## 4. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Single provider vs routing/fallback | A single provider simplifies behavior; routing improves resilience/cost but introduces semantic drift and data-governance differences. | Use capability-based routing with conformance tests and explicit fallback limits. |
| Synchronous vs streaming generation | Streaming improves perceived latency but commits partial output and complicates moderation, cancellation, and retries. | Treat streamed output as provisional and define interruption semantics. |
| Free-form vs structured output | Structured output improves parsing but does not guarantee semantic validity. | Validate against schema and domain invariants and reject unknown/unsafe actions. |
| Embedded agent vs isolated executor | Embedded execution is simple but shares secrets and privileges; isolation limits blast radius at operational cost. | Isolate untrusted code and high-impact tools with least privilege and approval gates. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 5. Ownership, state, and lifecycle

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

## 6. Data model and API implications

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

## 7. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### 7.1. Agent state

- **SHOULD — engineering rule:** Persist an explicit execution state machine with step IDs, budgets, tool results, approvals, and terminal reasons. Make each side-effecting step idempotent and resumable after crash.
- **Production failure mode:** The agent loops indefinitely, repeats a tool after retry, resumes with stale permissions, or bypasses an approval gate.
- **Existing-codebase evidence:** Crash/restart before and after every tool call and approval; verify limits and exactly one logical side effect.

### 7.2. Tool permissions

- **MUST — engineering rule:** Define authorization as `(principal, action, resource, context) -> decision + reason + policy version`. Enforce at the owning boundary and include tenant/resource state, not only route-level roles.
- **Production failure mode:** An authenticated caller accesses another object, hidden field, or state transition because lookup and authorization are separated or policy inputs are incomplete.
- **Existing-codebase evidence:** Trace each read/write from externally supplied identifier to the final query/serializer and verify denial before data exposure or mutation.

### 7.3. Execution loops

- **SHOULD — engineering rule:** Persist an explicit execution state machine with step IDs, budgets, tool results, approvals, and terminal reasons. Make each side-effecting step idempotent and resumable after crash.
- **Production failure mode:** The agent loops indefinitely, repeats a tool after retry, resumes with stale permissions, or bypasses an approval gate.
- **Existing-codebase evidence:** Crash/restart before and after every tool call and approval; verify limits and exactly one logical side effect.

### 7.4. Maximum iterations

- **SHOULD — engineering rule:** Persist an explicit execution state machine with step IDs, budgets, tool results, approvals, and terminal reasons. Make each side-effecting step idempotent and resumable after crash.
- **Production failure mode:** The agent loops indefinitely, repeats a tool after retry, resumes with stale permissions, or bypasses an approval gate.
- **Existing-codebase evidence:** Crash/restart before and after every tool call and approval; verify limits and exactly one logical side effect.

### 7.5. Termination

- **SHOULD — engineering rule:** Persist an explicit execution state machine with step IDs, budgets, tool results, approvals, and terminal reasons. Make each side-effecting step idempotent and resumable after crash.
- **Production failure mode:** The agent loops indefinitely, repeats a tool after retry, resumes with stale permissions, or bypasses an approval gate.
- **Existing-codebase evidence:** Crash/restart before and after every tool call and approval; verify limits and exactly one logical side effect.

### 7.6. Retries

- **SHOULD — engineering rule:** Define the exact semantics of **Retries** within Agent Execution: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for retries is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for retries, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.7. Tool failures

- **SHOULD — engineering rule:** Define the exact semantics of **Tool failures** within Agent Execution: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for tool failures is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for tool failures, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.8. Human approval

- **SHOULD — engineering rule:** Persist an explicit execution state machine with step IDs, budgets, tool results, approvals, and terminal reasons. Make each side-effecting step idempotent and resumable after crash.
- **Production failure mode:** The agent loops indefinitely, repeats a tool after retry, resumes with stale permissions, or bypasses an approval gate.
- **Existing-codebase evidence:** Crash/restart before and after every tool call and approval; verify limits and exactly one logical side effect.

### 7.9. Sandboxing

- **SHOULD — engineering rule:** Assume code is hostile: combine a strong isolation boundary with least-privilege filesystem/network/secret access, syscall/device restrictions, cgroup quotas, wall-clock kill, ephemeral state, and post-run cleanup.
- **Production failure mode:** Container escape, metadata-service access, fork bomb, disk fill, or secret inheritance compromises the host or other tenants.
- **Existing-codebase evidence:** Run adversarial workloads for escape, network exfiltration, resource exhaustion, persistence, signal handling, and cleanup.

### 7.10. Cost budgets

- **SHOULD — engineering rule:** Estimate and record input/output/cache/tool usage per request and tenant, reserve budget before execution, cap context/iterations/output, and reconcile provider-reported usage.
- **Production failure mode:** Large retrieved context or loops create unbounded spend and latency, while provider rounding/retries make local estimates drift.
- **Existing-codebase evidence:** Test oversized inputs, fallback providers, streaming cancellation, retries, and reconciliation against billing records.

### 7.11. Time budgets

- **SHOULD — engineering rule:** Define the exact semantics of **Time budgets** within Agent Execution: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for time budgets is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for time budgets, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.12. Context limits

- **SHOULD — engineering rule:** Estimate and record input/output/cache/tool usage per request and tenant, reserve budget before execution, cap context/iterations/output, and reconcile provider-reported usage.
- **Production failure mode:** Large retrieved context or loops create unbounded spend and latency, while provider rounding/retries make local estimates drift.
- **Existing-codebase evidence:** Test oversized inputs, fallback providers, streaming cancellation, retries, and reconciliation against billing records.

### 7.13. State persistence

- **SHOULD — engineering rule:** Define the exact semantics of **State persistence** within Agent Execution: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **Production failure mode:** A framework or provider default for state persistence is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Existing-codebase evidence:** Locate every implementation path for state persistence, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.

### 7.14. Idempotency

- **MUST — engineering rule:** Scope keys to caller and operation, bind them to a canonical request fingerprint, reserve atomically, persist terminal outcome, and distinguish in-progress, succeeded, retryable-failed, and permanently-failed states.
- **Production failure mode:** Two concurrent requests both execute, or the same key is reused with different parameters and returns the wrong result.
- **Existing-codebase evidence:** Synchronize duplicate requests before first commit; test timeout-after-commit, key mismatch, expiry, and response replay.

## 8. Concurrency, transactions, idempotency, and consistency

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

## 9. Security, authorization, privacy, and abuse resistance

Map trust boundaries, assets, attackers, privileges, data flows, and failure modes before selecting controls. Enforce least privilege in the component that owns the resource; edge filtering, WAFs, and gateways are supplementary. Treat every external, model-generated, cached, imported, or administrator-supplied value as untrusted at its use context.

- **MUST** authenticate the actual caller or workload and re-authorize the final action against authoritative tenant, ownership, resource state, and policy context.
- **MUST** reject mass assignment and unknown privileged fields; server-controlled identity, role, tenant, status, price, owner, and audit fields cannot come from an untrusted DTO.
- **MUST** classify and minimize sensitive data; redact logs/traces/errors, restrict exports and support tooling, propagate deletion, and account for backups and derived indexes.
- **SHOULD** combine rate limits with resource budgets, concurrency caps, payload/complexity limits, and detection. IP-only limiting is not an identity or abuse strategy.
- **AVOID** fail-open behavior for high-impact actions when policy, key, revocation, or tenant context is unavailable.

## 10. Distributed failure, retries, timeouts, and recovery

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

## 11. Persistence, constraints, indexes, and caching

- Put race-sensitive invariants in the database or authoritative store. Application checks remain useful for error quality but are not the final guard.
- Design indexes from real query predicates, tenant scope, ordering, soft-delete conditions, and production cardinality. Verify plans and write amplification.
- Keep transactions bounded in time and rows; avoid network/provider calls while locks are held.
- Treat caches, search indexes, analytics, and replicas as derived unless explicitly authoritative. Version them and provide rebuild/reconciliation.
- Retention and cleanup must include references, uniqueness, tombstones, legal hold, audit, external copies, and interrupted-job recovery.

## 12. Observability, audit, and operational control

Measure requests, tokens, cost, latency to first/last token, rate-limit/retry, provider/model mix, schema-validation failures, tool calls/effects, loop steps, retrieval quality proxies, safety blocks, and budget exhaustion. Logs must redact prompts/context according to data classification and consent.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 13. Compatibility, schema evolution, migration, deployment, and rollback

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

## 14. Cross-cutting implementation matrix

| Concern | Required production decision |
|---|---|
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Agent Execution path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Agent state`, `Maximum iterations`, `Tool failures`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Treat prompt, retrieval, model output, and tool output as untrusted. Re-authorize tools deterministically, enforce sandbox/data boundaries, and cap steps, time, tokens, and cost. |
| Privacy / retention | Classify data produced or touched by Agent Execution; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 15. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Agent Execution** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Agent state**: Persist an explicit execution state machine with step IDs, budgets, tool results, approvals, and terminal reasons. Make each side-effecting step idempotent and resumable after crash.
- **MUST** — For **Maximum iterations**: Persist an explicit execution state machine with step IDs, budgets, tool results, approvals, and terminal reasons. Make each side-effecting step idempotent and resumable after crash.
- **MUST** — For **Retries**: Define the exact semantics of **Retries** within Agent Execution: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
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

## 16. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Replay representative and adversarial prompts against pinned model/prompt/tool versions; validate semantic invariants beyond JSON schema.
- [ ] Inject prompt injection and poisoned retrieval content; tools and data access must remain independently authorized.
- [ ] Timeout and retry before/after model response and every tool side effect; verify execution-state idempotency and cost accounting.
- [ ] Run provider fallback, model deprecation, context overflow, rate limits, malformed streaming, and tool failure.
- [ ] Test cross-tenant memory/RAG, deletion propagation, provenance, permission changes, and reindexing under mixed versions.
- [ ] **Agent state:** Crash/restart before and after every tool call and approval; verify limits and exactly one logical side effect.
- [ ] **Maximum iterations:** Crash/restart before and after every tool call and approval; verify limits and exactly one logical side effect.
- [ ] **Retries:** Locate every implementation path for retries, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Sandboxing:** Run adversarial workloads for escape, network exfiltration, resource exhaustion, persistence, signal handling, and cleanup.
- [ ] **Time budgets:** Locate every implementation path for time budgets, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Idempotency:** Synchronize duplicate requests before first commit; test timeout-after-commit, key mismatch, expiry, and response replay.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 17. Common production bugs and incorrect implementations

- Tool call executed twice after retry.
- Prompt injection exfiltrating retrieved secrets.
- Cross-tenant vector search.
- Fallback model violating context or output contract.
- Agent loop consuming unbounded cost.
- **Agent state:** The agent loops indefinitely, repeats a tool after retry, resumes with stale permissions, or bypasses an approval gate.
- **Execution loops:** The agent loops indefinitely, repeats a tool after retry, resumes with stale permissions, or bypasses an approval gate.
- **Termination:** The agent loops indefinitely, repeats a tool after retry, resumes with stale permissions, or bypasses an approval gate.
- **Tool failures:** A framework or provider default for tool failures is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Cost budgets:** Large retrieved context or loops create unbounded spend and latency, while provider rounding/retries make local estimates drift.
- **Context limits:** Large retrieved context or loops create unbounded spend and latency, while provider rounding/retries make local estimates drift.
- **Idempotency:** Two concurrent requests both execute, or the same key is reused with different parameters and returns the wrong result.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Trusting structured model output without domain validation.
- Letting the model authorize tools.
- Retrying agent/tool loops without durable execution state.
- Retrieving across tenant/permission boundaries.
- Falling back to a model with incompatible safety/context semantics.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Agent Execution** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- For **Agent state**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: The agent loops indefinitely, repeats a tool after retry, resumes with stale permissions, or bypasses an approval gate.
- For **Maximum iterations**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: The agent loops indefinitely, repeats a tool after retry, resumes with stale permissions, or bypasses an approval gate.
- For **Retries**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for retries is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Sandboxing**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Container escape, metadata-service access, fork bomb, disk fill, or secret inheritance compromises the host or other tenants.
- For **Time budgets**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for time budgets is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- Which decisions and tool effects remain deterministic and authorized outside the model?

## 20. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Agent Execution**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] **Agent state:** Crash/restart before and after every tool call and approval; verify limits and exactly one logical side effect.
- [ ] **Execution loops:** Crash/restart before and after every tool call and approval; verify limits and exactly one logical side effect.
- [ ] **Termination:** Crash/restart before and after every tool call and approval; verify limits and exactly one logical side effect.
- [ ] **Tool failures:** Locate every implementation path for tool failures, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Cost budgets:** Test oversized inputs, fallback providers, streaming cancellation, retries, and reconciliation against billing records.
- [ ] **Context limits:** Test oversized inputs, fallback providers, streaming cancellation, retries, and reconciliation against billing records.
- [ ] **Idempotency:** Synchronize duplicate requests before first commit; test timeout-after-commit, key mismatch, expiry, and response replay.
- [ ] Inventory provider/model/prompt/tool/index versions, data routes, permissions, budgets, and replay metadata.

## 21. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [140. AI/LLM Backend Fundamentals](140-ai-llm-backend-fundamentals.md) — layer: `systems`; profile: `ai`.
- [144. Untrusted Code Execution](144-untrusted-code-execution.md) — layer: `systems`; profile: `ai`.
- [145. Plugin / Extension Architecture](145-plugin-extension-architecture.md) — layer: `systems`; profile: `ai`.
- [142. AI Memory](142-ai-memory.md) — layer: `systems`; profile: `ai`.
- [143. RAG Infrastructure](143-rag-infrastructure.md) — layer: `systems`; profile: `ai`.
- [146. Cross-Cutting Implementation Checklist](../cross-cutting/146-cross-cutting-implementation-checklist.md) — layer: `cross-cutting`; profile: `checklist`.
- [052. Retry Engineering](../primitives/052-retry-engineering.md) — layer: `primitives`; profile: `resilience`.
- [011. Request Lifecycle](../primitives/011-request-lifecycle.md) — layer: `primitives`; profile: `api`.
- [051. External Integrations](051-external-integrations.md) — layer: `systems`; profile: `resilience`.
- [012. Input Validation](../primitives/012-input-validation.md) — layer: `primitives`; profile: `api`.
- [053. Timeout Engineering](../primitives/053-timeout-engineering.md) — layer: `primitives`; profile: `resilience`.
- [120. Deduplication](../primitives/120-deduplication.md) — layer: `primitives`; profile: `async`.

## 22. Sources and further research

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

---

**Paper metadata:** canonical subtopics: 14; layer: `systems`; domain profile: `ai`; verified through: `2026-08-17`.
