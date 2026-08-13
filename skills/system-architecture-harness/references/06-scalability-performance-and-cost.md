# Scalability, Performance, Overload, and Cost

Scaling is the controlled removal or isolation of measured bottlenecks while preserving correctness and operability.

## Contents

- 1. Performance Model
- 2. Scaling Order
- 3. Stateless Compute
- 4. Load Balancing and Routing
- 5. Partitioning and Hot Spots
- 6. Caching and CDN Performance
- 7. Datastore Performance
- 8. Queueing and Backlog
- 9. Overload Control
- 10. Capacity and Autoscaling
- 11. Multi-Region Performance and Cost
- 12. Cellular Architecture
- 13. Cost Model and FinOps Controls
- 14. Sustainability
- 15. Performance Test Plan
- 16. Common Mistakes

## 1. Performance Model

Build a budget for each critical journey:

```text
client/network + edge/gateway + service hops + datastore/cache
+ queue/wait + external dependencies + serialization = end-to-end latency
```

Track p50, p95, p99, and timeout/error behavior. Tail latency compounds across serial fan-out.

### Bottleneck tree

For every stage inspect:

- arrival rate and burst;
- service time distribution;
- queue wait;
- concurrency and resource pool;
- CPU, memory, disk IOPS/throughput, network, accelerator;
- lock/contention and database waits;
- downstream quota/latency;
- retries and amplification;
- per-tenant/key skew.

## 2. Scaling Order

Prefer the least complex effective move:

1. remove unnecessary work and synchronous dependencies;
2. fix algorithm/query/index/pathological serialization;
3. reduce payloads, round trips, and copies;
4. batch, compress, paginate, stream, or precompute;
5. cache at the correct layer;
6. vertically scale where cost-effective;
7. horizontally scale stateless work;
8. isolate workloads/pools/tenants;
9. partition state and traffic;
10. introduce specialized storage or redesign the workflow.

Each step needs a hypothesis, measurement, target, and rollback.

## 3. Stateless Compute

To scale horizontally:

- externalize durable sessions/state;
- make requests independently retryable where possible;
- use shared or replicated configuration with versioning;
- drain connections/jobs during deploy;
- avoid local-only locks, files, and caches for correctness;
- set pool sizes per instance and account for aggregate dependency load;
- use readiness only when the instance can serve correctly;
- define autoscaling signals and maximum fleet size.

Local caches are valid optimizations if loss/staleness behavior is explicit.

## 4. Load Balancing and Routing

Choose based on:

- L4 vs L7 needs;
- health/readiness and outlier ejection;
- least-loaded vs round-robin vs consistent hashing;
- session/connection affinity;
- locality and cross-zone/region cost;
- tenant or shard routing;
- weighted canary/blue-green traffic;
- slow-start and connection draining;
- failover and DNS/TTL behavior.

Health checks must detect whether the instance can serve safely, not merely whether its process responds.

## 5. Partitioning and Hot Spots

Analyze:

- key cardinality and distribution;
- largest key/tenant/channel;
- temporal hot partitions;
- celebrity fan-out;
- monotonic IDs concentrating index writes;
- cross-partition queries/transactions;
- rebalancing movement and cache churn.

Mitigations:

- key salting/bucketing with read aggregation;
- adaptive partitions;
- dedicated partitions/pools for whales;
- replicate hot read keys;
- hybrid fan-out-on-write/read;
- time bucketing plus spreading;
- hierarchical aggregation;
- request coalescing;
- admission quotas.

## 6. Caching and CDN Performance

Model:

- cacheable fraction;
- object popularity and size distribution;
- target hit rate;
- TTL and invalidation rate;
- origin load under cold cache;
- stampede and synchronized expiry;
- edge geography and egress savings;
- personalization/security boundaries;
- stale-while-revalidate/error behavior;
- cache poisoning and key correctness.

A cache can improve latency and reduce cost, but can also create stale correctness, memory cost, hot keys, and cold-start outages.

## 7. Datastore Performance

Measure:

- query plans and index selectivity;
- read/write amplification;
- transaction/lock duration;
- connection saturation;
- replica lag;
- compaction/checkpoint impact;
- working set vs memory;
- IOPS/throughput and storage latency;
- partition skew;
- backup/restore and maintenance load.

Controls:

- bounded queries and pagination;
- covering/partial/composite indexes aligned to access patterns;
- read replicas only for reads that tolerate lag;
- materialized views/precomputation;
- batch writes where semantics allow;
- connection pooling with global budget;
- separate OLTP/OLAP workloads;
- archival and partition pruning.

Do not add indexes without modeling write/storage/maintenance cost.

## 8. Queueing and Backlog

A queue absorbs a finite mismatch; it does not create processing capacity.

Define:

- maximum accepted queue depth/age;
- normal and recovery processing rates;
- priority classes;
- producer admission behavior;
- consumer concurrency bounds;
- lag SLO and alerts;
- backlog drain objective;
- expiration/TTL and stale-work policy;
- DLQ and replay tooling;
- dependency outage behavior.

