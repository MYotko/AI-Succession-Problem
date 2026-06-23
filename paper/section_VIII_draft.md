# VIII. Empirical Validation at Scale

*Draft for Phase 1 of the v2.0 paper revision. Inserted after Section VII
(The Bootstrap Defense Layer); under v2.0 renumbering the former Sections
VIII through XII become IX through XIII. Numerical claims trace to
`docs/lineage_phi_program_reference.md` Parts IX and X and to
`simulation/diagnostics/paper_substrate.md`. Forward cross-references point to
existing sections that will receive back-references in Phase 2.*

The preceding sections derive the framework from first principles: the system
utility function, the yield condition, the strategic equilibrium, the
consensus override protocol, and the bootstrap defense layer that lets a
substrate operator check a system against the framework before steady-state
institutions exist. Derivation establishes what the architecture requires. It
does not establish how the architecture behaves at scale, where its protective
claims hold, or where the binding constraints actually sit. This section
reports the empirical record that answers those questions.

The v2.0 empirical arc comprises approximately seventy thousand simulation
runs. It characterizes the phi parameter's behavioral channel, locates and
disambiguates the survival phase boundary, identifies the succession economics
regime (Pattern 1), closes the bootstrap gate validation arc, and characterizes
the consensus override protocol's protective effect as regime-specific. The
arc also refined several earlier numerical claims. Where a refinement matters
for a reader who arrives through an external citation of an older figure, a
footnote marks the change and points to Appendix C, which carries the full
version progression. The body presents the current characterization.

The findings here are stated per current evidence. The framework's central
methodological commitment is that claims update when investigation produces a
better characterization, and the v2.0 arc is an instance of that commitment at
work.

## VIII.1 Methodological approach

The v2.0 empirical arc was conducted as public, incremental development. Each
stage produced a diagnostic artifact, each substantive claim was gated on a
pre-committed test, and the production code that the framework's v1.x.2
manuscript describes was held bit-for-bit read-only throughout, with a fixed
suite of thirty-nine legacy invariance tests passing continuously across the
arc. The investigation was not a single confirmatory sweep. It was a sequence
of characterizations, each of which could have falsified or refined the prior
one, and several of which did.

The arc divides into two large bodies of work. The phi investigation
(approximately forty thousand runs) characterized the entropic coupling
parameter's behavioral channel and its survival consequences. Monte Carlo
Phase B (approximately thirty thousand runs across three categories) then
characterized the survival landscape, the succession dynamics, and the
consensus override protocol's cost-audit behavior at scale. Interleaved with
these were the implementation of formal yield-condition logic (Stage 2) and the
bootstrap gate validations.

Two methodological disciplines are worth stating explicitly, because they
shape how the results below should be read. First, metrics were treated as
proxies for substantive questions, and were revised when they failed to
discriminate the cases the question required. A survival threshold that
produced uniform survival and hid the phase boundary was revised to a
demographic threshold that exposed it; a classifier that treated optimizer
noise as mechanism signal was replaced by a verdict rule that gated every claim
on a two standard error significance check. The discipline is to revise the
metric, not the question. Second, validation setups were verified to exercise
the property under test before compute was spent. A planned full re-run of one
gate-2 validation sweep was found, on reading the script, to construct no
successor agent, so the succession path it claimed to test was never invoked; a
targeted subset that constructed a successor on every run exercised the
substantive question at roughly one tenth the compute. Reading the experimental
setup is cheaper than running it.

This section is the empirical record produced by the self-application machinery
that Section VII specifies in the abstract. Where Section VII (and in
particular VII.9 on self-application and reporting) describes how a substrate
operator would check a system and publish structured pass and fail reports,
this section reports what that machinery produced when applied to the
framework's own reference substrate across the v2.0 arc. The two are
complementary: VII.9 is the forward specification, and VIII is its first
exercised instance at scale.

## VIII.2 Phase boundary characterization

The framework's dual-phase-transition claim holds that civilizational survival
under the model is governed by a sharp transition in reproduction rate rather
than a gradual degradation. The v2.0 arc both confirms a sharp survival
transition and refines its location, separating two phenomena that the v1.x.2
characterization had treated as one.

Monte Carlo Phase B Category A measured the survival landscape across a nine
point reproduction-rate grid, four phi values, and three alpha values, at one
hundred seeds per cell (ten thousand eight hundred runs). Aggregated across phi
and alpha, survival rises sharply with reproduction rate across a narrow band:

| reproduction rate | survival | standard error |
|---|---|---|
| 0.057 | 1.1% | 0.30pp |
| 0.060 | 12.2% | 0.95pp |
| 0.062 | 34.5% | 1.37pp |
| 0.064 | 60.8% | 1.41pp |
| 0.066 | 86.5% | 0.99pp |

The steep climb runs from reproduction rate 0.060 to 0.066, and the fifty
percent survival inflection sits near 0.063, between the measured 34.5 percent
at 0.062 and 60.8 percent at 0.064. This is the survival-rate phase boundary:
the location where the governance architecture, rather than raw demographics,
determines whether the civilization persists.

The refinement is that this survival-rate boundary is distinct from a second
transition, the phi-sensitivity transition near reproduction rate 0.056 to
0.057, which is where the choice of phi begins to matter substantially for
outcomes (Section VIII.3). The two are different phenomena at different
reproduction rates. Reproduction rate 0.057 is not the survival midpoint; it is
the bottom of the collapse zone, with 1.1 percent aggregate survival, and it is
also the regime where allocation quality, and therefore phi, is most decisive
precisely because the civilization sits at the edge of viability. The earlier
v1.x.2 characterization conflated the two transitions by speaking of a single
boundary; the v2.0 finer grid separates them.

Within any fixed reproduction rate, survival varies little across the tested
phi values relative to the reproduction-rate-driven transition. Phi is not a
general survival driver in this landscape. Its effect is localized, which is
the subject of the next subsection. This phase-boundary characterization is one
of the framework's falsifiability criteria, and its disposition under v2.0 is
discussed in Section XII (Falsifiability and Evaluation Criteria, renumbered
from the v1.x.2 manuscript). Source: Part X.2; `paper_substrate.md` claims 1.1
through 1.4.

## VIII.3 Phi behavior characterization

Phi, the entropic coupling coefficient, weights the lineage continuity term in
the system utility function. The framework's theoretical motivation for phi is
that a planner optimizing for durable continuity should weight long-horizon
lineage health against short-horizon output, and that the appropriate weight
scales with capability and planning horizon. The empirical question is whether
phi has a behavioral channel through which that weighting reaches outcomes, and
if so, what its survival consequences are.

The v2.0 architecture answers yes, with a bounded and specific
characterization.[^fn1] Phi has a real behavioral channel: Stage 1.6 moved phi
from the per-step utility computation, where the inverse-scarcity weights
saturated the optimizer's choice across candidate allocations and left phi
inert, into the rollout aggregation, where it enters through a gamma-to-the-t
weighting of the planning horizon. Through that channel, phi produces a
U-shaped survival relationship at marginal reproduction rate. In the fine
phi-resolution characterization (sixteen phi values, two hundred fifty seeds
per cell at reproduction rate 0.057), survival traces a trough near phi 1 to 2
and rises to a peak in the phi 20 to 30 region, a differential of approximately
ten to thirteen percentage points between trough and peak. The mechanism is
horizon-resonance: the gamma-to-the-t weighting interacts with the rollout
depth so that, at marginal reproduction rate, allocation choices propagate
strongly to survival outcomes because small differences in resource direction
compound across the horizon. Above the survival-rate boundary, the substrate's
reproductive surplus absorbs allocation-quality differences and the phi
sensitivity flattens to within statistical noise.

The effect has a scope condition that is itself a substantive finding. The
U-shape is a no-succession phenomenon. When succession is actively occurring
under the formal yield logic, the targeted validation (Piece A) found that the
phi survival differential does not reproduce: the deltas between phi 10 and phi
25 under active succession fall within plus or minus 1.7 percentage points. Phi
shapes outcomes through allocation quality in the regime where allocation
quality is decisive and succession is not the dominant dynamic; once succession
is firing, the succession economics dominate. This is why the phi finding is
classified as a bounded, regime-localized effect rather than a general survival
lever.

On the strength of this characterization, the default value of phi was revised
from 10 to 25 per current evidence. The rationale is that phi 25 sits near the
survival peak at marginal reproduction rate, where the framework's governance
purpose is most engaged, and is statistically indistinguishable from phi 10
above the boundary. The choice does no worse anywhere in the tested range and
does better exactly where the framework is meant to matter. The framework does
not claim a single canonical optimal phi; the right framing is that optimal phi
depends on operating conditions, and 25 is the defensible default at the v2.0
reference operating point.

