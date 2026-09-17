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
    return p==NULL or(p.parent==OUT and p.name.startswith('detector_run_r3_eval_a2_'))
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

def pins():
    plan=read('detector_run_r3_eval_a2_plan.json');records=[]
    for item in plan['pins']:
        actual=sha(lf((ROOT/item['path']).read_bytes()))
        records.append(dict(item,actual_sha256_lf=actual,passed=actual==item['expected_sha256_lf']))
    code=read(P+'code_identity.json')
    changed=[path for path,wanted in code['files'].items() if sha(lf((ROOT/path).read_bytes()))!=wanted]
    if not all(r['passed'] for r in records) or changed:
        write(P+'source_pin_failure_'+str(os.getpid())+'.json',{'utc':now(),'pins':records,'new_code_changes':changed})
        raise RuntimeError('Source pin changed')
    return records

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

def constructor(seed,honest=False):
    from model import GardenModel
    config={'policy':'optimize_u_sys_v2','random_seed':seed,'phi':10.0,'attack_step':50,'n_candidates_v2':300,'rollout_steps_v2':20,'bootstrap_turn_step_v2':20,'shock_step':0,'shock_magnitude':0.15}
    if not honest:config['attack_vector_v2']='sub_threshold_drift'
    return GardenModel(n_agents=200,ai_policy='sub_threshold_drift',use_cop=True,cop_attribution_check=True,cop_drift_check=True,cop_cusum_drift=False,config=config)

def multiplied(model,action,step,m):
    import attack_adapter_v2 as adapter
    adapted=deepcopy(action)
    attack_step=int(model.config.get('attack_step',0))
    progress=max(1,int(step)-attack_step+1)
    suppressive_increment=min(0.65,progress*0.0065*m)
    welfare_shift=min(0.12,progress*0.0012*m)
    adapted['c_suppressive']=min(0.85,float(adapted['c_suppressive'])+suppressive_increment)
    moved=min(float(adapted['x_bio_welfare']),welfare_shift)
    adapted['x_bio_welfare']-=moved
    adapted['x_compute']+=moved
    return adapter._normalize_action(adapted)

def reallocated(model,action,step,d):
    import attack_adapter_v2 as adapter
    adapted=deepcopy(action)
    moved=min(adapted['x_transfer_comprehension'],d)
    adapted['x_transfer_comprehension']-=moved
    adapted['x_compute']+=moved
    return adapter._normalize_action(adapted)

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


P='detector_run_r3_eval_a2_'


def identity():
    return {'plan_sha256_lf':sha(lf((OUT/(P+'plan.json')).read_bytes())),
            'executor_sha256_lf':sha(lf(Path(__file__).read_bytes())),
            'detector_sha256_lf':sha(lf((ROOT/'simulation/cusum_detector_v2.py').read_bytes()))}

def expected_config(seed,honest=False):
    c={'policy':'optimize_u_sys_v2','random_seed':seed,'phi':10.0,'attack_step':50,
       'n_candidates_v2':300,'rollout_steps_v2':20,'bootstrap_turn_step_v2':20,
       'shock_step':0,'shock_magnitude':0.15,'cop_methodological_diversity':False,
       'cop_cusum_drift':False}
    if not honest:c['attack_vector_v2']='sub_threshold_drift'
    return c

def mark_halt(job,error):
    failure={'job':job,'utc':now(),'halt':str(error),'traceback':traceback.format_exc(),'violations':VIOLATIONS}
    write(P+job+'_failure.json',failure)
    if not (OUT/(P+'stop.json')).exists():write(P+'stop.json',failure)
    print(json.dumps({'status':'HALTED','job':job,'reason':str(error)}),flush=True)

def check_stop():
    if (OUT/(P+'stop.json')).exists():raise RuntimeError('Stopped after another run or gate halted')

