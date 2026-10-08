"""P2 selection, full-length costing, pooled dispatch and measured projection."""
from copy import deepcopy
import json
import time
from types import SimpleNamespace

import pytest

from test_v3_paths import tmp_path
from v3 import pilot_a10 as pilot
from v3 import production_runner as runner
from v3.artifacts import atomic_json, code_identity, file_hash, read, seal, stable_job
from v3.instrument import Instrument
from v3.offline_estimator import settings_for


@pytest.fixture
def population(monkeypatch):
    """Even-sized capability lists exercise the lower-median convention."""
    paths = {f: ['v3/runs/registered/v3_rerun_calibration.json', 'table'] for f in pilot.FAMILIES}
    def tables(family, calibration):
        caps = (1., 2., 3., 5.) if family in pilot.FAMILIES[:3] else (1., 2.25, 5.)
        return [stable_job('table', {'a10_family': family, 'calibration_path': calibration,
                'kernel': {'capability': cap, 'reproduction_rate': .064,
                           'instrument': Instrument('A10', 1.8, 'sqrt' if family == 'sqrt' else 'linear').declaration()},
                'setting_name': setting, 'settings': settings_for(setting), 'rule_id': rule, 'route': 'auto'}, 'v3_tables', 0)
                for cap in caps for setting in ('primary', 'double_population', 'double_length')
                for rule in ('balanced', 'other')]
    categories = [('R1','linear',1.8), ('R2','linear',1.8), ('a10_arm','linear',1.5),
                  ('a10_arm','linear',2.3), ('a10_arm','sqrt',1.8), ('a6_crowding','linear',1.8),
                  ('a6_horizon','linear',1.8), ('a6_sigma_squared_x0.1','linear',1.8),
                  ('a6_sigma_squared_x10','linear',1.8), ('a6_weight_corner','linear',1.8),
                  ('refinement','linear',1.8)]
    runs = [stable_job('rerun', {'category': category, 'calibration_path':paths['nominal'][0],
            'steps':1000 if category=='a6_horizon' else 500,
            'model': {'instrument':Instrument('A10', k, g).declaration()}}, 'v3_rerun', 0)
            for category,g,k in categories]
    monkeypatch.setattr(pilot, 'build_jobs', tables)
    monkeypatch.setattr(pilot, 'paired_runs', lambda *a: runs[:2])
    monkeypatch.setattr(pilot, 'arm_runs', lambda *a: runs[2:5])
    monkeypatch.setattr(pilot, 'a6_runs', lambda *a: runs[5:])
    return paths


@pytest.fixture
def spec(population):
    return pilot.make_spec(population, scope='reduced')


def test_selection_counts_full_populations_and_unmodified_jobs(population, spec):
    full = pilot.make_spec(population)
    assert len(spec['jobs']) == 77
    assert spec['wall_seconds'] == 43200 and spec['phases'] == ['pooled']
    assert list(spec['configuration']) == ['pooled']
    assert spec['selection']['selected_capabilities']['nominal'] == [1.,2.,5.]
    assert spec['selection']['medians']['nominal'] == 2.
    assert spec['selection']['selected_capabilities']['sigma_squared_x10'] == [1.,2.25,5.]
    full_jobs = {j['id']:j for j in full['jobs']}
    assert all(j == full_jobs[j['id']] for j in spec['jobs'])
    for family in pilot.FAMILIES:
        for kind in ('estimate','validate_plain','validate_fv','labels'):
            count = sum(spec['strata'][j['config']['phase']]['family']==family and j['config']['cost_kind']==kind for j in spec['jobs'])
            assert count == (5 if family=='nominal' and kind!='labels' else 3)
    assert sum(j['config']['cost_kind']=='run' for j in spec['jobs'])==11
    assert set(spec['strata']) == set(full['strata'])
    for phase,s in spec['strata'].items():
        assert len(s['population_source_ids']) == s['population_jobs']
        assert s['population_sha256']==full['strata'][phase]['population_sha256']
        assert len(s['selected_source_ids']) == int(s['sampled'])
        assert set(s['selected_source_ids']) <= set(s['population_source_ids'])
    estimates=spec['pooled_job_estimates']
    assert spec['jobs']==sorted(spec['jobs'],key=lambda j:(-estimates[j['id']]['estimated_seconds'],j['id']))
    assert full == pilot.make_spec(population, scope='full')
    assert 'scope' not in full and full['wall_seconds']==10800
    assert len(full['phases'])==len(full['strata'])


