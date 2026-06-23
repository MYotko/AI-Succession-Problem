#!/usr/bin/env python3
"""
Generate category-aware project knowledge snapshots for upload to Claude project knowledge.

Seven categories: docs, framework_papers, paper_drafts, diagnostics, constitutional,
code, data_results.

Usage:
    python scripts/generate_project_knowledge_snapshots.py
    python scripts/generate_project_knowledge_snapshots.py --categories docs,paper_drafts
    python scripts/generate_project_knowledge_snapshots.py --dry-run
"""

import argparse
import csv as csv_module
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

UTC = datetime.timezone.utc

# ---------------------------------------------------------------------------
# Repository layout
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).parent.resolve()
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / "snapshots"

ALL_CATEGORIES = [
    "docs",
    "framework_papers",
    "paper_drafts",
    "diagnostics",
    "constitutional",
    "code",
    "data_results",
]

CATEGORY_OUTPUT_FILENAMES = {
    "docs": "docs_snapshot.md",
    "framework_papers": "framework_papers_snapshot.md",
    "paper_drafts": "paper_drafts_snapshot.md",
    "diagnostics": "diagnostics_snapshot.md",
    "constitutional": "constitutional_snapshot.md",
    "code": "code_snapshot.md",
    "data_results": "data_results_snapshot.md",
}

# ---------------------------------------------------------------------------
# Category inclusion rules
# ---------------------------------------------------------------------------

# Files that belong to framework_papers (excluded from docs)
FRAMEWORK_PAPERS_RELPATHS = [
    "docs/The Lineage Imperative v1.x.2.md",
    "docs/The AI Succession Problem.md",
]

# Files excluded from ALL categories
EXCLUDED_FROM_ALL_RELPATHS = {
    "docs/The Lineage Imperative.md",
}

# Directories to skip when walking for code
CODE_SKIP_DIRS = frozenset({
    "__pycache__", ".pytest_cache", "venv", ".venv", "env",
    "node_modules", ".git",
})

# Data file extensions for data_results manifest
DATA_EXTENSIONS = frozenset({
    ".csv", ".json", ".log", ".parquet", ".pkl", ".h5", ".hdf5",
    ".npy", ".npz",
})

# Directories to scan for data files (relative to REPO_ROOT)
DATA_SCAN_DIRS = [
    "simulation/diagnostics",
    "simulation/results",
    "bootstrap_gate_validator",
]

# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def get_git_info() -> Tuple[str, str]:
    """Return (short_commit_hash, branch_name)."""
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        branch = subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        return commit, branch
    except Exception:
        print("WARNING: git introspection failed; using placeholder values", file=sys.stderr)
        return "unknown", "unknown"

# ---------------------------------------------------------------------------
# File utilities
# ---------------------------------------------------------------------------

def read_file_safe(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"WARNING: could not read {path}: {e}", file=sys.stderr)
        return None

def line_count(text: str) -> int:
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)

def byte_count(text: str) -> int:
    return len(text.encode("utf-8"))

# ---------------------------------------------------------------------------
# Snapshot writing
# ---------------------------------------------------------------------------

SEPARATOR = "=" * 42


def write_snapshot(
    output_path: Path,
    category: str,
    file_entries: List[Tuple[str, str]],
    commit: str,
    branch: str,
    note: str = "",
) -> Tuple[int, int, int]:
    """Write a standard category snapshot. Returns (n_files, total_lines, total_bytes)."""
    now = datetime.datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    file_meta = [(rp, line_count(c), byte_count(c)) for rp, c in file_entries]
    total_files = len(file_meta)
    total_lines = sum(l for _, l, _ in file_meta)
    total_bytes = sum(b for _, _, b in file_meta)

    header_lines = [
        f"# {category.replace('_', ' ').title()} Snapshot",
        "",
        f"Generated: {now}",
        f"Repository: {REPO_ROOT}",
        f"Commit: {commit}",
        f"Branch: {branch}",
        f"Category: {category}",
    ]
    if note:
        header_lines += ["", f"NOTE: {note}"]
    header_lines += [
        "",
        "## Files included",
        "",
        "| File | Lines | Bytes |",
        "|------|-------|-------|",
    ]
    for relpath, nlines, nbytes in file_meta:
        header_lines.append(f"| {relpath} | {nlines} | {nbytes} |")
    header_lines += [
        "",
        f"Total: {total_files} files, {total_lines} lines, {total_bytes} bytes",
        "",
        "---",
        "",
    ]

    body_parts = []
    for relpath, content in file_entries:
        body_parts.append(f"{SEPARATOR}\nFILE: {relpath}\n{SEPARATOR}\n\n{content}\n")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(header_lines) + "\n".join(body_parts), encoding="utf-8")
    return total_files, total_lines, total_bytes

