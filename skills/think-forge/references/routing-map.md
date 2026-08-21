# ArcForge Routing Map

The routing table for the ArcForge skill set. Every entry names one skill, the surface it owns, the requests that belong to it, the requests that do not, and the companions it pulls in.

`arcforge.catalog.yaml` in the repository root is the canonical source for this map. Both `using-forge` and `think-forge` carry an identical copy of this file; when the catalog changes, update both copies together.

## How to read an entry

- **Owns** — the surface this skill is accountable for.
- **Route here when** — the request's real subject matches one of these.
- **Do not route here for** — matches that look right and are not. Check this before settling on an owner.
- **Companions** — typed relationships. `required` enters the route before or with the owner. `recommended` enters when its condition is met. `handoff` becomes a later step. `optional-depth` enters only when the request asks for that depth.

## Modes

| Mode | Purpose | Completion |
|---|---|---|
| **Think** | Clarify requirements, constraints, invariants, risks, alternatives, decisions, and validation paths before a change | May stop with a decision record and explicit unresolved questions |
| **Review** | Inspect an existing proposal, repository, diff, or operational state and separate evidence from assumptions | May stop with prioritized findings and blockers; does not claim changes were made |
| **Change** | Turn approved decisions into a change sequence while preserving contracts, safety, integrity, and rollback | Does not claim completion without Verify evidence |
| **Verify** | Prove behavior with tests, measurements, operational evidence, and explicit residual risk | Does not replace missing evidence with assumptions or planned checks |

## Ordering rules

1. The owner of an **invariant** precedes anything derived from it. Authoritative state before post-commit work, notifications, or caches.
2. A **required** companion whose decision constrains the owner runs first. Identity and authorization precede the contract exposing them; secret and key policy precedes the flow consuming it.
3. **Evolution and delivery follow the target design.** Migration sequencing and deploy ordering are decided after the shape they migrate toward.
4. **Evidence closes the route.** `quality-release` runs last on any route ending in a readiness or completion claim.
5. **Independent review is terminal.** `architecture-review-gate` is never a companion of the skill it reviews.
6. A **handoff never runs in parallel with its source** — it exists because the earlier decision produces its input.

## Standing down

The routing layer adds a step. These rules keep it from adding a step that buys no coverage.

1. When the user already named a skill, confirm that owner and hand off. Do not re-derive the route, and do not replace the named skill without stating the reason.
2. When one domain plainly owns the request and neither the mode nor the order is in question, name that skill directly.
3. A route is never approval, review, or release readiness. `architecture-review-gate` owns an independent verdict and `quality-release` owns release evidence.
4. A routing skill never answers the domain question on the owning skill's behalf, and never reports a skill as loaded, consulted, or already run.

## Routing layer

### `using-forge` — Using Forge

- **Owns:** routing entry point: skill selection, mode selection, companion resolution, and step order.
- **Route here when:** which skill, where do I start, route this, multi-domain request, what order, which mode, companion skills, is anything missing.
- **Do not route here for:** user already named a skill; single unambiguous domain; independent approval verdict; the domain answer itself.
- **Companions:** handoff `think-forge` when the route is the whole question and nothing should be inspected or changed · handoff `system-architecture-harness` when the routed surface is whole-system architecture · handoff `architecture-review-gate` when an independent approval verdict is requested · recommended `quality-release` when the route ends in a readiness or completion claim.

### `think-forge` — Think Forge

- **Owns:** read-only routing answer: which skill, which mode, which order.
- **Route here when:** which skill covers this, where do I start, which mode, what order, route only, do not change anything, check my plan, second opinion on the route.
- **Do not route here for:** perform the work; apply the change; user already named a skill; single unambiguous domain with the mode settled; independent approval verdict; inspect the repository.
- **Companions:** handoff `using-forge` when the route must carry companion contracts and continue into the work · handoff `architecture-review-gate` when an independent approval verdict is requested.

## Architecture layer

### `system-architecture-harness` — Think Through Production Systems

- **Owns:** general production-system architecture.
- **Route here when:** greenfield architecture, system decomposition, service boundaries, workload, invariants, multi-region, offline client, platform governance, rewrite.
- **Do not route here for:** an independent approval gate; an AI control plane.
- **Companions:** handoff `ai-agent-system-architecture` when model, retrieval, memory, tool, or approval boundaries are central · handoff `architecture-review-gate` when an independent approval verdict is requested · recommended `quality-release` when architecture claims need release evidence.

