"""Review regressions, exclusively synthetic inputs and executor metadata."""
from copy import deepcopy
from pathlib import Path
import time

import pytest
from test_v3_paths import tmp_path
from v3 import artifacts as a, worker_control as wc, production_runner as runner
from v3 import compatibility_shards_a11 as proof, qualification_a11 as q


def settings(workers=8, **extra):
    return dict(profile='local', workers=workers, threads=1, cpu_budget=8, mode='normal',
                override_reason='operator-selected initial target', operator='operator', **extra)


def test_identical_override_repeat_preserves_resume_target_and_history(tmp_path):
    first = wc.settings(settings())
    wc.initial_control(tmp_path, first)
    lowered = wc.control(tmp_path, first, workers=3)
    repeated = wc.settings(settings())
    assert repeated['operator_override']['epoch'] != first['operator_override']['epoch']
    assert wc.initial_control(tmp_path, repeated) == lowered
    assert wc.selection(repeated, lowered)['workers'] == 3
    changed = wc.settings(dict(settings(), operator='another operator'))
    value = wc.initial_control(tmp_path, changed)
    assert value['max_workers'] == 8 and len(value['history']) == 3
    assert value['history'][-1]['operator'] == 'another operator'


def test_pull_rejoin_and_resume_preserve_targets_and_default_is_sum(tmp_path):
    from test_v3_multihost_a11 import initialize, spec_fixture, SETTINGS, FINGERPRINT
    from v3 import multihost_a11 as m
    path, root, _ = initialize(tmp_path, spec_fixture(50))
    s = dict(SETTINGS, workers=16, override_reason='sixteen per host', operator='operator')
    request = dict(op='join', fingerprint=FINGERPRINT, code_hash=a.code_identity(), code_commit='fixture', settings=s)
    alpha = m.rpc(root, dict(request, host='alpha'))
    m.rpc(root, dict(request, host='beta'))
    # The coordinator's host-style --workers never installs an aggregate cap.
    m.prepare(path, root, s)
    assert 'max_workers' not in m.read_state(root)['control']
    assert m.rpc(root, dict(op='inspect'))['status']['overall_worker_target'] == 24
    m.control(root, 'alpha', max_workers=5)
    before = m.read_state(root)['host_controls']['alpha']
    m.rpc(root, dict(op='leave', host='alpha', session=alpha['session']))
    rejoined = m.rpc(root, dict(request, host='alpha'))
    assert rejoined['control'] == before
    assert m.rpc(root, dict(op='inspect'))['status']['overall_worker_target'] == 17
    explicit = dict(s, overall_workers=20)
    m.prepare(path, root, explicit)
    m.control(root, max_workers=9)
    m.prepare(path, root, explicit)
    assert m.read_state(root)['control']['max_workers'] == 9
    m.prepare(path, root, dict(explicit, overall_workers=22))
    assert m.read_state(root)['control']['max_workers'] == 22


@pytest.mark.parametrize('field,value', [('workers',6), ('memory_headroom',.9), ('override_reason','changed reason'), ('operator','another operator')])
def test_changed_substantive_override_replaces_target_even_with_normalized_settings(tmp_path, field, value):
    first = wc.settings(settings())
    wc.initial_control(tmp_path, first)
    wc.control(tmp_path, first, workers=2)
    changed = wc.settings(dict(first, **{field:value}))
    result = wc.initial_control(tmp_path, changed)
    assert result['max_workers'] == changed['workers']
    assert len(result['history']) == 3
    assert result['initial_override'] == changed['operator_override']


