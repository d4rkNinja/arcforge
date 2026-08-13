# Workflow and Decision Gates

This reference turns architecture work into an auditable control loop. It applies to greenfield design, reviews, migrations, scaling work, and incident-driven redesign.

## Contents

- 1. Evidence Hierarchy
- 2. Architecture Control Loop
- 3. Architecture Modes
- 4. Question Priority
- 5. Decision Record Contract
- 6. Mandatory Flow Clauses
- 7. Architecture Fitness Functions
- 8. Review Severity
- 9. Exit Criteria

## 1. Evidence Hierarchy

Prefer evidence in this order:

1. production measurements and incident evidence;
2. executable contracts, schemas, deployment manifests, and code;
3. current architecture records and runbooks;
4. stakeholder-confirmed requirements and constraints;
5. benchmark or proof-of-concept results from a representative environment;
6. calculations based on explicit assumptions;
7. analogies and general rules of thumb.

Never present an assumption as a measured fact. Label each material statement as **measured**, **confirmed**, **estimated**, or **assumed** when ambiguity could change a decision.

## 2. Architecture Control Loop

```text
Frame → Measure → Model correctness → Select boundaries → Design flows
     → Stress failures and abuse → Make operable → Compare alternatives
     → Validate → Record → Revisit on evidence
```

### Inputs

- business outcomes and user journeys;
- present architecture and codebase evidence;
- workload and growth projections;
- constraints: time, budget, people, vendors, geography, regulation;
- incidents, performance traces, cost data, and operational pain;
- lifecycle horizon and reversibility expectations.

### Outputs

- requirements and ASRs;
- calculations and uncertainty ranges;
- invariants and state machines;
- context/container/dynamic/deployment views;
- data, interface, and failure semantics;
- security and privacy threat model;
- SLOs, runbooks, deployment/migration strategy;
- cost model, alternatives, ADRs, risks, and validation evidence.

## 3. Architecture Modes

### Explore mode

Use when the problem is still ambiguous.

1. Restate the problem and current evidence.
2. Identify the 3–7 unknowns most likely to change the architecture.
3. Ask one question at a time when interactive.
4. When autonomous, create explicit scenarios instead of hiding assumptions.
5. Offer 2–3 coherent approaches, not a buffet of disconnected technologies.
6. Recommend the smallest approach that keeps a safe path to growth.

Exit when the user or stated assumptions establish enough ASRs to design.

### Design mode

Use for a new system or major capability.

1. Complete all phases in `SKILL.md`.
2. Produce the required output contract.
3. Identify the riskiest assumption.
4. Design the smallest vertical slice that tests it.
5. Record major decisions and reversal triggers.

### Review mode

Use for an existing design or implementation.

1. Establish the intended requirements before judging the design.
2. Inspect evidence; do not review only a diagram.
3. Reconstruct actual runtime and data flows.
4. Score each dimension with supporting evidence.
5. Separate correctness/security blockers from improvements.
6. Rank findings by risk reduction per unit effort.
7. Preserve good existing choices; avoid novelty-driven rewrites.

Output every finding as:

```text
ID | Severity | Evidence | Violated requirement/invariant | Failure mode
   | Recommendation | Alternative | Validation | Owner
```

### Scale mode

1. Establish the violated SLI or cost target.
2. Build a bottleneck tree: arrival rate, service time, concurrency, saturation, queueing, dependency limit.
3. Measure before replacing.
4. Optimize in this order unless evidence says otherwise:
   - remove unnecessary work;
   - fix algorithms and queries;
   - cache/precompute/batch/compress;
   - isolate hot paths and noisy neighbors;
   - vertically scale where economical;
   - horizontally scale stateless work;
   - partition state;
   - change architecture or storage engine.
5. Load-test each step against production-like distributions.

### Migrate mode

1. Document current state, target state, and every intermediate state.
2. Define compatibility between old and new readers/writers.
3. Choose migration pattern: expand/contract, strangler, shadow, dual-read, backfill, CDC, or controlled cutover.
4. Avoid uncontrolled dual writes.
5. Specify validation, reconciliation, traffic ramp, abort, rollback/roll-forward, and cleanup.
6. Define the point of no return before reaching it.

