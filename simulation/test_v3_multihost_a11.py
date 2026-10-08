"""A11 pull transactions, independent loopback hosts and failure recovery."""
import base64
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import hashlib
import multiprocessing as mp
from pathlib import Path
import threading
import time
import pytest
from test_v3_paths import tmp_path
from v3 import artifacts as a, multihost_a11 as m, qualification_a11 as q, host_a11 as h
from v3 import production_runner as runner, tables_a10 as tables

SETTINGS = dict(profile='local', workers=2, threads=1, cpu_budget=16, mode='work')
FINGERPRINT = dict(python='fixture', numpy='fixture', numpy_cpu_baseline=['SSE'], numpy_cpu_dispatch=['AVX'],
    numpy_cpu_features={'AVX': True}, conda_packages_sha256='c' * 64, threads_configured=1,
    threads_verified=[dict(library='fixture', effective=1)])


def evidence(host, code, kinds=('fixture',), speed=1., memory=40.):
    jobs = [a.stable_job(kind, {'phase': 'fixture'}, 'validation', i) for kind in kinds for i in range(20)]
    plan = a.seal(dict(schema=q.SCHEMA + '-plan', non_registered=True, jobs=jobs, kinds=list(kinds), code_hash=code))
    proofs = [dict(job_id=j['id'], kind=j['kind'], job_sha256=a.digest(j), canonical_sha256=a.digest([j, 'result'])) for j in jobs]
    ref = dict(schema=q.SCHEMA + '-run', non_registered=True, host='yotko-evo-x2', code_hash=code, plan_sha256=plan['sha256'], proofs=proofs, passed=True,
               elapsed_seconds=20., memory_gb=memory, fingerprint=FINGERPRINT, kinds=list(kinds))
    candidate = dict(ref, host=host, elapsed_seconds=20. / speed)
    return q.compare(plan, a.seal(ref), a.seal(candidate))


def spec_fixture(count=8, phases=('toy',), *, seconds=.01):
    jobs = [a.stable_job('fixture', {'phase': p, 'seconds': seconds}, 'validation', i) for p in phases for i in range(count)]
    profiles = {p: dict(kind='fixture', config={'phase': p, 'seconds': .005}, workers_local=[2],
        workers_x2=[8, 12, 16, 24, 32], threads=[1], rounds=1, jobs_per_worker=1) for p in phases}
    classes = {str(i): dict(worker_seconds=i + 1., memory_gb=1.) for i in range(len(jobs))}
    return dict(schema='v3-validation-1', registered=False, instrument=tables.NOMINAL.declaration(),
        code_hash=a.code_identity(), tag='validation', jobs=jobs, phases=list(phases), configuration=profiles,
        wall_seconds=300, x2_equivalent_hours=1, cleanup_reserve_seconds=0, configuration_seconds=60,
        publication=None, pull_dispatch=dict(schema=m.SCHEMA, code_commit='fixture', lease_seconds=30.,
        extra_inputs=[], job_classes={j['id']: str(i) for i, j in enumerate(jobs)}, cost_classes=classes))


def initialize(tmp_path, spec=None, hosts=('alpha', 'beta'), start=None):
    spec = spec or spec_fixture()
    path, root = tmp_path / 'spec.json', tmp_path / 'coordinator'
    a.atomic_json(path, a.seal(spec))
    m.prepare(path, root, SETTINGS)
    for index, host in enumerate(hosts):
        m.approve_host(root, evidence(host, spec['code_hash'], tuple(sorted({j['kind'] for j in spec['jobs']})),
                                     speed=1. / (index + 1)), 'operator', '2026-10-08T12:00:00Z')
    with m.transaction(root):
        c = m.Coordinator(root, start)
        c.start(); c.save()
    return path, root, spec


