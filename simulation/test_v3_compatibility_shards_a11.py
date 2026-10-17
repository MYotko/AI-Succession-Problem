"""Synthetic A11 proof attempts, real spawned workers, no registered outputs."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import ast
import hashlib
import subprocess
from pathlib import Path

import pytest
from test_v3_paths import tmp_path
from test_v3_multihost_a11 import evidence, SETTINGS, FINGERPRINT
from v3 import artifacts as a, compatibility_a10 as c, compatibility_shards_a11 as s
from v3 import host_a11 as host, qualification_a11 as q

ORIGINAL = 'yotko-evo-x2'
SECOND = 'x2-two'


def source_fixture(root, mismatch=False):
    before = a.source_manifest()
    before['v3/artifacts.py'] = '0' * 64
    old = a.digest(before)
    jobs = [a.stable_job('fixture', dict(phase='toy', seconds=.003, kernel={'capability': cap}), 'validation', i)
            for cap in (1., 2., 3., 4.) for i in range(3)]
    profile = dict(kind='fixture', config={'phase': 'toy', 'seconds': .003}, workers_local=[2],
                   workers_x2=[8, 12, 16, 24, 32], threads=[1], rounds=1, jobs_per_worker=1)
    spec = dict(code_hash=old, instrument={'mapping': 'A10', 'k_star': 1.8, 'g': 'linear'}, jobs=jobs,
                phases=['toy'], configuration={'toy': profile}, memory_estimate_gb={'toy': .25},
                pull_dispatch=dict(projection_sha256='p' * 64,
                    job_classes={j['id']: str(i) for i, j in enumerate(jobs)},
                    cost_classes={str(i): dict(worker_seconds=i + 1., memory_gb=.25) for i in range(len(jobs))}))
    source, spec_path, reasons = root / 'old', root / 'spec.json', root / 'reasons.json'
    a.atomic_json(spec_path, a.seal(spec))
    a.atomic_json(source / 'identity.json', dict(code_hash=old, spec_hash=a.digest(spec)))
    a.atomic_json(source / 'manifest.json', a.seal(spec))
    a.atomic_json(source / 'launches.json', [{'complete': True}])
    for job in jobs:
        output = source / 'toy/outputs' / (job['id'] + '.json')
        a.atomic_json(output, dict(job=job, code_hash=old, result=dict(seed=job['seed'] + int(mismatch), fixture=True)))
        a.atomic_json(source / 'toy/records' / (job['id'] + '.json'),
                      dict(job=job, code_hash=old, status='complete', output_hash=a.file_hash(output)))
    a.atomic_json(reasons, dict(producing_source_manifest=before, reasons={'v3/artifacts.py': 'Synthetic producing identity.'}))
    return [dict(spec=str(spec_path), root=str(source))], reasons


def hosts(two=True):
    entries = {name: dict(qualification=evidence(name, a.code_identity(), speed=speed), settings=SETTINGS, memory_floor_gb=.3)
               for name, speed in [(ORIGINAL, 1.), (SECOND, .8)][:2 if two else 1]}
    for entry in entries.values():
        entry['qualification_plan_sha256'] = a.unseal(entry['qualification'])['plan']['sha256']
    return entries


@pytest.fixture
def environment(monkeypatch, tmp_path):
    # Uncommitted local tests cannot pass a production commit check or claim a
    # real qualified host. Only those OS boundaries are replaced.
    monkeypatch.setattr(s, 'verify_code', lambda commit: None)
    monkeypatch.setattr(s.platform, 'node', lambda: ORIGINAL)
    monkeypatch.setattr(host, 'fingerprint', lambda: FINGERPRINT)
    monkeypatch.setattr(c, 'RECORD_DIRECTORY', tmp_path / 'registered_reservations')


def prepared(root, two=True, mismatch=False):
    sources, reasons = source_fixture(root, mismatch)
    target = root / 'proof.json'
    p = s.freeze(sources, reasons, target, hosts(two), 'f' * 40)
    return target.with_suffix('.attempt.json'), p, sources, reasons


def run_all(path, p, monkeypatch):
    results = []
    for name in p['hosts']:
        monkeypatch.setattr(s.platform, 'node', lambda: ORIGINAL)
        s.stage(path, name)
        monkeypatch.setattr(s.platform, 'node', lambda name=name: name)
        result = s.run_shard(path, name)
        assert result['passed']
        results.append(s.host_directory(path, name) / 'result.json')
    monkeypatch.setattr(s.platform, 'node', lambda: ORIGINAL)
    return results


def normalized(record):
    record = deepcopy(record)
    record.pop('execution')
    for row in record['proofs']:
        row.pop('runtime', None)
    return record


def test_partition_freeze_and_finality_before_any_execution(tmp_path, environment):
    path, p, sources, reasons = prepared(tmp_path)
    assert p['selected_job_ids'] == c._selected(p['record']['populations'])
    ids = sum(p['assignments'].values(), [])
    assert len(ids) == len(set(ids)) == 8 and set(ids) == set(p['selected_job_ids'])
    assert s.assign(dict(reversed(list(p['items'].items()))), dict(reversed(list(p['hosts'].items())))) == p['assignments']
    with pytest.raises(ValueError, match='final'):
        s.freeze(sources, reasons, tmp_path / 'proof.json', hosts(), 'f' * 40)
    with pytest.raises(ValueError, match='final'):
        c.build_record(sources, reasons, tmp_path / 'proof.json')
    with pytest.raises(ValueError, match='identity pair'):
        s.freeze(sources, reasons, tmp_path / 'different.json', hosts(), 'f' * 40)
    with pytest.raises(ValueError, match='identity pair'):
        c.build_record(sources, reasons, tmp_path / 'different.json')
    assert not list(tmp_path.rglob('started.json'))


def test_assignment_uses_cost_and_relative_throughput():
    items = {str(i): dict(resources=dict(worker_seconds=10., memory_gb=1.)) for i in range(12)}
    entries = {h: dict(worker_cap=1, memory_gb=10., memory_floor_gb=1., relative_throughput=r)
               for h, r in [('fast', 2.), ('slow', 1.)]}
    assigned = s.assign(items, entries)
    assert len(assigned['fast']) == 8 and len(assigned['slow']) == 4


@pytest.mark.parametrize('operation', ['stage', 'run', 'combine'])
def test_relocated_attempt_cannot_create_a_fresh_shard_round(tmp_path, environment, operation):
    path, p, _, _ = prepared(tmp_path)
    copied = tmp_path / 'another_attempt.json'
    copied.write_bytes(path.read_bytes())
    with pytest.raises(ValueError, match='attempt location changed'):
        if operation == 'stage': s.stage(copied, ORIGINAL)
        elif operation == 'run': s.run_shard(copied, ORIGINAL)
        else: s.combine(copied, [])
    assert not list(tmp_path.rglob('started.json'))


def test_single_and_two_host_real_spawned_records_equal(tmp_path, environment, monkeypatch):
    path, p, sources, reasons = prepared(tmp_path)
    results = run_all(path, p, monkeypatch)
    combined = s.combine(path, results)
    # Two independent synthetic worlds for the equivalence experiment. Within
    # either world B1 forbids a second proof of this pair, regardless of output.
    monkeypatch.setattr(c, 'RECORD_DIRECTORY', tmp_path / 'independent_single_host_world')
    single = c.build_record(sources, reasons, tmp_path / 'single.json', workers=2)
    assert normalized(combined) == normalized(single)
    assert combined['passed'] and len(combined['proofs']) == 8
    monkeypatch.setattr(c, 'RECORD_DIRECTORY', tmp_path / 'registered_reservations')
    for name in p['hosts']:
        result = a.unseal(a.read(s.host_directory(path, name) / 'result.json'))
        assert result['configuration']
        assert all(e['running_gb'] <= e['budget_gb'] for e in result['admission'])
        monkeypatch.setattr(s.platform, 'node', lambda name=name: name)
        with pytest.raises(ValueError, match='final'):
            s.run_shard(path, name)
    monkeypatch.setattr(s.platform, 'node', lambda: ORIGINAL)
    with pytest.raises(ValueError, match='final'):
        s.combine(path, results)


def fake_shards(path, p):
    """Only combine refusal tests fabricate results; success runs real workers."""
    paths = []
    for name, ids in p['assignments'].items():
        value = dict(schema=s.SCHEMA + '-result', attempt_sha256=a.digest(p), host=name,
                     fingerprint=FINGERPRINT, code_hash=a.code_identity(), code_commit=p['code_commit'],
                     job_ids=ids, started_epoch=1, finished_epoch=2, configuration={'fixture': True},
                     x2_equivalent_hours=1 / 3600, passed=True, workers=2,
                     proofs=[c.proof_row(p['items'][j], dict(after_sha256=p['items'][j]['before_sha256'])) for j in ids])
        target = s.host_directory(path, name) / 'result.json'
        a.atomic_json(target, a.seal(value))
        a.atomic_json(target.with_name('started.json'), a.seal(dict(attempt_sha256=a.digest(p), host=name, started_epoch=1)))
        paths.append(target)
    return paths


@pytest.mark.parametrize('defect', ['foreign_host', 'duplicate_host', 'attempt', 'identity', 'commit',
                                  'fingerprint', 'missing_job', 'duplicate_job', 'foreign_job', 'job_hash',
                                  'before_hash', 'source_hash', 'mismatch', 'pass_flag', 'incomplete',
                                  'wrong_start'])
def test_every_combine_refusal_is_final(tmp_path, environment, defect):
    path, p, sources, reasons = prepared(tmp_path)
    paths = fake_shards(path, p)
    originals = {f: f.read_bytes() for result in paths for f in (result, result.with_name('started.json'))}
    value = a.unseal(a.read(paths[0]))
    if defect == 'foreign_host': value['host'] = 'foreign'
    elif defect == 'duplicate_host': value['host'] = a.unseal(a.read(paths[1]))['host']
    elif defect == 'attempt': value['attempt_sha256'] = 'a' * 64
    elif defect == 'identity': value['code_hash'] = 'a' * 64
    elif defect == 'commit': value['code_commit'] = 'a' * 40
    elif defect == 'fingerprint': value['fingerprint'] = {}
    elif defect == 'missing_job': value['proofs'].pop()
    elif defect == 'duplicate_job': value['proofs'][1] = value['proofs'][0]
    elif defect == 'foreign_job': value['proofs'][0]['job_id'] = 'foreign'
    elif defect == 'job_hash': value['proofs'][0]['job_sha256'] = 'b' * 64
    elif defect == 'before_hash': value['proofs'][0]['before_sha256'] = 'b' * 64
    elif defect == 'source_hash': value['proofs'][0]['source_output_sha256'] = 'b' * 64
    elif defect == 'mismatch':
        value['proofs'][0].update(after_sha256='b' * 64, passed=False)
        value['passed'] = False
    elif defect == 'pass_flag': value['proofs'][0]['passed'] = False
    elif defect == 'incomplete': value.pop('configuration')
    elif defect == 'wrong_start':
        start = a.unseal(a.read(paths[0].with_name('started.json'))); start['started_epoch'] = 0
        a.atomic_json(paths[0].with_name('started.json'), a.seal(start))
    a.atomic_json(paths[0], a.seal(value))
    with pytest.raises(ValueError): s.combine(path, paths)
    failed = a.unseal(a.read(tmp_path / 'proof.json'))
    assert failed['passed'] is False and failed['error']
    for f, raw in originals.items(): f.write_bytes(raw)
    with pytest.raises(ValueError, match='final'): s.combine(path, paths)
    with pytest.raises(ValueError, match='failed'): c.approve_record(tmp_path / 'proof.json', 'operator', '2026-10-17')


@pytest.mark.parametrize('defect', ['missing_start', 'missing_result', 'extra_result', 'extra_start',
                                  'foreign_directory', 'extra_copy', 'mistyped_path', 'duplicate_path',
                                  'missing_path', 'unreadable', 'invalid_json', 'invalid_seal'])
def test_combine_structure_refuses_without_writes_then_corrected_retry_passes(tmp_path, environment, monkeypatch, defect):
    path, p, _, _ = prepared(tmp_path)
    paths = fake_shards(path, p)
    original = {f: f.read_bytes() for result in paths for f in (result, result.with_name('started.json'))}
    arguments = list(paths)
    extra = None
    if defect == 'missing_start': paths[0].with_name('started.json').unlink()
    elif defect == 'missing_result': paths[0].unlink()
    elif defect in ('extra_result', 'extra_start', 'foreign_directory', 'extra_copy'):
        extra = {'extra_result': paths[0].parent / 'copy/result.json',
                 'extra_start': paths[0].parent / 'copy/started.json',
                 'foreign_directory': paths[0].parent.parent / 'foreign/result.json',
                 'extra_copy': paths[0].with_name('result_copy.json')}[defect]
        a.atomic_json(extra, a.seal({}))
    elif defect == 'mistyped_path': arguments[0] = paths[0].with_name('reslut.json')
    elif defect == 'duplicate_path': arguments.append(paths[0])
    elif defect == 'missing_path': arguments.pop()
    elif defect == 'invalid_json': paths[0].write_bytes(b'{')
    elif defect == 'invalid_seal': a.atomic_json(paths[0], dict(payload={}, sha256='0' * 64))
    before = {str(f): f.read_bytes() for f in tmp_path.rglob('*') if f.is_file()}
    with monkeypatch.context() as m:
        if defect == 'unreadable':
            real_read = Path.read_bytes
            def refused(f):
                if f == paths[0]: raise PermissionError('synthetic unreadable transfer')
                return real_read(f)
            m.setattr(Path, 'read_bytes', refused)
        with pytest.raises((ValueError, OSError)):
            s.combine(path, arguments)
    assert {str(f): f.read_bytes() for f in tmp_path.rglob('*') if f.is_file()} == before
    assert not Path(p['target']).exists()
    assert not Path(p['target']).with_suffix('.combine.json').exists()
    assert not Path(p['target']).with_suffix('.combine.lock').exists()
    for f, raw in original.items(): f.write_bytes(raw)
    if extra: extra.unlink()
    # Paths come from the frozen attempt, not from operator arguments.
    assert s.combine(path)['passed']


def test_combine_cli_derives_paths_without_shard_arguments(tmp_path, environment, monkeypatch):
    import sys
    path, p, _, _ = prepared(tmp_path)
    fake_shards(path, p)
    monkeypatch.chdir(a.SIMULATION)
    monkeypatch.setattr(sys, 'argv', ['compatibility_shards_a11', 'combine', str(path.relative_to(a.SIMULATION))])
    assert s.main() == 0
    assert a.unseal(a.read(p['target']))['passed']


@pytest.mark.parametrize('defect', ['missing', 'old_identity', 'wrong_host', 'wrong_reference', 'too_few', 'kind', 'settings'])
def test_qualification_precondition_before_freeze(tmp_path, environment, defect):
    sources, reasons = source_fixture(tmp_path)
    entries = hosts()
    if defect == 'missing': entries[SECOND]['qualification'] = a.seal({})
    elif defect == 'old_identity': entries[SECOND]['qualification'] = evidence(SECOND, 'a' * 64)
    elif defect == 'wrong_host': entries[SECOND]['qualification'] = evidence('foreign', a.code_identity())
    elif defect == 'kind': entries[SECOND]['qualification'] = evidence(SECOND, a.code_identity(), kinds=('table',))
    elif defect == 'settings': entries[SECOND]['settings'] = dict(SETTINGS, workers=1)
    else:
        e = a.unseal(entries[SECOND]['qualification'])
        if defect == 'wrong_reference': e['reference']['host'] = 'other'
        else: e['proofs'] = e['proofs'][:19]
        entries[SECOND]['qualification'] = a.seal(e)
    with pytest.raises((ValueError, KeyError)):
        s.freeze(sources, reasons, tmp_path / 'proof.json', entries, 'f' * 40)
    assert not (tmp_path / 'proof.attempt.json').exists()


def test_qualification_bundle_and_existing_validator(tmp_path, environment):
    sources, _ = source_fixture(tmp_path)
    path = tmp_path / 'qualification.json'
    plan = s.qualification_bundle(sources, path)
    assert len(plan['jobs']) == 20 and len({j['seed'] for j in plan['jobs']}) == 20
    ref = q.run(path, tmp_path / 'reference.json', SETTINGS, environment=FINGERPRINT, host=ORIGINAL)
    other = q.run(path, tmp_path / 'candidate.json', SETTINGS, environment=FINGERPRINT, host=SECOND)
    document = q.compare(a.read(path), a.seal(ref), a.seal(other))
    assert q.validate_evidence(document, a.code_identity())['passed']


def test_memory_admission_and_longest_first_real_pool(tmp_path, monkeypatch):
    monkeypatch.setattr(s, 'memory_budget', lambda *args: 6.)
    items = [dict(job=a.stable_job('fixture', dict(seconds=.003), 'validation', i), phase_root=str(tmp_path),
                  producing_code_hash='0' * 64,
                  resources=dict(worker_seconds=i + 1., memory_gb=3., memory_class=str(i))) for i in range(8)]
    before = a.canonical(items)
    fresh, trace = s.run_items(items, 12, 6.)
    assert len(fresh) == 8 and a.canonical(items) == before
    assert trace[0]['job_id'] == items[-1]['job']['id']
    assert max(t['running'] for t in trace) == 2
    assert all(t['running_gb'] <= 6. for t in trace)
    with pytest.raises(ValueError, match='exceeds'): s.run_items(items, 2, 2.9)


def test_budget_rule_cap_and_unknown_memory(monkeypatch):
    from v3 import production_runner as r
    monkeypatch.setattr(r, 'mem_available_bytes', lambda: 100_000_000_000)
    monkeypatch.setattr(r, 'available_cpus', lambda: 32)
    assert s.memory_budget() == 80. and s.memory_budget(80.) == 64.
    assert s.worker_cap(dict(SETTINGS, workers=100)) == 12
    assert s.worker_cap(dict(SETTINGS, profile='x2', workers=100, cpu_budget=32)) == 28
    monkeypatch.setattr(r, 'mem_available_bytes', lambda: None)
    with pytest.raises(ValueError, match='measured'): s.memory_budget()


def test_configuration_uses_full_job_memory_and_tests_the_cap(tmp_path, environment, monkeypatch):
    path, p, _, _ = prepared(tmp_path, two=False)
    entry = p['hosts'][ORIGINAL]
    entry['settings'] = dict(SETTINGS, workers=2)
    entry['memory_floor_gb'] = 2.
    for profile in p['profiles'].values():
        profile['profile']['workers_local'] = [2, 4, 8, 12]
    counts = []
    def run(tasks, workers, budget, **kwargs):
        counts.append(workers)
        assert workers * kwargs['memory_floor_gb'] <= budget
        assert kwargs['idle_wait_seconds'] == 180.
        return ({t['job']['id']: dict(after_sha256='a' * 64, _worker_seconds=.1, _peak_rss_bytes=1000) for t in tasks}, [])
    monkeypatch.setattr(s, 'run_items', run)
    configured = s.configure_host(p, ORIGINAL, tmp_path / 'configuration', 6., None)
    assert counts == [2, 3]  # Memory cap 3 is tested even though absent from the listed counts.
    assert all(c['chosen']['workers'] <= 2 for c in configured.values())


def test_projection_matches_frozen_assignment_without_output_reads(tmp_path, environment, monkeypatch):
    path, p, sources, _ = prepared(tmp_path)
    original_read = s.read
    def spec_only(path):
        assert Path(path) == Path(sources[0]['spec'])
        return original_read(path)
    monkeypatch.setattr(s, 'read', spec_only)
    projected = s.project(sources, hosts())
    assert projected['selected_jobs'] == 8
    assert projected['assignment_sha256'] == a.digest(p['assignments'])
    assert projected['wall_hours'] > 0 and projected['x2_equivalent_hours'] > projected['wall_hours']


def test_shard_failure_and_interruption_spend_attempt(tmp_path, environment, monkeypatch):
    path, p, _, _ = prepared(tmp_path, two=False)
    s.stage(path, ORIGINAL)
    def configured(*args):
        return {'fixture': dict(chosen={'workers': 1}, observed_memory_gb=.3)}
    monkeypatch.setattr(s, 'configure_host', configured)
    def fail(*args, **kwargs): raise KeyboardInterrupt('synthetic interruption after start')
    monkeypatch.setattr(s, 'run_items', fail)
    with pytest.raises(KeyboardInterrupt): s.run_shard(path, ORIGINAL)
    root = s.host_directory(path, ORIGINAL)
    assert a.unseal(a.read(root / 'result.json'))['passed'] is False
    with pytest.raises(ValueError, match='final'): s.run_shard(path, ORIGINAL)
    with pytest.raises(ValueError): s.combine(path, [root / 'result.json'])


def test_snapshot_hash_readonly_and_old_aliases(tmp_path, monkeypatch):
    source = tmp_path / 'old/calibration.json'
    a.atomic_json(source, {'synthetic': True})
    item = dict(job=a.stable_job('fixture', {'calibration_path': str(source)}, 'validation', 1), phase_root=str(tmp_path))
    snapshot = s.portable_inventory([item])
    bundle = tmp_path / 'bundle'
    s.stage_inputs(snapshot, bundle)
    view = s.receive_inputs(snapshot, bundle, tmp_path / 'scratch')
    with a.input_view(view):
        assert a.read(source) == {'synthetic': True}
        assert Path(a.input_path(source)) != source
        with pytest.raises(ValueError, match='not in'): a.read(source.with_name('unlisted.json'))
    row = next(r for r in a.unseal(snapshot)['files'] if r['source'] == str(source))
    copied = bundle / row['path']
    assert not (copied.stat().st_mode & 0o200)
    copied.chmod(0o644); copied.write_bytes(b'corrupt')
    with pytest.raises(ValueError, match='hash'): s.receive_inputs(snapshot, bundle, tmp_path / 'again')


def test_selection_comparison_and_approval_functions_unchanged():
    baseline = subprocess.run(['git', 'show', '25b5f052:simulation/v3/compatibility_a10.py'],
                              capture_output=True, check=True, text=True).stdout
    current = Path(c.__file__).read_text()
    for name in ('_stratum', '_selected', 'comparison_bytes', 'approve_record'):
        def function(text):
            node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
            return ast.get_source_segment(text, node)
        assert function(current) == function(baseline)


@pytest.mark.parametrize('field', ['memory_gb', 'relative_throughput', 'fingerprint', 'worker_cap'])
def test_frozen_host_measurements_cannot_differ_from_qualification(tmp_path, environment, field):
    path, p, _, _ = prepared(tmp_path)
    p['hosts'][SECOND][field] = {} if field == 'fingerprint' else 1234
    a.atomic_json(path, a.seal(p))
    with pytest.raises(ValueError, match='host measurements'): s.load_attempt(path)


def test_commit_verification_refuses_uncommitted_source(monkeypatch):
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, check=True, text=True).stdout.strip()
    changed = a.source_manifest()
    changed['v3/artifacts.py'] = '0' * 64
    monkeypatch.setattr(host, 'source_manifest', lambda: changed)
    with pytest.raises(ValueError, match='differs'): s.verify_code(commit)
    with pytest.raises(ValueError, match='frozen commit'): s.verify_code('0' * 40)


def test_real_a4_job_uses_copied_a1_and_fit_with_original_roots_absent(tmp_path):
    from test_v3_a13 import toy_original
    from v3.production_runner import execute
    plan_path, root, _, _, _, source, _, _, _ = toy_original(tmp_path / 'pipeline')
    plan = a.unseal(a.read(plan_path))
    job = next(j for j in plan['jobs'] if j['config']['phase'] == 'validate_plain')
    phase_root = root / 'validate_plain'
    original = execute(job, registered=False, root=phase_root)
    item = dict(job=job, phase_root=str(phase_root), producing_code_hash=a.code_identity())
    snapshot = s.portable_inventory([item])
    s.stage_inputs(snapshot, tmp_path / 'bundle')
    view = s.receive_inputs(snapshot, tmp_path / 'bundle', tmp_path / 'received')
    # Both directories are synthetic, inside this test's scoped fixture.
    source.rename(source.with_name('hidden_source'))
    root.rename(root.with_name('hidden_validation'))
    s.check_input_paths([item], view)
    broken = deepcopy(view)
    broken['paths'] = {k: v for k, v in broken['paths'].items() if '/fit/' not in k.replace('\\', '/')}
    with pytest.raises(ValueError): s.check_input_paths([item], broken)
    fresh = c._execute_proof(dict(item, input_view=view))
    assert fresh['after_sha256'] == hashlib.sha256(c.comparison_bytes(job, original)).hexdigest(), fresh.get('error')


def process_probe(item):
    import os
    from v3.production_runner import peak_rss_bytes
    allocation = bytearray(item['bytes'])
    return dict(after_sha256='a' * 64, _pid=os.getpid(), _peak_rss_bytes=peak_rss_bytes(), _allocated=len(allocation))


def test_fresh_process_and_peak_rss_for_every_job(tmp_path, monkeypatch):
    from v3.production_runner import peak_rss_bytes
    monkeypatch.setattr(s, '_execute_proof', process_probe)
    items = [dict(job=a.stable_job('fixture', {}, 'validation', i), bytes=24_000_000 if i == 0 else 1,
                  resources=dict(worker_seconds=3 - i, memory_gb=.3, memory_class=str(i))) for i in range(3)]
    results, _ = s.run_items(items, 1, 1.)
    assert len({r['_pid'] for r in results.values()}) == 3
    if peak_rss_bytes() is None:  # The runner reports no ru_maxrss on Windows.
        assert all(r['_peak_rss_bytes'] is None for r in results.values())
    else:
        assert all(r['_peak_rss_bytes'] > 0 for r in results.values())
    assert results[items[0]['job']['id']]['_allocated'] == 24_000_000


def test_exclusive_pair_reservation_is_independent_of_output(tmp_path, environment):
    record = dict(producing_code_hash='1' * 64, new_code_hash=a.code_identity())
    def reserve(index):
        try:
            s.reserve_attempt(record, {'index': index}, tmp_path / f'output{index}.attempt.json')
            return True
        except ValueError:
            return False
    with ThreadPoolExecutor(2) as pool:
        assert sum(pool.map(reserve, range(2))) == 1


@pytest.mark.parametrize('operation', ['run', 'combine'])
def test_pair_reservation_checked_when_using_attempt(tmp_path, environment, operation):
    path, p, _, _ = prepared(tmp_path)
    reservation = s.reservation_path(p['record'])
    saved = a.unseal(a.read(reservation)); saved['attempt_sha256'] = '0' * 64
    a.atomic_json(reservation, a.seal(saved))
    with pytest.raises(ValueError, match='different compatibility attempt'):
        if operation == 'run': s.run_shard(path, ORIGINAL)
        else: s.combine(path, [])


@pytest.mark.parametrize('failure', ['inputs', 'fingerprint', 'memory', 'configuration'])
def test_preconditions_are_retryable_and_precede_start(tmp_path, environment, monkeypatch, failure):
    path, p, _, _ = prepared(tmp_path, two=False)
    s.stage(path, ORIGINAL)
    root = s.host_directory(path, ORIGINAL)
    def fail(*args, **kwargs): raise ValueError('synthetic precondition failure')
    with monkeypatch.context() as m:
        if failure == 'fingerprint': m.setattr(host, 'fingerprint', lambda: {})
        else: m.setattr(s, {'inputs': 'receive_inputs', 'memory': 'wait_for_memory', 'configuration': 'configure_host'}[failure], fail)
        with pytest.raises(ValueError): s.run_shard(path, ORIGINAL)
    assert not (root / 'started.json').exists() and not (root / 'result.json').exists()
    assert not a.unseal(a.read(root / 'preflight.json'))['passed']
    def configured(*args):
        assert not (root / 'started.json').exists()
        return {'fixture': dict(chosen={'workers': 1}, observed_memory_gb=.3)}
    def execute(tasks, *args, **kwargs):
        assert (root / 'started.json').exists()
        assert a.unseal(a.read(root / 'preflight.json'))['passed']
        return {i['job']['id']: dict(after_sha256=i['before_sha256']) for i in tasks}, []
    monkeypatch.setattr(s, 'configure_host', configured)
    monkeypatch.setattr(s, 'run_items', execute)
    assert s.run_shard(path, ORIGINAL)['passed']


def test_single_host_precondition_failure_does_not_reserve_pair(tmp_path, environment, monkeypatch):
    sources, reasons = source_fixture(tmp_path)
    record, _, _ = c.collect_record(sources, reasons)
    def fail(*args): raise ValueError('not enough memory before reservation')
    with monkeypatch.context() as m:
        m.setattr(s, 'single_preflight', fail)
        with pytest.raises(ValueError, match='before reservation'):
            c.build_record(sources, reasons, tmp_path / 'single.json', workers=2)
    assert not (tmp_path / 'single.attempt.json').exists()
    assert not s.reservation_path(record).exists()
    assert c.build_record(sources, reasons, tmp_path / 'single.json', workers=2)['passed']
    with pytest.raises(ValueError, match='identity pair'):
        s.freeze(sources, reasons, tmp_path / 'another.json', hosts(), 'f' * 40)


@pytest.mark.parametrize('bound', [180., 1800.])
def test_memory_release_wait_is_bounded(monkeypatch, bound):
    clock = [0.]
    monkeypatch.setattr(s.time, 'monotonic', lambda: clock[0])
    monkeypatch.setattr(s.time, 'sleep', lambda seconds: clock.__setitem__(0, clock[0] + seconds))
    monkeypatch.setattr(s, 'memory_budget', lambda *args: .1 if clock[0] < 2 else 4.)
    assert s.wait_for_memory(3.) == 4. and clock[0] == 2.
    clock[0] = 0.
    monkeypatch.setattr(s, 'memory_budget', lambda *args: .1)
    with pytest.raises(ValueError, match=f'{bound:g} seconds'): s.wait_for_memory(3., timeout=bound)
    assert clock[0] == bound
    clock[0] = 0.
    with pytest.raises(ValueError, match='qualified'): s.wait_for_memory(9., 10.)
    assert clock[0] == 0.


def test_live_memory_dip_waits_without_starting_a_job(tmp_path, monkeypatch):
    clock = [0.]
    monkeypatch.setattr(s.time, 'monotonic', lambda: clock[0])
    monkeypatch.setattr(s.time, 'sleep', lambda seconds: clock.__setitem__(0, clock[0] + seconds))
    monkeypatch.setattr(s, 'memory_budget', lambda *args: .1 if clock[0] < 181 else 1.)
    item = dict(job=a.stable_job('fixture', {}, 'validation', 1), phase_root=str(tmp_path), producing_code_hash='0' * 64,
                resources=dict(worker_seconds=1., memory_gb=.3, memory_class='fixture'))
    results, trace = s.run_items([item], 1, 1.)
    assert clock[0] == 181. and len(trace) == 1 and results[item['job']['id']]['after_sha256']
    assert s.MEMORY_WAIT_SECONDS == 180. and s.PROOF_MEMORY_WAIT_SECONDS == 1800.


def test_proof_idle_timeout_spends_no_memory_before_thirty_minutes(tmp_path, monkeypatch):
    clock = [0.]
    monkeypatch.setattr(s.time, 'monotonic', lambda: clock[0])
    monkeypatch.setattr(s.time, 'sleep', lambda seconds: clock.__setitem__(0, clock[0] + seconds))
    monkeypatch.setattr(s, 'memory_budget', lambda *args: .1)
    monkeypatch.setattr(s.ProcessPoolExecutor, 'submit', lambda *args: pytest.fail('job admitted without memory'))
    item = dict(job=a.stable_job('fixture', {}, 'validation', 1), phase_root=str(tmp_path), producing_code_hash='0' * 64,
                resources=dict(worker_seconds=1., memory_gb=.3, memory_class='fixture'))
    with pytest.raises(ValueError, match='1800 seconds'):
        s.run_items([item], 1, 1.)
    assert clock[0] == 1800.


@pytest.mark.parametrize('bad_hash', [False, True])
def test_twenty_per_assigned_kind_and_bundle_hash_required(tmp_path, environment, bad_hash):
    sources, reasons = source_fixture(tmp_path)
    entries = hosts()
    e = a.unseal(evidence(SECOND, a.code_identity(), kinds=('fixture', 'table')))
    plan = a.unseal(e['plan'])
    # Nineteen fixture plus twenty table proofs pass the old total-count rule.
    plan['jobs'] = [j for j in plan['jobs'] if j != next(j for j in plan['jobs'] if j['kind'] == 'fixture')]
    document = a.seal(plan)
    ids = {j['id'] for j in plan['jobs']}
    for run in (e['reference'], e['candidate']):
        run['plan_sha256'] = document['sha256']
        run['proofs'] = [r for r in run['proofs'] if r['job_id'] in ids]
    entries[SECOND]['qualification'] = q.compare(document, a.seal(e['reference']), a.seal(e['candidate']))
    entries[SECOND]['qualification_plan_sha256'] = '0' * 64 if bad_hash else document['sha256']
    q.validate_evidence(entries[SECOND]['qualification'], a.code_identity())
    with pytest.raises(ValueError, match='plan hash' if bad_hash else 'per assigned kind'):
        s.freeze(sources, reasons, tmp_path / 'proof.json', entries, 'f' * 40)


@pytest.mark.parametrize('interruption', [OSError, KeyboardInterrupt])
def test_interrupted_combine_reuses_exact_inputs_and_deterministic_record(tmp_path, environment, monkeypatch, interruption):
    path, p, _, _ = prepared(tmp_path)
    paths = fake_shards(path, p)
    captured = []
    original_write = s.atomic_json
    def fail(target, document):
        if Path(target) != Path(p['target']): return original_write(target, document)
        captured.append(a.canonical(document))
        raise interruption('synthetic interrupted final write')
    with monkeypatch.context() as m:
        m.setattr(s, 'atomic_json', fail)
        with pytest.raises(interruption): s.combine(path, paths)
    assert not Path(p['target']).exists()
    marker = Path(p['target']).with_suffix('.combine.json').read_bytes()
    result = s.combine(path, list(reversed(paths)))
    assert result['passed'] and a.canonical(a.read(p['target'])) == captured[0]
    assert Path(p['target']).with_suffix('.combine.json').read_bytes() == marker
    with pytest.raises(ValueError, match='final'): s.combine(path, paths)


@pytest.mark.parametrize('change', ['result', 'started', 'added_file', 'added_argument'])
def test_interrupted_combine_refuses_changed_or_added_inputs(tmp_path, environment, monkeypatch, change):
    path, p, _, _ = prepared(tmp_path)
    paths = fake_shards(path, p)
    original_write = s.atomic_json
    def fail(target, document):
        if Path(target) != Path(p['target']): return original_write(target, document)
        raise OSError('synthetic interrupted final write')
    with monkeypatch.context() as m:
        m.setattr(s, 'atomic_json', fail)
        with pytest.raises(OSError): s.combine(path, paths)
    if change == 'added_file':
        a.atomic_json(paths[0].parent / 'extra/result.json', a.seal({'foreign': True}))
    elif change == 'added_argument': paths.append(paths[0])
    else:
        target = paths[0] if change == 'result' else paths[0].with_name('started.json')
        value = a.unseal(a.read(target)); value['different'] = True
        a.atomic_json(target, a.seal(value))
    message = ('extra shard' if change == 'added_file' else 'path cross-check' if change == 'added_argument'
               else 'inputs changed')
    with pytest.raises(ValueError, match=message): s.combine(path, paths)
    assert not Path(p['target']).exists()


@pytest.mark.parametrize('after_binding', [False, True])
def test_combine_binding_interruption_is_recoverable(tmp_path, environment, monkeypatch, after_binding):
    path, p, _, _ = prepared(tmp_path)
    paths = fake_shards(path, p)
    original_write = s.atomic_json
    marker = Path(p['target']).with_suffix('.combine.json')
    def fail(target, document):
        assert Path(target) == marker
        if after_binding: original_write(target, document)
        raise OSError('synthetic interrupted binding write')
    with monkeypatch.context() as m:
        m.setattr(s, 'atomic_json', fail)
        with pytest.raises(OSError): s.combine(path, paths)
    assert marker.exists() is after_binding
    assert not Path(p['target']).exists()
    assert s.combine(path, paths)['passed']
