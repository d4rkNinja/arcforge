# 003. Identity

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Identity** exists to represent a person, device, workload, or external principal with stable identifiers while allowing attributes and credentials to change. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

The identity subsystem owns stable subject identifiers, external-identity bindings, merge history, and lifecycle status. Contact attributes, credentials, profiles, and authorization memberships may refer to a subject but must not redefine who that subject is. Separate human, guest, device, service, and workload identities when their assurance, ownership, and lifecycle differ.

The most important evidence base for this paper includes [S003](#s003) [S004](#s004) [S017](#s017) [S043](#s043). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- An identity is not an email address, phone number, display name, credential, or provider access token.
- Stable internal subject identifiers and provider-scoped external subject identifiers must be modeled separately.
- Linking and merging are security-sensitive state transitions because they can transfer authorization, history, and recovery paths.
- Identity records outlive individual authenticators and often outlive individual accounts or tenants.
- Uniqueness rules are contextual: globally unique, tenant unique, provider unique, verified-only unique, and reusable-after-deletion are different policies.

## 2. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Identity** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- Which identifier is stable for the subject, and what evidence permits linking, merging, or transferring contact attributes?

## 3. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Identity**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] Search every foreign key, cache key, token claim, URL, event, and analytics identifier that assumes email/phone/provider data is stable.

## 4. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S003](#s003) [S004](#s004) [S017](#s017) [S043](#s043)

1. **Invariant 1:** An identity is not an email address, phone number, display name, credential, or provider access token.
2. **Invariant 2:** Stable internal subject identifiers and provider-scoped external subject identifiers must be modeled separately.
3. **Invariant 3:** Linking and merging are security-sensitive state transitions because they can transfer authorization, history, and recovery paths.
4. **Invariant 4:** Identity records outlive individual authenticators and often outlive individual accounts or tenants.
5. **Invariant 5:** Uniqueness rules are contextual: globally unique, tenant unique, provider unique, verified-only unique, and reusable-after-deletion are different policies.

## 5. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Contact attribute vs canonical identity | Contact values are convenient lookup handles but mutable, recycled, and sometimes unverified. | Use a stable internal subject and treat contact points as versioned verified attributes. |
| Single identity row vs identity plus credentials/links | A single row is simple but conflates mutable attributes with stable identity and creates sparse provider-specific columns. | Use a stable subject plus separate credentials, provider links, aliases, and memberships in systems with more than one authenticator or tenant. |
| Automatic linking vs explicit linking | Automatic linking reduces friction but can create account takeover when an attribute is unverified, recycled, or provider-controlled. | Require a proof from both sides for sensitive linking; auto-link only under a documented high-confidence trust policy. |
| Merge vs alias | Merge rewrites ownership and history; alias preserves records but adds indirection. | Prefer aliasing or canonical-subject mapping when auditability and rollback matter. |
| Hard global uniqueness vs scoped uniqueness | Global uniqueness simplifies lookup but blocks valid reuse and multi-tenant cases. | Choose uniqueness scope from the identity and recovery threat model, not from ORM convenience. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 6. Ownership, state, and lifecycle

Use explicit states such as `provisional → active → restricted/suspended → recovered`, with terminal or irreversible branches for `merged`, `anonymized`, and `deleted`. Linking, unlinking, deduplication, and merge are privileged state transitions with preconditions and audit history. Preserve aliases or tombstones long enough to prevent stale references and recreated duplicates.

```mermaid
stateDiagram-v2
    provisional --> active --> restricted
    restricted --> active
    active --> suspended
    suspended --> active
    active --> merged
    active --> anonymized
    active --> deleted
```

### Lifecycle rules

- Every state and transition needs an owner, entry preconditions, atomic persistence rule, emitted side effects, audit requirement, timeout/expiry behavior, and recovery path.
- Terminal states must be explicit. “Failed” is rarely sufficient; distinguish retryable, permanently rejected, cancelled, expired, compensated, quarantined, and manual-review outcomes where relevant.
- Transition side effects should be driven from durable state or an outbox, not from best-effort callbacks that can be lost.
- Concurrent transitions must use an expected source state and version/condition so two valid requests cannot produce an impossible combined state.

## 7. Data model and API implications

Every identity lookup contract must state its namespace, stability, uniqueness scope, mutability, and verification semantics. External identifiers are normally keyed by `(issuer, subject)`; email and phone are attributes whose normalized forms, verification evidence, source, and timestamps are separate data. APIs must avoid leaking whether a contact value belongs to an account.

A production representation commonly needs the following fields or equivalent evidence:

- stable internal subject identifier and identity type.
- external bindings keyed by issuer/provider namespace and subject.
- contact attributes with normalized value, verification evidence, source, and timestamps.
- lifecycle/security version, merge survivor/alias history, and deletion/anonymization state.
- tenant memberships, provenance, and immutable identity events where required.

### API implications

- Define absent versus null, normalization, maximum sizes, unknown fields, error codes, and public versus internal detail.
- State the atomicity and idempotency contract for every mutation, including what happens when the response is lost after commit.
- Use stable public identifiers and deterministic ordering; never expose internal storage behavior as an accidental contract.
- Apply authentication, object/field/tenant authorization, rate/resource limits, and sensitive-data filtering consistently to single, list, bulk, export, job, and administrative paths.

## 8. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### Default obligations

These subtopics carry no additional domain-specific rule beyond the default obligation: for each, define owner, inputs, outputs, invariants, lifecycle, failure classification, and a compatibility contract; make the rule enforceable at the narrowest authoritative boundary; and do not accept a framework or provider default without proving it fits the domain.

- **User identity**
- **Internal identity**
- **External identity**
- **Identity providers**
- **Identity linking**
- **Identity merging**
- **Duplicate identities**
- **Identity lifecycle**
- **Anonymous identities**
- **Guest identities**
- **Machine identities**
- **Service identities**

### 8.5. Stable identifiers

- **SHOULD — engineering rule:** Persist the issuer/provider namespace together with the provider's stable subject. Never infer identity from display name or mutable profile attributes.
- **Production failure mode:** Two providers can issue the same subject string, while one provider can change email without changing subject; either mistake creates collision or duplicate accounts.
- **Existing-codebase evidence:** Verify uniqueness on `(issuer, subject)` and test account lookup after provider email/profile changes.

### 8.6. Email as attribute vs identity

- **SHOULD — engineering rule:** Treat this value as mutable, potentially recycled contact data. Bind it to a stable subject identifier and record verification status, verification time, source, and normalization policy.
- **Production failure mode:** Using it as the primary identity silently transfers access when the address or number changes, is recycled, or is reassigned by a provider.
- **Existing-codebase evidence:** Search schemas, foreign keys, caches, JWT claims, and URLs for places where the contact value is used as the canonical user key.

### 8.7. Phone as attribute vs identity

- **SHOULD — engineering rule:** Treat this value as mutable, potentially recycled contact data. Bind it to a stable subject identifier and record verification status, verification time, source, and normalization policy.
- **Production failure mode:** Using it as the primary identity silently transfers access when the address or number changes, is recycled, or is reassigned by a provider.
- **Existing-codebase evidence:** Search schemas, foreign keys, caches, JWT claims, and URLs for places where the contact value is used as the canonical user key.

## 9. Concurrency, transactions, idempotency, and consistency

Identity creation and linking require database uniqueness, not check-then-insert. Concurrent signup, provider callback, invitation acceptance, and account recovery can all target the same person. Merge operations must choose a survivor, redirect references, reconcile sessions and credentials, preserve audit provenance, and be resumable when downstream rewrites fail.

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

Partial identity creation is expected: an external provider may succeed while local profile initialization fails, or a subject row may commit before notifications and defaults. Record a recoverable state and make completion idempotent. Provider profile changes must not create a new local identity; recycled contact points must not transfer account ownership.

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

Audit creation, verification, linking, unlinking, merge, recovery, suspension, anonymization, and deletion with both actor and affected subject. Measure duplicate-candidate rates, failed link attempts, merge repair backlog, verification age, and orphaned external bindings. Keep sensitive contact values out of high-cardinality metrics and ordinary logs.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 14. Compatibility, schema evolution, migration, deployment, and rollback

Identifier migrations require dual lookup and durable aliasing; changing a primary key in place is rarely safe. Add new identity types and attributes additively, retain unknown provider claims, and version normalization rules. Before removing legacy identifiers, prove that caches, tokens, events, files, analytics, and external integrations no longer depend on them.

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
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Identity path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `User identity`, `Stable identifiers`, `Identity linking`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Identity; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 16. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Identity** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Phone as attribute vs identity**: Treat this value as mutable, potentially recycled contact data. Bind it to a stable subject identifier and record verification status, verification time, source, and normalization policy.

### SHOULD

- **SHOULD** — An identity is not an email address, phone number, display name, credential, or provider access token.
- **SHOULD** — Stable internal subject identifiers and provider-scoped external subject identifiers must be modeled separately.
- **SHOULD** — Linking and merging are security-sensitive state transitions because they can transfer authorization, history, and recovery paths.
- **SHOULD** — Identity records outlive individual authenticators and often outlive individual accounts or tenants.
- **SHOULD** — Uniqueness rules are contextual: globally unique, tenant unique, provider unique, verified-only unique, and reusable-after-deletion are different policies.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Choose **Contact attribute vs canonical identity** according to the stated trade-off: Use a stable internal subject and treat contact points as versioned verified attributes.
- **MAY** — Adopt the **Single identity row vs identity plus credentials/links** option that fits the workload and ownership boundary; Use a stable subject plus separate credentials, provider links, aliases, and memberships in systems with more than one authenticator or tenant.
- **MAY** — Adopt the **Automatic linking vs explicit linking** option that fits the workload and ownership boundary; Require a proof from both sides for sensitive linking; auto-link only under a documented high-confidence trust policy.
- **MAY** — Adopt the **Merge vs alias** option that fits the workload and ownership boundary; Prefer aliasing or canonical-subject mapping when auditability and rollback matter.

### AVOID

- **AVOID** — Using mutable email as primary key.
- **AVOID** — Linking accounts solely by matching email.
- **AVOID** — Losing provider subject identifiers during migration.
- **AVOID** — Creating duplicate subjects under concurrent signup.
- **AVOID** — Restoring a deleted identity into another user's reused email.
- **AVOID** — Using email or phone as the user primary key.
- **AVOID** — Linking accounts solely because emails match.
- **AVOID** — Merging rows without rewriting every reference and preserving audit.

### NEVER

- **NEVER** — Never use mutable contact data as the sole canonical identity.
- **NEVER** — Never link or merge identities solely from an unverified matching email/phone.
- **NEVER** — Never discard merge/link provenance needed to explain historical actions.

## 17. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Synchronize duplicate signup/link attempts for the same normalized contact and `(issuer, subject)`; prove one canonical identity and deterministic loser behavior.
- [ ] Change, remove, recycle, or unverify email/phone/provider attributes; verify the stable subject and recovery policy remain correct.
- [ ] Crash identity creation, linking, merge, anonymization, and deletion between each durable step; resume without duplicate or orphan state.
- [ ] Test every lifecycle transition, forbidden transition, stale version, and concurrent suspension/restoration.
- [ ] Trace merge effects across sessions, roles, tenant memberships, files, events, caches, audit, and external integrations.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Ignoring guest/service identity lifecycle.
- Making check-then-create uniqueness decisions.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [009. Users & Account Lifecycle](009-users-and-account-lifecycle.md)
- [005. OAuth / Social Authentication](005-oauth-social-authentication.md)
- [113. Machine-to-Machine Authentication](113-machine-to-machine-authentication.md)
- [004. Authentication](004-authentication.md)
- 060. Audit Logging — in the `production-operations` skill.
- 066. Privacy & Sensitive Data — in the `security-privacy` skill.
- [008. Authorization](008-authorization.md)
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.
- [006. MFA / Strong Authentication](006-mfa-strong-authentication.md)
- [007. Sessions](007-sessions.md)
- [010. Multi-Tenancy](010-multi-tenancy.md)
- [114. API Keys](114-api-keys.md)

## 20. Sources and further research

Primary standards and official documentation are preferred. Research papers and respected production guidance are used where they explain failure semantics or trade-offs not captured by a normative specification. Source versions and provider behavior can change; verify them at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s003"></a> **[S003] Digital Identity Guidelines.** NIST; 2025; SP 800-63-4. [https://pages.nist.gov/800-63-4/sp800-63.html](https://pages.nist.gov/800-63-4/sp800-63.html) — Tags: identity, authentication, federation, privacy.
- <a id="s004"></a> **[S004] Digital Identity Guidelines: Identity Proofing and Enrollment.** NIST; 2025; SP 800-63A-4. [https://pages.nist.gov/800-63-4/sp800-63a.html](https://pages.nist.gov/800-63-4/sp800-63a.html) — Tags: identity, proofing, enrollment.
- <a id="s005"></a> **[S005] Digital Identity Guidelines: Authentication and Authenticator Management.** NIST; 2025; SP 800-63B-4. [https://pages.nist.gov/800-63-4/sp800-63b.html](https://pages.nist.gov/800-63-4/sp800-63b.html) — Tags: authentication, passwords, mfa, sessions, passkeys.
- <a id="s006"></a> **[S006] Digital Identity Guidelines: Federation and Assertions.** NIST; 2025; SP 800-63C-4. [https://pages.nist.gov/800-63-4/sp800-63c.html](https://pages.nist.gov/800-63-4/sp800-63c.html) — Tags: federation, oidc, assertions.
- <a id="s017"></a> **[S017] System for Cross-domain Identity Management: Core Schema.** IETF; 2015; RFC 7643. [https://www.rfc-editor.org/rfc/rfc7643.html](https://www.rfc-editor.org/rfc/rfc7643.html) — Tags: identity, provisioning, schema.
- <a id="s018"></a> **[S018] System for Cross-domain Identity Management: Protocol.** IETF; 2015; RFC 7644. [https://www.rfc-editor.org/rfc/rfc7644.html](https://www.rfc-editor.org/rfc/rfc7644.html) — Tags: identity, provisioning, api.
- <a id="s021"></a> **[S021] Application Security Verification Standard.** OWASP; 2025; ASVS 5.0.0. [https://owasp.org/www-project-application-security-verification-standard/](https://owasp.org/www-project-application-security-verification-standard/) — Tags: security, authentication, authorization, validation, logging.
- <a id="s043"></a> **[S043] Designing Data-Intensive Applications, Second Edition.** Martin Kleppmann and Chris Riccomini / O'Reilly; 2025; 2nd edition. [https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/) — Tags: distributed-systems, databases, consistency, streams.
