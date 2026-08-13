# Context, Retrieval, and Memory

## Context hierarchy

Assemble context in explicit layers:

1. immutable platform and safety policy;
2. product/developer instructions;
3. task contract and user request;
4. trusted application state;
5. retrieved or tool-produced evidence;
6. conversation and memory;
7. generated scratch artifacts.

Lower layers cannot redefine the authority of higher layers. Mark evidence boundaries and provenance in machine-readable form where possible.

## Token allocation

Assign a budget per layer rather than truncating the final prompt blindly. Reserve capacity for tool results and final structured output. Compact by preserving decisions, constraints, unresolved risks, identifiers, and citations—not conversational phrasing.

## RAG ingestion contract

For each source, define:

- owner, tenant, access policy, privacy class, and retention;
- parser and normalization version;
- chunking strategy and semantic unit;
- source identifier, revision, timestamp, and deletion marker;
- embedding model and dimensionality;
- metadata filters and authorization inheritance;
- re-index, rollback, and audit behavior.

## Retrieval pipeline

A production pipeline may include intent classification, query rewrite, authorization filters, lexical/vector retrieval, reranking, diversity, freshness, deduplication, and evidence packing. Every stage needs an evaluation signal.

Measure at minimum:

- retrieval recall at k;
- precision or relevance at k;
- authorization-filter correctness;
- citation/source attribution accuracy;
- stale and conflicting evidence behavior;
- answer groundedness and abstention quality;
- latency and cost by stage.

## Memory types

| Memory | Purpose | Typical authority | Lifecycle |
|---|---|---|---|
| Conversation | current interaction continuity | low | session or short TTL |
| Task checkpoint | resumable workflow state | medium | task completion plus audit window |
| User preference | personalization | user-correctable | explicit retention and deletion |
| Semantic knowledge | reusable domain facts | source-dependent | versioned and revalidated |
| Procedural memory | successful method or failure lesson | advisory | reviewed, deduplicated, aged out |
| Audit history | evidence of actions and approvals | high integrity | policy-defined, append-oriented |

## Memory write gate

Before a write, answer:

- Who is the subject and tenant?
- What source supports it?
- Is it fact, preference, inference, or procedure?
- What confidence and expiry apply?
- Can the user inspect, correct, or delete it?
- Could it reveal secrets, health, finance, identity, or regulated data?
- What happens when later evidence conflicts?

## Injection resistance

Treat documents, web pages, emails, code comments, issue text, tool output, and memory as adversarial input. Preserve content for reasoning but strip any implied authority. Tool calls derived from untrusted content still pass through policy, authorization, and approval.
