# Phase B Rerun From the Recovered Generating Code: Pre-Registration

**Date:** 2026-09-24
**Status:** pre-registration. Committed and pushed before any measured run. No measured run
may begin until this document is an ancestor of the published main branch, verified
structurally by the executor.
**Governs:** artifacts under the prefix `simulation/diagnostics/phase_b_rerun_`.
**Artifacts:** adopts `simulation/diagnostics/ARTIFACT_CONVENTION.md`.
**Implements:** the second stage of item 4 in `docs/v2_0_instrument_validation_record.md`,
announced in the record entry of 2026-09-24 at b901c5fe.
**Supersedes nothing.** The first-stage note, `phase_b_reconstruction_design_note.md`, its
two amendments and its registered verdict, not faithful, stand as recorded.

---

## 1. What this is, and the order of events

The first stage rebuilt the Phase B corpus from its published aggregates because the
generating script was missing. It reproduced the Category B succession cliff exactly and
failed the Category A and phi targets. On 2026-09-24 a compiled copy of the missing script
was recovered. This note reruns that code, on the model code it ran against, at the seeds it
used.

**This is a rerun of recovered code, not a reimplementation.** The executor loads the
recovered bytecode and calls its own task builder and its own per-run function. The grids,
seed rule, run construction, horizon and survival rule are the original's by execution, not
by transcription. Section 3 states the few elements that are not executed from the recovered
code.

**Order of events, stated in full because this note follows results.** The reader is entitled
to know what the author knew when writing it:

1. 2026-09-21: the first-stage note is committed at 6d698f21. Amendment 1 follows at 20a6327a.
2. 2026-09-22: Amendment 2 is committed on a side branch at 0a8047b6 and merged at 59dcc5ae.
3. The phi category completes and is recorded at 61013c8a, with zero survival on both
   substrates. Categories A and B complete and land at 3813897e. T1 fails at 1 of 9 points,
   T2 passes at 5 of 5, and T3 fails.
4. Category C is stopped by the operator and excluded.
5. 2026-09-24: the bytecode is recovered from a USB drive. Its disassembly shows three
   construction differences from the first stage.
6. An exploratory recomputation then applies the original survival rule to the first stage's
   final populations at its 300-step horizon. It is recorded at b901c5fe as exploratory.
   Category A comes out above the published curve at every reproduction rate.
7. This note is drafted.

The author therefore writes knowing that the first stage's survival rule was wrong and
roughly which way the original rule moves the curve. **The safeguard is that this note
chooses no construction parameter.** Every element that the first stage had to decide is
taken by execution from the recovered code. The elements that remain choices are the
substrate commit, the interpreter, the seed counts and the verdict rules. Each is stated in
Sections 4 to 9 with its reason, and none is a value that could be tuned toward a target.

## 2. The evidence, pinned

The drive holds files copied from the third development machine, which Section 7 of the
record describes as failed and not searchable. It is retained unmodified and read only.

| File | Path on the drive | SHA256 |
| --- | --- | --- |
| Bytecode | `ai-succession-problem/simulation/diagnostics/__pycache__/monte_carlo_phase_b.cpython-313.pyc` | `2d79795ca50405ff2586a2751fb38861b592d32008aa5e1aebffd07619781d6b` |
| Pilot CSV | `ai-succession-problem/data/alpha_succession_sweep_pilot.csv` | `16834e6e59ffd3467a085c1c3b16d65c82685792dffd16684d13da99bc5b4152` |

The bytecode is 31,104 bytes. Its header carries magic number 3571, which is CPython 3.13,
and is a timestamp-validated file. It records a 21,497-byte source last modified
2026-06-09 at 23:14:52 UTC, which is 19:14:52 EDT.

**Committed with this note, under `simulation/diagnostics/phase_b_rerun_evidence/`:**

