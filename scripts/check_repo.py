"""Run local package checks. Use --release to require the full public package.

External validator overrides are JSON argument arrays in WRITING_DOC_*_VALIDATOR.
Use {root} and {skill} placeholders for paths. No command runs through a shell.
Tool output stays private. This command reports only check names and return codes.
"""

import argparse
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit

if __package__:
    from .privacy_scan import inspect_png, safe_path, scan_repository
else:
    from privacy_scan import inspect_png, safe_path, scan_repository

CORE_FILES = (
    "VERSION", "LICENSE", "HOW_IT_WORKS.md", "plugin.json", ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
    "skills/writing-doc/SKILL.md", "skills/writing-doc/agents/openai.yaml",
    "demo/README.md", "demo/source/AI_SETUP_GUIDE.md", "demo/expected/SETUP_GUIDE.md",
    "evals/cases.json", "evals/README.md", "evals/run_rubric.py",
    "scripts/check_repo.py", "scripts/privacy_scan.py", "tests/__init__.py",
    "tests/test_privacy_scan.py", "tests/test_check_repo.py",
)
RELEASE_FILES = (
    "README.md", "README.zh-CN.md", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md",
    "docs/distribution.md", ".github/ISSUE_TEMPLATE/bug.yml",
    ".github/ISSUE_TEMPLATE/compatibility.yml", ".github/ISSUE_TEMPLATE/feature.yml",
    ".github/pull_request_template.md", "tests/test_public_docs.py",
    "scripts/build_release.py", "tests/test_build_release.py",
)
IMAGE_SIZES = {
    "assets/x-problem-en.png": (1200, 1200),
    "assets/x-solution-en.png": (1200, 1200),
    "assets/x-problem-zh-CN.png": (1200, 1200),
    "assets/x-solution-zh-CN.png": (1200, 1200),
    "assets/social-preview.png": (1280, 640),
}
EXCLUDED_DIRS = {".git", ".worktrees", ".superpowers", ".validators", ".venv",
                 "__pycache__", "dist", "node_modules"}


def _files(root):
    """Use Git's publication surface, with a filesystem fallback for unit fixtures."""
    try:
        result = subprocess.run(["git", "-C", str(root), "ls-files", "--cached", "--others",
                                 "--exclude-standard", "-z"], capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        result = None
    if result is not None and result.returncode == 0:
        return sorted({root / name.decode("utf-8", "surrogateescape")
                       for name in result.stdout.split(b"\0") if name})
    return sorted(path for path in root.rglob("*") if path.is_file()
                  and not EXCLUDED_DIRS.intersection(path.relative_to(root).parts))


def _json_pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate key")
        value[key] = item
    return value


def _load_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_json_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid constant")))


def _frontmatter(text):
    """Validate the package's flat scalar YAML subset without a YAML dependency.

    Complex YAML fails closed. The required external skill validator supplies the
    full Agent Skills validation in release mode.
    """
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    if not match:
        return False
    values = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        field = re.fullmatch(r"([a-z-]+):[ \t]+(.+)", line)
        if not field or field[1] in values:
            return False
        key, raw = field.groups()
        try:
            if raw.startswith('"'):
                value = json.loads(raw)
            elif raw.startswith("'"):
                if not re.fullmatch(r"'(?:[^']|'')*'", raw):
                    return False
                value = raw[1:-1].replace("''", "'")
            else:
                if re.search(r"[:\[\]{}#]|^[>|&*!]", raw) or raw in {"true", "false", "null", "~"}:
                    return False
                value = raw.strip()
        except (ValueError, TypeError):
            return False
        if not isinstance(value, str) or not value.strip():
            return False
        values[key] = value
    return (values.get("name") == "writing-doc" and bool(values.get("description"))
            and len(values["description"]) <= 1024
            and not re.search(r"[<>]", values["description"])
            and set(values) <= {"name", "description", "license", "allowed-tools", "compatibility"})


def _missing(root, names):
    return ["missing-file: " + name for name in names if not (root / name).is_file()]


def check_structure(root: Path) -> list[str]:
    """Validate files that exist at this implementation stage, including READMEs."""
    root = root.resolve()
    failures = _missing(root, CORE_FILES)
    try:
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
        if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version):
            failures.append("invalid-version: VERSION")
    except (OSError, UnicodeError):
        version = None
        failures.append("unreadable-version: VERSION")
    documents = {}
    for path in _files(root):
        name = path.relative_to(root).as_posix()
        if path.suffix.lower() == ".json":
            try:
                documents[name] = _load_json(path)
            except (OSError, UnicodeError, ValueError, RecursionError):
                failures.append("invalid-json: " + safe_path(name))
    for name in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
        manifest = documents.get(name)
        if not isinstance(manifest, dict) or manifest.get("name") != "writing-doc":
            failures.append("invalid-manifest: " + name)
        if not isinstance(manifest, dict) or manifest.get("version") != version:
            failures.append("version-mismatch: " + name)
    market = documents.get(".claude-plugin/marketplace.json")
    entries = market.get("plugins") if isinstance(market, dict) else None
    if (not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict)
            or entries[0].get("name") != "writing-doc"):
        failures.append("invalid-marketplace: .claude-plugin/marketplace.json")
    elif entries[0].get("version") != version:
        failures.append("version-mismatch: .claude-plugin/marketplace.json")
    try:
        if not _frontmatter((root / "skills/writing-doc/SKILL.md").read_text(encoding="utf-8")):
            failures.append("invalid-frontmatter: skills/writing-doc/SKILL.md")
    except (OSError, UnicodeError):
        failures.append("unreadable-skill: skills/writing-doc/SKILL.md")
    for name, expected in IMAGE_SIZES.items():
        try:
            dimensions, _, valid = inspect_png((root / name).read_bytes())
            if not valid:
                failures.append("invalid-png: " + name)
            if dimensions != expected:
                failures.append("png-dimensions: " + name)
        except OSError:
            failures.append("missing-image: " + name)
    for name, language in (("README.md", "en"), ("README.zh-CN.md", "zh-CN")):
        path = root / name
        if path.exists():
            try:
                destinations = {target for target, image in _markdown_targets(path.read_text(encoding="utf-8")) if image}
                for kind in ("problem", "solution"):
                    required = "assets/x-" + kind + "-" + language + ".png"
                    if required not in {unquote(urlsplit(item).path).removeprefix("./") for item in destinations}:
                        failures.append("readme-image: " + name + ": " + kind)
            except (OSError, UnicodeError, ValueError):
                failures.append("unreadable-readme: " + name)
    return failures