@pytest.mark.parametrize('explicit', [False, True])
def test_modes_preserve_target_and_restore_measured_choice(tmp_path, explicit):
    s = wc.settings(dict(profile='x2', workers=15, threads=1, cpu_budget=16, mode='normal',
                         **({'override_reason':'explicit target'} if explicit else {})))
    measured = [dict(workers=w, threads=1, valid=True, completed=w, wall_seconds=1.) for w in (1,10,14)]
    value = wc.initial_control(tmp_path, s)
    original = deepcopy(value)
    assert wc.selection(s, value, measured)['workers'] == (15 if explicit else 14)
    for mode, expected in [('work',12 if explicit else 10), ('normal',15 if explicit else 14)]:
        value = wc.control(tmp_path, s, mode=mode)
        assert value['max_workers'] == 15
        assert value.get('target_set') == original.get('target_set')
        assert wc.selection(s, value, measured)['workers'] == expected
    assert wc.initial_control(tmp_path, wc.settings(s)) == value
    assert value['history'][-1]['target'] == 15
    assert value['history'][-1]['mode_caps_target']


def test_mode_precedence_is_one_setting(monkeypatch):
    s = wc.settings(settings())
    value = wc.apply_initial_override(dict(mode='normal', max_workers=8), s)
    assert wc.selection(s, value)['workers'] == 7
    changed = wc.change(value, s, mode='work')
    assert changed['max_workers'] == 8 and wc.selection(s, changed)['workers'] == 4
    monkeypatch.setattr(wc, 'MODE_CAPS_TARGET', False)
    assert wc.selection(s, changed)['workers'] == 8
    ordinary = dict(s, workers=7); ordinary.pop('operator_override')
    assert wc.selection(ordinary, dict(mode='work',max_workers=7))['workers'] == 4


@pytest.mark.parametrize('explicit', [False, True])
def test_pull_modes_restore_target_and_choice_per_host(tmp_path, explicit):
    from test_v3_multihost_a11 import initialize, spec_fixture, SETTINGS, FINGERPRINT
    from v3 import multihost_a11 as m
    launch = dict(SETTINGS, workers=12, mode='normal', cpu_budget=14)
    if explicit: launch['override_reason'] = 'explicit target'
    _, root, _ = initialize(tmp_path, spec_fixture(50))
    request = dict(op='join', fingerprint=FINGERPRINT, code_hash=a.code_identity(), code_commit='fixture', settings=launch)
    measured = [dict(workers=w,threads=1,completed=w,wall_seconds=1.,valid=True,job_seconds=[.1]*w) for w in (1,8,11)]
    sessions = {}
    for name in ('alpha','beta'):
        reply=m.rpc(root,dict(request,host=name)); sessions[name]=reply['session']
        identity=dict(host=name,session=reply['session'])
        snapshot=m.rpc(root,dict(identity,op='inputs',phase='toy',configuration=True))
        m.rpc(root,dict(identity,op='configure',phase='toy',input_sha256=snapshot['sha256'],measurements=measured))
    for name in sessions:
        for mode, expected in [('work',10 if explicit else 8),('normal',12 if explicit else 11)]:
            m.control(root,name,mode=mode)
            state=m.read_state(root)
            current=state['sessions'][sessions[name]]
            assert current['control']['max_workers']==12
            assert current['control'].get('target_set',False)==explicit
            assert wc.selection(current['settings'],current['control'],current['configuration']['toy'])['workers']==expected
        m.rpc(root,dict(op='leave',host=name,session=sessions[name]))
        reply=m.rpc(root,dict(request,host=name))
        assert reply['control']['max_workers']==12
        assert wc.selection(launch,reply['control'],measured)['workers']==(12 if explicit else 11)


def test_both_orders_of_mode_and_explicit_raise_keep_target(tmp_path):
    s=wc.settings(settings())
    estimates={'job':dict(memory_class='toy',memory_known=True)}
    wc.initial_control(tmp_path,s)
    value=wc.control(tmp_path,s,mode='work')
    assert value['max_workers']==8 and wc.selection(s,value)['workers']==4
    with pytest.raises(ValueError,match='reason'): wc.control(tmp_path,s,workers=6)
    value=wc.control(tmp_path,s,workers=6,reason='deliberate target',estimates=estimates)
    assert value['max_workers']==6 and wc.selection(s,value)['workers']==4
    value=wc.control(tmp_path,s,mode='normal')
    assert value['max_workers']==6 and wc.selection(s,value)['workers']==6
    value=wc.control(tmp_path,s,mode='work')
    assert value['max_workers']==6 and wc.selection(s,value)['workers']==4


