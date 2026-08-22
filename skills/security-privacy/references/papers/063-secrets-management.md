# 063. Secrets Management

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Secrets Management** exists to reduce exploitable trust, privilege, and data exposure across inputs, components, operators, and dependencies. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

Map trust boundaries, assets, attackers, privileges, data flows, and failure modes before selecting controls. Enforce least privilege in the component that owns the resource; edge filtering, WAFs, and gateways are supplementary. Treat every external, model-generated, cached, imported, or administrator-supplied value as untrusted at its use context.

The most important evidence base for this paper includes [S021](#s021) [S022](#s022) [S023](#s023) [S077](#s077). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Every external input—including data from trusted providers, queues, files, and internal services—crosses a trust boundary.
- Least privilege applies to identities, data fields, network paths, secrets, and administrative tooling.
- Secure defaults must remain safe when configuration is missing, stale, or partially deployed.
- Cryptographic protection fails when keys, randomness, nonces, algorithms, or lifecycle management are wrong.
- Security controls require abuse-case tests and operational detection, not only happy-path unit tests.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Secrets Management** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- What attacker-controlled input reaches which privileged sink, and what is the secure failure mode?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Secrets Management**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Search logs, traces, metrics, backups, support tools, and error reports for sensitive fields and bypasses.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S021](#s021) [S022](#s022) [S023](#s023) [S077](#s077)

1. **Invariant 1:** Every external input—including data from trusted providers, queues, files, and internal services—crosses a trust boundary.
2. **Invariant 2:** Least privilege applies to identities, data fields, network paths, secrets, and administrative tooling.
3. **Invariant 3:** Secure defaults must remain safe when configuration is missing, stale, or partially deployed.
4. **Invariant 4:** Cryptographic protection fails when keys, randomness, nonces, algorithms, or lifecycle management are wrong.
5. **Invariant 5:** Security controls require abuse-case tests and operational detection, not only happy-path unit tests.

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Prevent vs detect/respond | Prevention reduces incidents but no control is perfect; detection without prevention leaves easy exploit paths. | Layer preventive controls with detection, containment, and recovery. |
| Central gateway vs service-local controls | Gateways provide consistency but cannot understand all resource semantics; local checks know context but can drift. | Enforce coarse controls at the edge and object/action controls in the owning service. |
| Encryption field-level vs storage-level | Storage encryption protects media; field-level encryption narrows exposure but complicates query, rotation, and indexing. | Use field-level protection for high-impact data with a clear key and access model. |
| Block vs challenge vs observe | Blocking stops abuse but creates false positives; challenge adds friction; observe gathers evidence. | Stage controls by confidence and impact, with emergency switches. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

Security-sensitive objects—secrets, keys, grants, tokens, certificates, exceptions, and incident indicators—need issuance, activation, rotation, suspension, revocation, expiry, destruction, and audit states. Threats also evolve; controls need detection, review, and retirement rather than one-time setup.

```mermaid
stateDiagram-v2
    untrusted_input --> canonicalized_and_validated --> authenticated --> authorized --> least_privilege_execution --> encoded_or_protected_output --> audited
    any_stage --> denied_or_contained
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Specify accepted inputs and canonicalization, output encoding context, authorization policy, secret handling, cryptographic algorithm/key parameters, secure-failure behavior, and abuse limits. Security errors should not reveal account, resource, or parsing details useful to attackers.

A production representation commonly needs the following fields or equivalent evidence:

- asset/data classification and authoritative owner.
- credential/key/secret/certificate version and lifecycle state.
- grant/scope/policy and security-version metadata.
- security event actor, target, result, detection source, and containment status.
- retention, legal hold, deletion, and evidence-integrity metadata.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### 8.1. Environment secrets

- **MUST — engineering rule:** Separate environments cryptographically and administratively: production secrets live in a managed secret boundary reachable only by production principals, non-prod principals cannot resolve production paths, and every environment holds its own credential set — a shared dev/prod secret turns one leak into every environment.
- **Production failure mode:** A staging service or developer laptop holding production credentials becomes the cheapest path into production, and one leaked shared secret forces simultaneous rotation everywhere it was reused.
- **Existing-codebase evidence:** Inventory which secrets load from environment variables or files versus vault fetches, then verify IAM/policy scope actually denies a non-production principal reading a production secret path.

### 8.2. Secret stores

- **MUST — engineering rule:** Keep configuration-type secrets (database passwords, API keys, third-party tokens) in a managed secret manager (Vault, AWS Secrets Manager, GCP Secret Manager) that provides versioning, IAM-scoped reads, and read auditing; never place them in committed dotenv files, container images, or process arguments.
- **Production failure mode:** Secrets pasted into env files, Helm values, or image layers leak through git history and artifact registries; a store without version history makes rotation a breaking restart event.
- **Existing-codebase evidence:** Inventory env-var/file-loaded secrets versus vault-fetched ones, grep images and logs for accidental secret persistence, and confirm versions are retained so consumers can pin, roll back, and verify freshness.

### 8.3. Vault systems

- **SHOULD — engineering rule:** Treat vault platforms as policy engines, not dumb storage: bind each workload to a least-privilege policy on narrow paths, prefer dynamic/leased credentials that expire themselves, and make unseal strategy, auth methods, and audit-device enablement part of the deployment contract rather than tribal knowledge.
- **Production failure mode:** A vault that seals on restart with no auto-unseal story takes every dependent service down at once, and wildcard policies like `secret/*` recreate the flat all-access namespace inside the vault.
- **Existing-codebase evidence:** Read the policies bound to each auth role, compare lease/TTL settings against consumer refresh behavior, and verify an audit device is enabled and shipped off-box.

### 8.4. KMS integration

- **SHOULD — engineering rule:** Reserve KMS/HSM-backed custody for KEY material (data keys, signing keys, token-signing private keys): cryptographic operations happen inside the service boundary, plaintext keys never persist outside the HSM except wrapped, and key policies stay separate from secret-manager policies because rotation semantics, audit surfaces, and hardware boundaries differ between the two tiers.
- **Production failure mode:** Conflating the tiers leaves signing keys sharing a blast radius with config secrets; rotating or disabling a CMK without re-wrap planning renders existing ciphertext undecryptable.
- **Existing-codebase evidence:** Map which key protects which data, verify key IDs/versions are recorded alongside ciphertexts so pre-rotation data still decrypts, and confirm a rotation has actually been exercised rather than merely enabled.

### 8.5. Secret access

- **MUST — engineering rule:** Make workload identity federation the default machine authentication: cloud-native identities (IAM roles for service accounts, Azure managed identities, GCP service accounts) eliminate static credentials entirely, and OIDC-federated short-lived tokens replace stored deploy keys and cloud creds; static long-lived credentials are the legacy exception requiring documented compensating controls and a scheduled federation migration.
- **Production failure mode:** A static cloud access key embedded in service config outlives its creator, gets copied across environments and backups, and grants access nobody remembers provisioning until it leaks.
- **Existing-codebase evidence:** Find long-lived static credentials and map each to its federation replacement (IRSA, GCP workload identity federation, Azure managed identity); flag any survivor without an owner, rotation date, and compensating control.

### 8.6. Secret rotation

- **MUST — engineering rule:** Rotate with overlapping versions — issue the new value while the old remains valid through consumer-refresh lag — tie cadence to blast radius (shared database credentials rotate faster than a low-value third-party API key), use provider-managed automatic rotation where supported (managed database credentials), and rehearse the full path in staging, because a rotation nobody has tested is a future outage.
- **Production failure mode:** Single-version rotation locks out every process still holding the old value; the overlap window assumed in the runbook is shorter than real consumer cache TTLs, so cutover fails mid-migration.
- **Existing-codebase evidence:** Test rotation end-to-end in staging with real consumers: measure how long old-version acceptance must persist, find processes needing restart to refresh, and verify dual-version support before shortening any cadence.

### 8.7. Secret revocation

- **MUST — engineering rule:** Document the emergency revocation path BEFORE an incident: know how to kill a leaked credential by disabling the principal (not merely overwriting the secret value), and measure propagation delay honestly — effective revocation equals the longest cache/session TTL across every consumer — recording the measured number in the runbook.
- **Production failure mode:** Mid-incident the team discovers revocation takes effect only after a 15-minute cache TTL plus a session lifetime nobody measured, while the attacker keeps a working credential throughout.
- **Existing-codebase evidence:** Revoke a non-production principal in staging and time how long each consumer keeps accepting it; verify the kill switch disables the underlying principal or role, not just the latest secret version.

### 8.8. Secret auditing

- **MUST — engineering rule:** Audit secret READS, not only writes — leak investigation requires knowing which principal fetched which secret when — and alert on anomalous-read patterns such as a service suddenly reading secrets it never touched.
- **Production failure mode:** After a compromise nobody can enumerate what the attacker's principal read because reads were never logged, so incident response degenerates into rotate-everything.
- **Existing-codebase evidence:** Verify audit coverage of reads (successful and denied) in vault/secret-manager audit logs, confirm they ship off-box with tamper resistance, and check an alert exists for reads outside a principal's historical pattern.

### 8.9. Secret leakage prevention

- **MUST — engineering rule:** Assume secrets reach places they should not: run secret scanning on repositories and diffs, forbid secrets in process arguments/logs/images, give artifact registries their own rotatable credentials, and treat CI masking as best-effort — never as the control keeping secrets out of workflow logs.
- **Production failure mode:** A build argument bakes a registry credential into a public image layer, or a masked variable leaks through a command echo the masker did not recognize.
- **Existing-codebase evidence:** Grep built images and CI logs for accidental secret persistence, check build scripts for ARG/ENV-based secret injection, and confirm each registry and mirror has distinct, individually rotatable credentials.

### 8.10. Local development

- **SHOULD — engineering rule:** Give developers federated or brokered access to dedicated non-production secrets — dev vault namespaces, personal sandbox roles, expiring leases attributable to an individual — while local code defaults to stub credentials and can never reach production values from a laptop.
- **Production failure mode:** A shared `dev.env` file circulates in chat for years; when it contains production endpoint credentials, the leak surface includes every laptop the file ever reached.
- **Existing-codebase evidence:** Search the repo and onboarding docs for checked-in `.env` files and shared dev secrets; verify developer access goes through individual identity (SSO-backed vault auth) rather than a team-shared credential.

### 8.11. CI/CD secrets

- **MUST — engineering rule:** Replace stored pipeline credentials with OIDC federation — GitHub Actions/GitLab CI OIDC tokens exchanged for short-lived, scoped cloud roles; keep permissions job-scoped, ensure fork PRs never gain access to secret scopes, pull deploy-time secrets at runtime instead of baking them into artifacts, and provision artifact registries their own credentials.
- **Production failure mode:** A `pull_request_target` workflow exposes secrets to untrusted fork code, or a long-lived cloud key in repository variables outlives the employee who created it and ships in every exfiltrated repo mirror.
- **Existing-codebase evidence:** List stored CI variables/secrets and map each to an OIDC-federated equivalent; verify fork PR runs cannot read secret scopes and produced images reference deploy-time injection, not build-time baking.

### 8.12. Log redaction

- **SHOULD — engineering rule:** Redact secret-shaped values at the logging framework level (structured field allowlists, pattern scrubbers) while assuming any single mechanism misses values — so also constrain which components receive secrets at all, and keep debug/trace levels off in production where raw headers and connection strings surface.
- **Production failure mode:** A stack trace prints a connection string including its password, or an HTTP client logs the Authorization header verbatim after someone enables debug logging during an incident.
- **Existing-codebase evidence:** Grep logs, crash dumps, and APM payloads for known secret prefixes and connection-string patterns; identify log statements accepting raw header/env objects and add structured redaction at those sinks.

## 9. Concurrency, transactions, idempotency, and consistency

Authorization and validation must be tied to the operation that uses them; check-then-act gaps enable races. Key/secret rotation needs overlap and versioning. Revocation and policy changes require bounded propagation. Security controls that depend on distributed stores need explicit partition behavior.

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

Assume bypass attempts, malformed encodings, alternate protocols, SSRF redirects, oversized decompression, log injection, stale caches, leaked credentials, and unavailable security dependencies. Fail closed for high-impact actions, but design capacity and emergency paths so failure does not become uncontrolled outage.

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

Log security-relevant outcomes with redaction and tamper resistance; monitor abuse velocity, authorization denials, validation rejects, secret access, key/certificate age, anomaly detections, and control failures. Alerts need runbooks and containment actions, not merely dashboards.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

Security migrations—new keys, ciphers, headers, policies, scopes, token formats—require overlap, compatibility tests, and rollback. Remove insecure legacy only after usage evidence and client migration. Track exceptions with owner and expiry; permanent emergency bypasses are latent vulnerabilities.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Secrets Management path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Environment secrets`, `KMS`, `Secret revocation`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Secrets Management; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Secrets Management** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Environment secrets**: Store secrets in a managed secret boundary, grant workload-specific access, avoid process arguments/logs/images, support overlapping rotation, audit reads, and define emergency revocation.
- **MUST** — For **Secret auditing**: Record real actor, effective actor, action, resource, tenant, timestamp, request/trace, policy context, outcome, and appropriately minimized change details in tamper-resistant storage.

### SHOULD

- **SHOULD** — Every external input—including data from trusted providers, queues, files, and internal services—crosses a trust boundary.
- **SHOULD** — Least privilege applies to identities, data fields, network paths, secrets, and administrative tooling.
- **SHOULD** — Secure defaults must remain safe when configuration is missing, stale, or partially deployed.
- **SHOULD** — Cryptographic protection fails when keys, randomness, nonces, algorithms, or lifecycle management are wrong.
- **SHOULD** — Security controls require abuse-case tests and operational detection, not only happy-path unit tests.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Adopt the **Prevent vs detect/respond** option that fits the workload and ownership boundary; Layer preventive controls with detection, containment, and recovery.
- **MAY** — Adopt the **Central gateway vs service-local controls** option that fits the workload and ownership boundary; Enforce coarse controls at the edge and object/action controls in the owning service.
- **MAY** — Adopt the **Encryption field-level vs storage-level** option that fits the workload and ownership boundary; Use field-level protection for high-impact data with a clear key and access model.

### AVOID

- **AVOID** — Mass assignment updating privileged fields.
- **AVOID** — SSRF through URL fetchers.
- **AVOID** — Secret leakage in logs or crash dumps.
- **AVOID** — Weak random tokens.
- **AVOID** — Security control failing open on dependency error.
- **AVOID** — Creating custom cryptography or token generation.
- **AVOID** — Trusting gateway validation inside services.
- **AVOID** — Blacklisting strings instead of validating at the sink.

### NEVER

- **NEVER** — Never design custom cryptography when a reviewed standard primitive/protocol exists.
- **NEVER** — Never rely on a single perimeter control for object-level security.
- **NEVER** — Never retain an emergency bypass without scope, owner, audit, and expiry.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Build abuse cases from the threat model and test alternate encodings, protocol confusion, privilege changes, and bypass paths.
- [ ] Fuzz untrusted inputs at their use sinks for injection, traversal, SSRF, deserialization, decompression, and output-context failures.
- [ ] Rotate, revoke, expire, and lose keys/secrets/certificates while old and new versions coexist.
- [ ] Inject security-service/cache failure and verify secure failure without unbounded outage or bypass.
- [ ] Review and test logs, backups, traces, crash dumps, support tools, and exports for sensitive-data leakage.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Storing secrets in configuration files/logs.
- Adding a permanent fail-open bypass.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [065. TLS / PKI](065-tls-pki.md)
- [064. Cryptography](064-cryptography.md)
- 113. Machine-to-Machine Authentication — in the `auth-access` skill.
- 114. API Keys — in the `auth-access` skill.
- [061. Security Fundamentals](061-security-fundamentals.md)
- [066. Privacy & Sensitive Data](066-privacy-and-sensitive-data.md)
- [127. Randomness & Token Generation](127-randomness-and-token-generation.md)
- 002. Configuration Management — in the `runtime-delivery` skill.
- 144. Untrusted Code Execution — in the `ai-agent-system-architecture` skill.
- 107. CI/CD — in the `runtime-delivery` skill.
- 040. File Handling — in the `data-storage` skill.
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s021"></a> **[S021] Application Security Verification Standard.** OWASP; 2025; ASVS 5.0.0. [https://owasp.org/www-project-application-security-verification-standard/](https://owasp.org/www-project-application-security-verification-standard/) — Tags: security, authentication, authorization, validation, logging.
- <a id="s022"></a> **[S022] OWASP Top 10:2025.** OWASP; 2025; 2025. [https://owasp.org/Top10/](https://owasp.org/Top10/) — Tags: security, web, risks.
- <a id="s023"></a> **[S023] OWASP API Security Top 10.** OWASP; 2023; 2023. [https://owasp.org/API-Security/editions/2023/en/0x11-t10/](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) — Tags: api, security, authorization, abuse.
- <a id="s024"></a> **[S024] OWASP Cheat Sheet Series.** OWASP; 2026; Living collection. [https://cheatsheetseries.owasp.org/](https://cheatsheetseries.owasp.org/) — Tags: security, validation, sessions, files, logging, secrets.
- <a id="s077"></a> **[S077] Secure Software Development Framework.** NIST; 2022; SP 800-218 v1.1. [https://csrc.nist.gov/pubs/sp/800/218/final](https://csrc.nist.gov/pubs/sp/800/218/final) — Tags: secure-development, ci-cd, supply-chain.
- <a id="s078"></a> **[S078] The Transport Layer Security (TLS) Protocol Version 1.3.** IETF; 2018; RFC 8446. [https://www.rfc-editor.org/rfc/rfc8446.html](https://www.rfc-editor.org/rfc/rfc8446.html) — Tags: tls, cryptography, networking.
- <a id="s079"></a> **[S079] Recommendations for Secure Use of TLS and DTLS.** IETF; 2022; RFC 9325 / BCP 195. [https://www.rfc-editor.org/rfc/rfc9325.html](https://www.rfc-editor.org/rfc/rfc9325.html) — Tags: tls, security, pki.
- <a id="s080"></a> **[S080] Recommendation for Key Management.** NIST; 2020; SP 800-57 Part 1 Rev. 5. [https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final) — Tags: cryptography, keys, rotation.
- <a id="s081"></a> **[S081] Privacy Framework.** NIST; 2020; 1.0. [https://www.nist.gov/privacy-framework](https://www.nist.gov/privacy-framework) — Tags: privacy, pii, risk.
- <a id="s082"></a> **[S082] General Data Protection Regulation.** European Union; 2016; Regulation (EU) 2016/679. [https://eur-lex.europa.eu/eli/reg/2016/679/oj](https://eur-lex.europa.eu/eli/reg/2016/679/oj) — Tags: privacy, retention, deletion, consent.
- <a id="s097"></a> **[S097] HTTP Strict Transport Security.** IETF; 2012; RFC 6797. [https://www.rfc-editor.org/rfc/rfc6797.html](https://www.rfc-editor.org/rfc/rfc6797.html) — Tags: hsts, web-security, tls.
- <a id="s098"></a> **[S098] Content Security Policy Level 3.** W3C; 2025; Working Draft. [https://www.w3.org/TR/CSP3/](https://www.w3.org/TR/CSP3/) — Tags: csp, web-security, xss.
- <a id="s099"></a> **[S099] Fetch Standard.** WHATWG; 2026; Living Standard. [https://fetch.spec.whatwg.org/](https://fetch.spec.whatwg.org/) — Tags: cors, http, web-security.
- <a id="s100"></a> **[S100] Zero Trust Architecture.** NIST; 2020; SP 800-207. [https://csrc.nist.gov/pubs/sp/800/207/final](https://csrc.nist.gov/pubs/sp/800/207/final) — Tags: zero-trust, service-auth, authorization.
- <a id="s101"></a> **[S101] Computer Security Incident Handling Guide.** NIST; 2025; SP 800-61 Rev. 3. [https://csrc.nist.gov/pubs/sp/800/61/r3/final](https://csrc.nist.gov/pubs/sp/800/61/r3/final) — Tags: incidents, operations, recovery.
- <a id="s102"></a> **[S102] Security and Privacy Controls for Information Systems and Organizations.** NIST; 2020; SP 800-53 Rev. 5. [https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) — Tags: security, audit, privacy, operations.
- <a id="s135"></a> **[S135] Logging Cheat Sheet.** OWASP; 2026; Living document. [https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) — Tags: logging, security, audit, privacy.