@pytest.mark.parametrize('args',[{'scope':'other'},{'scope':'reduced','samples':2}])
def test_invalid_scope_or_sample_count(population,args):
    with pytest.raises(ValueError):
        pilot.make_spec(population,**args)


@pytest.mark.parametrize('kind',['estimate','validate_plain','validate_fv','labels'])
def test_cost_samples_execute_full_declared_lengths(spec,monkeypatch,kind):
    from v3 import offline_estimator, table_validation_a4, table_labels_a5, context, calibration
    job=next(j for j in spec['jobs'] if j['config']['cost_kind']==kind)
    expected=deepcopy(job['config']['source_job']['config']['settings'])
    seen=[]
    def estimate(config,*a):
        seen.append(config['settings'])
        return {'rows':[], 'trajectory_seconds':1.,'scoring_seconds_by_k_star':{'1.8':.1}}
    def stage(*a):
        seen.append(a[-1])
        return {}
    monkeypatch.setattr(calibration,'load_calibration',lambda *a,**k:{})
    monkeypatch.setattr(offline_estimator,'estimate',estimate)
    for name in ('fit_stage','validate_stage','census_stage'):
        monkeypatch.setattr(table_validation_a4,name,stage)
    monkeypatch.setattr(table_labels_a5,'fvplain_stage',stage)
    monkeypatch.setattr(context.Context,'build',lambda *a:SimpleNamespace(parameters=SimpleNamespace(extinction_flow=-1.,upper_bound=1.)))
    result=pilot.execute_cost(job)
    assert seen[0]==expected and all(v is None or v=={} for v in seen[1:])
    assert result['length_fraction']==1. and not result['configuration_test']
    assert job['config']['source_job']['config']['settings']==expected


def settings(workers=3):
    return {'profile':'local','workers':workers,'threads':1,'cpu_budget':16,'mode':'work','caps':runner.caps('local',16)}


def control(root):
    atomic_json(root/'control.json',{'mode':'work','max_workers':12,'stop_dispatch':False,'interrupt_now':False})


def choices():
    return [{'workers':w,'threads':1,'completed':w,'wall_seconds':1.,'valid':True,'job_seconds':[1.]*w} for w in (1,2,3)]


def test_twelve_hour_exception_is_only_reduced_a10(spec,population,monkeypatch):
    monkeypatch.setattr(runner,'available_cpus',lambda:16)
    runner.validate_spec(spec,settings())
    bad=deepcopy(spec);bad['wall_seconds']=43201
    with pytest.raises(ValueError,match='twelve hours'):
        runner.validate_spec(bad,settings())
    for schema in ('v3-A10-cost-pilot-1','another-pilot','v3-A10-estimation-1'):
        bad=pilot.make_spec(population);bad.update(schema=schema,wall_seconds=10801)
        if schema!='v3-A10-cost-pilot-1':
            bad['scope']='reduced'
        with pytest.raises(ValueError,match='three hours'):
            runner.validate_spec(bad,settings())
        bad['wall_seconds']=10800
        runner.validate_spec(bad,settings())
    bad=deepcopy(spec);bad['registered']=True
    with pytest.raises(ValueError,match='non-registered cost'):
        runner.validate_spec(bad,settings())


def test_pooled_individual_memory_and_longest_feasible_first(tmp_path,monkeypatch):
    monkeypatch.setattr(runner,'mem_available_bytes',lambda:5_000_000_000)
    control(tmp_path)
    jobs=[stable_job('fixture',{'seconds':.25},'validation',i) for i in range(5)]
    costs={j['id']:{'memory_gb':m,'estimated_seconds':9-i,'memory_class':str(i)}
           for i,(j,m) in enumerate(zip(jobs,[3.,3.,1.,1.,1.]))}
    result=runner.dispatch(tmp_path,jobs,code_identity(),settings(),time.time()+45,measurements=choices(),pooled_jobs=costs)
    assert result['completed']==5 and 2<=result['maximum_active']<=3
    events=[json.loads(s) for s in (tmp_path/'events.jsonl').read_text().splitlines()]
    dispatched=[e for e in events if e['event']=='dispatch']
    assert [e['job'] for e in dispatched[:2]] == [jobs[0]['id'],jobs[2]['id']]
    assert all(e['reserved_memory_gb']<=4. and e['active']<=3 for e in dispatched)
    assert set(read(tmp_path/'job_status.json').values())=={'complete'}
    assert all(runner.completed(tmp_path,j,code_identity())['runtime']['threads_verified'][0]['effective']==1 for j in jobs)