def test_no_memory_estimate_refuses_override_and_measured_peak_authorizes_it(tmp_path, monkeypatch):
    job = a.stable_job('fixture', dict(seconds=.01, phase='toy'), 'validation', 0)
    estimates = wc.resources(dict(jobs=[job]))
    assert not estimates[job['id']]['memory_known']
    s = wc.settings(settings())
    with pytest.raises(ValueError, match='sealed memory'):
        wc.load_sheet([job], estimates, s, 10.)
    peak = {estimates[job['id']]['memory_class']: 1.}
    assert wc.load_sheet([job], estimates, s, 10., peaks=peak)['planned_workers'] == 7
    monkeypatch.setattr(runner, 'mem_available_bytes', lambda: 10_000_000_000)
    wc.initial_control(tmp_path, s)
    result=runner.dispatch(tmp_path, [job], a.code_identity(), s, time.time()+20, job_resources=estimates)
    assert result['completed']==1  # Runtime caps safely instead of crashing on a stale control.


def test_ordinary_configuration_trial_is_not_an_above_mode_override():
    job = a.stable_job('fixture', {}, 'configuration', 0)
    estimates = wc.resources(dict(jobs=[job]))
    ordinary = wc.settings(dict(profile='local', workers=1, threads=1, cpu_budget=4, mode='work'))
    wc.require_memory_authority(ordinary, {}, estimates, {}, dict(workers=4), configuration_trial=True)
    with pytest.raises(ValueError, match='sealed memory'):
        wc.require_memory_authority(ordinary, {}, estimates, {}, dict(workers=4))
    override = wc.settings(dict(ordinary, workers=4, override_reason='operator raises target'))
    with pytest.raises(ValueError, match='sealed memory'):
        wc.require_memory_authority(override, {}, estimates, {}, dict(workers=4), configuration_trial=True)


def test_configuration_target_holds_lock_and_keeps_live_command(tmp_path, monkeypatch):
    s = wc.settings(settings())
    wc.initial_control(tmp_path, s)
    wc.control(tmp_path, s, workers=3)
    assert wc.configuration_target(tmp_path, 1)['max_workers'] == 3
    a.atomic_json(tmp_path/'control.json', dict(mode='normal', max_workers=3))
    original = wc.atomic_json
    def locked(path, value):
        with pytest.raises(RuntimeError):
            with a.lease(tmp_path/'control.lock'): pass
        original(path, value)
    monkeypatch.setattr(wc, 'atomic_json', locked)
    assert wc.configuration_target(tmp_path, 2)['max_workers'] == 2


def test_qualification_missing_memory_refuses_override_before_inputs(tmp_path, monkeypatch):
    job = a.stable_job('fixture', {}, 'validation', 0)
    plan = tmp_path/'qualification.json'
    a.atomic_json(plan, a.seal(dict(code_hash=a.code_identity(), non_registered=True, jobs=[job])))
    monkeypatch.setattr(runner, 'mem_available_bytes', lambda: 10_000_000_000)
    target = tmp_path/'qualification_result.json'
    with pytest.raises(ValueError, match='sealed memory'):
        q.run(plan, target, settings())
    assert not target.exists()


