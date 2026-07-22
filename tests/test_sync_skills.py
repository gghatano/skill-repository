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
    load_plugin_details,
    parse_frontmatter,
    render_catalog,
    render_html,
    render_skill_detail_pages,
    render_plugin_detail_pages,
    extract_readme_section,
    render_duplication_report,
    render_manifest,
    render_porting_guide,
    render_purpose_catalog,
    stage_skills,
)
from scripts.sync_skills import CatalogEntry


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

        marketplace = {"name": "gghatano-skills", "add": "/plugin marketplace add gghatano/skill-repository"}
        plugins = [{"name": "research", "displayName": "研究", "description": "", "skills": [{"name": "report-review", "description": "レビュー"}], "agents": [], "docs": [], "install": "/plugin install research@gghatano-skills"}]
        html = render_html("gghatano", "<script>__CATALOG_DATA__</script>", marketplace, plugins)
        self.assertIn('"name":"report-review"', html)
        self.assertIn('"marketplace":', html)
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


class DuplicationTest(unittest.TestCase):
    def _entry(self, repo: str, name: str, sha: str) -> CatalogEntry:
        return CatalogEntry(
            repository=f"gghatano/{repo}",
            name=name,
            description="d",
            source_path="p",
            source_url="u",
            skill_md_sha=sha,
            destination=f"{repo}/{name}",
            files=(),
            components=(),
            tools=(),
            project_paths=(),
        )

    def test_reports_only_cross_repo_duplicates(self) -> None:
        entries = [
            self._entry("a", "shared", "sha1"),
            self._entry("b", "shared", "sha1"),  # identical → 1 version
            self._entry("c", "drift", "shaX"),
            self._entry("d", "drift", "shaY"),  # divergent → 2 versions ⚠
            self._entry("a", "solo", "shaZ"),  # single repo → excluded
        ]
        report = render_duplication_report("gghatano", entries)
        self.assertIn("複数リポジトリに重複する名前: **2**", report)
        self.assertIn("`shared`", report)
        self.assertIn("`drift`", report)
        self.assertNotIn("`solo`", report)
        # identical content shows no warning flag; divergent one does.
        shared_line = next(l for l in report.splitlines() if "`shared`" in l)
        drift_line = next(l for l in report.splitlines() if "`drift`" in l)
        self.assertNotIn("⚠", shared_line)
        self.assertIn("⚠", drift_line)


