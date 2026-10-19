"""Synthetic worker targets, per-class memory and output-blind load sheets."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import threading
import time

import pytest
from test_v3_paths import tmp_path
from v3 import artifacts as a, worker_control as wc, production_runner as runner
from v3 import compatibility_shards_a11 as proof


def settings(workers=3, **extra):
    return dict(profile='local', workers=workers, threads=1, cpu_budget=8, mode='work', **extra)


def test_initial_override_reason_cpu_limit_and_metadata(monkeypatch):
    monkeypatch.setattr(runner, 'available_cpus', lambda: 16)
    with pytest.raises(ValueError, match='reason'): wc.settings(settings(5))
    s = wc.settings(settings(override_reason='operator chooses three', operator='test operator'))
    assert wc.selection(s, measurements=[dict(workers=1, threads=1, valid=True, completed=1, wall_seconds=1)])['workers'] == 3
    assert s['operator_override']['operator'] == 'test operator'
    assert s['operator_override']['epoch'] > 0
    with pytest.raises(ValueError, match='CPU'): wc.settings(settings(9, override_reason='too many'))
    for value in (.96, 0., float('nan')):
        with pytest.raises(ValueError, match='headroom'): wc.settings(settings(1, memory_headroom=value, override_reason='test'))
    with pytest.raises(ValueError, match='reason'): wc.settings(settings(1, memory_headroom=.95))
    assert wc.settings(settings(1, memory_headroom=.95, override_reason='approved'))['memory_headroom'] == .95


def test_persistent_raise_lower_zero_and_mode(tmp_path):
    s = settings(1)
    wc.control(tmp_path, s, workers=3, reason='raise')
    assert wc.selection(s, a.read(tmp_path / 'control.json'))['workers'] == 3
    wc.control(tmp_path, s, workers=0, reason='pause dispatch')
    assert wc.selection(s, a.read(tmp_path / 'control.json'))['workers'] == 0
    value = wc.control(tmp_path, s, workers=1, mode='normal')
    assert len(value['history']) == 3 and all(row['operator'] and row['epoch'] for row in value['history'])
    assert [row['workers'] for row in value['history']] == [3, 0, 1]
    with pytest.raises(ValueError, match='CPU'): wc.control(tmp_path, s, workers=9)


def test_registered_classes_ignore_phase_floor_and_peaks_are_own_class():
    jobs = [a.stable_job('fixture', {'phase':'toy'}, 'validation', i) for i in range(3)]
    spec = dict(jobs=jobs, memory_estimate_gb={'toy': 15}, pull_dispatch=dict(
        job_classes={j['id']:str(i) for i,j in enumerate(jobs)},
        cost_classes={str(i):dict(memory_gb=m, worker_seconds=1.) for i,m in enumerate((1., 2., 8.))}))
    r = wc.resources(spec); peaks = {}
    wc.observe(peaks, r[jobs[0]['id']], 2e9)
    assert [wc.reservation(r[j['id']], peaks) for j in jobs] == [2.4, 2., 8.]
    assert proof.resource_estimate(spec | {'code_hash':'x'}, jobs[0])['memory_gb'] == 1.


def test_per_class_packing_and_load_sheet(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'available_cpus', lambda: 16)
    jobs = [a.stable_job('fixture', {}, 'validation', i) for i in range(8)]
    estimates = {j['id']:dict(memory_class='big' if i<2 else 'small', memory_gb=3. if i<2 else .5,
                            estimated_seconds=10., measured_seconds=5.) for i,j in enumerate(jobs)}
    sheet = wc.load_sheet(jobs, estimates, settings(4, override_reason='pack'), 5.)
    assert sheet['planned_workers'] == 4 and sheet['memory_budget_gb'] == 4.
    assert sheet['projected_peak_memory_fraction'] <= .8
    assert sheet['measured_wall_hours'] == sheet['class_wall_hours'] / 2
    assert sorted(row['reservation_gb'] for row in sheet['classes']) == [.5, 3.]
    assert all(row['class_id'] not in ('big', 'small') for row in sheet['classes'])


def test_completion_peaks_reads_records_only(tmp_path, monkeypatch):
    jobs = [a.stable_job('fixture', {}, 'validation', i) for i in range(2)]
    resources = {j['id']:dict(memory_class=str(i),memory_gb=.25) for i,j in enumerate(jobs)}
    for i,j in enumerate(jobs):
        a.atomic_json(tmp_path / 'records' / (j['id']+'.json'), dict(job=j,status='complete',peak_rss_bytes=(i+1)*1e9))
    original = wc.read
    def records_only(path):
        assert Path(path).parent.name == 'records'
        return original(path)
    monkeypatch.setattr(wc,'read',records_only)
    assert wc.completion_peaks(tmp_path,jobs,resources) == {'0':1.2,'1':2.4}


def wait_until(check, timeout=30):
    end = time.monotonic()+timeout
    while time.monotonic()<end:
        if check(): return
        time.sleep(.02)
    raise AssertionError('synthetic control condition did not become ready')


def test_single_host_live_raise_lower_and_resume(tmp_path, monkeypatch):
    monkeypatch.setattr(runner,'mem_available_bytes',lambda:5_000_000_000)
    root = tmp_path / 'run'; phase=root/'toy'
    s = wc.settings(settings(1))
    a.atomic_json(root/'control.json',dict(mode='work',max_workers=1))
    jobs=[a.stable_job('fixture',dict(phase='toy',seconds=.3),'validation',i) for i in range(12)]
    resources={j['id']:dict(memory_class='small',memory_gb=.5,estimated_seconds=1.) for j in jobs}
    observed=[]
    def status():
        return a.read(phase/'status.json') if (phase/'status.json').exists() else {}
    def operator():
        wait_until(lambda:status().get('running',0)==1)
        wc.control(root,s,workers=3,reason='raise')
        wait_until(lambda:status().get('running',0)==3)
        wc.control(root,s,workers=1,reason='lower')
        observed.append(status()['running'])
    with ThreadPoolExecutor(1) as pool:
        task=pool.submit(operator)
        result=runner.dispatch(phase,jobs,a.code_identity(),s,time.time()+60,
                              measurements=[dict(workers=1,threads=1,valid=True,completed=1,wall_seconds=1)],
                              control_root=root,job_resources=resources)
        task.result()
    assert result['completed']==12 and result['maximum_active']==3 and observed[0]>=1
    assert a.read(root/'control.json')['max_workers']==1
    again=runner.dispatch(phase,jobs,a.code_identity(),s,time.time()+60,
                         measurements=[dict(workers=1,threads=1,valid=True,completed=1,wall_seconds=1)],
                         control_root=root,job_resources=resources)
    assert again['completed']==12 and again['maximum_active']==0
    events=[json.loads(line) for line in (phase/'events.jsonl').read_text().splitlines()]
    assert not any(e['event'] in ('restart','restart_required') for e in events)
    assert all(e['reserved_memory_gb']<=e['memory_budget_gb'] for e in events if e['event']=='dispatch')


def test_loopback_live_host_and_overall_targets_persist(tmp_path):
    from test_v3_multihost_a11 import initialize, join, ready, claim, finish, spec_fixture
    from v3 import multihost_a11 as m
    _,root,_=initialize(tmp_path,spec_fixture(14),hosts=('alpha','beta'))
    first=join(root,'alpha'); second=join(root,'beta')
    ready(root,first,'toy'); ready(root,second,'toy')
    m.control(root,'alpha',max_workers=3,reason='add a slot')
    m.control(root,max_workers=3,reason='whole launch')
    leases=[claim(root,first) for _ in range(3)]
    assert all(l.get('job') for l in leases) and not claim(root,second).get('job')
    m.control(root,'alpha',max_workers=1,reason='drain to one')
    assert not claim(root,first).get('job')
    finish(root,first,leases.pop()); assert not claim(root,first).get('job')
    finish(root,first,leases.pop()); assert not claim(root,first).get('job')
    finish(root,first,leases.pop()); assert claim(root,first).get('job')
    with m.transaction(root):
        c=m.Coordinator(root); c.start(); c.save()
    value=m.read_state(root)
    assert value['control']['max_workers']==3
    assert value['host_controls']['alpha']['max_workers']==1
    assert value['host_controls']['alpha']['history'][-1]['reason']=='drain to one'


def test_proof_shard_live_targets_preserve_selection_and_finality(tmp_path, monkeypatch):
    from test_v3_compatibility_shards_a11 import source_fixture, hosts, ORIGINAL, FINGERPRINT
    from v3 import compatibility_a10 as c, host_a11 as host
    monkeypatch.setattr(proof,'verify_code',lambda commit:None)
    monkeypatch.setattr(proof.platform,'node',lambda:ORIGINAL)
    monkeypatch.setattr(host,'fingerprint',lambda:FINGERPRINT)
    monkeypatch.setattr(c,'RECORD_DIRECTORY',tmp_path/'reservations')
    sources,reasons=source_fixture(tmp_path,seconds=1.5)
    target=tmp_path/'proof.json'; path=target.with_suffix('.attempt.json')
    plan=proof.freeze(sources,reasons,target,hosts(False),'f'*40)
    proof.stage(path,ORIGINAL)
    root=proof.host_directory(path,ORIGINAL)
    monkeypatch.setattr(proof,'configure_host',lambda *args:dict(fixture=dict(chosen={'workers':1},class_peaks_gb={})))
    def status():
        return a.read(root/'scheduling.json') if (root/'scheduling.json').exists() else {}
    def operator():
        wait_until(lambda:status().get('running')==1)
        proof.control_attempt(path,ORIGINAL,3,'add two')
        wait_until(lambda:status().get('running')==3)
        proof.control_attempt(path,ORIGINAL,0,'pause without interrupting')
        wait_until(lambda:status().get('running')==0 and status().get('pending',0)>0)
        proof.control_attempt(path,ORIGINAL,2,'continue')
    with ThreadPoolExecutor(1) as pool:
        task=pool.submit(operator)
        result=proof.run_shard(path,ORIGINAL,workers=1,override_reason='initial one',operator='test operator')
        task.result()
    assert result['passed'] and all(row['passed'] for row in result['proofs'])
    assert result['job_ids']==plan['assignments'][ORIGINAL]
    assert [r['workers'] for r in result['worker_control']['history']]==[1,3,0,2]
    assert result['settings']['operator_override']['reason']=='initial one'
    assert max(row['running'] for row in result['admission'])==3
    assert all(row['running_gb']<=row['budget_gb'] for row in result['admission'])
    assert proof.combine(path)['passed']
    with pytest.raises(ValueError,match='final'): proof.run_shard(path,ORIGINAL)


def test_actual_loopback_hosts_obey_live_targets(tmp_path):
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor
    from test_v3_multihost_a11 import initialize, spec_fixture, SETTINGS, FINGERPRINT
    from v3 import multihost_a11 as m, host_a11 as h
    spec=spec_fixture(40,seconds=.5)
    from v3 import tables_a10 as tables
    cfg=dict(phase='toy',steps=2,model=dict(n_agents=8,carrying_capacity=80,instrument=tables.NOMINAL.declaration()))
    spec['jobs']=[a.stable_job('rerun',cfg,'validation',i) for i in range(40)]
    spec['pull_dispatch']['job_classes']={j['id']:str(i) for i,j in enumerate(spec['jobs'])}
    spec['configuration']['toy'].update(kind='rerun',config=cfg)
    spec['pull_dispatch']['lease_seconds']=6.
    spec['configuration']['toy']['workers_local']=[1]
    _,root,spec=initialize(tmp_path,spec)
    def active(host):
        with m.transaction(root):
            return len([l for l in m.Coordinator(root).active() if l['host']==host])
    with ProcessPoolExecutor(max_workers=2,mp_context=mp.get_context('spawn')) as pool:
        futures=[pool.submit(h.run_host,h.Loopback(root),tmp_path/name,dict(SETTINGS,workers=1),
                            host=name,environment=FINGERPRINT,max_seconds=100) for name in ('alpha','beta')]
        wait_until(lambda:active('alpha')==1 and active('beta')==1)
        m.control(root,'alpha',max_workers=3,reason='raise')
        m.control(root,max_workers=4,reason='overall ceiling')
        wait_until(lambda:active('alpha')==3)
        m.control(root,'alpha',max_workers=0,reason='stop new work')
        m.control(root,max_workers=2,reason='lower overall')
        wait_until(lambda:active('alpha')==0)
        m.control(root,'alpha',max_workers=2,reason='resume dispatch')
        m.control(root,max_workers=3,reason='add overall slot')
        for future in futures: future.result(timeout=110)
    assert m.rpc(root,{'op':'inspect'})['status']['complete']
    assert all(not a.read(tmp_path/name/'host_exit.json')['error'] for name in ('alpha','beta'))


@pytest.mark.parametrize('memory,expected',[(.5,4),(3.,1)])
def test_initial_override_still_obeys_per_class_memory(tmp_path,monkeypatch,memory,expected):
    monkeypatch.setattr(runner,'mem_available_bytes',lambda:5_000_000_000)
    s=wc.settings(settings(4,override_reason='use all four CPUs'))
    a.atomic_json(tmp_path/'control.json',dict(mode='work',max_workers=4))
    jobs=[a.stable_job('fixture',dict(seconds=.2),'validation',i) for i in range(6)]
    resources={j['id']:dict(memory_class='class',memory_gb=memory,estimated_seconds=1.) for j in jobs}
    result=runner.dispatch(tmp_path/'phase',jobs,a.code_identity(),s,time.time()+60,control_root=tmp_path,
        measurements=[dict(workers=1,threads=1,valid=True,completed=1,wall_seconds=1.)],job_resources=resources)
    assert result['completed']==6 and result['maximum_active']==expected


def test_resume_preserves_live_target_until_new_initial_override(tmp_path):
    first = wc.settings(settings(1))
    wc.initial_control(tmp_path, first)
    wc.control(tmp_path, first, workers=3, reason='live raise')
    wc.initial_control(tmp_path, first)
    assert wc.selection(first, a.read(tmp_path/'control.json'))['workers'] == 3
    newer = wc.settings(settings(2, override_reason='new initial target', operator='operator'))
    value = wc.initial_control(tmp_path, newer)
    assert value['max_workers'] == 2 and len(value['history']) == 2
    assert value['initial_override']['operator'] == 'operator'


def test_distributed_load_sheet_counts_each_job_once_and_remote_cpu(monkeypatch):
    monkeypatch.setattr(runner, 'available_cpus', lambda: 2)
    jobs = [a.stable_job('fixture', {}, 'validation', i) for i in range(9)]
    estimates = {j['id']:dict(memory_class='small', memory_gb=.5, estimated_seconds=10., measured_seconds=5.) for j in jobs}
    host_settings = dict(profile='x2', workers=32, threads=1, cpu_budget=32, mode='work', override_reason='capacity forecast')
    hosts = {name:dict(settings=host_settings, memory_gb=16., rate=rate) for name,rate in [('first',1.),('second',2.)]}
    sheets = wc.distributed_load_sheet(jobs, estimates, hosts)
    assert sum(s['forecast_jobs'] for s in sheets.values()) == 9
    assert sum(s['total_worker_hours'] for s in sheets.values()) == 90/3600
    assert all(s['planned_workers']==31 and s['projected_peak_memory_fraction']<=.8 for s in sheets.values())
    assert all(s['measured_wall_hours'] is not None for s in sheets.values())


def test_configuration_heartbeat_mirrors_live_target(tmp_path):
    from v3.host_a11 import Client
    class Transport:
        def call(self, request):
            return dict(control=dict(mode='work',max_workers=0,worker_override=True),status={})
    client=Client(Transport(),'toy','session',.03)
    thread=threading.Thread(target=client.watch,args=(tmp_path,))
    thread.start()
    try:
        wait_until(lambda:(tmp_path/'control.json').exists())
        value=a.read(tmp_path/'control.json')
        assert value['worker_override'] and value['max_workers']==0
        assert wc.selection(settings(1),value,fixed=dict(workers=4,threads=1))['workers']==0
    finally:
        client.stop.set(); thread.join()


def test_load_sheet_uses_only_completion_timing_and_rss(tmp_path, monkeypatch):
    jobs=[a.stable_job('fixture',dict(phase='toy'),'validation',i) for i in range(2)]
    estimates={j['id']:dict(memory_class=str(i),memory_gb=.25,estimated_seconds=10.) for i,j in enumerate(jobs)}
    for i,j in enumerate(jobs):
        a.atomic_json(tmp_path/'toy/records'/(j['id']+'.json'),dict(job=j,status='complete',worker_seconds=2.+i,peak_rss_bytes=(i+1)*1e9))
    original=wc.read
    def only_metadata(path):
        assert Path(path).parent.name=='records'
        return original(path)
    monkeypatch.setattr(wc,'read',only_metadata)
    measured,peaks=wc.completion_measurements(tmp_path,jobs,estimates)
    assert peaks=={'0':1.2,'1':2.4}
    assert [measured[j['id']]['measured_seconds'] for j in jobs]==[2.,3.]


def test_legacy_phase_maximum_does_not_become_every_jobs_class():
    values=dict(groups=32,particles=128,runs_per_group=64,burn=1024,measure=2048)
    jobs=[a.stable_job('table',dict(phase='table',settings=dict(values,particles=n),kernel={'capability':1.}), 'validation',i) for i,n in enumerate((128,512))]
    spec=dict(schema='v3-A10-estimation-1',jobs=jobs,memory_estimate_gb={'table':99.})
    resources=wc.resources(spec)
    small,big=[resources[j['id']] for j in jobs]
    assert big['memory_gb']==4*small['memory_gb'] and big['memory_gb']<99.
    assert big['memory_class']!=small['memory_class']
    peaks={};wc.observe(peaks,big,20e9)
    assert wc.reservation(small,peaks)==99.  # No peak for this class: retain its sealed fallback.
    assert wc.reservation(big,peaks)==24.
    sheet=wc.load_sheet(jobs,resources,settings(1),100.)
    assert sheet['class_wall_hours'] is None  # No invented one-second cost rate.


def test_coordinator_initial_override_and_resumed_overall_target(tmp_path):
    from test_v3_multihost_a11 import initialize, spec_fixture, SETTINGS, FINGERPRINT, ready
    from v3 import multihost_a11 as m
    path,root,_=initialize(tmp_path,spec_fixture(24))
    request=dict(op='join',host='alpha',fingerprint=FINGERPRINT,code_hash=a.code_identity(),code_commit='fixture',settings=dict(SETTINGS,workers=16))
    with pytest.raises(ValueError,match='reason'): m.rpc(root,request)
    request['settings']['override_reason']='operator chooses CPU limit'
    joined=m.rpc(root,request)
    identity=dict(host='alpha',session=joined['session'])
    snapshot=m.rpc(root,dict(identity,op='inputs',phase='toy',configuration=True))
    chosen=m.rpc(root,dict(identity,op='configure',phase='toy',input_sha256=snapshot['sha256'],measurements=[
        dict(workers=2,threads=1,completed=2,wall_seconds=1.,valid=True,round=0,job_seconds=[.5,.5])]))
    assert chosen['workers']==12
    ready(root,identity,'toy')
    result=m.rpc(root,dict(identity,op='claim',request_id='sixteen',max_jobs=16,memory_available_gb=40.))
    assert len(result['claims'])==12
    assert m.read_state(root)['sessions'][joined['session']]['settings']['operator_override']['epoch']
    m.prepare(path,root,dict(SETTINGS,workers=4,overall_workers=4,override_reason='new overall target'))
    assert m.read_state(root)['control']['max_workers']==4
    m.control(root,max_workers=2,reason='live overall reduction')
    m.prepare(path,root,SETTINGS)
    assert m.read_state(root)['control']['max_workers']==2


def test_nondeterminism_recheck_waits_for_live_pause(tmp_path):
    job=a.stable_job('fixture',dict(phase='toy'),'validation',0)
    s=wc.settings(settings(1));code=a.code_identity()
    a.atomic_json(tmp_path/'manifest.json',a.seal(dict(jobs=[job])))
    a.atomic_json(tmp_path/'launches.json',[dict(settings=s)])
    a.atomic_json(tmp_path/'budget.json',dict(deadline_epoch=time.time()+30))
    runner.worker(str(tmp_path/'toy'),job,code,1,False,None)
    wc.control(tmp_path,s,workers=0,reason='pause before check')
    def resume():
        time.sleep(.2)
        assert not (tmp_path/'_nd_toy').exists()
        wc.control(tmp_path,s,workers=1,reason='continue check')
    with ThreadPoolExecutor(1) as pool:
        task=pool.submit(resume)
        assert runner.nondeterminism_check(tmp_path/'toy',[job])['matched']
        task.result()



def test_historical_phase_derived_class_is_reconstructed_without_plan_edit():
    from copy import deepcopy
    values=dict(groups=32,particles=256,runs_per_group=64,burn=1024,measure=2048)
    jobs=[a.stable_job('table',dict(phase='table',settings=dict(values,particles=n),kernel={'capability':1.}), 'validation',i) for i,n in enumerate((256,512))]
    maximum=wc.arithmetic_class(dict(schema='v3-A10-estimation-1'),jobs[1])[1]
    spec=dict(schema='v3-A10-estimation-1',code_hash='old',jobs=jobs,memory_estimate_gb={'table':maximum},pull_dispatch=dict(
        job_classes={j['id']:str(i) for i,j in enumerate(jobs)},cost_classes={str(i):dict(memory_gb=maximum,worker_seconds=10.) for i in range(2)}))
    original=deepcopy(spec)
    resources=wc.resources(spec)
    assert resources[jobs[0]['id']]['memory_gb']==maximum/2
    assert resources[jobs[1]['id']]['memory_gb']==maximum
    assert wc.reservation(resources[jobs[0]['id']], {})==maximum
    assert proof.resource_estimate(spec,jobs[0])['memory_gb']==maximum
    assert spec==original
    # New explicit stratum estimates are authoritative even if equal to a phase maximum.
    spec['pull_dispatch']['memory_basis']='registered-stratum'
    assert wc.resources(spec)[jobs[0]['id']]['memory_gb']==maximum



def test_census_memory_uses_declared_source_groups():
    values=dict(groups=2,particles=256,runs_per_group=64,burn=1024,measure=2048)
    source=a.stable_job('table',dict(settings=values,kernel={'capability':1.}),'validation',0)
    job=a.stable_job('a4_census',dict(phase='census',route='plain',a1_job=source),'validation',0)
    _,memory=wc.arithmetic_class(dict(schema='v3-A4-validation-1'),job)
    assert memory==pytest.approx(6.7*2*64*519/(32*256*3072))


def test_local_configuration_override_exceeds_default_twelve(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'available_cpus', lambda: 32)
    monkeypatch.setattr(runner, 'mem_available_bytes', lambda: 100_000_000_000)
    s=wc.settings(dict(profile='local',workers=24,threads=1,cpu_budget=32,mode='work',
                       override_reason='operator chooses twenty-four'))
    seen=[]
    def dispatch(root,jobs,code,settings,deadline,**kwargs):
        seen.append(kwargs['fixed']['workers'])
        assert kwargs['fixed']['workers']<=settings['cpu_budget']
        return dict(maximum_active=kwargs['fixed']['workers'],completed=len(jobs),wall_seconds=1.)
    monkeypatch.setattr(runner,'dispatch',dispatch)
    monkeypatch.setattr(runner,'completed',lambda *args:dict(seconds=1.))
    profile=dict(kind='fixture',config={},workers_local=[1,12],jobs_local=32,rounds=1)
    measurements=runner.configuration_test(tmp_path,'toy',profile,s,time.time()+60,0)
    assert 24 in seen and all(row['valid'] for row in measurements)


def test_load_sheet_preserves_default_pilot_ceiling_and_reasoned_override(monkeypatch):
    monkeypatch.setattr(runner,'available_cpus',lambda:32)
    job=a.stable_job('fixture',{},'validation',0)
    resources={job['id']:dict(memory_class='small',memory_gb=.25,estimated_seconds=1.)}
    s=dict(profile='x2',workers=24,threads=1,cpu_budget=32,mode='work')
    ordinary=wc.load_sheet([job],resources,s,100.,default_cap=16)
    override=wc.load_sheet([job],resources,dict(s,override_reason='operator target'),100.,default_cap=16)
    assert ordinary['planned_workers']==16 and 'default ceiling' in ordinary['binding_cap']
    assert override['planned_workers']==24 and override['binding_cap']=='mode/operator target'