def test_proof_control_lock_failure_precedes_marker_and_remains_retryable(tmp_path, monkeypatch):
    from test_v3_compatibility_shards_a11 import source_fixture, hosts, ORIGINAL, FINGERPRINT
    from v3 import compatibility_a10 as c, host_a11 as host
    monkeypatch.setattr(proof, 'verify_code', lambda commit: None)
    monkeypatch.setattr(proof.platform, 'node', lambda: ORIGINAL)
    monkeypatch.setattr(host, 'fingerprint', lambda: FINGERPRINT)
    monkeypatch.setattr(c, 'RECORD_DIRECTORY', tmp_path/'reservations')
    sources, reasons = source_fixture(tmp_path)
    target = tmp_path/'proof.json'; path = target.with_suffix('.attempt.json')
    proof.freeze(sources, reasons, target, hosts(False), 'f'*40)
    proof.stage(path, ORIGINAL)
    root = proof.host_directory(path, ORIGINAL)
    monkeypatch.setattr(proof, 'configure_host', lambda *args: dict(toy=dict(chosen=dict(workers=1))))
    with monkeypatch.context() as patch:
        def busy(*args):
            assert not (root/'started.json').exists()
            raise RuntimeError('lease already held')
        patch.setattr(wc, 'configuration_target', busy)
        with pytest.raises(RuntimeError, match='lease'): proof.run_shard(path, ORIGINAL)
    assert not (root/'started.json').exists() and not (root/'result.json').exists()
    assert proof.run_shard(path, ORIGINAL)['passed']


def test_qualification_speed_is_per_job_not_concurrency():
    from test_v3_multihost_a11 import evidence
    e = a.unseal(evidence('other', a.code_identity(), speed=2.))
    e['candidate']['workers'] = 4
    e['candidate']['settings']['workers'] = 4
    # A four-times elapsed speed combines two-times concurrency and job speed.
    e['candidate']['elapsed_seconds'] = e['reference']['elapsed_seconds']/4
    e['relative_throughput'] = 4.
    assert q.scheduling_rate(e) == 2.
    assert e['relative_throughput'] == 4.  # Existing participation charge is unchanged.
    for run in ('candidate', 'reference'):
        for row in e[run]['proofs']: row.pop('worker_seconds')
    with pytest.raises(ValueError, match='worker'): q.scheduling_rate(e)
    e['candidate']['workers'] = e['reference']['workers']
    assert q.scheduling_rate(e) == 4.


def test_informational_status_retries_are_bounded(monkeypatch, tmp_path):
    calls = []
    def broken(path, value):
        calls.append(path)
        raise OSError('injected informational disk error')
    monkeypatch.setattr(proof, 'atomic_json', broken)
    assert proof.informational_status(tmp_path/'scheduling.json', {}) is False
    assert len(calls) == 2


def test_status_io_failure_does_not_spend_or_fail_shard(tmp_path, monkeypatch):
    from test_v3_compatibility_shards_a11 import source_fixture, hosts, ORIGINAL, FINGERPRINT
    from v3 import compatibility_a10 as c, host_a11 as host
    monkeypatch.setattr(proof, 'verify_code', lambda commit: None)
    monkeypatch.setattr(proof.platform, 'node', lambda: ORIGINAL)
    monkeypatch.setattr(host, 'fingerprint', lambda: FINGERPRINT)
    monkeypatch.setattr(c, 'RECORD_DIRECTORY', tmp_path/'reservations')
    sources, reasons = source_fixture(tmp_path, seconds=.3)
    target = tmp_path/'proof.json'; path = target.with_suffix('.attempt.json')
    proof.freeze(sources, reasons, target, hosts(False), 'f'*40)
    proof.stage(path, ORIGINAL)
    original = proof.atomic_json
    attempts = []
    def status_failure(path, value):
        if Path(path).name == 'scheduling.json':
            attempts.append(time.monotonic())
            raise OSError('status disk error only')
        original(path, value)
    monkeypatch.setattr(proof, 'atomic_json', status_failure)
    result = proof.run_shard(path, ORIGINAL)
    assert result['passed'] and proof.combine(path)['passed']
    assert attempts and len(attempts) % 2 == 0
    # Successive pairs within each run_items call are at least one second apart.
    assert all(b-a >= .005 for a,b in zip(attempts[::2], attempts[1::2]))


