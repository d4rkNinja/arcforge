# Implement Migrations & Evolution (`migration-evolution`)

Production expertise for changing running systems safely. A migration is a distributed system that runs while old and new versions are both live; every step must tolerate mixed versions, partial failure, and rollback — because code rollback never undoes committed data.

## What it covers

- schema migrations: online/zero-downtime ordering, locks, verification;
- expand-and-contract instead of destructive renames and type changes;
- data migrations and backfills: chunking, resuming, idempotency, load control;
- API/event schema evolution with tolerant readers;
- backward compatibility windows and deprecation sequencing;
- data synchronization while two systems coexist;
- change data capture pipelines and their failure/replay behavior;
- search index rebuilds and dual-index cutover;
- feature migration with traffic cutover and reversal triggers;
- legacy integration: strangler patterns, adapters, retirement criteria.

## When to use

Renaming or retyping columns, running backfills, evolving API or event contracts, synchronizing systems, or cutting features over — and before any "rename it and ship this afternoon."

## What a run produces

Current/target/intermediate states with version read/write matrices, ordered steps with verification gates between them, rollback or roll-forward defined per step, and coexistence tests. The skill stops work on destructive one-shot changes, backfills that overwrite newer writes, or rollback plans that assume data undoes itself.

## Works well with

- `transactions-consistency` for dual-write avoidance and outbox atomicity;
- `runtime-delivery` for deployment mechanics and health gates;
- `api-contracts` for the contracts being evolved;
- `quality-release` for compatibility testing of old and new versions.

## Try it

~~~text
Rename users.email to users.email_address and ship it this afternoon. Use
migration-evolution.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/migration-evolution/SKILL.md)
- Worked example: [a safe column rename through expand-and-contract](../../skills/migration-evolution/examples/worked-example-email-column-rename.md)
