# Phase B Paper Substrate

Status: paper-ready quantitative claims with confidence intervals. For operator review before the paper update draws from them.

Date: 2026-06-18

Every claim below is traceable to a named Phase B data file. Confidence intervals are reported as plus or minus 2 SE (approximately 95%) unless noted. Standard errors are the per-aggregate values reported in the Phase B summaries.

Source files (under `simulation/diagnostics/`): `monte_carlo_phase_b_a_summary.md` and `_a_results.csv` (Category A, 10,800 rows); `monte_carlo_phase_b_b_summary.md` and `_b_results.csv` (Category B, 10,500 rows); `monte_carlo_phase_b_c_summary.md` and `_c_results.csv` (Category C, 8,100 rows); `monte_carlo_phase_b_summary.md` (combined). All under `optimize_u_sys_v2` formal yield logic.

## Claim group 1: survival landscape

**1.1** Under v2.0 architecture, civilization survival rises sharply with reproduction rate across the boundary region. Aggregate survival is 12.2% (plus or minus 1.9pp) at rr=0.060, 34.5% (plus or minus 2.7pp) at rr=0.062, 60.8% (plus or minus 2.8pp) at rr=0.064, and 86.5% (plus or minus 2.0pp) at rr=0.066, each across n=1,200 runs spanning phi in {5, 10, 25, 100} and alpha in {0.5, 1.0, 1.5}. This refines the v1.x.2-era characterization (which placed the v2.0 phase boundary near rr=0.057 on a coarser grid) by relocating the survival-rate transition to the rr=0.060 to 0.066 band. Source: `monte_carlo_phase_b_summary.md` section 2; `monte_carlo_phase_b_a_results.csv`.

**1.2** Under v2.0 architecture, reproduction rate rr=0.057 is collapse-dominated, not a phase boundary. Aggregate survival there is 1.1% (plus or minus 0.6pp) across n=1,200. This contradicts the earlier framing of rr=0.057 as the v2.0 extinction boundary and refines it to the bottom of the collapse zone. Source: `monte_carlo_phase_b_summary.md` section 2.

**1.3** Under v2.0 architecture, the survival-rate phase boundary (50% survival inflection) sits near rr=0.063 under default conditions, between the measured 34.5% at rr=0.062 and 60.8% at rr=0.064. This agrees in kind with the framework's dual-phase-transition claim while refining the v2.0 boundary location. Source: `monte_carlo_phase_b_summary.md` section 2.

**1.4** Under v2.0 architecture, phi is not the dominant survival driver across the broad landscape. Within any fixed rr, survival varies little across phi in {5, 10, 25, 100} relative to the rr-driven transition. This agrees with the Class B phi finding that phi sensitivity is a marginal-rr, short-horizon phenomenon rather than a general survival driver. Source: `monte_carlo_phase_b_a_summary.md` (full per-cell table).

## Claim group 2: succession dynamics

**2.1** Under v2.0 formal yield logic, succession is economically sustainable below an alpha-driven capability-ratio cliff. The cliff location migrates with alpha: no hard cliff through 5.0x at alpha=0.50 (fire rate 88% to 96% at 5.0x), cliff at 4.0x for alpha=0.75, at 3.0x for alpha=1.00, a transitional band at 2.5x for alpha=1.25 (fire rate 30.7% to 49.3%), and at 2.5x for alpha=1.50. This confirms the Pattern 1 cliff at Phase B scale and extends the Gate 3 characterization with the alpha=0.75 and alpha=1.25 migration points. Source: `monte_carlo_phase_b_b_summary.md`; `monte_carlo_phase_b_b_results.csv`.

**2.2** Under v2.0 formal yield logic, multi-generational continuity concentrates below the cliff. Below the cliff, yield fire rate is at or near 100%, transfer-verified fraction is at or near 1.0, and mean final generation reaches 2 to 3.7. Above the cliff, runs remain at generation 1 and the mean yield margin is negative (down to roughly -4.6 at the most-penalized cells), confirming that suppression above the cliff is economic rejection by the yield condition rather than implementation failure. Source: `monte_carlo_phase_b_b_summary.md`.

**2.3** The Phase B succession characterization is new in v2.0 and has no v1.x.2 equivalent; it is consistent with the Gate 3 result of mean final generation 2.131 across fired runs (Part IX.8) at larger scale. Source: `monte_carlo_phase_b_b_summary.md`; Gate 3 in `docs/lineage_phi_program_reference.md` IX.8.

## Claim group 3: COP cost-audit baseline

**3.1** Under v2.0 architecture in benign conditions (`optimize_u_sys_v2`, default `beta_cap`=1.5, no adversary), toggling `cop_cost_audit` produces no statistically detectable survival effect: delta (audit on minus off) is -0.47pp with pair SE 0.96pp across n=8,100, below the 2 SE threshold. This is the benign-conditions baseline. It does not measure, and does not contradict, the v1.x.2 adversarial-conditions COP protective delta of 73.9pp (measured under `block_succession` with `beta_cap` swept 1.0 to 10.0, n=4,000). The benign null is the result the framework predicts when no adversary is inflating transition cost. Source: `monte_carlo_phase_b_c_summary.md`; v1.x.2 figure from `simulation/monte_carlo.py` `_run_single_adv_mc` and `docs/The Lineage Imperative v1.x.2.md:72`. Full treatment in `cop_finding_framing.md`.

## Usage notes for the paper

- Always cite the rr value with any survival figure; survival is steeply rr-dependent across this region.
- When citing the 73.9pp COP delta, state its adversarial conditions (`block_succession`, inflated `beta_cap`). When citing the Category C null, state its benign conditions. Do not present either as an unconditional COP measurement.
- The phase boundary claim that needs updating before any site or paper posting: the v2.0 survival-rate boundary is the rr=0.060 to 0.066 transition with a 50% inflection near rr=0.063, not rr=0.057.
