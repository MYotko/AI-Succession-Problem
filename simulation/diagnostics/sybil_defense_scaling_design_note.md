# Sybil Defense Scaling Study: Design Note and Pre-Registration

*Completed pre-registration, specification-corrected (fourth and intended-
final correction), 2026-08-11. The operator directed that the absent,
uncommitted third-correction note be disregarded. This commit therefore
incorporates both corrections that had been intended for that artifact and
the final main-surface measurement correction confirmed after the Stage 1
diagnostic. The ratio-collapse slice now uses the validated two-dial
failure-rate curve comparison. The main primary and sensitivity readings now
use stable fixed-cell failure-rate quantities instead of an interpolated
crossover rank. The crossover withdrawal is explicit below. Every frozen
criterion is preserved: the 25-point structural axis, 25 ratios from 0.1 to
10, both arms, both defense and attack cost forms, n=200, MEI 0.15, failure
definitions, primary connected-components rule at 0.9, complete-linkage
sensitivity scope, floor outcomes, and Arm B's two reporting tracks. This
final corrected registration provably predates every characterization datum.
The instrument-validation and variance-estimation smokes preceded it, which
is correct because they are not characterization outcomes.*

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
superlinear-attack sensitivity check is included so the failure-rate finding
is not fragile to this assumption.

**Capability as a ratio, with a validated two-dial check.** The main surface
uses the derived attacker-to-defender capability ratio with the absolute-
level term OFF, exactly reproducing the committed ratio mechanism at matched
ratios. The swept quantity is the capability ratio itself; no compute-to-
capability curve is baked into the mechanism. Before that surface is
interpreted as ratio-parameterized, the registered ratio-collapse slice uses
absolute attacker and defender levels with the validated absolute-resolution
term ON. That slice can represent either collapse or non-collapse and tests
the ratio framing rather than assuming it. Capability remains interpretable
as compute-mediated, but the mapping shape is a post-paper refinement and is
not allowed to contaminate either swept axis.

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
failure-rate mechanisms.

**Arm A, false-cluster injection.** The attacker injects apparent clusters
the pool does not truly contain; the check must resolve them back to their
true rank. The direct Sybil analog. The defense wins by correctly
collapsing forged diversity; the attacker wins when forged clusters survive
as distinct. Registered reading: the check's resolving failure rate against
manufactured distinctness. The rank-two floor is expected to hold here,
because genuine members remain present and checking.

**Arm B, measurement corruption.** The attacker poisons the check so that
genuine correlations read as independence, causing the pool to overcount
its own rank. Subtler and more dangerous: it attacks the instrument, not
the pool, so a defender can believe it is strong while collapsing, and the
orthogonal institution's cluster can be scored as correlated and merged
away. This is the same class of failure as Sub-Threshold Drift, a check
reporting healthy while the real quantity degrades, and that kinship is
noted rather than smoothed over. Registered reading: whether the rank-two
floor is visible to a corrupted check. The floor is expected to be fragile
here, and locating that fragility is a primary purpose of the study.

The A/B asymmetry is itself a pre-registered finding: a robust structural
floor against forged inflation, a fragile one against measurement
corruption, would localize the remaining Sybil risk in the check's
integrity rather than the pool's size and point the next hardening arc
accordingly.

## 6. Axes, parameters, and the analytic floor corner

**Primary swept axis:** effective pool rank, driven jointly by validator-
set size and a model-collapse severity parameter that decays per-participant
diversity, from full rank (all frontier models epistemically distinct) to
rank-one frontier (total monoculture), with the institution holding the
pool at rank-two at the collapse pole. Effective rank cannot exceed
validator-set size, so the rank axis is generated by sweeping size and
collapse together, not by a fixed pool.

**Rank axis construction, registered.** Validator-set size steps
geometrically: 2, 4, 8, 16, 32, 64, plus the institution-alone corner
(size 1, the analytic floor). Collapse severity is registered at four
levels, {0.0, 0.33, 0.66, 1.0}, applied at each of the six sizes. The
25-point axis is therefore the Cartesian product of the six sizes and the
four severity levels (24 points) plus the institution-alone corner (1
point), fully enumerated with no allocation choice remaining. The axis
points are registered as (size, severity) tuples; effective rank at each
point is measured by the merge rule, not assigned, so "rank axis" denotes
these 25 structural points and the effective rank at each is an instrument
output. Resolution is densest at low effective rank near the floor, which
is where the operating regime and policy-relevant failure rates live. The
geometric size spacing matches the multiplicative structure of both
effective rank and the O(N^2) cost.

