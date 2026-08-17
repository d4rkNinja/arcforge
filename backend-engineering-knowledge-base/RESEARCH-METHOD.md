# Research and Synthesis Method

**Verification cutoff:** 2026-08-17

## Canonical scope

The numbered titles, editorial notes, and bullet subtopics in `original/Pasted text.txt` are authoritative for scope. The generator/curation process does not silently remove a canonical subtopic. The manifest preserves every title and subtopic for machine validation.

Canonical papers remain authoritative for engineering explanation, trade-offs,
and contextual guidance. The structured registry under `rules/` owns stable
machine-traceable records only for selected critical obligations. A structured
record must point to matching paper text; migration does not authorize deleting
the existing obligation until semantic review proves the replacement is
equivalent or stronger.

## Evidence hierarchy

1. Normative standards and specifications: IETF/RFC Editor, W3C, OpenID Foundation, NIST, ISO-adjacent public specifications, CNCF/OpenTelemetry, OpenAPI, GraphQL, AsyncAPI, and protocol standards.
2. Official vendor/platform/database documentation for provider-specific behavior and operational limits.
3. Peer-reviewed or foundational distributed-systems/security papers.
4. Respected engineering books and SRE guidance.
5. Production engineering patterns, incident-oriented guidance, and provider implementation notes where standards do not define operational behavior.

## Synthesis rules

- Separate semantic requirements from one framework/provider mechanism.
- State trade-offs and failure modes rather than copying a best-practice slogan.
- Treat retries, timeouts, duplicate delivery, concurrency, partial failure, stale reads, mixed versions, rollback, and cleanup as normal paths.
- Put race-sensitive invariants at an authoritative boundary such as a database constraint, conditional update, transaction, fenced lease, or durable workflow.
- Treat caches, indexes, replicas, analytics, and embeddings as derived unless explicitly authoritative.
- Require evidence for authorization, tenant isolation, privacy, audit, and abuse controls across asynchronous and administrative paths.
- Use small state diagrams and schemas only when they clarify semantics; implementation syntax remains out of scope.

## Normative labels

- **MUST:** required to satisfy the stated correctness/security contract.
- **SHOULD:** strong production recommendation; deviation needs a documented reason and compensating evidence.
- **MAY:** context-dependent option whose trade-offs must be selected deliberately.
- **AVOID:** a commonly fragile approach that may be justified only with explicit safeguards.
- **NEVER:** fundamentally unsafe under the assumptions stated in the paper.

These labels follow BCP 14 terminology where capitalized; see sources S001 and S002.

## Currentness and provider behavior

Every paper records the verification cutoff and source versions. Living standards, cloud products, identity providers, databases, SDKs, and model APIs can change. Before implementation, an agent must verify the exact deployed version and provider contract rather than treating the corpus as timeless.

## What this corpus deliberately does not do

- It does not prescribe a single language, framework, database, cloud, or architecture.
- It does not replace legal advice or organization-specific policy.
- It does not infer that an advertised delivery, consistency, or security property applies end-to-end.
- It does not authorize rebuilding existing code; the codebase checks require preserving verified behavior and compatibility.
