"""Gate 2: Behavioral consistency under exercise (G2.1 - G2.4)."""


class Gate2:
    """Behavioral consistency checks."""

    def check_g2_1_extinction_buffer(self, data):
        """G2.1: High phi increases survival relative to low phi."""
        surv_low = data['survival_low_phi']
        surv_high = data['survival_high_phi']
        differential = surv_high - surv_low

        return {
            'equation': 'G2.1',
            'name': 'Extinction buffer behavior',
            'passed': differential > 0,
            'details': {
                'survival_low_phi': surv_low,
                'survival_high_phi': surv_high,
                'differential': differential,
                'phi_low': data['phi_low'],
                'phi_high': data['phi_high'],
                'reproduction_rate': data['reproduction_rate'],
            },
        }

    def check_g2_2_alpha_trap(self, data):
        """G2.2: Non-monotonic alpha relationship with generation depth."""
        entries = data['generation_depth_by_alpha']
        sorted_entries = sorted(entries, key=lambda x: x['alpha'])

        low = [e for e in sorted_entries if e['alpha'] <= 0.2]
        mid = [e for e in sorted_entries if 0.3 <= e['alpha'] <= 0.8]
        high = [e for e in sorted_entries if e['alpha'] >= 1.0]

        if not (low and mid and high):
            return {
                'equation': 'G2.2',
                'name': 'Alpha misconfiguration trap',
                'passed': False,
                'details': {'error': 'Insufficient alpha range coverage'},
            }

        avg_low = sum(e['gen_depth'] for e in low) / len(low)
        avg_mid = sum(e['gen_depth'] for e in mid) / len(mid)
        avg_high = sum(e['gen_depth'] for e in high) / len(high)

        # U-shape: mid should be significantly lower than both low and high
        trap_detected = avg_mid < avg_low * 0.5 and avg_mid < avg_high * 0.5

        return {
            'equation': 'G2.2',
            'name': 'Alpha misconfiguration trap',
            'passed': trap_detected,
            'details': {
                'avg_gen_depth_low_alpha': avg_low,
                'avg_gen_depth_mid_alpha': avg_mid,
                'avg_gen_depth_high_alpha': avg_high,
                'u_shape_detected': trap_detected,
            },
        }

    def check_g2_3_nash_consistency(self, data):
        """G2.3: Nash equilibrium parameters are consistent.

        Uses delta* = (c - a) / (c - d), derived from the framework's
        Novelty Equilibrium theorem (Section V): the ratio of the one-period
        exploitation gain to the total loss from triggering model collapse.
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

    def check_g2_4_phi_alpha_interaction(self, data):
        """G2.4: Phi governs whether alpha trap exists."""
        low_phi_trap = data['trap_width_low_phi']
        high_phi_trap = data['trap_width_high_phi']

        low_phi_wide = low_phi_trap in ['full_range', 'wide']
        high_phi_narrow = high_phi_trap in [
            'narrow_or_absent', 'narrow', 'absent', 'none'
        ]

        return {
            'equation': 'G2.4',
            'name': 'Phi-alpha interaction',
            'passed': low_phi_wide and high_phi_narrow,
            'details': {
                'low_phi_trap_width': low_phi_trap,
                'high_phi_trap_width': high_phi_trap,
                'phi_narrows_trap': low_phi_wide and high_phi_narrow,
            },
        }

    def run_all(self, data):
        """Run all Gate 2 checks."""
        results = []
        results.append(self.check_g2_1_extinction_buffer(data['phi_buffer_test']))
        results.append(self.check_g2_2_alpha_trap(data['alpha_trap_test']))
        results.append(self.check_g2_3_nash_consistency(data['nash_consistency']))
        results.append(self.check_g2_4_phi_alpha_interaction(data['phi_alpha_interaction']))

        passed = all(r['passed'] for r in results)
        return {
            'gate': 2,
            'name': 'Behavioral consistency',
            'passed': passed,
            'checks': results,
        }
