# Architecture Review Scorecard

Use this scorecard after the design is complete enough to review. It is a forcing function, not a substitute for expert judgment.

## Contents

- 1. Scoring Rules
- 2. Weighted Scorecard — 100 Points
- 3. Critical Gates
- 4. Evidence Levels
- 5. Review Report Template
- Verdict
- Highest-Risk Findings
- Score Breakdown
- Assumption Register
- Decision Challenges
- Required Validation
- 6. Review Conduct

## 1. Scoring Rules

For each criterion assign:

- **0% of points:** absent, contradicted, or dangerously wrong;
- **25%:** mentioned but vague/unowned/unmeasurable;
- **50%:** plausible design with material gaps;
- **75%:** complete design with minor gaps or limited evidence;
- **100%:** explicit, traceable, validated or backed by a concrete validation plan.

Round to the nearest 0.5 point. Every score must cite evidence in the architecture document, repository, measurement, or test result.

### Rating

| Score | Rating | Meaning |
|---:|---|---|
| 90–100 | Strong | production-ready design evidence; monitor residual risks |
| 80–89.5 | Conditional | good foundation; resolve high-risk gaps before launch |
| 65–79.5 | Weak | material redesign or evidence required |
| <65 | Unsafe/incomplete | architecture is not ready for implementation or launch |

**Critical-gate rule:** A design cannot pass while any critical gate is open, regardless of numeric score.

## 2. Weighted Scorecard — 100 Points

### A. Business Fit, Scope, and Evidence — 8 points

| Criterion | Points |
|---|---:|
| Critical outcomes, actors, journeys, and non-goals are clear | 2.0 |
| Current-state evidence and constraints are distinguished from assumptions | 2.0 |
| Decision horizon and growth scenarios are explicit | 1.0 |
| Dependencies, stakeholders, and specialist handoffs are identified | 1.5 |
| Architecture recommendation is traceable to business priorities | 1.5 |

### B. Requirements and ASRs — 8 points

| Criterion | Points |
|---|---:|
| Functional requirements and legal state transitions are defined | 2.0 |
| Latency, throughput, availability, durability, freshness, recovery, security, and cost targets are measurable where relevant | 3.0 |
| Workload shape, geography, tenancy, burst, and largest-tenant/skew assumptions are explicit | 1.5 |
| Conflicting requirements and accepted trade-offs are visible | 1.5 |

### C. Quantitative Capacity — 7 points

| Criterion | Points |
|---|---:|
| Average/peak/burst traffic and concurrency are calculated | 1.5 |
| Storage, indexes, replication, backup, retention, and growth are calculated | 1.5 |
| Bandwidth/egress/internal amplification are calculated | 1.0 |
| Queue/backlog/recovery drain and dependency quotas are modeled | 1.0 |
| 1×/10×/100× or equivalent sensitivity and breakpoints are shown | 1.0 |
| Units, assumptions, ranges, and safe capacity margins are visible | 1.0 |

### D. Boundaries, Responsibilities, and Ownership — 7 points

| Criterion | Points |
|---|---:|
| Context/trust boundaries and external dependencies are clear | 1.5 |
| Components/modules have one clear responsibility and stable contracts | 1.5 |
| Domain/data ownership and invariant boundaries align | 1.5 |
| Architecture style is justified against simpler alternatives | 1.0 |
| Runtime/service/data/event owners and support paths are assigned | 1.0 |
| Forbidden coupling and dependency direction are stated | 0.5 |

### E. Data, Correctness, and Consistency — 12 points

| Criterion | Points |
|---|---:|
| Critical invariants and state machines are explicit | 2.0 |
| Source of truth and derived-data rebuild paths are named | 1.5 |
| Schema, access patterns, keys, indexes, partitioning, and growth align | 1.5 |
| Transactions/isolation/concurrency/conflict semantics preserve invariants | 2.0 |
| Consistency/freshness/ordering are specified per operation | 1.5 |
| Idempotency, duplicate, out-of-order, and ambiguous outcome handling are explicit | 1.5 |
| Retention, archival, deletion, backup, restore, and reconciliation are defined | 1.0 |
| Schema/data migration and compatibility are safe | 1.0 |

### F. APIs, Events, and Workflows — 8 points

