"""A5 pure-function tests: the tested set and M, living-source coverage with the
A4-support restriction, the width bound and range halts, classification and
exposure arithmetic reusing A4's test and safeguard, and the global seed guard.

Fast: no simulation, no I/O. Run with `python -B -m pytest test_v3_a5_functions.py`.
"""
import math

import numpy as np
import pytest

from v3.artifacts import seal, digest
from v3 import continuation_validation as cv
from v3 import table_labels_a5 as a5
from v3.production_tables import row_key
from v3.policies import execution_policy_class

CAL = "a5-test-calibration"
KERNEL = "a5-test-kernel"


def _fv_row(rule, scoring, status, entries, flow_range=10.0):
    return {"rule_id": rule.rule_id, "rule_hash": digest(rule.__dict__), "kernel_hash": KERNEL,
            "calibration_hash": CAL, "initial_population": 200, "scoring": scoring, "route": "fv",
            "status": status, "lambda_f": {"mean": 1.0, "replicates": [1.0, 1.0, 1.0]}, "LS": 1.0,
            "flow_range": flow_range, "continuation": {"entries": entries}}


def _plain_row(rule, scoring, entries):
    row = _fv_row(rule, scoring, "estimated", entries)
    row["route"] = "plain"
    return row


# --------------------------------------------------------------------------- tested set and M

def test_tested_set_membership_and_M():
    rules = execution_policy_class()
    sc1 = {"alpha": 1.0, "capability": 1.0, "kappa": 8.0}
    sc2 = {"alpha": 1.5, "capability": 1.0, "kappa": 8.0}
    e2 = [{"bin": [1, 0, 0, 0, 0, 0], "value": 1.0, "error": 1.0}, {"bin": [2, 0, 0, 0, 0, 0], "value": 2.0, "error": 1.0}]
    e3 = [{"bin": [1, 0, 0, 0, 0, 0], "value": 1.0, "error": 1.0}]
    rows = [
        _fv_row(rules[0], sc1, "estimated", e2),          # tested: 2 cells
        _fv_row(rules[1], sc2, "estimated", e3),          # tested: 1 cell
        _fv_row(rules[2], sc1, "not_estimable", e2),      # excluded (not_estimable)
        _plain_row(rules[3], sc1, e2),                    # excluded (plain)
    ]
    # The A4 family published to the reruns holds primary rows only, so a
    # sensitivity row never enters it; the tested set is by route and status.
    payload = {"rows": {row_key(r): seal(r) for r in rows}}
    tested = a5.tested_fv_rows(payload)
    assert len(tested) == 2
    assert all(r["route"] == "fv" and r["status"] == "estimated" for r in tested.values())
    M = sum(len((r.get("continuation") or {}).get("entries") or []) for r in tested.values())
    assert M == 3


# --------------------------------------------------------------------------- residual coverage

def test_next_cell_in_a1_but_not_a4_support_is_uncovered():
    # A5's value map holds only the A4-validated support. A next state that is an
    # A1-published cell but not in the A4 support is not covered.
    a4_support = int(cv.fine_codes([[1, 0, 0, 0, 0, 0]])[0])
    a1_only = int(cv.fine_codes([[2, 0, 0, 0, 0, 0]])[0])
    src = np.array([a4_support, a4_support])
    nxt = np.array([a4_support, a1_only])   # second transition lands in an A1-only cell
    source_alive = np.array([True, True])
    dead = np.array([False, False])
    flows = np.array([1.0, 1.0])
    value_by_code = {a4_support: 1.0}       # only the A4 support carries a value
    residual, covered, srcidx, codes = cv.living_source_residuals(src, nxt, source_alive, dead, flows, value_by_code, lower=0.0)
    assert covered.tolist() == [True, False]


def test_living_source_mask_with_extinct_tail():
    a4_support = int(cv.fine_codes([[1, 0, 0, 0, 0, 0]])[0])
    src = np.array([a4_support, a4_support, a4_support])
    nxt = np.array([a4_support, a4_support, a4_support])
    source_alive = np.array([True, True, False])   # third step's source already extinct
    dead = np.array([False, True, True])           # step 2 lands extinct -> V(next)=lower
    flows = np.array([1.0, 1.0, 1.0])
    residual, covered, srcidx, codes = cv.living_source_residuals(src, nxt, source_alive, dead, flows, {a4_support: 1.0}, lower=0.0)
    assert covered.tolist() == [True, True, False]


