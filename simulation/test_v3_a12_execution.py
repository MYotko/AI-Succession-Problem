"""Proposed A12 scheduling changes, with no registered machine access."""
import inspect
import hashlib
import time
from copy import deepcopy
import pytest
from test_v3_paths import tmp_path
from test_v3_multihost_a11 import (SETTINGS, FINGERPRINT, initialize, spec_fixture,
                                  join, ready, claim, finish, evidence)
from v3 import artifacts as a, multihost_a11 as m, host_a11 as h
from v3 import production_runner as runner, service


def completed_phase(tmp_path, original):
    now = time.time()
    _, root, spec = initialize(tmp_path, hosts=('alpha', 'beta', 'gamma'), start=now)
    identities = {host: join(root, host, now) for host in ('alpha', 'beta', 'gamma')}
    for identity in identities.values():
        ready(root, identity, 'toy', now)
    sample = m.read_state(root)['sample_jobs']['toy']
    others = iter(['alpha', 'beta', 'gamma'] * len(spec['jobs']))
    for job in reversed(spec['jobs']):
        owner = original if job['id'] == sample else next(others)
        leased = claim(root, identities[owner], now)
        assert leased['job'] == job
        finish(root, identities[owner], leased, now)
    with m.transaction(root):
        c = m.Coordinator(root, now)
        assert c.phase_hosts('toy') == set(identities)
    return root, spec, identities, sample, now


@pytest.mark.parametrize('original,preferred,other', [('gamma', 'alpha', 'beta'), ('alpha', 'beta', 'gamma')])
def test_fastest_eligible_non_original_host_gets_unchanged_check(tmp_path, original, preferred, other):
    root, spec, ids, sample, now = completed_phase(tmp_path, original)
    assert claim(root, ids[original], now)['job'] is None
    wait = claim(root, ids[other], now)
    assert wait['job'] is None and preferred in wait['waiting']
    check = claim(root, ids[preferred], now)
    assert check['job'] == next(j for j in spec['jobs'] if j['id'] == sample)
    assert check['purpose'] == 'check'
    finish(root, ids[preferred], check, now)
    record = a.read(root / 'toy/nondeterminism_check.json')
    assert record['matched'] and record['original_host'] == original and record['recheck_host'] == preferred
    assert m.read_state(root)['complete']


def test_recheck_preference_expires_without_reset_and_fallback_finishes(tmp_path):
    root, spec, ids, sample, now = completed_phase(tmp_path, 'gamma')
    assert claim(root, ids['beta'], now)['job'] is None
    window = deepcopy(m.read_state(root)['recheck_preferences']['toy'])
    assert window['expires_epoch'] == now + m.RECHECK_PREFERENCE_SECONDS
    assert claim(root, ids['beta'], now + 4.)['job'] is None
    assert m.read_state(root)['recheck_preferences']['toy'] == window
    leased = claim(root, ids['beta'], window['expires_epoch'])
    assert leased['job']['id'] == sample and leased['purpose'] == 'check'
    finish(root, ids['beta'], leased, window['expires_epoch'])
    assert a.read(root / 'toy/nondeterminism_check.json')['matched']


@pytest.mark.parametrize('exclusion', ['draining', 'memory', 'configuration', 'inputs'])
def test_ineligible_fast_host_cannot_hold_recheck_preference(tmp_path, exclusion):
    root, spec, ids, sample, now = completed_phase(tmp_path, 'gamma')
    with m.transaction(root):
        c = m.Coordinator(root, now)
        s = c.state['sessions'][ids['alpha']['session']]
        if exclusion == 'draining':
            s['control']['drain'] = True
        elif exclusion == 'memory':
            s['memory_available_gb'] = .01
        elif exclusion == 'configuration':
            s['chosen'].clear()
        else:
            s['ready'].clear()
        c.save()
    leased = claim(root, ids['beta'], now)
    assert leased['purpose'] == 'check' and leased['job']['id'] == sample
    finish(root, ids['beta'], leased, now)
    assert m.read_state(root)['complete']


def test_preference_cannot_change_mismatch_halt(tmp_path):
    root, _, ids, _, now = completed_phase(tmp_path, 'gamma')
    check = claim(root, ids['alpha'], now)
    assert finish(root, ids['alpha'], check, now, different=True)['halt'] == 'nondeterminism'
    assert a.unseal(a.read(root / 'nondeterminism_failure.json'))['original_host'] == 'gamma'


def test_ready_and_heartbeat_supply_current_memory_for_preference(tmp_path):
    root, _, ids, _, now = completed_phase(tmp_path, 'gamma')
    with m.transaction(root):
        c = m.Coordinator(root, now)
        c.state['sessions'][ids['alpha']['session']]['memory_available_gb'] = 0.
        c.save()
    m.rpc(root, dict(ids['alpha'], op='heartbeat', memory_available_gb=40.), now=now)
    assert claim(root, ids['beta'], now)['job'] is None
    check = claim(root, ids['alpha'], now)
    assert check['purpose'] == 'check'
    finish(root, ids['alpha'], check, now)


SECOND = 'second-x2'
X2_NONE = dict(profile='x2', workers=8, threads=1, cpu_budget=32, mode='normal', model_service='none')


def test_second_x2_joins_configures_and_runs_without_llm(tmp_path, monkeypatch):
    spec = spec_fixture(10)
    cfg = dict(phase='toy', steps=2, model=dict(n_agents=8, carrying_capacity=80, instrument=spec['instrument']))
    spec['jobs'] = [a.stable_job('rerun', cfg, 'validation', i) for i in range(10)]
    spec['pull_dispatch']['job_classes'] = {j['id']: str(i) for i, j in enumerate(spec['jobs'])}
    spec['configuration']['toy'].update(kind='rerun', config=cfg)
    # Keep this real-process service/transport fixture at eight trial jobs.
    # The CPU-cap candidate tests independently cover 31 with small trial RSS.
    spec['configuration']['toy'].pop('jobs_per_worker')
    spec['configuration']['toy']['jobs_x2'] = 8
    _, root, spec = initialize(tmp_path, spec, hosts=(SECOND,), host_settings={SECOND: X2_NONE})
    monkeypatch.setattr(h.platform, 'node', lambda: SECOND)
    monkeypatch.setattr(h.platform, 'system', lambda: 'Linux')
    monkeypatch.setattr(runner, 'available_cpus', lambda: 32)
    from v3 import worker_safety
    monkeypatch.setattr(worker_safety, 'swap_status', lambda: dict(total_bytes=32*1024**3, free_bytes=32*1024**3))
    # The actual toy worker pool is eight, within the workstation's 12 cap.
    monkeypatch.setattr(runner, 'mem_available_bytes', lambda: 10_000_000_000)
    monkeypatch.setattr(service, 'command', lambda *args: pytest.fail('no llm command is permitted'))
    settings = dict(X2_NONE, caps=runner.caps('x2', 32))
    runner.validate_spec(spec, settings)
    scratch = tmp_path / 'second_host'; scratch.mkdir()
    with h.host_service(scratch, 'x2', 'none') as record:
        result = h.run_host(h.Loopback(root), scratch, settings, host=SECOND, environment=FINGERPRINT,
                            service=record, max_seconds=60)
    assert result['stopped'] and m.read_state(root)['complete']
    approved = m.register_entries(root)[SECOND]
    assert approved['profile'] == 'x2' and approved['model_service'] == 'none'
    session = next(iter(m.read_state(root)['sessions'].values()))
    assert session['chosen']['toy']['workers'] == 8
    assert {x['workers'] for x in session['configuration']['toy']} == {8}
    assert spec['configuration']['toy']['workers_x2'] == [8, 12, 16, 24, 32]
    assert session['settings']['model_service'] == session['service']['model_service'] == 'none'
    record = a.read(scratch / 'service.json')
    assert record['actions_skipped'] and record['finished_epoch'] >= record['started_epoch']
    assert record['down_exit_code'] is record['up_exit_code'] is None
    assert all(runner.completed(root / 'toy', j, a.code_identity()) for j in spec['jobs'])


