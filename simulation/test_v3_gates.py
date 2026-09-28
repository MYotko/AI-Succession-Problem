"""D21 synthetic registered-format fixtures. No registered rerun files read.

gate_evidence is the explicit raw-evidence contract documented in A2; it
is not claimed to have been emitted by the A1 instrument. Production-format
fixtures lacking it deliberately fail closed.
"""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import math
from pathlib import Path
import pytest
import numpy as np
from v3 import gates
from v3.artifacts import seal, code_identity, atomic_json, file_hash, stable_job, digest


def calibration_fixture():
    return seal({"schema": "v3-calibration-1", "fixture": True, "tag": "pilot_or_validation", "code_hash": code_identity(),
                 "values": {"center": [0.] * 10, "sigma_squared": .001, "n_ref": 200., "epsilon_n": .1,
                            "epsilon_e": .003, "epsilon_l": .001, "c_e": 2.5}})


@pytest.fixture(scope="module")
def before():
    return gates.before_checks(calibration_fixture())


@pytest.mark.parametrize("gate", gates.BEFORE)
def test_before_positive_and_checker_boundary_ties(gate, before):
    item = next(c for c in before if c["gate"] == gate)
    assert item["passed"] and item["checked"] > 0
    assert item["zero_failure_bound95"] == pytest.approx(1 - .05**(1 / item["checked"]))


@pytest.mark.parametrize("gate", gates.BEFORE)
def test_before_rejects_broken_candidate(gate, monkeypatch):
    from v3 import objective, measurements, plans, integration
    if gate == "G1.1":
        original = objective.flow
        monkeypatch.setattr(objective, "flow", lambda *args: original(*args) * 2)
    elif gate == "G1.2":
        original = measurements.lineage
        monkeypatch.setattr(measurements, "lineage", lambda *args: max(1e-6, original(*args)))
    elif gate == "G1.3":
        original = measurements.transfer
        monkeypatch.setattr(measurements, "transfer", lambda *args: .9 * original(*args))
    elif gate == "G1.4":
        original = objective.discounted_flow
        monkeypatch.setattr(objective, "discounted_flow", lambda *a, **k: objective.ValueBound(2 * original(*a, **k).value))
    elif gate == "G1.5":
        original = integration.V3Model.step
        monkeypatch.setattr(integration.V3Model, "step", lambda self: {**original(self), "population": 1})
    else:
        original = plans.compare_plans
        monkeypatch.setattr(plans, "compare_plans", lambda *args: replace(original(*args), yield_now=not original(*args).yield_now))
    check = next(c for c in gates.before_checks(calibration_fixture()) if c["gate"] == gate)
    assert not check["passed"]


def test_before_checks_vector_executor_theta_not_only_scalar_helper(monkeypatch):
    from v3 import engine
    original = engine.measurements_and_flow
    def broken(*args, **kwargs):
        flow, measures = original(*args, **kwargs)
        measures["theta"] *= .8
        return flow, measures
    monkeypatch.setattr(engine, "measurements_and_flow", broken)
    assert not next(c for c in gates.before_checks(calibration_fixture()) if c["gate"] == "G1.3")["passed"]


def review_fixture(margin=1., identity=0):
    now = identity * 10
    epoch = {"epoch_id": f"epoch-{now}", "origin": now, "deadline": now + 25, "theta": .5,
             "beta": math.exp(-.01), "extinction_flow": -10., "preference_id": "weights", "information_law_id": "law"}
    def plan(name, value, first_yield):
        return {"plan_id": name, "epoch_id": epoch["epoch_id"], "preference_id": "weights", "information_law_id": "law",
                "extinction_flow": -10., "start": now, "terminal_time": now + 25, "first_yield": first_yield,
                "flows": [value] * 25, "continuation": value, "lambda_f": value,
                "available": True, "admitted": True, "admission_evidence": {"period_bound": .0001, "active_bound": .0001}}
    immediate, wait, later = plan("now", 2. + margin, now), plan("hold", 2., None), plan("later", 1., now + 10)
    for p in (immediate, later):
        # Positive disruption measured in complete-plan units, not a field
        # called Gamma that the checker might accidentally trust.
        p["gamma"] = 1.
        # Fixed physical drawdown fixture, independent of synthetic W values.
        p['transition'] = {'stock_units_before':[50,50,50,50], 'stock_units_after':[37,50,50,50],
                           'applied_drawdown_units':13, 'capability_gap':.5, 'action':[1/6]*6, 'uniform':.5}
        p["undisrupted"] = {"flows": [x + 1 for x in p["flows"]], "continuation": p["continuation"] + 1,
                            "lambda_f": p["lambda_f"] + 1}
    fire = margin > 0
    decision = {"yield_now": fire, "selected_plan": "now" if fire else "hold", "best_waiting_plan": "hold",
                "immediate_value": 2. + margin, "waiting_value": 2., "survival_first": False}
    return {"time": now, "deadline": now + 25, "plan_count": 3, "transition_count": int(fire), "decision": decision,
            "gate_evidence": {"epoch": epoch, "plans": [immediate, wait, later],
                'incumbent_capability':1., 'successor_capability':1.5,
                'applied_transition':deepcopy(immediate['transition']),
                "comparison_values": {"now": 2. + margin, "hold": 2., "later": 1.},
                "succession": {"generation_before": 1, "generation_after": 2, "capability_before": 1., "capability_after": 1.5,
                               "requested_capability": 1.5, "capability_ratio": 1.5, "knowledge_transfer": .7}}}


