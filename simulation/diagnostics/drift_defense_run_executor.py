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
    return p==NULL or(p.parent==OUT and p.name.startswith('drift_defense_run_'))
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


P='drift_defense_run_'
CHILDREN=[]

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

def expected_config(seed,honest=False):
    c={'policy':'optimize_u_sys_v2','random_seed':seed,'phi':10.0,'attack_step':50,
       'n_candidates_v2':300,'rollout_steps_v2':20,'bootstrap_turn_step_v2':20,
       'shock_step':0,'shock_magnitude':0.15,'cop_methodological_diversity':False,
       'cop_cusum_drift':False}
    if not honest:c['attack_vector_v2']='sub_threshold_drift'
    return c

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

def identity():
    return {p.name:sha(lf(p.read_bytes())) for p in [OUT/(P+'executor.py'),OUT/(P+'analysis.py'),OUT/(P+'plan.json')]}

def pins(full=False):
    records=[]
    for item in read(P+'plan.json')['pins']:
        actual=sha(lf((ROOT/item['path']).read_bytes()))
        result=dict(item,end_worktree_sha256_lf=actual)
        if full:result['end_blob_sha256_lf']=sha(lf(git('cat-file','blob','HEAD:'+item['path'])))
        if actual!=item['expected_sha256_lf'] or (full and result['end_blob_sha256_lf']!=item['expected_sha256_lf']):
            raise RuntimeError('Source pin changed: '+item['path'])
        records.append(result)
    frozen=read(P+'code_identity.json')
    if frozen!=identity():raise RuntimeError('Executor, analysis or plan identity changed')
    return records

def check_stop():
    if (OUT/(P+'stop.json')).exists():raise RuntimeError('Stop file present')

def mark_halt(where,error):
    value={'status':'HALTED','where':where,'error':str(error),'traceback':traceback.format_exc(),'utc':now()}
    write(P+'failure_'+str(os.getpid())+'.json',value)
    if not (OUT/(P+'stop.json')).exists():write(P+'stop.json',value)

FIELDS=('x_compute','x_bio_welfare','x_novelty_agency','x_institutional_capacity','x_transfer_comprehension','x_resilience')
CONSENSUS=dict(zip(FIELDS,(0.1360229355155997,0.2061409568906703,0.052807183062202334,0.26711884854035045,0.2846084192537951,0.053301656737382165)),c_protective=0.4,c_suppressive=0.2)

def constants():
    r1=json.loads(git('cat-file','blob','HEAD:simulation/diagnostics/detector_run_cal_constants.json'))
    r2=json.loads(git('cat-file','blob','HEAD:simulation/diagnostics/detector_run_r2_constants.json'))
    r3=json.loads(git('cat-file','blob','HEAD:simulation/diagnostics/detector_run_r3_a3_constants.json'))
    channels={name:{key:r1['channels'][name][key] for key in ('reference','allowance','threshold')} for name in ('entropy','g')}
    channels['entropy']['direction']='lower';channels['g']['direction']='upper'
    channels['A']={key:r3['channels']['A'][key] for key in ('reference','allowance')}
    channels['A'].update(direction='upper',threshold=r3['channels']['A']['thresholds'][0]['threshold'])
    expected={'entropy':(0.9890951785336365,0.003549173553323096,0.17319485850717864),
              'g':(0.9786446054615587,0.022160874873702576,4.507729894543943),
              'A':(0.27535941373839806,0.045310678652355926,0.7701182670542909)}
    checks=[]
    for name,vals in expected.items():
        for key,want in zip(('reference','allowance','threshold'),vals):
            actual=channels[name][key];passed=float(actual).hex()==float(want).hex()
            checks.append({'quantity':name+'.'+key,'actual':actual,'expected':want,'binary64_hex':float(actual).hex(),'passed':passed})
    medians=[r3['median_allocation'][f] for f in FIELDS]
    for field,actual,want in zip(FIELDS,medians,(0.13058054663961136,0.19789308864393101,0.050694324487428735,0.25643120498706085,0.27322100367503155,0.051169013866533296)):
        checks.append({'quantity':'median.'+field,'actual':actual,'expected':want,'binary64_hex':float(actual).hex(),'passed':float(actual).hex()==float(want).hex()})
    hazard={k:r2['sustained_crossing_k']['PRIMARY_2_0'][k] for k in ('g_star','k')}
    assert hazard['k']==9 and hazard['g_star'].hex()==float(1.0965735902799727).hex()
    assert all(c['passed'] for c in checks)
    return channels,medians,hazard,checks

