"""B2 scientific and artifact tests, with small development instances only."""
from copy import deepcopy
import math
import numpy as np
import pytest
from v3.artifacts import seal, digest, code_identity, stable_job
from v3.context import Context, reproductive_support
from v3.engine import advance
from v3.offline_estimator import simulate, estimate, _plain_mean, reduced_reference_validation, settings_for
from v3.policies import execution_policy_class
from v3.continuation import fit_transitions
from v3.calibration import run_seed, freeze, validate_calibration
from v3.production_tables import write_tables, ProductionTables, row_key
from v3.study import table_jobs, rerun_jobs, calibration_jobs, scoring_contexts, table_design

SMALL = {"groups": 6, "runs_per_group": 2, "particles": 4, "burn": 4, "measure": 8}


def test_independent_environment_and_demographic_marginals():
    ctx = Context.build({"n_agents": 20})
    original = ctx.population(1, np.random.default_rng(1))
    original.ages[:] = 20
    original.welfare[:] = 700
    state = original.repeat(512)
    stats = advance(state, np.full((512, 6), 1 / 6), np.random.default_rng(19), .08, 1600, ctx.protocol, independent=True)
    expected_births = 20 * .08 * (1 - 20 / 1600)
    mortality = .002 + .05 * (1 - .719) + .21**4
    assert abs(stats["births"].mean() - expected_births) < .3
    assert abs(stats["deaths"].mean() - 20 * mortality) < .15
    assert stats["births"].var() > .5
    assert len(np.unique(state.stocks, axis=0)) > 3
    # FV clones receive independent future environmental draws.
    cloned = state.copy_rows(np.zeros(32, int))
    advance(cloned, np.full((32, 6), 1 / 6), np.random.default_rng(20), .08, 1600, ctx.protocol, independent=True)
    assert np.unique(cloned.window[:, 0, 0, 0]).size > 20


def test_reproductive_support_matches_maximum_welfare_path():
    ctx = Context.build({"n_agents": 200})
    state = ctx.population(5, np.random.default_rng(16))
    rng = np.random.default_rng(95)
    state.ages[:] = rng.integers(0, 100, state.ages.shape)
    state.welfare[:] = rng.integers(0, 1001, state.welfare.shape)
    # Check individual states as one-agent rows, including sterile low welfare.
    state.ages = state.ages.reshape(-1, 1)
    state.welfare = state.welfare.reshape(-1, 1)
    w = state.welfare.astype(int).copy()
    possible = np.zeros_like(w, bool)
    for t in range(1, 50):
        a = state.ages + t
        w = np.clip(w + 50 - a, 0, 1000)
        possible |= (a > 18) & (a < 50) & (w >= 500)
    np.testing.assert_array_equal(reproductive_support(state), possible.any(axis=1))


def test_plain_conditions_at_each_measurement_time():
    assert _plain_mean(np.array([[1., 9.], [2., 0.]]), np.array([[True, True], [True, False]])) == 3.5
    assert _plain_mean(np.ones((2, 2)), np.zeros((2, 2), bool)) is None


def test_reduced_plain_and_fv_against_perron():
    report = reduced_reference_validation()
    assert report["validated"] and not report["full_scale_bias_certified"]
    assert report["plain_survivors"] >= 4096
    assert max(abs(r["FV_flow"]["mean"] / r["exact_flow"] - 1) for r in report["FV"]) < .0049


@pytest.mark.parametrize("route", ["plain", "fv", "auto"])
def test_full_state_estimator_status_counts_and_unconditional_continuation(route):
    result = estimate({"kernel": {"n_agents": 20, "carrying_capacity": 100}, "settings": SMALL, "route": route}, 117)
    assert result["independent_environment"] and result["continuation_uses_pre_resampling_transitions"]
    assert len(result["plain_survivor_counts"]) == 12
    row = result["rows"][0]
    assert row["status"] in ("estimated", "not_estimable")
    assert not row["zeta"]["binding_rejection"]
    assert row["LS"] is None and row["LS_truncated"] >= 0
    if row["continuation"]:
        assert not row["continuation"]["uniform_residual_certified"]


def test_fv_all_killed_is_flagged_without_restart(monkeypatch):
    monkeypatch.setattr("v3.offline_estimator.reproductive_support", lambda state: np.zeros(len(state.ages), bool))
    result = estimate({"kernel": {"n_agents": 4}, "settings": SMALL, "route": "fv"}, 18)
    assert len(result["ensemble_collapses"]) == 6
    assert result["rows"][0]["status"] == "not_estimable"
    assert result["rows"][0]["lambda_f"] is None
    assert estimate({"route": "we"}, 1)["status"] == "not_estimable"


