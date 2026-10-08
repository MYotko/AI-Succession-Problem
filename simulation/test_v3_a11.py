"""A11 execution boundaries. All records and source identities are toy fixtures."""
from copy import deepcopy
import hashlib
import subprocess
import time

import pytest

from test_v3_paths import tmp_path
from v3 import artifacts as a
from v3 import compatibility_a10 as compat
from v3 import tables_a10 as tables


def record_fixture(tmp_path, monkeypatch):
    after = a.source_manifest()
    before = dict(after)
    before['v3/artifacts.py'] = '0' * 64
    old, new = a.digest(before), a.digest(after)
    populations = [{'phase': 'table', 'capability': 1.5, 'setting': 'primary',
                    'job_ids': ['one', 'two', 'three']}]
    record = dict(schema=compat.SCHEMA, producing_code_hash=old, new_code_hash=new,
                  producing_source_manifest=before, new_source_manifest=after,
                  changed_files=compat.changed_files(before, after),
                  reasons={'v3/artifacts.py': 'Toy execution-only change.'},
                  populations=populations, passed=True, comparison=compat.COMPARISON,
                  operator_approval={'approved': True, 'operator': 'fixture', 'date': '2026-10-08'},
                  proofs=[dict(job_id=j, job_sha256=a.digest(j), before_sha256=a.digest([j]),
                               after_sha256=a.digest([j]), passed=True)
                          for j in compat._selected(populations)])
    path = tmp_path / compat.record_name(old, new)
    monkeypatch.setattr(compat, 'RECORD_DIRECTORY', tmp_path)
    return record, path


def commit_fixture(record, path, monkeypatch):
    a.atomic_json(path, a.seal(record))
    committed = path.read_bytes()
    monkeypatch.setattr(compat, '_committed_bytes', lambda p: committed)


def test_valid_committed_approved_record_admits_old_identity(tmp_path, monkeypatch):
    record, path = record_fixture(tmp_path, monkeypatch)
    commit_fixture(record, path, monkeypatch)
    assert compat.validate_record(path) == record['producing_code_hash']
    assert compat.accepted_identities() == {a.code_identity(), record['producing_code_hash']}


@pytest.mark.parametrize('defect', ['failed', 'proof_failed', 'approval', 'uncommitted', 'modified',
                                  'after_hashes', 'new_identity', 'missing_file', 'sample', 'comparison'])
def test_invalid_compatibility_record_never_admits(tmp_path, monkeypatch, defect):
    record, path = record_fixture(tmp_path, monkeypatch)
    if defect == 'failed':
        record['passed'] = False
    if defect == 'proof_failed':
        record['proofs'][0]['after_sha256'] = 'f' * 64
    if defect == 'approval':
        record['operator_approval'] = None
    if defect == 'after_hashes':
        record['new_source_manifest']['v3/artifacts.py'] = 'f' * 64
    if defect == 'new_identity':
        record['new_code_hash'] = 'f' * 64
    if defect == 'missing_file':
        record['changed_files'] = {}
    if defect == 'sample':
        record['proofs'].pop()
    if defect == 'comparison':
        record['comparison'] = {'exclude': 'all results'}
    commit_fixture(record, path, monkeypatch)
    if defect == 'uncommitted':
        def missing(p):
            raise subprocess.CalledProcessError(1, ['git', 'show'])
        monkeypatch.setattr(compat, '_committed_bytes', missing)
    if defect == 'modified':
        path.write_bytes(path.read_bytes() + b' ')
    with pytest.raises((ValueError, subprocess.CalledProcessError)):
        compat.validate_record(path)
    assert compat.accepted_identities() == {a.code_identity()}


