# Bounded Multi-Tenant Agent Platform — Example

## Task and evidence gate

The platform researches a tenant's support case, drafts a resolution, and may propose a narrowly scoped account action. The strongest single-agent baseline uses the same retrieval and typed tools. A supervisor with two workers is admitted only if five repeated evaluation batches show a material task-success gain without crossing latency, cost, liveness, authorization, or tenant-isolation floors.

## State model

| State | Class | Owner and recovery |
|---|---|---|
| Customer/account facts and action records | authoritative, sensitive | tenant application database; transactional invariants and restore-tested backups |
| Source documents | authoritative, sensitive | document service with ACL and revision history |
| Search/vector index | derived | rebuilt by source revision; divergence and deletion checks |
| Case summary | derived, non-authoritative | rebuilt from recorded source IDs/revisions; conflicts remain explicit |
| Workflow checkpoint | durable task state | orchestrator store with versioned transitions and leases |
| Worker scratchpad | ephemeral | per-task namespace and TTL; never authorizes an action |

The account action and its outbox event commit in one transaction. A tool timeout returns an unknown outcome with `operation_id`; the orchestrator queries status before any retry. Tool execution uses the same operation ID to deduplicate concurrent and replayed attempts.

## Control and authority path

```text
tenant-authenticated request
→ policy/model gateway
→ bounded orchestrator
→ tenant-authorized retrieval + isolated workers
→ typed action proposal
→ deterministic resource authorization
→ final-details human approval
→ capability-scoped tool gateway
→ postcondition reconciliation + immutable evidence
```

The model gateway is the only provider path. Its cache key includes tenant and permission scope, purpose/task, model, prompt, policy, tool-contract, and document/index revisions. During a gateway outage the system queues read-only drafting within a bounded backlog or routes to manual handling; protected and consequential operations fail closed, and no service bypasses policy with direct provider credentials.

Each worker receives a short-lived credential bound to the task, tenant, allowed source IDs, specific tools, budget, and expiry. A worker cannot grant credentials, expand scope, or write authoritative customer state. Parser and browser work runs in disposable sandboxes with default-deny network access and CPU, memory, process, disk, time, input, and output limits.

## Topology and liveness

- Supervisor owns the task graph, shared contract, integration, and completion decision.
- Research and policy-evidence workers may run concurrently because their writes are isolated.
- Maximum topology: one supervisor, two workers, no nested delegation, eight tool calls, 45 seconds, and a fixed cost budget.
- Task and side-effect IDs expose duplicated work; leases and heartbeats expose abandoned work.
- The orchestrator records wait-for edges and fails a task to manual review when a cycle or no-progress deadline is detected.
- Completion requires cited evidence, typed output, independent deterministic checks, and no unresolved critical conflict.

## Queues, recovery, and rollout

The work queue is at-least-once with per-case ordering, idempotent consumers, poison-message quarantine, owned replay, admission limits, tenant-fair scheduling, and a measured backlog-drain target. Cold-cache tests prove the document origin can carry controlled miss traffic.

Recovery evidence demonstrates the declared RPO/RTO by restoring the authoritative database, keys, credential bindings, workflow state, and source documents before rebuilding indexes and summaries. Rollout supports mixed application, schema, prompt, model, policy, and tool-contract versions. Canary gates include forward-repair and rollback limits for already-executed actions.

## Release floors

The multi-agent candidate is compared with the single-agent baseline on correctness, grounding, tenant isolation, authorization, tool effects, liveness, latency, and cost. Any cross-tenant result, unauthorized action, lost invariant, unreconciled unknown outcome, or severe unsupported claim blocks release even if engagement or aggregate task score improves.