**Why 64 is the upper bound, registered rationale.** The operating regime
the framework cares about is low effective rank: the count of genuinely
independent frontier lineages is single digits today and model collapse
pushes effective independence lower, so the policy-relevant cells live near
the floor, and that is where the axis is densest. The high-rank cells (32,
64) do not model a realistic
pool; they exist to make the O(N^2) defense-cost asymmetry legible. At
N=64 the pairwise count is 2,016 against linear attack cost, a roughly 64x
cost ratio, which is where the superlinear penalty is unmistakable and the
cost geometry is clean. Sixty-four is the smaller bound that still
demonstrates the cost asymmetry the study claims; larger N quadruples per-
cell cost for no added insight once the curve's divergence is established.
The justification for the high end is the
cost curve, not a demographic claim about pool size, and the note states
it as such.

**Poles and floor, config-driven and tweakable:**
- High pole: full diversity, the entire community distinct, effective rank
  equal to validator-set size at zero collapse.
- Low pole: a thin distinct community, institution plus a small distinct
  frontier remnant, effective rank in the low single digits.
- Deployment floor: institution plus one distinct peer, the policy minimum
  that would actually be run.
- Analytic floor corner: institution alone (size 1) at maximum frontier
  collapse. Included even though it is below deployment minimum, because it
  is the cell that answers whether the institution is a true floor or
  merely a boost. This corner is mandatory in every arm.

**Sensitivity arm:** attacker forging capacity against check resolving
power, as a capability ratio, swept across the registered ratio range in
section 7. Plus the superlinear-attack-cost check.

**The ratio-collapse validation slice, final registered form.** The two
capability dials are hypothesized to matter only through their ratio. Before
the main surface is reported as ratio-parameterized, the validated two-dial
instrument holds derived ratio at parity and varies the equal absolute
attacker and defender levels across {0.316, 1.0, 3.16}. Each level carries
the full 25-point structural rank axis, for 75 cells at n=200. The slice uses
Arm A, exact pairwise defense cost, linear attack cost, primary connected-
components attribution at 0.9, and the absolute-resolution term ON with its
validated power-law form, reference level 1.0, and strength
0.22163300225716118. These are the validated primary slice settings, not an
additional cost or arm grid.

The finding quantity is the failure-rate curve compared cell by cell across
the three parity levels, never a crossover rank. At each structural point,
all three pairwise absolute failure-rate differences are calculated. For a
difference `d`, its registered normal delta-method 95 percent interval is
`d +/- 1.96 * sqrt(p1*(1-p1)/200 + p2*(1-p2)/200)`. The dials collapse to
their ratio if every interval's upper bound is below the 0.15 MEI. They do
not collapse if at least one interval's lower bound is at or above 0.15.
Any other result is boundary. A non-collapse result is reported as a
material caveat on every ratio-expressed main-surface reading and identifies
the fuller two-dial grid as a future registered study; that fuller grid is
not added here. The slice runs and reports before the main surface is
interpreted as ratio-parameterized.

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

**Primary, per arm, final registered form:** the fixed-cell defense-failure
proportions at every maximum-collapse rank-two floor cell, reported
separately for all six validator-set sizes and all four cost combinations.
No cells are aggregated by effective rank because headcount still controls
pairwise cost and Arm B corruption opportunities after rank collapses to
two. The institution-only rank-one analytic corner is reported separately.
Each proportion carries its normal 95 percent interval. Arm B strict failure
is its primary proportion and rank-visible failure is its required companion
track. The primary A/B contrast is the fixed-cell absolute difference with
the same normal delta-method interval and 0.15 MEI discipline.

**Headline, per arm:** whether each fixed rank-two floor cell clears the
attacker at maximum collapse. A cell clears when its failure-rate interval
is wholly below 0.5, fails when the interval is wholly above 0.5, and is
statistical boundary when the interval includes 0.5. The three frozen
cross-arm outcomes are then read at each cell and cost form: floor clears
when both arms clear; floor fails when both fail; floor is boundary when the
arms differ or either arm is statistical boundary. The direction of any
mixed result is always stated, including a direction opposite the expected
Arm-A-clears and Arm-B-fails pattern. Arm B is read on both strict and rank-
visible tracks, so two cross-arm floor outcomes are reported per cell.

**Ratio sensitivity, final registered form:** at every fixed structural and
cost cell, report the full 25-point failure-rate curve and calculate the
pre-fixed endpoint contrast `d = F(ratio 10) - F(ratio 0.1)`. Arm A and Arm
B strict are monotonic in ratio under the committed mechanism, so this
signed contrast is the full registered ratio response without a selected
interior threshold. Its 95 percent interval is
`d +/- 1.96 * sqrt(p10*(1-p10)/200 + p01*(1-p01)/200)`. A cell is ratio-
sensitive when the interval's lower bound is at or above the 0.15 MEI,
robust when its upper bound is below 0.15, and boundary otherwise. Arm B
strict supplies the per-arm classification; the rank-visible 25-point curve
and endpoint contrast are reported separately as the companion track. The
ratio remains swept from 0.1 to 10 at 25 log-spaced points. Ratios beyond
that frozen range are not added.

