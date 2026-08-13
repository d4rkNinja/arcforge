# AI, ML, RAG, and Agentic Systems

AI components are probabilistic dependencies inside a deterministic product and risk-management system. Architecture must bound their authority, quality, latency, cost, data exposure, and failure behavior.

## Contents

- 1. Determine Whether AI Is Necessary
- 2. AI System Decomposition
- 3. Requirements and Risk Classification
- 4. Model Gateway
- 5. Prompt and Context Engineering as Configuration
- 6. RAG Architecture
- 7. Agent Architecture
- 8. Human-in-the-Loop
- 9. Memory
- 10. Structured Output and Tool Safety
- 11. Evaluation
- 12. Model and Prompt Release
- 13. Reliability and Fallback
- 14. Cost and Capacity
- 15. AI Security Threats
- 16. Privacy and Governance
- 17. AI Architecture Output Addendum
- 18. Critical Gates
- 19. Common Mistakes

## 1. Determine Whether AI Is Necessary

Define:

- user/business task;
- decision/action produced;
- acceptable errors and harm;
- deterministic/rule/search alternatives;
- required explanation, audit, latency, and cost;
- data availability and rights;
- human oversight;
- fallback when model is unavailable or uncertain.

Use AI when measurable task value exceeds complexity and risk. Do not use an agent where a deterministic workflow is sufficient.

## 2. AI System Decomposition

Separate:

- product/API layer;
- orchestration and policy;
- prompt/context construction;
- retrieval/indexing;
- model gateway/routing;
- tool execution sandbox;
- state/memory;
- safety/guardrails;
- evaluation and feedback;
- telemetry/cost controls;
- human review/approval;
- provider/model lifecycle.

This separation prevents prompts from becoming an unversioned application architecture.

## 3. Requirements and Risk Classification

Capture:

- task success and quality rubric;
- unacceptable output/action classes;
- p50/p95/p99 latency and streaming time-to-first-token;
- cost per successful task and budget;
- throughput/concurrency/token distributions;
- supported languages/modalities;
- freshness and grounding requirements;
- privacy/residency/retention;
- explainability/audit/reproducibility;
- human-review rate and turnaround;
- model/provider availability and fallback;
- high-impact domain obligations.

Classify actions:

| Risk | Example | Default control |
|---|---|---|
| Low | draft, summarize non-sensitive content | user review, basic safety/privacy |
| Medium | recommend or transform business data | grounding, validation, audit, reversible action |
| High | send messages, change production data, spend money | scoped tools, deterministic policy, confirmation/approval, idempotency, audit |
| Critical | safety, rights, financial authorization, identity/security control | specialist governance, strong human authority, independent verification, fail-safe behavior |

## 4. Model Gateway

A model gateway may provide:

- provider/model abstraction;
- authentication and secret isolation;
- policy-based routing by task/risk/latency/cost;
- timeout/retry/circuit breaker/rate limit;
- token and cost accounting;
- structured-output validation;
- prompt/template/version capture;
- safety filters and redaction;
- response caching where semantically safe;
- fallback and provider health;
- telemetry without leaking sensitive content.

Do not hide model-specific capability differences behind a false universal interface. Expose required features and test each route.

## 5. Prompt and Context Engineering as Configuration

- version prompts/templates/system policies;
- separate instructions from untrusted data with clear delimiters/structured fields;
- minimize context and sensitive data;
- define allowed tools/actions outside the model prompt;
- validate structured outputs against schema and business rules;
- regression-test prompt/model combinations;
- record model, prompt, retrieval, tool, policy, and output versions for audits where needed;
- avoid logging raw private context by default.

A prompt is not an authorization boundary.

## 6. RAG Architecture

### Ingestion

```text
source authorization → extraction/parser sandbox → normalize/deduplicate
→ classify/redact → chunk with metadata/ACLs/version
→ embed → vector/index + authoritative document store
→ quality/index validation → publish index version
```

### Query

```text
user/auth/tenant context → query rewrite (optional)
→ retrieve with ACL/tenant filters → rerank/filter/freshness checks
→ construct bounded cited context → model generation
→ output validation/grounding checks → response with provenance
```

### Required decisions

