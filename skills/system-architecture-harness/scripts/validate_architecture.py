#!/usr/bin/env python3
"""Provide a deterministic structural review of a Markdown architecture spec.

This validator rewards visible evidence and flags a small set of dangerous
claims. It cannot prove that a design is correct. Use it with expert review,
tests, measurements, threat modeling, and recovery rehearsals.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class Category:
    key: str
    label: str
    weight: int
    checks: tuple[tuple[str, tuple[str, ...]], ...]


@dataclass
class CategoryResult:
    key: str
    label: str
    weight: int
    earned: float
    passed_checks: int
    total_checks: int
    missing: list[str]


@dataclass
class Review:
    file: str
    score: int
    verdict: str
    categories: list[CategoryResult]
    critical_findings: list[str]
    warnings: list[str]
    missing_evidence: list[str]
    strict_pass: bool


CATEGORIES = (
    Category("scope", "Business fit, scope, and evidence", 8, (
        ("decision summary", ("decision summary", "recommendation")),
        ("context and scope", ("context", "scope", "in scope")),
        ("non-goals", ("non-goal", "out of scope")),
        ("constraints", ("constraint",)),
        ("facts/assumptions/evidence", ("assumption", "evidence", "current state")),
    )),
    Category("requirements", "Requirements and ASRs", 8, (
        ("functional requirements", ("functional requirement",)),
        ("architecturally significant requirements", ("architecturally significant", "asr-")),
        ("measurable latency/throughput target", ("p95", "p99", "rps", "requests per second")),
        ("availability/durability target", ("availability", "durability")),
        ("recovery/cost/security target", ("rto", "rpo", "cost", "security")),
    )),
    Category("capacity", "Quantitative workload and capacity", 7, (
        ("workload/capacity model", ("workload", "capacity model")),
        ("average and peak", ("average", "peak")),
        ("concurrency/fan-out/skew", ("concurrency", "fan-out", "skew")),
        ("storage/bandwidth/backlog", ("storage", "bandwidth", "backlog")),
        ("visible calculations and sensitivity", ("calculation", "sensitivity", "breakpoint")),
    )),
    Category("boundaries", "Boundaries, responsibilities, and ownership", 7, (
        ("system context", ("system context",)),
        ("containers/components", ("container", "component responsibilities")),
        ("data/domain ownership", ("owner", "ownership", "source of truth")),
        ("architecture style justification", ("architecture style", "modular monolith", "microservice")),
        ("trust/control/data-plane boundaries", ("trust boundary", "control plane", "data plane")),
    )),
    Category("data", "Data, correctness, and consistency", 12, (
        ("business invariants", ("invariant",)),
        ("state model/transitions", ("state machine", "legal transition")),
        ("authoritative source and transaction boundary", ("source of truth", "authoritative", "transaction boundary")),
        ("consistency/isolation/concurrency", ("consistency", "isolation", "concurrency")),
        ("idempotency and deduplication", ("idempotency", "dedup")),
        ("ordering and conflict semantics", ("ordering", "conflict")),
        ("keys/indexes/partition/skew", ("index", "partition", "skew")),
        ("retention/deletion/backup/restore", ("retention", "deletion", "backup", "restore")),
        ("reconciliation/repair/audit", ("reconciliation", "repair", "audit")),
    )),
    Category("interfaces", "APIs, events, and workflows", 8, (
        ("API contracts", ("api", "synchronous api")),
        ("authentication/authorization/validation", ("authentication", "authorization", "validation")),
        ("errors/versioning/pagination/quotas", ("error", "versioning", "pagination", "quota")),
        ("deadlines/timeouts/retries", ("deadline", "timeout", "retry")),
        ("event schema/key/delivery", ("event", "schema", "delivery")),
        ("retention/replay/DLQ/quarantine", ("replay", "dead-letter", "dlq", "quarantine")),
        ("success and failure sequence", ("success", "failure", "sequence")),
    )),
    Category("performance", "Performance, scalability, overload, and cost efficiency", 8, (
        ("latency budget", ("latency budget",)),
        ("scaling plan and limits", ("scaling plan", "safe limit")),
        ("hot spots/skew", ("hot spot", "hot key", "skew")),
        ("bounded resources/admission control", ("admission", "bounded", "concurrency limit")),
        ("backpressure/load shedding/degraded mode", ("backpressure", "load shedding", "degraded mode")),
        ("load/burst/soak validation", ("load test", "burst", "soak")),
    )),
    Category("reliability", "Reliability, resilience, and disaster recovery", 12, (
        ("SLIs/SLOs", ("sli", "slo")),
        ("error-budget action", ("error budget", "burn")),
        ("failure matrix", ("failure matrix", "failure mode")),
        ("timeouts and bounded retries", ("timeout", "bounded retries", "maximum attempts")),
        ("degradation and containment", ("degraded", "containment")),
        ("RTO/RPO", ("rto", "rpo")),
        ("backup and tested restore", ("backup", "restore", "drill")),
        ("failover/fencing/split-brain", ("failover", "fencing", "split-brain")),
        ("recovery/reconciliation", ("recovery", "reconciliation")),
    )),
    Category("security", "Security, privacy, abuse, and compliance", 12, (
        ("threat model and trust boundaries", ("threat", "trust boundary")),
        ("human/workload identity", ("identity", "workload identity")),
        ("resource/action authorization", ("authorization", "resource", "action")),
        ("tenant isolation", ("tenant isolation", "cross-tenant")),
        ("secrets and encryption/key lifecycle", ("secret", "encryption", "key", "rotation")),
        ("abuse/rate/egress/input controls", ("abuse", "rate limit", "egress", "input validation")),
        ("privacy lifecycle", ("privacy", "minimization", "retention", "deletion")),
        ("audit and incident response", ("audit", "incident")),
        ("compliance/specialist handoff", ("compliance", "legal", "specialist")),
    )),
    Category("operations", "Observability and operations", 8, (
        ("logs/metrics/traces", ("logs", "metrics", "traces")),
        ("business/correctness signals", ("business signal", "correctness", "reconciliation mismatch")),
        ("alerts tied to impact", ("alert", "user", "burn")),
        ("runbooks and escalation", ("runbook", "escalation")),
        ("ownership/on-call/service catalog", ("owner", "on-call", "service catalog")),
        ("telemetry cardinality/retention/privacy", ("cardinality", "retention", "sensitive data")),
    )),
    Category("delivery", "Delivery, migration, and evolution", 5, (
        ("build/deploy/IaC/supply chain", ("deploy", "infrastructure as code", "iac", "provenance")),
        ("progressive rollout and gates", ("progressive", "canary", "rollout")),
        ("compatibility and versioning", ("compatibility", "versioning")),
        ("rollback/roll-forward", ("rollback", "roll-forward")),
        ("data migration/backfill/cutover", ("migration", "backfill", "cutover")),
    )),
    Category("economics", "Cost, sustainability, and organization", 3, (
        ("cost drivers and unit economics", ("cost driver", "unit cost", "unit economics")),
        ("budget/quota controls", ("budget", "quota")),
        ("build/buy/lock-in/exit", ("build vs buy", "lock-in", "exit path")),
        ("team ownership/cognitive load", ("team", "cognitive load", "on-call")),
    )),
    Category("decisions", "Decision quality and validation", 2, (
        ("alternatives and trade-offs", ("alternative", "trade-off")),
        ("ADR/reversal trigger", ("adr", "reversal trigger")),
        ("risks/open questions", ("risk", "open question")),
        ("validation plan and implementation slices", ("validation plan", "implementation slice")),
    )),
)

assert sum(category.weight for category in CATEGORIES) == 100


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def phrase_present(text: str, alternatives: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in alternatives)


def line_is_negated(line: str, term: str) -> bool:
    before = line[: line.find(term)] if term in line else line
    return bool(re.search(r"\b(?:no|not|never|without|avoid|forbid(?:den)?|prohibit(?:ed)?|must not)\b[^.]{0,50}$", before))


def critical_checks(raw: str, text: str) -> tuple[list[str], list[str]]:
    critical: list[str] = []
    warnings: list[str] = []

    money_float = re.search(
        r"(?:money|amount|price|balance|currency|payment)[^.\n]{0,100}\b(?:float|double|floating[ -]point)\b|"
        r"\b(?:float|double|floating[ -]point)\b[^.\n]{0,100}(?:money|amount|price|balance|currency|payment)",
        raw,
        flags=re.IGNORECASE,
    )
    if money_float:
        line = raw.splitlines()[raw[: money_float.start()].count("\n")]
        if not line_is_negated(line.lower(), "float") and "exact" not in line.lower():
            critical.append("Money or financial values appear to use floating-point arithmetic; require integer minor units or fixed-precision decimal and explicit currency semantics.")

    for line in raw.splitlines():
        lower = line.lower()
        for match in re.finditer(r"\bunbounded\s+(queue|retry|retries|fan-out|concurrency|batch|cache|connection|buffer|cardinality)", lower):
            prefix = lower[: match.start()]
            if not re.search(r"\b(?:no|not|never|without|avoid|forbid(?:den)?|prohibit(?:ed)?|must not)\b[^.]{0,50}$", prefix):
                critical.append(f"Unbounded resource claimed: {match.group(0)}. Define a hard bound, admission/backpressure behavior, and overload outcome.")

    exactly_once_denial = re.search(
        r"(?:do not|don't|does not|doesn't|no need to|without)\s+(?:need\s+)?(?:consumer\s+)?idempot",
        text,
    )
    if "exactly once" in text and (("idempot" not in text and "transaction" not in text) or exactly_once_denial):
        critical.append("End-to-end exactly-once is claimed without idempotent or transactional effect semantics.")

    if "dual write" in text and not any(term in text for term in ("outbox", "change data capture", "cdc", "reconciliation", "two-phase", "2pc")):
        critical.append("Cross-system dual writes are mentioned without an atomic publication protocol or reconciliation path.")

    if re.search(r"(?:cache|redis)\s+(?:is|as|becomes)\s+(?:the\s+)?(?:source of truth|authoritative)", text):
        critical.append("A cache appears to be authoritative; define durable ownership and recovery or redesign it as a derived view.")

    has_backup = any(term in text for term in ("backup", "snapshot"))
    denies_restore_test = bool(re.search(
        r"(?:do not|don't|does not|doesn't|no need to|without|skip)\s+(?:need\s+to\s+)?(?:test|restore|drill|rehears)",
        text,
    ))
    if has_backup and (denies_restore_test or not any(term in text for term in ("restore", "recovery drill", "restore drill", "rehears"))):
        critical.append("Backups/snapshots are described without a tested restore or recovery rehearsal.")

    if "active-active" in text and not ("conflict" in text and any(term in text for term in ("fencing", "ownership", "routing", "quorum"))):
        critical.append("Active-active multi-region is proposed without both conflict semantics and ownership/fencing/routing controls.")

    if re.search(r"(?:internal (?:service|traffic|network)|vpc)[^.]{0,100}(?:trusted|trust)", text) and not any(
        term in text for term in ("zero trust", "workload identity", "service identity", "mutual tls", "mtls")
    ):
        critical.append("Internal network location is treated as sufficient trust without workload identity and service authorization.")

    if re.search(r"(?:only|solely)[^.]{0,60}(?:gateway|edge)[^.]{0,60}authoriz", text) or re.search(
        r"authoriz[^.]{0,60}(?:only|solely)[^.]{0,60}(?:gateway|edge)", text
    ):
        critical.append("Authorization appears to exist only at the gateway/edge; resource and action authorization must be enforced at the owning service boundary.")

    queue_terms = any(term in text for term in ("queue", "broker", "event stream", "message bus"))
    if queue_terms:
        missing = [
            label
            for label, present in (
                ("delivery semantics", any(term in text for term in ("at-least-once", "at-most-once", "delivery semantics"))),
                ("deduplication/idempotency", any(term in text for term in ("dedup", "idempot"))),
                ("replay/retention", "replay" in text and "retention" in text),
                ("backpressure/bounds", any(term in text for term in ("backpressure", "bounded", "capacity"))),
                ("poison-message handling", any(term in text for term in ("dead-letter", "dlq", "quarantine", "poison"))),
            )
            if not present
        ]
        if len(missing) >= 3:
            warnings.append("Messaging is present but several semantics are missing: " + ", ".join(missing) + ".")

    if "retry" in text:
        retry_missing = [
            label
            for label, present in (
                ("timeout/deadline", any(term in text for term in ("timeout", "deadline"))),
                ("bounded attempts/budget", any(term in text for term in ("bounded", "maximum attempts", "max attempts", "retry budget"))),
                ("backoff/jitter", "backoff" in text and "jitter" in text),
                ("idempotency", "idempot" in text),
            )
            if not present
        ]
        if len(retry_missing) >= 2:
            warnings.append("Retries are mentioned without enough safety evidence: " + ", ".join(retry_missing) + ".")

    if any(term in text for term in ("llm", "ai agent", "agentic", "model tool", "tool call")):
        ai_missing = [
            label
            for label, present in (
                ("evaluation", "evaluation" in text or "eval" in text),
                ("least-privilege tools", "least privilege" in text or "least-privileged" in text),
                ("human approval for high-impact actions", "approval" in text or "human" in text),
                ("execution budgets", "budget" in text and any(term in text for term in ("token", "step", "time", "cost"))),
                ("audit/provenance", "audit" in text or "provenance" in text),
            )
            if not present
        ]
        if len(ai_missing) >= 3:
            warnings.append("AI/agent behavior is present but governance evidence is incomplete: " + ", ".join(ai_missing) + ".")

    if any(term in text for term in ("payment", "wallet", "balance", "ledger", "trade")):
        if not any(term in text for term in ("integer minor", "fixed-precision", "decimal", "exact arithmetic")):
            warnings.append("A financial domain is present without an explicit exact numeric representation.")
        if not any(term in text for term in ("reconciliation", "double-entry", "immutable journal", "immutable ledger")):
            warnings.append("A financial domain is present without explicit ledger/journal or reconciliation controls.")

    return list(dict.fromkeys(critical)), list(dict.fromkeys(warnings))


def score_categories(text: str) -> tuple[list[CategoryResult], list[str]]:
    results: list[CategoryResult] = []
    missing_evidence: list[str] = []
    for category in CATEGORIES:
        passed = 0
        missing: list[str] = []
        for label, alternatives in category.checks:
            if phrase_present(text, alternatives):
                passed += 1
            else:
                missing.append(label)
        earned = category.weight * passed / len(category.checks)
        results.append(CategoryResult(
            key=category.key,
            label=category.label,
            weight=category.weight,
            earned=round(earned, 1),
            passed_checks=passed,
            total_checks=len(category.checks),
            missing=missing,
        ))
        if earned < category.weight * 0.6:
            missing_evidence.append(f"{category.label}: " + ", ".join(missing))
    return results, missing_evidence


def review_file(path: Path, strict_threshold: int = 80) -> Review:
    raw = path.read_text(encoding="utf-8")
    text = normalize(raw)
    categories, missing_evidence = score_categories(text)
    score = round(sum(item.earned for item in categories))
    critical, warnings = critical_checks(raw, text)

    core_keys = {"requirements", "data", "reliability", "security"}
    weak_core = [item.label for item in categories if item.key in core_keys and item.earned < item.weight * 0.5]
    if weak_core:
        warnings.append("Core architecture categories below 50% evidence: " + ", ".join(weak_core) + ".")

    if critical:
        verdict = "BLOCK"
    elif score >= 90:
        verdict = "PASS"
    elif score >= 75:
        verdict = "CONDITIONAL"
    else:
        verdict = "REVISE"

    strict_pass = not critical and score >= strict_threshold and not weak_core
    return Review(
        file=str(path),
        score=score,
        verdict=verdict,
        categories=categories,
        critical_findings=critical,
        warnings=warnings,
        missing_evidence=missing_evidence,
        strict_pass=strict_pass,
    )


def print_text(review: Review) -> None:
    print(f"Architecture document: {review.file}")
    print(f"Score: {review.score}/100")
    print(f"Verdict: {review.verdict}")
    print("\nCategory evidence:")
    for item in review.categories:
        print(
            f"- {item.label}: {item.earned:g}/{item.weight} "
            f"({item.passed_checks}/{item.total_checks} checks)"
        )
    if review.critical_findings:
        print("\nCritical findings:")
        for finding in review.critical_findings:
            print(f"- {finding}")
    if review.warnings:
        print("\nWarnings:")
        for warning in review.warnings:
            print(f"- {warning}")
    if review.missing_evidence:
        print("\nLowest-evidence categories:")
        for finding in review.missing_evidence:
            print(f"- {finding}")
    print("\nStrict gate: " + ("PASS" if review.strict_pass else "FAIL"))
    print("Note: this is a structural evidence check, not an architecture correctness certificate.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("architecture", help="Markdown architecture document")
    parser.add_argument("--strict", action="store_true", help="return non-zero when the strict gate fails")
    parser.add_argument("--threshold", type=int, default=80, help="strict score threshold, default 80")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    path = Path(args.architecture).expanduser().resolve()
    if not path.is_file():
        print(f"error: architecture document not found: {path}", file=sys.stderr)
        return 2
    if path.suffix.lower() not in {".md", ".markdown"}:
        print("warning: validator is optimized for Markdown headings and prose", file=sys.stderr)
    if not 0 <= args.threshold <= 100:
        print("error: --threshold must be between 0 and 100", file=sys.stderr)
        return 2

    review = review_file(path, args.threshold)
    if args.format == "json":
        print(json.dumps(asdict(review), indent=2, sort_keys=True))
    else:
        print_text(review)

    if args.strict and not review.strict_pass:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
