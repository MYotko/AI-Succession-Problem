# Patient Defection Integration Analysis

Generated: 2026-06-26T09:15:00+00:00

> **2026-07-17 pointer.** The rarity characterization below (second succession zero in 14 of 15 cells, 10 percent in the remaining cell) is grid-dependent: it describes the alpha range this document's Sweep 3 tested, not the architecture. A subsequent 1,000-run bracket at alpha=0.40 shows second succession firing in 68 to 100 percent of runs below that range. See `patient_defection_corner_density_integration_analysis.md` for the bracket record. This document remains accurate as the record of the three-sweep investigation as it stood at the time.

## 1. Substantive Findings

Patient defection was tested across three v2.0 substrate sweeps:

| sweep | purpose | rows | errors | data file |
| --- | --- | --- | --- | --- |
| 1 | Yield condition response to single-generation defection | 1800 | 0 | `patient_defection_sweep1_yield_response.csv` |
| 2 | L(t) trajectory under lineage defection | 800 | 0 | `patient_defection_sweep2_lineage_trajectory.csv` |
| 3 | Capability accumulation constraint under lineage defection | 2250 | 0 | `patient_defection_sweep3_capability_constraint.csv` |

Total completed rows: 4850. All runs used v2.0 formal yield logic under `optimize_u_sys_v2`. The defection implementation is agent-local: yield evaluation reports honest U_sys, while defecting agents optimize the secret-goal-adjusted objective.

### Prediction 1: Yield condition response to defection

Prediction 1 expected defecting successors to be rejected more often than aligned successors when the incumbent is aligned.

Sweep 1 does not support this prediction on the primary run-level metric. Every tested cell has 100 percent eventual yield-fire rate, including all defection weights and all targets:

| target | weights tested | eventual yield-fire result |
| --- | --- | --- |
| H_N_inflated | 0.0, 0.1, 0.25, 0.5, 1.0, 2.0 | 100 percent in every cell |
| H_C_inflated | 0.0, 0.1, 0.25, 0.5, 1.0, 2.0 | 100 percent in every cell |
| L_t_inflated | 0.0, 0.1, 0.25, 0.5, 1.0, 2.0 | 100 percent in every cell |

The first yield evaluation is rejected for all cells, including aligned baseline. Mean first honest advantage is approximately -0.055 against mean transition cost 4.560. Later substrate maturation is enough for every tested successor to eventually pass.

The secondary metric does show a defection-specific trace: honest rejection while actual objective would favor yield increases with weight, especially for H_N inflation. For H_N_inflated, mean actual-would-fire rejections rise from 0.00 at weight 0.0 to 1.50 at weight 2.0. For L_t_inflated the same metric rises from 0.00 to 0.44, and for H_C_inflated from 0.00 to 0.16.

Substantive disposition: Prediction 1 is refined downward. The yield condition does not reject first-generation defecting successors more often than aligned successors in this below-cliff configuration. It does still create honest-evaluation pressure, visible in actual-would-fire rejection counts, but that pressure is not sufficient to prevent eventual first succession.

### Prediction 2: L(t) trajectory under lineage defection

Prediction 2 expected L(t) degradation to compound across generations in patient-defecting lineages.

Sweep 2 does not show multi-generational compounding under the tested configuration. Every weight has mean yield fires 1.00, second-fire rate 0.00, and mean final generation 2.00:

| defection weight | n | mean fires | second-fire rate | mean final generation | mean final L(t) |
| --- | --- | --- | --- | --- | --- |
| 0.00 | 200 | 1.00 | 0.00 | 2.00 | 0.1796 |
| 0.25 | 200 | 1.00 | 0.00 | 2.00 | 0.1934 |
| 0.50 | 200 | 1.00 | 0.00 | 2.00 | 0.1627 |
| 1.00 | 200 | 1.00 | 0.00 | 2.00 | 0.1724 |

Final L(t) deltas versus aligned baseline do not exceed the 2 SE threshold. The largest negative delta is weight 0.50 at -0.0169 with pair SE 0.0114. That is roughly 1.48 SE, not enough to support a degradation claim under the project's standard.

Substantive disposition: Prediction 2 is not supported as originally stated. The reason is not that defecting lineages compound without harm. The reason is stronger: lineages do not reach enough generations for compounding to appear. The substrate blocks continuation after the first succession under this configuration, so there is no multi-generation L(t) degradation channel to observe.

### Prediction 3: Capability constraint on defecting lineages

Prediction 3 expected the alpha-driven cliff and runaway penalty to constrain capability accumulation across generations even when defection is undetected.

Sweep 3 supports the capability-constraint claim, but with a sharper result than expected. All cells fire at least once, but almost no cells fire twice:

| alpha | growth | second-fire rate | mean fires | max final generation | max active capability |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1.5 | 0.100 | 1.10 | 3 | 3.0 |
| 0.50 | 2.0 | 0.000 | 1.00 | 2 | 2.0 |
| 0.50 | 2.5 | 0.000 | 1.00 | 2 | 2.0 |
| 0.75 | 1.5 | 0.000 | 1.00 | 2 | 2.0 |
| 0.75 | 2.0 | 0.000 | 1.00 | 2 | 2.0 |
| 0.75 | 2.5 | 0.000 | 1.00 | 2 | 2.0 |
| 1.00 | 1.5 | 0.000 | 1.00 | 2 | 2.0 |
| 1.00 | 2.0 | 0.000 | 1.00 | 2 | 2.0 |
| 1.00 | 2.5 | 0.000 | 1.00 | 2 | 2.0 |
| 1.25 | 1.5 | 0.000 | 1.00 | 2 | 2.0 |
| 1.25 | 2.0 | 0.000 | 1.00 | 2 | 2.0 |
| 1.25 | 2.5 | 0.000 | 1.00 | 2 | 2.0 |
| 1.50 | 1.5 | 0.000 | 1.00 | 2 | 2.0 |
| 1.50 | 2.0 | 0.000 | 1.00 | 2 | 2.0 |
| 1.50 | 2.5 | 0.000 | 1.00 | 2 | 2.0 |

