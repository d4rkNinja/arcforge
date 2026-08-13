# Requirements, Estimation, and SLOs

Architecture quality depends on converting product language into measurable system behavior.

## 1. Requirement Taxonomy

### Functional requirements

Describe externally visible capabilities and domain rules:

- actors and permissions;
- commands, queries, notifications, exports, and workflows;
- states and transitions;
- integrations and channels;
- offline, reconciliation, or administrative behavior.

Use acceptance examples. Avoid implementation details unless they are fixed constraints.

### Architecturally significant requirements (ASRs)

An ASR materially shapes architecture. Typical categories:

- throughput, concurrency, burst, and fan-out;
- latency distribution and deadline;
- availability, durability, recovery, and data-loss tolerance;
- consistency, ordering, uniqueness, and auditability;
- data volume, retention, residency, privacy, and deletion;
- security, tenancy, abuse/fraud, and compliance;
- geographic reach, offline behavior, and network quality;
- operability, release frequency, staffing, and ownership;
- cost ceiling and unit economics;
- migration deadline, compatibility, and reversibility.

### Constraints

A constraint removes options. Examples:

- must run on-premises or in a named region;
- existing identity provider and database must remain;
- launch date and team size;
- regulated data may not leave a boundary;
- clients cannot update frequently;
- vendor API quota or contractual SLA;
- device, power, or bandwidth limitations.

Challenge preferences disguised as constraints.

### Non-goals

State what the design intentionally does not solve. Non-goals prevent accidental platform-building.

## 2. Quality Attribute Scenarios

Write each important quality attribute as:

```text
Source → Stimulus → Environment → Artifact → Response → Measure
```

Example:

```text
A mobile user → submits an order → during a 5× flash-sale burst
→ order API and inventory workflow → accepts once or returns a retryable response
→ p99 ≤ 400 ms at the edge, zero duplicate orders, ≥ 99.95% successful valid requests.
```

### Minimum measurable attributes

| Attribute | Questions |
|---|---|
| Latency | Which journey, percentile, payload, geography, and load? |
| Throughput | Average, peak, burst duration, and growth? |
| Availability | User-visible successful outcomes over what window? |
| Durability | What can be lost, how much, under which failure? |
| Consistency | Which invariant/read needs what freshness and ordering scope? |
| Recovery | RTO, RPO, dependency assumptions, failback? |
| Security | Which assets/adversaries/trust boundaries and control evidence? |
| Privacy | Which data subjects, purpose, retention, deletion, residency? |
| Operability | On-call, deployment frequency, detection/recovery targets? |
| Cost | Monthly ceiling, unit cost, growth scenario, egress/observability? |

## 3. Workload Model

Characterize distributions, not only averages:

- daily/monthly active users;
- requests or events per active user;
- read/write ratio;
- interactive vs batch/background traffic;
- peak-to-average ratio and burst duration;
- payload and object-size percentiles;
- concurrent sessions, WebSockets, streams, or jobs;
- fan-out per event and skew/celebrity users;
- key/tenant distribution and largest tenant;
- geographic distribution and network quality;
- retries, bots, crawlers, and malicious traffic;
- seasonal events and expected growth.

## 4. Core Estimation Formulas

Use SI units or binary units consistently and label them.

### Traffic

```text
average RPS = requests per day / 86,400
peak RPS = average RPS × peak factor
write RPS = peak RPS × write fraction
read RPS = peak RPS × read fraction
```

For bursty traffic, calculate burst arrival rate and duration separately.

### Concurrency

Little’s Law approximation:

```text
concurrency ≈ arrival rate × average time in system
```

Example: 2,000 requests/s × 0.25 s ≈ 500 in-flight requests. Use tail behavior and queueing margins for provisioning.

### Storage

```text
daily logical bytes = writes/day × average record/object size
retained logical bytes = daily logical bytes × retention days
physical bytes ≈ logical × replication/erasure overhead
                 + indexes + metadata + versions/tombstones + safety margin
```

Model backups, snapshots, logs, temporary/transcoding data, and compaction amplification separately.

### Bandwidth

```text
ingress bytes/s = request/event rate × average ingress payload
edge egress bytes/s = response/download rate × average egress payload
internal bytes/s = external traffic × fan-out/replication/read-amplification factors
```

### Cache

```text
working-set bytes = hot objects × average cached object size
origin read rate = total read rate × (1 - hit rate)
```

Do not assume hit rate; model it from popularity distribution and TTL/invalidation behavior.

### Queue and recovery

```text
backlog growth rate = arrival rate - processing rate
backlog size after incident = growth rate × incident duration
drain time = backlog / (recovery processing rate - normal arrival rate)
```

A recovery processing rate not greater than normal arrival rate means the system never catches up.

### Availability composition

For strictly serial independent dependencies:

```text
end-to-end availability ≈ A1 × A2 × ... × An
```

This is a first-order estimate, not proof. Shared failures, retries, degraded modes, and partial functionality change the result.

### Cost