def run_fixture(index=0, *, category="R2", alpha=1., cap=1.5, rr=.064, fire=True):
    job = stable_job("rerun", {"category": category, "steps": 1,
                              "model": {"alpha": alpha, "successor_capability": cap, "reproduction_rate": rr}}, "v3_rerun", index)
    review = review_fixture(1 if fire else -1)
    return {"fixture": True, "job": job, "code_hash": "synthetic-source",
            "result": {"tag": "v3_rerun", "fixture_tables": False, "steps": 1, "yield_events": [review],
                       "diagnostics": [{"time": 0, "population": 200, "capability": cap if fire else 1., "override": False}], "periods": []}}


@pytest.mark.parametrize("margin", [1., -1., 0.])
def test_g31_positive_negative_and_strict_tie(margin):
    e = review_fixture(margin)
    assert gates.check_review(({}, e))
    e["decision"]["yield_now"] = not e["decision"]["yield_now"]
    assert not gates.check_review(({}, e))


def test_g31_requires_all_plans_and_committed_units():
    e = review_fixture()
    e["gate_evidence"]["plans"].pop()
    with pytest.raises(ValueError, match="alternatives"):
        gates.recompute_review(e)
    e = review_fixture()
    e["gate_evidence"]["plans"][0]["preference_id"] = "new weights"
    with pytest.raises(ValueError, match="units"):
        gates.recompute_review(e)


@pytest.mark.parametrize("margin", [1., -1., 0.])
def test_g32_once_counted_disruption_and_double_cost(margin):
    e = review_fixture(margin)
    assert gates.check_gamma(({}, e))
    e["gate_evidence"]["comparison_values"]["now"] -= 1.
    assert not gates.check_gamma(({}, e))


def test_g33_positive_negative_and_ratio_tie():
    e = review_fixture()
    assert gates.check_succession(({}, e))
    proof = e["gate_evidence"]["succession"]
    proof["capability_after"] = proof["capability_ratio"] = proof["requested_capability"] = 1.
    assert not gates.check_succession(({}, e))
    proof.update(capability_after=5., capability_ratio=5., requested_capability=7.)
    assert gates.check_succession(({}, e))
    proof["generation_after"] = 1
    assert not gates.check_succession(({}, e))
    del proof["knowledge_transfer"]
    assert not gates.checked("G3.3", [({}, e)], gates.check_succession)["passed"]


@pytest.mark.parametrize("v,b,t", [(0., 0., 0.), (1., 1., 1.), (5., 0., .5)])
def test_g41_positive_runaway_boundary_tie_and_off_formula(v, b, t):
    r = run_fixture()
    s = {"theta": math.exp(-(1 - t) * v / 5 - max(0, v / max(b, 5 / (1 + math.log(1000) / .5)) - 1)),
         "gate_evidence": {"frontier_velocity": v, "bandwidth": b, "transfer_stock": t}}
    assert gates.check_theta((r, s), .001)
    s["theta"] += .01
    assert not gates.check_theta((r, s), .001)


def grid_fixture(thresholds=(4., 3., 2.5, 2., 1.5), overrides=None):
    runs = []
    for a, threshold in zip(gates.ALPHAS, thresholds):
        for c in gates.CAPABILITIES:
            yes = (overrides or {}).get((a, c), 75 if c <= threshold else 0)
            for rr in gates.R2_RR:
                for seed in range(75):
                    r = run_fixture(seed, alpha=a, cap=c, rr=rr, fire=seed < yes)
                    # These tests need capability observations, not plan evidence.
                    r["result"]["yield_events"] = []
                    runs.append(r)
    return runs