def test_legacy_configuration_profiles_use_sealed_phase_without_phase_in_config():
    source = a.stable_job('table', dict(settings=dict(groups=2, particles=2, runs_per_group=2, burn=3, measure=4), kernel={}), 'validation', 0)
    jobs = [a.stable_job('a4_validate', dict(phase='validate_plain', route='plain', a1_job=source), 'validation', 0)]
    spec = dict(schema='v3-A4-validation-1', jobs=jobs, memory_estimate_gb={'validate_plain': 3., 'validate_fv': 7.})
    for phase, route, expected in [('validate_plain','plain',3.), ('validate_fv','fv',7.)]:
        cfg = dict(route=route, a1_job=source)
        profile = a.stable_job('a4_validate', cfg, 'configuration', 0)
        before = deepcopy(profile)
        resource = wc.configuration_resources([profile], jobs, wc.resources(spec), phase=phase, spec=spec)[profile['id']]
        assert resource['memory_known'] and wc.reservation(resource, {}) == expected
        assert profile == before


def test_pull_empty_phase_accepts_only_its_declared_configuration_peak(tmp_path):
    from test_v3_multihost_a11 import initialize, join, spec_fixture
    from v3 import multihost_a11 as m
    spec = spec_fixture(phases=('toy','empty'))
    spec['jobs'] = [j for j in spec['jobs'] if j['config']['phase'] == 'toy']
    ids = {j['id'] for j in spec['jobs']}
    pull = spec['pull_dispatch']
    pull['job_classes'] = {k:v for k,v in pull['job_classes'].items() if k in ids}
    pull['cost_classes'] = {k:v for k,v in pull['cost_classes'].items() if k in set(pull['job_classes'].values())}
    spec['memory_estimate_gb'] = {'empty': 2.}
    # Historical configuration profiles may omit phase.
    spec['configuration']['empty']['config'].pop('phase')
    _, root, _ = initialize(tmp_path, spec)
    identity = join(root, 'alpha', configure=False)
    snapshot = m.rpc(root, dict(op='inputs', phase='empty', configuration=True, **identity))
    measurement = dict(workers=2, threads=1, completed=2, wall_seconds=1., valid=True, round=0,
                       job_seconds=[.5,.5], class_peaks_gb={'empty': 2.4})
    request = dict(op='configure', phase='empty', input_sha256=snapshot['sha256'], measurements=[measurement], **identity)
    assert m.rpc(root, request)['workers'] == 2
    state = m.read_state(root)
    assert not state['observed_memory_gb']  # Configuration-only peak is not a scientific reservation.
    assert state['sessions'][identity['session']]['configuration']['empty'][0]['class_peaks_gb'] == {'empty': 2.4}
    # The coordinator's compact spec omits cost_classes; use its indexed store.
    toy_snapshot = m.rpc(root, dict(op='inputs', phase='toy', configuration=True, **identity))
    toy_request = dict(request, phase='toy', input_sha256=toy_snapshot['sha256'],
                       measurements=[dict(measurement, class_peaks_gb={'0': 1.2})])
    assert m.rpc(root, toy_request)['workers'] == 2
    assert m.read_state(root)['observed_memory_gb'] == {'0': 1.2}
    bad = deepcopy(request); bad['measurements'][0]['class_peaks_gb'] = {'foreign': 2.4}
    with pytest.raises(ValueError, match='invalid configuration memory class'): m.rpc(root, bad)
    bad = deepcopy(request); bad['measurements'][0]['class_peaks_gb'] = {'empty': -1.}
    with pytest.raises(ValueError, match='invalid configuration memory class'): m.rpc(root, bad)


def test_legacy_a4_actual_launch_all_phases_resume_with_synthetic_inputs(tmp_path):
    from test_v3_a13 import toy_original
    from v3 import table_validation_a4 as a4
    original, _, _, _, _, source, calibration, probe, tiny = toy_original(tmp_path)
    # Build an A4-style plan directly, so the configuration profiles omit phase.
    plan = a4.prepare(source, calibration, registration=None, wall_hours=48, a3_probe_root=probe, settings_override=tiny)
    for profile in plan['configuration'].values():
        profile.update(workers_local=[1], jobs_local=1, rounds=1)
    path = tmp_path/'legacy.json'; root = tmp_path/'legacy_run'
    a.atomic_json(path, a.seal(plan))
    s = dict(profile='local', workers=2, threads=1, cpu_budget=4, mode='normal')
    assert runner.launch(path, root, s)['complete']
    assert runner.launch(path, root, s)['complete']


