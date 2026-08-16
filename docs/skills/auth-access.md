# Implement Auth & Access Control (`auth-access`)

Production expertise for anything that decides *who you are* and *what you may do*: login flows, credentials, sessions, permissions, and tenant isolation — the features where a first draft quietly becomes a breach.

## What it covers

- email/password, phone, passwordless, magic-link, and OTP login;
- password reset, change, verification, lockout, and account recovery;
- sessions: cookies, rotation, fixation defense, device and concurrent sessions;
- JWTs, opaque tokens, refresh rotation, revocation, reuse detection;
- OAuth 2.0/OIDC social login, account linking, provider outages;
- MFA: TOTP, passkeys/WebAuthn, recovery codes, step-up authentication;
- API keys and service-to-service authentication;
- RBAC/ABAC/ReBAC permissions, ownership checks, impersonation;
- account lifecycle: suspension, deletion, anonymization, merge, export;
- multi-tenant identification, isolation, and cross-tenant leakage prevention;
- internal admin operations with audit trails.

## When to use

Any time the agent is about to write or change code for login, tokens, permissions, user accounts, or tenancy — including "quick" versions. Reset flows, session handling, and permission checks are exactly where shortcut implementations hurt.

## What a run produces

Before code: the token/session/permission rules that apply (lifetime, storage, rotation, revocation), the enumeration and lockout defenses, and the tests that prove each rule. The skill stops the work if a must-rule has no enforcement point — e.g., reset tokens that are reusable, or authorization checked only in the controller.

## Works well with

- `api-contracts` for the endpoints and error responses around auth;
- `security-privacy` for password/token hashing, crypto, and token randomness;
- `resilience-flow-control` for brute-force rate limiting;
- `production-operations` for audit logging and alerting.

## Try it

~~~text
Implement password reset for our API: email link, single use, and it must
not let attackers enumerate accounts. Use auth-access.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/auth-access/SKILL.md)
- Worked example: [password reset end to end](../../skills/auth-access/examples/worked-example-password-reset.md)
