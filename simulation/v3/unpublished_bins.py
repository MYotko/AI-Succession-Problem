"""Read-only endpoint diagnostics on archived fixed-rule trajectory seeds.

The replay is plain, unconditioned and never scores W or produces a rerun
outcome. FV table bins can be checked on these plain paths. Their law is
not the adaptive all-rule allocation law, and marginal rates cannot give
the joint probability of the balanced fallback.
"""
import argparse
from pathlib import Path
import numpy as np
from .artifacts import ROOT, read, unseal, seal, file_hash, atomic_json, code_identity, stable_job


def coverage_bounds(row):
    """Bounds on unpublished *source* bins from the archived legacy check.

    Legacy coverage excluded unknown successors too. Entry visit counts
    alone therefore cannot identify an endpoint miss rate.
    """
    c = row["continuation"]
    if "legacy_all_training_bins" in c:
        raise ValueError("archived legacy entry counts required for source-bin bounds")
    n = c["heldout_transitions"]
    published_covered = sum(e["heldout_visits"] for e in c["entries"])
    return {"heldout_transitions": n, "published_source_and_known_successor": published_covered,
            "unpublished_source_fraction_lower": max(0., c["heldout_coverage"] - published_covered / n),
            "unpublished_source_fraction_upper": 1 - published_covered / n}


def endpoint_counts(trace, published, horizon=20, steps=500):
    """Use t+20 along held-out plain paths, omitting already extinct starts."""
    groups = trace["groups"]
    heldout = groups >= int(np.max(groups)) - 1
    alive = trace["features"][..., 0] > 0
    initial_alive = np.ones((1, alive.shape[1]), dtype=bool)
    start_alive = np.concatenate((initial_alive, alive[:steps - 1]))[:, heldout]
    end_alive = alive[horizon - 1:horizon - 1 + steps, heldout]
    endpoints = trace["after"][horizon - 1:horizon - 1 + steps, heldout]
    # Encode the small integer summary without a tuple per observation.
    radix = np.array([16**i for i in range(6)], dtype=np.int64)
    keys = endpoints.astype(np.int64) @ radix
    domain = np.asarray(sorted(published), dtype=np.int64).reshape(-1, 6) @ radix
    missing = start_alive & end_alive & ~np.isin(keys, domain)
    def counts(start, stop):
        opportunities = int(start_alive[start:stop].sum())
        live_endpoints = int((start_alive[start:stop] & end_alive[start:stop]).sum())
        misses = int(missing[start:stop].sum())
        return {"start_step": start, "stop_step_exclusive": stop,
                "allocation_opportunities": opportunities, "living_endpoints": live_endpoints,
                "exact_extinct_endpoints": opportunities - live_endpoints, "unpublished_endpoints": misses,
                "exclusion_fraction": misses / opportunities if opportunities else None,
                "fraction_among_living_endpoints": misses / live_endpoints if live_endpoints else None}
    return {**counts(0, steps), "heldout_paths": int(heldout.sum()), "horizon": horizon,
            "blocks": [counts(t, min(t + 100, steps)) for t in range(0, steps, 100)],
            "first_20_starts": counts(0, min(20, steps)),
            "paths_with_any_exclusion": int(missing.any(axis=0).sum())}


def replay(config):
    from .context import Context
    from .offline_estimator import simulate, _rule
    path = Path(config["source_output"])
    if file_hash(path) != config["source_sha256"]:
        raise ValueError("archived output changed")
    old = read(path)
    original = old["job"]["config"]
    calibration = read(config["calibration_path"])
    if calibration["sha256"] != old["result"]["calibration_hash"]:
        raise ValueError("replay calibration mismatch")
    horizon, steps = config.get("horizon", 20), config.get("steps", 500)
    settings = {**original["settings"], "burn": 0, "measure": horizon + steps - 1}
    ctx = Context.build(original["kernel"], calibration)
    trace = simulate(ctx, _rule(original["rule_id"]), settings, old["job"]["seed"], "plain")
    # Truncating allocation length changes no RNG draws or transition law.
    expected = old["result"]["plain_survivor_counts"][:settings["measure"]]
    if trace["survivor_counts"] != expected:
        raise RuntimeError("replay differs from the archived trajectory prefix")
    domains = [{tuple(e["bin"]) for e in row["continuation"]["entries"]} for row in old["result"]["rows"]]
    if not domains or any(d != domains[0] for d in domains):
        raise ValueError("context-dependent publication domains require separate analysis")
    return {"registered": False, "rule": original["rule_id"], "rr": original["kernel"]["reproduction_rate"],
            "table_settings": original["settings"], "table_route": old["result"]["route"],
            "source_output_sha256": config["source_sha256"], "replayed_seed": old["job"]["seed"],
            "prefix_survivor_counts_match": True, "table_status_ignored_for_domain_diagnostic_only": True,
            "law": "held-out independent plain fixed-rule paths from the archived initial law",
            "adaptive_all_rule_fallback_frequency": None, **endpoint_counts(trace, domains[0], horizon, steps)}


def prepare(input_root, target):
    from .offline_estimator import SENSITIVITY_RULES, SENSITIVITY_RR
    input_root = Path(input_root)
    cal = str(input_root / "v3_rerun_calibration.json")
    sources = []
    spec = unseal(read(input_root / "tables_manifest.json"))
    for job in spec["jobs"]:
        c = job["config"]
        if c["setting_name"] == "primary" and c["rule_id"] in SENSITIVITY_RULES and c["kernel"]["reproduction_rate"] in SENSITIVITY_RR:
            sources.append(input_root / "tables/table/outputs" / (job["id"] + ".json"))
    for folder in ("amendment_probe", "amendment_probe_extended"):
        for path in sorted((ROOT / folder / "table_diagnostic/outputs").glob("*.json")):
            if read(path)["job"]["config"]["setting_name"] == "primary":
                sources.append(path)
    jobs = [stable_job("continuation_audit", {"phase": "endpoints", "source_output": str(p.resolve()),
                        "source_sha256": file_hash(p), "calibration_path": cal, "steps": 500, "horizon": 20}, "validation", i)
            for i, p in enumerate(sources)]
    profile = {"kind": "continuation_audit", "configs": [{**j["config"], "steps": 8} for j in jobs[-2:]],
               "config": {**jobs[-1]["config"], "steps": 8}, "jobs_local": 8, "jobs_x2": 32,
               "workers_local": [2, 4, 8], "workers_x2": [8, 12, 16, 24, 32], "threads": [1], "rounds": 1}
    spec = {"schema": "v3-endpoint-diagnostic-1", "registered": False, "tag": "validation", "code_hash": code_identity(),
            "wall_seconds": 1200, "cleanup_reserve_seconds": 30, "configuration_seconds": 180,
            "phases": ["endpoints"], "jobs": jobs, "configuration": {"endpoints": profile},
            "purpose": "A1 unpublished endpoint diagnostic; frozen archived seeds, no W scoring or rerun outcomes"}
    atomic_json(target, seal(spec))
    return len(jobs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_root"); parser.add_argument("manifest")
    args = parser.parse_args()
    print({"prepared_jobs": prepare(args.input_root, args.manifest), "launched": False})


if __name__ == "__main__":
    main()
