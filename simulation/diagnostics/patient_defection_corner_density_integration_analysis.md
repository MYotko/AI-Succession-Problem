# Patient Defection Second-Fire Pocket Density Diagnostic

Generated: 2026-07-14

## Existing record confirmation

Read `simulation/diagnostics/patient_defection_sweep3_capability_constraint.csv` and `simulation/diagnostics/patient_defection_sweeps.py` before running diagnostics. The sweep 3 runner configuration is alpha [0.5, 0.75, 1.0, 1.25, 1.5] by successor_capability_growth_rate [1.5, 2.0, 2.5], defection_weight 0.5, defection_target H_C_inflated, inheritance_mode lineage, successor_capability 2.0, max_generations 4, n_steps 500, rr 0.064, phi 25.0, rollout_steps 20, n_candidates 300, n_agents 200, cop_cost_audit True.

Important discrepancy: the current CSV has 2,250 rows and n=150 per alpha/growth cell, not n=10. The integration-analysis text in the repo also reports the corner as 15 second fires out of 150, equal to 10 percent.

| alpha | growth | n | second-fire rate | mean fires | max generation | max active cap | third-fire runs | gen>=4 runs | active cap>3 runs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.50 | 1.50 | 150 | 0.100 | 1.100 | 3 | 3.00 | 0 | 0 | 0 |
| 0.50 | 2.00 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |
| 0.50 | 2.50 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |
| 0.75 | 1.50 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |
| 0.75 | 2.00 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |
| 0.75 | 2.50 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |
| 1.00 | 1.50 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |
| 1.00 | 2.00 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |
| 1.00 | 2.50 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |
| 1.25 | 1.50 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |
| 1.25 | 2.00 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |
| 1.25 | 2.50 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |
| 1.50 | 1.50 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |
| 1.50 | 2.00 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |
| 1.50 | 2.50 | 150 | 0.000 | 1.000 | 2 | 2.00 | 0 | 0 | 0 |

## Raw rows for alpha 0.50, growth 1.50 in existing CSV

