# ArcForge

> Architecture skills that make AI agents think before they build.

**Current release: 0.2.0 — evidence-led production, AI-agent, and architecture-review skills.**

AI coding agents can produce implementation quickly. They are less reliable at deciding what should be built, where durable state belongs, how a system fails, what it costs, or which trade-offs a team can safely operate.

ArcForge gives coding agents structured workflows for making those decisions explicit before implementation. It is for engineers, architects, and teams designing production software, AI systems, migrations, and architecture reviews.

The result is not a fashionable diagram or a technology list. It is a set of decisions that can be traced to requirements, invariants, risks, constraints, owners, validation evidence, and reversal triggers.

[Install all skills](#install-all-skills) · [Choose a skill](#which-skill-should-i-use) · [Read the examples](#examples)

## Contents

- [Why ArcForge?](#why-arcforge)
- [What ArcForge does](#what-arcforge-does)
- [How it works](#how-it-works)
- [What changed in 0.2.0](#what-changed-in-020)
- [Skills](#skills)
- [Research mode](#research-mode)
- [Which skill should I use?](#which-skill-should-i-use)
- [Quick start](#quick-start)
- [Examples](#examples)
- [Without ArcForge and With ArcForge](#without-arcforge-and-with-arcforge)
- [Architecture philosophy](#architecture-philosophy)
- [Design principles](#design-principles)
- [What ArcForge is not](#what-arcforge-is-not)
- [When to use ArcForge](#when-to-use-arcforge)
- [How the skills are structured](#how-the-skills-are-structured)
- [Repository structure](#repository-structure)
- [Compatibility](#compatibility)
- [Contributing](#contributing)
- [Standards](#standards)
- [Security](#security)
- [License](#license)

## Why ArcForge?

### AI can generate code. Architecture is the harder problem.

An agent can produce a convincing first draft while still making the decisions that cause production failures:

- coding before the requirements and non-goals are clear;
- choosing databases, queues, caches, or microservices before modeling access patterns and invariants;
- calling a system “high scale” without a workload, capacity, or bottleneck model;
- introducing distributed coordination before independent ownership or failure isolation justifies it;
- leaving retries, fan-out, queues, connection pools, or concurrency unbounded;
- treating a cache, search index, replica, or model output as durable truth;
- assuming replication is backup or that a backup is recovery evidence;
- enforcing authorization only in a UI or gateway;
- giving an AI system broad tools without deterministic policy, scoped permissions, approval, or audit;
- documenting a happy path without failure, recovery, migration, or rollback behavior;
- drawing diagrams that show components but not decisions, ownership, or consequences.

ArcForge makes those questions part of the architecture workflow. It helps an agent separate evidence from assumptions, quantify the workload, model correctness and ownership, compare alternatives, challenge failure and security boundaries, and finish with validation and implementation slices.

## What ArcForge does

ArcForge turns an architecture request into a chain of reviewable decisions:

~~~text
Requirements
    ↓
Constraints and invariants
    ↓
Workload and capacity model
    ↓
Data ownership and state boundaries
    ↓
Architecture options
    ↓
Trade-off analysis
    ↓
Failure, security, and abuse review
    ↓
Operations, rollout, and recovery
    ↓
Validation and implementation slices
~~~

Depending on the mode and skill, the work may produce:

- confirmed facts, estimates, assumptions, constraints, and non-goals;
- functional requirements and measurable architecturally significant requirements;
- workload estimates, capacity calculations, sensitivity ranges, and bottleneck hypotheses;
- invariants, state machines, consistency rules, and enforcement points;
- service or module boundaries, ownership, trust boundaries, and dependency rules;
- API, event, workflow, and error contracts with compatibility and idempotency semantics;
- alternatives, consequences, ADRs, reversal triggers, and unresolved risks;
- failure modes, degraded behavior, security controls, privacy lifecycle, and abuse cases;
- SLIs, SLOs, telemetry, runbooks, cost controls, rollout, rollback, and recovery plans;
- validation experiments, load or restore drills, evaluation gates, and smallest safe implementation slices.

ArcForge does not ask an agent to “design the system” in one leap. It makes the reasoning visible enough for another engineer to challenge it.

## How it works

The shared lifecycle is:

~~~mermaid
flowchart LR
    A["Discover"] --> B["Frame"]
    B --> C["Quantify"]
    C --> D["Model"]
    D --> E["Compare"]
    E --> F["Design"]
    F --> G["Challenge"]
    G --> H["Verify"]
    H --> I["Record"]
~~~

| Stage | Purpose |
| --- | --- |
| **Discover** | Establish the problem, actors, evidence, current state, and decision horizon. |
| **Frame** | Define outcomes, scope, non-goals, constraints, and architecturally significant requirements. |
| **Quantify** | Put units, ranges, peaks, growth, dependency limits, and cost around the workload. |
| **Model** | Make invariants, states, ownership, consistency, trust, and failure boundaries explicit. |
| **Compare** | Evaluate the smallest viable architecture against realistic alternatives and trade-offs. |
| **Design** | Specify data, interfaces, workflows, operations, security, delivery, and recovery. |
| **Challenge** | Look for correctness defects, evidence gaps, unbounded resources, unsafe authority, and unrecoverable change. |
| **Verify** | Define tests, experiments, drills, evaluation evidence, acceptance thresholds, and release gates. |
| **Record** | Capture decisions, risks, owners, reversal triggers, and implementation slices. |

The workflow can move backward when new evidence invalidates an assumption. It should not silently skip a decision gate.

## What changed in 0.2.0

ArcForge is now entirely instruction- and reference-led. Each skill is expressed through `SKILL.md`, focused technical references, reusable Markdown assets, and worked examples. There is no bundled executable evaluation or package logic.

Architecture review now uses a five-gate evidence vector generated from the decision,
requirements, state, failure impact, operations, lifecycle obligations, and supplied
evidence. It freezes the review frame before assessment, keeps every dimension visible,
and performs an adversarial second pass. A numeric summary is optional only when its
decision purpose, derivation, uncertainty, and sensitivity are defensible; it never
grants approval.

The supplied architecture research manuscript also expanded the skills with code and
runtime decisions, proportional assurance, client/offline architecture, platform and
repository governance, architecture metric controls, structural incident review, and
classical reliability obligations for AI systems. Critical correctness, security,
tenancy, recovery, overload, migration, and AI-authority failures remain non-waivable.

## Skills

The names shown in agent interfaces are human-facing display names. Each display name
maps to a stable skill ID used for installation, links, and invocation; keep the ID when
using a command or `$skill-id` invocation.

| Display name | Stable ID | Use it for | Primary result |
| --- | --- | --- | --- |
| [Design Production Systems](skills/system-architecture-harness/SKILL.md) | `system-architecture-harness` | New or changing production software architecture | An evidence-backed architecture specification and implementation handoff |
| [Design AI & Agent Systems](skills/ai-agent-system-architecture/SKILL.md) | `ai-agent-system-architecture` | AI, LLM, RAG, memory, tool, model-serving, or agent systems | A governed AI-system architecture with bounded authority, evaluation, and rollout gates |
| [Review Software Architecture](skills/architecture-review-gate/SKILL.md) | `architecture-review-gate` | Independent review of an existing architecture, incident, metric program, or release proposal | A five-gate evidence vector, findings, evidence gaps, verdict, blockers, and approval conditions |

### Design Production Systems (`system-architecture-harness`)

Use this skill when designing a new backend or production system, decomposing an existing system, planning a major feature, changing storage, choosing service boundaries, scaling a workload, introducing asynchronous processing, or preparing reliability, security, migration, or production-readiness work. Its stable ID is `system-architecture-harness`; use that ID in installation commands and `$system-architecture-harness` invocations.

It covers modular monoliths and distributed systems, requirements and capacity, data ownership and consistency, APIs and events, workflows, overload, failure and disaster recovery, security and privacy, observability, delivery, cost, alternatives, risks, validation, and implementation slices. Paper-derived references add code and information-hiding boundaries, language/runtime and assurance decisions, browser/mobile/desktop and offline/local-first architecture, platform engineering, repository/build topology, technical-debt and rewrite gates, migration sequencing, and governed metric vectors. It defaults to the smallest architecture that satisfies the requirements; a modular monolith remains the default when distribution has no evidence behind it.

Its standard output is a complete architecture specification, with narrower modes for exploration, review, scale, migration, or incident-driven redesign.

Read the [worked order-platform example](skills/system-architecture-harness/examples/worked-example-order-platform.md) for a concrete end-to-end artifact, or the [contextual architecture comparison](skills/system-architecture-harness/examples/contextual-architecture-comparison.md) to see the same framework produce different designs for a small SaaS product, payment worker, and offline collaborative client.

### Design AI & Agent Systems (`ai-agent-system-architecture`)

AI systems add decisions that ordinary backend architecture does not settle. The model is probabilistic; policy, permissions, durable state, verification, evaluation, and approval need deterministic boundaries around it.

Use this skill for LLM features, RAG, model routing, memory, tool use, autonomous or multi-agent workflows, long-running jobs, AI actions affecting customers or systems, and AI quality, safety, cost, observability, or release planning. Its stable ID is `ai-agent-system-architecture`; use that ID in installation commands and `$ai-agent-system-architecture` invocations.

It covers:

- task contracts, risk classes, non-AI alternatives, and measurable quality;
- control-plane decomposition for requests, context, policy, models, orchestration, tools, memory, verification, and human control;
- retrieval authorization, provenance, freshness, deletion, no-result behavior, and grounding;
- typed model output, route compatibility, fallback behavior, versioning, and rollback;
- capability-scoped tools, identity, tenant propagation, approval, idempotency, sandboxing, and audit;
- bounded agent depth, turns, tool calls, tokens, duration, cost, fan-out, cancellation, and termination;
- a strongest-single-agent baseline and measured justification before adding a multi-agent topology;
- authoritative versus derived state, unknown remote outcomes, queues, cache identity, restore-tested recovery, mixed-version rollout, and supply-chain provenance;
- non-authoritative model summaries, policy-mediated gateways with no unsafe bypass, attenuated delegation, and ephemeral per-task credentials;
- prompt injection, data leakage, memory poisoning, evaluation integrity, provider failure, and denial-of-wallet risks;
- golden, adversarial, trajectory, deterministic, human, reliability, and online evaluation evidence.

The governing rule is simple: the model proposes; the surrounding harness constrains, verifies, records, and decides what may happen next. See the [governed support-agent example](skills/ai-agent-system-architecture/examples/governed-support-agent.md).

### Review Software Architecture (`architecture-review-gate`)

Use this skill when an architecture already exists and needs an independent challenge: RFCs, ADRs, diagrams, migrations, scaling plans, production-readiness proposals, AI architectures, or post-incident redesigns. Its stable ID is `architecture-review-gate`; use that ID in installation commands and `$architecture-review-gate` invocations.

It reconstructs the design from supplied evidence, traces requirements to decisions, tests correctness and ownership, challenges scale and overload, walks failure and recovery paths, checks security and tenancy, and reviews delivery, migration, operations, and cost. It distinguishes defects from evidence gaps, risks, and preferences rather than treating every disagreement as a redesign.

The review result separates:

- critical findings and high/medium findings;
- five gates for problem/fitness, state/boundaries, failure/assurance, delivery/operation, and economics/complexity/evolution;
- requirement-to-decision and Complexity Ledger gaps;
- correctness, data, workflow, scale, recovery, security, and operations findings;
- source claims, reviewer inferences, evidence quality, counter-evidence, and missing evidence;
- incident causality that separates an initiating trigger from structural enabling conditions;
- governed architecture metrics that remain a vector and never rank individual engineers;
- confidence, model disclosure, verdict, and explicit approval conditions.

The review frame is created from the actual decision and frozen before the proposal is judged. The model must explain why each dimension applies, what condition it protects, what evidence maturity is required, and why any dimension is excluded. Optional numeric summaries remain secondary, transparent, and non-authorizing.

> No aggregate or AI-generated summary overrides a correctness, security, recovery, tenancy, overload, migration, or evidence blocker.

Read the [contextual evidence vector](skills/architecture-review-gate/references/01-contextual-ai-review-rubric.md), [calibration guide](skills/architecture-review-gate/references/04-rubric-calibration-guide.md), [fitness/incident/metrics guide](skills/architecture-review-gate/references/05-fitness-gates-incidents-and-metrics.md), and [worked review example](skills/architecture-review-gate/examples/contextual-review-example.md).

Use the [review report template](skills/architecture-review-gate/assets/architecture-review-report-template.md) when a file artifact is needed.

## Research mode

Research mode is part of [Design Production Systems](skills/system-architecture-harness/SKILL.md)
(`system-architecture-harness`). Use it when a paper, source corpus, incident set,
architecture claim, or conflicting technical guidance could change a design decision.
It keeps each conclusion claim-centric: record the atomic claim, source type and
context, supported finding, limitations or counter-evidence, applicable and failure
context, qualitative confidence, conditional architecture implication, and next
validation step. Correlation is not causation, and a vendor claim, case study, paper,
or isolated incident is not universal evidence.

Research mode also requires a dimensional complexity ledger for each added mechanism.
Keep concepts/state/protocols, operational responsibility, failure modes, knowledge,
dependencies, performance, security/privacy, cost, reversibility, and lifetime visible
instead of collapsing them into a synthetic score. Use the [evidence and complexity
reference](skills/system-architecture-harness/references/15-evidence-complexity-and-research.md),
[Architecture Evidence Map](skills/system-architecture-harness/assets/architecture-evidence-map-template.md),
[Complexity Ledger](skills/system-architecture-harness/assets/complexity-ledger-template.md),
and [worked complexity example](skills/system-architecture-harness/examples/complexity-ledger-example.md).

The broader paper-derived guidance is progressively loaded through [code, runtime, and
assurance decisions](skills/system-architecture-harness/references/16-code-runtime-and-assurance.md),
[client and platform architecture](skills/system-architecture-harness/references/17-client-platform-architecture.md),
and [platform, governance, economics, and evolution](skills/system-architecture-harness/references/18-platform-governance-and-evolution.md).
The manuscript is treated as user-supplied research input because author/title/publication
metadata was not present in the supplied text; individual cited sources are verified and
scoped separately before they are used as external evidence.

See the [research and standards map](docs/research-and-standards.md) and [source map](skills/system-architecture-harness/references/14-source-map.md) for provenance, source classification, and scope limits.

Research does not replace the normal architecture gates. Route the resulting conditional
recommendation back through requirements, invariants, ownership, failure, security,
operations, cost, and validation review.

## Which skill should I use?

| Situation | Start here |
| --- | --- |
| Designing a new production system or major backend capability | Design Production Systems (`system-architecture-harness`) |
| Planning a storage, service-boundary, scaling, reliability, or migration change | Design Production Systems (`system-architecture-harness`) |
| Building an LLM, RAG, memory, tool, or agent system | Design AI & Agent Systems (`ai-agent-system-architecture`) |
| Reviewing an existing architecture, RFC, ADR, diagram, or migration | Review Software Architecture (`architecture-review-gate`) |
| Reviewing an AI or agent architecture | Review Software Architecture (`architecture-review-gate`) plus Design AI & Agent Systems (`ai-agent-system-architecture`) |
| Designing a non-AI system that includes an AI subsystem | Design Production Systems (`system-architecture-harness`) plus Design AI & Agent Systems (`ai-agent-system-architecture`) |

Use the review gate as an independent challenge. It does not silently rewrite the architecture or implement fixes unless the user asks for that next step.

## Quick start

### Install all skills

For a project-scoped installation targeting Claude Code and Codex:

~~~bash
npx --yes skills add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -y
~~~

Run it from the project where the skills should be available. `--copy` installs copies rather than symlinks, and `-a` selects the agent directories.

### Install globally

To make the skills available across projects:

~~~bash
npx --yes skills add d4rkNinja/arcforge --skill '*' -a claude-code -a codex --copy -g -y
npx skills ls -g -a claude-code -a codex
~~~

### Install one skill

Install only the workflow you need:

~~~bash
npx --yes skills add d4rkNinja/arcforge --skill system-architecture-harness -a claude-code -a codex --copy -y
~~~

Replace `system-architecture-harness` with `ai-agent-system-architecture` or `architecture-review-gate` as needed.

### List available skills

~~~bash
npx --yes skills add d4rkNinja/arcforge --list
~~~

### Invoke a skill

After installation, invoke the skill by its name in the target agent:

~~~text
Claude Code
/system-architecture-harness

Codex
$system-architecture-harness
~~~

The same names apply to the other two skills. In a normal prompt, you can also be explicit:

~~~text
Design the architecture for a multi-tenant commerce backend.
Use the system-architecture-harness skill. State assumptions before choosing topology.
~~~

## 30-second quick start

Install ArcForge, then give your agent a bounded architecture problem:

~~~text
Design a multi-tenant commerce backend for 100,000 businesses.
We need order creation, inventory reservation, asynchronous notifications,
tenant isolation, and a migration path from the current monolith.

Use system-architecture-harness. Start by identifying the highest-impact
unknowns, then quantify the workload before recommending services or storage.
~~~

A useful run should make the agent investigate workload shape, invariants, data ownership, consistency, failure behavior, authorization, recovery objectives, cost, alternatives, and validation evidence before it hands off implementation slices.

## Examples

### Production backend

~~~text
Design a multi-tenant order platform with finite inventory, prepaid checkout,
tenant-scoped authorization, asynchronous fulfillment events, and a regional
recovery target. Compare a modular monolith with distributed alternatives.
Use system-architecture-harness.
~~~

### AI agent system

~~~text
Design an AI research agent that can search approved sources, cite evidence,
maintain bounded task memory, and ask for approval before any external write.
Define retrieval isolation, tool contracts, token and cost limits, evaluation,
fallback behavior, and rollback.
Use ai-agent-system-architecture.
~~~

### Architecture review

~~~text
Review this architecture RFC for production readiness. Reconstruct the data
and trust boundaries, challenge the capacity and recovery claims, inspect
authorization and migration safety, and return blockers, evidence gaps,
and approval conditions. Generate and freeze a five-gate evidence vector before
assessing the proposal, then report evidence quality and model uncertainty.
Use architecture-review-gate.
~~~

## Without ArcForge and With ArcForge

Without an architecture workflow, a design can jump from a vague requirement to a topology:

~~~text
User → API Gateway → Microservices → Kafka → Redis → MongoDB
~~~

The explanation may stop at:

~~~text
“We’ll use Kafka for scalability.”
~~~

With ArcForge, the agent establishes or asks about the decisions that make the topology meaningful:

~~~text
Peak requests/sec?
Read/write ratio and burst shape?
Consistency and freshness requirements?
What data loss is acceptable?
RTO and RPO by journey?
Which component owns each invariant and source of truth?
How are tenants isolated at every data boundary?
What is the expected fan-out and retry amplification?
What happens when the queue, cache, database, or provider is unavailable?
What workload or ownership need actually justifies Kafka or microservices?
How will the claim be measured, restored, migrated, and reversed?
~~~

The point is not to reject a particular technology. It is to make architecture choices follow constraints and evidence.

## Architecture philosophy

### Requirements before topology

Do not choose microservices, event-driven architecture, databases, queues, or caches before understanding the requirements, invariants, access patterns, and constraints.

### Quantify before scaling

“High scale” is not a workload. Use average and peak traffic, burst duration, concurrency, payloads, fan-out, skew, retention, dependency quotas, and cost ranges.

### Ownership before replication

Name the source of truth and accountable owner before creating replicas, caches, search indexes, event projections, or AI memories. Derived state needs freshness, invalidation, rebuild, and repair semantics.

### Failure before production

Every dependency introduces failure modes. Design deadlines, bounded retries, degraded behavior, containment, recovery objectives, restore evidence, and operator repair before calling a system production-ready.

### Reversibility matters

Major decisions should state migration, rollback, roll-forward, containment, and the measurable trigger that would cause the decision to be revisited.

### Evidence over architectural fashion

Technology popularity is not evidence. A new component earns its place by solving a named requirement, invariant, risk, or constraint with an understood operational cost.

## Design principles

> Evidence before confidence.

| Principle | What it means in practice |
| --- | --- |
| Decisions are traceable | Every material choice points to a requirement, invariant, risk, or constraint, plus an alternative and a validation path. |
| Durable truth has an owner | Authoritative state, immutable facts, derived views, caches, and memories are named separately. |
| Resources are bounded | Queues, retries, fan-out, concurrency, connections, payloads, retention, tokens, and spend have hard limits. |
| Correctness has an enforcement point | Invariants are protected by transactions, constraints, conditional writes, serialized ownership, policy, or explicit reconciliation. |
| Authorization happens at the action boundary | Identity, tenant, resource, and action permissions are enforced where state is read or changed, not only at a gateway. |
| Failure and recovery are designed intentionally | Timeouts, degraded modes, RTO/RPO, restore order, failover authority, reconciliation, and drills are part of the design. |
| Observability precedes production | User-journey SLIs, SLOs, alerts, runbooks, ownership, and useful evidence exist before a reliability claim is treated as fact. |
| Rollback is a design concern | Code, schema, event, data, and model changes define compatibility windows and valid rollback or roll-forward paths. |
| AI proposals are not authority | Model output is separated from policy, permissions, durable state, verification, approval, and audit. |
| Vectors do not waive blockers | Strong evidence in one dimension—and any optional numeric summary—cannot override a correctness, security, recovery, or evidence failure. |

## What ArcForge is not

ArcForge is not:

- a fixed microservices blueprint;
- a list of preferred databases, queues, cloud vendors, or model providers;
- a system-design interview cheat sheet;
- a generic “best practices” prompt;
- a reason to introduce distributed systems before the workload or ownership requires them;
- a replacement for engineering judgment, security testing, legal advice, compliance review, or domain approval;
- a guarantee that an agent-generated architecture is correct or production-ready.

ArcForge is a structured process for reaching, recording, and challenging architecture decisions.

## When to use ArcForge

Use ArcForge when you are:

- beginning a new production system or major subsystem;
- changing storage, consistency, service boundaries, or data ownership;
- moving from a monolith to services or introducing asynchronous processing;
- designing for high availability, regional recovery, or significant scale;
- creating an AI agent platform or designing memory, RAG, model routing, or tool execution;
- planning a migration, rollout, rollback, or production-readiness gate;
- reviewing an RFC, ADR, diagram, post-incident redesign, or existing architecture.

You probably do not need the full workflow for a trivial UI change, a small isolated bug fix, or a refactor with no architectural consequences. Use judgment; the goal is disciplined architecture work, not ceremony on every prompt.

## Representative output

ArcForge outputs vary by skill and operating mode. A compact architecture decision may look like this:

~~~markdown
### Decision: asynchronous order processing

**Requirement**
Order acceptance must stay within the user-facing latency budget while
notifications and analytics may arrive later.

**Options**
1. Keep every side effect synchronous.
2. Commit authoritative order state locally, then publish through an outbox.
3. Defer the entire order to a workflow queue.

**Decision**
Commit the order and its invariants in the authoritative transaction, then
publish side effects through a transactional outbox and idempotent consumers.

**Why**
The side effects are not part of the acceptance invariant, and the outbox
avoids an uncoordinated database-plus-broker dual write.

**Failure modes**
Relay outage, duplicate publication, consumer lag, poison messages, and
replay behavior are bounded and observable.

**Validation**
Exercise lost responses, duplicate events, broker outage, backlog drain, and
restore/reconciliation before the relevant release gate.

**Rollback or reversal trigger**
Revisit the decision if a downstream effect becomes legally atomic with order
acceptance or measured relay capacity cannot meet its lag objective.
~~~

This is a representative shape, not a promise that every run produces the same wording. The bundled [architecture specification](skills/system-architecture-harness/assets/architecture-spec-template.md), [ADR](skills/system-architecture-harness/assets/adr-template.md), [AI system specification](skills/ai-agent-system-architecture/assets/ai-system-spec-template.md), and [review report](skills/architecture-review-gate/assets/architecture-review-report-template.md) templates show the available artifact structures.

## How the skills are structured

The primary entrypoint is intentionally small enough to load first:

~~~text
<skill>/
├── SKILL.md
│   Core workflow, decision gates, output contract, and stop conditions
├── references/
│   Deep technical guidance loaded only when the task needs it
├── assets/
│   Reusable specifications, ADRs, contracts, checklists, and templates
├── examples/
│   Worked architecture examples where included
└── agents/
    Optional agent-facing metadata, including Codex display information
~~~

This is progressive disclosure for agents: load the core workflow first, then bring in only the references for data, APIs, scale, security, reliability, AI systems, or review that the task actually needs. It keeps every interaction from being flooded with the entire architecture knowledge base.

The complete workflow is natural-language and model-driven. References provide depth, assets provide reusable forms, and examples calibrate expected reasoning without embedding architecture judgment in executable logic.

## Repository structure

~~~text
skills/
├── system-architecture-harness/
├── ai-agent-system-architecture/
└── architecture-review-gate/

evals/       Runtime-neutral prompts and AI review expectations
docs/        Standards, research, and provenance
.github/     Portable skill discovery checks
~~~

The repository is deliberately skill-only. It does not add a root harness.md, a .harness/ control plane, native hooks, or vendor-specific runtime configuration.

## Compatibility

### Verified in this repository

- The package is organized as three portable Agent Skills under `skills/<name>/SKILL.md`.
- The primary instructions use progressive disclosure through one-level references, assets, and examples.
- CI checks Skills CLI discovery and explicit installation into the Claude Code and Codex skill directories.
- The documented remote install targets are claude-code and codex through the Skills CLI.

### Portable skill format

Primary `SKILL.md` files use only the shared `name` and `description` frontmatter fields. Codex-specific display metadata is isolated in optional `agents/openai.yaml` files. ArcForge requires no executable helper, model-provider API key, native harness CLI, or vendor control plane; the active agent model performs the reasoning.

### What is not claimed

ArcForge does not claim that every agent harness discovers every skill automatically, that every runtime supports the same invocation syntax, or that installing a skill guarantees correct architecture. Model-generated rubrics and scores can vary by model, version, context, and run. Real activation, adherence, blocker recall, false positives, latency, cost, and architecture quality require repeated trials in the target agent and independent review of consequential decisions.

See the [research and standards map](docs/research-and-standards.md) for the exact sources and repository decisions behind this section.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) before changing a skill or its documentation.

Keep changes focused and preserve the portable package contract:

- keep each skill directory name equal to its frontmatter name;
- keep primary frontmatter portable and primary SKILL.md files at 500 lines or fewer;
- preserve ## Output Contract and ## Stop Conditions in every primary skill;
- add or update a runtime-neutral behavioral case before changing skill behavior;
- run affected cases with an approved target model and retain the complete outputs;
- keep deep material in `references/`, reusable forms in `assets/`, and calibration artifacts in `examples/`;
- report model/runtime identity, trial count, compatibility impact, disagreement, and checks that were not run.

### Maintainer verification

Maintainers review the changed skill and every linked resource, exercise the affected prompts in [the AI behavioral cases](evals/README.md), verify local links and portable frontmatter, and check discovery when network access is available:

~~~bash
npx skills add . --list
~~~

Discovery confirms that a client can find the package; it does not establish behavioral quality. A behavioral claim needs retained target-model outputs, repeated fresh-context trials, evidence-based review, and honest reporting of variance or unrun checks.

## Standards

ArcForge follows the portable [Agent Skills specification](https://agentskills.io/specification) and uses the [Skills CLI](https://github.com/vercel-labs/skills) for discovery and installation.

The architecture references also map to the [C4 model](https://c4model.com/), [Architecture Decision Records](https://adr.github.io/), [Google SRE guidance](https://sre.google/sre-book/service-level-objectives/), [NIST Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final), [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework), and [OWASP GenAI guidance](https://owasp.org/www-project-top-10-for-large-language-model-applications/), adapted to the actual system and risk rather than treated as certification.

The full provenance and source map is in [docs/research-and-standards.md](docs/research-and-standards.md).

## Security

See [SECURITY.md](SECURITY.md) for reporting guidance and consumer responsibilities. ArcForge skills are instructions and reference material, not a security certification. The consuming runtime and its operators remain responsible for tool permissions, data access, credentials, approvals, and incident response.

## License

ArcForge is released under the [MIT License](LICENSE). The current repository release is 0.2.0.
