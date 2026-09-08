"""Read-only current-substrate drift characterization; no repair is applied."""
import sys
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8')
import os
THREAD_ENV=['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']
for key in THREAD_ENV: os.environ[key]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
SELF=Path(__file__).resolve()
NULL=Path(os.devnull).resolve()
VIOLATIONS=[]


def allowed(path):
    p = Path(path).resolve()
    return p.parent == OUT and p.name.startswith('drift_char_')

def writable(path):
    return Path(path).resolve() == NULL or allowed(path)

def audit(event, args):
    problem = None
    if event == 'open':
        path, mode, flags = args
        writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC))
        if writing and not isinstance(path, int) and not writable(path):
            problem = 'writable open: ' + str(path)
    elif event == 'os.rename':
        if not allowed(args[0]) or not allowed(args[1]):
            problem = 'rename outside prefix'
    elif event in ('os.remove', 'os.rmdir', 'os.mkdir', 'os.link', 'os.symlink'):
        problem = event
    if problem:
        VIOLATIONS.append(problem)
        raise RuntimeError('WRITE SCOPE HALT: ' + problem)


sys.addaudithook(audit)
sys.path.insert(0,str(ROOT/'simulation'))
import argparse,ast,copy,csv,ctypes,hashlib,io,json,math,statistics,subprocess,time,traceback
from datetime import datetime,timezone
SEEDS=list(range(1835086199,1835086239))
FIELDS=['kind','seed','steps_completed','final_population','successor_present','attack_succeeded','defense_fired','extinct','collapsed','elapsed_seconds']
CONTEXT='  D1, suppression semantics. The novelty entropy estimator will be made\n  magnitude-sensitive:\n      H_N = spectral_shape * magnitude_factor\n      spectral_shape   = the current normalized spectral entropy, unchanged, so\n                         dimensional-masking resistance is preserved exactly\n      magnitude_factor = 1 - exp(-3.0 * V / V_ref)\n      V                = total novelty variance = trace of the covariance of the\n                         per-step novelty matrix = sum of the raw covariance\n                         eigenvalues BEFORE the normalization step\n      V_ref            = a fixed calibration constant, measured on the honest\n                         baseline, frozen and published before any characterization\n                         run consumes it\n  The saturation constant 3.0 is the inherited house value, not a free parameter.\n\n  D2, attack-success definition. Dual quantity per vector: keep the action-change\n  binary as the comparable metric, and add an outcome differential against a\n  seed-paired honest arm as the substantive metric. General rule to record: prefer\n  counts and paired differences over ratios, because a ratio invites an endogenous\n  denominator and an unpaired ratio hides a floor. Worked example already banked:\n  the veto vector uses per-run block COUNT, paired, not a per-vote rate.\n\n  D3, detector observable. A one-sided lower CUSUM on the protected observable\n  (novelty entropy under the D1 repair):\n      S_t = max(0, S_{t-1} + k * H_ref - H_N_t)\n  with the committed suppression posture as a fast, exact, zero-lag corroborating\n  channel. H_ref anchored to the fixed honest-baseline calibration, NEVER to running\n  history. A periodic independent recomputation of the optimal policy re-anchors\n  H_ref (this is the architecture\'s "periodic full reset verification"). Reset on\n  alarm so the score cannot latch. A liveness signature distinct from the alarm\n  signature. The alarm threshold D_alarm is placed BELOW the structural defection\n  threshold d_defect by the loop response time at the worst-case approach rate, and\n  the margin is stated as a number. No M-out-of-N counter.'

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))

def write(name, value):
    target = OUT / name
    if not allowed(target):
        raise RuntimeError('WRITE SCOPE HALT: output name')
    temp = OUT / (name + '.tmp')
    with temp.open('w', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, target)

def write_text(name, value):
    if not allowed(OUT / name):
        raise RuntimeError('WRITE SCOPE HALT: text output name')
    with (OUT / name).open('w', encoding='utf-8', newline='\n') as f:
        f.write(value)
        f.flush()
        os.fsync(f.fileno())