def join(root, host, now=None, configure=True):
    spec = a.unseal(a.read(root / 'manifest.json'))
    result = m.rpc(root, dict(op='join', host=host, code_hash=a.code_identity(), code_commit='fixture',
                              fingerprint=FINGERPRINT, settings=SETTINGS), now=now)
    identity = dict(host=host, session=result['session'])
    if configure:
        for phase in spec['phases']:
            snapshot = m.rpc(root, dict(op='inputs', phase=phase, configuration=True, **identity), now=now)
            m.rpc(root, dict(op='configure', phase=phase, input_sha256=snapshot['sha256'], measurements=[
                dict(workers=2, threads=1, completed=2, wall_seconds=1., valid=True, round=0, job_seconds=[.5, .5])], **identity), now=now)
    return identity


def ready(root, identity, phase, now=None):
    snapshot = m.rpc(root, dict(op='inputs', phase=phase, **identity), now=now)
    m.rpc(root, dict(op='ready', phase=phase, input_sha256=snapshot['sha256'], **identity), now=now)


def claim(root, identity, now=None, memory=40):
    return m.rpc(root, dict(op='claim', memory_available_gb=memory, **identity), now=now)


def finish(root, identity, leased, now=None, different=False):
    job = leased['job']
    raw = a.canonical(dict(job=job, code_hash=a.code_identity(), host=identity['host'], lease=leased['lease'],
        seconds=.1, result=dict(seed=job['seed'] + int(different), fixture=True)))
    return m.rpc(root, dict(op='complete', data=base64.b64encode(raw).decode(), sha256=hashlib.sha256(raw).hexdigest(),
                            lease=leased['lease'], **identity), now=now)


@pytest.mark.parametrize('hosts', [('alpha', 'beta'), ('alpha', 'beta', 'gamma')])
def test_hosts_join_mid_phase_drain_leave_and_cross_host_check(tmp_path, hosts):
    _, root, spec = initialize(tmp_path, hosts=hosts)
    ids = [join(root, hosts[0])]
    ready(root, ids[0], 'toy')
    first = claim(root, ids[0]); finish(root, ids[0], first)
    for host in hosts[1:]:
        ids.append(join(root, host)); ready(root, ids[-1], 'toy')
    for identity in ids:
        leased = claim(root, identity)
        finish(root, identity, leased)
    m.control(root, hosts[0], stop='drain')
    assert claim(root, ids[0])['job'] is None
    m.rpc(root, dict(op='leave', **ids[0]))
    for _ in range(30):
        if m.rpc(root, {'op': 'inspect'})['status']['complete']:
            break
        for identity in ids[1:]:
            leased = claim(root, identity)
            if leased.get('job'):
                finish(root, identity, leased)
    status = m.rpc(root, {'op': 'inspect'})['status']
    # If the selected job was originally on the sole remaining host, rejoin
    # alpha for the mandatory other-host check; draining does not waive it.
    if not status['complete']:
        identity = join(root, hosts[0]); ready(root, identity, 'toy')
        m.control(root, hosts[0], stop='clear')
        leased = claim(root, identity); assert leased['purpose'] == 'check'
        finish(root, identity, leased)
    check = a.read(root / 'toy/nondeterminism_check.json')
    assert check['original_host'] != check['recheck_host']
    status = m.rpc(root, {'op': 'inspect'})['status']
    assert status['complete'] and status['completed'] == len(spec['jobs'])
    assert set(status['hosts']) == set(hosts)
    assert all(runner.completed(root / 'toy', j, spec['code_hash']) for j in spec['jobs'])


def test_expired_killed_host_restarts_exact_job_and_late_identical_duplicate(tmp_path):
    t = time.time()
    _, root, spec = initialize(tmp_path, start=t)
    alpha, beta = join(root, 'alpha', t), join(root, 'beta', t)
    for i in (alpha, beta): ready(root, i, 'toy', t)
    old = claim(root, alpha, t)
    m.rpc(root, dict(op='heartbeat', **beta), now=t + 20)
    fresh = claim(root, beta, t + 31)
    assert old['job'] == fresh['job'] and old['lease'] != fresh['lease']
    finish(root, beta, fresh, t + 31)
    assert finish(root, alpha, old, t + 32)['duplicate']
    assert len(list((root / 'toy/records').glob('*.json'))) == 1
    assert len(list((root / 'incidental_cross_checks').glob('*.json'))) == 1
    assert m.read_state(root)['sessions'][alpha['session']]['end'] == t + 30


