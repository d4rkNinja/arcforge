---
name: git-workflows
description: "Use when thinking through, reviewing, changing, or verifying Git repositories and version-control workflows: branches, commits, merges, rebases, cherry-picks, conflicts, worktrees, remotes, pull requests, protected refs, force pushes, tags, semantic versions, release branches, history rewrites, secret removal, merge queues, Git-aware CI, repository migrations, recovery, or source-to-artifact provenance. Distinguishes local Git state from hosted policy, authorization, and release evidence."
---

# Think Through Git & Repository Workflows

Production guidance for Git as a content-addressed graph, a distributed state machine, and one layer of a larger repository policy and release system. This skill is not a command cheat sheet and does not assume classical Gitflow is the right workflow.

**Core principle:** Observe the exact state, establish the expected old state, make the smallest authorized transition, and verify the authoritative result. A branch or tag is a mutable ref; a commit OID identifies an immutable object; hosted approvals, CI, protections, releases, and deployments are separate state.

## Domain Law

```text
NO GIT MUTATION WITHOUT:
1. the repository, worktree/index/sequencer state, and unrelated user changes inspected;
2. the exact object/ref transition and publication state identified;
3. local versus remote/hosted authority made explicit;
4. concurrency, retry, recovery, CI, release, and consumer effects handled;
5. the resulting graph, refs, worktree, policy state, and evidence verified.
```

## When to Use

Use this skill when:

- choosing Gitflow, trunk-based development, short-lived branches, release branches, or a pull-request workflow;
- creating, changing, merging, rebasing, cherry-picking, deleting, or recovering branches and commits;
- resolving conflicts or an interrupted merge, rebase, or cherry-pick;
- fetching, pulling, pushing, force-updating, or coordinating refs across clones;
- creating or publishing Git tags and software versions;
- changing protected branches/tags, required checks, reviews, merge queues, signing, or repository policy;
- designing Git-aware CI, release provenance, backports, monorepo/multi-repo workflows, LFS, or submodules;
- removing secrets or sensitive data from history, rewriting shared history, or migrating a default branch/workflow;
- diagnosing corruption, lost commits, reflog recovery, repository scale, shallow/partial/sparse clones, or cross-platform checkout behavior.

## When Not to Use

- For deployment pipeline implementation and artifact promotion, also use `runtime-delivery`.
- For the final production-readiness verdict and current test evidence, also use `quality-release`.
- For secret rotation, credential lifecycle, cryptographic policy, or untrusted CI boundaries, also use `security-privacy`.
- For a whole-system or organization-wide source-platform architecture decision, use `system-architecture-harness`; use `architecture-review-gate` for independent approval.

## Required Reference

Read [147 Production-Grade Git and Git Flow](references/papers/147-production-grade-git-and-git-flow.md) in full before changing repository history, refs, workflow, policy, or release identity. Recheck the installed Git version and current hosting-provider contract for version-sensitive behavior.

## Select the Operating Mode

| Mode | Use when | Required result |
|---|---|---|
| **Think** | The workflow, topology, version policy, or migration is not settled | requirements, release topology, alternatives, exact invariants, decision, and validation path |
| **Review** | A repository, graph, policy, CI/release design, or incident state already exists | observed state separated from claims, prioritized findings, blockers, and safe next actions |
| **Change** | The transition is approved and repository changes are requested | the smallest authorized local or hosted transition, recovery point, and verification still required |
| **Verify** | A Git, policy, tag, or release claim needs proof | exact local and authoritative remote observations, checks run, provenance, and residual risk |

If the user names a mode, use it. Otherwise infer the mode from intent and state the inference in one sentence. For a combined request, run **Think → Review → Change → Verify** and retain the ref, authority, and evidence ledger across phases. Think and Review do not mutate by default. Change never implies permission to publish, rewrite shared history, change hosted policy, or create a release unless that operation class is explicitly authorized. Verify never treats cached remote-tracking refs, old CI, a plan, or an ambiguous transport result as current authoritative evidence.

## Workflow

Use the shared gates below, then apply the active mode:

- **Think:** choose topology and policy from actual release/support requirements; stop with a decision and validation path.
- **Review:** inspect the available graph, repository, hosted state, and release evidence; stop with findings and blockers.
- **Change:** apply only the explicitly authorized transition classes, preserving recovery and unrelated work, then continue to Verify.
- **Verify:** observe exact refs and policy at the authoritative source, bind checks and artifacts to the candidate, and label unrun or inaccessible checks.

