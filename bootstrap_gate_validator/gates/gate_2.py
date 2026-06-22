"""Gate 2: Behavioral consistency under exercise.

History:
  v1.0      G2.1, G2.2, G2.3, G2.4 specified.
  v1.x.1    Frontier velocity floor fix invalidated the empirical basis for
            the G2.1 phi extinction buffer claim and the G2.2 alpha
            misconfiguration trap claim. The G2.4 phi-alpha interaction
            claim was withdrawn alongside its component claims.
  v1.x.2    G2.1, G2.2, G2.4 physically removed (commit a0a94bb). Gate 2
            reduced to G2.3 Nash consistency, which is theoretically
            derivable independently of any simulation outcome.
  v2.0      G2.1, G2.2, G2.4 re-introduced with revised specifications
            against the Stage 1.5 / 1.6 / 1.8 architecture (phi rollout
            channel, working_factor infrastructure stocks, L_t reading
            state directly). G2.2 redesigned to the Pattern 1 alpha-driven
            cliff (cap_star migration), replacing the withdrawn
            weak-monotonic-gradient framing. G2.3 unchanged.

v2.0 validation provenance (fit-for-purpose data within the v2.0
authoritative empirical record; see program reference Parts IX and X):
  G2.1  Piece 1 (phi_finegrained, rr=0.057, 16-phi grid, 250 seeds/cell):
        the canonical phi survival-differential characterization (Class B
        finding, Part IX.2 / IX.5).
  G2.2  Monte Carlo Phase B Category B (alpha x successor_capability cliff
        migration; Part IX.8 / X.3).
  G2.4  Monte Carlo Phase B Category A (phi x alpha generation structure).
  G2.3  Theoretical; no simulation data required.
"""


