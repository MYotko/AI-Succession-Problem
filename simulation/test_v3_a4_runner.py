"""A4 runner-path suite tests: the memory cap stays fixed within a phase (the
round-4 regression), the guard halts with no active task, the cap lowers after a
measured peak, a projection stop, and a tiny launch + resume through all phases.
Fast: fixture jobs for the memory checks; one small synthetic launch."""
import time
import shutil
from pathlib import Path
import tempfile

import pytest

from v3 import production_runner as pr
from v3.artifacts import ROOT, code_identity, atomic_json, stable_job, read, seal
from v3 import continuation_validation as cv
from v3 import table_validation_a4 as a4


def _settings(cpu_budget):
    return {"profile": "local", "workers": 8, "threads": 1, "cpu_budget": cpu_budget, "mode": "normal",
            "caps": pr.caps("local", cpu_budget)}


def _control(root):
    atomic_json(root / "control.json", {"mode": "normal", "max_workers": 8, "stop_dispatch": False, "interrupt_now": False})


def test_dispatch_holds_memory_cap_when_memavailable_drops(monkeypatch):
    # Live MemAvailable already excludes running tasks; the cap must NOT be
    # recomputed from it (the round-4 bug). With a fixed cap of 6, max active
    # must reach 6, not the ~3 a live recompute at 4 GB would give.
    monkeypatch.setattr(pr, "mem_available_bytes", lambda: 4_000_000_000)
    jobs = [stable_job("fixture", {"seconds": 0.5}, "validation", i) for i in range(8)]
    with tempfile.TemporaryDirectory(dir=ROOT, prefix="_a4_cap_") as d:
        root = Path(d)
        _control(root)
        result = pr.dispatch(root / "p", jobs, code_identity(), _settings(10), time.time() + 60,
                             fixed={"workers": 8, "threads": 1}, control_root=root,
                             memory_cap=6, memory_estimate_gb=1.0)
        assert result["completed"] == 8
        assert result["maximum_active"] == 6  # fixed cap honored, not shrunk to 3


def test_dispatch_guard_halts_with_no_active_task(monkeypatch):
    monkeypatch.setattr(pr, "mem_available_bytes", lambda: 1_000_000_000)  # 1 GB
    jobs = [stable_job("fixture", {"seconds": 0.1}, "validation", i) for i in range(2)]
    with tempfile.TemporaryDirectory(dir=ROOT, prefix="_a4_guard_") as d:
        root = Path(d)
        _control(root)
        with pytest.raises(RuntimeError, match="memory guard"):
            pr.dispatch(root / "p", jobs, code_identity(), _settings(10), time.time() + 60,
                        fixed={"workers": 4, "threads": 1}, control_root=root,
                        memory_cap=4, memory_estimate_gb=10.0)  # 1.2*10 = 12 GB > 1 GB available


def test_cap_lowers_after_measured_peak_arithmetic():
    # The FV primary cap of 9 lowers to 4 if a peak doubles the 9.5 GB estimate;
    # a smaller peak never raises the cap.
    assert pr.lowered_cap(9, 9.5, 19.0) == 4
    assert pr.lowered_cap(9, 9.5, 5.0) == 9      # never raises
    assert pr.lowered_cap(None, 9.5, 19.0) is None
    assert pr.lowered_cap(4, 19.0, 19.0) == 4


def test_successive_peaks_do_not_compound():
    # Reviewer regression: each raised estimate is applied to the phase's
    # ORIGINAL memory cap. FV primary peaks of 9.6 to 10.1 GB against a 9.5 GB
    # estimate and an original cap of 9 must settle at 8, not fall to 3.
    cap = 9
    for peak in (9.6, 9.7, 9.8, 9.9, 10.0, 10.1):
        cap = pr.next_memory_cap(9, cap, 9.5, peak)
    assert cap == 8
    # A plain phase whose memory cap (19) never binds keeps it through peaks of
    # 5.2 to 5.4 GB against a 4.75 GB estimate: 19 * 4.75 / 5.4 = 16.7, so 16.
    cap = 19
    for peak in (5.2, 5.3, 5.4):
        cap = pr.next_memory_cap(19, cap, 4.75, peak)
    assert cap == 16
    # The cap never rises when a later peak is lower, and None stays None.
    assert pr.next_memory_cap(9, 5, 9.5, 9.6) == 5
    assert pr.next_memory_cap(None, None, 9.5, 12.0) is None


