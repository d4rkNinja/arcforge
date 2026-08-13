# Repository Instructions for Coding Agents

## Purpose

This repository publishes portable Agent Skills and a native AI Harness for production system architecture. Preserve both layers:

- `skills/*/SKILL.md` must remain portable across Agent Skills-compatible runtimes.
- `harness.md` and `.harness/` may use native AI Harness features.

Do not put native-only hook or delegate syntax inside portable skills unless it is clearly optional and isolated in a reference.

## Required Workflow

1. Read the affected `SKILL.md` and linked references completely.
2. Write or update a failing deterministic test before changing behavior.
3. Keep skill frontmatter valid and the directory name equal to `name`.
4. Keep each primary `SKILL.md` at 500 lines or fewer; move deep material into `references/`, reusable forms into `assets/`, and deterministic helpers into `scripts/`.
5. Preserve exact headings `## Output Contract` and `## Stop Conditions`.
6. Run `python scripts/doctor.py` before claiming completion.
7. Read full output and report any unrun native or behavioral verification honestly.

## Architecture Content Rules

- Every decision traces to a requirement, invariant, risk, or constraint.
- Every critical claim has a validation path.
- No unsafe dual writes, floating-point money, unbounded resources, implicit internal trust, gateway-only authorization, backup-without-restore claims, or active-active ambiguity.
- AI systems separate model proposals from policy, permissions, durable truth, verification, and approval.
- A numeric score never waives a critical blocker.

## File Ownership

- General architecture: `skills/system-architecture-harness/`
- AI/agent architecture: `skills/ai-agent-system-architecture/`
- Independent review and scanner: `skills/architecture-review-gate/`
- Native orchestration: `harness.md` and `.harness/`
- Repository verification: `tests/` and `scripts/doctor.py`
- Behavioral cases: `evals/`

## Commands

```bash
python -m pip install -r requirements-dev.txt
python scripts/doctor.py
python -m unittest discover -s tests -p 'test_*.py' -v
python skills/architecture-review-gate/scripts/score_architecture.py tests/fixtures/good-architecture.md --format json
```

## Prohibited Changes

- Do not weaken tests, score thresholds, critical blockers, command guards, or evidence gates to make a change pass.
- Do not commit secrets, provider tokens, personal data, generated caches, extracted archives, or runtime state.
- Do not add undocumented broad shell, network, filesystem, SQL, cloud, or deployment authority.
- Do not claim `harness validate`, Skills CLI discovery, or real-agent evals passed unless they were run in the current change and their output was inspected.
