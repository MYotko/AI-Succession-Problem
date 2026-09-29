"""A4 pure-function tests: formulas against hand-computed values, the C0 refit
on a known fixed point, living-source masking, the width bound, empirical
Bernstein coverage, t quantiles, Fieller versus delta, seeds and range halts.

Fast: no simulation, no I/O. Run with `python -B -m pytest test_v3_a4_functions.py`.
"""
import math

import numpy as np
import pytest

from v3 import continuation_validation as cv


# --------------------------------------------------------------------------- seeds

def test_seed_streams_distinct_and_60_bit():
    seeds = cv.derive_seeds(1234567890123456789, "plain")
    assert set(seeds) == {"fit", "census", "validate_1", "validate_2", "validate_3"}
    for value in seeds.values():
        assert 0 <= value < (1 << 60)
    assert len(set(seeds.values())) == len(seeds)


def test_seed_distinctness_passes_for_real_seed():
    seeds = cv.assert_seeds_distinct(98765432109876543210, "plain")
    assert seeds["fit"] != seeds["census"]


def test_seed_collision_halts():
    a1 = 42
    collide = cv.fit_seed(a1)
    with pytest.raises(cv.SeedCollision):
        cv.assert_seeds_distinct(a1, "plain", probe_seeds=[collide])


def test_planning_seeds_match_committed_derivations():
    # The committed run_p3 / run_validation / analyze_validation derivations.
    seed = 777
    assert cv._planning_p1_seed(seed) == int(__import__("hashlib").sha256(b"planning_P1" + str(seed).encode()).hexdigest()[:15], 16)
    assert cv._planning_p3_seed(seed, 2) == int(__import__("hashlib").sha256(b"planning_P3" + str(seed).encode() + b"2").hexdigest()[:15], 16)


# --------------------------------------------------------------------------- t quantile

def test_student_t_known_quantiles():
    assert abs(cv.student_t_quantile(30, 0.975) - 2.0423) < 1e-3
    assert abs(cv.student_t_quantile(10, 0.975) - 2.2281) < 1e-3
    assert abs(cv.student_t_quantile(31, 0.995) - 2.744) < 2e-3


def test_student_t_tends_to_normal():
    # z at 0.975 = 1.959964; large df must approach it.
    assert abs(cv.student_t_quantile(10_000_000, 0.975) - 1.959964) < 1e-3


def test_student_t_symmetry_and_cdf_roundtrip():
    assert abs(cv.student_t_quantile(20, 0.1) + cv.student_t_quantile(20, 0.9)) < 1e-9
    q = cv.student_t_quantile(15, 0.99)
    assert abs(cv.student_t_cdf(q, 15) - 0.99) < 1e-6


def test_incomplete_beta_symmetry():
    # I_x(a,b) + I_{1-x}(b,a) = 1.
    assert abs(cv.regularized_incomplete_beta(2.5, 3.5, 0.4) + cv.regularized_incomplete_beta(3.5, 2.5, 0.6) - 1.0) < 1e-12


# --------------------------------------------------------------------------- empirical Bernstein

def test_empirical_bernstein_hand_value():
    # n=4 constant m_i=0, width=1, M=1, alpha=0.05: var=0, rho = 7 w ln(80)/(3*3).
    rho = 7 * 1.0 * math.log(80) / 9
    out = cv.empirical_bernstein(sum_m=0.0, sum_m2=0.0, n=4, width=1.0, M=1, tau=4.0)
    assert abs(out["rho"] - rho) < 1e-12
    assert out["status"] == "certified"
    tight = cv.empirical_bernstein(0.0, 0.0, 4, 1.0, 1, tau=rho - 0.01)
    assert tight["status"] == "unresolved"


def test_empirical_bernstein_violation():
    # mbar=10, var=0, rho~3.408, tau=4 -> disjoint from [-4,4].
    out = cv.empirical_bernstein(sum_m=40.0, sum_m2=400.0, n=4, width=1.0, M=1, tau=4.0)
    assert out["status"] == "violation"


def test_empirical_bernstein_n_lt_2_unresolved():
    assert cv.empirical_bernstein(0.0, 0.0, 1, 1.0, 1, 1.0)["status"] == "unresolved"


def test_empirical_bernstein_coverage_simulation():
    # Small Monte-Carlo: with a true mean 0 inside a tight tau, the two-sided
    # certificate must (almost) never falsely violate.
    rng = np.random.default_rng(20260929)
    width = 1.0
    false_violations = 0
    trials = 400
    for _ in range(trials):
        m = rng.uniform(-0.5, 0.5, size=200)  # mean ~0, bounded in width 1
        sm, sm2, n = float(m.sum()), float((m ** 2).sum()), len(m)
        out = cv.empirical_bernstein(sm, sm2, n, width, M=10, tau=0.6)
        if out["status"] == "violation":
            false_violations += 1
    assert false_violations == 0