### `ai-agent-system-architecture` — Think Through AI & Agent Systems

- **Owns:** AI, LLM, RAG, tool-using, and agent-system architecture.
- **Route here when:** LLM, RAG, model routing, memory, tool use, agent, multi-agent, evaluation, prompt injection, approval.
- **Do not route here for:** non-AI architecture only; an independent approval verdict.
- **Companions:** handoff `system-architecture-harness` when surrounding service, data, client, or regional architecture must be decided · handoff `architecture-review-gate` when an independent approval verdict is requested · required `security-privacy` when tools, hostile input, secrets, or sensitive data cross the AI boundary · recommended `quality-release` when candidate behavior needs release evidence.

### `architecture-review-gate` — Review Software Architecture

- **Owns:** independent architecture evidence and approval review.
- **Route here when:** independent review, approval gate, RFC, ADR, due diligence, blocker, evidence challenge, post-incident review.
- **Do not route here for:** greenfield design ownership; direct repository change.
- **Companions:** handoff `system-architecture-harness` when a general architecture must be created or revised · handoff `ai-agent-system-architecture` when an AI subsystem must be created or revised · recommended `quality-release` when code-level release evidence must be assessed.

## Domain layer

### `auth-access` — Think Through Identity & Access

- **Owns:** identity, authentication, authorization, and tenancy.
- **Route here when:** login, password reset, session, token, OAuth, MFA, passkey, API key, RBAC, tenancy, impersonation.
- **Do not route here for:** general API contract; cryptographic primitive selection; whole-system architecture.
- **Companions:** required `security-privacy` when credential hashing, token randomness, secret storage, or cryptography is in scope · recommended `api-contracts` when public request, validation, or error behavior changes · recommended `resilience-flow-control` when brute-force pacing, lockout, or abuse limits are required · optional-depth `production-operations` when privileged audit, alerting, or incident evidence needs focused depth · handoff `migration-evolution` when credential, session, permission, or tenant data must evolve.

### `api-contracts` — Think Through API & Client Contracts

- **Owns:** HTTP, RPC, GraphQL, webhook, realtime, SDK, and CLI contracts.
- **Route here when:** endpoint, request validation, error response, pagination, filtering, versioning, webhook, WebSocket, SSE, SDK, CLI.
- **Do not route here for:** queue internals; schema migration sequence; authentication policy ownership.
- **Companions:** required `auth-access` when authentication or object, field, action, or tenant authorization is in scope · recommended `data-storage` when filters, sorting, pagination, or serialization affect query or precision behavior · handoff `async-messaging` when event delivery or webhook worker internals are in scope · handoff `migration-evolution` when old clients or consumers must coexist with a contract change.

### `data-storage` — Think Through Data & Storage

- **Owns:** data modeling, identifiers, precision, indexes, files, search, and lifecycle.
- **Route here when:** schema, identifier, timestamp, money, constraint, index, query, soft delete, file, search, retention, reconciliation.
- **Do not route here for:** transaction isolation; migration sequencing; cache mechanics; whole-system architecture.
- **Companions:** required `transactions-consistency` when concurrent writers or transactional invariants cross the data boundary · handoff `migration-evolution` when existing data or schema must change · recommended `security-privacy` when sensitive fields, files, retention, or deletion are in scope · recommended `production-operations` when backup, restore, or reconciliation evidence is required.

### `transactions-consistency` — Think Through Transactions & Consistency

- **Owns:** transactions, concurrency, idempotency, distributed coordination, and ordering.
- **Route here when:** transaction, lost update, write skew, lock, state machine, idempotency, saga, consistency, replication, sharding, fencing.
- **Do not route here for:** queue delivery mechanics; retry pacing; schema design; whole-system boundaries.
- **Companions:** required `async-messaging` when post-commit events, outbox or inbox, jobs, or email are in scope · required `resilience-flow-control` when remote retries, timeouts, breakers, or overload are in scope · recommended `data-storage` when constraints or indexes backstop the invariant · recommended `quality-release` when race, duplicate, or ambiguous-outcome claims need proof.

