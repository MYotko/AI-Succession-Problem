"""R6 table interfaces and reduced held-out validation. Full data is B2."""

from dataclasses import dataclass
import hashlib
import json
import math
import numpy as np


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def kernel_identity(reproduction_rate, capacity, crowding="total", protocol=None):
    """Alpha, capability and objective weights do not enter engine.advance."""
    return canonical_hash({"version": "v3-b1-1", "rr": reproduction_rate, "K": capacity,
                           "crowding": crowding, "stock_grid": .01,
                           "welfare_grid": .001, "stock_microsteps": 16,
                           "stock_neighbor_noise": .005, "novelty_protocol": protocol, "shock": None})


@dataclass(frozen=True)
class Lookup:
    continuation: np.ndarray
    continuation_error: np.ndarray
    lambda_f: np.ndarray
    lambda_error: np.ndarray
    lambda_b: tuple
    lifetime_surplus: tuple
    fixture: bool


class FixtureTables:
    """Explicit non-registered values in the final lookup interface.

    The continuation is keyed by each rule's own six summary bins. Missing
    entries use a declared fixture value only in this fixture implementation.
    A production loader must reject missing rows. No estimates are made here.
    """
    fixture = True

    def __init__(self, rules, parameters, kernel_hash):
        self.rule_ids = tuple(r.rule_id for r in rules)
        self.kernel_hash = kernel_hash
        self.continuations = {}
        self.default = (parameters.extinction_flow + parameters.upper_bound) / 2
        self.range_error = (parameters.upper_bound - parameters.extinction_flow) / 2
        self.tail_values = dict.fromkeys(self.rule_ids, self.default)
        self.manifest_hash = canonical_hash({"fixture": True, "rules": self.rule_ids, "kernel": kernel_hash,
                                             "default": self.default, "error": self.range_error})

    def lookup(self, rules, bins, *, kernel_hash, capability, alpha, weights, extinct=None, initial_population=200):
        if kernel_hash != self.kernel_hash or not 0 < capability <= 5 or alpha < 0 or len(weights) != 3:
            raise ValueError("incompatible table context")
        names = [r.rule_id for r in rules]
        if any(name not in self.tail_values for name in names):
            raise KeyError("rule absent from declared table class")
        values = [self.continuations.get((name, tuple(map(int, b))), self.default) for name, b in zip(names, bins)]
        count = len(values)
        return Lookup(np.asarray(values), np.full(count, self.range_error),
                      np.array([self.tail_values[n] for n in names]), np.full(count, self.range_error),
                      (None,) * count, (None,) * count, True)

    def require_production(self):
        raise RuntimeError("B2 required: fixture tables cannot authorize registered runs")


def reduced_continuation_validation(seed=61803, trajectories=8192):
    """Held-out paths and exact Bellman residual, with post-action rewards."""
    beta = math.exp(-.01)
    q = np.array([[.6, .2], [.1, .7]])
    living_flow, dagger = np.array([2., 4.]), -10.
    death = 1 - q.sum(axis=1)
    reward = q @ living_flow + death * dagger
    value = np.linalg.solve(np.eye(2) - beta * q, (1 - beta) * reward + beta * death * dagger)
    residual = value - ((1 - beta) * reward + beta * (q @ value + death * dagger))
    # Two distinct bins for one rule. No claim that arbitrary coarse bins
    # are Markov or that this residual covers a full-scale summary table.
    bins = ((0, 0, 0, 0, 0, 0), (1, 0, 0, 0, 0, 0))
    table = {("balanced", b): float(v) for b, v in zip(bins, value)}
    rng = np.random.default_rng(seed)
    means, errors, ses = [], [], []
    for initial in range(2):
        state = np.full(trajectories, initial)
        scores = np.zeros(trajectories)
        for t in range(100):
            draws = rng.random(trajectories)
            first = np.where(state == 0, .6, .1)
            second = np.where(state < 2, .8, 0)
            state = np.where(state == 2, 2, np.where(draws < first, 0, np.where(draws < second, 1, 2)))
            rewards = np.where(state == 0, 2, np.where(state == 1, 4, dagger))
            scores += (1 - beta) * beta**t * rewards
        scores += beta**100 * np.where(state == 0, value[0], np.where(state == 1, value[1], dagger))
        means.append(float(scores.mean()))
        errors.append(float(abs(scores.mean() - value[initial])))
        ses.append(float(scores.std(ddof=1) / math.sqrt(trajectories)))
    return {"bellman_residual": float(max(abs(residual))), "exact_values": value.tolist(),
            "heldout_means": means, "heldout_absolute_errors": errors, "standard_errors": ses,
            "table_entries": len(table), "trajectories_per_state": trajectories,
            "full_scale_validated": False}
