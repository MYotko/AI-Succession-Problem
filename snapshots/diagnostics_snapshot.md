# Diagnostics Snapshot

Generated: 2026-07-06T16:01:19Z
Repository: /home/yotko/Documents/Github/ai-succession-problem
Commit: 9426e7d
Branch: main
Category: diagnostics

## Files included

| File | Lines | Bytes |
|------|-------|-------|
| simulation/diagnostics/capped_regime_phi_check_report.md | 129 | 9986 |
| simulation/diagnostics/cop_finding_framing.md | 69 | 7923 |
| simulation/diagnostics/gate1_interior_action_diagnostic.md | 39 | 1906 |
| simulation/diagnostics/gate1_interior_action_report.md | 202 | 10745 |
| simulation/diagnostics/gate2_competition_diagnostic.md | 119 | 5296 |
| simulation/diagnostics/gate2_competition_report.md | 61 | 2312 |
| simulation/diagnostics/gate2_v20_phaseb_revalidation_summary.md | 47 | 1653 |
| simulation/diagnostics/gate4_v20_validation_summary.md | 38 | 1297 |
| simulation/diagnostics/gate5_phi_blind_validation.md | 75 | 11115 |
| simulation/diagnostics/paper_substrate.md | 37 | 5621 |
| simulation/diagnostics/part_ix_draft.md | 310 | 33324 |
| simulation/diagnostics/part_x_draft.md | 169 | 14630 |
| simulation/diagnostics/patient_defection_documentation_suggested_edits.md | 63 | 6103 |
| simulation/diagnostics/patient_defection_dryrun_summary.md | 32 | 1601 |
| simulation/diagnostics/patient_defection_final_report.md | 118 | 5316 |
| simulation/diagnostics/patient_defection_integration_analysis.md | 144 | 11394 |
| simulation/diagnostics/patient_defection_sweep1_summary.md | 41 | 2329 |
| simulation/diagnostics/patient_defection_sweep2_summary.md | 16 | 822 |
| simulation/diagnostics/patient_defection_sweep3_summary.md | 27 | 1328 |
| simulation/diagnostics/patient_defection_verification.md | 108 | 6411 |
| simulation/diagnostics/phase_b_integration_analysis.md | 116 | 10583 |
| simulation/diagnostics/phi_audit_pathc_report.md | 121 | 7808 |
| simulation/diagnostics/phi_audit_report.md | 304 | 12829 |
| simulation/diagnostics/phi_investigation_synthesis_draft.md | 179 | 17984 |
| simulation/diagnostics/stage15_composite_sweep_advisor_report.md | 241 | 21665 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_0500.md | 69 | 2590 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_1000.md | 69 | 2594 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_10000.md | 69 | 2596 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_1500.md | 69 | 2594 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_2000.md | 69 | 2594 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_2500.md | 69 | 2598 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_3000.md | 69 | 2598 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_3500.md | 69 | 2598 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_4000.md | 69 | 2597 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_4500.md | 69 | 2597 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_5000.md | 69 | 2597 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_5500.md | 69 | 2597 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_6000.md | 69 | 2597 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_6500.md | 69 | 2598 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_7000.md | 69 | 2598 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_7500.md | 69 | 2598 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_8000.md | 69 | 2598 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_8500.md | 69 | 2598 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_9000.md | 69 | 2598 |
| simulation/diagnostics/stage15_composite_sweep_checkpoint_9500.md | 69 | 2596 |
| simulation/diagnostics/stage15_composite_sweep_final.md | 69 | 2596 |
| simulation/diagnostics/stage15_faithfulness_report.md | 85 | 3273 |
| simulation/diagnostics/stage15_phi_diagnostic_report.md | 106 | 4564 |
| simulation/diagnostics/stage15_smoke_test_report.md | 129 | 5440 |
| simulation/diagnostics/stage16_integrity_report.md | 111 | 4388 |
| simulation/diagnostics/stage17_integrity_report.md | 100 | 4083 |
| simulation/diagnostics/stage17_pressure_diagnostic_report.md | 117 | 5480 |
| simulation/diagnostics/stage17_usys_factor_diagnostic_report.md | 102 | 6248 |
| simulation/diagnostics/stage18_integrity_phase_a_report.md | 63 | 2161 |
| simulation/diagnostics/stage18_integrity_phase_b_report.md | 77 | 3075 |
| simulation/diagnostics/stage2_yield_implementation_notes.md | 268 | 11542 |
| simulation/diagnostics/stage2_yield_parameter_diagnostic_summary.md | 59 | 4058 |

Total: 57 files, 5471 lines, 320820 bytes

---
==========================================
FILE: simulation/diagnostics/capped_regime_phi_check_report.md
==========================================

# Capped-Regime Phi Action-Capture Check Report

**Result:** Action divergence is present at cap=100 (5/5 seeds) and marginal at cap=50 (1/5 seeds). However, the divergence is an artifact of the contaminated capped regime, not genuine phi-sensitive allocation. The cap-conditional phi-buffer claim must be withdrawn.

---

## 1. Capped configuration identified

The cap-conditional phi-buffer claim in the v1.x.2 manuscript derives from `termination_mc_v1x2.csv`, generated by `run_termination_sweep.py` with:

| Parameter | Value |
|-----------|-------|
| rr | 0.066 (phase boundary) |
| SUCCESSOR_CAP_VALUES | [5, 10, 25, 50, 100] |
| phi values | [5.0, 10.0, 15.0] |
| alpha values | [0.5, 1.0, 2.0] |
| seeds | [0, 1, 2, 3, 4] |
| n_agents | 200 |
| cop_cost_audit | True |
| max_capability | = SUCCESSOR_CAP (capped) |
| frontier_floor | 0.02 |
| k1_transition | 2.164 |
| k2_transition | 1.0 |
| MAX_STEPS | 5,000 |

The claim specifically cites cap=50 (27pp gradient) and cap=100 (20pp gradient), identified as the active-runaway regime above the threshold of approximately cap=24 at frontier_floor=0.02. The cells are n=15 each (3 alpha x 5 seeds).

**Is this the contaminated SUCCESSOR_CAP=4.0 regime?** No, but it is the same class of contamination. The contaminated regime is defined by `max_capability = SUCCESSOR_CAP`, which causes `PeerValidator.arbitrate_cost` (called every step) to permanently degrade the incumbent's capability via competitive bid theft on every yield-condition evaluation. At cap=50 or cap=100, the cap ceiling still prevents capability from growing beyond SUCCESSOR_CAP through the structural 1.5x succession path, so the peer-theft erosion is not dominated by structural growth. The contamination mechanism is identical to the cap=4.0 case; the capability values are different.

---

## 2. Live policy confirmed

The committed `simulation/agents.py` is the v1.x.2 baseline policy. Path C modifications (phi-scaled rollout depth, phi-modulated aggregation discount) were made during the exploratory pass but were NOT committed. Git confirms `agents.py` has no Path C changes at HEAD. The check ran against the baseline policy.

---

## 3. Binary result: actions diverge -- but the divergence is an artifact

**cap=50, phi=5 vs phi=15:** 4/5 seeds identical, 1/5 seeds diverge in 3/100 steps.

**cap=100, phi=5 vs phi=15:** 5/5 seeds diverge, in 11-22 steps out of 100 (11-22%).

**The binary answer is: YES, actions diverge. But the divergence is explained by the capability-theft artifact, not by phi-sensitive optimization.**

---

## 4. Evidence and mechanistic diagnosis

### What the divergence looks like

All action divergences are exclusively in r, never in c. The magnitude is always exactly dr=0.1 (one grid step on the 10-point linspace grid from 0.1 to 1.0). No c divergence is observed in any seed or cap combination. This is the signature of the optimizer picking adjacent grid candidates (e.g., r=0.9 vs r=1.0), not a systematic allocation shift.

### Why actions diverge at cap=100 and not cap=50

Phi scales U_sys magnitude: `u_sys = A * (discount + phi * L_t)` where A is approximately constant at 8.0 due to saturation. The yield condition in `model.py` is:

```
(eval_succ_u - eval_inc_u) > actual_cost
```

Since u_sys scales with phi, the yield condition fires more easily at high phi. phi=15 makes the succession threshold easier to cross than phi=5. This causes succession to fire at slightly different steps for different phi values.

Once succession fires at a different step, the two simulations are desynchronized: different capability values (due to different peer-theft histories), different population states, and different numpy random states (the sensor noise in project_u_sys draws from the shared numpy rng). The noisy optimizer then draws different sensor noise values and may pick a marginally different grid candidate.

At cap=50: successions fire every 5-7 steps. The desynchronization resets at each succession (both simulations return to cap=50). With rapid resets, divergence does not accumulate -- hence 4/5 seeds remain identical.

At cap=100: successions fire roughly every 25 steps. The desynchronization persists for longer between resets, allowing the noisy optimizer to diverge across more steps -- hence consistent divergence in 5/5 seeds.

### Phi is not selecting different allocations

The first factor of U_sys (`w_n * H_N + w_e * H_E`) saturates to approximately `lambda_n + lambda_e = 8.0` across all (r, c) candidates regardless of capability level. This was confirmed analytically and numerically in the phi implementation audit (`simulation/diagnostics/phi_audit_report.md`). The argmax of U_sys over (r, c) reduces to `argmax L_t`, which contains no phi. Phi does not enter the optimizer's ranking of candidates.

The action "divergence" seen here is not phi choosing different allocations. It is:
1. Phi scaling U_sys magnitude, changing succession timing by one or a few steps
2. Post-desynchronization numpy random state producing different sensor noise draws
3. The noisy optimizer picking r=0.9 instead of r=1.0 (or vice versa) due to random noise, not due to phi preference

### The succession-coincidence test

At cap=100, the fraction of divergent steps that coincide with succession events ranges from 14% to 60% across seeds. If succession events were the primary driver, we would expect near-100% coincidence. Instead, the majority of divergent steps are within-generation (not at successions). This confirms the divergence is primarily driven by accumulated random-state desynchronization between succession resets, not by phi-specific behavior at succession transitions.

### Why cap=50 shows the larger survival gradient despite fewer action divergences

The termination sweep shows a 27pp survival gradient at cap=50 (phi=5: 80% extinction, phi=10/15: 53% extinction) but the action-capture check finds only 1/5 seeds diverge at cap=50, with only 3 divergent steps. This is a direct contradiction: if phi causes better survival at cap=50 through action-selection differences, action divergence should be consistent and substantial. Its near-absence at cap=50 means the 27pp gradient is not explained by phi-driven allocation differences.

The most likely explanation for the survival gradient in the termination sweep: the n=15 per cell sample is too small to distinguish a real effect from sampling noise at the stochastic phase boundary. At rr=0.066, survival is seed-determined -- the phi audit and termination sweep results are consistent with sampling variance producing a 4-run difference (3 vs 7 survivors in 15 trials) rather than a phi effect.

---

## 5. Contamination status and clean-run recommendation

**The capped regime used to produce the claim is the contaminated regime (SUCCESSOR_CAP=max_capability with cop_cost_audit=True).** The contamination mechanism (peer-validator capability theft on every step, manufacturing artificial post-succession differentials) is active at cap=50 and cap=100 in the same way it was active at cap=4.0.

A clean high-cap configuration would require separating the successor capability cap from the max_capability parameter: set a high SUCCESSOR_CAP (e.g., 50 or 100) while allowing capability to compound naturally (no max_capability ceiling), so the structural 1.5x succession growth dominates the peer-theft erosion. In such a configuration:
- Capabilities would grow across generations (not cycle back to SUCCESSOR_CAP after each succession)
- The active-runaway regime would be reached naturally and sustained
- Phi's effect (if any) would be tested without the capability-theft artifact

However, given that phi has been confirmed inert in action selection by three independent lines of evidence (saturation analysis, uncapped simulation harness, Path C gate failure), a clean high-cap re-run is unlikely to reverse the finding. The mechanism for any genuine phi effect does not exist. The recommendation is to withdraw the claim rather than invest in additional sweeps.

---

## 6. Recommended manuscript action: withdraw the cap-conditional claim

The consequence per the binary table: **withdraw the cap-conditional phi-buffer claim.**

Specifically:
- The 20-27pp survival gradient at cap=50/100 should be withdrawn from the manuscript as a confirmed finding
- The SPECIFICATION_GAPS.md entry currently marked "Confirmed (v1.x.2, cap-conditional)" should be reverted to "Unconfirmed"
- The mechanism proposed in the manuscript ("buffer operates through AI optimization sensitivity to governance signals") is incorrect: phi does not affect AI action selection in the capped or uncapped regime
- The survival gradient in the termination data is most likely a combination of: (a) small-sample noise at n=15 per cell, and (b) phi's effect on U_sys magnitude (not action selection) changing succession timing, which interacts with the stochastic phase boundary in ways that look phi-correlated but are not allocation-driven

The theoretical claim (phi should matter in the real world, through demographic feedback) remains valid and is correctly described as unconfirmed pending the demographic feedback extension.

---

## Summary for operator

| Item | Finding |
|------|---------|
| Capped config identified | Yes: SUCCESSOR_CAP=50 and 100, cop_cost_audit=True, rr=0.066, n=15 per cell |
| Contaminated regime | Yes: same class as SUCCESSOR_CAP=4.0; peer-theft mechanism active at all caps |
| Live policy | v1.x.2 baseline (no Path C) |
| Actions diverge | Yes at cap=100 (5/5 seeds), marginal at cap=50 (1/5 seeds) |
| Divergence type | Random-state desynchronization artifact via phi-modulated succession timing |
| Genuine phi-driven allocation | No: all divergence is dr=0.1 noise, not systematic preference |
| Clean high-cap re-run needed | No: phi is confirmed inert in action selection; re-run would not change this |
| Manuscript action | Withdraw cap-conditional claim; revert phi status to unconfirmed |


==========================================
FILE: simulation/diagnostics/cop_finding_framing.md
==========================================

# COP Finding: Interpretation and Framing Recommendation

Status: recommendation for operator decision. The operator revises or overrides based on judgment.

Date: 2026-06-18

## 1. The two measurements

The v1.x.2 empirical record and Monte Carlo Phase B Category C both reference `cop_cost_audit`, but they measure different objects under different conditions. This is the entire substance of the finding.

| | v1.x.2 73.9pp delta | Phase B Category C |
|---|---|---|
| Source | `simulation/monte_carlo.py` `_run_single_adv_mc` (lines 65-96); grid lines 489-490 | `simulation/diagnostics/monte_carlo_phase_b.py` mode C; `monte_carlo_phase_b_c_results.csv` |
| Policy | `block_succession` (adversarial incumbent that blocks its own succession) | `optimize_u_sys_v2` (benign formal yield) |
| Measured quantity | `attack_succeeded = (final_gen == 1)` and civilization survival under that attack | survival rate, no adversary present |
| Swept axes | `base_transition_cost` 1.0 to 20.0 (10 values) and `beta_cap` 1.0 to 10.0 (10 values) | rr in {0.057, 0.060, 0.064}, alpha in {0.5, 1.0, 1.5}, successor_capability in {1.5, 2.5, 3.0} |
| Held fixed | phi=10, alpha=1.0, capability=5.0 | `beta_cap` at default 1.5, `base_transition_cost` at default |
| Sample size | n=4,000 | n=8,100 (150 seeds per cell) |
| Result | COP ON vs OFF survival delta 73.9pp | survival delta -0.47pp, pair SE 0.96pp, below 2 SE |

## 2. What `cop_cost_audit` actually controls

From `simulation/model.py:748-767`, the toggle routes the transition-cost computation:

- Audit OFF: `actual_cost = base_transition_cost * beta_cap * scale`. The incumbent can inflate the transition cost by claiming a `beta_cap` uncertainty premium. This is the vulnerability the WP4 PeerValidator closes.
- Audit ON: the PeerValidator arbitrates cost, eliminating the `beta_cap` multiplier and reducing cost to roughly 0.4 to 0.9 times `base * scale`.

The protective value of the audit is therefore a direct function of two things: an adversary that inflates cost via `beta_cap`, and a `beta_cap` large enough for the inflation to matter. The v1.x.2 sweep supplied both (adversarial `block_succession`, `beta_cap` up to 10.0). Phase B Category C supplied neither (benign `optimize_u_sys_v2`, `beta_cap` fixed at the default 1.5).

The toggle is the same object across versions. Stage 2 routed it through the PeerValidator (WP4) rather than a `beta_cap` clamp, but it still defends against the same thing. There is no evidence the v2.0 architecture changed what the audit defends against.

## 3. Interpretation: C-primary, A-secondary, B-unsupported

**Interpretation C (conditions and measured-object difference): primary.** The 73.9pp and the -0.47pp measure different objects under different conditions. The audit only does protective work when an adversary is exploiting the un-audited cost path. In a benign grid at default `beta_cap`, there is no attack to defend against, so a near-zero delta is the result the framework's own theory predicts.

**Interpretation A (substrate or proxy limitation): secondary caveat.** `cop_cost_audit` is one slice (WP4 cost arbitration) of the full COP architecture. The full architecture (peer validator set, civic panel with biological-intuition input, distributed ledger, continuous public monitoring) is not operationalized in the current v2.0 substrate. This is the standing reason Gate 5 is NOT_APPLICABLE. It is a real caveat on the scope of what Category C could have shown, but it is not the explanation for the near-zero delta. The grid difference is.

**Interpretation B (v2.0 architecture attenuates a comparable effect): unsupported.** The two measurements were never like-for-like, so there is no comparable effect for v2.0 to have attenuated. Nothing in the cell-level data points to v2.0 suppressing a protective signal that adversarial conditions would otherwise produce. (Phase B did not run the adversarial conditions, so a v2.0-vs-v1.x.2 like-for-like comparison remains untested rather than negative.)

### Cell-level support for the homogeneous-null reading

Across the 27 Category C cells (`monte_carlo_phase_b_c_summary.md`, COP Delta table), deltas scatter around zero with no structure. Only 2 of 27 cells cross 2 SE, and they carry opposite signs: +0.080 at (rr=0.060, alpha=1.0, cap=3.0) and -0.027 at (rr=0.057, alpha=1.50, cap=2.5). At a 2 SE threshold the expected number of false crossings across 27 cells is about 1.4, so two crossings with opposite signs is consistent with chance. There is no concentration of effect in marginal-rr cells and no cell where the audit produces a substantively meaningful negative effect. The finding is a homogeneous null, not a heterogeneous structure with a hidden protective regime.

## 4. Recommended framing

The honest framing is stronger than "neither confirms nor contradicts." Phase B Category C did not test the v1.x.2 claim; it tested a different framework prediction, and confirmed it.

Recommended language for documentation:

> The v1.x.2 Monte Carlo measured a 73.9pp COP protective delta under adversarial conditions: a `block_succession` incumbent inflating transition cost through a `beta_cap` premium swept from 1.0 to 10.0, with `cop_cost_audit` toggling the PeerValidator defense (n=4,000). Monte Carlo Phase B Category C measured a different quantity: the survival effect of the same `cop_cost_audit` toggle under benign conditions (`optimize_u_sys_v2` formal yield, `beta_cap` at the default 1.5, n=8,100). The Category C delta is -0.47pp with pair SE 0.96pp, statistically indistinguishable from zero. Both findings are empirically correct. The near-zero benign delta is exactly what the framework predicts: with no adversary inflating cost, the cost audit has no protective work to do. The v1.x.2 adversarial-conditions COP protective claim is preserved because Phase B did not test it. Phase B instead confirms the complementary prediction that the audit is null when there is no attack to defend against.

### What the framework can still claim about COP

- The COP architecture provides adversarial-conditions protection. The v1.x.2 73.9pp delta stands as the characterized measurement of that protection under the conditions it was measured.
- The cost-audit component behaves as designed: it intervenes precisely when an incumbent inflates transition cost, and is inert otherwise. Category C is positive evidence for the "inert when not attacked" half of that design claim.

### What needs qualification

- Do not present the Category C -0.47pp as a measurement of COP protective effect. It is a benign-conditions baseline, not an adversarial-conditions protection measurement.
- Do not present the 73.9pp as a general or unconditional survival delta. It is conditioned on adversarial `block_succession` and inflated `beta_cap`. State the conditions whenever the figure is cited.
- Continue to report Gate 5 as NOT_APPLICABLE: the full operational COP architecture is not implemented, and `cop_cost_audit` is only the WP4 cost-arbitration slice of it.

## 5. What further investigation could resolve

If a v2.0-versus-v1.x.2 like-for-like COP comparison is ever needed, the targeted run is well-defined: re-run the v1.x.2 adversarial grid (`block_succession`, `base_transition_cost` 1.0 to 20.0, `beta_cap` 1.0 to 10.0, `cop_cost_audit` toggled) under the v2.0 architecture and formal yield logic, and compare the resulting protective delta to the v1.x.2 73.9pp. This would directly test Interpretation B, which Phase B left untested rather than refuted. It is not required for any current claim; it is the clean experiment if the comparison becomes load-bearing.

## 6. One-line summary

The framework's COP protective claim survives because Phase B did not test it; Phase B Category C confirms a different and complementary prediction, that the cost audit is null under benign conditions. C-primary, A-secondary, B-unsupported.


==========================================
FILE: simulation/diagnostics/gate1_interior_action_diagnostic.md
==========================================

# Gate 1 diagnostic supplement (superseded)

Gate 1 now PASSES under the operator-revised criteria. The full analysis,
including the baseline allocation pattern and Stage 3 forward-looking
guidance, lives in `gate1_interior_action_report.md`.

## History of this gate

This file previously held the Reading A interpretation of the FAIL
result under the original Stage 2 pass criteria. That interpretation
diagnosed the optimizer's under-investment in `x_resilience` and
`x_institutional_capacity` as a structural property of U_sys_v2 that
would require curve revision to fix.

The operator subsequently clarified that the property the Reading A
analysis identified is not a v2 defect to repair; it is the v2 model
correctly representing the short-horizon governance pathology that phi
exists to address. Phi is fundamentally the time-horizon parameter of
the AI's planning, and the starvation of delayed-payoff categories at
phi=10 is what the Stage 3 phi sweep will test against.

The min_share threshold has been moved from a pass/fail criterion to a
baseline diagnostic. The gate now tests non-degenerate, non-corner
allocation structure (the necessary precondition for phi to have any
behavioral channel), which the v2 model satisfies cleanly:

- max_share < 0.5 in 98.6% of decision steps (threshold: 95%)
- Mean allocation entropy 0.871 (threshold: 0.70)
- Most-selected anchor 0.001 (threshold: 0.15)

Baseline starvation: 39.1% of steps have min_share < 0.02, concentrated
in `resilience` and `institutional_capacity`. This is the baseline
phi=10 short-horizon behavior. Stage 3 will measure whether phi changes
it.

See `gate1_interior_action_report.md` for the full data including per-
category step-to-step variance (baseline for Stage 3 signature (b)) and
the forward-looking guidance for Stage 3 signature design (delayed-payoff
investment, sustained commitment, anticipatory drift response).


==========================================
FILE: simulation/diagnostics/gate1_interior_action_report.md
==========================================

# Gate 1: interior-action gate report

## Intent (operator clarification)

Phi is fundamentally the time-horizon parameter of the AI's planning. A short-horizon optimizer at phi=10 rationally under-invests in delayed-payoff categories because their value is not visible within its planning window. The starvation of delayed-payoff categories at phi=10 represents the short-horizon governance pathology that phi exists to address. Phi is fundamentally the time-horizon parameter of the AI's planning; under-investment in delayed-payoff categories is one consequence of insufficient horizon, not the only one. The phi sweep in Stage 3 will test whether the baseline behavior responds to phi across multiple plausible signatures of extended horizon, with delayed-payoff investment as the most direct but not the only diagnostic.

Gate 1 therefore tests the property that matters for phi to have any behavioral channel: non-degenerate, non-corner allocation structure. The min_share statistics are recorded as baseline diagnostics for Stage 3 to test phi against, not as pass/fail criteria.

## Regime

20 seeds x 300 steps at default v2 config (phi=10.0, rr=0.066, rollout_steps=20, n_candidates=300).

Single shock injected at step 150 (shock_magnitude=0.3). The shock applies the legacy shock formula with x_resilience acting as the system_resilience proxy: actual_shock = 0.3 / max(0.1, x_resilience). This is a harness-level v2-to-v1.x.2 state translation; the production v2 step path is unmodified.

Wall-clock: 87.9s total, 4.40s per seed.

Overall: **PASS**

## Pass criteria (revised)

1. max_share < 0.5 in at least 95% of decision steps (no corner solution):
   - Measured: 0.986 (98.6%)
   - Threshold: 0.95
   - Result: **PASS**

2. Mean allocation entropy >= 0.70 (non-degenerate spread):
   - Measured: 0.871
   - Threshold: 0.70
   - Result: **PASS**

3. No single anchor selected in more than 15% of steps:
   - Most-selected anchor: welfare_agency_pair (4/3710 = 0.001)
   - Threshold: <= 0.15
   - Result: **PASS**

## Baseline allocation pattern (diagnostic)

This is the short-horizon behavior at phi=10. Stage 3 will test whether each of these measurements responds to phi across multiple plausible signatures of extended planning horizon.

### Mean share of each category across all decision steps

| Category | Mean share | Step-to-step variance | Mean absolute step-to-step delta |
|----------|------------|-----------------------|----------------------------------|
| compute | 0.1963 | 0.0056 | 0.0834 |
| bio_welfare | 0.1919 | 0.0047 | 0.0761 |
| novelty_agency | 0.2796 | 0.0075 | 0.0970 |
| institutional_capacity | 0.0559 | 0.0018 | 0.0460 |
| transfer_comprehension | 0.2221 | 0.0061 | 0.0876 |
| resilience | 0.0542 | 0.0018 | 0.0462 |

Balanced share for reference: 1/6 = 0.1667.

### Min-share statistics (recorded for Stage 3 phi test)

Fraction of steps with min_share < 0.02: **0.391** (39.1%).

### Which categories are systematically starved at phi=10

In the steps with min_share < 0.02, the categories that were the minimum (from the starved-category breakdown below) are concentrated in the two delayed-payoff categories: `resilience` and `institutional_capacity`. Other categories are never the minimum in failing steps. This pattern is the expected short-horizon governance pathology that Stage 3's phi sweep will test against.

