"""The declared R4 or A10 instrument, with a separately sealed constants record."""
from dataclasses import dataclass
import math
from pathlib import Path
import numpy as np
from .artifacts import read, unseal

TAU = 30
TECH_MIN = .01
W_REF = .8029014082336364
TR_REF = .7292628000000001
V_MAX = math.log(500) / TAU
EPSILON_L = .001412790614729507
BMIN_CAP = .014666388971338522
REFERENCE_SHA256 = "fc7364f228318b21f44fd85b13d1ecd003a4d82368dc85fe5c42532f71c3cfb1"
CALIBRATION_SHA256 = "bf0f7c3f10310558d567b6b3f7c24f6f99f2fe6eb71fd830cccfd8e2aa0bd6d6"
CONSTANTS_SHA256 = "3260290d2be9232906862d28af8eca9a2ca61d5613fed55e3acdf60e2024bf6c"
CONSTANTS_PATH = Path(__file__).with_name("a10_constants.json")


def validate_constants(document=None):
    document = read(CONSTANTS_PATH) if document is None else document
    payload = unseal(document)
    if document["sha256"] != CONSTANTS_SHA256:
        raise ValueError("A10 constants record does not match the declared seal")
    return payload


@dataclass(frozen=True)
class Instrument:
    mapping: str = "R4"
    k_star: float | None = None
    g: str | None = None

    def __post_init__(self):
        if self.mapping == "R4":
            if self.k_star is not None or self.g is not None:
                raise ValueError("R4 has no A10 arm declarations")
        elif self.mapping == "A10":
            if self.k_star not in (1.5, 1.8, 2.3) or self.g not in ("linear", "sqrt"):
                raise ValueError("A10 requires declared k_star and g")
            validate_constants()
        else:
            raise ValueError("unknown lineage mapping")

    @property
    def a10(self):
        return self.mapping == "A10"

    @property
    def floor(self):
        if not self.a10:
            raise ValueError("R4 floor depends on calibration")
        return min(BMIN_CAP, math.log(self.k_star) / TAU * .325 / (W_REF * TR_REF))

    def require_capability(self, capability):
        c = np.asarray(capability, dtype=float)
        if np.any(~np.isfinite(c)) or np.any(c < 1) or np.any(c > 5):
            raise ValueError("A10 capability must lie in [1,5]")
        return c

    def benefit(self, capability):
        c = self.require_capability(capability)
        return c if self.g == "linear" else np.sqrt(c)

    def log_frontier(self, capability, technology):
        c = self.require_capability(capability)
        technology = np.asarray(technology)
        if np.any(~np.isfinite(technology)) or np.any(technology < 0) or np.any(technology > 1):
            raise ValueError("technology outside the stock domain")
        return np.log(c * np.maximum(technology, TECH_MIN))

    def initialize(self, state, capability):
        value = self.log_frontier(capability, state.stocks[:, 2] / 100)
        state.frontier_history = np.repeat(value[:, None], TAU + 1, axis=1)

    def append(self, state, capability):
        self.require_capability(capability)
        if state.frontier_history is None:
            raise ValueError("A10 requires actual frontier history")
        state.frontier_history[:, :-1] = state.frontier_history[:, 1:].copy()
        state.frontier_history[:, -1] = self.log_frontier(capability, state.stocks[:, 2] / 100)

    def velocity(self, state):
        history = state.frontier_history
        if history is None or history.shape != (len(state.ages), TAU + 1):
            raise ValueError("missing A10 pace state")
        if (not np.isfinite(history).all() or np.any(history < math.log(TECH_MIN) - 1e-14)
                or np.any(history > math.log(5) + 1e-14)):
            raise ValueError("frontier history outside the declared domain")
        return np.maximum(0, history[:, -1] - history[:, 0]) / TAU

    def response(self, velocity, welfare, transfer, alpha):
        v, w, tr = np.broadcast_arrays(velocity, welfare, transfer)
        if (not np.isfinite(v).all() or np.any(v < 0) or np.any(v > V_MAX + 1e-14)
                or np.any(~np.isfinite(w)) or np.any((w < 0) | (w > 1))
                or np.any(~np.isfinite(tr)) or np.any((tr < 0) | (tr > 1))):
            raise ValueError("A10 response inputs outside bounds")
        bandwidth = math.log(self.k_star) / TAU * w * tr / (W_REF * TR_REF)
        ratio = v / np.maximum(bandwidth, self.floor)
        theta = np.exp(-(1 - tr) * v / V_MAX - alpha * np.maximum(0, ratio - 1))
        return theta, bandwidth, ratio

    def declaration(self):
        return {"mapping": self.mapping, "k_star": self.k_star, "g": self.g}


R4 = Instrument()


def declaration(value=None):
    if value is None:
        return R4
    if isinstance(value, Instrument):
        return value
    if not isinstance(value, dict) or "mapping" not in value:
        raise ValueError("instrument declaration must name its mapping")
    return Instrument(**value)


def allocation_horizon(time, handover):
    return max(20, handover + TAU - time) if handover is not None and 0 <= time - handover <= TAU else 20
