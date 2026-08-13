# Domain Pattern Catalog

This catalog translates the 28 source-repository chapters into reusable architecture patterns. Load the relevant sections; do not copy a reference system blindly. Recalculate requirements and preserve domain-specific invariants.

## Contents

- 1. Scale from One Server to a Large Service
- 2. Back-of-the-Envelope Estimation
- 3. System Design Framework
- 4. Distributed Rate Limiter
- 5. Consistent Hashing and Membership
- 6. Distributed Key-Value Store
- 7. Distributed Unique-ID Generator
- 8. URL Shortener
- 9. Web Crawler
- 10. Notification Platform
- 11. News Feed
- 12. Chat System
- 13. Search Autocomplete
- 14. Video Platform
- 15. Cloud File Sync/Drive
- 16. Proximity Search
- 17. Nearby Friends / Live Location
- 18. Maps and Navigation
- 19. Distributed Message Queue
- 20. Metrics, Monitoring, and Alerting Platform
- 21. Ad Click/Event Aggregation
- 22. Hotel/Resource Reservation
- 23. Distributed Email Service
- 24. S3-Like Object Storage
- 25. Real-Time Gaming Leaderboard
- 26. Payment System
- 27. Digital Wallet
- 28. Stock Exchange / Matching Engine
- Cross-Pattern Selection Guide
- Pattern Misuse Warning

## 1. Scale from One Server to a Large Service

### Baseline progression

1. one deployable and one datastore;
2. separate stateless compute from state;
3. load balance stateless replicas;
4. add datastore replication/failover;
5. add cache/CDN for measured hot reads/assets;
6. externalize sessions and background work;
7. add queues for temporal decoupling;
8. partition state only after a measured limit;
9. add multi-region/cells when availability, latency, or residency requires it.

### Required clauses

- **IF** sessions are local, **THEN** either use affinity with failure limitations or externalize durable session state.
- **IF** replicas serve reads, **THEN** define lag and which reads tolerate it.
- **IF** CDN/cache is used, **THEN** define invalidation, stale behavior, origin fallback, and cost.
- **IF** data is sharded, **THEN** define key, skew, resharding, cross-shard queries, and joins.
- **IF** multiple regions are used, **THEN** define routing, data ownership, replication, failover, and deployment consistency.

## 2. Back-of-the-Envelope Estimation

Always calculate traffic, concurrency, storage, bandwidth, cache working set, queue drain, availability/cost, and growth with visible units. Use peak distributions, not average-only numbers. See `02-requirements-estimation-and-slos.md`.

## 3. System Design Framework

Use the complete workflow:

```text
clarify → quantify → invariants → boundaries → data/interfaces
→ critical flows → scale → failure → security → operations → cost
→ alternatives/ADRs → validation
```

Do not spend the entire design on the first diagram or low-level schema before critical requirements and invariants are known.

## 4. Distributed Rate Limiter

### Requirements

- policy dimensions: global, tenant, user, credential, endpoint, resource;
- rate, burst, concurrency, and quota semantics;
- low latency and bounded memory;
- distributed consistency/fairness requirement;
- clear errors and retry guidance;
- high availability and fail-open/fail-closed decision.

### Algorithms

- token bucket for bursts plus average rate;
- leaky bucket for smoothing;
- fixed window for simplicity with boundary burst risk;
- sliding window/log for accuracy at higher state cost;
- concurrency limits for expensive in-flight work;
- hierarchical limits for fairness and protection.

### Flow

```text
request → authenticate/derive trusted key → load policy/version
→ atomically evaluate/update counter/token state
→ allow and emit remaining/reset metadata OR reject with retry guidance
→ record decision/metrics without high-cardinality explosion
```

### Failure clauses

- atomic script/conditional update prevents race;
- multi-region approximation must state over-admission bound;
- limiter datastore outage needs explicit fail-open/closed by operation risk;
- policy changes need versioning and propagation;
- abuse can rotate identifiers, so combine identity/device/network/business signals where lawful.

## 5. Consistent Hashing and Membership

Use for routing keys across changing nodes while limiting movement.

### Design

- stable hash function and ring/token space;
- virtual nodes/tokens per physical node;
- weighted capacity;
- replication to distinct failure domains;
- membership/version source;
- movement/throttling and cache warmup;
- hot-key escape path.

