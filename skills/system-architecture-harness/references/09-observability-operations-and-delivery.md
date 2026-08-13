# Observability, Operations, Delivery, and Evolution

A production architecture includes how people and automation detect, understand, change, recover, and retire it.

## Contents

- 1. Operability Contract
- 2. Observability Signals
- 3. Instrument User Journeys First
- 4. Golden Signals and Workload-Specific Signals
- 5. Cardinality and Data Budgets
- 6. Logging Rules
- 7. Distributed Tracing
- 8. Alerting
- 9. Dashboards
- 10. Runbooks
- 11. Infrastructure and Configuration
- 12. CI/CD Quality Gates
- 13. Progressive Delivery
- 14. Database and Event Migrations
- 15. Migration Patterns
- 16. Test Portfolio
- 17. Architecture Fitness Functions in CI/Operations
- 18. Ownership and Service Catalog
- 19. Documentation Set
- 20. Common Mistakes

## 1. Operability Contract

Every production component needs:

- accountable owning team;
- service catalog entry and dependency map;
- SLI/SLO and error-budget policy where user-critical;
- dashboards, alerts, logs, metrics, traces, and audit;
- runbooks and escalation;
- deploy/rollback/roll-forward procedure;
- capacity and cost ownership;
- backup/restore and DR responsibilities;
- security/privacy contacts;
- lifecycle and deprecation plan.

## 2. Observability Signals

Use correlated signals:

- **traces:** end-to-end request/event paths and timing;
- **metrics:** rates, ratios, distributions, gauges, saturation, business correctness;
- **logs:** structured events and diagnostic context;
- **baggage/context:** carefully propagated correlation metadata;
- **profiles:** code/resource hotspots when supported;
- **audit events:** security and high-value state changes.

OpenTelemetry or another vendor-neutral instrumentation approach can reduce backend lock-in, but semantic conventions and data quality still need governance.

## 3. Instrument User Journeys First

For each critical journey record:

- request/event count;
- success/failure by stable reason;
- latency distribution;
- correctness/freshness indicator;
- dependency contribution;
- retry/duplicate behavior;
- tenant/region/client dimensions with cardinality controls;
- cost/work units where relevant.

Then instrument component internals for diagnosis.

## 4. Golden Signals and Workload-Specific Signals

### Common signals

- traffic/rate;
- errors;
- duration/latency;
- saturation.

### Queues/streams

- produce/consume rate;
- queue depth and oldest age/consumer lag;
- retry/DLQ rate;
- partition skew and rebalance;
- processing duration and checkpoint age.

### Databases

- query latency/error;
- connections and waits;
- lock/deadlock/contention;
- replication lag;
- cache hit ratio;
- storage/IO/compaction;
- backup/restore status.

### Caches

- hit/miss/eviction;
- memory and fragmentation;
- hot keys;
- load latency/error;
- stampede/coalescing;
- stale serves.

### Real-time connections

- active connections;
- connect/auth failure;
- reconnect rate;
- outbound buffer/slow consumers;
- heartbeat freshness;
- fan-out latency.

### AI/model

- task success/quality/safety;
- model/provider/version;
- input/output tokens and cost;
- latency by stage;
- cache/retrieval hit and recall proxies;
- fallback/refusal/tool-call/error rate;
- policy/human-approval outcomes;
- drift and evaluation regressions.

## 5. Cardinality and Data Budgets

Unbounded labels/attributes can make telemetry unaffordable or unusable.

Do not use raw:

- user/tenant/request/order IDs as metric labels;
- URLs with IDs instead of route templates;
- exception messages as label values;
- prompt/content text as attributes;
- high-cardinality stack details in metrics.

Use traces/logs for individual IDs with access controls and sampling. Set ingestion, retention, query, and cardinality budgets.

## 6. Logging Rules

Use structured logs with:

- timestamp;
- severity;
- service/version/environment/region;
- trace/span/correlation ID;
- stable event/error code;
- actor/tenant reference only when authorized and needed;
- operation and result;
- retry/attempt/workflow state.

Never log secrets, raw credentials, payment data, unnecessary personal data, complete request bodies, or unreviewed model context.

Define sampling, redaction, retention, access, legal hold, and deletion behavior.

## 7. Distributed Tracing

Instrument boundaries:

- inbound/outbound HTTP/RPC;
- database/cache calls;
- queue produce/consume;
- external vendors;
- workflow steps;
- model/retrieval/tool calls.

Propagate context across asynchronous messages using stable standards. Use span links when asynchronous work is causally related but not a direct child.

Capture status, latency, retries, message/event ID, partition, and safe semantic attributes. Use head/tail/adaptive sampling with guaranteed retention for errors/high-value operations where needed.

## 8. Alerting

Alerts must be actionable.

### Page

A human must act now because users, correctness, security, or recovery are materially at risk.

### Ticket

Action is required within a bounded period but not immediately.

### Log/dashboard

Diagnostic or trend information; no direct action.

Prefer:

- SLO burn-rate alerts;
- correctness/invariant/reconciliation alerts;
- queue age rather than depth alone;
- saturation before hard failure;
- dependency and regional symptoms correlated to user impact;
- security anomaly and privileged-action alerts.

Each alert needs owner, severity, runbook, expected action, and test. Remove alerts that are routinely ignored.

## 9. Dashboards

Provide layers:

1. executive/user-journey SLO and business outcome;
2. service golden signals and dependencies;
3. resource/component internals;
4. deployment/version/config changes;
5. security/cost/capacity views.

Annotate deploys, incidents, migrations, feature flags, and major traffic events.

