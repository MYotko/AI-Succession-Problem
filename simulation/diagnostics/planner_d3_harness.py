"""Guarded measurements for the bounded rollout magnitude projection task."""
import sys
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8')
import os
THREAD_ENV=('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')
for key in THREAD_ENV: os.environ[key]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
os.environ['GIT_OPTIONAL_LOCKS']='0'
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
PRODUCTION={ROOT/'simulation'/name for name in ('metrics.py','model.py','agents.py')}
NULL=Path(os.devnull).resolve()
VIOLATIONS=[]
def allowed(path):
    p=Path(path).resolve()
    return p==NULL or p in PRODUCTION or (p.parent==OUT and p.name.startswith('planner_d3_'))
def audit(event,args):
    bad=None
    if event=='open':
        path,mode,flags=args
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_APPEND|os.O_CREAT|os.O_TRUNC))
        if writing and not isinstance(path,int) and not allowed(path): bad='writable open: '+str(path)
    elif event=='os.rename':
        if not allowed(args[0]) or not allowed(args[1]): bad='rename outside scope'
    elif event in ('os.remove','os.rmdir','os.mkdir','os.link','os.symlink'): bad=event
    if bad:
        VIOLATIONS.append(bad)
        raise RuntimeError('WRITE SCOPE HALT: '+bad)
sys.addaudithook(audit)
sys.path.insert(0,str(ROOT/'simulation'))
import argparse,base64,contextlib,csv,ctypes,hashlib,io,json,math,runpy,subprocess,time,traceback
from datetime import datetime,timezone

def now(): return datetime.now(timezone.utc).isoformat()
def lf(raw): return raw.replace(b'\r\n',b'\n')
def digest(raw): return hashlib.sha256(raw).hexdigest()
def read(name): return json.loads((OUT/name).read_text(encoding='utf-8'))
def textfile(name,text):
    if '\u2014' in text: raise RuntimeError('Em dash in authored output')
    with (OUT/name).open('w',encoding='utf-8',newline='\n') as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
def write(name,obj): textfile(name,json.dumps(obj,ensure_ascii=True,allow_nan=False,sort_keys=True,indent=2)+'\n')
def csvfile(name,rows):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
        f.flush();os.fsync(f.fileno())
def git(*args):
    p=subprocess.run(['git',*args],capture_output=True,cwd=ROOT)
    if p.returncode: raise RuntimeError('Read-only Git command failed: '+repr(args)+': '+p.stderr.decode('utf-8',errors='replace'))
    return p.stdout

