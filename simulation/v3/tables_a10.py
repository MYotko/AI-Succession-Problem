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
            "x2_equivalent_hours": wall_hours if wall_hours is not None else 1.,
            "configuration_seconds": 900, "cleanup_reserve_seconds": 300,
            "publication": None, "source_family": {"code_hash": code_identity()}}


def prepare_validation(source_root, calibration_path, *, registration=None, wall_hours=None,
                       probe_root=None, settings_override=None):
    from .table_validation_a4 import prepare
    info = verify_estimation_source(source_root, calibration_path, registered=registration is not None)
    if registration is not None and (wall_hours is None or settings_override):
        raise ValueError("registered A10 validation needs its operator-set ceiling and frozen settings")
    plan = prepare(source_root, calibration_path, registration, wall_hours or 1., probe_root,
                   settings_override, instrument=family_instrument(info["family"]))
    # A10 scheduling override only. Preserve A4's R4 profile builder and jobs.
    for profile in plan["configuration"].values():
        profile["workers_local"] = [2, 4, 8, 12]
    return plan


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
    from .compatibility_a10 import accepted_identities
    accepted = accepted_identities()
    root = Path(root)
    manifest = unseal(read(root / "tables_A1_manifest.json"))
    doc = read(root / "v3_rerun_tables_A1.json")
    payload = unseal(doc)
    info = payload["manifest"].get("a10")
    if (not info or info["constants_sha256"] != CONSTANTS_SHA256 or payload["code_hash"] not in accepted
            or info.get("producer_code_hash") not in accepted
            or (manifest.get("code_hash") or manifest.get("source_family", {}).get("code_hash")) not in accepted
            or manifest.get("source_family", {}).get("code_hash", manifest.get("code_hash")) not in accepted):
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


def stage1_run_specs(calibration_path, tables_path, registration, ceilings):
    """Five complete A10 stage-1 manifests; ceilings are explicit wall hours.

    Job builders and their seeds are unchanged. Only configuration-test jobs
    have short endpoints. The main manifest is the full gate-checker family.
    """
    import math
    from decimal import Decimal, ROUND_FLOOR
    from .artifacts import verify_registration
    from .pilot import profile
    from .sensitivity_a6 import build_weight_corner_jobs, build_horizon_jobs
    names = {"main", "k1p5", "k2p3", "weight_corner", "horizon"}
    if set(ceilings) != names:
        raise ValueError("stage 1 needs exactly five explicit ceilings")
    for value in ceilings.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError("stage 1 ceilings must be positive and finite")
        if not math.isfinite(value * 3600) or value * 3600 < 1:
            raise ValueError("stage 1 ceiling must fit a positive wall-second budget")
    verify_registration(registration, instrument=NOMINAL)
    groups = {"main": paired_runs(calibration_path, tables_path)}
    arms = arm_runs(calibration_path, tables_path, "UNUSED_STAGE_2_SQRT_TABLE")
    for name, k in (("k1p5", 1.5), ("k2p3", 2.3)):
        groups[name] = [j for j in arms if j["config"]["model"]["instrument"] == Instrument("A10", k, "linear").declaration()]
    groups["weight_corner"] = correct_runs(build_weight_corner_jobs(calibration_path, tables_path))
    groups["horizon"] = correct_runs(build_horizon_jobs(calibration_path, tables_path))
    counts = {"main": 24900, "k1p5": 4400, "k2p3": 4400, "weight_corner": 17600, "horizon": 1800}
    all_jobs = [j for jobs in groups.values() for j in jobs]
    if len({j["id"] for j in all_jobs}) != 53100 or len({j["seed"] for j in all_jobs}) != 53100:
        raise ValueError("stage 1 job or seed overlap")
    result = {}
    code = code_identity()
    for name, jobs in groups.items():
        if len(jobs) != counts[name]:
            raise ValueError("stage 1 job family is incomplete")
        phase, = {j["config"]["phase"] for j in jobs}
        cfg = deepcopy(max(jobs, key=lambda j: (j["config"]["model"]["successor_capability"],
                                              j["config"]["model"]["alpha"]))["config"])
        cfg.pop("a10_seed_source", None)
        cfg["steps"] = 5
        prof = profile("rerun", cfg)
        prof.update(workers_x2=[8, 12, 16, 24, 32], workers_local=[2, 4, 8, 12], jobs_per_worker=2)
        result[name] = {"schema": "v3-registered-1", "registered": True, "registered_a10": True,
                        "tag": "v3_rerun", "registration": registration, "code_hash": code,
                        "instrument": cfg["model"]["instrument"],
                        "wall_seconds": int((Decimal(str(ceilings[name])) * 3600).to_integral_value(rounding=ROUND_FLOOR)),
                        "x2_equivalent_hours": ceilings[name],
                        "configuration_seconds": 900, "cleanup_reserve_seconds": 300,
                        "phases": [phase], "configuration": {phase: prof}, "jobs": jobs, "publication": None}
    return result