@pytest.mark.parametrize('change', [dict(profile='local'), dict(model_service='llm')])
def test_join_refuses_profile_or_service_not_approved(tmp_path, change):
    _, root, _ = initialize(tmp_path, hosts=(SECOND,), host_settings={SECOND: X2_NONE})
    with pytest.raises(ValueError, match='approved register entry'):
        m.rpc(root, dict(op='join', host=SECOND, code_hash=a.code_identity(), code_commit='fixture',
                        fingerprint=FINGERPRINT, settings=dict(X2_NONE, **change),
                        service=dict(model_service='none', actions_skipped=True)))


def test_approval_requires_explicit_qualification_profile_not_hostname(tmp_path):
    _, root, spec = initialize(tmp_path, hosts=())
    doc = a.unseal(evidence('yotko-evo-x2', a.code_identity()))
    del doc['candidate']['settings']
    from v3.qualification_a11 import compare
    doc = compare(doc['plan'], a.seal(doc['reference']), a.seal(doc['candidate']))
    with pytest.raises(ValueError, match='declare the candidate profile'):
        m.approve_host(root, doc, 'operator', '2026-10-10')


@pytest.mark.parametrize('host', ['yotko-evo-x2', SECOND])
@pytest.mark.parametrize('fail_down', [False, True])
def test_x2_default_service_still_stands_down_and_restores(tmp_path, monkeypatch, host, fail_down):
    monkeypatch.setattr(h.platform, 'node', lambda: host)
    monkeypatch.setattr(h.platform, 'system', lambda: 'Linux')
    calls = []
    def command(root, action):
        calls.append(action)
        return int(fail_down and action == 'down')
    monkeypatch.setattr(service, 'command', command)
    if fail_down:
        with pytest.raises(RuntimeError, match='llm down failed'):
            with h.host_service(tmp_path, 'x2'):
                pytest.fail('work may not start')
    else:
        with h.host_service(tmp_path, 'x2') as record:
            assert record['down_exit_code'] == 0 and record['model_service'] == 'llm'
    assert calls == ['down', 'up']
    assert a.read(tmp_path / 'service.json')['up_exit_code'] == 0


def test_single_machine_x2_none_service_wrapper_attempts_no_command(tmp_path, monkeypatch):
    monkeypatch.setattr(service.platform, 'node', lambda: SECOND)
    monkeypatch.setattr(service.platform, 'system', lambda: 'Linux')
    monkeypatch.setattr(service, 'command', lambda *args: pytest.fail('no service command'))
    monkeypatch.setattr(runner, 'validate_spec', lambda *args: None)
    seen = []
    def launch(*args, **kwargs):
        service.require_service_record(X2_NONE, kwargs['service_record'])
        seen.append(kwargs['service_record'])
        return dict(complete=True)
    monkeypatch.setattr(runner, 'launch', launch)
    path = tmp_path / 'spec.json'; a.atomic_json(path, a.seal(dict(wall_seconds=500)))
    assert service.run_with_service(path, tmp_path / 'root', X2_NONE)['complete']
    assert seen and a.read(tmp_path / 'root/service.json')['model_service'] == 'none'


def test_none_service_needs_explicit_record():
    for bad in (None, {}, dict(down_exit_code=0), dict(model_service='llm', actions_skipped=True)):
        with pytest.raises(RuntimeError, match='no-service supervisor record'):
            service.require_service_record(X2_NONE, bad)


def test_r4_configuration_builders_are_unchanged():
    # Frozen source hashes from c19b54f5. Only A10 preparation overrides the
    # returned candidates; neither legacy profile builder is edited.
    from v3 import table_validation_a4 as a4, table_labels_a5 as a5
    expected = {
        a4._configuration_profiles: 'b3d258077fb1bc159da870c606e6f6d2595ca9f55abe64155cbac99849025262',
        a5._configuration_profile: '4da0a6da2920bf77258851236f76257f20bc8f2e40757cb37e800f4630d7603b',
    }
    for function, sha in expected.items():
        assert hashlib.sha256(inspect.getsource(function).encode()).hexdigest() == sha
