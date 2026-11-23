"""Incidence (section 4): the derived denominators of 4.4, the per-run records
of 4.3 and the pooling of 4.5.

A missing ``a13_decision_incidence`` is never turned into "unassessed" or a
fabricated zero. In a case 1 family it is an integrity failure; in a case 2
family it is required, and the record is normalized with a structural-zero
numerator and a denominator counted from the recorded decisions.
"""
from collections import Counter
from hashlib import sha256

from .common import integer, require

BRANCHES = ("ordinary_allocation", "survival_first", "yield_review")
COUNTS = ("excluded_by_reason", "balanced_fallbacks_by_reason", "survival_first_unavailable_selections_by_reason")
MISSING = "missing_or_not_estimable_row"
RECORDED = "recorded"
NO_ADMITTED = "no admitted rows"
NOT_DERIVABLE = "incidence denominators not derivable"
NOT_RECORDED = "not recorded"


def derive(result):
    """Section 4.4, exactly. Returns the three derived denominators, after the
    preconditions of D:455. A failed precondition refuses with A6.1's label."""
    try:
        steps, events = result["diagnostics"], result["yield_events"]
        allocation_steps = result["continuation_availability"]["allocation_steps"]
    except (KeyError, TypeError):
        require(False, NOT_DERIVABLE)
    require(isinstance(steps, list) and isinstance(events, list), NOT_DERIVABLE)
    ordinary = survival_first = 0
    evaluated_times = set()
    for step in steps:
        require(isinstance(step, dict), NOT_DERIVABLE)
        evaluated, first = step.get("allocation_evaluated"), step.get("survival_first")
        # Precondition: every allocation_evaluated and survival_first is a bool.
        require(type(evaluated) is bool and type(first) is bool, NOT_DERIVABLE)
        if evaluated is True:
            if first is True:
                survival_first += 1
            else:
                ordinary += 1
            evaluated_times.add(step.get("time"))
    times = []
    for event in events:
        require(isinstance(event, dict) and type(event.get("time")) is int, NOT_DERIVABLE)
        times.append(event["time"])
    # Preconditions: event times are distinct, each a multiple of 10 and each
    # the time of a step with allocation_evaluated true.
    require(len(set(times)) == len(times), NOT_DERIVABLE)
    require(all(t % 10 == 0 for t in times), NOT_DERIVABLE)
    require(all(t in evaluated_times for t in times), NOT_DERIVABLE)
    # Precondition: ordinary + survival_first == allocation_steps.
    require(type(allocation_steps) is int and ordinary + survival_first == allocation_steps, NOT_DERIVABLE)
    return {"ordinary_allocation": ordinary, "survival_first": survival_first, "yield_review": len(events)}


def try_derive(result):
    """The derived denominators, or ``None`` when a precondition fails. G8
    decides the refusal, so that gate order stays fixed."""
    from .common import Refused
    try:
        return derive(result)
    except Refused:
        return None


def validate(value):
    """Section 4.3, case 1: the recorded record. A10.8 item 2: D:417-420 is the
    complete list of tests; no test relates a numerator, or a denominator, to
    the reason maps. The denominator self-check is in ``per_run``."""
    require(isinstance(value, dict) and set(value) == set(BRANCHES), "a13 incidence branches")
    for b in BRANCHES:
        row = value[b]
        require(isinstance(row, dict), "a13 incidence branches")
        n, d = row.get("numerator"), row.get("denominator")
        require(integer(n) and integer(d) and n <= d and row.get("assessed") is bool(d) and
                row.get("rate") == (n / d if d else None), "a13 incidence counts")
        for name in COUNTS:
            counts = row.get(name)
            require(isinstance(counts, dict) and all(isinstance(k, str) and integer(v) for k, v in counts.items()),
                    "a13 incidence separate counts")


def normalized(derived):
    """Section 4.3, case 2: the normalized record (D:428-431)."""
    return {b: {"numerator": 0, "denominator": derived[b], "rate": 0.0 if derived[b] else None,
                "assessed": bool(derived[b]),
                "provenance": {"numerator": "structural_zero_from_verified_family",
                               "denominator": "derived_from_recorded_decisions"}} for b in BRANCHES}


def per_run(case, has_field, recorded, derived, missing_row):
    """G8 for one contributing run. ``case`` is the run's family case (1 or 2)."""
    if case == 1:
        # Absence is an integrity failure, never "no admitted rows" (D:417).
        require(has_field, "a13 incidence missing on admitted family")
        validate(recorded)
        # A10.8 item 1: D:455's preconditions apply to every contributing run. For
        # a case 1 run the label is the build's own; this build uses A6.1's.
        require(derived is not None, NOT_DERIVABLE)
        # The denominator self-check on every case 1 run (D:420).
        require(all(recorded[b]["denominator"] == derived[b] for b in BRANCHES),
                "derived incidence denominators differ from recorded")
        return {"status": RECORDED, "record": recorded}
    require(not has_field, "a13 incidence present on a no-admitted family")
    require(not missing_row, "missing row recorded in a no-admitted family")
    # A6.1: an underivable denominator of a no-admitted-rows run refuses.
    require(derived is not None, NOT_DERIVABLE)
    return {"status": NO_ADMITTED, "record": normalized(derived)}


def pooled(keys, runs, family_of, family_info):
    """Section 4.5 for one quantity. ``keys`` is its contributing runs in sorted
    order of "<component>/<job_id>"; ``runs`` maps a key to its per-run entry."""
    from v3.admission_a13 import pooled_incidence
    from v3.artifacts import canonical
    records = [runs[k]["record"] for k in keys]
    native = pooled_incidence(records)
    branches = {b: {"numerator": native["branches"][b]["numerator"], "denominator": native["branches"][b]["denominator"],
                    "rate": native["branches"][b]["rate"]} for b in BRANCHES}
    incidence = {"flag": native["affected_by_table_unavailability"], "branches": branches,
                 "per_run_sha256": sha256(canonical({k: runs[k]["record"] for k in keys})).hexdigest()}
    families = {}
    for k in keys:
        family = family_of[k.split("/", 1)[0]]
        entry = families.setdefault(family, {"status": runs[k]["status"], "runs": 0,
                                             "table_sha256": family_info[family]["table_file_sha256"],
                                             "receipt_sha256": family_info[family]["a10_receipt_file_sha256"]})
        require(entry["status"] == runs[k]["status"], "family incidence status inconsistent")
        entry["runs"] += 1
    status = {"branches": {b: ("assessed" if native["branches"][b]["assessed"] else "unassessed") for b in BRANCHES},
              "families": dict(sorted(families.items()))}
    recorded = [runs[k]["record"] for k in keys if runs[k]["status"] == RECORDED]
    counts = {}
    for b in BRANCHES:
        counts[b] = {}
        for name in COUNTS:
            # A10.1: with no recorded run in the pool, all nine values are the
            # string "not recorded". Otherwise each map sums, over the recorded
            # runs, every reason that is a key in at least one of them, whatever
            # its sum; the case 2 runs add nothing.
            if not recorded:
                counts[b][name] = NOT_RECORDED
                continue
            total = Counter()
            for record in recorded:
                total.update(record[b][name])
            counts[b][name] = dict(sorted(total.items()))
    separate = {"recorded_runs": len(recorded), "not_recorded_runs": len(keys) - len(recorded), "branches": counts}
    return native, incidence, status, separate
