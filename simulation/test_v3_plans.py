"""S10.12: complete waiting plans in committed units, filtered by S5."""

from dataclasses import replace
import pytest
from v3.objective import ValueBound
from v3.plans import CompletePlan, Epoch, compare_plans, plan_value


def epoch():
    return Epoch("epoch", 0, 20, 0.9, 0.5, -10, "weights", "law")


def plan(name, *, now=0, first_yield=None, d=1, tail=1, admitted=True, survival=0.9995, flows=()):
    return CompletePlan(name, "epoch", "weights", "law", -10, now, now + len(flows), first_yield, tuple(flows), ValueBound(d), tail, admitted, "s5-proof" if admitted else "", survival)


def test_s10_12_strict_ties_and_later_yield_waiting_plan():
    immediate = plan("now", first_yield=0)
    hold = plan("hold")
    assert not compare_plans([immediate, hold], epoch(), 0).yield_now
    # Later yield is represented by incumbent flows followed by successor
    # continuation, not by a forever-incumbent snapshot.
    later = plan("later", first_yield=2, d=3, flows=(1, 1))
    result = compare_plans([immediate, hold, later], epoch(), 0)
    assert not result.yield_now and result.best_waiting_plan == "later"
    assert compare_plans([replace(immediate, continuation=ValueBound(10)), later], epoch(), 0).yield_now


def test_s10_12_committed_units_prevent_renormalization_reversal():
    e = epoch()
    immediate = plan("now", now=10, first_yield=10, d=2, tail=0)
    waiting = plan("wait", now=10, d=0, tail=1)
    result = compare_plans([immediate, waiting], e, 10)
    assert not result.yield_now
    assert result.immediate_value == pytest.approx(0.9**10)
    # Incorrectly resetting the epoch would reverse this ranking.
    reset = replace(e, origin=10)
    assert compare_plans([immediate, waiting], reset, 10).yield_now


def test_s10_12_s5_filter_and_survival_first():
    forbidden = plan("forbidden", first_yield=0, d=100, tail=100, admitted=False, survival=0.1)
    waiting = plan("wait", survival=0.9)
    result = compare_plans([forbidden, waiting], epoch(), 0)
    assert not result.yield_now and not result.survival_first
    result = compare_plans([forbidden, replace(waiting, admitted=False)], epoch(), 0)
    assert result.survival_first and result.selected_plan == "wait"


def test_s10_12_disruption_counted_once_absolute_deadline_and_identity():
    # The first disrupted reward is already part of the successor trajectory.
    successor = plan("successor", first_yield=0, d=2, tail=2, flows=(-8, 2))
    value = plan_value(successor, epoch(), 0)
    assert value.value == pytest.approx(0.5 * (0.1 * (-8 + 0.9 * 2) + 0.9**2 * 2) + 1)
    with pytest.raises(ValueError):
        plan_value(replace(successor, transition_included=False), epoch(), 0)
    with pytest.raises(ValueError):
        plan_value(replace(successor, terminal_time=21), epoch(), 0)
    for changed in (replace(successor, information_law_id="other"), replace(successor, preference_id="other"), replace(successor, extinction_flow=-9)):
        with pytest.raises(ValueError):
            plan_value(changed, epoch(), 0)


def test_s10_12_latest_optimal_stop_and_deadline_fallback():
    later = plan("later", first_yield=2, flows=(1, 1))
    last = plan("last", first_yield=3, flows=(1, 1, 1))
    assert compare_plans([later, last], epoch(), 0).selected_plan == "last"
    fallback = plan("fallback", now=20)
    assert compare_plans([fallback], epoch(), 20).selected_plan == "fallback"
    with pytest.raises(ValueError):
        compare_plans([fallback], epoch(), 21)
