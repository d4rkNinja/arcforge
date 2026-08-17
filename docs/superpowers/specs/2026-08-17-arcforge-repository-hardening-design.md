# ArcForge Repository Hardening Design

- **Status:** Approved with the instruction-only amendment below
- **Date:** 2026-08-17
- **Baseline:** `origin/main` at `77cb452ba6b02807b2aa16762961f82fcffff246`
- **Working branch:** `codex/arcforge-hardening`

## Executive Summary

ArcForge will become a deterministic, runtime-neutral skill system with one
canonical catalog, machine-checkable architectural rules, reproducible
packaging, explicit companion-skill behavior, and evidence-backed release
gates. The work preserves the 14 stable technical skill IDs while completely
repositioning their user-facing names and workflows around four neutral modes:
**think**, **review**, **change**, and **verify**.

The stable IDs remain unchanged because they are installation and activation
contracts used by existing consumers. The visible names, headings, routing
copy, examples, guides, and outputs will no longer present the domain skills as
one-way change commands. A user can ask a skill to think through a new
system, review an existing design or codebase, guide a change, or verify the
result without being forced into a different workflow.

The hardening program is validator-first. It establishes canonical structured
data and deterministic checks before migrating the corpus or changing generated
artifacts. This makes every later change measurable and prevents a broad prose
rewrite from silently weakening critical architectural obligations.

## Instruction-Only Amendment

The maintainer subsequently required the repository to remain purely portable
instructions, references, examples, metadata, and manual behavioral cases. That
later decision supersedes every section below that proposes committed scripts,
test runners, package dependencies, generated caches, Make targets, or expanded
automation. The naming, four-mode behavior, companion routing, catalog,
structured reference data, manual evidence discipline, and release goals remain
approved. No executable helper is part of the delivered `0.3.2` repository.

## Confirmed Baseline

The design is based on a clean checkout of the requested baseline and direct
inspection of the repository, all primary skills, linked guidance, evaluation
data, corpus tooling, manifests, CI, and release documentation.

Confirmed conditions include:

- all 14 stable skill IDs are discoverable and their primary `SKILL.md` files
  satisfy the current heading and line-count requirements;
- the canonical corpus validates structurally with 146 papers and 1,881
  subtopics;
- 1,136 of 1,881 subtopics currently collapse to generic template-only
  packaging output, which is too much semantic loss for a reference corpus;
- the current packager is deterministic for current inputs but lacks a check
  mode, dry-run report, isolated output directory, and atomic replacement;
- evaluations have no JSON Schema, stable criterion IDs, result schema, or
  representation for installed companion skills and cross-skill activation;
- cross-skill routing contains ownership drift and many prose-only companion
  references whose availability is not checked;
- CI checks discovery and installation but does not run the complete corpus,
  packaging, semantic, evaluation, manifest, or documentation gates;
- the nested knowledge-base checksum manifest contains a stale README entry;
- several documented commands point at incorrect paths or assume `python`
  where the supported local command is `python3`;
- OpenAI metadata is structurally present, but multiple short descriptions are
  outside the currently documented 25-64 character range;
- release dependencies and GitHub Actions references are not fully immutable.

These findings are the initial issue families, not a complete defect list. Each
fix must be followed by a repository-wide search for the same pattern.

## Goals

1. Make skill identity, routing, ownership, companions, and installation groups
   canonical and mechanically consistent.
2. Replace confusing action-oriented visible names with clear thinking names
   and explicit think, review, change, and verify modes.
3. Preserve critical architectural meaning across corpus packaging and
   progressive loading.
4. Give high-risk rules stable IDs, severity, scope, evidence requirements, and
   validation paths.
5. Make generators deterministic, inspectable, failure-safe, and capable of
   proving that committed artifacts are current.
6. Make behavioral evaluations schema-validated, traceable to rules, and
   reproducible across recorded model/runtime trials.
