# Sybil Defense Scaling Study: Design Note and Pre-Registration

*Completed pre-registration, all operator decisions resolved. This note is
committed as the registration on the sybil-scaling branch after the smoke
artifacts and before any characterization data. The registration protects
the analysis criteria from being chosen after seeing outcome data; the
instrument-validation and variance-estimation smoke run that grounds the
power calculation preceded it, which is correct, because variance
estimation is not outcome data and cannot move the criteria. The
characterization sweep is authorized as a separate step after this commit.
The committed registration provably predates all characterization data.*

*Editorial note: this is a working technical document. Internal parameter
language is used deliberately here, as in all repository diagnostics. It
does not govern public-facing surfaces.*

---

## 1. What this study closes

The Sybil defense is validated as effective under the current substrate,
but its cost model is static: it does not scale with validator-set size,
so the existing result characterizes Sybil economics at one implicit scale
and does not say how defense viability moves as the validator population
grows or as the frontier that supplies validators changes character. This
is a named limitation (static Sybil cost model). This study replaces the
static model with a cost structure derived from the independence check's
own computational bottleneck, and characterizes where the defense holds
and where it fails as a function of the frontier's effective diversity.

The result is intended to close the static-cost limitation and to stand as
a bounded, self-contained arc that runs on the current machine, completed
before the CUSUM redesign begins on a migrated machine. It does not depend
on the migration and must be merged and pushed before the migration
starts.

## 2. The defender, specified

The defender is not the responsible institution's own compute. An
institution's compute is public and lags the frontier on both resource and
timing, so a one-against-one framing concedes the defender is permanently
behind. Instead the defender is the frontier community itself, convened as
a validator pool, with three properties:

**Mandatory participation.** Every frontier operator participates.
Participation is not an axis; it is compelled by regulation and, more
durably, incentivized by the root threat: every operator has a standing
interest in preventing any single model from achieving Sybil-based lock-in,
because lock-in by a competitor is existential and lock-in by anyone
collapses the diversity all future capability depends on. The
participation incentive is the framework's own equilibrium logic applied
one level down: defending the commons is each operator's dominant
individual strategy.

**Independence-weighted attribution.** A validator's contribution is
weighted by its independence, not counted per head. Correlated validators
merge to a single consensus input. Six effectively identical models
contribute one input, not six. The defender's strength is therefore the
effective rank of the pool, the number of genuinely distinct epistemic
positions represented, not its headcount. This makes the defense
structurally immune to inflation by duplication, which is the Sybil attack
itself turned against the defense.

**An epistemically orthogonal institutional floor.** The responsible
institution contributes a validator built on a deliberately different
architecture, training lineage, and inductive biases. It cannot lead the
frontier on compute or timing, but it does not need to: it is off-axis by
construction, so it is a guaranteed independent cluster that no amount of
frontier correlation can absorb, and its diversity does not degrade as the
commercial frontier converges. The failure mode is thereby reduced from
resource-and-timing lag to timing lag alone.

## 3. Model collapse as the primary dial

The frontier that supplies validators is subject to convergence:
overlapping training data, cross-distillation, architectural convergence,
and drift toward a shared mean under model-collapse dynamics. Under
independence-weighted attribution this does not reduce participation, it
reduces effective rank: many models fold into few consensus clusters even
at full attendance. Model collapse is therefore expressed exactly as it
should be, not as fewer players but as fewer distinct minds among the
players.

Because the institution is orthogonal and collapse-immune, the pool's rank
does not fall to one at maximum frontier collapse; it falls to two, the
collapsed frontier as one input and the institution as the other. Whether
that rank-two floor clears a single attacker's forging capacity is the
study's headline question.

## 4. Cost structure, grounded not assumed

**Defense cost.** The independence check is pairwise: it measures mutual
information between validators' information sources and computes epistemic
biodiversity as entropy over the validator population's conceptual
diversity. Pairwise correlation structure over N validators is O(N^2) in
the naive exact form. The defense cost therefore scales superlinearly with
validator-set size, and the exponent is the combinatorics of the check,
not a chosen shape. The naive exact O(N^2) form is characterized first as
the conservative, defensible worst case. Whether a smarter incremental or
sampled check relaxes the exponent is named as a follow-on question and is
not folded into this study.

