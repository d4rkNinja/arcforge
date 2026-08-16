# Architecture Specification

## Decision Summary

Use a modular monolith with PostgreSQL, Redis as a non-authoritative cache, and an outbox-backed event stream. The decision is reversible and reviewed at ten times current peak load.

## Scope and Evidence

Actors, tenants, critical journeys, system boundary, constraints, owners, and non-goals are explicit. Observed facts are separated from assumptions. Each unknown has an owner and validation experiment.

## Requirements, Workload, and Invariants

P99 write latency is 300 ms, availability is 99.95%, RTO is 30 minutes, and RPO is 5 minutes. Peak load is 2,000 requests per second, 500 writes per second, and 20,000 concurrent sessions. Money uses integer minor units. Inventory cannot become negative. Tenant data cannot cross boundaries.

## Options and Ownership

The proposal compares a modular monolith, microservices, and serverless functions across correctness, ownership, latency, blast radius, operability, migration, and cost. Order, payment, inventory, identity, and notification modules own their data and contracts. Server-side authorization is enforced at each boundary.

## Data and Workflows

PostgreSQL is authoritative. Transactions enforce order and inventory invariants. Optimistic concurrency uses version columns. Redis has TTL, invalidation, stampede protection, and safe miss behavior. Database and broker writes use a transactional outbox and idempotent consumers. API and event contracts define validation, authorization, errors, deadlines, quotas, versioning, delivery, ordering, replay, and dead-letter handling.

## Failure, Recovery, and Operations

Remote calls have deadlines and bounded retries with backoff, jitter, retry budgets, and degraded behavior. Queues and concurrency are bounded. The failure matrix covers infrastructure, dependency, data-corruption, deployment, and operator failures. SLOs, telemetry, ownership, runbooks, restore drills, game days, canaries, compatibility windows, reconciliation, rollback, and roll-forward are defined with validation owners.

## Security and Cost

The threat model covers identity, least privilege, tenant authorization, encryption, secrets, audit, SSRF, injection, dependency trust, privacy lifecycle, abuse, and incident response. Unit cost and dominant compute, storage, egress, queue, and observability costs are modeled across growth scenarios.
