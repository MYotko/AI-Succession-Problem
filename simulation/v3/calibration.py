"""Pre-registration section 5 calibration, dispatched as independent jobs.

No calibration is run at import. Production requires 50 disjoint-tag
500-step balanced trajectories and a verified pre-registration pin.
"""
import math
import numpy as np
from .artifacts import atomic_json, code_identity, digest, seal, unseal
from .context import Context, observable_features
from .engine import RuleBatch, advance
from .policies import execution_policy_class


def run_seed(config, seed, tag):
    if tag not in ("pilot", "configuration", "validation", "v3_calibration"):
        raise ValueError("calibration must have its own seed tag")
    steps = int(config.get("steps", 500))
    if tag == "v3_calibration" and (steps != 500 or config.get("n_agents", 200) != 200 or config.get("reproduction_rate", .08) != .08):
        raise ValueError("registered calibration is 500 steps at rr=.080")
    ctx = Context.build({"n_agents": config.get("n_agents", 200), "reproduction_rate": .08})
    rng = np.random.default_rng(seed)
    state = ctx.population(1, rng)
    action = np.full((1, 6), 1 / 6)
    total, squares, samples = np.zeros(10), np.zeros(10), 0
    measurements, populations, pooled_samples, features = [], [], [], []
    for step in range(steps):
        advance(state, action, rng, .08, 1600, ctx.protocol, independent=True)
        _, values = ctx.measure(state, action)
        n = int(state.counts[0, 0])
        points = state.window[0, 0, :n]
        total += points.sum(axis=0)
        squares += (points**2).sum(axis=0)
        samples += n
        measurements.append([float(values[k][0]) for k in ("h_n", "h_e", "lineage")])
        populations.append(int(state.population[0]))
        pooled = np.concatenate([state.window[0, j, :int(state.counts[0, j])] for j in range(10)])[:64]
        pooled_samples.append(pooled.tolist() if len(pooled) == 64 and state.population[0] else [])
        features.append(observable_features(state, action)[0].tolist())
    return {"tag": tag, "seed": seed, "steps": steps, "n_agents": config.get("n_agents", 200), "reproduction_rate": .08, "successor": None,
            "rule_id": "balanced", "samples": samples, "sample_sum": total.tolist(), "sample_squares": squares.tolist(),
            "measurements": measurements, "populations": populations,
            "pooled_samples": pooled_samples, "features": features,
            "code_hash": code_identity(), "measurement_protocol": "B1 honest-baseline trajectory law; rescore protected levels in frozen units"}