### `async-messaging` — Think Through Async Work & Messaging

- **Owns:** background work, queues, events, outbox, batch, email, and notifications.
- **Route here when:** background job, worker, cron, queue, event, outbox, inbox, batch, deduplication, email, notification.
- **Do not route here for:** transaction isolation; retry pacing only; public webhook contract; whole-system architecture.
- **Companions:** required `transactions-consistency` when work or events derive from an authoritative commit · required `resilience-flow-control` when retry, timeout, backpressure, or dependency failure policy is in scope · handoff `migration-evolution` when event schemas or consumers evolve · recommended `production-operations` when lag, depth, poison, or provider failures need operational evidence.

### `resilience-flow-control` — Think Through Resilience & Flow Control

- **Owns:** caching, rate limits, quotas, retries, timeouts, breakers, and overload.
- **Route here when:** cache, invalidation, stampede, rate limit, quota, retry, timeout, circuit breaker, degradation, backpressure.
- **Do not route here for:** queue delivery semantics; transaction locking; whole-system capacity architecture.
- **Companions:** required `transactions-consistency` when retries can duplicate or ambiguously complete state changes · recommended `async-messaging` when queue depth, worker concurrency, or backlog behavior is central · recommended `quality-release` when outage, overload, latency, or stampede claims need proof · handoff `system-architecture-harness` when capacity or overload changes whole-system topology.

### `security-privacy` — Think Through Security & Privacy

- **Owns:** secrets, cryptography, TLS, sensitive data, abuse, flags, and randomness.
- **Route here when:** secret, encryption, TLS, PKI, cryptography, hashing, sensitive data, redaction, abuse, feature flag, randomness.
- **Do not route here for:** login flow ownership; request contract ownership; whole-system threat model.
- **Companions:** handoff `auth-access` when login, session, OAuth, MFA, API key, or permission flow is central · recommended `api-contracts` when validation, error leakage, or public security headers change · recommended `resilience-flow-control` when abuse defense needs throttling mechanics · recommended `production-operations` when audit, alerting, rotation, or deletion evidence is required.

### `production-operations` — Think Through Production Operations

- **Owns:** observability, runbooks, incidents, import/export, backup, restore, DR, and regions.
- **Route here when:** logging, metrics, tracing, health check, audit, runbook, incident, backup, restore, disaster recovery, multi-region, residency.
- **Do not route here for:** deployment sequencing; sensitive-data policy ownership; whole-system topology decision.
- **Companions:** handoff `migration-evolution` when rollout order, compatibility, or data transition is central · required `security-privacy` when telemetry, export, audit, or recovery data contains sensitive material · recommended `quality-release` when load, failure, restore, or failover claims need proof · handoff `system-architecture-harness` when availability or region choices change system topology.

### `migration-evolution` — Think Through Migrations & Evolution

- **Owns:** schema, data, contract, feature, search, and legacy evolution.
- **Route here when:** schema migration, expand and contract, backfill, compatibility, data synchronization, CDC, reindex, cutover, strangler.
- **Do not route here for:** new contract design; CI pipeline tooling; whole-system rewrite decision.
- **Companions:** required `transactions-consistency` when transition writes, precedence, or concurrent backfills affect authoritative invariants · required `async-messaging` when transactional outbox or inbox, retained events, or relay migration is in scope · recommended `runtime-delivery` when deployment ordering, health gates, or pipeline mechanics are in scope · recommended `quality-release` when coexistence, resumability, or rollback claims need proof.

### `quality-release` — Think Through Quality & Release Readiness

- **Owns:** test strategy, failure and load evidence, performance, resources, and release readiness.
- **Route here when:** test strategy, test data, concurrency test, failure test, load test, performance, scalability, resource leak, release readiness, release exception, production ready.
- **Do not route here for:** independent architecture approval; SLO ownership; incident process.
- **Companions:** required `auth-access` when identity, authorization, or tenant-isolation boundaries need proof · required `security-privacy` when secrets, privacy, cryptography, or abuse boundaries need proof · recommended `transactions-consistency` when transaction or concurrency invariants must be forced · recommended `async-messaging` when queue, job, or event failure paths need proof · recommended `api-contracts` when request, response, webhook, or client compatibility needs proof · recommended `data-storage` when persistence constraints, precision, indexes, files, or lifecycle need proof · recommended `migration-evolution` when mixed-version compatibility, backfill, or cutover needs proof · recommended `runtime-delivery` when configuration, artifact promotion, shutdown, or deployment needs proof · recommended `production-operations` when restore, failover, alert, or runbook claims need evidence · recommended `git-workflows` when candidate refs, release tags, versions, or source-to-artifact identity need proof · handoff `architecture-review-gate` when an independent architecture approval verdict is requested.