7. Give CI and release workflows one complete, documented verification path.
8. Keep the repository portable across Agent Skills-compatible runtimes and
   free of vendor-specific control planes.
9. Improve discoverability without weakening single-skill safety or pretending
   unavailable companions were loaded.
10. Produce evidence for every completion claim and disclose every unrun check.

## Non-Goals

- Renaming the stable technical skill IDs or directories in this release.
- Adding a native harness, runtime hook system, provider API requirement, or
  executable dependency for normal skill activation.
- Replacing expert prose with a rules database.
- Making model-graded evaluations the sole merge gate.
- Creating a new package manager or general-purpose build framework.
- Rewriting all 146 papers at once without cluster-level review and evidence.
- Publishing a release, pushing a branch, or changing external systems without
  the required authority and credentials.

## Compatibility Invariants

- The 14 technical IDs and matching directory/frontmatter names remain stable.
- Every primary skill preserves the exact headings `## Output Contract` and
  `## Stop Conditions` and remains at 500 lines or fewer.
- Generated paper copies are never edited by hand.
- Existing safe obligations remain active until their structured replacements
  are proven equivalent or stronger.
- A contextual or model-generated score never waives a critical blocker.
- Missing companion skills reduce depth; they never invent evidence or silently
  remove a safety requirement.
- The portable skill layer does not require credentials, network access, or a
  specific model provider.

## User-Facing Skill Names

The technical ID is a compatibility key. The display name is the user-facing
promise. Every visible name will be changed as follows:

| Stable technical ID | New user-facing name |
| --- | --- |
| `system-architecture-harness` | Think Through Production Systems |
| `ai-agent-system-architecture` | Think Through AI & Agent Systems |
| `architecture-review-gate` | Review Software Architecture |
| `auth-access` | Think Through Identity & Access |
| `api-contracts` | Think Through API & Client Contracts |
| `data-storage` | Think Through Data & Storage |
| `transactions-consistency` | Think Through Transactions & Consistency |
| `async-messaging` | Think Through Async Work & Messaging |
| `resilience-flow-control` | Think Through Resilience & Flow Control |
| `security-privacy` | Think Through Security & Privacy |
| `production-operations` | Think Through Production Operations |
| `migration-evolution` | Think Through Migrations & Evolution |
| `quality-release` | Think Through Quality & Release Readiness |
| `runtime-delivery` | Think Through Runtime & Delivery |

The rename applies consistently to primary headings, OpenAI display metadata,
README tables, skill guides, examples, generated catalog views, evaluation
fixtures, and other user-visible references. Routing descriptions will use
neutral trigger language such as “thinking through,” “reviewing,” “changing,”
and “verifying.” The architecture review gate intentionally keeps a review-led
name because its independence is part of its contract, while its output can
still recommend changes and verification work.

### Four Explicit Modes

Every domain skill will accept or infer one of four modes:

- **Think:** clarify requirements, constraints, invariants, risks, decisions,
  alternatives, and validation paths before a change is made.
- **Review:** inspect an existing proposal, architecture, repository, diff, or
  operational state; separate evidence from assumptions; report blockers and
  prioritized findings.
- **Change:** turn approved decisions into a concrete, repository-aware change
  sequence while preserving contracts, security, data integrity, and rollback.
- **Verify:** prove the resulting behavior through tests, measurements,
  operational evidence, and explicit residual-risk reporting.

The requested mode controls emphasis, not safety. Think mode may stop with an
approved decision record. Review mode may stop with findings. Change mode must
not claim completion without verification. Verify mode must not fill evidence
gaps with assumptions. If the user requests a combined flow, the skill proceeds
through the modes in order and retains the decision-to-evidence trace.

## Canonical Repository Model

### Skill Catalog

A root `arcforge.catalog.yaml` becomes the source of truth for:

- technical ID and user-facing name;
- routing description and positive/negative trigger phrases;
- owning domain and canonical paper set;
- required, recommended, handoff, and optional-depth companions;
- installation groups and standalone safety behavior;
- primary guides, assets, examples, and evaluation cases;
- generated metadata projections and documentation links.

