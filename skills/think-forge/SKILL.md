---
name: think-forge
description: "Use when the question is which ArcForge skill to use and in what order, and nothing should be inspected, changed, or implemented yet: name the owning skill, the mode, the sequence, and the coverage gaps, then stop. Answers where do I start, which skill covers this, which mode should this run in, what order should these run in, and is anything missing. Read-only by contract. Use using-forge when the route should carry companion contracts and continue into the work."
---

# Think Forge

Answers one question: which ArcForge skill, in which mode, in what order.

It reads the request, names the route, and stops. It does not inspect the repository, run commands, change files, or produce the domain answer.

**Core principle:** A route is useful before the work starts. Deciding the route and doing the work in the same breath removes the moment where the user can correct the route.

## Routing Law

```text
THIS SKILL RETURNS A ROUTE AND NOTHING ELSE:
1. no file is created, edited, or deleted;
2. no command, migration, deployment, or repository operation runs;
3. no domain decision is made on the owning skill's behalf;
4. no skill is described as loaded, consulted, or already run;
5. the answer ends at the route, even when the fix looks obvious.
```

## When to Use

Use this skill when:

- the question is where to start, which skill covers this, or what order these should run in;
- a request spans several domains and the user wants the map before committing to work;
- a route needs a second opinion before an expensive or risky sequence begins;
- the user wants to know whether anything in a request has no owner, or needs a skill that is not installed;
- a plan already exists and the question is only whether the skill selection and order are right.

## When Not to Use

- When the route should carry companion contracts, handoff payloads, and continue into the work, use `using-forge`.
- When the user already named a skill and wants the work done, go to that skill. Do not spend a turn confirming a settled route.
- When one domain plainly owns the request and neither the mode nor the order is in question, name that skill directly. Routing a single unambiguous request adds a step and no coverage.
- When the user wants the design, the review, the change, or the evidence, route to the owning skill instead of answering here.
- When an independent approval verdict is wanted, that is `architecture-review-gate`.

## Required Reference

Read [ArcForge routing map](references/routing-map.md) before naming a route. It carries the owning domain, triggers, exclusions, and companions for every skill. Route from that map, not from a skill name that merely sounds related.

## Read-Only Boundary

This skill's value depends on stopping where it says it stops.

- Reasoning about what a repository probably contains is allowed; opening it to find out is not.
- Naming the check that should run is allowed; running it is not.
- Saying which skill owns a decision is allowed; making that decision is not.
- If the request cannot be routed without inspecting state, say exactly what must be inspected and which skill and mode should inspect it. That unresolved dependency is the answer.
- If the user asks for the work as well, return the route, state plainly that this skill does not perform the work, and name the skill and mode that should take it. Do not silently widen into the work.

A route delivered alongside an unrequested change destroys the review point the user asked for.

## Routing Workflow

1. **Restate the outcome** in one sentence, in the user's terms.
2. **Split it into surfaces.** A single sentence often carries several: identity, contract, data, invariant, async work, flow control, secret, operations, migration, evidence, runtime, repository.
3. **Name one owner per surface** from the ownership table. Match the real subject, not passing vocabulary. Check the exclusions column.
4. **Name the mode** for each step: Think to decide, Review to assess what exists, Change to apply an approved decision, Verify to prove behavior.
5. **Order the steps.** Invariants before what derives from them; identity and secrets before the flows that consume them; migration and delivery after the target shape; evidence last.
6. **Name the gaps.** Any surface with no clear owner, any skill not installed, and anything that cannot be routed without inspection.
7. **Stop.** Emit the output contract and end the turn.

## Domain Ownership Table

| The request is really about | Owner | Do not route here for |
|---|---|---|
| Whole-system boundaries, decomposition, workload, scale, topology, rewrite | `system-architecture-harness` | An independent approval verdict; an AI control plane |
| LLM, RAG, memory, model routing, tool use, agent authority, evaluation | `ai-agent-system-architecture` | Non-AI architecture; an approval verdict |
| An independent verdict on an existing RFC, ADR, design, or plan | `architecture-review-gate` | Owning greenfield design; making repository changes |
| Login, sessions, tokens, OAuth, MFA, API keys, permissions, tenancy | `auth-access` | General API shape; choosing cryptographic primitives |
| Endpoints, validation, errors, pagination, versioning, webhooks, SDKs | `api-contracts` | Queue internals; migration sequencing; authentication policy |
| Schemas, identifiers, money, time, indexes, files, search, lifecycle | `data-storage` | Isolation levels; migration sequencing; cache mechanics |
| Transactions, locking, idempotency, sagas, replication, sharding, ordering | `transactions-consistency` | Queue delivery mechanics; retry pacing; schema design |
| Jobs, workers, queues, events, outbox, batch, email, notifications | `async-messaging` | Isolation levels; retry pacing alone; public webhook contract |
| Caches, rate limits, quotas, retries, timeouts, breakers, backpressure | `resilience-flow-control` | Queue delivery semantics; transaction locking |
| Secrets, encryption, TLS, hashing, sensitive data, redaction, abuse, randomness | `security-privacy` | Owning the login flow; owning the request contract |
| Logs, metrics, tracing, health, audit, runbooks, backup, restore, DR, regions | `production-operations` | Deployment sequencing; owning sensitive-data policy |
| Schema and contract evolution, backfills, compatibility, CDC, cutover, legacy | `migration-evolution` | Designing a new contract; CI tooling; a rewrite decision |
| Test strategy, concurrency and failure evidence, load, release readiness | `quality-release` | Independent architecture approval; owning SLOs |
| Bootstrap, configuration, pools, networking, shutdown, deploy gates, CI/CD | `runtime-delivery` | Schema semantics; owning telemetry; owning retry policy |
| Branches, merges, refs, protected refs, tags, versions, history, Git recovery | `git-workflows` | Deployment implementation alone; test strategy alone |

When two owners both fit a surface, the owner of the **invariant** leads and the other follows as a companion. When no owner fits, say so and name the closest owner plus what it will not cover, rather than forcing a match.

## Missing Skill Honesty

When a routed skill is not installed, name its exact technical ID and the installation group that provides it, and state which part of the request loses coverage. Never present an uninstalled skill as available or already consulted, and never drop a surface from the route because the skill that owns it is missing — an unowned surface is a finding.

## Output Contract

1. **Outcome** — the request in one sentence, and the surfaces it touches.
2. **Route** — an ordered table of step, skill, mode, and why that skill owns that surface.
3. **Companions** — skills the owners will pull in, and what triggers each.
4. **Gaps** — surfaces with no clear owner, skills not installed, and anything that needs inspection before it can be routed.
5. **Not covered here** — the plain statement that this skill returns the route only, and the skill and mode that should perform the work.

## Stop Conditions

Stop and revise when any of these appears:

- a file was created, edited, or deleted;
- a command, migration, deployment, or repository operation ran;
- the answer contains the domain decision, the design, the review verdict, or the evidence;
- a skill is described as loaded, consulted, or already run;
- the turn continues into the work after the route is stated;
- an obvious-looking fix was applied because it was quick;
- state was inspected in order to route, instead of naming the inspection as a routed step;
- a surface was dropped from the route because no skill was installed for it;
- the user already named a skill and the answer re-litigates that choice without a stated reason;
- the route is presented as approval, review, or readiness.

## References

- [ArcForge routing map](references/routing-map.md)

## Worked Example

- [Returning a route only when the user also asked for the fix](examples/worked-example-route-only-answer.md)
