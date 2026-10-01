"""A5 plain-law certification labels for FV-route tables.

D31, 2026-09-29. A5 is label-only: it never changes a published support, value
or row status, so the reruns behave identically whether or not A5 has run. It
tests every cell in the validated support of every primary FV row with status
``estimated`` in the sealed A4 publication, on independent PLAIN trajectories,
with A4's certified plain-tier test. A certified cell is labelled "certified
under the plain law"; every other tested cell keeps "asymptotic, not certified".

A5 reads the A4 family, its receipt and its cell-results sidecar directly, never
through ``ProductionTables``, because A5's code identity differs from the family's
by design. It verifies their bytes against a committed identity record, and it
verifies the A4 census stage outputs against the receipt. The one stage kind,
``a5_fvplain``, runs through the production runner. The numerics are reused
unchanged from ``continuation_validation``; anything new lives here. It computes
no survival, extinction or fire rate, and none leaves any output, log or report.
"""
import dataclasses
from pathlib import Path

import numpy as np

from .artifacts import (ROOT, SIMULATION, atomic_json, read, seal, unseal, digest, file_hash,
                        code_identity, scoped, stable_job, verify_registration)
from . import continuation_validation as cv
from .table_validation_a4 import (a1_published_fv, estimate_memory_gb, load_probe_seeds, _load_a1,
                                   _source_code_hash)

SCHEMA = "v3-A5-labels-1"
AMENDMENT = "A5 adopted by D31, 2026-09-29; committed pin required"
A5_TAG = "v3_R_fvplain"
A5_REPLICATES = (1, 2, 3)
PHASE = "a5_fvplain"
CERTIFIED_LABEL = "certified under the plain law"
ASYMPTOTIC_LABEL = "asymptotic, not certified"

# The committed A4-family identity record a registered run must bind to, relative
# to the repository root, and the fixed 24-hour ceiling.
REGISTERED_IDENTITY_PATH = "simulation/v3/runs/registered/A4_family_identity.json"
REGISTERED_WALL_HOURS = 24
# P4 measured about 1.9 GB peak RSS for full-size plain tasks on FV kernels; A4's
# 20% margin gives the anchor. Scaling A4's FV anchor down to the plain population
# alone is not conservative, because the fixed overhead does not shrink, so the
# estimate is the larger of this anchor and the arithmetic scaling.
P4_PLAIN_ANCHOR_GB = 1.9 * 1.2


# ---------------------------------------------------------------------------
# Seeds
# ---------------------------------------------------------------------------

def fvplain_seed(a1_job_seed, replicate):
    """A5's plain-trajectory stream seed, by A4's ``stream_seed``."""
    return cv.stream_seed(A5_TAG, a1_job_seed, replicate)


def _planning_p4_seed(a1_job_seed, replicate):
    """The P4 planning seed, derived exactly as ``planning_study/run_p4.py``:
    SHA-256 of the tag, the A1 job seed and the replicate, truncated to 60 bits."""
    return cv._truncated_sha("planning_P4", a1_job_seed, replicate)


def forbidden_seeds(a1_job_seeds, a4_stream_seeds, probe_seeds):
    """The full global forbidden set A5 halts on, as the amendment lists it:
    every A1 job seed; every seed in the A4 plan; the D26 probe seeds; and the
    planning seeds P1, P1-census, P3 (0-3) and P4 (0-3) for every A1 job."""
    forbidden = set(int(s) for s in a1_job_seeds)
    forbidden |= set(int(s) for s in a4_stream_seeds)
    forbidden |= set(int(s) for s in probe_seeds)
    for s in a1_job_seeds:
        forbidden.add(cv._planning_p1_seed(s))
        forbidden.add(cv._planning_p1_census_seed(s))
        for r in range(4):
            forbidden.add(cv._planning_p3_seed(s, r))
            forbidden.add(_planning_p4_seed(s, r))
    return forbidden


def assert_a5_seeds(fv_job_seeds, forbidden):
    """Build A5's own seeds, halt on any collision with the forbidden set, and
    assert the 3 x |fv jobs| A5 seeds are pairwise distinct. Returns the map."""
    a5 = {}
    for seed in fv_job_seeds:
        for r in A5_REPLICATES:
            value = fvplain_seed(seed, r)
            if value in forbidden:
                raise cv.SeedCollision("A5 seed collides with a forbidden seed: %r" % ((seed, r), ))
            a5[(int(seed), r)] = value
    values = list(a5.values())
    if len(set(values)) != len(values):
        raise cv.SeedCollision("A5 seeds are not pairwise distinct")
    return a5


# ---------------------------------------------------------------------------
# The A4 publication: read and verify, never through ProductionTables
# ---------------------------------------------------------------------------

def _require(condition, message):
    if not condition:
        raise ValueError(message)