def test_differing_late_duplicate_latches_durable_halt_across_resume(tmp_path):
    _, root, _ = initialize(tmp_path)
    alpha = join(root, 'alpha'); ready(root, alpha, 'toy')
    leased = claim(root, alpha); finish(root, alpha, leased)
    assert finish(root, alpha, leased, different=True)['halt'] == 'nondeterminism'
    assert a.unseal(a.read(root / 'nondeterminism_failure.json'))['original_host'] == 'alpha'
    with m.transaction(root):
        c = m.Coordinator(root); c.start(); c.save()
    assert m.rpc(root, {'op': 'inspect'})['status']['halt'] == 'nondeterminism'
    with pytest.raises(ValueError, match='accepting joins'):
        join(root, 'beta')


def test_coordinator_crash_resume_voids_leases_accepts_late_output_and_rebuilds(tmp_path):
    _, root, spec = initialize(tmp_path)
    alpha = join(root, 'alpha'); ready(root, alpha, 'toy')
    first = claim(root, alpha); finish(root, alpha, first)
    late = claim(root, alpha)
    with m.transaction(root):
        c = m.Coordinator(root); c.state['completions'].clear(); c.save()  # cache lost, records survive
        c = m.Coordinator(root); c.start(); c.save()
    assert m.rpc(root, {'op': 'inspect'})['status']['completed'] == 1
    assert m.read_state(root)['leases'][late['lease']]['status'] == 'void_on_resume'
    assert finish(root, alpha, late)['accepted']
    beta = join(root, 'beta'); ready(root, beta, 'toy')
    assert claim(root, beta)['job']['id'] not in {first['job']['id'], late['job']['id']}
    bad = a.read(root / 'identity.json'); bad['code_hash'] = 'f' * 64
    a.atomic_json(root / 'identity.json', bad)
    with pytest.raises(RuntimeError, match='incompatible resumption'):
        m.rpc(root, {'op': 'inspect'})


@pytest.mark.parametrize('defect', ['unregistered', 'fingerprint', 'code', 'commit'])
def test_join_refusals(tmp_path, defect):
    _, root, _ = initialize(tmp_path)
    request = dict(op='join', host='alpha', fingerprint=FINGERPRINT, code_hash=a.code_identity(), code_commit='fixture', settings=SETTINGS)
    if defect == 'unregistered': request['host'] = 'stranger'
    if defect == 'fingerprint': request['fingerprint'] = {}
    if defect == 'code': request['code_hash'] = 'f' * 64
    if defect == 'commit': request['code_commit'] = 'different'
    with pytest.raises(ValueError): m.rpc(root, request)


def test_memory_order_caps_budget_and_unchanged_jobs(tmp_path):
    spec = spec_fixture()
    spec['pull_dispatch']['cost_classes']['7']['memory_gb'] = 15.
    t = time.time()
    _, root, spec = initialize(tmp_path, spec, start=t)
    identity = join(root, 'alpha', t); ready(root, identity, 'toy', t)
    first = claim(root, identity, t, memory=10)
    assert first['job'] == spec['jobs'][6]  # the 15 GB job is never offered
    second = claim(root, identity, t)
    assert second['job'] == spec['jobs'][7]
    assert claim(root, identity, t)['job'] is None  # two-worker cap
    finish(root, identity, first, t); finish(root, identity, second, t)
    for when in range(20, 3600, 20):
        m.rpc(root, dict(op='heartbeat', **identity), now=t + when)
    m.rpc(root, dict(op='heartbeat', **identity), now=t + 3600)
    assert claim(root, identity, t + 3600)['job'] is None
    status = m.rpc(root, {'op': 'inspect'}, now=t + 3600)['status']
    assert status['stops']['x2'] and status['x2_equivalent_hours'] == 1.
    assert a.unseal(a.read(root / 'manifest.json'))['jobs'] == spec['jobs']


