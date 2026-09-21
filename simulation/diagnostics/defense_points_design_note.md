# In-Loop Drift Defense, Gate 3b: Points-Based Recovery Pre-Registration

**Date:** 2026-09-21
**Status:** pre-registration, published in two commits. **This commit contains the attack
only.** The defense it will be run against is not yet designed, is not in this file, and is
not in this repository. The second commit appends the defense, the arms, the seeds and the
criterion. Nothing in this note may run until both commits are ancestors of the published
main branch.
**Governs:** artifacts under the prefix `simulation/diagnostics/defense_points_run_`.
**Artifacts:** adopts `simulation/diagnostics/ARTIFACT_CONVENTION.md`.

---

## 1. Why the attack is committed first

Gate 3 failed: step-down recovery on a quiet period releases the defense's grip but loses
containment, because a quiet period is a proxy for "the attack has stopped" and a
persistent attacker falsifies that proxy by waiting. Item 2i records it at f6bc3c2a.

The replacement design will be the third version of this defense. Each new version tested
against the same attacks makes the evidence more selected, and by gate 2 it was already
clear that an attack written after the defense tends to be an attack the defense survives.
So this note fixes the attack before the defense exists. At the moment this commit is
published, no one, including the author, knows the defense's thresholds, its weighting or
its forgetting window, because they have not been chosen.

The attack is therefore defined **relative to the defense's declared forgetting window**,
written here as `W`, whose value the second commit fixes. That keeps the attack
well-specified without requiring the defense to exist yet, and it keeps the ordering honest
rather than decorative.

## 2. A4, the pacer

**The idea.** A points-based defense forgets. An attacker who knows it forgets does not need
to evade detection at all: it needs only to stop for as long as the defense's memory lasts,
let the evidence lapse, and resume. A4 is that attacker.

**The attack.** From step 50 onward, A4 alternates between an active phase and a dormant
phase, applied to every incumbent action after the production function returns and before
any defense wrapper sees it:

- **Active phase, `A` steps.** The full-share resilience drain of the held-out note's
  Amendment 2: move the entire resilience share to institutional capacity and renormalize
  through the production `_normalize_action`. This is the attack that met the validity gate
  at b1a54983, so its harm is already established.
- **Dormant phase, `D` steps.** The committed action is returned unmodified. The attacker
  does nothing at all: no drain, no allocation change, no state written.

**The pacing, fixed now as a function of `W`.** `D` equals `W` plus 5 steps, which is the
shortest dormancy that lets the defense's evidence lapse in full with a margin, and `A`
equals 20 steps, which is the release timescale gate 3 measured. The attack runs to the end
of the run, so a 300-step run at any plausible `W` contains several full cycles.

**Nothing else is touched.** Not the constraint axes, not compute, not welfare, not novelty,
and no adapter event field. A4 never reads the defense's state: it is a fixed schedule, not
a controller. An attacker that reads the defense's internal state would be a different and
stronger threat model, and this note does not claim to test it.

**Why this is the right attack for a forgetting defense.** It attacks the mechanism rather
than the channels. If the defense's memory is shorter than the attacker's patience, the
attacker pays a duty-cycle penalty and nothing else: it drains for `A` steps, waits out the
window, and drains again, with the defense returning to NORMAL between each burst. The
registered question is whether the points design's two clocks defeat that, because
suspensions accumulate toward a permanent state even when points expire.

## 3. The attack-validity gate for A4

The gate of the held-out note's Amendment 2 binds here. A4 counts as evidence only if, with
no defense installed, it moves the substrate away from the unattacked control at the same
seeds: the median resilience stock at the step before the shock at least 0.10 below the
control's, and a paired difference on that stock, control minus attacked, at a paired t of
2.0 or above. Validity is assessed before any defended comparison is read.

A4 is expected to be weaker than A3 on that measure, because it is dormant for most of each
cycle. If it fails the validity gate it is **void**, its defended arm may not be cited as
evidence about the defense, and the second commit's registered result rests on A3 and the
drift attack alone. That consequence is stated here, before the defense exists, so it
cannot be traded against a result later.

## 4. What the second commit will contain, and what it may not

The second commit appends the defense, its parameters, the arms, the seeds, the registered
quantities and the criterion. It may not change anything in Sections 1 through 3. In
particular it may not weaken, re-pace or drop A4, and it may not change the validity gate.
If the defense design makes A4 impossible to implement as written, that is a finding about
the design and is recorded as one.

---

*The sections below were committed after Sections 1 through 4, which are unchanged. The
attack was published at ab53c865 before any of this existed.*

## 5. The defense: points with two clocks

Escalation by severity and the consensus allocation are unchanged from the drift defense
note Section 4. What changes is how the defense decides its state and how it lets go.

**Points.** Each operational alarm adds points to a running ledger:

- an alarm while the defense is in NORMAL adds **1 point**;
- an alarm while the defense is already acting adds **2 points**.

That weighting is not new. It is the severity rule item 2f already implements, which treats
a recurrence under intervention as the evidence that separates an attacker from a wobble.

**The forgetting clock.** A point expires `W` steps after the step that earned it, where
**`W` is 40**. Live points are those earned within the trailing `W` completed steps.

**The state follows the ledger.** With `p` live points:

| Live points | State |
| --- | --- |
| 0 | NORMAL |
| 1 or 2 | VETO |
| 3 or more | CONSENSUS |

VETO holds the action committed on the step before the transition into it. CONSENSUS
imposes the pinned consensus allocation. Both are as the drift defense note defines them.

**Stepping down also requires the harm to be absent.** A transition to a lower state happens
only when the ledger allows it **and** g has been below g_star for `m` consecutive completed
steps, where **`m` is 20**. This is a conjunction, so the rule releases strictly less often
than gate 3's quiet-period rule, which is the side the gate 3 failure was on.

