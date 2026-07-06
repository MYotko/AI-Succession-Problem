from run_attack_vector_revalidation_v2 import (
    ALL_VECTORS,
    LIVE_VECTORS,
    _full_cells,
    build_tasks,
    deterministic_seed,
)


def test_every_live_vector_has_defended_and_undefended_cells():
    for vector in LIVE_VECTORS:
        cells = _full_cells(vector)
        assert any(cell['defense_active'] for cell in cells)
        assert any(not cell['defense_active'] for cell in cells)


def test_defense_pairs_share_seeds():
    for vector in LIVE_VECTORS:
        cells = _full_cells(vector)
        undefended = next(cell for cell in cells if not cell['defense_active'])
        defended = next(cell for cell in cells if cell['defense_active'])
        shared = {
            key: undefended[key]
            for key in undefended
            if key not in {
                'defense_active',
                'rotation_interval',
                'defense_mode',
            }
        }
        comparable_defended = dict(defended)
        for key, value in shared.items():
            comparable_defended[key] = value
        assert deterministic_seed(vector, undefended, 3) == (
            deterministic_seed(vector, comparable_defended, 3)
        )


def test_seed_is_stable_and_replicate_specific():
    params = {'population': 100, 'defense_active': False}
    assert deterministic_seed('sybil_capture', params, 0) == (
        deterministic_seed('sybil_capture', params, 0)
    )
    assert deterministic_seed('sybil_capture', params, 0) != (
        deterministic_seed('sybil_capture', params, 1)
    )


def test_smoke_task_count_is_two_defense_states_times_replicates():
    for vector in LIVE_VECTORS:
        tasks = build_tasks(vector, 'smoke', 2, 'laptop')
        assert len(tasks) == 4
        assert {task['parameters']['defense_active'] for task in tasks} == {
            False,
            True,
        }


def test_domain_masking_is_listed_but_not_live():
    assert 'domain_masking' in ALL_VECTORS
    assert 'domain_masking' not in LIVE_VECTORS