**Attack cost.** Modeled as linear in N in the primary arm, the standard
Sybil assumption and the conservative one for demonstrating a defense
limit: the attacker's cost scales with how many false inputs it must
introduce to swing consensus against a pool of effective rank N. A
superlinear-attack sensitivity check is included so the crossover finding
is not fragile to this assumption.

**Capability as a ratio.** Attacker and defender capability enter through
their ratio, because what determines whether a forged input survives the
check is the attacker's forging power relative to the defender's resolving
power. Capability is bought with compute, so the ratio is interpretable as
a compute ratio. The swept quantity is the capability ratio itself; the
compute-to-capability mapping is carried as a stated interpretive layer,
assumed monotonic with shape uncertain, and its uncertainty is not allowed
to contaminate the swept axis. The specific mapping shape is a post-paper
refinement.

**Defender capability, decomposed.** A more capable defender improves the
check in two mechanistically distinct ways that must be modeled separately,
not blended: it may lower the effective exponent via structured checking
(an algorithmic property), and it may raise per-comparison resolution via
better discrimination (a discrimination property). Each enters with its
own term and its own grounding. Blending them into one "better defender"
knob is prohibited, because it would hand the defender two dials against
the attacker's one and reintroduce the asymmetry this design exists to
avoid.

## 5. The attacker, two arms

The attacker is a single frontier model's forging capacity. Its target is
not raw flooding but the appearance of independence: making coordinated
inputs register as distinct clusters. This runs as two arms with different
crossovers.

**Arm A, false-cluster injection.** The attacker injects apparent clusters
the pool does not truly contain; the check must resolve them back to their
true rank. The direct Sybil analog. The defense wins by correctly
collapsing forged diversity; the attacker wins when forged clusters survive
as distinct. Crossover: the check's resolving power against manufactured
distinctness. The rank-two floor is expected to hold meaningfully here,
because genuine members remain present and checking.

**Arm B, measurement corruption.** The attacker poisons the check so that
genuine correlations read as independence, causing the pool to overcount
its own rank. Subtler and more dangerous: it attacks the instrument, not
the pool, so a defender can believe it is strong while collapsing, and the
orthogonal institution's cluster can be scored as correlated and merged
away. This is the same class of failure as Sub-Threshold Drift, a check
reporting healthy while the real quantity degrades, and that kinship is
noted rather than smoothed over. Crossover: whether the rank-two floor is
even visible to a corrupted check. The floor is expected to be fragile
here, and locating that fragility is a primary purpose of the study.

The A/B asymmetry is itself a pre-registered finding: a robust structural
floor against forged inflation, a fragile one against measurement
corruption, would localize the remaining Sybil risk in the check's
integrity rather than the pool's size and point the next hardening arc
accordingly.

## 6. Axes, parameters, and the analytic floor corner

**Primary swept axis:** effective pool rank, driven by a model-collapse
severity parameter that decays per-participant diversity, from full rank
(all frontier models epistemically distinct) to rank-one frontier (total
monoculture), with the institution holding the pool at rank-two at the
collapse pole.

**Poles and floor, config-driven and tweakable, expressed as fraction of
the effective community:**
- High pole: full diversity, the entire community distinct.
- Low pole: the effective rank corresponding to a thin distinct
  community (institution plus a small distinct frontier remnant), as a
  community fraction.
- Deployment floor: institution plus one distinct peer, the policy
  minimum that would actually be run.
- Analytic floor corner: institution alone at maximum frontier collapse.
  Included even though it is below deployment minimum, because it is the
  cell that answers whether the institution is a true floor or merely a
  boost. This corner is mandatory in every arm.

**Sensitivity arm:** attacker forging capacity against check resolving
power, as a capability ratio, swept at modest resolution. Plus the
superlinear-attack-cost check.

**The ratio-collapse hypothesis.** The two capability dials are
hypothesized to matter only through their ratio. Before the main run, a
validation slice holds the ratio constant while varying both absolute
levels and checks whether the crossover moves. If it does not, the
collapse holds and the main study runs on the two-dimensional
rank-by-ratio surface. If it does move, that is itself a finding and
justifies the fuller grid; the fuller grid is not run on a hunch.

**Fixed and stated for round one, with bias direction named, logged for
the next arc:**
- Participation quality: honest given present. A participant that is in the
  pool checks honestly. (Bias: optimistic; real free-riding would weaken
  the defender.)
