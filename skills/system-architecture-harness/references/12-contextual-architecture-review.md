# Contextual Architecture Evidence Review

Use this reference after the design is complete enough to challenge. The active AI model creates a decision-specific evidence vector from the architecture context; it does not apply fixed categories, mandatory weights, or universal score thresholds.

## Contents

- Review contract
- Five-gate evidence-vector generation
- Evidence assessment
- Critical gates
- Complexity, adversarial, and independent passes
- Verdict and report structure

## Review Contract

Record the decision being gated, maturity horizon, owners, critical journeys, ASRs, invariants, data and tenant boundaries, failure impact, constraints, supplied evidence, missing evidence, and specialist-review limits.

The same architecture can require different evidence for exploration, implementation approval, migration cutover, or production launch. State the decision before creating the review frame.

## Five-Gate Evidence-Vector Generation

Before judging the proposal:

1. Derive applicable dimensions from the decision, requirements, invariants, risks, transition state, and evidence needs.
2. Organize applicable dimensions under five gates: problem/fitness; state/boundaries; failure/assurance; delivery/operation; economics/complexity/evolution.
3. For each selected dimension, define why it applies, what strong evidence looks like, what partial evidence looks like, what failure looks like, and what proof is expected.
4. Define the condition protected and minimum evidence maturity for this decision horizon.
5. Define context-specific pass, conditional, block, and insufficient-evidence conditions. Do not import a universal numeric threshold.
6. List excluded dimensions with reasons.
7. Publish and freeze the evidence vector before assessing the design.

If later evidence reveals a missing requirement, version the review frame and explain the change. Never silently reshape dimensions to improve the result.

## Evidence Assessment

For each dimension:

- cite exact evidence and location;
- classify it as observed, validated, implemented, designed, claimed, inferred, contradicted, or missing;
- compare it with the frozen evidence anchors;
- explain the finding and evidence quality without forcing incomparable dimensions into points;
- identify uncertainty or conflicting evidence; and
- state the smallest proof or remediation needed.

Do not award credit for headings, document length, fashionable technology, vendor claims, or author confidence. Do not double-count one control across unrelated dimensions.

## Critical Gates

Critical gates are evaluated independently from strengths elsewhere or any optional numeric summary. Any unresolved applicable gate blocks approval.

### Correctness and data

- A critical invariant lacks atomic or serialized enforcement and reconciliation.
- Money uses binary floating point or lacks currency and rounding semantics.
- A cross-system dual write lacks transactional coordination or explicit repair.
- Source of truth, ownership, idempotency, duplicate behavior, or migration safety is ambiguous.
- Data, queues, retries, fan-out, pools, or concurrency are unbounded.

### Reliability and recovery

- Critical remote calls lack deadlines or retries can amplify failure without bounds.
- Exclusive state can have multiple active writers without ownership and fencing.
- Required RTO/RPO has no implementable and exercised recovery path.
- Replication is treated as backup or restore/key recovery has not been exercised.
- The system cannot remain bounded under overload.

### Security, privacy, and tenancy

- Sensitive objects or actions lack server-side authorization.
- Tenant isolation is not enforced at data access and derived stores.
- Secrets or sensitive data are exposed in code, logs, prompts, or clients.
- Untrusted input can trigger unrestricted network, file, shell, or tool access.
- Data retention, deletion, residency, or a known critical control failure cannot be addressed.

### Operations and change

- A critical service has no owner, telemetry, incident path, or recovery responsibility.
- A deployment or migration lacks compatibility and rollback or roll-forward.
- A major operational claim has no validation owner or proof path.

### AI and agents

- Model output alone authorizes a high-impact action.
- Tool authority can expand from untrusted text or lacks server-side validation.
- Steps, tokens, cost, retries, delegation, or side effects are unbounded.
- Retrieval or memory lacks authorization and tenant isolation.
- Model, prompt, policy, tool, or index versions cannot be identified and rolled back.
- No representative quality and safety evaluation exists for the gated decision.

## Complexity, Adversarial, and Independent Passes

Inspect the Complexity Ledger for capability gained, alternatives, introduced concepts/state/protocol/configuration/dependencies, operational responsibility, failure modes, knowledge, security, performance, cost, reversibility, expected lifetime, evidence, validation trigger, owner, and review date. Report its absence.

After the first assessment, run a separate model pass that tries to disprove it. Look for omitted risks, proposal-friendly dimensions, unsupported inference, missing evidence treated as implementation, double counting, hidden dependencies, and deadline bias.

For consequential decisions, prefer an independent second reviewer or model using the same frozen review contract. Compare dimensions, blocker recall, evidence classification, verdict, and approval conditions. Model agreement does not replace the accountable human decision owner.

## Verdict

- **PASS:** no critical blocker; frozen context-specific conditions are met; evidence maturity is sufficient for this decision.
- **CONDITIONAL:** no critical blocker; named evidence or remediation conditions remain with owners and proof.
- **BLOCK:** a critical blocker exists or a required context-specific condition fails.
- **INSUFFICIENT EVIDENCE:** the context cannot support a defensible review frame or verdict.

The evidence vector, verdict, blockers, confidence, and evidence maturity are separate fields. If stakeholders request a numeric summary, require a named decision purpose, transparent mapping and assumptions, sensitivity analysis, and the full vector beside it. The number is optional and never approval-bearing.

## Report Structure

```markdown
# Architecture Review

## Verdict
- Decision gated:
- Verdict:
- Confidence:
- Model/version:
- Optional numeric summary and decision purpose (omit when not defensible):

## Five-Gate Evidence Vector
| Gate | Dimension | Protected condition | Evidence state/quality | Finding | Required proof |

## Critical Findings
| ID | Evidence | Failure mechanism | Impact | Required condition | Owner |

## Evidence and Assumptions
| Claim | Source claim / reviewer inference | Evidence maturity | Counter-evidence or gap | Next proof |

## Complexity Ledger Review

## Adversarial and Independent Challenge

## Approval Conditions
| Condition | Owner | Proof | Review trigger |

## Positive Evidence to Preserve
```

## Review Conduct

- Review requirements before implementation conclusions.
- Challenge claims, not people.
- Preserve working choices and avoid novelty bias.
- Separate defects, evidence gaps, risks, and preferences.
- Require evidence proportionate to impact.
- Record accepted risk and accountable authority explicitly.
- Never let an aggregate or optional number waive a critical issue.