def test_corrupt_transfer_and_partial_output_are_never_completed(tmp_path):
    _, root, spec = initialize(tmp_path)
    identity = join(root, 'alpha'); ready(root, identity, 'toy')
    leased = claim(root, identity)
    with pytest.raises(ValueError, match='corrupt output'):
        m.rpc(root, dict(op='complete', lease=leased['lease'], data=base64.b64encode(b'{}').decode(), sha256='0' * 64, **identity))
    assert not list(root.glob('*/records/*.json'))
    # A crash with an output alone cannot turn it into a completed row.
    a.atomic_json(root / 'toy/outputs' / (leased['job']['id'] + '.json'), {})
    assert runner.completed(root / 'toy', leased['job'], spec['code_hash']) is None


def test_network_drop_stops_client_and_configuration_control_without_records(tmp_path):
    _, root, _ = initialize(tmp_path)
    identity = join(root, 'alpha')
    transport = h.Loopback(root); transport.connected = False
    client = h.Client(transport, identity['host'], identity['session'], .08)
    client.last_contact -= 1
    thread = threading.Thread(target=client.watch, args=(tmp_path / 'host_alpha',))
    thread.start(); thread.join(2)
    assert client.lost.is_set() and not thread.is_alive()
    assert a.read(tmp_path / 'host_alpha/control.json')['interrupt_now']
    assert not list(root.glob('*/records/*.json'))


class DropAfterClaim(h.Loopback):
    def call(self, request):
        result = super().call(request)
        if request['op'] == 'claim' and (result.get('job') or result.get('claims')):
            self.claimed = result['claims'][0] if result.get('claims') else result
            self.connected = False
        return result


def test_network_drop_stops_real_host_processes_and_requeues_without_completion(tmp_path):
    spec = spec_fixture(2)
    cfg = dict(phase='toy', steps=0, model=dict(n_agents=8, carrying_capacity=80, instrument=tables.NOMINAL.declaration()))
    spec['jobs'] = [a.stable_job('rerun', cfg, 'validation', i) for i in range(2)]
    spec['pull_dispatch']['job_classes'] = {j['id']: str(i) for i, j in enumerate(spec['jobs'])}
    spec['pull_dispatch']['lease_seconds'] = 4.
    spec['configuration']['toy'].update(kind='rerun', config=cfg)
    _, root, spec = initialize(tmp_path, spec)
    transport = DropAfterClaim(root)
    scratch = tmp_path / 'disconnected_host'
    with pytest.raises(ConnectionError, match='contact'):
        h.run_host(transport, scratch, SETTINGS, host='alpha', environment=FINGERPRINT, max_seconds=30)
    assert a.read(scratch / 'host_exit.json')['contact_lost']
    assert not mp.active_children()
    assert not list(root.glob('*/records/*.json'))
    now = time.time() + 5
    beta = join(root, 'beta', now); ready(root, beta, 'toy', now)
    assert claim(root, beta, now)['job'] == transport.claimed['job']


def test_killed_worker_process_leaves_no_partial_record_and_lease_requeues(tmp_path):
    t = time.time()
    _, root, spec = initialize(tmp_path, spec_fixture(2, seconds=10), start=t)
    alpha, beta = join(root, 'alpha', t), join(root, 'beta', t)
    ready(root, alpha, 'toy', t); ready(root, beta, 'toy', t)
    old = claim(root, alpha, t)
    path = tmp_path / 'host_alpha/unpublished/killed.json'
    process = mp.get_context('spawn').Process(target=h.execute_scratch, args=(str(path), old['job'], spec['code_hash'],
        old['phase_root'], {'paths': {}, 'protected': []}, False, None, 'alpha', old['lease']))
    process.start()
    time.sleep(.7)
    assert process.is_alive()
    process.kill(); process.join(5)
    assert process.exitcode != 0 and not path.exists()
    assert not list(root.glob('*/records/*.json'))
    m.rpc(root, dict(op='heartbeat', **beta), now=t + 20)
    restarted = claim(root, beta, now=t + 31)
    assert restarted['job'] == old['job']
    assert finish(root, beta, restarted, now=t + 31)['accepted']


