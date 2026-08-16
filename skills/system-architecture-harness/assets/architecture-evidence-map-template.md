# Architecture Evidence Map

Use one row or record for each atomic claim that can change an architecture decision.
Keep the source finding separate from the architectural implication. Use qualitative
confidence with a rationale; do not treat it as a probability or a decision score.

See the [`evidence and complexity reference`](../references/15-evidence-complexity-and-research.md)
and connect a resulting decision to the [`ADR template`](adr-template.md).

## Source or corpus identity

Complete this block once per source, study, repository corpus, incident set, or dataset
before extracting claims. Do not infer publication status or independence from polished
formatting.

- Source ID: <stable local identifier>
- Exact title / corpus name: <preserve the source's identity>
- Author, organization, or custodian: <who produced or maintains it>
- Publication status: <peer reviewed / standard / preprint / internal / user supplied / unknown>
- Version, revision, and publication/access date: <what was actually inspected>
- Stable identifier or location: <DOI, canonical URL, repository commit, artifact, or attachment>
- Funding, affiliation, and declared conflicts: <reported facts or unknown>
- Independence / relationship to other sources: <shared authors, data, vendor, or derivation>
- Study or corpus context: <research question, system/domain, population, time period, geography>
- Sampling and scope: <units, sample size, inclusion/exclusion, missing data, survivor/selection limits>
- Method and comparison: <formal result, experiment, observation, survey, case study, synthesis, incident analysis>
- Measures and definitions: <units, outcomes, proxies, baselines, uncertainty and analysis method>
- Transfer limits: <conditions that differ from the target architecture>
- Verification status: <independently checked facts, unresolved identity, or user-provided only>

## Claim record

- Claim ID: <stable identifier>
- Atomic claim: <one proposition that could be supported, weakened, or rejected>
- Source type: <choose one class from the taxonomy; if none fits, document the mismatch and seek review>. See the [Evidence classes](../references/15-evidence-complexity-and-research.md#2-evidence-classes).
- Source: <author or organization, title, date, repository path, or stable citation>
- Source / corpus ID: <link to the identity block above>
- Citation or evidence location: <URL, section, query, commit, dashboard, or artifact>
- Study design or observation method: <how the finding was established>
- Scale and applicable context: <workload, data, organization, technology, geography, and lifecycle conditions>
- Supported finding: <what the source directly establishes; preserve units and scope>
- Limitations / counter-evidence: <competing findings, omitted cases, confounders, failure context, and threats to validity>
- Failure context: <conditions under which the claim may not hold or may cause harm>
- Architecture implication: <conditional inference tied to an ASR, invariant, risk, or constraint>
- Confidence: <High / Medium / Low / Contested — give a short reason>
- Next validation step: <repository check, experiment, benchmark, review, drill, or question that could change the decision>
- Notes and provenance: <interpretation kept separate from the source's words>

## Evidence map table

For several claims, copy the record above into a table and keep the limitations visible.

| Claim ID | Atomic claim | Source type and source | Supported finding | Limitations / counter-evidence | Applicable and failure context | Architecture implication | Confidence and reason | Next validation step |
|---|---|---|---|---|---|---|---|---|
| <C-001> | <...> | <...> | <...> | <...> | <...> | <...> | <...> | <...> |

## Synthesis check

- Requirement or decision affected: <ASR, invariant, risk, or constraint>
- Independent sources or measurements: <which claims corroborate or disagree>
- Unresolved unknown: <what remains unverified>
- Owner: <accountable person or team>
- Review trigger: <new evidence, incident, workload change, or date>
