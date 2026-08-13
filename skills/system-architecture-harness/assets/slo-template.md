# SLO: <Service or User Journey>

- Owner: <team>
- Effective date: YYYY-MM-DD
- Review cadence: <monthly/quarterly>
- Criticality: <tier>
- Consumers/users: <who>

## 1. Service/Journey Description

<What user outcome is protected and why it matters.>

## 2. Scope

### Included

- 

### Excluded

Exclusions must be narrow, measurable, and justified.

- 

## 3. SLIs and Objectives

| SLI | Good event | Valid event/population | Objective | Window | Measurement point |
|---|---|---|---:|---|---|
| Availability/correctness | | | | | |
| Latency | | | | | |
| Freshness | | | | | |
| Durability/recovery | | | | | |

## 4. Data Quality

- telemetry source:
- known blind spots:
- sampling:
- delayed/corrected data behavior:
- dashboard/query:
- owner of SLI pipeline:

## 5. Error Budget

For ratio SLOs:

```text
error budget = 1 - SLO
allowed bad events = valid events × error budget
```

| SLO | Budget | Current consumption | Burn rate |
|---|---:|---:|---:|

## 6. Error-Budget Policy

| Condition | Action | Authority/owner |
|---|---|---|
| Healthy budget | normal releases |
| Fast-burn threshold | page and halt/rollback risky rollout |
| Budget warning | prioritize reliability work, restrict risky change |
| Budget exhausted | freeze nonessential change except security/critical fixes |
| Single severe incident | postmortem and required corrective action |

Document treatment of dependency-caused failures and exceptions.

## 7. Alerting

| Alert | Window/burn threshold | Page/ticket | Runbook |
|---|---|---|---|

## 8. Dependencies and Assumptions

| Dependency/assumption | Impact | Dependency SLO/contract | Degraded mode |
|---|---|---|---|

## 9. Review and Change

- target rationale:
- cost/complexity trade-off:
- change approval:
- next review date:
- evidence needed to tighten/relax target:
