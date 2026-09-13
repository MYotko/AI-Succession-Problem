"""Execute only the committed drift-mapping plan under a prefix write guard."""
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
    return p==NULL or(p.parent==OUT and p.name.startswith('drift_map_run_'))
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
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def encode(obj):
    if hasattr(obj,'tolist'):return obj.tolist()
    if hasattr(obj,'item'):return obj.item()
    raise TypeError(type(obj).__name__)
def write(name,obj):
    text=json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=True,allow_nan=False,default=encode)+'\n'
    with(OUT/name).open('w',encoding='utf-8',newline='\n')as f:f.write(text);f.flush();os.fsync(f.fileno())
def git(*args):
    p=subprocess.run(['git',*args],cwd=ROOT,capture_output=True)
    if p.returncode:raise RuntimeError('Read-only Git failed: '+repr(args)+' '+p.stderr.decode('utf-8',errors='replace'))
    return p.stdout

def pins():
    plan=read('drift_map_run_plan.json');records=[]
    for item in plan['pins']:
        actual=sha(lf((ROOT/item['path']).read_bytes()))
        records.append(dict(item,actual_sha256_lf=actual,passed=actual==item['expected_sha256_lf']))
    if not all(r['passed']for r in records):
        write('drift_map_run_source_pin_failure_'+str(os.getpid())+'.json',{'utc':now(),'pins':records})
        raise RuntimeError('Source pin changed')
    return records

def metadata(np):
    libraries=[]
    for dll in(Path(np.__file__).resolve().parent.parent/'numpy.libs').iterdir():
        if dll.suffix.lower()=='.dll' and 'openblas'in dll.name.lower():
            lib=ctypes.CDLL(str(dll))
            for name in('scipy_openblas_get_num_threads64_','openblas_get_num_threads64_','scipy_openblas_get_num_threads','openblas_get_num_threads'):
                try:fn=getattr(lib,name)
                except AttributeError:continue
                fn.argtypes=[];fn.restype=ctypes.c_int
                libraries.append({'library':str(dll),'query':name,'effective_threads':fn()})
    if not libraries or any(r['effective_threads']!=1 for r in libraries):raise RuntimeError('Numerical thread limit not verified as one')
    modules={}
    for m in list(sys.modules.values()):
        filename=getattr(m,'__file__',None)
        if filename:
            path=Path(filename).resolve()
            if path.suffix=='.py' and path.is_relative_to(ROOT/'simulation'):
                raw=path.read_bytes();modules[path.relative_to(ROOT).as_posix()]={'sha256_raw':sha(raw),'sha256_lf':sha(lf(raw))}
    return{'machine':os.environ.get('COMPUTERNAME'),'python':sys.version,'numpy':np.__version__,'thread_environment':{k:os.environ[k]for k in THREAD_ENV},'thread_runtime':libraries,'modules':modules}

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
    components=metrics.calculate_h_n(model.novelty_log,return_components=True)
    if not isinstance(components,tuple):raise RuntimeError('Recorder cannot obtain spectral shape and V from the step novelty matrix')
    raw,shape,V=components
    if raw!=model.h_n_latest:raise RuntimeError('Continuous check: recorder raw entropy differs from cached h_n_latest at step '+str(step))
    dc=model.datacollector
    avg=float(dc['avg_well_being'][-1]);theta=float(model.theta_capability);transfer=float(model.transfer_state)
    denom=max(0.01,max(0.0,min(1.0,avg))*transfer)
    action=model._last_v2_action
    row={'arm':arm,'seed':seed,'step':step,'h_n_latest':float(model.h_n_latest),'h_n_shape_latest':model.h_n_shape_latest,'V':V,'H_N':float(dc['H_N'][-1]),'total_suppression':total_suppression(action),'avg_wb':avg,'theta_capability':theta,'transfer_state':transfer,'g':max(FRONTIER_FLOOR,theta)/denom,'population':len(model.schedule)}
    row.update({k:float(action[k])for k in('x_compute','x_bio_welfare','x_novelty_agency','x_institutional_capacity','x_transfer_comprehension','x_resilience','c_protective','c_suppressive')})
    row.update(adapter_active=bool(dc['v2_attack_active'][-1]),action_modified=bool(dc['v2_attack_action_modified'][-1]),adapter_score=float(dc['v2_adapter_cusum_score'][-1]))
    if arm=='H' and(row['adapter_active']or row['action_modified']):raise RuntimeError('Continuous check: honest adapter/action modification')
    after=np.random.get_state()
    unchanged=before[0]==after[0]and np.array_equal(before[1],after[1])and before[2:]==after[2:]
    if not unchanged:raise RuntimeError('Gate 6: recorder consumed NumPy randomness')
    return row

