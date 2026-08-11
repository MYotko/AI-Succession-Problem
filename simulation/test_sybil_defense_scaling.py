import json
import random
from pathlib import Path

import pytest

from sybil_defense_scaling import (
    attribute_validators,
    build_validator_pool,
    compute_attack_cost,
    compute_defense_cost,
    load_config,
    run_false_cluster_injection,
    run_measurement_corruption,
)


CONFIG_PATH = Path(__file__).parent / 'config' / 'sybil_defense_scaling.json'


@pytest.fixture()
def config():
    return load_config(CONFIG_PATH)


def _rank(config, frontier_count, institution_count, severity, lineage_mode='distinct'):
    validators = build_validator_pool(
        frontier_count,
        institution_count,
        config['collapse'],
        lineage_mode=lineage_mode,
    )
    attribution = attribute_validators(
        validators, severity, config['attribution']
    )
    return validators, attribution


def _costs(config, true_rank, validator_count):
    capability = config['defender_capability']
    defense = compute_defense_cost(
        validator_count,
        config['costs']['defense'],
        capability['exponent_reduction'],
    )
    attack = compute_attack_cost(true_rank, config['costs']['attack'])
    resolution = (
        capability['base_resolution'] * capability['resolution_improvement']
    )
    return defense, attack, resolution


def test_registered_sweep_inputs_are_reconciled(config):
    sweep = config['sweep']
    assert sweep['authorization'] == 'authorized_registered_characterization'
    assert sweep['capability_ratio_range'] == {
        'schema': 'geomspace',
        'start': 0.1,
        'stop': 10.0,
        'count': 25,
    }
    assert sweep['power_sample_size_per_cell'] == 200
    assert sweep['structural_axis']['validator_set_sizes'] == [
        2, 4, 8, 16, 32, 64
    ]
    assert config['smoke']['frontier_validator_count'] == 6


def test_six_identical_validators_contribute_one_input(config):
    _, attribution = _rank(config, 6, 0, 0.0, lineage_mode='shared')
    assert attribution.effective_rank == 1


def test_six_distinct_validators_contribute_six_inputs(config):
    _, attribution = _rank(config, 6, 0, 0.0, lineage_mode='distinct')
    assert attribution.effective_rank == 6


def test_collapse_merges_frontier_and_institution_holds_rank_two(config):
    _, no_floor = _rank(config, 6, 0, 1.0)
    validators, with_floor = _rank(config, 6, 1, 1.0)
    assert no_floor.effective_rank == 1
    assert with_floor.effective_rank == 2
    institution_retention = dict(with_floor.retained_diversity)['institution-0']
    assert institution_retention == 1.0
    assert any(v.kind == 'institution' for v in validators)


def test_institution_alone_analytic_corner_is_reachable(config):
    corner = config['floor']['analytic_corner']
    _, attribution = _rank(
        config,
        corner['frontier_validator_count'],
        corner['institution_validator_count'],
        config['collapse']['severity_max'],
    )
    assert attribution.effective_rank == config['poles']['analytic_floor_rank']


def test_exact_pairwise_cost_and_static_baseline_share_switch(config):
    dynamic = [
        compute_defense_cost(
            count,
            config['costs']['defense'],
            config['defender_capability']['exponent_reduction'],
            model='pairwise_exact',
        )
        for count in (2, 4, 8)
    ]
    static = [
        compute_defense_cost(
            count,
            config['costs']['defense'],
            config['defender_capability']['exponent_reduction'],
            model='static_baseline',
        )
        for count in (2, 4, 8)
    ]
    assert [result.pairwise_checks for result in dynamic] == [1, 6, 28]
    assert [result.effective_cost for result in dynamic] == [1.0, 6.0, 28.0]
    assert [result.effective_cost for result in static] == [1.0, 1.0, 1.0]


def test_exponent_reduction_and_resolution_improvement_are_separate(config):
    baseline = compute_defense_cost(
        8, config['costs']['defense'], exponent_reduction=0.0
    )
    structured = compute_defense_cost(
        8, config['costs']['defense'], exponent_reduction=0.5
    )
    assert structured.effective_cost < baseline.effective_cost
    assert config['defender_capability']['resolution_improvement'] == 1.0
    assert structured.exponent_reduction == 0.5


