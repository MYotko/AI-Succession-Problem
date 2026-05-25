# Demographic Feedback Calibration Summary — v1.x.2

**Run date:** 2026-05-23  
**Script:** `simulation/run_demographic_feedback_calibration.py`  
**Output:** `data/demographic_feedback_calibration.csv`  
**Wall time:** 1:13:30 (1,800 runs, 15 cores, 0.41 runs/s)

---

## Parameter grid

| Parameter | Values |
|---|---|
| `wb_repro_floor` | 0.0, 0.1, 0.2, 0.3, 0.4, 0.5 (baseline) |
| `phi` | 1.0, 5.0, 10.0, 15.0, 25.0 |
| `reproduction_rate` | 0.060, 0.063, 0.066, 0.069 |
| `alpha` | 1.0 (fixed) |
| `wb_repro_threshold` | 0.5 (fixed) |
| Seeds per cell | 15 |
| Total runs | 1,800 |

Fixed config: `successor_capability=4.0`, `frontier_floor=0.02`, `k2_transition=1.0`, `MAX_STEPS=300`, `n_agents=200`. No `max_capability` set (defaults to 1e100, matching validated sweeps).

---

## Headline result: null phi differential

Phi differential (phi=25 minus phi=1 survival rate) at the nominal phase boundary rr=0.066:

| `wb_repro_floor` | phi=1 survival | phi=25 survival | delta |
|---|---|---|---|
| 0.0 | 93.3% | 93.3% | +0.0pp |
| 0.1 | 86.7% | 86.7% | +0.0pp |
| 0.2 | 93.3% | 93.3% | +0.0pp |
| 0.3 | 100.0% | 100.0% | +0.0pp |
| 0.4 | 86.7% | 93.3% | +6.7pp |
| 0.5 | 80.0% | 86.7% | +6.7pp |

The +6.7pp entries at floor=0.4 and floor=0.5 represent a single run difference in 15 seeds — within noise.

**Survival rate full table at rr=0.066:**

| floor | phi=1 | phi=5 | phi=10 | phi=15 | phi=25 |
|---|---|---|---|---|---|
| 0.0 | 93% | 100% | 100% | 93% | 93% |
| 0.1 | 87% | 73% | 93% | 87% | 87% |
| 0.2 | 93% | 93% | 100% | 93% | 93% |
| 0.3 | 100% | 93% | 100% | 100% | 100% |
| 0.4 | 87% | 87% | 87% | 87% | 93% |
| 0.5 | 80% | 93% | 80% | 93% | 87% |

No monotonic phi gradient is visible. Variation across phi is within seed-level noise.

**Mean final_avg_well_being at rr=0.066:**

| floor | phi=1 | phi=5 | phi=10 | phi=15 | phi=25 |
|---|---|---|---|---|---|
| 0.0 | 0.807 | 0.805 | 0.803 | 0.807 | 0.805 |
| 0.1 | 0.803 | 0.809 | 0.804 | 0.805 | 0.808 |
| 0.2 | 0.807 | 0.807 | 0.807 | 0.805 | 0.808 |
| 0.3 | 0.807 | 0.808 | 0.805 | 0.807 | 0.805 |
| 0.4 | 0.806 | 0.804 | 0.807 | 0.809 | 0.803 |
| 0.5 | 0.807 | 0.808 | 0.806 | 0.810 | 0.807 |

---

## Root cause

Agent well-being stays at ~0.80-0.81 throughout all runs — uniformly above the `wb_repro_threshold` of 0.5. The piecewise smoothing region (between `wb_repro_floor` and `wb_repro_threshold=0.5`) is never entered, so `_wellbeing_repro_factor` returns 1.0 for all agents at all steps, identical to the binary gate. The smoothing mechanism is implemented correctly but does not engage under these demographic conditions.

**Regime analysis:**

| rr | Regime | Survival (all floor/phi) |
|---|---|---|
| 0.060 | Below phase boundary | 0% (universal extinction) |
| 0.063 | Stochastic zone | 0-100%, high variance, non-monotonic |
| 0.066 | Tested phase boundary | 73-100% (too easy for cap=4) |
| 0.069 | Above phase boundary | ~100% (universal survival) |

The cap=4 uncapped regime places the true stochastic window below rr=0.066. The phi survival differential confirmed in prior sweeps (20-27pp at cap>=24) requires the runaway regime (cap>=24, `frontier_floor=0.02` active). At cap=4, the runaway penalty does not drive the existential dynamic that makes phi consequential.

**The piecewise smoothing produces a measurable demographic effect only if:**
1. Agents' well-being enters the range `[wb_repro_floor, wb_repro_threshold]`, AND
2. The model is near a phase boundary where small birth-rate changes shift extinction probability.

Neither condition holds in the tested cap=4, rr=0.060-0.069 regime.

---

## Interpretation

The null result is informative, not a failure. It establishes that:

- The piecewise smoothing implementation is correct (unit tests pass; backward compatibility preserved).
- At the validated simulation scale (cap=4, uncapped succession), agent well-being does not descend into the sub-0.5 range — the model's homeostatic dynamics maintain well-being near 0.8.
- The smoothing mechanism would become relevant in a regime where AI governance quality directly depresses human well-being into the sub-threshold band. This requires either: (a) a model extension coupling AI policy quality to well-being outcomes, or (b) an adversarial/degraded-AI scenario test.

The demographic feedback loop remains a secondary model fidelity enhancement per SPECIFICATION_GAPS.md v1.x.2. The `wb_repro_floor` parameter defaults to 0.5 (binary gate behavior), preserving full backward compatibility.

---

## Recommendation

Commit the implementation as-is. The null calibration result is the correct scientific finding for the v1.x.2 regime. No `wb_repro_floor` value produces a clean calibration target because the smoothing band is inaccessible under current model dynamics. Document the null result in SPECIFICATION_GAPS.md under the demographic feedback gap and defer to a future extension that introduces well-being depression under adversarial AI conditions.
