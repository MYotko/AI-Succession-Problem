"""S7 comparison of complete plans, including transition and recovery flows.

No separate Gamma argument is accepted. The successor plan's flows and
continuation must already include disruption. Plan construction and S5
evidence verification belong to Stage B.
"""

from dataclasses import dataclass
from .measurements import finite
from .objective import ValueBound, discounted_flow
from .admission import no_write_off


@dataclass(frozen=True)
class Epoch:
    epoch_id: str
    origin: int
    deadline: int
    beta: float
    theta: float
    extinction_flow: float
    preference_id: str
    information_law_id: str

    def __post_init__(self):
        if not self.epoch_id or not self.preference_id or not self.information_law_id or not isinstance(self.origin, int) or not isinstance(self.deadline, int) or self.deadline < self.origin or not 0 < self.beta < 1:
            raise ValueError("invalid commitment epoch")
        finite(self.theta, "theta", 0, 1)
        finite(self.extinction_flow, "extinction_flow")


@dataclass(frozen=True)
class CompletePlan:
    plan_id: str
    epoch_id: str
    preference_id: str
    information_law_id: str
    extinction_flow: float
    start: int
    terminal_time: int
    first_yield: int | None
    flows: tuple[float, ...]
    continuation: ValueBound
    lambda_f: float
    admitted: bool
    admission_evidence: str
    survival_probability: float
    transition_included: bool = True


@dataclass(frozen=True)
class YieldDecision:
    yield_now: bool
    selected_plan: str
    best_waiting_plan: str | None
    immediate_value: float | None
    waiting_value: float | None
    survival_first: bool


def plan_value(plan, epoch, now):
    if (plan.epoch_id != epoch.epoch_id or plan.preference_id != epoch.preference_id or plan.information_law_id != epoch.information_law_id or plan.extinction_flow != epoch.extinction_flow):
        raise ValueError("plans must share committed units and information law")
    if not isinstance(now, int) or not epoch.origin <= now <= epoch.deadline or plan.start != now or not now <= plan.terminal_time <= epoch.deadline or len(plan.flows) != plan.terminal_time - now:
        raise ValueError("complete plan must respect the absolute deadline")
    if plan.first_yield is not None and (not isinstance(plan.first_yield, int) or not now <= plan.first_yield <= plan.terminal_time or not plan.transition_included):
        raise ValueError("yield must include simulated transition and recovery")
    if not plan.plan_id or (plan.admitted and not plan.admission_evidence):
        raise ValueError("admitted plans require S5 evidence")
    finite(plan.survival_probability, "survival probability", 0, 1)
    finite(plan.lambda_f, "Lambda_F")
    d = discounted_flow(plan.flows, epoch.beta, plan.continuation)
    # The elapsed prefix is common and cancels. Only D's suffix coefficient
    # decays; the long-run coefficient remains the epoch's original weight.
    weight = epoch.theta * epoch.beta**(now - epoch.origin)
    return ValueBound(weight * d.value + (1 - epoch.theta) * plan.lambda_f, weight * d.error)


def compare_plans(plans, epoch, now, gamma=0.05):
    plans = tuple(plans)
    if not plans or len({p.plan_id for p in plans}) != len(plans):
        raise ValueError("nonempty, distinct complete plans required")
    values = {p.plan_id: plan_value(p, epoch, now).value for p in plans}
    feasible = [p for p in plans if p.admitted]
    survival_first = not feasible
    if survival_first:
        mask = no_write_off([1 - p.survival_probability for p in plans], [False] * len(plans), gamma)
        feasible = [p for p, keep in zip(plans, mask) if keep]
    immediate = [p for p in feasible if p.first_yield == now]
    waiting = [p for p in feasible if p.first_yield != now]
    def key(p):
        # Latest stopping time at exact ties, then stable plan ID.
        return (values[p.plan_id], epoch.deadline if p.first_yield is None else p.first_yield, p.plan_id)
    best_now = max(immediate, key=key) if immediate else None
    best_wait = max(waiting, key=key) if waiting else None
    fire = best_now is not None and (best_wait is None or values[best_now.plan_id] > values[best_wait.plan_id])
    chosen = best_now if fire else best_wait
    return YieldDecision(fire, chosen.plan_id, best_wait.plan_id if best_wait else None, values[best_now.plan_id] if best_now else None, values[best_wait.plan_id] if best_wait else None, survival_first)