class PluginHtmlTest(unittest.TestCase):
    def test_load_plugins(self) -> None:
        from scripts.sync_skills import load_plugins

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill_dir = root / "plugins/research/skills/report-review"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: report-review\ndescription: レビューする\n---\n本文",
                encoding="utf-8",
            )
            (root / "plugins/research/docs").mkdir(parents=True)
            (root / "plugins/research/docs/documentation-conventions.md").write_text("x", encoding="utf-8")
            (root / "plugins/research/agents").mkdir(parents=True)
            (root / "plugins/research/agents/planner.md").write_text("x", encoding="utf-8")
            (root / "plugins/research/.claude-plugin").mkdir(parents=True)
            (root / "plugins/research/.claude-plugin/plugin.json").write_text(
                json.dumps({"name": "research", "displayName": "研究", "description": "説明"}),
                encoding="utf-8",
            )
            (root / ".claude-plugin").mkdir()
            (root / ".claude-plugin/marketplace.json").write_text(
                json.dumps({"name": "gghatano-skills"}), encoding="utf-8"
            )

            marketplace, plugins = load_plugins(
                root / "plugins", root / ".claude-plugin/marketplace.json", "gghatano/skill-repository"
            )
            self.assertEqual("gghatano-skills", marketplace["name"])
            self.assertIn("gghatano/skill-repository", marketplace["add"])
            self.assertEqual(1, len(plugins))
            self.assertEqual("research", plugins[0]["name"])
            self.assertEqual("研究", plugins[0]["displayName"])
            self.assertEqual([{"name": "report-review", "description": "レビューする"}], plugins[0]["skills"])
            self.assertEqual(["planner.md"], plugins[0]["agents"])
            self.assertEqual(["documentation-conventions.md"], plugins[0]["docs"])
            self.assertEqual("/plugin install research@gghatano-skills", plugins[0]["install"])

    def test_html_embeds_plugins(self) -> None:
        marketplace = {"name": "gghatano-skills", "add": "/plugin marketplace add gghatano/skill-repository"}
        plugins = [
            {
                "name": "research",
                "displayName": "研究",
                "description": "",
                "skills": [{"name": "report-review", "description": "レビュー"}],
                "agents": ["planner.md"],
                "docs": ["documentation-conventions.md"],
                "install": "/plugin install research@gghatano-skills",
            }
        ]
        html = render_html("gghatano", "<script>__CATALOG_DATA__</script>", marketplace, plugins)
        self.assertIn('"plugins":[', html)
        self.assertIn('"name":"report-review"', html)
        self.assertIn('/plugin install research@gghatano-skills', html)

    def test_render_skill_detail_pages(self) -> None:
        marketplace = {"name": "gghatano-skills", "add": "/plugin marketplace add gghatano/skill-repository"}
        plugins = [
            {
                "name": "research",
                "displayName": "研究",
                "description": "",
                "skills": [{"name": "report-review", "description": "レビューする"}],
                "agents": [],
                "docs": [],
                "install": "/plugin install research@gghatano-skills",
            }
        ]
        details = {"report-review": {"tagline": "実験レポートを点検", "canDo": ["点検する"], "whenToUse": "公開前", "io": "入力/出力"}}
        template = (
            "{{SKILL_NAME}}|{{PLUGIN_NAME}}|{{PLUGIN_TITLE}}|{{TAGLINE}}|{{DESCRIPTION}}"
            "|{{CANDO_ITEMS}}|{{WHENTOUSE}}|{{IO}}|{{INVOKE}}|{{INSTALL}}|{{SOURCE_URL}}"
        )
        pages = render_skill_detail_pages(template, plugins, details, marketplace, "gghatano/skill-repository")
        self.assertEqual(["skills/report-review.html"], list(pages))
        page = pages["skills/report-review.html"]
        self.assertIn("report-review", page)
        self.assertIn("実験レポートを点検", page)
        self.assertIn("点検する", page)
        self.assertIn("/research:report-review", page)
        self.assertIn("gghatano/skill-repository/blob/main/plugins/research/skills/report-review/SKILL.md", page)
        # No leftover placeholders.
        self.assertNotIn("{{", page)

    def test_load_plugin_details(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "plugin-details.json"
            path.write_text(
                '{"plugins": {"dev": {"input": "i", "process": "p", "output": "o"}}}',
                encoding="utf-8",
            )
            details = load_plugin_details(path)
            self.assertEqual({"input": "i", "process": "p", "output": "o"}, details["dev"])
            # Missing file returns empty, not an error.
            self.assertEqual({}, load_plugin_details(Path(temp) / "missing.json"))

    def test_extract_readme_section(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            readme = Path(temp) / "README.md"
            readme.write_text(
                "# title\n\n## 導入\n本文\n\n## 導入後の調整\n段落A。\n\n段落B。\n\n## 含まれるスキル\nx\n",
                encoding="utf-8",
            )
            section = extract_readme_section(readme, "導入後の調整")
            self.assertEqual(["段落A。", "段落B。"], section)
            self.assertEqual([], extract_readme_section(readme, "存在しない"))

    def test_render_plugin_detail_pages(self) -> None:
        marketplace = {"name": "gghatano-skills", "add": "/plugin marketplace add gghatano/skill-repository"}
        plugins = [
            {
                "name": "research",
                "displayName": "研究",
                "description": "説明",
                "skills": [{"name": "report-review", "description": "レビュー"}],
                "agents": ["planner.md"],
                "docs": ["documentation-conventions.md"],
                "install": "/plugin install research@gghatano-skills",
            },
            {
                "name": "writing",
                "displayName": "文章",
                "description": "自己完結",
                "skills": [{"name": "stop-ai-slop-jp", "description": "AI 臭を直す"}],
                "agents": [],
                "docs": [],
                "install": "/plugin install writing@gghatano-skills",
            },
        ]
        adjust = {"research": ["`docs/x.md` を調整してください。"]}
        details = {"research": {"input": "テーマとデータ", "process": "計画して実行する", "output": "レポート一式"}}
        template = (
            'A{{PLUGIN_NAME}}|{{PLUGIN_TITLE}}|{{DESCRIPTION}}|{{SKILL_COUNT}}|{{SKILL_ITEMS}}'
            '|{{INSTALL}}|{{MARKETPLACE_ADD}}|{{FIRST_SKILL}}'
            '<section data-section="flow">F{{IO_INPUT}}|{{IO_PROCESS}}|{{IO_OUTPUT}}</section>'
            '<section data-section="companions">C{{COMPANION_ITEMS}}</section>'
            '<section data-section="adjust">D{{ADJUST_ITEMS}}</section>Z'
        )
        pages = render_plugin_detail_pages(template, plugins, adjust, details, marketplace, Path("plugins"))
        self.assertEqual({"plugins/research.html", "plugins/writing.html"}, set(pages))
        research = pages["plugins/research.html"]
        self.assertIn("../skills/report-review.html", research)
        self.assertIn("agents/planner.md", research)
        self.assertIn("<code", research)  # inline markdown rendered
        self.assertIn('data-section="flow"', research)
        self.assertIn("テーマとデータ", research)
        self.assertIn("計画して実行する", research)
        self.assertIn("レポート一式", research)
        self.assertIn('data-section="companions"', research)
        self.assertIn('data-section="adjust"', research)
        self.assertNotIn("{{", research)
        # writing has no flow/companions/adjust details: those sections are dropped.
        writing = pages["plugins/writing.html"]
        self.assertNotIn('data-section="flow"', writing)
        self.assertNotIn('data-section="companions"', writing)
        self.assertNotIn('data-section="adjust"', writing)


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
