# Contextual Architecture Evidence Vector

Use this reference after establishing the review contract and reconstructing the architecture. Build a decision-specific evidence vector instead of applying universal categories, weights, or release thresholds.

## Contents

- Non-Negotiable Rule
- 1. Freeze the Review Frame Before Judging
- 2. Use the Five Gates
- 3. Define Each Dimension
- 4. Assess Evidence Dimension by Dimension
- 5. Inspect the Complexity Ledger
- 6. Challenge the First Pass
- 7. Decide Without Fake Precision
- 8. Report Provenance

## Non-Negotiable Rule

The vector makes trade-offs and evidence maturity visible. Strong evidence in one dimension cannot compensate for a critical blocker or a failed required condition in another. A scalar, when justified at all, is supplementary and never approval-bearing.

## 1. Freeze the Review Frame Before Judging

Derive the frame from:

- the decision being gated and its accountable owner;
- critical user and operator journeys;
- measurable requirements, invariants, constraints, and unacceptable failures;
- state classes, tenancy, data sensitivity, and trust boundaries;
- workload, dependency, cost, and organizational assumptions;
- failure impact, reversibility, blast radius, and uncertainty;
- current, target, and transition states; and
- the maturity horizon: exploration, implementation, migration, or production release.

Do not reshape dimensions or decision conditions after seeing a weak result. If new evidence reveals an omitted requirement, version the frame and explain the change.

## 2. Use the Five Gates

Select dimensions within these gates. Merge, split, or exclude dimensions only with a stated reason.

| Gate | Review question | Required artifact | Decision test |
|---|---|---|---|
| A — Problem and fitness | What problem, stakeholder, measurable requirement, and constraint justify this design? | prioritized requirements and quality-attribute scenarios | success and unacceptable failure are decidable |
| B — State and boundaries | What is authoritative, derived, ephemeral, sensitive, rebuildable, and independently governed? | context, component, data, interaction, and ownership models | every boundary buys a named capability and state semantics are explicit |
| C — Failure and assurance | What can fail, duplicate, reorder, become ambiguous, or be compromised, and what proves recovery? | failure analysis, threat model, tests, and recovery plan | behavior is explainable for slow, unavailable, duplicated, or compromised dependencies |
| D — Delivery and operation | How are code, schema, configuration, infrastructure, capacity, and recovery operated safely? | rollout, observability, capacity, ownership, and readiness plans | the system can be deployed, diagnosed, and restored without its original authors |
| E — Economics, complexity, and evolution | Does capability gained justify lifecycle obligations under uncertainty? | ADR/RFC, Complexity Ledger, cost/reversal analysis, validation trigger | the decision is affordable, reversible enough, owned, and revisable from observed evidence |

## 3. Define Each Dimension

For every applicable dimension, record:

| Field | Required content |
|---|---|
| Dimension | decision-specific concern |
| Gate | A, B, C, D, or E |
| Why applicable | requirement, invariant, risk, or constraint |
| Protected condition | outcome that must remain true |
| Full-evidence anchor | evidence sufficient for this decision horizon |
| Partial-evidence anchor | useful but incomplete evidence |
| Failure anchor | contradiction, unsafe behavior, or unacceptable uncertainty |
| Required maturity | minimum evidence state for the decision |
| Evidence expected | artifact, measurement, test, configuration, runbook, or owner |

List exclusions and explain why they do not affect this decision. Do not reward irrelevant completeness.

## 4. Assess Evidence Dimension by Dimension

Use these states consistently:

- **Observed:** representative production measurement, drill, or incident evidence.
- **Validated:** integration, load, security, migration, restore, or failover evidence in a relevant environment.
- **Implemented:** inspectable code, configuration, schema, policy, contract, or test.
- **Designed:** documented mechanism, owner, and validation path.
- **Claimed:** assertion without supporting evidence.
- **Inferred:** reviewer conclusion derived from incomplete evidence.
- **Contradicted:** supplied evidence conflicts with the claim.
- **Missing:** required evidence was not supplied.

For each dimension, cite the evidence, classify its state and quality, explain the finding, name uncertainty and counter-evidence, and identify the smallest proof or change needed. Keep evidence quality separate from blocker status: strong evidence can prove a blocker, while weak evidence can create an evidence gap without proving a defect.

## 5. Inspect the Complexity Ledger

Require an explicit ledger for high-impact decisions. Record its absence rather than silently reconstructing one. Check:

- decision, requirement, capability gained, and alternatives;
- introduced concepts, states, protocols, configurations, and dependencies;
- operational responsibility and new failure modes;
- knowledge requirement and ownership concentration;
- security, performance, and cost effects;
- reversibility and migration path;
- expected lifetime or deletion date;
- evidence and assumptions;
- validation trigger, owner, and review date.

The ledger is qualitative and prospective. Do not assign universal complexity points or add incomparable obligations into a synthetic total.

## 6. Challenge the First Pass

Run a separate adversarial pass:

- Which requirement, stakeholder, state, dependency, or transition was omitted?
- Did a technology name substitute for outcome evidence?
- Did one control receive credit in multiple dimensions?
- Did absence become an assumed control or a proven defect?
- Did the review hide a high-consequence weak dimension behind broad strengths?
- Is a shared dependency or correlated failure domain missing?
- Would counter-evidence or a different operating context reverse the conclusion?
- Does an independent critical pattern force a block?

For consequential decisions, use an independent reviewer with the same frozen contract and evidence. Compare dimension selection, blocker recall, evidence classification, verdict, and approval conditions. Resolve disagreement through evidence or accountable human judgment.

## 7. Decide Without Fake Precision

- **PASS:** no blocker; every required condition meets its evidence maturity; residual risks are owned.
- **CONDITIONAL:** no blocker; bounded evidence or remediation conditions remain with owner, proof, and review trigger.
- **BLOCK:** a critical blocker exists or a required condition fails.
- **INSUFFICIENT EVIDENCE:** the frame or decisive evidence is too incomplete for a responsible verdict.

Report the vector, blockers, verdict, confidence, and evidence limits separately.

If stakeholders need a numeric summary, first state its decision purpose. Publish its dimensions, mapping, assumptions, and sensitivity to plausible alternatives. Do not require weights to total 100, present a universal pass threshold, average away blockers, rank unrelated architectures by one number, or use the number as the verdict.

## 8. Report Provenance

Distinguish:

- source claims from reviewer inference;
- verified facts from unvalidated claims;
- supporting evidence from counter-evidence;
- evidence absence from evidence contradiction; and
- model/reviewer identity and confidence limits.

Honest uncertainty is more useful than fabricated precision.
