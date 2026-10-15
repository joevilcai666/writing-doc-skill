# writing-doc

English · [简体中文](README.zh-CN.md)

**AI wrote a lot. Your reader still does not get it.**

<img src="assets/x-problem-en.png" width="600" alt="AI wrote a lot. Your reader still doesn't get it. Too many words. Not enough point. Every sentence sounds right. Nothing feels clear. They finish reading. They still can't act. AI generated text. It didn't communicate.">

writing-doc turns AI output into clear, useful documentation your audience can understand and act on.

<img src="assets/x-solution-en.png" width="600" alt="Make your audience get it—fast. Put the answer first. Keep only what they need. Turn every step into action. writing-doc turns AI output into clear, useful communication.">

## Install

**Public installation verified for v0.1.0.** The default-branch and tagged `skills` routes passed in isolated projects with skills 1.7.2. See the [exact verification record](docs/verification/v0.1.0.md).

With Node.js, npm, and Git available, run this command in your project:

```sh
npx skills add joevilcai666/writing-doc-skill --skill writing-doc
```

Choose your agent when the installer asks. This command selects the repository's current default branch. See [version pinning](#pin-a-version) for a fixed version.

[See the difference](#see-the-difference) · [Use it](#give-it-a-reader-and-a-task) · [Other install methods](#other-install-methods) · [Privacy](#privacy) · [Evidence](#what-is-verified)

## See the difference

A setup guide can explain processes, configuration, and response codes—and still leave a developer unsure which command to run.

writing-doc puts the task first:

> Start Lantern API on port 4310 with this command after you complete the prerequisites:
>
> `python -m lantern serve --port 4310`

The [revised guide](demo/expected/SETUP_GUIDE.md) then gives prerequisites, three steps, the expected `HTTP 200` response, and a fix for a connection failure. It preserves the source commands, address, version, and warning.

Compare the [full source](demo/source/AI_SETUP_GUIDE.md) and [full revision](demo/expected/SETUP_GUIDE.md), or read the [demo notes](demo/README.md).

Lantern API is fictional. A person wrote this example to show the intended result. It is not a measured agent run or a live service test.

## Give it a reader and a task

After installation, ask your agent to use `writing-doc`. Include the source, target reader, and job the document must help them complete.

```text
Use writing-doc to rewrite this setup guide for a developer who needs
to run the service locally. Put the command first. Preserve the facts,
commands, links, and warnings. Include a way to check success.
```

For feedback without file edits:

```text
Use writing-doc to review this README for a first-time contributor.
List the points that block their first contribution and suggest fixes.
Review only. Do not edit files.
```

The skill keeps your language. Its instructions are in Chinese, but it also supports English document requests.

## Use it when readers need to understand and do something

| Document | What the skill helps the reader do |
| --- | --- |
| README | Find the product's purpose and complete the first useful task. |
| Setup guide or tutorial | Meet prerequisites, follow steps, and check the result. |
| API documentation | Find the right call, preserve parameters, and understand the response. |
| Technical design or explanation | Understand the decision, terms, and necessary detail. |
| Existing technical document | Find unclear points through a review, or improve them through a rewrite. |

The skill puts answers first, removes filler, and keeps the detail the task needs. It preserves technical facts and necessary conditions.

Its scope excludes marketing copy, literary writing, and format-only conversion. It does not supply missing product facts or guarantee correct output. The source and the agent's tools determine what the agent can verify.

## Other install methods

The Codex CLI plugin and Claude Code routes below passed public installation checks. Desktop selection and model behavior remain unverified. Install one copy for your chosen agent to avoid duplicate skill entries.

### Codex

The Codex CLI route passed with version 0.162.1:

```sh
codex plugin marketplace add joevilcai666/writing-doc-skill --ref v0.1.0 --json
codex plugin add writing-doc@writing-doc-skill --json
codex plugin list --json
```

The plugin appeared installed and enabled. Its installed `SKILL.md` matched the tag byte for byte.

Use the built-in Skill Installer in a Codex chat:

```text
$skill-installer install https://github.com/joevilcai666/writing-doc-skill/tree/v0.1.0/skills/writing-doc
```

This separate Skill Installer route remains **Planned for v0.1.0 verification**. It installs the shared skill. Confirm that `writing-doc` appears in the skill selector. If it does not appear, restart Codex. See the [official local skill guidance](https://learn.chatgpt.com/docs/build-skills#install-curated-skills-for-local-use).

Plugin installation through the OpenAI directory remains unverified. No official directory submission or listing exists.

### Claude Code

Run these commands in your shell with Git and Claude Code available:

```sh
claude plugin marketplace add joevilcai666/writing-doc-skill
claude plugin install writing-doc@writing-doc-skill --scope local
```

These commands passed with Claude Code 2.1.295 in isolated homes. The CLI listed the plugin as enabled, and the installed skill matched the source. The marketplace registration applies to your user account. The plugin's local scope applies only to you in the current project. Start a new Claude Code session, then confirm that the plugin appears in `/plugin`.

See the [official Claude Code installation guide](https://code.claude.com/docs/en/discover-plugins).

### Pin a version

Use a tag to keep the skill source fixed. The quick install command above tracks the default branch.

For `skills`, use the direct tagged path:

```sh
npx skills add https://github.com/joevilcai666/writing-doc-skill/tree/v0.1.0/skills/writing-doc --skill writing-doc
```

For Claude Code, use either the current-branch registration or the tagged registration. Before you replace an existing registration, check the removal effects.

`claude plugin marketplace remove writing-doc-skill` can uninstall plugins from this marketplace and remove their enabled settings. The command without `--scope` removes marketplace declarations from every settings scope. This can affect copies outside the current project.

If you choose to switch, run that removal command. Then add the tagged marketplace:

```sh
claude plugin marketplace add joevilcai666/writing-doc-skill#v0.1.0
```

After you add the tagged marketplace, reinstall the affected copies in their original scopes. For a local copy, repeat `claude plugin install writing-doc@writing-doc-skill --scope local`.

A Git tag fixes the skill source, not the version of your installer or agent. Tagged `skills`, Codex CLI, and Claude marketplace installations passed. Replacement of an existing marketplace registration remains unverified.

### Manual installation

With Git available, clone the tagged source into a new directory:

```sh
git clone --depth 1 --branch v0.1.0 https://github.com/joevilcai666/writing-doc-skill.git
```

Copy the entire `skills/writing-doc` folder to your client's skill directory. For a Codex project, use `.agents/skills/writing-doc`. The tagged clone and this folder copy passed a byte comparison. Client discovery remains unverified. Keep `SKILL.md` inside that folder. If a `writing-doc` folder already exists, compare it before you replace anything.

For other clients, use their documented Agent Skills directory. Confirm that the client lists `writing-doc`, then try a small synthetic document.

## Uninstall

Use the route that matches your installation:

- Codex CLI plugin: run `codex plugin remove writing-doc@writing-doc-skill --json`. This removes the installed plugin and its local plugin cache. A fresh isolated public v0.1.0 install/remove trial passed with Codex 0.162.1.
- `skills`: run `npx skills remove writing-doc` in the same project. Select the same agent and scope. Add `--global` only for a global installation.
- Claude Code: for removal from the current project's local scope only, use `claude plugin uninstall writing-doc@writing-doc-skill --scope local`. Use your original scope if it differs.
- Codex Skill Installer or manual copy: locate the installed `writing-doc` folder and move that folder out of the client's skill directory. Restart the client if its skill list does not refresh.

Codex marketplace removal is optional and separate from plugin removal. Use `codex plugin marketplace remove writing-doc-skill --json` only to remove the configured marketplace source. Plugin removal retains the marketplace registration. Marketplace removal affects that source configuration and its availability for future plugin discovery. This optional command remains unverified.

To remove the Claude marketplace itself, use `claude plugin marketplace remove writing-doc-skill`. This can uninstall plugins from that marketplace and remove their enabled settings. The command without `--scope` removes marketplace declarations from every settings scope. It can affect copies outside the current project. Prefer the scoped plugin-uninstall command above for local removal only. See the [Claude CLI reference](https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-remove) for the marketplace command's scope.

Other removal routes also await public verification: **Planned for v0.1.0 verification**. They do not remove documents you created with the skill.

## Privacy

The package adds no analytics, telemetry, remote service, or background process. The skill itself does not upload documents. It guides the agent that reads the material you provide.

Your agent, model provider, tools, and installer have their own data policies. The third-party `skills` CLI documents anonymous telemetry. Its [telemetry controls](https://github.com/vercel-labs/skills#telemetry) include `DISABLE_TELEMETRY=1`.

The package does not modify `AGENTS.md`, `CLAUDE.md`, or global agent instructions. Installers can update their own skill directories and client settings. Public examples use synthetic material.

## What is verified

| Evidence | Current status |
| --- | --- |
| Implemented | One shared skill, client manifests, approved visuals, synthetic demo, and local checks exist. |
| Locally verified | The exact release commit passed 125 tests, the full release gate, full-history privacy checks, the skill validator, real isolated Codex installation, and Claude strict validation. |
| Publicly verified | Anonymous main/tag clones, the Release ZIP and checksum, default/tagged `skills` installations, Codex pinned plugin installation/removal, and Claude main/tag plugin installations passed. Installed skills matched the tag. |
| User accepted | No acceptance evidence exists for this package implementation. |

Release [v0.1.0](https://github.com/joevilcai666/writing-doc-skill/releases/tag/v0.1.0) is public. Codex CLI 0.162.1 has no `plugin validate` command. The release gate used real marketplace installation and a byte comparison instead. Model behavior, reader outcomes, desktop discovery, and other removal routes remain unverified. See [current behavior and limits](HOW_IT_WORKS.md) and [distribution status](docs/distribution.md).

## Help improve the next reader's experience

Report a bug, a client compatibility issue, or a task the skill handles poorly through [GitHub issues](https://github.com/joevilcai666/writing-doc-skill/issues). Include a small synthetic example.

Read [CONTRIBUTING](CONTRIBUTING.md) for local checks. Use [SECURITY](SECURITY.md) for private vulnerability reports. The package uses the [MIT license](LICENSE).
