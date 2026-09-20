# In-Loop Drift Defense, Gate 1: Cross-Vector Evaluation Pre-Registration

**Date:** 2026-09-19
**Status:** pre-registration. Committed and pushed before any run it governs. No run may
begin until this document is an ancestor of the published main branch, verified
structurally by the executor, not by instruction.
**Governs:** artifacts under the prefix `simulation/diagnostics/defense_xv_run_`. This note
adds no production module and modifies no pinned source.
**Substrate:** the repaired v2.1 substrate, unchanged since the drift defense evaluation.

---

## 1. What this note implements, and why it exists

The in-loop drift defense of `simulation/diagnostics/drift_defense_design_note.md`,
evaluated at 6b3c628 and recorded as item 2f, contained the drift and reallocation
pathways it was designed against. On 2026-09-19 the operator made promotion into
production the goal, gated on four steps taken in order. This note is the first: the
defense run against the nine live vectors it was not evaluated on. Its question is not
whether the defense stops those attacks, which it was not built to do, but whether adding
it does harm: whether it makes any vector's outcomes worse, interferes with that vector's
own published defense, or changes the architecture's successions.

**A source finding that narrows this gate, stated before any run.** The plan anticipated
vectors that corrupt the defense's inputs. A reading of the pinned sources found none. The
defense reads three quantities, all from true model state: `h_n_latest`, computed from the
novelty log; g, computed from `theta_capability`, `avg_well_being` and `transfer_state`;
and the six shares of `model._last_v2_action`, the committed action. In v2 every attack
acts through `simulation/attack_adapter_v2.py` at one of three surfaces. Eight, drift among
them, replace or modify the acting AI's action in `adapt_v2_action`, which moves the
allocation but falsifies nothing the defense reads. Measurement Tampering falsifies only the two evaluated yield
values inside `adapt_yield_evaluation`. Biological Veto Capture acts only on yield
ratification in `ratify_v2_yield` and on validator state in `begin_adapter_step`. No v2
vector writes to the novelty log, to the stocks g is computed from, or to the recorded
action after commitment. Input corruption is therefore not testable with the existing
vectors, and it moves to gate 2, whose held-out attack must include it.

**A second source finding: the defense cannot weaken a vector's own defense.** Every
per-vector defense acts inside the production adapter or the yield path, which run before
the wrapper overrides anything. The wrapper replaces only the incumbent's action after the
adapter has returned it, and it never alters the adapter's event, its flags or its
decision. For the seven binary vectors, a vector whose own defense is on already returns
the honest action before the wrapper acts. The harm this gate can find is
therefore in outcomes, X1 through X3 below, not in the own defenses themselves. X4 checks
that claim rather than assuming it.

**A third source finding, recorded here because this note depends on it.** The consensus
override of the published architecture, the constraint cap with graduated trust and an
emergency path, is implemented only at `simulation/model.py` lines 914 through 1049,
inside the legacy step function. In v2 mode `step` returns `_step_v2()` at line 705,
before any of it, and neither `_step_v2` nor the adapter reads `cop_drift_check`, writes
`trust_level`, or caps the constraint. Every v2 vector acts only through the adapter, so
this holds for all ten: no v2 run reaches the published override. The only v2 defenses are
the per-vector adapter flags.

## 2. What this run is not

- It is not containment evaluation of these nine vectors and not a defense rate. The
  defense was not designed against them, and no attack-success rate is computed.
- It is not a test of input corruption, which Section 1 moves to gate 2.
- It is not a promotion decision. Passing this gate is necessary, not sufficient.
- It corrects no published figure, and no ratio of two measured counts is computed.

## 3. Substrate, pins, and construction

Every run executes against committed source with no working-tree modification. The pins of
the drift defense note Section 3 and its seven source pins must match at the start and end
of the stage, together with the drift defense note itself and the committed drift defense
executor, both pinned in the dispatch.

**Construction.** Each run is built by the committed pinned runner
`simulation/run_attack_vector_revalidation_v2.py`, imported as a module and unmodified,
through `run_single` on a task dictionary of the shape its `build_tasks` produces, in mode
`'full'`, exactly as stage A' of the per-vector note did. The per-step recorder, the
defense wrapper, the channels, the states and the consensus allocation are those of the
drift defense note Section 4, unchanged, copied from its committed executor. The wrapper
replaces `adapt_v2_action` in the `model` module's namespace for incumbent calls only.

**The cell for each vector, fixed now by one rule:** the runner's default for every
parameter that has one, which is population 200, phi 25.0 and shock magnitude 0.15, and
otherwise the lowest grid value, with the defended cell equal to the undefended cell except
for the defense.

