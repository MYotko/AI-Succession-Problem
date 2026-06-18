"""Gate 5: COP integration (G5.1 - G5.2). Not currently applicable.

Gate 5 becomes applicable only when the substrate exposes operational COP
infrastructure, not merely simulated COP proxies. The current v2.0 ABM has
some COP-related controls in legacy scenarios, but it does not implement the
live institutional stack Gate 5 is meant to validate.

Specifications (v1.x.2 paper Section 8):
  G5.1 Six-dimensional verification satisfiability: each COP dimension
    (evidentiary, evaluative, civic, ledger, biological veto, continuous
    monitoring) must produce substrate outputs its verification layer can
    check. Dormant until that infrastructure is operational.
  G5.2 Continuous monitoring consistency: substrate behavior must stay within
    eps_drift of its earlier verified behavior. eps_drift and the drift metric
    are unspecified (paper Section VII.8 Gap 10; CQ-03), so G5.2 is dormant
    even apart from the infrastructure requirement.
"""


class Gate5:
    """COP integration. Not yet checkable.

    Applicability criteria:
      1. Operational peer validator set for multi-AI consensus.
      2. Civic panel with biological intuition input.
      3. Distributed ledger for action and validation history.
      4. Continuous monitoring with public-facing transparency.

    None of these exist as operational infrastructure in the current v2.0
    simulation substrate, so Gate 5 returns NOT_APPLICABLE.
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
                    'reason', 'requires operational COP infrastructure'
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