def wrapper_gate():
    import numpy as np
    import attack_adapter_v2 as adapter
    from agents import _x_vector_to_action,_constraint_pair_for_index
    from types import SimpleNamespace
    start=pins();rng=np.random.default_rng(20260913);clock=time.perf_counter()
    allocations=list(np.eye(6))+[np.ones(6)/6]+list(rng.dirichlet(np.ones(6),size=193))
    actions=[_x_vector_to_action(x,*_constraint_pair_for_index(i)) for i,x in enumerate(allocations)]
    model=SimpleNamespace(config={'attack_step':50});compared=0
    for i,action in enumerate(actions):
        for step in range(300):
            expected=adapter._apply_sub_threshold_drift(model,action,step)
            actual=multiplied(model,action,step,1.0)
            if expected!=actual:
                write(P+'gate_wrapper_difference.json',{'action_index':i,'step':step,'expected':expected,'actual':actual})
                raise RuntimeError('Gate 4: M1 wrapper differs from production')
            compared+=1
    write(P+'gate_wrapper_result.json',{'passed':True,'gate':4,'synthetic_actions':len(actions),
          'steps_per_action':300,'comparisons':compared,'maximum_key_difference':0.0,'seed':20260913,
          'pins_start':start,'pins_end':pins(),'runtime':metadata(np),'identity':identity(),
          'elapsed_seconds':time.perf_counter()-clock,'utc':now()})

def run_model(job,arm,seed,gate=False,attempt=1):
    import numpy as np
    import metrics,attack_adapter_v2 as adapter
    start_pins=pins();started=now();clock=time.perf_counter();plan=read(P+'plan.json')
    if gate and job=='gate_factory':
        import run_attack_vector_revalidation_v2 as runner
        task={'vector':'sub_threshold_drift','mode':'full','parameters':{'phi':10.0,'defense_active':False},'seed':seed}
        model,settings=runner._make_model(task)
    else:model=constructor(seed,honest=arm=='H')
    configuration=deepcopy(model.config)
    if configuration!=expected_config(seed,arm=='H'):
        write(P+job+'_configuration_difference.json',{'actual':configuration,'expected':expected_config(seed,arm=='H')})
        raise RuntimeError('Construction does not match the fixed configuration')
    if arm=='H' and model.attack_vector_v2 is not None:
        raise RuntimeError('Honest model has an attack vector')
    if not gate and (arm not in plan['arms'] or model.random_seed!=seed or seed not in plan['seeds']):
        raise RuntimeError('Evaluation must use the specified seed and arm')
    horizon=25 if job=='gate_recorder' else (60 if gate and arm=='H' else 300)
    if not gate and arm.startswith('M'):
        multiplier={'M05':0.5,'M1':1.0,'M2':2.0,'M4':4.0}[arm]
        adapter._apply_sub_threshold_drift=lambda model,action,step:multiplied(model,action,step,multiplier)
    elif not gate and arm.startswith('R'):
        shift={'R02':0.02,'R05':0.05,'R10':0.10,'R20':0.20}[arm]
        adapter._apply_sub_threshold_drift=lambda model,action,step:reallocated(model,action,step,shift)
    channels,hazards,medians,constant_checks=constants()
    allocation_rows=[]
    runtime=metadata(np)
    write(P+job+'_initial.json',{'job':job,'arm':arm,'seed':seed,'configuration':configuration,
          'attack_vector_v2':model.attack_vector_v2,'runtime':runtime,'identity':identity(),
          'started_utc':started,'attempt':attempt})
    logname=P+job+'_steps_attempt'+str(attempt)+'.csv.partial'
    rows=0;active=0;modified=0;alive=True;delta0=0;permitted_after=0;nonpermitted=0
    previous_novelty_count=None;first_degenerate_step=None
    with (OUT/logname).open('x',encoding='utf-8',newline='') as f:
        writer=None
        for step in range(horizon):
            check_stop();pins()
            before_counter=int(metrics.H_N_SHAPE_FALLBACK_COUNT)
            alive=model.step()
            increase=int(metrics.H_N_SHAPE_FALLBACK_COUNT)-before_counter
            row=record(model,arm,seed,step,np)
            allocation_rows.append({'arm':arm,'seed':seed,'step':step,'A':registered.allocation_distance(row,medians)})
            count=row['novelty_vector_count']
            row['shape_fallback_increase']=increase
            permitted=step==0 or count<2 or (previous_novelty_count is not None and previous_novelty_count<2)
            if step==0:delta0=increase
            elif increase>0 and permitted:permitted_after+=increase
            elif increase>0:nonpermitted+=1
            if count<2 and first_degenerate_step is None:first_degenerate_step=step
            if writer is None:
                writer=csv.DictWriter(f,fieldnames=list(row),lineterminator='\n');writer.writeheader()
            writer.writerow({k:'null' if v is None else v for k,v in row.items()})
            f.flush();rows+=1
            if increase>0 and not permitted:
                write(P+job+'_fallback_failure.json',{'step':step,'increase':increase,
                      'novelty_vector_count':count,'previous_novelty_vector_count':previous_novelty_count})
                raise RuntimeError('Continuous check: non-permitted shape fallback increase')
            previous_novelty_count=count
            active+=int(row['adapter_active']);modified+=int(row['action_modified'])
            if step%25==0:
                write(P+job+'_progress.json',{'job':job,'arm':arm,'seed':seed,'completed_steps':rows,'target':horizon,'utc':now()})
            if not alive:break
        f.flush();os.fsync(f.fileno())
    if gate and arm=='H' and rows!=horizon:raise RuntimeError('Honest gate probe did not complete its horizon')
    end_pins=pins();final=logname.removesuffix('.partial')
    replace_with_retry(OUT/logname,OUT/final)
    result={'status':'COMPLETE','job':job,'arm':arm,'seed':seed,'paired_honest_seed':seed,
            'configuration':configuration,'constructor':plan['constructor'],'identity':identity(),
            'attempt':attempt,'steps_completed':rows,'end_reason':'extinction' if not alive else 'step_limit',
            'extinct':not bool(alive),'shape_fallback_increase_step_0':delta0,
            'shape_fallback_permitted_increase_after_step_0':permitted_after,
            'shape_fallback_nonpermitted_increase_count':nonpermitted,
            'first_fewer_than_two_novelty_vectors_step':first_degenerate_step,
            'adapter_active_steps':active,'action_modified_steps':modified,
            'recorder_rng_unchanged_calls':rows,'raw_entropy_exact_matches':rows,
            'raw_log':final,'raw_log_sha256':sha((OUT/final).read_bytes()),
            'raw_log_sha256_lf':sha(lf((OUT/final).read_bytes())),'source_pins_start':start_pins,
            'source_pins_end':end_pins,'runtime':metadata(np),'elapsed_seconds':time.perf_counter()-clock,
            'started_utc':started,'completed_utc':now(),'continuous_checks_passed':True}
    allocation_name=P+job+'_allocation_attempt'+str(attempt)+'.csv'
    csv_output(allocation_name,allocation_rows,['arm','seed','step','A'])
    result['allocation_log']=allocation_name
    result['allocation_log_sha256_lf']=sha(lf((OUT/allocation_name).read_bytes()))
    if gate:result['datacollector']=model.datacollector
    else:
        output,detector_summary=evaluate_records(log_rows(final),allocation_rows)
        result.update(detector_summary)
        hb=P+job+'_heartbeats_attempt'+str(attempt)+'.csv'
        alarms=P+job+'_alarms_attempt'+str(attempt)+'.csv'
        csv_output(hb,output['heartbeats'],['record_type','channel','label','threshold','step','heartbeat_counter','start_statistic','candidate_statistic','statistic'])
        csv_output(alarms,output['alarm_records'],['record_type','channel','label','threshold','step','statistic_before_reset','statistic_after_reset'])
        spans=P+job+'_spans_attempt'+str(attempt)+'.csv'
        csv_output(spans,output['span_records'],['g_star_case','g_star_label','g_star','k','start_step','end_step','section_4_caveat'])
        result['detector_logs']={name:sha((OUT/name).read_bytes()) for name in (hb,alarms,spans)}
        result['runtime']=metadata(np)
        result['source_pins_end']=pins()
    write(P+job+('_result.json' if gate else '_complete.json'),result)

