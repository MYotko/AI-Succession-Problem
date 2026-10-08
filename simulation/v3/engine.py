"""Vectorized full-population v3 transitions, shared by live and rollout paths.

Batch rows are independent candidate chains coupled by common random
numbers. Age, welfare, propensity indices and full novelty windows are
retained for each chain. No aggregate population projector is used.
"""

from dataclasses import dataclass
import numpy as np
from .cohort import mortality_numerator, MORTALITY_DENOMINATOR
from .measurements import NoveltyProtocol, bandwidth_clip
from .policies import POPULATION_CUTS, WELFARE_CUTS, STOCK_CUTS
from .stocks import stock_step, MICROSTEPS
from .instrument import R4


class ChannelRandom:
    """One independent stream per draw channel; prefixes survive shape changes.

    Instantiate afresh for each absolute rollout step. Unlike one sequential
    generator, a different candidate population cannot shift other channels.
    """
    def __init__(self, seed):
        self.seed, self.channel = int(seed), 0

    def _generator(self):
        self.channel += 1
        return np.random.default_rng((self.seed + self.channel * 0x9E3779B97F4A7C15) % 2**64)

    def random(self, *args, **kwargs):
        return self._generator().random(*args, **kwargs)

    def integers(self, *args, **kwargs):
        return self._generator().integers(*args, **kwargs)

    def uniform(self, *args, **kwargs):
        return self._generator().uniform(*args, **kwargs)

    def normal(self, *args, **kwargs):
        return self._generator().normal(*args, **kwargs)


def randomized_units(values, scale, uniforms):
    values = np.asarray(values) * scale
    lower = np.floor(values)
    return (lower + (uniforms < values - lower)).astype(np.int16)


@dataclass
class PopulationBatch:
    ages: np.ndarray
    welfare: np.ndarray  # integer thousandths, -1 age denotes empty slot
    traits: np.ndarray  # indices into complete propensity bank
    bank: np.ndarray
    stocks: np.ndarray  # integer hundredths
    window: np.ndarray  # row, step (newest first), sample, coordinate
    counts: np.ndarray
    h_n: np.ndarray
    frontier_history: np.ndarray | None = None

    @property
    def population(self):
        return (self.ages >= 0).sum(axis=1)

    def copy_rows(self, indices):
        rows = np.asarray(indices, int)
        return PopulationBatch(self.ages[rows].copy(), self.welfare[rows].copy(),
                               self.traits[rows].copy(), self.bank,
                               self.stocks[rows].copy(), self.window[rows].copy(),
                               self.counts[rows].copy(), self.h_n[rows].copy(),
                               **({"frontier_history": self.frontier_history[rows].copy()} if self.frontier_history is not None else {}))

    def repeat(self, count):
        if len(self.ages) != 1:
            raise ValueError("broadcast starts from one live state")
        return self.copy_rows(np.zeros(count, int))

    def summary_bins(self, capacity):
        n = self.population
        welfare = np.sum(np.where(self.ages >= 0, self.welfare, 0), axis=1) / np.maximum(n, 1) / 1000
        return np.column_stack((np.searchsorted(POPULATION_CUTS, n / capacity, side="right"),
                                np.searchsorted(WELFARE_CUTS, welfare, side="right"),
                                np.searchsorted(STOCK_CUTS, self.stocks / 100, side="right")))


def initial_batch(agents, rng, protocol):
    n = len(agents)
    ages = np.array([[a.age for a in agents]], dtype=np.int16).reshape(1, n)
    raw_welfare = np.array([a.well_being for a in agents])
    welfare = randomized_units(raw_welfare, 1000, rng.random(n)).reshape(1, n)
    bank = np.array([a.novelty_propensity for a in agents], dtype=float).reshape(n, 10)
    return PopulationBatch(ages, welfare, np.arange(n).reshape(1, n), bank,
                           np.array([[50, 30, 50, 50]], dtype=np.uint8),
                           np.zeros((1, protocol.lookback, protocol.sample_size, 10)),
                           np.zeros((1, protocol.lookback), dtype=np.int16), np.zeros(1))


