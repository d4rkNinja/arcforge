# Security, Privacy, Abuse, and Compliance

Security architecture protects assets and user outcomes against mistakes, malicious actors, compromised identities, unsafe dependencies, and misuse. It is a system property, not a perimeter appliance.

## Contents

- 1. Security Design Sequence
- 2. Data Classification
- 3. Threat Modeling
- 4. Identity and Authentication
- 5. Authorization
- 6. Zero-Trust Principles
- 7. Tenant Isolation
- 8. Secrets and Key Management
- 9. Encryption and Data Protection
- 10. API and Input Security
- 11. Abuse and Fraud Architecture
- 12. Logging and Audit
- 13. Supply-Chain Security
- 14. Privacy by Design
- 15. Compliance Handoff
- 16. Security Operations and Incident Response
- 17. Security Verification
- 18. Critical Security Gates
- 19. Common Mistakes

## 1. Security Design Sequence

1. Identify assets, users, administrators, services, tenants, vendors, and adversaries.
2. Classify data and map lifecycle.
3. Draw trust boundaries and privileged flows.
4. Define security and privacy requirements.
5. Enumerate threats, abuse cases, fraud, and failure-assisted attacks.
6. Select preventive, detective, responsive, and recovery controls.
7. Assign owners and evidence.
8. Test and monitor continuously.

Use `assets/threat-model-template.md`.

## 2. Data Classification

Example classes:

- public;
- internal;
- confidential business data;
- personal data;
- sensitive personal/health/financial data;
- credentials/secrets/cryptographic keys;
- regulated or legally held data.

For each class specify:

- allowed purpose and collection minimization;
- authorized roles/services;
- tenant and residency boundary;
- encryption/tokenization/redaction;
- logging/telemetry rules;
- retention, deletion, export, and backup behavior;
- audit and breach impact;
- third-party processors.

## 3. Threat Modeling

A practical STRIDE-like pass:

- **Spoofing:** fake user/service/device/provider.
- **Tampering:** unauthorized state, message, model, artifact, or configuration changes.
- **Repudiation:** inability to prove who did what.
- **Information disclosure:** data leakage through APIs, logs, caches, backups, prompts, side channels.
- **Denial of service:** resource exhaustion, algorithmic abuse, quota drain, cost attacks.
- **Elevation of privilege:** broken authorization, tenant escape, unsafe admin/tool capability.

Also model:

- business abuse and fraud;
- supply-chain compromise;
- insider and support/admin misuse;
- dependency/webhook impersonation;
- race/replay/duplicate attacks;
- data poisoning and prompt injection for AI systems;
- recovery system and backup compromise.

Write threats as scenarios with asset, attacker, precondition, path, impact, controls, residual risk, and validation.

## 4. Identity and Authentication

Define distinct identities for:

- humans;
- workloads/services;
- devices;
- tenants/organizations;
- third-party integrations;
- automation and agents.

Controls:

- phishing-resistant MFA for privileged access where feasible;
- short-lived credentials/tokens;
- audience, issuer, expiry, nonce/state, and signature validation;
- session revocation and risk-based reauthentication;
- service/workload identity rather than shared static secrets;
- device posture only where justified;
- secure account recovery;
- no credentials in URLs/logs/code.

Authentication proves identity. It does not grant resource access.

## 5. Authorization

Enforce server-side at every entry and sensitive state transition.

Model:

- roles and permissions;
- object/resource ownership;
- tenant scope;
- attributes/context (ABAC) where needed;
- separation of duties and approval;
- delegated access and expiry;
- admin/support impersonation safeguards;
- deny-by-default behavior;
- policy versioning and audit.

### Required authorization checks

- object-level: may this subject access this exact object?
- function-level: may this subject invoke this capability?
- property-level: may this subject read/write these fields?
- workflow-level: is this transition legal and approved?
- data-query-level: can filters or joins bypass tenant/row isolation?

Do not rely on hidden UI buttons, unguessable IDs, or gateway-only authorization.

## 6. Zero-Trust Principles

- no implicit trust from network location or ownership;
- authenticate and authorize each access based on identity and context;
- protect resources, not only network segments;
- least privilege and short-lived access;
- continuous policy evaluation/telemetry where risk requires;
- explicit service identity and encrypted transport;
- assume breach and limit blast radius;
- separate control, data, and administration planes.

Network segmentation remains useful containment, but it is not identity or authorization.

## 7. Tenant Isolation

Carry trusted tenant context end-to-end. Verify it cannot be overridden by user payload.

Enforce in:

- authorization policy;
- database row/schema/database boundary;
- cache keys and eviction;
- object storage paths/policies;
- search/vector filters;
- queue/event metadata and consumers;
- logs/metrics/traces;
- exports/backups/deletion;
- admin/support tooling;
- AI retrieval and memory.

Test cross-tenant access systematically, including indirect references and background jobs.

## 8. Secrets and Key Management

- central secrets manager/KMS/HSM according to risk;
- no secrets in source, images, logs, tickets, prompts, or client bundles;
- workload identity/short-lived credentials preferred;
- rotation and revocation without downtime;
- separate keys/roles by environment and blast radius;
- envelope encryption for data at scale;
- audit use and anomalous access;
- backup and disaster recovery for key material;
- cryptographic agility and versioned ciphertext;
- split knowledge/separation of duties for high-value keys.

Encryption with unrecoverable or over-permissive keys is not a complete control.

## 9. Encryption and Data Protection

Define:

