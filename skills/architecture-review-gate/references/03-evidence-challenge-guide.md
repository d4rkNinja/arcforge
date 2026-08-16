# Evidence and Challenge Guide

## Claim-Centric Evidence Record

Treat the unit of review as an atomic claim, not a bookmark or document. For every material external claim, record:

| Field | Required content |
|---|---|
| Claim ID and claim | One proposition the source directly supports |
| Source ID and stable citation | DOI, standard number, durable URL, or versioned artifact |
| Provenance | title, authors, year, and organization |
| Source type | theory, experiment, system paper, standard, incident, book, case study, vendor documentation, or local artifact |
| Study design | proof, controlled experiment, survey, observation, benchmark, case report, or engineering record |
| Scale and context | sample/system size, workload, organization, technology, and preconditions |
| Evidence | data, proof, trace, test, configuration, or argument supplied |
| Counter-evidence | contradictory sources, observations, or failed replication |
| Threats to validity | selection, confounding, measurement, publication, recency, and scale limits |
| Confidence | high, medium, low, or contested, with reason |
| Architecture implication | reviewer interpretation kept separate from the source claim |

Never turn a source's correlation into causation, local result into universal rule, or vendor capability into configured runtime behavior. Quote and paraphrase accurately within applicable copyright limits.

## Evidence Hierarchy

Prefer stronger evidence when available:

1. reproducible tests, measurements, traces, restore/failover results;
2. deployed configuration, schemas, contracts, policy, and code paths;
3. versioned architecture decisions and runbooks aligned with implementation;
4. incident reports and operational records;
5. owner statement or vendor documentation;
6. reviewer inference;
7. unsupported assertion.

Label the evidence class in material findings.

Evidence rank does not erase relevance or validity limits. A reproducible benchmark on an unlike workload may be weaker for the decision than a directly relevant incident record.

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
- **Source claim versus reviewer inference**
- **Counter-evidence and validity limits**

## Avoid false precision

Use ranges and confidence when evidence is incomplete. A quantified estimate with explicit assumptions is better than a precise number with hidden assumptions. Do not convert missing evidence into a factual defect; report the gap and why it matters.

## Closure evidence

A finding closes only when fresh evidence demonstrates the required postcondition. A code diff, agent report, or design promise is insufficient when the finding concerns runtime behavior, recovery, concurrency, migration, security, or performance.

## Source Challenge Sequence

For each consequential claim:

1. Restate the smallest claim actually supported.
2. Classify source type and study design.
3. Check sample/system scale and whether the reviewed context matches.
4. Search supplied material for counter-evidence and disagreements.
5. Name threats to validity and missing replication.
6. Separate the source claim from the reviewer's architecture implication.
7. Assign confidence and the next evidence that could change it.
8. Preserve a stable citation and artifact version so the challenge is reproducible.
