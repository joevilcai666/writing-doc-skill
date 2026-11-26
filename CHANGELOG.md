# Changelog

## v0.2.0 — 2026-11-26

- Extend the reader-oriented workflow to research, explanations, decision memos, and product designs.
- Preserve evidence, source disagreements, uncertainty, technical details, and review boundaries.
- Add six synthetic reader-outcome cases; distinguish model-generated output evaluation from static checks and human comprehension.
- Enforce a portable 64-level JSON nesting limit across Python decoder versions.
- Compare evidence on the same basis, explain how a mechanism applies to a new case, and keep specified commands verbatim.
- Record two model-output A/B experiments in the [verification record](docs/verification/v0.2.0.md).

## v0.1.0 — 2026-10-15

- One shared technical-document skill for Codex, Claude Code, and Agent Skills clients.
- Answers and actions first, with source facts, commands, links, and necessary conditions preserved.
- A review-only boundary that instructs the agent to leave files unchanged.
- English and Simplified Chinese READMEs with approved problem and solution artwork.
- A synthetic before-and-after guide and a deterministic local rubric.
- Local package, privacy, history, and validation gates.
- Public annotated tag, deterministic ZIP, SHA-256 sidecar, and isolated CLI installation evidence.

The [verification record](docs/verification/v0.1.0.md) separates local checks, public installation, and remaining user acceptance.
See [distribution status](docs/distribution.md) for channel states.