def test_worker_records_peak_rss():
    # The durable output carries peak_rss_bytes, which dispatch reads to raise
    # a phase estimate.
    job = stable_job("fixture", {"seconds": 0.05}, "validation", 0)
    with tempfile.TemporaryDirectory(dir=ROOT, prefix="_a4_rss_") as d:
        root = Path(d)
        _control(root)
        pr.dispatch(root / "p", [job], code_identity(), _settings(4), time.time() + 60,
                    fixed={"workers": 1, "threads": 1}, control_root=root)
        out = read(root / "p" / "outputs" / (job["id"] + ".json"))
        assert "peak_rss_bytes" in out


def test_projection_stop_before_phase():
    from v3.production_runner import a4_projection
    a1cfg = {"config": {"settings": {"runs_per_group": 64, "particles": 256, "burn": 1024, "measure": 2048}}}
    def mkjob(i):
        cfg = {"phase": "census", "stage": "census", "route": "plain", "a1_job": {"id": "a1_%d" % i, **a1cfg},
               "a1_source_code_hash": "h", "plan_hash": "P", "seed": i}
        return stable_job("a4_census", cfg, "v3_tables", i)
    spec = {"phases": ["census"], "jobs": [mkjob(1), mkjob(2)],
            "configuration": {"census": {"config": {"route": "plain", "settings_override": {"census_measure": 44},
                                                    "a1_job": {"config": {"settings": {"runs_per_group": 64}}}}}}}
    config = {"census": [{"job_seconds": [100.0]}]}
    with tempfile.TemporaryDirectory(dir=ROOT, prefix="_a4_stop_") as d:
        proj = a4_projection(spec, config, {"census": 1}, Path(d), code_identity(), 0, 0.0, 1.0)
        assert proj["fits"] is False  # 1 s budget, work >> 1 s


A1_ROOT = Path(r"C:\Users\matty\Dev\v3_instrument_inputs\registered_A1")
CAL = "v3/runs/registered/v3_rerun_calibration.json"
PROBE = Path(r"C:\Users\matty\Dev\v3_instrument_inputs\a3_probe")


@pytest.mark.skipif(not (A1_ROOT / "tables_A1_manifest.json").exists() or not PROBE.exists(),
                    reason="A1 records or probe not present")
def test_launch_all_phases_and_resume(tmp_path):
    # One plain A1 job -> fit + 3 validate + census across four phases (FV phases
    # empty). Minimal configuration profile so launch is quick. Then resume.
    from v3.production_runner import completed, launch
    from v3.production_tables import ProductionTables
    base = ROOT / ("_a4_launch_" + tmp_path.name)
    if base.exists():
        shutil.rmtree(base)
    src = base / "source"
    src_code = a4._source_code_hash(A1_ROOT)
    jobs = {j["id"]: j for j in a4.selected_a1_jobs(A1_ROOT)}
    plain_id = next(jid for jid in jobs if completed(A1_ROOT / "tables_A1/table", jobs[jid], src_code)["result"]["route"] == "plain")
    for sub in ("outputs", "records"):
        (src / "tables_A1/table" / sub).mkdir(parents=True, exist_ok=True)
        shutil.copy(A1_ROOT / "tables_A1/table" / sub / (plain_id + ".json"), src / "tables_A1/table" / sub / (plain_id + ".json"))
    atomic_json(src / "tables_A1_manifest.json", seal({"jobs": [jobs[plain_id]], "source_family": {"code_hash": src_code}, "tag": "v3_tables"}))
    atomic_json(src / "v3_rerun_tables_A1.json", {"placeholder": True})
    override = {"groups": 4, "burn": 8, "measure": 16, "runs_per_group": 16, "particles": 16, "census_measure": 30}
    plan = a4.prepare(src, CAL, registration=None, wall_hours=48, a3_probe_root=PROBE, settings_override=override)
    # Trim the configuration to a single tiny candidate so launch is quick.
    for phase in plan["configuration"]:
        plan["configuration"][phase].update(workers_local=[1], jobs_local=1)
    atomic_json(base / "plan.json", seal(plan))
    settings = {"profile": "local", "workers": 2, "threads": 1, "cpu_budget": 4, "mode": "normal"}
    result = launch(base / "plan.json", base / "run", settings)
    assert result["complete"], result
    # Resume: a second launch reuses everything and still completes.
    again = launch(base / "plan.json", base / "run", settings)
    assert again["complete"]
    cal = read(a4.SIMULATION / CAL)
    out = a4.publish(plan, base / "run", src, cal, base / "tables_A4.json", registered=False)
    ProductionTables(base / "tables_A4.json", calibration_hash=cal["sha256"])
    rep = a4.report(base / "tables_A4.json", base / "report_A4.json")
    assert out["detail_rows"] >= 1 and "rows_covered" in rep
    shutil.rmtree(base)
