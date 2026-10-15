# Distribution status

The package identity is `writing-doc` version `0.1.0`.
The intended repository is `joevilcai666/writing-doc-skill`, with default branch `main` and annotated tag `v0.1.0`.
Public publication and installation remain planned.

## Channel states

Only these status values apply: `planned`, `published`, `listed`, `submitted`, `rejected`, and `not adopted`.
An intended destination is not evidence that the destination exists.

| Channel | Status | Evidence or remaining action |
| --- | --- | --- |
| GitHub repository | planned | Configured in the [portable manifest](../plugin.json). No public repository check completed. |
| GitHub Release | planned | Intended tag: `v0.1.0`. Archive, checksum, public download, and tag checks remain incomplete. |
| skills.sh | planned | No discovery page was verified for this repository and skill. Check natural discovery after publication. |
| OpenAI directory | planned | [Codex compatibility manifest](../.codex-plugin/plugin.json) exists. No submission receipt, listing, or plugin installation evidence exists. |
| Anthropic directory | planned | The repository supplies its own [Claude marketplace](../.claude-plugin/marketplace.json). This is not a submission to Anthropic's directory. No receipt or listing exists. |

`planned` means the step has no completed external evidence.
`published` means the public artifact exists.
`listed` requires a directory page that resolves to this package.
`submitted` requires a submission receipt or equivalent record.
`rejected` requires an observed rejection.
`not adopted` records a decision not to use a channel.

## Install routes and version identity

The [English README](../README.md) and [Chinese README](../README.zh-CN.md) contain the planned commands.
Every remote route carries the label `Planned for v0.1.0 verification` until its exact command and source commit pass public checks.

The short `skills` command and unpinned Claude marketplace select the repository's default branch.
The tagged skill URL, tagged Claude marketplace, and manual tagged clone select `v0.1.0`.
The Git tag fixes package source. It does not fix the client or installer version.

The Codex Skill Installer route installs the shared skill.
It does not establish that the plugin is available in the OpenAI directory.
Codex and Claude manifests describe package discovery. Their presence does not prove installation.

## Evidence required before a status changes

| Evidence level | Required record | Current result |
| --- | --- | --- |
| Implemented | Package files and release identity. | Shared skill, manifests, assets, demo, checks, and public docs exist. |
| Locally verified | Exact commit, commands, environment, exits, and known limits. | The documentation candidate passed 94 local tests and the default repository checker. Final release checks remain incomplete. |
| Publicly verified | Public URL, source commit, client version, exact command, and observed result. | No public clone, download, installation, or runtime check completed. |
| User accepted | Explicit acceptance of the delivered package or observed result. | Four source images have user approval. The package implementation has no acceptance record. |

Current blockers include unsafe metadata in the private development history and an unavailable Codex plugin validator.
The release process requires a clean reviewed public history before any push.
See [HOW_IT_WORKS.md](../HOW_IT_WORKS.md) for the current gate behavior.

Do not infer endorsement from publication, discovery, or a self-hosted marketplace.
Record external login, review, or confirmation requirements as remaining actions with the appropriate channel status.

最后更新时间：2026-10-15
