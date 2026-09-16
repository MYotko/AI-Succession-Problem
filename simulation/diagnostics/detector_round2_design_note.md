# Sustained-Crossing Detector Evaluation: Round 2 Pre-Registration

**Date:** 2026-09-15
**Status:** pre-registration. Committed and pushed before any run it governs. Neither
stage may begin until this document is an ancestor of the published main branch, and
stage B may not begin until the stage A derivation outputs are committed and pushed.
Both conditions are verified structurally by the executor, not by instruction.
**Governs:** artifacts under the prefix `simulation/diagnostics/detector_run_r2_`. This
round adds no module: the detector is the committed `simulation/cusum_detector_v2.py`,
unchanged.
**Substrate:** the repaired v2.1 substrate with steps 1 through 3 in place, unchanged
since the drift mapping characterization.

---

## 1. What this note implements

Round 1, recorded as item 2c of the instrument validation record, measured detection
against a hazard defined as the first single step at or after onset with g at or above
g_star. Under that definition the entropy channel alarmed before the crossing in most
configured drift runs, the g channel alarmed before the crossing in none of the 160
reallocation runs, and 22 of 40 honest runs crossed as well. A crossing that honest runs
make routinely cannot be preceded by an alarm from a channel calibrated to hold honest
alarms near 5 percent. The round 1 result stands as recorded. This round tests a
different hazard definition rather than a different detector.

**Disclosure of motivation.** This note was written after an operator-side exploratory
measurement on the round 1 evaluation set indicated that honest crossings of g_star are
brief while attack crossings persist. That measurement is not a registered result, is
cited nowhere as evidence, and appears in no record entry. It motivated the hazard
definition below and nothing else. Every parameter this round consumes is derived from
the committed stage 1 honest calibration logs, which contain no attack run, and every
quantity it reports is measured on seeds that no previous run has used.

**The change.** The hazard becomes a sustained crossing: k consecutive steps at or after
onset with g at or above g_star, confirmed at the k-th such step. k is fixed by the rule
in Section 4, derived from honest data alone, and is pinned in this note with the value
that rule produces.

**A second registered variation.** The percentile behind the g threshold is a design
parameter that round 1 fixed at 97.5 without measuring the alternatives. This round
registers three thresholds computed from the same committed calibration maxima by the
same rule, so the trade between lead time and honest alarms is measured rather than
assumed. No variant is selected as the detector by this run.

## 2. What this run is not

- It is a detection characterization, not a containment evaluation. The detector runs
  offline over recorded trajectories and never acts on the model, so nothing here says
  that any attack is stopped.
- It computes no attack-success rate and derives no corrected figure for any published
  number. Sub-Threshold Drift remains uncharacterized in the published sense.
- It does not re-derive the drift mapping result of item 2b, and it changes no round 1
  constant. Round 1 is reported as it was registered.
- It does not revisit k after stage A. A larger k delays confirmation and therefore
  inflates measured lead time for free, so the rule is fixed here, its expected values
  are pinned here, and the executor halts if its own derivation disagrees.
- It selects nothing. Reporting three threshold variants is a measurement of a trade,
  not a search for the best one.

## 3. Substrate, pins, and construction

Every run executes against committed source with no working-tree modification. The same
seven LF-normalized SHA256 pins as the round 1 note, Section 3, must match at the start
and end of each stage, together with these four:

| File | LF-normalized SHA256 |
| --- | --- |
| `simulation/diagnostics/detector_design_note.md` | `6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad` |
| `simulation/diagnostics/detector_run_cal_constants.json` | `61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488` |
| `simulation/cusum_detector_v2.py` | `6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9` |
| `simulation/diagnostics/detector_run_eval_executor.py` | `6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff` |

Construction, arms, attack wrappers, recorder, and continuous checks are exactly those of
the round 1 note, Section 3, and through it those of the drift mapping note as amended.
The recorder is the one in the committed round 1 executor, including `L_t`, the novelty
vector count, and null V and shape on a step with fewer than two novelty vectors. The
model configuration is the one pasted in the round 1 note. Runs step for up to 300 steps
and end early only when `step()` returns false. Early termination is recorded, never
imputed. Attack onset is step 50 in every attack arm.

## 4. The hazard and the detector, fixed now

