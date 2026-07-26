#!/usr/bin/env python3
"""Structural checks for a Deep Research run directory.

The skills describe what to produce; this script decides whether it was actually
produced. It validates the JSON artefacts against the bundled schemas and runs
the Phase 1 lints, so a run cannot be declared shippable on prose alone.

    python3 research_lint.py research/runs/<run-id>

Exit code is 0 when nothing failed (warnings allowed) and 1 when any lint failed.
Only the standard library is used, so it runs wherever the plugin is installed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = PLUGIN_ROOT / "schemas"

# Phase 1 lints. The remaining lints in the design (claim-provenance, patch-scope,
# critical-findings, numeric-traceability, independence-count) need artefacts that
# later phases produce, so they are not registered yet.
PHASE1_LINTS = (
    "query-preserved",
    "schema-valid",
    "coverage-complete",
    "source-metadata",
    "quote-integrity",
    "internal-leak",
    "placeholder-check",
)

PLACEHOLDER_RE = re.compile(r"\bTODO\b|\bFIXME\b|\bTBD\b|\{\{[^}]*\}\}|<[A-Za-z_]+>")
INTERNAL_MARKERS = ("research/runs/", "scaffold.md", ".agents/", "coverage-matrix.md")


class LintError(RuntimeError):
    """Raised when the run directory itself cannot be inspected."""


# --------------------------------------------------------------------------- #
# Minimal JSON Schema subset validator
# --------------------------------------------------------------------------- #

def validate_schema(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Validate against the subset of JSON Schema the bundled schemas use.

    Supported: type, required, properties, items, enum, pattern, minLength,
    minItems, minimum. Unsupported keywords are ignored rather than guessed at,
    so a schema that grows beyond this subset silently loosens instead of
    failing on valid data.
    """
    errors: list[str] = []
    expected = schema.get("type")
    if expected and not _type_matches(instance, expected):
        return [f"{path}: expected {expected}, got {type(instance).__name__}"]

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} is not one of {schema['enum']}")

    if isinstance(instance, str):
        pattern = schema.get("pattern")
        if pattern and not re.search(pattern, instance):
            errors.append(f"{path}: {instance!r} does not match {pattern}")
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required property '{key}'")
        for key, subschema in schema.get("properties", {}).items():
            if key in instance:
                errors.extend(validate_schema(instance[key], subschema, f"{path}.{key}"))

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(validate_schema(item, item_schema, f"{path}[{index}]"))

    return errors


def _type_matches(instance: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(instance, dict)
    if expected == "array":
        return isinstance(instance, list)
    if expected == "string":
        return isinstance(instance, str)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if expected == "boolean":
        return isinstance(instance, bool)
    return True


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema(name: str) -> dict[str, Any]:
    try:
        return load_json(SCHEMA_DIR / name)
    except FileNotFoundError as exc:  # pragma: no cover - packaging error
        raise LintError(f"bundled schema is missing: {name}") from exc


def parse_frontmatter(text: str) -> dict[str, str]:
    """Read the leading YAML-ish frontmatter block of a Source Note."""
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}
    result: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            result[match.group(1)] = match.group(2).strip()
    return result


def extract_section(text: str, heading: str) -> str:
    """Return the body under a ``# <heading>`` section of a Source Note."""
    lines = text.splitlines()
    collecting = False
    body: list[str] = []
    for line in lines:
        if line.startswith("#"):
            if collecting:
                break
            collecting = line.lstrip("#").strip() == heading
            continue
        if collecting:
            body.append(line)
    return "\n".join(body)


def blockquote_lines(text: str) -> list[str]:
    """Verbatim quotes in a draft are written as markdown blockquotes."""
    quotes = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):
            quote = stripped.lstrip(">").strip()
            if len(quote) >= 10:
                quotes.append(quote)
    return quotes


def _result(name: str, result: str, detail: str, target: str = "") -> dict[str, str]:
    return {"lint": name, "result": result, "detail": detail, "target": target}


# --------------------------------------------------------------------------- #
# Lints
# --------------------------------------------------------------------------- #

def lint_query_preserved(run_dir: Path) -> list[dict[str, str]]:
    query = run_dir / "query.md"
    if not query.is_file():
        return [_result("query-preserved", "fail", "query.md が存在しない", str(query))]
    if not query.read_text(encoding="utf-8").strip():
        return [_result("query-preserved", "fail", "query.md が空", str(query))]
    return [_result("query-preserved", "pass", "Canonical Query が保存されている", str(query))]


