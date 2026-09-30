"""A6 variant table family tests: counts, contexts, assembly, A4 publication."""
import contextlib
import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest

from v3 import tables_a6 as t6
from v3.artifacts import ROOT, SIMULATION, atomic_json, code_identity, digest, file_hash, seal

CAL_PATH = "v3/runs/registered/v3_rerun_calibration.json"
FROZEN = SIMULATION / "v3" / "runs" / "registered" / "v3_rerun_calibration.json"
needs_cal = pytest.mark.skipif(not FROZEN.exists(), reason="frozen calibration not available")


@contextlib.contextmanager
def _scratch():
    d = tempfile.mkdtemp(dir=str(ROOT), prefix="_a6_test_")
    try:
        yield d
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_family_job_counts():
    assert len(t6.build_jobs("crowding", CAL_PATH)) == t6.COUNT_CROWDING_JOBS == 237
    assert len(t6.build_jobs("sigma_squared_x10", CAL_PATH)) == t6.COUNT_SIGMA_JOBS == 131


def test_scoring_has_no_kappa_075_and_no_stray_alpha():
    for family, grid in (("crowding", t6.CROWDING_RR), ("sigma_squared_x10", t6.SIGMA_RR)):
        for rr in grid:
            ctx = t6.family_scoring(family, rr)
            assert {c["kappa"] for c in ctx} == {8.0}
            if rr == 0.064 and family == "crowding":
                assert {c["alpha"] for c in ctx} == {0.5, 0.75, 1.0, 1.25, 1.5}
            else:
                assert {c["alpha"] for c in ctx} == {1.0}


def test_sensitivity_subset_counts():
    crowd = t6.build_jobs("crowding", CAL_PATH)
    assert len([j for j in crowd if j["config"]["setting_name"] != "primary"]) == 12
    sig = t6.build_jobs("sigma_squared_x10", CAL_PATH)
    assert len([j for j in sig if j["config"]["setting_name"] != "primary"]) == 6


# --------------------------------------------------------------------------
# Synthetic complete family (for the registered assembly + load tests)
# --------------------------------------------------------------------------

def _synthetic_outputs(family, cal, *, route="plain"):
    """Full synthetic estimated outputs covering the family's contexts, all
    estimated with a continuation entry, and passing sensitivity contrasts."""
    from v3.context import Context
    from v3.policies import execution_policy_class
    from v3.offline_estimator import settings_for, SENSITIVITY_RULES, SENSITIVITY_RR
    code = code_identity()
    outputs = []

    def row_for(rule, rr, scoring):
        ctx = Context.build(t6.family_kernel(family, rr), cal)
        lo, hi = ctx.parameters.extinction_flow, ctx.parameters.upper_bound
        mean = (lo + hi) / 2
        return {"rule_id": rule.rule_id, "rule_hash": digest(rule.__dict__), "kernel_hash": ctx.kernel_hash,
                "calibration_hash": cal["sha256"], "initial_population": 200, "scoring": scoring,
                "status": "estimated", "reason": None,
                "lambda_f": {"mean": mean, "replicates": [mean] * 6, "interval95": [lo, hi], "half_width": 0.0},
                "flow_range": hi - lo, "route": route, "lambda_b": mean, "LS": 1.0,
                "continuation": {"entries": [{"bin": [1, 0, 0, 0, 0, 0], "value": mean, "error": 0.1}]},
                "zeta": {"status": "unresolved", "upper": 1.0}, "screens": {}}

    def output_for(rule, rr, name):
        scoring = t6.family_scoring(family, rr)
        cfg = {"phase": "table", "rule_id": rule.rule_id, "kernel": t6.family_kernel(family, rr),
               "settings": settings_for(name), "setting_name": name, "route": route, "scoring": scoring,
               "calibration_path": CAL_PATH, "a6_family": family}
        result = {"rows": [row_for(rule, rr, s) for s in scoring], "route": route,
                  "calibration_hash": cal["sha256"], "fixture_calibration": False}
        return {"job": {"tag": "v3_tables", "config": cfg}, "code_hash": code, "result": result}

    for rr in t6.family_rrs(family):
        for rule in execution_policy_class():
            outputs.append(output_for(rule, rr, "primary"))
            if rule.rule_id in SENSITIVITY_RULES and rr in SENSITIVITY_RR:
                outputs.append(output_for(rule, rr, "double_population"))
                outputs.append(output_for(rule, rr, "double_length"))
    return outputs


