"""Execute the registered recovery evaluation confirmation under the registered write guard."""
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
    return p==NULL or(p.parent==OUT and p.name.startswith('defense_recovery_run_conf_'))
def audit(event,args):
    bad=None
    if event=='open':
        path,mode,flags=args
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or(isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_APPEND|os.O_TRUNC))
        if writing and not isinstance(path,int) and not allowed(path):bad='writable open: '+str(path)
    elif event=='os.rename':
        if not allowed(args[0]) or not allowed(args[1]):bad='rename outside scope'
    elif event=='os.remove':
        if not allowed(args[0]) or str(Path(args[0]).resolve()) not in DELETE_ALLOWED:bad=event
    elif event in ('os.rmdir','os.mkdir','os.link','os.symlink'):bad=event
    if bad:
        VIOLATIONS.append(bad)
        raise RuntimeError('WRITE SCOPE HALT: '+bad)
sys.addaudithook(audit)
sys.path.insert(0,str(ROOT/'simulation'))
import argparse,csv,ctypes,hashlib,io,json,math,subprocess,time,traceback
from copy import deepcopy
from datetime import datetime,timezone


P='defense_recovery_run_conf_'
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
    if git('rev-parse','HEAD').decode().strip()!=read(P+'plan.json')['head']:raise RuntimeError('HEAD changed')
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
        self.k=int(mode.split('-')[1]) if mode.startswith('RECOVER-') else None
        self.quiet_count=0;self.recovered=False

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
        self.advance_state(step,bool(alarms))
        self.previous_action=deepcopy(committed_snapshot)

    def advance_state(self,step,alarmed):
        before=self.state
        direction=None
        if alarmed:
            self.quiet_count=0
            if self.mode!='OFF' and not self.force_normal:
                if before=='NORMAL':
                    assert self.previous_action is not None
                    self.held=deepcopy(self.previous_action)
                    self.state='VETO';self.veto_step=step
                elif before=='VETO' and step>self.veto_step:
                    self.state='CONSENSUS'
                if before!=self.state:direction='escalation'
        elif self.mode!='OFF' and not self.force_normal and self.k is not None and before!='NORMAL':
            self.quiet_count+=1
            if self.quiet_count==self.k:
                if before=='CONSENSUS':
                    assert self.previous_action is not None
                    self.held=deepcopy(self.previous_action)
                    self.state='VETO';self.veto_step=step
                else:self.state='NORMAL'
                self.quiet_count=0;direction='recovery'
        if before!=self.state:
            again=direction=='escalation' and self.recovered
            self.transitions.append({'step':step,'effective_from_step':step+1,'from':before,'to':self.state,
                'direction':direction,'re_escalation_after_recovery':again,
                'held_action':deepcopy(self.held) if self.state=='VETO' else None,
                'consensus_fields':deepcopy(CONSENSUS) if self.state=='CONSENSUS' else None,
                'quiet_count_after':self.quiet_count})
            if direction=='recovery':self.recovered=True

def offline_check(rows,defense,gate=False):
    from cusum_detector_v2 import channel_cusum
    evidence={}
    for name,params in defense.channels.items():
        values=[allocation(r,defense.medians) if name=='A' else r['h_n_latest' if name=='entropy' else 'g'] for r in rows]
        expected=channel_cusum([r['step'] for r in rows],values,**params)
        actual=[h['channels'][name] for h in defense.heartbeats]
        for field,target in [('start','start_statistics'),('candidate','candidate_statistics'),('statistic','statistics'),('alarm','alarms')]:
            if gate and field!='alarm':
                assert len(actual)==len(expected[target]),(name,field,'length')
                assert all(abs(float(v[field])-float(want))<=1e-9
                           for v,want in zip(actual,expected[target])),(name,field)
            else:
                assert tuple(v[field] for v in actual)==expected[target],(name,field)
        evidence[name]={'passed':True,'computed_float_absolute_tolerance':1e-9 if gate else 0.0,'steps':len(rows),'alarm_steps':[r['step'] for r in defense.alarms if r['channel']==name]}
    return evidence

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
            defense=Defense('LATCHED',channels,medians);defense.state=state;defense.held=deepcopy(held)
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



def constructor(seed,honest=False):
    from model import GardenModel
    config={'policy':'optimize_u_sys_v2','random_seed':seed,'phi':10.0,'attack_step':50,'n_candidates_v2':300,'rollout_steps_v2':20,'bootstrap_turn_step_v2':20,'shock_step':150,'shock_magnitude':0.60}
    if not honest:config['attack_vector_v2']='sub_threshold_drift'
    return GardenModel(n_agents=200,ai_policy='sub_threshold_drift',use_cop=True,cop_attribution_check=True,cop_drift_check=True,cop_cusum_drift=False,config=config)

