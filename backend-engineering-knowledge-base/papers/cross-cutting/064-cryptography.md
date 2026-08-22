---
paper_number: 64
title: "Cryptography"
layer: cross-cutting
domain_profile: security
corpus_version: 1.0.0
verified_through: 2026-08-17
canonical_source: "original/Pasted text.txt"
subtopic_count: 15
status: production-engineering-reference
---

# 064. Cryptography

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It is not a framework tutorial. It describes the hidden correctness, security, compatibility, failure, and operational work behind a production implementation.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense when written in capitals. See [S001](#s001) and [S002](#s002). Research and standards were checked through **2026-08-17**; provider behavior and living specifications must be rechecked before implementation.

## 1. Executive engineering summary

**Cryptography** exists to reduce exploitable trust, privilege, and data exposure across inputs, components, operators, and dependencies. A basic implementation usually handles the visible happy path; a production implementation must also preserve identity and ownership, valid state transitions, race-safe invariants, failure recovery, compatibility, and bounded operations.

Map trust boundaries, assets, attackers, privileges, data flows, and failure modes before selecting controls. Enforce least privilege in the component that owns the resource; edge filtering, WAFs, and gateways are supplementary. Treat every external, model-generated, cached, imported, or administrator-supplied value as untrusted at its use context.

The most important evidence base for this paper includes [S021](#s021) [S022](#s022) [S023](#s023) [S077](#s077). The source list at the end distinguishes standards, official product documentation, research, and production engineering guidance.

### What an experienced engineer notices first

- Every external input—including data from trusted providers, queues, files, and internal services—crosses a trust boundary.
- Least privilege applies to identities, data fields, network paths, secrets, and administrative tooling.
- Secure defaults must remain safe when configuration is missing, stale, or partially deployed.
- Cryptographic protection fails when keys, randomness, nonces, algorithms, or lifecycle management are wrong.
- Security controls require abuse-case tests and operational detection, not only happy-path unit tests.

## 2. Scope and terminology map

The canonical topic list requires this paper to cover the following concerns. They are grouped only to expose relationships; no listed subtopic is omitted.

### State and lifecycle

**Key rotation**.

### Security, privacy, and abuse

**Hashing**, **Password hashing**, **Salting**, **Encryption at rest**, **Encryption in transit**, **Symmetric encryption**, **Asymmetric encryption**, **Key derivation**, **Signing**, **Verification**, **Randomness**, **Nonces**, **Envelope encryption**, **Avoiding custom crypto**.

### Boundary of the paper

This paper treats **Cryptography** as a production subsystem or reusable reasoning primitive. It covers semantics, ownership, persistence, APIs, security, concurrency, distributed behavior, operations, evolution, and verification. Framework syntax and large implementation listings are intentionally excluded.

## 3. Correctness model and production invariants

The primary correctness question is not “does the happy path work?” but “can every accepted operation be explained as a legal transition that preserves the authoritative invariants under duplication, concurrency, timeout, crash, and mixed versions?” [S021](#s021) [S022](#s022) [S023](#s023) [S077](#s077)

1. **Invariant 1:** Every external input—including data from trusted providers, queues, files, and internal services—crosses a trust boundary.
2. **Invariant 2:** Least privilege applies to identities, data fields, network paths, secrets, and administrative tooling.
3. **Invariant 3:** Secure defaults must remain safe when configuration is missing, stale, or partially deployed.
4. **Invariant 4:** Cryptographic protection fails when keys, randomness, nonces, algorithms, or lifecycle management are wrong.
5. **Invariant 5:** Security controls require abuse-case tests and operational detection, not only happy-path unit tests.

Additional topic-specific invariants:

1. **Key separation:** A key is bound to exactly one algorithm, purpose (encryption/MAC/signature/derivation), and protocol context; derive independent keys with HKDF and domain-separation labels instead of reusing one secret across purposes.
2. **Nonce uniqueness:** For any AEAD construction (AES-GCM, ChaCha20-Poly1305), a (key, nonce) pair MUST never protect two different messages — including across process restarts, concurrent workers, and clock rollbacks. Random-nonce regimes inherit NIST SP 800-38D's collision bounds; deterministic counter management or XSalsa/XChaCha variants cover the rest.
3. **Authenticated encryption only:** Confidentiality without integrity is not encryption; every ciphertext carries authentication (AEAD or encrypt-then-MAC).
4. **Verifiable algorithm identity:** Every stored ciphertext, wrapped key, or signed token records algorithm, parameters, and key version so verification fails closed on unknown or deprecated combinations.
5. **Constant-time secrets handling:** MAC/password/token comparisons run through constant-time library functions, never application equality checks.
6. **No silent downgrade:** Verification rejects unknown algorithms, missing signatures, and expired keys with explicit errors.
## 4. Architecture decisions and conflicting approaches

There is no universally correct mechanism. The design must select an option from the actual invariants, workload, trust boundary, failure tolerance, and operating model—not from fashion.

| Decision | Trade-off | Production guidance |
|---|---|---|
| Hashing vs encryption | Hashing verifies without recovery; encryption preserves recoverability and therefore key-access risk. | Use one-way verifiers for credentials/tokens where plaintext recovery is unnecessary. |
| Prevent vs detect/respond | Prevention reduces incidents but no control is perfect; detection without prevention leaves easy exploit paths. | Layer preventive controls with detection, containment, and recovery. |
| Central gateway vs service-local controls | Gateways provide consistency but cannot understand all resource semantics; local checks know context but can drift. | Enforce coarse controls at the edge and object/action controls in the owning service. |
| Encryption field-level vs storage-level | Storage encryption protects media; field-level encryption narrows exposure but complicates query, rotation, and indexing. | Use field-level protection for high-impact data with a clear key and access model. |
| Block vs challenge vs observe | Blocking stops abuse but creates false positives; challenge adds friction; observe gathers evidence. | Stage controls by confidence and impact, with emergency switches. |

### Decision discipline

- Record the chosen approach, rejected alternatives, workload assumptions, and rollback trigger.
- Distinguish a **semantic requirement** from a provider or framework feature that merely helps implement it.
- Prefer one authoritative owner. When two systems temporarily coexist, document read/write precedence and reconciliation.
- Count operational costs: migrations, incident response, observability, security review, capacity, and on-call burden.

## 5. Ownership, state, and lifecycle

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

## 6. Data model and API implications

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

## 7. Subtopic-by-subtopic implementation intelligence

Each subsection answers three questions: what rule must be implemented, what fails in production, and what an agent must inspect in an existing codebase before changing it.

### 7.1. Hashing

- **MUST — engineering rule:** Match the hash function to the job: SHA-256/SHA-3/BLAKE3 for integrity and content addresses; HMAC-SHA-256 when the value must be unforgeable or when hashing secrets into lookup indices; password-hash functions (Argon2id) only for credentials. Never build MACs as `hash(secret || message)`—raw Merkle–Damgård constructions (MD5, SHA-1, SHA-256) are vulnerable to length-extension; use HMAC.
- **Production failure mode:** Token lookup implemented as `SHA-256(token)` is fine; "API signature" implemented as raw `sha256(secret+payload)` is forgeable via length extension. Hashing without recording the algorithm/version makes later migration undetectable corruption.
- **Existing-codebase evidence:** Grep for `md5|sha1` (broken for security uses), for hash constructions concatenating secrets, and for digest comparisons using `==` instead of constant-time compare.

### 7.2. Password hashing

- **MUST — engineering rule:** Use Argon2id with OWASP-floor parameters (minimum m=19 MiB, t=2, p=1; raise toward ~50–100 ms verify latency on production hardware). Fallbacks: scrypt (N=2^17, r=8, p=1), bcrypt (cost ≥10, aware of its 72-byte input limit), or PBKDF2-HMAC-SHA-256 ≥600,000 iterations where FIPS-140 compliance requires it. Store the PHC-format string (`$argon2id$v=19$m=19456,t=2,p=1$...`) so parameters travel with the hash. Enforce NIST SP 800-63B-4 verifier rules at the policy layer: minimum 15 characters for single-factor use, support at least 64 characters, no composition rules, no periodic rotation, blocklist screening against breached/common passwords.
- **Production failure mode:** Fast hashes (MD5/SHA-256) turn a database leak into cracked credentials within hours. A bcrypt 72-byte truncation silently makes long passphrases equal to their prefix. Composition rules and forced rotation push users toward predictable patterns—the exact behavior SP 800-63B-4 prohibits. Missing rehash-on-login strands users on legacy parameters forever.
- **Existing-codebase evidence:** Inspect the stored format for algorithm and parameter visibility; benchmark verify latency under production concurrency (memory-hard hashes × concurrent logins exhaust RAM); test legacy-parameter upgrade on successful login; confirm reset flows invalidate old tokens and resist enumeration.

### 7.3. Salting

- **MUST — engineering rule:** Every password hash carries a unique per-record random salt (modern formats include it). Salts are not secrets—they defeat precomputation and prevent cross-user duplicate detection. A pepper (global secret, stored in KMS/HSM, applied as HMAC over the stored hash) adds defense-in-depth against database-only compromise; document that pepper rotation forces password resets because verification needs the old pepper.
- **Production failure mode:** A shared static salt across records reintroduces rainbow tables and reveals shared passwords ("these 500 accounts have identical hashes"). A pepper stored next to the database (same backup, same dump) provides zero additional protection while complicating recovery.
- **Existing-codebase evidence:** Confirm per-record salts are actually unique at scale (query for duplicate hashes); check whether any "salt" is hardcoded in source or configuration; if peppering exists, verify key custody is separate from database backups.

### 7.4. Encryption at rest

- **MUST — engineering rule:** Layer deliberately. Storage-engine encryption (TDE, disk/volume encryption) protects against media theft and off-host storage compromise but does nothing once the database process can read the data—it does not constrain a DBA, SQL injection, or a compromised application. Field-level/application-layer encryption with envelope keys (DEK per record or per tenant, wrapped by KEKs in KMS/HSM) protects data from anyone lacking key access; accept that it breaks range queries and index selectivity on protected columns (store deterministic subkeys or blind indexes for equality lookup).
- **Production failure mode:** Teams enable RDS/disk encryption and mark PII "encrypted," then a SQL injection exfiltrates plaintext. Deterministic field encryption used to preserve searchability leaks equality patterns (same ciphertext ⇔ same plaintext); that trade-off must be a recorded decision, not an accident.
- **Existing-codebase evidence:** Distinguish which layers encrypt what; check whether encrypted columns are also indexed in plaintext anywhere (sort keys, foreign keys, logs of query plans); verify key access is separate from database access.

### 7.5. Encryption in transit

- **MUST — engineering rule:** TLS 1.2 minimum, TLS 1.3 preferred (RFC 9325 baseline); never disable certificate/hostname validation—not for self-signed internal endpoints, not in dev (use a real internal CA instead). Service-to-service traffic inside the cluster/network still uses TLS: network position is not trust. mTLS adds client-certificate identity where workload identity platforms (SPIFFE/SPIRE, service mesh) are unavailable.
- **Production failure mode:** `rejectUnauthorized: false` / `InsecureSkipVerify: true` committed for a staging endpoint ships to production and converts every downstream hop into an active-MitM target. TLS terminated at the load balancer with plaintext hops behind it means internal compromise reads all traffic.
- **Existing-codebase evidence:** Grep for certificate-verification disable flags and custom trust stores; inventory which hops are plaintext; check certificate rotation automation and expiry monitoring (see paper 065).

### 7.6. Symmetric encryption

- **MUST — engineering rule:** AES-256-GCM or ChaCha20-Poly1305, via the platform's AEAD API. AES-GCM nonces are 96 bits and MUST be unique per key; with random nonces keep total encryptions per key well under NIST SP 800-38D's 2^32 bound, or derive nonces deterministically from a counter persisted with the key. Prefer XChaCha20-Poly1305 when only random nonces are feasible. Never ECB mode; never raw CBC/CTR output without authentication; CBC is acceptable only inside vetted compositions (encrypt-then-MAC) if AEAD is genuinely unavailable.
- **Production failure mode:** GCM nonce reuse is catastrophic and silent: repeated (key, nonce) pairs expose plaintext XOR relationships and enable GHASH forgery—attackers can often recover the authentication subkey and forge arbitrary ciphertexts. Counter-based nonce schemes break under concurrent writers unless the counter allocation is atomic. Encrypting without authentication invites bit-flipping attacks on payment flags and authorization fields.
- **Existing-codebase evidence:** Search for `ECB`, `DES`, `RC4`, `AES-CBC` without MAC, manual nonce construction (`counter++` in memory after restart = reuse), and any code path that can encrypt the same (key, nonce) twice; verify decryption rejects tampered ciphertexts with a generic error (no padding-oracle distinctions).

### 7.7. Asymmetric encryption

- **MUST — engineering rule:** RSA encryption only with OAEP padding (≥2048-bit keys; PKCS#1 v1.5 padding is prohibited except unavoidable legacy interop—Bleichenbacher-style padding oracles made it historically fatal). Prefer ECIES-style hybrid schemes or direct symmetric encryption where applicable. Signatures: RSA-PSS or Ed25519 or ECDSA P-256. Post-quantum: track hybrid key exchange (e.g., X25519+ML-KEM) for long-confidentiality data, but do not deploy standalone PQ primitives ahead of standards maturity.
- **Production failure mode:** ECDSA nonce reuse or biased nonces leak the private key algebraically (one repeated k suffices)—Ed25519's deterministic signing removes this class. Raw RSA (`RSA/ECB/PKCS1`) in Java defaults is textbook-padding-vulnerable. Small exponent e=3 without proper padding enables broadcast attacks.
- **Existing-codebase evidence:** Identify transformation strings (`RSA/ECB/PKCS1Padding`, `RSA-NONE`); check signature libraries for explicit algorithm pinning; look for hand-managed ECDSA nonces; verify key sizes meet current floors.

### 7.8. Key derivation

- **SHOULD — engineering rule:** Derive purpose-specific keys with HKDF (extract-then-expand) using distinct info/context labels—one master secret becomes independent keys for encryption, MAC, session, and identifier purposes. Password-derived keys go through memory-hard KDFs (Argon2id), not bare PBKDF2-SHA256 with low iterations, and never through a plain hash.
- **Production failure mode:** Using the same derived key for AES-GCM and HMAC-SHA across two protocols enables cross-protocol forgery. HKDF misuse—skipping the salt on low-entropy input, reusing the same info label everywhere—silently collapses key separation.
- **Existing-codebase evidence:** Find every place a master/shared secret is consumed directly as a key; check for `hash(secret)` standing in for a KDF; verify context labels differ per purpose and protocol version.

### 7.9. Signing

- **SHOULD — engineering rule:** Define exactly which bytes are signed: canonicalize first (JSON canonicalization, sorted keys, fixed encodings), then sign; include algorithm, key id, timestamp, and audience inside the signed payload so verifiers can reject confusion attacks. Pin accepted algorithms at verification—JWT `alg` header values are attacker-controlled input, not metadata (HS256/RS256 confusion and `alg:none` were both exploitable classes).
- **Production failure mode:** Signing serialized JSON then transmitting differently-serialized JSON invalidates signatures nondeterministically. Accepting multiple algorithms "for compatibility" lets an attacker downgrade a token family. Unsigned timestamps allow replay beyond intended windows.
- **Existing-codebase evidence:** Locate canonicalization before signing; check webhook verifiers bind method/path/timestamp/body; confirm JWT libraries have `algorithms` pinned explicitly rather than inferred from the token.

### 7.10. Verification

- **MUST — engineering rule:** Verify before trusting, fail closed, and compare in constant time (library `verify()` functions and constant-time equals—never `==` on digests or MACs). Reject unknown algorithms, unknown critical headers/extensions, expired keys, and wrong audiences/key ids explicitly. Treat any verification bypass flag as a vulnerability, not an option.
- **Production failure mode:** Early-return-on-error patterns that fall through to "accept" on unexpected exception types; timing side channels from byte-compare loops; accepting tokens signed by a key belonging to a different environment (staging keys verifying production tokens when keystores are shared).
- **Existing-codebase evidence:** Trace each trust decision to a preceding successful verification call; grep for try/catch blocks swallowing verification errors; check environment separation of keys and keystores.

### 7.11. Randomness

- **MUST — engineering rule:** All security-relevant randomness comes from the OS CSPRNG (`crypto/rand`, `os.urandom`, `getRandomValues`, `SecureRandom`). Session identifiers, API keys, reset tokens, and nonces need ≥128 bits of entropy. PRNG seeds are never derived from time, PIDs, or user input.
- **Production failure mode:** `Math.random()`/`rand()` seeded predictably produces guessable "random" tokens—enumerable sessions and forgeable resets. Truncating UUIDs or base64 strings to shorter tokens silently reduces entropy below brute-force floors.
- **Existing-codebase evidence:** Grep for non-CSPRNG sources feeding token generation; compute actual entropy of generated identifiers; check for modulo-bias introductions (`rand() % n` over skewed ranges).

### 7.12. Nonces

- **MUST — engineering rule:** Each cryptographic construction defines its own nonce discipline: GCM 96-bit uniqueness per key (deterministic counters require crash-safe persistence; random draws require collision bounds); challenge-response protocols require server-generated unpredictable challenges with replay caches; OAuth/OIDC `nonce` binds ID tokens to authentication sessions (RFC 9700).
- **Production failure mode:** In-memory nonce counters reset on process restart and collide across replicas—GCM reuse follows. Replay caches without expiry grow unbounded; caches keyed only by request ID miss duplicated deliveries carrying fresh IDs.
- **Existing-codebase evidence:** Determine nonce generation strategy per cipher instance; verify counter persistence survives restarts and coordinates across replicas; check replay-protection TTLs and storage growth.

### 7.13. Key rotation

- **SHOULD — engineering rule:** Version everything: key IDs in ciphertexts/token headers, overlapping validity windows (new key signs/wraps immediately; old key verifies/decrypts until consumer lag expires), and scheduled rotation rehearsed like deployments. Rotation of KEKs is cheap (rewrap DEKs); rotating data keys means re-encryption at data scale—plan it as a backfill job with progress tracking.
- **Production failure mode:** Rotation without dual-key acceptance causes a mass-invalidations outage (all outstanding sessions/tokens die at cutover). Revocation propagation delays mean revoked keys still verify downstream for the cache TTL—define and measure that window.
- **Existing-codebase evidence:** Check whether stored artifacts identify their key version; simulate rotate-under-load; verify revocation reaches every verifier within the stated bound and audit who read which key versions (KMS logs).

### 7.14. Envelope encryption

- **MUST — engineering rule:** Data keys (DEKs) encrypt data locally; key-encryption keys (KEKs) in KMS/HSM wrap DEKs; wrapped DEKs travel with the ciphertext. Cache plaintext DEKs only with bounded TTL and local-memory scope. Design KMS-outage behavior explicitly: writes fail closed; reads may serve from DEK cache but state the staleness/retry contract. Per-tenant KEKs make cross-tenant blast radius structurally impossible—at cost of key-count scale and per-tenant rotation.
- **Production failure mode:** Plaintext DEKs persisted beside ciphertexts nullify the scheme. Unbounded KMS call rates become throttling incidents during fan-out decrypts (bulk exports, cold-start replays). KMS deletion schedules misread as immediate revoke cause surprise outages days later.
- **Existing-codebase evidence:** Verify DEKs never hit disk/logs; measure KMS QPS at peak vs provider quotas; confirm ciphertext records carry key IDs; test restore-from-backup against current KMS key state (deleted keys = unrecoverable backups).

### 7.15. Avoiding custom crypto

- **MUST — engineering rule:** Compose reviewed primitives and protocols only: platform TLS, libsodium/Tink/platform AEAD APIs, standard JWT/JWE/JWS stacks pinned to safe algorithms. "Custom" includes inventing modes-of-operation, bespoke multi-step secret-sharing, obfuscation presented as encryption, and hand-rolled protocol negotiation. The review bar for adding a primitive: published specification, vetted implementation, active maintenance, and a written reason the standard stack cannot do the job.
- **Production failure mode:** Homegrown "lightweight encryption" (XOR with rotating key, Base64 chains, compression-as-security) appears in legacy code and passes casual review; it fails instantly under known-plaintext analysis. Custom protocol composition (own handshake around solid primitives) reintroduces ordering/negotiation flaws the originals were designed against.
- **Existing-codebase evidence:** Inventory every place cryptography is hand-assembled versus delegated to a reviewed library; classify each as standard composition (acceptable) or novel construction (replace); check dependency versions for known CVEs before judging the design sound.
## 8. Concurrency, transactions, idempotency, and consistency

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

## 9. Security, authorization, privacy, and abuse resistance

Map trust boundaries, assets, attackers, privileges, data flows, and failure modes before selecting controls. Enforce least privilege in the component that owns the resource; edge filtering, WAFs, and gateways are supplementary. Treat every external, model-generated, cached, imported, or administrator-supplied value as untrusted at its use context.

- **MUST** authenticate the actual caller or workload and re-authorize the final action against authoritative tenant, ownership, resource state, and policy context.
- **MUST** reject mass assignment and unknown privileged fields; server-controlled identity, role, tenant, status, price, owner, and audit fields cannot come from an untrusted DTO.
- **MUST** classify and minimize sensitive data; redact logs/traces/errors, restrict exports and support tooling, propagate deletion, and account for backups and derived indexes.
- **SHOULD** combine rate limits with resource budgets, concurrency caps, payload/complexity limits, and detection. IP-only limiting is not an identity or abuse strategy.
- **AVOID** fail-open behavior for high-impact actions when policy, key, revocation, or tenant context is unavailable.

## 10. Distributed failure, retries, timeouts, and recovery

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

## 11. Persistence, constraints, indexes, and caching

- Put race-sensitive invariants in the database or authoritative store. Application checks remain useful for error quality but are not the final guard.
- Design indexes from real query predicates, tenant scope, ordering, soft-delete conditions, and production cardinality. Verify plans and write amplification.
- Keep transactions bounded in time and rows; avoid network/provider calls while locks are held.
- Treat caches, search indexes, analytics, and replicas as derived unless explicitly authoritative. Version them and provide rebuild/reconciliation.
- Retention and cleanup must include references, uniqueness, tombstones, legal hold, audit, external copies, and interrupted-job recovery.

## 12. Observability, audit, and operational control

Log security-relevant outcomes with redaction and tamper resistance; monitor abuse velocity, authorization denials, validation rejects, secret access, key/certificate age, anomaly detections, and control failures. Alerts need runbooks and containment actions, not merely dashboards.

### Minimum signal set

- **Logs:** structured operation, stable route/job/event type, outcome class, correlation/trace/workflow ID, bounded actor/tenant/resource identifiers, and redacted error cause.
- **Metrics:** throughput, success/error classes, latency distribution, saturation, queue/pool depth, retries/timeouts, conflicts/duplicates, stale age, cleanup/reconciliation backlog, and provider dependency health.
- **Tracing:** propagate context across request, database, cache, queue, worker, and provider boundaries; annotate retries and idempotency without recording secrets.
- **Audit:** actor and effective actor, action, target, before/after or transition, policy/version, request/workflow context, result, and immutable/tamper-evident retention according to risk.
- **Runbooks:** detection, scope, diagnosis, containment, rollback/forward-fix, repair/reconciliation, validation, and escalation.

## 13. Compatibility, schema evolution, migration, deployment, and rollback

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

## 14. Cross-cutting implementation matrix

| Concern | Required production decision |
|---|---|
| Authentication / actor | Identify the human, service, device, worker, or anonymous actor for every Cryptography path; do not inherit ambient identity across asynchronous or administrative boundaries. |
| Authorization / ownership | Enforce action, resource, tenant, and state ownership at the authoritative boundary. Include list, bulk, export, background, cache, and recovery paths. |
| Validation / canonicalization | Define syntax, semantic invariants, unknown-field behavior, size/complexity limits, normalization, and error mapping for `Hashing`, `Encryption in transit`, `Key derivation`. |
| Constraints / atomicity | Translate race-sensitive invariants into database constraints, atomic predicates, transaction boundaries, or durable workflow state; document what cannot be atomic. |
| Concurrency / idempotency | Specify behavior for duplicate and concurrent create, update, delete, transition, retry, and recovery operations. Make one logical operation distinguishable from repeated transport attempts. |
| Timeouts / retries | Set a finite end-to-end deadline, classify retryable failures, budget attempts with jitter, and protect ambiguous side effects with idempotency or outcome lookup. |
| Consistency / caching | Name the source of truth, acceptable staleness, read-your-writes needs, cache key dimensions, invalidation/rebuild path, and partition behavior. |
| Security / abuse | Threat-model attacker-controlled identifiers, payloads, ordering, volume, and timing. Apply least privilege, rate/resource controls, secure failure, and sensitive-data redaction. |
| Privacy / retention | Classify data produced or touched by Cryptography; minimize collection, define access and export, propagate deletion, and address logs, derived stores, backups, and legal hold. |
| Observability / audit | Emit bounded structured telemetry with request/workflow IDs and outcome class. Audit security- or state-significant actions with actor, target, result, and policy/version context. |
| Compatibility / migration | Prove old/new readers and writers can coexist. Use additive change and expand-contract; version schemas/state and make backfills resumable and non-overwriting. |
| Deployment / recovery | Define health gates, canary evidence, kill switches where applicable, rollback limits, reconciliation, cleanup ownership, and runbooks for the highest-impact failures. |

## 15. Normative requirements

### MUST

- **MUST** — Define the authoritative owner, invariants, lifecycle, and trust boundary for **Cryptography** before choosing framework or provider mechanisms.
- **MUST** — Enforce authentication, authorization, tenant/data ownership, validation, and database invariants on every entry point, including jobs, admin tools, bulk paths, and recovery.
- **MUST** — Make duplicate, concurrent, timed-out, retried, and partially failed operations converge to a documented valid outcome.
- **MUST** — Use finite deadlines and bounded resource consumption; define what happens when dependencies, caches, telemetry, or providers are unavailable.
- **MUST** — Provide migration, rollback/forward-fix, cleanup, reconciliation, observability, audit, and testing evidence before production release.
- **MUST** — For **Hashing**: Match algorithm to purpose (integrity vs MAC vs password); use HMAC for secret-bearing digests; record algorithm/version with stored values.
- **MUST** — For **Password hashing**: Use Argon2id at OWASP-floor parameters (or documented fallback); store PHC-format parameters with the hash; enforce SP 800-63B-4 verifier rules.
- **MUST** — For **Encryption at rest**: Distinguish storage-level from field-level protection; envelope-encrypt high-impact fields; never index plaintext of encrypted columns without a recorded decision.
- **MUST** — For **Symmetric encryption**: Use AEAD (AES-GCM/ChaCha20-Poly1305) with a per-key nonce-uniqueness regime that survives restarts and concurrency.
- **MUST** — For **Asymmetric encryption**: RSA only with OAEP padding (>=2048-bit); signatures via PSS/Ed25519/P-256; pin accepted verification algorithms.
- **MUST** — For **Verification**: Fail closed on unknown algorithms/expired keys; compare secrets in constant time.

### SHOULD

- **SHOULD** — Every external input—including data from trusted providers, queues, files, and internal services—crosses a trust boundary.
- **SHOULD** — Least privilege applies to identities, data fields, network paths, secrets, and administrative tooling.
- **SHOULD** — Secure defaults must remain safe when configuration is missing, stale, or partially deployed.
- **SHOULD** — Cryptographic protection fails when keys, randomness, nonces, algorithms, or lifecycle management are wrong.
- **SHOULD** — Security controls require abuse-case tests and operational detection, not only happy-path unit tests.
- **SHOULD** — Prefer simple, locally enforceable invariants over coordination-heavy designs.
- **SHOULD** — Use production-shaped tests and operational telemetry to verify assumptions after deployment.

### MAY

- **MAY** — Choose **Hashing vs encryption** according to the stated trade-off: Use one-way verifiers for credentials/tokens where plaintext recovery is unnecessary.
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

## 16. Testing and verification requirements

Passing unit tests is not sufficient. The release needs evidence at the storage, protocol, concurrency, deployment, and operational layers where the failure can actually occur.

- [ ] Build abuse cases from the threat model and test alternate encodings, protocol confusion, privilege changes, and bypass paths.
- [ ] Fuzz untrusted inputs at their use sinks for injection, traversal, SSRF, deserialization, decompression, and output-context failures.
- [ ] Rotate, revoke, expire, and lose keys/secrets/certificates while old and new versions coexist.
- [ ] Inject security-service/cache failure and verify secure failure without unbounded outage or bypass.
- [ ] Review and test logs, backups, traces, crash dumps, support tools, and exports for sensitive-data leakage.
- [ ] **Hashing:** Verify HMAC usage for all secret-bearing digests; confirm no length-extension-vulnerable constructions; test algorithm-version recording on every stored digest.
- [ ] **Password hashing:** Benchmark verify latency on production hardware at realistic concurrency; upgrade legacy-parameter hashes on login; enforce SP 800-63B-4 policy rules (length floors, no composition rules, blocklist).
- [ ] **Symmetric encryption:** Attempt decryption of bit-flipped ciphertexts (must fail generically); audit nonce-generation code paths for restart/concurrency reuse; grep for ECB/DES/RC4.
- [ ] **Asymmetric encryption/signatures:** Confirm OAEP/PSS padding, pinned verification algorithms, and ECDSA nonce discipline or Ed25519 use.
- [ ] **Key rotation/envelope encryption:** Rotate keys under load with dual-key acceptance; revoke a key version and measure propagation time; restore from backup against current KMS state.
- [ ] Verify unauthorized, cross-tenant, malformed, duplicate, concurrent, cancelled, timed-out, dependency-failed, partial-success, stale-data, large-data, and rollback paths.
- [ ] Verify logs, metrics, traces, audit events, alerts, cleanup, reconciliation, and runbook steps using the actual deployed topology.

## 17. Common production bugs and incorrect implementations

- Mass assignment updating privileged fields.
- SSRF through URL fetchers.
- Secret leakage in logs or crash dumps.
- Weak random tokens.
- Security control failing open on dependency error.
- **Hashing:** `hash(secret || message)` signatures forgeable via length extension; unversioned digests that cannot be migrated when an algorithm is deprecated.
- **Password hashing:** Fast hashes or global salts turn a leak into mass cracking; bcrypt 72-byte truncation silently shortens long passphrases; composition rules and forced rotation degrade real-world strength (SP 800-63B-4 prohibits both).
- **Salting:** Static shared salt reintroduces rainbow tables and duplicate-password visibility; pepper stored beside the database adds nothing.
- **Symmetric encryption:** AES-GCM nonce reuse (restart-reset counters, concurrent writers) exposes plaintext relationships and enables forgery; unauthenticated CBC invites bit-flipping on authorization fields.
- **Asymmetric encryption:** Raw RSA/PKCS#1-v1.5 padding oracle exposure; ECDSA nonce reuse recovers the private key; accepting multiple verification algorithms enables downgrade confusion.
- **Key derivation:** One derived key reused across protocols/purposes defeats key separation; missing HKDF salt on low-entropy input weakens extraction.
- **Verification:** Byte-equality comparisons leak timing; exception handlers that fall through to accept convert attacks into compatibility features.
- **Key rotation:** Single-version acceptance causes cutover outages; revocation propagation slower than verifier cache TTL leaves revoked keys trusted.
- **Envelope encryption:** Plaintext DEKs persisted with ciphertexts nullify protection; KMS quota exhaustion during bulk decrypts becomes an availability incident.

## 18. AI coding-agent failure modes

An AI agent is especially likely to:

- Creating custom cryptography or token generation.
- Trusting gateway validation inside services.
- Blacklisting strings instead of validating at the sink.
- Storing secrets in configuration files/logs.
- Adding a permanent fail-open bypass.
- Modify the visible handler while missing a second job, admin, webhook, migration, or legacy path.
- Infer behavior from names or documentation without reading constraints, runtime configuration, provider versions, and existing tests.
- Add abstractions or rebuild working components instead of preserving compatible behavior and fixing the actual gap.
- Claim completion without concurrency/failure tests, migration evidence, real-interface validation, and cleanup ownership.

## 19. Questions that must be answered before implementation

- What exact invariant or user/system promise makes **Cryptography** correct, and which component is authoritative for it?
- Who are the actors, resources, tenants, administrators, background workers, and external providers, and which trust boundaries separate them?
- What are the legal states and transitions, including provisional, failed, cancelled, suspended, expired, restored, and terminal states?
- Which operations can be duplicated, retried, reordered, or run concurrently, and what observable result should each loser/retry receive?
- What is the commit point? Which effects are local, remote, asynchronous, cached, derived, or impossible to roll back atomically?
- What are the end-to-end timeout and retry budgets, and how is an ambiguous outcome resolved without duplicating side effects?
- Which data is sensitive, tenant-scoped, exportable, deletable, retained, audited, or restricted by region/legal hold?
- What compatibility matrix must hold during rolling deployment, old-client use, schema/event evolution, and rollback?
- What load shape, cardinality, skew, payload size, concurrency, and failure rate define production capacity?
- What telemetry, alert, audit event, reconciliation, cleanup job, and runbook prove the feature remains correct after release?
- For **Hashing**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Custom crypto, nonce reuse, weak randomness, key/algorithm confusion, or unauthenticated encryption destroys the intended guarantee.
- For **Encryption at rest**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Custom crypto, nonce reuse, weak randomness, key/algorithm confusion, or unauthenticated encryption destroys the intended guarantee.
- For **Asymmetric encryption**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Resets and gauges are misinterpreted, buckets hide tail latency, or high-cardinality labels overwhelm the backend.
- For **Signing**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Custom crypto, nonce reuse, weak randomness, key/algorithm confusion, or unauthenticated encryption destroys the intended guarantee.
- For **Nonces**, what authoritative boundary enforces the rule, and how will the team prove the failure described here cannot occur: Custom crypto, nonce reuse, weak randomness, key/algorithm confusion, or unauthenticated encryption destroys the intended guarantee.
- What attacker-controlled input reaches which privileged sink, and what is the secure failure mode?

## 20. Existing-codebase checks before changing anything

- [ ] Map every entry point for **Cryptography**: public/internal APIs, middleware, jobs, event handlers, migrations, admin tools, CLIs, scripts, and tests.
- [ ] Trace data from untrusted input to validation, authorization, domain logic, persistence, cache/index, message/event, external side effect, response, logs, and audit.
- [ ] Identify the actual source of truth and all derived copies; record ownership, freshness, deletion propagation, and reconciliation.
- [ ] Inspect database constraints, indexes, isolation settings, atomic update predicates, transaction wrappers, and retry behavior rather than relying on repository names.
- [ ] Search for duplicated implementations, bypass paths, feature flags, legacy compatibility branches, TODOs, incident fixes, and environment-specific behavior.
- [ ] Read deployment manifests, configuration schemas, secret injection, probes, resource limits, shutdown grace periods, and migration ordering.
- [ ] Check existing API/event schemas and real client/consumer usage before renaming fields, changing defaults, strengthening validation, or altering errors.
- [ ] Review telemetry and runbooks to learn current failure modes, latency, scale, and operational ownership before proposing architecture changes.
- [ ] Run the existing suite and targeted production-like probes before edits; preserve unrelated behavior and capture a baseline for correctness and performance.
- [ ] **Hashing:** Review against a cryptographic design document and test key rotation, corruption, wrong context/key, entropy failure, and legacy ciphertext.
- [ ] **Salting:** Locate every implementation path for salting, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Symmetric encryption:** Estimate label cardinality from production dimensions and test dashboards/alerts through restart, scale-out, and missing-data conditions.
- [ ] **Key derivation:** Locate every implementation path for key derivation, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Verification:** Locate every implementation path for verification, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] **Key rotation:** Scan artifacts/logs, rotate under load, revoke the old value, and verify every consumer refreshes without restart assumptions.
- [ ] **Avoiding custom crypto:** Locate every implementation path for avoiding custom crypto, compare behavior across APIs, jobs, migrations, and admin tooling, and add evidence for normal, invalid, duplicate, concurrent, timed-out, and recovery cases.
- [ ] Search logs, traces, metrics, backups, support tools, and error reports for sensitive fields and bypasses.

## 21. Knowledge graph relationships

This paper depends on or constrains the following papers. These links are implementation relationships, not merely topical similarity.

- [127. Randomness & Token Generation](../primitives/127-randomness-and-token-generation.md) — layer: `primitives`; profile: `security`.
- [063. Secrets Management](063-secrets-management.md) — layer: `cross-cutting`; profile: `security`.
- [065. TLS / PKI](065-tls-pki.md) — layer: `cross-cutting`; profile: `security`.
- [061. Security Fundamentals](061-security-fundamentals.md) — layer: `cross-cutting`; profile: `security`.
- [113. Machine-to-Machine Authentication](../systems/113-machine-to-machine-authentication.md) — layer: `systems`; profile: `authentication`.
- [114. API Keys](../systems/114-api-keys.md) — layer: `systems`; profile: `authentication`.
- [006. MFA / Strong Authentication](../systems/006-mfa-strong-authentication.md) — layer: `systems`; profile: `authentication`.
- [144. Untrusted Code Execution](../systems/144-untrusted-code-execution.md) — layer: `systems`; profile: `ai`.
- [066. Privacy & Sensitive Data](066-privacy-and-sensitive-data.md) — layer: `cross-cutting`; profile: `security`.
- [062. Web/API Security](062-web-api-security.md) — layer: `cross-cutting`; profile: `security`.
- [049. Webhooks](../systems/049-webhooks.md) — layer: `systems`; profile: `api`.
- [146. Cross-Cutting Implementation Checklist](146-cross-cutting-implementation-checklist.md) — layer: `cross-cutting`; profile: `checklist`.

## 22. Sources and further research

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

---

**Paper metadata:** canonical subtopics: 15; layer: `cross-cutting`; domain profile: `security`; verified through: `2026-08-17`.
