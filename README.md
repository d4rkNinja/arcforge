# ArcForge

> Production architecture skills and a governed AI Harness for designing, challenging, and verifying real systems.

ArcForge is a GitHub-ready collection of portable Agent Skills plus a native AI Harness control plane. It helps AI agents turn product goals, existing systems, incidents, and migration requests into architecture that can be implemented, operated, reviewed, measured, and safely changed.

The current package version is **0.1.0**. The canonical GitHub repository is [`d4rkNinja/arcforge`](https://github.com/d4rkNinja/arcforge). The installable skill identifiers remain stable while ArcForge serves as the project brand.

## What this project is

ArcForge deliberately keeps two layers separate:

1. **Portable skills** - standards-compatible `SKILL.md` packages that can be installed into Agent Skills-compatible tools and coding agents.
2. **Native harness** - `harness.md`, bounded specialist delegates, command governance, evidence gates, and evaluation artifacts for the AI Harness runtime.

The central model is:

```text
Harness = Instructions + Constraints + Feedback + Memory + Evaluation + Governance
```

The model proposes. The harness constrains, verifies, records, and decides what may happen next.

## Why ArcForge exists

Architecture is treated as a chain of explicit decisions under constraints - not a diagram, a technology list, or a popularity contest.

No architecturally significant decision is accepted without:

- a requirement, invariant, risk, or constraint that motivates it;
- a realistic alternative;
- a trade-off and consequence;
- an owner and decision horizon;
- a validation method and reversal trigger.

The project is intentionally strict about failure modes that are often hidden behind optimistic architecture language:

- no floating-point money or unprotected business invariants;
- no uncoordinated database-plus-broker dual writes;
- no unbounded queues, retries, fan-out, concurrency, or spend;
- no cache or search index accidentally becoming durable authority;
- no active-active write claim without conflict, ownership, fencing, and recovery semantics;
- no gateway-only authorization or implicit internal trust;
- no backup claim without a restore rehearsal and stated RTO/RPO;
- no consequential AI action without scoped authority, policy, approval, audit, and a kill switch.

A numeric score never waives a critical correctness, security, recovery, or evidence blocker.

## Included skills

Each skill is independently installable and can be used without the native harness.

| Skill | Use it for | Primary output |
|---|---|---|
| [`system-architecture-harness`](skills/system-architecture-harness/SKILL.md) | Greenfield design, scaling, modernization, migrations, reliability, security, data, APIs, operations, and incident-driven redesign | Complete production architecture specification, decisions, risks, validation plan, and implementation slices |
| [`ai-agent-system-architecture`](skills/ai-agent-system-architecture/SKILL.md) | LLM, RAG, memory, model routing, tools, autonomous agents, multi-agent workflows, evaluation, safety, latency, and inference economics | Governed AI system design with control plane, tool contracts, evaluation, budgets, safety, and rollout gates |
| [`architecture-review-gate`](skills/architecture-review-gate/SKILL.md) | Independent review of RFCs, ADRs, diagrams, migrations, production-readiness proposals, and AI architectures | Adversarial findings, evidence gaps, critical blockers, score, verdict, and approval conditions |

### Choosing a skill

- Use `system-architecture-harness` for general production system work.
- Use `ai-agent-system-architecture` when models, retrieval, memory, tools, or agents materially affect the design.
- Use `architecture-review-gate` for an independent quality gate or release decision.
- For mixed systems, use the general skill as the primary architecture output and add the AI-specific sections.
- For formal approval, always attach an independent review and fresh evidence.

## Architecture workflow

The skills use an evidence-first workflow and may move backward when new evidence invalidates an assumption:

```text
DISCOVER -> FRAME -> QUANTIFY -> MODEL -> OPTIONS -> DESIGN -> CHALLENGE -> VERIFY -> RECORD
              ^                                                     |
              +---------------- revise when evidence changes -------+
```

The workflow requires the agent to:

1. inspect the current system and separate facts, constraints, measurements, estimates, and assumptions;
2. define actors, tenants, critical journeys, non-goals, quality attributes, ownership, and risk;
3. quantify workload, burst, concurrency, storage, bandwidth, dependency quotas, latency, recovery, and cost;
4. model invariants, states, source of truth, consistency, concurrency, ordering, idempotency, reconciliation, and data lifecycle;
5. compare viable alternatives and select the smallest sufficient architecture;
6. design runtime components, data, APIs, events, critical flows, overload, reliability, security, observability, delivery, migration, and economics;
7. run independent challenge and pre-mortems for data loss, invariant breach, cross-tenant access, overload, dependency or region failure, unsafe migration, cost runaway, operator error, and AI tool misuse;
8. verify claims with current tests, calculations, scans, rehearsals, and scenario walkthroughs;
9. record ADRs, assumptions, risks, evidence, owners, review triggers, and the smallest safe implementation slices.

## AI system guardrails

The AI skill treats an AI product as governed software rather than a prompt wrapped around an API.

It separates the probabilistic model from the deterministic control plane:

```text
request boundary
  -> context and retrieval
  -> policy and model routing
  -> bounded planner/orchestrator
  -> capability-scoped tools
  -> verifier and human control plane
  -> durable state and evidence
```

The AI architecture guidance requires:

- a measurable task contract and deterministic or human baseline;
- explicit risk classification: informational, reversible, consequential, or irreversible;
- separate quality, safety, latency, availability, privacy, and cost requirements;
- tenant-aware retrieval with authorization inheritance, provenance, freshness, deletion, and no-result behavior;
- scoped memory with provenance, confidence, retention, correction, and deletion semantics;
- typed model outputs and evaluated fallbacks;
- capability-scoped tools instead of broad shell, SQL, browser, filesystem, cloud, or network authority;
- bounded depth, concurrency, iterations, tool calls, tokens, duration, and spend;
- prompt-injection, indirect-injection, exfiltration, privilege-escalation, poisoned-data, and denial-of-wallet defenses;
- golden, adversarial, trajectory, deterministic, human, reliability, and online evaluation;
- traceable model, prompt, retriever, index, policy, tool, approval, cost, and resulting-state evidence;
- safe degraded modes, manual paths, rollback criteria, and emergency kill switches.

## Native AI Harness

The native harness is the orchestration layer at the repository root:

- [`harness.md`](harness.md) contains runtime frontmatter and the principal architecture orchestrator prompt.
- [`.harness/agents/`](.harness/agents/) contains bounded specialist delegates.
- [`.harness/hooks/command-guard.md`](.harness/hooks/command-guard.md) blocks common destructive command patterns before execution.
- [`evals/`](evals/) contains runtime-neutral behavioral pressure cases.
- [`tests/`](tests/) and [`scripts/doctor.py`](scripts/doctor.py) provide deterministic repository verification.

The default harness configuration includes:

- OpenAI provider configuration with `gpt-4o` as the example model;
- `OPENAI_API_KEY` as the example secret environment variable;
- bounded retries with exponential backoff and a maximum retry count;
- maximum context history and token limits;
- denied filesystem deletion and metadata operations;
- delegation capped at depth 2, five concurrent delegates, and bounded iterations.

Change the provider, model, endpoint, and secret binding to match the approved runtime before adoption. Keep credentials in environment variables or a secret manager. Never commit them or place them in prompts, memory, traces, examples, or generated artifacts.

### Specialist delegates

Delegates return bounded findings. They do not concurrently mutate the shared architecture document; the orchestrator integrates their work.

| Delegate | Focus |
|---|---|
| `requirements-capacity-analyst` | Requirements, workload, SLOs, estimates, breakpoints, and cost drivers |
| `domain-data-architect` | Domain boundaries, invariants, state, data ownership, consistency, caches, and tenancy |
| `distributed-systems-architect` | APIs, events, queues, retries, ordering, scale, and multi-region behavior |
| `reliability-operations-architect` | SLOs, incidents, DR, overload, observability, on-call, and recovery evidence |
| `security-privacy-architect` | Identity, authorization, tenant isolation, privacy, abuse, and compliance handoffs |
| `ai-agent-architect` | AI control planes, memory, tools, evaluation, safety, and inference economics |
| `migration-delivery-architect` | Transition states, compatibility, backfills, cutover, rollout, and rollback |
| `architecture-critic` | Independent adversarial review and release blockers |
| `evidence-verifier` | Fresh command, test, calculation, restore, migration, and acceptance evidence |

### Command governance

The command hook is a safety layer, not a replacement for sandboxing or human approval. It blocks common patterns such as recursive destructive deletion, hard resets, force pushes, filesystem formatting, operating-system shutdown, and piping remote scripts directly into a shell.

Architecture requests never authorize production deployment, destructive commands, force pushes, secret exposure, or irreversible external actions.

## Installation

### Prerequisites

- Git for cloning or pinning the repository.
- Node.js and `npx` for Skills CLI discovery and installation.
- Python 3.10 or newer for the bundled validators and repository checks.
- The native `harness` CLI only when using the AI Harness runtime.

### Inspect the local package

```bash
npx skills add . --list
```

### Install one skill locally

```bash
npx skills add . --skill system-architecture-harness
```

### Install all three skills

```bash
npx skills add . --skill '*' --agent '*'
```

### Install selected skills into selected agents

```bash
npx skills add . \
  --skill system-architecture-harness \
  --skill architecture-review-gate \
  --agent codex \
  --agent claude-code \
  --agent cursor \
  --agent github-copilot
```

### Install from GitHub

Install from the canonical GitHub repository:

```bash
npx skills add d4rkNinja/arcforge --list
npx skills add d4rkNinja/arcforge --skill system-architecture-harness
```

The repository-level [`skills.sh.json`](skills.sh.json) groups all three skills for compatible catalog and index surfaces. Keep the skill names stable after publication because installation and catalog identity depend on them.

## Run the native harness

Set the provider credential through the environment or an approved secret manager:

```bash
export OPENAI_API_KEY="your-secret"
harness validate
harness run
```

On PowerShell:

```powershell
$env:OPENAI_API_KEY = "your-secret"
harness validate
harness run
```

The example configuration in [`harness.md`](harness.md) is a starting point, not proof of provider availability, production readiness, or security. Validate the actual provider, model, tool permissions, network policy, data handling, and approval workflow in the target environment.

## Architecture review scanner

Run the deterministic Markdown scanner against an architecture specification:

```bash
python skills/architecture-review-gate/scripts/score_architecture.py \
  path/to/architecture.md \
  --format json
```

The scanner checks visible evidence across scope, requirements, boundaries, data correctness, interfaces, performance, reliability, security, operations, decisions, cost, and validation. It also flags dangerous patterns such as:

- floating-point financial values;
- independent database and broker writes;
- unbounded retry or queue behavior;
- authoritative caches or search indexes without recovery semantics;
- unsupported end-to-end exactly-once claims;
- incomplete active-active write semantics;
- internal-network trust;
- gateway-only authorization;
- backup claims without restore evidence;
- direct deployment without rollback or progressive delivery;
- technology-first microservice justification.

Verdicts are structural gates, not certificates:

| Verdict | Meaning |
|---|---|
| `PASS` | Score is at least 85, no critical finding exists, and visible evidence is sufficient for the scanner |
| `CONDITIONAL` | Score is 60-84 or material evidence remains unresolved |
| `BLOCK` | A critical finding exists or the score is below 60 |

The scanner cannot prove correctness, security, compliance, scalability, recoverability, or operational readiness. Pair it with expert review and fresh runtime evidence.

## Validation

Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run the deterministic repository gate:

```bash
python scripts/doctor.py
```

The doctor runs:

- the repository unit tests;
- skill frontmatter, naming, link, line-count, and output-contract checks;
- native harness artifact and delegate checks;
- command-guard checks;
- Skills.sh grouping checks;
- positive and negative architecture-scanner fixtures.

Equivalent Make targets are available:

```bash
make test
make doctor
make package
```

The package command creates a reproducible ZIP, updates [`MANIFEST.sha256`](MANIFEST.sha256), and writes a checksum beside the ZIP. Generated archives should stay outside the repository unless explicitly needed for distribution.

### Optional external checks

Skills specification validation, when the reference validator is installed:

```bash
skills-ref validate skills/system-architecture-harness
skills-ref validate skills/ai-agent-system-architecture
skills-ref validate skills/architecture-review-gate
```

Native runtime validation:

```bash
harness validate
```

These checks are intentionally separate from the default doctor command. Do not claim they passed unless they were run in the current change and their complete output was inspected.

## Behavioral evaluation

[`evals/cases.json`](evals/cases.json) is a runtime-neutral pressure suite covering:

- technology-first greenfield design;
- queue and retry overload;
- financial ledger correctness;
- multi-region write semantics;
- backup and restore claims;
- gateway-only authorization;
- unsafe database-plus-broker dual writes;
- RAG tenant isolation;
- broad agent shell access;
- unbounded agent loops;
- unsafe model fallback;
- deadline pressure and unrun evidence.

For each approved agent and model, compare:

1. no-skill baseline;
2. named portable skill enabled;
3. native harness enabled, when adopted.

Use at least five fresh-context trials per condition. Score expected and forbidden behaviors, read flagged outputs, and report activation rate, instruction adherence, blocker recall, false-positive rate, output completeness, latency, and cost. A deterministic repository pass proves package structure and scanner behavior; it does not prove behavioral uplift in real agents.

## Repository layout

```text
.
├── skills/
│   ├── system-architecture-harness/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── assets/
│   │   ├── examples/
│   │   └── scripts/
│   ├── ai-agent-system-architecture/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── assets/
│   │   └── examples/
│   └── architecture-review-gate/
│       ├── SKILL.md
│       ├── references/
│       ├── assets/
│       └── scripts/
├── harness.md
├── .harness/
│   ├── agents/
│   └── hooks/
├── evals/
├── tests/
├── scripts/
├── docs/
├── skills.sh.json
├── CONTRIBUTING.md
├── SECURITY.md
└── LICENSE
```

### Progressive disclosure

Primary skills stay compact and portable. Detailed knowledge lives one link away in `references/`; reusable architecture artifacts live in `assets/`; deterministic helpers live in `scripts/`; worked examples and pressure cases live in `examples/` and `tests/`.

This keeps the skills useful across runtimes without injecting a giant prompt into every architecture task.

## Contributing

Read [`AGENTS.md`](AGENTS.md) before changing the repository. The contribution workflow is:

1. describe the observed failure, missing architecture case, or standards change;
2. add a failing deterministic test or behavioral case when behavior is changing;
3. make the smallest focused change;
4. preserve portable skill boundaries, frontmatter, output contracts, and stop conditions;
5. run `python scripts/doctor.py`;
6. document evidence, compatibility impact, and any native or behavioral checks that were not run.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full repository contract.

## Security and safe adoption

Skills contain instructions and executable helpers. Review the source before installation, pin trusted commits for production use, run validators in a sandboxed environment, keep provider credentials in secret bindings, and apply least privilege to every agent runtime.

Report suspected malicious instructions, unsafe executable behavior, secret exposure, cross-tenant risk, command-guard bypass, or supply-chain concerns through a private GitHub security advisory after publication. Do not put credentials, personal data, or exploitable customer information in public issues.

Read [`SECURITY.md`](SECURITY.md) for the security policy. ArcForge is not a security certification, compliance approval, penetration test, or substitute for domain-owner review.

## Standards and provenance

The repository structure and runtime artifacts are documented in [`docs/research-and-standards.md`](docs/research-and-standards.md), including the Agent Skills specification, Skills.sh conventions, native AI Harness references, and source coverage notes.

## License

ArcForge is released under the [MIT License](LICENSE).