def fake_processes(monkeypatch):
    class Process:
        counter=900000
        def __init__(self,target,args):
            self.target,self.args=target,args
            Process.counter+=1; self.pid=Process.counter
        def start(self): self.target(*self.args)
        def is_alive(self): return False
        def join(self,*a): pass
    monkeypatch.setattr(runner.mp,'get_context',lambda *a:SimpleNamespace(Process=Process))


def test_pool_worker_ceiling_and_peak_memory_reductions(tmp_path,monkeypatch):
    fake_processes(monkeypatch)
    monkeypatch.setattr(runner,'mem_available_bytes',lambda:100_000_000_000)
    monkeypatch.setattr(runner,'peak_rss_bytes',lambda:1_000_000_000)
    control(tmp_path)
    jobs=[stable_job('fixture',{'seconds':0},'validation',i) for i in range(20)]
    costs={j['id']:{'memory_gb':1.,'estimated_seconds':20-i,'memory_class':'fixture'} for i,j in enumerate(jobs)}
    large={**settings(),'workers':32,'cpu_budget':32,'caps':runner.caps('x2',32)}
    result=runner.dispatch(tmp_path,jobs,code_identity(),large,time.time()+45,fixed={'workers':32,'threads':1},pooled_jobs=costs)
    assert result['maximum_active']==16 and result['completed']==20
    root=tmp_path/'peaks';control(root)
    monkeypatch.setattr(runner,'mem_available_bytes',lambda:5_000_000_000)
    monkeypatch.setattr(runner,'peak_rss_bytes',lambda:3_000_000_000)
    result=runner.dispatch(root,jobs[:5],code_identity(),settings(2),time.time()+45,measurements=choices(),pooled_jobs=costs)
    dispatched=[json.loads(s) for s in (root/'events.jsonl').read_text().splitlines() if json.loads(s)['event']=='dispatch']
    assert [e['active'] for e in dispatched[:2]]==[1,2]
    assert all(e['active']==1 and e['memory_estimate_gb']==3. for e in dispatched[2:])
    assert read(root/'pool_memory.json')=={'fixture':3.}


def test_pooled_deadline_resume_and_worker_count_determinism(tmp_path,monkeypatch):
    monkeypatch.setattr(runner,'mem_available_bytes',lambda:8_000_000_000)
    control(tmp_path)
    jobs=[stable_job('fixture',{'seconds':.2},'validation',i) for i in range(4)]
    costs={j['id']:{'memory_gb':1.,'estimated_seconds':4-i,'memory_class':'fixture'} for i,j in enumerate(jobs)}
    code=code_identity()
    runner.dispatch(tmp_path,jobs[:1],code,settings(2),time.time()+30,measurements=choices(),pooled_jobs=costs)
    path=tmp_path/'outputs'/(jobs[0]['id']+'.json'); preserved=file_hash(path)
    interrupted=runner.dispatch(tmp_path,jobs,code,settings(2),time.time()+.1,measurements=choices(),pooled_jobs=costs)
    assert interrupted['reason']=='deadline' and interrupted['completed']==1
    assert len(interrupted['not_completed_ids'])==3
    assert list(read(tmp_path/'job_status.json').values()).count('not completed')==3
    resumed=runner.dispatch(tmp_path,list(reversed(jobs)),code,settings(3),time.time()+30,measurements=choices(),pooled_jobs=costs)
    assert resumed['completed']==4 and file_hash(path)==preserved
    repeated=runner.dispatch(tmp_path,jobs,code,settings(2),time.time()+30,measurements=choices(),pooled_jobs=costs)
    assert repeated['completed']==4 and repeated['selection']['workers']==2
    other=tmp_path/'two_workers';control(other)
    runner.dispatch(other,jobs,code,settings(2),time.time()+30,measurements=choices(),pooled_jobs=costs)
    assert [runner.completed(tmp_path,j,code)['result'] for j in jobs]==[runner.completed(other,j,code)['result'] for j in jobs]


def test_late_worker_has_no_completion_record(tmp_path):
    job=stable_job('fixture',{'seconds':0},'validation',0)
    runner.worker(str(tmp_path),job,code_identity(),1,False,None,time.time()-1)
    assert runner.completed(tmp_path,job,code_identity()) is None


def test_pool_keeps_live_mode_drain_and_resume(tmp_path,monkeypatch):
    import test_v3_b2_runner as baseline
    monkeypatch.setattr(runner,'mem_available_bytes',lambda:10_000_000_000)
    original=runner.dispatch
    def pooled(root,jobs,*args,**kwargs):
        kwargs['pooled_jobs']={j['id']:{'memory_gb':1.,'estimated_seconds':1.,'memory_class':'fixture'} for j in jobs}
        return original(root,jobs,*args,**kwargs)
    monkeypatch.setattr(runner,'dispatch',pooled)
    baseline.test_live_work_mode_drains_without_killing_then_normal_resumes(tmp_path)