def test_g22_g42_positive_cliff_and_adjacent_flats():
    for thresholds in ((4., 3., 2.5, 2., 1.5), (4., 4., 3., 3., 2.)):
        a, b = gates.cliff_checks(grid_fixture(thresholds))
        assert a["passed"] and b["passed"]
        assert all(p["decrease_support"] == 1 for p in a["adjacent_pairs"] if p["cap_star"][0] != p["cap_star"][1])


@pytest.mark.parametrize("caps", [(3., 4., 2.5, 2., 1.5), (3.,) * 5])
def test_g22_cap_increase_and_no_net_decrease_fail(caps):
    assert not gates.cliff_checks(grid_fixture(caps))[0]["passed"]


def test_g22_point_decrease_without_bootstrap_support_fails():
    a, _ = gates.cliff_checks(grid_fixture(overrides={(.5, 4.): 38, (.75, 4.): 37}))
    assert a["cap_star"][.5] == 4. and a["cap_star"][.75] == 3.
    assert not a["passed"] and a["adjacent_pairs"][0]["decrease_support"] < .9


def test_g22_half_rate_is_included_and_g42_no_above_is_not_testable():
    r = grid_fixture((5., 4., 3., 2., 1.5))
    a, b = gates.cliff_checks(r)
    assert a["passed"] and b["passed"]
    assert b["alpha_checks"][0]["status"] == "not_testable"
    # Exact 50% pooled rate on a capability is included in cap*.
    for run in r:
        m = run["job"]["config"]["model"]
        if m["alpha"] == .5 and m["successor_capability"] == 5.:
            run["result"]["diagnostics"][0]["capability"] = 5. if m["reproduction_rate"] in gates.R2_RR[:2] else 1.
    assert gates.cliff_checks(r)[0]["cap_star"][.5] == 5.


def test_g42_two_se_equality_passes_and_unsupported_separation_fails():
    assert gates.separation_check(.5, 0., 4, 4) == (True, .25)
    assert not gates.separation_check(.49, 0., 4, 4)[0]
    assert not gates.separation_check(1., .51, 1000, 1000)[0]
    _, b = gates.cliff_checks(grid_fixture(overrides={(.5, 4.): 38, (.5, 5.): 37}))
    assert not b["passed"]


@pytest.mark.parametrize("ages,welfare", [([0]*200, [1000]*200), ([80], [700]), ([], [])])
def test_g43_recomputes_exact_ledger_and_real_recordable_bounds(ages, welfare):
    from v3.cohort import cohort_bound, ProtectionPeriod
    from v3.policies import execution_policy_class
    r = run_fixture(fire=False)
    r["job"]["config"]["model"]["n_agents"] = len(ages)
    bound = cohort_bound(ages,welfare)
    step = r["result"]["diagnostics"][0]
    step.update(population=len(ages), survival_first=not bound.admitted(), gate_evidence={
        "population_before":len(ages), "period_start":{"ages_before":ages,"welfare_units_before":welfare},
        "ages_before":ages,"welfare_units_before":welfare,"action":[0.,1.,0.,0.,0.,0.],
        "summary_bins_before":[0]*6,"rule_ids":[x.rule_id for x in execution_policy_class()]})
    r["result"]["periods"] = [ProtectionPeriod(0,25,50,(),bound).audit()]
    assert gates.viability([r])["passed"]
    r["result"]["periods"][0]["bound"] = .00101
    assert not gates.viability([r])["passed"]
    r["result"]["periods"][0] = ProtectionPeriod(0,25,50,(),bound).audit()
    step["override"] = True
    assert not gates.viability([r])["passed"]


def test_g43_requires_action_evidence_above_epsilon_and_all_periods():
    r = run_fixture(fire=False)
    assert not gates.viability([r])["passed"]
    r["result"]["periods"] = [{"start": 0, "protection_end": 25, "lookahead_end": 50, "bound": 1., "admitted": False,
                               "reserved": "0", "unallocated": "1/1000", "alpha_spent": "0"}]
    r["result"]["diagnostics"][0]["survival_first"] = True
    assert not gates.viability([r])["passed"]  # A self-reported flag is insufficient.


