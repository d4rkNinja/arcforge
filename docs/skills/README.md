# Skill Guides

One page per skill: what it is, when to use it, what it covers, what a run produces, and which skills it pairs with. Not sure which one you need? Start with the routing layer and it will tell you. Every design and domain skill supports **Think**, **Review**, **Change**, and **Verify**. The `SKILL.md` inside each skill remains the authoritative instructions.

## Routing layer

| Guide | Skill ID | One-line purpose |
|---|---|---|
| [Using Forge](using-forge.md) | `using-forge` | Pick the owning skill, the mode, the companions, and the order, then start the work |
| [Think Forge](think-forge.md) | `think-forge` | Answer which skill, which mode, and what order, then stop |

## Design & review layer

| Guide | Skill ID | One-line purpose |
|---|---|---|
| [Think Through Production Systems](system-architecture-harness.md) | `system-architecture-harness` | Make evidence-backed production-system decisions |
| [Think Through AI & Agent Systems](ai-agent-system-architecture.md) | `ai-agent-system-architecture` | Decide LLM and agent systems where models propose and policy governs |
| [Review Software Architecture](architecture-review-gate.md) | `architecture-review-gate` | Independently challenge an existing design before approval |

## Domain layer

| Guide | Skill ID | One-line purpose |
|---|---|---|
| [Think Through Identity & Access](auth-access.md) | `auth-access` | Login, sessions, tokens, permissions, and tenancy done safely |
| [Think Through API & Client Contracts](api-contracts.md) | `api-contracts` | Endpoints, validation, errors, pagination, and webhooks clients can rely on |
| [Think Through Data & Storage](data-storage.md) | `data-storage` | Schemas, money, identifiers, files, and lifecycle that hold up |
| [Think Through Transactions & Consistency](transactions-consistency.md) | `transactions-consistency` | Concurrency, locking, and idempotency that keep invariants true |
| [Think Through Async Work & Messaging](async-messaging.md) | `async-messaging` | Jobs, queues, and events with bounded retries and no lost work |
| [Think Through Resilience & Flow Control](resilience-flow-control.md) | `resilience-flow-control` | Caching, rate limiting, timeouts, and breakers that survive failure |
| [Think Through Security & Privacy](security-privacy.md) | `security-privacy` | Secrets, crypto, sensitive data, and abuse resistance |
| [Think Through Production Operations](production-operations.md) | `production-operations` | Signals, runbooks, backups, and recovery you can prove |
| [Think Through Migrations & Evolution](migration-evolution.md) | `migration-evolution` | Schema and contract changes that ship without outages |
| [Think Through Quality & Release Readiness](quality-release.md) | `quality-release` | Evidence-based readiness instead of unsupported confidence |
| [Think Through Runtime & Delivery](runtime-delivery.md) | `runtime-delivery` | Config, pools, shutdown, and deploys that behave under failure |
| [Think Through Git & Repository Workflows](git-workflows.md) | `git-workflows` | Safe Git state, refs, workflows, tags, versions, provenance, and recovery |

## How the layers fit together

For a combined request, use the shared sequence **Think → Review → Change → Verify**. A skill may stop after Think with a decision or after Review with findings. Change applies approved work and cannot claim completion before Verify; Verify reports observed evidence and labels unrun checks. Each guide identifies frequent companions, while every installed skill retains a safe standalone boundary.

Companions are typed: **required** when the requested outcome cannot be completed safely without them, **recommended** when they materially deepen coverage, **handoff** when a separate skill owns the next decision, and **optional-depth** for focused extra material. When a companion is absent, the active skill completes only its safe local decision, names the missing depth, and recommends the exact technical ID or installation group. It never claims unavailable material was read or relaxes a safety gate.

Other documentation: [research and standards map](../research-and-standards.md) for provenance behind the repository.
