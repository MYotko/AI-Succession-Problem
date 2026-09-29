"""A4 publication, lookup and resume tests.

Constructs a minimal A4-shaped family, loads it through require_production, and
checks the single lookup change: a population-category-0 key of a plain row with
a published C0 resolves to C0, and nothing else changes. Also checks durable
resume and seed determinism. Fast: no simulation of the real kernel.
"""
from pathlib import Path
import tempfile

import numpy as np
import pytest

from v3.artifacts import ROOT, digest, atomic_json, read, code_identity
from v3.production_tables import write_tables, ProductionTables, row_key
from v3.policies import execution_policy_class
from v3 import continuation_validation as cv
from v3 import table_validation_a4 as a4

CAL = "a4-test-calibration"
KERNEL = "a4-test-kernel"


def _row(rule, route, scoring, entries, c0=None):
    row = {"rule_id": rule.rule_id, "rule_hash": digest(rule.__dict__), "kernel_hash": KERNEL,
           "calibration_hash": CAL, "initial_population": 200, "scoring": scoring, "route": route,
           "status": "estimated", "lambda_f": {"mean": 1.0, "replicates": [1.0, 1.0, 1.0]},
           "flow_range": 10.0, "lambda_b": 1.0, "LS": 1.0,
           "continuation": {"entries": entries}}
    if c0 is not None:
        row["c0"] = c0
    return row


def _family():
    rules = execution_policy_class()
    r0, r1, r2 = rules[0], rules[1], rules[2]
    scoring = {"alpha": 1.0, "capability": 1.0, "kappa": 8.0}
    # Plain row with a published C0 and one validated non-population-0 cell.
    plain_c0 = _row(r0, "plain", scoring,
                    entries=[{"bin": [2, 1, 0, 0, 0, 0], "value": 3.0, "error": 7.0}],
                    c0={"value": -4.0, "error": 6.0})
    # Plain row without a C0 (population-0 unpublished).
    plain_no_c0 = _row(r1, "plain", scoring,
                       entries=[{"bin": [2, 1, 0, 0, 0, 0], "value": 2.0, "error": 8.0}])
    # FV row with a published population-0 cell (served from entries, not C0).
    fv = _row(r2, "fv", scoring,
              entries=[{"bin": [0, 1, 0, 0, 0, 0], "value": 1.5, "error": 8.5}])
    return [plain_c0, plain_no_c0, fv], (r0, r1, r2), scoring


def test_publication_loads_through_require_production():
    rows, _, _ = _family()
    keys = [row_key(r) for r in rows]
    manifest = {"tag": "v3_tables", "calibration_hash": CAL, "complete_family": True,
                "sensitivity_status": "passed", "required_row_keys": keys}
    with tempfile.TemporaryDirectory(dir=ROOT, prefix="_a4_pub_") as d:
        path = Path(d) / "tables.json"
        write_tables(path, rows, manifest, fixture=False)
        loaded = ProductionTables(path, calibration_hash=CAL, registered=True)  # calls require_production
        assert set(loaded.rows) == set(keys)


