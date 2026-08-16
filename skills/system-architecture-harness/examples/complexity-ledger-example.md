# Complexity Ledger Example: Modular Monolith or Services?

> Calibration example only. The order platform, requirements, and observations below
> are fictional assumptions chosen to demonstrate the method. They are not empirical
> evidence and contain no universal architecture score.

This example uses the [`Complexity Ledger template`](../assets/complexity-ledger-template.md)
and the [`evidence and complexity reference`](../references/15-evidence-complexity-and-research.md).

## Decision context

A six-person team is designing a regional order and inventory platform. The assumed
launch requirements are:

- reserve finite stock and create an order atomically;
- return a durable, idempotent result after a client retry;
- sustain an assumed peak of 2,000 create-order requests per second for a bounded burst;
- publish notifications and analytics asynchronously, with a declared lag objective;
- operate within one region initially, with a tested recovery path;
- keep tenant authorization, audit, and data ownership explicit.

The team has not demonstrated a need for independently deployed services. The decision
is whether to start with a modular monolith or introduce service boundaries now.

## Dimensional comparison

| Dimension | Modular monolith | Independently deployed services | Evidence needed or condition |
|---|---|---|---|
| Requirement and capability fit | Can keep order, reservation, idempotency, and audit in one transaction boundary; async side effects can use an outbox | Can provide separate deployment, scaling, or fault boundaries when those capabilities are required | Confirm the atomicity, lag, recovery, and workload requirements; prove any need for independence |
| Concepts, state, and protocols | In-process module contracts, one authoritative store, one deployable | Network APIs/events, service identities, ownership records, schema compatibility, retries, and cross-boundary state | Inventory every new state and protocol before extraction |
| Transaction and consistency behavior | Local transaction can enforce the assumed stock and idempotency invariants | Requires co-location, a distributed protocol, or an explicit workflow with compensation and reconciliation | Run invariant and duplicate tests against the chosen boundary |
| Runtime distribution and performance | Fewer network hops on the critical path; capacity still requires a representative load test | Adds network hops and independently scalable units; benefits only if measured isolation matters | Measure tail latency, saturation, dependency quotas, and burst recovery |
| Failure modes and blast radius | Process/deploy failure can affect several modules; distributed surface is smaller | Partial failure, timeout, duplicate, reorder, and version-skew behavior become fundamental | Inject process, network, datastore, and deployment faults; record containment |
| Deployment and ownership | One release train, with module ownership and compatibility checks | Independent releases are possible, but each service needs a team, runbook, SLO, and escalation path | Show independent change cadence and accountable operators, not just a desired topology |
| Interface and observability burden | Module contracts and application telemetry are required; baseline coordination is lower | APIs/events, tracing, correlation, contract tests, and cross-service debugging are required | Count actual contracts and operational signals in a pilot or repository model |
| Security and privacy | One runtime trust boundary still needs action-, tenant-, and resource-level authorization | Adds workload identities, network trust boundaries, secrets, policy propagation, and cross-service audit | Threat-model each boundary and test tenant isolation end to end |
| Operations and knowledge | Fewer deployables and platform dependencies; module ownership still needs documentation | More deployables, dashboards, alerts, quotas, upgrades, and specialist knowledge | Confirm on-call capacity, recovery skills, and dependency ownership |
| Infrastructure and lifecycle cost | Lower baseline runtime and migration cost; shared scaling can create contention | Higher baseline tooling and runtime cost; may avoid waste if isolation is measured | Use a unit-cost model and workload-shaped capacity test; do not infer cost from fashion |
| Reversibility and migration | Can extract a stable module later if ownership and data contracts are prepared | Early boundaries can be expensive to consolidate, especially after data and contracts spread | Define source of truth, migration, rollback/roll-forward, and point of no return |
| Evidence status | Fits the stated assumptions; still requires load, recovery, and change-coupling validation | Independent deployment/scale/fault isolation are hypotheses, not established needs | Record source class, limitations, and next validation in the evidence map |

## Conditional decision

Under the stated assumptions, start with a modular monolith. Keep order, inventory,
idempotency, and audit in one authority; define module interfaces and ownership; use a
transactional outbox for asynchronous side effects. This recommendation follows the
requirements and current evidence, not a claim that a monolith is always simpler or
that services are always premature.

Reconsider extraction when measured evidence or an approved constraint shows that a
module needs independently governed deployment, materially different scaling, a
fault-containment boundary, a compliance boundary, or an ownership boundary that the
single deployable cannot safely provide. Record the condition and validation in an
[`ADR`](../assets/adr-template.md); do not replace it with a component-count target.

## Ledger entry: conditional service extraction

This entry records the burden that would be introduced if the evidence later justifies
independent services. The entry remains conditional until the validation signals exist.