### Clauses

- **IF** node membership changes, **THEN** version routing and tolerate client/server skew.
- **IF** virtual nodes balance token ranges, **THEN** still measure real key/value/work skew.
- **IF** ownership moves, **THEN** define dual-read/write, handoff, validation, and rollback.
- **IF** replication walks the ring, **THEN** ensure replicas do not share a failure domain.

## 6. Distributed Key-Value Store

### Core API and ASRs

- `put(key, value, options)` and `get(key, consistency)`;
- key/value size and throughput;
- latency, availability, durability;
- tunable consistency and conflict behavior;
- retention/TTL and versioning.

### Architecture

- consistent-hash partitioning with virtual nodes;
- N-way replication;
- coordinator routes reads/writes;
- commit log + memory table + immutable sorted tables for LSM-style storage;
- Bloom filters/indexes/compaction;
- gossip/member failure detection;
- hinted handoff/sloppy quorum where accepted;
- anti-entropy with Merkle-like comparisons;
- versions/vector or logical clocks for concurrent writes.

### Clauses

- state exact read/write quorum semantics and partition behavior;
- define sibling/conflict merge—never silently discard critical writes;
- compaction, tombstone, TTL, and repair must be bounded and observable;
- “eventual” needs convergence/repair and staleness behavior;
- quorum overlap alone does not prove linearizability.

## 7. Distributed Unique-ID Generator

### Options

- database sequence/range allocation;
- UUID/random ID;
- centralized ticket service;
- Snowflake-like timestamp + node + sequence;
- content-derived hash where identity semantics permit.

### Decision criteria

- uniqueness scope;
- sortability/locality;
- information leakage;
- generation availability and throughput;
- clock dependence;
- collision probability;
- bit/format lifetime.

### Snowflake-like flow

```text
read monotonicized wall time → verify no unsafe rollback
→ combine epoch timestamp, region/node identity, per-tick sequence
→ wait/advance safely on sequence exhaustion → emit ID
```

Define clock rollback, node-ID duplication, epoch rollover, and multi-process ownership.

## 8. URL Shortener

### Critical flows

**Create:** validate URL/policy → enforce quota → generate unique ID/token → atomically store mapping/owner/expiry → return short URL.

**Resolve:** parse token → edge/cache lookup → authoritative lookup on miss → expiry/abuse check → redirect → asynchronous analytics.

### Decisions

- random/Base62 encoded ID vs hash;
- collision handling and uniqueness constraint;
- 301 vs temporary redirect based on editability/analytics/cache semantics;
- custom aliases and tenant namespace;
- abuse/phishing/malware controls;
- expiration, deletion, and privacy;
- cache negative entries carefully.

### Failure clauses

- analytics must not block redirect;
- ID collision must be atomic, not pre-checked only;
- cache outage falls back within database capacity or sheds safely;
- redirect target changes require audit and cache invalidation.

## 9. Web Crawler

### Pipeline

```text
seed URLs → normalize/filter/dedupe → priority frontier
→ host/politeness scheduler → DNS/robots cache → downloader
→ content validation/dedupe → parser/extractor
→ discovered URLs back to frontier → content/index storage
```

### Key decisions

- scope, freshness, depth, content types, dynamic rendering;
- URL canonicalization and content fingerprint;
- per-host queues, rate, robots policy, crawl delay;
- priority/frontier fairness;
- DNS caching and timeout;
- distributed partition by host/domain;
- trap detection and maximum depth/parameter patterns;
- retry classification and dead-letter/quarantine;
- legal/terms/privacy compliance.

### Failure clauses

- **IF** crawler workers scale, **THEN** preserve per-host politeness globally.
- **IF** content is dynamic, **THEN** sandbox renderers and bound CPU/time/network.
- **IF** URLs are unbounded, **THEN** cap frontier, parameters, depth, object size, redirects, and retries.

## 10. Notification Platform

### Flow

```text
trusted trigger → validate template/audience/idempotency
→ resolve preferences/quiet hours/localization
→ create notification job and durable state
→ channel queue → worker → provider
→ callback/status/retry → final status/reconciliation/analytics
```

### Required design

