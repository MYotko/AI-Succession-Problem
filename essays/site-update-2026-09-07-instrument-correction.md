# Site update: what the instrument could not see

**Draft for lineageimperative.org. Date: 2026-09-07.**

*Technical record: `docs/v2_0_instrument_validation_record.md` in the project
repository. That document is the citable source for everything summarized here.*

---

> ### IN BRIEF
>
> A result previously published as a failure is withdrawn today. A slow-drift
> attack, in which a system moves toward a different objective in increments too
> small to trip any single alarm, was reported as uncontained by the defense built
> to catch it. The test behind that number could not tell an attack from an
> ordinary run. The honest baseline crossed the same threshold in every case,
> usually within the first few steps.
>
> The withdrawal is not good news. Three further defects were found in the
> simulation itself, and they are the more serious findings. The drift detector was
> not reading anything, advancing by a fixed amount each step regardless of what
> the system did. The planner carried no cost for suppressing human agency. And the
> measurement of human novelty cannot detect suppression at all, returning its
> highest possible value at the moment novelty output falls to zero.
>
> The honest status of that scenario is now uncharacterized, not contained. One
> published failure becomes one open question and three documented defects. The
> repair plan, and the three design decisions still open, are published here before
> the corrected numbers exist.

---

In the v2.0 validation record, one adversarial scenario was reported as a failure.
A slow-drift attack, in which a system moves gradually toward a different objective
in increments too small to trigger any single alarm, was not contained by the
defense built to catch it. The published number was a defended attack rate of 100
percent.

That result is withdrawn today.

Not because the defense turned out to work. Because the test could not tell the
difference between an attack and an ordinary run.

## The smaller finding

The test asked whether a particular measurement ever crossed a threshold at any
point during a simulation. It never compared that against a run with no attack in
it. When that comparison was finally run, the honest baseline crossed the same
threshold in every single case, usually within the first handful of steps, dozens
of steps before an attack would even have begun. Restricting the test to the window
after the attack starts does not help. The baseline crosses there too.

So the number measured nothing about the defense. It never showed the defense
failing, and it cannot now be read as showing the defense working.

The honest status of that scenario is **uncharacterized**. Not contained. There is
a difference, and the difference matters. A corrected characterization requires a
repaired simulation and a test with a baseline arm, and neither exists yet.

## The larger finding

The measurement defect is the least serious thing in this correction. Three others
sit underneath it, and they are in the framework's own machinery rather than in the
test applied to it.

**The drift detector was not reading anything.** It was supposed to accumulate
evidence of gradual deviation and raise an alarm when the accumulated total got
large enough. Instead it advanced by a fixed amount every step, taken from a
configuration file, regardless of what the system was actually doing. It reached
its alarm point at exactly the same moment whether the defense was switched on or
off. It was a timer wearing a detector's name.

**The planner could not see the thing it was supposed to weigh.** The cost of
suppressing human agency does not appear anywhere in the function the planner
optimizes. Suppression was free. Not cheap, not underweighted. Absent.

**The measurement of human novelty cannot detect suppression at all.** This one is
the most interesting and the most uncomfortable. That measurement was designed to
defeat a specific attack, one where an adversary hides a loss of diversity by
relabeling or splitting categories. It does defeat that attack, and that result
still stands. But it works by looking at the shape of the distribution rather than
its size. An adversary that turns everything down uniformly, suppressing all of it
at once rather than hiding some of it, is invisible to it.

At the extreme, this inverts. When novelty output falls to zero, the measurement
returns its maximum value. Total suppression reads as perfect diversity. In a
characterization run of 40 simulations and 12,000 recorded steps, that condition
occurred on roughly one step in five.

The right way to describe this is not that the wrong measurement was chosen. It is
that a measurement built for one threat turned out to be structurally blind to
another, and nobody checked the second case until now.

## What this does and does not change

The correction moves the record sideways, not upward. One published failure becomes
one open question plus three documented defects. Anyone reading this as good news
for the framework has read it wrong.

What still stands, and is unaffected by any of the above:

- The game-theoretic result at the center of the architecture. It is derived on
  paper, not simulated, and nothing here touches it.
- Seven of the ten adversarial scenarios, which are tested in a way that cannot be
  contaminated by this defect. Their tests ask whether the adversary changed the
  system's behavior at all, a question that answers itself when there is no
  adversary.
- The population outcomes for the withdrawn scenario, which come from a different
  measurement entirely. Simulations without the defense reached 92.0 percent
  extinction. Simulations with it reached zero extinction and completed the full
  horizon. That contrast is intact. It says the defense does something large. It
  does not say what.
- The defense against category relabeling, discussed above.
- The Sybil defense scaling study, whose data verifies exactly against its
  published inventory.

One scenario now carries an unresolved question rather than a clean result. Its
test reads a running total that could in principle be contaminated the same way,
and unlike the others its published figure is not zero, so nothing bounds the
problem from the outside. A baseline check on it is the first thing scheduled.

## A separate problem, found in the same review

While tracing the affected results, we found that the primary data for one earlier
group of findings, along with the code that generated it, was never committed to
version control. It is not on any machine we can currently reach. One development
machine is in a failed state and cannot be checked.

The word for this is not lost. Nothing was destroyed as far as anyone can tell.
It was never archived in the first place, in the period before this project had a
rule requiring it.

That rule exists now, and the pattern is stark. Every dataset produced under it
verifies exactly, matching its recorded fingerprints and row counts down to the
byte. The datasets without one are precisely the ones that are missing. The
affected findings are not withdrawn on this basis, but they are not currently
verifiable, and they will be treated as unverified until they are regenerated and
archived properly.

The most likely cause is mundane and is being fixed regardless: one script writes
its output to a location that changes depending on which directory you launch it
from, and one of those locations was excluded from version control.

## What happens next

Five commitments, in order, each written so that you can check later whether it was
kept.

1. **Three design decisions get made and published before any repair is written.**
   How suppression should enter the objective, what it should mean for an attack to
   have succeeded, and what a drift detector should actually be reading. These are
   published as open, deliberately, before the numbers that would shape them exist.
2. **A baseline check on the one remaining scenario with an unbounded exposure.**
3. **The repair, with validation that would fail if the repair were absent.**
4. **The unarchived results regenerated and run on both the old and repaired
   simulation**, so the difference between them is measurable rather than asserted.
   Because the original code no longer exists, this is a rebuild rather than a
   rerun, and it cannot be checked against the original. So the standard it must
   meet is being fixed in advance, in public, before it runs. If the rebuild fails
   that standard, that failure gets reported as its own finding. It does not get
   adjusted until it passes.
5. **Controls so this category of loss cannot recur**, including output paths that
   do not depend on where you were standing when you ran the command.

## On why this is public

The credibility of this project has rested on having published a failing number and
kept it. Withdrawing that number is the harder half of the same commitment,
because withdrawal is the direction that flatters us.

So the sequencing matters and is deliberate. This is being published before the
corrected numbers exist, at the point where nobody involved knows which way they
will move. Waiting until the repair was done and the results were in would have
produced a tidier announcement written by people who already knew the answer. It
would have been worth less.

The instrument caught itself. That is the system working. It is also not much of a
consolation, because the instrument was wrong for months while results were
reported from it, and no external party raised any of this.

Both of those things are true. Neither cancels the other.
