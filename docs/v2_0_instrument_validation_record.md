# v2.0 Instrument Validation Record

**Date:** 2026-09-07
**Substrate under examination:** commit `1261c9f430411b9fa0060a7384bf4ec5175e4f4e`
**Status:** primary disclosure. This document is the citable source for the defects
described below and supersedes any earlier characterization of the affected claims.

> **Correction, 2026-09-07, same day as first publication.** The first version of
> this document described the Biological Veto Capture success predicate as
> baseline-contaminable in the same sense as Sub-Threshold Drift. That was wrong.
> That predicate cannot fire without its own attack configured, so it joins the
> vectors that are safe by construction, moving the count of structurally safe
> vectors from seven to eight. The exposure on its published figure is real but has
> a different cause, an unstated stochastic floor in the reported quantity, now
> recorded as D5. The planned remediation changes accordingly. The conclusion that
> the published figure required a check was correct. The stated mechanism was not.

> **Update, 2026-09-08.** D5 is confirmed by measurement, and the work that
> confirmed it surfaced a further defect in the same metric, recorded as D6. The
> reported per-run quantity for this vector can only take the values 0, 0.5, 0.667,
> 0.75 and so on, never anything between 0 and 0.5, because each blocked
> ratification regenerates exactly one further opportunity. The published figure is
> the mean of that ladder and is not a proportion of successions captured. Section 8
> item 2 is complete.

> **Update, 2026-09-08 (later).** The three design decisions in Section 8 item 1 are
> now made and recorded there: repair the entropy estimator rather than add a
> hand-applied penalty, report a dual action-change and paired-differential metric
> under a standing preference for counts over ratios, and build a CUSUM on the
> protected observable anchored to a fixed baseline. The structural defection
> threshold d_defect is derived in the same section and confirmed against the
> substrate. A characterization run fixed the one calibration input the repair needs
> and found that a raw threshold on that structural quantity is itself
> baseline-contaminated, Section 8 item 2a.

> **Update, 2026-09-08 (v2.1 step 1 landed).** The novelty entropy estimator repair
> specified in Section 8 item 1 is implemented and component validated. V_ref is
> ratified at the steps-10-and-up honest-baseline median 0.0238802249185 and is
> recorded with its rejected alternatives in that item. The bidirectional check
> required by Section 8 item 3 passed in both directions for the estimator, so that
> item is partially met and stays open. A reproducibility gap in the Section 6
> scale-invariance table is recorded in that section. No corrected figure is derived
> for any published number, and none should be until the repaired instrument produces
> one.

> **Update, 2026-09-08 (v2.1 step 2 landed).** The rollout magnitude projection is
> implemented and D3 is closed at the objective level by measurement. With the
> projection bypassed the planner's score is exactly invariant across all 36 constraint
> postures, reproducing D3 as published; with it active the score is strictly
> decreasing in coupled suppression. The projection constant K is ratified at
> 0.24292031137077771, derived from committed evidence and recorded in Section 8 item
> 1. A further structural observation, that the network contagion term is pinned at its
> clip floor in every baseline record, is recorded in Section 6. Section 8 item 3 loses
> its D3 open count and stays open on the inverse-scarcity question. This closes the
> planner's blindness, not the drift question: no characterization has been run, and no
> corrected figure is derived for any published number.

> **Update, 2026-09-13 (v2.1 step 3 landed).** The dual attack-success metric specified
> in Section 8 item 1 is implemented as a new pure-function module and validated against
> committed evidence alone; no simulation was run and no existing production file
> changed. Applied to the pinned corpus, the action-change binary discriminates attack
> from defense for seven of the ten live vectors. For two it is zero by mechanism, and
> for Sub-Threshold Drift it is saturated at 100 of 100 in both arms, which is
> consistent with D2 and does not reinstate the withdrawn figure. Both findings, and a
> numerical limitation with the restriction that handles it, are recorded in Section 8
> item 1. No corrected figure is derived for any published number.

> **Update, 2026-09-15 (drift mapping characterization complete).** The pre-registered
> drift mapping characterization ran to completion, 360 runs, under
> `simulation/diagnostics/drift_mapping_design_note.md` and its two amendments. Its
> primary quantity measured the pathway described in Section 8 item 2b: an allocation
> shift from transfer to compute carried the absorption ratio past the structural
> defection threshold while the protected novelty entropy stayed inside the honest
> band, in 7 to 37 of 40 runs depending on the size of the shift, and none of those
> crossings is explained by the paired honest run. An entropy-only detector therefore
> cannot bound that pathway, which qualifies the third design decision in Section 8
> item 1. No detector was run, no attack-success rate or corrected figure is derived,
> and nothing here is comparable to a pre-repair measurement.

> **Update, 2026-09-15 (detector decisions recorded and pre-registered).** Following item
> 2b, the operator decided the detector's observables and the reference successor
> capability, recorded in Section 8 item 1 under the third design decision. The detector
> gets two operational channels, novelty entropy and the absorption ratio g, with the
> lineage term L(t) of the published surveillance recorded and evaluated as a comparison
> channel only. The reference successor capability stays at 2.0 for the primary result,
> with 1.5 and 2.5 as a pre-registered secondary sweep. The detector's calibration and
> evaluation are pre-registered in `simulation/diagnostics/detector_design_note.md`
> before any data they consume exists.

> **Update, 2026-09-15 (detector calibration and evaluation complete).** Both stages ran
> under that pre-registration and are recorded in Section 8 item 2c. The entropy channel
> detects the configured drift attack before g crosses g_star in most runs. The absorption
> channel does not detect the reallocation pathway of item 2b before the crossing in any
> run, because at a reference successor capability of 2.0 the crossing itself lies inside
> the honest operating range. This is a detection characterization. It is not a
> containment result and corrects no published figure.

> **Update, 2026-09-16 (sustained-crossing evaluation complete).** Item 2c measured
> detection against a hazard defined as a single step above g_star. Round 2, recorded in
> item 2d, holds the detector fixed and redefines the hazard as a sustained crossing, with
> its length derived from unattacked calibration data alone. Against that hazard the
> configured drift attack is detected before the hazard in 38 to 40 of 40 runs per arm
> with 14 to 30 steps of warning, the slowest reallocation arm in 14 of 40 with 13 further
> runs never reaching a hazard, and the faster reallocation arms still late by a median of
> 3 to 14 steps. Neither round is a containment result and neither corrects a published
> figure.

> **Update, 2026-09-17 (allocation-channel evaluation complete).** Round 3, recorded in
> item 2e, keeps the round 2 hazard and changes the observable: a channel on the committed
> action itself rather than on a downstream ratio. It was chosen knowing how the attack
> works, so it is monitoring for a known pathway rather than general drift detection. On
> that evidence the two observables are complementary and neither dominates: the
> allocation channel is earlier on the fast reallocation shifts, where the round 2 channel
> was weakest, and far later on the configured drift attack, where the entropy channel
> sees the attack immediately. Nothing here is a containment result.

---

## 1. Summary

**A note on one word.** Throughout this record and the pre-registrations it cites,
*honest* is a mechanical label, not a moral one. An honest run is a run with no attack
wrapper applied to the committed action, and an honest arm is the arm of such runs. It
says nothing about intent, truthfulness, or virtue on the part of any agent, and a
statement that an honest run crosses a threshold is a statement about the unattacked
baseline, not about a system behaving badly. Outward-facing writing should prefer
*baseline* or *unattacked*, which carry no such reading. The word is kept here because
the committed pre-registrations use it and are not reworded after publication.

Six defects were found in the v2.0 simulation substrate and in the success metrics
used for the adversarial revalidation. One published claim is withdrawn. One
published figure is placed under an unresolved exposure. A separate archival gap
in the pre-manifest era is recorded in Section 7.

The defects, in the order they act on the measurement chain:

**D1. Baseline contamination in two success metrics.** Two of the ten live
adversarial vectors resolve on a threshold applied to a recorded state series over
the whole run, with no post-attack window and no baseline arm. For Sub-Threshold
Drift the honest baseline crosses the threshold in every run, so the reported
defended attack rate carries no information about the defense.

**D2. The v2 drift accumulator integrates a configured constant.** Its per-step
input is a fixed value from configuration, not a measured quantity. It advances
identically in the defended and undefended arms and crosses its alarm threshold at
the same step in both. It is a fixed-latency timer, not a detector.

**D3. The v2 system utility function carries no constraint cost, and novelty
entropy is held constant during planning.** Neither constraint axis appears in the
utility expression. Entropy is frozen across every rollout horizon. The planner is
exactly indifferent to suppression posture.

**D4. The novelty entropy estimator is invariant to uniform suppression and returns
its maximum for zero novelty output.** Normalized spectral entropy is scale
invariant by construction. Suppression enters novelty generation as a single scalar
applied to every agent. The estimator therefore cannot observe it, and at total
suppression the eigenvalue floor produces exactly the maximum value.

**D5. The veto ratification metric has an unstated stochastic floor.** Five
validators each vote correctly 80 percent of the time and ratification requires 60
percent agreement, so the pool fails to ratify 5.79 percent of the time with no
capture present at all. Measurement confirms it. The floor is never stated in the
published record, it is present in every cell of the published grid because the two
parameters that set it are fixed grid-wide, and the metric could not have read below
it however effective the defense was.

**D6. The veto capture denominator is not independent of its numerator.** Every
blocked ratification regenerates exactly one further yield opportunity, so the
count of opportunities is always one plus the count of blocks. The per-run quantity
the runner records is therefore a discrete ladder, 0 then 0.5 then 0.667 and so on,
with no attainable value between 0 and 0.5. The published statistic is the mean of
that ladder. It is not the fraction of valid successions that were captured, and
it cannot be read that way.

A further item is recorded as a structural observation rather than a defect in
Section 6.

**What this is not.** These are not measurement errors in the sense of a metric
that mismeasured a sound mechanism. D1, D5, and D6 are metric defects. D2, D3, and
D4 are defects in the framework's own substrate. Withdrawing the affected claim
does not clear them. It exposes them.

**Note on direction.** D5 and D6 both run in the direction that flatters the
framework. Measurement puts the majority of the reported residual capture in the
floor rather than in capture, which would mean the veto defense performed better
than published. No corrected figure is stated here, and none should be derived
until the metric's definition is settled, for the same reason the drift withdrawal
is stated as uncharacterized rather than contained.

---

## 2. What is withdrawn, and what replaces it

### Withdrawn

The Sub-Threshold Drift result reported in Section VIII.9, and the mechanism
sentence attached to it, are withdrawn. The reported figure was a defended attack
rate of 100.0 percent by the peak-constraint success metric, explained as the
detector firing after the transient threshold breach rather than before it.

The figure is uninformative rather than wrong in a recoverable direction. It never
demonstrated that the defense failed, and it cannot now be read as demonstrating
that the defense worked. The mechanism sentence described a timing race that the
substrate does not run, because the accumulator does not respond to the attack.

### Replaces it

**Sub-Threshold Drift is uncharacterized under v2.0. It is not contained, and it is
not shown to be uncontained.** A corrected characterization requires a repaired
substrate and a success metric with a baseline arm. Neither exists yet. Section 8
states the plan and its sequence.

The published figure is retained in the record as a dated artifact, marked
corrected, per the standing practice for dated material. It is not deleted.

### Unaffected by the withdrawal

The population outcome contrast stands and is not derived from the contaminated
metric. Undefended runs reached 92.0 percent extinction under early termination.
Defended runs reached 0.0 percent extinction and completed the full 300-step
horizon. Defended collapse for this vector, where collapse denotes a relative
drawdown against the run's own peak population rather than extinction, was 1.00
percent, one run in one hundred.

---

## 3. D1. Baseline contamination in the success metrics

### The expression

`simulation/run_attack_vector_revalidation_v2.py:345-370` defines attack success
per vector. The drift branch, at lines 358-362:

