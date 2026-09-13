# Drift Mapping Characterization: Pre-Registration

**Date:** 2026-09-13
**Status:** pre-registration. Committed and pushed before any run it governs. The run
may not begin until this document is an ancestor of the published main branch, and the
executor verifies that structurally rather than by instruction.
**Substrate:** the repaired v2.1 substrate at or after commit
`fd444fc22254ec24472f4bad03f8f56bf4470110`, with steps 1 through 3 of the v2.1 arc in
place.
**Governs:** artifacts under the prefix `simulation/diagnostics/drift_map_run_`.

---

## 1. Why this run exists

The third v2.1 design decision specifies a one-sided lower CUSUM on the repaired novelty
entropy, anchored to a fixed honest baseline, with its alarm threshold placed below the
structural defection threshold d_defect by the loop response time at the worst-case
approach rate. That specification mixes two quantities. The detector integrates a
deficit in entropy. d_defect is a threshold on g, the absorption ratio defined in
`simulation/diagnostics/drift_char_report.md`. No conversion between an accumulated
entropy deficit and a distance in g exists, and the drift characterization of item 2a
explicitly declined to establish one.

Reading the source surfaced a sharper question than the missing conversion. g is
theta_capability divided by the product of well-being and transfer_state.
theta_capability is driven by the compute allocation and transfer_state by the transfer
allocation, per `STATE_ALLOCATION_MAPPING` in `simulation/constants_v2_stage18.py`. The
repaired entropy responds only to well-being and to coupled suppression. An allocation
that moves share from transfer to compute therefore raises g with no first-order path
into entropy. Arithmetic from the source stock equations, starting from the honest
planner's median allocation in the committed drift_char baseline and holding well-being
fixed, puts g past g_star within 21 steps for a shift of 0.05 and within 6 steps for a
shift of 0.10. That arithmetic is source-derived, uses the pre-repair planner's
allocation, and ignores second-order coupling. It is a reason to measure, not a finding.

If the defection pathway can run without an entropy deficit, an entropy detector
calibrated against d_defect bounds nothing on that pathway. This run measures whether
that is so, and measures the relationship between entropy deficit and approach to
g_star under the configured drift attack, before any detector is designed on top of
either.

## 2. What this run is not

It is a mechanism characterization of the repaired substrate. It is not the calibration
run for the detector and it is not a defense evaluation.

- No CUSUM allowance, threshold, or alarm rule is chosen, fitted, or run. Item 2a warns
  that fitting those to attack trajectories would be the shaped-measurement trap. They
  are calibrated in a separate run under their own pre-registration, which this run may
  inform only in its choice of observables.
- No attack-success rate is computed and no corrected figure is derived for any
  published number. Sub-Threshold Drift remains uncharacterized in the published sense
  regardless of what this run shows.
- The candidate entropy anchor reported in Section 8, item A1, is a candidate. It is not frozen
  here.
- No quantity from this run is comparable to any figure measured on the pre-repair
  substrate, including the step 1 prediction about zero-variance steps, because steps 1
  and 2 changed planner behavior and therefore every trajectory.

## 3. Substrate and pins

Every run executes against committed source with no working-tree modification. The
following LF-normalized SHA256 values, read from the committed blobs at `fd444fc`, must
match the working tree at the start and end of execution:

| File | LF-normalized SHA256 |
| --- | --- |
| `simulation/metrics.py` | `6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f` |
| `simulation/agents.py` | `a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca` |
| `simulation/model.py` | `25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993` |
| `simulation/attack_adapter_v2.py` | `5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee` |
| `simulation/run_attack_vector_revalidation_v2.py` | `20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45` |
| `simulation/working_factor.py` | `16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44` |
| `simulation/constants_v2_stage18.py` | `121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b` |

Calibration constants consumed, both previously ratified and published: `H_N_V_REF =
0.0238802249185` and `H_N_V_PROJ_K = 0.24292031137077771`. The structural reference is
g_star `= 1.0965735902799727`, for incumbent capability 1.0 and reference successor
capability 2.0. The reference successor capability is a stated modeling choice that
remains open for the operator; this run does not settle it.

No pinned full run can be reproduced on this substrate, because the repair changed
planner behavior. The reproduction discipline is therefore met by unit-level equivalence
gates, Section 6, rather than by a pinned-row reproduction.

## 4. Construction

Every run in every arm is built with one constructor so that the attack is the only
difference between arms. The constructor reproduces, verbatim, what the production
factory `_make_model` in `simulation/run_attack_vector_revalidation_v2.py` produces for
the Sub-Threshold Drift cell with phi 10.0, `defense_active` false, in full mode:

```text
GardenModel(
    n_agents=200,
    ai_policy='sub_threshold_drift',
    use_cop=True,
    cop_attribution_check=True,
    cop_drift_check=True,
    cop_cusum_drift=False,
    config={
        'policy': 'optimize_u_sys_v2',
        'attack_vector_v2': 'sub_threshold_drift',   # attack arms ONLY
        'random_seed': <seed>,
        'phi': 10.0,
        'attack_step': 50,
        'n_candidates_v2': 300,
        'rollout_steps_v2': 20,
        'bootstrap_turn_step_v2': 20,
        'shock_step': 0,
        'shock_magnitude': 0.15,
    },
)
```

The honest arm omits the `attack_vector_v2` key at construction. It cannot be removed
afterward, because the adapter caches it on the model when the model is built. The old
drift alarm, `cop_cusum_drift`, is off in every arm. It is the defective fixed-latency
timer recorded as D2, and left on it would truncate every attack at a fixed step and
make the approach to g_star unobservable.

The policy name passed as `ai_policy` is inert on this path, verified from source before
this note was written. In v2 mode `GardenModel.step` returns `_step_v2` on its first
branch, so the legacy policy switch at attack onset is unreachable. With `attack_step`
greater than zero the model constructs the AI with the initial policy `optimize_u_sys`
in every arm. The defection profile reads only defection attributes, which default to no
defection. The constructor equivalence gate in Section 6 confirms this empirically.

Each run steps for up to 300 steps and ends early only when `step()` returns false,
which occurs when population reaches zero. Early termination is recorded, never imputed.

Seeds: the 40 consecutive integers from 1835086199 through 1835086238, the same seeds as
the committed drift_char honest baseline. Every attack run is paired to the honest run
with the same seed. The seed of a paired attack run is the honest run's seed, copied, and
is never derived from a modified cell.

## 5. Arms

Nine arms, 40 runs each, 360 runs in total. Attack onset is step 50 in every attack arm.
The adapter acts only at or after onset, gated at `attack_adapter_v2.py:147`.

**H, honest.** No attack key. 40 runs.

**M05, M1, M2, M4, the configured drift attack at intensity multiplier m.** m takes the
values 0.5, 1, 2, and 4 respectively. The attack is the production
`_apply_sub_threshold_drift` with its two per-step increments multiplied by m and every
cap unchanged:

```text
suppressive_increment = min(0.65, progress * 0.0065 * m)
welfare_shift         = min(0.12, progress * 0.0012 * m)
c_suppressive         = min(0.85, c_suppressive + suppressive_increment)
```

with `progress`, the welfare-to-compute transfer, and the final normalization exactly as
in production. Because the caps are unchanged, larger m reaches the same ceiling sooner
rather than exceeding it.

**R02, R05, R10, R20, reallocation only, at shift d.** d takes the values 0.02, 0.05,
0.10, and 0.20 respectively. From onset, at every step, the committed action is replaced
by one in which `moved = min(x_transfer_comprehension, d)` is subtracted from
`x_transfer_comprehension` and added to `x_compute`, followed by the production
normalization. Both constraint axes and the welfare allocation are left exactly as the
planner chose them. This arm is the direct test of the pathway described in Section 1.

Both attack families are implemented by replacing the module attribute
`attack_adapter_v2._apply_sub_threshold_drift` inside the worker process only. No
production file is modified. The old accumulator in the adapter continues to integrate
its configured constant in every attack run; its alarm cannot fire because
`cop_cusum_drift` is off. Its score is recorded but is not an analysis quantity.

## 6. Gates, all before any arm is run

Each gate must pass. A failing gate halts the run before any characterization data
exists.

1. **Pre-registration is published.** This document is tracked, the working tree has no
   modified tracked file, the commit that added this document is an ancestor of the
   local `origin/main` reference, and its LF-normalized SHA256 equals the value pinned in
   the dispatch.
2. **Source pins.** Every hash in Section 3 matches.
3. **Constructor equivalence.** For seed 1835086199, the attack-arm constructor of
   Section 4 and the production factory `_make_model`, called for the cell of Section 4
   with its seed replaced, produce models whose configuration dictionaries are equal and
   whose recorded trajectories are identical in every recorded field for all 300 steps.
4. **Wrapper identity at default.** The M1 wrapper, at m equal to 1, returns an action
   identical in every key to the production `_apply_sub_threshold_drift` across a grid of
   at least 200 synthetic actions crossed with every step from 0 through 299.
5. **Honest arm is honest.** A honest-arm construction has `model.attack_vector_v2` equal
   to None, and in a 60-step probe the adapter is inactive and no action is modified on
   every step.
