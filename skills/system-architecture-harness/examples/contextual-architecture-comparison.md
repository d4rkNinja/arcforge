# Contextual Architecture Comparison

> Calibration example only. These fictional cases demonstrate that one decision
> framework should yield different architectures under different requirements. They
> are not benchmarks, universal reference designs, or empirical evidence.

Apply the normal workflow, the
[`Complexity Ledger`](../assets/complexity-ledger-template.md),
[`code/runtime assurance`](../references/16-code-runtime-and-assurance.md),
[`client architecture`](../references/17-client-platform-architecture.md), and
[`platform/evolution`](../references/18-platform-governance-and-evolution.md)
references. Keep every recommendation conditional.

## Case 1 — Small regional SaaS

### Context

- Five engineers need fast product learning and simple on-call.
- Ordinary tenant-scoped business transactions run in one region.
- Peak load and geography do not require partitioned state or independent scaling.
- Files and slow notifications are secondary to the transactional journey.

### Result

Use a capability-oriented modular monolith, one relational source of truth, object
storage for files, and a transactional outbox plus bounded worker for notifications.
Enforce tenant authorization in data access, test backup restore, and optimize local/CI
feedback. Use server rendering or client rendering per route based on measured user
needs; do not add an offline authority model unless the product requires offline work.

### Why this shape

One transaction boundary preserves ordinary invariants with fewer runtime, protocol,
and on-call obligations. Services, a multi-region write topology, multiple languages,
and a generalized internal platform do not yet buy a named requirement.

### Reversal evidence

Extract only when a module shows durable independent ownership, deploy cadence,
compliance, fault isolation, or measured scaling needs. Revisit topology when region,
recovery, tenant-size, or change-coupling evidence crosses an approved threshold.

## Case 2 — High-integrity payment worker

### Context

- Duplicate charges and unverifiable outcomes are unacceptable.
- A remote processor can time out after accepting a request.
- Durable audit, reconciliation, controlled concurrency, and specialist review are
  funded; availability must not silently violate financial invariants.

### Result

Use a ledger-oriented relational authority with exact arithmetic, unique durable
operation identities, an explicit payment state machine including `pending` and
`unknown`, provider status lookup, signed callback ingestion, transactional outbox,
idempotent effects, and reconciliation. Bound queues, tasks, connections, retries and
deadlines; propagate cancellation without discarding accepted work or audit evidence.

Choose the implementation language only after comparing memory/thread safety, workload
and latency, runtime behavior, processor ecosystem, team review skill, incident tooling,
build/support lifecycle, and measured prototype results. Do not select Rust—or reject
it—because of fashion.

### Proportionate assurance

Use property tests for money/state invariants, integration and version-skew tests for
the datastore and processor adapter, fuzzing for parsers/webhooks, systematic concurrency
tests for duplicate/timeout races, selective model checking for the protocol state
machine, load/soak tests for bounds, runtime invariant monitoring, and reconciliation/
restore drills. A formal model supports properties under declared assumptions; it does
not prove deployed implementation, environment, or operations automatically.

### Reversal evidence

Change the language, protocol, or service boundary when measured safety, latency,
operability, dependency, team, or lifecycle evidence outweighs migration risk—not when
a new stack becomes popular.

## Case 3 — Offline collaborative field client

### Context

- Field workers must create and edit jobs through long disconnections.
- Several devices may edit the same record, attachments can exceed local quotas, and
  permissions or device trust can change while a client is offline.
- Users need explicit conflicts rather than silent loss of safety-relevant edits.

### Result

Treat mobile clients as stateful system components. Use encrypted durable local storage
with versioned schema migrations, a local operation log with stable identities and
pending/acknowledged/rejected/conflicted states, and a server authority for permissions
and shared job truth. Synchronize by cursor/version using snapshot plus bounded deltas;
detect gaps and trigger a resumable full resync. Apply idempotently, reauthorize queued
operations, and reconcile after partial transfer.

Define merge rules per field or operation. Commutative low-risk edits may merge
automatically; safety, assignment, approval, and deletion conflicts require domain rules
and sometimes human resolution. CRDTs are candidates only where their merge behavior
matches those rules. Last-write-wins is not a default.

Handle partial datasets, attachment quotas, background limits, battery/network cost,
encryption/key recovery, backup, session expiry, device revocation, remote wipe limits,
data deletion, and skipped-version upgrades. Bound sync batches, concurrency, buffers,
retries and backpressure; show degraded offline, conflict, and recovery states accessibly.

### Reversal evidence

Simplify toward server-first caching only if validated product requirements no longer
include durable offline mutation or collaboration. Add peer/local-first authority only
if latency, autonomy, privacy, or availability needs justify its conflict, security,
backup, and recovery obligations.

## Comparison

| Decision pressure | Small SaaS | Payment worker | Offline collaborative client |
|---|---|---|---|
| Primary invariant | tenant-scoped transaction integrity | no duplicate value movement; auditable resolution | no silent loss; authorized convergent shared work |
| State authority | server relational store | ledger and payment state machine | explicit local operations plus server/shared authority |
| Distribution bought | asynchronous side effects only | remote processor integration and durable workflow | device/cloud synchronization and reconnect lifecycle |
| Assurance emphasis | component, authorization, migration and restore | property, concurrency, formal model, reconciliation and runtime evidence | sync-state, conflict, schema-upgrade, revocation and impaired-network tests |
| Main complexity avoided | premature services/platform | fashion-led runtime and unbounded async work | backend-only caching and automatic-merge assumptions |

The mechanism count is not the conclusion. Each architecture follows from its own
invariants, failure consequences, client authority, operating capacity, and validation
evidence. If those inputs change, revise the ledger and ADR rather than preserving the
example's topology.
