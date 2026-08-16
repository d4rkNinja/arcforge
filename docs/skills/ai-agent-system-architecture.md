# Design AI & Agent Systems (`ai-agent-system-architecture`)

Designs AI products as governed software systems rather than prompts wrapped in an API. The core rule: **the model proposes; the harness constrains, verifies, records, and decides what may happen next.**

## What it covers

- task contracts, risk classes, and measurable quality (no vague "make it smart");
- control-plane decomposition: request boundary, context assembly, policy engine, model gateway, orchestrator, tool gateway, memory, verifier, human control, evidence store;
- RAG done safely: authorization inheritance, freshness, deletion propagation, no-result behavior, grounded citations;
- model routing, structured outputs, fallbacks that preserve semantics, versioning and rollback;
- tools with capability-scoped permissions, tenant propagation, approval, idempotency, sandboxing, and audit;
- bounded agents: caps on depth, turns, tokens, duration, cost, fan-out, with cancellation and termination policies;
- a strongest-single-agent baseline before any multi-agent topology is allowed;
- durable truth versus model-generated state, unknown remote outcomes, restore-tested recovery;
- prompt injection, data leakage, memory poisoning, evaluation integrity, provider failure, and denial-of-wallet;
- evaluation portfolios (golden, adversarial, trajectory, deterministic, human, online) and release gates.

## When to use

- LLM features and assistants, RAG and document intelligence;
- tool-using or autonomous agents, multi-agent workflows;
- model gateways, routing, memory, or long-running AI jobs;
- AI actions that touch customers, money, permissions, or infrastructure;
- AI quality, safety, cost, or production-readiness reviews.

Use `system-architecture-harness` for the surrounding non-AI architecture and `architecture-review-gate` to review an AI design.

## What a run produces

A governed AI-system specification: task contract and risk class, measurable quality targets, control-plane architecture with trust boundaries, retrieval and memory design, model routes and fallback policy, tool contracts with permissions and approval, bounded orchestration, threat model, evaluation plan, reliability and observability design, rollout/rollback plan, and the smallest validation slice.

## How it works

Ten phases with gates — a model never owns permissions or durable truth; retrieved text is untrusted data; consequential actions require deterministic policy checks and human approval; "continue until done" is not a termination policy; no release on hand-picked demos.

## Works well with

- implementation skills for the surrounding backend (`api-contracts`, `async-messaging`, `security-privacy`, `production-operations`);
- `system-architecture-harness` when the AI subsystem is part of a larger production system;
- `architecture-review-gate` for independent review.

## Try it

~~~text
Design an AI research agent that can search approved sources, cite evidence,
and ask approval before any external write. Define tool contracts, token and
cost limits, evaluation, and rollback. Use ai-agent-system-architecture.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/ai-agent-system-architecture/SKILL.md)
- Templates: AI system spec, tool contract, evaluation plan, production-readiness checklist — under `skills/ai-agent-system-architecture/assets/`
- Worked examples: governed support agent, bounded multi-tenant agent platform — under `skills/ai-agent-system-architecture/examples/`