class RuleBatch:
    def __init__(self, rules):
        self.rules = tuple(rules)
        self.welfare = np.array([(1 / 6, .25, .4, .6)[r.welfare_tier] for r in rules])
        self.trigger = np.array([r.trigger for r in rules])
        self.gain = np.array([(.25, .5, .75, 1)[r.gain] for r in rules])
        self.balanced = np.array([r.balanced for r in rules])
        self.profiles = np.array([[.2] * 5 if r.profile == 0 else [.6 if i == r.profile - 1 else .1 for i in range(5)] for r in rules])

    def actions(self, bins, rule_indices=None):
        ix = np.arange(len(self.rules)) if rule_indices is None else np.asarray(rule_indices, int)
        b = np.asarray(bins)
        stress = (b[:, 0] <= self.trigger[ix]) | (b[:, 1] == 0) | (b[:, 2:].min(axis=1) < self.trigger[ix])
        welfare = self.welfare[ix] + stress * self.gain[ix] * (1 - self.welfare[ix])
        remainder = (1 - welfare[:, None]) * self.profiles[ix]
        actions = np.column_stack((remainder[:, 0], welfare, remainder[:, 1:]))
        actions[self.balanced[ix]] = 1 / 6
        return actions


def advance(batch, actions, rng, reproduction_rate, capacity, protocol, *, crowding="total", independent=False,
            capability=1., instrument=R4):
    """P5 order: age, welfare, births, deaths; then stocks and measurements.

    Births by dying parents count. Births are not immigration: an empty
    chain has no parents and remains empty. Stock changes cannot kill.
    All environmental draws are independent by channel, shared across rows.
    """
    if instrument.a10:
        instrument.require_capability(capability)
        if batch.frontier_history is None:
            raise ValueError("A10 advance requires initialized pace history")
    actions = np.asarray(actions, float)
    if actions.shape != (len(batch.ages), 6) or not np.isfinite(actions).all() or np.any(actions < 0) or not np.allclose(actions.sum(axis=1), 1) or np.any(actions[:, 1] < 1 / 6):
        raise ValueError("invalid allocation or welfare floor violation")
    if not 0 < reproduction_rate < 1 or capacity < 2 or crowding not in ("total", "reproductive"):
        raise ValueError("invalid declared demographic kernel")
    rows, width = batch.ages.shape
    draw_shape = (rows, width) if independent else (width,)
    alive = batch.ages >= 0
    count = alive.sum(axis=1)
    ages = np.where(alive, batch.ages + 1, 0)
    increment = np.maximum(40, 38 + 12 * actions[:, 1])[:, None]
    if instrument.a10:
        increment = np.maximum(40, 38 + 12 * instrument.benefit(capability) * actions[:, 1])[:, None]
    proposed = np.clip(batch.welfare + increment - ages, 0, 1000)
    lower = np.floor(proposed)
    welfare = (lower + (rng.random(draw_shape) < proposed - lower)).astype(np.int16)
    # Sample the integer mortality law exactly. A floating threshold on a
    # finite uniform grid could round the effective probability upward.
    mortality = mortality_numerator(ages, welfare)
    fertile = alive & (ages > 18) & (ages < 50) & (welfare >= 500)
    crowd = count if crowding == "total" else (alive & (ages > 18) & (ages < 50)).sum(axis=1)
    p_birth = reproduction_rate * np.maximum(0, 1 - crowd / capacity)
    births = (fertile & (rng.random(draw_shape) < p_birth[:, None])).sum(axis=1)
    surviving = alive & (rng.integers(0, MORTALITY_DENOMINATOR, draw_shape) >= mortality)
    survivors = surviving.sum(axis=1)
    new_count = survivors + births
    new_width = int(new_count.max(initial=0))
    if new_width > 2 * capacity and crowding == "total":
        raise ArithmeticError("total-crowding support exceeded 2K")
    # Keep survivor order and append newborns; every row remains compact.
    new_ages = np.full((rows, new_width), -1, dtype=np.int16)
    new_welfare = np.zeros((rows, new_width), dtype=np.int16)
    new_traits = np.zeros((rows, new_width), dtype=np.int32)
    ri, ci = np.nonzero(surviving)
    positions = np.cumsum(surviving, axis=1)[ri, ci] - 1
    new_ages[ri, positions] = ages[ri, ci]
    new_welfare[ri, positions] = welfare[ri, ci]
    new_traits[ri, positions] = batch.traits[ri, ci]
    max_births = int(births.max(initial=0))
    child_shape = (rows, max_births) if independent else (max_births,)
    child_ages = rng.integers(0, 50, child_shape, dtype=np.int16)
    child_raw_welfare = rng.uniform(.5, .8, child_shape)
    child_welfare = randomized_units(child_raw_welfare, 1000, rng.random(child_shape))
    child_traits = rng.uniform(.05, .5, (*child_shape, 10)).reshape(-1, 10)
    offset = len(batch.bank)
    if max_births:
        bank = np.concatenate((batch.bank, child_traits), axis=0)
        child = np.arange(max_births)[None, :]
        rr, jj = np.nonzero(child < births[:, None])
        pp = survivors[rr] + jj
        new_ages[rr, pp] = child_ages[rr, jj] if independent else child_ages[jj]
        new_welfare[rr, pp] = child_welfare[rr, jj] if independent else child_welfare[jj]
        new_traits[rr, pp] = offset + (rr * max_births + jj if independent else jj)
    else:
        bank = batch.bank
    batch.ages, batch.welfare, batch.traits, batch.bank = new_ages, new_welfare, new_traits, bank
    # Dead traits are not hidden state. Compact the bank so the evaluated
    # chain has bounded memory; ledger cohort slots refer to its start snapshot.
    live_slots = new_ages >= 0
    if live_slots.any():
        used, inverse = np.unique(new_traits[live_slots], return_inverse=True)
        batch.bank = bank[used]
        batch.traits[live_slots] = inverse
    else:
        batch.bank = np.empty((0, 10))
    draws = rng.random((rows, MICROSTEPS, 4) if independent else (MICROSTEPS, 4))
    updated_stocks = stock_step(batch.stocks, actions, draws)
    batch.stocks[count > 0] = updated_stocks[count > 0]
    update_novelty(batch, rng, protocol, independent=independent)
    if instrument.a10:
        instrument.append(batch, capability)
    return {"births": births, "deaths": count - survivors, "population": new_count}