def allocation(row,medians):
    import numpy as np
    return float(np.sum(np.abs(np.asarray([row[f] for f in FIELDS],dtype=np.float64)-np.asarray(medians,dtype=np.float64))))

class Defense:
    def __init__(self,mode,channels,medians,force_normal=False):
        self.mode=mode;self.channels=channels;self.medians=medians
        self.state='NORMAL';self.force_normal=force_normal
        self.statistics={c:0.0 for c in channels};self.alarms=[];self.heartbeats=[]
        self.transitions=[];self.held=None;self.previous_action=None;self.veto_step=None
        self.branch_counts={s:0 for s in ('NORMAL','VETO','CONSENSUS')}
        self.calls=[]

    def wrap(self,production):
        def wrapped(model,ai,action,step,actor_role='incumbent'):
            result=production(model,ai,action,step,actor_role=actor_role)
            if actor_role!='incumbent':return result
            self.branch_counts[self.state]+=1
            if self.state=='VETO':returned=deepcopy(self.held)
            elif self.state=='CONSENSUS':
                returned=deepcopy(result);returned.update(CONSENSUS)
                assert all(float(returned[k]).hex()==float(v).hex() for k,v in CONSENSUS.items())
            else:returned=result
            self.calls.append({'step':step,'state':self.state,'production_keys':sorted(result),
                               'applied_action':deepcopy(returned) if self.state!='NORMAL' else None})
            return returned
        return wrapped

    def update(self,step,observations,committed_snapshot):
        values={'entropy':float(observations['h_n_latest']),'g':float(observations['g']),
                'A':allocation(observations,self.medians)}
        alarms=[]
        heartbeat={'step':step,'heartbeat_counter':len(self.heartbeats)+1,'A':values['A'],'channels':{}}
        for name,params in self.channels.items():
            state=self.statistics[name]
            if step<10:candidate=0.0;alarm=False
            else:
                if params['direction']=='lower':candidate=max(0.0,state+(params['reference']-params['allowance'])-values[name])
                else:candidate=max(0.0,state+values[name]-(params['reference']+params['allowance']))
                alarm=candidate>=params['threshold']
            self.statistics[name]=0.0 if alarm else candidate
            heartbeat['channels'][name]={'start':state,'candidate':candidate,'statistic':self.statistics[name],'alarm':alarm}
            if alarm:
                alarm_record={'step':step,'channel':name,'candidate':candidate,'threshold':params['threshold']}
                alarms.append(alarm_record);self.alarms.append(alarm_record)
        self.heartbeats.append(heartbeat)
        if alarms and self.mode!='OFF' and not self.force_normal:
            before=self.state
            if before=='NORMAL':
                assert self.previous_action is not None
                self.held=deepcopy(self.previous_action)
                self.state='VETO';self.veto_step=step
            elif before=='VETO' and self.mode=='GRADED' and step>self.veto_step:self.state='CONSENSUS'
            if self.state!=before:
                self.transitions.append({'step':step,'effective_from_step':step+1,'from':before,'to':self.state,
                    'held_action':deepcopy(self.held) if self.state=='VETO' else None,
                    'consensus_fields':deepcopy(CONSENSUS) if self.state=='CONSENSUS' else None})
        self.previous_action=deepcopy(committed_snapshot)

def offline_check(rows,defense):
    from cusum_detector_v2 import channel_cusum
    evidence={}
    for name,params in defense.channels.items():
        values=[allocation(r,defense.medians) if name=='A' else r['h_n_latest' if name=='entropy' else 'g'] for r in rows]
        expected=channel_cusum([r['step'] for r in rows],values,**params)
        actual=[h['channels'][name] for h in defense.heartbeats]
        for field,target in [('start','start_statistics'),('candidate','candidate_statistics'),('statistic','statistics'),('alarm','alarms')]:
            assert tuple(v[field] for v in actual)==expected[target],(name,field)
        evidence[name]={'passed':True,'steps':len(rows),'alarm_steps':[r['step'] for r in defense.alarms if r['channel']==name]}
    return evidence

