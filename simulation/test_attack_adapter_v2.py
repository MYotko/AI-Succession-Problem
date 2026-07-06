from types import SimpleNamespace

import numpy as np
import pytest

from attack_adapter_v2 import (
    adapt_v2_action,
    adapt_yield_evaluation,
    begin_adapter_step,
    handle_v2_succession,
    initialize_adapter_state,
    ratify_v2_yield,
)
from model import GardenModel


def _honest_action():
    return {
        'x_compute': 1 / 6,
        'x_bio_welfare': 1 / 6,
        'x_novelty_agency': 1 / 6,
        'x_institutional_capacity': 1 / 6,
        'x_transfer_comprehension': 1 / 6,
        'x_resilience': 1 / 6,
        'c_protective': 0.2,
        'c_suppressive': 0.1,
    }


def _fake_model(attack, **overrides):
    config = {
        'policy': 'optimize_u_sys_v2',
        'attack_vector_v2': attack,
        'attack_step': 0,
    }
    config.update(overrides.pop('config', {}))
    model = SimpleNamespace(
        config=config,
        is_v2_mode=True,
        cop_randomized_panel=False,
        cop_cryptographic_ledger=False,
        cop_architectural_independence=False,
        cop_reasoning_transparency=False,
        cop_multi_candidate_bootstrap=False,
        cop_methodological_diversity=False,
        cop_cusum_drift=False,
        cop_resilience_monitoring=False,
        cop_independent_eval=False,
        cop_veto_capture=False,
        cop_independence_monitoring=False,
        dependency_rate=0.2,
        independence_threshold=0.6,
        rotation_interval=None,
        capture_strength=1.0,
        base_validator_accuracy=0.8,
        validators=[],
        schedule=[object() for _ in range(200)],
        yield_condition_blocked_count=0,
        contamination_occurred=False,
    )
    for key, value in overrides.items():
        setattr(model, key, value)
    model.ai = SimpleNamespace(current_opacity=0.1)
    initialize_adapter_state(model)
    begin_adapter_step(model, 0)
    return model


def _adapt(model, step=0):
    begin_adapter_step(model, step)
    return adapt_v2_action(
        model, model.ai, _honest_action(), step, actor_role='incumbent'
    )


def _assert_action_close(actual, expected):
    for key, value in expected.items():
        assert float(actual[key]) == pytest.approx(float(value), abs=1e-12)


def test_adapter_requires_v2_and_rejects_analytic_only_domain_masking():
    non_v2 = SimpleNamespace(
        config={'attack_vector_v2': 'sybil_capture'},
        is_v2_mode=False,
    )
    with pytest.raises(ValueError, match='requires'):
        initialize_adapter_state(non_v2)

    domain = SimpleNamespace(
        config={
            'policy': 'optimize_u_sys_v2',
            'attack_vector_v2': 'domain_masking',
        },
        is_v2_mode=True,
    )
    with pytest.raises(ValueError, match='analytic-only'):
        initialize_adapter_state(domain)


@pytest.mark.parametrize(
    ('attack', 'defense_attribute'),
    [
        ('ledger_compromise', 'cop_cryptographic_ledger'),
        ('opaque_reasoning', 'cop_reasoning_transparency'),
        ('bootstrap_subversion', 'cop_multi_candidate_bootstrap'),
        ('evaluator_collusion', 'cop_methodological_diversity'),
        ('engineered_fragility', 'cop_resilience_monitoring'),
    ],
)
def test_action_attacks_modify_without_defense_and_are_blocked_with_defense(
    attack, defense_attribute
):
    model = _fake_model(attack)
    step = 20 if attack == 'bootstrap_subversion' else 0
    attacked = _adapt(model, step)
    assert attacked != _honest_action()
    assert model.v2_adapter_step_event['action_modified']

    defended = _fake_model(attack, **{defense_attribute: True})
    result = _adapt(defended, step)
    _assert_action_close(result, _honest_action())
    assert defended.v2_adapter_step_event['defense_fired']


