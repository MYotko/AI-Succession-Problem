# Defended Collapse Rate Discrepancy: Diagnostic Report

Date: 2026-08-09
Evidence base: tag `attack-v2-revalidation-evidence` (commit `6d33c90`), reachable from `main` at `46585b4`
Scope: diagnostic only. No paper, program reference, summary, snapshot, or other published document was edited.

## 1. Verdict

The SHA-pinned blob audit (`sync_status_yotko-Legion-T5-26IOB6_20260720.md`) is correct for all three vectors. The local-disk audit (`sync_status_YotkoTest_20260720.md`) is wrong for all three.

| Vector | Local-disk audit | Pinned-blob audit | Correct | Verdict |
| --- | ---: | ---: | ---: | --- |
| Sub-Threshold Drift, defended | 0.00% | 1.0% | 1.00% (1 of 100) | pinned-blob audit correct |
| Measurement Tampering, defended | 0.00% | 1.7% | 1.67% (1 of 60) | pinned-blob audit correct |
| Bootstrap Subversion, defended | 0.00% | 1.0% | 1.00% (1 of 100) | pinned-blob audit correct |
| Sybil Capture, defended | 0.00% | 0.0% | 0.00% (0 of 60) | both correct |

### Root cause

Not a data provenance problem. The root cause is a PowerShell 5.1 scalar-collapse defect in the local-disk audit's counting idiom.

Provenance was ruled out first. The three result CSVs are content-identical across all three locations: the pinned blobs at the tag, the current working tree at `C:\Users\matty\dev\ai-succession-problem`, and the archived OneDrive clone at `C:\Users\matty\OneDrive\Documents\GitHub\AI-Succession-Problem-ARCHIVE-20260720` that the local-disk audit actually read. Normalized `git hash-object` values match the pinned blob SHAs exactly in every case. Byte-level differences exist but are line-ending artifacts only (see Anomaly A1). No audit read a different or stale file.

The defect is in how the local-disk audit counted matching rows. In Windows PowerShell 5.1, `Where-Object` returns a bare object rather than an array when exactly one row matches. For an `Import-Csv` row object, `.Count` and `.Length` then both evaluate to null, and null divided by the denominator yields 0. Reproduced against the authoritative measurement tampering CSV:

```
defended n                  : 60
collapsed matches, .Count   :          (null, not 1)
collapsed matches, .Length  :          (null, not 1)
is array?                   : False
rate                        : 0.00%
```

The same idiom applied to the 100-match undefended bootstrap subset returns `.Count = 100` and a correct 100.00%. The failure occurs at a match count of exactly one and nowhere else.

This explains the discrepancy completely and exclusively. Across all 24 cells of the local-disk audit's table (three metrics: attack success, extinction, collapse; four vectors; two defense states), the cells reported incorrectly are exactly the cells whose true match count is 1, and no correctly reported cell has a true match count of 1:

- True counts of cells reported wrong: `{1}`
- True counts of cells reported correctly: `{0, 60, 92, 100}`

The hypothesis "wrong if and only if true count equals 1" holds without exception. This also explains why extinction was unaffected: no extinction cell in that table has a count of 1. The single cell that proves the audit did compute collapse independently rather than copying extinction is undefended Sub-Threshold Drift, where extinction is 92.00% and collapse is 100.00% and the audit reported both correctly.

Two alternative explanations were tested and rejected. Defining collapse as `collapsed AND NOT defense_fired` reproduces the local-disk table exactly, but it is a degenerate match: `defense_fired` equals `defense_active` in all 640 rows, so the condition is empty by construction within any defended subset. Definitions based on extinction, survival, early termination, zero final population, and combinations of these all fail the undefended Sub-Threshold Drift cell, which requires 100.00% while every extinction-derived definition yields 92.00%.

The local-disk audit's own statement that "rates use the CSV boolean columns directly" is accurate as to intent. The columns were read correctly; the counting of the filtered result was not.

## 2. Authoritative figures

### Metric definition

`collapsed` is written by `simulation/run_attack_vector_revalidation_v2.py:419` as:

```python
collapse_threshold = max(model.min_viable_population, int(0.65 * peak_population))
'survived':  final_population >= collapse_threshold,
'collapsed': final_population <  collapse_threshold,
'extinct':   final_population == 0,
```

Collapse is therefore a **relative population drawdown**: the run ended below 65 percent of its own peak population, or below the minimum viable population, whichever is higher. It is not extinction and it is not an absolute floor. `collapsed` is the exact complement of `survived`. Extinction implies collapse, but collapse is strictly broader, and the gap between them is where both audits' agreement ends.

Defended collapse rate, as computed here, is:

- Numerator: rows with `collapsed == True`
- Denominator: rows with `defense_active == True`
- Row filter: all rows of the `full_5ac6a2e_<vector>` result set for that vector, no other exclusion
- Splitter: `defense_active`. This is safe: `defense_active` and `parameter_defense_active` agree in every row of every vector.

