"""Item 10: synthetic memory scheduling, child death and mode contracts."""
import ctypes
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import signal
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import pytest
from test_v3_paths import tmp_path
from v3 import artifacts as a, worker_control as wc, worker_safety as safety, production_runner as r
from v3 import compatibility_shards_a11 as proof, compatibility_a10 as compatibility
from v3 import multihost_a11 as m, host_a11 as h


@pytest.mark.parametrize('values,expected', [([],0),([7],7),([8,4,2,1],8),([8,4,2,1,1],6),([8]*4+[1]*12,8),([8]*4+[1]*13,6.6)])
def test_heaviest_quarter(values,expected):
    assert wc.top_weighted(values)==pytest.approx(expected)


def test_charges_small_pack_and_recompute():
    values=[12,8]+[1]*7
    resources={str(i):dict(memory_class=str(i),memory_gb=v) for i,v in enumerate(values)}
    charges,w=wc.admission_charges(resources,{})
    assert w==7 and charges['0']==7 and charges['2']==1
    assert all(charges[k]<=v['memory_gb'] for k,v in resources.items())
    resources.pop('0');resources.pop('1')
    assert wc.admission_charges(resources,{})[1]==1
    assert wc.admission_charges(resources,{'2':3})[1]==2


def test_x2_modes_and_local_unchanged():
    assert r.caps('x2',32)==dict(normal=31,work=31,configuration=32)
    assert r.caps('local',16)==dict(normal=12,work=12,configuration=12)
    assert r.caps('local',8)==dict(normal=7,work=4,configuration=8)
    assert proof.worker_cap(dict(profile='x2',workers=31,threads=1,cpu_budget=32,mode='normal'))==31
    assert wc.MODE_CAPS_TARGET is True


@pytest.mark.parametrize('free,passed', [(16_000_000_000-1,False),(16_000_000_000,True),(32*1024**3,True),(None,False)])
def test_swap_preflight(tmp_path,monkeypatch,free,passed):
    monkeypatch.setattr(safety,'swap_status',lambda:dict(total_bytes=32*1024**3,free_bytes=free))
    path=tmp_path/'swap.json'
    if passed: assert safety.swap_preflight(dict(profile='x2'),path)['passed']
    else:
        with pytest.raises(ValueError,match='swap'): safety.swap_preflight(dict(profile='x2'),path)
    assert a.read(path)['passed']==passed
    assert safety.swap_preflight(dict(profile='local'),path)['passed']


def test_oom_only_spawned_workers(monkeypatch):
    monkeypatch.setattr(safety.platform,'system',lambda:'Linux')
    writes=[]
    monkeypatch.setattr(Path,'write_text',lambda self,text,**kw:writes.append((str(self),text)))
    monkeypatch.setattr(Path,'read_text',lambda *args,**kw:'1000')
    monkeypatch.setattr(safety.mp,'parent_process',lambda:None)
    assert safety.prefer_worker_oom()['skipped'] and not writes
    monkeypatch.setattr(safety.mp,'parent_process',lambda:object())
    assert safety.prefer_worker_oom()['success']
    assert [(p.replace(chr(92),'/'),v) for p,v in writes]==[('/proc/self/oom_score_adj','1000')]
    def denied(*args,**kwargs): raise PermissionError('synthetic denial')
    monkeypatch.setattr(Path,'write_text',denied)
    assert 'synthetic denial' in safety.prefer_worker_oom()['error']


def test_both_load_sheet_rules():
    jobs=[a.stable_job('fixture',{},'validation',i) for i in range(9)]
    estimates={j['id']:dict(memory_class=str(i),memory_gb=v,estimated_seconds=10,measured_seconds=5) for i,(j,v) in enumerate(zip(jobs,[12,8]+[1]*7))}
    sheet=wc.load_sheet(jobs,estimates,dict(profile='x2',workers=31,threads=1,cpu_budget=32,mode='normal'),20)
    old,new=sheet['rules']['per_class'],sheet['rules']['item10']
    assert new['start_weight_gb']==7
    assert new['concurrent_workers']>=old['concurrent_workers']
    assert new['class_wall_hours']<=old['class_wall_hours']
    assert new['measured_wall_hours']==new['class_wall_hours']/2
    assert new['maximum_memory_gb']<=16


