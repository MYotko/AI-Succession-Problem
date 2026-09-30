"""A6 reading tests on synthetic data with known answers. No registered output.

Fast verdict cases use strict=False (small resamples); the registered strict guards
(registered grid, at least 50,000 resamples, full capability grid) are tested
separately.
"""
import math

import numpy as np
import pytest

from v3 import reading_a6 as r6

GRID = list(r6.R1_GRID)               # nine R1 rr
SGRID = list(r6.SIGMA_GRID)           # five sigma rr


def _det(cross_index, grid=GRID, n=200):
    """Deterministic populations: survive (50) at rr index > cross_index."""
    return {rr: np.full(n, 50 if i > cross_index else 5) for i, rr in enumerate(grid)}


def _noisy(boundary_rr, grid=GRID, n=300, slope=30.0, seed=0):
    rng = np.random.default_rng(seed)
    return {rr: np.where(rng.random(n) < min(0.97, max(0.03, 0.5 + (rr - boundary_rr) * slope)), 50, 5)
            for rr in grid}


def _cb(arm, nom, **kw):
    kw.setdefault("strict", False)
    return r6.compare_boundary(arm, nom, **kw)


def _cc(arm, nom, alpha, **kw):
    kw.setdefault("strict", False)
    return r6.compare_capstar(arm, nom, alpha, **kw)


def test_point_quantities():
    cells = _det(4)
    assert r6.survival_rate(cells[GRID[0]]) == 0.0 and r6.survival_rate(cells[GRID[5]]) == 1.0
    assert GRID[4] <= r6.boundary(GRID, [r6.survival_rate(cells[r]) for r in GRID]) <= GRID[5]


def test_boundary_edge_half_at_lowest_rr_is_a_crossing():
    # Survival exactly 0.5 at the lowest rr is a crossing at that rr, not below range.
    rates = [0.5] + [0.6] * (len(GRID) - 1)
    assert r6.boundary(GRID, rates) == GRID[0]
    assert r6._boundary_of_rates(GRID, rates) == GRID[0]
    # Above 0.5 at the lowest rr is below range.
    assert r6._boundary_of_rates(GRID, [0.7] + [0.9] * (len(GRID) - 1)) == -math.inf


def test_boundary_moves_materially_higher():
    res = _cb(_det(7), _det(3), grid=GRID, resamples=2000)
    assert res["verdict"] == "moves_materially_higher" and res["interval"][0] > r6.BOUNDARY_MARGIN


def test_boundary_moves_materially_lower_with_real_variance():
    arm = _noisy(0.059, n=400, slope=45.0, seed=1)
    nom = _noisy(0.064, n=400, slope=45.0, seed=2)
    res = _cb(arm, nom, grid=GRID, resamples=8000, seed=3)
    assert res["verdict"] == "moves_materially_lower"
    assert res["interval"][1] < -r6.BOUNDARY_MARGIN and math.isfinite(res["interval"][0])


def test_boundary_robust_when_identical():
    nom = _det(4)
    res = _cb({k: v.copy() for k, v in nom.items()}, nom, grid=GRID, resamples=2000)
    assert res["verdict"] == "robust" and res["interval"] == [0.0, 0.0]


def test_boundary_inconclusive_with_real_variance():
    arm = _noisy(0.061, n=80, slope=18.0, seed=11)
    nom = _noisy(0.061, n=80, slope=18.0, seed=12)
    res = _cb(arm, nom, grid=GRID, resamples=8000, seed=5)
    lo, hi = res["interval"]
    assert res["verdict"] == "inconclusive"
    assert (lo < -r6.BOUNDARY_MARGIN or hi > r6.BOUNDARY_MARGIN) and math.isfinite(lo) and math.isfinite(hi)


def test_undetermined_arm_no_crossing():
    arm = {rr: np.full(100, 5) for rr in GRID}
    res = _cb(arm, _det(4), grid=GRID, resamples=500)
    assert res["verdict"] == "undetermined" and "above range" in res["reason"]


def test_undetermined_undefined_comparator():
    nom = {rr: np.full(100, 5) for rr in GRID}
    res = _cb(_det(4), nom, grid=GRID, resamples=500)
    assert res["verdict"] == "undetermined" and "comparator" in res["reason"]