# ---------------------------------------------------------------------------
# Stage 2 (A10 section 12): the c^0.5 arm and A6's variant arms on the corrected
# instrument. The run jobs come from the unchanged builders above, so every seed
# follows the registered rules. A6's global seed check (design note line 1381)
# is carried onto the A10 path through an A10-aware registry, built from the
# configurations before any stage 2 simulation and sealed; the spec builder then
# refuses any job set whose seeds differ from that registry.
# ---------------------------------------------------------------------------

STAGE2_FAMILIES = ("sqrt", "crowding", "sigma_squared_x10", "sigma_squared_x0.1")
STAGE2_RUN_COUNTS = {"sqrt": 4400, "crowding": 4400, "sigma_squared_x10": 500, "sigma_squared_x0.1": 500}
STAGE2_REGISTRY_SCHEMA = "v3-A10-stage2-seed-registry-1"


def _stage2_paths(paths):
    """``paths`` maps 'nominal' and each stage 2 family to its (calibration_path,
    tables_path) pair of strings. The path strings enter every job's seed (audit A
    finding 7), so they are parameters here, never literals."""
    names = ("nominal",) + STAGE2_FAMILIES
    if set(paths) != set(names):
        raise ValueError("stage 2 paths must name exactly nominal and the four stage 2 families")
    result = {}
    for name in names:
        pair = paths[name]
        if (not isinstance(pair, (list, tuple)) or len(pair) != 2
                or not all(isinstance(p, str) and p for p in pair)):
            raise ValueError("stage 2 path for %s must be a (calibration_path, tables_path) pair of strings" % name)
        result[name] = (pair[0], pair[1])
    return result


def stage2_runs(paths):
    """The four stage 2 run groups from the unchanged job builders: the c^0.5 arm
    from ``arm_runs`` on the nominal calibration against its own family, and A6's
    crowding and sigma0^2 arms from ``a6_runs``'s builders through ``correct_runs``.
    Seeds are those builders' seeds; nothing is redrawn."""
    from .sensitivity_a6 import build_crowding_jobs, build_sigma_jobs, SIGMA_VARIANTS
    paths = _stage2_paths(paths)
    nominal_cal, nominal_tables = paths["nominal"]
    arms = arm_runs(nominal_cal, nominal_tables, paths["sqrt"][1])
    groups = {"sqrt": [j for j in arms if j["config"]["model"]["instrument"] == Instrument("A10", 1.8, "sqrt").declaration()]}
    groups["crowding"] = correct_runs(build_crowding_jobs(*paths["crowding"]))
    for variant in SIGMA_VARIANTS:
        groups[variant] = correct_runs(build_sigma_jobs({variant: paths[variant]}))
    for name, jobs in groups.items():
        if len(jobs) != STAGE2_RUN_COUNTS[name]:
            raise ValueError("stage 2 run group %s is incomplete" % name)
    return groups


def _stage2_check_reserved(groups, reserved_ranges):
    """No new seed may fall in a reserved range. ``reserved_ranges`` is the
    caller's list of half-open [low, high) integer pairs (the A13 and A14
    extension ranges now; a later reserve is appended by the caller)."""
    from .sensitivity_a6 import SeedCollision
    ranges = []
    for pair in reserved_ranges:
        low, high = pair
        if isinstance(low, bool) or isinstance(high, bool) or not isinstance(low, int) or not isinstance(high, int) or not 0 <= low < high:
            raise ValueError("reserved ranges must be [low, high) integer pairs")
        ranges.append((low, high))
    for name, seeds in groups.items():
        for raw in seeds:
            s = int(raw)
            for low, high in ranges:
                if low <= s < high:
                    raise SeedCollision("%s seed %d lies in the reserved range [%d, %d)" % (name, s, low, high))
    return ranges


