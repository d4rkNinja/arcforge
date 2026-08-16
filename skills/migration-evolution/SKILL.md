---
name: migration-evolution
description: "Use when implementing or changing data or contract evolution: schema migrations and zero-downtime deploy ordering, expand-and-contract patterns, data migrations and backfills with chunking and resumability, API and event schema evolution, backward compatibility windows, data synchronization between systems, change data capture, search index synchronization during reindexing, feature migration and traffic cutover, and legacy-system integration/strangler migration. Loads production implementation papers with MUST/SHOULD/AVOID/NEVER rules, failure modes, and verification checklists to read before writing code. For transaction internals of dual-write avoidance use transactions-consistency; for deployment mechanics use runtime-delivery; for whole-system replatforming architecture use system-architecture-harness."
---

# Migrations & Evolution Implementation

## Overview

Implementation intelligence for changing running systems safely. Each reference paper captures the sequences that prevent outages: expand-and-contract instead of in-place renames, resumable backfills that do not overwrite newer writes, compatibility windows for old clients, CDC pipelines with reconciliation, and cutover plans with genuine rollback.

**Core principle:** A migration is a distributed system that runs while the old and new versions are both live. Every step must tolerate mixed versions, partial failure, and rollback — code rollback never undoes committed data.

## Implementation Law

```text
NO MIGRATION WITHOUT:
1. the primary paper(s) for the change type read in full first;
2. current state, target state, and every intermediate state written
   down before the first migration step;
3. "Existing-codebase checks" run against deployed versions, consumers,
   and retained data — not just the latest code;
4. every applicable MUST mapped to a migration step, a verification gate,
   or a documented exception.
```

## When to Use

Use this skill when implementing or changing:

- database schema migrations, online/zero-downtime migrations, lock behavior;
- additive vs destructive changes, column renames, type changes, nullability flips;
- data migrations and backfills: chunking, resuming, idempotency, rate control;
- API and event schema evolution with old consumers;
- backward/forward compatibility windows and deprecation sequencing;
- data synchronization between two systems during transition;
- change data capture pipelines and their failure/replay behavior;
- search index rebuilds and dual-index cutover;
- feature migration: moving behavior between services with traffic cutover;
- legacy integration: strangler patterns, adapters, retirement sequencing.

## When Not to Use

- Transaction/outbox internals for avoiding dual writes: use `transactions-consistency` (047).
- CI/CD pipeline mechanics and deployment tooling: use `runtime-delivery` (106, 107).
- Whole-system replatforming or rewrite decisions: use `system-architecture-harness` (references 18).
- Contract design for new APIs: use `api-contracts`.

## Required Context Loading

| Situation | Papers |
|---|---|
| Additive vs destructive schema change, dual-read/dual-write | [029 Schema Evolution](references/papers/029-schema-evolution.md) |
| Online migrations, locks, ordering, rollback limits | [030 Database Migrations](references/papers/030-database-migrations.md) |
| Backfills: chunking, resume, idempotency, load control | [031 Data Migrations & Backfills](references/papers/031-data-migrations-and-backfills.md) |
| Event/API schema versioning and tolerant readers | [070 API / Event Schema Evolution](references/papers/070-api-event-schema-evolution.md) |
| Compatibility windows, old-client behavior | [071 Backward Compatibility](references/papers/071-backward-compatibility.md) |
| Two systems coexisting: precedence and reconciliation | [072 Data Synchronization](references/papers/072-data-synchronization.md) |
| CDC pipelines, replay, failure handling | [073 Change Data Capture](references/papers/073-change-data-capture.md) |
| Dual-index rebuild and cutover | [130 Search Index Synchronization](references/papers/130-search-index-synchronization.md) |
| Deploy ordering for mixed versions | [134 Zero-Downtime Changes](references/papers/134-zero-downtime-changes.md) |
| Moving a feature with traffic cutover | [135 Feature Migration](references/papers/135-feature-migration.md) |
| Strangler patterns and legacy coexistence | [136 Legacy-System Integration](references/papers/136-legacy-system-integration.md) |

## Workflow

1. Write the current state, target state, and each intermediate state, including which versions can read/write each representation.
2. Select and read the primary papers for the change type fully.
3. Answer the paper's pre-implementation questions; label autonomous assumptions and their impact.
4. Run the existing-codebase checks: inventory deployed clients, consumers, workers, retained messages/jobs, and data that already violates the target shape.
5. Convert each MUST/SHOULD/AVOID/NEVER into ordered migration steps with verification gates between them (counts match, behavior compared, usage at zero) and explicit rollback or roll-forward at each step.
6. Implement the smallest safe slice; carry the paper's verification checklist (mixed-version coexistence, interrupted backfill resume, replayed events) into the test plan.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Boundary Map

| If the task also involves | Also use |
|---|---|
| Dual-write avoidance and outbox atomicity | `transactions-consistency` (047, 048) |
| Deployment mechanics, health gates, CI/CD | `runtime-delivery` (106, 107) |
| Compatibility testing of old/new clients | `quality-release` (090, 093) |
| Reconciliation observability during migration | `production-operations` (124 paths, 057) |
| Schema constraint/index design of the target | `data-storage` (021, 022) |
| Rewrite/monolith-decomposition architecture | `system-architecture-harness` |

## Output Contract

1. **Papers consulted** — numbers and the sections relied on.
2. **State plan** — current, target, and intermediate states with version read/write matrices.
3. **Assumptions and unanswered questions** — labeled, with their design impact.
4. **Rule-to-decision map** — each applicable MUST → migration step, verification gate, and rollback/roll-forward action.
5. **Failure modes addressed** — interrupted backfill, mixed-version writes, replayed old events, rollback with newer data.
6. **Verification evidence** — coexistence tests, resumability drills, count/behavior comparisons, rollback rehearsal.

## Stop Conditions

Stop and revise when any of these appears:

- code is written before current/target/intermediate states are written down;
- a destructive or renaming change without expand-and-contract sequencing;
- a backfill without chunking, resumability, idempotency, or protection against overwriting newer writes;
- a dual write with no reconciliation or precedence rule;
- a schema/event change with no compatibility window for old clients, consumers, or retained messages;
- a deployment order that lets a version write what another version cannot read;
- a rollback plan that assumes data changes undo themselves;
- a cutover with no traffic verification or reversal trigger;
- a CDC/reindex path with no failure recovery or replay behavior;
- a legacy integration with no retirement criterion;
- any migration MUST downgraded to a TODO without a documented exception.

## References

Eleven production papers under `references/papers/`: 029 Schema Evolution, 030 Database Migrations, 031 Data Migrations & Backfills, 070 API / Event Schema Evolution, 071 Backward Compatibility, 072 Data Synchronization, 073 Change Data Capture, 130 Search Index Synchronization, 134 Zero-Downtime Changes, 135 Feature Migration, 136 Legacy-System Integration. Cross-domain pointers inside the papers name the sibling skill to activate.

Worked example: [a safe column rename through expand-and-contract](examples/worked-example-email-column-rename.md).
