"""S3-S4 flow and normalized, unconditional discount arithmetic."""

from dataclasses import dataclass
import math
import numpy as np
from .measurements import finite


@dataclass(frozen=True)
class FlowParameters:
    lambda_n: float
    mu: float
    kappa: float
    epsilon_n: float
    epsilon_e: float
    epsilon_l: float
    h_e_min: float
    h_n_max: float

    def __post_init__(self):
        for name in ("lambda_n", "mu", "kappa", "epsilon_n", "epsilon_e", "epsilon_l"):
            if finite(getattr(self, name), name, 0) == 0:
                raise ValueError(f"{name} must be positive")
        finite(self.h_e_min, "h_e_min", 0, 1)
        finite(self.h_n_max, "h_n_max", 0)

    @property
    def extinction_flow(self):
        return self.lambda_n * math.log(self.epsilon_n) + self.mu * math.log(
            self.h_e_min + self.epsilon_e
        ) + self.kappa * math.log(self.epsilon_l)

    @property
    def upper_bound(self):
        return flow(self.h_n_max, 1, 1, self)


def flow(h_n, h_e, l_value, parameters):
    p = parameters
    n = finite(h_n, "H_N", 0, p.h_n_max)
    e = finite(h_e, "H_E", p.h_e_min, 1)
    l_value = finite(l_value, "L", 0, 1)
    return p.lambda_n * math.log(n + p.epsilon_n) + p.mu * math.log(e + p.epsilon_e) + p.kappa * math.log(l_value + p.epsilon_l)


def discount_factor(rho, delta=1.0):
    rho = finite(rho, "rho", 0)
    delta = finite(delta, "delta", 0)
    beta = math.exp(-rho * delta)
    if not 0 < beta < 1:
        raise ValueError("rho*delta must give 0 < beta < 1")
    return beta


@dataclass(frozen=True)
class ValueBound:
    value: float
    error: float = 0.0

    def __post_init__(self):
        finite(self.value, "value")
        finite(self.error, "error", 0)


def discounted_flow(flows, beta, continuation, *, step_errors=None):
    """(1-beta) sum_{t<T} beta**t u_t + beta**T C(X_T).

    C is already normalized. Inputs are unconditional expected flows, or
    individual paths including u_dagger after death. Error bounds add by
    the triangle inequality; sampling/model bias is the caller's burden.
    """
    beta = finite(beta, "beta", 0, 1)
    if beta == 1:
        raise ValueError("beta must be below one")
    values = [finite(u, "flow") for u in flows]
    errors = [0.0] * len(values) if step_errors is None else list(step_errors)
    if len(errors) != len(values):
        raise ValueError("one error bound per flow required")
    weights = [(1 - beta) * beta**t for t in range(len(values))]
    value = math.fsum(w * u for w, u in zip(weights, values)) + beta**len(values) * continuation.value
    error = math.fsum(w * finite(e, "step error", 0) for w, e in zip(weights, errors)) + beta**len(values) * continuation.error
    return ValueBound(value, error)


def domain_continuation(lower, upper):
    lower, upper = finite(lower, "lower"), finite(upper, "upper")
    if lower > upper:
        raise ValueError("reversed bounds")
    return ValueBound((lower + upper) / 2, (upper - lower) / 2)


def exact_continuation(kernel, living_flows, beta, extinction_flow):
    """Reduced killed-chain resolvent, including the absorbing flow forever."""
    from .spectral import killed_kernel
    q = killed_kernel(kernel)
    u = np.asarray(living_flows, dtype=float)
    if u.shape != (len(q),) or not np.isfinite(u).all() or not 0 <= beta < 1:
        raise ValueError("invalid continuation inputs")
    death = 1 - q.sum(axis=1)
    rhs = (1 - beta) * u + beta * death * finite(extinction_flow, "extinction flow")
    return np.linalg.solve(np.eye(len(q)) - beta * q, rhs)


def objective(discounted, lambda_f, theta):
    theta = finite(theta, "theta", 0, 1)
    return theta * finite(discounted, "D_rho") + (1 - theta) * finite(lambda_f, "Lambda_F")