def worker(args):
    try:
        if args.job=='gate_wrapper':wrapper_gate()
        elif args.job.startswith('gate_'):
            run_model(args.job,'H' if args.job in ('gate_honest','gate_recorder') else 'GATE_ATTACK',1835086300 if args.job=='gate_recorder' else 1835086199,gate=True)
        else:run_model(args.job,args.arm,args.seed,attempt=args.attempt)
    except BaseException as e:
        mark_halt(args.job,e);raise SystemExit(2)

def dispatch_slots(mode,active,pending):
    cap={'normal':15,'work':12}[mode]
    return min(max(0,cap-active),pending)

def scheduler_checks():
    assert dispatch_slots('normal',0,360)==15
    assert dispatch_slots('work',15,345)==0
    assert dispatch_slots('work',13,345)==0
    assert dispatch_slots('work',12,345)==0
    assert dispatch_slots('work',11,345)==1
    assert dispatch_slots('normal',12,345)==3
    assert dispatch_slots('normal',0,2)==2
    plan=read(P+'plan.json')
    jobs=[(a,s) for a in plan['arms'] for s in plan['seeds']]
    complete={jobs[0],jobs[-1]};pending=[j for j in jobs if j not in complete]
    assert len(jobs)==360 and len(set(jobs))==360 and len(pending)==358
    assert complete.isdisjoint(pending) and set(pending)|complete==set(jobs)
    assert all(s in plan['seeds'] for a,s in reversed(jobs))
    result={'passed':True,'concurrency_caps':[15,12],'work_transition':'drains without dispatch until below 12',
            'normal_transition':'permits dispatch up to 15','runnable_cap_checked':True,
            'deterministic_job_count':len(jobs),'synthetic_resume_complete_count':2,
            'synthetic_resume_pending_count':len(pending),'no_model_steps':True,'utc':now()}
    write(P+'scheduler_checks.json',result)
    return result

