# Code, Runtime, and Assurance Decisions

Use this reference when module design, language/runtime choice, concurrency, operating-
system or network behavior, or assurance depth can change an architecture decision.
The topic coverage is informed by sections 5, 19, and 20 of the user-supplied research
manuscript; treat that manuscript as research input, not independent publication proof.

## Contents

- [1. Hide volatile decisions](#1-hide-volatile-decisions)
- [2. Preserve behavioral contracts](#2-preserve-behavioral-contracts)
- [3. Model outcomes and cancellation](#3-model-outcomes-and-cancellation)
- [4. Select languages and runtimes](#4-select-languages-and-runtimes)
- [5. Bound concurrency and resources](#5-bound-concurrency-and-resources)
- [6. Trace OS and network semantics](#6-trace-os-and-network-semantics)
- [7. Build assurance by failure model](#7-build-assurance-by-failure-model)
- [8. Decision gates](#8-decision-gates)

## 1. Hide volatile decisions

Decompose around coherent decisions likely to change, not around processing steps or
arbitrarily small files. A useful boundary exposes a truthful capability while hiding
replaceable policy or mechanism such as storage representation, provider integration,
protocol encoding, retry bookkeeping, or time and randomness.

For each boundary record:

- the decision hidden and its expected volatility;
- the stable capability and invariants exposed;
- representation, timing, error, identifier, or side-effect details that still leak;
- consumers and observed change coupling;
- the evidence or scenario that would justify splitting, merging, or removing it.

Remove duplication of stable knowledge. Similar text or control flow is not sufficient
evidence for a shared abstraction: temporary duplication may be cheaper when concepts
can diverge. Compare inconsistent-policy risk with coupling, indirection, ownership,
release coordination, and wrong-abstraction risk.

Keep deterministic policy and state transitions in a functional core where practical;
put clocks, files, networks, databases, retries, and other effects in an imperative
shell. This is a reasoning and test seam, not a requirement for pure functional code.

## 2. Preserve behavioral contracts

Compatibility is broader than schema or method signatures. For every independently
consumed interface preserve or explicitly version:

- domain meaning, invariants, and legal transitions;
- authorization and tenant scope;
- ordering, idempotency, delivery, and duplicate behavior;
- latency, deadline, cancellation, and resource expectations;
- error categories, retryability, partial completion, and unknown outcomes;
- durability, freshness, side effects, and deprecation windows.

A syntactically compatible change that alters any of these can still break consumers.
Test contracts at the layer that owns the behavior; do not let mocks become the only
evidence for a remote, persistent, or concurrent contract.

## 3. Model outcomes and cancellation

Use explicit terminal and nonterminal outcomes:

```text
accepted | rejected | completed | failed | canceled | pending | unknown
```

A timeout means the caller stopped waiting; it does not prove the remote effect failed.
For an ambiguous state-changing call, require a durable operation identity, idempotent
submission, status lookup, provider correlation, and reconciliation before retrying or
compensating. Preserve `unknown` until authoritative evidence resolves it.

Propagate an end-to-end deadline and cancellation signal through call chains. Stop work
whose result is no longer useful, release leases and resource reservations, and define
which accepted asynchronous work intentionally outlives the request. Cancellation must
not leave a half-applied invariant or erase evidence needed for recovery.

## 4. Select languages and runtimes

Choose per component risk and constraint, not fashion or a universal ranking. Compare:

| Dimension | Evidence to collect |
|---|---|
| Safety and correctness | memory/thread safety, type-level guarantees, unsafe boundary, failure consequence |
| Workload fit | CPU/I/O profile, latency tails, startup, footprint, allocation and GC behavior |
| Concurrency model | threads, async tasks, actors/channels, scheduling, cancellation, debugging |
| Ecosystem | protocol, database, security, domain libraries, maturity and supply-chain health |
| Operations | profiling, crash diagnostics, telemetry, packaging, patching, deployment and incident skills |
| Team and lifecycle | fluency, hiring, review capability, build speed, support horizon and migration cost |
| Interoperation | FFI/protocol boundary, serialization, versioning and data-copy cost |

Prototype and measure the dimensions that can reverse the choice. A public parser,
latency-critical engine, CRUD application, and data/ML orchestrator can rationally use
different languages. Add a language only when its component-level gain pays for another
toolchain, build path, dependency surface, security process, telemetry stack, staffing
need, and incident/debugging model. Record the exit path for a polyglot boundary.

## 5. Bound concurrency and resources

Lightweight tasks are not free. Every async, threaded, actor, or channel design must
bound and observe:

- admitted work, runnable tasks, queue depth and oldest age;
- worker/executor concurrency and fairness by tenant or priority;
- memory per task, buffers, payload size, connections, descriptors, and downstream pool;
- deadline, cancellation, retry attempts, retry budget, and total elapsed time;
- backpressure, rejection/shedding, degraded mode, and backlog drain rate;
- shutdown, lease handoff, orphan cleanup, and deploy/version-skew behavior.

Blocking calls can stall an async executor; shared-memory concurrency can race; task
cycles and channel waits can deadlock; unfair scheduling can starve work. Use a bounded
queue or semaphore and admission control rather than moving an unbounded queue into
process memory. Specialized lock-free techniques require measured latency benefit and
review expertise proportionate to their correctness burden.

## 6. Trace OS and network semantics

Do not reason from application APIs alone. For critical paths verify:

- file create/write/flush/sync/rename semantics and what event proves durability;
- page cache, writeback, disk-full, permission, and corruption behavior;
- memory limits, page faults, allocator/GC behavior, CPU quota and scheduler throttling;
- process lifecycle, signals, draining, sockets, ports and descriptor exhaustion;
- DNS lookup/cache/TTL, TLS and certificate path, proxies/load balancers, NAT and routing;
- handshake, connection reuse/drain, payload buffering, transport head-of-line effects;
- aligned client/proxy/server deadlines and retries at every layer.

Trace the real path from client rendering through DNS, transport, edge, service, cache,
datastore and response. A successful file API call is not automatically durable, and a
healthy process may still be throttled, deadlocked, resource-exhausted, or isolated from
dependencies.

## 7. Build assurance by failure model

Select complementary evidence; test count alone is not confidence.

| Failure model or claim | Proportionate assurance |
|---|---|
| Deterministic policy and invariants | focused unit/component tests; property tests over state transitions |
| Database, broker, file, runtime or provider semantics | integration tests with the real dependency or representative substitute |
| Independently evolving interfaces | producer/consumer contract and version-skew tests plus semantic journey tests |
| Critical user journey | small end-to-end set, synthetic probes, canary/invariant monitoring |
| Parsers, serializers and hostile inputs | fuzzing, corpus regression, sanitizers and resource-limit tests |
| Races, actors, retries and schedules | deterministic/systematic concurrency tests and fault injection |
| Test-suite fault sensitivity | selective mutation testing on critical logic; inspect equivalent mutants |
| Protocol/state-space subtlety | model checking or lightweight formal specification under explicit assumptions |
| Scale, latency and leaks | workload-shaped load, spike, soak, profiling and production telemetry |
| Recovery claim | replay, reconciliation, restore, failover and operator drills |

Formal methods prove stated properties of a model under assumptions. They do not by
themselves prove implementation conformance, compiler/runtime/OS behavior, deployment
configuration, external dependencies, operational execution, or that the modeled
property was the right one. Link each model property to implementation tests, runtime
invariants, versioned assumptions, and a responsible reviewer. Increase rigor when
failure impact, concurrency subtlety, state-space size, and reproduction cost justify it.

## 8. Decision gates

- Reject a language choice with no component risk, workload, team, ecosystem,
  operability, measurement, and migration evidence.
- Reject an abstraction that unifies only surface similarity while forcing unrelated
  policy or release changes.
- Treat unknown remote outcomes, unbounded tasks/queues/retries/connections, and missing
  cancellation semantics as blockers.
- Reject claims that schema compatibility proves behavioral compatibility.
- Reject claims that a formal model proves the deployed implementation correct.
- Require an assurance portfolio mapped to the actual failure model; do not substitute
  test volume, coverage, or one end-to-end suite for distinct evidence.
