---
event: tool.pre
priority: -100
when: payload.get("name", "") in ["exec", "run_command", "shell", "bash"]
script: |
  def handle(event, payload):
      args = payload.get("args", {})
      command = str(args.get("command", "")).lower()
      blocked = [
          "rm -rf /",
          "rm -rf /*",
          "git reset --hard",
          "git clean -fd",
          "git push --force",
          "git push -f",
          "mkfs",
          "shutdown",
          "reboot",
          "curl | sh",
          "wget | sh",
          ":(){:|:&};:",
      ]
      for pattern in blocked:
          if pattern in command:
              return block("destructive command blocked by the production architecture harness")
      return allow()
---

# Destructive command guard

This hook blocks common destructive shell patterns before execution. Architecture work is advisory and evidentiary; it does not authorize filesystem destruction, history rewriting, forced pushes, operating-system shutdown, or remote script piping.

The hook complements tool policy. It does not replace sandboxing, least privilege, command review, or human approval for state-changing operations.