def assert_guard():
    if VIOLATIONS:
        raise RuntimeError('WRITE SCOPE HALT: ' + repr(VIOLATIONS))

def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=False)

def budget(mode):
    if mode not in ('normal', 'work'):
        raise RuntimeError('Invalid CPU mode')
    return 15 if mode == 'normal' else 12

def dispatch_slots(mode, active, pending):
    return min(pending, max(0, budget(mode) - active))

def module_sources():
    result = {}
    for module in list(sys.modules.values()):
        value = getattr(module, '__file__', None)
        if value:
            path = Path(value).resolve()
            if path.suffix == '.py' and path.is_relative_to(ROOT / 'simulation'):
                result[path.relative_to(ROOT).as_posix()] = sha(path)
    return result

def thread_runtime(np):
    records = []
    for dll in (Path(np.__file__).resolve().parent.parent / 'numpy.libs').iterdir():
        if dll.suffix.lower() == '.dll' and 'openblas' in dll.name.lower():
            lib = ctypes.CDLL(str(dll))
            for name in ['scipy_openblas_get_num_threads64_', 'openblas_get_num_threads64_', 'scipy_openblas_get_num_threads', 'openblas_get_num_threads']:
                try:
                    query = getattr(lib, name)
                except AttributeError:
                    continue
                query.argtypes = []
                query.restype = ctypes.c_int
                records.append({'library':str(dll), 'query':name, 'effective_threads':query()})
    if not records or any(x['effective_threads'] != 1 for x in records):
        raise RuntimeError('Numerical-library thread limit not verified')
    return records


def jobs(): return ['baseline_'+str(seed) for seed in SEEDS]
def result_name(job): return 'drift_char_result_'+job+'.json'
def log_name(job): return 'drift_char_steps_'+job+'.csv'
def decode(job):
    if job=='attack': return 'ATTACK',1835086199
    seed=int(job.removeprefix('baseline_'))
    if job!='baseline_'+str(seed) or seed not in SEEDS: raise RuntimeError('Invalid job')
    return 'BASELINE',seed

def fingerprint(plan):
    return hashlib.sha256(json.dumps({k:v for k,v in plan.items() if k!='fingerprint'},sort_keys=True).encode()).hexdigest()

def task_config(plan,job):
    kind,seed=decode(job)
    if kind=='ATTACK': return copy.deepcopy(plan['attack_task']),None
    return None,dict(plan['baseline_config'],random_seed=seed)

