"""A4 validated continuation support: pure, tested numerics.

D30, adopted 2026-09-29. This module holds only pure functions: seed
derivation and the collision guard, the living-source residual, the plain
C0 refit and the a priori width, the sufficient statistics, the plain
empirical Bernstein test with the visit-weighted safeguard, the FV tier
(delta-method and Fieller intervals with a scipy-free Student t quantile),
the M and M_FV counts, and the census fractions. Nothing here reads or
writes a file, launches a job, or computes a survival, extinction or fire
rate. It is blind by construction.

The plain certificate bounds theta_b, the per-trajectory mean residual, at
0.95 simultaneously over published plain cells. The visit-weighted mean is
only checked. Aggregation bias within a cell is not covered. The FV tier is
asymptotic and never certified.
"""
import hashlib
import math

import numpy as np

BETA = math.exp(-0.01)
ALPHA = 0.05
MIN_VISITS = 4
GROUPS = 32
PLAIN_RUNS_PER_GROUP = 64          # 2,048 independent trajectories per replicate
FV_PARTICLES = 256
FIT_REPLICATE = 0
VALIDATE_REPLICATES = (1, 2, 3)    # plain
FV_VALIDATE_REPLICATE = 1          # FV gets one validation replicate
CENSUS_REPLICATE = 0
FV_MIN_GROUPS = 16                 # contributing groups below this are unresolved
STREAM_TAGS = ("v3_R_fit", "v3_R_validate", "v3_R_census")

# Cell encoding. Fine A1 bins are the six-coordinate base-8 code. The plain
# tier merges every population-category-0 bin into one cell, above every
# fine code. The FV tier keeps the fine A1 bins.
RADIX = np.array([8 ** i for i in range(6)], dtype=np.int64)
COARSE_BASE = 8 ** 6
POP0_CELL = COARSE_BASE + 100


class SeedCollision(RuntimeError):
    """Raised, to halt the run, on any validation seed collision."""


class OutOfRange(RuntimeError):
    """Raised, to halt the run, when a flow or value leaves [lower, upper]."""


# ----------------------------------------------------------------------------
# Seeds
# ----------------------------------------------------------------------------

def _truncated_sha(*parts):
    """SHA-256 of the concatenated byte parts, truncated to 60 bits."""
    m = hashlib.sha256()
    for part in parts:
        m.update(part if isinstance(part, bytes) else str(part).encode("utf-8"))
    return int(m.hexdigest()[:15], 16)


def stream_seed(tag, a1_job_seed, replicate):
    """A validation stream seed: SHA-256 of the tag, A1 job seed and index."""
    return _truncated_sha(tag, a1_job_seed, replicate)


def fit_seed(a1_job_seed):
    return stream_seed("v3_R_fit", a1_job_seed, FIT_REPLICATE)


def validate_seed(a1_job_seed, replicate):
    return stream_seed("v3_R_validate", a1_job_seed, replicate)


def census_seed(a1_job_seed):
    return stream_seed("v3_R_census", a1_job_seed, CENSUS_REPLICATE)


def _planning_p1_seed(a1_job_seed):
    return _truncated_sha("planning_P1", a1_job_seed)


def _planning_p1_census_seed(a1_job_seed):
    return _truncated_sha("planning_P1_census", a1_job_seed)


def _planning_p3_seed(a1_job_seed, replicate):
    return _truncated_sha("planning_P3", a1_job_seed, replicate)


def derive_seeds(a1_job_seed, route="plain"):
    """Return the validation seeds this table uses, keyed by stream."""
    seeds = {"fit": fit_seed(a1_job_seed), "census": census_seed(a1_job_seed)}
    replicates = VALIDATE_REPLICATES if route == "plain" else (FV_VALIDATE_REPLICATE,)
    for r in replicates:
        seeds["validate_%d" % r] = validate_seed(a1_job_seed, r)
    return seeds


