# ArcForge User-First README Design

- **Status:** Approved direction; written specification awaiting review
- **Date:** 2026-08-17
- **Branch:** `codex/readme-user-first`

## Objective

Make the repository immediately understandable to someone deciding whether to
install and use ArcForge. The README should lead with outcomes, make the first
successful invocation obvious, and explain the skill catalog without exposing
maintainer history or internal cleanup details.

## Audience

The primary reader is a Claude Code, Codex, or Agent Skills user who wants safer
architecture and backend decisions. Contributors remain a secondary audience
served by links near the end rather than by the opening narrative.

## README Structure

1. **Hero** — one sentence explaining the value, followed by the supported
   runtimes and the current release.
2. **Quick start** — the shortest install command and one useful first prompt.
3. **Choose a mode** — a compact Think, Review, Change, Verify table describing
   the outcome of each mode.
4. **Choose a skill** — group the catalog into production systems, AI and agent
   systems, independent review, and backend domains. Show the stable technical
   ID and a concise trigger for every skill.
5. **Examples** — one realistic prompt for each mode, written for copying.
6. **How skills work together** — explain typed companions and show one
   cross-domain checkout example.
7. **What a strong result contains** — decisions, assumptions, blockers,
   evidence, and next steps.
8. **Limits and deeper documentation** — concise boundaries plus links to skill
   guides, contributing guidance, security guidance, and license.

## Writing Rules

- Use direct, user-oriented language and short paragraphs.
- Lead with a working action before background explanation.
- Keep all fourteen approved display names and stable technical IDs exact.
- Explain technical IDs once, immediately before they are needed.
- Avoid maintainer chronology, packaging mechanics, internal validation details,
  and negative capability commentary.
- Use one compact catalog rather than repeating the same routing information.
- Keep examples realistic and mode-specific.
- Do not imply that every request must proceed to a repository change.

## Repository-Wide Wording Cleanup

Search all tracked user-facing and maintainer-facing text for the recently added
absence-focused operational commentary. Remove it rather than replacing it with
different wording that makes the same point. This includes current release
notes, governing instructions, primary skills, and prior design notes where the
commentary was introduced.

The cleanup must not remove substantive security boundaries, permission rules,
runtime-neutral frontmatter requirements, or honest evidence limitations.

## Verification

- Confirm the README contains the approved eight-part information flow.
- Confirm all fourteen display names and IDs match the canonical catalog.
- Confirm every mode has one distinct copyable example.
- Confirm repository-wide wording search finds no remaining targeted
  operational commentary.
- Confirm all primary skills preserve required headings and line limits.
- Confirm JSON and YAML metadata remain parseable.
- Run portable discovery and isolated Claude Code/Codex installation checks.
- Update checksum metadata after all text is final.

## Acceptance Criteria

A new reader can install ArcForge, choose a mode, choose the correct skill, and
write a useful first prompt without reading contributor documentation. The
README stays compact, the catalog remains exact, repository history does not
distract from the product, and the final tree passes the established portable
skill checks.
