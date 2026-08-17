# ArcForge

> Make production architecture decisions your AI coding agent can explain, challenge, and verify.

**v0.3.2 · 14 portable Agent Skills · Claude Code, Codex, and compatible runtimes · MIT**

ArcForge helps an AI agent reason about the decisions that determine whether a
system survives production: invariants, failure modes, trust boundaries,
recovery, rollout safety, and evidence. Use it before a change, during a review,
while implementing an approved decision, or when proving readiness.

## Quick start

Install every skill into the current project for Claude Code and Codex:

~~~bash
npx --yes skills@1.5.22 add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -y
~~~

Then give your agent a real decision:

~~~text
Think through a multi-tenant order platform with finite inventory and prepaid
checkout. Compare a modular monolith with distributed alternatives, identify
the invariants, and define the evidence needed before implementation. Use
system-architecture-harness in Think mode.
~~~

Install globally with `-g`, or replace `'*'` with a skill ID to install only one
skill. For a reviewed production source, clone a release tag or commit and use
that local checkout; see [Security](SECURITY.md).

## Choose a mode

Every ArcForge skill supports the same four modes. State one explicitly or let
the skill infer it from your request.

| Mode | Use it when you want |
|---|---|
| **Think** | Requirements, constraints, alternatives, decisions, and validation paths before a change |
| **Review** | Evidence-based findings and blockers for an existing proposal, repository, diff, or operational state |
| **Change** | An approved decision applied while preserving contracts, safety, integrity, and rollback |
| **Verify** | Tests, measurements, operational evidence, and an honest account of residual risk |

Think and Review can finish without changing a repository. Change reaches
completion only with Verify evidence. For a combined request, the skill keeps a
clear trace from the decision through the change to the proof.

## Choose a skill

The display name explains the skill's purpose. The stable ID is what you install
or invoke: `/auth-access` in Claude Code or `$auth-access` in Codex. You can also
name the ID naturally in a prompt.

### Production system design

| Skill | ID | Choose it for |
|---|---|---|
| **Think Through Production Systems** | `system-architecture-harness` | Whole-system boundaries, workloads, invariants, scale, reliability, migrations, clients, or platform governance |

### AI and agent systems

| Skill | ID | Choose it for |
|---|---|---|
| **Think Through AI & Agent Systems** | `ai-agent-system-architecture` | LLM, RAG, memory, model routing, tool use, agent authority, evaluation, latency, cost, or rollout |

### Independent review

| Skill | ID | Choose it for |
|---|---|---|
| **Review Software Architecture** | `architecture-review-gate` | An independent evidence gate for an RFC, ADR, migration plan, AI design, production proposal, or post-incident redesign |

### Backend domains

| Skill | ID | Choose it for |
|---|---|---|
| **Think Through Identity & Access** | `auth-access` | Login, recovery, sessions, OAuth/OIDC, MFA, API keys, permissions, account lifecycle, or tenancy |
| **Think Through API & Client Contracts** | `api-contracts` | Endpoints, validation, errors, pagination, versioning, webhooks, realtime, SDKs, or CLIs |
| **Think Through Data & Storage** | `data-storage` | Models, identifiers, money, indexes, files, search, lifecycle, provenance, or reconciliation |
| **Think Through Transactions & Consistency** | `transactions-consistency` | Transactions, concurrency, idempotency, state machines, sagas, replication, sharding, or ordering |
| **Think Through Async Work & Messaging** | `async-messaging` | Jobs, workers, schedules, queues, events, outbox/inbox, batch work, email, or notifications |
| **Think Through Resilience & Flow Control** | `resilience-flow-control` | Caches, rate limits, quotas, retries, timeouts, breakers, degradation, backpressure, or admission control |
| **Think Through Security & Privacy** | `security-privacy` | Secrets, encryption, TLS/PKI, hashing, sensitive-data lifecycle, redaction, abuse defense, or randomness |
| **Think Through Production Operations** | `production-operations` | Logs, metrics, tracing, health, audit, incidents, backup/restore, disaster recovery, regions, or residency |
| **Think Through Migrations & Evolution** | `migration-evolution` | Schema changes, backfills, compatibility, synchronization, CDC, reindexing, cutover, or legacy integration |
| **Think Through Quality & Release Readiness** | `quality-release` | Test strategy, concurrency and failure evidence, load, performance, resource limits, or release readiness |
| **Think Through Runtime & Delivery** | `runtime-delivery` | Bootstrap, configuration, pools, networking, shutdown, deployment gates, CI/CD, or infrastructure |

## Copy a prompt

### Think

~~~text
Think through our multi-region write strategy. Compare ownership and routing
models, define conflict and fencing semantics, and record the evidence needed
before approval. Use system-architecture-harness in Think mode.
~~~

### Review

~~~text
Review this architecture RFC independently. Challenge its capacity, recovery,
authorization, and migration claims. Return prioritized blockers, approval
conditions, and evidence gaps. Use architecture-review-gate in Review mode.
~~~

### Change

~~~text
Apply our approved password-reset decision: single-use email links, bounded
expiry, and no account enumeration. Preserve the existing API contract and add
the required coverage. Use auth-access in Change mode, then verify the result.
~~~

### Verify

~~~text
Verify whether this checkout change is ready to release. Run the available
concurrency and failure checks, report observed results, and label every check
that could not be run. Use quality-release in Verify mode.
~~~

## How skills work together

Real systems cross domains. ArcForge marks companion skills by relationship:

| Relationship | Meaning |
|---|---|
| **Required** | The requested outcome needs this domain for a safe conclusion |
| **Recommended** | It materially improves coverage while the current skill keeps a safe local path |
| **Handoff** | It owns a separate decision discovered during the current work |
| **Optional depth** | It adds focused detail when relevant |

For example, checkout usually combines `transactions-consistency` for inventory
and payment invariants, `async-messaging` for post-commit work, and
`resilience-flow-control` for retries and dependency failure. Each skill keeps
its own decision boundary and names any depth that remains unresolved.

## What a strong result contains

- Requirements, constraints, assumptions, and invariants tied to each decision.
- Alternatives with explicit tradeoffs and rejected options.
- Failure modes, trust boundaries, operational ownership, and rollback paths.
- Critical blockers that remain visible regardless of a score or checklist.
- Validation evidence, unrun checks, residual risks, and concrete next steps.

ArcForge improves the structure and auditability of agent reasoning. Final
responsibility remains with the people who approve, implement, operate, secure,
and regulate the system.

## Learn more

- [Skill guides](docs/skills/) — what each skill covers, when to use it, and what it produces
- [Research and standards](docs/research-and-standards.md) — source and evidence discipline
- [Contributing](CONTRIBUTING.md) — repository conventions and review requirements
- [Security](SECURITY.md) — source pinning, permissions, and reporting
- [Changelog](CHANGELOG.md) — release history

## License

[MIT](LICENSE)
