# ArcForge

> Skills that make AI coding agents think before they build.

**14 portable skills** for Claude Code, Codex, and any Agent Skills-compatible runtime. MIT licensed.

AI agents write code fast. They are less reliable at the decisions that decide whether that code survives production: what must never break, what happens when a dependency dies, what an attacker will try, what can be rolled back, and what "done" actually means. ArcForge gives your agent structured skills so it asks — and answers — those questions before and while it writes code.

You get two kinds of skills:

- **Design & review skills** — plan and challenge whole systems: requirements before technology, evidence before confidence, independent review before approval.
- **Implementation skills** — build backend features with built-in senior-engineer expertise: each skill carries the rules, edge cases, failure modes, and release checklists a first draft usually misses.

Both layers are pure instructions. No scripts, no API keys, no vendor lock-in — install, invoke, and your agent does the reasoning.

[Install](#install) · [Use it](#use-it) · [Pick a skill](#pick-a-skill)

## Design & review skills

| Skill | ID | Use it when |
|---|---|---|
| **Design Production Systems** | `system-architecture-harness` | You are starting or re-architecting a production system, changing storage or service boundaries, or planning scale, reliability, or migrations |
| **Design AI & Agent Systems** | `ai-agent-system-architecture` | You are building anything model-powered: chat assistants, RAG, agents with tools, model routing, or AI features that take real actions |
| **Review Software Architecture** | `architecture-review-gate` | A design already exists and you want an independent, adversarial review before committing budget — RFCs, ADRs, migration plans, or post-incident redesigns |

What you get from a run: a traceable set of decisions — requirements, workload numbers, data ownership, failure and recovery behavior, security boundaries, alternatives with trade-offs, and a validation plan — instead of a fashionable diagram.

## Implementation skills

Use these whenever the agent is about to **write or change backend code**. The skill loads the domain's production guidance, forces the key questions to be answered first, and turns the must/should/never rules into decisions, tests, and stop conditions.

| Skill | ID | Use it when |
|---|---|---|
| **Implement Auth & Access Control** | `auth-access` | Adding login, signup, password reset, sessions, tokens, OAuth, MFA, API keys, permissions, or multi-tenant isolation |
| **Implement API & Client Contracts** | `api-contracts` | Building endpoints, validation, error responses, pagination, versioning, webhooks, realtime channels, or SDKs |
| **Implement Data & Storage** | `data-storage` | Modeling data, choosing identifiers, handling money and time, indexes, soft delete, file uploads, or search |
| **Implement Transactions & Consistency** | `transactions-consistency` | Writing transactional or concurrent code: locking, idempotency, retries, state machines, sagas, or sharding |
| **Implement Async Jobs & Messaging** | `async-messaging` | Adding background jobs, scheduled work, queues, events, outbox patterns, batch pipelines, email, or notifications |
| **Implement Resilience & Flow Control** | `resilience-flow-control` | Adding caching, rate limiting, quotas, retries, timeouts, circuit breakers, or overload protection |
| **Implement Security & Privacy** | `security-privacy` | Handling secrets, encryption, TLS, sensitive data, log redaction, abuse protection, or token generation |
| **Implement Observability & Operations** | `production-operations` | Adding logging, metrics, tracing, health checks, audit trails, runbooks, backups, or disaster recovery |
| **Implement Migrations & Evolution** | `migration-evolution` | Changing schemas, running backfills, evolving API/event contracts, or cutting features over safely |
| **Verify Quality & Release Readiness** | `quality-release` | Deciding whether a change is actually done: test strategy, failure and load evidence, and the final release checklist |
| **Implement Runtime & Delivery** | `runtime-delivery` | Changing configuration, connection pools, startup/shutdown behavior, deployment ordering, or CI/CD |

Real tasks span several skills — "implement checkout" needs `transactions-consistency` and `async-messaging` together. Every skill lists its neighbors, so the agent knows which companions to load.

## Install

Into a project, for Claude Code and Codex:

~~~bash
npx --yes skills add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -y
~~~

Globally, across all projects:

~~~bash
npx --yes skills add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -g -y
~~~

Just one skill:

~~~bash
npx --yes skills add d4rkNinja/arcforge --skill auth-access -a claude-code -a codex --copy -y
~~~

## Use it

Invoke by skill ID after installing — `/auth-access` in Claude Code, `$auth-access` in Codex — or just name the skill in your prompt. The **bold names** above are display names; the **IDs** are what you type.

Implement a feature safely:

~~~text
Implement password reset for our API: email link, single use,
and it must not let attackers enumerate accounts. Use auth-access.
~~~

A good run states the reset-token rules (lifetime, storage, reuse), the lockout and enumeration defenses, and the tests that prove each rule — before any code is written.

Design a system:

~~~text
Design a multi-tenant order platform with finite inventory, prepaid
checkout, and a regional recovery target. Compare a modular monolith
with distributed alternatives. Use system-architecture-harness.
~~~

Review a proposal:

~~~text
Review this architecture RFC for production readiness. Challenge the
capacity and recovery claims and return blockers and approval
conditions. Use architecture-review-gate.
~~~

## Pick a skill

| Your situation | Start with |
|---|---|
| New system, migration, or big architecture change | `system-architecture-harness` |
| Anything powered by an LLM or agents | `ai-agent-system-architecture` |
| Judging a design that already exists | `architecture-review-gate` |
| Writing or changing backend code | the matching implementation skill above |
| Deciding if a change is ready to ship | `quality-release` |

## How it works

**Implementation skills** follow one shape: route the task to the right domain guidance → answer the pre-implementation questions (or label the assumptions) → check the existing codebase before editing → turn every rule into a decision, an enforcement point, and a test → stop if any rule is left unhandled. Each ships with a worked example showing what a good run looks like.

**Design & review skills** run a gated workflow — discover, frame, quantify, model, compare, design, challenge, verify, record — with hard rules like: no technology choice before workload and invariants are known; replication is not backup; "internal network" is not an authorization model; and no review score can waive a critical failure.

## What ArcForge is not

- Not a template that forces microservices or any specific stack.
- Not a guarantee that agent output is correct — it makes the reasoning visible so you can challenge it.
- Not a replacement for security testing, legal review, or domain experts.

## Repository layout

~~~text
skills/     The 14 skills (each: SKILL.md, references, examples)
docs/       Skill guides (one page per skill), standards, provenance
evals/      Behavioral test prompts and review expectations
.github/    CI checks for skill discovery and installation
~~~

New here? Browse the [skill guides](docs/skills/) — one page per skill explaining what it covers, when to use it, and what a run produces.

Contributing: [CONTRIBUTING.md](CONTRIBUTING.md) · Agent rules: [AGENTS.md](AGENTS.md) · Standards: [docs/research-and-standards.md](docs/research-and-standards.md) · Security: [SECURITY.md](SECURITY.md)

## License

[MIT](LICENSE)
