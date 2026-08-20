# Production-Grade Backend Engineering Knowledge Base

**Corpus version:** 1.1.0
**Generated / verified through:** 2026-08-20
**Papers:** 147
**Canonical subtopics covered:** 1901
**Approximate paper word count:** 938,492

This repository is designed as implementation intelligence for AI coding agents and experienced backend engineers. Each numbered topic from the canonical attachment is a separate research paper. The corpus emphasizes hidden correctness requirements, security boundaries, concurrency, failure recovery, compatibility, migration, observability, and operational evidence rather than framework syntax.

## Repository layout

```text
backend-engineering-knowledge-base/
├── README.md
├── ONTOLOGY.md
├── RESEARCH-METHOD.md
├── SOURCES.md
├── manifest.json
├── knowledge-graph.json
├── checksums.sha256
├── rules/
│   ├── critical-rules.schema.json
│   ├── critical-rules.json
│   ├── exceptions.schema.json
│   └── exceptions.json
├── original/
│   └── Pasted text.txt
└── papers/
    ├── primitives/
    ├── systems/
    └── cross-cutting/
```

## How to use this corpus before changing code

1. Open the requested feature/system paper.
2. Read **Questions that must be answered before implementation** and **Existing-codebase checks** before editing.
3. Follow the linked knowledge-graph papers for reusable primitives and cross-cutting constraints.
4. Turn the paper's MUST/SHOULD/AVOID/NEVER statements into design decisions, tests, migration gates, and review criteria.
5. Recheck living standards and provider documentation at implementation time; the corpus records its verification date and source versions.

## Three-layer ontology

| Layer | Meaning | Count |
|---|---|---:|
| `primitives` | Reusable reasoning units such as identifiers, time, validation, consistency, transactions, idempotency, and schema evolution. | 40 |
| `systems` | Subsystems with lifecycle and ownership: identity, authentication, authorization, APIs, storage, queues, files, clients, and AI execution. | 54 |
| `cross-cutting` | Security, reliability, observability, performance, deployment, testing, operations, recovery, migration, and version-control controls that span systems. | 53 |

See [ONTOLOGY.md](ONTOLOGY.md) for classification rules and graph semantics.

## Complete paper index

### Primitives

Reusable reasoning units such as identifiers, time, validation, consistency, transactions, idempotency, and schema evolution.

| No. | Paper | Domain profile | Subtopics | Words |
|---:|---|---|---:|---:|
| 011 | [Request Lifecycle](papers/primitives/011-request-lifecycle.md) | `api` | 16 | 6,545 |
| 012 | [Input Validation](papers/primitives/012-input-validation.md) | `api` | 22 | 6,959 |
| 013 | [Error Architecture](papers/primitives/013-error-architecture.md) | `api` | 20 | 7,062 |
| 016 | [Pagination](papers/primitives/016-pagination.md) | `api` | 15 | 6,420 |
| 017 | [Filtering / Sorting / Query APIs](papers/primitives/017-filtering-sorting-query-apis.md) | `api` | 14 | 6,129 |
| 018 | [Identifiers](papers/primitives/018-identifiers.md) | `data_model` | 15 | 6,674 |
| 019 | [Time & Date Handling](papers/primitives/019-time-and-date-handling.md) | `data_model` | 17 | 6,961 |
| 020 | [Money / Numeric Precision](papers/primitives/020-money-numeric-precision.md) | `data_model` | 13 | 6,612 |
| 022 | [Database Constraints](papers/primitives/022-database-constraints.md) | `data_model` | 13 | 5,978 |
| 023 | [Database Transactions](papers/primitives/023-database-transactions.md) | `transactions` | 18 | 6,735 |
| 024 | [Concurrency Anomalies](papers/primitives/024-concurrency-anomalies.md) | `transactions` | 11 | 6,006 |
| 025 | [Concurrency Control](papers/primitives/025-concurrency-control.md) | `transactions` | 13 | 6,270 |
| 026 | [Data Integrity](papers/primitives/026-data-integrity.md) | `data_model` | 13 | 6,365 |
| 029 | [Schema Evolution](papers/primitives/029-schema-evolution.md) | `migration` | 12 | 6,016 |
| 031 | [Data Migrations & Backfills](papers/primitives/031-data-migrations-and-backfills.md) | `migration` | 12 | 6,270 |
| 032 | [Soft Delete / Hard Delete](papers/primitives/032-soft-delete-hard-delete.md) | `data_model` | 11 | 5,940 |
| 033 | [Data Lifecycle](papers/primitives/033-data-lifecycle.md) | `data_model` | 11 | 6,064 |
| 034 | [Immutable Data](papers/primitives/034-immutable-data.md) | `data_model` | 9 | 5,958 |
| 035 | [State Machines](papers/primitives/035-state-machines.md) | `transactions` | 12 | 6,328 |
| 036 | [Idempotency](papers/primitives/036-idempotency.md) | `transactions` | 14 | 6,500 |
| 039 | [Quotas](papers/primitives/039-quotas.md) | `cache` | 12 | 5,688 |
| 052 | [Retry Engineering](papers/primitives/052-retry-engineering.md) | `resilience` | 11 | 5,863 |
| 053 | [Timeout Engineering](papers/primitives/053-timeout-engineering.md) | `resilience` | 11 | 5,703 |
| 054 | [Circuit Breakers](papers/primitives/054-circuit-breakers.md) | `resilience` | 10 | 6,106 |
| 069 | [Data Versioning](papers/primitives/069-data-versioning.md) | `data_model` | 8 | 5,966 |
| 070 | [API / Event Schema Evolution](papers/primitives/070-api-event-schema-evolution.md) | `migration` | 11 | 6,083 |
| 071 | [Backward Compatibility](papers/primitives/071-backward-compatibility.md) | `migration` | 10 | 6,112 |
| 072 | [Data Synchronization](papers/primitives/072-data-synchronization.md) | `migration` | 13 | 6,492 |
| 073 | [Change Data Capture](papers/primitives/073-change-data-capture.md) | `migration` | 11 | 6,227 |
| 116 | [Data Serialization](papers/primitives/116-data-serialization.md) | `api` | 11 | 6,408 |
| 117 | [Compression](papers/primitives/117-compression.md) | `performance` | 8 | 5,632 |
| 118 | [Batch Processing](papers/primitives/118-batch-processing.md) | `async` | 11 | 6,026 |
| 119 | [Bulk Operations](papers/primitives/119-bulk-operations.md) | `async` | 10 | 6,231 |
| 120 | [Deduplication](papers/primitives/120-deduplication.md) | `async` | 10 | 6,107 |
| 121 | [Ordering Guarantees](papers/primitives/121-ordering-guarantees.md) | `transactions` | 9 | 5,569 |
| 122 | [Data Provenance](papers/primitives/122-data-provenance.md) | `data_model` | 9 | 5,954 |
| 123 | [Source of Truth](papers/primitives/123-source-of-truth.md) | `data_model` | 9 | 6,011 |
| 124 | [Data Reconciliation](papers/primitives/124-data-reconciliation.md) | `data_ops` | 9 | 6,119 |
| 126 | [Temporary Data](papers/primitives/126-temporary-data.md) | `security` | 10 | 5,997 |
| 127 | [Randomness & Token Generation](papers/primitives/127-randomness-and-token-generation.md) | `security` | 10 | 6,192 |

### Systems

Subsystems with lifecycle and ownership: identity, authentication, authorization, APIs, storage, queues, files, clients, and AI execution.