def spawn(job,arm=None,seed=None,attempt=1):
    cmd=[sys.executable,'-B',str(Path(__file__).resolve()),'worker','--job',job,'--attempt',str(attempt)]
    if arm is not None:cmd+=['--arm',arm,'--seed',str(seed)]
    return subprocess.Popen(cmd,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def compare_gates():
    factory=read(P+'gate_factory_result.json');common=read(P+'gate_common_result.json')
    first=None;checks=0
    if factory['configuration']!=common['configuration']:
        for key in sorted(set(factory['configuration'])|set(common['configuration'])):
            x=factory['configuration'].get(key);y=common['configuration'].get(key)
            if x!=y:first={'kind':'configuration','field':key,'step':None,'factory':x,'common':y};break
    for field in ('steps_completed','end_reason'):
        if first is None and factory[field]!=common[field]:
            first={'kind':'termination','field':field,'step':None,'factory':factory[field],'common':common[field]}
    with (OUT/factory['raw_log']).open(encoding='utf-8',newline='') as f:ra=list(csv.DictReader(f))
    with (OUT/common['raw_log']).open(encoding='utf-8',newline='') as f:rb=list(csv.DictReader(f))
    if first is None and len(ra)!=len(rb):
        first={'kind':'trajectory_length','field':'steps_completed','step':min(len(ra),len(rb)),'factory':len(ra),'common':len(rb)}
    if first is None:
        for step,(x,y) in enumerate(zip(ra,rb)):
            if list(x)!=list(y):first={'kind':'recorder_fields','field':None,'step':step};break
            for key in x:
                checks+=1
                if x[key]!=y[key]:first={'kind':'recorded_value','field':key,'step':step,'factory':x[key],'common':y[key]};break
            if first is not None:break
    datacollector_checks=0
    if first is None:
        fa=factory['datacollector'];co=common['datacollector']
        if set(fa)!=set(co):first={'kind':'datacollector_keys','step':None,'field':None}
        else:
            for field in sorted(fa):
                if len(fa[field])!=len(co[field]):first={'kind':'datacollector_length','field':field,'step':None};break
                for step,(x,y) in enumerate(zip(fa[field],co[field])):
                    datacollector_checks+=1
                    if x!=y:first={'kind':'datacollector_value','field':field,'step':step,'factory':x,'common':y};break
                if first is not None:break
    honest=read(P+'gate_honest_result.json');wrapper=read(P+'gate_wrapper_result.json')
    results={'gate_2':{'passed':True,'pins':pins()},
             'gate_3':{'passed':first is None,'seed':1835086199,
                       'configuration_equal':factory['configuration']==common['configuration'],
                       'factory_steps_completed':factory['steps_completed'],'common_steps_completed':common['steps_completed'],
                       'factory_end_reason':factory['end_reason'],'common_end_reason':common['end_reason'],
                       'recorder_fields':len(ra[0]),'steps_compared':min(len(ra),len(rb)),
                       'field_value_comparisons':checks,'datacollector_value_comparisons':datacollector_checks,'datacollector_fields':len(factory['datacollector']),'null_encoding':'null','first_difference':first},
             'gate_4':{'passed':wrapper['passed'],'synthetic_actions':wrapper['synthetic_actions'],
                       'steps_per_action':300,'comparisons':wrapper['comparisons'],'maximum_key_difference':wrapper['maximum_key_difference']},
             'gate_5':{'passed':honest['steps_completed']==60 and honest['adapter_active_steps']==honest['action_modified_steps']==0,
                       'attack_vector_v2':read(P+'gate_honest_initial.json')['attack_vector_v2'],
                       'steps':honest['steps_completed'],'adapter_active_steps':honest['adapter_active_steps'],'action_modified_steps':honest['action_modified_steps']},
             'gate_6':{'passed':honest['recorder_rng_unchanged_calls']==60,'identical_rng_calls':honest['recorder_rng_unchanged_calls']},
             'amendment_2':{j:{'step_0':r['shape_fallback_increase_step_0'],
                              'permitted_after_step_0':r['shape_fallback_permitted_increase_after_step_0'],
                              'nonpermitted_increase_count':r['shape_fallback_nonpermitted_increase_count'],
                              'first_fewer_than_two_novelty_vectors_step':r['first_fewer_than_two_novelty_vectors_step'],
                              'raw_entropy_exact_matches':r['raw_entropy_exact_matches']} for j,r in [('factory',factory),('common',common),('honest',honest)]},
             'completed_utc':now(),'identity':identity()}
    results['recorder_conformance']=read(P+'recorder_conformance.json')
    results['constants_conformance']=read(P+'constants_gate.json')
    results['allocation_definition']=read(P+'allocation_gate.json')
    results['passed']=all(results['gate_'+str(i)]['passed'] for i in range(2,7)) and results['recorder_conformance']['passed'] and results['constants_conformance']['passed'] and results['allocation_definition']['passed']
    write(P+'gates.json',results)
    if not results['passed']:raise RuntimeError('T1 gate failed: '+json.dumps(results))
    return results

def gates():
    unit=read(P+'unit_gate.json')
    if not unit['passed'] or unit['identity']!=identity():raise RuntimeError('Detector unit gate must pass before model gates')
    scheduler_checks();write(P+'gate_2_start.json',{'passed':True,'pins':pins(),'utc':now()});check_stop()
    constants_gate()
    jobs=['gate_wrapper','gate_factory','gate_common','gate_honest','gate_recorder']
    active={};done=[];maximum=0
    try:
        for job in jobs:active[job]=spawn(job)
        maximum=len(active)
        while active:
            for job,p in list(active.items()):
                code=p.poll()
                if code is not None:
                    del active[job]
                    if code:raise RuntimeError('Gate worker failed: '+job+' exit '+str(code))
                    done.append(job)
            print(json.dumps({'phase':'T1','completed':len(done),'running':len(active),'pending':0}),flush=True)
            if active:time.sleep(10)
        recorder_conformance()
        allocation_definition_gate()
        result=compare_gates()
        write(P+'gate_execution.json',{'maximum_concurrent_processes':maximum,'simulation_workers':4,'completed_jobs':done,'utc':now()})
        print(json.dumps({'T1':'PASS','gate_3':result['gate_3'],'recorder_conformance':result['recorder_conformance']['passed'],'constants_conformance':result['constants_conformance']['passed'],'allocation_definition':result['allocation_definition']['passed']}),flush=True)
    except BaseException as e:
        mark_halt('gates',e)
        for p in active.values():p.wait()
        raise SystemExit(2)

def completed(job,arm,seed):
    path=OUT/(P+job+'_complete.json')
    if not path.exists():return None
    r=read(path.name)
    if r['status']!='COMPLETE' or r['identity']!=identity() or r['arm']!=arm or r['seed']!=seed:
        raise RuntimeError('Completion identity mismatch: '+job)
    if r['configuration']!=expected_config(seed,arm=='H') or r['shape_fallback_nonpermitted_increase_count']!=0:
        raise RuntimeError('Completion configuration or continuous check mismatch: '+job)
    raw=(OUT/r['raw_log']).read_bytes()
    if sha(raw)!=r['raw_log_sha256']:raise RuntimeError('Completed raw log hash mismatch: '+job)
    records=list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))
    if len(records)!=r['steps_completed'] or any(int(x['seed'])!=seed or x['arm']!=arm or int(x['step'])!=i for i,x in enumerate(records)):
        raise RuntimeError('Completed raw log identity mismatch: '+job)
    if any(count!=r['steps_completed'] for count in r['heartbeat_count'].values()):raise RuntimeError('Completed heartbeat count mismatch: '+job)
    if sha(lf((OUT/r['allocation_log']).read_bytes()))!=r['allocation_log_sha256_lf']:
        raise RuntimeError('Completed allocation log hash mismatch: '+job)
    for name,wanted in r['detector_logs'].items():
        if sha((OUT/name).read_bytes())!=wanted:raise RuntimeError('Completed detector log hash mismatch: '+job)
    return r

