---
paper_number: 107
title: "CI/CD"
layer: cross-cutting
domain_profile: runtime
corpus_version: 1.0.0
verified_through: 2026-08-17
canonical_source: "original/Pasted text.txt"
subtopic_count: 12
status: production-engineering-reference
---

# 107. CI/CD

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**CI/CD** exists so every change reaches production through one auditable, gated path. A basic setup builds and deploys ad hoc; a production pipeline is deterministic by construction: one immutable artifact per commit, promoted environment to environment through ordered stages — build, unit, integration, security scans, artifact packaging, deploy-to-dev, e2e/smoke, promotion gates — where each stage defines its failure semantics and no partial artifact is ever promoted.

Provenance is the spine: SBOMs, signing, and verification at deploy admission tie every running artifact to a reviewed commit. Migrations run as gated, lock-protected pipeline steps before app deploy and are forward-fix by policy. CI secrets arrive via OIDC workload federation instead of stored credentials, fork PRs stay isolated from secret scopes, and branch protection with merge queues guarantees the tested SHA is the merged SHA.

The most important evidence base for this paper includes [S122](#s122) [S123](#s123) [S124](#s124) [S070](#s070). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- One artifact, many promotions: rebuilding per environment destroys reproducibility and provenance.
- Every stage owns explicit failure semantics; partial or unsigned artifacts never get promoted.
- The tested SHA must equal the merged SHA; merge queues rerun tests or nothing merges.
- Build identity and configuration identity are operational data. Without them, mixed-version and rollback failures are hard to diagnose.
- Development conveniences must not silently change security or durability semantics in production.

## 2. Scope and terminology map

The canonical topic list requires this paper to cover the following concerns. They are grouped only to expose relationships; no listed subtopic is omitted.

### State and lifecycle

**Artifact creation**.

### Contracts and validation

**Type checking**.

### Security, privacy, and abuse

**Security scanning**.

### Operations and observability

**Builds**, **Linting**, **Dependency scanning**, **Environment promotion**, **Deployment**, **Rollback**, **Quality gates**.

### Testing and evolution

**Tests**, **Migration execution**.

### Boundary of the paper

This paper treats **CI/CD** as a production subsystem or reusable reasoning primitive. It covers semantics, ownership, persistence, APIs, security, concurrency, distributed behavior, operations, evolution, and verification. Framework syntax and large implementation listings are intentionally excluded.

## 3. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S122](#s122) [S123](#s123) [S124](#s124) [S070](#s070)

1. **Invariant 1:** The process is not ready merely because its socket is listening; readiness requires every dependency needed for the advertised request class to be usable.
2. **Invariant 2:** Initialization order is a dependency graph, not a convenient list. Cycles and hidden lazy initialization create startup-only incidents.
3. **Invariant 3:** Shutdown is a protocol: stop admission, drain work, finish or abandon with explicit semantics, then release resources.
4. **Invariant 4:** Build identity and configuration identity are operational data. Without them, mixed-version and rollback failures are hard to diagnose.
5. **Invariant 5:** Development conveniences must not silently change security or durability semantics in production.

Additional topic-specific invariants:

- **SHOULD — Builds:** Define the exact semantics of **Builds** within CI/CD: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Linting:** Define the exact semantics of **Linting** within CI/CD: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST — Security scanning:** Define the exact semantics of **Security scanning** within CI/CD: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Environment promotion:** Define the exact semantics of **Environment promotion** within CI/CD: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **SHOULD — Rollback:** Define what can be reversed, what requires compensation or forward repair, and how data written by the new version remains readable. Rehearse the exact control-plane and data-plane sequence.
- **SHOULD — Quality gates:** Define the exact semantics of **Quality gates** within CI/CD: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.

## 4. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Eager vs lazy initialization | Eager initialization fails fast and proves readiness; lazy initialization shortens startup but moves failures into live traffic. | Prefer eager initialization for mandatory dependencies; use lazy loading only for optional or high-cost capabilities with explicit degraded behavior. |
| Single process vs separate workers | A single binary simplifies deployment but couples failure and scaling domains; separate workers isolate resources but add orchestration and versioning. | Split when workload, scaling, privilege, or failure characteristics differ materially. |
| Strict startup vs degraded startup | Strict startup avoids serving incomplete behavior; degraded startup preserves availability when optional dependencies fail. | Define dependency classes and expose degraded state in readiness and metrics. |
| Framework-owned vs application-owned lifecycle | Framework defaults are convenient but often hide cancellation, ordering, and timeout semantics. | Own the composition root and lifecycle even when using framework hooks. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 5. Ownership, state, and lifecycle

Model the process explicitly as `created → configuration_validated → dependencies_initializing → ready → draining → stopped`, with `failed_startup` reachable from every initialization stage. Initialization must be ordered by real dependencies, not incidental file import order. Shutdown reverses ownership: stop admission first, then drain requests and workers, then close producers/consumers, flush bounded telemetry, and finally release pools and files.

```mermaid
stateDiagram-v2
    created --> config_validated --> initializing --> ready --> draining --> stopped
    initializing --> failed_startup
    ready --> failed_runtime
    draining --> forced_stop
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 6. Data model and API implications

Configuration and runtime metadata form a versioned input contract. Validate types, ranges, mutual exclusions, required secrets, endpoint formats, and environment-specific prohibitions before opening traffic. Expose build/version metadata without secrets, define exactly what readiness means, and make process exit codes and signal behavior observable to supervisors.

A production representation commonly needs the following fields or equivalent evidence:

- `configuration_version` and validated environment identity.
- `build_version`, commit/build time, and deployment instance identity.
- dependency initialization state and ownership.
- readiness/drain state and shutdown reason.
- bounded lifecycle timestamps and failure classification.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 7. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### 7.1. Builds

- **SHOULD — engineering rule:** Build ONCE per commit: produce one immutable artifact tagged with the commit SHA, push it to a registry, and promote that same artifact environment to environment. Rebuilding per environment breaks provenance and reproducibility — "works in staging" becomes ambiguous because the bytes differ.
- **Production failure mode:** Staging and production run different bytes built from the "same" commit; a later rebuild resolves dependencies differently, and incident response cannot name the artifact that produced a failure.
- **Existing-codebase evidence:** Trace one artifact SHA end to end across environments and confirm the digest never changes after the single build; flag any job that compiles again after that build.

### 7.2. Tests

- **SHOULD — engineering rule:** Order pipeline stages — build → unit → integration → security scans → artifact packaging → deploy-to-dev → e2e/smoke → promotion gates — and give every stage explicit failure semantics: fail fast, stop the run, publish nothing downstream, so no partial artifact is ever promoted.
- **Production failure mode:** A failed unit stage still publishes its artifact, a flaky e2e stage is retried into green, or smoke tests pass against dev-shaped data while promotion assumes production parity.
- **Existing-codebase evidence:** Inject a failure at every stage and verify the run stops, downstream stages do not execute, and reported status names the true failing stage.

### 7.3. Linting

- **SHOULD — engineering rule:** Pin the linter version, run it as a fast blocking stage on the exact candidate commit, attach results to commit status so branch protection can require them, and budget warnings instead of letting suppressions accumulate silently.
- **Production failure mode:** Diffs merge locally-clean but CI-dirty because lint ran on a stale base; suppression comments pile up until real defects hide among them.
- **Existing-codebase evidence:** Confirm which commits trigger lint, that the linter version is pinned, and that required status checks include the lint job.

### 7.4. Type checking

- **SHOULD — engineering rule:** Type-check the full project (no incremental cache) with a locked toolchain as a blocking pre-packaging stage, including generated code in the checked surface so checks cover what actually ships.
- **Production failure mode:** Incremental caches pass locally while CI surfaces type errors days later, or generated clients drift until runtime casts fail in production.
- **Existing-codebase evidence:** Commit a deliberate type error and verify the pipeline blocks promotion; confirm generated code is inside the checked surface.

### 7.5. Security scanning

- **MUST — engineering rule:** Gate deploys on security scans (SAST, secret detection, image scanning) with severity thresholds defined before the scan runs; supply CI credentials through OIDC workload federation instead of stored secrets, keep fork PRs fully isolated from secret scopes, and treat log masking as best-effort, never as containment.
- **Production failure mode:** A fork PR reads stored cloud credentials, a critical finding is triaged into silence, or a "masked" secret leaks through build logs or artifact metadata.
- **Existing-codebase evidence:** Attempt fork-PR secret access in dry-run mode and prove denial; verify scan failures block promotion and thresholds are version-controlled.

### 7.6. Dependency scanning

- **SHOULD — engineering rule:** Generate an SBOM (SPDX/CycloneDX) for every artifact and gate on dependency vulnerability scanning at build time; re-scan promoted artifacts when new advisories land, and treat an artifact without an SBOM as unpromotable. Frame pipeline maturity SLSA-style where useful.
- **Production failure mode:** A vulnerable transitive dependency ships because only direct manifests were scanned, or responders cannot match a CVE to the deployed artifact because no SBOM exists.
- **Existing-codebase evidence:** Verify SBOM presence per artifact; publish a new advisory and confirm re-scan flags affected releases; map one CVE report back to the deployed SHA.

### 7.7. Artifact creation

- **SHOULD — engineering rule:** Package deterministically with embedded build metadata (commit SHA, build time, pipeline run), sign the artifact, and attach provenance attestation; deploy admission verifies signature and provenance before anything is allowed to run.
- **Production failure mode:** Unsigned artifacts slip past admission, metadata claims a commit that was never built, or two builds of one SHA yield different digests and break verification.
- **Existing-codebase evidence:** Verify signature/provenance at admission in staging with a tampered artifact; rebuild one SHA twice and compare digests for reproducibility.

### 7.8. Environment promotion

- **SHOULD — engineering rule:** Promotion moves the SAME immutable artifact through gates: dev → staging → production transitions require the previous environment's health evidence plus recorded approval, and promotion state lives in the pipeline control plane rather than tribal knowledge.
- **Production failure mode:** An artifact reaches production having skipped staging, approvals exist outside any audit trail, or "promotion" secretly re-runs the build with different variables.
- **Existing-codebase evidence:** Enumerate every path an artifact can take to production and prove each crosses the same gates; replay one promotion's approval trail from audit logs.

### 7.9. Deployment

- **SHOULD — engineering rule:** Deploy jobs reference the immutable artifact by digest, verification happens at deploy admission, and pipeline success requires post-deploy rollout health from the platform — not merely a zero exit code from an apply command.
- **Production failure mode:** Admission verification is skipped under time pressure, or the pipeline reports success while the rollout quietly fails behind health gates nobody watches.
- **Existing-codebase evidence:** Deploy a tampered artifact in staging and confirm rejection at admission; confirm pipeline success status is granted only after health evidence arrives.

### 7.10. Rollback

- **SHOULD — engineering rule:** Rollback means redeploying the PREVIOUS immutable artifact — never rebuilding old source. Database changes follow the documented forward-fix policy (compatible-expand schema; destructive reversal refused), and rollback is rehearsed in staging exactly like a rollout, including DB coupling behavior.
- **Production failure mode:** Rollback rebuilds from an old tag with drifted dependencies, or reverted code cannot read rows written by the newer schema, causing a second outage worse than the first.
- **Existing-codebase evidence:** Perform a production-like rollback drill after generating new-version data and partially completed work; verify the restored digest matches the previous release exactly.

### 7.11. Migration execution

- **SHOULD — engineering rule:** Schema migrations run as gated pipeline steps BEFORE app deploy, additive-first (expand pattern), serialized by advisory locking so parallel pipeline runs cannot migrate concurrently. Migrations are forward-fix: document why automatic schema rollback is refused instead of shipping a reverse path.
- **Production failure mode:** Two pipeline runs apply overlapping migrations, an app deploy races its own migration, or an automatic rollback reverses a schema that newer data already depends on.
- **Existing-codebase evidence:** Launch parallel pipeline runs against one migration step and verify the lock serializes them; confirm migration ordering precedes app deploy and expand steps are idempotent.

### 7.12. Quality gates

- **SHOULD — engineering rule:** Required status checks fail closed in branch protection; merge queues can change the commit SHA, so tests must rerun on the final merged SHA unless the queue guarantees identity; promotion gates aggregate stage results into one automated go/no-go decision.
- **Production failure mode:** CI was green on the merge-group SHA but never ran on the final merged SHA, or a manually skipped gate becomes the silent precedent for every future skip.
- **Existing-codebase evidence:** Check recent merges for cases where CI did not test the exact merged SHA; attempt to bypass a required check and confirm rejection; verify the gate decision is machine-readable.

## 8. Concurrency, transactions, idempotency, and consistency

Startup and shutdown are concurrent workflows. A dependency may connect while cancellation arrives; two shutdown signals may race; workers may publish or acknowledge while drain begins. Use one-way state transitions, idempotent cleanup, bounded waits, and ownership-aware cancellation. Never close a shared resource while work that can still use it remains admitted.

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

Classify dependency failures as fatal-at-start, degraded-but-ready, or dynamically recoverable. Avoid making readiness depend on optional remote services, but do not report ready when a required store cannot preserve correctness. Bound retries during startup; otherwise rollouts hang and amplify provider outages. On termination, prefer a controlled incomplete shutdown with explicit recovery semantics over an unbounded wait.

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

Emit structured lifecycle events with build ID, configuration version, environment, dependency name, elapsed initialization time, and shutdown reason. Track startup latency, readiness flaps, active work during drain, forced terminations, cleanup failures, pool utilization, and process resource limits. Runbooks must distinguish crash loops, readiness failures, dependency exhaustion, and termination deadline overruns.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 13. Compatibility, schema evolution, migration, deployment, and rollback

Runtime changes must work during rolling deployments where old and new processes coexist. Treat configuration schema, probes, signal grace periods, ports, and dependency initialization as compatibility surfaces. Deploy additive configuration first, then code that consumes it; remove old variables only after every workload has moved. Rollback must not depend on resources already destructively migrated.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every CI/CD path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Builds`, `Type checking`, `Artifact creation`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by CI/CD; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 15. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **CI/CD** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Builds**: Define the exact semantics of **Builds** within CI/CD: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **Linting**: Define the exact semantics of **Linting** within CI/CD: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **Security scanning**: Define the exact semantics of **Security scanning** within CI/CD: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.
- **MUST** — For **Environment promotion**: Define the exact semantics of **Environment promotion** within CI/CD: owner, inputs, outputs, invariants, lifecycle, failure classification, and compatibility contract. Make the rule enforceable at the narrowest authoritative boundary.

### SHOULD

- **SHOULD** — Promote on evidence from the previous environment (health, metrics, smoke results), not on pipeline greenness alone.
- **SHOULD** — Keep stages ordered by dependency: nothing downstream consumes upstream output that has not passed its gate.
- **SHOULD** — Make every manual override (gate skip, emergency deploy) rare, recorded, and reviewed; silent precedents become policy.
- **SHOULD** — Build identity and configuration identity are operational data. Without them, mixed-version and rollback failures are hard to diagnose.
- **SHOULD** — Development conveniences must not silently change security or durability semantics in production.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Choose a **merge-queue strategy** (rerun-on-merge versus batching) according to merge throughput and the cost of testing unmerged combinations.
- **MAY** — Adopt dynamic dependency rescans (re-check promoted artifacts when new advisories drop) where artifact volume makes full re-scanning affordable.
- **MAY** — Parallelize environment suites (staging shards) where wall-clock duration, not correctness, limits delivery speed.

### AVOID

- **AVOID** — Deploying application versions whose required migration has not completed in the target environment.
- **AVOID** — Auto-retrying failed gates until they pass; a retried-into-green stage hides a real defect.
- **AVOID** — Parallel pipeline runs mutating shared state (migrations, shared environments) without advisory locking.
- **AVOID** — Publishing artifacts from failed runs even "temporarily"; partial artifacts eventually get promoted.
- **AVOID** — Different defaults between local and production.
- **AVOID** — Pipeline logic copy-pasted across repositories instead of shared, versioned templates.
- **AVOID** — Long-lived stored CI credentials where OIDC workload federation is available.
- **AVOID** — Reporting deploy success on exit codes alone, without rollout health evidence.

### NEVER

- **NEVER** — Never merge through a red required check; use the documented emergency process instead.
- **NEVER** — Never run a migration step without its advisory lock held against concurrent pipeline runs.
- **NEVER** — Never promote an artifact whose SHA cannot be traced to a reviewed commit.

## 16. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Trace one artifact SHA end to end across all environments and confirm the digest never changes after the single build.
- [ ] Inject a failure at each pipeline stage and verify fail-fast semantics: the run stops, nothing downstream executes, and no partial artifact is promoted.
- [ ] Attempt fork-PR secret access in dry-run mode and prove denial; confirm masking does not extend to artifact metadata.
- [ ] Launch two pipeline runs targeting the same migration step and verify advisory locking serializes them.
- [ ] Inspect recent merges for cases where CI tested the merge-group SHA but not the final merged SHA; verify queue reruns where required.
- [ ] **Builds:** Locate every implementation path for builds, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Linting:** Locate every implementation path for linting, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Security scanning:** Locate every implementation path for security scanning, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Environment promotion:** Locate every implementation path for environment promotion, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Rollback:** Perform a production-like rollback drill after generating new-version data and partially completed work.
- [ ] **Quality gates:** Locate every implementation path for quality gates, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 17. Common production bugs and incorrect implementations

- Accepting traffic before migrations/config/dependencies are ready.
- Hanging on termination because background tasks ignore cancellation.
- Double-starting workers after reload or fork.
- Leaking pooled connections on failed startup.
- Different defaults between local and production.
- **Builds:** A framework or provider default for builds is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Linting:** A framework or provider default for linting is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Security scanning:** A framework or provider default for security scanning is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Artifact creation:** A framework or provider default for artifact creation is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Environment promotion:** A framework or provider default for environment promotion is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- **Rollback:** Code rolls back while schema/data/side effects do not, creating a second outage or corruption.
- **Quality gates:** A framework or provider default for quality gates is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Adding another global singleton instead of using the composition root.
- Reading environment variables inside handlers or packages.
- Reporting ready before migrations/dependencies are usable.
- Closing shared clients while workers still run.
- Using unbounded startup or shutdown retries.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **CI/CD** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- For **Builds**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for builds is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Linting**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for linting is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Security scanning**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for security scanning is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Environment promotion**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: A framework or provider default for environment promotion is accepted without proving it matches the domain, causing ambiguous state, race-sensitive behavior, or an operational gap.
- For **Rollback**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Code rolls back while schema/data/side effects do not, creating a second outage or corruption.
- Which artifact digest is deployed to each environment right now, and how fast can the previous digest be redeployed?

## 20. Existing-codebase checks before changing anything

- [ ] Map every entry point for **CI/CD**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read pipeline definitions, runner/executor configuration, secret-injection mechanisms, branch protection and merge-queue settings, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] **Builds:** Locate every implementation path for builds, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Linting:** Locate every implementation path for linting, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Security scanning:** Locate every implementation path for security scanning, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Artifact creation:** Locate every implementation path for artifact creation, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Environment promotion:** Locate every implementation path for environment promotion, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Rollback:** Perform a production-like rollback drill after generating new-version data and partially completed work.
- [ ] **Quality gates:** Locate every implementation path for quality gates, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] Locate every path an artifact can take from commit to production, including manual bypasses; prove each crosses the same gates.

