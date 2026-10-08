"""A10 per-capability families, paired run manifests, and producer receipts.

No production data is read at import and no job is launched here. A4 and A5
remain the validation and labeling producers, now against this family's pin.
"""
from copy import deepcopy
from pathlib import Path
from .artifacts import (SIMULATION, atomic_json, code_identity, digest, read,
                        seal, unseal, stable_job, file_hash)
from .instrument import Instrument, CONSTANTS_SHA256
from .study import capabilities, scoring_contexts, scoring_for_rr, R1_RR, R2_ALPHA, R2_CAP

NOMINAL = Instrument("A10", 1.8, "linear")
FAMILIES = ("nominal", "sqrt", "crowding", "sigma_squared_x10", "sigma_squared_x0.1")


def arm_contexts():
    values = {(rr, 1., c) for rr in R1_RR for c in capabilities(1.5)}
    values.update((.064, a, c) for a in R2_ALPHA for first in R2_CAP for c in capabilities(first))
    return sorted(values)


def contexts(family):
    if family not in FAMILIES:
        raise ValueError("unknown A10 table family")
    if family == "nominal":
        return scoring_contexts()
    if family in ("sqrt", "crowding"):
        return arm_contexts()
    from .tables_a6 import SIGMA_RR
    return [(r, 1., c) for r in SIGMA_RR for c in capabilities(1.5)]


def family_instrument(family):
    contexts(family)  # validates the name
    return Instrument("A10", 1.8, "sqrt" if family == "sqrt" else "linear")


def scoring(family, rr, cap):
    inst = family_instrument(family)
    if family == "nominal":
        base = [s for s in scoring_for_rr(rr) if s["capability"] == cap]
    else:
        base = [{"alpha": a, "capability": c, "kappa": 8.}
                for r, a, c in contexts(family) if r == rr and c == cap]
    result = [dict(s, **inst.declaration()) for s in base]
    if family == "nominal":
        for r, a, c in arm_contexts():
            if r == rr and c == cap:
                for k in (1.5, 2.3):
                    result.append({"alpha": a, "capability": c, "kappa": 8.,
                                   **Instrument("A10", k, "linear").declaration()})
    return sorted(result, key=lambda v: (v["alpha"], v["kappa"], v["k_star"]))


def build_jobs(family, calibration_path=None, *, tag="v3_tables", settings_override=None,
               kernel_override=None, rule_ids=None, physical_contexts=None):
    from .offline_estimator import settings_for, SENSITIVITY_RULES, SENSITIVITY_RR
    from .policies import execution_policy_class
    inst = family_instrument(family)
    physical = sorted({(r, c) for r, _, c in contexts(family)})
    if physical_contexts is not None:
        if not set(physical_contexts) <= set(physical):
            raise ValueError("toy context outside the declared family")
        physical = sorted(physical_contexts)
    rules = [r for r in execution_policy_class() if rule_ids is None or r.rule_id in rule_ids]
    if not rules:
        raise ValueError("empty table rule class")
    jobs = []
    for rr, cap in physical:
        for rule in rules:
            names = ["primary"]
            if rule.rule_id in SENSITIVITY_RULES and rr in SENSITIVITY_RR:
                names += ["double_population", "double_length"]
            for name in names:
                kernel = {"reproduction_rate": rr, "capability": cap, "instrument": inst.declaration()}
                if family == "crowding":
                    kernel["crowding"] = "reproductive"
                if kernel_override:
                    if set(kernel_override) - {"n_agents", "carrying_capacity"}:
                        raise ValueError("toy override cannot alter A10 quantities")
                    kernel.update(kernel_override)
                cfg = {"phase": "table", "a10_family": family, "rule_id": rule.rule_id,
                       "kernel": kernel, "route": "auto", "setting_name": name,
                       "settings": {**settings_for(name), **(settings_override or {})},
                       "scoring": scoring(family, rr, cap)}
                if calibration_path is not None:
                    cfg["calibration_path"] = str(calibration_path)
                jobs.append(stable_job("table", cfg, tag, 0))
    return jobs


def provenance(family, jobs):
    instruments = {digest({k: s[k] for k in ("mapping", "k_star", "g")}):
                   {k: s[k] for k in ("mapping", "k_star", "g")}
                   for j in jobs for s in j["config"]["scoring"]}
    return {"family": family, "producer_code_hash": code_identity(), "constants_sha256": CONSTANTS_SHA256,
            "job_manifest_sha256": digest(jobs), "instruments": [instruments[k] for k in sorted(instruments)],
            "fit_first_source_step": 30, "k_star_scoring": "same pass, shared nominal physical trajectories"}