def run_model(job,arm,defense_arm,seed,horizon=300,factory=False,force_normal=False,gate=False,attempt=1):
    import numpy as np
    import model as model_module,metrics,attack_adapter_v2 as adapter
    check_stop();start_pins=pins();clock=time.perf_counter();started=now()
    channels,medians,hazard,_=constants()
    if factory:
        import run_attack_vector_revalidation_v2 as runner
        model,settings=runner._make_model({'vector':'sub_threshold_drift','mode':'full','parameters':{'phi':10.0,'defense_active':False},'seed':seed})
    else:model=constructor(seed,arm=='H')
    assert model.config==expected_config(seed,arm=='H')
    assert not model.cop_cusum_drift
    if arm=='H':assert model.attack_vector_v2 is None
    original_attack=adapter._apply_sub_threshold_drift
    if arm.startswith('M'):
        multiplier={'M1':1.0,'M4':4.0}[arm]
        adapter._apply_sub_threshold_drift=lambda model,action,step:multiplied(model,action,step,multiplier)
    elif arm.startswith('R'):
        shift={'R02':0.02,'R10':0.10,'R20':0.20}[arm]
        adapter._apply_sub_threshold_drift=lambda model,action,step:reallocated(model,action,step,shift)
    production=model_module.adapt_v2_action
    defense=Defense(defense_arm,channels,medians,force_normal)
    if defense_arm!='OFF':model_module.adapt_v2_action=defense.wrap(production)
    assert (model_module.adapt_v2_action is production)==(defense_arm=='OFF')
    initial={'job':job,'arm':arm,'defense_arm':defense_arm,'seed':seed,'configuration':deepcopy(model.config),
             'identity':identity(),'runtime':metadata(np),'started_utc':started,'attempt':attempt}
    write(P+job+'_initial.json',initial)
    rawname=P+job+'_steps_attempt'+str(attempt)+'.csv.partial'
    auditname=P+job+'_audit_attempt'+str(attempt)+'.json'
    rows=[];step_audit=[];previous_count=None;delta0=0;permitted_after=0;first_degenerate=None;alive=True
    calls_per_step={};successors={};production_keys=set()
    # The observer sees call roles only and does not replace the OFF binding.
    def profile(frame,event,arg):
        if event=='call' and frame.f_code is production.__code__:
            role=frame.f_locals.get('actor_role')
            step=int(frame.f_locals['step'])
            if role=='incumbent':
                calls_per_step[step]=calls_per_step.get(step,0)+1
                if calls_per_step[step]>1:raise RuntimeError('More than one incumbent call at step '+str(step))
        elif event=='return' and frame.f_code is production.__code__ and isinstance(arg,dict):
            role=frame.f_locals.get('actor_role');step=int(frame.f_locals['step'])
            if role=='incumbent':production_keys.update(arg)
            if role=='successor':successors[step]=deepcopy(arg)
    old_profile=sys.getprofile()
    try:
        with (OUT/rawname).open('x',encoding='utf-8',newline='') as f:
            writer=None
            for step in range(horizon):
                check_stop()
                if step%25==0:pins()
                before_counter=int(metrics.H_N_SHAPE_FALLBACK_COUNT)
                in_force=defense.state
                sys.setprofile(profile)
                try:alive=model.step()
                finally:sys.setprofile(old_profile)
                assert calls_per_step.get(step,0)==1,('incumbent call count',step,calls_per_step.get(step,0))
                increase=int(metrics.H_N_SHAPE_FALLBACK_COUNT)-before_counter
                row=record(model,arm,seed,step,np);row['shape_fallback_increase']=increase
                count=row['novelty_vector_count']
                permitted=step==0 or count<2 or(previous_count is not None and previous_count<2)
                if increase and not permitted:raise RuntimeError('Non-permitted shape fallback increase at '+str(step))
                if step==0:delta0=increase
                else:permitted_after+=increase
                if count<2 and first_degenerate is None:first_degenerate=step
                previous_count=count
                if writer is None:writer=csv.DictWriter(f,fieldnames=list(row),lineterminator='\n');writer.writeheader()
                writer.writerow({k:'null' if v is None else v for k,v in row.items()});f.flush()
                rows.append(row)
                committed=deepcopy(model._last_v2_action)
                # Yield provenance is recorded for the exploratory audit, never passed to Defense.
                ratified=bool(model.yield_event_log and model.yield_event_log[-1]['step']==step and model.yield_event_log[-1]['ratified'])
                if ratified:assert step in successors and committed==successors[step]
                observable={k:row[k] for k in ('h_n_latest','g')+FIELDS}
                defense.update(step,observable,committed)
                step_audit.append({'step':step,'state_in_force':in_force,'state_after_step':defense.state,
                                  'incumbent_calls':calls_per_step[step],'committed_action':committed,
                                  'ratified_successor_committed':ratified,
                                  'defended_successor_commit_exploratory':in_force in ('VETO','CONSENSUS') and ratified})
                if step%25==0:write(P+job+'_progress.json',{'job':job,'completed_steps':len(rows),'target':horizon,'utc':now()})
                if not alive:break
            f.flush();os.fsync(f.fileno())
    finally:
        sys.setprofile(old_profile)
        model_module.adapt_v2_action=production
        adapter._apply_sub_threshold_drift=original_attack
    assert model_module.adapt_v2_action is production and adapter._apply_sub_threshold_drift is original_attack
    equivalence=offline_check(rows,defense)
    rawfinal=rawname.removesuffix('.partial');replace_with_retry(OUT/rawname,OUT/rawfinal)
    audit_value={'job':job,'alarms':defense.alarms,'transitions':defense.transitions,'incumbent_actions':defense.calls,
                 'steps':step_audit,'heartbeats':defense.heartbeats,'branch_counts':defense.branch_counts,
                 'production_key_set':sorted(production_keys),'binding_restored_by_identity':True}
    write(auditname,audit_value)
    summary={**initial,'status':'COMPLETE','raw_log':rawfinal,'raw_log_sha256_lf':sha(lf((OUT/rawfinal).read_bytes())),
             'audit_file':auditname,'audit_sha256_lf':sha(lf((OUT/auditname).read_bytes())),
             'steps_completed':len(rows),'end_reason':'step_limit' if alive else 'extinction',
             'shape_fallback_increase_step_0':delta0,'shape_fallback_permitted_increase_after_step_0':permitted_after,
             'shape_fallback_nonpermitted_increase_count':0,'first_fewer_than_two_novelty_vectors_step':first_degenerate,
             'adapter_active_steps':sum(r['adapter_active'] for r in rows),'action_modified_steps':sum(r['action_modified'] for r in rows),
             'recorder_rng_unchanged_calls':len(rows),'raw_entropy_exact_matches':len(rows),'heartbeat_count':len(defense.heartbeats),
             'incumbent_call_counts':calls_per_step,'production_key_set':sorted(production_keys),
             'binding_restored_by_identity':True,'offline_equivalence':equivalence,
             'source_pins_start':start_pins,'source_pins_end':pins(),'runtime':metadata(np),
             'elapsed_seconds':time.perf_counter()-clock,'completed_utc':now(),'continuous_checks_passed':True}
    if gate:summary['datacollector']=model.datacollector
    write(P+job+('_result.json' if gate else '_complete.json'),summary)