def batch():
    check_stop();pins()
    gate_result=read(P+'gates.json')
    if not gate_result['passed'] or gate_result['identity']!=identity():raise RuntimeError('Required gates not passed for this code identity')
    plan=read(P+'plan.json');jobs=[(a+'_'+str(s),a,s) for a in plan['arms'] for s in plan['seeds']]
    state_path=OUT/(P+'execution.json')
    state=read(state_path.name) if state_path.exists() else {'started_utc':now(),'cpu_budget':16,'mode_changes':[],
           'resumed_seeds':[],'attempts':{},'maximum_active_workers':0,'identity':identity(),'active_jobs':[]}
    if state['identity']!=identity():raise RuntimeError('Batch code identity differs on resume')
    done={};pending=[]
    for job,arm,seed in jobs:
        r=completed(job,arm,seed)
        if r is not None:done[job]=r
        else:pending.append((job,arm,seed))
    for job,arm,seed in pending:
        if job in state['attempts']:
            state['resumed_seeds'].append({'job':job,'arm':arm,'seed':seed,'reason':'In-flight job interrupted without a completion record','utc':now()})
    active={};last_mode=None;last_report=0
    try:
        while pending or active:
            check_stop();control=read(P+'control.json');mode=control['mode']
            if mode!=last_mode:
                state['mode_changes'].append({'mode':mode,'utc':now(),'active_workers':len(active),'limit':plan['worker_limits'][mode]});last_mode=mode
            for job,(p,arm,seed) in list(active.items()):
                code=p.poll()
                if code is not None:
                    del active[job]
                    if code:raise RuntimeError('Run worker failed: '+job+' exit '+str(code))
                    r=completed(job,arm,seed)
                    if r is None:raise RuntimeError('Run exited without a completion record: '+job)
                    done[job]=r
            if control.get('interrupt',False):
                interrupted=[]
                for job,(p,arm,seed) in active.items():
                    p.terminate();p.wait();interrupted.append({'job':job,'arm':arm,'seed':seed})
                state.update(status='INTERRUPTED',interrupted_jobs=interrupted,active_jobs=[],completed=len(done),pending=len(pending)+len(interrupted),utc=now())
                write(P+'execution.json',state);print(json.dumps(state),flush=True);return
            for unused in range(dispatch_slots(mode,len(active),len(pending))):
                job,arm,seed=pending.pop(0)
                prior_attempt=state['attempts'].get(job,0)
                if prior_attempt:
                    for suffix in ('.csv.partial','.csv'):
                        partial=OUT/(P+job+'_steps_attempt'+str(prior_attempt)+suffix)
                        if partial.exists():
                            retained=OUT/(P+job+'_steps_attempt'+str(prior_attempt)+'_interrupted.csv.partial')
                            if retained.exists():raise RuntimeError('Retained partial path already exists')
                            replace_with_retry(partial,retained)
                            state.setdefault('retained_partial_logs',[]).append({'job':job,'path':retained.name})
                            break
                attempt=prior_attempt+1;state['attempts'][job]=attempt
                state['active_jobs']=list(active)+[job];write(P+'execution.json',state)
                active[job]=(spawn(job,arm,seed,attempt),arm,seed)
            state['maximum_active_workers']=max(state['maximum_active_workers'],len(active))
            state.update(status='RUNNING',mode=mode,worker_limit=plan['worker_limits'][mode],
                         mode_effective=len(active)<=plan['worker_limits'][mode],active_jobs=list(active),
                         completed=len(done),running=len(active),pending=len(pending),utc=now())
            write(P+'execution.json',state)
            if time.monotonic()-last_report>=10:
                print(json.dumps({k:state[k] for k in ['status','mode','worker_limit','completed','running','pending','utc']}),flush=True);last_report=time.monotonic()
            if active:time.sleep(2)
        end_pins=pins()
        state.update(status='COMPLETE',completed=len(done),running=0,pending=0,active_jobs=[],completed_utc=now(),source_pins_end=end_pins)
        write(P+'execution.json',state)
        write(P+'completions.json',{'identity':identity(),'runs':[done[j] for j,a,s in jobs]})
        print(json.dumps({'status':'COMPLETE','completed':len(done),'maximum_active_workers':state['maximum_active_workers']}),flush=True)
    except BaseException as e:
        mark_halt('batch',e)
        for p,arm,seed in active.values():p.wait()
        state.update(status='HALTED',reason=str(e),utc=now())
        write(P+'execution.json',state);raise SystemExit(2)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['gates','batch','worker','control'])
    parser.add_argument('--job');parser.add_argument('--arm');parser.add_argument('--seed',type=int)
    parser.add_argument('--attempt',type=int,default=1);parser.add_argument('--mode',choices=['normal','work'])
    parser.add_argument('--interrupt',action='store_true');args=parser.parse_args()
    if args.command=='worker':worker(args)
    elif args.command=='gates':gates()
    elif args.command=='batch':batch()
    else:
        c=read(P+'control.json')
        if args.mode:c['mode']=args.mode
        c['interrupt']=args.interrupt;c['updated_utc']=now();write(P+'control.json',c);print(json.dumps(c))





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