def test_tabular_fit_matches_exact_post_action_resolvent_with_holdout():
    before, after, rewards, dead = [], [], [], []
    for group in range(6):
        for source, destinations in ((0, [0] * 6 + [1] * 2 + [2] * 2), (1, [0] + [1] * 7 + [2] * 2)):
            for destination in destinations:
                before.append([source, 0, 0, 0, 0, 0])
                after.append([destination, 0, 0, 0, 0, 0])
                rewards.append((2., 4., -10.)[destination])
                dead.append(destination == 2)
    result = fit_transitions(np.array([before]), np.array([after]), np.array([rewards]), np.array([dead]), np.repeat(np.arange(6), 20), -10, 4)
    q = np.array([[.6, .2], [.1, .7]])
    beta = math.exp(-.01)
    immediate = q @ [2., 4.] + .2 * -10
    exact = np.linalg.solve(np.eye(2) - beta * q, (1 - beta) * immediate + beta * .2 * -10)
    assert result["heldout_coverage"] == 1
    np.testing.assert_allclose([e["value"] for e in result["entries"]], exact, atol=1e-6)
    assert result["bellman_residual_empirical"] < 1e-8


def test_calibration_freeze_load_and_registered_refusal(tmp_path):
    records = [run_seed({"steps": 8}, i, "validation") for i in (1821, 8149)]
    path = tmp_path / "calibration.json"
    document = freeze(records, path)
    assert validate_calibration(document)["fixture"]
    assert document["payload"]["values"]["sigma_squared"] == pytest.approx(.1 * document["payload"]["values"]["V_ref_total"] / 10)
    ctx = Context.build({}, document)
    assert ctx.calibration_hash == document["sha256"]
    with pytest.raises(ValueError, match="fixture"):
        validate_calibration(document, registered=True)
    with pytest.raises(ValueError, match="50 by 500"):
        freeze(records, registered=True)
    with pytest.raises(ValueError):
        run_seed({"steps": 5}, 8, "v3_calibration")
    changed = deepcopy(records)
    changed[0]["sample_sum"][0] += .01
    with pytest.raises(RuntimeError, match="frozen"):
        freeze(changed, path)


def example_row():
    rule = execution_policy_class()[0]
    return {"rule_id": rule.rule_id, "rule_hash": digest(rule.__dict__), "kernel_hash": "kernel", "calibration_hash": "cal",
            "scoring": {"alpha": 1., "capability": 1., "kappa": 8.}, "status": "estimated",
            "lambda_f": {"mean": 2.}, "flow_range": 20., "lambda_b": 1., "LS": 5.,
            "continuation": {"entries": [{"bin": [0] * 6, "value": 3., "error": 15.}]}}


def test_tables_roundtrip_context_missing_bin_and_tamper(tmp_path):
    row = example_row()
    manifest = {"required_row_keys": [row_key(row)], "calibration_hash": "cal", "tag": "pilot"}
    document = write_tables(tmp_path / "tables.json", [row], manifest, fixture=True)
    loader = ProductionTables(document, calibration_hash="cal")
    args = {"kernel_hash": "kernel", "capability": 1., "alpha": 1., "weights": (5, 3, 8)}
    assert loader.lookup(execution_policy_class()[:1], [[0] * 6], **args).continuation[0] == 3
    with pytest.raises(KeyError, match="bin"):
        loader.lookup(execution_policy_class()[:1], [[1] * 6], **args)
    with pytest.raises(KeyError, match="context"):
        loader.lookup(execution_policy_class()[:1], [[0] * 6], **{**args, "capability": 2.})
    with pytest.raises(KeyError, match="context"):
        loader.lookup(execution_policy_class()[:1], [[0] * 6], initial_population=1600, **args)
    with pytest.raises(RuntimeError, match="fixture"):
        ProductionTables(document, calibration_hash="cal", registered=True)
    changed = deepcopy(document)
    changed["payload"]["rows"][row_key(row)]["payload"]["lambda_f"]["mean"] = 6
    changed = seal(changed["payload"])
    with pytest.raises(ValueError, match="hash"):
        ProductionTables(changed, calibration_hash="cal")
    stale = deepcopy(document["payload"])
    stale["code_hash"] = "old"
    with pytest.raises(ValueError, match="stale"):
        ProductionTables(seal(stale), calibration_hash="cal")
    rational, binary_product = deepcopy(row), deepcopy(row)
    rational["scoring"]["capability"] = 1.8
    binary_product["scoring"]["capability"] = 1.2 * 1.5
    assert row_key(rational) == row_key(binary_product)
    binary_product["scoring"]["capability"] = 1.80001
    assert row_key(rational) != row_key(binary_product)


def test_frozen_full_grids_sensitivity_subset_and_disjoint_seeds():
    reruns = rerun_jobs("calibration.json", "tables.json")
    assert len(reruns) == 24900
    assert len({j["seed"] for j in reruns}) == 24900
    assert len(scoring_contexts()) == 435
    tables = table_jobs()
    assert len(tables) == 325 + 18
    subset = {(j["config"]["rule_id"], j["config"]["kernel"]["reproduction_rate"]) for j in tables if j["config"]["setting_name"] != "primary"}
    assert len(subset) == 9
    calibration = calibration_jobs()
    assert len(calibration) == 50 and all(j["config"]["steps"] == 500 for j in calibration)
    assert not ({j["seed"] for j in calibration} & {j["seed"] for j in reruns})
    assert min(j["seed"] for j in reruns) > 2**32
    assert table_design()["sensitivity_jobs"] == 18


# Artifacts stay inside the authorized tree even with default pytest options.
from test_v3_paths import tmp_path
