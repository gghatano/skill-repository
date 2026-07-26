"""Tests for the deep-research plugin's structural checks.

The plugin ships a lint script rather than a package, so it is loaded by path —
the same way it will be invoked in a project that installed the plugin.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = REPO_ROOT / "plugins" / "deep-research"
LINT_PATH = PLUGIN_ROOT / "scripts" / "research_lint.py"

_spec = importlib.util.spec_from_file_location("research_lint", LINT_PATH)
research_lint = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(research_lint)


RUN_ID = "example-repo-20260726-a3f9b7"
QUOTE = "The project favours a small, dependency-free core over a plugin system."


def build_run(root: Path, *, shipped: bool = True) -> Path:
    """Create a complete Phase 1 run: a GitHub repository investigation."""
    vault = root / "research"
    run_dir = vault / "runs" / RUN_ID
    (run_dir / "drafts").mkdir(parents=True)
    (run_dir / "verification").mkdir()
    (vault / "notes").mkdir(parents=True)

    (run_dir / "query.md").write_text(
        "# Canonical Query\n\nexample/repo の設計思想を、README と実装から調べてほしい。\n",
        encoding="utf-8",
    )
    (run_dir / "execution-contract.json").write_text(json.dumps({
        "output_path": f"research/runs/{RUN_ID}/final-report.md",
        "output_format": "markdown-report",
        "language": "ja",
        "citation_style": "inline-url",
        "required_sections": ["設計思想"],
        "prohibitions": ["未確認の数値を書かない"],
    }, ensure_ascii=False), encoding="utf-8")
    (run_dir / "run.json").write_text(json.dumps({
        "run_id": RUN_ID,
        "status": "shipped" if shipped else "running",
        "tier": "quick",
        "modality": "collect",
        "current_step": "ship-verify" if shipped else "source-collect",
        "next_step": "" if shipped else "draft-compose",
        "created_at": "2026-07-26T15:00:00+09:00",
        "updated_at": "2026-07-26T15:40:00+09:00",
        "query_file": f"research/runs/{RUN_ID}/query.md",
        "execution_contract_file": f"research/runs/{RUN_ID}/execution-contract.json",
        "completed_steps": ["research-router", "query-decompose", "source-collect"],
        "failed_steps": [],
        "blocked_reasons": [],
        "human_actions_required": [],
    }, ensure_ascii=False), encoding="utf-8")
    (run_dir / "decomposition.json").write_text(json.dumps({
        "run_id": RUN_ID,
        "ambiguous_terms": ["設計思想"],
        "open_questions": [],
        "atomic_items": [{
            "id": "Q-01",
            "question": "README はどのような設計方針を掲げているか",
            "importance": "high",
            "evidence_required": ["official-doc"],
            "output_section": "設計思想",
            "status": "verified",
        }],
    }, ensure_ascii=False), encoding="utf-8")

    (vault / "notes" / "src-001.md").write_text(
        "---\n"
        "source_id: src-001\n"
        "title: example/repo README\n"
        "url: https://github.com/example/repo\n"
        "source_type: official-doc\n"
        "retrieved_at: 2026-07-26T15:10:00+09:00\n"
        "independence_cluster: cluster-001\n"
        "sensitivity: public\n"
        "---\n\n"
        "# Summary\n\n設計方針が README に明記されている。\n\n"
        f"# Quotable Passages\n\n{QUOTE}\n\n"
        "# Notes\n\n-\n",
        encoding="utf-8",
    )
    (run_dir / "sources.json").write_text(json.dumps({
        "run_id": RUN_ID,
        "failed_fetches": [],
        "sources": [{
            "source_id": "src-001",
            "title": "example/repo README",
            "url": "https://github.com/example/repo",
            "source_type": "official-doc",
            "retrieved_at": "2026-07-26T15:10:00+09:00",
            "independence_cluster": "cluster-001",
            "quality_status": "confirmed",
            "sensitivity": "public",
            "supports": ["Q-01"],
            "note_path": "notes/src-001.md",
        }],
    }, ensure_ascii=False), encoding="utf-8")

    # Long enough that the patch-scope ratio means something: a two-line document
    # would make any single patch look like a rewrite.
    filler = "\n\n".join(
        f"README の記述{n}から読み取れる方針を、対応する箇所とともに整理する。"
        for n in range(1, 13)
    )
    body = (
        "# example/repo の設計思想\n\n"
        "## 設計思想\n\n"
        "README は小さな中核を保つ方針を明示している"
        "（[example/repo README](https://github.com/example/repo)）。\n\n"
        f"> {QUOTE}\n\n"
        f"{filler}\n"
    )
    (run_dir / "drafts" / "draft-01.md").write_text(body, encoding="utf-8")
    (run_dir / "verification" / "citation-check.json").write_text(json.dumps({
        "run_id": RUN_ID,
        "kind": "citation",
        "verdict": "pass",
        "checked_at": "2026-07-26T15:35:00+09:00",
        "unverified_numbers": [],
        "checks": [{
            "check_id": "CIT-001",
            "name": "quote-exists",
            "result": "pass",
            "detail": "引用が Source Note に存在する",
            "target": "src-001",
        }],
    }, ensure_ascii=False), encoding="utf-8")

    if shipped:
        (run_dir / "final-report.md").write_text(body, encoding="utf-8")
        (run_dir / "verification" / "ship-check.json").write_text(json.dumps({
            "run_id": RUN_ID,
            "kind": "ship",
            "verdict": "pass",
            "checked_at": "2026-07-26T15:40:00+09:00",
            "checks": [{
                "check_id": "SHIP-001",
                "name": "query-coverage",
                "result": "pass",
                "detail": "High Importance の論点をすべて処理",
                "target": "decomposition.json",
            }],
        }, ensure_ascii=False), encoding="utf-8")
    return run_dir


class SchemaValidatorTest(unittest.TestCase):
    def test_accepts_a_valid_instance(self) -> None:
        schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}}
        self.assertEqual([], research_lint.validate_schema({"a": "x"}, schema))

    def test_reports_missing_required_property(self) -> None:
        schema = {"type": "object", "required": ["a"]}
        errors = research_lint.validate_schema({}, schema)
        self.assertTrue(any("missing required property 'a'" in e for e in errors))

    def test_enforces_enum_pattern_and_items(self) -> None:
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["pass", "block"]},
                "run_id": {"type": "string", "pattern": r"^[a-z]+-[0-9]{8}-[a-z0-9]{6}$"},
                "items": {"type": "array", "minItems": 1, "items": {"type": "integer"}},
            },
        }
        errors = research_lint.validate_schema(
            {"status": "maybe", "run_id": "BAD", "items": ["x"]}, schema
        )
        self.assertEqual(3, len(errors), errors)

    def test_type_mismatch_stops_further_checks(self) -> None:
        schema = {"type": "object", "required": ["a"]}
        self.assertEqual(1, len(research_lint.validate_schema([], schema)))

    def test_bundled_schemas_are_readable_json(self) -> None:
        schemas = sorted((PLUGIN_ROOT / "schemas").glob("*.json"))
        self.assertTrue(schemas)
        for path in schemas:
            with self.subTest(schema=path.name):
                self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)


class FrontmatterTest(unittest.TestCase):
    def test_parses_source_note_frontmatter(self) -> None:
        text = "---\nsource_id: src-001\nurl: https://example.com\n---\n\n# Summary\n"
        self.assertEqual(
            {"source_id": "src-001", "url": "https://example.com"},
            research_lint.parse_frontmatter(text),
        )

    def test_returns_empty_without_frontmatter(self) -> None:
        self.assertEqual({}, research_lint.parse_frontmatter("# No frontmatter\n"))

    def test_extracts_named_section(self) -> None:
        text = "# Summary\n\nああ\n\n# Quotable Passages\n\n引用文\n\n# Notes\n\nいい\n"
        self.assertIn("引用文", research_lint.extract_section(text, "Quotable Passages"))
        self.assertNotIn("いい", research_lint.extract_section(text, "Quotable Passages"))


class EndToEndRunTest(unittest.TestCase):
    """A complete run must pass every Phase 1 lint."""

    def test_complete_run_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            report = research_lint.run_lints(run_dir)
            failed = [f for f in report["findings"] if f["result"] == "fail"]
            self.assertEqual([], failed, failed)
            self.assertEqual("pass", report["verdict"])

    def test_in_progress_run_skips_rather_than_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp), shipped=False)
            report = research_lint.run_lints(run_dir)
            self.assertEqual("pass", report["verdict"])
            lints = {f["lint"] for f in report["findings"] if f["result"] == "skipped"}
            self.assertIn("internal-leak", lints)
            self.assertIn("placeholder-check", lints)

    def test_cli_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            self.assertEqual(0, research_lint.main([str(run_dir), "--json"]))
            (run_dir / "query.md").unlink()
            self.assertEqual(1, research_lint.main([str(run_dir), "--json"]))

    def test_missing_run_directory_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(2, research_lint.main([str(Path(temp) / "absent")]))


class LintFailureTest(unittest.TestCase):
    """Each lint must actually catch the failure it is responsible for."""

    def test_missing_canonical_query_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            (run_dir / "query.md").write_text("", encoding="utf-8")
            self.assertIn("query-preserved", self._failed_lints(run_dir))

    def test_corrupt_json_fails_schema_lint(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            (run_dir / "run.json").write_text("{ not json", encoding="utf-8")
            self.assertIn("schema-valid", self._failed_lints(run_dir))

    def test_schema_violation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            data = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            data["status"] = "almost-done"  # not in the enum
            (run_dir / "run.json").write_text(json.dumps(data), encoding="utf-8")
            self.assertIn("schema-valid", self._failed_lints(run_dir))

    def test_uncovered_high_importance_item_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            data = json.loads((run_dir / "decomposition.json").read_text(encoding="utf-8"))
            data["atomic_items"][0]["status"] = "uncovered"
            (run_dir / "decomposition.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertIn("coverage-complete", self._failed_lints(run_dir))

    def test_source_without_note_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            (run_dir.parent.parent / "notes" / "src-001.md").unlink()
            self.assertIn("source-metadata", self._failed_lints(run_dir))

    def test_source_missing_retrieved_at_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            data = json.loads((run_dir / "sources.json").read_text(encoding="utf-8"))
            data["sources"][0]["retrieved_at"] = ""
            (run_dir / "sources.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertIn("source-metadata", self._failed_lints(run_dir))

    def test_invented_quote_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            (run_dir / "final-report.md").write_text(
                "# 報告\n\n> この文は情報源のどこにも書かれていない捏造引用である。\n",
                encoding="utf-8",
            )
            self.assertIn("quote-integrity", self._failed_lints(run_dir))

    def test_internal_path_leak_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            (run_dir / "final-report.md").write_text(
                f"# 報告\n\n詳細は research/runs/{RUN_ID}/scaffold.md を参照。\n", encoding="utf-8"
            )
            self.assertIn("internal-leak", self._failed_lints(run_dir))

    def test_placeholder_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            (run_dir / "final-report.md").write_text("# 報告\n\nTODO: あとで書く\n", encoding="utf-8")
            self.assertIn("placeholder-check", self._failed_lints(run_dir))

    def _failed_lints(self, run_dir: Path) -> set[str]:
        report = research_lint.run_lints(run_dir)
        self.assertEqual("block", report["verdict"])
        return {f["lint"] for f in report["findings"] if f["result"] == "fail"}


def add_phase2_artifacts(run_dir: Path, *, severity: str = "critical",
                         status: str = "resolved", changed_lines: int = 4) -> None:
    """Layer claims / reviews / patches onto a Phase 1 run."""
    (run_dir / "reviews").mkdir(exist_ok=True)
    (run_dir / "patches").mkdir(exist_ok=True)

    (run_dir / "claims.json").write_text(json.dumps({
        "run_id": RUN_ID,
        "claims": [
            {
                "claim_id": "C-001",
                "statement": "README は小さな中核を保つ方針を掲げている",
                "claim_type": "author-claim",
                "confidence": "high",
                "supports": [{"source_id": "src-001", "location": "README 冒頭",
                              "evidence_type": "document"}],
                "conditions": [], "limitations": [],
                "related_atomic_items": ["Q-01"],
            },
            {
                "claim_id": "C-002",
                "statement": "この方針は依存追加への慎重さとして表れていると考えられる",
                "claim_type": "inference",
                "confidence": "medium",
                "supports": [],
                "derived_from": ["C-001"],
                "conditions": [], "limitations": ["著者の明示的な主張ではない"],
                "related_atomic_items": ["Q-01"],
            },
        ],
    }, ensure_ascii=False), encoding="utf-8")

    (run_dir / "reviews" / "evidence-review.json").write_text(json.dumps({
        "run_id": RUN_ID,
        "reviewer": "evidence",
        "reviewed_file": "drafts/draft-01.md",
        "findings": [{
            "finding_id": "F-001",
            "reviewer": "evidence",
            "severity": severity,
            "target": {"file": "drafts/draft-01.md", "section": "設計思想",
                       "quote": "小さな中核を保つ方針"},
            "problem": "推論を著者の主張として書いている",
            "evidence": ["src-001"],
            "recommended_action": "推論であることを明示する",
            "requires_additional_research": False,
            "status": status,
        }],
    }, ensure_ascii=False), encoding="utf-8")

    (run_dir / "patches" / "applied-patches.json").write_text(json.dumps({
        "run_id": RUN_ID,
        "kind": "applied",
        "max_total_changed_ratio": 0.25,
        "patches": [{
            "patch_id": "P-001",
            "finding_ids": ["F-001"],
            "target_file": "drafts/draft-01.md",
            "target_section": "設計思想",
            "operation": "replace",
            "before_summary": "推論を著者の主張として記述",
            "after_summary": "推論であることを明示",
            "max_changed_lines": 8,
            "changed_lines": changed_lines,
            "status": "applied",
        }],
    }, ensure_ascii=False), encoding="utf-8")


class Phase2EndToEndTest(unittest.TestCase):
    def test_run_with_reviews_and_patches_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            add_phase2_artifacts(run_dir)
            report = research_lint.run_lints(run_dir)
            failed = [f for f in report["findings"] if f["result"] == "fail"]
            self.assertEqual([], failed, failed)
            lints = {f["lint"] for f in report["findings"] if f["result"] == "pass"}
            self.assertIn("claim-provenance", lints)
            self.assertIn("patch-scope", lints)
            self.assertIn("critical-findings", lints)

    def test_phase1_run_skips_phase2_lints(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            report = research_lint.run_lints(build_run(Path(temp)))
            skipped = {f["lint"] for f in report["findings"] if f["result"] == "skipped"}
            self.assertEqual("pass", report["verdict"])
            self.assertIn("claim-provenance", skipped)
            self.assertIn("patch-scope", skipped)
            self.assertIn("critical-findings", skipped)


class Phase2LintFailureTest(unittest.TestCase):
    def test_unresolved_critical_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            add_phase2_artifacts(run_dir, status="open")
            self.assertIn("critical-findings", self._failed(run_dir))

    def test_critical_accepted_without_reason_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            add_phase2_artifacts(run_dir, status="accepted")
            self.assertIn("critical-findings", self._failed(run_dir))

    def test_open_minor_finding_does_not_block(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            add_phase2_artifacts(run_dir, severity="minor", status="open")
            report = research_lint.run_lints(run_dir)
            self.assertEqual("pass", report["verdict"])

    def test_patch_exceeding_its_limit_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            add_phase2_artifacts(run_dir, changed_lines=40)  # declared max is 8
            self.assertIn("patch-scope", self._failed(run_dir))

    def test_per_patch_limit_blocks_even_when_the_ratio_is_fine(self) -> None:
        """The per-patch ceiling must stand on its own, not ride on the ratio check."""
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            add_phase2_artifacts(run_dir)
            draft = run_dir / "drafts" / "draft-01.md"
            draft.write_text(draft.read_text(encoding="utf-8") + "\n".join(
                f"補足 {n} 行目。" for n in range(200)), encoding="utf-8")
            path = run_dir / "patches" / "applied-patches.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            # 12 lines against a ~200-line draft is 6% — under the ratio ceiling —
            # but still over this patch's own declared maximum of 8.
            data["patches"][0]["changed_lines"] = 12
            data["patches"][0]["max_changed_lines"] = 8
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            failed = self._failed(run_dir)
            self.assertIn("patch-scope", failed)
            report = research_lint.run_lints(run_dir)
            details = [f["detail"] for f in report["findings"]
                       if f["lint"] == "patch-scope" and f["result"] == "fail"]
            self.assertTrue(any("上限 8 行" in d for d in details), details)
            self.assertFalse(any("変更総量" in d for d in details), details)

    def test_total_change_ratio_over_the_limit_blocks(self) -> None:
        """Many individually-small patches still add up to a rewrite."""
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            add_phase2_artifacts(run_dir)
            path = run_dir / "patches" / "applied-patches.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            template = data["patches"][0]
            data["patches"] = [
                {**template, "patch_id": f"P-{i:03d}", "changed_lines": 8, "status": "applied"}
                for i in range(1, 8)
            ]
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            failed = self._failed(run_dir)
            self.assertIn("patch-scope", failed)

    def test_patch_targeting_a_missing_file_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            add_phase2_artifacts(run_dir)
            path = run_dir / "patches" / "applied-patches.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["patches"][0]["target_file"] = "drafts/draft-99.md"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertIn("patch-scope", self._failed(run_dir))

    def test_applied_patch_without_changed_lines_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            add_phase2_artifacts(run_dir)
            path = run_dir / "patches" / "applied-patches.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            del data["patches"][0]["changed_lines"]
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertIn("patch-scope", self._failed(run_dir))

    def test_claim_without_support_or_inference_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            add_phase2_artifacts(run_dir)
            path = run_dir / "claims.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["claims"][0]["supports"] = []  # still typed author-claim
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertIn("claim-provenance", self._failed(run_dir))

    def test_claim_support_without_location_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            add_phase2_artifacts(run_dir)
            path = run_dir / "claims.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["claims"][0]["supports"][0]["location"] = ""
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertIn("claim-provenance", self._failed(run_dir))

    def test_claim_citing_unknown_source_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            add_phase2_artifacts(run_dir)
            path = run_dir / "claims.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["claims"][0]["supports"][0]["source_id"] = "src-999"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertIn("claim-provenance", self._failed(run_dir))

    def test_review_schema_violation_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run_dir = build_run(Path(temp))
            add_phase2_artifacts(run_dir)
            path = run_dir / "reviews" / "evidence-review.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["findings"][0]["severity"] = "blocker"  # not in the enum
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertIn("schema-valid", self._failed(run_dir))

    def _failed(self, run_dir: Path) -> set[str]:
        report = research_lint.run_lints(run_dir)
        self.assertEqual("block", report["verdict"])
        return {f["lint"] for f in report["findings"] if f["result"] == "fail"}


class PluginLayoutTest(unittest.TestCase):
    """The design maps skills/rules/schemas onto the plugin layout; keep them in sync."""

    IMPLEMENTED_SKILLS = (
        # Phase 1
        "research-router", "query-decompose", "source-collect",
        "draft-compose", "citation-verify", "ship-verify",
        # Phase 2
        "evidence-organize", "multi-review", "patch-apply",
    )
    REQUIRED_SECTIONS = (
        "# Purpose", "# Inputs", "# Outputs", "# Preconditions", "# Allowed Tools",
        "# Prohibited Actions", "# Procedure", "# Validation", "# Exit Criteria",
        "# Failure Handling", "# Next Skill",
    )

    def test_every_implemented_skill_has_the_common_structure(self) -> None:
        for skill in self.IMPLEMENTED_SKILLS:
            path = PLUGIN_ROOT / "skills" / skill / "SKILL.md"
            with self.subTest(skill=skill):
                self.assertTrue(path.is_file(), f"{path} が無い")
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"), "frontmatter が無い")
                self.assertIn(f"name: {skill}", text)
                for section in self.REQUIRED_SECTIONS:
                    self.assertIn(section, text, f"{skill}: {section} が無い")

    def test_rules_are_bundled(self) -> None:
        for rule in ("canonical-query", "evidence-provenance", "source-independence",
                     "patch-only", "human-intervention", "sensitive-data"):
            with self.subTest(rule=rule):
                self.assertTrue((PLUGIN_ROOT / "docs" / f"{rule}.md").is_file())

    def test_schemas_referenced_by_the_linter_are_bundled(self) -> None:
        for _, schema_name, _ in research_lint.SCHEMA_TARGETS:
            with self.subTest(schema=schema_name):
                self.assertTrue((PLUGIN_ROOT / "schemas" / schema_name).is_file())


if __name__ == "__main__":
    unittest.main()
