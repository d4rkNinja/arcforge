# Contextual Evidence-Vector Review Example

This abbreviated example reviews `review-input-critical.md`. It demonstrates a vector-first decision in which blockers remain separate from evidence quality.

## Review Contract

- **Decision gated:** approve implementation of a multi-region commerce platform.
- **Critical journeys:** price calculation, order acceptance, event publication, authorization, and regional failover.
- **Unacceptable failure:** financial error, lost or duplicated side effects, cross-tenant access, divergent write authority, or unrecoverable release.
- **Evidence supplied:** one short proposal; no workload model, contracts, measurements, tests, Complexity Ledger, or recovery evidence.
- **Decision horizon:** implementation approval.

## Five-Gate Evidence Vector

| Gate | Dimension / protected condition | Evidence state | Evidence quality | Finding | Required proof |
|---|---|---|---|---|---|
| A | Requirement and workload fit | claimed | low | “because they scale” does not establish workload, bottleneck, or independent-deployment need | measurable scenarios, ranges, sensitivity, and alternative comparison |
| B | Financial/state authority | contradicted | high | floating-point prices and independent database/broker writes violate required correctness | exact money model, atomic invariants, coordinated publication, reconciliation |
| B | Multi-region write authority | claimed | low | active-active is named without routing, conflict, fencing, failback, or repair semantics | authority model and failure-tested protocol |
| C | Authorization and trust | contradicted | high | gateway-only authorization and implicit internal trust leave downstream boundaries exposed | service/data-boundary authorization and tenant tests |
| C | Messaging and overload | contradicted | high | retries and queues are explicitly unbounded | deadlines, attempts, capacity, backpressure, replay, and repair proof |
| D | Recovery and delivery | claimed | low | backups and direct deployment are named without restore, RTO/RPO, compatibility, rollback, or forward repair | representative restore and release rehearsal evidence |
| E | Lifecycle obligations | missing | none | no Complexity Ledger, cost, reversibility, lifetime, owner, or revision trigger is supplied | owned ledger and evidence-based review trigger |

## Critical Blockers

1. Floating-point financial values can violate exact monetary semantics.
2. Database and broker effects are dual-written without atomic coordination or repair.
3. Retry and queue paths are unbounded.
4. Authorization is not enforced at service and data boundaries.
5. Active-active writes lack authority, conflict, and fencing semantics.
6. Backup is presented without restore evidence.
7. Delivery lacks compatibility and rollback/roll-forward evidence.

These blockers are not compensated by strengths elsewhere. **Verdict: BLOCK.** Confidence is high for statements explicit in the proposal and low for unstated implementation details.

## Complexity Ledger Review

No ledger was supplied. The review cannot verify capability gained, alternatives, introduced concepts/state/protocol/configuration/dependencies, operational responsibility, new failure modes, knowledge needs, security/performance/cost effects, reversibility, expected lifetime, evidence, validation trigger, owner, or review date.

## Evidence Challenge

The proposal's “scales” and “multi-region” statements are author claims, not measured evidence. The reviewer's conclusion that write authority is unsafe is an inference from missing protocol detail; the gateway-only authorization and unbounded retry findings are verified contradictions because the proposal states those behaviors directly.

## Adversarial Pass

A second pass asks whether the review overemphasizes correctness and security. It does not change the result: workload fit, recovery, delivery, regional authority, and lifecycle evidence are independently inadequate, and critical blockers remain regardless of prioritization. No numeric summary is useful because it would add no decision information and could obscure the non-compensable failures.

## Smallest Approval Conditions

- Define exact monetary representation and atomic order invariants.
- Use transactional outbox/CDC or an explicit idempotent workflow with reconciliation.
- Bound queue capacity, attempts, deadlines, concurrency, and backlog behavior.
- Enforce actor, tenant, resource, and action authorization server-side.
- Select one write-authority model and define routing, fencing, conflict, failover, failback, and reconciliation.
- Supply representative restore, migration, release, workload, and failure evidence.
- Add an owned Complexity Ledger entry with reversal, lifetime, and validation triggers.