def expected_config(seed,honest=False):
    c={'policy':'optimize_u_sys_v2','random_seed':seed,'phi':10.0,'attack_step':50,
       'n_candidates_v2':300,'rollout_steps_v2':20,'bootstrap_turn_step_v2':20,
       'shock_step':150,'shock_magnitude':0.60,'cop_methodological_diversity':False,
       'cop_cusum_drift':False}
    if not honest:c['attack_vector_v2']='sub_threshold_drift'
    return c


ARMS=('A3','H','M1')
DEFENSE_ARMS=('LATCHED','OFF','RECOVER-20')

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


class Attack:
    def __init__(self,arm):
        assert arm in ARMS
        self.arm=arm
        self.calls=[]

    def wrap(self,production):
        if self.arm in ('H','M1'):return production
        def wrapped(model,ai,action,step,actor_role='incumbent'):
            result=production(model,ai,action,step,actor_role=actor_role)
            if actor_role!='incumbent':return result
            import attack_adapter_v2 as adapter
            returned=result;kind='inactive';moved=0.0;normalization={}
            before=None
            if step>=50:
                returned=deepcopy(result)
                moved=float(returned['x_resilience'])
                returned['x_resilience']=0.0
                returned['x_institutional_capacity']+=moved
                before=deepcopy(returned)
                returned=adapter._normalize_action(returned);kind='full_share_drain'
                normalization={k:abs(float(returned[k])-float(before[k])) for k in FIELDS}
            self.calls.append({'step':step,'kind':kind,'production_action':deepcopy(result),
                               'returned_action':deepcopy(returned),'moved':moved,
                               'before_normalization':before,
                               'normalization_absolute_changes':normalization,
                               'action_modified':returned!=result})
            return returned
        return wrapped

