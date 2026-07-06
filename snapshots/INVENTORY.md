# Project Knowledge Snapshots Inventory

Last regeneration: 2026-07-06T16:01:19Z
Git commit at regeneration: 9426e7d
Branch: main

## Quick reference for Claude sessions

If you need specific content, ask the operator to upload the relevant category snapshot.

| Need | Category | Snapshot file |
|------|----------|---------------|
| Current framework state, defaults, gate status | docs | snapshots/docs_snapshot.md |
| Published paper content, framework derivation | framework_papers | snapshots/framework_papers_snapshot.md |
| Active paper work (Section VIII, Appendix C) | paper_drafts | snapshots/paper_drafts_snapshot.md |
| Essay series; public-facing framing and narrative | essays | snapshots/essays_snapshot.md |
| Investigation findings, sweep results, integration analyses | diagnostics | snapshots/diagnostics_snapshot.md |
| Constitutional questions, gate specifications | constitutional | snapshots/constitutional_snapshot.md |
| Implementation code, validator logic | code | snapshots/code_snapshot.md |
| Data file manifest, what raw data exists | data_results | snapshots/data_results_snapshot.md |

## Category status

### docs
- File: snapshots/docs_snapshot.md
- Last generated: 2026-07-06T16:01:19Z
- Files included: 12
- Snapshot size: 377974 bytes

### framework_papers
- File: snapshots/framework_papers_snapshot.md
- Last generated: 2026-07-06T16:01:19Z
- Files included: 3
- Snapshot size: 444577 bytes

### paper_drafts
- File: snapshots/paper_drafts_snapshot.md
- Last generated: 2026-07-06T16:01:19Z
- Files included: 4
- Snapshot size: 271321 bytes

### essays
- File: snapshots/essays_snapshot.md
- Last generated: 2026-07-06T16:01:19Z
- Files included: 14
- Snapshot size: 367512 bytes

### diagnostics
- File: snapshots/diagnostics_snapshot.md
- Last generated: 2026-07-06T16:01:19Z
- Files included: unknown
- Snapshot size: 334241 bytes

### constitutional
- File: snapshots/constitutional_snapshot.md
- Last generated: 2026-07-06T16:01:19Z
- Files included: 6
- Snapshot size: 40827 bytes

### code
- File: snapshots/code_snapshot.md
- Last generated: 2026-07-06T16:01:19Z
- Files included: unknown
- Snapshot size: 1024396 bytes

### data_results
- File: snapshots/data_results_snapshot.md
- Last generated: 2026-07-06T16:01:19Z
- Files included: unknown
- Snapshot size: 31399 bytes

## When to regenerate each category

### docs
Regenerate after: After RUNBOOK updates, glossary changes, specification gap closures, program reference updates, paper outline changes.

### framework_papers
Regenerate after: Rare. Only when paper version bumps (v2.0 publishes) or new framework paper added.

### paper_drafts
Regenerate after: After each substantive paper drafting session. Currently the most active category.

### essays
Regenerate after: After essay additions or revisions to the essay series. Rare.

### diagnostics
Regenerate after: After new sweep summaries, integration analyses, framing documents, investigation closures.

### constitutional
Regenerate after: After CQ document changes, gate specification updates. Rare.

### code
Regenerate after: After new validators, framework substrate refactors, significant implementation changes.

### data_results
Regenerate after: After major sweeps complete, when data files change substantially.

## Methodological note

If you (a future Claude session) are reading a category snapshot and find a substantive claim that conflicts with another category snapshot, the dating tells you which is current. If both are recent and conflict, raise the conflict explicitly with the operator rather than choosing arbitrarily.

If the operator references work that should appear in a category snapshot but does not (e.g., 'the Phase B integration analysis' but no such file in diagnostics_snapshot), ask the operator to either regenerate that category or upload the specific file directly. Do not assume the snapshot is comprehensive if it is outdated.
