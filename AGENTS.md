# Repository Instructions for Coding Agents

## Purpose

This repository publishes portable Agent Skills for production system architecture. It is intentionally skill-only: do not add a native AI Harness configuration, root `harness.md`, `.harness/` delegates, or runtime-specific hooks.

Portable skills live under `skills/*/`. Each skill must remain usable by Claude Code, Codex, and other Agent Skills-compatible runtimes without depending on a vendor-specific control plane.

## Required workflow

1. Read the affected `SKILL.md` and its linked references completely.
2. Add or update a deterministic test or evaluation case before changing observable behavior.
3. Keep skill frontmatter valid and make the directory name equal to the frontmatter `name`.
4. Keep each primary `SKILL.md` at 500 lines or fewer; move deep material into `references/`, reusable forms into `assets/`, and optional deterministic helpers into the skill's own `scripts/` directory.
5. Preserve the exact headings `## Output Contract` and `## Stop Conditions` in each primary skill.
6. Run the maintainer validation command before claiming completion.
7. Read full output and report any unrun agent-specific or behavioral verification honestly.

## Portable skill rules

- Use only the shared Agent Skills frontmatter fields unless a runtime-specific field is clearly optional and isolated.
- Keep portable `SKILL.md` frontmatter to `name` and `description`; place Codex UI metadata in the optional `agents/openai.yaml` file.
- Do not require Python, a provider API key, a native harness CLI, or a particular agent framework for basic skill installation or activation.
- Keep descriptions specific enough for implicit activation and include concrete trigger words.
- Reference supporting files with paths relative to the skill directory.
- Treat scripts as optional helpers; the main workflow must remain understandable from `SKILL.md`.
- Do not put secrets, tokens, personal data, generated caches, or runtime state in the repository.

## Architecture content rules

- Every decision traces to a requirement, invariant, risk, or constraint.
- Every critical claim has a validation path.
- No unsafe dual writes, floating-point money, unbounded resources, implicit internal trust, gateway-only authorization, backup-without-restore claims, or active-active ambiguity.
- AI systems separate model proposals from policy, permissions, durable truth, verification, and approval.
- A numeric score never waives a critical blocker.

## File ownership

- General architecture: `skills/system-architecture-harness/`
- AI/agent architecture: `skills/ai-agent-system-architecture/`
- Independent review and scanner: `skills/architecture-review-gate/`
- Repository documentation: `README.md`, `docs/`, `CONTRIBUTING.md`, and `SECURITY.md`
- Maintainer verification: `tests/` and `scripts/`

## Maintainer commands

End users do not need Python to install or use these skills. Maintainers may run:

```bash
python -m pip install -r requirements-dev.txt
python scripts/doctor.py
python scripts/doctor.py --skills-cli
python skills/architecture-review-gate/scripts/score_architecture.py tests/fixtures/good-architecture.md --format json
npx skills add . --list
```

## Prohibited changes

- Do not reintroduce native harness files, delegates, hooks, or undocumented runtime configuration.
- Do not weaken tests, scanner thresholds, critical blockers, or evidence gates to make a change pass.
- Do not add undocumented broad shell, network, filesystem, SQL, cloud, or deployment authority.
- Do not claim Skills CLI discovery, agent loading, or behavioral evaluations passed unless they were run in the current change and their output was inspected.