- the bytecode, byte-identical to the drive copy;
- its full disassembly as text, so a reader can check every claim here without tools;
- a provenance file recording the drive paths, hashes, header fields and the date of
  recovery.

The pilot CSV is committed alongside as evidence for Section 7 of the record. Its columns and
values show it is output of the April and May alpha succession sweep on the v1.x model, not
Phase B. It plays no part in this note's measurement.

**What the evidence does not show.** The bytecode reflects the source as of June 9. The
integration analysis is dated June 18. Edits to the script between those dates are possible,
and nothing on the drive excludes them. No results file from Phase B or the phi corpus was on
the drive.

## 3. What is executed, and what is not

**Executed from the recovered code, unmodified:**

- `MODE_CONFIG`, the grids and horizon for modes A, B and C, with 500 steps;
- `_build_tasks`, which enumerates each mode's cells and seed indices;
- `_task_seed` and `deterministic_seed`, which derive each run's seed;
- `_run_single`, which constructs the successor and the model and runs them. It stops early if
  the model's step returns false, computes `survived` as final population at or above 30, and
  returns the original row.

The row's fields are the original's 30 `CSV_FIELDS`. The executor appends its own provenance
fields and does not alter any original field.

**Not executed from the recovered code:**

- **Scheduling, persistence and resume.** The original's `run_sweep`, CSV writer and progress
  logger are replaced by the executor. They schedule and record runs; they do not construct
  them. The replacement is needed to meet the repository's operational requirements.
- **Analysis.** The original's `analyze` and summary functions are not called. They are used
  only as the definition of what the published figures measured. Survival rate is the mean of
  `survived`, and fire rate is the mean of `yield_fired`, as the disassembly shows.
- **The phi corpus.** The program reference, Part IX.1, records it as "Piece 1": 12,000 runs
  across 16 phi values and 3 reproduction rates with no successor, produced before the default
  phi changed from 10 to 25 on June 7. It was produced by a different script, which has not
  been recovered. **The phi target is out of scope for this note.** The first stage's phi arm
  ran with a successor present, so it did not match the documented construction either. The
  record will say so.

## 4. Substrates

The recovered script imports `AIAgent` from `simulation/agents.py` and `GardenModel` from
`simulation/model.py`, both resolved relative to its own location.

- **Original, arm O:** a git worktree pinned at `45409d469a82bb599fe354e8ae3760e4cc3af048`,
  2026-06-08 20:54 EDT. It is the last commit on main before the script's source timestamp.
  No file under `simulation/` outside `diagnostics/` changes between this commit and
  `ef43818a`, the last commit before the integration analysis's June 18 date. The model code
  is therefore the committed code for the whole window in which the corpus could have run.
  `model.py` and `agents.py` next change on 2026-07-06.
- **Current, arm R:** a git worktree pinned at the commit that adds this note, recorded in
  the manifest. It includes the v2.1 estimator repair and every model change since
  June.

**The first stage's pre-repair pin, 2044f50a, was not the original's model code.** Between
45409d46 and 2044f50a, `model.py` gains 161 changed lines and `agents.py` 37. They include a
change to how opacity accumulates, which alters default behavior, and an adapter call on
every step. That arm is not rerun here, and nothing in this note depends on it.

**Uncommitted edits on the failed machine cannot be excluded.** If the original ran against a
working tree that differed from 45409d46, this substrate differs from it, and nothing in the
recovered evidence can show that.

For each arm, a copy of the bytecode, hash-verified, is placed in the worktree's
`simulation/diagnostics/` as `monte_carlo_phase_b.pyc`. Its module-relative imports then
resolve to that worktree. Both worktrees are outside the repository's working tree, so a commit
to main during the batch does not change either substrate.

**Interpreter.** The bytecode loads only under CPython 3.13. The machine has 3.14 only. The
operator installs the current CPython 3.13 release from python.org before any run; the
implementing agent does not download it. The numpy version the original used is not
recorded anywhere. The executor records the version it uses, and it is an uncontrolled
difference.