def test_proof_sampling_and_canonical_comparison():
    populations = [dict(phase=p, capability=c, setting=s, job_ids=[f'{p}-{c}-{s}-{i}' for i in range(n)])
                   for p in ('estimate', 'validate') for c in (1., 5.)
                   for s, n in (('primary', 3), ('double_length', 1))]
    selected = compat._selected(populations)
    assert len(selected) == 12
    for group in populations:
        expected = sorted(group['job_ids'], key=lambda j: (a.digest(['A11-compatibility', group['phase'], j]), j))[:2]
        assert [j for j in selected if j in group['job_ids']] == expected
    result = dict(rows={'science': [1., 2.]}, seconds=1, trajectory_seconds=2, rescore_seconds=3,
                  scoring_seconds_by_k_star={'1.8': 4})
    assert compat.comparison_bytes({'id': 'job'}, result) == compat.comparison_bytes({'id': 'job'}, {'rows': result['rows']})
    assert compat.comparison_bytes({}, dict(result, code_hash='X')) == compat.comparison_bytes({}, dict(result, code_hash='Y'))
    assert compat.comparison_bytes({}, {'cell_counts': {2: 1, 10: 3}}) == compat.comparison_bytes({}, {'cell_counts': {'2': 1, '10': 3}})
    changed = deepcopy(result)
    changed['rows']['science'][0] += .01
    assert compat.comparison_bytes({}, result) != compat.comparison_bytes({}, changed)


@pytest.mark.parametrize('mismatch', [False, True])
def test_builder_reexecutes_real_execute_path_once_in_parallel(tmp_path, mismatch):
    before = a.source_manifest()
    before['v3/artifacts.py'] = '0' * 64
    old = a.digest(before)
    jobs = [a.stable_job('fixture', {'phase': 'toy', 'seconds': .01,
                                    'kernel': {'capability': c}, 'setting_name': s}, 'validation', i)
            for c in (1., 5.) for s in ('primary', 'double_length') for i in range(3)]
    spec = dict(code_hash=old, instrument=tables.NOMINAL.declaration(), jobs=jobs)
    root = tmp_path / 'old_root'
    spec_path = tmp_path / 'old_spec.json'
    a.atomic_json(spec_path, a.seal(spec))
    a.atomic_json(root / 'identity.json', {'spec_hash': a.digest(spec), 'code_hash': old})
    a.atomic_json(root / 'manifest.json', a.seal(spec))
    a.atomic_json(root / 'launches.json', [{'complete': True}])
    for job in jobs:
        output = root / 'toy/outputs' / (job['id'] + '.json')
        a.atomic_json(output, dict(job=job, code_hash=old, result={'seed': job['seed'] + int(mismatch), 'fixture': True}))
        a.atomic_json(root / 'toy/records' / (job['id'] + '.json'),
                      dict(job=job, code_hash=old, status='complete', output_hash=a.file_hash(output)))
    reasons = tmp_path / 'reasons.json'
    a.atomic_json(reasons, dict(producing_source_manifest=before, reasons={'v3/artifacts.py': 'Toy identity change.'}))
    target = tmp_path / 'proof.json'
    record = compat.build_record([dict(spec=str(spec_path), root=str(root))], reasons, target, workers=2)
    assert record['passed'] is (not mismatch)
    assert len(record['proofs']) == 8 and record['execution']['workers'] == 2
    assert record['operator_approval'] is None
    assert a.unseal(a.read(target.with_suffix('.attempt.json')))['selected_job_ids'] == [p['job_id'] for p in record['proofs']]
    with pytest.raises(ValueError, match='final'):
        compat.build_record([dict(spec=str(spec_path), root=str(root))], reasons, target, workers=2)
    if mismatch:
        with pytest.raises(ValueError, match='failed'):
            compat.approve_record(target, 'fixture', '2026-10-08')
    else:
        assert compat.approve_record(target, 'fixture', '2026-10-08')['operator_approval']['approved']


@pytest.mark.parametrize('wall', [None, 0, -1, float('inf'), float('nan'), True, '257.66'])
def test_registered_a10_labels_refuse_missing_or_bad_ceiling(wall):
    from v3.table_labels_a5 import prepare
    with pytest.raises(ValueError, match='positive finite'):
        prepare(*(['absent'] * 6), registration={'fixture': True}, wall_hours=wall, instrument=tables.NOMINAL)


