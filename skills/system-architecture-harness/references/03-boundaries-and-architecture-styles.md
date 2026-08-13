# Boundaries and Architecture Styles

Choose boundaries and topology from domain integrity, ownership, deployment, scaling, failure, security, and lifecycle needs—not fashion.

## 1. Start with Context

Identify:

- people and roles;
- external systems and vendors;
- system in scope;
- trust and regulatory boundaries;
- upstream/downstream contracts;
- control plane and data plane;
- online, offline, batch, and operator journeys.

A context diagram must be understandable without technology knowledge. A container/runtime view then shows major applications, services, data stores, queues/topics, protocols, and responsibilities.

## 2. Domain and Capability Boundaries

For each candidate boundary, ask:

- What business capability and vocabulary does it own?
- Which invariants must be atomic inside it?
- Which data is authoritative here?
- Who owns changes and production outcomes?
- Does it change at a different rate?
- Does it need independent scale, availability, security, or compliance?
- Can consumers use a stable contract without knowing internals?
- Can the boundary fail or deploy without corrupting another capability?

Avoid boundaries around technical layers such as “controllers service,” “database service,” or “utilities service” unless they are true platform capabilities.

## 3. Architecture Style Decision Table

| Style | Use when | Costs and cautions |
|---|---|---|
| **Layered modular monolith** | small/medium team, shared transaction needs, fast delivery, boundaries can be enforced in code | requires module discipline; one deploy/runtime blast radius |
| **Service-oriented/microservices** | independent teams/releases, different scaling/failure/security needs, mature operations, clear domain ownership | distributed consistency, network failures, contract evolution, observability, platform cost |
| **Event-driven** | temporal decoupling, asynchronous side effects, replay, integration fan-out, burst absorption | eventual consistency, duplicates, ordering, schema governance, replay safety |
| **Serverless/event functions** | irregular workloads, rapid integration, managed operations, short stateless tasks | cold starts, limits, observability, local testing, lock-in, cost at sustained load |
| **Pipeline/dataflow** | staged transformation, batch/stream processing, independently scalable operators | lineage, checkpointing, backpressure, state, late data, replay |
| **Actor model** | many independent stateful entities, serialized per-entity operations, real-time sessions | placement, passivation, persistence, cross-actor transactions, runtime dependence |
| **CQRS** | read and write models have materially different workloads/semantics | projection lag, duplication, replay/migration complexity |
| **Event sourcing** | immutable history and deterministic replay are core requirements | event evolution, privacy/deletion, debugging, projection rebuild, operational expertise |
| **Hexagonal/ports-and-adapters** | domain logic must remain independent of transports/vendors/storage | abstraction overhead if every dependency is generalized prematurely |
| **Edge/offline-first** | latency, availability, bandwidth, device operation, or residency requires local execution | synchronization, conflict, security, rollout, fleet management |
| **Hybrid** | distinct subsystems have genuinely different ASRs | integration and ownership must remain explicit |

## 4. Modular Monolith as Default Starting Point

A modular monolith is not an unstructured monolith. Require:

- capability-oriented modules;
- explicit public interfaces;
- private data access by module;
- dependency direction rules;
- no cyclic module dependencies;
- module-level tests and ownership;
- transactional boundaries aligned to invariants;
- events/interfaces that can become extraction seams;
- one deployable until independent deployment is justified.

### Extract a service only when evidence shows one or more:

- independent team ownership is blocked;
- release cadence or deployment risk must be isolated;
- workload requires independent scaling or specialized runtime;
- failure blast radius must be isolated;
- security/compliance boundary must be stronger;
- domain model and data ownership are stable enough;
- technology constraint cannot be satisfied in-process;
- acquisition/vendor boundary or external product requires it.

Do not extract merely because a module is large. First improve its cohesion and interface.

## 5. Microservice Boundary Contract

Every service must have:

- one clear capability and accountable owner;
- authoritative data and invariant scope;
- stable synchronous and/or asynchronous contracts;
- independent build, deploy, rollback, and observability;
- dependency and latency budget;
- failure/degraded behavior;
- backward compatibility and deprecation policy;
- operational SLO and runbook;
- tenant/security model;
- test strategy and local development path.

