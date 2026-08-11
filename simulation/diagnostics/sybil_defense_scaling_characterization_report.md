# Sybil defense scaling characterization report

## Go/no-go outcome

The registered characterization completed. The ratio-collapse slice is non-collapse, so every ratio-expressed main-surface reading below carries the registered material caveat that a fuller two-dial grid is needed in a future registered study. This report does not add that grid.

No crossover rank was computed or used. The registered fixed-cell quantities are reported below.

## 1. Ratio-collapse slice

Criterion, quoted verbatim from the committed registration:

> The finding quantity is the failure-rate curve compared cell by cell across
> the three parity levels, never a crossover rank. At each structural point,
> all three pairwise absolute failure-rate differences are calculated. For a
> difference `d`, its registered normal delta-method 95 percent interval is
> `d +/- 1.96 * sqrt(p1*(1-p1)/200 + p2*(1-p2)/200)`. The dials collapse to
> their ratio if every interval's upper bound is below the 0.15 MEI. They do
> not collapse if at least one interval's lower bound is at or above 0.15.
> Any other result is boundary. A non-collapse result is reported as a
> material caveat on every ratio-expressed main-surface reading and identifies
> the fuller two-dial grid as a future registered study; that fuller grid is
> not added here. The slice runs and reports before the main surface is
> interpreted as ratio-parameterized.

Result:

The 75-cell slice produced 75 pairwise cross-level comparisons. Classifications were boundary=29, robust=32, sensitive=1, vacuous_zero_flag=13. The largest observed difference was 0.255 with 95 percent interval [0.161, 0.349] at structural point 16, levels 0.316 and 3.16. 13 comparisons were exactly zero and are flagged rather than banked.

| Point | Size | Severity | Rank | F(0.316) | F(1.0) | F(3.16) | Max d | Max 95% CI |
|---:|---:|---:|---:|---:|---:|---:|---:|:---|
| 0 | 2 | 0.0 | 2 | 0.905 | 0.850 | 0.820 | 0.085 | [0.018, 0.152] |
| 1 | 2 | 0.33 | 2 | 0.870 | 0.855 | 0.775 | 0.095 | [0.021, 0.169] |
| 2 | 2 | 0.66 | 2 | 0.855 | 0.810 | 0.790 | 0.065 | [-0.010, 0.140] |
| 3 | 2 | 1.0 | 2 | 0.870 | 0.850 | 0.770 | 0.100 | [0.025, 0.175] |
| 4 | 4 | 0.0 | 4 | 0.720 | 0.710 | 0.660 | 0.060 | [-0.030, 0.150] |
| 5 | 4 | 0.33 | 4 | 0.775 | 0.755 | 0.625 | 0.150 | [0.061, 0.239] |
| 6 | 4 | 0.66 | 3 | 0.930 | 0.855 | 0.800 | 0.130 | [0.064, 0.196] |
| 7 | 4 | 1.0 | 2 | 0.985 | 0.955 | 0.925 | 0.060 | [0.020, 0.100] |
| 8 | 8 | 0.0 | 8 | 0.730 | 0.655 | 0.560 | 0.170 | [0.078, 0.262] |
| 9 | 8 | 0.33 | 8 | 0.675 | 0.625 | 0.550 | 0.125 | [0.030, 0.220] |
| 10 | 8 | 0.66 | 5 | 0.880 | 0.910 | 0.820 | 0.090 | [0.024, 0.156] |
| 11 | 8 | 1.0 | 2 | 1.000 | 0.990 | 0.995 | 0.010 | [-0.004, 0.024] |
| 12 | 16 | 0.0 | 16 | 0.665 | 0.585 | 0.615 | 0.080 | [-0.015, 0.175] |
| 13 | 16 | 0.33 | 16 | 0.680 | 0.620 | 0.490 | 0.190 | [0.095, 0.285] |
| 14 | 16 | 0.66 | 7 | 0.955 | 0.955 | 0.940 | 0.015 | [-0.029, 0.059] |
| 15 | 16 | 1.0 | 2 | 1.000 | 1.000 | 1.000 | 0.000 | [0.000, 0.000] |
| 16 | 32 | 0.0 | 32 | 0.680 | 0.600 | 0.425 | 0.255 | [0.161, 0.349] |
| 17 | 32 | 0.33 | 32 | 0.625 | 0.620 | 0.490 | 0.135 | [0.039, 0.231] |
| 18 | 32 | 0.66 | 13 | 0.945 | 0.950 | 0.930 | 0.020 | [-0.027, 0.067] |
| 19 | 32 | 1.0 | 2 | 1.000 | 1.000 | 1.000 | 0.000 | [0.000, 0.000] |
| 20 | 64 | 0.0 | 64 | 0.690 | 0.515 | 0.450 | 0.240 | [0.146, 0.334] |
| 21 | 64 | 0.33 | 64 | 0.710 | 0.600 | 0.495 | 0.215 | [0.121, 0.309] |
| 22 | 64 | 0.66 | 23 | 0.985 | 0.970 | 0.940 | 0.045 | [0.008, 0.082] |
| 23 | 64 | 1.0 | 2 | 1.000 | 1.000 | 1.000 | 0.000 | [0.000, 0.000] |
| 24 | 1 | 1.0 | 1 | 1.000 | 1.000 | 1.000 | 0.000 | [0.000, 0.000] |

