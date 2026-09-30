"""A6 variant calibrations: the sigma0^2 x10 and x0.1 families.

Amendment A6, 2026-09-29. sigma0^2 (the novelty protocol's ``sigma_squared``)
is the only calibrated input that epsilon_N depends on; the fixed center,
V_ref_total, N_ref, epsilon_E, epsilon_L and c_E do not. This module re-derives
epsilon_N from the 50 registered calibration records under a scaled sigma0^2,
mirroring ``calibration.freeze`` arithmetic exactly, and seals each variant as a
registered-shape ``v3-calibration-1`` document at A6's code identity.

It reads the 50 records read-only, computes no survival, extinction or fire
rate, and never launches a job. The self-check reproduces the frozen
calibration's ``values`` bit-for-bit from the real records; any mismatch halts.
"""
import math
from pathlib import Path

import numpy as np

from .artifacts import atomic_json, code_identity, digest, read, seal, unseal
from .calibration import validate_calibration

# The two registered variants: sigma0^2 scaled by these factors.
VARIANT_FACTORS = {"sigma_squared_x10": 10.0, "sigma_squared_x0.1": 0.1}
# The values that do not depend on sigma0^2; the re-derivation must leave them
# equal to the frozen calibration, and that is asserted.
FROZEN_VALUE_KEYS = ("center", "V_ref_total", "n_ref", "epsilon_e", "epsilon_l", "c_e", "psi_observable")


class SelfCheckFailed(RuntimeError):
    """Raised when the re-derivation does not reproduce the frozen values."""


def load_records(outputs_dir, frozen_calibration):
    """Load the 50 calibration result records and verify them against the
    frozen calibration's ``input_hashes``.

    ``outputs_dir`` holds the registered calibration job outputs, each a runner
    envelope whose ``result`` is the trajectory record. ``frozen_calibration``
    is the sealed frozen calibration document. Halts unless the set of record
    digests equals the frozen ``input_hashes`` exactly.
    """
    from .study import calibration_jobs
    payload = unseal(frozen_calibration)
    expected = set(payload["input_hashes"])
    by_seed, seen = {}, set()
    for path in sorted(Path(outputs_dir).glob("*.json")):
        envelope = read(path)
        record = envelope.get("result", envelope)
        h = digest(record)
        if h not in expected:
            continue
        if h in seen:
            raise SelfCheckFailed("duplicate calibration record digest: %s" % h)
        seen.add(h)
        by_seed[record["seed"]] = record
    if seen != expected:
        missing = expected - seen
        raise SelfCheckFailed("calibration records do not match input_hashes: %d loaded, %d missing"
                              % (len(seen), len(missing)))
    # Order the records by the committed calibration job order. Floating-point
    # summation is not associative, so the order must match the registered
    # freeze's for a bit-identical self-check; the committed calibration_jobs
    # seed order reproduces the frozen center, V_ref_total and every value.
    records = []
    for job in calibration_jobs():
        if job["seed"] not in by_seed:
            raise SelfCheckFailed("calibration record missing for committed job seed %s" % job["seed"])
        records.append(by_seed[job["seed"]])
    if len(records) != len(by_seed):
        raise SelfCheckFailed("calibration records do not match the committed 50 jobs")
    return records


def _derive(records, sigma_override=None):
    """Re-derive the calibration ``values`` from the records, mirroring
    ``calibration.freeze`` arithmetic. When ``sigma_override`` is given it
    replaces sigma0^2 in the epsilon_N measurement; every other computation is
    identical to the committed protocol. Returns (values, diagnostics)."""
    if not records or len({r["seed"] for r in records}) != len(records):
        raise ValueError("independent disjoint calibration seeds required")
    if any(r["rule_id"] != "balanced" or r["reproduction_rate"] != .08 or r["successor"] is not None for r in records):
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
    sigma = .1 * total_variance / 10 if sigma_override is None else float(sigma_override)
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
    diagnostics = {"reliable_positive_lower_levels": reliable, "block_lower_levels": lower.tolist(),
                   "steps": records[0]["steps"]}
    return values, diagnostics


def self_check(records, frozen_calibration):
    """With sigma0^2 unchanged, the re-derivation must reproduce the frozen
    calibration's ``values`` exactly. Halts otherwise. Returns the base sigma0^2.
    """
    frozen = unseal(frozen_calibration)["values"]
    values, _ = _derive(records, sigma_override=None)
    for key in sorted(set(values) | set(frozen)):
        if values.get(key) != frozen.get(key):
            raise SelfCheckFailed("self-check mismatch on %r: derived %r vs frozen %r"
                                  % (key, values.get(key), frozen.get(key)))
    return float(frozen["sigma_squared"])


