from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.sync_skills import (
    SyncError,
    discover_skills,
    parse_frontmatter,
    render_catalog,
    render_html,
    render_manifest,
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


if __name__ == "__main__":
    unittest.main()
