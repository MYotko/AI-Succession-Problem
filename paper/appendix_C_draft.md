# Appendix C. Version History and Empirical Refinement Record

*Draft for Phase 1 of the v2.0 paper revision. This appendix consolidates the
version progression that was previously carried in the manuscript front matter,
extended through v2.0. It is the authoritative record of how specific claims
were refined or withdrawn as the empirical investigation developed. Numerical
claims trace to `docs/lineage_phi_program_reference.md` Parts IX and X. Current
characterizations are cross-referenced to their body-text homes in Section
VIII.*

This appendix documents the framework's development across four versions. Its
purpose is not ceremonial. The framework rests its credibility on a claim that
its constraints are grounded in physics and mathematics rather than asserted,
and that claim obligates a specific kind of honesty: when investigation produces
a better characterization, the claim updates, and the update is recorded openly
rather than quietly absorbed. The progression below is that record. Read as a
whole, it shows the framework's central methodological commitment in operation:
claims were tested as the empirical record developed, and several were refined
or withdrawn when the evidence did not support the earlier framing.

Each entry states what the earlier version claimed, what the later version
established, and where the current characterization lives in the body text.

## v1.0 to v1.x.1

**Phi extinction buffer.** Version 1.0 characterized phi as producing a large
survival differential, referenced at roughly 65 percentage points at marginal
reproduction rate. Version 1.x.1 applied a frontier-velocity floor fix that
corrected a pre-fix implementation issue: the optimizer had been able to zero
out the runaway penalty by gaming the frontier-velocity term, which distorted
the survival landscape that the larger phi effect was measured against. After
the fix, the inflated differential did not survive revalidation, and a bounded
characterization began to emerge. Current home: Section VIII.3.

**Alpha behavior.** Version 1.0 characterized alpha (the runaway penalty
coefficient) as showing near-zero correlation with outcomes. This was a
consequence of the same pre-fix condition: with the runaway penalty inactive
under optimizer gaming, alpha had little to act through. The frontier-velocity
floor fix activated the penalty and revealed structure that the v1.0 measurement
could not have seen. Current home: Section VIII.4.

## v1.x.1 to v1.x.2

**Phi characterization.** Version 1.x.1, with the penalty active, reported
interim figures near 46 percentage points at the phase boundary and near 14
percentage points in the deep sub-viable regime. Version 1.x.2 work then
advanced a cap-conditional gradient hypothesis: that phi produced a measurable
survival gradient specifically at high successor capability. This was the best
characterization available at the time and was carried as a working claim.
Current home: Section VIII.3.

**Alpha trap.** Version 1.x.1 posited an "alpha trap," a low-phi misconfiguration
regime in which succession would stall at intermediate alpha values. Version
1.x.2 retained this framing pending further investigation. Current home: Section
VIII.4.

**Consensus override protocol.** Version 1.x.2 measured a 73.9 percentage point
survival differential between the protocol active and inactive in a deep
adversarial Monte Carlo, under a succession-blocking policy with an inflated
uncertainty premium. This superseded an earlier v1.0 figure of 16.2 percentage
points from a different and shallower measurement setup. Current home: Section
VIII.6.

## v1.x.2 to v2.0

**Phi.** The v1.x.2 cap-conditional gradient hypothesis did not reproduce under
investigation. A capped-regime analysis identified the apparent high-capability
gradient as an artifact of random-state desynchronization at low successor caps,
in which phi shifted succession timing and thereby desynchronized the optimizer's
noise between runs, producing a spurious differential. What reproduces under
v2.0 architecture is a bounded U-shaped survival curve at marginal reproduction
rate only, approximately ten percentage points between trough and peak, with a
clarified scope condition: the U-shape is a no-succession phenomenon and does
not reproduce under active succession. The behavioral channel itself was
restored by a Stage 1.6 architectural change that moved phi from the saturated
per-step utility computation into the rollout aggregation. Current home: Section
VIII.3.

