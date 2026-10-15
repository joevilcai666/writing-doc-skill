# Writing Doc Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a privacy-safe, bilingual, cross-client `writing-doc` skill that turns verbose AI output into technical documentation a target audience can understand and act on.

**Architecture:** One authoritative `skills/writing-doc/SKILL.md` supplies the writing workflow to every client. Thin portable, Codex, and Claude manifests point to that same skill. Standard-library Python scripts validate the package, scan privacy risks, evaluate a synthetic before-and-after example, and build a deterministic release archive.

**Tech Stack:** Agent Skills Markdown, portable Agent Plugin JSON, Claude plugin JSON, Python 3.9+ standard library, `unittest`, Mermaid, Git, GitHub CLI, PNG assets.

**Spec:** `docs/superpowers/specs/2026-10-15-writing-doc-skill-design.md`

## Global Constraints

- Keep `skills/writing-doc/SKILL.md` as the only authoritative writing workflow.
- Preserve the supplied `writing-doc` scope: technical documentation only, not marketing copy, literary writing, or format-only conversion.
- Preserve the user's language and technical facts, commands, parameters, links, units, and necessary conditions.
- Review-only requests must not modify files.
- Support Codex, Claude Code, and clients that implement the Agent Skills specification.
- Provide English and Simplified Chinese public documentation.
- Use the approved product message and the four approved 1200 × 1200 PNG assets.
- Do not modify a user's `AGENTS.md`, `CLAUDE.md`, or global configuration.
- Do not add analytics or telemetry.
- Use only synthetic source material, examples, screenshots, and evaluation records.
- Use MIT licensing and semantic version `0.1.0` for the first public release.
- Publish repository `joevilcai666/writing-doc-skill` with default branch `main` and annotated tag `v0.1.0`.
- Publish a deterministic release ZIP and its SHA-256 checksum.
- Do not use GitHub Actions as the release gate. Run release checks locally on the exact release commit.
- Keep `HOW_IT_WORKS.md` synchronized with current behavior and observed evidence.

## File Map

| Path | Responsibility |
|---|---|
| `plugin.json` | Canonical portable plugin identity and OpenAI presentation metadata. |
| `.codex-plugin/plugin.json` | Codex compatibility manifest that points to `skills/`. |
| `.claude-plugin/plugin.json` | Claude Code plugin metadata. |
| `.claude-plugin/marketplace.json` | Self-hosted Claude marketplace entry. |
| `skills/writing-doc/SKILL.md` | Authoritative technical-document writing, rewriting, and review workflow. |
| `skills/writing-doc/agents/openai.yaml` | Skill-list presentation metadata and default prompt. |
| `assets/x-problem-en.png` | Approved English problem image, 1200 × 1200. |
| `assets/x-solution-en.png` | Approved English solution image, 1200 × 1200. |
| `assets/x-problem-zh-CN.png` | Approved Chinese problem image, 1200 × 1200. |
| `assets/x-solution-zh-CN.png` | Approved Chinese solution image, 1200 × 1200. |
| `assets/social-preview.png` | GitHub social preview, 1280 × 640. |
| `demo/source/AI_SETUP_GUIDE.md` | Synthetic verbose input document. |
| `demo/expected/SETUP_GUIDE.md` | Synthetic audience-focused expected result. |
| `evals/cases.json` | Behavioral cases and observable scoring rules. |
| `evals/run_rubric.py` | Deterministic evaluator for generated or expected documents. |
| `scripts/privacy_scan.py` | Current-tree, Git-history, and PNG-metadata privacy checks. |
| `scripts/check_repo.py` | One local entry point for deterministic repository checks. |
| `scripts/build_release.py` | Deterministic ZIP and SHA-256 builder. |
| `tests/` | Standard-library unit and integration tests. |
| `README.md`, `README.zh-CN.md` | English and Chinese product explanation and installation guide. |
| `HOW_IT_WORKS.md` | Current product behavior, architecture, evidence, and limits. |
| `docs/distribution.md` | Distribution-channel status and release identity. |
| `docs/releases/v0.1.0.md` | Release notes for the first public version. |
| `docs/verification/v0.1.0.md` | Exact commands, commit, environment, checksums, and observed results. |

## Review Focus

1. A source document contains commands, URLs, units, or warnings that a rewrite must preserve. Task 3 tests exact preservation.
2. The user asks only for a review, or asks for marketing or literary writing. Task 2 pins the scope and non-mutation contract.
3. A generated document is fluent but hides the answer, omits prerequisites, or gives no verification step. Task 3 evaluates these observable failures.
4. A private value exists only in Git history or PNG metadata. Task 4 must fail before publication.
5. Manifests, `VERSION`, Release ZIP content, and Git tag disagree. Tasks 1, 5, and 7 enforce one release identity.

---

### Task 1: Create the cross-client package identity

**Files:**

- Create: `VERSION`
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `plugin.json`
- Create: `.codex-plugin/plugin.json`
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Create: `skills/writing-doc/agents/openai.yaml`
- Create: `tests/__init__.py`
- Create: `tests/test_manifests.py`

**Interfaces:**

- Consumes: repository name `writing-doc-skill`, plugin name `writing-doc`, version `0.1.0`, and repository URL `https://github.com/joevilcai666/writing-doc-skill`.
- Produces: four JSON manifests with consistent name, version, repository, license, and skill path; one `agents/openai.yaml` with implicit invocation enabled.

- [ ] **Step 1: Verify current primary specifications**

Read the current Agent Skills specification, portable Agent Plugin schema, current OpenAI plugin documentation, and current Claude Code plugin documentation. Record only fields required by those sources. If a current source conflicts with the approved structure, update the spec before implementation and request review of the changed contract.

- [ ] **Step 2: Write failing manifest tests**

Create `tests/test_manifests.py`:

```python
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
        portable = self.load("plugin.json")
        codex = self.load(".codex-plugin/plugin.json")
        claude = self.load(".claude-plugin/plugin.json")
        market = self.load(".claude-plugin/marketplace.json")
        for manifest in (portable, codex, claude):
            self.assertEqual(manifest["name"], "writing-doc")
            self.assertEqual(manifest["version"], version)
            self.assertEqual(manifest["repository"], REPOSITORY)
            self.assertEqual(manifest["license"], "MIT")
        self.assertEqual(market["plugins"][0]["version"], version)
        self.assertEqual(market["plugins"][0]["source"], "./")

    def test_codex_points_to_shared_skill_directory(self):
        codex = self.load(".codex-plugin/plugin.json")
        self.assertEqual(codex["skills"], "./skills/")
        self.assertTrue((ROOT / "skills/writing-doc/SKILL.md").is_file())

    def test_openai_yaml_uses_explicit_skill_name(self):
        text = (ROOT / "skills/writing-doc/agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Writing Doc"', text)
        self.assertIn("$writing-doc", text)
        self.assertNotIn("allow_implicit_invocation: false", text)
```

- [ ] **Step 3: Run tests and confirm RED**

Run: `python3 -m unittest tests.test_manifests -v`

Expected: errors for missing `VERSION`, manifests, and skill files.

- [ ] **Step 4: Add version, ignore rules, and MIT license**

Write `0.1.0` to `VERSION`. Ignore `.DS_Store`, `__pycache__/`, `*.pyc`, `.venv/`, `dist/`, temporary evaluation runs, and local validator installations. Use the standard MIT license text with copyright year `2026` and holder `Writing Doc Contributors`.

- [ ] **Step 5: Add consistent portable, Codex, and Claude manifests**

Use this release identity in every manifest:

```json
{
  "name": "writing-doc",
  "version": "0.1.0",
  "description": "Turn verbose AI output into technical documentation a target audience can understand and act on.",
  "author": {"name": "Writing Doc Contributors"},
  "repository": "https://github.com/joevilcai666/writing-doc-skill",
  "license": "MIT"
}
```

Add only the client-specific fields that current official documentation requires. The Codex compatibility manifest must point `skills` to `./skills/`. The Claude marketplace must expose one local plugin named `writing-doc` from `./`.

- [ ] **Step 6: Add OpenAI skill metadata**

Create `skills/writing-doc/agents/openai.yaml`:

```yaml
interface:
  display_name: "Writing Doc"
  short_description: "Make technical documentation clear and actionable."
  brand_color: "#0B3155"
  default_prompt: "Use $writing-doc to rewrite this technical document for its target audience."
policy:
  allow_implicit_invocation: true
```

- [ ] **Step 7: Run manifest tests and JSON checks**

Run:

```bash
python3 -m unittest tests.test_manifests -v
python3 -m json.tool plugin.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -m json.tool .claude-plugin/plugin.json >/dev/null
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null
```

Expected: all tests pass and every JSON command exits with status 0.

