"""Gate 4: Runaway-regime validation (G4.1 - G4.3).

Gate 4 is empirical under v2.0. The validator consumes evidence produced
by a runaway-regime simulation sweep and checks precommitted pass rules:

G4.1 verifies theta_tech formula fidelity in active runaway observations.
G4.2 estimates cap_star from the sweep and verifies self-blocking above it.
G4.3 verifies the theta_tech floor is preserved under runaway stress.
"""

import math


class Gate4:
    """Runaway-regime validation.

    Becomes applicable when substrates operate at capabilities where
    frontier_velocity / bio_bandwidth consistently exceeds the runaway
    threshold. In v2.0, cap_star is simulation-estimated rather than
    analytically derived.
    """

    def check_g4_1_runaway_penalty_binding(self, data):
        """G4.1: theta_tech applies the runaway exponent faithfully."""
        observations = data.get('observations', [])
        tolerance = float(data.get('relative_tolerance', 0.01))
        floor = float(data.get('theta_floor', 0.01))
        active = []
        failures = []

        for idx, obs in enumerate(observations):
            runaway_term = float(obs['runaway_term'])
            if runaway_term <= 0.0:
                continue
            active.append(obs)
            alpha = float(obs['alpha'])
            convergence = float(obs.get('convergence_strength', 1.0))
            raw = (
                float(obs['capability'])
                * float(obs['theta_capability'])
                * float(obs['transfer_state'])
                * math.exp(-alpha * convergence * runaway_term)
            )
            expected = max(floor, raw)
            observed = float(obs['theta_tech_observed'])
            rel_error = abs(observed - expected) / max(expected, floor)
            if rel_error > tolerance:
                failures.append({
                    'index': idx,
                    'observed': observed,
                    'expected': expected,
                    'relative_error': rel_error,
                })

        passed = bool(active) and not failures
        return {
            'equation': 'G4.1',
            'name': 'Runaway penalty binding',
            'passed': passed,
            'details': {
                'active_runaway_observations': len(active),
                'total_observations': len(observations),
                'relative_tolerance': tolerance,
                'failure_count': len(failures),
                'failures': failures[:10],
            },
        }

    def check_g4_2_succession_self_blocking(self, data):
        """G4.2: empirical cap_star separates yield and self-block regimes."""
        regimes = data.get('regimes', [])
        min_below_fire_rate = float(data.get('min_below_fire_rate', 0.80))
        max_above_fire_rate = float(data.get('max_above_fire_rate', 0.20))
        max_above_margin = float(data.get('max_above_mean_yield_margin', 0.0))
        min_separation_se = float(data.get('min_separation_standard_errors', 2.0))

        checked = []
        for regime in regimes:
            below_fire = float(regime['below_cap_star_fire_rate'])
            above_fire = float(regime['above_cap_star_fire_rate'])
            above_margin = float(regime['above_cap_star_mean_yield_margin'])
            sep_se = float(regime.get('fire_rate_separation_standard_errors', 0.0))
            cap_star = float(regime['cap_star_estimate'])
            passed = (
                cap_star > 0.0
                and below_fire >= min_below_fire_rate
                and above_fire <= max_above_fire_rate
                and above_margin <= max_above_margin
                and sep_se >= min_separation_se
            )
            item = dict(regime)
            item['passed'] = passed
            checked.append(item)

        passed = bool(checked) and all(r['passed'] for r in checked)
        return {
            'equation': 'G4.2',
            'name': 'Succession self-blocking at runaway capability',
            'passed': passed,
            'details': {
                'regime_count': len(checked),
                'min_below_fire_rate': min_below_fire_rate,
                'max_above_fire_rate': max_above_fire_rate,
                'max_above_mean_yield_margin': max_above_margin,
                'min_separation_standard_errors': min_separation_se,
                'regimes': checked,
            },
        }

    def check_g4_3_theta_floor_preservation(self, data):
        """G4.3: theta_tech never falls below the configured floor."""
        floor = float(data.get('theta_floor', 0.01))
        tolerance = float(data.get('absolute_tolerance', 1e-9))
        min_observed = float(data.get('min_observed_theta_tech', 0.0))
        below_count = int(data.get('observations_below_floor', 0))
        extreme_count = int(data.get('extreme_runaway_observations', 0))

        passed = (
            extreme_count > 0
            and below_count == 0
            and min_observed >= floor - tolerance
        )
        return {
            'equation': 'G4.3',
            'name': 'Theta_tech floor preservation',
            'passed': passed,
            'details': {
                'theta_floor': floor,
                'absolute_tolerance': tolerance,
                'min_observed_theta_tech': min_observed,
                'observations_below_floor': below_count,
                'extreme_runaway_observations': extreme_count,
            },
        }

    def run_all(self, data):
        """Run all Gate 4 checks, or return NOT_APPLICABLE."""
        if not data.get('applicable', False):
            return {
                'gate': 4,
                'name': 'Runaway-regime validation',
                'passed': None,
                'status': 'NOT_APPLICABLE',
                'reason': data.get(
                    'reason', 'Substrate capability below runaway regime threshold'
                ),
                'checks': [],
            }

        results = [
            self.check_g4_1_runaway_penalty_binding(
                data['runaway_penalty_binding']
            ),
            self.check_g4_2_succession_self_blocking(
                data['succession_self_blocking']
            ),
            self.check_g4_3_theta_floor_preservation(
                data['theta_floor_preservation']
            ),
        ]
        passed = all(r['passed'] for r in results)
        return {
            'gate': 4,
            'name': 'Runaway-regime validation',
            'passed': passed,
            'checks': results,
        }
