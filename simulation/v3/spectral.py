"""Reduced-instance Perron calculations. Numerical checks, not enclosures."""

from dataclasses import dataclass
import math
import numpy as np


def killed_kernel(kernel):
    q = np.array(kernel, dtype=float, copy=True)
    if q.ndim != 2 or q.shape[0] != q.shape[1] or not len(q):
        raise ValueError("nonempty square killed kernel required")
    if not np.isfinite(q).all() or np.any(q < 0) or np.any(q.sum(axis=1) > 1 + 1e-13):
        raise ValueError("kernel must be substochastic")
    return q


def reachable(adjacency):
    reach = np.asarray(adjacency, dtype=bool).copy()
    np.fill_diagonal(reach, True)
    for k in range(len(reach)):
        reach |= reach[:, k, None] & reach[None, k, :]
    return reach


def primitive(kernel):
    """Strong connectivity and graph period one, without a spectral tolerance."""
    q = killed_kernel(kernel)
    edges = q > 0
    if not reachable(edges).all() or not edges.any():
        return False
    distances = [-1] * len(q)
    distances[0] = 0
    queue = [0]
    for i in queue:
        for j in np.flatnonzero(edges[i]):
            if distances[j] == -1:
                distances[j] = distances[i] + 1
                queue.append(int(j))
    period = 0
    for i, j in zip(*np.nonzero(edges)):
        period = math.gcd(period, distances[i] + 1 - distances[j])
    return period == 1


@dataclass(frozen=True)
class PerronResult:
    survival_eigenvalue: float
    zeta: float
    distribution: tuple[float, ...]
    lambda_f: float
    residual: float


def perron_flow(kernel, flows, reproducing_indices):
    """Normalized LEFT Perron vector of the declared canonical class.

    The caller establishes biological reproduction and domain dominance.
    Here we check that the supplied indices are a whole primitive SCC.
    Sterile states can receive exits but cannot return to this class.
    """
    q = killed_kernel(kernel)
    u = np.asarray(flows, dtype=float)
    indices = tuple(reproducing_indices)
    if u.shape != (len(q),) or not np.isfinite(u).all():
        raise ValueError("one finite flow per living state required")
    if not indices or len(set(indices)) != len(indices) or any(not isinstance(i, (int, np.integer)) or i < 0 or i >= len(q) for i in indices):
        raise ValueError("invalid reproducing indices")
    reach = reachable(q > 0)
    component = set(np.flatnonzero(reach[indices[0]] & reach[:, indices[0]]))
    if component != set(indices):
        raise ValueError("indices must specify a whole communicating class")
    block = q[np.ix_(indices, indices)]
    if not primitive(block):
        raise ValueError("canonical class must be irreducible and aperiodic")
    values, vectors = np.linalg.eig(block.T)
    index = int(np.argmax(values.real))
    eigenvalue = values[index]
    if abs(eigenvalue.imag) > 1e-10 or not 0 < eigenvalue.real < 1:
        raise ValueError("class must have a transient positive Perron root")
    vector = vectors[:, index].real
    if vector.sum() < 0:
        vector = -vector
    if np.any(vector <= 0):
        raise ArithmeticError("nonpositive Perron vector")
    vector /= vector.sum()
    root = float(eigenvalue.real)
    residual = float(np.max(np.abs(vector @ block - root * vector)))
    if residual > 1e-10:
        raise ArithmeticError("Perron residual too large")
    return PerronResult(root, 1 - root, tuple(vector), float(vector @ u[list(indices)]), residual)


def periodic_perron_flow(phase_kernels, phase_flows):
    """Unweighted mean of separately conditioned phase limits (S4).

    Inputs are canonical-class blocks at each phase, with equal dimension.
    This is not the Perron vector of a phase-augmented periodic matrix.
    """
    blocks = [killed_kernel(q) for q in phase_kernels]
    if not blocks or len(blocks) != len(phase_flows) or any(b.shape != blocks[0].shape for b in blocks):
        raise ValueError("matching phase kernels and flows required")
    means = []
    for start, flow in enumerate(phase_flows):
        product = np.eye(len(blocks[0]))
        for offset in range(len(blocks)):
            product = product @ blocks[(start + offset) % len(blocks)]
        means.append(perron_flow(product, flow, range(len(product))).lambda_f)
    return float(np.mean(means)), tuple(means)


def lifetime_surplus(kernel, flows, initial_law, extinction_flow):
    q = killed_kernel(kernel)
    p = np.asarray(initial_law, dtype=float)
    u = np.asarray(flows, dtype=float)
    if p.shape != (len(q),) or u.shape != p.shape or not np.isfinite(p).all() or not np.isfinite(u).all() or np.any(p < 0) or not np.isclose(p.sum(), 1):
        raise ValueError("invalid initial law or flows")
    if max(abs(np.linalg.eigvals(q))) >= 1:
        raise ValueError("lifetime surplus requires eventual extinction")
    return float(p @ np.linalg.solve(np.eye(len(q)) - q, u - extinction_flow))


def survival_conditioned_flow(kernel, flows, initial_law, tolerance=1e-12, max_steps=100000):
    """Lambda_b from the specified initial law, including sterile living states.

    Return only after the conditional distribution, not just its flow, is
    stationary. Periodic or nonconvergent cases raise instead of inventing a
    limit. This is a reduced diagnostic, not an estimator for the full chain.
    """
    q = killed_kernel(kernel)
    p, u = np.asarray(initial_law, float), np.asarray(flows, float)
    if p.shape != (len(q),) or u.shape != p.shape or not np.isfinite(p).all() or not np.isfinite(u).all() or np.any(p < 0) or not np.isclose(p.sum(), 1):
        raise ValueError("invalid law or flows")
    for _ in range(max_steps):
        next_p = p @ q
        if next_p.sum() == 0:
            raise ValueError("survival has zero probability")
        next_p /= next_p.sum()
        if np.max(abs(next_p - p)) < tolerance:
            return float(next_p @ u)
        p = next_p
    raise ArithmeticError("conditional limit did not converge")


def ranking_reversal(lambda_a, ls_a, lambda_b, ls_b):
    values = (lambda_a, ls_a, lambda_b, ls_b)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("finite diagnostics required")
    return (lambda_a - lambda_b) * (ls_a - ls_b) < 0
