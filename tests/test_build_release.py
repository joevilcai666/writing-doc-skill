"""Exercise archive bytes, package boundaries, and failure behavior."""

import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts.build_release import build_release
from tests.test_privacy_scan import png_bytes

ROOT = Path(__file__).resolve().parents[1]


class ReleaseBuildTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "repo"
        self.root.mkdir()
        self.output = Path(self.directory.name) / "output"
        self.git("init", "-q")
        self.write("VERSION", b"0.1.0\n")
        self.write("plugin.json", b'{"name":"writing-doc"}\n')
        self.write("skills/writing-doc/SKILL.md", "Public skill.\n".encode())
        self.git("add", ".")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True,
                              capture_output=True).stdout

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def assert_rejected(self):
        with self.assertRaises(ValueError):
            build_release(self.root, self.output)
        self.assertFalse(self.output.exists(), "Failure must precede output creation")

    def test_two_builds_have_identical_bytes_despite_local_file_metadata(self):
        executable = self.write("scripts/tool", b"Public executable.\n")
        self.git("add", ".")
        self.git("update-index", "--chmod=+x", "scripts/tool")
        first, digest_a = build_release(self.root, self.output)
        first_bytes = first.read_bytes()
        os.chmod(executable, 0o600)
        os.utime(executable, (1700000000, 1700000000))
        second, digest_b = build_release(self.root, self.output.parent / "second")
        self.assertEqual(first_bytes, second.read_bytes())
        self.assertEqual(digest_a, digest_b)
        self.assertEqual(digest_a, hashlib.sha256(first_bytes).hexdigest())
        with zipfile.ZipFile(first) as bundle:
            self.assertEqual(bundle.namelist(), sorted(bundle.namelist()))
            for entry in bundle.infolist():
                self.assertEqual(entry.date_time, (1980, 1, 1, 0, 0, 0))
                mode = stat.S_IMODE(entry.external_attr >> 16)
                self.assertEqual(mode, 0o755 if entry.filename.endswith("scripts/tool") else 0o644)

    def test_exact_tracked_file_set_excludes_process_and_local_state(self):
        for name in ("docs/superpowers/design.md", ".superpowers/sdd/report.md",
                     ".validators/check.txt", ".worktrees/other/file", "dist/old.zip",
                     "evals/runs/private.md", "__pycache__/cached.pyc"):
            self.write(name, b"Local state.\n")
        self.write("docs/指南.md", "公开说明。\n".encode())
        self.git("add", "-f", ".")
        self.write("untracked.txt", b"Do not ship.\n")
        archive, _ = build_release(self.root, self.output)
        with zipfile.ZipFile(archive) as bundle:
            self.assertEqual(set(bundle.namelist()), {
                "writing-doc-skill/VERSION", "writing-doc-skill/plugin.json",
                "writing-doc-skill/skills/writing-doc/SKILL.md",
                "writing-doc-skill/docs/指南.md",
            })
            self.assertEqual(bundle.read("writing-doc-skill/docs/指南.md").decode(), "公开说明。\n")
            self.assertTrue(bundle.getinfo("writing-doc-skill/docs/指南.md").flag_bits & 0x800)

    def test_checksum_names_archive_and_cli_output_is_relocatable(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/build_release.py"),
                                 "--root", str(self.root), "--output", str(self.output)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        archive = self.output / "writing-doc-skill-v0.1.0.zip"
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        self.assertEqual(archive.with_suffix(".zip.sha256").read_text(),
                         digest + "  writing-doc-skill-v0.1.0.zip\n")
        self.assertIn(digest, result.stdout)

    def test_current_tracked_content_enters_archive(self):
        self.write("plugin.json", b'{"name":"current-content"}\n')
        archive, _ = build_release(self.root, self.output)
        with zipfile.ZipFile(archive) as bundle:
            self.assertEqual(bundle.read("writing-doc-skill/plugin.json"), b'{"name":"current-content"}\n')

    def test_private_content_and_png_metadata_fail_before_output(self):
        for name, data in (("secret.txt", ("gh" + "p_" + "A" * 30).encode()),
                           ("image.png", png_bytes(extra=((b"eXIf", b"metadata"),)))):
            with self.subTest(name=name):
                path = self.write(name, data)
                self.git("add", name)
                self.assert_rejected()
                self.git("rm", "--cached", name)
                path.unlink()

    def test_safe_png_is_preserved_exactly(self):
        data = png_bytes()
        self.write("image.png", data)
        self.git("add", ".")
        archive, _ = build_release(self.root, self.output)
        with zipfile.ZipFile(archive) as bundle:
            self.assertEqual(bundle.read("writing-doc-skill/image.png"), data)

    def test_bomless_encoded_content_fails_before_output_and_errors_stay_redacted(self):
        value = "gh" + "p_" + "A" * 30
        self.write("encoded.txt", b"Public text.\n")
        self.git("add", "encoded.txt")
        for encoding in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
            with self.subTest(encoding=encoding):
                self.write("encoded.txt", value.encode(encoding))
                self.assert_rejected()
                result = subprocess.run([sys.executable, str(ROOT / "scripts/build_release.py"),
                                         "--root", str(self.root), "--output", str(self.output)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 1)
                self.assertNotIn(value, result.stdout + result.stderr)
                self.assertNotIn("encoded.txt", result.stdout + result.stderr)
                self.assertFalse(self.output.exists())

    def test_safe_utf8_and_bom_text_bytes_are_preserved(self):
        payloads = {"ascii.txt": b"Public text.\n", "utf8.txt": "公开说明。\n".encode("utf-8")}
        for index, (encoding, bom) in enumerate((("utf-8", b"\xef\xbb\xbf"),
                                               ("utf-16-le", b"\xff\xfe"),
                                               ("utf-16-be", b"\xfe\xff"),
                                               ("utf-32-le", b"\xff\xfe\x00\x00"),
                                               ("utf-32-be", b"\x00\x00\xfe\xff"))):
            payloads["bom-" + str(index) + ".txt"] = bom + "公开说明。\n".encode(encoding)
        for name, data in payloads.items():
            self.write(name, data)
        self.git("add", ".")
        archive, _ = build_release(self.root, self.output)
        with zipfile.ZipFile(archive) as bundle:
            for name, data in payloads.items():
                self.assertEqual(bundle.read("writing-doc-skill/" + name), data)

    def test_unsafe_names_fail_without_echoing_private_values(self):
        for name in ("bad\\name.txt", "bad\nname.txt", "C:drive.txt", "CON.txt",
                     "trailing. ", "person" + "@" + "example.invalid"):
            with self.subTest(name=repr(name)):
                path = self.write(name, b"Public text.\n")
                self.git("add", "--", name)
                self.assert_rejected()
                result = subprocess.run([sys.executable, str(ROOT / "scripts/build_release.py"),
                                         "--root", str(self.root), "--output", str(self.output)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 1)
                self.assertNotIn(name, result.stdout + result.stderr)
                self.git("rm", "--cached", "--", name)
                path.unlink()

    def test_index_symlink_and_submodule_fail_closed(self):
        (self.root / "link").symlink_to("VERSION")
        self.git("add", "link")
        self.assert_rejected()
        self.git("rm", "--cached", "link")
        (self.root / "link").unlink()
        self.git("update-index", "--add", "--cacheinfo", "160000", "a" * 40, "module")
        self.assert_rejected()

    def test_worktree_symlink_and_parent_symlink_fail_closed(self):
        target = self.root / "plugin.json"
        target.unlink()
        target.symlink_to("VERSION")
        self.assert_rejected()
        target.unlink()
        target.write_bytes(b"Public text.\n")
        skill = self.root / "skills/writing-doc/SKILL.md"
        skill.unlink()
        skill.parent.rmdir()
        (self.root / "skills").rmdir()
        (self.root / "skills").symlink_to(self.output.parent)
        self.assert_rejected()

    def test_missing_file_nonregular_file_and_invalid_version_fail_closed(self):
        path = self.root / "plugin.json"
        path.unlink()
        self.assert_rejected()
        os.mkfifo(path)
        self.assert_rejected()
        path.unlink()
        path.write_bytes(b"Public text.\n")
        self.write("VERSION", b"../bad\n")
        self.assert_rejected()

    def test_no_git_and_git_failure_do_not_create_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                build_release(Path(directory), self.output)
        with patch("scripts.build_release.subprocess.run", side_effect=OSError("private detail")):
            self.assert_rejected()

    def test_unmerged_index_fails_closed(self):
        oid = self.git("rev-parse", ":plugin.json").strip()
        self.git("update-index", "--force-remove", "plugin.json")
        subprocess.run(["git", "-C", str(self.root), "update-index", "--index-info"],
                       input=b"100644 " + oid + b" 1\tplugin.json\n", check=True, capture_output=True)
        self.assert_rejected()

    def test_malformed_git_inventory_fails_closed(self):
        from scripts.build_release import _git

        for payload in (b"../outside\0", b"/absolute\0", b"VERSION\0VERSION\0",
                        b"VERSION", b"\xff\0"):
            def broken_inventory(root, *args):
                if args == ("ls-files", "-z"):
                    return payload
                return _git(root, *args)

            with self.subTest(payload=repr(payload)):
                with patch("scripts.build_release._git", side_effect=broken_inventory):
                    self.assert_rejected()

    def test_git_timeout_and_source_read_error_fail_closed(self):
        with patch("scripts.build_release.subprocess.run",
                   side_effect=subprocess.TimeoutExpired("git", 30)):
            self.assert_rejected()
        with patch("scripts.build_release.os.open", side_effect=OSError("private source detail")):
            self.assert_rejected()

    def test_untracked_version_and_nonroot_directory_fail_closed(self):
        self.git("rm", "--cached", "VERSION")
        self.assert_rejected()
        self.git("add", "VERSION")
        with self.assertRaises(ValueError):
            build_release(self.root / "skills", self.output)
        self.assertFalse(self.output.exists())

    def test_existing_destination_symlinks_do_not_overwrite_their_targets(self):
        self.output.mkdir()
        target = self.write("outside.txt", b"Preserve this file.\n")
        archive = self.output / "writing-doc-skill-v0.1.0.zip"
        archive.symlink_to(target)
        archive.with_suffix(".zip.sha256").symlink_to(target)
        actual, _ = build_release(self.root, self.output)
        self.assertEqual(target.read_bytes(), b"Preserve this file.\n")
        self.assertFalse(actual.is_symlink())
        self.assertFalse(actual.with_suffix(".zip.sha256").is_symlink())

    def test_parent_symlink_swap_during_read_fails_closed(self):
        self.write("nested/sample.txt", b"Tracked text.\n")
        self.git("add", ".")
        outside = self.output.parent / "outside"
        outside.mkdir()
        (outside / "sample.txt").write_bytes(b"Outside text.\n")
        original_open = os.open
        swapped = False

        def swap_then_open(path, flags, *args, **kwargs):
            nonlocal swapped
            if not swapped and (str(path).endswith("nested/sample.txt") or str(path) == "nested"):
                (self.root / "nested").rename(self.root / "moved")
                (self.root / "nested").symlink_to(outside)
                swapped = True
            return original_open(path, flags, *args, **kwargs)

        with patch("scripts.build_release.os.open", side_effect=swap_then_open):
            self.assert_rejected()


if __name__ == "__main__":
    unittest.main()
