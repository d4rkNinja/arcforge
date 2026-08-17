---
name: async-messaging
description: "Use when thinking through, reviewing, changing, or verifying asynchronous work: jobs, workers, schedules, queues, events, outbox or inbox, batch processing, deduplication, email, or notifications. For transaction invariants use transactions-consistency; for retry and overload controls use resilience-flow-control; for event evolution use migration-evolution."
---

# Think Through Async Work & Messaging

## Overview

Production guidance for asynchronous work. Each reference paper captures what breaks after deployment: poison jobs that loop forever, unacknowledged redeliveries, missed cron executions, event consumers that cannot tolerate duplicates or reordering, and email providers whose bounces and outages dominate the incident channel.

**Core principle:** Async work is a correctness surface. Every queue, job, and event needs defined delivery, ordering, idempotency, retry, retention, replay, and backlog semantics — with bounds and lag visibility.

## Domain Law

```text
NO ASYNC WORK OR MESSAGING CHANGE WITHOUT:
1. the primary paper(s) for the mechanism read in full first;
2. delivery, ordering, idempotency, retry, and replay semantics stated
   for every queue, job, and event;
3. "Existing-codebase checks" run when changing existing workers;
4. every applicable MUST mapped to a decision with bounds (attempts,
   payload, concurrency, retention), a test, or a documented exception.
```

## When to Use

Use this skill when thinking through, reviewing, changing, or verifying:

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

## Select the Operating Mode

| Mode | Use when | Required result |
|---|---|---|
| **Think** | The safe decision is not settled | requirements, constraints, invariants, risks, alternatives, decision, and validation path |
| **Review** | An artifact, repository, diff, or operating state already exists | evidence separated from assumptions, prioritized findings, and blockers |
| **Change** | Decisions are approved and repository changes are requested | the smallest safe change, compatibility notes, and verification still required |
| **Verify** | A claim needs proof | tests or measurements run, observed evidence, and residual risks |

If the user names a mode, use it. Otherwise infer the mode from intent and state the inference in one sentence. For a combined request, run **Think → Review → Change → Verify** and preserve the trace between phases. Think may stop with a decision; Review may stop with findings. Change must not claim completion before Verify. Verify must never turn a planned or unavailable check into evidence.

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

Use the domain workflow as shared gates, then branch by the selected mode:

- **Think:** answer the questions and stop with a reasoned decision and validation path; do not edit by default.
- **Review:** inspect the available artifact or repository and stop with evidence-backed findings; do not claim changes.
- **Change:** apply only approved decisions, then continue to Verify before claiming completion.
- **Verify:** run the relevant checks, report observed results, and label every unavailable or unrun check.

1. Identify each asynchronous unit of work and its failure semantics; select primary papers (an order-confirmation email touches 043 + 128 + 047).
2. Read the primary papers fully, including delivery/retry matrices and common bugs.
3. Answer the paper's pre-implementation questions; label autonomous assumptions and their impact.
4. For existing workers, run the existing-codebase checks: find every consumer, the real acknowledgment mode, poison-path handling, and current lag visibility.
5. Convert each MUST/SHOULD/AVOID/NEVER into bounded decisions: attempts, backoff with jitter, payload limits, concurrency, retention, DLQ policy, and lag alerts — each with a test.
6. Apply the active mode: stop at a decision in Think; stop at findings in Review; make the smallest approved safe change in Change; run duplicate-delivery, crash, backlog-drain, and poison checks in Verify.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Companion Skills and Standalone Safety

| Type | When | Companion | Missing companion behavior |
|---|---|---|---|
| **Required** | Work or events derive from an authoritative commit | `transactions-consistency` | Preserve no-dual-write and idempotency requirements. |
| **Required** | Retry, timeout, backpressure, or dependency-failure policy is in scope | `resilience-flow-control` | Require finite attempts and bounded load; label control depth missing. |
| **Handoff** | Event schemas or consumers evolve | `migration-evolution` | Do not prescribe a breaking one-step rollout. |
| **Recommended** | Lag, depth, poison, or provider failures need operational evidence | `production-operations` | State required signals and label operational proof missing. |

If a companion is unavailable, complete only the safe local delivery decision, name the missing depth, and recommend the exact technical ID or `transactional-workflow` installation group. Never claim unavailable material was read or weaken atomic publication, idempotency, bounded retry, or backlog limits.

## Output Contract

The selected mode is authoritative. Include only applicable fields below; a planned check is a validation path, not verification evidence.

Scale the output to the active mode: Think returns delivery decisions; Review returns findings; Change returns the repository-aware change plus pending proof; Verify returns observed duplicate, retry, lag, and recovery evidence with unrun checks labeled. A combined flow preserves all four phases.

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