Use the backlog formulas in `02-requirements-estimation-and-slos.md`.

## 9. Overload Control

Design for overload before autoscaling catches up.

### Controls

- request/body/query limits;
- rate and concurrency limits;
- admission control based on saturation;
- bounded queues and pools;
- deadline rejection before work begins;
- priority and fair scheduling;
- load shedding of optional/low-value work;
- graceful degradation and stale data;
- circuit breakers for repeated dependency harm;
- retry budgets;
- per-tenant quotas and bulkheads;
- backpressure to producers;
- cache/CDN fallback.

### Graceful degradation examples

- serve cached/stale catalog but block inventory-changing checkout if correctness is uncertain;
- omit recommendations/analytics while preserving core transactions;
- reduce feed depth or image quality;
- enqueue notification/report generation;
- return accepted/pending operation rather than holding long connection;
- disable nonessential model/tool calls and use deterministic fallback.

Never degrade a safety, authorization, accounting, or core invariant silently.

## 10. Capacity and Autoscaling

Autoscale on a signal causally related to work:

- concurrency or queue age/depth;
- CPU for CPU-bound work;
- request rate with known service time;
- active connections;
- custom saturation metric;
- model token/accelerator queue.

Avoid scaling solely on average CPU for I/O-bound or queued workloads.

Define:

- min/max capacity;
- scale-up/down windows;
- startup/warmup time;
- dependency capacity and quotas;
- regional/zone headroom;
- failover capacity;
- cost ceiling;
- protection against oscillation.

## 11. Multi-Region Performance and Cost

Evaluate:

- user-to-region routing;
- data ownership and write locality;
- synchronous replication latency;
- read freshness;
- cross-region egress and replication cost;
- cache/index/config propagation;
- failover spare capacity;
- conflict resolution;
- data residency;
- operational complexity and testing.

Active-active is justified when its availability/latency/business benefits exceed its correctness and operational cost. Active-passive or regional cells are often simpler.

## 12. Cellular Architecture

Cells isolate subsets of tenants/traffic into repeatable stacks.

Use when:

- blast-radius reduction is critical;
- tenant routing is stable;
- per-cell capacity is understood;
- independent deploy/failover is valuable.

Define:

- cell routing and control plane;
- tenant placement and movement;
- global services/dependencies;
- cell capacity and spare headroom;
- cross-cell data/features;
- incident isolation and evacuation;
- deployment wave and version skew.

## 13. Cost Model and FinOps Controls

### Cost dimensions

- baseline and burst compute;
- database/storage/IOPS/operations;
- replication and backup;
- network egress, NAT, cross-zone/region transfer;
- CDN/cache;
- queues/streams/search/analytics;
- observability ingestion, retention, and queries;
- model inference/training/vector search;
- licenses/support;
- engineers, on-call, compliance, and incident cost.

### Unit economics

Pick a business-relevant denominator:

- cost per order/payment;
- cost per active user/tenant;
- cost per GB-month stored and retrieved;
- cost per 1,000 notifications;
- cost per streamed minute;
- cost per AI task successfully completed.

### Controls

- ownership tags/account allocation;
- budget and anomaly alerts;
- unit-cost dashboards;
- right-sizing and autoscaling bounds;
- storage lifecycle/retention;
- reserved/committed capacity where stable;
- egress-aware architecture;
- query and cardinality budgets;
- model routing/caching/batching;
- monthly architecture cost review.

## 14. Sustainability

Improve resource efficiency without weakening requirements:

- right-size and autoscale;
- reduce unnecessary data movement and duplicate storage;
- compress/batch efficiently;
- use lifecycle tiers and delete unused data;
- choose efficient algorithms and hardware;
- schedule deferrable work where appropriate;
- measure utilization and work per useful outcome;
- keep software/runtime current when efficiency benefits are real.

## 15. Performance Test Plan

Include:

- representative payload and key distributions;
- normal, peak, burst, and 10× exploratory load;
- cold/warm cache;
- largest tenant/hot key;
- dependency latency/error injection;
- queue backlog and recovery drain;
- rolling deployment and node/zone loss;
- long soak for leaks/compaction/GC;
- data volume near target age;
- p50/p95/p99/error/saturation/cost;
- explicit pass/fail thresholds.

Benchmark in a representative topology. Microbenchmarks inform component choices but do not prove system behavior.

## 16. Common Mistakes

| Mistake | Correction |
|---|---|
| add replicas without identifying bottleneck | measure CPU, waits, I/O, locks, network, dependency quota |
| autoscaling used as overload strategy | add bounded admission, queues, retries, and degradation |
| average QPS and latency only | model peaks, bursts, skew, p99, largest tenant |
| shard early | maximize single-store safe capacity and create trigger/migration plan |
| queue hides slow consumer | define age/depth limit and drain rate |
| optimize component benchmark | validate end-to-end critical journey and tail latency |
| ignore observability/egress cost | include all variable and operational costs in unit economics |
| active-active chosen for prestige | quantify availability/latency benefit and conflict/operations cost |
