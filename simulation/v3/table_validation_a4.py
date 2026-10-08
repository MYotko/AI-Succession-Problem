"""A4 validated continuation support: stages, assembly and publication.

D30, 2026-09-29. This module orchestrates the four A4 stages on the pinned A1
table family: the plain fitting stage (C0), validation (plain and FV) on fresh
seeds, the availability census, and publication of a new table family.

The stages run as jobs through the production runner: ``run_stage_job`` is the
entry point ``production_runner.execute`` dispatches to for the A4 job kinds.
The numerics live in ``continuation_validation``. This module never rewrites
the frozen A1 files. It computes no survival, extinction or fire rate, and it
never puts a raw endpoint count into the published family, a log or a report:
only fractions and assessed flags leave the census stage records.
"""
import dataclasses
import time
from pathlib import Path

import numpy as np

from .artifacts import (ROOT, SIMULATION, atomic_json, read, seal, unseal, digest, file_hash,
                        code_identity, configure_threads, scoped, lease, stable_job)
from . import continuation_validation as cv

A1_FILE_SHA256 = "56db71633a0f4710692e3354e3bc2fb5829286abbfa59e61609bd3f8cf6fcb3c"
AMENDMENT = "A4 adopted by D30, 2026-09-29; committed pin required"
CENSUS_STEPS = 500
CENSUS_HORIZON = 20
CENSUS_MEASURE = CENSUS_HORIZON + CENSUS_STEPS - 1  # 519

# The five registered phases, in order. FV doubled-population is separate
# because its tasks need about 19 GB.
PHASES = ("fit", "validate_plain", "validate_fv_primary", "validate_fv_double_population", "census")


# ---------------------------------------------------------------------------
# Traces from A1 outputs
# ---------------------------------------------------------------------------

class TableTrace:
    """A validation trace for one A1 table job, on a derived stream seed."""

    def __init__(self, a1_output, seed, settings_override=None):
        from .context import Context
        from .offline_estimator import simulate, _rule, score_features
        self._score_features = score_features
        result = a1_output["result"]
        self.route = result["route"]
        config = a1_output["job"]["config"]
        calibration = read(SIMULATION / Path(config["calibration_path"])) if config.get("calibration_path") else None
        self.context = Context.build(result["kernel"], calibration)
        settings = {**result["settings"], "groups": cv.GROUPS}
        if settings_override:
            settings.update(settings_override)
        self.settings = settings
        self.seed = seed
        trace = simulate(self.context, _rule(result["rows"][0]["rule_id"]), settings, seed, self.route)
        source_initial = np.ones((1, len(trace["groups"])), dtype=bool)
        # A10 continuation fitting and validation start with a full history.
        if self.context.instrument.a10:
            source_initial = trace["conditioned"][29:30, :, 0] > 0
            for field in ("features", "conditioned", "before", "after", "support", "deaths"):
                trace[field] = trace[field][30:]
        self.features = trace["features"]
        conditioned = trace["conditioned"]
        length, self.count = trace["before"].shape[:2]
        self.length = length
        self.collapsed = trace["collapsed"]
        self.collapsed_groups = len({c["group"] for c in trace["collapsed"]})
        self.requested_length = max(0, settings["burn"] + settings["measure"] - (30 if self.context.instrument.a10 else 0))
        self.truncated = length < self.requested_length
        self.truncated_steps = self.requested_length - length
        self.traj = np.broadcast_to(np.arange(self.count)[None, :], (length, self.count)).ravel()
        self.group_of = np.broadcast_to(trace["groups"][None, :], (length, self.count)).ravel()
        self.n_groups = settings["groups"]
        self.before = trace["before"].reshape(-1, 6)
        self.after = trace["after"].reshape(-1, 6)
        if self.before.size and (self.before.min() < 0 or self.before.max() > 7 or self.after.min() < 0 or self.after.max() > 7):
            raise cv.OutOfRange("bin coordinates out of range")
        # The next-state (post-advance, pre-resampling) population gives the
        # extinct-next indicator; the living-source mask uses the conditioned
        # (resampled) state of the previous step, so an FV clone of a dead
        # particle counts as a living source. For plain, conditioned == features.
        alive_next = self.features[..., 0] > 0
        self.dead = (~alive_next).ravel()
        cond_alive = conditioned[..., 0] > 0
        self.source_alive = np.concatenate((source_initial, cond_alive[:-1])).ravel()
        self.lower = self.context.parameters.extinction_flow
        self.upper = self.context.parameters.upper_bound

    def flows(self, scoring):
        ctx = dataclasses.replace(self.context,
                                  parameters=dataclasses.replace(self.context.parameters, kappa=scoring.get("kappa", 8.0)))
        if ctx.instrument.a10:
            from .instrument import Instrument
            ctx = dataclasses.replace(ctx, instrument=Instrument("A10", scoring.get("k_star", ctx.instrument.k_star), ctx.instrument.g))
        return self._score_features(self.features, ctx, scoring["alpha"], scoring["capability"]).ravel()


def a1_published_plain(entries):
    """Published A1 cells with population category above zero, by fine code."""
    values = {}
    for e in entries:
        if e["bin"][0] != 0:
            values[int(cv.fine_codes([e["bin"]])[0])] = e["value"]
    return values


def a1_published_fv(entries):
    """Every published A1 FV cell, by fine code, with its value and error."""
    return {int(cv.fine_codes([e["bin"]])[0]): {"value": e["value"], "error": e["error"]} for e in entries}


def _entries(row):
    return (row.get("continuation") or {}).get("entries") or []


# ---------------------------------------------------------------------------
# Stage compute
# ---------------------------------------------------------------------------

def fit_stage(a1_output, seed, override=None):
    """C0 for every plain row of an A1 job, on the fitting replicate."""
    if a1_output["result"]["route"] != "plain":
        raise ValueError("fit stage is plain-route only")
    tr = TableTrace(a1_output, seed, override)
    src, nxt = cv.plain_cell_codes(tr.before), cv.plain_cell_codes(tr.after)
    rows = []
    for row in a1_output["result"]["rows"]:
        flows = tr.flows(row["scoring"])
        cv.check_in_range(flows, tr.lower, tr.upper, "flow")
        published = a1_published_plain(_entries(row))
        cv.check_in_range(list(published.values()) or [tr.lower], tr.lower, tr.upper, "A1 value")
        c0 = cv.refit_c0(src, nxt, tr.source_alive, tr.dead, flows, published, tr.lower)
        rows.append({"scoring": row["scoring"], "c0": c0})
    return {"stage": "fit", "a1_job_id": a1_output["job"]["id"], "seed": int(seed), "route": "plain",
            "settings": tr.settings, "collapsed": tr.collapsed, "collapsed_groups": tr.collapsed_groups,
            "truncated": bool(tr.truncated), "truncated_steps": tr.truncated_steps, "count": tr.count, "rows": rows}


