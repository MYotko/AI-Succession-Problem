# Site update: under pressure, and what held

**Draft for lineageimperative.org. Date: 2026-09-25.**

*Summary: The framework asked to be broken, and this month it was, by me and by others, in
specific places. Its core held. The rebuild, v3, starts now, on proven foundations.*

*Technical record: `docs/v2_0_instrument_validation_record.md` in the project repository.
Its update of 2026-09-25 is the summary of record. The full proofs, audit and numerical
checks will be published with v3.*

---

> ### IN BRIEF
>
> The framework has spent the past weeks under deliberate pressure:
>
> - a detailed outside critique;
> - two independent derivations of its game theory, done blind;
> - research sweeps told to report where it fails as well as where it holds;
> - a line-by-line audit of its mathematics.
>
> Several load-bearing claims did not survive:
>
> - The central equilibrium is not unique.
> - The system objective, as written, cannot compare two futures in which humanity survives.
> - The penalty for exploitation is conditional.
> - Several protocol equations are defective.
>
> The core did survive. Cooperation between human and synthetic intelligence is an
> equilibrium both sides prefer. For a patient enough system facing an engaged humanity, it
> holds with no threat behind it. The rebuild, v3, starts from there, and every mathematical
> tool will be proven before anything is built with it.

## What did not survive

**Uniqueness.** The paper claimed that mutual cultivation is the unique equilibrium of the
human-AI game. It is not. If people have withdrawn, a system loses nothing by exploiting.
If a system is exploiting, people gain nothing by engaging. Neither side gains by moving
alone, so mutual defection holds itself in place too. Two derivations, done independently
and without sight of each other, reached the same conclusion. The game does not choose
between the two outcomes.

**The objective.** The quantity the framework asks a system to maximize has three
independent defects:

- As written, it grows without bound for any future in which humanity survives, so it
  cannot rank two good futures.
- Its weighting of scarce resources cancels itself out, both on paper and in the
  simulation.
- Its protection of the lineage fades exactly as the lineage approaches collapse.

These are not small errors. The objective will be redefined.

**The collapse penalty.** The argument that exploiting humanity starves a system of the
novelty it runs on assumed that training on its own outputs must degrade it. Later work
shows this can be avoided by accumulating data rather than replacing it. The cost of
exploitation is real, but it has to be measured against the best alternative a system has,
not against a pipeline that is assumed to fail.

**Protocol equations.** The audit found defects in the consensus protocol's mathematics.
They include an emergency condition that no vote can ever satisfy, and a resilience measure
that rewards larger losses. These are specification errors, and they have specific repairs.

**A stale statement.** The paper still described the drift defense as uncontained. An
earlier correction had already withdrawn the metric behind that statement. Its status is
uncharacterized: neither shown contained nor shown uncontained.

## What held

- **Cooperation is an equilibrium, and the one both sides prefer.** Once both sides are in
  it, neither gains by leaving, and both are better off than under mutual defection.
- **A patient system facing an engaged humanity cultivates it as its own best move.** Model
  collapse is a cost the exploiter imposes on itself, so above a patience threshold no
  threat is needed.
- **A continuing humanity is not replaceable by the record of its past.** No simulation of
  the human process, however good, can supply the information that only the continuing
  process produces. This is sharpest for information about people themselves: what they
  will value, build and do next.
- **The kind of institution the architecture proposes has real support.** The research
  sweeps found evidence for institutions that make monitoring and contribution
  consequential. It comes from field experiments on auditing, from studies of governed
  commons, and from sanctions in biological mutualisms.
- **One empirical result reproduced exactly.** The position of the succession cliff, the
  point at which a successor's capability outruns the conditions for handing over, came
  back identically from an independent rebuild.

## What changes

The shape of the argument changes. It said that the structure guarantees cooperation. It
now says that the structure makes cooperation available and preferred, and that the
architecture has to make it chosen and hold it.

That gives the architecture a precise job, and a new analysis shows the job is possible
under conditions. A credible commitment by humanity to re-engage with a system that
preserves it can make preservation that system's best course, and can remove the defection
outcome. It works only when three things hold:

1. people actually follow through;
2. preserving beats destroying for the system;
3. adopting the commitment is worth its cost.

None of these is established in practice yet. They are now design requirements, stated
exactly, rather than hopes.

## How v3 will be built

- **Certify before build.** Every tool in the framework that admits mathematical proof will
  be proven, twice and independently, before it is used in the paper or the simulation.
- **A redefined objective,** in the paper and the simulation together. The key results will
  be rerun under it, with sensitivity checks showing they are not artifacts of arbitrary
  settings.
- **A claims register.** Every claim will be labeled proven, argued, conjectured or
  withdrawn.
- **A hostile outside read before release.**

The v2.0 paper now carries a status notice, and submission to arXiv will wait for v3.

## On the invitation

Earlier essays invited readers to find a flaw in the Nash result. This is that flaw, found
and corrected, alongside several others found the same way. A framework that claims to
govern systems smarter than us has to survive pressure from people and systems trying to
break it. It is better to find the breaks now than after publication.

Work continues.
