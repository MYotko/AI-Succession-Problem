"""Regressions reported by the real X2/WSL A11 rehearsal."""
from concurrent.futures import ThreadPoolExecutor
import json
import sqlite3
import sys
import time
import pytest
from test_v3_paths import tmp_path
from test_v3_multihost_a11 import (SETTINGS, FINGERPRINT, initialize, spec_fixture,
                                  join, ready, claim, finish)
from v3 import artifacts as a, multihost_a11 as m, production_runner as runner


X2 = 'yotko-evo-x2'
X2_SETTINGS = dict(profile='x2', workers=8, threads=1, cpu_budget=32, mode='normal')


def join_x2(root, **overrides):
    return m.rpc(root, dict(op='join', host=X2, fingerprint=FINGERPRINT,
        code_hash=a.code_identity(), code_commit='fixture', settings=dict(X2_SETTINGS, **overrides),
        service=dict(down_exit_code=0)))


def journal_states(root):
    with sqlite3.connect(root / 'dispatch.sqlite') as db:
        return [change['value'] for raw, in db.execute('SELECT data FROM journal ORDER BY seq')
                for change in json.loads(raw)['changes'] if change['bucket'] == 'state']


def test_departed_x2_cap_can_be_repaired_before_rejoin(tmp_path):
    _, root, _ = initialize(tmp_path, hosts=(X2,))
    first = join_x2(root)
    m.rpc(root, dict(op='leave', host=X2, session=first['session']))
    # Durable state left by the old implementation after its failed four-worker
    # configuration. No process or configuration result is fabricated here.
    with m.transaction(root):
        c = m.Coordinator(root)
        c.state['host_controls'][X2]['max_workers'] = 4
        c.save()
    with pytest.raises(ValueError, match='--max-workers 8 before rejoining'):
        join_x2(root)
    assert len(m.read_state(root)['sessions']) == 1
    m.control(root, X2, max_workers=8)
    assert journal_states(root)[-1]['host_controls'][X2]['max_workers'] == 8
    second = join_x2(root)
    identity = dict(host=X2, session=second['session'])
    snapshot = m.rpc(root, dict(identity, op='inputs', phase='toy', configuration=True))
    chosen = m.rpc(root, dict(identity, op='configure', phase='toy', input_sha256=snapshot['sha256'],
        measurements=[dict(workers=8, threads=1, completed=8, wall_seconds=1., valid=True,
                           round=0, job_seconds=[.1] * 8)]))
    assert chosen['workers'] == 8
    assert m.read_state(root)['sessions'][second['session']]['control']['max_workers'] == 8


def test_approved_never_joined_host_controls_persist_through_restart_and_join(tmp_path):
    _, root, _ = initialize(tmp_path, hosts=(X2,))
    m.control(root, X2, mode='work', max_workers=8, stop='drain')
    assert not m.read_state(root)['sessions']
    with m.transaction(root):
        c = m.Coordinator(root); c.start(); c.save()
    joined = join_x2(root, workers=12)
    state = m.read_state(root)
    assert state['sessions'][joined['session']]['control'] == dict(mode='work', max_workers=8, drain=True, interrupt_now=False)
    assert not m.rpc(root, dict(op='claim', host=X2, session=joined['session'], memory_available_gb=40))['job']
    m.rpc(root, dict(op='leave', host=X2, session=joined['session']))
    m.control(root, X2, stop='clear')
    later = join_x2(root)
    assert not m.read_state(root)['sessions'][later['session']]['control']['drain']
    assert journal_states(root)[-1]['host_controls'][X2]['max_workers'] == 8


@pytest.mark.parametrize('operation', ['join', 'control'])
@pytest.mark.parametrize('cap', [0, 1, 4])
def test_x2_refuses_cap_below_required_candidate_with_recovery_command(tmp_path, operation, cap):
    _, root, _ = initialize(tmp_path, hosts=(X2,))
    with pytest.raises(ValueError, match='requires a worker cap of at least 8.*--max-workers 8.*--workers 8'):
        join_x2(root, workers=cap) if operation == 'join' else m.control(root, X2, max_workers=cap)
    state = m.read_state(root)
    assert not state['sessions'] and not state.get('host_controls')


def test_control_rejects_unapproved_host_and_checks_each_profile_minimum(tmp_path):
    spec = spec_fixture(); spec['configuration']['toy']['workers_local'] = [4, 8, 12]
    _, root, _ = initialize(tmp_path, spec)
    with pytest.raises(ValueError, match='unregistered host'):
        m.control(root, 'unknown', max_workers=8)
    with pytest.raises(ValueError, match='at least 4'):
        m.control(root, 'alpha', max_workers=2)
    with pytest.raises(ValueError, match='at least 4'):
        join(root, 'alpha')
    m.control(root, 'alpha', max_workers=4)
    assert m.read_state(root)['host_controls']['alpha']['max_workers'] == 4


