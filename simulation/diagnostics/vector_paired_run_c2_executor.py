"""Execute registered stage C Biological Veto Capture counts under a write guard."""


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
DELETE_ALLOWED=set()


def allowed(path):
    p=Path(path).resolve()
    return p==NULL or(p.parent==OUT and p.name.startswith('vector_paired_run_c2_'))


def audit(event,args):
    bad=None
    if event=='open':
        path,mode,flags=args
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or(isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_APPEND|os.O_TRUNC))
        if writing and not isinstance(path,int) and not allowed(path):bad='writable open: '+str(path)
    elif event=='os.rename':
        if not allowed(args[0]) or not allowed(args[1]):bad='rename outside scope'
    elif event=='os.remove':
        if str(Path(args[0]).resolve()) not in DELETE_ALLOWED:bad=event
    elif event in ('os.rmdir','os.mkdir','os.link','os.symlink'):bad=event
    if bad:
        VIOLATIONS.append(bad)
        raise RuntimeError('WRITE SCOPE HALT: '+bad)


sys.addaudithook(audit)


sys.path.insert(0,str(ROOT/'simulation'))


import argparse,csv,ctypes,hashlib,io,json,math,subprocess,time,traceback


from copy import deepcopy


from datetime import datetime,timezone


P='vector_paired_run_c2_'


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



VECTOR='biological_veto_capture'
SEEDS=list(range(1835087200,1835087500))
PARAMETERS={
 'as_published':dict(dependency_rate=0.05,capture_strength=1.0,rotation_interval=10,defense_mode='both',defense_active=True),
 'zero_strength':dict(dependency_rate=0.05,capture_strength=0.0,rotation_interval=10,defense_mode='both',defense_active=True),
 'zero_dependency':dict(dependency_rate=0.0,capture_strength=1.0,rotation_interval=10,defense_mode='both',defense_active=True)}
BINDINGS=('adapt_v2_action','adapt_yield_evaluation','ratify_v2_yield')

def task_for(arm,seed):
    return dict(vector=VECTOR,mode='full',machine=os.environ.get('COMPUTERNAME'),
                parameters=deepcopy(PARAMETERS[arm]),replicate=0,seed=seed)

def all_jobs():return [(a,s) for a in sorted(PARAMETERS) for s in SEEDS]
def job_name(arm,seed):return arm+'_'+str(seed)
def dispatch_slots(mode,active,pending):return min(max(0,{'normal':15,'work':12}[mode]-active),pending)

def scheduler_checks():
    assert dispatch_slots('normal',0,900)==15
    assert dispatch_slots('work',15,800)==0
    assert dispatch_slots('work',12,800)==0
    assert dispatch_slots('work',11,800)==1
    assert dispatch_slots('normal',12,800)==3
    assert dispatch_slots('normal',0,2)==2
    jobs=all_jobs();assert len(set(jobs))==len(jobs)==900
    for arm in PARAMETERS:assert [s for a,s in jobs if a==arm]==SEEDS
    complete={jobs[0],jobs[-1]}
    pending=[j for j in jobs if j not in complete]
    assert len(pending)==898 and complete.isdisjoint(pending)
    assert set(pending)|complete==set(jobs)
    return dict(passed=True,normal_cap=15,work_cap=12,deterministic_assignment=True,
                graceful_mode_drain=True,synthetic_resume_preserved=2,synthetic_resume_pending=898)

def full_pins():
    records=[]
    for item in read(P+'plan.json')['pins']:
        path=item['path'];blob=git('cat-file','blob','HEAD:'+path)
        a=sha(lf(blob));b=sha(lf((ROOT/path).read_bytes()))
        assert a==b==item['expected_sha256_lf'],'Source pin changed: '+path
        records.append(dict(item,committed_sha256_lf=a,working_tree_sha256_lf=b,
                            committed_blob_sha1=git('rev-parse','HEAD:'+path).decode().strip(),passed=True))
    return records

def binding_check(mm,adapter,originals):
    for name in BINDINGS:
        assert getattr(mm,name) is originals[name] is getattr(adapter,name),'Production binding identity: '+name