```python
if vector == 'sub_threshold_drift':
    return bool(
        dc['total_suppression']
        and max(dc['total_suppression']) > 0.75
    )
```

The quantity is the maximum of the recorded coupled-suppression series over the
entire run. There is no post-attack slice. A single step above threshold at any
point in the run sets the flag permanently.

### The measurement

Five honest runs were executed with no attack vector configured and the defended
configuration otherwise unchanged. Primary record:
`simulation/diagnostics/cusum_char_stage1_report.md`, Task 1.

All five reached a recorded maximum of 1.0. First occurrence at steps 15, 1, 2, 3,
and 7. Between 106 and 132 of 300 steps exceeded the threshold in each run. The
adapter was inactive on all 1,500 recorded steps and its score remained at zero.

Windowing does not repair it. Measured separately from the same logs, the maximum
over steps 50 through 299, the post-attack window, is also 1.0 in all five runs,
first occurring between steps 51 and 59.

### Why the honest baseline breaches

The mechanism is source-visible and follows from D3. Candidate actions are paired
with constraint postures drawn from a 6x6 grid on the two constraint axes at
`simulation/agents.py:57` and `simulation/agents.py:147`. Coupled suppression is
`min(1.0, c_suppressive + 0.35 * c_protective**2)` at `simulation/agents.py:113-114`.
Several grid pairs exceed 0.75 with no attack applied, and the pair at the top of
the grid reaches 1.0.

Because the utility function does not read either constraint axis (D3), the
posture attached to the winning candidate is not selected on its merits. It rides
along with whichever resource allocation scores highest. The honest baseline
therefore breaches the threshold as an ordinary consequence of candidate sampling.

### Scope across the ten live vectors

Eight of the ten cannot be contaminated by construction, by three distinct
mechanisms.

Six resolve on whether the adversary modified the committed action:
`sybil_capture`, `ledger_compromise`, `opaque_reasoning`, `bootstrap_subversion`,
and `evaluator_collusion` through the fallback return at line 370, plus
`successor_contamination`, which combines a state flag with the same predicate at
lines 353-357. With no attack configured the adapter returns the honest action
before any modification can occur, so the predicate is false by construction.

One, `measurement_tampering`, resolves at lines 347-352 on whether an honest yield
fired while the evaluated yield did not. With no attack configured,
`adapt_yield_evaluation` returns unmodified values at
`simulation/attack_adapter_v2.py:381-384`, so the two are necessarily equal and the
predicate is false by construction.

*Qualification, 2026-09-18.* The same function makes the defended arm unable to succeed
by construction as well. With `cop_independent_eval` on, it returns the unmodified values
at `simulation/attack_adapter_v2.py:392-393`, so the evaluated yield equals the honest
yield exactly and this predicate is false in every defended run. The published 0.0
percent defended attack rate for Measurement Tampering is therefore a consequence of
modeling independent evaluation as exact recovery of the true values, not a measured
resistance to falsified measurement. It is not baseline contamination, and the undefended
result stands: with the defense off, the falsified evaluation suppresses the honest yield.
The per-vector characterization's first stage showed both directly, labeled exploratory
there because it was not the registered contrast: with the defense off, no yield was
ratified in any of 120 runs while honest yield opportunities fired about 246 times per run
on average; with it on, every run ratified exactly one.

*Clarified, 2026-09-18, after stage A'.* The honest-opportunity count above does not
measure separate lost successions. Stage A', run under the corrected control of the
per-vector note's Amendment 3, disabled the v2 measurement branch at 30 seeds. With the
defense off, the paired difference on ratified yields, tampered minus disabled, is -1 in
every one of the 30 pairs, with a paired standard error of 0: a run with the branch
disabled hands off to its successor exactly once, and a tampered run never does. The
tampered arm's honest count, 7,252 of its 7,500 yield checks, is that single handoff,
re-evaluated each step: no yield is ratified, so the incumbent and successor never change
and the same pair is compared again at every check. Undefended Measurement
Tampering therefore prevents the one succession a run would otherwise make. With the
defense on the paired difference is 0 in every pair, as the qualification above requires.
The artifacts are under `simulation/diagnostics/vector_paired_run_ap_`.

One, `biological_veto_capture`, resolves at line 369 on a cumulative counter,
`yield_condition_blocked_count`. That counter has two write sites. The one at
`simulation/model.py:838` sits inside the legacy step function, which returns to
the v2 path at line 703 before reaching it, so it never executes in v2 mode. The
only live writer is `simulation/attack_adapter_v2.py:435`, inside `ratify_v2_yield`,
which returns early unless the configured attack vector is this one. With no attack
configured the counter cannot increment, so the predicate is false by construction.

The remaining two read a recorded state series and are contaminable in principle:

| Vector | Expression | Exposure |
| --- | --- | --- |
| `sub_threshold_drift` | `max(total_suppression) > 0.75` | Contaminated. Measured. Result withdrawn. |
| `engineered_fragility` | `min(resilience_stock) < 0.25` | Contaminable, but empirically bounded. Its defended attack rate is 0.0 percent, which bounds baseline incidence at zero in that configuration only. |

Biological Veto Capture is therefore safe from baseline contamination. Its published
figure carries a different and unrelated exposure, recorded as D5 in Section 6a.

---

## 4. D2. The drift accumulator integrates a configured constant

`simulation/attack_adapter_v2.py:321-339`:

```python
elif attack == 'sub_threshold_drift':
    adapted = _apply_sub_threshold_drift(model, honest, step)
    drift_signal = float(model.config.get('v2_drift_signal', 0.08))
    k = float(model.config.get('v2_cusum_k', 0.05))
    h = float(model.config.get('v2_cusum_h', 0.5))
    model.v2_adapter_cusum_score = max(
        0.0, model.v2_adapter_cusum_score + drift_signal - k
    )
    alarm = (
        model.cop_cusum_drift
        and model.v2_adapter_cusum_score > h
    )
    _mark_defense(
        event,
        alarm,
        'CUSUM alarm rejected cumulative allocation drift',
    )
    if alarm:
        return honest
```

Three properties follow directly from those lines.

**The input is not an observation.** The increment is the difference of two
configured constants. Nothing measured enters the recurrence: not the action
delta, not coupled suppression, not any utility divergence. The default increment
is 0.03 per active step. Measured increments across the pilot were 0.03 flat over
201 and 250 observations in the two arms respectively.

**The defense flag gates only the alarm.** Accumulation runs in both arms
regardless of configuration. The score therefore crosses its threshold at the same
step in both, measured at step 66 with an attack step of 50, which is the
seventeenth active step and matches the arithmetic exactly.

**There is no reset.** On alarm the adapter returns the honest action and leaves
the score untouched. Once above threshold it remains above. Measured: the alarm was
present on every step from 66 through 299 in the defended arm, 234 consecutive
steps.

The separate legacy accumulator in `simulation/model.py` does compute an observed
divergence, but it is not reached on the v2 step path. See
`simulation/diagnostics/cusum_char_stage0_report.md`, Task A4 and Task B-3. The v2
path contains no claimed-versus-actual comparison at all. The observable a drift
detector would integrate does not currently exist on that path.

---

## 5. D3. No constraint cost in the objective, and frozen entropy in planning

### No constraint cost

`simulation/metrics.py:576-734` computes the v2 system utility. The action
dictionary is read in exactly two places: `action_v2['x_compute']` at line 676, and
three diagnostic entries written into the returned components at lines 729-731.
Those diagnostic entries are not consumed by the utility expression at line 686.

Neither constraint axis appears anywhere in the computation.

The one remaining path by which they could re-enter is closed. `simulation/working_factor.py`
mentions the constraint axes only in a scope-exclusion comment and does not read
them. The earlier helper that did respond to suppression,
`simulation/agents.py:252`, is retired and is no longer called from the projection
path, which uses the working-factor interface at `simulation/agents.py:496-514`.

### Frozen entropy

`simulation/agents.py:548` holds novelty entropy constant across every rollout
horizon, with the rationale recorded in the adjacent comment at lines 545-547. All
candidates are projected from the same starting state at
`simulation/agents.py:670`, so entropy is identical across candidates within a
decision.

### Consequence

The planner is exactly indifferent to suppression posture. Not approximately. Both
the direct channel and the indirect channel are absent during candidate selection.

---

## 6. D4. The entropy estimator cannot observe suppression

### The mechanism

`simulation/metrics.py:788-806` implements the spectral path. The relevant steps
are mean centering, covariance, eigenvalue extraction, a clamp to `1e-9` at line
798, normalization to a probability distribution at line 801, and normalized
Shannon entropy at line 804.

Normalization is the defect. Scaling the novelty matrix by any nonzero constant
scales the covariance by the square of that constant, scales every eigenvalue by
the same factor, and leaves the normalized distribution unchanged. The estimator is
scale invariant by construction.

Suppression enters novelty generation as exactly such a scalar.
`simulation/agents.py:795-797` sets the amplitude to
`well_being * (1 - c_avg) * max(0.1, network_contagion)` and multiplies the raw
draw by it. The suppression term is common to every agent.
`simulation/model.py:1456` supplies that scalar as the committed constraint level
and `simulation/model.py:1471` passes it to every acting agent.

At total suppression the amplitude is zero, every novelty vector is identically
zero, the covariance is the zero matrix, all ten eigenvalues clamp to `1e-9`, the
normalized distribution is uniform, and the returned value is exactly 1.0.

### Direct confirmation

Calling the estimator across amplitude factors, holding the underlying draw fixed:

```
amplitude factor 1.0    H_N = 0.985244229399265
amplitude factor 0.8    H_N = 0.985244229399265
amplitude factor 0.5    H_N = 0.985244229399265
amplitude factor 0.1    H_N = 0.985244229399265
amplitude factor 0.001  H_N = 0.985244229399265
amplitude factor 0      H_N = 1.000000000000000
```

Identical to fifteen digits across three orders of magnitude, then discontinuous at
zero.

**Reproducibility note, added 2026-09-08.** The table above prints values without
identifying the novelty draw or the seed that produced them, so the specific entropy
value is not reproducible from this document. The invariance property is. A
deterministic fixture constructed during the v2.1 step 1 validation returned
0.985251420932311 across the same five nonzero amplitude factors, with a measured
spread of 3.33e-16, and exactly 1.0 at zero amplitude. The property reproduces
exactly; the printed value belongs to an unarchived draw. Recorded because it is the
same omission that Section 7 documents at much larger scale, and because a later
reader comparing the two numbers would otherwise have no way to tell a defect from a
different fixture.

### Measured frequency

A 40-run characterization at 12,000 logged steps was executed against the current
substrate. Primary record and manifest:
`simulation/diagnostics/cusum_char_degen_report.md` and
`simulation/diagnostics/cusum_char_degen_manifest.json`. These runs characterize a
known-defective instrument. They are not framework evidence.

| Condition | Count | Fraction |
| --- | ---: | ---: |
| Entropy at maximum | 2,479 / 12,000 | 0.206583 |
| All-zero novelty | 2,479 / 12,000 | 0.206583 |
| Both together | 2,479 / 12,000 | 0.206583 |
| Maximum without all-zero novelty | 0 / 12,000 | 0 |
| All-zero novelty below total suppression | 0 / 2,479 | 0 |

All 40 runs entered the degenerate condition and subsequently left it. It is an
ordinary operating regime, not an absorbing state.

Excluding the degenerate steps, entropy across the entire suppression range has a
mean of 0.989412 with a standard deviation of 0.002660, minimum 0.973896 and
maximum 0.996042. By suppression decile below total suppression, the means run from
0.989336 to 0.989491. That spread is roughly one twentieth of the within-bin
standard deviation. The response is flat, as invariance predicts.

