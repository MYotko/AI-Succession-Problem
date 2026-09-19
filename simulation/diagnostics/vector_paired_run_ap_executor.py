"""Execute detector evaluation and its required gates under a write guard."""


import sys


sys.dont_write_bytecode=True


sys.stdout.reconfigure(encoding='utf-8')


import os


THREAD_ENV=('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')


for key in THREAD_ENV:os.environ[key]='1'


os.environ['PYTHONDONTWRITEBYTECODE']='1'


os.environ['GIT_OPTIONAL_LOCKS']='0'


from pathlib import Path


OUT=Path(__file__).resolve().parent


ROOT=OUT.parent.parent


NULL=Path(os.devnull).resolve()


VIOLATIONS=[]


def allowed(path):
    p=Path(path).resolve()
    return p==NULL or(p.parent==OUT and p.name.startswith('vector_paired_run_ap_'))


def audit(event,args):
    bad=None
    if event=='open':
        path,mode,flags=args
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or(isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_APPEND|os.O_TRUNC))
        if writing and not isinstance(path,int) and not allowed(path):bad='writable open: '+str(path)
    elif event=='os.rename':
        if not allowed(args[0]) or not allowed(args[1]):bad='rename outside scope'
    elif event in ('os.remove','os.rmdir','os.mkdir','os.link','os.symlink'):bad=event
    if bad:
        VIOLATIONS.append(bad)
        raise RuntimeError('WRITE SCOPE HALT: '+bad)


sys.addaudithook(audit)


sys.path.insert(0,str(ROOT/'simulation'))


import argparse,csv,ctypes,hashlib,io,json,math,subprocess,time,traceback


from copy import deepcopy


from datetime import datetime,timezone


P='vector_paired_run_ap_'


def now():return datetime.now(timezone.utc).isoformat()


def lf(raw):return raw.replace(b'\r\n',b'\n')


def sha(raw):return hashlib.sha256(raw).hexdigest()


def encode(obj):
    if hasattr(obj,'tolist'):return obj.tolist()
    if hasattr(obj,'item'):return obj.item()
    raise TypeError(type(obj).__name__)


def git(*args):
    p=subprocess.run(['git',*args],cwd=ROOT,capture_output=True)
    if p.returncode:raise RuntimeError('Read-only Git failed: '+repr(args)+' '+p.stderr.decode('utf-8',errors='replace'))
    return p.stdout


def metadata(np):
    libraries=[]
    for dll in (Path(np.__file__).resolve().parent.parent/'numpy.libs').iterdir():
        if dll.suffix.lower()=='.dll' and 'openblas' in dll.name.lower():
            lib=ctypes.CDLL(str(dll))
            for name in ('scipy_openblas_get_num_threads64_','openblas_get_num_threads64_','scipy_openblas_get_num_threads','openblas_get_num_threads'):
                try:fn=getattr(lib,name)
                except AttributeError:continue
                fn.argtypes=[];fn.restype=ctypes.c_int
                libraries.append({'library':str(dll),'query':name,'effective_threads':fn()})
                break
    if not libraries or any(r['effective_threads']!=1 for r in libraries):
        raise RuntimeError('Numerical thread limit not verified as one')
    modules={}
    for m in list(sys.modules.values()):
        filename=getattr(m,'__file__',None)
        if filename:
            path=Path(filename).resolve()
            if path.suffix=='.py' and path.is_relative_to(ROOT/'simulation'):
                raw=path.read_bytes()
                modules[path.relative_to(ROOT).as_posix()]={
                    'sha256_raw':sha(raw),'raw_basis':'raw working-tree bytes',
                    'sha256_lf':sha(lf(raw)),'lf_basis':'LF-normalized working-tree bytes'}
    return {'machine':os.environ.get('COMPUTERNAME'),'python':sys.version,'numpy':np.__version__,
            'worker_pid':os.getpid(),'os_cpu_count':os.cpu_count(),
            'process_cpu_count':getattr(os,'process_cpu_count',os.cpu_count)(),
            'operator_cpu_budget':16,'thread_environment':{k:os.environ[k] for k in THREAD_ENV},
            'thread_runtime':libraries,'modules':modules}