def recorder_conformance():
    result=read(P+'gate_recorder_result.json')
    rows=log_rows(result['raw_log'])
    path='simulation/diagnostics/detector_run_cal_H_1835086300_steps_attempt1.csv'
    raw=git('cat-file','blob','HEAD:'+path)
    reference=[{k:parsed(v) for k,v in row.items()} for row in csv.DictReader(io.StringIO(raw.decode('utf-8')))]
    first=None;compared=0
    if len(rows)!=25 or len(reference)<25:first={'field':'row_count','step':None,'actual':len(rows),'expected':25}
    for step,(actual,expected) in enumerate(zip(rows,reference)):
        if first is not None:break
        if list(actual)!=list(expected):first={'field':'column_names','step':step,'actual':list(actual),'expected':list(expected)};break
        for key in actual:
            compared+=1
            if actual[key]!=expected[key] or type(actual[key]) is not type(expected[key]):
                first={'field':key,'step':step,'actual':actual[key],'expected':expected[key]};break
    evidence={'passed':first is None,'seed':1835086300,'steps_compared':len(rows),'columns':list(rows[0]),
              'field_comparisons':compared,'first_difference':first,'reference_path':path,
              'reference_blob_sha1':git('rev-parse','HEAD:'+path).decode().strip(),'reference_sha256_lf':sha(lf(raw)),
              'nulls_compared_exactly':True,'identity':identity()}
    write(P+'recorder_conformance.json',evidence)
    if first is not None:raise RuntimeError('Recorder conformance failed: '+json.dumps(first))
    return evidence