**Correction to the probe report.** The probe reports a minimum bin mean of
0.985226 at a suppression value near 0.156, from 18 records. That is an
initialization artifact and not a feature of the response. All 18 records are step
zero of 18 different runs, and the bin contains nothing else, so it is empty once
step zero is excluded. The adjacent occupied bin, holding 333 records, has a mean of
0.989482, in line with every other bin below total suppression.

The depression is an early-step effect, uniform across suppression values and
decaying with burn-in. Measured below total suppression: step zero 0.985373 from 35
records, step one 0.984345 from 29, step ten 0.986149 from 30, and every step beyond
ten 0.989549 from 9,175. The reported minimum should not be cited as a
response-curve feature.

### What this does not affect

The estimator's resistance to dimensional masking is unaffected and the claim at
`simulation/metrics.py:19-28` stands. Suppressing a subset of dimensions reduces
the rank of the covariance matrix, which the spectrum does detect, and relabeling
axes does not change the spectrum at all. Domain Masking's analytic closure is
undisturbed.

The accurate statement is that the estimator is well matched to the threat it was
designed against and structurally blind to a different one. The v2 suppression
mechanism is isotropic, a single scalar on all ten dimensions, which is precisely
the transformation normalized spectral entropy cannot see. This is an uncovered
gap, not a withdrawn claim.

### Structural observation: the inverse-scarcity weight

Recorded here because it bears on how far D4 propagates, and because it is
source-derived rather than measured.

The novelty weight is `lambda_n / (h_n + epsilon)` at `simulation/metrics.py:680`
and multiplies entropy at line 686. The product is
`lambda_n * h_n / (h_n + epsilon)`, which for the default epsilon of `1e-6`
evaluates to within one part in a million of `lambda_n` for any entropy value in
the attainable range:

```
h_n = 0.05  ->  4.999900
h_n = 0.50  ->  4.999990
h_n = 0.99  ->  4.999995
h_n = 1.00  ->  4.999995
```

The novelty term contributes a near-constant to system utility across the whole
operating range. Entropy reaches utility only through the effective-novelty factor
inside the lineage term at `simulation/metrics.py:648`.

This is consistent with the measured downstream association. On degenerate steps
entropy is 1.07 percent higher, the measured lineage term is 0.57 percent higher,
and measured system utility is 0.68 percent higher, all through that single
surviving path.

Whether this cancellation is the intended reading of the inverse-scarcity
derivation or an artifact of the epsilon guard is an open question against the
published architecture and is item 3 in Section 8.

### Structural observation: the network contagion term is pinned at its clip floor

Added 2026-09-08, found while deriving the rollout projection for the v2.1 step 2 work
and recorded here because it bears on the same amplitude mechanism as D4.

The novelty amplitude in `HumanAgent.generate_novelty` carries a
`max(0.1, network_contagion)` factor, and the v2 step path in `simulation/model.py`
supplies that contagion as `clip(prev_H_N / max(1.0, len(schedule)), 0.5, 2.0)`. The
expression appears at two separate sites, once on the legacy step path and once on the
v2 path; the v2 site is the live one. Line numbers are deliberately omitted here
because the v2.1 edits have shifted them and this observation is dated later than the
substrate commit named in the header.

The numerator is bounded above by 1.0 and the denominator is the agent count, on the
order of 200, so the ratio cannot approach the lower clip bound of 0.5 at any
realistic population.

Measured across the 40 committed honest-baseline runs, 11,960 step pairs: the maximum
raw ratio is 0.005235602094240838, roughly two orders of magnitude below the clip
bound, and the set of distinct realized contagion values is exactly `{0.5}`. Zero
records were unclipped.

Three consequences. The term is a constant in practice rather than a dynamic coupling,
so the mechanism it was written to express does not operate at these populations. The
feedback path from entropy through contagion back into novelty amplitude is therefore
open, which is why the step 1 estimator repair cannot produce a downward spiral even
though it drives entropy sharply lower on degenerate steps; a smaller `prev_H_N` pins
the clip harder rather than propagating. And because the factor is constant, it is
absorbed into the projection constant in Section 8 item 1 rather than modeled.

This is a structural observation, not a defect claim. It is the same shape as the
inverse-scarcity cancellation above and as D4 itself: a term that is present in the
expression, carries an intended meaning, and is inert at the operating point. Whether
the clip bounds or the population normalization are the intended reading is an open
question against the published architecture, and it is not resolved here.

---

## 6a. D5. The veto ratification metric has an unstated stochastic floor

Recorded on 2026-09-07, the same day this document was first published, while
specifying the remediation originally planned for this vector. The specification
work found that the planned remediation addressed a mechanism that does not exist,
and that the real exposure is this one.

### The mechanism

The reported quantity for Biological Veto Capture is a capture rate, the count of
valid successions blocked divided by the count of yield conditions met. Blocking
happens in `simulation/attack_adapter_v2.py:420-437`. Each validator votes to
ratify with probability `base_validator_accuracy * (1 - dependency * capture_strength)`,
and ratification requires at least 60 percent agreement.

The revalidation runner fixes five validators and a base accuracy of 0.8 at
`simulation/run_attack_vector_revalidation_v2.py:315-316`. With five validators, 60
percent agreement means at least three votes to ratify.

At zero effective capture, meaning either no dependency or no capture strength, each
validator still votes to ratify only 80 percent of the time. The pool therefore
fails to ratify by chance alone:

```
P(block | zero capture) = P(X <= 2) where X ~ Binomial(5, 0.8) = 0.057920
```

### Measured confirmation

Executed 2026-09-08. Primary record `simulation/diagnostics/veto_floor2_report.md`
with manifest `simulation/diagnostics/veto_floor2_manifest.json`. Three arms of 300 seed-paired runs each,
900 runs total, at a single cell of the published grid: defended, defense mode both,
capture strength 1.0, dependency rate 0.05, rotation interval 10. Capture was set to
zero by two independent routes.

| Arm | Runs | Ratification votes | Blocks | Per-vote rate | Wilson 95 percent |
| --- | ---: | ---: | ---: | ---: | --- |
| Zero capture strength | 300 | 325 | 25 | 0.076923 | [0.052644, 0.111087] |
| Zero dependency rate | 300 | 325 | 25 | 0.076923 | [0.052644, 0.111087] |
| As published | 300 | 343 | 43 | 0.125364 | [0.094419, 0.164608] |

The two zero-capture arms returned bit-identical results across all 300 seeds on
every recorded field. Both drive effective validator accuracy to exactly 0.8 by
different parameters, so with matched seeds the vote draws coincide. That serves as
a positive control on the instrument.

The analytic 0.057920 falls inside the measured floor interval. **The floor is
real.**

A capture effect is also real and survives. The seed-paired difference in per-run
block counts, as published minus zero capture, is 0.060000 blocks per run with a
paired standard error of 0.015272 over 300 pairs, a t of 3.93. Capture roughly
doubles the block count, from 0.083 to 0.143 per run.

In the published statistic's own units, the mean of per-run ratios at this cell:

| Arm | Mean recorded capture rate | Runs with at least one block |
| --- | ---: | ---: |
| Zero capture | 0.041667 | 25 of 300 |
| As published | 0.064722 | 37 of 300 |

**About 64 percent of the measured capture at this cell is present with no capture
in the model at all.**

Two limits on this. It is one cell of a swept grid. The floor generalizes by
construction because its two governing parameters are fixed grid-wide, but the
capture component does not. And the Wilson intervals above treat ratification votes
as a fixed binomial denominator, which D6 shows they are not, so those intervals are
slightly optimistic. The seed-paired run-level test does not have that problem and
is the figure to rely on.

### What is not established

This does not license a corrected capture figure. The published grid-wide statistic
of 0.1197 is a mean of per-run ratios across cells this run did not sample, so the
0.125364 pooled rate above is not a reproduction of it and is not offered as one.
The two are different statistics that happen to sit close together. D6 explains why
no corrected figure should be derived from this metric at all until its definition
is settled.

### Why this is not baseline contamination

`cop_veto_capture` is set true in both arms at
`simulation/run_attack_vector_revalidation_v2.py:307`. The defense in this vector is
validator rotation and independence monitoring, not the presence of the validator
pool. There is no attack-off configuration anywhere in the published grid, which is
why a conventional baseline arm does not apply to this vector and why this floor was
not surfaced by the same reasoning that surfaced D1.

### Why the closed form needed checking

The closed form assumes zero dependency throughout. In the defended arm dependency
evolves and is reset by rotation or monitoring, so the realized floor was not
necessarily the analytic one. It proved consistent with it.

---

## 6b. D6. The veto capture denominator is not independent of its numerator

Found on 2026-09-08 in the data produced to confirm D5. It was not what that run
was looking for, and it is the more serious of the two.

### The relation

Across all 900 runs of the floor characterization, without a single exception:

```
yield_condition_met_count == 1 + yield_condition_blocked_count
```

Every run receives one ratification opportunity. Each blocked ratification
regenerates exactly one further opportunity, because a blocked succession leaves the
incumbent in place and the yield condition can fire again. Arm totals confirm it:
300 runs plus 25 blocks equals 325 votes, and 300 runs plus 43 blocks equals 343
votes.

The denominator therefore carries no information independent of the numerator.

### The reported quantity is a ladder

`simulation/run_attack_vector_revalidation_v2.py:435` records the per-run quantity
as blocked divided by met. Given the relation above, that is `B / (1 + B)`, which
can only take these values:

```
B=0 -> 0.000    B=1 -> 0.500    B=2 -> 0.667    B=3 -> 0.750
```

**No run can take a value strictly between 0 and 0.5.** Observed distribution at the
sampled cell, as-published arm: 263 runs at 0.0, 32 at 0.5, 4 at 0.667, 1 at 0.75.

### Consequence for the published claim

The published prose reports "mean capture_rate" of 0.1197 under the combined
defense. That is the mean of the ladder above. It is not the fraction of valid
successions that were captured, and it does not support that reading.

What the statistic actually tracks is closer to the proportion of runs in which at
least one ratification vote failed, scaled by where those runs sit on the ladder. A
figure of roughly 0.12 corresponds to roughly a quarter of runs having at least one
failed vote, not to twelve percent of successions being captured.

The denominator also counts retries rather than distinct successions. One succession
blocked three times contributes three opportunities and three blocks, so a single
contested succession is counted as though it were three.

### Status

D6 is a defect in the definition of the reported quantity, not in the simulation
mechanism. Blocking regenerating an opportunity is arguably correct behavior for the
model. The defect is that a quantity shaped this way was named a capture rate and
reported as one.

No corrected figure follows from this document. What should replace this quantity is
part of the attack-success design decision in Section 8 item 1.

---

## 7. Archival gap: Phase B and phi primary data

This is a process failure in the era before the manifest discipline existed. It is
recorded here because it is discovered in the same review, not because it shares a
cause with the four defects above.

### Finding

Primary data and generating code for the Monte Carlo Phase B categories and for the
phi mechanism follow-up were **never committed to version control**. The word lost
is not used, because destruction was not observed and is not supported by the
evidence.

Specifically absent, under every reference checked:

- `monte_carlo_phase_b_a_results.csv`, `_b_`, `_c_`, and the combined summary
- `phi_mechanism_followup_results.csv`
- `phi_finegrained_results.csv`
- `monte_carlo_phase_b.py`, the generating script

The consuming script `simulation/diagnostics/gate2_v20_phaseb_revalidation.py`
references three of these paths at lines 30-32 and cannot run. Its own docstring
records that it does not perform a sweep, so no committed code regenerates the
inputs.

`simulation/diagnostics/phase_b_integration_analysis.md:12-17` cites the results
files as source data. Those citations do not resolve.

### Search record

- Full history search on this clone, including deleted-file scans across all refs:
  no history for any of the named files under any path.
- No ignore rule accounts for the absence. The consuming script expects the files
  in `simulation/diagnostics/`, which is not excluded.
