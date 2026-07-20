#!/usr/bin/env python3
"""Pull common skills (and their companions) from this master repository into a project.

Typical use — from the root of a new research repository:

    python3 <skill-repository>/scripts/install_skills.py --bundle research --into .

This copies the bundle's skills into ``.claude/skills/`` and the shared companions
(conventions, sub-agents) into ``.claude/docs/`` and ``.claude/agents/``. Existing
files are left untouched unless ``--force`` is given, so repository-specific edits
are never clobbered.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


class InstallError(RuntimeError):
    """Raised when an install cannot be completed as requested."""


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_bundle(bundles_dir: Path, name: str) -> dict:
    path = bundles_dir / f"{name}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        available = ", ".join(sorted(p.stem for p in bundles_dir.glob("*.json"))) or "(none)"
        raise InstallError(f"unknown bundle: {name}. available: {available}") from exc
    except json.JSONDecodeError as exc:
        raise InstallError(f"bundle {name} is not valid JSON: {exc}") from exc


def available_skills(common_dir: Path) -> list[str]:
    skills_dir = common_dir / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(p.name for p in skills_dir.iterdir() if (p / "SKILL.md").is_file())


def resolve_selection(
    args: argparse.Namespace,
    common_dir: Path,
    bundles_dir: Path,
) -> tuple[list[str], dict[str, list[str]]]:
    """Return (skills, companions) to install based on CLI selection."""
    companions: dict[str, list[str]] = {"docs": [], "agents": []}
    skills: list[str] = []

    if args.bundle:
        bundle = load_bundle(bundles_dir, args.bundle)
        skills.extend(bundle.get("skills", []))
        bundle_companions = bundle.get("companions", {})
        companions["docs"] = list(bundle_companions.get("docs", []))
        companions["agents"] = list(bundle_companions.get("agents", []))

    for skill in args.skill:
        if skill not in skills:
            skills.append(skill)

    if not skills:
        raise InstallError("nothing selected: pass --bundle NAME and/or --skill NAME")

    known = set(available_skills(common_dir))
    missing = [s for s in skills if s not in known]
    if missing:
        raise InstallError(f"skill(s) not in common/: {', '.join(missing)}")

    # For a la carte --skill installs, only pull companions when asked.
    if not args.bundle and args.with_companions:
        companions["docs"] = sorted(p.name for p in (common_dir / "docs").glob("*.md"))
        companions["agents"] = sorted(p.name for p in (common_dir / "agents").glob("*.md"))

    return skills, companions


def _copy_file(src: Path, dest: Path, dry_run: bool, force: bool, results: dict) -> None:
    if not src.is_file():
        results["missing"].append(str(src))
        return
    if dest.exists() and not force:
        results["skipped"].append(str(dest))
        return
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    results["copied"].append(str(dest))


def install(
    common_dir: Path,
    skills: list[str],
    companions: dict[str, list[str]],
    target: Path,
    dry_run: bool,
    force: bool,
) -> dict:
    results: dict[str, list[str]] = {"copied": [], "skipped": [], "missing": []}
    claude = target / ".claude"

    for skill in skills:
        src_dir = common_dir / "skills" / skill
        for src in sorted(src_dir.rglob("*")):
            if src.is_file():
                rel = src.relative_to(src_dir)
                _copy_file(src, claude / "skills" / skill / rel, dry_run, force, results)

    for name in companions.get("docs", []):
        _copy_file(common_dir / "docs" / name, claude / "docs" / name, dry_run, force, results)
    for name in companions.get("agents", []):
        _copy_file(common_dir / "agents" / name, claude / "agents" / name, dry_run, force, results)

    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--into", type=Path, default=Path("."), help="Target repository root (default: current dir)")
    parser.add_argument("--bundle", help="Install a named bundle (see bundles/)")
    parser.add_argument("--skill", action="append", default=[], help="Install a single common skill (repeatable)")
    parser.add_argument("--with-companions", action="store_true", help="Also install common docs/agents for --skill selections")
    parser.add_argument("--list", action="store_true", help="List available bundles and common skills, then exit")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be copied without writing")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files (default: skip them)")
    parser.add_argument("--common-dir", type=Path, default=repo_root() / "common")
    parser.add_argument("--bundles-dir", type=Path, default=repo_root() / "bundles")
    return parser


def do_list(common_dir: Path, bundles_dir: Path) -> None:
    print("Bundles:")
    for path in sorted(bundles_dir.glob("*.json")):
        try:
            bundle = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        print(f"  {path.stem:12} {bundle.get('title', '')} ({len(bundle.get('skills', []))} skills)")
    print("\nCommon skills:")
    for skill in available_skills(common_dir):
        print(f"  {skill}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.list:
            do_list(args.common_dir, args.bundles_dir)
            return 0

        skills, companions = resolve_selection(args, args.common_dir, args.bundles_dir)
        results = install(args.common_dir, skills, companions, args.into, args.dry_run, args.force)

        verb = "Would copy" if args.dry_run else "Copied"
        print(f"{verb} {len(results['copied'])} file(s) into {args.into}/.claude")
        for path in results["copied"]:
            print(f"  + {path}")
        if results["skipped"]:
            print(f"Skipped {len(results['skipped'])} existing file(s) (use --force to overwrite):")
            for path in results["skipped"]:
                print(f"  = {path}")
        if results["missing"]:
            print(f"warning: {len(results['missing'])} source file(s) missing:", file=sys.stderr)
            for path in results["missing"]:
                print(f"  ! {path}", file=sys.stderr)

        if args.bundle:
            bundle = load_bundle(args.bundles_dir, args.bundle)
            note = bundle.get("after_install")
            if note:
                print(f"\n次のステップ: {note}")
        return 0
    except InstallError as exc:
        print(f"install failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
