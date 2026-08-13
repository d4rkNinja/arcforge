# 100-Point Architecture Review Scorecard

Score only visible evidence. A category may earn partial credit. Critical blockers override the total.

| Category | Weight | Full-credit evidence |
|---|---:|---|
| Scope, outcomes, and evidence | 10 | decision, actors, critical journeys, constraints, non-goals, facts vs assumptions, owners |
| Requirements and workload | 10 | measurable ASRs, peak/burst/concurrency, storage/bandwidth growth, sensitivity, dependency limits |
| Boundaries and ownership | 10 | context, runtime responsibilities, protocols, domain/data ownership, trust and deployment boundaries, justified style |
| Data and correctness | 15 | invariants, states, source of truth, transaction/isolation, concurrency, idempotency, ordering, retention, repair |
| APIs, events, and workflows | 10 | typed contracts, authn/authz, errors, versioning, deadlines, quotas, delivery/order/replay/DLQ, success/failure sequences |
| Performance and overload | 10 | latency budget, bottlenecks, partition/skew, bounded resources, backpressure, admission, load/burst/soak proof |
| Reliability and recovery | 15 | SLO/error budget, failure matrix, containment, degraded modes, RTO/RPO, tested restore/failover, reconciliation |
| Security, privacy, tenancy, abuse | 10 | threat model, identity/authz, tenant isolation, encryption/secrets, data lifecycle, abuse, audit, incident path |
| Operations, delivery, migration | 5 | telemetry, alerts/runbooks/ownership, compatible rollout, migration/backfill/cutover, rollback/roll-forward |
| Decisions, cost, and validation | 5 | alternatives, ADRs, unit economics, risks, review triggers, experiments and acceptance evidence |

## Verdict

- **PASS:** 85–100, no critical blockers, no unowned high risk.
- **CONDITIONAL:** 60–84 with explicit conditions, owners, and proof.
- **BLOCK:** below 60 or any unresolved critical blocker.

## Critical override

Block regardless of score for an unresolved invariant breach, cross-tenant or authorization failure, unsafe financial arithmetic, uncoordinated critical dual write, unbounded failure amplification, unrecoverable data path, active-active ambiguity, or high-impact AI action without governed authority.

## Scoring discipline

- Do not award points for headings without evidence.
- Do not double-count one sentence across unrelated categories.
- Treat estimates as useful when assumptions and validation are explicit.
- Treat vendor feature claims as hypotheses until configured behavior and recovery are shown.
- Preserve positive evidence so remediation does not remove working controls.