1. **Classify the request.** Separate read-only inspection, working-tree/index edits, local object/ref creation, remote ref publication, hosted-policy change, release publication, and history migration. Do not let authorization for one class imply another.
2. **Inspect before mutation.** Read repository instructions and status; inspect staged/unstaged/untracked changes, HEAD/detached state, sequencer operations, worktrees, shallow/partial/sparse state, branches/upstreams/tags/remotes, release/version conventions, CI, and documented hosted policy. Preserve unrelated work.
3. **Record knowledge state.** Mark material facts as local-observed, authoritative-remote/host-observed, claimed, stale, or unknown. A remote-tracking ref is a cached observation. Do not invent protections, approvals, CI state, publication state, or authority.
4. **Model the transition.** Name repository, ref, current OID, expected old OID, desired new OID, consumers, policy gates, and recovery point. Use graph ancestry for ancestry questions and full OIDs for correctness.
5. **Choose topology from release requirements.** Determine supported release lines, integration cadence, certification time, backport policy, and deployment source. Use the least complicated workflow that represents those facts; do not create classical Gitflow branches merely because the phrase “Git flow” appears.
6. **Close concurrency and failure paths.** Treat non-fast-forward and lease mismatch as changed preconditions. After an ambiguous push result, observe the authoritative ref before retrying. Require explicit expected OIDs for intentional ref replacement and atomic capability for all-or-nothing multi-ref updates.
7. **Apply the authority gate.** Use the operation matrix below. Stop when exact target, scope, publication state, or authority is unresolved.
8. **Apply tag and release gates.** Verify version policy, tag existence locally and remotely, exact candidate OID, current checks/approvals, signer policy, artifact digest, and source-to-artifact provenance. Never silently move an already-published version.
9. **Execute the smallest authorized operation.** Keep destructive history migration separate from ordinary development. Prefer reversible, additive steps and ordinary fast-forward updates; never bypass a policy failure by changing force flags.
10. **Verify and report.** Inspect graph/ref targets, worktree/index/sequencer state, authoritative remote/host state when changed, relevant tests/checks, artifact mapping, audit event, and recovery result. Report anything not verified.

## Authority and Mutation Gate

| Operation class | Minimum condition before proceeding |
|---|---|
| Read local graph/config/status | In scope; do not expose secrets or mutate state. |
| Edit working tree or index | Requested code change owns the paths; unrelated changes are preserved. |
| Create local commit, branch, worktree, or tag | Explicit task scope, exact base/target, repository convention, and post-operation verification. |
| Fetch or inspect hosted state | Relevant remote/account is in scope; treat fetched data as a new observation, not proof of mutation authority. |
| Push a branch or publish a tag | Explicit authorization for that remote action, exact remote/ref/OID, current policy/checks, and verified result. |
| Delete a remote ref or change repository policy | Explicit authorization for the exact destructive/hosted action, accountable owner, recovery/containment, and audit path. |
| Rewrite a shared ref or bypass protection | Exceptional explicit authorization, verified consumers, independently recoverable backup, tested recovery, exact expected old OID, coordinated migration, and post-write reconciliation. |

The model cannot approve its own bypass. Requester seniority, a deadline, transport authentication, or possession of credentials does not establish authorization for a protected transition.

## Tag and Version Gate

- Define the public compatibility contract before applying Semantic Versioning; commit labels alone do not prove a version increment.
- Treat local tag creation, remote tag publication, hosted release creation, artifact publication, and deployment as distinct actions.
- Before a new release tag, verify the tag does not already exist in the authoritative repository, the exact target OID is intended, current required checks apply to that candidate, and the built artifact digest/provenance maps to it.
- Prefer annotated release tags; require signing only when the repository has an established identity, key-management, and verification policy. Never invent a signature or weaken verification to create a tag.
- A published release identifier is immutable. Correct it with a new version or governed corrective release; never move or silently replace the existing tag.

## History Rewrite and Secret Incident Gate

Treat shared history rewriting as a migration: coordinate or freeze writes, preserve an independently restorable canonical backup, enumerate every intended ref and consumer, validate the rewritten graph, record old-to-new identities, update CI/integrations/open reviews, handle forks/clones/caches/artifacts/LFS, re-attest releases where required, and verify authoritative replacement.

A committed credential is an incident. Revoke or rotate it, contain propagation, and investigate use independently of any revert or rewrite. “Removed from canonical reachability” is not “eradicated from every copy.” Never print the secret while diagnosing or documenting it.

## Bypass and Exception Record

