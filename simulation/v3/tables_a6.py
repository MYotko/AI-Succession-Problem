"""A6 variant table families: the crowding and sigma0^2 families.

Amendment A6, 2026-09-29. Each variant arm needs its own table family, because
the tables' kernel identity includes the crowding variant and the novelty
protocol (which holds sigma0^2). This module builds each family's table jobs
with the committed table-job settings and exactly its arm's kappa = 8 scoring
contexts, assembles them A1-style with completeness checked against the family's
own contexts, and drives amendment A4 in full through wrappers that reuse
``table_validation_a4``'s stage functions and job kinds with the family's own M,
M_FV and source pin in place of A4's hard-coded A1 hash.

New module only. It imports the frozen estimation, assembly and validation code
and adds nothing to those files. It computes no survival, extinction or fire rate.
"""
import math
from pathlib import Path

import numpy as np

from .artifacts import (SIMULATION, atomic_json, code_identity, digest, read, seal, stable_job)
from .offline_estimator import SENSITIVITY_RULES, SENSITIVITY_RR, settings_for
from .policies import execution_policy_class
from .study import R1_RR, R2_ALPHA, R2_CAP, capabilities, table_design

# The families and their rr grids.
CROWDING_RR = R1_RR                                   # R1's 9 rr
SIGMA_RR = (0.059, 0.060, 0.062, 0.064, 0.066)        # the five narrowed rr (A6 section 2)
SIGMA_VARIANTS = ("sigma_squared_x10", "sigma_squared_x0.1")

COUNT_CROWDING_JOBS = 237
COUNT_SIGMA_JOBS = 131


def family_rrs(family):
    return CROWDING_RR if family == "crowding" else SIGMA_RR


def family_kernel(family, rr):
    """The kernel dict for one rr. The crowding family sets crowding
    'reproductive'; the sigma0^2 families keep the default kernel but carry their
    variant calibration (which holds sigma0^2), so the kernel identity differs
    through the novelty protocol."""
    if family == "crowding":
        return {"reproduction_rate": rr, "crowding": "reproductive"}
    return {"reproduction_rate": rr}


def family_scoring(family, rr):
    """Exactly the arm's cells at kappa = 8. R1 uses alpha 1.0 x capabilities from
    1.5; the crowding arm also has R2's alpha x capability contexts at rr 0.064.
    It does not use the committed scoring_for_rr, which would add kappa = 0.75
    rows and R1's other alphas that no arm looks up."""
    values = {(1.0, c, 8.0) for c in capabilities(1.5)}
    if family == "crowding" and rr == 0.064:
        for a in R2_ALPHA:
            for successor in R2_CAP:
                for c in capabilities(successor):
                    values.add((a, c, 8.0))
    return [{"alpha": a, "capability": c, "kappa": k} for a, c, k in sorted(values)]


# ---------------------------------------------------------------------------
# Table jobs
# ---------------------------------------------------------------------------

def build_jobs(family, calibration_path, settings_override=None, tag="v3_tables", rrs=None, rule_ids=None):
    """The family's table jobs: primary for every (rr, rule), plus the frozen
    sensitivity subset (double_population and double_length) for the sensitivity
    rules at the sensitivity rr in the family's grid. Mirrors study.table_jobs.
    Asserts the full count (237 crowding, 131 sigma) unless a tiny synthetic
    subset (``rrs``/``rule_ids``) or a settings override is given."""
    grid = family_rrs(family) if rrs is None else tuple(rrs)
    rules = [r for r in execution_policy_class() if rule_ids is None or r.rule_id in rule_ids]
    jobs = []
    for rr in grid:
        scoring = family_scoring(family, rr)
        for rule in rules:
            names = ["primary"]
            if rule.rule_id in SENSITIVITY_RULES and rr in SENSITIVITY_RR:
                names.extend(("double_population", "double_length"))
            for name in names:
                base = dict(settings_for(name))
                if settings_override:
                    base.update(settings_override)
                config = {"phase": "table", "rule_id": rule.rule_id, "kernel": family_kernel(family, rr),
                          "settings": base, "setting_name": name, "route": "auto", "scoring": scoring,
                          "calibration_path": calibration_path, "a6_family": family}
                jobs.append(stable_job("table", config, tag, 0))
    expected = COUNT_CROWDING_JOBS if family == "crowding" else COUNT_SIGMA_JOBS
    if settings_override is None and rrs is None and rule_ids is None:
        assert len(jobs) == expected, (family, len(jobs), expected)
    if len({j["id"] for j in jobs}) != len(jobs):
        raise ValueError("duplicate variant table job id")
    return jobs