# --------------------------------------------------------------------------- C0 refit and residuals

def test_refit_all_internal_returns_flow():
    # A chain that always stays in the population-0 cell with constant flow f
    # has fixed point C0 = f.
    n = 20
    src = np.full(n, cv.POP0_CELL, dtype=np.int64)
    nxt = np.full(n, cv.POP0_CELL, dtype=np.int64)
    alive = np.ones(n, bool)
    dead = np.zeros(n, bool)
    flows = np.full(n, 3.7)
    out = cv.refit_c0(src, nxt, alive, dead, flows, a1_published={}, lower=0.0)
    assert out["published"] and abs(out["value"] - 3.7) < 1e-9
    assert out["visits"] == n and out["internal"] == n


def test_refit_closed_form_with_boundary():
    # k internal, N-k to a published cell of value V; closed form check.
    N, k, f, V = 12, 5, 2.0, 9.0
    src = np.full(N, cv.POP0_CELL, dtype=np.int64)
    pub_code = 123
    nxt = np.array([cv.POP0_CELL] * k + [pub_code] * (N - k), dtype=np.int64)
    alive = np.ones(N, bool)
    dead = np.zeros(N, bool)
    flows = np.full(N, f)
    out = cv.refit_c0(src, nxt, alive, dead, flows, a1_published={pub_code: V}, lower=0.0)
    expected = ((1 - cv.BETA) * N * f + cv.BETA * (N - k) * V) / (N - cv.BETA * k)
    assert abs(out["value"] - expected) < 1e-9
    # Direct one-step check that expected is the fixed point.
    rhs = (1 - cv.BETA) * f + cv.BETA * ((k / N) * expected + ((N - k) / N) * V)
    assert abs(rhs - expected) < 1e-9


def test_refit_excludes_unpublished_and_min_visits():
    # Transitions into an unpublished cell are excluded; below 4 visits -> unpublished.
    src = np.full(3, cv.POP0_CELL, dtype=np.int64)
    nxt = np.array([cv.POP0_CELL, 555, cv.POP0_CELL], dtype=np.int64)  # 555 unpublished
    alive = np.ones(3, bool)
    dead = np.zeros(3, bool)
    flows = np.full(3, 1.0)
    out = cv.refit_c0(src, nxt, alive, dead, flows, a1_published={}, lower=0.0)
    assert out["visits"] == 2 and not out["published"]  # only two covered, below min_visits


def test_living_source_mask_with_extinct_tail():
    # A single trajectory alive for two steps then extinct; only living sources count.
    src = cv.plain_cell_codes([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]])
    nxt = cv.plain_cell_codes([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]])
    source_alive = np.array([True, True, False])   # third step's source already extinct
    dead = np.array([False, True, True])           # step 2 lands extinct
    flows = np.array([1.0, 1.0, 1.0])
    value = {int(cv.POP0_CELL): 1.0}
    residual, covered, srcidx, codes = cv.living_source_residuals(src, nxt, source_alive, dead, flows, value, lower=0.0)
    assert covered.tolist() == [True, True, False]


# --------------------------------------------------------------------------- width bound

def test_width_bounds_every_residual():
    rng = np.random.default_rng(7)
    lower, upper = -2.0, 5.0
    W = upper - lower
    for _ in range(50):
        C = rng.uniform(lower, upper)
        vmax = rng.uniform(C, upper)
        w = cv.row_width(W, vmax, lower, upper)
        # Every possible m_i = (1-beta) f + beta V - C lies in an interval of length w.
        f = rng.uniform(lower, upper, 100)
        V = rng.uniform(lower, vmax, 100)
        m = (1 - cv.BETA) * f + cv.BETA * V - C
        assert m.max() - m.min() <= w + 1e-9


def test_width_range_halt():
    with pytest.raises(cv.OutOfRange):
        cv.row_width(7.0, vmax=99.0, lower=0.0, upper=5.0)
    with pytest.raises(cv.OutOfRange):
        cv.check_in_range([0.0, 6.0], 0.0, 5.0, "flow")


# --------------------------------------------------------------------------- FV: Fieller vs delta

def test_fieller_and_delta_agree_on_perfect_ratio():
    # S_g = c N_g exactly -> both intervals collapse to the point c.
    c = 0.03
    N_g = np.array([5, 8, 3, 7, 6, 9, 4, 10.0])
    S_g = c * N_g
    t = 2.5
    delta = cv.delta_method_interval(S_g, N_g, t)
    fieller = cv.fieller_interval(S_g, N_g, t)
    assert abs(delta["mu"] - c) < 1e-12
    assert fieller["bounded"]
    assert abs(fieller["interval"][0] - c) < 1e-9 and abs(fieller["interval"][1] - c) < 1e-9


