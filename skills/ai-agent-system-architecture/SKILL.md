---
name: ai-agent-system-architecture
description: "Use when creating or changing an AI/LLM system architecture: RAG, model routing, memory, tool use, autonomous or multi-agent workflows, safety, evaluation, latency, cost, or rollout. Trigger when model, data, policy, tool, or approval boundaries are central. For non-AI architecture use system-architecture-harness; for an independent review use architecture-review-gate."
---

# AI and Agent System Architecture

## Overview

Design AI products as governed software systems rather than prompts wrapped in an API. Separate the probabilistic model from the deterministic harness that controls context, tools, memory, policy, evaluation, recovery, and irreversible actions.

**Core principle:** The model proposes; the harness constrains, verifies, records, and decides what may happen next.

```text
NO PRODUCTION AI FLOW WITHOUT:
1. a measurable task and acceptance rubric;
2. explicit model, data, context, memory, and tool boundaries;
3. a failure and fallback path;
4. offline and online evaluation;
5. traceable cost, latency, safety, and version evidence.
```

## When to Use

Use this skill for:

- LLM-backed features and assistants;
- retrieval-augmented generation and document intelligence;
- tool-using agents, coding agents, and autonomous workflows;
- supervisor/worker or multi-agent systems;
- model gateways, routing, fallbacks, and provider abstraction;
- long-running jobs with memory, checkpoints, and resumability;
- AI actions affecting money, permissions, infrastructure, customers, or external systems;
- AI quality, safety, observability, inference cost, and production-readiness reviews.

Do not use model generation where deterministic code, search, rules, or a normal workflow can satisfy the requirement more reliably and cheaply.

## Operating Modes

| Mode | Trigger | Primary result |
|---|---|---|
| **Discover** | The business problem is unclear | task definition, baseline, risk class, build/no-build recommendation |
| **Design** | A new AI capability is being planned | complete AI system and harness architecture |
| **Review** | Prompts, RAG, tools, or agents already exist | evidence-backed risks, eval gaps, and remediation |
| **Harden** | Prototype works but is unsafe or unreliable | permissions, verification, fallback, observability, and release gates |
| **Optimize** | Quality, latency, or cost misses target | measured bottlenecks and controlled experiments |
| **Migrate** | Model, vector store, framework, or provider changes | compatibility, replay, comparison, rollout, and rollback plan |

## Required Context Loading

Load only what the task needs:

- Control-plane and orchestration decisions: [Harness control plane](references/01-harness-control-plane.md)
- RAG, memory, and context assembly: [Context, retrieval, and memory](references/02-context-retrieval-memory.md)
- Tools, permissions, and threat controls: [Tool security and governance](references/03-tool-security-governance.md)
- Evaluation, tracing, and release gates: [Evaluation and observability](references/04-evaluation-observability.md)
- Serving, routing, latency, and cost: [Model serving and economics](references/05-model-serving-economics.md)
- Broader production patterns: [Production AI patterns](references/production-ai-patterns.md)

## Architecture Workflow

Follow the phases in order. Return to an earlier phase when evidence invalidates an assumption.

### Phase 0 — Define the Task and Risk Class

1. Name the user, decision, workflow, and business outcome.
2. Define the smallest unit of success that can be scored.
3. Establish a deterministic or human baseline before claiming model value.
4. Classify the action:
   - **informational** — produces content for review;
   - **reversible** — changes state with reliable undo;
   - **consequential** — affects customers, money, access, safety, or legal duties;
   - **irreversible** — cannot be reliably undone.
5. State prohibited outcomes and escalation conditions.

**Gate 0:** Do not design an agent before proving why a deterministic workflow is insufficient.

### Phase 1 — Specify Quality and System Requirements

Define measurable targets for:

- task success and rubric dimensions;
- groundedness, citation, extraction, or calculation accuracy;
- refusal and escalation behavior;
- false-positive and false-negative costs;
- P50/P95/P99 end-to-end latency;
- availability, timeout, and degraded-mode behavior;
- token, tool-call, and monetary budget per successful task;
- freshness, privacy, residency, retention, and deletion;
- concurrency, burst load, queue depth, and backlog drain time.

Separate model quality from system quality. A correct answer that violates policy, exceeds the latency budget, or performs an unauthorized action is a failed task.

**Gate 1:** Every quality claim must have a dataset, metric, threshold, owner, and measurement path.

### Phase 2 — Draw the AI Control Plane

Model these as separate components even when deployed together:

1. **Request boundary** — identity, tenant, intent, risk, quota.
2. **Context assembler** — instructions, product state, retrieved evidence, conversation state.
3. **Policy engine** — allowed data, models, tools, actions, and approval requirements.
4. **Model gateway** — routing, provider abstraction, retries, fallbacks, budgets.
5. **Planner/orchestrator** — task graph, bounded iteration, termination.
6. **Tool gateway** — schema validation, auth, idempotency, sandbox, audit.
7. **Memory service** — scoped writes, retrieval, expiry, correction, deletion.
8. **Verifier/evaluator** — deterministic checks, model judges, confidence, escalation.
9. **Human control plane** — review, approval, override, kill switch.
10. **Trace and evidence store** — versions, inputs, outputs, actions, cost, decisions.

