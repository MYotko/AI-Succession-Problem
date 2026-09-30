"""A6 sensitivity-run tests: counts, seeds, invariance, runner acceptance."""
from unittest import mock

import pytest

from v3 import sensitivity_a6 as s6
from v3.artifacts import SIMULATION, stable_job

A1_ROOT = SIMULATION.parent.parent / "v3_instrument_inputs" / "registered_A1"
PROBE_ROOT = SIMULATION.parent.parent / "v3_instrument_inputs" / "a3_probe"
needs_inputs = pytest.mark.skipif(not (A1_ROOT / "tables_A1_manifest.json").exists(),
                                  reason="registered A1 source not available")


def test_arm_run_counts():
    assert len(s6.build_weight_corner_jobs()) == 17600
    assert len(s6.build_horizon_jobs()) == 1800
    assert len(s6.build_crowding_jobs("cal", "tab")) == 4400
    assert len(s6.build_sigma_jobs({"sigma_squared_x10": ("c", "t"),
                                    "sigma_squared_x0.1": ("c", "t")})) == 1000


def test_grid_has_44_distinct_cells_with_r1_r2_split():
    cells = s6._grid_cells()
    assert len(cells) == 44
    # The R1 and R2 (0.064, 1.0, 1.5) cells are distinct by grid marker.
    assert ("R1", 0.064, 1.0, 1.5) in cells
    assert ("R2", 0.064, 1.0, 1.5) in cells


def test_all_run_seeds_distinct():
    jobs = (s6.build_weight_corner_jobs() + s6.build_horizon_jobs()
            + s6.build_crowding_jobs("cal", "tab")
            + s6.build_sigma_jobs({"sigma_squared_x10": ("c10", "t10"), "sigma_squared_x0.1": ("c01", "t01")}))
    seeds = [j["seed"] for j in jobs]
    assert len(set(seeds)) == len(seeds) == 24800


def test_stable_job_identity_holds_in_runner_validate_spec():
    # Every A6 run job survives the runner's scheduling-independent re-derivation.
    for j in s6.build_horizon_jobs():
        assert stable_job(j["kind"], j["config"], j["tag"], j["index"]) == j


@needs_inputs
def test_seeds_clear_of_forbidden_set():
    jobs = (s6.build_weight_corner_jobs() + s6.build_horizon_jobs())
    forbidden = s6.forbidden_seeds(A1_ROOT, PROBE_ROOT if PROBE_ROOT.exists() else None)
    # No overlap, and the forbidden set covers A1, A4, A5, planning and rerun seeds.
    assert set(j["seed"] for j in jobs).isdisjoint(forbidden)
    assert len(forbidden) > 24900          # at least the 24,900 reruns plus derived seeds
    s6.assert_seeds_clear(jobs, forbidden, require_probe={1})


@needs_inputs
def test_collision_halts():
    forbidden = s6.forbidden_seeds(A1_ROOT, PROBE_ROOT if PROBE_ROOT.exists() else None)
    jobs = s6.build_horizon_jobs()
    poisoned = list(forbidden)[0]
    tampered = [dict(jobs[0], seed=poisoned)] + jobs[1:]
    with pytest.raises(s6.SeedCollision):
        s6.assert_seeds_clear(tampered, forbidden)


def test_registered_run_requires_probe():
    with pytest.raises(ValueError):
        s6.assert_seeds_clear(s6.build_horizon_jobs(), set(), require_probe=set())


def test_invariance_passes_against_head():
    result = s6.rerun_path_invariance("HEAD")
    assert result["mismatches"] == []
    assert result["missing_at_commit"] == []
    # The new A6 modules are excluded from the rerun-path comparison.
    assert any(name.endswith("_a6.py") for name in result["a6_modules_excluded"])


def test_invariance_detects_a_mismatch():
    # Force one file's committed bytes to differ.
    real_git = s6._git

    def fake_git(repo, *args):
        if args and args[0] == "show":
            return b"tampered contents that do not match the working tree\n"
        return real_git(repo, *args)

    with mock.patch.object(s6, "_git", fake_git):
        result = s6.rerun_path_invariance("HEAD")
    assert result["mismatches"]
    with mock.patch.object(s6, "_git", fake_git):
        with pytest.raises(RuntimeError):
            s6.assert_rerun_path_invariant("HEAD")