def build_variant(records, frozen_calibration, variant_name):
    """Seal one variant calibration document at A6's code identity.

    Every value except sigma0^2 and epsilon_N is re-derived and asserted equal
    to the frozen calibration; only epsilon_N changes with sigma0^2.
    """
    if variant_name not in VARIANT_FACTORS:
        raise ValueError("unknown A6 variant %r" % variant_name)
    frozen_doc = unseal(frozen_calibration)
    frozen_values = frozen_doc["values"]
    base_sigma = float(frozen_values["sigma_squared"])
    factor = VARIANT_FACTORS[variant_name]
    values, diagnostics = _derive(records, sigma_override=factor * base_sigma)
    # The re-derivation must leave every sigma-independent value equal to frozen.
    for key in FROZEN_VALUE_KEYS:
        if values[key] != frozen_values[key]:
            raise SelfCheckFailed("variant %s changed a sigma-independent value %r: %r vs %r"
                                  % (variant_name, key, values[key], frozen_values[key]))
    if values["sigma_squared"] != factor * base_sigma:
        raise SelfCheckFailed("variant sigma0^2 is not the scaled frozen value")
    if values["epsilon_n"] == frozen_values["epsilon_n"]:
        raise SelfCheckFailed("variant epsilon_N did not change under scaled sigma0^2")
    payload = {"schema": "v3-calibration-1", "fixture": bool(frozen_doc["fixture"]),
               "tag": frozen_doc["tag"], "code_hash": code_identity(), "values": values,
               "seeds": list(frozen_doc["seeds"]), "input_hashes": list(frozen_doc["input_hashes"]),
               "trajectories": frozen_doc["trajectories"], "steps": frozen_doc["steps"],
               "reliable_positive_lower_levels": diagnostics["reliable_positive_lower_levels"],
               "block_lower_levels": diagnostics["block_lower_levels"],
               "protected_level_units": frozen_doc.get("protected_level_units"),
               "reliability_method": frozen_doc.get("reliability_method"),
               "a6_variant": variant_name, "a6_sigma_factor": factor,
               "a6_parent_sha256": frozen_calibration["sha256"],
               "a6_note": "A6 variant: only sigma0^2 and epsilon_N differ from the parent calibration"}
    document = seal(payload)
    validate_calibration(document, registered=not payload["fixture"])
    return document


def seal_variants(outputs_dir, frozen_calibration, targets=None, *, rerun_commit=None, repo=None):
    """The end-to-end A6 variant calibration step: load and verify the records,
    run the self-check, and seal both variants. ``targets`` optionally maps a
    variant name to an output path under simulation/v3; an existing target is
    never overwritten with differing bytes. In registered mode (``targets`` given,
    the variants being sealed to disk at A6's code identity) ``rerun_commit`` is
    required, and rerun-path invariance is asserted first, since A6 must change no
    file entering the code identity. Returns a summary."""
    if targets and rerun_commit is None:
        raise ValueError("sealing the variant calibrations requires the rerun commit for invariance")
    if rerun_commit is not None:
        from .sensitivity_a6 import assert_rerun_path_invariant
        assert_rerun_path_invariant(rerun_commit, repo)
    records = load_records(outputs_dir, frozen_calibration)
    base_sigma = self_check(records, frozen_calibration)
    frozen_en = unseal(frozen_calibration)["values"]["epsilon_n"]
    results = {"self_check": "reproduced frozen values exactly", "base_sigma_squared": base_sigma,
               "frozen_epsilon_n": frozen_en, "variants": {}}
    for name in VARIANT_FACTORS:
        document = build_variant(records, frozen_calibration, name)
        if targets and name in targets:
            path = Path(targets[name])
            if path.exists() and read(targets[name]) != document:
                raise RuntimeError("variant calibration is frozen; use a reviewed new artifact identity: %s" % targets[name])
            atomic_json(targets[name], document)
        results["variants"][name] = {"sha256": document["sha256"],
                                     "sigma_squared": document["payload"]["values"]["sigma_squared"],
                                     "epsilon_n": document["payload"]["values"]["epsilon_n"]}
    return results
