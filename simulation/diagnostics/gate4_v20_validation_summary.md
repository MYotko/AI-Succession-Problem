# Gate 4 v2.0 Validation Summary

Generated: 2026-06-09T22:07:43+00:00
Total rows: 1050
Verdict: PASS

## Gate Checks

- G4.1 Runaway penalty binding: PASS
  - active_runaway_observations: 426
  - total_observations: 426
  - relative_tolerance: 0.01
  - failure_count: 0

- G4.2 Succession self-blocking at runaway capability: PASS
  - regime_count: 6
  - min_below_fire_rate: 0.8
  - max_above_fire_rate: 0.2
  - max_above_mean_yield_margin: 0.0
  - min_separation_standard_errors: 2.0

- G4.3 Theta_tech floor preservation: PASS
  - theta_floor: 0.01
  - absolute_tolerance: 1e-09
  - min_observed_theta_tech: 0.01
  - observations_below_floor: 0
  - extreme_runaway_observations: 3769

## G4.2 Regimes

| alpha | rr | cap_star | below_cap | below_fire | above_cap | above_fire | above_margin | sep_SE |
|---|---|---|---|---|---|---|---|---|
| 1.000 | 0.057 | 3.000 | 2.500 | 1.000 | 3.000 | 0.080 | -2.075 | 16.956 |
| 1.000 | 0.060 | 3.000 | 2.500 | 1.000 | 3.000 | 0.120 | -1.980 | 13.540 |
| 1.000 | 0.064 | 3.000 | 2.500 | 1.000 | 3.000 | 0.040 | -2.320 | 24.495 |
| 1.500 | 0.057 | 2.500 | 2.000 | 1.000 | 2.500 | 0.000 | -2.543 | inf |
| 1.500 | 0.060 | 2.500 | 2.000 | 1.000 | 2.500 | 0.040 | -2.432 | 24.495 |
| 1.500 | 0.064 | 2.500 | 2.000 | 1.000 | 2.500 | 0.040 | -3.434 | 24.495 |
