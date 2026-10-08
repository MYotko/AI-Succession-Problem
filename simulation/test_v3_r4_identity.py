"""Permanent R4 scientific-byte regression against the fe98280c fixture.

The expected record is source-controlled. Test execution needs neither Git
nor calibration/table artifacts. Regeneration is a separate reviewed action.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from v3.integration import V3Model
from v3.recording import RecordedV3Model
from v3.policies import execution_policy_class


FIXTURE = {
    "instrument": {"mapping": "R4"},
    "paired_population_seeds": [[0, 11], [8, 12], [20, 13]],
    "rule_indices": [0, 12, 24],
    "successor_capabilities": [1.5, 3.0],
    "prefix_horizons": [1, 7, 20],
    "transition_offsets": ["none", "zero", "horizon_minus_one"],
    "live_steps": 40,
    "recorded_run": {"n_agents": 12, "seed": 871, "steps": 120, "successor_capability": 3.0},
    "serialization": "sorted compact ASCII JSON, allow_nan=false, trailing LF; raw uncompressed evidence",
    "other_parameters": "V3Model defaults at fe98280c; no calibration or table artifact",
}


def scientific_bytes(value):
    def clean(item):
        if isinstance(item, np.ndarray):
            return item.tolist()
        if isinstance(item, np.generic):
            return item.item()
        if isinstance(item, dict):
            return {k: clean(v) for k, v in item.items()}
        if isinstance(item, (list, tuple)):
            return [clean(v) for v in item]
        return item
    return json.dumps(clean(value), sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('utf-8') + b'\n'


def state_snapshot(state):
    return {k: getattr(state, k).copy() for k in
            ('ages', 'welfare', 'traits', 'bank', 'stocks', 'window', 'counts', 'h_n')}


def scientific_artifacts(*, instrument):
    """Use instrument=None only when regenerating from the pre-declaration code."""
    kwargs = {} if instrument is None else {'instrument': instrument}
    all_rules = execution_policy_class()
    rules = tuple(all_rules[i] for i in FIXTURE['rule_indices'])
    states, prefixes = [], []
    for population, seed in FIXTURE['paired_population_seeds']:
        for successor in FIXTURE['successor_capabilities']:
            model = V3Model(population, seed=seed, rules=rules, successor_capability=successor, **kwargs)
            case = {'population': population, 'seed': seed, 'successor': successor}
            states.append(dict(case, time=0, state=state_snapshot(model.state)))
            for horizon in FIXTURE['prefix_horizons']:
                for transition in (None, 0, horizon-1):
                    e = model.evaluate(horizon=horizon, capability=successor if transition is not None else 1.,
                                       transition_at=transition, incumbent_index=0)
                    prefixes.append(dict(case, horizon=horizon, transition=transition,
                        flows=e.flows, scores=e.scores, errors=e.errors, d_rho=e.d_rho, lambda_f=e.lambda_f,
                        actions=e.actions, terminal=state_snapshot(e.terminal)))
            steps = model.run(FIXTURE['live_steps'])
            states.append(dict(case, time=model.time, state=state_snapshot(model.state),
                               diagnostics=steps, yield_events=model.yield_events,
                               periods=[p.audit() for p in model.periods], overrides=model.override_records))
    record = FIXTURE['recorded_run']
    recorded = RecordedV3Model(record['n_agents'], seed=record['seed'], rules=rules,
                              successor_capability=record['successor_capability'], **kwargs)
    diagnostics = recorded.run(record['steps'])
    artifacts = {
        'paired_states': states,
        'evaluation_prefixes_with_transitions': prefixes,
        'recorded_run': {'diagnostics': diagnostics, 'yield_events': recorded.yield_events,
                         'periods': [p.audit() for p in recorded.periods],
                         'overrides': recorded.override_records, 'terminal': state_snapshot(recorded.state)},
    }
    return {name: scientific_bytes(value) for name, value in artifacts.items()}


def test_declared_r4_matches_frozen_scientific_artifact_hashes():
    expected = json.loads((Path(__file__).parent / 'v3/r4_identity_expected.json').read_text(encoding='utf-8'))
    assert expected['schema'] == 'v3-R4-scientific-identity-1'
    assert expected['baseline_commit'] == 'fe98280cac473d7b4e4febed4071bda10e2bae37'
    assert expected['fixture'] == FIXTURE
    actual = scientific_artifacts(instrument=FIXTURE['instrument'])
    assert set(actual) == set(expected['artifacts'])
    for name, data in actual.items():
        assert {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)} == expected['artifacts'][name], name