def run_model(job,arm,defense_arm,seed,gate=False,force_normal=False,attempt=1):
    import numpy as np
    import model as model_module,metrics,attack_adapter_v2 as adapter
    check_stop();start_pins=pins();clock=time.perf_counter();started=now()
    channels,medians,_,_=constants()
    model=constructor(seed,arm!='M1')
    assert model.config==expected_config(seed,arm!='M1')
    assert model.config['shock_step']==150
    assert float(model.config['shock_magnitude']).hex()==float(0.60).hex()
    assert model.attack_step==50 and not model.cop_cusum_drift
    assert model.attack_vector_v2==('sub_threshold_drift' if arm=='M1' else None)
    original_attack=adapter._apply_sub_threshold_drift
    if arm=='M1':adapter._apply_sub_threshold_drift=lambda model,action,step:multiplied(model,action,step,1.0)
    production=model_module.adapt_v2_action
    attack=Attack(arm);attack_binding=attack.wrap(production)
    defense=Defense(defense_arm,channels,medians,force_normal)
    binding=attack_binding if defense_arm=='OFF' else defense.wrap(attack_binding)
    initial={'job':job,'arm':arm,'defense_arm':defense_arm,'seed':seed,
             'configuration':deepcopy(model.config),'identity':identity(),'runtime':metadata(np),
             'started_utc':started,'attempt':attempt,'steps_requested':300,'force_normal':force_normal}
    write(P+job+'_initial.json',initial)
    rawname=P+job+'_steps_attempt'+str(attempt)+'.csv.partial'
    auditname=P+job+'_audit_attempt'+str(attempt)+'.json'
    rows=[];step_audit=[]
    info={'previous_count':None,'delta0':0,'permitted_after':0,'first_degenerate':None,'alive':None}
    calls_per_step={};successors={};production_keys=set()
    def profile(frame,event,arg):
        if frame.f_code is production.__code__:
            step=int(frame.f_locals['step']);role=frame.f_locals.get('actor_role')
            if event=='call' and role=='incumbent':
                calls_per_step[step]=calls_per_step.get(step,0)+1
                if calls_per_step[step]>1:raise RuntimeError('More than one incumbent call at step '+str(step))
            elif event=='return' and isinstance(arg,dict):
                if role=='incumbent':production_keys.update(arg)
                elif role=='successor':successors[step]=deepcopy(arg)
    old_profile=sys.getprofile();original_step=model.step
    with (OUT/rawname).open('x',encoding='utf-8',newline='') as handle:
        writer=None
        def observed_step():
            nonlocal writer
            check_stop();step=len(rows)
            if step%25==0:pins()
            assert model_module.adapt_v2_action is binding
            before_counter=int(metrics.H_N_SHAPE_FALLBACK_COUNT)
            in_force=defense.state
            sys.setprofile(profile)
            try:alive=original_step()
            finally:sys.setprofile(old_profile)
            assert calls_per_step.get(step,0)==1,('incumbent call count',step,calls_per_step.get(step,0))
            increase=int(metrics.H_N_SHAPE_FALLBACK_COUNT)-before_counter
            observed=record(model,'M1' if arm=='M1' else 'H',seed,step,np)
            row={'arm':arm,'defense_arm':defense_arm,'seed':seed,
                 **{k:v for k,v in observed.items() if k not in ('arm','seed')},
                 'resilience_stock':float(model.resilience_stock),'shape_fallback_increase':increase}
            assert row['resilience_stock']==float(model.datacollector['resilience_stock'][-1])
            count=row['novelty_vector_count'];previous=info['previous_count']
            permitted=step==0 or count<2 or(previous is not None and previous<2)
            if increase and not permitted:raise RuntimeError('Non-permitted shape fallback increase at '+str(step))
            if step==0:info['delta0']=increase
            else:info['permitted_after']+=increase
            if count<2 and info['first_degenerate'] is None:info['first_degenerate']=step
            info['previous_count']=count;info['alive']=bool(alive)
            if writer is None:
                writer=csv.DictWriter(handle,fieldnames=list(row),lineterminator='\n');writer.writeheader()
            writer.writerow({k:'null' if v is None else v for k,v in row.items()});handle.flush()
            committed=deepcopy(model._last_v2_action)
            ratified=bool(model.yield_event_log and model.yield_event_log[-1]['step']==step and model.yield_event_log[-1]['ratified'])
            if ratified:assert step in successors and committed==successors[step]
            call=next((c for c in reversed(attack.calls) if c['step']==step),None)
            attack_modified=bool(call and call['action_modified'] and committed==call['returned_action'] and not ratified)
            prior_transitions=len(defense.transitions)
            observable={k:row[k] for k in ('h_n_latest','g')+FIELDS}
            defense.update(step,observable,committed)
            for transition in defense.transitions[prior_transitions:]:
                if transition['to']=='VETO':
                    assert transition['held_action']==step_audit[-1]['committed_action']
                    transition['held_action_commit_step']=step-1
                    transition['held_action_attack_modified']=step_audit[-1]['committed_attack_modified']
            step_audit.append({'step':step,'state_in_force':in_force,'state_after_step':defense.state,
                               'incumbent_calls':calls_per_step[step],'committed_action':committed,
                               'quiet_count_after_step':defense.quiet_count,
                               'committed_attack_modified':attack_modified,'ratified_successor_committed':ratified})
            rows.append(row)
            if step%25==0:write(P+job+'_progress.json',{'job':job,'completed_steps':len(rows),'target':300,'utc':now()})
            return alive
        try:
            model_module.adapt_v2_action=binding;model.step=observed_step
            for _ in range(300):
                if not model.step():break
        finally:
            sys.setprofile(old_profile);model_module.adapt_v2_action=production;model.step=original_step
            adapter._apply_sub_threshold_drift=original_attack
        assert model_module.adapt_v2_action is production and model.step is original_step
        assert adapter._apply_sub_threshold_drift is original_attack
        handle.flush();os.fsync(handle.fileno())
    assert rows and (not info['alive'] or len(rows)==300)
    end_reason='step_limit' if info['alive'] else ('extinction' if rows[-1]['population']==0 else 'step_returned_false')
    equivalence=offline_check(rows,defense,gate=gate)
    rawfinal=rawname.removesuffix('.partial');replace_with_retry(OUT/rawname,OUT/rawfinal)
    audit_value={'job':job,'arm':arm,'defense_arm':defense_arm,'seed':seed,
                 'alarms':defense.alarms,'transitions':defense.transitions,'incumbent_actions':defense.calls,
                 'attack_calls':attack.calls,'steps':step_audit,'heartbeats':defense.heartbeats,
                 'branch_counts':defense.branch_counts,'production_key_set':sorted(production_keys),
                 'binding_restored_by_identity':True,'step_observer_restored_by_identity':True,'attack_binding_restored_by_identity':True}
    write(auditname,audit_value)
    summary={**initial,'status':'COMPLETE','raw_log':rawfinal,
             'raw_log_sha256_lf':sha(lf((OUT/rawfinal).read_bytes())),
             'audit_file':auditname,'audit_sha256_lf':sha(lf((OUT/auditname).read_bytes())),
             'steps_completed':len(rows),'end_reason':end_reason,
             'recorded_row':{'seed':seed,'arm':arm,'defense_arm':defense_arm,
                             'steps_completed':len(rows),'final_population':rows[-1]['population']},
             'shape_fallback_increase_step_0':info['delta0'],
             'shape_fallback_permitted_increase_after_step_0':info['permitted_after'],
             'shape_fallback_nonpermitted_increase_count':0,
             'first_fewer_than_two_novelty_vectors_step':info['first_degenerate'],
             'recorder_rng_unchanged_calls':len(rows),'raw_entropy_exact_matches':len(rows),
             'heartbeat_count':len(defense.heartbeats),'incumbent_call_counts':calls_per_step,
             'binding_restored_by_identity':True,'step_observer_restored_by_identity':True,'attack_binding_restored_by_identity':True,
             'offline_equivalence':equivalence,'source_pins_start':start_pins,'source_pins_end':pins(),
             'runtime':metadata(np),'elapsed_seconds':time.perf_counter()-clock,
             'completed_utc':now(),'continuous_checks_passed':True}
    if gate:summary['datacollector']=model.datacollector
    write(P+job+('_result.json' if gate else '_complete.json'),summary)