def assert_seeds_distinct(a1_job_seed, route="plain", probe_seeds=()):
    """Assert the streams are pairwise distinct and disjoint from every other
    seed A4 names. Halt on any collision. Returns the stream seeds."""
    seeds = derive_seeds(a1_job_seed, route)
    values = list(seeds.values())
    if len(set(values)) != len(values):
        raise SeedCollision("validation stream seeds are not pairwise distinct: %r" % seeds)
    forbidden = {int(a1_job_seed), _planning_p1_seed(a1_job_seed), _planning_p1_census_seed(a1_job_seed)}
    forbidden |= {_planning_p3_seed(a1_job_seed, r) for r in range(4)}
    forbidden |= {int(s) for s in probe_seeds}
    hits = {name: value for name, value in seeds.items() if value in forbidden}
    if hits:
        raise SeedCollision("validation seed collides with an A1, D26 probe or planning seed: %r" % hits)
    return seeds


# ----------------------------------------------------------------------------
# Cell codes and living-source residuals
# ----------------------------------------------------------------------------

def fine_codes(bins):
    return np.asarray(bins, dtype=np.int64).reshape(-1, 6) @ RADIX


def plain_cell_codes(bins):
    """Fine code, with every population-category-0 bin merged into POP0_CELL."""
    bins = np.asarray(bins, dtype=np.int64).reshape(-1, 6)
    return np.where(bins[:, 0] == 0, POP0_CELL, bins @ RADIX)


def is_low_population(code):
    """A cell is low-population when it is the merged population-0 cell or a
    fine bin whose population coordinate (the low base-8 digit) is zero."""
    code = int(code)
    return code >= COARSE_BASE or code % 8 == 0


def _lookup(codes, sorted_codes):
    if len(sorted_codes) == 0:
        return np.full(len(codes), -1)
    pos = np.searchsorted(sorted_codes, codes)
    safe = np.minimum(pos, len(sorted_codes) - 1)
    return np.where((pos < len(sorted_codes)) & (sorted_codes[safe] == codes), safe, -1)


def living_source_residuals(src_codes, nxt_codes, source_alive, dead, flows, value_by_code, lower):
    """The residual (1 - beta) f + beta V(next) - C(source) on living sources.

    Covered exactly when the source cell is published and the next state is
    extinct or lands in a published cell. Extinction takes the lower bound.
    This matches continuation.fit_transitions apart from the living-source
    restriction. Returns (residual, covered, source_index, sorted_codes).
    """
    src_codes = np.asarray(src_codes, dtype=np.int64)
    nxt_codes = np.asarray(nxt_codes, dtype=np.int64)
    dead = np.asarray(dead, dtype=bool)
    source_alive = np.asarray(source_alive, dtype=bool)
    flows = np.asarray(flows, dtype=float)
    codes = np.asarray(sorted(value_by_code), dtype=np.int64)
    vals = np.array([value_by_code[int(c)] for c in codes.tolist()], dtype=float)
    src = _lookup(src_codes, codes)
    nxt = _lookup(nxt_codes, codes)
    if not len(codes):
        return np.zeros(len(flows)), np.zeros(len(flows), dtype=bool), src, codes
    covered = source_alive & (src >= 0) & (dead | (nxt >= 0))
    next_value = np.where(dead, lower, vals[np.maximum(nxt, 0)])
    residual = (1 - BETA) * flows + BETA * next_value - vals[np.maximum(src, 0)]
    return residual, covered, src, codes


# ----------------------------------------------------------------------------
# The plain C0 refit
# ----------------------------------------------------------------------------

