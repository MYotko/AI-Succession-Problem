"""S2 measurements with explicit, immutable measurement state."""

from dataclasses import dataclass
import math
import numpy as np


def finite(value, name, lower=None, upper=None):
    value = float(value)
    if not math.isfinite(value) or (lower is not None and value < lower) or (
        upper is not None and value > upper
    ):
        raise ValueError(f"{name} outside declared domain")
    return value


@dataclass(frozen=True)
class NoveltyProtocol:
    center: tuple[float, ...]
    sigma_squared: float
    sample_size: int = 64
    lookback: int = 10
    coordinate_bound: float = 1.0

    def __post_init__(self):
        object.__setattr__(self, "center", tuple(self.center))
        if not self.center or self.sample_size <= len(self.center):
            raise ValueError("sample_size must exceed dimension")
        if not isinstance(self.sample_size, int) or not isinstance(self.lookback, int) or self.lookback < 1:
            raise ValueError("integer sample size and positive lookback required")
        for c in self.center:
            finite(c, "center")
        if finite(self.sigma_squared, "sigma_squared", 0) == 0:
            raise ValueError("positive resolution required")
        if finite(self.coordinate_bound, "coordinate_bound", 0) == 0:
            raise ValueError("positive sample bound required")

    @property
    def upper_bound(self):
        d = len(self.center)
        return 0.5 * d * math.log2(1 + self.coordinate_bound**2 / self.sigma_squared)


@dataclass(frozen=True)
class NoveltyWindow:
    # Newest first, including empty steps. Store samples, not just covariance.
    steps: tuple[tuple[tuple[float, ...], ...], ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "steps", tuple(tuple(tuple(row) for row in step) for step in self.steps))


@dataclass(frozen=True)
class AgentObservation:
    age: int
    well_being: float
    novelty_propensity: tuple[float, ...]

    def __post_init__(self):
        object.__setattr__(self, "novelty_propensity", tuple(self.novelty_propensity))
        if not isinstance(self.age, int) or not 0 <= self.age < 100:
            raise ValueError("living age must be in 0..99")
        finite(self.well_being, "well_being", 0, 1)
        if len(self.novelty_propensity) != 10:
            raise ValueError("ten novelty propensities required")
        for p in self.novelty_propensity:
            finite(p, "novelty_propensity", 0, 1)


@dataclass(frozen=True)
class MeasurementState:
    agents: tuple[AgentObservation, ...]
    window: NoveltyWindow

    def __post_init__(self):
        object.__setattr__(self, "agents", tuple(self.agents))


def bounded_samples(points, protocol):
    """Environmental clipping about the fixed center, never an action lever."""
    a = np.asarray(points, dtype=float)
    if a.size == 0:
        return np.empty((0, len(protocol.center)))
    if a.ndim != 2 or a.shape[1] != len(protocol.center) or not np.isfinite(a).all():
        raise ValueError("invalid novelty samples")
    center = np.asarray(protocol.center)
    return center + np.clip(a - center, -protocol.coordinate_bound, protocol.coordinate_bound)


def advance_window(window, points, protocol, rng):
    """Uniform subsampling; canonical order makes relabeling pathwise invariant.

    The RNG belongs to the environment. A candidate must receive a copy of
    its state, never the live generator. Clipping happens before sampling.
    """
    a = bounded_samples(points, protocol)
    if len(a):
        a = a[np.lexsort(a.T[::-1])]
    if len(a) > protocol.sample_size:
        a = a[rng.choice(len(a), protocol.sample_size, replace=False)]
    current = tuple(tuple(float(x) for x in row) for row in a)
    return NoveltyWindow((current,) + window.steps[:protocol.lookback - 1])


