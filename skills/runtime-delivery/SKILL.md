---
name: runtime-delivery
description: "Use when implementing or changing runtime foundations and delivery: project structure and module boundaries, application bootstrap and dependency initialization, configuration loading and validation, environment and tenant configuration, connection pools and management, networking behavior, load balancing assumptions, service discovery, service-to-service communication, graceful startup and shutdown, deployment safety and health gates, CI/CD pipelines including migration ordering, and infrastructure configuration. Loads production implementation papers with MUST/SHOULD/AVOID/NEVER rules, failure modes, and verification checklists to read before writing code. For schema migration sequencing use migration-evolution; for observability emitters use production-operations; for code-level architecture style decisions use system-architecture-harness."
---

# Runtime & Delivery Implementation

## Overview

Implementation intelligence for the layer every feature stands on. Each reference paper captures the unglamorous failures: configs that validate nowhere and break at boot in production, pools that exhaust under bursts, shutdowns that drop in-flight work, deployments that skip migration ordering, and CI that proves nothing about the released artifact.

**Core principle:** The runtime is a contract with the operating environment. Startup, shutdown, configuration, connections, and deployment must behave correctly under partial failure, bursts, and mixed versions — or every feature built on them inherits the risk.

## Implementation Law

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

Use this skill when implementing or changing:

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

1. Identify the runtime mechanism being changed and its failure window (boot, reload, burst, shutdown, deploy); select primary papers.
2. Read the primary papers fully, including failure modes and checklists.
3. Answer the paper's pre-implementation questions; label autonomous assumptions and their impact.
4. Run the existing-codebase checks: read deployed manifests, real environment variables, pipeline definitions, and probe configuration rather than trusting defaults.
5. Convert each MUST/SHOULD/AVOID/NEVER into decisions with enforcement points: validated config schemas, bounded pools, drain deadlines, health gates, and pipeline checks — each with a test or drill.
6. Implement the smallest safe slice; carry the paper's verification checklist (bad config at boot, kill -TERM under load, rollback) into the test plan.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Boundary Map

| If the task also involves | Also use |
|---|---|
| Migration ordering within deploys | `migration-evolution` (030, 134) |
| Health/readiness emitter design | `production-operations` (059) |
| Inter-service retry/timeout policy | `resilience-flow-control` (052, 053) |
| Config secrets storage and rotation | `security-privacy` (063) |
| Module boundary and architecture style | `system-architecture-harness` |
| Pipeline test stages and gates | `quality-release` (090, 093) |

## Output Contract

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
