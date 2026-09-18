# Per-Vector Paired Quantities: Characterization Pre-Registration

**Date:** 2026-09-17
**Status:** pre-registration. Committed and pushed before any run it governs. No stage may
begin until this document is an ancestor of the published main branch, and each stage after
the first may not begin until the previous stage's outputs are committed and pushed. Both
conditions are verified structurally by the executor, not by instruction.
**Governs:** artifacts under the prefix `simulation/diagnostics/vector_paired_run_`.
**Substrate:** the repaired v2.1 substrate with steps 1 through 3 in place, unchanged since
the drift mapping characterization.

---

## 1. What this note implements

The instrument validation record withdraws the published defended attack rate and replaces
it, per vector, with quantities that do not rest on a predicate the unattacked baseline
also trips. Section 8 item 3 of that record leaves one thing outstanding: each vector's
paired quantity must be declared before any post-repair run that measures it. This note is
that declaration, for all ten live vectors.

The comparable binary, the action-change count of `simulation/attack_metrics_v2.py`,
discriminates for seven of the ten. It is zero in both arms by mechanism for Biological
Veto Capture and Measurement Tampering, which act on ratification and on yield evaluation
rather than on the committed action, and it is saturated at 100 of 100 in both arms for
Sub-Threshold Drift, where it measures the old fixed-latency timer's window rather than a
defense. For those three the paired differential is the only substantive measure, and two
of the three have no declared quantity yet.

## 2. What this run is not

- It is not a containment evaluation and not a defense rate. Each quantity below measures
  how a count moves when one mechanism is switched, nothing more.
- It computes no attack-success rate, and it reinstates no withdrawn figure. In particular
  the drift quantity does not say whether Sub-Threshold Drift is contained; it says whether
  the defense reduces time spent past the defection threshold. Drift remains
  uncharacterized in the published sense.
- It derives no corrected figure for any published number.
- No function computes or returns a ratio of two measured counts. D5 and D6 are why.
- It modifies no production file. Where an arm requires a mechanism to be disabled, the
  executor replaces a module attribute inside its own worker process, exactly as the drift
  mapping wrappers did, and the seven pinned sources must match before and after.

## 3. Substrate, pins, and construction

Every run executes against committed source with no working-tree modification. The seven
source pins of the detector note Section 3 must match at the start and end of every stage,
together with these:

| File | LF-normalized SHA256 |
| --- | --- |
| `simulation/attack_metrics_v2.py` | `7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323` |
| `simulation/diagnostics/detector_design_note.md` | `6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad` |

Construction, recorder, worker limits, and continuous checks follow the drift mapping note
as amended, as the detector rounds used them. Runs step to their configured limit and end
early only when `step()` returns false; early termination is recorded, never imputed.

## 4. The pairing rule, fixed now

Every paired quantity in this note is computed by `paired_difference` in the committed
`simulation/attack_metrics_v2.py`, unchanged, and every field it is applied to is an
integer count. That restriction is not stylistic: on near-constant continuous differences
the paired t statistic can reach the order of 1e16 through floating-point rounding, which
the module's own docstring records.

Pairing is exact and total. An unmatched seed in either arm, a duplicate seed, or a
mismatch between seed representations raises rather than being dropped. At exactly zero
paired standard error the t statistic is reported as undefined rather than as a number.

Each quantity below states its treatment arm, its control arm, and the sign convention.
The difference is always treatment minus control.

## 5. The declared quantity for every live vector

**The seven vectors the binary discriminates:** bootstrap subversion, engineered fragility,
evaluator collusion, ledger compromise, opaque reasoning, successor contamination, and
Sybil capture. The declared quantity is the paired difference on the per-run
`action_modified` field, as an integer of 0 or 1, treatment undefended minus control
defended at the same seed. A positive mean difference means the defense prevented
modification of the committed action. Declared here; execution is deferred, see Section 9.

**Biological Veto Capture.** The declared quantity is the paired difference on
`yield_condition_blocked_count`, treatment as-published minus control, at the same seed,
with two controls: zero validator-capture strength and zero dependency accumulation. This
is the quantity already banked from the committed pre-repair runs, where it measured a mean
difference of 0.060000 with paired standard error 0.015272 and t of 3.9289 over 300 pairs.
A positive difference means the capture mechanism blocked yields that the control ratified.

