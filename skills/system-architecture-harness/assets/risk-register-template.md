# Architecture Risk Register

Use this register for uncertain events that could harm outcomes. Track current defects and outages in an issue or incident log; track unverified beliefs in the assumption register.

## Metadata

- System:
- Review date:
- Review cadence:
- Risk owner:
- Escalation authority:
- Risk tolerance statement:

## Scales

### Probability

| Rating | Meaning |
|---:|---|
| 1 | Rare; not expected during the planning horizon |
| 2 | Unlikely but plausible |
| 3 | Possible |
| 4 | Likely |
| 5 | Almost certain or recurring |

### Impact

| Rating | Meaning |
|---:|---|
| 1 | Negligible; no material user or business effect |
| 2 | Minor; contained degradation |
| 3 | Material; SLO or delivery impact |
| 4 | Major; serious financial, security, compliance, or availability impact |
| 5 | Critical; existential, irreversible, or safety-impacting consequence |

**Exposure = probability × impact.** Use the score to prioritize discussion, not as a substitute for judgment. A low-probability catastrophic risk can still require immediate treatment.

## Register

| ID | Category | Risk statement: because / event / impact | Probability | Impact | Exposure | Leading indicators | Preventive controls | Contingency / recovery | Validation or drill | Owner | Due date | Status | Residual risk | Acceptance authority |
|---|---|---|---:|---:|---:|---|---|---|---|---|---|---|---|---|
| R-001 | Reliability | Because ..., there is a risk that ..., causing ... | 3 | 5 | 15 | ... | ... | ... | ... | ... | ... | Open | ... | ... |

## Category Prompts

- Business and product assumptions
- Capacity and performance
- Data correctness, consistency, retention, and loss
- Dependency, regional, and control-plane failure
- Security, privacy, abuse, fraud, and compliance
- Delivery, migration, compatibility, and rollback
- Operations, observability, on-call, and ownership
- Cost, quota, licensing, and vendor concentration
- Organization, staffing, skills, and cognitive load
- AI/ML model, data, prompt, tool, and autonomy risk

## Treatment Decision

For every material risk, choose one explicitly:

- **Avoid:** remove the risky design or requirement.
- **Reduce:** lower probability or impact with controls.
- **Transfer:** shift contractual or financial exposure without pretending responsibility disappears.
- **Accept:** record rationale, residual exposure, expiry/review date, and named authority.

## Review Rules

1. Review critical and high risks at every architecture or operating review.
2. Convert triggered risks into incidents or issues while retaining the original risk history.
3. Close a risk only with evidence that exposure is removed or accepted by the authorized owner.
4. Reopen risks when assumptions, scale, dependencies, regulations, or threat conditions change.
5. Link each high risk to the relevant ADR, SLO, threat, failure mode, test, or migration plan.