- [ ] **Step 8: Commit the package identity**

```bash
git add VERSION .gitignore LICENSE plugin.json .codex-plugin .claude-plugin skills/writing-doc/agents tests
git commit -m "feat: add cross-client writing-doc manifests"
```

---

### Task 2: Package the authoritative writing skill and approved visuals

**Files:**

- Create: `skills/writing-doc/SKILL.md`
- Create: `assets/x-problem-en.png`
- Create: `assets/x-solution-en.png`
- Create: `assets/x-problem-zh-CN.png`
- Create: `assets/x-solution-zh-CN.png`
- Create: `assets/social-preview.png`
- Create: `tests/test_skill_contract.py`

**Interfaces:**

- Consumes: the installed source skill at `${CODEX_HOME:-$HOME/.codex}/skills/writing-doc/SKILL.md` and the four approved images in the task output directory.
- Produces: one self-contained skill with `name: writing-doc`; four exact 1200 × 1200 images; one 1280 × 640 social preview.

- [ ] **Step 1: Write failing skill-contract tests**

Create `tests/test_skill_contract.py`:

```python
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
```

- [ ] **Step 2: Run tests and confirm RED**

Run: `python3 -m unittest tests.test_skill_contract -v`

Expected: missing skill and image files.

- [ ] **Step 3: Copy the authoritative skill without broadening its scope**

Copy the approved `writing-doc` content into `skills/writing-doc/SKILL.md`. Preserve its Chinese instructions, scope exclusions, review-only boundary, accuracy requirements, and final reader-focused checklist. Do not add installation or repository-maintenance content to the skill itself.

- [ ] **Step 4: Copy the four approved images into `assets/`**

Map the approved outputs exactly:

```text
problem-en.png       -> assets/x-problem-en.png
solution-en.png      -> assets/x-solution-en.png
problem-zh-CN.png    -> assets/x-problem-zh-CN.png
solution-zh-CN.png   -> assets/x-solution-zh-CN.png
```

Retain PNG format and 1200 × 1200 dimensions. Do not regenerate approved artwork.

- [ ] **Step 5: Generate and inspect the GitHub social preview**

Use the built-in image-generation path. Create a 2:1 composition with the approved navy, off-white, coral, green, and blue visual language. Use only this text:

```text
writing-doc
AI wrote a lot. Make every word land.
```

Inspect the result for exact text, safe margins, and legibility. Save the accepted asset as `assets/social-preview.png` and resample it to exactly 1280 × 640 without changing its aspect ratio.

- [ ] **Step 6: Run the skill validator and focused tests**

Run:

```bash
python3 -m unittest tests.test_skill_contract -v
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" skills/writing-doc
```

Expected: all tests and the validator pass.

- [ ] **Step 7: Commit the skill and visuals**

```bash
git add skills/writing-doc/SKILL.md assets tests/test_skill_contract.py
git commit -m "feat: package writing-doc skill and visuals"
```

---

### Task 3: Add the synthetic demonstration and behavioral rubric

**Files:**

- Create: `demo/source/AI_SETUP_GUIDE.md`
- Create: `demo/expected/SETUP_GUIDE.md`
- Create: `demo/README.md`
- Create: `evals/cases.json`
- Create: `evals/run_rubric.py`
- Create: `evals/README.md`
- Create: `tests/test_rubric.py`

**Interfaces:**

- Consumes: a Markdown document path and case identifier.
- Produces: `evaluate(text: str, case: dict) -> list[str]`, where an empty list means the observable rubric passed; CLI exit 0 for pass and 1 for failures.

- [ ] **Step 1: Write failing rubric tests**

Create `tests/test_rubric.py`:

```python
from pathlib import Path
import json
import sys
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
```

- [ ] **Step 2: Run tests and confirm RED**

Run: `python3 -m unittest tests.test_rubric -v`

Expected: import or missing-file errors.

- [ ] **Step 3: Create a synthetic verbose setup guide**

Use a fictional local service named `Lantern API`. Include these facts in the source:

```text
Python 3.11+
LANTERN_TOKEN
python -m lantern serve --port 4310
http://127.0.0.1:4310/health
HTTP 200
WARNING: Never commit LANTERN_TOKEN.
```

Make the source intentionally verbose and poorly ordered. Hide the command after background material, omit a clear expected response, and mix setup, concepts, and troubleshooting in long paragraphs. Use no real company, token, domain, or user data.