def test_extension_and_a5_admission_from_synthetic_sealed_phases(tmp_path):
    from test_v3_a13 import toy_original
    from v3 import validation_extension_a13 as ext, table_labels_a5 as labels, tables_a10
    original, original_root, candidate, projection, inventory, source, cal_path, probe, tiny = toy_original(tmp_path)
    extension = ext.prepare(original, original_root, candidate, projection, inventory,
                            tmp_path/'extension_plan.json', rehearsal=True)
    target = tmp_path/'original_family.json'
    family = a.read(target)
    identity = dict(family_file_sha256=a.file_hash(target), table_seal_sha256=family['sha256'],
        receipt_file_sha256=a.file_hash(target.with_suffix('.compatibility.json')),
        sidecar_file_sha256=a.file_hash(target.with_suffix('.cell_results.json')), producing_commit='toy', code_hash=a.code_identity())
    identity_path = tmp_path/'family_identity.json'; a.atomic_json(identity_path, identity)
    label_plan = labels.prepare(target, original_root, original, source, cal_path, identity_path,
        wall_hours=1., a3_probe_root=probe, settings_override=tiny, instrument=tables_a10.NOMINAL)
    for plan in (extension, label_plan):
        before = a.digest(plan)
        estimates = wc.resources(plan)
        wc.require_memory_authority(wc.settings(settings()), None, estimates, {})
        for phase, profile in plan['configuration'].items():
            configs = profile.get('configs', [profile['config']])
            jobs = [a.stable_job(profile['kind'], cfg, 'configuration', i) for i,cfg in enumerate(configs)]
            mapped = wc.configuration_resources(jobs, plan['jobs'], estimates, phase=phase, spec=plan)
            assert all(r['memory_known'] and wc.reservation(r,{}) > 0 for r in mapped.values())
        assert a.digest(plan) == before


def test_stage1_five_run_families_admission_without_memory_does_not_invent_authority(monkeypatch):
    from v3 import tables_a10 as tables
    monkeypatch.setattr(a, 'verify_registration', lambda *args, **kwargs: None)
    plans = tables.stage1_run_specs('synthetic_calibration', 'synthetic_tables', {},
        {k:1 for k in ('main','k1p5','k2p3','weight_corner','horizon')})
    ordinary = wc.settings(dict(profile='local', workers=2, threads=1, cpu_budget=8, mode='normal'))
    override = wc.settings(settings())
    for plan in plans.values():
        before = a.digest(plan)
        estimates = wc.resources(plan)
        wc.require_memory_authority(ordinary, None, estimates, {})
        phase, = plan['phases']
        profile = plan['configuration'][phase]
        job = a.stable_job(profile['kind'], profile['config'], 'configuration', 0)
        matched = wc.configuration_resources([job], plan['jobs'], estimates, phase=phase, spec=plan)
        assert not matched[job['id']]['memory_known']
        with pytest.raises(ValueError, match='sealed memory'):
            wc.require_memory_authority(override, None, estimates, {})
        peaks = {r['memory_class']: 1. for r in estimates.values()}
        wc.require_memory_authority(override, None, estimates, peaks)
        assert a.digest(plan) == before


