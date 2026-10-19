"""Item 10 review: short-trial RSS, independent profile gates, registered authority."""
from copy import deepcopy
from concurrent.futures import Future
from pathlib import Path
import time
import pytest
from test_v3_paths import tmp_path
from v3 import artifacts as a, worker_control as wc, production_runner as r
from v3 import compatibility_shards_a11 as proof, worker_safety as safety, multihost_a11 as m


def settings():
    return dict(profile='x2', workers=31, threads=1, cpu_budget=32, mode='normal', caps=r.caps('x2',32))


def measurements(n):
    return [dict(workers=n, threads=1, valid=True, completed=n, wall_seconds=1., job_seconds=[1.]*n)]


@pytest.mark.parametrize('kind', ['fixture', 'a4_validate'])
def test_uniform_full_class_does_not_cap_short_trials(tmp_path, monkeypatch, kind):
    s=settings(); profile=dict(kind=kind,config={}, workers_x2=[8,12,16,24,32],threads=[1],rounds=1,jobs_per_worker=1)
    source=a.stable_job(kind,{},'validation',0)
    resources={source['id']:dict(memory_class='full',memory_gb=15.,estimated_seconds=100.)}
    monkeypatch.setattr(r,'mem_available_bytes',lambda:20_000_000_000)
    seen=[]
    def dispatch(target,jobs,code,settings,deadline,**kw):
        values=kw['job_resources']; count=kw['fixed']['workers']; peaks=kw['measured_peaks']
        assert all(v['memory_class'].startswith('trial:') for v in values.values())
        assert max(wc.reservation(v,peaks) for v in values.values())==.25
        assert sum(wc.admission_charges(values,peaks)[0].values())<=16.
        seen.append(count)
        measured={v['memory_class']:.12 for v in values.values()}
        a.atomic_json(target/'memory_reservations.json',measured)
        return dict(maximum_active=count,completed=len(jobs),wall_seconds=1.)
    monkeypatch.setattr(r,'dispatch',dispatch)
    monkeypatch.setattr(r,'completed',lambda *args:dict(seconds=.1))
    data=r.configuration_test(tmp_path,'phase',profile,s,time.time()+60,1,job_resources=resources,source_jobs=[source])
    assert seen==[8,12,16,24,31]
    assert r.choose(data,31,32,1)['workers']==31>int(16/15)
    assert all('full' not in row['class_peaks_gb'] for row in data)
    peaks={}; trial=next(iter(wc.trial_resources([source]).values()))
    wc.observe(peaks,trial,1e9)
    assert wc.reservation(trial,peaks)==1.2


def simulated_proof(monkeypatch, tmp_path, items, limits, budget, target=31):
    clock=[0.]; active={}; admissions=[]
    class Pool:
        def __init__(self,*args): pass
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def submit(self,fn,item):
            future=Future(); active[future]=(clock[0]+item['duration'],item)
            admissions.append((clock[0],item['job']['id'],len(active)))
            return future
        def result(self,future):
            _,item=active.pop(future)
            return dict(after_sha256=a.digest(item['job']),_peak_rss_bytes=0)
    def wait(futures,**kw):
        clock[0]=min(active[f][0] for f in futures)
        return {f for f in futures if active[f][0]==clock[0]},set()
    monkeypatch.setattr(safety,'IsolatedPools',Pool)
    monkeypatch.setattr(proof,'wait',wait)
    monkeypatch.setattr(proof,'memory_budget',lambda *args:budget)
    a.atomic_json(tmp_path/'control.json',dict(mode='normal',max_workers=target))
    fresh,trace=proof.run_items(items,target,budget,host_settings=settings(),control_path=tmp_path/'control.json',
        measurements_by_profile={p:dict(measurements=measurements(n)) for p,n in limits.items()})
    return fresh,trace,admissions,clock[0]


