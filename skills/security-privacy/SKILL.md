---
name: security-privacy
description: "Use when thinking through, reviewing, changing, or verifying security and privacy controls: secrets, encryption, TLS or PKI, cryptography, hashing, sensitive-data lifecycle, redaction, abuse defense, feature flags, temporary data, or secure randomness. For identity flows use auth-access; for public contract attacks use api-contracts; for whole-system threats use system-architecture-harness."
---

# Think Through Security & Privacy

## Overview

Production guidance for protective controls. Each reference paper captures the failures that audits find late: secrets in config and logs, home-grown crypto, disabled certificate verification, PII without retention or deletion paths, and abuse protections that rate-limit the wrong dimension.

**Core principle:** Controls attach to data and actions, not to layers. Every secret, sensitive field, and privileged action has a lifecycle — generation, use, rotation, redaction, deletion — that must be enforced somewhere concrete.

## Domain Law

```text
NO SECURITY OR PRIVACY CHANGE WITHOUT:
1. the primary paper(s) for the control read in full first;
2. the asset, actor, and trust boundary named before choosing a control;
3. "Existing-codebase checks" run when changing existing protections;
4. every applicable MUST/NEVER mapped to an enforcement point, a test,
   or a documented risk-accepted exception.
```

## When to Use

Use this skill when thinking through, reviewing, changing, or verifying:

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
- Rate-limit mechanics: use `resilience-flow-control` (038).
- Whole-system threat models and zero-trust architecture: use `system-architecture-harness`.
- Untrusted code execution sandboxes for AI: use `ai-agent-system-architecture`.

## Select the Operating Mode

| Mode | Use when | Required result |
|---|---|---|
| **Think** | The safe decision is not settled | requirements, constraints, invariants, risks, alternatives, decision, and validation path |
| **Review** | An artifact, repository, diff, or operating state already exists | evidence separated from assumptions, prioritized findings, and blockers |
| **Change** | Decisions are approved and repository changes are requested | the smallest safe change, compatibility notes, and verification still required |
| **Verify** | A claim needs proof | tests or measurements run, observed evidence, and residual risks |

If the user names a mode, use it. Otherwise infer the mode from intent and state the inference in one sentence. For a combined request, run **Think → Review → Change → Verify** and preserve the trace between phases. Think may stop with a decision; Review may stop with findings. Change must not claim completion before Verify. Verify must never turn a planned or unavailable check into evidence.

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

Use the domain workflow as shared gates, then branch by the selected mode:

- **Think:** answer the questions and stop with a reasoned decision and validation path; do not edit by default.
- **Review:** inspect the available artifact or repository and stop with evidence-backed findings; do not claim changes.
- **Change:** apply only approved decisions, then continue to Verify before claiming completion.
- **Verify:** run the relevant checks, report observed results, and label every unavailable or unrun check.

1. Name the asset, the actors, and the trust boundary; select primary papers (a password-reset flow touches 064 + 127 + 067 + 066).
2. Read the primary papers fully, including attack patterns and common bugs.
3. Answer the paper's pre-implementation questions; label autonomous assumptions and their impact.
4. For existing systems, run the existing-codebase checks: grep for secrets in config/logs, verify verification is not disabled, and map every sensitive field's real retention.
5. Convert each MUST/SHOULD/AVOID/NEVER into an enforcement point (validation, redaction middleware, rotation job, deletion propagation) with a test that proves the negative (secret absent, plaintext absent, verification on).
6. Apply the active mode: stop at a control decision in Think; stop at findings in Review; make the smallest approved safe change in Change; run the paper's negative and lifecycle checks in Verify.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Companion Skills and Standalone Safety

| Type | When | Companion | Missing companion behavior |
|---|---|---|---|
| **Handoff** | Login, session, OAuth, MFA, API key, or permission flow is central | `auth-access` | Limit the answer to protective controls and identify flow ownership missing. |
| **Recommended** | Validation, error leakage, or public security headers change | `api-contracts` | Preserve validation and non-disclosure obligations. |
| **Recommended** | Abuse defense needs throttling mechanics | `resilience-flow-control` | State required multi-dimensional limits without inventing mechanics. |
| **Recommended** | Audit, alerting, rotation, or deletion evidence is required | `production-operations` | State required evidence and label operational depth missing. |

If a companion is unavailable, complete only the safe local control decision, name the missing depth, and recommend the exact technical ID or relevant installation group. Never claim unavailable material was read or weaken least privilege, cryptographic, privacy, or abuse blockers.

## Output Contract

The selected mode is authoritative. Include only applicable fields below; a planned check is a validation path, not verification evidence.

Scale the output to the active mode: Think returns control and lifecycle decisions; Review returns findings; Change returns the repository-aware change plus pending proof; Verify returns observed security and privacy evidence with unrun checks labeled. A combined flow preserves all four phases.

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
