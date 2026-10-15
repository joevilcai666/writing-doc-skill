# Local documentation rubric

Run the rubric from the repository root:

```sh
python3 -m unittest tests.test_rubric -v
python3 evals/run_rubric.py --case lantern-setup demo/expected/SETUP_GUIDE.md
```

The command prints `PASS lantern-setup` and exits with code 0 for a pass.
For rule failures, it prints `FAIL lantern-setup`, lists rule identifiers, and exits with code 1.
Invalid arguments or unreadable files produce code 2.

`evaluate(text: str, case: dict) -> list[str]` returns an empty list for a pass.
`cases.json` defines the single supported case, its exact technical literals, background marker, and required section names.

| Rule identifier | Observable condition |
| --- | --- |
| `required-literal:<value>` | A required technical literal is absent. |
| `answer-first` | The start command is absent, follows more than 80 whitespace-separated words, or follows the configured background marker. |
| `missing-section:<name>` | A required level 2–6 Markdown heading is absent. Heading case does not matter. |
| `verification` | The Expected result section does not contain both the health URL and `HTTP 200`. |
| `long-paragraph` | A prose paragraph exceeds 80 whitespace-separated words. |

Failures appear in the table order. Literal and section failures follow case order.
Each non-literal rule appears at most once.
The paragraph check excludes fenced code, heading lines, and list marker lines.
The section check excludes headings inside fenced code.
The Expected result section can contain the health URL and status in prose or code.

These fixed checks are limited proxies for reader outcomes. They do not score exact prose or marketing language.
The [expected document](../demo/expected/SETUP_GUIDE.md) is synthetic and illustrates one acceptable result.
The checks do not prove factual correctness, reader comprehension, language retention, review-only behavior, or real agent performance.
They do not start a service or contact the health URL.
Manual review and real client sessions remain necessary for broader behavior evidence.
