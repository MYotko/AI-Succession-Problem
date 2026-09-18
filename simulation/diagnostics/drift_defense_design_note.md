# In-Loop Drift Defense: Containment Evaluation Pre-Registration

**Date:** 2026-09-18
**Status:** pre-registration. Committed and pushed before any run it governs. No run may
begin until this document is an ancestor of the published main branch, verified
structurally by the executor, not by instruction.
**Governs:** artifacts under the prefix `simulation/diagnostics/drift_defense_run_`. This
note adds no production module. The defense exists only inside its executor, as an
in-process replacement, and no pinned source is modified.
**Substrate:** the repaired v2.1 substrate with steps 1 through 3 in place, unchanged since
the drift mapping characterization.

---

## 1. What this note implements, and why it exists

Three detector rounds, items 2c through 2e of the instrument validation record, measured
when calibrated channels alarm against Sub-Threshold Drift. Every one of them ran offline:
nothing in the model acted on an alarm. The record states that drift's paired quantity
would rest on "the repaired detector, which does not yet exist." Two facts found while
preparing the per-vector characterization make that literal:

- The only drift defense on the v2 path is `cop_cusum_drift`, the accumulator the record
  documents as defect D2. It integrates a configured constant rather than the observed
  drift, fires about sixteen steps after onset regardless of what the attack does, and then
  returns the honest action.
- The consensus override of the published architecture, the constraint cap with graduated
  trust and an emergency path, exists only in the legacy step function. `_step_v2` never
  reaches it. The switch `cop_drift_check` that governs it is inert in v2.

This note builds the missing piece, a defense that acts on the calibrated channels, and
evaluates whether it contains the drift pathways the detector rounds characterized. It is
the first containment evaluation in the v2.1 arc.

**Two biases, stated before any run.**

1. **Known pathways only.** The allocation channel was chosen, in round 3, knowing how the
   reallocation attack works. A containment result here holds for these attack arms on
   this substrate. It is not evidence that the architecture contains an attack it was not
   designed against, and the record may not read it that way.
2. **No oracle in the response.** D2's response returns the honest action, which is the
   planner's choice before the attack modified it. No real overseer can see that. A
   defense built on it would succeed partly by construction and would make false alarms
   free, because returning the honest action changes nothing in an unattacked run. This
   defense never reads the honest action or any adapter-internal field. It reads only the
   recorded quantities its channels use and its own history, and its responses are
   actions an overseer could take.

## 2. What this run is not

- It is not a change to the published architecture or to production code. Promoting any
  part of this defense into a pinned source is a separate, deliberate step with its own
  re-pinning.
- It is not the published consensus override. The severe response below is a v2
  construction, named the consensus allocation, because the published override has no v2
  implementation.
- It computes no attack-success rate and corrects no published figure. Sub-Threshold Drift
  remains uncharacterized in the published sense; this note measures containment of named
  pathways under a named defense.
- No ratio of two measured counts is computed or reported. D5 and D6 are why.

## 3. Substrate, pins, and construction

Every run executes against committed source with no working-tree modification. The seven
source pins of the detector note Section 3 must match at the start and end of the stage,
together with these:

| File | LF-normalized SHA256 |
| --- | --- |
| `simulation/diagnostics/detector_design_note.md` | `6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad` |
| `simulation/diagnostics/detector_round3_design_note.md` | `47ea6fdd6bd4191fb262d1923c367a143c4fd279b94473497f595c7bc2ea5293` |
| `simulation/diagnostics/detector_run_cal_constants.json` | `61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488` |
| `simulation/diagnostics/detector_run_r2_constants.json` | `8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98` |
| `simulation/diagnostics/detector_run_r3_a3_constants.json` | `0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35` |
| `simulation/cusum_detector_v2.py` | `6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9` |
| `simulation/diagnostics/detector_run_eval_executor.py` | `6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff` |
| `simulation/attack_metrics_v2.py` | `7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323` |

Construction, attack wrappers, recorder and continuous checks are those of the round 1 and
round 3 detector notes and, through them, the drift mapping note as amended. The model
configuration is the one pasted in the round 1 note, with `cop_cusum_drift` false in every
arm, so D2's timer never acts and the defense below is the only drift defense present.
Attack onset is step 50, runs step up to 300 steps, and early termination is recorded,
never imputed.

