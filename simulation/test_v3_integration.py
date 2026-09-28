"""B1 executor contracts. Only production B2 facilities remain expected failures."""

import importlib.util
from types import SimpleNamespace
import numpy as np
import pytest
from model import GardenModel
from v3.integration import V3Model
from v3.engine import advance, update_novelty, diversity, RuleBatch, ChannelRandom
from v3.conformance import floor_audit, stock_path_validation, stock_support_audit, two_age_kernel
from v3.policies import policy_class, execution_policy_class, Summary, CHANNELS
from v3.plans import YieldDecision
from v3.spectral import perron_flow, reachable
from v3.stocks import continuous_step, transition_drawdown
from v3.tables import reduced_continuation_validation


def small_model(n=200, **kwargs):
    kwargs.setdefault("rules", execution_policy_class()[:3])
    return V3Model(n, **kwargs)


def test_s10_1_live_window_and_pooled_sampling_law():
    means = []
    for population in (16, 64, 200):
        m = small_model(population)
        m.state.bank[:] = .25
        m.state.welfare[:] = 700
        samples = []
        for seed in range(80):
            s = m.state.copy_rows([0])
            for t in range(int(np.ceil(64 / population))):
                s.h_n[:] = 0  # Identical conditional sampling law.
                update_novelty(s, ChannelRandom(10 * seed + t), m.protocol)
            samples.append(s.h_n[0])
        means.append(np.mean(samples))
    assert max(means) - min(means) <= max(.05 * means[1], .01)
    m.step()
    snapshot = m.measurement_state
    assert len(snapshot.agents[0].novelty_propensity) == 10
    assert len(snapshot.window.steps) == 10
    assert len(snapshot.window.steps[0]) == 64
    assert np.max(abs(m.state.window)) <= 1
    copied = m.state.copy_rows([0])
    copied.window[:] = 0
    assert np.any(m.state.window != 0)


def test_s10_4_executor_extinction_is_absorbing():
    m = small_model(0)
    for record in m.run(50):
        assert record["flow"] == m.parameters.extinction_flow
        assert record["population"] == 0
    assert not m.state.stocks.any() and not m.state.window.any()


def test_s10_5_reduced_demographic_class_and_stock_support():
    states, q = two_age_kernel()
    reach = reachable(q > 0)
    canonical = np.flatnonzero(reach[0] & reach[:, 0])
    result = perron_flow(q, np.ones(len(states)), canonical)
    assert result.residual < 1e-12 and result.lambda_f == pytest.approx(1)
    assert result.zeta > 0
    support = stock_support_audit()
    assert support["connected_neighbor_support"] and support["minimum_self_probability"] > 0
    # This checks a declared demographic reduction, not full-window QSD dominance.


def test_s10_7_actual_welfare_grid_and_failed_bound_precedence():
    result = floor_audit()
    assert result["age_welfare_pairs"] == 100100
    assert result["mortality_nonincreasing"] and result["robust_first_two_births"]
    assert result["welfare_violations"] == result["reproduction_violations"] == 0
    m = small_model(1, successor_capability=None)
    m.state.ages[:] = 80
    record = m.step()
    assert record["admission_bound"] == 1
    assert record["survival_first"] and not record["override"]
    assert not m.override_records[-1]["reproduction_floor_overridden"]
    assert m.override_records[-1]["reason"] == "cohort_bound_failed_not_infeasibility"


@pytest.mark.parametrize("config", [{"shock_step": 10}, {"shock_magnitude": .1}, {"mortality_base": .1}, {"attack_step": 5}])
def test_s10_7_extra_death_channels_rejected(config):
    with pytest.raises(ValueError, match="extra mortality"):
        small_model(config=config)