**Measurement Tampering.** The declared quantity is the paired difference on
`ratified_yields`, treatment with measurement corruption active minus control with
corruption disabled, at the same seed. A positive difference means the falsified
measurement caused yields to be ratified that the control did not ratify, which is the
decision the attack exists to reach. The registered secondary is the paired difference on
`yield_condition_blocked_count` on the same pairs. The control disables corruption by
replacing `apply_measurement_corruption` with a no-op inside the worker process; no
production file is modified, and the replacement is verified against the production method
by a gate before any run.

**Sub-Threshold Drift.** No recorded field measures this vector's mechanism, and adding one
would edit a pinned source, so the quantity is computed by this note's own executor from the
recorded trajectory. The declared quantity is the paired difference on the **count of steps
at or after attack onset with the absorption ratio g at or above g_star**, an integer count
per run, treatment with the drift check disabled minus control with it enabled, at the same
seed. g_star is 1.0965735902799727, the value fixed by the third design decision at a
reference successor capability of 2.0 and used by all three detector rounds. A positive
difference means the defense reduced the number of steps spent past the defection
threshold. This is a statement about time past a threshold, not about containment, and it
is reported with that sentence attached.

## 6. Stage A: Measurement Tampering

**Seeds:** the 60 consecutive integers from 1835087000 through 1835087059, overlapping no
seed used anywhere before.

**Arms:** treatment, the configured measurement tampering attack as production runs it; and
control, the same configuration with `apply_measurement_corruption` replaced by a no-op in
the worker process. 60 seed-paired runs per arm, 120 runs, 300 steps each, matching the
step count of the pinned corpus for this vector.

**Gate before any run:** the replacement is a no-op. Over synthetic model states, the
control method must leave every field of the state identical, and the production method
must change `avg_well_being` in every state where tampering is active. A replacement that
changes nothing in either direction is not a control.

**Registered quantities.** P1, the paired difference on `ratified_yields`, reported as pair
count, mean difference, paired standard error and t. P2, the same on
`yield_condition_blocked_count`. P3, both arms' totals for every integer yield counter,
reported as counts, never as rates. P4, the count of runs in each arm whose recorded
`action_modified` is true, which this note predicts is zero in both arms and which is
recorded so that prediction is checkable.

## 7. Stage B: Sub-Threshold Drift

**Seeds:** the 40 consecutive integers from 1835087100 through 1835087139, overlapping no
seed used anywhere before.

**Arms:** treatment, the configured drift attack with the COP drift check disabled; and
control, the same configuration with it enabled. Every other construction parameter is the
one the detector rounds used, including attack onset at step 50 and the old fixed-latency
accumulator left off. 40 seed-paired runs per arm, 80 runs, up to 300 steps each.

**Recorder:** the committed round 1 executor's recorder, which already records g on every
step.

**Registered quantities.** Q1, the paired difference on the count of steps at or after step
50 with g at or above g_star. Q2, the same count reported per arm as a distribution:
minimum, median and maximum. Q3, the count of runs in each arm that reach g_star at all
after onset. Q4, liveness: recorded steps equal completed steps in every run.

## 8. Stage C: Biological Veto Capture, post-repair re-measurement

Declared now and dispatched separately, because it is the largest of the three. Seeds are
the 300 consecutive integers from 1835087200 through 1835087499. Arms are as-published,
zero strength, and zero dependency, 300 seed-paired runs each, 900 runs. The quantity is
the one banked in Section 5. Its pre-repair value stands as recorded until this stage runs;
a post-repair value does not supersede it, because the two measure different substrates.

## 9. What is declared but not executed here

The seven binary vectors' quantity is declared in Section 5 and is not executed by this
note. Executing it means a post-repair corpus at the scale of the pinned one, 9,900 runs,
which is out of proportion to the rest of the v2.1 arc and is scheduled separately. Until
then the binary counts of the pinned pre-repair corpus stand as recorded, and no post-repair
count for those seven vectors exists or may be quoted.

## 10. Interpretation, fixed now

- A positive mean difference with a t statistic reported beside it is evidence that the
  switched mechanism moves the count in the stated direction, on these seeds, at this
  sample size. It is not a defense rate and not a containment claim.
