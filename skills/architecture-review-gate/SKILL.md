---
name: architecture-review-gate
description: "Use when independently reviewing an existing architecture specification, RFC, ADR, diagram, migration plan, AI/agent design, or production-readiness proposal. Trigger for adversarial evidence checks, critical blockers, security, reliability, operability, and release approval conditions. For designing a new system use system-architecture-harness or ai-agent-system-architecture."
---

# Architecture Review Gate

## Overview

Perform an independent, adversarial architecture review. Reconstruct the system from evidence, challenge the riskiest decisions, distinguish missing evidence from actual defects, and block approval when a critical invariant, security boundary, recovery path, or operational control is absent.

**Core principle:** A high score cannot waive a critical failure.

```text
NO APPROVAL WITHOUT FRESH EVIDENCE THAT:
- requirements and assumptions are explicit;
- critical invariants have enforcement points;
- resources and retries are bounded;
- failure and recovery are designed and rehearsable;
- security and tenant boundaries are enforced end to end;
- delivery, rollback, ownership, and validation are real.
```

## When to Use

Use this skill for:

- architecture RFC and ADR review;
- production-readiness and launch gates;
- design due diligence;
- monolith, microservice, event-driven, or multi-region proposals;
- data, API, queue, cache, migration, and disaster-recovery review;
- AI/agent architecture review;
- post-incident structural review;
- comparison of current and target architecture.

Review mode is independent. Do not rewrite the architecture or implement fixes unless the user explicitly changes the task.

## Reviewer Independence

1. Read the requirement and evidence before the author’s conclusion when possible.
2. Reconstruct critical flows and invariants independently.
3. Treat diagrams, claims, benchmarks, and agent reports as untrusted until corroborated.
4. Separate:
   - **defect** — design violates a requirement or safety/correctness rule;
   - **evidence gap** — claim may be valid but is not demonstrated;
   - **risk** — uncertain future harm requiring owner and mitigation;
   - **preference** — stylistic alternative with no material outcome difference.
5. Do not reward complexity, technology prestige, or document length.

## Required Context Loading

- Use [100-point scorecard](references/01-review-scorecard.md) for every formal gate.
- Use [critical failure patterns](references/02-critical-failure-patterns.md) for blocker review.
- Use [evidence and challenge guide](references/03-evidence-challenge-guide.md) for claim verification.
- For historical source details, consult [production scorecard source](references/production-scorecard-source.md).

## Review Workflow

### Phase 0 — Establish Review Contract

Record:

- review mode and decision being gated;
- business owner and technical owner;
- required launch date or decision horizon;
- evidence supplied and evidence unavailable;
- critical journeys, data classes, tenants, and failure impact;
- applicable compliance or specialist review boundaries.

Do not infer approval criteria from the proposed technology.

### Phase 1 — Reconstruct the Design

Create a compact model of:

- actors, system boundary, external dependencies, and trust boundaries;
- runtime components, protocols, data ownership, and deployment topology;
- critical synchronous and asynchronous paths;
- authoritative stores, caches, replicas, indexes, and event logs;
- operational owners and control plane;
- current state, target state, and transition state for migrations.

When the document and implementation disagree, report both and identify the effective behavior.

### Phase 2 — Trace Requirements to Decisions

For each architecturally significant requirement, identify:

- motivating requirement, invariant, risk, or constraint;
- selected decision and realistic alternative;
- trade-off and consequence;
- measurement or validation method;
- reversal or review trigger.

A decision with no traceable motivation is unsupported. A requirement with no decision or control is uncovered.

### Phase 3 — Challenge Correctness and Data Semantics

Inspect:

- business invariants and their atomic enforcement;
- state machines and legal transitions;
- source of truth and ownership for every critical entity;
- transaction and consistency boundaries;
- concurrent updates, conflicts, idempotency, deduplication, and ordering;
- duplicate, delayed, out-of-order, and lost messages;
- ledger, reconciliation, repair, and audit for money/inventory/quota/entitlement;
- schema, key, index, partition, retention, deletion, backup, and restore semantics.

A workflow diagram without failure and repair behavior is incomplete.

### Phase 4 — Challenge Distribution and Scale

Demand evidence for:

- service boundaries and independent ownership/deployment needs;
- capacity estimates with peak, burst, skew, growth, and sensitivity;
- latency budget and tail behavior;
- partition keys, resharding, hot keys, noisy neighbors, and celebrity tenants;
- queue bounds, backlog drain, consumer capacity, DLQ, and replay;
- connection, thread, memory, disk, file-descriptor, and dependency quotas;
- admission control, backpressure, load shedding, and degraded modes;
- retry amplification and timeout propagation.

Autoscaling and orchestration do not substitute for bounded overload behavior.

### Phase 5 — Challenge Failure and Recovery

Walk these failures where relevant:

- process, node, zone, region, network partition;
- database, broker, cache, DNS, certificate, identity provider, and external API;
- bad deploy, incompatible schema, configuration error, secret rotation;
- data corruption, operator error, backlog, quota exhaustion, and cost spike.

For each, require detection, containment, user impact, degraded behavior, recovery, reconciliation, owner, RTO, RPO, and proof method.

