# v2.1 step 3: dual attack-success metric

The new pure-function module and the requested evidence and synthetic-fixture validation are complete. No simulation or model steps were run. No quantity here is measured on the post-step-1-and-2 substrate. Figures computed from committed pre-repair evidence are not comparable to any future post-repair measurement. No corrected published figure is derived.

## T0. Preconditions and environment observations

| Check | Read result | Result |
| --- | --- | --- |
| a. Branch | `git rev-parse --abbrev-ref HEAD` returned `main`, exit 0 | PASS |
| b. Ancestry | `git merge-base --is-ancestor 5095f77827aadf37b19ccca04b0985f1b2f2060a HEAD` exited 0 | PASS |
| c. Tracked status | `git status --porcelain --untracked-files=no` exited 0 with zero stdout lines | PASS |
| d. New module | simulation/attack_metrics_v2.py did not exist | PASS |
| e. Runner provenance | LF-normalized SHA256 recorded before work and again at completion | PASS |

HEAD read during T0: `5095f77827aadf37b19ccca04b0985f1b2f2060a`. Read-only Git commands used `GIT_OPTIONAL_LOCKS=0`. The exact requested tracked-only status form was used.

T0 stderr warning, recorded without halting:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

The known CRLF worktree/LF blob condition and cache/global-ignore permission conditions were accepted and not repaired. Every committed CSV was retrieved through `git cat-file blob <commit>:<path>`. No working-tree evidence CSV was parsed, and no worktree bytes were compared with Git blob bytes. Normalized hashes use an in-memory LF representation; no source file was normalized in place.

## T1. Reproduction before module creation

The source is the committed `simulation/diagnostics/veto_floor2_runs.csv` blob at HEAD `5095f77827aadf37b19ccca04b0985f1b2f2060a`, Git blob SHA1 `fc6d781983ef88d42af7ee1b6aa071e8ec11a721`. Counted using csv.DictReader excluding its header: 900 rows, with 300 each in AS_PUBLISHED, ZERO_STRENGTH, and ZERO_DEPENDENCY. Each arm has 300 unique seeds, and both control seed sets match AS_PUBLISHED exactly.

Differences are AS_PUBLISHED minus the named control on yield_condition_blocked_count. Standard error uses sample standard deviation, ddof = 1, divided by sqrt(n). The following quantities were calculated from the committed rows before the module was written. Totals are shown as treatment followed by control, not as rates.

| Control | Pairs | Mean difference | Paired standard error | t statistic | Block totals: treatment / control | Vote totals: treatment / control |
| --- | --- | --- | --- | --- | --- | --- |
| ZERO_DEPENDENCY | 300 | 0.059999999999999998 | 0.015271602751943064 | 3.9288607079807631 | 43 / 25 | 343 / 325 |
| ZERO_STRENGTH | 300 | 0.059999999999999998 | 0.015271602751943064 | 3.9288607079807631 | 43 / 25 | 343 / 325 |

The expected rounded values matched: mean difference 0.060000, paired standard error 0.015272, and t statistic 3.9289. The two control comparisons are exactly equal in all recorded quantities. Counted D6 identity matches, yield_condition_met_count == 1 + yield_condition_blocked_count: 900 of 900. Exception count: 0.

T1 completed at `2026-09-09T13:14:54.391296+00:00`. The production module was created later, at `2026-09-09T13:16:20.116920+00:00`. [dual_metric_t1.json](dual_metric_t1.json) holds the gate results and [dual_metric_t1_pairs.csv](dual_metric_t1_pairs.csv) holds all 600 pair rows, 300 for each control.

## T2. New pure-function module

[attack_metrics_v2.py](../attack_metrics_v2.py) provides:

- `action_change_count(records)`: returns the tuple `(n_runs, n_action_modified)` using only the existing recorded action_modified field. CSV Boolean text is parsed explicitly, so the string False is not treated as true. Missing or invalid flags raise.
- `paired_difference(treatment, control, field)`: returns a named mapping containing n_pairs, mean_difference, paired_standard_error, t_statistic, and t_statistic_note. Exact seed type and value matching is required, with no seed coercion or silent intersection. Duplicate seeds, unmatched seeds in either direction, and fewer than two pairs raise. Non-finite values raise. At exactly zero standard error, t is null and the note states that t is undefined.

The module contains pure functions, with no model imports, simulation imports, I/O, or mutable global state. Its docstring names D5 and D6 as the reasons it does not compute or return a ratio of two measured counts. The retired ratios and Wilson intervals requested for contrast below are calculated in the diagnostic harness only.

## T3a through T3d. Module validation

The module reproduced every T1 paired statistic exactly against both control arms. There was no tolerance-based substitution. Both outputs are retained in [dual_metric_module_controls.json](dual_metric_module_controls.json).

The positive fixture used seeds 11, 22, 33, and 44, control counts 0, 2, 5, and 11, and a treatment offset of exactly 4 on every pair. Control rows were reversed to exercise seed-based matching. The negative fixture paired identical counts, also with reversed row order.

| Synthetic fixture | Pairs | Mean difference | Paired standard error | t statistic | Returned note |
| --- | --- | --- | --- | --- | --- |
| Constant offset | 4 | 4 | 0 | null | Paired standard error is exactly zero; t statistic is undefined. |
| Identical arms | 4 | 0 | 0 | null | Paired standard error is exactly zero; t statistic is undefined. |

Adding treatment seed 55 without a control match raised ValueError, as required. The mirror control-only case, a duplicate seed, and integer-versus-string seed mismatch also raised. Boolean parsing returned `(8, 4)` on eight fixture records; empty input returned `(0, 0)`; an invalid flag raised. All controls passed.

## T3e. D6 contrast on the same committed rows

The retired AS_PUBLISHED per-run blocked/met quantity has the following counted distribution:

| Retired value, exact | Decimal value | Number of runs |
| --- | --- | --- |
| 0 | 0 | 263 |
| 1/2 | 0.5 | 32 |
| 2/3 | 0.66666666666666663 | 4 |
| 3/4 | 0.75 | 1 |

Counted values strictly between 0 and 0.5: 0. The ladder is a property of the retired blocked/met quantity.

The same committed data under paired_difference gives:

| Control | Pairs | Mean block-count difference | Paired standard error | t statistic |
| --- | --- | --- | --- | --- |
| ZERO_DEPENDENCY | 300 | 0.059999999999999998 | 0.015271602751943064 | 3.9288607079807631 |
| ZERO_STRENGTH | 300 | 0.059999999999999998 | 0.015271602751943064 | 3.9288607079807631 |

## T3f. D5 contrast

The following per-vote rates and Wilson 95 percent intervals were calculated from the committed arm totals in the diagnostic. The Wilson normal critical value is `1.9599639845400536`.

| Arm | Blocks | Votes | Per-vote rate | Wilson 95 percent lower | Wilson 95 percent upper |
| --- | --- | --- | --- | --- | --- |
| AS_PUBLISHED | 43 | 343 | 0.12536443148688048 | 0.09441913435902409 | 0.16460831618326899 |
| ZERO_STRENGTH | 25 | 325 | 0.076923076923076927 | 0.052643757395406734 | 0.1110869930208661 |

Wilson intervals overlap: yes. Paired t for AS_PUBLISHED minus ZERO_STRENGTH on per-run block counts: `3.9288607079807631`.

## T3g. Ten-vector comparable metric, counts only

The selection source was the committed [attack_vector_revalidation_manifest.md](attack_vector_revalidation_manifest.md), Git blob SHA1 `f0ff7de14d1558c421cd9bd4895a18101c8b83e3`. Its evidence tag `attack-v2-revalidation-evidence` resolves to `6d33c905db18842f68e59b4148f65c5e6a1a62a3`. Each listed live run directory was resolved uniquely within that Git tree. No glob selected a result file. Every CSV blob SHA matched the manifest before row parsing, and every counted row total matched the manifest.