| No. | Paper | Domain profile | Subtopics | Words |
|---:|---|---|---:|---:|
| 001 | [Project & Runtime Foundations](papers/systems/001-project-and-runtime-foundations.md) | `runtime` | 19 | 7,096 |
| 002 | [Configuration Management](papers/systems/002-configuration-management.md) | `runtime` | 16 | 6,950 |
| 003 | [Identity](papers/systems/003-identity.md) | `identity` | 15 | 6,859 |
| 004 | [Authentication](papers/systems/004-authentication.md) | `authentication` | 35 | 8,533 |
| 005 | [OAuth / Social Authentication](papers/systems/005-oauth-social-authentication.md) | `authentication` | 22 | 7,420 |
| 006 | [MFA / Strong Authentication](papers/systems/006-mfa-strong-authentication.md) | `authentication` | 16 | 6,864 |
| 007 | [Sessions](papers/systems/007-sessions.md) | `authentication` | 17 | 6,971 |
| 008 | [Authorization](papers/systems/008-authorization.md) | `authorization` | 23 | 7,102 |
| 009 | [Users & Account Lifecycle](papers/systems/009-users-and-account-lifecycle.md) | `identity` | 20 | 7,304 |
| 010 | [Multi-Tenancy](papers/systems/010-multi-tenancy.md) | `authorization` | 23 | 7,133 |
| 014 | [API Design](papers/systems/014-api-design.md) | `api` | 20 | 7,269 |
| 015 | [API Versioning & Compatibility](papers/systems/015-api-versioning-and-compatibility.md) | `api` | 13 | 6,641 |
| 021 | [Database Modeling](papers/systems/021-database-modeling.md) | `data_model` | 17 | 6,749 |
| 027 | [Indexing](papers/systems/027-indexing.md) | `data_model` | 15 | 6,089 |
| 028 | [Query Design](papers/systems/028-query-design.md) | `data_model` | 14 | 6,267 |
| 037 | [Caching](papers/systems/037-caching.md) | `cache` | 20 | 6,905 |
| 040 | [File Handling](papers/systems/040-file-handling.md) | `data_model` | 23 | 7,121 |
| 041 | [Media Processing](papers/systems/041-media-processing.md) | `data_model` | 12 | 5,980 |
| 042 | [Search](papers/systems/042-search.md) | `data_model` | 17 | 6,752 |
| 043 | [Background Jobs](papers/systems/043-background-jobs.md) | `async` | 18 | 6,836 |
| 044 | [Scheduled Jobs](papers/systems/044-scheduled-jobs.md) | `async` | 11 | 6,265 |
| 045 | [Messaging / Queues](papers/systems/045-messaging-queues.md) | `async` | 19 | 6,877 |
| 046 | [Event Systems](papers/systems/046-event-systems.md) | `async` | 15 | 6,680 |
| 047 | [Transactional Outbox / Inbox](papers/systems/047-transactional-outbox-inbox.md) | `async` | 11 | 6,152 |
| 048 | [Distributed Transactions](papers/systems/048-distributed-transactions.md) | `transactions` | 11 | 6,516 |
| 049 | [Webhooks](papers/systems/049-webhooks.md) | `api` | 17 | 6,591 |
| 050 | [Realtime Communication](papers/systems/050-realtime-communication.md) | `api` | 18 | 6,966 |
| 051 | [External Integrations](papers/systems/051-external-integrations.md) | `resilience` | 16 | 6,572 |
| 079 | [Connection Management](papers/systems/079-connection-management.md) | `runtime` | 11 | 6,169 |
| 080 | [Networking Basics for Backend](papers/systems/080-networking-basics-for-backend.md) | `runtime` | 15 | 6,722 |
| 081 | [Load Balancing](papers/systems/081-load-balancing.md) | `runtime` | 10 | 6,289 |
| 082 | [Service Discovery](papers/systems/082-service-discovery.md) | `runtime` | 8 | 6,017 |
| 083 | [Service-to-Service Communication](papers/systems/083-service-to-service-communication.md) | `runtime` | 13 | 6,577 |
| 084 | [Modular Monolith Architecture](papers/systems/084-modular-monolith-architecture.md) | `architecture` | 9 | 5,984 |
| 085 | [Microservice Architecture](papers/systems/085-microservice-architecture.md) | `architecture` | 12 | 6,370 |
| 086 | [Dependency Boundaries](papers/systems/086-dependency-boundaries.md) | `architecture` | 10 | 6,057 |
| 087 | [Code-Level Architecture](papers/systems/087-code-level-architecture.md) | `architecture` | 17 | 6,724 |
| 088 | [Abstraction Design](papers/systems/088-abstraction-design.md) | `architecture` | 10 | 6,217 |
| 110 | [SDK / Client Design](papers/systems/110-sdk-client-design.md) | `client` | 13 | 6,281 |
| 111 | [CLI Backend Interaction](papers/systems/111-cli-backend-interaction.md) | `client` | 11 | 6,228 |
| 112 | [Internal Admin Operations](papers/systems/112-internal-admin-operations.md) | `authorization` | 9 | 5,857 |
| 113 | [Machine-to-Machine Authentication](papers/systems/113-machine-to-machine-authentication.md) | `authentication` | 11 | 6,532 |
| 114 | [API Keys](papers/systems/114-api-keys.md) | `authentication` | 13 | 6,733 |
| 115 | [Web Security Headers](papers/systems/115-web-security-headers.md) | `api` | 8 | 5,968 |
| 128 | [Email Delivery Infrastructure](papers/systems/128-email-delivery-infrastructure.md) | `async` | 13 | 6,550 |
| 129 | [Notification Infrastructure](papers/systems/129-notification-infrastructure.md) | `async` | 12 | 6,399 |
| 130 | [Search Index Synchronization](papers/systems/130-search-index-synchronization.md) | `migration` | 10 | 5,976 |
| 136 | [Legacy-System Integration](papers/systems/136-legacy-system-integration.md) | `migration` | 8 | 6,000 |
| 140 | [AI/LLM Backend Fundamentals](papers/systems/140-ai-llm-backend-fundamentals.md) | `ai` | 15 | 6,326 |
| 141 | [Agent Execution](papers/systems/141-agent-execution.md) | `ai` | 14 | 6,236 |
| 142 | [AI Memory](papers/systems/142-ai-memory.md) | `ai` | 12 | 5,992 |
| 143 | [RAG Infrastructure](papers/systems/143-rag-infrastructure.md) | `ai` | 14 | 6,407 |
| 144 | [Untrusted Code Execution](papers/systems/144-untrusted-code-execution.md) | `ai` | 12 | 6,070 |
| 145 | [Plugin / Extension Architecture](papers/systems/145-plugin-extension-architecture.md) | `ai` | 11 | 6,094 |

