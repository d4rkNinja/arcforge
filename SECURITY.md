# Security Policy

## Reporting

Report suspected malicious instructions, unsafe executable behavior, secret exposure, cross-tenant risk, command-guard bypass, or supply-chain concerns through a private GitHub security advisory on the repository after publication. Do not include live credentials, personal data, or exploitable customer information in a public issue.

## Scope

Security-sensitive surfaces include:

- executable scripts under `skills/*/scripts/` and `scripts/`;
- Starlark in `.harness/hooks/`;
- model/tool authority described in skills and delegates;
- installation paths and repository distribution;
- examples that could normalize unsafe production behavior.

## Consumer Guidance

Review skill source before installation, pin trusted commits for production use, run validators in a sandboxed environment, keep provider credentials in secret bindings, and apply least privilege to every agent runtime. Skills are instructions and code, not a security certification.
