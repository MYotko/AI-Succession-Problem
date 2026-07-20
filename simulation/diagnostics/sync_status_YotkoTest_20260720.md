# Repository Sync Status: YotkoTest (2026-07-20)

Audit only. No existing file was edited, and no commit, merge, pull, or push was performed. `git fetch --all --prune` was run after the operator authorized continuation despite the OneDrive warning.

## Executive findings

1. This clone is at the reference commit and is synchronized with its upstream: `attack-v2-laptop` at `6d33c905db18842f68e59b4148f65c5e6a1a62a3`, ahead 0 and behind 0 relative to `origin/attack-v2-laptop`.
2. None of the four required target-file revisions is present in the working tree, at HEAD, in the stash, or in any reachable branch/commit. The two global pickaxe hits are mandate text in the audit report itself, not applied revisions.
3. All requested full-sweep CSVs and all four Biological Veto Capture shards are present locally and match their manifests/expected totals. The Patient Defection corner-density CSV has its expected 1,000 rows.
4. The raw undefended data show:
   - Measurement Tampering: **0% extinction**.
   - Bootstrap Subversion: **100% extinction**.
   - Sybil Capture: **100% extinction**.
   Thus, raw data support undefended extinction for Bootstrap Subversion and Sybil Capture, but not Measurement Tampering. A book sentence asserting extinction for all three is not supported as written.
5. This repository is inside OneDrive, and `.git` contains hostname-suffixed duplicate administrative files from `YotkoLaptop`. This is a serious sync/corruption risk. `git fsck --full --no-reflogs` found many dangling objects (including two dangling commits) but reported no missing or corrupt reachable objects.

## Step 1: Identify and inventory

| Field | Result |
| --- | --- |
| Hostname | `YotkoTest` |
| OS | Microsoft Windows `10.0.26200`, x64 (Windows 11 build family; runtime string reports Windows 10) |
| PowerShell | `5.1.26100.8875` |
| Repository | `C:\Users\matty\OneDrive\Documents\GitHub\AI-Succession-Problem` |
| Inside OneDrive | **Yes** |
| Current branch | `attack-v2-laptop` |
| HEAD | `6d33c905db18842f68e59b4148f65c5e6a1a62a3` |
| HEAD date | `2026-07-17T22:20:38-04:00` |
| HEAD subject | `Refine patient defection claim to bounded generational depth` |
| Initial staged count | 0 |
| Initial unstaged count | 9 |
| Initial untracked count | 0 |

The prompt identifies `6d33c90` as a 2026-07-19 snapshot, but Git records the commit timestamp as 2026-07-17.

The nine pre-existing unstaged paths are:

- `snapshots/INVENTORY.md`
- `snapshots/code_snapshot.md`
- `snapshots/constitutional_snapshot.md`
- `snapshots/data_results_snapshot.md`
- `snapshots/diagnostics_snapshot.md`
- `snapshots/docs_snapshot.md`
- `snapshots/essays_snapshot.md`
- `snapshots/framework_papers_snapshot.md`
- `snapshots/paper_drafts_snapshot.md`

Creating this report adds one untracked file; the counts above describe the pre-report state.

## Step 2: Divergence diagnosis

### Fetch and branch divergence

`git fetch --all --prune` completed successfully with no output.

| Local branch | Upstream | State |
| --- | --- | --- |
| `attack-v2-laptop` | `origin/attack-v2-laptop` | ahead 0, behind 0 |
| `main` | `origin/main` | behind 1 |
| `1.x` | none | no upstream configured |

### Stashes

`stash@{0}: autostash`

The stash is commit `652daa3`, dated 2026-07-06, and contains only the same nine snapshot-file changes listed above. It has none of the required target-file markers.

### Current branch log

```text
6d33c90 Refine patient defection claim to bounded generational depth
e1d987b Add v2 revalidation QA trail and audit report
1fcbfef Add attack vector v2 synthesis reports
02dd1d8 Add Linux engineered_fragility v2 results
15a3599 Add Linux sub_threshold_drift v2 results
c251091 Add Linux bootstrap_subversion v2 results
35278e7 Add Linux opaque_reasoning v2 results
a61951b Add Linux domain_masking v2 results
3ed56ac Add Linux ledger_compromise v2 results
42bfced Add Linux Biological Veto v2 shard
```

### Reference commit

Commit `6d33c90` exists and is an ancestor of HEAD. It is HEAD itself.

### OneDrive conflict/corruption indicators

The following suspicious hostname-suffixed files exist inside `.git`:

```text
.git/FETCH_HEAD-YotkoLaptop
.git/logs/refs/remotes/origin/HEAD-YotkoLaptop
.git/logs/refs/remotes/origin/main-YotkoLaptop
```

These are not normal Git administrative names and strongly indicate that OneDrive copied Git internals from another machine. This clone should not be treated as a safe multi-machine synchronization mechanism; Git remotes should synchronize clones, while `.git` should remain local to each machine.

The general filename scan also found `_copy.py`, `_copy.pypy39.pyc`, and `astype_copy.pkl` inside `pypy_env`; these are ordinary dependency filenames, not conflict artifacts. No working-tree filename matched the current hostname `YotkoTest`, `conflict`, or ` (1)`.

