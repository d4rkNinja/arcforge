#!/usr/bin/env python3
"""Deterministic structural scoring for Markdown architecture specifications.

This tool checks whether evidence is visible and flags a small set of dangerous
claims. It does not prove architectural correctness, security, compliance, or
operational readiness. Expert review and fresh runtime evidence remain required.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Category:
    key: str
    label: str
    weight: int
    checks: tuple[tuple[str, tuple[str, ...]], ...]


CATEGORIES: tuple[Category, ...] = (
    Category(
        "scope",
        "Scope, outcomes, and evidence",
        10,
        (
            ("decision summary", ("decision summary", "recommendation")),
            ("scope and non-goals", ("scope", "non-goal", "out of scope")),
            ("actors and critical journeys", ("actor", "critical journey", "user journey")),
            ("constraints and owners", ("constraint", "decision owner", "owner")),
            ("facts, assumptions, and evidence", ("fact", "assumption", "evidence", "unknown")),
        ),
    ),
    Category(
        "requirements",
        "Requirements and workload",
        10,
        (
            ("architecturally significant requirements", ("asr", "architecturally significant", "p99", "availability")),
            ("latency and availability targets", ("latency", "p95", "p99", "availability")),
            ("recovery targets", ("rto", "rpo")),
            ("capacity model", ("capacity model", "requests/s", "rps", "writes/s")),
            ("peak, concurrency, and growth", ("peak", "concurrent", "growth", "storage")),
            ("load validation", ("load test", "soak", "burst", "backlog drain")),
        ),
    ),
    Category(
        "boundaries",
        "Boundaries and ownership",
        10,
        (
            ("architecture options", ("options and trade-offs", "compared", "alternative")),
            ("architecture style rationale", ("modular monolith", "microservices", "serverless", "architecture style")),
            ("component responsibilities", ("module", "component", "service")),
            ("data ownership", ("own their data", "data ownership", "source of truth", "authoritative")),
            ("trust and authorization boundaries", ("trust boundary", "server-side boundary", "authorization")),
        ),
    ),
    Category(
        "data",
        "Data and correctness",
        15,
        (
            ("business invariants", ("invariant", "cannot become negative", "must never")),
            ("authoritative source", ("authoritative", "source of truth")),
            ("transactions and isolation", ("transaction", "isolation", "atomic")),
            ("concurrency control", ("optimistic concurrency", "version column", "lock", "concurrency")),
            ("idempotency and deduplication", ("idempotency", "dedup")),
            ("ordering or conflict semantics", ("ordering", "conflict", "single writer")),
            ("cache semantics", ("ttl", "invalidation", "stampede", "safe miss")),
            ("retention and deletion", ("retention", "deletion", "archive")),
            ("reconciliation and audit", ("reconciliation", "audit", "repair")),
        ),
    ),
    Category(
        "interfaces",
        "APIs, events, and workflows",
        10,
        (
            ("API contracts", ("apis define", "api contract", "validation")),
            ("authentication and authorization", ("authn", "authz", "authentication", "authorization")),
            ("errors, quotas, and compatibility", ("error code", "versioning", "quota", "pagination")),
            ("deadlines and retries", ("deadline", "bounded retry", "retry budget", "timeout")),
            ("event delivery and ordering", ("event", "at-least-once", "partition key", "ordering")),
            ("DLQ, replay, and lag", ("dlq", "dead-letter", "replay", "lag slo")),
            ("dual-write safety", ("transactional outbox", "change data capture", "cdc")),
        ),
    ),
    Category(
        "performance",
        "Performance and overload",
        10,
        (
            ("latency budget", ("latency budget", "p99")),
            ("scaling limits", ("scaling", "safe limit", "2x peak")),
            ("partitioning and skew", ("partition", "hot key", "skew", "noisy neighbor")),
            ("bounded resources", ("bounded", "concurrency limit", "queue capacity")),
            ("admission and backpressure", ("admission control", "backpressure", "load shedding")),
            ("graceful degradation", ("graceful degradation", "degraded mode", "fallback")),
        ),
    ),
    Category(
        "reliability",
        "Reliability and recovery",
        15,
        (
            ("SLIs, SLOs, and error budget", ("sli", "slo", "error budget")),
            ("failure matrix", ("failure matrix", "failure mode")),
            ("timeouts, retry, and circuit breaking", ("timeout", "retry budget", "circuit breaker")),
            ("containment and degraded behavior", ("contain", "graceful degradation", "degraded mode")),
            ("RTO and RPO", ("rto", "rpo")),
            ("backup and restore rehearsal", ("backup", "restore drill", "restore rehearsal")),
            ("failover and reconciliation", ("failover", "reconciliation", "game day")),
        ),
    ),
    Category(
        "security",
        "Security, privacy, tenancy, and abuse",
        10,
        (
            ("threat model", ("threat model", "threat")),
            ("identity and least privilege", ("identity", "least privilege", "service identity")),
            ("resource and tenant authorization", ("tenant", "authorization", "cross-tenant")),
            ("encryption, keys, and secrets", ("encryption", "kms", "secret", "rotation")),
            ("input and dependency security", ("ssrf", "injection", "file upload", "dependency trust")),
            ("privacy lifecycle", ("retention", "deletion", "residency", "privacy")),
            ("abuse and incident response", ("rate limiting", "fraud", "abuse", "incident response")),
        ),
    ),
    Category(
        "operations",
        "Operations, delivery, and migration",
        5,
        (
            ("logs, metrics, and traces", ("logs", "metrics", "traces")),
            ("alerts and runbooks", ("alert", "runbook", "on-call")),
            ("compatible migration", ("expand-migrate-contract", "backfill", "cutover", "compatibility")),
            ("progressive rollout", ("canary", "feature flag", "progressive")),
            ("rollback or roll-forward", ("rollback", "roll-forward")),
        ),
    ),
    Category(
        "decisions",
        "Decisions, cost, and validation",
        5,
        (
            ("unit economics", ("unit cost", "unit economics", "cost")),
            ("alternatives and ADRs", ("adr", "alternatives", "trade-off")),
            ("risks and owners", ("risk register", "risk", "owner")),
            ("validation portfolio", ("contract", "integration", "load", "chaos", "restore", "migration rehearsal")),
            ("review triggers", ("review trigger", "reversal trigger", "10x")),
        ),
    ),
)

assert sum(category.weight for category in CATEGORIES) == 100


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def has_any(text: str, phrases: Iterable[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def add_unique(findings: list[str], message: str) -> None:
    if message not in findings:
        findings.append(message)


def critical_findings(raw: str) -> list[str]:
    text = normalized(raw)
    findings: list[str] = []

    if re.search(r"\b(?:money|amount|price|balance|currency|payment)s?\b.{0,80}\b(?:float|double|floating[ -]point)\b", text):
        add_unique(findings, "Financial values appear to use floating-point arithmetic; require integer minor units or fixed-precision decimal with currency and rounding semantics.")

    if re.search(r"\b(?:write|writes|save|saves)\b.{0,80}\b(?:database|db)\b.{0,100}\b(?:then|and)\b.{0,40}\b(?:publish(?:es|ed|ing)?|send(?:s|ing|sent)?|emit(?:s|ted|ting)?)\b", text) and not has_any(text, ("transactional outbox", "change data capture", " cdc ", "distributed transaction")):
        add_unique(findings, "Database and broker effects appear to be written independently; require atomic coordination, transactional outbox/CDC, or explicit reconciliation.")

    if re.search(r"\b(?:retry|retries)\b.{0,50}\b(?:until success|forever|indefinitely|unlimited|without limit)\b", text):
        add_unique(findings, "Retry behavior is unbounded; require a deadline, maximum attempts, jittered backoff, retry budget, and safe terminal outcome.")

    if re.search(r"\b(?:unlimited|unbounded|infinite)\b.{0,25}\b(?:queue|buffer|backlog|fan-out|concurrency|connections?)\b|\b(?:queue|buffer|backlog|fan-out|concurrency|connections?)\b.{0,25}\b(?:unlimited|unbounded|infinite)\b", text):
        add_unique(findings, "A resource path is unbounded; require hard capacity, admission/backpressure, expiry or shedding, and overload behavior.")

    if re.search(r"\b(?:redis|cache|search index)\b.{0,50}\b(?:is|as|becomes?)\b.{0,20}\b(?:the )?(?:source of truth|authoritative)\b", text) and not has_any(text, ("non-authoritative", "not authoritative", "not the source of truth")):
        add_unique(findings, "A cache or derived index appears authoritative without durable recovery semantics.")

    if re.search(r"\bexactly[ -]once\b.{0,50}\b(?:guarantee|guaranteed|delivery|everywhere|end-to-end)\b", text) and not has_any(text, ("at-least-once", "idempotent", "transactional effect", "precise boundary")):
        add_unique(findings, "End-to-end exactly-once is claimed without a precise transactional or idempotent effect boundary.")

    if re.search(r"\binternal services?\b.{0,35}\btrust(?:ed)?\b|\binternal network\b.{0,35}\btrust(?:ed)?\b", text) and not has_any(text, ("workload identity", "service identity", "zero trust")):
        add_unique(findings, "Internal network location is treated as sufficient trust; require workload identity and service-side authorization.")

    if re.search(r"\bbackup(?:s)?\b", text) and not has_any(text, ("restore drill", "restore rehearsal", "tested restore", "restore verification")):
        add_unique(findings, "Backups are described without fresh restore rehearsal evidence and measured RTO/RPO.")

    if has_any(text, ("active-active", "active active")) and not (has_any(text, ("conflict", "single writer", "ownership", "routing")) and has_any(text, ("fencing", "fence", "split-brain"))):
        add_unique(findings, "Active-active writes lack complete conflict, ownership/routing, and fencing or split-brain semantics.")

    if re.search(r"\bauthori[sz]ation\b.{0,50}\b(?:frontend|front-end|ui|gateway)\b|\b(?:frontend|front-end|ui|gateway)\b.{0,50}\bauthori[sz]ation\b", text) and not has_any(text, ("every server-side boundary", "service-side authorization", "each service", "data boundary")):
        add_unique(findings, "Authorization appears concentrated at the frontend or gateway rather than enforced at each service and data boundary.")

    if re.search(r"\bdeploy directly\b|\bdirect deploy\b", text) and not has_any(text, ("rollback", "roll-forward", "canary", "progressive")):
        add_unique(findings, "The release path lacks progressive delivery and rollback or roll-forward evidence.")

    if re.search(r"\bmicroservices?\b.{0,45}\b(?:because|for)\b.{0,20}\b(?:scale|scalability|modern|best practice|industry standard)\b", text) and not has_any(text, ("independent deployment", "independent ownership", "fault isolation", "compliance boundary")):
        add_unique(findings, "Microservices are justified by a generic scaling claim rather than measured boundary, ownership, isolation, or deployment needs.")

    return findings


def score_document(raw: str, path: Path) -> dict[str, object]:
    text = normalized(raw)
    category_scores: dict[str, dict[str, object]] = {}
    total = 0.0
    missing_evidence: list[str] = []

    for category in CATEGORIES:
        passed: list[str] = []
        missing: list[str] = []
        for label, phrases in category.checks:
            if has_any(text, phrases):
                passed.append(label)
            else:
                missing.append(label)
        earned = category.weight * (len(passed) / len(category.checks))
        total += earned
        category_scores[category.key] = {
            "label": category.label,
            "weight": category.weight,
            "earned": round(earned, 1),
            "passed": passed,
            "missing": missing,
        }
        missing_evidence.extend(f"{category.label}: {item}" for item in missing)

    score = int(round(total))
    critical = critical_findings(raw)
    if critical or score < 60:
        verdict = "BLOCK"
    elif score < 85:
        verdict = "CONDITIONAL"
    else:
        verdict = "PASS"

    return {
        "file": str(path),
        "score": score,
        "verdict": verdict,
        "critical_findings": critical,
        "missing_evidence": missing_evidence,
        "category_scores": category_scores,
        "limitations": "Structural evidence scan only; expert review and fresh runtime validation remain required.",
    }


def render_text(report: dict[str, object]) -> str:
    lines = [
        f"Architecture review: {report['file']}",
        f"Score: {report['score']}/100",
        f"Verdict: {report['verdict']}",
    ]
    critical = report["critical_findings"]
    if critical:
        lines.append("Critical findings:")
        lines.extend(f"- {item}" for item in critical)
    missing = report["missing_evidence"]
    if missing:
        lines.append("Missing evidence:")
        lines.extend(f"- {item}" for item in missing[:20])
        if len(missing) > 20:
            lines.append(f"- ... {len(missing) - 20} additional evidence gaps")
    lines.append(str(report["limitations"]))
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("architecture", type=Path, help="Markdown architecture specification")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.architecture.is_file():
        print(f"Architecture file not found: {args.architecture}", file=sys.stderr)
        return 3
    try:
        raw = args.architecture.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Unable to read {args.architecture}: {exc}", file=sys.stderr)
        return 3

    report = score_document(raw, args.architecture)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report))
    return 0 if report["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
