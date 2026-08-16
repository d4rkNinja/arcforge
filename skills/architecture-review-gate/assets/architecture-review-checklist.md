# Architecture Review Checklist

## Gate A — Problem and Fitness

- [ ] Problem and stakeholders precede technology.
- [ ] Quality attributes are measurable scenarios.
- [ ] Workload covers range, peak, burst, growth, skew, and uncertainty.
- [ ] Constraints, assumptions, unacceptable failure, and decision owner are explicit.

## Gate B — State and Boundaries

- [ ] State is classified as authoritative, derived, ephemeral, sensitive, or rebuildable.
- [ ] Invariants, transactions, consistency, ordering, duplication, cancellation, and unknown outcomes are explicit.
- [ ] Every boundary buys independent change, scale, failure, governance, or security capability.
- [ ] Ownership, retention, deletion, residency, backup, and restore are explicit.

## Gate C — Failure and Assurance

- [ ] Retries, deadlines, queues, pools, concurrency, fan-out, and recovery load are bounded.
- [ ] Shared dependencies and correlated failure domains are mapped.
- [ ] Threats, privileges, identities, secrets, abuse, and tenant boundaries are reviewed.
- [ ] Tests cover logic, integration, concurrency, load, recovery, and adversarial failure.
- [ ] Every applicable critical blocker was checked independently.

## Gate D — Delivery and Operation

- [ ] Code, schema, configuration, and infrastructure changes support mixed versions and safe repair.
- [ ] Canary, stop conditions, rollback/roll-forward, backfill, and reconciliation exist where needed.
- [ ] Telemetry connects user outcomes to requests, workflows, data, dependencies, cost, and owners.
- [ ] On-call, runbooks, restore drills, capacity envelope, and next bottleneck are evidenced.

## Gate E — Economics, Complexity, and Evolution

- [ ] Cost includes infrastructure, people, incidents, coordination, licensing, support, and migration.
- [ ] Complexity Ledger covers capability, alternatives, obligations, failure, knowledge, security, performance, cost, and operations.
- [ ] Reversibility, expected lifetime/deletion, compatibility, and exit path are explicit.
- [ ] Every decision has evidence, a validation trigger, owner, and review date.

## Evidence and Decision Integrity

- [ ] Every dimension has an evidence state and quality; missing is distinct from contradicted.
- [ ] Source type, study design, scale/context, counter-evidence, validity threats, and stable citation are recorded for consequential external claims.
- [ ] Source claims are separate from reviewer inferences.
- [ ] Blockers remain non-compensable; the vector is primary.
- [ ] Any optional numeric summary is transparent, sensitivity-aware, non-authorizing, and free of universal thresholds.
- [ ] A separate adversarial/sensitivity pass was completed and reports the challenges run, findings changed, and verdict sensitivity; it is not merely a future test list.

## Incident and Metric Addendum

- [ ] Incident analysis separates trigger from enabling conditions and traces decision → hidden dependency → trigger → propagation → blast radius → detection → recovery constraints → structural correction.
- [ ] Metrics document definition/unit, source/data quality, intended decision, confounders, gaming risk, owner, and review/retirement.
- [ ] Architecture metrics are not used to rank individual engineers.
