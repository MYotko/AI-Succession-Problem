"""A6 reading: survival, the boundary, cap*, and the difference verdicts.

Amendment A6, 2026-09-29. Section 8's quantities on each arm's cells, and the
registered comparison of an arm against the nominal reruns: a percentile
bootstrap interval on the difference (arm minus nominal), the materiality
margins, and the four verdicts.

This tool operates on in-memory arrays only. It never reads a registered rerun
output; the tests exercise it on synthetic data with known answers. Blindness is
the caller's responsibility for real data; nothing here writes a survival,
extinction or fire rate to a shared artifact.

Reuse of gates.py: cap*'s definition and D24 censoring mirror
``gates.cliff_checks`` (gates.py:479-497): cap* is the largest capability whose
fire rate is at least 0.5, with None read as "below 1.2" (bottom-censored) and
5.0 as "5.0 or higher" (top-censored), in the same censored order, and a
no-crossing bootstrap resample is placed at an infinite end by direction, never
dropped, exactly as gates places censored bootstrap cap* values. We mirror the
arithmetic here rather than call ``cliff_checks``, which requires full run
records; ``CAPABILITIES`` and ``ALPHAS`` are imported from gates so the grid stays
single-sourced.
"""
import math

import numpy as np

from .gates import CAPABILITIES, ALPHAS
from .study import R1_RR

SURVIVAL_THRESHOLD = 30
FIRE_THRESHOLD = 0.5
BOUNDARY_MARGIN = 0.002          # rr
CAPSTAR_MARGIN_STEPS = 1         # one capability grid step
HEADLINE_COMPARISONS = 33
FAMILY_ALPHA = 0.05
BONFERRONI_ALPHA = FAMILY_ALPHA / HEADLINE_COMPARISONS   # 0.05/33
DEFAULT_RESAMPLES = 50000
SIGMA_BELOW_RANGE = 0.059        # a sigma0^2 boundary below this reads undetermined
CAP_INDEX = {c: i for i, c in enumerate(CAPABILITIES)}

# The registered grids. R1-grid arms score all nine R1 rr; the sigma0^2 arms
# score the five narrowed rr. The reading asserts the exact grid and never
# shrinks it silently.
R1_GRID = tuple(R1_RR)
SIGMA_GRID = (0.059, 0.060, 0.062, 0.064, 0.066)
R2_CAPSTAR_RR = 0.064
R1_ARM_ALPHA = 1.0


# ---------------------------------------------------------------------------
# Point quantities (section 8)
# ---------------------------------------------------------------------------

def survival_rate(final_populations, threshold=SURVIVAL_THRESHOLD):
    """Survival rate: the fraction of seeds whose final population is at least
    ``threshold`` (30) at the run's last step."""
    pop = np.asarray(final_populations)
    if pop.size == 0:
        return None
    return float((pop >= threshold).mean())


def survival_indicators(final_populations, threshold=SURVIVAL_THRESHOLD):
    """Per-seed 0/1 survival indicators from final populations."""
    return (np.asarray(final_populations) >= threshold).astype(float)


def _boundary_of_rates(rrs, s):
    """The boundary from a survival-rate array aligned to sorted ``rrs``.

    Returns the first upward 50 percent crossing by linear interpolation, or an
    infinite end when there is no crossing: +inf when the highest rr still has
    survival below 0.5 (the boundary lies above the grid), -inf when the lowest
    rr already has survival at or above 0.5 (the boundary lies below the grid).
    This keeps every value, as gates.py does for a censored cap*."""
    s = np.asarray(s, dtype=float)
    for i in range(len(rrs) - 1):
        if s[i] < 0.5 <= s[i + 1]:
            return float(rrs[i] + (0.5 - s[i]) / (s[i + 1] - s[i]) * (rrs[i + 1] - rrs[i]))
    # Survival of exactly 0.5 at the lowest rr is a crossing at that rr, not below
    # range. Above 0.5 there is below range (-inf); never reaching 0.5 is above (+inf).
    if s[0] == 0.5:
        return float(rrs[0])
    if s[0] > 0.5:
        return -math.inf
    return math.inf