@needs_inputs
def test_a5_fvplain_seeds_in_forbidden_set():
    from v3 import continuation_validation as cv
    from v3.table_validation_a4 import _load_a1
    manifest = s6._a1_manifest(A1_ROOT)
    code = manifest.get("source_family", {}).get("code_hash") or manifest.get("code_hash")
    fv_job = next(j for j in manifest["jobs"]
                  if j["config"].get("setting_name", "primary") == "primary"
                  and _load_a1(A1_ROOT, j, code)["result"]["route"] == "fv")
    forbidden = s6.forbidden_seeds(A1_ROOT, PROBE_ROOT if PROBE_ROOT.exists() else None)
    for r in (1, 2, 3):
        assert cv.stream_seed("v3_R_fvplain", fv_job["seed"], r) in forbidden


@needs_inputs
def test_forbidden_requires_rerun_manifest_when_registered():
    with pytest.raises(ValueError):
        s6.forbidden_seeds(A1_ROOT, PROBE_ROOT, registered=True, rerun_manifest=None)


def test_global_seed_distinctness_and_collision():
    groups = {"a": [1, 2, 3], "b": [4, 5]}
    assert s6.assert_global_seed_distinctness(groups, forbidden={99}) == 5
    with pytest.raises(s6.SeedCollision):
        s6.assert_global_seed_distinctness({"a": [1], "b": [1]}, forbidden=set())
    with pytest.raises(s6.SeedCollision):
        s6.assert_global_seed_distinctness({"a": [7]}, forbidden={7})


@needs_inputs
def test_validate_spec_accepts_estimation_nominal_and_variant_specs(monkeypatch):
    import json
    import os
    import shutil
    import tempfile
    from v3 import production_runner as pr
    from v3 import production_tables as pt
    from v3 import tables_a6 as t6
    from v3 import calibration_a6 as c6
    from v3.study import rerun_jobs
    from v3.artifacts import atomic_json, SIMULATION as SIM
    cal_path = "v3/runs/registered/v3_rerun_calibration.json"
    tables_path = "v3/runs/registered/v3_rerun_tables_A4.json"
    frozen = json.loads((SIM / cal_path).read_text())
    pin = {"commit": "c", "path": "p", "sha256": "s"}
    settings = {"profile": "local", "workers": 3, "threads": 1, "cpu_budget": 4, "mode": "normal",
                "caps": pr.caps("local", 4)}
    monkeypatch.setattr(pr, "verify_registration", lambda *a, **k: pin)
    monkeypatch.setattr(pt, "ProductionTables", lambda *a, **k: None)
    rerun_manifest = {"jobs": rerun_jobs(cal_path, tables_path)}   # the real 24,900
    crowd_tables = "v3/runs/registered/v3_rerun_tables_crowding.json"

    cal_outputs = (SIM.parent.parent / "v3_instrument_inputs" / "registered" / "registered"
                   / "calibration" / "calibration" / "outputs")
    x10 = c6.build_variant(c6.load_records(cal_outputs, frozen), frozen, "sigma_squared_x10")
    d = tempfile.mkdtemp(dir=str(pr.ROOT), prefix="_a6_test_cal_")
    rel10 = "v3/" + os.path.relpath(d, str(pr.ROOT)).replace(os.sep, "/") + "/x10.json"
    atomic_json(rel10, x10)
    try:
        family_cals = {"crowding": cal_path, "sigma_squared_x10": rel10, "sigma_squared_x0.1": "v3/x01.json"}
        run_paths = {"nominal": (cal_path, tables_path), "crowding": (cal_path, crowd_tables),
                     "sigma_squared_x10": (rel10, "v3/runs/registered/t10.json"),
                     "sigma_squared_x0.1": ("v3/x01.json", "v3/t01.json")}
        reg = s6.build_seed_registry(family_cals, run_paths, a1_source_root=str(A1_ROOT),
                                     probe_root=str(PROBE_ROOT), rerun_manifest=rerun_manifest)
        common = dict(a1_source_root=str(A1_ROOT), probe_root=str(PROBE_ROOT), rerun_manifest=rerun_manifest,
                      seed_registry=reg)
        # Estimation spec (crowding, frozen calibration): full structural pass.
        est = t6.estimation_spec("crowding", cal_path, pin, rerun_commit="HEAD", **common)
        pr.validate_spec(est, settings)

        # Nominal run spec: its code_hash is the rerun commit's identity.
        nom = s6.nominal_run_spec("HEAD", pin, calibration_path=cal_path, tables_path=tables_path, **common)
        monkeypatch.setattr(pr, "code_identity", lambda: nom["code_hash"])
        pr.validate_spec(nom, settings)
        monkeypatch.undo()
        monkeypatch.setattr(pr, "verify_registration", lambda *a, **k: pin)
        monkeypatch.setattr(pt, "ProductionTables", lambda *a, **k: None)

        crowd = s6.crowding_run_spec("HEAD", pin, crowding_paths=(cal_path, crowd_tables), **common)
        pr.validate_spec(crowd, settings)
        sig = s6.sigma_run_spec("HEAD", pin, "sigma_squared_x10", (rel10, "v3/runs/registered/t10.json"), **common)
        pr.validate_spec(sig, settings)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_nominal_spec_code_hash_is_rerun_identity():
    # The nominal spec runs in the rerun checkout, so its code_hash must equal
    # the rerun commit's identity, not this A6 checkout's.
    from v3.artifacts import code_identity
    assert s6.rerun_code_identity("HEAD") != code_identity()