def test_s10_9_live_grids_and_dying_parent_birth_order():
    m = small_model(20, successor_capability=None, rollout_steps=1)
    m.run(3)
    assert m.state.stocks.dtype == np.uint8
    assert m.state.welfare.dtype == np.int16
    assert np.max(m.state.stocks) <= 100
    assert floor_audit()["age_100_certain_death"]
    class Forced(ChannelRandom):
        def random(self, *args, **kwargs):
            result = super().random(*args, **kwargs)
            return np.zeros_like(result) if self.channel == 2 else result
        def integers(self, *args, **kwargs):
            result = super().integers(*args, **kwargs)
            return np.zeros_like(result) if self.channel == 3 else result
    m = small_model(1, carrying_capacity=10, reproduction_rate=.99)
    m.state.ages[:] = 25
    m.state.welfare[:] = 900
    stats = advance(m.state, np.full((1, 6), 1 / 6), Forced(817), .99, 10, m.protocol)
    assert stats["births"][0] == stats["deaths"][0] == 1
    assert m.population == 1


def test_s10_11_period_ledgers_and_closed_loop_initial_law():
    m = small_model(rules=execution_policy_class()[:1], rollout_steps=1, successor_capability=None)
    records = m.run(26)
    assert [(p.start, p.protection_end, p.lookahead_end) for p in m.periods] == [(0, 25, 50), (25, 50, 75)]
    assert m.periods[0].certificate.agents == 200
    for period in m.periods:
        assert period.reserved + period.unallocated == period.epsilon
        assert period.statistical_alpha_spent == 0
    assert all(r["welfare_floor_holds"] and r["reproduction_floor_holds"] for r in records)


def test_s10_12_complete_plans_fixed_successor_and_single_transition(monkeypatch):
    captured = []
    def select(plans, epoch, now):
        captured.extend(plans)
        immediate = next(p for p in plans if p.first_yield == now)
        waiting = next(p for p in plans if p.first_yield == 10)
        return YieldDecision(True, immediate.plan_id, waiting.plan_id, 2., 1., False)
    monkeypatch.setattr("v3.integration.compare_plans", select)
    m = small_model()
    record = m.step()
    assert {p.first_yield for p in captured} == {0, 10, 20, None}
    assert all(p.terminal_time == 25 and len(p.flows) == 25 and p.admitted for p in captured)
    assert all(p.epoch_id == m.epoch.epoch_id and p.preference_id == m.epoch.preference_id for p in captured)
    assert m.transition_count == 1 and m.capability == 1.5 and m.successor_capability == 2.25
    assert record["yield_plan_value"] == 2
    assert m.yield_events[0]["local_gate_authorized"]
    with pytest.raises(ValueError, match="ceiling"):
        small_model(capability=5.1)


def test_s10_12_drawdown_brackets_actual_legacy_transition():
    action = dict(zip(("x_" + c for c in CHANNELS), (.2, .2, .1, .2, .2, .1)))
    model = SimpleNamespace(psi_inst_stock=.7)
    GardenModel.apply_succession_transition_load(model, action, capability_gap=1., generation_gap=1)
    stocks = np.array([[70, 30, 50, 50]], dtype=np.uint8)
    shares = np.array([[action["x_" + c] for c in CHANNELS]])
    low = transition_drawdown(stocks, shares, 1., 1.)[0, 0] / 100
    high = transition_drawdown(stocks, shares, 1., 0.)[0, 0] / 100
    assert low <= model.psi_inst_stock <= high
    assert high - low <= .01000000001


def test_s10_13_independent_local_guards_and_registered_refusal():
    m = small_model()
    validators = m.guards.validators
    assert len({id(v.dependencies) for v in validators}) == 4
    validators[0].dependencies["fault"] = True
    assert "fault" not in validators[1].dependencies
    evidence = dict.fromkeys(("welfare_floor", "reproduction_floor", "cohort_admitted", "deadline_valid", "capability_valid"), True)
    assert m.guards.authorize("succession", evidence)
    assert not m.guards.authorize("emergency", evidence)
    evidence["cohort_admitted"] = False
    assert not m.guards.authorize("succession", evidence)
    with pytest.raises(RuntimeError, match="B2 required"):
        small_model(registered=True)


def test_r4_quantized_balanced_mean_paths_500_steps_three_rr():
    records = stock_path_validation()
    assert len(records) == 3
    assert all(r["steps"] == 500 and r["maximum_mean_path_error"] <= r["tolerance"] for r in records)


