---
name: data-storage
description: "Use when thinking through, reviewing, changing, or verifying data models and storage behavior: schemas, identifiers, time, money, constraints, indexes, queries, deletion, lifecycle, files, media, search, provenance, authority, reconciliation, or cleanup. For concurrency use transactions-consistency; for schema evolution use migration-evolution; for caching use resilience-flow-control."
---

# Think Through Data & Storage

## Overview

Production guidance for data modeling and storage. Each reference paper captures the correctness work that schema-first drafts miss: precision hazards, constraint-race conditions, index design from real predicates, soft-delete interactions with uniqueness, file-handling abuse, derived-store rebuilds, and retention obligations.

**Core principle:** Data outlives code. Every column, identifier, file, and derived index is a durable decision with invariants, an owner, and a lifecycle — not a convenient shape for today's feature.

## Domain Law

```text
NO DATA OR STORAGE CHANGE WITHOUT:
1. the primary paper(s) for the data being modeled read in full first;
2. the paper's pre-change questions
   answered, or each open point labeled as an assumption;
3. "Existing-codebase checks" run when changing an existing schema or store;
4. every applicable MUST mapped to a decision (constraint, index, policy),
   a test, or a documented exception — never silently downgraded.
```

## When to Use

Use this skill when thinking through, reviewing, changing, or verifying:

- tables, documents, relationships, denormalization, and metadata modeling;
- identifier generation, exposure, and migration (auto-increment, UUIDv4/v7, ULID, snowflake);
- timestamps, timezones, DST, scheduling, and clock-skew handling;
- money and numeric precision, rounding modes, and serialization fidelity;
- primary/foreign/unique/check constraints and constraint race conditions;
- indexes (composite, partial, covering) and query plans, N+1 elimination;
- soft delete, restore, purging, and unique-constraint interaction;
- retention, archival, expiration, anonymization, and legal hold;
- immutable/append-only records, correction records, and tamper evidence;
- file upload/download, MIME and signature validation, signed URLs, orphan cleanup;
- image/video processing pipelines and original preservation;
- full-text/vector search and index synchronization;
- record versioning, provenance, source-of-truth boundaries, reconciliation, and cleanup jobs.

## When Not to Use

- Transaction boundaries, isolation, idempotency, distributed consistency: use `transactions-consistency`.
- Migration sequencing, expand-contract, backfills: use `migration-evolution`.
- Cache semantics, invalidation, coordination: use `resilience-flow-control` (037, 131).
- Replication/sharding topology decisions: `transactions-consistency` (100, 101).
- Whole-system architecture: use `system-architecture-harness`.

## Select the Operating Mode

| Mode | Use when | Required result |
|---|---|---|
| **Think** | The safe decision is not settled | requirements, constraints, invariants, risks, alternatives, decision, and validation path |
| **Review** | An artifact, repository, diff, or operating state already exists | evidence separated from assumptions, prioritized findings, and blockers |
| **Change** | Decisions are approved and repository changes are requested | the smallest safe change, compatibility notes, and verification still required |
| **Verify** | A claim needs proof | tests or measurements run, observed evidence, and residual risks |

If the user names a mode, use it. Otherwise infer the mode from intent and state the inference in one sentence. For a combined request, run **Think → Review → Change → Verify** and preserve the trace between phases. Think may stop with a decision; Review may stop with findings. Change must not claim completion before Verify. Verify must never turn a planned or unavailable check into evidence.

## Required Context Loading

| Situation | Papers |
|---|---|
| Tables, relationships, embedding vs referencing, denormalization | [021 Database Modeling](references/papers/021-database-modeling.md) |
| Keys, uniqueness, check constraints, referential integrity | [022 Database Constraints](references/papers/022-database-constraints.md) |
| Invariants, orphan prevention, partial writes, repair jobs | [026 Data Integrity](references/papers/026-data-integrity.md) |
| Index selection, order, selectivity, write overhead | [027 Indexing](references/papers/027-indexing.md) |
| Query plans, joins, batching, over-fetching, slow queries | [028 Query Design](references/papers/028-query-design.md) |
| ID strategy, collision handling, enumeration prevention | [018 Identifiers](references/papers/018-identifiers.md) |
| UTC storage, timezone conversion, DST, monotonic concerns | [019 Time & Date Handling](references/papers/019-time-and-date-handling.md) |
| Exact numeric representation, rounding, overflow | [020 Money / Numeric Precision](references/papers/020-money-numeric-precision.md) |
| Deleted-at columns, restoration, uniqueness, purging | [032 Soft Delete / Hard Delete](references/papers/032-soft-delete-hard-delete.md) |
| Retention, expiration, archival, anonymization | [033 Data Lifecycle](references/papers/033-data-lifecycle.md) |
| Append-only records, audit history, correction records | [034 Immutable Data](references/papers/034-immutable-data.md) |
| Uploads, downloads, validation, signed URLs, cleanup | [040 File Handling](references/papers/040-file-handling.md) |
| Image/video processing, async pipelines, originals | [041 Media Processing](references/papers/041-media-processing.md) |
| Full-text/fuzzy/vector search, reindexing | [042 Search](references/papers/042-search.md) |
| Row/document versioning and history | [069 Data Versioning](references/papers/069-data-versioning.md) |
| Lineage and origin tracking | [122 Data Provenance](references/papers/122-data-provenance.md) |
| Authoritative vs derived stores, freshness contracts | [123 Source of Truth](references/papers/123-source-of-truth.md) |
| Drift detection and repair across stores | [124 Data Reconciliation](references/papers/124-data-reconciliation.md) |
| Scheduled purge/cleanup ownership | [125 Cleanup Jobs](references/papers/125-cleanup-jobs.md) |