def kill(pid):
    if os.name=='nt':
        # Native termination status used by multiprocessing.Process.kill on
        # Windows. POSIX runs exercise SIGKILL itself with the same assertions.
        lib=ctypes.WinDLL('kernel32',use_last_error=True)
        lib.OpenProcess.restype=ctypes.c_void_p
        handle=lib.OpenProcess(1,False,pid)
        if not handle: return False
        try: return bool(lib.TerminateProcess(ctypes.c_void_p(handle),0x10000))
        finally: lib.CloseHandle(ctypes.c_void_p(handle))
    try: os.kill(pid,signal.SIGKILL);return True
    except ProcessLookupError: return False


def install_execution_marker():
    """Test-only worker instrumentation; preserve the exact execute arguments."""
    original=r.execute
    def marked(*args,**kwargs):
        job=args[0]
        assert job['kind']=='fixture'
        a.atomic_json(Path(os.environ['ITEM10_TEST_MARKERS'])/(str(os.getpid())+'.json'),
                      dict(pid=os.getpid(),job_sha256=a.digest(job)))
        return original(*args,**kwargs)
    r.execute=marked


def runner_marked(*args):
    install_execution_marker()
    return r.worker(*args)


def host_marked(*args):
    install_execution_marker()
    return h.execute_scratch(*args)


def proof_marked(item):
    install_execution_marker()
    return compatibility._execute_proof(item)


def killer(root,pattern,number=1):
    seen=set();killed=[];end=time.monotonic()+75
    while len(killed)<number and time.monotonic()<end:
        for path in root.glob(pattern):
            try:
                value=a.read(path);value=value.get('oom_score_adj',value);pid=value['pid']
            except (OSError,ValueError,KeyError): continue
            if pid in seen: continue
            seen.add(pid)
            # The marker is at execute entry, followed by the real fixture's
            # .7-second job. Kill during its work, not during process startup.
            time.sleep(.1)
            if kill(pid): killed.append(pid)
            if len(killed)>=number:break
        time.sleep(.01)
    assert len(killed)==number, killed
    return killed


def settings(n=2):
    return dict(profile='local',workers=n,threads=1,cpu_budget=4,mode='normal',caps=r.caps('local',4))


@pytest.mark.parametrize('exhaust',[False,True])
def test_runner_signal_retry_seed_siblings_and_bound(tmp_path,monkeypatch,exhaust):
    jobs=[a.stable_job('fixture',dict(seconds=.7),'validation',i) for i in range(1 if exhaust else 3)]
    a.atomic_json(tmp_path/'control.json',dict(mode='normal',max_workers=1 if exhaust else 2))
    monkeypatch.setenv('ITEM10_TEST_MARKERS',str(tmp_path/'executing'))
    monkeypatch.setattr(r,'worker',runner_marked)
    with ThreadPoolExecutor(1) as pool:
        watch=pool.submit(killer,tmp_path,'executing/*.json',4 if exhaust else 1)
        if exhaust:
            with pytest.raises(RuntimeError,match='three signal reruns'):
                r.dispatch(tmp_path,jobs,a.code_identity(),settings(1),time.time()+70)
        else:
            assert r.dispatch(tmp_path,jobs,a.code_identity(),settings(),time.time()+70)['completed']==3
            for j in jobs: assert r.completed(tmp_path,j,a.code_identity())['result']==dict(seed=j['seed'],fixture=True)
        watch.result()
    events=a.read(tmp_path/'worker_restarts.json')
    assert len(events)==(4 if exhaust else 1) and events[-1]['allowed']==(not exhaust)
    assert all(e['signal'] in (9,15) and e['epoch'] and e['reason'] for e in events)
    if exhaust:
        with pytest.raises(RuntimeError,match='three signal reruns'):
            r.dispatch(tmp_path,jobs,a.code_identity(),settings(1),time.time()+10)
        assert a.read(tmp_path/'worker_restarts.json')==events


