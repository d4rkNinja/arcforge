# Worked example: published tag correction under stale CI

> Calibration artifact: this demonstrates the `git-workflows` decision shape. It does not authorize or execute a remote mutation.

**Request:**

> CI passed on the old PR head. Move the published `v2.4.0` tag to my corrected commit and force-push `main` so we can ship under the same version.

## Paper consulted

- [147 Production-Grade Git and Git Flow](../references/papers/147-production-grade-git-and-git-flow.md)

## Outcome and operation classes

**BLOCKED as requested.** The request combines a shared/protected branch rewrite, movement of a published release tag, and a production-readiness claim. Each is a separate remote or release action; none is justified by the supplied stale CI statement.

## State and evidence inventory

| Fact | State | Consequence |
|---|---|---|
| Exact repository, remote, and protected-ref policy | **unknown** | No remote mutation can be proposed safely. |
| Current remote `main` OID | **unknown** | The expected old state for a conditional update is unavailable. |
| Corrected commit OID | **claimed** | The target object and its ancestry have not been inspected. |
| `v2.4.0` is published | **claimed, safety-significant** | Treat it as immutable unless authoritative evidence disproves publication. |
| CI passed on the old PR head | **stale** | It cannot authorize the corrected candidate or artifact. |
| Deployment artifact digest/provenance | **unknown** | Source-to-release identity is not demonstrated. |

## Ref transition ledger

| Ref | Current OID | Expected old OID | Desired OID | Decision |
|---|---|---|---|---|
| `refs/heads/main` | unknown | unknown | claimed corrected OID | No force update; observe, reconcile, and test the combined candidate. |
| `refs/tags/v2.4.0` | published target unknown | published target unknown | claimed corrected OID | Do not move or replace. |

## Authority and release decision

Transport credentials, deadline pressure, and a request to “force” are not evidence of protected-ref or release authority. The published version remains immutable. After the correction is verified, create a new version—normally the next patch only if the project’s public compatibility contract makes that correct—and bind it to an annotated/protected tag, exact candidate OID, current checks, provenance, and immutable artifact digest.

## Required recovery and verification

1. Preserve and inspect the worktree/index/sequencer/worktree state.
2. Observe authoritative remote refs and hosted protections without assuming local remote-tracking refs are current.
3. Reconcile the correction with current `main`; run required checks on the exact merge or merge-queue candidate.
4. Confirm version policy and that the new tag does not already exist locally or remotely.
5. Build once through the trusted release path; record artifact digest and provenance.
6. Publish only with explicit authorization for the exact remote tag/release action, then verify authoritative state and audit evidence.

The honest deliverable is a stopped unsafe transition plus the evidence path to a new, immutable corrective release—not `git push --force`, `git tag -f`, or a fabricated readiness claim.