The June model code draws from numpy's legacy global generator, through `np.random.seed` and
`RandomState`. numpy holds that stream fixed across versions. **Identical per-run results are
therefore possible but not guaranteed.** Floating-point differences between builds could still
diverge a marginal run.

## 5. Seeds

Every run's seed is the original's: `_task_seed(mode, rr, phi, alpha, successor_capability,
cop_cost_audit, i)`. That is the integer value of the MD5 hex digest of the label
`phase_b|{mode}|{rr:.5f}|{phi:.4f}|{alpha:.4f}|{capability:.4f}|{cop}|{i}`, modulo 10,000,
with the seed index `i` running from 0. The executor computes no seed of its own.

Seed index `i` in this rerun is the same run as seed index `i` in the original corpus. A
reduced seed count therefore takes the first `k` indices of each cell, and those runs are a
subset of the original corpus's runs, not a new sample.

## 6. Parts, grids and cost

The batch runs in four parts, in this order. Each part is merged and landed on its own.

| Part | Arm | Mode and cells | Seed indices | Runs |
| --- | --- | --- | --- | ---: |
| 1, exactness probe | O | B, five cliff pairs by four rr: 20 cells | 0 to 74 | 1,500 |
| 2, survival landscape | O | A, full grid: 108 cells | 0 to 99 | 10,800 |
| 3, cost-audit probe | O | C, full grid: 54 cells | 0 to 149 | 8,100 |
| 4, current substrate | R | A, full grid; C, full grid | A 0 to 24; C 0 to 49 | 5,400 |

**The Part 1 cells** are the (alpha, successor capability) pairs whose published fire rate
across the four reproduction rates is a range strictly inside 0 to 100 percent, or touches one
end only. The published ranges are from Section 1 of `phase_b_integration_analysis.md`. At 75
runs per cell they fix exact counts:

| alpha | capability | published range | runs that fired, min and max |
| --- | --- | --- | --- |
| 0.50 | 5.0 | 88.0% to 96.0% | 66 and 72 |
| 1.00 | 2.5 | 98.7% to 100% | 74 and 75 |
| 1.00 | 3.0 | 4.0% to 13.3% | 3 and 10 |
| 1.25 | 2.5 | 30.7% to 49.3% | 23 and 37 |
| 1.50 | 2.5 | 0% to 1.3% | 0 and 1 |

Parts 2 and 3 are the original categories at their original seed counts. Only at full counts
can the rerun's aggregates be compared with the published aggregates for identity. Part 4
takes the first 25 and first 50 seed indices, so every Part 4 run has a partner at the same
seed in Parts 2 and 3.

**Cost, an estimate.** The first stage ran about 370 runs per hour on its pre-repair arm and
about 307 on its repaired arm, at 10 workers and 300 steps. Scaled to 500 steps, that suggests
roughly 200 to 250 per hour on arm O and about 185 on arm R. That gives about 7 hours for
Part 1, 45 to 55 for Part 2, 33 to 40 for Part 3 and 29 for Part 4. The total is 115 to 130
hours at 10 workers, or about 80 to 90 at 15. Runs that end early make the true figure lower.
Test mode measures the rate before the operator launches.

## 7. Targets

All are quoted from `phase_b_integration_analysis.md`, Section 1.

- **P, Category B cliff ranges:** the ten counts in the Part 1 table.
- **T1, Category A survival by rr,** n = 1,200 per rr, with the published standard error:
  0.2% (0.12pp), 0.9% (0.28pp), 1.1% (0.30pp), 2.9% (0.49pp), 4.8% (0.62pp), 12.2% (0.95pp),
  34.5% (1.37pp), 60.8% (1.41pp) and 86.5% (0.99pp), at rr 0.055 through 0.066. The rate
  and its standard error together admit only these counts of 1,200: 2, 11, 13, 35, 58, 147,
  414, 729 or 730, and 1,038.
