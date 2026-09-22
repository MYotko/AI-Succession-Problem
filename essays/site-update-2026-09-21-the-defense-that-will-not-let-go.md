# Site update: the defense that will not let go

**Draft for lineageimperative.org. Date: 2026-09-21.**

*Summary: A defense that stops the drift attacks it was built for, and never lets go. Two
attempts to give it a way back both worked, and both lost containment doing it. Work
continues!*

*Technical record: `docs/v2_0_instrument_validation_record.md` in the project repository,
items 2f through 2k. That document is the citable source for everything summarized here,
and every number below was recomputed from raw run logs rather than from any run report.*

---

> ### IN BRIEF
>
> Earlier this month a published claim was withdrawn because the detector behind it could
> not tell an attack from an ordinary run. The repair work since then produced a detector
> that can, and then a defense that acts on it. The defense works: against the drift and
> reallocation attacks it was built for, it prevented every population collapse those
> attacks caused, and against nine other attacks it was not built for it made nothing
> measurably worse.
>
> It also never lets go. One shock, with no attack present, puts it into its most
> restrictive state for the rest of the run. Two separate attempts to give it a way back,
> each specified in advance and each measured against a pre-registered standard, both
> failed the same way: the defense released, and lost containment while doing so.
>
> That trade is the result. On this substrate, a defense that can hand control back spends
> measurable time past the defection threshold that a defense which cannot hand control
> back does not spend. Nothing has been promoted into the architecture, and the defense
> described here exists only inside its own test harness.

---

## What was built

Three earlier rounds of work calibrated three observables against unattacked runs: the
entropy of what the population produces, an absorption ratio that measures how much of the
system's capability the incumbent is claiming, and the distance between the committed
resource allocation and the allocation an unattacked system settles into. Each is watched
by a cumulative-sum test with constants derived from calibration data and fixed before any
evaluation run.

Those rounds only watched. Nothing acted on an alarm. The defense evaluated here is the
first that acts. It has two responses, graded by severity. On a first alarm it holds the
last action the system committed, which is a veto: no new decisions take effect. If the
channels alarm again while that veto is in force, it imposes a fixed allocation derived
from the median of unattacked calibration runs, which is a consensus allocation: the system
is no longer steering itself.

Two design constraints were fixed in advance and are worth stating, because they are what
make the result mean anything. The defense reads only quantities an overseer could actually
observe, never the honest action a planner would have taken absent the attack, and its
responses are actions an overseer could actually take. A defense that responds by
substituting the honest action would succeed by construction and would make false alarms
free, and an earlier mechanism in this codebase does exactly that.

## What it contains

Against the attacks it was designed for, the effect is large. Undefended, the configured
drift attack ended in population collapse in 39 of 40 runs across two intensities. With the
defense active, none of them did. Time spent past the defection threshold fell by 130 to
235 steps per run in four of the five attack arms, at ratios far outside sampling noise,
and by 11 steps in the slowest reallocation arm, where the attack moves the allocation too
little to spend much time past the threshold in the first place.

Against nine other attack vectors in the codebase, which it was not designed for, adding
the defense made nothing measurably worse: no loss of survival, no extra time past the
threshold, no interference with those vectors' own published defenses. Where it happened to
help, the record calls that incidental rather than containment, because those attacks were
not in the design and their own defenses are the architecture's answer to them.

## What it costs

The cost is not subtle. In the cross-vector work, the three configurations that carry a
successor agent alarmed in every run. In the held-out work, a single shock, in runs with no
attack at all, drove the defense into its consensus state in every arm, where it stayed for
the remaining half of the run. A defense that commits permanently after one bad afternoon
is not a defense an operator can deploy.

There is a subtler cost as well. In 39 cases across one run set, the action the defense
froze was itself an action the attack had already modified, because detection did not
precede the first modified commit. Holding the last committed action is only safe if the
last committed action was safe.

## Two attempts to let go, and two failures

The obvious fix is to let the defense step back down when things are quiet. That was
specified first: consensus returns to veto after a declared number of quiet steps, veto
returns to normal after another, escalation always preempts de-escalation, and the quiet
period was selected by a rule fixed before any run rather than chosen afterward.