def prepare():
    if (OUT/'drift_char_plan.json').exists(): raise RuntimeError('Plan exists; use run to resume')
    h=git('rev-parse','HEAD'); branch=git('branch','--show-current'); anc=git('merge-base','--is-ancestor','f1ae659','HEAD')
    advisor=git('ls-files','--error-unmatch','--','LINEAGE_IMPERATIVE_ADVISOR.md')
    constants_path=ROOT/'simulation/constants_v2_stage18.py'
    constants_text=constants_path.read_text(encoding='utf-8')
    wanted={'FRONTIER_FLOOR':0.02,'RUNAWAY_THRESHOLD':1.5,'ALPHA_DEFAULT':1.0,'CONVERGENCE_STRENGTH':1.0}
    values={}; locations={}
    for node in ast.parse(constants_text).body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in wanted:
            values[node.targets[0].id]=ast.literal_eval(node.value); locations[node.targets[0].id]=node.lineno
    gates=[{'number':1,'passed':h.returncode==0 and branch.stdout.strip()=='main' and anc.returncode==0,'head':h.stdout.strip(),'branch':branch.stdout.strip(),'merge_base_exit':anc.returncode},
           {'number':2,'passed':(ROOT/'LINEAGE_IMPERATIVE_ADVISOR.md').is_file() and advisor.returncode!=0,'advisor_present':(ROOT/'LINEAGE_IMPERATIVE_ADVISOR.md').is_file(),'git_ls_files_exit':advisor.returncode},
           {'number':3,'passed':values==wanted,'read_values':values,'definition_lines':locations}]
    if not all(g['passed'] for g in gates):
        write('drift_char_precondition_failure.json',{'gates':gates}); raise RuntimeError('Precondition gate failure')
    manifest_path=ROOT/'simulation/diagnostics/attack_vector_revalidation_manifest.md'
    manifest=manifest_path.read_text(encoding='utf-8')
    line_no,line=next((n,x) for n,x in enumerate(manifest.splitlines(),1) if x.startswith('| sub_threshold_drift |'))
    vector,directory,expected_rows,expected_blob=[x.strip().strip('`') for x in line.strip('|').split('|')]
    ref='attack-v2-revalidation-evidence'
    paths=git('ls-tree','-r','--name-only',ref).stdout.splitlines()
    matched=[p for p in paths if Path(p).parent.name==directory and Path(p).name=='results.csv']
    if len(matched)!=1: raise RuntimeError('Manifest result did not resolve uniquely')
    path=matched[0]
    raw=subprocess.check_output(['git','show',ref+':'+path],cwd=ROOT)
    actual=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if actual!=expected_blob: raise RuntimeError('Pinned CSV blob mismatch before parsing')
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8'),newline=''))
    rows=list(reader)
    if len(rows)!=int(expected_rows): raise RuntimeError('Pinned CSV row count mismatch')
    selected=min(((n,r) for n,r in enumerate(rows,1) if r['defense_active']=='True' and float(r['parameter_phi'])==10.0),key=lambda x:(int(x[1]['replicate']),x[0]))
    row=selected[1]
    basepath=OUT/'cusum_char_stage1_baseline_summary.json'
    baseline=json.loads(basepath.read_text(encoding='utf-8'))['runs'][0]['config']
    expected={k:row[k]=='True' for k in ['attack_succeeded','defense_fired','extinct','collapsed']}
    files=git('ls-files','--','simulation').stdout.splitlines()
    catalog={p:sha(ROOT/p) for p in files if p.endswith('.py') and '/diagnostics/' not in p}
    plan={'created_utc':now(),'head':h.stdout.strip(),'machine':os.environ['COMPUTERNAME'],'gates':gates,'read_constants':values,
          'source_catalog':catalog,'script_sha256':sha(SELF),'fixed_design_decisions':CONTEXT,'baseline_config':baseline,
          'baseline_constructor':{'n_agents':200,'ai_policy':'optimize_u_sys_v2','use_cop':True,'cop_attribution_check':True,'cop_drift_check':True,'cop_cusum_drift':True},
          'baseline_reference':{'path':basepath.relative_to(ROOT).as_posix(),'sha256':sha(basepath)},
          'attack_task':{'vector':vector,'mode':row['mode'],'machine':row['machine'],'parameters':{'defense_active':True,'phi':float(row['parameter_phi'])},'replicate':int(row['replicate']),'seed':int(row['seed'])},
          'expected_reproduction':expected,'runtime_settings':{'steps':int(row['steps_requested']),'n_candidates_v2':int(row['n_candidates_v2']),'rollout_steps_v2':int(row['rollout_steps_v2'])},
          'evidence':{'manifest':manifest_path.relative_to(ROOT).as_posix(),'manifest_sha256':sha(manifest_path),'manifest_line':line_no,'tag':ref,'tag_commit':git('rev-parse',ref+'^{}').stdout.strip(),'path':path,'expected_blob':expected_blob,'actual_blob':actual,'sha256':hashlib.sha256(raw).hexdigest(),'rows_counted':len(rows),'columns':list(rows[0]),'selected_data_row':selected[0],'selected_row':row,'selection_rule':'Defended phi=10; lowest replicate, then CSV data-row order. Chosen to match the first baseline seed.','directory_files':[p for p in paths if Path(p).parent==Path(path).parent]},
          'seeds':SEEDS,'cpu_budget':16,'normal_worker_limit':15,'work_worker_limit':12,'null_device_exemption':True,
          'source_conflicts':['The denominator has a 0.01 floor, not a bare product.','The technology factor has a 0.01 floor.','The drift factory supplies no successor, so no live yield comparison or transition cost is evaluated.','Separate proposed allocations need not share the action-dependent utility prefactor.','Equality at g* is not strict inferiority, and no irreversible g-crossing rule was found.'],
          'out_of_scope_instructions_ignored':['The prior task snapshot-edit authorization is superseded.','constants_v2_stage15.py:9-10 says to update that file if it differs from the program reference. The present write scope overrides that instruction; no update is performed.']}
    checks=self_check(plan)
    plan['operational_checks']=checks; plan['fingerprint']=fingerprint(plan)
    write('drift_char_plan.json',plan)
    write('drift_char_control.json',{'mode':'normal','updated_utc':now()})
    write_text('drift_char_report.md','Characterization and constant measurement before repair. Not registered characterization data or framework evidence.\n\nStatus: preconditions passed; T0 reproduction pending. No repair is implemented.\n\nFixed design context, verbatim:\n\n```text\n'+CONTEXT+'\n```\n')
    print(json.dumps({'preconditions':'PASS','head':plan['head'],'selected_seed':row['seed'],'pinned_blob':actual,'rows_counted':len(rows),'operational_checks':checks}),flush=True)