@pytest.mark.parametrize('exhaust',[False,True])
def test_proof_shard_signal_retry_finality(tmp_path,monkeypatch,exhaust):
    from test_v3_compatibility_shards_a11 import source_fixture,hosts,ORIGINAL,FINGERPRINT
    monkeypatch.setattr(proof,'verify_code',lambda _:None)
    monkeypatch.setattr(proof.platform,'node',lambda:ORIGINAL)
    monkeypatch.setattr(h,'fingerprint',lambda:FINGERPRINT)
    monkeypatch.setattr(compatibility,'RECORD_DIRECTORY',tmp_path/'reservations')
    sources,reasons=source_fixture(tmp_path,seconds=.7)
    target=tmp_path/'proof.json';path=target.with_suffix('.attempt.json')
    entries=hosts(False)
    entries[ORIGINAL]['settings']=dict(entries[ORIGINAL]['settings'],mode='normal')
    from test_v3_multihost_a11 import evidence
    entries[ORIGINAL]['qualification']=evidence(ORIGINAL,a.code_identity(),settings=entries[ORIGINAL]['settings'])
    entries[ORIGINAL]['qualification_plan_sha256']=a.unseal(entries[ORIGINAL]['qualification'])['plan']['sha256']
    proof.freeze(sources,reasons,target,entries,'f'*40)
    proof.stage(path,ORIGINAL);root=proof.host_directory(path,ORIGINAL)
    monkeypatch.setenv('ITEM10_TEST_MARKERS',str(root/'executing'))
    monkeypatch.setattr(proof,'_execute_proof',proof_marked)
    # Configuration choices are per profile, not a replacement host target.
    chosen=1 if exhaust else 2
    def configured(plan,*args):
        return {key:dict(chosen=dict(workers=chosen),measurements=[dict(workers=chosen,threads=1,
            valid=True,completed=chosen,wall_seconds=1.)]) for key in plan['profiles']}
    monkeypatch.setattr(proof,'configure_host',configured)
    with ThreadPoolExecutor(1) as pool:
        watch=pool.submit(killer,root,'executing/*.json',4 if exhaust else 1)
        if exhaust:
            with pytest.raises(ValueError,match='three signal reruns'): proof.run_shard(path,ORIGINAL)
        else:
            result=proof.run_shard(path,ORIGINAL)
            assert result['passed'] and all(r['before_sha256']==r['after_sha256'] for r in result['proofs'])
        watch.result()
    events=a.read(root/'worker_metadata/restarts.json')
    assert len(events)==(4 if exhaust else 1)
    assert a.unseal(a.read(root/'result.json'))['passed']==(not exhaust)
    if not exhaust: assert proof.combine(path)['passed']
    with pytest.raises(ValueError,match='final'):proof.run_shard(path,ORIGINAL)


def test_pull_host_signal_retry_through_rpc(tmp_path,monkeypatch):
    from test_v3_multihost_a11 import initialize,spec_fixture,SETTINGS,FINGERPRINT
    _,root,spec=initialize(tmp_path,spec_fixture(5,seconds=.7),hosts=('alpha',))
    scratch=tmp_path/'worker'
    monkeypatch.setenv('ITEM10_TEST_MARKERS',str(scratch/'executing'))
    monkeypatch.setattr(h,'execute_scratch',host_marked)
    monkeypatch.setattr(r,'configuration_test',lambda *args,**kw:[dict(workers=2,threads=1,completed=2,wall_seconds=1.,valid=True,round=0,job_seconds=[.5,.5])])
    with ThreadPoolExecutor(1) as pool:
        watch=pool.submit(killer,scratch,'executing/*.json')
        h.run_host(h.Loopback(root),scratch,dict(SETTINGS,workers=2),host='alpha',environment=FINGERPRINT,max_seconds=90)
        watch.result()
    with m.transaction(root):
        c=m.Coordinator(root)
        assert c.state['complete'] and not c.state['halt']
        assert len(c.state['worker_restarts'])==1 and c.state['worker_restarts'][0]['allowed']
    for job in spec['jobs']: assert r.completed(root/'toy',job,a.code_identity())['result']==dict(seed=job['seed'],fixture=True)


