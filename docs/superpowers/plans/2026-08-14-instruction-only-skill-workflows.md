# Instruction-Only Skill Workflows Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every ArcForge skill runnable through portable natural-language instructions without requiring Python or another programming-language runtime.

**Architecture:** Keep all existing skill resources and maintainer helpers. Remove executable commands from primary skill workflows, replace them with complete reasoning procedures, and enforce portability with deterministic repository tests.

**Tech Stack:** Markdown Agent Skills, Python repository contract tests, existing package manifest builder.

## Global Constraints

- Keep all three skill packages and all existing supporting files.
- Keep release version `0.1.0`.
- Do not require users or agents to execute Python, shell, JavaScript, or another programming language.
- Preserve the exact `## Output Contract` and `## Stop Conditions` headings.
- Keep maintainer scripts only as non-required repository verification resources.

---

### Task 1: Enforce instruction-only primary skills

**Files:**
- Modify: `tests/test_repository.py`
- Test: `tests/test_repository.py`

**Interfaces:**
- Consumes: every `skills/<name>/SKILL.md`
- Produces: a repository contract rejecting executable language fences and required script commands in primary skill instructions

- [ ] Add a test that scans all primary skill entrypoints for executable language fences and command-shaped references to bundled scripts.
- [ ] Run the repository tests and confirm the new test fails against the current two Python commands.

### Task 2: Replace commands with portable review instructions

**Files:**
- Modify: `skills/system-architecture-harness/SKILL.md`
- Modify: `skills/architecture-review-gate/SKILL.md`
- Modify: `skills/ai-agent-system-architecture/SKILL.md`

**Interfaces:**
- Consumes: existing scorecards, gates, and verification contracts
- Produces: language-independent procedures for evidence scoring, blocker detection, verdict assignment, and completion verification

- [ ] Replace the general architecture validator command with an explicit evidence-by-evidence verification procedure.
- [ ] Replace the review-gate scanner command with explicit weighted scoring, critical-blocker, verdict, confidence, and limitations instructions.
- [ ] Replace code-shaped examples and executable diagram syntax in primary skills with equivalent prose or text instructions.
- [ ] Keep each bundled script named as a maintainer-only resource so package navigation remains complete.
- [ ] Run the focused repository test and confirm it passes.

### Task 3: Align user-facing documentation and package metadata

**Files:**
- Modify: `README.md`
- Modify: `MANIFEST.sha256`

**Interfaces:**
- Consumes: the instruction-only installed-skill contract
- Produces: documentation clearly separating normal skill use from repository maintenance

- [ ] Remove the user-facing architecture scanner command from the README.
- [ ] State that installed skills perform reviews from instructions and do not invoke bundled scripts.
- [ ] Regenerate the source manifest.
- [ ] Run `scripts/doctor.py`, inspect the full output, and confirm all deterministic checks pass.
- [ ] Commit the focused change and push it to `main` with `VERSION` unchanged at `0.1.0`.