def refit_c0(src_codes, nxt_codes, source_alive, dead, flows, a1_published, lower, min_visits=MIN_VISITS):
    """The Bellman fixed point of the merged population-0 cell on the fitting
    replicate's covered living-source transitions.

    ``a1_published`` maps every published A1 non-population-0 cell code to its
    fixed value. Transitions into unpublished cells are excluded. The unique
    solution is C0 = a / (N - beta T), where T counts transitions that stay in
    the cell. C0 is published only with at least ``min_visits`` fitting visits.
    Returns a dict with the value, visit count N, T and the published flag.
    """
    src_codes = np.asarray(src_codes, dtype=np.int64)
    nxt_codes = np.asarray(nxt_codes, dtype=np.int64)
    dead = np.asarray(dead, dtype=bool)
    source_alive = np.asarray(source_alive, dtype=bool)
    flows = np.asarray(flows, dtype=float)
    pub_codes = np.asarray(sorted(a1_published), dtype=np.int64)
    pub_vals = np.array([a1_published[int(c)] for c in pub_codes.tolist()], dtype=float)
    src_is_cell = source_alive & (src_codes == POP0_CELL)
    nxt_pub = _lookup(nxt_codes, pub_codes)
    nxt_internal = (nxt_codes == POP0_CELL) & ~dead
    covered = src_is_cell & (dead | nxt_internal | (nxt_pub >= 0))
    n = int(covered.sum())
    if n == 0:
        return {"value": None, "visits": 0, "internal": 0, "published": False}
    internal = nxt_internal[covered]
    t = int(internal.sum())
    nxt_pub_cov = nxt_pub[covered]
    pub_contrib = np.zeros(n)
    has_pub = nxt_pub_cov >= 0
    if has_pub.any():
        pub_contrib[has_pub] = pub_vals[nxt_pub_cov[has_pub]]
    # Extinct -> lower; published cell -> its A1 value; internal entries are
    # excluded from the boundary sum below, so their contribution is unused.
    boundary_value = np.where(dead[covered], lower, pub_contrib)
    # Internal transitions contribute beta*C0 to the sum; they carry no boundary value.
    a = float((1 - BETA) * flows[covered].sum() + BETA * boundary_value[~internal].sum())
    denom = n - BETA * t
    if denom <= 0:
        raise OutOfRange("C0 denominator N - beta T is non-positive; check inputs")
    value = a / denom
    return {"value": value, "visits": n, "internal": t, "published": n >= min_visits}


# ----------------------------------------------------------------------------
# The a priori width and range checks
# ----------------------------------------------------------------------------

def check_in_range(values, lower, upper, what="value", tol=1e-9):
    values = np.asarray(values, dtype=float)
    if values.size and (values.min() < lower - tol or values.max() > upper + tol):
        raise OutOfRange("%s outside [%r, %r]: min %r max %r" % (what, lower, upper, float(values.min()), float(values.max())))
    return True


def row_width(flow_range, vmax, lower, upper):
    """w = (1 - beta) W + beta (vmax - lower). Requires vmax in [lower, upper].

    It bounds every per-trajectory mean residual m_i, provided every flow and
    every published value lies in [lower, upper]. Callers check those.
    """
    if not (lower - 1e-9 <= vmax <= upper + 1e-9):
        raise OutOfRange("vmax %r outside [%r, %r]" % (vmax, lower, upper))
    if flow_range <= 0:
        raise OutOfRange("non-positive flow range %r" % flow_range)
    return (1 - BETA) * flow_range + BETA * (vmax - lower)


# ----------------------------------------------------------------------------
# Sufficient statistics per cell
# ----------------------------------------------------------------------------

STAT_KEYS = ("n_traj", "sum_S", "sum_N", "sum_S2", "sum_N2", "sum_SN", "sum_m", "sum_m2")


def trajectory_sums(cell_index, traj, residuals, n_cells, count):
    """Trajectory-level sums per plain cell. Sums over disjoint trajectory sets
    add, so replicates combine by summation of these dicts."""
    keys = cell_index * count + traj
    total = n_cells * count
    N = np.bincount(keys, minlength=total).reshape(n_cells, count).astype(np.float64)
    S = np.bincount(keys, weights=residuals, minlength=total).reshape(n_cells, count)
    visited = N > 0
    m = np.where(visited, S / np.where(visited, N, 1), 0.0)
    return {"n_traj": visited.sum(axis=1), "sum_S": S.sum(axis=1), "sum_N": N.sum(axis=1),
            "sum_S2": (S ** 2).sum(axis=1), "sum_N2": (N ** 2).sum(axis=1), "sum_SN": (S * N).sum(axis=1),
            "sum_m": m.sum(axis=1), "sum_m2": (m ** 2).sum(axis=1)}


def group_sums(cell_index, group, residuals, n_cells, groups):
    """Group-level sums per FV cell: S_g and N_g over the 32 groups."""
    keys = cell_index * groups + group
    total = n_cells * groups
    N = np.bincount(keys, minlength=total).reshape(n_cells, groups).astype(np.float64)
    S = np.bincount(keys, weights=residuals, minlength=total).reshape(n_cells, groups)
    return {"N_g": N, "S_g": S}