- [ ] **Step 4: Create the expected audience-focused guide**

Write for a developer who needs to run the service locally. Put the result and command first. Then provide prerequisites, three numbered steps, an expected `HTTP 200` result, the warning, and one symptom-cause-fix troubleshooting entry. Preserve every required literal exactly.

- [ ] **Step 5: Implement the deterministic rubric**

Define `evals/cases.json` with one `lantern-setup` case and these rules:

```json
{
  "id": "lantern-setup",
  "required_literals": [
    "Python 3.11+",
    "LANTERN_TOKEN",
    "python -m lantern serve --port 4310",
    "http://127.0.0.1:4310/health",
    "HTTP 200",
    "WARNING: Never commit LANTERN_TOKEN."
  ],
  "answer_first_before": "## Why this service exists",
  "required_sections": ["Prerequisites", "Steps", "Expected result", "Troubleshooting"]
}
```

`evaluate` must return stable rule identifiers: `required-literal:<value>`, `answer-first`, `missing-section:<name>`, `verification`, and `long-paragraph`. It must not score exact marketing language.

- [ ] **Step 6: Add evaluation documentation and run RED to GREEN**

Document that the expected result is synthetic and illustrates observable outcomes, not one mandatory wording. Run:

```bash
python3 -m unittest tests.test_rubric -v
python3 evals/run_rubric.py --case lantern-setup demo/expected/SETUP_GUIDE.md
```

Expected: all tests pass and the CLI reports `PASS lantern-setup`.

- [ ] **Step 7: Commit the demonstration and rubric**

```bash
git add demo evals tests/test_rubric.py
git commit -m "test: add synthetic writing-doc evaluation"
```

---

### Task 4: Add deterministic repository and privacy checks

**Files:**

- Create: `scripts/privacy_scan.py`
- Create: `scripts/check_repo.py`
- Create: `tests/test_privacy_scan.py`
- Create: `tests/test_check_repo.py`

**Interfaces:**

- `privacy_scan.py`: `scan_text(text: str, path: str, commit: str | None = None) -> list[dict]`; `scan_png(path: Path) -> list[dict]`; `scan_repository(root: Path, history: bool) -> list[dict]`.
- `check_repo.py`: `check_structure(root: Path) -> list[str]`; `check_markdown_links(root: Path) -> list[str]`; `main() -> int`.
- CLI exit 0 when no finding exists and exit 1 when any deterministic check fails.

- [ ] **Step 1: Write failing privacy tests**

Create tests that assemble sensitive strings at runtime so those strings do not enter public history:

```python
def test_detects_home_path_without_committing_private_literal(self):
    value = "/" + "Users" + "/sample-person/private/file.md"
    findings = scan_text(value, "fixture.md")
    self.assertEqual(findings[0]["rule"], "home-path")
    self.assertNotIn("sample-person", str(findings))

def test_detects_credential_without_echoing_it(self):
    value = "gh" + "p_" + "A" * 30
    findings = scan_text(value, "fixture.txt")
    self.assertEqual(findings[0]["rule"], "credential")
    self.assertEqual(findings[0]["match"], "[REDACTED]")
```

Also test email addresses, private keys, signed URLs, PNG `tEXt` chunks, current untracked files, and a sensitive value in a deleted Git-history blob.

- [ ] **Step 2: Write failing repository-check tests**

Test inconsistent versions, invalid JSON, missing local Markdown links, missing images, wrong PNG dimensions, absent `SKILL.md`, and a clean temporary package.

- [ ] **Step 3: Run tests and confirm RED**

Run:

```bash
python3 -m unittest tests.test_privacy_scan -v
python3 -m unittest tests.test_check_repo -v
```

Expected: imports fail because both scripts are absent.

- [ ] **Step 4: Implement the privacy scanner**

Use standard-library regular expressions for home paths, common credential prefixes, private-key headers, signed URLs, and email addresses. Parse PNG chunks and reject `tEXt`, `zTXt`, `iTXt`, and `eXIf`. Use `git ls-files` for the current tree and `git rev-list --objects --all` plus `git cat-file` for history. Report only rule, redacted path, line, and optional commit. Never print the matched value.

- [ ] **Step 5: Implement the repository checker**

Check version consistency, required paths, JSON parsing, skill frontmatter, relative Markdown links, PNG signatures and dimensions, README image references, rubric output, unit tests, privacy, and `git diff --check`. Run available external validators and mark unavailable validators as `SKIP`, but return failure in release mode when a required validator is missing.