### `runtime-delivery` — Think Through Runtime & Delivery

- **Owns:** runtime foundations, configuration, connections, networking, shutdown, deployment, and CI/CD.
- **Route here when:** bootstrap, configuration, connection pool, networking, load balancing, service discovery, graceful shutdown, deployment, CI/CD, infrastructure.
- **Do not route here for:** schema migration semantics; telemetry ownership; architecture style decision; retry policy ownership.
- **Companions:** required `migration-evolution` when deployment includes schema, data, or contract evolution · required `security-privacy` when configuration carries secrets or service identity · recommended `production-operations` when health, readiness, deployment, or shutdown behavior needs signals · recommended `quality-release` when boot, shutdown, rollback, or pipeline claims need proof · recommended `git-workflows` when branch protections, merge queues, tags, versions, or source refs are in scope.

### `git-workflows` — Think Through Git & Repository Workflows

- **Owns:** Git repositories, branch topology, refs, hosted policy, releases, history migration, and recovery.
- **Route here when:** Git flow, branch, merge, rebase, cherry-pick, conflict, worktree, remote, pull request, protected ref, force push, tag, semantic version, release branch, history rewrite, secret removal, merge queue, Git CI, reflog.
- **Do not route here for:** deployment implementation only; test strategy only; independent architecture approval.
- **Companions:** required `runtime-delivery` when CI/CD, build identity, artifact promotion, or deployment is changed · required `security-privacy` when credentials, signing, untrusted CI, or sensitive history is involved · recommended `quality-release` when current checks, failure tests, or a release verdict is needed · recommended `production-operations` when backup, restore, audit, or incident response evidence is needed · handoff `migration-evolution` when default branch, workflow, shared history, or compatibility changes across consumers · handoff `architecture-review-gate` when an independent repository or release design approval is requested.

## Installation groups

Use these when recommending missing depth:

| Group | Covers | Skills |
|---|---|---|
| `production-system-thinking` | Whole-system decisions with domain change and verification depth | `system-architecture-harness`, `auth-access`, `api-contracts`, `data-storage`, `transactions-consistency`, `async-messaging`, `resilience-flow-control`, `security-privacy`, `production-operations`, `migration-evolution`, `quality-release`, `runtime-delivery` |
| `ai-system-thinking` | Governed AI-system decisions with surrounding backend and verification depth | `ai-agent-system-architecture`, `system-architecture-harness`, `auth-access`, `api-contracts`, `data-storage`, `async-messaging`, `resilience-flow-control`, `security-privacy`, `production-operations`, `quality-release`, `runtime-delivery` |
| `independent-architecture-review` | Independent evidence gate for an existing architecture | `architecture-review-gate` |
| `identity-boundary` | Identity, request contracts, cryptography, abuse controls, audit, and migration | `auth-access`, `api-contracts`, `security-privacy`, `resilience-flow-control`, `production-operations`, `migration-evolution`, `quality-release` |
| `transactional-workflow` | Authoritative state, outbox and jobs, retry controls, migration, and release evidence | `transactions-consistency`, `async-messaging`, `resilience-flow-control`, `data-storage`, `migration-evolution`, `production-operations`, `quality-release` |
| `repository-release-workflow` | Git topology, protected refs, CI candidate identity, immutable release versions, provenance, and release evidence | `git-workflows`, `runtime-delivery`, `quality-release`, `security-privacy`, `production-operations` |
| `skill-routing` | The routing entry point | `using-forge`, `think-forge` |

## Standalone policy

- **Available** — complete the safe local decision from installed material.
- **Missing companion** — name the missing depth, preserve every safety requirement, and give the exact technical ID or installation group.
- **Prohibited** — never claim an unavailable companion or reference was loaded, never invent evidence, and never weaken a blocker because companion depth is missing.
