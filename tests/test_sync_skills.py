from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.sync_skills import (
    SyncError,
    assign_categories,
    classify_portability,
    discover_skills,
    entries_from_manifest,
    load_categories,
    parse_frontmatter,
    render_catalog,
    render_html,
    render_manifest,
    render_porting_guide,
    render_purpose_catalog,
    stage_skills,
)


class FakeClient:
    def __init__(self) -> None:
        self.repositories = [
            {
                "name": "project-a",
                "nameWithOwner": "gghatano/project-a",
                "defaultBranchRef": {"name": "main"},
                "isArchived": False,
                "isFork": False,
                "url": "https://github.com/gghatano/project-a",
                "updatedAt": "2026-07-19T00:00:00Z",
            },
            {
                "name": "old-project",
                "nameWithOwner": "gghatano/old-project",
                "defaultBranchRef": {"name": "main"},
                "isArchived": True,
                "isFork": False,
                "url": "https://github.com/gghatano/old-project",
                "updatedAt": "2025-01-01T00:00:00Z",
            },
        ]
        self.contents = {
            "skill-sha": b"---\nname: issue-planner\ndescription: >-\n  Plan an issue before\n  implementation.\n---\n# Issue Planner\n",
            "ref-sha": b"# Reference\n",
            "script-sha": b"#!/bin/sh\nexit 0\n",
        }
        self.tree = {
            "truncated": False,
            "tree": [
                {
                    "path": ".claude/skills/issue-planner/SKILL.md",
                    "type": "blob",
                    "sha": "skill-sha",
                },
                {
                    "path": ".claude/skills/issue-planner/references/plan.md",
                    "type": "blob",
                    "sha": "ref-sha",
                },
                {
                    "path": ".claude/skills/issue-planner/scripts/check.sh",
                    "type": "blob",
                    "mode": "100755",
                    "sha": "script-sha",
                },
                {
                    "path": ".claude/commands/unrelated.md",
                    "type": "blob",
                    "sha": "other-sha",
                },
            ],
        }

    def list_repositories(self, owner: str):
        return self.repositories

    def get_tree(self, full_name: str, branch: str):
        return self.tree

    def get_blob(self, full_name: str, sha: str):
        return self.contents[sha]


class SyncSkillsTest(unittest.TestCase):
    def test_parses_folded_frontmatter(self) -> None:
        content = "---\nname: sample\ndescription: >-\n  First line\n  second line\n---\n"
        self.assertEqual(
            {"name": "sample", "description": "First line second line"},
            parse_frontmatter(content),
        )

    def test_discovers_and_stages_complete_skill_directory(self) -> None:
        client = FakeClient()
        sources = discover_skills(client, "gghatano")
        self.assertEqual(1, len(sources))
        self.assertEqual("project-a/issue-planner", sources[0].destination)

        with tempfile.TemporaryDirectory() as temp:
            entries = stage_skills(client, sources, Path(temp))
            skill = Path(temp) / "project-a/issue-planner/SKILL.md"
            reference = Path(temp) / "project-a/issue-planner/references/plan.md"
            script = Path(temp) / "project-a/issue-planner/scripts/check.sh"
            self.assertTrue(skill.is_file())
            self.assertTrue(reference.is_file())
            self.assertTrue(os.access(script, os.X_OK))

        self.assertEqual("issue-planner", entries[0].name)
        self.assertEqual("Plan an issue before implementation.", entries[0].description)
        self.assertIn("/.claude/skills/issue-planner/SKILL.md", entries[0].source_url)
        self.assertEqual(("references", "scripts"), entries[0].components)
        self.assertEqual(3, len(entries[0].files))

    def test_manifest_and_catalog_are_deterministic(self) -> None:
        client = FakeClient()
        with tempfile.TemporaryDirectory() as temp:
            entries = stage_skills(client, discover_skills(client, "gghatano"), Path(temp))
        catalog = render_catalog("gghatano", entries)
        manifest = render_manifest("gghatano", entries)
        self.assertIn("スキル数: **1**", catalog)
        self.assertNotIn("generated_at", manifest)
        self.assertEqual("issue-planner", json.loads(manifest)["skills"][0]["name"])

        html = render_html("gghatano", entries, "<script>__CATALOG_DATA__</script>")
        self.assertIn('"name":"issue-planner"', html)
        self.assertNotIn("__CATALOG_DATA__", html)

    def test_rejects_truncated_tree(self) -> None:
        client = FakeClient()
        client.tree["truncated"] = True
        with self.assertRaisesRegex(SyncError, "truncated"):
            discover_skills(client, "gghatano")

    def test_rejects_unknown_repository_filter(self) -> None:
        with self.assertRaisesRegex(SyncError, "repository not found"):
            discover_skills(FakeClient(), "gghatano", {"missing"})


class CategoryTest(unittest.TestCase):
    def _write_categories(self, temp: str, payload: dict) -> Path:
        path = Path(temp) / "categories.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def _entries(self) -> list:
        client = FakeClient()
        with tempfile.TemporaryDirectory() as temp:
            return stage_skills(client, discover_skills(client, "gghatano"), Path(temp))

    def test_load_categories_missing_file_returns_empty(self) -> None:
        self.assertEqual([], load_categories(Path("does-not-exist.json")))

    def test_load_categories_rejects_duplicate_skill_assignment(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = self._write_categories(
                temp,
                {
                    "categories": [
                        {"id": "a", "title": "A", "skills": ["x"]},
                        {"id": "b", "title": "B", "skills": ["x"]},
                    ]
                },
            )
            with self.assertRaisesRegex(SyncError, "both"):
                load_categories(path)

    def test_load_categories_rejects_duplicate_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = self._write_categories(
                temp,
                {
                    "categories": [
                        {"id": "a", "title": "A", "skills": []},
                        {"id": "a", "title": "A2", "skills": []},
                    ]
                },
            )
            with self.assertRaisesRegex(SyncError, "duplicate category id"):
                load_categories(path)

    def test_assign_categories_matches_by_skill_name(self) -> None:
        entries = self._entries()
        with tempfile.TemporaryDirectory() as temp:
            path = self._write_categories(
                temp,
                {"categories": [{"id": "planning", "title": "Planning", "skills": ["issue-planner"]}]},
            )
            categories = load_categories(path)
        assigned, uncategorized = assign_categories(entries, categories)
        self.assertEqual("planning", assigned[0].category)
        self.assertEqual([], uncategorized)

    def test_assign_categories_reports_uncategorized(self) -> None:
        entries = self._entries()
        assigned, uncategorized = assign_categories(entries, [])
        self.assertEqual("uncategorized", assigned[0].category)
        self.assertEqual(["issue-planner"], uncategorized)

    def test_render_purpose_catalog_groups_and_marks_uncategorized(self) -> None:
        entries = self._entries()
        with tempfile.TemporaryDirectory() as temp:
            path = self._write_categories(
                temp,
                {"categories": [{"id": "planning", "title": "計画", "skills": ["issue-planner"]}]},
            )
            categories = load_categories(path)
        assigned, _ = assign_categories(entries, categories)
        catalog = render_purpose_catalog("gghatano", assigned, categories)
        self.assertIn("# Skill Catalog（目的別）", catalog)
        self.assertIn("## 計画", catalog)
        self.assertIn('<a id="planning">', catalog)
        self.assertIn("`issue-planner`", catalog)
        self.assertNotIn("未分類", catalog)

    def test_render_purpose_catalog_appends_uncategorized_section(self) -> None:
        entries = self._entries()
        assigned, _ = assign_categories(entries, [])
        catalog = render_purpose_catalog("gghatano", assigned, [])
        self.assertIn("## 未分類", catalog)

    def test_manifest_includes_category(self) -> None:
        entries = self._entries()
        with tempfile.TemporaryDirectory() as temp:
            path = self._write_categories(
                temp,
                {"categories": [{"id": "planning", "title": "計画", "skills": ["issue-planner"]}]},
            )
            categories = load_categories(path)
        assigned, _ = assign_categories(entries, categories)
        manifest = json.loads(render_manifest("gghatano", assigned))
        self.assertEqual("planning", manifest["skills"][0]["category"])

    def test_from_manifest_refuses_when_taxonomy_missing(self) -> None:
        from scripts.sync_skills import main

        entries = self._entries()
        with tempfile.TemporaryDirectory() as temp:
            categories_path = self._write_categories(
                temp,
                {"categories": [{"id": "planning", "title": "計画", "skills": ["issue-planner"]}]},
            )
            assigned, _ = assign_categories(entries, load_categories(categories_path))
            manifest = Path(temp) / "manifest.json"
            manifest.write_text(render_manifest("gghatano", assigned), encoding="utf-8")
            # The manifest starts with a real category assigned.
            self.assertIn('"category": "planning"', manifest.read_text(encoding="utf-8"))

            code = main(
                [
                    "--from-manifest",
                    "--manifest",
                    str(manifest),
                    "--categories",
                    str(Path(temp) / "absent.json"),  # deliberately missing
                    "--catalog",
                    str(Path(temp) / "catalog.md"),
                    "--purpose-catalog",
                    str(Path(temp) / "purpose.md"),
                    "--html",
                    str(Path(temp) / "index.html"),
                ]
            )
            # Non-zero exit and the manifest is left untouched (category preserved).
            self.assertEqual(1, code)
            self.assertIn('"category": "planning"', manifest.read_text(encoding="utf-8"))
            self.assertNotIn("uncategorized", manifest.read_text(encoding="utf-8"))

    def test_entries_from_manifest_round_trips(self) -> None:
        entries = self._entries()
        with tempfile.TemporaryDirectory() as temp:
            manifest_path = Path(temp) / "manifest.json"
            manifest_path.write_text(render_manifest("gghatano", entries), encoding="utf-8")
            restored = entries_from_manifest(manifest_path)
        self.assertEqual(entries[0].name, restored[0].name)
        self.assertEqual(entries[0].source_url, restored[0].source_url)
        self.assertEqual(entries[0].components, restored[0].components)


class PortabilityTest(unittest.TestCase):
    def _files(self, *paths: str) -> list:
        return [{"path": p, "sha": "x", "mode": "100644"} for p in paths]

    def test_bundled_paths_do_not_trigger_rework(self) -> None:
        result = classify_portability(
            ["references/phrases.md", "references/examples.md"],
            ["references"],
            self._files("SKILL.md", "references/phrases.md"),
        )
        self.assertEqual("portable", result["tier"])
        self.assertEqual(["references/phrases.md", "references/examples.md"], result["bundled"])
        self.assertEqual([], result["external"])

    def test_parameterized_paths_are_portable(self) -> None:
        result = classify_portability(
            ["docs/report_{{NN}}.md", "issue/<n>-<slug>", "content/*.md"],
            [],
            self._files("SKILL.md"),
        )
        self.assertEqual("portable", result["tier"])
        self.assertEqual(3, len(result["parameterized"]))

    def test_harness_paths_yield_companions_tier(self) -> None:
        result = classify_portability(
            [".claude/agents/planner.md", "docs/plans/<ID>.md"],
            [],
            self._files("SKILL.md"),
        )
        self.assertEqual("companions", result["tier"])
        self.assertEqual([".claude/agents/planner.md"], result["companions"])

    def test_concrete_external_path_yields_rework(self) -> None:
        result = classify_portability(
            ["config/assets.yaml", ".claude/agents/planner.md"],
            [],
            self._files("SKILL.md"),
        )
        self.assertEqual("rework", result["tier"])
        self.assertEqual(["config/assets.yaml"], result["external"])
        self.assertEqual([".claude/agents/planner.md"], result["companions"])

    def test_manifest_carries_portability_and_bumps_schema(self) -> None:
        client = FakeClient()
        with tempfile.TemporaryDirectory() as temp:
            entries = stage_skills(client, discover_skills(client, "gghatano"), Path(temp))
        manifest = json.loads(render_manifest("gghatano", entries))
        self.assertEqual(2, manifest["schema_version"])
        skill = manifest["skills"][0]
        self.assertIn("portability", skill)
        self.assertEqual("portable", skill["portability"]["tier"])
        # Legacy field still derived for existing consumers.
        self.assertEqual("candidate", skill["portability_review"])

    def test_porting_guide_lists_tiers(self) -> None:
        client = FakeClient()
        with tempfile.TemporaryDirectory() as temp:
            entries = stage_skills(client, discover_skills(client, "gghatano"), Path(temp))
        guide = render_porting_guide("gghatano", entries)
        self.assertIn("# Skill Porting Guide", guide)
        self.assertIn("## そのまま", guide)
        self.assertIn("`issue-planner`", guide)


if __name__ == "__main__":
    unittest.main()
