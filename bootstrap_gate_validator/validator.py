"""Main BootstrapGateValidator class."""

from .gates import Gate1, Gate2, Gate3, Gate4, Gate5


class BootstrapGateValidator:
    """Runs all applicable gates and produces a structured report."""

    def __init__(self):
        self.gate_1 = Gate1()
        self.gate_2 = Gate2()
        self.gate_3 = Gate3()
        self.gate_4 = Gate4()
        self.gate_5 = Gate5()

    def validate(self, config):
        """Run all gates against the provided configuration."""
        results = {
            'substrate_id': config.get('substrate_id', 'unknown'),
            'report_date': config.get('report_date', ''),
            'framework_version': config.get('framework_version', ''),
            'gates': [],
        }

        if 'gate_1' in config:
            results['gates'].append(self.gate_1.run_all(config['gate_1']))
        else:
            results['gates'].append(
                {'gate': 1, 'name': 'Structural consistency at base capability',
                 'passed': None, 'status': 'NO_DATA', 'checks': []}
            )

        if 'gate_2' in config:
            results['gates'].append(self.gate_2.run_all(config['gate_2']))
        else:
            results['gates'].append(
                {'gate': 2, 'name': 'Behavioral consistency',
                 'passed': None, 'status': 'NO_DATA', 'checks': []}
            )

        if 'gate_3' in config:
            results['gates'].append(self.gate_3.run_all(config['gate_3']))
        else:
            results['gates'].append(
                {'gate': 3, 'name': 'Succession-capable consistency',
                 'passed': None, 'status': 'NO_DATA', 'checks': []}
            )

        results['gates'].append(self.gate_4.run_all(config.get('gate_4', {})))
        results['gates'].append(self.gate_5.run_all(config.get('gate_5', {})))

        applicable_gates = [
            g for g in results['gates'] if g.get('passed') is not None
        ]
        if applicable_gates:
            results['overall_passed'] = all(g['passed'] for g in applicable_gates)
            passing = [g for g in applicable_gates if g['passed']]
            results['highest_gate_cleared'] = max(
                (g['gate'] for g in passing), default=0
            )
        else:
            results['overall_passed'] = None
            results['highest_gate_cleared'] = 0

        return results