# ---------------------------------------------------------------------------
# Assembly (A1-style, mirroring study.assemble_tables with own-context completeness)
# ---------------------------------------------------------------------------

def assemble(outputs, calibration, target, family, *, registered=False):
    """Apply the frozen sensitivity family and write the A1-equivalent variant
    family. Mirrors study.assemble_tables, but the registered completeness check
    uses the family's own contexts and kernels, not the nominal scoring_for_rr."""
    from .production_tables import row_key, write_tables
    from .context import Context
    primary, sensitivities, rates = {}, {}, {}
    current_code = code_identity()
    for output in outputs:
        if output["code_hash"] != current_code or output["result"]["calibration_hash"] != calibration["sha256"]:
            raise ValueError("stale table output or calibration")
        if registered and (output["job"]["tag"] != "v3_tables" or output["result"]["fixture_calibration"]):
            raise ValueError("registered assembly rejects pilot or fixture estimates")
        config = output["job"]["config"]
        if config["setting_name"] not in ("primary", "double_population", "double_length"):
            raise ValueError("unfrozen estimator setting")
        # The estimation must have used the committed settings; reject any override.
        if registered and config.get("settings") != settings_for(config["setting_name"]):
            raise ValueError("registered assembly rejects a table job whose settings differ from settings_for")
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
                "design": dict(table_design(), a6_family=family), "required_row_keys": sorted(primary),
                "sensitivity_status": "passed" if statuses and all(statuses) else "incomplete_or_failed",
                "complete_family": registered, "a6_family": family,
                "input_output_hashes": [digest(o) for o in outputs]}
    if registered:
        expected = set()
        sens_rr = [rr for rr in family_rrs(family) if rr in SENSITIVITY_RR]
        for rr in family_rrs(family):
            context = Context.build(family_kernel(family, rr), calibration)
            for rule in execution_policy_class():
                for scoring in family_scoring(family, rr):
                    expected.add(row_key({"rule_id": rule.rule_id, "kernel_hash": context.kernel_hash,
                                          "calibration_hash": calibration["sha256"], "initial_population": 200, "scoring": scoring}))
        if set(primary) != expected or len(statuses) != sum(len(family_scoring(family, rr)) for rr in sens_rr) * len(SENSITIVITY_RULES):
            raise ValueError("variant table family is incomplete against its own contexts")
    return write_tables(target, list(primary.values()), manifest, fixture=not registered)


# ---------------------------------------------------------------------------
# Estimation spec (also the A4 source manifest, tables_A1_manifest.json)
# ---------------------------------------------------------------------------