def validate_stage(a1_output, fit_result, replicate, seed, override=None):
    """Sufficient statistics per cell on one validation replicate."""
    route = a1_output["result"]["route"]
    tr = TableTrace(a1_output, seed, override)
    src_plain, nxt_plain = cv.plain_cell_codes(tr.before), cv.plain_cell_codes(tr.after)
    src_fine, nxt_fine = cv.fine_codes(tr.before), cv.fine_codes(tr.after)
    rows = []
    for i, row in enumerate(a1_output["result"]["rows"]):
        flows = tr.flows(row["scoring"])
        cv.check_in_range(flows, tr.lower, tr.upper, "flow")
        flow_min, flow_max = (float(flows.min()), float(flows.max())) if flows.size else (tr.lower, tr.upper)
        entries = _entries(row)
        if route == "plain":
            values = a1_published_plain(entries)
            c0 = fit_result["rows"][i]["c0"]
            if c0["value"] is not None and c0["published"]:
                values[int(cv.POP0_CELL)] = c0["value"]
            residual, covered, srcidx, codes = cv.living_source_residuals(
                src_plain, nxt_plain, tr.source_alive, tr.dead, flows, values, tr.lower)
            sums = cv.trajectory_sums(srcidx[covered], tr.traj[covered], residual[covered], len(codes), tr.count)
            cells = [{"cell": int(c), **{k: (int(v[j]) if k == "n_traj" else float(v[j])) for k, v in sums.items()}}
                     for j, c in enumerate(codes.tolist()) if sums["n_traj"][j] > 0]
        else:
            fv = a1_published_fv(entries)
            cv.check_in_range([v["value"] for v in fv.values()] or [tr.lower], tr.lower, tr.upper, "FV A1 value")
            values = {c: v["value"] for c, v in fv.items()}
            residual, covered, srcidx, codes = cv.living_source_residuals(
                src_fine, nxt_fine, tr.source_alive, tr.dead, flows, values, tr.lower)
            g = cv.group_sums(srcidx[covered], tr.group_of[covered], residual[covered], len(codes), tr.n_groups)
            cells = [{"cell": int(c), "S_g": g["S_g"][j].tolist(), "N_g": g["N_g"][j].tolist()}
                     for j, c in enumerate(codes.tolist()) if g["N_g"][j].sum() > 0]
        rows.append({"scoring": row["scoring"], "route": route, "flow_range": row["flow_range"],
                     "flow_within_range": bool(tr.lower - 1e-9 <= flow_min and flow_max <= tr.upper + 1e-9),
                     "cells": cells})
    return {"stage": "validate", "a1_job_id": a1_output["job"]["id"], "seed": int(seed), "replicate": replicate,
            "route": route, "settings": tr.settings, "collapsed": tr.collapsed, "collapsed_groups": tr.collapsed_groups,
            "truncated": bool(tr.truncated), "truncated_steps": tr.truncated_steps, "count": tr.count, "rows": rows}


def census_stage(a1_output, seed, override=None):
    """Per-cell living-endpoint counts under the committed census law.

    Uses the job's own A1 settings (6 groups), burn 0, measure 519, the plain
    route, held-out groups only. Stores per-cell living-endpoint counts by fine
    code, not raw endpoints. The low-population split is derivable (fine code a
    multiple of 8). Blind: only counts leave here, and only fractions leave the
    family."""
    from .context import Context
    from .offline_estimator import simulate, _rule
    result = a1_output["result"]
    config = a1_output["job"]["config"]
    calibration = read(SIMULATION / Path(config["calibration_path"])) if config.get("calibration_path") else None
    ctx = Context.build(result["kernel"], calibration)
    settings = {**result["settings"], "burn": 0, "measure": CENSUS_MEASURE}
    if override:
        settings.update({k: v for k, v in override.items() if k in ("burn", "measure", "runs_per_group", "groups")})
        if "census_measure" in override:
            settings["measure"] = override["census_measure"]
    trace = simulate(ctx, _rule(result["rows"][0]["rule_id"]), settings, seed, "plain")
    groups = trace["groups"]
    heldout = groups >= int(np.max(groups)) - 1
    alive = trace["features"][..., 0] > 0
    steps = settings["measure"] - CENSUS_HORIZON + 1
    start = np.concatenate((np.ones((1, alive.shape[1]), dtype=bool), alive[:steps - 1]))[:, heldout]
    end = alive[CENSUS_HORIZON - 1:CENSUS_HORIZON - 1 + steps, heldout]
    ends = trace["after"][CENSUS_HORIZON - 1:CENSUS_HORIZON - 1 + steps, heldout].reshape(-1, 6)
    live = (start & end).ravel()
    endpoints = ends[live]
    codes = cv.fine_codes(endpoints)
    uniq, counts = np.unique(codes, return_counts=True)
    cell_counts = {int(c): int(n) for c, n in zip(uniq.tolist(), counts.tolist())}
    total = int(len(endpoints))
    total_low = int(sum(n for c, n in cell_counts.items() if c % 8 == 0))
    return {"stage": "census", "a1_job_id": a1_output["job"]["id"], "seed": int(seed),
            "law": "held-out plain fixed-rule paths, 20-step endpoints over 500 starts, living endpoints only",
            "settings": settings, "cell_counts": cell_counts, "total_living": total, "total_low": total_low}


# ---------------------------------------------------------------------------
# The runner entry point
# ---------------------------------------------------------------------------

def selected_a1_jobs(source_root):
    """The A1 table jobs, from the frozen A1 manifest, in manifest order."""
    return unseal(read(Path(source_root) / "tables_A1_manifest.json"))["jobs"]


def _source_code_hash(source_root):
    manifest = unseal(read(Path(source_root) / "tables_A1_manifest.json"))
    return manifest.get("source_family", {}).get("code_hash") or manifest.get("code_hash")


def _load_a1(source_root, a1_job, source_code):
    from .production_runner import completed
    a1 = completed(Path(source_root) / "tables_A1/table", a1_job, source_code)
    if a1 is None:
        raise ValueError("A1 job missing or changed: %s" % a1_job["id"])
    return a1


