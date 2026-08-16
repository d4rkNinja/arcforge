# AI Production Readiness Checklist

Use this checklist as a release artifact. Mark each item **Pass**, **Blocked**, or **Not applicable**, and attach evidence or an owner and due date. A weighted score cannot override a blocked critical item.

## Task and value

- [ ] Task contract, users, prohibited outcomes, and consequence class are explicit.
- [ ] Strongest practical deterministic or single-agent baseline is recorded.
- [ ] Candidate value is measured against that baseline on repeated representative trials.
- [ ] Multi-agent topology, if used, has evidence of material benefit after latency, cost, and coordination overhead.
- [ ] Multi-agent trials explicitly vary prompt, model/routing, coordination pattern, and shared-state policy against the strongest single-agent baseline.
- [ ] Each topology has finite depth, worker, turn, tool, token, duration, retry, spend, wait-cycle, cancellation, and orphan-work controls.
- [ ] Per-topology results include task success, overhead, latency, cost, reliability, disagreement, and robustness across model, prompt, and topology versions.

## State and consistency

- [ ] State is classified as authoritative, derived, ephemeral, and sensitive where applicable.
- [ ] Every invariant has an owner and transaction or concurrency boundary.
- [ ] Unknown remote outcomes reconcile by stable operation ID before retry.
- [ ] Side effects define idempotency scope, lifetime, duplicate result, and partial-failure repair.
- [ ] Derived indexes, caches, embeddings, and summaries have divergence checks and tested rebuild paths.

## Queues, caches, and capacity

- [ ] Delivery, duplicate, replay, ordering, poison-message, and dead-letter semantics are explicit.
- [ ] Backpressure has admission, throttling, shedding, lag, and backlog-drain controls.
- [ ] State-to-message publication avoids unsafe dual writes.
- [ ] Cache origin, full identity, TTL, invalidation, staleness, poisoning, stampede, and cold-start behavior are tested.
- [ ] AI cache identity includes tenant/permission, purpose/task, model, prompt, policy, tool, and data/index revisions as applicable.

## Identity, tools, and isolation

- [ ] Acting identity and tenant propagate through queries, retrieval, caches, queues, files, analytics, traces, approvals, and admin paths.
- [ ] Tool authorization is deterministic at resource and action boundaries.
- [ ] Delegated authority is attenuated; per-task credentials are scoped, short-lived, auditable, and revocable.
- [ ] Generic execution and hostile parsers use isolated workers with default-deny egress and CPU, memory, process, disk, time, input, and output limits.
- [ ] Consequential actions show final details to the required approver and preserve separation of duties.

## Gateways and supply chain

- [ ] Model/tool gateways have no unsafe privileged bypass and define degraded modes, quotas, timeouts, semantic fallback, and kill controls.
- [ ] Code, dependency, image, model, prompt, parser, adapter, embedding, eval, and tool-contract provenance is recoverable.
- [ ] Critical artifacts are pinned or compatibility-bounded, integrity checked where justified, revocable, and rollbackable.
- [ ] Provider data use, retention, region, version drift, deprecation, and exit path are known.

## Memory and retrieval

- [ ] Retrieved content and tool output remain untrusted data with source/ACL provenance.
- [ ] Protected content is authorized before entering context.
- [ ] Model summaries are non-authoritative and retain source IDs/revisions, confidence, conflicts, expiry, correction, deletion, and rebuild semantics.
- [ ] Memory writes define subject, tenant, source, type, confidence, retention, correction, and deletion.

## Orchestration and liveness

- [ ] Worker/dependency graph and single owner for shared writes are explicit.
- [ ] Depth, workers, turns, calls, tokens, time, cost, retries, and queue sizes have hard limits.
- [ ] Progress, completion, blocked, cancellation, and timeout predicates are observable.
- [ ] Wait cycles, orphaned work, duplicate work, stale leases, and replay are detected and repaired.
- [ ] Checkpoints cannot replay irreversible effects.

## Recovery, change, and evidence

- [ ] RPO/RTO are defined and a restoration exercise verifies data, keys, credentials, schemas, and dependency order.
- [ ] Mixed-version code/schema/config/model/prompt/policy/tool operation is defined for rollout.
- [ ] Canary, rollback limits, forward repair, backfill/rebuild checkpoints, and cleanup criteria are tested.
- [ ] Traces reconstruct request, tenant, versions, evidence, policy, approvals, effects, unknown outcomes, latency, and cost without leaking protected data.
- [ ] Runbooks, alert owners, manual/read-only modes, reconciliation, and kill switches are exercised.

## Critical risk floors

- [ ] No critical security, privacy, tenant-isolation, invariant, unauthorized-action, or severe-correctness floor fails.
- [ ] Engagement, business value, model confidence, or aggregate quality is not used to waive a floor.
- [ ] Residual unknowns name an owner, validation method, deadline, and release consequence.
