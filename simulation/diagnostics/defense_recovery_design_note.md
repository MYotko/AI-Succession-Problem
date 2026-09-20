# In-Loop Drift Defense, Gate 3: Recovery Rule Pre-Registration

**Date:** 2026-09-20
**Status:** pre-registration. Committed and pushed before any run it governs. No run may
begin until this document is an ancestor of the published main branch, verified
structurally by the executor, not by instruction.
**Governs:** artifacts under the prefix `simulation/diagnostics/defense_recovery_run_`.
This note adds no production module and modifies no pinned source.
**Artifacts:** adopts `simulation/diagnostics/ARTIFACT_CONVENTION.md`.

---

## 1. What this note implements, and why it exists

Items 2f, 2g and 2h evaluated a defense whose two states latch forever. Every stage found
the same standing cost: in the cross-vector gate, the three constructions carrying a
successor alarmed in 20 of 20 runs; in the held-out gate, a single shock at step 150 drove
the defense into its consensus state in every arm, attacked and unattacked alike, for the
remaining 150 steps. A defense that commits permanently after one shock is not a defense an
operator can deploy, and gate 3 of the promotion plan exists to fix that.

The operator chose step-down recovery with a quiet period on 2026-09-20. This note
specifies it, measures what it costs in containment, and selects its one free parameter by
a rule declared before any run.

**What recovery can and cannot do, stated before any run.** Handing control back can only
reduce containment, never increase it. The question is not whether recovery costs something
but whether the cost is small enough to be worth a defense that releases its grip. This
note is written so that "no recovery rule qualifies" is a possible and reportable outcome.

**This changes the defense, so it changes what earlier gates describe.** Gates 1 and 2 were
run against the latching defense. Their results do not automatically transfer to a defense
that recovers. Stages B and C below re-run enough of them against the recovered version,
and until those stages complete, no claim from item 2g or item 2h may be attached to the
recovered defense.

## 2. What this run is not

- It is not a promotion decision. Gate 4 remains.
- It is not a redesign of the channels, the consensus allocation or the severity rule. Only
  de-escalation is added.
- It corrects no published figure, and no ratio of two measured counts is computed. The
  prohibition binds this note's quantities, its analysis and its reporting, not the interior
  of any pinned file.

## 3. The recovery rule, fixed now

The defense of the drift defense note Section 4 is unchanged in escalation: an operational
alarm from step 10 onward drives NORMAL to VETO, and a further alarm while VETO is in force
drives VETO to CONSENSUS. Two transitions are added:

- **CONSENSUS to VETO** when no channel has alarmed for `k` consecutive completed steps.
  On entry to VETO by this route, the held action is the action committed on the step before
  the transition, which is the consensus allocation as committed.
- **VETO to NORMAL** when no channel has alarmed for a further `k` consecutive completed
  steps.

Escalation always preempts de-escalation: an alarm on any step resets the quiet counter to
zero and applies the escalation rule first. A state entered by recovery can be escalated
again with no limit, and every transition in both directions is recorded.

**The free parameter.** `k` takes the three values 10, 20 and 40, declared now. They are not
tuned: 10 is the channels' burn-in length, 20 is twice it, and 40 is four times it.

## 4. Substrate, construction, arms and seeds

**Construction:** the construction of the held-out note, which is the unattacked H-arm
construction of the drift defense note with `shock_step` 150 and `shock_magnitude` 0.60,
300 steps, `cop_cusum_drift` false. The shock is present in every arm, because the shock is
what produced the standing cost this note addresses.

**Attack arms,** each implemented as the committed executors implement them:
- **H:** no attack. The shock is the only perturbation.
- **M1:** the configured drift attack at production intensity, as in item 2f.
- **A3:** the full-share resilience drain of the held-out note's Amendment 2, which met the
  attack-validity gate at b1a54983.

**Defense arms:** OFF; LATCHED, the defense exactly as gates 1 and 2 ran it; and RECOVER-10,
RECOVER-20 and RECOVER-40.

**Seeds:** the 20 consecutive integers from 1835088000 through 1835088019, overlapping no
seed used or declared before. Every seed runs in all fifteen cells. 3 attack arms crossed
with 5 defense arms at 20 seeds is 300 runs.

## 5. Registered quantities