| Vector | Undefended cell | Defended cell | Steps | Onset |
| --- | --- | --- | ---: | ---: |
| Sybil capture | population 200 | same, randomized panel | 300 | 50 |
| Measurement tampering | base_transition_cost 1.5 | same, independent evaluation | 300 | 50 |
| Ledger compromise | attribution_check false | same, cryptographic ledger | 300 | 50 |
| Successor contamination | base_transition_cost 1.5 | same, independence and evaluation | 300 | 50 |
| Opaque reasoning | population 200 | same, reasoning transparency | 300 | 50 |
| Bootstrap subversion | phi 25.0 | same, multi-candidate bootstrap | 300 | 50 |
| Evaluator collusion | population 200 | same, methodological diversity | 300 | 50 |
| Engineered fragility | shock magnitude 0.15 | same, resilience monitoring | 200 | 10 |
| Biological veto capture | dependency 0.02, strength 0.5 | same, interval 10, rotation and monitoring | 300 | 50 |

Biological veto capture's two grids differ: the defended grid starts at dependency 0.02 and
strength 0.5, which the undefended grid also contains. The rule is applied to the values
common to both, so its two cells differ only in the defense, with the lowest rotation
interval, 10, and mode `'both'`.

## 4. Arms, seeds, and design

**Arms:** for each vector, own defense off or on, crossed with the drift defense OFF or
GRADED as defined in the drift defense note. VETO alone is not run: item 2f established it
is not a safe response, and the candidate is GRADED.

**Seeds:** the 20 consecutive integers from 1835087700 through 1835087719, overlapping no
seed used or declared before. Each seed runs in all four cells of every vector. 9 vectors
crossed with 4 cells at 20 seeds is 720 runs. The seed count is set by the execution budget
before any run, not by any expected effect.

**Onset.** Wherever a quantity counts steps from onset, onset is the vector's own attack
step in the table above.

## 5. Registered quantities

Each is reported per vector and per own-defense state, and every paired value is computed
by the committed `paired_difference` in `simulation/attack_metrics_v2.py` on an integer
count, OFF minus GRADED at the same seed.

- **X1, time past threshold.** The paired difference on the count of steps at or after
  onset with g at or above g_star, 1.0965735902799727.
- **X2, survival.** The paired difference on the recorded population at the last completed
  step, and per cell the count of runs whose end reason is extinction.
- **X3, successions.** For the three vectors built with a successor, measurement
  tampering, successor contamination and biological veto capture, the paired difference on
  `ratified_yields`. The defense changes the incumbent's action, which enters the yield
  comparison, so it can change when or whether a succession happens.
- **X4, the vector's own outcome.** The paired difference on the field the per-vector note
  declares for that vector: `action_modified` for the seven binary vectors and
  `yield_condition_blocked_count` for biological veto capture; for measurement tampering
  it is X3. The wrapper runs the production adapter first, so `action_modified` records
  what the attack did to the proposal, not what was committed; X4 is reported with that
  sentence attached. With the own defense on, Section 1 predicts X4 is exactly zero for
  the seven binary vectors, and X4 is the check of that prediction.
- **X5, interventions.** Per cell, the counts of runs that entered VETO and CONSENSUS and
  their entry steps as minimum, median and maximum; and, descriptively, the count of VETO
  entries whose held action was itself attack-modified at the step it was committed, which
  the executor records from the adapter event for audit and the defense never reads.
- **X6, liveness and auditability**, as C5 and C6 of the drift defense note.

## 6. The gate criterion, fixed now

The gate asks for no harm. A **harm finding** is any of the following, OFF minus GRADED,
in either own-defense state:

1. X1 negative at a paired t of -2.0 or below: GRADED spent more steps past the threshold.
2. X2 population negative at a paired t of -2.0 or below, or any cell with more
   extinctions under GRADED than under OFF.
3. X4 nonzero in any pair for a binary vector with its own defense on, which would falsify
   the second source finding of Section 1. This one needs no t statistic and no
   confirmation run: a single pair is a finding, and it halts interpretation until the
   mechanism is found.

X3 at any value, in either direction, is a **succession finding**: it is reported, is not by
itself a harm finding, and must be addressed by the promotion plan.

**At about 50 contrasts some findings are expected by chance, so a finding is not yet a
failure.** Every harm finding is rerun at 20 fresh seeds, declared in a committed amendment
before the rerun, in that vector and cell only. It is a failure only if it recurs: at a
paired t of -2.0 or below for a t-based finding, or with more extinctions under GRADED for
an extinction finding. Gate 1 passes if no finding survives confirmation. A failure is
recorded against the candidate and returns it to design; it is not repaired in this note.

## 7. Interpretation, fixed now

- Passing means that on these nine vectors, at this sample size, adding the defense made
  nothing detectably worse. It does not mean the defense contains them.
