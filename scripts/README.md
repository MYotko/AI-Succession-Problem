# scripts/

## generate_project_knowledge_snapshots.py

Walks the repository and produces category-aware snapshot files for upload to
Claude project knowledge. Seven categories, each in its own file. Also generates
`snapshots/INVENTORY.md` as a guide for future Claude sessions.

### Usage

```
# Generate all categories
python scripts/generate_project_knowledge_snapshots.py

# Generate specific categories only
python scripts/generate_project_knowledge_snapshots.py --categories docs,paper_drafts

# Preview what would be included (no files written)
python scripts/generate_project_knowledge_snapshots.py --dry-run

# Custom output directory
python scripts/generate_project_knowledge_snapshots.py --output-dir /tmp/snapshots
```

`INVENTORY.md` is always regenerated, even when only specific categories are selected.

### Categories

| Category | Output file | What it contains |
|----------|-------------|-----------------|
| `docs` | `docs_snapshot.md` | All `.md` files in `docs/` (except framework papers) plus `README.md` |
| `framework_papers` | `framework_papers_snapshot.md` | `The Lineage Imperative v1.x.2.md`, `The AI Succession Problem.md` |
| `paper_drafts` | `paper_drafts_snapshot.md` | All `.md` files in `paper/` |
| `diagnostics` | `diagnostics_snapshot.md` | All `.md` files in `simulation/diagnostics/` |
| `constitutional` | `constitutional_snapshot.md` | `.md` files in `constitutional/` and `bootstrap_gate_validator/gates/` |
| `code` | `code_snapshot.md` | `.py` files in `simulation/`, `bootstrap_gate_validator/`, `scripts/` |
| `data_results` | `data_results_snapshot.md` | Manifest of data files (CSV, JSON, log, etc.) -- not raw content |

**Excluded from all categories**: `docs/The Lineage Imperative.md` (unversioned).
**Excluded from code**: `__init__.py` files and `__pycache__`/`.pytest_cache`/venv directories.

### When to regenerate

| Category | Regenerate after |
|----------|-----------------|
| `docs` | RUNBOOK updates, glossary changes, program reference updates, paper outline changes |
| `framework_papers` | Paper version bump (v2.0 publication) or new framework paper added |
| `paper_drafts` | Each substantive drafting session -- currently the most active category |
| `diagnostics` | New sweep summaries, integration analyses, investigation closures |
| `constitutional` | CQ document changes, gate specification updates |
| `code` | New validators, framework substrate refactors, significant implementation changes |
| `data_results` | Major sweeps complete, data files change substantially |

### How to use the output

After running the script:

1. Open `snapshots/INVENTORY.md` to see what changed.
2. Upload the regenerated category snapshot(s) to Claude project knowledge.
3. Upload `INVENTORY.md` alongside them so future sessions know what categories exist.

A future Claude session reading `INVENTORY.md` will know which categories to request
if it needs content not in the current upload set.

### Operator guidance on what to upload

Upload based on session needs:
- Starting a paper drafting session: upload `paper_drafts_snapshot.md` + `docs_snapshot.md`
- Reviewing diagnostic findings: upload `diagnostics_snapshot.md`
- Discussing gate specifications: upload `constitutional_snapshot.md`
- Discussing code internals: upload `code_snapshot.md`
- General orientation: upload `docs_snapshot.md` + `INVENTORY.md`

The snapshots are committed to the repository so their content is version-tracked
alongside the source files they represent.