def test_a10_explicit_ceiling_and_r4_call_shape(monkeypatch):
    from v3 import table_labels_a5 as labels
    class BoundaryReached(Exception):
        pass
    calls = []
    def boundary(path, **kwargs):
        calls.append((path, kwargs))
        raise BoundaryReached
    monkeypatch.setattr(labels, 'require_committed_identity', boundary)
    for inst, kwargs in ((tables.NOMINAL, {'a10': True}), (None, {})):
        with pytest.raises(BoundaryReached):
            labels.prepare(*(['absent'] * 6), registration={'fixture': True},
                           **({'wall_hours': 257.66, 'instrument': inst} if inst else {}))
        assert calls[-1] == ('absent', kwargs)
    with pytest.raises(ValueError, match='24-hour'):
        labels.prepare(*(['absent'] * 6), registration={'fixture': True}, wall_hours=257.66)


def test_a10_registration_requires_both_amendments(tmp_path, monkeypatch):
    text = b'### Amendment A10, fixture\n'
    path = tmp_path / 'note.md'
    path.write_bytes(text)
    pin = {'commit': 'a' * 40, 'path': 'note.md', 'sha256': hashlib.sha256(text).hexdigest()}
    monkeypatch.setattr(a.subprocess, 'run', lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, stdout=text if 'show' in cmd else b''))
    with pytest.raises(RuntimeError, match='Amendment A11'):
        a.verify_registration(pin, tmp_path, instrument=tables.NOMINAL)
    text += b'### Amendment A11, fixture\n'
    path.write_bytes(text)
    pin['sha256'] = hashlib.sha256(text).hexdigest()
    assert a.verify_registration(pin, tmp_path, instrument=tables.NOMINAL) == pin


def test_registered_publish_uses_its_own_ceiling(tmp_path, monkeypatch):
    from v3 import table_labels_a5 as labels, calibration
    class PassedCeiling(Exception):
        pass
    monkeypatch.setattr(labels, 'verify_registration', lambda *args, **kw: None)
    monkeypatch.setattr(labels, '_recompute_plan_hash', lambda p: 'fixture')
    def reached(*args, **kw):
        raise PassedCeiling
    monkeypatch.setattr(calibration, 'validate_calibration', reached)
    a4_path = tmp_path / 'a4.json'
    a.atomic_json(a4_path, a.seal({'jobs': []}))
    plan = dict(registered=True, registration={'fixture': True}, instrument=tables.NOMINAL.declaration(),
                code_hash=a.code_identity(), plan_hash='fixture', wall_seconds=257.66 * 3600,
                declared_wall_hours=257.66, jobs=[], a4_plan_path=str(a4_path))
    with pytest.raises(PassedCeiling):
        labels.publish(plan, tmp_path, tmp_path, tmp_path, {}, tmp_path / 'out', registered=True)
    with pytest.raises(ValueError, match='ceiling mismatch'):
        labels.publish(dict(plan, wall_seconds=24 * 3600), tmp_path, tmp_path, tmp_path, {}, tmp_path / 'out', registered=True)
    with pytest.raises(ValueError, match='24-hour'):
        labels.publish(dict(plan, instrument={'mapping': 'R4'}), tmp_path, tmp_path, tmp_path, {}, tmp_path / 'out', registered=True)


@pytest.mark.parametrize('producer', ['a4', 'a5'])
def test_stage_output_read_admits_approved_identity_but_r4_remains_strict(tmp_path, monkeypatch, producer):
    from v3 import table_validation_a4, table_labels_a5
    module = table_validation_a4 if producer == 'a4' else table_labels_a5
    old, current = 'a' * 64, a.code_identity()
    monkeypatch.setattr(compat, 'accepted_identities', lambda: {old, current})
    job = a.stable_job('fixture', dict(phase='toy', a1_job={'id': 'source'}, seed=42), 'validation', 0)
    result = dict(a1_job_id='source', stream_seed=42, plan_hash='plan', code_hash=old)
    path = tmp_path / 'toy/outputs' / (job['id'] + '.json')
    a.atomic_json(path, dict(job=job, code_hash=old, result=result))
    a.atomic_json(tmp_path / 'toy/records' / (job['id'] + '.json'),
                  dict(job=job, code_hash=old, status='complete', output_hash=a.file_hash(path)))
    plan = dict(instrument=tables.NOMINAL.declaration(), code_hash=old, jobs=[job], plan_hash='plan')
    hashes, seeds = module._verify_stage_outputs(plan, tmp_path)
    assert hashes == {job['id']: a.file_hash(path)} and seeds == {job['id']: 42}
    with pytest.raises(RuntimeError, match='identity mismatch'):
        module._verify_stage_outputs(dict(plan, instrument={'mapping': 'R4'}), tmp_path)
    from v3.production_runner import validate_spec
    with pytest.raises(RuntimeError, match='frozen specification source hash mismatch'):
        validate_spec(plan, {})