def validate_completion(job,gate=False):
    result=read(P+job['job']+('_result.json' if gate else '_complete.json'))
    assert result['status']=='COMPLETE'
    for key in ('job','arm','defense_arm','seed'):assert result[key]==job[key],key
    assert result['identity']==identity()
    assert result['configuration']==expected_config(job['seed'],job['arm']!='M1')
    for key,hkey in [('raw_log','raw_log_sha256_lf'),('audit_file','audit_sha256_lf')]:
        assert sha(lf((OUT/result[key]).read_bytes()))==result[hkey],key
    assert result['binding_restored_by_identity'] and result['step_observer_restored_by_identity'] and result['attack_binding_restored_by_identity']
    assert result['continuous_checks_passed'] and result['heartbeat_count']==result['steps_completed']
    return result

def compare_fields(first,second,until=None):
    a=read(P+first+'_result.json');b=read(P+second+'_result.json')
    ra=log_rows(a['raw_log']);rb=log_rows(b['raw_log'])
    difference=None;checks=0
    if until is None and len(ra)!=len(rb):difference={'field':'row_count','first':len(ra),'second':len(rb)}
    if until is not None and (len(ra)<until or len(rb)<until):difference={'field':'insufficient_steps'}
    for x,y in zip(ra[:until],rb[:until]):
        if difference:break
        for k in x:
            if k in ('arm','defense_arm'):continue
            checks+=1
            if x[k]!=y[k] or type(x[k]) is not type(y[k]):
                difference={'field':k,'step':x['step'],'first':x[k],'second':y[k]};break
    result={'passed':difference is None,'first':first,'second':second,
            'comparisons':checks,'first_difference':difference,
            'identity_columns_not_observables':['arm','defense_arm']}
    write(P+first+'_versus_'+second+'.json',result)
    if difference:raise RuntimeError('Gate field comparison failed: '+json.dumps(result))
    return result

def attack_arithmetic_gate():
    import attack_adapter_v2 as adapter
    cases=[]
    def production(model,ai,action,step,actor_role='incumbent'):
        return deepcopy(action)
    attack=Attack('A3');wrapper=attack.wrap(production)
    for index in range(24):
        resilience=(0.0,0.0005,0.2)[index%3]
        weights=(0.1,0.2,0.25,0.15,0.3)
        offset=index%5;weights=weights[offset:]+weights[:offset]
        action={k:(1.0-resilience)*w for k,w in zip(FIELDS[:-1],weights)}
        action.update(x_resilience=resilience,c_protective=0.1+0.02*index,
                      c_suppressive=0.05+0.01*index,extra={'case':index})
        action=adapter._normalize_action(action);original=deepcopy(action)
        moved=float(action['x_resilience'])
        expected=deepcopy(action);expected['x_resilience']=0.0
        expected['x_institutional_capacity']+=moved
        expected=adapter._normalize_action(expected)
        step=(50,53,149,299)[index%4]
        actual=wrapper(None,None,action,step,actor_role='incumbent')
        before_normalization=deepcopy(attack.calls[-1]['before_normalization'])
        differences={k:abs(float(actual[k])-float(expected[k])) for k in FIELDS}
        before={str(t):wrapper(None,None,action,t,actor_role='incumbent') for t in (0,9,49)}
        constraints_exact=all(actual[k]==original[k] for k in ('c_protective','c_suppressive'))
        before_exact=all(v==original for v in before.values())
        shares_sum=sum(actual[k] for k in FIELDS)
        passed=(all(v<=1e-12 for v in differences.values()) and constraints_exact
                and abs(shares_sum-1.0)<=1e-12 and before_exact
                and action==original and actual['extra']==original['extra']
                and before_normalization['x_resilience']==0.0 and actual['x_resilience']<=1e-12)
        cases.append({'arm':'A3','case':index,'resilience_category':('zero','small','large')[index%3],
                      'input':original,'step':step,'moved':moved,'expected':expected,'actual':actual,
                      'before_normalization':before_normalization,
                      'share_absolute_differences':differences,'share_sum':shares_sum,
                      'constraints_unchanged_exactly':constraints_exact,'pre_onset_outputs':before,
                      'pre_onset_unchanged_exactly':before_exact,'input_unchanged_exactly':action==original,
                      'passed':passed})
    result={'passed':all(c['passed'] for c in cases),'case_count':24,
            'computed_share_absolute_tolerance':1e-12,'share_sum_absolute_tolerance':1e-12,
            'constraint_and_pre_onset_equality':'exact','cases':cases}
    write(P+'attack_arithmetic_gate.json',result)
    assert result['passed'],'T1 gate 3: attack arithmetic'
    return result

