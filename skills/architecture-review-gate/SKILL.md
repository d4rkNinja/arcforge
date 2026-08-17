---
name: architecture-review-gate
description: "Use when independently reviewing or verifying an architecture specification, RFC, ADR, diagram, migration plan, AI or agent design, production-readiness proposal, architecture metrics, or post-incident structural causes. May frame review criteria or recommend bounded remediation, but does not own greenfield design or repository changes."
---

# Review Software Architecture

## Overview

Perform an independent, adversarial architecture review. Reconstruct the system from evidence, challenge the riskiest decisions, distinguish missing evidence from actual defects, and block approval when a critical invariant, security boundary, recovery path, or operational control is absent.

**Core principle:** Review architecture as an evidence-backed vector of qualities and obligations. No scalar summary can waive a critical failure.

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
- architecture fitness-function and metric review;
- comparison of current and target architecture.

The review is independent. Do not rewrite the architecture or make repository changes unless the user explicitly changes the task.

## Select the Operating Mode

| Mode | Use when | Required result |
|---|---|---|
| **Think** | The independent review contract or rubric must be framed before assessment | decision being gated, frozen dimensions, evidence anchors, and blocker policy |
| **Review** | An architecture artifact or repository is ready for the default independent assessment | evidence-separated findings, blockers, confidence, and approval conditions |
| **Change** | The user explicitly requests remediation after the independent verdict | bounded recommendations or a handoff to the owning design/domain skill; no silent self-rewrite |
| **Verify** | A finding or approval condition is claimed resolved | fresh evidence, reassessment, and residual risks |

If the user names a mode, use it. Otherwise default to Review for an existing artifact and state the inference in one sentence. Combined work proceeds **Think → Review → Change → Verify**, but the independent verdict remains distinguishable from authoring and remediation. Think may stop with the review contract; Review may stop with findings. Change must not claim completion before Verify, and Verify must never convert missing evidence into a pass.

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

- Use [contextual architecture evidence vector](references/01-contextual-ai-review-rubric.md) for every formal gate.
- Use [critical failure patterns](references/02-critical-failure-patterns.md) for blocker review.
- Use [evidence and challenge guide](references/03-evidence-challenge-guide.md) for claim verification.
- Use [rubric calibration guide](references/04-rubric-calibration-guide.md) when selecting dimensions, evidence anchors, decision conditions, or multi-model review.
- Use [fitness gates, incident causality, and metric governance](references/05-fitness-gates-incidents-and-metrics.md) for formal gates, post-incident review, or architecture metrics.
- Use [strong review input](examples/review-input-strong.md) and [critical review input](examples/review-input-critical.md) to calibrate the evidence expected before judging a proposal.

## Review Workflow

Apply the phases according to mode: Think freezes the review contract before assessment; Review produces the independent verdict; Change occurs only after explicit user authorization and is recorded separately from the verdict; Verify re-runs the evidence gate and marks every unavailable check as missing evidence.

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

Organize the trace through five gates without treating them as equally weighted categories:

- **A — Problem and fitness:** measurable requirements, constraints, stakeholders, and unacceptable failure;
- **B — State and boundaries:** authority, invariants, communication semantics, and the capability purchased by each boundary;
- **C — Failure and assurance:** partial failure, detection, recovery, security, and test evidence;
- **D — Delivery and operation:** safe change, observability, capacity, ownership, and restore ability;
- **E — Economics, complexity, and evolution:** lifecycle cost, obligations, reversibility, lifetime, and revision triggers.

Report each gate's evidence state and decision test. Do not average a failed gate into stronger evidence elsewhere.

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

### Phase 8 — Assess the Evidence Vector and Decide

