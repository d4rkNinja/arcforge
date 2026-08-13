# Governed Support Agent — Compact Example

A support agent may search tenant-scoped documentation and account history, draft a response, and create a draft case note. It cannot issue refunds, change permissions, or send external messages without approval.

## Control path

1. Gateway authenticates the support operator and resolves tenant/customer scope.
2. Context assembler loads product policy and the active case, then retrieves only authorized documents.
3. Model produces a typed response draft, cited evidence IDs, and optional proposed actions.
4. Policy engine rejects actions outside the operator’s mandate.
5. Refund proposals invoke a typed preview tool; execution requires human approval and an idempotency key.
6. Verifier checks citations, forbidden claims, account identifiers, and policy compatibility.
7. Trace records versions, evidence, tool decisions, approval, latency, and cost with protected fields redacted.

## Bounds

- 2 model attempts;
- 6 retrieval/tool calls;
- 30-second deadline;
- tenant-scoped memory disabled by default;
- read-only degraded mode during billing-system outage;
- kill switch disables all write tools without disabling search and drafting.