def _without_code(text):
    lines, fence, length = [], None, 0
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if marker:
            if fence is None:
                fence, length = marker[1][0], len(marker[1])
            elif marker[1][0] == fence and len(marker[1]) >= length and not marker[2].strip():
                fence = None
            lines.append("")
        else:
            lines.append("" if fence else line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines))


def _destination(text, offset):
    while offset < len(text) and text[offset].isspace():
        offset += 1
    if offset < len(text) and text[offset] == "<":
        end = text.find(">", offset + 1)
        return text[offset + 1:end] if end >= 0 else ""
    start, depth = offset, 0
    while offset < len(text):
        char = text[offset]
        if char == "\\" and offset + 1 < len(text):
            offset += 2
            continue
        if char == "(":
            depth += 1
        elif char == ")":
            if depth == 0:
                break
            depth -= 1
        elif char.isspace() and depth == 0:
            break
        offset += 1
    return re.sub(r"\\([() ])", r"\1", text[start:offset])


class _HTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if value is not None and key in ("href", "src"):
                self.targets.append((value, tag == "img" and key == "src"))


def _markdown_targets(text):
    text = _without_code(text)
    definitions = {}
    for match in re.finditer(r"^[ ]{0,3}\[([^]\n]+)\]:[ \t]*(.*)$", text, re.M):
        definitions[" ".join(match[1].split()).casefold()] = _destination(match[2], 0)
    for match in re.finditer(r"(!?)\[[^]\n]*\]\(", text):
        yield _destination(text, match.end()), bool(match[1])
    for match in re.finditer(r"(!?)\[([^]\n]+)\]\[([^]\n]*)\]", text):
        key = " ".join((match[3] or match[2]).split()).casefold()
        yield definitions.get(key, "[undefined-reference]"), bool(match[1])
    for match in re.finditer(r"(!?)\[([^]\n]+)\](?![(:\[])", text):
        key = " ".join(match[2].split()).casefold()
        if key in definitions:
            yield definitions[key], bool(match[1])
    html = _HTMLLinks()
    html.feed(text)
    yield from html.targets