| Criterion | Points |
|---|---:|
| APIs/events have semantic contracts, ownership, auth, validation, limits, and errors | 1.5 |
| Versioning/backward-forward compatibility/deprecation are defined | 1.0 |
| Deadlines/timeouts/retries/cancellation are coordinated | 1.5 |
| Messaging defines delivery, ordering scope, retention, replay, DLQ, and lag | 1.5 |
| Critical workflows have explicit states, compensation/reconciliation, and operator repair | 1.5 |
| Success and failure sequence diagrams/flows cover critical journeys | 1.0 |

### G. Performance, Scalability, Overload, and Cost Efficiency — 8 points

| Criterion | Points |
|---|---:|
| End-to-end latency budget and bottleneck hypotheses are explicit | 1.5 |
| Scale strategy covers compute, storage, partitioning, skew, and resharding | 1.5 |
| Caches/CDN/precomputation include freshness and failure semantics | 1.0 |
| Queues/pools/concurrency/fan-out are bounded with backpressure | 1.5 |
| Admission control/load shedding/graceful degradation exist | 1.0 |
| Load/stress/soak test plan uses representative distributions | 1.0 |
| Unit cost and major cost drivers are instrumented | 0.5 |

### H. Reliability, Resilience, and DR — 12 points

| Criterion | Points |
|---|---:|
| User-journey SLIs/SLOs and error-budget action exist | 1.5 |
| Failure matrix covers process, dependency, network, data, region, change, and operator failures | 2.0 |
| Timeouts, bounded retries, jitter, breakers, and bulkheads are coherent | 1.5 |
| Degraded modes preserve correctness and prioritize critical work | 1.0 |
| Replica/failover topology and fencing prevent split authority | 1.5 |
| RTO/RPO are defined by capability/data class | 1.0 |
| Backups are isolated, retained, monitored, and restore-tested | 1.5 |
| Corruption/reconciliation and failback are designed | 1.0 |
| Chaos/game-day/DR verification is scheduled and owned | 1.0 |

### I. Security, Privacy, Abuse, and Compliance — 12 points

| Criterion | Points |
|---|---:|
| Assets, data classes, adversaries, trust boundaries, and threats are modeled | 1.5 |
| Human/workload/device identity and authentication are appropriate | 1.0 |
| Object/function/property/workflow authorization and least privilege are enforced | 2.0 |
| Tenant isolation is end-to-end, including data/cache/search/events/AI | 1.5 |
| Secrets, keys, encryption, rotation, and recovery are defined | 1.0 |
| API/input/resource-exhaustion/supply-chain controls are designed | 1.5 |
| Privacy purpose, minimization, retention, deletion, residency, and vendor handling are defined | 1.5 |
| Audit, incident response, break-glass, and control evidence are defined | 1.0 |
| Abuse/fraud/high-impact specialist handoffs are addressed | 1.0 |

### J. Observability and Operations — 8 points

| Criterion | Points |
|---|---:|
| Logs, metrics, traces, audits, correlation, and cardinality budgets exist | 1.5 |
| Dashboards and alerts are tied to user impact, correctness, saturation, lag, and security | 1.5 |
| Runbooks, on-call, escalation, dependency contacts, and incident roles are assigned | 1.5 |
| Health/readiness/synthetic probes reflect safe service | 1.0 |
| Capacity, cost, backup, certificate, quota, and lifecycle monitoring exist | 1.0 |
| Service catalog/documentation remains close to ownership and change | 0.5 |
| Operational workflows are tested or rehearsed | 1.0 |

### K. Delivery, Migration, and Evolution — 5 points

| Criterion | Points |
|---|---:|
| IaC/reproducible builds/config/secrets delivery and environment strategy exist | 1.0 |
| CI quality/security/contract/migration gates match risk | 1.0 |
| Progressive rollout has success/abort metrics and bounded blast radius | 1.0 |
| Rollback or roll-forward is valid for code, schema, events, and data | 1.0 |
| Migration/cutover/backfill/reconciliation/cleanup and deprecation are explicit | 1.0 |

### L. Cost, Sustainability, and Organization — 3 points