- authoritative sources and freshness;
- parser and file-security boundary;
- chunking strategy and metadata;
- embedding model/version/dimension;
- vector index, filters, tenancy, update/delete;
- hybrid lexical/vector retrieval;
- top-k and reranking;
- ACL enforcement before context reaches model;
- citation/provenance and unsupported-claim behavior;
- index rebuild/migration and backfill;
- evaluation dataset for retrieval and generation separately.

### RAG clauses

- **IF** a user cannot access a source document, **THEN** it must not enter retrieved context.
- **IF** embeddings/index are derived, **THEN** define deletion and rebuild from authoritative content.
- **IF** sources conflict or are stale, **THEN** expose/resolve by policy; do not let model silently decide critical truth.
- **IF** answer must be grounded, **THEN** require evidence/citation coverage and abstain when retrieval is insufficient.

## 7. Agent Architecture

An agent loop should be explicit:

```text
receive goal → authenticate/authorize → create bounded plan/state
→ select allowed action → policy check → tool call with typed input
→ validate result → update state/budget → stop, ask, approve, or continue
→ final validation and audit
```

### Required controls

- allowed tool registry by identity/tenant/task;
- least-privilege credentials and scoped resources;
- typed schemas and validation for tool input/output;
- maximum steps, wall time, tokens, cost, retries, and parallelism;
- idempotency and duplicate-action protection;
- deterministic policy before irreversible actions;
- human approval at defined boundaries;
- sandbox for code/browser/file execution;
- network/egress/domain allowlists;
- memory isolation and retention;
- tamper-evident action log;
- cancellation and safe stop;
- compensation/reconciliation for partial workflows.

### Never grant authority from text

Untrusted webpage, email, document, tool result, or retrieved text can contain instructions. Treat it as data. The model cannot expand its own permissions or bypass policy because content told it to.

## 8. Human-in-the-Loop

Define:

- what requires approval and why;
- information shown to reviewer;
- reviewer identity/role and separation of duties;
- timeout/escalation/cancellation;
- edits and reason codes;
- audit and appeal;
- maximum queue/latency;
- sampling for lower-risk actions;
- emergency stop.

Approval must occur after the final action details are known, not as blanket consent to an open-ended agent.

## 9. Memory

Classify memory:

- conversation/session state;
- user preferences;
- task/workflow state;
- retrieved organizational knowledge;
- episodic agent history;
- derived summaries/embeddings.

Define:

- source and confidence;
- tenant/user isolation;
- write authority and poisoning controls;
- retention, correction, export, deletion;
- sensitive data policy;
- version/provenance;
- retrieval relevance and stale behavior;
- whether memory can authorize actions (normally no).

Do not let model-generated memory become unquestioned truth.

## 10. Structured Output and Tool Safety

- use schemas/enums/ranges rather than free-form tool arguments;
- revalidate server-side;
- resolve resource IDs under authorization;
- preview diff/action and require approval where needed;
- execute through narrow domain APIs, not raw database/shell by default;
- use idempotency keys for side-effecting tools;
- set timeouts, quotas, and circuit breakers;
- sanitize tool outputs before reuse as instructions;
- never expose secrets to model unless strictly required and supported by policy.

## 11. Evaluation

### Evaluation layers

1. **component:** parser, retrieval, classifier, tool adapter;
2. **task:** end-to-end success against representative cases;
3. **safety/security:** prompt injection, data leakage, harmful actions, policy bypass;
4. **operational:** latency, cost, availability, rate-limit behavior;
5. **human:** usefulness, trust, correction burden, accessibility;
6. **production:** sampled/consented feedback, drift, incident and fallback rate.

### Dataset design

- representative normal cases;
- difficult/long-tail/adversarial cases;
- multilingual/format variants;
- tenant/data boundary cases;
- ambiguous cases with desired abstention;
- regression cases from incidents;
- versioned labels/rubrics and reviewer agreement;
- privacy-safe data handling.

### Metrics

Depending on task:

- exact/semantic correctness;
- precision/recall/F1;
- retrieval recall@k and ranking quality;
- grounding/citation coverage;
- hallucination/unsupported claim rate;
- tool selection and parameter correctness;
- policy violation and false refusal rate;
- task completion and human correction rate;
- p95/p99 latency and time to first token;
- cost per successful task;
- fallback/abstention rate.

Use model-based judges only with calibration against human labels and protection against shared bias.

## 12. Model and Prompt Release

