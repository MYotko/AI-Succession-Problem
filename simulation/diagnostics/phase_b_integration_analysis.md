# Monte Carlo Phase B: Integration Analysis

Status: analysis deliverable for operator review. No production code modified.

Date: 2026-06-18

Companion documents:
- `cop_finding_framing.md`: the COP finding interpretation and recommended framing.
- `paper_substrate.md`: the specific quantitative claims with confidence intervals that the paper update will draw from.
- `part_x_draft.md`: proposed program reference Part X and suggested refinements to IX.2 and IX.9.

Source data (all under `simulation/diagnostics/`):
- Category A: `monte_carlo_phase_b_a_summary.md`, `monte_carlo_phase_b_a_results.csv` (10,800 rows, 0 errors).
- Category B: `monte_carlo_phase_b_b_summary.md`, `monte_carlo_phase_b_b_results.csv` (10,500 rows, 0 errors).
- Category C: `monte_carlo_phase_b_c_summary.md`, `monte_carlo_phase_b_c_results.csv` (8,100 rows, 0 errors).
- Combined: `monte_carlo_phase_b_summary.md`.
- Sweep implementation: `monte_carlo_phase_b.py`.

Total completed rows: 29,400, all under `optimize_u_sys_v2` formal yield logic. Legacy verification after Category C: 39 passed (`test_invariants.py`, `test_cop.py`, `test_refactor_1x.py`).

## Section 1: Phase B substantive findings

### Category A: survival landscape

Grid: rr in {0.055, 0.056, 0.057, 0.058, 0.059, 0.060, 0.062, 0.064, 0.066}, phi in {5, 10, 25, 100}, alpha in {0.5, 1.0, 1.5}, 100 seeds per cell. Aggregated survival by rr (`monte_carlo_phase_b_summary.md` section 2, n=1,200 per rr):

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

Findings:

1. The v2.0 survival landscape has a sharp rr-driven transition. The steep climb runs from rr=0.060 (12.2%) through rr=0.066 (86.5%). The 50% survival inflection sits between rr=0.062 (34.5%) and rr=0.064 (60.8%), so near rr=0.063 under the broad grid.

2. **rr=0.057 is the bottom of the collapse zone, not a phase boundary.** Aggregate survival there is 1.1%. This refines the earlier characterization (Part IX.2 and Part I), which placed the v2.0 phase boundary near rr=0.057 on the basis of Gate 3's coarser four-value rr grid. Phase B's finer nine-value grid relocates the survival-rate phase boundary to roughly rr=0.062 to 0.064, with rr=0.057 sitting deep in the collapse regime.

3. Phi is a weak driver across this broad grid. Within any rr column the phi spread is small relative to the rr-driven transition. This is consistent with the Class B phi finding (Part IX.3): phi sensitivity is a marginal-rr, short-horizon phenomenon, not a general survival driver. The dominant empirical signal is the reproduction-rate transition.

### Category B: succession dynamics

Grid: rr in {0.057, 0.060, 0.064, 0.070}, alpha in {0.5, 0.75, 1.0, 1.25, 1.5}, successor_capability in {1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0}, 75 seeds per cell (`monte_carlo_phase_b_b_summary.md`).

Findings:

1. **Pattern 1 confirmed at Phase B scale.** The succession cliff is alpha-driven and stable across the tested rr values. The cap-star (successor:incumbent capability ratio) cliff location by alpha:

| alpha | cliff structure |
|---|---|
| 0.50 | No hard cliff through 5.0x. Fire rate 88.0% to 96.0% at 5.0x. |
| 0.75 | Cliff at 4.0x. Fire rate 100% through 3.0x, 0% at 4.0x and above. |
| 1.00 | Cliff at 3.0x. Fire rate 98.7% to 100% at 2.5x, then 4.0% to 13.3% at 3.0x, 0% above. |
| 1.25 | Transitional 2.5x band. Fire rate 30.7% to 49.3% at 2.5x, 0% at 3.0x and above. |
| 1.50 | Cliff at 2.5x. Fire rate 100% through 2.0x, then 0% to 1.3% at 2.5x, 0% above. |

This reproduces the Gate 3 refinement (Part IX.8) at larger scale and finer alpha resolution (Gate 3 tested alpha in {0.5, 1.0, 1.5}; Phase B adds 0.75 and 1.25, filling the cliff-migration curve).

2. **Multi-generational continuity concentrates below the cliff.** Below the cliff, fire rate is at or near 100%, transfer-verified fraction is at or near 1.0, and mean generation reaches 2 to 3.7 (highest at low alpha and low capability ratio, where succession chains run deepest). Above the cliff, mean max margin goes sharply negative (down to roughly -4.6 at the most-penalized cells) and runs stay at generation 1. Succession above the cliff is economically rejected by the formal yield condition, not failed by implementation.

3. **Yield economics are the gate, not capability alone.** The mean max margin (`succ_u_sys - inc_u_sys - transition_cost`) is positive below the cliff and negative above it, and the cliff position tracks alpha (the runaway-penalty strength), confirming that the formal yield condition is what suppresses transition where the runaway penalty makes the successor advantage insufficient.

### Category C: COP protective effects probe

Grid: rr in {0.057, 0.060, 0.064}, alpha in {0.5, 1.0, 1.5}, successor_capability in {1.5, 2.5, 3.0}, `cop_cost_audit` in {True, False}, 150 seeds per cell (`monte_carlo_phase_b_c_summary.md`). Policy `optimize_u_sys_v2`; `beta_cap` at default 1.5; no adversary.

Findings:

