"""Read-only audit of a completed table family; writes derived diagnostics only."""
import argparse
from collections import Counter, defaultdict
import math
from pathlib import Path
import statistics
from .artifacts import read, unseal, file_hash, digest, atomic_json
from .production_tables import row_key


def row_metrics(row):
    threshold = .05 * row["flow_range"]
    c = row.get("continuation") or {}
    lf = row.get("lambda_f") or {}
    halves = row.get("half_window_means", [])
    drift = abs(halves[1] - halves[0]) if len(halves) == 2 and None not in halves else None
    values = {"flow_half_width": lf.get("half_width"), "half_window_drift": drift,
              "bellman_residual": c.get("bellman_residual_empirical"), "continuation_coverage": c.get("heldout_coverage"),
              "survival_fraction": row.get("surviving_fraction")}
    limits = {"flow_half_width": threshold, "half_window_drift": threshold, "bellman_residual": threshold,
              "continuation_coverage": .9, "survival_fraction": .5}
    deficits = {key: None if value is None else (limits[key] - value if key in ("continuation_coverage", "survival_fraction") else value - limits[key])
                for key, value in values.items()}
    # FV survivor fraction describes pre-cloning kills and has no .5 gate.
    if row.get("route") == "fv":
        deficits["survival_fraction"] = None
    return {"rule": row["rule_id"], "context": row["scoring"], "row_key": row_key(row), "status": row["status"],
            "route": row.get("route"), "screens": row.get("screens", {}), "values": values, "limits": limits, "excess": deficits,
            "flow_range": row["flow_range"], "lambda_mean": lf.get("mean"), "replicates": lf.get("replicates", []),
            "half_means": halves, "continuation_entries": len(c.get("entries", [])),
            "fixed_point_converged": c.get("training_fixed_point_converged"), "iterations": c.get("iterations"),
            "minimum_training_visits": min((e["training_visits"] for e in c.get("entries", [])), default=None),
            "minimum_heldout_visits": min((e["heldout_visits"] for e in c.get("entries", [])), default=None)}


def contrast(primary, other):
    a, b = primary.get("lambda_f"), other.get("lambda_f")
    if not a or not b or a["mean"] is None or b["mean"] is None:
        return {"computable": False}
    av, bv = a["replicates"], b["replicates"]
    half = 2.015 * math.sqrt(statistics.variance(av) / len(av) + statistics.variance(bv) / len(bv))
    difference = b["mean"] - a["mean"]
    limit = .05 * primary["flow_range"]
    return {"computable": True, "difference": difference, "half_width": half, "limit": limit,
            "excess": abs(difference) + half - limit, "contrast_passed": abs(difference) + half <= limit,
            "other_status": other["status"], "other_failed_screens": [k for k, v in other.get("screens", {}).items() if not v]}