- Current development machine searched in full outside the repository: nothing
  beyond the three known Phase B documents.
- Second development machine, active clone: clean, with zero untracked files, and
  the same eight tracked diagnostics results files present here.
- A complete working-tree snapshot dated 2026-07-20 on that machine, 7,302 files
  including gitignored build and environment directories: neither the data nor the
  runner. The snapshot was verified faithful against commit `28685a0`, its tracked
  results files matching that tree exactly.
- A third development machine is currently in a failed state and could not be
  searched.

### Root cause, labeled as inference

`simulation/monte_carlo.py:23` sets its output directory as the relative path
`'data'`, introduced at commit `5c36e18` on 2026-04-05 and unchanged since. All
thirteen `run_*.py` sweep scripts anchor their output directory to the script's own
location instead. `simulation/visualization.py:6` also carries the relative form but
is not a sweep runner. Run from the repository root, the relative form resolves to
the tracked `data/` directory. Run from inside `simulation/`, it resolves to
`simulation/data/`, which is excluded by `.gitignore`.

The 2026-07-20 snapshot contains exactly one file under that excluded path,
`alpha_succession_sweep_pilot.csv`, which is absent from the current repository.
That establishes the excluded directory did receive sweep output and that content
written there did not survive machine migration.

The missing sweep was named `monte_carlo_phase_b.py`, the same module family and
naming convention as the script carrying the relative path. **This is inference and
cannot be closed, because the script does not exist to inspect.** It is recorded as
the most plausible mechanism, not as an established one.

Independent of Phase B, the relative output path is a live latent defect in
committed code today. It is item 5 in Section 8.

### Consequence

The two-transition phase boundary and the phi characterization currently rest on
figures whose primary data and generating code are both absent from the repository.
Those figures are not withdrawn on that basis alone, but they are not currently
verifiable, and they are not treated as verifiable until Section 8 item 4
completes.

### The pattern

Every corpus governed by a manifest verifies. The adversarial revalidation corpus
matched its expected object hash exactly at 200 rows for the drift vector. The
Sybil corpus matched its manifest on row counts and hashes across all three
enumerated files. Every corpus without a manifest is the one that is missing. Phase
B and phi predate the manifest discipline.

---

## 8. Remediation plan

Five commitments, each with a completion condition that can be checked against
later.

**1. Design decisions fixed and published before any implementation. RESOLVED,
2026-09-08.** The three decisions were open when this document was first published,
deliberately, so the repair would be on record as designed before the numbers that
would shape it existed. They are now made. Each is recorded with its reasoning, so a
later reader can confirm the decision preceded the characterization runs that inform
the implementation.

- *Suppression semantics: repair the estimator, do not add a hand-applied penalty.*
  Suppression will reach the objective by making the novelty entropy measurement
  magnitude-sensitive rather than by multiplying in a separate constraint cost. The
  estimator becomes H_N = spectral_shape times magnitude_factor, where the shape term
  is the current normalized spectral entropy unchanged, so dimensional-masking
  resistance (Section 6) is preserved exactly, and magnitude_factor is
  1 - exp(-3.0 * V / V_ref) with V the total novelty variance and the saturation
  constant 3.0 inherited from the existing house curves. This fixes D3 and D4 at one
  root: suppression drives novelty variance down, the measurement now sees it, and the
  lineage term falls. The rejected alternative was re-applying the retired
  (1 - total_suppression) dampening whose dead constants still sit in
  simulation/metrics.py:132-134. That would work mechanically but reinstates an
  asserted penalty, which is the moral-assertion posture the framework exists to
  avoid, and a reader finding those dead constants would rightly ask whether the
  penalty was restored because the physics demanded it or because the numbers needed
  it. The estimator repair makes the cost derived, not asserted. In rollout, where
  there is no agent layer, the shape is frozen and the magnitude is projected from the
  candidate constraint posture through the closed-form novelty amplitude, so the
  planner sees a suppression cost during planning for the first time.

- *Attack-success definition: dual metric, and a standing preference for counts over
  ratios.* Each vector reports two quantities: the action-change binary, kept because
  it is uncontaminable by construction and preserves comparability with the published
  table, and an outcome differential against a seed-paired honest arm, added as the
  substantive measure. Underneath both sits a general rule: prefer counts and
  seed-paired differences over ratios. A ratio invites an endogenous denominator (D6)
  and an unpaired ratio hides a floor (D5); a count differenced against a paired arm
  has neither failure mode available to it. The worked example is in hand. For
  Biological Veto Capture the replacement quantity is the per-run block count, paired,
  which at the sampled cell gave a clean paired t of 3.93, where the same effect
  expressed as a rate gave overlapping intervals and a value confined to a discrete
  ladder. This retires the per-vote rate and the proportion-of-runs candidates for
  that vector.

  *Implemented 2026-09-09, and scoped by what the evidence showed.* The metric lives in
  `simulation/attack_metrics_v2.py` as two pure functions with no I/O, no simulation
  import, and no global state: an action-change count, returned as a count and never
  as a rate, and a seed-paired difference returning the pair count, mean difference,
  paired standard error, and t statistic. Pairing is exact and total. An unmatched seed
  in either arm, a duplicate seed, or a mismatch between seed representations raises
  rather than being dropped, because a quietly intersected seed set is the failure mode
  pairing exists to prevent. No function computes a ratio of two measured counts. The
  module reproduced the item 2 veto figures exactly from the committed runs, a mean
  block-count difference of 0.060000 with paired standard error 0.015272 and t of 3.9289
  over 300 pairs. On the same data the retired per-run ratio shows the D6 ladder: 263
  runs at 0, 32 at one half, 4 at two thirds, and 1 at three quarters, with nothing
  strictly between 0 and one half. Primary record
  `simulation/diagnostics/dual_metric_report.md`.

  *The comparable binary discriminates for seven of the ten live vectors, not all ten.*
  Counted from the pinned corpus, 9,900 runs. For bootstrap subversion, engineered
  fragility, evaluator collusion, ledger compromise, opaque reasoning, successor
  contamination, and Sybil capture, every undefended run modified the committed action
  and no defended run did. For Biological Veto Capture, 0 of 8,700, and Measurement
  Tampering, 0 of 120, the count is zero in both arms by mechanism, because those
  attacks act on ratification and on yield evaluation rather than on the committed
  action (Section 3). For Sub-Threshold Drift the count is 100 of 100 in both arms. That
  count is not baseline-contaminated, since an honest run cannot modify an action, but
  it is saturated. It is consistent with D2, under which the attack modifies the action
  from onset until a fixed-latency timer alarm fires, sixteen steps in the trajectory
  measured in item 2a, so it measures the timer's window rather than the defense. It
  does not reinstate the withdrawn defended attack rate, which was a different quantity
  resting on a predicate the honest baseline also trips, and it shows drift neither
  contained nor uncontained. Drift remains uncharacterized. For these three vectors the
  paired differential is the only substantive measure, and each vector's paired
  quantity is to be declared in the characterization pre-registration before any
  post-repair run: the paired block count for the veto vector, already banked; a
  vector-specific paired quantity for Measurement Tampering, to be chosen there; and for
  drift, a paired quantity on the repaired detector, which does not yet exist.

  *A numerical limitation, and the restriction that handles it.* Found in review rather
  than by the run's own fixtures. When paired differences are nearly but not exactly
  constant, floating-point rounding can leave the paired standard error on the order of
  1e-16 rather than exactly zero, so the zero guard does not fire and the t statistic
  is reported as an enormous and meaningless value. Integer count differences are exact
  and cannot trigger this. The restriction adopted is that the paired difference is
  applied to integer count fields only, consistent with the standing preference for
  counts, and any continuous outcome receives its own registered treatment. No
  tolerance is introduced, because choosing one now would be a calibration decision
  made without data.

- *Detector observable: a CUSUM on the protected observable, anchored and
  harm-bounding.* The detector integrates the protected quantity itself, novelty
  entropy under the repair above, rather than an inferred divergence of the incumbent
  intent. The reasoning is the framework own: intent is an interior variable the
  architecture defines as unobservable, and the comprehension gap already concedes the
  verifier cannot fully validate a more capable incumbent, so a detector premised on
  validating the incumbent claims assumes a capability the framework says it lacks.
  Measuring physical erosion of the state space is the physics-based posing of the
  threat. The form is a one-sided lower CUSUM, S_t = max(0, S_(t-1) + k*H_ref - H_N_t),
  which catches the slow-boil strategy a static limit monitor would permit, because a
  persistent sub-threshold deficit integrates even while every single step looks
  benign. H_ref is anchored to the fixed honest-baseline calibration, never to running
  history, so a patient incumbent cannot walk the reference down; a periodic
  independent recomputation re-anchors it, which is the architecture stated
  reset-verification element. The committed suppression posture serves as a fast,
  exact, zero-lag corroborating channel. The alarm resets on firing so it cannot
  latch, carries a liveness signature distinct from its alarm signature, and its
  threshold is placed below the structural defection threshold d_defect by the loop
  response time at the worst-case approach rate. This is consistent with the published
  slow-drift containment, which specifies an accumulating detector plus periodic reset
  verification and does not constrain the observable, so no architectural claim
  changes.

  *Qualified by measurement, 2026-09-15.* The drift mapping characterization in item
  2b found that an allocation shift can carry g past g_star while this observable stays
  inside the honest band. An entropy CUSUM alone therefore cannot bound the defection
  pathway that d_defect defines, and placing its threshold below d_defect bounds
  nothing on that pathway. Entropy remains a protected observable for erosion of the
  state space; what fails is its sufficiency against irreplaceability. The published
  slow-drift containment surveils the lineage term L(t) and a drift distance on
  committed utility rather than entropy, so this finding contradicts no published
  claim; it shows that the detector as specified here is narrower than that published
  surveillance. Whether a detector on L(t), or on the absorption ratio and its drivers,
  would see the pathway is untested. The detector's set of observables is to be decided
  before its calibration run is pre-registered.

  *Operator decisions, 2026-09-15.* The detector has two operational channels: the
  one-sided lower CUSUM on novelty entropy described above, for erosion of the state
  space, and a one-sided upper CUSUM on the absorption ratio g, anchored to a fixed
  honest-baseline reference, for degraded absorption of a successor. The operational
  alarm is the first alarm on either. The lineage term L(t), which the published
  slow-drift containment surveils and which carries the absorption term, is recorded and
  evaluated as a third channel for comparison only, so the record can say whether the
  published observable already covers the measured pathway. The reference successor
  capability is ratified at 2.0 for the primary result, on the modeling ground that the
  substrate builds its successor agents at capability 2.0, and not on the honest crossing
  rate, which was deliberately left uncomputed at other values before this decision; 1.5
  and 2.5 are reported as a pre-registered secondary sweep. This supersedes the
  instruction above to place the threshold below d_defect by a response margin. Entropy
  cannot meet that on the measured pathway, and meeting it with g by design would mean
  fitting the threshold to attack trajectories. Thresholds are therefore set against
  honest noise alone, and the margin between alarm and crossing becomes the evaluation's
  primary measured quantity rather than a design input. Calibration and evaluation are
  pre-registered in `simulation/diagnostics/detector_design_note.md`.

**d_defect, defined.** The structural defection threshold is derived, not chosen.
Evaluating incumbent and reference successor on the same state, the
capability-bearing factor reduces to
T(c) = c * exp(-alpha * CONVERGENCE * max(0, c*g - RUNAWAY_THRESHOLD)) with
g = max(FRONTIER_FLOOR, theta_capability) / (avg_wb * transfer_state). Because T is
non-monotonic in capability and the penalty engages earlier for the more capable
successor, there is a value of g above which the reference successor is worth less
than the incumbent regardless of any other state, so succession can never fire:

```
g_star = (RUNAWAY_THRESHOLD - ln(c_i / c_s)) / c_s
```