@needs_cal
def test_registered_assembly_passing_case_and_registered_load():
    from v3.production_tables import ProductionTables
    cal = json.loads(FROZEN.read_text())
    outputs = _synthetic_outputs("sigma_squared_x10", cal)
    with _scratch() as tmp:
        target = Path(tmp) / "v3_rerun_tables_A1.json"
        # Registered assembly of a complete, all-estimated, sensitivity-passing family.
        t6.assemble(outputs, cal, target, "sigma_squared_x10", registered=True)
        # It loads at registered level.
        loaded = ProductionTables(target, calibration_hash=cal["sha256"], registered=True)
        assert loaded.fixture is False and len(loaded.rows) > 0


@needs_cal
def test_registered_assembly_rejects_settings_override():
    cal = json.loads(FROZEN.read_text())
    outputs = _synthetic_outputs("sigma_squared_x10", cal)
    outputs[0]["job"]["config"]["settings"] = dict(outputs[0]["job"]["config"]["settings"], burn=1)
    with _scratch() as tmp:
        with pytest.raises(ValueError):
            t6.assemble(outputs, cal, Path(tmp) / "v3_rerun_tables_A1.json", "sigma_squared_x10", registered=True)


def _tiny_family(tmp, family="crowding", rr=0.060):
    from v3.offline_estimator import estimate
    cal = json.loads(FROZEN.read_text())
    code = code_identity()
    src = Path(tmp)
    run = src / "tables_A1"
    (run / "table" / "outputs").mkdir(parents=True, exist_ok=True)
    (run / "table" / "records").mkdir(parents=True, exist_ok=True)
    tiny = {"groups": 4, "runs_per_group": 4, "particles": 8, "burn": 16, "measure": 64}
    jobs = t6.build_jobs(family, CAL_PATH, settings_override=tiny, rrs=[rr], rule_ids=["balanced"])
    outputs = []
    for j in jobs:
        res = estimate(j["config"], j["seed"], cal)
        out = {"job": j, "code_hash": code, "result": res}
        op = run / "table" / "outputs" / (j["id"] + ".json")
        atomic_json(op, out)
        atomic_json(run / "table" / "records" / (j["id"] + ".json"),
                    {"job": j, "code_hash": code, "status": "complete", "output_hash": file_hash(op)})
        outputs.append(out)
    manifest = {"schema": "v3-registered-1", "registered": True, "tag": "v3_tables", "code_hash": code,
                "phases": ["table"], "jobs": jobs, "configuration": {"table": {}}, "publication": None}
    atomic_json(src / "tables_A1_manifest.json", seal(manifest))
    return src, run, outputs, cal


@needs_cal
def test_registered_assembly_incomplete_family_raises():
    with _scratch() as tmp:
        src, run, outputs, cal = _tiny_family(tmp)
        with pytest.raises(ValueError):
            t6.assemble(outputs, cal, src / "v3_rerun_tables_A1.json", "crowding", registered=True)
        t6.assemble(outputs, cal, src / "v3_rerun_tables_A1.json", "crowding", registered=False)
        assert (src / "v3_rerun_tables_A1.json").exists()