### Incident-driven mode

1. Describe user impact and violated SLO/invariant.
2. Reconstruct the timeline and contributing conditions.
3. Identify failed assumptions and weak containment boundaries.
4. Distinguish trigger from systemic causes.
5. Design controls that prevent recurrence or reduce blast radius.
6. Create a verification drill and operational owner.

## 4. Question Priority

Ask questions in descending architecture impact:

1. What outcome and journey are critical?
2. What can never be wrong or lost?
3. What load, geography, latency, availability, and growth are expected?
4. What data sensitivity, tenancy, residency, and regulatory constraints exist?
5. What existing systems, contracts, team boundaries, deadlines, and budgets constrain the solution?
6. What failure or cost is acceptable?
7. What future flexibility is actually funded or probable?

Avoid asking for low-impact preferences while high-impact unknowns remain.

## 5. Decision Record Contract

Every architecturally significant decision must include:

- **Context:** requirement, invariant, risk, or constraint.
- **Decision drivers:** ordered priorities.
- **Options:** at least two viable choices, including “do less” where applicable.
- **Decision:** what is selected and its scope.
- **Consequences:** benefits, costs, new failure modes, operational burden, lock-in.
- **Validation:** benchmark, test, SLO, review, or production metric.
- **Reversal trigger:** measurable condition that causes reconsideration.
- **Owner and date:** accountable person/team and review date.

Use `assets/adr-template.md`.

## 6. Mandatory Flow Clauses

### Scope and assumptions

- **IF** the source of truth is a repository or live system, **THEN** inspect it before proposing a target architecture.
- **IF** requirements conflict, **THEN** make the conflict visible and request/prioritize a business decision; do not silently average incompatible goals.
- **IF** a value is unknown, **THEN** use a range and sensitivity analysis rather than false precision.
- **IF** a proposed future requirement is not funded, scheduled, or plausible, **THEN** preserve an extension seam but do not build the full machinery.

### Complexity

- **IF** one process and one transactional store satisfy the ASRs, **THEN** prefer a modular monolith.
- **IF** a component adds a network hop, datastore, queue, or control plane, **THEN** name the specific ASR it satisfies and the operational owner.
- **IF** a pattern is introduced only because a large company uses it, **THEN** reject the argument until workload and constraints match.
- **IF** a decision is difficult to reverse, **THEN** demand stronger evidence and isolate it behind a stable contract.

### Data and correctness

- **IF** two records must change atomically, **THEN** co-locate them in one transaction boundary or explicitly justify a distributed protocol.
- **IF** state is derived, **THEN** preserve the durable facts or source data needed to rebuild it.
- **IF** eventual consistency is accepted, **THEN** state maximum staleness, user-visible behavior, convergence mechanism, and repair path.
- **IF** concurrent writes are possible, **THEN** define isolation, optimistic/pessimistic control, conflict detection, and retry behavior.
- **IF** data is sharded, **THEN** define routing, skew, resharding, cross-shard operations, and tenant isolation.

### Interfaces and workflows

- **IF** an operation creates or changes durable state, **THEN** define idempotency and replay behavior.
- **IF** an API returns collections, **THEN** define stable pagination, sorting, filters, limits, and consistency during pagination.
- **IF** a contract is consumed independently, **THEN** define compatibility rules, ownership, versioning, deprecation, and contract tests.
- **IF** events are used, **THEN** define schema evolution, producer/consumer ownership, event identity, ordering key, and retention.
- **IF** a webhook or callback closes a workflow, **THEN** authenticate it, deduplicate it, tolerate reordering, and reconcile missing callbacks.

### Reliability

