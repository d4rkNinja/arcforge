# Worked example: order creation across Postgres, Kafka, and Redis

> Calibration artifact: this shows the shape and depth a run of the `transactions-consistency` skill should produce. It is illustrative, not exhaustive; the papers remain authoritative.

**Request (as a user would phrase it):**

> Make order creation atomic: write the order to Postgres, publish it to Kafka, and update the Redis cache, all in one go.

## Papers consulted

- [023 Database Transactions](../references/papers/023-database-transactions.md) — boundaries, isolation, retry scope
- [036 Idempotency](../references/papers/036-idempotency.md) — keys, fingerprints, ambiguous outcomes
- [048 Distributed Transactions](../references/papers/048-distributed-transactions.md) — saga/compensation boundaries
- 047 Transactional Outbox / Inbox — in the `async-messaging` skill
- [024 Concurrency Anomalies](../references/papers/024-concurrency-anomalies.md) — duplicate-create races

## Assumptions (labeled)

- **A1 (assumption):** order acceptance and downstream effects (analytics, notifications) may be briefly delayed but never lost or duplicated visibly. *If false:* effects become part of the acceptance invariant and the topology changes.
- **A2 (assumption):** inventory reservation stays inside the same Postgres database. *If false:* a saga with compensation is required (paper 048).

## Pre-implementation questions answered

- **What is the invariant?** An accepted order is exactly-once recorded with its reserved inventory in one database transaction; all external effects derive from that commit.
- **Is "one transaction over three systems" possible?** No. A local transaction cannot make a Kafka publish or a Redis write atomic (paper 023 invariant). This is a dual-write hazard: the request as stated is unsafe.
- **Correct pattern?** Commit order + inventory + **outbox row** in one transaction; a relay publishes to Kafka from the outbox; Redis is invalidated (not written) on commit and repopulated on read (papers 047 pointer, 036).
- **Duplicate submissions?** Idempotency key scoped to customer + operation, bound to a request fingerprint, reserved atomically; concurrent duplicates converge on one result (paper 036 MUST).
- **Timeout after commit?** Outcome is discoverable: replay by idempotency key returns the stored result; no blind retry (paper 036).

## Rule-to-decision map

| Rule (level) | Decision | Enforcement point | Verification |
|---|---|---|---|
| No uncoordinated dual write (MUST) | Outbox row committed with the order | Same-transaction insert; relay publishes after commit | Crash between commit and publish: event still delivered; between insert and commit: nothing delivered |
| Idempotent acceptance (MUST) | Key = customer + op + fingerprint | Unique index on idempotency key | Two concurrent identical requests: one order, both get same response |
| Inventory race safety (MUST) | Conditional decrement `WHERE reserved >= qty` | Atomic UPDATE in the transaction | Concurrent oversell attempt: exactly one wins |
| Cache is derived (MUST) | Invalidate-on-commit, rebuild on read | Cache invalidation hook + versioned keys | Stale-order read test after commit |
| Bounded relay retry (MUST) | Cap + backoff + DLQ for poison events | Relay configuration | Poison event lands in DLQ; lag alert fires |

## Failure modes addressed

- Order committed, event lost → outbox relay guarantees eventual publication.
- Event published, order rolled back → impossible: outbox row is inside the transaction.
- Duplicate charge/notification on retry → idempotency key replays the stored outcome.
- Ambiguous client timeout → status lookup by order id / idempotency key.

## Verification evidence

- Crash injection at each boundary (before commit, after commit before relay, after publish): system converges to one valid outcome.
- Barrier-forced duplicate requests: single order, identical responses.
- Concurrent inventory exhaustion: no oversell under 100 parallel checkouts.
- Relay outage drill: backlog drains within lag SLO; DLQ receives poison event.

## Stop-condition check

No stop condition remains: no dual write, every invariant has an enforcement point, idempotency scoped and atomic, ambiguous outcomes discoverable, retries bounded.

## Deliverable summary

Order transaction (order + inventory + outbox), idempotency reservation, relay with DLQ and lag alert, cache invalidation hook, and the boundary-crash test suite. The Kafka and relay configuration details route to `async-messaging`; publish semantics are at-least-once with idempotent consumers.
