"""A1: missing values exclude candidates without inventing objective values."""
import numpy as np
import pytest
from v3.artifacts import canonical, digest, stable_job
from v3.integration import V3Model
from v3.policies import execution_policy_class
from v3.production_tables import ProductionTables, write_tables, row_key, AvailableLookup
from v3.production_runner import execute
from v3.plans import YieldDecision
from v3.unpublished_bins import coverage_bounds, endpoint_counts


def model(**kwargs):
    return V3Model(200, rules=execution_policy_class()[:3], rollout_steps=1, successor_capability=None, **kwargs)


def sparse_tables(m, tmp_path, absent=(), missing_rows=()):
    endpoint = m.evaluate().terminal.summary_bins(m.capacity)
    rows = []
    for i, rule in enumerate(m.rules):
        if i in missing_rows:
            continue
        rows.append({"rule_id": rule.rule_id, "rule_hash": digest(rule.__dict__), "kernel_hash": m.kernel_hash,
                     "calibration_hash": m.calibration_hash, "scoring": {"alpha": m.alpha, "capability": m.capability, "kappa": m.parameters.kappa},
                     "status": "estimated", "lambda_f": {"mean": 100. - i}, "flow_range": 200.,
                     "continuation": {"entries": [] if i in absent else [{"bin": endpoint[i].tolist(), "value": 100. - i, "error": 200.}]}})
    document = write_tables(tmp_path / "tables.json", rows,
                            {"required_row_keys": [row_key(r) for r in rows], "calibration_hash": m.calibration_hash, "tag": "pilot"}, fixture=True)
    m.tables = ProductionTables(document, calibration_hash=m.calibration_hash)
    return m


@pytest.mark.parametrize("missing_row", [False, True])
def test_one_unavailable_rule_is_omitted_and_counted(tmp_path, missing_row):
    m = sparse_tables(model(), tmp_path, absent=() if missing_row else (0,), missing_rows=(0,) if missing_row else ())
    evaluated = m.evaluate()
    assert not evaluated.available[0] and np.isnan(evaluated.scores[0])
    record = m.step()
    assert record["chosen_rule"] != "balanced"
    assert record["unavailable_rule_count"] == 1 and not record["balanced_fallback"]
    expected = "missing_or_not_estimable_row" if missing_row else "unpublished_continuation_bin"
    assert record["unavailable_rules"] == {"balanced": expected}
    canonical(record)  # No NaN or infinity in durable records.


def test_all_unavailable_uses_balanced_without_a_score_and_preserves_floors(tmp_path):
    m = sparse_tables(model(), tmp_path, absent=(0, 1, 2))
    record = m.step()
    assert record["chosen_rule"] == "balanced" and record["balanced_fallback"]
    assert record["unavailable_rule_count"] == 3
    assert record["balanced_fallback_reason"] == "all_rule_scores_unavailable"
    assert all(record[k] is None for k in ("W", "D_rho", "Lambda_F", "W_error_enclosure"))
    assert record["welfare_floor_holds"] and record["reproduction_floor_holds"]
    assert not m.override_records[-1]["reproduction_floor_overridden"]
    canonical(record)


def test_no_scoreable_admitted_rule_falls_back_without_relaxing_risk_filter(tmp_path, monkeypatch):
    m = sparse_tables(model(), tmp_path, absent=(0,))
    monkeypatch.setattr(m, "_eligible", lambda actions: (np.array([True, False, False]), np.array([-3., -2., -1.]), False))
    record = m.step()
    assert record["balanced_fallback"] and record["balanced_fallback_reason"] == "no_scoreable_rule_passes_admission"
    assert record["unavailable_rule_count"] == 1 and record["W"] is None


def test_extinct_endpoint_is_exact_but_does_not_invent_missing_tail_row(tmp_path):
    m = sparse_tables(model(), tmp_path, absent=(0,), missing_rows=(1,))
    state = m.state.repeat(3)
    state.ages[:] = -1
    lookup = m._lookup(state, m.rules, m.capability)
    assert lookup.available.tolist() == [True, False, True]
    assert lookup.continuation[0] == m.parameters.extinction_flow and lookup.continuation_error[0] == 0
    assert np.isnan(lookup.lambda_f[1])