def _fit_job_id(c):
    """The plain fit job id for the A1 job this validate config references,
    reconstructed deterministically so no fit_job_id must be embedded before
    plan_hash exists."""
    fit_cfg = {"a1_source_root": c["a1_source_root"], "a1_job": c["a1_job"],
               "a1_source_code_hash": c["a1_source_code_hash"], "stage": "fit", "route": "plain",
               "seed": cv.fit_seed(c["a1_job"]["seed"]), "plan_hash": c["plan_hash"]}
    if "settings_override" in c:
        fit_cfg["settings_override"] = c["settings_override"]
    return _a4_job(fit_cfg, "fit")["id"]


def run_stage_job(job, root):
    """Execute one A4 stage job. ``production_runner.execute`` dispatches here.

    The A4 stream seed travels in ``job['config']['seed']``; the runner's own
    ``job['seed']`` is unused. For a plain validate job the fitting replicate's
    output is read from the sibling fit phase root."""
    c = job["config"]
    source_root = c["a1_source_root"]
    a1 = _load_a1(source_root, c["a1_job"], c["a1_source_code_hash"])
    override = c.get("settings_override")
    if c["stage"] == "fit":
        result = fit_stage(a1, c["seed"], override)
    elif c["stage"] == "census":
        result = census_stage(a1, c["seed"], override)
    elif c["stage"] == "validate":
        fit_result = None
        if c["route"] == "plain":
            if c.get("self_contained"):
                # Configuration-test task: fit inline, needing no fit sibling.
                fit_result = fit_stage(a1, cv.fit_seed(c["a1_job"]["seed"]), override)
            else:
                fit_id = _fit_job_id(c)
                fit_output = read(Path(root).parent / "fit" / "outputs" / (fit_id + ".json"))
                fit_result = fit_output.get("result", fit_output)
        result = validate_stage(a1, fit_result, c["replicate"], c["seed"], override)
    else:
        raise ValueError("unknown A4 stage %r" % c["stage"])
    # Identity: bind the A1 job, stream seed, settings, code and plan.
    result.update(a1_job_id=c["a1_job"]["id"], stream_seed=int(c["seed"]), plan_hash=c["plan_hash"],
                  code_hash=code_identity())
    return result


# ---------------------------------------------------------------------------
# M and M_FV, and probe seeds, from the A1 records
# ---------------------------------------------------------------------------

def counts_from_job_outputs(source_root, source_code=None):
    """M and M_FV from every A1 job output row, primary and sensitivity, any
    status, as A4 defines them."""
    from .production_runner import completed
    source_root = Path(source_root)
    source_code = source_code or _source_code_hash(source_root)
    manifest = unseal(read(source_root / "tables_A1_manifest.json"))
    plain_rows, fv_rows = [], []
    for job in manifest["jobs"]:
        a1 = _load_a1(source_root, job, source_code)
        for row in a1["result"]["rows"]:
            (plain_rows if row.get("route") == "plain" else fv_rows).append(row)
    return {"M": cv.count_M_plain(plain_rows), "M_FV": cv.count_M_fv(fv_rows),
            "plain_rows": len(plain_rows), "fv_rows": len(fv_rows)}


def load_probe_seeds(a3_probe_root):
    """Every D26 probe job seed found under the a3_probe records."""
    seeds = set()
    root = Path(a3_probe_root)
    if not root.exists():
        return seeds
    for path in root.rglob("*.json"):
        try:
            doc = read(path)
        except Exception:
            continue
        stack = [doc]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                if isinstance(item.get("seed"), int):
                    seeds.add(item["seed"])
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
    return seeds


# ---------------------------------------------------------------------------
# Memory estimate and phase assignment
# ---------------------------------------------------------------------------

# Arithmetic per-task memory, anchored on a measured A4 peak: the heaviest FV
# primary task (32 groups x 256 particles x 3,072 steps; 150 rows, 13,650
# published cells), run with this code on a planning seed on 2026-09-29, peaked
# at 5.56 GB. The anchor adds a 20% margin. (The first anchor, 9.5 GB, came from
# the planning code and held the FV phases to 10 and 5 workers.) Memory scales
# with population x length (the (length, count, features) arrays); the fixed
# overhead does not, so scaling up from the anchor is conservative.
ANCHOR_GB = 6.7
ANCHOR_CELLS = 32 * 256 * (1024 + 2048)


def estimate_memory_gb(route, settings):
    per_group = settings["particles"] if route == "fv" else settings["runs_per_group"]
    cells = settings["groups"] * per_group * (settings["burn"] + settings["measure"])
    return ANCHOR_GB * cells / ANCHOR_CELLS


def fv_phase(setting_name):
    # Double-length FV keeps 256 particles but doubles length to about 19 GB,
    # so it joins the doubled-population FV jobs in the high-memory phase.
    return "validate_fv_double_population" if setting_name in ("double_population", "double_length") else "validate_fv_primary"


def _a1_settings(a1_output):
    return {**a1_output["result"]["settings"], "groups": cv.GROUPS}


# ---------------------------------------------------------------------------
# Sealed plan (prepare)
# ---------------------------------------------------------------------------

def _a4_job(config, phase):
    return stable_job("a4_" + config["stage"], {**config, "phase": phase}, "v3_tables", 0)


