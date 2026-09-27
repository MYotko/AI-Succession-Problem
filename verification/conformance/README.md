# V3 certification probes against the current v2 instrument

These six tests import `simulation/metrics.py`, its constants, and the bootstrap
gate modules directly from this working tree. They never instantiate a
`GardenModel`, run an agent step, optimize a policy, launch workers, or run a
simulation. The source snapshot is
`e5716dfd6caffdb9f06eebee37605030334a8838` on `main`.

The result is **3 passed and 3 expected failures**, and pytest exits with status 0.
The first run reported 2 passed, 3 expected failures and 1 unexpected strict pass:
property (b) already holds in v2, so its predicted-failure mark was wrong. On review the
mark was removed, with a comment in the test giving the reason. With w*h = lambda*h/(h+eps),
the marginal-value ratio rises with h_e; the v2 defect is that both marginal values are
negligible, which test (a) checks. No scientific assertion was weakened.

## Run

From the repository root, in PowerShell, with the existing Python environment
that provides NumPy and pytest:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
$env:OMP_NUM_THREADS = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
python -B -m pytest -p no:cacheprovider --assert=plain verification/conformance/test_conformance_v2.py -q -rXxf
```

Use this exact test path. The module also sets `sys.dont_write_bytecode` before
loading instrument code and sets numerical thread environment variables before
NumPy initializes. No pytest cache, assertion-rewrite bytecode, or simulation
output is produced. Thread settings are configured limits, not a verified
operating-system CPU reservation. Imports are checked against paths in the main
working tree rather than another worktree or installed package. No existing
source file is modified, and no commits are created.

## Properties and current evidence

| Property | Test | Current result and interpretation |
| --- | --- | --- |
| (a) Novelty responsiveness | `test_objective_responds_to_novelty_at_fixed_lineage` | XFAIL. Direct novelty elasticities are about 2.50e-6, 1.25e-6, and 7.81e-7, below the proposed 0.01 materiality threshold. |
| (b) Rising relative scarcity value | `test_scarcity_relative_marginal_value_rises_with_execution_entropy` | PASS. Marginal novelty/execution ratios rise from 0.266668 to 1.066668 to 3.266663, as the formula implies. The property holds in v2; the defect is the size of the marginals, test (a). |
| (c) Lineage protection near collapse | `test_lineage_protection_near_collapse_retains_relative_sensitivity` | XFAIL, audit F015. Relative lineage sensitivities fall from 0.00101005 to 0.000101005 to 0.0000102015. |
| (d) Finiteness and boundedness | `test_per_step_objective_is_finite_and_bounded_on_default_physical_domain` | PASS. Checks 9,600 boundary combinations against a conservative analytic bound for the default physical domain. |
| (e) Payoff ordering | `test_g2_3_enforces_cultivate_exploit_collapse_payoff_ordering` | XFAIL, G2.3. The gate accepts a=1, c=1.5, d=2, discount=0.9 and reported threshold=-1 even though its ordering flag is false. |
| (f) Determinism | `test_seeded_per_step_metric_calls_with_identical_inputs_are_deterministic` | PASS. Repeated full metric tuples are identical for each of three seed configurations, and inputs remain unchanged. This is per-step purity, not a certification of whole-run determinism. |

The three remaining expected-failure marks use `strict=True` and `raises=PropertyViolation`.
Only a failed scientific property assertion raises that custom exception.
Import errors, fixture defects, nonfinite probe results, and ordinary assertion
failures cannot silently satisfy an expected-failure mark. Remove a mark when
the corresponding defect is fixed and the property is ratified. F015 is the
only audit finding ID supplied in the task. The other reasons explicitly say
that no audit ID was supplied; G2.3 is the gate ID.

## What the sensitivity tests measure

Write the current formula as

```text
A = lambda_n * h_n / (h_n + epsilon) + lambda_e * h_e / (h_e + epsilon)
U = A * (D + K * L)
D = exp(-rho * horizon)
K = LAMBDA_LINEAGE_COUPLING
```

Tests call the real `calculate_system_metrics_v2` function. No replacement
objective, patched constants, mocked output, or simulation rollout is used.

For (a) and (b), L is held at 0.06 by compensating institutional stock when
varying novelty. The test checks the returned L on every call. Execution
entropy is varied through the inverse of its actual saturation curve, with all
six allocation shares still summing to one. Representative novelty/execution
pairs are (0.25, 0.2), (0.5, 0.4), and (0.8, 0.7). Central differences use a 1%
relative input step, safely away from floors and large enough to resolve the
small residual slopes in double precision.

This isolates the direct entropy channel. An uncompensated novelty change
also changes L and can produce a substantial total derivative in healthy v2
states. Claiming that every total novelty derivative vanishes would be false.
Property (a) measures `h_n * (partial U / partial h_n) / abs(U)`. The threshold
0.01 is a proposed certification requirement, not an empirically measured
constant; it needs ratification for v3.

For (b), at fixed L and positive epsilon the actual marginal ratio is

```text
(partial U / partial h_n) / (partial U / partial h_e)
    = (lambda_n / lambda_e) * ((h_e + epsilon) / (h_n + epsilon))**2
```

It rises with h_e even though both marginal values are negligible. At h_n=0.5,
the numerical novelty marginal is about 3.1804e-5, while the execution marginal
falls from 1.1926e-4 to 9.7359e-6. Cancellation supports the materiality failure
in (a); it does not imply a failure of the ratio monotonicity in (b). A
requirement that marginal values also be economically material would be a
different assertion and has not been inserted into (b).

For (c), relative sensitivity means
`L * (partial U / partial L) / present_value`, the response to a fractional
lineage change compared with `A * D`. This equals `K * L / D` in v2 and tends
toward zero. Absolute `partial U / partial L`, divided by present value, is
instead `K / D`, about 10.1005 here, and does not vanish. The distinction is
necessary to interpret F015 honestly.

The production factor floors impose L >= 1e-6, so the test approaches that
accessible floor at 1e-4, 1e-5, and 1.01e-6. It does not fabricate states with
L below the floor. A 0.1% institutional-stock perturbation changes L while
keeping entropy fixed. The proposed protection criterion retains at least
half the initial relative sensitivity over this approach. That threshold also
needs v3 ratification. If F015 was intended to mean the absolute derivative,
its supplied expected-failure claim requires revision.

## Bounded-domain limits

The domain for (d) is the default configuration, normalized novelty, well-being
and infrastructure stocks in [0,1], nonnegative population, horizon >= 0, and
capability in [0,1e100]. These ranges come from spectral entropy clipping in
`metrics.calculate_h_n`, agent well-being clipping, stock clipping in
`working_factor.apply_delta_state`, and the default capability cap in
`model.py`. The horizon is nonnegative by the rollout definition.

With positive default epsilon and default lambdas, A <= 8; D <= 1;
h_eff <= 5; psi_inst <= 1; and theta_tech <= max(0.01, capability). Therefore
`U <= 8 * (1 + 10 * 5 * 1e100)`. The grid checks endpoints, population scaling
thresholds, zero and extreme capability, allocation endpoints, and discount
underflow. The bound follows from the formula; a finite grid alone is not a
proof for every real input.

The metric API does not validate a universally bounded configuration domain.
Arbitrary overrides such as epsilon=-h_n or unrestricted negative alpha can
make it singular or cause exponential overflow. This test does not certify
such configurations. Defining and enforcing the public v3 domain remains a
separate instrument change, outside this task's write authorization.