def test_lookup_pop0_resolves_to_c0_for_plain_row():
    rows, (r0, r1, r2), scoring = _family()
    keys = [row_key(r) for r in rows]
    manifest = {"tag": "v3_tables", "calibration_hash": CAL, "complete_family": True,
                "sensitivity_status": "passed", "required_row_keys": keys}
    with tempfile.TemporaryDirectory(dir=ROOT, prefix="_a4_pub_") as d:
        path = Path(d) / "tables.json"
        write_tables(path, rows, manifest, fixture=False)
        tables = ProductionTables(path, calibration_hash=CAL)
        common = dict(kernel_hash=KERNEL, capability=1.0, alpha=1.0, weights=[5, 3, 8], initial_population=200)

        # (1) population-0 key on the plain row with C0 -> resolves to C0.
        pop0 = (0, 3, 1, 0, 2, 1)
        out = tables.lookup_available([r0], [pop0], **common)
        assert bool(out.available[0]) and out.continuation[0] == -4.0 and out.continuation_error[0] == 6.0

        # (2) a non-population-0 key on that same plain row -> the ordinary entry, unchanged.
        out = tables.lookup_available([r0], [(2, 1, 0, 0, 0, 0)], **common)
        assert bool(out.available[0]) and out.continuation[0] == 3.0 and out.continuation_error[0] == 7.0

        # (3) an unpublished non-population-0 key -> unavailable (no C0 substitution).
        out = tables.lookup_available([r0], [(5, 5, 5, 5, 5, 5)], **common)
        assert not bool(out.available[0]) and out.unavailable_reasons[0] == "unpublished_continuation_bin"

        # (4) population-0 key on the plain row WITHOUT a C0 -> unavailable.
        out = tables.lookup_available([r1], [pop0], **common)
        assert not bool(out.available[0])

        # (5) population-0 key on the FV row -> its published entry, unchanged (no C0 path).
        out = tables.lookup_available([r2], [(0, 1, 0, 0, 0, 0)], **common)
        assert bool(out.available[0]) and out.continuation[0] == 1.5
        # a different population-0 FV key is not served from any C0.
        out = tables.lookup_available([r2], [(0, 7, 0, 0, 0, 0)], **common)
        assert not bool(out.available[0])

        # (6) extinct endpoint on the plain row -> unchanged (C0 path requires a living source).
        out = tables.lookup_available([r0], [pop0], extinct=[True], **common)
        assert bool(out.available[0]) and out.continuation[0] == 0.0  # extinct value is 0, as before


def test_lookup_c0_not_used_when_registered_strict():
    # The strict (non-allow_unavailable) lookup still returns C0 for a plain pop-0 key.
    rows, (r0, _, _), _ = _family()
    keys = [row_key(r) for r in rows]
    manifest = {"tag": "v3_tables", "calibration_hash": CAL, "complete_family": True,
                "sensitivity_status": "passed", "required_row_keys": keys}
    with tempfile.TemporaryDirectory(dir=ROOT, prefix="_a4_pub_") as d:
        path = Path(d) / "tables.json"
        write_tables(path, rows, manifest, fixture=False)
        tables = ProductionTables(path, calibration_hash=CAL)
        out = tables.lookup([r0], [(0, 3, 1, 0, 2, 1)], kernel_hash=KERNEL, capability=1.0, alpha=1.0,
                            weights=[5, 3, 8], initial_population=200)
        assert out.continuation[0] == -4.0


def test_c0_only_plain_row_passes_require_production():
    # A plain row certified through C0 alone (no fine entries) is valid support.
    rule = execution_policy_class()[0]
    scoring = {"alpha": 1.0, "capability": 1.0, "kappa": 8.0}
    row = _row(rule, "plain", scoring, entries=[], c0={"value": 0.0, "error": 1.0})
    keys = [row_key(row)]
    manifest = {"tag": "v3_tables", "calibration_hash": CAL, "complete_family": True,
                "sensitivity_status": "passed", "required_row_keys": keys}
    with tempfile.TemporaryDirectory(dir=ROOT, prefix="_a4_pub_") as d:
        path = Path(d) / "tables.json"
        write_tables(path, [row], manifest, fixture=False)
        loaded = ProductionTables(path, calibration_hash=CAL, registered=True)  # require_production
        tables = ProductionTables(path, calibration_hash=CAL)
        out = tables.lookup_available([rule], [(0, 3, 0, 0, 0, 0)], kernel_hash=KERNEL, capability=1.0,
                                      alpha=1.0, weights=[5, 3, 8], initial_population=200)
        assert bool(out.available[0]) and out.continuation[0] == 0.0


