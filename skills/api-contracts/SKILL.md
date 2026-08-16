---
name: api-contracts
description: "Use when implementing or changing HTTP/RPC/GraphQL APIs, SDKs, or CLIs: endpoint design, request validation, error architecture and status mapping, pagination, filtering and sorting, bulk and batch APIs, API versioning and backward compatibility, data serialization, webhooks (signing, retries, replay protection), realtime channels (WebSockets, SSE), security headers, or client/SDK behavior. Loads production implementation papers with MUST/SHOULD/AVOID/NEVER rules, failure modes, and verification checklists to read before writing code. For whole-system architecture use system-architecture-harness; for auth and permissions use auth-access; for queue/event internals use async-messaging; for schema migration sequencing use migration-evolution."
---

# API & Client Contracts Implementation

## Overview

Implementation intelligence for API surfaces and their clients. Each reference paper captures the contract work that first drafts skip: request lifecycle and deadlines, validation edge cases, error taxonomies that do not leak internals, stable pagination under concurrent writes, deprecation windows, webhook signature verification, and realtime reconnection semantics.

**Core principle:** An API is a compatibility promise. Every endpoint, error, cursor, and webhook is a contract with real clients — including old clients you no longer control.

## Implementation Law

```text
NO API IMPLEMENTATION WITHOUT:
1. the primary paper(s) for the surface read in full first;
2. the paper's "Questions that must be answered before implementation"
   answered, or each open point labeled as an assumption;
3. "Existing-codebase checks" run when changing an existing API;
4. every applicable MUST mapped to a decision, a test, or a documented
   exception — never silently downgraded.
```

## When to Use

Use this skill when implementing or changing:

- REST, RPC, gRPC, or GraphQL endpoints and resource/command design;
- request parsing, body limits, content-type handling, and input validation;
- error architecture: codes, HTTP status mapping, public vs internal detail;
- pagination (offset/cursor), filtering, sorting, and query complexity limits;
- bulk and batch operations with partial-failure reporting;
- API versioning, deprecation, sunset windows, and breaking-change detection;
- data serialization choices and precision/compatibility pitfalls;
- webhooks: registration, signing, timestamp/replay validation, retries, dead-lettering;
- realtime communication: WebSockets/SSE, presence, reconnection, ordering;
- SDK/client libraries and CLI-backend interactions;
- security headers for browser-facing APIs.

## When Not to Use

- Whole-system architecture design: use `system-architecture-harness`.
- Authentication, authorization, API keys: use `auth-access`.
- Queue delivery semantics, events, outbox: use `async-messaging`.
- Database schema evolution sequencing: use `migration-evolution` (070 overlaps at the contract level).
- Rate limiting and quotas mechanics: use `resilience-flow-control` (038, 039).

## Required Context Loading

| Situation | Papers |
|---|---|
| Middleware, request context, deadlines, cancellation | [011 Request Lifecycle](references/papers/011-request-lifecycle.md) |
| Field/type/cross-field validation, malformed payloads | [012 Input Validation](references/papers/012-input-validation.md) |
| Error taxonomy, status mapping, masking, correlation | [013 Error Architecture](references/papers/013-error-architecture.md) |
| Resource and command design, REST/RPC/GraphQL trade-offs | [014 API Design](references/papers/014-api-design.md) |
| Versioning strategies, deprecation, breaking changes | [015 API Versioning & Compatibility](references/papers/015-api-versioning-and-compatibility.md) |
| Offset vs cursor pagination, stable ordering | [016 Pagination](references/papers/016-pagination.md) |
| Allowed filter fields, operator validation, complexity limits | [017 Filtering / Sorting / Query APIs](references/papers/017-filtering-sorting-query-apis.md) |
| Webhook signing, retries, replay protection, versioning | [049 Webhooks](references/papers/049-webhooks.md) |
| WebSockets/SSE, auth, reconnection, scaling | [050 Realtime Communication](references/papers/050-realtime-communication.md) |
| Serialization formats and compatibility pitfalls | [116 Data Serialization](references/papers/116-data-serialization.md) |
| Browser security headers | [115 Web Security Headers](references/papers/115-web-security-headers.md) |
| SDK design, retries, compatibility for library clients | [110 SDK / Client Design](references/papers/110-sdk-client-design.md) |
| CLI auth, pagination, error display for backend CLIs | [111 CLI Backend Interaction](references/papers/111-cli-backend-interaction.md) |

## Workflow

1. Identify the surface being built or changed and select the primary paper; load neighbors for every contract edge you touch (a new list endpoint usually needs 014 + 016 + 017 + 012 + 013).
2. Read the primary paper fully, including normative requirements and common bugs.
3. Answer the paper's pre-implementation questions; label autonomous assumptions and their impact.
4. For existing APIs, run the existing-codebase checks: inventory real clients, current schemas, and usage before renaming fields, tightening validation, or changing defaults.
5. Convert each MUST/SHOULD/AVOID/NEVER into contract decisions: schemas, status codes, limits, versioning policy, and error model — each with a test.
6. Implement the smallest safe slice; carry the paper's verification checklist (malformed inputs, cursor stability under writes, old-client compatibility) into the test plan.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Boundary Map

| If the task also involves | Also use |
|---|---|
| Authentication and object-level authorization | `auth-access` (008, 113, 114) |
| Async side effects, event publication, webhooks at scale | `async-messaging` (045, 046, 047) |
| Rate limits and quotas on the surface | `resilience-flow-control` (038, 039) |
| Query/index implications of filters and sorting | `data-storage` (027, 028) |
| Contract-breaking rollout sequencing | `migration-evolution` (070, 071, 134) |
| Error/redaction and header security policy | `security-privacy` (062, 066) |

## Output Contract

1. **Papers consulted** — numbers and the sections relied on.
2. **Assumptions and unanswered questions** — labeled, with their design impact.
3. **Rule-to-decision map** — each applicable MUST/SHOULD → contract decision, enforcement point, and test.
4. **Failure modes addressed** — malformed input, cursor instability, breaking changes, webhook replay, realtime message loss.
5. **Verification evidence** — tests mapped to the paper's verification checklist.
6. **Compatibility and migration notes** — old clients, deprecation windows, versioning policy.

## Stop Conditions

Stop and revise when any of these appears:

- code is written before the primary paper's pre-implementation questions are answered or labeled;
- endpoints without validation, size limits, and a defined error contract;
- error responses that leak stack traces, SQL, internal codes, or sensitive data;
- pagination without stable ordering, maximum page size, or duplicate/miss handling under writes;
- user-controlled filter/sort fields without an allowlist and complexity limits;
- a breaking change with no versioning, deprecation window, or client inventory;
- webhooks without signature verification, timestamp validation, and bounded retries;
- realtime channels without authentication, reconnection, heartbeat, and ordering policy;
- serialization that silently loses precision, timezone, or unknown-field fidelity;
- bulk APIs without per-item error reporting and partial-failure semantics;
- any API MUST downgraded to a TODO without a documented exception.

## References

Thirteen production papers under `references/papers/`: 011 Request Lifecycle, 012 Input Validation, 013 Error Architecture, 014 API Design, 015 API Versioning & Compatibility, 016 Pagination, 017 Filtering / Sorting / Query APIs, 049 Webhooks, 050 Realtime Communication, 110 SDK / Client Design, 111 CLI Backend Interaction, 115 Web Security Headers, 116 Data Serialization. Cross-domain pointers inside the papers name the sibling skill to activate.

Worked example: [a bounded, cursor-paginated list endpoint](examples/worked-example-orders-list-api.md).