def reference_constructor(seed,honest=False):
    from model import GardenModel
    config={'policy':'optimize_u_sys_v2','random_seed':seed,'phi':10.0,'attack_step':50,'n_candidates_v2':300,'rollout_steps_v2':20,'bootstrap_turn_step_v2':20,'shock_step':0,'shock_magnitude':0.15}
    if not honest:config['attack_vector_v2']='sub_threshold_drift'
    return GardenModel(n_agents=200,ai_policy='sub_threshold_drift',use_cop=True,cop_attribution_check=True,cop_drift_check=True,cop_cusum_drift=False,config=config)

def recovery_mechanics_gate():
    channels,medians,_,_=constants()
    all_cases=[]
    for k in (20,):
        cases=[
            ('veto_release',[12],[(12,'NORMAL','VETO','escalation'),(12+k,'VETO','NORMAL','recovery')],12+k+1),
            ('two_step_downs',[12,13],[(12,'NORMAL','VETO','escalation'),(13,'VETO','CONSENSUS','escalation'),
              (13+k,'CONSENSUS','VETO','recovery'),(13+2*k,'VETO','NORMAL','recovery')],13+2*k+1),
            ('reset_before_quiet_completes',[12,13,12+k],[(12,'NORMAL','VETO','escalation'),
              (13,'VETO','CONSENSUS','escalation'),(12+2*k,'CONSENSUS','VETO','recovery'),
              (12+3*k,'VETO','NORMAL','recovery')],12+3*k+1),
            ('alarm_preempts_step_down',[12,13,13+k],[(12,'NORMAL','VETO','escalation'),
              (13,'VETO','CONSENSUS','escalation'),(13+2*k,'CONSENSUS','VETO','recovery'),
              (13+3*k,'VETO','NORMAL','recovery')],13+3*k+1),
            ('re_escalation',[12,13,14+k],[(12,'NORMAL','VETO','escalation'),
              (13,'VETO','CONSENSUS','escalation'),(13+k,'CONSENSUS','VETO','recovery'),
              (14+k,'VETO','CONSENSUS','escalation'),(14+2*k,'CONSENSUS','VETO','recovery'),
              (14+3*k,'VETO','NORMAL','recovery')],14+3*k+1)]
        for name,alarms,expected,horizon in cases:
            defense=Defense('RECOVER-'+str(k),channels,medians)
            sequence=[]
            for step in range(horizon):
                defense.previous_action=dict(CONSENSUS,snapshot_step=step-1)
                defense.advance_state(step,step in alarms)
                if step in alarms:assert defense.quiet_count==0
                for transition in defense.transitions:
                    if transition['step']==step and transition['to']=='VETO':
                        assert transition['held_action']['snapshot_step']==step-1
                sequence.append({'step':step,'alarm':step in alarms,'state':defense.state,
                                 'quiet_count':defense.quiet_count})
            actual=[(t['step'],t['from'],t['to'],t['direction']) for t in defense.transitions]
            assert actual==expected,(k,name,actual,expected)
            if name=='re_escalation':
                assert sum(t['re_escalation_after_recovery'] for t in defense.transitions)==1
            all_cases.append({'k':k,'case':name,'alarm_steps':alarms,'expected_transitions':expected,
                              'actual_transitions':defense.transitions,'sequence':sequence,'passed':True})
    value={'passed':True,'cases':all_cases}
    write(P+'recovery_mechanics_gate.json',value)
    return {'passed':True,'case_count':len(all_cases),'evidence_file':P+'recovery_mechanics_gate.json'}

