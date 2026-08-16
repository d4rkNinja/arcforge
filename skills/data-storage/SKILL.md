---
name: data-storage
description: "Use when implementing or changing data models and storage code: database schema design, identifiers (UUID/ULID/snowflake), time and date handling, money and numeric precision, constraints and referential integrity, indexing, query design and N+1 fixes, soft delete, data lifecycle and retention, immutable records and audit history, file upload/download handling, media processing, search, data versioning, provenance, source-of-truth boundaries, reconciliation, and cleanup jobs. Loads production implementation papers with MUST/SHOULD/AVOID/NEVER rules, failure modes, and verification checklists to read before writing code. For transactions, isolation, and idempotency use transactions-consistency; for schema migration sequencing use migration-evolution; for caching use resilience-flow-control; for whole-system architecture use system-architecture-harness."
---

# Data & Storage Implementation

## Overview

Implementation intelligence for data modeling and storage. Each reference paper captures the correctness work that schema-first drafts miss: precision hazards, constraint-race conditions, index design from real predicates, soft-delete interactions with uniqueness, file-handling abuse, derived-store rebuilds, and retention obligations.

**Core principle:** Data outlives code. Every column, identifier, file, and derived index is a durable decision with invariants, an owner, and a lifecycle — not a convenient shape for today's feature.

## Implementation Law

```text
NO DATA IMPLEMENTATION WITHOUT:
1. the primary paper(s) for the data being modeled read in full first;
2. the paper's "Questions that must be answered before implementation"
   answered, or each open point labeled as an assumption;
3. "Existing-codebase checks" run when changing an existing schema or store;
4. every applicable MUST mapped to a decision (constraint, index, policy),
   a test, or a documented exception — never silently downgraded.
```

## When to Use

Use this skill when implementing or changing:

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

1. Identify the entities and stores involved; select primary papers (a money column touches 020 + 022 + 026; a file upload touches 040 + 033 + 026).
2. Read the primary papers fully, including invariants and failure modes.
3. Answer each paper's pre-implementation questions; label autonomous assumptions and their impact.
4. For existing schemas, run the existing-codebase checks: inspect deployed constraints, indexes, isolation settings, and real query shapes rather than trusting repository names.
5. Convert each MUST/SHOULD/AVOID/NEVER into schema and access decisions with enforcement points (constraints, indexes, policies) and tests.
6. Implement the smallest safe slice; carry the paper's verification checklist (precision edges, constraint races, restore, purge) into the test plan.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Boundary Map

| If the task also involves | Also use |
|---|---|
| Transaction boundaries, isolation, concurrency control | `transactions-consistency` (023, 024, 025) |
| Migration sequencing and backfills | `migration-evolution` (029, 030, 031) |
| Caches and derived-store invalidation | `resilience-flow-control` (037, 131) |
| Search index sync pipelines | `migration-evolution` (130) or `async-messaging` (043) |
| Classification and deletion of sensitive fields | `security-privacy` (066) |
| Backup/restore of the new stores | `production-operations` (076, 077) |

## Output Contract

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
