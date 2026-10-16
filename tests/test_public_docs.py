"""Release contracts for the public reader paths specified in Task 5."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DOCS = ("README.md", "README.zh-CN.md", "HOW_IT_WORKS.md", "docs/distribution.md")


class PublicDocumentTests(unittest.TestCase):
    def read(self, name):
        return (ROOT / name).read_text(encoding="utf-8")

    def test_readmes_use_approved_message_and_image_order(self):
        for name, language, message, promise in (
            ("README.md", "en", "AI wrote a lot. Your reader still does not get it.",
             "writing-doc turns AI output into clear, useful documentation your audience can understand and act on."),
            ("README.zh-CN.md", "zh-CN", "AI 写了一大篇，读完还是不懂。",
             "writing-doc 把 AI 输出变成目标读者看得懂、用得上、能照着行动的文档。"),
        ):
            with self.subTest(name=name):
                text = self.read(name)
                problem = "assets/x-problem-" + language + ".png"
                solution = "assets/x-solution-" + language + ".png"
                self.assertLess(text.index(message), text.index(problem))
                self.assertLess(text.index(problem), text.index(promise))
                self.assertLess(text.index(promise), text.index(solution))

    def test_language_and_demo_paths_resolve(self):
        for name, other in (("README.md", "README.zh-CN.md"), ("README.zh-CN.md", "README.md")):
            with self.subTest(name=name):
                text = self.read(name)
                for target in (other, "demo/README.md", "demo/source/AI_SETUP_GUIDE.md",
                               "demo/expected/SETUP_GUIDE.md", "CONTRIBUTING.md", "SECURITY.md",
                               "HOW_IT_WORKS.md", "docs/distribution.md"):
                    self.assertIn("](" + target + ")", text)
                    self.assertTrue((ROOT / target).is_file(), target)

    def test_readmes_offer_install_use_and_remove_routes_with_pending_evidence(self):
        for name, install, privacy, boundary, uninstall in (
            ("README.md", "## Install", "## Privacy", "marketing copy", "## Uninstall"),
            ("README.zh-CN.md", "## 安装", "## 隐私", "营销文案", "## 卸载"),
        ):
            with self.subTest(name=name):
                text = self.read(name)
                for item in (install, privacy, boundary, uninstall, "Codex", "Claude Code",
                             "npx", "--skill writing-doc", "v0.1.0", "Planned for v0.1.0 verification"):
                    self.assertIn(item, text)

    def test_docs_distinguish_evidence_levels_without_approval_claims(self):
        combined = "\n".join(self.read(name) for name in PUBLIC_DOCS)
        self.assertNotIn("officially approved", combined.lower())
        for level in ("Implemented", "Locally verified", "Publicly verified", "User accepted"):
            self.assertIn(level, self.read("HOW_IT_WORKS.md"))
        self.assertIn("Planned for v0.1.0 verification", self.read("README.md"))

    def test_removal_sections_preserve_command_routes_and_pending_evidence(self):
        for name, heading, next_heading, pending, manual in (
            ("README.md", "## Uninstall", "## Privacy", "await public verification",
             ("Codex Skill Installer", "manual", "skill directory")),
            ("README.zh-CN.md", "## 卸载", "## 隐私", "尚未通过公开验证",
             ("Codex Skill Installer", "手动复制", "移出客户端技能目录")),
        ):
            with self.subTest(name=name):
                removal = self.read(name).split(heading, 1)[1].split(next_heading, 1)[0]
                for token in ("npx skills remove writing-doc", "--global",
                              "claude plugin uninstall writing-doc@writing-doc-skill --scope local",
                              "claude plugin marketplace remove writing-doc-skill",
                              "Planned for v0.1.0 verification", pending, *manual):
                    self.assertIn(token, removal)

    def test_marketplace_removal_effects_appear_at_version_switch_and_uninstall(self):
        for name, version, manual, uninstall, privacy, effects, reinstall, scopes in (
            ("README.md", "### Pin a version", "### Manual installation", "## Uninstall", "## Privacy",
             ("uninstall plugins", "enabled settings", "every settings scope", "without `--scope`"),
             "reinstall", "original scopes"),
            ("README.zh-CN.md", "### 固定版本", "### 手动安装", "## 卸载", "## 隐私",
             ("卸载该市场的插件", "启用配置", "所有设置范围", "未指定 `--scope`"),
             "重新安装", "原来的范围"),
        ):
            with self.subTest(name=name):
                text = self.read(name)
                switch = text.split(version, 1)[1].split(manual, 1)[0]
                removal = text.split(uninstall, 1)[1].split(privacy, 1)[0]
                for section in (switch, removal):
                    for token in ("claude plugin marketplace remove writing-doc-skill", *effects):
                        self.assertIn(token, section)
                self.assertIn(reinstall, switch)
                self.assertIn(scopes, switch)
                self.assertIn("claude plugin uninstall writing-doc@writing-doc-skill --scope local", removal)

    def test_codex_plugin_removal_has_separate_optional_marketplace_route(self):
        for name, heading, next_heading, effects in (
            ("README.md", "## Uninstall", "## Privacy",
             ("local plugin cache", "marketplace registration", "configured marketplace source", "optional")),
            ("README.zh-CN.md", "## 卸载", "## 隐私",
             ("本地插件缓存", "市场注册", "已配置的市场源", "可选")),
        ):
            with self.subTest(name=name):
                removal = self.read(name).split(heading, 1)[1].split(next_heading, 1)[0]
                self.assertIn("codex plugin remove writing-doc@writing-doc-skill --json", removal)
                self.assertIn("codex plugin marketplace remove writing-doc-skill --json", removal)
                for effect in effects:
                    self.assertIn(effect, removal)

    def test_privacy_distinguishes_package_from_installer_telemetry(self):
        for name, heading, next_heading, package_tokens, installer_tokens in (
            ("README.md", "## Privacy", "## What is verified",
             ("package adds no", "telemetry", "does not upload documents"),
             ("third-party", "`skills` CLI", "telemetry", "DISABLE_TELEMETRY=1")),
            ("README.zh-CN.md", "## 隐私", "## 目前验证到了哪一步",
             ("本包不添加", "遥测", "不会上传文档"),
             ("第三方", "`skills` CLI", "匿名使用数据", "DISABLE_TELEMETRY=1")),
        ):
            with self.subTest(name=name):
                section = self.read(name).split(heading, 1)[1].split(next_heading, 1)[0]
                paragraphs = section.strip().split("\n\n")
                for token in package_tokens:
                    self.assertIn(token, paragraphs[0])
                for token in installer_tokens:
                    self.assertIn(token, paragraphs[1])

    def test_current_behavior_explains_architecture_request_and_release(self):
        text = self.read("HOW_IT_WORKS.md")
        self.assertGreaterEqual(text.count("```mermaid"), 2)
        self.assertLessEqual(text.count("```mermaid"), 4)
        self.assertIn("The skill is an editor's desk: it keeps the source facts but rearranges them so the intended reader can find and use them.", text)
        self.assertIn("最后更新时间：2026-10-16", text)

    def test_distribution_rows_use_only_defined_statuses(self):
        text = self.read("docs/distribution.md")
        rows = re.findall(r"^\| (GitHub repository|GitHub Release|skills\.sh|OpenAI directory|Anthropic directory) \| ([^|]+) \|", text, re.M)
        self.assertEqual(len(rows), 5)
        allowed = {"planned", "published", "listed", "submitted", "rejected", "not adopted"}
        for channel, status in rows:
            self.assertIn(status.strip(), allowed, channel)

    def test_contribution_and_security_routes_exist(self):
        for name in ("CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md",
                     ".github/ISSUE_TEMPLATE/bug.yml", ".github/ISSUE_TEMPLATE/compatibility.yml",
                     ".github/ISSUE_TEMPLATE/feature.yml", ".github/pull_request_template.md"):
            with self.subTest(name=name):
                self.assertTrue((ROOT / name).is_file(), name)
        self.assertIn("synthetic", self.read("CONTRIBUTING.md"))
        self.assertIn("python3 scripts/check_repo.py", self.read("CONTRIBUTING.md"))
        self.assertIn("/security/advisories/new", self.read("SECURITY.md"))
        self.assertIn("private documents", self.read("SECURITY.md"))


if __name__ == "__main__":
    unittest.main()