| Ledger field | Entry |
|---|---|
| Decision / mechanism | Extract order or inventory into an independently deployed service only after a qualifying requirement is confirmed |
| Requirement / ASR / invariant / risk / constraint | Independent deployment, scale isolation, fault isolation, compliance, or ownership must be demonstrated as material; current atomic order/inventory invariants remain mandatory |
| Capability gained | A qualifying domain can be deployed, scaled, governed, or contained independently |
| Complexity introduced | Network calls, service lifecycle, API/event contracts, retries, timeouts, schema versions, distributed tracing, and reconciliation |
| New concepts, state, protocols, and components | Service identity, endpoint, contract version, inbox/outbox or workflow state, deadline policy, deployment unit, dashboards, and runbooks |
| Operational responsibility | Deploy, patch, monitor, secure, back up, restore, page, and rehearse each service and its dependencies |
| Failure modes | Timeouts, partial success, duplicate or reordered messages, stale reads, contract skew, and larger diagnostic paths |
| Knowledge requirement | Distributed failure, API compatibility, identity, tracing, replay, migration, and service-specific operations |
| Dependency effect | Adds runtime network and identity dependencies plus build, platform, and organizational coordination |
| Performance effect | May reduce contention or isolate load; may add hops, serialization, queue lag, and tail latency |
| Security/privacy effect | Adds trust boundaries, credentials, authorization propagation, audit joins, and possible data copies |
| Cost | Additional runtime, telemetry, support, testing, migration, and on-call work; amount requires a measured model |
| Reversibility | Extraction can be reversed only while source-of-truth, contracts, and compatibility windows remain recoverable |
| Expected lifetime | Strategic only if the qualifying boundary is durable; otherwise transitional and subject to removal review |
| Evidence | Current evidence is an assumption; require change-coupling, load, ownership, fault, compliance, or cost evidence that matches the trigger |
| Validation | Compare equivalent flows, run invariant/contract/load/fault tests, rehearse recovery, and review operational ownership |
| Validation trigger | The service fails a required invariant, latency/recovery/operability condition, or does not improve the named capability |
| Removal / review trigger | The independent boundary no longer reduces measured coupling or isolation burden, or its owner/cost cannot be sustained |
| Owner / review date | Architecture owner with Order and Inventory leads; review after the first representative load and change-coupling study |

## Ledger entry: transactional outbox

The selected modular monolith still adds a protocol and durable state for asynchronous
notifications and analytics. It therefore gets its own ledger entry rather than being
hidden inside the service-shape decision.

| Ledger field | Entry |
|---|---|
| Decision / mechanism | Record an integration event in the same transaction as the authoritative order change, then relay it asynchronously |
| Requirement / ASR / invariant / risk / constraint | Preserve the committed order as the source of truth while allowing downstream side effects to tolerate bounded lag and client/relay failure |
| Capability gained | Durable publication intent, replay, consumer isolation, and asynchronous fan-out without making notification delivery part of order acceptance |
| Complexity introduced | Outbox rows and lifecycle, relay leases/cursors, event identity and schema, broker delivery, consumer deduplication, retention, and reconciliation |
| New concepts, state, protocols, and components | Pending/published/failed handling, event envelope, ordering key, relay worker, broker topic, consumer inbox or dedupe record, replay and quarantine path |
| Operational responsibility | Order team owns row growth, relay health, oldest-event age, retry policy, replay, quarantine, schema compatibility, and runbooks; platform owns broker operations |
| Failure modes | Transaction rollback, relay crash, broker outage, duplicates, reordering, poison events, lag growth, and exhausted retention; repair by bounded retry, replay, quarantine, or source reconciliation |
| Knowledge requirement | Transaction boundaries, at-least-once effects, idempotent consumers, event evolution, backpressure, replay, and external-side-effect reconciliation |
| Dependency effect | Adds a relay runtime and broker dependency while retaining the order database as authority; consumers depend on event contracts rather than tables |
| Performance effect | Adds an outbox write and index work to the local transaction; shifts delivery to an asynchronous path with measurable lag, storage, and drain-rate limits |
| Security/privacy effect | Requires broker and worker identities, tenant-scoped authorization, payload minimization, replay access control, and secret/PII redaction |
| Cost | Additional storage, relay capacity, broker retention, telemetry, replay testing, and operator support; amount requires a measured model |
| Reversibility | Remove or replace only after consumers have a compatible source or migration path and retained events are reconciled; authoritative order data remains recoverable |
| Expected lifetime | Strategic while downstream integrations are asynchronous; review if there are no durable consumers or a different integration protocol is approved |
| Evidence | The asynchronous-lag assumption and need to avoid an uncoordinated dual write are design constraints; verify delivery and recovery behavior in a representative environment |
| Validation | Kill the relay, interrupt the broker, duplicate/reorder deliveries, inject poison events, replay retained rows, and verify no committed event is lost and consumers converge |
| Validation trigger | Any unexplained loss, unbounded outbox age/storage, unsafe replay, non-idempotent effect, or lag beyond the declared objective |
| Removal / review trigger | No remaining consumer needs durable asynchronous delivery, or measured relay/broker burden exceeds the capability gained and a safe replacement is validated |
| Owner / review date | Order team with platform support; review after the first outage/replay drill and at the integration-contract review |

## Validation plan before changing the recommendation

1. Run a representative load test for the assumed burst and record units, tail latency,
   saturation, and recovery from overload.
2. Exercise duplicate requests, reservation conflicts, timeouts, outbox replay, and
   datastore failure. Verify invariants and reconciliation, not only response codes.
3. Inspect repository or prototype change history for modules that change together,
   then compare the observed coupling with the proposed service boundary.
4. Rehearse deployment, rollback/roll-forward, tenant authorization, restore, and
   operator escalation for each candidate boundary.
5. Update the evidence map and ledger with observed results, limitations, and a
   conditional ADR decision. If a material gate remains unresolved, keep the boundary
   deferred and state the unknown.

The normal workflow and gates in
[`01-workflow-and-decision-gates.md`](../references/01-workflow-and-decision-gates.md)
remain authoritative for the final architecture decision.