def update_novelty(batch, rng, protocol, *, independent=False):
    rows, width = batch.ages.shape
    size = protocol.sample_size
    n = batch.population
    take = min(size, width)
    current = np.zeros((rows, size, 10))
    if take:
        # Random priorities give uniform sampling without replacement. Agent
        # labels never enter the priorities or values. Relabeling preserves
        # the law; exact pathwise relabeling is not claimed for the executor.
        keys = np.broadcast_to(rng.random((rows, width) if independent else width), (rows, width)).copy()
        keys[batch.ages < 0] = np.inf
        ix = np.argpartition(keys, take - 1, axis=1)[:, :take]
        traits = batch.bank[np.take_along_axis(batch.traits, ix, axis=1)]
        welfare = np.take_along_axis(batch.welfare, ix, axis=1) / 1000
        valid = np.take_along_axis(batch.ages, ix, axis=1) >= 0
        contagion = np.clip(batch.h_n / np.maximum(n, 1), .5, 2)
        normals = rng.normal(size=(rows, take, 10) if independent else (take, 10))
        samples = normals * traits * welfare[..., None] * .8685 * contagion[:, None, None]
        center = np.asarray(protocol.center)
        samples = center + np.clip(samples - center, -protocol.coordinate_bound, protocol.coordinate_bound)
        # Partition puts finite priorities ahead of infinities but does not
        # guarantee their order. Compact valid observations before pooling.
        order = np.argsort(~valid, axis=1, kind="stable")
        samples = np.take_along_axis(samples, order[..., None], axis=1)
        current[:, :take] = samples
    batch.window[:, 1:] = batch.window[:, :-1].copy()
    batch.counts[:, 1:] = batch.counts[:, :-1].copy()
    batch.window[:, 0] = current
    batch.counts[:, 0] = np.minimum(n, size)
    samples = current.copy()
    small = n < size
    if small.any():
        windows = batch.window[small].reshape((-1, protocol.lookback * size, 10))
        valid = (np.arange(size)[None, None, :] < batch.counts[small, :, None]).reshape((-1, protocol.lookback * size))
        ranks = valid.cumsum(axis=1) - 1
        rr, cc = np.nonzero(valid & (ranks < size))
        pooled = np.zeros((small.sum(), size, 10))
        pooled[rr, ranks[rr, cc]] = windows[rr, cc]
        samples[small] = pooled
    deviations = samples - np.asarray(protocol.center)
    covariance = np.swapaxes(deviations, 1, 2) @ deviations / size
    signs, logdets = np.linalg.slogdet(np.eye(10)[None] + covariance / protocol.sigma_squared)
    if np.any(signs <= 0):
        raise ArithmeticError("invalid covariance determinant")
    batch.h_n = logdets / (2 * np.log(2))
    batch.h_n[(n == 0) | (batch.counts.sum(axis=1) < size)] = 0
    batch.window[n == 0] = 0
    batch.counts[n == 0] = 0
    batch.stocks[n == 0] = 0