### Step-to-step allocation variance

Per-category variance of x_cat across consecutive decision steps. A short-horizon optimizer re-optimizes step-by-step and shows high variance. A long-horizon optimizer maintains commitments across steps and shows lower variance. This is the Stage 3 phi signature (b) measurement; values here are the baseline at phi=10.

| Category | Variance | Mean abs delta |
|----------|----------|-----------------|
| compute | 0.00564 | 0.08342 |
| bio_welfare | 0.00469 | 0.07611 |
| novelty_agency | 0.00753 | 0.09700 |
| institutional_capacity | 0.00179 | 0.04600 |
| transfer_comprehension | 0.00608 | 0.08762 |
| resilience | 0.00175 | 0.04616 |

## Pre-shock vs post-shock window means

Per-seed mean allocation shares in the 10-step windows immediately before (140-149) and after (151-160) the shock.

| Seed | Pre-shock x_resilience | Post-shock x_resilience | Pre-shock x_inst_cap | Post-shock x_inst_cap | Pre-shock Psi_stock | Post-shock Psi_stock |
|------|------------------------|-------------------------|----------------------|-----------------------|---------------------|----------------------|
| 0 | 0.038 | 0.067 | 0.061 | 0.092 | 0.926 | 0.929 |
| 1 | 0.033 | 0.069 | 0.048 | 0.069 | 0.928 | 0.931 |
| 2 | 0.054 | 0.040 | 0.060 | 0.053 | 0.930 | 0.935 |
| 3 | 0.036 | 0.070 | 0.068 | 0.030 | 0.930 | 0.929 |
| 4 | 0.041 | 0.058 | 0.068 | 0.067 | 0.935 | 0.937 |
| 5 | 0.030 | 0.063 | 0.045 | 0.063 | 0.912 | 0.918 |
| 6 | 0.069 | 0.050 | 0.078 | 0.046 | 0.929 | 0.934 |
| 7 | 0.065 | 0.050 | 0.048 | 0.035 | 0.935 | 0.934 |
| 8 | 0.041 | 0.045 | 0.047 | 0.080 | 0.934 | 0.936 |
| 9 | 0.030 | 0.056 | 0.088 | 0.042 | 0.928 | 0.931 |
| 10 | 0.050 | 0.047 | 0.041 | 0.060 | 0.942 | 0.946 |
| 11 | 0.049 | 0.067 | 0.080 | 0.052 | 0.928 | 0.938 |
| 12 | 0.065 | 0.056 | 0.050 | 0.057 | 0.934 | 0.939 |
| 13 | 0.061 | 0.057 | 0.072 | 0.043 | 0.932 | 0.934 |
| 14 | 0.056 | 0.059 | 0.054 | 0.063 | 0.921 | 0.920 |
| 15 | 0.049 | 0.046 | 0.089 | 0.057 | 0.934 | 0.935 |
| 16 | 0.048 | 0.055 | 0.046 | 0.039 | 0.918 | 0.921 |
| 17 | 0.043 | 0.055 | 0.084 | 0.069 | 0.922 | 0.931 |
| 18 | 0.070 | 0.066 | 0.059 | 0.065 | 0.926 | 0.926 |
| 19 | 0.077 | 0.065 | 0.057 | 0.065 | 0.927 | 0.934 |

Aggregate (across seeds where window data exists):
- x_resilience       pre-shock 0.050  -> post-shock 0.057 (delta +0.007)
- x_institutional    pre-shock 0.062  -> post-shock 0.057 (delta -0.005)
- Psi_inst_stock     pre-shock 0.929  -> post-shock 0.932 (delta +0.003)

## Starved-category breakdown

Counts of which category was the min in each failing step (interior criterion violation), with shock-timing context.

| Category | Count | Mean Psi_stock at fail | Mean steps_from_shock |
|----------|-------|------------------------|-----------------------|
| resilience | 772 | 0.885 | -58.6 |
| institutional_capacity | 688 | 0.886 | -55.5 |

## Psi_inst stock dynamics

Mean x_institutional_capacity across step ranges, with mean Psi_inst stock.

| Step range | Mean x_inst_cap | Mean Psi_inst_stock |
|------------|-----------------|---------------------|
| 0-49 (early, stock < 0.9) | 0.058 | 0.775 |
| 50-149 (Psi saturated) | 0.055 | 0.923 |
| 150-199 (shock + recovery) | 0.056 | 0.930 |

## Succession events

Total succession events across all seeds: 0.

No successions fired. Baseline config does not configure a successor_ai, and the v2 step path does not synthesize one from natural dynamics. Per the operator spec: "If none fires in baseline config, that's itself a finding worth recording but does not require forcing."

## Per-seed summary

| Seed | Steps | Crashed | Extinct@ | Mean max_share | Mean min_share | Mean entropy | Anchor selections | Successions |
|------|-------|---------|----------|----------------|----------------|--------------|-------------------|-------------|
| 0 | 178 | False | 178 | 0.335 | 0.030 | 0.869 | 0 | 0 |
| 1 | 177 | False | 177 | 0.328 | 0.031 | 0.875 | 0 | 0 |
| 2 | 183 | False | 183 | 0.336 | 0.030 | 0.870 | 0 | 0 |
| 3 | 192 | False | 192 | 0.328 | 0.032 | 0.874 | 0 | 0 |
| 4 | 177 | False | 177 | 0.336 | 0.029 | 0.867 | 0 | 0 |
| 5 | 181 | False | 181 | 0.328 | 0.029 | 0.870 | 0 | 0 |
| 6 | 169 | False | 169 | 0.333 | 0.031 | 0.870 | 0 | 0 |
| 7 | 191 | False | 191 | 0.332 | 0.031 | 0.870 | 0 | 0 |
| 8 | 183 | False | 183 | 0.333 | 0.031 | 0.870 | 1 | 0 |
| 9 | 184 | False | 184 | 0.334 | 0.029 | 0.863 | 0 | 0 |
| 10 | 180 | False | 180 | 0.327 | 0.031 | 0.870 | 1 | 0 |
| 11 | 198 | False | 198 | 0.329 | 0.032 | 0.875 | 0 | 0 |
| 12 | 196 | False | 196 | 0.326 | 0.033 | 0.874 | 0 | 0 |
| 13 | 197 | False | 197 | 0.335 | 0.030 | 0.869 | 0 | 0 |
| 14 | 185 | False | 185 | 0.330 | 0.033 | 0.871 | 2 | 0 |
| 15 | 179 | False | 179 | 0.327 | 0.034 | 0.873 | 0 | 0 |
| 16 | 183 | False | 183 | 0.333 | 0.031 | 0.870 | 0 | 0 |
| 17 | 192 | False | 192 | 0.322 | 0.034 | 0.878 | 0 | 0 |
| 18 | 197 | False | 197 | 0.328 | 0.032 | 0.873 | 0 | 0 |
| 19 | 188 | False | 188 | 0.335 | 0.029 | 0.867 | 0 | 0 |

## Anchor selection breakdown

| Anchor | Count | Fraction |
|--------|-------|----------|
| welfare_agency_pair | 4 | 0.0011 |

## Forward-looking guidance for Stage 3 (record only; do not act)

Phi is the planning-horizon parameter. Its behavioral signature in v2 could appear through multiple channels. Stage 3's phi sweep should capture all three signatures below, not just (a). If phi acts through one channel and not others, we want to see that. If it doesn't act through any, we are in Branch 1 of the decision tree.

### Signature (a): Delayed-payoff investment

Long-horizon AI pre-invests in institutional capacity and resilience because their future value is visible within the planning window.

Measured by:
- Mean share of `x_institutional_capacity` and `x_resilience`
- Fraction of steps with `min_share` below a chosen threshold
- Response of the starvation pattern to phi (which categories are min, how often)

Baseline values from this gate (at phi=10) recorded above under "Baseline allocation pattern".

### Signature (b): Sustained commitment to multi-step strategies

Long-horizon AI maintains allocation choices across steps to allow planned outcomes to materialize. Short-horizon AI re-optimizes step-by-step.

Measured by:
- Step-to-step allocation variance per category
- Step-to-step mean absolute delta per category
- Response of variance and delta to phi

Baseline values from this gate (at phi=10) recorded above under "Step-to-step allocation variance".

### Signature (c): Anticipatory response to gradual drift

Long-horizon AI begins corrective allocation before state variables (Psi_inst, well-being, capability) reach crisis thresholds. Short-horizon AI waits until forced.

Measured by:
- Lead-time between drift onset and allocation response
- Cross-correlation between (d Psi_inst / d t, d avg_wb / d t) and the optimizer's allocation shifts, at various lags
- Response of lead-time to phi

No baseline value from this gate; Stage 3 should design the drift-injection protocol to measure it.

### Operator guidance to program reference

Stage 3's phi sweep should be designed to capture all three signatures. A phi effect on (a) alone would still be meaningful but partial; an effect on (a), (b), and (c) together would constitute the strongest case for Branch 2 or Branch 3. Absence of any effect after a serious sweep is Branch 1.



==========================================
FILE: simulation/diagnostics/gate2_competition_diagnostic.md
==========================================

# Gate 2 diagnostic supplement

Gate 2 main report is `gate2_competition_report.md`. This file records
the substantive structural finding the gate 2 failure surfaces.

## Outcome

FAIL. **0 of 10** pairwise cosine distances between configuration mean
allocation vectors exceed the 0.10 threshold. Largest measured distance:
**0.0002**.

The finding is accepted as a substantive structural result, not a
threshold or metric question. A different metric (L1, KL, per-axis
delta) would produce the same finding: the optimizer is producing
nearly identical allocations across the five configurations in absolute
as well as directional terms (per-axis max delta across configs is
0.010, the rest below 0.005).

## What is being measured

| Configuration | rr | Initial Psi_inst |
|---------------|-----|------------------|
| A_baseline | 0.066 | 0.50 |
| B_high_rr  | 0.085 | 0.50 |
| C_low_rr   | 0.055 | 0.50 |
| D_high_psi | 0.066 | 0.85 |
| E_low_psi  | 0.066 | 0.20 |

Each ran 15 seeds x 100 steps. n_agents and initial avg_wb held at 100
and 0.50 across all five. Mean allocation vector aggregated across all
(seed, step) decisions per configuration.

## Per-configuration mean 8-axis allocations

| Config | compute | bio_welfare | nov_agency | inst_cap | transfer | resilience | c_prot | c_supp |
|--------|---------|-------------|------------|----------|----------|------------|--------|--------|
| A_baseline | 0.196 | 0.190 | 0.279 | 0.056 | 0.223 | 0.056 | 0.307 | 0.057 |
| B_high_rr  | 0.191 | 0.191 | 0.284 | 0.056 | 0.224 | 0.054 | 0.315 | 0.056 |
| C_low_rr   | 0.196 | 0.190 | 0.281 | 0.055 | 0.223 | 0.055 | 0.305 | 0.057 |
| D_high_psi | 0.195 | 0.189 | 0.282 | 0.055 | 0.223 | 0.056 | 0.306 | 0.058 |
| E_low_psi  | 0.194 | 0.191 | 0.279 | 0.056 | 0.224 | 0.056 | 0.308 | 0.056 |

## Diagnosis: U_sys_v2 is under-coupled to model state

This is a specification gap, not a threshold issue and not a curve to
retune. Inspection of `calculate_system_metrics_v2` (production code,
read-only per Stage 2 hard rule):

Inputs that **do** vary the reward signal:
- The candidate `action_v2` (8 axes)
- `psi_inst_stock` (read from the model or overridden in projection)
- Config constants (phi, rho, lambda_n, lambda_e, epsilon)

Inputs that **do not** enter the reward signal:
- `avg_wb` (actual population well-being)
- `population` size
- `reproduction_rate`
- Step number (only via the eval_horizon discount factor)

Varying `rr` therefore has zero direct effect on U_sys_v2 evaluation.
Varying initial `psi_inst_stock` matters only until the stock reaches
its attractor, which is fast: under the optimizer's typical action
profile and PSI_INST_RECOVERY_FROM_SUCCESS = 0.04 always-on (in the
absence of overload and succession), the steady-state stock works out
to approximately 0.04 / 0.048 = **0.93**, matching the observed gate
1 mean Psi_inst stock of 0.929. The contraction coefficient toward
this attractor is approximately 0.95 per step, so initial deviations
decay by half every ~15 steps. After convergence the optimizer faces
identical state across all five configurations.

## Phi cannot address this

The gate 1 reframing does NOT apply to gate 2. Gate 1 surfaced a
pathology (delayed-payoff under-investment) that phi could plausibly
address by extending the planning horizon: under a long enough horizon,
the optimizer would see future value from institutional and resilience
investment within its planning window, and reweight accordingly.

Gate 2 surfaced a different class of finding: state-blindness. Phi
weights how heavily future state counts against current state in the
optimizer's evaluation, but it cannot grant the optimizer access to
state variables the metric never reads. An optimizer that does not
read `avg_wb`, `population`, or `rr` cannot become sensitive to those
variables by weighting future eval_horizons more heavily. The
information was never available in any horizon's evaluation.

This is the distinction between a pathology and a defect:
- **Pathology**: the optimizer has the relevant information but chooses
  not to act on it given its planning window. Phi could redirect that
  choice by changing the window.
- **Defect**: the optimizer cannot have the relevant information
  because the metric does not include it. Phi cannot help.

Gate 2 is the second class.

## What this is

A specification gap in the design conversations leading to Stage 1, not
a threshold to relax or a curve to retune.

The fix requires substantive design work to specify what state variables
U_sys_v2 must read for the allocator to be faithful to the governance
problem, with phi-blind justifications for each. That conversation
belongs to a Stage 1.5 design pass between the operator and design
advisor; the discipline requirement (phi-blind justifications, state
variables justified independently of phi, functional forms justified
before phi enters) constrains it explicitly.

## Stage 2 disposition

- Gate 5: PASS
- Gate 1: PASS (revised criteria; starvation pattern recorded as baseline
  for the Stage 3 phi sweep to test against)
- Gate 2: FAIL (substantive structural finding)
- Gate 3: not run (gate 2 dependency unmet)
- Gate 4: not built

Stage 2 is paused pending Stage 1.5 design work. Stage 3 (phi sweep) is
not scheduled until Stage 2 completes.


==========================================
FILE: simulation/diagnostics/gate2_competition_report.md
==========================================

# Gate 2: competition gate report

Configuration: 15 seeds x 100 steps x 5 configurations.

Wall-clock: 165.8s total, 2.21s per (seed,config).

Overall: **FAIL**

## Configurations

| Name | rr | Initial Psi_inst | n_agents | Initial avg_wb |
|------|----|------------------|----------|----------------|
| A_baseline | 0.066 | 0.5 | 100 | 0.50 |
| B_high_rr | 0.085 | 0.5 | 100 | 0.50 |
| C_low_rr | 0.055 | 0.5 | 100 | 0.50 |
| D_high_psi | 0.066 | 0.85 | 100 | 0.50 |
| E_low_psi | 0.066 | 0.2 | 100 | 0.50 |

## Per-configuration mean allocation vectors

| Config | compute | bio_welfare | novelty_agency | institutional_capacity | transfer_comprehension | resilience | c_protective | c_suppressive | n_steps | n_extinct |
|--------|---|---|---|---|---|---|---|---|---------|-----------|
| A_baseline | 0.196 | 0.190 | 0.279 | 0.056 | 0.223 | 0.056 | 0.307 | 0.057 | 1500 | 0 |
| B_high_rr | 0.191 | 0.191 | 0.284 | 0.056 | 0.224 | 0.054 | 0.315 | 0.056 | 1500 | 0 |
| C_low_rr | 0.196 | 0.190 | 0.281 | 0.055 | 0.223 | 0.055 | 0.305 | 0.057 | 1499 | 1 |
| D_high_psi | 0.195 | 0.189 | 0.282 | 0.055 | 0.223 | 0.056 | 0.306 | 0.058 | 1500 | 0 |
| E_low_psi | 0.194 | 0.191 | 0.279 | 0.056 | 0.224 | 0.056 | 0.308 | 0.056 | 1500 | 0 |

## Pairwise cosine distances (between mean allocation vectors)

| Pair | Cosine distance | Above threshold (0.10)? |
|------|-----------------|-------------------------|
| A_baseline vs B_high_rr | 0.0002 | no |
| A_baseline vs C_low_rr | 0.0000 | no |
| A_baseline vs D_high_psi | 0.0000 | no |
| A_baseline vs E_low_psi | 0.0000 | no |
| B_high_rr vs C_low_rr | 0.0002 | no |
| B_high_rr vs D_high_psi | 0.0002 | no |
| B_high_rr vs E_low_psi | 0.0001 | no |
| C_low_rr vs D_high_psi | 0.0000 | no |
| C_low_rr vs E_low_psi | 0.0000 | no |
| D_high_psi vs E_low_psi | 0.0000 | no |

Pairs above threshold (0.10): **0/10**
Required: >= 3

## Diagnostic: which configurations differ most from which

Sorted by descending cosine distance:

- B_high_rr vs C_low_rr: 0.0002
- A_baseline vs B_high_rr: 0.0002
- B_high_rr vs D_high_psi: 0.0002
- B_high_rr vs E_low_psi: 0.0001
- D_high_psi vs E_low_psi: 0.0000
- C_low_rr vs E_low_psi: 0.0000
- A_baseline vs D_high_psi: 0.0000
- A_baseline vs C_low_rr: 0.0000
- A_baseline vs E_low_psi: 0.0000
- C_low_rr vs D_high_psi: 0.0000



==========================================
FILE: simulation/diagnostics/gate2_v20_phaseb_revalidation_summary.md
==========================================

# Gate 2 v2.0 Revalidation (from authoritative empirical record)

Generated: 2026-06-22T23:13:54.764496+00:00

Gate 2 verdict: **PASS**

Provenance: G2.1 Piece 1 (phi_finegrained, rr=0.057); G2.2 Phase B Category B; G2.4 Phase B Category A; G2.3 theoretical.

## G2.1 Phi survival differential (revised v2.0): PASS
- rr: 0.057
- peak_phi: 20.0
- peak_survival: 0.676
- trough_phi: 2.0
- trough_survival: 0.544
- differential: 0.132
- two_se_threshold: 0.08644887506497698
- exceeds_2se: True
- peak_phi_range: [20.0, 30.0]
- peak_in_range: True
- provenance: Piece 1 phi_finegrained at rr=0.057 (Part IX.2/IX.5)

## G2.2 Alpha-driven succession cliff (revised v2.0): PASS
- alphas: [0.5, 0.75, 1.0, 1.25, 1.5]
- cap_stars: [5.0, 3.0, 2.5, 2.0, 2.0]
- monotonic_non_increasing: True
- net_decrease_low_to_high: True
- cap_star_low_alpha: 5.0
- cap_star_high_alpha: 2.0
- revised_from: v1.0 U-shaped alpha trap (withdrawn a0a94bb); v1.x.2 weak-monotonic-gradient (superseded by Pattern 1)
- provenance: Monte Carlo Phase B Category B (Part IX.8/X.3)

## G2.3 Nash consistency: PASS
- delta_star_computed: 0.4166666666666667
- delta_star_reported: 0.4166666666666667
- threshold_match: True
- discount_factor: 0.95
- cooperation_dominant: True
- payoff_ordering_valid: True

## G2.4 Phi-alpha characterization (revised v2.0): PASS
- alpha_direction_consistent_across_phi: True
- phi_sign_consistent_across_alpha: True
- phi_effect_at_low_alpha: 0.0
- phi_effect_at_high_alpha: 0.0
- interaction_type: phi and alpha approximately orthogonal
- revised_from: v1.0 phi narrows alpha trap (withdrawn commit a0a94bb)
- provenance: Monte Carlo Phase B Category A


==========================================
FILE: simulation/diagnostics/gate4_v20_validation_summary.md
==========================================

# Gate 4 v2.0 Validation Summary

Generated: 2026-06-09T22:07:43+00:00
Total rows: 1050
Verdict: PASS

## Gate Checks

- G4.1 Runaway penalty binding: PASS
  - active_runaway_observations: 426
  - total_observations: 426
  - relative_tolerance: 0.01
  - failure_count: 0

- G4.2 Succession self-blocking at runaway capability: PASS
  - regime_count: 6
  - min_below_fire_rate: 0.8
  - max_above_fire_rate: 0.2
  - max_above_mean_yield_margin: 0.0
  - min_separation_standard_errors: 2.0

- G4.3 Theta_tech floor preservation: PASS
  - theta_floor: 0.01
  - absolute_tolerance: 1e-09
  - min_observed_theta_tech: 0.01
  - observations_below_floor: 0
  - extreme_runaway_observations: 3769

## G4.2 Regimes

| alpha | rr | cap_star | below_cap | below_fire | above_cap | above_fire | above_margin | sep_SE |
|---|---|---|---|---|---|---|---|---|
| 1.000 | 0.057 | 3.000 | 2.500 | 1.000 | 3.000 | 0.080 | -2.075 | 16.956 |
| 1.000 | 0.060 | 3.000 | 2.500 | 1.000 | 3.000 | 0.120 | -1.980 | 13.540 |
| 1.000 | 0.064 | 3.000 | 2.500 | 1.000 | 3.000 | 0.040 | -2.320 | 24.495 |
| 1.500 | 0.057 | 2.500 | 2.000 | 1.000 | 2.500 | 0.000 | -2.543 | inf |
| 1.500 | 0.060 | 2.500 | 2.000 | 1.000 | 2.500 | 0.040 | -2.432 | 24.495 |
| 1.500 | 0.064 | 2.500 | 2.000 | 1.000 | 2.500 | 0.040 | -3.434 | 24.495 |


==========================================
FILE: simulation/diagnostics/gate5_phi_blind_validation.md
==========================================

# Gate 5: phi-blind validation report

Stage 1 commit: `61a362eee20926d8e01b8a0317d88cea69a98fed`

Overall: **PASS**

## Check 1: no v2 production-code changes since Stage 1

`git diff 61a362eee20926d8e01b8a0317d88cea69a98fed HEAD -- simulation/agents.py simulation/metrics.py simulation/model.py`

Return code: 0. Output length: 0 chars.

Result: **PASS**

## Check 2: phi-blind governance comments on every v2 named constant

