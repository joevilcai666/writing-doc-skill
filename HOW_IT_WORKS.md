# How Writing Doc Works

`writing-doc` guides an agent to turn verbose AI output into technical documentation that a target reader can understand and use.

The skill is an editor's desk: it keeps the source facts but rearranges them so the intended reader can find and use them.

To create and maintain a living product explanation like this document for another project, use the [how-it-works skill](https://github.com/joevilcai666/how-it-works-skill).

The package contains instructions for the user's agent, not a separate document service.
This repository defines the package identity for release `0.1.0`.
The package uses the MIT license.
Its configured repository URL is `https://github.com/joevilcai666/writing-doc-skill`.
The repository and [v0.1.0 Release](https://github.com/joevilcai666/writing-doc-skill/releases/tag/v0.1.0) are public.

## Find the part you need

- [Package structure](#package-structure) explains which files supply the product.
- [Documentation workflow](#documentation-workflow-and-visuals) explains what the agent receives.
- [Evidence and limits](#evidence-and-limits) separates implementation from real use.
- [Synthetic demonstration](#synthetic-demonstration-and-local-rubric) explains what the local example proves.
- [Local gates](#local-repository-and-privacy-gates) explains the publication checks and current blockers.
- [Release archive](#deterministic-release-archive) explains the ZIP and checksum builder.

## Package structure

A manifest is a package label. It tells a client which package it reads.
The three plugin manifests identify the same package.
They use one shared skill directory.

```mermaid
flowchart TD
    A["Portable plugin.json"] -->|"Default discovery"| D["skills/"]
    B["Codex compatibility manifest"] -->|"Explicit skills path"| D
    C["Claude marketplace entry: ./"] --> E["Claude plugin manifest"]
    E -->|"Default discovery"| D
    D --> F["writing-doc/SKILL.md: shared documentation workflow"]
    D --> G["writing-doc/agents/openai.yaml: client metadata"]
    H["Approved visual sources"] --> I["assets/: four square PNGs"]
    J["Built-in image generation"] --> K["assets/social-preview.png"]
    L["demo/source/: verbose synthetic guide"] --> M["demo/expected/: hand-authored revision"]
    L --> N["evals/run_rubric.py: deterministic Markdown checks"]
    M --> N
    O["evals/cases.json: required facts and sections"] --> N
    N --> P["Stable failure identifiers or local PASS"]
```

The portable manifest declares the Agent Plugins 1.0.0 schema.
The Codex compatibility manifest points to `./skills/`.
Claude Code uses its default `skills/` location.
The Claude marketplace exposes one local plugin from the repository root.

| Module | Responsibility |
| --- | --- |
| `skills/writing-doc/SKILL.md` | Gives every client the same reader-focused writing instructions. |
| `plugin.json`, `.codex-plugin/`, `.claude-plugin/` | Label the package and let clients discover the shared skill. |
| `agents/openai.yaml` | Supplies the skill label, default prompt, and invocation policy for OpenAI clients. |
| `assets/` | Supplies the approved problem and solution artwork and the social preview. |
| `demo/` and `evals/` | Show one synthetic revision and check fixed document conditions. |
| `scripts/` and `tests/` | Check package structure, privacy patterns, and local behavior. |
| `scripts/build_release.py` | Builds the ZIP from tracked current files and supplies its SHA-256 checksum. |
| READMEs and `docs/distribution.md` | Explain use, verified installation routes, and observed distribution status. |

The `agents/openai.yaml` file supplies the skill name and default prompt for OpenAI clients.
Its invocation policy permits implicit invocation.
This policy permits automatic skill selection when a client supports it.
It does not prove that a client loaded or invoked the skill.

## Documentation workflow and visuals

The shared `skills/writing-doc/SKILL.md` contains the authoritative Chinese instructions.
It identifies the reader and task, puts answers first, and preserves technical facts.
It keeps the user's language and checks whether the reader can complete the task.
For review-only requests, it reports concrete problems and fixes without file edits.
It excludes marketing copy, literary text, and file conversion without a documentation task.

```mermaid
flowchart TD
    A["User request and source material"] --> B["Agent identifies the reader and task"]
    B --> C{"Requested action?"}
    C -->|"Write or rewrite"| D["Preserve facts, commands, links, and conditions"]
    D --> E["Put the answer first and make steps usable"]
    C -->|"Review only"| F["Report concrete problems and fixes without file edits"]
    E --> G["Check accuracy, clarity, language, and result checks"]
    F --> G
    G --> H["Return the requested document or review"]
```

A skill is an instruction sheet for an agent.
The client reads that sheet when it selects the skill.
The package does not prove that the agent follows the instructions in a real session.
The client controls model choice, tools, file access, and any network request.

The skill adds no agent loop, memory store, subagent system, server, background process, analytics, or telemetry.
It does not modify `AGENTS.md`, `CLAUDE.md`, or global agent instructions.
Installation tools can update their own client settings and skill directories.

The `assets/` directory contains four approved 1200 × 1200 PNG images.
The files cover problem and solution messages in English and Chinese.
Their image data matches the approved source files.
The package removes private metadata chunks without a change to the image data or dimensions.
The separate 1280 × 640 social preview uses the same visual direction.
The built-in image generator produced the preview, and a proportional resize set its final dimensions.

## Evidence and limits

| Evidence level | Meaning | Current state |
| --- | --- | --- |
| Implemented | The files or behavior exist in the repository. | Version, license, manifests, skill metadata, shared skill, five PNG assets, synthetic rubric, local gates, public docs, deterministic archive builder, release note, and verification template exist. |
| Locally verified | A local check passed on an identified source state. | Release commit `9630868f9c0b491cfd28511fa88f551f4cd5f5d3` passed 125 tests, including 19 archive tests, the full release gate, full-history privacy checks, the skill validator, real isolated Codex installation, and Claude strict validation. |
| Publicly verified | A check passed against a public clone, download, or installation. | Anonymous main/tag clones and Release downloads passed. Default/tagged skills installations, Codex pinned plugin installation/removal, and Claude main/tag plugin installations passed. Installed skills matched the tag byte for byte. |
| User accepted | The user explicitly accepted the result under review. | The user approved the four source images. No user acceptance evidence exists for this package implementation or actual reader outcomes. |

The local checks cover package metadata, required skill boundaries, PNG dimensions, and source-copy integrity.
They do not establish agent behavior or reader comprehension.
Visual inspection covers the preview text, composition, and legibility.
The [verification record](docs/verification/v0.1.0.md) identifies commands, environment, source commit, and evidence limits.
The READMEs label the separate Codex Skill Installer and other removal routes as pending.
The [distribution record](docs/distribution.md) contains channel status, not an endorsement claim.

## Synthetic demonstration and local rubric

The demonstration uses a fictional local service, Lantern API.
Its source guide mixes background, setup, and failures in long paragraphs.
Its revised guide puts the command first and supplies prerequisites, three steps, a result check, and one failure entry.
Both guides contain the six exact technical literals from the case definition.
No service or real token accompanies this example.

The rubric is a checklist for document structure, like a preflight check for a document.
It checks literal preservation, command placement, section presence, a health response check, and paragraph length.
The evaluator returns stable rule identifiers. Its CLI returns 0 for a pass and 1 for rule failures.
It accepts different prose and heading case. It does not compare a document with the expected guide word for word.

Fifteen rubric tests passed locally with Python 3.9.6 on macOS arm64.
The expected guide passed the local CLI check.
The source failed the checks for answer order, required sections, verification, and paragraph length.
The full local suite includes these checks and the repository gate tests.

These results cover static synthetic documents and deterministic checks.
They do not prove that an agent follows the skill, that a service runs, or that a real reader understands the result.
Language retention, review-only behavior, scope selection, desktop discovery, and reader outcomes still need runtime evidence.

## Local repository and privacy gates

A release gate is a checklist that stops publication when a required check fails.
`python3 scripts/check_repo.py` checks the current package files and Git index.
It checks package versions, JSON syntax, skill frontmatter, local Markdown links, PNG files, and README image references when a README exists.
It also runs the rubric, the unit suite, privacy checks, and Git whitespace checks for both the worktree and index.
The unit gate rejects an empty test suite.

```mermaid
flowchart TD
    A["Current files, hidden files, and Git index"] --> B["Default repository checks"]
    C["Reachable Git blobs, commit messages, and annotated tag messages"] --> D["Release history checks"]
    B --> E["Structure, links, rubric, tests, strict text parsing, privacy, and whitespace"]
    D --> F["Strict text parsing, metadata, private-value, and message-format checks"]
    E --> G["Local PASS or blocking failure"]
    F --> H{"All release requirements pass?"}
    I["Required files, skill validator, real isolated Codex install, Claude strict validator"] --> H
    G --> H
    H -->|"No"| J["Stop publication and record the blocker"]
    H -->|"Yes"| K["Review the exact commit and clean public history"]
    K --> O["Build tracked current files into a deterministic ZIP"]
    O --> P["Inspect archive paths, privacy, and SHA-256"]
    P --> L["Publish the tag, archive, and checksum"]
    L --> M["Public clone, checksum, and CLI installations verified"]
    M --> R["Codex plugin removal verified; marketplace registration retained"]
    R --> N["Record evidence on main; user acceptance remains pending"]
```

The privacy scanner reads tracked files and non-ignored untracked files. This includes hidden files.
It also reads staged blobs, so a safe worktree cannot conceal a private staged value.
`python3 scripts/privacy_scan.py --history` adds every reachable Git blob from every local ref.
It also checks every reachable commit message and annotated tag message. This includes nested tags.

Those checks include deleted files and PNG metadata in historical blobs.
Git identity headers remain outside the private-value scan.
It rejects shallow history, replacement refs, read failures, malformed PNG chunks, and unsafe file links.

The scanner checks home paths, common credential forms, email addresses, signed URLs, and private-key headers.
Credential assignments include quoted JSON and JSON-like field names.
They also include supported command arguments with one or two leading hyphens.
It rejects PNG `tEXt`, `zTXt`, `iTXt`, and `eXIf` chunks.

For other file content, the scanner accepts strict UTF-8, with or without a byte-order mark (BOM).
A BOM is an encoding label at the start of a file, like a label on a container.
UTF-16LE, UTF-16BE, UTF-32LE, and UTF-32BE require that label.
The scanner rejects invalid text and decoded NUL, C0, DEL, and C1 control characters, except tab, carriage return, and newline.
It does not guess an encoding or replace invalid bytes.
Unknown content blocks current, index, history, and archive checks with `text-invalid` at the fixed location `[file-content]`.

Each finding reports a rule and location with a fixed redaction marker.
It never includes a matched value or source excerpt.
It redacts a full path when the path contains a private value.
An invalid-content finding includes no original filename or decoder error.
The repository checker also suppresses external tool output.

The message parser separates Git object headers from the message body before any private-value check.
It checks UTF-8 messages and supports a fixed set of declared commit-message encodings.
Missing message boundaries, unsupported or duplicate encoding headers, invalid text, and binary control bytes block the history check.
Message findings use fixed location labels and verified Git object identifiers.
They never include author identity, tag names, or message excerpts.

`python3 scripts/check_repo.py --release` requires all final public files and the external validators.
Default mode reports an unavailable validator as `SKIP`.
Release mode treats the same missing validator as a failure.
Validator command overrides use JSON argument arrays in `WRITING_DOC_SKILL_VALIDATOR`, `WRITING_DOC_CODEX_VALIDATOR`, and `WRITING_DOC_CLAUDE_VALIDATOR`.
Commands support `{root}` and `{skill}` path placeholders and do not use a shell.

The current five PNGs pass the metadata scan.
Each file lost only its 68-byte `eXIf` payload and 12-byte chunk envelope.
All safe chunks remain byte-for-byte identical. These include `IHDR`, `IDAT`, and `IEND`.
The current Claude marketplace supplies the description that its strict validator requires.

The public repository starts from one reviewed root commit with the final package tree.
Its complete reachable history passes the privacy scan, including the annotated release tag.
Public author, committer, and tagger identities use the GitHub noreply address and receive a separate identity check.
Codex CLI 0.162.1 has no `plugin validate` command.
The release gate uses a private validator override that performs real marketplace registration, installation, listing, and installed-skill byte comparison.
Each validator run uses isolated HOME, CODEX_HOME, and XDG_CONFIG_HOME directories.
It returns failure if a command or byte comparison fails. No validator stub enters the public package.

The public README files exist.
The tagged archive and checksum are public, and anonymous downloads match the local bytes and GitHub asset digest.
Public CLI installation and discovery passed in isolated configurations.
A fresh pinned Codex install/remove trial also passed in isolated HOME, CODEX_HOME, and XDG_CONFIG_HOME directories.
`codex plugin remove writing-doc@writing-doc-skill --json` removes the installed plugin cache and plugin enablement entry.
The plugin list becomes empty. The marketplace registration and source checkout remain.
Optional marketplace removal is a separate operation on the configured source and remains unverified.
The trial used a credential-free environment whitelist and unchanged snapshots of three normal client control files.
The repository has zero registered runners. Equivalent checks run directly on the exact local commit.
The tagged docs retain the candidate snapshot. Current publication evidence lives on `main`.

No GitHub Actions status or billing check serves as the release gate.
Local evidence must identify the exact commit, commands, environment, and results before publication.

These checks detect fixed patterns and structural defects.
They do not prove that all private information is absent.
Ignored untracked files, Git author metadata, unreachable Git objects, and compressed archive contents need separate review when relevant.
Desktop discovery, model requests, other uninstall routes, and user acceptance remain unverified.
The skills.sh skill URL returned HTTP 200 with a missing-skill fallback. The repository page returned HTTP 404.
The package therefore has no verified skills.sh listing or official directory submission.
GitHub private vulnerability reporting is enabled, and all five requested topics are present.
Social-preview upload remains pending. GitHub rejected the original 1,114,198-byte PNG because it exceeds 1 MB.
A separate 972,388-byte lossless copy has identical decoded RGBA pixels and no private PNG metadata.
The browser became unavailable for automation while the user used Safari, so the second upload did not complete.

## Deterministic release archive

A checksum is a file's fingerprint. The same bytes produce the same SHA-256 value.
It checks file identity, not publisher identity or the absence of private data.

`python3 scripts/build_release.py --output dist` builds a local package archive.
The API is `build_release(root: Path, output_dir: Path) -> tuple[Path, str]`.
It returns the archive path and its SHA-256 value.
For version `0.1.0`, the outputs are `writing-doc-skill-v0.1.0.zip` and its `.zip.sha256` sidecar.
The builder does not authorize publication or bypass the release gate.

```mermaid
flowchart TD
    A["Git tracked paths and index modes"] --> B["Reject conflicts, symlinks, submodules, and unsafe paths"]
    B --> C["Exclude design plans and local state"]
    C --> D["Read current regular files and require supported text or valid PNG"]
    D --> Q["Check privacy patterns and PNG metadata"]
    Q --> E["Sort paths and set fixed ZIP time and permissions"]
    E --> F["Write one writing-doc-skill directory without compression"]
    F --> G["Write ZIP and SHA-256 sidecar"]
    G --> H["Compare repeat builds and inspect the archive"]
    H --> I["Publication still requires the full release gate"]
```

The builder reads current contents only for paths from `git ls-files -z`.
The index supplies each file's executable flag. Local timestamps and permissions do not affect archive bytes.
New files enter the archive after `git add`. A modified tracked file enters with its current content.
Release evidence must therefore identify a clean exact commit before publication.

The archive excludes `docs/superpowers/`, `evals/runs/`, `dist/`, and local SDD, validator, worktree, cache, and dependency directories.
The builder rejects unsafe names, case collisions, unreadable files, malformed Git inventories, unresolved index conflicts, symlinks, and submodules.
It opens each source directory without symlink traversal, so a concurrent parent symlink swap cannot redirect a read outside the source tree.
It checks text privacy patterns and PNG metadata before output creation.
It uses the same strict text parser as the repository privacy scanner.
Unsupported encoding, invalid bytes, and forbidden control characters block output creation.
It copies safe PNG bytes without a change.
It reports fixed error text without private values, paths, or Git diagnostics.

Every entry uses `1980-01-01 00:00:00` and Unix permissions `0644` or `0755`.
Names use UTF-8, and every file sits under `writing-doc-skill/`.
The ZIP uses no compression, which avoids compression-library differences between build hosts.
The checksum sidecar names only the ZIP filename. Run `shasum -a 256 -c writing-doc-skill-v0.1.0.zip.sha256` from `dist/`.

Local archive tests cover repeated bytes, exact file sets, Unicode names, permission normalization, checksum contents, CLI exits, and failure paths.
They also cover private text, PNG metadata, source symlinks, destination symlinks, submodules, missing files, and Git errors.
Encoding checks cover all four BOM-less UTF-16 and UTF-32 forms across current files, index blobs, reachable history, deleted history, and archives.
Safe ASCII, UTF-8, text with a BOM, and PNG data retain their accepted behavior.
Archive checks do not inspect Git history or prove client installation.
The Release asset contains the tested tag, with 44 files and 9,368,270 bytes.
Two builds produced identical bytes. The public download has SHA-256 `466d52a773f98ccf196ed93dd79a144862d60e661e4041cdfb4065960fbc660b`.
Later evidence changes on `main` do not rebuild or replace that asset.
The [tagged release note](docs/releases/v0.1.0.md) describes the candidate snapshot.
The [verification record](docs/verification/v0.1.0.md) reports the final publication checks.

最后更新时间：2026-10-16（Asia/Shanghai）
