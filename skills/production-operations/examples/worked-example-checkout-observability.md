# Worked example: observability and recovery evidence for checkout

> Calibration artifact: this shows the shape and depth a run of the `production-operations` skill should produce. It is illustrative, not exhaustive; the papers remain authoritative.

**Request (as a user would phrase it):**

> Our checkout service goes to production next month. Add whatever logging and monitoring it needs, and confirm the DR story — we take daily managed DB snapshots.

## Papers consulted

- [057 Metrics](../references/papers/057-metrics.md) — SLI selection, cardinality
- [056 Logging](../references/papers/056-logging.md) — structure, redaction, correlation
- [059 Health Checks](../references/papers/059-health-checks.md) — readiness semantics
- [076 Backup](../references/papers/076-backup.md) / [077 Restore](../references/papers/077-restore.md) / [078 Disaster Recovery](../references/papers/078-disaster-recovery.md) — backup ≠ restore, RTO/RPO
- [138 Operational Runbooks](../references/papers/138-operational-runbooks.md) — alert-to-action wiring

## Assumptions (labeled)

- **A1 (assumption):** checkout revenue tolerance is 99.9% availability and ≤15 minutes of data loss (RPO 15 min, RTO 1 h). *If false:* every downstream choice (snapshot cadence, failover design) changes.
- **A2 (assumption):** daily snapshots only — which contradicts RPO 15 minutes; flagged as a defect in the current story, not accepted.

## Pre-implementation questions answered

- **What journey is protected?** "Customer completes checkout." Its SLI: successful paid order creations / attempted checkouts, latency p95, payment-provider dependency health (paper 057).
- **Which signals, which owners?** Journey SLI + queue lag for the fulfillment queue + DB replica lag; each alert has a named owner and runbook link (papers 057, 138).
- **Logs?** Structured events with correlation ID, outcome class, bounded tenant/order identifiers, redacted errors; no payloads (paper 056).
- **Health?** Liveness = process serving; readiness = DB reachable, queue publisher ready, provider circuit not open — dependency depth bounded (paper 059).
- **DR claim valid?** No: daily snapshots give RPO ≈ 24 h ≠ 15 min, and a snapshot is not restore evidence. Required: transaction-log backups at 5–15 min cadence, restore rehearsal with observed RTO/RPO, and an isolated backup account (papers 076–078 MUST).

## Rule-to-decision map

| Rule (level) | Decision | Enforcement point | Verification |
|---|---|---|---|
| Alerts tied to user impact (MUST) | Checkout SLI alert + burn-rate alerting | Alert rules with owner + runbook link | Synthetic failure fires alert; runbook executes |
| Redacted structured logs (MUST) | Logging schema with redaction middleware | Emitter + CI log scan | No PII/secrets in sampled logs |
| Readiness ≠ liveness (MUST) | Separate probes, bounded dependency checks | Probe endpoints | Dependency outage flips readiness, not liveness |
| Restore is evidence (MUST) | Quarterly restore drill into isolated environment with timed RPO/RTO | Drill calendar + report | Observed RPO 9 min / RTO 41 min documented |
| Cardinality bounds (MUST) | No per-user metric labels; tenant as max granularity | Metric lint in CI | Cardinality report stable under load test |

## Failure modes addressed

- Outage detected late — journey SLI with burn-rate alerting.
- Alert fires, nobody knows what to do — runbook linked and rehearsed.
- Restore discovered broken during a real incident — quarterly drills.
- Metric explosion degrading the platform — cardinality lint.

## Verification evidence

- Chaos drill: payment provider down → readiness flips, degradation visible, alert fires with owner paged, runbook followed to resolution.
- Restore drill: timed restore of last log backup, integrity checks pass, drill report retained.
- Load test: metrics cardinality and log volume within budgets.

## Stop-condition check

No stop condition remains for observability; the DR gap (RPO 24 h vs required 15 min) is reported as a launch blocker with the log-backup remediation, not waived.

## Deliverable summary

SLI/alert set with owners, structured log schema, split probes, runbook drafts, and the restore-drill program — plus one honest blocker: current backup cadence fails the stated RPO until transaction-log shipping is enabled.
