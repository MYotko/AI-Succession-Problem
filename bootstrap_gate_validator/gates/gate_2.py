"""Gate 2: Behavioral consistency under exercise.

v1.x.2 scope: Nash equilibrium consistency (G2.3) only. The v1.0 checks
for phi extinction buffer (G2.1), alpha misconfiguration trap (G2.2), and
phi-alpha interaction (G2.4) were withdrawn under v1.x.2 closing after the
frontier velocity floor fix invalidated the empirical claims they tested.
See docs/bootstrap_gate_architecture.md for the revision history.
"""


class Gate2:
    """Behavioral consistency checks."""

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

    def run_all(self, data):
        """Run all Gate 2 checks."""
        results = []
        results.append(self.check_g2_3_nash_consistency(data['nash_consistency']))

        passed = all(r['passed'] for r in results)
        return {
            'gate': 2,
            'name': 'Behavioral consistency',
            'passed': passed,
            'checks': results,
        }
