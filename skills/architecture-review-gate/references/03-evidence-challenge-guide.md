# Evidence and Challenge Guide

## Evidence hierarchy

Prefer stronger evidence when available:

1. reproducible tests, measurements, traces, restore/failover results;
2. deployed configuration, schemas, contracts, policy, and code paths;
3. versioned architecture decisions and runbooks aligned with implementation;
4. incident reports and operational records;
5. owner statement or vendor documentation;
6. reviewer inference;
7. unsupported assertion.

Label the evidence class in material findings.

## High-value challenges

| Claim | Ask for |
|---|---|
| “Scales to 100k RPS” | workload shape, bottleneck model, test method, saturation point, dependency quotas |
| “Highly available” | journey SLO, topology, quorum/client behavior, failover test, degraded mode |
| “Zero data loss” | durability boundary, acknowledged-write semantics, RPO, corruption and restore evidence |
| “Exactly once” | precise boundary, transaction/deduplication proof, crash/replay behavior |
| “Secure” | threat model, identity/authz, tenant tests, secret/key lifecycle, incident evidence |
| “Multi-region” | write authority, routing, conflict, fencing, lag, failover/failback, residency |
| “Backed up” | restore drill, timing, permissions, dependencies, reconciliation |
| “Can roll back” | version compatibility, data effects, command/runbook, tested outcome |
| “AI is accurate” | task dataset, baseline, metrics, severe slices, repeated runs, online monitoring |
| “Agent is safe” | tool scopes, policy enforcement, approval, sandbox, injection eval, kill switch |

## Finding anatomy

Each material finding contains:

- **Claim/control reviewed**
- **Evidence** and location
- **Failure mechanism**
- **Impact and affected journey/data**
- **Severity and confidence**
- **Smallest approval condition**
- **Owner and proof method**

## Avoid false precision

Use ranges and confidence when evidence is incomplete. A quantified estimate with explicit assumptions is better than a precise number with hidden assumptions. Do not convert missing evidence into a factual defect; report the gap and why it matters.

## Closure evidence

A finding closes only when fresh evidence demonstrates the required postcondition. A code diff, agent report, or design promise is insufficient when the finding concerns runtime behavior, recovery, concurrency, migration, security, or performance.