Treat model/provider/prompt/retrieval changes as production releases:

- pin/version inputs where possible;
- run offline regression and safety suites;
- compare quality, latency, cost, and refusal;
- shadow/canary by tenant/task/risk;
- monitor with version dimensions;
- define automatic abort and manual review;
- preserve rollback/fallback;
- update documentation and risk assessment;
- reevaluate when provider behavior/terms/data policy change.

## 13. Reliability and Fallback

Failures include provider outage, timeout, rate limit, malformed output, quality regression, retrieval outage, tool error, looping, and unsafe output.

Possible fallback:

- alternate model/provider;
- smaller/local model;
- cached result with freshness label;
- deterministic rule/template/search;
- queue for later processing;
- ask user for clarification;
- abstain and route to human.

Do not automatically retry non-idempotent tool calls. Limit provider retries to the user deadline and cost budget.

## 14. Cost and Capacity

Estimate:

```text
monthly tokens = requests × average input/output tokens × retries/agent steps
model cost = tokens or compute time × route price
retrieval cost = embeddings + index/storage + query/rerank
agent cost = model calls + tool calls + sandbox + human review
unit cost = total / successful completed tasks
```

Model input/output percentiles, context growth, tool loops, cache hit, and fallback. Controls:

- model routing by task/risk;
- context compression and retrieval limits;
- semantic/exact cache where safe;
- batching for embeddings/inference;
- step/token/cost budgets;
- early deterministic filters;
- asynchronous processing;
- unit-cost alerts.

## 15. AI Security Threats

Model:

- direct/indirect prompt injection;
- sensitive information disclosure;
- insecure output handling;
- excessive agency and tool privilege;
- insecure plugin/tool supply chain;
- model/data poisoning;
- vector/embedding cross-tenant leakage;
- denial-of-wallet/resource exhaustion;
- model extraction or membership inference where relevant;
- unsafe code generation/execution;
- misinformation and overreliance;
- memory poisoning and persistence;
- provider/data-retention risk.

Controls must live outside the model where enforcement is required.

## 16. Privacy and Governance

- document model/provider data use and retention;
- minimize and redact inputs;
- obtain purpose/consent where applicable;
- prevent training/reuse when not authorized;
- tenant/region routing and residency;
- deletion across logs, vectors, caches, memory, providers;
- provenance and content labeling where needed;
- incident disclosure and model rollback;
- risk owner and periodic review;
- specialist/legal review for high-impact use.

Use NIST AI RMF/Generative AI Profile and OWASP GenAI guidance as risk references, adapted to the actual use case.

## 17. AI Architecture Output Addendum

Add these sections to the standard output contract:

- task/risk classification and non-AI alternative;
- model/provider selection and routing;
- prompt/context/retrieval architecture;
- tool/agent authority and approval gates;
- data/memory lifecycle;
- evaluation datasets, metrics, and release thresholds;
- safety/security threat model;
- fallback/abstention/human escalation;
- token/accelerator capacity and unit cost;
- model/prompt/index versioning and rollback.

## 18. Critical Gates

Block launch when:

- no representative task and safety evaluation exists;
- high-impact action relies solely on model output;
- untrusted content can grant or expand tool authority;
- tool arguments/actions are not deterministically validated;
- agent has unbounded steps, cost, retries, or side effects;
- tenant/ACL filters are missing before retrieval;
- sensitive data retention/provider use is unknown;
- no fallback/abstention path exists for critical dependency failure;
- model/prompt/index change cannot be identified and rolled back;
- human approval is blanket, pre-authorized, or lacks final action detail.

## 19. Common Mistakes

| Mistake | Correction |
|---|---|
| prompt treated as policy boundary | enforce auth, schemas, quotas, and approvals in deterministic code |
| RAG assumed to eliminate hallucination | evaluate retrieval and grounding; abstain when evidence is insufficient |
| one quality metric | measure task, safety, latency, cost, fallback, and human correction |
| model change deployed like config | version, regress, canary, monitor, and roll back |
| agent given raw shell/database | expose narrow typed domain tools in a sandbox with least privilege |
| all conversation saved as memory | classify, minimize, isolate, correct, expire, and delete |
| AI cost estimated from one prompt | include percentiles, retries, loops, context growth, tools, human review |
| provider abstraction hides capability differences | expose/test task-required features and route explicitly |