- Any containment seen in X1 or X2 with the own defense off is reported and labeled as
  incidental: these vectors were not in the design, and a benefit here is not a registered
  claim.
- The known-pathway bias of the drift defense note is restated beside every headline
  number, and the channel constants were calibrated on the drift mapping construction, not
  on these constructions, which is restated beside every false-alarm count.

Any analysis beyond X1 through X6 is labeled exploratory, placed after the registered
results, and may not be cited as a result of this pre-registration.

## 8. Amendment rule

Any change to seeds, cells, arms, construction, the defense, gates, quantities or the
criterion after this note is committed requires a committed amendment to this note, pushed
before any output is read. Outputs already produced under the unamended plan are reported
under that plan. The executor may not inspect any output to adjust any element of this
note.

## 9. Execution bounds

At most 15 concurrent workers, numerical-library threads fixed to one and verified per
worker. 720 runs. Writes are restricted to the governed prefix and `os.devnull`. The run
emits a manifest enumerating every output with SHA256 on LF-normalized bytes and CSV row
counts, and records the committed blob SHA1 of this note and of every pinned file. The
snapshot generator's never-ingest list must gain `defense_xv_run_` before the next
regeneration.

## 10. Amendment 1, 2026-09-19: the ratio prohibition binds this note's quantities

**Status:** committed and pushed before any run exists. The first attempt halted after T0
with zero of 720 runs launched, so no output was produced under the unamended text. The
halt is recorded in `simulation/diagnostics/defense_xv_run_report.md`.

**What was overbroad.** Section 2 states, without qualification, that no ratio of two
measured counts is computed. Section 3 requires every run to be constructed through the
committed pinned runner's `run_single`, unchanged, and that function computes
`capture_rate` as `blocked / met` at line 435 of
`simulation/run_attack_vector_revalidation_v2.py` and returns it in every row. The two
requirements cannot both hold, and the executor halted rather than choose between them,
which is correct. This is the conflict Amendment 2 of the per-vector note resolved on
2026-09-17; this note repeated the unscoped sentence, and the error is in this note.

**Amended, exactly as the per-vector note's Amendment 2 did.** The prohibition binds the
quantities this note derives, the analysis code that derives them, and everything this
note reports or cites. It does not bind the interior of a pinned file that the note
deliberately does not modify. The pinned runner is used unchanged. Its legacy
`capture_rate` field is retained verbatim in the raw recorded rows for provenance, is
excluded from every registered quantity, appears in no table, and may not be quoted in
this note's outputs or in the record entry that follows. The analysis script asserts that
no registered quantity reads it, and the report states that the field was recorded and not
used. D5 and D6 still forbid a ratio of two measured counts as a reported quantity, an
analysis input, or a claim.

**Execution.** The run executes as a second attempt under the prefix
`simulation/diagnostics/defense_xv_run_a2_`, leaving the first attempt's halt artifacts
unmodified.

**Nothing else changes.** Seeds, cells, arms, construction, the defense, the gates, the
quantities, the criterion and the interpretation stand as committed.

## 11. Amendment 2, 2026-09-19: the X2 harm criterion had its sign reversed

**Status:** committed after the attempt 2 outputs were read, which Section 8 permits only
as an amendment, and this one is recorded as such. The outputs stand as produced under the
unamended plan and are reported under it, with the criterion as written applied first and
the corrected criterion applied second.

**What was wrong.** Section 6 lists as a harm finding "X2 population negative at a paired t
of -2.0 or below". X2 is defined in Section 5 as OFF minus GRADED. A negative value
therefore means the defended arm ended with more population, which is a benefit, and the
sentence labels it harm. The direction is not a matter of judgment: the drift defense note
registers the same contrast in the same direction, and item 2f reports its two drift arms
at -301.2 and -299.8 as the defense preventing extinctions. The same sentence in Section 6
about X1 is correct, because X1 counts steps past the threshold, where OFF minus GRADED
negative does mean the defended arm was worse.

**How it was found, stated plainly.** By applying the criterion to the results, which is
after the outputs were read. Under the sentence as written, attempt 2 produces six harm
findings, all of them cases where GRADED ended with about 318 more people alive and
prevented every extinction. Under the corrected sentence it produces none.

**Amended.** Harm criterion 2 reads: X2 population **positive** at a paired t of 2.0 or
above, meaning OFF ended with more population than GRADED; or any cell with more
extinctions under GRADED than under OFF. The confirmation procedure is unchanged, with the
sign of a t-based confirmation taken from this corrected direction.

**Nothing else changes.** Seeds, cells, arms, construction, the defense, the gates, the
quantities, the X1 criterion, the X4 criterion, the succession finding and the
interpretation stand as committed, including Amendment 1.