- email/SMS/push/in-app channel adapters;
- template versioning and safe variables;
- user preferences, consent, unsubscribe, quiet hours;
- priority and emergency override governance;
- per-user/tenant/provider rate limits;
- provider credential isolation;
- dedupe/event ID;
- retries and DLQ by provider response;
- delivery vs provider acceptance semantics;
- feedback/bounce/token invalidation;
- audit and campaign safety.

Do not promise delivery when only provider acceptance is known.

## 11. News Feed

### Write path

create/validate post → store authoritative post → publish event → fan-out workers update follower feed indexes/caches → notification/analytics async.

### Read path

load feed IDs/ranking cursor → hydrate posts/authors/media → privacy/visibility filter → return cursor page → record feedback async.

### Fan-out choice

- fan-out on write for ordinary users and fast reads;
- fan-out on read for celebrity/high-fan-out publishers;
- hybrid based on follower count and activity;
- ranking/precompute vs real-time feature freshness.

### Clauses

- deletion/privacy change must invalidate fan-out copies;
- feed entries reference authoritative content, not duplicate sensitive truth;
- celebrity posts need bounded fan-out and cache strategy;
- cursor ordering and duplicate suppression must survive new inserts;
- recommendations/analytics must not block core feed.

## 12. Chat System

### Components

- stateless auth/profile/history APIs;
- stateful WebSocket/chat gateways;
- connection/session registry;
- message store partitioned by conversation/user;
- per-conversation ordering/ID service;
- delivery/fan-out workers;
- presence service with heartbeat/TTL;
- push notification for offline users;
- media/object storage.

### Message flow

```text
client message with idempotency ID → gateway auth/membership check
→ durable accept and sequence assignment → acknowledge sender
→ route/fan-out to online devices → store per-device/conversation cursor
→ push offline notification → delivery/read receipts as separate events
```

### Clauses

- ordering scope is conversation, not global;
- reconnect uses cursor/snapshot+delta;
- slow consumers get bounded buffers and disconnect/resume;
- presence is soft state with freshness, not absolute truth;
- group fan-out strategy changes for very large groups;
- multi-device read/delivery state must merge predictably;
- end-to-end encryption changes server search/moderation/recovery capabilities and must be designed explicitly.

## 13. Search Autocomplete

### Architecture

- collect privacy-safe query/selection signals;
- aggregate counts/trends by locale/time;
- build trie/FST or prefix index with top-k candidates at nodes;
- deploy versioned immutable snapshots to cache/query nodes;
- optional real-time trending overlay;
- filter policy/abuse before serving.

### Query flow

normalize prefix/locale → cache/index lookup → retrieve top candidates → apply policy/personalization → return under tight latency budget.

### Clauses

- prefix partitions must handle skew/hot first letters;
- top-k precomputation trades memory/build time for query latency;
- Unicode normalization and locale rules are part of correctness;
- harmful/private queries need filtering and retention controls;
- freshness and rebuild/cutover must be versioned.

## 14. Video Platform

### Upload flow

```text
create upload session → authorize quota/content policy
→ direct multipart/resumable upload to object storage
→ checksum/finalize metadata → enqueue processing DAG
→ transcode/package/thumbnails/moderation
→ publish renditions/manifest → CDN warm/invalidate → notify
```

### Playback flow

client fetches metadata/authorization → chooses manifest/rendition → adaptive HLS/DASH segments from CDN → origin fallback → QoE telemetry.

### Decisions

- codecs/rendition ladder by device/network/cost;
- transcoding DAG and worker specialization;
- resumable/direct upload and pre-signed URLs;
- DRM/encryption/watermark/access;
- CDN multi-region and origin shielding;
- moderation/copyright policy;
- storage lifecycle and hot/cold content;
- malformed vs retryable processing failures.

Analytics and recommendations stay off playback critical path.

## 15. Cloud File Sync/Drive

### Upload/sync flow

```text
chunk file → hash/dedupe candidate → resumable upload missing chunks
→ verify checksums → atomic metadata/version commit
→ publish change cursor → notify other devices
→ devices fetch metadata delta and missing chunks
```

### Required semantics

- versioned metadata and immutable chunks;
- per-file/user conflict policy and conflict copies;
- offline operation and sync cursor;
- chunking size/delta sync/compression;
- access sharing and revocation;
- encryption and tenant/user isolation;
- trash/version retention and quota;
- pending/uploaded/committed state machine;
- dedupe privacy boundary;
- rebuild/reconciliation between metadata and object storage.