### Shared database warning

Multiple services writing the same schema/table usually means the boundary is not independent. Accept only as a documented migration state with ownership, access controls, and an exit plan.

### Distributed monolith symptoms

- services must deploy together;
- synchronous request chain spans many services for every operation;
- shared database tables;
- cyclic service calls;
- changes require coordinated releases;
- no independent SLO or owner;
- local development requires the entire estate;
- retries and timeouts are inconsistent;
- one service knows another’s internal schema.

## 6. Control Plane vs Data Plane

Separate when different ASRs apply.

### Control plane

- configuration, policy, provisioning, metadata, orchestration;
- lower throughput but strong audit and authorization;
- can often tolerate higher latency;
- must not casually become a dependency on every data request.

### Data plane

- high-volume user/data traffic;
- strict latency and availability;
- minimal work on critical path;
- cached/snapshotted configuration where safe;
- bounded behavior during control-plane outage.

Define configuration propagation, versioning, rollback, and stale policy.

## 7. Synchronous vs Asynchronous Boundaries

Use synchronous interaction when:

- caller needs an immediate answer to continue;
- operation is short and dependency availability is acceptable;
- consistency requires a single transaction boundary or explicit immediate decision;
- user needs direct validation.

Use asynchronous interaction when:

- work can complete later;
- burst absorption or independent scaling is needed;
- side effects can be decoupled;
- fan-out is large;
- replay/audit is useful;
- dependency outage should not block acceptance.

Asynchrony does not remove coupling; it changes coupling to schema, ordering, delivery, and time.

## 8. Dependency Direction

Prefer:

- stable domain policies depend on abstractions, not infrastructure details;
- high-level capabilities do not import lower-level implementation internals;
- shared libraries remain small and stable;
- cross-domain changes go through contracts;
- platform capabilities provide paved roads without owning product semantics.

Avoid a universal “common” package containing mutable business models; it creates lockstep releases.

## 9. Multi-Tenancy Models

| Model | Benefits | Risks/use |
|---|---|---|
| Shared app + shared schema with tenant key | efficient and simple at scale | strongest need for end-to-end tenant enforcement and noisy-neighbor controls |
| Shared app + schema/database per tenant | better isolation/customization | migrations, connections, operational count, cost |
| Dedicated stack per tenant | strongest isolation/compliance | high cost and fleet-management complexity |
| Hybrid tiers | match isolation to tenant/risk | routing, policy, data movement, tier transitions |

Always define:

- tenant identity source and propagation;
- authorization and row/object isolation;
- encryption/key model;
- resource quotas and noisy-neighbor protection;
- tenant-specific backup/export/delete;
- per-tenant observability without leaking data;
- migration between tenancy tiers.

## 10. Build vs Buy

Evaluate:

- strategic differentiation;
- required correctness/security/compliance;
- integration and customization;
- availability/support/SLA and incident transparency;
- quotas, latency, geography, data use, and exit/export;
- total cost including engineers and on-call;
- lock-in and replacement path;
- vendor concentration and business continuity;
- contract and data-retention terms.

A managed service reduces some operational work; it does not transfer responsibility for system semantics, data lifecycle, access control, or recovery.

## 11. Team and Ownership Topology

Architecture must match the organization that operates it.

For each capability:

- one team owns build and run outcomes;
- ownership boundaries minimize handoffs on critical journeys;
- platform teams provide reusable capabilities, not ticket queues;
- cognitive load fits team size and expertise;
- service count and on-call burden are sustainable;
- dependencies have named owners and escalation paths;
- architecture records are reviewed with affected teams.

## 12. Boundary Review Questions

- Can the component be described in one sentence?
- Is its API smaller and more stable than its internals?
- Does it own data rather than merely proxy it?
- Which invariants remain inside the boundary?
- What breaks when it is unavailable?
- Can it be tested and deployed independently?
- Is the owner accountable for production behavior?
- Does the boundary reduce or increase coordination?
- Could an in-process module solve the same problem with lower cost?
- What evidence triggers splitting or merging it later?