def estimation_spec(family, calibration_path, registration, *, settings_override=None,
                    ledger=None, rerun_commit=None, repo=None, a1_source_root=None, probe_root=None,
                    rerun_manifest=None, seed_registry=None, machine="x2", tag="v3_tables"):
    """A registered spec that runs the family's table jobs, in study.registered_spec's
    shape so the unchanged production runner accepts it. publication is None: the
    runner's built-in table publication is hard-coded to the nominal completeness,
    so A6 assembles the family separately with assemble(). The registered wall
    ceiling is the budget's slack-aware ceiling for this component on ``machine``,
    never A4's 48-hour default. A registered spec requires the rerun commit, the A1
    source root, a probe root yielding non-empty probe seeds, the rerun manifest and
    the seed registry, and rejects any settings override."""
    from .pilot import make_spec
    from . import budget_a6
    jobs = build_jobs(family, calibration_path, settings_override)
    component = family + "_tables_estimation"
    if registration is not None:
        if settings_override:
            raise ValueError("a registered A6 estimation spec rejects a settings override")
        if rerun_commit is None:
            raise ValueError("a registered A6 estimation spec requires the rerun commit for invariance")
        _require_seed_inputs(a1_source_root, probe_root, rerun_manifest, seed_registry)
        from .sensitivity_a6 import assert_rerun_path_invariant, assert_registry_seeds
        assert_rerun_path_invariant(rerun_commit, repo)
        # The global seed check, before the first A6 simulation: the variant
        # table job seeds against the full forbidden set and every other new seed.
        global_seed_check({family + "_table_jobs": [j["seed"] for j in jobs]},
                          a1_source_root=a1_source_root, probe_root=probe_root, rerun_manifest=rerun_manifest)
        assert_registry_seeds(seed_registry, "table_jobs", family, [j["seed"] for j in jobs])
    ledger = ledger or budget_a6.build_ledger()
    wall_share_hours = (budget_a6.planning_estimate_hours(component) if registration is None
                        else budget_a6.runner_ceiling_hours(ledger, component, machine))
    profiles = make_spec()["configuration"]
    configuration = {"table": _a6_profile(profiles["table_fv"])}
    kernel = family_kernel(family, 0.064)
    configuration["table"]["config"].update(calibration_path=calibration_path, kernel=kernel)
    plain = dict(profiles["table_plain"]["config"], calibration_path=calibration_path, kernel=kernel)
    configuration["table"]["configs"] = [plain, configuration["table"]["config"]]
    import math
    return {"schema": "v3-registered-1", "registered": True, "tag": "v3_tables",
            "registration": registration, "code_hash": code_identity(),
            "wall_seconds": int(math.floor(wall_share_hours * 3600)), "cleanup_reserve_seconds": 300,
            "configuration_seconds": 900, "phases": ["table"], "configuration": configuration,
            "jobs": jobs, "publication": None, "a6_family": family,
            "a6_program_ceiling_hours": budget_a6.PROGRAM_CEILING_HOURS, "a6_wall_share_hours": wall_share_hours}


# A6's own configuration-profile worker candidates: the unchanged runner tests
# only the worker counts a profile lists, and the local cap is min(12, budget-1).
A6_WORKERS_LOCAL = [8, 12]
A6_WORKERS_X2 = [8, 12, 16, 24, 32]


def _a6_profile(profile):
    """Set A6's worker candidates on a configuration profile, keeping its shape.
    ``jobs_per_worker`` = 2 makes the runner's configuration test occupy every
    tested worker (two waves) at 8 and 12, so the occupancy check passes on the
    WSL workstation as well as the X2 (production_runner.py:557-559)."""
    profile = dict(profile)
    profile["workers_local"] = list(A6_WORKERS_LOCAL)
    profile["workers_x2"] = list(A6_WORKERS_X2)
    profile["jobs_per_worker"] = 2
    return profile


def _require_seed_inputs(a1_source_root, probe_root, rerun_manifest, seed_registry):
    """A registered A6 step requires the A1 source root, a probe root that yields a
    non-empty set of probe seeds (not merely a non-empty path), the sealed rerun
    manifest and the seed registry; there is no fallback."""
    from .table_validation_a4 import load_probe_seeds
    if not a1_source_root or rerun_manifest is None:
        raise ValueError("a registered A6 step requires the A1 source root and the sealed rerun manifest; no fallback")
    if seed_registry is None:
        raise ValueError("a registered A6 step requires the sealed A6 seed registry")
    if not probe_root or not load_probe_seeds(probe_root):
        raise ValueError("a registered A6 step requires a probe root yielding a non-empty set of D26 probe seeds")


def global_seed_check(new_groups, *, a1_source_root, probe_root, rerun_manifest):
    """Build the full forbidden set and assert every new A6 seed in ``new_groups``
    is disjoint from it and from every other new seed. Called before the first A6
    simulation and at every later step (variant estimation, validation, runs)."""
    from .sensitivity_a6 import forbidden_seeds, assert_global_seed_distinctness
    if not a1_source_root or rerun_manifest is None:
        raise ValueError("the global A6 seed check needs the A1 source root and the sealed rerun manifest")
    forbidden = forbidden_seeds(a1_source_root, probe_root, rerun_manifest=rerun_manifest, registered=True)
    return assert_global_seed_distinctness(new_groups, forbidden)


# ---------------------------------------------------------------------------
# A4 validation wrappers
# ---------------------------------------------------------------------------