# --------------------------------------------------------------------------- width and ranges

def test_width_bounds_every_residual():
    rng = np.random.default_rng(5)
    lower, upper = 0.0, 6.0
    for _ in range(30):
        C = rng.uniform(lower, upper)
        vmax = rng.uniform(C, upper)
        w = cv.row_width(upper - lower, vmax, lower, upper)
        f = rng.uniform(lower, upper, 100)
        V = rng.uniform(lower, vmax, 100)
        m = (1 - cv.BETA) * f + cv.BETA * V - C
        assert m.max() - m.min() <= w + 1e-9


def test_range_halt_on_out_of_range_value():
    with pytest.raises(cv.OutOfRange):
        cv.check_in_range([0.0, 7.5], 0.0, 6.0, "A4 published value")
    with pytest.raises(cv.OutOfRange):
        cv.row_width(6.0, vmax=99.0, lower=0.0, upper=6.0)


# --------------------------------------------------------------------------- classification and exposure

def test_classify_cell_reuses_a4_test_and_safeguard():
    # Zero residual, well visited -> certified.
    certified = a5.classify_cell({"sum_m": 0.0, "sum_m2": 0.0, "n_traj": 200, "sum_S": 0.0, "sum_N": 400.0},
                                 width=1.0, M=10, tau=0.5)
    assert certified["status"] == "certified" and a5.label_for(certified["status"]) == a5.CERTIFIED_LABEL
    # Large mean far outside tau -> violation.
    violation = a5.classify_cell({"sum_m": 2000.0, "sum_m2": 20000.0, "n_traj": 200, "sum_S": 2000.0, "sum_N": 200.0},
                                 width=1.0, M=10, tau=0.5)
    assert violation["status"] == "violation" and a5.label_for(violation["status"]) == a5.ASYMPTOTIC_LABEL
    # No visits -> unresolved.
    unresolved = a5.classify_cell(None, width=1.0, M=10, tau=0.5)
    assert unresolved["status"] == "unresolved" and a5.label_for(unresolved["status"]) == a5.ASYMPTOTIC_LABEL
    # Certified interval but safeguard fails -> unresolved (not certified).
    safeguard = a5.classify_cell({"sum_m": 0.0, "sum_m2": 0.0, "n_traj": 200, "sum_S": 800.0, "sum_N": 400.0},
                                 width=1.0, M=10, tau=0.5)
    assert safeguard["status"] == "unresolved" and not safeguard["visit_weighted_ok"]


def _one_job_plan(support, width=1.0, tau=0.5, flow_range=10.0):
    row = {"row_key": "RK", "scoring": {"alpha": 1.0, "capability": 1.0, "kappa": 8.0},
           "support": support, "vmax": max(v for _, v in support), "width": width, "tau": tau, "flow_range": flow_range}
    job = {"config": {"a1_job": {"id": "J"}, "tested_rows": [row]}}
    return {"jobs": [job], "M": len(support)}