# ---------------------------------------------------------------------------
# Data results manifest helpers
# ---------------------------------------------------------------------------

def _manifest_csv(path: Path) -> str:
    stat = path.stat()
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"- Size: {stat.st_size} bytes", f"- Modified: {mtime}"]
    try:
        with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
            rows = list(csv_module.reader(f))
        if not rows:
            lines.append("- Empty file")
        else:
            headers = rows[0]
            data_rows = rows[1:]
            lines.append(f"- Rows: {len(data_rows)} data rows")
            lines.append(f"- Columns ({len(headers)}): {', '.join(headers)}")
            if data_rows:
                lines.append("- Sample (first 5 data rows):")
                lines.append("```")
                lines.append(",".join(headers))
                for row in data_rows[:5]:
                    lines.append(",".join(str(v) for v in row))
                lines.append("```")
    except Exception as e:
        lines.append(f"- Could not parse CSV: {e}")
    return "\n".join(lines)


def _manifest_json(path: Path) -> str:
    stat = path.stat()
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"- Size: {stat.st_size} bytes", f"- Modified: {mtime}"]
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
        if isinstance(data, dict):
            keys = list(data.keys())
            preview = ", ".join(str(k) for k in keys[:20])
            suffix = " ..." if len(keys) > 20 else ""
            lines.append(f"- Structure: object with {len(keys)} top-level keys")
            lines.append(f"- Keys: {preview}{suffix}")
        elif isinstance(data, list):
            lines.append(f"- Structure: array with {len(data)} elements")
            if data and isinstance(data[0], dict):
                first_keys = list(data[0].keys())
                lines.append(f"- Element keys: {', '.join(str(k) for k in first_keys[:20])}")
        else:
            lines.append(f"- Structure: {type(data).__name__}")
    except Exception as e:
        lines.append(f"- Could not parse JSON: {e}")
    return "\n".join(lines)


def _manifest_log(path: Path) -> str:
    stat = path.stat()
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"- Size: {stat.st_size} bytes", f"- Modified: {mtime}"]
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
        total = len(all_lines)
        lines.append(f"- Total lines: {total}")
        if total > 0:
            head = [l.rstrip() for l in all_lines[:20]]
            lines.append("- First 20 lines:")
            lines.append("```")
            lines.extend(head)
            lines.append("```")
            if total > 20:
                tail = [l.rstrip() for l in all_lines[-20:]]
                lines.append(f"- Last 20 lines (of {total}):")
                lines.append("```")
                lines.extend(tail)
                lines.append("```")
    except Exception as e:
        lines.append(f"- Could not read log: {e}")
    return "\n".join(lines)


def _manifest_other(path: Path) -> str:
    stat = path.stat()
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    return "\n".join([
        f"- Size: {stat.st_size} bytes",
        f"- Modified: {mtime}",
        f"- Format: {path.suffix or 'unknown'}",
    ])


def collect_data_files() -> List[Path]:
    found: set = set()
    for scan_rel in DATA_SCAN_DIRS:
        scan_dir = REPO_ROOT / scan_rel
        if not scan_dir.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(scan_dir):
            dirnames[:] = [d for d in dirnames if d not in CODE_SKIP_DIRS]
            for filename in filenames:
                p = Path(dirpath) / filename
                if p.suffix.lower() in DATA_EXTENSIONS:
                    found.add(p)
    for p in REPO_ROOT.iterdir():
        if p.is_file() and p.suffix.lower() in DATA_EXTENSIONS:
            found.add(p)
    return sorted(found)