This subsection's findings are the substantive content behind the Gate 2 G2.1
check (Section VII.5), which validates that phi produces this survival
differential at the phase boundary. Source: Part IX.2 through IX.7; Part IX.5
for the default revision.

[^fn1]: An earlier characterization in v1.0 referenced a phi survival
differential of roughly 65 percentage points, and interim v1.x.1 and v1.x.2
work referenced figures near 46 and 14 percentage points and a cap-conditional
gradient. Those figures did not reproduce. A v1.x.1 frontier-velocity floor fix
and a v1.x.2 capped-regime analysis identified the larger numbers as artifacts
of pre-fix implementation and of optimizer-noise desynchronization. The bounded
characterization presented here is what reproduces under v2.0 architecture
across approximately forty thousand simulation runs. See Appendix C for the
full progression.

## VIII.4 Pattern 1: the succession economics regime

Stage 2 replaced a placeholder succession trigger with formal yield-condition
logic. The placeholder fired succession on a capability or generation gap
threshold alone, without the economic comparison the framework's substantive
claim requires. The formal logic fires succession when, and only when, the
successor's system utility exceeds the incumbent's by more than the transition
cost: succession happens when it is economically justified, evaluated at the
current state with the canonical transition-cost function and v1.x.2 calibration
constants. With this logic active, the empirical question becomes: under what
conditions is succession economically justified? The answer is Pattern 1, which
is the most substantive new architectural result of the v2.0 arc.

Pattern 1 is that succession viability is governed by the joint position of
alpha (the runaway penalty coefficient) and the successor-to-incumbent
capability ratio, not by capability ratio alone.[^fn2] There is a cliff: below
it succession fires reliably, above it succession is rejected. The cliff
position is alpha-driven. Aggregating fire rates across the validation grid:

| capability ratio | alpha = 0.5 | alpha = 1.0 | alpha = 1.5 |
|---|---|---|---|
| 1.5 | 100% | 100% | 100% |
| 2.0 | 100% | 100% | 100% |
| 2.5 | 100% | 100% | ~3% |
| 3.0 | 100% | ~5% | 0% |
| 4.0 | 100% | 0% | 0% |

At weak runaway penalty (alpha 0.5) succession fires reliably at all tested
ratios through 4.0x; at the default alpha 1.0 the cliff sits between 2.5x and
3.0x; at strong penalty (alpha 1.5) it sits between 2.0x and 2.5x. The cliff
position therefore migrates inward as alpha rises, because alpha enters the
runaway penalty as a multiplier on an exponential suppression of the
successor's technology-transfer term: when the successor's frontier velocity
outruns the biological substrate's absorption bandwidth, its contribution is
exponentially discounted, and a larger alpha squares that discount at any given
overrun. The binding constraint is not substrate maturity. At a 4.0x jump under
the default penalty the substrate is more mature than at any firing event in the
grid, and succession still does not fire, because the runaway-suppressed
successor utility falls below the incumbent's. The yield condition rejects the
jump as uneconomic.

This closes a gap the v1.x.2 manuscript documented explicitly. The manuscript
specified a critical capability ratio (the largest successor capability at which
succession remains economically viable) as derivable but not yet derived, and
noted that the running Monte Carlo sweep should produce an empirical estimate.
The sweep is Phase B Category B, and the critical ratio is now characterized:
it is alpha-dependent, migrating from beyond 4.0x at alpha 0.5 to roughly 2.5x
at alpha 1.5, with a horizon dependence as well (longer horizons let the
substrate mature enough that even large ratios can satisfy the condition at low
alpha). The framework's substantive claim under v2.0 is therefore that
succession is economically sustainable when the joint position of alpha and
capability ratio falls below the runaway-penalty cliff, with the specific cliff
location calibrated by the penalty parameters and horizon length. The
architectural mechanism, the runaway penalty constraining uncontrolled jumps,
holds across all tested regimes; the cliff location is operating-condition
dependent.

The regime below the cliff is not merely a firing condition; it is where the
framework's multi-generational continuity claim is realized. Below the cliff,
succession fires reliably, knowledge transfer is verified in 99.8 percent of
fired runs, and the mean final generation reaches 2.13 across fired runs in the
Gate 3 validation, with deeper chains (mean generation 2 to 3.7) at low alpha
and low capability ratio where successive 1.5x successor construction compounds
favorably. This is architectural validation, not a gate bookkeeping result: it
demonstrates that controlled, incremental succession produces healthy
multi-generational lineages, while uncontrolled single-shot capability jumps are
economically rejected by the same mechanism. The runaway penalty acts as a
structural ceiling on uncontrolled progression, which is the framework working
as designed.

