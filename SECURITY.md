# Security Policy

## Reporting

Report suspected malicious instructions, unsafe executable behavior, secret exposure, cross-tenant risk, or supply-chain concerns through a private GitHub security advisory after publication. Do not include live credentials, personal data, or exploitable customer information in a public issue.

## Scope

Security-sensitive surfaces include:

- skill instructions, references, examples, and templates;
- installation paths, symlinks/copies, and repository distribution;
- examples that could normalize unsafe production behavior.

## Consumer guidance

Review skill source before installation, pin trusted commits for production use, treat model-generated reviews as advisory evidence, keep provider credentials in secret bindings, and apply least privilege to every agent runtime.

The README installation commands pin the Skills CLI version, not the ArcForge
repository revision. For a production installation, clone an exact reviewed tag
or commit, verify the repository manifest, and install from the local checkout.
The repository's `.gitattributes` keeps text files at LF so the recorded hashes
remain portable across fresh Windows and POSIX checkouts:

```bash
git clone --branch v0.4.1 --depth 1 https://github.com/d4rkNinja/arcforge.git arcforge-0.4.1
cd arcforge-0.4.1
shasum -a 256 -c MANIFEST.sha256
npx --yes skills@1.5.22 add . --skill '*' -a claude-code -a codex --copy -y
```

Review a new release before changing the pinned tag. Do not execute skill output
with broader filesystem, network, shell, database, cloud, or deployment authority
than the requested task requires.

Skills are instructions and reference material, not a security certification. Agent behavior, tool permissions, data access, and approval policies remain the responsibility of the consuming runtime and its operators.
