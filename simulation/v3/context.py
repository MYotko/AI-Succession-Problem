"""Shared fixed-rule kernel context and independent entrant populations."""
from dataclasses import dataclass
import numpy as np
from metrics import H_N_V_REF
from .engine import PopulationBatch, randomized_units, measurements_and_flow
from .measurements import NoveltyProtocol
from .objective import FlowParameters
from .tables import kernel_identity


@dataclass
class Context:
    config: dict
    protocol: NoveltyProtocol
    parameters: FlowParameters
    n_ref: float
    calibration_hash: str
    fixture: bool

    @classmethod
    def build(cls, config, calibration=None):
        values = {"center": [0.] * 10, "sigma_squared": .1 * H_N_V_REF / 10,
                  "epsilon_n": 1e-6, "epsilon_e": 1e-6, "epsilon_l": 1e-6, "n_ref": 200., "c_e": 2.5}
        calibration_hash, fixture = "B1-fixture", True
        if calibration is not None:
            from .calibration import validate_calibration
            payload = validate_calibration(calibration, registered=False)
            values = payload["values"]
            calibration_hash, fixture = calibration["sha256"], payload["fixture"]
        protocol = NoveltyProtocol(tuple(values["center"]), values["sigma_squared"])
        params = FlowParameters(5, 3, config.get("kappa", 8.), values["epsilon_n"], values["epsilon_e"], values["epsilon_l"], 0, protocol.upper_bound)
        if values["c_e"] != 2.5:
            raise ValueError("this frozen kernel requires c_E=2.5")
        return cls(dict(config), protocol, params, values["n_ref"], calibration_hash, fixture)

    @property
    def kernel_hash(self):
        return kernel_identity(self.config.get("reproduction_rate", .08), self.config.get("carrying_capacity", 1600),
                               self.config.get("crowding", "total"), self.protocol.__dict__)

    def population(self, count, rng):
        n = self.config.get("n_agents", 200)
        ages = rng.integers(0, 50, (count, n), dtype=np.int16)
        welfare = randomized_units(rng.uniform(.5, .8, (count, n)), 1000, rng.random((count, n)))
        bank = rng.uniform(.05, .5, (count * n, 10))
        stocks = np.tile([50, 30, 50, 50], (count, 1)).astype(np.uint8)
        return PopulationBatch(ages, welfare, np.arange(count * n).reshape(count, n), bank, stocks,
                               np.zeros((count, 10, 64, 10)), np.zeros((count, 10), dtype=np.int16), np.zeros(count))

    def measure(self, state, actions, alpha=1., capability=1.):
        return measurements_and_flow(state, actions, self.parameters, alpha, capability, n_ref=self.n_ref)


def reproductive_support(state):
    """Exclude only a provably closed sterile set, using maximum welfare.

    Every retained agent has some possible future fertile age under the
    welfare envelope. This may retain policy-specific transient states;
    R14 stability and reduced checks address the asymptotic interpretation.
    """
    ages = state.ages.astype(int)
    remaining = np.maximum(0, 49 - ages)
    # Maximum gains to the last fertile age are 1+...+(49-age).
    possible = (ages >= 0) & (ages < 49) & (state.welfare + remaining * (remaining + 1) // 2 >= 500)
    return possible.any(axis=1)


def observable_features(state, actions):
    from .engine import diversity
    n = state.population
    mean = np.where(state.ages >= 0, state.welfare, 0).sum(axis=1) / np.maximum(1, n) / 1000
    return np.column_stack((n, state.h_n, -np.expm1(-2.5 * actions[:, 0]), diversity(state),
                            state.stocks[:, 0] / 100, state.stocks[:, 2] / 100,
                            state.stocks[:, 3] / 100, mean))


def score_features(features, context, alpha, capability):
    from .measurements import bandwidth_clip
    x = np.asarray(features)
    p = context.parameters
    v = capability * x[..., 5]
    b = x[..., 6] * x[..., 7]
    theta = np.exp(-(1 - x[..., 6]) * v / 5 - alpha * np.maximum(0, v / np.maximum(b, bandwidth_clip(5, .5, p.epsilon_l)) - 1))
    lineage = x[..., 3] * np.minimum(x[..., 0] / context.n_ref, 1) * x[..., 4] * theta
    components = np.stack((np.log(x[..., 1] + p.epsilon_n), np.log(x[..., 2] + p.epsilon_e), np.log(lineage + p.epsilon_l)), axis=-1)
    flows = components @ [p.lambda_n, p.mu, p.kappa]
    return np.where(x[..., 0] == 0, p.extinction_flow, flows)
