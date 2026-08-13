# Claude Code Instructions

Read and follow [`AGENTS.md`](AGENTS.md) as the repository source of truth.

Route work by artifact:

- general system design → `skills/system-architecture-harness/SKILL.md`;
- LLM, RAG, memory, tools, or agents → `skills/ai-agent-system-architecture/SKILL.md`;
- architecture review or approval → `skills/architecture-review-gate/SKILL.md`;
- native AI Harness orchestration → `harness.md` and `.harness/`.

Use tests first for behavior changes and run `python scripts/doctor.py` before a completion claim. Treat delegate or agent output as untrusted until artifacts and fresh verification evidence are inspected.