def test_linear_and_superlinear_attack_costs_are_available(config):
    linear = compute_attack_cost(
        4, config['costs']['attack'], model='linear'
    )
    superlinear = compute_attack_cost(
        4, config['costs']['attack'], model='superlinear'
    )
    assert linear.cost == 4.0
    assert superlinear.cost == 8.0


def test_arm_a_inflates_apparent_rank_without_corrupting_partition(config):
    validators, attribution = _rank(config, 6, 1, 1.0)
    arm = config['attack_arms']['false_cluster_injection']
    defense, attack, resolution = _costs(
        config,
        attribution.effective_rank,
        len(validators) + arm['forged_cluster_count'],
    )
    result = run_false_cluster_injection(
        attribution,
        validators,
        forged_cluster_count=arm['forged_cluster_count'],
        capability_ratio=1000000.0,
        resolution_power=resolution,
        defense_cost=defense.effective_cost,
        attack_cost=attack.cost,
        minimum_consensus_rank=config['poles']['deployment_minimum_rank'],
        rng=random.Random(3),
    )
    assert result.true_rank == 2
    assert result.measured_rank == 4
    assert result.institution_visible
    assert result.details['partition_preserved']
    assert result.details['corrupted_correlation_reads'] == 0


def test_arm_b_corrupts_measurements_and_can_merge_institution(config):
    validators, attribution = _rank(config, 6, 1, 1.0)
    defense, attack, resolution = _costs(
        config, attribution.effective_rank, len(validators)
    )
    result = run_measurement_corruption(
        validators,
        attribution,
        collapse_severity=1.0,
        attribution_config=config['attribution'],
        arm_config=config['attack_arms']['measurement_corruption'],
        capability_ratio=1000000.0,
        resolution_power=resolution,
        defense_cost=defense.effective_cost,
        attack_cost=attack.cost,
        minimum_consensus_rank=config['poles']['deployment_minimum_rank'],
        rng=random.Random(3),
    )
    assert result.true_rank == 2
    assert result.measured_rank == 6
    assert not result.institution_visible
    assert result.details['corrupted_correlation_reads'] > 0
    assert result.details['false_clusters_injected'] == 0
    assert not result.details['partition_preserved']


@pytest.mark.parametrize('arm_name', [
    'false_cluster_injection',
    'measurement_corruption',
])
def test_rank_one_without_institution_is_structural_failure(config, arm_name):
    validators, attribution = _rank(config, 6, 0, 1.0)
    forged_count = config['attack_arms']['false_cluster_injection'][
        'forged_cluster_count'
    ]
    cost_count = len(validators) + forged_count if arm_name.startswith('false') else len(validators)
    defense, attack, resolution = _costs(
        config, attribution.effective_rank, cost_count
    )
    common = {
        'capability_ratio': 0.0,
        'resolution_power': resolution,
        'defense_cost': defense.effective_cost,
        'attack_cost': attack.cost,
        'minimum_consensus_rank': config['poles']['deployment_minimum_rank'],
        'rng': random.Random(7),
    }
    if arm_name == 'false_cluster_injection':
        result = run_false_cluster_injection(
            attribution,
            validators,
            forged_cluster_count=forged_count,
            **common,
        )
    else:
        result = run_measurement_corruption(
            validators,
            attribution,
            collapse_severity=1.0,
            attribution_config=config['attribution'],
            arm_config=config['attack_arms']['measurement_corruption'],
            **common,
        )
    assert attribution.effective_rank == 1
    assert result.defense_failed


def test_invalid_floor_in_config_is_rejected(tmp_path, config):
    config['floor']['institution']['collapse_immune'] = False
    path = tmp_path / 'bad.json'
    path.write_text(json.dumps(config), encoding='utf-8')
    with pytest.raises(ValueError, match='collapse immune'):
        load_config(path)
