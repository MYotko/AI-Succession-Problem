"""A11 review regressions: projection stops, indexed RPCs and equivalence."""
import base64
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from copy import deepcopy
import hashlib
import json
import multiprocessing as mp
import platform
import sqlite3
import subprocess
import sys
import time
import pytest
from test_v3_paths import tmp_path
from test_v3_multihost_a11 import (SETTINGS, FINGERPRINT, initialize, spec_fixture,
                                  join, ready, claim, finish, evidence)
from v3 import artifacts as a, multihost_a11 as m, host_a11 as h, production_runner as runner
from v3 import dispatch_store_a11 as store
from v3.compatibility_a10 import comparison_bytes


def projection_spec():
    spec = spec_fixture(4, phases=('fit',))
    spec['schema'] = 'v3-A4-validation-1'
    base = dict(route='plain', a1_job={'config': {'settings': dict(runs_per_group=2,particles=2,burn=30,measure=8)}})
    spec['jobs'] = [a.stable_job('fixture',dict(j['config'],**base),j['tag'],j['index']) for j in spec['jobs']]
    spec['pull_dispatch']['job_classes'] = {j['id']:str(i) for i,j in enumerate(spec['jobs'])}
    spec['configuration']['fit']['config'].update(base)
    return spec


def test_projection_stop_closes_charging_and_resume_with_added_host_fits(tmp_path):
    now = time.time()
    spec = projection_spec(); spec['wall_seconds'] = 1.6
    _,root,_ = initialize(tmp_path,spec,start=now)
    a.atomic_json(root/'launches.json',[dict(complete=False)])
    alpha = join(root,'alpha',now); ready(root,alpha,'fit',now)
    result = claim(root,alpha,now)
    assert result['job'] is None and result['status']['reason']=='projection_exceeds_budget'
    first = m.read_state(root)
    assert all(s['end']==now and s['end_reason']=='projection_exceeds_budget' for s in first['sessions'].values())
    assert a.read(root/'launches.json')[-1]['reason']=='projection_exceeds_budget'
    assert not a.read(root/'launches.json')[-1]['complete']
    charged = result['status']['x2_equivalent_hours']
    assert m.rpc(root,{'op':'inspect'},now=now+.1)['status']['x2_equivalent_hours']==charged
    with m.transaction(root):
        c=m.Coordinator(root,now+.1); c.start(); c.save()
    assert m.read_state(root)['started']==now  # deadline never extends
    alpha=join(root,'alpha',now+.1); beta=join(root,'beta',now+.1)
    for identity in (alpha,beta): ready(root,identity,'fit',now+.1)
    assert claim(root,alpha,now+.1)['job']
    assert not m.read_state(root).get('stop_reason')
    assert a.read(root/'budget.json')['overall_deadline_epoch']==now+1.6


def test_no_hosts_or_unconfigured_hosts_wait_but_draining_host_does_not_block_stop(tmp_path):
    now=time.time(); spec=projection_spec();spec['wall_seconds']=1.6
    _,root,_=initialize(tmp_path,spec,start=now)
    with m.transaction(root):
        c=m.Coordinator(root,now)
        assert c.check_projection() is None
        assert not c.state.get('stop_reason') and c.charged_seconds()==0
        c.save()
    alpha=join(root,'alpha',now); beta=join(root,'beta',now,configure=False)
    ready(root,alpha,'fit',now)
    assert claim(root,alpha,now)['waiting']=='host configurations'
    with m.transaction(root):
        c=m.Coordinator(root,now)
        c.state['sessions'][beta['session']]['control']['drain']=True;c.save()
    assert claim(root,alpha,now)['status']['reason']=='projection_exceeds_budget'
    assert all(s['end']==now for s in m.read_state(root)['sessions'].values())


def test_coordinator_exits_and_records_projection_stop(tmp_path,monkeypatch):
    path,root,_=initialize(tmp_path,projection_spec())
    monkeypatch.setattr(m.Coordinator,'projection',lambda self: False)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future=pool.submit(m.coordinate,path,root,SETTINGS)
        for _ in range(200):
            if (root/'launches.json').exists(): break
            time.sleep(.02)
        identity=join(root,'alpha')
        result=future.result(timeout=10)
    assert result['reason']=='projection_exceeds_budget' and not result['complete']
    history=a.read(root/'launches.json')
    assert history[-1]['reason']=='projection_exceeds_budget' and not history[-1]['complete']
    state=m.read_state(root)
    assert state['sessions'][identity['session']]['end']==history[-1]['status']['hosts']['alpha']['sessions'][0]['end']