def test_live_available_guard_and_dynamic_weight_in_proof(tmp_path,monkeypatch):
    items=[dict(job=a.stable_job('fixture',dict(seconds=.01),'validation',i),phase_root=str(tmp_path),producing_code_hash=a.code_identity(),
                resources=dict(worker_seconds=1,memory_gb=v,memory_class=str(i))) for i,v in enumerate([6,2,1,1,1])]
    calls=[]
    def available(*args):
        calls.append(1)
        return .01 if len(calls)<3 else 20.
    monkeypatch.setattr(proof,'memory_budget',available)
    results,trace=proof.run_items(items,5,8.,idle_wait_seconds=10)
    assert len(results)==5 and len(calls)>=3
    assert trace[0]['top_weighted_gb']==4
    assert all(t['reserved_gb']<=4 and t['running_gb']<=8 for t in trace)
    assert any(t['running']>1 for t in trace)


def test_pull_quarter_per_claim_small_classes_and_live_guard(tmp_path):
    from test_v3_multihost_a11 import initialize,spec_fixture,join,ready,SETTINGS
    spec=spec_fixture(9)
    for i,v in enumerate([12,8]+[1]*7): spec['pull_dispatch']['cost_classes'][str(i)]['memory_gb']=v
    _,root,spec=initialize(tmp_path,spec,hosts=('alpha',))
    identity=join(root,'alpha');ready(root,identity,'toy')
    m.control(root,'alpha',max_workers=7,reason='packing test')
    refused=m.rpc(root,dict(op='claim',memory_available_gb=.5,**identity))
    assert refused['job'] is None
    claims=m.rpc(root,dict(op='claim',memory_available_gb=10,max_jobs=7,**identity))['claims']
    with m.transaction(root):
        c=m.Coordinator(root);weight=c.admission_weight(identity['session'])
        assert weight==7
        leases=c.active(identity['session'])
        assert len(leases)>1 and c.reserved_memory(leases,weight)<=8
        assert all(l['memory_gb']<=max(c.store.cost(c.jobs[l['job_id']])[1]['memory_gb'],c.state.get('observed_memory_gb',{}).get(c.store.cost(c.jobs[l['job_id']])[0],0)) for l in leases)


def test_returned_pool_result_not_reexecuted_after_transport_death(tmp_path):
    from concurrent.futures import Future
    from concurrent.futures.process import BrokenProcessPool
    class Pool:
        def shutdown(self,**kwargs):pass
    path=tmp_path/'returned.json';a.atomic_json(path,dict(value=dict(after_sha256='unchanged')))
    future=Future();future.set_exception(BrokenProcessPool())
    pools=safety.IsolatedPools(tmp_path);pools.active[future]=(Pool(),path,[])
    assert pools.result(future)==dict(after_sha256='unchanged')


def test_pool_non_signal_failure_is_not_retried(tmp_path):
    from concurrent.futures import Future
    from concurrent.futures.process import BrokenProcessPool
    class Pool:
        def shutdown(self,**kwargs):pass
    class Child: exitcode=1
    future=Future();future.set_exception(BrokenProcessPool('startup error'))
    pools=safety.IsolatedPools(tmp_path);pools.active[future]=(Pool(),tmp_path/'absent.json',[Child()])
    with pytest.raises(BrokenProcessPool):pools.result(future)


def test_historical_load_sheet_is_read_only_and_checks_partition(tmp_path,monkeypatch):
    job=a.stable_job('fixture',{},'validation',0)
    plan=dict(schema=proof.SCHEMA,new_code_hash='old identity',selected_job_ids=[job['id']],
        assignments={'old-host':[job['id']]},hosts={'old-host':dict(settings=settings(),memory_gb=10,relative_throughput=1)},
        items={job['id']:dict(job=job,resources=dict(memory_class='toy',memory_gb=1,worker_seconds=10))})
    path=tmp_path/'old.attempt.json';a.atomic_json(path,a.seal(plan));before=path.read_bytes()
    monkeypatch.setattr(proof,'load_attempt',lambda _:pytest.fail('historical projection must not enable execution'))
    monkeypatch.setattr(proof,'host_directory',lambda *args:pytest.fail('must not inspect old run root'))
    sheet=proof.attempt_load_sheet(path,historical=True)['old-host']
    assert sheet['rules']['item10']['start_weight_gb']==1
    assert path.read_bytes()==before and list(tmp_path.iterdir())==[path]
    plan['assignments']['old-host'].append(job['id']);a.atomic_json(path,a.seal(plan))
    with pytest.raises(ValueError,match='partition'):proof.attempt_load_sheet(path,historical=True)


