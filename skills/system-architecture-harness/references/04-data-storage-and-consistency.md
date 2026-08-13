# Data, Storage, and Consistency

Select storage from invariants, access patterns, data lifecycle, failure semantics, and operational capability. “SQL vs NoSQL” is too shallow to be an architecture decision.

## 1. Data Design Sequence

1. Identify entities, immutable facts, aggregates, and relationships.
2. Write invariants and state transitions.
3. List commands and query/access patterns with volume and latency.
4. Define source of truth and derived views.
5. Choose transaction and consistency boundaries.
6. Estimate data size, growth, retention, indexes, versions, backups, and rebuild time.
7. Select storage engines and partition/replication topology.
8. Define migration, archival, deletion, restore, reconciliation, and ownership.

## 2. Storage Decision Matrix

| Need | Likely fit | Verify before choosing |
|---|---|---|
| relational integrity, joins, transactions | relational database | write scale, partitioning, isolation, query plans, HA |
| key-based access at large scale | distributed key-value/document store | consistency, conditional writes, hot partitions, secondary queries |
| high-volume time-series writes | TSDB or wide-column/time-partitioned store | cardinality, retention, downsampling, late writes, query windows |
| full-text search/ranking | search index | source-of-truth rebuild, freshness, mapping evolution, shard sizing |
| graph traversal | graph database or modeled adjacency | traversal depth, write rate, partition crossing, operational maturity |
| immutable blobs/media/backups | object storage | multipart, checksums, versioning, lifecycle, egress, metadata/index |
| append/replay stream | durable log/message platform | partitioning, ordering, retention, replay, consumer state |
| sub-millisecond ephemeral state | cache/in-memory store | loss behavior, persistence, eviction, hot keys, memory cost |
| analytics/OLAP | columnar warehouse/lakehouse | ingestion freshness, partitioning, governance, cost, small-file handling |
| vector similarity | vector index or database extension | recall/latency, filters, update/delete, tenancy, rebuild, cost |

Use multiple stores only when their distinct responsibilities justify their consistency and operational costs.

## 3. Source of Truth and Derived Data

For every dataset classify it as:

- **authoritative state:** accepted current truth;
- **immutable fact/event:** evidence from which state can be derived;
- **derived projection/index/cache:** replaceable view;
- **audit/ledger:** append-focused evidence with controlled corrections;
- **temporary/staging:** bounded-lifetime intermediate data.

For derived data, define:

- source and transformation version;
- freshness contract;
- incremental update path;
- full rebuild path and duration;
- reconciliation checks;
- behavior while stale or rebuilding.

## 4. Invariants and Enforcement

Examples:

- account balance equals valid ledger entries;
- available inventory never falls below permitted floor;
- one active reservation per unique resource/time slot;
- a payment idempotency key maps to one semantic operation;
- each email address is unique within tenant scope;
- order state transitions follow the legal state machine;
- tenant data cannot be read or modified by another tenant.

Enforce at the strongest practical layer:

1. database constraint/transaction;
2. conditional compare-and-set/version check;
3. serialized owner/partition/actor;
4. consensus or distributed transaction where justified;
5. application check plus durable reconciliation when strict atomicity is impossible.

Application-only “check then write” is unsafe under concurrency unless protected by transaction, lock, or conditional write.

## 5. Transactions and Isolation

Define the anomaly tolerance per workflow:

- dirty reads;
- non-repeatable reads;
- phantom reads;
- lost updates;
- write skew;
- stale reads;
- fractured reads across replicas.

Use the weakest isolation level that still preserves invariants, not the weakest one that passes happy-path tests.

### Common controls

- unique/check/foreign-key constraints;
- atomic increment/decrement;
- compare-and-set with version;
- `SELECT ... FOR UPDATE` or equivalent;
- serializable transactions for compact high-value invariants;
- single-writer/partition ordering;
- advisory locks only with ownership, timeout, and fencing semantics.

### Optimistic vs pessimistic concurrency

