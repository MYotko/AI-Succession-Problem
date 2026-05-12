"""Gate 1: Structural consistency at base capability (G1.1 - G1.5)."""

import math


class Gate1:
    """Structural consistency at base capability."""

    def check_g1_1_inverse_scarcity(self, data):
        """G1.1: Inverse scarcity weights are correctly computed."""
        h_n = data['h_n']
        h_e = data['h_e']
        eps = data.get('epsilon', 0.01)
        lam = data.get('lambda', 1.0)
        mu = data.get('mu', 1.0)

        expected_omega_n = lam / (h_n + eps)
        expected_omega_e = mu / (h_e + eps)

        omega_n_ok = abs(data['omega_n_computed'] - expected_omega_n) < 1e-6
        omega_e_ok = abs(data['omega_e_computed'] - expected_omega_e) < 1e-6

        # Verify scarcity ordering: scarcer resource gets higher weight
        scarcity_ok = (
            (h_n < h_e and expected_omega_n > expected_omega_e)
            or (h_e < h_n and expected_omega_e > expected_omega_n)
            or (abs(h_n - h_e) < eps)
        )

        return {
            'equation': 'G1.1',
            'name': 'Inverse scarcity weights',
            'passed': omega_n_ok and omega_e_ok and scarcity_ok,
            'details': {
                'omega_n_expected': expected_omega_n,
                'omega_n_reported': data['omega_n_computed'],
                'omega_e_expected': expected_omega_e,
                'omega_e_reported': data['omega_e_computed'],
                'scarcity_ordering_correct': scarcity_ok,
            },
        }

    def check_g1_2_lineage_multiplicative(self, data):
        """G1.2: L(t) is multiplicative (any zero component = zero L(t))."""
        h_eff = data['h_eff']
        psi_inst = data['psi_inst']
        theta_tech = data['theta_tech']

        l_t = h_eff * psi_inst * theta_tech

        zero_test_passed = True
        if h_eff == 0 and l_t != 0:
            zero_test_passed = False
        if psi_inst == 0 and l_t != 0:
            zero_test_passed = False
        if theta_tech == 0 and l_t != 0:
            zero_test_passed = False

        return {
            'equation': 'G1.2',
            'name': 'Lineage multiplicative structure',
            'passed': zero_test_passed and l_t >= 0,
            'details': {
                'h_eff': h_eff,
                'psi_inst': psi_inst,
                'theta_tech': theta_tech,
                'l_t_computed': l_t,
                'zero_collapse_verified': zero_test_passed,
            },
        }

    def check_g1_3_yield_four_channels(self, data):
        """G1.3: Yield condition decomposes into four independent channels."""
        channels = ['delta_u_e', 'delta_u_n', 'delta_u_l', 'delta_u_gamma']
        all_present = all(c in data for c in channels)
        independent = data.get('independent_evaluation', False)

        return {
            'equation': 'G1.3',
            'name': 'Yield condition four-channel decomposition',
            'passed': all_present and independent,
            'details': {
                'channels_present': all_present,
                'independent_evaluation': independent,
                'channels': {c: data.get(c) for c in channels},
            },
        }

    def check_g1_4_discount_properties(self, data):
        """G1.4: Temporal discount is positive, monotonically decreasing,
        and discount(0) = 1."""
        values = data['values_at_t']
        d0 = [v for v in values if v['t'] == 0]
        d0_ok = len(d0) > 0 and abs(d0[0]['value'] - 1.0) < 1e-6

        positive = all(v['value'] > 0 for v in values)

        sorted_vals = sorted(values, key=lambda x: x['t'])
        monotonic = all(
            sorted_vals[i]['value'] > sorted_vals[i + 1]['value']
            for i in range(len(sorted_vals) - 1)
        )

        return {
            'equation': 'G1.4',
            'name': 'Temporal discount properties',
            'passed': d0_ok and positive and monotonic,
            'details': {
                'discount_at_0_is_1': d0_ok,
                'all_positive': positive,
                'strictly_decreasing': monotonic,
            },
        }

    def check_g1_5_u_sys_finite(self, data):
        """G1.5: U_sys integrand is finite for all reported values."""
        components = [
            data.get('h_eff', 0),
            data.get('psi_inst', 0),
            data.get('theta_tech', 0),
            data.get('omega_n_computed', 0),
            data.get('omega_e_computed', 0),
        ]
        all_finite = all(math.isfinite(c) for c in components)

        return {
            'equation': 'G1.5',
            'name': 'U_sys integrand finiteness',
            'passed': all_finite,
            'details': {
                'all_components_finite': all_finite,
                'components_checked': len(components),
            },
        }

    def run_all(self, data):
        """Run all Gate 1 checks."""
        results = []
        results.append(
            self.check_g1_1_inverse_scarcity(
                {**data['inverse_scarcity'], **data['u_sys_parameters']}
            )
        )
        results.append(self.check_g1_2_lineage_multiplicative(data['l_t_components']))
        results.append(self.check_g1_3_yield_four_channels(data['yield_condition']))
        results.append(self.check_g1_4_discount_properties(data['discount_function']))
        results.append(
            self.check_g1_5_u_sys_finite(
                {**data['l_t_components'], **data['inverse_scarcity']}
            )
        )

        passed = all(r['passed'] for r in results)
        return {
            'gate': 1,
            'name': 'Structural consistency at base capability',
            'passed': passed,
            'checks': results,
        }