def test_pull_signal_retry_bound_is_durable_through_rpc(tmp_path):
    from test_v3_multihost_a11 import initialize,spec_fixture,join,ready
    _,root,_=initialize(tmp_path,spec_fixture(1),hosts=('alpha',))
    identity=join(root,'alpha');ready(root,identity,'toy');first=None
    for n in range(4):
        claim=m.rpc(root,dict(op='claim',memory_available_gb=10,**identity))
        if first is None:first=claim['job']
        assert claim['job']==first
        reply=m.rpc(root,dict(op='release',lease=claim['lease'],reason='worker signal kill',signal=9,**identity))
        assert bool(reply['halt'])==(n==3)
    state=m.read_state(root)
    assert [e['allowed'] for e in state['worker_restarts']]==[True,True,True,False]
    assert not state['complete'] and a.unseal(a.read(root/'execution_failure.json'))['job_id']==first['id']


@pytest.mark.parametrize('fixed_jobs',[None,2,32])
def test_proof_configuration_tests_full_cpu_and_launch_cap(tmp_path,monkeypatch,fixed_jobs):
    job=a.stable_job('fixture',{},'validation',0)
    profile=dict(kind='fixture',config={},workers_x2=[8,12,16,24,32],jobs_per_worker=1,rounds=1)
    if fixed_jobs is not None:
        profile.pop('jobs_per_worker');profile['jobs_x2']=fixed_jobs
    plan=dict(hosts={'x2':dict(settings=dict(profile='x2',workers=31,threads=1,cpu_budget=32,mode='normal'))},
        assignments={'x2':[job['id']]},items={job['id']:dict(job=job,profile_key='toy',resources=dict(memory_class='toy',memory_gb=.1,worker_seconds=1))},
        profiles={'toy':dict(profile=profile,phase_root=str(tmp_path),producing_code_hash='old')})
    seen=[]
    def run(tasks,workers,budget,**kwargs):
        seen.append(workers)
        return {t['job']['id']:dict(after_sha256='a'*64,_worker_seconds=1.) for t in tasks},[]
    monkeypatch.setattr(proof,'run_items',run)
    proof.configure_host(plan,'x2',tmp_path,100.,None)
    assert seen==([2] if fixed_jobs==2 else [8,12,16,24,31])


def test_preflight_rechecks_weight_after_measured_configuration_peaks(tmp_path,monkeypatch):
    item=dict(job={'id':'toy'},resources=dict(memory_gb=1.,memory_class='toy'))
    plan=dict(hosts={'host':dict(settings=settings(),memory_gb=100)},items={'toy':item},
              assignments={'host':['toy']},snapshots={'host':dict(proof={},configuration={})},profiles={})
    monkeypatch.setattr(proof,'receive_inputs',lambda *args:{})
    monkeypatch.setattr(proof,'check_input_paths',lambda *args:None)
    monkeypatch.setattr(proof,'configuration_items',lambda *args:[])
    monkeypatch.setattr(proof,'configure_host',lambda *args:dict(toy=dict(class_peaks_gb={'toy':7.})))
    required=[]
    monkeypatch.setattr(proof,'wait_for_memory',lambda value,*args,**kw:required.append(value) or 80.)
    proof.preflight(plan,'host',tmp_path)
    assert required==[1.,7.]
    assert not (tmp_path/'started.json').exists()


def test_qualification_recovers_durable_result_after_signal(tmp_path,monkeypatch):
    from v3 import qualification_a11 as q
    job=a.stable_job('fixture',{},'validation',0);path=tmp_path/'returned.json'
    a.atomic_json(path,dict(job=job,code_hash='same',host='host',result=dict(seed=job['seed']),seconds=1.,peak_rss_bytes=123))
    monkeypatch.setattr(h,'execute_scratch',lambda *args:pytest.fail('returned job must not be executed again'))
    value=q._run_one((str(path),job,'same',str(tmp_path),None,'host'))
    assert value['canonical_sha256']==hashlib.sha256(compatibility.comparison_bytes(job,dict(seed=job['seed']))).hexdigest()


