# Gate 1 diagnostic supplement (superseded)

Gate 1 now PASSES under the operator-revised criteria. The full analysis,
including the baseline allocation pattern and Stage 3 forward-looking
guidance, lives in `gate1_interior_action_report.md`.

## History of this gate

This file previously held the Reading A interpretation of the FAIL
result under the original Stage 2 pass criteria. That interpretation
diagnosed the optimizer's under-investment in `x_resilience` and
`x_institutional_capacity` as a structural property of U_sys_v2 that
would require curve revision to fix.

The operator subsequently clarified that the property the Reading A
analysis identified is not a v2 defect to repair; it is the v2 model
correctly representing the short-horizon governance pathology that phi
exists to address. Phi is fundamentally the time-horizon parameter of
the AI's planning, and the starvation of delayed-payoff categories at
phi=10 is what the Stage 3 phi sweep will test against.

The min_share threshold has been moved from a pass/fail criterion to a
baseline diagnostic. The gate now tests non-degenerate, non-corner
allocation structure (the necessary precondition for phi to have any
behavioral channel), which the v2 model satisfies cleanly:

- max_share < 0.5 in 98.6% of decision steps (threshold: 95%)
- Mean allocation entropy 0.871 (threshold: 0.70)
- Most-selected anchor 0.001 (threshold: 0.15)

Baseline starvation: 39.1% of steps have min_share < 0.02, concentrated
in `resilience` and `institutional_capacity`. This is the baseline
phi=10 short-horizon behavior. Stage 3 will measure whether phi changes
it.

See `gate1_interior_action_report.md` for the full data including per-
category step-to-step variance (baseline for Stage 3 signature (b)) and
the forward-looking guidance for Stage 3 signature design (delayed-payoff
investment, sustained commitment, anticipatory drift response).
