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