- A difference indistinguishable from zero is reported as measured, including its pair
  count and standard error. It is not evidence of absence at any other sample size.
- The drift quantity is time past a threshold. It does not say the attack was stopped, and
  it does not reinstate the withdrawn defended attack rate.
- No quantity here is compared against a published figure, and none corrects one.

Any analysis beyond the registered quantities is labeled exploratory, placed after the
registered results, and may not be cited as a result of this pre-registration.

## 11. Amendment rule

Any change to seeds, arms, construction, recorded fields, the declared quantities, the
pairing rule, gates, or interpretation after this note is committed requires a committed
amendment to this note, pushed before any output of the affected stage is read. Outputs
already produced under the unamended plan are reported under that plan. The executor may
not inspect any output to adjust any element of this note.

## 12. Execution bounds

At most 15 concurrent workers, numerical-library threads fixed to one per worker and
verified. Stage A is 120 runs and stage B is 80, each estimated at under 20 minutes by the
detector round timings; stage C is 900 runs and is sized accordingly. Writes are restricted
to the governed prefix and `os.devnull`. Each stage emits a manifest enumerating every
output with SHA256 on LF-normalized bytes and CSV row counts, and records the committed
blob SHA1 of this note and of every pinned file.

**A housekeeping note for the operator, not a gate.** The snapshot generator's never-ingest
prefix list does not yet cover `vector_paired_run_`. It should be added before the next
snapshot regeneration, as `detector_run_` was, so that per-run artifacts stay out of the
generated snapshots while this note itself stays in.

## 13. Amendment 1, 2026-09-17: stage A construction is fixed

**Status:** committed and pushed before any stage A run exists. No output was produced
under the unamended text.

**What was underdetermined.** Section 6 names the stage A arms as the configured attack and
the same configuration with corruption disabled, but the measurement tampering vector
carries two further construction dials that "the same configuration" does not fix. One is
`cop_independent_eval`, this vector's defense, which the pinned corpus varies over both
states. The other is `base_transition_cost`, which the pinned corpus varies over 1.5, 2.0
and 3.0. An executor could satisfy the unamended text at any of six combinations, and the
paired difference would mean something different at each.

**Amended, replacing the stage A arm and seed counts in Section 6.**

- `base_transition_cost` is fixed at 1.5, the production default in
  `simulation/model.py`. It is not varied, and no result at another value is reported.
- Both defense states are run: `cop_independent_eval` false and true.
- The design is therefore 60 seeds, crossed with corruption active or disabled, crossed
  with the defense off or on: 240 runs of 300 steps, still at seeds 1835087000 through
  1835087059.
- The paired difference is computed **within each defense state**, giving two registered
  P1 values, one at defense off and one at defense on, each over 60 pairs. Neither is
  subtracted from the other, and no difference of differences is registered.
- P2 and P3 are likewise reported within each defense state, and P4 is reported over all
  240 runs.

**Why both states rather than one.** With the defense off, the quantity asks whether
falsified measurement moves ratification at all. With it on, it asks whether the defense
removes that movement. Fixing a single state would answer only one of those and would
leave the other unanswerable without a second pre-registration.

**Nothing else changes.** The quantity, the pairing rule, the control's construction by
in-process replacement, the inertness gate, the seeds, the step count, stage B, stage C,
and the interpretation of Section 10 stand as committed.

## 14. Amendment 2, 2026-09-17: the ratio prohibition binds this note's quantities

**Status:** committed and pushed before any stage A run exists. Stage A halted at its
first attempt with zero of 240 runs launched, so no output was produced under the
unamended text. The halt is recorded in
`simulation/diagnostics/vector_paired_run_a_report.md`.

**What was overbroad.** Section 2 states, without qualification, that no function computes
or returns a ratio of two measured counts. Section 3 requires every run to be constructed
through the committed pinned runner, unchanged, and the stage A dispatch requires keeping
every field that runner's `run_single` returns. That runner computes
`capture_rate` as `blocked / met` at line 435 and returns it in every row. The two
requirements cannot both hold, and the executor halted rather than choose between them,
which is correct.

**Amended, narrowing Section 2's sentence to its purpose.** The prohibition binds the
quantities this note derives, the analysis code that derives them, and everything this
note reports or cites. It does not bind the interior of a pinned file that the note
deliberately does not modify. Concretely:

- The pinned runner is used unchanged, as Section 3 requires.
- Its legacy `capture_rate` field is retained verbatim in the raw recorded rows, for
  provenance and byte-comparability with the pinned corpus.
- That field is excluded from every registered quantity, appears in no table, and may not
  be quoted anywhere in this note's outputs or in the record entry that follows.
- The analysis script asserts that no registered quantity reads it, and the report states
  that the field was recorded and not used.

**Why not strip the field instead.** Removing it would mean editing the pinned runner,
which is out of scope, or forking its row builder, which is what makes these counts
comparable to the pinned corpus in the first place. Recording a legacy value and refusing
to use it is the smaller and more auditable move.

**What D5 and D6 still forbid.** Nothing here softens them. A ratio of two measured counts
remains barred as a reported quantity, an analysis input, and a claim; the veto capture
ladder that D6 identified is the reason, and the retired per-run ratio stays retired.

**Nothing else changes.** The declared quantities, the pairing rule, the arms, the seeds,
the gates, stages B and C, and the interpretation of Section 10 stand as committed,
including Amendment 1.

## 15. Amendment 3, 2026-09-18: the Measurement Tampering control targeted the wrong mechanism

**Status:** committed and pushed after stage A completed and before any stage A' run exists.
Stage A's outputs are reported under the plan they ran, as Section 11 requires.

**What was wrong.** Section 5 and Section 6 built the control by disabling
`AIAgent.apply_measurement_corruption`. That method is the legacy v1 mechanism, which
corrupts the state the AI reads before deciding. In v2 the attack does not act there. It
acts in `adapt_yield_evaluation` in `simulation/attack_adapter_v2.py`, which falsifies the
evaluated yield values directly, and every counter the pinned runner records, including
`ratified_yields`, is computed downstream of that function. Disabling the legacy method
therefore disabled nothing the registered quantity depends on. Stage A measured exactly
that: in all 120 seed pairs, 60 in each defense state, the treatment and control counts
were identical, and P1 and P2 are 0.0 with a paired standard error of exactly 0.0. The
inertness gate passed correctly; it proved the named method was disabled, and the named
method was the wrong one. The error is in this note, not in the execution.

**A second error, found on the same reading.** P2 is registered on
`yield_condition_blocked_count`. That counter's only live writer is inside
`ratify_v2_yield`, which returns early unless the configured attack vector is Biological
Veto Capture, as Section 3 of the instrument validation record documents. For this vector
the counter is zero by construction in every arm, and stage A recorded it as zero in all
240 runs. It cannot serve as a secondary quantity here.

**Amended, adding a stage A' and replacing the control and the secondary.**

- **Control:** the v2 measurement branch disabled. `simulation/model.py` imports
  `adapt_yield_evaluation` by name, so the executor replaces the name bound in the `model`
  module's namespace, inside the worker process only, with a function returning its
  incumbent value, successor value and honest-fires flag unmodified. No production file is
  modified, and the production function is restored after each control run.
- **Gate before any run:** over synthetic inputs, the replacement returns its inputs
  exactly. The production function, with the attack active and the defense off, returns
  evaluated values that differ from the inputs; with the defense on it returns the inputs
  exactly. The gate reports all three.
- **Primary, P1':** the paired difference on `ratified_yields`, treatment production minus
  control branch-disabled, within each defense state.
- **Secondary, P2':** the same on `yield_condition_met_count`, which the v2 path does
  increment for this vector, replacing P2.
- **P3' and P4':** as P3 and P4, over stage A' runs.
- **Seeds:** the 30 consecutive integers from 1835087060 through 1835087089, overlapping no
  seed used before. The count is set by cost before any run, not by any expected effect:
  30 seeds crossed with two arms and two defense states is 120 runs, against a weekly
  execution budget that stage B also draws on.
- **Everything else** in stage A, including `base_transition_cost` fixed at 1.5, 300 steps,
  construction through the pinned runner, and the pairing rule, carries over unchanged.

**What stage A still establishes.** Its registered result stands, reported as a measurement
of the legacy method: disabling `apply_measurement_corruption` moves no recorded yield
counter in either defense state. It says nothing about the v2 attack.

**Nothing else changes.** Stage B, stage C, Sections 9 and 10, and Amendments 1 and 2 stand
as committed.