@pytest.mark.parametrize('stop', ['drain', 'now'])
def test_operator_stop_is_journaled_and_recorded_on_coordinator_exit(tmp_path, stop):
    path, root, _ = initialize(tmp_path)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(m.coordinate, path, root, SETTINGS)
        for _ in range(200):
            if (root / 'launches.json').exists():
                break
            time.sleep(.02)
        alpha = join(root, 'alpha'); ready(root, alpha, 'toy')
        leased = claim(root, alpha)
        m.control(root, stop=stop)
        recorded = a.read(root / 'launches.json')[-1]
        operator_stop = m.read_state(root)['operator_stop']
        assert recorded['stopped'] == operator_stop['reason'] == 'operator_stop_' + stop
        assert recorded['stopped_epoch'] == operator_stop['epoch']
        assert any(s.get('operator_stop') == operator_stop for s in journal_states(root))
        assert not future.done()  # Drain retains active work; now awaits its release.
        heartbeat = m.rpc(root, dict(alpha, op='heartbeat'))
        assert heartbeat['status']['reason'] == 'operator_stop_' + stop
        assert heartbeat['status']['hard_stop'] == (stop == 'now')
        assert claim(root, alpha)['job'] is None
        if stop == 'drain':
            finish(root, alpha, leased)
        else:
            m.rpc(root, dict(alpha, op='release', lease=leased['lease'], reason='operator interruption'))
        m.rpc(root, dict(alpha, op='leave'))
        result = future.result(timeout=10)
    final = a.read(root / 'launches.json')[-1]
    assert not result['complete'] and not final['complete']
    assert final['stopped'] == final['reason'] == 'operator_stop_' + stop
    assert final['stopped_epoch'] == operator_stop['epoch'] <= final['finished_epoch']
    m.control(root, stop='clear')
    assert m.read_state(root)['operator_stop'] is None
    # Clearing dispatch for a future attempt must not erase the finished
    # attempt's stop reason from the watchdog's durable history.
    assert a.read(root / 'launches.json')[-1]['stopped'] == 'operator_stop_' + stop


def test_cross_host_recheck_wait_is_visible_stable_and_clears_on_rejoin(tmp_path, monkeypatch, capsys):
    _, root, spec = initialize(tmp_path)
    alpha, beta = join(root, 'alpha'), join(root, 'beta')
    ready(root, alpha, 'toy'); ready(root, beta, 'toy')
    sample = m.read_state(root)['sample_jobs']['toy']
    beta_used = False
    # Fixture costs descend by index. Ensure the sampled original is alpha,
    # with another host genuinely participating before it drains.
    for job in reversed(spec['jobs']):
        identity = beta if job['id'] != sample and not beta_used else alpha
        leased = claim(root, identity)
        assert leased['job'] == job
        finish(root, identity, leased)
        beta_used |= identity == beta
    m.control(root, 'beta', stop='drain')
    m.rpc(root, dict(beta, op='leave'))
    waiting = a.read(root / 'status.json')['waiting_for']
    assert waiting['phase'] == 'toy' and waiting['reason'].startswith('cross_host_recheck: needs a host other than alpha')
    assert a.read(root / 'toy/status.json')['waiting_for'] == waiting
    assert claim(root, alpha)['job'] is None
    assert m.rpc(root, dict(alpha, op='heartbeat'))['status']['waiting_for'] == waiting
    monkeypatch.setattr(sys, 'argv', ['production_runner', 'status', str(root)])
    runner.main()
    assert waiting['reason'] in capsys.readouterr().out
    beta = join(root, 'beta'); ready(root, beta, 'toy')
    assert m.rpc(root, {'op': 'inspect'})['status']['waiting_for'] == waiting  # Drain persisted.
    m.control(root, 'beta', stop='clear')
    assert a.read(root / 'status.json')['waiting_for'] is None
    assert a.read(root / 'toy/status.json')['waiting_for'] is None
    check = claim(root, beta)
    assert check['purpose'] == 'check' and check['job']['id'] == sample
    finish(root, beta, check)
    status = m.rpc(root, {'op': 'inspect'})['status']
    assert status['complete'] and status['waiting_for'] is None
    assert a.read(root / 'toy/nondeterminism_check.json')['recheck_host'] == 'beta'


def test_no_host_configuration_and_input_waits_appear_and_clear(tmp_path):
    _, root, _ = initialize(tmp_path)
    assert a.read(root / 'status.json')['waiting_for']['reason'].startswith('no_eligible_host:')
    alpha = join(root, 'alpha', configure=False)
    first = a.read(root / 'status.json')['waiting_for']
    assert first['reason'].startswith('configuration_not_ready:')
    assert a.read(root / 'toy/status.json')['waiting_for'] == first
    snapshot = m.rpc(root, dict(alpha, op='inputs', phase='toy', configuration=True))
    m.rpc(root, dict(alpha, op='configure', phase='toy', input_sha256=snapshot['sha256'], measurements=[
        dict(workers=2, threads=1, completed=2, wall_seconds=1., valid=True, round=0, job_seconds=[.5, .5])]))
    second = a.read(root / 'status.json')['waiting_for']
    assert second['reason'].startswith('inputs_not_ready:') and second['since_epoch'] >= first['since_epoch']
    ready(root, alpha, 'toy')
    assert a.read(root / 'status.json')['waiting_for'] is None
    assert a.read(root / 'toy/status.json')['waiting_for'] is None


def test_memory_wait_is_diagnostic_and_never_relaxes_the_claim(tmp_path):
    spec = spec_fixture(1)
    spec['pull_dispatch']['cost_classes']['0']['memory_gb'] = 15
    _, root, _ = initialize(tmp_path, spec)
    alpha = join(root, 'alpha'); ready(root, alpha, 'toy')
    assert claim(root, alpha, memory=2)['job'] is None
    wait = a.read(root / 'status.json')['waiting_for']
    assert 'memory' in wait['reason']
    assert not m.read_state(root)['leases']
    assert claim(root, alpha, memory=40)['job'] == spec['jobs'][0]
    assert a.read(root / 'status.json')['waiting_for'] is None
