---
name: runtime-delivery
description: "Use when thinking through, reviewing, changing, or verifying runtime and delivery foundations: project structure, bootstrap, configuration, connection pools, networking, discovery, service communication, graceful startup or shutdown, deployment gates, CI/CD, migration ordering, or infrastructure configuration. For schema evolution use migration-evolution; for telemetry use production-operations."
---

# Think Through Runtime & Delivery

## Overview

Production guidance for the layer every feature stands on. Each reference paper captures the unglamorous failures: configs that validate nowhere and break at boot in production, pools that exhaust under bursts, shutdowns that drop in-flight work, deployments that skip migration ordering, and CI that proves nothing about the released artifact.

**Core principle:** The runtime is a contract with the operating environment. Startup, shutdown, configuration, connections, and deployment must behave correctly under partial failure, bursts, and mixed versions — or every feature built on them inherits the risk.

## Domain Law

```text
NO RUNTIME CHANGE WITHOUT:
1. the primary paper(s) for the mechanism read in full first;
2. failure behavior at boot, reload, shutdown, and deploy stated —
   not just the happy path;
3. "Existing-codebase checks" run against deployed configuration and
   pipeline reality;
4. every applicable MUST mapped to a decision, a gate, or a documented
   exception — never silently downgraded.
```

## When to Use

Use this skill when thinking through, reviewing, changing, or verifying:

- project structure, module boundaries, bootstrap, dependency injection, init ordering;
- configuration: hierarchy, defaults, validation, reload, versioning, secret separation;
- connection management: pools, timeouts, reuse, backpressure;
- networking behavior relevant to services: keepalives, DNS, retries at the transport layer;
- load balancing and health-gated traffic;
- service discovery and dependency resolution at runtime;
- service-to-service communication patterns and identity;
- graceful startup/shutdown, signal handling, drain, resource cleanup;
- deployment safety: ordering, health gates, rollback, migration hooks;
- CI/CD pipelines, artifact promotion, environment parity;
- infrastructure configuration and environment provisioning.

## When Not to Use

- Database/contract migration sequencing logic: use `migration-evolution` (030, 134).
- Telemetry emitters and alerting: use `production-operations`.
- Architecture style decisions (monolith vs services, boundaries): use `system-architecture-harness`.
- Retry/circuit-breaking policies for calls: use `resilience-flow-control`.

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
| Structure, bootstrap, DI, init order, lifecycle | [001 Project & Runtime Foundations](references/papers/001-project-and-runtime-foundations.md) |
| Config hierarchy, validation, reload, rollback | [002 Configuration Management](references/papers/002-configuration-management.md) |
| Pools, timeouts, reuse, saturation | [079 Connection Management](references/papers/079-connection-management.md) |
| Keepalives, DNS, transport behavior | [080 Networking Basics for Backend](references/papers/080-networking-basics-for-backend.md) |
| Health-gated traffic, session affinity | [081 Load Balancing](references/papers/081-load-balancing.md) |
| Discovery mechanisms and failure behavior | [082 Service Discovery](references/papers/082-service-discovery.md) |
| Inter-service calls, identity, fallbacks | [083 Service-to-Service Communication](references/papers/083-service-to-service-communication.md) |
| Signals, drain, cleanup, deadlines | [105 Graceful Shutdown](references/papers/105-graceful-shutdown.md) |
| Deploy ordering, gates, rollback windows | [106 Deployment Safety](references/papers/106-deployment-safety.md) |
| Pipelines, promotion, migration hooks | [107 CI/CD](references/papers/107-ci-cd.md) |
| Environment definitions and parity | [108 Infrastructure Configuration](references/papers/108-infrastructure-configuration.md) |

## Workflow

Use the domain workflow as shared gates, then branch by the selected mode:

- **Think:** answer the questions and stop with a reasoned decision and validation path; do not edit by default.
- **Review:** inspect the available artifact or repository and stop with evidence-backed findings; do not claim changes.
- **Change:** apply only approved decisions, then continue to Verify before claiming completion.
- **Verify:** run the relevant checks, report observed results, and label every unavailable or unrun check.

