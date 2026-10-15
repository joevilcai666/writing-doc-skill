# Distribution status

The public package is `writing-doc` version `0.1.0`.
Repository: [joevilcai666/writing-doc-skill](https://github.com/joevilcai666/writing-doc-skill), default branch `main`.
Annotated tag `v0.1.0` points to tested commit `9630868f9c0b491cfd28511fa88f551f4cd5f5d3`.
Later documentation on `main` does not change the tag or Release assets.

## Channel states

Only these status values apply: `planned`, `published`, `listed`, `submitted`, `rejected`, and `not adopted`.

| Channel | Status | Evidence or remaining action |
| --- | --- | --- |
| GitHub repository | published | [Public repository](https://github.com/joevilcai666/writing-doc-skill). Anonymous main/tag clones passed. |
| GitHub Release | published | [v0.1.0](https://github.com/joevilcai666/writing-doc-skill/releases/tag/v0.1.0), deterministic ZIP and checksum. Anonymous download matched GitHub's SHA-256 digest. |
| skills.sh | planned | [Skill URL](https://skills.sh/joevilcai666/writing-doc-skill/writing-doc) returned HTTP 200 with a missing-skill fallback and no canonical GitHub source. [Repository URL](https://skills.sh/joevilcai666/writing-doc-skill) returned HTTP 404. No verified listing. |
| OpenAI directory | planned | No submission receipt or official listing. Public self-hosted Codex plugin installation passed. |
| Anthropic directory | planned | No submission receipt or official listing. Public self-hosted Claude marketplace installation passed. |

`planned` means that external evidence is incomplete. `published` means that the public artifact exists.
`listed` requires a directory page for this exact package. `submitted` requires a submission receipt.
`rejected` requires an observed rejection. `not adopted` records a decision not to use a channel.
Publication and self-hosted marketplaces do not imply endorsement or official review.

## Install routes and version identity

The [English README](../README.md) and [Chinese README](../README.zh-CN.md) contain the commands.
Public tests used skills 1.7.2, Codex CLI 0.162.1, and Claude Code 2.1.295.
Default and tagged `skills` installations passed. Codex's pinned marketplace and Claude's main/tag marketplaces passed.
Each installed `SKILL.md` matched the tagged source byte for byte.
The manual tagged folder copy also matched. Desktop discovery and model execution remain unverified.
The separate Codex Skill Installer and removal routes remain pending.

The short `skills` command and unpinned Claude marketplace select the default branch.
Tagged commands select `v0.1.0`. A tag fixes package source, not the client or installer version.
CLI installation does not establish directory acceptance or correct model behavior.

## Evidence and remaining work

| Evidence level | Current result |
| --- | --- |
| Implemented | Shared skill, manifests, assets, synthetic demo, checks, and public documentation exist. |
| Locally verified | Exact release commit passed 125 tests, all release stages, full-history privacy checks, and actual client validation. |
| Publicly verified | Anonymous source and asset access, checksums, CLI installation and listing, and installed-skill byte comparisons passed. |
| User accepted | Four source images have user approval. Package implementation and reader outcomes have no acceptance record. |

The repository has zero registered runners. Exact-commit checks ran directly on local macOS arm64.
No GitHub Actions or billing status served as a release gate.
Private vulnerability reporting is enabled. Topics: `agent-skills`, `codex`, `claude-code`, `technical-writing`, `documentation`.

Social-preview upload remains pending. GitHub rejected the 1,114,198-byte original because it exceeds 1 MB.
An upload-only 972,388-byte PNG preserves the exact decoded RGBA pixels and has no private metadata.
The user's active browser prevented the second upload. No completed upload or public preview is claimed.
Official directory submission, desktop discovery, actual model tasks, uninstall checks, and user acceptance remain pending.

See the [verification record](verification/v0.1.0.md) for commands, source identity, digests, and limits.

最后更新时间：2026-10-15