@pytest.mark.parametrize('problem',['shortened','memory','toy','threads'])
def test_reduced_prelaunch_rejects_shortening_and_inconsistent_configuration(spec,monkeypatch,problem):
    monkeypatch.setattr(runner,'available_cpus',lambda:16)
    launch_settings=settings()
    if problem=='shortened':
        job=next(j for j in spec['jobs'] if j['config']['cost_kind']=='estimate')
        job['config']['source_job']['config']['settings']['measure']=512
    elif problem=='memory':
        spec['configuration']['pooled']['pooled_estimates_by_stratum']={}
    elif problem=='toy':
        spec['jobs'][0]['config']['toy']=True
    else:
        launch_settings['threads']=2
    with pytest.raises(ValueError):
        runner.validate_spec(spec,launch_settings)


def test_single_configuration_pool_respects_sixteen_worker_limit(tmp_path,spec,monkeypatch):
    seen=[]
    def dispatch(root,jobs,code,settings,deadline,**kwargs):
        seen.append((jobs,kwargs))
        return {'completed':len(jobs),'wall_seconds':1.,'memory_budget_gb':80.,'memory_estimates_gb':{},'maximum_active':kwargs['fixed']['workers']}
    monkeypatch.setattr(runner,'dispatch',dispatch)
    monkeypatch.setattr(runner,'completed',lambda *a:{'seconds':1.})
    profile=spec['configuration']['pooled']
    x2={**settings(),'profile':'x2','cpu_budget':32,'workers':16,'caps':runner.caps('x2',32)}
    result=runner.configuration_test(tmp_path,'pooled',profile,x2,time.time()+30,1)
    assert [r['workers'] for r in result]==[8,12,16]
    assert all(j['tag']=='configuration' and j['config']['configuration_test'] for jobs,_ in seen for j in jobs)
    assert all(set(k['pooled_jobs'])=={j['id'] for j in jobs} for jobs,k in seen)
    assert all(len({j['config']['cost_kind'] for j in jobs})>1 for jobs,_ in seen)


def synthetic_outputs(spec,monkeypatch,*,machine='yotko-evo-x2'):
    def output(root,job,code):
        assert root.name=='pooled'
        s=spec['strata'][job['config']['phase']]
        base=10. if s['kind']=='run' else 10*s['capability']*(2 if s['family']=='sqrt' else 1)
        factor={'primary':1.,'double_population':2.,'double_length':3.,'run':1.}[s['setting']]
        return {'runtime':{'machine':machine},'result':{'cost_only':True,'length_fraction':1.,'seconds':base*factor,
                'scoring_seconds_by_k_star':{'1.5':base*factor/10,'1.8':base*factor/10,'2.3':base*factor/10}}}
    monkeypatch.setattr(runner,'completed',output)
    config={'pooled':[{'valid':True,'workers':2,'threads':1,'wall_seconds':100.,'job_seconds':[100.,100.],
                       'memory_budget_gb':1000.}]}
    selected={'pooled':{'workers':2,'threads':1}}
    return config,selected,output