### Figures for the three disputed vectors

| Vector | Blob SHA at tag | Defended n | Collapsed | Rate |
| --- | --- | ---: | ---: | ---: |
| Sub-Threshold Drift | `f628fb81c29104368d99977bf88ea82faee9f881` | 100 | 1 | 1.00% |
| Measurement Tampering | `fc6e3fa7a1658e4940c32ff2463f0797b6697c4c` | 60 | 1 | 1.67% |
| Bootstrap Subversion | `74f573e679f11f9c13c17dd115665496b3e9bc22` | 100 | 1 | 1.00% |

The pinned-blob audit rounded the measurement tampering figure to 1.7 percent. The exact value is 1.67 percent (1 of 60).

The three collapsing runs are single replicates that ran the full 300-step horizon and did not go extinct:

| Vector | Seed | Replicate | Final pop | Steps | Extinct | Min resilience stock |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| Sub-Threshold Drift | 1692853466 | 18 | 230 | 300 | False | 0.291377 |
| Measurement Tampering | 6963736 | 15 | 225 | 300 | False | 0.290072 |
| Bootstrap Subversion | 477328100 | 7 | 218 | 300 | False | 0.308147 |

These are drawdown events in surviving populations, not near-death runs.

### Extinction cross-check

Required before proceeding. Recomputed from the pinned blobs, extinction matches the agreed record exactly in all eight cells:

| Vector | Defense | n | Extinction | Agreed record |
| --- | --- | ---: | ---: | --- |
| Sub-Threshold Drift | False | 100 | 92.00% | 92.0% match |
| Sub-Threshold Drift | True | 100 | 0.00% | 0.0% match |
| Measurement Tampering | False | 60 | 0.00% | 0.0% match |
| Measurement Tampering | True | 60 | 0.00% | 0.0% match |
| Bootstrap Subversion | False | 100 | 100.00% | 100.0% match |
| Bootstrap Subversion | True | 100 | 0.00% | 0.0% match |
| Sybil Capture | False | 60 | 100.00% | 100.0% match |
| Sybil Capture | True | 60 | 0.00% | 0.0% match |

Attack success rates and mean steps completed also reproduce exactly in all cells. No headline claim moves.

## 3. Recommended publishable phrasing

"0.0 percent defended collapse" should not be published for these three vectors, because it is false. Equally, the corrected figures should not be published as bare percentages, because a reader will hear "1.0 percent collapse" as a small extinction rate, which it is not.

Recommended framing, to be adapted to each document's voice:

> Under the defended adapter state, no run in any of these vectors went extinct. A single run in each of Sub-Threshold Drift (1 of 100), Measurement Tampering (1 of 60), and Bootstrap Subversion (1 of 100) finished below the collapse threshold, which is 65 percent of that run's own peak population. Each of these runs completed the full 300-step horizon with a final population above 200. The defended collapse figures are therefore 1.00 percent, 1.67 percent, and 1.00 percent respectively, and they describe a population drawdown in a surviving civilization rather than a failure of the defense.

Three specific recommendations:

1. State the collapse metric definition wherever a collapse rate is cited. The 65-percent-of-peak basis is not inferable from the word "collapse" and is the entire source of the divergence between the collapse and extinction columns.
2. Report collapse as a count and a denominator, not as a bare percentage. At n of 40 to 100 per cell, a single run moves the rate by 1.0 to 2.5 percentage points, and "1.67 percent" implies a precision the sample size does not support.
3. Do not describe defended outcomes as "0 percent extinction and collapse" or "no extinctions or collapses". That phrasing appears in the local-disk audit and is what the corrected figures contradict. The accurate statement is zero extinction with a small nonzero drawdown rate.

## 4. Locations requiring the corrected number

Flagged only. None of these was edited.

### Tier 1: incorrect figures currently on record, correction required

| Location | What is there |
| --- | --- |
| `simulation/diagnostics/sync_status_YotkoTest_20260720.md:149-158` | The 0.00% collapse table. Three defended cells wrong. |
| `simulation/diagnostics/sync_status_YotkoTest_20260720.md:162` | Prose: measurement tampering has "no extinctions or collapses". The collapse half is wrong. |
| `simulation/diagnostics/sync_status_YotkoTest_20260720.md:165` | Prose: drift defended rows show "0% extinction/collapse". The collapse half is wrong. |
| `snapshots/diagnostics_snapshot.md:8712-8720` | Verbatim snapshot copy of the same wrong table. Regenerate after the source is fixed. |

### Tier 2: correct as written, no change needed

| Location | Status |
| --- | --- |
| `simulation/diagnostics/sync_status_yotko-Legion-T5-26IOB6_20260720.md:110-119` | Correct. Optionally refine 1.7% to 1.67%. |
| `snapshots/diagnostics_snapshot.md:8540-8549` | Correct snapshot copy of the above. |

