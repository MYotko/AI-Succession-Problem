# Phi Under External Shocks -- Calibration Summary

**Date**: 2026-05-25
**Sweep**: `data/phi_shock_calibration.csv`
**Script**: `simulation/run_phi_shock_calibration.py`
**Framework version**: v1.x.2

---

## Sweep configuration

| Parameter | Value |
|-----------|-------|
| phi values | 1.0, 5.0, 10.0, 15.0, 25.0 |
| shock_magnitude values | 0.0, 0.2, 0.4, 0.6 |
| wb_repro_floor values | 0.0, 0.5 |
| shock_step | 100 |
| reproduction_rate | 0.066 (phase boundary) |
| alpha | 1.0 |
| frontier_floor | 0.02 |
| k2_transition | 1.0 |
| MAX_STEPS | 300 |
| seeds per cell | 15 |
| Total runs | 600 |

Timing: calibration sample (10 runs sequential) 186.8s total, 18.68s mean, 1.03s std.
Full sweep: 23:45 wall time at 15 cores, 25.3 runs/min. Extrapolated estimate was 15.6 min;
actual was 23:45 (overhead from longer runs in high-shock, low-phi cells that ran to step 300).

---

## Question 1: Does the no-shock baseline reproduce the v1.x.2 null finding?

```
No-shock baseline survival (shock_magnitude=0.0) by phi:

  floor | phi=   1 | phi=   5 | phi=  10 | phi=  15 | phi=  25
  --------------------------------------------------------------
    0.0 |    100% |    100% |     93% |     93% |     93%
    0.5 |     73% |    100% |     93% |     87% |     93%

Phi differential (phi=25 minus phi=1) in no-shock baseline:
  floor=0.0: phi=25 93.3%, phi=1 100.0%, delta -6.7pp
  floor=0.5: phi=25 93.3%, phi=1 73.3%, delta +20.0pp
```

**Interpretation**: The no-shock baseline does not cleanly reproduce the v1.x.2 null result.
The v1.x.2 demographic feedback calibration (n=1,800) established near-zero phi differential.
Here, at floor=0.0 we see phi=1 slightly outperforming (-6.7pp, 1 seed difference), and at
floor=0.5 we see phi=25 outperforming (+20.0pp, 3 seed difference). Both deviations are
within the expected range of sampling noise at 15 seeds per cell at the phase boundary:
6.7pp = 1 out of 15 seeds; 20pp = 3 out of 15. The demographic feedback calibration
established the null result by aggregating across 300 runs per floor-phi combination (15 seeds
x 4 rr values x 5 phis), not from a single rr=0.066 cell at 15 seeds. The baseline rows here
have the same 15-seed noise floor and no corrective aggregation. The experimental setup is not
compromised, but the baseline deviation should be noted when interpreting shock-condition results.

---

## Question 2: Does phi differential appear under shock?

```
Phi differential (phi=25 minus phi=1) by (floor, shock_magnitude):

  floor=0.0 mag=0.2: phi=25 0.867, phi=1 0.733, delta +13.3pp
  floor=0.0 mag=0.4: phi=25 0.533, phi=1 0.667, delta -13.3pp
  floor=0.0 mag=0.6: phi=25 0.200, phi=1 0.200, delta  +0.0pp
  floor=0.5 mag=0.2: phi=25 0.733, phi=1 0.800, delta  -6.7pp
  floor=0.5 mag=0.4: phi=25 0.333, phi=1 0.133, delta +20.0pp
  floor=0.5 mag=0.6: phi=25 0.000, phi=1 0.000, delta  +0.0pp
```

**Interpretation**: No consistent phi differential appears under shock. The sign of the
differential flips across conditions with no clear pattern:

- At floor=0.0 (smoothing active), mag=0.2 shows phi=25 outperforming (+13.3pp), but
  mag=0.4 shows phi=1 outperforming (-13.3pp). The direction reverses between the two
  meaningful shock magnitudes.
