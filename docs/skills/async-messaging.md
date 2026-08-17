# Think Through Async Work & Messaging (`async-messaging`)

Production expertise for asynchronous work — what breaks after deployment: poison jobs that loop forever, unacknowledged redeliveries, missed cron runs, and consumers that cannot tolerate duplicates.

## Modes

- **Think** clarifies requirements, invariants, risks, alternatives, decisions, and validation paths.
- **Review** inspects an existing artifact, repository, diff, or operating state and returns evidence-backed findings.
- **Change** applies approved decisions and keeps verification outstanding until proof is gathered.
- **Verify** reports tests, measurements, operational evidence, and residual risks without inventing missing proof.

If no mode is named, the skill infers one and states it. Combined work proceeds **Think → Review → Change → Verify**.

## What it covers

- background jobs, workers, progress, cancellation, crash recovery;
- retry policies, backoff with jitter, poison jobs, dead-letter queues;
- scheduled/cron jobs: duplicate-run and missed-run handling, DST, leader election;
- queues, topics, pub/sub, consumer groups, delivery guarantees;
- domain and integration events: schemas, versioning, ordering, fan-out, replay;
- the transactional outbox/inbox pattern that replaces dual writes;
- batch processing with chunking and resumability;
- bulk operations with partial-failure reporting;
- deduplication windows and scopes;
- email delivery: provider failure, bounces, idempotent sends;
- multi-channel notifications, preferences, quiet hours.

## When to use

Adding or changing anything that happens "later" or "in the background": jobs, queues, events, scheduled work, emails, notifications — and especially requests like "just retry forever until it works."

## What a run produces

The output follows the active mode: Think returns decisions and open questions; Review returns findings without claiming changes; Change records the approved work and pending proof; Verify returns observed evidence and explicitly labels unrun checks.

A semantics table for every queue, job, and event (delivery guarantee, ordering scope, idempotency, retry bound, retention, dead-letter policy), idempotent effects under redelivery, and lag visibility. The skill stops work on infinite retries, "exactly once" claims from broker settings, or side effects fired inside transactions.

## Works well with

- `transactions-consistency` for the transaction that publishes the event;
- `resilience-flow-control` for retry/timeout budgets and backpressure;
- `migration-evolution` for event schema changes with old consumers;
- `production-operations` for queue lag and backlog alerting.

## Try it

~~~text
Add a background job that charges cards and sends confirmation emails. If
anything fails, retry forever until it works. Use async-messaging.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/async-messaging/SKILL.md)
- Worked example: [a bounded background job with idempotent effects](../../skills/async-messaging/examples/worked-example-welcome-email-job.md)
