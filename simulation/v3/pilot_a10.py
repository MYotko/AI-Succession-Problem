"""Non-registered A10 cost pilot. Its durable results contain costs only.

Build with --toy for workstation testing. Production-sized pilot manifests
are prepared here but launched only by the operator through production_runner.
No outcome, population summary, table estimate, or decision is exported.
"""
import argparse
from copy import deepcopy
from pathlib import Path
import statistics
import time
from .artifacts import (atomic_json, code_identity, digest, read, seal, unseal,
                        stable_job, SIMULATION)
from .tables_a10 import build_jobs, paired_runs, arm_runs, a6_runs, FAMILIES
from .budget_a6 import REALISM, RESERVE_SECONDS, PROGRAM_CEILING_HOURS

SAMPLE_TAG = "A10-cost-pilot-2026-10-07"
TOY_SETTINGS = {"groups": 3, "runs_per_group": 2, "particles": 2, "burn": 30, "measure": 8}
POOLED_PHASE = "pooled"


def reduced_pilot(spec):
    return spec.get("schema") == "v3-A10-cost-pilot-1" and spec.get("scope") == "reduced"


def scheduling_estimate(job, memory_gb):
    """Declared A4 planning seconds, used for queue order only, never projection."""
    from .budget_a6 import A4_FIT, A4_VALIDATE_PLAIN, A4_CENSUS, SECONDS_PER_RUN_EQUIVALENT
    c = job["config"]
    source = c["source_job"]["config"]
    kind = c["cost_kind"]
    setting = source.get("setting_name", "run")
    if kind == "run":
        seconds = SECONDS_PER_RUN_EQUIVALENT * source["steps"] / 500
    else:
        s = source["settings"]
        scale = (s["burn"] + s["measure"]) / 3072 * s["particles"] / 256
        # Every validation/label job first builds its own disposable estimate.
        seconds = {"estimate": 1800, "validate_plain": 1800 + A4_FIT + 3*A4_VALIDATE_PLAIN,
                   "validate_fv": 1800 + 3600, "labels": 1800 + 3*A4_VALIDATE_PLAIN}[kind] * scale
        if kind.startswith("validate_"):
            seconds += A4_CENSUS * s["runs_per_group"] / 64
    return {"memory_gb": memory_gb, "estimated_seconds": seconds, "memory_class": kind + "." + setting}