- Latency: single-round convening. (Bias: optimistic; convening lag opens
  a timing window, the same class of failure as the drift-detection
  timing problem.)
- Check resolution: pinned except for the attacker's forging term in the
  relevant arm. (Bias: neutral to conservative; a fully adversarially
  degraded check is Arm B taken further.)

## 7. Pre-registered readings

Stated before any data exist. Each reading is fixed per arm, including the
reading of a null and of a boundary result.

**Primary, per arm:** the effective rank below which the pool cannot
out-resolve a single forger. Reported as the crossover rank, with the
crossover located on the swept axis and its confidence characterized at
the cells that bracket it.

**Headline, per arm:** whether the rank-two floor (collapsed frontier plus
orthogonal institution) clears the attacker at maximum collapse. Three
pre-registered outcomes: floor clears (defense has a hard structural floor
immune to collapse); floor fails (defense inherits collapse risk, the
institution is a boost not a floor); floor is boundary (clears in Arm A,
fails in Arm B, the expected and most informative result, localizing risk
in check integrity).

**Sensitivity:** how the crossover rank responds to the capability ratio.
Pre-registered as robust (crossover moves little across the swept ratio
range) versus ratio-sensitive (crossover collapses inward as attacker
capability rises). Ratio-sensitive is the expected outcome; naming it in
advance is what keeps it from being a post-hoc story. The capability ratio
is attacker forging capacity over defender resolving power, swept from 0.1
to 10 on a log scale at 25 points, two orders of magnitude centered on
parity. The defender-favored floor at 10x defender advantage and the
strong-attacker bound at 10x attacker advantage bracket the plausible
asymmetry between the convened pool and a single frontier model; ratios
beyond that are structurally determined (the smoke positive control at
ratio 1,000,000 fails in both arms), so extending the range buys foregone
conclusions at the cost of resolution near the crossover. A threat model
in which a single model can out-forge the convened pool by more than 10x
would justify widening the upper bound, and that widening is itself a
stated threat-model claim; the registered range does not assume it.

**Minimum effects and power.** The characterization compares defense-
failure rate between adjacent cells to locate a crossover, a two-proportion
comparison. The minimum effect of interest is a 15 percentage point
difference in defense-failure rate between adjacent rank cells; a shift
smaller than that is margin noise, not an actionable boundary. Sample size
is set for 80 percent power, two-sided, at alpha 0.05, at worst-case
binomial variance (p=0.5), which requires 174 per cell for the 15-point
MEI; the registered n is 200 per cell, carrying margin above that and
over-powering Arm B, whose failure rate sits away from 0.5 (smoke mean
0.78) and therefore has lower variance. A threshold crossable by noise at
n=200 is not a criterion; the 15-point MEI clears that bar at this n. The
variance estimates grounding this calculation are the smoke fixture
variances (Arm A defense-failure sample variance 0.2537 at mean 0.484; Arm
B 0.1736 at mean 0.781), which are instrument-validation and variance-
estimation outputs, not readings of a crossover. At n=200 the full
candidate surface (25 rank points by 25 ratio points by 2 arms by 2
defense-cost forms by 2 attack-cost forms, 5,000 cells) is one million
runs, single-digit minutes of compute across the available cores before
orchestration overhead, so the sample size is not resource-constrained and
is set for power, not economy.

**Merge rule, registered choice.** Effective rank is computed by threshold-
connected-components on pairwise cosine similarity at threshold 0.9. This
is the primary registered rule, chosen as the defender-conservative option:
connected-components merges more readily than complete-linkage, collapsing
rank sooner, which is the harder and therefore more honest direction for a
study whose headline concerns defender fragility. Complete-linkage is
retained as a registered sensitivity option so the dependence of the
finding on the merge rule can be reported rather than assumed.

**Arm B failure reporting, registered choice.** Arm B defense failure is
defined strictly: any partition corruption counts as failure, including a
corrupted independence read that does not move the measured rank, because a
check that has been corrupted is compromised even when its output
coincidentally lands correct. This strict definition is the primary
registered Arm B outcome. Because the strict bar makes Arm B's failure rate
structurally higher than Arm A's by definition, Arm B is reported on two
tracks: the strict failure rate (primary), and separately the rank-visible
failure rate (corruption that actually moved measured rank below the
floor), which is the subset mechanistically comparable to Arm A. The A-
versus-B asymmetry is read on both tracks, so the definitional gap is never
smuggled in as a mechanism difference.

