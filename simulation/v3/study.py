"""Frozen R13 settings and complete primary/refinement job definitions."""
from fractions import Fraction
from .artifacts import stable_job, code_identity, digest

R1_RR = (.055, .056, .057, .058, .059, .060, .062, .064, .066)
REFINEMENT_RR = (.061, .063, .065)
R2_RR = (.057, .060, .064, .070)
R1_ALPHA = (.5, 1., 1.5)
R2_ALPHA = (.5, .75, 1., 1.25, 1.5)
R2_CAP = (1.2, 1.5, 2., 2.5, 3., 4., 5.)


def capabilities(start):
    current = Fraction(str(start))
    result = {Fraction(1)}
    while True:
        result.add(current)
        if current == 5:
            break
        current = min(Fraction(5), current * Fraction(3, 2))
    return sorted(float(v) for v in result)


def scoring_contexts():
    values = set()
    for rr in R1_RR + REFINEMENT_RR:
        for alpha in R1_ALPHA:
            for cap in capabilities(1.5):
                values.add((rr, alpha, cap))
    for rr in R2_RR:
        for alpha in R2_ALPHA:
            for successor in R2_CAP:
                for cap in capabilities(successor):
                    values.add((rr, alpha, cap))
    return sorted(values)


def rerun_jobs(calibration_path, tables_path, tag="v3_rerun"):
    jobs = []
    for category, rates, alphas, caps_, seeds in (
        ("R1", R1_RR, R1_ALPHA, (1.5,), 400),
        ("refinement", REFINEMENT_RR, R1_ALPHA, (1.5,), 400),
        ("R2", R2_RR, R2_ALPHA, R2_CAP, 75),
    ):
        for rr in rates:
            for alpha in alphas:
                for successor in caps_:
                    config = {"phase": "rerun", "category": category, "steps": 500,
                              "model": {"reproduction_rate": rr, "alpha": alpha, "successor_capability": successor},
                              "calibration_path": calibration_path, "tables_path": tables_path}
                    jobs.extend(stable_job("rerun", config, tag, i) for i in range(seeds))
    assert len(jobs) == 24900
    return jobs


def table_jobs(calibration_path=None, tag="v3_tables"):
    from .offline_estimator import settings_for, SENSITIVITY_RULES, SENSITIVITY_RR
    from .policies import execution_policy_class
    jobs = []
    contexts = scoring_contexts()
    for rr in sorted({v[0] for v in contexts}):
        scoring = scoring_for_rr(rr)
        for rule in execution_policy_class():
            names = ["primary"]
            if rule.rule_id in SENSITIVITY_RULES and rr in SENSITIVITY_RR:
                names.extend(("double_population", "double_length"))
            for name in names:
                config = {"phase": "table", "rule_id": rule.rule_id, "kernel": {"reproduction_rate": rr},
                          "settings": settings_for(name), "setting_name": name, "route": "auto", "scoring": scoring}
                if calibration_path:
                    config["calibration_path"] = calibration_path
                jobs.append(stable_job("table", config, tag, 0))
    return jobs


def scoring_for_rr(rr):
    values = {(a, c, 8.) for r, a, c in scoring_contexts() if r == rr}
    if rr in R1_RR:
        values.update((1., c, .75) for c in capabilities(1.5))
    if rr == .064:
        values.update((a, c, .75) for a in R2_ALPHA for initial in R2_CAP for c in capabilities(initial))
    return [{"alpha": a, "capability": c, "kappa": k} for a, c, k in sorted(values)]


def calibration_jobs(tag="v3_calibration"):
    return [stable_job("calibration", {"phase": "calibration", "steps": 500, "n_agents": 200, "reproduction_rate": .08}, tag, i) for i in range(50)]