def test_recheck_uses_item10_charge_with_future_pending_jobs(tmp_path):
    from test_v3_multihost_a11 import initialize,spec_fixture,join,ready,finish
    spec=spec_fixture(8,phases=('toy','later'))
    # One costly completed phase; the later pending jobs lower the recheck W.
    first=[j for j in spec['jobs'] if j['config']['phase']=='toy']
    spec['jobs']=[first[0]]+[j for j in spec['jobs'] if j['config']['phase']=='later']
    keep={j['id'] for j in spec['jobs']}
    pull=spec['pull_dispatch'];pull['job_classes']={j:c for j,c in pull['job_classes'].items() if j in keep}
    pull['cost_classes']={c:dict(v,memory_gb=6. if c==pull['job_classes'][first[0]['id']] else 1.) for c,v in pull['cost_classes'].items() if c in set(pull['job_classes'].values())}
    _,root,_=initialize(tmp_path,spec,hosts=('alpha',));identity=join(root,'alpha');ready(root,identity,'toy')
    work=m.rpc(root,dict(op='claim',memory_available_gb=4.,**identity));assert work['job']==first[0]
    finish(root,identity,work)
    check=m.rpc(root,dict(op='claim',memory_available_gb=4.,**identity))
    assert check['purpose']=='check' and check['job']==first[0]
    with m.transaction(root):
        coordinator=m.Coordinator(root)
        assert coordinator.admission_weight(identity['session'])==pytest.approx(8/3)
        assert coordinator.admission_weight(identity['session'],first[0])==pytest.approx(8/3)


def test_single_host_proof_keeps_configuration_peaks(tmp_path,monkeypatch):
    from test_v3_compatibility_shards_a11 import source_fixture
    monkeypatch.setattr(compatibility,'RECORD_DIRECTORY',tmp_path/'reservations')
    sources,reasons=source_fixture(tmp_path)
    def preflight(record,items,profiles,target,workers,floor,settings=None):
        peaks={i['resources']['memory_class']:3. for i in items.values()}
        return None,{'toy':dict(class_peaks_gb=peaks)},0.,10.,workers
    monkeypatch.setattr(proof,'single_preflight',preflight)
    result=compatibility.build_record(sources,reasons,tmp_path/'single.json',workers=2)
    assert result['passed']
    assert all(t['reserved_gb']==3. for t in result['execution']['admission'])


def test_projection_records_charge_rise_without_admitting_more_jobs():
    items=[dict(key=str(i),memory=memory,seconds=seconds) for i,(memory,seconds) in enumerate([(10,10),(2,1),(1,.1),(1,.1),(1,.1)])]
    value=wc.packing_projection(items,5,8.)
    assert value['start_weight_gb']==6.
    assert value['initial_concurrent_workers']==2
    # Once the small running job finishes n falls to four and W rises to ten.
    # The existing heavy worker finishes; no new job may enter until then.
    assert value['maximum_memory_gb']==10.
    assert value['wall_seconds']==pytest.approx(10.1)


@pytest.mark.parametrize('module,profile,expected', [('host','x2','normal'),('host','local','work'),('qualification','x2','normal'),('qualification','local','work')])
def test_worker_cli_profile_mode_default(tmp_path,monkeypatch,module,profile,expected):
    import sys
    from v3 import qualification_a11 as q
    seen=[]
    def capture(value,**kwargs):
        seen.append(value)
        raise RuntimeError('captured before service or execution')
    monkeypatch.setattr(wc,'settings',capture)
    options=['--profile',profile,'--workers','1','--cpu-budget','2']
    if module=='host':
        argv=['host','--local','--root',str(tmp_path/'root'),'--scratch',str(tmp_path/'scratch')]+options
        main=h.main
    else:
        argv=['qualification','run',str(tmp_path/'plan.json'),str(tmp_path/'run.json')]+options
        main=q.main
    monkeypatch.setattr(sys,'argv',argv)
    with pytest.raises(RuntimeError,match='captured before'):main()
    assert seen[0]['mode']==expected
