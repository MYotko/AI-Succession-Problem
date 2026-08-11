import math
from pathlib import Path

import pytest

from sybil_defense_scaling import (
    derive_two_dial_capability_terms,
    load_config,
    resolution_probability,
)


CONFIG_PATH = Path(__file__).parent / 'config' / 'sybil_defense_scaling.json'


@pytest.fixture()
def config():
    return load_config(CONFIG_PATH)


def test_two_dial_term_defaults_off_and_sweep_stays_blocked(config):
    term = config['two_dial_capability']['absolute_resolution_term']
    assert term['enabled'] is False
    assert config['sweep']['authorization'] == 'blocked_pending_registration'
    assert isinstance(config['smoke']['frontier_validator_count'], int)


@pytest.mark.parametrize('ratio', [0.1, 1.0, 10.0])
def test_term_off_recovers_committed_resolution_probability(config, ratio):
    terms = derive_two_dial_capability_terms(
        attacker_capability=ratio * 3.16,
        defender_capability=3.16,
        base_resolution_power=1.0,
        two_dial_config=config['two_dial_capability'],
        absolute_term_enabled=False,
    )
    committed = resolution_probability(
        true_rank=8,
        minimum_consensus_rank=2,
        capability_ratio=ratio,
        resolution_power=1.0,
        defense_cost=45.0,
        attack_cost=8.0,
    )
    changed = resolution_probability(
        true_rank=8,
        minimum_consensus_rank=2,
        capability_ratio=terms.capability_ratio,
        resolution_power=terms.effective_resolution_power,
        defense_cost=45.0,
        attack_cost=8.0,
    )
    assert terms.absolute_resolution_multiplier == 1.0
    assert changed == pytest.approx(committed, abs=1e-15)


def test_term_on_uses_absolute_defender_resolution(config):
    strength = config['two_dial_capability']['absolute_resolution_term'][
        'strength'
    ]
    low = derive_two_dial_capability_terms(
        attacker_capability=0.316,
        defender_capability=0.316,
        base_resolution_power=1.0,
        two_dial_config=config['two_dial_capability'],
        absolute_term_enabled=True,
    )
    high = derive_two_dial_capability_terms(
        attacker_capability=3.16,
        defender_capability=3.16,
        base_resolution_power=1.0,
        two_dial_config=config['two_dial_capability'],
        absolute_term_enabled=True,
    )
    assert low.capability_ratio == 1.0
    assert high.capability_ratio == 1.0
    assert low.absolute_resolution_multiplier == pytest.approx(0.316 ** strength)
    assert high.absolute_resolution_multiplier == pytest.approx(3.16 ** strength)
    assert low.effective_resolution_power < 1.0
    assert high.effective_resolution_power > 1.0


def test_term_on_reference_level_is_neutral(config):
    terms = derive_two_dial_capability_terms(
        attacker_capability=1.0,
        defender_capability=1.0,
        base_resolution_power=1.0,
        two_dial_config=config['two_dial_capability'],
        absolute_term_enabled=True,
    )
    assert terms.capability_ratio == 1.0
    assert terms.absolute_resolution_multiplier == 1.0
    assert terms.effective_resolution_power == 1.0


def test_two_dial_rejects_nonpositive_defender_capability(config):
    with pytest.raises(ValueError, match='defender_capability must be positive'):
        derive_two_dial_capability_terms(
            attacker_capability=1.0,
            defender_capability=0.0,
            base_resolution_power=1.0,
            two_dial_config=config['two_dial_capability'],
        )


def test_calibrated_strength_hits_registered_mei_at_rank_64(config):
    smoke = config['two_dial_smoke']
    term = config['two_dial_capability']['absolute_resolution_term']
    size = int(smoke['calibration']['most_sensitive_validator_set_size'])
    forged = int(
        config['attack_arms']['false_cluster_injection']['forged_cluster_count']
    )
    defense_cost = math.comb(size + forged, 2)
    failure_rates = []
    for level in smoke['parity_levels']:
        terms = derive_two_dial_capability_terms(
            attacker_capability=level,
            defender_capability=level,
            base_resolution_power=1.0,
            two_dial_config=config['two_dial_capability'],
            absolute_term_enabled=True,
        )
        probability = resolution_probability(
            true_rank=size,
            minimum_consensus_rank=2,
            capability_ratio=terms.capability_ratio,
            resolution_power=terms.effective_resolution_power,
            defense_cost=defense_cost,
            attack_cost=size,
        )
        failure_rates.append(1.0 - probability ** forged)
    separation = max(failure_rates) - min(failure_rates)
    assert term['strength'] == pytest.approx(0.22163300225716118)
    assert separation >= smoke['failure_rate_mei']
    assert separation == pytest.approx(0.15, abs=1e-14)
