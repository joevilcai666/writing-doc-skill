"""Sensitive samples exist only in temporary files and in memory."""

import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

from scripts.privacy_scan import _scan_data, scan_png, scan_repository, scan_text

ROOT = Path(__file__).resolve().parents[1]


def png_bytes(width=1, height=1, extra=()):
    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + b"".join(chunk(kind, value) for kind, value in extra)
            + chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00"))
            + chunk(b"IEND", b""))


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


class TextPrivacyTests(unittest.TestCase):
    def assert_redacted(self, value, rule, path="fixture.md"):
        findings = scan_text("public\n" + value, path)
        self.assertIn(rule, [item["rule"] for item in findings])
        self.assertNotIn(value, json.dumps(findings))
        for item in findings:
            self.assertEqual(item["match"], "[REDACTED]")
            self.assertEqual(item["line"], 2)
        return findings

    def test_detects_home_paths_without_committing_private_literals(self):
        for value in ("/" + "Users" + "/sample-person/private/file.md",
                      "/" + "home" + "/sample-person/file",
                      "C:" + "\\" + "Users" + "\\sample-person\\file"):
            with self.subTest(platform=value.split(":")[0][:2]):
                findings = self.assert_redacted(value, "home-path")
                self.assertNotIn("sample-person", str(findings))

    def test_detects_common_credentials(self):
        values = ("gh" + "p_" + "A" * 30, "github" + "_pat_" + "A" * 40,
                  "sk" + "-proj-" + "A" * 35, "AK" + "IA" + "A" * 16,
                  "xox" + "b-" + "1" * 12 + "-" + "A" * 24,
                  'api_key = "' + "A" * 24 + '"')
        for value in values:
            with self.subTest(prefix=value[:2]):
                self.assert_redacted(value, "credential")

    def test_detects_quoted_json_and_json_like_credential_fields(self):
        value = "A" * 24
        for key in ("api_key", "api-key", "password", "access_token", "auth_token", "client_secret"):
            for text in (json.dumps({key: value}), "{'" + key + "': '" + value + "'}"):
                with self.subTest(field=key):
                    findings = self.assert_redacted(text, "credential")
                    self.assertNotIn(value, str(findings))

    def test_detects_single_and_double_hyphen_cli_credentials(self):
        value = "A" * 24
        for prefix in ("-", "--"):
            for key in ("api-key", "api_key"):
                findings = self.assert_redacted(prefix + key + "=" + value, "credential")
                self.assertNotIn(value, str(findings))

    def test_short_public_values_and_unrelated_quoted_fields_pass(self):
        for text in (json.dumps({"api_key": "placeholder"}), json.dumps({"password": "short"}),
                     json.dumps({"unrelated_field": "A" * 24}), json.dumps({"not_api_key": "A" * 24}),
                     json.dumps({"not-api-key": "A" * 24}), "not-api-key=" + "A" * 24):
            self.assertEqual(scan_text(text, "public.json"), [])

    def test_detects_email_and_private_key_headers(self):
        self.assert_redacted("sample-person" + "@" + "example.invalid", "email")
        for kind in ("RSA ", "EC ", "OPENSSH ", "ENCRYPTED ", ""):
            self.assert_redacted("-----" + "BEGIN " + kind + "PRIVATE KEY-----", "private-key")

    def test_detects_signed_urls_case_insensitively_and_encoded_keys(self):
        for key in ("X-Amz-Signature", "X-Goog-Signature", "sig", "token", "%73ignature"):
            value = "https://example.invalid/object?" + key + "=" + "A" * 32
            self.assert_redacted(value, "signed-url")

    def test_redacts_sensitive_paths_and_untrusted_commit_identifiers(self):
        value = "sample-person" + "@" + "example.invalid"
        findings = scan_text(value, value + ".md", commit=value)
        self.assertNotIn(value, str(findings))
        self.assertEqual(findings[0]["path"], "[REDACTED]")
        self.assertEqual(findings[0]["commit"], "[REDACTED]")

    def test_reports_every_rule_with_deterministic_lines(self):
        value = "gh" + "p_" + "A" * 30
        findings = scan_text(value + "\n" + value, "example.md", "a" * 40)
        self.assertEqual([item["line"] for item in findings], [1, 2])
        self.assertEqual(findings[0]["commit"], "a" * 40)

    def test_accepts_public_commands_and_repository_urls(self):
        text = "https://github.com/example/skill\nTOKEN\nhttp://127.0.0.1:4310/health"
        self.assertEqual(scan_text(text, "public.md"), [])


