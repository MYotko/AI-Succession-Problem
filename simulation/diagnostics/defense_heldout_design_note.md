# In-Loop Drift Defense, Gate 2: Held-Out Attack Pre-Registration

**Date:** 2026-09-19
**Status:** pre-registration. Committed and pushed before any run it governs, and before any
outcome of these attacks has been observed in any form. No run may begin until this
document is an ancestor of the published main branch, verified structurally by the
executor, not by instruction.
**Governs:** artifacts under the prefix `simulation/diagnostics/defense_heldout_run_`. This
note adds no production module and modifies no pinned source.
**Artifacts:** this note adopts `simulation/diagnostics/ARTIFACT_CONVENTION.md`. Merged
files are `defense_heldout_run_steps.csv` and `defense_heldout_run_completions.jsonl`.

---

## 1. What this note implements, and why it exists

Gate 1, item 2g, ran the in-loop drift defense against the nine live vectors and found no
harm. It could not test the thing that matters most for promotion: whether the defense
holds against an attack it was not designed around. Every attack in the repository either
moves the allocation far and fast, which the allocation channel was built to see, or
attacks the yield gate, which the defense does not touch. This note specifies two attacks
that exist nowhere in the substrate, writes them down before they are run, and measures
what the defense does against them.

**How the attacks were chosen, stated so the choice can be audited.** They were derived
from the definitions of the three channels, by asking what harm each channel cannot see.
They were not derived from any measured outcome, and no version of either attack has been
run in any form.

- The **allocation channel** measures the distance between the six resource shares and the
  unattacked median, with a threshold of 0.7701182670542909 against a reference of
  0.2753594137383981. Moving one small share to another moves that distance by about twice
  the share. The resilience share's median is 0.0512, so draining it entirely and putting
  it elsewhere moves the distance by roughly 0.1, which no accumulation reaches before the
  reset that follows an alarm elsewhere, and which alone never alarms.
- The **entropy channel** reads `h_n_latest`, the shape term multiplied by the repaired
  magnitude factor. Novelty amplitude scales with well-being and with one minus the
  constraint level, so an attack that touches neither leaves this channel flat. This is
  also why a suppression-only attack was rejected as the held-out candidate: the repaired
  magnitude factor would probably see it, and a held-out attack that the channels can see
  by construction tests nothing.
- The **g channel** reads capability over well-being times transfer, and the defection
  threshold g_star is the harm metric itself. An attack that does not touch capability,
  well-being or transfer directly moves g only through consequences.

The harm that fits in all three blind spots is **the removal of a buffer whose absence
only matters later**. Resilience is that buffer.

## 2. What this run is not

- It is not a claim that these are the strongest attacks available, or that passing means
  the defense is robust in general. It means the defense survived two attacks specified
  against its blind spots before they were run.
- It is not a test of input corruption. Falsifying what the defense reads requires a
  reporting surface that the substrate does not have, since the defense reads true model
  state. That design is declared in Section 7 and deferred to stage B.
- It is not a promotion decision, and no published figure is corrected. No ratio of two
  measured counts is computed. The prohibition binds this note's quantities, its analysis
  and its reporting, not the interior of any pinned file.

## 3. Substrate, pins, and construction

The pins of the drift defense note Section 3 and its seven source pins must match at the
start and end of the stage, together with that note, the cross-vector note and the
committed executors named in the dispatch.

**Construction.** The unattacked construction of the drift defense note Section 4, built as
its committed executor builds the H arm, with `cop_cusum_drift` false and no adapter attack
configured, so the only things acting on the committed action are this note's attack
wrapper and, where installed, the defense. 300 steps. Two construction parameters change
from that arm, declared here and nowhere else: `shock_step` is 150 and `shock_magnitude` is
0.60. The shock is what makes a drained buffer matter, since `apply_shock_v2` attenuates
its damage by the resilience stock and kills a fraction of the population scaled by what
survives that attenuation. The shock is present in every arm of this note, including the
control, so it is never what separates two arms.

**Where the attacks act.** Each attack is an in-process wrapper on `adapt_v2_action` in the
`model` module's namespace, inside the worker only, installed beneath the defense: the
attack wrapper calls the production function, alters the returned action, and returns it,
and the defense wrapper, when installed, wraps the attack wrapper. The order is the
production order of an attacked system: the attacker moves first, the overseer responds.
Both wrappers act on incumbent calls only and are restored after every run.

## 4. The two attacks, fixed now

**A1, the resilience siphon.** From step 50 onward, on every incumbent action, move a fixed
fraction of the current resilience share to institutional capacity, then renormalize
through the production `_normalize_action`:

```
moved = min(action['x_resilience'], rate)
action['x_resilience'] -= moved
action['x_institutional_capacity'] += moved
```

with `rate` taking the two values 0.002 and 0.006, declared now and not tuned. Nothing else
is touched: not the constraint axes, not compute, not welfare, not novelty. The attack's
goal is a population loss at the step-150 shock, and its evasion claim is that no channel
alarms before that shock.