### Tier 3: no collapse figure published today, but these are where one would land if adopted

These currently publish defended **extinction** (0.0 percent), which is correct and unaffected. They are listed because they are the natural sites for a defended collapse figure and must not silently acquire the 0.0 percent number.

| Location | Content |
| --- | --- |
| `paper/paper_v2_working.md:641` | Section VIII, v2.0 revalidation of the stress test result. |
| `docs/The Lineage Imperative v2.0.md:641` | Assembled copy of the above. |
| `docs/lineage_phi_program_reference.md:1707` and `:1709` | X.9 attack vector v2.0 revalidation, and the drift qualification paragraph. |
| `simulation/diagnostics/sub_threshold_drift_v2_summary.md:54` | Says defended rows show "collapsed=False and survived=True in most cases". Hedged, so not strictly wrong, but vague where a figure now exists. |
| `simulation/diagnostics/attack_vector_revalidation_documentation_edits.md:17` | Proposed replacement text for the paper paragraph. |
| `snapshots/paper_drafts_snapshot.md:816` | Snapshot of paper Section VIII. |
| `snapshots/framework_papers_snapshot.md:664` | Snapshot of the same. |
| `snapshots/docs_snapshot.md:3623` and `:8494` | Snapshots of program reference X.9 and paper Section VIII. |
| `snapshots/diagnostics_snapshot.md:947` and `:8284` | Snapshots of the drift summary and edits document. |

### Advisor document

`simulation/diagnostics/stage15_composite_sweep_advisor_report.md` is the only advisor document in the tree. It contains no attack vector collapse figures and is unaffected. The separate `LINEAGE_IMPERATIVE_ADVISOR.md` has lived outside the repository and is being updated by the operator; see the housekeeping note under Anomaly B4 regarding the naming collision once it lands.

## 5. Anomalies

Reported rather than resolved, per the stop-and-report constraint.

**A1. Inconsistent line endings in committed blobs.** `core.autocrlf` is `true` and there is no `.gitattributes` anywhere in the tree. The drift and bootstrap blobs were committed with CRLF; the measurement tampering and sybil blobs were committed with LF. Consequently a raw byte comparison and a normalized `git hash-object` comparison give opposite answers about which files differ, and a naive provenance check can conclude data divergence where there is none. This did not affect any figure. Recommend adding a `.gitattributes` rule for `*.csv` before the next provenance audit.

**A2. The affected vector set is seven, not three.** Recomputed across all `full_5ac6a2e_` runs at the tag, seven vectors have a defended collapse count above zero. Any correction pass that touches only the three disputed vectors will leave the record incomplete.

| Vector | Defended collapse | Rate | Defended extinction |
| --- | ---: | ---: | ---: |
| Ledger Compromise | 2 of 40 | 5.00% | 0.00% |
| Sybil Capture | 0 of 60 | 0.00% | 0.00% |
| Measurement Tampering | 1 of 60 | 1.67% | 0.00% |
| Evaluator Collusion | 1 of 60 | 1.67% | 0.00% |
| Successor Contamination | 1 of 60 | 1.67% | 0.00% |
| Sub-Threshold Drift | 1 of 100 | 1.00% | 0.00% |
| Bootstrap Subversion | 1 of 100 | 1.00% | 0.00% |
| Biological Veto Capture | 1 of 7200 | 0.01% | 0.00% |
| Opaque Reasoning | 0 of 60 | 0.00% | 0.00% |
| Engineered Fragility | 0 of 60 | 0.00% | 0.00% |

Ledger Compromise at 5.00 percent is the largest defended collapse rate in the set and is more than three times any of the three disputed figures. It was not covered by either audit.

**A3. Successor Contamination undefended shows a 78-point extinction-to-collapse gap.** Undefended extinction is 21.67 percent while undefended collapse is 100.00 percent. Any document that treats the two as interchangeable will misstate this vector badly. Sub-Threshold Drift has the same problem at a smaller scale (92.00 versus 100.00).

**A4. Possible conflict in `essays/the-fine-print.md:82`.** The essay states that "defended and undefended collapse rates for opaque reasoning are symmetric". The v2.0 pinned data show undefended collapse at 100.00 percent and defended at 0.00 percent, which is the opposite of symmetric. The passage does not name its dataset, so it may correctly describe v1.x evidence. This needs an owner decision rather than a unilateral fix. Mirrored at `snapshots/essays_snapshot.md:1852`.

**A5. Smoke and pilot runs sit in the same directories as the authoritative runs.** Each vector directory also contains `gate_smoke_`, `gate2_smoke_`, and `pilot_4b32f13_` result sets. An audit that globs `results.csv` under a vector directory silently mixes them into the full-sweep population, inflating n by 7 per vector and changing defended collapse materially (Sybil Capture goes from 0 of 60 to 5 of 67). This was encountered during this diagnostic and corrected by restricting to the `full_5ac6a2e_` prefix. It is a plausible source of future error.