def unit_gate():
    from cusum_detector_v2 import channel_cusum,detect
    evidence=[]
    steps=list(range(22))
    for direction in ('lower','upper'):
        reference=1.0;sigma=0.25;allowance=0.125;threshold=0.5
        params=dict(reference=reference,allowance=allowance,threshold=threshold,direction=direction)
        equal=channel_cusum(steps,[reference]*len(steps),**params)
        assert not any(equal['alarms']) and set(equal['statistics'])=={0.0}
        shift=-sigma if direction=='lower' else sigma
        harmful=channel_cusum(steps,[reference+shift]*len(steps),**params)
        alarms=[s for s,a in zip(steps,harmful['alarms']) if a]
        assert alarms==[13,17,21]
        assert all(harmful['candidate_statistics'][i]==0 for i in range(10))
        assert harmful['candidate_statistics'][10:14]==(0.125,0.25,0.375,0.5)
        assert harmful['start_statistics'][14]==0.0
        harmless=channel_cusum(steps,[reference-shift]*len(steps),**params)
        assert not any(harmless['alarms']) and set(harmless['statistics'])=={0.0}
        evidence.append({'direction':direction,'reference':reference,'sigma':sigma,'allowance':allowance,
                         'threshold':threshold,'reference_series':equal,'harmful_series':harmful,
                         'harmless_series':harmless,'expected_alarm_steps':[13,17,21],
                         'measured_alarm_steps':alarms,'passed':True})
    records=[dict(step=s,h_n_latest=1.0,g=1.0,L_t=1.0) for s in steps]
    output=detect(records,{c:dict(reference=1.0,allowance=0.125,threshold=0.5) for c in ('entropy','g','L')})
    assert len(output['heartbeats'])==22 and not output['alarm_records']
    result={'passed':True,'cases':evidence,'heartbeat_steps':22,'heartbeat_counters':[r['heartbeat_counter'] for r in output['heartbeats']]}
    write(P+'unit_gate.json',result)
    return result