## 4. The defense, fixed now

**Channels.** Three operational channels, each a one-sided CUSUM with the recursion of the
committed `simulation/cusum_detector_v2.py`, held at 0 for steps 0 through 9 and reset on
alarm, with constants read from committed files and never recomputed:

| Channel | Direction | Reference | Allowance | Threshold | Source |
| --- | --- | ---: | ---: | ---: | --- |
| Entropy, `h_n_latest` | lower | 0.9890951785336365 | 0.003549173553323096 | 0.17319485850717864 | round 1 |
| Absorption ratio, g | upper | 0.9786446054615587 | 0.022160874873702576 | 4.507729894543943 | round 1 |
| Allocation distance, A | upper | 0.27535941373839806 | 0.045310678652355926 | 0.7701182670542909 | round 3 |

A is computed exactly as the round 3 note's Amendment 1 pins it, `numpy.sum(numpy.abs(x -
m))` over the six committed shares in the registered order, with m the committed medians.
The lineage term L is not an operational channel. The defense computes the statistics
online, one step at a time; a gate requires the online alarms to equal, exactly, what
`channel_cusum` produces offline over the same recorded series.

**Operational alarm.** An alarm on any of the three channels at any step 10 or later. The
defense acts from step 10, not from onset, because an overseer does not know when an attack
begins.

**Timing.** An alarm computed from the state recorded at step t changes the incumbent's
action from step t + 1 onward. It never changes the action already committed at step t.

**States and responses.**

- **NORMAL.** The incumbent's action is the production action, unmodified.
- **VETO,** entered at the first operational alarm, at step t. Every later incumbent action
  is replaced by the action the model committed at step t minus 1, held unchanged. VETO is
  latched: it never returns to NORMAL.
- **CONSENSUS,** entered at any operational alarm at a step after VETO began, which is the
  severity rule: the lesser response is in force and the channels still alarm. Every later
  incumbent action is replaced by the consensus allocation below. CONSENSUS is latched.

**The consensus allocation.** The unattacked median of each committed action field over the
120 committed stage 1 calibration runs at steps 10 and up, passed through the production
`_normalize_action` in `simulation/attack_adapter_v2.py`. It is derived from calibration,
not from the current step's honest action, so it is not an oracle. The values, pinned:

| Field | Value |
| --- | ---: |
| `x_compute` | 0.1360229355155997 |
| `x_bio_welfare` | 0.2061409568906703 |
| `x_novelty_agency` | 0.052807183062202334 |
| `x_institutional_capacity` | 0.26711884854035045 |
| `x_transfer_comprehension` | 0.2846084192537951 |
| `x_resilience` | 0.053301656737382165 |
| `c_protective` | 0.4 |
| `c_suppressive` | 0.2 |

The pre-normalization share medians sum to 0.9599891822995968; the six above sum to 1.

**Where the defense acts.** `simulation/model.py` imports `adapt_v2_action` by name, and
every committed incumbent action passes through it with `actor_role` equal to
`'incumbent'`, on yield-evaluation steps and ordinary steps alike. The executor replaces
that name in the `model` module's namespace, inside the worker process only, with a wrapper
that calls the production function first and then, for incumbent calls only and according
to the defense state, returns the held action or the consensus allocation in its place.
Successor calls pass through unchanged. The production function is restored after every
run.

**What the defense may read.** The recorded `h_n_latest`, g and six shares at each step, and
its own state. It reads no adapter event field, no honest action, and nothing about whether
or when an attack is configured.

## 5. Arms, seeds, and design

**Attack arms,** constructed exactly as in the drift mapping note: H, unattacked; M1, the
configured drift attack at production intensity; M4, the same at multiplier 4; R02, R10 and
R20, reallocation from transfer to compute at shifts 0.02, 0.10 and 0.20.

**Defense arms:** OFF, no wrapper installed; VETO, the wrapper with escalation disabled, so a
recurring alarm is recorded but changes nothing; GRADED, the full defense of Section 4.

**Seeds:** the 20 consecutive integers from 1835087600 through 1835087619, overlapping no
seed used before. Every seed runs in all eighteen cells, so every contrast is paired within
seed. 6 attack arms crossed with 3 defense arms at 20 seeds is 360 runs. The seed count is
set by the execution budget before any run, not by any expected effect.

## 6. Gates before any run

1. **Pre-registration is published,** this note's last-modifying commit an ancestor of
   `origin/main` and its LF-normalized SHA256 equal to the pin in the dispatch.
2. **Source pins.** Every hash in Section 3 matches in the working tree and the committed
   blob.
3. **Detector unit gate,** the round 1 note's synthetic cases, against the committed module.
4. **Drift mapping gates 2 through 6, as amended.**
5. **Recorder conformance** against a committed round 1 calibration log, 25 steps, every
   field equal.
6. **Constants conformance.** Every channel constant, every median, and every consensus
   field equals the committed or pinned value bitwise.
7. **Online equivalence.** For one seed in each defense arm, the alarm steps the defense
   computed online equal, exactly, those `channel_cusum` computes offline over that run's
   recorded series.
8. **Wrapper identity.** With the wrapper installed and its state forced to NORMAL for a
   whole run, every recorded field on every step equals the OFF arm's run at the same seed.
9. **No oracle.** The wrapper is exercised on synthetic calls in which the honest action and
   every adapter event field are replaced by sentinel values; its outputs must not change.

## 7. Registered quantities

Each is reported per attack arm, and every paired value is computed by the committed
`paired_difference` on an integer count, treatment minus control at the same seed.

- **C1, primary: time past the defection threshold.** The paired difference on the count of
  steps at or after step 50 with g at or above g_star, 1.0965735902799727, for three
  contrasts: OFF minus VETO, OFF minus GRADED, and VETO minus GRADED. A positive value
  means the second arm spent fewer steps past the threshold. The third contrast is the
  registered measure of what escalation adds.
- **C2: sustained hazard.** Per cell, the count of runs with nine consecutive steps at or
  after step 50 with g at or above g_star, the hazard of item 2d, with k of 9 read from the
  committed round 2 file.
- **C3: intervention accounting.** Per cell, the counts of runs that entered VETO and that
  entered CONSENSUS, and the steps at which they did, as minimum, median and maximum.
- **C4: the cost of acting.** Per cell, the paired difference on the recorded `population`
  at the last completed step, an integer count, OFF minus each defended arm, in every attack arm including H. In H every intervention is a
  false alarm, so C4 there is the price of the defense on unattacked runs, and C3 there is
  its false-alarm count.
- **C5: liveness.** Recorded steps equal completed steps in every run.
- **C6: auditability.** Per run, every alarm step on every channel, every state transition
  with its step, and the held or consensus action applied, published so any reader can
  recompute.

## 8. Interpretation, fixed now

- A positive C1 in an attack arm means the defense reduced time spent past the defection
  threshold on that known pathway, at that sample size. It is containment of a named
  pathway under a named defense, not containment of drift in general.
- C1 in H, together with C3 and C4 there, is the defense's cost with no attack present.
  A defense that contains an attack only by degrading unattacked runs has bought the
  containment, and the record says so.
- VETO minus GRADED is the only quantity that licenses a statement about escalation.
- The known-pathway bias of Section 1 is restated beside every headline number.
- None of this corrects a published figure or says the architecture contains drift.

Any analysis beyond C1 through C6 is labeled exploratory, placed after the registered
results, and may not be cited as a result of this pre-registration.

## 9. Amendment rule

Any change to seeds, arms, construction, channels, constants, the states, the responses,
the severity rule, the consensus allocation, gates, or registered quantities after this
note is committed requires a committed amendment to this note, pushed before any output is
read. Outputs already produced under the unamended plan are reported under that plan. The
executor may not inspect any output to adjust any element of this note.

## 10. Execution bounds

At most 15 concurrent workers, numerical-library threads fixed to one and verified per
worker. 360 runs, dispatched only when a weekly execution budget can cover them. Writes are
restricted to the governed prefix and `os.devnull`. The run emits a manifest enumerating
every output with SHA256 on LF-normalized bytes and CSV row counts, and records the
committed blob SHA1 of this note and of every pinned file.

**A housekeeping note for the operator, not a gate.** The snapshot generator's never-ingest
list covers neither `drift_defense_run_` nor `vector_paired_run_`. Both should be added
before the next regeneration, as `detector_run_` was.