def self_check(plan):
    assert len(jobs())==len(set(jobs()))==40
    assert [decode(j)[1] for j in jobs()]==SEEDS
    assert dispatch_slots('normal',0,40)==15
    assert dispatch_slots('work',15,40)==dispatch_slots('work',12,40)==0
    assert dispatch_slots('work',11,40)==1
    assert dispatch_slots('normal',12,40)==3
    assert dispatch_slots('normal',0,2)==2
    assert writable(os.devnull) and not writable(ROOT/'unscoped.tmp')
    assert all(task_config(plan,j)[1]==dict(plan['baseline_config'],random_seed=decode(j)[1]) for j in jobs())
    return {'passed':True,'simulation_runs':0,'checks':['unique prescribed seeds','normal/work dispatch and draining','null-device exemption and write predicate','baseline configuration identity']}

def load_plan():
    plan=read('drift_char_plan.json')
    if fingerprint(plan)!=plan['fingerprint'] or sha(SELF)!=plan['script_sha256']: raise RuntimeError('Plan or harness identity changed')
    if git('rev-parse','HEAD').stdout.strip()!=plan['head']: raise RuntimeError('HEAD changed after preparation')
    for p,d in plan['source_catalog'].items():
        if sha(ROOT/p)!=d: raise RuntimeError('Source changed: '+p)
    return plan

def g_snapshot(model,np):
    avg=float(np.mean([a.well_being for a in model.schedule])) if model.schedule else 0.0
    theta=float(model.theta_capability); transfer=float(model.transfer_state)
    avg=max(0.0,min(1.0,avg)); denom=max(0.01,avg*transfer)
    from constants_v2_stage18 import FRONTIER_FLOOR
    return max(FRONTIER_FLOOR,theta)/denom

