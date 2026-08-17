# Structured Critical Rules

This directory adds stable, machine-checkable traceability for critical
architectural obligations. It does not replace the canonical papers.

## Field ownership

- `critical-rules.json` owns stable rule IDs, owner-paper anchors,
  applicability, exception policy, evidence requirements, source IDs, and
  evaluation criterion IDs.
- Canonical papers under `../papers/` own explanation, alternatives, failure
  modes, implementation guidance, and verification context.
- `exceptions.json` owns approved, scoped, expiring deviations for rules whose
  `exception_policy.mode` is `structured`.
- The two `*.schema.json` files document the portable JSON contract and the
  cross-file constraints reviewers must inspect.

## Migration discipline

1. Add or change the paper obligation first and review its semantic impact.
2. Add the structured record with an exact statement and section anchor.
3. Attach concrete evidence and stable evaluation criterion IDs.
4. Review the paper anchor, evidence path, exception policy, and linked
   evaluation criterion together.
5. Do not remove existing prose until a semantic comparison proves the
   structured and rendered replacement is equivalent or stronger.

The initial records are `seeded`: they prove the registry, ownership,
exception, evidence, and validator architecture while leaving existing paper
and packaged-skill semantics unchanged. Rendering decision cards or replacing
paper prose is a later, cluster-reviewed migration.

## Exceptions

An exception is never an informal waiver. It requires a rule that explicitly
allows structured exceptions, a narrow scope, reason, accountable owner,
evidence, compensating controls, human or policy-board approval, expiry, and a
review state. AI output or a model-generated score cannot approve or justify an
exception. Rules marked `prohibited` cannot have exception records.
