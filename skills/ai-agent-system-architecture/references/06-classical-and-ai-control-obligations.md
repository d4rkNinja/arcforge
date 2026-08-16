# Classical and AI Control Obligations

Use this reference when an AI design includes model gateways, retrieval, memory, tools, queues, caches, multiple agents, multi-tenancy, or consequential actions. It translates the user-supplied paper's Sections 9.4, 10-12, 14.9, 16-17, 26, 32.9, 33.3, and Appendix D.4 into reviewable obligations. Section 26.6 and Section 33.3 describe multi-agent practices as emerging evidence; treat them as hypotheses to validate locally, not universal proof.

## State, invariants, and remote outcomes

Classify every state item before choosing storage:

| Class | Meaning | Required control |
|---|---|---|
| Authoritative | Owns business truth or an invariant | named owner, atomic boundary, concurrency rule, recovery path |
| Derived | Rebuilt or corrected from authoritative state | source revision, lag bound, rebuild and divergence check |
| Ephemeral | Safe to lose after a bounded interval | TTL, loss behavior, no hidden authority |
| Sensitive | Requires access and lifecycle controls | classification, minimization, retention, deletion, audit |

- State invariants name the authority that enforces them and the operations that must be atomic.
- A timeout after a remote write is an **unknown outcome**, not proof of failure. Reconcile by stable operation identifier before retrying.
- Side effects use idempotency keys whose scope, retention window, duplicate result, and concurrent behavior are explicit.
- Search indexes, embeddings, caches, summaries, and read models do not become accidental sources of truth.

## Queues, caches, recovery, and change

For each queue or log, define delivery scope, duplicate handling, ordering key, replay, poison-message ownership, lag limit, admission control, and backlog-drain behavior. A queue absorbs a burst but does not create capacity. Couple durable state changes and event publication through a transactional outbox, inbox, change-data capture, or an equivalent proven protocol; do not use an unsafe dual write.

For each cache, define origin authority, complete key, TTL, invalidation owner, stale behavior, poisoning boundary, stampede control, and cold-start origin capacity. An AI-result cache identity includes, where applicable:

```text
tenant + actor/permission scope + purpose/task + model + prompt + policy
+ tool-contract versions + authoritative data/index revisions
```

Define cache version migration, invalidation or purge, and controlled rebuild before changing any identity component.

Define RPO, RTO, restore authority, dependency order, key and credential recovery, and evidence from periodic restoration. A backup job succeeding is not recovery evidence.

Design code, schema, index, prompt, model, policy, tool, and configuration changes for mixed versions. State compatible read/write periods, staged rollout, backfill or rebuild checkpoints, rollback limits, forward repair, and cleanup criteria. Do not call rollback safe when durable writes or external effects cannot be reversed.

## Identity, tenancy, supply chain, and gateways

Propagate acting identity and tenant through authorization, database queries, retrieval filters, cache keys, files, queues, analytics, traces, approvals, and support/admin paths. Verify isolation before protected data enters model context.

Track provenance and pinning for code, packages, containers, models, prompts, adapters, parsers, embeddings, evaluation datasets, and tool contracts. Define signature or integrity checks where justified, vulnerability and poisoning response, revocation, compatible rollback, and provider/model exit paths.

Treat model and tool gateways as critical trust, privacy, availability, and cost boundaries. They require scoped credentials, policy mediation, quotas, timeouts, semantic fallback tests, audit, degraded modes, and blast-radius controls. Clients must not bypass the gateway to reach a provider or privileged tool with ambient authority. If required controls are unavailable, fail closed for protected or consequential operations and expose only a bounded read-only or manual path.

Run ingestion parsers, generated code, browser/file tools, and other hostile-input handlers in isolated workers with default-deny egress and explicit CPU, memory, process, disk, time, input, and output limits. Treat parser output as untrusted evidence.

## Memory and summaries

Store authoritative facts separately from model-produced memory. A summary is a rebuildable, non-authoritative view and carries:

- source identifiers and revisions;
- summarizer model/prompt version;
- creation time, tenant and subject scope, and expiry;
- confidence, uncertainty, and unresolved conflicts;
- correction, deletion, and rebuild behavior.

When sources conflict, preserve the conflict and apply an explicit authority policy. Do not let a newer or more confident summary silently replace a stronger source.

## Multi-agent value and authority gate

Begin with the strongest practical single-agent design using deterministic tools and the same task contract. Add multiple agents only when repeated trials show a material gain from independent decomposition, specialization, adversarial review, or fault diversity after accounting for coordination, repeated context, latency, and cost.

Vary prompt, routing, topology, coordination, and shared-state choices as explicit experimental factors rather than assuming a hierarchy is superior. Measure task success, coordination overhead, latency, cost, reliability, disagreement, and robustness across model, prompt, and topology versions.

Record for each topology:

- task and dependency graph, state owner, and write serialization;
- maximum workers, depth, turns, tool calls, tokens, duration, and spend;
- progress, completion, blocked, cancellation, and timeout predicates;
- wait-for relationships and detection/recovery for cycles or orphaned work;
- task and side-effect identifiers for duplicate-work detection and reconciliation;
- conflict resolution and an independent acceptance path.

Delegation attenuates authority: a worker receives only the subset of capabilities, resources, tenant scope, duration, and budget required for its unit of work. Use ephemeral per-task credentials bound to identity, audience, tenant, capability, expiry, and revocation. A delegate cannot redelegate broader authority or infer permission from natural-language content.

## Evaluation risk floors

Evaluate correctness, groundedness, authorization, tenant isolation, tool effects, trajectory, liveness, latency, cost, and recovery separately. Define deterministic risk floors for security, privacy, invariants, unauthorized actions, and severe factual errors. Business value, engagement, model-judge confidence, or a weighted aggregate cannot compensate for a failed floor.

Require a fixed comparison against the single-agent baseline, repeated trials, per-dimension results, severe-failure examples, disagreement analysis, and rollback thresholds. Multi-agent count is not an architecture-quality metric.
