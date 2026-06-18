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
