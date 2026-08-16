# Source Map and Provenance

Accessed during package creation and the 0.2.0 evidence-led review on 2026-08-16;
the Research-mode and current AI sources below were independently verified on
2026-08-16. These links are provided for attribution and deeper verification. The
skill is an original synthesis; source text is not reproduced.

## Contents

- Supplied Research Input
- Independently Verified Research Sources
- Requested and Mapped Repository
- Agent Skills Format
- Architecture Quality and Documentation
- Reliability and SRE
- Security and Privacy
- AI and Agentic Risk
- APIs, Events, and Telemetry
- Cost and Sustainability
- Source-Use Rules

## Supplied Research Input

Two architecture-research texts were supplied during this change. The later, broader
August 2026 manuscript supersedes the earlier decomposition brief as the primary input.
It includes an abstract, 36 sections, appendices, and 79 references, but the supplied
text does not expose author, exact title, publisher, stable identifier, or repository
metadata that this repository can independently verify. It is therefore recorded as a
**user-supplied research manuscript**, not presented as a published or peer-reviewed
source merely because its formatting is complete.

Its methods and durable conclusions are reflected as reviewable repository behavior:
measurable quality scenarios; state and invariant ownership; boundaries purchased for
named capabilities; explicit partial-failure and recovery semantics; dimensional
complexity accounting; code/runtime and client-platform decisions; lifecycle cost and
reversibility; AI authority separation; claim-centric evidence; structural incident
analysis; and governed metric vectors. Individual citations are classified and scoped
separately before supporting an external factual claim.

## Independently Verified Research Sources