STAGE2_HISTORY_SCHEMA = "v3-A10-stage2-history-1"
# The categories a stage 2 history must carry, with the floor each must reach.
# A floor is a lower bound a partial inventory cannot meet, not the inventory's
# size: the R4 set holds the 24,900 rerun seeds plus every A1 job seed and
# stream; the stage 1 runs are exactly 53,100; the nominal family holds its
# 2,835 table job seeds plus their A4 and A5 streams; every other inventory
# holds at least one seed.
STAGE2_HISTORY_FLOORS = {"r4_forbidden": 24901, "a6_registry": 1, "nominal_family": 2835, "stage1_runs": 53100,
                         "a13_manifest": 1, "a14_manifest": 1, "qualification": 1, "configuration": 1, "rehearsal": 1}


def _stage2_check_history_counts(counts):
    """Refuse a history that lacks a category or is below its floor. The
    registered check is over every existing seed, so a partial history never
    satisfies it."""
    if set(counts) != set(STAGE2_HISTORY_FLOORS):
        raise ValueError("stage 2 history must carry exactly the categories %s" % sorted(STAGE2_HISTORY_FLOORS))
    if counts["stage1_runs"] != 53100:
        raise ValueError("stage 1 manifests must hold the 53,100 stage 1 run seeds; found %d" % counts["stage1_runs"])
    for name, floor in STAGE2_HISTORY_FLOORS.items():
        if counts[name] < floor:
            raise ValueError("stage 2 history category %s holds %d seeds, below its floor %d" % (name, counts[name], floor))


def _source_hash(document):
    """The hash of a sealed record, or the digest of a plain one."""
    if isinstance(document, dict) and set(document) == {"payload", "sha256"}:
        return document["sha256"]
    return digest(document)


def _seed_rows(rows):
    return sorted({int(row["seed"] if isinstance(row, dict) else row) for row in rows})


A6_REGISTRY_FAMILIES = ("crowding", "sigma_squared_x10", "sigma_squared_x0.1")
A6_REGISTRY_RUNS = ("nominal_runs", "crowding_runs", "sigma_squared_x10_runs", "sigma_squared_x0.1_runs")


def _inventory(name, value, *, declared_required=False):
    """An inventory is a list of seeds or manifest rows, or a mapping with
    ``seeds``, the ``declared_count`` of the launch record it comes from, and
    its ``sources``. The seeds must match a declared count exactly. The
    operational inventories (qualification, configuration, rehearsal) must use
    the mapping form with an explicit ``declared_count``: an integer, or null
    when the record carries no total, in which case the sources must be named.
    An absent total is recorded as absent, never invented."""
    if isinstance(value, dict):
        if not set(value) <= {"seeds", "declared_count", "sources"} or "seeds" not in value:
            raise ValueError("inventory %s must carry seeds and optionally declared_count and sources" % name)
        if declared_required and "declared_count" not in value:
            raise ValueError("inventory %s must state declared_count explicitly, an integer or null" % name)
        seeds = _seed_rows(value["seeds"])
        declared = value.get("declared_count")
        listed = list(value.get("sources", []))
        if declared is not None:
            if isinstance(declared, bool) or not isinstance(declared, int) or declared < 0:
                raise ValueError("inventory %s declared_count must be a non-negative integer" % name)
            if declared != len(seeds):
                raise ValueError("inventory %s holds %d distinct seeds against its declared count %d"
                                 % (name, len(seeds), declared))
        elif declared_required and not listed:
            raise ValueError("inventory %s has no declared total; name the records it comes from in sources" % name)
        return seeds, declared, listed, digest(value)
    if declared_required:
        raise ValueError("inventory %s must be a mapping with seeds, declared_count and sources" % name)
    return _seed_rows(value), None, [], digest(list(value))


