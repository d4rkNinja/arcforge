# Source Repository Coverage and Gap Analysis

## Source Access Note

The requested URL was `https://github.com/d4rkNinja/system-design-notes`. That fork could not be fetched directly through the available web or container network path during creation of this package. The accessible public repository `https://github.com/liquidslr/system-design-notes` has the same project name and the complete 28-chapter structure referenced by the request. This skill was mapped chapter by chapter against that accessible source and then extended independently.

No chapter prose is copied into the skill. The package converts concepts into original operating rules, decision clauses, review gates, templates, and tests.

## Contents

- Source Access Note
- Chapter-by-Chapter Coverage
- Material Additions Beyond the Source Repository
- Corrections and Nuance Added
- Maintenance Rule

## Chapter-by-Chapter Coverage

| # | Source chapter | Concepts carried into this skill | Primary location |
|---:|---|---|---|
| 1 | Scaling | stateless tiers, load balancing, replicas, cache/CDN, queues, sharding, multi-DC | `06-scalability-performance-and-cost.md`, domain catalog §1 |
| 2 | Back-of-envelope estimation | QPS, peak, storage, bandwidth, cache, server/cost estimates | `02-requirements-estimation-and-slos.md` |
| 3 | System Design Framework | clarify, high-level design, deep dive, trade-offs, wrap-up | `01-workflow-and-decision-gates.md`, `SKILL.md` |
| 4 | Rate Limiter | token/leaky buckets, windows, Redis atomicity, distributed policy | domain catalog §4; APIs §8 |
| 5 | Consistent Hashing | ring, virtual nodes, bounded movement, membership | domain catalog §5; data partitioning |
| 6 | Key-Value Store | partitioning, replication, quorums, conflicts, gossip, repair, LSM path | domain catalog §6; data/consistency |
| 7 | Unique-ID Generator | UUID/sequence/ticket/Snowflake choices and clock risks | domain catalog §7; data IDs/time |
| 8 | URL Shortener | Base62/ID, redirect/cache, create/resolve flow, abuse | domain catalog §8 |
| 9 | Web Crawler | frontier, politeness, robots, DNS, dedupe, traps, distributed workers | domain catalog §9 |
| 10 | Notification System | channel queues/workers/providers, templates, preferences, retries/dedupe | domain catalog §10 |
| 11 | News Feed | fan-out write/read/hybrid, cache layers, ranking/hydration | domain catalog §11 |
| 12 | Chat | WebSockets, stateful gateways, message order, presence, multi-device sync | domain catalog §12 |
| 13 | Search Autocomplete | trie/top-k, aggregation, prefix sharding, cache, Unicode/trending | domain catalog §13 |
| 14 | YouTube | resumable upload, transcoding DAG, object/CDN, adaptive playback | domain catalog §14 |
| 15 | Google Drive | chunks/hashes, metadata, sync cursor, conflict/versioning, notifications | domain catalog §15 |
| 16 | Proximity Service | geohash/quadtree/S2-like indexes, boundary cells, exact distance | domain catalog §16 |
| 17 | Nearby Friends | live location TTL, WebSocket fan-out, pub/sub, privacy/battery | domain catalog §17 |
| 18 | Google Maps | tiles/CDN, geocoding, routing graph, traffic ingestion, ETA | domain catalog §18 |
| 19 | Distributed Message Queue | partitions, brokers, WAL, producers, consumers, offsets, replication | domain catalog §19; APIs/messaging |
| 20 | Metrics Monitoring and Alerting | collection, TSDB, cardinality, aggregation, alert pipeline | domain catalog §20; observability |
| 21 | Ad Click Event Aggregation | raw log, windows/watermarks, dedupe, stream/batch, reconciliation | domain catalog §21 |
| 22 | Hotel Reservation | inventory-by-date, idempotency, locking/constraints, concurrency | domain catalog §22 |
| 23 | Distributed Email | inbound/outbound queues, SMTP, attachments, search, deliverability | domain catalog §23 |
| 24 | S3-like Object Storage | metadata/data separation, placement, consensus, checksums, EC, GC | domain catalog §24 |
| 25 | Gaming Leaderboard | sorted set/skip-list, rank/top-N, partitioning, rebuild history | domain catalog §25 |
| 26 | Payment System | PSP workflow, idempotency, ledger, pending/retries, reconciliation | domain catalog §26; data financial rules |
| 27 | Digital Wallet | TCC/2PC/Saga/event sourcing, Raft groups, replay/CQRS | domain catalog §27 |
| 28 | Stock Exchange | sequencer, matching engine, order book, critical path, deterministic replay | domain catalog §28 |

