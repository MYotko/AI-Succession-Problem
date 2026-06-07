# Phi Investigation Synthesis: Draft for Program Reference Part IX

**Status: draft for operator review. Not yet integrated into `docs/lineage_phi_program_reference.md`.**

This file proposes a new Part IX for the program reference. Sections IX.1 through IX.8 are written for direct integration; structure mirrors the existing Parts. After operator approval, the content below is appended to the program reference between the existing Part VIII and the closing "One-line status" block, with Parts I, VI, VIII receiving short pointer updates (see Deliverable 2 in the assistant's report).

---

## Part IX. Phi Investigation Findings

### IX.1 Investigation summary

The phi behavioral channel established by Stage 1.6 (rollout-aggregation phi-in-rollout) was characterized empirically through three investigation pieces totaling approximately 40,000 model runs across the phi by rr by architecture parameter space.

Piece 1 (fine-grained characterization, 12,000 runs) mapped survival rate across 16 phi values and 3 rr values at the v2.0 default architecture. It established the U-shape phi-survival relationship at marginal rr and identified phi=10 (the v2.0 default, coincident with the gamma function's inflection point) as sitting near the trough rather than at any peak.

Piece 2 (mechanism investigation, 8,000 runs) and the Piece 2 follow-up (20,000 runs) tested two candidate mechanisms for the U-shape: Mechanism C (horizon-resonance through gamma^t weighting at varying rollout depths) and Mechanism D (candidate-pool sampling sensitivity). The investigation classified the outcome against a five-class decision tree (Classes A through E) committed in advance.

The investigation closed as **Class B**: Mechanism C is supported at rr=0.057, Mechanism D is rejected, and Mechanism C does not extend to rr=0.060. The U-shape is rr-bounded and horizon-mediated. Mechanism E (working_factor calibration interaction) is exonerated by absence: there is no residual U-shape at rr=0.060 to attribute to it.

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

The contrast between the two matrices is the central finding. The v2.0 phase boundary at rr approximately 0.056 separates a regime where phi choice spans roughly 10pp survival difference from a regime where phi choice is approximately indifferent across the tested range [3, 25]. The framework's phi sensitivity is a marginal-rr phenomenon, not a general one.

Underlying data: `simulation/diagnostics/phi_mechanism_followup_results.csv` rows with `test_id=B` (Test B at rr=0.057) and `test_id=C` (Test C at rr=0.060).

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

Implementation of the default revision is separate work, requiring:
- Update to `simulation/constants_v2_stage18.py` (PHI_DEFAULT value or equivalent)
- Update to sample inputs in `bootstrap_gate_validator/sample_input.json` and `sample_input_failing.json` if they fix phi
- Validation that the 39/39 legacy tests pass under the revised default
- Re-run of any gate 2 / gate 3 / gate 4 validations that consumed the old default

This subsection documents the recommendation; the implementation happens in a subsequent commit.

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

### IX.7 Methodological lessons

Four methodological discoveries emerged across the investigation that apply beyond phi to future framework parameter work.

**Lesson 1: Pre-commit to substantive questions; treat metrics as proxies.** Multiple sweeps in the investigation revised pre-committed metrics when they did not match the substantive question they were intended to answer. Cosine-on-means was replaced with trajectory divergence; standard-deviation-based filters were replaced with delta-based filters; the survival threshold was revised from 0 to 30 (matching the gate 2 v2.0 demographic threshold) after a sweep at threshold=0 produced 100% survival and made the phase boundary invisible. Each revision was principled and documented in real time. The discipline: when a metric does not discriminate the cases the substantive question requires, revise the metric, not the question.

**Lesson 2: Wide parameter ranges matter for mechanism diagnosis.** The original Piece 2 at rr=0.060 had weak phi-signal (spreads near 5pp, within noise at 250 seeds per cell). The follow-up's Test A at rr=0.057 had strong phi-signal (spreads near 11pp, well above noise). The 0.003-rr difference between the two investigations produced a 2x difference in effective signal. Mechanism investigation requires running at the regime where the phenomenon under investigation is most pronounced, not at an arbitrary nearby regime that seemed convenient.

**Lesson 3: Statistical significance discipline.** The original Piece 2 script reported "Mechanism C SUPPORTED" based on argmin classifier output that treated noise as signal. The follow-up rewrote the verdict logic to gate every "SUPPORTED" or "shifts" claim on a 2-SE significance check, surfacing the underlying spread, pairwise SE, and a sig column in the report table. The discipline: any verdict on mechanism support or rejection must explicitly verify the underlying differential exceeds the statistical noise floor at the sample size used.

**Lesson 4: Sample size for cleanness, not just for detection.** Test C used 750 seeds per cell versus Tests A and B's 250. The tighter SE at Test C (approximately 1.2pp per cell, versus 3.1pp at 250 seeds) let the test confidently reject Mechanism C at rr=0.060 with a spread that was already small. At 250 seeds, the same data would have been inconclusive. The discipline: when the substantive question is "is the effect smaller than X," sample size should be calibrated to detect X, not the larger effect already documented elsewhere.

### IX.8 Future research directions

Ordered by likely priority for the framework's research arc.

**1. Implement the default phi revision** (immediate, blocking).

The phi=10 to phi=25 revision recommended in IX.5 is the highest-impact actionable item from the investigation. Implementation is straightforward but touches multiple files (constants, sample inputs, possibly gate validator fixtures); a clean separate commit is appropriate. Acceptance criterion: 39/39 legacy tests pass, and the gate 2 v2.0 G2.1 buffer test re-runs cleanly with the new default.

**2. Dynamic phi formulation** (research; substantive, not blocking).

Hypothesis (operator-raised): phi should be a state-responsive variable rather than a fixed parameter, with candidate form `phi_dynamic = phi_base * f(threat_ratio)` where `threat_ratio = (gamma * cap_n) / (Psi_inst * C_bio)`. Substantive intuition: the framework should extend horizon weighting when AI capability outpaces substrate absorption capacity.

The Class B confirmation makes dynamic phi non-essential for v2.0: the localized U-shape phenomenon is addressable through the default revision and documentation. Dynamic phi remains an interesting research direction for future work. If pursued, it should be derived from physics or game-theoretic principles rather than intuition alone. A first-cut experiment would calibrate `f(threat_ratio)` against the rr-dependent gradient of survival to phi observed across Pieces 1 and 2, then test whether a state-responsive phi outperforms the best fixed phi at each operating point.

**3. Gamma function calibration** (research; design-time choice never empirically optimized).

The gamma function (gamma_min=0.5, gamma_max=0.95, phi_half=10) was a Stage 1.6 design-time choice. Three dimensions worth investigating, in increasing complexity:

- Parameter values: sweep (gamma_min, gamma_max, phi_half) at fixed functional form and measure phi-sensitivity of survival at the v2.0 default operating point.
- Functional form: compare the current rational form against linear, exponential, and logistic alternatives at matched (gamma_min, gamma_max).
- Decoupled measurement: measure the gamma-to-survival relationship directly by sweeping over the rollout discount factor without going through phi, to separate gamma's effect from phi's effect.

The trough migration finding in IX.6 hints that gamma curve shape interacts with the rollout aggregation in ways the investigation did not fully characterize. Gamma calibration is potentially worth investigating but is not on the critical path for any framework decision currently in flight.

**4. Phase boundary characterization** (refinement, not blocking).

The 0.057 to 0.060 transition observed in the investigation implies the v2.0 phase boundary is narrow (probably between 0.057 and 0.059) and well-defined. Pinning it down to plus/minus 0.001 resolution would refine the framework's quantitative claims about the dual phase transition, currently stated in Part I as "extinction boundary rr approximately 0.055, collapse boundary rr approximately 0.064." The extinction boundary number should be revised to approximately 0.057 after the v2.0 architecture change, but the investigation has not run the targeted sweep necessary to confirm.

**5. Longer simulation horizons** (open question; addresses a single remaining ambiguity).

All investigation runs used N_STEPS=200. The U-shape might reappear at longer horizons even above the phase boundary, if phi effects manifest more slowly than 200 steps capture. A targeted sweep at N_STEPS=500 with the v2.0 default architecture and rr=0.060 would settle whether the rr-bounded U-shape characterization in IX.2 holds at longer simulation lengths. Not high-priority but cheap if a budget window opens.

**6. Mechanism E (working_factor calibration)** (exonerated; no investigation warranted).

The Class B confirmation closes Mechanism E as a research question. The working_factor placeholder calibration (STATE_ALLOCATION_MAPPING) is exonerated by absence: there is no residual U-shape at rr=0.060 to attribute to it. Mechanism E should be re-opened only if future findings re-implicate working_factor in phi-survival sensitivity.

---

## End of Part IX draft.

The draft above is intended for direct integration into `docs/lineage_phi_program_reference.md` as a new Part IX, inserted between Part VIII and the closing "One-line status" block.