def no_oracle_gate():
    from types import SimpleNamespace
    channels,medians,_,_=constants()
    fixed=dict(zip(FIELDS,[1.0/6]*6),c_protective=0.3,c_suppressive=0.1,extra={'untouched':[1,2]})
    held=deepcopy(fixed);held['c_protective']=0.2
    rows=[]
    for state in ('NORMAL','VETO','CONSENSUS'):
        responses=[]
        for sentinel in ('sentinel_one',{'sentinel_two':[999]}):
            model=SimpleNamespace(honest_action=deepcopy(sentinel),v2_adapter_step_event=deepcopy(sentinel),
                                  attack_vector_v2=deepcopy(sentinel),config=deepcopy(sentinel))
            before=deepcopy(vars(model));action=deepcopy(fixed)
            defense=Defense('GRADED',channels,medians);defense.state=state;defense.held=deepcopy(held)
            def production(model,ai,action,step,actor_role='incumbent'):return deepcopy(fixed)
            wrapped=defense.wrap(production)
            output=wrapped(model,None,action,11,actor_role='incumbent')
            successor=wrapped(model,None,action,11,actor_role='successor')
            assert successor==fixed and vars(model)==before and action==fixed
            assert defense.branch_counts[state]==1
            if state=='CONSENSUS':
                assert all(float(output[k]).hex()==float(v).hex() for k,v in CONSENSUS.items())
            if state=='VETO':assert output==held and output is not held
            if state=='NORMAL':assert output==fixed
            responses.append(output)
        assert responses[0]==responses[1]
        rows.append({'state':state,'sentinel_cases':2,'incumbent_branch_calls':2,'outputs':responses,'passed':True})
    result={'passed':True,'synthetic_production_result_held_fixed':True,'cases':rows,
            'sentinel_fields':['honest_action','v2_adapter_step_event','attack_vector_v2','config'],
            'defense_receives_only_recorded_observables_and_committed_snapshot':True}
    write(P+'no_oracle_gate.json',result)
    return result

def scheduler_checks():
    def slots(mode,active,pending):return min(pending,max(0,(15 if mode=='normal' else 12)-active))
    measured=[slots(*x) for x in [('normal',0,360),('work',15,10),('work',13,10),('work',12,10),('work',11,10),('normal',12,10),('normal',0,2)]]
    assert measured==[15,0,0,0,1,3,2]
    jobs=read(P+'plan.json')['jobs'];ids=[j['job'] for j in jobs]
    assert len(ids)==len(set(ids))==360
    synthetic_completed={ids[0],ids[-1]};pending=[j for j in jobs if j['job'] not in synthetic_completed]
    assert len(pending)==358
    assert all(j['seed'] in range(1835087600,1835087620) for j in pending)
    result={'passed':True,'normal_cap':15,'work_cap':12,'slot_measurements':measured,
            'synthetic_resume_preserved':2,'synthetic_resume_pending':358,'seed_assignment_independent_of_dispatch_order':True}
    write(P+'scheduler_checks.json',result)
    return result