def test_killed_coordinator_process_resume_and_persisted_host_mode(tmp_path):
    path, root, spec = initialize(tmp_path)
    def launch_and_wait(generation):
        p = mp.get_context('spawn').Process(target=m.coordinate, args=(path, root, SETTINGS))
        p.start()
        for _ in range(100):
            state = m.read_state(root)
            if state['epoch'] >= generation:
                return p
            time.sleep(.05)
        p.kill(); p.join()
        pytest.fail('coordinator did not start')
    first = launch_and_wait(2)
    try:
        alpha = join(root, 'alpha'); ready(root, alpha, 'toy')
        leased = claim(root, alpha)
        m.control(root, 'alpha', mode='work', max_workers=2, stop='drain')
    finally:
        first.kill(); first.join(5)
    second = launch_and_wait(3)
    try:
        assert m.read_state(root)['leases'][leased['lease']]['status'] == 'void_on_resume'
        assert finish(root, alpha, leased)['accepted']
        alpha = join(root, 'alpha'); ready(root, alpha, 'toy')
        assert claim(root, alpha)['job'] is None
        m.control(root, 'alpha', stop='clear')
        assert claim(root, alpha)['job']['id'] != leased['job']['id']
    finally:
        second.kill(); second.join(5)


def test_input_transfer_hashes_paths_and_read_only_view(tmp_path):
    from v3.snapshot_a11 import inventory, receive, fetch
    source = tmp_path / 'coordinator_inputs/data.json'
    a.atomic_json(source, {'fixture': True})
    doc = inventory([], tmp_path / 'toy', [source])
    view = receive(doc, tmp_path / 'host/snapshots', lambda name, offset: fetch(doc, name, offset))
    target = Path(view['paths'][str(source.resolve())])
    assert target != source and target.read_bytes() == source.read_bytes()
    with a.input_view(view):
        assert a.read(source) == {'fixture': True}
        with pytest.raises(ValueError, match='not in the verified snapshot'):
            a.read(source.parent / 'undeclared.json')
    assert a.input_path(source) == source
    def corrupt(name, offset):
        block = fetch(doc, name, offset); block['data'] = base64.b64encode(b'corrupt').decode(); return block
    with pytest.raises(ValueError, match='corrupt'):
        receive(doc, tmp_path / 'bad_host/snapshots', corrupt)


def test_wall_ceiling_no_late_first_completion_and_bad_duplicate_after_completion_halts(tmp_path):
    t = time.time()
    spec = spec_fixture(1)
    _, root, spec = initialize(tmp_path, spec, start=t)
    alpha = join(root, 'alpha', t); ready(root, alpha, 'toy', t)
    leased = claim(root, alpha, t)
    reply = finish(root, alpha, leased, t + spec['wall_seconds'])
    assert reply == {'accepted': False, 'reason': 'wall ceiling'}
    assert runner.completed(root / 'toy', leased['job'], spec['code_hash']) is None


def test_resume_charges_late_work_without_overlapping_same_host_rejoin(tmp_path):
    t = time.time()
    _, root, _ = initialize(tmp_path, start=t)
    alpha = join(root, 'alpha', t); ready(root, alpha, 'toy', t)
    old = claim(root, alpha, t)
    with m.transaction(root):
        c = m.Coordinator(root, t + 10); c.start(); c.save()
    join(root, 'alpha', t + 12)
    finish(root, alpha, old, t + 15)
    state = m.read_state(root)
    assert state['sessions'][alpha['session']]['end'] == t + 12
    assert m.rpc(root, {'op': 'inspect'}, now=t + 15)['status']['x2_equivalent_hours'] == pytest.approx(15 / 3600)