def freeze(records, target=None, *, registered=False):
    if not records or len({r["seed"] for r in records}) != len(records):
        raise ValueError("independent disjoint calibration seeds required")
    if registered and (len(records) != 50 or any(r["tag"] != "v3_calibration" or r["steps"] != 500 or r["n_agents"] != 200 for r in records)):
        raise ValueError("registered calibration requires all 50 by 500 jobs")
    if any(r["rule_id"] != "balanced" or r["reproduction_rate"] != .08 or r["successor"] is not None or r["code_hash"] != code_identity() for r in records):
        raise ValueError("incompatible calibration input")
    if len({r["steps"] for r in records}) != 1:
        raise ValueError("calibration horizons differ")
    count = sum(r["samples"] for r in records)
    if count == 0:
        raise ValueError("no novelty samples")
    center = np.sum([r["sample_sum"] for r in records], axis=0) / count
    variance = np.sum([r["sample_squares"] for r in records], axis=0) / count - center**2
    total_variance = float(variance.sum())
    if total_variance <= 0:
        raise ValueError("unresolved variance calibration")
    sigma = .1 * total_variance / 10
    population = np.asarray([r["populations"] for r in records])
    n_ref = max(1., float(population[:, population.shape[1] // 2:].mean()))
    measurements = np.zeros((len(records), records[0]["steps"], 3))
    for i, record in enumerate(records):
        x = np.asarray(record["features"])
        for j, points in enumerate(record["pooled_samples"]):
            if points:
                deviations = np.clip(np.asarray(points) - center, -1., 1.)
                measurements[i, j, 0] = np.linalg.slogdet(np.eye(10) + deviations.T @ deviations / (64 * sigma))[1] / (2 * math.log(2))
        measurements[i, :, 1] = x[:, 2]
        # Use the unclipped bandwidth response as a lower observable for L.
        # Every positive b_min only increases this response, so selecting
        # epsilon_L below it cannot create circular bandwidth calibration.
        velocity, bandwidth = x[:, 5], x[:, 6] * x[:, 7]
        exponent = -(1 - x[:, 6]) * velocity / 5 - np.maximum(0, velocity / np.maximum(bandwidth, 1e-300) - 1)
        theta = np.where((bandwidth > 0) | (velocity == 0), np.exp(exponent), 0.)
        measurements[i, :, 2] = x[:, 3] * np.minimum(x[:, 0] / n_ref, 1) * x[:, 4] * theta
    block_count = min(10, measurements.shape[1])
    block_means = np.stack([b.mean(axis=1) for b in np.array_split(measurements, block_count, axis=1)], axis=1)
    means = block_means.mean(axis=0)
    se = block_means.std(axis=0, ddof=1) / math.sqrt(len(records)) if len(records) > 1 else means * 0
    lower = means - 4 * se
    reliable = []
    for column in range(3):
        positive = lower[:, column][lower[:, column] > 0]
        if not len(positive):
            raise ValueError("no positive reliable protected measurement level")
        reliable.append(float(positive.min()))
    values = {"center": center.tolist(), "V_ref_total": total_variance, "sigma_squared": sigma,
              "n_ref": n_ref,
              "epsilon_n": .01 * reliable[0], "epsilon_e": .01 * reliable[1], "epsilon_l": .01 * reliable[2],
              "c_e": 2.5, "psi_observable": "institutional_stock"}
    payload = {"schema": "v3-calibration-1", "fixture": not registered, "tag": "v3_calibration" if registered else "pilot_or_validation",
               "code_hash": code_identity(), "values": values, "seeds": sorted(r["seed"] for r in records),
               "input_hashes": sorted(digest(r) for r in records), "trajectories": len(records), "steps": records[0]["steps"],
               "reliable_positive_lower_levels": reliable, "block_lower_levels": lower.tolist(),
               "protected_level_units": "final center, sigma and N_ref; L uses conservative unclipped bandwidth",
               "reliability_method": "four-standard-error lower block means across independent trajectories; exploratory calibration, not admission confidence"}
    document = seal(payload)
    validate_calibration(document, registered=registered)
    if target is not None:
        from pathlib import Path
        from .artifacts import read
        if Path(target).exists() and read(target) != document:
            raise RuntimeError("calibration is frozen; use a reviewed new artifact identity")
        atomic_json(target, document)
    return document


def validate_calibration(document, *, registered=False):
    payload = unseal(document)
    if payload.get("schema") != "v3-calibration-1" or payload.get("code_hash") != code_identity():
        raise ValueError("stale calibration")
    if registered and (payload["fixture"] or payload["tag"] != "v3_calibration" or payload["trajectories"] != 50 or payload["steps"] != 500):
        raise ValueError("registered execution rejects fixture calibration")
    v = payload["values"]
    if len(v["center"]) != 10 or not all(math.isfinite(float(x)) for x in v["center"]):
        raise ValueError("invalid fixed center")
    for name in ("sigma_squared", "n_ref", "epsilon_n", "epsilon_e", "epsilon_l", "c_e"):
        if not math.isfinite(v[name]) or v[name] <= 0:
            raise ValueError("invalid calibration value")
    if v["epsilon_l"] >= 1 or v["c_e"] != 2.5:
        raise ValueError("unsupported calibration convention")
    return payload
