# Think Through Security & Privacy (`security-privacy`)

Production expertise for protective controls. Controls attach to data and actions, not layers: every secret, sensitive field, and privileged action has a lifecycle — generation, use, rotation, redaction, deletion — enforced somewhere concrete.

## Modes

- **Think** clarifies requirements, invariants, risks, alternatives, decisions, and validation paths.
- **Review** inspects an existing artifact, repository, diff, or operating state and returns evidence-backed findings.
- **Change** applies approved decisions and keeps verification outstanding until proof is gathered.
- **Verify** reports tests, measurements, operational evidence, and residual risks without inventing missing proof.

If no mode is named, the skill infers one and states it. Combined work proceeds **Think → Review → Change → Verify**.

## What it covers

- secrets management: storage, injection, rotation, scoping, audit;
- encryption at rest and in transit; key management;
- TLS configuration, certificate verification, rotation;
- cryptography primitive selection, nonce/IV handling, password hashing;
- sensitive-data classification, minimization, retention, deletion propagation;
- log/trace/error redaction and export controls;
- abuse protection: brute force, credential stuffing, enumeration, scraping, fraud;
- feature-flag safety and kill switches;
- temporary and expiring data (sessions, tokens, uploads, exports);
- randomness and token generation done with real entropy.

## When to use

Handling secrets or sensitive fields, configuring TLS/crypto, adding redaction, defending against abuse, generating tokens or IDs — and especially requests like "log request bodies including passwords to debug this."

## What a run produces

The output follows the active mode: Think returns decisions and open questions; Review returns findings without claiming changes; Change records the approved work and pending proof; Verify returns observed evidence and explicitly labels unrun checks.

An asset/actor/boundary map, controls with enforcement points, and negative tests (secret absent, verification on, deletion reached). The skill stops work on secrets in logs or config by default, home-grown crypto, disabled certificate verification, or sensitive data with no deletion path.

## Works well with

- `auth-access` for the flows that use these controls;
- `api-contracts` for validation and error leakage at the surface;
- `resilience-flow-control` for abuse-driven rate limiting;
- `production-operations` for audit events and alerting.

## Try it

~~~text
Debug auth failures by logging full request bodies including passwords at
info level. Use security-privacy.
~~~

## Where to look

- Skill instructions: [SKILL.md](../../skills/security-privacy/SKILL.md)
- Worked example: [debugging without leaking credentials](../../skills/security-privacy/examples/worked-example-secrets-and-redaction.md)