def prepare(source_root, calibration_path, registration=None, wall_hours=48, a3_probe_root=None, settings_override=None,
            instrument=None):
    """A sealed A4 plan with the five phased job lists, pinned M, M_FV and
    per-phase memory estimates.

    Pure: launches nothing and reads no rerun output. Refuses a missing or empty
    probe root, and asserts seed distinctness across all jobs including the D26
    probe seeds. ``plan_hash`` binds the source identity, M, M_FV, the code, the
    settings override, the registration and the full job skeleton."""
    source_root = Path(source_root)
    from .instrument import declaration
    instrument = declaration(instrument)
    if instrument.a10:
        from .tables_a10 import verify_estimation_source
        verify_estimation_source(source_root, calibration_path, registered=registration is not None)
    actual_a1 = file_hash(source_root / "v3_rerun_tables_A1.json")
    if registration is not None and not instrument.a10 and actual_a1 != A1_FILE_SHA256:
        raise ValueError("A1 source publication changed")
    # Registered runs pin the canonical A1 file; a fixture (smoke) run records the
    # actual source hash so a synthetic small family can run end to end.
    source_file_sha256 = A1_FILE_SHA256 if registration is not None and not instrument.a10 else actual_a1
    manifest = unseal(read(source_root / "tables_A1_manifest.json"))
    source_code = _source_code_hash(source_root)
    counts = counts_from_job_outputs(source_root, source_code)

    probe_seeds = load_probe_seeds(a3_probe_root) if a3_probe_root else set()
    if not probe_seeds:
        raise ValueError("A4 prepare requires a non-empty D26 probe root; none found under %r" % a3_probe_root)

    # First pass: build the job skeletons (no plan_hash yet) and check seeds.
    a1_seeds = {j["seed"] for j in manifest["jobs"]}
    all_stream, forbidden = {}, set(a1_seeds) | set(probe_seeds)
    skeletons, phase_estimates = [], {p: 0.0 for p in PHASES}
    for job in manifest["jobs"]:
        a1 = _load_a1(source_root, job, source_code)
        route = a1["result"]["route"]
        settings = _a1_settings(a1)
        base = {"a1_source_root": str(source_root.resolve()), "a1_job": job, "a1_source_code_hash": source_code}
        if settings_override:
            base["settings_override"] = settings_override
        seeds = cv.assert_seeds_distinct(job["seed"], route, probe_seeds=probe_seeds)
        for name, value in seeds.items():
            if value in all_stream.values() or value in forbidden:
                raise cv.SeedCollision("cross-job seed collision: %r -> %r" % ((job["id"], name), value))
            all_stream[(job["id"], name)] = value
        if route == "plain":
            skeletons.append(({**base, "stage": "fit", "route": "plain", "seed": cv.fit_seed(job["seed"])}, "fit"))
            for r in cv.VALIDATE_REPLICATES:
                skeletons.append(({**base, "stage": "validate", "route": "plain", "replicate": r,
                                   "seed": cv.validate_seed(job["seed"], r), "fit_a1_job_id": job["id"]}, "validate_plain"))
            phase_estimates["fit"] = max(phase_estimates["fit"], estimate_memory_gb("plain", settings))
            phase_estimates["validate_plain"] = max(phase_estimates["validate_plain"], estimate_memory_gb("plain", settings))
        else:
            phase = fv_phase(job["config"].get("setting_name", "primary"))
            skeletons.append(({**base, "stage": "validate", "route": "fv", "replicate": cv.FV_VALIDATE_REPLICATE,
                               "seed": cv.validate_seed(job["seed"], cv.FV_VALIDATE_REPLICATE)}, phase))
            phase_estimates[phase] = max(phase_estimates[phase], estimate_memory_gb("fv", settings))
        census_settings = {**settings, "burn": 0, "measure": CENSUS_MEASURE, "groups": a1["result"]["settings"]["groups"]}
        skeletons.append(({**base, "stage": "census", "route": "plain", "seed": cv.census_seed(job["seed"])}, "census"))
        phase_estimates["census"] = max(phase_estimates["census"], estimate_memory_gb("plain", census_settings))

    plan_core = {"schema": "v3-A4-validation-1", "amendment": AMENDMENT, "registered": bool(registration),
                 "tag": "v3_tables", "code_hash": code_identity(), "source_root": str(source_root.resolve()),
                 "source_file_sha256": source_file_sha256, "source_manifest_sha256": digest(manifest),
                 "source_code_hash": source_code, "calibration_path": calibration_path,
                 "wall_seconds": wall_hours * 3600, "cleanup_reserve_seconds": 1200, "configuration_seconds": 1800,
                 "phases": list(PHASES), "M": counts["M"], "M_FV": counts["M_FV"],
                 "groups": cv.GROUPS, "alpha": cv.ALPHA, "min_visits": cv.MIN_VISITS,
                 "validate_replicates": list(cv.VALIDATE_REPLICATES), "fv_validate_replicate": cv.FV_VALIDATE_REPLICATE,
                 "fit_replicate": cv.FIT_REPLICATE, "census_replicate": cv.CENSUS_REPLICATE,
                 "stream_tags": list(cv.STREAM_TAGS), "settings_override": settings_override,
                 "memory_estimate_gb": phase_estimates,
                 "memory_basis": "arithmetic, anchored on the FV primary planning peak of 9.5 GB, scaling with population x length"}
    plan_hash = digest({**{k: plan_core[k] for k in ("schema", "source_file_sha256", "source_manifest_sha256",
                                                     "source_code_hash", "M", "M_FV", "code_hash", "settings_override")},
                        "registration": registration, "job_skeleton": [(c, p) for c, p in skeletons]})
    plan_core["plan_hash"] = plan_hash

    jobs = [_a4_job({**config, "plan_hash": plan_hash}, phase) for config, phase in skeletons]
    if len({j["id"] for j in jobs}) != len(jobs):
        raise ValueError("duplicate A4 job identifier")

    # Each phase's configuration test times real tasks of that phase's own kind,
    # shortened in length only so populations (and memory) stay representative.
    # A self-contained validate config job fits C0 inline, needing no fit
    # sibling in the isolated configuration root.
    plan_core["configuration"] = _configuration_profiles(source_root, source_code, manifest, plan_hash, settings_override)
    plan_core.update(jobs=jobs, registration=registration,
                     probe_seed_count=len(probe_seeds), stream_seed_count=len(all_stream))
    if instrument.a10:
        plan_core.update(instrument=instrument.declaration(), registered_a10=bool(registration),
                         x2_equivalent_hours=wall_hours)
    return plan_core


def _configuration_profiles(source_root, source_code, manifest, plan_hash, settings_override):
    """One profile per phase, of that phase's own kind, length-shortened."""
    short = {"burn": 8, "measure": 24, "census_measure": 44}
    if settings_override:
        short = {**short, **{k: v for k, v in settings_override.items() if k in short}}
    reps = {}
    for job in manifest["jobs"]:
        a1 = _load_a1(source_root, job, source_code)
        route = a1["result"]["route"]
        setting = job["config"].get("setting_name", "primary")
        base = {"a1_source_root": str(Path(source_root).resolve()), "a1_job": job,
                "a1_source_code_hash": source_code, "plan_hash": plan_hash, "settings_override": short}
        reps.setdefault("census_cfg", {**base, "stage": "census", "route": "plain", "seed": cv.census_seed(job["seed"])})
        reps.setdefault("fit" if route == "plain" else None, None)
        if route == "plain":
            reps.setdefault("fit_cfg", {**base, "stage": "fit", "route": "plain", "seed": cv.fit_seed(job["seed"])})
            reps.setdefault("validate_plain_cfg", {**base, "stage": "validate", "route": "plain", "replicate": 1,
                                                   "seed": cv.validate_seed(job["seed"], 1), "self_contained": True})
            reps.setdefault("census_cfg", {**base, "stage": "census", "route": "plain", "seed": cv.census_seed(job["seed"])})
        else:
            phase = fv_phase(setting)
            reps.setdefault(phase + "_cfg", {**base, "stage": "validate", "route": "fv", "replicate": 1,
                                             "seed": cv.validate_seed(job["seed"], 1), "self_contained": True})
    profiles = {}
    layout = {"fit": ("a4_fit", "fit_cfg"), "validate_plain": ("a4_validate", "validate_plain_cfg"),
              "validate_fv_primary": ("a4_validate", "validate_fv_primary_cfg"),
              "validate_fv_double_population": ("a4_validate", "validate_fv_double_population_cfg"),
              "census": ("a4_census", "census_cfg")}
    for phase, (kind, key) in layout.items():
        cfg = reps.get(key) or reps["census_cfg"]  # fall back to census if a route is absent
        profiles[phase] = {"kind": kind, "config": cfg, "configs": [cfg], "jobs_local": 4, "jobs_x2": 32,
                           "workers_local": [2, 4], "workers_x2": [8, 12, 16, 24, 32], "threads": [1], "rounds": 1,
                           "jobs_per_worker": 2, "shortened_length_only": True}
    return profiles


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------