1. Identify the runtime mechanism being changed and its failure window (boot, reload, burst, shutdown, deploy); select primary papers.
2. Read the primary papers fully, including failure modes and checklists.
3. Answer the paper's pre-implementation questions; label autonomous assumptions and their impact.
4. Run the existing-codebase checks: read deployed manifests, real environment variables, pipeline definitions, and probe configuration rather than trusting defaults.
5. Convert each MUST/SHOULD/AVOID/NEVER into decisions with enforcement points: validated config schemas, bounded pools, drain deadlines, health gates, and pipeline checks — each with a test or drill.
6. Apply the active mode: stop at a runtime decision in Think; stop at findings in Review; make the smallest approved safe change in Change; run bad-config, shutdown-under-load, deployment, and rollback checks in Verify.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Companion Skills and Standalone Safety

| Type | When | Companion | Missing companion behavior |
|---|---|---|---|
| **Required** | Schema, data, or contract changes must be ordered with deployment | `migration-evolution` | Preserve mixed-version safety and stop before an unsafe rollout sequence. |
| **Recommended** | Health, readiness, startup, shutdown, or delivery signals are designed | `production-operations` | State required signals and label operations depth missing. |
| **Recommended** | Inter-service retry, timeout, or overload policy is in scope | `resilience-flow-control` | Require bounded deadlines and attempts without inventing parameters. |
| **Handoff** | Module boundaries or architecture style must change | `system-architecture-harness` | Bound the runtime decision and identify architecture depth missing. |

If a companion is unavailable, complete only the safe local runtime or delivery decision, name the missing depth, and recommend the exact technical ID or relevant installation group. Never claim unavailable material was read or weaken configuration validation, graceful shutdown, mixed-version, or rollback requirements.

## Output Contract

The selected mode is authoritative. Include only applicable fields below; a planned check is a validation path, not verification evidence.

Scale the output to the active mode: Think returns runtime and delivery decisions; Review returns findings; Change returns the repository-aware change plus pending proof; Verify returns observed boot, shutdown, deployment, and rollback evidence with unrun checks labeled. A combined flow preserves all four phases.

1. **Papers consulted** — numbers and the sections relied on.
2. **Failure-window map** — behavior at boot, reload, burst, shutdown, and deploy.
3. **Assumptions and unanswered questions** — labeled, with their design impact.
4. **Rule-to-decision map** — each applicable MUST → decision, enforcement point (schema, gate, deadline), and test.
5. **Failure modes addressed** — invalid config at boot, pool exhaustion, dropped in-flight work on shutdown, deploy skipping migrations.
6. **Verification evidence** — boot/shutdown drills under load, config validation tests, rollback rehearsal.

## Stop Conditions

Stop and revise when any of these appears:

- code is written before the failure windows (boot/reload/shutdown/deploy) are stated;
- configuration without schema validation, typed access, and defined invalid/missing behavior;
- secrets inside general config files or passed through unvalidated layers;
- pools, workers, or connections without bounds, timeouts, and saturation behavior;
- shutdown without drain deadlines, in-flight completion or explicit drop policy, and cleanup;
- startup without dependency ordering and readiness signaling;
- deploys without health gates, ordering, and a rollback window;
- pipelines that promote artifacts different from what was tested;
- environment drift between staging and production with no parity check;
- a runtime MUST downgraded to a TODO without a documented exception.

## References

Eleven production papers under `references/papers/`: 001 Project & Runtime Foundations, 002 Configuration Management, 079 Connection Management, 080 Networking Basics for Backend, 081 Load Balancing, 082 Service Discovery, 083 Service-to-Service Communication, 105 Graceful Shutdown, 106 Deployment Safety, 107 CI/CD, 108 Infrastructure Configuration. Cross-domain pointers inside the papers name the sibling skill to activate.

Worked example: [fail-fast configuration and graceful shutdown](examples/worked-example-validated-config.md).
