---
name: security-privacy
description: "Use when implementing or changing security and privacy controls: secrets management and rotation, encryption at rest and in transit, TLS/PKI configuration and certificate rotation, cryptography primitive selection, password/token hashing, sensitive-data classification and retention, PII minimization and deletion, log redaction, abuse and fraud protection, brute-force and enumeration defense, feature flag security, temporary/expiring data, and secure randomness for tokens and IDs. Loads production implementation papers with MUST/SHOULD/AVOID/NEVER rules, failure modes, and verification checklists to read before writing code. For authentication flows and permissions use auth-access; for API-surface attacks (injection, BOLA, mass assignment) use api-contracts; for whole-system threat modeling use system-architecture-harness."
---

# Security & Privacy Implementation

## Overview

Implementation intelligence for protective controls. Each reference paper captures the failures that audits find late: secrets in config and logs, home-grown crypto, disabled certificate verification, PII without retention or deletion paths, and abuse protections that rate-limit the wrong dimension.

**Core principle:** Controls attach to data and actions, not to layers. Every secret, sensitive field, and privileged action has a lifecycle — generation, use, rotation, redaction, deletion — that must be enforced somewhere concrete.

## Implementation Law

```text
NO SECURITY IMPLEMENTATION WITHOUT:
1. the primary paper(s) for the control read in full first;
2. the asset, actor, and trust boundary named before choosing a control;
3. "Existing-codebase checks" run when changing existing protections;
4. every applicable MUST/NEVER mapped to an enforcement point, a test,
   or a documented risk-accepted exception.
```

## When to Use

Use this skill when implementing or changing:

- secrets: storage, injection, rotation, scoping, and audit;
- encryption at rest/in transit and key management;
- TLS configuration, certificate rotation, and PKI assumptions;
- crypto primitive selection: hashing, MACs, ciphers, nonce management;
- password and token hashing parameters;
- sensitive-data classification, minimization, retention, and deletion propagation;
- log/trace/error redaction and export controls;
- abuse protection: brute force, credential stuffing, enumeration, scraping, fraud;
- feature flag safety and kill switches;
- temporary and expiring data (sessions, tokens, uploads, exports);
- randomness and token generation (IDs, secrets, nonces).

## When Not to Use

- Login/session/OAuth/permission flows: use `auth-access`.
- API-surface attack classes (injection, object-level authorization, mass assignment): use `api-contracts` (062 pairs here).
- Rate-limit mechanism implementation: use `resilience-flow-control` (038).
- Whole-system threat models and zero-trust architecture: use `system-architecture-harness`.
- Untrusted code execution sandboxes for AI: use `ai-agent-system-architecture`.

## Required Context Loading

| Situation | Papers |
|---|---|
| Threat vocabulary, trust boundaries, least privilege | [061 Security Fundamentals](references/papers/061-security-fundamentals.md) |
| Injection, object-level authz, mass assignment, replay | [062 Web/API Security](references/papers/062-web-api-security.md) |
| Secret storage, injection, rotation, scoping | [063 Secrets Management](references/papers/063-secrets-management.md) |
| Primitives, nonce/IV handling, password hashing | [064 Cryptography](references/papers/064-cryptography.md) |
| TLS setup, verification, certificate lifecycle | [065 TLS / PKI](references/papers/065-tls-pki.md) |
| Classification, minimization, retention, deletion | [066 Privacy & Sensitive Data](references/papers/066-privacy-and-sensitive-data.md) |
| Brute force, stuffing, enumeration, fraud, scraping | [067 Abuse Protection](references/papers/067-abuse-protection.md) |
| Flag safety, kill switches, exposure control | [068 Feature Flags](references/papers/068-feature-flags.md) |
| Expiring tokens, temp files, purge paths | [126 Temporary Data](references/papers/126-temporary-data.md) |
| CSPRNG use, token entropy, ID unpredictability | [127 Randomness & Token Generation](references/papers/127-randomness-and-token-generation.md) |

## Workflow

1. Name the asset, the actors, and the trust boundary; select primary papers (a password-reset flow touches 064 + 127 + 067 + 066).
2. Read the primary papers fully, including attack patterns and common bugs.
3. Answer the paper's pre-implementation questions; label autonomous assumptions and their impact.
4. For existing systems, run the existing-codebase checks: grep for secrets in config/logs, verify verification is not disabled, and map every sensitive field's real retention.
5. Convert each MUST/SHOULD/AVOID/NEVER into an enforcement point (validation, redaction middleware, rotation job, deletion propagation) with a test that proves the negative (secret absent, plaintext absent, verification on).
6. Implement the smallest safe slice; carry the paper's verification checklist into the test plan and code review criteria.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Boundary Map

| If the task also involves | Also use |
|---|---|
| Login, sessions, permissions | `auth-access` (004, 007, 008) |
| Request validation and error leakage | `api-contracts` (012, 013) |
| Throttling mechanics for abuse defense | `resilience-flow-control` (038, 067 policy) |
| Audit events for privileged actions | `production-operations` (060) |
| Sensitive schema/retention design | `data-storage` (033) |
| Compliance/residency architecture | `production-operations` (133) |

## Output Contract

1. **Papers consulted** — numbers and the sections relied on.
2. **Asset/actor/boundary map** — what is protected, from whom, and where the control sits.
3. **Assumptions and unanswered questions** — labeled, with their design impact.
4. **Rule-to-decision map** — each applicable MUST/NEVER → control, enforcement point, and negative test.
5. **Failure modes addressed** — leaked secrets, disabled verification, weak randomness, unreached deletion, wrong-dimension limits.
6. **Verification evidence** — redaction checks, rotation drills, deletion propagation, entropy review.

## Stop Conditions

Stop and revise when any of these appears:

- code is written before the asset and trust boundary are named;
- secrets, tokens, passwords, or PII committed, logged, or returned in errors by default;
- custom cryptography, fixed nonces/IVs, or primitives chosen without the paper's guidance;
- TLS/certificate verification disabled or skipped "for dev" without an environment-gated exception;
- tokens or IDs generated without a CSPRNG or with insufficient entropy for their scope;
- sensitive data without classification, retention, and a deletion path that reaches derived stores and backups;
- temporary data with no expiry or purge job;
- abuse controls that rate-limit only IPs while the attack dimension is accounts, tenants, or payment instruments;
- a security control that fails open silently;
- feature flags without a kill switch or with unreviewed production exposure;
- any security MUST/NEVER downgraded to a TODO without a documented, risk-accepted exception.

## References

Ten production papers under `references/papers/`: 061 Security Fundamentals, 062 Web/API Security, 063 Secrets Management, 064 Cryptography, 065 TLS / PKI, 066 Privacy & Sensitive Data, 067 Abuse Protection, 068 Feature Flags, 126 Temporary Data, 127 Randomness & Token Generation. Cross-domain pointers inside the papers name the sibling skill to activate.

Worked example: [debugging without leaking credentials](examples/worked-example-secrets-and-redaction.md).