def a1_base_screens_ok(a1_row):
    """Rebuild A1's own screens, dropping the continuation-residual condition:
    route, flow half-width, half-window drift, held-out coverage >= 0.9, and
    fixed-point convergence."""
    screens = a1_row.get("screens") or {}
    cont = a1_row.get("continuation") or {}
    return bool(screens.get("route_applicable") and screens.get("flow_half_width") and screens.get("half_window_drift")
                and cont.get("heldout_coverage", 0) >= 0.9 and cont.get("training_fixed_point_converged"))


def _row_vmax(published_values, c0):
    values = list(published_values.values())
    if c0 is not None and c0.get("value") is not None and c0.get("published"):
        values.append(c0["value"])
    return max(values) if values else None


def assemble_plain_row(a1_row, fit_row, combined_cells, M, tau, lower, upper):
    published = a1_published_plain(_entries(a1_row))
    c0 = fit_row["c0"] if fit_row else {"value": None, "published": False}
    vmax = _row_vmax(published, c0)
    if vmax is None:
        return {"support": [], "support_values": {}, "c0": None, "cells": [], "vmax": None, "width": None}
    cv.check_in_range(list(published.values()) + ([c0["value"]] if c0["value"] is not None else []), lower, upper, "A1/C0 value")
    width = cv.row_width(a1_row["flow_range"], vmax, lower, upper)
    tests, support, c0_result = [], {}, None
    for cell_code, stat in combined_cells.items():
        eb = cv.empirical_bernstein(stat["sum_m"], stat["sum_m2"], stat["n_traj"], width, M, tau)
        safeguard = cv.visit_weighted_ok(stat["sum_S"], stat["sum_N"], tau)
        passed = eb["status"] == "certified" and safeguard
        tests.append({"cell": int(cell_code), "eb": eb["status"], "visit_weighted_ok": bool(safeguard),
                      "n_traj": stat["n_traj"], "visits": stat["sum_N"], "published_and_passed": bool(passed)})
        if cell_code == cv.POP0_CELL:
            if passed and c0["value"] is not None and c0["published"]:
                c0_result = {"value": c0["value"], "error": max(c0["value"] - lower, upper - c0["value"])}
                support[int(cell_code)] = c0["value"]
        elif passed:
            support[int(cell_code)] = published.get(int(cell_code))
    return {"support": sorted(support), "support_values": support, "c0": c0_result, "cells": tests,
            "vmax": vmax, "width": width}


def assemble_fv_row(a1_row, combined_cells, M_fv, tau):
    published = a1_published_fv(_entries(a1_row))
    support, tests = {}, []
    for cell_code, gs in combined_cells.items():
        result = cv.fv_cell_test(np.asarray(gs["S_g"]), np.asarray(gs["N_g"]), M_fv, tau)
        passed = result["status"] == "passed"
        tests.append({"cell": int(cell_code), "status": result["status"], "n": result["n"],
                      "visits": float(np.asarray(gs["N_g"]).sum()), "passed": bool(passed)})
        if passed and int(cell_code) in published:
            support[int(cell_code)] = published[int(cell_code)]
    return {"support": sorted(support), "support_values": support, "cells": tests,
            "label": "asymptotic, not certified"}


def _combine_plain(replicate_outputs, row_index):
    combined = {}
    for out in replicate_outputs:
        for cell in out["rows"][row_index]["cells"]:
            acc = combined.setdefault(cell["cell"], dict.fromkeys(cv.STAT_KEYS, 0.0))
            for k in cv.STAT_KEYS:
                acc[k] += cell[k]
    return combined


def _combine_fv(replicate_output, row_index):
    return {cell["cell"]: {"S_g": cell["S_g"], "N_g": cell["N_g"]} for cell in replicate_output["rows"][row_index]["cells"]}


def numerical_contrast(primary, other):
    """Same arithmetic and threshold as study.assemble_tables / A3."""
    import math
    a, b = primary.get("lambda_f"), other.get("lambda_f")
    if not a or not b or a.get("mean") is None or b.get("mean") is None:
        return {"passed": False, "reason": "contrast unavailable"}
    av, bv = np.asarray(a["replicates"]), np.asarray(b["replicates"])
    half = 2.015 * math.sqrt(float(av.var(ddof=1) / len(av) + bv.var(ddof=1) / len(bv)))
    difference = b["mean"] - a["mean"]
    threshold = 0.05 * primary["flow_range"]
    return {"passed": bool(abs(difference) + half <= threshold), "difference": difference,
            "interval90": [difference - half, difference + half], "threshold": threshold}


