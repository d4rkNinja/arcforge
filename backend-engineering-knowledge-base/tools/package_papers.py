#!/usr/bin/env python3
"""Package canonical corpus papers into portable skill reference directories.

The corpus under `papers/` stays canonical and is validated by
`validate_corpus.py`. This tool derives distribution copies for the skill
package so each installed skill remains self-contained:

- strips corpus bookkeeping (frontmatter, canonical scope map, metadata footer);
- removes template boilerplate that the corpus generator repeated across the
  invariants, subtopic, normative, bugs, questions, testing, and codebase-check
  sections, keeping the first occurrence of every distinct statement;
- collapses subtopics whose entire entry is the generic template into a single
  "Default obligations" list, keeping their names visible;
- moves "Questions that must be answered before implementation" and
  "Existing-codebase checks" directly after the executive summary so a
  linear read hits them first;
- renumbers sections and rewrites cross-paper links (same-skill links stay
  relative; cross-skill links become plain-text skill pointers).

Run from anywhere:  python tools/package_papers.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

KB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = KB_ROOT.parent
MANIFEST = KB_ROOT / "manifest.json"

# Paper number -> owning skill directory (skills live under REPO_ROOT/skills/).
# The final two entries enrich existing architecture skills instead of
# creating competing implementation skills.
SKILL_PAPERS: dict[str, list[int]] = {
    "auth-access": [3, 4, 5, 6, 7, 8, 9, 10, 112, 113, 114],
    "api-contracts": [11, 12, 13, 14, 15, 16, 17, 49, 50, 110, 111, 115, 116],
    "data-storage": [18, 19, 20, 21, 22, 26, 27, 28, 32, 33, 34, 40, 41, 42, 69, 122, 123, 124, 125],
    "transactions-consistency": [23, 24, 25, 35, 36, 48, 98, 99, 100, 101, 102, 103, 121],
    "async-messaging": [43, 44, 45, 46, 47, 118, 119, 120, 128, 129],
    "resilience-flow-control": [37, 38, 39, 51, 52, 53, 54, 55, 104, 131],
    "security-privacy": [61, 62, 63, 64, 65, 66, 67, 68, 126, 127],
    "production-operations": [56, 57, 58, 59, 60, 74, 75, 76, 77, 78, 97, 132, 133, 137, 138, 139],
    "migration-evolution": [29, 30, 31, 70, 71, 72, 73, 130, 134, 135, 136],
    "quality-release": [90, 91, 92, 93, 94, 95, 96, 109, 117, 146],
    "runtime-delivery": [1, 2, 79, 80, 81, 82, 83, 105, 106, 107, 108],
    "system-architecture-harness": [84, 85, 86, 87, 88, 89],
    "ai-agent-system-architecture": [140, 141, 142, 143, 144, 145],
}

NEW_SKILLS = set(SKILL_PAPERS) - {"system-architecture-harness", "ai-agent-system-architecture"}

SECTION_RE = re.compile(r"^## (\d+)\. (.+)$", re.M)
ITEM_RE = re.compile(r"^- (?:\[[ xX]\] )?(.*)$")
SUBTOPIC_SECTION = "Subtopic-by-subtopic implementation intelligence"
QUESTIONS_SECTION = "Questions that must be answered before implementation"
CHECKS_SECTION = "Existing-codebase checks before changing anything"
EXEC_SECTION = "Executive engineering summary"
NORMATIVE_SECTION = "Normative requirements"
DEFAULT_OBLIGATION_NOTE = (
    "These subtopics carry no additional domain-specific rule beyond the default "
    "obligation: for each, define owner, inputs, outputs, invariants, lifecycle, "
    "failure classification, and a compatibility contract; make the rule "
    "enforceable at the narrowest authoritative boundary; and do not accept a "
    "framework or provider default without proving it fits the domain."
)

# Corpus-generator template sentence shapes, matched anywhere in the item text.
TEMPLATE_PATTERNS = [
    re.compile(r"define the exact semantics of \*\*.+\*\* within", re.I),
    re.compile(r"a framework or provider default for .+ is accepted without proving", re.I),
    re.compile(r"locate every implementation path for .+, compare behavior across", re.I),
    re.compile(r"for \*\*.+\*\*, what authoritative boundary enforces the rule", re.I),
]

BOLD_LABEL_RE = re.compile(r"^\*\*[^*]+\*\*:?\s*(?:[—-]\s*)?")
FOR_X_RE = re.compile(r"^for\s+\*\*[^*]+\*\*:\s*", re.I)
LEVEL_WORD_RE = re.compile(r"^(MUST|SHOULD|MAY|AVOID|NEVER)\b[\s:—-]*", re.I)


def build_owner_map() -> dict[int, str]:
    owner: dict[int, str] = {}
    for skill, numbers in SKILL_PAPERS.items():
        for n in numbers:
            if n in owner:
                raise SystemExit(f"paper {n:03d} assigned to both {owner[n]} and {skill}")
            owner[n] = skill
    missing = set(range(1, 147)) - set(owner)
    extra = set(owner) - set(range(1, 147))
    if missing or extra:
        raise SystemExit(f"paper ownership mismatch: missing={sorted(missing)} extra={sorted(extra)}")
    return owner


def strip_label(item: str) -> str:
    """Remove leading normative/field labels for comparison purposes."""
    t = item.strip()
    changed = True
    while changed:
        changed = False
        m = BOLD_LABEL_RE.match(t)
        if m:
            t = t[m.end():]
            changed = True
        m = LEVEL_WORD_RE.match(t)
        if m:
            t = t[m.end():]
            changed = True
        m = FOR_X_RE.match(t)
        if m:
            t = t[m.end():]
            changed = True
    return t.strip()


def core_text(item: str) -> str:
    t = strip_label(item)
    t = re.sub(r"[*_`#\[\]]", "", t)
    t = re.sub(r"\s+", " ", t).strip().lower().rstrip(".")
    return t


def is_template(item: str) -> bool:
    body = re.sub(r"\s+", " ", strip_label(item))
    return any(p.search(body) for p in TEMPLATE_PATTERNS)


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    return text[end + len("\n---\n"):].lstrip("\n")


def rewrite_relationship_lines(text: str, owner: dict[int, str], this_skill: str, stats: dict) -> str:
    pattern = re.compile(r"^- \[(\d{3})\. ([^\]]+)\]\(([^)]+)\)[^\n]*$", re.M)

    def repl(m: re.Match) -> str:
        num = int(m.group(1))
        title = m.group(2)
        target_skill = owner.get(num, this_skill)
        if target_skill == this_skill:
            stats["same_links"] += 1
            return f"- [{num:03d}. {title}]({Path(m.group(3)).name})"
        stats["cross_links"] += 1
        return f"- {num:03d}. {title} — in the `{target_skill}` skill."

    return pattern.sub(repl, text)


def remove_scope_section(text: str) -> str:
    return re.sub(
        r"^## 2\. Scope and terminology map$.*?(?=^## )",
        "",
        text,
        flags=re.M | re.S,
    )


def remove_metadata_footer(text: str) -> str:
    return re.sub(r"\n---\s*\n\s*\*\*Paper metadata:\*\*[^\n]*\n?\s*$", "\n", text)


def remove_unnumbered_scope_note(text: str) -> str:
    """Paper 146 carries an unnumbered generator-facing scope note before the
    first numbered section; strip it (it is corpus bookkeeping)."""
    return re.sub(r"^## Canonical scope note\n.*?(?=^## )", "", text, flags=re.M | re.S)


def split_sections(text: str) -> tuple[str, list[dict]]:
    matches = list(SECTION_RE.finditer(text))
    if not matches:
        return text, []
    preamble = text[: matches[0].start()]
    sections = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append({"num": m.group(1), "title": m.group(2).strip(), "body": text[m.end():end].strip()})
    return preamble, sections


def rebuild_subtopic_section(body: str, stats: dict) -> set[str]:
    """Collapse fully-templated subtopics into one 'Default obligations' list
    (in place). Returns the comparison keys of the kept, specific entries."""
    entries = re.split(r"(?=^### \d+\.\d+\. )", body, flags=re.M)
    head = entries[0].strip()
    specific: list[str] = []
    collapsed: list[str] = []
    keys: set[str] = set()
    for entry in entries[1:]:
        hm = re.match(r"^### \d+\.\d+\. (.+)$", entry, re.M)
        if not hm:
            specific.append(entry.rstrip())
            continue
        name = hm.group(1).strip()
        items = [ITEM_RE.match(l.strip()).group(1) for l in entry.splitlines() if ITEM_RE.match(l.strip())]
        if items and all(is_template(i) for i in items):
            collapsed.append(name)
            stats["collapsed"] += 1
        else:
            specific.append(entry.rstrip())
            for i in items:
                keys.add(core_text(i))
    parts = [head]
    if collapsed:
        parts.append("### Default obligations\n\n" + DEFAULT_OBLIGATION_NOTE + "\n\n"
                     + "\n".join(f"- **{n}**" for n in collapsed))
    parts.extend(specific)
    return keys, "\n\n".join(parts)


def filter_section(body: str, keys_7: set[str], seen: set[str], drop_templates: bool, stats: dict) -> str:
    out_lines: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        m = ITEM_RE.match(stripped)
        if m is None:
            out_lines.append(line)
            continue
        item = m.group(1)
        key = core_text(item)
        if drop_templates and is_template(item):
            stats["dropped_items"] += 1
            continue
        if key in keys_7 or key in seen:
            stats["dropped_items"] += 1
            continue
        seen.add(key)
        out_lines.append(line)
    text = "\n".join(out_lines)
    # Remove sub-headings whose entire list vanished.
    text = re.sub(r"\n(### [^\n]+)\n\n(?=### |## |\Z)", "\n", text)
    return text.strip()


def drop_empty_sections(sections: list[dict]) -> list[dict]:
    kept = []
    for s in sections:
        content = [l for l in s["body"].splitlines() if l.strip()]
        if content:
            kept.append(s)
    return kept


def renumber(text: str) -> str:
    matches = list(SECTION_RE.finditer(text))
    mapping: dict[str, str] = {}
    parts: list[str] = []
    last = 0
    for idx, m in enumerate(matches, start=1):
        mapping[m.group(1)] = str(idx)
        parts.append(text[last:m.start()])
        parts.append(f"## {idx}. {m.group(2)}")
        last = m.end()
    parts.append(text[last:])
    text = "".join(parts)
    return re.sub(
        r"^### (\d+)\.(\d+)\. (.+)$",
        lambda m: f"### {mapping.get(m.group(1), m.group(1))}.{m.group(2)}. {m.group(3)}",
        text,
        flags=re.M,
    )


def transform(text: str, owner: dict[int, str], skill: str, stats: dict) -> str:
    text = strip_frontmatter(text)
    text = rewrite_relationship_lines(text, owner, skill, stats)
    text = remove_scope_section(text)
    text = remove_metadata_footer(text)
    text = remove_unnumbered_scope_note(text)

    preamble, sections = split_sections(text)
    if not sections:
        raise ValueError("no sections found")

    keys_7: set[str] = set()
    for s in sections:
        if s["title"] == SUBTOPIC_SECTION:
            keys_7, s["body"] = rebuild_subtopic_section(s["body"], stats)
            break

    seen: set[str] = set()
    for s in sections:
        if s["title"] == SUBTOPIC_SECTION:
            continue
        if s["title"] == NORMATIVE_SECTION:
            # Codification summary: drop template items, keep every distinct
            # normative statement even if prose repeats it earlier.
            s["body"] = filter_section(s["body"], set(), set(), drop_templates=True, stats=stats)
            # Register kept normative items so later sections drop verbatim repeats.
            for line in s["body"].splitlines():
                m = ITEM_RE.match(line.strip())
                if m:
                    seen.add(core_text(m.group(1)))
        else:
            s["body"] = filter_section(s["body"], keys_7, seen, drop_templates=True, stats=stats)

    # Front-load the questions and codebase checks after the executive summary.
    def take(title: str):
        for i, s in enumerate(sections):
            if s["title"] == title:
                return sections.pop(i)
        return None

    questions = take(QUESTIONS_SECTION)
    checks = take(CHECKS_SECTION)
    ordered: list[dict] = []
    for s in sections:
        ordered.append(s)
        if s["title"] == EXEC_SECTION:
            if questions:
                ordered.append(questions)
            if checks:
                ordered.append(checks)

    ordered = drop_empty_sections(ordered)
    if len(ordered) < 5:
        raise ValueError("too few sections survived filtering")

    doc = preamble.rstrip() + "\n\n" + "\n\n".join(f"## {s['num']}. {s['title']}\n\n{s['body']}" for s in ordered) + "\n"
    doc = renumber(doc)
    # Safety net: no relative paper links may survive outside same-skill references.
    doc = re.sub(
        r"\[([^\]]+)\]\((?:\.\./)?(?:primitives|systems|cross-cutting)/([^)/]+\.md)\)",
        lambda m: f"{m.group(1)} (see `{owner.get(int(Path(m.group(2)).name[:3]), skill)}` skill)",
        doc,
    )
    return doc.rstrip() + "\n"


def main() -> int:
    owner = build_owner_map()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    papers = {p["number"]: p for p in manifest["papers"]}

    totals = {"written": 0, "collapsed": 0, "dropped_items": 0, "same_links": 0, "cross_links": 0}
    words_before = words_after = 0
    per_skill: dict[str, int] = {skill: 0 for skill in SKILL_PAPERS}

    for number in sorted(papers):
        skill = owner[number]
        src = KB_ROOT / papers[number]["path"]
        dest = REPO_ROOT / "skills" / skill / "references" / "papers" / src.name
        raw = src.read_text(encoding="utf-8")
        words_before += len(raw.split())
        stats = {"collapsed": 0, "dropped_items": 0, "same_links": 0, "cross_links": 0}
        try:
            cleaned = transform(raw, owner, skill, stats)
        except ValueError as e:
            print(f"FAILED: paper {number:03d}: {e}", file=sys.stderr)
            return 1
        if len(cleaned) < 1500:
            print(f"FAILED: paper {number:03d} transformed to only {len(cleaned)} bytes", file=sys.stderr)
            return 1
        words_after += len(cleaned.split())
        for k in totals:
            totals[k] += stats.get(k, 0)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(cleaned, encoding="utf-8", newline="\n")
        totals["written"] += 1
        per_skill[skill] += 1

    leftovers = [
        str(p)
        for p in REPO_ROOT.glob("skills/*/references/papers/*.md")
        if owner.get(int(p.name[:3])) != p.parent.parent.parent.name
    ]
    if leftovers:
        print(f"FAILED: stale paper copies in wrong skills: {leftovers}", file=sys.stderr)
        return 1

    pct = 100 * (1 - words_after / words_before)
    print(f"OK: packaged {totals['written']} papers into {len(SKILL_PAPERS)} skills "
          f"({totals['same_links']} same-skill links, {totals['cross_links']} cross-skill pointers, "
          f"{totals['collapsed']} template subtopics collapsed, {totals['dropped_items']} duplicate "
          f"items removed; {words_before:,} -> {words_after:,} words, {pct:.1f}% smaller).")
    for skill in sorted(SKILL_PAPERS):
        marker = "existing" if skill not in NEW_SKILLS else "new"
        print(f"  {skill:<34} {per_skill[skill]:>3} papers ({marker})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