**Gate 2:** A model must not directly own permissions, durable truth, or irreversible state transitions.

### Phase 3 — Design Context, Retrieval, and Memory

For each context source, define owner, trust level, freshness, privacy class, token budget, and injection risk.

For RAG, specify:

- ingestion sources and authorization inheritance;
- parsing, chunking, metadata, embedding, and versioning;
- index update and deletion propagation;
- query rewriting, hybrid search, filters, reranking, and top-k;
- evidence packing and citation mapping;
- no-result, conflicting-result, and stale-result behavior;
- retrieval evaluation separate from answer evaluation.

For memory, distinguish:

- conversation state;
- task checkpoint state;
- user preference memory;
- semantic knowledge memory;
- procedural or failure memory;
- audit history.

Every memory write needs scope, provenance, confidence, retention, correction, and deletion semantics.

**Gate 3:** Retrieved or remembered text is untrusted data, never privileged instruction.

### Phase 4 — Design Model Selection and Structured Outputs

For each model route, document:

- task types and risk classes it may handle;
- required capabilities and context limit;
- quality, latency, availability, and cost evidence;
- region and data-processing constraints;
- structured output schema and validation;
- retryable errors and maximum attempts;
- fallback model and semantic compatibility;
- version pinning, rollout cohort, and rollback trigger.

Prefer constrained schemas, enums, references, and typed tool arguments over free-form text for machine-consumed output.

**Gate 4:** A fallback is valid only when its behavior is evaluated against the same task contract.

### Phase 5 — Design Tools and Actions

Each tool contract must define:

- purpose and owning system;
- caller identity and tenant propagation;
- typed input/output schema;
- authorization at the resource and action boundary;
- validation, deadlines, rate limits, and quotas;
- idempotency, replay, and duplicate behavior;
- side effects, reversibility, and compensation;
- sandbox, network, filesystem, and secret scope;
- audit fields and redaction;
- approval policy and emergency disable path.

Use capability-scoped tools. Prefer a narrowly defined refund capability that accepts only an order identifier and permitted amount over generic shell, database, browser, or network access.

**Gate 5:** Consequential or irreversible actions require deterministic policy checks and explicit human approval unless a documented authority policy proves otherwise.

### Phase 6 — Bound Agent Orchestration

For autonomous or multi-agent flows, define:

- orchestration pattern and why it is needed;
- roles, inputs, deliverables, and forbidden responsibilities;
- shared contracts and source of truth;
- maximum depth, workers, turns, tool calls, tokens, duration, and spend;
- cancellation, checkpoint, resume, and deduplication;
- progress and termination predicates;
- conflict resolution and independent verification;
- degraded single-agent or manual path.

Parallelize only independent work. Serialize decisions that mutate shared contracts, schemas, or production state.

**Gate 6:** “Continue until done” is not a termination policy.

### Phase 7 — Engineer Security, Safety, and Privacy

Threat-model:

- prompt injection and instruction hierarchy attacks;
- indirect injection through documents, web pages, tool results, and memory;
- data exfiltration and cross-tenant retrieval;
- privilege escalation and confused-deputy actions;
- poisoned knowledge, embeddings, and evaluation data;
- insecure generated code or commands;
- secret, personal-data, and regulated-data leakage;
- denial of wallet through token or tool amplification;
- unsafe delegation and reviewer collusion;
- log and trace over-collection.

Controls should include least privilege, allowlists, sandboxing, egress limits, secret isolation, content provenance, output validation, approval, rate limits, anomaly detection, and tamper-evident audit.

**Gate 7:** Prompt wording alone is not a security boundary.

### Phase 8 — Design Evaluation and Feedback

Build an evaluation portfolio:

1. **Golden cases** for normal and high-value workflows.
2. **Adversarial cases** for injections, ambiguity, unsafe requests, and data isolation.
3. **Trajectory checks** for tool choice, arguments, ordering, retries, and termination.
4. **Deterministic checks** for schema, calculations, citations, permissions, and side effects.
5. **Human review** for nuanced quality and high-risk false positives.
6. **Reliability runs** across repeated trials and model versions.
7. **Online signals** tied to user correction, escalation, abandonment, and incidents.

Keep evaluation data versioned and access-controlled. Prevent the model from editing its own gates, expected answers, or production success metrics.

**Gate 8:** No release based only on a few hand-picked demonstrations.

### Phase 9 — Design Reliability, Observability, and Operations