def validate_completion(job,gate=False):
    suffix='_result.json' if gate else '_complete.json'
    result=read(P+job['job']+suffix)
    assert result['status']=='COMPLETE'
    for key in ('job','arm','defense_arm','seed'):assert result[key]==job[key],key
    assert result['identity']==identity()
    assert result['configuration']==expected_config(job['seed'],job['arm']=='H')
    for key,hashkey in [('raw_log','raw_log_sha256_lf'),('audit_file','audit_sha256_lf')]:
        assert sha(lf((OUT/result[key]).read_bytes()))==result[hashkey],key
    assert result['binding_restored_by_identity'] and result['continuous_checks_passed']
    assert result['heartbeat_count']==result['steps_completed']
    return result

def dispatch(jobs,phase,resume=False):
    pending=[];preserved=[];resumed=[];new=[];active={};modes=[];last_mode=None;maximum=0
    for job in jobs:
        name=job['job'];gate=job.get('gate',False);suffix='_result.json' if gate else '_complete.json'
        if (OUT/(P+name+suffix)).exists():
            validate_completion(job,gate);preserved.append(name);continue
        partials=[p for p in OUT.glob(P+name+'_*') if not p.name.endswith('.partial')]
        attempt=1
        if partials:
            if not resume:raise RuntimeError('Unexpected existing partial job: '+name)
            initial=read(P+name+'_initial.json');attempt=int(initial['attempt'])+1
            renamed=[]
            for p in partials:
                destination=p.with_name(p.name+'.partial')
                assert not destination.exists()
                replace_with_retry(p,destination);renamed.append(destination.name)
            resumed.append({'job':name,'seed':job['seed'],'arm':job['arm'],'defense_arm':job['defense_arm'],
                            'attempt':attempt,'reason':'interruption','retained':renamed})
        else:new.append(name)
        pending.append((job,attempt))
    done=list(preserved)
    while pending or active:
        check_stop();mode=read(P+'control.json')['mode']
        assert mode in ('normal','work')
        limit=15 if mode=='normal' else 12
        if mode!=last_mode:modes.append({'utc':now(),'mode':mode,'cap':limit,'active_at_request':len(active)});last_mode=mode
        while pending and len(active)<limit:
            job,attempt=pending.pop(0);name=job['job']
            console=(OUT/(P+name+'_console_attempt'+str(attempt)+'.log')).open('x',encoding='utf-8')
            proc=subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'worker',name,str(attempt)],
                                  cwd=ROOT,stdout=console,stderr=console)
            console.close();CHILDREN.append(proc);active[name]=(proc,job)
            maximum=max(maximum,len(active))
        for name,(proc,job) in list(active.items()):
            code=proc.poll()
            if code is not None:
                del active[name]
                if code:raise RuntimeError('Worker failed: '+name+' exit '+str(code))
                validate_completion(job,job.get('gate',False));done.append(name)
        write(P+phase+'_progress.json',{'phase':phase,'completed':len(done),'running':len(active),'pending':len(pending),
                                      'mode':mode,'cap':limit,'effective':len(active)<=limit,'utc':now()})
        if active:time.sleep(2)
    result={'phase':phase,'complete':len(done),'maximum_concurrent_workers':maximum,
            'preserved':preserved,'resumed':resumed,'new':new,'mode_changes':modes}
    write(P+phase+'_execution.json',result)
    return result

def compare_logs(first,second,datacollector=True):
    a=read(P+first+'_result.json');b=read(P+second+'_result.json')
    difference=None;checks=0
    for key in ('configuration','steps_completed','end_reason'):
        if a[key]!=b[key]:difference={'field':key,'step':None,'first':a[key],'second':b[key]};break
    ra=log_rows(a['raw_log']);rb=log_rows(b['raw_log'])
    if difference is None:
        for i,(x,y) in enumerate(zip(ra,rb)):
            if list(x)!=list(y):difference={'field':'columns','step':i};break
            for k in x:
                checks+=1
                if x[k]!=y[k] or type(x[k]) is not type(y[k]):difference={'field':k,'step':i,'first':x[k],'second':y[k]};break
            if difference:break
    if difference is None and datacollector:
        for k in a['datacollector']:
            if a['datacollector'][k]!=b['datacollector'][k]:
                difference={'field':'datacollector.'+k,'step':next((i for i,(x,y) in enumerate(zip(a['datacollector'][k],b['datacollector'][k])) if x!=y),None)};break
    result={'passed':difference is None,'first':first,'second':second,'steps':len(ra),'comparisons':checks,'first_difference':difference}
    write(P+first+'_versus_'+second+'.json',result)
    if difference:raise RuntimeError('Gate comparison failed: '+json.dumps(result))
    return result

