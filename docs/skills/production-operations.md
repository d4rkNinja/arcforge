# Think Through Production Operations (`production-operations`)

Production expertise for running systems: what separates operable systems from hopeful ones — logs without correlation IDs, alerts with no owners, audit trails that can be edited, and backups that have never been restored.

## Modes

- **Think** clarifies requirements, invariants, risks, alternatives, decisions, and validation paths.
- **Review** inspects an existing artifact, repository, diff, or operating state and returns evidence-backed findings.
- **Change** applies approved decisions and keeps verification outstanding until proof is gathered.
- **Verify** reports tests, measurements, operational evidence, and residual risks without inventing missing proof.

If no mode is named, the skill infers one and states it. Combined work proceeds **Think → Review → Change → Verify**.

## What it covers

- structured logging with redaction and correlation IDs;
- metrics, SLI selection, and cardinality limits;
- distributed tracing and context propagation;
- health checks: liveness vs readiness, dependency depth, synthetic probes;
- audit logging: actor, action, target, immutable retention;
- async observability: queue lag, backlog, poison visibility;
- runbooks, escalation, and on-call ownership;
- incident readiness: detection, severity, communication, review;
- data import/export with validation, quarantine, and authorization;
- backup, restore rehearsal, and recovery evidence;
- disaster recovery: RTO/RPO, failover authority;
- high availability, multi-region systems, data residency.

## When to use

Adding telemetry or alerting, writing runbooks, setting up backups or DR, changing regions — and whenever someone says "we take snapshots, so DR is covered" (it is not, and this skill shows what is).

## What a run produces

The output follows the active mode: Think returns decisions and open questions; Review returns findings without claiming changes; Change records the approved work and pending proof; Verify returns observed evidence and explicitly labels unrun checks.

A journey-to-signal map (each user journey → SLI, alert, owner, runbook), restore and failover evidence with observed numbers, and honest blockers where a claim has no drill behind it. The skill stops work on unowned alerts, replication-as-backup claims, or unaudited privileged actions.

## Works well with

- `migration-evolution` for rollout ordering and rollback windows;
- `async-messaging` for the queue semantics being observed;
- `security-privacy` for what must be redacted before emission;
- `quality-release` for the drills that prove the claims.

## Try it

~~~text
Our checkout service goes to production next month. Add the observability it
needs and confirm the DR story — we take daily managed DB snapshots. Use
production-operations.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/production-operations/SKILL.md)
- Worked example: [observability and recovery evidence for a checkout service](../../skills/production-operations/examples/worked-example-checkout-observability.md)
