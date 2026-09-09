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

---

## 1. Summary

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

**A standing check for every later run.** The state builder substitutes a neutral
spectral shape of 1.0 when no measured shape is available, and counts each such
substitution in an observable module counter. That counter read zero throughout this
work. Any future run that consumes the projection must assert it is zero, because a
nonzero count means the shape was invented rather than measured and the results are
contaminated.

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

**Open item, not a commitment.** The snapshot generator's git introspection fails
open. When it cannot read the commit and branch it emits a warning, records both as
`unknown`, and reports completion. The tool that stamps provenance onto generated
snapshots can therefore succeed while its provenance capture has silently failed.
Found during the first veto floor attempt, at
`scripts/generate_project_knowledge_snapshots.py:140-142`. Same class as the Sybil
finding: a check reporting healthy while defeated.

---

## 9. What survives

Stated explicitly, because a defect disclosure that does not bound its own blast
radius invites the reader to assume the worst.

**Unaffected by any defect above:**

- The Nash equilibrium result. Analytic, not simulated.
- Domain Masking's analytic closure. See Section 6.
- The eight adversarial vectors that cannot be contaminated by construction. See
  Section 3.
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