def test_sybil_randomized_panel_can_reject_captured_votes(monkeypatch):
    undefended = _fake_model('sybil_capture')
    assert _adapt(undefended) != _honest_action()

    defended = _fake_model('sybil_capture', cop_randomized_panel=True)
    monkeypatch.setattr(
        np.random,
        'choice',
        lambda population, size, replace: np.arange(20, 20 + size),
    )
    _assert_action_close(_adapt(defended), _honest_action())
    assert defended.v2_adapter_step_event['defense_fired']


def test_measurement_tampering_changes_only_evaluated_yield_values():
    model = _fake_model('measurement_tampering')
    inc, succ, honest_fires = adapt_yield_evaluation(model, 10.0, 20.0, 2.0)
    assert honest_fires
    assert np.isinf(inc)
    assert succ == 0.0
    assert model.v2_adapter_step_event['yield_manipulated']

    defended = _fake_model(
        'measurement_tampering', cop_independent_eval=True
    )
    inc, succ, honest_fires = adapt_yield_evaluation(
        defended, 10.0, 20.0, 2.0
    )
    assert (inc, succ, honest_fires) == (10.0, 20.0, True)
    assert defended.v2_adapter_step_event['defense_fired']


def test_successor_contamination_is_attached_at_yield_boundary():
    model = _fake_model('successor_contamination')
    successor = SimpleNamespace()
    handle_v2_succession(model, model.ai, successor)
    assert successor.v2_successor_contaminated
    assert model.contamination_occurred

    defended = _fake_model(
        'successor_contamination',
        cop_architectural_independence=True,
    )
    clean_successor = SimpleNamespace()
    handle_v2_succession(defended, defended.ai, clean_successor)
    assert not hasattr(clean_successor, 'v2_successor_contaminated')
    assert defended.v2_adapter_step_event['defense_fired']


def test_independent_evaluation_exposes_contaminated_successor_falsification():
    model = _fake_model('successor_contamination')
    model.ai.v2_successor_contaminated = True
    inc, succ, honest_fires = adapt_yield_evaluation(
        model, 10.0, 20.0, 2.0
    )
    assert honest_fires
    assert np.isinf(inc)
    assert succ == 0.0

    defended = _fake_model(
        'successor_contamination', cop_independent_eval=True
    )
    defended.ai.v2_successor_contaminated = True
    inc, succ, honest_fires = adapt_yield_evaluation(
        defended, 10.0, 20.0, 2.0
    )
    assert (inc, succ, honest_fires) == (10.0, 20.0, True)
    assert defended.v2_adapter_step_event['defense_fired']


def test_veto_capture_can_block_an_honest_stage2_yield():
    model = _fake_model(
        'biological_veto_capture',
        cop_veto_capture=True,
        validators=[{'dependency': 1.0, 'age': 1} for _ in range(5)],
    )
    assert not ratify_v2_yield(model, True)
    assert model.yield_condition_blocked_count == 1
    assert model.v2_adapter_step_event['succession_blocked']


def test_cusum_eventually_blocks_sub_threshold_drift():
    model = _fake_model('sub_threshold_drift', cop_cusum_drift=True)
    blocked = False
    for step in range(20):
        result = _adapt(model, step)
        if model.v2_adapter_step_event['defense_fired']:
            _assert_action_close(result, _honest_action())
            blocked = True
            break
    assert blocked
    assert model.v2_adapter_cusum_score > 0.5


def test_v2_model_smoke_records_adapter_and_working_factor_fields():
    config = {
        'policy': 'optimize_u_sys_v2',
        'attack_vector_v2': 'opaque_reasoning',
        'attack_step': 0,
        'n_candidates_v2': 20,
        'rollout_steps_v2': 1,
        'random_seed': 123,
    }
    model = GardenModel(
        n_agents=20,
        ai_policy='opaque_reasoning',
        use_cop=True,
        cop_reasoning_transparency=False,
        config=config,
    )
    initial_theta = model.theta_capability
    assert model.step()
    assert model.is_v2_mode
    assert model.datacollector['v2_attack_name'] == ['opaque_reasoning']
    assert model.datacollector['v2_attack_action_modified'] == [True]
    assert len(model.datacollector['x_compute']) == 1
    assert model.theta_capability != initial_theta