@needs_cal
def test_a4_publication_of_tiny_family_loads_through_production_tables():
    from v3.production_runner import execute
    from v3.production_tables import ProductionTables
    with _scratch() as tmp:
        src, run, outputs, cal = _tiny_family(tmp)
        code = code_identity()
        t6.assemble(outputs, cal, src / "v3_rerun_tables_A1.json", "crowding", registered=False)
        probe = Path(tmp) / "probe"
        probe.mkdir(parents=True, exist_ok=True)
        atomic_json(probe / "p.json", {"seed": 424242424242})
        plan = t6.prepare_validation(src, CAL_PATH, family="crowding", a3_probe_root=str(probe),
                                     settings_override={"groups": 4, "burn": 16, "measure": 64, "census_measure": 44})
        for j in plan["jobs"]:
            proot = run.parent / j["config"]["phase"]
            (proot / "outputs").mkdir(parents=True, exist_ok=True)
            (proot / "records").mkdir(parents=True, exist_ok=True)
            res = execute(j, root=proot)
            out = {"job": j, "code_hash": code, "result": res}
            op = proot / "outputs" / (j["id"] + ".json")
            atomic_json(op, out)
            atomic_json(proot / "records" / (j["id"] + ".json"),
                        {"job": j, "code_hash": code, "status": "complete", "output_hash": file_hash(op)})
        target = src / "v3_rerun_tables_crowding.json"
        result = t6.publish_validation(plan, run.parent, src, cal, target, registered=False, registration=None)
        assert result["rows"] >= 1
        loaded = ProductionTables(target, calibration_hash=cal["sha256"], registered=False)
        assert len(loaded.rows) == result["rows"] and loaded.fixture is True


@needs_cal
def test_registered_estimation_spec_rejects_settings_override():
    with pytest.raises(ValueError):
        t6.estimation_spec("crowding", CAL_PATH, {"commit": "c", "path": "p", "sha256": "s"},
                           settings_override={"burn": 1})


@needs_cal
def test_registered_prepare_validation_without_family_refuses():
    with _scratch() as tmp:
        src, run, outputs, cal = _tiny_family(tmp)
        t6.assemble(outputs, cal, src / "v3_rerun_tables_A1.json", "crowding", registered=False)
        probe = Path(tmp) / "probe"
        probe.mkdir(parents=True, exist_ok=True)
        atomic_json(probe / "p.json", {"seed": 1234567})
        with pytest.raises(ValueError):
            t6.prepare_validation(src, CAL_PATH, family=None,
                                  registration={"commit": "c", "path": "p", "sha256": "s"},
                                  rerun_commit="HEAD", a3_probe_root=str(probe))


@needs_cal
def test_validate_spec_on_validation_plan():
    from v3 import production_runner as pr
    with _scratch() as tmp:
        src, run, outputs, cal = _tiny_family(tmp)
        t6.assemble(outputs, cal, src / "v3_rerun_tables_A1.json", "crowding", registered=False)
        probe = Path(tmp) / "probe"
        probe.mkdir(parents=True, exist_ok=True)
        atomic_json(probe / "p.json", {"seed": 222333})
        plan = t6.prepare_validation(src, CAL_PATH, family="crowding", a3_probe_root=str(probe),
                                     settings_override={"groups": 4, "burn": 16, "measure": 64, "census_measure": 44})
        assert plan["schema"] == "v3-A4-validation-1"
        settings = {"profile": "local", "workers": 3, "threads": 1, "cpu_budget": 4, "mode": "normal",
                    "caps": pr.caps("local", 4)}
        pr.validate_spec(plan, settings)          # the unchanged runner accepts the A6 validation plan


def test_registered_publish_guard_and_registration_binding():
    # A registered publish needs a registered plan with a bound registration, and
    # rejects a passed pin that disagrees with the plan's bound one (item 11).
    with pytest.raises(RuntimeError):
        t6.publish_validation({"registered": False, "registration": None}, "r", "s", {"sha256": "x"}, "t",
                              registered=True, registration={"commit": "c", "path": "p", "sha256": "s"})
    plan = {"registered": True, "registration": {"commit": "a", "path": "p", "sha256": "s"}, "jobs": []}
    with pytest.raises(RuntimeError):
        t6.publish_validation(plan, "r", "s", {"sha256": "x"}, "t", registered=True,
                              registration={"commit": "DIFFERENT", "path": "p", "sha256": "s"})
