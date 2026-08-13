# Architecture Specification

## Decision Summary
Use a modular monolith with PostgreSQL, Redis as a non-authoritative cache, and an outbox-backed event stream. The decision is reversible and is reviewed at 10x current peak load.

## Scope and Non-Goals
Actors, tenants, critical journeys, system boundary, constraints, decision owners, and non-goals are explicit.

## Facts, Assumptions, Unknowns, and Evidence
Observed facts are separated from assumptions. Each unknown has an owner and validation experiment.

## Requirements, ASRs, and Invariants
P99 write latency is 300 ms, availability is 99.95%, RTO is 30 minutes, RPO is 5 minutes. Money uses integer minor units. Inventory cannot become negative. Tenant data cannot cross boundaries.

## Capacity Model
Peak is 2,000 requests/s, 500 writes/s, 20,000 concurrent sessions, 4 KB average payload, 3 TB/year primary growth, 2x index overhead, and 3x replicated storage. Load tests validate 2x peak and backlog drain time.

## Options and Trade-offs
Compared modular monolith, microservices, and serverless functions on correctness, ownership, latency, blast radius, operability, migration, and cost. Modular monolith is chosen because independent deployment is not yet required.

## Boundaries and Ownership
Order, payment, inventory, identity, and notification modules own their data and contracts. Authorization is enforced at every server-side boundary.

## Data and Consistency
PostgreSQL is authoritative. Transactions enforce order and inventory invariants. Idempotency keys live for 24 hours. Optimistic concurrency uses version columns. Read replicas serve stale-tolerant reporting only. Redis has TTL, invalidation, stampede protection, and safe miss behavior.

## APIs, Events, and Workflows
APIs define validation, authn, authz, pagination, deadlines, error codes, quotas, and versioning. Events define schema owner, partition key, ordering scope, at-least-once delivery, deduplication, retry, DLQ, replay, and lag SLO. Database and broker writes use a transactional outbox and idempotent consumers.

## Failure, Overload, and Recovery
Every remote call has a deadline, bounded retry with exponential backoff and jitter, retry budget, circuit breaker, and fallback. Queues are bounded. Admission control, concurrency limits, load shedding, and graceful degradation prevent overload. Failure matrix covers process, host, zone, region, dependency, data corruption, certificate, deployment, and operator error.

## Security, Privacy, Tenancy, and Abuse
Threat model covers identity, least privilege, service identity, object and tenant authorization, encryption, KMS rotation, secrets, audit, SSRF, injection, replay, file upload, dependency trust, retention, deletion, residency, rate limiting, fraud, and incident response.

## Observability and Operations
SLIs, SLOs, error budget, logs, metrics, traces, correlation IDs, dashboards, symptom alerts, runbooks, ownership, capacity signals, queue lag, restore drills, and game days are defined.

## Delivery, Migration, and Rollback
Uses expand-migrate-contract schemas, backward-compatible APIs/events, canary release, feature flags, reconciliation, cutover criteria, rollback and roll-forward. Irreversible changes require backup and rehearsal.

## Cost and Sustainability
Unit cost is tracked per completed order. Dominant compute, storage, egress, queue, and observability costs are modeled at 1x, 10x, and 100x.

## ADRs, Risks, Review Triggers, and Validation
ADRs record alternatives and consequences. The risk register has owner, probability, impact, mitigation, trigger, and residual risk. Validation includes contract, integration, concurrency, load, soak, chaos, failover, restore, security, and migration rehearsal evidence.