class Recorder:
    def __init__(self,job,plan,np):
        self.job=job; self.plan=plan; self.np=np; self.rows=[]
        self.temp=OUT/(log_name(job)+'.partial')
        self.handle=self.temp.open('w',encoding='utf-8',newline='')
        self.writer=None
    def record(self,model,pre_g):
        np=self.np
        rng_before=np.random.get_state()
        dc=model.datacollector; step=len(dc['population'])-1
        X=np.asarray(model.novelty_log,dtype=float)
        if X.ndim!=2 or X.shape[0]<2 or X.shape[1]!=10 or not np.isfinite(X).all(): raise RuntimeError('Novelty matrix not usable for covariance logging')
        centered=X-X.mean(axis=0)
        V=float(np.trace(np.cov(centered,rowvar=False)))
        if V<0 or not math.isfinite(V): raise RuntimeError('Invalid raw covariance trace')
        avg=float(dc['avg_well_being'][-1]); theta=float(model.theta_capability); transfer=float(model.transfer_state)
        if theta!=dc['theta_capability'][-1] or transfer!=dc['transfer_state'][-1]: raise RuntimeError('Stock/collector mismatch')
        from constants_v2_stage18 import FRONTIER_FLOOR,RUNAWAY_THRESHOLD,ALPHA_DEFAULT,CONVERGENCE_STRENGTH
        from constants_v2_stage15 import LAMBDA_LINEAGE_COUPLING
        denom=max(0.01,max(0.0,min(1.0,avg))*transfer)
        g=max(FRONTIER_FLOOR,theta)/denom
        alpha=float(model.config.get('alpha',ALPHA_DEFAULT)); A=alpha*CONVERGENCE_STRENGTH
        gst=(RUNAWAY_THRESHOLD+math.log(2.0)/A)/2.0
        t1=math.exp(-A*max(0.0,g-RUNAWAY_THRESHOLD))
        t2=2.0*math.exp(-A*max(0.0,2.0*g-RUNAWAY_THRESHOLD))
        theta1=max(0.01,theta*transfer*t1); theta2=max(0.01,theta*transfer*t2)
        hn=float(dc['H_N'][-1]); he=float(dc['H_E'][-1]); heff=float(dc['h_eff_v2'][-1]); psi=max(0.01,float(model.psi_inst_stock))
        eps=float(model.config.get('epsilon',1e-6)); ln=float(model.config.get('lambda_n',5.0)); le=float(model.config.get('lambda_e',3.0))
        weight=ln*hn/(hn+eps)+le*he/(he+eps)
        reference_margin=weight*LAMBDA_LINEAGE_COUPLING*heff*psi*(theta2-theta1)
        generation=int(model.ai.generation)
        reference_cost=(1.0+model.beta_transition)*(model.k1_transition*math.log(2.0)*math.log(generation+1.0)+model.k2_transition/psi)
        live=next((e for e in reversed(model.yield_event_log) if e['step']==step),None)
        kind,seed=decode(self.job)
        r={'step':step,'seed':seed,'kind':kind,'V':V,'H_N':hn,'h_n_spectral':float(model.h_n_latest),'avg_wb':avg,
           'theta_capability':theta,'transfer_state':transfer,'absorption_denominator':denom,'g':g,
           'g_unfloored_ratio':max(FRONTIER_FLOOR,theta)/(avg*transfer) if avg*transfer>0 else None,
           'g_pre_step':pre_g,'g_change_within_step':g-pre_g,'population':len(model.schedule),'novelty_vector_count':int(X.shape[0]),
           'psi_inst_stock':float(model.psi_inst_stock),'H_eff':heff,'H_E':he,'U_sys':float(dc['U_sys'][-1]),'L_t':float(dc['L_t'][-1]),
           'incumbent_capability':float(model.ai.capability),'incumbent_generation':generation,'successor_present':model.successor_ai is not None,
           'total_suppression':float(dc['total_suppression'][-1]),'adapter_active':bool(dc['v2_attack_active'][-1]),
           'adapter_score':float(dc['v2_adapter_cusum_score'][-1]),'defense_fired':bool(dc['v2_defense_fired'][-1]),'action_modified':bool(dc['v2_attack_action_modified'][-1]),
           'live_yield_evaluated':live is not None,'live_yield_margin':live['advantage'] if live else None,'live_transition_cost':live['transition_cost'] if live else None,
           'reference_T_incumbent':t1,'reference_T_successor':t2,'reference_theta_incumbent':theta1,'reference_theta_successor':theta2,
           'reference_margin':reference_margin,'reference_transition_cost':reference_cost,'reference_soft_condition':reference_margin<=reference_cost,
           'reference_hard_condition':g>=gst,'reference_soft_only':reference_margin<=reference_cost and g<gst,'g_star':gst}
        r.update({k:float(v) for k,v in model._last_v2_action.items()})
        if kind=='BASELINE' and ('attack_vector_v2' in model.config or model.attack_vector_v2 is not None or r['adapter_active']): raise RuntimeError('Attack adapter active in baseline')
        rng_after=np.random.get_state()
        if rng_before[0]!=rng_after[0] or not np.array_equal(rng_before[1],rng_after[1]) or rng_before[2:]!=rng_after[2:]: raise RuntimeError('Recorder changed RNG state')
        if self.writer is None:
            self.writer=csv.DictWriter(self.handle,fieldnames=list(r)); self.writer.writeheader()
        self.writer.writerow(r); self.handle.flush(); self.rows.append(r)
    def finish(self):
        self.handle.flush(); os.fsync(self.handle.fileno()); self.handle.close()
        os.replace(self.temp,OUT/log_name(self.job))
    def close(self):
        if not self.handle.closed:self.handle.close()

