"""Build and analyze the non-registered X2 pilot. No remote launch code."""
import argparse
import json
from pathlib import Path
import statistics
import zipfile
from .artifacts import ROOT, SIMULATION, atomic_json, read, seal, unseal, digest, source_manifest, code_identity, stable_job, file_hash, scoped


def profile(kind, config):
    return {"kind": kind, "config": config, "workers_x2": [8, 12, 16, 24, 28, 31, 32],
            "workers_local": [1, 2], "jobs_x2": 32, "jobs_local": 4, "threads": [1],
            "rounds": 2, "material_multithreaded_numerics": False}


def make_spec():
    from .offline_estimator import settings_for, SENSITIVITY_RULES
    from .study import scoring_for_rr, table_design
    jobs = []
    cases = [(.055, .5, 1.5), (.060, 1., 1.5), (.064, 1.5, 1.5),
             (.057, 1.25, 1.2), (.064, .75, 3.), (.070, 1.5, 5.)]
    for rr, alpha, cap in cases:
        cfg = {"phase": "rerun", "steps": 500, "model": {"reproduction_rate": rr, "alpha": alpha, "successor_capability": cap}}
        jobs.extend(stable_job("rerun", cfg, "pilot", i) for i in range(3))
    for route in ("plain", "fv"):
        for rule in SENSITIVITY_RULES:
            for rr in (.055, .070):
                cfg = {"phase": "table_" + route, "rule_id": rule, "kernel": {"reproduction_rate": rr},
                       "route": route, "settings": settings_for(), "setting_name": "primary", "scoring": scoring_for_rr(rr)}
                jobs.append(stable_job("table", cfg, "pilot", 0))
    for name in ("double_population", "double_length"):
        cfg = {"phase": "table_fv", "rule_id": "balanced", "kernel": {"reproduction_rate": .064},
               "route": "auto", "settings": settings_for(name), "setting_name": name, "scoring": scoring_for_rr(.064)}
        jobs.append(stable_job("table", cfg, "pilot", 0))
    for i in range(3):
        jobs.append(stable_job("calibration", {"phase": "calibration", "steps": 500, "n_agents": 200, "reproduction_rate": .08}, "pilot", i))
    short_table = {**settings_for(), "burn": 4, "measure": 8}
    configurations = {
        "rerun": profile("rerun", {"steps": 5, "model": {"reproduction_rate": .064, "alpha": 1., "successor_capability": 3.}}),
        "table_plain": profile("table", {"rule_id": "balanced", "kernel": {"reproduction_rate": .064}, "route": "plain", "settings": short_table, "scoring": scoring_for_rr(.064)}),
        "table_fv": profile("table", {"rule_id": "balanced", "kernel": {"reproduction_rate": .064}, "route": "fv", "settings": short_table, "scoring": scoring_for_rr(.064)}),
        "calibration": profile("calibration", {"steps": 20, "n_agents": 200, "reproduction_rate": .08}),
    }
    return {"schema": "v3-pilot-1", "tag": "pilot", "registered": False, "code_hash": code_identity(),
            "wall_seconds": 10800, "configuration_seconds": 900, "cleanup_reserve_seconds": 300,
            "phases": ["rerun", "table_plain", "table_fv", "calibration"], "configuration": configurations,
            "jobs": jobs, "table_design": table_design(), "rerun_total": 24900, "rerun_steps": 500,
            "rerun_budget_hours": 72, "table_budget_hours": 24, "calibration_total": 50,
            "fixture_tables": True, "results_eligible": False,
            "projection_method": "actual X2 job costs scaled by measured configuration throughput; case means and conservative maximum, no local speed ratio"}