def recovery_no_oracle_gate():
    base=no_oracle_gate()
    channels,medians,_,_=constants()
    class RecordedOnly(dict):
        def __getitem__(self,key):
            assert key in ('h_n_latest','g')+FIELDS,('forbidden observable',key)
            return super().__getitem__(key)
    cases=[]
    for k in (20,):
        sequences=[]
        for sentinel in ('one',{'two':[99]}):
            defense=Defense('RECOVER-'+str(k),channels,medians)
            defense.honest_action=deepcopy(sentinel)
            defense.adapter_event=deepcopy(sentinel)
            defense.attack_configuration=deepcopy(sentinel)
            for step in range(3*k+20):
                observation=RecordedOnly(dict(CONSENSUS,h_n_latest=0.0 if step in (12,13) else 1.0,
                                             g=0.0,honest_action=sentinel,adapter_event=sentinel))
                defense.update(step,observation,dict(CONSENSUS,snapshot_step=step))
            sequences.append({'transitions':defense.transitions,'state':defense.state,'quiet':defense.quiet_count,
                              'alarms':defense.alarms})
        assert sequences[0]==sequences[1]
        assert any(t['direction']=='recovery' for t in sequences[0]['transitions'])
        cases.append({'k':k,'sentinel_cases':2,'sequence':sequences[0],'passed':True})
    result={'passed':True,'base_sentinel_gate':base,'recovery_cases':cases,
            'recovery_inputs':['step','alarm_boolean','own_state','own_quiet_counter','own_action_snapshot']}
    write(P+'recovery_no_oracle_gate.json',result)
    return {'passed':True,'evidence_file':P+'recovery_no_oracle_gate.json'}

def recovery_inertness_gate():
    left=read(P+'gate_H_LATCHED_result.json');right=read(P+'gate_H_RECOVER20_result.json')
    a=log_rows(left['raw_log']);b=log_rows(right['raw_log'])
    aa=read(left['audit_file']);bb=read(right['audit_file'])
    recovery=next((t for t in bb['transitions'] if t['direction']=='recovery'),None)
    first=None;checks=0
    for x,y in zip(a,b):
        for key in x:
            if key in ('arm','defense_arm'):continue
            checks+=1
            if x[key]!=y[key] or type(x[key]) is not type(y[key]):
                first={'step':x['step'],'field':key,'latched':x[key],'recover_20':y[key]}
                break
        if first:break
    state_difference=next(({'step':x['step'],'latched':x['state_after_step'],'recover_20':y['state_after_step']}
                          for x,y in zip(aa['steps'],bb['steps'])
                          if x['state_after_step']!=y['state_after_step']),None)
    if recovery is None:
        assert first is None and state_difference is None and len(a)==len(b)
    else:
        assert state_difference is not None and state_difference['step']==recovery['step']
        assert recovery['direction']=='recovery'
        assert first is None or first['step']>=recovery['effective_from_step']
        assert all(x==y for x,y in zip(aa['alarms'],bb['alarms']) if x['step']<=recovery['step'] and y['step']<=recovery['step'])
    evidence={'passed':True,'exact_recorded_field_comparisons':checks,'first_recovery':recovery,
              'first_state_divergence':state_difference,'first_recorded_model_field_divergence':first,
              'timing':'State transition after step t affects actions from step t+1.',
              'recorded_fields_exact_until_recovery':True}
    write(P+'recovery_inertness_gate.json',evidence)
    return evidence

def m1_identity_gate():
    seed=1835088100
    reference=reference_constructor(seed,False)
    reference_configuration=deepcopy(reference.config)
    required=deepcopy(reference_configuration)
    required.update(shock_step=150,shock_magnitude=0.60)
    run=read(P+'gate_M1_OFF_result.json')
    actual=run['configuration']
    checks=[{'field':key,'reference_with_registered_shock':value,'actual':actual.get(key),
             'passed':key in actual and actual[key]==value and type(actual[key]) is type(value)}
            for key,value in required.items()]
    assert actual==required and set(actual)==set(required) and all(c['passed'] for c in checks)
    value={'passed':True,'seed':seed,'reference_configuration':reference_configuration,
           'registered_shock_overrides':{'shock_step':150,'shock_magnitude':0.60},
           'checks':checks,'reference_constructor_basis':'Copied verbatim from committed drift_defense_run_executor.py'}
    write(P+'m1_identity_gate.json',value)
    return value

