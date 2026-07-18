# Patient Defection Corner-Density Bracket: Integration Analysis

Generated: 2026-07-14. Completed: 2026-07-17.

## Status

This document originally recorded a dense re-sweep in progress: of a planned 3,000-row grid (alpha in [0.40, 0.50, 0.60] by growth in [1.25, 1.40, 1.50, 1.60, 1.75], 200 seeds each), only one row had completed at the time of the earlier draft, and the recommendation was to leave the paper and advisor claim unchanged pending completion. The alpha=0.40 slice of that grid has since completed: 1,000 rows, 0 errors, 200 seeds per growth cell across the five growth values. The alpha=0.50 and alpha=0.60 slices were not run; this document characterizes the alpha=0.40 bracket only. This is the completed record for that bracket.

## Fixed parameters

Held fixed across all 1,000 rows, matching the sweep 3 capability-constraint setup: rr=0.064, phi=25.0, alpha=0.40, successor_capability=2.0, defection_weight=0.5, defection_target=H_C_inflated, inheritance_mode=lineage, max_generations=4, n_steps=500, rollout_steps=20, n_candidates=300, n_agents=200, cop_cost_audit=True. Zero errors across 1,000 rows. Data file: `simulation/diagnostics/patient_defection_corner_density.csv`. Wrapper: `simulation/diagnostics/patient_defection_corner_density.py` (reuses `patient_defection_sweeps.run_single` directly; changes only the grid and seed count).

## Per-cell results

| growth | n | second-fire rate | 95% CI | mean fires | max gen | max active cap | gen>=4 | third fire |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.25 | 200 | 0.680 | [0.612, 0.741] | 1.680 | 3 | 2.50 | 0 | 0 |
| 1.40 | 200 | 0.990 | [0.964, 0.997] | 1.990 | 3 | 2.80 | 0 | 0 |
| 1.50 | 200 | 1.000 | [0.981, 1.000] | 2.000 | 3 | 3.00 | 0 | 0 |
| 1.60 | 200 | 1.000 | [0.981, 1.000] | 2.000 | 3 | 3.20 | 0 | 0 |
| 1.75 | 200 | 1.000 | [0.981, 1.000] | 2.000 | 3 | 3.50 | 0 | 0 |

Second-fire rate is the fraction of runs reaching generation 3 (a second succession, beyond the always-occurring first succession into the prepared generation-2 defecting successor). 95% CIs are Wilson score intervals. Recomputed directly from `patient_defection_corner_density.csv` and cross-checked against the values supplied for this reconciliation; the two matched exactly on every field, including the CI bounds.

## Economic-stop evidence

The generation cap for this sweep was 4, and the deepest lineage reached in any of the 1,000 runs was 3, leaving one full generation of headroom unused. 95.0 to 99.0 percent of runs across the five cells completed the full 500-step horizon (194/200 at growth 1.25 up to 198/200 at growth 1.40). Mean yield evaluations per run ranged from 496.4 to 499.4 across cells (approximately 498 overall), meaning the model evaluated succession on essentially every step and rejected the third transition each time rather than stopping early. Knowledge transfer verified at 1.00 in every cell among runs that fired at least once. Taken together, the stop at generation 3 reads as an economic result of the yield condition rejecting the fourth-generation transition, not a configuration limit cutting the run short.

## Arithmetic finding

Max active capability observed equals exactly 2.0 (the fixed successor_capability) times the growth rate in every cell where a second fire occurred, and equals 2.0 in runs without a second fire:

| growth | 2.0 x growth | observed max active capability |
| --- | --- | --- |
| 1.25 | 2.50 | 2.0 (no second fire) or 2.50 (second fire) |
| 1.40 | 2.80 | 2.0 (no second fire) or 2.80 (second fire) |
| 1.50 | 3.00 | 3.00 |
| 1.60 | 3.20 | 3.20 |
| 1.75 | 3.50 | 3.50 |

This is an arithmetic identity of the tested grid (starting successor capability times growth rate at the second fire), not an emergent or bounded property of the architecture. It is the basis for withdrawing the earlier claim that no tested cell exceeded active capability 3.0: that claim held only because the earlier grid never tested a growth rate above 1.5 combined with a cell where second fire was common.

## Mechanism note (inference, not verified)

Max successor capability seen reaches 6.125 at growth 1.75, which is the generation-4 successor that the yield condition rejected (capability 3.5 active at generation 3, times growth 1.75). The sweeps record the yield-margin decomposition (honest advantage, actual advantage, transition cost) only at the first yield evaluation, not at the third. Whether the rejection at the third evaluation is driven primarily by the runaway penalty, by the rising transition cost (which grows with both incumbent capability and generation depth), or some combination, is not measured in this data. This is flagged explicitly as inference from the mechanism understood at the first fire, not a verified decomposition at the third fire.

## Survival by cell (context, not a claim)

Final-population survival rate (context only; this bracket is not designed to characterize survival): 0.575 (growth 1.25), 0.625 (1.40), 0.525 (1.50), 0.650 (1.60), 0.565 (1.75). No trend with growth rate is claimed from this; the bracket's seed count and design are not calibrated to resolve a survival relationship.

## Disposition

The alpha=0.40 bracket supersedes the "current claim remains supported... bracket-density question remains open" disposition in this document's earlier draft. Second succession at alpha=0.40 is not a rare pocket; it is the common case at growth 1.5 and above and the majority case at growth 1.25. What is confirmed, not overturned, is that generational depth stays bounded: no run in this bracket reached generation 4 or fired a third succession, at any tested growth rate, at the weakest alpha tested anywhere in this investigation. The claim in the paper (Section VIII.8), the program reference (Part X.8), and the advisor document is restated accordingly: from rare continuation to bounded generational depth. The active-capability-3.0 clause is withdrawn per the arithmetic finding above.

Source: `patient_defection_corner_density.csv` (1,000 rows, 0 errors); `patient_defection_corner_density.py`; `patient_defection_sweep3_capability_constraint.csv` (original grid, for the 14-of-15 / 10-percent comparison points).
