# Worked example: debugging auth failures without leaking credentials

> Calibration artifact: this shows the shape and depth a run of the `security-privacy` skill should produce. It is illustrative, not exhaustive; the papers remain authoritative.

**Request (as a user would phrase it):**

> Debug auth failures by logging full request bodies, including passwords and tokens, at info level in production.

## Papers consulted

- [066 Privacy & Sensitive Data](../references/papers/066-privacy-and-sensitive-data.md) — classification, minimization
- [063 Secrets Management](../references/papers/063-secrets-management.md) — secret lifecycle
- [067 Abuse Protection](../references/papers/067-abuse-protection.md) — what attackers learn from logs
- 056 Logging — in the `production-operations` skill
- 004 Authentication — in the `auth-access` skill, for the underlying failures

## Assumptions (labeled)

- **A1 (assumption):** the actual debugging goal is distinguishing bad-password from unknown-account failures. *If the goal is broader:* a scoped, time-bounded debug mode may be justified — never default info-level bodies.
- **A2 (assumption):** logs ship to a shared platform with broad internal read access and 90-day retention. *If false:* retention and access controls for the debug channel must match its sensitivity.

## Pre-implementation questions answered

- **What is the asset?** User credentials, session tokens, and the account-existence metadata implicit in differentiated errors (paper 066).
- **Why is the request rejected as stated?** Secrets in logs at info level become part of the blast radius of every log consumer, exporter, and support workflow — and remain after the debugging session ends (papers 063, 066 MUST).
- **What serves the debugging goal?** Structured outcome codes (`invalid_credentials`, `unknown_account` internal-only), correlation IDs, and hash prefixes of tokens (never the token) — enough to reconstruct failure patterns (paper 067).
- **Escape hatch for deep debugging?** Opt-in per-request debug flag, admin-authorized, 15-minute TTL, redacting serializer, separate retention, audit event on use (papers 063, 066).
- **Existing exposure?** Grep current logs for `password`, `token`, `authorization` patterns; rotate anything found (paper 063 recovery rules).

## Rule-to-decision map

| Rule (level) | Decision | Enforcement point | Verification |
|---|---|---|---|
| No secrets in default logs (MUST) | Redacting serializer with denylist + allowlist by field type | Logging middleware | Fuzz suite: known secret shapes never emitted |
| Outcome codes instead of bodies (SHOULD) | `failure_reason` enum at warn level | Auth handler | Debugging goal met: failure classes distinguishable |
| Scoped debug mode (MAY) | Flag + TTL + audit event + separate retention | Debug feature config | Mode auto-expires; usage audited |
| Token identifiers only (MUST) | First 8 hex of token hash as `token_hint` | Logger field | Raw token never present in any level |
| Retention/deletion for debug channel (SHOULD) | 7-day retention, restricted ACL | Log pipeline config | Access review + expiry verified |

## Failure modes addressed

- Credential leakage via log export or support tooling — redaction at emission, not downstream.
- Post-incident exposure of retained debug bodies — time-boxed, isolated retention.
- Attacker reconnaissance from error differentiation — internal-only outcome codes.
- Silent regression adding a new secret field — serializer allowlist fails closed.

## Verification evidence

- Automated log scan in CI: test traffic with fake secrets produces zero matches in emitted logs.
- Debug-mode drill: enabled, used, expired; audit event present; retention isolated.
- Access check: debug channel readable only by the on-call role.

## Stop-condition check

No stop condition remains: no secrets written by default, redaction enforced at the enforcement point (the serializer), debug escape hatch authorized and time-boxed, existing exposure swept.

## Deliverable summary

Redacting log serializer, outcome-code taxonomy for auth failures, scoped debug mode, and a CI log-scanning test. The auth failure semantics themselves route to `auth-access`; log pipeline configuration routes to `production-operations`.