def test_fieller_unbounded_flagged():
    # Visit counts vary widely across groups -> Nbar^2 <= (t^2/n) s_NN, unbounded.
    N_g = np.array([1.0] * 19 + [100.0])
    S_g = np.zeros(20)
    out = cv.fieller_interval(S_g, N_g, t=8.0)
    assert out["bounded"] is False


def test_fv_cell_unresolved_below_16_groups():
    N_g = np.ones(10)
    S_g = np.zeros(10)
    out = cv.fv_cell_test(S_g, N_g, M_fv=1000, tau=1.0)
    assert out["status"] == "unresolved"


def test_fv_cell_passes_clean_data():
    N_g = np.full(32, 10.0)
    S_g = np.zeros(32)  # zero residuals -> both intervals are the point 0
    out = cv.fv_cell_test(S_g, N_g, M_fv=1000, tau=0.5)
    assert out["status"] == "passed"


# --------------------------------------------------------------------------- M and M_FV

def test_M_counts():
    plain = [{"route": "plain", "continuation": {"entries": [
        {"bin": [0, 1, 0, 0, 0, 0]}, {"bin": [2, 1, 0, 0, 0, 0]}, {"bin": [0, 3, 0, 0, 0, 0]}]}}]
    # published cells with pop>0: two ([2,...] and... wait bin[0] is population). Here bin[0] in {0,2,0}
    # so one has pop>0 -> M = 1 + 1 = 2.
    assert cv.count_M_plain(plain) == 2
    fv = [{"route": "fv", "continuation": {"entries": [{"bin": [1, 0, 0, 0, 0, 0]}, {"bin": [2, 0, 0, 0, 0, 0]}]}}]
    assert cv.count_M_fv(fv) == 2


# --------------------------------------------------------------------------- census

def test_census_fractions_and_floor():
    endpoints = np.array([[0, 0, 0, 0, 0, 0], [3, 1, 0, 0, 0, 0], [0, 2, 0, 0, 0, 0], [4, 0, 0, 0, 0, 0]])
    low = np.array([True, False, True, False])
    support = {int(cv.POP0_CELL), int(cv.fine_codes([[3, 1, 0, 0, 0, 0]])[0])}
    frac = cv.census_fractions(endpoints, low, support, "plain")
    # Endpoint 4 (fine, pop>0) is outside support -> 1 of 4 living missing.
    assert abs(frac["fraction_among_living_endpoints"] - 0.25) < 1e-9
    # Both low endpoints are POP0_CELL, in support -> 0 missing among low.
    assert frac["fraction_among_low_population_living_endpoints"] == 0.0
    floor = cv.census_floor(frac)
    assert floor["living_ok"] is False  # 25% > 2%
    assert floor["passed"] is False


def test_census_floor_low_not_assessed_below_50():
    frac = {"fraction_among_living_endpoints": 0.0, "fraction_among_low_population_living_endpoints": 0.9,
            "living_endpoints": 1000, "low_population_living_endpoints": 10}
    floor = cv.census_floor(frac)
    assert floor["low_assessed"] is False and floor["passed"] is True and floor["assessed"] is True


def test_census_floor_zero_living_passes_not_assessed():
    frac = {"fraction_among_living_endpoints": None, "fraction_among_low_population_living_endpoints": None,
            "living_endpoints": 0, "low_population_living_endpoints": 0}
    floor = cv.census_floor(frac)
    assert floor["passed"] is True and floor["assessed"] is False


def test_census_fractions_from_counts():
    fine = int(cv.fine_codes([[3, 1, 0, 0, 0, 0]])[0])   # pop>0
    pop0 = int(cv.fine_codes([[0, 2, 0, 0, 0, 0]])[0])   # pop cat 0 (code % 8 == 0)
    out_fine = int(cv.fine_codes([[4, 0, 0, 0, 0, 0]])[0])  # pop>0, outside support
    counts = {fine: 10, pop0: 5, out_fine: 5}
    support = {int(cv.POP0_CELL), fine}
    frac = cv.census_fractions_from_counts(counts, support, "plain")
    assert frac["living_endpoints"] == 20 and frac["low_population_living_endpoints"] == 5
    assert abs(frac["fraction_among_living_endpoints"] - 5 / 20) < 1e-9  # only out_fine missing
    assert frac["fraction_among_low_population_living_endpoints"] == 0.0  # pop0 -> POP0_CELL in support
