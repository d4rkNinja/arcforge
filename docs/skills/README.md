# Skill Guides

One page per skill: what it is, when to use it, what it covers, what a run produces, and which skills it pairs with. Start here when deciding which skill fits your task; the skill's own `SKILL.md` remains the authoritative instructions.

## Design & review layer

| Guide | Skill ID | One-line purpose |
|---|---|---|
| [Design Production Systems](system-architecture-harness.md) | `system-architecture-harness` | Turn a requirement into an evidence-backed production architecture |
| [Design AI & Agent Systems](ai-agent-system-architecture.md) | `ai-agent-system-architecture` | Design LLM/agent systems where the model proposes and the harness governs |
| [Review Software Architecture](architecture-review-gate.md) | `architecture-review-gate` | Independently challenge an existing design before approval |

## Implementation layer

| Guide | Skill ID | One-line purpose |
|---|---|---|
| [Implement Auth & Access Control](auth-access.md) | `auth-access` | Login, sessions, tokens, permissions, and tenancy done safely |
| [Implement API & Client Contracts](api-contracts.md) | `api-contracts` | Endpoints, validation, errors, pagination, webhooks clients can rely on |
| [Implement Data & Storage](data-storage.md) | `data-storage` | Schemas, money, identifiers, files, and lifecycle that hold up |
| [Implement Transactions & Consistency](transactions-consistency.md) | `transactions-consistency` | Concurrency, locking, and idempotency that keep invariants true |
| [Implement Async Jobs & Messaging](async-messaging.md) | `async-messaging` | Jobs, queues, and events with bounded retries and no lost work |
| [Implement Resilience & Flow Control](resilience-flow-control.md) | `resilience-flow-control` | Caching, rate limiting, timeouts, and breakers that survive failure |
| [Implement Security & Privacy](security-privacy.md) | `security-privacy` | Secrets, crypto, sensitive data, and abuse resistance |
| [Implement Observability & Operations](production-operations.md) | `production-operations` | Signals, runbooks, backups, and recovery you can prove |
| [Implement Migrations & Evolution](migration-evolution.md) | `migration-evolution` | Schema and contract changes that ship without outages |
| [Verify Quality & Release Readiness](quality-release.md) | `quality-release` | Evidence-based "done" instead of "tests passed" |
| [Implement Runtime & Delivery](runtime-delivery.md) | `runtime-delivery` | Config, pools, shutdown, and deploys that behave under failure |

## How the layers fit together

Typical flow for a new feature: pick the architecture skill if the shape of the system is being decided, then switch to the matching implementation skill (or skills) when code gets written, and finish with `quality-release` before calling it done. Implementation skills list their frequent companions in each guide's "Works well with" section.

Other documentation: [research and standards map](../research-and-standards.md) for provenance behind the repository.