- TLS and certificate lifecycle;
- service-to-service encryption and identity;
- at-rest encryption for databases, object stores, queues, backups, devices;
- field-level encryption/tokenization when infrastructure operators must not see data;
- password hashing with a modern adaptive algorithm;
- nonce/IV and authenticated encryption handling;
- key ownership/rotation/versioning;
- redaction/masking in UI, exports, and logs;
- integrity signatures/checksums where tampering matters.

Do not invent cryptographic protocols.

## 10. API and Input Security

- schema and type validation;
- size, depth, complexity, decompression, and file limits;
- allowlists for URLs/protocols/redirects where relevant;
- parameterized queries and safe serializers/templates;
- object/function/property authorization;
- mass-assignment protection;
- SSRF protections and egress policy;
- upload malware/content validation and isolated processing;
- rate/concurrency/cost limits;
- CORS/CSRF/session protections appropriate to client model;
- safe error messages;
- replay prevention for signed requests/webhooks;
- inventory/version/deprecation of APIs.

Treat partner and internal APIs as attack surfaces too.

## 11. Abuse and Fraud Architecture

Model legitimate-looking misuse:

- account creation/credential stuffing;
- scraping and enumeration;
- promotional/referral abuse;
- spam/notification abuse;
- payment fraud/refunds/chargebacks;
- resource/cost exhaustion;
- marketplace manipulation;
- fake reviews/content;
- automated agent/tool misuse.

Controls may include:

- velocity/risk limits;
- device/session reputation;
- step-up verification;
- holds and delayed irreversible actions;
- anomaly detection;
- manual review and appeal;
- audit and explainable reason codes;
- per-tenant/user quotas;
- privacy-preserving signals.

Avoid automated decisions whose false positives cause severe harm without a review path.

## 12. Logging and Audit

Security/audit events should capture:

- actor/workload/tenant identity;
- action and target;
- decision/policy/result;
- timestamp and correlation;
- source/device context where justified;
- before/after reference or immutable event for privileged changes;
- admin/support access;
- auth failures, key use, policy changes, export/delete, and high-value transactions.

Protect logs from tampering and unauthorized access. Do not log secrets, raw tokens, passwords, full payment data, unnecessary personal data, or sensitive prompt/retrieval content.

## 13. Supply-Chain Security

- dependency and base-image inventory/SBOM;
- pinned/reproducible builds and lockfiles;
- signed commits/artifacts/provenance where appropriate;
- vulnerability and license scanning;
- minimal trusted builders and protected CI credentials;
- review of generated code and build scripts;
- secret scanning;
- artifact registry access/retention;
- update and emergency-patch process;
- third-party package compromise scenario;
- runtime allowlisting/sandboxing for untrusted plugins/tools.

## 14. Privacy by Design

- minimize collection and precision;
- purpose limitation and consent where required;
- default-private access;
- retention tied to purpose;
- user/admin access, correction, export, and deletion workflows;
- data residency and processor inventory;
- privacy-safe analytics and telemetry;
- pseudonymization/tokenization where feasible;
- deletion propagation to caches, search, vectors, derived data, and vendors;
- backup expiration/recovery policy;
- privacy impact assessment for high-risk processing.

## 15. Compliance Handoff

Architecture must identify applicable obligations, but do not invent legal conclusions.

For regulated/high-risk systems:

- name jurisdiction, data, business process, and likely framework;
- map controls and evidence owners;
- record assumptions and unresolved interpretations;
- involve legal/compliance/security/domain specialists;
- preserve auditability, retention, and change control;
- test control operation, not only policy existence.

Examples may include payment-card, financial, healthcare, identity, child data, public-sector, export, accessibility, and regional privacy requirements.

## 16. Security Operations and Incident Response

Define:

- detection and triage signals;
- severity and escalation;
- identity/token/key revocation;
- containment and tenant/customer scoping;
- forensic evidence retention;
- breach notification decision path;
- dependency/vendor coordination;
- recovery and credential rotation;
- post-incident fixes and validation;
- tabletop exercises.

Break-glass access must be time-limited, audited, approved/reviewed, and easy to revoke.

## 17. Security Verification

- threat-model review;
- static/dependency/secret scanning;
- unit/integration authorization tests;
- tenant-isolation tests;
- API security and abuse-case tests;
- fuzz/property tests for parsers/protocols;
- penetration testing for material exposure;
- infrastructure/policy-as-code checks;
- key/credential rotation drills;
- backup ransomware/corruption exercise;
- incident tabletop;
- AI red-team/evaluation for model systems.

## 18. Critical Security Gates

Block launch when any applies without accountable acceptance:

- missing server-side authorization on sensitive resources/actions;
- tenant scope not enforced at data access;
- secrets or sensitive data exposed in code/logs/prompts;
- privileged shared static credentials;
- irreversible high-risk action without policy/approval/audit;
- no rate/resource limits on expensive public operations;
- untrusted input can direct internal network/file/tool access;
- critical dependency/webhook unauthenticated;
- backup/key recovery untested;
- known critical vulnerability or insecure default;
- no incident owner or revocation/containment path.

## 19. Common Mistakes

| Mistake | Correction |
|---|---|
| “inside VPC” equals trusted | authenticate/authorize resource access and contain networks |
| role check only at gateway | enforce object/function/property/workflow policy at service/data boundary |
| tenant ID accepted from request body | derive trusted context and enforce in every storage/query layer |
| encrypt everything with one broad key role | isolate keys/roles, rotate, audit, plan recovery |
| privacy deletion only from primary DB | propagate to caches, search, vectors, exports, vendors, backups policy |
| security checklist after design | threat-model during boundary/data/interface decisions |
| log full payload for debugging | structured minimal telemetry with redaction and controlled sampling |
| dependency scanning treated as supply-chain program | add provenance, protected builds, inventory, patch and incident processes |