def test_mixed_proof_profile_counts_load_sheet_and_tail(tmp_path, monkeypatch):
    # Long heavy jobs begin first. A profile choice of 3 must not leave the
    # other 28 slots empty, nor block heavy replacements behind light jobs.
    items=[]
    for p,count,duration,memory in [('heavy',9,10.,8.),('light',140,2.,.5)]:
        for n in range(count):
            job=a.stable_job('fixture',dict(profile=p),'validation',n)
            items.append(dict(job=job,profile_key=p,duration=duration,
                resources=dict(memory_class=p,memory_gb=memory,worker_seconds=duration)))
    limits=dict(heavy=3,light=28)
    fresh,trace,admissions,wall=simulated_proof(monkeypatch,tmp_path,items,limits,100.)
    starts={jid:t for t,jid,_ in admissions}
    assert len(fresh)==149 and max(t['running'] for t in trace)==31
    heavy=[i for i in items if i['profile_key']=='heavy']
    assert sorted(starts[i['job']['id']] for i in heavy)==[0.]*3+[10.]*3+[20.]*3
    assert wall==30.  # No wait for unrelated light jobs; only the own limit.
    estimates={i['job']['id']:dict(i['resources'],estimated_seconds=i['duration']) for i in items}
    sheet=wc.load_sheet([i['job'] for i in items],estimates,settings(),125.,
        job_profiles={i['job']['id']:i['profile_key'] for i in items},
        measurements_by_profile={p:measurements(n) for p,n in limits.items()})
    row=sheet['rules']['item10']
    assert row['class_wall_hours']*3600==wall
    assert row['initial_concurrent_workers']==31 and row['concurrent_workers']==31
    assert row['mean_concurrent_workers']==pytest.approx(sum(i['duration'] for i in items)/wall)
    assert row['tail_seconds']==10 and sheet['configuration_choices_known']


def test_near_target_mixed_shard_has_no_artificial_heavy_tail(tmp_path, monkeypatch):
    items=[]
    for p,count,seconds,memory in [('heavy',62,10.,3.),('light',124,5.,.5)]:
        for n in range(count):
            job=a.stable_job('fixture',dict(profile=p),'validation',n)
            items.append(dict(job=job,profile_key=p,duration=seconds,resources=dict(memory_class=p,memory_gb=memory,worker_seconds=seconds)))
    _,trace,admissions,wall=simulated_proof(monkeypatch,tmp_path,items,dict(heavy=31,light=31),112.)
    assert wall==40 and max(t['running'] for t in trace)==31
    # The unfinished top-quarter mean admits all 31 heavy jobs immediately.
    assert sum(t==0 for t,_,_ in admissions)==31
    assert sum(i['duration'] for i in items)/wall==31


def test_profile_choice_counts_only_own_jobs_and_host_still_binds():
    s=settings(); choices=measurements(3)
    assert wc.profile_slots(s,None,'heavy',['light']*28,choices)==3
    assert wc.profile_slots(s,None,'heavy',['light']*27+['heavy']*2,choices)==1
    assert wc.profile_slots(s,None,'heavy',['heavy']*3,choices)==0
    assert wc.profile_slots(s,None,'heavy',['light']*31,choices)==0


@pytest.mark.parametrize('kind', ['table','a4_fit','a4_validate','a4_census','a13_validate_plain_ext','a5_fvplain','rerun'])
def test_registered_launch_requires_memory_before_configuration_and_frozen_path_passes(tmp_path,monkeypatch,kind):
    job=a.stable_job(kind,dict(phase='stage'),'validation',0)
    spec=dict(registered=True,jobs=[job]);path=tmp_path/'spec.json'
    a.atomic_json(path,a.seal(spec))
    def reached(*args):raise RuntimeError('validated memory preflight reached')
    monkeypatch.setattr(r,'preflight_completion',lambda *args:None)
    monkeypatch.setattr(r,'validate_spec',reached)
    monkeypatch.setattr(r,'available_cpus',lambda:32)
    with pytest.raises(ValueError,match='freeze for pull dispatch first'):r.launch(path,tmp_path/'root',settings())
    assert not (tmp_path/'root').exists()
    frozen=deepcopy(spec);frozen['pull_dispatch']=dict(job_classes={job['id']:'sealed'},cost_classes={'sealed':dict(memory_gb=2.,worker_seconds=1.)})
    wc.require_registered_memory(True,wc.resources(frozen),{})
    # A single-host carried plan with a sealed phase estimate is also valid.
    spec['memory_estimate_gb']={'stage':2.};a.atomic_json(path,a.seal(spec))
    with pytest.raises(RuntimeError,match='validated memory preflight reached'):r.launch(path,tmp_path/'root',settings())
    absent=wc.resources(dict(jobs=[job]))
    wc.require_registered_memory(True,absent,{'stage':.7})
    wc.require_registered_memory(False,absent,{})