def _a6_registry_seeds(registry):
    """The R4 A6 registry's seeds, checked for its three variant families, the
    five arms' run groups, and its own declared total."""
    for kind, names in (("table_jobs", A6_REGISTRY_FAMILIES), ("a4_streams", A6_REGISTRY_FAMILIES), ("runs", A6_REGISTRY_RUNS)):
        if not set(names) <= set(registry.get(kind, {})):
            raise ValueError("A6 seed registry lacks %s for %s" % (kind, sorted(set(names) - set(registry.get(kind, {})))))
    values = [int(s) for kind in ("table_jobs", "a4_streams", "runs") for v in registry[kind].values() for s in v]
    seeds = sorted(set(values))
    declared = registry.get("total_seeds")
    if not isinstance(declared, int) or declared != len(values) or len(seeds) != len(values):
        raise ValueError("A6 seed registry's declared total %r differs from its %d seeds" % (declared, len(seeds)))
    return seeds, declared


def stage2_history_seeds(nominal_calibration_path, *, r4_forbidden, a6_registry, stage1_manifests,
                         a13_manifest, a14_manifest, qualification, configuration, rehearsal):
    """The inventory of every seed that exists before stage 2, as a structured
    record with one category per source, assembled from the committed
    derivations and the sealed records:

    - ``r4_forbidden``: ``sensitivity_a6.forbidden_seeds`` over the registered A1
      root, the D26 probe root and the sealed 24,900-job rerun manifest (every A1,
      A4, A5, probe, planning and R4 rerun seed);
    - ``a6_registry``: the sealed A6 seed registry (schema v3-A6-seed-registry-1):
      the R4 variant table jobs, their streams and the five arms' R4 runs;
    - ``nominal_family``: the A10 nominal family's table jobs at
      ``nominal_calibration_path``, with their A4 stream superset and A5 streams;
    - ``stage1_manifests``: the five sealed stage 1 run specs, holding the 53,100
      stage 1 jobs between them;
    - ``a13_manifest`` and ``a14_manifest``: the A13 and A14 extension seed
      manifests, as rows with a ``seed`` or as seeds, each inside its reserved range;
    - ``qualification``, ``configuration`` and ``rehearsal``: the seeds those
      operations used, from the launch records and the A13 and A14 inventories.

    An extension manifest may be a list or a mapping ``{"seeds": [...],
    "declared_count": N, "sources": [...]}``; the operational inventories must be
    that mapping with ``declared_count`` stated explicitly (an integer, or null
    with the records named in ``sources``). Seeds must match a declared count
    exactly. The A6 registry must cover its
    three variant families and five run groups and match its own declared
    total. Every declared total, or its absence, is recorded. The floors are a
    sanity bound; every category is required and recorded with its count and
    source hashes, so a registry built on a partial history is refused by
    ``stage2_seed_registry`` and ``stage2_run_specs`` alike."""
    from .sensitivity_a6 import _a4_stream_superset
    from .table_labels_a5 import fvplain_seed, A5_REPLICATES
    from .validation_extension_a13 import RESERVED as A13_RESERVED
    from .validation_extension_a14 import RESERVED as A14_RESERVED
    categories, sources, declared_totals = {}, {}, {}
    categories["r4_forbidden"] = sorted({int(s) for s in r4_forbidden})
    declared_totals["r4_forbidden"] = None  # sensitivity_a6.forbidden_seeds carries no total of its own
    registry = unseal(a6_registry) if set(a6_registry) == {"payload", "sha256"} else a6_registry
    if registry.get("schema") != "v3-A6-seed-registry-1":
        raise ValueError("stage 2 history needs the sealed A6 seed registry")
    categories["a6_registry"], declared_totals["a6_registry"] = _a6_registry_seeds(registry)
    sources["a6_registry_sha256"] = _source_hash(a6_registry)
    nominal = set()
    for job in build_jobs("nominal", nominal_calibration_path):
        s = int(job["seed"])
        nominal.add(s)
        nominal.update(int(v) for v in _a4_stream_superset(s))
        if job["config"]["setting_name"] == "primary":
            nominal.update(int(fvplain_seed(s, r)) for r in A5_REPLICATES)
    categories["nominal_family"] = sorted(nominal)
    declared_totals["nominal_family"] = None  # derived here from build_jobs; no record declares it
    sources["nominal_calibration_path"] = str(nominal_calibration_path)
    stage1, hashes = set(), []
    for document in stage1_manifests:
        spec = unseal(document) if set(document) == {"payload", "sha256"} else document
        stage1.update(int(j["seed"]) for j in spec["jobs"])
        hashes.append(_source_hash(document))
    categories["stage1_runs"] = sorted(stage1)
    declared_totals["stage1_runs"] = 53100  # the registered count, A12 clarification of 2026-10-12
    sources["stage1_manifest_sha256"] = hashes
    for name, rows, low_high in (("a13_manifest", a13_manifest, A13_RESERVED), ("a14_manifest", a14_manifest, A14_RESERVED)):
        seeds, declared, listed, source_hash = _inventory(name, rows)
        if any(not low_high[0] <= s < low_high[1] for s in seeds):
            raise ValueError("%s holds a seed outside its reserved range" % name)
        categories[name], declared_totals[name] = seeds, declared
        sources[name + "_sha256"] = source_hash
        if listed:
            sources[name + "_sources"] = listed
    for name, rows in (("qualification", qualification), ("configuration", configuration), ("rehearsal", rehearsal)):
        seeds, declared, listed, source_hash = _inventory(name, rows, declared_required=True)
        categories[name], declared_totals[name] = seeds, declared
        sources[name + "_sha256"] = source_hash
        if listed:
            sources[name + "_sources"] = listed
    counts = {name: len(values) for name, values in categories.items()}
    _stage2_check_history_counts(counts)
    return {"schema": STAGE2_HISTORY_SCHEMA, "categories": categories, "counts": counts,
            "declared_totals": declared_totals, "sources": sources}


