"""Frozen pilot, conservative projections, bundle and complete local launch."""
from copy import deepcopy
import time
import zipfile
import pytest
from v3.artifacts import atomic_json, read, seal, code_identity, stable_job, file_hash
from v3.pilot import make_spec, project_costs, build_bundle, verify_bundle
from v3.study import registered_spec
from v3 import production_runner as runner


def test_pilot_freezes_complete_runs_routes_and_cost_sensitivities():
    spec = make_spec()
    assert len(spec["jobs"]) == 35
    assert not spec["registered"] and not spec["results_eligible"]
    assert spec["wall_seconds"] == 10800 and spec["cleanup_reserve_seconds"] >= 300
    reruns = [j for j in spec["jobs"] if j["kind"] == "rerun"]
    assert len(reruns) == 18 and all(j["config"]["steps"] == 500 for j in reruns)
    assert len({tuple(j["config"]["model"].values()) for j in reruns}) == 6
    assert len({j["seed"] for j in spec["jobs"]}) == 35
    assert all(j["tag"] == "pilot" for j in spec["jobs"])
    tables = [j for j in spec["jobs"] if j["kind"] == "table"]
    assert {j["config"]["route"] for j in tables} == {"plain", "fv", "auto"}
    assert sum(j["config"]["setting_name"] != "primary" for j in tables) == 2
    for profile in spec["configuration"].values():
        assert {8, 12, 16, 24, 28, 31, 32} == set(profile["workers_x2"])


@pytest.mark.parametrize("machine", ["yotko-evo-x2", "local-test"])
def test_cost_projection_counts_all_work_and_labels_machine(tmp_path, monkeypatch, machine):
    spec = make_spec()
    def completed(root, job, code):
        return {"job": job, "seconds": 100., "runtime": {"machine": machine},
                "result": {"population_mean": 200., "population_max": 1600, "rescore_seconds": 20.}}
    monkeypatch.setattr(runner, "completed", completed)
    outcomes = {p: {"selection": {"workers": 2, "threads": 1}} for p in spec["phases"]}
    measurements = {p: [{"workers": 2, "threads": 1, "valid": True, "job_seconds": [100., 100.], "wall_seconds": 100.}] for p in spec["phases"]}
    report = project_costs(spec, tmp_path, outcomes, measurements)
    assert report["rerun_hours_max_case"] == pytest.approx(24900 * 100 / 2 / 3600)
    minimum_contexts = min(len(j["config"]["scoring"]) for j in spec["jobs"] if j["kind"] == "table")
    scaled_primary = (100 + 20 * (report["primary_table_scoring_context_allowance"] / minimum_contexts - 1)) / 2
    assert report["table_hours_conservative"] == pytest.approx((325 * scaled_primary + 9 * 100 + 50 * 50) / 3600 + .25)
    assert report["actual_X2_measurement"] == (machine == "yotko-evo-x2")
    if machine == "local-test":
        assert report["rerun_gap_hours"] is None and report["tables_within_24h_projection"] is None
    else:
        assert report["rerun_gap_hours"] == pytest.approx(24900 * 50 / 3600 - 72)
    first = spec["jobs"][0]["id"]
    monkeypatch.setattr(runner, "completed", lambda root, job, code: None if job["id"] == first else completed(root, job, code))
    assert project_costs(spec, tmp_path, outcomes, measurements)["status"] == "incomplete"


def test_bundle_roundtrip_hashes_and_tamper(tmp_path):
    result = build_bundle(tmp_path / "bundle")
    extracted = tmp_path / "extracted"
    with zipfile.ZipFile(result["archive"]) as stream:
        assert all(name.startswith("simulation/") or name == "BUNDLE_MANIFEST.json" for name in stream.namelist())
        assert not any("inputs" in name or "preregistration" in name for name in stream.namelist())
        stream.extractall(extracted)
    manifest = verify_bundle(extracted)
    assert manifest["code_hash"] == code_identity()
    assert manifest["spec_hash"] == result["spec_hash"]
    source = extracted / "simulation" / "v3" / "integration.py"
    source.write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        verify_bundle(extracted)


def test_full_registered_manifest_builders_keep_grids_and_pin_gate():
    pin = {"commit": "uncommitted", "path": "plan.md", "sha256": "missing"}
    rerun = registered_spec("rerun", pin, "v3/cal.json", "v3/tables.json")
    table = registered_spec("table", pin, "v3/cal.json", publication_path="v3/tables.json")
    calibration = registered_spec("calibration", pin, publication_path="v3/cal.json")
    assert len(rerun["jobs"]) == 24900 and rerun["wall_seconds"] == 72 * 3600
    assert len(table["jobs"]) == 343 and table["wall_seconds"] == 24 * 3600
    assert {c["route"] for c in table["configuration"]["table"]["configs"]} == {"plain", "fv"}
    assert len(calibration["jobs"]) == 50
    assert all(s["registered"] and s["registration"] == pin for s in (rerun, table, calibration))


def test_complete_local_scientific_launch_and_resume(tmp_path):
    settings = {"profile": "local", "workers": 2, "threads": 1, "cpu_budget": 4, "mode": "normal"}
    model = {"n_agents": 20, "carrying_capacity": 100, "reproduction_rate": .064}
    cfg = {"phase": "rerun", "steps": 2, "model": model}
    jobs = [stable_job("rerun", cfg, "validation", i) for i in range(2)]
    profile = {"kind": "rerun", "config": {"steps": 1, "model": model}, "workers_local": [1, 2],
               "jobs_local": 2, "threads": [1], "rounds": 1}
    spec = {"registered": False, "tag": "validation", "code_hash": code_identity(), "jobs": jobs,
            "phases": ["rerun"], "configuration": {"rerun": profile}, "wall_seconds": 120, "cleanup_reserve_seconds": 5}
    path, root = tmp_path / "spec.json", tmp_path / "run"
    atomic_json(path, seal(spec))
    first = runner.launch(path, root, settings)
    assert first["complete"]
    output = root / "rerun" / "outputs" / (jobs[0]["id"] + ".json")
    preserved = file_hash(output)
    assert read(output)["result"]["steps"] == 2
    control = read(root / "control.json")
    control["mode"] = "work"
    atomic_json(root / "control.json", control)
    second = runner.launch(path, root, settings)
    assert second["complete"] and file_hash(output) == preserved
    assert read(root / "control.json")["mode"] == "work"
    assert len(read(root / "launches.json")) == 2
    broken = deepcopy(spec)
    broken["phases"] = []
    with pytest.raises(ValueError, match="phase"):
        runner.validate_spec(broken, {**settings, "caps": runner.caps("local", 4)})


# Artifacts stay inside the authorized tree even with default pytest options.
from test_v3_paths import tmp_path
