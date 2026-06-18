# Draft: Program Reference Part X (Monte Carlo Phase B)

Status: proposed content for the program reference. Do NOT merge directly. For operator review.

Date: 2026-06-18

Placement decision (operator-confirmed): new Part X immediately after Part IX. Part VIII (immediate next actions) stays in place. This draft also specifies in-place refinements to IX.2 and IX.9, and edits to Part I and Part VIII to reference Part X.

The draft follows the program reference's existing prose style. Note for the editor: the program reference body uses em-dashes; this draft avoids them per the deliverable constraint, so light punctuation harmonization at merge time is expected.

---

## Part X. Monte Carlo Phase B: Quantitative Validation at Scale

### X.1 Investigation summary

Monte Carlo Phase B is the quantitative-characterization arc that follows the phi mechanism investigation (Part IX). Where Part IX investigated mechanism (why phi behaves as it does, where the U-shape lives, what drives the succession cliff), Phase B measures v2.0 behavior at scale across three categories: the survival landscape (Category A), succession dynamics (Category B), and the COP cost-audit probe (Category C). All three ran under `optimize_u_sys_v2` formal yield logic.

Totals: 29,400 completed rows, 0 errors. Category A 10,800 rows (100 seeds per cell), Category B 10,500 rows (75 seeds per cell), Category C 8,100 rows (150 seeds per cell). Legacy verification after Category C: 39 passed (`test_invariants.py`, `test_cop.py`, `test_refactor_1x.py`). Implementation: `simulation/diagnostics/monte_carlo_phase_b.py`. Summaries: `monte_carlo_phase_b_summary.md` and the three category files.

Phase B closes the v2.0 empirical characterization arc (modulo the Gate 4 specification dependency). It produces the quantitative substrate the paper update draws from.

### X.2 Survival landscape characterization (Category A)

Grid: rr in {0.055, 0.056, 0.057, 0.058, 0.059, 0.060, 0.062, 0.064, 0.066}, phi in {5, 10, 25, 100}, alpha in {0.5, 1.0, 1.5}, 100 seeds per cell. Aggregate survival by rr (n=1,200 each):

| rr | survival | SE |
|---|---|---|
| 0.055 | 0.2% | 0.12pp |
| 0.056 | 0.9% | 0.28pp |
| 0.057 | 1.1% | 0.30pp |
| 0.058 | 2.9% | 0.49pp |
| 0.059 | 4.8% | 0.62pp |
| 0.060 | 12.2% | 0.95pp |
| 0.062 | 34.5% | 1.37pp |
| 0.064 | 60.8% | 1.41pp |
| 0.066 | 86.5% | 0.99pp |

The v2.0 survival-rate transition is sharp and rr-driven. The steep climb runs from rr=0.060 to rr=0.066, and the 50% survival inflection sits near rr=0.063 (between 34.5% at rr=0.062 and 60.8% at rr=0.064).

This refines the v2.0 phase boundary location. The earlier characterization (IX.2, Part I) placed the v2.0 phase boundary near rr=0.057 on the basis of Gate 3's coarser four-value rr grid. Phase B's finer nine-value grid shows rr=0.057 is the bottom of the collapse zone at 1.1% aggregate survival, with the actual survival-rate transition occurring at rr=0.060 to 0.066. The refinement does not change the dual-phase-transition claim; it sharpens the v2.0 boundary location. See the IX.2 refinement note in this draft.

Phi is a weak driver across the broad landscape. Within any fixed rr column, survival varies little across phi relative to the rr-driven transition. This is consistent with the Class B finding (IX.3) that phi sensitivity is a marginal-rr, short-horizon phenomenon, not a general survival driver. Source: `monte_carlo_phase_b_a_summary.md`, `monte_carlo_phase_b_a_results.csv`.

### X.3 Succession dynamics characterization (Category B)

Grid: rr in {0.057, 0.060, 0.064, 0.070}, alpha in {0.5, 0.75, 1.0, 1.25, 1.5}, successor_capability in {1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0}, 75 seeds per cell.

Pattern 1 is confirmed at Phase B scale, and the alpha-driven cliff migration is characterized at finer alpha resolution than Gate 3:

| alpha | cliff structure |
|---|---|
| 0.50 | No hard cliff through 5.0x. Fire rate 88.0% to 96.0% at 5.0x. |
| 0.75 | Cliff at 4.0x. Fire rate 100% through 3.0x, 0% at 4.0x and above. |
| 1.00 | Cliff at 3.0x. Fire rate 98.7% to 100% at 2.5x, then 4.0% to 13.3% at 3.0x, 0% above. |
| 1.25 | Transitional 2.5x band. Fire rate 30.7% to 49.3% at 2.5x, 0% at 3.0x and above. |
| 1.50 | Cliff at 2.5x. Fire rate 100% through 2.0x, then 0% to 1.3% at 2.5x, 0% above. |

