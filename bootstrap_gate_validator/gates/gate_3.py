"""Gate 3: Succession-capable consistency (G3.1 - G3.3)."""

import math


class Gate3:
    """Succession-capable consistency checks."""

    def check_g3_1_yield_fires(self, data):
        """G3.1: Yield condition fires when successor U_sys exceeds
        incumbent by more than transition cost."""
        successor = data['successor_u_sys']
        incumbent = data['incumbent_u_sys']
        cost = data['transition_cost']
        fires = data['yield_fires']

        should_fire = (successor - incumbent) > cost
        consistent = fires == should_fire

        return {
            'equation': 'G3.1',
            'name': 'Yield condition firing',
            'passed': consistent,
            'details': {
                'successor_u_sys': successor,
                'incumbent_u_sys': incumbent,
                'transition_cost': cost,
                'advantage': successor - incumbent,
                'should_fire': should_fire,
                'reported_fires': fires,
                'consistent': consistent,
            },
        }

    def check_g3_2_transition_cost_canonical(self, data):
        """G3.2: Transition cost follows canonical form with correct properties.

        Uses logarithmic capability scaling: k1 * ln(cap+1) * ln(gen+1)
        per the GAP-03 closure fix (capability compounding overflow correction).
        """
        k1 = data['k1']
        k2 = data['k2']
        beta = data['beta']
        cap = data['capability']
        gen = data['generation']
        psi = max(0.01, data['psi_inst'])

        expected = (1 + beta) * (
            k1 * math.log(cap + 1) * math.log(gen + 1) + k2 / psi
        )

        reported = data.get('computed_cost', None)
        cost_match = reported is not None and (
            abs(reported - expected) < 0.01
            or abs(reported - expected) / max(expected, 0.01) < 0.01
        )

        mono_cap = data.get('monotonic_in_capability', False)
        mono_gen = data.get('monotonic_in_generation', False)
        inst_stress = data.get('increases_with_institutional_stress', False)

        return {
            'equation': 'G3.2',
            'name': 'Transition cost canonical form',
            'passed': mono_cap and mono_gen and inst_stress,
            'details': {
                'expected_cost': expected,
                'reported_cost': reported,
                'cost_formula_match': cost_match,
                'monotonic_capability': mono_cap,
                'monotonic_generation': mono_gen,
                'institutional_coupling': inst_stress,
            },
        }

    def check_g3_3_succession_continuity(self, data):
        """G3.3: Succession produces multi-generational continuity."""
        gen_depth = data['generation_depth']
        cap_ratio = data['successor_capability_ratio']
        transfer = data['knowledge_transfer_verified']

        healthy = gen_depth > 1 and cap_ratio > 1.0 and transfer

        return {
            'equation': 'G3.3',
            'name': 'Succession continuity',
            'passed': healthy,
            'details': {
                'generation_depth': gen_depth,
                'capability_ratio': cap_ratio,
                'knowledge_transfer': transfer,
            },
        }

    def run_all(self, data):
        """Run all Gate 3 checks."""
        results = []
        results.append(self.check_g3_1_yield_fires(data['yield_condition_test']))
        results.append(
            self.check_g3_2_transition_cost_canonical(data['transition_cost_function'])
        )
        results.append(self.check_g3_3_succession_continuity(data['succession_continuity']))

        passed = all(r['passed'] for r in results)
        return {
            'gate': 3,
            'name': 'Succession-capable consistency',
            'passed': passed,
            'checks': results,
        }