def test_lookup_c0_wins_even_when_entry_exists():
    # Item 9: for a plain row with a published C0, a population-0 key resolves to
    # C0 whether or not a fine entry exists for that key.
    rule = execution_policy_class()[0]
    scoring = {"alpha": 1.0, "capability": 1.0, "kappa": 8.0}
    row = _row(rule, "plain", scoring,
               entries=[{"bin": [0, 1, 0, 0, 0, 0], "value": 9.0, "error": 1.0}],
               c0={"value": -2.0, "error": 3.0})
    keys = [row_key(row)]
    manifest = {"tag": "v3_tables", "calibration_hash": CAL, "complete_family": True,
                "sensitivity_status": "passed", "required_row_keys": keys}
    with tempfile.TemporaryDirectory(dir=ROOT, prefix="_a4_pub_") as d:
        path = Path(d) / "tables.json"
        write_tables(path, [row], manifest, fixture=False)
        tables = ProductionTables(path, calibration_hash=CAL)
        out = tables.lookup_available([rule], [(0, 1, 0, 0, 0, 0)], kernel_hash=KERNEL, capability=1.0,
                                      alpha=1.0, weights=[5, 3, 8], initial_population=200)
        assert bool(out.available[0]) and out.continuation[0] == -2.0  # C0, not the 9.0 entry


def test_seed_determinism():
    a = cv.derive_seeds(123456789, "plain")
    b = cv.derive_seeds(123456789, "plain")
    assert a == b
    assert cv.fit_seed(123456789) == cv.fit_seed(123456789)


def test_registered_publish_refuses_smoke_plan():
    # A smoke plan (not registered, or carrying a settings override) is refused.
    with pytest.raises(RuntimeError, match="registered"):
        a4.registered_publish_guard({"registered": False, "registration": None, "jobs": []})
    with pytest.raises(RuntimeError, match="registered"):
        a4.registered_publish_guard({"registered": True, "registration": None, "jobs": []})
    with pytest.raises(RuntimeError, match="override"):
        a4.registered_publish_guard({"registered": True, "registration": {"commit": "x"}, "jobs": [],
                                     "settings_override": {"burn": 8}})
    with pytest.raises(RuntimeError, match="override"):
        a4.registered_publish_guard({"registered": True, "registration": {"commit": "x"},
                                     "jobs": [{"config": {"settings_override": {"burn": 8}}}]})
    # A registered plan with no override passes the guard.
    a4.registered_publish_guard({"registered": True, "registration": {"commit": "x"}, "jobs": [], "settings_override": None})


def test_publish_itself_refuses_smoke_plan():
    # publish() (not just the guard) refuses a non-registered plan when
    # registered=True, before touching any source file.
    plan = {"registered": False, "registration": None, "jobs": [], "settings_override": None}
    with pytest.raises(RuntimeError, match="registered"):
        a4.publish(plan, "unused", "unused", {"sha256": "x"}, "unused", registered=True)


def _complete_a4_job(phase_root, job, result):
    from v3.artifacts import atomic_json, file_hash, code_identity
    opath = phase_root / "outputs" / (job["id"] + ".json")
    atomic_json(opath, {"job": job, "code_hash": code_identity(), "result": result, "peak_rss_bytes": 1})
    atomic_json(phase_root / "records" / (job["id"] + ".json"),
                {"job": job, "code_hash": code_identity(), "status": "complete", "output_hash": file_hash(opath)})


