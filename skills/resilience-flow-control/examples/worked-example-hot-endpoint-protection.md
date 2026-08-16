# Worked example: Redis "forever cache" and the endpoint it would have taken down

> Calibration artifact: this shows the shape and depth a run of the `resilience-flow-control` skill should produce. It is illustrative, not exhaustive; the papers remain authoritative.

**Request (as a user would phrase it):**

> Put Redis in front of Postgres and cache query results forever. No TTL, no invalidation — it's just faster. Also the pricing page is getting hammered; do we need anything there?

## Papers consulted

- [037 Caching](../references/papers/037-caching.md) — TTL, invalidation, stampede, loss behavior
- [038 Rate Limiting](../references/papers/038-rate-limiting.md) — algorithms, scopes, fail policy
- [053 Timeout Engineering](../references/papers/053-timeout-engineering.md) — deadline budgeting
- [054 Circuit Breakers](../references/papers/054-circuit-breakers.md) — provider failure containment
- [131 Distributed Cache Coordination](../references/papers/131-distributed-cache-coordination.md) — multi-instance invalidation

## Assumptions (labeled)

- **A1 (assumption):** read-your-writes is required for 5 seconds after a user edits their own data. *If false:* longer TTLs become safe for self data; if *stronger*, caching self reads is unsafe entirely (paper 037).
- **A2 (assumption):** the pricing page is public and identical for all visitors. *If false:* rate-limit scope must move from IP toward session/account (paper 038).

## Pre-implementation questions answered

- **What failure is being defended against?** Postgres read load and latency; pricing-page abuse. Controls are chosen for those, not for fashion (workflow step 1).
- **TTL?** Public data 5 minutes; self data TTL 5 s plus explicit invalidation on write — "forever" rejected: stale authority, unbounded drift from truth (paper 037 MUST).
- **Invalidation?** Write-through invalidation (delete key) with versioned key prefixes; cross-instance via coordination topic (papers 037, 131).
- **Stampede?** Request coalescing (single-flight) per hot key plus jittered early refresh (paper 037).
- **Cache loss?** Cold-start falls back to Postgres with circuit-breaker protection; capacity for 100% miss at launch (papers 037, 054).
- **Rate limit?** Sliding window per IP for the public page (100/min) with 429 + Retry-After; limiter fails closed for this route because abuse is the defended failure (paper 038).

## Rule-to-decision map

| Rule (level) | Decision | Enforcement point | Verification |
|---|---|---|---|
| Named source of truth (MUST) | Postgres authoritative; cache derived with TTL + invalidation | Cache layer policy | Stale read test after write: bounded by 5 s |
| Stampede protection (MUST) | Single-flight + jittered refresh | Cache client | Expire 1 hot key under 500 parallel requests: 1 DB load |
| Bounded TTL (MUST) | 5 min public / 5 s self | Key TTL at write | Audit: no key written without TTL |
| Fail behavior stated (MUST) | Limiter fails closed on this route; cache miss fails open to DB | Middleware config | Limiter outage: requests blocked (intended), cache outage: served from DB |
| Deadline budget (MUST) | Cache 10 ms / DB 150 ms / endpoint 300 ms | Per-hop timeouts composing to the endpoint budget | Timeout composition test under latency injection |

## Failure modes addressed

- Unbounded staleness presenting old pricing — TTL + invalidation + versioned keys.
- Thundering herd on expiry — single-flight.
- Redis outage — cold-start capacity plus breaker on DB fallback.
- Retry storm against the limiter — 429 with Retry-After honored client-side.

## Verification evidence

- Stampede drill: one DB query for 500 concurrent misses on the same key.
- Invalidation drill: write on instance A; read on instance B sees fresh value within bound.
- Redis-kill drill: page stays up from DB within latency budget; breaker trips cleanly at threshold.
- Limiter drill: 101st request in window → 429; Retry-After honored; limiter-down → closed (blocked) as designed and alerted.

## Stop-condition check

No stop condition remains: no unbounded TTL, cache is not authoritative, stampede and loss behavior defined, rate limit has an explicit fail policy, timeouts compose into an end-to-end deadline.

## Deliverable summary

Cache client with TTL/invalidation/single-flight, cross-instance invalidation wiring, IP rate limit with fail-closed policy, per-hop timeout budget, and the outage/stampede drills above. The Postgres authority rules route to `data-storage`; consumer semantics route to `api-contracts`.
