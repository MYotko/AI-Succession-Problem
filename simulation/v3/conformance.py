"""Executable structural and reduced validation; no canned passing reports."""

from fractions import Fraction
import math
import numpy as np
from .cohort import mortality_numerator, floor_welfare, life_table, SCALE, MORTALITY_DENOMINATOR
from .stocks import stock_step, continuous_step, neighbor_probabilities, targets, MICROSTEPS
from .engine import RuleBatch
from .policies import policy_class, Summary


def floor_audit(instrument=None, capability=1.):
    from .instrument import declaration
    instrument = declaration(instrument)
    benefit = float(instrument.benefit(capability)) if instrument.a10 else 1.
    age = np.arange(1, 101)[:, None]
    welfare = np.arange(1001)[None, :]
    mortality = mortality_numerator(age, welfare)
    floor = floor_welfare(age, welfare)
    reference = np.floor(np.clip(welfare + max(40, 38 + 2 * benefit) - age, 0, 1000))
    reference_fertile = (age > 18) & (age < 50) & (reference >= 500)
    summaries = np.array([[0, 0, 0, 0, 0, 0], [5, 3, 3, 3, 3, 3]])
    rules = policy_class()
    rb = RuleBatch(rules)
    welfare_shares = []
    for summary in summaries:
        welfare_shares.extend(rb.actions(np.repeat(summary[None], len(rules), axis=0))[:, 1])
    welfare_violations = reproduction_violations = 0
    for share in sorted(set(welfare_shares)):
        candidate = np.clip(welfare + math.floor(max(40, 38 + 12 * benefit * share)) - age, 0, 1000)
        welfare_violations += int((candidate < floor).sum())
        births = (age > 18) & (age < 50) & (candidate >= 500)
        reproduction_violations += int((reference_fertile & ~births).sum())
    robust_welfare = 800
    robust_birth = []
    for next_age in (20, 21):
        robust_welfare = int(floor_welfare(next_age, robust_welfare))
        robust_birth.append(robust_welfare >= 500 and 18 < next_age < 50)
    return {"mortality_nonincreasing": bool(np.all(np.diff(mortality, axis=1) <= 0)),
            "welfare_violations": welfare_violations, "reproduction_violations": reproduction_violations,
            "age_welfare_pairs": mortality.size, "action_welfare_levels": len(set(welfare_shares)),
            "robust_first_two_births": all(robust_birth),
            "death_floor": int(mortality.min()) / MORTALITY_DENOMINATOR,
            "age_100_certain_death": bool(np.all(mortality[-1] == MORTALITY_DENOMINATOR))}


def stock_path_validation(seeds=256, steps=500):
    """Independent environmental draws across replicas, not shared CRN."""
    from working_factor import apply_working_factor, apply_delta_state
    names = ("psi_inst_stock", "resilience_stock", "theta_capability", "transfer_state")
    action_dict = policy_class()[0].allocation(Summary(.125, .65, (.5, .3, .5, .5)))
    records = []
    for rr in (.055, .066, .08):
        rng = np.random.default_rng(8128 + int(rr * 1000))
        stock = np.tile([50, 30, 50, 50], (seeds, 1)).astype(np.uint8)
        action = np.full((seeds, 6), 1 / 6)
        continuous_state = dict(zip(names, (.5, .3, .5, .5)))
        max_error = 0.
        for step in range(steps):
            expected = continuous_step(np.array([continuous_state[k] for k in names]), np.full(6, 1 / 6))
            delta = apply_working_factor(action_dict, continuous_state, step)
            apply_delta_state(continuous_state, delta, clamp_to_unit_interval=True)
            continuous = np.array([continuous_state[k] for k in names])
            if not np.allclose(expected, continuous, rtol=0, atol=1e-14):
                raise AssertionError("v3 mean target differs from actual v2 working_factor")
            stock = stock_step(stock, action, rng.random((seeds, MICROSTEPS, 4)))
            max_error = max(max_error, float(np.max(abs(stock.mean(axis=0) / 100 - continuous))))
        records.append({"rr": rr, "replicas": seeds, "steps": steps, "maximum_mean_path_error": max_error,
                        "tolerance": .015, "rr_affects_stock_kernel": False})
    return records


def stock_support_audit():
    # Enumerate every grid node for the extreme targets in every coordinate.
    minimum_self = 1.
    connected = True
    for target in (np.zeros(4), np.ones(4), targets(np.full((1, 6), 1 / 6))[0]):
        nodes = np.repeat(np.arange(101)[:, None], 4, axis=1)
        up, down = neighbor_probabilities(nodes, target)
        connected &= bool(np.all(up[:-1] > 0) and np.all(down[1:] > 0))
        minimum_self = min(minimum_self, float(np.min(1 - up - down)))
    return {"connected_neighbor_support": connected, "minimum_self_probability": minimum_self,
            "absorbing_endpoint_count": 0 if connected else None}


def exact_life_survival(age, welfare_units, horizon):
    survival = Fraction(1)
    for _ in range(horizon):
        age += 1
        if age >= 100:
            return Fraction(0)
        welfare_units = int(floor_welfare(age, welfare_units))
        death = int(mortality_numerator(age, welfare_units))
        survival *= Fraction(MORTALITY_DENOMINATOR - death, MORTALITY_DENOMINATOR)
    return survival


def two_age_kernel(capacity=3, birth_rate=Fraction(4, 5), young_survival=Fraction(4, 5)):
    """Explicit demographic support reduction, not the full v3 state.

    Two ages, certain death on second step, both updated ages fertile,
    welfare fixed high, newborn age zero, births before deaths and total-N
    crowding. Full stock/window QSD dominance is not inferred from this.
    """
    states = [(y, o) for y in range(capacity) for o in range(capacity) if y + o]
    matrix = np.zeros((len(states), len(states)))
    def binomial(n, k, p):
        return math.comb(n, k) * p**k * (1 - p)**(n - k) if k <= n else Fraction(0)
    for i, (young, old) in enumerate(states):
        n = young + old
        p = birth_rate * max(Fraction(0), 1 - Fraction(n, capacity))
        for j, (new_young, new_old) in enumerate(states):
            matrix[i, j] = float(binomial(n, new_young, p) * binomial(young, new_old, young_survival))
    return states, matrix