def require_committed_identity(path):
    """A registered run's identity record is the committed one at the fixed
    repository path, tracked, with bytes equal to ``git show HEAD:<path>``."""
    import subprocess
    repo = SIMULATION.parent
    resolved = Path(path).resolve()
    expected = (repo / REGISTERED_IDENTITY_PATH).resolve()
    _require(resolved == expected, "registered A5 requires the committed identity record at %s" % REGISTERED_IDENTITY_PATH)

    def git(*args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout
    try:
        git("ls-files", "--error-unmatch", REGISTERED_IDENTITY_PATH)
        committed = git("show", "HEAD:" + REGISTERED_IDENTITY_PATH)
    except subprocess.CalledProcessError as exc:
        raise ValueError("A4 family identity record is not tracked or committed at HEAD") from exc
    if committed != resolved.read_bytes():
        raise ValueError("A4 family identity record differs from HEAD")


def verify_a4_plan(a4_plan, receipt, a1_manifest):
    """The A4 plan supplies the 252 jobs, the forbidden A1 and A4 seeds and the
    census map, so it is cross-checked against the receipt and the A1 manifest."""
    from .table_validation_a4 import _recompute_plan_hash as a4_recompute
    _require(a4_plan.get("plan_hash") == receipt.get("plan_hash"), "A4 plan hash differs from the receipt")
    _require(a4_recompute(a4_plan) == a4_plan["plan_hash"], "A4 plan hash does not match its own job list")
    _require(digest(a1_manifest) == a4_plan.get("source_manifest_sha256"),
             "A4 plan source manifest hash differs from the A1 manifest")
    stream_seeds = receipt.get("stream_seeds") or {}
    for job in a4_plan["jobs"]:
        _require(int(job["config"]["seed"]) == int(stream_seeds.get(job["id"], -2)),
                 "A4 plan job seed differs from the receipt: %s" % job["id"])
    plan_a1_seeds = {int(j["config"]["a1_job"]["seed"]) for j in a4_plan["jobs"]}
    manifest_seeds = {int(j["seed"]) for j in a1_manifest["jobs"]}
    _require(len(manifest_seeds) == len(a1_manifest["jobs"]), "duplicate A1 job seeds in the manifest")
    _require(bool(manifest_seeds) and plan_a1_seeds == manifest_seeds,
             "A4 plan A1 job seeds differ from the A1 manifest seeds")
    return manifest_seeds


def load_a4_publication(family_path, identity_record):
    """Read and verify the A4 family, its receipt and its cell-results sidecar
    against the committed identity record. Halt on any mismatch. Returns
    ``(payload, receipt, sidecar, hashes)`` where ``hashes`` pins the three files.

    ``identity_record`` holds ``family_file_sha256``, ``table_seal_sha256``,
    ``receipt_file_sha256``, ``sidecar_file_sha256``, ``producing_commit`` and
    ``code_hash``.
    """
    family_path = Path(family_path)
    receipt_path = family_path.with_suffix(".compatibility.json")
    sidecar_path = family_path.with_suffix(".cell_results.json")
    for key in ("family_file_sha256", "table_seal_sha256", "receipt_file_sha256",
                "sidecar_file_sha256", "producing_commit", "code_hash"):
        _require(key in identity_record, "identity record missing %r" % key)

    family_file_sha256 = file_hash(family_path)
    _require(family_file_sha256 == identity_record["family_file_sha256"], "A4 family file hash mismatch")
    family_doc = read(family_path)
    payload = unseal(family_doc)  # verifies the internal seal
    _require(family_doc["sha256"] == identity_record["table_seal_sha256"], "A4 family seal mismatch")
    _require(payload.get("code_hash") == identity_record["code_hash"], "A4 family producer code hash mismatch")

    receipt_file_sha256 = file_hash(receipt_path)
    _require(receipt_file_sha256 == identity_record["receipt_file_sha256"], "A4 receipt file hash mismatch")
    receipt = unseal(read(receipt_path))
    _require(receipt.get("table_seal_sha256") == identity_record["table_seal_sha256"], "receipt table seal mismatch")
    _require(receipt.get("table_file_sha256") == identity_record["family_file_sha256"], "receipt table file mismatch")
    _require(receipt.get("cell_results_sha256") == identity_record["sidecar_file_sha256"], "receipt sidecar mismatch")
    _require(receipt.get("producer_code_hash") == identity_record["code_hash"], "receipt producer code mismatch")

    sidecar_file_sha256 = file_hash(sidecar_path)
    _require(sidecar_file_sha256 == identity_record["sidecar_file_sha256"], "A4 sidecar file hash mismatch")
    sidecar = unseal(read(sidecar_path))

    hashes = {"family_file_sha256": family_file_sha256, "table_seal_sha256": family_doc["sha256"],
              "receipt_file_sha256": receipt_file_sha256, "sidecar_file_sha256": sidecar_file_sha256,
              "producing_commit": identity_record["producing_commit"], "code_hash": identity_record["code_hash"]}
    return payload, receipt, sidecar, hashes


def family_rows(payload):
    """Every primary row of the A4 family, keyed by row key (unsealed)."""
    return {key: unseal(sealed) for key, sealed in payload["rows"].items()}


def tested_fv_rows(payload):
    """Every primary FV row with status ``estimated``, keyed by row key. The A4
    family published to the reruns holds primary rows only, so this is exactly
    the FV set the reruns can look up. Sensitivity rows are not published, so
    they are not tested."""
    return {key: row for key, row in family_rows(payload).items()
            if row.get("route") == "fv" and row.get("status") == "estimated"}


# ---------------------------------------------------------------------------
# The census stage outputs: read from the A4 run root, verify against the receipt
# ---------------------------------------------------------------------------

def census_jobs(a4_plan):
    return [j for j in a4_plan["jobs"] if j["config"].get("phase") == "census"]


def census_job_map(a4_plan, receipt):
    """Map each A4 census stage job id to its A1 job id and pinned output hash,
    from the A4 plan and the receipt. The map is stored in the A5 plan so publish
    never needs the A4 plan file."""
    stage_hashes = receipt.get("stage_output_sha256") or {}
    job_map, pinned = {}, {}
    for job in census_jobs(a4_plan):
        job_id = job["id"]
        _require(job_id in stage_hashes, "census job %s absent from the receipt" % job_id)
        job_map[job_id] = job["config"]["a1_job"]["id"]
        pinned[job_id] = stage_hashes[job_id]
    return job_map, pinned


def read_census(a4_run_root, job_map, expected_hashes):
    """Read every A4 census stage output from the A4 run root and verify each
    against the pinned hash. Halt on any mismatch. Returns a map from A1 job id
    to living-endpoint counts."""
    a4_run_root = Path(a4_run_root)
    census = {}
    for job_id, a1_job_id in job_map.items():
        path = a4_run_root / "census" / "outputs" / (job_id + ".json")
        actual = file_hash(path)
        _require(actual == expected_hashes.get(job_id), "A4 census stage output hash mismatch: %s" % job_id)
        result = read(path).get("result", read(path))
        _require(result["a1_job_id"] == a1_job_id, "census output A1 job id mismatch: %s" % job_id)
        census[a1_job_id] = {"cell_counts": {int(c): int(n) for c, n in result["cell_counts"].items()},
                             "total_living": int(result["total_living"])}
    return census


# ---------------------------------------------------------------------------
# The tested set, widths and M, from the A4 publication (before any A5 data)
# ---------------------------------------------------------------------------

def _context_bounds(a1_output, cal_cache):
    from .context import Context
    config = a1_output["job"]["config"]
    path = config.get("calibration_path")
    calibration = None
    if path:
        if path not in cal_cache:
            cal_cache[path] = read(SIMULATION / Path(path))
        calibration = cal_cache[path]
    params = Context.build(a1_output["result"]["kernel"], calibration).parameters
    return params.extinction_flow, params.upper_bound


def fv_primary_jobs(a4_plan):
    """The A4 plan's primary FV validate jobs, one per primary FV A1 job."""
    return [j for j in a4_plan["jobs"] if j["config"].get("phase") == "validate_fv_primary"]


def build_tested_set(payload, a4_plan, a1_source_root, source_code, cal_cache):
    """Bind every tested row-cell to its A1 job, computing per-row widths and
    tau from the A4 values before any A5 data exist. Range checks halt.

    Returns ``(per_job, M)`` where ``per_job`` maps an A1 job id to a dict with
    the A1 job, its flow bounds, and the tested rows (each carrying its scoring,
    its support ``[[code, value], ...]``, vmax, width, tau and flow_range)."""
    from .production_tables import row_key
    tested = tested_fv_rows(payload)
    # Map each family FV row key to its A1 job and flow bounds, via the plan's
    # primary FV validate jobs.
    index = {}
    for job in fv_primary_jobs(a4_plan):
        a1_job = job["config"]["a1_job"]
        a1 = _load_a1(a1_source_root, a1_job, source_code)
        _require(a1["result"]["route"] == "fv", "primary FV job is not FV route: %s" % a1_job["id"])
        lower, upper = _context_bounds(a1, cal_cache)
        for a1_row in a1["result"]["rows"]:
            index[row_key(a1_row)] = (a1_job, lower, upper)

    per_job, M = {}, 0
    for key, row in sorted(tested.items()):
        _require(key in index, "tested FV row not found among the A4 plan's primary FV jobs: %s" % key)
        a1_job, lower, upper = index[key]
        entries = (row.get("continuation") or {}).get("entries") or []
        _require(bool(entries), "estimated FV row has empty support: %s" % key)
        support = [[int(cv.fine_codes([e["bin"]])[0]), float(e["value"])] for e in entries]
        values = [v for _, v in support]
        cv.check_in_range(values, lower, upper, "A4 published value")
        vmax = max(values)
        width = cv.row_width(row["flow_range"], vmax, lower, upper)
        tau = 0.05 * row["flow_range"]
        entry = per_job.setdefault(a1_job["id"], {"a1_job": a1_job, "lower": lower, "upper": upper, "rows": []})
        entry["rows"].append({"row_key": key, "scoring": row["scoring"], "support": support,
                              "vmax": vmax, "width": width, "tau": tau, "flow_range": row["flow_range"]})
        M += len(support)
    return per_job, M


# ---------------------------------------------------------------------------
# The stage: plain trajectories on FV jobs
# ---------------------------------------------------------------------------

def fvplain_stage(a1_output, tested_rows, lower, upper, seed, override=None):
    """Sufficient statistics per tested cell for one FV A1 job and replicate,
    on the PLAIN route with the job's own A1 settings and 32 groups.

    Living-source residuals on fine cells against the A4 published values, with
    ``V(next)`` the published value or ``lower`` at extinction, covered only when
    the source is alive and both the source cell and the (non-extinct) next cell
    are in the row's A4 support. Emits trajectory-level sums and per-cell visit
    counts. No survival, extinction or fire quantity."""
    from .context import Context
    from .offline_estimator import simulate, _rule, score_features
    result = a1_output["result"]
    _require(result["route"] == "fv", "A5 covers FV-route A1 jobs only")
    config = a1_output["job"]["config"]
    calibration = read(SIMULATION / Path(config["calibration_path"])) if config.get("calibration_path") else None
    context = Context.build(result["kernel"], calibration)
    if abs(context.parameters.extinction_flow - lower) > 1e-9 or abs(context.parameters.upper_bound - upper) > 1e-9:
        raise cv.OutOfRange("job flow bounds differ from the pinned plan bounds")
    settings = {**result["settings"], "groups": cv.GROUPS}
    if override:
        settings.update({k: v for k, v in override.items() if k in ("burn", "measure", "runs_per_group", "groups")})
    trace = simulate(context, _rule(result["rows"][0]["rule_id"]), settings, seed, "plain")
    length, count = trace["before"].shape[:2]
    traj = np.broadcast_to(np.arange(count)[None, :], (length, count)).ravel()
    before6 = trace["before"].reshape(-1, 6)
    after6 = trace["after"].reshape(-1, 6)
    if before6.min() < 0 or before6.max() > 7 or after6.min() < 0 or after6.max() > 7:
        raise cv.OutOfRange("bin coordinates out of range")
    src_fine = cv.fine_codes(before6)
    nxt_fine = cv.fine_codes(after6)
    # features are post-advance; alive marks the next state, and a plain trace
    # keeps recording after extinction, so the living-source mask is required.
    alive = trace["features"][..., 0] > 0
    dead = (~alive).ravel()
    source_alive = np.concatenate((np.ones((1, count), dtype=bool), alive[:-1])).ravel()

    rows_out = []
    for tested in tested_rows:
        scoring = tested["scoring"]
        value_by_code = {int(c): float(v) for c, v in tested["support"]}
        ctx = dataclasses.replace(context, parameters=dataclasses.replace(context.parameters, kappa=scoring.get("kappa", 8.0)))
        flows = score_features(trace["features"], ctx, scoring["alpha"], scoring["capability"]).ravel()
        cv.check_in_range(flows, lower, upper, "flow")
        residual, covered, srcidx, codes = cv.living_source_residuals(
            src_fine, nxt_fine, source_alive, dead, flows, value_by_code, lower)
        sums = cv.trajectory_sums(srcidx[covered], traj[covered], residual[covered], len(codes), count)
        cells = [{"cell": int(c), **{k: (int(v[j]) if k == "n_traj" else float(v[j])) for k, v in sums.items()}}
                 for j, c in enumerate(codes.tolist()) if sums["n_traj"][j] > 0]
        rows_out.append({"row_key": tested["row_key"], "scoring": scoring, "cells": cells})
    return {"stage": PHASE, "a1_job_id": a1_output["job"]["id"], "seed": int(seed), "route": "plain",
            "settings": settings, "count": count, "rows": rows_out}


def run_stage_job(job, root=None):
    """Execute one A5 stage job. ``production_runner.execute`` dispatches here.
    The A5 stream seed travels in ``job['config']['seed']``; the runner's own job
    seed is unused. A5 needs no sibling phase."""
    c = job["config"]
    a1 = _load_a1(c["a1_source_root"], c["a1_job"], c["a1_source_code_hash"])
    result = fvplain_stage(a1, c["tested_rows"], c["lower"], c["upper"], c["seed"], c.get("settings_override"))
    result.update(a1_job_id=c["a1_job"]["id"], stream_seed=int(c["seed"]), plan_hash=c["plan_hash"],
                  code_hash=code_identity())
    return result


# ---------------------------------------------------------------------------
# The sealed plan (prepare)
# ---------------------------------------------------------------------------

def _a5_job(config):
    return stable_job(PHASE, {**config, "phase": PHASE}, "v3_tables", 0)


def prepare(a4_family_path, a4_run_root, a4_plan_path, a1_source_root, calibration_path,
            identity_record_path, registration=None, wall_hours=24, a3_probe_root=None,
            settings_override=None):
    """A sealed A5 plan: the 252 x 3 plain-trajectory jobs, the pinned tested set
    with per-row widths, M, every input hash and the registration pin.

    Pure: launches nothing and reads no rerun output. Verifies the A4 family,
    receipt and sidecar against the identity record, verifies the A4 census stage
    outputs against the receipt, checks the A1 source, and asserts the global
    seed guard."""
    a1_source_root = Path(a1_source_root)
    if registration is not None:
        _require(wall_hours == REGISTERED_WALL_HOURS, "registered A5 uses the 24-hour ceiling")
        require_committed_identity(identity_record_path)
    identity_record = read(identity_record_path)
    payload, receipt, sidecar, a4_hashes = load_a4_publication(a4_family_path, identity_record)
    a4_plan = unseal(read(a4_plan_path))
    a4_plan_file_sha256 = file_hash(a4_plan_path)
    a1_manifest = unseal(read(a1_source_root / "tables_A1_manifest.json"))

    # Cross-check the A4 plan against the receipt and the A1 manifest.
    manifest_seeds = verify_a4_plan(a4_plan, receipt, a1_manifest)

    # The calibration is the one the A4 receipt binds.
    calibration = read(SIMULATION / Path(calibration_path))
    _require(calibration.get("sha256") == receipt.get("calibration_sha256"),
             "calibration hash differs from the A4 receipt")

    # The A1 source the A4 family was built from.
    source_code = _source_code_hash(a1_source_root)
    actual_a1 = file_hash(a1_source_root / "v3_rerun_tables_A1.json")
    expected_a1 = receipt.get("source_family", {}).get("file_sha256")
    if registration is not None:
        from .table_validation_a4 import A1_FILE_SHA256
        _require(payload.get("fixture") is False, "registered A5 rejects a fixture A4 family")
        _require(actual_a1 == A1_FILE_SHA256, "A1 source is not the canonical A1 publication")
        _require(actual_a1 == expected_a1, "A1 source publication differs from the A4 receipt")

    census_map, census_hashes = census_job_map(a4_plan, receipt)
    # Read and verify the census outputs now, as a prepare-time gate.
    read_census(a4_run_root, census_map, census_hashes)

    cal_cache = {}
    per_job, M = build_tested_set(payload, a4_plan, a1_source_root, source_code, cal_cache)

    # Seeds. The A1 job seeds are taken from the A1 manifest; the A4 plan stream
    # seeds from the plan; the D26 probe seeds from the a3_probe records; P1/P3/P4
    # by derivation.
    a1_job_seeds = manifest_seeds
    a4_stream_seeds = {j["config"]["seed"] for j in a4_plan["jobs"]}
    probe_seeds = load_probe_seeds(a3_probe_root) if a3_probe_root else set()
    if not probe_seeds:
        raise ValueError("A5 prepare requires a non-empty D26 probe root; none found under %r" % a3_probe_root)
    forbidden = forbidden_seeds(a1_job_seeds, a4_stream_seeds, probe_seeds)

    fv_jobs = [j["config"]["a1_job"] for j in fv_primary_jobs(a4_plan)]
    fv_job_seeds = [j["seed"] for j in fv_jobs]
    a5_seeds = assert_a5_seeds(fv_job_seeds, forbidden)
    _require(len(a5_seeds) == len(fv_jobs) * len(A5_REPLICATES),
             "expected %d A5 seeds, built %d" % (len(fv_jobs) * len(A5_REPLICATES), len(a5_seeds)))
    if registration is not None:
        _require(len(fv_jobs) == 252, "registered A5 expects 252 primary FV tables")
        _require(len(a5_seeds) == 252 * len(A5_REPLICATES), "registered A5 expects 756 A5 seeds")

    memory_estimate = 0.0
    skeletons = []
    for a1_job in fv_jobs:
        bounds = per_job.get(a1_job["id"])
        if bounds is not None:
            lower, upper, tested_rows = bounds["lower"], bounds["upper"], bounds["rows"]
        else:
            # A primary FV table with no estimated rows still runs (252 tables),
            # but has no tested cell. Its bounds come from its own A1 output.
            a1 = _load_a1(a1_source_root, a1_job, source_code)
            lower, upper, tested_rows = (*_context_bounds(a1, cal_cache), [])
        base = {"a1_source_root": str(a1_source_root.resolve()), "a1_job": a1_job,
                "a1_source_code_hash": source_code, "stage": PHASE, "route": "plain",
                "lower": lower, "upper": upper, "tested_rows": tested_rows}
        if settings_override:
            base["settings_override"] = settings_override
        settings = {**a1_job["config"]["settings"], "groups": cv.GROUPS}
        # The larger of the P4 measured anchor and the arithmetic scaling.
        memory_estimate = max(memory_estimate, estimate_memory_gb("plain", settings), P4_PLAIN_ANCHOR_GB)
        for r in A5_REPLICATES:
            skeletons.append({**base, "replicate": r, "seed": fvplain_seed(a1_job["seed"], r)})

    plan_core = {"schema": SCHEMA, "amendment": AMENDMENT, "registered": bool(registration),
                 "tag": "v3_tables", "code_hash": code_identity(),
                 "a4_family_path": str(Path(a4_family_path).resolve()), "a4_run_root": str(Path(a4_run_root).resolve()),
                 "a4_plan_path": str(Path(a4_plan_path).resolve()), "a4_plan_file_sha256": a4_plan_file_sha256,
                 "a4": a4_hashes,
                 "a4_census_output_sha256": census_hashes, "a4_census_jobs": census_map,
                 "a1_source_root": str(a1_source_root.resolve()), "a1_source_file_sha256": actual_a1,
                 "a1_source_code_hash": source_code, "calibration_path": calibration_path,
                 "wall_seconds": wall_hours * 3600, "cleanup_reserve_seconds": 1200, "configuration_seconds": 1800,
                 "phases": [PHASE], "M": M, "alpha": cv.ALPHA, "groups": cv.GROUPS, "stream_tag": A5_TAG,
                 "replicates": list(A5_REPLICATES), "memory_estimate_gb": {PHASE: memory_estimate},
                 "memory_basis": ("the larger of P4's measured plain-task peak RSS of about 1.9 GB with A4's 20 percent "
                                  "margin and the arithmetic population-times-length scaling; scaling A4's FV anchor down "
                                  "alone is not conservative because the fixed overhead does not shrink"),
                 "probe_seed_count": len(probe_seeds), "forbidden_seed_count": len(forbidden),
                 "a5_seed_count": len(a5_seeds), "fv_tables": len(fv_jobs), "settings_override": settings_override}
    plan_hash = digest({**{k: plan_core[k] for k in ("schema", "a4", "a4_plan_file_sha256", "a4_census_jobs",
                                                     "a4_census_output_sha256", "a1_source_file_sha256",
                                                     "a1_source_code_hash", "M", "code_hash", "settings_override",
                                                     "wall_seconds")},
                        "registration": registration,
                        "job_skeleton": skeletons})
    plan_core["plan_hash"] = plan_hash

    jobs = [_a5_job({**config, "plan_hash": plan_hash}) for config in skeletons]
    if len({j["id"] for j in jobs}) != len(jobs):
        raise ValueError("duplicate A5 job identifier")

    plan_core["configuration"] = {PHASE: _configuration_profile(skeletons)}
    plan_core.update(jobs=jobs, registration=registration)
    return plan_core


def _configuration_profile(skeletons):
    """One profile of A5's own kind, length-shortened so populations (and memory)
    stay representative. A5 tasks are self-contained, needing no sibling phase."""
    # The representative task is the one with the most tested row-cells, since task
    # cost grows with the number of tested rows and cells.
    def cell_count(config):
        return sum(len(row["support"]) for row in config.get("tested_rows") or [])
    representative = max(skeletons, key=cell_count) if skeletons else None
    _require(representative is not None, "A5 plan has no jobs")
    # Registered: the real population with a short length (memory-representative).
    # Smoke: keep the smoke population override too, so the test stays tiny.
    short = {**(representative.get("settings_override") or {}), "burn": 8, "measure": 24}
    cfg = {k: representative[k] for k in ("a1_source_root", "a1_job", "a1_source_code_hash", "stage", "route",
                                          "lower", "upper", "tested_rows", "seed", "plan_hash")
           if k in representative}
    cfg.update(plan_hash=representative.get("plan_hash", "configuration"), settings_override=short)
    return {"kind": PHASE, "config": cfg, "configs": [cfg], "jobs_local": 4, "jobs_x2": 32,
            "workers_local": [2, 4], "workers_x2": [8, 12, 16, 24, 32], "threads": [1], "rounds": 1,
            "jobs_per_worker": 2, "shortened_length_only": True}


# ---------------------------------------------------------------------------
# Publication: labels and report
# ---------------------------------------------------------------------------

def _recompute_plan_hash(plan):
    skeleton = [{k: v for k, v in j["config"].items() if k not in ("plan_hash", "phase")} for j in plan["jobs"]]
    return digest({**{k: plan.get(k) for k in ("schema", "a4", "a4_plan_file_sha256", "a4_census_jobs",
                                              "a4_census_output_sha256", "a1_source_file_sha256",
                                              "a1_source_code_hash", "M", "code_hash", "settings_override",
                                              "wall_seconds")},
                   "registration": plan.get("registration"), "job_skeleton": skeleton})


def _verify_stage_outputs(plan, run_root):
    """Verify every A5 stage output through the runner's durable completion record
    plus the A5 identity fields. Returns the output hashes and stream seeds."""
    from .production_runner import completed
    run_root = Path(run_root)
    code = code_identity()
    hashes, stream_seeds = {}, {}
    for job in plan["jobs"]:
        phase_root = run_root / job["config"]["phase"]
        output = completed(phase_root, job, code)
        if output is None:
            raise ValueError("missing or unverified stage output: %s" % job["id"])
        result, c = output["result"], job["config"]
        if (result.get("a1_job_id") != c["a1_job"]["id"] or int(result.get("stream_seed", -1)) != int(c["seed"])
                or result.get("plan_hash") != plan["plan_hash"] or result.get("code_hash") != code):
            raise ValueError("stage output identity mismatch: %s" % job["id"])
        hashes[job["id"]] = file_hash(phase_root / "outputs" / (job["id"] + ".json"))
        stream_seeds[job["id"]] = int(c["seed"])
    return hashes, stream_seeds


# The statistics the A5 test and safeguard need; the stage emits A4's full set.
A5_STAT_KEYS = ("n_traj", "sum_S", "sum_N", "sum_m", "sum_m2")


def _combine_row_cells(stage_results_for_job, row_key):
    """Combine the replicate cell statistics for one row by summation. Trajectory
    sets are disjoint across replicates, so the sums add."""
    combined = {}
    for result in stage_results_for_job:
        for row in result["rows"]:
            if row["row_key"] != row_key:
                continue
            for cell in row["cells"]:
                acc = combined.setdefault(cell["cell"], dict.fromkeys(A5_STAT_KEYS, 0.0))
                for k in A5_STAT_KEYS:
                    acc[k] += cell[k]
    return combined


def classify_cell(stat, width, M, tau):
    """A4's plain-tier classification, unchanged: empirical Bernstein at
    delta = alpha / M, then the visit-weighted safeguard."""
    if stat is None:
        return {"status": "unresolved", "eb": "unresolved", "visit_weighted_ok": False,
                "n_traj": 0, "visits": 0.0, "interval": None, "reason": "no visits"}
    eb = cv.empirical_bernstein(stat["sum_m"], stat["sum_m2"], stat["n_traj"], width, M, tau)
    safeguard = cv.visit_weighted_ok(stat["sum_S"], stat["sum_N"], tau)
    if eb["status"] == "certified" and safeguard:
        status = "certified"
    elif eb["status"] == "violation":
        status = "violation"
    else:
        status = "unresolved"
    return {"status": status, "eb": eb["status"], "visit_weighted_ok": bool(safeguard),
            "n_traj": int(stat["n_traj"]), "visits": float(stat["sum_N"]), "interval": eb.get("interval")}


def label_for(status):
    return CERTIFIED_LABEL if status == "certified" else ASYMPTOTIC_LABEL


def build_labels(plan, stage_results, census):
    """Combine replicates, classify every tested row-cell, and attach labels and
    exposure. Returns the per-row records and the totals."""
    # Group stage results by A1 job id.
    by_job = {}
    for result in stage_results:
        by_job.setdefault(result["a1_job_id"], []).append(result)
    # The pinned tested set, from the plan's own jobs (identical across replicates).
    tested_by_job = {}
    for job in plan["jobs"]:
        c = job["config"]
        tested_by_job.setdefault(c["a1_job"]["id"], c["tested_rows"])

    rows_out = []
    # Only cell counts and shares are sealed into the record. The visit and census
    # endpoint sums stay local, so no raw census-endpoint count (which, divided by
    # the known census size, would give a survival fraction) ever leaves here.
    totals = {"certified": 0, "unresolved": 0, "violation": 0, "cells": 0, "violations": 0}
    pooled_visits, pooled_certified_visits = 0.0, 0.0
    pooled_certified_census, pooled_living_census = 0, 0
    M = plan["M"]
    for a1_job_id, tested_rows in sorted(tested_by_job.items()):
        job_results = by_job.get(a1_job_id, [])
        job_census = census.get(a1_job_id, {"cell_counts": {}, "total_living": 0})
        total_living = job_census["total_living"]
        cell_counts = job_census["cell_counts"]
        for tested in tested_rows:
            width, tau = tested["width"], tested["tau"]
            combined = _combine_row_cells(job_results, tested["row_key"])
            support_codes = [int(code) for code, _ in tested["support"]]
            cells, certified, unresolved, violation = [], 0, 0, 0
            certified_visits, row_visits, certified_census, violations = 0.0, 0.0, 0, []
            for code in support_codes:
                stat = combined.get(code)
                result = classify_cell(stat, width, M, tau)
                census_count = int(cell_counts.get(code, 0))
                exposure = (census_count / total_living) if total_living else None
                # Blind: only shares leave the record; n_traj and visits are the
                # audit statistics the test needs, as A4's sidecar keeps.
                cell = {"cell": code, "status": result["status"], "label": label_for(result["status"]),
                        "n_traj": result["n_traj"], "visits": result["visits"], "interval": result["interval"],
                        "visit_weighted_ok": result["visit_weighted_ok"], "exposure": exposure}
                cells.append(cell)
                row_visits += result["visits"]
                totals["cells"] += 1
                pooled_visits += result["visits"]
                if result["status"] == "certified":
                    certified += 1
                    totals["certified"] += 1
                    certified_visits += result["visits"]
                    certified_census += census_count
                elif result["status"] == "violation":
                    violation += 1
                    totals["violation"] += 1
                    violations.append({"cell": code, "interval": result["interval"], "exposure": exposure})
                else:
                    unresolved += 1
                    totals["unresolved"] += 1
            pooled_certified_visits += certified_visits
            totals["violations"] += violation
            pooled_certified_census += certified_census
            pooled_living_census += total_living
            rows_out.append({
                "row_key": tested["row_key"], "a1_job_id": a1_job_id, "scoring": tested["scoring"],
                "tau": tau, "width": width, "flow_range": tested["flow_range"], "vmax": tested["vmax"],
                "cells": cells, "certified": certified, "unresolved": unresolved, "violation": violation,
                "certified_visit_share": (certified_visits / row_visits) if row_visits else None,
                "certified_census_share": (certified_census / total_living) if total_living else None,
                "violation_count": violation,
                "violation_exposure_total": sum((v["exposure"] or 0.0) for v in violations) if violations else 0.0,
                "violations": violations})
    totals["certified_visit_share"] = (pooled_certified_visits / pooled_visits) if pooled_visits else None
    # Pooled over tested rows: sum of certified-cell living census endpoints over
    # the sum of living census endpoints across all tested rows. Only the share
    # leaves; the two sums are local.
    totals["certified_census_share"] = ((pooled_certified_census / pooled_living_census)
                                        if pooled_living_census else None)
    return rows_out, totals


def publish(plan, a5_run_root, a4_run_root, a1_source_root, calibration, target, *, registered=True):
    """Assemble and write the sealed A5 label record. Refuses to overwrite a
    published record, and asserts the A4 family bytes are unchanged."""
    from .calibration import validate_calibration
    if registered:
        _require(plan.get("registered") and plan.get("registration"),
                 "registered publish requires a registered plan and a registration pin")
        _require(not plan.get("settings_override") and not any(j["config"].get("settings_override") for j in plan.get("jobs", [])),
                 "registered publish rejects a settings override")
        verify_registration(plan["registration"])
    _require(plan["code_hash"] == code_identity(), "A5 producer source changed since prepare")
    _require(_recompute_plan_hash(plan) == plan["plan_hash"], "plan hash does not match its job list")
    if registered:
        _require(plan["wall_seconds"] == REGISTERED_WALL_HOURS * 3600, "registered A5 uses the 24-hour ceiling")
        _require(plan["fv_tables"] == 252, "registered A5 expects 252 primary FV tables")
        _require(len(plan["jobs"]) == 252 * len(A5_REPLICATES), "registered A5 expects 756 stage jobs")
    validate_calibration(calibration, registered=registered)

    # Re-read and re-verify the A4 publication against the pinned identity, and
    # capture the bytes for the label-only check.
    family_path = Path(plan["a4_family_path"])
    identity = {"family_file_sha256": plan["a4"]["family_file_sha256"], "table_seal_sha256": plan["a4"]["table_seal_sha256"],
                "receipt_file_sha256": plan["a4"]["receipt_file_sha256"], "sidecar_file_sha256": plan["a4"]["sidecar_file_sha256"],
                "producing_commit": plan["a4"]["producing_commit"], "code_hash": plan["a4"]["code_hash"]}
    payload, receipt, sidecar, before = load_a4_publication(family_path, identity)
    _require(calibration.get("sha256") == receipt.get("calibration_sha256"),
             "calibration hash differs from the A4 receipt")

    # The A1 source is unchanged.
    actual_a1 = file_hash(Path(a1_source_root) / "v3_rerun_tables_A1.json")
    _require(actual_a1 == plan["a1_source_file_sha256"], "A1 source publication changed since prepare")

    # Census hashes are taken from the receipt just re-verified, not the plan's
    # copy; the plan's copy must agree (it is bound into the plan hash).
    receipt_hashes = {jid: (receipt.get("stage_output_sha256") or {}).get(jid) for jid in plan["a4_census_jobs"]}
    _require(receipt_hashes == plan["a4_census_output_sha256"], "census hashes differ from the re-verified receipt")
    census = read_census(a4_run_root, plan["a4_census_jobs"], receipt_hashes)

    stage_hashes, stream_seeds = _verify_stage_outputs(plan, a5_run_root)
    stage_results = [read(Path(a5_run_root) / j["config"]["phase"] / "outputs" / (j["id"] + ".json"))["result"]
                     for j in plan["jobs"]]

    rows, totals = build_labels(plan, stage_results, census)
    _require(totals["cells"] == plan["M"], "classified cell count differs from the pinned M")

    record = {"schema": "v3-A5-label-1", "amendment": AMENDMENT,
              "a4_family": plan["a4"], "a4_census_output_sha256": plan["a4_census_output_sha256"],
              "plan_hash": plan["plan_hash"], "code_hash": code_identity(),
              "M": plan["M"], "alpha": cv.ALPHA, "stream_tag": A5_TAG,
              "stage_output_sha256": stage_hashes, "stream_seeds": stream_seeds,
              "certified_label": CERTIFIED_LABEL, "asymptotic_label": ASYMPTOTIC_LABEL,
              "rows": rows, "totals": totals, "fv_tables": plan["fv_tables"],
              "note": "plain-law FV certification labels; no survival, extinction or fire rate"}
    document = seal(record)

    # Label-only check, before writing: the A4 family, receipt and sidecar bytes
    # are still what prepare pinned, so a change during publish stops us before a
    # record is written.
    _, _, _, before_write = load_a4_publication(family_path, identity)
    _require(before_write == before, "A5 must not change the A4 family, receipt or sidecar bytes")

    target_path = scoped(target) if str(Path(target).resolve()).startswith(str(ROOT)) else SIMULATION / target
    # Refuse to overwrite a published label record with different bytes.
    if target_path.exists() and read(target_path) != document:
        raise RuntimeError("A5 label record is frozen; publish a new path")
    atomic_json(target_path, document)

    # Label-only check, after writing too.
    _, _, _, after = load_a4_publication(family_path, identity)
    _require(after == before, "A5 must not change the A4 family, receipt or sidecar bytes")

    return {"rows": len(rows), "M": plan["M"], "certified": totals["certified"],
            "unresolved": totals["unresolved"], "violations": totals["violation"]}


def report(label_record_path, output_path):
    """A5's reporting items, per row and in total: counts of certified,
    unresolved and violating cells; the share of plain-law visits in certified
    cells; the share of living census endpoints in certified cells; and every
    violation with its exposure. No survival, extinction or fire rate."""
    record = unseal(read(label_record_path))
    per_row = []
    all_violations = []
    for row in record["rows"]:
        per_row.append({"row_key": row["row_key"], "a1_job_id": row["a1_job_id"], "scoring": row["scoring"],
                        "certified": row["certified"], "unresolved": row["unresolved"], "violation": row["violation"],
                        "certified_visit_share": row["certified_visit_share"],
                        "certified_census_share": row["certified_census_share"],
                        "violation_count": row["violation_count"],
                        "violation_exposure_total": row["violation_exposure_total"]})
        for v in row["violations"]:
            all_violations.append({"row_key": row["row_key"], "a1_job_id": row["a1_job_id"],
                                   "cell": v["cell"], "interval": v["interval"], "exposure": v["exposure"]})
    result = {"schema": "v3-A5-report-1", "amendment": AMENDMENT, "M": record["M"],
              "certified_label": CERTIFIED_LABEL, "asymptotic_label": ASYMPTOTIC_LABEL,
              "totals": {"certified": record["totals"]["certified"], "unresolved": record["totals"]["unresolved"],
                         "violation": record["totals"]["violation"], "cells": record["totals"]["cells"],
                         "certified_visit_share": record["totals"]["certified_visit_share"],
                         "certified_census_share": record["totals"].get("certified_census_share")},
              "census_pooling": "sum of certified-cell living census endpoints over sum of living census endpoints, over tested rows",
              "rows": per_row, "violations": all_violations,
              "note": "plain-law FV certification labels; no survival, extinction or fire rate"}
    out = scoped(output_path) if str(Path(output_path).resolve()).startswith(str(ROOT)) else SIMULATION / output_path
    atomic_json(out, result)
    return {"rows": len(per_row), "certified": result["totals"]["certified"],
            "unresolved": result["totals"]["unresolved"], "violations": len(all_violations)}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("a4_family"); p.add_argument("a4_run_root"); p.add_argument("a4_plan")
    p.add_argument("a1_source_root"); p.add_argument("calibration_path")
    p.add_argument("identity_record"); p.add_argument("output")
    p.add_argument("--pin"); p.add_argument("--wall-hours", type=int, default=24); p.add_argument("--a3-probe-root")
    p = sub.add_parser("publish")
    p.add_argument("plan"); p.add_argument("a5_run_root"); p.add_argument("a4_run_root")
    p.add_argument("a1_source_root"); p.add_argument("calibration"); p.add_argument("target")
    p = sub.add_parser("report"); p.add_argument("record"); p.add_argument("output")
    args = parser.parse_args()
    if args.command == "prepare":
        plan = prepare(args.a4_family, args.a4_run_root, args.a4_plan, args.a1_source_root, args.calibration_path,
                       args.identity_record, read(args.pin) if args.pin else None, args.wall_hours, args.a3_probe_root)
        out = args.output if str(Path(args.output).resolve()).startswith(str(ROOT)) else SIMULATION / args.output
        atomic_json(out, seal(plan))
        print({"phase": PHASE, "jobs": len(plan["jobs"]), "M": plan["M"], "fv_tables": plan["fv_tables"], "launched": False})
    elif args.command == "publish":
        print(publish(unseal(read(args.plan)), args.a5_run_root, args.a4_run_root, args.a1_source_root,
                      read(args.calibration), args.target))
    else:
        print(report(args.record, args.output))


if __name__ == "__main__":
    main()
