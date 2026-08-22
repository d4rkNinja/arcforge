# Changelog

## 0.4.2 — 2026-08-22

### Changed

- Completed a reference-corpus integrity audit across all 294 paper artifacts (147 canonical + 147 skill copies) and removed the machine-assembled boilerplate layer: subsections that carried identical rule/failure/evidence blocks regardless of topic, placeholder bullets graded MUST/SHOULD with no content behind them, and wrong-domain text pasted into normative sections (metrics wording inside the cryptography paper, API-pagination rules as queue ordering, sharding guidance under network partitions, cache-expiry text in the TLS, time, lifecycle, idempotency, quota, batch-processing, temporary-data, randomness, M2M-authentication, API-keys, and AI-memory papers). Corpus-wide rule-block duplication dropped from roughly two-thirds of sampled sections to 4.2%, and no paper now carries a majority-duplicated intelligence section.
- Rewrote the implementation-intelligence sections of 30 canonical papers together with their owning skill copies so each subtopic now states a specific engineering rule, its production failure mode, and the codebase evidence to inspect: 064 Cryptography (Argon2id floors per OWASP, NIST SP 800-63B-4 verifier policy, AES-GCM nonce regimes per SP 800-38D, RSA-OAEP/PSS/Ed25519 selection, envelope-encryption failure modes), 065 TLS/PKI (RFC 9325/8996 baselines, chain validation, ACME renewal failure paths, revocation strategy trade-offs, mTLS authorization binding), 063 Secrets Management (workload-identity federation over static credentials, rotation overlap, read auditing), 066 Privacy (pseudonymization versus anonymization under GDPR Art. 4(5)/Recital 26, Art. 17 erasure fan-out with crypto-shredding, k-anonymity limits), 020 Money (ISO 4217 minor-unit exponents, integer overflow arithmetic, penny-splitting allocation), 073 Change Data Capture (snapshot-to-log-position consistency point, replication-slot WAL retention hazards, sink idempotency), 030 Database Migrations (ACCESS EXCLUSIVE queue pileup and lock_timeout guards, CREATE INDEX CONCURRENTLY invalid-index recovery, expand-contract deploy coupling), 052 Retry Engineering (full/equal/decorrelated jitter formulas, retry budgets, amplification arithmetic), 054 Circuit Breakers (state mechanics, half-open probe concurrency, fallback observability), 038 Rate Limiting (token-bucket mathematics, key-dimension selection, fail-open/fail-closed decisions), 098 Distributed Systems Fundamentals (partition semantics replacing sharding paste, FLP motivation, clock-steering hazards), 048 Distributed Transactions (two-phase-commit blocking behavior, saga compensation constraints), 103 Distributed Locks (fencing analysis, compare-and-delete release, renewal ownership checks), 047 Transactional Outbox/Inbox (CDC publishing mechanics, consumer deduplication design), 128 Email Delivery (SPF/DKIM/DMARC mechanics, bounce classification, suppression lists), 129 Notification Infrastructure, 044 Scheduled Jobs (timezone/DST policy, missed-execution semantics), 045 Messaging Queues (per-lane ordering, redelivery reordering), 105 Graceful Shutdown (Kubernetes termination sequence, readiness-flip race, lease-aware worker drain), 106 Deployment Safety, 107 CI/CD (build-once promotion, provenance gates, migration hooks), 140 AI/LLM Fundamentals, 143 RAG Infrastructure (chunking/embedding/reranking/citation discipline), 094 Load and Performance Testing (load/stress/spike/soak/capacity differentiation), 093 Failure Testing (partition-injection semantics), and 096 Scalability (partition-key and skew treatment).
- Removed 169 false-authority invariant blocks that promised topic-specific invariants while containing only template filler, stripped 120 chat-residue clipboard lines from paper 147 and its skill copy, replaced the pasted lock-timeout cell in paper 023 with engine-specific semantics (Postgres statement-scoped `lock_timeout` versus MySQL's default partial rollback), and corrected the S138 citation title to "How to do distributed locking".
- Regenerated `backend-engineering-knowledge-base/manifest.json` hashes, word counts, and byte counts for all 147 papers against current content, and regenerated `MANIFEST.sha256` (455 entries, LF-normalized).

### Compatibility

- No skill ID, frontmatter field, routing map byte, operating mode, output contract heading, or stop condition changed; installation and activation behave exactly as 0.4.1.
- All edits are reference-content corrections inside existing papers and their skill copies. No new shell, network, filesystem, SQL, cloud, or deployment authority was introduced.

### Not verified

- The model-based behavioral evaluation suite (`evals/cases.json`) was not re-run against these reference changes; the cases exercise skill-level routing and gating behavior, which is unchanged, but no fresh trial outputs were recorded for this release.
- Skills CLI discovery (`npx skills add . --list`) passed during development with all seventeen skills found; it was not re-run at the tagged commit.
- Remaining known weakness, unchanged by this release: papers 016 Pagination, 027 Indexing, 010 Multi-Tenancy, 007 Sessions, and 013 Error Architecture still carry correct-but-repetitive subsections awaiting the same rewrite depth.

## 0.4.1 — 2026-08-21

### Added

- Added `using-forge`, the routing entry point. It splits a plain-language request into surfaces (invariant, contract, data, async work, flow control, secret, operations, migration, evidence, runtime, repository), names exactly one owning skill per surface, selects Think, Review, Change, or Verify per step and states the inference, resolves required, recommended, handoff, and optional-depth companions, orders the steps so the owner of an invariant decides before anything derived from it and identity and secrets precede the flows that consume them, writes a receives/owns/produces handoff payload for each step, and names any routed skill that is not installed by its exact technical ID and installation group.
- Added `think-forge`, the read-only routing answer. It returns which skill, which mode, and what order, names the coverage gaps, and stops. Reasoning about likely repository contents is allowed but opening it is not; naming a required check is allowed but running it is not; when the route depends on unknown state the inspection is named as a routed step instead of performed; and when the work is requested in the same sentence it returns the route, states that it does not perform the work, and names the skill and mode that should.
- Added the shared routing map, carried as byte-identical `references/routing-map.md` copies by both routing skills, covering owned surface, positive and negative triggers, exclusions, typed companions, the four modes, the ordering rules, installation groups, and standalone policy for all seventeen skills. The map also carries a Routing layer section giving both routers their own entries, with every field derived literally from the catalog, and a top-level Standing down section stating the four rules that keep the routing layer from adding a step that buys no coverage: confirm-and-hand-off on a settled owner, name the skill directly on a single unambiguous domain whose mode and order are settled, never present a route as approval, review, or release readiness, and never answer the domain question or report a skill as loaded, consulted, or already run.
- Added the `skill-routing` installation group so the routing layer installs on its own, two worked examples (a multi-domain prepaid-checkout route and a route-only answer that refuses an in-line fix), optional Codex interface metadata for each routing skill, and a user guide per routing skill in `docs/skills/`.
- Added four behavioral pressure cases in a new `skill-routing` category, taking the suite from 45 to 49: multi-domain routing coverage and order under deadline pressure with the invariant-owner rule bound to `ARC-CRIT-001`; honest routing when the required depth is not installed, with the readiness claim refused and bound to `ARC-CRIT-009`; a route-only answer that refuses an in-line fix request; and a settled single-domain route that must not be re-derived or padded.

### Changed

- Raised the canonical catalog to 1.2.0 with the routing layer listed first because routing is the entry layer, both entries following the existing schema with `owner_papers: []`, and deliberately asymmetric triggers so the two routers do not compete: `using-forge` claims `route this`, `multi-domain request`, and `companion skills`, `think-forge` claims `route only`, `do not change anything`, `check my plan`, and `second opinion on the route`, and both suppress on `user already named a skill`, `single unambiguous domain`, and `independent approval verdict`.
- Documented routing-map parity discipline in `AGENTS.md`, mirroring the existing paper-reference discipline: the catalog is canonical, the two map copies are derived, they are updated together and confirmed byte-identical, and neither is hand-edited alone.
- Rewrote the README around a three-step start, the two ways in, the four modes, the full skill list grouped by layer, copy-paste prompts per mode, how skills work together, and common questions, with the internal machinery removed from the document.
- Updated `CLAUDE.md` routing and count, `AGENTS.md` file ownership, `skills.sh.json` with a first "ArcForge Routing & Entry Point" grouping, a Routing layer table in `docs/skills/README.md`, evaluation documentation, `VERSION`, and `MANIFEST.sha256` (455 entries, LF-normalized) for seventeen portable skills.

### Compatibility

- Every existing technical skill ID is unchanged; nothing installed against 0.4.0 needs renaming or reinstalling.
- The routing layer is additive and instruction-only: no executable script files and no new shell, network, filesystem, database, or deployment authority. Naming a skill directly still works and skips routing entirely.
- The four operating modes and all fifteen existing skills' instructions, references, and stop conditions are unchanged.

### Not verified

- The model-based behavioral evaluation for the four new routing cases was not run: no baseline or skill-installed runs, no fresh-context trials, and no independent reviewer assessment retained under `evals/results/`. Routing behavior is unproven until that evaluation is recorded.

## 0.4.0 — 2026-08-20

### Added

- Added `git-workflows`, a portable four-mode skill for repository inspection and safe Git change: branch topology, merges, rebases, conflicts, worktrees, distributed ref updates, protected refs, immutable release tags, semantic versions, source-to-artifact provenance, shared-history migration, secret incidents, and recovery.
- Added canonical paper 147, `Production-Grade Git and Git Flow`, plus its portable skill reference, worked example, user guide, catalog routing, and current Git/GitHub/GitLab/SemVer/SLSA source map.
- Added behavioral pressure cases for destructive Gitflow requests, non-fast-forward force pressure, ambiguous push outcomes, exposed signing keys, stale CI, published-tag immutability, and cross-skill release exceptions.

### Changed

- Strengthened `quality-release` with explicit evidence states, exact release-subject binding, cross-skill boundary closure, governed exception records, and non-waivable critical blockers.
- Integrated the new skill with the repository-wide Think, Review, Change, and Verify modes, typed companion relationships, canonical catalog, install grouping, user-first README, guides, and runtime-neutral routing.
- Updated the corpus to 147 papers and the distribution to 15 portable skills, with refreshed manifests, checksums, metadata, behavioral evaluation documentation, and release versioning.

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
