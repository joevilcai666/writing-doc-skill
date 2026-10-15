from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not PNG")
    return struct.unpack(">II", data[16:24])


class SkillContractTests(unittest.TestCase):
    def test_skill_scope_and_review_boundary(self):
        text = (ROOT / "skills/writing-doc/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: writing-doc", text)
        self.assertIn("用户只要求审阅时", text)
        self.assertIn("不擅自改动文件", text)
        self.assertIn("不用于营销文案", text)
        self.assertIn("保持用户的语言", text)

    def test_x_images_are_exact_square_size(self):
        for name in (
            "x-problem-en.png", "x-solution-en.png",
            "x-problem-zh-CN.png", "x-solution-zh-CN.png",
        ):
            self.assertEqual(png_size(ROOT / "assets" / name), (1200, 1200))

    def test_social_preview_size(self):
        self.assertEqual(png_size(ROOT / "assets/social-preview.png"), (1280, 640))