Support:

```text
python3 scripts/check_repo.py
python3 scripts/check_repo.py --release
```

- [ ] **Step 6: Run focused and full checks**

Run:

```bash
python3 -m unittest tests.test_privacy_scan tests.test_check_repo -v
python3 -m unittest discover -s tests -v
python3 scripts/check_repo.py
```

Expected: all tests pass and deterministic checks report `PASS`.

- [ ] **Step 7: Commit the release checks**

```bash
git add scripts/privacy_scan.py scripts/check_repo.py tests/test_privacy_scan.py tests/test_check_repo.py
git commit -m "test: add privacy and repository release gates"
```

---

### Task 5: Write bilingual public documentation and project behavior

**Files:**

- Create: `README.md`
- Create: `README.zh-CN.md`
- Create: `HOW_IT_WORKS.md`
- Create: `CONTRIBUTING.md`
- Create: `SECURITY.md`
- Create: `CHANGELOG.md`
- Create: `docs/distribution.md`
- Create: `.github/ISSUE_TEMPLATE/bug.yml`
- Create: `.github/ISSUE_TEMPLATE/compatibility.yml`
- Create: `.github/ISSUE_TEMPLATE/feature.yml`
- Create: `.github/pull_request_template.md`
- Create: `tests/test_public_docs.py`

**Interfaces:**

- Consumes: approved copy, images, install commands validated in Task 7, synthetic demo, evidence vocabulary, and version `0.1.0`.
- Produces: equivalent English and Chinese discovery paths, current `HOW_IT_WORKS.md`, contribution and security routes, and exact distribution statuses.

- [ ] **Step 1: Write failing public-document tests**

Create `tests/test_public_docs.py` with assertions that:

```python
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DOCS = (
    ROOT / "README.md",
    ROOT / "README.zh-CN.md",
    ROOT / "HOW_IT_WORKS.md",
    ROOT / "docs/distribution.md",
)


class PublicDocumentTests(unittest.TestCase):
    def test_readmes_use_approved_product_message(self):
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        self.assertIn("AI wrote a lot. Your reader still does not get it.", english)
        self.assertIn("AI 写了一大篇，读完还是不懂。", chinese)
        self.assertIn("assets/x-problem-en.png", english)
        self.assertIn("assets/x-solution-zh-CN.png", chinese)

    def test_docs_do_not_overstate_evidence(self):
        combined = "\n".join(path.read_text(encoding="utf-8") for path in PUBLIC_DOCS)
        self.assertNotIn("officially approved", combined.lower())
        self.assertIn("Locally verified", combined)
        self.assertIn("Publicly verified", combined)
```

Also require working language links, installation headings, privacy statement, supported-task boundary, demo links, two to four Mermaid diagrams in `HOW_IT_WORKS.md`, and a `最后更新时间：2026-10-15` line.

- [ ] **Step 2: Run tests and confirm RED**

Run: `python3 -m unittest tests.test_public_docs -v`

Expected: missing public documents.

- [ ] **Step 3: Write the English and Chinese READMEs**

Use the approved opening copy and image order. Put the shortest verified install command before background explanation. Include Codex, Claude Code, `npx skills`, and manual installation. Link each README to the other language. Explain supported tasks, boundaries, privacy, synthetic demo, version pinning, uninstall, verification evidence, and contribution routes.

Do not claim a command passed until Task 7 records the exact command and commit. Before that verification, label commands `Planned for v0.1.0 verification`.

- [ ] **Step 4: Write `HOW_IT_WORKS.md` as a current-state product document**

Include:

- one-sentence product position;
- package architecture diagram;
- skill request workflow diagram;
- release evidence flow diagram;
- module responsibilities in product language;
- the distinction between implemented, locally verified, publicly verified, and user accepted;
- current limits;
- `最后更新时间：2026-10-15`.

Use the analogy: “The skill is an editor's desk: it keeps the source facts but rearranges them so the intended reader can find and use them.”

- [ ] **Step 5: Add contribution, security, distribution, and issue documents**

`SECURITY.md` must direct users to GitHub private vulnerability reporting and tell them not to open public issues with credentials or private documents. `CONTRIBUTING.md` must require synthetic fixtures and local checks. `docs/distribution.md` must use the status set `planned`, `published`, `listed`, `submitted`, `rejected`, or `not adopted`, with evidence links where available.