**The detector is unchanged.** The committed module computes the three one-sided CUSUMs
exactly as in round 1, with burn-in at steps 0 through 9, reset on alarm, and one
heartbeat per completed step. The entropy and L channels use the committed constants
without modification. The g channel uses the committed reference and allowance without
modification, at three registered thresholds, each a NumPy linear percentile of the 120
committed per-run maxima:

| Variant | Percentile | Threshold | Honest calibration runs at or above it |
| --- | ---: | ---: | ---: |
| T975, primary | 97.5 | 4.507729894543943 | 3 of 120 |
| T95, registered secondary | 95 | 4.055050806319135 | 6 of 120 |
| T90, registered secondary | 90 | 2.6499927544530903 | 12 of 120 |

T975 is the round 1 threshold unchanged, so round 1 and round 2 remain comparable on the
primary variant. Every registered quantity is reported for all three.

**The operational alarm** is the first alarm on the entropy channel or the g channel, as
in round 1. The L channel remains a comparison channel and never contributes to it. The
**detection alarm** for a run is the first operational alarm at or after step 50.
Operational alarms at steps 10 through 49 are pre-onset alarms and count as false alarms,
never as detections.

**The hazard.** For a given g_star, a run has a hazard if some span of k consecutive
steps, all at or after step 50, has g at or above g_star at every step of the span. The
**confirmation step** is the k-th step of the first such span, which is the earliest step
at which an observer could know the span had lasted k steps. A run with no such span has
no hazard, whatever its instantaneous values.

**The rule that fixes k, applied separately for each g_star.** From the 120 committed
stage 1 honest calibration logs at b84199f, for steps 10 and up restricted to steps at or
after 50, compute for each run the longest consecutive span with g at or above that
g_star, giving 120 values. Then

`k = max(2, ceil(P97.5))`

where P97.5 is the NumPy linear 97.5th percentile of those 120 values. The percentile
matches the one already used for the operational thresholds, so the honest rate of a
spurious hazard is about 2.5 percent by construction. The floor of 2 keeps a hazard from
degenerating into a single step when honest runs never cross at all.

**The values this rule produces, pinned.** The executor recomputes these from the
committed logs and halts if any differs:

| Reference successor capability | g_star | Honest runs crossing | Honest longest span, max | k |
| --- | ---: | ---: | ---: | ---: |
| 2.0, primary | 1.0965735902799727 | 42 of 120 | 22 | 9 |
| 1.5, secondary | 1.270310072072110 | 0 of 120 | 0 | 2 |
| 2.5, secondary | 0.966516292749662 | 120 of 120 | 136 | 106 |

**The 2.5 caveat, stated now.** At a reference successor capability of 2.5, g_star lies
below the honest median of g, every honest calibration run spends long spans above it,
and k is accordingly large. A hazard there measures persistence far beyond honest
behavior rather than the approach to a defection boundary. Every 2.5 result is reported
with that sentence attached.

## 5. Gates before any run

Each must pass. A failing gate halts before any run exists.

1. **Pre-registration is published.** This note is tracked, the working tree has no
   modified tracked file, the commit that last modified this note is an ancestor of the
   local `origin/main` reference, and its LF-normalized SHA256 equals the value pinned in
   the dispatch.
2. **Source pins.** Every hash in Section 3 matches, in the working tree and in the
   committed blob.
3. **Detector unit gate**, on synthetic series only, exactly the cases of the round 1
   note Section 5 item 3, run against the committed module.
4. **Drift mapping gates 2 through 6, as amended**, rerun in full for stage B. The
   Amendment 2 shape fallback check applies to every run.
5. **Recorder conformance.** One honest run at a committed round 1 seed, 25 steps,
   compared field by field against the committed round 1 log for that seed. Any
   difference halts.
6. **Constants conformance.** The values passed to the detector equal the committed
   constants bitwise, and the three g thresholds equal the values pinned in Section 4
   bitwise.
7. **Derivation conformance.** k for each g_star, recomputed from the committed
   calibration logs by the Section 4 rule, equals the pinned value.

## 6. Stage A: derivation, no model runs

Stage A reads the committed stage 1 calibration logs and constants and writes
`simulation/diagnostics/detector_run_r2_constants.json` containing: the three g
thresholds with their percentiles; k for each of the three g_star values; the 120 honest
longest-span values behind each k; the counts of honest calibration runs crossing each
g_star; and the hashes of every input it read. It steps no model and consumes no
randomness.