def diversity(batch):
    n = batch.population
    if batch.ages.shape[1] == 0:
        return np.zeros(len(n))
    # Exact pairwise L1 observable, including every agent's propensity.
    traits = np.where((batch.ages >= 0)[..., None], batch.bank[batch.traits], 0)
    ordered = np.sort(traits, axis=1)
    width = batch.ages.shape[1]
    positions = np.arange(1, width)[None, :]
    alive_below = np.maximum(0, positions - (width - n)[:, None])
    coefficient = alive_below * (n[:, None] - alive_below)
    # Difference form gives exact zero for identical traits, including
    # ragged rows with dead-slot zeros, without subtractive cancellation.
    distance = (coefficient[..., None] * np.diff(ordered, axis=1)).sum(axis=(1, 2))
    result = 2 * distance / (np.maximum(n * (n - 1), 1) * 10 * .45)
    return np.where(n < 2, 0, np.clip(result, 0, 1))


def measurements_and_flow(batch, actions, parameters, alpha, capability, *, n_ref=200, v_max=5, instrument=R4):
    n = batch.population
    welfare = np.where(batch.ages >= 0, batch.welfare, 0).sum(axis=1) / np.maximum(n, 1) / 1000
    stocks = batch.stocks / 100
    frontier = np.asarray(capability) * stocks[:, 2]
    bandwidth = welfare * stocks[:, 3]
    clip = bandwidth_clip(v_max, .5, parameters.epsilon_l)
    theta = np.exp(-(1 - stocks[:, 3]) * frontier / v_max - alpha * np.maximum(0, frontier / np.maximum(bandwidth, clip) - 1))
    if instrument.a10:
        instrument.require_capability(capability)
        frontier = instrument.velocity(batch)
        theta, bandwidth, ratio = instrument.response(frontier, welfare, stocks[:, 3], alpha)
        clip = instrument.floor
    d_gen = diversity(batch)
    lineage = d_gen * np.minimum(n / n_ref, 1) * stocks[:, 0] * theta
    h_e = -np.expm1(-2.5 * actions[:, 0])
    if instrument.a10:
        h_e = -np.expm1(-2.5 * instrument.benefit(capability) * actions[:, 0])
    components = np.column_stack((np.log(batch.h_n + parameters.epsilon_n), np.log(h_e + parameters.epsilon_e), np.log(lineage + parameters.epsilon_l)))
    values = components @ np.array([parameters.lambda_n, parameters.mu, parameters.kappa])
    values[n == 0] = parameters.extinction_flow
    extra = ({"frontier_velocity": frontier, "bandwidth": bandwidth, "bandwidth_at_floor": bandwidth <= clip,
              "velocity_bandwidth_ratio": ratio} if instrument.a10 else {})
    return values, {"h_n": batch.h_n.copy(), "h_e": h_e, "lineage": lineage, "diversity": d_gen,
                    "psi": stocks[:, 0], "theta": theta, "bandwidth_below_clip": (bandwidth < clip) & (n > 0),
                    "log_components": components, **extra}