def test_barrier_waits_for_active_duplicate_and_longest_class_ties_use_id(tmp_path):
    t = time.time(); spec = spec_fixture(3)
    for row in spec['pull_dispatch']['cost_classes'].values(): row['worker_seconds'] = 1.
    _, root, _ = initialize(tmp_path, spec, start=t)
    alpha, beta = join(root, 'alpha', t), join(root, 'beta', t)
    ready(root, alpha, 'toy', t); ready(root, beta, 'toy', t)
    first = claim(root, alpha, t)
    assert first['job']['id'] == min(j['id'] for j in spec['jobs'])
    m.rpc(root, dict(op='heartbeat', **beta), now=t + 20)
    duplicate = claim(root, beta, t + 31)
    finish(root, alpha, first, t + 31)
    with m.transaction(root):
        c = m.Coordinator(root, t + 31)
        # A completed nondeterminism check cannot erase another running lease.
        for j in spec['jobs']: c.done.setdefault(j['id'], {'host': 'alpha', 'phase': 'toy'})
        c.state['checks']['toy'] = {'matched': True}
        c.advance()
        assert c.phase == 'toy' and not c.state['complete']
    assert duplicate['job'] == first['job']


def test_a4_projection_sums_present_measured_host_rates(tmp_path):
    spec = spec_fixture(4, phases=('fit',))
    spec['schema'] = 'v3-A4-validation-1'
    base = dict(route='plain', a1_job={'config': {'settings': dict(runs_per_group=2, particles=2, burn=30, measure=8)}})
    spec['jobs'] = [a.stable_job('fixture', dict(j['config'], **base), j['tag'], j['index']) for j in spec['jobs']]
    spec['pull_dispatch']['job_classes'] = {j['id']: str(i) for i, j in enumerate(spec['jobs'])}
    spec['configuration']['fit']['config'].update(base)
    _, root, _ = initialize(tmp_path, spec)
    alpha, beta = join(root, 'alpha'), join(root, 'beta')
    with m.transaction(root):
        c = m.Coordinator(root)
        c.state['sessions'][beta['session']]['configuration']['fit'][0]['job_seconds'] = [1., 1.]
        assert c.projection()
        projection = next(iter(c.state['projections'].values()))
    rate_a = .5 / (32 * 2 * 32)
    rate_b = 1. / (32 * 2 * 32)
    expected = 4 * (32 * 2 * 38) / (2 / rate_a + 2 / rate_b) + (32 * 2 * 38) * rate_b
    assert projection['total_seconds'] == pytest.approx(expected)
    assert projection['phases']['fit']['hosts'] == ['alpha', 'beta']


def test_actual_loopback_worker_hosts_use_parallel_processes_and_separate_scratch(tmp_path):
    spec = spec_fixture(12)
    cfg = dict(phase='toy', steps=0, model=dict(n_agents=8, carrying_capacity=80, instrument=tables.NOMINAL.declaration()))
    spec['jobs'] = [a.stable_job('rerun', cfg, 'validation', i) for i in range(12)]
    spec['pull_dispatch']['job_classes'] = {j['id']: str(i) for i, j in enumerate(spec['jobs'])}
    spec['configuration']['toy'].update(kind='rerun', config=cfg)
    _, root, spec = initialize(tmp_path, spec)
    with ProcessPoolExecutor(max_workers=2, mp_context=mp.get_context('spawn')) as pool:
        futures = [pool.submit(h.run_host, h.Loopback(root), tmp_path / host, SETTINGS,
                   host=host, environment=FINGERPRINT, max_seconds=60) for host in ('alpha', 'beta')]
        results = [f.result() for f in futures]
    status = m.rpc(root, {'op': 'inspect'})['status']
    assert status['complete'] and set(status['hosts']) == {'alpha', 'beta'}
    assert all(r['stopped'] for r in results)
    assert not list((tmp_path / 'alpha/unpublished').glob('../records/*'))
    for host in ('alpha', 'beta'):
        assert list((tmp_path / host / 'unpublished').glob('*.json'))
    for job in spec['jobs']:
        record = a.read(root / 'toy/records' / (job['id'] + '.json'))
        assert record['host'] in ('alpha', 'beta') and record['lease']


