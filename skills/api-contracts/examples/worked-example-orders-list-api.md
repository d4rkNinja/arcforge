# Worked example: a list endpoint that almost shipped unbounded

> Calibration artifact: this shows the shape and depth a run of the `api-contracts` skill should produce. It is illustrative, not exhaustive; the papers remain authoritative.

**Request (as a user would phrase it):**

> Add GET /orders with search and sorting. The frontend wants all results in one call by default — no pagination UI planned.

## Papers consulted

- [016 Pagination](../references/papers/016-pagination.md) — cursor design, stable ordering, deep pagination
- [017 Filtering / Sorting / Query APIs](../references/papers/017-filtering-sorting-query-apis.md) — allowlists, complexity limits
- [012 Input Validation](../references/papers/012-input-validation.md) — query parameter validation
- [013 Error Architecture](../references/papers/013-error-architecture.md) — error contract for rejected queries
- 027 Indexing — in the `data-storage` skill, via the boundary map

## Assumptions (labeled)

- **A1 (assumption):** ~2,000 orders per tenant maximum today, growing 10×/year. *If false at 100×:* the "return everything" default becomes a denial-of-service vector against our own service.
- **A2 (assumption):** consumers are first-party web and mobile only. *If false:* a deprecation window is required for any third party already relying on unbounded responses.

## Pre-implementation questions answered

- **Default page size?** 50; maximum 200; `limit` above 200 is a 400, not a silent clamp (paper 016).
- **Ordering?** `created_at DESC, id DESC` tiebreaker; every sortable field is backed by an index and is order-stable under concurrent writes (papers 016, 027).
- **Filterable fields?** Allowlist: `status`, `created_after`, `created_before`, `customer_id`. Everything else is a 400 with the allowlist in the error detail (paper 017).
- **Search?** Prefix match on order reference via index; full-text deferred until paper 042 (Search) requirements are met.
- **Cursor?** Opaque base64 of `(created_at, id)`; decoded and validated server-side; rejected if malformed or older than retention (paper 016).

## Rule-to-decision map

| Rule (level) | Decision | Enforcement point | Verification |
|---|---|---|---|
| Maximum page size (MUST) | `limit` ∈ [1, 200], default 50 | Query schema validation before handler | `limit=201` → 400 with error code `QUERY_LIMIT_EXCEEDED` |
| Stable ordering (MUST) | Composite sort key with unique tiebreaker | Query builder + index `(tenant_id, created_at DESC, id DESC)` | Page walk during concurrent inserts: no duplicates, no gaps |
| Filter allowlist (MUST) | Closed set of fields/operators | Validator + repo layer reject unknown fields | `?filter=sql-injection-attempt` → 400, never reaches SQL |
| Cursor integrity (SHOULD) | Signed, versioned cursor payload | Cursor codec | Tampered cursor → 400; old-version cursor → clean error |
| Error contract (MUST) | Typed error body: code, message, details | Error middleware mapping validation failures | Contract test asserts response shape |

## Failure modes addressed

- Unbounded response memory — hard limit enforced at validation, not best effort.
- Duplicate/missing rows during pagination — keyset pagination, not offset.
- User-controlled sort field reaching SQL — allowlist plus parameterization.
- Silent truncation confusing clients — explicit `next_cursor` null semantics documented.

## Verification evidence

- Page walk of 10,000 orders under concurrent inserts: zero duplicates, zero skips.
- Contract tests: over-limit, unknown filter, malformed cursor, negative limit.
- Load probe: p95 latency with limit=200 stays within the endpoint budget; query plan uses the composite index (no seq scan).

## Stop-condition check

No stop condition remains: bounded response size, allowlisted inputs, stable ordering, defined error contract, and index-backed predicates (paper 027 check passed via explain plan).

## Deliverable summary

One endpoint, one index, a cursor codec, and a contract test suite — plus an explicit note to the frontend that "all results in one call" is rejected as a contract, with the cursor-walk alternative documented.