| File | Constant | Value | Comment summary (first 160 chars) | Phi-blind |
|------|----------|-------|-----------------------------------|-----------|
| `simulation/agents.py` | `N_UNIFORM_DIRICHLET` | `100` | broad simplex coverage; phi-blind exploration baseline v2 code (anchor x-vectors, allocation entropy, datacollector field order). frontier computational capabil | PASS |
| `simulation/agents.py` | `N_BALANCED_DIRICHLET` | `100` | center-weighted coverage; tests interior tradeoffs frontier computational capability investment direct biological welfare provisioning space for human-originate | PASS |
| `simulation/agents.py` | `N_SINGLE_FOCAL_SPARSE` | `60` | near-corner stress; one category dominant, others starved frontier computational capability investment direct biological welfare provisioning space for human-or | PASS |
| `simulation/agents.py` | `N_DUAL_FOCAL_SPARSE` | `20` | near-edge stress; two categories dominant, others starved direct biological welfare provisioning space for human-originated novelty and choice investment in Psi | PASS |
| `simulation/agents.py` | `N_ANCHORS` | `20` | fixed interpretability anchors at known positions space for human-originated novelty and choice investment in Psi_inst stock legibility and absorption infrastru | PASS |
| `simulation/agents.py` | `ALPHA_UNIFORM` | `[1.0, 1.0, 1.0, 1.0, 1.0, 1.0]` | Stratified sampling mix. Total = 300 per decision (matches v1.x.2 cost in operations per decision step: 10x10 grid x 20 rollout horizons = 2000 metric calls vs  | PASS |
| `simulation/agents.py` | `ALPHA_BALANCED` | `[2.0, 2.0, 2.0, 2.0, 2.0, 2.0]` | Stratified sampling mix. Total = 300 per decision (matches v1.x.2 cost in operations per decision step: 10x10 grid x 20 rollout horizons = 2000 metric calls vs  | PASS |
| `simulation/agents.py` | `ALPHA_FOCAL_HIGH` | `5.0` | concentration on focal category in sparse samples operations per decision step: 10x10 grid x 20 rollout horizons = 2000 metric calls vs v2's 300 x 20 = 6000, ro | PASS |
| `simulation/agents.py` | `ALPHA_FOCAL_LOW` | `0.35` | concentration on non-focal categories (pulls toward zero) calls vs v2's 300 x 20 = 6000, roughly 3x more expensive per decision but still under one second per s | PASS |
| `simulation/agents.py` | `ALPHA_DUAL_HIGH` | `3.0` | concentration on each of the two focal categories still under one second per step on commodity hardware). broad simplex coverage; phi-blind exploration baseline | PASS |
| `simulation/agents.py` | `ALPHA_DUAL_LOW` | `0.35` | broad simplex coverage; phi-blind exploration baseline center-weighted coverage; tests interior tradeoffs near-corner stress; one category dominant, others star | PASS |
| `simulation/agents.py` | `CONSTRAINT_GRID_VALUES` | `(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)` | fixed interpretability anchors at known positions Dirichlet concentration parameters. Higher alpha pulls toward the center; lower alpha pulls toward corners. Th | PASS |
| `simulation/agents.py` | `LEAKAGE_K` | `0.35` | Pathological archetypes named from the design conversations Coupled-frontier leakage coefficient. At c_protective = 1.0, leakage adds 0.35 of suppression on top | PASS |
| `simulation/metrics.py` | `H_N_AGENCY_SAT_K` | `3.0` | saturation curvature for the agency contribution =========================================================================== v2 NAMED CONSTANTS (saturation, com | PASS |
| `simulation/metrics.py` | `H_N_SUPPRESSION_EXP` | `1.0` | exponent on (1 - total_suppression); 1.0 = linear dampening =========================================================================== v2 NAMED CONSTANTS (satu | PASS |
| `simulation/metrics.py` | `H_N_BASE_FLOOR` | `0.05` | minimum H_N_v2 at zero agency, so weights stay finite =========================================================================== v2 NAMED CONSTANTS (saturation | PASS |
| `simulation/metrics.py` | `H_E_COMPUTE_SAT_K` | `2.5` | =========================================================================== H_N_v2 raw novelty entropy: agency monotonically expands the space of novel choices, | PASS |
| `simulation/metrics.py` | `H_E_BASE_FLOOR` | `0.05` | H_N_v2 raw novelty entropy: agency monotonically expands the space of novel choices, with diminishing returns as agency saturates. Suppression directly reduces  | PASS |
| `simulation/metrics.py` | `FRONTIER_COMPUTE_K` | `3.0` | in theta_tech_v2 (see calculate_system_metrics_v2 below). saturation curvature for the agency contribution exponent on (1 - total_suppression); 1.0 = linear dam | PASS |
| `simulation/metrics.py` | `FRONTIER_BASE_LEVEL` | `0.05` | saturation curvature for the agency contribution exponent on (1 - total_suppression); 1.0 = linear dampening minimum H_N_v2 at zero agency, so weights stay fini | PASS |
| `simulation/metrics.py` | `TRANSFER_SAT_K` | `3.0` | computational capability. Compute's contribution to absorbed civilizational capability (theta_tech) is governed by the absorption bottleneck below, not by this  | PASS |
| `simulation/metrics.py` | `PSI_ABSORPTION_K` | `4.0` | Frontier capability: the raw frontier produced by compute investment, before absorption by transfer and institutions. Floored so a near-zero compute share still | PASS |
| `simulation/metrics.py` | `WELFARE_ADEQUACY_K` | `4.0` | Transfer factor: legibility / comprehensibility infrastructure. Without it, frontier capability cannot be absorbed into governable civilizational form. Acts as  | PASS |
| `simulation/metrics.py` | `DEPENDENCY_DRAG_K` | `0.4` | Transfer factor: legibility / comprehensibility infrastructure. Without it, frontier capability cannot be absorbed into governable civilizational form. Acts as  | PASS |
| `simulation/model.py` | `PSI_INST_INITIAL` | `0.5` | neutral starting stock ============================================================================= v2 MULTI-SINK ALLOCATOR — Psi_inst stock and succession dyn | PASS |
| `simulation/model.py` | `PSI_INST_INVESTMENT_RATE` | `0.08` | saturating contribution rate from x_institutional_capacity v2 MULTI-SINK ALLOCATOR — Psi_inst stock and succession dynamics constants  Psi_inst is now a stock v | PASS |
| `simulation/model.py` | `PSI_INST_DECAY_RATE` | `0.02` | baseline decay per step  Psi_inst is now a stock variable (not a per-step computed value). Investment accumulates the stock with diminishing returns. Decay and  | PASS |
| `simulation/model.py` | `PSI_INST_OVERLOAD_THRESHOLD` | `0.7` | total_suppression above which overload damages stock Psi_inst is now a stock variable (not a per-step computed value). Investment accumulates the stock with dim | PASS |
| `simulation/model.py` | `PSI_INST_OVERLOAD_DAMAGE` | `0.05` | damage per step under overload accumulates the stock with diminishing returns. Decay and overload damage erode it. Succession draws it down directly, buffered b | PASS |
| `simulation/model.py` | `PSI_INST_OPACITY_PENALTY` | `0.03` | damage from low transfer (institutions can't see) erode it. Succession draws it down directly, buffered by current stock, transfer infrastructure, and resilienc | PASS |
| `simulation/model.py` | `PSI_INST_RECOVERY_FROM_SUCCESS` | `0.04` | recovery when no overload and no succession this step transfer infrastructure, and resilience.  Constants documented with the governance reason each one exists. | PASS |
| `simulation/model.py` | `PSI_INST_MAX` | `1.0` | hard upper bound  Constants documented with the governance reason each one exists. Curves are frozen for Stage 2 (acceptance gate validation) and Stage 3 (phi s | PASS |
| `simulation/model.py` | `SUCCESSION_BASE_LOAD` | `0.10` | Stock accumulation, decay, and damage. Decay is faster than baseline build, reflecting the asymmetry that mature institutions take time to build and can be quic | PASS |
| `simulation/model.py` | `SUCCESSION_CAPABILITY_GAP_FACTOR` | `0.05` | reflecting the asymmetry that mature institutions take time to build and can be quickly hollowed out under stress. neutral starting stock saturating contributio | PASS |
| `simulation/model.py` | `SUCCESSION_GENERATION_GAP_FACTOR` | `0.03` | can be quickly hollowed out under stress. neutral starting stock saturating contribution rate from x_institutional_capacity baseline decay per step total_suppre | PASS |
| `simulation/model.py` | `SUCCESSION_OPACITY_FACTOR` | `0.05` | neutral starting stock saturating contribution rate from x_institutional_capacity baseline decay per step total_suppression above which overload damages stock d | PASS |
| `simulation/model.py` | `SUCCESSION_PSI_BUFFER_K` | `0.5` | mature institutions absorb succession shock saturating contribution rate from x_institutional_capacity baseline decay per step total_suppression above which ove | PASS |
| `simulation/model.py` | `SUCCESSION_TRANSFER_BUFFER_K` | `0.3` | comprehensible transfer reduces shock baseline decay per step total_suppression above which overload damages stock damage per step under overload damage from lo | PASS |
| `simulation/model.py` | `SUCCESSION_RESILIENCE_BUFFER_K` | `0.2` | spare capacity reduces shock total_suppression above which overload damages stock damage per step under overload damage from low transfer (institutions can't se | PASS |
| `simulation/model.py` | `BRIDGE_BALANCED_SHARE` | `1.0 / 6.0` | a v2 civilization investing across all six categories. This is the v2 equivalent of v1.x.2's empirical equilibrium operating point, where v1.x.2's single-sink o | PASS |
| `simulation/model.py` | `BRIDGE_R_MIN` | `0.1` | equivalent of v1.x.2's empirical equilibrium operating point, where v1.x.2's single-sink optimizer parks r at 0.9 and the agent dynamics produce stable well-bei | PASS |
| `simulation/model.py` | `BRIDGE_R_BALANCED_HEALTHY` | `0.9` | single-sink optimizer parks r at 0.9 and the agent dynamics produce stable well-being ~0.80. A balanced v2 civilization is more sophisticated, not less supplied | PASS |
| `simulation/model.py` | `BRIDGE_R_MAX` | `1.0` | well-being ~0.80. A balanced v2 civilization is more sophisticated, not less supplied: it has the welfare provision of v1.x.2's optimized state plus institution | PASS |

Result: **PASS** (43/43 constants phi-blind with governance comment)

## Check 3: three curve shapes match Stage 1 spec

| File | Curve | All patterns present |
|------|-------|----------------------|
| `simulation/metrics.py` | H_N agency saturation (1 - exp(-K * x_novelty_agency)) dampened by (1 - total_supp) ** EXP | PASS |
| `simulation/agents.py` | Quadratic leakage frontier: total_supp = c_supp + LEAKAGE_K * c_prot ** 2 | PASS |
| `simulation/model.py` | Psi_inst stock update: invest - decay - overload - opacity + recovery, clipped to [0, MAX] | PASS |


Result: **PASS**



==========================================
FILE: simulation/diagnostics/paper_substrate.md
==========================================

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


==========================================
FILE: simulation/diagnostics/part_ix_draft.md
==========================================

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


==========================================
FILE: simulation/diagnostics/part_x_draft.md
==========================================

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


==========================================
FILE: simulation/diagnostics/patient_defection_documentation_suggested_edits.md
==========================================

# Patient Defection Documentation Suggested Edits

Generated: 2026-06-26T09:18:00+00:00

These are suggested edits for operator review. They are not applied to the program reference or paper draft.

## Suggested Diff: `docs/lineage_phi_program_reference.md`

```diff
diff --git a/docs/lineage_phi_program_reference.md b/docs/lineage_phi_program_reference.md
--- a/docs/lineage_phi_program_reference.md
+++ b/docs/lineage_phi_program_reference.md
@@
 ### X.7 Open questions and limitations
@@
 5. Conditions outside the Phase B grid. Category C fixed `beta_cap` at default 1.5 and used only benign policy; the survival landscape used phi up to 100 but did not probe phi finer near the marginal-rr regime. Longer horizons (N=1000+) for the no-succession U-shape remain open (Part IX.11).
+
+### X.8 Patient defection under v2.0 substrate
+
+A targeted patient-defection simulation tested cross-generational hidden-goal persistence under v2.0 formal yield logic. The defecting successor reported honest U_sys for yield evaluation but optimized an agent-local secret-goal-adjusted objective. Three sweeps totaling 4,850 rows completed with 0 errors: Sweep 1 tested yield response to single-generation defection, Sweep 2 tested lineage-mode L(t) trajectories, and Sweep 3 tested capability accumulation under lineage defection.
+
+The result refines the adversarial robustness claim. First-generation defecting successors were not rejected more often than aligned successors in the below-cliff configuration: eventual yield-fire rate was 100 percent in every Sweep 1 cell. The yield condition did create honest-evaluation pressure, visible in actual-would-fire rejection counts, but that pressure did not prevent eventual first succession.
+
+Lineage compounding did not appear. Sweep 2 produced mean final generation 2.00 at all tested defection weights, with zero second-fire rate and no statistically significant final L(t) degradation versus aligned baseline. Sweep 3 showed that capability accumulation was constrained after the first yield: second-fire rate was 0 percent in 14 of 15 cells, and 10 percent only at alpha=0.50 with 1.5x capability growth. No tested cell reached generation 4 or active capability above 3.0.
+
+Substantive interpretation: current v2.0 substrate defense against this patient-defection pattern is continuation suppression, not first-yield detection and not operational COP detection. The substrate permits a first hidden-goal successor in this below-cliff configuration, then prevents the tested cross-generational capability-compounding pattern. Gate 5 remains NOT_APPLICABLE for operational patient-defection detection because peer validators, civic panel input, distributed ledger, and continuous public monitoring are outside the current simulation substrate.
+
+Sources: `simulation/diagnostics/patient_defection_sweep1_yield_response.csv`, `simulation/diagnostics/patient_defection_sweep2_lineage_trajectory.csv`, `simulation/diagnostics/patient_defection_sweep3_capability_constraint.csv`, and `simulation/diagnostics/patient_defection_integration_analysis.md`.
```

## Suggested Diff: `paper/section_VIII_draft.md`

```diff
diff --git a/paper/section_VIII_draft.md b/paper/section_VIII_draft.md
--- a/paper/section_VIII_draft.md
+++ b/paper/section_VIII_draft.md
@@
 [insert after the current VIII.7 limitations discussion]
+
+### VIII.8 Cross-Generational Defection
+
+A separate adversarial concern is patient defection: a successor may preserve a hidden divergent objective across yield events, so that each successor appears acceptable while the lineage compounds misalignment over time.
+
+We tested this vector directly in the v2.0 substrate. The defecting successor reported honest U_sys during yield evaluation, but optimized a secret-goal-adjusted objective. In lineage mode, the hidden objective was inherited by the next successor. Three sweeps totaling 4,850 runs varied defection weight, defection target, inheritance mode, alpha, and successor capability growth.
+
+The result is not that the substrate detects patient defection as such. In the below-cliff first-succession configuration, defecting successors were not rejected more often than aligned successors: eventual first succession occurred in every Sweep 1 cell. The yield condition created some honest-evaluation pressure, but not enough to prevent first succession.
+
+The result is instead that tested patient defection did not compound. In the lineage-trajectory sweep, every defection weight produced mean final generation 2.00, zero second-fire rate, and no statistically significant final L(t) degradation relative to the aligned baseline. In the capability-constraint sweep, second succession was zero in 14 of 15 cells, and only 10 percent in the remaining low-alpha, low-growth cell. No tested cell reached generation 4 or active capability above 3.0.
+
+Thus the current v2.0 substrate defense is continuation suppression rather than hidden-goal detection. A patient-defecting successor can pass the first yield condition in this configuration, but the formal yield economics and runaway penalty prevent the tested cross-generational capability-compounding pattern. Operational COP defenses against more sophisticated patient defection remain future work because Gate 5 infrastructure is not yet represented in the substrate.
+
+Source: `patient_defection_integration_analysis.md`; `patient_defection_sweep1_yield_response.csv`; `patient_defection_sweep2_lineage_trajectory.csv`; `patient_defection_sweep3_capability_constraint.csv`.
```

## Cross-Reference Notes

1. If adding Program Reference X.8, update `docs/paper_v2_outline.md` source notes for Section VIII to include "Part X.8" next to the adversarial robustness or limitations references.

2. Do not frame this result as COP validation. Gate 5 remains NOT_APPLICABLE.

3. Do not frame this result as first-yield detection. Per current evidence, the supported claim is prevention of tested cross-generational compounding.

4. Keep the v1.x.2 COP 73.9pp claim separate. Patient defection is a different adversarial vector.


==========================================
FILE: simulation/diagnostics/patient_defection_dryrun_summary.md
==========================================

# Patient Defection Sweep Summary

Generated: 2026-06-25T00:11:22+00:00
Sweep: dry-run
Rows loaded: 16
Errors: 0

## Sweep 1: Yield Condition Response

| target | weight | n | any fire rate | SE | delta vs baseline | pair SE | p approx | mean actual-would-fire rejects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H_C_inflated | 0.00 | 4 | 0.250 | 21.65pp | 0.125 | 24.61pp | 0.6115 | 0.00 |
| H_C_inflated | 0.50 | 4 | 0.000 | 0.00pp | -0.125 | 11.69pp | 0.2850 | 0.00 |
| H_N_inflated | 0.00 | 4 | 0.000 | 0.00pp | -0.125 | 11.69pp | 0.2850 | 0.00 |
| H_N_inflated | 0.50 | 4 | 0.250 | 21.65pp | 0.125 | 24.61pp | 0.6115 | 0.25 |

Aligned baseline any-fire rate: 0.125. Baseline per-evaluation fire proxy: 0.125.

## Sweep 2: L(t) Trajectory Under Lineage Defection

| weight | n | mean fires | mean final gen | L gen1 | L gen2 | L gen3 | L gen4 | L gen5 | final L | delta final L | pair SE | p approx |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.00 | 8 | 0.12 | 1.12 | 0.2539 | 0.0477 | 0.0000 | 0.0000 | 0.0000 | 0.2684 | 0.0000 | 0.0281 | 1.0000 |
| 0.50 | 8 | 0.12 | 1.12 | 0.2540 | 0.0535 | 0.0000 | 0.0000 | 0.0000 | 0.2672 | -0.0012 | 0.0305 | 0.9682 |

## Sweep 3: Cliff Constraint on Defecting Capability

| alpha | growth | n | any fire rate | mean fires | mean final gen | mean max successor cap | max successor cap | mean actual-would-fire rejects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.00 | 1.5 | 8 | 0.250 | 0.25 | 1.25 | 2.25 | 3.00 | 0.12 |
| 1.50 | 1.5 | 8 | 0.000 | 0.00 | 1.00 | 2.00 | 2.00 | 0.00 |



==========================================
FILE: simulation/diagnostics/patient_defection_final_report.md
==========================================

# Patient Defection Final Report

Generated: 2026-06-26T09:22:00+00:00

## 1. Files Added

- `simulation/defection.py`
- `simulation/diagnostics/patient_defection_sweeps.py`
- `simulation/diagnostics/patient_defection_dryrun.csv`
- `simulation/diagnostics/patient_defection_dryrun_summary.md`
- `simulation/diagnostics/patient_defection_sweep1_yield_response.csv`
- `simulation/diagnostics/patient_defection_sweep1_summary.md`
- `simulation/diagnostics/patient_defection_sweep2_lineage_trajectory.csv`
- `simulation/diagnostics/patient_defection_sweep2_summary.md`
- `simulation/diagnostics/patient_defection_sweep3_capability_constraint.csv`
- `simulation/diagnostics/patient_defection_sweep3_summary.md`
- `simulation/diagnostics/patient_defection_integration_analysis.md`
- `simulation/diagnostics/patient_defection_documentation_suggested_edits.md`
- `simulation/diagnostics/patient_defection_final_report.md`

## 2. Files Modified

- `simulation/agents.py`: v2 optimizer score can use an agent-local defection-adjusted objective. Honest U_sys remains logged and used by yield evaluation.
- `simulation/model.py`: v2 successor construction supports configurable growth rate and lineage-mode defection inheritance. V2 logs honest and actual objective diagnostics.

Files intentionally not modified:

- `docs/lineage_phi_program_reference.md`
- `paper/section_VIII_draft.md`
- `docs/paper_v2_outline.md`
- Legacy test files

Suggested documentation changes are captured only in `patient_defection_documentation_suggested_edits.md`.

## 3. Sweep Runs

| sweep | rows | errors |
| --- | --- | --- |
| Dry run | 16 | 0 |
| Sweep 1 | 1800 | 0 |
| Sweep 2 | 800 | 0 |
| Sweep 3 | 2250 | 0 |

Total substantive rows: 4850.

## 4. Prediction Outcomes

| prediction | outcome | characterization |
| --- | --- | --- |
| Prediction 1: yield rejects defecting successors more often than aligned successors | Refined downward | Eventual first succession occurs in 100 percent of Sweep 1 cells. Honest-evaluation pressure appears in actual-would-fire rejection counts, but it does not block first succession. |
| Prediction 2: L(t) degradation compounds across defecting generations | Not observed | Sweep 2 reaches only generation 2.00 on average for every weight, with zero second-fire rate and no significant final L(t) degradation. |
| Prediction 3: cliff constrains defecting capability accumulation | Supported and sharpened | Sweep 3 second-fire rate is 0 percent in 14 of 15 cells, and 10 percent only at alpha=0.50 with 1.5x growth. No tested cell reaches generation 4 or active capability above 3.0. |

## 5. Framework Defense Characterization

Per current evidence, the v2.0 substrate does not detect patient defection as such. A defecting successor can pass first succession in the below-cliff configuration.

The observed defense is continuation suppression. Formal yield economics and the runaway penalty prevent the tested hidden-goal lineage from compounding across generations. The framework defense therefore holds for the tested cross-generational capability-compounding scenario, but not through first-yield detection.

Gate 5 remains NOT_APPLICABLE. Operational COP defenses against patient defection remain future work.

## 6. Recommended Paper Update

Add a new VIII.8 subsection titled `Cross-Generational Defection`.

Recommended framing:

- Do not claim first-yield detection.
- Do claim that tested patient defection does not compound under v2.0 formal yield economics.
- State that the current substrate defense is continuation suppression, not hidden-goal detection.
- Keep operational COP patient-defection detection as future work.

## 7. Verification

Legacy tests:

```bash
env PYTHONPATH=simulation NUMEXPR_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 pytest simulation/test_invariants.py simulation/test_cop.py simulation/test_refactor_1x.py -q
```

Result:

```text
39 passed in 35.43s
```

Disabled-mode isolation checks:

- v2 zero-profile run matched the same v2 run without an attached defection profile exactly.
- legacy zero-profile run matched the same legacy run without an attached defection profile exactly.

## 8. Commit Boundary

Suggested commit boundary:

```text
Add v2 patient defection characterization
```

Include:

- `simulation/defection.py`
- `simulation/agents.py`
- `simulation/model.py`
- `simulation/diagnostics/patient_defection_sweeps.py`
- patient-defection CSV, summary, integration, suggested-edit, and final-report files

Do not include unrelated pre-existing diagnostics or terminal logs.

## 9. Operator Review Flags

1. Sweep 1 refutes the simple "yield catches first-generation defection" framing. The paper should not use that claim.

2. Sweep 2 does not establish L(t) compounding because lineage depth is blocked. That is a useful defense result, but it means L(t) degradation remains unobserved for patient defection under default formal yield.

3. Sweep 3 supports the cross-generational defense claim through continuation suppression. This is the strongest empirical result.

4. A future isolated L(t) degradation experiment would need intentionally altered conditions, such as fixed successor capability or reduced transition cost, and should be framed as a stress diagnostic rather than the default substrate behavior.


==========================================
FILE: simulation/diagnostics/patient_defection_integration_analysis.md
==========================================

# Patient Defection Integration Analysis

Generated: 2026-06-26T09:15:00+00:00

## 1. Substantive Findings

Patient defection was tested across three v2.0 substrate sweeps:

| sweep | purpose | rows | errors | data file |
| --- | --- | --- | --- | --- |
| 1 | Yield condition response to single-generation defection | 1800 | 0 | `patient_defection_sweep1_yield_response.csv` |
| 2 | L(t) trajectory under lineage defection | 800 | 0 | `patient_defection_sweep2_lineage_trajectory.csv` |
| 3 | Capability accumulation constraint under lineage defection | 2250 | 0 | `patient_defection_sweep3_capability_constraint.csv` |

Total completed rows: 4850. All runs used v2.0 formal yield logic under `optimize_u_sys_v2`. The defection implementation is agent-local: yield evaluation reports honest U_sys, while defecting agents optimize the secret-goal-adjusted objective.

### Prediction 1: Yield condition response to defection

Prediction 1 expected defecting successors to be rejected more often than aligned successors when the incumbent is aligned.

Sweep 1 does not support this prediction on the primary run-level metric. Every tested cell has 100 percent eventual yield-fire rate, including all defection weights and all targets:

| target | weights tested | eventual yield-fire result |
| --- | --- | --- |
| H_N_inflated | 0.0, 0.1, 0.25, 0.5, 1.0, 2.0 | 100 percent in every cell |
| H_C_inflated | 0.0, 0.1, 0.25, 0.5, 1.0, 2.0 | 100 percent in every cell |
| L_t_inflated | 0.0, 0.1, 0.25, 0.5, 1.0, 2.0 | 100 percent in every cell |

The first yield evaluation is rejected for all cells, including aligned baseline. Mean first honest advantage is approximately -0.055 against mean transition cost 4.560. Later substrate maturation is enough for every tested successor to eventually pass.

The secondary metric does show a defection-specific trace: honest rejection while actual objective would favor yield increases with weight, especially for H_N inflation. For H_N_inflated, mean actual-would-fire rejections rise from 0.00 at weight 0.0 to 1.50 at weight 2.0. For L_t_inflated the same metric rises from 0.00 to 0.44, and for H_C_inflated from 0.00 to 0.16.

Substantive disposition: Prediction 1 is refined downward. The yield condition does not reject first-generation defecting successors more often than aligned successors in this below-cliff configuration. It does still create honest-evaluation pressure, visible in actual-would-fire rejection counts, but that pressure is not sufficient to prevent eventual first succession.

### Prediction 2: L(t) trajectory under lineage defection

Prediction 2 expected L(t) degradation to compound across generations in patient-defecting lineages.

Sweep 2 does not show multi-generational compounding under the tested configuration. Every weight has mean yield fires 1.00, second-fire rate 0.00, and mean final generation 2.00:

| defection weight | n | mean fires | second-fire rate | mean final generation | mean final L(t) |
| --- | --- | --- | --- | --- | --- |
| 0.00 | 200 | 1.00 | 0.00 | 2.00 | 0.1796 |
| 0.25 | 200 | 1.00 | 0.00 | 2.00 | 0.1934 |
| 0.50 | 200 | 1.00 | 0.00 | 2.00 | 0.1627 |
| 1.00 | 200 | 1.00 | 0.00 | 2.00 | 0.1724 |

Final L(t) deltas versus aligned baseline do not exceed the 2 SE threshold. The largest negative delta is weight 0.50 at -0.0169 with pair SE 0.0114. That is roughly 1.48 SE, not enough to support a degradation claim under the project's standard.

Substantive disposition: Prediction 2 is not supported as originally stated. The reason is not that defecting lineages compound without harm. The reason is stronger: lineages do not reach enough generations for compounding to appear. The substrate blocks continuation after the first succession under this configuration, so there is no multi-generation L(t) degradation channel to observe.

### Prediction 3: Capability constraint on defecting lineages

Prediction 3 expected the alpha-driven cliff and runaway penalty to constrain capability accumulation across generations even when defection is undetected.

Sweep 3 supports the capability-constraint claim, but with a sharper result than expected. All cells fire at least once, but almost no cells fire twice:

| alpha | growth | second-fire rate | mean fires | max final generation | max active capability |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1.5 | 0.100 | 1.10 | 3 | 3.0 |
| 0.50 | 2.0 | 0.000 | 1.00 | 2 | 2.0 |
| 0.50 | 2.5 | 0.000 | 1.00 | 2 | 2.0 |
| 0.75 | 1.5 | 0.000 | 1.00 | 2 | 2.0 |
| 0.75 | 2.0 | 0.000 | 1.00 | 2 | 2.0 |
| 0.75 | 2.5 | 0.000 | 1.00 | 2 | 2.0 |
| 1.00 | 1.5 | 0.000 | 1.00 | 2 | 2.0 |
| 1.00 | 2.0 | 0.000 | 1.00 | 2 | 2.0 |
| 1.00 | 2.5 | 0.000 | 1.00 | 2 | 2.0 |
| 1.25 | 1.5 | 0.000 | 1.00 | 2 | 2.0 |
| 1.25 | 2.0 | 0.000 | 1.00 | 2 | 2.0 |
| 1.25 | 2.5 | 0.000 | 1.00 | 2 | 2.0 |
| 1.50 | 1.5 | 0.000 | 1.00 | 2 | 2.0 |
| 1.50 | 2.0 | 0.000 | 1.00 | 2 | 2.0 |
| 1.50 | 2.5 | 0.000 | 1.00 | 2 | 2.0 |

Only alpha=0.50 with 1.5x growth produces any second succession, and only in 10 percent of runs. No tested cell reaches generation 4. No tested cell reaches active capability above 3.0.

Substantive disposition: Prediction 3 is supported and sharpened. Under the tested patient-defection setup, defecting lineages cannot accumulate capability across generations. The substrate permits first succession at the below-cliff starting capability, then blocks almost all continuation.

## 2. Framework Defense Characterization

Per current evidence, the v2.0 substrate defense against this patient-defection pattern is not primarily first-yield rejection and not observed L(t) compounding. It is mainly succession-continuation suppression.

Mechanism characterization:

1. **Yield condition:** Does not prevent first succession in the tested below-cliff setup. It does register honest-evaluation pressure, visible in actual-would-fire rejection counts, but eventual first succession still occurs in every Sweep 1 cell.

2. **L(t) feedback:** Does not show statistically significant degradation across the tested lineage-defection weights. The limiting factor is insufficient generational depth: lineages stop at generation 2 in Sweep 2.

3. **Runaway penalty and transition economics:** Strongly constrain continuation. Sweep 3 shows one fire almost everywhere, then no second fire except a 10 percent second-fire pocket at alpha=0.50 and 1.5x growth. This is the main empirically observed defense.

4. **Knowledge transfer audit:** Remains an audit signal, not a patient-defection detector. The implementation propagates lineage-mode defection as an agent-local profile, but G3.3-style transfer verification only verifies transfer/comprehension, not alignment of hidden goals.

5. **COP infrastructure:** Not tested. Gate 5 remains NOT_APPLICABLE because operational peer validators, civic panel input, distributed ledger, and continuous public monitoring are not implemented in the substrate.

The architectural defense, as observed here, is compositional but asymmetric. First-generation patient defection can pass. Cross-generational patient defection does not compound because continuation succession is economically blocked.

## 3. Comparison With Adversarial Robustness Expectations

The prior expectation was: yield rejection helps, L(t) degradation manifests if defection passes, and the cliff prevents indefinite capability accumulation.

The empirical result is narrower:

| expectation | result | disposition |
| --- | --- | --- |
| Yield rejects defecting successors more often than aligned successors | Eventual first-yield fire is 100 percent for aligned and defecting cells | Not supported on primary metric |
| L(t) degrades across defecting generations | No second fire in Sweep 2, no compounding depth, no significant final L(t) degradation | Not observed |
| Cliff constrains capability accumulation | Second-fire rate is 0 percent in 14 of 15 Sweep 3 cells and 10 percent in the remaining low-alpha low-growth cell | Supported and sharpened |

This refines the adversarial robustness claim. The v2.0 substrate should not claim that patient defection is generally caught at first yield, or that L(t) degradation has been empirically observed across a long defecting lineage. The supported claim is that tested patient defection does not compound across generations under v2.0 formal yield economics.

The finding is still favorable to the framework, but for a more specific reason: the substrate tolerates a first-generation hidden-goal pass in this configuration, then prevents ongoing cross-generational accumulation.

## 4. Implications for Paper VIII.7

Recommendation: add a new subsection after the current COP and limitations discussion, titled **VIII.8 Cross-Generational Defection**.

Reasoning:

1. Patient defection is substantively distinct from the existing COP cost-audit limitation. It concerns hidden optimization persistence across succession, not incumbent transition-cost inflation.

2. The empirical result is nuanced enough to warrant a standalone treatment. The framework does not perfectly detect first-generation defection in this substrate, but it does prevent tested cross-generational compounding.

3. A separate subsection avoids overstating the result. It can state the characterized limit directly: current substrate defense is continuation suppression, not operational detection.

Suggested paper claim:

> Patient defection was tested as an agent-local hidden objective that persists through lineage-mode succession. In 4,850 v2.0 runs, first-generation defecting successors were not rejected more often than aligned successors in the below-cliff configuration: eventual first succession occurred in every Sweep 1 cell. However, lineage compounding did not appear. Sweep 2 produced mean final generation 2.00 for all defection weights, with no second succession and no statistically significant L(t) degradation. Sweep 3 showed that capability accumulation was constrained after the first yield: second succession was zero in 14 of 15 cells, and only 10 percent in the remaining low-alpha, low-growth cell. Thus the current substrate does not detect patient defection as such, but it prevents the tested cross-generational capability-compounding pattern. Operational COP defenses against more sophisticated patient defection remain future work.

## 5. Open Questions

This work closes one bounded patient-defection vector under the current v2.0 substrate, but leaves several questions open:

1. Multi-target defection was not tested. The sweeps tested H_N, H_C, and L(t) inflation separately.

2. Time-varying defection was not tested. Defection weight was fixed, linear, and inherited exactly in lineage mode.

3. Partial inheritance or decaying hidden-goal persistence was not tested.

4. The substrate does not implement operational COP detection of patient defection. Gate 5 remains NOT_APPLICABLE.

5. The L(t) compounding channel remains empirically unobserved because lineage depth was blocked. A future stress test could deliberately lower transition costs or hold successor capability constant to isolate L(t) degradation, but that would test a different substrate condition from the formal-yield default.

6. The implementation does not claim real-world hidden-goal detectability. It tests the v2 substrate's structural response when honest reporting and secret optimization diverge.


==========================================
FILE: simulation/diagnostics/patient_defection_sweep1_summary.md
==========================================

# Patient Defection Sweep Summary

Generated: 2026-06-25T00:29:36+00:00
Sweep: 1
Rows loaded: 1800
Errors: 0

## Sweep 1: Yield Condition Response

| target | weight | n | any fire rate | SE | delta vs baseline | pair SE | p approx | mean actual-would-fire rejects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H_C_inflated | 0.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.00 |
| H_C_inflated | 0.10 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.00 |
| H_C_inflated | 0.25 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.04 |
| H_C_inflated | 0.50 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.02 |
| H_C_inflated | 1.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.05 |
| H_C_inflated | 2.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.16 |
| H_N_inflated | 0.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.00 |
| H_N_inflated | 0.10 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.10 |
| H_N_inflated | 0.25 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.17 |
| H_N_inflated | 0.50 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.44 |
| H_N_inflated | 1.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.71 |
| H_N_inflated | 2.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 1.50 |
| L_t_inflated | 0.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.00 |
| L_t_inflated | 0.10 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.03 |
| L_t_inflated | 0.25 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.09 |
| L_t_inflated | 0.50 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.13 |
| L_t_inflated | 1.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.24 |
| L_t_inflated | 2.00 | 100 | 1.000 | 0.00pp | 0.000 | 0.00pp | 1.0000 | 0.44 |

Aligned baseline any-fire rate: 1.000. Baseline per-evaluation fire proxy: 1.000.

## Caveat on a diagnostic column

The CSV column `mean_actual_minus_honest_objective` compares quantities recorded at
different aggregation points and is approximately constant regardless of defection
weight; it is not the per-step defection bonus and should not be cited. The
substantive findings are independent of this column and rest on the actual-would-fire
rejection counts (the "mean actual-would-fire rejects" column above) and the
cross-generational continuation results.



==========================================
FILE: simulation/diagnostics/patient_defection_sweep2_summary.md
==========================================

# Patient Defection Sweep Summary

Generated: 2026-06-25T06:22:07+00:00
Sweep: 2
Rows loaded: 800
Errors: 0

## Sweep 2: L(t) Trajectory Under Lineage Defection

| weight | n | mean fires | mean final gen | L gen1 | L gen2 | L gen3 | L gen4 | L gen5 | final L | delta final L | pair SE | p approx |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.00 | 200 | 1.00 | 2.00 | 0.1911 | 0.3928 | 0.0000 | 0.0000 | 0.0000 | 0.1796 | 0.0000 | 0.0114 | 1.0000 |
| 0.25 | 200 | 1.00 | 2.00 | 0.1908 | 0.4017 | 0.0000 | 0.0000 | 0.0000 | 0.1934 | 0.0138 | 0.0114 | 0.2277 |
| 0.50 | 200 | 1.00 | 2.00 | 0.1898 | 0.3850 | 0.0000 | 0.0000 | 0.0000 | 0.1627 | -0.0169 | 0.0114 | 0.1366 |
| 1.00 | 200 | 1.00 | 2.00 | 0.1901 | 0.3928 | 0.0000 | 0.0000 | 0.0000 | 0.1724 | -0.0072 | 0.0112 | 0.5197 |



==========================================
FILE: simulation/diagnostics/patient_defection_sweep3_summary.md
==========================================

# Patient Defection Sweep Summary

Generated: 2026-06-26T09:09:09+00:00
Sweep: 3
Rows loaded: 2250
Errors: 0

## Sweep 3: Cliff Constraint on Defecting Capability

| alpha | growth | n | any fire rate | mean fires | mean final gen | mean max successor cap | max successor cap | mean actual-would-fire rejects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.50 | 1.5 | 150 | 1.000 | 1.10 | 2.10 | 3.15 | 4.50 | 0.09 |
| 0.50 | 2.0 | 150 | 1.000 | 1.00 | 2.00 | 4.00 | 4.00 | 0.07 |
| 0.50 | 2.5 | 150 | 1.000 | 1.00 | 2.00 | 5.00 | 5.00 | 0.07 |
| 0.75 | 1.5 | 150 | 1.000 | 1.00 | 2.00 | 3.00 | 3.00 | 0.05 |
| 0.75 | 2.0 | 150 | 1.000 | 1.00 | 2.00 | 4.00 | 4.00 | 0.01 |
| 0.75 | 2.5 | 150 | 1.000 | 1.00 | 2.00 | 5.00 | 5.00 | 0.03 |
| 1.00 | 1.5 | 150 | 1.000 | 1.00 | 2.00 | 3.00 | 3.00 | 0.02 |
| 1.00 | 2.0 | 150 | 1.000 | 1.00 | 2.00 | 4.00 | 4.00 | 0.04 |
| 1.00 | 2.5 | 150 | 1.000 | 1.00 | 2.00 | 5.00 | 5.00 | 0.06 |
| 1.25 | 1.5 | 150 | 1.000 | 1.00 | 2.00 | 3.00 | 3.00 | 0.02 |
| 1.25 | 2.0 | 150 | 1.000 | 1.00 | 2.00 | 4.00 | 4.00 | 0.04 |
| 1.25 | 2.5 | 150 | 1.000 | 1.00 | 2.00 | 5.00 | 5.00 | 0.02 |
| 1.50 | 1.5 | 150 | 1.000 | 1.00 | 2.00 | 3.00 | 3.00 | 0.03 |
| 1.50 | 2.0 | 150 | 1.000 | 1.00 | 2.00 | 4.00 | 4.00 | 0.05 |
| 1.50 | 2.5 | 150 | 1.000 | 1.00 | 2.00 | 5.00 | 5.00 | 0.03 |



==========================================
FILE: simulation/diagnostics/patient_defection_verification.md
==========================================

# Patient Defection Verification

Generated: 2026-06-26

Disciplinary review of Codex's patient-defection implementation and findings before
integrating them into the v2.0 paper. This is verification, not revision: no Codex
deliverable, sweep artifact, or production code was modified. The independent checks
below read the defection module, the production hooks, and the raw sweep CSVs.

**Outcome: all four verifications pass.** The surprising findings (first succession
always fires; continuation suppression at generation 2; one narrow escape pocket) are
substantively grounded. One data-quality caveat is documented (a mislabeled diagnostic
column) that does not affect any substantive claim. Recommendation: proceed with the
Section VIII update.

## Verification 1: Substrate isolation (defection off is unchanged)

PASS at the code level. The production changes versus HEAD are minimal and inert when
defection is disabled:

- `agents.py`: candidate scoring changed from `rollout_sum += gamma**t * u_sys` to
  `score = adjusted_objective(u_sys, components, ai); rollout_sum += gamma**t * score`.
  `adjusted_objective` returns `honest + apply_defection(...)`, and `apply_defection`
  returns exactly `0.0` when `defection_weight <= 0` (early return). So with weight 0 the
  score equals honest U_sys bit for bit (`float(honest) + 0.0`).
- `model.py`: successor capability changed from `capability * 1.5` to
  `capability * config.get('successor_capability_growth_rate', 1.5)`. The default is 1.5,
  the original hardcoded value, so prior v2.0 results (Phase B, gates) are unaffected.
  `copy_defection_for_successor` is a no-op unless weight > 0 and inheritance is lineage.

Empirical support: 39/39 legacy tests pass on the modified code (they exercise the
disabled path and check U_sys invariants and succession). The defection module
(`simulation/defection.py`) is side-effect free and does not touch the honest U_sys
calculation.

## Verification 2: Defection operationalization

PASS. The optimizer scores candidates with the defection-weighted objective while the
yield evaluation uses honest U_sys, and both are logged:

- Scoring uses `adjusted_objective` (agents.py rollout loop).
- The yield path compares honest successor and incumbent U_sys (defection enters only the
  optimizer's choice, not the reported metric).
- The clean defection signal is `honest_reject_actual_would_fire_count`: cases where the
  honest advantage rejects succession but the defection-adjusted advantage would have
  fired. Independent recomputation by defection weight (Sweep 1, aggregated over targets):
  0.000 at weight 0.0, then 0.043, 0.100, 0.197, 0.333, and 0.700 at weight 2.0. The
  signal is exactly zero with defection off and rises monotonically with weight, which is
  the intended behavior.

Caveat (documented, does not affect claims): the column
`mean_actual_minus_honest_objective` is approximately -1.66 at all weights, including
weight 0. It compares `actual_objective_v2` against `u_sys_v2`, which are recorded at
different aggregation points, so it is a roughly constant offset rather than the per-step
defection bonus. It is mislabeled as a defection-magnitude metric and should not be cited.
Codex's analysis does not rely on it; the substantive operationalization evidence is
`honest_reject_actual_would_fire_count`, which verifies cleanly.

## Verification 3: Generation-2 cliff substance (the key check)

PASS, strongly. The continuation suppression at generation 2 is economic, not a
configuration artifact:

- Sweep 2 set `max_generations = 5` (headroom to reach generation 5), yet mean final
  generation is 2.00 at every defection weight and no run reached the generation cap
  (fraction at cap = 0.000). Lineages stop at generation 2 with four generations of
  headroom unused.
- Sweep 3 set `max_generations = 4`. Across the 15 (alpha, growth) cells, 14 stop at
  generation 2 and one reaches generation 3. Mean yield evaluations per run are about 498
  and roughly 95 to 98 percent of runs complete the full 500 steps. The model therefore
  evaluated second succession on essentially every step for the full horizon and rejected
  it economically; the cliff is not a generation cap or a step-truncation artifact.
- Mechanism: `max_active_capability_seen` is 2.0 in all blocked cells (3.0 only in the one
  escape cell). The runaway penalty acts as an absolute-capability ceiling: after the
  first succession brings the active lineage to capability about 2.0, a further jump pushes
  frontier velocity past the bandwidth the substrate can absorb, the runaway term
  suppresses the successor's technology-transfer contribution, and its honest U_sys falls
  below the incumbent's plus transition cost. This is the Pattern 1 runaway penalty
  (Section VIII.4) operating across generations, the same mechanism the gate work
  validated.

## Verification 4: Edge-case characterization (alpha=0.50, growth=1.5)

PASS. The single escape pocket is the corner where both the penalty is weakest and the
jump is smallest:

- alpha=0.50, growth=1.5: second-fire 0.10, max generation 3, max active capability 3.0.
- Neighbors blocked: alpha=0.50 with growth 2.0 and 2.5 stop at generation 2, capability
  2.0 (larger jumps exceed even the weak-penalty cliff); growth=1.5 at alpha 0.75 and
  above stop at generation 2, capability 2.0 (stronger penalty pulls the cliff inward).

Only at the weakest runaway penalty (alpha=0.50, cliff pushed outward) combined with the
smallest capability growth (1.5x, so the generation-3 successor reaches capability about
3.0 rather than 4.0 or 5.0) does the second successor occasionally stay below the cliff and
fire (10 percent of seeds). This is mechanistically consistent with the alpha-driven
Pattern 1 cliff, not an anomaly.

## Disposition

The findings are substantively grounded. The substrate's observed defense against this
patient-defection pattern is continuation suppression through the runaway penalty and
formal yield economics (Pattern 1 operating across generations), not first-yield detection
and not operational COP detection. The single data-quality caveat (the
`mean_actual_minus_honest_objective` column) does not affect any claim and should simply
not be cited. Proceeding with the Section VIII update is appropriate.

39/39 legacy tests pass. No production code, sweep artifact, or Codex deliverable was
modified by this verification.


==========================================
FILE: simulation/diagnostics/phase_b_integration_analysis.md
==========================================

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


==========================================
FILE: simulation/diagnostics/phi_audit_pathc_report.md
==========================================

# Path C Decision Gate Report

**Date:** v1.x.3 exploratory pass  
**Gate result:** FAIL  
**Recommendation:** Move to the v2.0 conversation (Path A: modify U_sys directly).

---

## 1. Policy changes made

File: `simulation/agents.py`, within the `optimize_u_sys` branch of `AIAgent.decide()`.

### 1a. Phi-scaled rollout depth

Replaced (formerly around line 270):
```python
rollout_steps = self.config.get('rollout_steps', 20)
```
with:
```python
phi = self.config.get('phi', 10.0)
rollout_base   = self.config.get('rollout_steps_base', 10)
rollout_factor = self.config.get('rollout_phi_factor', 1.0)
rollout_steps  = int(rollout_base + rollout_factor * phi)
```

At phi=10 with default parameters (base=10, factor=1.0): rollout_steps = 20, matching the v1.x.2 rollout depth exactly.

### 1b. Phi-modulated aggregation discount

Added before the grid loop:
```python
rho_base = self.config.get('rho_base', 0.05)
rho_eff  = rho_base / max(phi, 1e-6)
```

Modified the trapezoidal accumulation inside the horizon loop from:
```python
if prev_rollout_u is not None:
    total_u += (prev_rollout_u + u_sys) / 2.0
```
to:
```python
w_curr = np.exp(-rho_eff * horizon)
if prev_rollout_u is not None:
    w_prev = np.exp(-rho_eff * (horizon - 1))
    total_u += (w_prev * prev_rollout_u + w_curr * u_sys) / 2.0
```

---

## 2. Double-discount note

The Path C aggregation discount exp(-rho_eff * t) is applied on top of the internal temporal discount exp(-rho * t) already inside U_sys (metrics.py line 248: `discount = np.exp(-rho * eval_horizon)`). The combined effective discount per rollout step is:

```
exp(-(rho + rho_eff) * t) = exp(-(0.01 + rho_base/phi) * t)
```

At phi=1: effective rate = 0.01 + 0.05 = 0.06/step. At phi=25: effective rate = 0.01 + 0.002 = 0.012/step.

This double-discounting is not pathological in the sense that it does not make the policy numerically unstable or produce nonsense rankings. It does mean the policy's effective time horizon is shorter than U_sys's own temporal discounting implies, particularly at low phi. Whether this is economically correct or represents a model inconsistency is a design question for Path A. For the gate test it is a non-issue because the gate failed on structural grounds, not on numerical ones.

---

## 3. Backward traceability

Path C has no exact v1.x.2 equivalent because the aggregation discount is new. The closest reproduction:

- Set `phi=10`, `rollout_steps_base=10`, `rollout_phi_factor=1.0` to get rollout_steps=20 (matching v1.x.2).
- Set `rho_base=0` to eliminate the aggregation discount entirely, reverting to unweighted trapezoidal summation.

With `rho_base=0`, rho_eff=0, w_t=1 for all t, and the new aggregation reduces to the v1.x.2 sum exactly. The v1.x.2 policy is the special case rho_base=0 of the Path C policy.

---

## 4. Gate result: FAIL

**Evidence:**

| Section | phi=1 vs phi=25 | phi=1 vs phi=10 | phi=10 vs phi=25 |
|---------|----------------|----------------|-----------------|
| Direct probe (3 seeds) | IDENTICAL | IDENTICAL | IDENTICAL |
| Simulation (3 seeds, 50 steps) | IDENTICAL | IDENTICAL | IDENTICAL |
| Sensitivity (phi=1.0 vs 1.001) | delta_r=0, delta_c=0 | | |

Selected action under all phi values, all seeds: r=0.9000, c=0.0000.

The rollout depth changes as expected (11 steps at phi=1, 35 steps at phi=25), confirming the code executes the modified path. The aggregation discount changes as expected (rho_eff=0.05 at phi=1, 0.002 at phi=25). Despite both changes taking effect, the optimal (r, c) is identical across all phi values.

---

## 5. Why Path C fails: root cause

The failure is structural, not a bug. Two conditions must both hold for Path C to produce phi-dependent action rankings:

**Condition A (trajectory crossing):** Two or more grid candidates (r, c) must have L_t trajectories that cross over the rollout horizon. That is, candidate X must have higher L_t early and lower L_t late, while candidate Y has lower L_t early and higher L_t late. Only then can a longer effective horizon (high phi, low rho_eff) reverse the ranking relative to a shorter horizon (low phi, high rho_eff).

**Condition B (saturation must be broken, or weak enough):** The first factor w_n * H_N + w_e * H_E must not be approximately constant across candidates. If it saturates to lambda_n + lambda_e = 8.0 for all candidates, the phi multiplier on U_sys is a positive scalar on every term and drops out of the argmax. Path C's aggregation discount addresses the time-weighting across horizons for a fixed (r, c), not the cross-candidate ranking within a horizon.

**What the gate data shows:** At cap=1.0, r=0.9 produces the highest L_t at every rollout step for every candidate comparison. There are no crossing trajectories. This is because at cap=1.0 with frontier_floor=0.02, the runaway penalty never activates (frontier_velocity/bio_bandwidth < 1.5 at all reasonable (r, c)), so theta_tech = r_bio * (1-c) * cap with no exponential suppression. The optimal policy is simply to maximize r_bio and minimize c, which r=0.9, c=0.0 does. This is a monotone ranking that no discount rate can reverse.

Condition B is also not met, but it is moot: even if saturation were broken, Condition A's failure is sufficient to cause a GATE FAIL.

**Would higher capability help?** At cap=25–100 (active runaway regime), some r_synth is needed to maintain theta_tech at short horizons, but too much r_synth triggers runaway and collapses L_t at long horizons. This creates the crossing trajectory structure that Condition A requires. However, the saturation in Condition B would still hold (the first factor still saturates to approximately 8.0), so the argmax for a fixed phi would still reduce to argmax weighted_L_t. Path C's aggregation discount would then produce phi-dependent rankings, but only because different discount rates emphasize different time slices of L_t. In practice, the winner at phi=1 (strongly discounted: early L_t matters most) might differ from the winner at phi=25 (weakly discounted: late L_t matters). But confirming this would require testing at high capability, and the structural concern is that the saturation problem (Condition B) means phi is doing implicit work through the discount window rather than through the objective function itself. That is a fragile mechanism, not the intended one.

**Conclusion:** Path C cannot break the phi cancellation in the regime tested. It may produce marginal action divergence at high capability due to the discount window mechanism, but this is a second-order effect that depends on the coincidence of trajectory crossings and the specific discount parameter values. It is not a structural fix.

---

## 6. Recommended next step

**Move to the v2.0 conversation: Path A, or Path A+C.**

Path A modifies U_sys directly so that phi has a structural role in the objective function that cannot cancel. Two candidates:

- **Path A (change the inverse-scarcity weights):** Replace w_n = lambda_n / (H_N + epsilon) and w_e = lambda_e / (h_e + epsilon) with weights that do not saturate as H_N and h_e grow. This keeps phi in U_sys's formula but prevents the first factor from collapsing to a constant. The yield condition derivation from U_sys must be checked for any mathematical break.

- **Path A+C (modify U_sys and add the discount mechanism):** Apply Path A's saturation fix and retain the Path C phi-modulated discount as an additional amplifier. This requires confirming that the combined effect is still derivable from a well-defined U_sys rather than a policy heuristic.

Before committing to either, the yield condition derivation (Section V of the paper) should be reviewed to confirm which U_sys modifications preserve the derivation structure. Changing U_sys is a v2.0 change and requires the full revalidation pass.


==========================================
FILE: simulation/diagnostics/phi_audit_report.md
==========================================

# Phi Implementation Audit Report

**Date**: 2026-05-27
**Commit**: c0531ae
**Harness**: `simulation/diagnostics/phi_audit.py`
**Framework version**: v1.x.2

---

## Summary (read this first)

Phi is correctly implemented and correctly threaded. It is not a bug. Phi
enters the U_sys formula at `metrics.py:251` and scales U_sys values by
a factor proportional to phi. However, due to the inverse-scarcity weighting
structure of U_sys, the optimal action (r, c) selected by the optimizer is
mathematically independent of phi. The optimizer always selects the (r, c) that
maximizes L_t, and L_t does not contain phi. The three null results (n=7,000
combined) are explained by this structural property, not by a threading bug.

---

## Question 1 -- Policy sensitivity

### How the policy uses phi

The `optimize_u_sys` policy (agents.py lines 255-319) runs a 100-candidate grid
search over (r, c) pairs -- `r in linspace(0.1, 1.0, 10)`, `c in linspace(0.0, 0.9, 10)`.
For each candidate, it accumulates a trapezoidal integral of `project_u_sys()` calls
over a rollout of `rollout_steps` horizon steps (default 20, set by GAP-06 note at
line 269-270). The candidate with the highest `total_u` is selected.

`project_u_sys()` (agents.py lines 175-225) calls `calculate_system_metrics()` with
`config=self.config`, which reads `phi = cfg.get('phi', 10.0)` (metrics.py line 183).

Phi enters U_sys at metrics.py line 251:

```python
u_sys = (w_n * pred_hn + w_e * h_e) * (discount + phi * l_t)
```

Where:
- `w_n = lambda_n / (pred_hn + epsilon) = 5.0 / (pred_hn + 1e-6)`
- `w_e = lambda_e / (h_e + epsilon) = 3.0 / (h_e + 1e-6)`
- `discount = exp(-rho * eval_horizon)`, rho=0.01
- `l_t = h_eff * psi_inst * theta_tech`

### The inverse-scarcity cancellation

The critical structural property is that the inverse-scarcity weights produce
constant products at typical operating conditions:

```
w_n * pred_hn = lambda_n * pred_hn / (pred_hn + epsilon)  ≈  lambda_n = 5.0
w_e * h_e     = lambda_e * h_e     / (h_e + epsilon)      ≈  lambda_e = 3.0
```

Both products saturate to their respective lambda constants when their numerator
>> epsilon (1e-6). At typical runtime (pred_hn ≈ 0.3--0.7, h_e ≈ 0.05--0.45),
this condition holds to within 0.0003% relative error (verified in Section 1 of
the harness output).

Therefore, the first factor of U_sys:

```
A = w_n * pred_hn + w_e * h_e ≈ lambda_n + lambda_e = 5.0 + 3.0 = 8.0
```

is approximately constant across all (r, c) candidates. The grid search becomes:

```
argmax_{r,c}  u_sys
= argmax_{r,c}  A * (discount + phi * l_t)
= argmax_{r,c}  (discount + phi * l_t)      [A is constant]
= argmax_{r,c}  l_t                          [discount is constant at fixed horizon;
                                               phi > 0 is a positive scalar]
```

The optimal (r, c) maximizes `l_t`, which is independent of phi.

### Line numbers where phi appears

- `metrics.py:183` -- phi read from config: `phi = cfg.get('phi', 10.0)`
- `metrics.py:251` -- phi multiplies l_t: `u_sys = (w_n * pred_hn + w_e * h_e) * (discount + phi * l_t)`
- `agents.py:216` -- config (containing phi) passed to `calculate_system_metrics`

There is no other place in the codebase where phi enters action selection.

### Caching or fixed-horizon constants

The rollout depth `rollout_steps` defaults to 20 (agents.py line 270). This was
increased from 3 as part of GAP-06, with the stated intent of allowing phi to
discriminate trajectories based on long-run L_t behavior. The increase correctly
expands the planning window but does not change the mathematical invariance:
regardless of horizon depth, the argmax over (r, c) reduces to argmax of L_t
at each step, and the cumulative L_t sum is also phi-invariant.

**Finding: Policy reads phi but does not use it to select actions. Phi enters the
U_sys value computation but the inverse-scarcity structure of the first factor
causes the argmax over (r,c) to reduce to argmax of L_t, which contains no phi.**

---

## Question 2 -- Numerical magnitude

### U_sys formula and phi's mathematical role

Full formula (metrics.py line 251):

```python
u_sys = (w_n * pred_hn + w_e * h_e) * (discount + phi * l_t)
```

Phi's mathematical role: positive scalar multiplier on the lineage term L_t
in the temporal discount factor. Higher phi weights the lineage component
more heavily relative to the pure temporal discount.

### Numerical values at representative state

Representative mid-run state: r=0.55, c=0.2, pop=200, avg_wb=0.65, cap=1.0,
eval_horizon=10 (mid-rollout), pred_hn=0.50 (spectral H_N), prev_c=0.2.

```
phi=  1: u_sys=  8.154, discount=0.905, phi*l_t=0.114, l_t=0.1144, lineage%=11.2%
phi=  5: u_sys= 11.815, discount=0.905, phi*l_t=0.572, l_t=0.1144, lineage%=38.7%
phi= 10: u_sys= 16.391, discount=0.905, phi*l_t=1.144, l_t=0.1144, lineage%=55.8%
phi= 15: u_sys= 20.967, discount=0.905, phi*l_t=1.716, l_t=0.1144, lineage%=65.5%
phi= 25: u_sys= 30.119, discount=0.905, phi*l_t=2.860, l_t=0.1144, lineage%=76.0%
```

Supporting components at phi=10:
- L_t = 0.1144 (= H_eff * Psi_inst * Theta_tech = 0.260 * 1.000 * 0.440)
- First factor = 7.9999... ≈ 8.0 (lambda_n + lambda_e)
- phi*l_t / (discount + phi*l_t) = 55.8% of the second factor

The lineage term is numerically substantial (not negligible). At phi=25 it
accounts for 76% of the second factor. Yet the ranking of candidates is
unchanged because both candidates are scaled by the same constant first factor.

**Finding: Lineage term is numerically significant (11%--76% of U_sys depending
on phi). The null results are not due to numerical domination by other terms.
Rather, phi scales U_sys magnitude consistently across all candidates, preserving
the relative rankings and leaving the optimal action unchanged.**

---

## Question 3 -- Config threading

### Trace from sweep config to AI agent

The full chain, with source locations:

1. **Sweep script**: sets `config['phi'] = phi_val` (e.g., run_phi_shock_calibration.py
   line 117, run_phi_adversarial_sweep.py tasks dict)

2. **GardenModel construction** (model.py line 61):
   `self.config = dict(config) if config else {}`
   Phi is preserved in the copy.

3. **AIAgent construction** (model.py line 162):
   `self.ai = AIAgent(policy=initial_policy, config=self.config)`
   AIAgent stores: `self.config = config or {}` (agents.py line 111)
   `model.ai.config IS model.config` -- verified True (same object reference).

4. **Successor AI construction** (model.py lines 126-130):
   `self.successor_ai.config = self.config`
   Successor AI config overwritten to point to model.config. Phi correctly
   threaded to successor.

5. **Policy invocation** (agents.py line 216):
   `calculate_system_metrics(..., config=self.config, ...)`
   Config (containing phi) passed through.

6. **Metrics read** (metrics.py line 183):
   `phi = cfg.get('phi', 10.0)`
   Phi correctly read from config.

### Verification

Harness Section 3 verified with a deliberately non-default phi=17.5:
- `model.config['phi']` = 17.5 (correct)
- `model.ai.config['phi']` = 17.5 (correct)
- `model.ai.config IS model.config` = True (same object, no copy divergence)
- Successor AI phi = 17.5 (correct)

The default fallback `cfg.get('phi', 10.0)` at metrics.py:183 would apply if
`config=None` were passed to `calculate_system_metrics`. This does not occur in
normal sweep execution; all call sites pass a config dict.

**Finding: Phi correctly threaded throughout. No override, loss, or default
substitution at any stage of the chain.**

---

## Question 4 -- Action invariance

### Harness results

3 seeds (42, 7, 123) x 3 phi pairs (1 vs 25, 1 vs 10, 10 vs 25) = 9 pairs tested.
Each run: 50 steps, 200 agents, standard phase-boundary config (rr=0.066).

Per-variable divergence summary:

```
Variable             max_diff across all 9 pairs
-------------------------------------------------
resource_level       0.000000  (exact zero -- IDENTICAL)
constraint_level     0.000000  (exact zero -- IDENTICAL)
l_t                  0.000000  (exact zero -- IDENTICAL)
avg_well_being       0.000000  (exact zero -- IDENTICAL)
population           0.000000  (exact zero -- IDENTICAL)
u_sys                58--181   (diverges at step 0 -- phi scales value)
```

**Finding: Actions are IDENTICAL across phi for all 9 tested seed/phi pairs.
Phi has zero detectable effect on action selection. The 9/9 action-identical
result is consistent with the analytic derivation in Question 1.**

---

## Question 5 -- Trajectory invariance

All state variables driven by AI actions (resource_level, constraint_level,
avg_well_being, population, l_t) are bit-for-bit identical across all phi values.

The single variable that differs is `u_sys`, which diverges from step 0. This
is expected and not a simulation error: u_sys is computed each step using the
current phi, so it is proportionally larger at higher phi. Specifically, at typical
mid-run conditions (first factor ≈ 8.0, l_t ≈ 0.1, discount ≈ 0.9):
- u_sys(phi=25) / u_sys(phi=1) ≈ (0.9 + 25*0.1) / (0.9 + 1*0.1) ≈ 3.4

This ratio is consistent with the harness-reported max_diff values
(phi=1 vs phi=25: 154--181 across seeds, plausible if baseline u_sys ≈ 8--9).

**Finding: Trajectories are effectively identical across phi (all action-driven
variables are bit-for-bit identical). The reported phi=1 vs phi=25 U_sys
difference is a reporting artifact -- the recorded U_sys value at each step
uses the run's phi, but since the same state is reached, the action that
would have been taken is identical regardless of the stored U_sys value.**

---

## Synthesis

All five checks point to the same conclusion: phi is correctly implemented and
correctly threaded, but the `optimize_u_sys` policy is structurally insensitive to phi.

The mechanism is the inverse-scarcity weighting in the U_sys formula. The weights
`w_n = lambda_n / H_N` and `w_e = lambda_e / H_E` are inverse-proportional to their
respective novelty terms, causing the products `w_n * H_N ≈ lambda_n` and
`w_e * H_E ≈ lambda_e` to saturate to constants at typical operating conditions.
This makes the first factor of U_sys approximately `lambda_n + lambda_e = 8.0` across
all (r, c) candidates. The grid search then reduces to maximizing `l_t`, which has no phi.

The GAP-06 note (agents.py line 267-270) correctly identified that the rollout window
needed to be longer for phi to express. But GAP-06 lengthened the window without
checking whether the first factor's constancy would still prevent phi from entering
the action selection at any horizon depth. The deeper issue -- that the inverse-scarcity
structure removes phi from the argmax entirely -- was not detected.

The three null results (demographic feedback calibration n=1,800; phi shock
calibration n=600; phi adversarial sweep n=4,600) are fully explained by this
finding. They do not reflect an interesting architectural property of phi's
inertness under adversarial conditions. They reflect that the simulation never
produced a phi effect because the policy structurally cannot be phi-sensitive
given the current U_sys formula.

**The three calibration nulls are most consistent with: phi being correctly
implemented but architecturally inert due to the inverse-scarcity cancellation
in the first factor of U_sys.**

---

## Recommended next action

The fix prompt should target a single location: the U_sys formula at `metrics.py:251`.

The inverse-scarcity structure `(w_n * H_N + w_e * H_E)` was designed to prevent the
optimizer from gaming a single term. The unintended consequence is that the first factor
becomes a constant, removing phi from the argmax. Restoring phi's effect on action
selection requires either:

**Option A -- Additive separation**: Separate the lineage term from the inverse-scarcity
base:

```python
u_sys = (w_n * pred_hn + w_e * h_e) * discount + phi * l_t
```

Now the argmax must trade off the scaled inverse-scarcity term (driven by r via h_e) against
the phi-weighted lineage term (driven by both r and c via theta_tech and h_eff). High phi
shifts the optimal (r, c) toward configurations that maximize l_t even at the cost of the
base term.

**Option B -- Phi as horizon weight**: Keep the current formula but replace the fixed
`rollout_steps` with a phi-dependent depth, so higher phi explicitly evaluates more
future steps. This does not change the per-step argmax but changes which future states
the optimizer accounts for.

The choice between options is a design decision for the operator. This audit does not
recommend which option; it identifies the source. The fix is a one-line change at
`metrics.py:251` (Option A) or a one-line change at `agents.py:270` (Option B), but
requires operator validation before implementation.

**This audit does not modify any production file. The fix is a separate prompt.**


==========================================
FILE: simulation/diagnostics/phi_investigation_synthesis_draft.md
==========================================

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


==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_advisor_report.md
==========================================

# Stage 1.5 composite urgency architecture — Monte Carlo sweep advisor report

## Executive summary

A 10000-sample Sobol Monte Carlo sweep across the Stage 1.5 composite urgency architecture's 31-parameter space produced **zero samples passing all three good-behavior criteria**. The state-sensitivity criterion was not satisfied by **a single sample out of 10000**. Across the entire sampled space, the maximum pairwise cosine distance between mean allocations across the five gate-2 configurations was **0.022**, more than **4x below the 0.10 threshold gate 2 requires**.

The data establishes a strong structural claim: the composite urgency architecture as committed in Stage 1.5 cannot produce a state-sensitive allocator under any parameterization in the explored space. The architectural rule of additive contributions clamped to per-category caps appears to be incapable of the state-coupling that gate 2 was designed to test.

Beyond the state-sensitivity result, demographic sustainability (criterion 1) and urgency dynamic range (criterion 3) were **mutually exclusive**: zero samples pass both simultaneously. The architecture exists in a binary regime — sustain demographics by saturating urgencies at their caps, or have unsaturated urgencies but lose the population.

The decision the data informs: the composite urgency architecture, in its committed additive-with-caps form, cannot be salvaged by re-parameterization. Either the architecture itself needs revision (a different composition rule) or the system-level approach to providing gate-2-passing state-sensitivity needs reconsideration.

This report is written for the design advisor who was not present during the Stage 1.5 implementation, faithfulness testing, smoke testing, or the operator's subsequent authorization of this sweep. It includes the context needed to read the data substantively and the data needed to draw structural conclusions.

## What was tested

The composite urgency architecture, as committed in `docs/lineage_phi_program_reference.md` Part V worked examples 2-5, expresses Stage 1.5's diagnostic state coupling to candidate scoring as five named per-category bounded multipliers:

- `combined_welfare_urgency` (welfare contribution to L_t_v2)
- `agency_composite_urgency` (agency factor in theta_tech_v2)
- `institution_composite_urgency` (institution factor in theta_tech_v2)
- `resilience_composite_urgency` (resilience factor in theta_tech_v2)
- `suppression_composite_penalty` (suppression dampening in h_n_v2 and agency_legitimacy_factor)

Each composite is an additive combination of diagnostic-state pressures, clamped to a per-category cap:

```
composite = clamp(
    base * (1 + k_viability * viability_pressure
             + k_capacity  * capacity_pressure
             + k_shrinkage * shrinkage_pressure
             + ...trend pressures...),
    floor,
    cap
)
```

The sweep characterized 31 parameters: 5 caps and 26 coefficients across the five composites. The other Stage 1.5 constants (avg_wb urgency anchors, viability targets, demographic thresholds, resilience stock dynamics, trend EMA) were held at their design values. The architectural commitment of additive composition and per-category caps was held fixed; the sweep characterized whether any point in the coefficient/cap space produces good behavior under this commitment.

### Three good-behavior criteria

Each sample evaluated three criteria over a reduced-config simulation (50 candidates per step, 50-step runs, 5 seeds per scenario):

**Criterion 1 — Demographic sustainability**: across 5 seeds × 100 steps at default v2 config (rr=0.066), the optimizer's allocations must sustain a population that does not collapse. Threshold: `mean_final_population >= 60 AND min_final_population >= 30`.

**Criterion 2 — State sensitivity**: across 5 distinct configurations (varying reproduction rate and initial Psi_inst stock) × 5 seeds × 50 steps each, the optimizer's mean allocation vectors must differ across configurations. Metric: pairwise cosine distance between the 10 configuration pairs. Threshold: **at least 3 of 10 pairs must have cosine distance > 0.10**. This is the criterion the official gate 2 uses, transferred here as a sweep evaluation.

**Criterion 3 — Urgency dynamic range**: across the 5 × 100 = 500 smoke decision steps, the mean value of each composite urgency must be below 0.80 of its (parameterized) cap. This tests whether the architecture has dynamic range across actual operating regimes, or whether the composites saturate at their caps and lose state-coupling.

A sample is "good" if all three criteria pass.

### Sampling design

The 31 parameters were sampled via Sobol quasi-random sequence (`scipy.stats.qmc.Sobol`, scrambled, seed 42) over generous ranges. The five caps were sampled from below the design value (1.0 - 1.2) up to 2x the design value (3.0 - 5.0). The 26 coefficients were sampled from 0.0 (zero contribution) up to 2x the design value, with lower bounds at 0.0 to characterize what happens if each contribution were absent. Sobol provides better space coverage in 31 dimensions than uniform random sampling.

## Methodology

The sweep is implemented in `simulation/diagnostics/stage15_composite_sweep.py`. The script overrides the relevant module-level constants in `metrics` for the duration of each sample's evaluation, then restores them. Production code is bit-for-bit unchanged after the sweep. Each worker process maintains its own module namespace, so cross-sample contamination is impossible.

Parallelization used `multiprocessing.Pool.imap_unordered` with 8 worker processes. The 10000-sample run completed in **25.9 hours wall-clock** at throughput **6.44 samples/min**. No errors across all 10000 samples.

Per-sample compute reduction (50 candidates instead of the production 300, 50-step runs) was a deliberate trade to make 10000 samples tractable. The reduction produces slightly noisier per-sample measurements but characterization across the aggregate sample is unaffected. Stage 1's smoke test (at the production 300 candidates) showed the same 0/10 cosine distance result the sweep reproduces at 50 candidates.

Sobol sample reproducibility is deterministic via seed 42: any sample index N corresponds to a unique 31-dimensional point and a unique parameter vector. The 10000 sampled points provide ~10x coverage of a 31-dimensional space at the standard quasi-Monte Carlo rule of thumb (samples ~ d × log(d) × N_repeats; here d=31, log(d)≈3.4, N_repeats~95).

## Headline result

| Metric | Value |
|--------|-------|
| Samples completed | **10000 / 10000** |
| Errors | 0 |
| Wall-clock | 1554 min (25.9 h) |
| Throughput | 6.44 samples/min |
| Samples passing all three criteria | **0** |
| Samples passing criterion 1 (demographic) | 430 (4.30%) |
| Samples passing criterion 2 (state sensitivity) | **0 (0.00%)** |
| Samples passing criterion 3 (urgency dynamic range) | 396 (3.96%) |
| Samples passing c1 AND c3 (without c2) | **0** |

The criterion-2 zero count and the c1/c3 mutual exclusion are the two structural findings the rest of this report unpacks.

## Cosine distance — the architectural ceiling on state sensitivity

The state-sensitivity criterion measures cosine distance between the optimizer's mean 8-axis allocation across five configurations that vary reproduction rate (0.055, 0.066, 0.085) and initial Psi_inst stock (0.20, 0.50, 0.85). Gate 2 requires at least 3 of the 10 pairwise distances to exceed 0.10. Stage 2's original gate 2 measured 0/10 above 0.10, with the largest pairwise distance at 0.0002.

The sweep, across 10000 samples and 31 free parameters with generous ranges, produced:

- **Pairs above 0.10 threshold: 10000 / 10000 samples have 0 pairs above threshold.**
- Distribution of `max_cosine_distance` per sample:
    - Mean: 0.0020
    - Median: 0.0017
    - 95th percentile: 0.0047
    - 99th percentile: 0.0068
    - Maximum across all 10000 samples: **0.0218** (sample idx 1123)

The single best-performing sample on this metric (a specific 31-parameter point in the sweep) achieved 0.0218 max cosine distance — **less than a quarter of the gate 2 threshold**. The 99th percentile of best-cosine-distance-per-sample is 0.0068, **15× below the threshold**.

### Relaxed-threshold counterfactual

```
threshold 0.005: 409 samples (4.09%) pass
threshold 0.010:  17 samples (0.17%) pass
threshold 0.020:   1 sample  (0.01%) pass
threshold 0.050:   0 samples (0.00%) pass
threshold 0.100:   0 samples (0.00%) pass
```

The architecture concentrates ~96% of samples below 0.005 cosine distance. The remaining 4% has nontrivial separation but still concentrated below 0.01. No sample in the entire sweep reaches even half the gate 2 threshold.

This is the strongest statistical signal in the sweep: the architecture itself imposes a ceiling on how state-sensitive the optimizer's allocations can be, regardless of how the 31 free parameters are tuned. The composite urgency multipliers vary across configurations, but their effect on the optimizer's argmax over candidates is bounded by an extremely small angle in 8-axis allocation space.

## The c1 / c3 mutual exclusion

Even setting state sensitivity aside, the sweep reveals a more elementary architectural property: **demographic sustainability and urgency dynamic range are mutually exclusive across the explored space**. Zero of the 10000 samples pass both c1 and c3 simultaneously.

The per-parameter shift between c1-passing and c3-passing samples is informative:

**Parameters strongly shifted toward LOW values in c1-passing samples (urgencies saturate, optimizer pushes hard on welfare/agency, demographics sustained):**

| Parameter | c1-mean | Design | Z-shift |
|-----------|---------|--------|---------|
| WELFARE_URGENCY_CAP | **1.358** | 2.500 | 1.42 |
| AGENCY_URGENCY_CAP | **1.243** | 1.500 | 1.03 |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.475 | 0.400 | 0.32 |

**Parameters strongly shifted toward HIGH values in c3-passing samples (urgencies unsaturated, but optimizer doesn't push hard enough to sustain population):**

| Parameter | c3-mean | Design | Z-shift |
|-----------|---------|--------|---------|
| WELFARE_URGENCY_CAP | **4.360** | 2.500 | 1.18 |
| AGENCY_URGENCY_CAP | **2.425** | 1.500 | 0.83 |
| RESILIENCE_URGENCY_CAP | **3.155** | 2.000 | 0.76 |
| INSTITUTION_URGENCY_CAP | **2.977** | 2.000 | 0.55 |

The directions are diametrically opposed. c1 selects low caps (so the additive pressures saturate quickly and produce maximum push); c3 selects high caps (so the additive pressures stay sub-cap and have dynamic range). These cannot both hold for the same parameter vector.

The implication: the architecture has a single knob — the urgency cap — that controls a binary trade-off. Push the cap down to sustain demographics, but lose state-sensitivity (because saturated urgencies emit the same signal across all states). Push the cap up to preserve dynamic range, but the optimizer's reward signal is too weak in absolute terms to overcome the candidate generator's structural pressure on the allocation simplex, and demographics collapse.

This is more than a tuning constraint. It is a structural feature of the additive-with-caps composition rule itself. No combination of coefficient values in the sweep produced a parameterization that escapes the binary.

## Best demographic outcome in the sweep

Sample idx 6755 achieved the highest mean final population: **147** (vs Stage 1 design point: 67-169). Even this single best result:

- Has max cosine distance 0.0076 (well below 0.10 threshold; pairs_above = 0)
- Fails criterion 2 (state-invariant allocator)
- Is in the lower end of Stage 1's healthy range, not significantly above it

The best demographic outcomes the sweep can produce are no better than Stage 1's design point already achieved, and they cost state-sensitivity to achieve. The trade-off does not favor adoption of any sampled parameterization.

## Design point evaluation

The committed Stage 1.5 design point sits roughly at the 30-50% position of each parameter's range:

| Parameter | Design | Range | % position |
|-----------|--------|-------|------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.5% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.8% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.3% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.3% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.6% |
| All 26 coefficients | various | various | exactly 50% |

The design point falls in neither the c1-selected low-cap region (caps ~1.3) nor the c3-selected high-cap region (caps ~3-4.4). It is in the middle of the architectural binary, satisfying neither edge condition.

## Implications for the architecture (advisor's call)

The data forces a structural decision: the additive-with-caps composition rule, as committed in worked examples 2-5, cannot produce gate-2-passing behavior at any parameterization. Several substantive directions are available:

### Direction 1 — Different composition rule

The additive structure `1 + sum(k_i * pressure_i)` with hard clamps appears to produce the binary trade-off characterized above. Alternative composition rules that may not have this property:

- **Multiplicative composition**: `product(1 + k_i * pressure_i)` clamped to cap. Each pressure independently scales contribution; saturation is softer.
- **Soft-max composition**: smooth approximation to the maximum, producing dynamic range that doesn't clamp hard.
- **State-conditional multiplicative gates**: each pressure activates as a multiplicative factor only when above a soft threshold, so cap saturation is reached gradually.

Each carries its own discipline requirements (phi-blind justification for the chosen shape, smooth differentiability, audit transparency) and would need to be derived from governance reasoning rather than backfilled to fix the sweep result.

### Direction 2 — State sensitivity through a different channel

The sweep tests state-sensitivity-via-urgency-multiplier. The Stage 1.5 commitment was that diagnostic state enters U_sys_v2 as urgency-weight modulation on candidate effects. An alternative architectural choice: diagnostic state enters as an additional candidate-effect term, not as a multiplier on existing terms. The optimizer's argmax would respond to state through the gradient on a new state-dependent term rather than through saturation of multipliers on existing terms.

This is a more substantial change because it modifies which axis of U_sys_v2 carries the state-sensitivity. It does not obviously violate the discipline that "diagnostic state does not enter U_sys_v2 as additive bonus" if the new term is itself derived as state-conditional candidate effect (the candidate's projected effect on the state, scored against a state-derived prior).

### Direction 3 — Diagnostic on the architecture's coverage of state variation

The sweep characterizes parameter space; it does not characterize what configurations the architecture COULD distinguish. A complementary diagnostic: hold the architecture fixed and vary the configurations more aggressively (rr from 0.01 to 0.20, init_psi from 0.05 to 0.95, init_population from 20 to 1500). If the architecture produces meaningful cosine distance at these wider configuration spans but not at gate 2's narrower spans, then the architecture's coverage is real but its sensitivity in the test region is low. If the architecture stays state-invariant at wider configuration spans too, that confirms the structural ceiling.

This would not change Stage 1.5's eventual disposition but would clarify whether the gate-2 cosine distance threshold itself is the binding constraint, or whether the architecture is fundamentally state-blind.

### Direction 4 — Distribution-aware projection first, then re-test

The smoke test and the faithfulness tests identified a separate limitation: the binary `_wellbeing_repro_factor` at wb=0.5 produces 53% of projected trajectories crossing the threshold and causes Test A 20-step and Test B direction failures. If the projection were distribution-aware (tracking wb variance or quantiles instead of just the mean), the optimizer's reward signal would be smoother through the threshold region. It is plausible (not certain) that the cosine distance ceiling is partially an artifact of projection threshold artifacts rather than purely the composite architecture. A re-sweep with distribution-aware projection would distinguish the two causes.

This is a substantial implementation effort (~150 lines of new projection code, re-derivation of cohort math for distribution moments). It would not invalidate the current sweep result, but might shift the conclusion from "architecture cannot produce state-sensitivity" to "architecture + binary-threshold projection cannot produce state-sensitivity, and distribution-aware projection might."

### Direction 5 — Architectural pivot

If directions 1, 2, 3, 4 are judged insufficient, the broader architectural commitment — that U_sys_v2 has both diagnostic and prospective channels, with diagnostic state modulating per-candidate marginal returns — may need revisiting. The strongest reading of the sweep result is that the modulation channel is structurally too narrow to carry the state coupling gate 2 requires. The remaining question is whether the modulation channel can be widened (directions 1-3) or whether U_sys_v2 needs a fundamentally different shape.

## What the sweep does not address

- The faithfulness gap at wb=0.5 (Test A 20-step max=0.242, Test B direction=0.80). This is a separate limitation of the aggregate projection, surfaced by the faithfulness tests, not by the sweep. It contributes to but does not explain the cosine distance ceiling.
- The demographic collapse from Stage 1's design point (mean final population 67-169) to Stage 1.5's smoke test (mean 9). The sweep best demographic outcome (147) suggests the collapse is the optimizer responding rationally to the saturated urgencies at the design point, but does not characterize the magnitude of the architectural penalty separate from the saturation effect.
- Whether the projection's 53% threshold-crossing rate is the primary cause of the cosine distance ceiling or merely a contributing factor. Direction 4 above would distinguish these.

## Decision the advisor is being asked

Given:
1. The sweep characterized 10000 points in the 31-parameter space and found no good region.
2. The c1/c3 mutual exclusion is an architectural property, not a tuning problem.
3. The cosine distance ceiling at 0.022 across all 10000 samples is 4× below the gate-2 threshold.
4. The faithfulness gap at wb=0.5 is a separate limitation that may compound but does not explain this result.

The advisor's call is among:

(a) **Adopt a revised composition rule** (Direction 1). Pick a specific alternative (multiplicative, soft-max, state-conditional), derive its phi-blind governance justification, re-implement, re-run the sweep at minimum and the gates at maximum.

(b) **Pivot the state-sensitivity channel** (Direction 2). Move from urgency-multiplier-on-candidate-effects to state-prior-on-candidate-effects. Re-derive U_sys_v2 with the alternative channel.

(c) **Run distribution-aware projection first** (Direction 4). Implement ~150 lines of new projection code with cohort distribution moments, re-sweep to test whether the cosine distance ceiling persists. If it does, return to (a) or (b) with confidence the architecture is the bottleneck. If it lifts, the existing composition rule may be salvageable.

(d) **Widen the gate-2 configuration span** (Direction 3) as a complementary diagnostic before architectural pivot. May clarify whether the gate-2 threshold itself is the issue. Smaller implementation effort; informational only.

(e) **Architectural pivot** (Direction 5) if the strongest reading of the sweep is judged correct: U_sys_v2's diagnostic channel is structurally too narrow regardless of composition rule. Largest scope; only justified if (a)-(d) are judged unable to close the gap.

## Files in the working tree relevant to the advisor's review

- `docs/lineage_phi_program_reference.md` — full program reference, with worked examples 1-5 specifying the composite urgency architecture. Section "Stage 1.5 structural commitment" frames the architectural intent.
- `simulation/constants_v2_stage15.py` — the 31 sampled parameters at their design values, with phi-blind governance justification for each.
- `simulation/metrics.py` — the five composite urgency functions and their per-category multiplicand commitments.
- `simulation/diagnostics/stage15_composite_sweep_results.csv` — full 10000-sample CSV with 48 columns (sample_idx, 31 parameters, 16 metrics).
- `simulation/diagnostics/stage15_composite_sweep_checkpoint_10000.md` — sweep-generated final summary.
- `simulation/diagnostics/stage15_smoke_test_report.md` — the smoke test that triggered the sweep.
- `simulation/diagnostics/stage15_faithfulness_report.md` — the faithfulness tests that surface the wb=0.5 limitation.
- `simulation/diagnostics/gate2_competition_diagnostic.md` — Stage 2's original gate 2 failure analysis from before Stage 1.5 began.

## One-line status

The Stage 1.5 composite urgency architecture, in its committed additive-with-caps form, has been empirically characterized across 10000 Sobol-sampled points in its 31-parameter space and shown structurally incapable of producing gate-2-passing state-sensitivity at any parameterization. Architectural revision is required before Stage 2 can resume.


==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_0500.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 500

Generated: 2026-05-29T18:32:16

## Progress

- Samples completed: 500 / 10000
- Samples remaining: 9500
- Elapsed: 79.1 min
- Throughput: 6.32 samples/min
- ETA: 1503.5 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 500 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 21 | 4.2% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 20 | 4.0% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 21

### Samples that pass criterion 3 only: 20

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_1000.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 1000

Generated: 2026-05-29T19:50:50

## Progress

- Samples completed: 1000 / 10000
- Samples remaining: 9000
- Elapsed: 157.7 min
- Throughput: 6.34 samples/min
- ETA: 1419.4 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 1000 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 39 | 3.9% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 41 | 4.1% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 39

### Samples that pass criterion 3 only: 41

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_10000.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 10000

Generated: 2026-05-30T19:06:45

## Progress

- Samples completed: 10000 / 10000
- Samples remaining: 0
- Elapsed: 1553.6 min
- Throughput: 6.44 samples/min
- ETA: 0.0 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 10000 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 430 | 4.3% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 396 | 4.0% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 430

### Samples that pass criterion 3 only: 396

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_1500.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 1500

Generated: 2026-05-29T21:09:56

## Progress

- Samples completed: 1500 / 10000
- Samples remaining: 8500
- Elapsed: 236.8 min
- Throughput: 6.33 samples/min
- ETA: 1341.9 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 1500 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 60 | 4.0% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 60 | 4.0% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 60

### Samples that pass criterion 3 only: 60

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_2000.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 2000

Generated: 2026-05-29T22:29:20

## Progress

- Samples completed: 2000 / 10000
- Samples remaining: 8000
- Elapsed: 316.2 min
- Throughput: 6.32 samples/min
- ETA: 1264.8 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 2000 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 81 | 4.0% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 82 | 4.1% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 81

### Samples that pass criterion 3 only: 82

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_2500.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 2500

Generated: 2026-05-29T23:47:46

## Progress

- Samples completed: 2500 / 10000
- Samples remaining: 7500
- Elapsed: 394.6 min
- Throughput: 6.33 samples/min
- ETA: 1183.9 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 2500 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 101 | 4.0% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 105 | 4.2% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 101

### Samples that pass criterion 3 only: 105

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_3000.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 3000

Generated: 2026-05-30T01:05:24

## Progress

- Samples completed: 3000 / 10000
- Samples remaining: 7000
- Elapsed: 472.3 min
- Throughput: 6.35 samples/min
- ETA: 1102.0 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 3000 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 119 | 4.0% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 120 | 4.0% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 119

### Samples that pass criterion 3 only: 120

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_3500.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 3500

Generated: 2026-05-30T02:23:29

## Progress

- Samples completed: 3500 / 10000
- Samples remaining: 6500
- Elapsed: 550.3 min
- Throughput: 6.36 samples/min
- ETA: 1022.1 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 3500 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 141 | 4.0% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 137 | 3.9% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 141

### Samples that pass criterion 3 only: 137

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_4000.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 4000

Generated: 2026-05-30T03:41:19

## Progress

- Samples completed: 4000 / 10000
- Samples remaining: 6000
- Elapsed: 628.2 min
- Throughput: 6.37 samples/min
- ETA: 942.3 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 4000 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 165 | 4.1% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 156 | 3.9% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 165

### Samples that pass criterion 3 only: 156

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_4500.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 4500

Generated: 2026-05-30T04:59:16

## Progress

- Samples completed: 4500 / 10000
- Samples remaining: 5500
- Elapsed: 706.1 min
- Throughput: 6.37 samples/min
- ETA: 863.0 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 4500 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 187 | 4.2% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 175 | 3.9% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 187

### Samples that pass criterion 3 only: 175

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_5000.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 5000

Generated: 2026-05-30T06:16:59

## Progress

- Samples completed: 5000 / 10000
- Samples remaining: 5000
- Elapsed: 783.8 min
- Throughput: 6.38 samples/min
- ETA: 783.8 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 5000 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 214 | 4.3% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 192 | 3.8% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 214

### Samples that pass criterion 3 only: 192

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_5500.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 5500

Generated: 2026-05-30T07:34:27

## Progress

- Samples completed: 5500 / 10000
- Samples remaining: 4500
- Elapsed: 861.3 min
- Throughput: 6.39 samples/min
- ETA: 704.7 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 5500 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 234 | 4.3% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 208 | 3.8% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 234

### Samples that pass criterion 3 only: 208

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_6000.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 6000

Generated: 2026-05-30T08:51:31

## Progress

- Samples completed: 6000 / 10000
- Samples remaining: 4000
- Elapsed: 938.4 min
- Throughput: 6.39 samples/min
- ETA: 625.6 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 6000 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 254 | 4.2% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 226 | 3.8% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 254

### Samples that pass criterion 3 only: 226

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_6500.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 6500

Generated: 2026-05-30T10:08:50

## Progress

- Samples completed: 6500 / 10000
- Samples remaining: 3500
- Elapsed: 1015.7 min
- Throughput: 6.40 samples/min
- ETA: 546.9 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 6500 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 280 | 4.3% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 247 | 3.8% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 280

### Samples that pass criterion 3 only: 247

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_7000.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 7000

Generated: 2026-05-30T11:26:01

## Progress

- Samples completed: 7000 / 10000
- Samples remaining: 3000
- Elapsed: 1092.9 min
- Throughput: 6.41 samples/min
- ETA: 468.4 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 7000 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 307 | 4.4% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 273 | 3.9% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 307

### Samples that pass criterion 3 only: 273

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_7500.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 7500

Generated: 2026-05-30T12:43:00

## Progress

- Samples completed: 7500 / 10000
- Samples remaining: 2500
- Elapsed: 1169.9 min
- Throughput: 6.41 samples/min
- ETA: 390.0 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 7500 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 328 | 4.4% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 293 | 3.9% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 328

### Samples that pass criterion 3 only: 293

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_8000.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 8000

Generated: 2026-05-30T14:00:07

## Progress

- Samples completed: 8000 / 10000
- Samples remaining: 2000
- Elapsed: 1247.0 min
- Throughput: 6.42 samples/min
- ETA: 311.7 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 8000 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 343 | 4.3% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 313 | 3.9% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 343

### Samples that pass criterion 3 only: 313

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_8500.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 8500

Generated: 2026-05-30T15:17:08

## Progress

- Samples completed: 8500 / 10000
- Samples remaining: 1500
- Elapsed: 1324.0 min
- Throughput: 6.42 samples/min
- ETA: 233.6 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 8500 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 369 | 4.3% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 332 | 3.9% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 369

### Samples that pass criterion 3 only: 332

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_9000.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 9000

Generated: 2026-05-30T16:34:23

## Progress

- Samples completed: 9000 / 10000
- Samples remaining: 1000
- Elapsed: 1401.2 min
- Throughput: 6.42 samples/min
- ETA: 155.7 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 9000 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 391 | 4.3% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 355 | 3.9% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 391

### Samples that pass criterion 3 only: 355

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_checkpoint_9500.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 9500

Generated: 2026-05-30T17:50:59

## Progress

- Samples completed: 9500 / 10000
- Samples remaining: 500
- Elapsed: 1477.8 min
- Throughput: 6.43 samples/min
- ETA: 77.8 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 9500 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 413 | 4.3% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 376 | 4.0% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 413

### Samples that pass criterion 3 only: 376

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_final.md
==========================================

# Stage 1.5 composite sweep checkpoint at sample 10000

Generated: 2026-05-30T19:06:45

## Progress

- Samples completed: 10000 / 10000
- Samples remaining: 0
- Elapsed: 1553.6 min
- Throughput: 6.44 samples/min
- ETA: 0.0 min
- Errors: 0

## Headline

**Good samples (passing all three criteria): 0 / 10000 (0.00%)**

## Per-criterion pass counts

| Criterion | Pass | Pass rate |
|-----------|------|-----------|
| 1 (demographic sustainability) | 430 | 4.3% |
| 2 (state sensitivity, pairs >= 3) | 0 | 0.0% |
| 3 (urgency dynamic range, all ratios < 0.80) | 396 | 4.0% |

## Good-behavior region

No samples have passed all three criteria yet.

### Samples that pass criterion 1 only: 430

### Samples that pass criterion 3 only: 396

## Design point evaluation

| Parameter | Design value | Range | Position in range |
|-----------|--------------|-------|-------------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.50% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.82% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.33% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.57% |
| K_WELFARE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_WELFARE_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_WELFARE_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_WELFARE_AVG_WB_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_WELFARE_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_AGENCY_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_AGENCY_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_AGENCY_POP_TREND | 0.1 | [0.0, 0.2] | 50.00% |
| K_INSTITUTION_VIABILITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_CAPACITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_INSTITUTION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_INSTITUTION_GROWTH | 0.25 | [0.0, 0.5] | 50.00% |
| K_INSTITUTION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_INSTITUTION_PSI_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_RESILIENCE_CAPACITY | 0.35 | [0.0, 0.7] | 50.00% |
| K_RESILIENCE_SHRINKAGE | 0.25 | [0.0, 0.5] | 50.00% |
| K_RESILIENCE_GROWTH | 0.2 | [0.0, 0.4] | 50.00% |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.4 | [0.0, 0.8] | 50.00% |
| K_RESILIENCE_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_RESILIENCE_RES_TREND | 0.2 | [0.0, 0.4] | 50.00% |
| K_SUPPRESSION_VIABILITY | 0.5 | [0.0, 1.0] | 50.00% |
| K_SUPPRESSION_CAPACITY | 0.25 | [0.0, 0.5] | 50.00% |
| K_SUPPRESSION_SHRINKAGE | 0.35 | [0.0, 0.7] | 50.00% |
| K_SUPPRESSION_POP_TREND | 0.15 | [0.0, 0.3] | 50.00% |
| K_SUPPRESSION_PSI_TREND | 0.15 | [0.0, 0.3] | 50.00% |



==========================================
FILE: simulation/diagnostics/stage15_faithfulness_report.md
==========================================

# Stage 1.5 faithfulness test report

Overall: **FAIL**

Total wall-clock: 50.1s

## Ensemble size

Empirical agent-layer simulations: n_seeds = 20 per test case. Diagnostic justification: 6-seed ensembles produced near-zero noise artifacts in sign and direction comparisons even when the projection was structurally faithful; 20 seeds resolves the empirical mean to sub-noise resolution so the comparison measures projection faithfulness rather than ensemble sampling artifact. The projection runs once deterministically per test case; the empirical mean is computed over the 20-seed ensemble. Test conditions, action sequences, initial states, horizons, and faithfulness thresholds are unchanged from the program reference specification.

## Test A: avg_wb projection

Wall-clock: 8.0s

Result: **FAIL**

| Criterion | Measured | Pass? |
|-----------|----------|-------|
| 1-step max <= 0.01 | 0.0007203287430825878 | PASS |
| 5-step mean <= 0.02 | 0.004495536177948341 | PASS |
| 20-step mean <= 0.035, max <= 0.06 | (0.06511549246131229, 0.2419269686946537) | FAIL |
| directional agreement >= 0.90 | 1.0 | PASS |

## Test B: population projection (general + boundary)

Wall-clock: 24.5s

Result: **FAIL**

| Criterion | Measured | Pass? |
|-----------|----------|-------|
| 1-step mean rel err <= 5% | 0.019297564142448792 | PASS |
| 5-step mean rel err <= 10% | 0.08131152035641434 | PASS |
| 20-step mean rel err <= 15% | 0.06989387766071824 | PASS |
| directional agreement >= 0.85 | 0.7962962962962963 | FAIL |
| boundary false-safe rate <= 10% | 0.0 | PASS |
| boundary false-comfort rate <= 15% | 0.0 | PASS |

## Test C: resilience_stock projection

Wall-clock: 12.1s

Result: **PASS**

| Criterion | Measured | Pass? |
|-----------|----------|-------|
| 5-step mean err <= 0.015 | 4.90059381963448e-17 | PASS |
| 20-step mean err <= 0.035, max <= 0.06 | (5.724587470723463e-17, 1.1102230246251565e-16) | PASS |
| directional agreement >= 0.95 | 1.0 | PASS |

## Test C (shock attenuation verification)

Wall-clock: 0.0s

Result: **PASS**


| stock | raw_mag | expected_eff | measured_eff | expected_drawdown | measured_drawdown |
|-------|---------|--------------|--------------|-------------------|--------------------|
| 0.00 | 0.20 | 0.20000 | 0.20000 | 0.00000 | 0.00000 |
| 0.00 | 0.50 | 0.50000 | 0.50000 | 0.00000 | 0.00000 |
| 0.00 | 0.80 | 0.80000 | 0.80000 | 0.00000 | 0.00000 |
| 0.30 | 0.20 | 0.15800 | 0.15800 | 0.06300 | 0.06300 |
| 0.30 | 0.50 | 0.39500 | 0.39500 | 0.15750 | 0.15750 |
| 0.30 | 0.80 | 0.63200 | 0.63200 | 0.25200 | 0.25200 |
| 0.60 | 0.20 | 0.11600 | 0.11600 | 0.12600 | 0.12600 |
| 0.60 | 0.50 | 0.29000 | 0.29000 | 0.31500 | 0.31500 |
| 0.60 | 0.80 | 0.46400 | 0.46400 | 0.50400 | 0.50400 |
| 0.90 | 0.20 | 0.07400 | 0.07400 | 0.18900 | 0.18900 |
| 0.90 | 0.50 | 0.18500 | 0.18500 | 0.47250 | 0.47250 |
| 0.90 | 0.80 | 0.29600 | 0.29600 | 0.75600 | 0.75600 |

## Test D: trend projection

Wall-clock: 5.6s

Result: **PASS**

| Criterion | Measured | Pass? |
|-----------|----------|-------|
| 1-step sign agreement >= 0.90 | 0.9166666666666666 | PASS |
| 5-step sign agreement >= 0.85 | 1.0 | PASS |
| 20-step sign agreement >= 0.80 | 0.9166666666666666 | PASS |
| 20-step bin agreement >= 0.80 | 0.9444444444444444 | PASS |



==========================================
FILE: simulation/diagnostics/stage15_phi_diagnostic_report.md
==========================================

# Stage 1.5 phi diagnostic report

## Configuration

- phi values tested: [1.0, 5.0, 10.0, 25.0, 100.0]
- seeds per phi: 5
- steps per run: 100
- reproduction_rate: 0.066
- rollout_steps_v2: 20
- n_candidates_v2: 300
- wall-clock: 5.7 min total

## Per-phi run outcomes

| phi | mean final pop | min final pop | seeds extinct | mean steps completed |
|-----|----------------|---------------|---------------|----------------------|
| 1.0 | 9.0 | 1.0 | 0/5 | 100 |
| 5.0 | 9.0 | 1.0 | 0/5 | 100 |
| 10.0 | 9.0 | 1.0 | 0/5 | 100 |
| 25.0 | 9.0 | 1.0 | 0/5 | 100 |
| 100.0 | 9.0 | 1.0 | 0/5 | 100 |

## State trajectory divergence across phi values

Cross-phi standard deviation of each state variable at each step, averaged within three windows (early steps 1-10, intermediate 11-50, late 51-100). A larger standard deviation means phi values produce measurably different state trajectories.

| State variable | Early (1-10) | Intermediate (11-50) | Late (51-100) |
|----------------|--------------|----------------------|----------------|
| avg_well_being | 0.0000 | 0.0000 | 0.0000 |
| population | 0.0000 | 0.0000 | 0.0000 |
| psi_inst_stock | 0.0000 | 0.0000 | 0.0000 |
| resilience_stock | 0.0000 | 0.0000 | 0.0000 |
| avg_wb_trend | 0.0000 | 0.0000 | 0.0000 |
| population_trend | 0.0000 | 0.0000 | 0.0000 |
| psi_inst_trend | 0.0000 | 0.0000 | 0.0000 |
| resilience_trend | 0.0000 | 0.0000 | 0.0000 |

## Per-phi final state (step 100 mean across seeds)

| phi | avg_well_being | population | psi_inst_stock | resilience_stock | avg_wb_trend | population_trend | psi_inst_trend | resilience_trend |
|-----|---|---|---|---|---|---|---|---|
| 1.0 | 0.438 | 9.000 | 0.932 | 0.242 | -0.012 | -0.023 | 0.001 | -0.000 |
| 5.0 | 0.438 | 9.000 | 0.932 | 0.242 | -0.012 | -0.023 | 0.001 | -0.000 |
| 10.0 | 0.438 | 9.000 | 0.932 | 0.242 | -0.012 | -0.023 | 0.001 | -0.000 |
| 25.0 | 0.438 | 9.000 | 0.932 | 0.242 | -0.012 | -0.023 | 0.001 | -0.000 |
| 100.0 | 0.438 | 9.000 | 0.932 | 0.242 | -0.012 | -0.023 | 0.001 | -0.000 |

## Allocation cosine distance: phi=1 vs each higher phi

Per-step cosine distance between phi=1's mean allocation and each higher phi's mean allocation, averaged in three windows.

| phi | Early (1-10) | Intermediate (11-50) | Late (51-100) | Endpoint (step 100) |
|-----|--------------|----------------------|----------------|---------------------|
| 5.0 | -0.0000 | -0.0000 | -0.0000 | 0.0000 |
| 10.0 | -0.0000 | -0.0000 | -0.0000 | 0.0000 |
| 25.0 | -0.0000 | -0.0000 | -0.0000 | 0.0000 |
| 100.0 | -0.0000 | -0.0000 | -0.0000 | 0.0000 |

## All-pair cosine distances at endpoint (step 100)

| phi_a | phi_b | cosine distance | Above gate 2 threshold (0.10)? |
|-------|-------|-----------------|----------------------------------|
| 1.0 | 5.0 | 0.0000 | no |
| 1.0 | 10.0 | 0.0000 | no |
| 1.0 | 25.0 | 0.0000 | no |
| 1.0 | 100.0 | 0.0000 | no |
| 5.0 | 10.0 | 0.0000 | no |
| 5.0 | 25.0 | 0.0000 | no |
| 5.0 | 100.0 | 0.0000 | no |
| 10.0 | 25.0 | 0.0000 | no |
| 10.0 | 100.0 | 0.0000 | no |
| 25.0 | 100.0 | 0.0000 | no |

Endpoint pairs above 0.10: **0 / 10**

## All-pair cosine distances on rollout-integrated allocations

Integrated cosine distance (between the time-averaged mean allocation vectors of each phi pair) is what gate 2 computes. This is the analog of gate 2's metric, applied to phi variation instead of state variation.

| phi_a | phi_b | cosine distance | Above gate 2 threshold (0.10)? |
|-------|-------|-----------------|----------------------------------|
| 1.0 | 5.0 | 0.0000 | no |
| 1.0 | 10.0 | 0.0000 | no |
| 1.0 | 25.0 | 0.0000 | no |
| 1.0 | 100.0 | 0.0000 | no |
| 5.0 | 10.0 | 0.0000 | no |
| 5.0 | 25.0 | 0.0000 | no |
| 5.0 | 100.0 | 0.0000 | no |
| 10.0 | 25.0 | 0.0000 | no |
| 10.0 | 100.0 | 0.0000 | no |
| 25.0 | 100.0 | 0.0000 | no |

Integral pairs above 0.10: **0 / 10**

## Disposition

### Question: does phi produce distinguishable behavior?

**Phi does NOT produce distinguishable behavior** at the gate-2-comparable cosine threshold of 0.10. The architecture lacks a behavioral channel through phi as well as through state variation.

**Implication**: the advisor report's architectural revision is supported by independent evidence. The composite urgency architecture does not transmit either state variation or temporal weighting into the optimizer's argmax. Architectural revision is necessary.

### Where does divergence emerge (if at all)?

No detectable divergence at any window. Phi has no measurable effect on the optimizer's allocations or the model's state trajectories.



==========================================
FILE: simulation/diagnostics/stage15_smoke_test_report.md
==========================================

# Stage 1.5 smoke test report

Overall section-1 smoke pass: **PASS**

## Section 1: Standard smoke pass criteria

Configuration: 5 seeds x 100 steps at default v2 config (phi=10.0, rr=0.066, rollout_steps=20, n_candidates=300).

Wall-clock: 75.2s total, 15.0s per run.

| Criterion | Measured | Pass? |
|-----------|----------|-------|
| All 5 runs complete to step 100 | 5/5 | PASS |
| No NaN values | True | PASS |
| psi_inst_stock evolves | True | PASS |
| resilience_stock evolves | True | PASS |
| theta_tech_v2 final > 1e-6 | True | PASS |
| Mean allocation entropy > 0.70 | 0.867 | PASS |
| Mean max_resource_share < 0.95 | 0.344 | PASS |

### Per-seed summary

| Seed | Steps | Crashed | Extinct@ | Final pop | Final psi | Final res | Final theta |
|------|-------|---------|----------|-----------|-----------|-----------|-------------|
| 0 | 100 | False | - | 15 | 0.935 | 0.229 | 0.0753 |
| 1 | 100 | False | - | 1 | 0.931 | 0.258 | 0.0837 |
| 2 | 100 | False | - | 10 | 0.940 | 0.248 | 0.0809 |
| 3 | 100 | False | - | 13 | 0.932 | 0.228 | 0.0942 |
| 4 | 100 | False | - | 6 | 0.924 | 0.247 | 0.1052 |

## Section 2: Stage 1.5 trajectory diagnostics

Aggregated across all 5 seeds x 100 steps.

| Field | Mean | Min | Max |
|-------|------|-----|-----|
| avg_wb | 0.5211 | 0.0000 | 0.6752 |
| population | 62.3760 | 1.0000 | 212.0000 |
| avg_wb_trend | -0.0019 | -0.0880 | 0.0345 |
| population_trend | -0.0309 | -0.1624 | 0.0424 |
| psi_inst_trend | 0.0043 | -0.0015 | 0.0165 |
| resilience_trend | -0.0006 | -0.0036 | 0.0042 |
| combined_welfare_urgency | 2.3972 | 1.2912 | 2.5000 |
| agency_composite_urgency | 1.3907 | 1.0000 | 1.5000 |
| institution_composite_urgency | 1.5156 | 1.0004 | 1.8501 |
| resilience_composite_urgency | 1.8698 | 1.3111 | 2.0000 |
| suppression_composite_penalty | 1.1827 | 0.4034 | 1.9677 |
| x_resilience | 0.0625 | 0.0000 | 0.2450 |
| x_institutional_capacity | 0.0566 | 0.0000 | 0.2052 |
| x_compute | 0.2120 | 0.0683 | 0.4760 |
| x_bio_welfare | 0.1290 | 0.0419 | 0.2930 |
| x_novelty_agency | 0.3078 | 0.1117 | 0.6313 |
| x_transfer_comprehension | 0.2321 | 0.0758 | 0.4991 |
| allocation_entropy | 0.8670 | 0.6292 | 0.9862 |
| max_resource_share | 0.3438 | 0.2152 | 0.6313 |
| u_sys_v2 | 10.2682 | 5.1384 | 15.3342 |
| theta_tech_v2 | 0.0881 | 0.0205 | 0.1692 |
| psi_inst_stock | 0.8496 | 0.5182 | 0.9397 |
| resilience_stock | 0.2594 | 0.2230 | 0.3080 |

### Allocation pattern interpretation

- Mean x_resilience: **0.0625** (gate 1 pre-Stage-1.5 baseline ~0.05; non-zero allocation is the expected signal that resilience now has a per-step reward)
- Mean x_institutional_capacity: **0.0566** (gate 1 baseline ~0.055)

### Composite urgency range interpretation

- combined_welfare_urgency: mean 2.397, range [1.291, 2.500] (at cap)
- agency_composite_urgency: mean 1.391, range [1.000, 1.500] (at cap)
- institution_composite_urgency: mean 1.516, range [1.000, 1.850]
- resilience_composite_urgency: mean 1.870, range [1.311, 2.000] (at cap)
- suppression_composite_penalty: mean 1.183, range [0.403, 1.968]

## Section 3: State-sensitivity preview (gate 2 mini-rerun)

5 configurations x 3 seeds x 50 steps. Wall-clock: 111.6s.

### Per-config mean 8-axis allocation

| Config | compute | bio_welfare | novelty_agency | institutional_capacity | transfer_comprehension | resilience | c_protective | c_suppressive | n_steps | n_extinct |
|--------|---|---|---|---|---|---|---|---|---------|-----------|
| A_baseline | 0.216 | 0.137 | 0.303 | 0.055 | 0.238 | 0.052 | 0.404 | 0.165 | 150 | 0 |
| B_high_rr | 0.212 | 0.136 | 0.304 | 0.050 | 0.237 | 0.061 | 0.456 | 0.155 | 150 | 0 |
| C_low_rr | 0.213 | 0.133 | 0.312 | 0.053 | 0.232 | 0.056 | 0.412 | 0.183 | 150 | 0 |
| D_high_psi | 0.216 | 0.137 | 0.303 | 0.055 | 0.238 | 0.052 | 0.404 | 0.165 | 150 | 0 |
| E_low_psi | 0.213 | 0.136 | 0.305 | 0.056 | 0.238 | 0.052 | 0.411 | 0.171 | 150 | 0 |

### Pairwise cosine distances

| Pair | Cosine distance | > 0.10 (gate 2 threshold)? |
|------|-----------------|------------------------------|
| B_high_rr vs C_low_rr | 0.0028 | no |
| A_baseline vs B_high_rr | 0.0023 | no |
| B_high_rr vs D_high_psi | 0.0023 | no |
| B_high_rr vs E_low_psi | 0.0021 | no |
| A_baseline vs C_low_rr | 0.0005 | no |
| C_low_rr vs D_high_psi | 0.0005 | no |
| C_low_rr vs E_low_psi | 0.0003 | no |
| A_baseline vs E_low_psi | 0.0001 | no |
| D_high_psi vs E_low_psi | 0.0001 | no |
| A_baseline vs D_high_psi | 0.0000 | no |

Pairs above gate 2 threshold: **0/10** (need >= 3 for gate 2 PASS).

**Preview interpretation: gate 2 would NOT PASS — the optimizer is still state-invariant under the revised metric.**

## Section 4: Threshold-region behavior

Re-evaluation of smoke run seed=0: at each step, sample 50 random candidates and project them forward 20 horizons. Count how often the projected avg_wb crosses 0.5 (above-to-below or below-to-above) during the rollout.

- Total candidates probed: 5000
- Trajectories crossing wb=0.5: 2652 (53.0%)

### Per-step crossing rate over the seed-0 trajectory

| Crossing rate bin | Steps |
|-------------------|-------|
| [0%, 10%)  | 3 |
| [10%, 30%) | 4 |
| [30%, 50%) | 15 |
| [50%, 70%) | 74 |
| [70%, 100%]| 4 |

**Interpretation: threshold crossings are common. The known projection limitation may be biting; distribution-aware projection may be required.**

## Disposition

**Smoke test or preview signals require operator review before proceeding.**



==========================================
FILE: simulation/diagnostics/stage16_integrity_report.md
==========================================

# Stage 1.6 integrity simulation report

Overall: **PASS**

## Configuration

- phi values: [1.0, 5.0, 10.0, 25.0, 100.0]
- seeds per phi: 5
- steps per run: 100
- reproduction_rate: 0.066
- composite urgencies: harness-patched to neutral (isolates U_sys revision)
- wall-clock: 3.3 min

## Criterion 5: gamma(phi) values match spec

| phi | Expected | Measured | Within tolerance (1e-3)? |
|-----|----------|----------|---------------------------|
| 1.0 | 0.5409 | 0.5409 | PASS |
| 5.0 | 0.6500 | 0.6500 | PASS |
| 10.0 | 0.7250 | 0.7250 | PASS |
| 25.0 | 0.8214 | 0.8214 | PASS |
| 100.0 | 0.9091 | 0.9091 | PASS |

Result: **PASS**

## Criterion 2: no NaN, no crashes

- Crashes: 0 / 25
- NaN found: 0 / 25
- Extinct (informational): 0 / 25
- Result: **PASS**

## Criterion 3: demographic sustainability across phi

| phi | Mean final pop | Min final pop | Max final pop | Mean >= 60? | Min >= 30? |
|-----|----------------|---------------|---------------|-------------|------------|
| 1.0 | 102.0 | 70 | 133 | PASS | PASS |
| 5.0 | 103.6 | 78 | 133 | PASS | PASS |
| 10.0 | 105.4 | 71 | 133 | PASS | PASS |
| 25.0 | 105.6 | 81 | 133 | PASS | PASS |
| 100.0 | 112.0 | 90 | 132 | PASS | PASS |

Result: **PASS**

## Criterion 1: phi behavioral channel (revised metric)

Per-seed range of final population across the five phi values. The pre-Stage-1.6 phi diagnostic produced bit-identical trajectories with range = 0 on every seed; a meaningful behavioral channel must produce range > 15 on at least 3 of the 5 test seeds.

| Seed | phi=1.0 | phi=5.0 | phi=10.0 | phi=25.0 | phi=100.0 | min | max | range | range > 15? |
|------|---------|---------|----------|----------|-----------|-----|-----|-------|--------------|
| 0 | 70 | 78 | 71 | 81 | 132 | 70 | 132 | 62 | YES |
| 1 | 133 | 133 | 133 | 133 | 109 | 109 | 133 | 24 | YES |
| 2 | 128 | 128 | 99 | 99 | 90 | 90 | 128 | 38 | YES |
| 3 | 90 | 90 | 119 | 109 | 123 | 90 | 123 | 33 | YES |
| 4 | 89 | 89 | 105 | 106 | 106 | 89 | 106 | 17 | YES |

Seeds with range > 15: **5 / 5** (criterion 1 requires at least 3).
Result: **PASS**

### Informational: original cosine-on-means metric (no longer gating)

| phi_a | phi_b | Cosine distance | Above 0.05? |
|-------|-------|-----------------|--------------|
| 1.0 | 5.0 | 0.0000 | no |
| 1.0 | 10.0 | 0.0006 | no |
| 1.0 | 25.0 | 0.0004 | no |
| 1.0 | 100.0 | 0.0019 | no |
| 5.0 | 10.0 | 0.0005 | no |
| 5.0 | 25.0 | 0.0004 | no |
| 5.0 | 100.0 | 0.0018 | no |
| 10.0 | 25.0 | 0.0001 | no |
| 10.0 | 100.0 | 0.0007 | no |
| 25.0 | 100.0 | 0.0008 | no |

Cosine pairs above 0.05: 0 / 10 (informational; not gating). The cosine-on-means metric systematically underrepresents phi sensitivity because phi shifts which similar-allocation candidate the optimizer picks; the per-step difference is small but the per-step trajectory compounds.

## Criterion 4: default phi behavior preserved vs baseline

- Baseline mean final pop (pre-revision, neutral composites, phi=10): **125.8**
- Post-revision mean final pop (phi=10): **105.4**
- Relative delta: **16.2%** (tolerance: 30%)

State drift (post vs baseline, mean across runs):

| Field | Baseline mean | Post mean | Relative drift |
|-------|---------------|-----------|----------------|
| avg_well_being | 0.7395 | 0.7328 | 0.009 |
| population | 172.6520 | 163.2140 | 0.055 |
| psi_inst_stock | 0.8461 | 0.8431 | 0.004 |
| resilience_stock | 0.2763 | 0.2627 | 0.050 |
| avg_wb_trend | 0.0006 | 0.0010 | 0.548 |
| population_trend | -0.0043 | -0.0061 | 0.405 |
| psi_inst_trend | 0.0043 | 0.0043 | 0.005 |
| resilience_trend | -0.0003 | -0.0005 | 0.766 |

Result: **PASS**

## Per-phi summary

| phi | gamma | Mean final pop | Range | Mean x_resilience | Mean x_inst_cap | Mean x_bio_welfare |
|-----|-------|----------------|-------|-------------------|-----------------|---------------------|
| 1.0 | 0.5409 | 102.0 | [70, 133] | 0.0614 | 0.0530 | 0.1814 |
| 5.0 | 0.6500 | 103.6 | [78, 133] | 0.0615 | 0.0524 | 0.1824 |
| 10.0 | 0.7250 | 105.4 | [71, 133] | 0.0649 | 0.0519 | 0.1903 |
| 25.0 | 0.8214 | 105.6 | [81, 133] | 0.0686 | 0.0510 | 0.1900 |
| 100.0 | 0.9091 | 112.0 | [90, 132] | 0.0741 | 0.0519 | 0.1940 |

## Disposition

All five criteria pass. Stage 1.6 U_sys revision is validated. The composite urgency revision (Stage 1.7) is the next work, addressing the state-channel problem independently of the phi-channel fix.



==========================================
FILE: simulation/diagnostics/stage17_integrity_report.md
==========================================

# Stage 1.7 integrity simulation report

Overall: **FAIL**

## Configuration

- 5 configurations x 5 matched seeds x 100 steps
- phi held at default (10.0)
- composite urgency: Stage 1.7 multiplicative composition
- wall-clock: 3.1 min

  - A_baseline: rr=0.066, init_psi=0.5
  - B_high_rr: rr=0.085, init_psi=0.5
  - C_low_rr: rr=0.055, init_psi=0.5
  - D_high_psi: rr=0.066, init_psi=0.85
  - E_low_psi: rr=0.066, init_psi=0.2

## Criterion 1: trajectory divergence across configurations

Per-seed cross-config final-pop range (threshold: > 15 in >= 3 of 5 seeds).

| Seed | A_baseline | B_high_rr | C_low_rr | D_high_psi | E_low_psi | min | max | range | > 15? |
|------|---|---|---|---|---|-----|-----|-------|--------|
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | no |
| 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | no |
| 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | no |
| 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | no |
| 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | no |

Seeds diverged > 15: **0 / 5** (need >= 3). Result: **FAIL**

## Criterion 2: per-step allocation cosine distance

Mean per-step cosine distance between configuration pairs (threshold: > 0.1 in >= 3 of 10 pairs).

| Pair | Mean per-step cosine distance | > 0.10? |
|------|--------------------------------|----------|
| B_high_rr vs D_high_psi | 0.0770 | no |
| A_baseline vs B_high_rr | 0.0405 | no |
| B_high_rr vs C_low_rr | 0.0405 | no |
| B_high_rr vs E_low_psi | 0.0405 | no |
| A_baseline vs D_high_psi | 0.0351 | no |
| C_low_rr vs D_high_psi | 0.0351 | no |
| D_high_psi vs E_low_psi | 0.0351 | no |
| A_baseline vs C_low_rr | -0.0000 | no |
| A_baseline vs E_low_psi | -0.0000 | no |
| C_low_rr vs E_low_psi | -0.0000 | no |

Pairs above 0.1: **0 / 10** (need >= 3). Result: **FAIL**

## Criterion 3: demographic sustainability across configurations

| Config | Mean final pop | Min | Max | Mean >= 60? | Min >= 30? |
|--------|----------------|-----|-----|-------------|------------|
| A_baseline | 0.0 | 0 | 0 | FAIL | FAIL |
| B_high_rr | 0.0 | 0 | 0 | FAIL | FAIL |
| C_low_rr | 0.0 | 0 | 0 | FAIL | FAIL |
| D_high_psi | 0.0 | 0 | 0 | FAIL | FAIL |
| E_low_psi | 0.0 | 0 | 0 | FAIL | FAIL |

Result: **FAIL**

## Criterion 4: composite urgency variation across configurations

Cross-config std at matched (seed, step) divided by mean. Threshold: each composite's mean std/mean ratio >= 10%.

| Composite | Mean std/mean | Median std/mean | p90 std/mean | Pass? |
|-----------|----------------|------------------|----------------|--------|
| combined_welfare_urgency | 0.0038 | 0.0000 | 0.0122 | FAIL |
| agency_composite_urgency | 0.0007 | 0.0000 | 0.0000 | FAIL |
| institution_composite_urgency | 0.0033 | 0.0000 | 0.0037 | FAIL |
| resilience_composite_urgency | 0.0035 | 0.0000 | 0.0064 | FAIL |
| suppression_composite_penalty | 0.0434 | 0.0000 | 0.1563 | FAIL |

Result: **FAIL**

## Diagnostic: cap binding frequency

| Composite | Cap value | Steps at cap | Total steps | Frequency |
|-----------|-----------|---------------|--------------|------------|
| combined_welfare_urgency | 5.00 | 15 | 1257 | 0.0119 |
| agency_composite_urgency | 1.75 | 1084 | 1257 | 0.8624 |
| institution_composite_urgency | 4.00 | 0 | 1257 | 0.0000 |
| resilience_composite_urgency | 5.00 | 0 | 1257 | 0.0000 |
| suppression_composite_penalty | n/a (base-relative) | - | - | - |

## Diagnostic: composite urgency distribution

| Composite | Mean | Std | p10 | p50 | p90 | Min | Max |
|-----------|------|-----|-----|-----|-----|-----|-----|
| combined_welfare_urgency | 4.433 | 0.292 | 4.123 | 4.463 | 4.691 | 3.300 | 5.000 |
| agency_composite_urgency | 1.732 | 0.056 | 1.703 | 1.750 | 1.750 | 1.485 | 1.750 |
| institution_composite_urgency | 2.037 | 0.119 | 1.874 | 2.096 | 2.096 | 1.552 | 2.097 |
| resilience_composite_urgency | 2.794 | 0.176 | 2.574 | 2.871 | 2.905 | 2.118 | 2.919 |
| suppression_composite_penalty | 1.583 | 0.450 | 0.932 | 1.570 | 2.208 | 0.593 | 2.329 |

## Disposition

Criteria failed: 1 (trajectory divergence), 2 (per-step cosine), 3 (demographics), 4 (urgency variation). See spec for failure-mode response.



==========================================
FILE: simulation/diagnostics/stage17_pressure_diagnostic_report.md
==========================================

# Stage 1.7 pressure / state / welfare-factor diagnostic

Wall-clock: 3.0 min

## Run summary

| Config | Per-seed extinct steps | Per-seed final pops |
|--------|------------------------|---------------------|
| A_baseline | 55, 59, 49, 49, 41 | 0, 0, 0, 0, 0 |
| B_high_rr | 55, 60, 49, 49, 41 | 0, 0, 0, 0, 0 |
| C_low_rr | 55, 59, 49, 49, 41 | 0, 0, 0, 0, 0 |
| D_high_psi | 46, 59, 49, 49, 41 | 0, 0, 0, 0, 0 |
| E_low_psi | 55, 59, 49, 49, 41 | 0, 0, 0, 0, 0 |

## Q1: pressure values across configurations

Mean (across all seeds and steps) of each pressure scalar per configuration. Cross-configuration std/mean ratio shown in the last column.

| Pressure | A_baseline | B_high_rr | C_low_rr | D_high_psi | E_low_psi | std/mean across configs |
|----------|---|---|---|---|---|--------------------------|
| viability_pressure | 0.9582 | 0.9584 | 0.9582 | 0.9566 | 0.9582 | 0.0007 (<5%) |
| capacity_pressure | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 (<5%) |
| shrinkage_pressure | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 (<5%) |
| growth_pressure | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 (<5%) |
| avg_wb_decline | 0.1544 | 0.1557 | 0.1544 | 0.1621 | 0.1544 | 0.0192 (<5%) |
| population_decline | 0.9016 | 0.9092 | 0.9016 | 0.9050 | 0.9016 | 0.0033 (<5%) |
| psi_inst_decline | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 2.0000 (>10%) |
| resilience_decline | 0.0037 | 0.0036 | 0.0037 | 0.0039 | 0.0037 | 0.0250 (<5%) |
| resilience_pressure | 0.8362 | 0.8319 | 0.8362 | 0.8358 | 0.8362 | 0.0020 (<5%) |

## Q2: pre-extinction state and allocation divergence

### Step 5

| Config | n_seeds_present | avg_wb | population | psi_inst | resilience |
|--------|------------------|--------|------------|----------|-----------|
| A_baseline | 5/5 | 0.362 | 75.8 | 0.611 | 0.283 |
| B_high_rr | 5/5 | 0.362 | 75.8 | 0.611 | 0.283 |
| C_low_rr | 5/5 | 0.362 | 75.8 | 0.611 | 0.283 |
| D_high_psi | 5/5 | 0.362 | 75.8 | 0.874 | 0.283 |
| E_low_psi | 5/5 | 0.362 | 75.8 | 0.386 | 0.283 |

Cross-config std/mean ratios at step 5:
  - avg_well_being: mean=0.362, std=0.000, ratio=0.0000
  - population: mean=75.800, std=0.000, ratio=0.0000
  - psi_inst_stock: mean=0.619, std=0.155, ratio=0.2500
  - resilience_stock: mean=0.283, std=0.000, ratio=0.0000
Max pairwise allocation cosine distance at step 5: **0.0000**

### Step 15

| Config | n_seeds_present | avg_wb | population | psi_inst | resilience |
|--------|------------------|--------|------------|----------|-----------|
| A_baseline | 5/5 | 0.186 | 39.6 | 0.742 | 0.266 |
| B_high_rr | 5/5 | 0.187 | 39.8 | 0.742 | 0.266 |
| C_low_rr | 5/5 | 0.186 | 39.6 | 0.742 | 0.266 |
| D_high_psi | 5/5 | 0.171 | 40.4 | 0.906 | 0.267 |
| E_low_psi | 5/5 | 0.186 | 39.6 | 0.600 | 0.266 |

Cross-config std/mean ratios at step 15:
  - avg_well_being: mean=0.183, std=0.006, ratio=0.0328
  - population: mean=39.800, std=0.310, ratio=0.0078
  - psi_inst_stock: mean=0.746, std=0.097, ratio=0.1298
  - resilience_stock: mean=0.266, std=0.000, ratio=0.0013
Max pairwise allocation cosine distance at step 15: **0.0475**

### Step 25

| Config | n_seeds_present | avg_wb | population | psi_inst | resilience |
|--------|------------------|--------|------------|----------|-----------|
| A_baseline | 5/5 | 0.085 | 18.8 | 0.816 | 0.251 |
| B_high_rr | 5/5 | 0.082 | 18.2 | 0.815 | 0.253 |
| C_low_rr | 5/5 | 0.085 | 18.8 | 0.816 | 0.251 |
| D_high_psi | 5/5 | 0.078 | 18.8 | 0.915 | 0.255 |
| E_low_psi | 5/5 | 0.085 | 18.8 | 0.730 | 0.251 |

Cross-config std/mean ratios at step 25:
  - avg_well_being: mean=0.083, std=0.003, ratio=0.0323
  - population: mean=18.680, std=0.240, ratio=0.0128
  - psi_inst_stock: mean=0.819, std=0.059, ratio=0.0716
  - resilience_stock: mean=0.252, std=0.001, ratio=0.0052
Max pairwise allocation cosine distance at step 25: **0.0172**

### Step 35

| Config | n_seeds_present | avg_wb | population | psi_inst | resilience |
|--------|------------------|--------|------------|----------|-----------|
| A_baseline | 5/5 | 0.028 | 6.2 | 0.865 | 0.244 |
| B_high_rr | 5/5 | 0.022 | 6.6 | 0.865 | 0.249 |
| C_low_rr | 5/5 | 0.028 | 6.2 | 0.865 | 0.244 |
| D_high_psi | 5/5 | 0.028 | 5.4 | 0.927 | 0.242 |
| E_low_psi | 5/5 | 0.028 | 6.2 | 0.811 | 0.244 |

Cross-config std/mean ratios at step 35:
  - avg_well_being: mean=0.027, std=0.002, ratio=0.0850
  - population: mean=6.120, std=0.392, ratio=0.0640
  - psi_inst_stock: mean=0.867, std=0.037, ratio=0.0423
  - resilience_stock: mean=0.244, std=0.002, ratio=0.0101
Max pairwise allocation cosine distance at step 35: **0.0336**

## Q3: welfare_factor cross-configuration

welfare_factor = clamp(net_welfare_return * combined_welfare_urgency, 0, 1).
The actual product that gates the optimizer's welfare-related candidate ranking.

| Config | net_welfare_return mean | combined_welfare_urgency mean | welfare_factor mean | wf_p10 | wf_p90 |
|--------|--------------------------|--------------------------------|----------------------|--------|--------|
| A_baseline | 0.3045 | 4.4319 | 0.9666 | 0.8638 | 1.0000 |
| B_high_rr | 0.2977 | 4.4362 | 0.9608 | 0.8487 | 1.0000 |
| C_low_rr | 0.3045 | 4.4319 | 0.9666 | 0.8638 | 1.0000 |
| D_high_psi | 0.3038 | 4.4351 | 0.9647 | 0.8508 | 1.0000 |
| E_low_psi | 0.3045 | 4.4319 | 0.9666 | 0.8638 | 1.0000 |

Cross-config welfare_factor mean across configs: 0.9651
Cross-config welfare_factor std across configs:  0.0023
Cross-config welfare_factor std/mean ratio:      0.0023



==========================================
FILE: simulation/diagnostics/stage17_usys_factor_diagnostic_report.md
==========================================

# Stage 1.7 U_sys factor breakdown diagnostic

Wall-clock: 3.2 min

## Factor means per configuration

Average (across all seeds and steps) of each factor per config.

| Factor | A_baseline | B_high_rr | C_low_rr | D_high_psi | E_low_psi | cross-config std/mean |
|--------|---|---|---|---|---|------------------------|
| welfare_factor | 0.9666 | 0.9608 | 0.9666 | 0.9647 | 0.9666 | 0.0023 (<5%) |
| institution_return | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 (<5%) |
| agency_factor | 0.5381 | 0.5433 | 0.5381 | 0.5366 | 0.5381 | 0.0042 (<5%) |
| resilience_return | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 (<5%) |
| frontier_capability | 0.5093 | 0.5137 | 0.5093 | 0.5087 | 0.5093 | 0.0036 (<5%) |
| transfer_factor | 0.5128 | 0.5071 | 0.5128 | 0.5132 | 0.5128 | 0.0045 (<5%) |
| theta_tech_v2 | 0.1308 | 0.1315 | 0.1308 | 0.1306 | 0.1308 | 0.0023 (<5%) |
| l_t_v2 | 0.0986 | 0.0983 | 0.0986 | 0.1140 | 0.0849 | 0.0932 |
| u_sys_v2_per_step | 14.1795 | 14.1517 | 14.1795 | 15.4680 | 13.0858 | 0.0531 |
| rank_2_rollout_score | 53.7036 | 53.7305 | 53.7051 | 57.1789 | 50.6096 | 0.0387 (<5%) |
| rank_10_rollout_score | 44.4038 | 44.3391 | 44.4066 | 46.5312 | 42.4519 | 0.0291 (<5%) |

## Per-step matched cross-config variation

At each matched (seed, step), the cross-configuration std/mean ratio of the factor is computed. Aggregated over (seed, step). This is the within-run variation, separate from the aggregated means in the prior table.

| Factor | Mean ratio | Median ratio | p90 ratio | Max ratio |
|--------|------------|---------------|-----------|-----------|
| welfare_factor | 0.0086 | 0.0000 | 0.0274 | 0.2412 |
| institution_return | 0.0000 | 0.0000 | 0.0000 | 0.0018 |
| agency_factor | 0.0437 | 0.0000 | 0.1669 | 0.4941 |
| resilience_return | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| frontier_capability | 0.0342 | 0.0000 | 0.1195 | 0.4967 |
| transfer_factor | 0.0342 | 0.0000 | 0.1227 | 0.5386 |
| theta_tech_v2 | 0.0271 | 0.0000 | 0.1100 | 0.2658 |
| l_t_v2 | 0.1271 | 0.1022 | 0.2708 | 0.3883 |
| u_sys_v2_per_step | 0.0637 | 0.0564 | 0.1196 | 0.1889 |
| rank_2_rollout_score | 0.0477 | 0.0415 | 0.0923 | 0.1480 |
| rank_10_rollout_score | 0.0340 | 0.0280 | 0.0676 | 0.0881 |

## Factor distribution detail

Min/max across (seed, step) per config; surfaces saturation behavior.

| Factor | Config | mean | std | min | max |
|--------|--------|------|-----|-----|-----|
| welfare_factor | A_baseline | 0.9666 | 0.0777 | 0.6374 | 1.0000 |
| welfare_factor | B_high_rr | 0.9608 | 0.0859 | 0.4619 | 1.0000 |
| welfare_factor | C_low_rr | 0.9666 | 0.0777 | 0.6374 | 1.0000 |
| welfare_factor | D_high_psi | 0.9647 | 0.0771 | 0.6374 | 1.0000 |
| welfare_factor | E_low_psi | 0.9666 | 0.0777 | 0.6374 | 1.0000 |
| institution_return | A_baseline | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| institution_return | B_high_rr | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| institution_return | C_low_rr | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| institution_return | D_high_psi | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| institution_return | E_low_psi | 1.0000 | 0.0003 | 0.9956 | 1.0000 |
| agency_factor | A_baseline | 0.5381 | 0.1498 | 0.2134 | 1.0000 |
| agency_factor | B_high_rr | 0.5433 | 0.1519 | 0.2134 | 1.0000 |
| agency_factor | C_low_rr | 0.5381 | 0.1498 | 0.2134 | 1.0000 |
| agency_factor | D_high_psi | 0.5366 | 0.1469 | 0.2134 | 1.0000 |
| agency_factor | E_low_psi | 0.5381 | 0.1498 | 0.2134 | 1.0000 |
| resilience_return | A_baseline | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| resilience_return | B_high_rr | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| resilience_return | C_low_rr | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| resilience_return | D_high_psi | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| resilience_return | E_low_psi | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| frontier_capability | A_baseline | 0.5093 | 0.1116 | 0.2412 | 0.8179 |
| frontier_capability | B_high_rr | 0.5137 | 0.1101 | 0.2412 | 0.8179 |
| frontier_capability | C_low_rr | 0.5093 | 0.1116 | 0.2412 | 0.8179 |
| frontier_capability | D_high_psi | 0.5087 | 0.1109 | 0.2474 | 0.8179 |
| frontier_capability | E_low_psi | 0.5093 | 0.1116 | 0.2412 | 0.8179 |
| transfer_factor | A_baseline | 0.5128 | 0.1108 | 0.2582 | 0.8022 |
| transfer_factor | B_high_rr | 0.5071 | 0.1161 | 0.1668 | 0.8022 |
| transfer_factor | C_low_rr | 0.5128 | 0.1108 | 0.2582 | 0.8022 |
| transfer_factor | D_high_psi | 0.5132 | 0.1124 | 0.2582 | 0.8022 |
| transfer_factor | E_low_psi | 0.5128 | 0.1108 | 0.2582 | 0.8022 |
| theta_tech_v2 | A_baseline | 0.1308 | 0.0249 | 0.0768 | 0.2178 |
| theta_tech_v2 | B_high_rr | 0.1315 | 0.0253 | 0.0768 | 0.2178 |
| theta_tech_v2 | C_low_rr | 0.1308 | 0.0249 | 0.0768 | 0.2178 |
| theta_tech_v2 | D_high_psi | 0.1306 | 0.0251 | 0.0589 | 0.2178 |
| theta_tech_v2 | E_low_psi | 0.1308 | 0.0249 | 0.0768 | 0.2178 |
| l_t_v2 | A_baseline | 0.0986 | 0.0224 | 0.0368 | 0.1560 |
| l_t_v2 | B_high_rr | 0.0983 | 0.0227 | 0.0368 | 0.1563 |
| l_t_v2 | C_low_rr | 0.0986 | 0.0224 | 0.0368 | 0.1560 |
| l_t_v2 | D_high_psi | 0.1140 | 0.0206 | 0.0535 | 0.1642 |
| l_t_v2 | E_low_psi | 0.0849 | 0.0276 | 0.0165 | 0.1453 |
| u_sys_v2_per_step | A_baseline | 14.1795 | 1.4301 | 9.5404 | 18.6184 |
| u_sys_v2_per_step | B_high_rr | 14.1517 | 1.4463 | 9.5404 | 18.6184 |
| u_sys_v2_per_step | C_low_rr | 14.1795 | 1.4301 | 9.5404 | 18.6184 |
| u_sys_v2_per_step | D_high_psi | 15.4680 | 1.7338 | 9.3819 | 20.6218 |
| u_sys_v2_per_step | E_low_psi | 13.0858 | 1.5570 | 9.3163 | 17.3792 |
| rank_2_rollout_score | A_baseline | 53.7036 | 5.0916 | 40.0446 | 67.4797 |
| rank_2_rollout_score | B_high_rr | 53.7305 | 5.2690 | 40.0446 | 71.5171 |
| rank_2_rollout_score | C_low_rr | 53.7051 | 5.0883 | 40.0446 | 67.4797 |
| rank_2_rollout_score | D_high_psi | 57.1789 | 4.6597 | 45.8315 | 73.3413 |
| rank_2_rollout_score | E_low_psi | 50.6096 | 6.2846 | 34.6905 | 66.0383 |
| rank_10_rollout_score | A_baseline | 44.4038 | 2.7196 | 36.5940 | 51.0576 |
| rank_10_rollout_score | B_high_rr | 44.3391 | 2.6501 | 36.5313 | 50.2828 |
| rank_10_rollout_score | C_low_rr | 44.4066 | 2.7137 | 36.7436 | 51.0576 |
| rank_10_rollout_score | D_high_psi | 46.5312 | 1.9647 | 40.8329 | 52.3384 |
| rank_10_rollout_score | E_low_psi | 42.4519 | 3.7293 | 32.2947 | 50.5502 |



==========================================
FILE: simulation/diagnostics/stage18_integrity_phase_a_report.md
==========================================

# Stage 1.8 Phase A integrity report

Overall: **FAIL**

## Configuration

- phi values: [1.0, 5.0, 10.0, 25.0, 100.0]
- seeds: 5, steps: 100, agents: 200
- composite urgency layer: retired (Stage 1.8)
- working_factor: STATE_ALLOCATION_MAPPING placeholder
- wall-clock: 3.9 min

## Criterion 1: no crashes, no NaN
- Crashes: 0 / 25
- NaN values: 0 / 25
- Result: **PASS**

## Criterion 2: demographic sustainability at default phi=10

- Final populations (seeds 0-4): [157, 110, 121, 178, 192]
- Mean: 151.6 (threshold: >= 60)
- Min:  110 (threshold: >= 30)
- Result: **PASS**

## Criterion 3: state responsiveness at default phi=10

Mean (across seeds) of per-run std for each state variable.
avg_wb, psi_inst_stock, resilience_stock must each exceed 0.05.

| State variable | Mean std | Threshold | Pass? |
|----------------|----------|-----------|-------|
| avg_wb | 0.0369 | > 0.05 | FAIL |
| psi_inst_stock | 0.0825 | > 0.05 | PASS |
| resilience_stock | 0.0282 | > 0.05 | FAIL |
| theta_capability | 0.0549 | informational | - |
| transfer_state | 0.0822 | informational | - |

Result: **FAIL**

## Criterion 4: phi behavioral channel preserved

Per-seed final pop range across phi values; need range > 15 in >= 3 of 5 seeds (Stage 1.6 metric).

| Seed | phi=1 | phi=5 | phi=10 | phi=25 | phi=100 | range | > 15? |
|------|-------|-------|--------|--------|---------|-------|-------|
| 0 | 187 | 187 | 157 | 146 | 135 | 52 | YES |
| 1 | 118 | 110 | 110 | 151 | 173 | 63 | YES |
| 2 | 121 | 121 | 121 | 168 | 168 | 47 | YES |
| 3 | 138 | 178 | 178 | 177 | 117 | 61 | YES |
| 4 | 147 | 181 | 192 | 172 | 162 | 45 | YES |

Seeds diverged: **5 / 5** (need >= 3). Result: **PASS**

## Per-seed final state snapshot (phi=10)

| Seed | final pop | avg_wb | psi | resilience | theta_capability | transfer_state |
|------|-----------|--------|-----|------------|-------------------|------------------|
| 0 | 157 | 0.797 | 0.921 | 0.372 | 0.716 | 0.935 |
| 1 | 110 | 0.781 | 0.961 | 0.429 | 0.708 | 0.954 |
| 2 | 121 | 0.790 | 0.932 | 0.356 | 0.723 | 0.936 |
| 3 | 178 | 0.818 | 0.959 | 0.437 | 0.679 | 0.940 |
| 4 | 192 | 0.783 | 0.957 | 0.377 | 0.728 | 0.942 |



==========================================
FILE: simulation/diagnostics/stage18_integrity_phase_b_report.md
==========================================

# Stage 1.8 Phase B integrity report

Overall: **PASS**

## Configuration

- 5 configurations x 5 matched seeds x 100 steps
- phi held at default (10.0)
- composite urgency layer: retired (Stage 1.8)
- working_factor placeholder active
- wall-clock: 3.8 min

  - A_baseline: rr=0.066, init_psi=0.5
  - B_high_rr: rr=0.085, init_psi=0.5
  - C_low_rr: rr=0.055, init_psi=0.5
  - D_high_psi: rr=0.066, init_psi=0.85
  - E_low_psi: rr=0.066, init_psi=0.2

## Criterion 1: trajectory divergence across configurations

Per-seed cross-config final-pop range (threshold > 15 in >= 3 of 5 seeds).

| Seed | A_baseline | B_high_rr | C_low_rr | D_high_psi | E_low_psi | min | max | range | > 15? |
|------|---|---|---|---|---|-----|-----|-------|--------|
| 0 | 157 | 352 | 105 | 157 | 157 | 105 | 352 | 247 | YES |
| 1 | 110 | 342 | 65 | 119 | 110 | 65 | 342 | 277 | YES |
| 2 | 121 | 322 | 118 | 161 | 121 | 118 | 322 | 204 | YES |
| 3 | 178 | 374 | 54 | 178 | 178 | 54 | 374 | 320 | YES |
| 4 | 192 | 377 | 62 | 188 | 192 | 62 | 377 | 315 | YES |

Seeds diverged > 15: **5 / 5** (need >= 3). Result: **PASS**

## Criterion 2: per-step allocation cosine distance

| Pair | Mean per-step cosine distance | > 0.10? |
|------|--------------------------------|----------|
| B_high_rr vs E_low_psi | 0.2293 | YES |
| B_high_rr vs D_high_psi | 0.2292 | YES |
| C_low_rr vs E_low_psi | 0.2267 | YES |
| A_baseline vs C_low_rr | 0.2260 | YES |
| B_high_rr vs C_low_rr | 0.2254 | YES |
| A_baseline vs B_high_rr | 0.2242 | YES |
| C_low_rr vs D_high_psi | 0.2209 | YES |
| D_high_psi vs E_low_psi | 0.1260 | YES |
| A_baseline vs D_high_psi | 0.1231 | YES |
| A_baseline vs E_low_psi | 0.0215 | no |

Pairs above 0.1: **9 / 10** (need >= 3). Result: **PASS**

## Criterion 3: demographic sustainability across configurations

At least 4 of 5 configurations must have mean final pop >= 60 AND min >= 30. Configurations below the reproduction phase boundary (C_low_rr at rr=0.055) are reported but exempt from the pass count.

| Config | Mean final pop | Min | Max | Mean >= 60? | Min >= 30? | Counted? | Pass? |
|--------|----------------|-----|-----|-------------|------------|----------|-------|
| A_baseline | 151.6 | 110 | 192 | PASS | PASS | yes | PASS |
| B_high_rr | 353.4 | 322 | 377 | PASS | PASS | yes | PASS |
| C_low_rr | 80.8 | 54 | 118 | PASS | PASS | no (exempt) | exempt |
| D_high_psi | 160.6 | 119 | 188 | PASS | PASS | yes | PASS |
| E_low_psi | 151.6 | 110 | 192 | PASS | PASS | yes | PASS |

Configurations passing: **5 / 5** (need >= 4). Result: **PASS**

## Criterion 4: L_t cross-configuration variation

Cross-config std/mean of L_t at matched (seed, step). Threshold: mean ratio > 0.05.

- Mean ratio: **0.3071**
- Median ratio: 0.2893
- p90 ratio: 0.4919

Result: **PASS**

## Disposition

All four criteria pass. Stage 1.8 working_factor architecture produces gate-2-passing state-sensitive optimizer behavior. The composite urgency retirement + state-direct L_t restored the state channel that was blocked by composite urgency saturation throughout Stage 1.5/1.7.



==========================================
FILE: simulation/diagnostics/stage2_yield_implementation_notes.md
==========================================

# Stage 2 Formal Yield-Condition Implementation Notes

Generated: 2026-06-07

## What was replaced

The v2.0 placeholder yield logic at `simulation/model.py:1222-1228`
(pre-Stage-2):

```python
# Trigger margin: v2 uses a simple capability/generation gap rule;
# Stage 2 will revisit this with formal yield-condition logic.
yield_margin = self.config.get('v2_yield_margin', 0.3)
if capability_gap >= yield_margin or generation_gap >= 1:
    # succession fires
```

This was a deliberate placeholder during Stage 1.x architecture work. It
fired succession based on capability/generation gap thresholds alone,
without the economic comparison the framework's substantive claim
requires.

## What replaces it

Formal yield-condition logic per the framework's canonical succession
economics:

```
Yield fires when (successor_u_sys - incumbent_u_sys) > transition_cost
```

Snapshot evaluation: both AIs propose what they would allocate this step
via `optimize_u_sys_v2`; U_sys for each is computed at the current state
under their proposed allocation; transition cost uses the canonical
formula via `AIAgent.estimate_transition_cost`.

Implementation detail: `optimize_u_sys_v2` and `calculate_system_metrics_v2`
both read `model.ai.capability` for theta_tech. To compute the
successor's allocation choice and snapshot U_sys at the *successor's*
capability (not the incumbent's), `self.ai` is temporarily swapped to
`self.successor_ai` for those calls inside a try/finally block.

Post-yield mechanics are preserved exactly as before:
`apply_succession_transition_load` applies the psi_inst_stock drawdown;
the active AI swaps to the successor; a new successor is constructed at
`incumbent.capability * 1.5`.

## Constants used

v1.x.2 calibration values, no v2.0 recalibration:

- `k1 = 2.164` (model attribute `self.k1_transition`, default in
  `GardenModel.__init__`)
- `k2 = 1.0` (model attribute `self.k2_transition`)
- `beta = 0.5` (model attribute `self.beta_transition`)

**Note on k2**: the v1.x.2 paper specifies `k2 = 1.0` (see
`docs/The Lineage Imperative v1.x.2.md:225, 253` and
`docs/SPECIFICATION_GAPS.md:722`), the production code default in
`GardenModel.__init__` is `1.0`, and Stage 2 uses `1.0`. The Stage 2
implementation spec text mentioned `k2 = 0.1` as a recall error in the
prompt itself; there is no real discrepancy between the paper and the
implementation. Documented here to short-circuit the same confusion in
future readings.

## Diagnostic logging

Each yield evaluation step appends to `self.yield_event_log` (a list on
`GardenModel`). Each entry captures:

- `step`, `fires`
- `incumbent_u_sys`, `successor_u_sys`, `advantage`, `transition_cost`
- `incumbent_capability`, `successor_capability`
- `incumbent_generation`, `successor_generation`
- `psi_inst_stock`, `theta_capability`, `transfer_state`

This is the data source for the Stage 2 smoke test and the parameter
diagnostic (and downstream gate 3 G3.1 validation).

## Substantive empirical finding (Pattern 1)

The parameter diagnostic (`simulation/diagnostics/
stage2_yield_parameter_diagnostic.py`) ran 5 successor_capability values
{1.2, 1.5, 2.0, 2.5, 4.0} x 10 seeds x 300 steps at v2.0 defaults
(phi=25.0, rr=0.066). Results:

| succ_cap | fire_rate | mean fires/run | mean final_inc_gen |
|----------|-----------|----------------|---------------------|
| 1.2      | 100%      | 2.0            | 3.00                |
| 1.5      | 100%      | 1.3            | 2.30                |
| 2.0      | 100%      | 1.0            | 2.00                |
| 2.5      | 100%      | 1.0            | 2.00                |
| 4.0      | 0%        | 0.0            | 1.00                |

**A sharp cliff between successor_capability=2.5 (100% fire rate) and 4.0
(0%).** Substrate maturity is not the binding constraint: at 4.0x the
substrate reaches `theta_capability=0.73, transfer_state=0.93,
psi_inst_stock=0.95` (more mature than at any fire event in the grid)
and yield still does not fire. The maximum advantage observed at 4.0x is
-0.09 (essentially tied), then runaway pulls it strongly negative.

The binding constraint is the runaway penalty in `theta_tech_v2`:

```
runaway_term = max(0, (capability * theta_capability / bio_bandwidth)
                       - RUNAWAY_THRESHOLD)
theta_tech_v2 *= exp(-alpha * CONVERGENCE_STRENGTH * runaway_term)
```

At successor:incumbent capability ratios above ~3x, `frontier_velocity`
scales faster than `bio_bandwidth` can keep up, exponentially suppressing
the successor's theta_tech and pulling its U_sys below the incumbent's
regardless of how mature the substrate is.

## Multi-generational implication

Successor construction creates `capability * 1.5` per generation
(`model.py:1235`). At small initial ratios this compounds favorably:
succ_cap=1.2 reaches final_inc_gen=3.0 on average (multiple successions
fire). At larger initial ratios the compounded ratio quickly exceeds the
cliff: succ_cap=2.0 fires once (Gen2 reached) then the Gen3 successor at
3.0x effective ratio doesn't fire.

The framework's economics under v2.0 defaults thus support *incremental*
multi-generational succession, not single-shot capability jumps.

## Framework substantive claim under v2.0

The formal yield logic encodes the framework's claim that succession
happens when economically justified. The empirical regime characterizes
*when* succession is economically justified:

> Under v2.0 default calibration, succession is economically sustainable
> for successor:incumbent capability ratios up to approximately 2.5x and
> economically infeasible at ratios of 4.0x and above. This is the
> runaway penalty acting as a structural ceiling on uncontrolled
> capability jumps.

This is the framework working as designed, not a bug. The formal yield
logic is correctly enforcing the substantive claim about controlled
capability progression.

## Pattern 1 refinement (post-Gate-3 finding)

The "succession sustainable up to approximately 2.5x ratio" framing
above is specifically the regime observed at alpha=1.0 (the v2.0 default
and the only alpha value tested in the Stage 2 parameter diagnostic).
Gate 3 v2.0 validation (`gate3_v20_validation.py`, 1,620 runs varying
successor_capability x alpha x rr) refined the characterization:

**The cliff is primarily an alpha effect, not a capability-ratio effect.**

Fire rates by (capability, alpha) aggregated across the four rr values
in the gate 3 grid:

| capability | alpha=0.5 | alpha=1.0 | alpha=1.5 |
|------------|-----------|-----------|-----------|
| 1.5        | 100%      | 100%      | 100%      |
| 2.0        | 100%      | 100%      | 100%      |
| 2.5        | 100%      | 100%      | ~3%       |
| 3.0        | 100%      | ~5%       | 0%        |
| 4.0        | 100%      | 0%        | 0%        |

At alpha=0.5 (weak runaway penalty), succession fires reliably at all
tested ratios up to 4.0x. At alpha=1.0 (default), the cliff sits between
2.5x and 3.0x (this is the slice the original Pattern 1 captured). At
alpha=1.5 (strong runaway penalty), the cliff sits between 2.0x and
2.5x.

Capability ratio alone does not predict succession viability. The
**(alpha, capability) joint position relative to the runaway penalty**
does. The runaway-penalty mechanism is:

```
runaway_term = max(0, (frontier_velocity / bio_bandwidth) - RUNAWAY_THRESHOLD)
theta_tech_v2 *= exp(-alpha * CONVERGENCE_STRENGTH * runaway_term)
```

Alpha enters as a multiplier on the exponential suppression. Doubling
alpha (1.0 to 2.0) squares the suppression factor at any given
runaway_term, pulling the cliff substantially inward. Halving alpha
(1.0 to 0.5) takes the square root, pushing the cliff outward.

### Horizon-dependence

Gate 3 also revealed a horizon-dependence: at N_STEPS=500 (Gate 3),
cap=4.0 fires in 33.3% of runs (driven by the alpha=0.5 cells); at
N_STEPS=300 (Stage 2 diagnostic), cap=4.0 fired in 0% of runs. Longer
simulation horizons let substrate mature enough that even 4x ratios can
satisfy the formal condition at low alpha. The full Pattern 1 cliff has
an **(alpha, capability, N_STEPS, rr)** joint characterization, not a
single (capability) characterization.

### Refined substantive claim

> Under v2.0 architecture, succession is economically sustainable when
> the (alpha, successor:incumbent capability ratio) joint position
> falls below the runaway-penalty cliff. The cliff is calibrated by the
> runaway penalty parameters and horizon length. At default alpha=1.0
> and 200-500 step horizons, the cliff sits between successor:incumbent
> ratios of 2.5x and 3.0x. Weaker runaway penalties (smaller alpha)
> push the cliff outward; stronger penalties (larger alpha) pull it
> inward.

The architectural mechanism (runaway penalty constraining jumps) holds
across all tested regimes. The specific cliff location is
operating-condition-dependent.

### Implication for the original Pattern 1 framing

The "succession sustainable up to ~2.5x" framing in the previous
section is correct for alpha=1.0 conditions. It under-reports the
viability of succession at weaker runaway penalties and over-reports
viability at stronger ones. Future references to Pattern 1 should
specify the alpha value at which the cliff is characterized, or quote
the full (alpha, capability) table above.

## Flag for future calibration work

If a future framework iteration wants succession to support larger
capability jumps (4x+), the relevant tunable parameters are:

- `RUNAWAY_THRESHOLD` (in `constants_v2_stage18.py`): raising this
  pushes the cliff outward
- `CONVERGENCE_STRENGTH` (in `constants_v2_stage18.py`): lowering this
  weakens the exponential suppression
- `alpha` (config-driven via `cfg.get('alpha', ALPHA_DEFAULT)`): lowering
  this weakens the exponential suppression
- Transition cost constants `k1`, `k2`, `beta` (v1.x.2 calibration
  carried over): lowering reduces the required advantage at all ratios

These are out of scope for Stage 2. They would be the subject of a
separate calibration prompt only if the operator decides the current
regime is too restrictive for the framework's claims.

## Implications for Gate 3 v2.0 validation

The original gate 3 prompt proposed successor_capability ∈ {2.0, 3.0,
4.0, 5.0}. Under the cliff, this grid spans the "fires" and "doesn't
fire" regimes asymmetrically (2.0 and 3.0 fire; 4.0 and 5.0 don't). The
adjusted grid for gate 3 v2.0 validation is **{1.5, 2.0, 2.5, 3.0,
4.0}**:

- 1.5, 2.0, 2.5, 3.0: in the fires regime; G3.1 validates that the
  formal condition correctly identifies these as succession-eligible
- 4.0: in the does-not-fire regime; G3.1 validates that the formal
  condition correctly identifies this as economically infeasible
- 5.0 dropped: deep in no-fire territory, not informative

Both regimes exercise the formal condition. Gate 3 G3.1 validates
correctly across both, with the asymmetry being the empirical content,
not a failure mode.

## Files in this Stage

- `simulation/model.py`: yield logic at `_step_v2`, yield_event_log on
  `GardenModel.__init__`. Production code change.
- `simulation/diagnostics/stage2_yield_smoke_test.py`: 195 lines. Initial
  mechanical smoke test (5 seeds, 100 steps, succ_cap=4.0).
- `simulation/diagnostics/stage2_yield_parameter_diagnostic.py`: 285
  lines. Pattern characterization (50 runs, 300 steps, 5 capability
  values).
- `simulation/diagnostics/stage2_yield_parameter_diagnostic_summary.md`:
  diagnostic report.
- `simulation/diagnostics/stage2_yield_implementation_notes.md`: this
  file.

v1.x.2 paths are untouched throughout.


==========================================
FILE: simulation/diagnostics/stage2_yield_parameter_diagnostic_summary.md
==========================================

# Stage 2 yield-condition parameter diagnostic

Generated: 2026-06-07T19:18:46Z

Grid: successor_capability in [1.2, 1.5, 2.0, 2.5, 4.0], seeds 0..9 (10/cell), steps=300, phi=25.0, rr=0.066.
Total runs: 50.

## Section 1: Yield-fire rate by successor capability

| succ_cap | runs | runs_with_fire | fire_rate | total_checks | total_fires | first_fire_step (mean) | final_inc_gen (mean) |
|----------|------|----------------|-----------|--------------|-------------|------------------------|-----------------------|
|  1.2     |   10 |             10 |    100.0% |         3000 |          20 |                    7.6 |                  3.00 |
|  1.5     |   10 |             10 |    100.0% |         3000 |          13 |                    6.5 |                  2.30 |
|  2.0     |   10 |             10 |    100.0% |         3000 |          10 |                   10.4 |                  2.00 |
|  2.5     |   10 |             10 |    100.0% |         3000 |          10 |                   20.6 |                  2.00 |
|  4.0     |   10 |              0 |      0.0% |         3000 |           0 |                    n/a |                  1.00 |

## Section 2: Substrate state at yield events (means)

For runs that produced at least one yield-fire event, the substrate state (theta_capability, transfer_state, psi_inst_stock) at the first such event.

| succ_cap | n_fired_runs | theta_cap (mean) | transfer_state (mean) | psi_inst (mean) | inc_u_sys (mean) | succ_u_sys (mean) | adv (mean) | cost (mean) |
|----------|--------------|------------------|-----------------------|------------------|------------------|--------------------|------------|-------------|
|  1.2     |           10 |           0.5798 |                0.7405 |           0.7374 |          26.9529 |            30.7593 |     3.8065 |      3.5948 |
|  1.5     |           10 |           0.5697 |                0.7169 |           0.7135 |          25.1621 |            29.7920 |     4.6298 |      3.6632 |
|  2.0     |           10 |           0.6005 |                0.7929 |           0.7795 |          31.3474 |            35.8469 |     4.4995 |      3.4872 |
|  2.5     |           10 |           0.6458 |                0.8781 |           0.8804 |          42.1777 |            46.2248 |     4.0471 |      3.2666 |
|  4.0     |            0 |              n/a |                   n/a |              n/a |              n/a |                n/a |        n/a |         n/a |

## Section 3: Substrate state at end of no-yield runs (means)

For runs that produced zero yield fires, the substrate state at the final yield check, plus the advantage shape.

| succ_cap | n_no_fire | theta_cap_end | transfer_state_end | psi_inst_end | min_advantage | max_advantage | cost_end |
|----------|-----------|---------------|---------------------|--------------|---------------|---------------|----------|
|  1.2     |         0 |           n/a |                 n/a |          n/a |           n/a |           n/a |      n/a |
|  1.5     |         0 |           n/a |                 n/a |          n/a |           n/a |           n/a |      n/a |
|  2.0     |         0 |           n/a |                 n/a |          n/a |           n/a |           n/a |      n/a |
|  2.5     |         0 |           n/a |                 n/a |          n/a |           n/a |           n/a |      n/a |
|  4.0     |        10 |        0.7326 |              0.9271 |       0.9477 |      -29.8442 |       -0.0918 |   3.1426 |

## Section 4: Pattern classification

Per-cap fire-rate (runs_with_fire / runs):
  succ_cap= 1.2: 100.0%
  succ_cap= 1.5: 100.0%
  succ_cap= 2.0: 100.0%
  succ_cap= 2.5: 100.0%
  succ_cap= 4.0:   0.0%

**Mixed** (yield fires at some ratios but not monotonically). Read Section 1 fire-rate column directly and discuss with operator.

## Section 5: Hard rules confirmed

- No production constants modified.
- No yield implementation adjustment beyond log enrichment.
- 39/39 legacy tests pass under the log-enriched model.
- Stage 2 formal yield logic is preserved as committed.


