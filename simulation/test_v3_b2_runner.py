"""Real local spawn/resume/mode checks and mocked X2 service lifecycle."""
from copy import deepcopy
import hashlib
from pathlib import Path
import subprocess
import threading
import time
import pytest
from v3.artifacts import ROOT, atomic_json, read, seal, code_identity, stable_job, lease, verify_registration, file_hash
from v3 import production_runner as runner
from v3 import service


def local_settings(workers=2, budget=4, mode="normal"):
    return {"profile": "local", "workers": workers, "threads": 1, "cpu_budget": budget, "mode": mode, "caps": runner.caps("local", budget)}


def control(root, mode="normal"):
    atomic_json(root / "control.json", {"mode": mode, "max_workers": 3, "stop_dispatch": False, "interrupt_now": False})


def measured(workers=(1, 2)):
    return [{"workers": w, "threads": 1, "completed": w * 10, "wall_seconds": 10, "valid": True} for w in workers]


def test_configuration_choice_caps_and_two_thread_slot_budget():
    assert runner.caps("x2", 32) == {"normal": 31, "work": 28, "configuration": 32}
    assert runner.caps("local", 16)["work"] == 12
    choices = measured((8, 12, 16, 24, 32))
    assert runner.choose(choices, 31, 32)["workers"] == 24
    assert runner.choose(choices, 28, 32)["workers"] == 24
    choices += [{"workers": 24, "threads": 2, "completed": 1000, "wall_seconds": 10, "valid": True}]
    assert runner.choose(choices, 31, 32, 2)["threads"] == 1
    tied = [{"workers": w, "threads": 1, "completed": 100, "wall_seconds": t, "valid": True} for w, t in ((8, 10), (12, 9.8))]
    assert runner.choose(tied, 31, 32)["workers"] == 8


def test_real_configuration_work_is_separate_from_results(tmp_path):
    control(tmp_path)
    profile = {"kind": "calibration", "config": {"steps": 4, "n_agents": 200}, "workers_local": [1, 2],
               "workers_x2": [8, 12, 16, 24, 32], "jobs_local": 2, "jobs_x2": 32, "threads": [1], "rounds": 1}
    result = runner.configuration_test(tmp_path, "calibration", profile, local_settings(), time.time() + 30, 1)
    assert len(result) == 2 and all(r["valid"] for r in result)
    for path in (tmp_path / "configuration").rglob("outputs/*.json"):
        output = read(path)
        assert output["job"]["tag"] == "configuration"
        assert output["runtime"]["threads_verified"][0]["effective"] == 1
    assert not (tmp_path / "outputs").exists()


def test_deadline_restart_and_exact_completed_output_resumption(tmp_path):
    control(tmp_path)
    jobs = [stable_job("fixture", {"seconds": .2}, "validation", i) for i in range(3)]
    code = code_identity()
    first = runner.dispatch(tmp_path, jobs[:1], code, local_settings(), time.time() + 15, measurements=measured())
    assert first["completed"] == 1
    preserved = file_hash(tmp_path / "outputs" / (jobs[0]["id"] + ".json"))
    interrupted = runner.dispatch(tmp_path, jobs, code, local_settings(), time.time() + .1, measurements=measured())
    assert interrupted["reason"] == "deadline" and interrupted["completed"] == 1
    assert not read(tmp_path / "active.json")["pids"]
    resumed = runner.dispatch(tmp_path, list(reversed(jobs)), code, local_settings(), time.time() + 15, measurements=measured())
    assert resumed["completed"] == 3 and resumed["maximum_active"] <= 2
    assert file_hash(tmp_path / "outputs" / (jobs[0]["id"] + ".json")) == preserved
    assert all(runner.completed(tmp_path, j, code)["result"]["seed"] == j["seed"] for j in jobs)
    assert "restart_required" in (tmp_path / "events.jsonl").read_text()
    damaged = tmp_path / "outputs" / (jobs[1]["id"] + ".json")
    atomic_json(damaged, {"partial": True})
    with pytest.raises(RuntimeError, match="identity"):
        runner.completed(tmp_path, jobs[1], code)