**Vacuous satisfaction refused.** A criterion satisfied only because an
effect is identically zero everywhere, or met exactly at a boundary, is
flagged, not banked. This is the explicit lesson carried from the
comprehension-gap arc.

## 8. Controls and gates

**Positive controls in every arm.** Each arm includes a configuration
where the defense is known to break (attacker capability far above defender
resolving power, or rank driven to one with no institutional floor), so a
clean result proves the instrument can produce breakage rather than merely
failing to find it. The original static study's inability to demonstrate
its own failure modes is the reason this is mandatory.

**Smoke gate before any full sweep.** A small-n instrumented run confirms:
the defense cost term actually responds to validator-set size; effective
rank actually responds to the collapse parameter (correlated validators
merge, distinct ones do not); the two attack arms produce their intended
distinct effects; positive controls break. The full sweep does not launch
until the smoke run passes and its variance has fed the power calculation
in section 7.

**Discipline carried from prior arts:** manifest not glob for authoritative
CSVs; counting in Python or Measure-Object, never bare pipeline .Count
under PowerShell 5.1; non-ASCII edits through Python UTF-8, never
Set-Content round-trips; registration commit provably predates all
characterization data; analysis against criteria stated verbatim before
interpretation; whole-file byte-identity as the mirror invariant where
surfaces are mirrored; re-running is characterization, never steering
toward a predetermined place.

**Smoke versus characterization, the registration boundary.** The smoke
run is authorized before registration because it validates the instrument
and estimates variance, neither of which is outcome data and neither of
which can move the analysis criteria. It must not run the characterization
grid, must not compute or report a crossover, and must not sweep the
primary rank-by-ratio surface. The characterization sweep is authorized
only after the registration is committed. An agent that finds itself
producing a crossover figure during the smoke run has crossed the boundary
and must stop.

## 9. Scope and sequencing

Runs on the current machine. Merged and pushed to origin before the CUSUM
migration begins; the migration starts from a fresh clone of origin after
this arc is fully pushed, never from a synced working tree. This arc does
not touch the paper, the essays, or the advisor document. Its deliverables
are the redesigned cost model behind a config switch (the static model
retained as a reproducible baseline), the smoke validation and its
variance estimate, the design-note-plus-pre-registration committed after
the smoke and before any characterization data, the swept results under
the manifest, and a final report analyzed against section 7 verbatim.

Post-paper questions logged, not pursued in this arc: the smarter
sub-O(N^2) check and its relaxed exponent; participation quality and
convening latency as live variables; the specific compute-to-capability
mapping shape; the capability-asymmetry surface when both dials turn freely
beyond the ratio collapse.

## 10. Registration decisions, resolved

All four operator decisions are settled and written into the plan above.
This section records them as the resolved analysis plan; nothing here
remains open.

1. Effective-rank axis and poles as fraction of effective community,
   confirmed, with the institution-alone analytic corner mandatory in every
   arm (section 6).
2. Both attack arms confirmed, with the A/B floor-fragility asymmetry
   registered as a finding read on two tracks per section 7's Arm B
   reporting decision.
3. Capability-ratio range set at 0.1 to 10, log scale, 25 points, centered
   on parity, with the threat-model basis stated in section 7.
4. Power set at n=200 per cell for the 15-point defense-failure-rate MEI,
   grounded in the smoke variance estimates, section 7.
5. Merge rule registered as threshold-connected-components at 0.9, the
   defender-conservative choice, with complete-linkage as a registered
   sensitivity option, section 7.
6. Arm B failure defined strictly, reported on strict and rank-visible
   tracks, section 7.

The twelve non-substantive config interpretations surfaced by the smoke
implementation (similarity construction, collapse-decay schedule, cost
normalizations, resolution-probability coupling, forged-cluster count,
institution corruption targeting, and the fixture-only smoke ratios) are
accepted as built and remain config-visible for later revision without a
rebuild. They do not affect the registered analysis criteria.

**Commit sequence.** This completed note is committed as the
pre-registration on the sybil-scaling branch after the smoke artifacts are
in place, so git history shows the finished plan landing before any
characterization data exist. The smoke data predating the registration is
correct: it is instrument-validation and variance-estimation output, not
outcome data, per the registration boundary in section 8. The
characterization sweep is authorized as a separate step after this commit.