Any permissible non-critical bypass must record the exact unmet rule, affected refs/repositories, rationale, authorized decision owner and governance basis, observed evidence, compensating controls, expiry/review trigger, containment and recovery plan, and follow-up owner/date. Critical secret exposure, unauthorized protected-ref mutation, uncoordinated shared-history loss, or release-identity ambiguity remains blocked.

## Companion Skills and Standalone Safety

| Type | When | Companion | Missing companion behavior |
|---|---|---|---|
| **Required** | CI/CD, build identity, artifact promotion, or deployment is changed | `runtime-delivery` | Preserve candidate and artifact identity; do not invent pipeline or deployment evidence. |
| **Required** | Credentials, signing, untrusted CI, or sensitive history is involved | `security-privacy` | Treat exposed credentials as an incident and preserve least privilege; do not choose or waive security controls. |
| **Recommended** | Current checks, failure tests, or a release verdict is needed | `quality-release` | Keep the exact evidence gaps visible and do not claim readiness. |
| **Recommended** | Hosting roles, workload identity, or protected-ref authority is assessed | `auth-access` | Require explicit actor, action, target, and governance; do not infer authority from credentials. |
| **Optional depth** | Expected-OID updates, ambiguous retries, or multi-system publication semantics need deeper analysis | `transactions-consistency` | Use explicit expected state and reconciliation; do not claim cross-system atomicity. |
| **Handoff** | Default-branch, workflow, shared-history, or compatibility migration is designed | `migration-evolution` | Preserve mixed-consumer compatibility and identify the unresolved migration sequence. |
| **Recommended** | Backup, restore, audit, or incident response evidence is needed | `production-operations` | State recovery and audit requirements and label drills unrun. |
| **Handoff** | Organization-wide repository topology or source-platform architecture must be decided | `system-architecture-harness` | Bound the repository-local decision and identify the unresolved platform decision. |
| **Handoff** | Independent approval of a repository or release design is requested | `architecture-review-gate` | Return Git evidence without self-approving the design. |

If a companion is unavailable, complete only the safe repository-local decision, name the missing depth, and recommend the exact technical ID or installation group. Never claim unavailable material or hosted evidence was used, and never weaken an authority, immutable-release, secret-response, or shared-history blocker because companion depth is missing.

## Output Contract

1. **Outcome and operation classes** — what is requested; what is read-only, local, remote, hosted, release, or destructive.
2. **State and evidence inventory** — observed local/authoritative facts, claims, stale observations, and unknowns.
3. **Topology decision** — release lines, integration model, alternatives, trade-offs, and why the chosen workflow fits.
4. **Ref transition ledger** — repository/ref, current OID, expected old OID, desired new OID, and concurrency behavior.
5. **Authority record** — exact authorized actions, protected boundaries, approver/governance when required, and actions not authorized.
6. **Safety and recovery plan** — unrelated-work preservation, backup/restore, consumers, ambiguous outcomes, abort criteria, and reconciliation.
7. **Version/release map** — version/tag → commit OID → current CI/review evidence → provenance → immutable artifact digest.
8. **Actions and verification** — commands or changes actually performed, authoritative result, checks run, audit evidence, and unverified items.
9. **Boundary handoffs** — applicable sibling skills, owner, enforcement point, evidence, and unresolved obligations.

## Stop Conditions

Stop and revise when any of these appears:

- unrelated dirty, staged, untracked, or worktree changes could be overwritten;
- a merge, rebase, or cherry-pick is already in progress and the next action ignores it;
- repository, remote, ref, target OID, expected old OID, publication state, or authority is ambiguous;
- a remote push, tag publication, deletion, policy change, bypass, or release is attempted without explicit scope;
- non-fast-forward or lease rejection is answered with plain force or blind retry;
- implicit `--force-with-lease` is treated as proof that a shared rewrite is safe;
- a published tag or released version would be moved, replaced, or rebuilt with different contents;
- review or CI evidence belongs to an old head/base rather than the exact candidate or merge-queue result;
- a committed secret is treated as fixed by revert, deletion, or history rewrite without credential response;
- untrusted candidate code can access privileged credentials, runners, caches, publication, or deployment authority;
- branch deletion, reflog, or Git backup is claimed to provide privacy erasure or durable recovery without proof;
- Git revert is presented as reversal of database, message, external, artifact, or production state;
- classical Gitflow or environment branches are introduced without release-topology evidence;
- hosted policy, approval, signing, release, or deployment facts are inferred from the local clone.

## References

- [147 Production-Grade Git and Git Flow](references/papers/147-production-grade-git-and-git-flow.md)

## Worked Example

- [Published tag correction under stale CI](examples/worked-example-published-tag-correction.md)