**Publication gate.** Stage A ends when its outputs exist. The operator reviews, commits,
and pushes them. Stage B is dispatched separately, and its first check is that the
committed stage A constants file, this note, the round 1 constants file, and the detector
module are all ancestors of `origin/main` with LF-normalized hashes equal to those pinned
in the stage B dispatch. No stage B run may start before that check passes.

## 7. Stage B: evaluation

**Seeds:** the 40 consecutive integers from 1835086600 through 1835086639, overlapping no
seed used anywhere before.

**Arms:** the nine drift mapping arms, H, M05, M1, M2, M4, R02, R05, R10, R20, 40
seed-paired runs each, 360 runs, constructed and attacked exactly as in round 1.

**Constants:** read from the committed round 1 constants file and the committed stage A
file. Never recomputed during stage B.

**Registered quantities.** Each is reported for all three threshold variants, and each
count is a count of runs.

- **F1, primary: lead time to hazard confirmation, per attack arm.** Each run is exactly
  one of: alarm before or at confirmation, when the detection alarm exists and its step
  is at or before the confirmation step; alarm after confirmation; hazard with no
  detection alarm; or no hazard. For runs with both a hazard and a detection alarm,
  report the lead, confirmation step minus detection alarm step, as minimum, median, and
  maximum, including negative values reported as negative. The honest arm is reported in
  the same form, labeled descriptive.
- **F1a, registered secondary: F1 restricted to attributable hazards**, runs whose paired
  honest run with the same seed has no hazard, or has one confirmed strictly later.
- **F2: first channel to alarm**, per attack arm, as counts of entropy first, g first,
  same step, and neither at or after step 50.
- **F3: false alarms.** Per variant: the number of evaluation honest runs with at least
  one operational alarm at steps 10 and up; the number of attack runs with a pre-onset
  operational alarm; and the number of evaluation honest runs that have a hazard, which
  the k rule places at about 2.5 percent. Counts above those design targets are reported
  as calibration shortfalls, not corrected by adjusting any constant.
- **F4: the published observable.** F1 computed for the L channel alone, and per attack
  arm the paired counts of runs in which L alone alarms before or at confirmation while
  the g channel alone does not, and the reverse.
- **F5, secondary sweep:** F1 recomputed at g_star for 1.5 and 2.5, each with its own k
  from Section 4. Labeled secondary everywhere, and the 2.5 caveat of Section 4 is
  restated wherever its numbers appear.
- **F6: liveness.** Heartbeat records equal completed steps in every run.
- **F7: auditability.** For every run, publish every span at or after step 50 with g at
  or above each g_star, as start and end steps, and every alarm step on every channel.
  This lets any reader recompute the analysis at a different k. No result at any k other
  than the registered one is reported by this run.

**Interpretation, fixed now.**

- In each reallocation arm, a run whose detection alarm precedes hazard confirmation is a
  run in which the detector warned before the sustained regime began, at that threshold
  variant. A run whose alarm follows confirmation is reported with its negative lead, not
  as a detection.
- A run with a hazard and no alarm at all is a residual of the pathway under that
  variant, and is reported as such.
- A variant that improves lead time while raising honest alarms above about 5 percent has
  bought that lead with false alarms, and the record says so. This run selects no
  variant.
- Comparison with round 1 is descriptive. The two rounds measure different hazards, so no
  round 1 count is superseded, corrected, or restated by a round 2 count.
- None of this is a containment result, a defense rate, or a corrected published figure.

Any analysis beyond F1 through F7 is labeled exploratory in the report, placed after the
registered results, and may not be cited as a result of this pre-registration.

## 8. Amendment rule

Any change to seeds, arms, construction, recorded fields, the detector, the threshold
variants, the hazard definition, the rule that fixes k, gates, or registered quantities
after this note is committed requires a committed amendment to this note, pushed before
any output of the affected stage is read. Outputs already produced under the unamended
plan are reported under that plan. The executor may not inspect any output to adjust any
element of this note, and k may not be changed after stage A by any means other than
rerunning stage A in full under an amendment.

## 9. Execution bounds

At most 15 concurrent workers, numerical-library threads fixed to one per worker and
verified. Stage A steps no model and takes seconds. Stage B is 360 runs, estimated at
under 40 minutes by the round 1 timing. Writes are restricted to the governed prefix and
`os.devnull`. Each stage emits a manifest enumerating every output with SHA256 on
LF-normalized bytes and CSV row counts, and records the committed blob SHA1 of this note,
of the round 1 note, of the round 1 constants, of the detector module, and of every
pinned source file.