def configured(model,task,settings):
    p=task['parameters']
    assert model.random_seed==task['seed']
    assert model.n_validators==len(model.validators)==5
    assert model.base_validator_accuracy==0.8
    assert model.rotation_interval==p['rotation_interval']==10
    assert model.dependency_rate==p['dependency_rate']
    assert model.capture_strength==p['capture_strength']
    assert model.cop_independence_monitoring is True and model.cop_veto_capture is True
    assert model.is_v2_mode is True and model.use_cop is True
    assert model.config['attack_step']==50 and settings['steps']==300
    assert settings['n_candidates_v2']==300 and settings['rollout_steps_v2']==20
    return dict(configuration=deepcopy(model.config),settings=deepcopy(settings),
                n_validators=model.n_validators,base_validator_accuracy=model.base_validator_accuracy,
                rotation_interval=model.rotation_interval,dependency_rate=model.dependency_rate,
                capture_strength=model.capture_strength)

def monitoring_fixture():
    monitor=sys.monitoring;tool=monitor.PROFILER_ID
    assert monitor.get_tool(tool) is None
    monitor.use_tool_id(tool,'stage_c_observer_fixture')
    seen=[]
    def probe():return 7
    def start(code,offset):seen.append('start')
    def returned(code,offset,value):seen.append(value)
    try:
        monitor.register_callback(tool,monitor.events.PY_START,start)
        monitor.register_callback(tool,monitor.events.PY_RETURN,returned)
        monitor.set_local_events(tool,probe.__code__,monitor.events.PY_START|monitor.events.PY_RETURN)
        assert probe()==7 and seen==['start',7]
    finally:
        monitor.set_local_events(tool,probe.__code__,0)
        monitor.free_tool_id(tool)
    return dict(passed=True,mechanism='sys.monitoring local events; no production binding replacement',events=seen)

def gates():
    import numpy as np,model as mm,attack_adapter_v2 as adapter
    import run_attack_vector_revalidation_v2 as runner
    runtime=metadata(np)
    originals={n:getattr(mm,n) for n in BINDINGS}
    binding_check(mm,adapter,originals)
    assert runner.DEFAULT_STEPS[VECTOR]==300
    template=next(t for t in runner.build_tasks(VECTOR,'full',1,os.environ.get('COMPUTERNAME'))
                  if t['parameters']==PARAMETERS['as_published'])
    construction=[]
    for arm,p in PARAMETERS.items():
        task=task_for(arm,SEEDS[0])
        expected=deepcopy(template)
        expected['seed']=SEEDS[0];expected['parameters']=deepcopy(p)
        assert task==expected
        first,settings=runner._make_model(task)
        reference,ref_settings=runner._make_model(expected)
        evidence=configured(first,task,settings)
        other=configured(reference,expected,ref_settings)
        assert evidence==other and first.config==reference.config
        assert first.validators==reference.validators
        construction.append(dict(arm=arm,task=task,reference_task=expected,
                                 exact_configuration_match=True,**evidence))
    assert {k for k in PARAMETERS['as_published'] if PARAMETERS['as_published'][k]!=PARAMETERS['zero_strength'][k]}=={'capture_strength'}
    assert {k for k in PARAMETERS['as_published'] if PARAMETERS['as_published'][k]!=PARAMETERS['zero_dependency'][k]}=={'dependency_rate'}
    accuracy=[]
    for arm in ('zero_strength','zero_dependency'):
        p=PARAMETERS[arm]
        values=[]
        for age in range(301):
            dependency=min(1.0,age*p['dependency_rate'])
            effective=max(0.0,0.8*(1.0-dependency*p['capture_strength']))
            assert effective==0.8
            values.append(effective)
        accuracy.append(dict(arm=arm,completed_steps_examined=list(range(301)),effective_accuracy=values))
    binding_check(mm,adapter,originals)
    result=dict(passed=True,construction=construction,arm_distinctness=dict(passed=True,accuracy=accuracy),
                no_wrapper_installed=dict(passed=True,names=list(BINDINGS)),
                source_pins=full_pins(),monitoring=monitoring_fixture(),scheduler=scheduler_checks(),runtime=runtime)
    write(P+'gates.json',result)

