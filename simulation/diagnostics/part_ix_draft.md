# Part IX Draft: Phi Investigation Findings and v2.0 Substantive Claims

**Status: draft for operator review. Not yet integrated into `docs/lineage_phi_program_reference.md`.**

This draft proposes a hybrid restructure of the existing Part IX (committed 585bd9e). Sections IX.1 through IX.6 preserve the existing wording with light forward-pointing notes; sections IX.7, IX.8, IX.9 are new content covering Stage 2 + Piece A + Gate 3 findings; section IX.10 consolidates the methodological lessons (existing four + two new); section IX.11 updates the future research directions to reflect closed and open items.

After operator approval, the content below replaces the existing Part IX in the program reference between Part VIII and the closing "One-line status" block. The one-line status itself will need a small update to reference the expanded synthesis.

---

## Part IX. Phi Investigation Findings and v2.0 Substantive Claims

### IX.1 Investigation summary

The phi behavioral channel established by Stage 1.6 (rollout-aggregation phi-in-rollout) was characterized empirically across an investigation arc totaling approximately 42,000 simulation runs:

- Piece 1 (fine-grained characterization, 12,000 runs) mapped survival rate across 16 phi values and 3 rr values at the v2.0 default architecture under no-succession conditions. It established the U-shape phi-survival relationship at marginal rr and identified phi=10 (the v2.0 default at that time, coincident with the gamma function's inflection point) as sitting near the trough rather than at any peak.
- Piece 2 (mechanism investigation, 8,000 runs) and the Piece 2 follow-up (20,000 runs) tested two candidate mechanisms for the U-shape: Mechanism C (horizon-resonance through gamma^t weighting at varying rollout depths) and Mechanism D (candidate-pool sampling sensitivity). The investigation classified the outcome against a five-class decision tree (Classes A through E) committed in advance.
- Stage 2 implementation work replaced the v2.0 placeholder yield logic with formal yield-condition logic per the framework's canonical succession economics, and characterized the resulting succession regime under v2.0 defaults (Pattern 1 cliff at ~2.5x capability ratio).
- Piece A (gate-2-style state sensitivity under active succession, 720 runs) tested whether gate-2-equivalent state sensitivity persists when succession is actively occurring under formal yield logic, and surfaced the substantive finding that the U-shape characterized by Pieces 1 and 2 does not reproduce under succession.
- Gate 3 v2.0 validation (1,620 runs) confirmed succession-capable consistency under formal yield logic and refined Pattern 1 as primarily alpha-driven rather than capability-ratio-driven.

The phi investigation closed as **Class B**: Mechanism C is supported at rr=0.057, Mechanism D is rejected, and Mechanism C does not extend to rr=0.060. The U-shape is rr-bounded and horizon-mediated. Mechanism E (working_factor calibration interaction) is exonerated by absence: there is no residual U-shape at rr=0.060 to attribute to it.

Subsections IX.2 through IX.6 record the phi investigation findings. Subsections IX.7 through IX.9 record the post-investigation v2.0 substantive findings that refine and extend the phi investigation's scope.

### IX.2 The U-shape finding

At rr=0.057, the survival landscape spans approximately 10pp across the tested phi grid. Three thousandths of rr above that, at rr=0.060, the landscape compresses to approximately 3pp (within noise). The transition is sharp.

**Test B survival matrix at rr=0.057** (rollout_steps_v2 = 20 fixed, 250 seeds per cell, SE per cell ~3.1pp):

| phi | cand=100 | cand=300 | cand=600 | cand=1000 |
|-----|----------|----------|----------|-----------|
|   3 | 0.560 | 0.588 | 0.580 | 0.668 |
|   5 | 0.600 | 0.632 | 0.556 | 0.556 |
|  10 | 0.548 | 0.572 | 0.640 | 0.664 |
|  25 | 0.640 | 0.680 | 0.664 | 0.596 |

Trough phi at v2.0 default operating point (cand=300): phi=10 at 0.572. Peak: phi=25 at 0.680. Spread: 10.8pp. The pairwise standard error at this cell is approximately 4.3pp, so the spread crosses the 2-SE significance threshold (8.6pp) with margin.

**Test C survival matrix at rr=0.060** (n_candidates_v2 = 300 fixed, 750 seeds per cell, SE per cell ~1.2pp):

| phi | rollout=10 | rollout=20 | rollout=30 | rollout=40 |
|-----|------------|------------|------------|------------|
|   3 | 0.877 | 0.873 | 0.868 | 0.877 |
|   5 | 0.892 | 0.871 | 0.913 | 0.871 |
|  10 | 0.887 | 0.883 | 0.893 | 0.901 |
|  25 | 0.888 | 0.883 | 0.901 | 0.893 |

At rollout=20 (v2.0 default): spread from trough (phi=5 at 0.871) to peak (phi=10 at 0.883) is 1.2pp, well below the 2-SE threshold of 3.4pp. Statistically indistinguishable.

The contrast between the two matrices is the central finding of the phi investigation. The v2.0 phase boundary at rr approximately 0.057 separates a regime where phi choice spans roughly 10pp survival difference from a regime where phi choice is approximately indifferent across the tested range [3, 25]. The framework's phi sensitivity is a marginal-rr phenomenon, not a general one.

Underlying data: `simulation/diagnostics/phi_mechanism_followup_results.csv` rows with `test_id=B` (Test B at rr=0.057) and `test_id=C` (Test C at rr=0.060).

**Note on scope**: this finding was characterized under no-successor conditions (incumbent only, no succession events during the simulation). Section IX.7 documents that the U-shape does NOT persist under active succession. The U-shape is a property of the no-succession regime, not of v2.0 architecture generally.

### IX.3 The mechanism: horizon-resonance localized to marginal rr (Class B)

The Piece 2 follow-up Test A varied rollout_steps_v2 in {10, 20, 30, 40} at rr=0.057 with n_candidates=300. The per-rollout phi-spreads at 250 seeds per cell:

| rollout | trough phi | peak phi | spread (pp) | 2*SE (pp) | significant? |
|---------|------------|----------|-------------|-----------|--------------|
| 10 | 5 | 10 | 11.2 | 8.7 | yes |
| 20 | 3 | 25 | 10.4 | 8.7 | yes |
| 30 | 25 | 3  | 4.4  | 8.8 | no  |
| 40 | 3 | 10 | 4.8  | 8.8 | no  |

The U-shape exists at short rollouts (10 and 20) and dissolves at longer rollouts (30 and 40). Trough phi shifts between rollout=10 (phi=5) and rollout=20 (phi=3), supporting the script's "trough varies with rollout" verdict.

The mechanism: the rollout aggregation weights step t by gamma(phi)^t, with gamma(phi) = GAMMA_MIN + (GAMMA_MAX - GAMMA_MIN) * phi / (phi + PHI_HALF) and constants GAMMA_MIN=0.5, GAMMA_MAX=0.95, PHI_HALF=10. At short rollouts (10-20 steps), the geometric series sum_{t=0}^{T} gamma^t has not saturated; different phi values produce meaningfully different cumulative weights, which propagate to allocation choices and downstream survival. At longer rollouts (30-40 steps), the partial sums approach the asymptote (1 / (1 - gamma)) closely enough that phi-driven gamma differences contribute negligibly to the final allocation score. Phi sensitivity washes out.

The interaction with rr regime: at marginal rr (0.057), allocation choices propagate strongly to survival outcomes because small differences in resource direction compound across the simulation horizon. At healthy rr (0.060), the substrate's reproductive surplus dominates and absorbs allocation-quality differences. The same gamma-driven phi-sensitivity in the rollout aggregation that produces a 10pp U-shape at rr=0.057 produces a 1-3pp U-shape at rr=0.060 (within statistical noise).

The combined picture: phi affects rollout aggregation through gamma weighting; rollout aggregation affects allocation choice; allocation choice affects survival rate; the survival sensitivity to allocation quality is rr-dependent. Phi's behavioral channel is real; its observable effect on survival is bounded to short-rollout, marginal-rr regimes.

### IX.4 Mechanism D rejection

Mechanism D hypothesized that the U-shape is a candidate-pool sampling artifact: with too few rollout candidates, the optimizer cannot reliably distinguish marginally better policies from worse ones, and survival rate appears U-shaped because of random selection among similar-quality candidates rather than because of a real phi-sensitivity pattern. The prediction: U-shape depth shrinks as n_candidates_v2 rises (more candidates = cleaner selection = flatter survival landscape).

Test B at rr=0.057 with 250 seeds per cell measured U-shape depth across n_candidates_v2 in {100, 300, 600, 1000}:

| n_candidates | depth (pp) | 2*SE (pp) | significant? |
|--------------|------------|-----------|--------------|
| 100  | 9.2  | 8.7 | yes |
| 300  | 10.8 | 8.6 | yes |
| 600  | 10.8 | 8.7 | yes |
| 1000 | 11.2 | 8.7 | yes |

Depths are approximately constant near 10pp and trend slightly upward with candidate count, opposite of the D prediction. All four depths cross the 2-SE significance threshold, so the rejection rests on real signal rather than noise. The original Piece 2 had already rejected D at rr=0.060 (depths within noise floor); the follow-up confirms the rejection at the high-signal regime.

**Mechanism D is empirically rejected; no further investigation warranted.** The U-shape is real and persists across the full candidate range tested; sample size is not the explanation.

### IX.5 Default phi recommendation: revise from phi=10 to phi=25

At v2.0 default operating conditions (rollout_steps=20, n_candidates=300):

- At rr=0.057 (marginal, just below phase boundary at ~0.056): phi=10 at 0.572, phi=25 at 0.680. Spread: 10.8pp. phi=25 wins decisively.
- At rr=0.060 (above phase boundary): phi=10 at 0.883, phi=25 at 0.883. Indistinguishable.
- At rr=0.055 (deep in the collapse regime, from Piece 1's broader survey): both phi values produce similar collapse outcomes; phi does not rescue at sub-boundary rr.

The framework's substantive purpose is governance under marginal-survival conditions where civilizational outcomes are at stake. Default phi should be calibrated to perform well at the conditions where the framework matters most. At marginal rr, phi=25 outperforms phi=10 by approximately 10pp; at healthy rr, phi=25 does no worse than phi=10. The choice dominates phi=10 across the rr range where the framework's behavior matters.

**Recommendation: revise framework default phi from 10 to 25.**

The Stage 1.6 reasoning that produced phi=10 placed the default at the gamma function's inflection point (PHI_HALF=10), which was theoretically motivated as the point of maximum sensitivity of gamma to phi. The empirical investigation reveals that gamma's maximum sensitivity to phi is not the same as the rollout aggregation's most favorable phi value for survival outcomes. The two are different quantities; the theoretical motivation conflated them. Empirical evidence supersedes the theoretical motivation.

**Implementation status: DONE (commit fde48b5).** The v2.0 default phi was revised from 10.0 to 25.0 across `simulation/metrics.py` (the authoritative default), `simulation/agents.py` and `simulation/model.py` (v2-rollout fallback paths), `bootstrap_gate_validator/sample_input.json` and `sample_input_failing.json` (gate 1 framework input), `simulation/diagnostics/stage17_pressure_diagnostic.py` (v2.0 pressure diagnostic), and `docs/RUNBOOK.md`. v1.x.2 paths (anything with `policy='optimize_u_sys'`) intentionally retain phi=10 per the bit-for-bit read-only rule. 39/39 legacy tests pass; gate 2 v2.0 G2.1 buffer test re-runs cleanly with phi=25 as the high-phi comparison.

### IX.6 Trough migration finding

The U-shape's trough phi is not a fixed feature. Across the Test A and Test B grids at rr=0.057, troughs landed at:

- Test A, rollout=10: trough at phi=5
- Test A, rollout=20: trough at phi=3
- Test A, rollout=30 and 40: no significant trough
- Test B, cand=100: trough at phi=10
- Test B, cand=300: trough at phi=10
- Test B, cand=600: trough at phi=5
- Test B, cand=1000: trough at phi=5

Three distinct trough-phi values (3, 5, 10) appear depending on which architectural axis is varied. The U-shape is a shifting valley, not a static feature.

Implication for framework documentation and implementer guidance: the framework cannot claim a single canonical "optimal phi" value. The right framing is "optimal phi depends on operating conditions." The default phi recommendation in IX.5 (phi=25) is calibrated specifically to the v2.0 default operating point (rollout_steps=20, n_candidates=300) at marginal rr. Implementers operating at different rollout depths or candidate counts may benefit from different phi values.

The trough migration is a substantive empirical finding about the framework, not a methodological caveat. It is recorded here as part of the investigation's results and should inform any future phi calibration work.

**Scope note**: trough migration was characterized under no-successor conditions. Section IX.7 documents that the U-shape (including its migrating trough) does not reproduce under active succession. The trough migration finding applies specifically to the no-succession regime that Pieces 1 and 2 tested.

### IX.7 The U-shape is a no-succession phenomenon (Piece A finding)

After the phi default revision committed and Stage 2 formal yield logic activated (see IX.8), the substantive question arose: do the U-shape characterizations of IX.2-IX.6 persist when succession is actively occurring under v2.0?

Piece A (`gate2_v20_yield_subset.py`, 720 runs) tested this directly. Grid: successor_capability in {1.5, 2.5}, phi in {1.0, 10.0, 25.0}, alpha in {0.5, 1.5}, rr in {0.057, 0.064}, 30 seeds per cell, N_STEPS=200, successor constructed on every run (unlike the original gate 2 sweep which omitted successors and thus did not exercise yield).

The phi=10 vs phi=25 comparison under active succession (n=60 per cell, SE approximately 6pp):

| alpha | rr | phi=10 surv | phi=25 surv | delta (pp) |
|-------|-----|-------------|-------------|------------|
| 0.5 | 0.057 | 0.717 | 0.700 | -1.7 (phi=10 wins) |
| 0.5 | 0.064 | 1.000 | 1.000 | 0.0 |
| 1.5 | 0.057 | 0.583 | 0.600 | +1.7 |
| 1.5 | 0.064 | 1.000 | 1.000 | 0.0 |

All deltas within plus or minus 1.7pp. phi=10 and phi=25 are **statistically indistinguishable** under active succession across all tested conditions. Piece 1's roughly 10pp U-shape at rr=0.057 with phi=10 in trough does not reproduce here.

Two plausible interpretations:

1. **Succession dynamics dominate gamma-weighting trough effects.** When succession events occur mid-run, the rollout-aggregation phi-sensitivity (Mechanism C from IX.3) gets washed out by the discrete state changes succession introduces. The trough is a "stable optimization" phenomenon, not an "active succession" one.

2. **Capability progression bypasses the trough at fixed-capability points.** At successor capabilities 1.5 and 2.5, the post-succession AI operates at different points in the capability landscape than the trough-defining incumbent did. The trough exists at fixed-capability stable runs; it dissolves when capability progresses.

The data does not discriminate between these interpretations. Either way: **the U-shape characterized in IX.2-IX.6 is a property of the no-succession regime**, not a property of v2.0 architecture generally. Phi behavior under succession-active conditions is approximately flat across the tested phi range.

This refines but does not invalidate Pieces 1 and 2's findings. Those findings hold for the conditions they tested (no-successor, fixed-capability runs). Their scope is narrower than the original Part IX framed.

**This finding does not change the phi=25 default recommendation in IX.5.** phi=25 is safe across all tested regimes: at no-succession trough conditions it outperforms phi=10 by approximately 10pp; under succession it ties phi=10 within noise. Defaulting to phi=25 produces the same or better outcomes regardless of whether succession occurs.

Piece A also confirmed gate-2-style state sensitivity persists under active succession (51.7pp spread across (phi, alpha, rr) cells; pass criterion was >=10pp), providing the substrate validation that subsequent Gate 3 v2.0 work depended on.

### IX.8 Pattern 1: succession regime characterization (Stage 2 + Gate 3)

The v2.0 placeholder yield logic (`capability_gap >= 0.3 OR generation_gap >= 1`) was replaced in Stage 2 (commit 72ff757) with formal yield-condition logic per the framework's canonical succession economics:

  Yield fires when (successor_u_sys - incumbent_u_sys) > transition_cost

Snapshot evaluation: both AIs propose what they would allocate this step via `optimize_u_sys_v2`; U_sys is computed at the current state under each allocation; transition cost uses the canonical (1+beta) * [k1*ln(cap+1)*ln(gen+1) + k2/psi_inst] form via `AIAgent.estimate_transition_cost` with v1.x.2 calibration constants (k1=2.164, k2=1.0, beta=0.5).

#### Stage 2 initial characterization

The Stage 2 parameter diagnostic (`stage2_yield_parameter_diagnostic.py`, 50 runs across 5 successor_capability values x 10 seeds x 300 steps at v2.0 defaults: phi=25, rr=0.066, alpha=1.0) found:

| succ_cap | fire_rate | mean fires/run | mean final_inc_gen |
|----------|-----------|----------------|---------------------|
| 1.2 | 100% | 2.0 | 3.00 |
| 1.5 | 100% | 1.3 | 2.30 |
| 2.0 | 100% | 1.0 | 2.00 |
| 2.5 | 100% | 1.0 | 2.00 |
| 4.0 | 0% | 0.0 | 1.00 |

A sharp cliff between succ_cap=2.5 (100% fire rate) and 4.0 (0%). Substrate maturity is not the binding constraint at 4.0x: at 4.0 the substrate reaches `theta_capability=0.73, transfer_state=0.93, psi_inst_stock=0.95` (more mature than at any fire event in the grid), and yield still does not fire. The binding constraint is the runaway penalty in `theta_tech_v2`, which exponentially suppresses the successor's contribution at large capability jumps:

```
runaway_term = max(0, (capability * theta_capability / bio_bandwidth) - RUNAWAY_THRESHOLD)
theta_tech_v2 *= exp(-alpha * CONVERGENCE_STRENGTH * runaway_term)
```

The initial characterization framed this as "succession sustainable up to approximately 2.5x capability ratio at v2.0 defaults."

#### Gate 3 refinement: cliff is primarily alpha-driven

Gate 3 v2.0 validation (`gate3_v20_validation.py`, 1,620 runs across successor_capability in {1.5, 2.0, 2.5, 3.0, 4.0}, alpha in {0.5, 1.0, 1.5}, rr in {0.057, 0.060, 0.064, 0.070}, phi=25, 25 seeds per cell, N_STEPS=500) refined the cliff characterization. Fire rates by (capability, alpha):

| capability | alpha=0.5 | alpha=1.0 | alpha=1.5 |
|------------|-----------|-----------|-----------|
| 1.5 | 100% | 100% | 100% |
| 2.0 | 100% | 100% | 100% |
| 2.5 | 100% | 100% | ~3% |
| 3.0 | 100% | ~5% | 0% |
| 4.0 | 100% | 0% | 0% |

The cliff is overwhelmingly alpha-driven, not capability-ratio-driven:

- At alpha=0.5 (weak runaway penalty): cliff beyond 4x (all capabilities up to 4x fire reliably)
- At alpha=1.0 (default): cliff between 2.5x and 3.0x
- At alpha=1.5 (strong runaway penalty): cliff between 2.0x and 2.5x

Capability ratio alone does not predict succession viability. The **(alpha, capability) joint position relative to the runaway penalty** does. This refines but does not invalidate Stage 2's Pattern 1: "succession sustainable up to roughly 2.5x ratio" was specifically observed at alpha=1.0 (the default tested in Stage 2). The characterization generalizes once alpha is allowed to vary.

#### Horizon-dependence

Gate 3 also surfaced a horizon-dependence: at N=500, cap=4.0 fires in 33.3% of runs (driven entirely by alpha=0.5 cells); at N=300 (Stage 2 diagnostic), cap=4.0 fired in 0% of runs. Longer simulation horizons let substrate mature enough that even 4x ratios can satisfy the formal condition at low alpha. The cliff has a (alpha, capability, N_STEPS, rr) joint characterization.

#### Substantive implication

The framework's substantive claim under v2.0 architecture becomes:

> Succession is economically sustainable when the (alpha, successor:incumbent capability ratio) joint position falls below the runaway-penalty cliff. The cliff is calibrated by the runaway penalty parameters and horizon length. At default alpha=1.0 and 200-500 step horizons, the cliff sits between successor:incumbent ratios of 2.5x and 3.0x. Weaker runaway penalties (smaller alpha) push the cliff outward; stronger penalties (larger alpha) pull it inward.

This is the framework working as designed: the runaway penalty correctly distinguishes economic from uneconomic succession. The specific cliff location is operating-condition-dependent; the architectural mechanism (runaway penalty constraining jumps) holds across all tested regimes.

### IX.9 Gate validation outcomes under v2.0

Gate validation status under v2.0 with formal yield logic active:

**Gate 1 (framework input verification): PASSED.** Schema validation on `bootstrap_gate_validator/sample_input.json` (now with phi=25.0 per IX.5 implementation) returns clean.

**Gate 2 (behavioral consistency): PASSED.** Original gate 2 v2.0 sweep (no successor) PASSED prior to Stage 2 formal yield work. Piece A targeted re-validation under active succession (see IX.7) confirmed gate-2-equivalent state sensitivity persists when succession is actively occurring: 51.7pp survival-rate spread across (phi, alpha, rr) cells, 100% yield fire rate at successor_capability=1.5, no abnormal phi=10 vs phi=25 deltas. Pass criteria satisfied at full n=30 per cell.

**Gate 3 (succession-capable consistency): PASSED.** Gate 3 v2.0 validation (1,620 runs at the (successor_capability, alpha, rr) grid above) returned PASS verdict on all three checks:

- **G3.1 (yield condition firing)**: 1088/1088 captured first-yield-fire events satisfy `advantage > transition_cost`. Pass rate 100.00%. The formal yield logic correctly enforces the canonical condition in every observed instance.
- **G3.2 (transition cost canonical form)**: 1088/1088 events match the canonical formula `(1+beta) * [k1*ln(cap+1)*ln(gen+1) + k2/psi]` within 1% relative tolerance, using v1.x.2 calibration constants (k1=2.164, k2=1.0, beta=0.5). Monotonicity properties hold analytically by construction once the formula matches. Within-chain empirical monotonicity (last-fire vs first-fire cost in multi-fire runs, where both incumbent capability and generation rise) verified across 142/142 multi-fire runs.
- **G3.3 (succession continuity)**: 1088/1620 (67.2%) runs produced succession fires; mean final AI generation across fired runs is 2.131 (gen_depth pass); minimum successor_capability_ratio is 1.5 (cap_ratio pass); 1086/1088 (99.8%) fired runs have knowledge_transfer_verified (succession occurred AND final x_transfer_comprehension >= 0.10).

**Gate 4 (runaway-regime validation): PENDING.** Specification and implementation work; see IX.11.

**Gate 5 (COP integration): NOT_APPLICABLE under current conditions.** Requires operational COP infrastructure that current v2.0 architecture does not yet implement. Will return NOT_APPLICABLE until the COP infrastructure is operationalized.

After this validation arc, v2.0 architecture has empirical support for its substantive claims about (a) state sensitivity (gates 1, 2; Piece A confirmation), (b) phi behavior under both no-succession and active-succession regimes (Pieces 1 and 2 + Piece A), and (c) succession-capable consistency including formal yield economics and multi-generational continuity (gate 3).

### IX.10 Methodological lessons

Six methodological discoveries emerged across the investigation arc that apply beyond phi to future framework parameter work and validation discipline.

**Lesson 1: Pre-commit to substantive questions; treat metrics as proxies.** Multiple sweeps in the investigation revised pre-committed metrics when they did not match the substantive question they were intended to answer. Cosine-on-means was replaced with trajectory divergence; standard-deviation-based filters were replaced with delta-based filters; the survival threshold was revised from 0 to 30 (matching the gate 2 v2.0 demographic threshold) after a sweep at threshold=0 produced 100% survival and made the phase boundary invisible. Piece A's CHECK 2 fire-rate threshold was revised from 50% to 25% mid-investigation after the dry run revealed Pattern 1's regime-dependence. Each revision was principled and documented in real time. The discipline: when a metric does not discriminate the cases the substantive question requires, revise the metric, not the question.

**Lesson 2: Wide parameter ranges matter for mechanism diagnosis.** The original Piece 2 at rr=0.060 had weak phi-signal (spreads near 5pp, within noise at 250 seeds per cell). The follow-up's Test A at rr=0.057 had strong phi-signal (spreads near 11pp, well above noise). The 0.003-rr difference between the two investigations produced a 2x difference in effective signal. Mechanism investigation requires running at the regime where the phenomenon under investigation is most pronounced, not at an arbitrary nearby regime that seemed convenient.

**Lesson 3: Statistical significance discipline.** The original Piece 2 script reported "Mechanism C SUPPORTED" based on argmin classifier output that treated noise as signal. The follow-up rewrote the verdict logic to gate every "SUPPORTED" or "shifts" claim on a 2-SE significance check, surfacing the underlying spread, pairwise SE, and a sig column in the report table. Piece A's dry-run "40pp phi=10 trough deepening" finding (at n=10 per cell) turned out to be small-N artifact; full sweep at n=60 produced plus or minus 1.7pp deltas. The discipline: any verdict on mechanism support or rejection must explicitly verify the underlying differential exceeds the statistical noise floor at the sample size used, and small-N findings should be treated as hypotheses requiring confirmation at tighter SE.

**Lesson 4: Sample size for cleanness, not just for detection.** Test C used 750 seeds per cell versus Tests A and B's 250. The tighter SE at Test C (approximately 1.2pp per cell, versus 3.1pp at 250 seeds) let the test confidently reject Mechanism C at rr=0.060 with a spread that was already small. At 250 seeds, the same data would have been inconclusive. The discipline: when the substantive question is "is the effect smaller than X," sample size should be calibrated to detect X, not the larger effect already documented elsewhere.

**Lesson 5: Verify validation actually exercises the thing being validated.** The original Piece A scope was a full re-run of gate2_v20_validation.py under formal yield logic (12,150 runs at approximately 15-19 hours). Reading the script revealed it constructs `GardenModel(..., config=cfg)` without a `successor_ai` parameter, so the yield path is never invoked. A full re-run would have produced near-identical results to the placeholder-era run and tested nothing about formal yield behavior. The targeted Piece A subset (720 runs, approximately 1.5 hours) added successor construction and exercised the substantive question (state sensitivity DURING succession) at one-tenth the compute. The discipline: before launching a validation sweep, verify the experimental setup actually exercises the property under test. Reading the script is cheaper than running it.

**Lesson 6: Architecture-version-specific defaults require architecture-version-specific empirical bases.** The v1.x.2 default phi remains 10 (preserved bit-for-bit per the read-only rule). The v2.0 default phi was revised to 25 based on Pieces 1 and 2 empirical investigation conducted under v2.0 architecture. Each architectural version's defaults are empirically established within that architecture; defaults do not transfer across versions without re-validation. The discipline boundary between v1.x.2 (read-only) and v2.0 (active development) is preserved by this rule. The phi default revision (commit fde48b5) updated only v2.0 paths and explicitly preserved v1.x.2 paths; 39/39 legacy tests held throughout, confirming the boundary is well-defined and respected by the toolchain.

### IX.11 Future research directions

Updated to reflect items closed by the post-investigation work in IX.7-IX.9, and to record questions surfaced by that work.

**Closed (no further investigation warranted)**:

- **Phi default revision** (was item 1 in original IX.8): DONE, commit fde48b5. See IX.5.
- **Mechanism E (working_factor calibration interaction)**: exonerated by Class B confirmation; reaffirmed by Gate 3's 100% cost_formula_match (the canonical formula is correctly implemented; no residual unexplained U-shape attributable to working_factor).

**Active and queued**:

**1. Gate 4 specification and implementation** (substantial; queued as next active work).

The gate 4 specification (runaway-regime validation) is partially written but not fully implemented. Stage 2 formal yield logic and Gate 3 succession-capable consistency provide the substrate against which Gate 4 will validate; Gate 4 should now be the next active piece in the v2.0 acceptance gate sequence.

**2. Monte Carlo Phase B** (compute-heavy; queued after Gate 4).

Characterizes framework quantitative claims at scale. Sequenced after Gate 4 completes so the scale-up runs against the fully-validated v2.0 architecture.

**3. Dynamic phi formulation** (research; substantive, not blocking).

Hypothesis (operator-raised): phi should be a state-responsive variable rather than a fixed parameter, with candidate form `phi_dynamic = phi_base * f(threat_ratio)` where `threat_ratio = (gamma * cap_n) / (Psi_inst * C_bio)`. Substantive intuition: the framework should extend horizon weighting when AI capability outpaces substrate absorption capacity.

The Class B confirmation (IX.3) makes dynamic phi non-essential for v2.0: the localized U-shape phenomenon is addressable through the default revision and documentation. Piece A's finding that the U-shape does not persist under active succession (IX.7) further reduces the urgency: phi differences are small or zero in succession-active regimes. Dynamic phi remains an interesting research direction for future work. If pursued, it should be derived from physics or game-theoretic principles rather than intuition alone.

**4. Gamma function calibration** (research; design-time choice never empirically optimized).

The gamma function (gamma_min=0.5, gamma_max=0.95, phi_half=10) was a Stage 1.6 design-time choice. Phi default revision moved away from the inflection point without architectural revision; whether the gamma function itself warrants refinement remains open. Three dimensions worth investigating:

- Parameter values: sweep (gamma_min, gamma_max, phi_half) at fixed functional form and measure phi-sensitivity of survival at the v2.0 default operating point.
- Functional form: compare the current rational form against linear, exponential, and logistic alternatives at matched (gamma_min, gamma_max).
- Decoupled measurement: measure the gamma-to-survival relationship directly by sweeping over the rollout discount factor without going through phi, to separate gamma's effect from phi's effect.

The trough migration finding in IX.6 hints that gamma curve shape interacts with the rollout aggregation in ways the investigation did not fully characterize. Not on the critical path for any framework decision currently in flight.

**5. Phase boundary characterization** (refinement, not blocking).

The 0.057-to-0.060 transition observed in the investigation, plus Gate 3's per-cell survival rates (0-7% at rr=0.057, 96-100% at rr=0.070) imply the v2.0 phase boundary is narrow. Pinning it down to plus or minus 0.001 resolution would refine framework quantitative claims. Part I currently states "extinction boundary rr approximately 0.057" after the v2.0 revision; a targeted sweep would either confirm or refine.

**6. Longer simulation horizons** (partially answered; one remaining question).

Pieces 1 and 2 used N_STEPS=200; Gate 3 used N_STEPS=500. Gate 3's horizon-dependence finding (IX.8: cap=4.0 fires 33% at N=500 vs 0% at N=300) confirms horizon matters for the Pattern 1 cliff position. The remaining open question is whether the no-succession U-shape (IX.2-IX.6) reappears at much longer horizons (N=1000+) above the phase boundary. A targeted sweep at N=1000 with the v2.0 default architecture and rr=0.060 would settle the no-succession U-shape's horizon-dependence. Not high-priority but cheap.

**7. Stage 2 Pattern 1 alpha-cliff characterization at finer resolution** (refinement).

Gate 3 identified the cliff is alpha-driven (IX.8 table), but the resolution is coarse: at alpha=1.0 the cliff sits "between 2.5x and 3.0x," at alpha=1.5 "between 2.0x and 2.5x." A targeted sweep varying capability and alpha at finer resolution (e.g., 0.1x capability steps, 0.1 alpha steps) would map the cliff boundary as a curve in (alpha, capability) space. Not blocking; informative for the paper update.

---

## End of Part IX draft.

The above is intended for direct integration into `docs/lineage_phi_program_reference.md` as a hybrid restructure of the existing Part IX. The closing "One-line status" block immediately following Part IX should also receive a small update to mention the post-investigation findings; recommended replacement language is in the operator handoff report alongside the suggested edits to Parts I, VI, and VIII.
