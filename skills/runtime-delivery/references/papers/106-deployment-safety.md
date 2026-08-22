# 106. Deployment Safety

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Deployment Safety** exists so changes reach production reversibly and observably. Progressive rollout strategies — rolling, blue/green, canary — trade capacity cost against detection speed, and the choice is made deliberately per service. Health gates control every traffic shift, and automatic abort criteria are defined BEFORE the rollout starts, derived from SLO burn rates and error-rate deltas rather than manual judgment made under pressure.

Rollback reality shapes the design: code reverts but data does not, so schema-coupled deploys follow forward-fix discipline and additive changes migrate before the deploy that needs them. Configuration and secrets stay consistent across environments, and every release pins the identity and provenance of the exact artifact deployed, so "what is running?" always has an answer and a revert path.

The most important evidence base for this paper includes [S122](#s122) [S123](#s123) [S124](#s124) [S070](#s070). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- A rollout is an experiment; traffic shifts move only as fast as the evidence gathered between stages.
- Abort criteria are declared before the rollout and enforced by automation, not negotiated during the incident.
- Code rolls back; data does not. Schema changes ride ahead of deploys and never require reverse migration.
- Build identity and configuration identity are operational data. Without them, mixed-version and rollback failures are hard to diagnose.
- Development conveniences must not silently change security or durability semantics in production.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Deployment Safety** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- Which environments gate promotion, who approves each transition, and how quickly can the last release be reverted, including its database coupling?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Deployment Safety**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, rollout strategy definitions, health-gate rules, automatic abort criteria, secret injection, probes, resource limits, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Locate every rollout strategy config, health gate, abort criterion, and rollback path; prove each executes via automation rather than memory.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S122](#s122) [S123](#s123) [S124](#s124) [S070](#s070)

1. **Invariant 1:** The process is not ready merely because its socket is listening; readiness requires every dependency needed for the advertised request class to be usable.
2. **Invariant 2:** Initialization order is a dependency graph, not a convenient list. Cycles and hidden lazy initialization create startup-only incidents.
3. **Invariant 3:** Shutdown is a protocol: stop admission, drain work, finish or abandon with explicit semantics, then release resources.
4. **Invariant 4:** Build identity and configuration identity are operational data. Without them, mixed-version and rollback failures are hard to diagnose.
5. **Invariant 5:** Development conveniences must not silently change security or durability semantics in production.

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Rolling vs blue/green/canary | Rolling is efficient but creates mixed versions; blue/green simplifies cutover but duplicates capacity; canary provides evidence with routing complexity. | Choose by compatibility and rollback needs; database changes must remain independently safe. |
| Eager vs lazy initialization | Eager initialization fails fast and proves readiness; lazy initialization shortens startup but moves failures into live traffic. | Prefer eager initialization for mandatory dependencies; use lazy loading only for optional or high-cost capabilities with explicit degraded behavior. |
| Single process vs separate workers | A single binary simplifies deployment but couples failure and scaling domains; separate workers isolate resources but add orchestration and versioning. | Split when workload, scaling, privilege, or failure characteristics differ materially. |
| Strict startup vs degraded startup | Strict startup avoids serving incomplete behavior; degraded startup preserves availability when optional dependencies fail. | Define dependency classes and expose degraded state in readiness and metrics. |
| Framework-owned vs application-owned lifecycle | Framework defaults are convenient but often hide cancellation, ordering, and timeout semantics. | Own the composition root and lifecycle even when using framework hooks. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

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

## 7. Data model and API implications

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

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **Blue/green**
- **Canary**
- **Progressive rollout**
- **Database compatibility**
- **Health gating**
- **Deployment validation**

### 8.1. Rolling deployment

- **SHOULD — engineering rule:** Define a compatibility window in which old and new readers/writers coexist. Make changes additive first, preserve unknown fields where required, and test both deployment orders.
- **Production failure mode:** A new writer emits data an old reader cannot parse, or rollback code cannot read records created during the failed release.
- **Existing-codebase evidence:** Run an N/N+1 matrix for requests, stored data, events, queues, caches, and rollback.

### 8.5. Rollback

- **SHOULD — engineering rule:** Define what can be reversed, what requires compensation or forward repair, and how data written by the new version remains readable. Rehearse the exact control-plane and data-plane sequence.
- **Production failure mode:** Code rolls back while schema/data/side effects do not, creating a second outage or corruption.
- **Existing-codebase evidence:** Perform a production-like rollback drill after generating new-version data and partially completed work.

### 8.6. Feature flags

- **SHOULD — engineering rule:** Give flags typed ownership, safe defaults, evaluation context, audit, expiry, dependency rules, and deterministic assignment. Separate release flags from durable configuration.
- **Production failure mode:** A missing flag service changes behavior unsafely, cohorts flap, or stale dead flags permanently fork code paths.
- **Existing-codebase evidence:** Test provider outage, missing/invalid values, rollout stability, rollback, authorization of changes, and cleanup.

### 8.8. Mixed-version compatibility

- **SHOULD — engineering rule:** Define a compatibility window in which old and new readers/writers coexist. Make changes additive first, preserve unknown fields where required, and test both deployment orders.
- **Production failure mode:** A new writer emits data an old reader cannot parse, or rollback code cannot read records created during the failed release.
- **Existing-codebase evidence:** Run an N/N+1 matrix for requests, stored data, events, queues, caches, and rollback.

## 9. Concurrency, transactions, idempotency, and consistency

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

## 10. Security, authorization, privacy, and abuse resistance

Map trust boundaries, assets, attackers, privileges, data flows, and failure modes before selecting controls. Enforce least privilege in the component that owns the resource; edge filtering, WAFs, and gateways are supplementary. Treat every external, model-generated, cached, imported, or administrator-supplied value as untrusted at its use context.

- **MUST** authenticate the actual caller or workload and re-authorize the final action against authoritative tenant, ownership, resource state, and policy context.
- **MUST** reject mass assignment and unknown privileged fields; server-controlled identity, role, tenant, status, price, owner, and audit fields cannot come from an untrusted DTO.
- **MUST** classify and minimize sensitive data; redact logs/traces/errors, restrict exports and support tooling, propagate deletion, and account for backups and derived indexes.
- **SHOULD** combine rate limits with resource budgets, concurrency caps, payload/complexity limits, and detection. IP-only limiting is not an identity or abuse strategy.
- **AVOID** fail-open behavior for high-impact actions when policy, key, revocation, or tenant context is unavailable.

## 11. Distributed failure, retries, timeouts, and recovery

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

## 12. Persistence, constraints, indexes, and caching

- Put race-sensitive invariants in the database or authoritative store. Application checks remain useful for error quality but are not the final guard.
- Design indexes from real query predicates, tenant scope, ordering, soft-delete conditions, and production cardinality. Verify plans and write amplification.
- Keep transactions bounded in time and rows; avoid network/provider calls while locks are held.
- Treat caches, search indexes, analytics, and replicas as derived unless explicitly authoritative. Version them and provide rebuild/reconciliation.
- Retention and cleanup must include references, uniqueness, tombstones, legal hold, audit, external copies, and interrupted-job recovery.

## 13. Observability, audit, and operational control

Emit structured lifecycle events with build ID, configuration version, environment, dependency name, elapsed initialization time, and shutdown reason. Track startup latency, readiness flaps, active work during drain, forced terminations, cleanup failures, pool utilization, and process resource limits. Runbooks must distinguish crash loops, readiness failures, dependency exhaustion, and termination deadline overruns.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

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

## 15. Cross-cutting implementation matrix

| Concern | Required production decision |
|---|---|
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Deployment Safety path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Rolling deployment`, `Canary`, `Rollback`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Deployment Safety; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Deployment Safety** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Rolling deployment**: Define a compatibility window in which old and new readers/writers coexist. Make changes additive first, preserve unknown fields where required, and test both deployment orders.
- **MUST** — For **Rollback**: Define what can be reversed, what requires compensation or forward repair, and how data written by the new version remains readable. Rehearse the exact control-plane and data-plane sequence.
- **MUST** — For **Feature flags**: Give flags typed ownership, safe defaults, evaluation context, audit, expiry, dependency rules, and deterministic assignment. Separate release flags from durable configuration.

### SHOULD

- **SHOULD** — Health gates evaluate release-level evidence — error-rate delta, latency, saturation against baseline — not container liveness alone; a passing probe is not a healthy release.
- **SHOULD** — Order schema, configuration, and code changes deliberately: additive migration first, deploy second, cleanup last, with old and new versions coexisting throughout the window.
- **SHOULD** — Rehearse rollback like rollout: drill the revert of the last release in staging, including database coupling behavior, before production ever needs it.
- **SHOULD** — Build identity and configuration identity are operational data. Without them, mixed-version and rollback failures are hard to diagnose.
- **SHOULD** — Development conveniences must not silently change security or durability semantics in production.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Choose **Rolling vs blue/green/canary** according to the stated trade-off: Choose by compatibility and rollback needs; database changes must remain independently safe.
- **MAY** — Choose **progressive exposure level** (canary percentage, ring count, hold duration) according to blast-radius tolerance and metric sensitivity.
- **MAY** — Choose **cutover style** (rolling in-place versus blue/green swap) according to capacity headroom and how quickly traffic must be able to return to the old version.
- **MAY** — Adopt **automated analysis windows** (metric comparison against baseline for a fixed bake time) where traffic patterns are stable enough for statistical gating.

### AVOID

- **AVOID** — Accepting traffic before migrations/config/dependencies are ready.
- **AVOID** — Advancing a rollout stage while its abort threshold is breached because automation waits for human judgment.
- **AVOID** — Rebuilding artifacts per environment, which silently breaks provenance and reproducibility.
- **AVOID** — Widening canary traffic without comparing against a matched control baseline.
- **AVOID** — Different defaults between local and production.
- **AVOID** — Production changes made by console that bypass the pinned artifact and configuration pipeline.
- **AVOID** — Coupling deploy success to schema mutation so tightly that rollback becomes impossible.
- **AVOID** — Reporting ready before migrations/dependencies are usable.

### NEVER

- **NEVER** — Never report readiness before required correctness dependencies and configuration are usable.
- **NEVER** — Never advance a rollout stage without evaluating the pre-declared automatic abort criteria.
- **NEVER** — Never deploy an artifact whose provenance cannot be verified to a reviewed commit.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Diff resolved configuration and secret references across dev, staging, and production; promote only when sources and shape match.
- [ ] Deploy a deliberately unhealthy build behind the health gates in staging; prove no traffic reaches it and the rollout halts without manual intervention.
- [ ] Trigger each automatic abort criterion mid-rollout by injecting SLO burn and error-rate deltas; verify traffic freezes or reverts and the record shows which criterion fired.
- [ ] Run mixed-version rolling deployment tests covering probes, configuration, stored-data readability, event consumption, and rollback.
- [ ] Verify artifact identity end to end: the digest deployed to each environment matches the single build, with signature/provenance verification at admission.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Closing shared clients while workers still run.
- Using unbounded startup or shutdown retries.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- 071. Backward Compatibility — in the `migration-evolution` skill.
- [108. Infrastructure Configuration](108-infrastructure-configuration.md)
- [107. CI/CD](107-ci-cd.md)
- [002. Configuration Management](002-configuration-management.md)
- [001. Project & Runtime Foundations](001-project-and-runtime-foundations.md)
- 068. Feature Flags — in the `security-privacy` skill.
- 030. Database Migrations — in the `migration-evolution` skill.
- [105. Graceful Shutdown](105-graceful-shutdown.md)
- 134. Zero-Downtime Changes — in the `migration-evolution` skill.
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.
- 059. Health Checks — in the `production-operations` skill.
- 015. API Versioning & Compatibility — in the `api-contracts` skill.

## 20. Sources and further research

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
