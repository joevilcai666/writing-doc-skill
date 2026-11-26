# Distribution status

The package is `writing-doc` version `0.2.0`. The [verification record](verification/v0.2.0.md) identifies the exact release commit, model-output evaluation, and tested installation routes.

The [public repository](https://github.com/joevilcai666/writing-doc-skill) uses `main` as its default branch. The tag `v0.2.0` identifies the source for the release ZIP.

## Channel states

Only these status values apply: `planned`, `published`, `listed`, `submitted`, `rejected`, and `not adopted`.

| Channel | Status | Evidence or remaining action |
| --- | --- | --- |
| GitHub repository | published | [Public repository](https://github.com/joevilcai666/writing-doc-skill). Anonymous main/tag clones passed. |
| GitHub Release | published | [v0.2.0](https://github.com/joevilcai666/writing-doc-skill/releases/tag/v0.2.0), deterministic ZIP and checksum. Anonymous downloads match the local build and GitHub asset digests. |
| skills.sh | planned | [Skill URL](https://skills.sh/joevilcai666/writing-doc-skill/writing-doc) returned HTTP 200 with a missing-skill fallback and no canonical GitHub source. [Repository URL](https://skills.sh/joevilcai666/writing-doc-skill) returned HTTP 404. No verified listing. |
| OpenAI directory | planned | No submission receipt or official listing. Public self-hosted Codex plugin installation passed. |
| Anthropic directory | planned | No submission receipt or official listing. Public self-hosted Claude marketplace installation passed. |

`planned` means that external evidence is incomplete. `published` means that the public artifact exists.
`listed` requires a directory page for this exact package. `submitted` requires a submission receipt.
`rejected` requires an observed rejection. `not adopted` records a decision not to use a channel.
Publication and self-hosted marketplaces do not imply endorsement or official review.

## Install routes and version identity

The [English README](../README.md) and [Chinese README](../README.zh-CN.md) contain the commands.
Pinned Codex CLI 0.162.1 and Claude Code 2.1.218 plugin installs and a tagged skills 1.7.2 project install passed in isolated configurations. All three installed skill files matched the tag. The [v0.1.0 record](verification/v0.1.0.md) covers its earlier tests.
The Codex CLI plugin remove route passed a fresh isolated public v0.1.0 install/remove trial.
The plugin cache and enablement entry disappear. Marketplace registration and its source checkout remain.
Optional Codex marketplace removal affects the configured source and remains unverified.
The separate Codex Skill Installer and other removal routes remain pending.

The short `skills` command and unpinned Claude marketplace select the default branch.
Tagged commands select `v0.2.0`. A tag fixes package source, not the client or installer version.
CLI installation does not establish directory acceptance or correct model behavior.

## Evidence and remaining work

| Evidence level | Current result |
| --- | --- |
| Implemented | Shared skill, manifests, assets, synthetic demo, checks, and public documentation exist. |
| Locally verified | See the v0.2.0 record for regression, gate, package and isolated client checks. |
| Publicly verified | See the v0.2.0 record for verified source, asset and client access. |
| User accepted | Four source images have user approval. Package implementation and reader outcomes have no acceptance record. |

The repository has zero registered runners. Exact-commit checks ran directly on local macOS arm64.
No GitHub Actions or billing status served as a release gate.
Private vulnerability reporting is enabled. Topics: `agent-skills`, `codex`, `claude-code`, `technical-writing`, `documentation`.

Social-preview upload remains pending. GitHub rejected the 1,114,198-byte original because it exceeds 1 MB.
An upload-only 972,388-byte PNG preserves the exact decoded RGBA pixels and has no private metadata.
The user's active browser prevented the second upload. No completed upload or public preview is claimed.
Official directory submission, desktop selection, other uninstall checks, and user acceptance remain open.

最后更新时间：2026-11-26（Asia/Shanghai）