def audit(root):
    root = Path(root)
    table_document = read(root / "v3_rerun_tables.json")
    table = unseal(table_document)
    calibration = read(root / "v3_rerun_calibration.json")
    unseal(calibration)
    specification = unseal(read(root / "tables_manifest.json"))
    required_jobs = {j["id"]: j for j in specification["jobs"]}
    published = {k: unseal(v) for k, v in table["rows"].items()}
    if set(published) != set(table["manifest"]["required_row_keys"]):
        raise ValueError("incomplete published keys")
    primary, sensitivity, rows, jobs = {}, {}, [], []
    for job_id, job in required_jobs.items():
        path = root / "tables" / "table" / "outputs" / (job_id + ".json")
        output = read(path)
        record = read(root / "tables" / "table" / "records" / (job_id + ".json"))
        if record["status"] != "complete" or file_hash(path) != record["output_hash"] or output["job"] != job or record["job"] != job:
            raise ValueError("job or completion identity mismatch")
        if output["code_hash"] != table["code_hash"] or record["code_hash"] != table["code_hash"]:
            raise ValueError("mixed source identities")
        result, config = output["result"], job["config"]
        if result["calibration_hash"] != calibration["sha256"]:
            raise ValueError("calibration mismatch")
        rr, setting = config["kernel"]["reproduction_rate"], config["setting_name"]
        for row in result["rows"]:
            metric = row_metrics(row)
            metric.update(rr=rr, setting=setting, job_id=job_id)
            rows.append(metric)
            key = row_key(row)
            if setting == "primary":
                if key in primary:
                    raise ValueError("duplicate primary")
                primary[key] = row
            else:
                sensitivity.setdefault(key, {})[setting] = row
        jobs.append({"id": job_id, "rule": config["rule_id"], "rr": rr, "setting": setting,
                     "route": result["route"], "settings": result["settings"], "seed": job["seed"],
                     "seconds": record.get("worker_seconds", output["seconds"]),
                     "trajectory_seconds": result["trajectory_seconds"], "rescore_seconds": result["rescore_seconds"],
                     "population_mean": result["population_mean"], "population_max": result["population_max"],
                     "plain_final_survivors": result["plain_survivor_counts"][-1],
                     "ensemble_collapses": result["ensemble_collapses"],
                     "input_sha256": record["output_hash"], "row_count": len(result["rows"])})
    if set(primary) != set(published):
        raise ValueError("published family differs from job family")
    contrasts, pair_counts = [], defaultdict(Counter)
    primary_metrics = {r["row_key"]: r for r in rows if r["setting"] == "primary"}
    for key, row in published.items():
        if not row["sensitivity"]["selected"]:
            continue
        metric = primary_metrics[key]
        for setting in ("double_population", "double_length"):
            other = sensitivity.get(key, {}).get(setting)
            result = {"computable": False, "missing": True} if other is None else contrast(primary[key], other)
            contrasts.append({"row_key": key, "rule": row["rule_id"], "rr": metric["rr"], "context": row["scoring"], "setting": setting, **result})
        counts = pair_counts[(row["rule_id"], metric["rr"])]
        counts["rows"] += 1
        counts["published_failed"] += not row["sensitivity"]["passed"]
        counts["primary_not_estimable"] += primary[key]["status"] != "estimated"
    summaries = {}
    for setting in ("primary", "double_population", "double_length"):
        family = [r for r in rows if r["setting"] == setting]
        failed = [r for r in family if r["status"] != "estimated"]
        summaries[setting] = {"rows": len(family), "not_estimable": len(failed),
            "failed_rule_kernels": len({(r["rule"], r["rr"]) for r in failed}),
            "screens": dict(Counter(k for r in family for k, v in r["screens"].items() if not v)),
            "continuation_reasons": {"residual": sum(r["excess"]["bellman_residual"] is not None and r["excess"]["bellman_residual"] > 0 for r in family),
                                     "coverage": sum(r["excess"]["continuation_coverage"] is not None and r["excess"]["continuation_coverage"] > 0 for r in family),
                                     "solver": sum(not r["fixed_point_converged"] for r in family),
                                     "empty": sum(not r["continuation_entries"] for r in family)},
            "worst": {k: sorted((r for r in family if r["excess"][k] is not None), key=lambda r: r["excess"][k], reverse=True)[:3]
                      for k in ("flow_half_width", "half_window_drift", "bellman_residual", "continuation_coverage", "survival_fraction")}}
    launches = read(root / "tables" / "launches.json")
    return {"schema": "v3-table-screen-audit-1", "source_table_sha256": table_document["sha256"],
            "calibration_sha256": calibration["sha256"], "registered_code_hash": table["code_hash"],
            "source_manifest_sha256": digest(specification), "input_job_hashes_verified": len(jobs),
            "design": {k: v for k, v in table["manifest"]["design"].items() if k != "scoring_contexts"},
            "summary": summaries, "published_status": dict(Counter(r["status"] for r in published.values())),
            "sensitivity_pairs": [{"rule": rule, "rr": rr, **counts} for (rule, rr), counts in sorted(pair_counts.items())],
            "contrasts": contrasts, "rows": rows, "jobs": jobs,
            "table_execution": launches[-1]["outcomes"]["table"],
            "table_service": read(root / "tables" / "service.json"),
            "no_rerun_directory": not (root / "reruns").exists() and not (root / "rerun").exists()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input"); parser.add_argument("output")
    args = parser.parse_args()
    result = audit(args.input)
    atomic_json(args.output, result)
    print({"jobs_verified": result["input_job_hashes_verified"], "published_status": result["published_status"],
           "summaries": {s: {k: v for k, v in r.items() if k != "worst"} for s, r in result["summary"].items()},
           "sensitivity_pairs": result["sensitivity_pairs"]})


if __name__ == "__main__":
    main()
