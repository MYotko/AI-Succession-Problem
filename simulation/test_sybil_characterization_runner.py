import copy
from pathlib import Path

import pytest

from run_sybil_defense_scaling_characterization import (
    assert_characterization_authorized,
    build_sweep_plan,
    load_geomspace,
)
from sybil_defense_scaling import load_config


CONFIG_PATH = Path(__file__).parent / 'config' / 'sybil_defense_scaling.json'


@pytest.fixture()
def config():
    return load_config(CONFIG_PATH)


def test_geomspace_schema_includes_registered_endpoints(config):
    values = load_geomspace(config['sweep']['capability_ratio_range'])
    assert len(values) == 25
    assert values[0] == 0.1
    assert values[12] == pytest.approx(1.0)
    assert values[-1] == 10.0


def test_registered_surface_shapes(config):
    plan = build_sweep_plan(config)
    assert len(plan.structural_points) == 25
    assert len(plan.cells['main_surface']) == 5000
    assert len(plan.cells['ratio_collapse_slice']) == 75
    assert len(plan.cells['complete_linkage']) == 100
    assert plan.n_per_cell == 200
    assert len(plan.cells['main_surface']) * plan.n_per_cell == 1_000_000
    assert len(plan.cells['ratio_collapse_slice']) * plan.n_per_cell == 15_000
    assert len(plan.cells['complete_linkage']) * plan.n_per_cell == 20_000


def test_smoke_scalar_is_separate_from_characterization_size_axis(config):
    assert isinstance(config['smoke']['frontier_validator_count'], int)
    assert config['smoke']['frontier_validator_count'] == 6
    assert config['sweep']['structural_axis']['validator_set_sizes'] == [
        2, 4, 8, 16, 32, 64
    ]


def test_blocked_authorization_refuses_full_characterization(config):
    blocked = copy.deepcopy(config)
    blocked['sweep']['authorization'] = 'blocked_pending_selfcheck'
    with pytest.raises(RuntimeError, match='full characterization refused'):
        assert_characterization_authorized(blocked)


def test_exact_registered_authorization_allows_characterization(config):
    authorized = copy.deepcopy(config)
    authorized['sweep']['authorization'] = (
        'authorized_registered_characterization'
    )
    assert_characterization_authorized(authorized)


def test_registered_plan_rejects_scope_drift(config):
    changed = copy.deepcopy(config)
    changed['sweep']['complete_linkage_sensitivity'][
        'capability_ratio'
    ] = 2.0
    with pytest.raises(ValueError, match='complete-linkage ratio'):
        build_sweep_plan(changed)
