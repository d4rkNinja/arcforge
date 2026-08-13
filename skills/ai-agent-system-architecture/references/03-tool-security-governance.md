# Tool Security and Governance

## Capability design

Expose the narrowest operation that matches the product workflow. A typed domain tool is safer and easier to evaluate than generic shell, SQL, HTTP, browser, filesystem, or cloud-console access.

A tool contract includes:

- stable name and owner;
- exact input and output schema;
- identity, tenant, resource, and action authorization;
- data classification and redaction;
- timeout, rate limit, quota, and payload limit;
- idempotency and duplicate semantics;
- side effect, compensation, and reversibility;
- allowed network, filesystem, secret, and credential scope;
- audit fields and result provenance;
- approval and disable policy.

## Authorization sequence

```text
authenticate caller
→ resolve tenant and acting identity
→ validate structured arguments
→ classify action risk
→ authorize resource + action
→ require approval when policy says so
→ execute with scoped credentials and deadline
→ validate result
→ record tamper-evident evidence
→ reconcile asynchronous effect
```

The model may suggest arguments. It does not create authority.

## Consequence classes

| Class | Examples | Default control |
|---|---|---|
| Read-only public | public search | validation, quota, provenance |
| Read-only protected | customer record | tenant/resource authz, redaction, audit |
| Reversible write | draft, feature flag in test | idempotency, change record, undo |
| Consequential write | refund, permission, production deploy | deterministic policy plus human approval |
| Irreversible/high hazard | deletion, legal filing, security key rotation | two-step confirmation, separation of duties, recovery evidence |

## Command and code execution

When generic execution is unavoidable:

- use an isolated disposable sandbox;
- mount only required paths, preferably read-only;
- deny ambient cloud and production credentials;
- default-deny network egress;
- enforce CPU, memory, process, disk, time, and output limits;
- scan generated dependencies and artifacts;
- block destructive commands in the execution path;
- require review before publishing, deploying, or changing external state.

## Tool-output trust

Tool success does not prove semantic success. Validate status, schema, affected resource, expected postcondition, and duplicate/partial effects. A tool response can contain injection text, stale data, or attacker-controlled fields.

## Secret handling

Pass secrets through scoped runtime bindings, never prompts or durable memory. Redact traces by field classification, not brittle string replacement. Rotate credentials after suspected exposure and preserve an incident audit trail without retaining the secret itself.
