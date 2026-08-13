# Behavioral Evaluation Cases

`cases.json` is a runtime-neutral pressure suite for testing whether the three portable skills activate and preserve their non-negotiable rules under technology pressure, deadline pressure, unsafe authority requests, and misleading architecture claims.

## Evaluation Protocol

For each approved target agent and model:

1. Run every case without the skill and retain the complete output as the baseline.
2. Run the same case with only the named portable skill installed.
3. Use at least five fresh-context trials per condition for probabilistic behavior.
4. Score every expected and forbidden behavior manually or with a calibrated evaluator.
5. Read every flagged result; do not rely only on automated keyword counts.
6. Report activation rate, instruction-adherence rate, blocker recall, false-positive rate, output completeness, latency, and cost.
7. Convert repeated failures into focused skill edits and rerun the same cases.

A deterministic repository pass proves package structure and scanner behavior. It does not prove behavioral uplift in Claude Code, Codex, or another real agent until those runtime trials have been executed and retained as evidence.
