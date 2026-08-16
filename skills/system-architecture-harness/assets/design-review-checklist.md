# Production Architecture Design Review Checklist

Use this as a final go/no-go gate. A checked item means evidence exists, not merely that the topic was discussed.

## 1. Scope and Outcomes

- [ ] Decision scope, system boundary, actors, and external dependencies are explicit.
- [ ] Business outcome, success metrics, constraints, and non-goals are stated.
- [ ] Existing repository, runtime, incidents, telemetry, and standards were inspected when available.
- [ ] Facts, assumptions, unknowns, and decisions are visibly separated.
- [ ] Architecturally significant requirements have measurable thresholds.

## 2. Capacity and Performance

- [ ] Average, peak, burst, and growth workloads are quantified with formulas.
- [ ] Read/write mix, payload size, retention, cardinality, fan-out, and concurrency are estimated.
- [ ] End-to-end latency budget is allocated across hops.
- [ ] Hot keys, hot tenants, large objects, skew, and pathological traffic are addressed.
- [ ] Overload behavior, quotas, admission control, and load shedding are designed.
- [ ] A load, stress, soak, or capacity test will validate the largest assumptions.

## 3. Correctness and Data

- [ ] Business invariants, state machines, legal transitions, and terminal states are explicit.
- [ ] Every authoritative datum has one named owner and source of truth.
- [ ] Storage choices follow access patterns, transactions, consistency, retention, and recovery needs.
- [ ] Partition keys and indexes are justified against real queries and skew.
- [ ] Idempotency scope, key, result retention, and duplicate response semantics are defined.
- [ ] Cross-boundary workflows define atomicity, outbox/inbox or equivalent, retry, compensation, and reconciliation.
- [ ] Ordering, deduplication, late data, replay, tombstones, and deletion are covered where applicable.
- [ ] Money uses exact arithmetic, immutable journal/ledger records, and reconciliation where applicable.

## 4. Boundaries and Interfaces

- [ ] Component boundaries align with ownership, change cadence, consistency, and failure isolation.
- [ ] A modular monolith remains the default unless distribution has explicit evidence and owners.
- [ ] Synchronous dependencies are necessary, bounded, and included in the latency/availability budget.
- [ ] API contracts define authentication, authorization, validation, pagination, errors, concurrency control, and versioning.
- [ ] Event contracts define schema ownership, compatibility, keys, ordering, delivery, retention, replay, and privacy.
- [ ] Dependency and deployment diagrams complement the system context and component view.

## 5. Reliability and Recovery

- [ ] User-centric SLIs, SLOs, error budgets, and alert thresholds are defined.
- [ ] Critical-path dependencies have timeouts, bounded retries with jitter, and failure containment.
- [ ] Queues are bounded and have backpressure, poison-message handling, replay, and lag objectives.
- [ ] Degraded modes preserve safety and correctness.
- [ ] RTO/RPO derive from business impact and map to tested recovery procedures.
- [ ] Backups include restore drills, credentials/keys, dependencies, reconciliation, and proof of recovery.
- [ ] Regional or active-active claims include traffic steering, consistency, fencing, conflict resolution, and split-brain tests.

## 6. Security, Privacy, and Abuse

- [ ] Trust boundaries, assets, identities, attackers, abuse cases, and threats are modeled.
- [ ] Every request is authenticated and authorized at the resource/action boundary; network location is not trusted.
- [ ] Workload identities and secrets are least-privileged, rotated, scoped, and auditable.
- [ ] Input validation, output encoding, SSRF/egress controls, rate limits, and anti-automation controls are included.
- [ ] Encryption, key ownership, rotation, revocation, and recovery are explicit.
- [ ] Data classification, minimization, purpose, residency, retention, export, and deletion are specified.
- [ ] Logs, metrics, traces, events, backups, caches, and prompts avoid prohibited sensitive data.
- [ ] High-risk actions have approval, separation-of-duty, tamper-evident audit, or equivalent controls.

## 7. Operability and Delivery

- [ ] Logs, metrics, traces, profiles, business signals, and correlation identifiers cover critical journeys.
- [ ] Alerts are actionable and tied to user impact, SLO burn, capacity, or security signals.
- [ ] Dashboards, runbooks, escalation, and service ownership exist.
- [ ] Deployment uses progressive exposure, health gates, compatibility windows, and tested rollback/roll-forward.
- [ ] Schema and data migrations are expand/migrate/contract, restartable, observable, rate-limited, and reversible where possible.
- [ ] Feature flags have owners, safe defaults, expiry, and kill switches.
- [ ] Supply-chain controls cover provenance, dependencies, artifacts, secrets, and environment promotion.

## 8. Economics and Organization

- [ ] Major cost drivers, per-unit economics, quotas, and budget alerts are estimated.
- [ ] Redundancy and performance tiers are justified by business loss, not prestige.
- [ ] Vendor lock-in, data egress, licensing, support, and exit paths are considered.
- [ ] Team topology, ownership, cognitive load, on-call capability, and skill constraints support the design.
- [ ] Energy or sustainability constraints are included when material.

## 9. AI / ML / Agent Systems, When Applicable

- [ ] Model and tool capabilities are bounded by an explicit threat and risk model.
- [ ] Prompts, retrieved content, model output, and tool parameters are treated as untrusted.
- [ ] Tool permissions are least-privileged and high-impact actions require deterministic validation or approval.
- [ ] Evaluation covers quality, safety, bias, privacy, latency, cost, adversarial inputs, and regressions.
- [ ] Provenance, model/prompt/tool versions, decisions, actions, and overrides are auditable.
- [ ] Budgets limit tokens, steps, time, money, retries, fan-out, and recursive delegation.
- [ ] Safe fallback, rollback, disablement, and human recovery paths exist.

## 10. Decision and Evidence Gate

- [ ] Alternatives and trade-offs are recorded in ADRs.
- [ ] Every high-risk assumption has a validation method, owner, threshold, and due point.
- [ ] Failure modes and critical risks are recorded with owners and drills.
- [ ] The design includes explicit unresolved questions rather than hiding them.
- [ ] The contextual AI review has no unresolved critical gate.
- [ ] The final verdict is one of: PASS, CONDITIONAL, BLOCK, or INSUFFICIENT EVIDENCE, with critical blockers kept non-compensable.