@pytest.mark.parametrize('defect', ['failed', 'few', 'wrong_code', 'fingerprint', 'seal', 'coverage'])
def test_qualification_refusals(tmp_path, defect):
    code = a.code_identity(); doc = evidence('alpha', code)
    value = deepcopy(doc['payload'])
    if defect == 'failed': value['passed'] = False
    if defect == 'few': value['proofs'].pop()
    if defect == 'wrong_code': value['code_hash'] = 'f' * 64
    if defect == 'fingerprint': value['candidate']['fingerprint'] = {}
    if defect == 'coverage': value['kinds'].append('table')
    document = a.seal(value)
    if defect == 'seal': document['sha256'] = '0' * 64
    with pytest.raises(ValueError): q.validate_evidence(document, code)


def test_frozen_cost_classes_use_only_projection_and_job_declarations():
    jobs = tables.build_jobs('nominal', 'calibration', rule_ids=['balanced'], physical_contexts=[(.064, 1.)])
    spec = spec_fixture(); spec['jobs'] = jobs; spec['phases'] = ['table']
    del spec['pull_dispatch']
    costs = {key: dict(mean_worker_seconds=10 + i, memory_estimate_gb=2) for i, j in enumerate(jobs) for key in m.cost_keys(j)}
    result = m.freeze(spec, a.seal({'per_phase_capability': costs}), code_commit='fixture')
    assert result['jobs'] == spec['jobs'] and result['pull_dispatch']['projection_sha256']
    assert set(result['pull_dispatch']['job_classes']) == {j['id'] for j in jobs}
    for bad in (dict(result, instrument={'mapping': 'R4'}), dict(result, registered=True), dict(result, x2_equivalent_hours=None)):
        with pytest.raises(ValueError): m.validate_extension(bad)


def run_pipeline_root(tmp_path, spec, root):
    costs = {key: dict(mean_worker_seconds=1., memory_estimate_gb=.01)
             for job in spec['jobs'] for key in m.cost_keys(job)}
    spec = deepcopy(spec)
    for profile in spec['configuration'].values():
        profile.update(workers_local=[1], jobs_per_worker=1, rounds=1)
    spec['configuration_seconds'] = 240
    spec['memory_estimate_gb'] = {p: .01 for p in spec['phases']}
    spec = m.freeze(spec, a.seal(dict(per_phase_capability=costs)), code_commit='fixture')
    path = tmp_path / (root.name + '_spec.json')
    a.atomic_json(path, a.seal(spec))
    m.prepare(path, root, SETTINGS)
    kinds = sorted({j['kind'] for j in spec['jobs']})
    for host in ('alpha', 'beta'):
        covered = ['a4_fit'] if host == 'alpha' and 'a4_fit' in kinds else kinds
        m.approve_host(root, evidence(host, spec['code_hash'], covered), 'fixture', '2026-10-08')
    with m.transaction(root):
        c = m.Coordinator(root); c.start(); c.save()
    with ProcessPoolExecutor(max_workers=2, mp_context=mp.get_context('spawn')) as pool:
        futures = [pool.submit(h.run_host, h.Loopback(root), tmp_path / (root.name + '_' + host),
            dict(SETTINGS, workers=1), host=host, environment=FINGERPRINT, max_seconds=240) for host in ('alpha', 'beta')]
        for f in futures: f.result()
    status = m.rpc(root, {'op': 'inspect'})['status']
    assert status['complete'], status
    assert sum(s['completed'] for s in status['hosts'].values()) == len(spec['jobs'])
    a.atomic_json(root / 'launches.json', [dict(complete=True, pull=True)])
    return spec, path


