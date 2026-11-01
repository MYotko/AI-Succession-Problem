"""A14 fixtures use only generated records and non-reserved rehearsal streams."""
from copy import deepcopy
import hashlib
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest
from test_v3_paths import tmp_path
from test_v3_a13 import row_fixture, parameters, source_job
from v3 import artifacts as a
from v3 import validation_extension_a13 as old
from v3 import validation_extension_a14 as ext


def forecast_config_file(tmp_path, monkeypatch):
    path = tmp_path / 'forecast_config.json'
    a.atomic_json(path, {})
    from v3 import forecast_a14
    monkeypatch.setattr(forecast_a14, 'validate_configuration', lambda *args, **kw: {})
    return path


def job_fixture():
    source = source_job()
    manifest = ext.seed_manifest([source], 24, [], rehearsal=True)
    config = dict(phase=ext.PHASE, route='plain', a1_job=source, a1_source_root='unused',
        a1_source_code_hash=a.code_identity(), eligible_rows={'a': parameters(8), 'b': parameters(9)},
        M=20, R_max=24, full_seed_manifest=manifest, forbidden_seeds=[],
        stream_seeds=[m['seed'] for m in manifest], trajectory_count=6, plan_hash='toy',
        non_registered_rehearsal=True, fit=a.seal(dict(a1_job_id=source['id'], rows=[])))
    return a.stable_job(ext.KIND, config, 'v3_tables', 0)


def test_a13_and_numerical_modules_unchanged():
    for name in ('validation_extension_a13.py', 'continuation_validation.py', 'offline_estimator.py'):
        before = subprocess.check_output(['git', 'show', '17f17ef9:simulation/v3/' + name])
        assert before.replace(b'\r\n', b'\n') == (a.ROOT / name).read_bytes().replace(b'\r\n', b'\n')


def test_seed_ranges_and_manifest():
    source = source_job()
    m = ext.seed_manifest([source], 32, [])
    assert [x['replicate'] for x in m] == list(range(20, 52))
    assert len({x['seed'] for x in m}) == 32
    assert all(2**61 <= x['seed'] < 2**61 + 2**60 < 2**62 for x in m)
    assert not {x['seed'] for x in m} & {x['seed'] for x in old.seed_manifest([source], 16, [])}
    with pytest.raises(ValueError, match='collision'):
        ext.seed_manifest([source], 32, [m[3]['seed']])
    with pytest.raises(ValueError, match='collision'):
        ext.check_seed_manifest([m[0], m[0]], [])
    assert all(not ext.reserved(x['seed']) for x in ext.seed_manifest([source], 32, [], rehearsal=True))


@pytest.mark.parametrize('replicate', [4, 19, 52, 20.])
def test_replicate_domain(replicate):
    with pytest.raises(ValueError):
        ext.ext2_seed(1, replicate)


def test_pricing_keeps_a13_bound_and_reuses_payload_check():
    j = source_job()
    projection = a.seal({'per_phase_capability': {'nominal.1.0.primary.validate_plain':
        {'jobs': 10, 'x2_hours_max': 3.}}})
    original = {'pull_dispatch': {'projection_sha256': projection['sha256']}}
    price = ext.price_round(original, projection, [j], registered=False, projection_file_hash=None)
    assert price['R_max'] == 32
    assert old.price_extension(original, projection, [j], registered=False)['R_max'] == 16
    with pytest.raises(ValueError, match='payload seal'):
        ext.price_round({'pull_dispatch': {'projection_sha256': 'bad'}}, projection, [j],
                        registered=False, projection_file_hash=None)


def test_test_uses_only_round2_pairs():
    p = parameters(8)
    data = [dict(replicate=20, trajectories=[[0., 1]] * 7)]
    assert ext.extension_test(data, p)['reason'] == 'N* not reached'
    data.append(dict(replicate=21, trajectories=[[0., 1]] * 7))
    expected = old.extension_test([dict(r, replicate=r['replicate'] - 16) for r in data], p)
    assert ext.extension_test(data, p) == expected
    with pytest.raises(ValueError, match='order'):
        ext.extension_test([dict(data[0], replicate=4)], p)


def test_stop_checkpoint_resume_from_twenty(tmp_path, monkeypatch):
    from v3.production_runner import execute
    job, calls = job_fixture(), []
    monkeypatch.setattr(old.a4, '_load_a1', lambda *args: {})
    def stage(source, fit, rows, seed, override):
        calls.append(seed)
        if len(calls) == 2:
            raise OSError('synthetic interruption')
        return dict(count=6, rows={k: [[0., 1]] * 6 for k in rows})
    monkeypatch.setattr(ext, 'extension_stage', stage)
    with pytest.raises(OSError):
        execute(job, root=tmp_path / ext.PHASE)
    assert len(ext.durable_checkpoints(tmp_path, job)) == 1
    result = execute(job, root=tmp_path / ext.PHASE)
    assert result['stopped_on_visits'] and [r['replicate'] for r in result['replicates']] == [20, 21]
    assert calls == [job['config']['stream_seeds'][0], job['config']['stream_seeds'][1], job['config']['stream_seeds'][1]]
    assert execute(job, root=tmp_path / ext.PHASE) == result
    changed = deepcopy(result['replicates'])
    changed[1]['replicate'] = 22
    with pytest.raises(ValueError, match='seed/order'):
        ext.validate_replicates(job, changed)


def test_unregistered_neither_flag_and_reserved_seed_refused(tmp_path):
    from v3.production_runner import execute
    job = job_fixture()
    job['config']['non_registered_rehearsal'] = False
    with pytest.raises(ValueError, match='requires rehearsal'):
        execute(job, root=tmp_path)
    job['config']['non_registered_rehearsal'] = True
    job['config']['stream_seeds'][0] = 2**61
    with pytest.raises(ValueError, match='reserved'):
        execute(job, root=tmp_path)