Use optimistic concurrency when contention is low and retries are safe. Use pessimistic locking when conflicts are frequent or the cost of speculative work is high. Measure lock hold time and deadlock behavior.

## 6. Consistency Models

Specify consistency per operation, not per whole system.

- **linearizable:** operations appear instantaneous in one global order;
- **serializable:** transactions behave as if executed serially, without necessarily real-time ordering;
- **causal:** causally related operations are observed in order;
- **read-your-writes/session:** a client observes its own accepted changes;
- **monotonic reads:** later reads do not go backward;
- **bounded staleness:** reads lag by no more than a defined time/version;
- **eventual:** replicas converge without a fixed freshness guarantee.

CAP describes behavior during a network partition; it does not mean a system casually picks two properties forever. Also consider latency/consistency trade-offs during normal operation, topology, quorums, and application invariants.

## 7. Replication and Quorums

Define:

- leader/follower, multi-leader, or leaderless topology;
- synchronous vs asynchronous acknowledgement;
- replication factor and failure domains;
- read/write quorum and overlap requirements;
- stale/dirty replica handling;
- leader election and split-brain fencing;
- lag measurement and routing policy;
- failover/failback and consistency after recovery.

Generic quorum reasoning:

```text
N = replica count
W = write acknowledgements
R = read responses
R + W > N can provide overlapping read/write quorums under assumptions.
```

This does not by itself guarantee linearizability; conflict resolution, sloppy quorums, clock behavior, and implementation semantics matter.

## 8. Partitioning and Sharding

Choose a key that balances:

- distribution and hot-key risk;
- locality for common reads/writes;
- transaction scope;
- tenant isolation;
- resharding and routing stability;
- range scans and time-based access;
- deletion and residency boundaries.

### Strategies

| Strategy | Strength | Risk |
|---|---|---|
| hash partitioning | even distribution | poor range locality; scatter-gather queries |
| range partitioning | range/time locality | hot latest range, skew |
| directory/lookup routing | flexible placement | routing metadata availability/consistency |
| consistent hashing + virtual nodes | bounded movement during membership changes | operational complexity; still requires hot-key handling |
| tenant-based | isolation and ownership | large tenants create skew |
| composite/hierarchical | balances locality and distribution | more complex routing and migrations |

### Resharding plan

State:

- trigger metric;
- new shard creation;
- data copy/backfill;
- write routing during movement;
- consistency validation;
- traffic cutover;
- cleanup and rollback;
- handling of cross-shard transactions and indexes.

## 9. IDs, Ordering, and Time

### IDs

Choose based on:

- uniqueness scope;
- sortability/locality;
- generation availability;
- information leakage;
- storage/index size;
- clock dependence;
- collision and rollover behavior.

Options include database sequences, UUIDs, random tokens, Snowflake-like time/node/sequence IDs, and centralized allocation ranges.

Do not use a timestamp alone as a unique ID. If time-based IDs are used, define clock rollback, node identity, sequence exhaustion, and epoch/bit rollover.

### Time

- use UTC instants for machine events;
- preserve user timezone separately for business calendars;
- use monotonic clocks for elapsed durations/timeouts;
- do not rely on wall-clock timestamps for distributed ordering;
- define clock synchronization tolerance;
- use logical/sequence ordering when correctness depends on order.

## 10. Caching

A cache design must answer:

- What is cached and why?
- What is the source of truth?
- Cache-aside, read-through, write-through, write-behind, or refresh-ahead?
- TTL and freshness requirement?
- Invalidation/update path?
- Miss and cache-outage behavior?
- Stampede protection: request coalescing, locks, jittered TTL, stale-while-revalidate?
- Hot-key replication or local cache?
- Negative caching and its TTL?
- Eviction policy and memory ceiling?
- Tenant isolation and sensitive-data controls?
- Warmup and cold-start behavior?

Never make the cache the accidental only copy unless it is intentionally durable state with matching guarantees.

## 11. Search Indexes and Materialized Views