def table_design():
    from .offline_estimator import PRIMARY, SENSITIVITY_RULES, SENSITIVITY_RR
    from .policies import execution_policy_class
    return {"resolution": "R13, 2026-09-27", "primary": PRIMARY,
            "amendment": "A1 proposed, 2026-09-28; commit and pin required before registered execution",
            "sensitivity_rule_ids": list(SENSITIVITY_RULES), "sensitivity_rr": list(SENSITIVITY_RR),
            "sensitivity_settings": ["double_population", "double_length"],
            "rule_ids": [r.rule_id for r in execution_policy_class()], "rule_class_hash": digest([r.__dict__ for r in execution_policy_class()]),
            "primary_rule_kernels": 325, "sensitivity_rule_kernels": 9, "sensitivity_jobs": 18,
            "plain_route_minimum_surviving_fraction": .5, "WE": "not implemented; not_estimable status",
            "full_scale_tail_standard": "diagnostic only", "scoring_contexts": scoring_contexts()}


def assemble_tables(outputs, calibration, target, *, registered=False, a10_jobs=None, a10_family=None):
    """Apply the frozen nine-pair sensitivity family before table publication."""
    import math
    import numpy as np
    from .production_tables import row_key, write_tables
    from .offline_estimator import SENSITIVITY_RULES, SENSITIVITY_RR
    primary, sensitivities, rates = {}, {}, {}
    current_code = code_identity()
    if a10_jobs is not None:
        expected_jobs = {j["id"]: j for j in a10_jobs}
        if len(outputs) != len(expected_jobs) or {o["job"]["id"] for o in outputs} != set(expected_jobs):
            raise ValueError("incomplete A10 estimation jobs")
        if any(o["job"] != expected_jobs[o["job"]["id"]] for o in outputs):
            raise ValueError("A10 estimation job differs from declared family")
    for output in outputs:
        if output["code_hash"] != current_code or output["result"]["calibration_hash"] != calibration["sha256"]:
            raise ValueError("stale table output or calibration")
        if registered and (output["job"]["tag"] != "v3_tables" or output["result"]["fixture_calibration"]):
            raise ValueError("registered assembly rejects pilot or fixture estimates")
        config = output["job"]["config"]
        if config["setting_name"] not in ("primary", "double_population", "double_length"):
            raise ValueError("unfrozen estimator setting")
        destination = primary if config["setting_name"] == "primary" else sensitivities
        for row in output["result"]["rows"]:
            key = row_key(row)
            if destination is primary:
                if key in primary:
                    raise ValueError("duplicate primary row")
                primary[key] = dict(row)
                rates[key] = config["kernel"]["reproduction_rate"]
            else:
                if config["setting_name"] in destination.get(key, {}):
                    raise ValueError("duplicate sensitivity estimate")
                destination.setdefault(key, {})[config["setting_name"]] = row
    statuses = []
    for key, row in primary.items():
        rr = rates[key]
        row["primary_status"], row["primary_reason"] = row["status"], row.get("reason")
        selected = row["rule_id"] in SENSITIVITY_RULES and rr in SENSITIVITY_RR
        passed = True
        contrasts = []
        if selected:
            others = sensitivities.get(key, {})
            passed = set(others) == {"double_population", "double_length"}
            for name, other in others.items():
                a, b = row.get("lambda_f"), other.get("lambda_f")
                if not a or not b or a["mean"] is None or b["mean"] is None:
                    passed = False
                    contrasts.append({"setting": name, "passed": False, "other_status": other["status"],
                                      "reason": "contrast unavailable", "other_screens": other.get("screens", {})})
                    continue
                av, bv = np.asarray(a["replicates"]), np.asarray(b["replicates"])
                half = 2.015 * math.sqrt(float(av.var(ddof=1) / len(av) + bv.var(ddof=1) / len(bv)))
                difference = b["mean"] - a["mean"]
                ok = abs(difference) + half <= .05 * row["flow_range"]
                eligible = other["status"] == "estimated"
                passed &= ok and eligible
                contrasts.append({"setting": name, "difference": difference, "interval90": [difference - half, difference + half],
                                  "passed": bool(ok and eligible), "numerical_contrast_passed": bool(ok),
                                  "other_status": other["status"], "other_screens": other.get("screens", {}),
                                  "threshold": .05 * row["flow_range"], "excess": abs(difference) + half - .05 * row["flow_range"]})
            statuses.append(bool(passed))
        row["sensitivity"] = {"selected": selected, "passed": bool(passed) if selected else None, "contrasts": contrasts}
        if selected and not passed:
            row["status"] = "not_estimable"
            row["reason"] = "declared sensitivity subset failed or is incomplete"
    manifest = {"tag": "v3_tables" if registered else "pilot", "calibration_hash": calibration["sha256"],
                "design": table_design(), "required_row_keys": sorted(primary),
                "sensitivity_status": "passed" if statuses and all(statuses) else "incomplete_or_failed",
                "complete_family": registered,
                "input_output_hashes": [digest(o) for o in outputs]}
    if a10_jobs is not None:
        from .tables_a10 import provenance, expected_keys
        manifest["a10"] = provenance(a10_family, a10_jobs)
        if set(primary) != expected_keys(a10_jobs, calibration):
            raise ValueError("A10 per-capability scoring family is incomplete")
    if registered and a10_jobs is None:
        from .context import Context
        from .policies import execution_policy_class
        expected = set()
        for rr in {r for r, _, _ in scoring_contexts()}:
            context = Context.build({"reproduction_rate": rr}, calibration)
            for rule in execution_policy_class():
                for scoring in scoring_for_rr(rr):
                    expected.add(row_key({"rule_id": rule.rule_id, "kernel_hash": context.kernel_hash,
                                          "calibration_hash": calibration["sha256"], "initial_population": 200, "scoring": scoring}))
        if set(primary) != expected or len(statuses) != sum(len(scoring_for_rr(rr)) for rr in SENSITIVITY_RR) * len(SENSITIVITY_RULES):
            raise ValueError("full production table family is incomplete")
    return write_tables(target, list(primary.values()), manifest, fixture=not registered)