def test_live_work_mode_drains_without_killing_then_normal_resumes(tmp_path):
    control(tmp_path)
    jobs = [stable_job("fixture", {"seconds": .35}, "validation", i) for i in range(10)]
    observed = []
    def steer():
        deadline = time.time() + 20
        while time.time() < deadline:
            if (tmp_path / "status.json").exists() and read(tmp_path / "status.json")["running"] >= 3:
                break
            time.sleep(.02)
        control(tmp_path, "work")
        while time.time() < deadline:
            status = read(tmp_path / "status.json")
            if status["mode"] == "work" and status["running"] <= 1:
                observed.append(status["running"])
                control(tmp_path, "normal")
                return
            time.sleep(.02)
    thread = threading.Thread(target=steer)
    thread.start()
    result = runner.dispatch(tmp_path, jobs, code_identity(), local_settings(3), time.time() + 25, measurements=measured((1, 3)))
    thread.join(2)
    assert observed and result["completed"] == 10 and result["maximum_active"] <= 3
    events = [__import__("json").loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    assert not any(e["event"] == "restart_required" for e in events)
    assert all(e["active"] <= 1 for e in events if e["event"] == "dispatch" and e["mode"] == "work")
    assert read(tmp_path / "control.json")["mode"] == "normal"


@pytest.mark.parametrize("failure", [None, "down", "work", "up"])
def test_service_lease_always_restores_after_mocked_failures(tmp_path, monkeypatch, failure):
    calls = []
    monkeypatch.setattr(service.platform, "node", lambda: "yotko-evo-x2")
    monkeypatch.setattr(service.platform, "system", lambda: "Linux")
    monkeypatch.setattr(runner, "validate_spec", lambda spec, settings: None)
    def command(root, action):
        calls.append(action)
        return int(failure == action)
    def launch(*args, **kwargs):
        assert kwargs["service_record"]["down_exit_code"] == 0
        if failure == "work":
            raise RuntimeError("work failed")
        return {"complete": True}
    monkeypatch.setattr(service, "command", command)
    monkeypatch.setattr(runner, "launch", launch)
    spec_path = tmp_path / "spec.json"
    atomic_json(spec_path, seal({"wall_seconds": 500}))
    settings = {"profile": "x2", "cpu_budget": 32}
    if failure:
        with pytest.raises(RuntimeError):
            service.run_with_service(spec_path, tmp_path / "run", settings)
    else:
        assert service.run_with_service(spec_path, tmp_path / "run", settings)["complete"]
    assert calls == ["down", "up"]
    assert read(tmp_path / "run" / "service.json")["up_exit_code"] == int(failure == "up")


def test_lease_excludes_concurrent_service_owners(tmp_path):
    with lease(tmp_path / "lease.lock"):
        with pytest.raises((RuntimeError, OSError)):
            with lease(tmp_path / "lease.lock"):
                raise AssertionError("second lease acquired")


def test_registration_pin_is_required_and_verified_against_git(tmp_path, monkeypatch):
    with pytest.raises(RuntimeError, match="pinned"):
        verify_registration(None)
    plan = tmp_path / "plan.md"
    plan.write_bytes(b"frozen plan\n")
    pin = {"commit": "a" * 40, "path": "plan.md", "sha256": hashlib.sha256(plan.read_bytes()).hexdigest()}
    calls = []
    def git(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout=plan.read_bytes() if "show" in command else b"")
    monkeypatch.setattr("v3.artifacts.subprocess.run", git)
    assert verify_registration(pin, tmp_path) == pin
    assert any("--is-ancestor" in c for c in calls)
    with pytest.raises(RuntimeError, match="stale"):
        verify_registration({**pin, "sha256": "0" * 64}, tmp_path)


def test_registered_launch_rejects_fixture_before_any_dispatch(tmp_path, monkeypatch):
    job = stable_job("rerun", {"steps": 500}, "v3_rerun", 0)
    spec = {"code_hash": code_identity(), "registered": True, "jobs": [job]}
    with pytest.raises(RuntimeError, match="pinned"):
        runner.validate_spec(spec, local_settings())
    monkeypatch.setattr(runner, "verify_registration", lambda pin: {"verified": True})
    with pytest.raises(RuntimeError, match="calibration"):
        runner.validate_spec(spec, local_settings())


def test_expired_batch_budget_cannot_be_reset_on_resume(tmp_path):
    spec = {"code_hash": code_identity(), "registered": False, "jobs": [], "wall_seconds": 500, "configuration": {}, "phases": []}
    path = tmp_path / "spec.json"
    atomic_json(path, seal(spec))
    root = tmp_path / "run"
    atomic_json(root / "budget.json", {"deadline_epoch": time.time() - 1})
    with pytest.raises(RuntimeError, match="expired"):
        runner.launch(path, root, local_settings())
