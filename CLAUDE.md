# Claude Code Repository Instructions

Read [`AGENTS.md`](AGENTS.md) as the repository source of truth.

This is a portable Agent Skills repository. Keep the three skills runtime-neutral and do not add native Claude Code plugins, hooks, agents, or a separate harness configuration unless the user explicitly requests a new distribution format.

Route work by skill:

- general system design -> `skills/system-architecture-harness/SKILL.md`;
- LLM, RAG, memory, tools, or agents -> `skills/ai-agent-system-architecture/SKILL.md`;
- architecture review or approval -> `skills/architecture-review-gate/SKILL.md`.

Use the Skills CLI for installation checks and restart Claude Code when a newly created top-level skill directory is not visible in the current session.
