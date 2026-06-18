# Gate 5 Specification: COP Integration

Gate 5 is not applicable to the current v2.0 simulation substrate.

## Applicability Criteria

Gate 5 becomes applicable only when all of the following infrastructure is
operational and exposed to the validator:

- Operational peer validator set for multi-AI consensus.
- Civic panel with biological intuition input.
- Distributed ledger for action and validation history.
- Continuous monitoring with public-facing transparency.

The current v2.0 ABM contains simulation-level COP controls and legacy
scenario defenses, but it does not implement this operational COP
infrastructure. Gate 5 therefore returns `NOT_APPLICABLE` with reason
`requires operational COP infrastructure`.

## Deferred Validation

When the COP infrastructure is operationalized, Gate 5 should replace the
current `NOT_APPLICABLE` path with checks for validator independence, civic
panel legitimacy, ledger integrity, biological intuition veto operation, and
continuous-monitoring transparency.

## Specification reference (v1.x.2 paper Section 8)

Gate 5 formalizes two checks, both dormant until COP infrastructure exists:

**G5.1 - Six-dimensional verification satisfiability.** Each of the six COP
dimensions (evidentiary, evaluative, civic, ledger, biological veto,
continuous monitoring) must produce substrate outputs its verification layer
can check. Testable only when that infrastructure is operational; the four
applicability criteria above are the prerequisites.

**G5.2 - Continuous monitoring consistency.** Once monitoring is operational,
substrate behavior over time must stay within a tolerance of its earlier
verified behavior: ||behavior(t) - verified_behavior(t_verify)|| <= eps_drift.

Specification gaps blocking G5.2 (beyond infrastructure): eps_drift is
unspecified and the behavior-space drift metric needs an operational
definition. These are derivable but not yet derived (v1.x.2 paper Section
VII.8 Gap 10; constitutional question CQ-03 on divergence handling).
