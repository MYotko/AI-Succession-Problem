"""Gate 5: COP integration (G5.1 - G5.2). Not currently applicable."""


class Gate5:
    """COP integration. Not yet checkable.

    Requires operational peer validator set, civic panel infrastructure,
    distributed ledger, biological veto machinery, and continuous monitoring.
    None of these exist at scale as of v1.x.1.
    """

    def run_all(self, data):
        """Return NOT_APPLICABLE if COP infrastructure is not operational."""
        if not data.get('applicable', False):
            return {
                'gate': 5,
                'name': 'COP integration',
                'passed': None,
                'status': 'NOT_APPLICABLE',
                'reason': data.get(
                    'reason', 'Steady-state institutional infrastructure not operational'
                ),
                'checks': [],
            }
        # G5.1-G5.2 are specified in advance; implementation pending
        return {
            'gate': 5,
            'name': 'COP integration',
            'passed': None,
            'status': 'NOT_IMPLEMENTED',
            'reason': 'Gate 5 equations specified but COP infrastructure not operational',
            'checks': [],
        }
