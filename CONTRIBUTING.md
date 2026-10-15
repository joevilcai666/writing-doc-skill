# Contribute to writing-doc

Help a reader find the answer, understand it, and complete a task.
Keep `skills/writing-doc/SKILL.md` as the only authoritative writing workflow.

## Report a problem

Use the bug template for a wrong or unclear result.
Use the compatibility template for a client installation or discovery problem.
Use the feature template for a reader task that needs better support.

Include the client version, package version or commit, expected result, and observed result.
Use a minimal synthetic document that reproduces the problem.
Do not include real user documents, credentials, private URLs, personal paths, or conversation transcripts.
Report security issues through [SECURITY.md](SECURITY.md).

## Make a focused change

1. Explain the reader task and the problem your change fixes.
2. Keep correct facts, commands, links, warnings, and language intact.
3. Use only synthetic fixtures and public source material.
4. Add a failing behavioral test before a code change. Run the test to confirm the failure.
5. Make the smallest change that resolves the problem. Run the local checks below.

Human prose does not need tests for every sentence.
The release tests protect required language paths, approved assets, and evidence labels.
For evaluation, check reader outcomes and technical facts rather than exact generated prose.

## Run the local checks

Use Python 3.9 or later and Git from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 evals/run_rubric.py --case lantern-setup demo/expected/SETUP_GUIDE.md
python3 scripts/check_repo.py
git diff --check
```

The unit command must report a nonempty passing suite.
The rubric must print `PASS lantern-setup`.
The repository checker must end with `PASS repository`.
Default mode can report `SKIP` for an unavailable external validator. A skip is not a validation pass.

Before publication, run the stricter gate:

```sh
python3 scripts/check_repo.py --release
```

Release mode requires the complete public package, history checks, and all required external validators.
See [HOW_IT_WORKS.md](HOW_IT_WORKS.md) for current blockers and validator configuration.
GitHub Actions status is not a release requirement.

## Keep the evidence honest

Record the exact commit, commands, environment, exit codes, and limits of each check.
Distinguish implementation, local verification, public verification, and user acceptance.
Do not describe a planned command as a passed check.
The synthetic demo does not prove real agent performance or reader comprehension.

If a change affects the core workflow, architecture, agent behavior, or visible product behavior, update [HOW_IT_WORKS.md](HOW_IT_WORKS.md).
Update its affected Mermaid diagrams, current limits, evidence, and final update date.
Describe the current system rather than a history of changes.

Keep the English and Chinese README paths equivalent.
Preserve the approved images and their original copy.
Update [CHANGELOG.md](CHANGELOG.md) for a user-visible release change.

## Open a pull request

State the problem, resulting behavior, and checks you actually ran.
Link any issue and identify remaining limits.
Use the [pull request template](.github/pull_request_template.md).
Contributions use the repository's [MIT license](LICENSE).
