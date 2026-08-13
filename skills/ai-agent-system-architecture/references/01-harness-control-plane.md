# Harness Control Plane

## System boundary

Treat the harness as the policy-enforced runtime around one or more models. It owns context construction, tool exposure, state, budgets, approvals, verification, tracing, and termination. Models generate proposals inside that boundary.

## Required components

| Component | Owns | Must not delegate to model judgment alone |
|---|---|---|
| Request gateway | identity, tenant, quota, risk classification | authentication and tenant selection |
| Context assembler | instruction precedence, evidence packing, token allocation | authority classification of untrusted text |
| Policy engine | allowed models, data, tools, actions, approvals | final authorization |
| Model gateway | routing, versions, retry, timeout, fallback, usage | unrestricted provider switching |
| Orchestrator | task graph, checkpoints, termination, budgets | endless continuation |
| Tool gateway | schemas, authz, sandbox, idempotency, audit | arbitrary command construction |
| Memory manager | scoped reads/writes, provenance, retention, deletion | silent permanent memory writes |
| Verifier | deterministic checks, rubric scores, escalation | self-certification by the same generation |
| Human control plane | approval, override, kill switch, incident action | ambiguous irreversible approval |
| Evidence store | versions, inputs, outputs, actions, cost, decisions | secret or raw personal-data retention by default |

## Orchestration patterns

### Single bounded agent

Use when one model can complete the task with a small tool set and clear acceptance checks. This is the default.

### Planner and executor

Use when decomposition is valuable but execution remains deterministic enough to verify. The planner cannot silently rewrite constraints; each task carries inputs, output contract, budget, and acceptance criteria.

### Supervisor and workers

Use when workstreams are independent and benefit from different context or tools. The supervisor owns shared contracts, integration, conflict resolution, and final evidence.

### Generator and independent verifier

Use for consequential outputs, generated code, extraction, or decisions where correlated self-review is insufficient. The verifier receives the requirement and evidence, not the generator’s private rationale.

### Event-driven long-running workflow

Use when work spans minutes or hours, waits on external systems, or must resume. Persist state transitions, idempotency keys, checkpoints, leases, cancellation, and operator repair.

## Delegation contract

Every delegated unit includes:

```yaml
objective: one observable outcome
inputs: versioned evidence and constraints
allowed_tools: capability-scoped set
forbidden_actions: explicit list
budget:
  turns: finite integer
  tool_calls: finite integer
  tokens: finite integer
  duration_seconds: finite integer
  cost_minor_units: finite integer
output_schema: typed deliverable
acceptance: deterministic checks plus review rubric
state_access: read/write scope
termination: success, blocked, budget_exhausted, cancelled, failed
```

## Shared-state rule

Agents may read common evidence concurrently. Writes to shared plans, schemas, public contracts, production state, or release decisions are serialized through one owner and version-checked. Parallel output is integrated only after conflict and contract review.

## Failure handling

- Persist checkpoints before external side effects.
- Use leases or fencing tokens for resumable workers.
- Make tool effects idempotent or reconciled.
- Distinguish model failure, tool failure, policy block, budget exhaustion, and user cancellation.
- Never convert a blocked action into a broader alternative action without approval.
- Preserve evidence sufficient to resume without replaying irreversible effects.