def assemble_family(source_root, source_code, stage_root, M, M_fv, calibrations):
    """Assemble the full A4 family from the stage outputs, primary and
    sensitivity rows separately, with A4-rebuilt statuses and sensitivity
    contrasts. ``stage_root`` holds the phase subdirectories."""
    from .production_runner import completed
    from .production_tables import row_key
    from .offline_estimator import SENSITIVITY_RULES, SENSITIVITY_RR
    from .context import Context
    source_root, stage_root = Path(source_root), Path(stage_root)
    manifest = unseal(read(source_root / "tables_A1_manifest.json"))
    # Index every stage output once by A1 job id; a per-job glob-and-read would
    # be quadratic across the 343-job family.
    fit_index = _index_phase(stage_root, "fit")
    census_index = _index_phase(stage_root, "census")
    validate_index = {}
    for phase in ("validate_plain", "validate_fv_primary", "validate_fv_double_population"):
        for jid, results in _index_phase(stage_root, phase).items():
            validate_index.setdefault(jid, []).extend(results)
    primary, sensitivity, rates, details = {}, {}, {}, []
    for job in manifest["jobs"]:
        a1 = _load_a1(source_root, job, source_code)
        route = a1["result"]["route"]
        setting_name = job["config"].get("setting_name", "primary")
        rr = job["config"]["kernel"]["reproduction_rate"]
        # Calibrations are keyed by content hash, not by path string.
        cal = calibrations[a1["result"]["calibration_hash"]]
        params = Context.build(a1["result"]["kernel"], cal).parameters
        lower, upper = params.extinction_flow, params.upper_bound
        fit_out = (fit_index.get(job["id"]) or [None])[0] if route == "plain" else None
        census_hits = census_index.get(job["id"])
        if not census_hits:
            raise ValueError("missing census stage output for A1 job %s" % job["id"])
        census_out = census_hits[0]
        validate_outs = sorted(validate_index.get(job["id"], []), key=lambda r: r.get("replicate", 0))
        if not validate_outs:
            raise ValueError("missing validate outputs for A1 job %s" % job["id"])
        cells_of = {}
        collapse = None
        if route == "fv" and validate_outs and validate_outs[0].get("collapsed"):
            collapse = {"collapsed_groups": validate_outs[0].get("collapsed_groups", len(validate_outs[0]["collapsed"])),
                        "truncated_steps": validate_outs[0].get("truncated_steps", 0),
                        "transitions_lost": validate_outs[0].get("truncated_steps", 0) * validate_outs[0].get("count", 0)}
        for i, a1_row in enumerate(a1["result"]["rows"]):
            tau = 0.05 * a1_row["flow_range"]
            base_ok = a1_base_screens_ok(a1_row)
            new_row = dict(a1_row)
            # Preserve A1's own failure reason; A4 rebuilds status from scratch.
            new_row["a1_reason"] = a1_row.get("reason")
            new_row["a1_primary_reason"] = a1_row.get("primary_reason") if a1_row.get("primary_reason") is not None else a1_row.get("reason")
            new_row.pop("reason", None)
            new_row.pop("primary_reason", None)
            if route == "plain":
                built = assemble_plain_row(a1_row, fit_out["rows"][i] if fit_out else None,
                                           _combine_plain(validate_outs, i), M, tau, lower, upper)
                support_codes = set(built["support_values"])
                new_row["c0"] = built["c0"]
                new_row["continuation"] = dict(a1_row.get("continuation") or {},
                                               entries=[e for e in _entries(a1_row) if e["bin"][0] != 0 and int(cv.fine_codes([e["bin"]])[0]) in support_codes])
                census_support = support_codes | ({int(cv.POP0_CELL)} if built["c0"] else set())
                fractions = cv.census_fractions_from_counts(census_out["cell_counts"], census_support, "plain")
            else:
                built = assemble_fv_row(a1_row, _combine_fv(validate_outs[0], i), M_fv, tau)
                support_codes = set(built["support_values"])
                new_row.pop("c0", None)
                new_row["continuation"] = dict(a1_row.get("continuation") or {},
                                               entries=[e for e in _entries(a1_row) if int(cv.fine_codes([e["bin"]])[0]) in support_codes])
                new_row["fv_label"] = "asymptotic, not certified"
                fractions = cv.census_fractions_from_counts(census_out["cell_counts"], support_codes, "fv")
            floor = cv.census_floor(fractions)
            nonempty = bool(_entries(new_row)) or (route == "plain" and new_row.get("c0"))
            passed = base_ok and floor["passed"] and nonempty
            new_row["status"] = "estimated" if passed else "not_estimable"
            if not passed:
                new_row["reason"] = ("A1 base screen failed" if not base_ok else
                                     "A4 availability floor failed" if not floor["passed"] else "empty validated support")
            # Blind: only fractions and flags, never raw endpoint counts. The
            # per-cell results are large, so they go to a sidecar (see details),
            # not into the family that every rerun job loads.
            new_row["a4"] = {"route": route, "base_screens_ok": base_ok, "a1_screens": a1_row.get("screens"),
                             "census": {k: fractions[k] for k in ("fraction_among_living_endpoints",
                                                                  "fraction_among_low_population_living_endpoints")},
                             "floor": {k: floor[k] for k in ("passed", "assessed", "living_ok", "low_assessed", "low_ok",
                                                             "living_fraction", "low_fraction")},
                             "validated_support_size": len(support_codes), "tau": tau, "collapse": collapse}
            key = row_key(a1_row)
            details.append({"row": key, "setting": setting_name, "route": route, "status": new_row["status"],
                            "floor": floor, "collapse": collapse, "cell_tests": built["cells"]})
            if setting_name == "primary":
                if key in primary:
                    raise ValueError("duplicate primary row")
                primary[key] = new_row
                rates[key] = rr
            else:
                sensitivity.setdefault(key, {})[setting_name] = new_row
    statuses = []
    for key, row in primary.items():
        row["primary_status"], row["primary_reason"] = row["status"], row.get("reason")
        selected = row["rule_id"] in SENSITIVITY_RULES and rates[key] in SENSITIVITY_RR
        passed, contrasts = True, []
        if selected:
            others = sensitivity.get(key, {})
            passed = set(others) == {"double_population", "double_length"}
            for name in sorted(others):
                other = others[name]
                check = numerical_contrast(row, other)
                check.update(setting=name, other_status=other["status"],
                             passed=bool(check["passed"] and other["status"] == "estimated"))
                passed &= check["passed"]
                contrasts.append(check)
            statuses.append(bool(passed))
        row["sensitivity"] = {"selected": selected, "passed": bool(passed) if selected else None, "contrasts": contrasts}
        if selected and not passed:
            row["status"] = "not_estimable"
            row["reason"] = "declared sensitivity subset failed or is incomplete"
    return primary, ("passed" if statuses and all(statuses) else "incomplete_or_failed"), details


def _index_phase(stage_root, phase):
    """Index a phase's stage outputs by A1 job id, reading each file once."""
    outputs = Path(stage_root) / phase / "outputs"
    index = {}
    if not outputs.exists():
        return index
    for path in outputs.glob("*.json"):
        doc = read(path)
        result = doc.get("result", doc)
        jid = result.get("a1_job_id")
        if jid is not None:
            index.setdefault(jid, []).append(result)
    return index