def stage2_seed_registry(paths, history, *, reserved_ranges):
    """A6's one global seed check on the A10 path, over the complete stage 2
    inventory, computed deterministically from the configurations:

    - every stage 2 estimation family's table job seeds (``build_jobs``);
    - the A4 validation streams each table job could derive, over both routes
      (fit, census and the three validate replicates), as A6's registry does;
    - A5's label streams over the c^0.5 family's primary table jobs. The three
      A6 variant families make no A5 labels (A6 line 1374; operator decision,
      2026-10-29), so no stream is reserved for them;
    - the four run groups of ``stage2_runs``.

    ``history`` is the structured inventory from ``stage2_history_seeds`` of every
    seed that exists already; every category must be present and above its
    floor. ``reserved_ranges`` lists the reserved integer ranges as [low, high)
    pairs (the A13 and A14 ranges now; a later reserve is one more pair).

    Every new seed must be disjoint from every history seed, from every reserved
    range and from every other new seed. A collision is a hard failure
    (SeedCollision), never a redraw. Returns the registry in sealed shape, with
    the history's counts and source hashes bound; ``stage2_run_specs`` requires it."""
    from .sensitivity_a6 import _a4_stream_superset, assert_global_seed_distinctness
    from .table_labels_a5 import fvplain_seed, A5_REPLICATES
    paths = _stage2_paths(paths)
    if not isinstance(history, dict) or history.get("schema") != STAGE2_HISTORY_SCHEMA:
        raise ValueError("stage 2 seed registry needs the structured history record")
    counts = {name: len(values) for name, values in history["categories"].items()}
    if counts != history.get("counts"):
        raise ValueError("stage 2 history counts do not match its categories")
    declared = history.get("declared_totals")
    if not isinstance(declared, dict) or set(declared) != set(counts):
        raise ValueError("stage 2 history must record a declared total, or its absence, for every category")
    for name, total in declared.items():
        if total is not None and total != counts[name]:
            raise ValueError("stage 2 history category %s holds %d seeds against its declared total %d" % (name, counts[name], total))
    _stage2_check_history_counts(counts)
    forbidden = {int(s) for values in history["categories"].values() for s in values}
    table_jobs, a4_streams, a5_streams = {}, {}, {}
    for family in STAGE2_FAMILIES:
        jobs = build_jobs(family, paths[family][0])
        table_jobs[family] = [int(j["seed"]) for j in jobs]
        a4_streams[family] = [int(v) for s in table_jobs[family] for v in _a4_stream_superset(s)]
        if family == "sqrt":
            a5_streams[family] = [int(fvplain_seed(int(j["seed"]), r)) for j in jobs
                                  if j["config"]["setting_name"] == "primary" for r in A5_REPLICATES]
    runs = {name: [int(j["seed"]) for j in jobs] for name, jobs in stage2_runs(paths).items()}
    groups = {}
    groups.update({"table_jobs:" + f: v for f, v in table_jobs.items()})
    groups.update({"a4_streams:" + f: v for f, v in a4_streams.items()})
    groups.update({"a5_streams:" + f: v for f, v in a5_streams.items()})
    groups.update({"runs:" + n: v for n, v in runs.items()})
    ranges = _stage2_check_reserved(groups, reserved_ranges)
    total = assert_global_seed_distinctness(groups, forbidden)
    return {"schema": STAGE2_REGISTRY_SCHEMA, "paths": {k: list(v) for k, v in paths.items()},
            "table_jobs": table_jobs, "a4_streams": a4_streams, "a5_streams": a5_streams, "runs": runs,
            "reserved_ranges": [list(r) for r in ranges],
            "history": {"schema": STAGE2_HISTORY_SCHEMA, "counts": counts, "declared_totals": declared,
                        "sources": history["sources"], "sha256": digest(history)},
            "forbidden_seeds": len(forbidden), "total_seeds": total}


