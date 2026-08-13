# APIs, Messaging, and Workflows

Interfaces are long-lived contracts and failure boundaries. Design them around semantics, compatibility, deadlines, identity, and recovery—not endpoint aesthetics alone.

## 1. Interaction Choice

| Interaction | Use when | Key design obligations |
|---|---|---|
| REST/HTTP | public/resource APIs, broad interoperability, cacheable queries | resource semantics, status/errors, idempotency, pagination, versioning |
| gRPC/RPC | internal typed low-latency calls, streaming, controlled clients | deadlines, compatibility, status mapping, load balancing, observability |
| WebSocket | bidirectional long-lived real-time sessions | connection lifecycle, auth refresh, backpressure, resume, fan-out |
| SSE | server-to-client ordered event stream over HTTP | cursor/resume, heartbeat, buffering, proxy limits |
| webhook | asynchronous callback to external consumer | signature, replay prevention, retries, dedupe, ordering, reconciliation |
| queue | work distribution and temporal decoupling | delivery, visibility/lease, retry, DLQ, idempotency, backpressure |
| pub/sub log | event fan-out, replay, stream processing | partitions, ordering key, retention, consumer offsets, schema evolution |
| batch/file exchange | large periodic integration, settlement/reconciliation | manifest, checksum, atomic publication, partial files, reruns, audit |

## 2. API Contract Checklist

For every operation define:

- business purpose and actor;
- authentication and authorization;
- tenant and resource scope;
- request schema, validation, limits, and content type;
- command/query semantics and side effects;
- idempotency and duplicate requests;
- consistency and freshness of response;
- deadline/timeout and cancellation;
- error model and retryability;
- pagination/filter/sort/search behavior;
- rate/quota limits and `Retry-After`-like guidance;
- versioning, compatibility, deprecation, and ownership;
- audit, metrics, traces, and data redaction.

Use OpenAPI for HTTP contracts and AsyncAPI or equivalent schema contracts for event-driven APIs when useful. Generated documentation does not replace semantic review.

## 3. Resource and Command Semantics

Prefer resource-oriented operations for stable domain entities, but use explicit commands when an operation represents a business transition rather than CRUD.

Examples:

```text
POST /orders                    create order
GET  /orders/{id}               fetch current view
POST /orders/{id}:cancel        request domain transition
POST /payments/{id}:capture     explicit side effect
```

Rules:

- do not expose database tables as API design;
- make illegal state transitions explicit errors;
- avoid ambiguous generic endpoints such as `/execute`;
- return an operation/workflow resource for long-running work;
- include correlation and stable resource identifiers;
- distinguish accepted, pending, completed, failed, canceled, and unknown states.

## 4. Idempotency

Idempotency protects semantic effects, not only HTTP retries.

For a mutating operation define:

- key source: client-generated, server-issued, or business-natural key;
- scope: actor/tenant/operation/resource;
- normalized request fingerprint;
- dedupe retention window;
- atomic storage with the business effect;
- behavior for same key/same request;
- behavior for same key/different request;
- response replay and status lookup;
- propagation to downstream providers;
- cleanup and privacy.

Never implement idempotency as an eventually consistent cache check before an unprotected write.

## 5. Error Model

Errors should be stable, machine-readable, safe, and actionable.

Include:

- stable type/code;
- human-readable title/detail without secrets;
- HTTP/RPC status;
- field validation details;
- correlation/trace ID;
- retryable flag or documented retry classification;
- optional retry delay;
- current operation/resource state when safe.

Classify:

- validation/client errors—do not retry unchanged;
- authentication/authorization—refresh/escalate, not blind retry;
- conflict/precondition—refresh state or use version;
- quota/rate limit—retry after bounded delay;
- transient dependency/service errors—bounded retry if idempotent;
- permanent business failure—surface final state;
- ambiguous timeout—query by idempotency/operation ID before retrying.

## 6. Deadlines, Timeouts, Retries, and Cancellation

### Deadline propagation

Set an end-to-end deadline and allocate per hop. Downstream work must stop when the result is no longer useful where possible.

### Retry policy

Define:

- retryable failure set;
- max attempts and elapsed time;
- exponential backoff with jitter;
- retry budget to prevent load amplification;
- per-attempt timeout smaller than total deadline;
- idempotency/conditional effect;
- fallback or final error;
- observability of attempts and exhausted retries.

Do not layer uncontrolled retries at client, gateway, service, SDK, and database. Coordinate them.

### Hedging

Hedged requests can reduce tail latency for safe, idempotent reads but increase load. Use only with delayed hedges, budget, duplicate cancellation, and evidence.

## 7. Pagination and Queries

Prefer cursor/keyset pagination for large or changing datasets.

Define:

- stable sort key and tie-breaker;
- opaque cursor version and expiry;
- page-size max/default;
- filter compatibility with indexes;
- consistency snapshot or acceptable movement between pages;
- authorization on every page;
- cost limits for deep/unbounded queries.

Offset pagination is acceptable for small/static data or user interfaces where drift is harmless.

## 8. Rate Limiting and Quotas

Choose policy based on goal:

- abuse protection;
- fairness/noisy-neighbor control;
- dependency protection;
- contractual plan quotas;
- cost control;
- admission control under overload.

Algorithms:

- token bucket—bursts with average rate;
- leaky bucket—smooth processing;
- fixed window—simple but boundary bursts;
- sliding log/window—more accurate, more state;
- concurrency limit—protects work-in-flight and latency;
- hierarchical quota—global, tenant, user, endpoint, resource.