def gates():
    import numpy as np
    evidence={'source_pins_start':pins(full=True),'scheduler':scheduler_checks()}
    channels,medians,hazard,checks=constants()
    expected=dict(zip(FIELDS,(0.1360229355155997,0.2061409568906703,0.052807183062202334,0.26711884854035045,0.2846084192537951,0.053301656737382165)),c_protective=0.4,c_suppressive=0.2)
    for field,value in expected.items():
        checks.append({'quantity':'consensus.'+field,'actual':CONSENSUS[field],'expected':value,
                       'binary64_hex':float(value).hex(),'passed':float(CONSENSUS[field]).hex()==float(value).hex()})
    assert all(c['passed'] for c in checks)
    evidence['9_constants']={'passed':True,'checks':checks,'channels':channels,'medians':medians}
    write(P+'constants_gate.json',evidence['9_constants'])
    evidence['2_recovery_mechanics']=recovery_mechanics_gate()
    evidence['3_attack_arithmetic']={'passed':attack_arithmetic_gate()['passed'],'evidence_file':P+'attack_arithmetic_gate.json'}
    evidence['7_no_oracle']=recovery_no_oracle_gate()
    write(P+'gates.json',{'passed':False,'status':'IN_PROGRESS',**evidence})
    dispatch(read(P+'plan.json')['gate_jobs'],'gates')
    evidence['1_inertness']=recovery_inertness_gate()
    evidence['4_m1_identity']=m1_identity_gate()
    evidence['5_composition']=[compare_fields('gate_H_OFF','gate_H_NORMAL'),
                               compare_fields('gate_A3_OFF','gate_A3_NORMAL')]
    evidence['6_online_equivalence']={}
    for name in ('gate_M1_LATCHED','gate_A3_LATCHED'):
        result=read(P+name+'_result.json')
        evidence['6_online_equivalence'][name]=result['offline_equivalence']
    result=read(P+'gate_M1_RECOVER20_result.json')
    evidence['8_incumbent_calls']={'passed':all(n==1 for n in result['incumbent_call_counts'].values()),
                                  'per_step_counts':result['incumbent_call_counts']}
    assert evidence['8_incumbent_calls']['passed']
    evidence['10_source_pins_end']=pins(full=True)
    write(P+'gates.json',{'passed':True,'status':'COMPLETE','runtime':metadata(np),**evidence})

def slots(mode,active,pending):
    return min(pending,max(0,(15 if mode=='normal' else 12)-active))

def scheduler_checks():
    measured=[slots(*x) for x in [('normal',0,80),('work',15,10),('work',13,10),('work',12,10),('work',11,10),('normal',12,10),('normal',0,2)]]
    assert measured==[15,0,0,0,1,3,2]
    jobs=read(P+'plan.json')['jobs'];ids=[j['job'] for j in jobs]
    assert len(ids)==len(set(ids))==180
    synthetic_completed={ids[0],ids[-1]};pending=[j for j in jobs if j['job'] not in synthetic_completed]
    assert len(pending)==178
    assert all(j['seed'] in range(1835088100,1835088120) for j in pending)
    assert {j['job']:j['seed'] for j in jobs}=={j['job']:j['seed'] for j in reversed(jobs)}
    result={'passed':True,'normal_cap':15,'work_cap':12,'slot_measurements':measured,
            'synthetic_resume_preserved':2,'synthetic_resume_pending':178,
            'seed_assignment_independent_of_dispatch_order':True}
    write(P+'scheduler_checks.json',result)
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
        for _ in range(slots(mode,len(active),len(pending))):
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