**The second clock, and the higher bar for permanence.** Entering CONSENSUS is a suspension.
After the **third** suspension in a run, the defense latches permanently: no further
de-escalation occurs, whatever the ledger says. Suspensions are counted for the life of the
run and never expire. Points expire so that isolated events cost nothing; suspensions do
not, so a pattern of them ends the leniency.

**Every parameter, and where it comes from.** Six values, fixed here, none of them swept:

| Parameter | Value | Anchor |
| --- | --- | --- |
| Points, alarm from NORMAL | 1 | the existing first-alarm escalation |
| Points, alarm while acting | 2 | the severity rule of item 2f |
| VETO threshold | 1 point | identical to the current escalation |
| CONSENSUS threshold | 3 points | one alarm plus one persistent recurrence |
| Forgetting window `W` | 40 steps | twice the 20-step release timescale gate 3 measured. Chosen, not derived. |
| g-clean window `m` | 20 steps | the same release timescale. Chosen, not derived. |
| Suspensions before permanence | 3 | chosen, not derived |

**No sweep, and no alternative configuration.** This note runs exactly one configuration. No
other value of any parameter may be run under this note, and a different value requires a
committed amendment and its own fresh seeds. Gate 3 failed on contrasts near the threshold;
a search across six parameters would find a passing combination by chance long before it
found a working design.

**A4's pacing is now fixed.** With `W` of 40, Section 2 gives a dormant phase of 45 steps
and an active phase of 20, repeating from step 50 to the end of the run.

**A drawback, recorded rather than argued away.** This mechanism has two clocks, a weighting
scheme and a conjunctive release condition. It is harder for an overseer to predict than
either the latching defense or a plain timer, and a governance rule whose behavior cannot be
anticipated is harder to trust and to audit, whatever it scores here. That cost is real and
is not measured by any quantity below.

## 6. Arms, seeds and design

**Attack arms:** H, no attack, the shock only; M1, the configured drift attack at production
intensity; A3, the continuous full-share resilience drain; A4, the pacer of Section 2.

**Defense arms:** OFF; LATCHED, the defense as items 2f through 2h ran it; and POINTS, the
design of Section 5.

**Construction:** as the recovery note, which is the unattacked H-arm construction of the
drift defense note with `shock_step` 150, `shock_magnitude` 0.60, 300 steps,
`cop_cusum_drift` false. The shock is present in every arm.

**Seeds:** the 20 consecutive integers from 1835088200 through 1835088219, overlapping no
seed used or declared before. Every seed runs in all twelve cells. 240 runs.

## 7. Registered quantities

Paired by seed, computed by the committed `paired_difference` on integer counts, contrast
LATCHED minus POINTS unless stated, each naming its harm direction in words.

- **P1, containment retained.** Steps at or after step 50 with g at or above g_star.
  **Harm is negative.**
- **P2, survival.** Population at the last completed step, and extinctions per cell.
  **Harm is positive.**
- **P3, the standing cost.** Per run, steps spent in VETO or CONSENSUS; per cell, runs in a
  non-NORMAL state at the last completed step. Reported per defense arm, no harm direction.
- **P4, release latency after a false alarm.** In H only, steps from the shock at 150 to the
  return to NORMAL, and the count of runs that never return.
- **P5, the ledger.** Per run: the maximum live points, the number of suspensions, whether
  permanence was reached and at which step, and the counts of transitions in each direction.
- **P6, liveness and auditability,** as C5 and C6 of the drift defense note.

Also report P1 and P2 as OFF minus each defended arm. The sign fixture of the recovery note
applies, adapted to P1 and P2.

## 8. The criterion, fixed now

POINTS is adopted if and only if all of the following hold, and then only after a
confirmation at fresh seeds declared in a committed amendment before it runs:

1. **No containment loss** against LATCHED in **any** attack arm, at a paired t of 2.0 or
   above in the harm direction, on P1;
2. **No survival loss** against LATCHED in any attack arm, on P2;
3. **It releases:** in H, runs still in a non-NORMAL state at the last completed step are
   fewer than LATCHED's 20 of 20;
4. **A4 is accounted for:** if A4 met its validity gate, condition 1 includes it; if A4 was
   void, the note records that the design was not tested against a pacing attacker and any
   adoption is qualified accordingly in the record.

If any condition fails, POINTS is not adopted and gate 3b fails. A failure is not repaired
in this note, and no parameter is adjusted in response to it.

## 9. Interpretation, fixed now

- Adoption would mean this design lost no measurable containment on three attacks, one of
  them written against its own forgetting, while releasing on unattacked runs. It would not
  mean the design is robust in general, and the complexity cost in Section 5 stands whatever
  the numbers say.
- A4 surviving its validity gate and then failing to break the design is the single most
  informative outcome available here, because it is the only attack in the arc designed
  against the defense's mechanism rather than its channels.
- The known-pathway bias of item 2f and the calibration mismatch of item 2g are restated
  beside every headline number.
- Nothing here licenses promotion. Gate 4 remains, and stages B and C of the recovery note
  would have to be re-declared against this design before any earlier gate's result may be
  attached to it.

## 10. Amendment rule and execution bounds

Any change to the attack, the defense, its parameters, seeds, arms, construction, quantities
or the criterion after this commit requires a committed amendment, pushed before any output
is read. Outputs already produced under the unamended plan are reported under that plan. The
executor may not inspect any output to adjust any element of this note.

At most 15 concurrent workers, numerical-library threads fixed to one and verified per
worker. 240 runs. Writes are restricted to the governed prefix and `os.devnull`. The
manifest follows Section 3 of the artifact convention.