The 13 live-result CSV files contribute 9,900 recorded runs. Domain masking was excluded because the manifest identifies it as analytic, 0 MC. Defended means the recorded defense_active field is True; undefended means False. Each result below is returned by action_change_count from the recorded action_modified field. No rate is calculated.

| Vector | Defense arm | n_runs | n_action_modified |
| --- | --- | --- | --- |
| biological_veto_capture | Undefended | 1500 | 0 |
| biological_veto_capture | Defended | 7200 | 0 |
| bootstrap_subversion | Undefended | 100 | 100 |
| bootstrap_subversion | Defended | 100 | 0 |
| engineered_fragility | Undefended | 60 | 60 |
| engineered_fragility | Defended | 60 | 0 |
| evaluator_collusion | Undefended | 60 | 60 |
| evaluator_collusion | Defended | 60 | 0 |
| ledger_compromise | Undefended | 40 | 40 |
| ledger_compromise | Defended | 40 | 0 |
| measurement_tampering | Undefended | 60 | 0 |
| measurement_tampering | Defended | 60 | 0 |
| opaque_reasoning | Undefended | 60 | 60 |
| opaque_reasoning | Defended | 60 | 0 |
| sub_threshold_drift | Undefended | 100 | 100 |
| sub_threshold_drift | Defended | 100 | 100 |
| successor_contamination | Undefended | 60 | 60 |
| successor_contamination | Defended | 60 | 0 |
| sybil_capture | Undefended | 60 | 60 |
| sybil_capture | Defended | 60 | 0 |

The count table is retained in [dual_metric_vector_counts.csv](dual_metric_vector_counts.csv).

## T4. Runner hash and provenance

| Runner hash, LF-normalized SHA256 | Value |
| --- | --- |
| T0 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 |
| Completion | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 |

The required runner hash is unchanged. This is the explicit T0e/T4 check; the operator performs the containment diff.

Machine: `YOTKOTEST`. HEAD: `5095f77827aadf37b19ccca04b0985f1b2f2060a`. Python: `3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]`. Installed NumPy: `2.4.4`, read from package metadata. The calculations use Python statistics and math; no NumPy calculation, model step, simulation import from the existing mechanism, or sweep was required. The only production module loaded for validation was the new pure-function module.

One evidence-analysis process ran each sequential stage. Simulation workers used: 0. Bytecode writes were disabled. The Python writable-open guard allowed only the new module, dual_metric_ artifacts in simulation/diagnostics, and the explicit os.devnull exemption. No out-of-scope writable-open attempt was recorded.

| Repository Python module | SHA256, LF-normalized basis |
| --- | --- |
| simulation/attack_metrics_v2.py | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 |
| simulation/diagnostics/dual_metric_harness.py | f977339bfc1014e287774b33bec6be12aae4ea6da498397b1058232e0838fc7b |

Raw and LF-normalized module hashes are labeled separately in [dual_metric_validation.json](dual_metric_validation.json) and the manifest. The harness was extended after T1 with the module and corpus controls; T1 itself was recorded before the production module existed.

### Committed evidence inventory

