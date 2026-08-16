# Evidence, Complexity, and Architecture Research

Use this reference when an architecture decision depends on a paper, source corpus,
incident set, architecture claim, or conflicting technical guidance. It supplements
the normal workflow; it does not replace the gates in
[`01-workflow-and-decision-gates.md`](01-workflow-and-decision-gates.md).

Treat conclusions in a supplied paper or brief as hypotheses until an independent
source, repository fact, measurement, or validation exercise supports them. Keep the
source's claim separate from the architecture implication inferred from it.

## Contents

- [1. Scope and decomposition](#1-scope-and-decomposition)
- [2. Evidence classes](#2-evidence-classes)
- [3. Atomic claim records](#3-atomic-claim-records)
- [4. Contradiction analysis](#4-contradiction-analysis)
- [5. Complexity accounting](#5-complexity-accounting)
- [6. Dimensional decision matrices](#6-dimensional-decision-matrices)
- [7. Incident learning](#7-incident-learning)
- [8. Experiments and validation](#8-experiments-and-validation)
- [9. Synthesis and stop gates](#9-synthesis-and-stop-gates)
- [10. Reusable resources](#10-reusable-resources)

## 1. Scope and decomposition

Start with the decision, not the technology or the literature list.

1. State the decision horizon, user journey, affected actors, and system boundary.
2. Extract the measurable requirements, invariants, risks, constraints, workload,
   ownership, and failure tolerance that can change the decision.
3. Separate desired outcomes from mechanisms. Treat a queue, service, cache,
   replication scheme, language, or platform as a means whose value must be shown.
4. Break the domain into research questions. For each question, name the decision it
   could change, the evidence needed, and the smallest validation path.
5. List competing options, including preserving the current design or doing less.
6. Mark known facts, estimates, assumptions, and unknowns before collecting sources.

Use the existing workflow's evidence hierarchy and decision-record contract. Research
should reduce a material uncertainty; it should not become a detached literature
summary.

## 2. Evidence classes

Classify every source and state what it can and cannot establish. Authority, recency,
and relevance are separate properties.

| Evidence class | Typical use | Limits to record |
|---|---|---|
| Production measurement | Test a workload, SLO, cost, or failure claim in the target context | Instrumentation, sampling, seasonality, and changed conditions |
| Incident or postmortem | Reconstruct a failure mechanism, containment boundary, and recovery gap | Reporting scope, survivorship, missing counterfactuals, and context mismatch |
| Executable contract, schema, code, or deployment record | Establish what the repository or runtime actually does | Version, environment, generated code, and untested paths |
| Current architecture record or runbook | Establish intended ownership, control, and recovery behavior | Drift between documentation and operation |
| Requirement or stakeholder constraint | Define the target and acceptable trade-off | May be unmeasured, conflicting, or subject to later approval |
| Benchmark, proof of concept, or pilot | Compare options under a declared workload and environment | Representativeness, tuning, duration, and omitted operations |
| Explicit calculation or estimate | Bound capacity, cost, storage, or sensitivity | Assumptions and unit errors; it is not a measurement |
| Formal or theoretical result | Establish a constraint, invariant, or impossibility condition | Model assumptions may not match the deployment |
| Controlled, observational, or survey study | Test a relationship or reported experience | Sampling, confounding, measurement design, and external validity |
| Original system paper or implementation record | Explain why a system chose a mechanism under stated requirements | The original scale and goals may not transfer |
| Official standard or specification | Define protocol behavior, security guidance, or conformance expectations | Guidance is not evidence of a particular outcome magnitude |
| Practitioner synthesis or opinion | Generate a question, option, or hypothesis | Do not use alone to establish a universal rule |

For each material claim, record source type, citation or stable location, study or
operational context, and limitations. Do not turn a correlation into a causal claim,
or a single vendor, project, or incident into universal evidence.

## 3. Atomic claim records

Record one proposition per claim. A document can support several claims, and one claim
can require several sources. Use the
[`architecture evidence map template`](../assets/architecture-evidence-map-template.md)
for a reusable form.

Capture these fields:

| Field | Procedure |
|---|---|
| Claim ID and atomic claim | State the smallest proposition that could be supported, weakened, or rejected. Avoid bundled recommendations. |
| Source type and source | Name the evidence class, author/organization, title, date, and stable citation or repository path. |
| Study design or observation | Identify measurement, experiment, survey, system paper, standard, incident, code inspection, or other method. |
| Scale and applicable context | Record workload, organization, technology, geography, lifecycle stage, and preconditions that matter. |
| Supported finding | State only what the source directly supports; include units or observed behavior where available. |
| Limitations and counter-evidence | Record competing results, omitted cases, confounders, measurement limits, and failure context. |
| Architecture implication | Write the conditional inference separately and name the requirement or risk it serves. |
| Confidence | Use qualitative High, Medium, Low, or Contested with a reason; do not imply a probability or universal validity. |
| Next validation step | Name the repository check, experiment, benchmark, review, drill, or question that could change the decision. |

Label inference explicitly. For example, “the study observed association X in context
Y” is a claim; “therefore choose mechanism Z here” is an architectural hypothesis that
must also fit the local requirements and complexity ledger.

## 4. Contradiction analysis

Treat contradictory guidance as a context and definition problem to investigate, not as
noise to average away.

1. Pair the competing propositions and define terms such as “scalable,” “simple,”
   “autonomous,” or “reliable” before comparing them.
2. Align their requirements, workloads, organizational structures, failure models,
   time horizons, and measurement units.
3. Record the evidence design and limitations for each position.
4. Search for counter-evidence and failure cases, including situations in which each
   position performs poorly.
5. Decide whether the propositions are compatible, conditional on different contexts,
   or genuinely unresolved.
6. Convert an unresolved material difference into an experiment, repository analysis,
   stakeholder decision, or explicit assumption with an owner.

Use a record like this before writing a recommendation:

| Proposition A | Proposition B | Context difference or shared assumption | Evidence and counter-evidence | Conditional conclusion | Next validation |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

Do not resolve a contradiction by selecting the newer, more popular, or more complex
mechanism. Record when the available evidence supports only a conditional statement.

## 5. Complexity accounting

Open a ledger entry for every mechanism that adds a process, network hop, datastore,
queue, control plane, protocol, state machine, trust boundary, deployment unit, or
specialist operating practice. Use the
[`Complexity Ledger template`](../assets/complexity-ledger-template.md).

For each entry:

1. Tie the change to a requirement, invariant, risk, or constraint and name the
   capability gained.
2. Enumerate new concepts, states, protocols, components, interfaces, and data paths.
3. Assign operational responsibility for deployment, monitoring, backup, patching,
   access, incident response, and recovery.
4. List new failure modes, partial-failure behavior, blast radius, and repair paths.
5. Record knowledge, dependency, coordination, and vendor or control-plane effects.
6. Assess performance, security/privacy, resource, sustainability, and cost effects
   with measured quantities where available and labeled assumptions otherwise.
7. State reversibility, migration conditions, expected lifetime, and the point at which
   removal becomes harder.
8. Attach evidence and a validation trigger. Define what observation would show the
   mechanism is unnecessary, insufficient, or ready for removal.

Preserve dimensions instead of adding them into a universal score. Component count is
not a complexity model; a local module can increase cognitive burden, while a service
boundary can reduce one kind of coupling and introduce network, operational, and
coordination burdens. Do not invent synthetic points, ratios, or rankings when the
underlying quantities are not measured.

Avoid duplicating existing contracts: put decision context and reversal in an ADR,
failure behavior in the
[`failure-mode template`](../assets/failure-mode-template.md), economics in the cost
model, and acceptance evidence in the validation plan. The ledger connects these
artifacts and exposes the burden introduced by a decision.

## 6. Dimensional decision matrices

Compare at least two viable options on the dimensions that the requirements make
material. Include a defer/do-less option where it is viable. Do not collapse the rows
into a context-free score.

Use rows such as:

- capability and requirement fit;
- state ownership, transaction, consistency, and recovery semantics;
- runtime distribution, latency, capacity, and overload behavior;
- failure modes, blast radius, and degraded operation;
- deployment cadence, team ownership, and coordination;
- interface, observability, security/privacy, and compliance burden;
- infrastructure, development, vendor, and lifecycle cost;
- knowledge requirements, reversibility, migration path, and expected lifetime;
- evidence available, missing, or contradictory.

For each row, state the consequence and uncertainty, not just a preference. Recommend an
option only conditionally: name the requirements and evidence under which it wins, the
conditions under which another option wins, the owner, and the validation or reversal
trigger. Record the selected scope and consequences in an
[`ADR`](../assets/adr-template.md).

## 7. Incident learning

Use incidents to test architecture assumptions and containment, not to assign a
mechanism a universal reputation. Start with the
[`failure-mode template`](../assets/failure-mode-template.md) and map:

```text
architecture decision → trigger → failure mechanism → blast radius
→ detection → containment/degraded behavior → recovery/reconciliation
→ violated assumption → design or validation change
```

Separate the initiating trigger from contributing conditions and systemic weaknesses.
Identify the affected journey, data and ordering effects, ownership, evidence captured,
and what would have detected the problem earlier. Record missing evidence as unknown;
do not infer causality from timing alone. Add any newly exposed operational, dependency,
security, or coordination burden to the relevant ledger entry and update the validation
trigger or failure drill.

## 8. Experiments and validation

When sources do not resolve a decision, design a bounded validation exercise rather than
substituting opinion.

1. State the unresolved claim and a falsifiable, context-specific hypothesis.
2. Define the decision variable, alternatives, representative workload and data, team
   or operator context, and safety boundary.
3. Predeclare metrics with units, observation window, comparison method, pass condition,
   abort condition, and evidence artifact.
4. Include failure, duplicate, timeout, reordering, migration, restore, security, or
   cost behavior when those dimensions affect the decision.
5. Run the smallest safe repository analysis, benchmark, pilot, fault injection,
   restore drill, or operational review that can change the decision.
6. Record results, uncertainty, threats to validity, and the next step. Do not claim
   generalization beyond the tested context.

Useful experiment shapes include:

- implement equivalent behavior in a modular monolith and independently deployed
  services, then compare change locality, deployment work, fault behavior, observability,
  latency, resource use, and operational cost;
- compare synchronous and asynchronous workflows under timeout, duplicate, reorder, and
  dependency-failure conditions;
- compare a proposed abstraction with deliberate local duplication across representative
  changes, measuring change propagation and maintenance work;
- mine repository co-change, ownership, dependency, and incident data before proposing a
  boundary;
- create a prospective ledger entry and compare predicted burdens with observed operation,
  coordination, incident, and reversal work after a declared review period.

## 9. Synthesis and stop gates

Synthesize each material conclusion in this order:

```text
Claim → Evidence → Counter-evidence/limitations → Applicable context
→ Failure context → Confidence → Conditional architecture implication
→ Next validation
```

Use qualitative confidence labels only with an explanation of source quality,
independence, context fit, and unresolved threats to validity. Keep measured facts,
calculations, assumptions, and inferences visibly distinct. A recent paper, official
guidance, vendor case study, or isolated incident can inform a decision without proving
that its recommendation is universal.

Stop synthesis and return to the workflow when any applicable gate remains open:

- the decision, requirements, invariants, risks, or constraints are not decomposed;
- a claim bundles several propositions or lacks a source class and limitation;
- relevant counter-evidence or failure context was not considered;
- a mechanism lacks a dimensional complexity ledger and accountable owner;
- alternatives, including doing less where viable, were not compared;
- the recommendation has no conditional applicability or validation path;
- a material unknown is hidden behind confidence language or a synthetic score;
- a critical correctness, security, recovery, ownership, or operability gate from the
  workflow is unresolved.

If evidence cannot resolve the issue, state the unknown, ask the highest-value question,
or define the next safe experiment. Do not force a recommendation to make the research
look complete.

## 10. Reusable resources

- [`Complexity Ledger`](../assets/complexity-ledger-template.md) — record capability and
  every material burden introduced by a mechanism.
- [`Architecture Evidence Map`](../assets/architecture-evidence-map-template.md) — keep
  atomic claims, source classes, limitations, context, and validation together.
- [`Complexity Ledger worked example`](../examples/complexity-ledger-example.md) — compare
  a modular monolith with independently deployed services without a universal score.
- [`Order-platform architecture example`](../examples/worked-example-order-platform.md) —
  see how ASRs, ADRs, failure analysis, economics, and validation connect in a larger
  example.
