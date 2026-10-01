"""A5 runner-path tests: stage determinism and identity through execute(), a full
tiny launch (config test, staged projection, memory cap and per-phase
nondeterminism recheck) with resume, publish and report, and a check that the
non-A5 runner path is unchanged.

Requires the A1 records, the D26 probe records and the calibration; skips
otherwise. Fast: one FV table at tiny settings.
"""
import shutil
import time
from pathlib import Path

import pytest

from v3.artifacts import ROOT, SIMULATION, atomic_json, read, seal, unseal, digest, code_identity, stable_job
from v3.production_runner import launch, dispatch, caps, completed, execute
from v3 import table_labels_a5 as a5

from test_v3_a5_publication import build_publication, A1_ROOT, PROBE, CAL, OVERRIDE, _prepare, pytestmark  # noqa: F401


def _fresh(name):
    base = ROOT / ("_a5_run_" + name)
    if base.exists():
        shutil.rmtree(base)
    return base


def test_stage_determinism_and_identity():
    base = _fresh("det")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)
        job = plan["jobs"][0]
        r1 = execute(job, root=None)
        r2 = execute(job, root=None)
        assert digest(r1) == digest(r2)                              # deterministic
        c = job["config"]
        assert r1["a1_job_id"] == c["a1_job"]["id"]
        assert r1["stream_seed"] == int(c["seed"]) and r1["plan_hash"] == plan["plan_hash"]
        assert r1["stage"] == "a5_fvplain" and r1["route"] == "plain"
    finally:
        shutil.rmtree(base)


def test_launch_resume_publish_report():
    base = _fresh("launch")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)
        # Trim the configuration to a single tiny candidate so launch is quick.
        plan["configuration"][a5.PHASE].update(workers_local=[1], jobs_local=1)
        atomic_json(base / "plan.json", seal(plan))
        settings = {"profile": "local", "workers": 2, "threads": 1, "cpu_budget": 4, "mode": "normal"}
        run = base / "run"
        result = launch(base / "plan.json", run, settings)
        assert result["complete"], result
        # The staged nondeterminism recheck ran for the A5 phase.
        assert read(run / a5.PHASE / "nondeterminism_check.json")["matched"] is True
        # Resume reuses everything and still completes.
        again = launch(base / "plan.json", run, settings)
        assert again["complete"]
        out = a5.publish(plan, run, pub["a4_run"], pub["src"], pub["cal"], base / "labels.json", registered=False)
        assert out["rows"] >= 1 and out["M"] == plan["M"]
        rep = a5.report(base / "labels.json", base / "report.json")
        assert rep["rows"] >= 1
    finally:
        shutil.rmtree(base)


def test_stop_in_flight_then_resume_skips_completed():
    import json
    import threading
    from v3.artifacts import digest, file_hash
    base = _fresh("resume")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)
        settings = {"profile": "local", "workers": 2, "threads": 1, "cpu_budget": 4, "mode": "normal", "caps": caps("local", 4)}
        root = base / "run"
        root.mkdir(parents=True, exist_ok=True)
        atomic_json(root / "control.json", {"mode": "normal", "max_workers": 2, "stop_dispatch": False, "interrupt_now": False})
        phase = root / a5.PHASE

        # A watcher sets interrupt_now once the first job completes, so the stop
        # lands with other jobs still in flight.
        stop_watch = {"go": True}

        def watcher():
            while stop_watch["go"]:
                events = phase / "events.jsonl"
                if events.exists() and any('"complete"' in ln for ln in events.read_text().splitlines()):
                    ctl = read(root / "control.json")
                    ctl["interrupt_now"] = True
                    atomic_json(root / "control.json", ctl)
                    return
                time.sleep(0.02)
        t = threading.Thread(target=watcher)
        t.start()
        a = dispatch(phase, plan["jobs"], code_identity(), settings, time.time() + 300,
                     fixed={"workers": 2, "threads": 1}, control_root=root)
        stop_watch["go"] = False
        t.join()
        events = [json.loads(ln) for ln in (phase / "events.jsonl").read_text().splitlines()]
        assert sum(e["event"] == "complete" for e in events) >= 1                 # at least one finished
        assert sum(e["event"] == "restart_required" for e in events) >= 1         # at least one interrupted
        assert a["reason"] == "interrupted" and a["completed"] < len(plan["jobs"])
        done_after_stop = {j["id"]: file_hash(phase / "outputs" / (j["id"] + ".json"))
                           for j in plan["jobs"] if completed(phase, j, code_identity()) is not None}
        assert done_after_stop  # something completed before the stop

        # Resume: clear the interrupt, finish the rest.
        atomic_json(root / "control.json", {"mode": "normal", "max_workers": 2, "stop_dispatch": False, "interrupt_now": False})
        b = dispatch(phase, plan["jobs"], code_identity(), settings, time.time() + 300,
                     fixed={"workers": 2, "threads": 1}, control_root=root)
        assert b["completed"] == len(plan["jobs"])
        # Completed-before-stop outputs are byte-for-byte unchanged (skipped).
        for jid, h in done_after_stop.items():
            assert file_hash(phase / "outputs" / (jid + ".json")) == h

        # A clean uninterrupted run, then publish both and compare the record. The
        # scientific content is byte-identical; only stage_output_sha256 differs,
        # because the worker output files carry per-run timestamps.
        clean = base / "clean"
        clean.mkdir(parents=True, exist_ok=True)
        atomic_json(clean / "control.json", {"mode": "normal", "max_workers": 2, "stop_dispatch": False, "interrupt_now": False})
        dispatch(clean / a5.PHASE, plan["jobs"], code_identity(), settings, time.time() + 300,
                 fixed={"workers": 2, "threads": 1}, control_root=clean)
        r_resumed = a5.publish(plan, root, pub["a4_run"], pub["src"], pub["cal"], base / "labels_resumed.json", registered=False)
        r_clean = a5.publish(plan, clean, pub["a4_run"], pub["src"], pub["cal"], base / "labels_clean.json", registered=False)
        assert r_resumed == r_clean
        resumed = read(base / "labels_resumed.json")["payload"]
        clean_rec = read(base / "labels_clean.json")["payload"]
        for k in ("rows", "totals", "M", "stream_seeds"):
            assert digest(resumed[k]) == digest(clean_rec[k])
    finally:
        shutil.rmtree(base)


def test_non_a5_runner_path_unchanged():
    # A plain fixture dispatch still records the runner seed (a5 seed labelling
    # only applies to a4_/a5_ kinds), and completes normally.
    base = _fresh("other")
    try:
        base.mkdir(parents=True, exist_ok=True)
        atomic_json(base / "control.json", {"mode": "normal", "max_workers": 2, "stop_dispatch": False, "interrupt_now": False})
        jobs = [stable_job("fixture", {"seconds": 0.05}, "validation", i) for i in range(2)]
        settings = {"profile": "local", "workers": 2, "threads": 1, "cpu_budget": 4, "mode": "normal", "caps": caps("local", 4)}
        result = dispatch(base / "p", jobs, code_identity(), settings, time.time() + 60,
                          fixed={"workers": 2, "threads": 1}, control_root=base)
        assert result["completed"] == 2
        events = (base / "p" / "events.jsonl").read_text().splitlines()
        dispatched = [__import__("json").loads(e) for e in events if '"dispatch"' in e]
        assert dispatched and all("seed" in e and not e.get("runner_seed_unused") for e in dispatched)
    finally:
        shutil.rmtree(base)
