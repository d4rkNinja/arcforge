# Think Through Runtime & Delivery (`runtime-delivery`)

Production expertise for the layer every feature stands on: configs that validate nowhere and break at boot in production, pools that exhaust under bursts, shutdowns that drop in-flight work, and deploys that skip migration ordering.

## Modes

- **Think** clarifies requirements, invariants, risks, alternatives, decisions, and validation paths.
- **Review** inspects an existing artifact, repository, diff, or operating state and returns evidence-backed findings.
- **Change** applies approved decisions and keeps verification outstanding until proof is gathered.
- **Verify** reports tests, measurements, operational evidence, and residual risks without inventing missing proof.

If no mode is named, the skill infers one and states it. Combined work proceeds **Think → Review → Change → Verify**.

## What it covers

- project structure, bootstrap, dependency initialization ordering;
- configuration: hierarchy, schema validation, typed access, reload, rollback;
- connection pools and their saturation behavior;
- networking behavior that services actually depend on: keepalives, DNS;
- load balancing with health-gated traffic; service discovery;
- service-to-service communication, identity, and fallbacks;
- graceful startup/shutdown: signals, drain deadlines, cleanup ordering;
- deployment safety: ordering, health gates, rollback windows;
- CI/CD pipelines, artifact promotion, environment parity;
- infrastructure configuration and provisioning.

## When to use

Changing configuration loading, bootstrap, pools, shutdown handling, deploy ordering, or pipelines — and before accepting ".env straight into process.env, ops will hand-edit production."

## What a run produces

The output follows the active mode: Think returns decisions and open questions; Review returns findings without claiming changes; Change records the approved work and pending proof; Verify returns observed evidence and explicitly labels unrun checks.

Runtime behavior defined across every failure window — boot, reload, burst, shutdown, deploy — with enforcement points (validated config schemas, bounded pools, drain deadlines, health gates) and drills for each. The skill stops work on unvalidated stringly config, secrets bundled into config files, or deploys without rollback windows.

## Works well with

- `migration-evolution` for migration ordering inside deploys;
- `production-operations` for health/readiness emitter design;
- `resilience-flow-control` for inter-service retry and timeout policy;
- `security-privacy` for config secret storage and rotation.

## Try it

~~~text
Load all settings from a .env file straight into process.env with no
validation. Ops will hand-edit production values. Use runtime-delivery.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/runtime-delivery/SKILL.md)
- Worked example: [fail-fast configuration and graceful shutdown](../../skills/runtime-delivery/examples/worked-example-validated-config.md)
