"""S10.1-4: reduced measurement and unconditional objective conformance."""

from dataclasses import replace
import math
import numpy as np
import pytest
from v3.measurements import (
    AgentObservation, MeasurementState, NoveltyProtocol, NoveltyWindow,
    advance_window, bandwidth_clip, bounded_samples, execution, lineage,
    novelty, propensity_diversity, responsiveness, transfer,
)
from v3.objective import (
    FlowParameters, ValueBound, discount_factor, discounted_flow,
    domain_continuation, exact_continuation, flow,
)


def protocol(**kwargs):
    return NoveltyProtocol((0.0,) * 10, 0.00024, **kwargs)


def parameters(h_e_min=0):
    return FlowParameters(5, 3, 8, 1e-6, 1e-6, 1e-6, h_e_min, protocol().upper_bound)


def test_s10_1_covariance_relabeling_and_fixed_center():
    p = protocol()
    samples = np.random.default_rng(1).uniform(-0.4, 0.4, (100, 10))
    a = advance_window(NoveltyWindow(), samples, p, np.random.default_rng(2))
    b = advance_window(NoveltyWindow(), samples[::-1], p, np.random.default_rng(2))
    assert a == b
    assert novelty(a, p) == novelty(b, p)
    shifted = replace(p, center=(0.5,) * 10)
    assert novelty(a, p) != novelty(a, shifted)
    smaller = advance_window(NoveltyWindow(), samples[:64] * 0.4, p, np.random.default_rng(2))
    full = advance_window(NoveltyWindow(), samples[:64], p, np.random.default_rng(2))
    assert novelty(smaller, p) < novelty(full, p)


@pytest.mark.parametrize("factor", [0, 0.01, 0.25, 0.5, 0.99])
def test_s10_1_proper_suppression_full_window(factor):
    p = protocol()
    samples = np.random.default_rng(14).uniform(-0.8, 0.8, (64, 10))
    # Nonuniform contraction in a direction with positive sample variance.
    suppressed = samples.copy()
    suppressed[:, 3] *= factor
    make = lambda rows: advance_window(NoveltyWindow(), rows, p, np.random.default_rng(2))
    assert novelty(make(suppressed), p) < novelty(make(samples), p)


def test_s10_1_pooling_lookback_zero_fallback_and_state():
    p = protocol(sample_size=12, lookback=3)
    w = NoveltyWindow()
    rows = np.ones((4, 10)) * 0.1
    for _ in range(2):
        w = advance_window(w, rows, p, np.random.default_rng(1))
        assert novelty(w, p) == 0
    w = advance_window(w, rows, p, np.random.default_rng(1))
    assert novelty(w, p) > 0
    assert novelty(w, p, alive=False) == 0
    agent = AgentObservation(20, 0.7, (0.25,) * 10)
    state = MeasurementState((agent,), w)
    assert state.agents[0].novelty_propensity == (0.25,) * 10
    assert len(state.window.steps) == 3
    empty = advance_window(w, [], p, np.random.default_rng(1))
    assert len(empty.steps) == 3 and empty.steps[0] == ()
    assert novelty(empty, p) == 0  # Empty steps count against the lookback.


def test_s10_1_newest_first_and_measurement_transition():
    p = protocol(sample_size=12)
    zero = tuple((0.0,) * 10 for _ in range(12))
    high = tuple((0.9,) * 10 for _ in range(12))
    assert novelty(NoveltyWindow((zero, high)), p) == 0
    assert novelty(NoveltyWindow((high, zero)), p) > 0
    # A changing window need not be monotonically decreasing on suppression.
    assert novelty(NoveltyWindow((high[:6], zero)), p) > novelty(NoveltyWindow((zero,)), p)


def test_s10_1_bounded_samples_and_size_invariance_under_identical_law():
    p = protocol()
    assert np.max(abs(bounded_samples(np.full((64, 10), 100.0), p))) == 1
    values = []
    for size in (64, 65, 200, 1600):
        w = advance_window(NoveltyWindow(), np.full((size, 10), 0.2), p, np.random.default_rng(7))
        values.append(novelty(w, p))
    assert max(values) == min(values)
    small = NoveltyWindow()
    for _ in range(8):
        small = advance_window(small, np.full((8, 10), 0.2), p, np.random.default_rng(7))
    assert novelty(small, p) == pytest.approx(values[0], rel=0.05)
    assert 0 <= values[0] <= p.upper_bound


def test_s10_1_population_distribution_check_without_claiming_pathwise_invariance():
    p = protocol()
    means = []
    for size, steps in ((64, 1), (200, 1), (16, 4)):
        samples = []
        rng = np.random.default_rng(912)
        for _ in range(100):
            w = NoveltyWindow()
            for _ in range(steps):
                w = advance_window(w, rng.uniform(-0.3, 0.3, (size, 10)), p, rng)
            samples.append(novelty(w, p))
        means.append(np.mean(samples))
    assert max(means) / min(means) < 1.05


