# v2.0 Instrument Validation Record

**Date:** 2026-09-07
**Substrate under examination:** commit `1261c9f430411b9fa0060a7384bf4ec5175e4f4e`
**Status:** primary disclosure. This document is the citable source for the defects
described below and supersedes any earlier characterization of the affected claims.

---

## 1. Summary

Four defects were found in the v2.0 simulation substrate and in the success metrics
used for the adversarial revalidation. One published claim is withdrawn. One
published figure is placed under an unresolved exposure. A separate archival gap
in the pre-manifest era is recorded in Section 7.

The defects, in the order they act on the measurement chain:

**D1. Baseline contamination in three success metrics.** Three of the ten live
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

A fifth item is recorded as a structural observation rather than a defect in
Section 6.

**What this is not.** These are not measurement errors in the sense of a metric
that mismeasured a sound mechanism. D1 is a metric defect. D2, D3, and D4 are
defects in the framework's own substrate. Withdrawing the affected claim does not
clear them. It exposes them.

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

Seven of the ten cannot be contaminated by construction, by two distinct
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

Three read a recorded state series or counter and are contaminable in principle:

| Vector | Expression | Exposure |
| --- | --- | --- |
| `sub_threshold_drift` | `max(total_suppression) > 0.75` | Contaminated. Measured. Result withdrawn. |
| `engineered_fragility` | `min(resilience_stock) < 0.25` | Contaminable, but empirically bounded. Its defended attack rate is 0.0 percent, which bounds baseline incidence at zero in that configuration only. |
| `biological_veto_capture` | `yield_condition_blocked_count > 0` | Contaminable, and **not bounded**. Its defended result is a capture rate of 0.1197 rather than zero, so no empirical bound follows. |

The Biological Veto Capture exposure is unresolved. Its figure is published. A
baseline arm for it is open work and is item 2 in Section 8.

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

**1. Design decisions fixed and published before any implementation.** Three
decisions are open and are recorded here as open, deliberately, so that the repair
is on record as having been designed before the numbers that would shape it
existed:

- *Suppression semantics.* Whether suppression enters the objective as a direct
  cost, or through a repaired entropy channel, or both. D3 and D4 are separate
  defects and a repair addressing one does not address the other.
- *Attack-success definition.* Whether success means the adversary changed the
  outcome or changed the action. Seven vectors already answer the second question,
  which is why they cannot be contaminated. A paired-baseline differential resolves
  all three contaminable vectors uniformly, but makes them non-comparable to the
  seven in the published table.
- *Detector observable.* What quantity a drift detector integrates. Per D2 this is
  not a selection among available signals. The v2 path currently computes no
  divergence observable at all, so this is a decision about what to build. It also
  depends on the suppression-semantics decision and cannot be settled before it.

*Completion condition:* the three decisions are written and committed before any
v2.1 code is written.

**2. Baseline arm for Biological Veto Capture.** The one unresolved contamination
exposure. Executed against the current substrate with the attack vector omitted and
the configuration otherwise unchanged, following the pattern already used for the
drift baseline.

*Completion condition:* a reported baseline incidence of blocked yields with no
attack configured, either zero or nonzero, both reported.

**3. v2.1 implementation and component validation.** Including a bidirectional
check on the entropy estimator specifically. A repair tested only in the direction
of the known defect is not validated. Also resolves the inverse-scarcity question
raised in Section 6 against the published architecture.

*Completion condition:* component validation passes, including a positive control
that would fail if the repair were absent.

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

**Open item, not a commitment.** The third development machine is in a failed state
and holds an unknown quantity of untracked output. There is no inventory of what
that might be, because untracked files were never enumerated anywhere. This is the
same failure mode as Section 7, still live, on a machine that cannot currently be
reached.

---

## 9. What survives

Stated explicitly, because a defect disclosure that does not bound its own blast
radius invites the reader to assume the worst.

**Unaffected by any defect above:**

- The Nash equilibrium result. Analytic, not simulated.
- Domain Masking's analytic closure. See Section 6.
- The seven adversarial vectors that cannot be contaminated by construction. See
  Section 3.
- The reproduction gate. Eight of eight outcome booleans reproduced exactly in both
  arms against the pinned evidence, confirming the substrate has not drifted since
  the recorded runs.
- Population outcome measures, which do not read the contaminated metrics.
- The Sybil defense scaling corpus, which verifies exactly against its manifest.

**Under an unresolved exposure:**

- Biological Veto Capture, whose defended capture rate of 0.1197 is published and
  whose metric is contaminable with no empirical bound. Section 8 item 2.

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

The withdrawn claim in Section 2 appears on the following surfaces. The first two
are byte-identical in the affected regions and must be corrected together, as
nothing in the repository tests that they remain in agreement.

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

Generated snapshots follow from their sources and require no direct edit.

Surfaces outside this repository also carry the claim and are tracked separately:
the book chapter covering slow drift, and the project site.

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