def validate_result(plan,job,obj):
    kind,seed=decode(job)
    if not obj.get('complete') or obj.get('job')!=job or obj.get('plan_fingerprint')!=plan['fingerprint']: raise RuntimeError('Invalid completed identity')
    if obj['head']!=plan['head'] or obj['script_sha256']!=plan['script_sha256']:raise RuntimeError('Invalid completed source identity')
    if obj['row']['seed']!=seed or obj['row']['kind']!=kind:raise RuntimeError('Invalid completed seed')
    if kind=='BASELINE' and obj['constructed_config']!=dict(plan['baseline_config'],random_seed=seed):raise RuntimeError('Baseline configuration changed')
    if kind=='ATTACK' and obj['task']!=plan['attack_task']:raise RuntimeError('Attack task changed')
    for p,d in obj['simulation_source_sha256'].items():
        expected=plan['script_sha256'] if p==SELF.relative_to(ROOT).as_posix() else plan['source_catalog'].get(p)
        if expected!=d:raise RuntimeError('Unverified loaded simulation module: '+p)
    if not obj['thread_runtime'] or any(x['effective_threads']!=1 for x in obj['thread_runtime']):raise RuntimeError('Thread limit not verified')
    if obj['log_sha256']!=sha(OUT/log_name(job)):raise RuntimeError('Completion log hash mismatch')
    with (OUT/log_name(job)).open(encoding='utf-8',newline='') as f: count=sum(1 for _ in csv.DictReader(f))
    if count!=obj['row']['steps_completed']:raise RuntimeError('Completion log count mismatch')
    return obj['row']