def estimation_spec(family, calibration_path, *, registration=None, wall_hours=None, jobs=None):
    """Prepare, without launching, a family at the operator's wall ceiling.

    ``jobs`` is an explicit toy subset only. Registered manifests use the exact
    full family and require an A10 registration pin and an operator-set ceiling.
    """
    from .table_validation_a4 import estimate_memory_gb
    inst = family_instrument(family)
    if registration is not None and (jobs is not None or wall_hours is None):
        raise ValueError("registered A10 estimation needs the full family and its operator-set ceiling")
    jobs = build_jobs(family, calibration_path) if jobs is None else jobs
    if not jobs:
        raise ValueError("empty A10 estimation manifest")
    representative = max(jobs, key=lambda j: len(j["config"]["scoring"]))
    cfg = deepcopy(representative["config"])
    cfg["settings"].update(burn=30, measure=8)
    profile = {"kind": "table", "config": cfg, "workers_local": [2,4,8,12],
               "workers_x2": [8,12,16,24,32], "threads": [1], "rounds": 1,
               "jobs_per_worker": 1, "jobs_local": 12, "jobs_x2": 32}
    memory = max(estimate_memory_gb("fv", j["config"]["settings"]) * 9/8 for j in jobs)
    return {"schema": "v3-A10-estimation-1", "registered": registration is not None,
            "registered_a10": registration is not None, "registration": registration,
            "instrument": inst.declaration(), "tag": "v3_tables", "code_hash": code_identity(),
            "a10_family": family, "jobs": jobs, "phases": ["table"], "configuration": {"table": profile},
            "memory_estimate_gb": {"table": max(.25, memory)},
            "wall_seconds": (wall_hours if wall_hours is not None else 1.) * 3600,
            "configuration_seconds": 900, "cleanup_reserve_seconds": 300,
            "publication": None, "source_family": {"code_hash": code_identity()}}


def prepare_validation(source_root, calibration_path, *, registration=None, wall_hours=None,
                       probe_root=None, settings_override=None):
    from .table_validation_a4 import prepare
    info = verify_estimation_source(source_root, calibration_path, registered=registration is not None)
    if registration is not None and (wall_hours is None or settings_override):
        raise ValueError("registered A10 validation needs its operator-set ceiling and frozen settings")
    return prepare(source_root, calibration_path, registration, wall_hours or 1., probe_root,
                   settings_override, instrument=family_instrument(info["family"]))


def expected_keys(jobs, calibration):
    from .context import Context
    from .production_tables import row_key
    result = set()
    for job in jobs:
        c = job["config"]
        if c["setting_name"] != "primary":
            continue
        ctx = Context.build(c["kernel"], calibration)
        for s in c["scoring"]:
            result.add(row_key({"rule_id": c["rule_id"], "kernel_hash": ctx.kernel_hash,
                                "calibration_hash": ctx.calibration_hash,
                                "initial_population": c["kernel"].get("n_agents", 200), "scoring": s}))
    return result


def assemble(outputs, calibration, target, family, *, registered=False, jobs=None):
    from .study import assemble_tables
    if not outputs:
        raise ValueError("empty A10 estimation")
    cal_path = outputs[0]["job"]["config"].get("calibration_path")
    declared = build_jobs(family, cal_path) if registered else jobs
    if declared is None:
        raise ValueError("non-registered assembly requires its declared toy jobs")
    return assemble_tables(outputs, calibration, target, registered=registered,
                           a10_jobs=declared, a10_family=family)


def verify_estimation_source(root, calibration_path, *, registered):
    root = Path(root)
    manifest = unseal(read(root / "tables_A1_manifest.json"))
    doc = read(root / "v3_rerun_tables_A1.json")
    payload = unseal(doc)
    info = payload["manifest"].get("a10")
    if not info or info["constants_sha256"] != CONSTANTS_SHA256 or payload["code_hash"] != code_identity():
        raise ValueError("A10 source has a different producer or constants")
    jobs = manifest["jobs"]
    if digest(jobs) != info["job_manifest_sha256"]:
        raise ValueError("A10 source job manifest mismatch")
    if registered and jobs != build_jobs(info["family"], calibration_path):
        raise ValueError("registered A10 requires every exact per-capability estimation job")
    calibration = read(SIMULATION / calibration_path)
    if set(payload["rows"]) != expected_keys(jobs, calibration):
        raise ValueError("A10 source lacks required scoring rows")
    return info


