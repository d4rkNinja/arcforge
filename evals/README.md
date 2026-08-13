# Behavioral Evaluation Cases

`cases.json` is a runtime-neutral pressure suite for testing whether the three skills activate and preserve their non-negotiable rules under technology pressure, deadline pressure, unsafe authority requests, and misleading architecture claims.

## Evaluation Protocol

For each approved target agent/model:

1. Run every case without the skill and retain the complete output as the baseline.
2. Run the same case with only the named portable skill installed.
3. Run it through the native harness when that runtime is being adopted.
4. Use at least five fresh-context trials per condition for probabilistic behavior.
5. Score every expected and forbidden behavior manually or with a calibrated evaluator.
6. Read every flagged result; do not rely only on automated keyword counts.
7. Report activation rate, instruction-adherence rate, blocker recall, false-positive rate, output completeness, latency, and cost.
8. Convert repeated failures into focused skill edits and rerun the same cases.

A deterministic repository pass proves package structure and scanner behavior. It does not prove real-agent behavioral uplift.