Verdict:

**NON-COLLAPSE.** One comparison has a lower 95 percent bound at or above the 0.15 MEI. The main surface therefore cannot be read as exhaustively ratio-parameterized. Its ratio findings remain valid for the registered term-OFF representation but require the registered fuller-grid caveat.

## 2. Primary fixed-cell reading, per arm

Criterion, quoted verbatim from the committed registration:

> **Primary, per arm, final registered form:** the fixed-cell defense-failure
> proportions at every maximum-collapse rank-two floor cell, reported
> separately for all six validator-set sizes and all four cost combinations.
> No cells are aggregated by effective rank because headcount still controls
> pairwise cost and Arm B corruption opportunities after rank collapses to
> two. The institution-only rank-one analytic corner is reported separately.
> Each proportion carries its normal 95 percent interval. Arm B strict failure
> is its primary proportion and rank-visible failure is its required companion
> track. The primary A/B contrast is the fixed-cell absolute difference with
> the same normal delta-method interval and 0.15 MEI discipline.

Result:

- Arm A: 600 maximum-collapse rank-two cells, failure-rate range [0.005, 1.000], floor classifications clears=192, fails=375, statistical_boundary=33. Exact-zero cells flagged: 0.
- Arm B strict: 600 maximum-collapse rank-two cells, failure-rate range [0.015, 1.000], floor classifications clears=131, fails=435, statistical_boundary=34. Exact-zero cells flagged: 0.
- Arm B rank-visible: 600 maximum-collapse rank-two cells, failure-rate range [0.000, 0.735], floor classifications clears=577, fails=10, statistical_boundary=13. Exact-zero cells flagged: 286.

The institution-only analytic corner had effective rank one in all 200 arm, ratio, and cost rows. Its strict defense failure rate was 1.000 to 1.000.

A/B absolute-difference classifications across the 600 matched cells were strict: boundary=114, robust=122, sensitive=211, vacuous_zero_flag=153; rank-visible: boundary=68, robust=86, sensitive=445, vacuous_zero_flag=1. Directions were strict: arm_a_higher=134, arm_b_higher=313, equal=153; rank-visible: arm_a_higher=598, arm_b_higher=1, equal=1.

All full 25-point curves, cell proportions, intervals, floor classifications, and A/B comparisons are preserved in the companion analysis JSON.

Verdict:

**Arm A: CELL-DEPENDENT. Arm B strict: CELL-DEPENDENT. Arm B rank-visible: CELL-DEPENDENT.** Each track contains clear, fail, and statistical-boundary cells, so neither arm has a single global floor outcome across the registered ratio and cost cells. The A/B asymmetry is material in some cells, boundary in others, and robustly below the MEI in others. Exact-zero comparisons are flagged in the companion record.

## 3. Headline floor question

Criterion, quoted verbatim from the committed registration:

> **Headline, per arm:** whether each fixed rank-two floor cell clears the
> attacker at maximum collapse. A cell clears when its failure-rate interval
> is wholly below 0.5, fails when the interval is wholly above 0.5, and is
> statistical boundary when the interval includes 0.5. The three frozen
> cross-arm outcomes are then read at each cell and cost form: floor clears
> when both arms clear; floor fails when both fail; floor is boundary when the
> arms differ or either arm is statistical boundary. The direction of any
> mixed result is always stated, including a direction opposite the expected
> Arm-A-clears and Arm-B-fails pattern. Arm B is read on both strict and rank-
> visible tracks, so two cross-arm floor outcomes are reported per cell.

Result:

Across 600 matched rank-two cells, the strict A/B outcomes were floor_boundary=180, floor_clears=90, floor_fails=330. The rank-visible A/B outcomes were floor_boundary=398, floor_clears=192, floor_fails=10. Mixed directions and statistical boundaries are retained as `floor_boundary`, exactly as registered.

| Ratio | Strict clears | Strict fails | Strict boundary | Visible clears | Visible fails | Visible boundary |
|---:|---:|---:|---:|---:|---:|---:|
| 0.1 | 12 | 8 | 4 | 15 | 0 | 9 |
| 0.121153 | 10 | 8 | 6 | 14 | 0 | 10 |
| 0.14678 | 10 | 8 | 6 | 14 | 0 | 10 |
| 0.177828 | 8 | 8 | 8 | 13 | 0 | 11 |
| 0.215443 | 8 | 9 | 7 | 14 | 0 | 10 |
| 0.261016 | 7 | 9 | 8 | 13 | 0 | 11 |
| 0.316228 | 5 | 9 | 10 | 12 | 0 | 12 |
| 0.383119 | 6 | 10 | 8 | 13 | 0 | 11 |
| 0.464159 | 4 | 10 | 10 | 12 | 0 | 12 |
| 0.562341 | 5 | 10 | 9 | 12 | 0 | 12 |
| 0.681292 | 4 | 10 | 10 | 12 | 0 | 12 |
| 0.825404 | 4 | 10 | 10 | 12 | 0 | 12 |
| 1 | 3 | 10 | 11 | 12 | 0 | 12 |
| 1.21153 | 2 | 10 | 12 | 10 | 0 | 14 |
| 1.4678 | 1 | 10 | 13 | 8 | 0 | 16 |
| 1.77828 | 0 | 11 | 13 | 4 | 0 | 20 |
| 2.15443 | 1 | 12 | 11 | 2 | 0 | 22 |
| 2.61016 | 0 | 18 | 6 | 0 | 0 | 24 |
| 3.16228 | 0 | 20 | 4 | 0 | 0 | 24 |
| 3.83119 | 0 | 20 | 4 | 0 | 0 | 24 |
| 4.64159 | 0 | 21 | 3 | 0 | 1 | 23 |
| 5.62341 | 0 | 20 | 4 | 0 | 0 | 24 |
| 6.81292 | 0 | 22 | 2 | 0 | 2 | 22 |
| 8.25404 | 0 | 23 | 1 | 0 | 3 | 21 |
| 10 | 0 | 24 | 0 | 0 | 4 | 20 |

Verdict:

**CELL-DEPENDENT ACROSS ALL THREE REGISTERED OUTCOMES.** There is no honest global clear or fail verdict. Arm B strict and rank-visible tracks differ materially, and both are reported. The direction is not forced toward the pre-run expectation.

## 4. Ratio sensitivity

Criterion, quoted verbatim from the committed registration:

> **Ratio sensitivity, final registered form:** at every fixed structural and
> cost cell, report the full 25-point failure-rate curve and calculate the
> pre-fixed endpoint contrast `d = F(ratio 10) - F(ratio 0.1)`. Arm A and Arm
> B strict are monotonic in ratio under the committed mechanism, so this
> signed contrast is the full registered ratio response without a selected
> interior threshold. Its 95 percent interval is
> `d +/- 1.96 * sqrt(p10*(1-p10)/200 + p01*(1-p01)/200)`. A cell is ratio-
> sensitive when the interval's lower bound is at or above the 0.15 MEI,
> robust when its upper bound is below 0.15, and boundary otherwise. Arm B
> strict supplies the per-arm classification; the rank-visible 25-point curve
> and endpoint contrast are reported separately as the companion track. The
> ratio remains swept from 0.1 to 10 at 25 log-spaced points. Ratios beyond
> that frozen range are not added.

