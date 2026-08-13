# Reliability, Resilience, and Disaster Recovery

Reliability is the system’s ability to deliver correct user outcomes under expected conditions and failures. Resilience is controlled degradation and recovery. Disaster recovery is the proven restoration of critical capability and data after large failures.

## Contents

- 1. Reliability Begins with User Journeys
- 2. Failure Taxonomy
- 3. Failure Matrix
- 4. Timeouts and Deadlines
- 5. Retries
- 6. Circuit Breakers
- 7. Bulkheads and Resource Isolation
- 8. Load Shedding and Graceful Degradation
- 9. Health, Readiness, and Liveness
- 10. Redundancy and Failure Domains
- 11. Leader Election, Leases, and Fencing
- 12. Multi-Region Topologies
- 13. RTO/RPO and Recovery Tiers
- 14. Backup Architecture
- 15. Data Corruption and Reconciliation
- 16. Deployment Reliability
- 17. Chaos and Game Days
- 18. Incident Readiness
- 19. Reliability Review Questions
- 20. Common Mistakes

## 1. Reliability Begins with User Journeys

For each critical journey define:

- valid request/event population;
- successful outcome and deadline;
- correctness/freshness condition;
- dependency set;
- degraded but acceptable outcome;
- data-loss tolerance;
- SLI/SLO and error-budget policy;
- owner and escalation.

Component uptime is diagnostic. It is not a substitute for journey success.

## 2. Failure Taxonomy

Cover at least:

### Compute and process

- crash, OOM, deadlock, GC pause, event-loop stall;
- CPU throttling, disk full, file descriptor exhaustion;
- thread/connection pool exhaustion;
- startup/warmup failure;
- stale process/config/version.

### Network

- timeout, packet loss, high latency, partition;
- DNS failure/staleness;
- load balancer/proxy failure;
- asymmetric reachability;
- TLS/certificate expiration;
- cross-zone/region link failure.

### Data

- leader/replica failure;
- replication lag or split brain;
- lock/contention/deadlock;
- corruption, accidental deletion, bad migration;
- backup failure or un-restorable backup;
- index/projection drift;
- clock skew/order anomalies.

### Messaging

- broker/partition failure;
- duplicate, loss, reorder, poison message;
- consumer lag or rebalance storm;
- DLQ growth/replay failure;
- offset/checkpoint corruption.

### Dependencies and vendors

- outage, slow responses, quota exhaustion;
- behavioral/schema change;
- invalid callback/webhook;
- regional unavailability;
- account suspension or credential failure.

### Change and people

- bad deploy/config/feature flag;
- secret/key rotation failure;
- operator error, compromised account;
- capacity change or noisy neighbor;
- destructive automation.

### AI/model

- provider outage/rate limit;
- quality drift/regression;
- unsafe output or prompt injection;
- tool misuse/looping;
- retrieval/index staleness;
- model/version incompatibility.

## 3. Failure Matrix

Use `assets/failure-mode-template.md`. Each row must include:

```text
Failure → Detection → Containment → User effect → Data effect
        → Automated response → Manual response → RTO/RPO
        → Validation drill → Owner
```

Prioritize failures by impact, probability, detectability, and recovery difficulty. Include correlated failures; independence assumptions are frequently false.

## 4. Timeouts and Deadlines

- every remote call needs a timeout/deadline;
- derive per-hop budget from end-to-end objective;
- connect, TLS, request, idle, and stream timeouts may differ;
- cancel downstream work after caller deadline where possible;
- avoid timeout values shorter than normal tail behavior;
- alert on timeout rate and latency before timeout;
- preserve enough time for fallback/response serialization.

A timeout converts a slow failure into a bounded failure; it does not repair the operation’s ambiguous state.

## 5. Retries

Retries are safe only when:

- the error is plausibly transient;
- operation is idempotent or conditionally protected;
- total deadline remains;
- attempts are bounded;
- exponential backoff and jitter prevent synchronization;
- retry budget prevents amplification;
- lower layers are not also retrying uncontrollably;
- ambiguous outcomes are resolved by status/idempotency lookup;
- attempts are observable.

Do not retry validation, authorization, invariant, or permanent business failures unchanged.

## 6. Circuit Breakers

Use a circuit breaker when repeated calls to an unhealthy dependency consume scarce resources or amplify harm.

Define:

- failure/slow-call classification;
- rolling window and threshold;
- open duration and probe policy;
- fallback/degraded response;
- per-endpoint/tenant isolation;
- metrics and manual override;
- interaction with retries and autoscaling.

Avoid a single global breaker that blocks healthy partitions/tenants unnecessarily.

## 7. Bulkheads and Resource Isolation

Isolate:

- critical vs optional traffic;
- interactive vs batch/background;
- tenants/whales;
- external dependencies;
- regions/zones/cells;
- thread/connection pools;
- queues and rate limits;
- model/tool workloads.

A shared pool lets one slow dependency or tenant starve unrelated work.

## 8. Load Shedding and Graceful Degradation

Define priority and rejection before saturation.

Possible strategies:

- reject low-priority requests early;
- serve stale/cache/snapshot data;
- disable expensive enrichment/recommendations;
- reduce response depth/quality;
- queue deferrable work;
- switch to deterministic/local fallback;
- read-only mode;
- preserve critical transactions while disabling reports/search.

Never accept a critical write when the system cannot enforce its invariant merely to improve availability metrics.

## 9. Health, Readiness, and Liveness

- **liveness:** process can make progress; restart only when restart helps.
- **readiness:** instance can safely receive this class of traffic.
- **startup:** initialization/warmup completed.
- **dependency health:** diagnostic; do not automatically make every instance unready for every downstream fluctuation.

Avoid cascading restarts and fleet-wide readiness failure. Separate critical from optional dependencies.

## 10. Redundancy and Failure Domains

Place replicas across real failure domains:

- process/host;
- rack/power/network;
- availability zone/data center;
- region/provider when required.

Define:

- replication acknowledgement;
- quorum and failover authority;
- spare capacity during failure;
- shared dependencies/control planes;
- maintenance behavior;
- data consistency after failover;
- failback and reconciliation.

Redundancy without diversity can preserve the same bug/configuration/corruption everywhere.

## 11. Leader Election, Leases, and Fencing

Leader/lease designs must handle stale owners.

- use a consensus-backed authority where correctness requires one active owner;
- assign monotonically increasing fencing tokens/epochs;
- downstream state changes reject stale token values;
- define lease duration, renewal, clock assumptions, and pause behavior;
- ensure failover does not create two valid writers;
- observe leadership churn and blocked progress.

A distributed lock without fencing can allow a paused former owner to write after its lease expires.

## 12. Multi-Region Topologies

### Active-passive

- simpler write ownership and conflict model;
- define replication lag/RPO, warm capacity, routing, promotion, and failback;
- regularly exercise promotion.

### Active-active with regional ownership

- route each entity/tenant to a home region;
- replicate for reads/recovery;
- define movement and outage override;
- prevent concurrent owners with fencing.

### Multi-writer active-active

Require:

- explicit conflict semantics per data type;
- commutative/mergeable operations or deterministic conflict resolution;
- global uniqueness/ordering strategy where needed;
- user-visible conflict behavior;
- residency and latency model;
- reconciliation and failback;
- tests under partitions and clock skew.

Do not use last-write-wins for money, inventory, identity, or other invariants without proving it is semantically valid.

## 13. RTO/RPO and Recovery Tiers

Classify capabilities/data:

| Tier | Example intent | Typical architecture evidence |
|---|---|---|
| 0 | life/safety or immediate financial integrity | domain-specific controls, synchronous durable replicas, strict authority, continuous validation |
| 1 | core revenue/identity | hot/warm failover, low RPO, rehearsed runbooks, reconciliation |
| 2 | important but degradable | restore from backup/replay within hours |
| 3 | rebuildable/noncritical | longer restore, derived-data rebuild |

Actual values must come from business impact, not the table.

## 14. Backup Architecture

Define:

- full/incremental/log/PITR method;
- frequency and retention;
- isolation from production credentials and deletion;
- encryption and key recovery;
- immutability/legal hold where required;
- region/account/provider placement;
- backup monitoring and inventory;
- corruption/ransomware scenario;
- restore ordering and dependencies;
- deletion/privacy behavior in backups;
- restore-test schedule and evidence.

### Restore proof

A restore test must verify:

- backup can be located and decrypted;
- infrastructure and dependencies can be recreated;
- data restores within RTO and meets RPO;
- checksums/invariants/reconciliation pass;
- application version/schema is compatible;
- access controls and audit are correct;
- traffic can be resumed safely.

## 15. Data Corruption and Reconciliation

Plan for silent semantic corruption, not only node loss.

- checksums and scrubbing for bytes/objects;
- invariant checks for domain state;
- double-entry/zero-sum checks for ledgers;
- source-vs-projection counts/hashes;
- sequence gap/duplicate checks;
- provider/internal settlement comparison;
- quarantine rather than destructive “repair”;
- point-in-time recovery and replay;
- operator tooling with audit.

## 16. Deployment Reliability

- small, reversible changes;
- canary/progressive rollout by zone/cell/tenant;
- health based on SLO/error/latency/correctness signals;
- version skew and contract compatibility;
- automatic halt/rollback for safe failures;
- roll-forward for irreversible data changes;
- feature flags with owner/expiry;
- configuration validation and staged rollout;
- connection draining and job handoff;
- dependency-order avoidance through backward compatibility.

## 17. Chaos and Game Days

Test hypotheses, not randomness.

Examples:

- terminate process/host/zone;
- add dependency latency and errors;
- exhaust pool/quota/disk;
- pause consumers and build backlog;
- corrupt/revoke credential;
- simulate DNS/certificate failure;
- fail over datastore/region;
- restore from isolated backup;
- replay duplicate/out-of-order messages;
- serve stale model/index/config.

For each experiment define blast radius, abort criteria, expected signals, expected user behavior, owner, and learning.

## 18. Incident Readiness

Require:

- severity model and incident commander role;
- paging and escalation;
- dependency/vendor contact path;
- status/customer communication;
- runbooks and access break-glass process;
- immutable timeline/evidence;
- post-incident learning without blame;
- action owners and verification;
- recurring-incident and error-budget review.

## 19. Reliability Review Questions

- What is the user-visible SLI?
- What single/correlated failure consumes the most error budget?
- What happens when every dependency is slow, not down?
- Which retries can amplify load?
- Which queues/pools are unbounded?
- Can a stale leader still write?
- Can the system operate when cache/search/analytics/control plane is unavailable?
- How are ambiguous write outcomes resolved?
- How is corruption detected and repaired?
- When was the last successful restore/failover?
- Is there enough capacity during maintenance plus failure?
- Who owns recovery at 03:00?

## 20. Common Mistakes

| Mistake | Correction |
|---|---|
| replication called backup | isolate immutable backups and prove restore |
| retries added without budget | bounded jittered retries under end-to-end deadline |
| all dependencies in readiness | distinguish criticality and prevent fleet-wide ejection |
| failover documented but untested | schedule game day and capture RTO/RPO evidence |
| active-active with last-write-wins | define semantic conflict model and fencing |
| availability favored over invariant | reject/degrade safely when correctness cannot be enforced |
| circuit breaker used as universal cure | combine with timeout, isolation, fallback, and capacity controls |
| only infrastructure failures tested | include bad deploy, corruption, credential, operator, vendor, and model failures |
