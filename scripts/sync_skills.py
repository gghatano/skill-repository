#!/usr/bin/env python3
"""Synchronize Claude skills from repositories owned by a GitHub account."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Protocol


SKILL_PATH_RE = re.compile(r"(?:^|/)\.claude/skills/(?P<skill>.+)/SKILL\.md$")


class SyncError(RuntimeError):
    """Raised when a complete, trustworthy synchronization is not possible."""


class GitHubClient(Protocol):
    def list_repositories(self, owner: str) -> list[dict[str, Any]]: ...

    def get_tree(self, full_name: str, branch: str) -> dict[str, Any]: ...

    def get_blob(self, full_name: str, sha: str) -> bytes: ...


class GhClient:
    """Small adapter around GitHub CLI so local and Actions auth behave alike."""

    def _run(self, *args: str) -> Any:
        try:
            result = subprocess.run(
                ["gh", *args],
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except FileNotFoundError as exc:
            raise SyncError("GitHub CLI (gh) is not installed") from exc
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.strip() or exc.stdout.strip() or "unknown gh error"
            raise SyncError(detail) from exc
        except subprocess.TimeoutExpired as exc:
            raise SyncError(f"gh command timed out: {' '.join(args)}") from exc

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise SyncError(f"gh returned invalid JSON: {exc}") from exc

    def list_repositories(self, owner: str) -> list[dict[str, Any]]:
        data = self._run(
            "repo",
            "list",
            owner,
            "--limit",
            "1000",
            "--json",
            "name,nameWithOwner,defaultBranchRef,isArchived,isFork,url,updatedAt",
        )
        if not isinstance(data, list):
            raise SyncError("gh repo list returned an unexpected response")
        return data

    def get_tree(self, full_name: str, branch: str) -> dict[str, Any]:
        encoded_branch = urllib.parse.quote(branch, safe="")
        data = self._run(
            "api",
            f"repos/{full_name}/git/trees/{encoded_branch}?recursive=1",
        )
        if not isinstance(data, dict):
            raise SyncError(f"unexpected tree response for {full_name}")
        return data

    def get_blob(self, full_name: str, sha: str) -> bytes:
        data = self._run("api", f"repos/{full_name}/git/blobs/{sha}")
        if data.get("encoding") != "base64" or "content" not in data:
            raise SyncError(f"unsupported blob response for {full_name}@{sha}")
        try:
            return base64.b64decode(data["content"], validate=False)
        except (ValueError, TypeError) as exc:
            raise SyncError(f"invalid base64 blob for {full_name}@{sha}") from exc


@dataclass(frozen=True)
class SkillSource:
    repository: str
    repository_url: str
    branch: str
    source_root: str
    destination: str
    skill_md_sha: str
    files: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class CatalogEntry:
    repository: str
    name: str
    description: str
    source_path: str
    source_url: str
    skill_md_sha: str
    destination: str
    files: tuple[dict[str, str], ...]
    components: tuple[str, ...]
    tools: tuple[str, ...]
    project_paths: tuple[str, ...]


TOOL_PATTERNS = {
    "Claude Code": r"\bclaude\b",
    "Docker": r"\bdocker\b",
    "Git": r"\bgit\b",
    "GitHub CLI": r"\bgh\b",
    "Make": r"\bmake\b",
    "Node.js": r"\bnode(?:\.js)?\b",
    "npm": r"\bnpm\b",
    "Python": r"\bpython(?:3)?\b",
    "uv": r"\buv\b",
}
PROJECT_PATH_RE = re.compile(
    r"^[A-Za-z0-9_.$~-]+(?:/[A-Za-z0-9_.$*{}<>\[\]-]+)+/?$"
)


def discover_skills(
    client: GitHubClient,
    owner: str,
    repository_filter: set[str] | None = None,
) -> list[SkillSource]:
    sources: list[SkillSource] = []
    repositories = client.list_repositories(owner)

    for repo in sorted(repositories, key=lambda item: item["nameWithOwner"].lower()):
        full_name = repo["nameWithOwner"]
        if repository_filter and full_name not in repository_filter and repo["name"] not in repository_filter:
            continue
        if repo.get("isArchived"):
            continue

        branch_ref = repo.get("defaultBranchRef") or {}
        branch = branch_ref.get("name")
        if not branch:
            continue

        tree_data = client.get_tree(full_name, branch)
        if tree_data.get("truncated"):
            raise SyncError(f"Git tree is truncated for {full_name}; refusing a partial sync")
        tree = tree_data.get("tree")
        if not isinstance(tree, list):
            raise SyncError(f"Git tree is missing for {full_name}")

        blobs = [item for item in tree if item.get("type") == "blob" and item.get("path")]
        destinations: set[str] = set()
        for item in blobs:
            match = SKILL_PATH_RE.search(item["path"])
            if not match:
                continue

            source_root = str(PurePosixPath(item["path"]).parent)
            skill_relative = match.group("skill")
            destination = str(PurePosixPath(repo["name"]) / skill_relative)
            if destination in destinations:
                raise SyncError(f"destination collision in {full_name}: {destination}")
            destinations.add(destination)

            prefix = source_root + "/"
            skill_files = tuple(
                sorted(
                    (blob for blob in blobs if blob["path"].startswith(prefix)),
                    key=lambda blob: blob["path"],
                )
            )
            sources.append(
                SkillSource(
                    repository=full_name,
                    repository_url=repo["url"],
                    branch=branch,
                    source_root=source_root,
                    destination=destination,
                    skill_md_sha=item["sha"],
                    files=skill_files,
                )
            )

    if repository_filter:
        known = {
            repo["nameWithOwner"] for repo in repositories
        } | {repo["name"] for repo in repositories}
        missing = repository_filter - known
        if missing:
            raise SyncError(f"repository not found: {', '.join(sorted(missing))}")

    return sorted(sources, key=lambda source: (source.repository.lower(), source.destination.lower()))


def parse_frontmatter(content: str) -> dict[str, str]:
    lines = content.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return {}

    result: dict[str, str] = {}
    index = 1
    while index < end:
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", lines[index])
        if not match:
            index += 1
            continue
        key, value = match.groups()
        if value in {"|", "|-", "|+", ">", ">-", ">+"}:
            block: list[str] = []
            index += 1
            while index < end and (not lines[index].strip() or lines[index][0].isspace()):
                block.append(lines[index].strip())
                index += 1
            value = " ".join(part for part in block if part)
            result[key] = value.strip()
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        result[key] = value.strip()
        index += 1
    return result


def fallback_description(content: str) -> str:
    lines = content.lstrip("\ufeff").splitlines()
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                lines = lines[index + 1 :]
                break
    paragraph: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("```"):
            if paragraph:
                break
            continue
        if not stripped:
            if paragraph:
                break
            continue
        paragraph.append(stripped)
    summary = " ".join(paragraph)
    return summary[:237] + "..." if len(summary) > 240 else summary


def detect_tools(content: str) -> tuple[str, ...]:
    return tuple(
        name
        for name, pattern in TOOL_PATTERNS.items()
        if re.search(pattern, content, flags=re.IGNORECASE)
    )


def detect_project_paths(content: str, limit: int = 8) -> tuple[str, ...]:
    paths: list[str] = []
    for candidate in re.findall(r"`([^`\n]{1,120})`", content):
        value = candidate.strip()
        if PROJECT_PATH_RE.fullmatch(value) and value not in paths:
            paths.append(value)
        if len(paths) >= limit:
            break
    return tuple(paths)


def stage_skills(
    client: GitHubClient,
    sources: Iterable[SkillSource],
    stage_directory: Path,
) -> list[CatalogEntry]:
    entries: list[CatalogEntry] = []
    for source in sources:
        skill_content: bytes | None = None
        copied_files: list[dict[str, str]] = []
        for file_info in source.files:
            relative = PurePosixPath(file_info["path"]).relative_to(source.source_root)
            destination = stage_directory / source.destination / Path(*relative.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            blob = client.get_blob(source.repository, file_info["sha"])
            destination.write_bytes(blob)
            if file_info.get("mode") == "100755":
                destination.chmod(destination.stat().st_mode | 0o111)
            copied_files.append(
                {
                    "path": str(relative),
                    "sha": file_info["sha"],
                    "mode": file_info.get("mode", "100644"),
                }
            )
            if relative == PurePosixPath("SKILL.md"):
                skill_content = blob

        if skill_content is None:
            raise SyncError(f"SKILL.md was not fetched for {source.repository}:{source.source_root}")
        text = skill_content.decode("utf-8", errors="replace")
        metadata = parse_frontmatter(text)
        default_name = PurePosixPath(source.source_root).name
        name = metadata.get("name") or default_name
        description = metadata.get("description") or fallback_description(text) or "説明なし"
        components = sorted(
            {
                PurePosixPath(file["path"]).parts[0]
                for file in copied_files
                if len(PurePosixPath(file["path"]).parts) > 1
            }
        )
        encoded_path = urllib.parse.quote(f"{source.source_root}/SKILL.md", safe="/")
        entries.append(
            CatalogEntry(
                repository=source.repository,
                name=name,
                description=" ".join(description.split()),
                source_path=f"{source.source_root}/SKILL.md",
                source_url=f"{source.repository_url}/blob/{urllib.parse.quote(source.branch, safe='')}/{encoded_path}",
                skill_md_sha=source.skill_md_sha,
                destination=source.destination,
                files=tuple(copied_files),
                components=tuple(components),
                tools=detect_tools(text),
                project_paths=detect_project_paths(text),
            )
        )
    return sorted(entries, key=lambda entry: (entry.repository.lower(), entry.name.lower()))


def render_catalog(owner: str, entries: list[CatalogEntry]) -> str:
    lines = [
        "# Skill Catalog",
        "",
        f"GitHub account `{owner}` のリポジトリから自動生成した Claude Skills の一覧です。",
        "このファイルは直接編集せず、`python3 scripts/sync_skills.py` で更新してください。",
        "",
        f"スキル数: **{len(entries)}**",
        "",
        "| Repository | Skill | Description | Source |",
        "| --- | --- | --- | --- |",
    ]
    for entry in entries:
        description = entry.description.replace("|", "\\|").replace("\n", " ")
        name = entry.name.replace("|", "\\|")
        repo_name = entry.repository.split("/", 1)[-1]
        lines.append(
            f"| `{repo_name}` | `{name}` | {description} | [SKILL.md]({entry.source_url}) |"
        )
    lines.append("")
    return "\n".join(lines)


def render_manifest(owner: str, entries: list[CatalogEntry]) -> str:
    payload = {
        "schema_version": 1,
        "owner": owner,
        "skills": [
            {
                "repository": entry.repository,
                "name": entry.name,
                "description": entry.description,
                "source_path": entry.source_path,
                "source_url": entry.source_url,
                "skill_md_sha": entry.skill_md_sha,
                "destination": entry.destination,
                "files": list(entry.files),
                "components": list(entry.components),
                "tools": list(entry.tools),
                "project_paths": list(entry.project_paths),
                "portability_review": "required" if entry.project_paths else "candidate",
            }
            for entry in entries
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_html(owner: str, entries: list[CatalogEntry], template: str) -> str:
    if "__CATALOG_DATA__" not in template:
        raise SyncError("HTML template is missing __CATALOG_DATA__")
    payload = {
        "owner": owner,
        "skills": [
            {
                "repository": entry.repository,
                "name": entry.name,
                "description": entry.description,
                "sourcePath": entry.source_path,
                "sourceUrl": entry.source_url,
                "destination": entry.destination,
                "files": list(entry.files),
                "components": list(entry.components),
                "tools": list(entry.tools),
                "projectPaths": list(entry.project_paths),
                "portabilityReview": "required" if entry.project_paths else "candidate",
            }
            for entry in entries
        ],
    }
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return template.replace("__CATALOG_DATA__", data)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def replace_directory(staged: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup = destination.with_name(destination.name + ".previous")
    if backup.exists():
        shutil.rmtree(backup)
    if destination.exists():
        os.replace(destination, backup)
    try:
        os.replace(staged, destination)
    except Exception:
        if backup.exists() and not destination.exists():
            os.replace(backup, destination)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default="gghatano", help="GitHub account to scan")
    parser.add_argument(
        "--repo",
        action="append",
        default=[],
        help="Limit the scan to a repository name or owner/name (repeatable)",
    )
    parser.add_argument("--output", type=Path, default=Path("skills"))
    parser.add_argument("--catalog", type=Path, default=Path("docs/skill-catalog.md"))
    parser.add_argument("--manifest", type=Path, default=Path("catalog/manifest.json"))
    parser.add_argument("--html", type=Path, default=Path("docs/index.html"))
    parser.add_argument("--html-template", type=Path, default=Path("web/index.template.html"))
    parser.add_argument("--dry-run", action="store_true", help="Discover skills without fetching files")
    return parser


def main(argv: list[str] | None = None, client: GitHubClient | None = None) -> int:
    args = build_parser().parse_args(argv)
    github = client or GhClient()
    try:
        sources = discover_skills(github, args.owner, set(args.repo) or None)
        print(f"Discovered {len(sources)} skill(s) in {len({s.repository for s in sources})} repository/repositories")
        for source in sources:
            print(f"- {source.repository}:{source.source_root}")
        if args.dry_run:
            return 0

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="skill-sync-", dir=args.output.parent) as temp:
            staged = Path(temp) / args.output.name
            staged.mkdir()
            entries = stage_skills(github, sources, staged)
            catalog_content = render_catalog(args.owner, entries)
            manifest_content = render_manifest(args.owner, entries)
            try:
                html_template = args.html_template.read_text(encoding="utf-8")
            except OSError as exc:
                raise SyncError(f"cannot read HTML template: {args.html_template}") from exc
            html_content = render_html(args.owner, entries, html_template)
            replace_directory(staged, args.output)
        atomic_write(args.catalog, catalog_content)
        atomic_write(args.manifest, manifest_content)
        atomic_write(args.html, html_content)
        print(f"Updated {args.output}, {args.catalog}, {args.manifest}, and {args.html}")
        return 0
    except SyncError as exc:
        print(f"sync failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
