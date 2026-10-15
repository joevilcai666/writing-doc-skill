"""Check observable Markdown outcomes for the synthetic Lantern API case."""

import argparse
import json
from pathlib import Path
import re

COMMAND = "python -m lantern serve --port 4310"
HEALTH_URL = "http://127.0.0.1:4310/health"
MAX_INTRO_WORDS = 80
MAX_PARAGRAPH_WORDS = 80


def evaluate(text: str, case: dict) -> list[str]:
    """Return stable failure identifiers in rule order, without prose scores."""
    failures = [
        "required-literal:" + literal
        for literal in case["required_literals"]
        if literal not in text
    ]
    command_position = text.find(COMMAND)
    background_position = text.find(case["answer_first_before"])
    if (
        command_position < 0
        or len(text[:command_position].split()) > MAX_INTRO_WORDS
        or (background_position >= 0 and command_position > background_position)
    ):
        failures.append("answer-first")

    # Ignore fenced examples when identifying headings and prose paragraphs.
    prose = re.sub(
        r"^(`{3,}|~{3,}).*?^\1[^\n]*$",
        lambda match: re.sub(r"[^\n]", " ", match.group()),
        text, flags=re.M | re.S,
    )
    headings = list(re.finditer(r"^#{2,6}[ \t]+(.+?)[ \t]*#*[ \t]*$", prose, re.M))
    sections = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(prose)
        sections[heading.group(1).strip().casefold()] = text[heading.end():end]
    for name in case["required_sections"]:
        if name.casefold() not in sections:
            failures.append("missing-section:" + name)

    expected = sections.get("expected result", "")
    if HEALTH_URL not in expected or "HTTP 200" not in expected:
        failures.append("verification")

    for paragraph in re.split(r"\n\s*\n", prose):
        lines = [
            line for line in paragraph.splitlines()
            if not re.match(r"^\s*(?:#{1,6}\s|[-*+]\s|\d+[.)]\s)", line)
        ]
        if len(" ".join(lines).split()) > MAX_PARAGRAPH_WORDS:
            failures.append("long-paragraph")
            break
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, dest="case_id")
    parser.add_argument("document", type=Path)
    args = parser.parse_args()
    cases = json.loads(Path(__file__).with_name("cases.json").read_text(encoding="utf-8"))
    case = next((item for item in cases if item["id"] == args.case_id), None)
    if case is None:
        parser.error("unknown case: " + args.case_id)
    try:
        text = args.document.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        parser.error(str(error))
    failures = evaluate(text, case)
    if failures:
        print("FAIL " + case["id"])
        for failure in failures:
            print(failure)
        return 1
    print("PASS " + case["id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
