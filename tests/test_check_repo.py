"""Repository gates run against disposable, independently assembled packages."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.check_repo import check_markdown_links, check_structure
from tests.test_privacy_scan import git, png_bytes

ROOT = Path(__file__).resolve().parents[1]


class RepositoryCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("VERSION", "LICENSE", "HOW_IT_WORKS.md", "plugin.json",
                     ".codex-plugin/plugin.json", ".claude-plugin/plugin.json",
                     ".claude-plugin/marketplace.json", "skills/writing-doc/SKILL.md",
                     "skills/writing-doc/agents/openai.yaml", "demo/README.md",
                     "demo/source/AI_SETUP_GUIDE.md", "demo/expected/SETUP_GUIDE.md",
                     "evals/cases.json", "evals/README.md", "evals/run_rubric.py",
                     "scripts/check_repo.py", "scripts/privacy_scan.py",
                     "tests/__init__.py", "tests/test_privacy_scan.py", "tests/test_check_repo.py"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Public sample\n")
        (self.root / "VERSION").write_text("0.1.0\n")
        for name in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
            (self.root / name).write_text(json.dumps({"name": "writing-doc", "version": "0.1.0"}))
        (self.root / ".claude-plugin/marketplace.json").write_text(json.dumps({
            "name": "writing-doc-skill", "plugins": [{"name": "writing-doc", "version": "0.1.0"}]}))
        (self.root / "evals/cases.json").write_text("[]")
        (self.root / "skills/writing-doc/SKILL.md").write_text(
            '---\nname: writing-doc\ndescription: "Clear technical documents."\n---\n\n# Skill\n')
        (self.root / "assets").mkdir()
        for name in ("x-problem-en.png", "x-solution-en.png", "x-problem-zh-CN.png", "x-solution-zh-CN.png"):
            (self.root / "assets" / name).write_bytes(png_bytes(1200, 1200))
        (self.root / "assets/social-preview.png").write_bytes(png_bytes(1280, 640))

    def test_clean_current_stage_package_passes_without_future_readmes(self):
        self.assertEqual(check_structure(self.root), [])
        self.assertEqual(check_markdown_links(self.root), [])

    def test_missing_skill_fails(self):
        (self.root / "skills/writing-doc/SKILL.md").unlink()
        self.assertTrue(any("SKILL.md" in item for item in check_structure(self.root)))

    def test_inconsistent_manifest_and_marketplace_versions_fail(self):
        for name in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json",
                     ".claude-plugin/marketplace.json"):
            with self.subTest(path=name):
                path = self.root / name
                original = path.read_text()
                path.write_text(original.replace("0.1.0", "0.2.0"))
                self.assertTrue(any("version" in item for item in check_structure(self.root)))
                path.write_text(original)

    def test_invalid_json_and_duplicate_keys_fail_without_exception(self):
        path = self.root / "plugin.json"
        for content in ('{"name":', '{"version":"0.2.0","version":"0.1.0"}', '[]', 'null'):
            path.write_text(content)
            self.assertTrue(check_structure(self.root))

    def test_invalid_other_json_fails(self):
        (self.root / "evals/cases.json").write_text("{")
        self.assertTrue(any("json" in item.lower() for item in check_structure(self.root)))

    def test_invalid_version_and_empty_marketplace_fail(self):
        (self.root / "VERSION").write_text("not-a-version")
        self.assertTrue(check_structure(self.root))
        (self.root / "VERSION").write_text("0.1.0\n")
        (self.root / ".claude-plugin/marketplace.json").write_text('{"plugins": []}')
        self.assertTrue(check_structure(self.root))

    def test_skill_requires_valid_frontmatter(self):
        path = self.root / "skills/writing-doc/SKILL.md"
        for text in ("# no frontmatter", "---\nname: other\n---\n",
                     '---\nname: writing-doc\ndescription: "unterminated\n---\n',
                     "---\nname: writing-doc\nname: other\ndescription: text\n---\n"):
            path.write_text(text)
            self.assertTrue(check_structure(self.root))

    def test_missing_and_wrong_dimension_pngs_fail(self):
        path = self.root / "assets/x-problem-en.png"
        path.unlink()
        self.assertTrue(check_structure(self.root))
        path.write_bytes(png_bytes(1199, 1200))
        self.assertTrue(any("dimensions" in item for item in check_structure(self.root)))
        path.write_bytes(b"not an image")
        self.assertTrue(check_structure(self.root))

    def test_readme_requires_problem_and_solution_images_for_its_language(self):
        path = self.root / "README.md"
        path.write_text("# Documentation\n")
        self.assertTrue(any("image" in item for item in check_structure(self.root)))
        path.write_text("![Problem](assets/x-problem-en.png)\n![Solution](assets/x-solution-en.png)")
        self.assertEqual(check_structure(self.root), [])

    def test_missing_inline_reference_and_html_links_fail(self):
        path = self.root / "HOW_IT_WORKS.md"
        for text in ("[Read](missing.md)", "![Image](assets/missing.png)",
                     "[Read][guide]\n\n[guide]: missing.md", '<img src="assets/missing.png">',
                     '<a href="missing.md">Read</a>'):
            with self.subTest(kind=text[:4]):
                path.write_text(text)
                self.assertTrue(check_markdown_links(self.root))

    def test_relative_encoded_nested_and_parenthesized_links_pass(self):
        (self.root / "docs/a (b).md").parent.mkdir(exist_ok=True)
        (self.root / "docs/a (b).md").write_text("# Guide\n[Home](../HOW_IT_WORKS.md)")
        (self.root / "HOW_IT_WORKS.md").write_text(
            '[Guide](docs/a%20%28b%29.md#guide)\n[Guide](<docs/a (b).md>)\n'
            '[Guide](docs/a%20(b).md "Title")\n[License][license]\n\n[license]: LICENSE\n'
            '[Web](https://example.invalid/no-request)\n[Section](#local)')
        self.assertEqual(check_markdown_links(self.root), [])

    def test_fenced_and_inline_code_are_not_links(self):
        (self.root / "HOW_IT_WORKS.md").write_text(
            '```md\n[example](missing.md)\n```\n`[example](missing.md)`\n')
        self.assertEqual(check_markdown_links(self.root), [])

    def test_relative_links_cannot_escape_package(self):
        (self.root / "HOW_IT_WORKS.md").write_text("[Escape](../outside.md)")
        self.assertTrue(check_markdown_links(self.root))

    def test_empty_and_unclosed_markdown_destinations_fail(self):
        for text in ("[Guide]()", "[Guide](<missing.md)"):
            (self.root / "HOW_IT_WORKS.md").write_text(text)
            self.assertTrue(check_markdown_links(self.root))

    def test_deep_json_fails_without_exception(self):
        (self.root / "deep.json").write_text("[" * 2000 + "0" + "]" * 2000)
        self.assertTrue(check_structure(self.root))

    def test_reference_images_satisfy_readme_image_requirement(self):
        (self.root / "README.md").write_text(
            "![Problem][problem]\n![Solution][solution]\n\n"
            "[problem]: assets/x-problem-en.png\n[solution]: assets/x-solution-en.png\n")
        self.assertEqual(check_structure(self.root), [])

    def test_checker_suppresses_external_validator_output(self):
        value = "gh" + "p_" + "A" * 30
        env = dict(os.environ)
        for kind in ("SKILL", "CODEX", "CLAUDE"):
            env["WRITING_DOC_" + kind + "_VALIDATOR"] = json.dumps(
                [sys.executable, "-c", "import sys; print(" + repr(value) + "); sys.exit(1)"])
        result = subprocess.run([sys.executable, str(ROOT / "scripts/check_repo.py"),
                                 "--root", str(self.root)], capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(value, result.stdout + result.stderr)
        self.assertIn("validator-command-failed", result.stdout)

    def test_default_checks_current_state_and_release_checks_history(self):
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Synthetic Fixture")
        git(self.root, "config", "user.email", "fixture" + "@" + "example.invalid")
        path = self.root / "deleted.md"
        path.write_text("gh" + "p_" + "A" * 30)
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "temporary fixture")
        git(self.root, "rm", "-q", "deleted.md")
        git(self.root, "commit", "-qm", "remove fixture")
        env = dict(os.environ)
        for kind in ("SKILL", "CODEX", "CLAUDE"):
            env["WRITING_DOC_" + kind + "_VALIDATOR"] = json.dumps([sys.executable, "-c", "pass"])
        command = [sys.executable, str(ROOT / "scripts/check_repo.py"), "--root", str(self.root)]
        current = subprocess.run(command, capture_output=True, text=True, env=env)
        release = subprocess.run(command + ["--release"], capture_output=True, text=True, env=env)
        self.assertIn("PASS privacy-current-index\n", current.stdout)
        self.assertIn("FAIL privacy-current-index-history\n", release.stdout)

    def test_empty_test_suite_cannot_pass_unit_gate(self):
        for path in (self.root / "tests").glob("*.py"):
            path.write_text("# No tests in this fixture.\n")
        result = subprocess.run([sys.executable, str(ROOT / "scripts/check_repo.py"),
                                 "--root", str(self.root)], capture_output=True, text=True)
        self.assertIn("FAIL unit-tests\n", result.stdout)

    def test_release_mode_requires_future_public_documents_and_validators(self):
        env = dict(os.environ)
        env["WRITING_DOC_SKILL_VALIDATOR"] = json.dumps(["missing-writing-doc-validator"])
        result = subprocess.run([sys.executable, str(ROOT / "scripts/check_repo.py"),
                                 "--root", str(self.root), "--release"],
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 1)
        self.assertIn("README.md", result.stdout)
        self.assertIn("validator", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