@pytest.mark.parametrize('explicit',[False,True])
def test_single_dispatch_work_normal_restores_slots(tmp_path,monkeypatch,explicit):
    from concurrent.futures import ThreadPoolExecutor
    from test_v3_worker_control import wait_until
    monkeypatch.setattr(runner,'mem_available_bytes',lambda:30_000_000_000)
    s=wc.settings(dict(profile='local',workers=7,threads=1,cpu_budget=8,mode='normal',
                       **({'override_reason':'explicit target'} if explicit else {})))
    root=tmp_path/'run'; phase=root/'toy'
    wc.initial_control(root,s)
    jobs=[a.stable_job('fixture',dict(phase='toy',seconds=.8),'validation',i) for i in range(40)]
    estimates={j['id']:dict(memory_class='toy',memory_gb=.25,memory_known=True,estimated_seconds=1.) for j in jobs}
    measured=[dict(workers=w,threads=1,completed=w,wall_seconds=1.,valid=True) for w in (1,3,6)]
    normal,work=(7,4) if explicit else (6,3)
    def status(): return a.read(phase/'status.json') if (phase/'status.json').exists() else {}
    def operator():
        wait_until(lambda:status().get('running')==normal)
        wc.control(root,s,mode='work')
        wait_until(lambda:status().get('selection',{}).get('workers')==work and status().get('running',99)<=work)
        wc.control(root,s,mode='normal')
        wait_until(lambda:status().get('selection',{}).get('workers')==normal and status().get('running')==normal)
    with ThreadPoolExecutor(1) as pool:
        task=pool.submit(operator)
        result=runner.dispatch(phase,jobs,a.code_identity(),s,time.time()+120,measurements=measured,control_root=root,job_resources=estimates)
        task.result()
    assert result['completed']==len(jobs)
    value=a.read(root/'control.json')
    assert value['max_workers']==7 and value.get('target_set',False)==explicit


def test_single_control_refuses_unknown_memory_without_mutation_then_uses_configuration_peak(tmp_path,monkeypatch):
    import sys
    s=wc.settings(dict(profile='local',workers=2,threads=1,cpu_budget=8,mode='normal'))
    job=a.stable_job('fixture',dict(phase='toy'),'validation',0)
    a.atomic_json(tmp_path/'manifest.json',a.seal(dict(jobs=[job])))
    a.atomic_json(tmp_path/'launches.json',[dict(settings=s)])
    wc.initial_control(tmp_path,s)
    before=(tmp_path/'control.json').read_bytes()
    monkeypatch.setattr(sys,'argv',['production_runner','control',str(tmp_path),'--workers','8','--reason','deliberate raise'])
    with pytest.raises(ValueError,match='sealed memory'): runner.main()
    assert (tmp_path/'control.json').read_bytes()==before
    assert not (tmp_path/'events.jsonl').exists()
    a.atomic_json(tmp_path/'launches.json',[dict(settings=s,configuration=dict(toy=[dict(class_peaks_gb={'toy':1.})]))])
    runner.main()
    value=a.read(tmp_path/'control.json')
    assert value['max_workers']==8 and wc.selection(s,value)['workers']==7


def test_pull_control_checks_memory_before_state_or_event_write(tmp_path,monkeypatch):
    from test_v3_multihost_a11 import initialize,join,spec_fixture
    from v3 import multihost_a11 as m
    _,root,_=initialize(tmp_path,spec_fixture())
    join(root,'alpha')
    prior=m.read_state(root)
    events={p.name:p.read_bytes() for p in (root/'protocol_events').glob('*.json')}
    monkeypatch.setattr(wc,'resources',lambda *args:{'toy':dict(memory_class='unknown',memory_known=False)})
    with pytest.raises(ValueError,match='sealed memory'):
        m.control(root,'alpha',max_workers=16,reason='deliberate raise')
    assert m.read_state(root)==prior and {p.name:p.read_bytes() for p in (root/'protocol_events').glob('*.json')}==events
    with m.transaction(root):
        c=m.Coordinator(root); c.state['observed_memory_gb']={'unknown':1.}; c.save(force=True)
    m.control(root,'alpha',max_workers=16,reason='measured raise')
    assert m.read_state(root)['host_controls']['alpha']['max_workers']==16