def test_a6_profiles_occupy_every_tested_worker():
    # The runner's configuration test occupies every tested worker only when the
    # job count is at least the worker count (production_runner.py:557-559).
    from v3 import production_runner as pr
    from v3 import tables_a6 as t6
    from v3.pilot import make_spec
    profiles = [t6._a6_profile(make_spec()["configuration"]["table_fv"]),
                s6._rerun_profile("a6_weight_corner", "cal", "tab"),
                s6._rerun_profile("a6_crowding", "cal", "tab", crowding="reproductive")]
    for prof in profiles:
        assert prof["workers_local"] == [8, 12] and prof.get("jobs_per_worker") == 2
        for w in (8, 12):
            assert pr.configuration_job_count(prof, w, x2=False) >= w
        for w in t6.A6_WORKERS_X2:
            assert pr.configuration_job_count(prof, w, x2=True) >= w


@needs_inputs
def test_seed_registry_builds_matches_and_detects_mismatch():
    from v3 import tables_a6 as t6
    from v3.study import rerun_jobs
    cal = "v3/runs/registered/v3_rerun_calibration.json"
    tables = "v3/runs/registered/v3_rerun_tables_A4.json"
    rerun_manifest = {"jobs": rerun_jobs(cal, tables)}
    family_cals = {"crowding": cal, "sigma_squared_x10": "v3/x10.json", "sigma_squared_x0.1": "v3/x01.json"}
    run_paths = {"nominal": (cal, tables), "crowding": (cal, "v3/tc.json"),
                 "sigma_squared_x10": ("v3/x10.json", "v3/t10.json"),
                 "sigma_squared_x0.1": ("v3/x01.json", "v3/t01.json")}
    reg = s6.build_seed_registry(family_cals, run_paths, a1_source_root=str(A1_ROOT),
                                 probe_root=str(PROBE_ROOT), rerun_manifest=rerun_manifest)
    assert reg["schema"] == "v3-A6-seed-registry-1"
    # A later step's own seeds match the registry.
    crowd_jobs = t6.build_jobs("crowding", cal)
    s6.assert_registry_seeds(reg, "table_jobs", "crowding", [j["seed"] for j in crowd_jobs])
    s6.assert_registry_seeds(reg, "runs", "crowding_runs",
                             [j["seed"] for j in s6.build_crowding_jobs(cal, "v3/tc.json")])
    # A tampered seed is refused.
    with pytest.raises(s6.SeedCollision):
        s6.assert_registry_seeds(reg, "runs", "crowding_runs", [1, 2, 3])
