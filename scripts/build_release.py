"""Build a deterministic candidate ZIP from tracked current files.

This command does not authorize publication. Run check_repo.py --release on the
exact public candidate commit before publication. Checksum paths are relative to
the checksum file's directory: run the checksum command from that directory.
"""

import argparse
import hashlib
import io
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
import zipfile

if __package__:
    from .privacy_scan import _scan_data, scan_text
else:
    from privacy_scan import _scan_data, scan_text

EXCLUDED_PARTS = {".git", ".worktrees", ".superpowers", ".validators", ".venv",
                  "__pycache__", "dist", "node_modules", ".DS_Store"}
EXCLUDED_PREFIXES = (("docs", "superpowers"), ("evals", "runs"))


def _git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args],
                            capture_output=True, timeout=30)
    if result.returncode:
        raise ValueError("Git file inventory failed")
    return result.stdout


def _safe_name(name):
    parts = name.split("/")
    if (not name or any(part in ("", ".", "..") for part in parts)
            or "\\" in name or ":" in name
            or any(ord(char) < 32 or ord(char) == 127 for char in name)
            or any(part.endswith((".", " ")) for part in parts)
            or any(re.fullmatch(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part, re.I)
                   for part in parts)
            or scan_text(name, "[archive-path]")):
        raise ValueError("Unsafe archive path")
    return parts


def _read_file(root, name):
    parts = name.split("/")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory = os.open(root, flags)
    try:
        for part in parts[:-1]:
            child = os.open(part, flags, dir_fd=directory)
            os.close(directory)
            directory = child
        descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                             dir_fd=directory)
    finally:
        os.close(directory)
    with os.fdopen(descriptor, "rb") as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise ValueError("Archive source is not a regular file")
        data = source.read()
    if _scan_data(data, name):
        raise ValueError("Archive privacy check failed")
    return data


def _archive_bytes(root):
    if Path(_git(root, "rev-parse", "--show-toplevel").decode("utf-8").strip()).resolve() != root:
        raise ValueError("Use the repository root")
    names = _git(root, "ls-files", "-z").decode("utf-8").split("\0")
    if names[-1] != "" or len(set(names[:-1])) != len(names) - 1:
        raise ValueError("Invalid tracked file inventory")
    names = names[:-1]
    modes = {}
    for raw in _git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not raw:
            continue
        header, raw_name = raw.split(b"\t", 1)
        mode, oid, stage = header.split()
        name = raw_name.decode("utf-8")
        if (mode not in (b"100644", b"100755") or stage != b"0"
                or not re.fullmatch(rb"[0-9a-f]{40,64}", oid) or name in modes):
            raise ValueError("Unsupported tracked entry")
        modes[name] = 0o755 if mode == b"100755" else 0o644
    if set(names) != set(modes) or "VERSION" not in modes:
        raise ValueError("Incomplete tracked file inventory")
    payloads, folded = [], set()
    for name in sorted(names):
        parts = _safe_name(name)
        if EXCLUDED_PARTS.intersection(parts) or any(tuple(parts[:2]) == prefix for prefix in EXCLUDED_PREFIXES):
            continue
        if name.casefold() in folded:
            raise ValueError("Archive paths collide")
        folded.add(name.casefold())
        payloads.append((name, modes[name], _read_file(root, name)))
    version = next(data for name, _, data in payloads if name == "VERSION").decode("utf-8").strip()
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?", version):
        raise ValueError("Invalid package version")
    buffer = io.BytesIO()
    # ZIP_STORED avoids compression-library differences between build hosts.
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as bundle:
        for name, mode, data in payloads:
            entry = zipfile.ZipInfo("writing-doc-skill/" + name, (1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | mode) << 16
            bundle.writestr(entry, data)
    return version, buffer.getvalue()


def build_release(root: Path, output_dir: Path) -> tuple[Path, str]:
    """Return (archive path, SHA-256). Reject unsafe input before any output."""
    try:
        root = root.resolve(strict=True)
        version, data = _archive_bytes(root)
        digest = hashlib.sha256(data).hexdigest()
        archive = output_dir / ("writing-doc-skill-v" + version + ".zip")
        checksum = archive.with_suffix(".zip.sha256")
        output_dir.mkdir(parents=True, exist_ok=True)
        # Replace destination files without following destination symlinks.
        for destination, contents in ((archive, data), (checksum, (digest + "  " + archive.name + "\n").encode("ascii"))):
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=output_dir, delete=False) as handle:
                    temporary = Path(handle.name)
                    handle.write(contents)
                temporary.replace(destination)
            finally:
                if temporary is not None and temporary.exists():
                    temporary.unlink()
        return archive, digest
    except (OSError, ValueError, UnicodeError, subprocess.TimeoutExpired, StopIteration):
        # Do not expose paths, Git diagnostics, or content in errors.
        raise ValueError("Release build failed: unsafe, unreadable, or invalid input") from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("dist"))
    args = parser.parse_args()
    try:
        archive, digest = build_release(args.root, args.output)
    except ValueError as error:
        print(str(error))
        return 1
    print("Built " + archive.name)
    print("SHA-256 " + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
