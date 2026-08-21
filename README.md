# ArcForge

> Production architecture decisions your AI coding agent can explain, challenge, and prove.

**v0.4.1 · 17 portable Agent Skills · Claude Code, Codex, and compatible runtimes · MIT**

ArcForge gives your agent the part it usually skips: invariants, failure modes,
trust boundaries, recovery, rollout safety, and evidence. Describe what you want
in plain language and ArcForge works out which skill owns it, how deep to go, and
what proof the answer needs.

## Start here

**1. Install** every skill into the current project, for Claude Code and Codex:

~~~bash
npx --yes skills@1.5.22 add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -y
~~~

**2. Describe the problem** and let ArcForge choose the skills:

~~~text
Use using-forge. We are adding prepaid checkout: the card is charged up front,
inventory is finite so we cannot oversell, and the customer gets a receipt email.
Which skills own this, in what order, and what proof do we need?
~~~

**3. That is the whole setup.** `using-forge` names the owning skill for every
part of the request, picks the mode, pulls in only the companion skills this
request actually needs, puts them in a safe order, and starts the work.

Install globally with `-g`, or replace `'*'` with a single skill ID to install
just one. For a reviewed production source, clone a release tag or commit and use
that local checkout — see [Security](SECURITY.md).

## Two ways in

| Say this | What you get |
|---|---|
| `use using-forge` | Full routing: the owning skill for each part of the request, the mode, the companions, the order — then the work itself |
| `use think-forge` | The route only: which skill, which mode, what order, what is missing — then it stops. Nothing is opened, changed, or run |

Already know which skill you want? Name it directly — `use data-storage` — and
skip routing entirely.

## The four modes

Every design and domain skill runs in one of four modes. Name one, or let the
skill infer it from your request.

| Mode | Use it when you want |
|---|---|
| **Think** | Requirements, constraints, alternatives, decisions, and the validation path — before anything changes |
| **Review** | Findings and blockers for an existing proposal, repository, diff, or production state |
| **Change** | An approved decision applied, with contracts, safety, integrity, and rollback preserved |
| **Verify** | Tests, measurements, operational evidence, and an honest account of what is still at risk |

Think and Review can finish without touching your repository. **Change never
claims to be finished without Verify evidence**, and Verify labels every check it
could not run instead of assuming it passed.

## The skills

You type the ID: `/data-storage` in Claude Code, `$data-storage` in Codex, or
just name it in a sentence.

### Not sure which one? Start here

| Skill | Choose it for |
|---|---|
| `using-forge` | Picking the skill, the mode, the companions, and the order — then continuing into the work |
| `think-forge` | Answering which skill, which mode, and what order, then stopping |

### Whole systems, AI systems, independent review

| Skill | Choose it for |
|---|---|
| `system-architecture-harness` | Whole-system boundaries, workloads, invariants, scale, reliability, clients, platform governance |
| `ai-agent-system-architecture` | LLM, RAG, memory, model routing, tool use, agent authority, evaluation, latency, cost, rollout |
| `architecture-review-gate` | An independent evidence gate on an RFC, ADR, migration plan, AI design, or post-incident redesign |

### Backend domains

| Skill | Choose it for |
|---|---|
| `auth-access` | Login, recovery, sessions, OAuth/OIDC, MFA, API keys, permissions, account lifecycle, tenancy |
| `api-contracts` | Endpoints, validation, errors, pagination, versioning, webhooks, realtime, SDKs, CLIs |
| `data-storage` | Models, identifiers, money, indexes, files, search, lifecycle, provenance, reconciliation |
| `transactions-consistency` | Transactions, concurrency, idempotency, state machines, sagas, replication, sharding, ordering |
| `async-messaging` | Jobs, workers, schedules, queues, events, outbox and inbox, batch work, email, notifications |
| `resilience-flow-control` | Caches, rate limits, quotas, retries, timeouts, breakers, degradation, backpressure |
| `security-privacy` | Secrets, encryption, TLS and PKI, hashing, sensitive-data lifecycle, redaction, abuse defense, randomness |
| `production-operations` | Logs, metrics, tracing, health, audit, incidents, backup and restore, disaster recovery, regions, residency |
| `migration-evolution` | Schema changes, backfills, compatibility, synchronization, CDC, reindexing, cutover, legacy integration |
| `quality-release` | Test strategy, concurrency and failure evidence, load, performance, resource limits, release readiness |
| `runtime-delivery` | Bootstrap, configuration, pools, networking, shutdown, deployment gates, CI/CD, infrastructure |
| `git-workflows` | Branches, merges, rebases, conflicts, remotes, protected refs, tags, versions, release provenance, history rewrites, Git recovery |

Each skill has a short guide in [docs/skills/](docs/skills/): what it covers, when
to use it, what a run produces, and which skills it pairs with.

## Copy a prompt

### Not sure where to start

~~~text
Use think-forge. Our nightly backfill keeps dying halfway and leaves duplicate
rows. Which skills cover this, in which modes, and in what order? Route only.
~~~

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

### Git and releases

~~~text
Review the current repository and hosted state, then publish the approved release
without overwriting concurrent work or moving an existing tag. Bind the exact
candidate commit to current checks and the release tag. Use git-workflows in
Review, Change, and Verify modes.
~~~

## How skills work together

Real requests cross domains. Checkout is an invariant, a schema, a retry policy,
an email, and a readiness claim all at once. ArcForge marks companion skills by
relationship, so a request gets the depth it needs and nothing it does not:

| Relationship | Meaning |
|---|---|
| **Required** | The outcome cannot be completed safely without this domain |
| **Recommended** | It materially improves coverage, while the active skill keeps a safe local path |
| **Handoff** | It owns a separate decision that this work uncovered |
| **Optional depth** | It adds focused detail when you ask for it |

Order matters as much as coverage: the skill that owns an invariant decides
before anything derived from it, identity and secrets come before the flows that
use them, migration and delivery follow the target shape, and evidence closes the
work. `using-forge` handles that ordering for you.

## Common questions

**Do I have to pick a skill myself?** No. Say `use using-forge` and describe the
problem in your own words.

**Will it change my code?** Only in Change mode, and only after a decision is on
record. Think and Review can finish without touching your repository, and
`think-forge` never touches it at all.

**What if I only installed some of the skills?** ArcForge names the missing skill
by its exact ID and tells you what coverage you lose. It never pretends to have
read material it does not have, and it never drops a safety blocker because the
skill that owns it is absent.

**Can I use it outside Claude Code?** Yes. These are portable Agent Skills and
work in Codex and other compatible runtimes.

## What a good answer contains

- Requirements, constraints, assumptions, and invariants tied to each decision.
- Alternatives with explicit tradeoffs, and the options that were rejected.
- Failure modes, trust boundaries, operational ownership, and rollback paths.
- Critical blockers that stay visible regardless of any score or checklist.
- Validation evidence, unrun checks, residual risk, and concrete next steps.

ArcForge improves the structure and auditability of agent reasoning. Final
responsibility stays with the people who approve, implement, operate, secure, and
regulate the system.

## Learn more

- [Skill guides](docs/skills/) — what each skill covers, when to use it, and what it produces
- [Research and standards](docs/research-and-standards.md) — source and evidence discipline
- [Contributing](CONTRIBUTING.md) — repository conventions and review requirements
- [Security](SECURITY.md) — source pinning, permissions, and reporting
- [Changelog](CHANGELOG.md) — release history

## License

[MIT](LICENSE)