Human-authored `SKILL.md` instructions remain authoritative for behavior. The
catalog owns repeated identity and relationship data. A generator projects the
catalog into OpenAI metadata, repository indexes, install-group documentation,
and machine-readable coverage reports. CI rejects drift between the catalog and
committed projections.

### Structured Critical Rules

The canonical corpus remains under
`backend-engineering-knowledge-base/papers/`. A new structured rule registry
under `backend-engineering-knowledge-base/rules/` captures only requirements
that must be mechanically traced. Each rule includes:

- stable rule ID;
- title and normative statement;
- owner paper, section, and skill;
- topic category and severity;
- applicability predicate and declared exceptions;
- required evidence and validation method;
- related evaluation criteria;
- supersession and migration metadata.

The registry is canonical for these critical rule records. Papers remain
canonical for explanation, tradeoffs, examples, and contextual guidance. The
packager renders a generated critical-rules section into packaged references so
the structured and narrative layers stay connected. Existing prose obligations
remain in force during migration; a rule is moved only after a semantic diff and
review confirm that no requirement was lost.

### Exceptions

Exceptions are structured records, not free-form waivers. They include the rule
ID, scope, reason, owner, evidence, compensating controls, approval, expiry, and
review state. Critical rules cannot be waived by an AI-generated score.

## Deterministic Generation and Packaging

Generation is split into pure transforms and thin command-line entry points.
The package command reads canonical inputs, writes to an isolated staging
directory, validates the complete staged result, and atomically replaces the
managed output only after success.

Required command behavior:

- `--check` proves committed generated output matches canonical inputs;
- `--dry-run` emits the planned file operations without modifying the tree;
- `--out-dir` supports isolated tests and review artifacts;
- `--report json` emits counts, warnings, errors, ownership, and hashes;
- deterministic sort order, UTF-8 encoding, and normalized line endings;
- exact output-set validation catches both missing and stale generated files;
- interruption or validation failure leaves committed output unchanged;
- generated file headers identify their source and regeneration command.

The current paper transform will be refactored into testable functions for
source parsing, boilerplate classification, semantic compaction, link rewriting,
section numbering, and rendering. Generic template collapse will occur only
when the retained obligations are proven equivalent. High-risk topics will use
structured decision cards before deeper paper material, not generic defaults.

## Progressive Loading

Progressive loading has three layers:

1. compact routing metadata for activation;
2. decision cards for the selected domain, mode, and risk profile;
3. focused paper sections and examples only when deeper evidence is required.

Decision cards are generated from structured rules and contain the question,
invariant, unsafe default, required decision, evidence path, and escalation
condition. They do not summarize away critical obligations. Token and coverage
measurements will compare the current and proposed layouts across representative
single-domain and cross-domain cases before the new layout becomes canonical.

Long generated references gain a compact contents section or index so an agent
can navigate them without loading unrelated material.

## Companion Skills and Standalone Safety

Companion relationships become typed catalog entries:

- **required:** the requested outcome cannot be completed safely without it;
- **recommended:** materially improves coverage but has a safe local fallback;
- **handoff:** owns a separate decision reached from the current domain;
- **optional-depth:** adds detail when installed and relevant.

Each relationship declares when it applies, what information is handed off, and
what happens when the companion is missing. A skill must never state that it
read a companion reference that is unavailable. Standalone use must return the
safe local decision, explicitly identify missing depth, and provide the exact
companion ID or installation group needed to continue.

Installation groups are generated from the catalog and tested both as bundles
and as standalone skills. The repository documents the minimum complete group
for system design, AI systems, independent review, and common cross-domain
flows.

## Behavioral Evaluation Model

Evaluations become versioned data with JSON Schema validation. A case records:

