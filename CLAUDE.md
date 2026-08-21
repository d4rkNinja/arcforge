# Claude Code Repository Instructions

Read [`AGENTS.md`](AGENTS.md) as the repository source of truth.

This is a portable Agent Skills repository. Keep all seventeen skills runtime-neutral and do not add native Claude Code plugins, hooks, agents, or a separate harness configuration unless the user explicitly requests a new distribution format.

Route work by skill:

Routing layer (use when the owning skill, the mode, or the order is not settled):

- pick the skill, the mode, the companions, and the order, then continue into the work -> `skills/using-forge/SKILL.md`;
- answer which skill, which mode, and what order, then stop, with nothing inspected or changed -> `skills/think-forge/SKILL.md`.

Architecture layer:

- general system design -> `skills/system-architecture-harness/SKILL.md`;
- LLM, RAG, memory, tools, or agents -> `skills/ai-agent-system-architecture/SKILL.md`;
- architecture review or approval -> `skills/architecture-review-gate/SKILL.md`.

Domain thinking layer (select think, review, change, or verify and read the
routed papers before making claims):

- identity, authentication, sessions, permissions, tenancy -> `skills/auth-access/SKILL.md`;
- APIs, validation, errors, pagination, versioning, webhooks, realtime, SDKs -> `skills/api-contracts/SKILL.md`;
- schemas, identifiers, money, time, indexes, files, search, lifecycle -> `skills/data-storage/SKILL.md`;
- transactions, locking, idempotency, sagas, sharding, distributed locks -> `skills/transactions-consistency/SKILL.md`;
- jobs, queues, events, outbox, batch, email, notifications -> `skills/async-messaging/SKILL.md`;
- caching, rate limiting, quotas, retries, timeouts, breakers, backpressure -> `skills/resilience-flow-control/SKILL.md`;
- secrets, crypto, TLS, sensitive data, redaction, abuse, randomness -> `skills/security-privacy/SKILL.md`;
- logging, metrics, tracing, health, audit, runbooks, backup/DR, multi-region -> `skills/production-operations/SKILL.md`;
- schema/data/contract migration, backfills, cutover, legacy integration -> `skills/migration-evolution/SKILL.md`;
- test strategy, concurrency/failure/load evidence, release checklist -> `skills/quality-release/SKILL.md`;
- config, connection pools, graceful shutdown, deploy ordering, CI/CD -> `skills/runtime-delivery/SKILL.md`;
- branches, commits, merges, rebases, remotes, tags, versions, protected refs, history rewrites, Git recovery -> `skills/git-workflows/SKILL.md`.

Domain papers live in each skill's `references/papers/`. When a canonical paper
changes, update every owning skill copy with it and review semantic parity and
links; do not hand-edit only one side.

Use the Skills CLI for installation checks and restart Claude Code when a newly created top-level skill directory is not visible in the current session.
