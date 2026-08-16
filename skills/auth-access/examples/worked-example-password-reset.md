# Worked example: password reset for an existing API

> Calibration artifact: this shows the shape and depth a run of the `auth-access` skill should produce. It is illustrative, not exhaustive; the papers remain authoritative.

**Request (as a user would phrase it):**

> Add password reset to our Node/Postgres API. Email a reset link that logs the user in. We need it today, keep it simple.

## Papers consulted

- [004 Authentication](../references/papers/004-authentication.md) — reset flow, lockout, enumeration (§2 questions, §8 subtopic rules)
- [007 Sessions](../references/papers/007-sessions.md) — rotation after privilege change, device sessions
- 127 Randomness & Token Generation — in the `security-privacy` skill, via the boundary map

## Assumptions (labeled)

- **A1 (assumption):** single-tenant API; no per-tenant reset policy needed. *If false:* reset windows and lockout policy become tenant-configurable.
- **A2 (assumption):** email delivery is async and unreliable; the link is the only channel. *If false:* an OTP fallback changes the UI flow, not the token rules.

## Pre-implementation questions answered

- **Reset token lifetime?** 30 minutes, single use, invalidated on password change and on any successful login (paper 004 MUST).
- **Token storage?** SHA-256 hash of a 256-bit CSPRNG token; the raw token exists only in the email link (paper 127).
- **Enumeration defense?** The response to an unknown email is byte-identical to the known-email response, and the email is sent only to registered addresses; timing is equalized (paper 004 failure modes).
- **What happens to sessions on reset?** All sessions revoked, a new session issued only after the new password is confirmed (paper 007 — rotation on privilege change).
- **Lockout?** 5 attempts per account per hour, 20 requests per IP per hour, with alerting on spikes (paper 004 abuse rules; mechanism owned by `resilience-flow-control` paper 038).

## Rule-to-decision map

| Rule (level) | Decision | Enforcement point | Verification |
|---|---|---|---|
| Reset tokens single-use + expiring (MUST) | 30-min TTL, consumed atomically on use | `UPDATE ... WHERE token_hash = ? AND used_at IS NULL AND expires_at > now()` returning affected-row count | Concurrent use of one link: exactly one request succeeds |
| Token entropy (MUST) | 256-bit CSPRNG, hashed at rest | Token service + DB constraint on token_hash uniqueness | Entropy review; no sequential or time-based tokens |
| No enumeration (MUST) | Identical response and timing for known/unknown emails | Controller + response template | Timing and byte comparison across cases |
| Session rotation (MUST) | Revoke all sessions at reset confirmation | Session store delete-by-user in the same transaction | Old session cookies rejected after reset |
| Lockout bounds (MUST) | Per-account and per-IP limits with alert | Rate limiter middleware + metric | 6th attempt blocked; alert fires |

## Failure modes addressed

- Reset link reused after success (duplicate reset) — token consumed atomically.
- Attacker harvests accounts via reset responses — enumeration-neutral responses.
- Stolen link replayed after password change — invalidation on change.
- Mail-provider delay treated as failure — reset request is idempotent and never confirms account existence in-band.

## Verification evidence

- Concurrent double-click on the reset link: one success, one 410.
- Unknown-email and known-email requests: identical status, body, and timing within tolerance.
- After reset, prior session cookie: rejected.
- Lockout: 6 attempts within the window blocked with Retry-After.
- Token table has no plaintext tokens (schema review).

## Stop-condition check

No stop condition remains: no reusable tokens, no plaintext secrets at rest, no enumeration, authorization enforced at the data boundary, lockout bounded, audit trail on every reset event (owner, outcome, request ID).

## Deliverable summary

The implementation slice is: token service + `POST /auth/reset-request` + `POST /auth/reset-confirm` + session revocation + lockout wiring + the five verification tests above. Migration note: additive table, no existing-user impact; rollout behind a flag with the audit events wired before launch.