## 21. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [108. Infrastructure Configuration](108-infrastructure-configuration.md) — layer: `cross-cutting`; profile: `runtime`.
- [106. Deployment Safety](106-deployment-safety.md) — layer: `cross-cutting`; profile: `runtime`.
- [002. Configuration Management](../systems/002-configuration-management.md) — layer: `systems`; profile: `runtime`.
- [001. Project & Runtime Foundations](../systems/001-project-and-runtime-foundations.md) — layer: `systems`; profile: `runtime`.
- [063. Secrets Management](063-secrets-management.md) — layer: `cross-cutting`; profile: `security`.
- [089. Dependency Management](089-dependency-management.md) — layer: `cross-cutting`; profile: `architecture`.
- [105. Graceful Shutdown](105-graceful-shutdown.md) — layer: `cross-cutting`; profile: `runtime`.
- [079. Connection Management](../systems/079-connection-management.md) — layer: `systems`; profile: `runtime`.
- [146. Cross-Cutting Implementation Checklist](146-cross-cutting-implementation-checklist.md) — layer: `cross-cutting`; profile: `checklist`.
- [011. Request Lifecycle](../primitives/011-request-lifecycle.md) — layer: `primitives`; profile: `api`.
- [138. Operational Runbooks](138-operational-runbooks.md) — layer: `cross-cutting`; profile: `observability`.
- [059. Health Checks](059-health-checks.md) — layer: `cross-cutting`; profile: `observability`.

