---
name: auth-access
description: "Use when implementing or changing identity, authentication, or authorization code: login, signup, password reset, sessions, cookies, JWT and opaque tokens, refresh-token rotation, OAuth/OIDC social login, MFA, passkeys, API keys, service-to-service auth, RBAC/ABAC/ReBAC permissions, account lifecycle, multi-tenant isolation, or internal admin operations. Loads production implementation papers with MUST/SHOULD/AVOID/NEVER rules, failure modes, and verification checklists to read before writing code. For whole-system architecture design use system-architecture-harness; for AI/agent systems use ai-agent-system-architecture; for API error and versioning contracts use api-contracts; for secrets, cryptography, and token randomness use security-privacy."
---

# Auth & Access Implementation

## Overview

Implementation intelligence for identity, authentication, authorization, and tenancy. Each reference paper is a production checklist of the correctness, security, and lifecycle work that a first-draft implementation misses: token rotation and reuse detection, session fixation, account enumeration, OAuth linking edge cases, permission inheritance, tenant leakage, and admin audit paths.

**Core principle:** Authentication and authorization are invariant-enforcement systems, not login forms. Every identity, credential, session, and permission decision must trace to an enforceable rule at the authoritative data boundary.

## Implementation Law

```text
NO AUTH IMPLEMENTATION WITHOUT:
1. the primary paper(s) for the feature read in full first;
2. the paper's "Questions that must be answered before implementation"
   answered, or each open point labeled as an assumption;
3. "Existing-codebase checks" run when changing an existing system;
4. every applicable MUST mapped to a decision, a test, or a documented
   exception — never silently downgraded.
```

## When to Use

Use this skill when implementing or changing:

- email/password, phone, passwordless, magic-link, or OTP login;
- password reset, change, verification, lockout, and account recovery;
- session management: cookies, rotation, fixation defense, device sessions;
- JWTs, opaque tokens, refresh-token rotation, revocation, reuse detection;
- OAuth 2.0 / OIDC social login, provider account linking, provider outages;
- MFA enrollment, removal, recovery codes, passkeys/WebAuthn, step-up auth;
- API keys and machine-to-machine / service-to-service authentication;
- permissions: roles, RBAC/ABAC/ReBAC, ownership checks, impersonation;
- account lifecycle: suspension, deletion, anonymization, merge, export;
- multi-tenant identification, isolation, quotas, and cross-tenant leakage prevention;
- internal admin operations and privileged tooling.

## When Not to Use

- Designing the architecture of a whole new system: use `system-architecture-harness`.
- Building LLM/agent features: use `ai-agent-system-architecture`.
- API contracts, validation, pagination, error models: use `api-contracts`.
- Secrets storage, cryptography primitives, TLS, token randomness: use `security-privacy` (papers 063, 064, 127).
- Rate limiting and brute-force pacing mechanics: use `resilience-flow-control` (paper 038).

## Required Context Loading

| Situation | Papers |
|---|---|
| Login, signup, logout, password hashing, reset, lockout | [004 Authentication](references/papers/004-authentication.md) |
| OAuth/OIDC flows, social providers, account linking | [005 OAuth / Social Authentication](references/papers/005-oauth-social-authentication.md) |
| TOTP, SMS/email/push MFA, recovery codes, passkeys | [006 MFA / Strong Authentication](references/papers/006-mfa-strong-authentication.md) |
| Sessions, cookies, rotation, fixation, distributed sessions | [007 Sessions](references/papers/007-sessions.md) |
| Identity model, stable IDs, machine identities | [003 Identity](references/papers/003-identity.md) |
| Users vs accounts, merge, suspend, anonymize, delete | [009 Users & Account Lifecycle](references/papers/009-users-and-account-lifecycle.md) |
| Permissions, roles, RBAC/ABAC/ReBAC, ownership checks | [008 Authorization](references/papers/008-authorization.md) |
| Tenant identification, isolation, provisioning, quotas | [010 Multi-Tenancy](references/papers/010-multi-tenancy.md) |
| API key issuance, hashing, scoping, rotation | [114 API Keys](references/papers/114-api-keys.md) |
| Service-to-service and workload authentication | [113 Machine-to-Machine Authentication](references/papers/113-machine-to-machine-authentication.md) |
| Admin tooling, impersonation, privileged operations | [112 Internal Admin Operations](references/papers/112-internal-admin-operations.md) |

## Workflow

1. Identify the feature and select the primary paper from the table; load papers for every touched boundary (a login change usually touches 004 + 007 + 127 mechanics).
2. Read the primary paper fully, including its normative requirements and failure modes.
3. Answer the paper's "Questions that must be answered before implementation." When working autonomously, choose conservative assumptions, label them, and show how each answer changes the implementation.
4. For existing code, run the paper's "Existing-codebase checks": map every entry point (APIs, jobs, admin tools, tests), trace identity/tenant propagation, and find bypass paths before editing.
5. Convert each MUST/SHOULD/AVOID/NEVER into an implementation decision with an enforcement point (constraint, middleware, policy check, or test), plus migration and rollout notes for existing users.
6. Implement the smallest safe slice; carry the paper's "Testing and verification requirements" into the test plan.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Boundary Map

| If the task also involves | Also use |
|---|---|
| Request middleware, validation, error responses | `api-contracts` (011, 012, 013) |
| Token/password hashing, secret storage, CSPRNG use | `security-privacy` (063, 064, 127) |
| Brute-force pacing, lockout windows, rate limits | `resilience-flow-control` (038) |
| Login audit trails and alerting | `production-operations` (060, 139) |
| Session/cache storage semantics | `data-storage` (021) or `resilience-flow-control` (037) |
| Password/credential schema migrations | `migration-evolution` (029, 030) |

## Output Contract

1. **Papers consulted** — numbers and the sections relied on.
2. **Assumptions and unanswered questions** — labeled, with their design impact.
3. **Rule-to-decision map** — each applicable MUST/SHOULD → decision, enforcement point, and test.
4. **Failure modes addressed** — from the paper's failure matrix and common-bug lists (enumeration, fixation, reuse, leakage, bypass).
5. **Verification evidence** — tests mapped to the paper's verification checklist.
6. **Migration and rollout notes** — for existing users, sessions, tokens, and tenants.

## Stop Conditions

Stop and revise when any of these appears:

- code is written before the primary paper's pre-implementation questions are answered or labeled;
- credentials, reset tokens, or session IDs generated without a CSPRNG or stored without approved hashing parameters;
- sessions without expiry policy, rotation on privilege change, revocation, and secure cookie attributes;
- OAuth flows without state/nonce and exact redirect-URI validation;
- reset or recovery tokens that are reusable, unexpiring, or enumerable; account enumeration unexamined;
- authorization enforced only in UI, controllers, or a gateway — not at the resource, row, field, and tenant boundary;
- tenant identity missing from any query, cache key, job, event, or file path;
- MFA without recovery paths, rate limits, and step-up policy;
- admin or impersonation actions without immutable audit logging;
- a lockout or abuse control that fails open silently;
- any auth MUST downgraded to a TODO without a documented exception.

## References

Eleven production papers under `references/papers/`: 003 Identity, 004 Authentication, 005 OAuth / Social Authentication, 006 MFA / Strong Authentication, 007 Sessions, 008 Authorization, 009 Users & Account Lifecycle, 010 Multi-Tenancy, 112 Internal Admin Operations, 113 Machine-to-Machine Authentication, 114 API Keys. Cross-domain pointers inside the papers name the sibling skill to activate.

Worked example: [password reset end to end](examples/worked-example-password-reset.md).