Treat search/index systems as derived unless the product explicitly makes them authoritative.

Define:

- source event/CDC path;
- indexing delay SLO;
- document/version identity;
- out-of-order update handling;
- mapping/schema evolution;
- reindex strategy and alias/cutover;
- deletion/privacy propagation;
- reconciliation and rebuild;
- query filters and tenant enforcement;
- shard/segment sizing and hot queries.

## 12. Data Lifecycle

For each class, specify:

- purpose and owner;
- collection source and consent/legal basis where relevant;
- classification and access roles;
- retention and archival tier;
- deletion/tombstone/erasure process;
- backups and expiration from backups;
- export/portability;
- residency and cross-border movement;
- encryption and key lifecycle;
- audit and lineage;
- restore priority and RPO.

Data that cannot be deleted because it was copied into opaque logs, prompts, or events is an architectural privacy failure.

## 13. Schema and Contract Evolution

Prefer expand/contract:

1. add backward-compatible field/table/index;
2. deploy readers tolerant of old/new;
3. deploy writers producing new form;
4. backfill with throttling and checkpoints;
5. validate/reconcile;
6. switch reads;
7. stop old writes;
8. remove old schema after compatibility window.

Rules:

- consumers ignore unknown optional fields;
- never reuse field meanings;
- distinguish absent, null, default, and zero;
- avoid changing event meaning in place;
- version transformations and retain replay compatibility;
- large index/schema changes need load and lock-impact testing.

## 14. Cross-Boundary Data Patterns

### Transactional outbox

Commit domain state and an outbox record in one local transaction. A relay publishes the event; consumers deduplicate. Define ordering, cleanup, relay lag, and replay.

### Inbox/idempotent consumer

Store processed message IDs or semantic idempotency keys in the same transaction as the effect. Define dedupe retention based on replay window.

### CDC

Useful for propagating authoritative changes without application dual writes. Define schema semantics, ordering, snapshots, tombstones, lag, and recovery.

### Saga/workflow

Model explicit steps, intermediate states, timeouts, retries, compensation, non-compensable actions, and operator repair. Compensation is a business action, not a database rollback.

### Two-phase commit

Use only when atomicity across participants outweighs coordinator/blocking/availability/operational costs and all participants support the protocol reliably.

## 15. Financial and High-Integrity Data

- represent money as integer minor units or fixed-precision decimal with currency;
- never use binary floating point for authoritative amounts;
- model rounding rules explicitly;
- use immutable double-entry ledger entries where appropriate;
- preserve an idempotency key through every external processor;
- separate authorization, capture, settlement, refund, and chargeback states;
- reconcile internal ledger, provider records, and bank/settlement files;
- make corrections through compensating entries, not destructive edits;
- audit privileged actions and separation of duties;
- classify mismatches and provide operator workflows.

## 16. Object and Blob Storage

Define:

- object identity and versioning;
- metadata vs data path;
- multipart/chunked upload and resume;
- checksums at write/read/scrub;
- replication vs erasure coding;
- placement across failure domains;
- small-object strategy;
- encryption and key ownership;
- lifecycle and legal hold;
- deletion/tombstones/garbage collection;
- metadata list/index behavior;
- restore and corruption repair;
- egress and CDN strategy.

## 17. Common Mistakes

| Mistake | Better approach |
|---|---|
| database chosen from brand familiarity | derive from invariants, access patterns, scale, recovery, operations |
| one consistency label for whole system | specify semantics per command/query/journey |
| replicas treated as backups | isolate/version backups and test restore |
| sharding added before measuring | optimize/scale single store, then shard with migration plan |
| cache invalidation omitted | define source, TTL, update, stale behavior, outage behavior |
| event log contains private data forever | minimize/tokenize, define deletion strategy and access |
| search index used as only truth | keep authoritative source and rebuild path |
| dual writes to DB and broker | local transaction + outbox/CDC or explicit protocol |
| “unique” enforced by pre-check | use atomic unique constraint/conditional write |
