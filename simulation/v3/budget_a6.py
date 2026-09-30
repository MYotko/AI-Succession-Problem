"""A6 budget: the A6 ceiling in X2-equivalent wall hours, honest estimates, slack-aware ceilings.

Amendment A6, 2026-09-29; ceiling raised to 90 X2-equivalent wall hours by
amendment A7 (operator decision D34, 2026-09-30). ``PROGRAM_CEILING_HOURS`` is the
single source. One total covers the three variant table families (estimation and
validation) and every sensitivity run. Each planned component carries an honest
planning estimate from the committed measurements with one realism factor,
including the high-memory Fleming-Viot validation at 6,200 s on a memory-capped
worker count, and each launch's own configuration-test and cleanup reserve. The
planned total may exceed the ceiling; that is correct and visible, and the first
registered projection then refuses, so the operator chooses a budget amendment or
a uniform seed reduction before any registered A6 run.

The budget is in X2-equivalent hours. A launch on another bit-identical machine is
projected and charged in X2-equivalent hours (wall hours times the machine's
measured relative throughput), and its runner wall ceiling is the X2-equivalent
allowance converted back to that machine's wall hours. Consumption is an
append-only JSONL log, separate from the ledger; an entry is written before any
check that might raise.

New module only. It computes no survival, extinction or fire rate.
"""
import json
import math
from pathlib import Path

from .artifacts import scoped, seal, unseal

PROGRAM_CEILING_HOURS = 90.0     # X2-equivalent wall hours; raised from 72 by amendment A7 (D34)
REALISM = 1.35
X2_PLATEAU = 16
HIGH_MEM_WORKERS = 5          # the memory cap on the ~19 GB doubled-population FV validation (A4)

# Machines: aggregate throughput relative to the X2 at its plateau, and the
# worker counts A6's configuration profiles test (never 4).
MACHINES = {"x2": {"relative": 1.0, "workers": (8, 12, 16, 24, 32)},
            "wsl": {"relative": 0.37, "workers": (8, 12)}}

# Readiness note (2026-09-29) measured per-task worker seconds.
EST_PLAIN, EST_FV = 202, 1577
EST_PLAIN_SENS, EST_FV_SENS = 695, 3751
A4_FIT, A4_VALIDATE_PLAIN, A4_VALIDATE_FV = 870, 1026, 3101
A4_VALIDATE_FV_HIGHMEM = 6200      # the high-memory doubled-population FV validation
A4_CENSUS = 150
PLAIN_VALIDATE_REPLICATES = 3
FV_ROUTE_FRACTION = 201 / 225
RUN_HOURS_TOTAL = 12.0

FAMILIES = ("crowding", "sigma_squared_x10", "sigma_squared_x0.1")
FAMILY_JOBS = {"crowding": (225, 12), "sigma_squared_x10": (125, 6), "sigma_squared_x0.1": (125, 6)}
RUN_EQUIVALENTS = {"nominal_runs": 17600 + 1800 * 2, "crowding_runs": 4400,
                   "sigma_squared_x10_runs": 500, "sigma_squared_x0.1_runs": 500}
TOTAL_RUN_EQUIVALENTS = sum(RUN_EQUIVALENTS.values())
SECONDS_PER_RUN_EQUIVALENT = RUN_HOURS_TOTAL / REALISM * X2_PLATEAU * 3600 / TOTAL_RUN_EQUIVALENTS

COMPONENTS = ([f + "_tables_estimation" for f in FAMILIES]
              + [f + "_tables_validation" for f in FAMILIES]
              + list(RUN_EQUIVALENTS))

# Configuration-test plus cleanup reserve per launch, in seconds.
RESERVE_SECONDS = {"estimation": 900 + 300, "validation": 1800 + 1200, "runs": 900 + 300}


def _wall_hours(worker_seconds, workers):
    return worker_seconds / workers / 3600.0 * REALISM


def _family_estimation_seconds(family):
    primary, sensitivity = FAMILY_JOBS[family]
    fv, plain = primary * FV_ROUTE_FRACTION, primary * (1 - FV_ROUTE_FRACTION)
    est = fv * EST_FV + plain * EST_PLAIN
    est += sensitivity * (FV_ROUTE_FRACTION * EST_FV_SENS + (1 - FV_ROUTE_FRACTION) * EST_PLAIN_SENS)
    return est


def _plain_validation_seconds():
    return A4_FIT + PLAIN_VALIDATE_REPLICATES * A4_VALIDATE_PLAIN + A4_CENSUS


def _fv_validation_seconds():
    return A4_VALIDATE_FV + A4_CENSUS


