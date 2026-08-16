# Ontology and Knowledge-Graph Model

The canonical topic set is organized into three primary layers. This prevents every concern from being treated as an isolated feature and makes reusable reasoning visible to AI coding agents.

## 1. Primitives

Primitives are reusable semantic and correctness mechanisms that appear in many systems: identifiers, time, precision, validation, errors, state machines, transactions, concurrency control, idempotency, consistency, ordering, data versioning, and schema evolution.

An implementation should import the reasoning from a primitive rather than reinvent it independently in authentication, payments, jobs, search, or any other subsystem.

## 2. Systems

Systems own domain state and lifecycle: identity, authentication, authorization, user accounts, multi-tenancy, APIs, files, search, queues, webhooks, realtime, integrations, architecture boundaries, clients, and AI execution.

A system paper describes ownership, state transitions, data model, contracts, failure recovery, and operations. It links to primitives for reusable mechanisms and to cross-cutting papers for release controls.

## 3. Cross-cutting concerns

Cross-cutting papers constrain many systems: security, privacy, abuse protection, resilience, logging, metrics, tracing, audit, testing, performance, scalability, deployment, disaster recovery, runbooks, and zero-downtime change.

These are not optional polish. They define whether a system remains safe and operable after the happy path.

## Primary classification versus relationships

Each paper has one primary `layer` for filesystem navigation and one `category`/domain profile for generation and review. A paper may still function in other layers. For example:

- **Idempotency** is a primitive but constrains APIs, jobs, messages, webhooks, and AI tools.
- **Authentication** is a system but depends on identity, randomness, cryptography, sessions, abuse protection, and audit.
- **Database migrations** are cross-version change mechanics and are linked from every storage-owning system.
- **Cross-Cutting Implementation Checklist** acts as a release gate across all layers.

## Edge semantics in `knowledge-graph.json`

Every paper lists related paper numbers. A relationship means at least one of:

1. the source paper depends on a mechanism defined by the target;
2. the source paper constrains the target's implementation;
3. the two papers share an ownership, state, consistency, security, or deployment boundary;
4. changes to one should trigger review of the other.

The graph is intentionally not a strict DAG. Production concerns are mutually constraining.

## Recommended traversal for an implementation request

```text
requested system paper
    -> identity/auth/authorization/tenant boundaries
    -> validation + identifiers + time + state machine
    -> constraints + transactions + concurrency + idempotency
    -> cache/queue/integration failure semantics
    -> security/privacy/abuse
    -> observability/audit/runbooks
    -> compatibility/migrations/deployment/rollback
    -> testing/performance/scalability
    -> paper 146 release checklist
```

## Editorial layer counts

- Primitives: 40
- Systems: 54
- Cross-cutting: 52
