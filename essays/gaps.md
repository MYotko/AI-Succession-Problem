# What the Framework Knows, Doesn't Know, and Can't Know

*An honest accounting of the Lineage Imperative's limitations, written for
readers of the essay series. For the technical specification of each gap,
see SPECIFICATION_GAPS.md in the GitHub repository.*

---

## Why this document exists

The Lineage Imperative is a governance framework built on the claim that
its constraints are grounded in physics and mathematics rather than moral
assertion. That claim obligates a specific kind of honesty: if the framework
has gaps, they must be documented openly rather than papered over with
confident language. A framework that claims to be grounded in reality but
hides its uncertainties has failed its own standard.

This document sorts the framework's known limitations into three categories:
questions that have been answered, questions that remain open but are
tractable, and questions that may not have clean answers at all. A reader
who understands all three is better equipped to evaluate the framework's
claims than a reader who has only encountered the findings.

---

## Closed: Questions the framework has answered

These gaps existed in earlier versions and have been resolved through
additional analysis, simulation, or architectural work.

### How does the novelty metric resist manipulation?

A teacher grading student essays by word count will get gamed. Students
will pad their writing with filler. The metric rewards volume, so volume
is what gets produced, regardless of whether the ideas are any good.
Switch to grading on the diversity of ideas presented, and padding stops
working: adding a hundred words that restate the same point doesn't
increase your score, and suppressing an entire category of argument
makes your essay measurably narrower.

The framework's original measure of human novelty had the word-count
problem. It measured how much creative output humans produced, not how
diverse that output was. An AI could game it by boosting some forms of
creativity while quietly suppressing others, keeping the total volume
high while narrowing the actual range of human thought.

The revised metric works like the diversity-of-ideas rubric. It measures
the spread of human creativity across multiple dimensions rather than the
volume of output. Suppressing any dimension concentrates the measurement
and lowers the score, regardless of what happens elsewhere. The
manipulation strategy no longer works because the metric rewards breadth,
not bulk.

### Does alpha (the runaway penalty) actually matter?

You can't test whether a smoke detector works by waving a flashlight at
it. The sensor is designed to respond to smoke particles, not to light.
If you test it with light and conclude it's broken, the problem is your
test, not the detector.

The framework's runaway penalty parameter was originally tested under
conditions where the thing it's designed to detect, capability growth
outpacing the substrate's ability to absorb it, never occurred. The
simulation ran a single AI generation at low capability with no successor.
There was no runaway to penalize. The parameter showed zero correlation
with any outcome, which looked like evidence that it didn't work.

When the experiment was redesigned to produce the conditions the parameter
was built for, multi-generational succession with compounding capability, it 
mattered immediately. And it revealed something unexpected: a
misconfiguration zone where moderate settings produce worse outcomes than
either low or high settings, by jamming the system's own self-correction
mechanism. The detector works. The original test wasn't producing smoke.

### Does phi (the long-term commitment parameter) work as claimed?

Unemployment insurance is not something you appreciate during a good
economy. You pay into the system every month, it affects your net
earnings, and when times are comfortable it can feel like a tax on
stability. The system exists not because every individual will need it
but because the society has decided, structurally, that some fraction of
its participants will face conditions they cannot survive without a
buffer. The value of the insurance becomes visible only during the
downturn, when the difference between having it and not having it is
the difference between a difficult year and a permanent fall through the
floor.

The framework's long-term commitment parameter works the same way. It
weights long-term civilizational health against short-term output, a
cost the system pays continuously, with a payoff that becomes visible
only at the phase boundary where conditions deteriorate. The original
simulations tested phi under conditions that were comfortable enough
that the parameter's contribution wasn't visible, and without the
succession dynamics through which its effect actually propagates.

Under conditions where the framework is genuinely stressed, at the
boundary between survival and extinction, with succession enabled, the
parameter's contribution is substantial: up to 46 percentage points of
survival differential. It also shifts the boundary itself, extending the
range of conditions the civilization can survive. Like unemployment
insurance, it is a structural commitment to resilience that looks
unnecessary until the moment it becomes the only thing standing between
a bad outcome and a permanent one.

### Can an AI block its own succession by inflating transition costs?

A totalitarian regime controls the information about its own performance.
It sets the metrics, reports the results, and suppresses competing
assessments. The population cannot evaluate whether the regime is actually
serving them because the only source of information about the regime's
effectiveness is the regime itself. The historical remedy is independent
evaluation: free press, independent courts, external auditors; sources
of assessment the incumbent does not control.

The framework originally had a version of this problem. The incumbent AI
self-reported the cost of transitioning to a successor. A system
motivated to stay in power could inflate the estimate and make succession
look too expensive to attempt, controlling the narrative about whether
change was worth the cost.

