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

    body = (
        "# example/repo の設計思想\n\n"
        "## 設計思想\n\n"
        "README は小さな中核を保つ方針を明示している"
        "（[example/repo README](https://github.com/example/repo)）。\n\n"
        f"> {QUOTE}\n"
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


class PluginLayoutTest(unittest.TestCase):
    """The design maps skills/rules/schemas onto the plugin layout; keep them in sync."""

    PHASE1_SKILLS = (
        "research-router", "query-decompose", "source-collect",
        "draft-compose", "citation-verify", "ship-verify",
    )
    REQUIRED_SECTIONS = (
        "# Purpose", "# Inputs", "# Outputs", "# Preconditions", "# Allowed Tools",
        "# Prohibited Actions", "# Procedure", "# Validation", "# Exit Criteria",
        "# Failure Handling", "# Next Skill",
    )

    def test_every_phase1_skill_exists_with_the_common_structure(self) -> None:
        for skill in self.PHASE1_SKILLS:
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