### Cross Cutting

Security, reliability, observability, performance, deployment, testing, operations, recovery, and migration controls that span systems.

| No. | Paper | Domain profile | Subtopics | Words |
|---:|---|---|---:|---:|
| 030 | [Database Migrations](papers/cross-cutting/030-database-migrations.md) | `migration` | 11 | 6,196 |
| 038 | [Rate Limiting](papers/cross-cutting/038-rate-limiting.md) | `cache` | 15 | 6,486 |
| 055 | [Resilience](papers/cross-cutting/055-resilience.md) | `resilience` | 12 | 5,990 |
| 056 | [Logging](papers/cross-cutting/056-logging.md) | `observability` | 13 | 6,091 |
| 057 | [Metrics](papers/cross-cutting/057-metrics.md) | `observability` | 13 | 6,106 |
| 058 | [Distributed Tracing](papers/cross-cutting/058-distributed-tracing.md) | `observability` | 11 | 5,703 |
| 059 | [Health Checks](papers/cross-cutting/059-health-checks.md) | `observability` | 10 | 6,063 |
| 060 | [Audit Logging](papers/cross-cutting/060-audit-logging.md) | `observability` | 14 | 6,178 |
| 061 | [Security Fundamentals](papers/cross-cutting/061-security-fundamentals.md) | `security` | 11 | 6,335 |
| 062 | [Web/API Security](papers/cross-cutting/062-web-api-security.md) | `security` | 16 | 6,888 |
| 063 | [Secrets Management](papers/cross-cutting/063-secrets-management.md) | `security` | 12 | 6,069 |
| 064 | [Cryptography](papers/cross-cutting/064-cryptography.md) | `security` | 15 | 6,315 |
| 065 | [TLS / PKI](papers/cross-cutting/065-tls-pki.md) | `security` | 11 | 6,373 |
| 066 | [Privacy & Sensitive Data](papers/cross-cutting/066-privacy-and-sensitive-data.md) | `security` | 13 | 6,403 |
| 067 | [Abuse Protection](papers/cross-cutting/067-abuse-protection.md) | `security` | 13 | 6,192 |
| 068 | [Feature Flags](papers/cross-cutting/068-feature-flags.md) | `security` | 11 | 6,092 |
| 074 | [Data Import](papers/cross-cutting/074-data-import.md) | `backup_dr` | 14 | 6,310 |
| 075 | [Data Export](papers/cross-cutting/075-data-export.md) | `backup_dr` | 10 | 6,030 |
| 076 | [Backup](papers/cross-cutting/076-backup.md) | `backup_dr` | 10 | 5,935 |
| 077 | [Restore](papers/cross-cutting/077-restore.md) | `backup_dr` | 9 | 5,790 |
| 078 | [Disaster Recovery](papers/cross-cutting/078-disaster-recovery.md) | `backup_dr` | 11 | 5,828 |
| 089 | [Dependency Management](papers/cross-cutting/089-dependency-management.md) | `architecture` | 11 | 6,311 |
| 090 | [Testing Foundations](papers/cross-cutting/090-testing-foundations.md) | `testing` | 12 | 6,271 |
| 091 | [Test Data](papers/cross-cutting/091-test-data.md) | `testing` | 11 | 6,120 |
| 092 | [Concurrency Testing](papers/cross-cutting/092-concurrency-testing.md) | `testing` | 8 | 5,482 |
| 093 | [Failure Testing](papers/cross-cutting/093-failure-testing.md) | `testing` | 12 | 6,252 |
| 094 | [Load & Performance Testing](papers/cross-cutting/094-load-and-performance-testing.md) | `testing` | 10 | 5,827 |
| 095 | [Performance Engineering](papers/cross-cutting/095-performance-engineering.md) | `performance` | 14 | 6,168 |
| 096 | [Scalability](papers/cross-cutting/096-scalability.md) | `performance` | 13 | 6,210 |
| 097 | [High Availability](papers/cross-cutting/097-high-availability.md) | `backup_dr` | 10 | 6,066 |
| 098 | [Distributed Systems Fundamentals](papers/cross-cutting/098-distributed-systems-fundamentals.md) | `transactions` | 13 | 6,468 |
| 099 | [Consistency Models](papers/cross-cutting/099-consistency-models.md) | `transactions` | 9 | 6,296 |
| 100 | [Replication](papers/cross-cutting/100-replication.md) | `transactions` | 9 | 5,778 |
| 101 | [Partitioning / Sharding](papers/cross-cutting/101-partitioning-sharding.md) | `transactions` | 10 | 5,834 |
| 102 | [Distributed Consensus](papers/cross-cutting/102-distributed-consensus.md) | `transactions` | 9 | 5,973 |
| 103 | [Distributed Locks](papers/cross-cutting/103-distributed-locks.md) | `transactions` | 10 | 6,389 |
| 104 | [Backpressure](papers/cross-cutting/104-backpressure.md) | `resilience` | 9 | 5,963 |
| 105 | [Graceful Shutdown](papers/cross-cutting/105-graceful-shutdown.md) | `runtime` | 9 | 6,183 |
| 106 | [Deployment Safety](papers/cross-cutting/106-deployment-safety.md) | `runtime` | 10 | 6,244 |
| 107 | [CI/CD](papers/cross-cutting/107-ci-cd.md) | `runtime` | 12 | 6,531 |
| 108 | [Infrastructure Configuration](papers/cross-cutting/108-infrastructure-configuration.md) | `runtime` | 10 | 6,287 |
| 109 | [Resource Management](papers/cross-cutting/109-resource-management.md) | `performance` | 12 | 6,274 |
| 125 | [Cleanup Jobs](papers/cross-cutting/125-cleanup-jobs.md) | `data_ops` | 10 | 6,116 |
| 131 | [Distributed Cache Coordination](papers/cross-cutting/131-distributed-cache-coordination.md) | `cache` | 7 | 5,900 |
| 132 | [Multi-Region Systems](papers/cross-cutting/132-multi-region-systems.md) | `backup_dr` | 11 | 6,152 |
| 133 | [Data Residency](papers/cross-cutting/133-data-residency.md) | `backup_dr` | 7 | 5,681 |
| 134 | [Zero-Downtime Changes](papers/cross-cutting/134-zero-downtime-changes.md) | `migration` | 10 | 6,040 |
| 135 | [Feature Migration](papers/cross-cutting/135-feature-migration.md) | `migration` | 10 | 6,045 |
| 137 | [Observability for Async Systems](papers/cross-cutting/137-observability-for-async-systems.md) | `observability` | 9 | 6,110 |
| 138 | [Operational Runbooks](papers/cross-cutting/138-operational-runbooks.md) | `observability` | 9 | 5,984 |
| 139 | [Incident Readiness](papers/cross-cutting/139-incident-readiness.md) | `observability` | 10 | 5,858 |
| 146 | [Cross-Cutting Implementation Checklist](papers/cross-cutting/146-cross-cutting-implementation-checklist.md) | `checklist` | 42 | 9,046 |
| 147 | [Production-Grade Git and Git Flow](papers/cross-cutting/147-production-grade-git-and-git-flow.md) | `version_control` | 20 | 14,747 |