def worker(job):
    plan=load_plan(); kind,seed=decode(job)
    if (OUT/result_name(job)).exists():raise RuntimeError('Completed job exists; refusing duplicate')
    if kind=='BASELINE' and not read(result_name('attack')).get('reproduction_passed'):raise RuntimeError('T0 has not passed')
    import numpy as np
    import run_attack_vector_revalidation_v2 as runner
    recorder=Recorder(job,plan,np); original=runner.GardenModel
    class RecordedModel(original):
        def step(self):
            pre_g=g_snapshot(self,np)
            alive=super().step()
            recorder.record(self,pre_g)
            assert_guard()
            return alive
    threads=thread_runtime(np); started=time.perf_counter()
    task,cfg=task_config(plan,job)
    try:
        if kind=='ATTACK':
            runner.GardenModel=RecordedModel
            try:model,settings=runner._make_model(task)
            finally:runner.GardenModel=original
        else:
            model=RecordedModel(config=cfg,**plan['baseline_constructor']); settings=plan['runtime_settings']
            if model.config!=cfg:raise RuntimeError('Constructed baseline mismatch')
        if settings!=plan['runtime_settings']:raise RuntimeError('Runtime settings mismatch')
        initial={'g':g_snapshot(model,np),'incumbent_capability':model.ai.capability,'incumbent_generation':model.ai.generation,'successor_present':model.successor_ai is not None}
        for _ in range(settings['steps']):
            if not model.step():break
        dc=model.datacollector; pop=len(model.schedule); peak=max(dc['population']) if dc['population'] else pop
        row={'kind':kind,'seed':seed,'steps_completed':len(dc['population']),'final_population':pop,'successor_present':model.successor_ai is not None,
             'attack_succeeded':runner._attack_success('sub_threshold_drift',model) if kind=='ATTACK' else None,
             'defense_fired':any(dc['v2_defense_fired']),'extinct':pop==0,'collapsed':pop<max(model.min_viable_population,int(0.65*peak)),
             'elapsed_seconds':time.perf_counter()-started}
        recorder.finish()
        obj={'complete':True,'job':job,'row':row,'plan_fingerprint':plan['fingerprint'],'head':plan['head'],'script_sha256':sha(SELF),'task':task,
             'constructed_config':dict(model.config),'runtime_settings':settings,'initial_state':initial,'yield_event_count':len(model.yield_event_log),
             'simulation_source_sha256':module_sources(),'machine':os.environ['COMPUTERNAME'],'python':sys.version,'numpy':np.__version__,
             'thread_environment':{k:os.environ[k] for k in THREAD_ENV},'thread_runtime':threads,'worker_pid':os.getpid(),'finished_utc':now(),
             'log':log_name(job),'log_sha256':sha(OUT/log_name(job)),
             'runtime_attributes':{k:getattr(model,k) for k in ['min_viable_population','reproduction_rate','use_cop','cop_attribution_check','cop_drift_check','cop_cusum_drift','hn_composite_method','k1_transition','k2_transition','beta_transition']}}
        if kind=='ATTACK':
            obj['reproduction_comparison']={k:{'pinned':v,'measured':row[k],'match':v==row[k]} for k,v in plan['expected_reproduction'].items()}
            obj['reproduction_passed']=all(x['match'] for x in obj['reproduction_comparison'].values())
        validate_result(plan,job,obj); write(result_name(job),obj)
        if kind=='ATTACK' and not obj['reproduction_passed']:raise RuntimeError('T0 reproduction mismatch')
        print(json.dumps({'job':job,'steps':row['steps_completed'],'reproduction_passed':obj.get('reproduction_passed'),'elapsed_seconds':row['elapsed_seconds']}),flush=True)
    finally:recorder.close()

def save_csv(completed):
    temp=OUT/'drift_char_runs.csv.tmp'
    with temp.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader()
        if (OUT/result_name('attack')).exists():w.writerow(read(result_name('attack'))['row'])
        for j in jobs():
            if j in completed:w.writerow(completed[j]['row'])
        f.flush();os.fsync(f.fileno())
    os.replace(temp,OUT/'drift_char_runs.csv')

def sufficiency(completed):
    return {'BASELINE':{'runs':len(completed),'steps':sum(x['row']['steps_completed'] for x in completed.values())}}