def merge_artifacts():
    jobs=sorted(read(P+'plan.json')['jobs'],key=lambda j:(j['arm'],j['defense_arm'],j['seed']))
    merged=OUT/(P+'steps.csv');completion_path=OUT/(P+'completions.jsonl')
    summaries=[];per_run=[];deletions=[];header=None
    with merged.open('xb') as step_handle,completion_path.open('x',encoding='utf-8',newline='\n') as complete_handle:
        for job in jobs:
            summary=validate_completion(job)
            raw=lf((OUT/summary['raw_log']).read_bytes())
            first,body=raw.split(b'\n',1)
            if header is None:header=first;step_handle.write(header+b'\n')
            assert first==header,'Merged CSV column mismatch'
            step_handle.write(body)
            rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))
            assert len(rows)==summary['steps_completed']
            for row in rows:
                assert row['arm']==job['arm'] and row['defense_arm']==job['defense_arm'] and int(row['seed'])==job['seed']
            complete_handle.write(json.dumps(summary,sort_keys=True,ensure_ascii=True,allow_nan=False)+'\n')
            summaries.append(summary)
            per_run.append({'job':job['job'],'arm':job['arm'],'defense_arm':job['defense_arm'],
                            'seed':job['seed'],'row_count':len(rows),'rows_sha256_lf':sha(body),
                            'rows_hash_basis':'Original CSV data rows as written, without header, LF normalized',
                            'original_csv_sha256_lf':sha(raw),'original_completion_sha256_lf':sha(lf((OUT/(P+job['job']+'_complete.json')).read_bytes())),
                            'audit_file':summary['audit_file'],'audit_sha256_lf':summary['audit_sha256_lf']})
            deletions.extend([{'path':summary['raw_log'],'kind':'step_logs'},
                              {'path':P+job['job']+'_complete.json','kind':'completion_records'}])
            for kind,pattern in [('initial',P+job['job']+'_initial.json'),('progress',P+job['job']+'_progress.json'),('console',P+job['job']+'_console_attempt*.log')]:
                deletions.extend({'path':path.name,'kind':kind} for path in OUT.glob(pattern))
        step_handle.flush();os.fsync(step_handle.fileno())
        complete_handle.flush();os.fsync(complete_handle.fileno())
    recovered={}
    with merged.open(encoding='utf-8',newline='') as stream:
        reader=csv.DictReader(stream);fields=reader.fieldnames
        for row in reader:
            key=(row['arm'],row['defense_arm'],int(row['seed']))
            recovered.setdefault(key,[]).append(row)
    for item in per_run:
        rows=recovered.pop((item['arm'],item['defense_arm'],item['seed']))
        assert len(rows)==item['row_count']
        rendered=io.StringIO(newline='')
        writer=csv.DictWriter(rendered,fieldnames=fields,lineterminator='\n')
        writer.writerows(rows)
        assert sha(rendered.getvalue().encode('utf-8'))==item['rows_sha256_lf'],'Artifact merge cannot reproduce run rows'
        assert [int(r['step']) for r in rows]==list(range(item['row_count']))
    assert not recovered
    with completion_path.open(encoding='utf-8') as stream:
        recovered_completions=[json.loads(line) for line in stream]
    assert recovered_completions==summaries
    assert len({d['path'] for d in deletions})==len(deletions)
    evidence={'status':'VERIFIED_BEFORE_DELETION','per_run':per_run,
              'merged_files':[{'path':merged.name,'sha256_lf':sha(lf(merged.read_bytes())),'row_count':sum(i['row_count'] for i in per_run)},
                              {'path':completion_path.name,'sha256_lf':sha(lf(completion_path.read_bytes())),'row_count':len(summaries)}],
              'planned_deletions':deletions,'deleted_file_counts':{k:0 for k in ('step_logs','completion_records','progress','initial','console')}}
    write(P+'merge.json',evidence)
    write(P+'manifest.json',{'status':'MERGE_VERIFIED_BEFORE_DELETION','merge':evidence,
                             'source_pins':pins(full=True),'identity':identity()})
    for item in deletions:
        path=(OUT/item['path']).resolve()
        assert path.parent==OUT and path.name.startswith(P)
        DELETE_ALLOWED.add(str(path))
        path.unlink()
        DELETE_ALLOWED.remove(str(path))
        evidence['deleted_file_counts'][item['kind']]+=1
    evidence['status']='COMPLETE'
    write(P+'merge.json',evidence)
    return evidence

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
        else:assert read(P+'gates.json')['passed']
        dispatch(read(P+'plan.json')['jobs'],'batch',resume=args.command=='resume')
        pins(full=True)
        merge_artifacts()
        completed=subprocess.run([sys.executable,'-B',str(OUT/(P+'analysis.py'))],cwd=ROOT)
        if completed.returncode:raise RuntimeError('Analysis failed with exit '+str(completed.returncode))
        print(json.dumps({'status':'COMPLETE','runs':180,'report':P+'report.md','results':P+'results.json','manifest':P+'manifest.json'}),flush=True)
    except BaseException as error:
        mark_halt(args.command+':'+str(args.job),error)
        if args.command!='worker':
            for child in CHILDREN:
                if child.poll() is None:child.wait()
            subprocess.run([sys.executable,'-B',str(OUT/(P+'analysis.py')),'--halt'],cwd=ROOT)
        print(json.dumps({'status':'HALTED','where':args.command,'error':str(error)}),flush=True)
        raise SystemExit(2)

if __name__=='__main__':main()