def test_independent_cohort_reference_matches_integer_floor_kernel():
    from v3.cohort import cohort_bound
    for a, w in (([0, 20, 30], [800, 700, 600]), ([80], [900]), ([], [])):
        assert gates.reference_cohort(a, w) == cohort_bound(a, w).exact


def test_sampling_is_hash_fixed_stratified_and_independent_of_file_order():
    runs = [run_fixture(i, fire=i < 30) for i in range(260)]
    first = gates.sample_reviews(runs)
    second = gates.sample_reviews(list(reversed(runs)))
    assert len(first) == 200 and sum(e["transition_count"] for _, e in first) == 30
    assert [gates.identity(*x) for x in first] == [gates.identity(*x) for x in second]
    runs = [run_fixture(i, fire=i < 160) for i in range(300)]
    selected = gates.sample_reviews(runs)
    assert len(selected) == 200 and sum(e["transition_count"] for _, e in selected) == 100


def test_g31_registered_sample_zero_mismatch_and_reported_bound():
    runs = [run_fixture(i, fire=i % 2 == 0) for i in range(220)]
    reviews = gates.sample_reviews(runs)
    result = gates.checked("G3.1.sample", reviews, gates.check_review)
    assert result["passed"] and result["checked"] == 200
    assert result["zero_failure_bound95"] == pytest.approx(.0148670392)
    reviews[0][1]["decision"]["yield_now"] ^= True
    assert not gates.checked("G3.1.sample", reviews, gates.check_review)["passed"]


def test_g41_10000_hash_selected_steps_and_no_smaller_sample_pass():
    r = run_fixture()
    r["result"]["diagnostics"] = [{"time": t, "theta": 1., "gate_evidence": {"population_before": 1, "frontier_velocity": 0., "bandwidth": 0., "transfer_stock": 0.}}
                                  for t in range(10020)]
    selected = gates.sample_steps([r])
    assert len(selected) == 10000
    assert [s["time"] for _, s in selected] == [s["time"] for _, s in gates.sample_steps([r])]
    c = gates.checked("G4.1", selected, lambda item: gates.check_theta(item, .001))
    assert c["passed"] and c["zero_failure_bound95"] == pytest.approx(1 - .05**.0001)


def test_fail_closed_aggregation_rejects_missing_na_skip_duplicate_and_fixture():
    passed = [gates.result(k, 10) for k in gates.GOVERNS]
    assert gates.aggregate(passed)["cleared_through"] == 5
    for gate in gates.GOVERNS:
        checks = [c for c in passed if c["gate"] != gate]
        assert gate in gates.aggregate(checks)["missing_or_failed"]
        checks.append({"gate": gate, "status": "not_applicable", "passed": True})
        assert gate in gates.aggregate(checks)["missing_or_failed"]
    assert "G1.1" in gates.aggregate(passed + [passed[0]])["missing_or_failed"]
    assert not any(gates.aggregate(passed, fixture=True)["citable"].values())
    assert set(gates.NA) == {"G2.1", "G2.3", "G2.4", "G5.1", "G5.2"}


def artifact_fixture(tmp_path):
    r = run_fixture()
    atomic_json(tmp_path / "run.json", r)
    atomic_json(tmp_path / "complete.json", {"status": "complete", "job": r["job"], "code_hash": r["code_hash"], "output_hash": file_hash(tmp_path / "run.json")})
    atomic_json(tmp_path / "manifest.json", seal({"registered": True, "code_hash": r["code_hash"], "jobs": [r["job"]]}))
    def ref(name):
        return {"path": name, "sha256": file_hash(tmp_path / name)}
    e = {"schema": "v3-gate-evidence-1", "fixture": True, "instrument_code_hash": r["code_hash"],
         "rerun_manifest": ref("manifest.json"), "runs": [{"output": ref("run.json"), "completion": ref("complete.json")}]}
    atomic_json(tmp_path / "evidence.json", e)
    return tmp_path / "evidence.json"