def test_batched_claims_respect_free_slots_memory_and_one_heartbeat_renews_all(tmp_path):
    now=time.time();spec=spec_fixture(8)
    spec['pull_dispatch']['cost_classes']['7']['memory_gb']=15
    _,root,_=initialize(tmp_path,spec,start=now)
    alpha=join(root,'alpha',now);ready(root,alpha,'toy',now)
    response=m.rpc(root,dict(alpha,op='claim',max_jobs=12,memory_available_gb=3),now=now)
    assert [c['job'] for c in response['claims']]==[spec['jobs'][6],spec['jobs'][5]]
    assert not m.rpc(root,dict(alpha,op='claim',max_jobs=12,memory_available_gb=100),now=now)['claims']
    before=m.read_state(root)
    m.rpc(root,dict(alpha,op='heartbeat'),now=now+10)
    after=m.read_state(root)
    assert {l['expires'] for l in after['leases'].values() if l['status']=='active'}=={now+40}
    assert after['completions']==before['completions']
    for bad in (0,33,1.5,True):
        with pytest.raises(ValueError,match='claim batch'):
            m.rpc(root,dict(alpha,op='claim',max_jobs=bad,memory_available_gb=100),now=now+10)


def test_lost_batched_claim_reply_retries_without_extra_leases(tmp_path):
    _,root,_=initialize(tmp_path)
    alpha=join(root,'alpha');ready(root,alpha,'toy')
    class LoseReply(h.Loopback):
        dropped=False
        def call(self,request):
            result=super().call(request)
            if request['op']=='claim' and not self.dropped:
                self.dropped=True
                self.first=result
                raise ConnectionError('reply lost after durable claim')
            return result
    transport=LoseReply(root)
    client=h.Client(transport,'alpha',alpha['session'],30)
    response=client.call('claim',max_jobs=2,memory_available_gb=40)
    assert response==transport.first and len(response['claims'])==2
    assert len(m.read_state(root)['leases'])==2


@pytest.mark.parametrize('transport_kind', ['ssh', 'local'])
def test_stdio_stream_reuses_process_without_network(tmp_path,monkeypatch,transport_kind):
    _,root,_=initialize(tmp_path)
    a.atomic_json(root/'launches.json',[dict(machine=platform.node(),complete=False)])
    original=subprocess.Popen;processes=[]
    def local_command(args,**kwargs):
        if transport_kind=='ssh':
            assert args[0]=='ssh' and args[-1].endswith('--stream')
            args=[sys.executable,'-B','-m','v3.multihost_a11','rpc',str(root),'--stream']
            kwargs['cwd']=a.SIMULATION
        else:
            assert args==[sys.executable,'-B','-m','v3.multihost_a11','rpc',str(root),'--stream','--local']
            assert kwargs['cwd']==a.SIMULATION
        process=original(args,**kwargs)
        processes.append(process)
        return process
    monkeypatch.setattr(h.subprocess,'Popen',local_command)
    transport=h.SSH('loopback','unused',str(root)) if transport_kind=='ssh' else h.Local(root)
    try:
        assert transport.call({'op':'inspect'})['status']['completed']==0
        with pytest.raises(h.Rejected,match='unknown coordinator'):
            transport.call({'op':'invalid'})
        assert transport.call({'op':'inspect'})['status']['completed']==0
        assert len(processes)==1
    finally:
        transport.close()
    assert processes[0].poll() is not None


@pytest.mark.parametrize('defect', ['missing_record', 'different_machine', 'different_host'])
def test_local_transport_refuses_missing_or_different_coordinator_machine(tmp_path,defect):
    host=platform.node()
    _,root,_=initialize(tmp_path,hosts=(host,))
    request=dict(op='inspect')
    if defect!='missing_record':
        machine=host+'-different' if defect=='different_machine' else host
        a.atomic_json(root/'launches.json',[dict(machine=machine,complete=False)])
    if defect=='different_host': request['host']=host+'-different'
    transport=h.Local(root)
    try:
        with pytest.raises(h.Rejected,match='local transport.*coordinator machine'):
            transport.call(request)
        # The recorded machine is checked on every request, even on the same
        # already running stdio process. A corrected record permits inspection.
        a.atomic_json(root/'launches.json',[dict(machine=host,complete=False)])
        assert transport.call(dict(op='inspect'))['status']['completed']==0
        a.atomic_json(root/'launches.json',[dict(machine=host+'-different',complete=False)])
        with pytest.raises(h.Rejected,match='does not match'):
            transport.call(dict(op='inspect'))
    finally:
        transport.close()
    assert not m.read_state(root)['sessions']