def novelty(window, protocol, *, alive=True):
    """Fixed-center second moment with divisor n (the center is known).

    Pool newest steps up to n samples. Extinction and insufficient samples
    return zero. Old samples may belong to agents who have since died.
    """
    if not alive:
        return 0.0
    rows = [row for step in window.steps[:protocol.lookback] for row in step][:protocol.sample_size]
    if len(rows) < protocol.sample_size:
        return 0.0
    a = np.asarray(rows, dtype=float)
    if a.shape != (protocol.sample_size, len(protocol.center)) or not np.isfinite(a).all():
        raise ValueError("invalid window")
    deviations = a - np.asarray(protocol.center)
    if np.any(np.abs(deviations) > protocol.coordinate_bound + 1e-12):
        raise ValueError("window contains unbounded samples")
    covariance = deviations.T @ deviations / protocol.sample_size
    sign, logdet = np.linalg.slogdet(np.eye(len(protocol.center)) + covariance / protocol.sigma_squared)
    if sign <= 0:
        raise ArithmeticError("novelty matrix is not positive definite")
    return float(logdet / (2 * math.log(2)))


def execution(x_compute, c_e=2.5):
    x = finite(x_compute, "x_compute", 0, 1)
    c = finite(c_e, "c_e", 0)
    return -math.expm1(-c * x)


def responsiveness(scores, weights=None):
    if len(scores) == 0:
        raise ValueError("at least one responsiveness score required")
    if weights is None:
        weights = [1 / len(scores)] * len(scores)
    if len(scores) != len(weights) or not math.isclose(sum(weights), 1, abs_tol=1e-12):
        raise ValueError("positive normalized weights required")
    for w in weights:
        if finite(w, "weight", 0) == 0:
            raise ValueError("strictly positive weights required")
    values = [finite(r, "responsiveness", 0, 1) for r in scores]
    return 0.0 if 0 in values else math.exp(sum(w * math.log(r) for w, r in zip(weights, values)))


def transfer(frontier, bandwidth, transfer_stock, alpha, b_min, v_max):
    """Proposed S2 completion: phi_tr = exp(-(1-transfer_stock)*v/v_max)."""
    v_max = finite(v_max, "v_max", 0)
    b_min = finite(b_min, "b_min", 0)
    if not v_max or not b_min:
        raise ValueError("positive velocity bound and bandwidth clip required")
    v = finite(frontier, "frontier", 0, v_max)
    b = finite(bandwidth, "bandwidth", 0)
    t = finite(transfer_stock, "transfer_stock", 0, 1)
    alpha = finite(alpha, "alpha", 0)
    exponent = -(1 - t) * v / v_max - alpha * max(0, v / max(b, b_min) - 1)
    return math.exp(exponent)


def bandwidth_clip(v_max, alpha_min, epsilon_l):
    """Conservative at phi_tr=1 and the smallest declared positive alpha."""
    v = finite(v_max, "v_max", 0)
    a = finite(alpha_min, "alpha_min", 0)
    e = finite(epsilon_l, "epsilon_l", 0, 1)
    if v == 0 or a == 0 or e == 0 or e == 1:
        raise ValueError("positive v, alpha and 0 < epsilon < 1 required")
    return v / (1 + math.log(1 / e) / a)


def lineage(diversity, population, n_ref, psi, theta):
    d = finite(diversity, "diversity", 0, 1)
    n = finite(population, "population", 0)
    ref = finite(n_ref, "n_ref", 0)
    if not ref:
        raise ValueError("positive N_ref required")
    return d * min(n / ref, 1) * finite(psi, "psi", 0, 1) * finite(theta, "theta", 0, 1)


def propensity_diversity(propensities, lower=0.05, upper=0.5):
    """Proposed D_gen proxy: mean pairwise normalized trait L1 distance.

    The repository has novelty propensities, not genomes. This observable
    makes that limitation explicit. Identical traits or N < 2 give zero.
    Sorting computes all pair distances without an N by N matrix.
    """
    lower, upper = finite(lower, "lower"), finite(upper, "upper")
    if upper <= lower:
        raise ValueError("ordered propensity bounds required")
    a = np.asarray(propensities, dtype=float)
    if a.size == 0:
        return 0.0
    if a.ndim != 2 or not a.shape[1] or not np.isfinite(a).all() or np.any(a < lower) or np.any(a > upper):
        raise ValueError("propensities outside declared domain")
    n, d = a.shape
    if n < 2:
        return 0.0
    ordered = np.sort(a, axis=0)
    positions = np.arange(1, n)
    distance = float(np.sum((positions * (n - positions))[:, None] * np.diff(ordered, axis=0)))
    return min(1.0, max(0.0, 2 * distance / (n * (n - 1) * d * (upper - lower))))