The alpha=0.75 and alpha=1.25 points fill the cliff-migration curve between the Gate 3 alpha values (IX.8). Multi-generational continuity concentrates below the cliff: fire rate at or near 100%, transfer-verified at or near 1.0, mean final generation 2 to 3.7. Above the cliff, runs remain at generation 1 and the mean yield margin is negative (down to roughly -4.6 at the most-penalized cells). Suppression above the cliff is economic rejection by the formal yield condition, not implementation failure. This is the runaway penalty working as designed (IX.8). Source: `monte_carlo_phase_b_b_summary.md`, `monte_carlo_phase_b_b_results.csv`.

### X.4 COP protective effects under v2.0 (Category C)

Grid: rr in {0.057, 0.060, 0.064}, alpha in {0.5, 1.0, 1.5}, successor_capability in {1.5, 2.5, 3.0}, `cop_cost_audit` in {True, False}, 150 seeds per cell. Policy `optimize_u_sys_v2`; `beta_cap` at default 1.5; no adversary.

Aggregate survival: audit False 25.4% (SE 0.68pp), audit True 24.9% (SE 0.68pp). Delta (True minus False) is -0.47pp with pair SE 0.96pp, below 2 SE. By rr the delta is uniformly small (-0.30pp, -0.37pp, -0.74pp at rr 0.057, 0.060, 0.064). Cell-level, only 2 of 27 cells cross 2 SE, with opposite signs, consistent with chance (about 1.4 expected false crossings). The finding is a homogeneous null.

This is a benign-conditions baseline, not a measurement of COP protection. The `cop_cost_audit` toggle (`model.py:748-767`) defends against an incumbent inflating transition cost via a `beta_cap` premium; its protective value requires both an adversary and a large `beta_cap`. Category C supplied neither, so the near-zero delta is the result the framework predicts.

This must not be read as a failure of the COP claim. The v1.x.2 73.9pp COP protective delta was measured under different conditions entirely: adversarial `block_succession` with `beta_cap` swept 1.0 to 10.0, n=4,000 (`monte_carlo.py` `_run_single_adv_mc`). Phase B did not test that. The interpretation is C-primary (conditions and measured-object difference), A-secondary (`cop_cost_audit` is only the WP4 cost-arbitration slice of the full COP architecture), B-unsupported (the two were never like-for-like). Gate 5 remains NOT_APPLICABLE. Full treatment: `simulation/diagnostics/cop_finding_framing.md`. Source: `monte_carlo_phase_b_c_summary.md`, `monte_carlo_phase_b_c_results.csv`.

### X.5 Comparison with the v1.x.2 empirical record

| Claim | Prior value | Phase B | Status |
|---|---|---|---|
| v2.0 survival-rate phase boundary | rr approximately 0.057 (Gate 3 coarse grid) | Transition rr=0.060 to 0.066; 50% inflection near rr=0.063 | Refined |
| rr=0.057 status | Boundary / marginal | Collapse-dominated, 1.1% survival | Refined |
| Pattern 1 cliff | Alpha-driven, 2.5x to 3.0x at alpha=1.0 | Confirmed; cliff 4.0x (alpha=0.75) to 2.5x (alpha=1.5) | Holds and extends |
| Multi-generational continuity | Mean final gen 2.131 (Gate 3) | Mean gen 2 to 3.7 below cliff | Holds |
| COP protective effect | 73.9pp (adversarial) | Not tested; Category C is benign baseline (-0.47pp) | Preserved |
| Pattern 1 economics | New in v2.0 | Confirmed at scale | New v2.0 claim |

The one substantive shift is the survival-rate phase boundary location. The COP claim is preserved and reframed.

### X.6 Substrate for paper update

The paper-ready quantitative claims, with confidence intervals and supporting data files, are maintained in `simulation/diagnostics/paper_substrate.md` (operator decision to keep paper substrate as a standalone document). Summarized: the v2.0 survival-rate transition (X.2), the Pattern 1 cliff and continuity statistics (X.3), and the COP cost-audit benign baseline with its conditions caveat (X.4).

### X.7 Open questions and limitations

1. Gate 4 runaway-regime validation remains pending on the G4.1 to G4.3 specification dependency (Part VIII item 11). Phase B characterizes the cliff empirically; the formal acceptance checks are not yet built.
2. Operational COP infrastructure is not implemented; Gate 5 remains NOT_APPLICABLE.
3. The v2.0-versus-v1.x.2 like-for-like COP comparison (Interpretation B) is untested rather than refuted. The clean experiment is defined in `cop_finding_framing.md` section 5.
4. The survival-rate phase boundary is located to a 0.060 to 0.066 band on a grid spaced at 0.002 near the inflection. A targeted sweep would pin the 50% inflection to plus or minus 0.001 (Part IX.11).
5. Conditions outside the Phase B grid (finer phi near marginal rr, longer horizons, varied `beta_cap`) remain open.

---

## Suggested in-place refinements and cross-references

These are the precise edits to existing sections. Format: section, then replace Y with Z. For operator review; do NOT apply directly.

### Refinement R1: Part IX.2 (the U-shape finding), line ~1340

Replace:

> The contrast between the two matrices is the central finding. The v2.0 phase boundary at rr approximately 0.056 separates a regime where phi choice spans roughly 10pp survival difference from a regime where phi choice is approximately indifferent across the tested range [3, 25].

With:

> The contrast between the two matrices is the central finding. The phi-sensitivity transition near rr approximately 0.056 to 0.057 separates a regime where phi choice spans roughly 10pp survival difference from a regime where phi choice is approximately indifferent across the tested range [3, 25]. Note that this phi-sensitivity transition is distinct from the survival-rate phase boundary. Monte Carlo Phase B (Part X.2) relocates the v2.0 survival-rate phase boundary to the rr=0.060 to 0.066 transition with a 50% inflection near rr=0.063; rr=0.057 is collapse-dominated (1.1% aggregate survival), the bottom of the collapse zone rather than the survival midpoint. The strong phi sensitivity at rr=0.057 is precisely because rr=0.057 sits deep in the collapse regime where allocation quality is decisive.

Rationale: the prior text conflated the phi-sensitivity transition (rr approximately 0.056) with the survival-rate phase boundary. Phase B shows these are different rr locations. The phi finding itself is unchanged; only the phase-boundary attribution is corrected.

### Refinement R2: Part IX.9 (gate validation outcomes), Gate 3 entry, line ~1518

Add a clarifying sentence after the Gate 3 PASSED paragraph:

> Note on rr coverage: Gate 3's rr grid {0.057, 0.060, 0.064, 0.070} placed rr=0.057 within the collapse regime, not at the survival-rate phase boundary. Monte Carlo Phase B (Part X.2) characterizes rr=0.057 as collapse-dominated (1.1% aggregate survival) and locates the survival-rate transition at rr=0.060 to 0.066. Gate 3's succession-economics findings are unaffected; the clarification concerns only the rr-to-boundary mapping.

### Cross-reference C1: Part IX.11 future research directions, line ~1583

Replace:

> The 0.057-to-0.060 transition observed in the investigation, plus Gate 3's per-cell survival rates (0-7% at rr=0.057, 96-100% at rr=0.070) imply the v2.0 phase boundary is narrow. Pinning it down to plus or minus 0.001 resolution would refine framework quantitative claims. Part I currently states "extinction boundary rr approximately 0.057" after the v2.0 revision; a targeted sweep would either confirm or refine.

With:

> Monte Carlo Phase B (Part X.2) refined the v2.0 survival-rate phase boundary to the rr=0.060 to 0.066 transition with a 50% inflection near rr=0.063, and reclassified rr=0.057 as collapse-dominated (1.1% aggregate survival). The remaining open item is pinning the 50% inflection to plus or minus 0.001 resolution, which would require a targeted sweep on a grid finer than Phase B's 0.002 spacing near the inflection.

## Suggested edits to Part I and Part VIII

### Edit E1: Part I, line 15

Replace:

> **The dual phase transition is stable.** v1.x.2 placed the extinction boundary at rr approximately 0.055 and the collapse boundary at rr approximately 0.064; v2.0 architecture places the extinction boundary at rr approximately 0.057 (see Part IX.2). Collapse boundary not yet re-characterized under v2.0. Targeted phase-boundary sweep is future work (Part IX.11).

With:

> **The dual phase transition is stable.** v1.x.2 placed the extinction boundary at rr approximately 0.055 and the collapse boundary at rr approximately 0.064. Under v2.0 architecture, Monte Carlo Phase B (Part X.2) characterizes the survival-rate transition at rr=0.060 to 0.066 with a 50% inflection near rr=0.063; rr=0.057 is collapse-dominated (1.1% aggregate survival), refining the earlier Gate 3-grid estimate of approximately 0.057. Pinning the inflection to plus or minus 0.001 is future work (Part IX.11).

### Edit E2: Part I, line 24 (status paragraph)

After the sentence ending "gates 1, 2, 3 pass under v2.0 (Part IX.9)", add:

> Monte Carlo Phase B (Part X) completed the v2.0 quantitative-characterization arc across the survival landscape, succession dynamics, and the COP cost-audit baseline (29,400 rows, 0 errors).

### Edit E3: Part VIII item 10 (optional research directions), line 1293

The item lists "Monte Carlo Phase B" as an optional research direction. Replace its leading mention:

> **Optional research directions** in priority order (Part IX.11): Monte Carlo Phase B; dynamic phi formulation; ...

With:

> **Optional research directions** in priority order (Part IX.11): ~~Monte Carlo Phase B~~ (done; see Part X); dynamic phi formulation; ...

### Edit E4: Part VIII, new completed-item note

Add to the completed-items list (alongside items 6 to 9 which use the struck-through "done" convention):

> 12. ~~Run Monte Carlo Phase B quantitative validation at scale.~~ Done. Categories A, B, C totaling 29,400 rows, 0 errors (Part X). Survival landscape, succession dynamics, and COP cost-audit baseline characterized. 39/39 legacy tests pass.

## Pointers for non-program-reference documents (operator action)

These live outside the program reference and are flagged for the operator, not drafted here:

- Stage 2 implementation notes: update any "marginal conditions at rr=0.057" language to "collapse-dominated conditions at rr=0.057" consistent with X.2.
- Site status update draft (not yet posted): update the phase boundary claim to the rr=0.060 to 0.066 transition with 50% inflection near rr=0.063 before posting.