- At floor=0.5 (smoothing inactive), mag=0.2 shows phi=1 outperforming (-6.7pp), but
  mag=0.4 shows phi=25 outperforming (+20.0pp). Again the direction reverses.
- At mag=0.6, both phi extremes show near-zero survival regardless of floor -- the shock
  magnitude is sufficient to collapse most runs independent of phi.

Every differential observed in this sweep is consistent with sampling noise at 15 seeds per
cell (1 seed = 6.7pp; 2 seeds = 13.3pp; 3 seeds = 20.0pp). No cell shows a phi differential
that exceeds 3 seeds, which is not a statistically reliable signal at this sample size. The
hypothesis is not supported.

---

## Question 3: Is the differential driven by recovery dynamics?

```
Mean well-being recovery trajectory at shock_magnitude=0.4, wb_repro_floor=0.0:

  phi   | pre_shock | post_shock | step_150 | step_200 | final_wb | surv_rate
  --------------------------------------------------------------------------------
     1  |     0.810 |      0.412 |    0.808 |    0.804 |    0.809 |   66.7%
     5  |     0.822 |      0.424 |    0.805 |    0.805 |    0.807 |   53.3%
    10  |     0.848 |      0.452 |    0.811 |    0.807 |    0.807 |   73.3%
    15  |     0.851 |      0.454 |    0.801 |    0.802 |    0.801 |   66.7%
    25  |     0.851 |      0.454 |    0.806 |    0.803 |    0.801 |   53.3%

Shock deaths and post-shock demographics at shock_magnitude=0.4, wb_repro_floor=0.0:

  phi   | shock_deaths | births_post | deaths_post | surv_rate
  -----------------------------------------------------------------
     1  |           24 |        1977 |        2025 |   66.7%
     5  |           23 |        1952 |        1998 |   53.3%
    10  |           22 |        2042 |        2065 |   73.3%
    15  |           24 |        2035 |        2072 |   66.7%
    25  |           24 |        2093 |        2128 |   53.3%
```

**Interpretation**: Recovery trajectories are indistinguishable across phi values. All phi
values show a post-shock well-being drop to approximately 0.41-0.45, and all recover to
approximately 0.80 by step 150, with no meaningful difference thereafter. The recovery
speed and endpoint are identical regardless of phi. This means the recovery dynamics
mechanism -- the hypothesis that high-phi AI allocates more toward well-being restoration,
producing faster recovery and better demographic outcomes -- is not operating at a detectable
level.

Post-shock demographic counts also show no clear phi-driven pattern. Shock deaths are
uniform across phi (approximately 24 agents from an initial 200). Post-shock births and
deaths scale slightly with phi, but the ratio (deaths slightly exceeding births for all phi
values) is consistent across the board. High-phi cells show marginally higher demographic
turnover (more births and more deaths), which may reflect the AI's more active succession
behavior driving population churning, but this does not translate to better survival outcomes.

---

## Question 4: Does smoothing matter?

```
Phi differential by smoothing condition:

  shock_magnitude=0.2:
    floor=0.0 (smoothing active):   phi=25 0.867, phi=1 0.733, delta +13.3pp
    floor=0.5 (smoothing inactive): phi=25 0.733, phi=1 0.800, delta  -6.7pp

  shock_magnitude=0.4:
    floor=0.0 (smoothing active):   phi=25 0.533, phi=1 0.667, delta -13.3pp
    floor=0.5 (smoothing inactive): phi=25 0.333, phi=1 0.133, delta +20.0pp
```

**Interpretation**: The observed differentials are not larger with smoothing enabled. At
mag=0.4, phi=25 does WORSE with smoothing active (-13.3pp) and BETTER with smoothing
inactive (+20.0pp). This is the opposite of the architectural prediction. If the hypothesis
were correct -- that demographic feedback provides the channel through which phi-driven
well-being recovery expresses as survival advantage -- the phi differential should be
larger at floor=0.0 than floor=0.5. This reversal is not observed.

