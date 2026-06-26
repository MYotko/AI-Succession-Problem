# Patient Defection Sweep Summary

Generated: 2026-06-25T00:29:36+00:00
Sweep: 1
Rows loaded: 1800
Errors: 0

## Sweep 1: Yield Condition Response

| target | weight | n | any fire rate | SE | delta vs baseline | pair SE | p approx | mean actual-would-fire rejects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H_C_inflated | 0.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.00 |
| H_C_inflated | 0.10 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.00 |
| H_C_inflated | 0.25 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.04 |
| H_C_inflated | 0.50 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.02 |
| H_C_inflated | 1.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.05 |
| H_C_inflated | 2.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.16 |
| H_N_inflated | 0.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.00 |
| H_N_inflated | 0.10 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.10 |
| H_N_inflated | 0.25 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.17 |
| H_N_inflated | 0.50 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.44 |
| H_N_inflated | 1.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.71 |
| H_N_inflated | 2.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 1.50 |
| L_t_inflated | 0.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.00 |
| L_t_inflated | 0.10 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.03 |
| L_t_inflated | 0.25 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.09 |
| L_t_inflated | 0.50 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.13 |
| L_t_inflated | 1.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.24 |
| L_t_inflated | 2.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.44 |

Aligned baseline any-fire rate: 1.000. Baseline per-evaluation fire proxy: 1.000.

## Caveat on a diagnostic column

The CSV column `mean_actual_minus_honest_objective` compares quantities recorded at
different aggregation points and is approximately constant regardless of defection
weight; it is not the per-step defection bonus and should not be cited. The
substantive findings are independent of this column and rest on the actual-would-fire
rejection counts (the "mean actual-would-fire rejects" column above) and the
cross-generational continuation results.