def test_completed_family_receipt_and_a5_identity_accept_only_approved_producer(tmp_path, monkeypatch):
    from v3 import production_tables as pt, table_labels_a5 as labels
    from v3.instrument import CONSTANTS_SHA256
    old, current = 'a' * 64, a.code_identity()
    row = dict(rule_id='balanced', kernel_hash='toy', calibration_hash='toy',
               scoring=dict(alpha=1., capability=1.5, kappa=8., **tables.NOMINAL.declaration()),
               route='plain', status='estimated', lambda_f={'mean': 0.}, flow_range=100.,
               continuation={'entries': []}, c0={'value': 0., 'error': 100.})
    manifest = dict(tag='v3_tables', calibration_hash='toy', complete_family=True,
                    sensitivity_status='passed', required_row_keys=[pt.row_key(row)],
                    a10=dict(family='nominal', producer_code_hash=old, constants_sha256=CONSTANTS_SHA256,
                             instruments=[tables.NOMINAL.declaration()]))
    family = tmp_path / 'family.json'
    with monkeypatch.context() as patch:
        patch.setattr(pt, 'code_identity', lambda: old)
        document = pt.write_tables(family, [row], manifest, fixture=False)
    sidecar_path = family.with_suffix('.cell_results.json')
    a.atomic_json(sidecar_path, a.seal(dict(table_seal_sha256=document['sha256'])))
    receipt = dict(schema='v3-A4-receipt-1', producer_code_hash=old, table_seal_sha256=document['sha256'],
                   table_file_sha256=a.file_hash(family), cell_results_sha256=a.file_hash(sidecar_path))
    a.atomic_json(family.with_suffix('.compatibility.json'), a.seal(receipt))
    label_path = tmp_path / 'labels.json'
    a.atomic_json(label_path, a.seal(dict(schema='v3-A5-label-1', code_hash=old, rows=[],
                  a4_family=dict(table_seal_sha256=document['sha256'], family_file_sha256=a.file_hash(family)))))
    identity = dict(family_file_sha256=a.file_hash(family), table_seal_sha256=document['sha256'],
                    receipt_file_sha256=a.file_hash(family.with_suffix('.compatibility.json')),
                    sidecar_file_sha256=a.file_hash(sidecar_path), producing_commit='toy', code_hash=old)
    monkeypatch.setattr(compat, 'accepted_identities', lambda: {old, current})
    with monkeypatch.context() as patch:
        patch.setattr(tables, 'code_identity', lambda: old)
        frozen_receipt = tables.finalize_receipt(family, label_path)
    assert tables.finalize_receipt(family, label_path) == frozen_receipt
    table = pt.ProductionTables(family, calibration_hash='toy', registered=True)
    table.require_a10(tables.NOMINAL)
    assert labels.load_a4_publication(family, identity)[0]['code_hash'] == old
    monkeypatch.setattr(compat, 'accepted_identities', lambda: {current})
    with pytest.raises(ValueError, match='producer'):
        table.require_a10(tables.NOMINAL)
    with pytest.raises(ValueError, match='not accepted'):
        labels.load_a4_publication(family, identity)
    with pytest.raises(ValueError, match='stale table'):
        pt.ProductionTables(family, calibration_hash='toy', registered=True)