## Distribution into portable skills

The canonical corpus stays in this directory. Portable, self-contained copies
are committed under each owning skill's `references/papers/` directory. The root
`../arcforge.catalog.yaml` records ownership (identity/auth maps to
`auth-access`, transactions to `transactions-consistency`, Git workflow and
release controls to `git-workflows`, papers 084–089 enrich
`system-architecture-harness`, and 140–145 enrich
`ai-agent-system-architecture`). Each portable copy:

- strips corpus bookkeeping (frontmatter, the canonical scope map, the scope note, the metadata footer);
- removes the template boilerplate the generator repeated across the invariants, subtopic, normative, bugs, questions, testing, and codebase-check sections, keeping the first occurrence of every distinct statement;
- collapses subtopics whose entire entry is the generic template into one "Default obligations" list that keeps every subtopic name visible;
- moves "Questions that must be answered before implementation" and "Existing-codebase checks" directly after the executive summary so a linear read reaches them first;
- renumbers sections, keeps same-skill links relative, and converts cross-skill links into explicit skill pointers.

The copies are roughly 30% smaller per paper while preserving domain-specific
rules, failure modes, questions, and sources. When a canonical paper changes,
update every owning portable copy in the same review and compare their meaning,
links, headings, and source coverage manually.

## Structured critical rules

