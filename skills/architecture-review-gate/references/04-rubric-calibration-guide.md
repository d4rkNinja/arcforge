# Evidence-Vector Calibration Guide

Use this dimension library to preserve broad production coverage without imposing fixed categories, weights, point allocations, or universal pass thresholds. Start from the five-gate review contract in `references/01-contextual-ai-review-rubric.md`, not from this list.

## Calibration Method

1. Select, merge, split, or rename dimensions to match the decision.
2. Tie every dimension to a requirement, invariant, risk, constraint, or obligation.
3. Define evidence anchors and required maturity before assessment.
4. Explain exclusions and avoid double counting.
5. Keep the resulting vector visible; do not collapse it into a mandatory score.

## Possible Dimensions

### Gate A — Problem and fitness

Consider stakeholders, critical journeys, non-goals, decision horizon, measurable quality scenarios, current-state evidence, assumptions, workload ranges, bursts, skew, growth, dependency limits, legal constraints, and specialist handoffs.

### Gate B — State and boundaries

Consider authoritative, derived, ephemeral, sensitive, and rebuildable state; invariants; state machines; transactions; concurrency; sources of truth; ownership; consistency; ordering; idempotency; unknown outcomes; data lifecycle; component and trust boundaries; communication semantics; and whether every boundary purchases independent change, scale, failure, governance, or security capability.

### Gate C — Failure and assurance

Consider partial failure, timeout and retry coherence, duplicate and delayed work, overload, bulkheads, degraded modes, shared dependencies, correlated failure, recovery load, reconciliation, RTO/RPO, restore/failover evidence, threat model, identity, authorization, tenant isolation, secrets, abuse, privacy, and logic/integration/concurrency/load/recovery/adversarial tests.

### Gate D — Delivery and operation

Consider telemetry linked to user outcomes, workflows, data, dependencies, cost, and owners; impact-based alerts; runbooks; on-call; capacity envelope and next bottleneck; compatible API/event/schema/configuration evolution; progressive rollout; canary and stop conditions; rollback/roll-forward; migration, backfill, reconciliation, cleanup; dependency upgrades; and restore drills.

### Gate E — Economics, complexity, and evolution

Consider development, infrastructure, licensing, support, incident, coordination, and migration cost; code, dependency, state, distribution, operations, configuration, security, and organizational complexity; knowledge concentration; capability gained; alternative simplicity; reversibility; compatibility and exit path; expected lifetime; temporary-path deletion; validation triggers; and owner/review date.

### AI and agent dimensions

When applicable, consider task suitability, baseline alternatives, model/prompt/index provenance, retrieval authorization, memory scope, typed outputs, tool identity and least privilege, policy outside the model, human approval, sandboxing, audit, budgets, termination, evaluation, fallback, prompt injection, data exfiltration, and kill switches. Keep these within the five gates rather than treating “AI” as an automatically compensating category.

## Calibration Questions

- What failure would make approval irresponsible?
- Which dimensions protect the most important invariant or journey?
- Which uncertainties could reverse the recommendation?
- Is transition-state risk visible, or only target-state quality?
- Does evidence maturity match the decision horizon?
- Is missing evidence distinguished from a proven defect?
- Would the same frame be fair to a simpler competing design?
- Is the Complexity Ledger present and complete enough to reveal lifecycle obligations?
- Is any metric being mistaken for the outcome it only approximates?

## Optional Numeric Summaries

Use a number only for a named decision where stakeholders can explain how it helps. Require:

- explicit mapping from evidence states to values;
- transparent assumptions and uncertainty;
- sensitivity to plausible alternative mappings or priorities;
- no universal threshold or normalized-weight requirement;
- blockers and required conditions evaluated separately; and
- the full vector presented beside the number.

Omit the number when dimensions are incomparable, evidence is sparse, or the summary would obscure a weak critical dimension.

## Multi-Reviewer Calibration

Give reviewers the same frozen contract and evidence, but not each other's conclusions. Compare:

- selected and excluded dimensions;
- blocker recall;
- evidence state and quality;
- complexity obligations;
- source claims versus reviewer inference;
- verdict and confidence; and
- approval conditions.

Do not average away disagreement. Resolve it with better evidence or an accountable decision owner.