class SelectivePlans:
    def __init__(self, original, all_missing=False):
        self.original, self.all_missing, self.fixture = original, all_missing, True
        self.lookup = original.lookup

    def lookup_available(self, rules, bins, **context):
        result = self.original.lookup(rules, bins, **context)
        available = np.zeros(len(rules), bool) if self.all_missing else np.array([False, True, True])
        arrays = [np.where(available, a, np.nan) for a in (result.continuation, result.continuation_error, result.lambda_f, result.lambda_error)]
        return AvailableLookup(*arrays, result.lambda_b, result.lifetime_surplus, True, available,
                               tuple(None if x else "unpublished_continuation_bin" for x in available))


def test_yield_comparison_omits_unavailable_complete_plans(monkeypatch):
    m = model()
    m.successor_capability = 1.5
    m.tables = SelectivePlans(m.tables)
    captured = []
    def compare(plans, epoch, now):
        captured.extend(plans)
        hold = next(p for p in plans if p.first_yield is None)
        return YieldDecision(False, hold.plan_id, hold.plan_id, 1., 2., False)
    monkeypatch.setattr("v3.integration.compare_plans", compare)
    record = m.step()
    event = m.yield_events[0]
    assert len(captured) == 8 and event["plan_count"] == 12
    assert all(not p.plan_id.endswith("balanced") for p in captured)
    assert event["unavailable_plan_count"] == 4 and event["admissible_plan_count"] == 8
    assert record["yield_unavailable_plan_count"] == 4
    assert not record["yield_held_no_admissible_plan"]
    canonical(record); canonical(event)


def test_no_available_plan_holds_yield_and_records_reason(monkeypatch):
    m = model()
    m.successor_capability = 1.5
    m.tables = SelectivePlans(m.tables, all_missing=True)
    monkeypatch.setattr("v3.integration.compare_plans", lambda *args: pytest.fail("empty plan comparison"))
    record = m.step()
    event = m.yield_events[0]
    assert event["decision"] is None and event["unavailable_plan_count"] == 12
    assert event["admissible_plan_count"] == 0 and event["yield_held_no_admissible_plan"]
    assert m.transition_count == 0 and m.capability == 1.
    assert record["balanced_fallback"] and record["yield_held_no_admissible_plan"]
    canonical(record); canonical(event)


def test_runner_aggregates_each_step_counts(tmp_path, monkeypatch):
    m = sparse_tables(model(), tmp_path, absent=(0, 1, 2))
    monkeypatch.setattr("v3.integration.V3Model", lambda **kwargs: m)
    job = stable_job("rerun", {"steps": 3}, "validation", 0)
    result = execute(job)
    counts = result["continuation_availability"]
    assert counts["allocation_steps"] == 3 and counts["rule_exclusions_total"] == 9
    assert counts["balanced_fallback_steps"] == counts["steps_with_rule_exclusions"] == 3
    assert set(counts["rule_exclusions_by_rule"].values()) == {3}
    canonical(result)


def test_absorbed_step_does_not_count_an_allocation_or_fallback():
    m = V3Model(0, successor_capability=None)
    record = m.step()
    assert not record["allocation_evaluated"] and not record["balanced_fallback"]
    assert record["unavailable_rule_count"] == record["yield_unavailable_plan_count"] == 0


def test_endpoint_analysis_uses_post_action_horizon_and_exact_extinction():
    features = np.ones((4, 6, 8))
    features[1:, 4, 0] = 0  # Dies before the first horizon endpoint.
    after = np.zeros((4, 6, 6), dtype=np.int8)
    after[1, 5, 0] = 1  # Only the first live endpoint is missing.
    trace = {"features": features, "after": after, "groups": np.arange(6)}
    result = endpoint_counts(trace, {(0,) * 6}, horizon=2, steps=3)
    assert result["heldout_paths"] == 2 and result["allocation_opportunities"] == 5
    assert result["exact_extinct_endpoints"] == 2 and result["unpublished_endpoints"] == 1
    assert result["exclusion_fraction"] == .2


def test_archived_coverage_is_a_source_bound_not_an_endpoint_rate():
    row = {"continuation": {"heldout_transitions": 100, "heldout_coverage": .95,
                            "entries": [{"heldout_visits": 90}]}}
    bounds = coverage_bounds(row)
    assert bounds["unpublished_source_fraction_lower"] == pytest.approx(.05)
    assert bounds["unpublished_source_fraction_upper"] == pytest.approx(.1)
    row["continuation"]["legacy_all_training_bins"] = {"heldout_coverage": 1.}
    with pytest.raises(ValueError, match="legacy entry counts"):
        coverage_bounds(row)


def test_endpoint_audit_cannot_run_registered():
    with pytest.raises(ValueError, match="validation only"):
        execute(stable_job("continuation_audit", {}, "v3_rerun", 0), registered=True)
