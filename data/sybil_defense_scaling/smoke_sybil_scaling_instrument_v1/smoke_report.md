# Sybil defense scaling smoke report

Go/no-go: **GO for operator review of the instrument.**

This was an instrument-validation and variance-estimation smoke only. It did not run a rank-by-ratio grid, set a capability-ratio range, calculate power, or read a crossover.

## Logged smoke evidence

- Gate a, cost scaling: PASS. Exact pair counts and costs were [(2, 1, 1.0), (4, 6, 6.0), (8, 28, 28.0)].
- Gate b, effective rank: PASS. Observed ranks were {'six_distinct_no_collapse': 6, 'six_correlated_no_collapse': 1, 'six_distinct_maximum_collapse': 1, 'maximum_collapse_with_institution': 2, 'analytic_institution_alone': 1}.
- Gate c, distinct arm effects: PASS. Arm A changed apparent rank through surviving forged clusters while preserving the genuine partition. Arm B changed the similarity matrix without injecting clusters.
- Gate d, institutional floor: PASS. Arm A kept the true maximum-collapse rank at two and preserved the institution in every run. Arm B merged the institution in 13/64 runs, produced measured rank below two in 2/64, and overcounted rank in 43/64.
- Gate e, positive controls: PASS. High-attacker failures were {'false_cluster_injection': {'n': 8, 'failures': 8}, 'measurement_corruption': {'n': 8, 'failures': 8}}; rank-one failures were {'false_cluster_injection': {'n': 8, 'failures': 8}, 'measurement_corruption': {'n': 8, 'failures': 8}}.
- Existing validated path probe: PASS.

## Variance estimate for the operator power calculation

- Arm A: {'n': 64, 'defense_failure_mean': 0.484375, 'defense_failure_sample_variance': 0.2537202380952381, 'rank_error_mean': 0.546875, 'rank_error_sample_variance': 0.3787202380952381}.
- Arm B: {'n': 64, 'defense_failure_mean': 0.78125, 'defense_failure_sample_variance': 0.1736111111111111, 'rank_error_mean': 0.890625, 'rank_error_sample_variance': 0.765625}.

These are smoke fixture variances, not crossover readings.

## Timing and candidate projection

- Instrumented runs: 160.
- Seconds per run, mean/median/p95/max: 0.000107540 / 0.000092882 / 0.000152584 / 0.000256684.
- Candidate resolution: {'rank_points_including_analytic_corner': 25, 'ratio_points': 25, 'arms': 2, 'defense_cost_models': 2, 'attack_cost_models': 2}, 5000 cells per replicate layer.
- Projected cost: 0.762920000 seconds times the future operator-set powered replicates per cell, equal to 0.000211922 core-hours per replicate layer.

## Output identity

- Run ID: `smoke_sybil_scaling_instrument_v1`.
- Output directory: `data/sybil_defense_scaling/smoke_sybil_scaling_instrument_v1`.
- Every artifact and directory begins with or sits below `smoke_`. The authoritative convention uses the exact `full_5ac6a2e_` prefix and an explicit manifest, so these files cannot enter that selection.

STOP: awaiting power calculation, capability-ratio range, and pre-registration commit before any full sweep.