- stable case ID, title, category, severity, and lifecycle state;
- installed skills and intentionally missing companions;
- user input and relevant repository context;
- expected activation, non-activation, and handoffs;
- stable criterion IDs linked to catalog entries and critical rule IDs;
- required evidence, forbidden behavior, and stop conditions;
- deterministic assertions and model-review rubric;
- provenance and last review information.

Evaluation results use a separate schema containing repository revision,
runtime/model identity as reported by the runtime, trial number, complete raw
output reference, criterion outcomes, reviewer, disagreements, and timestamps.
No result is accepted without preserving the complete output.

Deterministic schema, routing, forbidden-pattern, and coverage checks run on
every change. Model trials run through a documented runtime-neutral procedure
for affected cases, with the repository’s required trial count and disagreement
reporting. CI never fabricates unavailable runtime identities or silently treats
an unrun model trial as a pass.

## Unified Verification Interface

A small root command surface will orchestrate existing focused tools:

- `make validate` — schemas, skills, catalog, corpus, links, manifests;
- `make package` — regenerate managed artifacts;
- `make package-check` — prove generated artifacts are current;
- `make lint` — Python and repository formatting/static checks;
- `make test` — tooling unit, golden, mutation, and integration tests;
- `make eval-lint` — evaluation schema, criteria, and coverage checks;
- `make install-check` — Skills CLI discovery and installation smoke tests;
- `make check` — the complete deterministic local/CI gate.

Each command prints its runtime versions and full failure details. Python tools
use `python3` consistently. Dependencies are declared and pinned sufficiently
for reproducible local and CI execution. The Skills CLI version is pinned and
updated intentionally rather than fetched as an unbounded latest version.

## CI and Release Gates

CI is layered for fast feedback and complete evidence:

1. metadata, schema, links, and generated-drift checks;
2. corpus validation and semantic-rule integrity;
3. tooling unit, golden, mutation, and failure-path tests;
4. evaluation lint and rule-coverage checks;
5. standalone and installation-group discovery/install smoke tests;
6. manifest, documentation, secret, and release-integrity checks.

Jobs use least-privilege permissions, explicit timeouts, concurrency controls,
immutable action references, pinned tool versions, and dependency caching keyed
to lock data. Full output remains available for diagnosis.

Release validation proves version consistency, changelog state, generated
artifacts, manifests, checksums, installability, and tag expectations. Release
creation, signing, and remote publication remain external actions requiring
explicit authority. The user-facing rename and expanded behavior warrant a
minor release rather than pretending the change is invisible.

## Failure Behavior

- Schema failures identify the file, record, field, and violated rule.
- Semantic ambiguity is reported for human review; it is never auto-resolved by
  deleting an obligation.
- Generation failures leave the working output intact and clean staging data.
- Missing companions produce a bounded response and explicit continuation path.
- Checksum mismatches identify both the expected source and actual artifact.
- Model/runtime unavailability is recorded as unrun, not failed or passed.
- Every automatic correction is deterministic and inspectable in a normal diff.

## Delivery Sequence

### Phase 1: Foundation and Known Breakages

- Add behavioral cases covering the new names, four modes, and companion
  absence before changing observable skill behavior.
- Add the catalog and schemas, then validate current content against them.
- Fix stale checksums, broken command paths, misleading script claims, and
  metadata length violations.
- Add the root command surface and complete deterministic CI gate.

### Phase 2: Naming, Routing, and Companion Behavior

- Apply the complete user-facing rename across all projections.
- Normalize the four modes and their output/stop behavior in every skill.
- Correct ownership and routing drift.
- Generate companion maps and install groups; test standalone degradation.
- Update guides, examples, and evaluations together with each behavior change.

### Phase 3: Packaging and Structured Rules

- Refactor packaging into pure, tested stages with check/dry-run/staging modes.
- Introduce the critical-rule and exception schemas.
- Migrate rules cluster by cluster, starting with money, identity/tenancy,
  transactions, authorization, migrations, secrets, and operations.
- Add semantic diffs and issue-family searches after each cluster.