def test_projection_resume_aware_and_stop():
    from v3.artifacts import code_identity, stable_job
    from v3.production_runner import a4_projection
    a1cfg = {"config": {"settings": {"runs_per_group": 64, "particles": 256, "burn": 1024, "measure": 2048}}}
    def mkjob(seed_i):
        cfg = {"phase": "census", "stage": "census", "route": "plain", "a1_job": {"id": "a1_%d" % seed_i, **a1cfg},
               "a1_source_code_hash": "h", "plan_hash": "P", "seed": seed_i}
        return stable_job("a4_census", cfg, "v3_tables", seed_i)
    j1, j2 = mkjob(1), mkjob(2)
    spec = {"phases": ["census"], "jobs": [j1, j2],
            "configuration": {"census": {"config": {"route": "plain", "settings_override": {"census_measure": 44},
                                                    "a1_job": {"config": {"settings": {"runs_per_group": 64}}}}}}}
    config_meas = {"census": [{"job_seconds": [10.0, 10.0]}]}
    effective = {"census": 2}
    with tempfile.TemporaryDirectory(dir=ROOT, prefix="_a4_proj_") as d:
        run_root = Path(d)
        # Nothing done yet: 2 remaining.
        proj = a4_projection(spec, config_meas, effective, run_root, code_identity(), 0, 0.0, 1e9)
        assert proj["phases"]["census"]["remaining"] == 2 and proj["fits"]
        # Complete j1 -> resume-aware projection counts only 1 remaining.
        _complete_a4_job(run_root / "census", j1, {"a1_job_id": "a1_1"})
        proj = a4_projection(spec, config_meas, effective, run_root, code_identity(), 0, 0.0, 1e9)
        assert proj["phases"]["census"]["remaining"] == 1
        # A tiny deadline -> does not fit -> launch would stop.
        proj = a4_projection(spec, config_meas, effective, run_root, code_identity(), 0, 0.0, 0.001)
        assert proj["fits"] is False


def test_verify_stage_outputs_refuses_identity_mismatch():
    from v3.artifacts import atomic_json, file_hash, code_identity, stable_job
    from v3.production_runner import completed
    with tempfile.TemporaryDirectory(dir=ROOT, prefix="_a4_idm_") as d:
        run_root = Path(d)
        a1_job = {"id": "table_real", "config": {}}
        config = {"stage": "census", "route": "plain", "a1_source_root": "x", "a1_job": a1_job,
                  "a1_source_code_hash": "h", "seed": 111, "plan_hash": "PLAN", "phase": "census"}
        job = stable_job("a4_census", config, "v3_tables", 0)
        phase_root = run_root / "census"
        # A completed record whose result carries the WRONG a1_job_id.
        output = {"job": job, "code_hash": code_identity(),
                  "result": {"a1_job_id": "WRONG", "stream_seed": 111, "plan_hash": "PLAN", "code_hash": code_identity()}}
        opath = phase_root / "outputs" / (job["id"] + ".json")
        atomic_json(opath, output)
        atomic_json(phase_root / "records" / (job["id"] + ".json"),
                    {"job": job, "code_hash": code_identity(), "status": "complete", "output_hash": file_hash(opath)})
        assert completed(phase_root, job, code_identity()) is not None
        plan = {"jobs": [job], "plan_hash": "PLAN"}
        with pytest.raises(ValueError, match="identity mismatch"):
            a4._verify_stage_outputs(plan, run_root)


CALIBRATION_PATH = Path(r"C:\Users\matty\Dev\v3_validation_repo\simulation\v3\runs\registered\v3_rerun_calibration.json")


def _write_a1_job(source_root, code, rule, rr, setting, rows, cal):
    from v3.artifacts import atomic_json, file_hash, stable_job, seal
    config = {"rule_id": rule.rule_id, "kernel": {"reproduction_rate": rr}, "setting_name": setting,
              "route": "auto", "scoring": [r["scoring"] for r in rows], "calibration_path": "v3/runs/registered/v3_rerun_calibration.json"}
    job = stable_job("table", config, "v3_tables", 0)
    output = {"job": job, "code_hash": code, "result": {"route": "plain", "calibration_hash": cal["sha256"],
              "kernel": {"reproduction_rate": rr}, "settings": {"groups": 6, "runs_per_group": 64, "particles": 256, "burn": 1024, "measure": 2048}, "rows": rows}}
    opath = source_root / "tables_A1/table/outputs" / (job["id"] + ".json")
    atomic_json(opath, output)
    atomic_json(source_root / "tables_A1/table/records" / (job["id"] + ".json"),
                {"job": job, "code_hash": code, "status": "complete", "output_hash": file_hash(opath)})
    return job