## 22. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s122"></a> **[S122] The Twelve-Factor App.** Heroku; 2017; Current. [https://12factor.net/](https://12factor.net/) — Tags: runtime, configuration, deployment, processes.
- <a id="s123"></a> **[S123] The Twelve-Factor App: Config.** Heroku; 2017; Current. [https://12factor.net/config](https://12factor.net/config) — Tags: configuration, secrets, environment.
- <a id="s124"></a> **[S124] Linux signal(7) Manual.** Linux man-pages project; 2026; Current. [https://man7.org/linux/man-pages/man7/signal.7.html](https://man7.org/linux/man-pages/man7/signal.7.html) — Tags: signals, shutdown, processes.
- <a id="s070"></a> **[S070] Kubernetes Documentation.** Cloud Native Computing Foundation; 2026; Current. [https://kubernetes.io/docs/](https://kubernetes.io/docs/) — Tags: deployment, containers, health, shutdown, autoscaling.
- <a id="s071"></a> **[S071] Pod Lifecycle and Container Lifecycle Hooks.** Kubernetes; 2026; Current. [https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) — Tags: lifecycle, health, shutdown, deployment.
- <a id="s053"></a> **[S053] Site Reliability Engineering.** Google; 2016; Online book. [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/) — Tags: reliability, operations, monitoring, capacity.
- <a id="s077"></a> **[S077] Secure Software Development Framework.** NIST; 2022; SP 800-218 v1.1. [https://csrc.nist.gov/pubs/sp/800/218/final](https://csrc.nist.gov/pubs/sp/800/218/final) — Tags: secure-development, ci-cd, supply-chain.
- <a id="s128"></a> **[S128] Kubernetes Deployments.** Kubernetes; 2026; Current. [https://kubernetes.io/docs/concepts/workloads/controllers/deployment/](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) — Tags: deployment, rolling-update, rollback.
- <a id="s129"></a> **[S129] Kubernetes Resource Management for Pods and Containers.** Kubernetes; 2026; Current. [https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) — Tags: resources, containers, capacity.
- <a id="s073"></a> **[S073] Supply-chain Levels for Software Artifacts.** OpenSSF; 2026; SLSA v1.1. [https://slsa.dev/spec/v1.1/](https://slsa.dev/spec/v1.1/) — Tags: supply-chain, builds, provenance, ci-cd.
- <a id="s074"></a> **[S074] Sigstore Documentation.** OpenSSF; 2026; Current. [https://docs.sigstore.dev/](https://docs.sigstore.dev/) — Tags: signing, supply-chain, artifacts.
- <a id="s075"></a> **[S075] SPDX Specification.** Linux Foundation; 2026; 3.0. [https://spdx.github.io/spdx-spec/v3.0/](https://spdx.github.io/spdx-spec/v3.0/) — Tags: sbom, licenses, supply-chain.
- <a id="s076"></a> **[S076] CycloneDX Specification.** OWASP; 2026; Current. [https://cyclonedx.org/specification/overview/](https://cyclonedx.org/specification/overview/) — Tags: sbom, supply-chain, dependencies.

---

**Paper metadata:** canonical subtopics: 12; layer: `cross-cutting`; domain profile: `runtime`; verified through: `2026-08-17`.