def test_proof_control_checks_memory_before_writing_or_spending(tmp_path,monkeypatch):
    from test_v3_compatibility_shards_a11 import prepared,ORIGINAL,FINGERPRINT
    from v3 import compatibility_a10 as c,host_a11 as host
    monkeypatch.setattr(proof,'verify_code',lambda commit:None)
    monkeypatch.setattr(proof.platform,'node',lambda:ORIGINAL)
    monkeypatch.setattr(host,'fingerprint',lambda:FINGERPRINT)
    monkeypatch.setattr(c,'RECORD_DIRECTORY',tmp_path/'reservations')
    path,plan,_,_=prepared(tmp_path,two=False)
    root=proof.host_directory(path,ORIGINAL)
    wc.initial_control(root,plan['hosts'][ORIGINAL]['settings'])
    a.atomic_json(root/'started.json',a.seal(dict(synthetic=True)))
    before=(root/'control.json').read_bytes()
    for item in plan['items'].values():
        item['resources'].update(memory_known=False,measured_memory_gb=0.)
    monkeypatch.setattr(proof,'load_attempt',lambda p:deepcopy(plan))
    with pytest.raises(ValueError,match='sealed memory'):
        proof.control_attempt(path,ORIGINAL,16,'deliberate raise')
    assert (root/'control.json').read_bytes()==before and not (root/'result.json').exists()
    for item in plan['items'].values(): item['resources']['measured_memory_gb']=1.
    assert proof.control_attempt(path,ORIGINAL,16,'measured raise')['max_workers']==16
    assert not (root/'result.json').exists()


def test_stale_unknown_control_clamps_runtime_under_alternate_policy(monkeypatch,tmp_path):
    monkeypatch.setattr(wc,'MODE_CAPS_TARGET',False)
    monkeypatch.setattr(proof,'memory_budget',lambda *args:10.)
    s=wc.settings(dict(profile='local',workers=4,threads=1,cpu_budget=4,mode='work',override_reason='stale target'))
    value=dict(mode='work',max_workers=4,worker_override=True,target_set=True)
    estimates={'job':dict(memory_class='toy',memory_known=False)}
    assert wc.memory_safe_selection(s,value,estimates,{},wc.selection(s,value))['workers']==1
    job=a.stable_job('fixture',dict(seconds=.01),'validation',0)
    item=dict(job=job,phase_root=str(tmp_path),producing_code_hash='0'*64,
              resources=dict(memory_class='toy',memory_known=False,memory_gb=.25,worker_seconds=1.))
    a.atomic_json(tmp_path/'control.json',value)
    fresh,trace=proof.run_items([item],4,10.,control_path=tmp_path/'control.json',host_settings=s)
    assert job['id'] in fresh and max(row['running'] for row in trace)==1


def test_legacy_proof_control_checks_copied_executor_authority(tmp_path,monkeypatch):
    import sys
    from v3 import compatibility_a10 as c
    target=tmp_path/'proof.json'; root=target.with_suffix('.workers')
    s=wc.settings(dict(profile='local',workers=1,threads=1,cpu_budget=8,mode='work'))
    a.atomic_json(root/'identity.json',dict(code_hash=a.code_identity(),target=str(target)))
    a.atomic_json(root/'settings.json',s)
    a.atomic_json(root/'memory_authority.json',dict(estimates={'job':dict(memory_class='toy',memory_known=False)},peaks={}))
    wc.initial_control(root,s)
    before=(root/'control.json').read_bytes()
    monkeypatch.setattr(sys,'argv',['compatibility_a10','control',str(target),'--workers','8','--reason','deliberate raise'])
    with pytest.raises(ValueError,match='sealed memory'): c.main()
    assert (root/'control.json').read_bytes()==before and not target.exists()
    authority=a.read(root/'memory_authority.json');authority['peaks']['toy']=1.
    a.atomic_json(root/'memory_authority.json',authority)
    assert c.main()==0
    assert a.read(root/'control.json')['max_workers']==8 and not target.exists()