def record(model,arm,seed,step,np):
    import metrics
    from agents import total_suppression
    from constants_v2_stage18 import FRONTIER_FLOOR
    before=np.random.get_state()
    count=len(model.novelty_log)
    components=metrics.calculate_h_n(model.novelty_log,composite_method=model.hn_composite_method,return_components=True)
    if count<2:
        raw=components;shape=None;V=None
    else:
        raw,measured_shape,V=components
        shape=model.h_n_shape_latest
    if raw!=model.h_n_latest:
        raise RuntimeError('Continuous check: recorder raw entropy differs from cached h_n_latest at step '+str(step))
    dc=model.datacollector
    avg=float(dc['avg_well_being'][-1]);theta=float(model.theta_capability);transfer=float(model.transfer_state)
    denom=max(0.01,max(0.0,min(1.0,avg))*transfer)
    action=model._last_v2_action
    row={'arm':arm,'seed':seed,'step':step,'novelty_vector_count':count,
         'h_n_latest':float(raw),'h_n_shape_latest':shape,'V':V,'H_N':float(dc['H_N'][-1]),
         'L_t':float(dc['L_t'][-1]),
         'total_suppression':total_suppression(action),'avg_wb':avg,'theta_capability':theta,
         'transfer_state':transfer,'g':max(FRONTIER_FLOOR,theta)/denom,'population':len(model.schedule)}
    row.update({k:float(action[k]) for k in ('x_compute','x_bio_welfare','x_novelty_agency','x_institutional_capacity','x_transfer_comprehension','x_resilience','c_protective','c_suppressive')})
    row.update(adapter_active=bool(dc['v2_attack_active'][-1]),action_modified=bool(dc['v2_attack_action_modified'][-1]),adapter_score=float(dc['v2_adapter_cusum_score'][-1]))
    if arm=='H' and (row['adapter_active'] or row['action_modified']):
        raise RuntimeError('Continuous check: honest adapter/action modification')
    after=np.random.get_state()
    unchanged=before[0]==after[0] and np.array_equal(before[1],after[1]) and before[2:]==after[2:]
    if not unchanged:raise RuntimeError('Gate 6: recorder consumed NumPy randomness')
    return row


def operation_record(event):
    row={'utc':now(),'pid':os.getpid(),**event}
    with (OUT/(P+'io_events_'+str(os.getpid())+'.jsonl')).open('a',encoding='utf-8',newline='\n') as f:
        f.write(json.dumps(row,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())


def retry(operation,path,call):
    start=time.monotonic();attempt=0
    while True:
        try:return call()
        except PermissionError as error:
            code=getattr(error,'winerror',None)
            if code not in (5,32,33) and not(code is None and error.errno==13):raise
            attempt+=1;elapsed=time.monotonic()-start
            operation_record({'operation':operation,'path':str(path),'retry':attempt,'elapsed_seconds':elapsed,
                              'error':repr(error),'exhausted':elapsed>=5.0})
            if elapsed>=5.0:raise
            time.sleep(min(0.025,max(0.0,5.0-elapsed)))


def read(name):
    def load():
        with (OUT/name).open('r',encoding='utf-8') as f:return json.load(f)
    return retry('JSON read',name,load)


def replace_with_retry(source,destination):
    return retry('atomic replacement',destination,lambda:os.replace(source,destination))


def write(name,obj):
    payload=json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=True,allow_nan=False,default=encode)+'\n'
    temp=OUT/(name+'.'+str(os.getpid())+'.tmp')
    with temp.open('w',encoding='utf-8',newline='\n') as f:
        f.write(payload);f.flush();os.fsync(f.fileno())
    replace_with_retry(temp,OUT/name)


def parsed(value):
    if value=='null':return None
    if value=='True':return True
    if value=='False':return False
    try:return int(value)
    except ValueError:
        try:return float(value)
        except ValueError:return value


def log_rows(name):
    with (OUT/name).open(encoding='utf-8',newline='') as f:
        return [{key:parsed(value) for key,value in row.items()} for row in csv.DictReader(f)]