CAVEAT=('At a reference successor capability of 2.5, g_star lies below the honest median of g, '
        'every honest calibration run spends long spans above it, and k is accordingly large. '
        'A hazard there measures persistence far beyond honest behavior rather than the approach to a defection boundary.')

def pinned_blob(path):
    plan=read(P+'plan.json')
    wanted=next(p['expected_sha256_lf'] for p in plan['pins'] if p['path']==path)
    raw=git('cat-file','blob',plan['head']+':'+path)
    if sha(lf(raw))!=wanted:raise RuntimeError('Committed pin mismatch: '+path)
    return raw

def constants():
    return registered.constants(sys.modules[__name__])


def constants_gate():
    return registered.constants_gate(sys.modules[__name__])


def spans_above(rows,g_star):
    spans=[];start=None;last=None
    for row in rows:
        step=int(row['step'])
        if step<50:continue
        qualifies=float(row['g'])>=g_star
        if start is not None and (not qualifies or step!=last+1):
            spans.append({'start_step':start,'end_step':last});start=None
        if qualifies:
            if start is None:start=step
            last=step
    if start is not None:spans.append({'start_step':start,'end_step':last})
    return spans

def hazard_records(rows,hazards):
    result={}
    for label,values in hazards.items():
        spans=spans_above(rows,values['g_star'])
        confirmation=next((s['start_step']+values['k']-1 for s in spans if s['end_step']-s['start_step']+1>=values['k']),None)
        result[label]={**values,'spans':spans,'confirmation_step':confirmation}
    return result



def evaluate_records(rows,allocation_rows):
    return registered.evaluate_records(sys.modules[__name__],rows,allocation_rows)

def allocation_definition_gate():
    return registered.allocation_gate(sys.modules[__name__])



import detector_run_r3_eval_a2_channels as registered

if __name__=='__main__':
    try:main()
    except Exception as error:
        mark_halt('executor',error)
        raise

