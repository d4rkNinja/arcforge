# Think Through API & Client Contracts (`api-contracts`)

Production expertise for API surfaces and their clients. An API is a compatibility promise: every endpoint, error, cursor, and webhook is a contract with real clients — including old clients you no longer control.

## Modes

- **Think** clarifies requirements, invariants, risks, alternatives, decisions, and validation paths.
- **Review** inspects an existing artifact, repository, diff, or operating state and returns evidence-backed findings.
- **Change** applies approved decisions and keeps verification outstanding until proof is gathered.
- **Verify** reports tests, measurements, operational evidence, and residual risks without inventing missing proof.

If no mode is named, the skill infers one and states it. Combined work proceeds **Think → Review → Change → Verify**.

## What it covers

- REST, RPC, gRPC, and GraphQL endpoint and resource design;
- request lifecycle, deadlines, cancellation, and body limits;
- input validation and malformed-payload handling;
- error architecture: codes, status mapping, no internal detail leaks;
- pagination (offset vs cursor), filtering, sorting, and query complexity limits;
- bulk and batch operations with partial-failure reporting;
- API versioning, deprecation, sunset windows, breaking-change detection;
- data serialization and precision/timezone fidelity;
- webhooks: signing, timestamp/replay validation, bounded retries, dead-lettering;
- realtime channels (WebSockets/SSE): auth, reconnection, ordering, presence;
- SDK/client libraries and CLI-backend behavior.

## When to use

Adding or changing endpoints, error responses, pagination, versioning, webhooks, or realtime channels — and before any request that says "just return everything in one call."

## What a run produces

The output follows the active mode: Think returns decisions and open questions; Review returns findings without claiming changes; Change records the approved work and pending proof; Verify returns observed evidence and explicitly labels unrun checks.

Contract-complete implementations: bounded responses, allowlisted inputs, stable ordering, versioned changes with compatibility windows, and webhook/realtime semantics that survive duplicates and reconnects. The skill stops work on unbounded queries, leaky errors, or breaking changes without a migration path.

## Works well with

- `auth-access` for authentication and object-level authorization;
- `async-messaging` for events, webhooks at scale, and async side effects;
- `resilience-flow-control` for rate limits and quotas on the surface;
- `migration-evolution` for rolling out contract-breaking changes.

## Try it

~~~text
Add GET /orders with search and sorting. The frontend wants all results in
one call. Use api-contracts.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/api-contracts/SKILL.md)
- Worked example: [a bounded, cursor-paginated list endpoint](../../skills/api-contracts/examples/worked-example-orders-list-api.md)