def registered_spec(kind, registration, calibration_path=None, tables_path=None, publication_path=None):
    """Prepare reviewable full manifests; launch performs the actual pin check."""
    from .pilot import make_spec
    profiles = make_spec()["configuration"]
    if kind == "rerun":
        if not calibration_path or not tables_path:
            raise ValueError("reruns need calibration and table paths")
        jobs = rerun_jobs(calibration_path, tables_path)
        configuration = {"rerun": profiles["rerun"]}
        # Configuration jobs use the same production artifacts and kernel.
        configuration["rerun"]["config"].update(calibration_path=calibration_path, tables_path=tables_path)
        hours, publication = 72, None
    elif kind == "table":
        if not calibration_path or not publication_path:
            raise ValueError("table run needs calibration and publication paths")
        jobs = table_jobs(calibration_path)
        configuration = {"table": profiles["table_fv"]}
        configuration["table"]["config"]["calibration_path"] = calibration_path
        plain = dict(profiles["table_plain"]["config"], calibration_path=calibration_path)
        configuration["table"]["configs"] = [plain, configuration["table"]["config"]]
        hours, publication = 24, {"kind": "tables", "path": publication_path, "calibration_path": calibration_path}
    elif kind == "calibration":
        if not publication_path:
            raise ValueError("calibration needs a publication path")
        jobs = calibration_jobs()
        configuration = {"calibration": profiles["calibration"]}
        hours, publication = 24, {"kind": "calibration", "path": publication_path}
    else:
        raise ValueError("unknown registered workload")
    return {"schema": "v3-registered-1", "registered": True, "tag": "v3_" + kind,
            "registration": registration, "code_hash": code_identity(), "wall_seconds": hours * 3600,
            "cleanup_reserve_seconds": 300, "configuration_seconds": 900,
            "phases": [kind], "configuration": configuration, "jobs": jobs, "publication": publication}


def main():
    import argparse
    from .artifacts import read, seal, atomic_json
    parser = argparse.ArgumentParser(description="Prepare a full registered manifest; does not launch it")
    parser.add_argument("kind", choices=("rerun", "table", "calibration"))
    parser.add_argument("--pin", required=True, help="JSON with commit, path and sha256")
    parser.add_argument("--output", required=True)
    parser.add_argument("--calibration"); parser.add_argument("--tables"); parser.add_argument("--publication")
    args = parser.parse_args()
    spec = registered_spec(args.kind, read(args.pin), args.calibration, args.tables, args.publication)
    atomic_json(args.output, seal(spec))
    print({"jobs": len(spec["jobs"]), "manifest_hash": digest(spec), "launched": False})


if __name__ == "__main__":
    main()