Never expose a metadata version before required chunks are durable and authorized.

## 16. Proximity Search

### Index choices

- geohash/grid for simple hierarchical cells;
- quadtree for adaptive density;
- S2/Hilbert-like cells for spherical geometry/geofencing;
- R-tree/spatial database for rich spatial queries.

### Query flow

normalize location/radius/category → identify covering cells → query cell index (including boundary neighbors) → fetch candidates → exact distance/filter/rank → paginate/cache.

### Clauses

- approximate cell lookup must be followed by exact distance when correctness requires;
- query must include neighboring cells at boundaries;
- privacy/precision controls apply to user location;
- index update freshness and business source of truth differ;
- dense areas need adaptive cell/radius/result limits;
- partitioning by business ID vs geospatial key changes update/query costs.

## 17. Nearby Friends / Live Location

### Flow

client sends bounded-frequency location → auth/consent/precision validation → latest-location TTL store + optional history → publish to authorized friend/channel subscribers → connection servers filter exact distance and push → cursor/heartbeat manages freshness.

### Clauses

- location is sensitive: opt-in, purpose, precision, retention, blocking, audit;
- latest location is soft state with expiry;
- pub/sub partitioning and connection subscriptions must rebalance safely;
- friend add/remove/block changes revoke subscriptions promptly;
- high-degree users and geospatial channels need fan-out controls;
- background updates balance battery, bandwidth, and freshness;
- never infer exact presence from stale heartbeat.

## 18. Maps and Navigation

### Components

- map tile pipeline/object storage/CDN;
- geocoding and place index/cache;
- road graph partitioned into routing tiles;
- route planner with hierarchical pathfinding;
- traffic/location ingestion stream;
- ETA/ranking models;
- location history/telemetry store with privacy controls.

### Navigation flow

geocode origin/destination → fetch relevant graph hierarchy/traffic → compute candidate routes → rank ETA/preferences/restrictions → return route + map tile references → ingest anonymized/consented progress → reroute on deviation/traffic.

### Clauses

- vector/raster tile choice affects bandwidth/client compute;
- precompute stable road hierarchy; overlay dynamic traffic;
- location updates are high-volume and privacy-sensitive;
- offline maps need versioning/delta updates/storage budget;
- routing correctness includes road restrictions, closures, vehicle type, and freshness;
- fall back when live traffic/model is unavailable.

## 19. Distributed Message Queue

### Architecture

- topics and ordered partitions;
- brokers with leaders/followers;
- append-only segmented log and indexes;
- producer batching/compression/ack policy;
- consumer groups, offsets, heartbeats, rebalancing;
- metadata/coordination and partition assignment;
- retention/compaction and tiered storage;
- replication, leader election, ISR-like health.

### Clauses

- order is per partition unless stronger mechanism is justified;
- producer key determines distribution and ordering;
- consumer commit order defines duplicate/loss behavior;
- pull supports consumer-controlled backpressure;
- rebalancing must revoke ownership before new owner processes;
- DLQ is not disposal—provide inspection and safe replay;
- replication acknowledgement and data-loss behavior must be explicit;
- exact-once claims must define transaction boundary.

## 20. Metrics, Monitoring, and Alerting Platform

### Pipeline

agents/pull collectors → service discovery → ingestion collectors → durable buffer/stream → validation/aggregation/downsampling → TSDB/hot storage → cold object storage → query/cache → dashboards and alert evaluator → dedup/routing/notification.

### Clauses

- metric name + bounded tags + timestamp + value/schema;
- high cardinality needs budgets and rejection/aggregation;
- pull vs push chosen by reachability/lifecycle/security;
- aggregation point trades detail, cost, and recovery;
- raw/high-resolution retention shorter than downsampled history;
- alert state, dedupe, silence, routing, retries, and audit explicit;
- monitoring pipeline must monitor itself and degrade safely;
- telemetry loss should be distinguishable from healthy zero traffic.

## 21. Ad Click/Event Aggregation

### Pipeline

```text
edge event with unique ID and event time → durable raw log
→ validation/dedupe/privacy filtering → stream aggregation by window/dimensions
→ hot aggregate store → query/reporting
→ raw immutable storage for replay/backfill/reconciliation
```

### Decisions