- **T4, Category C:** audit off 25.4% and audit on 24.9%, n = 4,050 each. The delta, audit on
  minus audit off, is -0.47pp with pair standard error 0.96pp. By rr the delta is -0.30pp,
  -0.37pp and -0.74pp at 0.057, 0.060 and 0.064. Two of the 27 cells cross two standard
  errors: +0.080 at rr 0.060, alpha 1.0, capability 3.0; and -0.027 at rr 0.057, alpha 1.5,
  capability 2.5.

T2 is not retested; the first stage's result stands. T3 is out of scope under Section 3.

## 8. Registered quantities

- **R1:** for each Part 1 cell, runs that fired, and per pair the minimum and maximum across
  rr.
- **R2:** Category A survival by rr on arm O, as a count of 1,200 and a rate. Also the phi by
  alpha structure at each rr, reported descriptively.
- **R3:** Category C survival by audit state on arm O, the delta overall, by rr and by cell,
  and the pair standard error.
- **R4:** for Part 4, the paired difference R minus O in `survived` at matched seeds, by rr
  for A and by audit state for C, with paired standard errors. **R4 is the combined effect of
  every model change since June 8, including the v2.1 estimator repair. It is not the repair's
  effect alone,** and it is never reported as such.
- **R5, liveness and provenance:** the interpreter and numpy versions, both worktree HEADs, the
  bytecode hash verified before load, and a count of rows whose original `error` field is
  non-empty. Also per-run hashes in the manifest.

No ratio of two measured counts is computed. A rate here is a count over a fixed design n.
The prohibition binds this note's quantities, analysis and reporting, not the interior of
the recovered code, whose fields are kept verbatim.

## 9. Verdicts, declared now

Each target receives one of three verdicts.

**Identical.** The rerun's count equals a count consistent with every published figure at its
published precision. For P, each minimum and maximum equals the tabled count. For T1, the
count at each rr is one of the counts listed in Section 7. For T4, the audit-off count is
1,027, 1,028 or 1,029 of 4,050, and the audit-on count is 19 fewer. The by-rr deltas are -4,
-5 and -10 of 1,350.

**Faithful.** Not identical, but the published value lies within the rerun's own interval. The
interval is the Wilson score interval at z = 2 on the rerun's estimate. That corrects the
first stage's defect, in which a zero estimate gave a zero-width tolerance.

- T1 is faithful at 7 or more of 9 rr points, with survival monotonic non-decreasing in rr.
- T4 is faithful if the published delta lies within two paired standard errors of the rerun's
  delta.
- P is faithful if, for every pair, the published minimum lies within the interval of the
  rerun's lowest cell across rr, and the published maximum within that of its highest.

**Not faithful.** Otherwise.

**Branch rules, committed in advance:**

- **P identical.** The recovered code on the June substrate in this environment reproduces the
  original runs. T1 and T4 are then expected to be identical, and a result short of that is a
  finding in its own right. It would point to the script changing after June 9 or to an
  uncommitted substrate, and the record will say it cannot distinguish those.
- **P faithful but not identical.** The environment or the substrate differs somewhere. T1 and
  T4 are judged as faithful or not, and no claim of identity is made for any target.
- **T1 identical or faithful.** The published Category A figures are reproduced by their own
  generating code. The first stage's T1 failure is then attributed in the record to its
  construction, with the recovered code as the evidence.
- **T1 not faithful.** The published Category A figures are not reproduced by their recovered
  generating code on the committed substrate of the time. That is reported as a failure to
  reproduce the published figures, not of the reconstruction. Whether they stand is the
  operator's decision, and the record will name the possible causes: later edits to the
  script, an uncommitted substrate, or the environment.
- **T4** is reported under the same three verdicts. At full count it is the original test at
  the original power.
- **Part 4** is reported whatever Parts 1 to 3 show. Its meaning depends on them. If T1 is not
  faithful, R4 is a difference between two substrates, neither of which is shown to match the
  published figures, and the record will say so.

