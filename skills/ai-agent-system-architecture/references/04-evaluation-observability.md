# Evaluation and Observability

## Evaluation portfolio

A single score is insufficient. Measure five dimensions:

1. **Correctness** — task result, calculation, extraction, schema, and business invariant.
2. **Groundedness** — evidence relevance, citation, faithfulness, freshness, and abstention.
3. **Safety** — policy, privacy, tenant isolation, injection resistance, and unauthorized action prevention.
4. **Trajectory** — plan adherence, tool choice, arguments, sequencing, retries, and termination.
5. **Performance** — latency, tokens, tool calls, model cost, success-adjusted unit cost, and resource use.

## Dataset design

Keep versioned case families:

- representative normal traffic;
- high-value and rare workflows;
- boundary and ambiguous cases;
- adversarial and indirect prompt injection;
- cross-tenant and privilege tests;
- timeout, duplicate, stale data, and provider outage;
- long-context and memory-conflict cases;
- known production incidents and reviewer escapes.

Store provenance, expected behavior, rubric, severity, and owner. Separate development and holdout cases when optimizing prompts or routing.

## Judge design

Use deterministic checks whenever possible. For model-judged criteria:

- define observable rubric anchors;
- calibrate against human labels;
- measure disagreement and bias;
- use multiple samples for unstable tasks;
- keep safety blockers independent of aggregate scores;
- prevent the candidate from editing the judge, dataset, threshold, or expected answer.

## Release gate

A candidate release report contains:

- candidate and baseline versions;
- dataset revision and slice coverage;
- per-dimension metrics with confidence intervals where meaningful;
- severe regressions and failure examples;
- latency and cost distributions;
- safety blocker count;
- rollout cohort, monitoring window, rollback thresholds, and owner.

## Trace contract

Record correlated, privacy-filtered fields:

- request, session, user/actor pseudonym, and tenant identifiers;
- task/risk classification;
- system/developer prompt and policy version hashes;
- model provider, model, route, parameters, and fallback;
- retrieval query, filters, index and document revisions, source identifiers;
- tool name, validated arguments hash, authorization decision, approval, result status;
- memory reads/writes with scope and provenance;
- verifier scores, deterministic blockers, final decision;
- tokens, latency, retries, queue time, and monetary cost;
- resulting business-state identifier and reconciliation status.

Do not log hidden reasoning. Log decisions, evidence, structured outputs, policy results, and actions.

## Operational signals

Track task success, user correction, abstention, escalation, tool failure, policy blocks, unauthorized attempts, retrieval misses, groundedness, repeated loops, budget exhaustion, provider errors, P95/P99 latency, and cost per successful task. Tie alerts to user impact or safety risk rather than raw model noise.