Replication is not backup. Backup is not recovery evidence. Multi-zone is not regional disaster recovery.

### Phase 6 — Challenge Security, Privacy, and Abuse

Inspect identity and authorization at every service and data boundary, not only UI or gateway. Verify tenant propagation and isolation in APIs, caches, queues, jobs, search, object storage, logs, analytics, backups, and support tooling.

Review secrets, encryption and key lifecycle, input/output validation, SSRF, injection, file upload, dependency trust, audit, data minimization, retention, deletion, residency, rate limiting, abuse, fraud, incident response, and privileged operator paths.

For AI systems, also review prompt injection, tool authority, memory scope, data exfiltration, eval integrity, budgets, approval, traces, and kill switches.

### Phase 7 — Challenge Delivery and Operations

Verify:

- SLIs/SLOs and error-budget actions tied to user journeys;
- logs, metrics, traces, correlation, cardinality, retention, and privacy;
- alerts tied to impact, runbooks, escalation, and on-call ownership;
- compatible API/event/schema evolution;
- expand-migrate-contract, backfill, reconciliation, cutover, rollback, and roll-forward;
- progressive delivery, feature flags, canaries, and stop criteria;
- restore drills, game days, capacity tests, chaos tests, and migration rehearsals;
- cost drivers, unit economics, budgets, lock-in, and exit paths.

### Phase 8 — Score and Decide

1. Score visible evidence using the 100-point scorecard.
2. Run the deterministic scanner when the input is Markdown:

```bash
python scripts/score_architecture.py path/to/architecture.md --format json
```

3. List critical findings independently of the numeric score.
4. Assign one verdict:
   - **PASS** — score at least 85, no critical blocker, validation evidence is sufficient;
   - **CONDITIONAL** — score 60–84 or material evidence remains, with explicit conditions and owners;
   - **BLOCK** — critical blocker exists or score is below 60.
5. State confidence and evidence limitations.

The script is a structural aid, not a correctness or compliance certificate.

## Critical Blockers

Block approval when any applicable condition is unresolved:

- money or balances use floating-point arithmetic;
- an invariant has no atomic enforcement point;
- database and broker are dual-written without atomic coordination or repair;
- a queue, retry loop, fan-out, cache, connection pool, or concurrency path is unbounded;
- cache or search index is accidental authority without durable recovery;
- exactly-once is claimed without a precise boundary and effect proof;
- active-active writes lack conflict, ownership/routing, and fencing semantics;
- internal network location substitutes for workload identity and authorization;
- tenant authorization exists only at UI/gateway;
- backups have no restore rehearsal and stated RTO/RPO;
- irreversible migration/deploy lacks compatibility window and rollback/roll-forward;
- consequential AI tools lack deterministic policy, scoped authority, approval, and audit;
- critical recovery, security, or load claims have no validation method.

## Severity Model

| Severity | Meaning | Release effect |
|---|---|---|
| **Critical** | likely data loss, invariant breach, cross-tenant access, unauthorized consequential action, unrecoverable outage, or invalid release claim | block |
| **High** | major user impact or operational failure with no adequate containment | block or explicit executive risk acceptance |
| **Medium** | material weakness with bounded workaround | condition with owner and date |
| **Low** | maintainability, clarity, or optimization opportunity | follow-up |

Prioritize by impact and exploitability/frequency, not count.

## Output Contract

Produce sections in this order:

1. **Verdict, score, confidence, and decision being gated.**
2. **Architecture reconstruction** — concise current/target model.
3. **Critical findings** — evidence, impact, failure scenario, required condition.
4. **High and medium findings** — ranked, deduplicated, actionable.
5. **Requirement-to-decision gaps.**
6. **Invariant, data, and workflow findings.**
7. **Scale and overload findings.**
8. **Reliability and recovery findings.**
9. **Security, privacy, tenancy, and abuse findings.**
10. **Operations, delivery, migration, and cost findings.**
11. **Evidence reviewed and evidence missing.**
12. **Approval conditions** with owner, proof, and due/review trigger.
13. **Positive evidence** worth preserving.

Use [review report template](assets/architecture-review-report-template.md) for a file artifact.

## Stop Conditions

Stop and request/recover evidence rather than inventing it when:

- the reviewed artifact is unavailable or materially incomplete;
- diagrams omit labels, ownership, protocols, or trust boundaries needed for the decision;
- repository behavior cannot be reconciled with the architecture claim;
- workload, incident, restore, security, or migration evidence is referenced but not supplied;
- the reviewer would need legal, compliance, safety, or domain certification beyond architecture review;
- approval depends on a live test that has not been run;
- the author asks the reviewer to lower a gate instead of resolving the risk.

Do not stop merely because the design is complex. Report verified findings and explicit evidence gaps.

## Review Quality Rules

- Cite the exact evidence for every material finding.
- Explain the failure mechanism, not only the preferred pattern.
- Do not list generic best practices that do not affect this design.
- Merge repeated symptoms under the root architectural cause.
- State when a finding is an inference.
- Give the smallest sufficient approval condition; do not prescribe a rewrite reflexively.
- Verify fresh test, restore, load, migration, or policy evidence before claiming a blocker is resolved.