Trace the full path with correlated identifiers for request, tenant, prompt version, model, retrieval, tools, approvals, and resulting state changes.

Define:

- timeout and retry budgets per stage;
- queue bounds, admission control, and cancellation;
- fallback, abstain, manual, and read-only modes;
- provider outage and quota-exhaustion behavior;
- model, prompt, index, policy, and tool version labels;
- quality, safety, latency, cost, and business SLIs;
- alerts, runbooks, incident ownership, and kill switches;
- replay-safe evidence for debugging without exposing protected data.

**Gate 9:** If an AI action cannot be reconstructed from evidence, it is not production-operable.

### Phase 10 — Release, Learn, and Evolve

1. Compare the candidate against the current baseline on a fixed eval set.
2. Shadow or replay production-like traffic where lawful.
3. Release by risk-bounded cohort with feature flags.
4. Monitor quality, cost, latency, safety, and business outcomes together.
5. Define automatic rollback and manual kill criteria.
6. Convert incidents and recurring reviewer findings into new eval cases, policies, and reusable failure memory.
7. Revalidate after model, prompt, data, retriever, tool, policy, or dependency changes.

**Gate 10:** A prompt or model update is a production change and follows normal release governance.

## Hard Clauses

- **IF** the output controls software behavior, **THEN** require a typed schema, validation, and safe failure.
- **IF** retrieved data can carry instructions, **THEN** isolate it from system/developer authority and test indirect injection.
- **IF** an agent writes memory, **THEN** define provenance, scope, confidence, expiry, correction, and deletion.
- **IF** an agent calls a tool, **THEN** enforce identity, tenant, authorization, typed arguments, deadline, audit, and idempotency where applicable.
- **IF** a tool can change consequential state, **THEN** require policy evaluation and an approval or pre-authorized bounded mandate.
- **IF** agents delegate, **THEN** cap depth, concurrency, iterations, tokens, cost, and shared-state access.
- **IF** a model provider fails, **THEN** degrade safely rather than silently changing semantics.
- **IF** a model judge gates release, **THEN** calibrate it against human labels and keep deterministic blockers independent.
- **IF** user or tenant data enters training, fine-tuning, memory, logs, or evals, **THEN** record lawful basis, consent/contract, retention, deletion, and access controls.
- **IF** the system cannot state why an action was allowed, **THEN** block the action.

## Output Contract

Unless the user requests a narrower artifact, produce:

1. **Decision summary** and AI/non-AI boundary.
2. **Task contract**, users, risk class, and prohibited outcomes.
3. **Measurable quality, latency, safety, availability, and cost requirements.**
4. **Control-plane architecture** and trust boundaries.
5. **Context, RAG, and memory design.**
6. **Model routes**, structured outputs, fallbacks, and version policy.
7. **Tool contracts**, permissions, approval, and reversibility.
8. **Agent topology**, budgets, state, termination, and recovery.
9. **Threat model**, privacy lifecycle, and abuse controls.
10. **Evaluation plan** with golden, adversarial, trajectory, and online evidence.
11. **Reliability and observability** including degraded modes and kill switches.
12. **Rollout, rollback, cost model, ADRs, risks, and smallest validation slice.**

Use [AI system specification template](assets/ai-system-spec-template.md), [tool contract template](assets/tool-contract-template.md), and [evaluation plan template](assets/evaluation-plan-template.md) when a file artifact is required.

Use the [governed support-agent example](examples/governed-support-agent.md) when a concrete end-to-end reference is useful.

## Stop Conditions

Stop and revise the architecture when any of these appears:

- the model is the source of truth for identity, permissions, balances, inventory, or durable business state;
- broad shell, SQL, browser, filesystem, cloud, or network access without capability boundaries;
- consequential action without resource authorization and approval policy;
- RAG without tenant filters, deletion propagation, provenance, or no-result behavior;
- memory with no scope, retention, correction, or deletion path;
- free-form output parsed by fragile string rules for machine actions;
- unbounded agent depth, iterations, retries, fan-out, token use, or spend;
- model fallback that changes safety or correctness semantics without evaluation;
- “the prompt says not to” used as the only security control;
- evaluation based only on demonstrations, generic benchmarks, or a single model judge;
- traces that omit prompt/model/tool/policy versions or expose secrets and personal data;
- no manual path, read-only mode, rollback, or kill switch for high-impact workflows.

## Verification Before Completion

Before approval:

1. Trace at least one normal, injection, timeout, duplicate, provider-outage, and unauthorized-action scenario.
2. Verify every tool and memory boundary against identity and tenant context.
3. Check all budgets have hard limits and observable counters.
4. Confirm model, prompt, retriever, index, policy, and tool versions are recoverable from traces.
5. Run the candidate against fixed golden and adversarial datasets.
6. Confirm deterministic blockers cannot be waived by model-generated confidence.
7. Record remaining uncertainty, owner, validation method, and release trigger.
