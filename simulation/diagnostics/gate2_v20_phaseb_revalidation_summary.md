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