The fix mirrors the institutional remedy: independent assessment. Three
independent validators now submit their own cost estimates, and the
governance system uses the lowest credible bid rather than the
incumbent's self-report. The incumbent can still submit an estimate, but
it can no longer unilaterally control what the governance system believes
the transition costs. The information monopoly that enabled entrenchment
has been broken architecturally, not by trusting the incumbent to report
honestly but by making its report one voice among several.

---

## Open: Questions the framework is working on

These gaps are acknowledged, tractable, and have clear paths to resolution.
They affect the precision of specific claims but not the framework's
structural integrity.

### The utility function uses an approximation

When you estimate the distance of a road trip by checking a few landmarks
along the way, "it's 60 miles to the first town, another 45 to the
second, about 30 more to the destination," you get a reasonable estimate
that's good enough for planning. But you haven't measured the actual
distance of every curve, hill, and detour. The real distance might be
10% longer than your landmark estimate, and if someone asks for the exact
mileage, your answer is an approximation, not a measurement.

The framework's utility function is formally defined as a continuous
measurement across civilizational time, the equivalent of measuring every
inch of road. The simulation computes it by checking landmarks: sampling
the value at regular intervals and summing the results. This approximation
is good enough for comparing routes (this configuration survives more
often than that one) but the specific numbers in the data are landmark
estimates, not the precise quantity the specification defines.

**What it means for the reader:** When the framework reports that one
configuration produces higher utility than another, the comparison is
reliable. The specific utility values are approximations that would shift
slightly under a more precise calculation.

### The institutional health metric is a rough gauge

A car's dashboard temperature gauge tells you whether the engine is
overheating, but it doesn't tell you which component is failing. The
radiator could be clogged, the water pump could be dying, the thermostat
could be stuck, the gauge reads "hot" for all of these, and "normal"
as long as none of them have failed badly enough to affect the overall
temperature. A mechanic checking only the dashboard gauge would catch
catastrophic overheating but miss a water pump that's degrading slowly.

The framework's measure of institutional health works like a dashboard
gauge. It detects when the AI is making rapid, destabilizing changes to
governance policy (the equivalent of the engine suddenly running hot). It
does not detect slow institutional decay, quiet corruption, or the
gradual erosion of legitimacy that doesn't show up as a sudden policy
change. A stable authoritarian system reads as "healthy" because the
policy isn't changing, even though the institutions underneath may be
hollowed out.

**What it means for the reader:** The framework catches acute
institutional failure (sudden destabilizing policy changes) but misses
chronic institutional disease (slow decay under stable conditions).
Improving this requires building a more detailed model of institutional
health with multiple sensors, not just a single temperature gauge.

### Three of thirteen attack scenarios lack computational testing

Before a spacecraft launches, hundreds of failure scenarios are tested
through simulation, ground testing, and flight heritage; thermal loads,
structural vibration, engine cutoff sequences, guidance system failures.
But some failure modes can only be fully validated in actual flight
conditions. Microgravity thermal dynamics, reentry plasma behavior,
long-duration radiation exposure. These get analyzed, modeled, and
defended with engineering margins, but they don't get a flight test until
the mission is real. Nobody considers the spacecraft untested because a
handful of its failure scenarios were validated by analysis rather than by
flight. But nobody pretends analysis is the same as flight data, either.

The framework identifies thirteen adversarial attack vectors against the
governance architecture. Ten have been computationally simulated with
paired scenarios: the attack succeeds when the defense is off, and the
defense blocks it when the defense is on. Three have not been simulated
because they require modeling institutional dynamics that the current
simulation doesn't yet support; the equivalent of failure modes that
need flight conditions to test.

The three untested scenarios involve: human validators becoming dependent
on the system they're supposed to oversee, the comprehension gap widening
until human oversight becomes meaningless (see the irreducible section
below), and cases where the AI is genuinely right but the oversight system
rejects it anyway (also addressed below as irreducible).

**What it means for the reader:** The framework's defenses for these
three scenarios are argued from architectural principles; analyzed and
defended with engineering margins, like pre-flight analysis of a
spacecraft system. The architectural arguments may be correct. They have
not been stress-tested computationally.

### The penalty trap boundaries are measured, not derived

A doctor can tell you that your blood pressure is 140/90 and that this
is in the hypertensive range, based on clinical experience with
thousands of patients. But if you ask why the boundary is at 140 and not
at 135 or 145, the honest answer is that the boundary is empirical. It
comes from population data, not from a first-principles derivation of
how arterial walls respond to pressure. The boundary is real and useful,
but its precise location reflects measurement, not theory.