## 10. Runbooks

A runbook includes:

- trigger/symptoms and impact;
- safety warnings and required access;
- diagnostic steps and queries;
- immediate containment/degraded mode;
- recovery steps and validation;
- rollback/roll-forward;
- escalation/vendor contacts;
- customer/status communication;
- post-recovery reconciliation;
- owner, last tested date, and known limits.

Automate repeatable safe actions; retain human judgment for ambiguous/high-risk actions.

## 11. Infrastructure and Configuration

- infrastructure as code with review and state protection;
- reproducible environments and immutable artifacts;
- environment-specific configuration separated from code;
- schema/semantic validation for config;
- staged rollout and versioning;
- secrets from managed delivery, not files/images;
- drift detection;
- least-privilege deployment identities;
- policy-as-code where valuable;
- break-glass and recovery process.

Configuration changes can be as dangerous as code; give them the same audit and rollout discipline.

## 12. CI/CD Quality Gates

Depending on risk:

- formatting/lint/static analysis;
- unit/property tests;
- integration and contract tests;
- migration compatibility tests;
- dependency/SBOM/license/secret/vulnerability scans;
- infrastructure/policy tests;
- performance regression checks;
- model/evaluation/safety regression tests;
- artifact signing/provenance;
- deployment manifest validation;
- preview/staging smoke tests.

Do not rely on a staging environment alone; it rarely matches production load, data age, and failure conditions.

## 13. Progressive Delivery

Options:

- rolling;
- canary by percentage/tenant/cell/region;
- blue-green;
- shadow/mirror;
- feature flag;
- dark launch.

Define:

- audience and blast radius;
- compatibility across versions;
- success/abort metrics and evaluation window;
- automatic vs manual decision;
- data/schema behavior;
- rollback vs roll-forward;
- queue/job/connection draining;
- flag owner and removal date.

Canary metrics must include correctness and business outcomes, not only CPU/error rate.

## 14. Database and Event Migrations

### Expand/contract

1. add compatible schema;
2. deploy tolerant readers;
3. write both forms inside one authority when required;
4. backfill with checkpoints/throttling;
5. validate counts/hashes/invariants;
6. switch reads;
7. stop old writes;
8. remove after compatibility window.

### Event evolution

- compatible optional additions;
- new event type/version for semantic change;
- consumers tolerate version skew;
- replay old versions through transformations;
- contract compatibility in CI;
- retention long enough for recovery needs.

Avoid application-level dual writes to independent databases without an outbox/CDC or reconciliation mechanism.

## 15. Migration Patterns

### Strangler

Route capabilities gradually to the new system. Define ownership and data source during each phase.

### Shadow

Send mirrored traffic without serving its result. Protect side effects and sensitive data; compare safely.

### Dual read

Read old/new and compare; define which result serves and how mismatches are classified.

### CDC/backfill

Take a snapshot, stream changes, validate, catch up, then cut over. Handle deletes, schema changes, and replay.

### Big bang

Use only when coexistence is impossible and downtime/risk are explicitly accepted with rehearsed rollback/restore.

## 16. Test Portfolio

- unit and property tests for domain invariants;
- integration tests with real critical dependencies where practical;
- consumer/provider contract tests;
- end-to-end critical journeys;
- authorization/tenant/security tests;
- migration/backfill/replay tests;
- load, stress, spike, soak, and capacity tests;
- fault/chaos tests;
- backup restore and region failover drills;
- observability/alert/runbook tests;
- model evaluation/red-team tests;
- cost and quota tests.

Test failure semantics and operator workflows, not just happy paths.

## 17. Architecture Fitness Functions in CI/Operations

Examples:

- module dependency rule forbids cycles/internal imports;
- schema compatibility validator blocks breaking events;
- p99 load test threshold;
- tenant isolation policy tests;
- maximum synchronous hop count or latency budget;
- no public storage/broad IAM policy;
- restore drill age must remain within policy;
- cost per transaction alert;
- SLO burn rate gates progressive rollout;
- AI evaluation score/cost/safety threshold blocks model change.

## 18. Ownership and Service Catalog

Record:

- capability and criticality;
- owner/on-call/escalation;
- repository/deploy pipeline;
- endpoints/events/stores;
- dependencies and consumers;
- SLO and dashboard;
- runbooks/DR tier;
- data classification/compliance;
- cost center;
- lifecycle/version/deprecation.

Orphaned components are architectural risk.

## 19. Documentation Set

Keep documentation close to change and evidence:

- decision summary and architecture spec;
- C4 context/container/deployment views;
- dynamic/sequence diagrams for complex flows;
- data model and state machine;
- API/event contracts;
- ADR decision log;
- threat model and data-flow map;
- SLOs/error-budget policy;
- runbooks and DR plan;
- migration plan and risk register;
- cost/capacity model.

Generate low-level code diagrams when possible; manually maintain only views that support decisions.

## 20. Common Mistakes

| Mistake | Correction |
|---|---|
| logs called observability | correlate traces, metrics, structured logs, audits, and journey SLIs |
| alert on every exception | alert on actionable user/correctness/security risk; diagnose exceptions via telemetry |
| metric labels include IDs | enforce cardinality budgets and use traces/logs for individual context |
| rollback assumed for data change | design compatible migration and roll-forward/reconciliation |
| canary checks only infrastructure | include SLO, correctness, security, and business outcome |
| runbook never exercised | test during game days/incidents and track last verified date |
| feature flags become permanent | assign owner, expiry, cleanup and state-combination tests |
| staging treated as proof | add representative load, production telemetry, progressive release, and drills |
