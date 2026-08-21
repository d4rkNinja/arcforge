# Think Forge

Skill ID: `think-forge`

## What this skill does

Answers one question: which ArcForge skill, in which mode, in what order. Then it stops.

Nothing is opened, changed, or run. You get the route, the companions each owner will pull in, and the gaps — and you get to correct the route before any work starts. That review point is the whole value, so this skill is read-only by contract.

## What it covers

- restating the outcome in your terms and splitting it into the surfaces it touches;
- naming one owning skill per surface, checking the exclusions so a near-miss skill is not picked;
- naming the mode for each step: Think, Review, Change, or Verify;
- ordering the steps so nothing is decided before the thing it depends on;
- naming the companions each owner will bring in, and what triggers them;
- naming the gaps: surfaces with no clear owner, skills that are not installed, and anything that cannot be routed without inspecting state — which it names as a routed step instead of doing.

## When to use

Use it when the question is where do I start, which skill covers this, or what order should these run in; when you want the map before committing to expensive or risky work; when a plan already exists and you only want the skill selection and order checked; or when you want to know whether any part of a request has no owner.

## When not to use

- You want the route to carry companion contracts and continue into the work — use `using-forge`.
- You already named a skill and want the work done — go to that skill.
- You want the design, the review, the change, or the evidence — go to the owning skill.
- You want an independent approval verdict — that is `architecture-review-gate`.

## What a run produces

The outcome in one sentence with its surfaces, an ordered route of step, skill, mode, and why that skill owns that surface, the companions the owners will pull in, the gaps, and a plain statement that this skill returns the route only plus the skill and mode that should perform the work.

If you also ask for the fix, you still get the route, plus a plain statement that the fix belongs to the routed step. It will not quietly widen into the work.

## Works well with

- `using-forge` when the route is agreed and should carry handoff payloads into the work;
- the owning skill named in the route — that is where the request goes next;
- `architecture-review-gate` when the ask turns out to be an independent verdict rather than a route.

## Try it

```text
Use think-forge. Our nightly backfill keeps dying halfway and leaves duplicate
rows. Which skills cover this, in which modes, and in what order? Route only.
```

Authoritative instructions: [SKILL.md](../../skills/think-forge/SKILL.md)

Routing map: [ArcForge routing map](../../skills/think-forge/references/routing-map.md)

Worked example: [route-only answer](../../skills/think-forge/examples/worked-example-route-only-answer.md)
