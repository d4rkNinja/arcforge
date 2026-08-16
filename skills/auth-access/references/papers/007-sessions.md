# 007. Sessions

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Sessions** exists to establish and continuously manage evidence that a claimant controls authenticators bound to a subject. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

Authentication owns enrollment, challenge issuance, credential verification, factor policy, recovery, token/session issuance, rotation, and revocation. It must consume identity status and risk inputs but must not silently embed business authorization. A successful authenticator check is only evidence; session issuance still depends on account state, required factors, audience, device policy, and current risk.

The most important evidence base for this paper includes [S005](#s005) [S007](#s007) [S015](#s015) [S016](#s016). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Authentication is a lifecycle of enrollment, verification, use, rotation, recovery, revocation, and audit—not only a login endpoint.
- A successful credential check is not sufficient when account status, risk policy, factor freshness, or session policy rejects the login.
- Recovery paths are usually weaker than primary authentication and therefore define the effective security level.
- Token and session expiry limit exposure but do not by themselves provide revocation or prevent replay.
- Authentication responses must resist account enumeration while still being diagnosable internally.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Sessions** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- What is the weakest recovery/factor-removal path, and does it reduce the effective assurance below the stated policy?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Sessions**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Enumerate all credential issuance, reset, recovery, linking, refresh, logout, support override, and revocation paths.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S005](#s005) [S007](#s007) [S015](#s015) [S016](#s016)

1. **Invariant 1:** Authentication is a lifecycle of enrollment, verification, use, rotation, recovery, revocation, and audit—not only a login endpoint.
2. **Invariant 2:** A successful credential check is not sufficient when account status, risk policy, factor freshness, or session policy rejects the login.
3. **Invariant 3:** Recovery paths are usually weaker than primary authentication and therefore define the effective security level.
4. **Invariant 4:** Token and session expiry limit exposure but do not by themselves provide revocation or prevent replay.
5. **Invariant 5:** Authentication responses must resist account enumeration while still being diagnosable internally.

Additional topic-specific invariants:

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Database-backed vs distributed-cache session store | A database improves durability/audit; an in-memory distributed cache improves latency but may lose state during failover. | Select based on revocation and durability needs; keep session semantics independent of store. |
| Server-side session vs self-contained access token | Server-side sessions give immediate control and small cookies; self-contained tokens reduce lookup dependency but complicate revocation and claim freshness. | Use short-lived access tokens with controlled refresh or server-side sessions according to trust boundaries and operational needs. |
| Opaque vs JWT access token | Opaque tokens centralize authority and revocation; JWTs enable local verification but replicate authorization data and key-management burden. | Prefer opaque tokens when introspection latency is acceptable; use JWTs for bounded audiences with strict validation and short lifetimes. |
| Password vs passwordless/passkey | Passwords are ubiquitous but phishable and reused; passkeys reduce phishing but introduce recovery, device-sync, and compatibility concerns. | Offer phishing-resistant authenticators for higher assurance and design recovery before enrollment. |
| Lockout vs adaptive throttling | Hard lockouts can be weaponized for denial of service; adaptive throttling is less disruptive but more complex. | Use layered IP/account/device controls with escalating delays and alerting. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

Model each ceremony as a short-lived transaction: `initiated → challenge_issued → evidence_verified → additional_factor_required|authenticated → consumed`, with `expired`, `locked`, and `cancelled` terminal outcomes. Credentials separately move through enrollment, active use, rotation, compromise, revocation, and deletion. Session/token families need their own lineage and revocation state.

```mermaid
stateDiagram-v2
    initiated --> challenge_issued --> evidence_verified
    evidence_verified --> step_up_required --> authenticated
    evidence_verified --> authenticated
    challenge_issued --> expired
    challenge_issued --> locked
    authenticated --> rotated
    authenticated --> revoked
    authenticated --> expired
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Authentication requests must bind purpose, subject or discovery context, client, redirect/return intent, challenge, expiry, and attempt budget. Tokens require explicit issuer, audience, type, scopes, temporal claims, key identifier, and revocation strategy. Public responses should resist enumeration; internal error codes and audit events must still distinguish failure causes.

A production representation commonly needs the following fields or equivalent evidence:

- credential/factor identifier, type, protected verifier/public key, parameters, status, and timestamps.
- short-lived challenge transaction with purpose, binding, expiry, attempts, and atomic consumed state.
- session/token-family lineage, audience/scopes, device context, issued/idle/absolute expiry, and revocation reason.
- risk and assurance state without storing raw secrets.
- security events for enrollment, use, reset, recovery, rotation, reuse, and revocation.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **Session creation**
- **Session storage**
- **HttpOnly**
- **SameSite**
- **Session hijacking**
- **Session invalidation**
- **Session limits**
- **Device metadata**
- **Session history**
- **Distributed sessions**
- **Session cache**
- **Session cleanup**

### 8.3. Session cookies

- **SHOULD — engineering rule:** Set the narrowest domain/path and appropriate Secure, HttpOnly, and SameSite attributes; rotate identifiers after authentication or privilege changes and prevent caching of sensitive responses.
- **Production failure mode:** Over-broad cookies leak to sibling hosts, cross-site requests carry ambient authority, or a pre-authentication identifier is fixed and upgraded.
- **Existing-codebase evidence:** Inspect real `Set-Cookie` headers through proxies and browsers for every environment and authentication flow.

### 8.4. Secure cookies

- **SHOULD — engineering rule:** Set the narrowest domain/path and appropriate Secure, HttpOnly, and SameSite attributes; rotate identifiers after authentication or privilege changes and prevent caching of sensitive responses.
- **Production failure mode:** Over-broad cookies leak to sibling hosts, cross-site requests carry ambient authority, or a pre-authentication identifier is fixed and upgraded.
- **Existing-codebase evidence:** Inspect real `Set-Cookie` headers through proxies and browsers for every environment and authentication flow.

### 8.7. Session rotation

- **SHOULD — engineering rule:** Replace the session identifier atomically after authentication, factor elevation, recovery, and other trust-boundary changes while preserving only explicitly allowed session state.
- **Production failure mode:** An attacker-supplied or previously stolen identifier becomes an authenticated or higher-privilege session.
- **Existing-codebase evidence:** Test that old identifiers stop working immediately and concurrent requests cannot resurrect the prior session.

### 8.8. Session fixation

- **SHOULD — engineering rule:** Replace the session identifier atomically after authentication, factor elevation, recovery, and other trust-boundary changes while preserving only explicitly allowed session state.
- **Production failure mode:** An attacker-supplied or previously stolen identifier becomes an authenticated or higher-privilege session.
- **Existing-codebase evidence:** Test that old identifiers stop working immediately and concurrent requests cannot resurrect the prior session.

### 8.14. Concurrent session handling

- **SHOULD — engineering rule:** Use barriers/hooks to force the critical interleaving, repeat across real database isolation, and assert the invariant rather than timing or one response.
- **Production failure mode:** A probabilistic sleep-based test passes while the actual race remains reachable.
- **Existing-codebase evidence:** Instrument the exact read/check/write or lease boundary and run deterministic competing operations.

## 9. Concurrency, transactions, idempotency, and consistency

Challenge consumption, refresh rotation, password reset, recovery-code use, and account linking are atomic compare-and-set operations. Concurrent use must yield one winner and deterministic containment for losers. Do not rely on token expiry to serialize security events; maintain server-side state for revocation, token-family reuse detection, or security-version checks where immediate control is required.

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

Treat provider timeout, email/SMS delay, clock skew, stale keys, duplicate callbacks, and lost responses as normal. A retry must not issue multiple sessions or consume a challenge inconsistently. Recovery and factor removal deserve stricter controls than ordinary login because attackers deliberately target the weakest ceremony.

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

Record security events without credentials: attempted and successful login, challenge lifecycle, factor enrollment/removal, recovery, refresh reuse, revocation, risk decision, and administrative override. Monitor credential stuffing, per-account/IP/device failure velocity, reset abuse, token verification failures, key rotation health, provider latency, and anomalous session creation.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

Roll out new token claims, algorithms, keys, authenticators, and session policies under mixed-version verification. Verifiers should accept old and new formats during a bounded migration, while issuers move first or last according to compatibility. Never remove an old key or hashing scheme before all still-valid credentials/tokens have expired or been migrated.

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
| Authentication / actor | Bind every ceremony to a stable subject or pre-authentication transaction, client/session, purpose, challenge, factor policy, and risk context; session issuance occurs only after all required checks. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Session creation`, `HttpOnly`, `Session hijacking`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Sessions; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Sessions** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Secure cookies**: Set the narrowest domain/path and appropriate Secure, HttpOnly, and SameSite attributes; rotate identifiers after authentication or privilege changes and prevent caching of sensitive responses.
- **MUST** — For **Session rotation**: Replace the session identifier atomically after authentication, factor elevation, recovery, and other trust-boundary changes while preserving only explicitly allowed session state.

### SHOULD

- **SHOULD** — Authentication is a lifecycle of enrollment, verification, use, rotation, recovery, revocation, and audit—not only a login endpoint.
- **SHOULD** — A successful credential check is not sufficient when account status, risk policy, factor freshness, or session policy rejects the login.
- **SHOULD** — Recovery paths are usually weaker than primary authentication and therefore define the effective security level.
- **SHOULD** — Token and session expiry limit exposure but do not by themselves provide revocation or prevent replay.
- **SHOULD** — Authentication responses must resist account enumeration while still being diagnosable internally.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Choose **Database-backed vs distributed-cache session store** according to the stated trade-off: Select based on revocation and durability needs; keep session semantics independent of store.
- **MAY** — Adopt the **Server-side session vs self-contained access token** option that fits the workload and ownership boundary; Use short-lived access tokens with controlled refresh or server-side sessions according to trust boundaries and operational needs.
- **MAY** — Adopt the **Opaque vs JWT access token** option that fits the workload and ownership boundary; Prefer opaque tokens when introspection latency is acceptable; use JWTs for bounded audiences with strict validation and short lifetimes.
- **MAY** — Adopt the **Password vs passwordless/passkey** option that fits the workload and ownership boundary; Offer phishing-resistant authenticators for higher assurance and design recovery before enrollment.

### AVOID

- **AVOID** — Issuing a session before all required factors complete.
- **AVOID** — Accepting JWTs without issuer/audience/algorithm validation.
- **AVOID** — Rotating refresh tokens without reuse detection.
- **AVOID** — Account takeover through weak reset or MFA removal.
- **AVOID** — Credential stuffing amplified by unlimited parallel attempts.
- **AVOID** — Implementing login but omitting recovery, revocation, rotation, and abuse controls.
- **AVOID** — Accepting token library defaults without issuer/audience/type policy.
- **AVOID** — Making challenge redemption non-atomic.

### NEVER

- **NEVER** — Never store plaintext passwords, reusable OTPs, refresh tokens, recovery codes, or reset tokens when a protected verifier can be used.
- **NEVER** — Never accept a token without explicit issuer, audience, type, algorithm/key, and time validation appropriate to that token.
- **NEVER** — Never make recovery or factor removal weaker than the account risk requires.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Test challenge issuance and redemption for missing, altered, expired, cross-purpose, cross-session, replayed, and simultaneous requests.
- [ ] Run synchronized refresh/reset/recovery-code use; prove one winner, token-family containment, and correct audit/notification.
- [ ] Exercise wrong issuer, audience, algorithm, key, token type, temporal claims, and key rotation for every token verifier.
- [ ] Test account enumeration resistance and rate-limit interaction across account, IP, device, tenant, and provider failures.
- [ ] Verify recovery, factor removal, password change, suspension, and logout revoke exactly the intended sessions and credentials.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Issuing sessions before all factors and account-state checks finish.
- Logging tokens, OTPs, reset links, or provider payload secrets.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [004. Authentication](004-authentication.md)
- [006. MFA / Strong Authentication](006-mfa-strong-authentication.md)
- [005. OAuth / Social Authentication](005-oauth-social-authentication.md)
- [003. Identity](003-identity.md)
- [113. Machine-to-Machine Authentication](113-machine-to-machine-authentication.md)
- [114. API Keys](114-api-keys.md)
- 127. Randomness & Token Generation — in the `security-privacy` skill.
- 125. Cleanup Jobs — in the `data-storage` skill.
- 067. Abuse Protection — in the `security-privacy` skill.
- 038. Rate Limiting — in the `resilience-flow-control` skill.
- [009. Users & Account Lifecycle](009-users-and-account-lifecycle.md)
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s003"></a> **[S003] Digital Identity Guidelines.** NIST; 2025; SP 800-63-4. [https://pages.nist.gov/800-63-4/sp800-63.html](https://pages.nist.gov/800-63-4/sp800-63.html) — Tags: identity, authentication, federation, privacy.
- <a id="s005"></a> **[S005] Digital Identity Guidelines: Authentication and Authenticator Management.** NIST; 2025; SP 800-63B-4. [https://pages.nist.gov/800-63-4/sp800-63b.html](https://pages.nist.gov/800-63-4/sp800-63b.html) — Tags: authentication, passwords, mfa, sessions, passkeys.
- <a id="s006"></a> **[S006] Digital Identity Guidelines: Federation and Assertions.** NIST; 2025; SP 800-63C-4. [https://pages.nist.gov/800-63-4/sp800-63c.html](https://pages.nist.gov/800-63-4/sp800-63c.html) — Tags: federation, oidc, assertions.
- <a id="s007"></a> **[S007] Best Current Practice for OAuth 2.0 Security.** IETF; 2025; RFC 9700 / BCP 240. [https://www.rfc-editor.org/rfc/rfc9700.html](https://www.rfc-editor.org/rfc/rfc9700.html) — Tags: oauth, security, tokens, redirects.
- <a id="s008"></a> **[S008] The OAuth 2.0 Authorization Framework.** IETF; 2012; RFC 6749. [https://www.rfc-editor.org/rfc/rfc6749.html](https://www.rfc-editor.org/rfc/rfc6749.html) — Tags: oauth, authorization.
- <a id="s009"></a> **[S009] OAuth 2.0 Bearer Token Usage.** IETF; 2012; RFC 6750. [https://www.rfc-editor.org/rfc/rfc6750.html](https://www.rfc-editor.org/rfc/rfc6750.html) — Tags: oauth, tokens.
- <a id="s010"></a> **[S010] Proof Key for Code Exchange by OAuth Public Clients.** IETF; 2015; RFC 7636. [https://www.rfc-editor.org/rfc/rfc7636.html](https://www.rfc-editor.org/rfc/rfc7636.html) — Tags: oauth, pkce, security.
- <a id="s011"></a> **[S011] OAuth 2.0 Token Revocation.** IETF; 2013; RFC 7009. [https://www.rfc-editor.org/rfc/rfc7009.html](https://www.rfc-editor.org/rfc/rfc7009.html) — Tags: oauth, revocation, tokens.
- <a id="s012"></a> **[S012] OAuth 2.0 Token Introspection.** IETF; 2015; RFC 7662. [https://www.rfc-editor.org/rfc/rfc7662.html](https://www.rfc-editor.org/rfc/rfc7662.html) — Tags: oauth, tokens, introspection.
- <a id="s013"></a> **[S013] JSON Web Token (JWT).** IETF; 2015; RFC 7519. [https://www.rfc-editor.org/rfc/rfc7519.html](https://www.rfc-editor.org/rfc/rfc7519.html) — Tags: jwt, tokens, serialization.
- <a id="s014"></a> **[S014] JSON Web Token Best Current Practices.** IETF; 2020; RFC 8725 / BCP 225. [https://www.rfc-editor.org/rfc/rfc8725.html](https://www.rfc-editor.org/rfc/rfc8725.html) — Tags: jwt, security, tokens.
- <a id="s015"></a> **[S015] OpenID Connect Core 1.0 incorporating errata set 2.** OpenID Foundation; 2023; Core 1.0 Errata 2. [https://openid.net/specs/openid-connect-core-1_0-errata2.html](https://openid.net/specs/openid-connect-core-1_0-errata2.html) — Tags: oidc, oauth, identity, federation.
- <a id="s016"></a> **[S016] Web Authentication: An API for accessing Public Key Credentials Level 3.** W3C; 2026; Candidate Recommendation Snapshot. [https://www.w3.org/TR/webauthn-3/](https://www.w3.org/TR/webauthn-3/) — Tags: webauthn, passkeys, mfa, authentication.
- <a id="s021"></a> **[S021] Application Security Verification Standard.** OWASP; 2025; ASVS 5.0.0. [https://owasp.org/www-project-application-security-verification-standard/](https://owasp.org/www-project-application-security-verification-standard/) — Tags: security, authentication, authorization, validation, logging.
- <a id="s024"></a> **[S024] OWASP Cheat Sheet Series.** OWASP; 2026; Living collection. [https://cheatsheetseries.owasp.org/](https://cheatsheetseries.owasp.org/) — Tags: security, validation, sessions, files, logging, secrets.