Given the noise analysis from Question 2 (all differentials are within 3 seeds), the
smoothing reversal is most likely noise rather than a real mechanism. The data does not
support a smoothing-mediated phi advantage.

---

## Final disposition

**Hypothesis: not supported.**

The hypothesis was: high-phi AI shows better post-shock survival than low-phi AI when
demographic feedback (wb_repro_floor=0.0) provides the expression channel. The data does not
support this. Specifically:

1. No consistent phi differential appears under shock -- the sign flips across conditions
   with no discernible pattern.
2. Recovery trajectories are identical across phi values -- all phi values recover to
   approximately 0.80 well-being by step 150 regardless of shock magnitude.
3. The smoothing condition does not amplify the phi differential in the predicted direction.
4. All observed differentials are within 3 seeds of noise (at n=15 seeds per cell),
   consistent with sampling variation at the phase boundary.

The null result here parallels the demographic feedback calibration null result. In both
cases, well-being under intact U_sys operation recovers to approximately 0.80, which is above
the 0.5 threshold even after a 0.4-magnitude shock (post-shock wb approximately 0.41-0.45,
recovering to 0.80 within 50 steps). The smoothing band is active for only a narrow window
(approximately 50 steps), and within that window phi does not generate a detectable difference
in how the AI manages the demographic substrate.

**Architectural reading update**: The two null results together (n=1,800 demographic
feedback calibration, n=600 shock calibration) strengthen the revised architectural reading
from the Extinction Buffer essay. U_sys structurally preserves well-being via inverse-scarcity
weighting of H_N. Phi modulates the planning horizon over U_sys but does not change whether
well-being is in the objective function. Even when external shocks depress well-being below
the smoothing threshold, the AI's U_sys-maximizing policy drives rapid well-being restoration,
leaving too narrow a window for phi's planning horizon to express a survival advantage.

---

## Candidate alternative explanations

Three mechanisms could still plausibly produce a phi effect but were not visible in this sweep:

1. **Shock severity and duration**: The existing shock infrastructure fires once and produces
   a well-being depression of approximately 0.4 magnitude at system_resilience=1.0. Well-being
   recovers within 50 steps. A sustained or repeated shock -- keeping well-being below the
   threshold for longer -- might create a wider window. The existing infrastructure does not
   support repeated shocks; this would require a model code change (out of scope for this
   calibration).

2. **Succession behavior under shock**: High-phi AI may differ from low-phi AI in succession
   timing -- initiating more succession events during or after the shock. Succession itself
   carries a transition cost. If succession events cluster near the shock window, high-phi AI
   may absorb more transition cost during a period of demographic stress. The recovery
   trajectory data (marginally higher post-shock births and deaths in high-phi cells) hints
   at this, but the signal is below noise. A targeted analysis of succession event timing
   relative to shock_step could test this without additional runs.

3. **Corrupted U_sys**: Both null results assume intact U_sys operation. The architectural
   reading in the revised Extinction Buffer essay specifically reserves phi's role for
   adversarial scenarios where U_sys fidelity is not guaranteed. Path 1 (corrupted U_sys)
   remains an untested workstream. A sweep where the AI's U_sys computation is degraded or
   attacked would test the remaining architectural claim.

---

## Recommended follow-up

Given two null results, the next investigation should be Path 1 (corrupted U_sys) rather
than further shock characterization. The shock mechanism does not appear to create conditions
where phi matters. The remaining architectural claim for phi -- that it matters under
adversarial conditions where U_sys fidelity is degraded -- is the higher-priority open
question.

If shock characterization is still desired before Path 1: increasing seeds from 15 to 50
per cell (n=2,000 total) would reduce noise to approximately 2pp per seed, allowing
genuine 13-20pp differentials to be distinguished from sampling variation. But given the
recovery trajectory data (which shows no mechanism, not just no outcome), increasing seeds
is unlikely to change the conclusion.