def _family_validation_wall_hours(family):
    """Estimation-plus-A4-validation is split so the high-memory doubled-population
    FV validation (6,200 s per task) runs on its memory-capped worker count, and
    everything else on the plateau."""
    primary, sensitivity = FAMILY_JOBS[family]
    fv, plain = primary * FV_ROUTE_FRACTION, primary * (1 - FV_ROUTE_FRACTION)
    sens_fv, sens_plain = sensitivity * FV_ROUTE_FRACTION, sensitivity * (1 - FV_ROUTE_FRACTION)
    normal = plain * _plain_validation_seconds() + fv * _fv_validation_seconds()
    normal += sens_plain * _plain_validation_seconds() + sens_fv * A4_CENSUS
    high_mem = sens_fv * A4_VALIDATE_FV_HIGHMEM
    return _wall_hours(normal, X2_PLATEAU) + _wall_hours(high_mem, HIGH_MEM_WORKERS)


def _component_kind(component):
    if component.endswith("_tables_estimation"):
        return "estimation"
    if component.endswith("_tables_validation"):
        return "validation"
    if component.endswith("_runs"):
        return "runs"
    raise KeyError("unknown A6 budget component %r" % component)


def _component_wall_hours_at_plateau(component):
    kind = _component_kind(component)
    if kind == "estimation":
        return _wall_hours(_family_estimation_seconds(component[: -len("_tables_estimation")]), X2_PLATEAU)
    if kind == "validation":
        return _family_validation_wall_hours(component[: -len("_tables_validation")])
    return _wall_hours(RUN_EQUIVALENTS[component] * SECONDS_PER_RUN_EQUIVALENT, X2_PLATEAU)


def _reserve_hours(component):
    return RESERVE_SECONDS[_component_kind(component)] / 3600.0


def planning_estimate_hours(component):
    """The honest planning estimate in X2-equivalent hours: the component's
    committed cost at the plateau (high-memory FV validation at its memory cap)
    plus this launch's own configuration-test and cleanup reserve."""
    if component not in COMPONENTS:
        raise KeyError("unknown A6 budget component %r" % component)
    return _component_wall_hours_at_plateau(component) + _reserve_hours(component)


def planned_total_hours():
    """The honest planned total in X2-equivalent hours. May exceed the A6 ceiling (A7)."""
    return sum(planning_estimate_hours(c) for c in COMPONENTS)


def relative_throughput(machine):
    if machine not in MACHINES:
        raise ValueError("unknown machine %r" % machine)
    return MACHINES[machine]["relative"]


# ---------------------------------------------------------------------------
# The ledger and its consumption log
# ---------------------------------------------------------------------------

def build_ledger():
    planning = {c: planning_estimate_hours(c) for c in COMPONENTS}
    total = sum(planning.values())
    return {"schema": "v3-A6-budget-3", "program_ceiling_hours": PROGRAM_CEILING_HOURS,
            "units": "X2-equivalent wall hours", "realism": REALISM, "x2_plateau": X2_PLATEAU,
            "components": list(COMPONENTS), "planning_hours": planning,
            "planned_total_hours": total, "exceeds_ceiling": total > PROGRAM_CEILING_HOURS,
            "consumed_hours": {c: 0.0 for c in COMPONENTS}, "consumed_total_hours": 0.0,
            "high_memory_fv_validation_seconds": A4_VALIDATE_FV_HIGHMEM, "high_memory_workers": HIGH_MEM_WORKERS,
            "basis": "committed readiness measurements; high-memory FV validation at 6,200 s on a memory-capped "
                     "worker count; each launch's configuration and cleanup reserve included"}


def write_ledger(ledger_path, ledger):
    from .artifacts import atomic_json
    if Path(ledger_path).exists():
        raise RuntimeError("A6 ledger already exists; do not rebuild over it (consumption lives in the log)")
    atomic_json(ledger_path, seal(ledger))
    return ledger


def append_consumption(log_path, component, wall_hours, machine="x2"):
    """Append a consumption entry (charged in X2-equivalent hours: wall hours times
    the machine's relative throughput). The entry is written before any check that
    might raise. Then verify the total and raise if it exceeds the A6 ceiling (A7)."""
    if component not in COMPONENTS:
        raise KeyError("unknown A6 budget component %r" % component)
    x2_equivalent = float(wall_hours) * relative_throughput(machine)
    p = scoped(log_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"component": component, "wall_hours": float(wall_hours), "machine": machine,
                                 "hours": x2_equivalent}) + "\n")
        stream.flush()
    entries = read_consumption_log(log_path)
    total = sum(e["hours"] for e in entries)
    if total > PROGRAM_CEILING_HOURS + 1e-9:
        raise ValueError("A6 total consumption %.3f X2-equivalent hours exceeds the %.0f-hour A6 ceiling (A7) (recorded)"
                         % (total, PROGRAM_CEILING_HOURS))
    return entries