def test_undetermined_sigma_above_0066():
    arm = {rr: np.full(100, 5) for rr in SGRID}
    nom = {rr: np.full(100, 50 if rr >= 0.062 else 5) for rr in SGRID}
    res = _cb(arm, nom, grid=SGRID, resamples=500, sigma_variant=True)
    assert res["verdict"] == "undetermined"


def test_undetermined_sigma_below_0059():
    arm = {rr: np.full(100, 50) for rr in SGRID}
    nom = {rr: np.full(100, 50 if rr >= 0.062 else 5) for rr in SGRID}
    res = _cb(arm, nom, grid=SGRID, resamples=500, sigma_variant=True)
    assert res["verdict"] == "undetermined" and "0.059" in res["reason"]


def test_interval_reaches_infinity_with_both_points_defined():
    top = np.array([50] * 52 + [5] * 48)
    arm = {rr: (top.copy() if rr == GRID[-1] else np.full(100, 5)) for rr in GRID}
    res = _cb(arm, _det(3), grid=GRID, resamples=8000, seed=1)
    assert math.isfinite(res["arm_boundary"]) and math.isfinite(res["nominal_boundary"])
    assert not (math.isfinite(res["interval"][0]) and math.isfinite(res["interval"][1]))
    assert res["verdict"] in ("inconclusive", "moves_materially_higher")


def test_undefined_resamples_placed_conservatively():
    # The helper places undefined resamples at -inf for the lower percentile and
    # +inf for the upper, so they can only widen the interval.
    diff = np.zeros(10000)
    undefined = np.zeros(10000, bool)
    undefined[:100] = True                       # 1% undefined
    lo, hi = r6._conservative_interval(diff, undefined, 0.01)   # tail 0.5% each side
    assert lo == -math.inf and hi == math.inf
    # With none undefined the interval is the finite point.
    lo2, hi2 = r6._conservative_interval(diff, np.zeros(10000, bool), 0.01)
    assert lo2 == 0.0 and hi2 == 0.0 and lo <= lo2 and hi >= hi2


def test_boundaries_edge_half_at_lowest_rr_on_resamples():
    # The vectorized bootstrap also treats 0.5 at the lowest rr as a crossing there.
    rrs = GRID
    mat = np.array([[0.5, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6],   # crossing at rrs[0]
                    [0.7, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9],   # below range
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])  # above range
    out = r6._boundaries(rrs, mat)
    assert out[0] == rrs[0] and out[1] == -math.inf and out[2] == math.inf


def test_grid_assertion_rejects_shrunk_grid():
    nom = _det(4)
    arm = {k: v for k, v in _det(4).items() if k != GRID[0]}
    with pytest.raises(ValueError):
        _cb(arm, nom, grid=GRID, resamples=100)


def test_strict_guards():
    nom = _det(4)
    arm = {k: v.copy() for k, v in nom.items()}
    # Too few resamples is refused in strict mode (explicit raise, not a bare assert).
    with pytest.raises(ValueError):
        r6.compare_boundary(arm, nom, grid=GRID, resamples=1000, strict=True)
    # A non-registered grid is refused.
    tiny = [GRID[0], GRID[1], GRID[2]]
    with pytest.raises(ValueError):
        r6.compare_boundary({r: nom[r] for r in tiny}, {r: nom[r] for r in tiny}, grid=tiny,
                            resamples=r6.DEFAULT_RESAMPLES, strict=True)
    # A registered strict call runs (50,000 resamples over the nine rr).
    res = r6.compare_boundary(arm, nom, grid=GRID, resamples=r6.DEFAULT_RESAMPLES, strict=True)
    assert res["verdict"] == "robust"