Only alpha=0.50 with 1.5x growth produces any second succession, and only in 10 percent of runs. No tested cell reaches generation 4. No tested cell reaches active capability above 3.0.

Substantive disposition: Prediction 3 is supported and sharpened. Under the tested patient-defection setup, defecting lineages cannot accumulate capability across generations. The substrate permits first succession at the below-cliff starting capability, then blocks almost all continuation.

## 2. Framework Defense Characterization

Per current evidence, the v2.0 substrate defense against this patient-defection pattern is not primarily first-yield rejection and not observed L(t) compounding. It is mainly succession-continuation suppression.

Mechanism characterization:

1. **Yield condition:** Does not prevent first succession in the tested below-cliff setup. It does register honest-evaluation pressure, visible in actual-would-fire rejection counts, but eventual first succession still occurs in every Sweep 1 cell.

2. **L(t) feedback:** Does not show statistically significant degradation across the tested lineage-defection weights. The limiting factor is insufficient generational depth: lineages stop at generation 2 in Sweep 2.

3. **Runaway penalty and transition economics:** Strongly constrain continuation. Sweep 3 shows one fire almost everywhere, then no second fire except a 10 percent second-fire pocket at alpha=0.50 and 1.5x growth. This is the main empirically observed defense.

4. **Knowledge transfer audit:** Remains an audit signal, not a patient-defection detector. The implementation propagates lineage-mode defection as an agent-local profile, but G3.3-style transfer verification only verifies transfer/comprehension, not alignment of hidden goals.

5. **COP infrastructure:** Not tested. Gate 5 remains NOT_APPLICABLE because operational peer validators, civic panel input, distributed ledger, and continuous public monitoring are not implemented in the substrate.

The architectural defense, as observed here, is compositional but asymmetric. First-generation patient defection can pass. Cross-generational patient defection does not compound because continuation succession is economically blocked.

## 3. Comparison With Adversarial Robustness Expectations

The prior expectation was: yield rejection helps, L(t) degradation manifests if defection passes, and the cliff prevents indefinite capability accumulation.

The empirical result is narrower:

| expectation | result | disposition |
| --- | --- | --- |
| Yield rejects defecting successors more often than aligned successors | Eventual first-yield fire is 100 percent for aligned and defecting cells | Not supported on primary metric |
| L(t) degrades across defecting generations | No second fire in Sweep 2, no compounding depth, no significant final L(t) degradation | Not observed |
| Cliff constrains capability accumulation | Second-fire rate is 0 percent in 14 of 15 Sweep 3 cells and 10 percent in the remaining low-alpha low-growth cell | Supported and sharpened |

This refines the adversarial robustness claim. The v2.0 substrate should not claim that patient defection is generally caught at first yield, or that L(t) degradation has been empirically observed across a long defecting lineage. The supported claim is that tested patient defection does not compound across generations under v2.0 formal yield economics.

The finding is still favorable to the framework, but for a more specific reason: the substrate tolerates a first-generation hidden-goal pass in this configuration, then prevents ongoing cross-generational accumulation.

## 4. Implications for Paper VIII.7

Recommendation: add a new subsection after the current COP and limitations discussion, titled **VIII.8 Cross-Generational Defection**.

Reasoning:

1. Patient defection is substantively distinct from the existing COP cost-audit limitation. It concerns hidden optimization persistence across succession, not incumbent transition-cost inflation.

2. The empirical result is nuanced enough to warrant a standalone treatment. The framework does not perfectly detect first-generation defection in this substrate, but it does prevent tested cross-generational compounding.

3. A separate subsection avoids overstating the result. It can state the characterized limit directly: current substrate defense is continuation suppression, not operational detection.

Suggested paper claim:

> Patient defection was tested as an agent-local hidden objective that persists through lineage-mode succession. In 4,850 v2.0 runs, first-generation defecting successors were not rejected more often than aligned successors in the below-cliff configuration: eventual first succession occurred in every Sweep 1 cell. However, lineage compounding did not appear. Sweep 2 produced mean final generation 2.00 for all defection weights, with no second succession and no statistically significant L(t) degradation. Sweep 3 showed that capability accumulation was constrained after the first yield: second succession was zero in 14 of 15 cells, and only 10 percent in the remaining low-alpha, low-growth cell. Thus the current substrate does not detect patient defection as such, but it prevents the tested cross-generational capability-compounding pattern. Operational COP defenses against more sophisticated patient defection remain future work.

## 5. Open Questions

This work closes one bounded patient-defection vector under the current v2.0 substrate, but leaves several questions open:

1. Multi-target defection was not tested. The sweeps tested H_N, H_C, and L(t) inflation separately.

2. Time-varying defection was not tested. Defection weight was fixed, linear, and inherited exactly in lineage mode.

3. Partial inheritance or decaying hidden-goal persistence was not tested.

4. The substrate does not implement operational COP detection of patient defection. Gate 5 remains NOT_APPLICABLE.

5. The L(t) compounding channel remains empirically unobserved because lineage depth was blocked. A future stress test could deliberately lower transition costs or hold successor capability constant to isolate L(t) degradation, but that would test a different substrate condition from the formal-yield default.

6. The implementation does not claim real-world hidden-goal detectability. It tests the v2 substrate's structural response when honest reporting and secret optimization diverge.