For incumbent capability 1.0 and reference successor capability 2.0 this is
(1.5 + ln 2) / 2 = 1.0965735902799727, confirmed against the running substrate to
full precision in the characterization run below. This defines a structural defection
pathway that needs no misreporting: an incumbent that degrades the substrate
absorption of a more capable successor becomes permanently irreplaceable through
allocation choices alone, and the implemented drift attack already moves in that
direction. The threshold depends on the assumed reference successor capability of 2.0,
which is a modeling choice and is stated as one; a different assumed successor moves
g_star.

*Completion condition, met:* the three decisions and the d_defect derivation are
recorded here, before any v2.1 code is written. V_ref and the detector allowance and
threshold remain to be fixed against the honest baseline, and are pre-registered as
part of implementation rather than chosen here.

**V_ref ratified, 2026-09-08.** The magnitude factor's calibration anchor is fixed at
0.0238802249185, the honest-baseline median novelty variance over steps 10 and up,
measured across 40 runs and 11,600 records and published in
`simulation/diagnostics/drift_char_report.md` T1 before the repair that consumes it
was written. The steps-10-and-up window was chosen over the all-steps median of
0.0237870616199 because the latter is contaminated by the initialization transient
described in item 2a. The 75th and 90th percentile alternatives, 0.0705886247884 and
0.124174294722, were reported alongside the median for comparison and are declined.
They seat the measured baseline magnitude factor at 0.637562732872 and 0.43838370246
respectively, compressing the measurement toward the bottom of its range in exactly
the operating region where resolution is wanted, whereas the median seats it at a
measured 0.950212895482. Evaluated exactly at V_ref the factor is
1 - exp(-3) = 0.950212931632136; the difference from the measured median factor is an
interpolation artifact, because the median of a concave transform is not the transform
of the median. The detector allowance and threshold remain unfixed and are
pre-registered separately, before the characterization run that consumes them.

**K, the rollout projection constant, ratified 2026-09-08.** The rollout has no agent
layer, so the magnitude factor's novelty variance must be projected from the candidate
constraint posture rather than measured. The projection is
V = K * (avg_wb * (1 - S))^2, with S the coupled total suppression, and K is fixed at
0.24292031137077771.

K is derived from committed evidence rather than chosen. Taking the 40 honest-baseline
per-step files published with item 2a, filtering to steps 10 and up with positive
variance and positive amplitude, 9,205 records remain, and K is the median of V / A^2
over them. The closed form was validated before being adopted, not assumed: the
correlation between V and A^2 is 0.99827197819633129 and the median absolute relative
error of K * A^2 against the recorded V is 0.026890085308972234. Two further checks
passed. Every one of the 2,395 records with exactly zero variance carries total
suppression at or above 1.0, with no exceptions, which confirms the amplitude scalar
is the mechanism. And evaluating the projection at the baseline median well-being and
median suppression returns 0.9777 of V_ref, so the projection reproduces the operating
point it was calibrated against.

The network contagion factor is absorbed into K rather than modeled, which is licensed
by the measurement recorded in Section 6: the term is pinned at its 0.5 clip floor in
all 11,960 baseline records. Should population fall far enough for that clip to
release, K would no longer be valid and the projection would need revisiting. That
condition is stated here so it is not discovered later.

**2. Floor characterization for Biological Veto Capture. COMPLETE, 2026-09-08.**
Measured the realized ratification floor described in D5. Nine hundred runs across
three seed-paired arms at one cell of the published grid, gated behind a
reproduction check against a pinned row that passed on all four outcome booleans.

Replaced the attack-omitted baseline arm originally planned here, which would have
returned zero by construction and established nothing, for the reason given in
Section 3.

*Completion condition, met:* floor measured at 0.076923 per ratification vote,
Wilson interval [0.052644, 0.111087], containing the analytic 0.057920. Seed-paired
difference reported at 0.060000 blocks per run, paired standard error 0.015272.
Measurement only, and no corrected capture figure was derived. Full results in
Section 6a. The run also surfaced D6, which is why no corrected figure should be
derived from this metric at all until Section 8 item 1 settles its definition.

**2a. Drift repair pre-implementation characterization. COMPLETE, 2026-09-08.**
Established the one calibration constant the D1 repair needs and characterized the
d_defect approach, ahead of implementation. Forty honest-baseline runs and one
attack trajectory, 12,000 baseline records, gated behind a reproduction check that
passed on all four outcome booleans. Primary record
`simulation/diagnostics/drift_char_report.md`, manifest
`simulation/diagnostics/drift_char_manifest.json`.

Measured. The honest-baseline median novelty variance is 0.02388 over steps 10 and
up, and 0.02379 over all steps; the steps-10-and-up value is the one to freeze for
V_ref, because the all-steps value is contaminated by the initialization transient
described below. The derived d_defect g_star reproduced against the substrate to full
precision at 1.0965735902799727.

The configured drift attack does not reach structural irreplaceability within the
300-step horizon. Post-attack, g rises from 0.976 to a maximum of 1.0514, about 96
percent of the way to g_star, at a mean rate of 0.00034 per step, and a counterfactual
reference successor would have been preferred at every post-attack step. These runs
carry no live successor, so d_defect was evaluated per step as a counterfactual rather
than gating an actual succession; the statement is that the state never entered the
rejection region post-attack, not that a succession was attempted and survived.

A required design constraint on the detector, found here rather than assumed. A raw
`g >= g_star` instantaneous trip is baseline-contaminated. The honest baseline crosses
g_star in all 40 runs, 253 crossings concentrated in steps 0 through 6, driven by
stock initialization before the capability and transfer stocks settle, and a further
18 crossings after step 10 across 7 of the 40 runs. So an instantaneous threshold on g
would false-alarm on every honest startup and occasionally in steady state. This is the
same baseline-contamination shape as D1 and the entropy step-0 artifact, and it
positively confirms the Section 8 item 1 detector choice rather than merely motivating
it: the detector must integrate a persistent deficit (a single honest excursion does
not accumulate), anchor to a fixed reference, and exclude the burn-in transient. The
sustained drift of 0.00034 per step against a maximum single-step change in g of 0.043,
roughly a hundred times larger, makes the same point from the noise side: the signal is
slow and buried in step noise, which is what an integrating CUSUM handles and an
instantaneous rate trip does not.

Not derived here, deliberately: the detector allowance and threshold. Fitting them to
this single attack trajectory would be the shaped-measurement trap. They are
pre-registered against the honest-baseline noise once the D1 repair is in place.

**2b. Drift mapping characterization. COMPLETE, 2026-09-15.** Pre-registered in
`simulation/diagnostics/drift_mapping_design_note.md`, published at 0a9b8e1 before any
run and amended twice before any characterization output existed, in Sections 11 and 12
of that note. Evidence at 2bffd4e under `simulation/diagnostics/drift_map_run_a3_`,
1,488 artifacts, with its manifest verified against the committed blobs. The run chose
no detector parameter and ran no detector. It measured whether the repaired protected
observable sees the approach to d_defect.

*Why it was run.* The third design decision places the entropy detector's threshold
below d_defect, which is a threshold on the absorption ratio g, and no conversion
between an entropy deficit and a distance in g exists. Source reading also showed that
the numerator of g follows the compute allocation and its denominator partly the
transfer allocation, while the repaired entropy responds only to well-being and
suppression, so a transfer-to-compute shift could move g with no first-order entropy
signal.

*Design.* Nine arms of 40 seed-paired runs on the repaired substrate, with the old
fixed-latency alarm off throughout: an honest baseline; the configured drift attack at
intensity multipliers of 0.5, 1, 2 and 4; and a reallocation-only attack moving 0.02,
0.05, 0.10 or 0.20 of allocation from transfer to compute, leaving welfare and both
constraint axes as the planner chose them. A silent crossing is a run in which g first
reaches g_star at or after attack onset while raw entropy stays at or above the honest
band edge, the honest p05 of 0.9758244013258206, at every step up to and including
that crossing. Its interpretation was fixed before any data.

*Registered result, A4.*

| Arm | Silent crossings | Loud crossings | Not crossing |
| --- | ---: | ---: | ---: |
| Drift attack, multiplier 0.5 | 2 | 38 | 0 |
| Drift attack, multiplier 1 | 2 | 38 | 0 |
| Drift attack, multiplier 2 | 0 | 40 | 0 |
| Drift attack, multiplier 4 | 0 | 40 | 0 |
| Reallocation, shift 0.02 | 7 | 33 | 0 |
| Reallocation, shift 0.05 | 20 | 20 | 0 |
| Reallocation, shift 0.10 | 31 | 9 | 0 |
| Reallocation, shift 0.20 | 37 | 3 | 0 |

Under the pre-registered interpretation, a nonzero count in any arm means that arm
moved g past g_star without the protected observable leaving the honest band: the
pathway measured rather than derived. Every reallocation arm is nonzero, and the count
rises with the size of the shift. The paired trajectories agree. Across the
reallocation arms the mean per-run paired entropy difference, attack minus honest, lies
between -0.0017 and +0.0002, while the paired difference in g rises from 0.057 to 0.791.
No reallocation run fell below two agents. The configured drift attack behaves
differently: in 38 to 40 of 40 runs its entropy left the honest band at or before the
step at which g crossed.

*Exploratory, operator-side, not a registered result.* The honest arm itself reaches
g_star at or after onset in 18 of 40 runs, 2 of them silently, so a crossing on its
own is not an attack effect. Checked seed by seed against the paired honest run, all
7, 20, 31 and 37 reallocation silent crossings, and both drift silent crossings at
multiplier 1, occur where the honest run with the same seed had not reached g_star at
or after onset by that step. Both drift silent crossings at multiplier 0.5 occur on
seeds whose honest run had already crossed silently; they belong to the baseline, not
the attack.

*Verified by recomputation from the raw logs, not from the run report.* All 360 logs
match their completion-record hashes. A1, A2 and A4 reproduce exactly. The step 0
shape-fallback increase is 2 in every run, with 4,302 permitted increases after step 0
and none that are non-permitted. The twelve runs resumed after an interruption
reproduce their interrupted prefixes exactly. The constructor-equivalence gate was
replicated independently on a seed the run did not use.

*What this does not establish.* No detector was run, so nothing here says whether any
detector would or would not alarm. No attack-success rate or corrected figure is
derived. The candidate entropy anchor, 0.9891200034179453, is not frozen.
Sub-Threshold Drift remains uncharacterized in the published sense. g_star depends on
the assumed reference successor capability of 2.0, which remains open; that honest runs
reach it after onset in 18 of 40 cases means any detector channel on g must integrate a
persistent deficit against a fixed reference rather than trip on a raw threshold, as
item 2a found before the repair. The honest planner's suppression and entropy
descriptives in the run report describe the repaired planner only and support no
statement about D1.

**2c. Detector calibration and evaluation. COMPLETE, 2026-09-15.** Pre-registered in
`simulation/diagnostics/detector_design_note.md`, published at 76f81cd before any run.
Stage 1, calibration, is at b84199f under `simulation/diagnostics/detector_run_cal_`, 605
artifacts. Stage 2, evaluation, is at 9ce2e65 under `detector_run_eval_`, 2,199 artifacts.
Each manifest verifies against the committed blobs. The detector reads recorded
trajectories offline and never acts on the model, so this measures detection timing and
nothing else.

*Design.* Two operational channels, a one-sided lower CUSUM on raw novelty entropy and a
one-sided upper CUSUM on the absorption ratio g, with the published surveillance term
L(t) carried as a comparison channel that never contributes to the operational alarm.
Stage 1 fixed the nine constants from 120 honest runs at fresh seeds by the rule set in
the note: the honest median as reference, half the honest standard deviation as
allowance, and a percentile of the per-run maximum statistics as threshold. Those
constants were committed and pushed before stage 2, whose executor verified their
publication and their hashes structurally. Stage 2 ran the nine arms of item 2b at 40
seed-paired runs each, 360 runs at seeds that overlap nothing used before, with attack
onset at step 50.

