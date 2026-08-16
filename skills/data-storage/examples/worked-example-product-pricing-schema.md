# Worked example: pricing column and soft delete, done correctly

> Calibration artifact: this shows the shape and depth a run of the `data-storage` skill should produce. It is illustrative, not exhaustive; the papers remain authoritative.

**Request (as a user would phrase it):**

> Add a price column to products (just use FLOAT) and a deleted flag so rows are never really deleted.

## Papers consulted

- [020 Money / Numeric Precision](../references/papers/020-money-numeric-precision.md) — exact representation, rounding
- [032 Soft Delete / Hard Delete](../references/papers/032-soft-delete-hard-delete.md) — uniqueness interaction, purging
- [022 Database Constraints](../references/papers/022-database-constraints.md) — constraint backstops
- [033 Data Lifecycle](../references/papers/033-data-lifecycle.md) — retention and purge ownership
- [026 Data Integrity](../references/papers/026-data-integrity.md) — partial writes, repair

## Assumptions (labeled)

- **A1 (assumption):** single currency (USD), two decimal places, tax computed elsewhere. *If false:* currency code becomes part of the key and rounding mode must be per-currency (paper 020).
- **A2 (assumption):** "never really deleted" means recoverable for 90 days, not forever. *If false:* storage grows unbounded and privacy deletion obligations are violated (paper 033).

## Pre-implementation questions answered

- **Numeric type?** `NUMERIC(12,2)` — FLOAT rejected: binary floating point cannot represent 0.10 exactly and comparison/rounding errors compound (paper 020 MUST).
- **Uniqueness with soft delete?** `deleted_at IS NULL` partial unique index on the business key, so a soft-deleted SKU can be recreated while live rows stay unique (paper 032).
- **Query filtering?** Every read path filters `deleted_at IS NULL` via repository default scope; admin recovery paths opt in explicitly (paper 032).
- **Purge?** Nightly job hard-deletes rows soft-deleted >90 days, cascades to derived stores, and records purge counts (papers 032, 033, 125 pointer).
- **Rounding?** Display rounding happens at the edge with banker's rounding for aggregates; stored values are never rounded (paper 020).

## Rule-to-decision map

| Rule (level) | Decision | Enforcement point | Verification |
|---|---|---|---|
| Exact money representation (MUST) | `NUMERIC(12,2)` column; integer cents in app layer | Schema migration + type checks in repo layer | Insert 0.10; read back equal; sum of 1M rows exact |
| Soft-delete uniqueness (MUST) | Partial unique index `... WHERE deleted_at IS NULL` | DB constraint | Recreate SKU after soft delete succeeds; duplicate live SKU rejected |
| No deleted-row leakage (MUST) | Default scope `deleted_at IS NULL` | Repository base query | Automated scan: no query touches products without the scope or explicit opt-in |
| Retention enforcement (SHOULD) | 90-day purge with derived-store cascade | Scheduled job + metric | Purge drill: counts reconciled across DB, search index, cache |
| Constraint backstop (MUST) | CHECK (`price >= 0`) | DB constraint | Negative price insert rejected at DB, not just app validation |

## Failure modes addressed

- Floating-point drift in sums and comparisons — exact numeric type.
- Soft-deleted rows leaking into reports and unique conflicts — partial index + default scope.
- Unbounded growth and missed privacy deletion — owned purge job.
- Negative or null prices from bad imports — CHECK constraint.

## Verification evidence

- Precision test: sum of 10,000 rows priced 0.10 equals exactly 1,000.00.
- Soft-delete suite: recreate-after-delete, restore, purge, and derived-store cascade.
- Constraint suite: negative price, duplicate live SKU rejected.
- Purge job: dry-run report matches actual counts; job is idempotent under re-run.

## Stop-condition check

No stop condition remains: no floating-point money, constraints back the invariants, derived stores have rebuild/purge paths, retention has an owner.

## Deliverable summary

One migration (column + partial index + check), a repository default scope, a purge job, and the precision/purge test suites. Rollout: additive migration, backfill of defaults for existing rows, then application change — sequenced with `migration-evolution` paper 030 rules.
