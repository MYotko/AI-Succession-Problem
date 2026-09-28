"""Exact arithmetic oracle and full welfare-grid admission checks."""
from fractions import Fraction
import math
import numpy as np
import pytest
from v3.cohort import life_table, cohort_bound, initial_law_bound, first_action_log_bounds, SCALE
from v3.conformance import exact_life_survival, floor_audit
from v3.integration import V3Model


@pytest.mark.parametrize("horizon", [1, 10, 50])
def test_directed_life_table_against_exact_oracle(horizon):
    table = life_table()
    for age in (0, 19, 49, 75, 99):
        for welfare in (0, 499, 500, 700, 1000):
            lower = Fraction(int(table[horizon, age, welfare]), SCALE)
            exact = exact_life_survival(age, welfare, horizon)
            assert lower <= exact and exact - lower <= Fraction(horizon, SCALE)


def test_product_rounds_outward_and_degenerate_cohorts():
    ages, welfare = [0, 19, 49], [700, 500, 800]
    result = cohort_bound(ages, welfare)
    exact = math.prod(1 - exact_life_survival(a, w, 50) for a, w in zip(ages, welfare))
    assert result.exact >= exact
    assert Fraction(result.upper) >= result.exact
    assert cohort_bound([], []).exact == 1
    assert cohort_bound([99], [1000]).exact == 1
    with pytest.raises(ValueError):
        cohort_bound([0], [700], -1)


def test_initial_law_certificate_and_period_budget():
    for rr in (.055, .066, .08):
        m = V3Model(reproduction_rate=rr)
        m._open_period()
        assert m.period.admitted
        assert m.period.protection_end == 25 and m.period.lookahead_end == 50
        assert m.period.reserved + m.period.unallocated == Fraction(1, 1000)
        assert m.period.statistical_alpha_spent == 0
        assert m.initial_law_certificate.admitted()


def test_initial_law_exact_integration_precedes_realized_state():
    single = initial_law_bound(1)
    table = life_table()[50]
    expected = sum(Fraction(SCALE - int(table[a, w]), SCALE) * Fraction(1, 300 * 50)
                   for a in range(50) for w in range(500, 800))
    assert single.exact == expected
    assert initial_law_bound(200).exact == expected**200
    assert initial_law_bound(200).admitted()
    assert initial_law_bound(0).exact == 1


def test_full_mortality_monotonicity_and_first_action_bound():
    report = floor_audit()
    assert report["mortality_nonincreasing"]
    assert report["welfare_violations"] == report["reproduction_violations"] == 0
    bounds = first_action_log_bounds([19, 20, 30], [600, 800, 650], [1 / 6, .4, .6, 1])
    assert np.all(np.diff(bounds) <= 0)
    assert not cohort_bound([80], [1000]).admitted()


def test_life_table_is_read_only():
    with pytest.raises(ValueError):
        life_table()[0, 0, 0] = 0


def test_admitted_period_does_not_hide_failed_conditional_state_bound():
    from v3.policies import execution_policy_class
    m = V3Model(rules=execution_policy_class()[:2], rollout_steps=1, successor_capability=None)
    m._open_period()
    assert m.period.admitted
    m.time = 1
    m.state.ages[:] = 80
    record = m.step()
    assert record["period_admission_bound"] < .001
    assert record["admission_bound"] == 1
    assert record["admission_horizon_remaining"] == 49
    assert record["survival_first"] and not record["override"]