def stage2_run_specs(paths, registration, ceilings, seed_registry):
    """Four complete A10 stage 2 run manifests, one per arm, so a family that
    cannot load reports only its own arm as not run (A6). Ceilings are explicit
    wall hours, one per arm, set by the dated amendment A10 section 12 requires.

    Job builders and their seeds are unchanged. ``seed_registry`` is the sealed
    registry from ``stage2_seed_registry`` for these exact paths; every group's
    seeds must equal its registry entry, and the four groups must be pairwise
    disjoint in identifier and seed."""
    import math
    from decimal import Decimal, ROUND_FLOOR
    from .artifacts import verify_registration
    from .pilot import profile
    from .sensitivity_a6 import assert_registry_seeds, assert_global_seed_distinctness
    paths = _stage2_paths(paths)
    if set(ceilings) != set(STAGE2_FAMILIES):
        raise ValueError("stage 2 needs exactly four explicit ceilings")
    for value in ceilings.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError("stage 2 ceilings must be positive and finite")
        if not math.isfinite(value * 3600) or value * 3600 < 1:
            raise ValueError("stage 2 ceiling must fit a positive wall-second budget")
    if seed_registry is None:
        raise ValueError("a registered stage 2 run spec requires the sealed A10 stage 2 seed registry")
    registry = unseal(seed_registry) if set(seed_registry) == {"payload", "sha256"} else seed_registry
    if registry.get("schema") != STAGE2_REGISTRY_SCHEMA or registry.get("paths") != {k: list(v) for k, v in paths.items()}:
        raise ValueError("stage 2 seed registry was not built for these paths")
    bound = registry.get("history") or {}
    if bound.get("schema") != STAGE2_HISTORY_SCHEMA or not isinstance(bound.get("counts"), dict):
        raise ValueError("stage 2 seed registry does not bind its history")
    _stage2_check_history_counts(bound["counts"])
    verify_registration(registration, instrument=NOMINAL)
    groups = stage2_runs(paths)
    all_jobs = [j for jobs in groups.values() for j in jobs]
    if len({j["id"] for j in all_jobs}) != 9800 or len({j["seed"] for j in all_jobs}) != 9800:
        raise ValueError("stage 2 job or seed overlap")
    assert_global_seed_distinctness({"runs:" + n: [j["seed"] for j in jobs] for n, jobs in groups.items()}, set())
    for name, jobs in groups.items():
        assert_registry_seeds(registry, "runs", name, [j["seed"] for j in jobs])
    result = {}
    code = code_identity()
    for name, jobs in groups.items():
        phase, = {j["config"]["phase"] for j in jobs}
        cfg = deepcopy(max(jobs, key=lambda j: (j["config"]["model"]["successor_capability"],
                                              j["config"]["model"]["alpha"]))["config"])
        cfg.pop("a10_seed_source", None)
        cfg["steps"] = 5
        prof = profile("rerun", cfg)
        prof.update(workers_x2=[8, 12, 16, 24, 32], workers_local=[2, 4, 8, 12], jobs_per_worker=2)
        result[name] = {"schema": "v3-registered-1", "registered": True, "registered_a10": True,
                        "tag": "v3_rerun", "registration": registration, "code_hash": code,
                        "instrument": cfg["model"]["instrument"], "a10_stage": 2, "a10_family": name,
                        "wall_seconds": int((Decimal(str(ceilings[name])) * 3600).to_integral_value(rounding=ROUND_FLOOR)),
                        "x2_equivalent_hours": ceilings[name],
                        "configuration_seconds": 900, "cleanup_reserve_seconds": 300,
                        "phases": [phase], "configuration": {phase: prof}, "jobs": jobs, "publication": None,
                        "seed_registry_sha256": digest(registry)}
    return result