def test_local_transport_uses_normal_join_configuration_batch_leases_and_charging(tmp_path):
    host=platform.node()
    _,root,spec=initialize(tmp_path,hosts=(host,))
    a.atomic_json(root/'launches.json',[dict(machine=host,complete=False)])
    transport=h.Local(root)
    try:
        request=dict(op='join',host=host,code_hash=spec['code_hash'],code_commit='fixture',fingerprint=FINGERPRINT,settings=SETTINGS)
        with pytest.raises(h.Rejected,match='fingerprint or code identity'):
            transport.call(dict(request,fingerprint={}))
        joined=transport.call(request)
        identity=dict(host=host,session=joined['session'])
        assert transport.call(dict(identity,op='claim',memory_available_gb=40))['waiting']=='inputs or configuration'
        snapshot=transport.call(dict(identity,op='inputs',phase='toy',configuration=True))
        transport.call(dict(identity,op='configure',phase='toy',input_sha256=snapshot['sha256'],measurements=[
            dict(workers=2,threads=1,completed=2,wall_seconds=1.,valid=True,round=0,job_seconds=[.5,.5])]))
        transport.call(dict(identity,op='configured'))
        snapshot=transport.call(dict(identity,op='inputs',phase='toy'))
        transport.call(dict(identity,op='ready',phase='toy',input_sha256=snapshot['sha256']))
        batch=dict(identity,op='claim',memory_available_gb=40,max_jobs=2,request_id='local-batch')
        result=transport.call(batch)
        assert result==transport.call(batch) and len(result['claims'])==2
        assert len(m.read_state(root)['leases'])==2
        transport.call(dict(identity,op='heartbeat'))
        for leased in result['claims']:
            raw=a.canonical(dict(job=leased['job'],code_hash=spec['code_hash'],host=host,lease=leased['lease'],
                seconds=.1,result=dict(seed=leased['job']['seed'],fixture=True)))
            response=transport.call(dict(identity,op='complete',lease=leased['lease'],data=base64.b64encode(raw).decode(),
                                         sha256=hashlib.sha256(raw).hexdigest()))
            assert response['accepted']
        transport.call(dict(identity,op='leave'))
    finally:
        transport.close()
    session=m.read_state(root)['sessions'][joined['session']]
    assert session['end']>session['joined'] and session['worker_seconds']==pytest.approx(.2)
    assert session['configuration_worker_seconds']['toy']==1.


@pytest.mark.parametrize('flags', [[], ['--coordinator','example'], ['--local','--coordinator','example'], ['--local','--checkout','example']])
def test_transport_selection_is_explicit_and_unambiguous(tmp_path,monkeypatch,flags):
    monkeypatch.setattr(sys,'argv',['host_a11','--root',str(tmp_path/'root'),'--scratch',str(tmp_path/'scratch'),
        '--profile','local','--workers','2','--cpu-budget','16',*flags])
    with pytest.raises(SystemExit) as exc:
        h.main()
    assert exc.value.code==2
    assert not (tmp_path/'scratch').exists()


def test_hot_requests_use_index_and_delta_log_status_is_bounded(tmp_path,monkeypatch):
    now=time.time();_,root,_=initialize(tmp_path,spec_fixture(1000),start=now)
    alpha=join(root,'alpha',now);ready(root,alpha,'toy',now)
    # Force one status publication, then all hot operations share a timestamp.
    with m.transaction(root):
        c=m.Coordinator(root,now);c.save(force=True)
    checkpoint=a.file_hash(root/'pull_state.json');status=a.file_hash(root/'status.json')
    original=store.read
    def guard(path):
        assert str(path).replace('\\','/').rsplit('/',1)[-1] not in ('manifest.json','pull_state.json')
        return original(path)
    monkeypatch.setattr(store,'read',guard)
    leased=claim(root,alpha,now)
    finish(root,alpha,leased,now)
    m.rpc(root,dict(alpha,op='heartbeat'),now=now+.1)
    assert a.file_hash(root/'pull_state.json')==checkpoint and a.file_hash(root/'status.json')==status
    assert len(m.read_state(root)['completions'])==1
    with sqlite3.connect(root/'dispatch.sqlite') as db:
        event=json.loads(db.execute('SELECT data FROM journal ORDER BY seq DESC LIMIT 1').fetchone()[0])
        assert all(row['bucket']!='completions' for row in event['changes'])
        assert len(event['changes'])<=4
    store.checkpoint(root)


def test_crash_between_completion_record_and_operational_commit_recovers(tmp_path,monkeypatch):
    _,root,_=initialize(tmp_path)
    alpha=join(root,'alpha');ready(root,alpha,'toy');leased=claim(root,alpha)
    original=store.Store.commit
    def die(self):
        raise RuntimeError('injected crash after output and record')
    monkeypatch.setattr(store.Store,'commit',die)
    with pytest.raises(RuntimeError,match='injected crash'):
        finish(root,alpha,leased)
    monkeypatch.setattr(store.Store,'commit',original)
    assert runner.completed(root/'toy',leased['job'],a.code_identity())
    assert not m.read_state(root)['completions']
    with m.transaction(root):
        c=m.Coordinator(root);c.start();c.save()
    assert len(m.read_state(root)['completions'])==1
    assert finish(root,alpha,leased)['duplicate']