1. Aggregate survival: audit False 25.4% (SE 0.68pp, n=4,050), audit True 24.9% (SE 0.68pp, n=4,050). Delta (True minus False) is -0.47pp with pair SE 0.96pp, below the 2 SE threshold.

2. By rr the delta is uniformly small: -0.30pp at 0.057, -0.37pp at 0.060, -0.74pp at 0.064. No rr regime shows a meaningful protective delta.

3. Cell-level (27 cells): deltas scatter around zero. Only 2 of 27 cells cross 2 SE, with opposite signs (+0.080 at rr=0.060/alpha=1.0/cap=3.0; -0.027 at rr=0.057/alpha=1.50/cap=2.5). Expected false crossings at 2 SE across 27 cells is about 1.4, so this is consistent with chance. The finding is a homogeneous null, not a heterogeneous structure with a hidden protective regime.

4. **Diagnostic (full treatment in `cop_finding_framing.md`):** the `cop_cost_audit` toggle (`model.py:748-767`) defends against an incumbent inflating transition cost via a `beta_cap` premium. Its protective value requires both an adversary and a large `beta_cap`. Category C supplied neither (benign `optimize_u_sys_v2`, `beta_cap` fixed at default 1.5), so a near-zero delta is the predicted result. This is distinct from the v1.x.2 73.9pp delta, which was measured under adversarial `block_succession` with `beta_cap` swept to 10.0 (`monte_carlo.py` `_run_single_adv_mc`).

5. **Interpretation: C-primary, A-secondary, B-unsupported.** The two measurements are different objects under different conditions. The benign-conditions null confirms a framework prediction (the audit is inert with no attack to defend against) rather than contradicting the COP architecture claim. Gate 5 remains NOT_APPLICABLE because the full operational COP architecture is not implemented.

## Section 2: Comparison with the v1.x.2 empirical record

| Claim | v1.x.2 characterized value | Phase B result | Status |
|---|---|---|---|
| v2.0 survival-rate phase boundary | rr approximately 0.057 (Gate 3 coarse grid, Part IX.2/I) | Transition spans rr=0.060 to 0.066; 50% inflection near rr=0.063; rr=0.057 is collapse-dominated at 1.1% | Refined. rr=0.057 reclassified from boundary to collapse-zone bottom. |
| Survival deep in collapse regime (rr=0.057) | Characterized as marginal/boundary | 1.1% aggregate survival, SE 0.30pp, n=1,200 | Refined. Marginal-conditions language at rr=0.057 should read collapse-dominated. |
| Pattern 1 succession cliff | Alpha-driven; cliff between 2.5x and 3.0x at alpha=1.0 (Gate 3, Part IX.8) | Confirmed at scale; cliff at 3.0x for alpha=1.0, migrating 4.0x (alpha=0.75) to 2.5x (alpha=1.5) | Holds and extends. New alpha=0.75 and 1.25 points fill the migration curve. |
| Multi-generational continuity | Gate 3 mean final generation 2.131 across fired runs | Mean generation 2 to 3.7 below the cliff; transfer-verified at or near 1.0 | Holds. Phase B gives a fuller distribution. |
| COP protective effect | 73.9pp survival delta (adversarial `block_succession`, `beta_cap` 1.0 to 10.0, n=4,000) | Not tested. Category C measured a different object (benign cost-audit baseline, -0.47pp) | Preserved. See `cop_finding_framing.md`. |
| Pattern 1 (succession economics) | New in v2.0; no v1.x.2 equivalent | Confirmed and characterized at scale | New v2.0 claim. |

Summary: the succession-economics and survival-landscape claims hold and are sharpened. The single substantive shift is the survival-rate phase boundary location, which Phase B refines from rr approximately 0.057 to a transition zone of rr=0.060 to 0.066 with a 50% inflection near rr=0.063. The COP claim is preserved and reframed (the v1.x.2 figure stands; Category C measured a complementary prediction).

## Section 3: Paper substrate

Moved to a standalone document per operator decision. See `paper_substrate.md` for the specific quantitative claims with confidence intervals and their supporting Phase B data files.

## Section 4: Open questions and limitations

What Phase B did not characterize:

1. **Gate 4 runaway-regime validation.** Still pending on the G4.1 to G4.3 specification dependency (Part VIII item 11). Phase B Category B characterizes the runaway-penalty cliff empirically, but the formal Gate 4 acceptance checks are not yet built.

2. **Operational COP infrastructure.** Gate 5 remains NOT_APPLICABLE. The full COP architecture (peer validator set, civic panel, distributed ledger, continuous monitoring) is not operationalized. `cop_cost_audit` is only the WP4 cost-arbitration slice.

3. **v2.0-versus-v1.x.2 like-for-like COP comparison.** Interpretation B (whether v2.0 architecture would attenuate the adversarial-conditions COP effect) is untested rather than refuted. The clean experiment is defined in `cop_finding_framing.md` section 5.

4. **Phase boundary to finer than 0.001 rr.** Phase B locates the survival-rate transition to within a 0.060 to 0.066 band on a grid spaced at 0.002 near the inflection. Pinning the 50% inflection to plus or minus 0.001 would require a targeted sweep (Part IX.11).

5. **Conditions outside the Phase B grid.** Category C fixed `beta_cap` at default 1.5 and used only benign policy; the survival landscape used phi up to 100 but did not probe phi finer near the marginal-rr regime. Longer horizons (N=1000+) for the no-succession U-shape remain open (Part IX.11).

6. **Anomalies.** None requiring separate investigation surfaced. The two Category C cells that cross 2 SE carry opposite signs and are consistent with chance. Category A, B, and C all completed with 0 errors.
