# Worked example: the background job that was told to retry forever

> Calibration artifact: this shows the shape and depth a run of the `async-messaging` skill should produce. It is illustrative, not exhaustive; the papers remain authoritative.

**Request (as a user would phrase it):**

> Add a background job that charges cards and sends confirmation emails. If anything fails, just retry forever until it works.

## Papers consulted

- [043 Background Jobs](../references/papers/043-background-jobs.md) — retries, poison jobs, DLQ
- [045 Messaging / Queues](../references/papers/045-messaging-queues.md) — delivery guarantees, redelivery
- [128 Email Delivery Infrastructure](../references/papers/128-email-delivery-infrastructure.md) — bounces, idempotent sends
- 036 Idempotency — in the `transactions-consistency` skill
- 137 Observability for Async Systems — in the `production-operations` skill

## Assumptions (labeled)

- **A1 (assumption):** card charge executes via a payment provider whose timeout leaves the outcome ambiguous (captured or not). *If false:* a simple status check still applies; the design does not change.
- **A2 (assumption):** marketing insists a welcome email may arrive late but must never arrive twice per signup event. *If false:* dedup scope widens per campaign, changing key design.

## Pre-implementation questions answered

- **Delivery model?** At-least-once queue with idempotent effects — "exactly once" is not claimed (paper 045).
- **Retry policy?** 5 attempts, exponential backoff with full jitter, 24-hour total budget, then dead-letter with alert (paper 043 MUST — "retry forever" rejected).
- **Charge idempotency?** Provider idempotency key = order id + attempt family; ambiguous timeout triggers status reconciliation, never a blind re-charge (paper 036 pointer).
- **Email idempotency?** Send keyed on (signup event id, email type); provider webhook dedupes bounces/complaints; suppression list honored (paper 128).
- **Visibility?** Queue depth, attempt histogram, DLQ count, oldest-job age — alert on lag SLO breach (paper 137 pointer).

## Rule-to-decision map

| Rule (level) | Decision | Enforcement point | Verification |
|---|---|---|---|
| Bounded retries (MUST) | 5 attempts / 24h budget / DLQ | Worker retry policy | Permanent failure lands in DLQ after 5 attempts, never loops |
| Backoff with jitter (MUST) | Exponential, full jitter, honors Retry-After | Retry scheduler | Storm test: 1k simultaneous failures do not synchronize |
| Idempotent charge (MUST) | Provider idempotency key + status reconciliation | Payment adapter | Timeout-then-retry: exactly one capture |
| Idempotent email (MUST) | Dedup key at sender + suppression list | Email service adapter | Redelivered job: no second email |
| Poison-path handling (MUST) | DLQ + alert + replay tooling | Queue config + alert rule | Poison job quarantined; replay works after fix |

## Failure modes addressed

- Infinite retry loop consuming workers — bounded policy with DLQ.
- Duplicate charge on ambiguous timeout — reconciliation before retry.
- Duplicate email on redelivery — send-level dedup key.
- Provider outage cascading into backlog — bounded concurrency, lag alert, drain-time budget.

## Verification evidence

- Failure injection per class (4xx, 5xx, timeout, DNS): attempt counts, schedule, and terminal routing asserted.
- Redelivery drill: same job delivered twice → one charge, one email.
- Provider outage drill: backlog drains within SLO after recovery; no message loss.
- DLQ replay drill: fixed job reprocessed exactly once.

## Stop-condition check

No stop condition remains: bounded retries, explicit delivery semantics, idempotent effects under redelivery, DLQ with ownership, and lag visibility for the queue backing a user journey.

## Deliverable summary

One job class with retry policy, two idempotent adapters (payment, email), DLQ wiring with alert, and the failure-injection suite. The charge's transactional context routes to `transactions-consistency`; pacing mechanics route to `resilience-flow-control`.