Define key, scope, distribution, consistency, fail-open/fail-closed behavior, headers/errors, clock/window semantics, storage, race handling, and monitoring.

## 9. Event Contract

Every event must declare:

- event name, semantic meaning, and owner;
- event ID and causation/correlation IDs;
- aggregate/entity ID and tenant;
- occurred-at and observed/published-at timestamps;
- schema version and compatibility rules;
- partition/ordering key;
- whether it is a fact, command, notification, or snapshot;
- sensitive fields and retention;
- replay behavior and side-effect safety.

Avoid generic “entity updated” events when consumers require hidden database knowledge. Prefer meaningful facts such as `OrderConfirmed` with enough stable context.

## 10. Message Delivery Semantics

### At-most-once

Possible loss, no broker redelivery. Use when loss is acceptable and duplicates are worse or data is continuously refreshed.

### At-least-once

Redelivery possible. Most business systems should make consumers idempotent and support replay.

### Effectively/exactly once

Define boundary precisely. Broker transaction guarantees may cover producer/broker/consumer offsets but not arbitrary external side effects. End-to-end correctness usually combines durable delivery, atomic state+dedupe, and reconciliation.

## 11. Ordering

Global order is expensive and rarely required. Define the smallest ordering scope:

- per entity/order/account/device;
- per partition;
- per symbol in an exchange;
- per conversation;
- per workflow.

Handle:

- duplicate sequence numbers;
- gaps and delayed messages;
- out-of-order arrival;
- producer retries and leader failover;
- consumer parallelism;
- rebalancing;
- snapshot plus delta recovery.

Use sequence/version checks and quarantine/repair rather than silently applying stale events.

## 12. Queue and Consumer Design

Define:

- topic/queue purpose;
- partition count and key;
- retention and maximum message size;
- producer durability acknowledgement;
- consumer group and concurrency;
- visibility timeout/lease and extension;
- batch size and processing timeout;
- offset/ack commit order;
- retry schedule and maximum age;
- DLQ/quarantine with replay tooling;
- poison message isolation;
- backpressure and lag SLO;
- autoscaling metric and upper bound;
- schema registry/compatibility;
- disaster recovery and replay source.

### Backpressure

Consumers must signal or enforce bounded demand. Options:

- pull with bounded batches;
- semaphore/concurrency cap;
- pause partitions;
- bounded in-memory buffers;
- reject/defer producers;
- spill to durable storage;
- shed low-priority work.

An unbounded consumer buffer merely moves the queue into process memory.

## 13. Transactional Outbox Flow

```text
1. Begin local DB transaction.
2. Validate invariant and write domain state.
3. Write outbox row with event ID/payload/version.
4. Commit once.
5. Relay publishes to broker, retrying safely.
6. Mark/delete outbox after acknowledgement according to retention policy.
7. Consumer applies idempotently in local transaction.
8. Reconcile relay lag and stuck rows.
```

Define whether order is per aggregate, table, or relay partition.

## 14. Long-Running Workflows

Use an explicit state machine/orchestrator when steps span services or time.

For each step:

- precondition and command;
- idempotency key;
- timeout/deadline;
- retry policy;
- success/failure event;
- compensation or forward-recovery action;
- non-compensable side effects;
- operator intervention;
- audit evidence.

Example states:

```text
REQUESTED → RESERVED → PAYMENT_PENDING → CONFIRMED
         ↘ REJECTED      ↘ PAYMENT_FAILED → RELEASE_PENDING → FAILED
```

Never hide workflow state only in queue position or transient logs.

## 15. WebSocket/SSE Real-Time Design

Specify:

- connection authentication and token refresh;
- routing/discovery and sticky/stateful placement;
- connection limits and heartbeat;
- per-client outbound buffer and slow-consumer policy;
- message sequence/cursor and reconnect resume;
- server drain during deploy;
- presence freshness and TTL;
- fan-out topology and celebrity/hot-channel handling;
- offline notifications and history source;
- multi-device synchronization;
- regional routing and failover.

## 16. Webhooks

Provider:

- sign payload and timestamp;
- use stable event ID;
- retry with exponential backoff for bounded duration;
- expose delivery history and manual replay;
- preserve ordering metadata but do not promise global order casually;
- limit payload and redact secrets.

Consumer:

- verify signature, timestamp, and endpoint ownership;
- acknowledge quickly after durable acceptance;
- deduplicate event ID;
- process asynchronously;
- tolerate duplicates, missing, and out-of-order events;
- reconcile by querying provider/source of truth.

## 17. Contract Testing and Governance

- producer schema compatibility in CI;
- consumer-driven or provider contract tests where valuable;
- generated clients pinned and reviewed;
- API/event catalog with owner and lifecycle;
- deprecation telemetry by consumer;
- security tests for object/function/property authorization;
- replay tests using historical events;
- version skew tests across rolling deployment windows.

## 18. Common Mistakes

| Mistake | Correction |
|---|---|
| queue added to make system “reliable” | define durable acceptance, delivery, consumer idempotency, lag, replay, DLQ |
| retry on every 5xx everywhere | coordinate bounded retries under one deadline and budget |
| event name mirrors database CRUD | publish stable domain facts with clear ownership |
| HTTP 200 with hidden business failure | use explicit operation state/error contract |
| webhook treated as exactly once | authenticate, dedupe, tolerate reorder, reconcile |
| offset pagination for huge changing feed | use cursor/keyset and define snapshot/drift |
| global event ordering demanded | reduce order scope to the entity/partition that needs it |
| idempotency key only in gateway cache | store atomically with the durable effect and propagate downstream |