def finalize_receipt(family_path, labels_path):
    """Bind the existing A4 publication and A5 labels without rewriting either."""
    family_path = Path(family_path)
    from .compatibility_a10 import accepted_identities
    accepted = accepted_identities()
    table = read(family_path)
    payload = unseal(table)
    p = payload["manifest"].get("a10")
    if not p or p["producer_code_hash"] not in accepted or payload["code_hash"] not in accepted:
        raise ValueError("not this A10 producer's family")
    a4_path = family_path.with_suffix(".compatibility.json")
    a4 = unseal(read(a4_path))
    labels_doc = read(labels_path)
    labels = unseal(labels_doc)
    if (a4["table_seal_sha256"] != table["sha256"] or a4["table_file_sha256"] != file_hash(family_path)
            or labels["a4_family"]["table_seal_sha256"] != table["sha256"]
            or labels["a4_family"]["family_file_sha256"] != file_hash(family_path)
            or a4.get("producer_code_hash") not in accepted or labels["code_hash"] not in accepted):
        raise ValueError("A10 validation or label provenance mismatch")
    receipt = seal({"schema": "v3-A10-table-receipt-1", "table_sha256": table["sha256"],
                    "producer_code_hash": code_identity(), "constants_sha256": CONSTANTS_SHA256,
                    "validation_receipt_sha256": file_hash(a4_path), "labels_sha256": file_hash(labels_path),
                    "validation_receipt": read(a4_path), "labels": labels_doc})
    target = family_path.with_suffix(".a10_receipt.json")
    if target.exists():
        existing = read(target)
        prior = unseal(existing)
        expected = dict(receipt["payload"], producer_code_hash=prior.get("producer_code_hash"))
        if prior.get("producer_code_hash") not in accepted or prior != expected:
            raise RuntimeError("A10 producer receipt is frozen")
        return existing
    atomic_json(target, receipt)
    return receipt


def main():
    import argparse
    from .artifacts import scoped
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("stage1-runs")
    p.add_argument("--calibration", required=True)
    p.add_argument("--tables", required=True)
    p.add_argument("--pin", required=True)
    p.add_argument("--ceilings", required=True, help="JSON mapping the five component names to wall hours")
    p.add_argument("--output-dir", required=True)
    p = commands.add_parser("stage2-runs")
    p.add_argument("--paths", required=True,
                   help="JSON mapping nominal and the four stage 2 families to [calibration_path, tables_path]")
    p.add_argument("--pin", required=True)
    p.add_argument("--ceilings", required=True, help="JSON mapping the four stage 2 arm names to wall hours")
    p.add_argument("--seed-registry", required=True, help="the sealed A10 stage 2 seed registry")
    p.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    if args.command == "stage2-runs":
        specs = stage2_run_specs(read(args.paths), read(args.pin), read(args.ceilings), read(args.seed_registry))
    else:
        specs = stage1_run_specs(args.calibration, args.tables, read(args.pin), read(args.ceilings))
    root = scoped(args.output_dir)
    for name, spec in specs.items():
        path = root / (name + ".json")
        document = seal(spec)
        if path.exists() and read(path) != document:
            raise RuntimeError(("stage 2 manifest is frozen: " if args.command == "stage2-runs"
                                else "stage 1 manifest is frozen: ") + str(path))
    for name, spec in specs.items():
        path = root / (name + ".json")
        atomic_json(path, seal(spec))
        print({"component": name, "jobs": len(spec["jobs"]), "wall_seconds": spec["wall_seconds"],
               "spec_sha256": file_hash(path)})


if __name__ == "__main__":
    main()