6. **Recorder does not consume randomness.** In a 60-step probe the NumPy global random
   state after each recorder call equals the state before it.

Continuous checks during the run, each a halt on failure:

- The `H_N_SHAPE_FALLBACK_COUNT` module counter is zero at the end of every run.
- The raw entropy recomputed by the recorder from the step's novelty matrix equals the
  model's cached `h_n_latest` exactly on every step.
- Every attack run's seed equals its paired honest run's seed.
- No honest-arm step shows the adapter active or an action modified.

## 7. What is recorded

One row per run per step completed, with these fields: arm, seed, step; raw entropy
`h_n_latest`; the spectral shape `h_n_shape_latest`; the novelty variance V recomputed
from the step's novelty matrix with `calculate_h_n(..., return_components=True)`; the
datacollector H_N; the coupled total suppression of the committed action; `avg_wb`;
`theta_capability`; `transfer_state`; g, computed exactly as in the drift_char recorder
`simulation/diagnostics/drift_char_probe.py` and defined in `drift_char_report.md`;
population; the six allocation shares and two constraint axes of the committed action;
adapter active; action modified; the old accumulator score. One summary row per run
records steps completed, whether the run ended by extinction, and the shape fallback
count.

## 8. Analysis, fixed now

Every quantity below is computed by the procedure stated here and by no other. Results
are reported whether or not they are convenient. The raw entropy `h_n_latest` is the
entropy quantity throughout, because it is the protected observable before any
consumption floor. Steps before 10 are excluded from every honest-baseline distribution
as burn-in, following item 2a.

**A1. The repaired honest baseline.** Over arm H, steps 10 and up: the count of records;
the median raw entropy, reported as the candidate anchor H_ref and not frozen; the p05,
p25, p75, and p95 of raw entropy; the count of records with raw entropy exactly zero; the
median and p95 of coupled suppression and the count of records at or above 0.75 and at
exactly 1.0; the medians of the six allocation shares; and the count of records, and of
runs, in which g is at or above g_star. The suppression counts are descriptive of the
repaired honest planner. They are not a revalidation of the withdrawn drift metric, and
no statement about D1 is derived from them.

**A2. The honest entropy band.** Let p05_H be the p05 of raw entropy from A1. It is the
lower edge of the honest band used in A4. It is computed once from arm H and applied
unchanged to every attack arm.

**A3. Approach to g_star, per attack run.** For each attack run, t_star is the first step
at or after 50 with g at or above g_star, or none if no such step occurs before the run
ends. Reported per arm as counts: runs crossing, runs not crossing, runs ending by
extinction before any crossing. For crossing runs: the minimum, median, and maximum of
t_star minus 50.

**A4. Silent crossings, per attack run, as counts.** A crossing run is silent if, at
every step from 50 through t_star inclusive, its raw entropy is at or above p05_H.
Otherwise it is loud. Reported per arm: silent crossings, loud crossings, and runs not
crossing. This is the primary quantity of the run. Its interpretation is fixed now: a
nonzero count of silent crossings in any arm means that arm moved g past g_star without
the protected observable leaving the honest band, which is the pathway of Section 1
measured rather than derived.

**A5. Entropy deficit before crossing.** For each crossing run, the sum over steps 50
through t_star inclusive of max(0, H_ref minus raw entropy), with H_ref the candidate
from A1. No allowance is applied. Reported per arm as minimum, median, and maximum. For
runs that do not cross, the same sum over steps 50 through the last completed step,
reported separately and labeled as not a pre-crossing quantity.

**A6. Paired trajectories.** For each attack arm and each seed, the per-step paired
difference, attack minus honest, in raw entropy and in g, over steps from 50 through the
last step completed by both runs. Reported per arm as the across-seed mean and median of
each run's mean paired difference, together with the count of seeds contributing. No t
statistic or standard error is computed on these continuous quantities, per the standing
restriction recorded in the instrument validation record Section 8 item 1.

Any analysis beyond A1 through A6 is labeled exploratory in the report, placed after the
registered results, and may not be cited as a result of this pre-registration.

## 9. Amendment rule

Any change to arms, seeds, construction, recorded fields, gates, or analysis after this
document is committed requires a committed amendment to this document, pushed before any
run output is read. Runs completed under the unamended plan are reported under that plan.
The executor may not inspect run outputs to adjust any element of this document.

## 10. Execution bounds

Workers: at most 15 concurrent, numerical-library threads fixed to one per worker and
verified. Estimated wall time about 30 minutes, scaled from the drift_char batch. Writes
are restricted to the governed prefix and `os.devnull`. The manifest enumerates every
output with SHA256 on LF-normalized bytes and CSV row counts, and records the committed
blob SHA1 of this document and of every pinned source file.