def combine_stats(a, b):
    """Combine two trajectory-sum dicts (from disjoint replicates) by summation."""
    return {k: a[k] + b[k] for k in STAT_KEYS}


# ----------------------------------------------------------------------------
# The plain empirical Bernstein test
# ----------------------------------------------------------------------------

def empirical_bernstein(sum_m, sum_m2, n, width, M, tau, alpha=ALPHA):
    """Maurer and Pontil two-sided empirical Bernstein classification.

    ``width`` is the a priori interval length holding every m_i. Returns one of
    'certified', 'violation', 'unresolved', with mbar and rho.
    """
    n = int(n)
    if n < 2:
        return {"status": "unresolved", "reason": "n<2", "n": n, "mbar": None, "rho": None}
    mbar = sum_m / n
    var = max(0.0, (sum_m2 - sum_m ** 2 / n) / (n - 1))
    log_term = math.log(4 * M / alpha)
    rho = math.sqrt(2 * var * log_term / n) + 7 * width * log_term / (3 * (n - 1))
    lo, hi = mbar - rho, mbar + rho
    if lo >= -tau and hi <= tau:
        status = "certified"
    elif hi < -tau or lo > tau:
        status = "violation"
    else:
        status = "unresolved"
    return {"status": status, "n": n, "mbar": mbar, "rho": rho, "interval": [lo, hi]}


def visit_weighted_estimate(sum_S, sum_N):
    """The visit-weighted point estimate sum_S / sum_N (the safeguard)."""
    if sum_N <= 0:
        return None
    return sum_S / sum_N


def visit_weighted_ok(sum_S, sum_N, tau):
    estimate = visit_weighted_estimate(sum_S, sum_N)
    return estimate is not None and -tau <= estimate <= tau


# ----------------------------------------------------------------------------
# The Student t quantile, scipy-free
# ----------------------------------------------------------------------------

def _betacf(a, b, x):
    """Continued fraction for the incomplete beta (Lentz), Numerical Recipes."""
    MAXIT, EPS, FPMIN = 300, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < EPS:
            break
    return h


