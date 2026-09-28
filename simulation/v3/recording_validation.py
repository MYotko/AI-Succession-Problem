"""Frozen non-registered A2 comparisons and runner evidence validation.

The reference interpreter imports an isolated snapshot extracted from Git
34ffbfe9. This module is never part of a registered scientific workload.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from .artifacts import ROOT, SIMULATION, read, unseal, seal, atomic_json, canonical, digest, code_identity, stable_job, file_hash

WORK = ROOT / "runs/a2_recording_validation"
COMMIT = "34ffbfe99e79ea9f546f1ed353a251ef8aede08e"


def validation_probe_compatible(document, file_sha256):
    """Only the existing frozen pilot fixture, never registered tables.

    Keeps the six original validation inputs/seeds usable after closing
    the former broad A1 compatibility exception. Exact bytes are required.
    The production loader calls this only in non-registered fixture mode.
    """
    return (document.get("sha256") == "b8514fc253961874cc420999b5b31056918f2c0879a8528c72a6fe3fc9114285" and
            digest(document["payload"]) == document["sha256"] and
            file_sha256 == "80444e1dffe6f63f7fe9254208c8493a5c361bb584c56dc0fdec374582feffd3" and
            document["payload"].get("fixture") is True and document["payload"]["manifest"].get("tag") == "pilot")


def refresh_boundary():
    """Print proposed hashes for review. Never approve or write them."""
    path = ROOT / "table_compatibility_A2.json"
    record = read(path)
    for key in record["approved_boundary_sha256"]:
        record["approved_boundary_sha256"][key] = hashlib.sha256((SIMULATION / key).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    print(json.dumps(record["approved_boundary_sha256"], sort_keys=True, indent=2))
    return record["approved_boundary_sha256"]


def prepare():
    def git(*args):
        return subprocess.run(["git", "-C", str(SIMULATION.parent), *args], check=True, capture_output=True).stdout
    baseline = WORK / "baseline/simulation"
    source = {}
    for name in git("ls-tree", "-r", "--name-only", COMMIT, "simulation").decode().splitlines():
        p = Path(name)
        if p.suffix != ".py" or p.name.startswith("test_") or p.parent.as_posix() not in ("simulation", "simulation/v3"):
            continue
        content = git("show", f"{COMMIT}:{name}")
        path = baseline / p.relative_to("simulation")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        source[name] = hashlib.sha256(content).hexdigest()
    name = "simulation/v3/calibration_compatibility_A1.json"
    (baseline / "v3/calibration_compatibility_A1.json").write_bytes(git("show", f"{COMMIT}:{name}"))
    atomic_json(WORK / "baseline_source.json", {"commit": COMMIT, "sha256": source})
    # Repackage existing non-registered probe estimates without changing a row.
    # Their failed statuses and sparse publication domains remain unchanged.
    from .production_tables import row_key
    from .study import table_design
    sources = sorted((ROOT / "amendment_probe_extended/table_diagnostic/outputs").glob("*.json"))
    rows = [r for path in sources for r in read(path)["result"]["rows"]]
    cal_path = ROOT / "runs/registered/v3_rerun_calibration.json"
    cal = read(cal_path)
    manifest = {"tag": "pilot", "calibration_hash": cal["sha256"], "design": table_design(),
                "required_row_keys": sorted(row_key(r) for r in rows), "complete_family": False,
                "sensitivity_status": "incomplete_or_failed",
                "probe_sources": [{"path": str(p), "sha256": file_hash(p)} for p in sources]}
    producer = read(ROOT / "table_compatibility_A2.json")["producer_code_hash"]
    tables = seal({"schema": "v3-tables-1", "fixture": True, "code_hash": producer,
                   "manifest": manifest, "manifest_hash": digest(manifest), "rows": {row_key(r): seal(r) for r in rows}})
    table_path = WORK / "A1_probe_tables.json"
    atomic_json(table_path, tables)
    cases = [("R1", .064, .5, 1.5, 200, True), ("refinement", .063, 1., 1.5, 200, True),
             ("R2", .055, 1.5, 1.8, 40, True), ("R1", .060, .5, 1.5, 200, False),
             ("refinement", .061, 1.5, 1.5, 40, False), ("R2", .064, 1., 3., 200, False)]
    jobs = []
    for i, (category, rr, alpha, cap, n, probe) in enumerate(cases):
        config = {"phase": "rerun", "category": category, "steps": 500, "calibration_path": str(cal_path),
                  "model": {"reproduction_rate": rr, "alpha": alpha, "successor_capability": cap, "n_agents": n}}
        if probe:
            config["tables_path"] = str(table_path)
        jobs.append(stable_job("rerun", config, "validation", i))
    config = dict(jobs[-1]["config"], steps=3)
    spec = {"schema": "v3-a2-validation-1", "registered": False, "tag": "validation", "code_hash": code_identity(),
            "wall_seconds": 1800, "cleanup_reserve_seconds": 30, "configuration_seconds": 180,
            "phases": ["rerun"], "configuration": {"rerun": {"kind": "rerun", "config": config,
                "workers_local": [2, 4], "workers_x2": [8, 12, 16, 24, 32], "jobs_local": 4, "jobs_x2": 32,
                "threads": [1], "rounds": 1}}, "jobs": jobs, "publication": None}
    atomic_json(WORK / "spec.json", seal(spec))
    return {"jobs": len(jobs), "spec": str(WORK / "spec.json"), "baseline": str(baseline), "tables": "existing sparse probe rows and existing FixtureTables"}


REFERENCE_SCRIPT = r'''
import hashlib, json, time
from pathlib import Path
import numpy as np
from v3.artifacts import read, canonical
from v3.production_runner import execute
from v3.integration import V3Model
job = read(JOB_PATH)
trace = hashlib.sha256(); count = [0]
original = V3Model._rng
class Audited:
    def __init__(self, rng, identity): self.rng, self.identity = rng, identity
    def __getattr__(self, name):
        target = getattr(self.rng, name)
        def draw(*args, **kwargs):
            value = target(*args, **kwargs)
            array = np.asarray(value)
            trace.update(canonical([self.identity, name, str(array.dtype), array.shape]))
            trace.update(array.tobytes()); count[0] += 1
            return value
        return draw
V3Model._rng = lambda self, channel: Audited(original(self, channel), [self.time, channel])
start = time.perf_counter()
result = execute(job, False, None)
elapsed = time.perf_counter() - start
Path(OUT_PATH).write_bytes(canonical({'result':result,'seconds':elapsed,'draw_sha256':trace.hexdigest(),'draw_calls':count[0]}) + b'\n')
'''


def compare(workers=4):
    if not 1 <= workers <= 8:
        raise ValueError("local validation worker limit is eight")
    spec = unseal(read(WORK / "spec.json"))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1")
    tasks = []
    for job in spec["jobs"]:
        path = WORK / "pairs" / (job["id"] + ".job.json")
        atomic_json(path, job)
        for variant in ("baseline", "amended"):
            tasks.append((job, path, variant))
    def run(item):
        job, path, variant = item
        output = WORK / "pairs" / (job["id"] + "." + variant + ".json")
        body = "JOB_PATH=" + repr(str(path)) + "\nOUT_PATH=" + repr(str(output)) + "\n" + REFERENCE_SCRIPT
        python_path = WORK / "baseline/simulation" if variant == "baseline" else SIMULATION
        subprocess.run([sys.executable, "-B", "-c", body], cwd=python_path, env=dict(env, PYTHONPATH=str(python_path)), check=True,
                       capture_output=True, timeout=900)
        return output
    with ThreadPoolExecutor(max_workers=workers) as pool:
        paths = list(pool.map(run, tasks))
    report = []
    for job in spec["jobs"]:
        base, new = [read(WORK / "pairs" / (job["id"] + "." + v + ".json")) for v in ("baseline", "amended")]
        recording = new["result"].pop("gate_evidence")
        same = canonical(base["result"]) == canonical(new["result"])
        row = {"job": job, "scientific_bytes_identical": same,
               "baseline_sha256": digest(base["result"]), "amended_stripped_sha256": digest(new["result"]),
               "draw_hash_identical": base["draw_sha256"] == new["draw_sha256"], "draw_calls": [base["draw_calls"], new["draw_calls"]],
               "baseline_seconds": base["seconds"], "amended_seconds": new["seconds"], "overhead_seconds": new["seconds"] - base["seconds"],
               "baseline_result_bytes": len(canonical(base["result"])), "evidence_bytes": len(canonical(recording)),
               "raw_evidence_bytes": recording["raw_bytes"],
               "fired": sum(e["transition_count"] for e in new["result"]["yield_events"]),
               "above_bound_periods": sum(not p["admitted"] for p in new["result"]["periods"]),
               "balanced_fallback_steps": new["result"]["continuation_availability"]["balanced_fallback_steps"]}
        if not same or not row["draw_hash_identical"] or base["draw_calls"] != new["draw_calls"]:
            raise AssertionError(row)
        report.append(row)
    atomic_json(WORK / "noninterference.json", {"registered": False, "baseline_commit": COMMIT,
                 "table_scope": "Existing non-registered probe rows, unchanged, and existing FixtureTables; not A1 registered tables",
                 "comparison_scope": "Exact canonical result bytes excluding evidence; operational timestamps/source identities necessarily differ",
                 "private_diagnostic_draws": "excluded from scientific draw audit; never advance original streams", "jobs": report})
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("prepare", "compare")); p.add_argument("--workers", type=int, default=4)
    a = p.parse_args()
    print(prepare() if a.command == "prepare" else compare(a.workers))


if __name__ == "__main__":
    main()
