"""The comparison registry (section 1), as frozen data.

Every literal here is registered: the family sizes 18 and 33 never become 6, 8
or 14 and never depend on how many arms ran (D:85). The registry is built from
the literal tables below, checked against the native constants and
``reading_a6.headline_comparisons()`` (D:181-183), and pinned by its digest.
"""
from .common import Refused, digest, require

# G0 literals (A6.3, A4.9, D:48).
PYTHON_VERSION = "3.13.12"
NUMPY_VERSION = "2.4.4"
RUNNING_IDENTITY = "93a453b27c82a9cb16ed0d04b1029168014b73c1f3d97f5b884e1b6d52f161da"

COMPONENTS = ("A10", "A6")
FAMILY_OF_COMPONENT = {"A10": "A10arm", "A6": "A6"}
ARMS = {"A10": ("sqrt",), "A6": ("crowding", "sigma_squared_x0.1", "sigma_squared_x10")}
ARM_FAMILIES = ("sqrt", "crowding", "sigma_squared_x10", "sigma_squared_x0.1")
COMPONENT_OF_ARM = {arm: component for component, arms in ARMS.items() for arm in arms}
FAMILY_SIZE = {"A10arm": 18, "A6": 33}
LEVEL_ALPHA = {"A10arm": 0.05 / 18, "A6": 0.05 / 33}
UNDEFINED_TAIL = {"A10arm": 0.05 / 36, "A6": 0.05 / 66}
SEED = {"A10arm": 20261011, "A6": 20260929}
RESAMPLES = 50000
QUANTILE_METHOD = "inverted_cdf"

R1_GRID = (0.055, 0.056, 0.057, 0.058, 0.059, 0.06, 0.062, 0.064, 0.066)
SIGMA_GRID = (0.059, 0.06, 0.062, 0.064, 0.066)
ALPHAS = (0.5, 0.75, 1.0, 1.25, 1.5)
CAPABILITIES = (1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0)
CAPSTAR_RR = 0.064
GRIDS = {"R1": R1_GRID, "SIGMA": SIGMA_GRID}
SEEDS_REGISTERED = {"arm": 100, "comparator_boundary": 400, "comparator_capstar": 75}
RUN_COUNTS = {"sqrt": 4400, "crowding": 4400, "sigma_squared_x10": 500, "sigma_squared_x0.1": 500}
COMPARATOR_JOBS = 24900
COMPARATOR_CONTRIBUTING = 6225
PRIMARY_ROWS = {"nominal": 19500, "sqrt": 2875, "crowding": 2875, "sigma_squared_x10": 625,
                "sigma_squared_x0.1": 625}
CAPS = {"nominal": 19, "sqrt": 2, "crowding": 2, "sigma_squared_x10": 0, "sigma_squared_x0.1": 0}
STAGE1_A10_ARMS = ("k1p5", "k2p3")

# The filters of D:133-137, matched by exact equality on every key.
_COMMON = {"kappa": 8.0, "theta": 0.5, "steps": 500, "k_star": 1.8}
_COMPARATOR = dict(_COMMON, component="main", crowding="total", variant=None, g="linear")
ARM_FILTERS = {
    "sqrt": dict(_COMMON, component="sqrt", category="a10_arm", crowding="total", variant=None, g="sqrt"),
    "crowding": dict(_COMMON, component="crowding", category="a6_crowding", arm="a6_crowding",
                     variant="crowding_reproductive", crowding="reproductive", g="linear"),
    "sigma_squared_x10": dict(_COMMON, component="sigma_squared_x10", category="a6_sigma_squared_x10",
                              arm="a6_sigma_squared_x10", variant="sigma_squared_x10", crowding="total", g="linear"),
    "sigma_squared_x0.1": dict(_COMMON, component="sigma_squared_x0.1", category="a6_sigma_squared_x0.1",
                               arm="a6_sigma_squared_x0.1", variant="sigma_squared_x0.1", crowding="total", g="linear"),
}
BOUNDARY_ARMS = {"A10arm": ("sqrt",), "A6": ("crowding", "sigma_squared_x0.1", "sigma_squared_x10")}
CAPSTAR_ARMS = {"A10arm": ("sqrt",), "A6": ("crowding",)}

LABEL_COMPARATOR = "produced under A13 and A14, amendments informed by outcomes"
UNCERTIFIED_SENTENCE = "An unflagged quantity is not certified unaffected."
CASE2_REASON = "A13 accumulator absent: `admission_a13.enabled` is false for an empty admitted-row set"
A16_STATEMENT = "at least 1 - alpha(1 + P/M), given the fitted family"
NO_LABEL_DISCLOSURE = "no A5 labels; FV asymptotic and uncertified"
STAGE1_STATEMENT = ("Stage 1's 12 A10 comparisons (arms k1p5 and k2p3), its 25 A6 comparisons and its "
                    "seed-convergence seal are not recomputed.")
REGISTRY_DIGEST = "79a6d20c886a3732bf2578b7c8c0c455d6fc322381921b3c1d66c781ef13f94c"


def identity(family, kind, arm, alpha=None):
    """D:61-68: ``<family>.<kindkey>.<arm>`` and, for cap*, ``.<repr(alpha)>``."""
    if kind == "boundary":
        return "%s.boundary.%s" % (family, arm)
    return "%s.capstar.%s.%r" % (family, arm, alpha)