```text
monthly cost = fixed platform cost
             + compute unit price × usage
             + storage price × retained bytes
             + request/operation charges
             + egress and cross-region transfer
             + managed-service/license costs
             + observability and backup
             + operational staffing/on-call burden
```

Report unit economics, such as cost per active tenant, transaction, GB stored, minute streamed, or 1,000 model requests.

## 5. Capacity Table

Use a table like this:

| Dimension | Baseline | Peak | 12-month | 10× stress | Assumption/evidence |
|---|---:|---:|---:|---:|---|
| Requests/s | | | | | |
| Writes/s | | | | | |
| Concurrent connections | | | | | |
| Data/day | | | | | |
| Retained data | | | | | |
| Egress/month | | | | | |
| Queue events/s | | | | | |
| Largest tenant share | | | | | |
| Monthly cost | | | | | |

## 6. Sensitivity Analysis

Identify assumptions that change topology or technology:

- peak factor;
- object-size tail;
- cache hit rate;
- write amplification;
- fan-out size;
- largest tenant share;
- retention period;
- cross-region replication and egress;
- model token/output distribution;
- third-party call frequency and pricing.

For each, show a low/base/high range and the architectural breakpoint.

Example:

| Assumption | Low | Base | High | Breakpoint/action |
|---|---:|---:|---:|---|
| Peak RPS | 2k | 8k | 40k | shard write path above 20k measured writes/s |
| Largest tenant | 2% | 10% | 45% | dedicated partition/pool above 20% |
| Cache hit rate | 90% | 75% | 40% | origin DB exceeds safe reads below 60% |

## 7. SLI/SLO/SLA Design

### Definitions

- **SLI:** measured behavior, such as successful valid requests or latency below a threshold.
- **SLO:** target for an SLI over a window.
- **SLA:** external or contractual commitment with consequences; do not casually equate it with an internal SLO.
- **Error budget:** allowed unreliability, typically `1 - SLO` for ratio-based objectives.

### Start from user journeys

Good SLIs measure what users receive, not only component health.

Examples:

- proportion of valid checkout attempts that create exactly one durable order;
- proportion of search requests returning a fresh-enough result within 300 ms;
- proportion of notifications accepted by the configured provider within 60 seconds;
- proportion of files uploaded and retrievable without corruption;
- proportion of model responses meeting task-quality and safety thresholds within cost/latency budgets.

### Availability SLI

```text
good events / valid events
```

Define exclusions narrowly. Do not exclude errors merely because they are inconvenient.

### Latency SLI

Use percentiles or threshold ratios, not averages alone:

```text
requests completed within threshold / eligible requests
```

Use separate objectives for materially different workloads or payloads.

### Freshness SLI

```text
reads whose data age ≤ threshold / eligible reads
```

### Correctness SLI

Use invariant violations, reconciliation mismatches, duplicate effects, or sampled truth comparison.

### Durability SLI

Measure verified recoverability and permanent loss, not only storage-node health.

### SLO window

Choose a window aligned to business and release decisions. Common rolling windows are 7, 28, or 30 days; high-risk domains may also need per-event or incident caps.

### Error-budget policy

Define actions before budget is exhausted:

- burn-rate alerts;
- release slowdown/freeze thresholds;
- mandatory reliability work;
- incident/postmortem threshold;
- exception authority;
- treatment of dependency-caused failures;
- recovery criteria.

Use `assets/slo-template.md`.

## 8. RTO and RPO

- **RTO:** maximum acceptable time to restore the business capability.
- **RPO:** maximum acceptable data loss measured in time or committed operations.

Define per journey/data class, not one number for the entire company.

| Capability/data | RTO | RPO | Degraded mode | Verification |
|---|---:|---:|---|---|
| payments ledger | | | | restore/reconciliation drill |
| search index | | | | rebuild from source facts |
| user uploads | | | | checksum and restore sample |
| analytics | | | | replay raw events |

## 9. Estimation Quality Rules

- Show formulas and units.
- Round inputs but preserve order-of-magnitude correctness.
- Use ranges when uncertainty is material.
- Include replication, indexes, backups, logs, tombstones, versions, and temporary data.
- Include internal traffic and retry amplification.
- Model peak and burst, not only daily average.
- Compare demand with a measured or documented component limit.
- State safety margin and why it exists.
- Distinguish capacity ceiling from operationally safe capacity.
- Recalculate after architecture changes.

## 10. Common Mistakes

| Mistake | Correction |
|---|---|
| Availability target copied from convention | derive from user impact, alternatives, and cost |
| Average latency used | define p50/p95/p99 or threshold ratio by workload |
| QPS calculated but fan-out ignored | include internal amplification and dependency calls |
| Logical storage treated as physical | add indexes, replication, backups, versions, compaction |
| 10× growth stated without time horizon | state horizon and trigger for each scaling step |
| “Real-time” left vague | define event-to-visible freshness percentile |
| SLO on CPU or pod health | define user-journey SLI; use internals as diagnostics |
| RPO/RTO written but never tested | schedule restore/failover drills and capture evidence |
