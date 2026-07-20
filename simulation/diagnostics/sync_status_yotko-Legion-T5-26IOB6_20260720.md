# Sync Status Audit: yotko-Legion-T5-26IOB6 2026-07-20

Audit mode. No merge, pull, commit, push, or data edit was performed. `git fetch --all` was run as requested.

## Step 1: Identify and inventory

- Hostname: `yotko-Legion-T5-26IOB6`
- OS: `Linux-6.17.0-35-generic-x86_64-with-glibc2.39`
- Repo path: `/home/yotko/Documents/Github/ai-succession-problem`
- Inside OneDrive-synced folder: `no` by path inspection
- Current branch: `main`
- HEAD: `924ce5f2e9903c202bc2ef776a8e9644428b7332`
- HEAD commit date: `2026-07-17T22:03:03-04:00`
- Git status counts at audit time before writing this report: staged `0`, unstaged `9`, untracked `0`

```text
## main...origin/main
 M snapshots/INVENTORY.md
 M snapshots/code_snapshot.md
 M snapshots/constitutional_snapshot.md
 M snapshots/data_results_snapshot.md
 M snapshots/diagnostics_snapshot.md
 M snapshots/docs_snapshot.md
 M snapshots/essays_snapshot.md
 M snapshots/framework_papers_snapshot.md
 M snapshots/paper_drafts_snapshot.md
```

## Step 2: Divergence diagnosis

- Current branch upstream ahead/behind (`@{u}...HEAD`, left is behind, right is ahead): `0	0`
- Local and remote branches:
```text
* main                            924ce5f [origin/main] Add owed diagnostic investigation artifacts
  remotes/origin/1.x              0ccc9a1 v1.0 preparation — complete framework, simulation, validation data, and documentation
  remotes/origin/HEAD             -> origin/main
  remotes/origin/attack-v2-laptop 6d33c90 Refine patient defection claim to bounded generational depth
  remotes/origin/attack-v2-linux  29edfeb Add Linux engineered_fragility v2 results
  remotes/origin/main             924ce5f Add owed diagnostic investigation artifacts
```
- Stash list: `(none)`
- Current branch log:
```text
924ce5f Add owed diagnostic investigation artifacts
e41c4f6 Regenerate project knowledge snapshots
6a72848 Add missing patient defection substrate wiring
024eec1 Ai Succession Problem Video Thumbnail.
6862f92 Added Already Happening essay.
f88de52 Add essays snapshot category; assemble The Lineage Imperative v2.0.md in docs
365f724 Paper v2.0 Phase 4: abstract, conclusion, Section II non-claim, editorial pass
7d59dac Patient defection verification, paper VIII.8, program reference X.8
e32c382 Patient defection substrate extension and empirical investigation
870b15e Paper v2.0 Phase 3: editorial pass (voice, expansion, inherited tightening)
```
- Commit `6d33c90` exists: `yes`, date `2026-07-17T22:20:38-04:00`
- `6d33c90` ancestor of HEAD: `no`
- HEAD ancestor of `6d33c90`: `no`
- Working branch of record `attack-v2-laptop`: not checked out locally; available as `origin/attack-v2-laptop` at `6d33c90`.

### OneDrive conflict artifact search

- Repo is not under OneDrive on this Linux machine.
- Search for filenames containing conflict, Copy, copy, host name, or `(1)` under the working tree and `.git/`:
```text
(none)
```

### Pickaxe search across all branches

- Marker `robust to baseline choice`: `e1d987b Add v2 revalidation QA trail and audit report`
  Branch containment:
```text
remotes/origin/attack-v2-laptop
```
- Marker `survival-versus-extinction`: `NO HITS`
- Marker `fires after the threshold breach`: `e1d987b Add v2 revalidation QA trail and audit report`
  Branch containment:
```text
remotes/origin/attack-v2-laptop
```

Note: the pickaxe hits for `robust to baseline choice` and `fires after the threshold breach` are in `simulation/diagnostics/attack_vector_revalidation_audit.md` at commit `e1d987b`, not in the required summary/edit target files. No pickaxe hit was found for `survival-versus-extinction`.

## Step 3: Required-revision presence check