def test_exposure_arithmetic_and_shares():
    cert = int(cv.fine_codes([[1, 0, 0, 0, 0, 0]])[0])
    viol = int(cv.fine_codes([[2, 0, 0, 0, 0, 0]])[0])
    plan = _one_job_plan([[cert, 1.0], [viol, 2.0]])
    good = {"sum_m": 0.0, "sum_m2": 0.0, "n_traj": 100, "sum_S": 0.0, "sum_N": 300.0}
    bad = {"sum_m": 1000.0, "sum_m2": 10000.0, "n_traj": 100, "sum_S": 1000.0, "sum_N": 100.0}
    stage = [{"a1_job_id": "J", "rows": [{"row_key": "RK", "scoring": plan["jobs"][0]["config"]["tested_rows"][0]["scoring"],
                                          "cells": [{"cell": cert, **good}, {"cell": viol, **bad}]}]}]
    census = {"J": {"cell_counts": {cert: 30, viol: 20}, "total_living": 100}}
    rows, totals = a5.build_labels(plan, stage, census)
    r = rows[0]
    assert r["certified"] == 1 and r["violation"] == 1 and r["unresolved"] == 0
    # Exposure of the violated cell = its share of the row's living census endpoints.
    assert abs(r["violations"][0]["exposure"] - 0.20) < 1e-12
    assert abs(r["violation_exposure_total"] - 0.20) < 1e-12
    # Plain-law visit share in certified cells = 300 / (300 + 100).
    assert abs(r["certified_visit_share"] - 0.75) < 1e-12
    # Census share in certified cells = 30 / 100.
    assert abs(r["certified_census_share"] - 0.30) < 1e-12
    assert r["cells"][0]["label"] == a5.CERTIFIED_LABEL and r["cells"][1]["label"] == a5.ASYMPTOTIC_LABEL
    assert totals["violation"] == 1 and totals["certified"] == 1


def test_unvisited_support_cell_is_unresolved_and_counted_in_M():
    cert = int(cv.fine_codes([[1, 0, 0, 0, 0, 0]])[0])
    missing = int(cv.fine_codes([[3, 0, 0, 0, 0, 0]])[0])
    plan = _one_job_plan([[cert, 1.0], [missing, 1.0]])
    good = {"sum_m": 0.0, "sum_m2": 0.0, "n_traj": 100, "sum_S": 0.0, "sum_N": 300.0}
    stage = [{"a1_job_id": "J", "rows": [{"row_key": "RK", "scoring": plan["jobs"][0]["config"]["tested_rows"][0]["scoring"],
                                          "cells": [{"cell": cert, **good}]}]}]  # `missing` never visited
    census = {"J": {"cell_counts": {}, "total_living": 0}}
    rows, totals = a5.build_labels(plan, stage, census)
    assert rows[0]["unresolved"] == 1 and rows[0]["certified"] == 1
    assert totals["cells"] == 2   # both support cells classified, even the unvisited one


# --------------------------------------------------------------------------- seeds

def test_forbidden_set_includes_a4_plan_and_p4_seeds():
    a1_seeds = {111, 222}
    a4_stream = {987654321, 123456789}
    probe = {555}
    forbidden = a5.forbidden_seeds(a1_seeds, a4_stream, probe)
    assert 987654321 in forbidden and 123456789 in forbidden  # A4 plan stream seeds
    assert 111 in forbidden and 555 in forbidden              # A1 job and D26 probe seeds
    assert a5._planning_p4_seed(111, 0) in forbidden and a5._planning_p4_seed(222, 3) in forbidden
    assert cv._planning_p1_seed(111) in forbidden and cv._planning_p3_seed(222, 2) in forbidden


def test_seed_collision_with_a4_plan_seed_halts():
    seed = 424242
    collide = a5.fvplain_seed(seed, 2)          # this A5 seed is planted as an A4 plan seed
    forbidden = a5.forbidden_seeds({seed}, {collide}, {1})
    with pytest.raises(cv.SeedCollision):
        a5.assert_a5_seeds([seed], forbidden)


def test_a5_seeds_pairwise_distinct():
    seeds = [11, 22, 33, 44]
    forbidden = a5.forbidden_seeds(set(seeds), set(), {1})
    # Remove the P1/P3/P4 derivations of these seeds so only genuine A5 seeds are tested.
    a5_seeds = a5.assert_a5_seeds(seeds, a5.forbidden_seeds(set(), set(), {1}))
    values = list(a5_seeds.values())
    assert len(a5_seeds) == len(seeds) * 3 and len(set(values)) == len(values)


def test_fvplain_seed_matches_committed_derivation():
    seed = 777
    assert a5.fvplain_seed(seed, 2) == cv.stream_seed("v3_R_fvplain", seed, 2)
    assert a5.fvplain_seed(seed, 2) == int(
        __import__("hashlib").sha256(b"v3_R_fvplain" + str(seed).encode() + b"2").hexdigest()[:15], 16)


