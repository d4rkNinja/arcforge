# Changelog

## 0.3.2 — 2026-08-17

- Renamed every user-facing skill to the approved Think Through or Review name
  while preserving all fourteen stable technical IDs.
- Added explicit Think, Review, Change, and Verify modes to every skill, with
  mode-specific outputs, evidence boundaries, and combined-flow ordering.
- Added typed companion relationships, safe standalone behavior, a canonical
  catalog, and corrected transactional-outbox ownership and review routing.
- Expanded the manual behavioral suite to 42 cases and linked nine critical
  architecture rules to stable review criteria.
- Refined the portable distribution around skills, references, examples,
  metadata, and retained behavioral review evidence.

## 0.3.1 — 2026-08-17

- Added `docs/skills/` — a user-facing guide for every skill (index plus one page per skill: what it covers, when to use it, what a run produces, companion skills, a try-it prompt, and links into the skill), linked from the README.
- Rewrote the README to be user-centric: what each skill does for the user, when to use it, install and invocation examples, and a pick-a-skill routing table — with the internal knowledge-base machinery removed from the document entirely.
- Fixed stale repository documentation after the 0.3.0 expansion: `CLAUDE.md` now routes all fourteen skills (it previously said "the three skills" and omitted the eleven production domain skills), and the README architecture section disambiguated its phrasing before the full rewrite.
- Documented the implementation-suite cases (`impl-*`) in `evals/README.md`, including the co-activation and architecture-boundary cases.
- Re-verified with deeper checks than 0.3.0: YAML parsing of every `SKILL.md` frontmatter and `agents/openai.yaml`, exhaustive markdown link scanning (including paths with spaces or parentheses), in-paper anchor resolution, `skills.sh.json` ↔ skill-directory consistency, README numeric claims, and knowledge-graph paths — all clean.

## 0.3.0 — 2026-08-17

- Added the backend implementation intelligence layer: eleven portable skills that load production implementation papers before code is written (`auth-access`, `api-contracts`, `data-storage`, `transactions-consistency`, `async-messaging`, `resilience-flow-control`, `security-privacy`, `production-operations`, `migration-evolution`, `quality-release`, `runtime-delivery`).
- Packaged all 146 corpus papers into skill references as restructured, self-contained copies: corpus bookkeeping stripped, generator template boilerplate deduplicated (one occurrence per distinct statement), fully-templated subtopics collapsed into a "Default obligations" list, pre-implementation questions and existing-codebase checks moved directly after the executive summary, sections renumbered, same-skill links kept relative, and cross-skill links converted to explicit skill pointers — about 31% smaller per paper with every domain-specific rule, failure mode, and source preserved.
- Folded the code/service boundary papers (084–089) into `system-architecture-harness` and the AI backend papers (140–145) into `ai-agent-system-architecture` instead of creating competing skills.
- Recorded canonical paper ownership, packaged-reference integrity, and checksum coverage across the complete corpus.
- Each production domain skill carries a routing table, a boundary map for co-activation, an `## Output Contract`, and domain `## Stop Conditions`; paper 146 (cross-cutting checklist) lives canonically in `quality-release`.
- Expanded the behavioral suite from 23 to 36 cases: activation-and-rules cases for every production domain skill plus multi-domain co-activation and architecture-boundary redirect cases.
- Added a worked calibration example to every production domain skill (`examples/`) showing the expected output shape: papers consulted, labeled assumptions, initial decision questions, rule-to-decision map, failure modes, verification evidence, and stop-condition check.
- Rewrote the README around the two-layer skill model with explicit display-name/stable-ID naming guidance, complete 14-skill tables, worked-example pointers, and an honest-limits section.
- Updated `skills.sh.json` groupings, `AGENTS.md` ownership and pipeline rules, CI discovery to iterate all skill directories, and the repository README.

## 0.2.0 — 2026-08-16

- Converted the repository to reference-led Agent Skills with portable activation across compatible runtimes.
- Replaced fixed architecture category weights and universal numeric thresholds with a frozen, five-gate evidence vector; any numeric summary is optional, sensitivity-aware, and non-authorizing.
- Added adversarial second-pass review, model disclosure, evidence maturity, Complexity Ledger inspection, structural incident analysis, and governed metric definitions.
- Preserved non-waivable correctness, security, tenancy, recovery, overload, migration, and AI-authority blockers outside aggregation.
- Added architecture-review calibration guidance, strong and critical review inputs, and a complete contextual review example.
- Expanded the behavioral suite with dynamic-rubric and outcome-driven reweighting pressure cases.
- Integrated the supplied architecture manuscript through focused guidance for code/runtime assurance, client and offline systems, platform governance and evolution, classical AI-system obligations, multi-agent value and authority, gateway/memory safety, and post-incident review.
- Aligned the human-facing architecture skill names with Think Through Production Systems, Think Through AI & Agent Systems, and Review Software Architecture while preserving stable installable IDs.
- Consolidated review criteria, calibration resources, and evidence guidance into the portable skill package.
- Enhanced the README with the 0.2.0 architecture, limitations, examples, research provenance, and repeated model-based verification workflow.

## 0.1.0 — 2026-08-13

- Initial ArcForge release as a Skills.sh-compatible multi-skill repository.
- Added dedicated AI/agent architecture and independent architecture-review skills.
- Added critical blocker detection, behavioral evaluation cases, and portable-agent discovery support.
- Preserved detailed system-design references and reusable architecture templates through progressive disclosure.
- Established a portable Agent Skills distribution for Claude Code, Codex, and compatible agents.
- Aligned all skills with the current portable structure: minimal frontmatter, optional Codex UI metadata, explicit trigger boundaries, resource navigation, and reference contents sections.
