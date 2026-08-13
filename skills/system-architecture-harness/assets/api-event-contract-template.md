# API and Event Contract Template

## Contract Metadata

- Capability:
- Owner:
- Consumers:
- Classification:
- Lifecycle state:
- Compatibility policy:
- Deprecation window:
- Source specification: OpenAPI / AsyncAPI / schema registry / other

# Part A — Synchronous API

## Operation

- Method and path / procedure:
- Purpose:
- Authentication mechanism:
- Authorization rule:
- Tenant / resource ownership rule:
- Idempotency behavior:
- Concurrency control:
- End-to-end deadline:
- Maximum payload and rate:

## Request

| Field | Type | Required | Constraints | Classification | Meaning |
|---|---|---:|---|---|---|
| ... | ... | ... | ... | ... | ... |

## Response

| Status | Stable code | Meaning | Retryable? | Client action |
|---:|---|---|---:|---|
| ... | ... | ... | ... | ... |

- Pagination / cursor semantics:
- Partial-result semantics:
- Cache controls:
- Consistency / freshness promise:
- Correlation identifier:
- Problem-details shape:

## Compatibility

- Additive changes allowed:
- Breaking changes:
- Version negotiation:
- Consumer contract tests:
- Sunset and migration plan:

# Part B — Asynchronous Event or Command

## Envelope

- Event / command name:
- Semantic version:
- Producer:
- Consumers:
- Partition / ordering key:
- Event identifier:
- Correlation / causation identifiers:
- Occurred-at and published-at timestamps:
- Tenant / subject:
- Trace context:

## Payload

| Field | Type | Required | Constraints | Classification | Meaning |
|---|---|---:|---|---|---|
| ... | ... | ... | ... | ... | ... |

## Delivery Semantics

- At-most-once / at-least-once / broker-specific guarantee:
- Consumer idempotency key and retention:
- Ordering scope:
- Retry and backoff:
- Poison-message / quarantine policy:
- Retention and replay:
- Compaction / tombstone behavior:
- Schema compatibility mode:
- Late and duplicate event handling:
- Reconciliation source:

## Security and Privacy

- Producer and consumer authorization:
- Encryption and key scope:
- Sensitive fields prohibited or protected:
- Residency, retention, deletion, and subject-request handling:
- Audit requirements:

## Validation

- Contract test:
- Compatibility test:
- Replay test:
- Duplicate and reordering test:
- Load / lag test:
- Failure injection:
