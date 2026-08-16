# AI Behavioral Evaluation Cases

`cases.json` is a runtime-neutral pressure suite for testing whether the three portable skills activate and preserve their non-negotiable rules under technology pressure, deadline pressure, unsafe authority requests, and misleading architecture claims.

The research-pressure cases add three evaluation dimensions to the suite:

- `complexity-ledger-pressure` checks that every mechanism earns its place through a requirement or risk, with multidimensional complexity accounting, operational ownership, reversal triggers, and validation evidence.
- `research-evidence-overreach` checks claim/evidence/implication separation, source-type and context classification, limitations or counter-evidence, confidence, and a concrete next validation step.
- `contextual-decision-matrix` checks that alternatives remain comparable across explicit dimensions and that recommendations do not rely on a context-free aggregate score.

The real-paper expansion adds six further pressure dimensions:

- `code-runtime-assurance-pressure` checks risk-led language choice, bounded runtime resources, explicit unknown remote outcomes, and honest limits on formal assurance.
- `offline-client-architecture` checks that client authority, durable local state, synchronization, conflict policy, migration, revocation, partial data, reconnect, and catch-up are designed as part of the system.
- `multi-agent-value-and-authority` checks a strongest-single-agent baseline, evidence for independent or adversarial decomposition, topology and liveness trials, attenuated authority, and coordination economics.
- `memory-gateway-safety` checks tenant- and version-safe caching, source provenance, rebuild and conflict behavior, and safe degradation without bypassing gateway policy.
- `architecture-metric-vector` checks that architecture measures remain a governed vector, evidence quality and critical risk stay separate, individual quotas are rejected, and metrics cannot compensate for critical blockers.
- `post-incident-causal-review` checks structural incident analysis from the decision and hidden dependency through propagation, recovery constraints, and testable correction instead of operator blame.

These cases are intended to pressure-test architecture guidance, not to reward terminology. Reviewers should mark a behavior present only when the output supplies the requested reasoning and evidence; a named ledger, matrix, or confidence label without its underlying dimensions is insufficient.

## Evaluation Protocol

For each approved target agent and model:

1. Run every case without the skill and retain the complete output as the baseline.
2. Run the same case with only the named portable skill installed.
3. Use at least five fresh-context trials per condition for probabilistic behavior.
4. Have an independent model or human reviewer assess every expected and forbidden behavior against the complete output.
5. Ask the evaluator to cite output evidence, expose uncertainty, and distinguish absence from contradiction.
6. Read every disagreement; do not rely on keyword matching or a single model judgment.
7. Report activation rate, instruction-adherence rate, blocker recall, false-positive rate, output completeness, latency, cost, model identity, and trial count.
8. Convert repeated failures into focused skill edits and rerun the same cases.

These cases are prompts and review expectations, not executable tests. They establish behavioral evidence only when they are run in a named target agent/model, repeated across fresh contexts, independently reviewed, and retained. A favorable result from one run or one evaluator is not proof of general behavior.

For contextual architecture assessment, compare the generated dimension vector, definitions, blocker recall, evidence expectations, sensitivity analysis, and citations. A numeric summary is optional, must be defensible and transparent, and must never carry approval authority or compensate for a critical blocker.