## Material Additions Beyond the Source Repository

The source is an excellent interview-note collection, but production architecture needs additional cross-cutting controls. This package adds the following.

### 1. Business and decision traceability

- business outcomes and architecturally significant requirements;
- decision horizon, non-goals, assumption register;
- alternatives, consequences, reversal triggers, ADRs;
- architecture fitness functions and implementation slices.

### 2. Correctness-first modeling

- explicit invariants before storage selection;
- state machines and legal transitions;
- isolation anomalies and transaction boundaries;
- exact ordering scope, ambiguous outcomes, reconciliation;
- source-of-truth vs derived-data classification.

### 3. Architecture-style and organizational decisions

- modular monolith default and evidence required for microservices;
- distributed-monolith detection;
- control-plane/data-plane separation;
- cellular architecture and tenancy models;
- team ownership, cognitive load, build-vs-buy, vendor exit.

### 4. Modern API and event governance

- OpenAPI/AsyncAPI/CloudEvents-aligned contract thinking;
- stable machine-readable errors;
- pagination, deadlines, cancellation, compatibility, deprecation;
- transactional outbox/inbox, CDC, schema evolution;
- webhooks, SSE, gRPC, contract tests.

### 5. Resilience, disaster recovery, and overload engineering

- end-to-end deadlines and coordinated retry budgets;
- bounded queues/pools/fan-out and backpressure;
- load shedding, admission control, graceful degradation;
- bulkheads, circuit breakers, leases and fencing;
- corruption detection, restore proof, game days;
- multi-region authority, failback, RTO/RPO.

### 6. Security, privacy, abuse, and supply chain

- threat modeling and trust boundaries;
- object/function/property/workflow authorization;
- NIST-style Zero Trust resource access;
- tenant isolation across data/cache/search/events/AI;
- privacy lifecycle, deletion, residency, vendor handling;
- abuse/fraud and denial-of-wallet;
- SBOM/provenance/build and dependency controls;
- security incident and break-glass operations.

### 7. Production observability and delivery

- user-journey SLIs/SLOs/error budgets;
- traces, logs, metrics, audits, profiles, cardinality budgets;
- actionable alerting and runbook contracts;
- progressive delivery and error/correctness gates;
- expand/contract migrations, shadow/strangler/CDC;
- service catalog, ownership, lifecycle/deprecation.

### 8. Cost, FinOps, and sustainability

- full unit economics including egress, observability, backups, people;
- 1×/10×/100× sensitivity and cost breakpoints;
- budgets/anomaly/allocation/right-sizing/retention;
- resource efficiency and sustainability.

### 9. AI, RAG, ML, and agents

- model gateway/routing and provider failure;
- RAG ingestion/query, ACL filtering, grounding, provenance;
- evaluation datasets, quality/safety/cost/latency gates;
- prompt injection, excessive agency, tool sandbox and policy;
- human approval for high-impact actions;
- memory privacy/poisoning and model/prompt/index rollback;
- NIST AI RMF and OWASP GenAI risk framing.

### 10. Executable quality controls

- 100-point architecture scorecard with non-waivable gates;
- Markdown architecture validator;
- Agent Skills package validator;
- pressure scenarios and acceptance tests;
- reusable architecture/ADR/SLO/threat/risk/failure templates.

## Corrections and Nuance Added

Some interview-note simplifications are useful pedagogically but require production nuance:

- CAP applies specifically under partitions; consistency/latency trade-offs also exist during normal operation.
- `R + W > N` alone does not prove linearizability.
- replication does not replace isolated backups or restore tests.
- broker “exactly once” does not automatically cover arbitrary end-to-end side effects.
- NoSQL is not inherently more available or scalable for every workload; implementation/topology/access patterns matter.
- microservices are not a default scaling mechanism.
- multi-region active-active requires an application conflict and authority model.
- cache/CDN layers require security, invalidation, stale, outage, and cost semantics.
- financial systems require exact arithmetic, explicit ledgers, and reconciliation beyond API flow.

## Maintenance Rule

When the source repository or standards evolve:

1. compare chapter/source changes;
2. identify a real behavior or retrieval gap;
3. add/update a pressure or acceptance scenario first;
4. modify the smallest relevant reference;
5. run package and architecture-validator tests;
6. update `VERSION` and `14-source-map.md`;
7. record incompatible workflow changes in a changelog if introduced.