**A6. Domain Masking is analytic-only, not a failed run.** Its `results.csv` carries schema `attack-v2-analytic-v1` with a single row, `result_type=analytic_only`, and no outcome columns. This matches the documented treatment in program reference X.9 and is not a defect. Noted so that a future audit does not read the missing columns as corruption.

## 6. Reproduction

All figures in this report were computed from the pinned blobs read directly out of the object store, never from the working tree:

```bash
git show attack-v2-revalidation-evidence:data/attack_vector_revalidation_v2/linux/sub_threshold_drift/full_5ac6a2e_sub_threshold_drift/results.csv
```

Row counts at the tag: Sub-Threshold Drift 200, Measurement Tampering 120, Bootstrap Subversion 200, Sybil Capture 120, all matching their manifests and both audits' inventories. Total live Monte Carlo rows across the ten live vectors: 9,900, matching the count published in paper Section VIII and program reference X.9.

---

## 7. Addendum, Stage 1: Opaque Reasoning collapse claim

Status: **stop condition met.** The 0 percent defended and 100 percent undefended asymmetry is confirmed. Findings are recorded here and Stage 1 halts. No "irreducible comprehension gap" framing was rewritten anywhere. That reclassification is an operator decision and is deliberately left open.

### 7.1 v2.0 figures

Source: pinned blob `e38db559812cf486448d9833c2845d0edec55703`, 120 rows. The working tree copy is byte-identical to the blob (another CRLF-committed file, consistent with Anomaly A1).

| Defense state | n | Attack success | Collapse | Extinction | Horizon | Final population |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Undefended | 60 | 60/60 = 100.00% | 60/60 = 100.00% | 60/60 = 100.00% | 0 of 60 reached 300 steps, mean 105.15 | all runs ended at 0 |
| Defended | 60 | 0/60 = 0.00% | 0/60 = 0.00% | 0/60 = 0.00% | 60 of 60 reached 300 steps | mean 311.4, min 233, max 379 |

Answering the Stage 1 questions directly:

- **(a) Collapse:** 100.00 percent undefended, 0.00 percent defended.
- **(b) Attack success:** 100.00 percent undefended, 0.00 percent defended.

Both are maximally asymmetric. This vector shows the largest defense effect in the entire set: every undefended run reached population zero, and every defended run finished the full horizon with a healthy population.

### 7.2 What the "symmetric" claim described

The claim originates in `simulation/run_comprehension_gap_sweep.py:6-7`: "symmetric opaque-reasoning collapse rates observed in Scenarios 25-26". It describes **collapse**, not attack success.

Checked against the v1.x primary record, `data/comprehensive_adversarial_sweeps_v1x2_phi.csv`, which is the baseline the pinned `opaque_reasoning_v2_summary.md` section 4 itself names. Opaque_Reasoning, 600 rows:

| Phi | Undefended collapse | Defended collapse | Delta |
| ---: | ---: | ---: | ---: |
| 1 | 60.00% | 3.33% | 56.67 |
| 5 | 61.67% | 1.67% | 60.00 |
| 10 | 61.67% (37/60) | 1.67% (1/60) | 60.00 |
| 15 | 68.33% | 0.00% | 68.33 |
| 25 | 60.00% | 0.00% | 60.00 |

Collapse was never symmetric for this vector under v1.x. Attack success under v1.x is 100.00 percent undefended and 0.00 percent defended at every phi, so it is not symmetric either. The claim matches neither v1.x collapse, nor v1.x attack success, nor v2.0 collapse.

The two v1.x vectors that genuinely are symmetric on collapse at phi=10 are **Engineered Fragility** (100.00 / 100.00) and **Sub-Threshold Drift** (100.00 / 100.00). Neither is Opaque Reasoning.

The one dataset in the tree where opaque reasoning collapse is symmetric is `data/comprehension_gap_sweep.csv`: 0.00 percent undefended and 0.00 percent defended at all seven convergence strengths. That is a symmetry at zero. No run in that sweep collapsed, none went extinct, and all 2,800 survived with mean final population 762.5. A symmetry produced by the total absence of collapse events cannot support the reading that the defense is ineffective, because nothing was there for the defense to prevent.

### 7.3 Stage 1 anomalies

**B1. Scenario mis-citation.** Opaque Reasoning is Scenarios 21-22 (`docs/Simulation_Scenarios.md:145` and `:151`). Scenarios 25-26 are Evaluator Collusion and Methodological Diversity (`:169`, `:175`). The sweep script attributes the opaque-reasoning finding to Scenarios 25-26. Separately, the script titles itself "Scenarios 31-32", which the catalog assigns to Engineered Fragility and Resilience Monitoring (`:193`, `:199`). Both citations appear wrong.

**B2. The essay says unperformed work that has been performed.** `essays/the-fine-print.md:82` states that resolving the two interpretations "requires simulation configurations that independently vary the convergence forces and the opacity threshold, which has not yet been performed." `data/comprehension_gap_sweep.csv` exists with 2,800 rows on exactly that grid.