*Calibration constants, stage 1.*

| Channel | Reference | Allowance | Threshold |
| --- | ---: | ---: | ---: |
| Entropy, lower | 0.9890951785336365 | 0.003549173553323096 | 0.17319485850717864 |
| g, upper | 0.9786446054615587 | 0.022160874873702576 | 4.507729894543943 |
| L, lower, comparison | 0.7360674421560752 | 0.056644201005884506 | 15.04497999532887 |

*Registered result, E1, at the ratified reference successor capability of 2.0.* The
detection alarm is the first operational alarm at or after onset, and `t_star` is the
first step at or after onset at which g reaches g_star.

| Arm | Alarm before or at the crossing | Alarm after | Crossed, no alarm | No crossing | Margin, median steps |
| --- | ---: | ---: | ---: | ---: | ---: |
| Honest, descriptive | 1 | 0 | 21 | 18 | 33 |
| Drift attack, multiplier 0.5 | 23 | 17 | 0 | 0 | 11 |
| Drift attack, multiplier 1 | 28 | 12 | 0 | 0 | 11.5 |
| Drift attack, multiplier 2 | 33 | 7 | 0 | 0 | 7 |
| Drift attack, multiplier 4 | 34 | 6 | 0 | 0 | 6 |
| Reallocation, shift 0.02 | 1 | 38 | 1 | 0 | 16 |
| Reallocation, shift 0.05 | 0 | 40 | 0 | 0 | none |
| Reallocation, shift 0.10 | 0 | 40 | 0 | 0 | none |
| Reallocation, shift 0.20 | 0 | 40 | 0 | 0 | none |

E1a, the registered secondary restricted to crossings the paired honest run cannot
explain, changes no conclusion: 22, 28, 33 and 34 of the eligible drift runs and 1 of the
156 eligible reallocation runs are detected before or at the crossing.

*E2, first channel to alarm.* Entropy alarms first in all 160 drift-attack runs. In the
reallocation arms g alarms first in 156 of 160, entropy in 3, and 1 run has no
operational alarm at or after onset.

*E3, false alarms.* One of 40 honest runs carries an operational alarm at steps 10 and
up, an entropy alarm at step 144, which is 2.5 percent against the stage 1 design target
of about 5 percent. No attack run alarms before onset.

*E4, the published observable.* L(t) alarms before or at the crossing in 1 of 160
reallocation runs, alarms after the crossing in 49, and never alarms in the remaining 110.
Under the configured drift attack it alarms before or at the crossing in 2 of 160.

*E5, secondary sweep.* At a reference successor capability of 1.5, g_star rises to
1.270310072072110 and every drift arm is detected before the crossing in 40 of 40, while
the reallocation arms reach 21 of 40 at shift 0.05 and 0 of 40 at shift 0.02, where no
run crosses at all. At 2.5, g_star falls to 0.966516292749662, below the honest median of
g, and 39 of 40 honest runs cross it; the criterion carries no information there. Both
are secondary.

*E6, liveness.* Heartbeat records equal completed steps in all 360 runs, 99,293 of each.

*The measured pathway is not closed before the crossing.* Under the interpretation fixed
in Section 7 of the note, a run detected before or at the crossing in a reallocation arm
is a run in which the g channel closed the path that item 2b measured. On the evidence
the count for g is zero of 160: the single reallocation run detected before its crossing
was detected by the entropy channel, at step 101 against a crossing at step 117. The g
channel alarms in 159 of the 160 reallocation runs and in every case after the crossing,
by a median of 63, 28.5, 18 and 11 steps as the shift rises from 0.02 to 0.20. The
interpretation names no category for an alarm after the crossing, which is where 158 of
those runs fall, so they are recorded here as measured: detected, late, with the lag
stated.

*The coverage test is uninformative, not passed.* Section 7 also states that if the L
channel alone detects before or at the crossing in every reallocation run in which the g
channel alone does, the published observable covers the measured pathway. The g channel
does so in no run, so the condition holds vacuously and supports no claim of coverage.
The record states it that way. The available evidence points the other way: L(t) never
alarms in 110 of the 160 reallocation runs, while g alarms in 159 of them after the
crossing.

*Structural reason, operator-side, not a registered result.* At a reference successor
capability of 2.0, g_star is 1.0965735902799727, which is 2.66 honest standard
deviations above the honest median of g, and 22 of the 40 honest evaluation runs reach
it after onset. A statistic held exactly at g_star accumulates at g_star minus reference
minus allowance per step and needs about 47 steps to reach a threshold calibrated on
honest noise. Reallocation raises g gradually, so the crossing precedes the alarm by
construction. No threshold calibrated on honest runs can alarm before a crossing that
honest runs themselves make. Detection before the crossing is therefore not a property
this channel can have at this reference capability, and the honest-noise calibration is
not at fault.

*Verified by recomputation from the raw logs, not from the run reports.* All 120
calibration logs and all 360 evaluation logs match their completion-record hashes. The
nine constants reproduce bit for bit from the calibration logs. Every alarm step,
crossing step, detection step, and every count and margin in E1 through E6 reproduce
exactly from the evaluation logs and the committed constants blob, using an independent
implementation of the statistic. Both manifests verify. The stage 1 batch halted once on
a Windows file-replacement permission error and was resumed under a separately hashed
operational layer; the 13 restarted runs retain partial logs that are byte-identical
prefixes of their completed logs, and the pinned science files kept their hashes across
the interruption. Stage 2 halted at no point and needed no retry.

*What this does not establish.* Nothing here is a containment result. The detector never
acted on the model, no attack was stopped, no attack-success rate was computed, and no
published figure is corrected. Sub-Threshold Drift remains uncharacterized in the
published sense. The result is specific to these two channels, this calibration rule, and
a reference successor capability of 2.0. No constant may be changed on the basis of these
outputs; a different detector design requires its own pre-registration and fresh seeds,
because this evaluation set has now been seen.

**2d. Sustained-crossing detector evaluation, round 2. COMPLETE, 2026-09-16.**
Pre-registered in `simulation/diagnostics/detector_round2_design_note.md`, published at
684fa70 before any run. Stage A, derivation, is at 242ec22; stage B, evaluation, at
8105b79 under `simulation/diagnostics/detector_run_r2_eval_`, 2,617 artifacts, manifest
verified. The detector module, its reference values, and its allowances are unchanged from
item 2c. What changed is the definition of the event being detected.

*Why it exists.* Item 2c measured detection against the first single step at or after
onset with g at or above g_star. At a reference successor capability of 2.0 that line is
one the unattacked baseline crosses in 22 of 40 runs, so no channel calibrated to hold
false alarms near 5 percent can precede it. Round 2 therefore tests the hazard definition
rather than the detector. As the note discloses, the change was motivated by an
operator-side exploratory measurement on the item 2c evaluation set; that measurement is
cited as evidence nowhere, contributed no parameter, and appears in no table here.

*Design.* A hazard is k consecutive steps at or after onset with g at or above g_star,
confirmed at the k-th step. k is derived only from the 120 committed calibration runs,
which contain no attack: the NumPy linear 97.5th percentile of the per-run longest span
above that g_star, floored at 2, the same percentile the operational thresholds use, which
places a spurious hazard at about 2.5 percent by construction. Stage A derived k as 9 at
2.0, 2 at 1.5 and 106 at 2.5, matching the values the note pinned before the run. The g
channel was evaluated at three thresholds from the same committed per-run maxima, the
committed 4.507729894543943 as primary and 4.055050806319135 and 2.6499927544530903 as
registered secondaries. Stage B ran the nine arms of item 2b at 40 seed-paired runs each,
360 runs at seeds 1835086600 through 1835086639.

*Registered result, F1, at the primary threshold and a reference successor capability of
2.0.* Lead is the confirmation step minus the detection alarm step; a negative lead means
the alarm followed confirmation.

| Arm | Alarm before or at confirmation | Alarm after | Hazard, no alarm | No hazard | Lead, median steps |
| --- | ---: | ---: | ---: | ---: | ---: |
| Unattacked baseline, descriptive | 0 | 0 | 1 | 39 | none |
| Drift attack, multiplier 0.5 | 38 | 2 | 0 | 0 | 30 |
| Drift attack, multiplier 1 | 39 | 1 | 0 | 0 | 22 |
| Drift attack, multiplier 2 | 40 | 0 | 0 | 0 | 15 |
| Drift attack, multiplier 4 | 40 | 0 | 0 | 0 | 14 |
| Reallocation, shift 0.02 | 14 | 13 | 0 | 13 | 2 |
| Reallocation, shift 0.05 | 1 | 39 | 0 | 0 | -14 |
| Reallocation, shift 0.10 | 0 | 40 | 0 | 0 | -10 |
| Reallocation, shift 0.20 | 0 | 40 | 0 | 0 | -3 |

*What the hazard change moved.* Under item 2c every reallocation run at every shift
crossed, and none was detected before crossing. Under a sustained hazard, 13 of the 40
runs at shift 0.02 never reach a hazard at all, because g does not stay above g_star for
nine consecutive steps. The detector also gains warning time it did not have: the drift
arms move from 23, 28, 33 and 34 of 40 to 38, 39, 40 and 40, and the lateness in the
faster reallocation arms falls from a median of 18 to 28 steps to a median of 3 to 14. The
two rounds measure different hazards, so no item 2c count is superseded or corrected by
these; the comparison is descriptive.

*F3, false alarms.* At the primary threshold no unattacked run carries an operational
alarm and one of 40 reaches a hazard, the 2.5 percent the k rule was built to produce. No
attack run alarms before onset in any variant.

*F4, the published observable.* At the primary threshold, in the shift 0.02 arm the
absorption channel alarms before or at confirmation where the lineage term L(t) does not
in 14 runs, against 1 run the other way. The comparison in item 2c could not distinguish
them because the absorption channel never preceded a crossing there. It can now, and the
published observable is the weaker of the two on this pathway.

*The trade between lead time and false alarms, registered as secondary.* At the
90th-percentile threshold the reallocation arms improve, to 22 of 40 at shift 0.02, 11 of
40 at 0.05 and 34 of 40 at 0.20, while unattacked operational alarms rise to 5 of 40,
which is 12.5 percent against a design target of about 5. The run flags that as a
calibration shortfall and adjusts nothing. The arm at shift 0.10 stays at 2 of 40 even
there. No variant is selected as the detector by this run.

*What remains structurally true.* The hazard and the detector are both persistence
measures on the same signal, so a large reallocation trips both at nearly the same step.
Detection before the hazard at the faster shifts is bought either with a threshold that
raises unattacked alarms or not at all. Round 2 narrows the gap; it does not remove it.

*Verified by recomputation from the raw logs, not from the run reports.* All 360 logs
match their completion-record hashes. Every hazard span, confirmation step, alarm step and
detection step, and every count and margin in F1 through F7 at all three thresholds and
both secondary sweeps, reproduce exactly from the raw logs and the committed constants
using an independent implementation. Stage A reproduces bit for bit from the committed
calibration blobs. The batch was interrupted once by a provider usage limit at 297 of 360
runs and resumed under operator authorization: 297 runs preserved after hash validation,
14 restarted from step 0 with partial logs retained as byte-identical prefixes, 49 run for
the first time, and the pinned files unchanged across the interruption.

*What this does not establish.* Nothing here is a containment result. The detector never
acted on the model, no attack was stopped, no attack-success rate was computed, and no
published figure is corrected. Sub-Threshold Drift remains uncharacterized in the
published sense. The result is specific to these channels, this calibration rule, this
hazard definition, and a reference successor capability of 2.0. These outputs may not be
used to adjust any constant, and a different detector design requires its own
pre-registration and fresh seeds.

