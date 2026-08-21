# Repository Instructions for Coding Agents

## Purpose

This repository publishes portable Agent Skills for production system architecture. Core behavior belongs in the portable skill format and must remain usable across compatible runtimes.

Portable skills live under `skills/*/`. Each skill must remain usable by Claude Code, Codex, and other Agent Skills-compatible runtimes without depending on a vendor-specific control plane.

## Required workflow

1. Read the affected `SKILL.md` and its linked references completely.
2. Add or update a runtime-neutral behavioral case before changing observable behavior, then review it with an approved target model.
3. Keep skill frontmatter valid and make the directory name equal to the frontmatter `name`.
4. Keep each primary `SKILL.md` at 500 lines or fewer; move deep material into `references/`, reusable forms into `assets/`, and worked calibration artifacts into `examples/`.
5. Preserve the exact headings `## Output Contract` and `## Stop Conditions` in each primary skill.
6. Run portable skill discovery and perform the repository review checklist before claiming completion.
7. Read full output and report any unrun agent-specific or behavioral verification honestly.

## Portable skill rules

- Use only the shared Agent Skills frontmatter fields unless a runtime-specific field is clearly optional and isolated.
- Keep portable `SKILL.md` frontmatter to `name` and `description`; place Codex UI metadata in the optional `agents/openai.yaml` file.
- Keep installation and activation compatible with the shared Agent Skills format across supported runtimes.
- Keep descriptions specific enough for implicit activation and include concrete trigger words.
- Reference supporting files with paths relative to the skill directory.
- Keep skill behavior in natural-language instructions, references, examples, and reusable Markdown assets.
- Protect secrets, tokens, personal data, and runtime state from repository content.

## Architecture content rules

- Every decision traces to a requirement, invariant, risk, or constraint.
- Every critical claim has a validation path.
- No unsafe dual writes, floating-point money, unbounded resources, implicit internal trust, gateway-only authorization, backup-without-restore claims, or active-active ambiguity.
- AI systems separate model proposals from policy, permissions, durable truth, verification, and approval.
- An AI-generated contextual score never waives a critical blocker.

## File ownership

- Skill routing, mode selection, companion resolution, and step order: `skills/using-forge/`
- Route-only answers that inspect and change nothing: `skills/think-forge/`
- General architecture: `skills/system-architecture-harness/`
- AI/agent architecture: `skills/ai-agent-system-architecture/`
- Independent AI review: `skills/architecture-review-gate/`
- Identity, authentication, authorization, tenancy: `skills/auth-access/`
- APIs, validation, errors, pagination, webhooks, realtime, SDKs: `skills/api-contracts/`
- Data modeling, storage, identifiers, money, files, search, lifecycle: `skills/data-storage/`
- Transactions, concurrency, idempotency, consistency, distribution: `skills/transactions-consistency/`
- Jobs, queues, events, outbox, email, notifications: `skills/async-messaging/`
- Caching, rate limiting, quotas, retries, timeouts, breakers, backpressure: `skills/resilience-flow-control/`
- Secrets, cryptography, TLS, privacy, abuse, randomness: `skills/security-privacy/`
- Observability, runbooks, backup/DR, multi-region: `skills/production-operations/`
- Schema, data, and contract migration and cutover: `skills/migration-evolution/`
- Testing, performance, and release verification: `skills/quality-release/`
- Runtime, configuration, deployment, CI/CD: `skills/runtime-delivery/`
- Git repositories, branches, remotes, tags, versions, history, and repository workflow: `skills/git-workflows/`
- Canonical backend knowledge corpus and reference integrity: `backend-engineering-knowledge-base/`
- Repository documentation: `README.md`, `docs/`, `CONTRIBUTING.md`, and `SECURITY.md`
- Behavioral pressure cases: `evals/`

## Domain paper reference discipline

- The canonical corpus is `backend-engineering-knowledge-base/papers/`; never edit it casually.
- Skill copies under `skills/*/references/papers/` are committed portable reference artifacts. When a paper changes, update the canonical paper and every owning skill copy together, then review their semantic parity and links.
- Keep canonical papers and owning skill copies semantically aligned and review their links together.

## Routing map discipline

- The canonical routing source is `arcforge.catalog.yaml`: technical IDs, routing descriptions, positive and negative triggers, typed companions, and installation groups.
- `skills/using-forge/references/routing-map.md` and `skills/think-forge/references/routing-map.md` are identical committed copies derived from that catalog. When routing changes, update the catalog and both copies together and confirm they stay byte-identical.
- Never hand-edit one routing map copy alone, and never let a skill route from a name that merely sounds related instead of from the map.

## Maintainer review

Before completion:

1. inspect every changed instruction and its linked resources;
2. run affected cases in `evals/cases.json` with the target model and retain complete outputs;
3. verify frontmatter names, required headings, line limits, and local links;
4. run `npx skills add . --list` when network access is available; and
5. report model/runtime identity, trial count, disagreements, and any verification not performed.

## Prohibited changes

- Keep runtime-specific metadata optional, isolated, and documented.
- Do not weaken behavioral cases, critical blockers, or evidence gates to make a change pass.
- Do not add undocumented broad shell, network, filesystem, SQL, cloud, or deployment authority.
- Do not claim Skills CLI discovery, agent loading, or model-based behavioral evaluation passed unless it was run in the current change and its output was inspected.
