# Worked example: configuration that fails at boot, not at 3 a.m.

> Calibration artifact: this shows the shape and depth a run of the `runtime-delivery` skill should produce. It is illustrative, not exhaustive; the papers remain authoritative.

**Request (as a user would phrase it):**

> Load all settings from a .env file straight into process.env with no validation. Ops will hand-edit production values.

## Papers consulted

- [002 Configuration Management](../references/papers/002-configuration-management.md) — hierarchy, validation, reload
- [001 Project & Runtime Foundations](../references/papers/001-project-and-runtime-foundations.md) — bootstrap ordering
- [105 Graceful Shutdown](../references/papers/105-graceful-shutdown.md) — drain and cleanup
- 063 Secrets Management — in the `security-privacy` skill
- [106 Deployment Safety](../references/papers/106-deployment-safety.md) — health-gated rollout of config changes

## Assumptions (labeled)

- **A1 (assumption):** the service is stateless behind a load balancer; restart to reload config is acceptable outside incidents. *If false:* hot-reload semantics and partial-application rules are required (paper 002).
- **A2 (assumption):** secrets arrive via the platform's secret store, not files. *If false:* the secret-loading path changes, validation stays identical (paper 063 pointer).

## Pre-implementation questions answered

- **Why is the request rejected as stated?** Unvalidated stringly config fails at first use in production, hand-edits drift silently, and secrets in `.env` leak via images, backups, and shells (papers 002, 063 MUST).
- **Validation contract?** Typed schema: every variable declared with type, range, default, and required-per-environment; invalid or missing config fails the process at boot with an actionable message (paper 002 MUST).
- **Hierarchy?** Defaults < file < environment < secret store, documented once; no environment-only magic values (paper 002).
- **Hand-edit replacement?** Changes go through the deploy pipeline as config commits or secret-store updates; rollout is health-gated and rollback is a config revert (papers 002, 106).
- **Shutdown behavior?** SIGTERM drains in-flight requests within a 20 s deadline, closes pools and queue publishers, and exits non-zero on failed cleanup (paper 105).

## Rule-to-decision map

| Rule (level) | Decision | Enforcement point | Verification |
|---|---|---|---|
| Schema-validated config (MUST) | Typed loader, fail-fast at boot | Bootstrap step 1 | Missing/invalid var: process exits with named-variable error |
| Secret separation (MUST) | Secrets from secret store, never `.env`/image | Loader source rules | Image and repo scans: zero secrets |
| Documented hierarchy (SHOULD) | Defaults < file < env < secret store | Config module | Override test per level |
| Health-gated config rollout (SHOULD) | Config changes deploy like code with revert path | Pipeline gate | Bad value in staging blocks promotion |
| Graceful shutdown (MUST) | Drain deadline, resource cleanup, ordered dependency close | Signal handler | Kill -TERM under load: 0 dropped requests within deadline |

## Failure modes addressed

- Typo'd production port discovered at traffic time — boot-time failure instead.
- Drifting hand-edited values — pipeline-managed config with history.
- Secrets in images/repos — source separation plus scans.
- Dropped requests on deploys — drain deadline verified under load.

## Verification evidence

- Boot test matrix: missing required, wrong type, out-of-range, unknown variable (warn), each with the expected behavior.
- Shutdown drill under synthetic load: zero 5xx, clean pool close, deadline respected.
- Scan: no secret-shaped strings in image layers or repo history for the config paths.

## Stop-condition check

No stop condition remains: validation enforced at boot, secrets separated, failure windows (boot/reload/shutdown/deploy) each stated and tested, rollout gated.

## Deliverable summary

Typed config module with fail-fast schema, secret-store wiring, pipeline-managed config changes, graceful-shutdown handler, and the boot/shutdown test matrix. Secret-store operations route to `security-privacy`.