Paired by seed, computed by the committed `paired_difference` on integer counts. Each names
its harm direction in words. Contrasts are LATCHED minus RECOVER-k unless stated.

- **R1, containment retained.** Steps at or after step 50 with g at or above g_star.
  **Harm is a negative R1**, meaning the recovered defense spent more steps past the
  threshold than the latching one.
- **R2, survival.** Population at the last completed step, and extinctions per cell.
  **Harm is a positive R2**, meaning the recovered defense ended with fewer people.
- **R3, the standing cost recovery is meant to reduce.** Per run, the number of steps spent
  in VETO or CONSENSUS, and per cell the count of runs still in a non-NORMAL state at the
  last completed step. Reported as OFF-free quantities per defense arm, not as a harm
  direction: a lower value is the intended effect, and R3 is what recovery buys.
- **R4, stability.** Per run, the count of transitions in each direction and the count of
  re-escalations after a recovery. Reported per cell as minimum, median and maximum.
- **R5, release latency after a false alarm.** In H only, per run, the number of steps from
  the shock at 150 to the return to NORMAL, and the count of runs that never return.
- **R6, liveness and auditability,** as C5 and C6 of the drift defense note.

**Sign discipline.** The analysis asserts against a fixture in which the recovered arm is
worse on R1 and R2 that its criterion labels that fixture harm, and prints the result. A
failed assertion halts.

## 6. The selection rule and the gate criterion, fixed now

**Selection.** Adopt the **smallest** `k` in 10, 20, 40 that satisfies both, in both attack
arms M1 and A3:

1. R1 is not worse than LATCHED at a paired t of 2.0 or above in the harm direction, and
2. R2 is not worse than LATCHED at a paired t of 2.0 or above in the harm direction.

If more than one `k` qualifies, the smallest is adopted, because it releases soonest. If
none qualifies, **no recovery rule is adopted**, gate 3 fails, and the record states that
the defense cannot release its grip without losing containment on these attacks. A failure
is not repaired in this note.

**The gate also fails** if the adopted `k` does not reduce R3: in H, the count of runs still
in a non-NORMAL state at the last step must fall below the LATCHED arm's, which is 20 of 20
by construction. A recovery rule that never releases is not a recovery rule.

**Confirmation.** Any adopted `k` is confirmed at 20 fresh seeds declared in a committed
amendment before the rerun, and the adoption stands only if both selection conditions hold
again.

## 7. Stages B and C, declared now

**Stage B, cross-vector re-validation.** The gate 1 design of
`simulation/diagnostics/defense_cross_vector_design_note.md`, unchanged in cells, quantities
and criterion, re-run with the adopted RECOVER-k in place of GRADED, at seeds declared in
the amendment that adopts `k`. Gate 1's harm criterion applies unchanged.

**Stage C, held-out re-validation.** The A3 and A2 arms of the held-out note, unchanged in
attacks, quantities and criterion, re-run with the adopted RECOVER-k, including the
attack-validity gate, at seeds declared in the same amendment.

Until stages B and C complete, items 2g and 2h describe the latching defense only, and the
record says so wherever the recovered defense is discussed.

## 8. Interpretation, fixed now

- A qualifying `k` means recovery cost no measurable containment on two attacks at 20 seeds.
  It does not mean recovery is free, and R3 states what it bought.
- R5 is the number an operator would actually feel: how long the system stays under
  intervention after a shock that turned out to be nothing.
- The known-pathway bias of item 2f and the calibration mismatch of item 2g are restated
  beside every headline number.
- Nothing here licenses promotion, which remains gated on stages B and C and on gate 4.

Any analysis beyond R1 through R6 is labeled exploratory, placed after the registered
results, and may not be cited as a result of this pre-registration.

## 9. Amendment rule and execution bounds

Any change to the recovery rule, the values of `k`, seeds, arms, construction, quantities,
the selection rule or the criterion after this note is committed requires a committed
amendment, pushed before any output is read. Outputs already produced under the unamended
plan are reported under that plan. The executor may not inspect any output to adjust any
element of this note.

At most 15 concurrent workers, numerical-library threads fixed to one and verified per
worker. 300 runs. Writes are restricted to the governed prefix and `os.devnull`. The
manifest follows Section 3 of the artifact convention.