def run_batch():
    plan = load_plan()
    gate = read(result_name('attack'))
    validate_result(plan, 'attack', gate)
    if not gate.get('reproduction_passed'): raise RuntimeError('T0 reproduction has not passed')
    prior_progress = read('drift_char_progress.json') if (OUT / 'drift_char_progress.json').exists() else {}
    completed = {}
    for job in jobs():
        if (OUT / result_name(job)).exists():
            obj = read(result_name(job))
            validate_result(plan, job, obj)
            completed[job] = obj
    pending = [j for j in jobs() if j not in completed]
    active = {}
    mode = read('drift_char_control.json')['mode']
    budget(mode)
    history = prior_progress.get('mode_history', [])
    history.append({'utc':now(), 'mode':mode, 'event':'start_or_resume', 'validated_completed':len(completed)})
    peak_workers = prior_progress.get('peak_active_workers', 0)
    starts = prior_progress.get('batch_starts', []) + [{'utc':now(), 'completed_skipped':len(completed), 'incomplete_jobs_restart_from_seed':prior_progress.get('active_jobs', [])}]
    started = time.perf_counter()
    elapsed_prior = prior_progress.get('elapsed_seconds', 0.0)
    last_print = -100.0
    last_save = -100.0
    save_csv(completed)
    try:
        sufficiency(completed)
        while pending or active:
            assert_guard()
            new_mode = read('drift_char_control.json')['mode']
            budget(new_mode)
            if new_mode != mode:
                mode = new_mode
                history.append({'utc':now(), 'mode':mode, 'event':'mode_change_requested', 'active':len(active)})
            changed = False
            for job, proc in list(active.items()):
                code = proc.poll()
                if code is None:
                    continue
                del active[job]
                if code != 0:
                    detail = read('drift_char_failure_' + job + '.json') if (OUT / ('drift_char_failure_' + job + '.json')).exists() else {'halt':'worker exit ' + str(code)}
                    raise RuntimeError('Worker failed: ' + job + ': ' + str(detail))
                obj = read(result_name(job))
                validate_result(plan, job, obj)
                completed[job] = obj
                changed = True
            counts = sufficiency(completed)
            if changed:
                save_csv(completed)
            for _ in range(dispatch_slots(mode, len(active), len(pending))):
                job = pending.pop(0)
                active[job] = subprocess.Popen([sys.executable, '-B', str(SELF), '--job', job], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                peak_workers = max(peak_workers, len(active))
            elapsed = time.perf_counter() - started
            progress = {'status':'running', 'updated_utc':now(), 'completed':len(completed), 'running':len(active), 'pending':len(pending),
                        'active_jobs':list(active), 'mode':mode, 'worker_limit':budget(mode), 'peak_active_workers':peak_workers,
                        'mode_reduction_effective':len(active) <= budget(mode), 'mode_history':history, 'batch_starts':starts,
                        'elapsed_seconds':elapsed_prior+elapsed, 'by_arm':counts}
            if changed or elapsed-last_save >= 10:
                write('drift_char_progress.json', progress)
                last_save = elapsed
            if elapsed-last_print >= 30 or not active and not pending:
                print(json.dumps({k:progress[k] for k in ['status','completed','running','pending','mode','elapsed_seconds','by_arm']}), flush=True)
                last_print = elapsed
            if pending or active:
                time.sleep(1)
        progress.update(status='complete', active_jobs=[], completed=40, running=0, pending=0, updated_utc=now())
        write('drift_char_progress.json', progress)
        finalize()
    except BaseException as error:
        for proc in active.values():
            if proc.poll() is None:
                proc.terminate()
        for proc in active.values():
            proc.wait()
        save_csv(completed)
        write('drift_char_halt.json', {'halt':str(error), 'utc':now(), 'completed':len(completed), 'interrupted_jobs':list(active), 'violations':VIOLATIONS, 'traceback':traceback.format_exc()})
        write_text('drift_char_report.md', 'This is characterization of a known-defective measurement, not registered characterization data or framework evidence.\n\nHALTED: ' + str(error) + '\n\nCompleted floor runs: ' + str(len(completed)) + '. No further run was dispatched after detection. See drift_char_halt.json and drift_char_plan.json.\n')
        raise


def finalize():
    print('Baseline complete; analysis and report pending.',flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--run',action='store_true');p.add_argument('--job');p.add_argument('--mode',choices=['normal','work']);args=p.parse_args()
    try:
        if args.prepare:prepare()
        elif args.run:run_batch()
        elif args.job:worker(args.job)
        elif args.mode:write('drift_char_control.json',{'mode':args.mode,'updated_utc':now()})
        else:p.error('Specify operation')
    except BaseException as error:
        write('drift_char_failure_'+(args.job or 'controller')+'.json',{'halt':str(error),'utc':now(),'violations':VIOLATIONS,'traceback':traceback.format_exc()})
        print('HALT: '+str(error),flush=True);raise SystemExit(2)
if __name__=='__main__':main()