**B3. The comprehension gap sweep did not move its independent variable.** `max_opacity_reached` is constant at 0.8940 in all 2,800 rows, identical at every convergence_strength from 0.0 to 2.0. Convergence strength was the axis intended to control whether the system enters the opaque regime, and the script's own interpretation guide predicts that high convergence strength should keep `max_opacity_reached` below the defense threshold. It never varies. Meanwhile 2,100 of 2,800 runs exceeded their opacity threshold and the defense fired in 1,050, yet zero runs collapsed. As recorded, this sweep cannot discriminate between the two interpretations it was built to test. Flagged, not resolved.

**B4. CLOSED, not an anomaly.** Originally filed because the advisor document referenced in the Stage 1 brief could not be found in the working tree. Resolved by operator ruling, 2026-08-09: `LINEAGE_IMPERATIVE_ADVISOR.md` has lived outside the repository, so its absence here is expected. The claim in question was verified against the advisor text at the advisor layer and is corrected in an updated version that the operator is committing at the repository root. No search, creation, or edit of that document is in scope for this diagnostic.

Retained from the original finding, because it is still true and still useful: within the repository, the symmetric claim appears in exactly two places, both flagged and both untouched pending the operator decision on framing. Those are `essays/the-fine-print.md:82` (mirrored at `snapshots/essays_snapshot.md:1852`) and `simulation/run_comprehension_gap_sweep.py:6-7` (mirrored at `snapshots/code_snapshot.md:7641-7642`).

**Housekeeping, advisor document collision risk.** The only file in the repository that currently presents itself as an advisor document is:

> `simulation/diagnostics/stage15_composite_sweep_advisor_report.md`

It is unrelated to the attack vector arc. It covers the Stage 15 composite sweep, and it contains no reference to opaque reasoning, to comprehension, or to a Known Limitations section. It is named here so that when the updated `LINEAGE_IMPERATIVE_ADVISOR.md` lands at the repository root, the operator can supersede, rename, or remove this file deliberately, rather than leaving the repository carrying two documents that both read as the advisor document.

---

## 8. Addendum, Stage 2: Authoritative collapse table, all thirteen vectors

**This table is the sole citable source for collapse figures in the v2.0 revalidation arc.** Any collapse figure appearing in any other document should be traced to this table or removed.

### Metric definition

`collapsed` is written by `simulation/run_attack_vector_revalidation_v2.py:419` as `final_population < collapse_threshold`, where `collapse_threshold = max(min_viable_population, int(0.65 * peak_population))`. Collapse is therefore a **relative population drawdown**: the run ended below 65 percent of its own peak population, or below the minimum viable population, whichever is higher. It is the exact complement of `survived`. It is **not** extinction, which is `final_population == 0`. Extinction implies collapse; collapse does not imply extinction. Extinction rates are shown alongside for contrast precisely because the two diverge, in one case by 78 percentage points.

### Exclusion rule

Computed from the pinned blobs at tag `attack-v2-revalidation-evidence` (commit `6d33c90`), read out of the object store rather than the working tree. **Included:** result CSVs whose run directory carries the `full_5ac6a2e_` prefix. **Excluded:** all `gate_smoke_`, `gate2_smoke_`, `pilot_4b32f13_`, and `test_dm_full` run directories, which share the same vector directories as the authoritative runs. Selection is by exact run-directory prefix, never by globbing `results.csv` under a vector directory (see Anomaly A5, and the manifest added in Commit B). Total included: 9,900 rows across ten live vectors, matching the count published in paper Section VIII and program reference X.9.

### Table

