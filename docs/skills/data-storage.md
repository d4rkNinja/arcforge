# Think Through Data & Storage (`data-storage`)

Production expertise for data that outlives code. Every column, identifier, file, and derived index is a durable decision with invariants and a lifecycle — not a convenient shape for today's feature.

## Modes

- **Think** clarifies requirements, invariants, risks, alternatives, decisions, and validation paths.
- **Review** inspects an existing artifact, repository, diff, or operating state and returns evidence-backed findings.
- **Change** applies approved decisions and keeps verification outstanding until proof is gathered.
- **Verify** reports tests, measurements, operational evidence, and residual risks without inventing missing proof.

If no mode is named, the skill infers one and states it. Combined work proceeds **Think → Review → Change → Verify**.

## What it covers

- tables, relationships, embedding vs referencing, denormalization;
- identifiers: auto-increment vs UUID/ULID/snowflake, enumeration risks;
- time and date handling: UTC policy, timezones, DST, clock skew;
- money and numeric precision — why floating point loses money;
- constraints, referential integrity, and constraint race conditions;
- indexes from real query predicates; query design and N+1 elimination;
- soft delete vs hard delete, restore, purging, uniqueness interaction;
- retention, archival, expiration, anonymization, legal hold;
- immutable/append-only records, audit history, correction records;
- file upload/download: size/type/signature validation, signed URLs, cleanup;
- media processing pipelines with original preservation;
- full-text and vector search, index synchronization, rebuilds;
- source-of-truth boundaries, provenance, reconciliation, and cleanup jobs.

## When to use

Modeling new entities, adding columns (especially money or timestamps), designing indexes, changing files or search, or defining what happens to data over its lifetime.

## What a run produces

The output follows the active mode: Think returns decisions and open questions; Review returns findings without claiming changes; Change records the approved work and pending proof; Verify returns observed evidence and explicitly labels unrun checks.

Data models with invariants backed by constraints, indexes matched to real queries, lifecycle owners for retention and purge, and rebuild paths for anything derived. The skill stops work on floating-point money, soft delete that breaks uniqueness, or derived stores with no reconciliation.

## Works well with

- `transactions-consistency` for boundaries, isolation, and concurrency;
- `migration-evolution` for changing existing schemas safely;
- `resilience-flow-control` for caches and derived-store invalidation;
- `security-privacy` for classifying and deleting sensitive fields.

## Try it

~~~text
Add a price column to products and a deleted flag so rows are never really
deleted. Use data-storage.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/data-storage/SKILL.md)
- Worked example: [exact-money pricing and soft delete](../../skills/data-storage/examples/worked-example-product-pricing-schema.md)