def check_markdown_links(root: Path) -> list[str]:
    """Check local destinations without network requests or private excerpts."""
    root, failures = root.resolve(), []
    for path in _files(root):
        if path.suffix.lower() != ".md":
            continue
        name = safe_path(path.relative_to(root).as_posix())
        try:
            if not path.resolve().is_relative_to(root) or path.is_symlink():
                failures.append("unsafe-markdown: " + name)
                continue
            for target, _ in _markdown_targets(path.read_text(encoding="utf-8")):
                parsed = urlsplit(target)
                if parsed.scheme in ("http", "https", "mailto", "tel", "data") or target.startswith("#"):
                    continue
                if parsed.scheme or parsed.netloc or target.startswith("/"):
                    failures.append("unsafe-local-link: " + name)
                    continue
                destination = (path.parent / unquote(parsed.path)).resolve()
                if (not parsed.path or not destination.is_relative_to(root) or not destination.exists()):
                    failures.append("missing-local-link: " + name)
        except (OSError, UnicodeError, ValueError):
            failures.append("unreadable-markdown: " + name)
    return sorted(set(failures))


def _run(root, command, require_tests=False):
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return 1
    if require_tests and not re.search(rb"\bRan [1-9][0-9]* tests?\b", result.stdout + result.stderr):
        return 1
    return result.returncode


def _validator_command(root, kind):
    override = os.environ.get("WRITING_DOC_" + kind.upper() + "_VALIDATOR")
    if override is not None:
        try:
            command = json.loads(override)
            if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
                return None, "invalid-config"
            return [part.replace("{root}", str(root)).replace("{skill}", str(root / "skills/writing-doc"))
                    for part in command], None
        except ValueError:
            return None, "invalid-config"
    if kind == "skill":
        base = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
        script = base / "skills/.system/skill-creator/scripts/quick_validate.py"
        if script.is_file():
            return [sys.executable, str(script), str(root / "skills/writing-doc")], None
    else:
        executable = shutil.which(kind)
        if executable:
            try:
                help_result = subprocess.run([executable, "plugin", "--help"], capture_output=True, timeout=15)
                if help_result.returncode == 0 and re.search(rb"\bvalidate\b", help_result.stdout):
                    strict = ["--strict"] if kind == "claude" else []
                    return [executable, "plugin", "validate", *strict, str(root)], None
            except (OSError, subprocess.TimeoutExpired):
                pass
    return None, "unavailable"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root, failed = args.root.resolve(), False

    def report(name, failures):
        nonlocal failed
        print(("FAIL " if failures else "PASS ") + name)
        for failure in failures:
            print("  " + failure)
        failed = failed or bool(failures)

    report("structure", check_structure(root))
    if args.release:
        missing = _missing(root, RELEASE_FILES)
        try:
            version = (root / "VERSION").read_text(encoding="utf-8").strip()
            if re.fullmatch(r"\d+\.\d+\.\d+", version):
                missing.extend(_missing(root, ("docs/releases/v" + version + ".md",
                                               "docs/verification/v" + version + ".md")))
        except (OSError, UnicodeError):
            missing.append("unreadable-version")
        report("release-files", missing)
    report("markdown-links", check_markdown_links(root))
    report("rubric", [] if _run(root, [sys.executable, "evals/run_rubric.py", "--case", "lantern-setup",
                                       "demo/expected/SETUP_GUIDE.md"]) == 0 else ["rubric-command-failed"])
    report("unit-tests", [] if _run(root, [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], require_tests=True) == 0
           else ["unit-tests-failed"])
    findings = scan_repository(root, history=args.release)
    privacy_label = "privacy-current-index-history" if args.release else "privacy-current-index"
    report(privacy_label, [json.dumps(item, sort_keys=True, ensure_ascii=True) for item in findings])
    for label, command in (("git-diff", ["git", "diff", "--check"]),
                           ("git-index-diff", ["git", "diff", "--cached", "--check"])):
        report(label, [] if _run(root, command) == 0 else ["diff-check-failed"])
    for kind in ("skill", "codex", "claude"):
        command, reason = _validator_command(root, kind)
        name = kind + "-validator"
        if command is None:
            print("SKIP " + name + ": " + reason)
            if args.release or reason == "invalid-config":
                report(name, ["required-validator-" + reason])
        else:
            report(name, [] if _run(root, command) == 0 else ["validator-command-failed"])
    print("FAIL repository" if failed else "PASS repository")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
