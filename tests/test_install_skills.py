from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.install_skills import InstallError, available_skills, install, main, resolve_selection


class Args:
    """Minimal stand-in for argparse.Namespace in resolve_selection tests."""

    def __init__(self, bundle=None, skill=None, with_companions=False):
        self.bundle = bundle
        self.skill = skill or []
        self.with_companions = with_companions


def make_master(root: Path) -> tuple[Path, Path]:
    """Create a minimal common/ + bundles/ layout and return their paths."""
    common = root / "common"
    bundles = root / "bundles"
    for skill in ("report-review", "experiment-plan"):
        d = common / "skills" / skill
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"# {skill}\n", encoding="utf-8")
    (common / "docs").mkdir(parents=True)
    (common / "docs" / "documentation-conventions.md").write_text("# conventions\n", encoding="utf-8")
    (common / "agents").mkdir(parents=True)
    (common / "agents" / "planner.md").write_text("# planner\n", encoding="utf-8")
    bundles.mkdir(parents=True)
    (bundles / "research.json").write_text(
        json.dumps(
            {
                "name": "research",
                "title": "研究",
                "skills": ["report-review", "experiment-plan"],
                "companions": {"docs": ["documentation-conventions.md"], "agents": ["planner.md"]},
            }
        ),
        encoding="utf-8",
    )
    return common, bundles


class InstallSkillsTest(unittest.TestCase):
    def test_available_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            common, _ = make_master(Path(temp))
            self.assertEqual(["experiment-plan", "report-review"], available_skills(common))

    def test_bundle_installs_skills_and_companions(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            common, bundles = make_master(root)
            target = root / "target"
            skills, companions = resolve_selection(Args(bundle="research"), common, bundles)
            results = install(common, skills, companions, target, dry_run=False, force=False)
            self.assertTrue((target / ".claude/skills/report-review/SKILL.md").is_file())
            self.assertTrue((target / ".claude/docs/documentation-conventions.md").is_file())
            self.assertTrue((target / ".claude/agents/planner.md").is_file())
            self.assertEqual(4, len(results["copied"]))

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            common, bundles = make_master(root)
            target = root / "target"
            skills, companions = resolve_selection(Args(bundle="research"), common, bundles)
            results = install(common, skills, companions, target, dry_run=True, force=False)
            self.assertFalse((target / ".claude").exists())
            self.assertEqual(4, len(results["copied"]))

    def test_existing_files_are_skipped_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            common, bundles = make_master(root)
            target = root / "target"
            skills, companions = resolve_selection(Args(bundle="research"), common, bundles)
            install(common, skills, companions, target, dry_run=False, force=False)
            edited = target / ".claude/skills/report-review/SKILL.md"
            edited.write_text("LOCAL EDIT\n", encoding="utf-8")
            results = install(common, skills, companions, target, dry_run=False, force=False)
            self.assertEqual("LOCAL EDIT\n", edited.read_text(encoding="utf-8"))
            self.assertIn(str(edited), results["skipped"])
            forced = install(common, skills, companions, target, dry_run=False, force=True)
            self.assertEqual("# report-review\n", edited.read_text(encoding="utf-8"))
            self.assertIn(str(edited), forced["copied"])

    def test_a_la_carte_skill_without_companions(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            common, bundles = make_master(root)
            skills, companions = resolve_selection(Args(skill=["report-review"]), common, bundles)
            self.assertEqual(["report-review"], skills)
            self.assertEqual({"docs": [], "agents": []}, companions)

    def test_with_companions_flag_pulls_shared_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            common, bundles = make_master(root)
            _, companions = resolve_selection(Args(skill=["report-review"], with_companions=True), common, bundles)
            self.assertEqual(["documentation-conventions.md"], companions["docs"])
            self.assertEqual(["planner.md"], companions["agents"])

    def test_unknown_bundle_and_skill_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            common, bundles = make_master(root)
            with self.assertRaisesRegex(InstallError, "unknown bundle"):
                resolve_selection(Args(bundle="nope"), common, bundles)
            with self.assertRaisesRegex(InstallError, "not in common"):
                resolve_selection(Args(skill=["ghost"]), common, bundles)

    def test_main_nothing_selected_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            common, bundles = make_master(root)
            code = main(["--common-dir", str(common), "--bundles-dir", str(bundles), "--into", str(root / "t")])
            self.assertEqual(1, code)


if __name__ == "__main__":
    unittest.main()
