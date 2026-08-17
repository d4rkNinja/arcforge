# Think Through Transactions & Consistency (`transactions-consistency`)

Production expertise for correctness under concurrency and distribution — the hazards that pass code review silently: dual writes, lost updates, unfenced locks, and retries that duplicate committed effects.

## Modes

- **Think** clarifies requirements, invariants, risks, alternatives, decisions, and validation paths.
- **Review** inspects an existing artifact, repository, diff, or operating state and returns evidence-backed findings.
- **Change** applies approved decisions and keeps verification outstanding until proof is gathered.
- **Verify** reports tests, measurements, operational evidence, and residual risks without inventing missing proof.

If no mode is named, the skill infers one and states it. Combined work proceeds **Think → Review → Change → Verify**.

## What it covers

- transaction boundaries, isolation levels, deadlocks, retry scope;
- optimistic/pessimistic locking, compare-and-swap, conditional updates;
- concurrency anomalies: lost updates, write skew, check-then-act races;
- entity state machines, legal transitions, transition history;
- idempotency keys, request fingerprinting, response replay, retry safety;
- sagas, compensation, and cross-service workflow consistency;
- consistency models and staleness for read paths;
- replication, partitioning/sharding, skew and resharding;
- consensus assumptions behind managed stores;
- distributed locks, leases, and fencing tokens;
- ordering guarantees and their scope.

## When to use

Any transactional or concurrent code — checkouts, reservations, counters, state transitions, duplicate handling — and especially requests like "make writing to the database, queue, and cache atomic in one transaction" (that request is unsafe, and this skill explains why and what to do instead).

## What a run produces

The output follows the active mode: Think returns decisions and open questions; Review returns findings without claiming changes; Change records the approved work and pending proof; Verify returns observed evidence and explicitly labels unrun checks.

Named invariants with enforcement points, the narrowest safe control for each, interleaving tests that force real races, and defined outcomes for duplicates, conflicts, timeouts, and ambiguous results. The skill stops work on uncoordinated dual writes, unfenced locks, or "exactly once" claims without proof.

## Works well with

- `async-messaging` for outbox-based effects after commit;
- `resilience-flow-control` for retry pacing and deadlines;
- `data-storage` for constraint and index backstops;
- `quality-release` for concurrency test suites.

## Try it

~~~text
Make order creation atomic: write the order to Postgres, publish it to
Kafka, and update the Redis cache, all in one go. Use transactions-consistency.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/transactions-consistency/SKILL.md)
- Worked example: [order creation across a database, queue, and cache](../../skills/transactions-consistency/examples/worked-example-order-creation-outbox.md)