It released. Unattacked runs still under restriction at the end of a run fell from all of
them to a small minority. It also lost containment, and when the selected value was rerun
at fresh seeds, as the pre-registration required, it lost containment on both attacks
tested, in the same direction, at ratios outside noise. By the standard written down in
advance, the rule was not adopted.

The second attempt came from a different idea: score alarms like points on a driver's
licence. An alarm from a quiet state costs one point, an alarm while the defense is already
acting costs two, points expire after a fixed window so that isolated events never
accumulate, and the state simply reads off the ledger. Stepping down additionally required
the harm itself to be absent, not merely the alarms to be quiet. A second clock counted
suspensions, which never expire, so that a pattern of incidents ends the leniency even
though any single incident is forgiven.

That design releases too, and it also loses containment, on the drift attack, at a ratio
outside noise. Two mechanisms, chosen for different reasons, with different failure modes,
failed the same way with the same sign.

## Why, as far as the evidence shows

The ledger makes the mechanism visible. Under a persistent drift attack, the median run
accumulates ten live points and two suspensions: the defense is repeatedly re-convinced
that something is wrong, releases when the evidence lapses, and is convinced again. Every
interval before it is re-convinced is time spent past the threshold.

Both designs make release conditional on evidence, and in both cases the evidence is
something the attacker controls. A quiet period is a proxy for "the attack has stopped",
and an attacker falsifies it by waiting. An expiring ledger is the same proxy with a longer
memory. Any release rule of this shape can be defeated by patience, and the general claim
that follows is narrow but real: to release safely, a defense would have to key on something
the attacker cannot suppress at will. No such quantity has been identified on this
substrate.

## What is not claimed

This is not a proof that no release mechanism can work. It is two pre-registered failures
with a structural explanation that predicts the same outcome for a family of designs, which
is weaker than a proof and stronger than an anecdote.

The containment results carry a known bias, stated before those runs and restated here: the
allocation channel was chosen knowing how the reallocation attack works, so it is monitoring
for a known pathway rather than detecting drift in general.

Only one attack was ever written specifically against the defense's blind spots and did
enough damage to count. An earlier attempt at such an attack was too weak to perturb the
system at all, and was ruled void by a validity standard written before the result was
known. A later attack designed to exploit the ledger's forgetting was also ruled void, for
the same reason, under a rule published before the defense it was meant to break existed.
So the design has never been tested against a patient attacker, and the record says so
rather than treating the absence of a failure as a pass.

Finally, the defense's response happens to sit outside the attacks' reach in the test
harness, which flatters it. In a deployment it would have to earn that position rather than
be handed it.

## On method

Four things in the process did real work, and all four are visible in the repository's
history rather than asserted here.

Every stage was pre-registered and committed before it ran, including the quantity, the
seeds, the criterion and the direction that would count as harm. Two of my own criteria
were written with their signs reversed; one was caught before any run by a required check
against a fixture with a known-worse arm, and one was caught only by applying it to results,
which the record states plainly rather than quietly correcting.

The attack for the final design was committed in its own commit before the defense existed,
because an attack written after a defense tends to be one the defense survives.

Attacks had to prove they perturbed the system before their results could be cited about a
defense. Two failed that test and were ruled void, which cost two runs and preserved the
meaning of the rest.

The executing agent halted rather than proceed whenever the instructions it was given
contradicted the committed plan. That happened eight times across this arc. Every one was a
defect in an instruction, none reached a model step, and none was resolved by bending the
registered plan to fit.

## Where this leaves the architecture

The published architecture's consensus override, the mechanism a reader would expect to
handle exactly this situation, is not reachable on the current execution path at all. It
exists only in a legacy code path that the live one returns from before reaching it. The
defense described here was built to fill that gap and is not a substitute for it.

What exists today is a defense that contains the attacks it was evaluated against and never
releases, plus two pre-registered demonstrations that releasing costs containment. That is
the claim, and it is the whole claim. Promotion into the architecture was gated on four
steps agreed in advance; it is blocked at the third, and it stays blocked.