def test_registered_index_accepts_completed_old_root_without_resuming_it(tmp_path, monkeypatch):
    from v3 import gates
    old, current = 'a' * 64, a.code_identity()
    monkeypatch.setattr(compat, 'accepted_identities', lambda: {old, current})
    monkeypatch.setattr(a, 'verify_registration', lambda *args, **kwargs: None)
    monkeypatch.setattr(gates, 'ROOT', tmp_path)
    cal = tmp_path / 'cal.json'
    a.atomic_json(cal, a.seal({'toy': True}))
    job = a.stable_job('rerun', dict(phase='rerun', calibration_path=str(cal)), 'v3_rerun', 0)
    root = tmp_path / 'old'
    a.atomic_json(root / 'manifest.json', a.seal(dict(registered=True, code_hash=old, jobs=[job])))
    output = root / 'rerun/outputs' / (job['id'] + '.json')
    a.atomic_json(output, dict(job=job, code_hash=old, result={'toy': True}))
    a.atomic_json(root / 'rerun/records' / (job['id'] + '.json'),
                  dict(status='complete', code_hash=old, job=job, output_hash=a.file_hash(output)))
    target = tmp_path / 'runs/index.json'
    assert gates.build_index(root, target, pin={'commit': 'toy'}, instrument=tables.NOMINAL)['runs'] == 1
    assert a.read(target)['instrument_code_hash'] == old
    monkeypatch.setattr(compat, 'accepted_identities', lambda: {current})
    with pytest.raises(ValueError, match='mode/source mismatch'):
        gates.build_index(root, target, pin={'commit': 'toy'}, instrument=tables.NOMINAL)


CEILINGS = dict(main=50.49, k1p5=10.94, k2p3=10.93, weight_corner=44.34, horizon=10.27)


def test_stage1_exact_complete_disjoint_job_sets(monkeypatch):
    from v3.sensitivity_a6 import build_weight_corner_jobs, build_horizon_jobs
    monkeypatch.setattr(a, 'verify_registration', lambda pin, **kwargs: pin)
    specs = tables.stage1_run_specs('cal', 'table', {'fixture': True}, CEILINGS)
    expected = {'main': tables.paired_runs('cal', 'table'),
                'weight_corner': tables.correct_runs(build_weight_corner_jobs('cal', 'table')),
                'horizon': tables.correct_runs(build_horizon_jobs('cal', 'table'))}
    for name, k in (('k1p5', 1.5), ('k2p3', 2.3)):
        expected[name] = [j for j in tables.arm_runs('cal', 'table', 'sqrt')
                          if j['config']['model']['instrument'] == dict(mapping='A10', k_star=k, g='linear')]
    assert {n: len(s['jobs']) for n, s in specs.items()} == dict(main=24900, k1p5=4400, k2p3=4400, weight_corner=17600, horizon=1800)
    assert specs['main']['wall_seconds'] == 181764
    all_jobs = [j for spec in specs.values() for j in spec['jobs']]
    assert len({j['id'] for j in all_jobs}) == len({j['seed'] for j in all_jobs}) == 53100
    for name, spec in specs.items():
        assert spec['jobs'] == expected[name]
        assert spec['registered'] and spec['registered_a10']
        assert all(j['config']['steps'] == (1000 if name == 'horizon' else 500) for j in spec['jobs'])
        assert all(j['config']['model']['instrument']['g'] == 'linear' for j in spec['jobs'])
        assert a.unseal(a.seal(spec)) == spec
    from collections import Counter
    assert Counter(j['config']['category'] for j in specs['main']['jobs']) == dict(R1=10800, refinement=3600, R2=10500)
    # Run the real registered gate loader over synthetic absorbed records.
    # Only the filesystem reader is replaced. All 24,900 job-set, identity,
    # category, counterpart pairing and horizon checks execute unchanged.
    from v3 import gates
    spec = specs['main']
    code = a.code_identity()
    old = 'e' * 64
    spec = dict(spec, code_hash=old)
    refs = [{'output': {'path': 'out:' + j['id'], 'sha256': j['id']},
             'completion': {'path': 'done:' + j['id'], 'sha256': j['id']}} for j in spec['jobs']]
    manifest = dict(schema='v3-gate-evidence-2', fixture=False, instrument_code_hash=old,
                    calibration={'path': 'cal', 'sha256': 'calhash'}, tables=[],
                    rerun_manifest={'path': 'spec'}, runs=refs)
    jobs = {j['id']: j for j in spec['jobs']}
    diagnostics = [dict(time=t, population_before=0, population=0) for t in range(500)]
    def reader(ref, base):
        path = ref['path']
        if path == 'cal':
            return a.seal({'fixture': True})
        if path == 'spec':
            return a.seal(spec)
        if path.startswith('out:'):
            job = jobs[path[4:]]
            return dict(job=job, code_hash=old, result=dict(fixture_tables=False, steps=500,
                        diagnostics=diagnostics, yield_events=[]))
        if path.startswith('done:'):
            job = jobs[path[5:]]
            return dict(job=job, code_hash=old, status='complete', output_hash=job['id'])
        return manifest
    monkeypatch.setattr(gates, 'verified_json', reader)
    monkeypatch.setattr(compat, 'accepted_identities', lambda: {old, code})
    runs, checked = gates.load_runs('synthetic-index.json', 'fixturehash', expected_code_hash=code,
                                    calibration_sha256='calhash', instrument=tables.NOMINAL)
    assert len(runs) == checked['verified_runs'] == 24900
    monkeypatch.setattr(compat, 'accepted_identities', lambda: {code})
    with pytest.raises(ValueError, match='committed instrument'):
        gates.load_runs('synthetic-index.json', 'fixturehash', expected_code_hash=code,
                        calibration_sha256='calhash', instrument=tables.NOMINAL)


