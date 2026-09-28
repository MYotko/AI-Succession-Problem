"""A1 diagnostics and exact frozen-calibration compatibility, no private inputs."""
from copy import deepcopy
import math
import statistics
import pytest
import numpy as np
from v3.artifacts import digest, seal, file_hash, atomic_json
from v3.diagnose_tables import row_metrics, contrast
from v3 import calibration, calibration_compatibility as compatibility
from v3.continuation import fit_transitions


def screen_row():
    return {"rule_id": "balanced", "kernel_hash": "k", "calibration_hash": "c", "scoring": {"alpha": 1., "capability": 1., "kappa": 8.},
            "status": "not_estimable", "route": "plain", "flow_range": 10., "surviving_fraction": .4,
            "half_window_means": [1., 2.], "lambda_f": {"mean": 1.5, "half_width": .2, "replicates": [1.5] * 6},
            "screens": {"route_applicable": False, "flow_half_width": True, "half_window_drift": False, "continuation": False},
            "continuation": {"heldout_coverage": .85, "bellman_residual_empirical": .75, "training_fixed_point_converged": True,
                             "iterations": 100, "entries": [{"training_visits": 4, "heldout_visits": 2}]}}


def test_audit_quantifies_each_failure_and_does_not_gate_fv_at_half_survival():
    row = screen_row()
    metrics = row_metrics(row)
    assert metrics["excess"]["half_window_drift"] == .5
    assert metrics["excess"]["bellman_residual"] == .25
    assert metrics["excess"]["continuation_coverage"] == pytest.approx(.05)
    assert metrics["excess"]["survival_fraction"] == pytest.approx(.1)
    assert metrics["excess"]["flow_half_width"] == pytest.approx(-.3)
    row["route"] = "fv"
    assert row_metrics(row)["excess"]["survival_fraction"] is None


def test_contrast_is_computed_even_when_other_row_failed_a_different_screen():
    primary, other = screen_row(), screen_row()
    other["lambda_f"].update(mean=2.1, replicates=[2.1] * 6)
    result = contrast(primary, other)
    assert result["excess"] == pytest.approx(.1)
    assert not result["contrast_passed"] and result["other_status"] == "not_estimable"
    other["lambda_f"].update(mean=1.5, replicates=[1., 2.] * 3)
    result = contrast(primary, other)
    assert result["half_width"] == pytest.approx(2.015 * math.sqrt(statistics.variance([1., 2.] * 3) / 6))


def compatible_fixture(tmp_path, monkeypatch):
    monkeypatch.setattr(compatibility, "ROOT", tmp_path)
    monkeypatch.setattr(compatibility, "SIMULATION", tmp_path)
    dep = tmp_path / "dependency.py"
    dep.write_text("unchanged scientific dependency\n", encoding="utf-8")
    payload = {"schema": "v3-calibration-1", "code_hash": "historical", "fixture": False, "tag": "v3_calibration", "trajectories": 50, "steps": 500,
               "values": {"center": [0.] * 10, "sigma_squared": .1, "n_ref": 200., "epsilon_n": .01, "epsilon_e": .01, "epsilon_l": .001, "c_e": 2.5}}
    document = seal(payload)
    record = {"calibration_sha256": document["sha256"], "old_code_hash": "historical", "values_sha256": digest(payload["values"]),
              "dependency_sha256": {"dependency.py": compatibility.dependency_hash(dep)},
              "function_sha256": {n: compatibility.function_hash(getattr(calibration, n)) for n in ("run_seed", "freeze")}}
    atomic_json(tmp_path / "calibration_compatibility_A1.json", record)
    return document, dep