- Google Research (2025), [*Understanding Architectural Complexity, Maintenance Burden, and Developer Sentiment -- A Large-Scale Study*](https://research.google/pubs/understanding-architectural-complexity-maintenance-burden-and-developer-sentiment-a-large-scale-study/)

The publication reports analysis of more than 1,200 C++ and Java projects and 7,200
survey responses, with statistical correlations among structural complexity measures,
maintenance activity, and developer sentiment. This is evidence about the reported
study population and measures; it does not establish universal causation. Project and
language selection, metric definitions, confounding factors, organizational context,
and transferability to another system remain limitations to record before applying the
finding.

ArcForge uses this source only to support measuring complexity, maintenance activity,
and developer experience as dimensions to investigate when they are relevant to a
decision. It does not set an architecture threshold, prove that one architecture style
causes a universal outcome, or justify a synthetic complexity score. Local requirements,
invariants, ownership, incidents, measurements, and validation remain authoritative
for a specific architecture decision.

The following current primary sources cited by the supplied manuscript were also
verified on 2026-08-16:

- NIST CAISI (2025, updated 2025), [*Strengthening AI Agent Hijacking Evaluations*](https://www.nist.gov/news-events/news/2025/01/technical-blog-strengthening-ai-agent-hijacking-evaluations). It supports adaptive, repeated, task-specific agent-security evaluation; it does not prove that a prompt-only defense is sufficient.
- NIST CAISI (2026), [*Request for Information About Securing AI Agent Systems*](https://www.nist.gov/news-events/news/2026/01/caisi-issues-request-information-about-securing-ai-agent-systems). This is an RFI identifying threats and research questions, not a finalized standard or validated architecture recipe.
- NIST NVD (2026), [CVE-2026-27966](https://nvd.nist.gov/vuln/detail/CVE-2026-27966). The record documents prompt injection reaching an enabled Python execution tool in affected Langflow versions; it is a concrete failure example, not evidence that every agent framework has the same flaw.
- Google Research / ICLR 2026, [*Multi-Agent Design: Optimizing Agents with Better Prompts and Topologies*](https://research.google/pubs/multi-agent-design-optimizing-agents-with-better-prompts-and-topologies/). It reports results for the paper's evaluated tasks and search method. ArcForge treats multi-agent topology optimization as emerging, context-dependent evidence and still requires comparison with a strong single-agent baseline.

## Requested and Mapped Repository

- Requested fork: https://github.com/d4rkNinja/system-design-notes
- Accessible 28-chapter source used for chapter mapping: https://github.com/liquidslr/system-design-notes

The accessible repository states that its notes are based on *System Design Interview — An Insider’s Guide*, volumes 1 and 2, and marks the notes as work in progress. The skill therefore treats the repo as a pattern source, not a complete production standard.

## Agent Skills Format

- Agent Skills project: https://github.com/agentskills/agentskills
- Specification: https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx
- Website: https://agentskills.io/
- Best practices: https://agentskills.io/skill-creation/best-practices

Used for the required `SKILL.md` contract, metadata, progressive disclosure, focused relative references, optional resources, examples, and the recommended primary-file size. ArcForge 0.2.0 intentionally implements its behavior through instructions and on-demand reference material.

## Architecture Quality and Documentation

- AWS Well-Architected Framework pillars: https://docs.aws.amazon.com/wellarchitected/latest/framework/the-pillars-of-the-framework.html
- AWS Well-Architected overview: https://docs.aws.amazon.com/wellarchitected/latest/userguide/waf.html
- C4 model: https://c4model.com/
- C4 system context: https://c4model.com/diagrams/system-context
- C4 container diagram: https://c4model.com/diagrams/container
- C4 dynamic diagram: https://c4model.com/diagrams/dynamic
- C4 deployment diagram: https://c4model.com/diagrams/deployment
- Architectural Decision Records: https://adr.github.io/
- Markdown ADR template family: https://adr.github.io/madr/

Used for cross-cutting quality coverage, audience-appropriate diagrams, deployment views, and decision records.

## Reliability and SRE

- Google SRE book — Service Level Objectives: https://sre.google/sre-book/service-level-objectives/
- Google SRE workbook — Error Budget Policy: https://sre.google/workbook/error-budget-policy/
- Google SRE book — Embracing Risk: https://sre.google/sre-book/embracing-risk/
- Google SRE book — Service Best Practices: https://sre.google/sre-book/service-best-practices/

Used for user-focused SLIs/SLOs, error budgets, actionable alerting, and balancing reliability with change.

## Security and Privacy

- NIST SP 800-207 Zero Trust Architecture: https://csrc.nist.gov/pubs/sp/800/207/final
- NIST Secure Software Development Framework: https://csrc.nist.gov/projects/ssdf
- OWASP Top 10: https://owasp.org/Top10/
- OWASP API Security: https://owasp.org/API-Security/
- OWASP Cheat Sheet Series: https://cheatsheetseries.owasp.org/

Used for identity/resource-centric trust, secure development, API threats, and threat/control verification.

## AI and Agentic Risk

- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI RMF 1.0: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
- NIST Generative AI Profile: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- NIST SP 800-218A announcement: https://csrc.nist.gov/News/2024/nist-publishes-sp-800-218a
- OWASP GenAI/LLM security project: https://owasp.org/www-project-top-10-for-large-language-model-applications/

Used for trustworthy AI lifecycle, evaluation/governance, secure model-system development, prompt injection, excessive agency, and data/tool risk.

## APIs, Events, and Telemetry

- OpenAPI Specification: https://spec.openapis.org/oas/latest.html
- AsyncAPI documentation: https://www.asyncapi.com/docs
- CloudEvents: https://cloudevents.io/
- IETF RFC 9457 Problem Details for HTTP APIs: https://www.rfc-editor.org/rfc/rfc9457.html
- OpenTelemetry signals: https://opentelemetry.io/docs/concepts/signals/
- OpenTelemetry specification: https://opentelemetry.io/docs/specs/otel/

Used for contract-first APIs/events, portable event envelopes, machine-readable HTTP errors, and correlated traces/metrics/logs.

## Cost and Sustainability

- FinOps Framework capabilities: https://www.finops.org/framework/capabilities/
- AWS Well-Architected cost optimization and sustainability pillars (via the framework link above).

Used for unit economics, allocation, budgets, anomaly detection, ownership, and resource efficiency.

## Source-Use Rules

- Prefer primary standards, official documentation, research papers, and original project sources.
- Verify version/date before relying on rapidly changing standards.
- Treat vendor guidance as an input, not a universal requirement.
- Adapt every pattern to the system’s requirements, domain, team, and risk.
- Do not copy proprietary book text or present this skill as formal compliance certification.