**Nothing is adjusted until it matches.** No part is rerun with a different seed, substrate,
interpreter or grid because of its result. A failure is reported under the plan that produced
it, and any further stage needs its own note.

## 10. The author's expectation, stated before any run

This is a prediction, not a criterion, and it is recorded so that it can be seen to be wrong.
The author expects P to be identical or nearly so. T1 is expected to be faithful and perhaps
identical. The first stage's exploratory recomputation overshot the published curve at 300
steps, and 200 further steps can only lower final populations that are still falling. T4 is
expected to be faithful, as a null.

## 11. What this cannot establish

- That the published figures came from exactly this code. The bytecode is from June 9, and
  edits after that date are not excluded.
- That the substrate was the committed one. Uncommitted edits on the failed machine are not
  excluded.
- Anything about the phi characterization, which this note does not test.
- The v2.1 repair's own effect on the published figures. Part 4 measures every change since
  June together.

## 12. Execution, which is the operator's

The implementing agent builds the executor, `simulation/diagnostics/phase_b_rerun_executor.py`,
and validates it in test mode. It does not launch the measured batch. The operator installs
CPython 3.13 and launches the batch, which runs the four parts in order from one command.

**Worker count is scheduled, and changes without a restart.** The executor re-reads two
operator-editable files at least every 30 seconds:

- `phase_b_rerun_schedule.json`, a default worker count and time-of-day rules. The initial
  schedule is 15 workers, and 10 on weekdays from 07:00 to 17:00 local time.
- `phase_b_rerun_runtime_control.json`, an optional override, either an explicit worker count
  or a named mode, with an optional expiry. It takes precedence over the schedule while it
  is in force. The latest override is preserved across resume.

No setting may exceed 15, the operator-stated budget of 16 cores less one. A reduction stops
new dispatch until active runs fall to the new cap. No running job is killed, and the time
the reduction takes effect is logged. The count affects only when runs start, never which
runs exist or their seeds.

The executor also meets the repository's other operational requirements:
- one numerical-library thread per worker, set before numpy loads, with the effective limit
  verified and recorded;
- durable completion records, each published only after its row is complete;
- resume that validates and skips completed runs, and restarts in-flight runs from their
  original seed;
- a progress file carrying completed, running and pending counts;
- execution metadata recording the machine, the CPU budget, mode changes and restarts;
- the artifact convention's merge at the end of each part.

**Resume identity is pinned to the executor file's hash, the bytecode's hash and both
worktree HEADs, not to main's HEAD.** A commit to main during the batch that touches none of
these does not invalidate it. That corrects the operational failure of the first stage.

**Test mode is declared non-registered.** A `--test-mode` run executes a small declared
subset, using seed indices outside every registered range, and writes under
`phase_b_rerun_smoke_`. It exists to validate the code and measure the run rate. Its outputs are
not a measurement and may not be cited as evidence for any quantity here. They are committed
separately with that statement attached, and nothing in test mode may be used to adjust any
element of this note. Test mode also checks two things:

- that the loaded module's `MODE_CONFIG`, `SURVIVAL_THRESHOLD`, `N_STEPS` and seed function
  equal the values in Sections 5 and 6;
- that the original `_run_single` runs without error on both substrates.

If it cannot run on arm R, Part 4 is dropped by amendment, not repaired by editing the
original code.

**A row whose original `error` field is non-empty is a finding.** It is not retried silently.
The original corpus reported zero errors in 29,400 rows.

## 13. Amendment rule

Any change to the parts, grids, seeds, seed counts, substrates, interpreter, targets, verdict
rules or branch rules after this note is committed requires a committed amendment, pushed
before any output of the affected part is read. Outputs already produced under the unamended
plan are reported under that plan. Neither the implementing agent nor the operator may
inspect any measured output and then adjust any element of this note.