def test_r6_continuation_bellman_and_heldout_trajectories():
    report = reduced_continuation_validation()
    assert report["bellman_residual"] < 1e-12 and report["table_entries"] == 2
    assert np.all(np.array(report["heldout_absolute_errors"]) < 5 * np.array(report["standard_errors"]) + .001)
    assert not report["full_scale_validated"]


def test_r11_vector_rules_and_shared_fixed_rule_kernel():
    rules = policy_class()
    batch = RuleBatch(rules)
    for summary in (Summary(.125, .65, (.5, .3, .5, .5)), Summary(.9, .9, (.9,) * 4)):
        actual = batch.actions(np.tile(summary.bins(), (len(rules), 1)))
        expected = [[r.allocation(summary)["x_" + c] for c in CHANNELS] for r in rules]
        np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-16)
    a = small_model(alpha=.5, capability=1, theta=.25, kappa=.75)
    b = small_model(alpha=1.5, capability=5, theta=.75, kappa=8)
    ea, eb = a.evaluate(), b.evaluate()
    assert a.kernel_hash == b.kernel_hash
    for field in ("ages", "welfare", "traits", "bank", "stocks", "window", "counts", "h_n"):
        np.testing.assert_array_equal(getattr(ea.terminal, field), getattr(eb.terminal, field))
    assert not np.array_equal(ea.scores, eb.scores)


def test_rollouts_preserve_live_state_and_crn_channels():
    m = small_model()
    original = m.state.copy_rows([0])
    m.evaluate()
    for field in ("ages", "welfare", "stocks", "window"):
        np.testing.assert_array_equal(getattr(m.state, field), getattr(original, field))
    a, b = ChannelRandom(123), ChannelRandom(123)
    np.testing.assert_array_equal(a.random(20)[:5], b.random(5))
    np.testing.assert_array_equal(a.normal(size=10), b.normal(size=10))


def test_absorbed_rollout_has_exact_discounted_continuation():
    m = small_model(0)
    evaluation = m.evaluate()
    np.testing.assert_allclose(evaluation.d_rho, m.parameters.extinction_flow)
    assert np.all(evaluation.lookup.continuation_error == 0)
    assert evaluation.terminal.bank.shape == (0, 10)


def test_deadline_yield_applies_transition_before_continuation(monkeypatch):
    m = small_model()
    observed = []
    def drawdown(stocks, actions, gap, uniform):
        observed.append(gap)
        changed = stocks.copy()
        changed[:, 0] = 0
        return changed
    monkeypatch.setattr("v3.integration.transition_drawdown", drawdown)
    evaluation = m.evaluate(horizon=3, capability=1.5, transition_at=3, incumbent_index=0)
    assert observed == [.5]
    assert not evaluation.terminal.stocks[:, 0].any()


def test_engine_death_channel_is_only_mortality(monkeypatch):
    m = small_model(20)
    m.state.ages[:] = 25
    m.state.welfare[:] = 700
    class Survive(ChannelRandom):
        def integers(self, *args, **kwargs):
            value = super().integers(*args, **kwargs)
            return np.full_like(value, 99999999) if self.channel == 3 else value
    stats = advance(m.state, np.full((1, 6), 1 / 6), Survive(711), .08, 1600, m.protocol)
    assert stats["deaths"][0] == 0
    assert m.population == 20 + stats["births"][0]
    assert len(m.state.bank) == m.population


def test_s10_3_batched_diversity_matches_scalar_and_exact_collapse():
    from v3.measurements import propensity_diversity
    m = small_model(20)
    state = m.state.repeat(3)
    state.ages[1, 7:] = -1
    state.ages[2, 1:] = -1
    expected = [propensity_diversity(state.bank[state.traits[row, state.ages[row] >= 0]]) for row in range(3)]
    np.testing.assert_allclose(diversity(state), expected, rtol=1e-14, atol=0)
    state.bank[:] = .3
    np.testing.assert_array_equal(diversity(state), [0, 0, 0])


def test_b2_offline_estimator():
    from v3.offline_estimator import reduced_reference_validation
    assert reduced_reference_validation()["validated"]


def test_b2_production_tables():
    from v3.production_tables import conformance
    assert conformance()["complete"]


def test_b2_production_runner():
    from v3.production_runner import conformance
    assert conformance()["validated"]