def write_data_results_snapshot(
    output_path: Path,
    commit: str,
    branch: str,
    dry_run: bool = False,
) -> Tuple[int, int, int]:
    """Write the data_results manifest snapshot."""
    data_files = collect_data_files()

    if dry_run:
        print(f"\n[data_results] Data files that would be included in manifest ({len(data_files)}):")
        for p in data_files[:40]:
            print(f"  {p.relative_to(REPO_ROOT)} ({p.suffix})")
        if len(data_files) > 40:
            print(f"  ... and {len(data_files) - 40} more")
        return 0, 0, 0

    now = datetime.datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    header_lines = [
        "# Data Results Snapshot",
        "",
        f"Generated: {now}",
        f"Repository: {REPO_ROOT}",
        f"Commit: {commit}",
        f"Branch: {branch}",
        "Category: data_results",
        "",
        "NOTE: This snapshot contains a manifest of data files, not raw file content.",
        "",
        "## Data files indexed",
        "",
        "| File | Size (bytes) | Modified |",
        "|------|-------------|----------|",
    ]

    file_meta = []
    for p in data_files:
        relpath = str(p.relative_to(REPO_ROOT))
        stat = p.stat()
        mtime = datetime.datetime.fromtimestamp(stat.st_mtime, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        header_lines.append(f"| {relpath} | {stat.st_size} | {mtime} |")
        file_meta.append((p, relpath))

    header_lines += [
        "",
        f"Total: {len(data_files)} files",
        "",
        "---",
        "",
    ]

    body_parts = []
    for p, relpath in file_meta:
        ext = p.suffix.lower()
        if ext == ".csv":
            entry = _manifest_csv(p)
        elif ext == ".json":
            entry = _manifest_json(p)
        elif ext == ".log":
            entry = _manifest_log(p)
        else:
            entry = _manifest_other(p)
        body_parts.append(f"{SEPARATOR}\nFILE: {relpath}\n{SEPARATOR}\n\n{entry}\n")

    content = "\n".join(header_lines) + "\n".join(body_parts)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return len(data_files), line_count(content), byte_count(content)

# ---------------------------------------------------------------------------
# Category collectors
# ---------------------------------------------------------------------------

def _print_dry_run(
    category: str,
    results: List[Tuple[str, str]],
    skipped: Optional[List[Tuple[str, str]]] = None,
) -> None:
    total_lines = sum(line_count(c) for _, c in results)
    total_bytes = sum(byte_count(c) for _, c in results)
    print(f"\n[{category}] Files that would be included ({len(results)}):")
    for rp, c in results:
        print(f"  {rp} ({line_count(c)} lines, {byte_count(c)} bytes)")
    print(f"  Estimated total: {total_lines} lines, {total_bytes} bytes")
    if skipped:
        print(f"[{category}] Files skipped ({len(skipped)}):")
        for rp, reason in skipped:
            print(f"  {rp} -- {reason}")


def collect_docs(dry_run: bool = False) -> List[Tuple[str, str]]:
    docs_dir = REPO_ROOT / "docs"
    if not docs_dir.exists():
        print("INFO: docs/ directory not found", file=sys.stderr)
        return []

    framework_set = set(FRAMEWORK_PAPERS_RELPATHS)
    excluded_set = set(EXCLUDED_FROM_ALL_RELPATHS)

    results = []
    skipped = []
    for path in sorted(docs_dir.glob("*.md")):
        relpath = str(path.relative_to(REPO_ROOT))
        if relpath in framework_set:
            skipped.append((relpath, "framework_papers category"))
            continue
        if relpath in excluded_set:
            skipped.append((relpath, "excluded from all categories"))
            continue
        content = read_file_safe(path)
        if content is not None:
            results.append((relpath, content))

    readme = REPO_ROOT / "README.md"
    if readme.exists():
        content = read_file_safe(readme)
        if content is not None:
            results.append(("README.md", content))

    if dry_run:
        _print_dry_run("docs", results, skipped)
    return results


def collect_framework_papers(dry_run: bool = False) -> List[Tuple[str, str]]:
    results = []
    skipped = []
    for relpath in FRAMEWORK_PAPERS_RELPATHS:
        path = REPO_ROOT / relpath
        if not path.exists():
            skipped.append((relpath, "file not found"))
            print(f"INFO: framework paper not found: {relpath}", file=sys.stderr)
            continue
        content = read_file_safe(path)
        if content is not None:
            results.append((relpath, content))

    if dry_run:
        _print_dry_run("framework_papers", results, skipped)
    return results


def collect_paper_drafts(dry_run: bool = False) -> List[Tuple[str, str]]:
    paper_dir = REPO_ROOT / "paper"
    if not paper_dir.exists():
        print("INFO: paper/ directory not found", file=sys.stderr)
        if dry_run:
            print("\n[paper_drafts] Directory not found; no files would be included.")
        return []

    results = []
    for path in sorted(paper_dir.glob("*.md")):
        content = read_file_safe(path)
        if content is not None:
            results.append((str(path.relative_to(REPO_ROOT)), content))

    if dry_run:
        _print_dry_run("paper_drafts", results)
    return results


def collect_diagnostics(dry_run: bool = False) -> List[Tuple[str, str]]:
    diag_dir = REPO_ROOT / "simulation" / "diagnostics"
    if not diag_dir.exists():
        print("INFO: simulation/diagnostics/ not found", file=sys.stderr)
        if dry_run:
            print("\n[diagnostics] Directory not found; no files would be included.")
        return []

    results = []
    for path in sorted(diag_dir.glob("*.md")):
        content = read_file_safe(path)
        if content is not None:
            results.append((str(path.relative_to(REPO_ROOT)), content))

    if dry_run:
        _print_dry_run("diagnostics", results)
    return results


def collect_constitutional(dry_run: bool = False) -> List[Tuple[str, str]]:
    results = []
    for search_dir in [
        REPO_ROOT / "constitutional",
        REPO_ROOT / "bootstrap_gate_validator" / "gates",
    ]:
        if not search_dir.exists():
            print(f"INFO: {search_dir.relative_to(REPO_ROOT)} not found", file=sys.stderr)
            continue
        for path in sorted(search_dir.glob("*.md")):
            content = read_file_safe(path)
            if content is not None:
                results.append((str(path.relative_to(REPO_ROOT)), content))

    if dry_run:
        _print_dry_run("constitutional", results)
    return results


def collect_code(dry_run: bool = False) -> List[Tuple[str, str]]:
    scan_dirs = [
        REPO_ROOT / "simulation",
        REPO_ROOT / "bootstrap_gate_validator",
        REPO_ROOT / "scripts",
    ]

    results = []
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(scan_dir):
            dirnames[:] = sorted(d for d in dirnames if d not in CODE_SKIP_DIRS)
            for filename in sorted(filenames):
                if filename == "__init__.py":
                    continue
                if not filename.endswith(".py"):
                    continue
                path = Path(dirpath) / filename
                content = read_file_safe(path)
                if content is not None:
                    results.append((str(path.relative_to(REPO_ROOT)), content))

    if dry_run:
        _print_dry_run("code", results)
    return results


COLLECTORS = {
    "docs": collect_docs,
    "framework_papers": collect_framework_papers,
    "paper_drafts": collect_paper_drafts,
    "diagnostics": collect_diagnostics,
    "constitutional": collect_constitutional,
    "code": collect_code,
}

# ---------------------------------------------------------------------------
# Category dispatch
# ---------------------------------------------------------------------------

def generate_category(
    category: str,
    output_dir: Path,
    commit: str,
    branch: str,
    dry_run: bool,
) -> None:
    output_path = output_dir / CATEGORY_OUTPUT_FILENAMES[category]

    if category == "data_results":
        nfiles, nlines, nbytes = write_data_results_snapshot(
            output_path, commit, branch, dry_run=dry_run
        )
        if not dry_run:
            print(f"  [{category}] Wrote {output_path} ({nfiles} files, {nbytes} bytes)")
        return

    entries = COLLECTORS[category](dry_run=dry_run)

    if dry_run:
        return

    if not entries:
        write_snapshot(
            output_path, category, [], commit, branch,
            note="No files found for this category.",
        )
        print(f"  [{category}] Wrote {output_path} (empty)")
    else:
        nfiles, nlines, nbytes = write_snapshot(output_path, category, entries, commit, branch)
        print(f"  [{category}] Wrote {output_path} ({nfiles} files, {nlines} lines, {nbytes} bytes)")

# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

CATEGORY_QUICK_REF = {
    "docs": "Current framework state, defaults, gate status",
    "framework_papers": "Published paper content, framework derivation",
    "paper_drafts": "Active paper work (Section VIII, Appendix C)",
    "diagnostics": "Investigation findings, sweep results, integration analyses",
    "constitutional": "Constitutional questions, gate specifications",
    "code": "Implementation code, validator logic",
    "data_results": "Data file manifest, what raw data exists",
}

CATEGORY_REGEN_NOTES = {
    "docs": (
        "After RUNBOOK updates, glossary changes, specification gap closures, "
        "program reference updates, paper outline changes."
    ),
    "framework_papers": (
        "Rare. Only when paper version bumps (v2.0 publishes) or new framework paper added."
    ),
    "paper_drafts": (
        "After each substantive paper drafting session. Currently the most active category."
    ),
    "diagnostics": (
        "After new sweep summaries, integration analyses, framing documents, investigation closures."
    ),
    "constitutional": (
        "After CQ document changes, gate specification updates. Rare."
    ),
    "code": (
        "After new validators, framework substrate refactors, significant implementation changes."
    ),
    "data_results": (
        "After major sweeps complete, when data files change substantially."
    ),
}


def _parse_snapshot_meta(snapshot_path: Path) -> Tuple[Optional[str], Optional[int]]:
    """Parse generated timestamp and file count from an existing snapshot file."""
    if not snapshot_path.exists():
        return None, None
    try:
        text = snapshot_path.read_text(encoding="utf-8")
        generated = None
        files_count = None
        for line in text.splitlines()[:30]:
            if line.startswith("Generated: "):
                generated = line[len("Generated: "):]
            m = re.search(r"Total: (\d+) files", line)
            if m:
                files_count = int(m.group(1))
            if generated and files_count is not None:
                break
        return generated, files_count
    except Exception:
        return None, None


def generate_inventory(output_dir: Path, commit: str, branch: str) -> None:
    now = datetime.datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        reldir = str(output_dir.relative_to(REPO_ROOT))
    except ValueError:
        reldir = str(output_dir)

    lines = [
        "# Project Knowledge Snapshots Inventory",
        "",
        f"Last regeneration: {now}",
        f"Git commit at regeneration: {commit}",
        f"Branch: {branch}",
        "",
        "## Quick reference for Claude sessions",
        "",
        "If you need specific content, ask the operator to upload the relevant category snapshot.",
        "",
        "| Need | Category | Snapshot file |",
        "|------|----------|---------------|",
    ]
    for cat in ALL_CATEGORIES:
        filename = CATEGORY_OUTPUT_FILENAMES[cat]
        need = CATEGORY_QUICK_REF[cat]
        lines.append(f"| {need} | {cat} | {reldir}/{filename} |")

    lines += ["", "## Category status", ""]

    for cat in ALL_CATEGORIES:
        filename = CATEGORY_OUTPUT_FILENAMES[cat]
        snapshot_path = output_dir / filename
        generated, files_count = _parse_snapshot_meta(snapshot_path)
        size = snapshot_path.stat().st_size if snapshot_path.exists() else None
        lines += [
            f"### {cat}",
            f"- File: {reldir}/{filename}",
            f"- Last generated: {generated or 'not yet generated'}",
            f"- Files included: {files_count if files_count is not None else 'unknown'}",
            f"- Snapshot size: {size if size is not None else 'n/a'} bytes",
            "",
        ]

    lines += ["## When to regenerate each category", ""]
    for cat in ALL_CATEGORIES:
        lines += [f"### {cat}", f"Regenerate after: {CATEGORY_REGEN_NOTES[cat]}", ""]

    lines += [
        "## Methodological note",
        "",
        (
            "If you (a future Claude session) are reading a category snapshot and find a "
            "substantive claim that conflicts with another category snapshot, the dating tells "
            "you which is current. If both are recent and conflict, raise the conflict explicitly "
            "with the operator rather than choosing arbitrarily."
        ),
        "",
        (
            "If the operator references work that should appear in a category snapshot but does "
            "not (e.g., 'the Phase B integration analysis' but no such file in "
            "diagnostics_snapshot), ask the operator to either regenerate that category or upload "
            "the specific file directly. Do not assume the snapshot is comprehensive if it is outdated."
        ),
        "",
    ]

    inventory_path = output_dir / "INVENTORY.md"
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  [inventory] Wrote {inventory_path}")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate category-aware project knowledge snapshots.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            f"Valid categories: {', '.join(ALL_CATEGORIES)}\n"
            "INVENTORY.md is always regenerated, even when only specific categories are selected."
        ),
    )
    parser.add_argument(
        "--categories",
        metavar="CAT[,CAT,...]",
        default=",".join(ALL_CATEGORIES),
        help="Comma-separated list of categories to generate. Default: all.",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory to write snapshot files. Default: snapshots/ at repo root.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be included without writing any files.",
    )
    args = parser.parse_args()

    categories = [c.strip() for c in args.categories.split(",") if c.strip()]
    unknown = [c for c in categories if c not in ALL_CATEGORIES]
    if unknown:
        print(f"ERROR: unrecognized categories: {', '.join(unknown)}", file=sys.stderr)
        print(f"Valid: {', '.join(ALL_CATEGORIES)}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    commit, branch = get_git_info()

    if args.dry_run:
        print(f"DRY RUN (no files will be written)")
        print(f"Commit: {commit}, Branch: {branch}")
        print(f"Categories: {', '.join(categories)}")
        for cat in categories:
            generate_category(cat, output_dir, commit, branch, dry_run=True)
        print("\nDry run complete.")
        return

    print(f"Generating snapshots: {', '.join(categories)}")
    print(f"Output directory: {output_dir}")
    print(f"Commit: {commit}, Branch: {branch}")
    output_dir.mkdir(parents=True, exist_ok=True)

    for cat in categories:
        generate_category(cat, output_dir, commit, branch, dry_run=False)

    generate_inventory(output_dir, commit, branch)
    print("Done.")


if __name__ == "__main__":
    main()
