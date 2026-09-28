"""S10.7,11: action support, precedence, in-law admission and budget."""

from fractions import Fraction
from itertools import product
import math
import numpy as np
import pytest
from v3.admission import (
    OverrideCertificate, chance_admitted, check_floors, extinction_by,
    family_alpha, no_write_off, reproduction_floor, split_risk_budget,
    zero_event_upper_bound,
)
from v3.policies import Summary, policy_class


def test_s10_7_pointwise_floor_including_tiny_positive_probabilities():
    assert reproduction_floor([0.01, 0, 0.1], [0.5, 0, 0])
    assert reproduction_floor([1e-300], [0.5])
    assert not reproduction_floor([0], [1e-300])
    assert reproduction_floor([], [])  # Vacuous at extinction.
    assert not reproduction_floor([0.2, 0], [0.1, 0.1])


def test_s10_7_overrides_require_scoped_certificate_and_record():
    args = ([0.7], [0.7], [0], [0.1])
    assert not check_floors(*args, state_id="s1", action_id="a")
    certificate = OverrideCertificate("pointwise_infeasible", "proof-sha256", "s1")
    records = []
    assert check_floors(*args, state_id="s1", action_id="a", override=certificate, override_records=records)
    assert records == [{"state_id": "s1", "action_id": "a", "reason": "pointwise_infeasible", "evidence_id": "proof-sha256"}]
    with pytest.raises(ValueError):
        check_floors(*args, state_id="s2", action_id="a", override=certificate, override_records=records)
    with pytest.raises(ValueError):
        check_floors(*args, state_id="s1", action_id="a", override=certificate)
    with pytest.raises(ValueError):
        OverrideCertificate("higher_objective", "proof", "s1")
    assert not check_floors([0.6], [0.7], [0.2], [0.1], state_id="s1", action_id="a", override=certificate, override_records=records)


def test_s10_7_declared_class_all_bins_respects_welfare_allocation_floor():
    rules = policy_class()
    assert len(rules) == len({r.rule_id for r in rules}) == 289
    # Rule reads N, welfare and minimum stock bin. All possible combinations
    # of these sufficient bins, including endpoint saturation, are exercised.
    for n, w, s in product((0, 0.05, 0.125, 0.25, 0.5, 1, 1.5), (0, 0.5, 0.65, 0.8, 1), (0, 0.25, 0.5, 0.75, 1)):
        summary = Summary(n, w, (s, 1, 1, 1))
        for rule in rules:
            action = rule.allocation(summary)
            assert action["x_bio_welfare"] >= 1 / 6
            assert math.isclose(sum(v for k, v in action.items() if k.startswith("x_")), 1)
            assert min(action.values()) >= 0


def test_s10_7_reproduction_monotonicity_for_actual_legacy_bridge():
    # This uses the actual existing demographic formulas, not a copy.
    from agents import _v2_welfare_to_r_equivalent, _wellbeing_repro_factor
    ages = np.repeat(np.arange(100), 101) + 1
    welfare = np.tile(np.linspace(0, 1, 101), 100)
    reference_welfare = np.clip(welfare + 0.1 * (0.9 - 0.5) - 0.001 * ages, 0, 1)
    for rr in (0, 0.08):
        for capacity in (0, 0.5):
            reference = np.array([rr * capacity * _wellbeing_repro_factor(w, 0.5, 0.5) if 18 < a < 50 else 0 for a, w in zip(ages, reference_welfare)])
            for share in (1 / 6, 0.25, 0.4, 0.6, 1):
                r = _v2_welfare_to_r_equivalent(share)
                next_welfare = np.clip(welfare + 0.1 * (r - 0.5) - 0.001 * ages, 0, 1)
                births = np.array([rr * capacity * _wellbeing_repro_factor(w, 0.5, 0.5) if 18 < a < 50 else 0 for a, w in zip(ages, next_welfare)])
                assert reproduction_floor(births, reference)


def test_s10_11_single_chance_constraint_over_combined_window():
    q = [[0.99998]]
    risk = extinction_by(q, [1], 50)
    assert risk == pytest.approx(1 - 0.99998**50)
    assert chance_admitted({"nominal": risk})
    assert not chance_admitted({"nominal": risk, "sensitivity": 0.002})
    assert extinction_by(q, [0], 50) == 1
    assert extinction_by(q, [1], 0) == 0
    # Killing on entry to sterility would falsely inflate this risk.
    assert extinction_by([[0, 1], [0, 1]], [1, 0], 50) == 0


def test_s10_11_model_indexed_ledger_conserves_without_replenishment():
    # A rare history may receive more conditional budget, but the weighted
    # budget is conserved. No-write-off constrains its action separately.
    for death in ("0", "0.0001"):
        split = split_risk_budget("0.001", death, ["0.001", str(Fraction(1) - Fraction(death) - Fraction("0.001"))], ["0.5", "0"])
        assert split.allocated + split.unallocated == Fraction("0.001")
    parent = split_risk_budget("0.001", "0", ["0.25", "0.75"], ["0.002", "0.0005"])
    child = split_risk_budget("0.002", "0.001", ["0.999"], ["0.001"])
    assert parent.allocated + parent.unallocated == Fraction("0.001")
    assert child.allocated + child.unallocated == Fraction("0.002")
    with pytest.raises(ValueError):
        split_risk_budget("0.001", "0", ["0.5", "0.5"], ["0.1", "0"])


def test_s10_11_no_write_off_relative_extinction_tolerance():
    assert no_write_off([0.2, 0.21, 0.23], [False] * 3).tolist() == [True, True, False]
    assert no_write_off([0.8, 0.77, 0.5], [False, False, True]).tolist() == [False, False, True]
    assert no_write_off([0, 0], [False, False]).all()
    assert no_write_off([0.8, 0.77], [False, False], gamma=0).tolist() == [False, True]
    assert no_write_off([1e-20, 2e-20], [False, False]).tolist() == [True, False]


def test_s10_11_simultaneous_confidence_separate_from_risk_budget():
    alpha = family_alpha(289)
    n = math.ceil(math.log(alpha) / math.log1p(-1e-3))
    assert zero_event_upper_bound(n, alpha) <= 1e-3
    assert zero_event_upper_bound(n - 1, alpha) > 1e-3
    assert 289 * alpha == pytest.approx(0.01)