def _fire(cross_index, n=200, marginal=None):
    cells = {}
    for i, c in enumerate(r6.CAPABILITIES):
        if marginal is not None and i == marginal:
            cells[c] = np.array([1, 0] * (n // 2))
        else:
            cells[c] = np.ones(n, int) if i <= cross_index else np.zeros(n, int)
    return cells


def test_capstar_point_and_censoring():
    assert r6.cap_star({c: 1.0 for c in r6.CAPABILITIES})["censored"] == "top"
    assert r6.cap_star({c: 0.1 for c in r6.CAPABILITIES})["censored"] == "bottom"
    mid = r6.cap_star({c: (1.0 if i <= 3 else 0.0) for i, c in enumerate(r6.CAPABILITIES)})
    assert mid["value"] == r6.CAPABILITIES[3] and mid["step"] == 3


def test_capstar_moves_robust_inconclusive():
    assert _cc(_fire(5), _fire(2), 1.0, resamples=2000)["verdict"] == "moves_materially_higher"
    rob = _cc(_fire(3), _fire(3), 1.0, resamples=2000)
    assert rob["verdict"] == "robust" and rob["interval"] == [0.0, 0.0]
    inc = _cc(_fire(2, marginal=3), _fire(2), 1.0, resamples=4000, seed=7)
    assert inc["verdict"] == "inconclusive"


def test_capstar_strict_missing_capability_fails():
    arm = _fire(3)
    nom = _fire(3)
    del arm[r6.CAPABILITIES[-1]]                  # drop one capability
    with pytest.raises(ValueError):
        r6.compare_capstar(arm, nom, 1.0, resamples=r6.DEFAULT_RESAMPLES, strict=True)
    with pytest.raises(ValueError):
        r6.compare_capstar(_fire(3), _fire(3), 1.0, resamples=1000, strict=True)


def test_headline_comparisons_count():
    comps = r6.headline_comparisons()
    assert len(comps) == 33
    assert sum(c["kind"] == "boundary" for c in comps) == 8
    assert sum(c["kind"] == "cap_star" for c in comps) == 25


def test_cell_selection_filters_and_seed_counts():
    arm_r1 = [{"rr": rr, "alpha": 1.0, "capability": 1.5, "kappa": 0.75, "theta": 0.25, "steps": 500,
               "variant": None, "category": "R1", "final_population": 50} for rr in GRID for _ in range(100)]
    arm_r2 = [{"rr": 0.064, "alpha": 1.0, "capability": 1.5, "kappa": 0.75, "theta": 0.25, "steps": 500,
               "variant": None, "category": "R2", "final_population": 5} for _ in range(50)]
    filters = {"category": "R1", "kappa": 0.75, "theta": 0.25, "steps": 500, "variant": None, "capability": 1.5}
    cells = r6.select_boundary_cells(arm_r1 + arm_r2, GRID, filters, expected_seeds=100)
    assert all(len(cells[rr]) == 100 for rr in GRID)
    with pytest.raises(ValueError):
        r6.select_boundary_cells(arm_r1[:-1], GRID, filters, expected_seeds=100)
    comp = [{"rr": 0.064, "alpha": 1.0, "capability": c, "kappa": 8.0, "theta": 0.5, "steps": 500,
             "variant": None, "category": "R2", "fired": i % 2 == 0}
            for c in r6.CAPABILITIES for i in range(75)]
    cfilters = {"category": "R2", "kappa": 8.0, "theta": 0.5, "steps": 500, "variant": None}
    fcells = r6.select_capstar_cells(comp, 1.0, cfilters, expected_seeds=75)
    assert all(len(fcells[c]) == 75 for c in r6.CAPABILITIES)


def test_survival_differences_descriptive():
    rows = r6.survival_differences(_det(3), _det(4), resamples=1000)
    assert len(rows) == len(GRID) and all("interval95" in r for r in rows)


def test_seed_convergence_requires_indices():
    cells = _det(4)
    with pytest.raises(ValueError):
        r6.seed_convergence(cells, None)
    idx = {k: np.arange(len(cells[k]))[::-1] for k in cells}
    conv = r6.seed_convergence(cells, idx)
    assert conv["half_seed_count"][GRID[5]] == 100 and conv["full_seed_count"][GRID[5]] == 200
    fire = _fire(3)
    fidx = {c: np.arange(len(fire[c])) for c in fire}
    cap = r6.seed_convergence(fire, fidx, quantity="cap_star")
    assert cap["quantity"] == "cap_star" and cap["full_seed"]["step"] == 3
