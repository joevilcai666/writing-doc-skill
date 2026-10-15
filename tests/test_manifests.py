from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/joevilcai666/writing-doc-skill"


class ManifestTests(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((ROOT / name).read_text(encoding="utf-8"))

    def test_release_identity_is_consistent(self):
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version, "0.1.0")
        portable = self.load("plugin.json")
        codex = self.load(".codex-plugin/plugin.json")
        claude = self.load(".claude-plugin/plugin.json")
        market = self.load(".claude-plugin/marketplace.json")
        for manifest in (portable, codex, claude):
            with self.subTest(name=manifest):
                self.assertEqual(manifest["name"], "writing-doc")
                self.assertEqual(manifest["version"], version)
                self.assertEqual(manifest["repository"], REPOSITORY)
                self.assertEqual(manifest["license"], "MIT")
                self.assertEqual(manifest["author"], {"name": "Writing Doc Contributors"})
        self.assertEqual(market["name"], "writing-doc-skill")
        self.assertTrue(isinstance(market.get("description"), str) and market["description"].strip())
        self.assertEqual(market["owner"], {"name": "Writing Doc Contributors"})
        self.assertEqual(len(market["plugins"]), 1)
        entry = market["plugins"][0]
        self.assertEqual(entry["name"], "writing-doc")
        self.assertEqual(entry["version"], version)
        self.assertEqual(entry["source"], "./")
        self.assertEqual(entry["repository"], REPOSITORY)
        self.assertEqual(entry["license"], "MIT")

    def test_portable_manifest_declares_schema_without_client_paths(self):
        portable = self.load("plugin.json")
        self.assertEqual(
            portable["$schema"],
            "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        )
        self.assertNotIn("skills", portable)

    def test_codex_points_to_shared_skill_directory(self):
        codex = self.load(".codex-plugin/plugin.json")
        self.assertEqual(codex["skills"], "./skills/")
        # Task 2 owns the SKILL.md file and its existence check.

    def test_openai_yaml_uses_explicit_skill_name(self):
        text = (ROOT / "skills/writing-doc/agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Writing Doc"', text)
        self.assertIn("$writing-doc", text)
        self.assertIn("allow_implicit_invocation: true", text)
        self.assertNotIn("allow_implicit_invocation: false", text)