SCHEMA_TARGETS = (
    ("run.json", "run.schema.json", True),
    ("execution-contract.json", "execution-contract.schema.json", True),
    ("decomposition.json", "decomposition.schema.json", False),
    ("sources.json", "source.schema.json", False),
    ("verification/citation-check.json", "verification.schema.json", False),
    ("verification/ship-check.json", "verification.schema.json", False),
)


def lint_schema_valid(run_dir: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for relative, schema_name, required in SCHEMA_TARGETS:
        path = run_dir / relative
        if not path.is_file():
            if required:
                findings.append(_result("schema-valid", "fail", f"{relative} が存在しない", relative))
            else:
                findings.append(_result("schema-valid", "skipped", f"{relative} は未生成", relative))
            continue
        try:
            instance = load_json(path)
        except json.JSONDecodeError as exc:
            findings.append(_result("schema-valid", "fail", f"JSON として読めない: {exc}", relative))
            continue
        errors = validate_schema(instance, load_schema(schema_name))
        if errors:
            findings.append(_result("schema-valid", "fail", "; ".join(errors[:5]), relative))
        else:
            findings.append(_result("schema-valid", "pass", f"{schema_name} に適合", relative))
    return findings


def lint_coverage_complete(run_dir: Path) -> list[dict[str, str]]:
    path = run_dir / "decomposition.json"
    if not path.is_file():
        return [_result("coverage-complete", "skipped", "decomposition.json が未生成", "decomposition.json")]
    try:
        items = load_json(path).get("atomic_items", [])
    except json.JSONDecodeError:
        return [_result("coverage-complete", "skipped", "decomposition.json を読めない", "decomposition.json")]
    stalled = [
        item.get("id", "?")
        for item in items
        if item.get("importance") == "high" and item.get("status") in {"uncovered", "collecting"}
    ]
    if stalled:
        return [_result(
            "coverage-complete", "fail",
            f"High Importance の論点が未処理: {', '.join(stalled)}", "decomposition.json",
        )]
    return [_result("coverage-complete", "pass", "High Importance の論点はすべて処理済み", "decomposition.json")]


def lint_source_metadata(run_dir: Path, vault_root: Path) -> list[dict[str, str]]:
    path = run_dir / "sources.json"
    if not path.is_file():
        return [_result("source-metadata", "skipped", "sources.json が未生成", "sources.json")]
    try:
        sources = load_json(path).get("sources", [])
    except json.JSONDecodeError:
        return [_result("source-metadata", "skipped", "sources.json を読めない", "sources.json")]

    findings: list[dict[str, str]] = []
    for source in sources:
        source_id = source.get("source_id", "?")
        missing = [key for key in ("url", "retrieved_at", "source_type") if not source.get(key)]
        if missing:
            findings.append(_result(
                "source-metadata", "fail", f"{source_id}: {', '.join(missing)} が無い", "sources.json"))
            continue
        note = _resolve_note(source.get("note_path", ""), run_dir, vault_root)
        if note is None or not note.is_file():
            findings.append(_result(
                "source-metadata", "fail", f"{source_id}: Source Note が実在しない", source.get("note_path", "")))
            continue
        frontmatter = parse_frontmatter(note.read_text(encoding="utf-8"))
        note_missing = [key for key in ("url", "retrieved_at", "source_type") if not frontmatter.get(key)]
        if note_missing:
            findings.append(_result(
                "source-metadata", "fail",
                f"{source_id}: Note の frontmatter に {', '.join(note_missing)} が無い", str(note)))
    if not findings:
        findings.append(_result("source-metadata", "pass", f"{len(sources)} 件の情報源に必須項目がある", "sources.json"))
    return findings


def _resolve_note(note_path: str, run_dir: Path, vault_root: Path) -> Path | None:
    """Source notes live in the shared vault, but a run may reference them relatively."""
    if not note_path:
        return None
    candidate = Path(note_path)
    if candidate.is_absolute():
        return candidate
    for base in (vault_root, run_dir, vault_root.parent):
        resolved = base / candidate
        if resolved.is_file():
            return resolved
    return vault_root / candidate


def lint_quote_integrity(run_dir: Path, vault_root: Path) -> list[dict[str, str]]:
    draft = _draft_path(run_dir)
    if draft is None:
        return [_result("quote-integrity", "skipped", "草稿が未生成", "drafts/")]
    quotes = blockquote_lines(draft.read_text(encoding="utf-8"))
    if not quotes:
        return [_result("quote-integrity", "pass", "逐語引用なし", str(draft.name))]

    corpus = _quotable_corpus(run_dir, vault_root)
    if not corpus:
        return [_result("quote-integrity", "skipped", "照合先の Source Note が無い", str(draft.name))]

    findings = [
        _result("quote-integrity", "fail", f"引用が情報源に存在しない: {quote[:40]}...", str(draft.name))
        for quote in quotes
        if _normalize(quote) not in corpus
    ]
    if not findings:
        findings.append(_result("quote-integrity", "pass", f"{len(quotes)} 件の引用が情報源に存在", str(draft.name)))
    return findings


def _quotable_corpus(run_dir: Path, vault_root: Path) -> str:
    path = run_dir / "sources.json"
    if not path.is_file():
        return ""
    try:
        sources = load_json(path).get("sources", [])
    except json.JSONDecodeError:
        return ""
    parts: list[str] = []
    for source in sources:
        note = _resolve_note(source.get("note_path", ""), run_dir, vault_root)
        if note and note.is_file():
            parts.append(extract_section(note.read_text(encoding="utf-8"), "Quotable Passages"))
    return _normalize("\n".join(parts))


def _normalize(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _draft_path(run_dir: Path) -> Path | None:
    final = run_dir / "final-report.md"
    if final.is_file():
        return final
    drafts = sorted((run_dir / "drafts").glob("draft-*.md")) if (run_dir / "drafts").is_dir() else []
    return drafts[0] if drafts else None


def lint_internal_leak(run_dir: Path) -> list[dict[str, str]]:
    report = run_dir / "final-report.md"
    if not report.is_file():
        return [_result("internal-leak", "skipped", "final-report.md が未生成", "final-report.md")]
    text = report.read_text(encoding="utf-8")
    leaked = [marker for marker in INTERNAL_MARKERS if marker in text]
    if leaked:
        return [_result(
            "internal-leak", "fail",
            f"内部情報が混入している: {', '.join(leaked)}", "final-report.md")]
    return [_result("internal-leak", "pass", "内部情報の混入なし", "final-report.md")]


def lint_placeholder_check(run_dir: Path) -> list[dict[str, str]]:
    report = run_dir / "final-report.md"
    if not report.is_file():
        return [_result("placeholder-check", "skipped", "final-report.md が未生成", "final-report.md")]
    found = sorted(set(PLACEHOLDER_RE.findall(report.read_text(encoding="utf-8"))))
    if found:
        return [_result(
            "placeholder-check", "fail",
            f"プレースホルダーが残っている: {', '.join(found[:5])}", "final-report.md")]
    return [_result("placeholder-check", "pass", "プレースホルダーなし", "final-report.md")]


# --------------------------------------------------------------------------- #
# Runner
# --------------------------------------------------------------------------- #

def run_lints(run_dir: Path, vault_root: Path | None = None) -> dict[str, Any]:
    """Run every Phase 1 lint and summarise the outcome."""
    if not run_dir.is_dir():
        raise LintError(f"run directory not found: {run_dir}")
    # research/runs/<run-id> -> research/
    vault = vault_root if vault_root is not None else run_dir.parent.parent

    findings: list[dict[str, str]] = []
    findings += lint_query_preserved(run_dir)
    findings += lint_schema_valid(run_dir)
    findings += lint_coverage_complete(run_dir)
    findings += lint_source_metadata(run_dir, vault)
    findings += lint_quote_integrity(run_dir, vault)
    findings += lint_internal_leak(run_dir)
    findings += lint_placeholder_check(run_dir)

    failed = [f for f in findings if f["result"] == "fail"]
    return {
        "run_dir": str(run_dir),
        "verdict": "block" if failed else "pass",
        "failed": len(failed),
        "findings": findings,
    }


def format_report(report: dict[str, Any]) -> str:
    symbols = {"pass": "OK  ", "fail": "FAIL", "skipped": "--  ", "warn": "WARN"}
    lines = [f"run: {report['run_dir']}"]
    for finding in report["findings"]:
        symbol = symbols.get(finding["result"], "?   ")
        target = f" [{finding['target']}]" if finding["target"] else ""
        lines.append(f"  {symbol} {finding['lint']}: {finding['detail']}{target}")
    lines.append(f"verdict: {report['verdict']} ({report['failed']} failed)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path, help="research/runs/<run-id>")
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON")
    args = parser.parse_args(argv)
    try:
        report = run_lints(args.run_dir)
    except LintError as exc:
        print(f"lint failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else format_report(report))
    return 1 if report["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
