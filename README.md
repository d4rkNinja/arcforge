# ArcForge

> Architecture and implementation skills that make AI agents think before they build.

**Current release: 0.3.0** · 14 portable skills · Built for Claude Code, Codex, and any Agent Skills-compatible runtime.

AI coding agents write code quickly. They are much less reliable at deciding what should be built, where durable state belongs, how a system fails, what it costs, or which trade-offs a team can safely operate. ArcForge gives agents structured workflows — expressed entirely as natural-language instructions — so those decisions become explicit, evidence-backed, and reviewable before implementation.

ArcForge ships skills in two layers:

1. **Architecture skills (3)** — design and review whole systems: requirements, boundaries, data ownership, failure, security, operations, and independent adversarial review.
2. **Backend implementation skills (11)** — load production engineering papers *before writing code* for a specific feature: authentication, caching, transactions, queues, multi-tenancy, migrations, and more.

Both layers are instruction-only. No scripts, no API keys, no vendor runtime — install and the agent model does the reasoning.

- [Install](#install) · [Choose a skill](#choose-a-skill) · [How naming works](#how-naming-works) · [See it in action](#see-it-in-action)

## Contents

- [Why ArcForge exists](#why-arcforge-exists)
- [The 14 skills](#the-14-skills)
- [How naming works](#how-naming-works)
- [Choose a skill](#choose-a-skill)
- [How the implementation skills work](#how-the-implementation-skills-work)
- [How the architecture skills work](#how-the-architecture-skills-work)
- [Install](#install)
- [See it in action](#see-it-in-action)
- [Skill package structure](#skill-package-structure)
- [Repository structure](#repository-structure)
- [The knowledge base behind the implementation skills](#the-knowledge-base-behind-the-implementation-skills)
- [Design principles](#design-principles)
- [What ArcForge is not](#what-arcforge-is-not)
- [Compatibility and honest limits](#compatibility-and-honest-limits)
- [Contributing](#contributing)
- [Standards](#standards)
- [Security](#security)
- [License](#license)

## Why ArcForge exists

An agent can produce a convincing first draft while still making the decisions that cause production failures:

- coding before requirements and non-goals are clear, or before hidden correctness rules are known;
- choosing databases, queues, caches, or microservices before modeling access patterns and invariants;
- storing money in floating point, retrying forever, or writing to two systems "atomically" in one transaction;
- enforcing authorization only in the UI or a gateway;
- treating a cache or model output as durable truth; assuming replication is backup;
- implementing password reset without reuse protection, rate limiting, or account-enumeration defenses;
- shipping a column rename without a compatibility window; claiming "tests pass" equals "production-ready."

The architecture layer makes those decisions part of a visible, challengeable workflow. The implementation layer puts a production checklist in front of the code: the rules, failure modes, security boundaries, migration gates, and verification evidence that experienced engineers apply and first drafts skip.

## The 14 skills

Every skill is a directory under `skills/` with a `SKILL.md` entry point. The table shows the human-facing display name, the stable ID (used for installation and invocation), and what it produces.

### Architecture layer

| Display name | Stable ID | Use it when | Primary result |
|---|---|---|---|
| Design Production Systems | `system-architecture-harness` | Designing or changing a production system, its boundaries, storage, scale, or reliability | An evidence-backed architecture specification with alternatives, ADRs, and implementation slices |
| Design AI & Agent Systems | `ai-agent-system-architecture` | Building LLM, RAG, memory, tool-use, or agent systems | A governed AI architecture with bounded authority, evaluation, and rollout gates |
| Review Software Architecture | `architecture-review-gate` | Independently reviewing an architecture, RFC, migration, incident, or release proposal | A five-gate evidence vector, findings, blockers, verdict, and approval conditions |

### Implementation layer

Each implementation skill routes the task to production papers, forces the pre-implementation questions to be answered, and turns every MUST/SHOULD/AVOID/NEVER rule into a decision, a test, or a documented exception — before code is written.

| Display name | Stable ID | Covers | Papers |
|---|---|---|---:|
| Implement Auth & Access Control | `auth-access` | login, password reset, sessions, tokens, OAuth, MFA, API keys, RBAC/ABAC, multi-tenancy, admin ops | 11 |
| Implement API & Client Contracts | `api-contracts` | endpoints, validation, error models, pagination, versioning, webhooks, realtime, SDKs/CLIs | 13 |
| Implement Data & Storage | `data-storage` | schemas, identifiers, money, time, constraints, indexes, soft delete, files, search, lifecycle | 19 |
| Implement Transactions & Consistency | `transactions-consistency` | isolation, locking, state machines, idempotency, sagas, replication, sharding, distributed locks | 13 |
| Implement Async Jobs & Messaging | `async-messaging` | background jobs, cron, queues, events, outbox/inbox, batch, dedup, email, notifications | 10 |
| Implement Resilience & Flow Control | `resilience-flow-control` | caching, rate limiting, quotas, retries, timeouts, circuit breakers, backpressure | 10 |
| Implement Security & Privacy | `security-privacy` | secrets, crypto, TLS, sensitive-data lifecycle, redaction, abuse protection, randomness | 10 |
| Implement Observability & Operations | `production-operations` | logging, metrics, tracing, health, audit, runbooks, backup/restore, DR, multi-region | 16 |
| Implement Migrations & Evolution | `migration-evolution` | schema change, backfills, contract evolution, CDC, zero-downtime, feature cutover, legacy | 11 |
| Verify Quality & Release Readiness | `quality-release` | test strategy, concurrency/failure/load evidence, performance, release checklist | 10 |
| Implement Runtime & Delivery | `runtime-delivery` | project foundations, config, connection pools, shutdown, deploy ordering, CI/CD | 11 |

## How naming works

- **Display name** — what you see in agent UIs (for example, *Implement Auth & Access Control*).
- **Stable ID** — the directory name and frontmatter `name`, used everywhere else: installation (`--skill auth-access`), Claude Code (`/auth-access`), Codex (`$auth-access`), and cross-references between skills.

The three architecture skills keep their original IDs for backward compatibility; the eleven implementation skill IDs are name-descriptive with no shared prefix — they read naturally in commands (`/transactions-consistency`, `/async-messaging`).

Skills cross-reference each other by ID in their descriptions and boundary maps, so an agent implementing "checkout" knows to combine `transactions-consistency` with `async-messaging` rather than guessing.

## Choose a skill

| Your task | Skill to use |
|---|---|
| Design a new system, migration, or scaling change | `system-architecture-harness` |
| Build an AI/agent feature or platform | `ai-agent-system-architecture` |
| Review an architecture, RFC, or post-incident redesign | `architecture-review-gate` |
| Implement or change a specific backend feature | the matching implementation skill from the table above |
| Decide whether a change is ready to ship | `quality-release` (plus `architecture-review-gate` for formal approval) |

If a task spans domains, activate every matching skill: "implement checkout" needs `transactions-consistency` and `async-messaging` together. Each skill's **Boundary Map** section names its common co-activations.

## How the implementation skills work

Every implementation skill follows the same shape:

1. **Route** — a table maps the task ("password reset", "add caching", "rename a column") to its primary paper(s).
2. **Read** — the paper is loaded from the skill's `references/papers/` before any code.
3. **Answer** — the paper's *Questions that must be answered before implementation* are answered, or each open point is labeled as an assumption with its design impact.
4. **Inspect** — when changing an existing system, the paper's *Existing-codebase checks* run first: map every entry point, constraint, and bypass path.
5. **Map rules to decisions** — each applicable MUST/SHOULD/AVOID/NEVER becomes a decision with an enforcement point and a test; nothing is silently downgraded.
6. **Verify** — the paper's verification checklist becomes the test plan, and the skill's `## Stop Conditions` list halts the work if a rule lacks a decision, test, or documented exception.

Each skill also carries a worked example in `examples/` that calibrates the expected output, and each `agents/openai.yaml` provides Codex display metadata (optional, isolated, ignored by Claude Code).

## How the architecture skills work

The shared lifecycle is Discover → Frame → Quantify → Model → Compare → Design → Challenge → Verify → Record. Decisions trace to requirements, invariants, risks, or constraints; every critical claim has a validation path. The three skills enforce hard gates — for example:

- no architecture decision without a motivating requirement, an alternative, a stated trade-off, and a validation path;
- no "scales to X" claim without a capacity model; no invariant without an enforcement point;
- replication is not backup; "internal network" is not an authorization model;
- the model proposes, the harness constrains — AI output never owns permissions or durable truth;
- review verdicts keep a five-gate evidence vector, and no aggregate score can waive a correctness, security, recovery, tenancy, overload, migration, or evidence blocker.

See each skill's `SKILL.md` for its full workflow, `references/` for depth, `assets/` for reusable templates, and `examples/` for worked calibration artifacts.

## Install

Project-scoped installation for Claude Code and Codex:

~~~bash
npx --yes skills add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -y
~~~

Install globally instead:

~~~bash
npx --yes skills add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -g -y
~~~

Install one skill only:

~~~bash
npx --yes skills add d4rkNinja/arcforge --skill auth-access -a claude-code -a codex --copy -y
~~~

List available skills:

~~~bash
npx --yes skills add d4rkNinja/arcforge --list
~~~

After installation, invoke by stable ID: `/auth-access` in Claude Code, `$auth-access` in Codex, or simply name the skill in a prompt.

## See it in action

Implementation example:

~~~text
Implement password reset for our API: email link, single use,
and it must not let attackers enumerate accounts. Use auth-access.
~~~

A good run consults the authentication/sessions papers, states reset-token lifetime, reuse, and storage rules, defines lockout and enumeration defenses, and lists the tests that prove each rule — before writing code.

Architecture example:

~~~text
Design a multi-tenant order platform with finite inventory, prepaid
checkout, tenant-scoped authorization, asynchronous fulfillment events,
and a regional recovery target. Compare a modular monolith with
distributed alternatives. Use system-architecture-harness.
~~~

Review example:

~~~text
Review this architecture RFC for production readiness. Reconstruct the
data and trust boundaries, challenge the capacity and recovery claims,
and return blockers, evidence gaps, and approval conditions.
Use architecture-review-gate.
~~~

Each implementation skill's `examples/` folder contains one full worked example showing the expected shape and depth of a run.

## Skill package structure

Every skill follows the same portable layout:

~~~text
skills/<stable-id>/
├── SKILL.md            Core workflow, routing, output contract, stop conditions
├── references/         Deep material loaded on demand
│   └── papers/         (implementation skills) production papers
├── examples/           Worked calibration examples
├── assets/             Reusable templates (architecture skills)
└── agents/
    └── openai.yaml     Optional Codex UI metadata
~~~

This is progressive disclosure: only `name` and `description` are read at discovery, the `SKILL.md` loads on activation, and references load only when the task needs them. Primary `SKILL.md` files stay well under the 500-line specification limit.

## Repository structure

~~~text
skills/                                14 portable skills (all instruction-only)
├── system-architecture-harness/       + 6 boundary/code-architecture papers
├── ai-agent-system-architecture/      + 6 AI-backend papers
├── architecture-review-gate/
├── auth-access/  api-contracts/  data-storage/  transactions-consistency/
├── async-messaging/  resilience-flow-control/  security-privacy/
└── production-operations/  migration-evolution/  quality-release/  runtime-delivery/

backend-engineering-knowledge-base/    Canonical 146-paper corpus + validator + packager
evals/                                 36 runtime-neutral behavioral cases
docs/                                  Standards and provenance map
.github/                               Portable skill discovery CI
~~~

## The knowledge base behind the implementation skills

The eleven implementation skills are built on a canonical corpus of **146 production papers** (roughly 923,000 words, 1,881 canonical subtopics) organized in three layers: primitives (reusable reasoning units), systems (subsystems with lifecycle and ownership), and cross-cutting controls (security, reliability, operations).

Each paper covers the hidden production work of its topic: correctness model and invariants, architecture trade-offs, ownership and lifecycle, subtopic-by-subtopic rules with failure modes, normative MUST/SHOULD/MAY/AVOID/NEVER lists, testing requirements, AI-agent failure modes, pre-implementation questions, existing-codebase checks, and a scoped bibliography.

Skills receive **restructured copies**: the packager (`backend-engineering-knowledge-base/tools/package_papers.py`) removes corpus bookkeeping, deduplicates generator boilerplate, collapses fully-templated subtopics into a compact "Default obligations" list, and front-loads the pre-implementation questions — about 31% smaller per paper with every domain-specific rule preserved. Same-skill paper links stay relative so each installed skill is self-contained; cross-skill links become explicit skill pointers. The canonical corpus remains in the repository and is validated by `tools/validate_corpus.py`.

## Design principles

- **Evidence before confidence** — claims need a validation path; assumptions are labeled, not hidden.
- **Requirements before topology** — no technology choice before workload, invariants, and ownership are known; the smallest architecture that satisfies the requirements is the default.
- **Ownership before replication** — every piece of durable state has a named source of truth; derived stores have rebuild paths.
- **Correctness has an enforcement point** — invariants are protected by constraints, transactions, conditional writes, or policy — not by hope.
- **Resources are bounded** — queues, retries, fan-out, concurrency, tokens, and spend have hard limits.
- **Authorization happens at the action boundary** — enforced where state is read or changed, never only at a gateway.
- **Failure and recovery are designed** — timeouts, degraded modes, RTO/RPO, restore drills, and rollback paths exist before launch, and are rehearsed, not assumed.
- **AI proposals are not authority** — model output is separated from policy, permissions, durable state, verification, approval, and audit.
- **No score waives a blocker** — critical failures cannot be averaged away.

## What ArcForge is not

- not a fixed microservices blueprint or a preferred technology list;
- not an interview cheat sheet or a generic "best practices" prompt;
- not a reason to introduce distributed systems before evidence justifies them;
- not a replacement for engineering judgment, security testing, legal advice, or domain approval;
- not a guarantee that agent-generated designs or code are correct — it is a structured process for reaching, recording, and challenging decisions.

## Compatibility and honest limits

**Verified in this repository:** portable Agent Skills packaging (shared frontmatter only, optional isolated Codex metadata), progressive disclosure, CI-checked Skills CLI discovery, and explicit installation into Claude Code and Codex skill directories.

**Not claimed:** ArcForge does not claim every harness discovers every skill automatically, that installation guarantees correct output, or that behavioral quality is proven by packaging. The 36 behavioral cases in `evals/` are prompts and review expectations, not executable tests — they establish evidence only when run repeatedly with a named target model and independently reviewed. Model outputs vary by model, version, context, and run.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) first. The rules that matter most:

- one skill per directory, directory name equals frontmatter `name`, primary `SKILL.md` ≤ 500 lines;
- `## Output Contract` and `## Stop Conditions` headings are mandatory in every skill;
- add or update a runtime-neutral behavioral case in `evals/cases.json` before changing observable skill behavior, and run affected cases with an approved target model;
- implementation papers are changed in the canonical corpus, then re-packaged — never hand-edited inside skills;
- report honestly what was verified and what was not.

Maintainers check discovery with `npx skills add . --list` when network access is available.

## Standards

ArcForge follows the portable [Agent Skills specification](https://agentskills.io/specification) and distributes through the [Skills CLI](https://github.com/vercel-labs/skills). Architecture references map to the [C4 model](https://c4model.com/), [Architecture Decision Records](https://adr.github.io/), [Google SRE guidance](https://sre.google/sre-book/service-level-objectives/), [NIST Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final), [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework), and [OWASP GenAI guidance](https://owasp.org/www-project-top-10-for-large-language-model-applications/), adapted to the actual system rather than treated as certification. Full provenance: [docs/research-and-standards.md](docs/research-and-standards.md).

## Security

See [SECURITY.md](SECURITY.md). ArcForge skills are instructions and reference material, not a security certification; the consuming runtime and its operators remain responsible for tool permissions, data access, credentials, approvals, and incident response.

## License

Released under the [MIT License](LICENSE).
