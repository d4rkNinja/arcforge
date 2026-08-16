# Fitness Gates, Incident Causality, and Metric Governance

Use this reference for production gates, post-incident structural reviews, and architecture fitness metrics. It adapts Sections 23.3, 27, 29–35 and Appendices B, C, and E of the supplied research paper into reviewer behavior.

## Contents

- Five-Gate Review
- Complexity Ledger Review
- Post-Incident Structural Review
- Metric Governance
- Review Completion Check

## Five-Gate Review

Run the gates in order because later evidence depends on earlier meaning. Do not give each gate an automatic weight or average a failed condition into unrelated strengths.

### Gate A — Problem and Fitness

Require problem, stakeholders, measurable behavior, constraints, quality scenarios, and unacceptable failure. Ask whether a reviewer can tell what success means without referring to technology brands.

### Gate B — State and Boundaries

Require the simplest viable option, state classification, invariants, ownership, communication semantics, consistency, and a named capability for every boundary. Ask whether authoritative and derived state, transaction scope, time, ordering, duplication, cancellation, and unknown outcomes are explicit.

### Gate C — Failure and Assurance

Require failure analysis, detection, recovery, threat model, privilege model, and tests aligned to logic, integration, concurrency, load, recovery, and adversarial input. Ask what happens when each dependency is slow, unavailable, duplicated, reordered, or compromised.

### Gate D — Delivery and Operation

Require compatible change for code, schema, configuration, and infrastructure; observable user outcomes and workflows; bounded capacity; owner/on-call/runbooks; backup restore; and rollback or forward repair. Ask whether a capable operator can deploy, diagnose, and restore the system without its original authors.

### Gate E — Economics, Complexity, and Evolution

Require total lifecycle cost, a Complexity Ledger entry, compatibility and migration paths, reversibility, expected lifetime, owner, review date, and evidence-based validation trigger. Ask whether the measurable capability gained justifies all introduced obligations under uncertainty.

## Complexity Ledger Review

Inspect every field rather than accepting “complexity considered”:

| Area | Reviewer question |
|---|---|
| Decision and requirement | What mechanism changes, and which measurable requirement necessitates it? |
| Capability and alternatives | What becomes materially better, and what simpler options were considered? |
| Introduced complexity | Which concepts, states, protocols, configurations, and dependencies now exist? |
| Operational responsibility | What must be deployed, monitored, patched, backed up, restored, and retired? |
| Failure modes | What can fail now that could not fail before, including correlated failure and recovery load? |
| Knowledge | Which skills must be acquired and retained, and where is knowledge concentrated? |
| Security | What privileges, attack surfaces, data movement, identities, or trust boundaries are added? |
| Performance | What changes in latency, throughput, memory, storage, network, and capacity limits? |
| Cost | What build, runtime, license, support, incident, coordination, and migration costs arise? |
| Reversibility | What exit path, data portability, compatibility, and migration difficulty exist? |
| Lifetime | Is the mechanism transitional, tactical, or strategic; when is temporary machinery deleted? |
| Evidence and trigger | Which measurements, experiments, sources, assumptions, and observations could reverse the decision? |
| Accountability | Who reviews the decision, and when? |

Reject invented universal complexity points. Compare vectors and changes over time. A mechanism may reduce code complexity while increasing state, distribution, operational, configuration, security, or organizational complexity.

## Post-Incident Structural Review

Build this chain from evidence:

`architecture decision → hidden dependency → initiating trigger → propagation mechanism → blast radius → detection → recovery constraints → structural corrective action`

For every link, cite an incident timestamp, trace, change record, configuration, dependency map, runbook action, or explicit inference.

### Separate trigger from enabling conditions

- **Trigger:** the event that initiated the incident, such as a credential deletion, deployment, dependency failure, load spike, or operator command.
- **Enabling conditions:** architectural properties that allowed propagation or delayed containment, such as shared critical dependencies, weak configuration controls, retry amplification, incomplete isolation, accumulated state, absent semantic detection, insufficient rollback, or recovery that added load.

Correct the enabling conditions. Training, replacing a person, or reverting one command does not prevent a different trigger from exploiting the same structure.

### Structural questions

- Which prior decision created or accepted the dependency?
- Why was the dependency hidden from topology, telemetry, ownership, or recovery plans?
- Which isolation boundary failed or never existed?
- How did retries, queues, caches, control planes, or recovery work amplify impact?
- Which user-visible or semantic signal detected the problem, and what was missed?
- What constrained rollback, failover, reconciliation, or restoration?
- Which correction changes dependency, isolation, rollout, boundedness, detection, or recovery semantics?
- What validation proves that correction, and what recurrence signal remains?

Do not force a single root cause when multiple enabling conditions interacted. Distinguish verified causal links from plausible contributors and unknowns.

## Metric Governance

Architecture metrics are diagnostic signals, not an architecture score. Prefer vectors and within-system trends interpreted alongside domain and organizational change.

For every metric record:

| Field | Required content |
|---|---|
| Name, definition, and unit | exact numerator/denominator, population, window, aggregation, and unit |
| Data source and quality | instrument, coverage, freshness, missingness, bias, and validation |
| Intended decision | specific action or question the metric informs |
| Known confounders | domain change, incident mix, staffing, seasonality, migration, instrumentation change |
| Gaming risk | behavior that improves the number while degrading the system |
| Owner | accountable interpreter and maintainer |
| Review and retirement | review cadence, invalidation trigger, and removal date/condition |

Use multiple signal families where relevant:

- **Structural:** dependency cycles/depth, fan-in/fan-out, propagation cost, change coupling, ownership fragmentation, smell trends.
- **Delivery:** lead time, deployment frequency, deployment rework/change failure, recovery time, reliability.
- **Developer experience:** satisfaction, build/test time, onboarding, interruption, cognitive load, and ease of debugging.
- **Operational/economic:** SLO and error-budget state, incident severity/blast radius/recurrence, detection/mitigation/recovery/understanding time, restore success, queue age, replication lag, capacity headroom, unit cost, platform toil, and temporary compatibility-path age.

Never rank individual engineers with architecture, delivery, or developer-experience metrics. Do not turn a proxy into a quota. Retire a metric when its definition, boundary, decision use, or validity no longer holds.

## Review Completion Check

A formal review is complete only when:

- all applicable gates expose their evidence state and failed conditions;
- blockers remain separate and non-compensable;
- the Complexity Ledger is inspected or its absence is reported;
- source claims are distinguishable from reviewer inference;
- incident reviews identify enabling conditions and structural proof;
- metrics have governance metadata and no individual-ranking use; and
- every approval condition has an owner, proof, and review trigger.
