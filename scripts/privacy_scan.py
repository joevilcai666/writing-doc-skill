"""Fail-closed privacy checks for files, index blobs, and reachable Git messages.

Findings contain locations and rule names, never source excerpts or private values.
Ignored, untracked files are outside the publication surface. Tracked ignored files
remain in scope. Git identity headers and unreachable objects are outside this scan.
"""

import argparse
import codecs
import json
from pathlib import Path
import re
import stat
import struct
import subprocess
from typing import Optional
from urllib.parse import parse_qsl, unquote, urlsplit
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PRIVATE_CHUNKS = {b"tEXt", b"zTXt", b"iTXt", b"eXIf"}
RULES = (
    ("home-path", re.compile(r"(?:/(?:Users|home)/[^\s/\"'<>]+(?:/[^\s\"'<>]*)?"
                             r"|[A-Za-z]:[\\/]+Users[\\/]+[^\s\"'<>]+)", re.I)),
    ("credential", re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
        r"|sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}|(?:AKIA|ASIA)[A-Z0-9]{16}"
        r"|xox[baprs]-[A-Za-z0-9-]{20,}|AIza[A-Za-z0-9_-]{30,})\b"
        r"|(?<![\w-])(?:--?)?(?P<key_quote>[\"']?)"
        r"(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|client[_-]?secret)"
        r"(?P=key_quote)\s*[=:]\s*[\"']?[A-Za-z0-9_./+\-=]{16,}", re.I)),
    ("private-key", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----")),
    ("email", re.compile(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
                         r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?"
                         r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+")),
)
URL_PATTERN = re.compile(r"https?://[^\s<>\"'`]+", re.I)
SIGNED_KEYS = {"signature", "sig", "token", "access_token", "auth", "key",
               "x-amz-signature", "x-amz-credential", "awsaccesskeyid",
               "x-goog-signature", "x-goog-credential", "googleaccessid"}


def _matches(text):
    for rule, pattern in RULES:
        for match in pattern.finditer(text):
            yield rule, match.start()
    for match in URL_PATTERN.finditer(text):
        try:
            query = urlsplit(match.group()).query
            keys = {unquote(key).casefold() for key, _ in parse_qsl(query, keep_blank_values=True)}
            if keys & SIGNED_KEYS:
                yield "signed-url", match.start()
        except ValueError:
            # A URL with invalid authority syntax cannot bypass query checks.
            if any(key in match.group().casefold() for key in SIGNED_KEYS):
                yield "signed-url", match.start()


def safe_path(path):
    """Redact the whole location if any private value occurs in its name."""
    text = str(path)
    return "[REDACTED]" if next(_matches(text), None) is not None else text


def _finding(rule, path, line=1, commit=None):
    result = {"rule": rule, "path": safe_path(path), "line": line, "match": "[REDACTED]"}
    if commit is not None:
        result["commit"] = commit if re.fullmatch(r"[0-9a-f]{40,64}", commit) else "[REDACTED]"
    return result


def scan_text(text: str, path: str, commit: Optional[str] = None) -> list[dict]:
    """Return rule and line locations. Do not return the matched value."""
    locations = {(rule, text.count("\n", 0, offset) + 1) for rule, offset in _matches(text)}
    return [_finding(rule, path, line, commit) for rule, line in sorted(locations, key=lambda x: (x[1], x[0]))]


def inspect_png(data):
    """Return (dimensions, metadata_present, valid) after bounded chunk parsing."""
    if not data.startswith(PNG_SIGNATURE):
        return None, False, False
    offset, dimensions, metadata, image_seen = 8, None, False, False
    while offset < len(data):
        if len(data) - offset < 12:
            break
        length = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4:offset + 8]
        metadata = metadata or kind in PRIVATE_CHUNKS
        if length > len(data) - offset - 12 or not re.fullmatch(rb"[A-Za-z]{4}", kind):
            break
        payload = data[offset + 8:offset + 8 + length]
        checksum = struct.unpack_from(">I", data, offset + 8 + length)[0]
        if zlib.crc32(kind + payload) & 0xffffffff != checksum:
            break
        if dimensions is None:
            if kind != b"IHDR" or length != 13:
                break
            dimensions = struct.unpack_from(">II", payload)
            if not all(dimensions):
                break
        elif kind == b"IHDR":
            break
        if kind == b"IDAT":
            image_seen = True
        offset += length + 12
        if kind == b"IEND":
            return dimensions, metadata, length == 0 and image_seen and offset == len(data)
    return dimensions, metadata, False


def _scan_png_data(data, path, commit=None):
    _, metadata, valid = inspect_png(data)
    findings = []
    if metadata:
        findings.append(_finding("png-metadata", path, commit=commit))
    if not valid:
        findings.append(_finding("png-invalid", path, commit=commit))
    return findings


def _scan_data(data, path, commit=None):
    """Accept PNG or strict supported text. Reject ambiguous binary content."""
    if data.startswith(PNG_SIGNATURE) or str(path).lower().endswith(".png"):
        return _scan_png_data(data, path, commit)
    encoding = "utf-8-sig"
    if data.startswith((b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff")):
        encoding = "utf-32"
    elif data.startswith((b"\xff\xfe", b"\xfe\xff")):
        encoding = "utf-16"
    try:
        text = data.decode(encoding, errors="strict")
    except UnicodeError:
        return [_finding("text-invalid", "[file-content]", commit=commit)]
    if any((ord(char) < 32 and char not in "\n\r\t") or 127 <= ord(char) <= 159 for char in text):
        return [_finding("text-invalid", "[file-content]", commit=commit)]
    return scan_text(text, str(path), commit)


def scan_png(path: Path) -> list[dict]:
    """Reject private metadata, malformed PNG data, and read failures."""
    try:
        return _scan_png_data(path.read_bytes(), path)
    except OSError:
        return [_finding("scan-error", path)]


class ScanFailure(Exception):
    """Internal failures carry no tool output or private locations."""


def _git(root, *args, data=None):
    try:
        result = subprocess.run(["git", "-C", str(root), *args], input=data,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        raise ScanFailure() from None
    if result.returncode:
        raise ScanFailure()
    return result.stdout


def _object_contents(root, objects):
    """Read exact byte counts and expected types from cat-file's batch format."""
    if not objects:
        return {}
    output = _git(root, "cat-file", "--batch", data=("\n".join(sorted(objects)) + "\n").encode())
    position, contents = 0, {}
    for expected in sorted(objects):
        end = output.find(b"\n", position)
        if end < 0:
            raise ScanFailure()
        header = output[position:end].split()
        if (len(header) != 3 or header[0].decode("ascii", "replace") != expected
                or header[1].decode("ascii", "replace") != objects[expected]):
            raise ScanFailure()
        try:
            size = int(header[2])
        except ValueError:
            raise ScanFailure() from None
        start = end + 1
        if size < 0 or start + size >= len(output) or output[start + size:start + size + 1] != b"\n":
            raise ScanFailure()
        contents[expected] = output[start:start + size]
        position = start + size + 1
    if position != len(output):
        raise ScanFailure()
    return contents


def _blob_contents(root, objects):
    return _object_contents(root, {oid: "blob" for oid in objects})


def _message_text(data, kind):
    """Decode only the message body. Never pass identity headers to scan_text."""
    headers, separator, message = data.partition(b"\n\n")
    if not separator:
        raise ValueError("missing message boundary")
    encodings = []
    previous = None
    for line in headers.split(b"\n"):
        if line.startswith(b" "):
            if previous == b"encoding":
                raise ValueError("continued encoding header")
            continue
        key, separator, value = line.partition(b" ")
        if not separator or not re.fullmatch(rb"[a-z][a-z0-9-]*", key):
            raise ValueError("invalid message header")
        if key == b"encoding":
            encodings.append(value.decode("ascii").strip())
        previous = key
    if len(encodings) > 1 or (encodings and kind != "commit"):
        raise ValueError("invalid encoding headers")
    encoding = codecs.lookup(encodings[0] if encodings else "utf-8-sig").name
    if encoding not in {"utf-8", "utf-8-sig", "ascii", "iso8859-1", "cp1252",
                        "utf-16", "utf-16-le", "utf-16-be", "utf-32", "utf-32-le", "utf-32-be"}:
        raise ValueError("unsupported message encoding")
    text = message.decode(encoding, errors="strict")
    if any((ord(char) < 32 and char not in "\n\r\t") or 127 <= ord(char) <= 159 for char in text):
        raise ValueError("binary message content")
    return text


def _scan_message(data, kind, oid):
    path = "[commit-message]" if kind == "commit" else "[tag-message]"
    commit = oid if kind == "commit" else None
    try:
        findings = scan_text(_message_text(data, kind), path, commit)
    except (ValueError, UnicodeError, LookupError):
        findings = [_finding("history-message-invalid", path, commit=commit)]
    for item in findings:
        item["object"] = oid
    return findings


def _entries(raw, tree=False):
    for entry in raw.split(b"\0"):
        if entry:
            try:
                header, name = entry.split(b"\t", 1)
                mode, second, third = header.split()
                oid, stage = (third, second) if tree else (second, third)
                yield mode, oid.decode("ascii"), stage, name.decode("utf-8", "surrogateescape")
            except (ValueError, UnicodeError):
                raise ScanFailure() from None


def _current(root):
    findings, index = [], list(_entries(_git(root, "ls-files", "--stage", "-z")))
    names = set()
    for mode, oid, stage, name in index:
        names.add(name)
        if stage != b"0" or mode not in (b"100644", b"100755"):
            findings.append(_finding("unsafe-path", name))
    for raw in _git(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0"):
        if raw:
            names.add(raw.decode("utf-8", "surrogateescape"))
    for name in sorted(names):
        findings.extend(scan_text(name, name))
        path = root / name
        try:
            if path.is_symlink() or not path.resolve().is_relative_to(root):
                findings.append(_finding("unsafe-path", name))
                continue
            if not path.exists():
                # A local deletion has no current file. The index still enters the scan.
                continue
            if not stat.S_ISREG(path.stat().st_mode):
                findings.append(_finding("unsafe-path", name))
                continue
            findings.extend(_scan_data(path.read_bytes(), name))
        except (OSError, ValueError):
            findings.append(_finding("scan-error", name))
    blobs = _blob_contents(root, {oid for mode, oid, _, _ in index if mode != b"160000"})
    for mode, oid, _, name in index:
        if oid in blobs:
            findings.extend(_scan_data(blobs[oid], name))
    return findings


def _history(root):
    graft_name = _git(root, "rev-parse", "--git-path", "info/grafts").decode("utf-8", "surrogateescape").strip()
    if (_git(root, "rev-parse", "--is-shallow-repository").strip() != b"false"
            or _git(root, "for-each-ref", "--format=%(refname)", "refs/replace").strip()
            or (root / graft_name).exists()):
        return [_finding("incomplete-history", "[repository]")]
    object_ids = _git(root, "rev-list", "--objects", "--all", "--no-object-names").splitlines()
    if not object_ids:
        return []
    typed = _git(root, "cat-file", "--batch-check=%(objectname) %(objecttype)",
                 data=b"\n".join(object_ids) + b"\n")
    object_types = {}
    for line in typed.splitlines():
        fields = line.split()
        if (len(fields) != 2 or not re.fullmatch(rb"[0-9a-f]{40,64}", fields[0])
                or fields[1] not in (b"commit", b"tree", b"blob", b"tag")):
            raise ScanFailure()
        if fields[1] != b"tree":
            object_types[fields[0].decode("ascii")] = fields[1].decode("ascii")
    contents, locations, findings = _object_contents(root, object_types), {}, []
    for commit_raw in _git(root, "rev-list", "--all").splitlines():
        commit = commit_raw.decode("ascii")
        tree = _git(root, "ls-tree", "-r", "-z", "--full-tree", commit)
        for mode, oid, kind, name in _entries(tree, tree=True):
            findings.extend(scan_text(name, name, commit))
            if mode not in (b"100644", b"100755"):
                findings.append(_finding("unsafe-path", name, commit=commit))
            if kind == b"blob":
                # Scan each blob once, even when many commits retain it.
                locations.setdefault(oid, (name, commit))
    for oid, data in contents.items():
        if object_types[oid] == "blob":
            name, commit = locations.get(oid, ("[history-blob]", None))
            findings.extend(_scan_data(data, name, commit))
        else:
            findings.extend(_scan_message(data, object_types[oid], oid))
    return findings


def scan_repository(root: Path, history: bool) -> list[dict]:
    """Scan files and index blobs, plus reachable blobs and messages on request."""
    try:
        root = root.resolve()
        findings = _current(root)
        if history:
            findings.extend(_history(root))
    except (ScanFailure, OSError, UnicodeError, ValueError):
        return [_finding("scan-error", "[repository]")]
    unique = {json.dumps(item, sort_keys=True): item for item in findings}
    return [unique[key] for key in sorted(unique)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--history", action="store_true")
    args = parser.parse_args()
    findings = scan_repository(args.root, args.history)
    for item in findings:
        print(json.dumps(item, sort_keys=True, ensure_ascii=True))
    print("FAIL privacy" if findings else "PASS privacy")
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
