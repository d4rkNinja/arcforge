# Think Through Resilience & Flow Control (`resilience-flow-control`)

Production expertise for surviving load and dependency failure: retry storms, synchronized expiry, thundering herds, timeouts that compose badly, and rate limits that fail open exactly when they matter.

## Modes

- **Think** clarifies requirements, invariants, risks, alternatives, decisions, and validation paths.
- **Review** inspects an existing artifact, repository, diff, or operating state and returns evidence-backed findings.
- **Change** applies approved decisions and keeps verification outstanding until proof is gathered.
- **Verify** reports tests, measurements, operational evidence, and residual risks without inventing missing proof.

If no mode is named, the skill infers one and states it. Combined work proceeds **Think → Review → Change → Verify**.

## What it covers

- caching: placement, TTL, eviction, invalidation, warming, stampede protection, hot keys;
- distributed cache coordination across instances;
- rate limiting: algorithms, scopes (IP/user/tenant/endpoint), distributed state, fail-open vs fail-closed;
- quotas: soft/hard limits, reservation, reset windows;
- external integrations: provider contracts, outages, degraded modes, exit risk;
- retries: classification, caps, budgets, backoff with jitter, honoring provider pushback;
- timeouts: per-hop and end-to-end deadlines, cancellation propagation;
- circuit breakers with real fallbacks; bulkheads; load shedding;
- backpressure and admission control for queues and workers.

## When to use

Adding or changing caching, rate limiting, quotas, retries, timeouts, circuit breakers, or overload protection — and before accepting "cache forever, no TTL needed" or "autoscaling will handle spikes."

## What a run produces

The output follows the active mode: Think returns decisions and open questions; Review returns findings without claiming changes; Change records the approved work and pending proof; Verify returns observed evidence and explicitly labels unrun checks.

A defense map: each named failure → mechanism, bounds, and fallback; explicit fail-open/closed decisions; timeouts that compose into an end-to-end deadline; outage drills. The skill stops work on unbounded TTLs, caches treated as source of truth, retries without caps, or autoscaling presented as overload control.

## Works well with

- `transactions-consistency` for idempotent effects under retry;
- `async-messaging` for queue depth and worker bounds;
- `api-contracts` for rate-limit responses and headers clients see;
- `quality-release` for outage and overload drills.

## Try it

~~~text
Put Redis in front of Postgres and cache query results forever. No TTL, no
invalidation — it's just faster. Use resilience-flow-control.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/resilience-flow-control/SKILL.md)
- Worked example: [caching, stampede defense, and rate limiting for a hot endpoint](../../skills/resilience-flow-control/examples/worked-example-hot-endpoint-protection.md)