- [ ] **Step 6: Run document and repository checks**

Run:

```bash
python3 -m unittest tests.test_public_docs -v
python3 scripts/check_repo.py
```

Expected: public-document tests and deterministic checks pass.

- [ ] **Step 7: Commit public documentation**

```bash
git add README.md README.zh-CN.md HOW_IT_WORKS.md CONTRIBUTING.md SECURITY.md CHANGELOG.md docs/distribution.md .github tests/test_public_docs.py
git commit -m "docs: add bilingual writing-doc release guide"
```

---

### Task 6: Build a deterministic release archive

**Files:**

- Create: `scripts/build_release.py`
- Create: `tests/test_build_release.py`
- Create: `docs/releases/v0.1.0.md`
- Create: `docs/verification/v0.1.0.md`

**Interfaces:**

- Consumes: repository root, `VERSION`, and output directory.
- Produces: `dist/writing-doc-skill-v0.1.0.zip` and `dist/writing-doc-skill-v0.1.0.zip.sha256`.
- Produces function `build_release(root: Path, output_dir: Path) -> tuple[Path, str]`.

- [ ] **Step 1: Write failing deterministic-build tests**

Create `tests/test_build_release.py`:

```python
from pathlib import Path
import tempfile
import unittest
import zipfile

from scripts.build_release import build_release

ROOT = Path(__file__).resolve().parents[1]


class ReleaseBuildTests(unittest.TestCase):
    def test_two_builds_have_the_same_digest(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            _, digest_a = build_release(ROOT, Path(first))
            _, digest_b = build_release(ROOT, Path(second))
            self.assertEqual(digest_a, digest_b)

    def test_archive_contains_public_package_and_excludes_local_state(self):
        with tempfile.TemporaryDirectory() as directory:
            archive, _ = build_release(ROOT, Path(directory))
            with zipfile.ZipFile(archive) as bundle:
                names = set(bundle.namelist())
            self.assertIn("writing-doc-skill/skills/writing-doc/SKILL.md", names)
            self.assertIn("writing-doc-skill/plugin.json", names)
            self.assertFalse(any("/.git/" in name or "/dist/" in name for name in names))
```

- [ ] **Step 2: Run tests and confirm RED**

Run: `python3 -m unittest tests.test_build_release -v`

Expected: import failure because the builder does not exist.

- [ ] **Step 3: Implement the deterministic ZIP builder**

Use `git ls-files -z` as the archive file list. Exclude design and implementation process files under `docs/superpowers/`, local validator state, and `dist/`. Sort paths, set every ZIP timestamp to `1980-01-01 00:00:00`, normalize permissions to `0644` or `0755`, use UTF-8 names, and write a single top-level `writing-doc-skill/` directory. Hash the final bytes with SHA-256.

- [ ] **Step 4: Write release and verification documents**

`docs/releases/v0.1.0.md` must state the product promise, supported clients, scope boundaries, assets, install routes, and known limits. `docs/verification/v0.1.0.md` must start with all results marked `pending` and provide exact sections for commit, environment, commands, local results, public results, checksum, external directories, and user acceptance.

- [ ] **Step 5: Run build tests and create the candidate archive**

Run:

```bash
python3 -m unittest tests.test_build_release -v
python3 scripts/build_release.py --output dist
shasum -a 256 -c dist/writing-doc-skill-v0.1.0.zip.sha256
```

Expected: tests pass and `shasum` reports `OK`.

- [ ] **Step 6: Run the full local gate**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_repo.py --release
git diff --check
```

Expected: all tests and required validators pass. If a required external validator is unavailable, stop publication and record it as a blocker.

- [ ] **Step 7: Commit release automation and candidate documents**

```bash
git add scripts/build_release.py tests/test_build_release.py docs/releases/v0.1.0.md docs/verification/v0.1.0.md
git commit -m "build: add deterministic v0.1.0 release"
```

---

### Task 7: Review, publish, and verify the public release

**Files:**

- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Modify: `HOW_IT_WORKS.md`
- Modify: `docs/distribution.md`
- Modify: `docs/verification/v0.1.0.md`
- Modify: `CHANGELOG.md`

**Interfaces:**

- Consumes: a clean, locally reviewed exact commit and deterministic archive from Task 6.
- Produces: public repository `https://github.com/joevilcai666/writing-doc-skill`, branch `main`, annotated tag `v0.1.0`, GitHub Release, downloadable ZIP and checksum, and public installation evidence.