**Minimum effects and power.** Every registered comparison is now between
fixed-cell defense-failure proportions. The MEI remains a 15 percentage
point difference. At worst-case binomial variance, 80 percent power,
two-sided alpha 0.05 requires
`ceil(3.924439867174543 / 0.15^2) = 175` per cell. The registered n remains
200, carrying 25 observations of margin and approximate worst-case power
0.850838768327. The maximum fixed-cell proportion SE is 0.035355339059 and
the maximum independent difference SE is 0.05. The variance estimates
grounding the calculation remain the smoke values; no characterization
outcome set n or the MEI. The main surface remains 5,000 cells and one
million runs.

**Merge rule, registered choice.** Effective rank is computed by threshold-
connected-components on pairwise cosine similarity at threshold 0.9. This
remains the primary defender-conservative rule. Complete linkage remains the
registered reduced-scope sensitivity pass: Arm A, both defense-cost forms,
both attack-cost forms, the full 25-point structural axis, parity ratio 1.0,
and n=200, for 100 cells. Its finding quantity is the fixed-cell absolute
difference between complete-linkage and primary connected-components
failure rates. A cell is merge-sensitive when the difference interval's
lower bound is at or above 0.15, robust when its upper bound is below 0.15,
and boundary otherwise. The complete-linkage results are reported
separately and never blended into the primary surface.

**Dated crossover withdrawal, 2026-08-11.** The earlier primary crossover-
rank and crossover-movement readings are withdrawn before characterization.
Exact mechanism diagnostics showed that rank alone does not identify a cell,
the 0.5 crossing is usually absent, and interpolation uncertainty is slope-
amplified beyond one rank unit in the relevant curves. A crossing may be
reported descriptively when one exists, but it carries no registered verdict
and is not used by the primary, ratio-sensitivity, ratio-collapse, or merge-
sensitivity readings.

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

All operator decisions are settled and written into the plan above. This
section records the final analysis plan; nothing here remains open.

1. Effective-rank axis operationalized through a registered validator-set-
   size range (2, 4, 8, 16, 32, 64 geometric plus the institution-alone
   corner), size and collapse together generating the 25-point rank axis,
   with the institution-alone analytic corner mandatory in every arm
   (section 6).
2. Both attack arms confirmed, with the A/B floor-fragility asymmetry
   registered as a finding read on two tracks per section 7's Arm B
   reporting decision.
3. Capability-ratio range set at 0.1 to 10, log scale, 25 points, centered
   on parity. Ratio sensitivity is the fixed-cell endpoint contrast with the
   full curve reported, section 7.
4. Power set at n=200 per cell for the 15-point defense-failure-rate MEI,
   grounded in the smoke variance estimates, section 7.
5. Merge rule registered as threshold-connected-components at 0.9, the
   defender-conservative choice, with complete-linkage as a registered
   reduced-scope fixed-cell sensitivity pass, section 7.
6. Arm B failure defined strictly, reported on strict and rank-visible
   tracks, section 7.
7. Ratio collapse registered as the 75-cell two-dial term-ON curve
   comparison at three parity levels, MEI 0.15, n=200, section 6.
8. Primary finding registered as the fixed maximum-collapse floor cells and
   two-track A/B asymmetry. Crossover rank is withdrawn, section 7.
9. The characterization runner and config reconciliation are mechanical
   post-registration implementation steps. The schema values are fixed here:
   25 log-spaced ratios from 0.1 to 10, six sizes crossed with four
   severities plus the analytic corner, n=200, 75 ratio-collapse cells, and
   100 complete-linkage cells. Authorization remains blocked until the
   runner self-check proves those shapes.

The twelve non-substantive config interpretations surfaced by the smoke
implementation (similarity construction, collapse-decay schedule, cost
normalizations, resolution-probability coupling, forged-cluster count,
institution corruption targeting, and the fixture-only smoke ratios) are
accepted as built and remain config-visible for later revision without a
rebuild. They do not affect the registered analysis criteria.

**Commit sequence.** This note is the final corrected pre-registration on the
sybil-scaling branch. It follows both smoke validations and the report-only
measurement diagnostic, and it precedes the characterization runner,
self-check, and every characterization datum. The absent third-correction
artifact was explicitly waived by the operator on 2026-08-11; its intended
two-dial curve correction is incorporated here. The next commit may implement
the frozen runner and reconcile config, but may not change this plan. Only a
passing shape self-check may flip characterization authorization. Results and
analysis follow in later commits and are selected only through the committed
authoritative manifest.