def _a1_row(rule, kernel_hash, cal, scoring, status, entries, coverage=0.95, converged=True, drift=True):
    from v3.artifacts import digest
    row = {"rule_id": rule.rule_id, "rule_hash": digest(rule.__dict__), "kernel_hash": kernel_hash,
           "calibration_hash": cal["sha256"], "initial_population": 200, "scoring": scoring, "route": "plain",
           "status": status, "reason": "continuation residual" if status != "estimated" else None,
           "lambda_f": {"mean": 1.0, "replicates": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]}, "flow_range": 10.0,
           "screens": {"route_applicable": True, "flow_half_width": True, "half_window_drift": drift},
           "continuation": {"entries": entries, "heldout_coverage": coverage, "training_fixed_point_converged": converged}}
    return row


@pytest.mark.skipif(not CALIBRATION_PATH.exists(), reason="calibration not present")
def test_end_to_end_assembly_four_row_types():
    from v3.artifacts import read, atomic_json, code_identity
    from v3.context import Context
    cal = read(CALIBRATION_PATH)
    code = code_identity()
    from v3.offline_estimator import SENSITIVITY_RULES
    rules = execution_policy_class()
    balanced = next(r for r in rules if r.rule_id == "balanced")
    non_sensitivity = [r for r in rules if r.rule_id not in SENSITIVITY_RULES]
    other = non_sensitivity[0]
    rr = 0.064
    kernel_hash = Context.build({"reproduction_rate": rr}, cal).kernel_hash
    sc = {"alpha": 1.0, "capability": 1.0, "kappa": 8.0}
    fine = [2, 1, 0, 0, 0, 0]
    fine_code = int(cv.fine_codes([fine])[0])
    entries = [{"bin": fine, "value": 3.0, "error": 7.0}]

    with tempfile.TemporaryDirectory(dir=ROOT, prefix="_a4_e2e_") as d:
        source = Path(d) / "src"
        stage = Path(d) / "stage"
        (source / "tables_A1/table/outputs").mkdir(parents=True)
        (source / "tables_A1/table/records").mkdir(parents=True)
        # Job A: a rescued (A1 not_estimable, continuation-only) row + a normal row; sensitivity pair.
        rescued = _a1_row(balanced, kernel_hash, cal, sc, "not_estimable", entries)
        jobA = _write_a1_job(source, code, balanced, rr, "primary", [rescued], cal)
        jobA_dp = _write_a1_job(source, code, balanced, rr, "double_population", [_a1_row(balanced, kernel_hash, cal, sc, "estimated", entries)], cal)
        jobA_dl = _write_a1_job(source, code, balanced, rr, "double_length", [_a1_row(balanced, kernel_hash, cal, sc, "estimated", entries)], cal)
        # Job B: zero-endpoint census -> floor passes not assessed.
        jobB = _write_a1_job(source, code, other, rr, "primary", [_a1_row(other, kernel_hash, cal, sc, "estimated", entries)], cal)
        # Job C: living endpoints outside support -> floor fails.
        jobC_rule = non_sensitivity[1]
        jobC = _write_a1_job(source, code, jobC_rule, rr, "primary", [_a1_row(jobC_rule, kernel_hash, cal, sc, "estimated", entries)], cal)
        manifest = {"jobs": [jobA, jobA_dp, jobA_dl, jobB, jobC], "source_family": {"code_hash": code}, "tag": "v3_tables"}
        from v3.artifacts import seal
        atomic_json(source / "tables_A1_manifest.json", seal(manifest))

        PT = {"n_traj": 1000, "sum_S": 0.0, "sum_N": 1000.0, "sum_S2": 0.0, "sum_N2": 1000.0, "sum_SN": 0.0, "sum_m": 0.0, "sum_m2": 0.0}
        inside = {int(cv.fine_codes([[0, 1, 0, 0, 0, 0]])[0]): 60, fine_code: 40}   # all inside support
        outside = {int(cv.fine_codes([[7, 7, 7, 7, 7, 7]])[0]): 50, fine_code: 50}  # 50% outside
        census = {jobA["id"]: inside, jobA_dp["id"]: inside, jobA_dl["id"]: inside,
                  jobB["id"]: {}, jobC["id"]: outside}
        for job in manifest["jobs"]:
            jid = job["id"]
            cc = census[jid]
            atomic_json(stage / "census" / "outputs" / ("a4_census_" + jid + ".json"),
                        {"a1_job_id": jid, "cell_counts": cc, "total_living": sum(cc.values()),
                         "total_low": sum(v for c, v in cc.items() if c % 8 == 0)})
            atomic_json(stage / "fit" / "outputs" / ("a4_fit_" + jid + ".json"),
                        {"a1_job_id": jid, "rows": [{"scoring": sc, "c0": {"value": 0.0, "published": True, "visits": 100}}]})
            phase = "validate_plain"
            for rep in cv.VALIDATE_REPLICATES:
                cells = [{"cell": int(cv.POP0_CELL), **PT}, {"cell": fine_code, **PT}]
                atomic_json(stage / phase / "outputs" / ("a4_validate_%s_r%d.json" % (jid, rep)),
                            {"a1_job_id": jid, "replicate": rep, "rows": [{"scoring": sc, "cells": cells}]})

        M = cv.count_M_plain([r for j in manifest["jobs"] for r in read(source / "tables_A1/table/outputs" / (j["id"] + ".json"))["result"]["rows"]])
        primary, sens, details = a4.assemble_family(source, code, stage, M, 1, {cal["sha256"]: cal})
        # Sidecar details cover primary AND sensitivity rows.
        assert any(d["setting"] != "primary" for d in details)
        from v3.production_tables import row_key
        rowA = primary[row_key(rescued)]
        rowB = primary[row_key(read(source / "tables_A1/table/outputs" / (jobB["id"] + ".json"))["result"]["rows"][0])]
        rowC = primary[row_key(read(source / "tables_A1/table/outputs" / (jobC["id"] + ".json"))["result"]["rows"][0])]
        # rescued A1 row -> estimated, with its A1 reason preserved and cleared from reason
        assert rowA["status"] == "estimated" and rowA["a1_reason"] == "continuation residual" and rowA.get("reason") is None
        assert rowA["sensitivity"]["selected"] and rowA["sensitivity"]["passed"] and sens == "passed"
        # zero-endpoint census -> estimated, floor not assessed
        assert rowB["status"] == "estimated" and rowB["a4"]["floor"]["assessed"] is False
        # living endpoints outside support -> floor fails -> not_estimable
        assert rowC["status"] == "not_estimable" and rowC["a4"]["floor"]["assessed"] is True and not rowC["a4"]["floor"]["living_ok"]