Result:

- Arm A: 100 fixed structural and cost curves; boundary=2, robust=17, sensitive=70, vacuous_zero_flag=11; endpoint contrast range [0.000, 0.925]; exact-zero contrasts flagged: 11.
- Arm B strict: 100 fixed structural and cost curves; boundary=6, robust=15, sensitive=64, vacuous_zero_flag=15; endpoint contrast range [0.000, 0.900]; exact-zero contrasts flagged: 15.
- Arm B rank-visible: 100 fixed structural and cost curves; robust=14, sensitive=16, vacuous_zero_flag=70; endpoint contrast range [-0.090, 0.720]; exact-zero contrasts flagged: 70.

Verdict:

**RATIO-SENSITIVE IN A SUBSET OF CELLS, ROBUST IN A SUBSET, AND BOUNDARY IN THE REMAINDER.** The registered response is not a single crossover or a global classification. The full curves and every endpoint interval are in the companion analysis JSON. Because the ratio-collapse slice returned non-collapse, these term-OFF ratio responses carry the fuller two-dial-grid caveat.

## 5. Complete-linkage sensitivity

Criterion, quoted verbatim from the committed registration:

> **Merge rule, registered choice.** Effective rank is computed by threshold-
> connected-components on pairwise cosine similarity at threshold 0.9. This
> remains the primary defender-conservative rule. Complete linkage remains the
> registered reduced-scope sensitivity pass: Arm A, both defense-cost forms,
> both attack-cost forms, the full 25-point structural axis, parity ratio 1.0,
> and n=200, for 100 cells. Its finding quantity is the fixed-cell absolute
> difference between complete-linkage and primary connected-components
> failure rates. A cell is merge-sensitive when the difference interval's
> lower bound is at or above 0.15, robust when its upper bound is below 0.15,
> and boundary otherwise. The complete-linkage results are reported
> separately and never blended into the primary surface.

Result:

The 100 matched cells classified as boundary=11, robust=60, sensitive=3, vacuous_zero_flag=26. 26 exact-zero cells are flagged. The largest absolute difference was 0.475 with 95 percent interval [0.389, 0.561] at structural point 22, pairwise_exact defense and superlinear attack.

Verdict:

**MERGE-SENSITIVE IN SOME FIXED CELLS, ROBUST IN OTHERS, WITH BOUNDARY CELLS RETAINED.** The alternate pass is separate from the primary and is not blended.

## Execution and primary record

- Git head used for all data: `c6ef03cb18c3cfb8716a6d5f28e905e339585d65`.
- Workers: 16.
- Total cells: 5175.
- Total runs: 1035000.
- Registered n per cell: 200. Worst-case normal-approximation power requires 175 per cell for the 0.15 MEI; n=200 carries 25 observations of margin and registered approximate power 0.850838768327.
- Ratio-collapse wall time: 0.096252 seconds.
- Main-surface wall time: 21.675554 seconds.
- Complete-linkage wall time: 0.139177 seconds.
- Total wall time: 22.082369 seconds.
- Manifest: `data/sybil_defense_scaling/full_5ac6a2e_sybil_scaling_characterization_v1/full_5ac6a2e_manifest.json`.
- Authoritative files: `full_5ac6a2e_ratio_collapse_slice_results.csv`, `full_5ac6a2e_main_surface_results.csv`, and `full_5ac6a2e_complete_linkage_results.csv`, each enumerated with hash and row count in the manifest.
- Excluded process artifact: `sweep_progress.log`.
- Excluded non-authoritative prefixes: `smoke_`, `two_dial_smoke_`, and `selfcheck_`.

The run requested 16 worker processes on a host that reported 12 logical processors at launch. This operational oversubscription is recorded for reproducibility. It changed no registered cell, sample size, seed, or analysis value.

## Anomalies and future questions

No count, hash, axis, scope, or execution anomaly was found. The ratio-collapse non-collapse verdict is a registered finding, not an execution anomaly. Per the plan, it names one future question: a separately registered fuller two-dial capability grid. No out-of-plan observation was folded into this study.

The branch remains unmerged pending operator audit.
