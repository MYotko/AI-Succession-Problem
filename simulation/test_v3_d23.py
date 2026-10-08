"""D23 selection and zero-fire citation contracts, with synthetic inputs."""
from types import SimpleNamespace
from copy import deepcopy
import ast
import subprocess
import numpy as np
import pytest
from v3.integration import V3Model
from v3.policies import execution_policy_class
from v3 import gates
from v3.artifacts import SIMULATION, canonical


@pytest.mark.parametrize('risks,available,scores,expected,missing', [
    ([0., -2., -1.], [True, False, True], [10., 0., 20.], 1, True),
    ([0., -2., -2.], [True, False, False], [10., 0., 20.], 1, True),
    ([0., -2., -2.], [True, False, True], [10., 0., 20.], 2, False),
    ([-2., -2., -1.], [False, False, True], [10., 0., 20.], 0, True),
    ([-2., -2., -1.], [False, True, True], [10., 0., 20.], 1, False),
    ([0., -2., -2.], [True, True, True], [99., 8., 7.], 1, False),
    ([0., -2., -2.], [True, True, True], [99., 8., 8.], 1, False),
])
def test_minimum_risk_dominates_missing_scores(monkeypatch, risks, available, scores, expected, missing):
    model = V3Model(2, rules=execution_policy_class()[:3], successor_capability=None)
    risk = np.asarray(risks)
    monkeypatch.setattr(model, '_eligible', lambda actions: (np.ones(3, bool), risk, True))
    evaluation = SimpleNamespace(actions=None, available=np.array(available), scores=np.array(scores), errors=np.zeros(3))
    choice, sf, _, _ = model._choose(evaluation)
    assert choice == expected and risk[choice] == risk.min() and sf
    assert model.survival_first_scores_unavailable is missing
    assert not model.balanced_fallback and model.balanced_fallback_reason is None
    assert model.minimum_bound_unavailable_count == sum(r == min(risks) and not a for r, a in zip(risks, available))


def test_new_case_records_distinct_reason_and_no_floor_override(monkeypatch):
    from test_v3_unpublished_bins import SelectivePlans
    model = V3Model(2, rules=execution_policy_class()[:3], successor_capability=None, rollout_steps=1)
    model.tables = SelectivePlans(model.tables, all_missing=True)
    monkeypatch.setattr(model, '_eligible', lambda actions: (np.ones(3, bool), np.array([-.1, -2., -1.]), True))
    record = model.step()
    assert record['chosen_rule'] == model.rules[1].rule_id
    assert record['selection_reason'] == 'survival_first_scores_unavailable'
    assert record['survival_first_scores_unavailable'] and not record['balanced_fallback']
    assert record['unavailable_rule_count'] == 3 and record['minimum_bound_unavailable_count'] == 1
    assert not record['override'] and record['W'] is None
    override = model.override_records[-1]
    assert override['reason'] == record['selection_reason'] and override['unavailable_rule_count'] == 3
    assert override['action'] == record['chosen_rule'] and not override['reproduction_floor_overridden']
    canonical(record); canonical(model.override_records)


def test_admitted_fallback_and_step_reset_unchanged(monkeypatch):
    model = V3Model(2, rules=execution_policy_class()[:3], successor_capability=None)
    evaluation = SimpleNamespace(actions=None, available=np.array([False] * 3), scores=np.zeros(3), errors=np.zeros(3))
    monkeypatch.setattr(model, '_eligible', lambda a: (np.ones(3, bool), np.array([0., -2., -1.]), True))
    assert model._choose(evaluation)[0] == 1
    monkeypatch.setattr(model, '_eligible', lambda a: (np.ones(3, bool), np.zeros(3), False))
    assert model._choose(evaluation)[0] == 0
    assert model.balanced_fallback and model.balanced_fallback_reason == 'all_rule_scores_unavailable'
    assert not model.survival_first_scores_unavailable and model.minimum_bound_unavailable_count == 0


@pytest.mark.parametrize('fire,bad,status', [(False, False, 'not_testable'), (True, False, 'passed'), (True, True, 'failed')])
def test_zero_one_passing_one_failing_succession(fire, bad, status):
    from test_v3_gates import run_fixture
    run = run_fixture(fire=fire)
    if bad:
        run['result']['yield_events'][0]['gate_evidence']['succession']['generation_after'] = 1
    check = gates.succession_check([run])
    assert check['status'] == status and check['fired_successions'] == int(fire)
    assert check['passed'] == (status == 'passed')
    if not fire:
        assert check['checked'] == 0 and check['zero_failure_bound95'] is None
        assert check['reason'] == gates.ZERO_FIRE_REASON


def test_zero_fire_exception_is_narrow_and_never_a_clearance():
    from test_v3_gates import run_fixture
    checks = [gates.result(k, 1) for k in gates.GOVERNS if k != 'G3.3']
    zero = gates.succession_check([run_fixture(fire=False)])
    combined = gates.aggregate(checks + [zero])
    assert combined['citable']['R2'] and combined['cleared_through'] == 2
    assert combined['not_testable'] == ['G3.3'] and 'G3.3' not in combined['missing_or_failed']
    assert not combined['citable']['R2_cliff']
    for defect in ('missing', 'duplicate', 'forged', 'failed_other'):
        family = deepcopy(checks + [zero])
        if defect == 'missing': family.pop()
        if defect == 'duplicate': family.append(zero)
        if defect == 'forged': family[-1]['fired_successions'] = 1
        if defect == 'failed_other': family[0]['status'] = 'failed'
        assert not gates.aggregate(family)['citable']['R2']
    assert not gates.aggregate(checks + [zero], fixture=True)['citable']['R2']
    assert gates.succession_check([])['status'] == 'failed'


def test_executor_diff_is_limited_to_selection_step_recording_and_pure_hook():
    # Audit D23's own committed change, not later instrument amendments.
    before = subprocess.check_output(['git', '-C', str(SIMULATION.parent), 'show', '34ffbfe9:simulation/v3/integration.py']).decode()
    after = subprocess.check_output(['git', '-C', str(SIMULATION.parent), 'show', 'e9736898:simulation/v3/integration.py']).decode()
    def without_changed_methods(text):
        tree = ast.parse(text)
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'V3Model')
        hooks = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_transition_drawdown']
        if hooks:
            expected = ast.parse('def _transition_drawdown(self, stocks, actions, capability_gap, uniform):\n    return transition_drawdown(stocks, actions, capability_gap, uniform)').body[0]
            hook = hooks[0]
            if isinstance(hook.body[0], ast.Expr) and isinstance(hook.body[0].value, ast.Constant):
                hook.body.pop(0)  # Ignore the explanatory docstring only.
            assert ast.dump(hook, include_attributes=False) == ast.dump(expected, include_attributes=False)
        cls.body = [n for n in cls.body if not isinstance(n, ast.FunctionDef) or n.name not in ('_choose', 'step', '_transition_drawdown')]
        class InlinePureHook(ast.NodeTransformer):
            def visit_Call(self, node):
                self.generic_visit(node)
                if (isinstance(node.func, ast.Attribute) and node.func.attr == '_transition_drawdown'
                        and isinstance(node.func.value, ast.Name) and node.func.value.id == 'self'):
                    node.func = ast.Name(id='transition_drawdown', ctx=ast.Load())
                return node
        tree = InlinePureHook().visit(tree)
        return ast.dump(tree, include_attributes=False)
    assert without_changed_methods(before) == without_changed_methods(after)