def test_single_root_toy_pipeline_inputs_a4_a5_publication_and_receipt(tmp_path):
    from v3 import table_validation_a4 as a4, table_labels_a5 as a5
    from v3.snapshot_a11 import inventory
    cal_path = 'v3/runs/registered/v3_rerun_calibration.json'
    calibration = a.read(a.SIMULATION / cal_path)
    toy = dict(groups=3, runs_per_group=2, particles=2, burn=30, measure=8)
    jobs = tables.build_jobs('sqrt', cal_path, settings_override=toy,
        kernel_override={'n_agents': 16, 'carrying_capacity': 160}, rule_ids=['balanced'],
        physical_contexts=[(.064, 1.), (.064, 1.5)])
    jobs = [a.stable_job(j['kind'], dict(j['config'], route='fv' if j['config']['kernel']['capability'] == 1.5 else 'plain'),
                          j['tag'], j['index']) for j in jobs]
    source = tmp_path / 'source'
    estimate = tables.estimation_spec('sqrt', cal_path, jobs=jobs)
    estimate, _ = run_pipeline_root(tmp_path, estimate, source / 'tables_A1')
    outputs = [runner.completed(source / 'tables_A1/table', j, a.code_identity()) for j in jobs]
    a.atomic_json(source / 'tables_A1_manifest.json', a.seal(dict(jobs=jobs, code_hash=a.code_identity(),
        source_family={'code_hash': a.code_identity()}, tag='pilot', registered=False)))
    tables.assemble(outputs, calibration, source / 'v3_rerun_tables_A1.json', 'sqrt', jobs=jobs)
    probe = tmp_path / 'probe'; a.atomic_json(probe / 'seeds.json', {'seed': 72349024834789})
    plan = tables.prepare_validation(source, cal_path, probe_root=probe, settings_override=dict(toy, census_measure=38))
    run = tmp_path / 'a4'
    plan, plan_path = run_pipeline_root(tmp_path, plan, run)
    plain = next(j for j in plan['jobs'] if j['kind'] == 'a4_validate' and j['config']['route'] == 'plain')
    paths = [r['path'] for r in a.unseal(inventory([plain], run / plain['config']['phase']))['files']]
    assert any('/fit/outputs/' in p for p in paths) and any('/fit/records/' in p for p in paths)
    family = tmp_path / 'family.json'
    a4.publish(plan, run, source, calibration, family, registered=False)
    document = a.read(family)
    identity_path = tmp_path / 'identity.json'
    a.atomic_json(identity_path, dict(family_file_sha256=a.file_hash(family), table_seal_sha256=document['sha256'],
        receipt_file_sha256=a.file_hash(family.with_suffix('.compatibility.json')),
        sidecar_file_sha256=a.file_hash(family.with_suffix('.cell_results.json')), producing_commit='toy', code_hash=a.code_identity()))
    labels = a5.prepare(family, run, plan_path, source, cal_path, identity_path, wall_hours=1.25,
        a3_probe_root=probe, settings_override=toy, instrument=tables.family_instrument('sqrt'))
    label_root = tmp_path / 'a5'
    labels, _ = run_pipeline_root(tmp_path, labels, label_root)
    label_path = tmp_path / 'labels.json'
    a5.publish(labels, label_root, run, source, calibration, label_path, registered=False)
    receipt = tables.finalize_receipt(family, label_path)
    assert a.unseal(receipt)['table_sha256'] == document['sha256']
    assert labels['x2_equivalent_hours'] == 1.25
    # Qualification really re-executes 20 distinct short jobs on both fixture
    # hosts; evidence differs only in host metadata, not in canonical results.
    qual_plan_path = tmp_path / 'qualification.json'
    qual_plan = q.build(plan_path, run, qual_plan_path, kinds=['a4_fit'])
    assert len(qual_plan['jobs']) >= 20
    reference_path, candidate_path = tmp_path / 'ref.json', tmp_path / 'candidate.json'
    q.run(qual_plan_path, reference_path, dict(SETTINGS, workers=2), host='yotko-evo-x2', environment=FINGERPRINT)
    q.run(qual_plan_path, candidate_path, dict(SETTINGS, workers=2), host='loopback', environment=FINGERPRINT)
    document = q.compare(a.read(qual_plan_path), a.read(reference_path), a.read(candidate_path))
    assert q.validate_evidence(document, a.code_identity())['passed']
