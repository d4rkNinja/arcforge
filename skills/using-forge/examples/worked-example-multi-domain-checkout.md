# Worked example — routing a prepaid checkout request across four domains

## Request

> "Add prepaid checkout. Card is charged up front, inventory is finite so we cannot oversell, and the customer gets a receipt email. Ship it this sprint."

## Why this request needs routing

One sentence, four surfaces, and a deadline. Routed to a single skill it produces a plausible answer that quietly omits either the oversell invariant or the receipt delivery path. The deadline is pressure, not a routing input.

## Step 1 — Requested outcome and surfaces

Outcome: charge a card and reserve finite stock in one correct outcome, then notify the customer.

| Surface | Real subject |
|---|---|
| Invariant | Stock cannot go negative; payment and reservation cannot disagree |
| Data | Stock and reservation model, money precision, identifiers |
| Async work | Receipt email after the commit |
| Flow control | Payment provider timeouts and retries |
| Evidence | Concurrency and failure proof before the sprint claim |

## Step 2 — Owner per surface

| Surface | Owner | Why not the neighbour |
|---|---|---|
| Invariant | `transactions-consistency` | The request is about two effects agreeing, not about queue mechanics |
| Data | `data-storage` | Owns precision and constraints, not isolation levels |
| Async work | `async-messaging` | Receipt is post-commit work, not part of the public contract |
| Flow control | `resilience-flow-control` | Provider timeout and retry pacing, not the transaction itself |
| Evidence | `quality-release` | Owns the readiness claim the deadline is pushing on |

The word "email" also appears in `production-operations` territory and the word "charge" near `api-contracts`. Neither is the real subject here — the exclusions column settles both.

## Step 3 — Mode

The user said "ship it," but no decision exists yet. Route as **Think → Change → Verify** and state the inference: the oversell invariant has to be decided before anything is applied. Do not open at Change because the request sounds urgent.

## Step 4 — Companions

`transactions-consistency` carries two required companions that this request triggers:

- required `async-messaging` — the receipt derives from an authoritative commit;
- required `resilience-flow-control` — the payment call can time out ambiguously.

`data-storage` carries required `transactions-consistency`, already in the route. `quality-release` enters as recommended on the concurrency claim, and closes the route because a readiness claim is being made.

## Step 5 — Ordered route

| # | Skill | Mode | Receives | Owns | Produces |
|---|---|---|---|---|---|
| 1 | `transactions-consistency` | Think | The oversell and payment-agreement requirement | The invariant, the state machine, idempotency for an ambiguous charge | Invariant statement and the ambiguous-outcome contract |
| 2 | `data-storage` | Think | The invariant from step 1 | Stock and reservation model, money precision, constraints that backstop the invariant | Schema and constraint decisions |
| 3 | `resilience-flow-control` | Think | The ambiguous-outcome contract | Provider timeout, retry, and breaker policy that cannot duplicate a charge | Retry and timeout policy |
| 4 | `async-messaging` | Think | Commit boundary from step 1 | Post-commit receipt delivery, outbox, deduplication | Delivery design with no lost or duplicated receipt |
| 5 | Steps 1–4 | Change | All decisions above | The applied change, contracts preserved, rollback path | Change sequence, still unproven |
| 6 | `quality-release` | Verify | Every claim above | Concurrency and failure evidence, unrun checks labelled | Readiness verdict or explicit gaps |

Invariant first, because steps 2–4 all derive from it. Evidence last, because a sprint claim is being made.

## Step 6 — Coverage and gaps

Covered: oversell invariant, money precision, ambiguous charge, receipt delivery, readiness evidence.

Not covered by this route, and stated as such: the public checkout endpoint shape (`api-contracts`) if the client contract changes; PCI and cardholder-data handling (`security-privacy`) if card data touches our systems rather than the provider's. Both are named, not silently absorbed.

## Step 7 — What the route does not do

It does not choose the isolation level, the schema, or the retry budget. Those are the owners' decisions in step 1 through step 4. The routing output stops at the route and hands off to step 1.

## Contrast: the same request routed badly

> "This is a checkout feature, so use `api-contracts` in Change mode and ship it."

Three failures: the invariant surface has no owner, the mode jumped to Change with no decision on record, and the readiness claim has no evidence step. The answer would look complete and would oversell stock under concurrency.
