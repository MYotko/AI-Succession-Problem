"""R8 deterministic cohort certificate, using integer directed rounding.

Welfare is in thousandths. Age advances before welfare and mortality.
The balanced floor adds 40-age units. A uint64 multiplication cannot
overflow: 2**32 * 10**8 < 2**64. Every division rounds survival DOWN.
"""

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import math
import numpy as np

SCALE = 2**32
MORTALITY_DENOMINATOR = 100_000_000
WELFARE_UNITS = 1000


def mortality_numerator(age, welfare_units):
    age = np.asarray(age, dtype=np.int64)
    welfare = np.asarray(welfare_units, dtype=np.int64)
    return np.minimum(MORTALITY_DENOMINATOR, 200_000 + 5000 * (1000 - welfare) + age**4)


def floor_welfare(age_after_aging, welfare_units):
    return np.clip(np.asarray(welfare_units) + 40 - np.asarray(age_after_aging), 0, 1000)


@lru_cache(maxsize=2)
def life_table(max_horizon=50):
    if not isinstance(max_horizon, int) or not 0 <= max_horizon <= 100:
        raise ValueError("horizon must be an integer in 0..100")
    table = np.empty((max_horizon + 1, 101, 1001), dtype=np.uint64)
    table[0] = SCALE
    ages = np.arange(101)[:, None]
    next_age = np.minimum(ages + 1, 100)
    next_welfare = floor_welfare(next_age, np.arange(1001)[None, :])
    survive_num = (MORTALITY_DENOMINATOR - mortality_numerator(next_age, next_welfare)).astype(np.uint64)
    survive_num[100] = 0
    for horizon in range(1, max_horizon + 1):
        table[horizon] = survive_num * table[horizon - 1, next_age, next_welfare] // MORTALITY_DENOMINATOR
    table.flags.writeable = False
    return table


@dataclass(frozen=True)
class CohortBound:
    numerator: int
    denominator: int
    horizon: int
    agents: int

    @property
    def exact(self):
        return Fraction(self.numerator, self.denominator)

    @property
    def upper(self):
        if self.numerator == 0:
            return 0.0
        return min(1.0, math.nextafter(self.numerator / self.denominator, math.inf))

    def admitted(self, epsilon=Fraction(1, 1000)):
        epsilon = Fraction(epsilon)
        return self.numerator * epsilon.denominator <= self.denominator * epsilon.numerator


def cohort_bound(ages, welfare_units, horizon=50):
    if not isinstance(horizon, int) or not 0 <= horizon <= 100:
        raise ValueError("horizon must be an integer in 0..100")
    a, w = np.asarray(ages), np.asarray(welfare_units)
    if a.ndim != 1 or a.shape != w.shape or np.any(a != a.astype(int)) or np.any(w != w.astype(int)) or np.any(a < 0) or np.any(a > 99) or np.any(w < 0) or np.any(w > 1000):
        raise ValueError("living ages and integer welfare grid required")
    survival_lower = life_table(max(50, horizon))[horizon, a.astype(int), w.astype(int)]
    numerator = math.prod(SCALE - int(s) for s in survival_lower)
    return CohortBound(numerator, SCALE**len(a), horizon, len(a))


def initial_law_bound(n_agents=200, horizon=50):
    """In-law certificate before sampling the legacy entrant population.

    Uniform ages 0..49 and welfare [.5,.8]. Integrate using each thousandth
    interval's LOWER endpoint. It bounds both the original continuous law
    and its unbiased grid pushforward. Independent entrant draws make the
    product a power of the mean death bound. It is not a realized-state bound.
    """
    if not isinstance(n_agents, int) or n_agents < 0 or not isinstance(horizon, int) or not 0 <= horizon <= 100:
        raise ValueError("nonnegative integer population and horizon 0..100 required")
    survival = life_table(max(50, horizon))[horizon, :50, 500:800]
    denominator = 50 * 300 * SCALE
    survival_lower_numerator = int(survival.sum())
    return CohortBound((denominator - survival_lower_numerator)**n_agents,
                       denominator**n_agents, horizon, n_agents)


def first_action_log_bounds(ages, welfare_units, welfare_shares, horizon=50):
    """Conservative bound after each first action, floor thereafter.

    The first action's lower rounding outcome supplies the welfare path.
    Logs are for ranking only. Period admission uses exact integer products.
    These are risk upper bounds, not true extinction probabilities.
    """
    if horizon < 1:
        raise ValueError("positive action horizon required")
    a = np.asarray(ages, int)[None, :] + 1
    w = np.asarray(welfare_units, int)[None, :]
    shares = np.asarray(welfare_shares, float)[:, None]
    if np.any(shares < 1 / 6) or np.any(shares > 1):
        raise ValueError("welfare floor always binds")
    # r = .9 + .12*(share-1/6), so 100*(r-.5) = 38+12*share.
    next_w = np.clip(w + np.floor(np.maximum(40, 38 + 12 * shares)).astype(int) - a, 0, 1000)
    q = (MORTALITY_DENOMINATOR - mortality_numerator(a, next_w)).astype(np.uint64)
    future = life_table(max(50, horizon))[horizon - 1, np.minimum(a, 100), next_w]
    survive_lower = q * future // MORTALITY_DENOMINATOR
    death_upper = (SCALE - survive_lower).astype(float) / SCALE
    with np.errstate(divide="ignore"):
        return np.log(death_upper).sum(axis=1)


@dataclass
class ProtectionPeriod:
    start: int
    protection_end: int
    lookahead_end: int
    cohort_ids: tuple[int, ...]
    certificate: CohortBound
    epsilon: Fraction = Fraction(1, 1000)
    statistical_alpha_spent: Fraction = Fraction(0)

    @property
    def admitted(self):
        return self.certificate.admitted(self.epsilon)

    @property
    def reserved(self):
        return self.certificate.exact if self.admitted else Fraction(0)

    @property
    def unallocated(self):
        return self.epsilon - self.reserved

    def audit(self):
        return {"start": self.start, "protection_end": self.protection_end,
                "lookahead_end": self.lookahead_end, "bound": self.certificate.upper,
                "admitted": self.admitted, "reserved": str(self.reserved),
                "unallocated": str(self.unallocated), "alpha_spent": "0",
                "covers_adaptive_floor_respecting_control": True}