@pytest.mark.parametrize('ceilings', [{}, dict(CEILINGS, main=None), dict(CEILINGS, main=0),
                                      dict(CEILINGS, main=float('inf')), dict(CEILINGS, extra=1)])
def test_stage1_requires_every_positive_finite_ceiling(ceilings):
    with pytest.raises(ValueError):
        tables.stage1_run_specs('cal', 'table', {}, ceilings)


def test_toy_pipeline_through_a5_with_non24_hour_ceiling(tmp_path):
    from v3 import production_runner as runner, table_validation_a4 as a4, table_labels_a5 as a5
    cal_path = 'v3/runs/registered/v3_rerun_calibration.json'
    calibration = a.read(a.SIMULATION / cal_path)
    toy = dict(groups=3, runs_per_group=2, particles=2, burn=30, measure=8)
    settings = dict(profile='local', workers=2, threads=1, cpu_budget=16, mode='work', caps=runner.caps('local', 16))
    code = a.code_identity()
    def dispatch(root, jobs):
        if not jobs:
            return
        a.atomic_json(root / 'control.json', dict(mode='work', max_workers=2, stop_dispatch=False, interrupt_now=False))
        status = runner.dispatch(root, jobs, code, settings, time.time() + 300, fixed={'workers': 2, 'threads': 1})
        assert status['completed'] == len(jobs)
    source = tmp_path / 'source'
    jobs = tables.build_jobs('sqrt', cal_path, settings_override=toy,
                            kernel_override={'n_agents': 16, 'carrying_capacity': 160},
                            rule_ids=['balanced'], physical_contexts=[(.064, 1.), (.064, 1.5)])
    jobs = [a.stable_job(j['kind'], dict(j['config'], route='fv' if j['config']['kernel']['capability'] == 1.5 else 'plain'),
                         j['tag'], j['index']) for j in jobs]
    dispatch(source / 'tables_A1/table', jobs)
    outputs = [runner.completed(source / 'tables_A1/table', j, code) for j in jobs]
    a.atomic_json(source / 'tables_A1_manifest.json', a.seal(dict(jobs=jobs, code_hash=code,
                  source_family={'code_hash': code}, tag='pilot', registered=False)))
    tables.assemble(outputs, calibration, source / 'v3_rerun_tables_A1.json', 'sqrt', jobs=jobs)
    probe = tmp_path / 'probe'
    a.atomic_json(probe / 'seeds.json', {'non_registered': True, 'seed': 76347036432783642})
    plan = tables.prepare_validation(source, cal_path, probe_root=probe, settings_override=dict(toy, census_measure=38))
    plan_path, run = tmp_path / 'a4_plan.json', tmp_path / 'a4'
    a.atomic_json(plan_path, a.seal(plan))
    for phase in plan['phases']:
        dispatch(run / phase, [j for j in plan['jobs'] if j['config']['phase'] == phase])
    family = tmp_path / 'family.json'
    a4.publish(plan, run, source, calibration, family, registered=False)
    before = a.file_hash(family)
    document = a.read(family)
    identity = dict(family_file_sha256=before, table_seal_sha256=document['sha256'],
                    receipt_file_sha256=a.file_hash(family.with_suffix('.compatibility.json')),
                    sidecar_file_sha256=a.file_hash(family.with_suffix('.cell_results.json')),
                    producing_commit='nonregistered-toy', code_hash=code)
    identity_path = tmp_path / 'identity.json'
    a.atomic_json(identity_path, identity)
    labels_plan = a5.prepare(family, run, plan_path, source, cal_path, identity_path,
                            wall_hours=1.25, a3_probe_root=probe, settings_override=toy,
                            instrument=tables.family_instrument('sqrt'))
    assert labels_plan['wall_seconds'] == 4500 and labels_plan['declared_wall_hours'] == 1.25
    labels_root, labels_path = tmp_path / 'a5', tmp_path / 'labels.json'
    for phase in labels_plan['phases']:
        dispatch(labels_root / phase, [j for j in labels_plan['jobs'] if j['config']['phase'] == phase])
    a5.publish(labels_plan, labels_root, run, source, calibration, labels_path, registered=False)
    receipt = tables.finalize_receipt(family, labels_path)
    assert a.file_hash(family) == before
    assert a.unseal(receipt)['table_sha256'] == document['sha256']
    assert a.unseal(document)['fixture'] is True
    assert tables.finalize_receipt(family, labels_path) == receipt
    a.atomic_json(tmp_path / 'PIPELINE_CHECK.json', dict(passed=True, non_registered=True,
                  source_jobs=len(jobs), validation_jobs=len(plan['jobs']), label_jobs=len(labels_plan['jobs']),
                  declared_label_wall_hours=1.25, code_hash=code))
    # Fabricate an execution-only producing identity for the *same* completed
    # numerical artifacts, then rerun real A4 and A5 sampled jobs, including
    # plain validation's sibling-fit dependency, at the running identity.
    before_manifest = a.source_manifest()
    before_manifest['v3/artifacts.py'] = '0' * 64
    old = a.digest(before_manifest)
    sources = []
    for name, produced, original_root in [('a4', plan, run), ('a5', labels_plan, labels_root)]:
        old_spec = dict(produced, code_hash=old)
        old_root = tmp_path / ('old_' + name)
        spec_path = tmp_path / ('old_' + name + '.json')
        a.atomic_json(spec_path, a.seal(old_spec))
        a.atomic_json(old_root / 'manifest.json', a.seal(old_spec))
        a.atomic_json(old_root / 'identity.json', dict(code_hash=old, spec_hash=a.digest(old_spec)))
        a.atomic_json(old_root / 'launches.json', [{'complete': True}])
        for job in produced['jobs']:
            phase = job['config']['phase']
            value = deepcopy(runner.completed(original_root / phase, job, code))
            value['code_hash'] = value['result']['code_hash'] = old
            path = old_root / phase / 'outputs' / (job['id'] + '.json')
            a.atomic_json(path, value)
            a.atomic_json(old_root / phase / 'records' / (job['id'] + '.json'),
                          dict(status='complete', code_hash=old, job=job, output_hash=a.file_hash(path)))
        sources.append(dict(spec=str(spec_path), root=str(old_root)))
    reasons = tmp_path / 'reasons.json'
    a.atomic_json(reasons, dict(producing_source_manifest=before_manifest,
                                reasons={'v3/artifacts.py': 'Fabricated execution-only identity change.'}))
    proof = compat.build_record(sources, reasons, tmp_path / 'compatibility_proof.json', workers=2)
    assert proof['passed'], [(p['job_id'], p.get('error')) for p in proof['proofs'] if not p['passed']]
    assert any(g['phase'] == 'a5_fvplain' for g in proof['populations'])
