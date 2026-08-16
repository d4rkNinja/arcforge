# Complexity Ledger

Use one entry for each architectural mechanism or boundary that adds a process,
network hop, datastore, queue, control plane, protocol, state machine, trust boundary,
deployment unit, or specialist operating practice. Keep the dimensions separate; do
not convert this ledger into a universal numeric score.

Use with the
[`evidence and complexity reference`](../references/15-evidence-complexity-and-research.md),
the [`ADR template`](adr-template.md), and the
[`failure-mode template`](failure-mode-template.md).

## Decision context

- Decision / mechanism: <what is being added, changed, or deliberately deferred>
- Requirement / ASR / invariant / risk / constraint: <IDs and measurable need>
- Capability gained: <what becomes possible or materially better>
- Scope and affected journey: <where this applies and who is affected>
- Owner: <accountable team or person>
- Expected lifetime: <temporary / transitional / strategic; state the horizon>

## Complexity dimensions

| Dimension | Entry | Evidence or assumption | Owner / consequence |
|---|---|---|---|
| New concepts, state, protocols, and components | <new terms, states, transitions, interfaces, stores, workers, or deployment units> | <measured / confirmed / estimated / assumed; source> | <who explains and maintains them; consequence> |
| Operational responsibility | <deploy, monitor, back up, patch, access, recover, and runbook work> | <existing evidence or explicit estimate> | <service owner and on-call burden> |
| Failure modes and blast radius | <new partial failures, data loss/duplication, overload, or containment changes> | <failure analysis, drill, or assumption> | <owner, degraded behavior, and repair path> |
| Knowledge and coordination | <specialist skills, cognitive load, handoffs, team or approval dependencies> | <team evidence, change history, or assumption> | <training/coordination owner and consequence> |
| Dependency effect | <runtime, build-time, organizational, vendor, control-plane, or lock-in dependency> | <contract, manifest, measurement, or assumption> | <dependency owner, quota, exit path> |
| Performance and scale effect | <latency, throughput, resource, fan-out, queue, or capacity change> | <measurement, calculation with units, benchmark, or assumption> | <capacity owner, bottleneck, and overload behavior> |
| Security and privacy effect | <new trust boundary, privilege, attack surface, data flow, or retention obligation> | <threat analysis, policy, test, or assumption> | <security/privacy owner and control> |
| Cost and sustainability | <development, infrastructure, license, observability, support, energy, and migration cost> | <billing/measurement or labeled estimate with units> | <cost owner, budget signal, and lifecycle consequence> |
| Reversibility and migration | <what can be removed, how data/contracts move, and the point of no return> | <migration rehearsal, contract, or assumption> | <rollback/roll-forward owner and residual risk> |

## Evidence and validation

- Evidence supporting addition: <atomic claims, sources, measurements, incidents, or repository facts>
- Evidence classification and limitations: <source type, context, counter-evidence, and unknowns>
- Validation plan: <test, benchmark, repository analysis, fault injection, restore drill, review, or production metric>
- Validation pass condition: <observable result with units or explicit qualitative condition>
- Validation trigger: <observation showing the mechanism is insufficient, unsafe, or unnecessary>
- Removal / review trigger: <condition that starts simplification, migration, or scheduled reassessment>
- Review date or lifecycle checkpoint: <date or trigger>
- Related ADR / failure analysis / risk / fitness function: <links or IDs>

## Review outcome

- Observed capability: <what the system actually gained>
- Observed burden: <new work, failures, cost, or coordination actually seen>
- Decision status: <proposed / accepted / conditional / deprecated>
- Follow-up owner and date: <accountability>