def _entry(family, kind, arm, alpha=None):
    sigma = arm.startswith("sigma_squared")
    boundary = kind == "boundary"
    arm_filters = dict(ARM_FILTERS[arm], grid="R1" if boundary else "R2")
    comparator_filters = dict(_COMPARATOR, category="R1" if boundary else "R2")
    if boundary:
        arm_filters.update(alpha=1.0, capability=1.5)
        comparator_filters.update(alpha=1.0, capability=1.5)
    grid = ("SIGMA" if sigma else "R1") if boundary else "CAPABILITIES"
    return {
        "identity": identity(family, kind, arm, alpha),
        "component": "A10" if family == "A10arm" else "A6",
        "family": family, "kind": kind, "arm": arm, "alpha": alpha,
        "tuple": {"kind": kind, "arm": arm} if boundary else {"kind": kind, "arm": arm, "alpha": alpha},
        "family_size": FAMILY_SIZE[family], "level_alpha": LEVEL_ALPHA[family],
        "undefined_tail": UNDEFINED_TAIL[family] if boundary else None,
        "seed": SEED[family], "resamples": RESAMPLES, "quantile_method": QUANTILE_METHOD,
        "grid": grid, "grid_values": list(GRIDS[grid]) if boundary else list(CAPABILITIES),
        "capstar_rr": None if boundary else CAPSTAR_RR, "sigma_variant": bool(boundary and sigma),
        "arm_filters": arm_filters, "comparator_filters": comparator_filters,
        "arm_seeds": SEEDS_REGISTERED["arm"],
        "comparator_seeds": SEEDS_REGISTERED["comparator_boundary" if boundary else "comparator_capstar"],
    }


def build():
    entries = []
    for family in ("A10arm", "A6"):
        rows = [_entry(family, "boundary", arm) for arm in BOUNDARY_ARMS[family]]
        rows += [_entry(family, "cap_star", arm, a) for arm in CAPSTAR_ARMS[family] for a in ALPHAS]
        entries += sorted(rows, key=lambda e: e["identity"])
    return entries


REGISTRY = build()
BY_IDENTITY = {e["identity"]: e for e in REGISTRY}


def registry_digest():
    return digest(REGISTRY)


def for_component(component):
    """The component's comparisons in the registered call order (DN:1872)."""
    return [e for e in REGISTRY if e["component"] == component]


def quantity_keys(entry):
    """D:494-497: the quantity keys one comparison owns, each with its kind."""
    f, arm = entry["family"], entry["arm"]
    if entry["kind"] == "boundary":
        keys = [("%s.boundary.%s" % (f, arm), "boundary", None), ("%s.boundary_point.%s" % (f, arm), "boundary_point", None)]
        for rr in entry["grid_values"]:
            keys.append(("%s.survival.%s.%r" % (f, arm, rr), "survival", rr))
            keys.append(("%s.survival_difference.%s.%r" % (f, arm, rr), "survival_difference", rr))
        return keys
    a = entry["alpha"]
    return [("%s.capstar.%s.%r" % (f, arm, a), "capstar", None),
            ("%s.capstar_point.%s.%r" % (f, arm, a), "capstar_point", None)]


def verify_formation():
    """D:181-183 and the native constants. Any other count is a refusal."""
    from v3 import reading_a6, gates, study
    try:
        native = reading_a6.headline_comparisons()
    except Exception:
        raise Refused("registry formation differs from the native registry") from None
    stage2 = {"crowding", "sigma_squared_x10", "sigma_squared_x0.1"}
    kept = [c for c in native if c["arm"] in stage2]
    rest = [c for c in native if c["arm"] not in stage2]
    corners = ["weight_corner_k0.75_t0.25", "weight_corner_k0.75_t0.75", "weight_corner_k8_t0.25", "weight_corner_k8_t0.75"]
    stage1 = [{"kind": "boundary", "arm": a} for a in corners] + [{"kind": "boundary", "arm": "horizon"}]
    stage1 += [{"kind": "cap_star", "arm": a, "alpha": al} for a in corners for al in gates.ALPHAS]
    key = lambda c: (c["kind"], c["arm"], c.get("alpha", -1.0))
    mine_a6 = [e["tuple"] for e in REGISTRY if e["family"] == "A6"]
    mine_a10 = [e["tuple"] for e in REGISTRY if e["family"] == "A10arm"]
    a10 = [{"kind": "boundary", "arm": "sqrt"}] + [{"kind": "cap_star", "arm": "sqrt", "alpha": a} for a in gates.ALPHAS]
    ok = (len(native) == 33 and len(kept) == 8 and len(rest) == 25
          and sorted(kept, key=key) == sorted(mine_a6, key=key)
          and sum(c["kind"] == "boundary" for c in kept) == 3
          and sorted(rest, key=key) == sorted(stage1, key=key)
          and sorted(a10, key=key) == sorted(mine_a10, key=key) and len(mine_a10) == 6
          and tuple(reading_a6.R1_GRID) == R1_GRID == tuple(study.R1_RR) and tuple(reading_a6.SIGMA_GRID) == SIGMA_GRID
          and tuple(gates.ALPHAS) == ALPHAS == tuple(study.R2_ALPHA)
          and tuple(gates.CAPABILITIES) == CAPABILITIES == tuple(study.R2_CAP)
          and reading_a6.R2_CAPSTAR_RR == CAPSTAR_RR and reading_a6.DEFAULT_RESAMPLES == RESAMPLES
          and reading_a6.BONFERRONI_ALPHA == LEVEL_ALPHA["A6"] and reading_a6.UNDEFINED_RESAMPLE_TAIL == UNDEFINED_TAIL["A6"]
          and reading_a6.HEADLINE_COMPARISONS == FAMILY_SIZE["A6"] and reading_a6.SURVIVAL_THRESHOLD == 30
          and (reading_a6.ARM_SEEDS, reading_a6.R1_COMPARATOR_SEEDS, reading_a6.R2_COMPARATOR_SEEDS) == (100, 400, 75))
    require(ok, "registry formation differs from the native registry")
    require(registry_digest() == REGISTRY_DIGEST, "registry digest differs from its frozen literal")
