"""S10.5,6,8,10 on explicitly reduced kernels and phase support."""

import numpy as np
import pytest
from v3.admission import tail_rejection
from v3.spectral import (
    lifetime_surplus, perron_flow, periodic_perron_flow, primitive,
    ranking_reversal, survival_conditioned_flow,
)
from v3.support import relay_graph, shock_support


def test_s10_6_left_perron_formula_and_sterile_invariance():
    q = np.array([[0.5, 0.3, 0.1], [0.2, 0.4, 0.1], [0, 0, 0.95]])
    u = [1, 4, -20]
    result = perron_flow(q, u, [0, 1])
    expected_root = (0.9 + np.sqrt(0.25)) / 2  # eigenvalue of the 2x2 block
    assert result.survival_eigenvalue == pytest.approx(expected_root)
    left = np.array(result.distribution)
    assert left @ q[:2, :2] == pytest.approx(expected_root * left)
    assert result.lambda_f == pytest.approx(left @ u[:2])
    modified = q.copy()
    modified[2, 2] = 0.2
    assert perron_flow(modified, [1, 4, 2000], [0, 1]).lambda_f == result.lambda_f
    # Restoring reproduction changes the communicating class, hence the value.
    restored = q.copy()
    restored[2] = [0.1, 0.1, 0.7]
    with pytest.raises(ValueError):
        perron_flow(restored, u, [0, 1])
    assert perron_flow(restored, u, [0, 1, 2]).lambda_f != result.lambda_f


def test_s10_6_side_diagnostics_lifetime_surplus_and_ranking_flag():
    q = np.array([[0.8, 0.1], [0, 0.95]])
    u, initial = np.array([3.0, -2.0]), [1, 0]
    assert perron_flow(q, u, [0]).lambda_f == 3
    assert survival_conditioned_flow(q, u, initial) == pytest.approx(-2, abs=1e-9)
    ls = lifetime_surplus(q, u, initial, -3)
    p, summed = np.array(initial, float), 0.0
    for _ in range(2000):
        summed += float(p @ (u + 3))
        p = p @ q
    assert ls == pytest.approx(summed)
    assert ranking_reversal(4, 10, 3, 20)
    assert not ranking_reversal(3, 10, 3, 20)
    assert perron_flow(q, u + 0.25, [0]).lambda_f == pytest.approx(3.25)


def test_s10_6_periodic_limits_are_phase_conditioned_then_unweighted():
    phases = [np.array([[0.5, 0.2], [0.1, 0.4]]), np.array([[0.3, 0.4], [0.2, 0.6]])]
    flows = [[1, 3], [4, 0]]
    value, means = periodic_perron_flow(phases, flows)
    p = np.array([1.0, 0.0])
    for _ in range(1000):
        p = p @ phases[0] @ phases[1]
        p /= p.sum()
    next_p = p @ phases[0]
    next_p /= next_p.sum()
    assert means == pytest.approx([p @ flows[0], next_p @ flows[1]])
    assert value == pytest.approx(sum(means) / 2)


@pytest.mark.parametrize("mix", [0, 0.3, 1])
def test_s10_5_primitive_reduced_constant_feedback_randomized(mix):
    first = np.array([[0.5, 0.2], [0.3, 0.4]])
    second = np.array([[0.2, 0.5], [0.1, 0.7]])
    feedback = np.array([first[0], second[1]])
    assert primitive(mix * feedback + (1 - mix) * second)
    assert not primitive([[0, 0.8], [0.7, 0]])
    with pytest.raises(ValueError):
        perron_flow([[0, 0.8], [0.7, 0]], [1, 1], [0, 1])


def test_s10_8_shock_support_requires_birth_relay_and_reachability():
    # Nodes include two phases. One parent survives to phase 1, then gives
    # birth to a phase-0 entrant even if the parent dies on that step.
    survival = np.array([[False, True], [False, False]])
    birth = np.array([[False, False], [True, False]])
    result = shock_support(0.99, 0.6, 0.3187, survival_support=survival, birth_support=birth, initial_nodes=[0])
    assert result.admitted and result.relay_cycle
    assert relay_graph(survival, birth)[0, 0]
    assert not shock_support(1, 0, 0.3187).admitted
    assert shock_support(0.9, 0.3, 0.3187).admitted
    assert not shock_support(0, 1, 0.3187, survival_support=np.eye(2, dtype=bool), birth_support=np.zeros((2, 2), bool), initial_nodes=[0]).admitted
    unreachable_birth = np.array([[False, False], [False, True]])
    assert not shock_support(0, 1, 0.3187, survival_support=np.zeros((2, 2), bool), birth_support=unreachable_birth, initial_nodes=[0]).admitted
    with pytest.raises(ValueError):
        shock_support(0.2, 0.6, 0.3187)


def test_s10_8_relay_matches_direct_marked_cycle_enumeration():
    # Exhaust all 256 two-node survivor/birth supports. Independently
    # enumerate simple cycles in the combined graph containing a birth.
    for mask in range(256):
        bits = [(mask >> i) & 1 for i in range(8)]
        s = np.array(bits[:4], bool).reshape(2, 2)
        b = np.array(bits[4:], bool).reshape(2, 2)
        edges = s | b
        expected = bool(b[0, 0] or b[1, 1] or (edges[0, 1] and edges[1, 0] and (b[0, 1] or b[1, 0])))
        actual = shock_support(0, 1, 0, survival_support=s, birth_support=b, initial_nodes=[0, 1])
        assert actual.admitted == expected


def test_s10_10_eta_zero_exact_and_bias_coverage_gate():
    candidate = perron_flow([[0.7]], [1], [0]).zeta
    comparator = perron_flow([[0.8]], [1], [0]).zeta
    assert tail_rejection(candidate, [comparator], coverage_including_bias=True).binding
    diagnostic = tail_rejection(candidate, [comparator], coverage_including_bias=False)
    assert diagnostic.would_reject and not diagnostic.binding
    assert not tail_rejection(comparator, [comparator], coverage_including_bias=True).would_reject