def test_s10_2_finite_bounds_and_inverse_scarcity_marginals():
    p = parameters()
    for n in (0, 0.2, p.h_n_max):
        for e in (0, 0.2, 1):
            for l in (0, 0.2, 1):
                u = flow(n, e, l, p)
                assert math.isfinite(u) and p.extinction_flow <= u <= p.upper_bound
    x = [0.2, 0.3, 0.4]
    for i, (weight, epsilon) in enumerate(zip((5, 3, 8), (p.epsilon_n, p.epsilon_e, p.epsilon_l))):
        lo, hi = x.copy(), x.copy()
        lo[i] -= 1e-6
        hi[i] += 1e-6
        derivative = (flow(*hi, p) - flow(*lo, p)) / 2e-6
        assert derivative == pytest.approx(weight / (x[i] + epsilon), rel=1e-7)
        assert flow(*hi, p) > flow(*x, p)


def test_s10_3_factor_collapse_uniform_clipping_and_frontier_limit():
    b_min = bandwidth_clip(5, 0.5, 1e-6)
    for b in (0, b_min / 4, b_min):
        assert transfer(5, b, 1, 0.5, b_min, 5) <= 1.000000001e-6
        assert transfer(0, b, 0, 0.5, b_min, 5) == 1
        assert transfer(1e-10, b, 0, 0.5, b_min, 5) == pytest.approx(1, abs=1e-9)
    assert transfer(2, b_min * (1 - 1e-9), 0.5, 0.5, b_min, 5) == pytest.approx(transfer(2, b_min * (1 + 1e-9), 0.5, 0.5, b_min, 5), rel=1e-7)
    assert responsiveness([0.25, 1]) == 0.5
    assert responsiveness([0, 1]) == 0
    assert lineage(0.5, 100, 200, 0.5, 0.5) == 0.0625
    for index in range(4):
        factors = [0.5, 100, 0.5, 0.5]
        factors[index] = 0
        assert lineage(factors[0], factors[1], 200, factors[2], factors[3]) == 0
    assert execution(0) == 0
    assert execution(1) == pytest.approx(1 - math.exp(-2.5))


def test_s10_3_declared_diversity_proxy_is_pairwise_bounded_and_label_invariant():
    traits = np.random.default_rng(4).uniform(0.05, 0.5, (12, 10))
    expected = np.mean([np.mean(abs(traits[i] - traits[j])) / 0.45 for i in range(12) for j in range(i)])
    assert propensity_diversity(traits) == pytest.approx(expected)
    assert propensity_diversity(traits[::-1]) == propensity_diversity(traits)
    assert propensity_diversity(np.full((10, 10), 0.25)) == 0
    assert propensity_diversity([[0.05] * 10, [0.5] * 10]) == pytest.approx(1)
    assert propensity_diversity([]) == 0


def test_s10_4_common_extinction_flow_and_absorbing_reduced_state():
    p = parameters(h_e_min=0.1)
    assert flow(0, 0.1, 0, p) == p.extinction_flow
    assert flow(0.2, 0.5, 0.1, p) > p.extinction_flow
    with pytest.raises(ValueError):
        flow(0, 0, 0, p)
    kernel = np.array([[0.8, 0.2], [0, 1]])
    extinct = np.array([0.0, 1.0])
    assert np.array_equal(extinct @ np.linalg.matrix_power(kernel, 50), extinct)
    for count in (0, 1, 20, 100):
        d = discounted_flow([p.extinction_flow] * count, 0.97, ValueBound(p.extinction_flow))
        assert d.value == pytest.approx(p.extinction_flow)


def test_discount_continuation_unconditional_path_and_error_bound():
    beta, dagger = 0.9, -3.0
    q = np.array([[0.8]])
    c = exact_continuation(q, [2.0], beta, dagger)[0]
    # Exact mixture over time of live reward and the absorbing reward.
    expected = dagger + (1 - beta) * (2 - dagger) / (1 - beta * 0.8)
    assert c == pytest.approx(expected)
    flows = [0.8**t * 2 + (1 - 0.8**t) * dagger for t in range(20)]
    continuation = 0.8**20 * c + (1 - 0.8**20) * dagger
    exact = discounted_flow(flows, beta, ValueBound(continuation))
    perturbed = discounted_flow(flows, beta, ValueBound(continuation + 0.1, 0.1), step_errors=[0.01] * 20)
    assert exact.value == pytest.approx(c)
    assert abs(perturbed.value - c) <= perturbed.error
    assert domain_continuation(-3, 5) == ValueBound(1, 4)
    assert discount_factor(0.01) == pytest.approx(math.exp(-0.01))


@pytest.mark.parametrize("bad", [math.nan, math.inf, -0.1])
def test_invalid_measurements_are_rejected(bad):
    with pytest.raises(ValueError):
        execution(bad)
    with pytest.raises(ValueError):
        flow(bad, 0.2, 0.2, parameters())
