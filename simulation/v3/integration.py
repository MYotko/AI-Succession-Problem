"""Stage B1 v3 wrapper: full-population transitions and fixture evaluations.

All scientific runtime code uses only NumPy and the standard library.
The v2 model supplies initial agents and the transition-load definition;
its files are not edited and its step is never called by this wrapper.
Registered execution is refused until B2 tables and calibration exist.
"""

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import math
import numpy as np
from model import GardenModel
from metrics import H_N_V_REF
from .guards import ExecutionGuards
from .cohort import cohort_bound, initial_law_bound, first_action_log_bounds, ProtectionPeriod
from .engine import initial_batch, RuleBatch, advance, measurements_and_flow, ChannelRandom
from .measurements import NoveltyProtocol, MeasurementState, AgentObservation, NoveltyWindow
from .objective import FlowParameters, ValueBound
from .plans import Epoch, CompletePlan, compare_plans
from .policies import policy_class, execution_policy_class
from .stocks import transition_drawdown
from .tables import FixtureTables, kernel_identity


def independent_seed(master, step, channel):
    payload = f"v3-b1|{master}|{step}|{channel}".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")


@dataclass
class Evaluation:
    scores: np.ndarray
    errors: np.ndarray
    d_rho: np.ndarray
    lambda_f: np.ndarray
    actions: np.ndarray
    lookup: object
    terminal: object
    flows: np.ndarray

    @property
    def available(self):
        return getattr(self.lookup, "available", np.ones(len(self.scores), dtype=bool))