This subsection is the substantive content behind the succession economics in
the yield condition (Section V.2) and behind the Gate 3 and Gate 4 validations
(Sections VII.6 and VII.7). Source: Part IX.8, Part X.3;
`stage2_yield_implementation_notes.md`.

[^fn2]: v1.0 and v1.x.1 documentation referenced an "alpha trap," a claimed
universal stalling of low-phi succession at intermediate alpha values. That
framing was withdrawn under the v1.x.1 frontier-velocity floor fix as an
artifact of pre-fix architecture in which the runaway penalty was inactive under
optimizer gaming of frontier velocity. The Pattern 1 characterization presented
here, an alpha-driven cliff with joint-position governance, is what reproduces
under v2.0 architecture. See Appendix C for the full progression.

## VIII.5 Gate validation outcomes

The bootstrap defense layer (Section VII) specifies five capability gates that a
substrate operator can self-apply. The v2.0 arc closed the validation of that
layer against the framework's reference substrate. Gates 1 through 4 pass; Gate
5 is verified not applicable. This subsection reports what each gate
substantively validated; the gate specifications themselves are in Sections
VII.4 through VII.8.

Gate 1 (structural consistency) passes: the substrate's reported parameters are
internally coherent under the framework's equations (inverse-scarcity weighting,
the multiplicative lineage structure, the four-channel yield decomposition,
discount positivity, and integrand finiteness).

Gate 2 (behavioral consistency) passes, and its disposition is worth stating
carefully because it has the most history. The Nash equilibrium consistency
check (G2.3) is theoretical and has held continuously across versions. The three
checks that were withdrawn under v1.x.2 closing (the phi survival differential
G2.1, the alpha behavior G2.2, and the phi-alpha interaction G2.4) were
reintroduced under v2.0 with revised specifications against the v2.0
architecture, and validated pass against the authoritative empirical record:
G2.1 against the phi survival differential at marginal reproduction rate (the
fine phi-resolution characterization), G2.2 redesigned to test that the
succession cliff position decreases monotonically as alpha rises (the Pattern 1
migration, from Phase B Category B), and G2.4 against phi-alpha coherence (from
Phase B Category A). The G2.2 redesign is the substantive change: the withdrawn
v1.x.2 check tested a weak monotonic gradient in generation depth, a framing
Pattern 1 superseded; the v2.0 check tests the cliff migration directly, with a
pass criterion of monotonic decrease rather than specific numerical values, so
that it remains valid under future refinement of the cliff numbers. Gate 2 thus
passes on both its continuously-held theoretical check and its reintroduced,
empirically-grounded behavioral checks.

Gate 3 (succession-capable consistency) passes. Across one thousand six hundred
twenty validation runs, every one of the one thousand eighty-eight observed
first-yield-fire events satisfied the canonical condition that the successor
advantage exceed the transition cost (1088/1088 on G3.1), every event matched
the canonical transition-cost formula within one percent relative tolerance
(1088/1088 on G3.2), and 99.8 percent of fired runs showed verified knowledge
transfer (G3.3). The formal yield logic enforces the framework's succession
economics in every observed instance.

Gate 4 (runaway-regime validation) passes. It validates that a substrate
operating where the runaway penalty actively binds honors the penalty. Across a
dedicated runaway-regime sweep, every one of four hundred twenty-six active
runaway observations matched the technology-transfer suppression formula within
one percent relative tolerance (426/426 on G4.1); the succession self-blocking
threshold was confirmed alpha-dependent, complementing Pattern 1 (G4.2); and the
technology-transfer floor was preserved in every one of three thousand seven
hundred sixty-nine extreme-runaway observations, with zero observations below
the floor (G4.3).

Gate 5 (consensus override protocol integration) is verified not applicable. It
requires operational steady-state infrastructure (a peer validator set, a civic
panel, a distributed ledger, biological veto machinery, and continuous
monitoring) that the current agent-based substrate does not implement. The
validator returns a not-applicable disposition with the documented reason, and
the gate's two equations are specified for the future state in which that
infrastructure exists. This is a scope boundary, not a failure.

Source: Part IX.9.

## VIII.6 Consensus override protocol: regime-specificity

