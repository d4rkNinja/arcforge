# Using Forge

Skill ID: `using-forge`

## What this skill does

The entry point for ArcForge. Describe what you want in your own words and it works out which skill owns the request, which mode that skill should run in, which companion skills the request actually needs, and what order they must run in. Then it hands off and the work begins.

It routes. It does not answer the domain question itself — that belongs to the skill it routes to.

Most requests touch more than one surface. "Add prepaid checkout" is an invariant, a schema, a retry policy, an email, and a readiness claim. Routed to one skill, four of those five get a plausible answer that quietly skips the rest. This skill names all of them first.

## What it covers

- splitting a request into the surfaces it really touches: identity, contract, data, invariant, async work, flow control, secrets, operations, migration, evidence, runtime, repository;
- choosing one owning skill per surface, using explicit exclusions so a skill is never picked on vocabulary that merely appears in passing;
- choosing the mode — **Think** to decide, **Review** to assess what exists, **Change** to apply an approved decision, **Verify** to prove behavior;
- resolving companions by type: required, recommended, handoff, and optional-depth;
- ordering the steps safely: invariants before what derives from them, identity and secrets before the flows that consume them, migration and delivery after the target shape, evidence last;
- writing the handoff payload for each step, so nothing decided early is dropped later;
- naming any skill that is not installed, with its exact ID and installation group, and what the route loses without it.

## When to use

Use it when a request touches production system work and no skill has been named; when a request spans several domains and the full set is not obvious; when the owning skill is clear but the mode is not; when a previous answer covered one domain and skipped an adjacent one; or when part of the depth you need may not be installed.

## When not to use

- You already named a skill — go straight to it.
- One domain plainly owns the request and no companion is in question — invoke that skill directly.
- You want the route only, with nothing inspected or changed — use `think-forge`.
- You want an independent approval verdict — that is `architecture-review-gate`.

## What a run produces

The requested outcome and its surfaces, an ordered route of skill and mode with the reason each skill owns its surface, the companion record by type, receives/owns/produces payloads per step, what the route covers and deliberately does not, the installation status of every routed skill, open questions, and the exact first action.

## Works well with

Every ArcForge skill — that is the point. Most often:

- `system-architecture-harness` and `ai-agent-system-architecture` when the request is whole-system or AI-shaped;
- `architecture-review-gate` as a terminal step when an independent verdict is requested;
- `quality-release` as the closing step on any route that ends in a readiness or completion claim;
- `think-forge` when the answer should stop at the route.

## Try it

```text
Use using-forge. We are adding prepaid checkout: the card is charged up front,
inventory is finite so we cannot oversell, and the customer gets a receipt email.
Which skills own this, in which modes, and in what order?
```

Authoritative instructions: [SKILL.md](../../skills/using-forge/SKILL.md)

Routing map: [ArcForge routing map](../../skills/using-forge/references/routing-map.md)

Worked example: [multi-domain checkout](../../skills/using-forge/examples/worked-example-multi-domain-checkout.md)
