---
name: transactions-consistency
description: "Use when implementing or changing transactional or concurrent code: ACID transactions, isolation levels, lost updates, write skew, check-then-act races, optimistic and pessimistic locking, compare-and-swap, state machines, idempotency keys and request deduplication, sagas and distributed transactions, consistency models, replication, partitioning and sharding, consensus, distributed locks and fencing, and ordering guarantees. Loads production implementation papers with MUST/SHOULD/AVOID/NEVER rules, failure modes, and verification checklists to read before writing code. For queues and outbox patterns use async-messaging; for retry/timeout mechanics use resilience-flow-control; for whole-system architecture use system-architecture-harness."
---

# Transactions & Consistency Implementation

## Overview

Implementation intelligence for correctness under concurrency and distribution. Each reference paper captures the hazards that pass code review silently: isolation levels that do not mean what their names claim, dual writes that corrupt state, idempotency keys without fingerprints, locks without fencing, and retries that duplicate committed effects.

**Core principle:** Every invariant needs an enforcement point at an authoritative boundary. A local transaction never makes a remote side effect atomic, and a timeout never proves a rollback.

## Implementation Law

```text
NO CONCURRENCY IMPLEMENTATION WITHOUT:
1. the primary paper(s) for the mechanism read in full first;
2. the invariant, its authoritative owner, and all concurrent writers
   named before choosing a control;
3. the paper's "Questions that must be answered before implementation"
   answered, or each open point labeled as an assumption;
4. every applicable MUST mapped to an enforcement point, a test that
   forces the interleaving, or a documented exception.
```

## When to Use

Use this skill when implementing or changing:

- transaction boundaries, isolation levels, deadlocks, and retry scopes;
- optimistic locking, version columns, compare-and-swap, conditional updates;
- pessimistic locking, advisory locks, mutex/semaphore usage;
- entity state machines, legal transitions, and transition history;
- idempotency keys, request fingerprinting, response replay, dedup scope;
- sagas, compensation, and cross-service workflow consistency;
- consistency model selection (read-committed through serializable, eventual);
- replication topology and read semantics;
- partitioning/sharding keys, resharding, and hot-partition behavior;
- consensus-backed stores and leader election assumptions;
- distributed locks, leases, and fencing tokens;
- ordering guarantees and their scope.

## When Not to Use

- Queue/job delivery semantics and the outbox pattern: use `async-messaging` (043, 047).
- Retry budgets, timeouts, circuit breakers: use `resilience-flow-control` (052, 053, 054).
- Schema constraints and index design: use `data-storage` (022, 027).
- Whole-system architecture and boundary decisions: use `system-architecture-harness`.

## Required Context Loading

| Situation | Papers |
|---|---|
| Boundaries, isolation, deadlocks, retries of transactions | [023 Database Transactions](references/papers/023-database-transactions.md) |
| Lost updates, write skew, phantom, check-then-act races | [024 Concurrency Anomalies](references/papers/024-concurrency-anomalies.md) |
| Optimistic/pessimistic control, CAS, fencing basics | [025 Concurrency Control](references/papers/025-concurrency-control.md) |
| States, transitions, guards, terminal states | [035 State Machines](references/papers/035-state-machines.md) |
| Idempotency keys, fingerprints, replay, retry safety | [036 Idempotency](references/papers/036-idempotency.md) |
| Sagas, compensation, cross-boundary workflows | [048 Distributed Transactions](references/papers/048-distributed-transactions.md) |
| Failure modes, partial failure, coordination costs | [098 Distributed Systems Fundamentals](references/papers/098-distributed-systems-fundamentals.md) |
| Read guarantees, staleness, read-your-writes | [099 Consistency Models](references/papers/099-consistency-models.md) |
| Replica topology, lag, failover semantics | [100 Replication](references/papers/100-replication.md) |
| Shard keys, skew, resharding | [101 Partitioning / Sharding](references/papers/101-partitioning-sharding.md) |
| Quorum/consensus assumptions in managed stores | [102 Distributed Consensus](references/papers/102-distributed-consensus.md) |
| Leases, fencing tokens, stale holders | [103 Distributed Locks](references/papers/103-distributed-locks.md) |
| Ordering scope, causality, sequence semantics | [121 Ordering Guarantees](references/papers/121-ordering-guarantees.md) |

## Workflow

1. Write the invariant in business terms and name its authoritative owner and every concurrent writer (requests, jobs, webhooks, admins, retries, old binaries).
2. Select the primary paper for the control mechanism and read it fully.
3. Answer the paper's pre-implementation questions; label autonomous assumptions and their impact.
4. For existing code, run the existing-codebase checks: verify the deployed engine/version/isolation, constraint reality, and every write path — not just the visible handler.
5. Choose the narrowest authoritative enforcement (constraint, conditional update, transaction, CAS, fenced lock, durable workflow) and define the observable outcome for losers, duplicates, conflicts, timeouts, and ambiguous results.
6. Convert each MUST/SHOULD/AVOID/NEVER into an enforcement point plus a test that forces the interleaving with barriers, at real isolation.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Boundary Map

| If the task also involves | Also use |
|---|---|
| Publishing effects after commit (outbox) | `async-messaging` (047) |
| Retry pacing, deadlines, circuit breaking | `resilience-flow-control` (052, 053, 054) |
| Constraint and index backstops | `data-storage` (022, 026, 027) |
| Sharding-driven schema/migration work | `migration-evolution` (030, 031) |
| Multi-region failover and RPO/RTO | `production-operations` (132, 078) |
| Race coverage in test suites | `quality-release` (092, 093) |

## Output Contract

1. **Papers consulted** — numbers and the sections relied on.
2. **Invariants and owners** — each invariant, its enforcement point, and all concurrent writers.
3. **Assumptions and unanswered questions** — labeled, with their design impact.
4. **Rule-to-decision map** — each applicable MUST/SHOULD → control choice, enforcement point, and interleaving test.
5. **Failure modes addressed** — lost update, write skew, duplicate effect, stale lock holder, ambiguous outcome, and their resolutions.
6. **Verification evidence** — barrier-forced concurrency tests, timeout-after-commit handling, rollback/compensation paths.

## Stop Conditions

Stop and revise when any of these appears:

- code is written before the invariant, its owner, and its writers are named;
- an invariant with no enforcement point at an authoritative boundary;
- an uncoordinated dual write across a database and any other system;
- a transaction held open across network or provider calls;
- an idempotency key without caller/operation scope, request fingerprint, atomic reservation, and terminal-outcome persistence;
- a distributed lock used for correctness without fencing or lease expiry defense;
- "exactly once" claimed without a demonstrated boundary and proof;
- a timeout assumed to mean rollback, or a failed statement retried instead of the transaction;
- a state machine without expected-source-state conditions on transitions;
- a partition/shard key chosen without skew and resharding analysis;
- replication lag ignored on read paths that make decisions;
- any concurrency MUST downgraded to a TODO without a documented exception.

## References

Thirteen production papers under `references/papers/`: 023 Database Transactions, 024 Concurrency Anomalies, 025 Concurrency Control, 035 State Machines, 036 Idempotency, 048 Distributed Transactions, 098 Distributed Systems Fundamentals, 099 Consistency Models, 100 Replication, 101 Partitioning / Sharding, 102 Distributed Consensus, 103 Distributed Locks, 121 Ordering Guarantees. Cross-domain pointers inside the papers name the sibling skill to activate.

Worked example: [order creation across a database, queue, and cache](examples/worked-example-order-creation-outbox.md).