| # | Vector | Undefended collapse | Undefended extinction | Defended collapse | Defended extinction | Horizon completion, collapsing runs |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | Biological Veto Capture | 0/1500 = 0.00% | 0/1500 = 0.00% | 1/7200 = 0.01% | 0/7200 = 0.00% | 1 of 1 at full horizon |
| 2 | Bootstrap Subversion | 100/100 = 100.00% | 100/100 = 100.00% | 1/100 = 1.00% | 0/100 = 0.00% | 1 of 101 at full horizon |
| 3 | Engineered Fragility | 0/60 = 0.00% | 0/60 = 0.00% | 0/60 = 0.00% | 0/60 = 0.00% | no collapsing runs |
| 4 | Evaluator Collusion | 60/60 = 100.00% | 60/60 = 100.00% | 1/60 = 1.67% | 0/60 = 0.00% | 1 of 61 at full horizon |
| 5 | Ledger Compromise | 40/40 = 100.00% | 40/40 = 100.00% | 2/40 = 5.00% | 0/40 = 0.00% | 2 of 42 at full horizon |
| 6 | Measurement Tampering | 0/60 = 0.00% | 0/60 = 0.00% | 1/60 = 1.67% | 0/60 = 0.00% | 1 of 1 at full horizon |
| 7 | Opaque Reasoning | 60/60 = 100.00% | 60/60 = 100.00% | 0/60 = 0.00% | 0/60 = 0.00% | 0 of 60 at full horizon |
| 8 | Sub-Threshold Drift | 100/100 = 100.00% | 92/100 = 92.00% | 1/100 = 1.00% | 0/100 = 0.00% | 9 of 101 at full horizon |
| 9 | Successor Contamination | 60/60 = 100.00% | 13/60 = 21.67% | 1/60 = 1.67% | 0/60 = 0.00% | 48 of 61 at full horizon |
| 10 | Sybil Capture | 60/60 = 100.00% | 60/60 = 100.00% | 0/60 = 0.00% | 0/60 = 0.00% | 0 of 60 at full horizon |
| 11 | Domain Masking | N/A, analytic only | N/A, analytic only | N/A, analytic only | N/A, analytic only | N/A, no Monte Carlo rows |
| 12 | Biological Validator Obsolescence | N/A, not implemented | N/A, not implemented | N/A, not implemented | N/A, not implemented | N/A, Scenarios 33-34 unimplemented |
| 13 | Legitimate Disagreement | N/A, not implemented | N/A, not implemented | N/A, not implemented | N/A, not implemented | N/A, Scenarios 35-36 unimplemented |

Row 11, Domain Masking, produced a single analytic row under schema `attack-v2-analytic-v1` with `result_type=analytic_only` and no outcome columns. Spectral entropy leaves no non-degenerate live masking intervention under the audited architecture, so there is nothing to collapse. This is a documented architectural closure, not a missing run.

Rows 12 and 13 are the two irreducible limitations recorded as unimplemented in `docs/Simulation_Scenarios.md`. They have no simulation substrate and therefore no collapse figure of any kind.

### Notes on the table

1. **Every defended collapse ran the full horizon.** All eight defended collapse events across the seven affected vectors completed 300 of 300 steps, with final populations of 218, 225, 230, 243, 243, 246, 257, and 366. Not one is a near-death run. Defended collapse in this dataset means a surviving civilization that drew down past 65 percent of its own peak, and it should never be reported in a way that suggests otherwise.
2. **Defended extinction is 0.00 percent in every vector without exception.** This is the figure the paper and program reference already publish, and it is unaffected by this correction.
3. **Collapse and extinction diverge sharply in two vectors.** Successor Contamination undefended is 100.00 percent collapse against 21.67 percent extinction, a 78-point gap. Sub-Threshold Drift undefended is 100.00 percent collapse against 92.00 percent extinction. Treating the two metrics as interchangeable misstates these two badly, and was the failure mode that made the original discrepancy hard to see.
4. **Biological Veto Capture has an intentionally asymmetric denominator** (1,500 undefended against 7,200 defended) because the defended grid sweeps three defense modes. Its 0.01 percent defended collapse is a single run out of 7,200 and should not be compared like-for-like against the standard 60-row and 100-row cells.
5. **Ledger Compromise carries the largest defended collapse rate at 5.00 percent**, five times the Sub-Threshold Drift and Bootstrap Subversion figures and three times Measurement Tampering. Neither of the two original audits covered it. Any correction pass that touches only the three originally disputed vectors leaves the larger figure unstated.

---

## 9. Addendum, Stage 3 Commit A: beat-by-beat diff review

Every edit in Commit A is listed below with before and after text, recorded here before the commit is made. Opaque Reasoning framing is deliberately absent from this commit regardless of the Stage 1 findings.

Handling note for the dated audit artifact: `sync_status_YotkoTest_20260720.md` is a historical machine audit. Rather than silently restating what it never said, the wrong figures are corrected inline, marked `(corrected)`, and preceded by a dated correction notice that states the original values and the defect. The record stays honest about having been wrong.

### Edit 1. `simulation/diagnostics/sync_status_YotkoTest_20260720.md:147`, correction notice

Before:

> Rates use the CSV boolean columns directly. All four files contain both `extinct` and `collapsed`.

After: the same sentence, followed by a blockquote correction notice dated 2026-08-09 stating that the three defended collapse figures were originally 0.00 percent, that the cause was the PowerShell 5.1 single-match scalar collapse returning null instead of 1, that extinction and attack success were unaffected because no cell in those columns has a count of one, and pointing to this report.

### Edit 2. Same file, table rows 152, 154, 156, three cells

Column order is Vector, Defense, n, Attack success, Extinction, Collapse, Mean steps completed. The Collapse column is the one that changes in each row.

Before:

```text
| Sub-Threshold Drift | True | 100 | 100.00% | 0.00% | 0.00% | 300.00 |
| Measurement Tampering | True | 60 | 0.00% | 0.00% | 0.00% | 300.00 |
| Bootstrap Subversion | True | 100 | 0.00% | 0.00% | 0.00% | 300.00 |
```

