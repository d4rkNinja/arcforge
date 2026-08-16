# Worked example: the column rename that could not ship this afternoon

> Calibration artifact: this shows the shape and depth a run of the `migration-evolution` skill should produce. It is illustrative, not exhaustive; the papers remain authoritative.

**Request (as a user would phrase it):**

> Rename users.email to users.email_address and ship it this afternoon.

## Papers consulted

- [029 Schema Evolution](../references/papers/029-schema-evolution.md) — expand-and-contract
- [030 Database Migrations](../references/papers/030-database-migrations.md) — online migration ordering, locks
- [031 Data Migrations & Backfills](../references/papers/031-data-migrations-and-backfills.md) — chunked, resumable backfill
- [071 Backward Compatibility](../references/papers/071-backward-compatibility.md) — mixed-version windows
- 075 Data Export — in the `production-operations` skill, for downstream consumers of the old field

## Assumptions (labeled)

- **A1 (assumption):** a mobile app release older than 6 months still reads `email` from API responses. *If false:* the dual-read window shortens but does not disappear (server rollouts are still gradual).
- **A2 (assumption):** the table holds ~40M rows; online migration must not lock beyond seconds. *If false:* lock strategy changes (paper 030).

## Pre-implementation questions answered

- **Why is "rename this afternoon" rejected?** A rename is destructive: old binaries/readers break instantly, and rollback cannot restore dropped data (papers 029, 030 MUST).
- **Correct sequence?** Expand-and-contract: (1) add `email_address` nullable; (2) dual-write both columns in one transaction; (3) chunked resumable backfill; (4) flip reads; (5) verify zero readers of `email`; (6) drop `email` in a later release (paper 029).
- **Backfill safety?** 10k-row chunks, idempotent (`WHERE email_address IS NULL`), never overwrites newer writes, rate-limited, resumable (paper 031).
- **Compatibility window?** API continues to emit `email` until telemetry shows zero old-field consumers, then one release with both, then removal (paper 071).
- **Rollback at each step?** Steps 1–4 reversible by flipping config; step 6 irreversible and gated on verification evidence (paper 029).

## Rule-to-decision map

| Rule (level) | Decision | Enforcement point | Verification |
|---|---|---|---|
| No destructive rename (MUST) | Expand-and-contract sequence | Migration pipeline stages with gates | Gate report per stage before the next runs |
| Dual-write atomicity (MUST) | Both columns written in one transaction | Repository write path | Crash between writes: impossible (single transaction) |
| Idempotent backfill (MUST) | Chunked, null-guarded, resumable | Backfill job predicates | Kill mid-run, restart: converges, no overwrite of newer values |
| Compatibility window (MUST) | Emit both fields until usage zero | API serializer + usage telemetry | Old-field consumer count → 0 before removal release |
| Rollback defined per step (MUST) | Config flips for 1–4; drop deferred and gated | Deployment runbook | Rollback rehearsal on staging copy |

## Failure modes addressed

- Old clients reading a vanished field — dual-emit window.
- Backfill overwriting concurrent user updates — null-guard + newer-wins reconciliation.
- Lock storm on 40M rows — chunked online migration with lock timeouts.
- Rollback discovering data gone — drop deferred to its own gated release.

## Verification evidence

- Staging rehearsal of the full sequence on a production copy with timed locks.
- Backfill kill/restart convergence test.
- Mixed-version test: old and new server versions run simultaneously against the migrated schema.
- Telemetry report: old-field reads at zero for 7 days before step 6.

## Stop-condition check

No stop condition remains: every step ordered, gated, and reversible-or-gated-irreversible with evidence; the "this afternoon" framing is answered with a dated stage plan instead.

## Deliverable summary

Six-stage migration plan with gates, the idempotent backfill job, dual-emit serializer change, usage telemetry, and the rehearsal evidence checklist.