**Alpha trap.** The alpha trap framing was withdrawn as a pre-fix artifact. The
current characterization is Pattern 1: an alpha-driven succession cliff in which
the joint position of alpha and the successor-to-incumbent capability ratio
governs succession viability, with the cliff migrating inward as alpha rises.
There is no universal stalling regime; there is an economically rejected region
above an operating-condition-dependent cliff. Current home: Section VIII.4.

**Phase boundary.** Version 1.x.2 characterized the survival transition with a
single-boundary framing, with a collapse band near reproduction rate 0.062 to
0.066 and an extinction band near 0.075 to 0.085 under the natural-termination
measurement. The v2.0 finer grid disambiguated two distinct transitions that the
single-boundary framing had conflated: a phi-sensitivity transition near
reproduction rate 0.056 to 0.057, and a survival-rate boundary with its fifty
percent inflection near 0.063. The v2.0 natural-termination measurement and the
survival-rate measurement are different quantities and are now reported as such.
Current home: Section VIII.2.

**Default phi.** The default value of phi was revised from 10 to 25 per current
evidence, on the basis that 25 sits near the survival peak at marginal
reproduction rate and is indistinguishable from 10 above the boundary. Current
home: Section VIII.3.

**Consensus override protocol.** The protocol's protective effect was clarified
as regime-specific. The 73.9 percentage point figure is an adversarial-conditions
measurement; a benign-conditions probe (Phase B Category C) found a null effect,
which is the architecture's complementary prediction rather than a weakening of
the protective claim. The two measurements characterize different regimes.
Current home: Section VIII.6.

**Formal yield logic.** Version 1.x.2 carried a placeholder succession trigger
that fired on a capability or generation gap alone. Version 2.0 (Stage 2)
replaced it with formal yield-condition logic that fires succession only when
the successor's system utility exceeds the incumbent's by more than the
transition cost, using the canonical transition-cost function and the v1.x.2
calibration constants. This is what makes Pattern 1 observable: succession now
fires when it is economically justified. Current home: Section VIII.4 and
Section V.2.

**Bootstrap gate validation arc.** Version 1.x.2 had Gates 1 through 3 active in
specification. Version 2.0 completed the validation arc: Gates 1 through 4 pass
against the reference substrate, including the reintroduction and validation of
the Gate 2 behavioral checks that v1.x.2 had withdrawn, and Gate 5 is verified
not applicable pending operational protocol infrastructure. The critical
capability ratio that the v1.x.2 manuscript documented as an open gap is closed:
it is alpha-dependent, characterized by Pattern 1. Current home: Section VIII.5.

**Patient defection continuation characterization (v2.0, July 2026).** The initial capability-constraint sweep characterized second succession as rare, at zero in 14 of 15 (alpha, growth) cells and 10 percent in the remaining cell. A 1,000-run bracket at alpha=0.40 established that this rarity was a property of the tested alpha floor rather than of the architecture: below the characterized Pattern 1 alpha range, second succession is reliable. The claim is restated from rare continuation to bounded generational depth, which the bracket supports at a weaker runaway penalty than any previously tested. The associated statement that no tested cell exceeded active capability 3.0 is withdrawn as an artifact of the original growth grid. Current home: Section VIII.8.

## The methodological pattern

Across these refinements a single pattern holds. Each earlier claim was the best
characterization available given the implementation and the evidence at the time.
Each refinement followed from a specific, identifiable cause: a frontier-velocity
floor fix that activated a penalty the optimizer had been gaming, a capped-regime
analysis that exposed a noise artifact, a finer grid that separated two
transitions, an architectural change that restored a behavioral channel, or a
formal logic that made an economic regime observable. None of the refinements
were cosmetic, and none were hidden. The numbers that changed were load-bearing,
and they changed because investigation produced a more accurate account of what
the model actually does.

This is the discipline the framework asks of any governance architecture that
claims to be grounded in reality: state the claim, test it, and update it when
the evidence warrants. The progression recorded here is the framework holding
itself to that standard. The current characterizations in Section VIII are
stated per current evidence, and the framework's commitment is that they too will
update if further investigation establishes a better account.