def test_history_verifier_failure_is_read_only(tmp_path):
    from v3.history_a14 import verify_history
    copy = tmp_path / 'copies' / 'plan.json'
    a.atomic_json(copy, {})
    document = a.seal(dict(schema='v3-A14-history-1', files=[
        dict(source=str(tmp_path / 'original' / 'plan.json'), copy=str(copy), sha256='wrong', bytes=copy.stat().st_size)],
        directories={}, roles={}))
    before = {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    with pytest.raises(ValueError, match='copy changed'):
        verify_history(document, registered=False)
    assert before == {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}


def test_reservation_before_check_and_different_output_refused(tmp_path, monkeypatch):
    history = a.seal(dict(a13_plan_hash='toy'))
    path = ext.reserve_preparation(tmp_path / 'plan.json', history, registered=False)
    assert a.unseal(a.read(path))['state'] == 'preparing'
    assert ext.reserve_preparation(tmp_path / 'plan.json', history, registered=False, resume=True) == path
    with pytest.raises(ValueError, match='reserved'):
        ext.reserve_preparation(tmp_path / 'plan.json', history, registered=False)
    ext.preparation_failure(path, 'synthetic terminal check')
    with pytest.raises(ValueError, match='terminal'):
        ext.reserve_preparation(tmp_path / 'plan.json', history, registered=False, resume=True)
    # The registered anchor is shared, even when output paths differ. Redirect
    # its exact family target to a synthetic path; no registered root is used.
    monkeypatch.setattr(ext, 'TARGET', (tmp_path / 'family.json').relative_to(a.SIMULATION).as_posix())
    ext.reserve_preparation(tmp_path / 'registered_1.json', history, registered=True)
    with pytest.raises(ValueError, match='reserved'):
        ext.reserve_preparation(tmp_path / 'registered_2.json', history, registered=True)
    assert ext.reserve_preparation(tmp_path / 'rehearsal.json', history, registered=False)


@pytest.mark.parametrize('fault', ['both_flags', 'neither_flag', 'stale_output', 'bad_pin',
    *['missing_' + name for name in ('history', 'projection', 'seeds', 'forecast')],
    *['directory_' + name for name in ('history', 'projection', 'seeds', 'forecast')]])
def test_invocation_errors_create_no_record_or_evidence_read(tmp_path, monkeypatch, fault):
    inputs = {name: tmp_path / (name + '.json') for name in ('history', 'projection', 'seeds', 'forecast')}
    for name, path in inputs.items():
        if fault == 'missing_' + name:
            continue
        if fault == 'directory_' + name:
            path.mkdir()
        else:
            path.write_text('{', encoding='utf-8')  # Deliberately unparsable evidence.
    output = tmp_path / 'plan.json'
    if fault == 'stale_output':
        output.write_bytes(b'unchanged stale output')
    monkeypatch.setattr(ext, 'TARGET', (tmp_path / 'family.json').relative_to(a.SIMULATION).as_posix())
    pin = {} if fault == 'bad_pin' else {'synthetic': True}
    if fault != 'bad_pin':
        monkeypatch.setattr(a, 'verify_registration', lambda *args, **kw: None)
    monkeypatch.setattr(ext, 'read', lambda *args: pytest.fail('invocation read evidence'))
    before = {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    with pytest.raises((ValueError, RuntimeError)):
        ext.prepare(*inputs.values(), output,
                    registration=None if fault == 'neither_flag' else pin,
                    rehearsal=fault == 'both_flags')
    assert before == {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    assert not output.with_suffix('.round.json').exists()
    assert not (tmp_path / 'family.a14_round.json').exists()


@pytest.mark.parametrize('fault', ['no_anchor_absent', 'no_anchor_present', 'prepared', 'refused',
    'halted', 'halt', 'request', 'output_directory', 'unbound_output', 'bound_hash',
    'self_hash', 'seal', 'schema', 'no_resume'])
def test_invalid_resume_is_read_only_and_never_reads_evidence(tmp_path, monkeypatch, fault):
    inputs = [tmp_path / (name + '.json') for name in ('history', 'projection', 'seeds', 'forecast')]
    for path in inputs:
        path.write_text('{', encoding='utf-8')
    output = tmp_path / 'plan.json'
    reference = dict(history_path=str(inputs[0].resolve()))
    anchor = output.with_suffix('.round.json')
    if not fault.startswith('no_anchor'):
        ext.reserve_preparation(output, reference, registered=False)
        record = a.unseal(a.read(anchor))
        if fault in ('prepared', 'refused', 'halted'):
            record['state'] = fault
        elif fault == 'halt':
            record['halt'] = {'reason': 'synthetic halt'}
        elif fault == 'request':
            record['request']['output'] = str(tmp_path / 'different.json')
        elif fault == 'schema':
            record['schema'] = 'not-an-A14-anchor'
        a.atomic_json(anchor, a.seal(record))
    if fault == 'output_directory':
        output.mkdir()
    if fault in ('no_anchor_present', 'unbound_output', 'bound_hash', 'self_hash', 'seal'):
        plan = {'schema': ext.SCHEMA, 'round': 2}
        plan['plan_hash'] = ext.plan_hash(plan)
        if anchor.exists() and fault != 'unbound_output':
            record['plan_hash'] = 'different' if fault == 'bound_hash' else plan['plan_hash']
            a.atomic_json(anchor, a.seal(record))
        if fault == 'self_hash':
            plan['round'] = 3
        document = a.seal(plan)
        if fault == 'seal':
            document['sha256'] = 'changed'
        a.atomic_json(output, document)
    actual_read = ext.read
    def metadata_only(path):
        assert Path(path) in (anchor, output), 'resume read historical evidence'
        return actual_read(path)
    monkeypatch.setattr(ext, 'read', metadata_only)
    before = {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    with pytest.raises(ValueError):
        ext.prepare(*inputs, output, rehearsal=True, resume=fault != 'no_resume')
    assert before == {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}


@pytest.mark.parametrize('when', ['before_history', 'after_output'])
@pytest.mark.parametrize('error', [OSError, MemoryError])
def test_preparing_resume_with_absent_or_consistent_output(tmp_path, monkeypatch, when, error):
    from v3 import forecast_a14
    history, history_path, projection, seeds, args, old_plan = history_fixture(tmp_path, monkeypatch)
    forecast_path = forecast_config_file(tmp_path, monkeypatch)
    output = tmp_path / 'plan.json'
    anchor = output.with_suffix('.round.json')
    old_records = {str(p): p.read_bytes() for p in (Path(old_plan['round_record_path']),
                   Path(old_plan['round_record_path']).with_suffix('.admission.json'))}
    monkeypatch.setattr(forecast_a14, 'forecast', lambda *args, **kw:
                        {'p_all_part2': .8, 'p_all_part2_certification_0_9': .7})
    actual_read, actual_write = ext.read, ext.atomic_json
    def interrupted_read(path):
        if when == 'before_history' and Path(path) == history_path:
            assert anchor.exists() and not output.exists()
            raise error('synthetic interruption before history')
        return actual_read(path)
    def interrupted_write(path, value):
        if when == 'after_output' and Path(path) == output.with_suffix('.public.json'):
            assert output.exists()
            raise error('synthetic interruption after output')
        return actual_write(path, value)
    with monkeypatch.context() as patch:
        patch.setattr(ext, 'read', interrupted_read)
        patch.setattr(ext, 'atomic_json', interrupted_write)
        with pytest.raises(error, match='synthetic interruption'):
            ext.prepare(history_path, projection, seeds, forecast_path, output, rehearsal=True)
    record = a.unseal(a.read(anchor))
    assert record['state'] == 'preparing' and record['halt'] is None
    assert output.exists() == (when == 'after_output')
    output_before = output.read_bytes() if output.exists() else None
    def checked_reserve(*args, **kw):
        assert a.unseal(a.read(anchor)) == record
        return reserve(*args, **kw)
    reserve = ext.reserve_preparation
    monkeypatch.setattr(ext, 'reserve_preparation', checked_reserve)
    plan = ext.prepare(history_path, projection, seeds, forecast_path, output, rehearsal=True, resume=True)
    assert a.unseal(a.read(anchor))['state'] == 'prepared'
    assert a.unseal(a.read(output)) == plan
    assert a.unseal(a.read(output.with_suffix('.public.json'))) == ext.public_record(plan)
    if output_before is not None:
        assert output.read_bytes() == output_before
    assert all(Path(path).read_bytes() == data for path, data in old_records.items())


def test_two_round_reassembly_preserves_other_rows_and_violation_reaches_admission(tmp_path):
    from v3.admission_a13 import binding
    rows, details, selected, fits, censuses = {}, [], {}, {}, {}
    for i in range(4):
        row, detail, fit = row_fixture(context=i)
        key = detail['row']
        rows[key], fits[key], censuses[key] = row, fit['c0'], {'1': 9950, '0': 50}
        details.append(detail)
        if i < 3:
            selected[key] = dict(parameters(8), lower=-10., upper=0.)
    keys = list(rows)
    tests = {k: dict(status='certified', n=8, visit_weighted_ok=True) for k in selected}
    tests[keys[1]] = dict(status='unresolved', reason='N* not reached', n=0, visit_weighted_ok=False)
    tests[keys[2]] = deepcopy(tests[keys[1]])
    verified = dict(rows=rows, details=details, selected=selected, fits=fits, censuses=censuses, tests=tests,
                    eligible={k: k in keys[1:3] for k in selected}, classification_sha256='synthetic')
    newer = {keys[1]: dict(status='violation', n=8, visit_weighted_ok=False), keys[2]: tests[keys[2]]}
    after, sidecar, _ = ext.reassemble(verified, newer)
    assert a.canonical(after[keys[3]]) == a.canonical(rows[keys[3]])
    assert a.canonical(sidecar[3]) == a.canonical(details[3])
    assert after[keys[0]]['a13']['round'] == 1
    assert after[keys[1]]['a13']['round'] == 2
    assert after[keys[2]]['a13']['round'] is None
    # Add estimated unrelated rows so the count cap does not hide violation.
    for i in range(4000):
        after['padding' + str(i)] = dict(status='estimated')
    with pytest.raises(ValueError, match='violation'):
        binding(after, sidecar, 'A10_nominal_after_A14')


def test_snapshot_external_input_and_unchanged_internal_layout(tmp_path, monkeypatch):
    from v3 import snapshot_a11 as snapshot
    inside = tmp_path / 'inside.json'
    a.atomic_json(inside, dict(synthetic=True))
    # Make the enumeration root a child of the true authorized write scope,
    # so the synthetic external input never leaves the worktree.
    monkeypatch.setattr(snapshot, 'ROOT', tmp_path / 'checkout')
    monkeypatch.setattr(snapshot, 'dependencies', lambda *args: [inside])
    external = snapshot.inventory([], tmp_path, historical_roots=[str(tmp_path)])
    row = external['payload']['files'][0]
    assert row['aliases'] == [str(inside)] and row['source'] == str(inside)
    view = snapshot.receive(external, tmp_path / 'received',
                            lambda name, offset: snapshot.fetch(external, name, offset))
    with a.input_view(view):
        assert a.read(inside) == {'synthetic': True}
        with pytest.raises(ValueError, match='not in'):
            a.read(inside.with_name('undeclared.json'))
    monkeypatch.setattr(snapshot, 'ROOT', a.ROOT)
    original = snapshot.inventory([], tmp_path)
    assert original['payload']['files'] == [dict(path=inside.relative_to(a.SIMULATION).as_posix(),
                                                sha256=a.file_hash(inside), bytes=inside.stat().st_size)]


def test_forecast_exact_scripts_and_import_guard(tmp_path):
    from v3 import forecast_a14 as f
    assert len(f.SCRIPTS) == 3 and f.COMMIT == '55817036'
    # A forged reachable source is refused before any script or input read.
    a.atomic_json(tmp_path / 'source.json', a.seal(dict(commit=f.COMMIT, files={})))
    (tmp_path / 'validation_extension_a14.py').write_text('raise AssertionError("must not import")')
    with pytest.raises(ValueError, match='reachable'):
        f.verified_source(tmp_path)


def synthetic_calibration(monkeypatch):
    """Synthetic calibration authority, restricted to this exact fixture."""
    from v3 import calibration
    from v3.instrument import EPSILON_L
    document = a.seal(dict(schema='v3-calibration-1', fixture=True, code_hash=a.code_identity(),
        values=dict(center=[0.] * 10, sigma_squared=.02, n_ref=200., epsilon_n=1e-6,
                    epsilon_e=1e-6, epsilon_l=EPSILON_L, c_e=2.5)))
    original = calibration.validate_calibration
    def validate(doc, **kw):
        if doc == document and not kw.get('registered'):
            return original(doc, registered=False)
        return original(doc, **kw)
    monkeypatch.setattr(calibration, 'validate_calibration', validate)
    from v3 import compatibility_a10
    monkeypatch.setattr(compatibility_a10, 'accepted_identities', lambda: {a.code_identity()})
    return document


def history_fixture(tmp_path, monkeypatch):
    import inspect
    import shutil
    import test_v3_a13 as fixtures
    calibration = synthetic_calibration(monkeypatch)
    cal_path = tmp_path / 'calibration' / 'calibration.json'
    a.atomic_json(cal_path, calibration)
    # Reuse the existing toy pipeline with an explicit locally generated
    # calibration. The registered path in its old helper is never opened.
    source = inspect.getsource(fixtures.toy_original).replace(
        "'v3/runs/registered/v3_rerun_calibration.json'", repr(cal_path.relative_to(a.SIMULATION).as_posix())).replace(
        '[execution_policy_class()[2].rule_id]', '[p.rule_id for p in execution_policy_class()[2:4]]')
    namespace = dict(vars(fixtures))
    exec(compile(source, '<synthetic-A14-original>', 'exec'), namespace)
    args = namespace['toy_original'](tmp_path)
    original, original_root, candidate, projection, seeds, source_root, _, probe, settings = args
    plan_path, root = tmp_path / 'a13' / 'plan.json', tmp_path / 'a13' / 'root'
    plan = old.prepare(original, original_root, candidate, projection, seeds, plan_path, rehearsal=True)
    keys = [k for j in plan['jobs'] for k in j['config']['eligible_rows']]
    assert len(keys) >= 2
    def stage(source, fit, rows, seed, override):
        return dict(count=6, settings=settings,
                    rows={k: [[0., 1 if k != keys[-1] else 0]] * 6 for k in rows})
    monkeypatch.setattr(old, 'extension_stage', stage)
    from v3.production_runner import execute
    for job in plan['jobs']:
        result = execute(job, root=root / old.PHASE)
        fixtures.durable(root / old.PHASE, job, result)
        record = root / old.PHASE / 'records' / (job['id'] + '.json')
        a.atomic_json(record, dict(a.read(record), worker_seconds=1.))
    fixtures.round_evidence(plan, root, plan_path=plan_path)
    checked = plan['jobs'][0]
    fixtures.durable(root / ('_nd_' + old.PHASE), checked, result)
    record = root / ('_nd_' + old.PHASE) / 'records' / (checked['id'] + '.json')
    a.atomic_json(record, dict(a.read(record), worker_seconds=1.))
    with pytest.raises(ValueError, match='cap exceeded'):
        old.publish(plan, root, tmp_path / 'refused_a13.json', registered=False)
    directories, files = {}, {}
    for index, original_dir in enumerate((source_root, original_root, root)):
        copy_dir = tmp_path / 'copies' / str(index)
        directories[str(original_dir)] = str(copy_dir)
        for path in original_dir.rglob('*'):
            if path.is_file():
                files[str(path)] = copy_dir / path.relative_to(original_dir)
    loose = [original, plan_path, plan_path.with_suffix('.public.json'), Path(plan['round_record_path']),
             Path(plan['round_record_path']).with_suffix('.admission.json'), cal_path]
    for path in loose:
        files[str(path)] = tmp_path / 'copies' / 'loose' / a.digest(str(path)) / path.name
    inventory = []
    for source, destination in files.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        destination.chmod(0o444)
        inventory.append(dict(source=source, copy=str(destination), sha256=a.file_hash(destination), bytes=destination.stat().st_size))
    history = a.seal(dict(schema='v3-A14-history-1', a13_plan_hash=plan['plan_hash'], files=inventory,
        directories=directories, roles=dict(a13_plan=str(plan_path), a13_public=str(plan_path.with_suffix('.public.json')),
                                           a13_root=str(root))))
    history_path = tmp_path / 'history.json'
    a.atomic_json(history_path, history)
    global_seeds = a.unseal(a.read(seeds))
    global_seeds.update(a13_qualification_seeds=[], a13_configuration_seeds=[])
    a.atomic_json(seeds, a.seal(global_seeds))
    return history, history_path, projection, seeds, args, plan


@pytest.mark.parametrize('outcome', ['certified', 'violation', 'violation_only', 'unreached', 'halt'])
def test_actual_history_two_round_publication_and_a5(tmp_path, monkeypatch, outcome):
    from v3.history_a14 import verify_history
    from v3 import forecast_a14, table_labels_a5 as labels, tables_a10
    from test_v3_a13 import durable
    history, history_path, projection, seeds, args, old_plan = history_fixture(tmp_path, monkeypatch)
    verified = verify_history(history, registered=False)
    if outcome == 'violation_only':
        # Add unavailable-independent, certified toy rows so the cap admits one
        # residual row; the actual round-2 numerical violation must then refuse.
        from v3 import history_a14
        template = deepcopy(next(iter(verified['rows'].values())))
        template['status'] = 'estimable'
        while len(verified['rows']) < 1000:
            key = 'synthetic_padding_' + str(len(verified['rows']))
            verified['rows'][key] = deepcopy(template)
            verified['details'].append(dict(row=key, setting='primary', cell_tests=[]))
        monkeypatch.setattr(history_a14, 'verify_history', lambda *args, **kw: verified)
    assert sum(verified['eligible'].values()) == 1
    assert sum(t.get('reason') != 'N* not reached' for t in verified['tests'].values()) == len(verified['tests']) - 1
    monkeypatch.setattr(forecast_a14, 'forecast', lambda *args, **kw: {'p_all_part2': .8, 'p_all_part2_certification_0_9': .7})
    path, root = tmp_path / 'a14_plan.json', tmp_path / 'a14_root'
    plan = ext.prepare(history_path, projection, seeds, forecast_config_file(tmp_path, monkeypatch), path, rehearsal=True)
    ext.begin_round(plan, path, root)
    a.atomic_json(root / 'identity.json', dict(code_hash=plan['code_hash'], spec_hash=a.digest(plan)))
    a.atomic_json(root / 'launches.json', [dict(complete=True)])
    a.atomic_json(root / ext.PHASE / 'nondeterminism_check.json', dict(checked=plan['jobs'][0]['id'], matched=True))
    def stage(source, fit, rows, seed, override):
        return dict(count=6, rows={k: [[3 * p['tau'] if outcome in ('violation', 'violation_only') else 0.,
                                      int(outcome != 'unreached')]] * 6 for k, p in rows.items()})
    monkeypatch.setattr(ext, 'extension_stage', stage)
    from v3.production_runner import execute
    for job in plan['jobs']:
        durable(root / ext.PHASE, job, execute(job, root=root / ext.PHASE))
    target = tmp_path / 'amended.json'
    old_records = {str(p): a.file_hash(p) for p in (Path(old_plan['round_record_path']),
                    Path(old_plan['round_record_path']).with_suffix('.admission.json'))}
    if outcome == 'halt':
        ext.latch_round_halt(root, 'synthetic scientific halt')
        monkeypatch.setattr(ext, 'extension_test', lambda *args: pytest.fail('halted data were tested'))
        with pytest.raises(ValueError, match='certifies nothing'):
            ext.publish(plan, root, target, registered=False)
        assert not target.exists()
        assert all(a.file_hash(p) == sha for p, sha in old_records.items())
        return
    if outcome in ('violation', 'violation_only', 'unreached'):
        with pytest.raises(ValueError, match='violation' if outcome == 'violation_only' else 'cap exceeded'):
            ext.publish(plan, root, target, registered=False)
        record = ext.round_record_path(plan).with_suffix('.admission.json')
        before = record.read_bytes()
        refusal = a.unseal(a.read(record))
        assert refusal['outcome'] == 'refused'
        if outcome == 'violation_only':
            assert refusal['residual_count'] == refusal['cap'] == 1
        with pytest.raises(ValueError):
            ext.publish(plan, root, target, registered=False)
        assert record.read_bytes() == before and not target.exists()
        assert all(a.file_hash(p) == sha for p, sha in old_records.items())
        return
    document, receipt = ext.publish(plan, root, target, registered=False)
    assert receipt['plan_hash'] == verified['receipt']['plan_hash']
    assert receipt['stream_seeds'] == verified['receipt']['stream_seeds']
    assert receipt['extension_seed_manifest'] == old_plan['seed_manifest'] + plan['seed_manifest']
    assert set(receipt) >= {'a13_round', 'a14_round', 'refusals'}
    assert {a.unseal(v)['a13']['round'] for v in document['payload']['rows'].values() if 'a13' in a.unseal(v)} == {1, 2}
    assert all(a.file_hash(p) == sha for p, sha in old_records.items())
    with pytest.raises(ValueError, match='root/plan'):
        ext.publish(plan, tmp_path / 'wrong_root', tmp_path / 'wrong.json', registered=False)
    identity_path = tmp_path / 'identity.json'
    a.atomic_json(identity_path, dict(family_file_sha256=a.file_hash(target), table_seal_sha256=document['sha256'],
        receipt_file_sha256=a.file_hash(target.with_suffix('.compatibility.json')),
        sidecar_file_sha256=a.file_hash(target.with_suffix('.cell_results.json')),
        producing_commit='toy', code_hash=a.code_identity()))
    original, original_root, candidate, projection, seeds, source_root, cal_path, probe, settings = args
    label_plan = labels.prepare(target, original_root, original, source_root, cal_path, identity_path,
        wall_hours=1., a3_probe_root=probe, settings_override=settings, instrument=tables_a10.NOMINAL)
    assert label_plan['jobs']
    assert not {j['config']['seed'] for j in label_plan['jobs']} & {m['seed'] for m in receipt['extension_seed_manifest']}


def test_preliminary_reservation_precedes_malformed_inventory(tmp_path, monkeypatch):
    history = tmp_path / 'bad.json'
    history.write_text('{', encoding='utf-8')
    output = tmp_path / 'plan.json'
    inputs = [tmp_path / name for name in ('projection.json', 'seeds.json', 'forecast.json')]
    a.atomic_json(inputs[0], a.seal({}))
    a.atomic_json(inputs[1], a.seal({k: [] for k in seed_categories()}))
    inputs[2] = forecast_config_file(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        ext.prepare(history, *inputs, output, rehearsal=True)
    record = a.unseal(a.read(output.with_suffix('.round.json')))
    assert record['state'] == 'refused' and record['halt'] and record['plan_hash'] is None


@pytest.mark.parametrize('fault', ['admission', 'constants', 'floor', 'skeleton'])
def test_preparation_findings_are_terminal_and_do_not_write_a13(tmp_path, monkeypatch, fault):
    from v3.history_a14 import verify_history
    history, history_path, projection, seeds, args, old_plan = history_fixture(tmp_path, monkeypatch)
    old_records = {str(p): a.file_hash(p) for p in (Path(old_plan['round_record_path']),
                    Path(old_plan['round_record_path']).with_suffix('.admission.json'))}
    if fault in ('admission', 'skeleton'):
        payload = a.unseal(history)
        row = next(r for r in payload['files'] if
                   (r['source'].endswith('.admission.json') if fault == 'admission'
                    else r['source'] == payload['roles']['a13_plan']))
        copy = Path(row['copy'])
        refusal = a.unseal(a.read(copy))
        if fault == 'admission':
            refusal['residual_rows'] = []
        else:
            refusal['jobs'][0]['seed'] += 1
        copy.chmod(0o600)
        a.atomic_json(copy, a.seal(refusal))
        copy.chmod(0o444)
        row.update(sha256=a.file_hash(copy), bytes=copy.stat().st_size)
        history = a.seal(payload)
        a.atomic_json(history_path, history)
        message = 'residual set' if fault == 'admission' else 'skeleton'
    elif fault == 'constants':
        original_sample_size = old.sample_size
        monkeypatch.setattr(old, 'sample_size', lambda *args, **kw: original_sample_size(*args, **kw) + 1)
        message = 'constants'
    else:
        monkeypatch.setattr(ext, 'price_round', lambda *args, **kw: dict(R_max=23, projected_x2_hours=1.))
        message = 'floor'
    output = tmp_path / 'a14.json'
    with pytest.raises(ValueError, match=message):
        ext.prepare(history_path, projection, seeds, forecast_config_file(tmp_path, monkeypatch), output, rehearsal=True)
    assert a.unseal(a.read(output.with_suffix('.round.json')))['state'] == 'refused'
    assert all(a.file_hash(p) == sha for p, sha in old_records.items())
    assert not output.exists()


def test_a14_pin_keeps_later_validation_admission(tmp_path, monkeypatch):
    from v3 import table_validation_a4 as a4, tables_a10, calibration
    history, _, _, _, args, _ = history_fixture(tmp_path, monkeypatch)
    original, root, candidate, _, _, source, cal_path, *_ = args
    plan = a.unseal(a.read(original))
    plan['registration'] = dict(commit=a.A14_COMMIT)
    monkeypatch.setattr(a4, 'registered_publish_guard', lambda *args: None)
    monkeypatch.setattr(a4, '_recompute_plan_hash', lambda p: p['plan_hash'])
    monkeypatch.setattr(tables_a10, 'verify_estimation_source', lambda *args, **kw: None)
    monkeypatch.setattr(a, 'verify_registration', lambda *args, **kw: None)
    monkeypatch.setattr(calibration, 'validate_calibration', lambda doc, **kw: a.unseal(doc))
    # The fixture published this run root non-registered; the registered attempt
    # is the run root's first publication under its pin, and under A16's
    # coordinated-change clause the refusal preserves the refused candidate.
    for suffix in ('.json', '.cell_results.json', '.compatibility.json'):
        Path(candidate).with_suffix(suffix).unlink()
    with pytest.raises(ValueError, match='cap exceeded'):
        a4.publish(plan, root, source, a.read(a.SIMULATION / cal_path), tmp_path / 'not_published.json', registered=True)
    assert a.unseal(a.read(root / 'a13_admission_check.json'))['outcome'] == 'refused'
    assert not (tmp_path / 'not_published.json').exists()
    assert 'a13_admission' not in a.unseal(a.read(candidate))['manifest']


def test_frozen_forecast_on_rehearsal_copies(tmp_path, monkeypatch):
    import os
    import platform
    import numpy
    from v3 import forecast_a14 as f
    from v3.history_a14 import verify_history
    history, *_ = history_fixture(tmp_path, monkeypatch)
    verified = verify_history(history, registered=False)
    eligible = sorted(k for k, ok in verified['eligible'].items() if ok)
    scripts = Path(os.environ.get('A14_FEASIBILITY_SCRIPTS',
        'C:/Users/matty/Dev/Lineage v3/a13_extension_2026-10-19/feasibility'))
    if not scripts.is_dir():
        pytest.skip('frozen assessment scripts must be supplied on rehearsal executor')
    source = f.stage_source(tmp_path / 'forecast_source')
    config = a.seal(dict(registered=False, source_view=str(source), scripts=str(scripts),
                        python=platform.python_version(), numpy=numpy.__version__,
                        package_paths=[str(Path(numpy.__file__).resolve().parent.parent)]))
    result = f.forecast(history, 32, eligible, config)
    assert 0 <= result['p_all_part2'] <= 1
    assert 0 <= result['p_all_part2_certification_0_9'] <= 1
    assert result['repository_imports'] and result['source_commit'] == f.COMMIT
    assert result['python'] == platform.python_version() and result['numpy'] == numpy.__version__
    with pytest.raises(ValueError, match='case A'):
        f.forecast(history, 32, [], config)
    # The parent verifier still receives the complete inventory. Only the
    # isolated reader loses one mapping, so refusal exercises that boundary.
    real_run = f.subprocess.run
    def missing_mapping(command, **kw):
        if '-c' in command and command[-1] == f.CHILD:
            import json
            value = json.loads(kw['input'])
            value['paths'].pop(str(Path(verified['history'].role('a13_plan')).resolve()))
            kw['input'] = json.dumps(value)
        return real_run(command, **kw)
    monkeypatch.setattr(f.subprocess, 'run', missing_mapping)
    with pytest.raises(ValueError, match='unmapped'):
        f.forecast(history, 32, eligible, config)


def test_replay_does_not_load_perturbed_checkpoints(tmp_path, monkeypatch):
    from test_v3_a13 import minimal_extension_job
    from v3 import replay_a14 as replay, compatibility_a10 as compat
    original = minimal_extension_job()
    config = {k: v for k, v in original['config'].items() if k != 'plan_hash'}
    plan = dict(schema=old.SCHEMA, registered=False, code_hash=a.code_identity(), job_skeletons=[config])
    plan['plan_hash'] = old.plan_hash(plan)
    job = a.stable_job(old.KIND, dict(config, plan_hash=plan['plan_hash']), 'v3_tables', 0)
    plan['jobs'] = [job]
    calls = []
    def stage(source, fit, rows, seed, override):
        calls.append(seed)
        return dict(count=6, rows={k: [[0., 1]] * 6 for k in rows})
    monkeypatch.setattr(old, 'extension_stage', stage)
    monkeypatch.setattr(old.a4, '_load_a1', lambda *args: {})
    result = old.run_stage_job(job, tmp_path)
    checkpoints = [a.read(tmp_path / 'a13_checkpoints' / job['id'] / f'{r["replicate"]:02d}.json')
                   for r in result['replicates']]
    bound = replay.binding(plan, job, result, checkpoints)
    item = dict(job=job, a13_replay=bound)
    token = compat._proof_producer.set(plan['code_hash'])
    try:
        calls.clear()
        assert replay.replay(item) == result
        assert calls == job['config']['stream_seeds'][:len(result['replicates'])]
        changed = deepcopy(result)
        changed['replicates'][0]['rows']['a'][0][0] = 1.
        altered = [a.seal(dict(job_sha256=a.digest(job), replicate=r)) for r in changed['replicates']]
        item['a13_replay'] = replay.binding(plan, job, changed, altered)
        with pytest.raises(ValueError, match='byte mismatch'):
            replay.replay(item)
    finally:
        compat._proof_producer.reset(token)


def test_physical_replay_matches_and_detects_joint_perturbation(tmp_path, monkeypatch):
    from v3 import replay_a14 as replay, compatibility_a10 as compat
    physical_stage = ext.extension_stage
    *_, plan = history_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(old, 'extension_stage', physical_stage)
    job = plan['jobs'][0]
    original = tmp_path / 'fresh_rehearsal'
    result = old.run_stage_job(job, original)
    paths = sorted((original / 'a13_checkpoints' / job['id']).glob('*.json'))
    documents = [a.read(p) for p in paths]
    before = {str(p): a.file_hash(p) for p in paths}
    item = dict(job=job, a13_replay=replay.binding(plan, job, result, documents))
    monkeypatch.setattr(replay, 'ROOT', tmp_path / 'isolated')
    token = compat._proof_producer.set(plan['code_hash'])
    try:
        assert a.canonical(replay.replay(item)) == a.canonical(result)
        changed = deepcopy(result)
        last = changed['replicates'][-1]
        pair = next(iter(last['rows'].values()))[0]
        pair[0] += .01
        pair[1] += 1
        altered = [a.seal(dict(job_sha256=a.digest(job), replicate=r)) for r in changed['replicates']]
        item['a13_replay'] = replay.binding(plan, job, changed, altered)
        with pytest.raises(ValueError, match='byte mismatch'):
            replay.replay(item)
        assert before == {str(p): a.file_hash(p) for p in paths}
        assert not list((tmp_path / 'isolated').rglob('*.json'))
    finally:
        compat._proof_producer.reset(token)


def install_worker_fixture_calibration():
    from v3 import calibration
    original = calibration.validate_calibration
    def validate(document, **kw):
        if document.get('payload', {}).get('fixture') is True and not kw.get('registered'):
            return original(document, registered=False)
        return original(document, **kw)
    calibration.validate_calibration = validate


def a14_fixture_runner_worker(*args):
    install_worker_fixture_calibration()
    from v3.production_runner import worker
    return worker(*args)


def a14_fixture_host_worker(*args):
    install_worker_fixture_calibration()
    from v3.host_a11 import execute_scratch
    return execute_scratch(*args)


def a14_fixture_halt_worker(*args):
    install_worker_fixture_calibration()
    from v3.host_a11 import execute_scratch
    original, calls = ext.extension_stage, 0
    def stage(*args, **kw):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ext.ScientificHalt('synthetic A14 halt')
        return original(*args, **kw)
    ext.extension_stage = stage
    return execute_scratch(*args)


class A14Transport:
    pass


def transport_fixture(root, route, drain):
    from v3.host_a11 import Loopback, Local
    class Transport(Loopback):
        def __init__(self):
            super().__init__(root)
            self.local = Local(root) if route == 'local' else None
            self.ops, self.first_hashes = [], {}
            self.drain = drain

        def call(self, request):
            from v3 import multihost_a11 as multi
            reply = self.local.call(request) if self.local else super().call(request)
            self.ops.append(request['op'])
            if request['op'] == 'a14_checkpoint' and self.drain:
                self.drain = False
                self.first_hashes = {p.name: a.file_hash(p) for p in (root / ext.PHASE / 'a14_checkpoints').glob('*/*.json')}
                multi.control(root, stop='drain')
            return reply

        def close(self):
            if self.local:
                self.local.close()
    return Transport()


@pytest.mark.parametrize('route', ['loopback', 'local'])
@pytest.mark.parametrize('halt', [False, True])
def test_a14_real_host_checkpoint_resume_and_halt(tmp_path, monkeypatch, route, halt):
    from v3 import multihost_a11 as multi, host_a11 as host, production_runner as runner, forecast_a14
    from test_v3_multihost_a11 import evidence
    from test_v3_a13 import host_loop_attempt
    history, history_path, projection, seeds, *_ = history_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(forecast_a14, 'forecast', lambda *args, **kw: {'p_all_part2': .8, 'p_all_part2_certification_0_9': .7})
    plan_path, root = tmp_path / 'a14_plan.json', tmp_path / 'coordinator'
    plan = ext.prepare(history_path, projection, seeds, forecast_config_file(tmp_path, monkeypatch), plan_path, rehearsal=True)
    for profile in plan['configuration'].values():
        profile.update(workers_local=[1], jobs_local=1, jobs_per_worker=1, rounds=1)
    plan = multi.freeze(plan, a.read(projection), code_commit='fixture', lease_seconds=15)
    a.atomic_json(plan_path, a.seal(plan))
    settings = dict(profile='local', workers=1, threads=1, cpu_budget=2, mode='work')
    multi.prepare(plan_path, root, settings)
    multi.approve_host(root, evidence(host.platform.node(), plan['code_hash'], (ext.KIND,), settings=settings),
                       'synthetic operator', '2026-10-20')
    monkeypatch.setattr(runner, 'worker', a14_fixture_runner_worker)
    monkeypatch.setattr(host, 'execute_scratch', a14_fixture_halt_worker if halt else a14_fixture_host_worker)
    transport = transport_fixture(root, route, not halt)
    if halt:
        with pytest.raises((RuntimeError, ConnectionError)):
            host_loop_attempt(plan_path, root, settings, tmp_path / 'host', transport)
        assert {'a14_checkpoint', 'a14_halt'} <= set(transport.ops)
        assert a.unseal(a.read(ext.round_record_path(plan)))['halt']
        assert all(runner.completed(root / ext.PHASE, j, plan['code_hash']) is None for j in plan['jobs'])
        with pytest.raises(ValueError, match='certifies nothing'):
            ext.publication_round(plan, root)
    else:
        _, first = host_loop_attempt(plan_path, root, settings, tmp_path / 'host', transport)
        assert not first['complete'] and not first['halt'] and transport.first_hashes
        before = {p.name: a.file_hash(p) for p in (root / ext.PHASE / 'a14_checkpoints').glob('*/*.json')}
        assert all(before[k] == v for k, v in transport.first_hashes.items())
        multi.control(root, stop='clear')
        second = transport_fixture(root, route, False)
        _, status = host_loop_attempt(plan_path, root, settings, tmp_path / 'host_resumed', second)
        assert status['complete'] and not status['halt']
        assert before == {p.name: a.file_hash(p) for p in (root / ext.PHASE / 'a14_checkpoints').glob('*/*.json')}
        assert a.read(root / ext.PHASE / 'nondeterminism_check.json')['matched']
        ext.publication_round(plan, root)


def a14_fixture_qualification_worker(args):
    install_worker_fixture_calibration()
    from v3.qualification_a11 import _run_one
    return _run_one(args)


def a14_fixture_host_loop(root, scratch, settings, name, fingerprint):
    install_worker_fixture_calibration()
    from v3 import production_runner, host_a11
    production_runner.worker = a14_fixture_runner_worker
    host_a11.execute_scratch = a14_fixture_host_worker
    return host_a11.run_host(host_a11.Loopback(root), scratch, settings, host=name,
                            environment=fingerprint, max_seconds=180)


def test_external_snapshot_qualification_and_two_hosts(tmp_path, monkeypatch):
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor
    from v3 import snapshot_a11, qualification_a11 as q, multihost_a11 as multi, forecast_a14
    from test_v3_multihost_a11 import evidence, FINGERPRINT
    history, history_path, projection, seeds, *_ = history_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(forecast_a14, 'forecast', lambda *args, **kw: {'p_all_part2': .8, 'p_all_part2_certification_0_9': .7})
    plan_path, root = tmp_path / 'a14_plan.json', tmp_path / 'coordinator'
    plan = ext.prepare(history_path, projection, seeds, forecast_config_file(tmp_path, monkeypatch), plan_path, rehearsal=True)
    for profile in plan['configuration'].values():
        profile.update(workers_local=[1], jobs_local=1, jobs_per_worker=1, rounds=1)
    plan = multi.freeze(plan, a.read(projection), code_commit='fixture', lease_seconds=30, historical_roots=[str(tmp_path / p) for p in ('copies', 'source', 'original', 'a13', 'calibration')])
    a.atomic_json(plan_path, a.seal(plan))
    # The historical copies are outside this simulated execution checkout,
    # but all physical fixture writes remain within the authorized worktree.
    monkeypatch.setattr(snapshot_a11, 'ROOT', tmp_path / 'fresh_checkout')
    qp = tmp_path / 'qualification.json'
    qual = q.build(plan_path, root, qp)
    assert len(qual['jobs']) >= 20 and qual['kinds'] == [ext.KIND]
    assert all(not ext.reserved(j['config']['seed']) for j in qual['jobs'])
    assert all('source' in r and 'aliases' in r for r in qual['inputs']['payload']['files'])
    monkeypatch.setattr(q, '_run_one', a14_fixture_qualification_worker)
    settings = dict(profile='local', workers=2, threads=1, cpu_budget=4, mode='normal')
    reference, candidate = tmp_path / 'reference.json', tmp_path / 'candidate.json'
    q.run(qp, reference, settings, host='yotko-evo-x2', environment=FINGERPRINT)
    q.run(qp, candidate, settings, host='candidate', environment=FINGERPRINT)
    assert a.unseal(q.compare(a.read(qp), a.read(reference), a.read(candidate)))['passed']
    multi.prepare(plan_path, root, settings)
    for name in ('alpha', 'beta'):
        multi.approve_host(root, evidence(name, plan['code_hash'], (ext.KIND,), settings=settings),
                           'synthetic operator', '2026-10-20')
    with multi.transaction(root):
        coordinator = multi.Coordinator(root)
        coordinator.start()
        coordinator.save()
    with ProcessPoolExecutor(max_workers=2, mp_context=mp.get_context('spawn')) as pool:
        futures = [pool.submit(a14_fixture_host_loop, root, tmp_path / name, settings, name, FINGERPRINT)
                   for name in ('alpha', 'beta')]
        for future in futures:
            future.result()
    status = multi.rpc(root, {'op': 'inspect'})['status']
    assert status['complete'] and not status['halt'] and set(status['hosts']) == {'alpha', 'beta'}
    assert a.read(root / ext.PHASE / 'nondeterminism_check.json')['matched']


def test_run_result_and_unadmitted_loader_equivalence_at_5df9866f(tmp_path):
    import sys
    from v3.forecast_a14 import stage_source
    source = stage_source(tmp_path / 'old_source')
    before = subprocess.check_output(['git', 'show', '55817036:simulation/v3/artifacts.py'])
    assert before.replace(b'\r\n', b'\n') == (source / 'simulation/v3/artifacts.py').read_bytes().replace(b'\r\n', b'\n')
    script = r'''
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
sys.path.append(sys.argv[2])
from v3 import artifacts as a, recording, production_runner as runner, calibration
from v3.instrument import EPSILON_L
from v3.tables_a10 import NOMINAL
from v3.policies import execution_policy_class
from test_v3_unpublished_bins import sparse_tables
validate = calibration.validate_calibration
def fixture_calibration(doc, **kw):
    payload = a.unseal(doc)
    validate(a.seal(dict(payload, code_hash=a.code_identity())), registered=False)
    return payload
calibration.validate_calibration = fixture_calibration
cal = a.seal(dict(schema='v3-calibration-1', fixture=True, code_hash='equivalence-fixture',
    values=dict(center=[0.]*10, sigma_squared=.02, n_ref=200., epsilon_n=1e-6,
                epsilon_e=1e-6, epsilon_l=EPSILON_L, c_e=2.5)))
real_model = recording.RecordedV3Model
if sys.argv[4] != 'current':
    assert a.code_identity() == sys.argv[4]
results = []
for index, (seed, reviews, missing) in enumerate(((200,False,()),(201,True,()),(202,True,(1,)))):
    model = sparse_tables(real_model(seed, rules=execution_policy_class()[:3], calibration=cal,
        instrument=NOMINAL.declaration(), rollout_steps=1, successor_capability=None),
        a.ROOT / '_pytest_v3' / ('equivalence_' + sys.argv[3]) / str(index), missing_rows=missing)
    availability = model.evaluate().available.tolist()
    if reviews: model.successor_capability = 1.5
    recording.RecordedV3Model = lambda **kwargs: model
    result = runner.execute(a.stable_job('rerun', {'steps': 3}, 'validation', index))
    results.append(dict(result=result, available=availability, fixture=model.tables.fixture))
print(a.canonical(results).decode())
'''
    outputs = [subprocess.check_output([sys.executable, '-B', '-c', script, str(root), str(a.SIMULATION), tmp_path.name, expected])
               for root, expected in ((source / 'simulation', '5df9866f1a59ab9c6c67660c18fbee694a64f97d5eebb65a41c8deaf2d650d1c'),
                                      (a.SIMULATION, 'current'))]
    assert outputs[0] == outputs[1]  # Every existing result field, including yield events.


def seed_categories():
    return ('registered', 'planning', 'probe', 'rehearsal', 'qualification',
            'a13_qualification_seeds', 'a13_configuration_seeds')


def operator_inputs(tmp_path, monkeypatch, *, registered=False):
    import platform, sys, numpy
    from v3 import forecast_a14 as f
    paths = {name: tmp_path / (name + '.json') for name in ('history', 'projection', 'seed_inventory', 'forecast_configuration')}
    a.atomic_json(paths['history'], {})
    a.atomic_json(paths['projection'], a.seal({'per_phase_capability': {}}))
    a.atomic_json(paths['seed_inventory'], a.seal({k: [] for k in seed_categories()}))
    scripts = tmp_path / 'scripts'; scripts.mkdir()
    hashes = {}
    for name in f.SCRIPTS:
        path = scripts / name; path.write_bytes(b'# synthetic frozen source\n'); hashes[name] = a.file_hash(path)
    monkeypatch.setattr(f, 'SCRIPTS', hashes)
    monkeypatch.setattr(f, 'verified_source', lambda path: {})
    monkeypatch.setattr(f.platform, 'node', lambda: 'yotko-evo-x2')
    config = dict(registered=registered, source_view=str(tmp_path / 'source_view'), scripts=str(scripts),
        python_executable=sys.executable, python=platform.python_version(), numpy=numpy.__version__,
        package_paths=[str(Path(numpy.__file__).resolve().parent.parent)])
    a.atomic_json(paths['forecast_configuration'], a.seal(config))
    monkeypatch.setattr(a, 'verify_registration', lambda *args, **kw: None)
    monkeypatch.setattr(old, 'PROJECTION_FILE_SHA256', a.file_hash(paths['projection']))
    monkeypatch.setattr(old, 'PROJECTION_SEAL', a.read(paths['projection'])['sha256'])
    monkeypatch.setattr(ext, 'TARGET', (tmp_path / 'family.json').relative_to(a.SIMULATION).as_posix())
    return paths, config


@pytest.mark.parametrize('fault', ['projection_hash', 'projection_seal', 'categories', 'seed_type',
    'intent', 'host', 'packages', 'source', 'scripts', 'interpreter', 'versions'])
def test_registered_operator_checks_precede_reservation(tmp_path, monkeypatch, fault):
    from v3 import forecast_a14 as f
    paths, config = operator_inputs(tmp_path, monkeypatch, registered=True)
    if fault == 'projection_hash':
        monkeypatch.setattr(old, 'PROJECTION_FILE_SHA256', 'wrong')
    elif fault == 'projection_seal':
        monkeypatch.setattr(old, 'PROJECTION_SEAL', 'wrong')
    elif fault in ('categories', 'seed_type'):
        inv = a.unseal(a.read(paths['seed_inventory']))
        if fault == 'categories': inv.pop('planning')
        else: inv['planning'] = [True]
        a.atomic_json(paths['seed_inventory'], a.seal(inv))
    elif fault == 'intent': config['registered'] = False
    elif fault == 'host': monkeypatch.setattr(f.platform, 'node', lambda: 'wrong-host')
    elif fault == 'packages': config['package_paths'] = [str(tmp_path)]
    elif fault == 'source': monkeypatch.setattr(f, 'verified_source', lambda path: (_ for _ in ()).throw(ValueError('source')))
    elif fault == 'scripts': (Path(config['scripts']) / next(iter(f.SCRIPTS))).write_text('changed')
    elif fault == 'interpreter': config['python_executable'] = str(tmp_path / 'absent.exe')
    else: config['numpy'] = 'not-the-installed-version'
    a.atomic_json(paths['forecast_configuration'], a.seal(config))
    real_read = ext.read
    def no_history(path):
        assert Path(path) != paths['history'], 'historical evidence was read'
        return real_read(path)
    monkeypatch.setattr(ext, 'read', no_history)
    before = {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    with pytest.raises((ValueError, OSError)):
        ext.prepare(*paths.values(), tmp_path / 'plan.json', registration={'fixture': True})
    assert before == {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    assert not (tmp_path / 'family.a14_round.json').exists()


@pytest.mark.parametrize('state,anchor_mode,allowed', [('preparing', True, True), ('prepared', False, True),
    ('launched', False, False), ('preparing', False, False), ('prepared', True, False), ('halted', True, False)])
def test_decline_only_before_launch_with_recorded_operator(tmp_path, monkeypatch, state, anchor_mode, allowed):
    anchor, plan_path = tmp_path / 'anchor.json', tmp_path / 'plan.json'
    plan = dict(registered=False, round_record_path=str(anchor), plan_hash='toy')
    a.atomic_json(plan_path, a.seal(plan))
    a.atomic_json(anchor, a.seal(dict(schema=ext.SCHEMA + '-round', state=state, halt=None,
                                    root='launched-root' if state == 'launched' else None, plan_hash='toy')))
    monkeypatch.setattr(ext, 'validate_plan', lambda plan: None)
    before = anchor.read_bytes()
    kw = dict(anchor_path=anchor) if anchor_mode else dict(plan_path=plan_path)
    if allowed:
        ext.decline(**kw, operator='synthetic operator', reason='declined go')
        value = a.unseal(a.read(anchor))
        assert value['state'] == 'refused' and value['halt']['operator'] == 'synthetic operator'
        assert value['halt']['epoch'] > 0
    else:
        with pytest.raises(ValueError): ext.decline(**kw, operator='operator', reason='reason')
        assert anchor.read_bytes() == before


def test_registered_a14_pull_is_refused_before_any_record(tmp_path):
    from v3 import multihost_a11 as m
    spec = dict(registered=True, registered_a10=True, instrument={'mapping': 'A10'}, jobs=[job_fixture()])
    before = list(tmp_path.rglob('*'))
    with pytest.raises(ValueError, match='single-host'): m.freeze(spec, a.seal({}), code_commit='toy')
    with pytest.raises(ValueError, match='single-host'): m.validate_extension(spec)
    assert list(tmp_path.rglob('*')) == before


@pytest.mark.parametrize('kind', ['a5_fvplain', 'table'])
def test_snapshot_historical_roots_are_required_hashed_and_enforced(tmp_path, monkeypatch, kind):
    from v3 import snapshot_a11 as snapshot
    source = tmp_path / 'old_checkout' / 'input.json'; a.atomic_json(source, {'fixture': True})
    monkeypatch.setattr(snapshot, 'ROOT', tmp_path / 'fresh_checkout')
    monkeypatch.setattr(snapshot, 'dependencies', lambda *args: [source])
    jobs = [dict(kind=kind, config={})]
    with pytest.raises(ValueError, match='historical roots'): snapshot.inventory(jobs, tmp_path)
    doc = snapshot.inventory(jobs, tmp_path, historical_roots=[str(source.parent)])
    payload = a.unseal(doc)
    assert payload['historical_roots_sha256'] == a.digest(payload['historical_roots'])
    snapshot.fetch(doc, payload['files'][0]['path'])
    bad = deepcopy(payload); bad['historical_roots'] = [str(tmp_path / 'other')]
    bad['historical_roots_sha256'] = a.digest(bad['historical_roots'])
    with pytest.raises(ValueError, match='historical roots'): snapshot.fetch(a.seal(bad), bad['files'][0]['path'])
    with pytest.raises(ValueError, match='historical roots'):
        snapshot.receive(a.seal(bad), tmp_path / 'snapshot', lambda *args: pytest.fail('must not transfer'))
    spec = dict(historical_roots=payload['historical_roots'], historical_roots_sha256='wrong')
    with pytest.raises(ValueError, match='hash'): snapshot.historical_roots(spec)


def registered_history_fixture(tmp_path, monkeypatch):
    """Exercise registered branches with injected toy authorities, never registered streams."""
    import json
    from v3 import history_a14 as h, tables_a10, calibration
    document, history_path, projection, seeds, args, plan = history_fixture(tmp_path, monkeypatch)
    payload = a.unseal(document)
    plan = deepcopy(plan)
    previous_jobs = plan['jobs']
    plan.update(registered=True, registered_a10=True, non_registered_rehearsal=False, registration={'fixture_pin': True})
    for config in plan['job_skeletons']:
        config.pop('settings_override', None)
    plan['plan_hash'] = old.plan_hash(plan)
    plan['jobs'] = [a.stable_job(old.KIND, dict(c, plan_hash=plan['plan_hash']), 'v3_tables', i)
                    for i, c in enumerate(plan['job_skeletons'])]
    jobs = {prior['id']: new for prior, new in zip(previous_jobs, plan['jobs'])}
    docs = {r['source']: a.read(r['copy']) for r in payload['files']}
    docs[payload['roles']['a13_plan']] = a.seal(plan)
    docs[payload['roles']['a13_public']] = a.seal(old.public_record(plan))
    root = Path(payload['roles']['a13_root'])
    anchor = a.unseal(docs[plan['round_record_path']]); anchor.update(plan_hash=plan['plan_hash'], spec_hash=a.digest(plan))
    docs[plan['round_record_path']] = a.seal(anchor)
    admission_path = str(Path(plan['round_record_path']).with_suffix('.admission.json'))
    admission = a.unseal(docs[admission_path]); admission['plan_hash'] = plan['plan_hash']
    docs[admission_path] = a.seal(admission)
    docs[str(root / 'identity.json')] = dict(code_hash=plan['code_hash'], spec_hash=a.digest(plan))
    check = docs[str(root / old.PHASE / 'nondeterminism_check.json')]
    check['checked'] = jobs[check['checked']]['id']
    environment = dict(python='synthetic-A13-python', numpy='synthetic-A13-numpy')
    for path, doc in docs.items():
        if isinstance(doc, dict) and doc.get('job', {}).get('id') in jobs:
            new = jobs[doc['job']['id']]
            doc['job'] = new
            if 'result' in doc:
                doc['result']['plan_hash'] = plan['plan_hash']
                doc['runtime'] = environment
    for path, doc in docs.items():
        if isinstance(doc, dict) and 'output_hash' in doc and doc.get('job', {}).get('kind') == old.KIND:
            output_path = str(Path(path).parent.parent / 'outputs' / Path(path).name)
            doc['output_hash'] = hashlib.sha256(a.canonical(docs[output_path]) + b'\n').hexdigest()
    for row in payload['files']:
        source, copied = row['source'], Path(row['copy'])
        data = docs[source]
        copied.chmod(0o600)
        a.atomic_json(copied, data)
        for old_id, new in jobs.items():
            if copied.name == old_id + '.json':
                renamed = copied.with_name(new['id'] + '.json')
                copied.replace(renamed)
                copied = renamed
                row['source'] = str(Path(source).with_name(new['id'] + '.json'))
                row['copy'] = str(renamed)
        copied.chmod(0o444)
        row.update(sha256=a.file_hash(copied), bytes=copied.stat().st_size)
    payload['a13_plan_hash'] = plan['plan_hash']
    document = a.seal(payload); a.atomic_json(history_path, document)
    monkeypatch.setattr(ext, 'APPROVED_A13_PLAN', plan['plan_hash'])
    monkeypatch.setattr(h, 'PRODUCER', plan['code_hash'])
    monkeypatch.setattr(h, 'ADMISSION_HASH', next(r['sha256'] for r in payload['files'] if r['source'] == admission_path))
    real_seed_check = old.check_seed_manifest
    monkeypatch.setattr(old, 'check_seed_manifest', lambda manifest, forbidden, **kw:
                        real_seed_check(manifest, forbidden, rehearsal=True))
    pin_calls = []
    monkeypatch.setattr(h, 'verify_registration', lambda pin, **kw: pin_calls.append(kw))
    monkeypatch.setattr(old.a4, 'registered_publish_guard', lambda original: None)
    original_calibration = calibration.validate_calibration
    monkeypatch.setattr(calibration, 'validate_calibration', lambda doc, **kw:
                        original_calibration(doc, **dict(kw, registered=False)))
    source_manifest = a.unseal(a.read(args[5] / 'tables_A1_manifest.json'))
    monkeypatch.setattr(tables_a10, 'build_jobs', lambda *args, **kw: source_manifest['jobs'])
    return document, history_path, projection, seeds, args, plan, pin_calls, environment


def test_registered_history_checks_with_synthetic_authorities(tmp_path, monkeypatch):
    from v3 import history_a14 as h
    document, _, _, _, _, plan, calls, environment = registered_history_fixture(tmp_path, monkeypatch)
    before = {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    verified = h.verify_history(document, registered=True)
    assert verified['old']['plan_hash'] == plan['plan_hash'] and verified['environment'] == environment
    assert len(calls) == 2 and all(c['historical'] is True for c in calls)
    assert sum(verified['eligible'].values()) == 1
    assert before == {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    monkeypatch.setattr(h, 'ADMISSION_HASH', 'wrong')
    with pytest.raises(ValueError, match='admission identity'): h.verify_history(document, registered=True)
    assert before == {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}


@pytest.mark.parametrize('fault', [None, 'committed', 'approval', 'after_hash', 'proof'])
def test_registered_producer_committed_copy_checks(tmp_path, monkeypatch, fault):
    from v3 import history_a14 as h, compatibility_a10 as compat
    after = a.source_manifest(); before = dict(after); before['v3/fixture.py'] = 'a' * 64
    producing, current = a.digest(before), a.code_identity()
    changes = compat.changed_files(before, after)
    record = dict(schema=compat.SCHEMA, passed=True, producing_code_hash=producing, new_code_hash=current,
        comparison=compat.COMPARISON, operator_approval=dict(approved=True, operator='toy', date='2026-10-20'),
        producing_source_manifest=before, new_source_manifest=after, changed_files=changes,
        reasons={k: 'synthetic proof' for k in changes}, populations=[dict(phase='fixture', job_ids=['a','b'])],
        proofs=[dict(job_id=j, passed=True, before_sha256='a'*64, after_sha256='a'*64) for j in ('a','b')])
    if fault == 'approval': record['operator_approval']['approved'] = False
    elif fault == 'after_hash': record['new_source_manifest'] = {}
    elif fault == 'proof': record['proofs'].pop()
    copy = tmp_path / 'committed_proof.json'; a.atomic_json(copy, a.seal(record))
    logical = a.SIMULATION / 'v3/runs/registered' / compat.record_name(producing, current)
    # This logical path is never opened. All reads return the synthetic copy.
    history = SimpleNamespace(payload={'compatibility_records':[str(logical)]},
                              file=lambda path: copy, read=lambda path: a.read(copy))
    def committed(command, **kw):
        assert command[:2] == ['git','-C'] and command[-1].startswith('HEAD:simulation/v3/runs/registered/')
        return SimpleNamespace(stdout=b'changed' if fault == 'committed' else copy.read_bytes())
    monkeypatch.setattr(h.subprocess, 'run', committed)
    if fault is None: h.verify_producer(history, producing)
    else:
        with pytest.raises(ValueError): h.verify_producer(history, producing)


def test_preentry_is_repeatable_read_only_and_never_forecasts(tmp_path, monkeypatch):
    from v3 import forecast_a14 as f
    document, history_path, projection, seeds, *_ = registered_history_fixture(tmp_path, monkeypatch)
    inputs, _ = operator_inputs(tmp_path / 'operator', monkeypatch, registered=True)
    # operator_inputs uses distinct metadata; restore the verified historical inventory.
    a.atomic_json(history_path, document)
    inputs.update(history=history_path, projection=projection, seed_inventory=seeds)
    monkeypatch.setattr(old, 'PROJECTION_FILE_SHA256', a.file_hash(projection))
    monkeypatch.setattr(old, 'PROJECTION_SEAL', a.read(projection)['sha256'])
    preentry_tooling(inputs, monkeypatch)
    monkeypatch.setattr(f, 'forecast', lambda *args, **kw: pytest.fail('preentry computed a forecast'))
    before = {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    reports = []
    for i in range(2):
        report = tmp_path / ('preentry_' + str(i) + '.json'); reports.append(str(report))
        result = ext.preentry(*inputs.values(), tmp_path / 'plan.json', report, registration={'fixture':True})
        assert result['passed'] and all(c['passed'] for c in result['checks'].values())
        assert set(result) == {'schema','passed','checks','E2','R_max','projected_x2_hours'}
    assert before == {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file() and str(p) not in reports}
    assert not (tmp_path / 'plan.json').exists() and not (tmp_path / 'family.a14_round.json').exists()
    from v3 import history_a14 as h
    verified = h.verify_history(document, registered=True)
    for fault in ('layout', 'case_a'):
        changed = dict(verified)
        if fault == 'layout':
            roles = {name: verified['history'].role(name) for name in ('a13_plan', 'a13_root')}
            roles['a13_plan'] = str(Path(roles['a13_plan']).with_name('wrong.json'))
            changed['history'] = SimpleNamespace(role=roles.__getitem__, paths=verified['history'].paths)
        else:
            changed['eligible'] = {key: True for key in verified['eligible']}
            assert changed['eligible'] != verified['eligible']
        report = tmp_path / ('bad_' + fault + '.json'); reports.append(str(report))
        with monkeypatch.context() as patch:
            patch.setattr(h, 'verify_history', lambda *args, **kw: changed)
            result = ext.preentry(*inputs.values(), tmp_path / 'plan.json', report, registration={'fixture':True})
        assert not result['passed']
        assert result['checks']['forecast_' + fault]['status'] == 'failed'
    assert before == {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file() and str(p) not in reports}
    real = old.sample_size
    monkeypatch.setattr(old, 'sample_size', lambda *args, **kw: real(*args, **kw)+1)
    result = ext.preentry(*inputs.values(), tmp_path / 'plan.json', tmp_path / 'failed.json', registration={'fixture':True})
    assert not result['passed'] and not (tmp_path / 'family.a14_round.json').exists()


def test_inventory_builder_requires_roles_and_reproduces_history(tmp_path, monkeypatch):
    from v3 import history_a14 as h
    document, history_path, projection, seeds, args, plan = history_fixture(tmp_path / 'historical', monkeypatch)
    original, original_root, candidate, _, _, source_root, calibration, *_ = args
    old_roles = a.unseal(document)['roles']
    roles = dict(a13_plan=old_roles['a13_plan'], a13_public=old_roles['a13_public'], a13_root=old_roles['a13_root'],
        a13_round=plan['round_record_path'], a13_admission=str(Path(plan['round_record_path']).with_suffix('.admission.json')),
        original_plan=str(original), original_root=str(original_root), candidate=str(candidate),
        original_receipt=str(candidate.with_suffix('.compatibility.json')), original_sidecar=str(candidate.with_suffix('.cell_results.json')),
        a1_root=str(source_root), calibration=str((a.SIMULATION / calibration).resolve()))
    declaration = dict(roles=roles, historical_roots=[str(tmp_path / 'historical')], compatibility_records=[])
    roles_path = tmp_path / 'roles.json'; a.atomic_json(roles_path,a.seal(declaration))
    built = h.build_inventory(roles_path,tmp_path / 'historical',tmp_path/'built_copies',tmp_path/'built_inventory.json')
    verified = h.verify_history(built,registered=False)
    assert verified['classification_sha256'] == h.verify_history(document,registered=False)['classification_sha256']
    assert all(not Path(r['copy']).stat().st_mode & 0o222 for r in a.unseal(built)['files'])
    for name in h.REQUIRED_ROLES:
        bad = deepcopy(declaration); del bad['roles'][name]
        a.atomic_json(roles_path,a.seal(bad))
        with pytest.raises(ValueError,match='every declared role'):
            h.build_inventory(roles_path,tmp_path / 'historical',tmp_path/'absent_copies',tmp_path/'absent_inventory.json')
        assert not (tmp_path/'absent_copies').exists() and not (tmp_path/'absent_inventory.json').exists()


def test_registered_forecast_records_environment_difference(tmp_path, monkeypatch):
    import json
    from v3 import forecast_a14 as f, history_a14 as h
    document, *_ = registered_history_fixture(tmp_path, monkeypatch)
    verified = h.verify_history(document, registered=True)
    inputs, config = operator_inputs(tmp_path / 'operator', monkeypatch, registered=True)
    validated = f.validate_configuration(inputs['forecast_configuration'], registered=True)
    actual = validated['actual_environment']
    monkeypatch.setattr(h, 'verify_history', lambda *args, **kw: verified)
    monkeypatch.setattr(f.subprocess, 'run', lambda *args, **kw: SimpleNamespace(returncode=0, stderr='',
        stdout=json.dumps(dict(p_all_part2=.8,p_all_part2_certification_0_9=.7,**actual))))
    eligible = [k for k,v in verified['eligible'].items() if v]
    result = f.forecast(document,32,eligible,inputs['forecast_configuration'],registered=True,validated=validated)
    assert result['a13_environment'] == verified['environment']
    assert result['actual_environment'] == result['declared_environment'] == actual
    assert result['environment_matches_a13'] is False and result['declared_matches_actual'] is True


@pytest.mark.parametrize('body,finding', [('raise MemoryError("synthetic")',False),
    ('import os; os._exit(9)',False), ('import sys; print("finding: synthetic unmapped read",file=sys.stderr); sys.exit(78)',True)])
def test_forecast_child_finding_and_infrastructure_exits(tmp_path, monkeypatch, body, finding):
    from v3 import forecast_a14 as f, history_a14 as h
    history, history_path, projection, seeds, *_ = history_fixture(tmp_path, monkeypatch)
    verified = h.verify_history(history,registered=False)
    inputs, config = operator_inputs(tmp_path / 'operator', monkeypatch)
    validated = f.validate_configuration(inputs['forecast_configuration'],registered=False)
    monkeypatch.setattr(h,'verify_history',lambda *args,**kw:verified)
    monkeypatch.setattr(f,'CHILD',body)
    eligible = [k for k,v in verified['eligible'].items() if v]
    output = tmp_path / 'plan.json'
    with pytest.raises(ValueError if finding else OSError):
        ext.prepare(history_path,projection,seeds,inputs['forecast_configuration'],output,rehearsal=True)
    record = a.unseal(a.read(output.with_suffix('.round.json')))
    assert record['state'] == ('refused' if finding else 'preparing')
    assert bool(record['halt']) == finding
    assert not output.exists()



def test_proof_snapshots_require_declared_roots_and_preserve_internal_bytes(tmp_path, monkeypatch):
    from v3 import compatibility_shards_a11 as proof, snapshot_a11 as snapshot
    current = tmp_path / 'v3'
    external = tmp_path / 'historical'
    inside, outside = current / 'input.json', external / 'input.json'
    a.atomic_json(inside, {'toy': 'inside'}); a.atomic_json(outside, {'toy': 'outside'})
    monkeypatch.setattr(proof, 'ROOT', current)
    monkeypatch.setattr(snapshot, 'ROOT', current)
    monkeypatch.setattr(snapshot, 'SIMULATION', current.parent)
    monkeypatch.setattr(proof, 'SIMULATION', current.parent)
    items = [dict(job={'kind':'fixture','config':{}}, phase_root=str(tmp_path))]
    monkeypatch.setattr(snapshot, 'dependencies', lambda *args: [inside])
    internal = proof.portable_inventory(items)
    key = a.digest(str(inside))
    assert internal == a.seal(dict(schema='v3-A11-inputs-1', simulation=str(current.parent), files=[
        dict(path='v3/proof_inputs/' + key + '/' + inside.name, source=str(inside), aliases=[str(inside)],
             sha256=a.file_hash(inside), bytes=inside.stat().st_size)]))
    monkeypatch.setattr(snapshot, 'dependencies', lambda *args: [outside])
    with pytest.raises(ValueError, match='historical roots'): proof.portable_inventory(items)
    spec = tmp_path / 'source_spec.json'; a.atomic_json(spec, a.seal({}))
    roots = proof.source_historical_roots([dict(spec=str(spec),historical_roots=[str(external)])])
    document = proof.portable_inventory(items,historical_roots=roots)
    assert a.unseal(document)['historical_roots_sha256'] == a.digest(roots)
    bundle = tmp_path / 'proof_bundle'
    proof.stage_inputs(document,bundle)
    view = proof.receive_inputs(document,bundle,tmp_path / 'proof_snapshot')
    with a.input_view(view): assert a.read(outside) == {'toy':'outside'}
    bad = a.unseal(document); bad['historical_roots'] = []
    bad['historical_roots_sha256'] = a.digest([])
    with pytest.raises(ValueError, match='historical roots'):
        proof.stage_inputs(a.seal(bad),tmp_path / 'refused_bundle')
    assert not (tmp_path / 'refused_bundle').exists()



def test_proof_roots_are_frozen_for_qualification_and_shards(tmp_path, monkeypatch):
    from test_v3_compatibility_shards_a11 import source_fixture, hosts, ORIGINAL
    from v3 import compatibility_shards_a11 as proof, compatibility_a10 as compatibility
    sources, reasons = source_fixture(tmp_path)
    roots = [str(tmp_path / 'old')]
    sources[0]['historical_roots'] = roots
    qualification = proof.qualification_bundle(sources, tmp_path / 'qualification.json')
    assert a.unseal(qualification['inputs'])['historical_roots_sha256'] == a.digest(roots)
    monkeypatch.setattr(proof, 'verify_code', lambda commit: None)
    monkeypatch.setattr(proof.platform, 'node', lambda: ORIGINAL)
    monkeypatch.setattr(compatibility, 'RECORD_DIRECTORY', tmp_path / 'reservations')
    attempt = proof.freeze(sources, reasons, tmp_path / 'proof.json', hosts(), 'f' * 40)
    for snapshots in attempt['snapshots'].values():
        for document in snapshots.values():
            assert a.unseal(document)['historical_roots'] == roots
            assert a.unseal(document)['historical_roots_sha256'] == a.digest(roots)
    assert proof.load_attempt(tmp_path / 'proof.attempt.json') == attempt



def preentry_tooling(inputs, monkeypatch):
    """Synthetic source/scripts; script execution fails, import-only checks pass."""
    from v3 import forecast_a14 as f
    config = a.unseal(a.read(inputs['forecast_configuration']))
    source = Path(config['source_view'])
    paths = {
        'simulation/v3/__init__.py': '',
        'simulation/v3/artifacts.py': 'from layout_helper import SENTINEL\n',
        'simulation/layout_helper.py': 'SENTINEL = True\n'}
    hashes = {}
    for relative, content in paths.items():
        path = source / relative; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        hashes[str(path.resolve())] = a.file_hash(path)
    def verified(view):
        assert Path(view) == source
        assert all(a.file_hash(path) == sha for path,sha in hashes.items())
        return dict(hashes)
    monkeypatch.setattr(f, 'verified_source', verified)
    scripts = {}
    for name in f.SCRIPTS:
        path = Path(config['scripts']) / name
        path.write_text('raise AssertionError("preentry executed a probability script")\n', encoding='utf-8')
        scripts[name] = a.file_hash(path)
    monkeypatch.setattr(f, 'SCRIPTS', scripts)
    return source


def test_preparation_failure_preserves_decline_and_records_late_failures(tmp_path):
    anchor = ext.reserve_preparation(tmp_path/'plan.json', {}, registered=False)
    ext.decline(anchor_path=anchor, operator='synthetic operator', reason='declined preparation')
    declined = a.unseal(a.read(anchor))
    for reason in ('late preparation exception', 'another late failure'):
        ext.preparation_failure(anchor, reason)
    after = a.unseal(a.read(anchor))
    assert after['halt'] == declined['halt']
    assert after['state'] == declined['state'] == 'refused'
    assert {k:v for k,v in after.items() if k!='later_failures'} == declined
    assert [r['reason'] for r in after['later_failures']] == ['late preparation exception', 'another late failure']
    assert all(r['epoch'] >= declined['halt']['epoch'] for r in after['later_failures'])


@pytest.mark.parametrize('fault', [None, 'ext', 'script', 'source', 'reachable_a14'])
def test_preentry_layout_import_audit_never_executes_probability_scripts(tmp_path, monkeypatch, fault):
    from v3 import forecast_a14 as f
    inputs, _ = operator_inputs(tmp_path/'operator', monkeypatch)
    source = preentry_tooling(inputs, monkeypatch)
    validated = f.validate_configuration(inputs['forecast_configuration'], registered=False)
    roles = dict(a13_plan=str(tmp_path/'historical/plan.json'), a13_root=str(tmp_path/'historical/root'))
    verified = dict(history=SimpleNamespace(role=roles.__getitem__,paths={}))
    if fault == 'ext':
        roles['a13_plan'] = str(tmp_path/'historical/mistyped.json')
    elif fault == 'script':
        Path(next(iter(validated['scripts']))).write_text('# changed',encoding='utf-8')
    elif fault == 'source':
        (source/'simulation/v3/artifacts.py').write_text('raise AssertionError("source changed")',encoding='utf-8')
    elif fault == 'reachable_a14':
        path=source/'simulation/v3/forecast_a14.py'
        path.write_text('raise AssertionError("must not import A14")',encoding='utf-8')
        validated['sources'][str(path.resolve())]=a.file_hash(path)
    monkeypatch.setattr(f,'forecast',lambda *args,**kw:pytest.fail('probability calculation called'))
    before={str(p):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    if fault:
        with pytest.raises(ValueError): f.check_preentry_layout(verified,validated)
    else:
        result=f.check_preentry_layout(verified,validated)
        assert result['checks_only'] is True
        assert 'layout_helper' in result['repository_imports']
        assert not any(k.startswith('p_all_part2') for k in result)
    assert before=={str(p):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