- event time vs processing time;
- tumbling/hopping/sliding/session windows;
- watermark and allowed lateness;
- dedupe identity/window;
- top-N structures and hot ad keys;
- streaming (Kappa-like) vs batch+stream (Lambda-like);
- billing truth and reconciliation;
- star schema/dimensions and privacy.

### Clauses

- billing-relevant counts need raw evidence and reconciliation;
- late events need correction policy, not silent loss;
- duplicate effects handled at ingestion/aggregation/sink;
- checkpoint and replay must reproduce deterministic results;
- hot campaigns require key spreading and merge.

## 22. Hotel/Resource Reservation

### State and flow

```text
search availability (possibly cached/derived)
→ create idempotent reservation request
→ atomically reserve inventory under concurrency policy
→ pending payment/confirmation
→ confirm OR expire/cancel and release
→ reconcile inventory/reservations/provider
```

### Correctness options

- database unique/check constraints;
- pessimistic row/range locking under high contention;
- optimistic version/CAS with retry under low contention;
- preallocated inventory by resource/date;
- controlled overbooking threshold as business rule.

### Clauses

- search cache is not inventory authority;
- idempotency key prevents duplicate reservation;
- reservation hold has explicit expiry and release worker;
- payment timeout must query/reconcile before release/refund;
- date/timezone and room/resource type semantics explicit;
- shard by hotel/property/resource where transactions/locality align.

## 23. Distributed Email Service

### Outbound flow

compose/validate → persist message/attachments → enqueue → spam/virus/policy → domain/MX resolution → SMTP delivery with retry schedule → bounce/feedback → status/search/notification.

### Inbound flow

SMTP accept → authenticate/domain checks → spam/virus/size policy → durable message/attachment storage → mailbox metadata/index → real-time notify → client sync/search.

### Clauses

- separate metadata, blob, queue, and search responsibilities;
- partition mailbox data by user/domain with strong enough consistency;
- outbound retry distinguishes transient/permanent SMTP responses;
- deliverability requires SPF/DKIM/DMARC-like domain controls, IP reputation, feedback, and warmup;
- attachments use object storage and malware isolation;
- search is derived and rebuildable;
- privacy, retention, legal hold, and abuse/spam are first-class.

## 24. S3-Like Object Storage

### Data path

client/API/IAM → routing → placement/version metadata → data nodes across failure domains → checksum/ack → metadata commit. Download resolves metadata/placement then streams verified object/range.

### Control plane

bucket/object namespace, IAM/policy, placement/membership, repair, lifecycle, versions, multipart sessions, quotas, audit.

### Clauses

- immutable object versions simplify durability and repair;
- separate metadata from bulk data while preserving commit semantics;
- replication vs erasure coding chosen by object size, durability, repair, and cost;
- consensus protects placement/metadata authority;
- checksums and background scrubbing detect silent corruption;
- small objects need packing/log strategy without losing individual lifecycle;
- multipart abandoned uploads and tombstones require garbage collection;
- list operations need dedicated metadata index and consistency contract;
- placement spans real failure domains.

## 25. Real-Time Gaming Leaderboard

### Architecture

trusted game server submits score event → validate/idempotently append history → update in-memory sorted set/index → replicate/persist → queries return top-N, user rank, and neighbors → periodic archive/reset/rebuild.

### Data structures

Redis-like sorted set/skip list is a common fit for score/rank/range. Preserve durable event history or authoritative scores for rebuild.

### Clauses

- never trust direct client score updates;
- define score update semantics: replace, max, increment, latest;
- define ties and stable ranking;
- partition by score range for efficient global top/rank, or hash with scatter-gather tradeoff;
- monthly/season reset must be versioned and atomic to clients;
- user profile hydration is separate/cacheable;
- anti-cheat and audit are domain requirements.

## 26. Payment System

### Entities and states

Payment intent/order, attempt, authorization, capture, settlement, refund, dispute/chargeback, ledger entries, provider reconciliation.

### Pay-in flow

```text
merchant creates payment with idempotency key
→ validate amount/currency/merchant/order
→ persist payment state and ledger intent
→ use hosted/tokenized provider flow; never handle raw card data unless scope requires
→ provider executes authorization/capture
→ signed callback or polling updates state idempotently
→ ledger records balanced entries
→ merchant/customer receives durable status
→ settlement files reconcile provider/internal/bank records
```

