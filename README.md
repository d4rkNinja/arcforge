# ArcForge

> Skills that make AI coding agents think before they build.

**14 portable skills** for Claude Code, Codex, and any Agent Skills-compatible runtime. MIT licensed.

AI agents write code fast. They are less reliable at the decisions that decide whether that code survives production: what must never break, what happens when a dependency dies, what an attacker will try, what can be rolled back, and what "done" actually means. ArcForge gives your agent structured skills so it asks — and answers — those questions before and while it writes code.

Every skill supports four neutral operating modes: **Think** clarifies the
decision, **Review** inspects existing evidence, **Change** applies an approved
decision, and **Verify** proves or limits the resulting claim. A skill can stop
after Think or Review when that is the requested outcome; Change never claims
completion without Verify evidence.

The repository is pure instructions, references, examples, metadata, and manual
behavioral cases. It contains no executable helper, package dependency, API key,
or vendor control plane.

[Install](#install) · [Use it](#use-it) · [Pick a skill](#pick-a-skill)

## Pick a skill

| Skill | ID | Use it when |
|---|---|---|
| **Think Through Production Systems** | `system-architecture-harness` | You are starting or re-architecting a production system, changing storage or service boundaries, or planning scale, reliability, or migrations |
| **Think Through AI & Agent Systems** | `ai-agent-system-architecture` | You are building anything model-powered: chat assistants, RAG, agents with tools, model routing, or AI features that take real actions |
| **Review Software Architecture** | `architecture-review-gate` | A design already exists and you want an independent, adversarial review before committing budget — RFCs, ADRs, migration plans, or post-incident redesigns |
| **Think Through Identity & Access** | `auth-access` | Login, signup, recovery, sessions, tokens, OAuth/OIDC, MFA, API keys, permissions, account lifecycle, or tenancy |
| **Think Through API & Client Contracts** | `api-contracts` | Endpoints, validation, errors, pagination, filtering, versioning, webhooks, realtime channels, SDKs, or CLIs |
| **Think Through Data & Storage** | `data-storage` | Data models, identifiers, money, indexes, lifecycle, files, search, provenance, or reconciliation |
| **Think Through Transactions & Consistency** | `transactions-consistency` | Transactions, concurrency, locking, idempotency, state machines, sagas, replication, sharding, or ordering |
| **Think Through Async Work & Messaging** | `async-messaging` | Jobs, workers, schedules, queues, events, outbox/inbox, batch work, email, or notifications |
| **Think Through Resilience & Flow Control** | `resilience-flow-control` | Caches, rate limits, quotas, retries, timeouts, breakers, degradation, backpressure, or admission control |
| **Think Through Security & Privacy** | `security-privacy` | Secrets, encryption, TLS/PKI, hashing, sensitive-data lifecycle, redaction, abuse defense, or randomness |
| **Think Through Production Operations** | `production-operations` | Logs, metrics, tracing, health, audit, runbooks, incidents, backup/restore, DR, regions, or residency |
| **Think Through Migrations & Evolution** | `migration-evolution` | Schema changes, backfills, contract compatibility, synchronization, CDC, reindexing, cutover, or legacy integration |
| **Think Through Quality & Release Readiness** | `quality-release` | Test strategy, failure and load evidence, performance, resource limits, scalability, or release readiness |
| **Think Through Runtime & Delivery** | `runtime-delivery` | Bootstrap, configuration, connection pools, networking, shutdown, deployment gates, CI/CD, or infrastructure |

Real tasks span several skills — "implement checkout" needs `transactions-consistency` and `async-messaging` together. Every skill lists its neighbors, so the agent knows which companions to load.

## Install

Into a project, for Claude Code and Codex:

~~~bash
npx --yes skills@1.5.22 add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -y
~~~

Globally, across all projects:

~~~bash
npx --yes skills@1.5.22 add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -g -y
~~~

Just one skill:

~~~bash
npx --yes skills@1.5.22 add d4rkNinja/arcforge --skill auth-access -a claude-code -a codex --copy -y
~~~

These commands pin the Skills CLI but install ArcForge from its current default branch. For production use, clone a reviewed release tag or commit and replace `d4rkNinja/arcforge` with that local checkout. See [Security](SECURITY.md) for the pinned-source procedure.

## Use it

Invoke by skill ID after installing — `/auth-access` in Claude Code, `$auth-access` in Codex — or just name the skill in your prompt. The **bold names** above are display names; the **IDs** are what you type.

Think through a decision without forcing a change:

~~~text
Think through a multi-tenant order platform with finite inventory,
prepaid checkout, and a regional recovery target. Compare a modular
monolith with distributed alternatives. Use system-architecture-harness.
~~~

Review an existing proposal independently:

~~~text
Review this architecture RFC for production readiness. Challenge the
capacity and recovery claims and return blockers and approval
conditions. Use architecture-review-gate.
~~~

Change an approved behavior safely:

~~~text
Change our approved password-reset design: email link, single use,
and no account enumeration. Preserve the API contract and add the
required tests. Use auth-access in Change mode.
~~~

Verify a readiness claim with evidence:

~~~text
Verify whether this checkout change is ready to release. Run the
available concurrency and failure checks, report observed results,
and label anything unavailable. Use quality-release in Verify mode.
~~~

## How it works

The selected mode controls the outcome, while each domain keeps the same safety
bar: requirements and invariants trace to decisions; critical rules trace to
enforcement and evidence; assumptions remain visible; unavailable companions or
checks are named instead of invented. Typed companions add required depth,
recommend useful coverage, or hand a separate decision to the owning skill.

## What ArcForge is not

- Not a template that forces microservices or any specific stack.
- Not a guarantee that agent output is correct — it makes the reasoning visible so you can challenge it.
- Not a replacement for security testing, legal review, or domain experts.

## Repository layout

~~~text
skills/     The 14 skills (each: SKILL.md, references, examples)
docs/       Skill guides (one page per skill), standards, provenance
evals/      Manual behavioral prompts, review criteria, and result templates
.github/    Portable skill discovery and installation smoke check
~~~

New here? Browse the [skill guides](docs/skills/) — one page per skill explaining what it covers, when to use it, and what a run produces.

Contributing: [CONTRIBUTING.md](CONTRIBUTING.md) · Agent rules: [AGENTS.md](AGENTS.md) · Standards: [docs/research-and-standards.md](docs/research-and-standards.md) · Security: [SECURITY.md](SECURITY.md)

## License

[MIT](LICENSE)
