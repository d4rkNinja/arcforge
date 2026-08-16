# Platform, Governance, Economics, and Evolution

Use this reference when platform engineering, repository/build topology, ownership,
technical debt, rewrites, migration, or architecture metrics affect a decision. The
topic coverage is informed by sections 22–25 and 34 of the user-supplied research
manuscript; treat it as research input, not independent publication proof.

## Contents

- [1. Define platform outcomes](#1-define-platform-outcomes)
- [2. Govern paved roads and exceptions](#2-govern-paved-roads-and-exceptions)
- [3. Align repository and build topology](#3-align-repository-and-build-topology)
- [4. Make ownership operational](#4-make-ownership-operational)
- [5. Account for TCO and debt](#5-account-for-tco-and-debt)
- [6. Gate rewrites](#6-gate-rewrites)
- [7. Sequence migration](#7-sequence-migration)
- [8. Govern metric vectors](#8-govern-metric-vectors)

## 1. Define platform outcomes

Treat developer experience as an architecture outcome: onboarding, local setup, build
and test feedback, documentation/discovery, deploy safety, debugging, incident handling,
and cognitive load affect delivery and reliability.

Create or expand an internal platform only when repeated cross-team work can be
productized. Define its users, product owner, support model, reliability/security
contract, roadmap, cost, and exit. Measure outcomes such as lead time, deployment
rework/failure, diagnosis time, toil removed, control adoption, cognitive load, and user
feedback—not portal visits or generated-service count alone.

## 2. Govern paved roads and exceptions

A paved road should make the safe, observable, operable path easy through reusable
templates and capabilities for identity, secrets, policy, delivery, telemetry,
migrations, dependencies, ownership, and cost.

Define an exception process with:

- the unmet workload or control requirement;
- accountable owner and risk acceptance authority;
- compensating controls and evidence;
- support/on-call and lifecycle responsibility;
- review/expiry date and path to converge, productize, or retire the exception.

Do not force legitimate workloads into unsafe defaults or let exceptions silently bypass
governance. Platform abstractions must expose enough underlying behavior for diagnosis.

## 3. Align repository and build topology

Choose monorepo, polyrepo, or hybrid from observed change coupling, ownership,
compatibility, release cadence, access boundaries, and tool capacity.

| Topology | Capability | Burden to validate |
|---|---|---|
| Monorepo | atomic cross-component change, shared policy/tooling, discoverability | scalable build graph/cache, ownership, access, dependency rules |
| Polyrepo | independent access, ownership, release and lifecycle | versioning, cross-repo change, contract testing, discovery and dependency update |
| Hybrid | separates stable platform/product or security boundaries | explicit grouping rule, duplicated tooling and cross-boundary compatibility |

Slow feedback encourages larger batches. Treat hermeticity, reproducibility, incremental
builds, cache correctness, test selection, parallelism, artifact provenance, and local/CI
parity as architectural capabilities with owners and measured targets.

## 4. Make ownership operational

Assign an accountable owner for every runtime component, dataset, schema, queue,
certificate/key, model, platform capability, dashboard, SLO, recovery path, and temporary
migration mechanism. Ownership covers roadmap, compatibility, on-call, security/privacy,
cost, documentation, deprecation, restore, and migration—not only code review.

Review socio-technical fit in both directions: dependencies create communication work,
and team boundaries shape software. Avoid both shared-no-owner assets and boundaries so
rigid that every user outcome requires central coordination. Architecture review should
surface requirements, state authority, new failure modes, operations, reversibility, and
evidence early without becoming mandatory approval for every local change.

## 5. Account for TCO and debt

Compare lifecycle cost as a vector:

- build and product-learning delay;
- infrastructure, network, observability, backup, licenses and vendor support;
- testing, delivery, security, privacy and compliance;
- on-call, incidents, restore, migration and decommissioning;
- coordination, review, onboarding and specialist knowledge;
- lock-in, opportunity cost and expected failure loss.

Classify debt as intentional, accidental, architectural, dependency, infrastructure, or
knowledge debt. Record the capability bought, current “interest” (slower changes,
incidents, coordination, risk), owner, repayment/review trigger, and evidence. An
imperfection with no material present consequence is not automatically debt.

## 6. Gate rewrites

Do not approve a rewrite from stack preference or dislike of old code. Require:

- a non-negotiable requirement the current system cannot meet, or evidence that the
  safest incremental path has worse expected lifecycle cost;
- an executable behavior inventory including hidden integrations and operational rules;
- source-of-truth and data migration, reconciliation, compatibility, and audit plan;
- capacity to operate old and new paths through the transition;
- bounded scope, product-change strategy, milestones, abort criteria and cleanup;
- validation of correctness, performance, recovery, security, cost and user outcomes.

Prefer targeted refactoring or replacement behind a stable boundary when it can retire
the constraint with less simultaneous risk.

## 7. Sequence migration

Evaluate architecture as deployable, recoverable states, not only a target diagram.
For each step define old/new authority, compatible readers/writers, traffic and data
movement, observation window, reconciliation, abort, rollback or roll-forward, cleanup,
owner, and point of no return.

Use strangler, branch by abstraction, parallel change, expand-contract, facade, shadow,
backfill, CDC, or controlled cutover according to the boundary. Avoid naive independent
dual writes. Mark transitional components with expected lifetime and deletion trigger.

Before extracting services, restore module/data ownership and remove internal cycles and
cross-module table access. Before active-active, prove backup/restore and simpler regional
failover. Consider consolidation when services always deploy together, share one model,
form chatty cycles, lack independent owners, or cost more than the isolation they provide.

## 8. Govern metric vectors

Use metrics to answer named decisions and detect changing risk, not to rank teams or emit
one “architecture score.” Combine only relevant dimensions:

- **structure:** cycles, fan-in/out, propagation/change coupling, ownership fragmentation;
- **delivery:** lead time, deployment frequency, rework/failure, recovery and reliability;
- **developer experience:** satisfaction, build/test/onboarding time, interruption,
  cognitive load and debugging effort;
- **operations:** SLO/error budget, incident frequency/severity/blast radius/recurrence,
  detection/mitigation/recovery/understanding, restore proof, lag and capacity headroom;
- **economics/evolution:** cost per useful outcome, platform toil, temporary-path age,
  migration progress, decommissioned burden and vendor concentration.

For every metric record definition and unit, population/window, data source and quality,
intended decision, owner, known confounders, gaming risk, segmentation/privacy, target or
interpretation rule, and review/retirement date. Compare a system to its own baseline or
an explicitly justified cohort. Triangulate before inferring causation; never turn an
individual or team quota into a proxy for architecture quality.