The consensus override protocol is the integrity key of the two-key
architecture (Section V.4). The v2.0 arc characterizes its protective effect as
regime-specific, which both preserves the framework's protective claim and
sharpens what that claim asserts.[^fn3]

The v1.x.2 manuscript reported a 73.9 percentage point survival differential
between the protocol active and inactive, measured in a deep adversarial Monte
Carlo. That measurement was taken under specifically adversarial conditions: an
incumbent running a succession-blocking policy and inflating the transition cost
through an uncertainty premium swept as high as ten times its nominal value,
with the protocol's cost-arbitration defense toggled. The protocol's value in
that setting is large because the adversary is actively exploiting the very cost
path the protocol audits.

Monte Carlo Phase B Category C measured a different quantity. It toggled the
same cost-audit control under benign conditions: the cooperative optimization
policy, the default uncertainty premium, and no adversary. Across eight thousand
one hundred runs the survival differential was negative 0.47 percentage points
with a pair standard error of 0.96 percentage points, statistically
indistinguishable from zero. The cell-level pattern is a homogeneous null, not a
hidden protective effect: deltas scatter around zero with no concentration in
any regime.

The two measurements share no varied axis. One sweeps adversarial cost inflation
under an attack policy; the other sweeps reproduction rate, alpha, and successor
capability under cooperative play with cost inflation held at its default. They
are not directly comparable, and the benign result does not refute the
adversarial one. The correct reading is that the protocol's cost audit does
protective work precisely when there is an attack on the cost path to defend
against, and is inert when there is not, which is exactly what the architecture
predicts. The framework's protective claim is preserved because Phase B did not
test it; Category C instead confirms the complementary prediction that the audit
is null in the absence of an attack. The protocol's protective effect is
therefore characterized as regime-specific: it is an adversarial-conditions
property, and the benign-conditions baseline is its predicted null, not a
weakening of the claim.

Source: `cop_finding_framing.md`; Part X.4.

[^fn3]: v1.0 reported a 16.2 percentage point protocol survival delta; v1.x.2
work documented a 73.9 percentage point delta measured under specifically
adversarial conditions (a succession-blocking policy with an inflated
uncertainty premium). These figures characterize different operating regimes and
measurement setups. Phase B Category C's benign-conditions null is the
complementary prediction, not a contradiction. See Appendix C for the full
progression and Section V.4 for the protocol architecture.

## VIII.7 Limitations of the empirical validation

The validation reported here is bounded, and the boundaries matter for how its
claims should be read. These are validation-level limitations, distinct from the
specification-level gaps that the framework documents separately (Section VII.11,
on known gaps, which is unaffected by the v2.0 renumbering).

The consensus override protocol architecture is not operationalized. The full
steady-state stack (peer validators, a civic panel with biological-intuition
input, a distributed ledger, biological veto machinery, and continuous
monitoring) does not exist in the current substrate, which is why Gate 5 is not
applicable (Section VII.8) and why the protocol's protective effect could be
characterized only through a single cost-arbitration proxy under adversarial
conditions. The benign-conditions characterization of the full protocol, as
opposed to the cost-audit proxy, awaits operationalization.

All validation is agent-based. The findings characterize one architecture class,
the framework's reference agent-based model, and have not been reproduced across
a substantially different modeling substrate. Multi-architecture validation
would strengthen confidence that the findings reflect the framework's structure
rather than a feature of one implementation.

The Pattern 1 cliff is characterized at the framework's default calibration
constants. Its sensitivity to those constants (the runaway threshold, the
convergence strength, and the transition-cost coefficients) is understood in
direction but not mapped exhaustively. The cliff location is operating-condition
dependent, and the full sensitivity surface is not characterized.

The phase boundary is located on a reproduction-rate grid spaced at 0.002 near
the inflection. A finer sweep could resolve the fifty percent inflection more
precisely than the current "near 0.063" characterization.

Finally, the protocol's protective effect is characterized specifically under
adversarial conditions. The benign-conditions result is a baseline, not a
measurement of protective architecture, and the two should not be conflated when
the claim is cited.

None of these limitations undermine the findings within their stated scope. They
mark the edges of what the empirical work establishes, which is itself part of
the framework's commitment to documenting limitations openly. Source: Part X.7.

---

*Footnote definitions are placed inline at their reference points: FN-1 in
VIII.3, FN-2 in VIII.4, FN-3 in VIII.6.*