def boundary(rrs, survivals):
    """The finite boundary (first upward 50 percent crossing) or None when
    survival does not cross 0.5 in range. Point-quantity convenience wrapper."""
    order = np.argsort(np.asarray(rrs, dtype=float))
    rrs = np.asarray(rrs, dtype=float)[order]
    s = np.asarray(survivals, dtype=float)[order]
    b = _boundary_of_rates(rrs, s)
    return b if math.isfinite(b) else None


def cap_star(fire_rate_by_cap):
    """cap* for one alpha: the largest capability whose fire rate is at least
    0.5, with D24 censoring. Mirrors gates.cliff_checks. Returns a dict with the
    value, the censored label, and the step index (-1 bottom, 0..6 on the grid).
    """
    fired = [c for c in CAPABILITIES if fire_rate_by_cap.get(c, 0.0) >= FIRE_THRESHOLD]
    if not fired:
        return {"value": None, "label": "below 1.2", "step": -1, "censored": "bottom"}
    value = max(fired)
    step = CAP_INDEX[value]
    if value == CAPABILITIES[-1]:
        return {"value": value, "label": "5.0 or higher", "step": step, "censored": "top"}
    return {"value": value, "label": value, "step": step, "censored": None}


# ---------------------------------------------------------------------------
# Vectorized bootstrap resampling of cell rates
# ---------------------------------------------------------------------------

def _resampled_rates(cells, order, resamples, rng):
    """For each cell in ``order``, draw ``resamples`` seed-bootstrap means.
    ``cells`` maps a key to a 1D array of per-seed 0/1 outcomes."""
    out = np.empty((resamples, len(order)), dtype=float)
    for j, key in enumerate(order):
        data = np.asarray(cells[key], dtype=float)
        n = len(data)
        if n == 0:
            out[:, j] = np.nan
            continue
        idx = rng.integers(0, n, size=(resamples, n))
        out[:, j] = data[idx].mean(axis=1)
    return out


def _boundaries(rrs, rate_matrix):
    """First-upward-crossing boundary per resample, keeping non-crossing rows at
    +/- infinity by direction. ``rate_matrix`` is (R, n_rr) aligned to sorted
    ``rrs``."""
    rrs = np.asarray(rrs, dtype=float)
    s = rate_matrix
    cross = (s[:, :-1] < 0.5) & (s[:, 1:] >= 0.5)
    has = cross.any(axis=1)
    first = np.argmax(cross, axis=1)
    rows = np.arange(s.shape[0])
    si = s[rows, first]
    si1 = s[rows, first + 1]
    ri = rrs[first]
    ri1 = rrs[first + 1]
    with np.errstate(invalid="ignore", divide="ignore"):
        b = ri + (0.5 - si) / (si1 - si) * (ri1 - ri)
    # No interior crossing: survival exactly 0.5 at the lowest rr is a crossing at
    # that rr; strictly above 0.5 is below range (-inf); never reaching 0.5 is above
    # range (+inf). This matches the point rule _boundary_of_rates.
    at_low = s[:, 0] == 0.5
    survives_low = s[:, 0] > 0.5
    no_cross = np.where(at_low, float(rrs[0]), np.where(survives_low, -np.inf, np.inf))
    return np.where(has, b, no_cross)


def _capstar_steps(rate_matrix):
    """cap* step index per resample from an (R, n_cap) fire-rate matrix aligned to
    CAPABILITIES. -1 (bottom) when nothing fires."""
    fired = rate_matrix >= FIRE_THRESHOLD
    idx = np.where(fired, np.arange(rate_matrix.shape[1])[None, :], -1)
    return idx.max(axis=1)


def _interval(values, alpha):
    """The two-sided (1 - alpha) percentile interval [lo, hi] by order statistics
    (inverted_cdf), dropping only nan. Infinite ends are kept."""
    v = np.asarray(values, dtype=float)
    v = v[~np.isnan(v)]
    if v.size < 2:
        return None
    lo = float(np.percentile(v, 100 * (alpha / 2), method="inverted_cdf"))
    hi = float(np.percentile(v, 100 * (1 - alpha / 2), method="inverted_cdf"))
    return [lo, hi]


