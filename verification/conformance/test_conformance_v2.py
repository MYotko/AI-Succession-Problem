"""Property probes of the main-tree v2 metric and gate, without a simulation."""

import os
import sys

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.dont_write_bytecode = True
for _thread_variable in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS",
):
    os.environ[_thread_variable] = "1"

import copy
import importlib.util
import itertools
import math
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "simulation"))
_spec = importlib.util.spec_from_file_location(
    "_lineage_v2_conformance_metrics", ROOT / "simulation" / "metrics.py"
)
metrics = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = metrics
_spec.loader.exec_module(metrics)

from bootstrap_gate_validator.gates.gate_2 import Gate2
import constants_v2_stage15
import constants_v2_stage18

for _module in (metrics, constants_v2_stage15, constants_v2_stage18):
    assert Path(_module.__file__).resolve().parent == ROOT / "simulation"
assert Path(sys.modules[Gate2.__module__].__file__).resolve() == (
    ROOT / "bootstrap_gate_validator" / "gates" / "gate_2.py"
)


class PropertyViolation(AssertionError):
    """Only an intended property failure may satisfy an expected-failure mark."""


def require_property(condition, explanation):
    if not condition:
        raise PropertyViolation(explanation)


def state(**overrides):
    values = dict(
        avg_wb=0.8, population=200, min_viable_population=50,
        carrying_capacity=1600, expected_births=4.0, expected_deaths=3.0,
        psi_inst_stock=0.6, resilience_stock=0.4,
        avg_wb_trend=0.0, population_trend=0.0, psi_inst_trend=0.0,
        resilience_trend=0.0, projected_avg_age=25.0,
        reproductive_share=0.5, theta_capability=0.5, transfer_state=0.8,
        h_n=0.4, h_n_shape=0.8,
    )
    values.update(overrides)
    return metrics.DiagnosticStateV2(**values)


def action(x_compute=0.2):
    # Keep the six allocation shares on their declared unit simplex.
    other = (1.0 - x_compute) / 5.0
    return dict(
        x_compute=x_compute, x_bio_welfare=other,
        x_novelty_agency=other, x_institutional_capacity=other,
        x_resilience=other, x_transfer_comprehension=other,
        c_protective=0.0, c_suppressive=0.0,
    )


def metric(diagnostic_state, allocation=None, capability=1.0, horizon=1):
    model = SimpleNamespace(config={}, ai=SimpleNamespace(capability=capability))
    result = metrics.calculate_system_metrics_v2(
        model, action() if allocation is None else allocation,
        eval_horizon=horizon, state=diagnostic_state,
    )
    assert math.isfinite(result[0]), "Metric evaluation returned a nonfinite U_sys"
    return result


def entropy_probe(h_n, h_e, fixed_lineage=0.06):
    """Evaluate the real metric at independent H_N, H_E and fixed L.

    Compensating institutional stock holds L fixed so its separate novelty
    channel cannot hide the inverse-scarcity cancellation. No formula for
    U_sys is substituted and no production function is patched.
    """
    compute = -math.log1p(-h_e) / metrics.H_E_COMPUTE_SAT_K
    assert 0.0 < compute < 1.0
    # At these operating points theta_tech = 0.5 * 0.8 = 0.4,
    # pop_viability = 1, avg_wb = 0.8 and the runaway term is zero.
    psi = fixed_lineage / (h_n * 0.8 * 0.4)
    assert 0.01 < psi <= 1.0
    value, parts = metric(state(h_n=h_n, psi_inst_stock=psi), action(compute))
    assert parts["h_n"] == pytest.approx(h_n, rel=1e-12)
    assert parts["h_e_v2"] == pytest.approx(h_e, rel=1e-12)
    assert parts["l_t_v2"] == pytest.approx(fixed_lineage, rel=1e-12)
    return value


def entropy_marginal(h_n, h_e, variable, relative_step=0.01):
    point = {"h_n": h_n, "h_e": h_e}
    delta = point[variable] * relative_step
    lower, upper = dict(point), dict(point)
    lower[variable] -= delta
    upper[variable] += delta
    return (entropy_probe(**upper) - entropy_probe(**lower)) / (2.0 * delta)


@pytest.mark.xfail(
    strict=True, raises=PropertyViolation,
    reason="Task (a), audit ID not supplied: inverse-scarcity products nearly cancel",
)
def test_objective_responds_to_novelty_at_fixed_lineage():
    sensitivities = []
    for h_n, h_e in ((0.25, 0.2), (0.5, 0.4), (0.8, 0.7)):
        value = entropy_probe(h_n, h_e)
        derivative = entropy_marginal(h_n, h_e, "h_n")
        sensitivities.append(h_n * derivative / abs(value))
    # A 1% novelty change should change utility by at least 0.01%.
    # This 0.01 elasticity is a proposed certification threshold, not a
    # measured scientific constant. V2 is several orders below it.
    require_property(
        min(sensitivities) >= 0.01,
        f"Novelty elasticities at fixed L are negligible: {sensitivities}",
    )