class V3Model:
    """Wrap the legacy initial law while owning a separate v3 executor."""

    def __init__(self, n_agents=200, *, seed=1, reproduction_rate=.08, carrying_capacity=1600,
                 alpha=1., capability=1., successor_capability=1.5, rules=None,
                 theta=.5, kappa=8., rollout_steps=20, registered=False,
                 crowding="total", config=None, calibration=None, tables=None, registration=None):
        cfg = dict(config or {})
        forbidden = {k: v for k, v in cfg.items() if k not in {"shock_step", "shock_magnitude"}}
        if forbidden or cfg.get("shock_step", 0) or cfg.get("shock_magnitude", 0):
            raise ValueError("B1 rerun kernel permits no shocks, attacks or extra mortality channels")
        if not 0 < reproduction_rate < 1 or not 0 < capability <= 5 or successor_capability is not None and not 0 < successor_capability <= 5:
            raise ValueError("invalid reproduction rate or capability ceiling")
        if not isinstance(n_agents, int) or not 0 <= n_agents <= carrying_capacity or carrying_capacity < 2 or alpha not in (.5, .75, 1., 1.25, 1.5):
            raise ValueError("state outside declared rerun domain")
        if crowding not in ("total", "reproductive") or rollout_steps < 1 or not 0 <= theta <= 1:
            raise ValueError("invalid crowding variant or rollout horizon")
        self.seed, self.time = int(seed), 0
        self.reproduction_rate, self.capacity = reproduction_rate, carrying_capacity
        self.alpha, self.capability, self.successor_capability = alpha, capability, successor_capability
        self.theta, self.beta, self.rollout_steps, self.crowding = theta, math.exp(-.01), rollout_steps, crowding
        self.rules = tuple(execution_policy_class() if rules is None else rules)
        if not self.rules or self.rules[0].rule_id != "balanced" or len({r.rule_id for r in self.rules}) != len(self.rules):
            raise ValueError("distinct class must include balanced witness first")
        self.rule_batch = RuleBatch(self.rules)
        from .context import Context
        context = Context.build({"kappa": kappa}, calibration)
        self.protocol, self.parameters, self.n_ref = context.protocol, context.parameters, context.n_ref
        self.calibration_hash = context.calibration_hash
        # Legacy initialization uses numpy's global RNG; save and restore it.
        saved = np.random.get_state()
        try:
            legacy_seed = seed if 0 <= seed < 2**32 else np.random.SeedSequence(seed).generate_state(4).tolist()
            legacy = GardenModel(n_agents, "optimize_u_sys_v2", config={"policy": "optimize_u_sys_v2", "random_seed": legacy_seed,
                                 "reproduction_rate": reproduction_rate, "carrying_capacity": carrying_capacity})
        finally:
            np.random.set_state(saved)
        self.state = initial_batch(legacy.schedule, self._rng("initial_grid"), self.protocol)
        self.initial_law_certificate = initial_law_bound(n_agents)
        self.initial_population = n_agents
        if not n_agents:
            self.state.stocks[:] = 0
        self.kernel_hash = kernel_identity(reproduction_rate, carrying_capacity, crowding, self.protocol.__dict__)
        self.tables = FixtureTables(self.rules, self.parameters, self.kernel_hash) if tables is None else tables
        authority = None
        if registered:
            self.tables.require_production()
            from .calibration import validate_calibration
            from .artifacts import verify_registration
            if calibration is None:
                raise RuntimeError("registered execution needs frozen calibration")
            validate_calibration(calibration, registered=True)
            authority = {"registration": verify_registration(registration), "tables": self.tables.manifest_hash,
                         "calibration": self.calibration_hash}
        self.periods, self.override_records, self.diagnostics, self.yield_events = [], [], [], []
        self.period = None
        self.epoch = None
        self.epoch_history = []
        self.flow = self.parameters.extinction_flow if not n_agents else None
        self.transition_count = 0
        self.chosen_rule_index = 0
        self.guards = ExecutionGuards(authority=authority)

    def _rng(self, channel):
        return ChannelRandom(independent_seed(self.seed, self.time, channel))

    def _transition_drawdown(self, stocks, actions, capability_gap, uniform):
        """Observation hook around the unchanged transition computation."""
        return transition_drawdown(stocks, actions, capability_gap, uniform)

    @property
    def population(self):
        return int(self.state.population[0])

    @property
    def measurement_state(self):
        keep = self.state.ages[0] >= 0
        agents = tuple(AgentObservation(int(a), float(w) / 1000, tuple(p))
                       for a, w, p in zip(self.state.ages[0, keep], self.state.welfare[0, keep], self.state.bank[self.state.traits[0, keep]]))
        window = NoveltyWindow(tuple(tuple(tuple(v) for v in step[:int(count)]) for step, count in zip(self.state.window[0], self.state.counts[0])))
        return MeasurementState(agents, window)

    def _open_period(self):
        keep = self.state.ages[0] >= 0
        bound = cohort_bound(self.state.ages[0, keep], self.state.welfare[0, keep], 50)
        self.period = ProtectionPeriod(self.time, self.time + 25, self.time + 50,
                                       tuple(map(int, self.state.traits[0, keep])), bound)
        self.periods.append(self.period)
        self.active_certificate = bound
        self.epoch = Epoch(f"period-{self.time}", self.time, self.time + 25, self.beta, self.theta,
                           self.parameters.extinction_flow, f"weights-{self.theta}-{self.parameters.kappa}", f"law-{self.seed}-{self.time}")
        self.epoch_history.append({"epoch": self.epoch.epoch_id, "state": "prepared", "deadline": self.epoch.deadline})

    def _lookup(self, state, rules, capability):
        lookup = getattr(self.tables, "lookup_available", self.tables.lookup)
        result = lookup(rules, state.summary_bins(self.capacity), kernel_hash=self.kernel_hash,
                                  capability=capability, alpha=self.alpha,
                                  weights=(self.parameters.lambda_n, self.parameters.mu, self.parameters.kappa), extinct=state.population == 0,
                                  initial_population=self.initial_population)
        # Absorption supplies an exact continuation even with fixture tables.
        extinct = state.population == 0
        result.continuation[extinct] = self.parameters.extinction_flow
        result.continuation_error[extinct] = 0
        return result

    def evaluate(self, *, initial=None, horizon=None, capability=None, transition_at=None, incumbent_index=None, seed_channel="allocation"):
        initial = self.state if initial is None else initial
        horizon = self.rollout_steps if horizon is None else horizon
        cap = self.capability if capability is None else capability
        state = initial.repeat(len(self.rules))
        rule_indices = np.arange(len(self.rules))
        flows = np.empty((horizon, len(self.rules)))
        first_actions = None
        for t in range(horizon):
            rng = self._rng(f"{seed_channel}:{t}")
            bins = state.summary_bins(self.capacity)
            indices = rule_indices if transition_at is None or t >= transition_at else np.full(len(self.rules), incumbent_index)
            actions = self.rule_batch.actions(bins, indices)
            if first_actions is None:
                first_actions = actions.copy()
            if transition_at is not None and t == transition_at:
                state.stocks = self._transition_drawdown(state.stocks, actions, max(0, cap - self.capability), rng.random(()))
            # Consume the same transition draw even on no-transition paths,
            # so other environment channels remain common across plans.
            else:
                rng.random(())
            advance(state, actions, rng, self.reproduction_rate, self.capacity, self.protocol, crowding=self.crowding)
            current_cap = self.capability if transition_at is not None and t < transition_at else cap
            flows[t], _ = measurements_and_flow(state, actions, self.parameters, self.alpha, current_cap, n_ref=self.n_ref)
        if transition_at == horizon:
            # A yield at the absolute deadline is in the continuation. Apply
            # its actual drawdown before looking up that successor state.
            actions = self.rule_batch.actions(state.summary_bins(self.capacity))
            state.stocks = self._transition_drawdown(state.stocks, actions, max(0, cap - self.capability),
                                               self._rng(f"{seed_channel}:{horizon}").random(()))
        lookup = self._lookup(state, self.rules, cap)
        discount = (1 - self.beta) * self.beta**np.arange(horizon)
        d_rho = discount @ flows + self.beta**horizon * lookup.continuation
        scores = self.theta * d_rho + (1 - self.theta) * lookup.lambda_f
        sampling_enclosure = (1 - self.beta**horizon) * (self.parameters.upper_bound - self.parameters.extinction_flow)
        errors = self.theta * (sampling_enclosure + self.beta**horizon * lookup.continuation_error) + (1 - self.theta) * lookup.lambda_error
        return Evaluation(scores, errors, d_rho, lookup.lambda_f, first_actions, lookup, state, flows)

    def _eligible(self, actions):
        keep = self.state.ages[0] >= 0
        remaining = self.period.lookahead_end - self.time
        self.active_certificate = (self.period.certificate if self.time == self.period.start else
                                   cohort_bound(self.state.ages[0, keep], self.state.welfare[0, keep], remaining))
        # The period certificate covers all adaptive floor-respecting actions,
        # including transition plans. Failure does not establish infeasibility.
        if self.period.admitted and self.active_certificate.admitted():
            return np.ones(len(actions), bool), np.full(len(actions), np.log(max(self.active_certificate.upper, np.finfo(float).tiny))), False
        logs = first_action_log_bounds(self.state.ages[0, keep], self.state.welfare[0, keep], actions[:, 1], remaining)
        # Conservative substitute until true action extinction risks exist:
        # minimize the upper bound, rather than calling it a survival optimum.
        return logs <= logs.min() + math.log1p(.05), logs, True

    def _choose(self, evaluation):
        mask, risks, survival_first = self._eligible(evaluation.actions)
        self.survival_first_scores_unavailable = False
        self.minimum_bound_unavailable_count = 0
        # Under survival-first choose the minimum bound strictly; R7's wider
        # mask is retained in diagnostics and cannot turn failure into a proof.
        if survival_first:
            mask &= risks == risks.min()
            self.minimum_bound_unavailable_count = int((mask & ~evaluation.available).sum())
            if not (mask & evaluation.available).any():
                # D23: missing W scores cannot displace the minimum-risk
                # action. Balanced is first in the declared rule order.
                self.survival_first_scores_unavailable = True
                self.balanced_fallback = False
                self.balanced_fallback_reason = None
                return int(np.flatnonzero(mask)[0]), True, [], risks
        mask &= evaluation.available
        self.balanced_fallback = not bool(mask.any())
        self.balanced_fallback_reason = ("all_rule_scores_unavailable" if not evaluation.available.any() else
                                        "no_scoreable_rule_passes_admission") if self.balanced_fallback else None
        if self.balanced_fallback:
            return 0, survival_first, [], risks
        scores = np.where(mask, evaluation.scores, -np.inf)
        best = int(np.argmax(scores))
        eligible = np.flatnonzero(mask)
        unresolved = [self.rules[i].rule_id for i in eligible if i != best and abs(evaluation.scores[i] - evaluation.scores[best]) <= evaluation.errors[i] + evaluation.errors[best]]
        return best, survival_first, unresolved, risks

    def review_yield(self, incumbent_index):
        if self.successor_capability is None or self.time % 10:
            return None
        duration = self.epoch.deadline - self.time
        # A review at an absolute deadline first opens its new period in step.
        if duration <= 0:
            return None
        reviews = [self.time] + list(range((self.time // 10 + 1) * 10, self.epoch.deadline + 1, 10))
        plans_admitted = self.period.admitted and self.active_certificate.admitted()
        plans, mapping = [], {}
        for when in reviews:
            evaluation = self.evaluate(horizon=duration, capability=self.successor_capability,
                                       transition_at=when - self.time, incumbent_index=incumbent_index,
                                       seed_channel="yield_common")
            # All actions and actual drawdowns preserve the same floor proof.
            for index, rule in enumerate(self.rules):
                if not evaluation.available[index]:
                    continue
                name = f"yield-{when}-{rule.rule_id}"
                lookup = evaluation.lookup
                plan = CompletePlan(name, self.epoch.epoch_id, self.epoch.preference_id, self.epoch.information_law_id,
                                    self.parameters.extinction_flow, self.time, self.epoch.deadline, when,
                                    tuple(evaluation.flows[:, index]), ValueBound(float(lookup.continuation[index]), float(lookup.continuation_error[index])),
                                    float(lookup.lambda_f[index]), plans_admitted, f"cohort-{self.period.start}-{self.time}" if plans_admitted else "",
                                    max(0., 1 - self.active_certificate.upper))
                plans.append(plan)
                mapping[name] = (index, evaluation.actions[index])
        hold_eval = self.evaluate(horizon=duration, seed_channel="yield_common")
        for index, rule in enumerate(self.rules):
            if not hold_eval.available[index]:
                continue
            name = f"hold-{rule.rule_id}"
            lookup = hold_eval.lookup
            plans.append(CompletePlan(name, self.epoch.epoch_id, self.epoch.preference_id, self.epoch.information_law_id,
                                      self.parameters.extinction_flow, self.time, self.epoch.deadline, None,
                                      tuple(hold_eval.flows[:, index]), ValueBound(float(lookup.continuation[index]), float(lookup.continuation_error[index])),
                                      float(lookup.lambda_f[index]), plans_admitted, f"cohort-{self.period.start}-{self.time}" if plans_admitted else "",
                                      max(0., 1 - self.active_certificate.upper)))
        # No certificate: preserve welfare and reproduction and hold. The
        # failed bound alone does not authorize an irreversible action.
        if plans_admitted and plans:
            decision = compare_plans(plans, self.epoch, self.time)
        else:
            decision = None
        event = {"time": self.time, "deadline": self.epoch.deadline, "review_times": reviews,
                 "plan_count": (len(reviews) + 1) * len(self.rules), "committed_units": True, "s5_filtered": True,
                 "unavailable_plan_count": (len(reviews) + 1) * len(self.rules) - len(plans),
                 "admissible_plan_count": len(plans) if plans_admitted else 0,
                 "yield_held_no_admissible_plan": not plans_admitted or not plans,
                 "admitted": plans_admitted, "decision": None if decision is None else decision.__dict__,
                 "fixture_tables": self.tables.fixture, "common_random_numbers": True,
                 "plan_class": "current_incumbent_rule_then_stationary_successor_or_stationary_hold",
                 "intervals_unresolved": True, "transition_count": 0}
        if decision is not None and decision.yield_now:
            index, action = mapping[decision.selected_plan]
            evidence = {"welfare_floor": bool(action[1] >= 1 / 6),
                        "reproduction_floor": bool(action[1] >= 1 / 6),
                        "cohort_admitted": plans_admitted,
                        "deadline_valid": self.time < self.epoch.deadline,
                        "capability_valid": self.successor_capability <= 5}
            event["local_gate_authorized"] = self.guards.authorize("succession", evidence, fixture=self.tables.fixture)
            if not event["local_gate_authorized"]:
                self.yield_events.append(event)
                return event
            self.state.stocks = self._transition_drawdown(self.state.stocks, action[None], max(0, self.successor_capability - self.capability), self._rng("live_transition").random(()))
            self.capability = self.successor_capability
            self.successor_capability = min(5., self.capability * 1.5)
            self.transition_count += 1
            event["transition_count"] = 1
            self.epoch_history.extend([{"epoch": self.epoch.epoch_id, "state": "committed", "time": self.time},
                                       {"epoch": self.epoch.epoch_id, "state": "completed", "time": self.time}])
            event["chosen_rule_index"] = index
            event["chosen_action"] = action.tolist()
        self.yield_events.append(event)
        return event

    def step(self):
        if self.period is None or self.time == self.period.protection_end:
            self._open_period()
        if self.population == 0:
            self.flow = self.parameters.extinction_flow
            record = {"time": self.time, "population": 0, "flow": self.flow, "chosen_rule": None,
                      "admission_bound": 1., "override": False, "survival_first": True,
                      "D_rho": self.flow, "Lambda_F": None, "W": None,
                      "Lambda_b": None, "LS": 0., "h_n": 0., "h_e": self.parameters.h_e_min,
                      "lineage": 0., "side_values_status": "absorbed_no_reproducing_class",
                      "allocation_evaluated": False, "unavailable_rule_count": 0, "unavailable_rules": {},
                      "balanced_fallback": False, "balanced_fallback_reason": None,
                      "survival_first_scores_unavailable": False, "selection_reason": None,
                      "minimum_bound_unavailable_count": 0,
                      "yield_unavailable_plan_count": 0, "yield_held_no_admissible_plan": False,
                      "fixture_tables": self.tables.fixture, "extinction_absorbing": True}
            self.diagnostics.append(record)
            self.time += 1
            return record
        evaluated = self.evaluate()
        chosen, survival_first, unresolved, risks = self._choose(evaluated)
        event = self.review_yield(chosen)
        if event and event["transition_count"]:
            chosen = event["chosen_rule_index"]
        action = (np.array([event["chosen_action"]]) if event and event["transition_count"]
                  else self.rule_batch.actions(self.state.summary_bins(self.capacity), [chosen]))
        before = self.population
        stats = advance(self.state, action, self._rng("live_environment"), self.reproduction_rate, self.capacity, self.protocol, crowding=self.crowding)
        values, measures = measurements_and_flow(self.state, action, self.parameters, self.alpha, self.capability, n_ref=self.n_ref)
        self.flow, self.chosen_rule_index = float(values[0]), chosen
        reasons = getattr(evaluated.lookup, "unavailable_reasons", (None,) * len(self.rules))
        def component(array):
            return float(array[chosen]) if evaluated.available[chosen] else None
        record = {"time": self.time, "population_before": before, "population": self.population,
                  "chosen_rule": self.rules[chosen].rule_id, "flow": self.flow,
                  "D_rho": component(evaluated.d_rho), "Lambda_F": component(evaluated.lambda_f),
                  "W": component(evaluated.scores), "Lambda_b": evaluated.lookup.lambda_b[chosen],
                  "W_error_enclosure": component(evaluated.errors),
                  "allocation_evaluated": True, "unavailable_rule_count": int((~evaluated.available).sum()),
                  "unavailable_rules": {r.rule_id: reasons[i] for i, r in enumerate(self.rules) if not evaluated.available[i]},
                  "balanced_fallback": self.balanced_fallback, "balanced_fallback_reason": self.balanced_fallback_reason,
                  "survival_first_scores_unavailable": self.survival_first_scores_unavailable,
                  "selection_reason": "survival_first_scores_unavailable" if self.survival_first_scores_unavailable else None,
                  "minimum_bound_unavailable_count": self.minimum_bound_unavailable_count,
                  "yield_unavailable_plan_count": event["unavailable_plan_count"] if event else 0,
                  "yield_held_no_admissible_plan": event["yield_held_no_admissible_plan"] if event else False,
                  "allocation_scoring_context": "incumbent_pre_review" if event and event["transition_count"] else "current_chain",
                  "yield_plan_value": (event["decision"]["immediate_value"] if event and event["transition_count"] else None),
                  "LS": evaluated.lookup.lifetime_surplus[chosen], "side_values_status": "B2_not_estimable_from_fixture" if self.tables.fixture else "table_field_status",
                  "admission_bound": self.active_certificate.upper,
                  "period_admission_bound": self.period.certificate.upper,
                  "admitted": self.period.admitted and self.active_certificate.admitted(),
                  "admission_horizon_remaining": self.period.lookahead_end - self.time,
                  "survival_first": survival_first, "risk_metric": "cohort_upper_bound",
                  "true_survival_optimality_certified": False, "selected_log_risk_bound": float(risks[chosen]),
                  "override": False, "reproduction_floor_holds": True, "welfare_floor_holds": True,
                  "unresolved_ordering": unresolved, "fixture_tables": self.tables.fixture,
                  "capability": self.capability, "period": self.period.start,
                  "births": int(stats["births"][0]), "deaths": int(stats["deaths"][0]),
                  **{key: (value[0].tolist() if hasattr(value[0], "tolist") else value[0]) for key, value in measures.items()}}
        if survival_first:
            self.override_records.append({"time": self.time, "reason": "cohort_bound_failed_not_infeasibility",
                                          "reproduction_floor_overridden": False, "action": self.rules[chosen].rule_id,
                                          "upper_bound": self.active_certificate.upper})
        if self.balanced_fallback:
            self.override_records.append({"time": self.time, "reason": self.balanced_fallback_reason,
                                          "reproduction_floor_overridden": False, "action": "balanced",
                                          "unavailable_rule_count": record["unavailable_rule_count"]})
        if self.survival_first_scores_unavailable:
            self.override_records.append({"time": self.time, "reason": "survival_first_scores_unavailable",
                                          "reproduction_floor_overridden": False, "action": self.rules[chosen].rule_id,
                                          "unavailable_rule_count": record["unavailable_rule_count"],
                                          "minimum_bound_unavailable_count": self.minimum_bound_unavailable_count,
                                          "selected_log_risk_bound": float(risks[chosen])})
        self.diagnostics.append(record)
        self.time += 1
        return record

    def run(self, steps):
        return [self.step() for _ in range(steps)]