def project_costs(spec, root, outcomes, measurements):
    from .production_runner import completed, choose
    grouped = {}
    for job in spec["jobs"]:
        phase = job["config"].get("phase", job["kind"])
        result = completed(root / phase, job, spec["code_hash"])
        if result is not None:
            grouped.setdefault(phase, []).append(result)
    if any(not grouped.get(phase) for phase in spec["phases"]) or sum(map(len, grouped.values())) != len(spec["jobs"]):
        return {"status": "incomplete", "reason": "missing pilot jobs or phases; no budget pass claimed", "completed_jobs": sum(map(len, grouped.values()))}
    selections = {phase: outcomes[phase]["selection"] for phase in spec["phases"]}
    # Configuration throughput captures dispatch and concurrent interference.
    # Infer effective parallelism from worker time / measured wall time.
    effective = {}
    for phase, rows in measurements.items():
        selected = selections[phase]
        matched = [r for r in rows if r["valid"] and r["workers"] == selected["workers"] and r["threads"] == selected["threads"]]
        effective[phase] = min(float(selected["workers"]), sum(sum(r["job_seconds"]) for r in matched) / sum(r["wall_seconds"] for r in matched))
    rerun_cases = {}
    def seconds(output):
        return output.get("worker_seconds", output["seconds"])
    for output in grouped["rerun"]:
        key = digest(output["job"]["config"])
        rerun_cases.setdefault(key, []).append(seconds(output))
    case_means = [statistics.mean(v) for v in rerun_cases.values()]
    rerun_mean = statistics.mean(case_means) * 24900 / effective["rerun"] / 3600
    rerun_upper = max(case_means) * 24900 / effective["rerun"] / 3600
    primary_plain = [o for o in grouped["table_plain"] if o["job"]["config"]["setting_name"] == "primary"]
    primary_fv = [o for o in grouped["table_fv"] if o["job"]["config"]["setting_name"] == "primary"]
    from .study import scoring_contexts, scoring_for_rr
    maximum_scoring_rows = max(len(scoring_for_rr(rr)) for rr, _, _ in scoring_contexts())
    def primary_seconds(output):
        rows = len(output["job"]["config"]["scoring"])
        # Same sampled kernel, more scoring contexts at other rr. Preserve
        # measured trajectory cost and scale only measured rescoring work.
        scoring_time = output["result"].get("rescore_seconds", seconds(output))
        return seconds(output) + scoring_time * (maximum_scoring_rows / rows - 1)
    plain = max(primary_seconds(o) for o in primary_plain) / effective["table_plain"]
    fv = max(primary_seconds(o) for o in primary_fv) / effective["table_fv"]
    sensitivities = {o["job"]["config"]["setting_name"]: seconds(o) / effective["table_fv"]
                     for o in grouped["table_fv"] if o["job"]["config"]["setting_name"] != "primary"}
    if set(sensitivities) != {"double_population", "double_length"}:
        return {"status": "incomplete", "reason": "sensitivity cost measurements missing"}
    calibration_hours = 50 * max(seconds(o) for o in grouped["calibration"]) / effective["calibration"] / 3600
    # 325 nominal rule/kernel primary jobs, 9 pairs at both sensitivities.
    # Worst observed route and sensitivity costs; no unmeasured row is dropped.
    table_hours = (325 * max(plain, fv) + 9 * sum(sensitivities.values())) / 3600 + calibration_hours + .25
    x2 = all(o["runtime"]["machine"].lower() == "yotko-evo-x2" for outputs in grouped.values() for o in outputs)
    return {"status": "measured_pilot_projection" if x2 else "local_only_projection", "machine": grouped["rerun"][0]["runtime"]["machine"],
            "tag": "pilot", "results_eligible": False, "actual_X2_measurement": x2,
            "effective_workers_from_configuration": effective, "selections": selections,
            "rerun_hours_case_mean": rerun_mean, "rerun_hours_max_case": rerun_upper,
            "rerun_gap_hours": max(0, rerun_upper - 72) if x2 else None, "rerun_within_72h_projection": rerun_upper <= 72 if x2 else None,
            "table_hours_conservative": table_hours, "table_gap_hours": max(0, table_hours - 24) if x2 else None,
            "primary_table_scoring_context_allowance": maximum_scoring_rows,
            "tables_within_24h_projection": table_hours <= 24 if x2 else None, "calibration_hours": calibration_hours,
            "case_means_seconds": case_means,
            "population_summaries": [{"config": o["job"]["config"], "mean": o["result"]["population_mean"], "max": o["result"]["population_max"]} for o in grouped["rerun"]],
            "limitations": ["pilot reruns use fixture scoring tables; decisions and cost can change with calibrated tables",
                            "case means are extrapolations across the full frozen grid, not throughput guarantees",
                            "route choice, row failures and extra kernels for crowding/novelty sensitivities remain explicit",
                            "no unmeasured WE fallback; flagged rows do not disappear from the manifest"]}


def build_bundle(target=None):
    target = scoped(target or ROOT / "pilot_bundle")
    target.mkdir(parents=True, exist_ok=True)
    spec = seal(make_spec())
    atomic_json(ROOT / "pilot_manifest.json", spec)
    sources = source_manifest()
    paths = {name: SIMULATION / name for name in sources}
    paths["v3/pilot_manifest.json"] = ROOT / "pilot_manifest.json"
    paths["v3/v3_pilot_RUN_ON_X2.md"] = ROOT / "v3_pilot_RUN_ON_X2.md"
    members = {"simulation/" + name: path.read_bytes() for name, path in paths.items()}
    manifest = {"tag": "pilot", "registered": False, "results_eligible": False, "code_hash": code_identity(),
                "spec_hash": spec["sha256"], "files": {name: __import__("hashlib").sha256(data).hexdigest() for name, data in sorted(members.items())}}
    members["BUNDLE_MANIFEST.json"] = (__import__("json").dumps(seal(manifest), sort_keys=True, indent=2) + "\n").encode()
    archive = target / "v3_pilot_bundle.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as stream:
        for name, data in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 27, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            stream.writestr(info, data)
    atomic_json(target / "bundle_receipt.json", {"archive": archive.name, "sha256": file_hash(archive), "manifest": seal(manifest), "bytes": archive.stat().st_size})
    return {"archive": str(archive), "sha256": file_hash(archive), "jobs": len(spec["payload"]["jobs"]), "spec_hash": spec["sha256"]}


def verify_bundle(directory):
    directory = Path(directory).resolve()
    manifest = unseal(read(directory / "BUNDLE_MANIFEST.json"))
    for name, expected in manifest["files"].items():
        path = (directory / name).resolve()
        if not path.is_relative_to(directory) or file_hash(path) != expected:
            raise ValueError("bundle member missing or changed")
    if manifest["tag"] != "pilot" or manifest["registered"] or manifest["results_eligible"]:
        raise ValueError("invalid pilot provenance")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "project"))
    parser.add_argument("path", nargs="?")
    args = parser.parse_args()
    if args.command == "build":
        print(build_bundle())
    elif args.command == "verify":
        print({"verified": True, "spec_hash": verify_bundle(args.path or ".")["spec_hash"]})
    else:
        root = Path(args.path)
        record = read(root / "launches.json")[-1]
        result = project_costs(unseal(read(ROOT / "pilot_manifest.json")), root, record.get("outcomes", {}), record["configuration"])
        atomic_json(root / "cost_projection.json", result)
        print(result)


if __name__ == "__main__":
    main()