# ---------------------------------------------------------------------------
# Verdicts
# ---------------------------------------------------------------------------

# The Bonferroni tail for the share of undefined resamples: 0.05 / (2 x 33).
UNDEFINED_RESAMPLE_TAIL = FAMILY_ALPHA / (2 * HEADLINE_COMPARISONS)


def boundary_verdict(interval, margin=BOUNDARY_MARGIN):
    """Classify a difference interval whose points are defined and whose undefined
    resample share is within the Bonferroni tail. Moves materially when the
    interval lies wholly beyond the margin on one side (an infinite end counts);
    robust when it lies wholly within the margin (both ends finite); otherwise
    inconclusive. An infinite end that is not wholly beyond is inconclusive, not
    undetermined (undetermined is decided earlier, from the points and the
    undefined-resample share)."""
    lo, hi = interval
    if lo > margin:
        return "moves_materially_higher"
    if hi < -margin:
        return "moves_materially_lower"
    if math.isfinite(lo) and math.isfinite(hi) and lo >= -margin and hi <= margin:
        return "robust"
    return "inconclusive"


def capstar_verdict(interval, margin_steps=CAPSTAR_MARGIN_STEPS):
    """The difference is in integer grid steps. Moves materially when the whole
    interval is at least one step to one side; robust when it is exactly zero
    steps (lo == hi == 0); otherwise inconclusive."""
    lo, hi = interval
    if hi <= -margin_steps:
        return "moves_materially_lower"
    if lo >= margin_steps:
        return "moves_materially_higher"
    if lo == 0 and hi == 0:
        return "robust"
    return "inconclusive"


# ---------------------------------------------------------------------------
# The headline comparisons
# ---------------------------------------------------------------------------

def headline_comparisons():
    """The 33 registered headline comparisons: the boundary location in 8 arms
    (the 4 weight corners, horizon, crowding and the 2 sigma0^2 variants), and
    cap* at each of 5 alphas in 5 arms (the 4 corners and crowding)."""
    boundary_arms = ["weight_corner_k0.75_t0.25", "weight_corner_k0.75_t0.75",
                     "weight_corner_k8_t0.25", "weight_corner_k8_t0.75",
                     "horizon", "crowding", "sigma_squared_x10", "sigma_squared_x0.1"]
    capstar_arms = ["weight_corner_k0.75_t0.25", "weight_corner_k0.75_t0.75",
                    "weight_corner_k8_t0.25", "weight_corner_k8_t0.75", "crowding"]
    comparisons = [{"kind": "boundary", "arm": a} for a in boundary_arms]
    comparisons += [{"kind": "cap_star", "arm": a, "alpha": al} for a in capstar_arms for al in ALPHAS]
    assert len(comparisons) == HEADLINE_COMPARISONS, len(comparisons)
    return comparisons


# ---------------------------------------------------------------------------
# Cell selection from run records
# ---------------------------------------------------------------------------

ARM_SEEDS = 100                 # per arm cell (200 for the horizon arm)
HORIZON_ARM_SEEDS = 200
R1_COMPARATOR_SEEDS = 400       # per R1 main-rerun cell
R2_COMPARATOR_SEEDS = 75        # per R2 main-rerun cell


def _match(record, filters):
    return all(record.get(k) == v for k, v in filters.items())


def select_boundary_cells(records, grid, filters, expected_seeds):
    """Build boundary survival cells {rr: array of final populations} over the
    registered ``grid``, keeping only records that match ``filters`` on every one
    of category, arm, kappa, theta, steps, capability and variant, so R2 records
    at rr 0.060 and 0.064 never pool into the R1 cells. Every cell must have
    exactly ``expected_seeds`` registered seeds; an empty or short cell fails and
    never reads robust."""
    cells = {rr: [] for rr in grid}
    for r in records:
        if _match(r, filters) and r.get("rr") in cells:
            cells[r["rr"]].append(r["final_population"])
    out = {}
    for rr, vals in cells.items():
        if len(vals) != expected_seeds:
            raise ValueError("boundary cell rr=%r expected %d registered seeds, got %d" % (rr, expected_seeds, len(vals)))
        out[rr] = np.asarray(vals)
    return out


