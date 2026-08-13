# Source Map and Provenance

Accessed during package creation on 2026-08-13. These links are provided for attribution and deeper verification. The skill is an original synthesis; source text is not reproduced.

## Requested and Mapped Repository

- Requested fork: https://github.com/d4rkNinja/system-design-notes
- Accessible 28-chapter source used for chapter mapping: https://github.com/liquidslr/system-design-notes

The accessible repository states that its notes are based on *System Design Interview — An Insider’s Guide*, volumes 1 and 2, and marks the notes as work in progress. The skill therefore treats the repo as a pattern source, not a complete production standard.

## Agent Skills Format

- Agent Skills project: https://github.com/agentskills/agentskills
- Specification: https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx
- Website: https://agentskills.io/

Used for the folder structure, `SKILL.md` metadata, progressive disclosure, relative references, and validation expectations.

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
