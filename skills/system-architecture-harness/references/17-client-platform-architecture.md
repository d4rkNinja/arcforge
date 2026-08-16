# Client and Platform Architecture

Use this reference when browser, mobile, desktop, offline/local-first, real-time, or
search behavior affects correctness or system boundaries. The topic coverage is informed
by section 21 of the user-supplied research manuscript; treat it as research input, not
independent publication proof.

## Contents

- [1. Include the client in the system](#1-include-the-client-in-the-system)
- [2. Select rendering per route](#2-select-rendering-per-route)
- [3. Classify client state](#3-classify-client-state)
- [4. Treat accessibility and performance as correctness](#4-treat-accessibility-and-performance-as-correctness)
- [5. Model mobile and desktop lifecycle](#5-model-mobile-and-desktop-lifecycle)
- [6. Design offline and local-first authority](#6-design-offline-and-local-first-authority)
- [7. Define synchronization and conflicts](#7-define-synchronization-and-conflicts)
- [8. Complete real-time and search lifecycles](#8-complete-real-time-and-search-lifecycles)
- [9. Client architecture gates](#9-client-architecture-gates)

## 1. Include the client in the system

A backend-only view is incomplete when the client owns presentation, interaction,
durable local state, pending operations, encryption keys, notifications, or real-time
connections. Model client versions, device lifecycle, data authority, and degraded
behavior alongside cloud services. Trace critical journeys through rendering, network,
local persistence, sync, authorization, server state, and recovery.

## 2. Select rendering per route

Choose route by route rather than imposing one product-wide mechanism.

| Need | Candidate | Obligations to validate |
|---|---|---|
| Rich post-load interaction | SPA/client rendering | bundle, CPU, API waterfall, caching, error/offline states |
| Personalized initial content | server rendering | server capacity, cache variation, hydration and version skew |
| Stable public content | static generation | publish invalidation, freshness, preview and rollback |
| Mostly static with selective interaction | islands/selective hydration | component boundaries, shared state and navigation |
| Server-owned data composition | server components or equivalent | framework execution, caching, authorization and observability |

Record first-content and interaction targets, round trips, JavaScript/image/font budgets,
cache rules, crawler/discoverability needs, personalization, and failure fallback.

## 3. Classify client state

For every state item classify authority and lifetime:

| Class | Required contract |
|---|---|
| Server-authoritative remote state | freshness, cache key, invalidation, optimistic update and rollback |
| URL/navigation state | shareability, history, deep-link and restore behavior |
| Form/interaction state | validation authority, draft lifetime and sensitive-data handling |
| Derived cached state | derivation source, invalidation and rebuild |
| Durable local/offline state | storage, schema version, authority, sync, conflict and backup |
| Identity/session state | secure storage, refresh, expiry, logout and device revocation |

Derive rather than mirror where possible. Do not copy remote state into a global store
without freshness and invalidation semantics. Separate ephemeral UI state from durable
operations whose loss would violate user expectations.

## 4. Treat accessibility and performance as correctness

Define and test semantic structure, names/roles, keyboard operation, focus order and
restoration, contrast, text scaling, assistive technology, reduced motion, and error
announcements. Include accessibility in component contracts and release acceptance.

Allocate an end-to-end performance budget across initial bytes, images, fonts,
JavaScript, hydration, main-thread work, local storage, request waterfalls, and server
latency. Test representative low-power devices and impaired networks. A client that
serializes independent requests or blocks on optional enrichment can violate the user
journey while each backend remains within its own SLO.

## 5. Model mobile and desktop lifecycle

For mobile define memory pressure, battery and radio cost, background execution limits,
process death, intermittent connectivity, notification delivery, secure key storage,
store review/distribution, minimum supported version, and forced/optional upgrades.

For desktop add installer/package trust, OS and architecture matrix, filesystem and
native integration permissions, auto-update channels, rollback, local backups, and
enterprise-managed deployment. Cross-platform frameworks still require platform-
specific behavior, accessibility, native module, lifecycle, and release testing.

## 6. Design offline and local-first authority

Caching API responses is not an offline architecture. Specify:

- which entities and operations remain usable offline and which fail closed;
- server-, local-, peer-, or jointly authoritative state per field/operation;
- durable local schema, encryption/key recovery, quota, eviction, backup and deletion;
- local operation identity, causal/version metadata, pending/acknowledged/rejected/
  conflicted states, and idempotent replay;
- partial datasets, missing dependencies, attachment/blob transfer and storage pressure;
- login/session expiry, permission change, user/device revocation and remote wipe limits;
- client schema migration across skipped versions, rollback, corrupt state and reset;
- data retention, export, deletion, audit and consent while a device is disconnected.

State what the user can observe and edit when offline, what evidence confirms durable
local acceptance, and what can be lost if the device fails before synchronization.

## 7. Define synchronization and conflicts

Choose operation log, state synchronization, snapshot-plus-delta, operational
transformation, CRDT, or a hybrid from domain semantics. None removes product decisions.

For each synchronized object define:

- identity, version/vector/sequence or causal metadata and ordering scope;
- initial snapshot, incremental cursor, gap detection, catch-up and full-resync trigger;
- duplicate, reorder, concurrent edit, tombstone, deletion and resurrection behavior;
- automatic merge rules by field/operation and conflicts requiring human resolution;
- authorization at sync time and again when applying queued operations;
- server rejection, local rollback/compensation, conflict UI and audit history;
- batch size, compression, concurrency, retry/deadline, backpressure and quota behavior;
- reconciliation invariant and repair path after interruption or partial transfer.

Last-write-wins is acceptable only when losing a concurrent value is a declared domain
rule. CRDT convergence does not prove semantic correctness: test whether its merge
matches user intent, authorization, invariants, deletion, and undo expectations.

## 8. Complete real-time and search lifecycles

### Real-time

Define connection authentication/refresh, routing, heartbeat, idle expiry, regional
handoff, drain on deployment, per-client buffer, slow-consumer policy, fan-out limits,
reconnect cursor, gap detection, snapshot-plus-delta catch-up, duplicate/order semantics,
and fallback when the real-time path is unavailable. Keep ephemeral presence separate
from durable facts. Quantify “real time” per journey.

### Search

Treat the index as derived unless explicitly authoritative. Define source capture,
document/version identity, analyzer/language behavior, tenant and ACL filtering, update
and deletion freshness, out-of-order changes, backfill, index version/alias cutover,
rebuild and reconciliation. Evaluate relevance with a representative query/judgment set;
measure added latency and cost for hybrid retrieval or reranking.

## 9. Client architecture gates

- Reject a client design that omits authority, durable local state, lifecycle, version
  compatibility, accessibility, performance, security, and degraded behavior.
- Reject “cache then reconnect” without operation/state synchronization, gap detection,
  conflict semantics, reconciliation, backpressure, and full-resync behavior.
- Reject CRDT, operational transformation, or last-write-wins as automatic correctness.
- Block launch when client schema migration, device revocation, encryption/key handling,
  partial-data/quota behavior, or authorization after reconnect is unspecified.
- Reject real-time or search designs with no lifecycle, source of truth, catch-up/rebuild,
  or tenant/access-control semantics.
