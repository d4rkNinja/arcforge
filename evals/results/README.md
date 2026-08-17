# Evaluation Results

Behavioral trials are evidence records, not executable tests. Copy
`result.template.json` for each trial, preserve the complete raw output at the
referenced path, compute its SHA-256 digest, and record the runtime/model identity
exactly as reported by the runtime.

Use `status: "unrun"` with a concrete `unrun_reason` when the required runtime,
model, credentials, or reviewer is unavailable. Never convert an unavailable
trial into a pass. For completed trials, record every criterion outcome and every
reviewer disagreement; a favorable aggregate result cannot waive a critical
criterion or critical rule.

Before reporting results, compare the record with
`../schema/results.schema.json`, inspect case and criterion references, and
confirm the complete raw output and recorded SHA-256 digest. Templates are not
counted as trials.