# ---------------------------------------------------------------------------
# Publication
# ---------------------------------------------------------------------------

def registered_publish_guard(plan):
    """A registered publish needs the registered flag and a registration pin,
    and rejects any settings override, so a smoke plan cannot publish
    registered."""
    if not plan.get("registered") or not plan.get("registration"):
        raise RuntimeError("registered publish requires a registered plan and a registration pin")
    if plan.get("settings_override") or any(j["config"].get("settings_override") for j in plan.get("jobs", [])):
        raise RuntimeError("registered publish rejects a settings override")


def publish(plan, run_root, source_root, calibration, target, *, registered=True):
    """Assemble and write the A4 family, with a sealed compatibility receipt."""
    from .production_tables import write_tables, ProductionTables
    from .study import table_design
    # Registration intent is checked first, before touching any source file, so
    # a smoke plan can never be published registered.
    from .instrument import declaration
    instrument = declaration(plan.get("instrument"))
    if instrument.a10:
        from .tables_a10 import verify_estimation_source
        verify_estimation_source(source_root, plan["calibration_path"], registered=registered)
    if registered:
        registered_publish_guard(plan)
        from .artifacts import verify_registration
        verify_registration(plan["registration"], **({"instrument": instrument} if instrument.a10 else {}))
    source_root, run_root = Path(source_root), Path(run_root)
    expected_a1 = A1_FILE_SHA256 if registered and not instrument.a10 else plan["source_file_sha256"]
    if file_hash(source_root / "v3_rerun_tables_A1.json") != expected_a1:
        raise ValueError("A1 publication changed")
    a1_manifest = unseal(read(source_root / "tables_A1_manifest.json"))
    if digest(a1_manifest) != plan["source_manifest_sha256"]:
        raise ValueError("A1 manifest changed")
    accepted = {code_identity()}
    if instrument.a10:
        from .compatibility_a10 import accepted_identities
        accepted = accepted_identities()
    if plan["code_hash"] not in accepted:
        raise ValueError("A4 producer source changed since prepare")
    if _recompute_plan_hash(plan) != plan["plan_hash"]:
        raise ValueError("plan hash does not match its job list, overrides and registration")
    from .calibration import validate_calibration
    validate_calibration(calibration, registered=registered, **({"instrument": instrument} if instrument.a10 else {}))
    source_code = plan["source_code_hash"]
    counts = counts_from_job_outputs(source_root, source_code)
    if (counts["M"], counts["M_FV"]) != (plan["M"], plan["M_FV"]):
        raise ValueError("M or M_FV differs from the pinned plan")
    # Calibrations are keyed by content hash, not by path string.
    calibrations = {calibration["sha256"]: calibration}

    # Verify every stage output through the runner's durable completion record
    # (which binds the whole job, so config, settings and seed) plus the A4
    # identity fields.
    stage_hashes, stream_seeds = _verify_stage_outputs(plan, run_root)

    rows, sensitivity_status, details = assemble_family(source_root, source_code, run_root, plan["M"], plan["M_FV"], calibrations)
    manifest = {"tag": "v3_tables", "calibration_hash": calibration["sha256"], "design": dict(table_design(), amendment=AMENDMENT),
                "validated_continuation": {"amendment": AMENDMENT, "M": plan["M"], "M_FV": plan["M_FV"],
                                           "plan_hash": plan["plan_hash"], "stream_tags": plan["stream_tags"],
                                           "source_family": {"file_sha256": plan["source_file_sha256"], "code_hash": source_code}},
                "required_row_keys": sorted(rows), "complete_family": True,
                "sensitivity_status": sensitivity_status,
                "source_family": {"file_sha256": plan["source_file_sha256"], "code_hash": source_code}}
    candidate = scoped(run_root) / "candidate_unpublished_tables.json"
    if instrument.a10:
        source_payload = unseal(read(source_root / "v3_rerun_tables_A1.json"))
        manifest["a10"] = source_payload["manifest"]["a10"]
    document = write_tables(candidate, list(rows.values()), manifest, fixture=not registered)
    # Per-cell results (primary and sensitivity) live in a sidecar, not the
    # family; the receipt binds the sidecar by hash.
    sidecar_doc = seal({"schema": "v3-A4-cell-results-1", "amendment": AMENDMENT, "plan_hash": plan["plan_hash"],
                        "table_seal_sha256": document["sha256"], "rows": details})
    atomic_json(candidate.with_suffix(".cell_results.json"), sidecar_doc)
    receipt = {"schema": "v3-A4-receipt-1", "amendment": AMENDMENT, "table_seal_sha256": document["sha256"],
               "table_file_sha256": file_hash(candidate), "producer_code_hash": document["payload"]["code_hash"],
               "source_family": {"file_sha256": plan["source_file_sha256"], "code_hash": source_code},
               "calibration_sha256": calibration["sha256"], "M": plan["M"], "M_FV": plan["M_FV"],
               "plan_hash": plan["plan_hash"], "stream_tags": plan["stream_tags"], "stage_output_sha256": stage_hashes,
               "stream_seeds": stream_seeds, "cell_results_sha256": file_hash(candidate.with_suffix(".cell_results.json"))}
    atomic_json(candidate.with_suffix(".compatibility.json"), seal(receipt))
    if registered:
        ProductionTables(candidate, calibration_hash=calibration["sha256"], registered=True)
    target_path = scoped(target) if str(Path(target).resolve()).startswith(str(ROOT)) else SIMULATION / target
    # Frozen-target check: refuse to overwrite existing published bytes.
    if target_path.exists() and read(target_path) != document:
        raise RuntimeError("A4 table target is frozen; publish a new path")
    atomic_json(Path(str(target_path)).with_suffix(".compatibility.json"), seal(receipt))
    atomic_json(Path(str(target_path)).with_suffix(".cell_results.json"), sidecar_doc)
    atomic_json(target_path, document)
    return {"rows": len(rows), "M": plan["M"], "M_FV": plan["M_FV"], "sensitivity_status": sensitivity_status,
            "not_estimable": sum(r["status"] != "estimated" for r in rows.values()), "detail_rows": len(details)}


def _recompute_plan_hash(plan):
    """Recompute plan_hash from the plan's own fields and job list, matching
    prepare, so a tampered hash is caught."""
    skeleton = [({k: v for k, v in j["config"].items() if k not in ("plan_hash", "phase")}, j["config"]["phase"])
                for j in plan["jobs"]]
    return digest({**{k: plan.get(k) for k in ("schema", "source_file_sha256", "source_manifest_sha256",
                                              "source_code_hash", "M", "M_FV", "code_hash", "settings_override")},
                   "registration": plan.get("registration"), "job_skeleton": skeleton})