def read_consumption_log(log_path):
    p = Path(log_path)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def apply_consumption(ledger, entries):
    consumed = {c: 0.0 for c in ledger["components"]}
    for entry in entries:
        consumed[entry["component"]] = consumed.get(entry["component"], 0.0) + float(entry["hours"])
    return dict(ledger, consumed_hours=consumed, consumed_total_hours=sum(consumed.values()))


def load(ledger_document, log_path=None):
    payload = unseal(ledger_document) if set(ledger_document) == {"payload", "sha256"} else ledger_document
    if payload.get("schema") != "v3-A6-budget-3":
        raise ValueError("not an A6 budget ledger")
    return apply_consumption(payload, read_consumption_log(log_path) if log_path else [])


def assert_up_to_date(ledger, required_components):
    """Assert the consumption log already records every earlier launch's component,
    so a spec built now seals a current ceiling (item 4). ``required_components`` is
    the list of components launched before this one."""
    consumed = ledger.get("consumed_hours", {})
    missing = [c for c in required_components if not consumed.get(c, 0.0)]
    if missing:
        raise ValueError("A6 consumption log is not up to date; earlier launches unrecorded: %r" % missing)
    return True


# ---------------------------------------------------------------------------
# Projection, refusal and the runner ceiling
# ---------------------------------------------------------------------------

def _not_yet_run(ledger, current):
    consumed = ledger.get("consumed_hours", {})
    return [c for c in ledger["components"] if c != current and not consumed.get(c, 0.0)]


def _assert_workers(machine, workers):
    if workers not in MACHINES[machine]["workers"]:
        raise ValueError("A6 uses one of %s's tested worker counts %r, never another (e.g. 4)"
                         % (machine, MACHINES[machine]["workers"]))


def runner_ceiling_hours(ledger, component, machine="x2"):
    """The runner wall ceiling for a launch, in the machine's wall hours: the
    X2-equivalent allowance (the A6 ceiling less consumed and every later component's estimate)
    converted back to that machine's wall hours. Floored to whole seconds by the
    caller."""
    later = sum(planning_estimate_hours(c) for c in _not_yet_run(ledger, component))
    allowance_x2 = PROGRAM_CEILING_HOURS - ledger.get("consumed_total_hours", 0.0) - later
    return allowance_x2 / relative_throughput(machine)


def runner_ceiling_seconds(ledger, component, machine="x2"):
    return int(math.floor(runner_ceiling_hours(ledger, component, machine) * 3600))


def project(ledger, component, machine, workers):
    """Project and decide. The X2-equivalent projection is the component's planning
    estimate; the wall projection is that converted to the machine's wall hours.
    Refuses when the consumed time plus this projection plus the planning estimates
    of every component not yet run would exceed the A6 ceiling, A7 (unrounded)."""
    _assert_workers(machine, workers)
    rel = relative_throughput(machine)
    x2_projection = planning_estimate_hours(component)
    consumed = ledger.get("consumed_total_hours", 0.0)
    later = sum(planning_estimate_hours(c) for c in _not_yet_run(ledger, component))
    allowance_x2 = PROGRAM_CEILING_HOURS - consumed - later
    would = consumed + x2_projection + later
    result = {"component": component, "machine": machine, "workers": workers,
              "x2_equivalent_projection_hours": x2_projection, "wall_projection_hours": x2_projection / rel,
              "consumed_total_hours": consumed, "later_planning_hours": later,
              "runner_ceiling_wall_hours": allowance_x2 / rel, "would_total_hours": would,
              "planned_total_hours": planned_total_hours(), "refused": would > PROGRAM_CEILING_HOURS + 1e-9}
    if result["refused"]:
        tail = (" A6's planned total is %.1f X2-equivalent hours, over the %.0f-hour A6 ceiling (A7): the operator "
                "must choose a budget amendment or a uniform seed reduction across the arms' cells before any "
                "registered A6 run." % (result["planned_total_hours"], PROGRAM_CEILING_HOURS)) \
               if result["planned_total_hours"] > PROGRAM_CEILING_HOURS else \
               (" After a hard stop, a stopped component restarts in a new run root on the same seeds, its "
                "completed jobs kept only as a record; the ledger charges the hours already spent plus a fresh "
                "estimate. The operator chooses a budget amendment or a uniform seed reduction.")
        raise ValueError(("A6 launch of %r on %s/%d workers would bring the total to %.3f X2-equivalent hours, over "
                          "the %.0f-hour A6 ceiling (A7)." % (component, machine, workers, would, PROGRAM_CEILING_HOURS)) + tail)
    return result
