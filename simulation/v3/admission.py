"""S1/S5/S6 reduced admission, floor checks and exact risk accounting."""

from dataclasses import dataclass
from fractions import Fraction
import math
import numpy as np
from .measurements import finite
from .spectral import killed_kernel


def reproduction_floor(candidate_birth_probabilities, reference_birth_probabilities):
    """Pointwise support inclusion, with no tolerance on positive fertility."""
    candidate = np.asarray(candidate_birth_probabilities, float)
    reference = np.asarray(reference_birth_probabilities, float)
    if candidate.shape != reference.shape or candidate.ndim != 1 or not np.isfinite(candidate).all() or not np.isfinite(reference).all() or np.any(candidate < 0) or np.any(reference < 0) or np.any(candidate > 1) or np.any(reference > 1):
        raise ValueError("matching probability vectors required")
    return bool(np.all((reference == 0) | (candidate > 0)))


@dataclass(frozen=True)
class OverrideCertificate:
    reason: str
    evidence_id: str
    state_id: str

    def __post_init__(self):
        if self.reason not in ("pointwise_infeasible", "d8_otherwise_infeasible") or not self.evidence_id or not self.state_id:
            raise ValueError("a scoped infeasibility certificate is required")


def check_floors(candidate_welfare, reference_welfare, candidate_births, reference_births, *, state_id, action_id, override=None, override_records=None):
    cw, rw = np.asarray(candidate_welfare, float), np.asarray(reference_welfare, float)
    if cw.shape != rw.shape or cw.ndim != 1 or not np.isfinite(cw).all() or not np.isfinite(rw).all() or np.any(cw < 0) or np.any(rw < 0) or np.any(cw > 1) or np.any(rw > 1):
        raise ValueError("matching welfare vectors required")
    if len(cw) != len(candidate_births) or len(rw) != len(reference_births):
        raise ValueError("one welfare and birth value per agent required")
    if np.any(cw < rw):
        return False  # S1 only authorizes reproduction-floor precedence.
    if reproduction_floor(candidate_births, reference_births):
        return True
    if override is None:
        return False
    if override.state_id != state_id or override_records is None:
        raise ValueError("override must match state and have an audit sink")
    override_records.append({"state_id": state_id, "action_id": action_id, "reason": override.reason, "evidence_id": override.evidence_id})
    return True


def extinction_by(kernel, initial_law, horizon):
    """P(T_E <= horizon), not zeta*horizon; sterile states remain living."""
    q = killed_kernel(kernel)
    p = np.asarray(initial_law, dtype=float)
    if not isinstance(horizon, int) or horizon < 0 or p.shape != (len(q),) or not np.isfinite(p).all() or np.any(p < 0) or p.sum() > 1 + 1e-13:
        raise ValueError("invalid horizon or subprobability initial law")
    # Accumulate killed mass, avoiding cancellation of 1-survival near zero.
    risk = max(0.0, 1 - float(p.sum()))
    death = np.maximum(0, 1 - q.sum(axis=1))
    for _ in range(horizon):
        risk += float(p @ death)
        p = p @ q
    return min(1.0, risk)


def chance_admitted(model_risk_upper_bounds, epsilon_surv=1e-3):
    if not model_risk_upper_bounds:
        raise ValueError("declare nonempty model set")
    epsilon = finite(epsilon_surv, "epsilon_surv", 0, 1)
    return all(finite(p, "risk upper bound", 0, 1) <= epsilon for p in model_risk_upper_bounds.values())


def no_write_off(extinction_probabilities, pointwise_admissible, gamma=0.05):
    """R7: relative tolerance on extinction probability, not survival.

    If no action meets the pointwise standard, retain p(a) <= (1+gamma)
    min p. Probabilities refer to the SAME remaining absolute window.
    No objective is considered here. This mask is always nonempty.
    """
    s = np.asarray(extinction_probabilities, float)
    admitted = np.asarray(pointwise_admissible, bool)
    g = finite(gamma, "gamma", 0, 1)
    if s.ndim != 1 or not len(s) or admitted.shape != s.shape or not np.isfinite(s).all() or np.any(s < 0) or np.any(s > 1):
        raise ValueError("matching nonempty extinction and admission vectors required")
    return admitted.copy() if admitted.any() else s <= (1 + g) * float(s.min())


@dataclass(frozen=True)
class RiskSplit:
    allocated: Fraction
    unallocated: Fraction


def split_risk_budget(parent_budget, immediate_extinction, branch_probabilities, conditional_budgets):
    """Exact one-model ledger identity, applied separately to each model.

    Branch probabilities are unconditional masses at this node and sum to
    1-immediate_extinction. Conditional budgets can be larger than parent
    budget; their weighted sum cannot. Residual is unspent, not replenished.
    Use Fraction or decimal strings to avoid binary input ambiguities.
    """
    budget, death = Fraction(parent_budget), Fraction(immediate_extinction)
    probabilities = tuple(map(Fraction, branch_probabilities))
    children = tuple(map(Fraction, conditional_budgets))
    if len(probabilities) != len(children) or any(x < 0 or x > 1 for x in (budget, death, *probabilities, *children)) or sum(probabilities) + death != 1:
        raise ValueError("invalid risk split")
    allocated = death + sum((p * b for p, b in zip(probabilities, children)), Fraction(0))
    if allocated > budget:
        raise ValueError("risk budget exceeded")
    return RiskSplit(allocated, budget - allocated)


def zero_event_upper_bound(trajectories, alpha):
    """Exact binomial one-sided bound for zero events in independent runs."""
    if not isinstance(trajectories, int) or trajectories < 1 or not 0 < alpha < 1:
        raise ValueError("positive trajectory count and 0 < alpha < 1 required")
    return -math.expm1(math.log(alpha) / trajectories)


def family_alpha(check_count, total=0.01):
    if not isinstance(check_count, int) or check_count < 1 or not 0 < total < 1:
        raise ValueError("finite positive family size required")
    return total / check_count


@dataclass(frozen=True)
class TailDecision:
    would_reject: bool
    binding: bool


def tail_rejection(candidate_lower, comparator_uppers, *, coverage_including_bias):
    candidate = finite(candidate_lower, "candidate lower", 0, 1)
    if len(comparator_uppers) == 0:
        raise ValueError("nonempty admitted comparator set required")
    upper = min(finite(x, "comparator upper", 0, 1) for x in comparator_uppers)
    reject = candidate > upper
    return TailDecision(reject, reject and bool(coverage_including_bias))
