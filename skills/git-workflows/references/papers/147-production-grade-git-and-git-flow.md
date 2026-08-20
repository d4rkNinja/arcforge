# 147. Production-Grade Git and Git Flow

> **Purpose:** This is an implementation-intelligence paper for AI coding agents and backend engineers. It covers Git’s object graph, repository state, workflow topology, hosted collaboration policy, remote concurrency, CI trust, release provenance, recovery, scale, and migrations. It is not a command tutorial.

> **Normative language:** **MUST**, **MUST NOT/NEVER**, **SHOULD**, **SHOULD NOT/AVOID**, and **MAY** are used in the BCP 14 sense where written in capitals. See [S001](#s001) and [S002](#s002). Research and provider behavior were checked through **2026-08-20**; recheck living documentation and the deployed Git/hosting versions before implementation.

## 1. Executive engineering summary

Git correctness is graph correctness plus distributed-state correctness plus policy correctness. Git stores immutable, content-addressed objects; refs provide mutable names; clones hold divergent observations; hosted platforms arbitrate protected ref transitions; CI validates candidate states; release systems bind accepted source to immutable artifacts. Gitflow, trunk-based development, GitHub-style flow, and release-branch models are collaboration policies layered over these mechanics, not properties of Git itself.

A production workflow must preserve exact object identity, explicit old/new ref preconditions, review/check freshness, least-privilege automation, secret-remediation limits, rollback semantics, and evidence that the bytes tested are the bytes released. A basic workflow remembers commands; an experienced agent asks which object, ref, authority, candidate, race, side effect, and recovery path each command changes.

## 2. Questions that must be answered before implementation

- What exact Git object/OID, ref, merge candidate, artifact digest, and deployment record are authoritative?
- Is this SaaS/CD, periodically released software, or multiple concurrently supported versions, and which topology follows?
- Which actor, workload identity, repository role, ruleset, protected ref, approval, and bypass authority can perform each mutation?
- What is the expected old OID, proposed new OID, idempotency key, timeout, retry class, and ambiguous-outcome reconciliation path?
- Which approvals/checks become stale after a push, target-branch change, queue reorder, workflow/config change, or dependency update?
- Does any untrusted code execute with credentials, access protected variables/runners, reuse caches, or influence privileged artifacts?
- What source, artifact, deployment, database, external-side-effect, and secret-remediation rollback paths exist?
- Are tags immutable, signed, protected, and mapped to reproducible artifacts under the public compatibility/versioning policy?
- Are the repository and CI shallow, partial, sparse, LFS-backed, submodule-based, multi-worktree, or cross-repository?
- What default-branch, ruleset, merge-method, signing, release, or history migration is in flight, and how will active consumers be protected?
- What evidence is executed versus planned, claimed, unavailable, or contradicted, and who owns the next check?

## 3. Existing-codebase checks before changing anything

- [ ] Inspect `git status`, current branch/HEAD, worktrees, in-progress merge/rebase/cherry-pick state, remotes, tracking refs, shallow/partial/sparse configuration, LFS, submodules, and alternates.
- [ ] Map branch/tag/ref topology, default HEAD, protected refs, rulesets, required checks, CODEOWNERS, review/merge methods, queue events, bypass actors, and audit retention.
- [ ] Search CI workflows, scripts, hooks, release jobs, deployment triggers, caches, artifacts, credential scopes, OIDC claims, runner labels, and mutable action/dependency references.
- [ ] Trace the source OID from checkout through tests, artifacts, provenance, deployment, rollback, and audit; prove the bytes are the same candidate.
- [ ] Inventory open requests, active release/backport lines, downstream clones/forks, tags, submodule consumers, LFS objects, and external repository coordination.
- [ ] Inspect repository policy and history for secrets, regulated data, legal holds, previous rewrites, bypasses, incidents, and retention requirements.
- [ ] Reproduce risky remote behavior in a disposable bare remote with two clones; preserve a baseline and do not use production refs for experiments.
- [ ] Read actual Git/hosting versions and provider documentation for behavior that affects atomic pushes, rulesets, merge queues, signatures, protected resources, OIDC, and secret removal.
- [ ] Record owners, evidence links, expiry, rollback/forward-fix, and unresolved cross-skill obligations for every exception or “not applicable” decision.

## 4. Correctness model and production invariants

1. **Object invariant:** the complete OID identifies the exact object; commits and trees are immutable after creation.
2. **Ref invariant:** mutable refs move only under an explicit authority and expected-old-state policy.
3. **Observation invariant:** local remote-tracking refs, CI checkouts, caches, and queue candidates are observations with freshness and identity, not authoritative truth by themselves.
4. **Candidate invariant:** every approval, check, artifact, and deployment record binds to the exact candidate OID or immutable merge candidate.
5. **Trust invariant:** untrusted repository code cannot reach credentials or privileged mutation authority merely because it was checked out.
6. **Recovery invariant:** source rollback, artifact rollback, deployment rollback, database rollback, and secret eradication are separate state machines.
7. **Evidence invariant:** a plan, claim, or policy intention is not executed evidence; evidence must identify the artifact, configuration, environment, time, and inspected result.
8. **Migration invariant:** changing branch, tag, workflow, or history policy is a compatibility migration with consumer inventory and rollback.

## 5. Architecture decisions and conflicting approaches

| Decision | Trade-off | Production guidance |
|---|---|---|
| Trunk-based vs Gitflow | Short-lived integration reduces divergence; supported release lines may require explicit branches. | Choose from actual release/support topology, not the request’s vocabulary. |
| Merge vs squash vs rebase | Topology, bisectability, reviewability, and rewrite costs differ. | Make the method part of the repository contract and test it. |
| Client hooks vs hosted/server policy | Client hooks are fast feedback and bypassable; server controls are authoritative. | Enforce critical invariants at protected refs/rulesets/receive hooks. |
| Force-with-lease vs transactional update | Lease protects one expected state; multi-ref invariants need transactions/atomic capability. | Use explicit old OIDs and verify server atomic support. |
| Revert vs history rewrite | Revert preserves public history; rewrite may be required for secrets but changes identities. | Prefer revert for shared code; treat sensitive-data rewrite as a migration. |
| Local reflog vs canonical backup | Reflog is local and expiring; backups support loss recovery. | Test independent restore and integrity verification. |

## 6. Ownership, state, and lifecycle

Model a workflow as `discover → classify authority → observe → plan → review → mutate conditionally → verify authoritative state → publish/audit → recover or rollback`. Record actor, repository, ref, expected old OID, proposed new OID, policy decision, evidence state, request/run ID, timestamp, and rollback. No agent may silently expand a local change into a remote write, protected-ref bypass, tag movement, history rewrite, or deployment.

## 7. Data, API, and release-contract implications

Any automation API or tool interface that mutates Git state MUST make target repository/ref, expected old OID, proposed new OID, authorization scope, dry-run behavior, idempotency key, timeout, retry classification, and post-write verification explicit. Use opaque OID fields rather than assuming SHA-1 forever. Bind artifact records to source OID and digest. Represent hosted policy and evidence as separate data with freshness, owner, and expiry rather than inferring them from commit metadata.

## 8. Subtopic-by-subtopic implementation intelligence



### 8.1. Git objects, commits, trees, refs, and object identifiers

Git is a content-addressed object database. Blobs hold content, trees describe snapshots, and commits identify a tree plus parent and metadata relationships. The complete object identifier (OID), not an abbreviated display prefix, identifies the exact object. A commit is immutable after creation; a branch or tag is a mutable name pointing at an object. Annotated tags add a signed or otherwise auditable release object but are still refs whose movement must be governed. The protected canonical repository, not an arbitrary clone, is the policy authority for accepted ref transitions. See [S141](#s141), [S143](#s143), and [S150](#s150).

### 8.2. Working tree, index, HEAD, and remote state

Keep working tree, index, HEAD/current commit, local branch refs, and remote-tracking refs distinct. `git add` changes the index, `git commit` creates an object and moves a local ref, and `git push` requests a remote ref transition. `git diff`, `git restore`, `git reset`, and `git revert` operate on different state layers. A detached HEAD is valid, especially in CI; deployment identity MUST use an OID or immutable artifact mapping rather than a branch label. A remote-tracking ref is a cached observation, not proof of current remote state. See [S141](#s141) and [S142](#s142).

### 8.3. Reachability, ancestry, revision ranges, and diff semantics

Use graph reachability and ancestry predicates for ancestry questions; timestamps and commit-message order are not substitutes. Define whether “changes in a branch” means commits unique to a ref, a merge-base range, first-parent history, or a path-filtered diff. Revision expressions must be explicit about symmetric differences, merge bases, and deleted refs. Rename detection is an interpretation based on similarity thresholds, not a permanent object-level fact. Build and release records MUST retain the exact candidate OID and evaluated range. See [S141](#s141) and [S143](#s143).

### 8.4. Filesystem portability, attributes, renames, and worktrees

Repositories cross case-sensitive and case-insensitive filesystems, newline conventions, and symlink capabilities. Use `.gitattributes` for line-ending and binary normalization; do not treat `.gitignore` as a way to hide already-tracked files or `assume-unchanged` as a semantic ignore. Test case collisions, CRLF/LF changes, symlink behavior, generated files, and path limits on supported developer and CI platforms. Inspect linked worktrees before branch deletion, forced checkout, or maintenance. See [S141](#s141) and [S143](#s143).

### 8.5. Branching models and release topology

Choose trunk-based development, GitHub-style flow, Gitflow, release branches, or another topology from actual deployment and support topology. Gitflow is a specific model and is most defensible when multiple versions are supported or releases are explicitly staged; it is not a synonym for “use Git.” Prefer the least complicated model that expresses the real lifecycle, use short-lived branches and feature controls where safe, and document the authoritative line for fixes and backports. See [S145](#s145), [S146](#s146), and [S158](#s158).

### 8.6. Merge, squash, rebase, fast-forward, and cherry-pick

Merge commits preserve branch topology; squash creates one new commit; rebase rewrites commit identities; fast-forward moves a ref without creating a merge commit; cherry-pick applies a selected change as a new commit. Select the method for bisectability, auditability, release/backport policy, and rollback behavior. Rebase private work when useful, but do not rewrite shared history without a migration plan and consumer inventory. Always inspect the resulting diff and run semantic tests after integration. See [S141](#s141), [S145](#s145), and [S158](#s158).

### 8.7. Conflicts, sequencers, stash, and dirty state

Conflicts mean Git cannot determine a unique safe result, not that a command should be bypassed. Understand base and both sides, construct the intended program, stage the resolution, run relevant checks, and continue or abort the sequencer. Detect merge/rebase/cherry-pick state before starting another operation. `rerere` MAY accelerate repeated resolutions but reused resolutions require review. Dirty worktrees and `stash pop` are not transactional guarantees; preserve a recoverable starting point. See [S141](#s141).

### 8.8. Pull requests, approvals, required checks, and merge queues

Pull/merge requests are state machines: draft, reviewable, checks running, changes pushed, approved, mergeable, merged, closed, or superseded. Bind approvals and checks to the concrete commit or merge candidate, invalidate stale decisions after material changes, and treat required checks, CODEOWNERS, protected branches, rulesets, and merge queues as hosted policy state outside Git objects. A merge queue must test the candidate that includes the current target branch and queued predecessors; workflows must handle the platform’s queue event. See [S147](#s147), [S148](#s148), [S149](#s149), [S153](#s153), and [S158](#s158).

### 8.9. Ref concurrency, force-with-lease, transactions, and atomic pushes

A remote ref update is compare-and-swap: establish expected old OID, propose new OID, let the server reject if the precondition changed, and reconcile. Prefer `--force-with-lease` with an explicit expected state over plain `--force`; the implicit lease can derive from stale local remote-tracking state. Use local ref transactions and request atomic multi-ref pushes when a logical invariant spans refs, but verify server capability because one CLI invocation is not automatically a distributed transaction. Remote mutation requires explicit authority, target, reason, and post-write verification. See [S142](#s142) and [S144](#s144).

### 8.10. Idempotency, retry classification, ambiguous writes, and consistency

Object writes may be naturally content-addressed and idempotent while commits, merges, reverts, cherry-picks, and ref movements are not. Define automation by desired ref state and explicit old/new OIDs. Classify failures before retrying: pre-send failure, rejected precondition, confirmed success with lost response, or ambiguous outcome. After an ambiguous push, observe authoritative remote state and reconcile by operation identity; do not blindly repeat a force mutation. Remote-tracking refs and caches are stale observations, so eventual agreement must not replace a protected source of truth. See [S137](#s137), [S139](#s139), and [S142](#s142).

### 8.11. Recovery, reflogs, corruption, backups, and application rollback

Recovery uses the least destructive source of truth available: current refs, remote refs, other clones, reflogs, dangling objects, canonical mirrors, and tested backups. Reflogs help recover local ref movement but are not backups or regulatory retention. Run integrity checks when copying, rewriting, or restoring repositories, and test restoration rather than merely creating backups. A Git revert changes source history; it does not automatically undo a database migration, external side effect, deployment, or data exposure. See [S141](#s141), [S146](#s146), and [S156](#s156).

### 8.12. Repository trust, identity, authorization, protected refs, and bypasses

Treat repository configuration, hooks, filters, submodule URLs, and tooling as potentially hostile input. Distinguish author/committer metadata, cryptographic signature, authenticated actor, and authorization to update a protected ref. Enforce critical invariants server-side through protected refs, rulesets, receive hooks, review policy, and audit; client hooks are feedback and may be skipped. Bypasses MUST be narrowly scoped, explicitly authorized, time-bounded where possible, auditable, and followed by remediation. See [S141](#s141), [S147](#s147), [S148](#s148), and [S154](#s154).

### 8.13. Untrusted CI, credentials, runners, workflow dependencies, and OIDC

Pre-merge code is untrusted with respect to secrets and privileged credentials. Separate unprivileged checkout/test from privileged publish/deploy; do not expose production credentials to arbitrary forks or untrusted merge-request pipelines. Minimize workflow-token permissions, use short-lived identity/OIDC where possible, pin security-sensitive workflow dependencies to immutable identities, and isolate runners, caches, artifacts, and workspace reuse. A cache key or artifact MUST NOT allow untrusted code to influence a privileged job. See [S152](#s152), [S154](#s154), [S157](#s157), and [S159](#s159).

### 8.14. Commit and tag signing, provenance, audit, and release evidence

Signatures provide cryptographic evidence about an object and its signing identity under a verifier policy; they do not prove review, CI, authorization, or deployment. Release provenance MUST bind source OID, policy decision, workflow/run identity, artifact digest, and deployment evidence. Preserve administrative audit events for approvals, bypasses, permission changes, ref updates, tag deletion, and deployment. Consumers must verify provenance rather than merely store it. See [S150](#s150), [S156](#s156), [S157](#s157), and [S158](#s158).

### 8.15. Secrets, sensitive data, branch deletion, and history rewriting

A secret committed to history remains in earlier objects, clones, forks, caches, pull-request refs, and backups even after a later revert. Credential remediation (revoke/rotate and investigate use) is mandatory; history filtering is a coordinated migration, not a cosmetic cleanup. Branch deletion removes a name, not necessarily object reachability or LFS content. Distinguish removal from the canonical ref from eradication of every copy, record retention/legal-hold constraints, and communicate rewritten identities to consumers. See [S151](#s151), [S160](#s160), and [S161](#s161).

### 8.16. Release tags, versioning, artifacts, release branches, and backports

Release tags and artifacts need stable, unique identity. Annotated protected tags, SemVer rules, artifact digests, and provenance should form a reproducible mapping from release name to exact source and bytes. Do not move a published version tag; SemVer released contents are immutable. Release branches are compatibility lines, not environments by default. Test the actual release/backport target after applying a fix, and keep trunk authoritative when the support policy permits. See [S145](#s145), [S155](#s155), [S156](#s156), and [S157](#s157).

### 8.17. Repository scale, maintenance, sparse, partial, and shallow clones

Large repositories impose bounded resource and history assumptions. Measure before adding commit-graph, multi-pack-index, maintenance, filesystem-monitor, sparse, partial, or shallow-clone complexity. Sparse checkouts may omit files; partial clones may fetch missing objects later; shallow clones have incomplete ancestry. History-dependent versioning, changelog, merge-base, and recovery logic must detect these modes and fail clearly rather than treating missing history as proof of nonexistence. See [S141](#s141) and [S162](#s162).

### 8.18. Git LFS, submodules, monorepos, and cross-repository changes

Git LFS creates a separate pointer/object lifecycle; submodules pin another repository and introduce URL, credential, availability, and recursive trust boundaries. Monorepos trade repository coordination for scale, ownership, and selective CI complexity. Multiple repositories cannot commit atomically with ordinary Git; cross-repository changes require compatibility windows, ordered rollout, explicit coordination, and recovery. Pin nested dependencies to exact immutable identities and test unavailable/unauthorized cases. See [S141](#s141), [S160](#s160), and [S161](#s161).

### 8.19. Default-branch and workflow-policy migrations

Default-branch renames, merge-method changes, signing enforcement, ruleset changes, merge queues, and Gitflow-to-trunk migrations are ecosystem migrations. Inventory remote HEAD, branch protections, CI triggers, deployment rules, scripts, docs, badges, submodules, release jobs, open requests, and monitoring. Roll out in observe/dual-compatible/migrate/enforce/remove phases, preserve a deterministic mapping for active work, and define rollback that does not silently rewrite consumer histories. See [S147](#s147), [S148](#s148), [S149](#s149), and [S153](#s153).

### 8.20. Agent preflight, authority, testing, metrics, and verification

An agent MUST discover the repository’s collaboration, release, authorization, and CI contract before interpreting “implement Git flow.” It must declare the exact mutation, authority, expected old/new state, evidence state, rollback, and validation scope. It must inspect existing work and in-progress operations, preserve unrelated changes, use a disposable test remote for risky behavior, and verify graph, worktree/index, remote refs, policy, tests, and artifacts. Metrics should expose review/CI wait, branch age, force pushes, bypasses, queue health, rejected updates, rollback time, and escaped defects without incentivizing unsafe shortcuts. See [S147](#s147), [S156](#s156), and [S158](#s158).

## 9. Normative requirements

### MUST

- **MUST** — Identify the immutable candidate OID and every mutable ref before changing, testing, approving, releasing, or deploying.
- **MUST** — Require explicit authority, target, expected old state, proposed new state, and post-write verification for every remote mutation.
- **MUST** — Bind approvals, required checks, artifacts, provenance, and deployments to the exact candidate or immutable merge-queue state.
- **MUST** — Enforce authorization, protected-ref, review, secret, and privileged-CI invariants server-side or in the authoritative hosted policy system.
- **MUST** — Reconcile ambiguous pushes and classify retry outcomes before repeating a mutation.
- **MUST** — Separate source rollback from application/data/external-state rollback and credential remediation.
- **MUST** — Test restore, concurrency, stale observations, untrusted CI, history rewriting, and release identity at the boundary where failure can occur.
- **MUST** — Treat branch/tag/history policy changes as compatibility migrations with owners and rollback.

### SHOULD

- **SHOULD** — Choose the least complicated workflow topology that represents supported release lines and deployment cadence.
- **SHOULD** — Prefer short-lived branches, small coherent reviews, feature controls, and selective backports over long-running divergence.
- **SHOULD** — Use annotated protected release tags and provenance that maps source OID to artifact digest and deployment.
- **SHOULD** — Use short-lived credentials, OIDC/workload identity, isolated runners, immutable workflow dependencies, and bounded caches.
- **SHOULD** — Record audit events for approvals, bypasses, permission changes, ref updates, tag movement, and deployments.
- **SHOULD** — Measure branch age, queue/CI wait, rejected updates, force pushes, bypasses, rollback time, and escaped defects.

### MAY

- **MAY** — Use Gitflow when multiple supported versions or explicit release stabilization require its additional branch topology.
- **MAY** — Use merge commits, squash, rebase, fast-forward, or cherry-pick when the choice is explicit, tested, and compatible with the repository contract.
- **MAY** — Use merge queues, sparse/partial clones, worktrees, rerere, LFS, submodules, or monorepo tooling when their trust, consistency, and operational costs are bounded.
- **MAY** — Use history filtering for sensitive-data remediation only with credential rotation, consumer coordination, retention analysis, and verification.

### AVOID

- **AVOID** — Treating branch names, abbreviated OIDs, local remote-tracking refs, signatures, approvals, or green unit tests as sufficient release identity.
- **AVOID** — Plain `--force`, blind retry after timeout, client-only policy enforcement, mutable privileged workflow dependencies, or shared caches crossing trust boundaries.
- **AVOID** — Creating environment branches solely because environments have names, or adding Gitflow branches without a release/support invariant.
- **AVOID** — Mixing history rewrites, dependency/schema migrations, product behavior, and large formatting churn when they can be staged.
- **AVOID** — Claiming a secret was erased because a later commit deleted or reverted it.

### NEVER

- **NEVER** — Force-push a protected/shared ref or move a published release tag merely to make automation convenient.
- **NEVER** — Treat untrusted pull-request/fork code as eligible for production credentials, deployment authority, or repository-rule mutation.
- **NEVER** — Resolve semantic conflicts by blindly choosing ours/theirs or delete sequencer state without deliberate recovery.
- **NEVER** — Claim a remote write, backup restore, security remediation, or release verification occurred when only a plan or user assertion exists.
- **NEVER** — Treat Git revert, branch deletion, or canonical-history rewrite as automatic application rollback or complete privacy erasure.

## 10. Testing and verification requirements

Passing a local happy-path test is insufficient. Test a bare remote plus two independent clones where possible and retain complete evidence bound to the tested OIDs and configuration.

- [ ] Verify root, linear, merge, first-parent, multiple-branch, deleted-ref, and nontrivial merge-base histories.
- [ ] Verify working tree/index/HEAD/detached-HEAD/dirty-state/stash/sequencer behavior and conflict continuation/abort.
- [ ] Verify stale expected-old-OID rejection, `--force-with-lease`, explicit CAS, local ref transactions, atomic and non-atomic multi-ref push behavior.
- [ ] Verify pre-send, rejection, timeout-after-success, retry, duplicate, and ambiguous-write classification with authoritative reconciliation.
- [ ] Verify protected refs, review/check invalidation, merge-queue candidate changes, bypass authorization, tag protection, and audit evidence.
- [ ] Verify untrusted fork/MR CI cannot read privileged secrets, poison caches/artifacts, mutate protected refs, or use floating workflow dependencies.
- [ ] Verify signatures, provenance, artifact digest mapping, release-tag immutability, SemVer rules, backports, and actual release-branch behavior.
- [ ] Verify restore from independent backup, fsck/integrity checks, reflog recovery, source-vs-application rollback, and secret-remediation limits.
- [ ] Verify case collisions, line endings, symlinks, worktrees, sparse/partial/shallow clones, LFS, submodules, monorepo scale, and unavailable nested repos.
- [ ] Verify default-branch/ruleset/merge-policy migrations in observe, compatibility, enforcement, and rollback phases.

## 11. Common production bugs and AI-agent failure modes

- A job tests a pull-request head but deploys a mutable branch tip or different merge candidate.
- A stale remote-tracking ref causes a force update over another developer’s work.
- A multi-ref command partially succeeds because server atomic support was assumed rather than verified.
- A timeout after a successful push causes a duplicate commit, repeated revert, or destructive blind retry.
- A signature or approval is treated as proof of authorization, current policy, or production provenance.
- A merge queue never receives its required check because the workflow ignores the queue event.
- A fork pipeline receives production secrets or writes a cache later trusted by a privileged job.
- A branch deletion/revert is treated as secret erasure, data rollback, or object deletion.
- A shallow/partial/sparse checkout makes missing history/files look like absence or success.
- An agent introduces classical Gitflow branches without discovering the existing deployment contract.
- An agent overwrites unrelated work, resets a dirty tree, or erases sequencer state to obtain a clean command result.

## 12. Operational metrics and evidence

Measure enough to separate correctness, security, and workflow friction: pull/merge-request lead time; review, CI, and merge-queue wait; required-check failure/flakiness; non-fast-forward rejection; force-push and protected-ref bypass count; branch-age distribution; release/backport/revert rate; restore and rollback time; artifact/provenance verification rate; secret-remediation time; runner/cache isolation findings; clone/fetch/push latency; repository/object-store size; pack/MIDX/commit-graph/fsck failures; LFS volume; and escaped defects. Do not turn speed metrics into incentives to bypass review or critical gates. Every release record should expose candidate OID, ref transition, policy result, artifact digest, deployment identity, and verification timestamp.

## 13. Knowledge graph relationships

This paper depends on or constrains the following papers. These are implementation relationships, not merely topical similarity.

- 001. Project & Runtime Foundations — in the `runtime-delivery` skill.
- 023. Database Transactions — in the `transactions-consistency` skill.
- 025. Concurrency Control — in the `transactions-consistency` skill.
- 036. Idempotency — in the `transactions-consistency` skill.
- 048. Distributed Transactions — in the `transactions-consistency` skill.
- 052. Retry Engineering — in the `resilience-flow-control` skill.
- 063. Secrets Management — in the `security-privacy` skill.
- 071. Backward Compatibility — in the `migration-evolution` skill.
- 076. Backup — in the `production-operations` skill.
- 077. Restore — in the `production-operations` skill.
- 089. Dependency Management — in the `system-architecture-harness` skill.
- 090. Testing Foundations — in the `quality-release` skill.
- 092. Concurrency Testing — in the `quality-release` skill.
- 093. Failure Testing — in the `quality-release` skill.
- 106. Deployment Safety — in the `runtime-delivery` skill.
- 107. CI/CD — in the `runtime-delivery` skill.
- 122. Data Provenance — in the `data-storage` skill.
- 123. Source of Truth — in the `data-storage` skill.
- 124. Data Reconciliation — in the `data-storage` skill.
- 137. Observability for Async Systems — in the `production-operations` skill.
- 139. Incident Readiness — in the `production-operations` skill.
- 146. Cross-Cutting Implementation Checklist — in the `quality-release` skill.

## 14. Sources and further research

Primary standards and official documentation are preferred. Provider behavior and living sources can change; verify the exact deployed versions at implementation time.

- <a id="s001"></a> **[S001] Key words for use in RFCs to Indicate Requirement Levels (RFC 2119).** IETF; 1997; RFC 2119 / BCP 14. [https://www.rfc-editor.org/rfc/rfc2119.html](https://www.rfc-editor.org/rfc/rfc2119.html) — Tags: requirements, standards.
- <a id="s002"></a> **[S002] Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words (RFC 8174).** IETF; 2017; RFC 8174 / BCP 14. [https://www.rfc-editor.org/rfc/rfc8174.html](https://www.rfc-editor.org/rfc/rfc8174.html) — Tags: requirements, standards.
- <a id="s141"></a> **[S141] Git User Manual.** Git community; 2026; current documentation. [https://git-scm.com/docs/user-manual](https://git-scm.com/docs/user-manual) — Tags: git, objects, refs, workflows.
- <a id="s142"></a> **[S142] git-push Documentation.** Git community; 2026; current documentation. [https://git-scm.com/docs/git-push](https://git-scm.com/docs/git-push) — Tags: git, push, refs, concurrency, atomicity.
- <a id="s143"></a> **[S143] Git Repository Layout.** Git community; 2026; current documentation. [https://git-scm.com/docs/gitrepository-layout](https://git-scm.com/docs/gitrepository-layout) — Tags: git, repository, refs, worktrees.
- <a id="s144"></a> **[S144] git-update-ref Documentation.** Git community; 2026; current documentation. [https://git-scm.com/docs/git-update-ref](https://git-scm.com/docs/git-update-ref) — Tags: git, ref-transactions, atomicity.
- <a id="s145"></a> **[S145] A successful Git branching model.** Vincent Driessen; 2010/2020 reflection; article. [https://nvie.com/posts/a-successful-git-branching-model/](https://nvie.com/posts/a-successful-git-branching-model/) — Tags: gitflow, branching, release-topology.
- <a id="s146"></a> **[S146] Trunk Based Development.** Trunk Based Development community; 2026; current guidance. [https://trunkbaseddevelopment.com/](https://trunkbaseddevelopment.com/) — Tags: trunk, branching, continuous-delivery.
- <a id="s147"></a> **[S147] About rulesets.** GitHub; 2026; current documentation. [https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) — Tags: github, rulesets, protected-refs, bypass.
- <a id="s148"></a> **[S148] About protected branches.** GitHub; 2026; current documentation. [https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) — Tags: github, branches, reviews, required-checks.
- <a id="s149"></a> **[S149] Managing a merge queue.** GitHub; 2026; current documentation. [https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue) — Tags: github, merge-queue, ci, concurrency.
- <a id="s150"></a> **[S150] About commit signature verification.** GitHub; 2026; current documentation. [https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification) — Tags: github, signatures, provenance.
- <a id="s151"></a> **[S151] Removing sensitive data from a repository.** GitHub; 2026; current documentation. [https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) — Tags: github, secrets, history-rewrite, remediation.
- <a id="s152"></a> **[S152] Security hardening your deployments with OpenID Connect.** GitHub; 2026; current documentation. [https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect) — Tags: github-actions, oidc, workload-identity.
- <a id="s153"></a> **[S153] Merge requests.** GitLab; 2026; current documentation. [https://docs.gitlab.com/user/project/merge_requests/](https://docs.gitlab.com/user/project/merge_requests/) — Tags: gitlab, merge-requests, reviews, checks.
- <a id="s154"></a> **[S154] Control access to protected variables and runners.** GitLab; 2026; current documentation. [https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/#control-access-to-protected-variables-and-runners](https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/#control-access-to-protected-variables-and-runners) — Tags: gitlab, ci, protected-resources, secrets.
- <a id="s155"></a> **[S155] Semantic Versioning 2.0.0.** Semantic Versioning; 2013; SemVer 2.0.0. [https://semver.org/](https://semver.org/) — Tags: versioning, compatibility, releases.
- <a id="s156"></a> **[S156] SLSA v1.2 Source Track.** OpenSSF/SLSA; 2026; v1.2. [https://slsa.dev/spec/v1.2/tracks](https://slsa.dev/spec/v1.2/tracks) — Tags: provenance, source, supply-chain.
- <a id="s157"></a> **[S157] OpenSSF Project Security Baseline.** OpenSSF; 2026; current baseline. [https://baseline.openssf.org/](https://baseline.openssf.org/) — Tags: project-security, releases, signing, ci.
- <a id="s158"></a> **[S158] Code Review Developer Guide.** Google; 2026; current engineering guidance. [https://google.github.io/eng-practices/review/](https://google.github.io/eng-practices/review/) — Tags: code-review, correctness, collaboration.
- <a id="s159"></a> **[S159] Security hardening for GitHub Actions.** GitHub; 2026; current documentation. [https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) — Tags: github-actions, runners, secrets, dependencies.
- <a id="s160"></a> **[S160] Git Large File Storage.** Git LFS community; 2026; current documentation. [https://git-lfs.com/](https://git-lfs.com/) — Tags: git-lfs, large-files, storage.
- <a id="s161"></a> **[S161] Git Tools: Submodules.** Git community; 2026; current documentation. [https://git-scm.com/book/en/v2/Git-Tools-Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules) — Tags: git, submodules, dependencies.
- <a id="s162"></a> **[S162] git-maintenance Documentation.** Git community; 2026; current documentation. [https://git-scm.com/docs/git-maintenance](https://git-scm.com/docs/git-maintenance) — Tags: git, maintenance, scale, performance.

---

**Paper metadata:** canonical subtopics: 20; layer: `cross-cutting`; domain profile: `version_control`; verified through: `2026-08-20`.

## 15. Supplied research notes

The following supplied research text is appended after this normalized contract for traceability. It retains additional examples, diagrams, edge cases, and rationale from the user attachment.

Scope and production mental model
This paper treats Git itself, repository workflows, Gitflow, trunk-based development, pull-request workflows, release management, CI/CD integration, repository security, recovery, scaling, and hosted-platform policy as related but distinct concerns. That distinction is foundational: Git is a distributed version-control system; GitHub and GitLab add collaboration, authorization, pull/merge-request, policy, audit, and CI/CD layers; and Gitflow is only one branching model, not “how Git works.” Gitflow’s original author explicitly revisited the model in 2020 and recommended simpler approaches such as GitHub Flow for continuously delivered web applications, while retaining Gitflow as potentially useful for explicitly versioned software supporting multiple versions in the field.

This research is aligned with the current Git documentation available in August 2026; Git’s official site lists Git 2.55.0, released June 29, 2026, as the latest source release at the time of research. Git also maintains explicit documentation for anticipated compatibility-breaking changes, so an engineering agent changing repository infrastructure must not assume every historical Git behavior is permanent.

The normative words in this paper have these meanings:

Level	Engineering meaning
MUST	Required to preserve correctness, security, recoverability, or an explicitly stated invariant.
SHOULD	Strong production default; deviation requires an understood reason.
MAY	Context-dependent option with legitimate trade-offs.
AVOID	Usually creates unnecessary risk, coupling, operational burden, or confusing history.
NEVER	Fundamentally unsafe or incorrect for the stated situation.

The most important production insight is that Git is not fundamentally a sequence of patches. Its object database is content-addressed; commits reference trees representing snapshots and refer to parent commits, producing a directed acyclic ancestry graph. A merge commit normally has multiple parents. Branches are movable references into that graph, not independent copies of the source tree.

A simplified repository model is:

text
Copy
                    object database
                        |
                        v
     blob <- tree <- commit C <- commit D <- commit E
                         \                    ^
                          \-> commit X -------|
                                   merge ancestry

refs/heads/main -----------------------------> E
refs/heads/feature --------------------------> X
HEAD -> refs/heads/main
This creates the first set of production invariants:

MUST — distinguish immutable objects from mutable names. A commit object does not “change.” A branch changes by making its ref point to another commit. Tags are refs too and technically can be moved unless policy prevents it. A system that stores “main” as though it were an immutable software version is therefore incorrectly modeled.

MUST — distinguish Git state from hosting-platform state. A clone contains Git objects, refs, configuration, and local metadata. It does not inherently contain GitHub required checks, GitLab approval policies, CODEOWNERS approval state, merge queues, hosted audit logs, or deployment-environment authorization. Those are policy-system states layered around Git. GitHub rulesets, protected branches, and merge queues explicitly operate as controls around ref updates.

MUST — distinguish author identity, cryptographic identity, and authorization. Commit author/committer fields are metadata, not proof that a particular authenticated user was authorized to modify a protected branch. Signing adds cryptographic evidence about the commit or tag; server authorization and review policy independently determine whether that object may become reachable through a protected ref. GitHub, for example, separately supports signature verification and protected-branch/ruleset controls.

SHOULD — treat the protected canonical repository as the policy authority even though Git itself is distributed. Every clone can create commits and refs independently, but production acceptance should occur through controlled server-side ref transitions. This is exactly the kind of protected-source control assumed by modern software-supply-chain models such as SLSA’s Source Track.

The four states an agent must keep separate
Most everyday Git mistakes come from confusing the working tree, index, HEAD/current commit, and remote state.

text
Copy
Working tree
    |
    | git add
    v
Index / staging area
    |
    | git commit
    v
Commit object + local branch ref
    |
    | git push
    v
Remote repository ref

Remote repository
    |
    | git fetch
    v
Local remote-tracking refs
The index is an explicit staging state between the working tree and the next commit. git diff without --cached normally compares working-tree content against the index, while staged differences can be compared against HEAD. git restore, git reset, and git revert affect different layers and are therefore not interchangeable “undo” commands.

MUST — identify which state is being changed before executing an “undo.”

restore primarily restores working-tree/index content; reset moves refs and/or resets index/worktree state depending on mode; revert creates a new commit whose change reverses an earlier commit. On shared history, that difference is crucial.

SHOULD — prefer revert over history movement to undo already-published production changes. A revert preserves the fact that both the original change and its reversal occurred. Resetting a shared branch instead rewrites the ref’s visible history and can strand collaborators on the previous lineage.

NEVER — equate “not visible on the current branch” with “deleted.” An object may remain reachable through another branch, tag, remote-tracking ref, pull-request ref, reflog, alternate object database, clone, cache, or server backup. Even unreachable objects may remain until maintenance eventually prunes them.

The experienced-engineer mental model is therefore:

Git stores immutable graph objects; refs provide mutable names; clones provide divergent local views; hosting platforms arbitrate which ref transitions are allowed; CI decides whether candidate states are acceptable; release systems turn accepted commits into immutable deployable artifacts.

Any implementation that collapses those layers will eventually fail under concurrency, rollback, security review, or history migration.

Repository state, object graph, and correctness invariants
A production system interacting with Git must understand enough of Git’s data model to avoid treating the CLI as a magical file synchronization utility.

Git’s object store includes blobs for file contents, trees for directory/snapshot structure, commits that identify a tree and parent relationship plus metadata, and annotated tag objects. Object IDs are content-derived. Reachability is computed by graph traversal from refs or other roots. git log, git rev-list, garbage collection, negotiation during fetch, and many policy decisions depend on ancestry rather than filesystem chronology.

MUST — model commit identity as the complete object ID, not as a fixed seven-character “SHA.” Abbreviated IDs are human-readable conveniences whose required uniqueness depends on the repository’s object population. Git also supports repository object formats beyond the traditional SHA-1 representation, and modern Git exposes the repository’s object format explicitly. A database schema hard-coded to a 40-character SHA-1 column bakes repository-format assumptions into application architecture.

A robust external model is conceptually:

text
Copy
CommitIdentity {
    repository_id
    hash_algorithm
    full_object_id
}
rather than:

text
Copy
commit_sha CHAR(7)
or even blindly:

text
Copy
commit_sha CHAR(40)
SHOULD — store ref identity separately from commit identity.

text
Copy
RefState {
    repository_id
    ref_name       # refs/heads/main
    target_oid
    observed_at
}
The pair is important because refs/heads/main may point to different objects at different moments, while the commit itself remains the same object. This becomes essential for caches, API idempotency, deployment records, audit events, and optimistic concurrency.

HEAD and detached state
HEAD normally symbolically references the currently checked-out branch, but it can point directly to a commit in detached-HEAD mode. CI systems and temporary worktrees commonly operate without needing a developer-style current branch, so automation that assumes git branch --show-current always returns a meaningful deployment branch is structurally fragile.

MUST — identify the commit with an OID when correctness depends on exactly what was built or tested.

AVOID — deriving deployment identity solely from “current branch.” A CI checkout may be detached, may represent a temporary merge commit, or may represent merge-queue state rather than the PR head. GitHub merge queues explicitly create temporary grouped states and trigger a merge_group event.

Reachability and revision expressions
Git history is graph-based rather than strictly linear. A commit can be reachable from multiple branches or tags, and one commit can have multiple parents. git merge-base computes best common ancestors for three-way merge operations, and there can be more than one merge base.

MUST — use ancestry tests when asking ancestry questions. Timestamp comparisons are not a substitute for graph reachability. Author dates and committer dates do not establish whether one commit contains another.

SHOULD — define precisely what “changes in this branch” means. Possible interpretations include:

text
Copy
A..B        commits reachable from B but not A
A...B       symmetric relationship based around merge history
merge-base  comparison against the common ancestor
tip-to-tip  raw snapshot difference
Those answer different questions. Production review tooling, changelog generation, code-owner analysis, and deployment diffing can become incorrect when they use tip-to-tip diff where a merge-base comparison was intended. Git’s revision and merge-base documentation explicitly distinguish reachability and common-ancestor semantics.

Branch creation, update, and deletion
A branch is cheap because creating one primarily creates another ref pointing into existing history. Adding commits creates objects and advances the ref. Deleting a branch deletes the name; it does not necessarily delete the commits.

The useful lifecycle is:

text
Copy
nonexistent
    |
    | create ref
    v
active branch -> advancing -> merged/abandoned
                               |
                               | delete ref
                               v
                        ref no longer exists

Commit objects survive while reachable
through other roots, and may survive
temporarily even after becoming unreachable.
SHOULD — delete short-lived integration branches after merge. Keeping thousands of dead branch names provides little historical benefit when commits are already reachable from the canonical branch and review metadata exists separately. Trunk-based guidance similarly recommends deleting short-lived review branches while retaining review/audit records.

NEVER — implement data-retention or privacy guarantees by merely deleting a branch. That operation does not imply object eradication.

Remote-tracking refs are caches of remote state
After clone or fetch, names such as refs/remotes/origin/main describe locally observed remote state. They are not a live pointer into another server. Clone config normally establishes origin and its fetch mapping, after which fetching refreshes remote-tracking refs.

This is one of Git’s most important distributed-system properties:

origin/main means roughly “what this repository last observed about that remote ref,” not “the remote main branch at this instant.”

MUST — refresh remote state before making a concurrency-sensitive decision.

MUST — still expect a race after fetching. The remote may change again between fetch and push. Fetch-then-push is therefore not a transaction.

That second fact is why ref updates need optimistic concurrency rather than “I fetched recently” reasoning.

Working-tree filesystem behavior
Git repositories cross operating-system and filesystem boundaries that differ in case handling, newline conventions, and symbolic-link support.

.gitattributes can normalize line-ending behavior. core.ignoreCase exists because Git must compensate for case-insensitive filesystems. core.symlinks=false causes symbolic links to be checked out as small ordinary files containing link text rather than native symlinks.

MUST — test repository changes on the filesystem classes used by production developers and CI when filenames, generated artifacts, symlinks, or line endings matter.

Typical cross-platform failures include:

text
Copy
Linux:
  UserService.go
  userservice.go
  -> two distinct paths

case-insensitive developer filesystem:
  those names may collide
and:

text
Copy
repository normalized to LF
developer editor emits CRLF
generator rewrites whole file
-> enormous misleading diff
SHOULD — encode text normalization in .gitattributes, not in undocumented per-developer configuration.

AVOID — using assume-unchanged as a method for “ignoring” tracked local configuration. It is a local optimization promise and is not the semantic equivalent of .gitignore. .gitignore itself only affects untracked files; it does not make already-tracked files disappear from version control.

For developer-specific configuration, the safer design usually separates a tracked template from an ignored local override.

Renames are a diff interpretation
Git’s diff machinery performs rename detection using configurable similarity behavior. This means downstream systems should not model “rename” as though every repository operation stored a permanent first-class rename record in each commit.

SHOULD — let history-analysis tools perform rename-aware comparison when that meaning matters.

AVOID — depending on exact rename classification as a permanent database invariant. A large rewrite and rename may be classified differently depending on diff options and similarity thresholds.

Worktrees
Git supports multiple linked working trees attached to the same repository so multiple branches can be checked out simultaneously. A branch already checked out in another linked worktree cannot always be treated like an ordinary inactive branch.

MUST — inspect worktrees before automation performs branch deletion, forced checkout, or destructive maintenance in developer repositories.

For AI coding agents, worktrees are often safer than repeatedly stashing and switching when multiple independent tasks must coexist.

Index versus “indexing”
The Git index means the staging area; it is not the same concept as a database index. Git additionally maintains performance indexes such as the commit-graph and multi-pack-index. The commit-graph serializes commit relationships and metadata to accelerate graph walks; a multi-pack-index provides efficient lookup across multiple packfiles.

An AI agent must never confuse these three meanings:

text
Copy
Git index             = proposed next tree / staging state
commit-graph          = history traversal acceleration
multi-pack-index      = object lookup acceleration across packs
Transport and protocol state
Git protocol v2 is capability-oriented and stateless by default, which helps Git servers scale across backend infrastructure. Git supports multiple transport forms, but authentication and authorization are generally provided through the transport and hosting layer rather than encoded in commit objects.

SHOULD — use authenticated SSH or HTTPS for write access.

NEVER — treat transport success as authorization proof for later operations. Credentials can expire, permissions can change, branch rules can reject the final ref update, and an authenticated user may still lack permission for a protected ref. Git’s receive hooks and hosting rules can reject pushes even after transport and object transfer begin.

Collaboration workflows, branching, and history policy
Branching strategy is an architecture decision derived from deployment and release requirements, not a cosmetic preference.

The first question is not “Gitflow or trunk?” It is:

How many simultaneously supported lines of software exist, how frequently do changes integrate, where are releases created, and how rapidly must a fix propagate among those lines?

Major workflow families
Model	Core shape	Best fit	Hidden cost
Trunk-based development	Developers integrate into one trunk directly or through very short-lived change branches.	Frequent integration and continuous delivery.	Requires excellent CI, small changes, and mechanisms for incomplete features.
GitHub-style flow	Short-lived branch → pull request → checks/review → merge to default branch.	Most web/backend products with one primary production line.	PR latency can silently turn short branches into long-lived branches.
Gitflow	Long-lived production and development lines plus feature, release, and hotfix branches.	Explicitly versioned products and multiple supported versions.	More merge paths, branch synchronization, hotfix propagation, and release coordination.
Release branches from trunk	Main development stays on trunk; temporary or supported release branches are cut when necessary.	Continuous integration plus selective older-version maintenance.	Fixes must have an explicit forward/backport policy.

The Gitflow author’s own reflection is unusually important here: the model was designed for versioned software rather than modern continuously delivered web applications, and he recommends simpler workflows where continuous delivery is the actual lifecycle.

Trunk-based guidance allows short-lived feature/change branches but argues they should normally last only a couple of days, specifically to avoid large divergence from trunk.

SHOULD — choose the least complicated branching model that represents actual release topology.

AVOID — creating develop, release, staging, qa, uat, and production branches merely because deployment environments have those names. Environment state and source lineage are different concerns. Long-lived environment branches frequently create unclear merge direction, accidental omissions, and multiple competing truths.

A healthier deployment model is commonly:

text
Copy
main commit A
   |
   +--> artifact A
           |
           +--> dev
           +--> staging
           +--> production
rather than rebuilding successively unrelated branch states:

text
Copy
dev -> qa -> staging -> prod branches
The former promotes an immutable artifact; the latter can accidentally test one source state and deploy another.

Gitflow when it is actually appropriate
Classical Gitflow distinguishes a production branch, a development integration branch, feature branches, release branches, and hotfix branches. The model provides explicit places for stabilizing upcoming releases and servicing production independently.

That has real value when:

text
Copy
customers on v3.x need critical fixes
customers on v4.x need different fixes
v5 is under active development
release certification takes weeks
It is excessive when:

text
Copy
one SaaS backend
one supported production state
multiple deployments every day
feature rollout controlled independently
MUST — define hotfix propagation. In any multi-line model, a fix made on an old release branch must have an explicit policy for whether and how it reaches later maintained lines. Otherwise the next release can silently reintroduce the defect.

SHOULD — implement fixes on the most authoritative applicable line and systematically backport/forward-port where practical. The exact direction depends on support policy. Trunk-based release-branch guidance, for example, normally develops fixes on trunk and cherry-picks applicable fixes into release branches.

AVOID — repeatedly developing the same logical fix independently on multiple branches. Those implementations inevitably diverge.

Long-running work is not an excuse for long-running integration
A six-month product capability does not require a six-month branch.

Teams can split work into backward-compatible increments, introduce abstractions before switching behavior, or use feature controls to decouple source integration from user-visible activation. Trunk-based development explicitly treats short-lived review branches and feature flags/branch-by-abstraction as supporting techniques.

SHOULD — integrate incomplete but safe structural work incrementally rather than carrying huge divergent branches.

This reduces:

merge conflict surface,
integration surprises,
review size,
stale architectural assumptions,
hidden dependency conflicts.
Google’s engineering guidance similarly recommends small changes because they are easier to review, test, merge, and roll back, and describes stacking dependent small changes rather than bundling everything into one enormous review.

Merge, squash, rebase, and fast-forward are architectural choices
GitHub, for example, explicitly supports merge commits, squash merging, and rebase merging as different repository-level strategies.

Integration method	What main receives	Strength	Cost
Merge commit	Existing commits plus an explicit integration commit	Preserves branch topology and development history	Main history can become noisy when branches contain low-quality intermediary commits
Squash merge	One new commit containing the branch’s net change	Clean atomic PR-level history; easy PR-level revert	Original individual commits no longer form main’s ancestry
Rebase then fast-forward / rebase merge	Rewritten linear commits	Linear detailed history	Changes commit IDs; repeated rebases amplify conflict work
Fast-forward	Existing branch commits directly advance target	Minimal artificial history	No explicit node representing the integration event

There is no universally correct choice.

SHOULD — optimize history for its intended operational use.

For a product team where “one PR = one coherent deployable change,” squash merging is often attractive. For projects where preserving contributor commits or detailed bisectable steps matters, merge/rebase approaches can be better.

MUST — make individual commits buildable/testable if the organization depends on commit-level bisectability. Squashing can compensate for messy feature-branch commits on the canonical branch; preserving every commit cannot.

Rebase
Rebase replays commits onto another base, constructing new commits. Because commit parentage participates in commit identity, rebased commits are different objects. Rebase normally linearizes commits; --rebase-merges can attempt to recreate branch topology, but manual resolutions from earlier merges may need to be repeated.

MAY — rebase private/unpublished work freely when doing so improves reviewability.

AVOID — rebasing a shared branch that others have based work on unless the entire collaboration explicitly expects history rewriting. Git’s own guidance distinguishes rewriting private history from rewriting commits others already use.

A non-obvious conflict trap is that during rebase, “ours” and “theirs” can feel reversed: Git is replaying your commit onto the rebased target, so labels refer to the sequencer’s current sides rather than the developer’s intuitive idea of “my branch versus their branch.”

MUST — inspect the resulting diff and tests after conflict resolution; never resolve conflicts based solely on ours/theirs terminology.

Cherry-pick
Cherry-pick applies the change represented by an existing commit and records it as a commit on another history. It is therefore useful for targeted backports, release branches, and selective hotfix propagation. Git has explicit handling for commits that become redundant or empty under the destination history, showing that cherry-pick semantics are more nuanced than “copy commit.”

MAY — use cherry-pick for backports where merging the entire source branch is wrong.

AVOID — using cherry-pick as the normal synchronization method among many permanently diverging branches. The same conceptual change becomes represented through different ancestry, making later merging and provenance reasoning harder.

Merge conflicts
A conflict is not itself an error. It means Git could not automatically determine a unique safe combined result.

A correct conflict workflow is:

text
Copy
discover conflict
       |
       v
understand base + both sides
       |
       v
construct intended resulting program
       |
       v
stage resolved files
       |
       v
run relevant tests/static checks
       |
       v
continue merge/rebase/cherry-pick
NEVER — resolve conflicts mechanically by choosing all “ours” or all “theirs” without understanding semantics.

MUST — test behavior created by the resolution. Both branches can individually pass tests while their semantically combined result is wrong.

git rerere can record previous conflict resolutions and reuse them when substantially the same conflict occurs again, which can be useful in repeated rebases or backports.

MAY — enable rerere for workflows with repetitive integration conflicts.

SHOULD — still review reused resolutions when important code has changed.

Dirty working trees
Merge/rebase operations can interact badly with uncommitted modifications. Git warns that aborting a merge may not always reconstruct the exact original uncommitted state if the operation began with complex local changes. Autostash can reduce friction but reapplying the stash itself can generate conflicts.

SHOULD — start complex history operations from a known, recoverable state.

That usually means committing work to a temporary branch or explicitly stashing it, then verifying the stash exists.

NEVER — assume git stash pop is transactionally guaranteed to restore everything without intervention. A pop can conflict, and Git retains the stash when application fails.

Pull requests and merge requests are state machines
A production PR should be understood approximately as:

text
Copy
Draft
  |
  v
Reviewable
  |
  +----> changes pushed ------+
  |                           |
  v                           |
Checks running                |
  |                           |
  v                           |
Reviews / owners              |
  |                           |
  v                           |
Candidate acceptable <--------+
  |
  v
Merge queue / latest-base validation
  |
  v
Merged
A new push can invalidate old assumptions about review and CI. Required checks that passed on an old head are not evidence that the new head is safe.

MUST — bind approvals and CI decisions to a concrete candidate commit or merge candidate.

SHOULD — invalidate relevant approval/check state when material changes are pushed.

GitHub’s branch controls can require passing checks, reviews, signed commits, linear history, and current-base validation; CODEOWNERS can add ownership-based review policy.

The stale-base race
Consider:

text
Copy
main = A

PR1: A -> B       tests pass
PR2: A -> C       tests pass

merge PR1:
main = B

merge PR2 without retesting B+C:
main = B+C        possibly broken
Both PRs were “green,” but neither tested their combined result.

MUST — address this race on high-throughput protected branches.

Possible strategies:

require branches to be up to date and retest,
test an automatically generated merge result,
use a merge queue.
GitHub’s merge queue explicitly creates candidate states containing the current target branch plus preceding queued changes, then waits for required checks against those combined states.

SHOULD — use a merge queue when main changes frequently enough that constantly rebasing every PR creates substantial CI churn.

A platform-specific trap: GitHub Actions workflows used as merge-queue checks must handle the merge_group trigger. A workflow listening only for normal pull-request/push events can leave the queue waiting for a required status that never appears.

Review is not just approval count
Good review examines system design, functionality, complexity, test adequacy, edge cases, concurrency, privacy/security concerns, and integration with the existing system. Google’s published review guidance explicitly calls out concurrency and the need for qualified reviewers on specialized concerns such as security and privacy.

SHOULD — optimize for small, coherent reviews rather than arbitrary line-count rules.

AVOID — treating “two approvals” as proof of correctness. Review policy only helps when the selected reviewers understand the affected domain and the change is small enough to comprehend.

Concurrency, atomicity, retries, consistency, and recovery
Git is a distributed system. Production Git automation must therefore reason about stale observations, concurrent ref updates, partial network failures, and ambiguity about whether an operation succeeded.

Ref updates are compare-and-swap problems
Suppose two developers fetch:

text
Copy
origin/main = A

Developer 1 creates:
A -> B

Developer 2 creates:
A -> C
Developer 1 pushes first:

text
Copy
remote main: A -> B
Developer 2’s ordinary push of C would discard the advancement to B, so Git rejects a non-fast-forward update by default.

That rejection is a concurrency-control mechanism.

MUST — treat a non-fast-forward rejection as “the precondition changed,” not as an inconvenience to bypass.

Correct response:

text
Copy
refresh
understand B
integrate/rebase C with B
test B+C
attempt update again
Incorrect response:

text
Copy
git push --force
Force-with-lease
When history rewriting is intentionally allowed, --force-with-lease is safer than unconditional force because it can require that the remote ref still have an expected value. This is analogous to optimistic locking / compare-and-swap.

Conceptually:

text
Copy
UPDATE ref
SET target = NEW
WHERE target = EXPECTED_OLD
SHOULD — use an explicit expected OID when automation must intentionally replace a ref.

AVOID — plain --force on shared refs.

A particularly non-obvious Git edge case is that the convenient implicit lease often derives its expectation from a local remote-tracking ref. Background git fetch activity can refresh that ref, weakening the protection a developer thought they had. Git’s own push documentation calls out this interaction.

For highly sensitive automation, explicit expected state is preferable:

text
Copy
expected old OID known from workflow state
                 |
                 v
conditional ref update
rather than:

text
Copy
whatever origin/main currently says locally
Local ref transactions
Git’s update-ref supports ref transactions. Updates can be prepared, locks acquired, and the transaction aborted if necessary rather than silently modifying only whichever refs happened to succeed first.

MUST — use transactional ref primitives when multiple local refs form one logical invariant.

For example:

text
Copy
release branch -> commit X
release tag    -> commit X
If policy says both must transition together, independently writing them introduces an intermediate invalid state.

Git also exposes a reference-transaction hook around transaction phases, enabling repository infrastructure to observe preparation, commit, or abort states.

Multi-ref remote pushes
Git’s protocol supports atomic push when the receiving server advertises the capability: either all requested ref updates occur or none do. Without atomic support, automation must not assume a multi-ref push behaves like a distributed database transaction.

MUST — request atomic push where correctness requires all-or-nothing remote ref updates and verify server support.

NEVER — infer atomicity from the fact that all refspecs were passed in one CLI command.

Idempotency
Git’s content-addressed storage has naturally idempotent properties at the object level: writing identical object contents produces the same content identity. But higher-level Git operations are not automatically idempotent. Commit objects include parent and metadata relationships; retrying “create a commit” can create another object. Repeating revert, merge, cherry-pick, or branch movement can therefore have different semantics from retrying an object upload.

Production automation should define mutations in terms of desired ref state:

text
Copy
desired:
refs/heads/main = X

current:
refs/heads/main = ?

if current == X:
    operation already complete

elif current == expected_old:
    attempt CAS(expected_old -> X)

else:
    concurrent modification; stop and reconcile
MUST — make ref-mutating automation idempotent around explicit old/new OIDs.

SHOULD — record operation identifiers separately from commit IDs when the surrounding application accepts retries.

The ambiguous push problem
A classic distributed failure is:

text
Copy
client sends push
server updates ref successfully
network drops before client receives response
client sees timeout
A blind retry cannot distinguish “never reached server” from “already succeeded.”

This is an engineering inference from Git’s network/ref-update model: after an ambiguous failure, the correct recovery is to observe the authoritative ref, compare it with the intended OID, and only retry when necessary. Git push and ref transactions expose the old/new-state model needed to do this safely.

MUST — reconcile after ambiguous write failures.

AVOID — retrying forced ref mutations blindly after a timeout.

Retry classification
Failure	Default action
DNS/connection failure before meaningful exchange	MAY retry with bounded backoff.
Fetch interruption	MAY retry; verify repository state afterward.
Push timeout with unknown server result	MUST read remote ref before retrying.
Non-fast-forward	MUST NOT blindly retry; refresh and integrate.
Lease mismatch	MUST NOT override automatically; expected state is stale.
Branch-policy rejection	MUST fix policy failure, not retry endlessly.
Merge conflict	MUST perform semantic resolution.
Authentication failure	SHOULD refresh credentials if expected; otherwise stop.
Rate-limit response from hosting API	SHOULD honor server retry/backoff semantics rather than spinning.

Consistency model
Git clones are intentionally capable of diverging.

text
Copy
clone A                    canonical remote                   clone B
main=A                     main=A                            main=A

local B1                                                    local C1

push B1
                           main=B1

                                                               still sees A
There is no global automatically synchronized local state.

MUST — treat remote-tracking refs as cached observations.

MUST — never build correctness around the assumption that all clones immediately agree.

SHOULD — make the canonical protected ref or immutable release object the externally visible source of truth.

Merge/rebase state machines
Merge, rebase, and cherry-pick are multi-step sequencer operations. Conflict resolution must either continue or explicitly abort. Git exposes --continue/--abort style lifecycle behavior for these operations.

An AI agent should check for operation-in-progress state before starting another history operation.

MUST — detect existing merge/rebase/cherry-pick state before modifying history.

NEVER — delete .git sequencer/state files to “fix” an operation unless performing deliberate repository-level recovery with full understanding of their role.

Recovery hierarchy
A disciplined recovery order is:

text
Copy
Understand current state
        |
        v
Use operation-specific abort/continue
        |
        v
Inspect reflog / previous ref values
        |
        v
Restore or branch from known object
        |
        v
Verify graph + worktree
        |
        v
Only then consider deeper object recovery
Reflogs record updates to local ref tips and often make accidental resets or branch movement recoverable. But they are local operational metadata, not permanent backup; garbage collection can eventually expire reflog data and prune unreachable objects.

SHOULD — teach “reflog before panic.”

NEVER — advertise reflog as a backup or regulatory retention system.

Corruption
git fsck checks object connectivity and validity, while maintenance commands manage packing and supporting structures. Git cannot repair genuinely lost object bytes merely because their hash is known.

MUST — maintain independent repository backups or replicated canonical storage when loss is unacceptable.

SHOULD — periodically test restoration, not just backup creation.

SHOULD — include repository integrity verification when moving archival mirrors, rewriting history, or recovering from storage incidents.

Git rollback versus application rollback
A Git revert changes source history. It does not automatically:

reverse a database migration,
restore deleted production data,
downgrade an external API,
revoke an emitted message,
un-send an email,
remove an already published package,
restore infrastructure state.
MUST — keep source rollback and production-state rollback conceptually separate.

This is one of the most consequential errors an AI coding agent can make: “revert the commit” is not synonymous with “undo the incident.”

Security, authorization, CI/CD, and software supply chain
Production Git security has at least six distinct trust layers:

text
Copy
human / workload identity
        |
        v
transport authentication
        |
        v
repository authorization
        |
        v
branch/tag policy
        |
        v
review + CI decision
        |
        v
artifact provenance / deployment authorization
Compromising any one layer must not automatically imply unrestricted control of all later layers.

Repository trust
A repository itself can be untrusted input. Local Git configuration, hooks, submodule URLs, filters, paths, or external tooling around checkout can influence behavior.

Git has explicit safe.directory handling for repositories owned by other users and protected configuration scopes. Current documentation also describes safe.bareRepository; the Git 2.x default is broad, while explicit is documented as the intended Git 3.0 default to reduce exposure to unintended bare repositories.

MUST — treat repositories from untrusted sources as potentially hostile.

Git’s own security documentation advises that when dealing with an untrusted .git directory, cloning rather than directly using that repository structure gives a cleaner boundary, while noting that server-side upload processing remains attack surface that should be isolated appropriately.

NEVER — run arbitrary repository hooks or repository-provided executable tooling with high-privilege credentials merely because the repository cloned successfully.

Authentication and credentials
Git credential helpers can retrieve and store credentials. The store helper specifically stores credentials unencrypted on disk, relying primarily on filesystem permissions.

AVOID — plaintext credential storage for production credentials.

SHOULD — use operating-system-backed credential managers, short-lived credentials, or managed workload identity where available.

For GitHub automation, repository-scoped workflow tokens and OIDC-based cloud authentication can reduce dependence on long-lived stored secrets; GitHub explicitly documents OIDC for deployments and recommends minimizing workflow token permissions.

MUST — apply least privilege separately to repository write, package publishing, deployment, and infrastructure credentials.

A CI job needing read access to source does not automatically need permission to:

text
Copy
push main
delete tags
publish packages
deploy production
modify repository rules
Authorization and protected refs
Protected branch and ruleset systems can require checks, reviews, signed commits, restrict force pushes, restrict deletion, and limit who can update matching refs.

MUST — enforce critical invariants server-side.

Client-side conventions are useful ergonomics but not security boundaries.

Git supports server-side pre-receive and per-ref update hooks that can reject proposed updates before refs change.

Conversely, some client workflow hooks can be skipped by user options such as --no-verify.

Therefore:

NEVER — rely solely on developer-side hooks to enforce security, authorization, compliance, or canonical-history invariants.

Client hooks are appropriate for rapid feedback:

text
Copy
formatting
simple lint
commit-message assistance
Server/host policy must own:

text
Copy
protected-ref rules
required approval
mandatory CI
security gates
release-tag control
force-push prevention
Review bypasses
Emergency bypasses may be operationally necessary, but they create a high-risk path around normal controls.

SHOULD — make bypass narrow, explicit, auditable, and exceptional.

GitHub rulesets support defined bypass actors and can preserve a pull-request-based path rather than uncontrolled direct modification.

MUST — audit use of bypass privileges separately from ordinary merge activity.

SHOULD — alert on protected-ref force pushes, rule changes, release-tag movement, and unexpected privilege escalation.

CI executes potentially hostile code
A pull request may modify:

text
Copy
build scripts
test scripts
package-manager hooks
CI workflow code
container build instructions
Makefiles
code generators
Therefore CI is not merely “testing contributor code”; it is often executing contributor-controlled code.

MUST — treat pre-merge code as untrusted with respect to secrets and privileged credentials.

GitLab explicitly restricts access to protected variables/runners in merge-request pipelines based on protected-branch status, repository relationship, and triggering-user permissions.

NEVER — expose production credentials to arbitrary fork/untrusted PR execution.

SHOULD — separate unprivileged validation from privileged release/deployment stages.

A secure conceptual pipeline is:

text
Copy
untrusted candidate
      |
      v
build + test with no production secrets
      |
      v
review + protected merge
      |
      v
canonical protected commit
      |
      v
trusted release workflow
      |
      v
short-lived deployment identity
Third-party CI dependencies
Workflow dependencies themselves are supply-chain dependencies. GitHub’s security guidance says pinning a third-party Action to a full-length commit SHA is the immutable way to reference that exact Action content.

SHOULD — pin security-sensitive automation dependencies to immutable identities.

AVOID — floating references such as mutable branches for privileged CI dependencies.

This same principle applies beyond GitHub Actions:

text
Copy
bad trust anchor:
some-tool@main

stronger trust anchor:
verified immutable revision / digest
Commit and tag signing
Git supports cryptographic signatures for commits, tags, merge tags, and related operations. GitHub verifies GPG, SSH, and S/MIME signatures for supported commit/tag workflows.

Signing answers a question like:

“Was this object signed by a credential mapped to the expected identity under the verifier’s policy?”

It does not by itself answer:

“Was this change reviewed, CI-tested, authorized for production, and produced by our release pipeline?”

SHOULD — require signed commits or tags where provenance requirements justify the key-management and usability cost.

MUST — combine signing with authorization and protected-ref rules when the goal is source integrity.

A subtle hosted-platform behavior is that signature-verification status can be historical platform metadata; GitHub documents persistent verification records even as signing-key state changes. Therefore the meaning of a “Verified” badge must be understood in the platform’s verification model rather than interpreted as timeless present-day key authorization.

NEVER — treat “Verified commit” as equivalent to “approved production change.”

Source provenance
Modern supply-chain assurance goes beyond signing individual commits. SLSA’s Source Track defines source provenance describing how a revision came to exist on a protected branch or tag, including evidence around the source-control process.

This is a more complete production model:

text
Copy
commit cryptographic identity
           +
protected branch acceptance
           +
review evidence
           +
CI/release provenance
           +
artifact identity
           =
stronger supply-chain evidence
SHOULD — record artifact-to-source provenance for important production releases.

MUST — deploy the tested artifact, not silently rebuild an ambiguous mutable branch later.

SLSA also highlights verification: provenance has little value unless consumers actually check it.

Secrets committed to Git
This is an incident, not a cleanup-only problem.

A normal revert leaves the secret in earlier Git history. GitHub explicitly warns that reverting a secret-containing commit does not remove the sensitive value from repository history.

Correct incident thinking is:

text
Copy
secret exposed
    |
    +--> credential compromise response / revoke or rotate
    |
    +--> stop further propagation
    |
    +--> history rewrite if removal is necessary
    |
    +--> coordinate clones/caches/PR refs/LFS
    |
    +--> investigate access and downstream usage
History-removal documentation recommends dedicated history-filtering approaches and explains that pull-request refs, cached views, forks/clones, and LFS content complicate complete cleanup.

MUST — assume an exposed credential requires credential remediation; history rewriting alone does not restore secrecy.

NEVER — “fix” a committed password merely by deleting it in a later commit.

SHOULD — use pre-commit detection as developer feedback and server-side/host secret protection as defense in depth.

Audit
Git object history answers many questions about source evolution, but enterprise audit often needs additional events:

text
Copy
who authenticated
who changed permissions
who bypassed protection
who altered repository rules
who approved a PR
which credential performed an action
who deleted a branch/tag
which CI identity deployed
GitHub and GitLab expose audit event systems for repository/organization administrative actions beyond what the commit graph contains. GitHub also supports audit streaming to retain persistent copies externally.

MUST — retain administrative audit records separately when compliance or forensic requirements exceed Git history.

SHOULD — correlate ref-update events using:

text
Copy
actor identity
authentication mechanism
repository
old OID
new OID
ref name
policy decision/bypass
request/run identifier
timestamp
SHOULD — avoid logging raw credentials, credential-bearing URLs, or unnecessarily sensitive repository contents.

Abuse and resource exhaustion
Repository infrastructure can be abused through:

enormous pushes,
pathological object histories,
CI-trigger storms,
repeated failed authentication,
repeated merge-queue churn,
intentionally expensive validation,
excessive API polling.
GitHub notes, for example, that reordering a busy merge queue can force rebuilds of queued candidates because the candidate graph changes.

SHOULD — rate-limit expensive automation by authenticated principal and repository where possible.

SHOULD — deduplicate CI for obsolete commits and cancel superseded jobs when safe.

MUST — ensure rate limiting cannot bypass correctness gates. When overloaded, fail closed on protected release actions rather than silently skipping validation.

Releases, scalability, migrations, and operational lifecycle
Git history management becomes substantially harder once repositories produce public releases, accumulate years of history, or need structural migration.

Release identity
A release needs an immutable answer to:

text
Copy
What exact source produced this?
Git tags are common release anchors. Git documentation recommends annotated tags for releases, while lightweight tags are better suited to temporary/private labeling. Git also strongly discourages silently replacing an already published tag with a different object because consumers can otherwise have different source content associated with “the same” version.

MUST — make published release identifiers immutable.

SHOULD — protect release tags from ordinary force-update or deletion.

SHOULD — use signed annotated tags when release authenticity requires it.

A robust release relationship is:

text
Copy
version 3.8.2
      |
      v
protected tag v3.8.2
      |
      v
commit 9f...
      |
      +--> build provenance
      |
      v
artifact digest sha256:...
The artifact digest should identify what was actually deployed; the Git commit identifies source; the provenance binds the two.

Semantic Versioning
SemVer 2.0.0 requires software using SemVer to define a public API and gives semantic meaning to major, minor, and patch increments. It also states that once a version has been released, that version’s contents must not be modified.

MUST — define what constitutes the public compatibility contract before claiming SemVer.

For backend systems that can include:

text
Copy
HTTP APIs
event schemas
database integration contracts
SDK interfaces
CLI behavior
configuration formats
plugin APIs
AVOID — calculating version changes from commit-message labels alone when compatibility cannot be inferred mechanically.

Conventional Commits is an optional commit-message convention designed to support automation and map concepts such as feat, fix, and breaking changes into SemVer-oriented workflows. It is not a native Git correctness requirement.

MAY — use Conventional Commits for changelog/version automation.

SHOULD — make the merge/squash message comply with the convention if the canonical branch is squash-based.

Release supply-chain controls
The 2026 OpenSSF Project Security Baseline includes controls requiring official release assets at relevant maturity levels to be signed or represented in a signed manifest with cryptographic hashes; the baseline also emphasizes unique release identifiers.

SHOULD — treat release signing/provenance as part of the release pipeline, not an informal maintainer workstation task, for high-assurance systems.

MUST — preserve reproducible mapping from release identifier to artifact/source provenance even if the repository is later reorganized.

Release branches
Release branches are justified when a released line must remain independently serviceable.

Example:

text
Copy
main
  |
  +---- 6.0 development
  |
release/5.x ---- critical maintenance
  |
release/4.x ---- security-only support
MUST — document support windows and backport rules.

MUST — test the actual release branch after a backport. A change that passed on main can fail when applied to an older dependency/API state.

AVOID — merging old release branches wholesale back into main merely to “keep them synchronized.” Instead, integrate intentional fixes. Trunk-based release-branch guidance explicitly recommends keeping trunk authoritative and selectively applying release fixes.

Large repositories
Repository scale appears in several dimensions:

text
Copy
number of files
total historical blob size
number of commits
number of refs
number/size of packfiles
checkout size
working-tree scan cost
network clone/fetch cost
Git provides specialized mechanisms for these different bottlenecks.

The commit-graph accelerates commit graph walks; multi-pack-indexes accelerate object lookup across packs; git maintenance manages these supporting structures incrementally; Scalar configures advanced Git features for very large repositories.

SHOULD — measure the actual bottleneck before adopting repository-scale complexity.

Maintenance
git gc performs housekeeping including object compression, unreachable-object cleanup, ref packing, reflog cleanup, and potentially supporting-index maintenance.

SHOULD — let canonical repository infrastructure schedule and monitor maintenance rather than running aggressive manual pruning ad hoc.

NEVER — run destructive pruning as a first response to “repository uses too much disk” without understanding unreachable-object recovery and retention implications.

Useful operational metrics include:

text
Copy
repository/object-store size
packfile count
ref count
clone/fetch/push latency
maintenance duration
commit-graph/MIDX failures
fsck errors
working-tree status latency
CI checkout time
LFS transfer volume
Git exposes Trace2 and lower-level trace facilities for performance, refs, packet exchange, setup, shallow operations, and pack access, providing a foundation for detailed diagnosis when Git itself is the bottleneck.

Working-tree status performance
git status may need to scan many paths for untracked files, making very large working trees expensive.

Possible optimizations include sparse checkout, filesystem monitoring where supported, and repository-scale tooling, but each affects developer and automation assumptions. Git’s filesystem monitor is currently available only on selected platforms, so cross-platform CI cannot assume identical optimization behavior.

Sparse checkout
Sparse checkout limits which paths populate the working tree; sparse indexes can further reduce index cost for large repositories.

MAY — use sparse checkout in monorepos when developers or CI only need a bounded subset.

MUST — test tooling under sparse conditions before standardizing it. Scripts that walk the filesystem and assume “all repository files are present” can behave differently from Git-aware commands.

Partial clones
Partial clone deliberately omits some reachable objects and retrieves missing objects from a promisor remote on demand. It exists specifically to improve very large-repository operation.

MAY — use partial clone to reduce initial object transfer.

MUST — recognize that some Git operations may require network access later to materialize missing objects.

AVOID — designing offline build/recovery procedures around a partial clone unless required objects are guaranteed present.

Shallow clones
A shallow repository contains intentionally incomplete history with some ancestry cut off. clone --depth creates such a repository; it can later be deepened or unshallowed.

This is extremely common in CI and extremely easy for agents to forget.

MUST — determine whether history-dependent operations are running in a shallow checkout.

Potentially affected logic includes:

text
Copy
version calculation from historical tags
merge-base calculations across old ancestry
full changelog generation
historical policy checks
bisecting
repository migration tools
SHOULD — fetch the minimum sufficient history where performance matters, but fetch complete history where the algorithm actually requires it.

NEVER — interpret “commit not found” in a shallow clone as proof that the commit never existed upstream.

Shared clones and alternates
Git can create local repositories that borrow objects from another repository using alternates or shared-clone behavior. The clone documentation warns that object deletion in the source can make such a dependent clone unsafe if borrowed objects disappear.

AVOID — using object-borrowing clones as durable independent backups.

MUST — sever the dependency by copying required objects if the clone must become self-contained.

Git LFS
Git LFS stores small pointer files in Git while large content is managed separately by an LFS service.

This creates a second object lifecycle.

text
Copy
Git commit
   |
   v
LFS pointer
   |
   v
external LFS object
MUST — include LFS storage in backup, migration, authentication, access-control, and retention planning.

NEVER — assume deleting LFS tracking or a Git branch automatically removes remote LFS objects. GitHub’s LFS documentation notes separate cleanup considerations and orphaned data behavior.

Submodules
A submodule records another repository relationship; .gitmodules contains path and URL information. Recursive clone/update can cause Git to follow nested repository relationships.

MUST — treat submodule URLs as trust-sensitive input. Git has explicit protocol controls, including restrictions intended to prevent recursive operations from casually using protocols derived from untrusted input.

MUST — pin submodules to exact commits for reproducibility.

SHOULD — choose submodules only when independent repository ownership/versioning is genuinely valuable. They increase clone, credential, CI, release, security, and developer-workflow complexity.

Monorepo versus multiple repositories
Git does not decide architecture ownership boundaries for you.

A monorepo can simplify:

text
Copy
atomic cross-component source changes
global refactoring
single review graph
dependency visibility
while increasing:

text
Copy
checkout/index scale
CI selection complexity
authorization granularity
tooling requirements
Multiple repositories improve independent permissions and lifecycle but make cross-repository changes distributed operations with no Git-native atomic transaction.

MUST — recognize that two repositories cannot be atomically committed together using normal Git semantics.

For cross-repository migrations, design compatibility windows:

text
Copy
repo A publishes backward-compatible contract
        |
repo B migrates
        |
old behavior retired later
rather than expecting synchronized merge timestamps to provide atomicity.

History rewriting
History filtering or large-scale rebase changes commit identities because trees, parents, or metadata change. Git’s filter-branch documentation warns that rewritten and original histories have different object IDs and no longer naturally converge. Modern GitHub migration/remediation documentation generally recommends git-filter-repo for serious history transformation.

MUST — treat repository-wide history rewriting as a migration, not cleanup.

A migration plan should cover:

text
Copy
freeze or coordinate writes
backup canonical repository
define exact rewrite
rewrite all intended refs
validate resulting history
replace canonical refs
update CI/integrations
invalidate old clones
coordinate forks
recreate/reconcile open PRs
handle LFS
re-sign/re-attest releases if necessary
communicate old-to-new identities
NEVER — rewrite widely consumed public history casually.

Sensitive-data history rewrite
This is particularly disruptive because data may remain in:

forks,
developer clones,
cached patches,
closed review refs,
build artifacts,
package registries,
LFS stores,
mirrors.
GitHub explicitly documents these caveats around sensitive-data removal.

MUST — distinguish “removed from canonical Git reachability” from “eradicated from every copy.”

Hash-format evolution
Git has SHA-256 repository support and a hash-transition design. Current commands can report a repository’s object format, so infrastructure should avoid embedding assumptions that “Git object ID” always means a SHA-1-shaped string.

SHOULD — represent object identifiers opaquely in APIs where possible.

AVOID — naming application fields sha1 unless the SHA-1 algorithm is genuinely part of the contract. Prefer oid, commit_id, or {algorithm, digest}.

Ref storage evolution
Current Git can report the repository’s reference storage format, including traditional files/packed-refs and reftable.

NEVER — build Git integration by directly parsing .git/refs files when official Git commands or libraries can expose refs.

Internal repository representation is an implementation boundary subject to evolution.

Default branch migration
Renaming the default branch is not just a git branch -m operation in a production ecosystem.

An agent should inspect:

text
Copy
remote default HEAD
branch protections/rulesets
CI triggers
deployment rules
scripts
documentation
badges
submodules
release jobs
automation API calls
base branches of open PRs
monitoring queries
MUST — treat default-branch renaming as an integration migration.

Rollback of repository-policy migrations
Changing from Gitflow to trunk, changing merge method, enforcing signing, switching default branch, or adopting merge queues can strand active work if rolled out instantaneously.

SHOULD — separate policy migration into phases:

text
Copy
observe existing behavior
        |
introduce tooling compatible with both models
        |
migrate active branches/PRs
        |
enable enforcement
        |
remove legacy assumptions
A rollback plan should preserve the old canonical references or document a deterministic mapping rather than force-rewriting active developer histories unnecessarily.

AI coding-agent implementation contract, production failure patterns, and knowledge graph
An AI coding agent should not interpret:

“Implement Git flow”

as:

“Create develop, feature/*, release/*, and hotfix/* branches.”

That is precisely the shallow implementation this knowledge base is intended to prevent.

The agent must first infer or discover the repository’s existing release and collaboration contract.

Questions that MUST be answered before changing a production repository workflow
Question	Why it matters
What is the canonical repository and default protected branch?	Establishes authority.
Is this SaaS/CD, periodically released software, or multiple concurrently supported versions?	Determines whether Gitflow, trunk, or release branches make sense.
What exact branches/tags are protected?	Prevents accidental policy bypass.
Are force pushes permitted anywhere?	Determines rewrite safety.
What merge methods are allowed?	Determines resulting history shape.
Are commits expected to be individually buildable/bisectable?	Affects squash versus preserved commits.
Are required checks strict/current-base checks?	Determines stale-base race handling.
Is a merge queue enabled?	Changes CI candidate identity and events.
What approvals/CODEOWNERS rules exist?	Determines authorization state.
Are signatures mandatory?	Affects commit creation/rebase/bot identities.
How are release versions generated?	Commit messages/tags/history may be inputs.
Are release tags immutable/protected?	Determines release reproducibility.
Are there active release/support branches?	Determines backport topology.
How are production deployments tied to commits/artifacts?	Prevents source/artifact drift.
Is the CI clone shallow, sparse, or partial?	Changes available repository data.
Are LFS or submodules used?	Adds separate object/credential lifecycles.
Are there multiple worktrees?	Affects local branch operations.
Is repository history consumed by external tooling?	History rewriting can break it.
Are secrets or regulated data present historically?	Changes migration/retention handling.
What Git versions and OS/filesystems are supported?	Determines feature and checkout compatibility.
What rollback method is expected for bad production releases?	Source revert may not equal service rollback.

MUST — answer these from repository configuration and code wherever possible rather than inventing a generic workflow.

Existing-codebase checks before touching anything
An agent should build a repository inventory approximately equivalent to:

text
Copy
Repository state
  current HEAD + detached status
  clean/dirty working tree
  staged changes
  merge/rebase/cherry-pick in progress
  worktrees
  shallow/partial state

Topology
  local branches
  remote-tracking refs
  upstream configuration
  tags
  release branches
  merge bases
  recent merge style

Configuration
  .gitconfig-relevant repository settings
  .gitattributes
  .gitignore
  .gitmodules
  LFS attributes
  hooks/hook configuration

Hosted policy
  default branch
  protected refs
  force-push policy
  required checks
  approvals
  CODEOWNERS
  signing requirements
  merge methods
  merge queue

Automation
  CI triggers
  release jobs
  versioning logic
  deployment source
  bot credentials
  third-party actions/plugins

Documentation
  CONTRIBUTING
  release instructions
  support policy
  architecture decisions
MUST — preserve unrelated uncommitted user changes.

NEVER — run destructive reset, clean, rebase, checkout, or forced branch manipulation merely to produce a convenient working state unless the task explicitly owns those changes.

Common production bugs and what they reveal
Incorrect implementation	Production failure
“origin/main is always current.”	Decisions use stale distributed state.
“Push failed, use --force.”	Concurrent work is lost.
“--force-with-lease makes force push impossible to misuse.”	Implicit lease may be affected by background fetch; expected state can still be wrong.
“Green PR means safe to merge.”	Base changed after testing; combined state was never validated.
“Delete branch to delete data.”	Objects survive through reachability, reflogs, clones, caches, or host refs.
“Revert secret commit.”	Secret remains in history.
“Signed means authorized.”	Signature authenticity and repository authorization are different controls.
“Use client pre-commit hook to enforce policy.”	Users can bypass or lack the hook; server still accepts bad state.
“Store the seven-character SHA.”	Abbreviation can become ambiguous.
“OID is always SHA-1.”	Object-format evolution breaks schema assumptions.
“CI always has complete history.”	Shallow checkout breaks history-dependent logic.
“All repository files exist locally.”	Sparse/partial clones invalidate that assumption.
“Gitignore hides this tracked secret/config.”	.gitignore does not affect already-tracked files.
“Run on Linux; Windows will be equivalent.”	Case, line-ending, and symlink behavior can differ.
“Rebase conflict: accept ours.”	Rebase side semantics can differ from intuitive branch ownership.
“Stash pop always restores state.”	Stash application itself can conflict.
“Feature needs six months, therefore feature branch needs six months.”	Massive integration divergence accumulates.
“We have dev/stage/prod, therefore we need three branches.”	Source topology becomes incorrectly coupled to deployment environments.
“Multiple refs in one push are automatically atomic.”	Server capability/atomic push semantics were ignored.
“Push timed out, retry.”	First update may already have succeeded.
“Git revert rolls back production.”	Database/external side effects remain.
“Tag v2.4.0 can be moved to the corrected build.”	Consumers can obtain two different releases with one identifier.
“All Git repos have .git/refs/heads/* files.”	Ref-storage format is an internal implementation detail.
“Submodule is just another folder.”	It has independent repository, trust, credential, and lifecycle semantics.
“LFS object is stored in the Git commit.”	Commit contains pointer; binary lifecycle is separate.
“PR metadata exists in Git.”	Reviews/checks/queue state are hosting-platform metadata.

What AI agents are especially likely to get wrong
NEVER — introduce a branching model solely because its name appeared in the request. “Git flow” is frequently used colloquially to mean “our Git workflow”; classical Gitflow is a specific model with significant costs.

NEVER — rewrite shared history without first determining publication and consumer state.

NEVER — force push a protected or shared branch to make an automation error disappear.

NEVER — resolve a semantic merge conflict without examining surrounding code and running relevant tests.

NEVER — put production secrets into a CI context that executes untrusted change code.

NEVER — use mutable branch/tag names as the sole identity of an already-built production artifact.

NEVER — assume the local repository knows current hosted authorization, PR, approval, or merge-queue state.

NEVER — erase or overwrite unrelated developer changes while “cleaning” a worktree.

NEVER — assume a branch deletion, commit revert, or history rewrite is sufficient for privacy erasure.

AVOID — large autogenerated reformatting combined with functional changes. It damages reviewability, makes conflicts worse, and weakens git blame/history usefulness.

AVOID — mixing repository-wide renames, dependency upgrades, schema migrations, and product behavior in one gigantic PR when they can be independently staged. Google’s engineering guidance strongly favors smaller review units that are easier to reason about and roll back.

AVOID — automatic git pull in infrastructure scripts without specifying intended reconciliation semantics. Fetch, merge, and rebase represent different state transitions; automation should state exactly which one it wants. Git documents pull as fetching followed by integration rather than as a simple synchronization primitive.

Required testing strategy for Git-aware code
A production Git feature should not be tested only against one happy-path repository.

Test class	Required scenario
Basic history	Root commit, linear commits, branch creation/deletion.
Graph topology	Merge commits, multiple branches, nontrivial merge bases.
Concurrency	Two clones update the same branch concurrently.
Optimistic locking	Correct and incorrect expected-old-OID cases.
Atomicity	Multi-ref update success and induced failure.
Conflicts	Merge, rebase, cherry-pick conflicts.
Dirty worktree	Staged and unstaged unrelated changes.
Detached HEAD	Operation without a current branch.
Recovery	Reflog-based restoration after mistaken ref movement.
Remote failure	Connection failure before push and ambiguous post-send failure.
Authorization	Protected ref rejection and ordinary branch acceptance.
CI policy	Required checks missing, failed, stale, and successful.
Merge queue	Candidate tested with changed target branch.
Filesystem	Case collisions, CRLF/LF normalization, symlinks where applicable.
Shallow clone	Incomplete ancestry.
Partial clone	Missing object fetched on demand/offline failure.
Sparse checkout	Tool runs without every repository path materialized.
Submodules	Missing/unavailable/unauthorized nested repository.
LFS	Pointer present but LFS object unavailable.
Large repo	Meaningful object/ref/file scale.
Corruption	Missing/invalid object detected through integrity checking.
History rewrite	Old and rewritten identities deliberately diverge.
Release	Protected annotated tag maps to expected commit/artifact.
Secrets	Detection path and history-remediation process.
Rollback	Revert source while validating external-state recovery separately.

Two independent clones plus a bare test remote are particularly valuable because a single local repository cannot reproduce the most important stale-state and non-fast-forward races.

Operational metrics
A Git platform or engineering organization SHOULD measure enough to distinguish repository correctness problems from workflow friction.

Useful metrics include:

text
Copy
pull/merge request lead time
time waiting for review
time waiting for CI
merge-queue depth and wait
required-check failure rate
flaky-check retry rate
non-fast-forward rejection rate
force-push count
protected-ref bypass count
reverted-change rate
hotfix frequency
branch age distribution
release backport count
clone/fetch/push latency
repository/object size
maintenance duration
CI checkout time
shallow/partial-clone object misses
LFS transfer failures
authentication failures
fsck/integrity errors
These metrics should not become performance targets that incentivize bypassing review. Google’s review guidance explicitly frames review speed as a system-level throughput concern while maintaining the overriding goal of code health.

A safe agent execution contract
Before an AI agent changes repository history or workflow, its decision path SHOULD resemble:

text
Copy
Inspect
  |
  +--> repository state clean/safe?
  |
  +--> existing workflow documented/configured?
  |
  +--> canonical branch and protections known?
  |
  +--> local remote state refreshed?
  |
  +--> publication/shared-history status known?
  |
  +--> CI/release implications known?
  |
  v
Plan explicit state transition
  |
  +--> expected old ref OID
  +--> desired new OID
  +--> required policy/checks
  +--> rollback/recovery point
  |
  v
Perform smallest safe mutation
  |
  v
Verify
  |
  +--> graph
  +--> worktree/index
  +--> remote ref
  +--> tests
  +--> CI/platform policy
  |
  v
Record/audit where applicable
For shared ref updates, the governing principle is:

Observe → establish expected state → mutate conditionally → verify authoritative state.

This is more important than memorizing any individual Git command.

Knowledge graph relationships
Git should not be stored as an isolated “version-control” topic in an AI engineering knowledge base. It has strong dependency edges to several other production domains.

Related knowledge topic	Git relationship
Continuous integration	Git ref changes trigger validation; candidate identity must be immutable and race-safe.
Continuous delivery	Branch topology should reflect deployment/release topology rather than replace it.
Feature flags	Allow trunk integration without immediate exposure.
Database migrations	Git revert cannot automatically reverse persisted-state transformations.
Backward-compatible API evolution	Enables short-lived branches and independently deployed components.
Semantic Versioning	Tags/releases need compatibility semantics.
Artifact repositories	Git source identity must map to immutable build artifacts.
Software-supply-chain security	Protected refs, review, signatures, provenance, and trusted builds establish source integrity.
Secrets management	Credentials must stay outside repository history and untrusted CI.
Authentication	Git transport authenticates users/workloads.
Authorization/RBAC	Hosting platform decides who may change protected refs.
Audit logging	Administrative actions and bypasses exist beyond commit history.
Distributed systems	Fetch/push involve stale state, optimistic concurrency, retries, and ambiguous failures.
Transactions	Ref updates have local/remote atomicity constraints; multiple repositories do not form one transaction.
Idempotency	Automation must reason in expected old/new ref states.
Caching	Remote-tracking refs are staleable caches; CI caches must be bound to appropriate immutable inputs.
Monorepo architecture	Repository scale affects checkout, CI selection, ownership, and dependency structure.
Observability	Git Trace2, platform audits, CI metrics, and ref-transition logs diagnose failures.
Incident response	Secrets, malicious commits, compromised credentials, and bad releases need coordinated source and runtime recovery.
Disaster recovery	Reflogs help locally but do not replace canonical backups and restoration testing.
Release engineering	Protected tags, provenance, signing, and immutable artifacts link source to shipped software.
Code review	Small coherent changes and domain-aware review are controls against source-integrity and correctness failures.
Deployment rollback	Source history rollback and production-state rollback are separate state machines.
Schema evolution	Long-running branches magnify migration compatibility problems; incremental compatibility reduces branch lifetime.
Infrastructure as code	Git ref authorization can become production infrastructure authorization when merges trigger deployment.

The final production rule for an AI coding agent is therefore:

Git correctness is graph correctness plus distributed-state correctness plus policy correctness.

A basic implementation thinks in commands:

text
Copy
checkout
pull
commit
push
merge
An experienced backend engineer thinks in invariants:

text
Copy
Which immutable object represents the candidate?

Which mutable ref currently points where?

How fresh is my observation?

What concurrent update can occur before my write?

What expected old state protects this mutation?

Which repository policy authorizes the transition?

Which exact combined state did CI validate?

Can the operation partially succeed?

What happens if the network fails after the server commits it?

Which history is already public and therefore unsafe to rewrite?

How will a release consumer identify these exact bytes later?

Does rollback alter only source, or also persistent/external state?

Could untrusted repository code reach privileged credentials?

What audit evidence proves why this commit became production?

What happens to clones, caches, submodules, LFS objects,
release branches, tags, and CI when history changes?
That shift—from command memorization to object identity, graph topology, explicit state transitions, optimistic concurrency, controlled authorization, immutable release provenance, and deliberate recovery semantics—is what separates a Git workflow that merely works on one developer laptop from production-grade version-control engineering.