def test_only_exact_frozen_calibration_with_unchanged_scientific_dependencies_is_reused(tmp_path, monkeypatch):
    document, dep = compatible_fixture(tmp_path, monkeypatch)
    assert calibration.validate_calibration(document, registered=True)["code_hash"] == "historical"
    dep.write_bytes(dep.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    assert calibration.validate_calibration(document, registered=True)["code_hash"] == "historical"
    changed = deepcopy(document["payload"])
    changed["values"]["n_ref"] = 201.
    with pytest.raises(ValueError, match="stale"):
        calibration.validate_calibration(seal(changed), registered=True)
    dep.write_text("changed scientific dependency\n", encoding="utf-8")
    with pytest.raises(ValueError, match="stale"):
        calibration.validate_calibration(document, registered=True)


def test_calibration_compatibility_does_not_bypass_fixture_or_hash_guards(tmp_path, monkeypatch):
    document, _ = compatible_fixture(tmp_path, monkeypatch)
    document["payload"]["fixture"] = True
    with pytest.raises(ValueError, match="hash"):
        calibration.validate_calibration(document, registered=True)
    assert not compatibility.compatible(seal(document["payload"]))


def test_continuation_validates_published_domain_and_preserves_original_diagnostic():
    before = np.zeros((1, 18, 6), dtype=int)
    after = np.zeros_like(before)
    before[0, [0, 3, 12], 0] = 1
    reward = np.zeros((1, 18))
    reward[0, 12] = 9
    result = fit_transitions(before, after, reward, np.zeros_like(reward, bool), np.repeat(np.arange(6), 3), 0., 10.)
    worst = result["legacy_all_training_bins"]["largest_residual_bins"][0]
    assert worst["bin"] == [1, 0, 0, 0, 0, 0]
    assert worst["training_visits"] == 2 and worst["heldout_visits"] == 1
    assert not worst["published"]
    assert result["legacy_all_training_bins"]["bellman_residual_empirical"] == pytest.approx(9 * (1 - math.exp(-.01)), abs=1e-6)
    assert result["bellman_residual_empirical"] < 1e-6
    assert result["heldout_coverage"] == pytest.approx(5 / 6)  # Still fails 90%.
    assert result["legacy_all_training_bins"]["heldout_coverage"] == 1.
    assert result["unpublished_source_heldout"] == 1


def test_bad_published_bin_still_fails_maximum_residual_screen():
    before = np.zeros((1, 30, 6), dtype=int)
    before[0, :, 0] = np.tile([0, 0, 1, 2, 2], 6)
    after = before.copy()
    after[0, [2, 7, 12, 17], 0] = 0
    after[0, [22, 27], 0] = 2
    reward = (after[:, :, 0] == 2).astype(float) * 10
    result = fit_transitions(before, after, reward, np.zeros_like(reward, bool), np.repeat(np.arange(6), 5), 0., 10.)
    assert result["heldout_coverage"] == 1.
    assert result["largest_residual_bins"][0]["training_visits"] == 4
    assert result["bellman_residual_empirical"] == pytest.approx(10., abs=1e-6)
    assert result["bellman_residual_empirical"] > .05 * 10.


def test_unpublished_successors_reduce_coverage_but_extinction_remains_exact():
    before = np.zeros((1, 18, 6), dtype=int)
    after = before.copy()
    after[0, [12, 13], 0] = 1
    reward = np.zeros((1, 18))
    dead = np.zeros_like(reward, bool)
    dead[0, 13] = True
    result = fit_transitions(before, after, reward, dead, np.repeat(np.arange(6), 3), 0., 10.)
    assert result["heldout_coverage"] == pytest.approx(5 / 6)
    assert result["unpublished_successor_heldout"] == 1


def test_compatibility_record_is_part_of_code_identity_and_must_be_committed(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from v3 import artifacts
    assert "v3/calibration_compatibility_A1.json" in artifacts.source_manifest()
    note = tmp_path / "note.md"
    note.write_bytes(b"pinned")
    pin = {"commit": "commit", "path": "note.md", "sha256": file_hash(note)}
    def fake_git(command, **kwargs):
        if "show" in command:
            return SimpleNamespace(stdout=note.read_bytes())
        if "ls-files" in command:
            assert "simulation/v3/calibration_compatibility_A1.json" in command
            return SimpleNamespace(stdout=b"simulation/v3/calibration_compatibility_A1.json")
        return SimpleNamespace(stdout=b"")
    monkeypatch.setattr(artifacts.subprocess, "run", fake_git)
    with pytest.raises(RuntimeError, match="committed and clean"):
        artifacts.verify_registration(pin, tmp_path)


def test_a1_changes_only_primary_effort_and_retains_exact_sensitivity_family():
    from v3.offline_estimator import settings_for, SENSITIVITY_RULES, SENSITIVITY_RR
    from v3.study import table_jobs
    primary = settings_for()
    assert primary == {"groups": 6, "runs_per_group": 64, "particles": 256, "burn": 1024, "measure": 2048}
    assert settings_for("double_population") == {**primary, "runs_per_group": 128, "particles": 512}
    assert settings_for("double_length") == {**primary, "burn": 2048, "measure": 4096}
    jobs = table_jobs()
    assert len(jobs) == 343
    pairs = {(j["config"]["rule_id"], j["config"]["kernel"]["reproduction_rate"]) for j in jobs if j["config"]["setting_name"] != "primary"}
    assert pairs == {(r, rr) for r in SENSITIVITY_RULES for rr in SENSITIVITY_RR}


def test_assembly_preserves_primary_failure_and_exposes_a_passing_contrast_with_failed_counterpart(tmp_path):
    from v3.artifacts import code_identity
    from v3.study import assemble_tables
    primary = screen_row()
    primary["reason"] = "original primary failure"
    outputs = []
    for setting in ("primary", "double_population", "double_length"):
        row = deepcopy(primary)
        if setting == "double_length":
            row["status"] = "estimated"
        outputs.append({"code_hash": code_identity(),
                        "job": {"tag": "validation", "config": {"setting_name": setting, "kernel": {"reproduction_rate": .055}}},
                        "result": {"calibration_hash": "c", "fixture_calibration": True, "rows": [row]}})
    document = assemble_tables(outputs, {"sha256": "c"}, tmp_path / "table.json")
    result = next(iter(document["payload"]["rows"].values()))["payload"]
    assert result["primary_status"] == "not_estimable" and result["primary_reason"] == "original primary failure"
    counterpart = next(c for c in result["sensitivity"]["contrasts"] if c["setting"] == "double_population")
    assert counterpart["numerical_contrast_passed"] and not counterpart["passed"]
    assert counterpart["other_status"] == "not_estimable"
    assert not result["sensitivity"]["passed"] and result["status"] == "not_estimable"


# Artifacts stay inside the authorized tree even with default pytest options.
from test_v3_paths import tmp_path