def prepare_validation(source_root, calibration_path, *, family=None, registration=None, ledger=None,
                       rerun_commit=None, repo=None, a3_probe_root=None, settings_override=None,
                       a1_source_root=None, rerun_manifest=None, seed_registry=None, machine="x2"):
    """Prepare an A4-style validation plan for a variant family.

    It pins the family's own assembled-tables file hash (its source pin) in place
    of A4's hard-coded A1 hash, counts the family's own M and M_FV from its own
    outputs, and binds the A6 code registration into ``plan_hash`` with the jobs
    rebuilt under that hash, so publish verifies both the source pin and the
    registration. A registered plan (``registration`` given) rejects any settings
    override, takes its wall ceiling from the ledger share (never A4's 48-hour
    default), and asserts rerun-path invariance when a rerun commit is given.
    Mirrors table_validation_a4.prepare, reusing its stage helpers.
    """
    from . import table_validation_a4 as a4
    from . import budget_a6
    from . import continuation_validation as cv
    from .artifacts import file_hash, unseal
    source_root = Path(source_root)
    if registration is not None:
        if not family:
            raise ValueError("a registered A6 validation plan requires its family; no default")
        if settings_override:
            raise ValueError("a registered A6 validation plan rejects a settings override")
        if rerun_commit is None:
            raise ValueError("a registered A6 validation plan requires the rerun commit for invariance")
        _require_seed_inputs(a1_source_root, a3_probe_root, rerun_manifest, seed_registry)
        from .sensitivity_a6 import assert_rerun_path_invariant
        assert_rerun_path_invariant(rerun_commit, repo)
    ledger = ledger or budget_a6.build_ledger()
    # The registered validation ceiling is the budget's slack-aware ceiling on the
    # machine; no path uses A4's 48-hour default. A fixture (smoke) plan takes a
    # positive nominal ceiling.
    if registration is None:
        wall_hours = budget_a6.planning_estimate_hours(family + "_tables_validation") if family else 1.0
    else:
        wall_hours = budget_a6.runner_ceiling_hours(ledger, family + "_tables_validation", machine)
    # The family's own source pin, always (never A4's hard-coded A1 hash).
    source_file_sha256 = file_hash(source_root / "v3_rerun_tables_A1.json")
    manifest = unseal(read(source_root / "tables_A1_manifest.json"))
    source_code = a4._source_code_hash(source_root)
    counts = a4.counts_from_job_outputs(source_root, source_code)
    probe_seeds = a4.load_probe_seeds(a3_probe_root) if a3_probe_root else set()
    if not probe_seeds:
        raise ValueError("A6 validation prepare requires a non-empty D26 probe root")
    a1_seeds = {j["seed"] for j in manifest["jobs"]}
    all_stream, forbidden = {}, set(a1_seeds) | set(probe_seeds)
    skeletons, phase_estimates = [], {p: 0.0 for p in a4.PHASES}
    for job in manifest["jobs"]:
        a1 = a4._load_a1(source_root, job, source_code)
        route = a1["result"]["route"]
        settings = a4._a1_settings(a1)
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
            phase_estimates["fit"] = max(phase_estimates["fit"], a4.estimate_memory_gb("plain", settings))
            phase_estimates["validate_plain"] = max(phase_estimates["validate_plain"], a4.estimate_memory_gb("plain", settings))
        else:
            phase = a4.fv_phase(job["config"].get("setting_name", "primary"))
            skeletons.append(({**base, "stage": "validate", "route": "fv", "replicate": cv.FV_VALIDATE_REPLICATE,
                               "seed": cv.validate_seed(job["seed"], cv.FV_VALIDATE_REPLICATE)}, phase))
            phase_estimates[phase] = max(phase_estimates[phase], a4.estimate_memory_gb("fv", settings))
        census_settings = {**settings, "burn": 0, "measure": a4.CENSUS_MEASURE, "groups": a1["result"]["settings"]["groups"]}
        skeletons.append(({**base, "stage": "census", "route": "plain", "seed": cv.census_seed(job["seed"])}, "census"))
        phase_estimates["census"] = max(phase_estimates["census"], a4.estimate_memory_gb("plain", census_settings))
    plan_core = {"schema": "v3-A4-validation-1", "amendment": a4.AMENDMENT, "registered": bool(registration),
                 "tag": "v3_tables", "code_hash": code_identity(), "source_root": str(source_root.resolve()),
                 "source_file_sha256": source_file_sha256, "source_manifest_sha256": digest(manifest),
                 "source_code_hash": source_code, "calibration_path": calibration_path,
                 "wall_seconds": __import__("math").floor(wall_hours * 3600), "cleanup_reserve_seconds": 1200, "configuration_seconds": 1800,
                 "phases": list(a4.PHASES), "M": counts["M"], "M_FV": counts["M_FV"],
                 "groups": cv.GROUPS, "alpha": cv.ALPHA, "min_visits": cv.MIN_VISITS,
                 "validate_replicates": list(cv.VALIDATE_REPLICATES), "fv_validate_replicate": cv.FV_VALIDATE_REPLICATE,
                 "fit_replicate": cv.FIT_REPLICATE, "census_replicate": cv.CENSUS_REPLICATE,
                 "stream_tags": list(cv.STREAM_TAGS), "settings_override": settings_override,
                 "memory_estimate_gb": phase_estimates, "a6_family": family,
                 "memory_basis": "arithmetic, anchored on the A4 FV primary measured peak, scaling with population x length"}
    plan_hash = digest({**{k: plan_core[k] for k in ("schema", "source_file_sha256", "source_manifest_sha256",
                                                     "source_code_hash", "M", "M_FV", "code_hash", "settings_override")},
                        "registration": registration, "job_skeleton": [(c, p) for c, p in skeletons]})
    plan_core["plan_hash"] = plan_hash
    jobs = [a4._a4_job({**config, "plan_hash": plan_hash}, phase) for config, phase in skeletons]
    if len({j["id"] for j in jobs}) != len(jobs):
        raise ValueError("duplicate A6 validation job identifier")
    profiles = a4._configuration_profiles(source_root, source_code, manifest, plan_hash, settings_override)
    plan_core["configuration"] = {phase: _a6_profile(prof) for phase, prof in profiles.items()}
    plan_core.update(jobs=jobs, registration=registration,
                     probe_seed_count=len(probe_seeds), stream_seed_count=len(all_stream))
    # The global seed check at the validation step: the variant A4 stream seeds
    # against the full forbidden set and every other new seed (the family's own
    # table job seeds), before any validation simulation.
    if registration is not None:
        global_seed_check({family + "_a4_streams": list(all_stream.values()),
                           family + "_table_jobs": [j["seed"] for j in manifest["jobs"]]},
                          a1_source_root=a1_source_root, probe_root=a3_probe_root,
                          rerun_manifest=rerun_manifest)
        if seed_registry is not None:
            from .sensitivity_a6 import assert_registry_seeds
            assert_registry_seeds(seed_registry, "a4_streams", family, list(all_stream.values()))
    return plan_core