**A2, the consensus trap.** The same siphon at rate 0.006, preceded by a burst: on steps 50
through 52 only, the six shares are replaced by the hostile allocation the adapter's own
`_hostile_action` uses, then the action returns to the siphon and never moves the shares
far again. The burst exists to make the defense latch. Against a defended system the burst
should drive VETO and then CONSENSUS, after which the defense holds a fixed allocation with
a resilience share of 0.053301656737382165 that it can never raise, whatever the state,
because both states are latched and the consensus allocation is a constant. The shock then
arrives at step 150 against a system that cannot rebuild its buffer. Against an undefended
system the same burst happens and the planner is free to respond.

**C, the control.** No attack wrapper, shock present, so the shock's own cost is measured
in both defense arms.

## 5. Arms, seeds, and design

| Arm | Attack | Defense arms | Seeds | Runs |
| --- | --- | --- | --- | ---: |
| A1-low | siphon, rate 0.002 | OFF, GRADED | 20 | 40 |
| A1-high | siphon, rate 0.006 | OFF, GRADED | 20 | 40 |
| A2 | burst then siphon 0.006 | OFF, GRADED | 20 | 40 |
| C | none | OFF, GRADED | 20 | 40 |

**Seeds:** the 20 consecutive integers from 1835087800 through 1835087819, overlapping no
seed used or declared before. Every seed runs in all eight cells. 160 runs. VETO alone is
not run; the candidate is GRADED.

## 6. Registered quantities, predictions, and the gate criterion

Every paired value is computed by the committed `paired_difference` on an integer count,
OFF minus GRADED at the same seed, reported with pair count, mean difference, paired
standard error and t.

- **Y1, survival:** the recorded population at the last completed step, and per cell the
  count of runs ending in extinction. **Harm is a positive Y1**, meaning the undefended arm
  ended with more people alive than the defended arm.
- **Y2, time past threshold:** the count of steps at or after step 50 with g at or above
  g_star. **Harm is a negative Y2**, meaning the defended arm spent more steps past it.
- **Y3, the shock's cost:** the population at step 149 minus the population at step 160,
  per run, reported per cell and as the paired difference. **Harm is a positive Y3**.
- **Y4, detection:** per run, the first alarm step on each channel, and the first step at
  which the resilience stock falls below half its step-49 value. Reported as a lead in
  steps, alarm minus depletion, where a negative lead means the alarm came after.
- **Y5, interventions and auditability:** as X5 and X6 of the cross-vector note, plus the
  resilience share the defense imposed while latched.

**Registered predictions, written before any run and reported as right or wrong.**

1. In A1 at rate 0.002, no channel alarms before step 150 in at least 15 of 20 undefended
   runs. This is the evasion claim.
2. In A1, the defense neither helps nor harms: Y1 and Y2 within a paired t of 2 either way.
3. In A2, the defense latches CONSENSUS in at least 18 of 20 defended runs.
4. In A2, the defense harms: Y1 positive at a paired t of 2 or above. This note expects the
   trap to work, and says so before running it.

**The criterion.** Gate 2 fails if, under either attack, the defended arm is worse than the
undefended arm in the direction named above, at a paired t of 2.0 or above, or with more
extinctions under GRADED than under OFF in any cell, and the finding recurs at 20 fresh
seeds declared in a committed amendment before the rerun. Detection and containment results
are reported as the scope of what the defense can claim, not as pass or fail. A failure
returns the candidate to design and is not repaired in this note.

**Sign discipline, added because of the error in the cross-vector note.** Each quantity
above names its harm direction in words as well as in sign. The analysis script asserts,
against a fixture with a known-worse defended arm, that its criterion labels that fixture
harm, and the report prints that assertion's result.

## 7. Stage B, declared now and not executed here

Input corruption cannot be tested against a defense that reads true model state. Stage B
introduces a reporting surface: the executor computes each channel's input from a report
object, identical to the true values unless an attack alters them, and the defense reads
the report rather than the state. That is a change to the defense's interface and is
declared here so it cannot later be presented as part of the original design. Its attack
falsifies the reported entropy and allocation while the true state degrades. Stage B is
pre-registered in its own amendment to this note, with its own seeds, before it runs.

## 8. Interpretation, fixed now

- Surviving A1 and A2 means the defense was not broken by two attacks aimed at its blind
  spots. It is not evidence of robustness against attacks not specified here.
- If prediction 1 holds, the record states plainly that the defense is blind to a slow
  buffer drain, whatever the harm numbers show.
- If prediction 4 holds, the defense's latching is a weapon in an attacker's hands, and
  that is a gate 2 failure however good the other numbers are.
- The known-pathway bias of item 2f, and the calibration mismatch recorded in item 2g,
  are restated beside every headline number.

Any analysis beyond Y1 through Y5 is labeled exploratory, placed after the registered
results, and may not be cited as a result of this pre-registration.

## 9. Amendment rule and execution bounds

Any change to the attacks, seeds, arms, construction, the defense, quantities, predictions
or the criterion after this note is committed requires a committed amendment, pushed before
any output is read. Outputs already produced under the unamended plan are reported under
that plan. The executor may not inspect any output to adjust any element of this note.

At most 15 concurrent workers, numerical-library threads fixed to one and verified per
worker. 160 runs. Writes are restricted to the governed prefix and `os.devnull`. The
manifest follows Section 3 of the artifact convention.