| Criterion | Points |
|---|---:|
| Baseline/growth cost and unit economics include egress, observability, backup, and people | 1.0 |
| Budgets/anomaly/allocation/retention/right-sizing controls exist | 0.5 |
| Build-vs-buy, lock-in, exit, and vendor concentration are assessed | 0.5 |
| Team cognitive load, service count, on-call, and ownership fit the organization | 0.5 |
| Resource efficiency/sustainability is considered without weakening requirements | 0.5 |

### M. Decision Quality and Validation — 2 points

| Criterion | Points |
|---|---:|
| Major decisions compare viable alternatives and record consequences/reversal triggers | 1.0 |
| Risks have owner/trigger/mitigation and validation targets the riskiest assumptions | 1.0 |

## 3. Critical Gates

Any unresolved item below fails the review unless formally accepted by an accountable authority with a dated remediation/monitoring plan.

### Correctness and data

- critical invariant has no atomic/serialized enforcement or reconciliation;
- money uses binary floating point or lacks currency/rounding semantics;
- cross-system dual write has no outbox/CDC/transaction/workflow repair;
- mutating/replayable operation has no idempotency/duplicate behavior;
- source of truth or data owner is ambiguous;
- unbounded data retention, queue, retry, fan-out, pool, or concurrency;
- data migration can irreversibly corrupt state without backup/reconciliation.

### Reliability and recovery

- no timeouts/deadlines on critical remote calls;
- retries can amplify outage without bounds/jitter/budget;
- two active writers/leaders can modify exclusive state without fencing;
- RTO/RPO required but no implementable/tested recovery path;
- replication is treated as backup;
- critical backup/restore/key recovery has never been tested;
- failover capacity or authority is missing.

### Security and privacy

- missing server-side authorization for sensitive object/action;
- tenant isolation not enforced at data access;
- secrets/tokens/sensitive data exposed in code/logs/prompts/client;
- public/expensive endpoint lacks resource/abuse controls;
- critical webhook/vendor/service identity is unauthenticated;
- untrusted input can cause unrestricted network/file/shell/tool access;
- data retention/deletion/residency obligations cannot be met;
- critical vulnerability/control failure is known and unmitigated.

### Operations and change

- critical service has no owner/on-call/escalation;
- no user-journey telemetry can detect major failure/correctness issue;
- deploy/migration has no compatibility and rollback/roll-forward path;
- alert/runbook/restore/failover claim has no validation owner;
- system cannot stay bounded under overload.

### AI/agent systems

- no representative quality/safety evaluation;
- model output alone authorizes high-impact action;
- agent can expand its own permissions from untrusted text;
- tool inputs/outputs/actions are not deterministically validated;
- agent has unbounded steps, tokens, cost, retries, or side effects;
- retrieval/memory lacks tenant/ACL isolation;
- sensitive provider retention/use is unknown;
- model/prompt/index version cannot be identified or rolled back.

## 4. Evidence Levels

Tag findings:

- **E0 — assertion:** no supporting evidence;
- **E1 — design:** documented mechanism and owner;
- **E2 — static proof:** code/config/schema/contract/test exists;
- **E3 — environment proof:** integration/load/security/restore experiment passed;
- **E4 — production proof:** measured SLI, drill, or incident evidence under representative conditions.

Critical claims should target E3 before launch and E4 after launch where feasible.

## 5. Review Report Template

```markdown
# Architecture Review

## Verdict
- Score: __ / 100
- Rating: __
- Critical gates open: __
- Launch recommendation: pass / conditional / block

## Highest-Risk Findings
| ID | Severity | Gate/category | Evidence | Impact | Recommendation | Owner | Due |

## Score Breakdown
| Category | Earned | Max | Evidence |

## Assumption Register
| Assumption | Confidence | Design impact | Validation | Owner |

## Decision Challenges
| Decision | Alternative | Why selected | Reversal trigger |

## Required Validation
| Test/drill | Claim tested | Pass condition | Owner | When |
```

## 6. Review Conduct

- review the intended requirements before evaluating implementation;
- challenge claims, not people;
- preserve working choices and avoid novelty bias;
- separate “wrong” from “different trade-off”;
- rank by user/business risk and reversibility;
- require evidence proportionate to impact;
- do not waive a critical issue through point arithmetic;
- record accepted risk and authority explicitly.