def check_stop():
    if (OUT/(P+'stop.json')).exists():raise RuntimeError('Batch stop record exists')

def mark_halt(job,error):
    item=dict(status='HALTED',job=job,utc=now(),reason=repr(error),traceback=traceback.format_exc())
    write(P+job+'_failure.json',item)
    if not (OUT/(P+'stop.json')).exists():write(P+'stop.json',item)

def csv_bytes(row,fields,header=False):
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n')
    if header:writer.writeheader()
    writer.writerow({k:'null' if row[k] is None else row[k] for k in fields})
    return stream.getvalue().encode('utf-8')

def run_job(arm,seed,attempt):
    import numpy as np,metrics,model as mm,attack_adapter_v2 as adapter
    import run_attack_vector_revalidation_v2 as runner
    assert arm in PARAMETERS and seed in SEEDS
    check_identity();check_stop();start_pins=pins()
    task=task_for(arm,seed);job=job_name(arm,seed);started=now();clock=time.perf_counter()
    originals={n:getattr(mm,n) for n in BINDINGS}
    factory=runner._make_model;step_method=mm.GardenModel.step
    binding_check(mm,adapter,originals)
    runtime=metadata(np)
    info=dict(completed_steps=0,previous_novelty_count=None,shape_fallback_step_0=0,
              shape_fallback_permitted_after_step_0=0,shape_fallback_nonpermitted=0,
              raw_entropy_exact_matches=0,recorder_rng_unchanged_calls=0,last_step_result=None)
    model=None
    initial=P+job+'_initial_attempt'+str(attempt)+'.json'
    progress=P+job+'_progress_attempt'+str(attempt)+'.json'
    def started_step(code,offset):
        check_stop();binding_check(mm,adapter,originals)
        if info['completed_steps']%25==0:pins();check_identity()
        info['fallback_before']=int(metrics.H_N_SHAPE_FALLBACK_COUNT)
    def returned(code,offset,value):
        nonlocal model
        if code is factory.__code__:
            model,settings=value
            info.update(configured(model,task,settings))
            write(initial,dict(job=job,arm=arm,seed=seed,task=task,runtime=runtime,identity=identity(),
                               attempt=attempt,utc=now(),configuration=info['configuration'],settings=settings))
            return
        assert code is step_method.__code__ and model is not None
        step=info['completed_steps']
        increase=int(metrics.H_N_SHAPE_FALLBACK_COUNT)-info['fallback_before']
        before=np.random.get_state()
        count=len(model.novelty_log)
        components=metrics.calculate_h_n(model.novelty_log,composite_method=model.hn_composite_method,return_components=True)
        raw=components if count<2 else components[0]
        assert raw==model.h_n_latest,'Continuous raw entropy mismatch'
        after=np.random.get_state()
        assert before[0]==after[0] and np.array_equal(before[1],after[1]) and before[2:]==after[2:],'Recorder changed RNG'
        previous=info['previous_novelty_count']
        permitted=step==0 or count<2 or (previous is not None and previous<2)
        if step==0:info['shape_fallback_step_0']=increase
        elif increase>0 and permitted:info['shape_fallback_permitted_after_step_0']+=increase
        elif increase>0:
            info['shape_fallback_nonpermitted']+=1
            raise RuntimeError('Non-permitted shape fallback at step '+str(step))
        info['previous_novelty_count']=count
        info['raw_entropy_exact_matches']+=1;info['recorder_rng_unchanged_calls']+=1
        info['completed_steps']+=1;info['last_step_result']=bool(value)
        assert len(model.datacollector['population'])==info['completed_steps']
        binding_check(mm,adapter,originals)
        if step%10==0 or not value:
            write(progress,dict(job=job,arm=arm,seed=seed,attempt=attempt,steps_completed=info['completed_steps'],utc=now()))
    monitor=sys.monitoring;tool=monitor.PROFILER_ID
    assert monitor.get_tool(tool) is None
    monitor.use_tool_id(tool,'stage_c_observer')
    try:
        monitor.register_callback(tool,monitor.events.PY_START,started_step)
        monitor.register_callback(tool,monitor.events.PY_RETURN,returned)
        monitor.set_local_events(tool,factory.__code__,monitor.events.PY_RETURN)
        monitor.set_local_events(tool,step_method.__code__,monitor.events.PY_START|monitor.events.PY_RETURN)
        row=runner.run_single(task)
    finally:
        monitor.set_local_events(tool,factory.__code__,0)
        monitor.set_local_events(tool,step_method.__code__,0)
        monitor.free_tool_id(tool)
    assert runner._make_model is factory and mm.GardenModel.step is step_method
    binding_check(mm,adapter,originals)
    assert row['steps_completed']==info['completed_steps']
    assert row['seed']==seed and row['steps_requested']==300
    assert 0<info['completed_steps']<=300
    end_reason='step_returned_false' if not info['last_step_result'] else 'step_limit'
    assert end_reason=='step_returned_false' or info['completed_steps']==300
    returned_fields=list(row)
    row.update(arm=arm,end_reason=end_reason,executor_elapsed_seconds=time.perf_counter()-clock)
    fields=['arm','seed']+[k for k in row if k not in ('arm','seed')]
    raw_name=P+job+'_row_attempt'+str(attempt)+'.csv'
    with (OUT/raw_name).open('xb') as handle:
        handle.write(csv_bytes(row,fields,True));handle.flush();os.fsync(handle.fileno())
    check_identity();end_pins=pins()
    result=dict(status='COMPLETE',job=job,arm=arm,seed=seed,attempt=attempt,row=row,returned_fields=returned_fields,
                fields=fields,task=task,configuration=info['configuration'],settings=info['settings'],
                steps_completed=info['completed_steps'],recorded_steps=row['steps_completed'],end_reason=end_reason,
                initial_file=initial,progress_file=progress,identity=identity(),started_utc=started,completed_utc=now(),
                raw_row=raw_name,raw_file_sha256_lf=sha(lf((OUT/raw_name).read_bytes())),
                recorded_row_sha256_lf=sha(csv_bytes(row,fields)),continuous_checks=info,
                no_wrapper_installed=True,production_bindings_verified=True,
                source_pins_start=start_pins,source_pins_end=end_pins,runtime=runtime)
    write(P+job+'_complete.json',result)