def _verify_stage_outputs(plan, run_root):
    """Verify every stage output through the runner's durable completion record
    (which binds the whole job: config, settings and seed) plus the A4 identity
    fields. Refuse any mismatch. Returns the output hashes and the stream seeds."""
    from .production_runner import completed
    run_root = Path(run_root)
    code = code_identity()
    if plan.get("instrument", {}).get("mapping") == "A10":
        from .compatibility_a10 import accepted_identities
        if plan["code_hash"] not in accepted_identities():
            raise ValueError("A10 validation stage producer is not accepted")
        code = plan["code_hash"]
    hashes, stream_seeds = {}, {}
    for job in plan["jobs"]:
        phase_root = run_root / job["config"]["phase"]
        output = completed(phase_root, job, code)  # validates record, output hash, and job identity
        if output is None:
            raise ValueError("missing or unverified stage output: %s" % job["id"])
        result, c = output["result"], job["config"]
        if (result.get("a1_job_id") != c["a1_job"]["id"] or int(result.get("stream_seed", -1)) != int(c["seed"])
                or result.get("plan_hash") != plan["plan_hash"] or result.get("code_hash") != code):
            raise ValueError("stage output identity mismatch: %s" % job["id"])
        hashes[job["id"]] = file_hash(phase_root / "outputs" / (job["id"] + ".json"))
        stream_seeds[job["id"]] = int(c["seed"])
    return hashes, stream_seeds


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def report(family_path, output_path):
    """Write A4's Reporting paragraph from the per-cell sidecar (bound by hash in
    the compatibility receipt), covering primary and sensitivity rows: per-tier
    counts and visit shares, plain cells failing the safeguard, every violation,
    each row's floor result, and FV collapse effects. No survival, extinction or
    fire rate."""
    family_path = Path(family_path)
    receipt = unseal(read(family_path.with_suffix(".compatibility.json")))
    sidecar_path = family_path.with_suffix(".cell_results.json")
    if file_hash(sidecar_path) != receipt["cell_results_sha256"]:
        raise ValueError("cell-results sidecar hash does not match the receipt")
    details = unseal(read(sidecar_path))["rows"]
    plain = {"certified": 0, "unresolved": 0, "violation": 0, "cells": 0,
             "visits": 0.0, "certified_visits": 0.0, "safeguard_failures": 0}
    fv = {"passed": 0, "unresolved": 0, "violation": 0, "cells": 0, "visits": 0.0, "passed_visits": 0.0}
    violations, safeguard_failures, floor_results, collapses = [], [], [], []
    rows_seen = {"primary": 0, "double_population": 0, "double_length": 0}
    for entry in details:
        route = entry["route"]
        rows_seen[entry.get("setting", "primary")] = rows_seen.get(entry.get("setting", "primary"), 0) + 1
        ctx = {"row": entry["row"], "setting": entry.get("setting")}
        for cell in entry.get("cell_tests", []):
            visits = cell.get("visits", 0.0) or 0.0
            if route == "plain":
                plain["cells"] += 1
                plain["visits"] += visits
                status = cell.get("eb")
                plain[status] = plain.get(status, 0) + 1
                if status == "certified":
                    plain["certified_visits"] += visits
                    if not cell.get("visit_weighted_ok"):
                        plain["safeguard_failures"] += 1
                        safeguard_failures.append({**ctx, "cell": cell["cell"]})
                if status == "violation":
                    violations.append({**ctx, "tier": "plain", "cell": cell["cell"]})
            else:
                fv["cells"] += 1
                fv["visits"] += visits
                status = cell.get("status")
                fv[status] = fv.get(status, 0) + 1
                if status == "passed":
                    fv["passed_visits"] += visits
                if status == "violation":
                    violations.append({**ctx, "tier": "fv", "cell": cell["cell"]})
        floor_results.append({**ctx, "status": entry["status"], "floor": entry.get("floor")})
        if entry.get("collapse"):
            collapses.append({**ctx, "collapse": entry["collapse"]})
    plain["certified_visit_share"] = plain["certified_visits"] / plain["visits"] if plain["visits"] else None
    fv["passed_visit_share"] = fv["passed_visits"] / fv["visits"] if fv["visits"] else None
    result = {"schema": "v3-A4-report-1", "amendment": AMENDMENT, "rows_covered": rows_seen,
              "plain_tier": plain, "fv_tier": fv, "fv_label": "asymptotic, not certified",
              "safeguard_failures": safeguard_failures, "violations": violations,
              "floor_results": floor_results, "fv_collapses": collapses,
              "note": "continuation validation only; no survival, extinction or fire rate"}
    atomic_json(scoped(output_path) if str(Path(output_path).resolve()).startswith(str(ROOT)) else SIMULATION / output_path, result)
    return {"rows_covered": rows_seen, "plain_cells": plain["cells"], "fv_cells": fv["cells"],
            "violations": len(violations), "safeguard_failures": len(safeguard_failures), "collapses": len(collapses)}


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("source_root"); p.add_argument("calibration_path"); p.add_argument("output")
    p.add_argument("--pin"); p.add_argument("--wall-hours", type=int, default=48); p.add_argument("--a3-probe-root")
    p = sub.add_parser("counts"); p.add_argument("source_root")
    p = sub.add_parser("publish")
    p.add_argument("plan"); p.add_argument("run_root"); p.add_argument("source_root")
    p.add_argument("calibration"); p.add_argument("target")
    p = sub.add_parser("report"); p.add_argument("family"); p.add_argument("output")
    args = parser.parse_args()
    if args.command == "report":
        print(report(args.family, args.output)); return
    if args.command == "prepare":
        plan = prepare(args.source_root, args.calibration_path, read(args.pin) if args.pin else None,
                       args.wall_hours, args.a3_probe_root)
        out = args.output if str(Path(args.output).resolve()).startswith(str(ROOT)) else SIMULATION / args.output
        atomic_json(out, seal(plan))
        print({"phases": plan["phases"], "jobs": len(plan["jobs"]), "M": plan["M"], "M_FV": plan["M_FV"], "launched": False})
    elif args.command == "counts":
        print(counts_from_job_outputs(args.source_root))
    else:
        print(publish(unseal(read(args.plan)), args.run_root, args.source_root, read(args.calibration), args.target))


if __name__ == "__main__":
    main()