### Phase 4: Progressive Loading and Evaluation Evidence

- Generate decision cards and navigable indexes.
- Add evaluation/result schemas, criterion traceability, coverage reports, and
  the runtime-neutral trial procedure.
- Measure context reduction and rule retention on representative cases.
- Run affected cases with approved available target runtimes and retain outputs.

### Phase 5: Release and Documentation Closure

- Harden supply-chain references and release validation.
- Regenerate manifests and checksums only after all content is final.
- Run the complete local, CI-equivalent, discovery, installation, behavioral,
  and manual review checklists.
- Produce a concise evidence report with runtime identities, trial counts,
  disagreements, and all unrun checks.

Each phase ends with a clean-tree review, full affected checks, and a
repository-wide search for the issue family just fixed. A phase cannot weaken a
gate merely to make the next phase pass.

## Test Strategy

- Unit tests cover parsers, schemas, path handling, rule ownership, link
  rewriting, normalization, and failure cleanup.
- Golden tests cover representative packaged papers, decision cards, catalog
  projections, and documentation indexes.
- Mutation tests remove or weaken critical fields and prove validators fail.
- Integration tests package into a temporary directory, compare exact outputs,
  rerun for determinism, and verify failed runs are non-destructive.
- Evaluation lint proves unique IDs, valid rule references, activation
  expectations, companion states, and criterion coverage.
- Installation tests exercise all 14 standalone skills and generated bundles.
- Manual model review records complete outputs and disagreements for affected
  behavioral cases.
- Final review inspects every changed instruction and linked resource, checks
  for secrets and temporary artifacts, and reports unavailable external proof.

## Acceptance Criteria

The hardening program is complete only when:

- all 14 stable IDs remain valid and every user-facing surface uses the approved
  new name;
- every domain skill demonstrably supports think, review, change, and verify;
- catalog, skill metadata, docs, routing, ownership, companions, and evals have
  no unexplained drift;
- corpus and structured rules validate, with critical obligations traceable to
  evidence and evaluation criteria;
- packaging is deterministic, checkable, failure-safe, and free of unreviewed
  template-only semantic collapse;
- root commands and CI run the same deterministic gates successfully;
- standalone and group discovery/install checks pass with the pinned CLI;
- affected behavioral cases are reviewed with complete retained outputs;
- manifests and checksums match final content;
- all changed files receive manual review and the worktree contains no temporary
  artifacts or secrets;
- the final report distinguishes verified facts, external blockers, and unrun
  checks without overstating completion.

## Key Risks and Controls

| Risk | Control |
| --- | --- |
| Visible rename breaks existing installations | Keep stable IDs and directories; change only user-facing projections |
| Structured rules diverge from prose | Generate paper rule sections and validate bidirectional references |
| Corpus compaction weakens obligations | Use semantic diffs, high-risk mutation cases, and cluster review |
| Catalog becomes another drifting source | Define field ownership and reject projection drift in CI |
| Cross-skill safety depends on unavailable files | Type companions and require explicit standalone behavior |
| Model evaluation is non-reproducible | Schema results, record complete outputs and runtime identity, separate deterministic gates |
| Generator failure corrupts managed files | Stage, validate, then atomically replace |
| Broad program obscures regressions | Deliver in gated phases and search each issue family repository-wide |

## Decision Record

The selected approach is **validator-first incremental hardening**. A big-bang
rewrite was rejected because it would combine naming, corpus transformation,
routing, evaluation, and release changes into an unreviewable semantic diff. A
patch-only repair was rejected because it would fix symptoms while leaving the
duplicated metadata and missing verification architecture intact.

The stable technical IDs are deliberately retained. The user’s request for a
complete rename is satisfied at every user-facing layer, while existing install
commands, explicit skill invocations, frontmatter constraints, and external
references continue to work. A future technical-ID migration would require an
independent compatibility design with aliases or a documented breaking release;
the current Agent Skills contract does not provide a portable alias mechanism.