class DataPrivacyTests(unittest.TestCase):
    def test_bomless_utf16_and_utf32_fail_with_only_fixed_redacted_details(self):
        value = "gh" + "p_" + "A" * 30
        name = "sample-person" + "@" + "example.invalid" + ".txt"
        for encoding in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
            with self.subTest(encoding=encoding):
                self.assertEqual(_scan_data(value.encode(encoding), name), [{
                    "rule": "text-invalid", "path": "[file-content]", "line": 1,
                    "match": "[REDACTED]",
                }])

    def test_invalid_utf8_and_truncated_bom_encodings_fail_closed(self):
        for data in (b"public\xff", b"\xff\xfeA", b"\xfe\xff\x00",
                     b"\xff\xfe\x00\x00A", b"\x00\x00\xfe\xff\x00"):
            with self.subTest(payload=data.hex()):
                self.assertEqual([item["rule"] for item in _scan_data(data, "sample.txt")],
                                 ["text-invalid"])

    def test_binary_controls_fail_even_with_valid_text_encoding(self):
        for control in ("\x00", "\x01", "\x1f", "\x7f", "\x85", "\x9f"):
            for encoding in ("utf-8", "utf-16", "utf-32"):
                with self.subTest(control=ord(control), encoding=encoding):
                    self.assertEqual([item["rule"] for item in _scan_data(
                        ("Public" + control + "text").encode(encoding), "sample.txt")],
                        ["text-invalid"])

    def test_public_ascii_utf8_and_whitespace_pass(self):
        for text in ("", "Public ASCII.\n\r\t", "公开说明。 Café\n"):
            self.assertEqual(_scan_data(text.encode("utf-8"), "sample.txt"), [])

    def test_public_bom_encodings_pass(self):
        for encoding, bom in (("utf-8", b"\xef\xbb\xbf"),
                              ("utf-16-le", b"\xff\xfe"), ("utf-16-be", b"\xfe\xff"),
                              ("utf-32-le", b"\xff\xfe\x00\x00"),
                              ("utf-32-be", b"\x00\x00\xfe\xff")):
            with self.subTest(encoding=encoding):
                self.assertEqual(_scan_data(bom + "公开说明。\n".encode(encoding), "sample.txt"), [])

    def test_bom_encodings_still_detect_private_content(self):
        value = "gh" + "p_" + "A" * 30
        for encoding, bom in (("utf-8", b"\xef\xbb\xbf"),
                              ("utf-16-le", b"\xff\xfe"), ("utf-16-be", b"\xfe\xff"),
                              ("utf-32-le", b"\xff\xfe\x00\x00"),
                              ("utf-32-be", b"\x00\x00\xfe\xff")):
            with self.subTest(encoding=encoding):
                findings = _scan_data(bom + value.encode(encoding), "sample.txt")
                self.assertIn("credential", [item["rule"] for item in findings])
                self.assertNotIn(value, str(findings))

    def test_png_signature_and_extension_keep_png_validation(self):
        self.assertEqual(_scan_data(png_bytes(), "image.bin"), [])
        self.assertEqual(_scan_data(png_bytes(), "image.png"), [])
        self.assertEqual([item["rule"] for item in _scan_data(b"Public text", "image.png")],
                         ["png-invalid"])


class PNGPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "fixture.png"

    def test_accepts_valid_png_without_private_metadata(self):
        self.path.write_bytes(png_bytes())
        self.assertEqual(scan_png(self.path), [])

    def test_rejects_all_private_metadata_chunks_without_echoing_values(self):
        value = ("sample-person" + "@" + "example.invalid").encode()
        for kind in (b"tEXt", b"zTXt", b"iTXt", b"eXIf"):
            self.path.write_bytes(png_bytes(extra=((kind, value),)))
            findings = scan_png(self.path)
            self.assertIn("png-metadata", [item["rule"] for item in findings])
            self.assertNotIn(value.decode(), str(findings))

    def test_rejects_truncated_corrupt_and_trailing_png_data(self):
        good = png_bytes()
        corrupt = bytearray(good)
        corrupt[29] ^= 1
        for data in (b"invalid", good[:-1], bytes(corrupt), good + b"private"):
            self.path.write_bytes(data)
            self.assertIn("png-invalid", [item["rule"] for item in scan_png(self.path)])

    def test_unreadable_png_fails_closed(self):
        self.assertEqual(scan_png(self.path)[0]["rule"], "scan-error")

    def test_png_entry_point_checks_signature_without_relying_on_extension(self):
        path = self.path.with_suffix(".bin")
        path.write_bytes(b"invalid")
        self.assertEqual(scan_png(path)[0]["rule"], "png-invalid")

    def test_current_public_images_have_no_private_metadata(self):
        for path in sorted((ROOT / "assets").glob("*.png")):
            with self.subTest(image=path.name):
                self.assertEqual(scan_png(path), [])


class RepositoryPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Synthetic Fixture")
        git(self.root, "config", "user.email", "fixture" + "@" + "example.invalid")
        (self.root / "safe.md").write_text("Public sample.\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "initial fixture")

    def raw_message_object(self, kind, message, extra_headers=b"", separator=b"\n"):
        identity = b"Synthetic Fixture <" + b"fixture" + b"@" + b"example.invalid> 1 +0000\n"
        head = git(self.root, "rev-parse", "HEAD").strip()
        if kind == "commit":
            tree = git(self.root, "rev-parse", "HEAD^{tree}").strip()
            headers = (b"tree " + tree + b"\nparent " + head + b"\nauthor " + identity
                       + b"committer " + identity)
            ref = "refs/heads/message-fixture"
        else:
            headers = b"object " + head + b"\ntype commit\ntag message-fixture\ntagger " + identity
            ref = "refs/tags/message-fixture"
        result = subprocess.run(["git", "-C", str(self.root), "hash-object", "--literally", "-t", kind, "-w", "--stdin"],
                                input=headers + extra_headers + separator + message, capture_output=True, check=True)
        oid = result.stdout.decode().strip()
        git(self.root, "update-ref", ref, oid)
        return oid

    def test_scans_current_untracked_and_hidden_files(self):
        value = "gh" + "p_" + "A" * 30
        (self.root / ".untracked").write_text(value)
        findings = scan_repository(self.root, history=False)
        self.assertIn("credential", [item["rule"] for item in findings])
        self.assertNotIn(value, str(findings))

    def test_quoted_json_credentials_enter_current_and_deleted_history_scans(self):
        value = "A" * 24
        for key in ("api_key", "password"):
            path = self.root / "quoted.json"
            path.write_text(json.dumps({key: value}))
            self.assertIn("credential", [item["rule"] for item in scan_repository(self.root, False)])
            git(self.root, "add", ".")
            git(self.root, "commit", "-qm", "temporary JSON fixture")
            git(self.root, "rm", "-q", "quoted.json")
            git(self.root, "commit", "-qm", "remove JSON fixture")
        self.assertEqual(scan_repository(self.root, False), [])
        findings = scan_repository(self.root, True)
        self.assertIn("credential", [item["rule"] for item in findings])
        self.assertNotIn(value, str(findings))

    def test_cli_credentials_enter_current_deleted_history_and_redacted_cli_output(self):
        value = "A" * 24
        command = [sys.executable, str(ROOT / "scripts/privacy_scan.py"), "--root", str(self.root)]
        for prefix in ("-", "--"):
            for key in ("api-key", "api_key"):
                path = self.root / "command.txt"
                path.write_text(prefix + key + "=" + value)
                findings = scan_repository(self.root, False)
                self.assertIn("credential", [item["rule"] for item in findings])
                current = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(current.returncode, 1)
                self.assertNotIn(value, str(findings) + current.stdout + current.stderr)
                git(self.root, "add", ".")
                git(self.root, "commit", "-qm", "temporary command fixture")
                git(self.root, "rm", "-q", "command.txt")
                git(self.root, "commit", "-qm", "remove command fixture")
        self.assertEqual(scan_repository(self.root, False), [])
        findings = scan_repository(self.root, True)
        self.assertIn("credential", [item["rule"] for item in findings])
        historical = subprocess.run(command + ["--history"], capture_output=True, text=True)
        self.assertEqual(historical.returncode, 1)
        self.assertIn("credential", historical.stdout)
        self.assertNotIn(value, str(findings) + historical.stdout + historical.stderr)

    def test_scans_staged_content_even_when_worktree_is_clean(self):
        (self.root / "safe.md").write_text("gh" + "p_" + "A" * 30)
        git(self.root, "add", "safe.md")
        (self.root / "safe.md").write_text("Public sample.\n")
        self.assertIn("credential", [item["rule"] for item in scan_repository(self.root, False)])

    def test_bomless_encoded_untracked_and_current_files_fail_closed(self):
        value = "gh" + "p_" + "A" * 30
        for encoding in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
            for name in ("untracked.txt", "safe.md"):
                with self.subTest(encoding=encoding, surface=name):
                    path = self.root / name
                    path.write_bytes(value.encode(encoding))
                    findings = scan_repository(self.root, False)
                    self.assertIn("text-invalid", [item["rule"] for item in findings])
                    self.assertNotIn(value, str(findings))
                    if name == "safe.md":
                        path.write_text("Public sample.\n")
                    else:
                        path.unlink()

    def test_bomless_encoded_index_fails_with_safe_current_content(self):
        value = "gh" + "p_" + "A" * 30
        path = self.root / "safe.md"
        for encoding in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
            with self.subTest(encoding=encoding):
                path.write_bytes(value.encode(encoding))
                git(self.root, "add", "safe.md")
                path.write_text("Public sample.\n")
                findings = scan_repository(self.root, False)
                self.assertIn("text-invalid", [item["rule"] for item in findings])
                self.assertNotIn(value, str(findings))

    def test_bomless_encoded_reachable_and_deleted_history_fail_closed(self):
        value = "gh" + "p_" + "A" * 30
        for encoding in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
            with self.subTest(encoding=encoding):
                path = self.root / "encoded.txt"
                path.write_bytes(value.encode(encoding))
                git(self.root, "add", "encoded.txt")
                git(self.root, "commit", "-qm", "temporary encoded fixture")
                commit = git(self.root, "rev-parse", "HEAD").decode().strip()
                for deleted in (False, True):
                    if deleted:
                        git(self.root, "rm", "-q", "encoded.txt")
                        git(self.root, "commit", "-qm", "remove encoded fixture")
                        self.assertEqual(scan_repository(self.root, False), [])
                    findings = scan_repository(self.root, True)
                    self.assertTrue(any(item["rule"] == "text-invalid"
                                        and item.get("commit") == commit for item in findings))
                    self.assertNotIn(value, str(findings))

    def test_bomless_encoded_cli_failure_does_not_echo_value_or_private_filename(self):
        value = "gh" + "p_" + "A" * 30
        name = "sample-person" + "@" + "example.invalid" + ".txt"
        command = [sys.executable, str(ROOT / "scripts/privacy_scan.py"), "--root", str(self.root)]
        for encoding in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
            with self.subTest(encoding=encoding):
                path = self.root / name
                path.write_bytes(value.encode(encoding))
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 1)
                self.assertIn("text-invalid", result.stdout)
                self.assertNotIn(value, result.stdout + result.stderr)
                self.assertNotIn(name, result.stdout + result.stderr)
                git(self.root, "add", "--", name)
                git(self.root, "commit", "-qm", "temporary encoded CLI fixture")
                git(self.root, "rm", "-q", "--", name)
                git(self.root, "commit", "-qm", "remove encoded CLI fixture")
                result = subprocess.run(command + ["--history"], capture_output=True, text=True)
                self.assertEqual(result.returncode, 1)
                self.assertIn("text-invalid", result.stdout)
                self.assertNotIn(value, result.stdout + result.stderr)
                self.assertNotIn(name, result.stdout + result.stderr)

    def test_bomless_encoded_messages_keep_fixed_invalid_message_findings(self):
        value = "gh" + "p_" + "A" * 30
        for kind in ("commit", "tag"):
            for encoding in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
                with self.subTest(kind=kind, encoding=encoding):
                    oid = self.raw_message_object(kind, value.encode(encoding))
                    findings = scan_repository(self.root, True)
                    self.assertTrue(any(item["rule"] == "history-message-invalid"
                                        and item.get("object") == oid for item in findings))
                    self.assertNotIn(value, str(findings))

    def test_finds_deleted_history_content_with_real_commit(self):
        value = "sample-person" + "@" + "example.invalid"
        (self.root / "deleted.md").write_text(value)
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "temporary fixture")
        commit = git(self.root, "rev-parse", "HEAD").decode().strip()
        git(self.root, "rm", "-q", "deleted.md")
        git(self.root, "commit", "-qm", "remove fixture")
        self.assertEqual(scan_repository(self.root, False), [])
        findings = scan_repository(self.root, True)
        self.assertTrue(any(item["rule"] == "email" and item.get("commit") == commit
                            for item in findings))
        self.assertNotIn(value, str(findings))

    def test_finds_metadata_in_deleted_history_png(self):
        (self.root / "deleted.png").write_bytes(png_bytes(extra=((b"iTXt", b"metadata"),)))
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "temporary image")
        git(self.root, "rm", "-q", "deleted.png")
        git(self.root, "commit", "-qm", "remove image")
        self.assertIn("png-metadata", [item["rule"] for item in scan_repository(self.root, True)])

    def test_redacts_private_filenames_and_handles_newlines(self):
        name = "sample-person" + "@" + "example.invalid" + "\nfile.md"
        (self.root / name).write_text("Public sample")
        findings = scan_repository(self.root, False)
        self.assertIn("email", [item["rule"] for item in findings])
        self.assertNotIn("sample-person", str(findings))

    def test_does_not_follow_symlinks(self):
        (self.root / "link.md").symlink_to(self.root / "safe.md")
        self.assertIn("unsafe-path", [item["rule"] for item in scan_repository(self.root, False)])

    def test_reports_invalid_git_repository_without_tool_output(self):
        with tempfile.TemporaryDirectory() as directory:
            findings = scan_repository(Path(directory), True)
        self.assertEqual(findings[0]["rule"], "scan-error")

    def test_cli_returns_one_and_only_redacted_output_for_findings(self):
        value = "gh" + "p_" + "A" * 30
        (self.root / "fixture.md").write_text(value)
        result = subprocess.run([sys.executable, str(ROOT / "scripts/privacy_scan.py"),
                                 "--root", str(self.root), "--history"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(value, result.stdout + result.stderr)
        self.assertIn("credential", result.stdout)

    def test_clean_repository_passes_with_history(self):
        self.assertEqual(scan_repository(self.root, True), [])

    def test_history_covers_other_branches(self):
        git(self.root, "checkout", "-qb", "fixture-branch")
        (self.root / "branch.md").write_text("gh" + "p_" + "A" * 30)
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "branch fixture")
        git(self.root, "checkout", "-q", "-")
        self.assertEqual(scan_repository(self.root, False), [])
        self.assertIn("credential", [item["rule"] for item in scan_repository(self.root, True)])

    def test_utf16_text_cannot_hide_private_values(self):
        value = "sample-person" + "@" + "example.invalid"
        (self.root / "encoded.txt").write_bytes(value.encode("utf-16"))
        self.assertIn("email", [item["rule"] for item in scan_repository(self.root, False)])

    def test_shallow_history_fails_closed(self):
        (self.root / "safe.md").write_text("Another public sample.\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "second fixture")
        with tempfile.TemporaryDirectory() as directory:
            clone = Path(directory) / "clone"
            git(self.root, "clone", "-q", "--depth", "1", self.root.as_uri(), str(clone))
            self.assertIn("incomplete-history", [item["rule"] for item in scan_repository(clone, True)])

    def test_replace_refs_cannot_hide_history(self):
        (self.root / "safe.md").write_text("Second public sample.\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "second fixture")
        git(self.root, "replace", "--graft", "HEAD")
        self.assertIn("incomplete-history", [item["rule"] for item in scan_repository(self.root, True)])

    def test_missing_index_object_fails_closed(self):
        oid = git(self.root, "rev-parse", "HEAD:safe.md").decode().strip()
        (self.root / ".git/objects" / oid[:2] / oid[2:]).unlink()
        self.assertEqual(scan_repository(self.root, True)[0]["rule"], "scan-error")

    def test_commit_message_credential_has_fixed_location_and_verified_object(self):
        value = "gh" + "p_" + "A" * 30
        git(self.root, "commit", "--allow-empty", "-qm", "Public subject\n\n" + value)
        oid = git(self.root, "rev-parse", "HEAD").decode().strip()
        self.assertEqual(scan_repository(self.root, False), [])
        findings = scan_repository(self.root, True)
        self.assertTrue(any(item["rule"] == "credential" and item["path"] == "[commit-message]"
                            and item.get("object") == oid and item.get("commit") == oid
                            and item["line"] == 3 for item in findings))
        self.assertNotIn(value, str(findings))

    def test_annotated_tag_message_is_scanned_without_echo_in_cli(self):
        value = "gh" + "p_" + "A" * 30
        git(self.root, "tag", "-a", "fixture-tag", "-m", value)
        oid = git(self.root, "rev-parse", "refs/tags/fixture-tag").decode().strip()
        findings = scan_repository(self.root, True)
        self.assertTrue(any(item["rule"] == "credential" and item["path"] == "[tag-message]"
                            and item.get("object") == oid for item in findings))
        result = subprocess.run([sys.executable, str(ROOT / "scripts/privacy_scan.py"),
                                 "--root", str(self.root), "--history"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(value, str(findings) + result.stdout + result.stderr)

    def test_public_messages_pass_and_author_tagger_identity_stays_excluded(self):
        value = "gh" + "p_" + "A" * 30
        git(self.root, "config", "user.name", value)
        git(self.root, "commit", "--allow-empty", "-qm", "Public release subject\n\nPublic body.")
        git(self.root, "tag", "-a", "fixture-tag", "-m", "Public release annotation.")
        self.assertEqual(scan_repository(self.root, True), [])

    def test_message_parser_handles_declared_latin1_and_utf16_encodings(self):
        value = "gh" + "p_" + "A" * 30
        for encoding, header in (("latin-1", b"ISO-8859-1"), ("utf-16", b"UTF-16")):
            with self.subTest(encoding=encoding):
                oid = self.raw_message_object("commit", ("Caf\u00e9\n" + value).encode(encoding),
                                              b"encoding " + header + b"\n")
                findings = scan_repository(self.root, True)
                self.assertTrue(any(item["rule"] == "credential" and item.get("object") == oid
                                    for item in findings))
                self.assertNotIn(value, str(findings))

    def test_public_declared_encoding_message_passes(self):
        self.raw_message_object("commit", "Caf\u00e9 public release.\n".encode("latin-1"),
                                b"encoding ISO-8859-1\n")
        self.assertEqual(scan_repository(self.root, True), [])

    def test_invalid_binary_messages_fail_closed_for_both_object_types(self):
        value = "gh" + "p_" + "A" * 30
        for kind in ("commit", "tag"):
            for payload in (b"\xff" + value.encode(), b"public\x00" + value.encode(),
                            png_bytes() + value.encode()):
                with self.subTest(kind=kind, prefix=payload[:1].hex()):
                    oid = self.raw_message_object(kind, payload)
                    findings = scan_repository(self.root, True)
                    self.assertTrue(any(item["rule"] == "history-message-invalid"
                                        and item.get("object") == oid for item in findings))
                    self.assertNotIn(value, str(findings))

    def test_unsupported_duplicate_and_invalid_encoding_headers_fail_closed(self):
        for header in (b"encoding unavailable-fixture-codec\n", b"encoding unicode_escape\n",
                       b"encoding UTF-8\nencoding ISO-8859-1\n", b"encoding \xff\n"):
            oid = self.raw_message_object("commit", b"Public message.\n", header)
            findings = scan_repository(self.root, True)
            self.assertTrue(any(item["rule"] == "history-message-invalid"
                                and item.get("object") == oid for item in findings))

    def test_tag_message_does_not_use_png_extension_or_signature_shortcuts(self):
        payload = b"\xff\xfe" + "Public text".encode("utf-16-le")
        oid = self.raw_message_object("tag", payload)
        findings = scan_repository(self.root, True)
        self.assertTrue(any(item["rule"] == "history-message-invalid" and item.get("object") == oid
                            for item in findings))

    def test_nested_annotated_tag_message_remains_reachable(self):
        value = "gh" + "p_" + "A" * 30
        git(self.root, "tag", "-a", "inner-fixture", "-m", value)
        oid = git(self.root, "rev-parse", "refs/tags/inner-fixture").decode().strip()
        git(self.root, "tag", "-a", "outer-fixture", "inner-fixture", "-m", "Public outer annotation.")
        git(self.root, "tag", "-d", "inner-fixture")
        findings = scan_repository(self.root, True)
        self.assertTrue(any(item["rule"] == "credential" and item.get("object") == oid for item in findings))
        self.assertNotIn(value, str(findings))

    def test_missing_message_boundary_and_truncated_encoding_fail_closed(self):
        for kind in ("commit", "tag"):
            oid = self.raw_message_object(kind, b"Public message.", separator=b"")
            findings = scan_repository(self.root, True)
            self.assertTrue(any(item["rule"] == "history-message-invalid" and item.get("object") == oid
                                for item in findings))
        oid = self.raw_message_object("commit", "Public message.".encode("utf-16")[:-1],
                                      b"encoding UTF-16\n")
        findings = scan_repository(self.root, True)
        self.assertTrue(any(item["rule"] == "history-message-invalid" and item.get("object") == oid
                            for item in findings))


if __name__ == "__main__":
    unittest.main()
