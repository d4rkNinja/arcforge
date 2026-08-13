# Failure Mode and Recovery Analysis

## Metadata

- System / capability:
- Critical user journey:
- Analysis date:
- Facilitator:
- Service owners:
- Last drill date:

## Recovery Objectives

| Data or capability | Maximum tolerable outage | RTO | RPO | Required integrity / ordering | Recovery authority |
|---|---:|---:|---:|---|---|
| ... | ... | ... | ... | ... | ... |

## Critical-Path Dependency Map

| Step | Component / dependency | Synchronous? | Timeout budget | Failure containment boundary | Fallback | Owner |
|---|---|---:|---:|---|---|---|
| 1 | ... | Yes | ... | ... | ... | ... |

## Failure Modes

| ID | Failure mode | Trigger / cause | Blast radius | User and data effect | Detection signal | Automatic containment | Degraded behavior | Retry / replay rule | Manual recovery | Reconciliation / repair | RTO / RPO effect | Test or drill | Owner |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F-001 | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Required Failure Classes

Analyze at least the applicable classes:

- Instance, process, pod, or host termination
- Network delay, partition, packet loss, DNS, and TLS failure
- Database primary loss, replica lag, hot partition, lock contention, and storage exhaustion
- Cache loss, stale data, stampede, and split brain
- Queue or stream lag, poison messages, duplicates, reordering, partition loss, and broker outage
- Dependency timeout, throttling, malformed response, semantic drift, and control-plane failure
- Region, zone, provider, account, credential, certificate, and quota failure
- Clock skew, leap behavior, sequence gaps, and stale leases
- Partial deployment, schema incompatibility, bad configuration, feature-flag failure, and rollback failure
- Operator error, compromised identity, destructive automation, and observability loss
- Backup corruption, missing keys, inaccessible snapshots, and failed restoration
- AI model outage, low-confidence output, prompt injection, unsafe tool call, and runaway execution

## Retry and Overload Budget

- End-to-end deadline:
- Per-hop timeouts:
- Maximum attempts:
- Backoff and jitter:
- Retryable error classes:
- Non-retryable error classes:
- Idempotency mechanism:
- Queue capacity / retention:
- Load shedding and admission control:
- Dead-letter, quarantine, or poison-message handling:

## Recovery Procedure

1. **Detect:** exact alert, query, or signal.
2. **Classify:** severity, scope, and whether data correctness is at risk.
3. **Contain:** stop propagation, unsafe writes, retries, or automation.
4. **Fail over or degrade:** state the safe alternate behavior.
5. **Restore:** dependencies, data, configuration, and traffic.
6. **Reconcile:** duplicates, omissions, divergent state, and external side effects.
7. **Validate:** user journey, invariants, SLOs, and audit records.
8. **Return:** controlled traffic ramp and rollback trigger.
9. **Learn:** incident review, action owner, and fitness-function update.

## Chaos / Game-Day Experiment

- Hypothesis:
- Failure injected:
- Scope and safety boundary:
- Preconditions:
- Abort condition:
- Expected detection time:
- Expected automatic behavior:
- Expected operator action:
- Success criteria:
- Evidence captured:
- Result and follow-up:
