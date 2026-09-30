"""A6 budget tests: the A6 ceiling (A7, 90 X2-equivalent hours), honest estimates."""
import contextlib
import math
import shutil
import tempfile
from pathlib import Path

import pytest

from v3 import budget_a6 as b6
from v3.artifacts import ROOT


@contextlib.contextmanager
def _scratch():
    d = tempfile.mkdtemp(dir=str(ROOT), prefix="_a6_test_")
    try:
        yield Path(d)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_planned_total_within_ceiling_and_no_refusal_at_plan():
    led = b6.build_ledger()
    total = b6.planned_total_hours()
    # About 82 X2-equivalent hours, now within the A7 ceiling of 90.
    assert b6.PROGRAM_CEILING_HOURS == 90.0
    assert 80 < total < b6.PROGRAM_CEILING_HOURS and led["exceeds_ceiling"] is False
    assert led["planned_total_hours"] == pytest.approx(total)
    # The first registered projection at plan does not refuse.
    for c in b6.COMPONENTS:
        assert not b6.project(led, c, "x2", 16)["refused"]


def test_refusal_past_the_ceiling():
    led = b6.build_ledger()
    # A doubled component (an overrun recorded at twice its estimate) plus the
    # remaining estimates pushes past 90, so the next projection refuses.
    over = [{"component": c, "hours": 2 * b6.planning_estimate_hours(c)}
            for c in ("crowding_tables_validation", "sigma_squared_x10_tables_validation")]
    led = b6.apply_consumption(led, over)
    with pytest.raises(ValueError) as e:
        b6.project(led, "sigma_squared_x0.1_tables_validation", "x2", 16)
    assert "budget amendment or a uniform seed reduction" in str(e.value)


def test_total_never_exceeds_ceiling_across_a_sequence():
    led = b6.build_ledger()
    entries, running = [], 0.0
    factor = {c: 1.0 for c in b6.COMPONENTS}
    factor["crowding_tables_validation"] = 3.0        # a large overrun
    factor["nominal_runs"] = 0.2                       # an underrun
    for c in b6.COMPONENTS:
        cur = b6.apply_consumption(led, entries)
        ceiling = b6.runner_ceiling_hours(cur, c, "x2")
        recorded = min(b6.planning_estimate_hours(c) * factor[c], ceiling)   # the runner stops at the ceiling
        running += recorded
        assert running <= b6.PROGRAM_CEILING_HOURS + 1e-9
        entries.append({"component": c, "hours": recorded})


def test_high_memory_fv_validation_costed_at_6200():
    # The high-memory doubled-population FV validation raises the validation
    # estimate above what 3,101 s alone would give.
    assert b6.A4_VALIDATE_FV_HIGHMEM == 6200 and b6.HIGH_MEM_WORKERS < b6.X2_PLATEAU
    val = b6._family_validation_wall_hours("crowding")
    # Recompute without the high-memory premium (FV sensitivity at 3,101) -> smaller.
    saved = b6.A4_VALIDATE_FV_HIGHMEM
    b6.A4_VALIDATE_FV_HIGHMEM = b6.A4_VALIDATE_FV
    try:
        cheaper = b6._family_validation_wall_hours("crowding")
    finally:
        b6.A4_VALIDATE_FV_HIGHMEM = saved
    assert val > cheaper


def test_x2_equivalent_charge_and_wsl_no_false_refusal():
    led = b6.build_ledger()
    # Free the later components by recording tiny consumption for all but one small
    # run component, so the last one has room.
    entries = [{"component": c, "hours": 0.5} for c in b6.COMPONENTS if c != "sigma_squared_x10_runs"]
    led = b6.apply_consumption(led, entries)
    p_x2 = b6.project(led, "sigma_squared_x10_runs", "x2", 16)
    p_wsl = b6.project(led, "sigma_squared_x10_runs", "wsl", 12)
    assert not p_x2["refused"] and not p_wsl["refused"]        # WSL does not falsely refuse
    # Charged in X2-equivalent hours: the projection is machine-independent.
    assert p_wsl["x2_equivalent_projection_hours"] == pytest.approx(p_x2["x2_equivalent_projection_hours"])
    # WSL wall is longer, and its runner ceiling is the X2-equivalent allowance
    # converted back to WSL wall hours.
    assert p_wsl["wall_projection_hours"] > p_x2["wall_projection_hours"]
    assert p_wsl["runner_ceiling_wall_hours"] == pytest.approx(p_x2["runner_ceiling_wall_hours"] / 0.37)


def test_charging_converts_wall_to_x2_equivalent():
    with _scratch() as d:
        log = d / "A6_consumption.jsonl"
        b6.append_consumption(log, "crowding_runs", 3.0, machine="wsl")   # 3 WSL wall hours
        entries = b6.read_consumption_log(log)
        assert entries[-1]["hours"] == pytest.approx(3.0 * 0.37)          # X2-equivalent
        assert entries[-1]["wall_hours"] == 3.0 and entries[-1]["machine"] == "wsl"


def test_workers_must_be_a_tested_count():
    led = b6.build_ledger()
    with pytest.raises(ValueError):
        b6.project(led, "nominal_runs", "wsl", 4)                # never 4
    with pytest.raises(ValueError):
        b6.project(led, "nominal_runs", "x2", 4)


def test_runner_ceiling_floored_down():
    led = b6.build_ledger()
    hours = b6.runner_ceiling_hours(led, "nominal_runs", "x2")
    assert b6.runner_ceiling_seconds(led, "nominal_runs", "x2") == math.floor(hours * 3600)


def test_append_only_log_and_no_rebuild():
    with _scratch() as d:
        ledger_path = d / "A6_budget.json"
        log = d / "A6_consumption.jsonl"
        b6.write_ledger(ledger_path, b6.build_ledger())
        with pytest.raises(RuntimeError):
            b6.write_ledger(ledger_path, b6.build_ledger())       # no rebuild over an existing ledger
        b6.append_consumption(log, "crowding_tables_estimation", 2.0)
        from v3.artifacts import read
        led = b6.load(read(ledger_path), log)
        assert led["consumed_hours"]["crowding_tables_estimation"] == pytest.approx(2.0)


def test_consumption_written_before_raise():
    with _scratch() as d:
        log = d / "A6_consumption.jsonl"
        with pytest.raises(ValueError):
            b6.append_consumption(log, "crowding_runs", 100.0)    # over the ceiling -> raises
        assert b6.read_consumption_log(log)[-1]["wall_hours"] == 100.0   # entry kept


def test_assert_up_to_date():
    led = b6.build_ledger()
    with pytest.raises(ValueError):
        b6.assert_up_to_date(led, ["crowding_tables_estimation"])   # not yet recorded
    led = b6.apply_consumption(led, [{"component": "crowding_tables_estimation", "hours": 1.0}])
    assert b6.assert_up_to_date(led, ["crowding_tables_estimation"])
