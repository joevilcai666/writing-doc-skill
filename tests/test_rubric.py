from pathlib import Path
import json
import sys
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "evals"))
from run_rubric import evaluate


class RubricTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))[0]

    def test_verbose_source_fails_reader_outcomes(self):
        text = (ROOT / "demo/source/AI_SETUP_GUIDE.md").read_text(encoding="utf-8")
        failures = evaluate(text, self.case)
        self.assertIn("answer-first", failures)
        self.assertIn("verification", failures)

    def test_expected_document_passes(self):
        text = (ROOT / "demo/expected/SETUP_GUIDE.md").read_text(encoding="utf-8")
        self.assertEqual(evaluate(text, self.case), [])

    def test_expected_document_preserves_technical_literals(self):
        text = (ROOT / "demo/expected/SETUP_GUIDE.md").read_text(encoding="utf-8")
        for literal in self.case["required_literals"]:
            self.assertIn(literal, text)

    def expected_text(self):
        return (ROOT / "demo/expected/SETUP_GUIDE.md").read_text(encoding="utf-8")

    def test_each_missing_literal_has_a_stable_identifier(self):
        for literal in self.case["required_literals"]:
            with self.subTest(literal=literal):
                failures = evaluate(self.expected_text().replace(literal, "omitted"), self.case)
                self.assertIn("required-literal:" + literal, failures)

    def test_each_missing_section_has_a_stable_identifier(self):
        for name in self.case["required_sections"]:
            with self.subTest(name=name):
                text = self.expected_text().replace("## " + name, "## Other topic")
                self.assertIn("missing-section:" + name, evaluate(text, self.case))

    def test_status_elsewhere_does_not_supply_verification(self):
        text = self.expected_text().replace("returns `HTTP 200`", "returns a response")
        text += "\nThe unrelated status literal is HTTP 200.\n"
        self.assertEqual(evaluate(text, self.case), ["verification"])

    def test_long_paragraph_has_one_stable_identifier(self):
        text = self.expected_text() + "\n" + "word " * 81 + "\n\n" + "word " * 81
        self.assertEqual(evaluate(text, self.case), ["long-paragraph"])

    def test_answer_after_background_fails(self):
        text = "## Why this service exists\n\nBackground.\n\n" + self.expected_text()
        self.assertEqual(evaluate(text, self.case), ["answer-first"])

    def test_answer_after_long_introduction_fails(self):
        text = "word " * 81 + "\n\n" + self.expected_text()
        self.assertEqual(evaluate(text, self.case), ["answer-first", "long-paragraph"])

    def test_prose_and_heading_case_can_change(self):
        text = self.expected_text().replace("Run Lantern API locally", "Start your local service")
        for name in self.case["required_sections"]:
            text = text.replace("## " + name, "## " + name.upper())
        self.assertEqual(evaluate(text, self.case), [])

    def test_fenced_status_is_valid_verification(self):
        text = self.expected_text().replace("returns `HTTP 200`.", "returns:\n\n```text\nHTTP 200\n```\n")
        self.assertEqual(evaluate(text, self.case), [])

    def test_fenced_result_can_supply_the_entire_verification(self):
        before, result = self.expected_text().split("## Expected result\n", 1)
        _, after = result.split("## Troubleshooting", 1)
        text = before + "## Expected result\n\n```text\nhttp://127.0.0.1:4310/health\nHTTP 200\n```\n\n## Troubleshooting" + after
        self.assertEqual(evaluate(text, self.case), [])

    def test_code_example_cannot_supply_a_required_heading(self):
        text = self.expected_text().replace("## Prerequisites", "```text\n## Prerequisites\n```")
        self.assertIn("missing-section:Prerequisites", evaluate(text, self.case))

    def test_cli_pass_and_failure(self):
        for document, code, prefix in (
            ("demo/expected/SETUP_GUIDE.md", 0, "PASS lantern-setup"),
            ("demo/source/AI_SETUP_GUIDE.md", 1, "FAIL lantern-setup"),
        ):
            with self.subTest(document=document):
                result = subprocess.run(
                    [sys.executable, str(ROOT / "evals/run_rubric.py"), "--case", "lantern-setup", str(ROOT / document)],
                    capture_output=True, text=True,
                )
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(result.stdout.splitlines()[0], prefix)

    def test_cli_unknown_case_reports_input_error(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "evals/run_rubric.py"), "--case", "unknown", str(ROOT / "demo/expected/SETUP_GUIDE.md")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown case: unknown", result.stderr)