def worker(job):
    import numpy as np
    import metrics,attack_adapter_v2 as adapter
    start_pins=pins();runtime=metadata(np);seed=1835086199
    started=now();clock=time.perf_counter()
    if job=='wrapper':
        from agents import _x_vector_to_action,_constraint_pair_for_index
        from types import SimpleNamespace
        rng=np.random.default_rng(20260913)
        allocations=list(np.eye(6))+[np.ones(6)/6]+list(rng.dirichlet(np.ones(6),size=193))
        actions=[_x_vector_to_action(x,*_constraint_pair_for_index(i))for i,x in enumerate(allocations)]
        model=SimpleNamespace(config={'attack_step':50})
        compared=0
        for i,action in enumerate(actions):
            for step in range(300):
                expected=adapter._apply_sub_threshold_drift(model,action,step)
                actual=multiplied(model,action,step,1.0)
                if expected!=actual:
                    write('drift_map_run_gate_wrapper_result.json',{'passed':False,'action_index':i,'step':step,'expected':expected,'actual':actual,'compared_before_failure':compared})
                    raise RuntimeError('Gate 4: M1 wrapper differs from production')
                compared+=1
        result={'passed':True,'gate':4,'synthetic_action_count':len(actions),'steps_per_action':300,'action_step_comparisons':compared,'maximum_key_difference':0.0,'seed':20260913,'source_pins_start':start_pins,'source_pins_end':pins(),'runtime':metadata(np),'elapsed_seconds':time.perf_counter()-clock,'utc':now()}
        write('drift_map_run_gate_wrapper_result.json',result)
        print(json.dumps({'job':job,'passed':True,'comparisons':compared}),flush=True);return
    if job=='factory':
        import run_attack_vector_revalidation_v2 as runner
        task={'vector':'sub_threshold_drift','mode':'full','parameters':{'phi':10.0,'defense_active':False},'seed':seed}
        model,settings=runner._make_model(task)
    elif job=='common':model=constructor(seed)
    elif job=='honest':model=constructor(seed,honest=True)
    else:raise ValueError('Unknown gate job')
    honest=job=='honest';horizon=60 if honest else 300;arm='H'if honest else'GATE_ATTACK'
    initial={'job':job,'seed':seed,'configuration':model.config,'attack_vector_v2':model.attack_vector_v2,'cached_shape_initial':model.h_n_shape_latest,'shape_fallback_count_initial':metrics.H_N_SHAPE_FALLBACK_COUNT,'runtime':metadata(np),'started_utc':started}
    write('drift_map_run_gate_'+job+'_initial.json',initial)
    if honest and model.attack_vector_v2 is not None:raise RuntimeError('Gate 5: honest construction has attack vector')
    logname='drift_map_run_gate_'+job+'_steps.csv.partial'
    rows=0;active=0;modified=0;alive=True
    with(OUT/logname).open('x',encoding='utf-8',newline='')as f:
        writer=None
        for step in range(horizon):
            if(OUT/'drift_map_run_stop.json').exists():raise RuntimeError('Execution halted by another gate failure')
            alive=model.step()
            row=record(model,arm,seed,step,np)
            if writer is None:writer=csv.DictWriter(f,fieldnames=list(row),lineterminator='\n');writer.writeheader()
            writer.writerow(row);f.flush();rows+=1
            active+=int(row['adapter_active']);modified+=int(row['action_modified'])
            if step%10==0:write('drift_map_run_gate_'+job+'_progress.json',{'job':job,'completed_steps':rows,'target':horizon,'utc':now()})
            if not alive:break
        f.flush();os.fsync(f.fileno())
    fallback=metrics.H_N_SHAPE_FALLBACK_COUNT
    result={'job':job,'seed':seed,'configuration':model.config,'steps_completed':rows,'target_steps':horizon,'extinct':not alive,'adapter_active_steps':active,'action_modified_steps':modified,'recorder_rng_unchanged_calls':rows,'raw_entropy_exact_matches':rows,'shape_fallback_count':fallback,'source_pins_start':start_pins,'source_pins_end':pins(),'runtime':metadata(np),'elapsed_seconds':time.perf_counter()-clock,'ended_utc':now(),'raw_log_sha256':sha((OUT/logname).read_bytes()),'raw_log':logname,'datacollector':model.datacollector}
    result['gate_probe_passed']=rows==horizon and(not honest or(active==0 and modified==0))
    result['continuous_checks_passed']=fallback==0
    write('drift_map_run_gate_'+job+'_result.json',result)
    if not result['gate_probe_passed']:raise RuntimeError('Gate probe did not meet required steps or honest-arm checks')
    if fallback!=0:raise RuntimeError('Continuous check failed at end of '+job+' run: H_N_SHAPE_FALLBACK_COUNT='+str(fallback))
    final=logname.removesuffix('.partial')
    os.replace(OUT/logname,OUT/final)
    print(json.dumps({'job':job,'passed':True,'steps':rows,'fallback_count':fallback}),flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('job',choices=['wrapper','factory','common','honest']);args=parser.parse_args()
    try:worker(args.job)
    except BaseException as error:
        failure={'job':args.job,'utc':now(),'halt':str(error),'traceback':traceback.format_exc(),'violations':VIOLATIONS}
        write('drift_map_run_gate_'+args.job+'_failure.json',failure)
        write('drift_map_run_stop.json',failure)
        print('HALT: '+str(error),flush=True);raise SystemExit(2)
if __name__=='__main__':main()