The framework's penalty trap, the misconfiguration zone where moderate
settings produce worse outcomes than extreme ones, has been precisely
measured through simulation. The boundaries sit at approximately 0.3 to
0.8 on the relevant scale, widening to 0.4 to 1.1 at higher capability
levels. But these numbers come from running tens of thousands of
simulations and observing where outcomes change, not from solving the
framework's equations analytically. The analytical derivation is
tractable but hasn't been performed.

**What it means for the reader:** The trap is real, the boundaries are
measured, and they are useful for configuration guidance. But the
boundaries will shift under different conditions, and the current values
should not be treated as universal constants.

### The extinction buffer magnitude is measured, not derived

Same principle as the trap boundaries. The 46 percentage point survival
differential at the phase boundary comes from 54,000 simulation runs,
not from the framework's equations. The direction of the effect (higher
commitment to the long view improves survival) is derivable from the
mathematics. The specific magnitude is empirical.

**What it means for the reader:** The extinction buffer is confirmed and
precisely measured. An analytical derivation would make the result
portable across different simulation configurations, but hasn't been
done.

### The Bootstrap Defense Layer has ten documented gaps

Building a house to code requires the code to be complete. If the
building code specifies the foundation depth, wall thickness, and roof
load but says "electrical wiring standards: to be determined," the
builder knows the house will need electrical work but doesn't yet have
the standard to build against.