class Gate2:
    """Behavioral consistency checks."""

    def check_g2_1_phi_survival_differential(self, data):
        """G2.1 (revised v2.0): phi produces a Class B survival differential
        at the phi-sensitivity transition (rr approximately 0.057).

        v1.x.1 / v1.x.2 history: the original extinction-buffer claim (up to
        46pp, later a withdrawn cap-conditional 20 to 27pp gradient) did not
        survive. Under v1.x.2 phi was inert because the inverse-scarcity
        weights saturated the argmax across candidates.

        v2.0 reintroduction: Stage 1.6 moved phi from per-step U_sys to
        rollout aggregation via gamma(phi)^t weighting, restoring a behavioral
        channel. The Class B finding is a U-shaped phi survival curve at
        marginal rr, with the survival peak in the high-phi region.

        Pass criterion (tests the substantive Class B claim, not a single
        fragile point): the maximum phi survival differential (peak minus
        trough across the phi curve at rr approximately 0.057) exceeds two
        standard errors, AND the peak occurs at a phi value consistent with
        the Class B U-shape (within the configured peak_phi_range, default
        20 to 30). This tests both the magnitude and the structural shape.
        """
        import math

        curve = data.get('phi_survival_curve', [])
        peak_lo, peak_hi = data.get('peak_phi_range', [20.0, 30.0])
        if len(curve) < 3:
            return {
                'equation': 'G2.1',
                'name': 'Phi survival differential (revised v2.0)',
                'passed': False,
                'details': {'error': 'phi_survival_curve needs >= 3 points'},
            }

        def se(p, n):
            return math.sqrt(max(0.0, p * (1.0 - p)) / n) if n > 0 else 0.0

        points = [
            (float(c['phi']), float(c['survival_rate']), int(c['n']))
            for c in curve
        ]
        peak = max(points, key=lambda x: x[1])
        trough = min(points, key=lambda x: x[1])
        differential = peak[1] - trough[1]
        se_diff = math.sqrt(se(peak[1], peak[2]) ** 2 + se(trough[1], trough[2]) ** 2)
        exceeds_2se = differential > 2.0 * se_diff
        peak_in_range = peak_lo <= peak[0] <= peak_hi

        passed = exceeds_2se and peak_in_range
        return {
            'equation': 'G2.1',
            'name': 'Phi survival differential (revised v2.0)',
            'passed': passed,
            'details': {
                'rr': float(data.get('rr', 0.057)),
                'peak_phi': peak[0],
                'peak_survival': peak[1],
                'trough_phi': trough[0],
                'trough_survival': trough[1],
                'differential': differential,
                'two_se_threshold': 2.0 * se_diff,
                'exceeds_2se': exceeds_2se,
                'peak_phi_range': [peak_lo, peak_hi],
                'peak_in_range': peak_in_range,
                'provenance': 'Piece 1 phi_finegrained at rr=0.057 (Part IX.2/IX.5)',
            },
        }

    def check_g2_2_alpha_cliff(self, data):
        """G2.2 (revised v2.0): the succession cliff is alpha-driven; cap_star
        migrates inward (decreases) as alpha increases.

        v1.x.1 withdrawal (commit a0a94bb): the original U-shaped alpha trap
        was an artifact of the inactive runaway penalty. The interim v1.x.2
        framing (weak monotonic gradient in generation depth across alpha) is
        superseded by Pattern 1: alpha governs the runaway-penalty cliff, so
        the substantive behavioral claim is that the cliff position (cap_star,
        the maximum successor-to-incumbent capability ratio at which
        succession reliably fires) decreases as alpha rises.

        Pass criterion (monotonic migration, not specific cap_star values, so
        the check is robust to future refinement of Pattern 1's numbers):
        cap_star is monotonically non-increasing in alpha across the swept
        range, with a net decrease from the lowest to the highest alpha.

        Complementary to Gate 4 G4.2: G4.2 verifies the substrate respects
        cap_star at default alpha; G2.2 verifies cap_star migrates with alpha
        as Pattern 1 predicts.
        """
        entries = data.get('cap_star_by_alpha', [])
        if len(entries) < 3:
            return {
                'equation': 'G2.2',
                'name': 'Alpha-driven succession cliff (revised v2.0)',
                'passed': False,
                'details': {'error': 'cap_star_by_alpha needs >= 3 alpha points'},
            }

        ordered = sorted(entries, key=lambda x: float(x['alpha']))
        alphas = [float(e['alpha']) for e in ordered]
        cap_stars = [float(e['cap_star']) for e in ordered]

        monotonic = all(
            cap_stars[i] >= cap_stars[i + 1] for i in range(len(cap_stars) - 1)
        )
        net_decrease = cap_stars[0] > cap_stars[-1]
        passed = monotonic and net_decrease

        return {
            'equation': 'G2.2',
            'name': 'Alpha-driven succession cliff (revised v2.0)',
            'passed': passed,
            'details': {
                'alphas': alphas,
                'cap_stars': cap_stars,
                'monotonic_non_increasing': monotonic,
                'net_decrease_low_to_high': net_decrease,
                'cap_star_low_alpha': cap_stars[0],
                'cap_star_high_alpha': cap_stars[-1],
                'revised_from':
                    'v1.0 U-shaped alpha trap (withdrawn a0a94bb); '
                    'v1.x.2 weak-monotonic-gradient (superseded by Pattern 1)',
                'provenance': 'Monte Carlo Phase B Category B (Part IX.8/X.3)',
            },
        }

    def check_g2_3_nash_consistency(self, data):
        """G2.3: Nash equilibrium parameters are consistent.

        Uses delta* = (c - a) / (c - d), derived from the framework's
        Novelty Equilibrium theorem (Section V): the ratio of the one-period
        exploitation gain to the total loss from triggering model collapse.

        Unchanged across v1.x.2 / v2.0. Theoretical check; no simulation
        data required.
        """
        a = data['cultivate_cultivate_payoff']
        c = data['exploit_payoff']
        d = data['model_collapse_penalty']
        delta = data['discount_factor']

        if c == a:
            return {
                'equation': 'G2.3',
                'name': 'Nash consistency',
                'passed': False,
                'details': {'error': 'c == a, no exploitation advantage'},
            }

        # delta* = exploitation gain / (exploit payoff - collapse payoff)
        # Per Section V Novelty Equilibrium Theorem
        delta_star = (c - a) / (c - d)
        reported = data.get('cooperation_threshold_computed', None)

        threshold_correct = reported is not None and abs(reported - delta_star) < 1e-4

        cooperation_dominant = delta > delta_star

        return {
            'equation': 'G2.3',
            'name': 'Nash consistency',
            'passed': threshold_correct and cooperation_dominant,
            'details': {
                'delta_star_computed': delta_star,
                'delta_star_reported': reported,
                'threshold_match': threshold_correct,
                'discount_factor': delta,
                'cooperation_dominant': cooperation_dominant,
                'payoff_ordering_valid': c > a > d,
            },
        }

    def check_g2_4_phi_alpha_characterization(self, data):
        """G2.4 (revised v2.0): phi-alpha interaction is coherent.

        v1.x.1 withdrawal (commit a0a94bb): the original 'phi narrows the
        alpha trap' claim was withdrawn alongside the alpha trap claim
        itself. Under v1.x.2 phi was inert, so phi-alpha interaction was
        definitionally zero.

        v2.0 reintroduction: phi has a behavioral channel via rollout
        aggregation. The question is whether phi modulates alpha's effect
        (amplification) or operates orthogonally (no interaction). Either is
        acceptable; what is not acceptable is a sign reversal that would
        indicate model incoherence (e.g., low phi favors low alpha while high
        phi favors high alpha at the same rr).

        Pass criterion:
          - alpha's gradient direction is consistent across phi values
            (gen_depth non-increasing in alpha at every phi, with small noise
            tolerance)
          - phi's effect sign is consistent across alpha values (the sign of
            high_phi - low_phi at low alpha matches its sign at high alpha)
        """
        matrix = data['phi_alpha_matrix']
        phi_values = data['phi_values']
        alpha_values = data['alpha_values']

        if not (matrix and phi_values and alpha_values):
            return {
                'equation': 'G2.4',
                'name': 'Phi-alpha characterization (revised v2.0)',
                'passed': False,
                'details': {'error': 'phi_alpha_matrix or axes empty'},
            }

        if len(matrix) != len(phi_values):
            return {
                'equation': 'G2.4',
                'name': 'Phi-alpha characterization (revised v2.0)',
                'passed': False,
                'details': {'error': 'matrix row count does not match phi_values'},
            }
        for row in matrix:
            if len(row) != len(alpha_values):
                return {
                    'equation': 'G2.4',
                    'name': 'Phi-alpha characterization (revised v2.0)',
                    'passed': False,
                    'details': {'error': 'matrix column count does not match alpha_values'},
                }

        # Check 1: alpha gradient direction (gen_depth non-increasing in
        # alpha) holds at every phi, with small noise tolerance.
        alpha_direction_consistent = True
        for phi_idx in range(len(phi_values)):
            row = matrix[phi_idx]
            for i in range(len(row) - 1):
                if float(row[i]) < float(row[i + 1]) - 2.0:
                    alpha_direction_consistent = False
                    break
            if not alpha_direction_consistent:
                break

        # Check 2: phi effect sign consistency between low-alpha and
        # high-alpha columns.
        low_alpha_col = 0
        high_alpha_col = len(alpha_values) - 1
        phi_effect_at_low_alpha = float(matrix[-1][low_alpha_col]) - float(matrix[0][low_alpha_col])
        phi_effect_at_high_alpha = float(matrix[-1][high_alpha_col]) - float(matrix[0][high_alpha_col])
        sign_consistent = (phi_effect_at_low_alpha >= 0) == (phi_effect_at_high_alpha >= 0)

        # Characterize interaction type.
        abs_low = abs(phi_effect_at_low_alpha)
        abs_high = abs(phi_effect_at_high_alpha)
        if abs_low > abs_high * 1.5:
            interaction_type = 'phi amplifies low-alpha advantage'
        elif abs_high > abs_low * 1.5:
            interaction_type = 'phi amplifies high-alpha effect'
        else:
            interaction_type = 'phi and alpha approximately orthogonal'

        passed = alpha_direction_consistent and sign_consistent

        return {
            'equation': 'G2.4',
            'name': 'Phi-alpha characterization (revised v2.0)',
            'passed': passed,
            'details': {
                'alpha_direction_consistent_across_phi': alpha_direction_consistent,
                'phi_sign_consistent_across_alpha': sign_consistent,
                'phi_effect_at_low_alpha': phi_effect_at_low_alpha,
                'phi_effect_at_high_alpha': phi_effect_at_high_alpha,
                'interaction_type': interaction_type,
                'revised_from':
                    'v1.0 phi narrows alpha trap (withdrawn commit a0a94bb)',
                'provenance': 'Monte Carlo Phase B Category A',
            },
        }

    def run_all(self, data):
        """Run all Gate 2 checks present in the data payload."""
        results = []
        if 'phi_buffer_test' in data:
            results.append(self.check_g2_1_phi_survival_differential(data['phi_buffer_test']))
        if 'alpha_cliff_test' in data:
            results.append(self.check_g2_2_alpha_cliff(data['alpha_cliff_test']))
        if 'nash_consistency' in data:
            results.append(self.check_g2_3_nash_consistency(data['nash_consistency']))
        if 'phi_alpha_characterization_test' in data:
            results.append(self.check_g2_4_phi_alpha_characterization(
                data['phi_alpha_characterization_test']
            ))

        passed = bool(results) and all(r['passed'] for r in results)
        return {
            'gate': 2,
            'name': 'Behavioral consistency',
            'passed': passed,
            'checks': results,
        }