def reduce_spec(spec):
    """Select P2 strata without changing a sampled job, its seed or its length."""
    capabilities = {f: sorted({s["capability"] for s in spec["strata"].values() if s["family"] == f})
                    for f in FAMILIES}
    selected = {f: sorted({c[0], c[(len(c)-1)//2], c[-1]}) for f, c in capabilities.items()}
    medians = {f: c[(len(c)-1)//2] for f, c in capabilities.items()}
    jobs = []
    for job in spec["jobs"]:
        phase = job["config"]["phase"]
        s = spec["strata"][phase]
        keep = s["kind"] == "run" or (s["setting"] == "primary" and s["capability"] in selected[s["family"]])
        keep = keep or (s["family"] == "nominal" and s["setting"] != "primary"
                        and s["capability"] == medians["nominal"] and s["kind"] != "labels")
        s["sampled"] = keep
        if keep:
            jobs.append(job)
        else:
            s["selected_source_ids"] = []
    estimates = {j["id"]: scheduling_estimate(j, spec["memory_estimate_gb"][j["config"]["phase"]]) for j in jobs}
    jobs.sort(key=lambda j: (-estimates[j["id"]]["estimated_seconds"], j["id"]))
    # Interleave kinds in the single short configuration workload. This work is
    # not a sample and never contributes timing to a measured stratum.
    by_kind = {}
    for j in sorted(jobs, key=lambda j: j["config"]["phase"]):
        by_kind.setdefault(j["config"]["cost_kind"], []).append(j)
    mixed = [group[i] for i in range(max(map(len, by_kind.values()))) for group in by_kind.values() if i < len(group)]
    profile = dict(next(iter(spec["configuration"].values())))
    profile["configs"] = [dict(j["config"], configuration_test=True) for j in mixed]
    profile["config"] = profile["configs"][0]
    profile["pooled_estimates_by_stratum"] = {j["config"]["phase"]: estimates[j["id"]] for j in jobs}
    spec.update(scope="reduced", jobs=jobs, phases=[POOLED_PHASE], configuration={POOLED_PHASE: profile},
                wall_seconds=43200, pooled_job_estimates=estimates,
                selection={"capabilities": capabilities, "selected_capabilities": selected, "medians": medians,
                           "rule": "primary: minimum, lower median, maximum; nominal non-primary: lower median; all run categories",
                           "sample_rule": SAMPLE_TAG, "jobs_per_selected_stratum": 1},
                dispatch_policy={"queue": "longest-estimated-first among jobs fitting individual memory reservations",
                                 "worker_ceiling": 16, "memory_headroom": .8,
                                 "planning_seconds": "A4 declared estimation 1800, FV validation 3600, budget_a6 plain/census/run costs; setup included; queue order only"})
    return spec


def hash_sample(jobs, count, phase):
    if count < 1 or not jobs:
        raise ValueError("positive sample from a nonempty phase required")
    return sorted(jobs, key=lambda j: (digest([SAMPLE_TAG, phase, j]), j["id"]))[:count]


def make_spec(paths, *, toy=False, samples=1, toy_capabilities=(1., 1.5), scope="full"):
    """Pin every source job and select smallest hashes within phase/capability.

    Estimation times the actual auto route. Validation times both plain and FV
    routes; projections retain both scenarios rather than guessing a route mix.
    Every setting remains a separate stratum, including the memory-heavy arm.
    """
    if scope not in ("full", "reduced") or (scope == "reduced" and samples != 1):
        raise ValueError("scope must be full or reduced; reduced requires one sample per stratum")
    populations = {}
    for family in FAMILIES:
        cal, _ = paths[family]
        for j in build_jobs(family, cal):
            cap = j["config"]["kernel"]["capability"]
            if toy and scope == "full" and cap not in toy_capabilities:
                continue
            setting = j["config"]["setting_name"]
            for kind in ("estimate", "validate_plain", "validate_fv", "labels"):
                if kind == "labels" and setting != "primary":
                    continue
                phase = f"{family}.{cap}.{setting}.{kind}"
                populations.setdefault(phase, []).append(j)
    nominal_cal, nominal_tables = paths["nominal"]
    runs = paired_runs(nominal_cal, nominal_tables)
    runs += arm_runs(nominal_cal, nominal_tables, paths["sqrt"][1])
    runs += a6_runs(paths)
    for j in runs:
        cfg = j["config"]
        inst = cfg["model"]["instrument"]
        phase = f"runs.{cfg['category']}.{inst['g']}.{inst['k_star']}"
        populations.setdefault(phase, []).append(j)
    jobs, configuration, strata, memory = [], {}, {}, {}
    for phase, population in sorted(populations.items()):
        selected = hash_sample(population, samples, phase)
        strata[phase] = {"population_jobs": len(population), "population_sha256": digest(population),
                        "selected_source_ids": [j["id"] for j in selected], "sample_rule": SAMPLE_TAG,
                        "family": selected[0]["config"].get("a10_family"),
                        "capability": selected[0]["config"].get("kernel", {}).get("capability"),
                        "category": selected[0]["config"].get("category")}
        if scope == "reduced":
            strata[phase].update(population_source_ids=[j["id"] for j in population],
                                 setting=selected[0]["config"].get("setting_name", "run"),
                                 kind="run" if phase.startswith("runs.") else phase.rsplit(".", 1)[1])
        for i, source in enumerate(selected):
            cfg = {"phase": phase, "source_job": source, "toy": toy,
                   "cost_kind": "run" if phase.startswith("runs.") else phase.rsplit(".", 1)[1]}
            jobs.append(stable_job("a10_cost", cfg, "pilot", i))
        if not phase.startswith("runs."):
            from .table_validation_a4 import estimate_memory_gb
            kind = phase.rsplit(".", 1)[1]
            setting = dict(TOY_SETTINGS if toy else selected[0]["config"]["settings"])
            if kind != "estimate" and not toy:
                setting["groups"] = 32
            route = "fv" if kind in ("estimate", "validate_fv") else "plain"
            # Nine feature columns replace eight, plus 31 history doubles per
            # particle. Keep a fixed process-overhead allowance for tiny jobs.
            history_gb = setting["groups"] * setting["particles"] * 31 * 8 / 1e9
            memory[phase] = max(.25, estimate_memory_gb(route, setting) * 9/8 + history_gb)
        else:
            memory[phase] = .25 if toy else 2.
        short = dict(jobs[-1]["config"], configuration_test=True)
        configuration[phase] = {"kind": "a10_cost", "config": short, "workers_local": [2, 4, 8, 12],
                                "workers_x2": [8, 12, 16, 24, 32], "threads": [1], "rounds": 1,
                                "jobs_per_worker": 1, "jobs_local": 12, "jobs_x2": 32}
    spec = {"schema": "v3-A10-cost-pilot-1", "registered": False, "tag": "pilot", "results_eligible": False,
            "code_hash": code_identity(), "toy": toy, "strata": strata, "jobs": jobs,
            "phases": list(strata), "configuration": configuration, "wall_seconds": 10800,
            "configuration_seconds": 900, "cleanup_reserve_seconds": 300,
            "memory_estimate_gb": memory,
            "projection": "phase and capability strata; measured effective workers; realism 1.35; reserves per launch",
            "outcome_policy": "cost-only worker results; no scientific outcome exported"}
    if scope == "reduced":
        spec["source_paths"] = deepcopy(paths)
        return reduce_spec(spec)
    return spec


def execute_cost(job):
    """Execute real functions, retaining only time and workload identity."""
    from .calibration import load_calibration
    c = job["config"]
    if job["tag"] not in ("pilot", "configuration", "validation"):
        raise ValueError("cost pilot is never registered")
    source = deepcopy(c["source_job"])
    config = source["config"]
    toy, short, kind = c["toy"], c.get("configuration_test", False), c["cost_kind"]
    started = time.perf_counter()
    extra = {}
    if kind == "run":
        from .recording import RecordedV3Model
        model_args = dict(config["model"])
        model_args.pop("registered_a10", None)
        if toy:
            model_args.update(n_agents=8, carrying_capacity=80)
        calibration = load_calibration(SIMULATION / config["calibration_path"], instrument=model_args.get("instrument"))
        model = RecordedV3Model(seed=job["seed"], calibration=calibration, **model_args)
        steps = 2 if toy else (5 if short else config["steps"])
        for _ in range(steps):
            model.step()
        units = steps / config["steps"]
    else:
        from .offline_estimator import estimate
        from . import table_validation_a4 as a4
        from . import table_labels_a5 as a5
        from .context import Context
        from .production_tables import row_key
        from .continuation_validation import fine_codes
        from .continuation_validation import fit_seed, validate_seed, census_seed
        calibration = load_calibration(SIMULATION / config["calibration_path"], instrument=config["kernel"].get("instrument"))
        original_settings = dict(config["settings"])
        if toy:
            config["settings"] = dict(TOY_SETTINGS)
            config["kernel"].update(n_agents=16, carrying_capacity=160)
        elif short:
            config["settings"].update(burn=30, measure=8)
        override = dict(config["settings"]) if toy or short else None
        units = ((config["settings"]["burn"] + config["settings"]["measure"])
                 / (original_settings["burn"] + original_settings["measure"]))
        if kind != "estimate":
            config["route"] = "plain" if kind == "validate_plain" else "fv"
        result = estimate(config, job["seed"], calibration)
        if kind == "estimate":
            extra = {"trajectory_seconds": result["trajectory_seconds"],
                     "scoring_seconds_by_k_star": result["scoring_seconds_by_k_star"]}
        else:
            envelope = {"job": source, "result": result, "code_hash": code_identity()}
            # Setup creates disposable cost fixtures. It is not charged twice.
            setup_seconds = time.perf_counter() - started
            started = time.perf_counter()
            if kind == "validate_plain":
                fit = a4.fit_stage(envelope, fit_seed(job["seed"]), override)
                for r in (1, 2, 3):
                    a4.validate_stage(envelope, fit, r, validate_seed(job["seed"], r), override)
                a4.census_stage(envelope, census_seed(job["seed"]),
                                {**(override or {}), **({"census_measure": 38} if toy or short else {})})
            elif kind == "validate_fv":
                a4.validate_stage(envelope, None, 1, validate_seed(job["seed"], 1), override)
                a4.census_stage(envelope, census_seed(job["seed"]),
                                {**(override or {}), **({"census_measure": 38} if toy or short else {})})
            elif kind == "labels":
                ctx = Context.build(config["kernel"], calibration)
                tested = [{"row_key": row_key(r), "scoring": r["scoring"],
                           "support": [(int(fine_codes([e["bin"]])[0]), e["value"])
                                       for e in (r.get("continuation") or {}).get("entries", [])]}
                          for r in result["rows"]]
                for r in (1, 2, 3):
                    a5.fvplain_stage(envelope, tested, ctx.parameters.extinction_flow, ctx.parameters.upper_bound,
                                     a5.fvplain_seed(job["seed"], r), override)
            else:
                raise ValueError("unknown pilot phase")
            extra["unprojected_setup_seconds"] = setup_seconds
    return {"non_registered": True, "results_eligible": False, "cost_only": True,
            "source_job_id": c["source_job"]["id"], "source_job_sha256": digest(c["source_job"]),
            "executed_seed": job["seed"], "seed_namespace": job["tag"],
            "toy": toy, "configuration_test": short, "cost_kind": kind,
            "seconds": time.perf_counter() - started, "length_fraction": units, **extra}


def project(spec, root, configurations, selections, *, relative_to_x2=None):
    """Only completed cost envelopes enter projection; toy data cannot set ceilings."""
    if reduced_pilot(spec):
        return project_reduced(spec, root, configurations, selections, relative_to_x2=relative_to_x2)
    from .production_runner import completed
    root = Path(root)
    if spec["code_hash"] != code_identity():
        raise ValueError("pilot source identity changed")
    rows = {}
    for job in spec["jobs"]:
        output = completed(root / job["config"]["phase"], job, spec["code_hash"])
        if output is None:
            raise ValueError("pilot projection requires every sampled job")
        if not output["result"].get("cost_only"):
            raise ValueError("pilot projection refuses outcome records")
        rows.setdefault(job["config"]["phase"], []).append(output)
    actual_x2 = all(o["runtime"]["machine"].lower() == "yotko-evo-x2" for v in rows.values() for o in v)
    can_project = not spec["toy"] and (actual_x2 or relative_to_x2 is not None)
    relative = 1. if actual_x2 else relative_to_x2
    if relative is not None and (relative <= 0 or not __import__("math").isfinite(relative)):
        raise ValueError("a measured positive relative throughput is required")
    details = {}
    for phase, outputs in rows.items():
        selected = selections[phase]
        matched = [r for r in configurations[phase] if r["valid"] and
                   (r["workers"], r["threads"]) == (selected["workers"], selected["threads"])]
        if not matched:
            raise ValueError("missing selected configuration measurements")
        effective = min(selected["workers"], sum(sum(r["job_seconds"]) for r in matched) / sum(r["wall_seconds"] for r in matched))
        if effective <= 0:
            raise ValueError("zero measured throughput")
        seconds = [o["result"]["seconds"] / o["result"]["length_fraction"] for o in outputs]
        count = spec["strata"][phase]["population_jobs"]
        details[phase] = {"jobs": count, "sampled_jobs": len(outputs), "effective_workers": effective,
                          "mean_worker_seconds": statistics.mean(seconds), "max_worker_seconds": max(seconds),
                          "x2_hours_mean": statistics.mean(seconds) * count / effective / 3600 * REALISM * relative if can_project else None,
                          "x2_hours_max": max(seconds) * count / effective / 3600 * REALISM * relative if can_project else None}
        if phase.endswith(".estimate"):
            for arm in ("1.5", "1.8", "2.3"):
                costs = [o["result"]["scoring_seconds_by_k_star"].get(arm, 0.) / o["result"]["length_fraction"] for o in outputs]
                details[phase]["scoring_" + arm + "_x2_hours"] = max(costs) * count / effective / 3600 * REALISM * relative if can_project else None
    # Both route scenarios are retained. Their maximum bounds the unknown mix;
    # they are not added as if every family ran both validation routes.
    grouped, family_of = {}, {}
    for phase, d in details.items():
        base = phase.rsplit(".", 1)[0] if not phase.startswith("runs.") else phase
        grouped.setdefault(base, {})[phase.rsplit(".", 1)[-1]] = d["x2_hours_max"]
        family_of[base] = spec["strata"][phase].get("family")
    workload, components = 0., {}
    if can_project:
        for base, d in grouped.items():
            value = (sum(d.values()) if base.startswith("runs.") else
                     d["estimate"] + max(d["validate_plain"], d["validate_fv"] + d.get("labels", 0.)))
            component = base if base.startswith("runs.") else family_of[base] + ".tables"
            components[component] = components.get(component, 0.) + value
            workload += value
    reserves = (len(FAMILIES) * (RESERVE_SECONDS["estimation"] + RESERVE_SECONDS["validation"] + 3000)
                + len({p for p in details if p.startswith("runs.")}) * RESERVE_SECONDS["runs"]) / 3600
    a6_components = {k: v for k, v in components.items() if k.startswith("runs.a6_") or
                     k in ("crowding.tables", "sigma_squared_x10.tables", "sigma_squared_x0.1.tables")}
    a6_reserves = (3 * (RESERVE_SECONDS["estimation"] + RESERVE_SECONDS["validation"] + 3000)
                   + len([k for k in a6_components if k.startswith("runs.")]) * RESERVE_SECONDS["runs"]) / 3600
    a6_total = sum(a6_components.values()) + a6_reserves if can_project else None
    return {"schema": "v3-A10-cost-projection-1", "non_registered": True, "results_eligible": False,
            "status": "toy_execution_only" if spec["toy"] else "X2_projection" if can_project else "local_costs_only",
            "actual_x2": actual_x2, "relative_to_x2": relative, "realism": REALISM, "per_phase_capability": details,
            "launch_reserves_x2_hours": reserves, "total_x2_hours_conservative": workload + reserves if can_project else None,
            "a6_ceiling_x2_hours": PROGRAM_CEILING_HOURS,
            "components_x2_hours_before_reserves": components,
            "a6_x2_hours_conservative": a6_total,
            "a6_within_ceiling": a6_total <= PROGRAM_CEILING_HOURS if a6_total is not None else None,
            "k_star_scoring_accounting": "per-arm estimates are subsets of nominal estimation, counted once in totals",
            "limits": ["fixture continuation tables measure run cost only", "route maxima are scenarios, not guarantees",
                       "short configuration work is excluded from samples", "toy timings cannot set registered ceilings"]}


def fill_reduced_costs(strata, measured, nominal_median):
    """Complete declared strata using only the two approved cost rules."""
    result = {p: {**v, "cost_source": "measured", "source_strata": [p], "sampled_jobs": 1}
              for p, v in measured.items()}
    index = {(s["family"], s["kind"], s["setting"], s["capability"]): p for p, s in strata.items()
             if s["kind"] != "run"}
    for phase, s in strata.items():
        if phase in result or s["setting"] != "primary":
            continue
        neighbors = sorted((a["capability"], p) for p, a in strata.items() if p in measured
                           and (a["family"], a["kind"], a["setting"]) == (s["family"], s["kind"], "primary"))
        lower = [(c, p) for c, p in neighbors if c < s["capability"]]
        upper = [(c, p) for c, p in neighbors if c > s["capability"]]
        if not lower or not upper:
            raise ValueError("missing bracketing capability samples: " + phase)
        a, lo = lower[-1]
        b, hi = upper[0]
        fraction = (s["capability"] - a) / (b - a)
        result[phase] = {k: measured[lo][k] + fraction * (measured[hi][k] - measured[lo][k]) for k in measured[lo]}
        result[phase].update(cost_source="interpolated", source_strata=[lo, hi], sampled_jobs=0,
                             interpolation_fraction=fraction)
    for phase, s in strata.items():
        if phase in result:
            continue
        if s["kind"] == "run":
            raise ValueError("missing run-category sample: " + phase)
        primary = index[(s["family"], s["kind"], "primary", s["capability"])]
        numerator = index[("nominal", s["kind"], s["setting"], nominal_median)]
        denominator = index[("nominal", s["kind"], "primary", nominal_median)]
        ratios = {}
        for key, value in measured[numerator].items():
            base = measured[denominator][key]
            if base <= 0 and value != 0:
                raise ValueError("positive nominal primary cost required for a setting ratio")
            ratios[key] = value / base if base else 0.
        result[phase] = {k: result[primary][k] * ratio for k, ratio in ratios.items()}
        result[phase].update(cost_source="scaled", source_strata=[primary, numerator, denominator],
                             primary_cost_source=result[primary]["cost_source"], setting_ratios=ratios, sampled_jobs=0)
    return result


def project_reduced(spec, root, configurations, selections, *, relative_to_x2=None):
    """P2 projection: measurements, capability interpolation, then setting ratios."""
    import math
    from .production_runner import completed
    if spec["code_hash"] != code_identity():
        raise ValueError("pilot source identity changed")
    root = Path(root)
    outputs, measured = {}, {}
    for job in spec["jobs"]:
        output = completed(root / POOLED_PHASE, job, spec["code_hash"])
        if output is None:
            raise ValueError("pilot projection requires every sampled job; incomplete jobs are not counted")
        r = output["result"]
        if not r.get("cost_only") or r.get("configuration_test"):
            raise ValueError("pilot projection requires sample costs only")
        if not spec["toy"] and r["length_fraction"] != 1.:
            raise ValueError("P2 samples must run at full declared length")
        phase = job["config"]["phase"]
        outputs[phase] = output
        seconds = r["seconds"] / r["length_fraction"]
        if not math.isfinite(seconds) or seconds <= 0:
            raise ValueError("positive finite measured costs required")
        measured[phase] = {"mean_worker_seconds": seconds, "max_worker_seconds": seconds}
        if job["config"]["cost_kind"] == "estimate":
            measured[phase].update({"scoring_" + k + "_worker_seconds": r["scoring_seconds_by_k_star"].get(k, 0.) / r["length_fraction"]
                                   for k in ("1.5", "1.8", "2.3")})
    details = fill_reduced_costs(spec["strata"], measured, spec["selection"]["medians"]["nominal"])
    selected = selections[POOLED_PHASE]
    matched = [r for r in configurations[POOLED_PHASE] if r["valid"] and
               (r["workers"], r["threads"]) == (selected["workers"], selected["threads"])]
    if not matched:
        raise ValueError("missing selected configuration measurements")
    effective = min(16, selected["workers"], sum(sum(r["job_seconds"]) for r in matched) / sum(r["wall_seconds"] for r in matched))
    if not math.isfinite(effective) or effective <= 0:
        raise ValueError("zero measured throughput")
    memory_budget = min(r["memory_budget_gb"] for r in matched)
    memory_peaks = {}
    for r in matched:
        for key, value in r.get("memory_estimates_gb", {}).items():
            memory_peaks[key] = max(memory_peaks.get(key, 0.), value)
    for phase, output in outputs.items():
        s = spec["strata"][phase]
        key = s["kind"] + "." + s["setting"]
        memory_peaks[key] = max(memory_peaks.get(key, 0.), (output.get("peak_rss_bytes") or 0.) / 1e9)
    actual_x2 = all(o["runtime"]["machine"].lower() == "yotko-evo-x2" for o in outputs.values())
    relative = 1. if actual_x2 else relative_to_x2
    if relative is not None and (not math.isfinite(relative) or relative <= 0):
        raise ValueError("a measured positive relative throughput is required")
    can_project = not spec["toy"] and relative is not None
    for phase, d in details.items():
        s = spec["strata"][phase]
        memory = max(spec["memory_estimate_gb"][phase], memory_peaks.get(s["kind"] + "." + s["setting"], 0.))
        workers = min(effective, max(1, int(memory_budget / memory)))
        count = s["population_jobs"]
        factor = count / workers / 3600 * REALISM * relative if can_project else None
        d.update(jobs=count, effective_workers=workers, memory_estimate_gb=memory,
                 x2_hours_mean=d["mean_worker_seconds"] * factor if can_project else None,
                 x2_hours_max=d["max_worker_seconds"] * factor if can_project else None)
        if s["kind"] == "estimate":
            for arm in ("1.5", "1.8", "2.3"):
                d["scoring_" + arm + "_x2_hours"] = d["scoring_" + arm + "_worker_seconds"] * factor if can_project else None
    run_families = {}
    for job in spec["jobs"]:
        if job["config"]["cost_kind"] != "run":
            continue
        source = job["config"]["source_job"]["config"]
        family = next((f for f in FAMILIES if source["category"] == "a6_" + f),
                      "sqrt" if source["model"]["instrument"]["g"] == "sqrt" else "nominal")
        run_families[job["config"]["phase"]] = family

    def components(include_estimated):
        groups, totals = {}, {}
        for phase, d in details.items():
            s = spec["strata"][phase]
            value = d["x2_hours_max"] if include_estimated or d["cost_source"] == "measured" else 0.
            if s["kind"] == "run":
                totals[phase] = value
            else:
                key = (s["family"], s["capability"], s["setting"])
                groups.setdefault(key, {})[s["kind"]] = value
        for (family, _, _), costs in groups.items():
            key = family + ".tables"
            totals[key] = totals.get(key, 0.) + costs["estimate"] + max(costs["validate_plain"], costs["validate_fv"] + costs.get("labels", 0.))
        return totals

    all_components = components(True) if can_project else {}
    measured_components = components(False) if can_project else {}
    family_reserve = (RESERVE_SECONDS["estimation"] + RESERVE_SECONDS["validation"] + 3000) / 3600
    run_reserve = RESERVE_SECONDS["runs"] / 3600
    reserves = len(FAMILIES) * family_reserve + len(run_families) * run_reserve
    families = {}
    for family in FAMILIES:
        keys = [family + ".tables"] + [p for p, f in run_families.items() if f == family]
        reserve = family_reserve + (len(keys)-1) * run_reserve
        full = sum(all_components.get(k, 0.) for k in keys) if can_project else None
        measured_only = sum(measured_components.get(k, 0.) for k in keys) if can_project else None
        families[family] = {"components": keys, "launch_reserves_x2_hours": reserve,
                            "with_estimated_parts_x2_hours": full + reserve if can_project else None,
                            "without_estimated_parts_x2_hours": measured_only + reserve if can_project else None,
                            "estimated_parts_x2_hours": full - measured_only if can_project else None,
                            "tables_with_estimated_parts_x2_hours_before_reserves": all_components.get(family + ".tables")}
    a6_keys = [k for k in all_components if k.startswith("runs.a6_") or k in
               ("crowding.tables", "sigma_squared_x10.tables", "sigma_squared_x0.1.tables")]
    a6_reserve = 3*family_reserve + sum(k.startswith("runs.") for k in a6_keys)*run_reserve
    a6 = sum(all_components[k] for k in a6_keys) + a6_reserve if can_project else None
    full = sum(all_components.values()) + reserves if can_project else None
    measured_only = sum(measured_components.values()) + reserves if can_project else None
    return {"schema": "v3-A10-cost-projection-2", "scope": "reduced", "non_registered": True, "results_eligible": False,
            "status": "toy_execution_only" if spec["toy"] else "X2_projection" if can_project else "local_costs_only",
            "actual_x2": actual_x2, "relative_to_x2": relative, "realism": REALISM,
            "per_phase_capability": details, "pooled_effective_workers": effective, "memory_budget_gb": memory_budget,
            "launch_reserves_x2_hours": reserves, "total_x2_hours_conservative": full,
            "total_without_estimated_parts_x2_hours": measured_only,
            "estimated_parts_x2_hours": full - measured_only if can_project else None,
            "per_family": families, "components_x2_hours_before_reserves": all_components,
            "components_without_estimated_parts_x2_hours_before_reserves": measured_components,
            "a6_ceiling_x2_hours": PROGRAM_CEILING_HOURS, "a6_x2_hours_conservative": a6,
            "a6_within_ceiling": a6 <= PROGRAM_CEILING_HOURS if can_project else None,
            "k_star_scoring_accounting": "per-arm estimates are subsets of nominal estimation, counted once in totals",
            "limits": ["fixture continuation tables measure run cost only", "route maxima are scenarios, not guarantees",
                       "without-estimated totals retain all launch reserves", "toy timings cannot set registered ceilings",
                       "unprojected fixture setup consumes pilot wall time but is not charged twice to study costs"]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("build", "project"))
    p.add_argument("--output", required=True)
    p.add_argument("--paths")
    p.add_argument("--spec")
    p.add_argument("--root")
    p.add_argument("--toy", action="store_true")
    p.add_argument("--scope", choices=("full", "reduced"), default="full")
    p.add_argument("--relative-to-x2", type=float)
    args = p.parse_args()
    if args.command == "build":
        value = make_spec(read(args.paths), toy=args.toy, scope=args.scope)
    else:
        spec = unseal(read(args.spec))
        launch = read(Path(args.root) / "launches.json")[-1]
        value = project(spec, args.root, launch["configuration"],
                        {k: v["selection"] for k, v in launch["outcomes"].items()}, relative_to_x2=args.relative_to_x2)
    atomic_json(args.output, seal(value))
    print({"non_registered": True, "artifact": args.output})


if __name__ == "__main__":
    main()