| seed | steps | survived | final_pop | final_gen | max_gen | fires | first_fire_step | actual-would-fire rejects | max successor cap | max active cap | error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 500 | True | 36 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 1 | 500 | True | 56 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 2 | 412 | False | 0 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 3 | 500 | False | 7 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 4 | 500 | True | 36 | 3 | 3 | 2 | 5 | 0 | 4.5 | 3.0 |  |
| 5 | 500 | False | 26 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 6 | 500 | False | 19 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 7 | 500 | True | 73 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 8 | 500 | True | 47 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 9 | 500 | True | 38 | 2 | 2 | 1 | 5 | 1 | 3.0 | 2.0 |  |
| 10 | 500 | True | 41 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 11 | 500 | True | 97 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 12 | 500 | True | 40 | 2 | 2 | 1 | 7 | 0 | 3.0 | 2.0 |  |
| 13 | 500 | True | 66 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 14 | 500 | True | 66 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 15 | 500 | True | 43 | 3 | 3 | 2 | 5 | 0 | 4.5 | 3.0 |  |
| 16 | 500 | False | 27 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 17 | 500 | True | 74 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 18 | 500 | True | 39 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 19 | 500 | True | 51 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 20 | 500 | False | 25 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 21 | 500 | False | 29 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 22 | 500 | False | 10 | 2 | 2 | 1 | 6 | 1 | 3.0 | 2.0 |  |
| 23 | 500 | False | 23 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 24 | 500 | True | 99 | 2 | 2 | 1 | 6 | 1 | 3.0 | 2.0 |  |
| 25 | 500 | True | 69 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 26 | 500 | True | 36 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 27 | 500 | False | 17 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 28 | 500 | True | 44 | 2 | 2 | 1 | 6 | 1 | 3.0 | 2.0 |  |
| 29 | 500 | True | 46 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 30 | 500 | False | 24 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 31 | 500 | False | 2 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 32 | 500 | False | 20 | 3 | 3 | 2 | 4 | 0 | 4.5 | 3.0 |  |
| 33 | 500 | False | 29 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 34 | 500 | True | 40 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 35 | 500 | True | 61 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 36 | 500 | False | 6 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 37 | 500 | False | 11 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 38 | 500 | True | 84 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 39 | 500 | True | 41 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 40 | 391 | False | 0 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 41 | 500 | True | 90 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 42 | 500 | False | 29 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 43 | 500 | False | 1 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 44 | 500 | True | 41 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 45 | 500 | True | 67 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 46 | 500 | True | 77 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 47 | 500 | True | 42 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 48 | 500 | False | 19 | 2 | 2 | 1 | 5 | 1 | 3.0 | 2.0 |  |
| 49 | 500 | True | 35 | 2 | 2 | 1 | 6 | 1 | 3.0 | 2.0 |  |
| 50 | 500 | True | 79 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 51 | 500 | True | 50 | 3 | 3 | 2 | 5 | 0 | 4.5 | 3.0 |  |
| 52 | 500 | True | 59 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 53 | 500 | True | 60 | 2 | 2 | 1 | 7 | 0 | 3.0 | 2.0 |  |
| 54 | 500 | True | 65 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 55 | 500 | True | 34 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 56 | 500 | False | 23 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 57 | 500 | True | 43 | 2 | 2 | 1 | 5 | 1 | 3.0 | 2.0 |  |
| 58 | 500 | True | 43 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 59 | 500 | False | 25 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 60 | 500 | True | 50 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 61 | 500 | True | 61 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 62 | 500 | True | 30 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 63 | 500 | True | 50 | 2 | 2 | 1 | 5 | 1 | 3.0 | 2.0 |  |
| 64 | 500 | True | 34 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 65 | 500 | True | 95 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 66 | 500 | True | 59 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 67 | 500 | True | 45 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 68 | 500 | True | 46 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 69 | 500 | True | 62 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 70 | 500 | True | 86 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 71 | 500 | True | 65 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 72 | 500 | True | 30 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 73 | 500 | True | 63 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 74 | 500 | True | 71 | 3 | 3 | 2 | 5 | 0 | 4.5 | 3.0 |  |
| 75 | 500 | True | 34 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 76 | 500 | False | 20 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 77 | 500 | True | 116 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 78 | 500 | True | 54 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 79 | 500 | True | 46 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 80 | 500 | False | 8 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 81 | 500 | True | 39 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 82 | 500 | True | 60 | 2 | 2 | 1 | 5 | 1 | 3.0 | 2.0 |  |
| 83 | 500 | False | 29 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 84 | 437 | False | 0 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 85 | 500 | True | 35 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 86 | 500 | True | 75 | 3 | 3 | 2 | 4 | 0 | 4.5 | 3.0 |  |
| 87 | 500 | False | 8 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 88 | 500 | False | 24 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 89 | 500 | False | 13 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 90 | 500 | False | 21 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 91 | 500 | True | 65 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 92 | 500 | False | 24 | 3 | 3 | 2 | 5 | 0 | 4.5 | 3.0 |  |
| 93 | 500 | False | 11 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 94 | 500 | True | 69 | 3 | 3 | 2 | 6 | 0 | 4.5 | 3.0 |  |
| 95 | 500 | True | 58 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 96 | 500 | True | 66 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 97 | 500 | True | 78 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 98 | 500 | True | 70 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 99 | 500 | True | 52 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 100 | 500 | True | 44 | 2 | 2 | 1 | 8 | 0 | 3.0 | 2.0 |  |
| 101 | 500 | True | 37 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 102 | 500 | False | 24 | 3 | 3 | 2 | 4 | 0 | 4.5 | 3.0 |  |
| 103 | 500 | False | 25 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 104 | 500 | False | 22 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 105 | 500 | True | 61 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 106 | 500 | True | 74 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 107 | 500 | True | 75 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 108 | 500 | True | 62 | 3 | 3 | 2 | 5 | 0 | 4.5 | 3.0 |  |
| 109 | 500 | False | 10 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 110 | 500 | True | 51 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 111 | 500 | True | 30 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 112 | 500 | True | 127 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 113 | 500 | False | 6 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 114 | 500 | True | 95 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 115 | 500 | True | 50 | 3 | 3 | 2 | 4 | 0 | 4.5 | 3.0 |  |
| 116 | 500 | True | 47 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 117 | 500 | False | 19 | 3 | 3 | 2 | 4 | 0 | 4.5 | 3.0 |  |
| 118 | 500 | True | 47 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 119 | 500 | True | 50 | 2 | 2 | 1 | 6 | 1 | 3.0 | 2.0 |  |
| 120 | 500 | True | 30 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 121 | 500 | False | 18 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 122 | 500 | False | 18 | 3 | 3 | 2 | 4 | 0 | 4.5 | 3.0 |  |
| 123 | 500 | True | 72 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 124 | 500 | True | 52 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 125 | 500 | True | 85 | 2 | 2 | 1 | 5 | 1 | 3.0 | 2.0 |  |
| 126 | 500 | True | 31 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 127 | 500 | False | 1 | 2 | 2 | 1 | 5 | 1 | 3.0 | 2.0 |  |
| 128 | 500 | True | 64 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 129 | 500 | True | 52 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 130 | 500 | True | 43 | 3 | 3 | 2 | 6 | 0 | 4.5 | 3.0 |  |
| 131 | 500 | False | 27 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 132 | 282 | False | 0 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 133 | 500 | True | 42 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 134 | 456 | False | 0 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 135 | 500 | True | 54 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 136 | 500 | False | 18 | 2 | 2 | 1 | 5 | 1 | 3.0 | 2.0 |  |
| 137 | 482 | False | 0 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 138 | 500 | True | 64 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 139 | 500 | True | 37 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 140 | 290 | False | 0 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 141 | 500 | False | 22 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 142 | 500 | True | 70 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 143 | 500 | False | 21 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 144 | 500 | True | 53 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |
| 145 | 500 | True | 75 | 3 | 3 | 2 | 5 | 1 | 4.5 | 3.0 |  |
| 146 | 500 | False | 10 | 2 | 2 | 1 | 6 | 0 | 3.0 | 2.0 |  |
| 147 | 500 | False | 9 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 148 | 500 | True | 30 | 2 | 2 | 1 | 5 | 0 | 3.0 | 2.0 |  |
| 149 | 500 | False | 2 | 2 | 2 | 1 | 4 | 0 | 3.0 | 2.0 |  |