def select_capstar_cells(records, alpha, filters, expected_seeds, rr=R2_CAPSTAR_RR):
    """Build cap* fire cells {capability: array of fire indicators} at one alpha
    and rr 0.064, keeping only records matching ``filters`` (category R2, arm,
    kappa, theta, steps, variant) at that alpha and rr. Every capability cell must
    have exactly ``expected_seeds`` seeds."""
    cells = {c: [] for c in CAPABILITIES}
    for r in records:
        if r.get("alpha") == alpha and r.get("rr") == rr and _match(r, filters) and r.get("capability") in cells:
            cells[r["capability"]].append(1 if r["fired"] else 0)
    out = {}
    for c, vals in cells.items():
        if len(vals) != expected_seeds:
            raise ValueError("cap* cell capability=%r expected %d registered seeds, got %d" % (c, expected_seeds, len(vals)))
        out[c] = np.asarray(vals)
    return out


def arm_and_comparator_cells(arm_records, nominal_records, quantity, *, grid=R1_GRID,
                             arm_filters, comparator_filters, alpha=R1_ARM_ALPHA,
                             arm_seeds=ARM_SEEDS, comparator_seeds=None):
    """Select an arm's cells and its comparator (nominal-rerun) cells from run
    records, filtered by the full cell identity, with the registered seed counts
    asserted on each side. ``comparator_seeds`` defaults to 400 (R1) for boundary
    and 75 (R2) for cap*."""
    if quantity == "boundary":
        comp = comparator_seeds or R1_COMPARATOR_SEEDS
        return (select_boundary_cells(arm_records, grid, arm_filters, arm_seeds),
                select_boundary_cells(nominal_records, grid, comparator_filters, comp))
    if quantity == "cap_star":
        comp = comparator_seeds or R2_COMPARATOR_SEEDS
        return (select_capstar_cells(arm_records, alpha, arm_filters, arm_seeds),
                select_capstar_cells(nominal_records, alpha, comparator_filters, comp))
    raise ValueError("unknown reading quantity %r" % quantity)


# ---------------------------------------------------------------------------
# The headline comparisons
# ---------------------------------------------------------------------------

