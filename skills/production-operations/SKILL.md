---
name: production-operations
description: "Use when implementing or changing operational code and practices: structured logging, metrics and cardinality control, distributed tracing and correlation IDs, health checks and readiness probes, audit logging, observability for async systems, operational runbooks, incident readiness and escalation, data import and export, backup, restore, disaster recovery, RTO/RPO targets, high availability, multi-region systems, and data residency. Loads production implementation papers with MUST/SHOULD/AVOID/NEVER rules, failure modes, and verification checklists to read before writing code. For deployment sequencing and zero-downtime changes use migration-evolution; for telemetry-driven architecture reviews use architecture-review-gate; for whole-system availability architecture use system-architecture-harness."
---

# Observability & Operations Implementation

## Overview

Implementation intelligence for running systems. Each reference paper captures what separates operable systems from hopeful ones: logs without correlation IDs, metrics with unbounded cardinality, health checks that pass while the system is down, audit trails that can be edited, and backups that have never been restored.

**Core principle:** An operational claim is only as real as its evidence. If a journey cannot be observed, an alert has no owner, or a restore has never been rehearsed, the system does not actually have that capability.

## Implementation Law

```text
NO OPERATIONAL IMPLEMENTATION WITHOUT:
1. the primary paper(s) for the practice read in full first;
2. the user journey or failure the signal protects named first;
3. "Existing-codebase checks" run when changing existing telemetry;
4. every applicable MUST mapped to an enforcement point (emitter, alert,
   runbook, drill) and evidence — never silently downgraded.
```

## When to Use

Use this skill when implementing or changing:

- structured logging, log levels, redaction, and retention;
- metrics, SLI selection, and cardinality limits;
- distributed tracing, context propagation, and sampling;
- health checks: liveness vs readiness, dependency depth, synthetic probes;
- audit logging: actor, action, target, immutable retention;
- async-system observability: lag, depth, backlog, poison queues;
- runbooks, escalation paths, and on-call ownership;
- incident readiness: detection, severity, communication, postmortems;
- data import pipelines with validation and quarantine;
- data export with authorization and rate control;
- backup: scope, isolation, retention, encryption;
- restore: rehearsal, RPO/RTO evidence, cross-region recovery;
- high availability topology and failover authority;
- multi-region systems, residency, and conflict policy.

## When Not to Use

- Deployment ordering and zero-downtime rollout mechanics: use `migration-evolution` (134, 106 pairs here).
- Architecture-level SLO/SLA design and review: use `system-architecture-harness` / `architecture-review-gate`.
- Security log redaction policy ownership: `security-privacy` (066) defines what is sensitive; this skill implements the emitters.
- Cost modeling: use `system-architecture-harness` Phase 10.

## Required Context Loading

| Situation | Papers |
|---|---|
| Structured logs, levels, redaction, retention | [056 Logging](references/papers/056-logging.md) |
| Metrics, SLIs, cardinality, aggregation | [057 Metrics](references/papers/057-metrics.md) |
| Trace propagation, sampling, cross-service context | [058 Distributed Tracing](references/papers/058-distributed-tracing.md) |
| Liveness vs readiness, dependency checks, probes | [059 Health Checks](references/papers/059-health-checks.md) |
| Audit events, immutability, tamper evidence | [060 Audit Logging](references/papers/060-audit-logging.md) |
| Queue lag, backlog, poison visibility | [137 Observability for Async Systems](references/papers/137-observability-for-async-systems.md) |
| Runbook structure, diagnosis, escalation steps | [138 Operational Runbooks](references/papers/138-operational-runbooks.md) |
| Incident detection, severity, comms, review | [139 Incident Readiness](references/papers/139-incident-readiness.md) |
| Import validation, quarantine, partial failure | [074 Data Import](references/papers/074-data-import.md) |
| Export authorization, scope, rate control | [075 Data Export](references/papers/075-data-export.md) |
| Backup scope, isolation, retention | [076 Backup](references/papers/076-backup.md) |
| Restore rehearsal and recovery evidence | [077 Restore](references/papers/077-restore.md) |
| DR plans, RTO/RPO, failover authority | [078 Disaster Recovery](references/papers/078-disaster-recovery.md) |
| HA topology, quorum, failover behavior | [097 High Availability](references/papers/097-high-availability.md) |
| Multi-region routing, replication, conflicts | [132 Multi-Region Systems](references/papers/132-multi-region-systems.md) |
| Residency constraints and boundaries | [133 Data Residency](references/papers/133-data-residency.md) |

## Workflow

1. Name the user journey or failure mode the operational work protects; select primary papers (a new async feature touches 056 + 057 + 137; a DR plan touches 076 + 077 + 078).
2. Read the primary papers fully, including failure modes and checklists.
3. Answer the paper's pre-implementation questions; label autonomous assumptions and their impact.
4. For existing systems, run the existing-codebase checks: inspect current emitters, cardinality, dashboards, and whether alerts have owners and runbooks.
5. Convert each MUST/SHOULD/AVOID/NEVER into concrete artifacts: emitter schemas, alerts tied to user impact, runbook steps, and scheduled drills — each with evidence.
6. Implement the smallest safe slice; carry the paper's verification checklist (alert fires, restore completes within target, runbook executes) into acceptance.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Boundary Map

| If the task also involves | Also use |
|---|---|
| Rollout ordering and rollback windows | `migration-evolution` (106 paths, 134) |
| Queue/job failure semantics being observed | `async-messaging` (043, 045) |
| What must be redacted before emission | `security-privacy` (066) |
| Retention/lifecycle of the data itself | `data-storage` (033) |
| Load/chaos drills proving the claims | `quality-release` (093, 094) |
| SLO targets and error budgets | `system-architecture-harness` |

## Output Contract

1. **Papers consulted** — numbers and the sections relied on.
2. **Journey-to-signal map** — each protected journey → SLI, alert, owner, and runbook.
3. **Assumptions and unanswered questions** — labeled, with their design impact.
4. **Rule-to-decision map** — each applicable MUST → emitter/alert/runbook/drill decision and enforcement point.
5. **Failure modes addressed** — undetected lag, silent backup rot, unowned alerts, unaudited privileged actions.
6. **Verification evidence** — fired alerts, executed runbook steps, restore/recovery drill results with observed RPO/RTO.

## Stop Conditions

Stop and revise when any of these appears:

- code is written before the protected journey or failure is named;
- logs without structure, correlation IDs, or redaction; secrets or PII in telemetry;
- metrics with unbounded or user-controlled cardinality;
- a single "health" endpoint standing in for readiness of dependencies;
- audit logs that can be modified or lack actor/target/result;
- alerts with no owner, threshold rationale, or runbook;
- a backup with no tested restore, or replication presented as backup;
- RTO/RPO claimed without a rehearsed drill and observed numbers;
- failover with no defined authority or fencing;
- multi-region without residency analysis and conflict policy;
- async queues with no lag or backlog visibility;
- imports/exports without validation, quarantine, or authorization;
- any operations MUST downgraded to a TODO without a documented exception.

## References

Sixteen production papers under `references/papers/`: 056 Logging, 057 Metrics, 058 Distributed Tracing, 059 Health Checks, 060 Audit Logging, 074 Data Import, 075 Data Export, 076 Backup, 077 Restore, 078 Disaster Recovery, 097 High Availability, 132 Multi-Region Systems, 133 Data Residency, 137 Observability for Async Systems, 138 Operational Runbooks, 139 Incident Readiness. Cross-domain pointers inside the papers name the sibling skill to activate.

Worked example: [observability and recovery evidence for a checkout service](examples/worked-example-checkout-observability.md).
