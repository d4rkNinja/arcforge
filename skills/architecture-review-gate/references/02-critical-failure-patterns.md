# Critical Failure Patterns

## Correctness

### Floating-point money

Binary floating point cannot safely represent many decimal values. Use integer minor units or fixed-precision decimal with currency, scale, rounding, and overflow rules.

### Missing enforcement point

A stated invariant is not a control. Identify the exact transaction, constraint, conditional write, lock/version check, ledger rule, or single-writer boundary that enforces it under concurrency.

### Unsafe dual write

Writing the database and broker independently creates ambiguous partial success. Use a transactional outbox/CDC, idempotent state machine with reconciliation, or a justified distributed transaction.

### Exactly-once handwave

Broker delivery does not prove end-to-end effect exactly once. Define boundary, deduplication identity/lifetime, transaction, replay, consumer crash behavior, and proof.

## Boundedness

### Infinite retry or unlimited queue

Retries amplify outages; queues convert overload into delayed failure. Require maximum attempts/deadline, retry budget, capacity, admission, backpressure, expiry, DLQ/quarantine, and user behavior.

### Unbounded fan-out or concurrency

Calculate worst-case amplification and cap it per request, tenant, dependency, and process. Include cancellation and partial-result policy.

## Authority and isolation

### Cache as authority

A cache can be lost, stale, evicted, or partitioned. If it holds authority, the design must explicitly provide durability, consensus/transaction semantics, backup, recovery, and audit; otherwise make it derived.

### Gateway-only authorization

A gateway authenticates and filters broad access, but downstream services and data boundaries still enforce actor, tenant, resource, and action authorization.

### Internal equals trusted

Use workload identity, least privilege, authenticated/encrypted transport where required, scoped credentials, and service-side authorization. Network placement is context, not authority.

## Multi-region

Active-active writes require conflict semantics, ownership/routing, fencing, replication lag behavior, split-brain handling, failback, residency, and reconciliation. Without them, failover can produce divergent authority.

## Recovery

Backups without restore evidence are inventory, not recovery. Require retention/isolation, corruption scenario, access, restore steps, RTO/RPO measurement, dependency order, and reconciliation after recovery.

## Delivery

Irreversible schema/data changes need expand-migrate-contract, compatibility windows, backfill/reconciliation, cutover gates, and rollback or roll-forward. “Deploy directly” is not a release strategy.

## AI and agents

Block high-impact tool use when the model can choose arbitrary authority, arguments are untyped, prompt text is the only guardrail, memory crosses users/tenants, delegation is unbounded, eval gates are editable by the candidate, or no approval/audit/kill switch exists.