## Workflow

Use the domain workflow as shared gates, then branch by the selected mode:

- **Think:** answer the questions and stop with a reasoned decision and validation path; do not edit by default.
- **Review:** inspect the available artifact or repository and stop with evidence-backed findings; do not claim changes.
- **Change:** apply only approved decisions, then continue to Verify before claiming completion.
- **Verify:** run the relevant checks, report observed results, and label every unavailable or unrun check.

1. Identify the entities and stores involved; select primary papers (a money column touches 020 + 022 + 026; a file upload touches 040 + 033 + 026).
2. Read the primary papers fully, including invariants and failure modes.
3. Answer each paper's pre-implementation questions; label autonomous assumptions and their impact.
4. For existing schemas, run the existing-codebase checks: inspect deployed constraints, indexes, isolation settings, and real query shapes rather than trusting repository names.
5. Convert each MUST/SHOULD/AVOID/NEVER into schema and access decisions with enforcement points (constraints, indexes, policies) and tests.
6. Apply the active mode: stop at a decision in Think; stop at findings in Review; make the smallest approved safe change in Change; run precision, constraint-race, restore, and purge checks in Verify.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Companion Skills and Standalone Safety

| Type | When | Companion | Missing companion behavior |
|---|---|---|---|
| **Required** | Concurrent writers or transactional invariants cross the data boundary | `transactions-consistency` | Preserve atomic enforcement requirements and label concurrency depth missing. |
| **Handoff** | Existing data or schema must change | `migration-evolution` | Do not prescribe destructive or one-shot evolution. |
| **Recommended** | Sensitive fields, files, retention, or deletion are in scope | `security-privacy` | Preserve minimization and deletion obligations; label policy depth missing. |
| **Recommended** | Backup, restore, or reconciliation evidence is required | `production-operations` | Do not equate replication or snapshots with recovery. |

If a companion is unavailable, complete only the safe local data decision, name the missing depth, and recommend the exact technical ID or relevant installation group. Never claim unavailable material was read or weaken an integrity, precision, lifecycle, or recovery requirement.

## Output Contract

The selected mode is authoritative. Include only applicable fields below; a planned check is a validation path, not verification evidence.

Scale the output to the active mode: Think returns data decisions; Review returns findings; Change returns the repository-aware change plus pending proof; Verify returns observed integrity and lifecycle evidence with unrun checks labeled. A combined flow preserves all four phases.

1. **Papers consulted** — numbers and the sections relied on.
2. **Assumptions and unanswered questions** — labeled, with their design impact.
3. **Rule-to-decision map** — each applicable MUST/SHOULD → schema/index/policy decision, enforcement point, and test.
4. **Failure modes addressed** — precision loss, constraint races, orphaned records, index bloat, unrebuildable derived data.
5. **Verification evidence** — tests mapped to the paper's verification checklist.
6. **Lifecycle and migration notes** — retention, purge, growth, and rollout for existing data.

## Stop Conditions

Stop and revise when any of these appears:

- code is written before the primary paper's pre-implementation questions are answered or labeled;
- money, quotas, or entitlements stored in floating point;
- invariants enforced only in application code with no constraint or conditional-write backstop;
- indexes designed without the real query predicates, tenant scope, and write-cost analysis;
- identifiers that are enumerable, collision-prone, or leak internal ordering publicly without intent;
- timestamps stored without UTC policy or compared across clock sources;
- soft delete that breaks unique constraints or leaks deleted rows into queries;
- derived stores (search, caches, projections) with no rebuild or reconciliation path;
- files accepted without size, type, and signature validation, or stored without ownership and cleanup;
- retention or deletion obligations with no enforcing job;
- unbounded growth with no capacity estimate or lifecycle policy;
- any data MUST downgraded to a TODO without a documented exception.

## References

Nineteen production papers under `references/papers/`: 018 Identifiers, 019 Time & Date Handling, 020 Money / Numeric Precision, 021 Database Modeling, 022 Database Constraints, 026 Data Integrity, 027 Indexing, 028 Query Design, 032 Soft Delete / Hard Delete, 033 Data Lifecycle, 034 Immutable Data, 040 File Handling, 041 Media Processing, 042 Search, 069 Data Versioning, 122 Data Provenance, 123 Source of Truth, 124 Data Reconciliation, 125 Cleanup Jobs. Cross-domain pointers inside the papers name the sibling skill to activate.

Worked example: [exact-money pricing and soft delete](examples/worked-example-product-pricing-schema.md).