- [ ] **Step 1: Perform a whole-branch pre-publication review**

Review the complete diff from the root design commit to `HEAD`. Check skill scope, manifest compatibility, private data, README claims, image text, archive contents, and release identity. Fix each important finding with a failing test when behavior changes. Repeat the full local gate after fixes.

- [ ] **Step 2: Record the exact candidate and rebuild from it**

Run:

```bash
git status --short
git rev-parse HEAD
python3 scripts/check_repo.py --release
python3 scripts/build_release.py --output dist
shasum -a 256 -c dist/writing-doc-skill-v0.1.0.zip.sha256
```

Expected: clean tracked tree, one exact commit, all checks pass, and checksum reports `OK`.

- [ ] **Step 3: Create the empty public repository without pushing content**

Run:

```bash
gh repo create joevilcai666/writing-doc-skill --public --description "Turn verbose AI output into technical documentation a target audience can understand and act on."
git remote add origin https://github.com/joevilcai666/writing-doc-skill.git
```

Expected: the repository exists but no unreviewed branch is pushed.

- [ ] **Step 4: Push the reviewed commit to `main` and create the release tag**

Run:

```bash
git push -u origin HEAD:main
git tag -a v0.1.0 -m "writing-doc v0.1.0"
git push origin v0.1.0
```

Verify that `git ls-remote origin refs/heads/main refs/tags/v0.1.0` resolves to the intended commit and annotated tag object.

- [ ] **Step 5: Create the GitHub Release and repository metadata**

Run:

```bash
gh release create v0.1.0 dist/writing-doc-skill-v0.1.0.zip dist/writing-doc-skill-v0.1.0.zip.sha256 --title "writing-doc v0.1.0" --notes-file docs/releases/v0.1.0.md
gh repo edit joevilcai666/writing-doc-skill --add-topic agent-skills --add-topic codex --add-topic claude-code --add-topic technical-writing --add-topic documentation
```

Upload `assets/social-preview.png` through GitHub repository settings if an authenticated, unlocked UI is available. If UI access is unavailable, record the action as pending instead of claiming completion.

- [ ] **Step 6: Verify anonymous clone, archive, and generic skill installation**

Use fresh temporary directories created with `mktemp -d`. Verify:

```bash
git clone --depth 1 --branch v0.1.0 https://github.com/joevilcai666/writing-doc-skill.git
npx -y skills add joevilcai666/writing-doc-skill --skill writing-doc --yes
```

Compare the installed `SKILL.md` byte-for-byte with the tagged source. Download the Release ZIP anonymously, verify the published SHA-256, extract it, and run the package checker where applicable.

- [ ] **Step 7: Verify Codex and Claude installation paths**

Install from the public repository into isolated client directories. Run the current Codex plugin validation or installation command and `claude plugin validate --strict .` on the public clone. Record the exact versions, commands, exits, and any client limitation. Do not reuse the developer's active global skill directories.

- [ ] **Step 8: Inspect discovery and external distribution without overstating status**

Check the public GitHub pages and skills.sh discovery page. Record `listed` only when the public page resolves to this repository and skill. Record OpenAI and Anthropic directory submissions as `pending` unless an authenticated submission and receipt exist. Do not submit to directories whose permissions, version pinning, or removal path cannot be verified.

- [ ] **Step 9: Update live evidence and `HOW_IT_WORKS.md`**

Replace planned statuses with observed results in `docs/verification/v0.1.0.md` and `docs/distribution.md`. Update `HOW_IT_WORKS.md` diagrams, evidence table, current limits, and `最后更新时间：2026-10-15`. Update README verification language without changing the approved product message or image order.

- [ ] **Step 10: Run final checks and push the evidence commit**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_repo.py --release
git diff --check
git status --short
```

Commit and push:

```bash
git add README.md README.zh-CN.md HOW_IT_WORKS.md CHANGELOG.md docs/distribution.md docs/verification/v0.1.0.md
git commit -m "docs: record v0.1.0 public verification"
git push origin HEAD:main
```

- [ ] **Step 11: Verify final public state**

Confirm with GitHub API and anonymous HTTP requests that `main`, the `v0.1.0` tag, Release assets, READMEs, `HOW_IT_WORKS.md`, and primary links resolve. Re-run the privacy scan against the full local history. The final report must list completed work, pending manual actions, exact public URLs, commit IDs, test counts, and checksum.