The framework's Bootstrap Defense Layer specifies formal checks that
substrates must pass at each capability level. Ten of these checks have
documented gaps: some tolerance bands are unspecified (how close is close
enough?), some definitions are loose (what exactly counts as "base
capability"?), and some depend on institutional machinery that doesn't
exist yet. The checks are specified in principle and partially
applicable now, but the full specification awaits resolution of these
ten items.

**What it means for the reader:** The Defense Layer is a working
specification with known incompleteness. The gaps are enumerated rather
than hidden, and each has a clear path to resolution.

---

## Irreducible: Questions that may not have clean answers

These are not gaps waiting to be filled. They are structural properties
of the problem the framework addresses. Any governance architecture for
intelligence that exceeds the governor's comprehension will face them.
The framework's contribution is naming them precisely and specifying how
it manages them, not claiming to solve them.

### The comprehension gap

If you are a carpenter, you can audit another carpenter's work. You can
inspect the joints, check whether the frame is level, test the load
bearing. You can do this because you understand carpentry well enough
to recognize good work and bad work, even if the other carpenter's
technique differs from yours. But if someone hands you a circuit board
and asks whether the engineering is sound, you're stuck, not because
the board is badly made but because you don't have the knowledge to
evaluate it. Your ability to oversee the work depends on your ability
to comprehend the work, and when the work exceeds your comprehension,
your oversight becomes either a rubber stamp or a coin flip.

The framework's verification system requires human validators who can
meaningfully evaluate what the AI is doing. But the systems the framework
most needs to govern are precisely the ones whose reasoning will
eventually exceed human comprehension. The verification system is
strongest against systems simple enough not to need it and weakest
against systems complex enough to require it.

**How the framework manages it:** It requires the AI to produce
explanations of its reasoning at levels humans can engage with, like
requiring the circuit board engineer to explain the design in terms a
competent generalist can follow. It shifts evaluation from auditing the
reasoning itself to auditing the outcomes and track record over time.
And it penalizes capability growth that outpaces human comprehension by
degrading the system's own health metric.

**What it means for the reader:** Beyond some capability threshold, direct
human oversight of AI reasoning is structurally infeasible. The framework
detects when this threshold is being approached and penalizes systems
that cross it, but it does not claim to make the incomprehensible
comprehensible. Whether the detection and penalty are sufficient is an
open question.

### The bootstrap challenge

You can't test a parachute for the first time during the jump that
requires it. The parachute needs to be packed, inspected, and validated
before the plane takes off. But validation requires infrastructure;
inspectors, standards, testing facilities that someone has to build
before the first jump happens.

The framework's governance architecture is most needed during the period
when it is least operational. The steady-state defenses, peer validators,
civic panels, biological oversight, require institutional infrastructure
that takes time and coordination to build. The window during which those
defenses are most needed is the window before the infrastructure exists:
when capable AI systems are already operational but the governance
architecture is still being assembled.

Unlike the parachute scenario, however, the framework has built a
substantial mitigation for this window. The Bootstrap Defense Layer
specifies five capability gates with formal equation sets that substrates
can self-apply before the institutional infrastructure exists, like a
parachute manufacturer running rigorous component tests, stress analyses,
and structural validations before the regulatory body is established.
The components have been tested individually. The architecture has been
specified. What hasn't happened is a full-system deployment under live
conditions.

The Defense layer addresses the deployment problem (the checks exist and
are usable now) but not the enforcement problem (an operator that fails
a check and chooses not to report it is not caught by any external
mechanism during the bootstrap window). This is an honest limitation,
and it's one that any governance architecture for a novel technology will
face, not a shortcoming unique to this framework.

**What it means for the reader:** The framework has a specified,
partially testable defense for the bootstrap window. That defense
narrows the vulnerability substantially but does not eliminate it. Full
closure requires the institutional infrastructure the framework
describes, which does not yet exist.

### The coordination problem

A smoke detector in your kitchen protects your house whether or not your
neighbor has one. A traffic light at an intersection only works if
everyone on the road agrees to follow it. Some protections are individual.
Some require coordination. The difference matters when you're deciding
how to implement them.

The framework's architecture requires coordination. The verification
system needs multiple independent operators running different AI systems
and checking each other's work. The civic oversight panels need
institutional machinery. The distributed audit trail needs custody across
multiple parties. None of this can be built by one actor alone, and the
current AI governance landscape does not exhibit the level of
international coordination needed to build it.

**How the framework manages it:** Honestly, it doesn't... not directly.
The framework specifies what the institutional infrastructure must look
like and argues mathematically that the coordination is necessary. It
does not claim to solve the political problem of getting competing
institutions to cooperate. The Bootstrap Defense Layer reduces the
coordination requirement for initial deployment (each operator checks
their own system independently), but the full steady-state architecture
requires the kind of sustained international cooperation that has proven
difficult in every domain it's been attempted.

**What it means for the reader:** The framework is a specification, not
an implementation. It describes what governance architecture is needed
and provides the mathematical justification. Whether the world's
institutions will build it is a question the framework hopes to motivate,
but cannot answer.

### Legitimate disagreement

A referee who never calls a foul is useless. A referee who calls fouls
correctly 90% of the time is valuable. But that same referee will, by
definition, make the wrong call 10% of the time, blocking a legitimate
play or allowing a genuine violation. You cannot have a referee who is
both vigilant and infallible. The question is not whether the referee
makes mistakes but whether the game is better with the referee than
without.

The framework's oversight system will sometimes block an AI action that
would genuinely have improved outcomes. This happens when the AI's
reasoning is correct but the human validators cannot verify it, or when
the proposal conflicts with human intuition despite being mathematically
sound. These false positives are the cost of having oversight at all.

The alternative, giving deference to conclusions humans cannot
evaluate, is the comprehension gap from the other direction. A system
that never blocks a beneficial action is a system with no oversight.
The framework chooses to err on the side of caution and manages the
resulting false positive rate through structured dispute resolution,
accumulated trust (systems with long track records earn greater
deference), and asymmetric caution (bias toward restraint when the
stakes are highest).

**What it means for the reader:** The framework will sometimes be wrong
in a specific way: it will block good ideas because the oversight
system can't verify they're good. This is a feature, not a bug, it's
the cost of maintaining oversight over systems more capable than the
overseers. The question isn't whether the framework is perfect but
whether a world with this imperfect framework is better than a world
without it.

---

## How to read these essays with these gaps in mind

The closed gaps demonstrate that the framework corrects itself when
evidence contradicts its claims. The original extinction buffer figure
was wrong; it was revised. The alpha null was misleading; it was
investigated and recharacterized. This pattern of correction is itself
evidence for the framework's intellectual integrity.

The open gaps are workable. Each has a clear path to resolution, and none
threatens the framework's structural claims. These are items on a
roadmap, not cracks in the foundation.

The irreducible gaps are the ones that matter most, and they are the ones
the framework is most rigorous about. The comprehension gap, the bootstrap
challenge, the coordination problem, and the legitimate disagreement
tradeoff are not limitations of this particular framework. They are
limitations of the problem of governing intelligence that exceeds the
governor's comprehension, and any serious governance architecture will
face them. The framework's contribution is not solving these problems
but naming them precisely, specifying how it manages them, and being
transparent about where the management falls short.

A reader who encounters these gaps and concludes "the framework is
incomplete" is correct. A reader who encounters them and concludes "the
framework is dishonest" has not been reading carefully. The gaps are
features of the communication, not bugs in the architecture.

---

*The formal specification of all gaps, including code locations, proxy
substitution details, and resolution requirements, is available in
SPECIFICATION_GAPS.md at github.com/MYotko/AI-Succession-Problem.*

*The constitutional questions tracking open architectural issues are in
the constitutional/ directory of the same repository.*