def regularized_incomplete_beta(a, b, x):
    """I_x(a, b), the regularized incomplete beta function."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln_beta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(ln_beta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def student_t_cdf(t, df):
    """CDF of the Student t distribution with df degrees of freedom."""
    x = df / (df + t * t)
    ib = regularized_incomplete_beta(df / 2.0, 0.5, x)
    return 1.0 - 0.5 * ib if t >= 0 else 0.5 * ib


def student_t_quantile(df, p):
    """The p-quantile of Student t with df degrees of freedom, by inverting the
    regularized incomplete beta CDF. Handles extreme upper tails."""
    if not 0.0 < p < 1.0:
        raise ValueError("quantile probability must lie in (0, 1)")
    if p == 0.5:
        return 0.0
    if p < 0.5:
        return -student_t_quantile(df, 1.0 - p)
    lo, hi = 0.0, 1.0
    for _ in range(200):
        if student_t_cdf(hi, df) >= p:
            break
        hi *= 2.0
    else:
        raise RuntimeError("could not bracket the t quantile")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if student_t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ----------------------------------------------------------------------------
# The FV tier
# ----------------------------------------------------------------------------

def delta_method_interval(S_g, N_g, t):
    """The delta-method ratio interval over groups with N_g >= 1.

    Returns (mu, half_width, n) with the interval [mu - half, mu + half], or
    None when fewer than two contributing groups.
    """
    S_g = np.asarray(S_g, dtype=float)
    N_g = np.asarray(N_g, dtype=float)
    mask = N_g >= 1
    n = int(mask.sum())
    if n < 2:
        return None
    S, N = S_g[mask], N_g[mask]
    total_N = N.sum()
    mu = S.sum() / total_N
    Nbar = total_N / n
    var = float(((S - mu * N) ** 2).sum()) / (n * (n - 1) * Nbar ** 2)
    var = max(0.0, var)
    half = t * math.sqrt(var)
    return {"mu": mu, "half_width": half, "n": n, "interval": [mu - half, mu + half]}


def fieller_interval(S_g, N_g, t):
    """The Fieller interval at critical value t over contributing groups.

    The set of mu with (Sbar - mu Nbar)^2 <= (t^2 / n)(s_SS - 2 mu s_SN +
    mu^2 s_NN). An unbounded set (Nbar^2 <= (t^2/n) s_NN) is returned as
    ``bounded=False``; callers count it unresolved.
    """
    S_g = np.asarray(S_g, dtype=float)
    N_g = np.asarray(N_g, dtype=float)
    mask = N_g >= 1
    n = int(mask.sum())
    if n < 2:
        return {"bounded": False, "n": n, "reason": "n<2"}
    S, N = S_g[mask], N_g[mask]
    Sbar, Nbar = S.mean(), N.mean()
    s_SS = float(S.var(ddof=1))
    s_NN = float(N.var(ddof=1))
    s_SN = float(((S - Sbar) * (N - Nbar)).sum() / (n - 1))
    k = t * t / n
    A = Nbar ** 2 - k * s_NN
    B = -2.0 * Sbar * Nbar + 2.0 * k * s_SN
    C = Sbar ** 2 - k * s_SS
    if A <= 0:
        return {"bounded": False, "n": n, "reason": "unbounded_set"}
    disc = B * B - 4 * A * C
    if disc < 0:
        # A>0 with no real roots: the quadratic is always positive, so no mu
        # satisfies the inequality. Treat as undefined, hence unresolved.
        return {"bounded": False, "n": n, "reason": "empty_set"}
    root = math.sqrt(disc)
    lo = (-B - root) / (2 * A)
    hi = (-B + root) / (2 * A)
    if lo > hi:
        lo, hi = hi, lo
    return {"bounded": True, "n": n, "interval": [lo, hi]}


def fv_cell_test(S_g, N_g, M_fv, tau, alpha=ALPHA, min_groups=FV_MIN_GROUPS):
    """Classify an FV cell: 'passed', 'unresolved' or 'violation'.

    Passes only when both the delta-method and Fieller intervals lie within
    [-tau, tau], using the Student t quantile at 1 - alpha/(2 M_fv) with n - 1
    degrees of freedom. Fewer than ``min_groups`` groups, or an unbounded
    Fieller set, is unresolved.
    """
    S_g = np.asarray(S_g, dtype=float)
    N_g = np.asarray(N_g, dtype=float)
    n = int((N_g >= 1).sum())
    if n < min_groups:
        return {"status": "unresolved", "reason": "fewer than %d groups" % min_groups, "n": n}
    t = student_t_quantile(n - 1, 1.0 - alpha / (2.0 * M_fv))
    delta = delta_method_interval(S_g, N_g, t)
    fieller = fieller_interval(S_g, N_g, t)
    if delta is None or not fieller["bounded"]:
        return {"status": "unresolved", "reason": "unbounded Fieller set" if delta is not None else "n<2",
                "n": n, "t": t, "delta": delta, "fieller": fieller}
    d_in = delta["interval"][0] >= -tau and delta["interval"][1] <= tau
    f_in = fieller["interval"][0] >= -tau and fieller["interval"][1] <= tau
    d_out = delta["interval"][1] < -tau or delta["interval"][0] > tau
    f_out = fieller["interval"][1] < -tau or fieller["interval"][0] > tau
    if d_in and f_in:
        status = "passed"
    elif d_out or f_out:
        status = "violation"
    else:
        status = "unresolved"
    return {"status": status, "n": n, "t": t, "delta": delta, "fieller": fieller}


# ----------------------------------------------------------------------------
# M and M_FV, from the pinned A1 publication
# ----------------------------------------------------------------------------

def published_bins(row):
    return [tuple(e["bin"]) for e in row.get("continuation", {}).get("entries", [])]


def count_M_plain(plain_rows):
    """M = sum over plain rows of (A1 published cells with population category
    above zero) plus one, the merged population-0 cell. Fixed before any new
    validation data exist."""
    total = 0
    for row in plain_rows:
        above = sum(1 for b in published_bins(row) if b[0] != 0)
        total += above + 1
    return total


def count_M_fv(fv_rows):
    """M_FV = the number of A1 published FV cells."""
    return sum(len(published_bins(row)) for row in fv_rows)


# ----------------------------------------------------------------------------
# The availability census
# ----------------------------------------------------------------------------

def census_fractions(endpoints, low_mask, support_codes, partition="plain"):
    """Fractions of living endpoints, and of low-population living endpoints,
    that fall outside the validated support.

    ``endpoints`` is an (n, 6) array of living endpoint bins; ``low_mask`` marks
    the low-population (population-category-0) living endpoints. ``support_codes``
    is the set of published cell codes under the same partition as the rerun
    lookup. Mirrors v3.unpublished_bins.endpoint_counts, restricted to living
    endpoints, with the low-population split A4 adds.
    """
    endpoints = np.asarray(endpoints, dtype=np.int64).reshape(-1, 6)
    low_mask = np.asarray(low_mask, dtype=bool)
    codes = plain_cell_codes(endpoints) if partition == "plain" else fine_codes(endpoints)
    domain = np.asarray(sorted(int(c) for c in support_codes), dtype=np.int64)
    miss = ~np.isin(codes, domain)
    living = len(endpoints)
    low = int(low_mask.sum())
    return {"living_endpoints": living, "low_population_living_endpoints": low,
            "fraction_among_living_endpoints": float(miss.mean()) if living else None,
            "fraction_among_low_population_living_endpoints": float(miss[low_mask].mean()) if low else None,
            "misses": int(miss.sum()), "low_misses": int(miss[low_mask].sum()) if low else 0}


def census_fractions_from_counts(cell_counts, support_codes, partition="plain"):
    """Fractions of living endpoints, and of low-population living endpoints,
    outside the validated support, from stored per-cell living counts.

    ``cell_counts`` maps a fine endpoint code to its living-endpoint count under
    the committed census law. A low-population endpoint has population category
    zero, i.e. its fine code is a multiple of 8. For the plain partition a code
    with population category zero belongs to the merged POP0_CELL; the FV
    partition uses the fine codes directly. ``support_codes`` is the set of
    published cell codes under the same partition as the rerun lookup.
    """
    support = {int(c) for c in support_codes}

    def inside(code):
        key = POP0_CELL if (partition == "plain" and code % 8 == 0) else code
        return key in support

    total = sum(cell_counts.values())
    total_low = sum(c for code, c in cell_counts.items() if int(code) % 8 == 0)
    outside = sum(c for code, c in cell_counts.items() if not inside(int(code)))
    low_outside = sum(c for code, c in cell_counts.items() if int(code) % 8 == 0 and not inside(int(code)))
    return {"living_endpoints": int(total), "low_population_living_endpoints": int(total_low),
            "fraction_among_living_endpoints": (outside / total) if total else None,
            "fraction_among_low_population_living_endpoints": (low_outside / total_low) if total_low else None,
            "misses": int(outside), "low_misses": int(low_outside)}


def census_floor(fractions, living_cap=0.02, low_cap=0.05, low_minimum=50):
    """A row passes when at most 2% of its living endpoints fall outside the
    validated support, and at most 5% of its low-population living endpoints do
    when it has at least 50 of them. Below 50 the low fraction is reported, not
    assessed. A row with no living endpoints has nothing to look up: it passes,
    reported as not assessed. Returns pass/fail with the assessed components."""
    living = fractions["fraction_among_living_endpoints"]
    low = fractions["fraction_among_low_population_living_endpoints"]
    n_living = fractions.get("living_endpoints")
    n_low = fractions.get("low_population_living_endpoints", 0)
    if not n_living:
        return {"passed": True, "assessed": False, "living_ok": True, "low_assessed": False,
                "low_ok": True, "living_fraction": None, "low_fraction": None,
                "living_endpoints": 0, "low_population_living_endpoints": n_low,
                "reason": "no living census endpoints"}
    living_ok = living is not None and living <= living_cap
    low_assessed = n_low >= low_minimum
    low_ok = (low is None) or (not low_assessed) or (low <= low_cap)
    return {"passed": bool(living_ok and low_ok), "assessed": True, "living_ok": bool(living_ok),
            "low_assessed": bool(low_assessed), "low_ok": bool(low_ok),
            "living_fraction": living, "low_fraction": low,
            "living_endpoints": int(n_living), "low_population_living_endpoints": n_low}