def test_trial_peaks_stay_separate_in_coordinator(tmp_path):
    from test_v3_multihost_a11 import initialize,spec_fixture,join
    _,root,spec=initialize(tmp_path,spec_fixture(),hosts=('alpha',))
    identity=join(root,'alpha',configure=False)
    snapshot=m.rpc(root,dict(op='inputs',phase='toy',configuration=True,**identity))
    profile=spec['configuration']['toy']; prototype=a.stable_job(profile['kind'],profile['config'],'configuration',0)
    key=wc.trial_resources([prototype])[prototype['id']]['memory_class']
    data=measurements(2); data[0]['class_peaks_gb']={key:.4}
    m.rpc(root,dict(op='configure',phase='toy',measurements=data,input_sha256=snapshot['sha256'],**identity))
    assert m.read_state(root).get('observed_memory_gb',{})=={}


def test_load_sheet_without_choices_is_explicitly_conditional():
    job=a.stable_job('fixture',{},'validation',0)
    estimates={job['id']:dict(memory_class='one',memory_gb=1.,estimated_seconds=1.)}
    sheet=wc.load_sheet([job],estimates,settings(),100.)
    assert not sheet['configuration_choices_known']
    assert 'Conditional' in sheet['projection_condition']


def test_real_short_trial_dispatch_exceeds_full_class_memory_cap(tmp_path,monkeypatch):
    from v3 import tables_a10 as tables
    s=dict(profile='local',workers=3,threads=1,cpu_budget=4,mode='normal',caps=r.caps('local',4))
    wc.initial_control(tmp_path,s)
    monkeypatch.setattr(r,'mem_available_bytes',lambda:5_000_000_000)
    cfg=dict(phase='toy',steps=2,model=dict(n_agents=8,carrying_capacity=80,instrument=tables.NOMINAL.declaration()))
    source=a.stable_job('rerun',cfg,'validation',0)
    profile=dict(kind='rerun',config=cfg,workers_local=[1,2,3],threads=[1],rounds=1,jobs_per_worker=1)
    data=r.configuration_test(tmp_path,'toy',profile,s,time.time()+60,1,
        source_jobs=[source],job_resources={source['id']:dict(memory_class='full',memory_gb=3.,estimated_seconds=100.)})
    assert max(row['workers'] for row in data)==s['caps']['configuration']>int(4/3)
    assert all(row['valid'] for row in data)
    # RSS can be unavailable on a platform. Never turn a missing measurement
    # into a purported observed peak; deterministic peak tests are above.
    assert all(key.startswith('trial:') for row in data for key in row['class_peaks_gb'])


@pytest.mark.parametrize('kind,category', [('a13_validate_plain_ext',None),('a5_fvplain',None)]+[('rerun',f) for f in ('main','k1p5','k2p3','weightcorner','horizon')])
def test_stage1_real_freeze_supplies_registered_memory(kind,category):
    from v3 import tables_a10 as tables
    cfg=dict(phase=category or 'stage')
    if category:
        cfg.update(category=category,model=dict(instrument=tables.NOMINAL.declaration()))
    else:
        cfg.update(a1_job=dict(config=dict(a10_family='nominal',kernel=dict(capability=1.),setting_name='fixture')),
                   route='plain',R_max=6)
    job=a.stable_job(kind,cfg,'validation',0)
    spec=dict(registered=True,registered_a10=True,instrument=tables.NOMINAL.declaration(),jobs=[job],
              wall_seconds=100,x2_equivalent_hours=1.,publication=None)
    with pytest.raises(ValueError,match='freeze for pull'):wc.require_registered_memory(True,wc.resources(spec),{})
    projection=a.seal(dict(per_phase_capability={k:dict(mean_worker_seconds=1.,memory_estimate_gb=2.) for k in m.cost_keys(job)}))
    frozen=m.freeze(spec,projection,code_commit='f'*40)
    assert frozen['jobs']==spec['jobs']
    assert wc.resources(frozen)[job['id']]['memory_gb']==2.
    wc.require_registered_memory(True,wc.resources(frozen),{})
