# Model Serving and Economics

## Route by task, not prestige

Choose a model route from measured capability requirements: modality, reasoning, context, structured output reliability, tool use, safety, latency, region, availability, and cost. A larger model is not automatically the correct default.

## Gateway responsibilities

- versioned route policy;
- provider authentication and regional endpoint selection;
- request deadlines and cancellation;
- bounded retry with jitter for transient failures;
- quota and concurrency control;
- response schema validation;
- fallback compatibility and circuit breaking;
- prompt/model/cache version labels;
- token and cost accounting;
- redaction and provider data policy enforcement.

## Latency budget

Break end-to-end latency into queue, context assembly, retrieval, rerank, model first-token, model generation, tools, verification, and persistence. Optimize the dominant stage, not the most visible one.

Use streaming only when partial output is useful and cannot trigger unverified actions. Cancellation must propagate to model and tool calls.

## Cache classes

- exact deterministic response cache;
- semantic response cache;
- embedding cache;
- retrieval result cache;
- prompt prefix/provider cache;
- tool result cache.

For each, define key, tenant scope, source authority, TTL, invalidation, privacy, poisoning resistance, stale behavior, and cost benefit. Never share protected semantic cache entries across tenants without a proof-safe partition.

## Unit economics

Model cost per successful task:

```text
model input + model output + embeddings + reranking + tools
+ storage + observability + retries + human review + failed-task waste
```

Track distribution, not only average. Include long-tail prompts, repeated loops, fallback routes, and provider egress. Set per-request and per-tenant hard budgets, daily anomaly alerts, and a graceful response when budget is exhausted.

## Provider resilience

Document quota, region, data retention, incident behavior, rate-limit headers, model deprecation, version drift, and exit path. Test failover for semantic compatibility; an available but unsafe or lower-quality fallback is not resilience.