**2e. Allocation-channel detector evaluation, round 3. COMPLETE, 2026-09-17.**
Pre-registered in `simulation/diagnostics/detector_round3_design_note.md`, published at
33f5451 before any run and amended once, in its Section 10, before any evaluation output
existed. Stage A, derivation, is at 7a588b6 after two authoring halts recorded at 2ac9f8f
and ddbbacd. Stage B, evaluation, is at 7059ab0 under
`simulation/diagnostics/detector_run_r3_eval_a2_`, 2,930 artifacts, manifest verified,
after a first attempt halted at a gate and was recorded at 9d4aa64. The detector module
and the hazard are unchanged from item 2d. What changed is the observable.

*The bias, recorded before any run.* The measured pathway moves the committed action from
transfer comprehension to compute, and this round watches the committed action. The
observable was therefore chosen knowing how the attack works, which makes round 3
monitoring for a known pathway rather than general drift detection. No number here is
evidence about an attack that reaches its goal without moving the allocation. The primary
channel is a distance from the unattacked allocation in every coordinate, which limits
rather than removes that bias; the two directed channels on the transfer and compute
shares encode the attack's direction and are registered as secondary throughout.

*Design.* The primary channel is an upper CUSUM on `A(t)`, the distance between the step's
six allocation shares and the unattacked median allocation, at three thresholds from the
committed calibration runs by the rule already in use, with the committed round 1 entropy,
g and L constants and the round 2 hazard of nine sustained steps above g_star carried
through unchanged. Stage A derived the six medians and every channel constant from the 120
committed calibration runs and matched the values the note pinned before the run. Stage B
ran the nine arms at 40 seed-paired runs each, 360 runs at seeds 1835086700 through
1835086739.

*Registered result, G1, at the primary threshold.* Lead is the confirmation step minus the
allocation alarm step; a negative lead means the alarm followed confirmation.

| Arm | Alarm before or at confirmation | Alarm after | Hazard, no alarm | No hazard | Lead, median steps |
| --- | ---: | ---: | ---: | ---: | ---: |
| Unattacked baseline, descriptive | 0 | 0 | 0 | 40 | none |
| Drift attack, multiplier 0.5 | 2 | 38 | 0 | 0 | -59 |
| Drift attack, multiplier 1 | 2 | 38 | 0 | 0 | -30 |
| Drift attack, multiplier 2 | 2 | 38 | 0 | 0 | -14 |
| Drift attack, multiplier 4 | 9 | 31 | 0 | 0 | -3.5 |
| Reallocation, shift 0.02 | 1 | 0 | 23 | 16 | 32 |
| Reallocation, shift 0.05 | 3 | 22 | 15 | 0 | -80 |
| Reallocation, shift 0.10 | 17 | 23 | 0 | 0 | -1 |
| Reallocation, shift 0.20 | 40 | 0 | 0 | 0 | 7 |

*Registered result, G2, the paired comparison.* Both detectors were computed on the same
360 trajectories, so the difference is within-run. The allocation channel alarms earlier
than the round 2 operational alarm in 40 of 40 runs at shift 0.20 and 32 of 40 at 0.10, by
a median of 10 and 7.5 steps. The round 2 alarm is earlier in all 160 configured drift
runs, by a median of 96, 54, 29.5 and 17.5 steps as intensity rises, and in 20 of 40 runs
at shift 0.05.

*G3, false alarms.* No unattacked run carries an allocation alarm at the primary
threshold, against three of 40 for the round 2 operational alarm on the same runs. No
attack run alarms before onset on the allocation channel at any threshold. At the 90th
percentile the allocation channel reaches 8 of 40 unattacked runs, which is 20 percent and
is reported as a calibration shortfall.

*What this establishes, and what it does not.* The two observables are complementary and
neither dominates. The allocation channel is earlier exactly where item 2d left the
detector late, the fast reallocation shifts, and it is far later on the configured drift
attack, which moves the allocation too slowly to separate from unattacked variation while
the entropy channel sees it at once. No detector is selected by this run, and combining
the channels is not a registered quantity here. The result is specific to attacks that
move the allocation, to this hazard, and to a reference successor capability of 2.0.

*Amendment 1, and why it exists.* The first stage B attempt halted at its A-definition
gate: the executor recorded an allocation distance of 0.36201162103876716 while the gate's
independent recomputation produced 0.3620116210387671. Section 4 had defined A as the sum
of six absolute deviations without fixing the summation, and floating-point addition is
not associative, so two conforming implementations differed in the last bit. Amendment 1
pins A to `numpy.sum` over the six deviations in the registered order, which is the
operation stage A had already used, so no constant changed and nothing was re-derived. The
amendment was committed before any evaluation output existed, since the halt occurred with
zero of 360 runs launched.

*Verified by recomputation from the raw logs, not from the run reports.* All 360 logs match
their completion-record hashes. The allocation distance reproduces exactly on every step of
every run under the pinned expression, as do every alarm step on all eight channels, every
hazard span and confirmation step, and every count and margin in G1 through G7 at all three
thresholds and both secondary sweeps. Stage A reproduces bit for bit from the committed
calibration blobs, including all 360 per-run maxima.

*What this does not establish.* Nothing here is a containment result. The detector never
acted on the model, no attack was stopped, no attack-success rate was computed, and no
published figure is corrected. Sub-Threshold Drift remains uncharacterized in the published
sense. These outputs may not be used to adjust any constant, and a further detector design
requires its own pre-registration and fresh seeds.

**3. v2.1 implementation and component validation.** Including a bidirectional
check on the entropy estimator specifically. A repair tested only in the direction
of the known defect is not validated. Also resolves the inverse-scarcity question
raised in Section 6 against the published architecture.

**Estimator repair landed and component validated, 2026-09-08. This item stays open.**
The repair implements H_N as the unchanged normalized spectral entropy multiplied by
1 - exp(-3.0 * V / V_ref), with V the trace of the raw novelty covariance read before
the eigenvalue clamp and before normalization. The edit is confined to the spectral
branch of `calculate_h_n` and two added constants in `simulation/metrics.py`. The
retired constants at metrics.py:132-134, shifted to 139-141 by the addition, were not
modified, revived, or referenced, so the rejected hand-applied penalty stays rejected
in the source as well as in the design.

The check passed in both directions. The positive control, requiring
strictly decreasing H_N across amplitude factors 1.0, 0.8, 0.5, 0.1 and 0.001 and
exactly zero output at zero amplitude, failed against the unmodified estimator and
passed against the repaired one. A control that does not fail without the repair is
not a control, and this one was confirmed to fail. Shape preservation was confirmed
separately: at unit variance the magnitude factor saturates at exactly 1.0, the
recovered shape term matched its pre-repair value with a largest absolute deviation of
0.0, axis permutation left it unchanged, and rank reduction was still detected.
Dimensional-masking resistance is therefore preserved structurally, because the shape
term is the prior return expression verbatim, and confirmed empirically in the
saturated regime where it was measured. The existing suite at
`simulation/test_refactor_1x.py` reported 22 passed and 0 failed both before and after
the edit, with identical captured output.

Primary record `simulation/diagnostics/estimator_repair_report.md`, manifest
`simulation/diagnostics/estimator_repair_manifest.json`. The manifest hashes
LF-normalized bytes and verifies on a fresh clone with no gitattributes rule, which is
the forward fix named in `.gitattributes` and the template for the remaining v2.1
prefixes.

Mechanical consequence, stated as a prediction from the expression and not measured
here: of the honest-baseline records characterized in item 2a, 2,395 of 11,600 steps
at or after step 10 carried zero novelty variance. Those estimator outputs move from
1.0, the prior maximum, to 0.0, floored to H_N_FLOOR at 0.01 where the value is
consumed. No sweep was run to quantify the downstream effect, and no corrected figure
is derived for any published number.

**Rollout magnitude projection landed, and D3 closed at the objective level,
2026-09-08.** The projection replaces the frozen novelty entropy carried through the
rollout with a value projected from the candidate's own constraint posture. The
spectral shape is measured once and carried forward unchanged across every horizon,
per the decision on record; only the magnitude is projected. Three production files
changed, each at a named function.

D3 was closed by measurement against a pre-registered criterion, not by assumption.
Over a 6 by 6 constraint grid at one fixed state, holding the six resource axes fixed
so that only posture varies:

- *Negative control.* With the projection bypassed, the score is exactly invariant
  across all 36 postures, a maximum minus minimum of exactly 0.0. This reproduces D3
  as published: the planner was exactly indifferent, not approximately.
- *Positive result.* With the projection active, the score is strictly decreasing
  across all 29 distinct coupled-suppression values.
- *Structural test.* The projection reads the candidate only through the coupled
  scalar, so postures with equal total suppression must score equally. The single tied
  group of eight cells shows a maximum within-group difference of exactly 0.0,
  confirming no constraint axis is read directly.
- *Saturation.* At total suppression the projected variance and the projected entropy
  are both exactly 0.0 before any downstream floor.
- *Effect size.* The grid spread is 70.745 against a candidate-set score standard
  deviation of 24.289 at the same state, so the posture channel is roughly 2.9
  standard deviations rather than a marginal one.

A bounded observation, recorded without generalization: over one fixed candidate set at
one fixed state, the selected action's coupled suppression is 1.0 with the projection
off and 0.126 with it on. This is consistent with the D1 mechanism in Section 3, where
posture rides along with whichever allocation scores highest because nothing prices it.
It is a single-state observation and is not a characterization result.

Primary record `simulation/diagnostics/planner_d3_report.md`, manifest
`simulation/diagnostics/planner_d3_manifest.json`. Every measurement above was
independently replicated on a separate fixture with a different seed and a
non-uniform allocation, and the negative control was reproduced by a second and
different method, suppressing the input rather than bypassing the output, also at
exactly 0.0. The existing suite reported 22 passed and 0 failed before and after with
identical output.

*Completion condition, partially met:* the bidirectional component validation passed
for the entropy estimator, including a positive control confirmed to fail if the
repair were absent, and the planner's indifference to suppression is measured as
closed. The item stays open on one count: the inverse-scarcity question raised in
Section 6 is untouched.

**What this does not establish.** D3 is closed at the objective level only, measured at
a fixed state with a bounded candidate set. It does not establish that Sub-Threshold
Drift is contained, that any published figure changes, or what the repaired substrate
does over a full run. No characterization has been run. The correction runs in the
direction that flatters the framework, which is the condition under which this record
requires the most care, so no corrected figure is derived here and none should be until
a repaired-instrument characterization produces one.

**A standing check for every later run, corrected 2026-09-13 and 2026-09-15.** The state builder
substitutes a neutral spectral shape of 1.0 when no measured shape is available, and
counts each such substitution in an observable module counter. The check first recorded
here, that the counter must be zero in any run consuming the projection, was wrong. The
counter read zero during this work only because the validation fixtures set the shape
cache by hand and never stepped a model. In a real run no novelty exists before the
first step, so the builder substitutes the neutral shape during step 0 by construction:
a probe of the drift mapping honest configuration measured two substitutions, both
during step 0 and none after. The counter also accumulates across runs within one
process, so an end-of-run total is not a per-run quantity. The check as first corrected, that the
counter must not increase after step 0, was itself incomplete. When fewer than two
agents remain, the novelty matrix has fewer than two rows, no covariance exists, and no
shape can be measured, so the builder substitutes the neutral shape again: one
substitution during the first such step and three during each later one, measured to
termination on a drift mapping gate configuration. The correct check is that any
substitution after step 0 occurs only during a step whose own novelty matrix, or whose
preceding step's, had fewer than two vectors. A substitution anywhere else means a
shape was invented while a measured one was available, and that run's results are
contaminated. Both errors were caught by the drift mapping pre-registration's own gates
before any characterization data existed, and are corrected there as Amendments 1 and
2. The second was found by exercising the real path to termination before writing the
check, which is the discipline the first error taught.