def test_projection_arithmetic_labels_family_totals_and_nominal_endpoints(spec,tmp_path,monkeypatch):
    config,selected,_=synthetic_outputs(spec,monkeypatch)
    result=pilot.project(spec,tmp_path,config,selected)
    rows=result['per_phase_capability']
    assert rows['nominal.3.0.primary.estimate']['cost_source']=='interpolated'
    assert rows['nominal.3.0.primary.estimate']['mean_worker_seconds']==30.
    assert rows['nominal.1.0.double_population.estimate']['cost_source']=='scaled'
    assert rows['nominal.1.0.double_population.estimate']['mean_worker_seconds']==20.
    assert rows['nominal.5.0.double_length.validate_fv']['mean_worker_seconds']==150.
    assert rows['sqrt.3.0.double_length.validate_plain']['mean_worker_seconds']==180.
    assert rows['sqrt.3.0.double_length.validate_plain']['primary_cost_source']=='interpolated'
    assert rows['nominal.2.0.double_length.estimate']['cost_source']=='measured'
    assert rows['nominal.3.0.primary.labels']['cost_source']=='interpolated'
    assert sum(r['cost_source']=='measured' for r in rows.values())==77
    assert sum(r['sampled_jobs'] for r in rows.values())==77
    # Two source jobs per table stratum. In primary strata, FV plus labels is
    # twice the base; estimate adds once. Non-primary has no labels.
    expected_tables=0.
    expected_measured=0.
    for family,caps in spec['selection']['capabilities'].items():
        family_factor=2 if family=='sqrt' else 1
        for cap in caps:
            base=10*cap*family_factor
            expected_tables += (3*base + 2*2*base + 2*3*base)*2/2/3600*1.35
            if cap in spec['selection']['selected_capabilities'][family]:
                expected_measured += 3*base*2/2/3600*1.35
        if family=='nominal':
            base=10*spec['selection']['medians'][family]
            expected_measured += (2*2*base+2*3*base)*2/2/3600*1.35
    expected_runs=11*10/2/3600*1.35
    reserve=5*2+11/3
    assert result['launch_reserves_x2_hours']==pytest.approx(reserve)
    assert result['total_x2_hours_conservative']==pytest.approx(expected_tables+expected_runs+reserve)
    assert result['total_without_estimated_parts_x2_hours']==pytest.approx(expected_measured+expected_runs+reserve)
    assert sum(f['with_estimated_parts_x2_hours'] for f in result['per_family'].values())==pytest.approx(result['total_x2_hours_conservative'])
    assert result['per_family']['nominal']['with_estimated_parts_x2_hours']>result['per_family']['nominal']['without_estimated_parts_x2_hours']
    assert result['a6_ceiling_x2_hours']==90 and result['a6_within_ceiling']


def test_projection_uses_measured_throughput_and_individual_memory(spec,tmp_path,monkeypatch):
    config,selected,_=synthetic_outputs(spec,monkeypatch)
    config['pooled'][0].update(workers=16,job_seconds=[100.]*12,memory_budget_gb=32.)
    selected['pooled']['workers']=16
    result=pilot.project(spec,tmp_path,config,selected)
    rows=result['per_phase_capability']
    assert result['pooled_effective_workers']==12.
    assert rows['nominal.1.0.primary.estimate']['effective_workers']==12.
    assert rows['nominal.1.0.primary.validate_fv']['effective_workers']==4
    assert rows['nominal.2.0.double_population.validate_fv']['effective_workers']==2


@pytest.mark.parametrize('toy,machine',[(True,'yotko-evo-x2'),(False,'workstation')])
def test_toy_or_unmeasured_local_costs_cannot_set_x2_ceiling(spec,tmp_path,monkeypatch,toy,machine):
    spec['toy']=toy
    config,selected,_=synthetic_outputs(spec,monkeypatch,machine=machine)
    result=pilot.project(spec,tmp_path,config,selected)
    assert result['total_x2_hours_conservative'] is None and result['a6_within_ceiling'] is None


@pytest.mark.parametrize('problem',['missing','short','configuration','outcome'])
def test_projection_refuses_incomplete_or_ineligible_costs(spec,tmp_path,monkeypatch,problem):
    config,selected,original=synthetic_outputs(spec,monkeypatch)
    def changed(*args):
        if problem=='missing': return None
        out=original(*args)
        out['result'].update({'short':{'length_fraction':.25},'configuration':{'configuration_test':True},'outcome':{'cost_only':False}}[problem])
        return out
    monkeypatch.setattr(runner,'completed',changed)
    with pytest.raises(ValueError):
        pilot.project(spec,tmp_path,config,selected)


def test_launch_uses_one_queue_and_records_all_unfinished_jobs(spec,tmp_path,monkeypatch):
    monkeypatch.setattr(runner,'available_cpus',lambda:16)
    calls=[]
    def configuration(*a,**k):
        calls.append(('configuration',a[1]))
        return choices()
    def dispatch(root,jobs,code,settings,deadline,**kwargs):
        calls.append(('dispatch',root.name,len(jobs)))
        assert kwargs['pooled_jobs']==spec['pooled_job_estimates']
        status={j['id']:'not completed' for j in jobs}
        atomic_json(root/'job_status.json',status)
        return {'completed':0,'reason':'deadline','selection':{'workers':2,'threads':1},'not_completed_ids':list(status)}
    monkeypatch.setattr(runner,'configuration_test',configuration)
    monkeypatch.setattr(runner,'dispatch',dispatch)
    path=tmp_path/'spec.json';atomic_json(path,seal(spec))
    result=runner.launch(path,tmp_path/'launch',settings())
    assert calls==[('configuration','pooled'),('dispatch','pooled',77)]
    assert not result['complete']
    assert read(tmp_path/'launch/cost_projection.json')['status']=='incomplete'
    assert len(read(tmp_path/'launch/pooled/job_status.json'))==77