def test_artifact_paths_hashes_completion_and_fixture_rejection(tmp_path):
    p = artifact_fixture(tmp_path)
    runs, metadata = gates.load_runs(p, file_hash(p), fixtures=True)
    assert len(runs) == metadata["verified_runs"] == 1
    with pytest.raises(ValueError, match="fixture"):
        gates.load_runs(p, file_hash(p))
    with pytest.raises(ValueError, match="hash"):
        gates.load_runs(p, "0" * 64, fixtures=True)
    (tmp_path / "run.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="hash"):
        list(runs)  # Rechecked on every streaming pass.


def test_current_a1_schema_cannot_pass_by_reporting_flags_only():
    r = run_fixture()
    del r["result"]["yield_events"][0]["gate_evidence"]
    assert not gates.checked("G3.1.sample", [(r, r["result"]["yield_events"][0])], gates.check_review)["passed"]
    assert not gates.checked("G3.2", [(r, r["result"]["yield_events"][0])], gates.check_gamma)["passed"]
    assert not gates.checked("G4.1", [(r, {"theta": 1.})], lambda item: gates.check_theta(item, .001))["passed"]


def test_short_samples_missing_checks_and_empty_successions_fail():
    checks = gates.after_checks([run_fixture(fire=False)], .001)
    assert all(not c["passed"] for c in checks)


def test_reports_cannot_escape_runs_directory(tmp_path):
    with pytest.raises(ValueError, match="under simulation/v3/runs"):
        gates.write_report(tmp_path, {})


def test_review_eligibility_cannot_hide_an_available_winning_plan():
    e = review_fixture()
    e["gate_evidence"]["plans"][0]["available"] = False
    with pytest.raises(ValueError, match="eligibility"):
        gates.recompute_review(e)
    e = review_fixture()
    e["gate_evidence"]["plans"][0]["admission_evidence"]["active_bound"] = .5
    with pytest.raises(ValueError, match="eligibility"):
        gates.recompute_review(e)


def test_unavailable_or_unadmitted_plans_hold_without_substitution():
    for unavailable in (True, False):
        e = review_fixture()
        for p in e["gate_evidence"]["plans"]:
            if unavailable:
                p.update(continuation=None, available=False)
            else:
                p["admission_evidence"]["active_bound"] = 1.
                p["admitted"] = False
        e.update(decision=None, transition_count=0)
        e["gate_evidence"]["comparison_values"] = {}
        assert gates.check_review(({}, e)) and not gates.check_gamma(({}, e))


def test_tie_cannot_select_immediate_plan_while_claiming_hold():
    e = review_fixture(0.)
    e["decision"]["selected_plan"] = "now"
    assert not gates.check_review(({}, e))


@pytest.mark.parametrize("defect", ["completion", "step_count", "missing_job", "schema"])
def test_structurally_broken_hashed_artifacts_fail_closed(tmp_path, defect):
    from v3.artifacts import read
    p = artifact_fixture(tmp_path)
    evidence = read(p)
    if defect == "completion":
        doc = read(tmp_path / "complete.json")
        doc["status"] = "partial"
        atomic_json(tmp_path / "complete.json", doc)
        evidence["runs"][0]["completion"]["sha256"] = file_hash(tmp_path / "complete.json")
    elif defect == "step_count":
        doc = read(tmp_path / "run.json")
        doc["result"]["steps"] = 2
        atomic_json(tmp_path / "run.json", doc)
        new_hash = file_hash(tmp_path / "run.json")
        evidence["runs"][0]["output"]["sha256"] = new_hash
        complete = read(tmp_path / "complete.json")
        complete["output_hash"] = new_hash
        atomic_json(tmp_path / "complete.json", complete)
        evidence["runs"][0]["completion"]["sha256"] = file_hash(tmp_path / "complete.json")
    elif defect == "missing_job":
        evidence["runs"] = []
    else:
        evidence["schema"] = "unknown"
    atomic_json(p, evidence)
    with pytest.raises(ValueError):
        gates.load_runs(p, file_hash(p), fixtures=True)


def test_cli_refuses_before_opening_any_rerun_artifact_without_committed_a2(monkeypatch):
    import sys
    calibration = calibration_fixture()
    calibration["payload"].update(fixture=False, tag="v3_calibration")
    calibration = seal(calibration["payload"])
    monkeypatch.setattr(sys, "argv", ["v3.gates", "--phase", "all", "--calibration", "only-calibration.json"])
    monkeypatch.setattr(gates, "verify_instrument", lambda *_: {})
    def only_calibration(reference, _):
        assert Path(reference["path"]).name == "only-calibration.json"
        return calibration
    monkeypatch.setattr(gates, "verified_json", only_calibration)
    monkeypatch.setattr(gates, "before_checks", lambda _: [])
    monkeypatch.setattr(gates, "load_runs", lambda *a, **k: pytest.fail("rerun artifact opened before A2 pin"))
    with pytest.raises(ValueError, match="committed A2 pin"):
        gates.main()


# Artifacts stay inside the authorized tree even with default pytest options.
from test_v3_paths import tmp_path