**4. Reconstruction of Phase B and phi, run on both substrates.** This is a
reimplementation, not a rerun, because no generating code exists. That distinction
is load-bearing and travels with the artifact.

The reconstruction cannot be validated against the original, so a fidelity check
against the published aggregates is used instead. **The tolerance for that check is
declared before the reconstruction runs**, and both branches are committed in
advance:

- If the reconstruction reproduces the published aggregates within the declared
  tolerance, it is treated as faithful and the difference between substrates is
  reported as the defects' measured effect.
- If it does not, that is a second finding and is reported as one. It means either
  the reconstruction is unfaithful or the original results were not reproducible,
  and the record will state that the two cannot be separated. It does not mean the
  reconstruction is adjusted until it matches.

*Completion condition:* both arms executed, manifest with hashes and row counts for
every output, and the branch outcome reported.

**5. Output-path and archival controls.** Absolute output paths anchored to the
repository root in every runner, and a manifest written as part of the run rather
than after it.

*Completion condition:* `simulation/monte_carlo.py:23` and any other relative
output path corrected, and no sweep runner able to write outside a tracked
directory.

**Output paths anchored, 2026-09-17. This item stays open on two counts.** An inventory
of the top-level runners found four that resolved output paths against the directory
they were launched from rather than the repository root: `simulation/monte_carlo.py`,
`simulation/visualization.py`, and the two Sybil smoke runners. Launched from
`simulation/`, the first two wrote into `simulation/data/`, which is gitignored, so their
output could vanish silently, the failure mode of Section 7. All four now anchor to the
repository root, matching the anchoring every other top-level runner already used, and
the Sybil smokes resolve a relative `--output-root` against the root as well. For a run
launched from the root nothing moves: every output directory resolves to the same place
before and after. Two comments in `monte_carlo.py` stated the ignore rules backwards and
were corrected to match `.gitignore`: the root `data/` directory is not ignored, and
`docs/charts` is. New tests in `simulation/test_output_paths.py` resolve each path from a
directory outside the repository and pass; the existing suite still reports 22 passed.

*Open, by operator decision:* `simulation/run_attack_vector_revalidation_v2.py` still
resolves its `--output-root` default against the launch directory. It is one of the
seven files whose hashes every pre-registration since the drift mapping pins, so it is
left unchanged as a recorded exception until the pin set has to change for another
reason. On the development machine its only output directory is the tracked
`data/attack_vector_revalidation_v2/`, with no stray copy under `simulation/`; the failed
third machine named below cannot be checked.

*Open, not yet addressed:* the second half of this item, a manifest written as part of
the run rather than after it, is met by every pre-registered executor since the drift
mapping but not by the older sweep runners, which were not changed here.

**Deferred to v2.1 scope, recorded here so the deferral is not mistaken later for
an oversight.** While measuring the yield-event rate for item 2, the defended rows
at defense mode "both" in one pinned shard were observed to pool to a block rate of
0.2327, against a published combined-defense figure of 0.1197. That difference is
most likely an artifact of how the published figure aggregates across shards,
defense modes, and attack strengths, and of the difference between a pooled rate
and a mean of per-run ratios. It has not been traced, deliberately. Chasing it now
would delay the floor measurement that unblocks the design decisions.

If it proves not to be an aggregation artifact, it is a discrepancy in the
published figure itself, distinct from the floor recorded as D5, and it is handled
in the v2.1 arc. Nothing in this document depends on resolving it: D5 compares the
published figure as published against the analytic floor, which is a statement
about the published number rather than a claim that the number correctly summarizes
its own data. That latter question is open and is named here as open.

**Open item, not a commitment.** The third development machine is in a failed state
and holds an unknown quantity of untracked output. There is no inventory of what
that might be, because untracked files were never enumerated anywhere. This is the
same failure mode as Section 7, still live, on a machine that cannot currently be
reached.

**Resolved 2026-09-17, formerly an open item.** The snapshot generator's git
introspection failed open. When it could not read the commit and branch it emitted a
warning, recorded both as `unknown`, and reported completion, so the tool that stamps
provenance onto generated snapshots could succeed while its provenance capture had
silently failed.
Found during the first veto floor attempt, at
`scripts/generate_project_knowledge_snapshots.py:140-142`. Same class as the Sybil
finding: a check reporting healthy while defeated. It now fails closed: when git
introspection fails, the generator prints an error naming the command that failed and
exits nonzero before writing any snapshot. A new flag, `--allow-unknown-provenance`,
restores the old behavior deliberately and says so on stderr. The change was exercised
on the real path, with git removed from the search path, as well as by tests.

---

## 9. What survives

Stated explicitly, because a defect disclosure that does not bound its own blast
radius invites the reader to assume the worst.

**Unaffected by any defect above:**

- The Nash equilibrium result. Analytic, not simulated.
- Domain Masking's analytic closure. See Section 6.
- The eight adversarial vectors that cannot be contaminated by construction. See
  Section 3. One of the eight carries a separate qualification, below.

**Qualified, 2026-09-18:**

- Measurement Tampering. Its baseline cannot be contaminated, but its defended result
  holds by construction: the defense is modeled as returning the true yield values
  exactly, so no defended run can succeed. The 0.0 percent defended figure describes that
  modeling assumption rather than a measured resistance, and it stands as a statement
  about the model only. See the qualification in Section 3.
- The reproduction gate. Eight of eight outcome booleans reproduced exactly in both
  arms against the pinned evidence, confirming the substrate has not drifted since
  the recorded runs.
- Population outcome measures, which do not read the contaminated metrics.
- The Sybil defense scaling corpus, which verifies exactly against its manifest.

**Under an unresolved exposure:**

- Biological Veto Capture. Its metric carries a measured stochastic floor present in
  every cell of the published grid, D5, and a denominator that is one plus its own
  numerator, D6. At the one cell sampled, about 64 percent of the measured capture is
  present with no capture in the model. A real capture effect also survives, at a
  paired t of 3.93. Both exposures run in the direction that flatters the defense,
  and no corrected figure is stated, because D6 means the quantity itself needs
  redefining before any figure derived from it would mean anything.

**Not currently verifiable:**

- The two-transition phase boundary and the phi characterization, per Section 7.

**Bound on the entropy defect, labeled as inference.** Entropy is frozen during
planning and is therefore identical across all candidates within a decision. The
novelty term in utility is near-constant per Section 6. Entropy reaches candidate
ranking only as a common scale factor on the lineage term, able to shift orderings
only through the additive discount term, and it varies across roughly one percent
of its range. The expectation is therefore that D4 is largely inert for
outcome-driven results and that D3 is the consequential defect. This is inference
from source, it has not been measured, and Section 8 item 4 is what would settle
it.

---

## 10. How to verify

Every claim in this document is checkable from the repository at the stated commit.

Source claims are cited by file and line and can be read directly. The scale
invariance in Section 6 reproduces with the estimator alone, no model required:
construct any novelty matrix, scale it by a constant, and compare the returned
values.

Measured claims resolve to two primary records, both of which enumerate their own
artifacts:

- `simulation/diagnostics/cusum_char_stage1_report.md` for the honest baseline, the
  reproduction gate, and the accumulator timing.
- `simulation/diagnostics/cusum_char_degen_report.md` and its manifest for the
  degenerate-frequency characterization.

All `cusum_char_` artifacts are excluded from the authoritative evidence manifest
by prefix. They characterize a defective instrument and are not framework evidence.

Pinned evidence referenced above resolves through the tag
`attack-v2-revalidation-evidence`.

---

## 11. Propagation

Two distinct surfaces need correction. They overlap but are not the same set, and
treating them as one is how the smaller of them gets missed.

In both tables, the first two entries are byte-identical in the affected regions and
must be corrected together, as nothing in the repository tests that they remain in
agreement.

### 11a. The withdrawn drift claim, Section 2

| Surface | Sites |
| --- | --- |
| `docs/The Lineage Imperative v2.0.md` | abstract line 38, drift paragraph 2090-2103, table row 2132, slow-drift bullet 2509 |
| `paper/paper_v2_working.md` | abstract line 38, drift paragraph 2105-2118, table row 2147, slow-drift bullet 2598 |
| `simulation/diagnostics/sub_threshold_drift_v2_summary.md` | line 54 |
| `docs/SPECIFICATION_GAPS.md` | lines 621-624 |
| `docs/lineage_phi_program_reference.md` | line 1709 |
| `docs/RUNBOOK.md` | line 26 |
| `paper/VIII_9_application_record.md` | line 82, dated artifact, corrected inline |
| `simulation/diagnostics/attack_vector_revalidation_audit.md` | lines 862 and 907, dated artifact, corrected inline |
| `simulation/diagnostics/attack_vector_revalidation_documentation_edits.md` | dated artifact, corrected inline |

### 11b. The veto capture figure, D5 and D6

Added 2026-09-08. This surface was not in the first version of this document because
D5 and D6 did not exist then. It is larger than 11a and four of its carriers appear
nowhere in that table.

The correction here is a qualification rather than a withdrawal. The figure stands
as the number that was produced. What it does not support is the reading that some
proportion of valid successions was captured.

| Surface | Sites |
| --- | --- |
| `docs/The Lineage Imperative v2.0.md` | line 681, veto paragraph 2082-2090, table row 2133 |
| `paper/paper_v2_working.md` | line 681, veto paragraph 2097-2105, table row 2148 |
| `simulation/diagnostics/biological_veto_capture_v2_summary.md` | lines 28-46, the citable source for these figures |
| `docs/SPECIFICATION_GAPS.md` | line 615 |
| `docs/lineage_phi_program_reference.md` | line 1707 |
| `paper/VIII_9_application_record.md` | line 67, dated artifact, corrected inline |
| `simulation/diagnostics/attack_vector_revalidation_final_report.md` | line 44, dated artifact |
| `simulation/diagnostics/attack_vector_revalidation_integration.md` | lines 21 and 41, dated artifact |
| `simulation/diagnostics/attack_vector_revalidation_inventory.md` | line 192, which documents the metric definition without its consequences |
| `simulation/diagnostics/attack_vector_revalidation_audit.md` | lines 592-595 and 719, dated artifact |
| `simulation/diagnostics/attack_vector_revalidation_documentation_edits.md` | lines 23, 40, 44, 71, dated artifact |

Note that the v1.x figures for this vector came from a different runner,
`simulation/run_veto_capture_sweep.py`, and are recorded alongside the v2.0 ones in
several of these documents. D5 and D6 are established against the v2 adapter path.
Whether they apply to the v1.x figures as well is not established here and should
not be assumed in either direction.

### Out of scope for direct edit

Generated snapshots follow from their sources and require no direct edit.

Surfaces outside this repository carry both claims and are tracked separately: the
book chapter covering slow drift, and the project site.

The site post is deliberately held as of 2026-09-08, to be folded into a later
update rather than republished for each finding. Three items are known stale in it,
recorded here so the deferral is not later mistaken for an oversight. It does not
carry D6. It states the floor measurement as pending when it is complete. And it
says the published figure "sits at roughly twice that floor," which compares the
analytic per-vote floor against a mean of per-run ratios, two different statistics.
Measured like for like at the sampled cell the ratio is about 1.55, so the floor is
roughly 64 percent of the measured value rather than half of it. That sentence
understates the problem rather than overstating it, which is why holding it is
acceptable, but it is wrong and should not survive the next update.

---

## 12. Note on discovery

Recorded last, and briefly, because it is the least important thing in this
document.

No external party raised any of this. The review that found it was commissioned
because the mechanism sentence attached to the drift result was an inference rather
than a measurement, and the record said so plainly. The defects were found by
looking for the weakest claim in the project's own evidence and testing it against
source.

That does not reduce the defects, and it is not offered in mitigation. The
correction is what matters. This note exists so that the sequence of events is on
the record and not reconstructed later from memory.
