# GitHub Copilot Repository Instructions

Follow `AGENTS.md`.

This is a dual-format repository: portable Agent Skills under `skills/` and native AI Harness artifacts at the root. Keep portable skills runtime-neutral, use progressive disclosure, preserve frontmatter and output/stop contracts, and add deterministic tests before changing behavior.

Run `python scripts/doctor.py` before proposing completion. Do not weaken architecture blockers or evidence requirements to satisfy tests.
