# Report a security problem privately

Use [GitHub private vulnerability reporting](https://github.com/joevilcai666/writing-doc-skill/security/advisories/new) for a suspected vulnerability or private-data leak.
Do not open public issues with credentials, private documents, private URLs, personal data, or full conversation transcripts.

The private form requires a published repository with private vulnerability reporting enabled.
If the form is unavailable, withhold sensitive details. Do not move the report to a public issue.
This release candidate does not yet establish that the public reporting form is available.

## What to include

- The affected package version or commit.
- A short description of the problem and its effect.
- Minimal reproduction steps with synthetic values.
- The client and tool versions needed to reproduce the issue.

If a credential leaked, revoke or rotate it through its provider.
Do not paste the credential into the report.

## Scope and current limits

Relevant reports include private data in package files, unsafe package paths, and privacy-check defects.
The privacy scanner detects specific patterns. It cannot prove that all sensitive information is absent.
Client, model-provider, and third-party installer behavior remains subject to those projects' policies.

Version `0.1.0` is the first planned release. No public support history or response-time guarantee exists yet.
See [current behavior and limits](HOW_IT_WORKS.md) for the package's actual checks.