- **IF** a dependency can fail slowly, **THEN** use explicit deadlines and isolate its resources.
- **IF** a retry can multiply load, **THEN** use bounded attempts, jitter, retry budgets, and load shedding.
- **IF** a queue absorbs spikes, **THEN** prove its bounded capacity and backlog drain time.
- **IF** leader failover can produce two writers, **THEN** use fencing or an equivalent authority mechanism.
- **IF** data can be corrupted, **THEN** design checksum/audit detection, isolated backups, point-in-time recovery, and reconciliation.
- **IF** a region can fail, **THEN** specify traffic steering, data topology, failover authority, RTO/RPO, and failback.

### Security and privacy

- **IF** a component crosses a trust boundary, **THEN** authenticate, authorize, validate, encrypt, rate-limit, and observe it as appropriate.
- **IF** tenants share infrastructure, **THEN** carry tenant context end-to-end and enforce it in data access—not only routing/UI.
- **IF** a user can reference an object identifier, **THEN** enforce object-level authorization on every request.
- **IF** sensitive data is not needed, **THEN** do not collect it; if collected, define retention, deletion, access, and audit.
- **IF** a vendor handles sensitive or critical data, **THEN** model contract, breach, residency, retention, availability, and exit risks.

### Operations and delivery

- **IF** a critical path has no SLI, **THEN** define one from the user perspective before setting alerts.
- **IF** an alert has no immediate or scheduled action, **THEN** remove or convert it to diagnostic logging.
- **IF** a schema change is not backward compatible, **THEN** use expand/contract or schedule coordinated downtime explicitly.
- **IF** rollback cannot undo a data change, **THEN** design roll-forward and reconciliation before rollout.
- **IF** a backup is claimed, **THEN** show successful restore evidence and restore duration.

### AI and agents

- **IF** model output affects rights, money, safety, identity, or irreversible actions, **THEN** add deterministic policy checks and human approval where risk requires it.
- **IF** untrusted text reaches a model with tools, **THEN** treat it as hostile instructions; separate data from authority and constrain tools.
- **IF** retrieval is used, **THEN** evaluate retrieval quality separately from generation quality.
- **IF** a model/provider can change behavior, **THEN** pin versions where possible, regression-test, monitor drift, and provide fallback.

## 7. Architecture Fitness Functions

Translate important claims into automated or rehearsed checks.

| Claim | Fitness function example |
|---|---|
| p99 API latency ≤ 250 ms | production SLI and representative load test fail above 250 ms |
| no cross-tenant reads | automated authorization tests plus policy/database isolation checks |
| duplicate payment cannot double-charge | idempotency property test and replay test against PSP sandbox |
| region loss RTO ≤ 15 minutes | quarterly failover game day records traffic restored within target |
| event contracts remain compatible | schema compatibility check in CI and consumer contract tests |
| queue remains bounded | alerts/load shedding at configured depth; drain-time test after burst |
| restore RPO ≤ 5 minutes | point-in-time restore drill verifies data gap |
| model task accuracy ≥ target | versioned evaluation dataset and CI/production evaluation gates |
| monthly cost per active tenant ≤ target | allocation tags plus unit-cost dashboard and budget alert |

## 8. Review Severity

| Severity | Meaning | Required action |
|---|---|---|
| **Critical** | Likely loss of funds/data, security breach, tenant escape, safety impact, or inability to recover | block launch/change until resolved or formally accepted by accountable authority |
| **High** | Material outage, severe scale/cost failure, correctness drift, or unowned critical dependency | remediation plan before launch; owner and date required |
| **Medium** | Operability, maintainability, moderate performance, or migration risk | scheduled remediation and validation |
| **Low** | Clarity, optimization, or future resilience improvement | backlog with rationale |
| **Observation** | Context or optional alternative | no action required |

## 9. Exit Criteria

Architecture work is ready for handoff only when:

- critical user journeys and ASRs are measurable;
- capacity calculations and uncertainty are visible;
- invariants, ownership, states, and consistency are explicit;
- critical flows include failure and recovery;
- security/privacy/abuse risks are modeled;
- SLOs, telemetry, ownership, rollout, rollback, and DR are defined;
- cost and organizational load are bounded;
- major alternatives and trade-offs are recorded;
- validation and implementation slices target the highest risks;
- no critical review gate is unresolved.
