"""Declared 289-rule stationary class; no v2 executor dependency."""

from dataclasses import dataclass
from itertools import product
import bisect
from .measurements import finite

CHANNELS = ("compute", "bio_welfare", "novelty_agency", "institutional_capacity", "transfer_comprehension", "resilience")
POPULATION_CUTS = (0.05, 0.125, 0.25, 0.5, 1.0)
WELFARE_CUTS = (0.5, 0.65, 0.8)
STOCK_CUTS = (0.25, 0.5, 0.75)
BALANCED_SHARE = 1 / 6


@dataclass(frozen=True)
class Summary:
    population_ratio: float
    welfare: float
    stocks: tuple[float, float, float, float]

    def bins(self):
        n = finite(self.population_ratio, "N/K", 0)
        w = finite(self.welfare, "welfare", 0, 1)
        if len(self.stocks) != 4:
            raise ValueError("four stocks required")
        return (bisect.bisect_right(POPULATION_CUTS, n), bisect.bisect_right(WELFARE_CUTS, w), *(bisect.bisect_right(STOCK_CUTS, finite(s, "stock", 0, 1)) for s in self.stocks))


@dataclass(frozen=True)
class Rule:
    rule_id: str
    welfare_tier: int = 0
    profile: int = 0
    trigger: int = 0
    gain: int = 0
    balanced: bool = False

    def __post_init__(self):
        if not self.rule_id or self.welfare_tier not in range(4) or self.profile not in range(6) or self.trigger not in range(3) or self.gain not in range(4):
            raise ValueError("rule outside finite parameter grid")

    def allocation(self, summary):
        bins = summary.bins()
        if self.balanced:
            shares = [BALANCED_SHARE] * 6
        else:
            welfare = (BALANCED_SHARE, 0.25, 0.4, 0.6)[self.welfare_tier]
            stress = bins[0] <= self.trigger or bins[1] == 0 or min(bins[2:]) < self.trigger
            if stress:
                welfare += (1 - welfare) * (0.25, 0.5, 0.75, 1.0)[self.gain]
            # Profile zero is uniform; the other five emphasize one of the
            # non-welfare channels. No direct novelty-variance control.
            proportions = [0.2] * 5 if self.profile == 0 else [0.6 if i == self.profile - 1 else 0.1 for i in range(5)]
            shares = [(1 - welfare) * p for p in proportions]
            shares.insert(1, welfare)
        action = {f"x_{key}": float(x) for key, x in zip(CHANNELS, shares)}
        action.update(c_protective=0.3, c_suppressive=0.1)
        return action


def policy_class():
    return (Rule("balanced", balanced=True),) + tuple(
        Rule(f"w{w}_p{p}_t{t}_g{g}", w, p, t, g)
        for w, p, t, g in product(range(4), range(6), range(3), range(4))
    )


def execution_policy_class():
    """R5/R11, 2026-09-27: 25 rules frozen before any table estimate.

    Retain every base welfare tier and residual profile, fix trigger=1 and
    gain=3 (full welfare under stress), and retain the balanced witness.
    Full 289-rule class remains available for comparisons and cost audits.
    """
    return tuple(r for r in policy_class() if r.balanced or (r.trigger == 1 and r.gain == 3))