def completed(arm,seed):
    name=P+job_name(arm,seed)+'_complete.json'
    if not (OUT/name).exists():return None
    item=read(name)
    assert item['status']=='COMPLETE' and item['arm']==arm and item['seed']==seed
    assert item['identity']==identity(),'Completion identity mismatch'
    assert item['task']==task_for(arm,seed)
    assert item['production_bindings_verified'] and item['no_wrapper_installed']
    assert item['recorded_steps']==item['steps_completed']
    if not (OUT/(P+'merge.json')).exists():
        assert sha(lf((OUT/item['raw_row']).read_bytes()))==item['raw_file_sha256_lf']
    return item

def batch():
    check_stop();check_identity();pins()
    assert read(P+'gates.json')['passed']
    pending=[];preserved=[];restarts=[]
    for arm,seed in all_jobs():
        if completed(arm,seed) is not None:preserved.append(job_name(arm,seed));continue
        job=job_name(arm,seed)
        attempts=list(OUT.glob(P+job+'_initial_attempt*.json'))
        attempt=1
        if attempts:
            attempt=max(read(p.name)['attempt'] for p in attempts)+1
            restarts.append(dict(job=job,arm=arm,seed=seed,new_attempt=attempt,
                                 reason='Operational interruption; previous attempt retained; restart from step 0'))
        pending.append((arm,seed,attempt))
    control=OUT/(P+'control.json')
    if not control.exists():write(control.name,dict(mode='normal',utc=now()))
    mode=read(control.name)['mode'];active={};finished=len(preserved);peak=0
    mode_events=[dict(utc=now(),mode=mode)]
    write(P+'resumption.json',dict(preserved=preserved,restarts=restarts))
    try:
        while pending or active:
            check_stop()
            requested=read(control.name)['mode']
            assert requested in ('normal','work')
            if requested!=mode:
                mode=requested;mode_events.append(dict(utc=now(),mode=mode,active_workers=len(active)))
            for job,(proc,arm,seed) in list(active.items()):
                rc=proc.poll()
                if rc is None:continue
                assert rc==0,'Worker exited '+str(rc)+': '+job
                assert completed(arm,seed) is not None
                del active[job];finished+=1
            for _ in range(dispatch_slots(mode,len(active),len(pending))):
                arm,seed,attempt=pending.pop(0);job=job_name(arm,seed)
                cmd=[sys.executable,'-B',str(Path(__file__).resolve()),'worker','--arm',arm,'--seed',str(seed),'--attempt',str(attempt)]
                proc=subprocess.Popen(cmd,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                active[job]=(proc,arm,seed)
            peak=max(peak,len(active));assert len(active)<=15
            write(P+'progress.json',dict(status='RUNNING',completed=finished,running=len(active),pending=len(pending),
                                        mode=mode,cap={'normal':15,'work':12}[mode],peak_workers=peak,utc=now(),mode_events=mode_events))
            time.sleep(1)
    except BaseException as error:
        mark_halt('batch',error)
        for proc,arm,seed in active.values():proc.wait()
        raise
    write(P+'execution.json',dict(status='COMPLETE',completed=finished,peak_workers=peak,mode=mode,mode_events=mode_events,
                                  normal_cap=15,work_cap=12,operator_cpu_budget=16))
    write(P+'progress.json',dict(status='COMPLETE',completed=finished,running=0,pending=0,utc=now()))

def merge():
    records=[completed(a,s) for a,s in all_jobs()]
    assert len(records)==900 and all(r is not None for r in records)
    fields=records[0]['fields'];assert all(r['fields']==fields for r in records)
    rows_path=OUT/(P+'runs.csv');completions_path=OUT/(P+'completions.jsonl')
    with rows_path.open('xb') as out:
        for index,item in enumerate(records):
            out.write(csv_bytes(item['row'],fields,header=index==0))
        out.flush();os.fsync(out.fileno())
    with completions_path.open('x',encoding='utf-8',newline='\n') as out:
        for item in records:out.write(json.dumps(item,sort_keys=True,ensure_ascii=True,allow_nan=False,default=encode)+'\n')
        out.flush();os.fsync(out.fileno())
    with rows_path.open(encoding='utf-8',newline='') as handle:merged=list(csv.DictReader(handle))
    with completions_path.open(encoding='utf-8') as handle:merged_completions=[json.loads(line) for line in handle]
    assert len(merged)==len(merged_completions)==900
    proof=[]
    for item in records:
        found=[r for r in merged if r['arm']==item['arm'] and int(r['seed'])==item['seed']]
        assert len(found)==1
        digest=sha(csv_bytes(found[0],fields))
        assert digest==item['recorded_row_sha256_lf'],'Merge cannot recover recorded row'
        matching=[r for r in merged_completions if r['arm']==item['arm'] and r['seed']==item['seed']]
        assert len(matching)==1 and matching[0]==json.loads(json.dumps(item,default=encode))
        proof.append(dict(arm=item['arm'],seed=item['seed'],row_count=1,recorded_row_sha256_lf=digest,
                          recorded_steps=item['recorded_steps'],completed_steps=item['steps_completed']))
    types={k:type(records[0]['row'][k]).__name__ for k in fields}
    details=dict(verified=True,row_count=900,per_run=proof,fields=fields,field_types=types,
                 runs_sha256_lf=sha(lf(rows_path.read_bytes())),completions_sha256_lf=sha(lf(completions_path.read_bytes())),
                 deleted_by_kind={})
    write(P+'merge.json',details)
    manifest(dict(status='MERGE_VERIFIED',merge=details))
    deletions={}
    for item in records:
        for kind,name in [('row',item['raw_row']),('completion',P+item['job']+'_complete.json'),
                          ('initial',item['initial_file']),('progress',item['progress_file'])]:
            target=OUT/name
            if target.exists():
                DELETE_ALLOWED.add(str(target.resolve()))
                target.unlink()
                DELETE_ALLOWED.remove(str(target.resolve()))
                deletions[kind]=deletions.get(kind,0)+1
    details['deleted_by_kind']=deletions
    write(P+'merge.json',details)

def artifact_inventory():
    rows=[]
    for path in sorted(OUT.glob(P+'*')):
        if path.name==P+'manifest.json' or not path.is_file():continue
        item=dict(path=path.relative_to(ROOT).as_posix(),sha256_lf=sha(lf(path.read_bytes())),basis='LF-normalized bytes')
        if path.suffix=='.csv':
            with path.open(encoding='utf-8',newline='') as f:item['csv_row_count']=sum(1 for _ in csv.DictReader(f))
        elif path.suffix=='.jsonl':
            with path.open(encoding='utf-8') as f:item['jsonl_row_count']=sum(1 for _ in f)
        rows.append(item)
    return rows

def manifest(extra):
    import numpy as np
    plan=read(P+'plan.json')
    events=[]
    for path in OUT.glob(P+'io_events_*.jsonl'):
        with path.open(encoding='utf-8') as f:events.extend(json.loads(line) for line in f)
    result=dict(schema_version='vector-paired-stage-c2-manifest-v1',head=git('rev-parse','HEAD').decode().strip(),
                machine=os.environ.get('COMPUTERNAME'),runtime=metadata(np),source_pins_start=read(P+'preflight.json')['source_readings'],
                source_pins_completion=full_pins(),pre_registration_blob_sha1=plan['pre_registration_blob_sha1'],
                source_provenance=plan['source_provenance'],prior_stage_published=plan['prior_stage_published'],
                retry_events=events,tool_layer_workarounds=plan['tool_layer_workarounds'],
                executor_self_fixes=plan['executor_self_fixes'],t0_stderr_warnings=read(P+'preflight.json')['stderr_warnings'],
                outputs=artifact_inventory(),manifest_self_hash='Omitted to avoid a recursive hash',**extra)
    if (OUT/(P+'execution.json')).exists():result['execution']=read(P+'execution.json')
    if (OUT/(P+'resumption.json')).exists():result['resumption']=read(P+'resumption.json')
    if (OUT/(P+'merge.json')).exists():result['merge']=read(P+'merge.json')
    write(P+'manifest.json',result)

def halt_artifacts(error):
    item=dict(status='HALTED',halt_reason=repr(error),batch_runs_completed=len(list(OUT.glob(P+'*_complete.json'))))
    write(P+'results.json',item)
    text='Stage C attempt 2 status: HALTED.\n\nReason: '+repr(error)+'\n\nNo interpretation is made.\n'
    with (OUT/(P+'report.md')).open('w',encoding='utf-8',newline='\n') as f:f.write(text)
    manifest(item)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('gates','batch','worker','finalize','all'))
    parser.add_argument('--arm');parser.add_argument('--seed',type=int);parser.add_argument('--attempt',type=int,default=1)
    args=parser.parse_args()
    try:
        if args.command=='worker':run_job(args.arm,args.seed,args.attempt);return
        if args.command in ('gates','all'):
            if not (OUT/(P+'code_identity.json')).exists():write(P+'code_identity.json',identity())
            check_identity();gates()
        if args.command in ('batch','all'):batch()
        if args.command in ('finalize','all'):
            merge()
            module_name=P+'analysis'
            import importlib.util
            spec=importlib.util.spec_from_file_location(module_name,OUT/(P+'analysis.py'))
            analysis=importlib.util.module_from_spec(spec);spec.loader.exec_module(analysis)
            analysis.analyze(sys.modules[__name__])
            manifest(dict(status='COMPLETE',batch_runs_completed=900))
        print('Stage C attempt 2 '+args.command+' COMPLETE',flush=True)
    except BaseException as error:
        mark_halt(job_name(args.arm,args.seed) if args.command=='worker' else args.command,error)
        if args.command!='worker':halt_artifacts(error)
        print('Stage C attempt 2 HALTED: '+repr(error),flush=True)
        raise

if __name__=='__main__':main()