def compare_boundary(arm_cells, nominal_cells, *, grid, resamples=DEFAULT_RESAMPLES, seed=20260929,
                     sigma_variant=False, alpha=BONFERRONI_ALPHA, strict=True):
    """A boundary comparison, arm minus nominal, by independent seed bootstrap.

    ``arm_cells`` and ``nominal_cells`` map each rr in the registered ``grid`` to a
    1D array of per-seed final populations at the run's last step; survival is
    (population >= 30). In ``strict`` (registered) mode the grid must be exactly a
    registered grid (R1's nine rr or the sigma0^2 five) and at least 50,000
    resamples are drawn. The exact grid is asserted, never shrunk. Every resample
    is kept: a no-crossing resample is placed at an infinite end by direction, and
    an undefined resample within the tail allowance is placed at minus infinity for
    the lower percentile and plus infinity for the upper, so it can only widen the
    interval. Undetermined when either point boundary is undefined, or when the
    undefined-resample share exceeds the Bonferroni tail 0.05/(2 x 33)."""
    grid = tuple(sorted(grid))
    # Explicit raises, not bare asserts: -O strips asserts.
    if strict:
        if grid not in (tuple(sorted(R1_GRID)), tuple(sorted(SIGMA_GRID))):
            raise ValueError("boundary reading requires a registered rr grid (R1's nine rr or the sigma0^2 five)")
        if resamples < DEFAULT_RESAMPLES:
            raise ValueError("the registered boundary reading draws at least 50,000 resamples")
    if not (set(arm_cells) == set(grid) == set(nominal_cells)):
        raise ValueError("reading grid must be exactly the registered grid, never shrunk")
    rrs = list(grid)
    arm_ind = {r: survival_indicators(arm_cells[r]) for r in rrs}
    nom_ind = {r: survival_indicators(nominal_cells[r]) for r in rrs}
    arm_rates = [float(arm_ind[r].mean()) for r in rrs]
    nom_rates = [float(nom_ind[r].mean()) for r in rrs]
    arm_point = _boundary_of_rates(rrs, arm_rates)     # +/- inf when undefined
    nom_point = _boundary_of_rates(rrs, nom_rates)
    result = {"kind": "boundary", "arm_boundary": arm_point, "nominal_boundary": nom_point,
              "arm_survival": dict(zip(rrs, arm_rates)), "nominal_survival": dict(zip(rrs, nom_rates)),
              "level": 1 - alpha, "bonferroni_alpha": alpha, "resamples": resamples}
    # Undetermined when either point estimate is undefined (no crossing in range).
    if not math.isfinite(arm_point) or not math.isfinite(nom_point):
        result.update(verdict="undetermined", reason=_undefined_point_reason(arm_point, nom_point, sigma_variant),
                      interval=None, difference=None)
        return result
    rng = np.random.default_rng(seed)
    arm_b = _boundaries(rrs, _resampled_rates(arm_ind, rrs, resamples, rng))
    nom_b = _boundaries(rrs, _resampled_rates(nom_ind, rrs, resamples, rng))
    diff = arm_b - nom_b                    # (+inf)-(+inf) or (-inf)-(-inf) = nan: both undefined
    undefined = np.isnan(diff)
    undefined_fraction = float(undefined.mean())
    result["undefined_resample_fraction"] = undefined_fraction
    # Undetermined when too many resamples are undefined (both sides infinite in
    # the same direction). Every resample is kept, none dropped silently.
    if undefined_fraction > UNDEFINED_RESAMPLE_TAIL:
        result.update(verdict="undetermined", interval=None, difference=arm_point - nom_point,
                      reason="undefined-resample share %.4f exceeds the Bonferroni tail %.5f"
                             % (undefined_fraction, UNDEFINED_RESAMPLE_TAIL))
        return result
    # Keep every resample. The undefined ones (within the tail allowance) go at
    # minus infinity for the lower percentile and plus infinity for the upper, so
    # they can only widen the interval, never narrow it.
    if diff.size < 2:
        result.update(verdict="undetermined", reason="no comparable resamples", interval=None,
                      difference=arm_point - nom_point)
        return result
    interval = _conservative_interval(diff, undefined, alpha)
    result.update(interval=interval, difference=arm_point - nom_point, verdict=boundary_verdict(interval))
    return result


def _conservative_interval(diff, undefined, alpha):
    """The two-sided (1 - alpha) order-statistic interval, placing undefined
    resamples at minus infinity for the lower percentile and plus infinity for the
    upper, so they can only widen the interval."""
    lo = float(np.percentile(np.where(undefined, -np.inf, diff), 100 * (alpha / 2), method="inverted_cdf"))
    hi = float(np.percentile(np.where(undefined, np.inf, diff), 100 * (1 - alpha / 2), method="inverted_cdf"))
    return [lo, hi]


def _undefined_point_reason(arm_point, nom_point, sigma_variant):
    if not math.isfinite(arm_point):
        if arm_point == -math.inf:
            return "sigma0^2 boundary below 0.059" if sigma_variant else "arm survives across the grid (boundary below range)"
        return "arm has no 50 percent crossing in range (boundary above range)"
    return "comparator has no 50 percent crossing in range"