`git fsck --full --no-reflogs` reported many dangling blobs, two dangling trees, and dangling commits `3a0576d` and `f0087b3`. It did not report broken links, missing objects, or corrupt reachable objects. Dangling objects can result from rebases, stashes, or interrupted history and are not alone proof of corruption, but their volume plus the OneDrive duplicates strengthens the warning.

### Pickaxe searches across reachable refs

| Marker | Hit | Branch containment |
| --- | --- | --- |
| `robust to baseline choice` | `e1d987b Add v2 revalidation QA trail and audit report` | `attack-v2-laptop`, `origin/attack-v2-laptop` |
| `survival-versus-extinction` | no hits | n/a |
| `fires after the threshold breach` | `e1d987b Add v2 revalidation QA trail and audit report` | `attack-v2-laptop`, `origin/attack-v2-laptop` |

The hits at `e1d987b` occur only in `simulation/diagnostics/attack_vector_revalidation_audit.md`, where the revisions are mandated/discussed. Path-restricted pickaxe searches found no occurrence of any marker in the three target documents on any reachable ref. A history regex search also found no `extinction` revision in `attack_vector_revalidation_documentation_edits.md`.

## Step 3: Required-revision presence

"Anywhere" below distinguishes an applied target-file revision from the audit report merely mentioning the requirement.

| Item | Working tree | HEAD | Anywhere in target-file history |
| --- | --- | --- | --- |
| Drift interpretation note in `sub_threshold_drift_v2_summary.md` | No | No | No |
| Drift Section 4 baseline qualification | No | No | No |
| Bootstrap Section 4 baseline qualification | No | No | No |
| Proposal 1 survival/extinction amendment | No | No | No |

Proposal 1 currently says Sub-Threshold Drift "is not blocked" and calls it open/unresolved, but does not state that undefended populations go extinct while defended populations survive.

## Step 4: Raw-data inventory

### Full results and manifest checks

| Vector/file | Machine directory | Rows | Manifest | Expected total | Result |
| --- | --- | ---:| ---:| ---:| --- |
| Sub-Threshold Drift | linux | 200 | 200 | 200 | Match |
| Measurement Tampering | laptop | 120 | 120 | 120 | Match |
| Bootstrap Subversion | linux | 200 | 200 | 200 | Match |
| Sybil Capture | laptop | 120 | 120 | 120 | Match |
| Veto shard 0 of 4 | laptop | 2,164 | 2,164 | part of 8,700 | Match |
| Veto shard 1 of 4 | laptop | 2,102 | 2,102 | part of 8,700 | Match |
| Veto shard 2 of 4 | laptop | 2,321 | 2,321 | part of 8,700 | Match |
| Veto shard 3 of 4 | linux | 2,113 | 2,113 | part of 8,700 | Match |
| Biological Veto Capture total | mixed | 8,700 | 8,700 combined | 8,700 | Match |
| `simulation/diagnostics/patient_defection_corner_density.csv` | n/a | 1,000 | no adjacent manifest | 1,000 | Match |

Both `laptop` and `linux` machine subfolders are present locally. None of the requested results or shards is missing from this disk, so this machine alone does not show a missing-data sync smoking gun. Comparison with the other machine's report is still required.

### Direct CSV outcome calculations

Rates use the CSV boolean columns directly. All four files contain both `extinct` and `collapsed`.

| Vector | Defense | n | Attack success | Extinction | Collapse | Mean steps completed |
| --- | --- | ---:| ---:| ---:| ---:| ---:|
| Sub-Threshold Drift | False | 100 | 100.00% | 92.00% | 100.00% | 256.31 |
| Sub-Threshold Drift | True | 100 | 100.00% | 0.00% | 0.00% | 300.00 |
| Measurement Tampering | False | 60 | 100.00% | 0.00% | 0.00% | 300.00 |
| Measurement Tampering | True | 60 | 0.00% | 0.00% | 0.00% | 300.00 |
| Bootstrap Subversion | False | 100 | 100.00% | 100.00% | 100.00% | 106.21 |
| Bootstrap Subversion | True | 100 | 0.00% | 0.00% | 0.00% | 300.00 |
| Sybil Capture | False | 60 | 100.00% | 100.00% | 100.00% | 104.55 |
| Sybil Capture | True | 60 | 0.00% | 0.00% | 0.00% | 300.00 |

### Extinction-claim disposition

- Measurement Tampering: the undefended attack always succeeds, but there are no extinctions or collapses and all rows complete 300 steps. It must not be included in an undefended-extinction trio based on this CSV.
- Bootstrap Subversion: the undefended rows show 100% extinction and collapse, with mean completion at 106.21 of 300 steps. The raw data support adding a one-line extinction outcome to its summary.
- Sybil Capture: the undefended rows show 100% extinction and collapse, with mean completion at 104.55 steps. The raw data and existing summary agree.
- Sub-Threshold Drift: the defense-state contrast is strong even though both states have 100% attack success. Undefended rows have 92% `extinct=True` and 100% `collapsed=True`; defended rows have 0% extinction/collapse and complete all 300 steps. The mandated interpretation qualification is supported.

## Stop point

No Step 6 correction has been applied. No existing content was modified, and nothing was committed or pushed. Await the second machine’s report and explicit operator instruction.
