# Worked example — returning a route only when the user also asked for the fix

## Request

> "Our nightly backfill keeps dying halfway and leaves duplicate rows. Which skill covers this, and can you just fix it while you're in there?"

Two asks in one sentence: a route, and the work. This skill answers the first and declines the second in plain terms.

## Outcome and surfaces

Outcome: make a resumable backfill that cannot leave duplicates behind.

| Surface | Real subject |
|---|---|
| Migration | Resumable backfill, restart semantics, progress tracking |
| Invariant | Duplicate rows — the write is not idempotent under retry |
| Data | The constraint that should have made duplicates impossible |
| Async work | Whether the nightly runner is a job with its own retry policy |
| Evidence | Proof the restart path works before trusting the next run |

## Route

| # | Skill | Mode | Why it owns this surface |
|---|---|---|---|
| 1 | `migration-evolution` | Review | Owns backfill resumability and restart semantics; the failure is a migration-shaped failure |
| 2 | `transactions-consistency` | Think | Duplicates on retry are an idempotency problem, and it is required by step 1 when backfill writes affect authoritative invariants |
| 3 | `data-storage` | Think | Owns the uniqueness constraint that should backstop the invariant rather than relying on the job behaving |
| 4 | `async-messaging` | Review | Owns the nightly runner if it is a job or queue with its own retry policy |
| 5 | `quality-release` | Verify | Owns proof that a mid-run kill resumes cleanly and produces no duplicates |

Step 1 opens in Review because a broken thing already exists and its actual behavior is not yet established. Step 2 precedes step 3 because the constraint is chosen to enforce a decided invariant, not the reverse.

## Companions each owner will pull in

- `migration-evolution` — required `transactions-consistency` (already step 2), required `async-messaging` when a relay or retained events are involved (already step 4), recommended `quality-release` for resumability proof (step 5).
- `transactions-consistency` — recommended `data-storage` where constraints backstop the invariant (step 3).

## Gaps

- Whether the nightly runner is a cron job, a queue worker, or a script changes whether step 4 applies. That cannot be routed without inspection — **`async-messaging` in Review mode owns that inspection**, and it is named as a routed step rather than performed here.
- Nothing in this route is unowned, and no routed skill is missing from the installed set.

## Not covered here

This skill returns the route only. It has not opened the backfill, read the schema, or run anything.

The fix belongs to **step 1, `migration-evolution` in Review mode**, continuing through the route above into Change and closing with `quality-release` in Verify mode.

## Why the fix was not applied

The duplicate rows are the visible symptom; the missing constraint and the non-idempotent write are the cause. Patching the symptom during a routing answer would have removed the moment where the route — invariant before constraint, evidence at the end — could be corrected, and the next nightly run would fail the same way for a different reason.