def test_seed_collision_through_p4_derivation():
    # The P4 value comes through the module's own derivation, not a magic constant.
    S = 424242
    forbidden = a5.forbidden_seeds({S}, set(), {1})
    for r in range(4):
        assert a5._planning_p4_seed(S, r) in forbidden        # every P4 replicate, derived, forbidden
    # The guard halts on any forbidden member; cross-tag equality between an A5
    # seed and a P4 seed cannot occur naturally, so we exercise the halt with the
    # A5 seed value present in the forbidden set.
    with pytest.raises(cv.SeedCollision):
        a5.assert_a5_seeds([S], forbidden | {a5.fvplain_seed(S, 1)})


# --------------------------------------------------------------------------- A4 plan verification

def _mini_a4_plan():
    from v3 import table_validation_a4 as a4
    from v3.artifacts import stable_job, digest
    a1 = {"id": "a1_x", "seed": 11, "config": {"settings": {"runs_per_group": 64, "particles": 256}}}
    j1 = stable_job("a4_validate", {"a1_job": a1, "phase": "validate_fv_primary", "seed": 501}, "v3_tables", 0)
    j2 = stable_job("a4_census", {"a1_job": a1, "phase": "census", "seed": 502}, "v3_tables", 1)
    manifest = {"jobs": [a1]}
    plan = {"schema": "v3-A4-validation-1", "jobs": [j1, j2], "source_file_sha256": "s",
            "source_manifest_sha256": digest(manifest), "source_code_hash": "c", "M": 0, "M_FV": 3, "code_hash": "h",
            "settings_override": None, "registration": None}
    plan["plan_hash"] = a4._recompute_plan_hash(plan)
    receipt = {"plan_hash": plan["plan_hash"], "stream_seeds": {j1["id"]: 501, j2["id"]: 502}}
    return plan, receipt, manifest


def test_verify_a4_plan_passes_and_returns_seeds():
    plan, receipt, manifest = _mini_a4_plan()
    assert a5.verify_a4_plan(plan, receipt, manifest) == {11}


def test_verify_a4_plan_rejects_hash_seed_and_subset():
    plan, receipt, manifest = _mini_a4_plan()
    with pytest.raises(ValueError, match="A4 plan hash differs"):
        a5.verify_a4_plan(plan, {**receipt, "plan_hash": "wrong"}, manifest)
    bad_seed = {**receipt, "stream_seeds": {**receipt["stream_seeds"], plan["jobs"][0]["id"]: 999}}
    with pytest.raises(ValueError, match="job seed differs"):
        a5.verify_a4_plan(plan, bad_seed, manifest)
    from v3.artifacts import digest
    from v3 import table_validation_a4 as a4

    def variant(manifest):
        p = {**plan, "source_manifest_sha256": digest(manifest)}
        p["plan_hash"] = a4._recompute_plan_hash(p)
        return p, {**receipt, "plan_hash": p["plan_hash"]}, manifest

    with pytest.raises(ValueError, match="differ from the A1 manifest"):
        a5.verify_a4_plan(*variant({"jobs": [{"seed": 77}]}))
    with pytest.raises(ValueError, match="duplicate A1 job seeds"):
        a5.verify_a4_plan(*variant({"jobs": [{"seed": 11}, {"seed": 11}]}))
    with pytest.raises(ValueError, match="source manifest hash"):
        a5.verify_a4_plan(plan, receipt, {"jobs": [{"seed": 11}], "extra": True})


def test_registered_prepare_refuses_non_24_wall_hours():
    with pytest.raises(ValueError, match="24-hour"):
        a5.prepare("f", "r", "p", "src", "cal", "id.json",
                   registration={"commit": "x", "path": "p", "sha256": "s"}, wall_hours=48, a3_probe_root="probe")


def test_registered_prepare_requires_committed_identity_path():
    with pytest.raises(ValueError, match="committed identity record"):
        a5.prepare("f", "r", "p", "src", "cal", "not/the/committed/path.json",
                   registration={"commit": "x", "path": "p", "sha256": "s"}, wall_hours=24, a3_probe_root="probe")