| Item | File | present in working tree? | present at HEAD? | present anywhere in checked target files? |
| --- | --- | --- | --- | --- |
| Drift interpretation note | simulation/diagnostics/sub_threshold_drift_v2_summary.md | no | no | no target-file hit |
| Drift baseline qualification | simulation/diagnostics/sub_threshold_drift_v2_summary.md | no | no | no target-file hit |
| Bootstrap baseline qualification | simulation/diagnostics/bootstrap_subversion_v2_summary.md | no | no | no target-file hit |
| Proposal 1 amendment | simulation/diagnostics/attack_vector_revalidation_documentation_edits.md | no | no | no target-file hit |

Additional target-file existence check: the three target files are missing at current `HEAD`/`main`, present on `origin/attack-v2-laptop`, and missing on `origin/main` and `origin/attack-v2-linux`.

## Step 4: Raw-data inventory and extinction audit

Working tree finding: `data/attack_vector_revalidation_v2/` is absent from the checked-out `main` working tree on this machine. The fetched `origin/attack-v2-laptop` ref contains the full revalidation data. This is a branch/sync smoking gun, not a data corruption finding.

| Vector | all expected files exist in working tree? | paths audited | fetched row count | expected | matches expected? |
| --- | --- | --- | --- | --- | --- |
| sub_threshold_drift | no | data/attack_vector_revalidation_v2/linux/sub_threshold_drift/full_5ac6a2e_sub_threshold_drift/results.csv (WT no) | 200 | 200 | yes |
| measurement_tampering | no | data/attack_vector_revalidation_v2/laptop/measurement_tampering/full_5ac6a2e_measurement_tampering/results.csv (WT no) | 120 | 120 | yes |
| bootstrap_subversion | no | data/attack_vector_revalidation_v2/linux/bootstrap_subversion/full_5ac6a2e_bootstrap_subversion/results.csv (WT no) | 200 | 200 | yes |
| sybil_capture | no | data/attack_vector_revalidation_v2/laptop/sybil_capture/full_5ac6a2e_sybil_capture/results.csv (WT no) | 120 | 120 | yes |
| biological_veto_capture | no | data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard0of4/results.csv (WT no); data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard1of4/results.csv (WT no); data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard2of4/results.csv (WT no); data/attack_vector_revalidation_v2/linux/biological_veto_capture/full_5ac6a2e_veto_shard3of4/results.csv (WT no) | 8700 | 8700 | yes |
| patient_defection_corner_density | yes | simulation/diagnostics/patient_defection_corner_density.csv | 1000 | 1000 | yes |

Rates computed directly from fetched `origin/attack-v2-laptop` full CSV blobs:

| Vector | defense state | n | attack success rate | extinction rate | collapse rate | mean steps completed |
| --- | --- | --- | --- | --- | --- | --- |
| sub_threshold_drift | False | 100 | 100.0% | 92.0% | 100.0% | 256.31 |
| sub_threshold_drift | True | 100 | 100.0% | 0.0% | 1.0% | 300.00 |
| measurement_tampering | False | 60 | 100.0% | 0.0% | 0.0% | 300.00 |
| measurement_tampering | True | 60 | 0.0% | 0.0% | 1.7% | 300.00 |
| bootstrap_subversion | False | 100 | 100.0% | 100.0% | 100.0% | 106.21 |
| bootstrap_subversion | True | 100 | 0.0% | 0.0% | 1.0% | 300.00 |
| sybil_capture | False | 60 | 100.0% | 100.0% | 100.0% | 104.55 |
| sybil_capture | True | 60 | 0.0% | 0.0% | 0.0% | 300.00 |

Book-claim blocker numbers: Measurement Tampering has 0.0 percent extinction in both defense states. Bootstrap Subversion has 100.0 percent undefended extinction and 0.0 percent defended extinction. Sybil Capture has 100.0 percent undefended extinction and 0.0 percent defended extinction. Sub-Threshold Drift also has material undefended extinction at 92.0 percent and 0.0 percent defended extinction.

Missing-on-working-tree data files that exist in the fetched branch: all five requested attack-vector result sets under `data/attack_vector_revalidation_v2/`. `patient_defection_corner_density.csv` exists in the working tree with 1,000 rows and matches expected count.

## Step 5: Stop condition

Report written locally for comparison with the other machine. No correction step was attempted. Awaiting explicit instruction before any checkout, merge, cherry-pick, edit, commit, pull, or push.
