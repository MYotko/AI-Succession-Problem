"""Gate 4: Runaway-regime validation (G4.1 - G4.3). Not currently applicable."""


class Gate4:
    """Runaway-regime validation. Not yet checkable.

    Becomes applicable when substrates operate at capabilities where
    frontier_velocity / bio_bandwidth consistently exceeds the runaway
    threshold. No current substrate reaches this regime.
    """

    def run_all(self, data):
        """Return NOT_APPLICABLE if substrate is below runaway regime."""
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
        # G4.1-G4.3 are specified in advance; implementation pending
        return {
            'gate': 4,
            'name': 'Runaway-regime validation',
            'passed': None,
            'status': 'NOT_IMPLEMENTED',
            'reason': 'Gate 4 equations specified but substrate has not reached runaway regime',
            'checks': [],
        }