1. Read `references/01-contextual-ai-review-rubric.md` and derive decision-specific dimensions from the five gates, ASRs, invariants, failure impact, regulatory context, change scope, and supplied evidence.
2. Before assessing the proposal, publish and freeze each applicable dimension, why it matters, its evidence anchors, required evidence maturity, and the condition it protects. Explain exclusions.
3. For every dimension, cite evidence and classify it as observed, validated, implemented, designed, claimed, inferred, contradicted, or missing. Keep evidence quality separate from blocker status.
4. Inspect the proposal's Complexity Ledger. If none exists, report the absence. Review at least: decision, requirement, capability, alternatives, introduced concepts/state/protocol/configuration/dependencies, operational responsibility, failure modes, knowledge, security, performance, cost, reversibility, expected lifetime, evidence, validation trigger, owner, and review date.
5. Perform an adversarial second pass. Challenge omitted dimensions, hidden dependencies, duplicated credit, unsupported inference, technology favoritism, and whether stronger evidence changes the conclusion. This is a completed review pass, not a list of future adversarial tests: report what was challenged, what changed, and why the verdict did or did not move.
6. Review every applicable pattern in `references/02-critical-failure-patterns.md` independently. A critical blocker forces **BLOCK** regardless of strengths elsewhere.
7. Assign one verdict:
   - **PASS** — no blocker, every required decision condition is met, and evidence maturity is sufficient;
   - **CONDITIONAL** — no blocker, but named evidence or remediation conditions remain;
   - **BLOCK** — a critical blocker exists or a required decision condition fails;
   - **INSUFFICIENT EVIDENCE** — the review contract or decisive evidence is too incomplete for a responsible verdict.
8. State confidence, model identity/version when available, evidence limitations, and which conclusions are source claims, verified facts, reviewer inferences, or unvalidated claims.

Keep the dimension vector primary. A numeric summary is optional only when the decision owner has a defensible use for it, the derivation and assumptions are transparent, no universal threshold is implied, and sensitivity analysis shows what changes under plausible alternatives. It never determines approval.

### Phase 9 — Review Incidents and Metrics When Applicable

For a post-incident review, trace:

`decision → hidden dependency → trigger → propagation → blast radius → detection → recovery constraints → structural correction`

Separate the initiating trigger from the architectural enabling conditions. Do not substitute retraining or replacing the triggering person for structural correction.

For every architecture metric, require definition, unit, source, data quality, intended decision, confounders, gaming risk, owner, and review/retirement date. Use metric vectors and within-system trends; never use architecture metrics to rank individual engineers.

Perform this review through the active AI model and the supplied references. No executable helper or external model API is required.

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

## Companion Skills and Standalone Safety

| Type | When | Companion | Missing companion behavior |
|---|---|---|---|
| **Handoff** | A general production architecture must be created or revised | `system-architecture-harness` | Finish the independent verdict without pretending the redesign was completed. |
| **Handoff** | An AI subsystem must be created or revised | `ai-agent-system-architecture` | Finish the independent verdict and identify missing AI design depth. |
| **Recommended** | Code-level release evidence must be assessed | `quality-release` | Classify the evidence gap and do not infer release readiness. |

If a companion is unavailable, complete the independent verdict from visible evidence, name the missing design or verification depth, and recommend the exact technical ID or `independent-architecture-review` installation group. Never claim unavailable material was read, invent evidence, or lower a blocker to compensate for missing depth.

## Output Contract

The selected mode is authoritative. Include only applicable fields below; a planned check is a validation path, not verification evidence.

Scale the output to the active mode: Think returns a frozen review contract; Review returns the independent verdict and findings; Change returns bounded remediation or an explicit owner-skill handoff; Verify returns fresh reassessment evidence. Keep those artifacts separate in a combined flow.

Produce sections in this order:

1. **Verdict, confidence, model disclosure, and decision being gated.**
2. **Architecture reconstruction** — concise current/target model.
3. **Five-gate evidence vector** — dimension, protected condition, evidence state, evidence quality, finding, and required proof.
4. **Critical blockers** — evidence, impact, failure scenario, required condition.
5. **High and medium findings** — ranked, deduplicated, actionable.
6. **Requirement-to-decision and Complexity Ledger gaps.**
7. **Invariant, data, workflow, scale, and overload findings.**
8. **Reliability, recovery, and post-incident causal findings.**
9. **Security, privacy, tenancy, and abuse findings.**
10. **Operations, delivery, migration, cost, and metric-governance findings.**
11. **Evidence reviewed, evidence challenged, and evidence missing.**
12. **Adversarial and sensitivity second-pass findings** — challenges run, result changes, and verdict sensitivity.
13. **Approval conditions** with owner, proof, and due/review trigger.
14. **Positive evidence** worth preserving.

Use [review report template](assets/architecture-review-report-template.md) for a file artifact. Use [post-incident review template](assets/post-incident-architecture-review-template.md) for an incident. Use [review checklist](assets/architecture-review-checklist.md) for a compact gate artifact. Read [the contextual review example](examples/contextual-review-example.md) or [post-incident structural review example](examples/post-incident-structural-review-example.md) when calibrating a first review.

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