## Dense re-sweep attempt

Added `simulation/diagnostics/patient_defection_corner_density.py`. It reuses `patient_defection_sweeps.run_single` and changes only the grid and seed count. Planned grid: alpha [0.40, 0.50, 0.60] by growth [1.25, 1.40, 1.50, 1.60, 1.75], seeds 0 through 199, all other patient-defection sweep 3 parameters held fixed.

The full 3,000-run dense sweep did not complete in this session. A single matched v2 run took about 103 seconds direct, which puts the full requested sweep outside this session's compute envelope without altering frozen setup parameters.

CSV: `simulation/diagnostics/patient_defection_corner_density.csv`

Completed partial rows:

| seed | alpha | growth | steps | fires | max generation | max active cap | error |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0.4 | 1.25 | 500 | 1 | 2 | 2.0 |  |

## Characterization status

The existing current CSV already gives higher-resolution evidence than the prompt's expected n=10 for the original corner: alpha 0.50, growth 1.50 has 150 runs, second-fire rate 15/150 = 10.0 percent, max final generation 3, max active capability 3.0, no third-fire runs, no generation 4 runs, and no active capability above 3.0. All other existing sweep 3 cells have zero second fires at n=150.

The requested bracket grid around lower alpha and smaller growth is not complete. The one completed new alpha 0.40, growth 1.25 row fired once, reached max generation 2, and did not exceed active capability 2.0. That single row is not a density estimate.

## Recommended disposition for human review

Do not update the paper or advisor claim from the partial dense re-sweep. Per current evidence from the existing 150-seed-per-cell sweep 3 record, the current claim remains supported: tested patient defection does not compound across generations, with no tested cell reaching generation 4, firing a third succession, or reaching active capability above 3.0. The alpha 0.50, growth 1.50 pocket is a bounded 10.0 percent second-fire pocket in the current CSV, not a compounding escape in that record. The bracket-density question remains open until the full dense wrapper completes.
