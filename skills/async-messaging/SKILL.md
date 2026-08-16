---
name: async-messaging
description: "Use when implementing or changing asynchronous processing: background jobs and workers, retries and dead-letter queues, scheduled/cron jobs, message queues and pub/sub, consumer groups and delivery guarantees, domain and integration events, transactional outbox/inbox, batch processing, bulk operations, deduplication, email delivery infrastructure, and notification systems. Loads production implementation papers with MUST/SHOULD/AVOID/NEVER rules, failure modes, and verification checklists to read before writing code. For transaction and idempotency internals use transactions-consistency; for retry/timeout pacing use resilience-flow-control; for event schema evolution use migration-evolution; for whole-system architecture use system-architecture-harness."
---

# Async Jobs & Messaging Implementation

## Overview

Implementation intelligence for asynchronous work. Each reference paper captures what breaks after deployment: poison jobs that loop forever, unacknowledged redeliveries, missed cron executions, event consumers that cannot tolerate duplicates or reordering, and email providers whose bounces and outages dominate the incident channel.

**Core principle:** Async work is a correctness surface. Every queue, job, and event needs defined delivery, ordering, idempotency, retry, retention, replay, and backlog semantics — with bounds and lag visibility.

## Implementation Law

```text
NO ASYNC IMPLEMENTATION WITHOUT:
1. the primary paper(s) for the mechanism read in full first;
2. delivery, ordering, idempotency, retry, and replay semantics stated
   for every queue, job, and event;
3. "Existing-codebase checks" run when changing existing workers;
4. every applicable MUST mapped to a decision with bounds (attempts,
   payload, concurrency, retention), a test, or a documented exception.
```

## When to Use

Use this skill when implementing or changing:

- background jobs, workers, progress reporting, and cancellation;
- retry policies, backoff, poison-job handling, and dead-letter queues;
- scheduled/cron jobs, missed-run behavior, duplicate-run prevention, leader election;
- queues, topics, pub/sub, streams, and consumer groups;
- delivery guarantee selection (at-most/at-least-once) and consumer acknowledgment;
- domain and integration events: schemas, versioning, ordering, fan-out, replay;
- transactional outbox/inbox to avoid dual writes;
- batch processing with chunking and resumability;
- bulk operations with partial-failure reporting;
- deduplication windows and scopes;
- transactional email delivery, bounces, provider failure;
- notification infrastructure across channels.

## When Not to Use

- Transaction boundaries and idempotency-key internals: use `transactions-consistency` (023, 036).
- Retry pacing, deadlines, circuit breakers, backpressure policy: use `resilience-flow-control` (052–055, 104).
- API/webhook surface contracts (signing, versioning): use `api-contracts` (049).
- Event/schema evolution rollout: use `migration-evolution` (070, 071).
- Whole-system architecture: use `system-architecture-harness`.

## Required Context Loading

| Situation | Papers |
|---|---|
| Job queues, workers, retries, DLQs, poison jobs | [043 Background Jobs](references/papers/043-background-jobs.md) |
| Cron, recurrence, missed/duplicate execution, DST | [044 Scheduled Jobs](references/papers/044-scheduled-jobs.md) |
| Queues, topics, consumer groups, delivery guarantees | [045 Messaging / Queues](references/papers/045-messaging-queues.md) |
| Domain/integration events, ordering, replay, fanout | [046 Event Systems](references/papers/046-event-systems.md) |
| Outbox/inbox to replace dual writes | [047 Transactional Outbox / Inbox](references/papers/047-transactional-outbox-inbox.md) |
| Chunked, resumable batch pipelines | [118 Batch Processing](references/papers/118-batch-processing.md) |
| Bulk APIs and partial failure semantics | [119 Bulk Operations](references/papers/119-bulk-operations.md) |
| Dedup windows, keys, and scopes | [120 Deduplication](references/papers/120-deduplication.md) |
| Provider failure, bounces, idempotent sends | [128 Email Delivery Infrastructure](references/papers/128-email-delivery-infrastructure.md) |
| Multi-channel notifications, preferences, quiet hours | [129 Notification Infrastructure](references/papers/129-notification-infrastructure.md) |

## Workflow

1. Identify each asynchronous unit of work and its failure semantics; select primary papers (an order-confirmation email touches 043 + 128 + 047).
2. Read the primary papers fully, including delivery/retry matrices and common bugs.
3. Answer the paper's pre-implementation questions; label autonomous assumptions and their impact.
4. For existing workers, run the existing-codebase checks: find every consumer, the real acknowledgment mode, poison-path handling, and current lag visibility.
5. Convert each MUST/SHOULD/AVOID/NEVER into bounded decisions: attempts, backoff with jitter, payload limits, concurrency, retention, DLQ policy, and lag alerts — each with a test.
6. Implement the smallest safe slice; carry the paper's verification checklist (duplicate delivery, crash between steps, backlog drain, poison reruns) into the test plan.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Boundary Map

| If the task also involves | Also use |
|---|---|
| The transaction that publishes the event | `transactions-consistency` (023, 036, 048) |
| Retry/timeout budgets and backpressure | `resilience-flow-control` (052, 053, 104) |
| Event schema changes and old consumers | `migration-evolution` (070, 071, 134) |
| Webhook delivery surface | `api-contracts` (049) |
| Job/queue observability and lag alerts | `production-operations` (137) |
| Failure and load drills for workers | `quality-release` (093, 094) |

## Output Contract

1. **Papers consulted** — numbers and the sections relied on.
2. **Semantics table** — per queue/job/event: delivery guarantee, ordering scope, idempotency, retry bound, retention/replay, DLQ policy.
3. **Assumptions and unanswered questions** — labeled, with their design impact.
4. **Rule-to-decision map** — each applicable MUST/SHOULD → bounded decision, enforcement point, and test.
5. **Failure modes addressed** — duplicate delivery, poison jobs, missed schedules, backlog storms, provider outages.
6. **Verification evidence** — crash-between-steps, duplicate/redelivery, backlog drain, and cancel/timeout tests.

## Stop Conditions

Stop and revise when any of these appears:

- code is written before the delivery and idempotency semantics are stated;
- a job or consumer retry without a finite attempt cap, backoff with jitter, and a dead-letter path;
- "exactly once" claimed from broker settings without end-to-end idempotent effects;
- an event published from inside a transaction as if it were atomic with the commit;
- a scheduled job without duplicate-run and missed-run handling;
- an unbounded queue, payload, fan-out, or backlog with no drain model;
- consumers that assume single delivery, strict order, or stable retries;
- deduplication windows shorter than the maximum redelivery horizon;
- email/notification sends that are not idempotent under provider retries;
- worker crashes that lose in-flight work with no recovery or lease;
- no lag/depth visibility for any queue that backs a user journey;
- any async MUST downgraded to a TODO without a documented exception.

## References

Ten production papers under `references/papers/`: 043 Background Jobs, 044 Scheduled Jobs, 045 Messaging / Queues, 046 Event Systems, 047 Transactional Outbox / Inbox, 118 Batch Processing, 119 Bulk Operations, 120 Deduplication, 128 Email Delivery Infrastructure, 129 Notification Infrastructure. Cross-domain pointers inside the papers name the sibling skill to activate.

Worked example: [a bounded background job with idempotent effects](examples/worked-example-welcome-email-job.md).