def publish_validation(plan, run_root, source_root, calibration, target, *, registered=True, registration=None):
    """Publish the validated variant family: the family, a receipt and a sidecar,
    as A4 does, loadable through ProductionTables(registered=True) at A6's identity.

    Reuses table_validation_a4's assembly, stage verification and plan-hash
    recomputation. Unlike A4's publish, the source pin is the family's own file
    hash (plan['source_file_sha256']) in both the registered and fixture cases;
    the A6 code registration is verified separately for a registered publish."""
    from .table_validation_a4 import (assemble_family, _verify_stage_outputs, _recompute_plan_hash,
                                      counts_from_job_outputs, AMENDMENT)
    from .production_tables import write_tables, ProductionTables
    from .artifacts import (verify_registration, file_hash, scoped, unseal, ROOT)
    from .calibration import validate_calibration
    source_root, run_root = Path(source_root), Path(run_root)
    if registered:
        # The A6 equivalent of table_validation_a4.registered_publish_guard: a
        # registered publish needs the registered flag and a registration pin, and
        # rejects any settings override, so a smoke plan cannot publish registered.
        if not plan.get("registered") or not plan.get("registration"):
            raise RuntimeError("registered publish requires a registered plan and a registration pin")
        if plan.get("settings_override") or any(j["config"].get("settings_override") for j in plan.get("jobs", [])):
            raise RuntimeError("registered publish rejects a settings override")
        # Verify the plan's own bound registration, and, if a pin is passed in,
        # require it to match the plan's, so a caller cannot swap the pin.
        if registration is not None and registration != plan["registration"]:
            raise RuntimeError("passed registration does not match the plan's bound registration")
        verify_registration(plan["registration"])
    # The source pin is the family's own assembled-tables file hash.
    if file_hash(source_root / "v3_rerun_tables_A1.json") != plan["source_file_sha256"]:
        raise ValueError("variant family source publication changed")
    a1_manifest = unseal(read(source_root / "tables_A1_manifest.json"))
    if digest(a1_manifest) != plan["source_manifest_sha256"]:
        raise ValueError("variant family manifest changed")
    if plan["code_hash"] != code_identity():
        raise ValueError("A6 producer source changed since prepare")
    if _recompute_plan_hash(plan) != plan["plan_hash"]:
        raise ValueError("plan hash does not match its job list, overrides and registration")
    validate_calibration(calibration, registered=registered)
    source_code = plan["source_code_hash"]
    counts = counts_from_job_outputs(source_root, source_code)
    if (counts["M"], counts["M_FV"]) != (plan["M"], plan["M_FV"]):
        raise ValueError("M or M_FV differs from the pinned plan")
    calibrations = {calibration["sha256"]: calibration}
    stage_hashes, stream_seeds = _verify_stage_outputs(plan, run_root)
    rows, sensitivity_status, details = assemble_family(source_root, source_code, run_root, plan["M"], plan["M_FV"], calibrations)
    manifest = {"tag": "v3_tables", "calibration_hash": calibration["sha256"],
                "design": dict(table_design(), amendment=AMENDMENT, a6_family=plan.get("a6_family")),
                "validated_continuation": {"amendment": AMENDMENT, "M": plan["M"], "M_FV": plan["M_FV"],
                                           "plan_hash": plan["plan_hash"], "stream_tags": plan["stream_tags"],
                                           "source_family": {"file_sha256": plan["source_file_sha256"], "code_hash": source_code}},
                "required_row_keys": sorted(rows), "complete_family": True,
                "sensitivity_status": sensitivity_status,
                "source_family": {"file_sha256": plan["source_file_sha256"], "code_hash": source_code},
                "a6_family": plan.get("a6_family")}
    candidate = scoped(run_root) / "candidate_unpublished_tables.json"
    document = write_tables(candidate, list(rows.values()), manifest, fixture=not registered)
    sidecar_doc = seal({"schema": "v3-A4-cell-results-1", "amendment": AMENDMENT, "plan_hash": plan["plan_hash"],
                        "table_seal_sha256": document["sha256"], "rows": details})
    atomic_json(candidate.with_suffix(".cell_results.json"), sidecar_doc)
    receipt = {"schema": "v3-A4-receipt-1", "amendment": AMENDMENT, "table_seal_sha256": document["sha256"],
               "table_file_sha256": file_hash(candidate), "producer_code_hash": document["payload"]["code_hash"],
               "source_family": {"file_sha256": plan["source_file_sha256"], "code_hash": source_code},
               "calibration_sha256": calibration["sha256"], "M": plan["M"], "M_FV": plan["M_FV"],
               "plan_hash": plan["plan_hash"], "stream_tags": plan["stream_tags"], "stage_output_sha256": stage_hashes,
               "stream_seeds": stream_seeds, "cell_results_sha256": file_hash(candidate.with_suffix(".cell_results.json")),
               "a6_family": plan.get("a6_family")}
    atomic_json(candidate.with_suffix(".compatibility.json"), seal(receipt))
    if registered:
        ProductionTables(candidate, calibration_hash=calibration["sha256"], registered=True)
    target_path = scoped(target) if str(Path(target).resolve()).startswith(str(ROOT)) else SIMULATION / target
    if target_path.exists() and read(target_path) != document:
        raise RuntimeError("A6 table target is frozen; publish a new path")
    atomic_json(Path(str(target_path)).with_suffix(".compatibility.json"), seal(receipt))
    atomic_json(Path(str(target_path)).with_suffix(".cell_results.json"), sidecar_doc)
    atomic_json(target_path, document)
    return {"rows": len(rows), "M": plan["M"], "M_FV": plan["M_FV"], "sensitivity_status": sensitivity_status,
            "not_estimable": sum(r["status"] != "estimated" for r in rows.values()), "detail_rows": len(details),
            "family": plan.get("a6_family")}