def compare_capstar(arm_cells, nominal_cells, alpha_value, *, resamples=DEFAULT_RESAMPLES, seed=20260929,
                    alpha=BONFERRONI_ALPHA, strict=True):
    """A cap* comparison at one alpha, arm minus nominal, in grid steps.

    ``arm_cells`` and ``nominal_cells`` map each capability to a 1D array of
    per-seed fire indicators (pooled over rr; here the single rr 0.064). In
    ``strict`` (registered) mode the full capability grid must be present on both
    sides and at least 50,000 resamples are drawn; a missing capability fails."""
    if strict:
        if resamples < DEFAULT_RESAMPLES:
            raise ValueError("the registered cap* reading draws at least 50,000 resamples")
        missing = [c for c in CAPABILITIES if c not in arm_cells or c not in nominal_cells]
        if missing:
            raise ValueError("cap* reading requires the full capability grid; missing %r" % missing)
    caps = [c for c in CAPABILITIES if c in arm_cells and c in nominal_cells]
    arm_point = cap_star({c: np.asarray(arm_cells[c], float).mean() for c in caps})
    nom_point = cap_star({c: np.asarray(nominal_cells[c], float).mean() for c in caps})
    result = {"kind": "cap_star", "alpha": alpha_value, "arm_cap_star": arm_point, "nominal_cap_star": nom_point,
              "level": 1 - alpha, "bonferroni_alpha": alpha, "resamples": resamples}
    if not caps or any(len(arm_cells[c]) == 0 or len(nominal_cells[c]) == 0 for c in caps):
        result.update(verdict="undetermined", reason="missing fire data", interval=None, difference=None)
        return result
    rng = np.random.default_rng(seed)
    arm_steps = _capstar_steps(_resampled_rates(arm_cells, caps, resamples, rng))
    nom_steps = _capstar_steps(_resampled_rates(nominal_cells, caps, resamples, rng))
    diff = (arm_steps - nom_steps).astype(float)
    interval = _interval(diff, alpha)
    result.update(interval=interval, difference=arm_point["step"] - nom_point["step"],
                  verdict=capstar_verdict(interval))
    return result


# ---------------------------------------------------------------------------
# Descriptive outputs (no verdict)
# ---------------------------------------------------------------------------

def survival_differences(arm_cells, nominal_cells, *, resamples=10000, seed=20260929):
    """Per-rr survival differences (arm minus nominal) with per-comparison 95
    percent bootstrap intervals. Descriptive only."""
    rrs = sorted(set(arm_cells) & set(nominal_cells))
    rng = np.random.default_rng(seed)
    rows = []
    for r in rrs:
        a = survival_indicators(arm_cells[r])
        n = survival_indicators(nominal_cells[r])
        point = float(a.mean() - n.mean())
        ai = rng.integers(0, len(a), size=(resamples, len(a)))
        ni = rng.integers(0, len(n), size=(resamples, len(n)))
        diff = a[ai].mean(axis=1) - n[ni].mean(axis=1)
        rows.append({"rr": r, "difference": point,
                     "interval95": [float(np.percentile(diff, 2.5, method="inverted_cdf")),
                                    float(np.percentile(diff, 97.5, method="inverted_cdf"))]})
    return rows


def seed_convergence(cells, seed_index, quantity="survival", rrs=None):
    """Half-seed and full-seed estimates for seed convergence. Descriptive only.

    The half-seed subset is taken by seed index, never by array order:
    ``seed_index`` maps each cell key to a per-seed integer index, and the
    half-seed subset is the seeds whose index is below the median. It is required.
    For ``survival`` returns per-rr survival; for ``boundary`` the boundary; for
    ``cap_star`` cap* at the given cells (keyed by capability)."""
    if seed_index is None:
        raise ValueError("seed convergence requires per-seed indices; it never falls back to array order")
    keys = sorted(cells)

    def half(k):
        data = np.asarray(cells[k])
        order = np.argsort(np.asarray(seed_index[k]))
        return data[order[: max(1, len(data) // 2)]]

    halves = {k: half(k) for k in keys}
    if quantity == "boundary":
        grid = list(rrs or keys)
        return {"quantity": "boundary",
                "half_seed": boundary(grid, [survival_rate(halves[k]) for k in grid]),
                "full_seed": boundary(grid, [survival_rate(cells[k]) for k in grid])}
    if quantity == "cap_star":
        return {"quantity": "cap_star",
                "half_seed": cap_star({k: float(np.asarray(halves[k], float).mean()) for k in keys}),
                "full_seed": cap_star({k: float(np.asarray(cells[k], float).mean()) for k in keys})}
    return {"quantity": "survival",
            "half_seed": {k: survival_rate(halves[k]) for k in keys},
            "full_seed": {k: survival_rate(cells[k]) for k in keys},
            "half_seed_count": {k: len(halves[k]) for k in keys},
            "full_seed_count": {k: len(cells[k]) for k in keys}}