| Evidence path | Commit | Git blob SHA1 | Counted CSV rows |
| --- | --- | --- | --- |
| simulation/diagnostics/veto_floor2_runs.csv | 5095f77827aadf37b19ccca04b0985f1b2f2060a | fc6d781983ef88d42af7ee1b6aa071e8ec11a721 | 900 |
| simulation/diagnostics/attack_vector_revalidation_manifest.md | 5095f77827aadf37b19ccca04b0985f1b2f2060a | f0ff7de14d1558c421cd9bd4895a18101c8b83e3 | Not CSV |
| data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard0of4/results.csv | 6d33c905db18842f68e59b4148f65c5e6a1a62a3 | 3334d7b4ffcac08c708ac3e43f48c4efeb38e9a2 | 2164 |
| data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard1of4/results.csv | 6d33c905db18842f68e59b4148f65c5e6a1a62a3 | 4d6c83821bad99368bd94c6b1469202d2ca51bb9 | 2102 |
| data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard2of4/results.csv | 6d33c905db18842f68e59b4148f65c5e6a1a62a3 | 330369c806bc1db05ceb385afe177fe8d252c63a | 2321 |
| data/attack_vector_revalidation_v2/laptop/evaluator_collusion/full_5ac6a2e_evaluator_collusion/results.csv | 6d33c905db18842f68e59b4148f65c5e6a1a62a3 | 173582bbabdf37fe35df0dfdb346e5dc3e14a97c | 120 |
| data/attack_vector_revalidation_v2/laptop/measurement_tampering/full_5ac6a2e_measurement_tampering/results.csv | 6d33c905db18842f68e59b4148f65c5e6a1a62a3 | fc6e3fa7a1658e4940c32ff2463f0797b6697c4c | 120 |
| data/attack_vector_revalidation_v2/laptop/successor_contamination/full_5ac6a2e_successor_contamination/results.csv | 6d33c905db18842f68e59b4148f65c5e6a1a62a3 | 9b94dc455569abf645b0666fed936e259161e78d | 120 |
| data/attack_vector_revalidation_v2/laptop/sybil_capture/full_5ac6a2e_sybil_capture/results.csv | 6d33c905db18842f68e59b4148f65c5e6a1a62a3 | dc56fd9402c98be2dc453cf5df8215fc28ca6278 | 120 |
| data/attack_vector_revalidation_v2/linux/biological_veto_capture/full_5ac6a2e_veto_shard3of4/results.csv | 6d33c905db18842f68e59b4148f65c5e6a1a62a3 | a790f7569e6a27581a2ef78424376d0bf108743f | 2113 |
| data/attack_vector_revalidation_v2/linux/bootstrap_subversion/full_5ac6a2e_bootstrap_subversion/results.csv | 6d33c905db18842f68e59b4148f65c5e6a1a62a3 | 74f573e679f11f9c13c17dd115665496b3e9bc22 | 200 |
| data/attack_vector_revalidation_v2/linux/engineered_fragility/full_5ac6a2e_engineered_fragility/results.csv | 6d33c905db18842f68e59b4148f65c5e6a1a62a3 | 4fb28e596ee8fa10c14f341cb97ebd1bddfc5a7a | 120 |
| data/attack_vector_revalidation_v2/linux/ledger_compromise/full_5ac6a2e_ledger_compromise/results.csv | 6d33c905db18842f68e59b4148f65c5e6a1a62a3 | d128c0bbca8353f7fe300d2e7b4aa98abcad619f | 80 |
| data/attack_vector_revalidation_v2/linux/opaque_reasoning/full_5ac6a2e_opaque_reasoning/results.csv | 6d33c905db18842f68e59b4148f65c5e6a1a62a3 | e38db559812cf486448d9833c2845d0edec55703 | 120 |
| data/attack_vector_revalidation_v2/linux/sub_threshold_drift/full_5ac6a2e_sub_threshold_drift/results.csv | 6d33c905db18842f68e59b4148f65c5e6a1a62a3 | f628fb81c29104368d99977bf88ea82faee9f881 | 200 |

[dual_metric_manifest.json](dual_metric_manifest.json) enumerates every output with SHA256 on LF-normalized bytes and CSV row counts using csv.DictReader excluding headers. Non-CSV row counts are null. The manifest self-entry has a null hash to avoid self-reference; its final LF-normalized digest is emitted separately. Committed inputs are inventoried separately from outputs, including the SHA1 of every evidence blob read.

All T1 and T3 gates passed. No quantity in this report was measured on the post-step-1-and-2 model substrate, and no corrected figure for a published number was derived.