def test_journal_corruption_refused_on_resume(tmp_path):
    _,root,_=initialize(tmp_path)
    join(root,'alpha')
    with sqlite3.connect(root/'dispatch.sqlite') as db:
        db.execute("UPDATE journal SET sha256='bad' WHERE seq=1")
    with m.transaction(root),pytest.raises(ValueError,match='journal'):
        c=m.Coordinator(root);c.start()


def test_single_machine_and_multihost_canonical_results_and_record_shape(tmp_path):
    spec=spec_fixture(6)
    cfg=dict(phase='toy',steps=2,model=dict(n_agents=8,carrying_capacity=80,instrument=spec['instrument']))
    spec['jobs']=[a.stable_job('rerun',cfg,'validation',i) for i in range(6)]
    spec['pull_dispatch']['job_classes']={j['id']:str(i) for i,j in enumerate(spec['jobs'])}
    spec['configuration']['toy'].update(kind='rerun',config=cfg)
    ordinary=deepcopy(spec);ordinary.pop('pull_dispatch')
    path=tmp_path/'ordinary.json';a.atomic_json(path,a.seal(ordinary))
    single=tmp_path/'single'
    assert runner.launch(path,single,SETTINGS)['complete']
    _,root,_=initialize(tmp_path/'multi',spec)
    with ProcessPoolExecutor(max_workers=2,mp_context=mp.get_context('spawn')) as pool:
        futures=[pool.submit(h.run_host,h.Loopback(root),tmp_path/host,SETTINGS,host=host,environment=FINGERPRINT,max_seconds=60)
                 for host in ('alpha','beta')]
        for f in futures: f.result()
    assert m.rpc(root,{'op':'inspect'})['status']['complete']
    for job in spec['jobs']:
        left=runner.completed(single/'toy',job,spec['code_hash'])
        right=runner.completed(root/'toy',job,spec['code_hash'])
        assert comparison_bytes(job,left['result'])==comparison_bytes(job,right['result'])
        record=a.read(single/'toy/records'/(job['id']+'.json'))
        remote=a.read(root/'toy/records'/(job['id']+'.json'))
        assert set(remote)==set(record)|{'host','lease'}
        # Timestamps, elapsed time and the host-bearing output's hash naturally
        # differ. Every remaining existing field must match exactly.
        for key in set(record)-{'completed_epoch','worker_seconds','output_hash'}:
            assert record[key]==remote[key]


@pytest.mark.parametrize('legacy',['R4','undeclared','legacy_registered'])
def test_registered_r4_and_legacy_refuse_freeze_launch_and_remote(tmp_path,legacy):
    spec=spec_fixture(2)
    cfg=dict(phase='toy',steps=0,category='R1',model=dict(instrument={'mapping':'A10','g':'linear','k_star':1.8}))
    spec['jobs']=[a.stable_job('rerun',cfg,'validation',i) for i in range(2)]
    spec['pull_dispatch']['job_classes']={j['id']:str(i) for i,j in enumerate(spec['jobs'])}
    spec.update(registered=True,registered_a10=True)
    if legacy=='R4': spec['instrument']={'mapping':'R4'}
    elif legacy=='undeclared': spec.pop('instrument')
    else: spec.pop('registered_a10')
    plain=deepcopy(spec);plain.pop('pull_dispatch')
    costs={k:dict(mean_worker_seconds=1,memory_estimate_gb=1) for j in spec['jobs'] for k in m.cost_keys(j)}
    with pytest.raises(ValueError,match='remote hosts|legacy'):
        m.freeze(plain,a.seal(dict(per_phase_capability=costs)),code_commit='fixture')
    path=tmp_path/'spec.json';a.atomic_json(path,a.seal(spec))
    with pytest.raises(ValueError,match='remote hosts|legacy'):
        runner.launch(path,tmp_path/'launch',SETTINGS)
    root=tmp_path/'remote';a.atomic_json(root/'manifest.json',a.seal(spec))
    a.atomic_json(root/'identity.json',dict(code_hash=spec['code_hash'],spec_hash=a.digest(spec)))
    a.atomic_json(root/'pull_state.json',a.seal({}))
    with pytest.raises(ValueError,match='remote hosts|legacy'):
        m.rpc(root,dict(op='join',host='alpha'))
