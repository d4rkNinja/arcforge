---
name: api-contracts
description: "Use when thinking through, reviewing, changing, or verifying APIs and client contracts: endpoint design, validation, errors, pagination, filtering, bulk behavior, versioning, serialization, webhooks, realtime channels, SDKs, or CLIs. For whole-system architecture use system-architecture-harness; for identity and permissions use auth-access; for event delivery use async-messaging; for compatibility rollout use migration-evolution."
---

# Think Through API & Client Contracts

## Overview

Production guidance for API surfaces and their clients. Each reference paper captures the contract work that first drafts skip: request lifecycle and deadlines, validation edge cases, error taxonomies that do not leak internals, stable pagination under concurrent writes, deprecation windows, webhook signature verification, and realtime reconnection semantics.

**Core principle:** An API is a compatibility promise. Every endpoint, error, cursor, and webhook is a contract with real clients — including old clients you no longer control.

## Domain Law

```text
NO API OR CLIENT CONTRACT CHANGE WITHOUT:
1. the primary paper(s) for the surface read in full first;
2. the paper's pre-change questions
   answered, or each open point labeled as an assumption;
3. "Existing-codebase checks" run when changing an existing API;
4. every applicable MUST mapped to a decision, a test, or a documented
   exception — never silently downgraded.
```

## When to Use

Use this skill when thinking through, reviewing, changing, or verifying:

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

## Select the Operating Mode

| Mode | Use when | Required result |
|---|---|---|
| **Think** | The safe decision is not settled | requirements, constraints, invariants, risks, alternatives, decision, and validation path |
| **Review** | An artifact, repository, diff, or operating state already exists | evidence separated from assumptions, prioritized findings, and blockers |
| **Change** | Decisions are approved and repository changes are requested | the smallest safe change, compatibility notes, and verification still required |
| **Verify** | A claim needs proof | tests or measurements run, observed evidence, and residual risks |

If the user names a mode, use it. Otherwise infer the mode from intent and state the inference in one sentence. For a combined request, run **Think → Review → Change → Verify** and preserve the trace between phases. Think may stop with a decision; Review may stop with findings. Change must not claim completion before Verify. Verify must never turn a planned or unavailable check into evidence.

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

Use the domain workflow as shared gates, then branch by the selected mode:

- **Think:** answer the questions and stop with a reasoned decision and validation path; do not edit by default.
- **Review:** inspect the available artifact or repository and stop with evidence-backed findings; do not claim changes.
- **Change:** apply only approved decisions, then continue to Verify before claiming completion.
- **Verify:** run the relevant checks, report observed results, and label every unavailable or unrun check.

1. Identify the surface being built or changed and select the primary paper; load neighbors for every contract edge you touch (a new list endpoint usually needs 014 + 016 + 017 + 012 + 013).
2. Read the primary paper fully, including normative requirements and common bugs.
3. Answer the paper's pre-implementation questions; label autonomous assumptions and their impact.
4. For existing APIs, run the existing-codebase checks: inventory real clients, current schemas, and usage before renaming fields, tightening validation, or changing defaults.
5. Convert each MUST/SHOULD/AVOID/NEVER into contract decisions: schemas, status codes, limits, versioning policy, and error model — each with a test.
6. Apply the active mode: stop at a decision in Think; stop at findings in Review; make the smallest approved safe change in Change; run the paper's malformed-input, cursor-stability, and old-client checks in Verify.
7. Before completion, re-scan the normative lists and stop if any rule lacks a decision, test, or documented exception.

## Companion Skills and Standalone Safety

| Type | When | Companion | Missing companion behavior |
|---|---|---|---|
| **Required** | Authentication or object, field, action, or tenant authorization is in scope | `auth-access` | Preserve authorization requirements and identify missing access-policy depth. |
| **Recommended** | Filters, sorting, pagination, or serialization affect queries or precision | `data-storage` | Keep fields allowlisted and responses bounded; label storage depth missing. |
| **Handoff** | Event delivery or webhook worker internals are in scope | `async-messaging` | Define the surface contract and identify delivery internals as incomplete. |
| **Handoff** | Old clients or consumers must coexist with a contract change | `migration-evolution` | Do not prescribe a breaking one-step rollout. |

If a companion is unavailable, complete only the safe local contract decision, name the missing depth, and recommend the exact technical ID or relevant installation group. Never claim unavailable material was read or weaken a compatibility, authorization, or boundedness requirement.

## Output Contract

The selected mode is authoritative. Include only applicable fields below; a planned check is a validation path, not verification evidence.

Scale the output to the active mode: Think returns contract decisions; Review returns evidence-backed findings; Change returns the repository-aware change plus pending proof; Verify returns observed compatibility and failure evidence with unrun checks labeled. A combined flow preserves all four phases.

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