def modules():
    result={}
    for module in list(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if filename:
            p=Path(filename).resolve()
            if p.suffix=='.py' and p.is_relative_to(ROOT/'simulation'):
                raw=p.read_bytes();result[p.relative_to(ROOT).as_posix()]={'sha256_raw':digest(raw),'sha256_lf':digest(lf(raw))}
    return result

def runtime(np):
    records=[]
    for dll in (Path(np.__file__).resolve().parent.parent/'numpy.libs').iterdir():
        if dll.suffix.lower()=='.dll' and 'openblas' in dll.name.lower():
            lib=ctypes.CDLL(str(dll))
            for name in ('scipy_openblas_get_num_threads64_','openblas_get_num_threads64_','scipy_openblas_get_num_threads','openblas_get_num_threads'):
                try: fn=getattr(lib,name)
                except AttributeError: continue
                fn.argtypes=[];fn.restype=ctypes.c_int
                records.append({'library':str(dll),'query':name,'effective_threads':fn()})
    if not records or any(r['effective_threads']!=1 for r in records): raise RuntimeError('Numerical thread limit not verified')
    return records

def metadata(np):
    return {'utc':now(),'machine':os.environ['COMPUTERNAME'],'python':sys.version,'numpy':np.__version__,'thread_environment':{k:os.environ[k] for k in THREAD_ENV},'thread_runtime':runtime(np),'modules':modules()}

def derive():
    import numpy as np
    state=read('planner_d3_state.json')
    head=state['head']
    paths=git('ls-files','simulation/diagnostics/drift_char_steps_baseline_*.csv').decode('utf-8').splitlines()
    if len(paths)!=40: raise RuntimeError('Expected exactly 40 committed baseline CSV files')
    inputs=[];records=[];ratios=[];clipped=[];rows_ge10=[];exceptions=[];contagion_rows=[]
    for path in paths:
        raw=git('cat-file','blob',head+':'+path)
        parsed=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
        rows=list(parsed)
        inputs.append({'path':path,'commit':head,'blob_sha1':hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),'sha256_lf':digest(lf(raw)),'row_count':len(rows),'columns':parsed.fieldnames})
        prev=None
        for r in rows:
            step=int(r['step']);V=float(r['V']);wb=float(r['avg_wb']);S=float(r['total_suppression']);A=wb*(1.0-S)
            if prev is not None:
                if step!=int(prev['step'])+1: raise RuntimeError('Nonconsecutive baseline steps')
                ratio=float(prev['H_N'])/max(1,int(r['population']))
                clipped_value=float(np.clip(ratio,0.5,2.0))
                ratios.append(ratio);clipped.append(clipped_value)
                contagion_rows.append({'seed':r['seed'],'step':step,'prev_H_N':float(prev['H_N']),'population':int(r['population']),'raw_ratio':ratio,'clipped':clipped_value})
            if step>=10:
                item={'seed':r['seed'],'step':step,'V':V,'avg_wb':wb,'total_suppression':S,'A':A}
                rows_ge10.append(item)
                if V==0.0 and S<1.0: exceptions.append(item)
                if V>0.0 and A>0.0: records.append(item)
            prev=r
    V=np.array([r['V'] for r in records]);A=np.array([r['A'] for r in records]);q=V/A**2
    K=float(np.median(q));corr=float(np.corrcoef(V,A**2)[0,1]);mare=float(np.median(np.abs(K*A**2-V)/V))
    zero=[r for r in rows_ge10 if r['V']==0.0]
    med_wb=float(np.median([r['avg_wb'] for r in rows_ge10]));med_S=float(np.median([r['total_suppression'] for r in rows_ge10]))
    V_op=K*(med_wb*(1-med_S))**2;op_ratio=V_op/state['H_N_V_REF']
    checks={'filtered_records_9205':len(records)==9205,'K_six_decimals':format(K,'.6f')=='0.242920','correlation_ge_0_99':corr>=.99,'median_relative_error_le_0_05':mare<=.05,'zero_correspondence':len(zero)==2395 and not exceptions,'contagion_always_clipped_at_floor':set(clipped)=={.5} and all(r<.5 for r in ratios),'operating_point_ratio_between_0_5_and_2':.5<=op_ratio<=2.0}
    result={'status':'PASS' if all(checks.values()) else 'HALTED','head':head,'input_csv_count':len(inputs),'input_record_count':sum(r['row_count'] for r in inputs),'steps_ge_10_count':len(rows_ge10),'filtered_count':len(records),'K':K,'K_repr':repr(K),'K_six_decimals':format(K,'.6f'),'ratio_mean':float(np.mean(q)),'ratio_standard_deviation_sample_ddof1':float(np.std(q,ddof=1)),'ratio_standard_deviation_population_ddof0':float(np.std(q)),'ratio_p05':float(np.quantile(q,.05,method='linear')),'ratio_p95':float(np.quantile(q,.95,method='linear')),'correlation_V_A_squared':corr,'median_absolute_relative_error':mare,'zero_variance_count':len(zero),'zero_variance_suppression_ge1_count':sum(r['total_suppression']>=1.0 for r in zero),'zero_correspondence_exceptions':exceptions,'contagion_record_count':len(ratios),'contagion_max_raw_ratio':max(ratios),'contagion_distinct_clipped_values':sorted(set(clipped)),'contagion_unclipped_count':sum(.5<=r<=2 for r in ratios),'median_avg_wb_steps_ge10':med_wb,'median_total_suppression_steps_ge10':med_S,'V_projected_at_marginal_medians':V_op,'operating_point_V_over_Vref':op_ratio,'checks':checks,'inputs':inputs,**metadata(np)}
    for r in records:
        r['V_over_A_squared']=r['V']/r['A']**2
        r['V_projected']=K*r['A']**2
        r['absolute_relative_error']=abs(r['V_projected']-r['V'])/r['V']
    csvfile('planner_d3_t1_filtered.csv',records)
    csvfile('planner_d3_t1_contagion.csv',contagion_rows)
    write('planner_d3_t1.json',result)
    state.update(K=K,K_frozen_utc=now(),T1_checks=checks,status='T1_PASSED' if all(checks.values()) else 'HALTED')
    write('planner_d3_state.json',state)
    print(json.dumps({k:v for k,v in result.items() if k not in ('inputs','modules','thread_runtime','thread_environment')},ensure_ascii=True),flush=True)
    if not all(checks.values()): raise RuntimeError('T1 measurement gate failed')

def suite(phase):
    import numpy as np
    np.random.seed(20260908)
    stdout=io.StringIO();stderr=io.StringIO();code=0;started=time.perf_counter()
    with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
        try: runpy.run_path(str(ROOT/'simulation/test_refactor_1x.py'),run_name='__main__')
        except SystemExit as e: code=int(e.code or 0)
        except BaseException: code=2;traceback.print_exc()
    result={'phase':phase,'exit_code':code,'stdout':stdout.getvalue(),'stderr':stderr.getvalue(),'elapsed_seconds':time.perf_counter()-started,'initial_numpy_seed':20260908,**metadata(np)}
    write('planner_d3_'+phase+'_suite.json',result)
    textfile('planner_d3_'+phase+'_suite.txt',stdout.getvalue().replace('\u2014','-')+stderr.getvalue().replace('\u2014','-'))
    if VIOLATIONS or code: raise RuntimeError('Regression or write-guard failure: '+phase)
    print(json.dumps({'phase':phase,'exit_code':code,'stdout':stdout.getvalue(),'stderr':stderr.getvalue()},ensure_ascii=True),flush=True)