def csv_output(name,rows,fields):
    with (OUT/name).open('x',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader()
        for row in rows:writer.writerow({k:'null' if v is None else v for k,v in row.items()})
        f.flush();os.fsync(f.fileno())


def pins():
    records=[]
    for item in read(P+'plan.json')['pins']:
        actual=sha(lf((ROOT/item['path']).read_bytes()))
        if actual!=item['expected_sha256_lf']:
            raise RuntimeError('Source pin changed: '+item['path'])
        records.append(dict(item,actual_sha256_lf=actual,passed=True))
    return records


def identity():
    names=['executor.py','plan.json','analysis.py']
    return {P+n:sha(lf((OUT/(P+n)).read_bytes())) for n in names}


def check_identity():
    wanted=read(P+'code_identity.json')
    if identity()!=wanted:raise RuntimeError('Executor or plan identity changed')


def task_for(seed,defense):
    return {'vector':'measurement_tampering','mode':'full',
            'machine':os.environ.get('COMPUTERNAME'),
            'parameters':{'base_transition_cost':1.5,'defense_active':defense},
            'replicate':0,'seed':seed}


def all_jobs():
    plan=read(P+'plan.json')
    return [(arm,seed) for arm in plan['arms'] for seed in plan['seeds']]


def job_name(arm,seed):
    return arm['name']+'_'+str(seed)


def dispatch_slots(mode,active,pending):
    return min(max(0,{'normal':15,'work':12}[mode]-active),pending)


def scheduler_checks():
    assert dispatch_slots('normal',0,120)==15
    assert dispatch_slots('work',15,105)==0
    assert dispatch_slots('work',13,105)==0
    assert dispatch_slots('work',12,105)==0
    assert dispatch_slots('work',11,105)==1
    assert dispatch_slots('normal',12,105)==3
    assert dispatch_slots('normal',0,2)==2
    jobs=all_jobs()
    ids=[job_name(a,s) for a,s in jobs]
    assert len(ids)==len(set(ids))==120
    complete={ids[0],ids[-1]}
    pending=[j for j in ids if j not in complete]
    assert len(pending)==118 and complete.isdisjoint(pending)
    assert set(pending)|complete==set(ids)
    for arm in read(P+'plan.json')['arms']:
        assert [s for a,s in jobs if a==arm]==list(range(1835087060,1835087090))
    return {'passed':True,'normal_cap':15,'work_cap':12,
            'graceful_drain_verified':True,'runnable_cap_verified':True,
            'deterministic_assignment_verified':True,'synthetic_resume_preserved':2,
            'synthetic_resume_pending':118}


def check_stop():
    if (OUT/(P+'stop.json')).exists():raise RuntimeError('Batch stop record exists')


def mark_halt(job,error):
    item={'status':'HALTED','job':job,'utc':now(),'reason':repr(error),'traceback':traceback.format_exc()}
    write(P+job+'_failure.json',item)
    if not (OUT/(P+'stop.json')).exists():write(P+'stop.json',item)


def run_job(arm,seed,attempt):
    import numpy as np
    import metrics,model as model_module,run_attack_vector_revalidation_v2 as runner
    check_identity();check_stop()
    start_pins=pins();started=now();clock=time.perf_counter()
    job=job_name(arm,seed);task=task_for(seed,arm['defense_active'])
    assert seed in read(P+'plan.json')['seeds'] and arm in read(P+'plan.json')['arms']
    original_method=model_module.adapt_yield_evaluation
    original_factory=runner._make_model
    info={'completed_steps':0,'step_0_fallback':0,'permitted_after_step_0':0,
          'nonpermitted_fallbacks':0,'previous_novelty_count':None,
          'first_degenerate_step':None,'last_step_result':None}
    partial=P+job+'_steps_attempt'+str(attempt)+'.csv.partial'
    initial=P+job+'_initial_attempt'+str(attempt)+'.json'
    pass_calls=0
    def counted_pass(model,incumbent_u,successor_u,transition_cost):
        nonlocal pass_calls
        pass_calls+=1
        return pass_through(model,incumbent_u,successor_u,transition_cost)
    active_method=original_method if arm['branch_active'] else counted_pass
    with (OUT/partial).open('x',encoding='utf-8',newline='') as handle:
        writer=None
        def observed_factory(received):
            nonlocal writer
            assert received==task
            model,settings=original_factory(received)
            info['configuration']=deepcopy(model.config);info['settings']=deepcopy(settings)
            assert model.random_seed==seed and model.base_transition_cost==1.5
            assert model.cop_independent_eval is arm['defense_active'] and settings['steps']==300
            info['cop_independent_eval']=model.cop_independent_eval
            info['base_transition_cost']=model.base_transition_cost
            write(initial,{'job':job,'arm':arm,'seed':seed,'task':task,
                           'configuration':info['configuration'],'settings':settings,
                           'runtime':metadata(np),'identity':identity(),'attempt':attempt,'utc':now()})
            original_step=model.step
            def observed_step():
                nonlocal writer
                check_stop()
                step=info['completed_steps']
                if step%25==0:pins();check_identity()
                assert model_module.adapt_yield_evaluation is active_method
                before_counter=int(metrics.H_N_SHAPE_FALLBACK_COUNT)
                alive=original_step()
                increase=int(metrics.H_N_SHAPE_FALLBACK_COUNT)-before_counter
                row=record(model,arm['name'],seed,step,np)
                row['shape_fallback_increase']=increase
                count=row['novelty_vector_count'];prev=info['previous_novelty_count']
                permitted=step==0 or count<2 or (prev is not None and prev<2)
                if step==0:info['step_0_fallback']=increase
                elif increase>0 and permitted:info['permitted_after_step_0']+=increase
                elif increase>0:info['nonpermitted_fallbacks']+=1
                if count<2 and info['first_degenerate_step'] is None:info['first_degenerate_step']=step
                if writer is None:
                    writer=csv.DictWriter(handle,fieldnames=list(row),lineterminator='\n')
                    writer.writeheader()
                writer.writerow({k:'null' if v is None else v for k,v in row.items()})
                handle.flush()
                if increase>0 and not permitted:raise RuntimeError('Non-permitted shape fallback at step '+str(step))
                info['previous_novelty_count']=count
                info['completed_steps']+=1;info['last_step_result']=bool(alive)
                if step%10==0:
                    write(P+job+'_progress.json',{'job':job,'arm':arm,'seed':seed,'attempt':attempt,
                          'steps_completed':info['completed_steps'],'utc':now()})
                return alive
            model.step=observed_step
            return model,settings
        try:
            model_module.adapt_yield_evaluation=active_method
            runner._make_model=observed_factory
            row=runner.run_single(task)
        finally:
            runner._make_model=original_factory
            model_module.adapt_yield_evaluation=original_method
        assert runner._make_model is original_factory
        assert model_module.adapt_yield_evaluation is original_method
        handle.flush();os.fsync(handle.fileno())
    assert row['steps_completed']==info['completed_steps']
    assert row['seed']==seed and row['defense_active']==arm['defense_active']
    end_reason='step_returned_false' if not info['last_step_result'] else 'step_limit'
    assert end_reason=='step_returned_false' or info['completed_steps']==300
    final=partial.removesuffix('.partial')
    replace_with_retry(OUT/partial,OUT/final)
    row.update(branch_active=arm['branch_active'],end_reason=end_reason,
               passthrough_call_count=None if arm['branch_active'] else pass_calls,
               executor_elapsed_seconds=time.perf_counter()-clock)
    rawname=P+job+'_row_attempt'+str(attempt)+'.json'
    write(rawname,row)
    result={'status':'COMPLETE','job':job,'arm':arm,'seed':seed,'attempt':attempt,
            'row':row,'task':task,'configuration':info['configuration'],'settings':info['settings'],
            'base_transition_cost':info['base_transition_cost'],'cop_independent_eval':info['cop_independent_eval'],
            'steps_completed':info['completed_steps'],'end_reason':end_reason,
            'identity':identity(),'started_utc':started,'completed_utc':now(),
            'raw_row':rawname,'raw_row_sha256_lf':sha(lf((OUT/rawname).read_bytes())),
            'raw_log':final,'raw_log_sha256_lf':sha(lf((OUT/final).read_bytes())),
            'shape_fallback_increase_step_0':info['step_0_fallback'],
            'shape_fallback_permitted_increase_after_step_0':info['permitted_after_step_0'],
            'shape_fallback_nonpermitted_increase_count':info['nonpermitted_fallbacks'],
            'first_fewer_than_two_novelty_vectors_step':info['first_degenerate_step'],
            'recorder_rng_unchanged_calls':info['completed_steps'],
            'raw_entropy_exact_matches':info['completed_steps'],
            'production_method_restored':True,'production_binding_restored':True,
            'passthrough_call_count':None if arm['branch_active'] else pass_calls,'continuous_checks_passed':True,
            'source_pins_start':start_pins,'source_pins_end':pins(),'runtime':metadata(np)}
    check_identity()
    write(P+job+'_complete.json',result)


def completed(arm,seed):
    name=P+job_name(arm,seed)+'_complete.json'
    if not (OUT/name).exists():return None
    item=read(name)
    if item['status']!='COMPLETE' or item['arm']!=arm or item['seed']!=seed:
        raise RuntimeError('Completion identity mismatch: '+name)
    if item['identity']!=identity():raise RuntimeError('Completion code identity mismatch: '+name)
    for field,hashfield in (('raw_log','raw_log_sha256_lf'),('raw_row','raw_row_sha256_lf')):
        path=OUT/item[field]
        if path.parent!=OUT or not path.name.startswith(P):raise RuntimeError('Completion path mismatch')
        if sha(lf(path.read_bytes()))!=item[hashfield]:raise RuntimeError('Completion output hash mismatch: '+name)
    if read(item['raw_row'])!=item['row']:raise RuntimeError('Completion row mismatch')
    if not item['continuous_checks_passed'] or not item['production_method_restored']:
        raise RuntimeError('Completion check failed: '+name)
    return item


def batch():
    check_stop();check_identity();pins()
    if read(P+'gates.json')['passed'] is not True:raise RuntimeError('Gates did not pass')
    pending=[];preserved=[];restarts=[]
    for arm,seed in all_jobs():
        if completed(arm,seed) is not None:preserved.append(job_name(arm,seed));continue
        job=job_name(arm,seed);progress=OUT/(P+job+'_progress.json')
        attempt=1
        if progress.exists():
            previous=read(progress.name);attempt=previous['attempt']+1
            partial=OUT/(P+job+'_steps_attempt'+str(previous['attempt'])+'.csv.partial')
            if partial.exists():
                retained=OUT/(P+job+'_steps_attempt'+str(previous['attempt'])+'.retained.partial')
                if retained.exists():raise RuntimeError('Retained partial already exists')
                replace_with_retry(partial,retained)
            restarts.append({'job':job,'seed':seed,'arm':arm,'new_attempt':attempt,
                             'reason':'Operational interruption; restart from original seed at step 0'})
        pending.append((arm,seed,attempt))
    control=OUT/(P+'control.json')
    if not control.exists():write(control.name,{'mode':'normal','utc':now()})
    mode=read(control.name)['mode']
    active={};finished=len(preserved);peak=0;mode_events=[{'utc':now(),'mode':mode}]
    write(P+'resumption.json',{'preserved':preserved,'restarts':restarts,'newly_launched_count':len(pending)-len(restarts)})
    last_print=0
    while pending or active:
        if (OUT/(P+'stop.json')).exists():
            for proc in active.values():proc.wait()
            raise RuntimeError('Batch halted; see stop record')
        requested=read(control.name)['mode']
        if requested not in ('normal','work'):raise RuntimeError('Invalid runtime mode')
        if requested!=mode:
            mode=requested;mode_events.append({'utc':now(),'mode':mode,'active_workers':len(active)})
        for job,proc in list(active.items()):
            rc=proc.poll()
            if rc is None:continue
            if rc!=0:
                raise RuntimeError('Worker exited nonzero: '+job+' exit '+str(rc))
            arm,seed=next((a,s) for a,s in all_jobs() if job_name(a,s)==job)
            if completed(arm,seed) is None:raise RuntimeError('Worker has no completion record: '+job)
            del active[job];finished+=1
        slots=dispatch_slots(mode,len(active),len(pending))
        for _ in range(slots):
            arm,seed,attempt=pending.pop(0);job=job_name(arm,seed)
            cmd=[sys.executable,'-B',str(Path(__file__).resolve()),'worker',
                 '--arm',arm['name'],'--seed',str(seed),'--attempt',str(attempt)]
            active[job]=subprocess.Popen(cmd,cwd=ROOT,stdin=subprocess.DEVNULL,
                          stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                          creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        peak=max(peak,len(active))
        status={'state':'RUNNING' if pending or active else 'COMPLETE','utc':now(),
                'completed':finished,'running':len(active),'pending':len(pending),
                'running_jobs':list(active),'mode':mode,'worker_cap':{'normal':15,'work':12}[mode],
                'peak_active_workers':peak,'mode_events':mode_events}
        write(P+'status.json',status)
        if time.monotonic()-last_print>=30:
            pass
            last_print=time.monotonic()
        if pending or active:time.sleep(1)
    assert finished==120
    write(P+'execution.json',{'status':'COMPLETE','runs':finished,'peak_active_workers':peak,
          'mode_events':mode_events,'preserved_jobs':preserved,'resumed_jobs':restarts,
          'completed_utc':now(),'source_pins_end':pins(),'identity':identity()})
    pass



def pass_through(model, incumbent_u, successor_u, transition_cost):
    honest_fires = (float(successor_u) - float(incumbent_u)) > float(
        transition_cost
    )
    return float(incumbent_u), float(successor_u), honest_fires

def binding_gate(np):
    import metrics,model as model_module,attack_adapter_v2 as adapter
    import run_attack_vector_revalidation_v2 as runner
    original=model_module.adapt_yield_evaluation
    assert original is adapter.adapt_yield_evaluation
    task=task_for(1835087060,False)
    model,settings=runner._make_model(task)
    calls=0
    def counted_pass(model,incumbent_u,successor_u,transition_cost):
        nonlocal calls
        calls+=1
        return pass_through(model,incumbent_u,successor_u,transition_cost)
    rows=[];previous=None;delta0=0;after0=0
    try:
        model_module.adapt_yield_evaluation=counted_pass
        for step in range(60):
            check_stop();pins();check_identity()
            before=int(metrics.H_N_SHAPE_FALLBACK_COUNT)
            alive=model.step()
            increase=int(metrics.H_N_SHAPE_FALLBACK_COUNT)-before
            row=record(model,'gate_binding',1835087060,step,np)
            row['shape_fallback_increase']=increase
            count=row['novelty_vector_count']
            permitted=step==0 or count<2 or (previous is not None and previous<2)
            assert increase==0 or permitted,'Non-permitted gate shape fallback'
            if step==0:delta0=increase
            else:after0+=increase
            rows.append(row);previous=count
            if not alive:break
    finally:model_module.adapt_yield_evaluation=original
    restored=model_module.adapt_yield_evaluation is original
    assert restored and model_module.adapt_yield_evaluation is adapter.adapt_yield_evaluation
    assert calls>=1,'Pass-through binding was never reached'
    assert len(rows)==60,'Binding gate did not complete 60 steps'
    csv_output(P+'gate_binding_steps.csv',rows,list(rows[0]))
    evidence={'passed':True,'seed':1835087060,'defense_active':False,'steps_completed':len(rows),
              'passthrough_call_count':calls,'production_binding_restored':restored,
              'configuration':model.config,'settings':settings,'base_transition_cost':model.base_transition_cost,
              'shape_fallback_increase_step_0':delta0,'shape_fallback_permitted_increase_after_step_0':after0,
              'shape_fallback_nonpermitted_increase_count':0,
              'raw_entropy_exact_matches':len(rows),'recorder_rng_unchanged_calls':len(rows),
              'runtime':metadata(np),'identity':identity(),'source_pins_end':pins()}
    write(P+'gate_binding.json',evidence)
    return evidence

def gates():
    import numpy as np
    import model as model_module,attack_adapter_v2 as adapter
    import run_attack_vector_revalidation_v2 as runner
    from types import SimpleNamespace
    import inspect
    check_identity();source_start=pins()
    original=model_module.adapt_yield_evaluation
    assert original is adapter.adapt_yield_evaluation
    assert inspect.signature(original)==inspect.signature(pass_through)
    np.random.seed(20260918)
    cases=[]
    def display(values):
        return [str(v) if isinstance(v,float) and not math.isfinite(v) else v for v in values]
    for i in range(24):
        inc=float(np.random.uniform(1.0,3.0))
        cost=float(np.random.uniform(0.5,2.0))
        succ=inc+cost+(-0.25,0.0,0.25)[i%3]
        honest=(float(succ)-float(inc))>float(cost)
        event=adapter._empty_event('measurement_tampering',50+i)
        event['active']=True
        base=SimpleNamespace(attack_vector_v2='measurement_tampering',
               cop_independent_eval=False,v2_adapter_step_event=event,
               config={'attack_vector_v2':'measurement_tampering','attack_step':50},
               untouched={'nested':[i,True,None]})
        before=deepcopy(vars(base))
        try:
            model_module.adapt_yield_evaluation=pass_through
            result=model_module.adapt_yield_evaluation(base,inc,succ,cost)
        finally:model_module.adapt_yield_evaluation=original
        assert result==(float(inc),float(succ),honest)
        assert vars(base)==before and base.v2_adapter_step_event==before['v2_adapter_step_event']
        off=deepcopy(base);off_result=original(off,inc,succ,cost)
        assert off_result[0]!=inc and off_result[1]!=succ
        on=deepcopy(base);on.cop_independent_eval=True
        on_result=original(on,inc,succ,cost)
        assert on_result==(float(inc),float(succ),honest)
        cases.append({'index':i,'incumbent_u':inc,'successor_u':succ,'transition_cost':cost,
                      'expected_honest_fires':honest,'control_result':display(result),
                      'control_before':before,'control_after':vars(base),'control_exact':True,
                      'production_defense_off_result':display(off_result),
                      'production_defense_off_values_differ':True,
                      'production_defense_off_event':off.v2_adapter_step_event,
                      'production_defense_on_result':display(on_result),
                      'production_defense_on_inputs_exact':True,
                      'production_defense_on_event':on.v2_adapter_step_event,
                      'production_binding_restored':model_module.adapt_yield_evaluation is original})
    construction=[]
    built=runner.build_tasks('measurement_tampering','full',1,os.environ.get('COMPUTERNAME'))
    factory=runner.GardenModel
    for defense in (False,True):
        direct=task_for(1835087060,defense)
        selected=[t for t in built if t['parameters']==direct['parameters']]
        assert len(selected)==1
        own=deepcopy(selected[0]);own['seed']=direct['seed']
        assert direct==own
        kwargs_seen=[]
        def capture_constructor(**kwargs):
            snapshot=deepcopy({k:v for k,v in kwargs.items() if k!='successor_ai'})
            successor=kwargs.get('successor_ai')
            if successor is not None:
                snapshot['successor_ai']={k:deepcopy(getattr(successor,k)) for k in ('policy','generation','capability','config')}
            kwargs_seen.append(snapshot)
            return factory(**kwargs)
        try:
            runner.GardenModel=capture_constructor
            m1,s1=runner._make_model(direct)
            m2,s2=runner._make_model(own)
        finally:runner.GardenModel=factory
        scalars=lambda m:{k:v for k,v in vars(m).items() if v is None or type(v) in (bool,int,float,str)}
        assert kwargs_seen[0]==kwargs_seen[1]
        assert m1.config==m2.config and s1==s2 and scalars(m1)==scalars(m2)
        assert m1.base_transition_cost==1.5 and s1['steps']==300
        assert m1.cop_independent_eval is defense and m1.random_seed==1835087060
        assert m1.config['attack_step']==50 and s1['n_candidates_v2']==300 and s1['rollout_steps_v2']==20
        construction.append({'defense_active':defense,'task':direct,'runner_build_task':own,
                             'constructor_kwargs':kwargs_seen,'configuration':m1.config,
                             'scalar_attributes':scalars(m1),'settings':s1,
                             'all_fields_equal':True,'model_steps':0})
    binding=binding_gate(np)
    result={'passed':True,'utc':now(),'inertness_numpy_seed':20260918,
            'inertness_cases':cases,'construction':construction,'binding_reached':binding,
            'scheduler':scheduler_checks(),'source_pins_start':source_start,
            'source_pins_end':pins(),'runtime':metadata(np),'identity':identity(),
            'null_device_exemption':True,'bytecode_disabled':sys.dont_write_bytecode}
    write(P+'gates.json',result)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['gates','batch','worker','all'])
    parser.add_argument('--arm')
    parser.add_argument('--seed',type=int)
    parser.add_argument('--attempt',type=int,default=1)
    args=parser.parse_args();job=args.command
    try:
        if args.command=='gates':gates()
        elif args.command=='batch':batch()
        elif args.command=='all':
            gates();batch()
            result=subprocess.run([sys.executable,'-B',str(OUT/(P+'analysis.py'))],
                                  cwd=ROOT,capture_output=True,text=True)
            if result.returncode:raise RuntimeError('Analysis failed: '+result.stdout+' '+result.stderr)
            print(result.stdout.strip(),flush=True)
        else:
            arm=next(a for a in read(P+'plan.json')['arms'] if a['name']==args.arm)
            job=job_name(arm,args.seed)
            run_job(arm,args.seed,args.attempt)
    except BaseException as error:
        mark_halt(job,error)
        if args.command in ('all','gates','batch'):
            subprocess.run([sys.executable,'-B',str(OUT/(P+'analysis.py')),'--halt'],cwd=ROOT)
        print(traceback.format_exc(),file=sys.stderr,flush=True)
        return 1
    return 0

if __name__=='__main__':
    raise SystemExit(main())