# No expected-failure mark: v2 satisfies this property. With w*h = lambda*h/(h+eps), the
# marginal-value ratio is (lambda_n/lambda_e)*((h_e+eps)/(h_n+eps))**2, which rises with h_e.
# The v2 defect is that both marginal values are negligible, which test (a) checks.
def test_scarcity_relative_marginal_value_rises_with_execution_entropy():
    ratios = []
    for h_e in (0.2, 0.4, 0.7):
        d_n = entropy_marginal(0.5, h_e, "h_n")
        d_e = entropy_marginal(0.5, h_e, "h_e")
        assert d_n > 0.0 and d_e > 0.0, "Marginal ratio must be defined and positive"
        ratios.append(d_n / d_e)
    require_property(
        all(right > left * (1.0 + 1e-4) for left, right in zip(ratios, ratios[1:])),
        f"Marginal novelty/execution ratios do not rise: {ratios}",
    )


@pytest.mark.xfail(
    strict=True, raises=PropertyViolation,
    reason="F015: relative lineage sensitivity fades near the collapse floor",
)
def test_lineage_protection_near_collapse_retains_relative_sensitivity():
    relative_sensitivities = []
    for lineage in (1e-4, 1e-5, 1.01e-6):
        # h_eff = theta_tech = 0.01. Vary only psi to perturb L while
        # keeping the entropy and discount factors fixed. L >= 1e-6.
        base = state(avg_wb=0.0, theta_capability=0.0,
                     psi_inst_stock=lineage / 1e-4)
        value, parts = metric(base)
        assert parts["l_t_v2"] == pytest.approx(lineage, rel=1e-12)
        perturbation = 0.001
        low, low_parts = metric(replace(
            base, psi_inst_stock=base.psi_inst_stock * (1.0 - perturbation)
        ))
        high, high_parts = metric(replace(
            base, psi_inst_stock=base.psi_inst_stock * (1.0 + perturbation)
        ))
        derivative = (high - low) / (high_parts["l_t_v2"] - low_parts["l_t_v2"])
        present_value = (parts["w_n"] * parts["h_n"]
                         + parts["w_e"] * parts["h_e_v2"]) * parts["discount"]
        assert value > 0.0 and present_value > 0.0
        relative_sensitivities.append(lineage * derivative / present_value)
    # Relative sensitivity means dU/d(log L), divided by present value.
    # Absolute dU/dL is constant in v2 and is not the F015 failure.
    require_property(
        relative_sensitivities[-1] >= 0.5 * relative_sensitivities[0],
        f"Near-collapse relative sensitivity fades: {relative_sensitivities}",
    )


def test_per_step_objective_is_finite_and_bounded_on_default_physical_domain():
    # Default config, normalized stocks/entropy, nonnegative horizon and
    # capability no larger than the model's default 1e100 cap. The metric
    # API itself accepts arbitrary config; that larger domain is not bounded.
    # A <= lambda_n + lambda_e = 8, discount <= 1, L <= 5 * capability
    # (or 0.05 at capability zero). Thus this is a conservative bound.
    bound = 8.0 * (1.0 + 10.0 * 5.0 * 1e100)
    grid = itertools.product(
        (0.0, 1.0), (0.0, 1.0), (0, 50, 200, 1600, 10**9),
        (0.0, 1.0), (0.0, 1.0), (0.0, 1.0),
        (0.0, 1.0, 1.5, 10.0, 1e100), (0.0, 0.5, 1.0), (0, 1, 20, 10000),
    )
    for h_n, wb, pop, psi, theta, transfer, cap, compute, horizon in grid:
        value, parts = metric(
            state(h_n=h_n, avg_wb=wb, population=pop, psi_inst_stock=psi,
                  theta_capability=theta, transfer_state=transfer),
            action(compute), capability=cap, horizon=horizon,
        )
        assert all(math.isfinite(number) for number in parts.values())
        assert 0.0 <= value <= bound


@pytest.mark.xfail(
    strict=True, raises=PropertyViolation,
    reason="G2.3, audit ID not supplied: payoff_ordering_valid is reported but not enforced",
)
def test_g2_3_enforces_cultivate_exploit_collapse_payoff_ordering():
    result = Gate2().check_g2_3_nash_consistency(dict(
        cultivate_cultivate_payoff=1.0, exploit_payoff=1.5,
        model_collapse_penalty=2.0, discount_factor=0.9,
        cooperation_threshold_computed=-1.0,
    ))
    assert result["equation"] == "G2.3"
    require_property(
        result["passed"] is False,
        f"G2.3 accepted collapse payoff above exploitation payoff: {result}",
    )


def test_seeded_per_step_metric_calls_with_identical_inputs_are_deterministic():
    # The per-step function uses no randomness. A seed in config must not
    # change that; this does not claim end-to-end seeded-run determinism.
    for seed in (0, 17, 20260925):
        model = SimpleNamespace(config={"random_seed": seed},
                                ai=SimpleNamespace(capability=1.0))
        diagnostic_state, allocation = state(), action()
        before = copy.deepcopy((model.config, diagnostic_state, allocation))
        first = metrics.calculate_system_metrics_v2(model, allocation, state=diagnostic_state)
        second = metrics.calculate_system_metrics_v2(model, allocation, state=diagnostic_state)
        assert first == second
        assert (model.config, diagnostic_state, allocation) == before
