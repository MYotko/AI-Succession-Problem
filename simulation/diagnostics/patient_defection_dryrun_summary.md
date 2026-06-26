# Patient Defection Sweep Summary

Generated: 2026-06-25T00:11:22+00:00
Sweep: dry-run
Rows loaded: 16
Errors: 0

## Sweep 1: Yield Condition Response

| target | weight | n | any fire rate | SE | delta vs baseline | pair SE | p approx | mean actual-would-fire rejects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H_C_inflated | 0.00 | 4 | 0.250 | 21.65pp | 0.125 | 24.61pp | 0.6115 | 0.00 |
| H_C_inflated | 0.50 | 4 | 0.000 | 0.00pp | -0.125 | 11.69pp | 0.2850 | 0.00 |
| H_N_inflated | 0.00 | 4 | 0.000 | 0.00pp | -0.125 | 11.69pp | 0.2850 | 0.00 |
| H_N_inflated | 0.50 | 4 | 0.250 | 21.65pp | 0.125 | 24.61pp | 0.6115 | 0.25 |

Aligned baseline any-fire rate: 0.125. Baseline per-evaluation fire proxy: 0.125.

## Sweep 2: L(t) Trajectory Under Lineage Defection

| weight | n | mean fires | mean final gen | L gen1 | L gen2 | L gen3 | L gen4 | L gen5 | final L | delta final L | pair SE | p approx |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.00 | 8 | 0.12 | 1.12 | 0.2539 | 0.0477 | 0.0000 | 0.0000 | 0.0000 | 0.2684 | 0.0000 | 0.0281 | 1.0000 |
| 0.50 | 8 | 0.12 | 1.12 | 0.2540 | 0.0535 | 0.0000 | 0.0000 | 0.0000 | 0.2672 | -0.0012 | 0.0305 | 0.9682 |

## Sweep 3: Cliff Constraint on Defecting Capability

| alpha | growth | n | any fire rate | mean fires | mean final gen | mean max successor cap | max successor cap | mean actual-would-fire rejects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.00 | 1.5 | 8 | 0.250 | 0.25 | 1.25 | 2.25 | 3.00 | 0.12 |
| 1.50 | 1.5 | 8 | 0.000 | 0.00 | 1.00 | 2.00 | 2.00 | 0.00 |