A1_ROOT = Path(r"C:\Users\matty\Dev\v3_instrument_inputs\registered_A1")


@pytest.mark.skipif(not (A1_ROOT / "tables_A1_manifest.json").exists(), reason="A1 records not present")
def test_run_stage_job_census_determinism_and_identity():
    from v3.production_runner import completed, execute
    from v3.artifacts import digest
    source_code = a4._source_code_hash(A1_ROOT)
    jobs = {j["id"]: j for j in a4.selected_a1_jobs(A1_ROOT)}
    jid = next(iter(jobs))
    a1_job = jobs[jid]
    seed = cv.census_seed(a1_job["seed"])
    config = {"stage": "census", "route": "plain", "a1_source_root": str(A1_ROOT.resolve()),
              "a1_job": a1_job, "a1_source_code_hash": source_code, "seed": seed, "plan_hash": "test-plan",
              "settings_override": {"groups": 4, "runs_per_group": 8, "census_measure": 40}, "phase": "census"}
    job = {"kind": "a4_census", "config": config, "tag": "v3_tables", "index": 0, "id": "x", "seed": 1}
    r1 = execute(job, root=None)
    r2 = execute(job, root=None)
    # deterministic result, and identity bound to the A1 job / stream seed / plan
    assert digest(r1) == digest(r2)
    assert r1["a1_job_id"] == jid and r1["stream_seed"] == int(seed) and r1["plan_hash"] == "test-plan"
    assert "cell_counts" in r1