### Clauses

- exact decimal/integer money and explicit currency/rounding;
- idempotency end-to-end, including provider;
- pending/unknown is a real state after timeout;
- webhook duplicates/out-of-order events tolerated;
- at-least-once plus idempotent effect, not magical exactly-once;
- double-entry ledger balances to zero per transaction/currency;
- side effects use durable queue/outbox;
- retries, DLQ, manual repair, refunds, and reconciliation explicit;
- hosted/tokenized card collection minimizes sensitive-data scope;
- never delete or mutate financial audit evidence destructively.

## 27. Digital Wallet

### Core invariant

Transfers preserve value and never create/destroy funds except authorized issuance/fees/corrections represented explicitly.

### Architecture options

- single transactional ledger when scale permits;
- partitioned ledger with account ownership;
- 2PC for strict atomic participants where cost is accepted;
- TCC (try/confirm/cancel) with reserved states;
- orchestrated saga with compensation/forward recovery;
- event-sourced deterministic state machine with replicated ordered log;
- sharded consensus groups plus transaction coordinator at extreme scale.

### Clauses

- debit-before-credit/reservation rules prevent overspend;
- each command is idempotent and state-transition guarded;
- out-of-order confirm/cancel handled explicitly;
- compensation is a new audited transaction;
- immutable event/ledger history supports replay and audit;
- snapshots accelerate replay but logs remain authoritative;
- CQRS read models are derived and freshness-labeled;
- reconciliation spans shards, external rails, and balances;
- distributed transaction failure and operator repair are first-class.

## 28. Stock Exchange / Matching Engine

### Critical path

```text
client/broker gateway → authenticate/rate/risk/pre-trade checks
→ deterministic sequencer assigns total order within symbol/partition
→ single-writer matching engine updates in-memory order book
→ emits immutable order/execution events
→ durable replicated log/recovery
→ wallet/clearing/reporting/market-data consumers off critical path
```

### Order book requirements

- fast lookup by order ID;
- fast add/cancel/execute;
- best bid/ask;
- ordered price-level iteration;
- FIFO or specified priority within price;
- deterministic replay.

A price-level map/tree plus linked order queues and order-ID index is a common shape; actual implementation must be benchmarked and allocation-conscious.

### Clauses

- no floating-point authoritative price/quantity;
- deterministic sequence and matching rules are correctness boundaries;
- critical path excludes logging/reporting/network calls not required for acceptance;
- event log and snapshots reconstruct engine state exactly;
- risk/fund/position holds prevent invalid orders before matching;
- cancel vs fill races resolve by sequenced order;
- partition by symbol/product while preserving per-book total order;
- hot symbols need dedicated engines/capacity, not split order across inconsistent writers;
- market data, candles, reporting, surveillance are derived consumers;
- failover must prevent two active matching writers and prove replay position;
- fairness, clock/sequence audit, security, KYC/market rules, and operational controls require domain specialists.

## Cross-Pattern Selection Guide

| Need | Start with |
|---|---|
| low-latency hot reads | cache/CDN + source-of-truth and invalidation rules |
| ordered durable events | partitioned append log + idempotent consumers |
| bursty deferred work | bounded queue + backpressure + drain model |
| high-integrity cross-step workflow | explicit state machine + idempotency + reconciliation; saga/TCC/2PC by invariant |
| rapidly changing membership | consistent hashing/virtual nodes + movement protocol |
| nearby spatial query | geohash/S2/quadtree + exact post-filter |
| real-time connections | stateful gateways + session discovery + resume cursor + bounded buffers |
| immutable large media/blobs | object storage + checksums + multipart + lifecycle + CDN |
| ranked top-N/rank | sorted set/index + durable rebuild source |
| financial value movement | exact arithmetic + double-entry ledger + idempotency + reconciliation |
| deterministic matching/order | sequencer + single-writer partition + durable replay log |
| derived search/analytics | authoritative facts + CDC/events + versioned rebuildable projection |

## Pattern Misuse Warning

A pattern is valid only if its assumptions match the system. Always re-evaluate:

- workload distribution and scale;
- consistency/invariant scope;
- team and operational maturity;
- data sensitivity and regulation;
- latency/geography;
- cost and migration horizon;
- failure and recovery goals.
