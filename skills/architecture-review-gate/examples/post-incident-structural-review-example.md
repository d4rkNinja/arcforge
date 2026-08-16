# Post-Incident Structural Review Example

This fictional example shows how to separate an initiating error from the architecture that amplified it.

## Incident and Evidence

A production credential rotation placed new storage credentials in staging and removed the old production credential. For 38 minutes, all writes and 31% of reads failed. Evidence includes the change record, secret-manager audit log, dependency traces, alert timeline, and operator transcript.

## Causal Chain

| Link | Finding | Evidence state |
|---|---|---|
| Architecture decision | one shared object store and credential set served upload, configuration, and asset paths | implemented: deployment/configuration and dependency map |
| Hidden dependency | authentication and static asset delivery indirectly depended on the same credentialed path | observed: traces during incident; absent from architecture diagram |
| Initiating trigger | old production credential was removed after the replacement was written to staging | observed: audit log |
| Propagation | clients retried writes while unrelated critical paths lost shared storage access | observed: retry and dependency metrics |
| Blast radius | all writes and 31% of reads failed across three products | observed: journey SLIs |
| Detection | availability alerts fired after seven minutes; no semantic rotation check existed | observed: alert timeline and missing control |
| Recovery constraints | rollback required manual environment identification; retries added load after restoration | observed: operator transcript and queue metrics |
| Structural correction | environment-bound credential automation, staged synthetic validation, bounded retries, dependency isolation, and tested rollback | designed: owner and tests assigned; not yet validated |

## Trigger Versus Enabling Conditions

The deletion was the trigger. Enabling conditions were environment ambiguity, manual rotation, shared critical-path concentration, missing semantic validation, unbounded retry amplification, and an untested rollback path. Replacing or retraining the operator would leave these conditions available to another trigger.

## Five-Gate Findings

- **A — Problem and fitness:** the rotation's required availability and acceptable blast radius were never defined.
- **B — State and boundaries:** a shared dependency crossed product boundaries without explicit ownership or isolation.
- **C — Failure and assurance:** failure propagation and retry load were not tested; the trigger and blast radius are now observed.
- **D — Delivery and operation:** configuration lacked code-equivalent staging, validation, and rollback controls.
- **E — Economics, complexity, and evolution:** no Complexity Ledger recorded the shared dependency, operational duty, reversal path, or validation trigger.

## Verdict and Conditions

**Verdict: BLOCK repeated rotation until conditions are validated.** This is not a general release block for unrelated changes.

1. Platform owner automates environment-bound rotation and proves staged synthetic read/write checks.
2. Product owners remove authentication and static assets from the shared failure path or prove bounded degradation.
3. Reliability owner caps retry attempts and concurrency, then demonstrates recovery without load amplification.
4. Operations owner rehearses rollback and records time to detect, mitigate, recover, and understand.
5. Architecture owner creates a Complexity Ledger entry with expected lifetime, cost, reversibility, review date, and recurrence trigger.

## Governed Metrics

| Metric | Definition/unit | Intended decision | Confounders/gaming | Owner | Retirement |
|---|---|---|---|---|---|
| Rotation validation coverage | production credentialed paths passing synthetic read/write checks / all critical paths, percent per rotation | allow promotion to revoke-old phase | stale inventory or tests that bypass actual policy | platform security | review quarterly; retire when mechanism changes |
| Shared-dependency blast radius | affected critical journeys / mapped critical journeys, percent per exercise | prioritize isolation work | incomplete journey map or synthetic-only exercises | reliability | review after each topology change |

These metrics evaluate controls and system trends. They must not rank the operator or any individual engineer.