def test_assemble_plain_row_builds_support_and_c0():
    rule = execution_policy_class()[0]
    scoring = {"alpha": 1.0, "capability": 1.0, "kappa": 8.0}
    fine = int(cv.fine_codes([[2, 1, 0, 0, 0, 0]])[0])
    a1_row = _row(rule, "plain", scoring, entries=[{"bin": [2, 1, 0, 0, 0, 0], "value": 0.5, "error": 0.5}])
    a1_row["flow_range"] = 2.0
    fit_row = {"c0": {"value": 0.0, "published": True, "visits": 100}}
    lower, upper = -1.0, 1.0
    # Zero-residual, well-visited cells certify at this tau and width.
    combined = {
        cv.POP0_CELL: {"n_traj": 200, "sum_S": 0.0, "sum_N": 300.0, "sum_S2": 0.0, "sum_N2": 900.0,
                       "sum_SN": 0.0, "sum_m": 0.0, "sum_m2": 0.0},
        fine: {"n_traj": 200, "sum_S": 0.0, "sum_N": 300.0, "sum_S2": 0.0, "sum_N2": 900.0,
               "sum_SN": 0.0, "sum_m": 0.0, "sum_m2": 0.0},
    }
    from v3.table_validation_a4 import assemble_plain_row
    out = assemble_plain_row(a1_row, fit_row, combined, M=10, tau=0.5, lower=lower, upper=upper)
    assert out["c0"] is not None and abs(out["c0"]["value"]) < 1e-9
    # bounded-domain enclosure error = max(C0 - lower, upper - C0)
    assert abs(out["c0"]["error"] - max(0.0 - lower, upper - 0.0)) < 1e-9
    assert cv.POP0_CELL in out["support_values"] and fine in out["support_values"]


def test_assemble_plain_row_drops_uncertified_cell():
    rule = execution_policy_class()[0]
    scoring = {"alpha": 1.0, "capability": 1.0, "kappa": 8.0}
    fine = int(cv.fine_codes([[2, 1, 0, 0, 0, 0]])[0])
    a1_row = _row(rule, "plain", scoring, entries=[{"bin": [2, 1, 0, 0, 0, 0], "value": 3.0, "error": 7.0}])
    fit_row = {"c0": {"value": None, "published": False, "visits": 0}}
    from v3.table_validation_a4 import assemble_plain_row
    # A large mean residual with tiny n -> unresolved, so not in support.
    combined = {fine: {"n_traj": 3, "sum_S": 30.0, "sum_N": 3.0, "sum_S2": 300.0, "sum_N2": 3.0,
                       "sum_SN": 30.0, "sum_m": 30.0, "sum_m2": 300.0}}
    out = assemble_plain_row(a1_row, fit_row, combined, M=100, tau=0.5, lower=-5.0, upper=5.0)
    assert fine not in out["support_values"] and out["c0"] is None


def test_assemble_fv_row_support():
    rule = execution_policy_class()[0]
    scoring = {"alpha": 1.0, "capability": 1.0, "kappa": 8.0}
    fine = int(cv.fine_codes([[1, 0, 0, 0, 0, 0]])[0])
    a1_row = _row(rule, "fv", scoring, entries=[{"bin": [1, 0, 0, 0, 0, 0], "value": 1.5, "error": 8.5}])
    from v3.table_validation_a4 import assemble_fv_row
    combined = {fine: {"S_g": [0.0] * 32, "N_g": [10.0] * 32}}  # zero residuals, 32 groups -> pass
    out = assemble_fv_row(a1_row, combined, M_fv=1000, tau=0.5)
    assert fine in out["support_values"] and out["label"] == "asymptotic, not certified"