def paired_runs(calibration_path, tables_path, *, source_calibration_path=None, source_tables_path=None):
    from .study import rerun_jobs
    from .sensitivity_a6 import NOMINAL_CALIBRATION_PATH, NOMINAL_TABLES_PATH
    original = rerun_jobs(source_calibration_path or NOMINAL_CALIBRATION_PATH,
                          source_tables_path or NOMINAL_TABLES_PATH)
    return correct_runs(original, calibration_path, tables_path)


def correct_runs(original, calibration_path=None, tables_path=None):
    result = []
    for old in original:
        cfg = deepcopy(old["config"])
        cfg["a10_seed_source"] = deepcopy(old["config"])
        cfg["model"]["instrument"] = NOMINAL.declaration()
        if calibration_path is not None:
            cfg["calibration_path"] = str(calibration_path)
        if tables_path is not None:
            cfg["tables_path"] = str(tables_path)
        new = stable_job(old["kind"], cfg, old["tag"], old["index"])
        if new["seed"] != old["seed"]:
            raise AssertionError("A10 changed its counterpart's seed")
        result.append(new)
    return result


def arm_runs(calibration_path, nominal_tables_path, sqrt_tables_path):
    from .sensitivity_a6 import _grid_cells
    result = []
    for inst in (Instrument("A10", 1.5, "linear"), Instrument("A10", 2.3, "linear"), Instrument("A10", 1.8, "sqrt")):
        for grid, rr, alpha, cap in _grid_cells():
            cfg = {"phase": "a10_arm", "category": "a10_arm", "grid": grid, "steps": 500,
                   "calibration_path": str(calibration_path),
                   "tables_path": str(sqrt_tables_path if inst.g == "sqrt" else nominal_tables_path),
                   "model": {"reproduction_rate": rr, "alpha": alpha, "successor_capability": cap,
                             "instrument": inst.declaration()}}
            result.extend(stable_job("rerun", cfg, "v3_rerun", i) for i in range(100))
    assert len(result) == 13200
    return result


def a6_runs(paths):
    from .sensitivity_a6 import (build_weight_corner_jobs, build_horizon_jobs, build_crowding_jobs, build_sigma_jobs)
    nominal = paths["nominal"]
    old = build_weight_corner_jobs(*nominal) + build_horizon_jobs(*nominal)
    old += build_crowding_jobs(*paths["crowding"])
    old += build_sigma_jobs({f: paths[f] for f in FAMILIES if f.startswith("sigma")})
    return correct_runs(old)


def finalize_receipt(family_path, labels_path):
    """Bind the existing A4 publication and A5 labels without rewriting either."""
    family_path = Path(family_path)
    table = read(family_path)
    payload = unseal(table)
    p = payload["manifest"].get("a10")
    if not p or p["producer_code_hash"] != code_identity() or payload["code_hash"] != code_identity():
        raise ValueError("not this A10 producer's family")
    a4_path = family_path.with_suffix(".compatibility.json")
    a4 = unseal(read(a4_path))
    labels_doc = read(labels_path)
    labels = unseal(labels_doc)
    if (a4["table_seal_sha256"] != table["sha256"] or a4["table_file_sha256"] != file_hash(family_path)
            or labels["a4_family"]["table_seal_sha256"] != table["sha256"]
            or labels["a4_family"]["family_file_sha256"] != file_hash(family_path)
            or labels["code_hash"] != code_identity()):
        raise ValueError("A10 validation or label provenance mismatch")
    receipt = seal({"schema": "v3-A10-table-receipt-1", "table_sha256": table["sha256"],
                    "producer_code_hash": code_identity(), "constants_sha256": CONSTANTS_SHA256,
                    "validation_receipt_sha256": file_hash(a4_path), "labels_sha256": file_hash(labels_path),
                    "validation_receipt": read(a4_path), "labels": labels_doc})
    target = family_path.with_suffix(".a10_receipt.json")
    if target.exists() and read(target) != receipt:
        raise RuntimeError("A10 producer receipt is frozen")
    atomic_json(target, receipt)
    return receipt