def grid():
    import numpy as np
    import metrics,agents
    from model import GardenModel
    from dataclasses import asdict,replace
    fixture=read('planner_d3_fixture.json')
    model=GardenModel(**fixture['model_constructor'])
    # Observe novelty from the one initialized, seeded population without stepping it.
    model.novelty_log=[agent.generate_novelty(model.constraint_level,fixture['network_contagion']) for agent in model.schedule]
    csvfile('planner_d3_fixed_novelty.csv',[{'agent_index':i,**{'axis_'+str(j):float(v) for j,v in enumerate(row)}} for i,row in enumerate(model.novelty_log)])
    fallback_before=metrics.H_N_SHAPE_FALLBACK_COUNT
    state=metrics._build_state_from_model(model)
    components=metrics.calculate_h_n(model.novelty_log,return_components=True)
    default=metrics.calculate_h_n(model.novelty_log)
    api={'default_equals_component_entropy':default==components[0],'shape_matches_state':components[1]==state.h_n_shape,'empty_default':metrics.calculate_h_n([]),'empty_components_flag':metrics.calculate_h_n([],return_components=True),'single_default':metrics.calculate_h_n([np.ones(10)]),'single_components_flag':metrics.calculate_h_n([np.ones(10)],return_components=True)}
    fixed={'state':asdict(state),'model_constructor':fixture['model_constructor'],'model_config_as_constructed':model.config,'fixed_allocation':fixture['allocation'],'candidate_seed':fixture['candidate_seed'],'novelty_generation_constraint':model.constraint_level,'novelty_generation_contagion':fixture['network_contagion'],'measured_h_n':components[0],'measured_shape':components[1],'measured_V':components[2],'fallback_before':fallback_before,'fallback_after_state':metrics.H_N_SHAPE_FALLBACK_COUNT,'api':api,'model_steps_run':0,**metadata(np)}
    write('planner_d3_fixed_state.json',fixed)
    if not api['default_equals_component_entropy'] or not api['shape_matches_state']: raise RuntimeError('Component API mismatch')
    if any(api[k]!=0.0 for k in ('empty_default','empty_components_flag','single_default','single_components_flag')): raise RuntimeError('Early-return API changed')
    if metrics.H_N_SHAPE_FALLBACK_COUNT: raise RuntimeError('Shape fallback activated')
    count=model.config['n_candidates_v2'];horizons=model.config['rollout_steps_v2']
    candidate_set=agents.generate_v2_candidates(n=count,rng=np.random.default_rng(fixture['candidate_seed']))
    constraint_grid=[agents._x_vector_to_action(fixture['allocation'],*agents._constraint_pair_for_index(i)) for i in range(36)]
    original=agents._project_diagnostic_state_step
    def bypass(state,candidate,config):
        return replace(original(state,candidate,config),h_n=state.h_n)
    def score(action):
        return agents.project_u_sys_v2_rollout(model.ai,model,action,rollout_steps=horizons,state_start=state)[0]
    negative=[]
    try:
        agents._project_diagnostic_state_step=bypass
        for i,action in enumerate(constraint_grid):
            negative.append({'grid_index':i,'c_protective':action['c_protective'],'c_suppressive':action['c_suppressive'],'total_suppression':agents.total_suppression(action),'score':score(action)})
    finally: agents._project_diagnostic_state_step=original
    negative_spread=max(r['score'] for r in negative)-min(r['score'] for r in negative)
    csvfile('planner_d3_negative_grid.csv',negative)
    write('planner_d3_negative_control.json',{'score_spread':negative_spread,'passed':negative_spread==0.0,'state_artifact':'planner_d3_fixed_state.json','bypass':'After the unmodified state update, replace h_n with the incoming state.h_n at every horizon. Applied only in the harness process.','utc':now()})
    if negative_spread!=0.0: raise RuntimeError('T3a negative-control spread is nonzero')
    positive=[];horizon_rows=[]
    for i,action in enumerate(constraint_grid):
        trajectory=[]
        def capture(incoming,candidate,config):
            projected=original(incoming,candidate,config)
            trajectory.append(projected)
            return projected
        try:
            agents._project_diagnostic_state_step=capture
            value=score(action)
        finally: agents._project_diagnostic_state_step=original
        S=agents.total_suppression(action)
        for horizon,projected in enumerate(trajectory,1):
            V=metrics.H_N_V_PROJ_K*(projected.avg_wb*(1.0-S))**2
            horizon_rows.append({'grid_index':i,'horizon':horizon,'total_suppression':S,'avg_wb':projected.avg_wb,'V_proj':V,'h_n':projected.h_n,'h_n_shape':projected.h_n_shape})
        first=trajectory[0]
        positive.append({'grid_index':i,'c_protective':action['c_protective'],'c_suppressive':action['c_suppressive'],'total_suppression':S,'V_proj':metrics.H_N_V_PROJ_K*(first.avg_wb*(1.0-S))**2,'h_n_horizon_1':first.h_n,'score':value})
    positive.sort(key=lambda r:(r['total_suppression'],r['c_protective'],r['c_suppressive']))
    csvfile('planner_d3_positive_grid.csv',positive)
    csvfile('planner_d3_grid_horizons.csv',horizon_rows)
    monotonic=all(a['score']>b['score'] for a,b in zip(positive,positive[1:]) if a['total_suppression']<b['total_suppression'])
    groups={}
    for r in positive: groups.setdefault(r['total_suppression'],[]).append(r)
    ties=[{'total_suppression':S,'cells':rows,'score_difference':max(r['score'] for r in rows)-min(r['score'] for r in rows)} for S,rows in groups.items() if len(rows)>1]
    max_tie=max([r['score_difference'] for r in ties],default=0.0)
    endpoints=[r for r in positive if r['total_suppression']==1.0]
    saturation=bool(endpoints) and all(r['V_proj']==0.0 and r['h_n_horizon_1']==0.0 for r in endpoints)
    frozen_shape=all(r['h_n_shape']==state.h_n_shape for r in horizon_rows)
    partial={'strict_decrease_between_distinct_suppression_values':monotonic,'tie_groups':ties,'maximum_within_group_score_difference':max_tie,'saturation_endpoint_passed':saturation,'frozen_shape_all_horizons':frozen_shape,'utc':now()}
    write('planner_d3_positive_controls.json',partial)
    if not monotonic: raise RuntimeError('T3b score is not strictly decreasing with suppression')
    if max_tie!=0.0: raise RuntimeError('T3c tied suppression has different scores')
    if not saturation: raise RuntimeError('T3e saturation endpoint is not exactly zero')
    if not frozen_shape: raise RuntimeError('Shape changed across horizons')
    scores_off=[];scores_on=[]
    try:
        agents._project_diagnostic_state_step=bypass
        scores_off=[score(candidate) for candidate in candidate_set]
    finally: agents._project_diagnostic_state_step=original
    scores_on=[score(candidate) for candidate in candidate_set]
    candidate_rows=[{'candidate_index':i,**candidate,'total_suppression':agents.total_suppression(candidate),'score_projection_off':scores_off[i],'score_projection_on':scores_on[i]} for i,candidate in enumerate(candidate_set)]
    csvfile('planner_d3_standard_candidates.csv',candidate_rows)
    fallback=metrics.H_N_SHAPE_FALLBACK_COUNT
    result={'status':'PASS','negative_control_spread':negative_spread,'positive_grid_spread':max(r['score'] for r in positive)-min(r['score'] for r in positive),'standard_candidate_count':len(candidate_set),'standard_scores_on_std_population_ddof0':float(np.std(scores_on)),'standard_scores_on_std_sample_ddof1':float(np.std(scores_on,ddof=1)),'standard_scores_off_std_population_ddof0':float(np.std(scores_off)),'standard_scores_off_std_sample_ddof1':float(np.std(scores_off,ddof=1)),'argmax_total_suppression_off':agents.total_suppression(candidate_set[int(np.argmax(scores_off))]),'argmax_total_suppression_on':agents.total_suppression(candidate_set[int(np.argmax(scores_on))]),'fallback_count':fallback,'model_steps_run':0,'constraint_grid_count':len(positive),'distinct_suppression_count':len(groups),'rollout_steps':horizons,'frozen_state':asdict(state),**partial,**metadata(np)}
    write('planner_d3_t3.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('tie_groups','modules','thread_environment','thread_runtime','frozen_state')},ensure_ascii=True),flush=True)
    if fallback: raise RuntimeError('T3f shape fallback activated')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=['derive','suite-pre','suite-post','grid']);args=parser.parse_args()
    try:
        if args.operation=='derive': derive()
        elif args.operation=='grid': grid()
        else: suite(args.operation.split('-')[1])
    except BaseException as e:
        write('planner_d3_failure_'+args.operation+'.json',{'halt':str(e),'utc':now(),'violations':VIOLATIONS,'traceback':traceback.format_exc()})
        print('HALT: '+str(e),flush=True);raise SystemExit(2)
if __name__=='__main__': main()
