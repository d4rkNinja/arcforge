# Think Through Git & Repository Workflows

Skill ID: `git-workflows`

## What this skill does

Production guidance for Git as an immutable object graph with mutable refs, distributed observations, hosted authorization, and release-policy layers. It helps an agent reason about branches, merges, rebases, worktrees, remotes, pull requests, protected refs, tags, versions, history rewrites, secrets, recovery, repository migrations, and source-to-artifact provenance before running commands.

Like every ArcForge skill, it supports Think, Review, Change, and Verify modes. A combined flow retains the exact ref, authority, recovery, and evidence ledger from the initial decision through authoritative post-change verification.

## What it covers

- object IDs, refs, HEAD, index, working trees, remotes, ancestry, and diff semantics;
- workflow selection from real release topology rather than name-driven Gitflow;
- non-fast-forward updates, leases, atomic ref operations, retries, and ambiguous push results;
- conflicts, sequencer recovery, reflogs, backups, corruption, and history migration;
- protected branches/tags, review and CI candidate identity, merge queues, signing, and audit;
- immutable release tags, semantic versions, backports, artifact digests, and provenance;
- secret incidents, untrusted CI, LFS, submodules, monorepos, and large/shallow/partial repositories.

## When to use

Use it before changing repository history or workflow; pushing or force-updating refs; creating release tags or versions; rewriting history; removing a committed secret; changing branch protections, CI, merge queues, or default branches; or recovering Git state.

## What a run produces

A verified/unknown state inventory, workflow decision tied to release requirements, exact old/new ref transition ledger, local-versus-remote authority record, recovery plan, immutable tag/commit/artifact map, actions actually taken, and explicit unresolved handoffs.

## Works well with

- `runtime-delivery` for CI/CD, builds, promotion, and deployment;
- `quality-release` for current test evidence and the final readiness verdict;
- `security-privacy` for credentials, signing, sensitive history, and untrusted CI;
- `auth-access` for hosted roles and protected-ref authority;
- `transactions-consistency` for expected-OID compare-and-swap and ambiguous retries;
- `migration-evolution` and `production-operations` for history/policy migration, backup, recovery, audit, and incidents.

## Try it

```text
Use git-workflows. We support one SaaS production line and deploy daily.
Review our branch, merge, release-tag, and CI policy; recommend the smallest safe
workflow and show how every release tag maps to the tested artifact.
```

Authoritative instructions: [SKILL.md](../../skills/git-workflows/SKILL.md)

Worked example: [published tag correction](../../skills/git-workflows/examples/worked-example-published-tag-correction.md)