`rules/critical-rules.json` is the machine-checkable registry for the small set
of obligations that require stable traceability. The papers remain canonical
for explanation, trade-offs, examples, and contextual guidance. Each structured
rule must remain anchored to its owner paper and declares applicability,
exception policy, evidence, source IDs, and evaluation criterion IDs.

`rules/exceptions.json` is the exception ledger. Exceptions are allowed only
where the rule declares `structured` handling and must carry scope, owner,
evidence, compensating controls, non-model approval, expiry, and review state.
The seed ledger is intentionally empty. See [rules/README.md](rules/README.md)
for field ownership and migration rules.

## Manual integrity review

Review paper count, manifest paths and aggregate counts, SHA-256 entries,
canonical topic titles and subtopics, knowledge-graph targets, source IDs,
structured critical-rule anchors, evaluation criteria, local links, and empty
files. `checksums.sha256` intentionally covers an explicit reviewed set; update
or remove an entry only with the corresponding source change.

## Source policy

The papers prioritize specifications, RFCs, official platform/database/security documentation, academic papers, respected engineering books, and production engineering guidance. [SOURCES.md](SOURCES.md) is the global catalog; every paper also carries a scoped bibliography.

## Important limitations

- This is a production-oriented reference, not a substitute for inspecting the real codebase, deployed configuration, provider contract, database version, and incidents.
- Standards and provider behavior continue to evolve after the verification date.
- The ontology classification is editorial: a topic can participate in multiple layers through graph relationships even though it has one primary filesystem location.
- Regulatory obligations depend on jurisdiction and organization; papers identify engineering concerns but do not provide legal advice.