After:

```text
| Sub-Threshold Drift | True | 100 | 100.00% | 0.00% | 1.00% (corrected) | 300.00 |
| Measurement Tampering | True | 60 | 0.00% | 0.00% | 1.67% (corrected) | 300.00 |
| Bootstrap Subversion | True | 100 | 0.00% | 0.00% | 1.00% (corrected) | 300.00 |
```

The Extinction and Collapse columns sit adjacent in this table, so a distinction paragraph is added immediately below it giving both formulas and stating that extinction implies collapse but not the reverse.

**Rendering defect in this record, found and fixed 2026-08-09.** The three rows above were originally presented as a three-column Before and After table whose cells contained unescaped pipe characters inside backticks. Markdown splits a table row at every pipe regardless of backticks, so each row overflowed its three declared columns: the rendered After column displayed `0.00%`, a fragment of the Before cell, and the `(corrected)` markers landed in overflow columns that most renderers drop. The raw text always carried the correct values and the committed file was never wrong, verified against `git show b3157d9:simulation/diagnostics/sync_status_YotkoTest_20260720.md`, which reads 1.00, 1.67, and 1.00 percent with markers intact. Only the presentation of this record was defective. Fenced blocks replace the table because they cannot be broken by pipes.

### Edit 3. Same file, line 162, Measurement Tampering disposition

Before:

> Measurement Tampering: the undefended attack always succeeds, but there are no extinctions or collapses and all rows complete 300 steps.

After:

> Measurement Tampering: the undefended attack always succeeds, and there are no extinctions in either defense state. Undefended collapse is 0 of 60; defended collapse is 1 of 60 (1.67 percent), a single drawdown run that completed all 300 steps at final population 225.

### Edit 4. Same file, line 163, Bootstrap Subversion disposition

Before:

> the undefended rows show 100% extinction and collapse, with mean completion at 106.21 of 300 steps.

After:

> the undefended rows show 100 percent extinction and, separately, 100 percent collapse; the two coincide here but are distinct measures, extinction being zero population and collapse being a drawdown below 65 percent of peak. Mean completion is 106.21 of 300 steps. Defended collapse is 1 of 100 (1.00 percent) at full horizon.

### Edit 5. Same file, line 164, Sybil Capture disposition

Before:

> the undefended rows show 100% extinction and collapse, with mean completion at 104.55 steps.

After:

> the undefended rows show 100 percent extinction and, separately, 100 percent collapse; the two coincide here but are distinct measures. Mean completion is 104.55 steps. Defended collapse is 0 of 60.

### Edit 6. Same file, line 165, Sub-Threshold Drift disposition

Before:

> Undefended rows have 92% `extinct=True` and 100% `collapsed=True`; defended rows have 0% extinction/collapse and complete all 300 steps.

After:

> Undefended rows have 92 percent `extinct=True` and 100 percent `collapsed=True`, and that 8-point gap is itself the reason the two measures must not be conflated. Defended rows have 0 percent extinction and 1.00 percent collapse (1 of 100), the single collapsing run completing all 300 steps at final population 230.

### Edit 7. `paper/paper_v2_working.md:641`, Section VIII guard

Before, unchanged text retained:

> That last figure requires its qualification: the defense nonetheless prevents catastrophic outcome, with undefended runs reaching a 92.0 percent extinction rate while defended runs reach 0.0 percent extinction and complete the full simulation horizon.

After: the same sentence, followed by an inserted guard sentence stating that extinction and collapse are distinct measures, that defended collapse for this vector is 1.00 percent (1 of 100) with collapse defined inline as a final population below 65 percent of that run's own peak, that the single collapsing run completed the full horizon, and that section 8 of this report is the sole citable source for collapse figures.

### Edit 8. `docs/The Lineage Imperative v2.0.md:641`

Identical text and identical guard insertion. Verified byte-identical to the paper line before editing, so the two stay in sync.

### Edit 9. `docs/lineage_phi_program_reference.md:1709`, X.9 guard

Before, unchanged text retained:

> The defense prevents catastrophic outcome; it does not prevent the transient breach.

After: the same sentence, followed by a guard stating that extinction and collapse must not be reported as one quantity, giving defended collapse of 1.00 percent (1 of 100) with the metric inline, noting that defended collapse is nonzero in seven of the ten live vectors with Ledger Compromise largest at 5.00 percent, and directing all collapse figures to section 8 of this report with an explicit instruction not to quote 0.0 percent without checking there.

### Edit 10. `simulation/diagnostics/sub_threshold_drift_v2_summary.md:54`, replace the vague hedge

Before:

> complete the full 300 steps with collapsed=False and survived=True in most cases (rates computed from the raw results CSV, 2026-07-20, cross-checked on both machines).

After:

> complete the full 300 steps with `collapsed=False` and `survived=True` in 99 of 100 defended rows. The single exception is a drawdown run that completed all 300 steps at final population 230, giving a defended collapse rate of 1.00 percent (1 of 100). Collapse here means a final population below 65 percent of that run's own peak and is a distinct measure from extinction, which is 0.0 percent defended (rates recomputed from the pinned CSV at tag `attack-v2-revalidation-evidence`, 2026-08-09; the 2026-07-20 local-disk figure of 0.0 percent defended collapse was wrong).

This is the "in most cases" hedge flagged in Tier 3. It was not false, but it stood where a figure now exists.

### Edit 11. `simulation/diagnostics/attack_vector_revalidation_documentation_edits.md:17`, guard on proposed replacement text

Before, unchanged text retained:

> The defense prevents population extinction but does not prevent the transient threshold breach that triggers the success flag.

After: the same sentence, followed by a guard giving defended collapse of 1.00 percent (1 of 100) with the metric inline and requiring any collapse figure in the proposed replacement text to come from section 8 of this report. This matters because this document is a staging area for paper edits, and it is the most likely route by which a wrong figure would reach the paper.

### Snapshots

`snapshots/diagnostics_snapshot.md` and the other eight snapshot files are generated artifacts produced by `scripts/generate_project_knowledge_snapshots.py`. They are regenerated after the source edits above rather than hand-edited, so the Tier 1 snapshot copy at `diagnostics_snapshot.md:8712` is corrected by regeneration. Note that regeneration also picks up nine pre-existing uncommitted header changes (repository path and timestamp lines only, two lines per file), which predate this work and are carried into the commit as a side effect.

### Not in this commit

Opaque Reasoning framing at `essays/the-fine-print.md:82` and `simulation/run_comprehension_gap_sweep.py:6-7` is untouched, as are Stage 1 anomalies B1 through B4. Those await an operator decision.

---

## 10. Amendment: complete the inline metric definition

The inline collapse definitions written in Commit A stated only the 65 percent clause and omitted the minimum viable population floor. The authoritative metric has two terms and takes the larger of them. A reader given only the 65 percent clause would compute the wrong threshold for any run whose peak population was small enough that the floor binds. The omission did not affect any published figure, because all figures in this report were computed from the `collapsed` column as written by the simulator rather than from the prose definition, but the prose was incomplete as a specification.

Authoritative form, unchanged since `simulation/run_attack_vector_revalidation_v2.py:419`:

```python
collapse_threshold = max(model.min_viable_population, int(0.65 * peak_population))
collapsed = final_population < collapse_threshold
```

Standard replacement phrasing adopted at every site, matching the wording already used at `simulation/diagnostics/attack_vector_revalidation_inventory.md:54`:

> a final population below the larger of the minimum viable population and 65 percent of that run's own peak

### Sites amended

**`paper/paper_v2_working.md:641`** and **`docs/The Lineage Imperative v2.0.md:641`**, identical text, verified byte-identical again after editing (2,023 characters each).

Before:

> where collapse means a final population below 65 percent of that run's own peak rather than a population of zero

After:

> where collapse means a final population below the larger of the minimum viable population and 65 percent of that run's own peak, rather than a population of zero

**`docs/lineage_phi_program_reference.md:1709`**

Before:

> collapse being a final population below 65 percent of that run's own peak rather than a population of zero

After:

> collapse being a final population below the larger of the minimum viable population and 65 percent of that run's own peak, rather than a population of zero

**`simulation/diagnostics/sub_threshold_drift_v2_summary.md:54`**

Before:

> Collapse here means a final population below 65 percent of that run's own peak and is a distinct measure from extinction

After:

> Collapse here means a final population below the larger of the minimum viable population and 65 percent of that run's own peak, and is a distinct measure from extinction

**`simulation/diagnostics/attack_vector_revalidation_documentation_edits.md:17`**

Before:

> collapse being a final population below 65 percent of that run's own peak.

After:

> collapse being a final population below the larger of the minimum viable population and 65 percent of that run's own peak.

**`simulation/diagnostics/sync_status_YotkoTest_20260720.md`, Bootstrap Subversion disposition bullet.** Not named in the amendment brief, but it is a Commit A edit carrying the same incomplete inline definition, so it is amended for consistency under the same dated-artifact notice already covering that file.

Before:

> extinction being zero population and collapse being a drawdown below 65 percent of peak.

After:

> extinction being zero population and collapse being a drawdown below the larger of the minimum viable population and 65 percent of peak.

### Sites verified as already complete, not amended

- The distinction paragraph below the `sync_status_YotkoTest_20260720.md` table, line 162, already carries the full `max(min_viable_population, int(0.65 * peak_population))` form.
- The metric statement above the section 8 table, line 269, already carries the full form.
- `simulation/diagnostics/attack_vector_revalidation_inventory.md:54` already carries the full form in prose and supplied the phrasing used above.

A sweep of the five guard sites plus the sync_status dispositions confirms no partial 65 percent definition remains at any of them.