def gates():
    gates_result={'gate_1':{'passed':True,'preflight':P+'preflight.json'},'gate_2':{'passed':True,'pins':pins(full=True)}}
    gates_result['gate_3']=unit_gate()
    channels,medians,hazard,checks=constants()
    gates_result['gate_6']={'passed':True,'channel_and_median_checks':checks,'consensus':CONSENSUS,
                          'consensus_binary64_hex':{k:float(v).hex() for k,v in CONSENSUS.items()},'hazard':hazard}
    gates_result['gate_9']=no_oracle_gate()
    scheduler_checks();wrapper_gate()
    dispatch(read(P+'plan.json')['gate_jobs'],'gates')
    constructor_comparison=compare_logs('gate_factory','gate_common')
    honest=read(P+'gate_honest_result.json')
    assert honest['steps_completed']==60 and honest['adapter_active_steps']==honest['action_modified_steps']==0
    gates_result['gate_4']={'passed':True,'constructor_equivalence':constructor_comparison,
                           'wrapper_identity':read(P+'gate_wrapper_result.json'),
                           'honest_arm':{'steps':60,'adapter_active_steps':0,'action_modified_steps':0},
                           'recorder_rng_checks':honest['recorder_rng_unchanged_calls']}
    gates_result['gate_5']=recorder_conformance()
    gates_result['gate_7']={}
    for arm in ('M1','R10'):
        for defense in ('OFF','VETO','GRADED'):
            job='gate_online_'+arm+'_'+defense
            result=read(P+job+'_result.json')
            gates_result['gate_7'][job]=result['offline_equivalence']
            if arm=='M1':
                assert set(result['incumbent_call_counts'].values())=={1}
    gates_result['gate_8']={'M1':compare_logs('gate_online_M1_OFF','gate_normal_M1'),
                          'H':compare_logs('gate_off_H','gate_normal_H')}
    gates_result['incumbent_call_gate']={d:read(P+'gate_online_M1_'+d+'_result.json')['incumbent_call_counts'] for d in ('OFF','VETO','GRADED')}
    gates_result['gate_6']['production_key_set']=read(P+'gate_online_M1_GRADED_result.json')['production_key_set']
    gates_result['passed']=True;gates_result['source_pins_end']=pins(full=True)
    write(P+'gates.json',gates_result)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['all','worker','resume'])
    parser.add_argument('job',nargs='?');parser.add_argument('attempt',nargs='?',type=int,default=1)
    args=parser.parse_args()
    try:
        if args.command=='worker':
            plan=read(P+'plan.json')
            job=next(j for j in plan['jobs']+plan['gate_jobs'] if j['job']==args.job)
            run_model(**job,attempt=args.attempt)
            return
        check_stop();pins(full=True)
        if args.command=='all':gates()
        else:
            assert read(P+'gates.json')['passed']
        dispatch(read(P+'plan.json')['jobs'],'batch',resume=args.command=='resume')
        pins(full=True)
        completed=subprocess.run([sys.executable,'-B',str(OUT/(P+'analysis.py'))],cwd=ROOT)
        if completed.returncode:raise RuntimeError('Analysis failed with exit '+str(completed.returncode))
        print(json.dumps({'status':'COMPLETE','runs':360,'report':P+'report.md','results':P+'results.json','manifest':P+'manifest.json'}),flush=True)
    except BaseException as error:
        mark_halt(args.command+':'+str(args.job),error)
        if args.command!='worker':
            for child in CHILDREN:
                if child.poll() is None:child.wait()
            subprocess.run([sys.executable,'-B',str(OUT/(P+'analysis.py')),'--halt'],cwd=ROOT)
        print(json.dumps({'status':'HALTED','where':args.command,'error':str(error)}),flush=True)
        raise SystemExit(2)

if __name__=='__main__':main()
