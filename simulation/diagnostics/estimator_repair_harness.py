"""Component validation for the bounded entropy-estimator edit."""
import sys
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8')
import os
THREAD_ENV=['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']
for key in THREAD_ENV:os.environ[key]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
METRICS=ROOT/'simulation/metrics.py'
NULL=Path(os.devnull).resolve()
VIOLATIONS=[]
def allowed(path):
    p=Path(path).resolve()
    return p in (METRICS,NULL) or (p.parent==OUT and p.name.startswith('estimator_repair_'))
def audit(event,args):
    bad=None
    if event=='open':
        path,mode,flags=args
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_APPEND|os.O_CREAT|os.O_TRUNC))
        if writing and not isinstance(path,int) and not allowed(path):bad='writable open: '+str(path)
    elif event=='os.rename':
        if not allowed(args[0]) or not allowed(args[1]):bad='rename outside scope'
    elif event in ('os.remove','os.rmdir','os.mkdir','os.link','os.symlink'):bad=event
    if bad:
        VIOLATIONS.append(bad)
        raise RuntimeError('WRITE SCOPE HALT: '+bad)
sys.addaudithook(audit)
sys.path.insert(0,str(ROOT/'simulation'))
import argparse,contextlib,csv,ctypes,hashlib,inspect,io,json,math,runpy,time,traceback
from datetime import datetime,timezone

def now():return datetime.now(timezone.utc).isoformat()
def lf(raw):return raw.replace(b'\r\n',b'\n')
def digest(raw):return hashlib.sha256(raw).hexdigest()
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def write(name,obj):
    with (OUT/name).open('w',encoding='utf-8',newline='\n') as f:
        json.dump(obj,f,indent=2,sort_keys=True,ensure_ascii=True,allow_nan=False)
        f.write('\n');f.flush();os.fsync(f.fileno())
def textfile(name,text):
    if '\u2014' in text:raise RuntimeError('Em dash in authored artifact')
    with (OUT/name).open('w',encoding='utf-8',newline='\n') as f:f.write(text)
def csvfile(name,rows):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def sources():
    result={}
    for mod in list(sys.modules.values()):
        filename=getattr(mod,'__file__',None)
        if filename:
            path=Path(filename).resolve()
            if path.suffix=='.py' and path.is_relative_to(ROOT/'simulation'):
                raw=path.read_bytes()
                result[path.relative_to(ROOT).as_posix()]={'sha256_lf':digest(lf(raw)),'sha256_raw':digest(raw)}
    return result

def runtime(np):
    records=[]
    for dll in (Path(np.__file__).resolve().parent.parent/'numpy.libs').iterdir():
        if dll.suffix.lower()=='.dll' and 'openblas' in dll.name.lower():
            lib=ctypes.CDLL(str(dll))
            for name in ['scipy_openblas_get_num_threads64_','openblas_get_num_threads64_','scipy_openblas_get_num_threads','openblas_get_num_threads']:
                try:fn=getattr(lib,name)
                except AttributeError:continue
                fn.argtypes=[];fn.restype=ctypes.c_int
                records.append({'library':str(dll),'query':name,'effective_threads':fn()})
    if not records or any(r['effective_threads']!=1 for r in records):raise RuntimeError('Numerical thread limit not verified')
    return records

def fixture(np,state):
    raw=np.random.default_rng(state['fixture']['seed']).normal(size=(200,10))
    centered=raw-raw.mean(axis=0)
    V=float(np.trace(np.cov(centered,rowvar=False)))
    scaled=centered*math.sqrt(state['V_ref']/V)
    reduced=raw.copy();reduced[:,5:]=0.0
    return scaled,{'unit_variance':raw,'axis_permuted':raw[:,::-1].copy(),'rank_reduced':reduced}

def variance(np,X):
    centered=X-X.mean(axis=0)
    return float(np.trace(np.cov(centered,rowvar=False)))

def metadata(np):
    return {'utc':now(),'machine':os.environ['COMPUTERNAME'],'python':sys.version,'numpy':np.__version__,
            'thread_environment':{k:os.environ[k] for k in THREAD_ENV},'thread_runtime':runtime(np),'modules':sources()}

def measure(phase):
    state=read('estimator_repair_state.json')
    if phase=='pre' and digest(METRICS.read_bytes())!=state['metrics_pre_raw_sha256']:raise RuntimeError('Pinned estimator changed before T1')
    import numpy as np
    import metrics
    scaled,preservation=fixture(np,state)
    rows=[]
    for a in [1.0,.8,.5,.1,.001,0.0]:
        X=scaled*a;V=variance(np,X)
        h=float(metrics.calculate_h_n(list(X),composite_method='spectral'))
        row={'amplitude_factor':a,'V':V,'H_N':h,'H_N_15_decimals':f'{h:.15f}'}
        if phase=='post':row['magnitude']=float(-np.expm1(-metrics.H_N_MAGNITUDE_SAT_K*max(0.0,V)/metrics.H_N_V_REF))
        rows.append(row)
    control=all(rows[i]['H_N']>rows[i+1]['H_N'] for i in range(4)) and rows[-1]['H_N']==0.0
    preserve=[]
    for label,X in preservation.items():
        V=variance(np,X);value=float(metrics.calculate_h_n(list(X),composite_method='spectral'))
        r={'matrix':label,'V':V,'H_N':value}
        if phase=='post':
            magnitude=float(-np.expm1(-metrics.H_N_MAGNITUDE_SAT_K*max(0.0,V)/metrics.H_N_V_REF))
            r.update(magnitude=magnitude,recovered_shape=value/magnitude)
        preserve.append(r)
    result={'phase':phase,'amplitudes':rows,'preservation':preserve,'positive_control_passed':control,
            'base_covariance_trace':variance(np,scaled),'fixture':state['fixture'],'metrics_raw_sha256':digest(METRICS.read_bytes()),
            'metrics_lf_sha256':digest(lf(METRICS.read_bytes())),**metadata(np)}
    csvfile('estimator_repair_'+phase+'_amplitudes.csv',rows)
    csvfile('estimator_repair_'+phase+'_preservation.csv',preserve)
    if phase=='pre':
        spread=max(r['H_N'] for r in rows[:-1])-min(r['H_N'] for r in rows[:-1])
        result['nonzero_scale_spread']=spread;result['equal_to_15_digit_tolerance']=spread<=1e-15
        result['zero_factor_exactly_one']=rows[-1]['H_N']==1.0
        write('estimator_repair_pre.json',result)
        if control:raise RuntimeError('Positive control did not fail on unmodified estimator')
        if spread>1e-15 or rows[-1]['H_N']!=1.0:raise RuntimeError('Unmodified scale-invariance reproduction anomaly')
    else:
        pre=read('estimator_repair_pre.json')
        deviations=[abs(r['recovered_shape']-b['H_N']) for r,b in zip(preserve,pre['preservation'])]
        at_pin=float(-np.expm1(-metrics.H_N_MAGNITUDE_SAT_K*metrics.H_N_V_REF/metrics.H_N_V_REF))
        result.update(calibration={'V_exactly_equal_to_V_ref':metrics.H_N_V_REF,'measured_magnitude':at_pin,'expected':0.9502129316321361,
                                  'prior_report_median_factor':state['read_median_factor'],'expected_interpolation_difference':at_pin-float(state['read_median_factor'])},
                      largest_absolute_shape_deviation=max(deviations),shape_deviations=deviations,
                      axis_permutation_deviation=abs(preserve[0]['recovered_shape']-preserve[1]['recovered_shape']),
                      rank_reduction_detected=preserve[2]['recovered_shape']<preserve[0]['recovered_shape'],saturation_magnitude=preserve[0]['magnitude'])
        fn_source=inspect.getsource(metrics.calculate_system_metrics_v2)
        if 'h_n = max(H_N_FLOOR, float(state.h_n))' not in fn_source:raise RuntimeError('Consumption floor missing')
        from constants_v2_stage18 import H_N_FLOOR
        floor_result=max(H_N_FLOOR,0.0);denominator=floor_result+1e-6
        result['consumption_floor_assertion']={'returned_entropy':0.0,'read_H_N_FLOOR':H_N_FLOOR,'floored_entropy':floor_result,
                                             'default_epsilon':1e-6,'denominator':denominator,'finite_default_weight':5.0/denominator,'function_source_contains_floor':True}
        result['early_returns']={'empty':metrics.calculate_h_n([]),'single_agent':metrics.calculate_h_n([np.ones(10)])}
        result['modules']=sources()
        write('estimator_repair_post.json',result)
        if not control:raise RuntimeError('Repaired positive control failed')
        if at_pin!=0.9502129316321361:raise RuntimeError('Calibration pin mismatch')
        if max(deviations)>1e-12 or result['axis_permutation_deviation']>1e-12 or not result['rank_reduction_detected']:raise RuntimeError('Shape preservation failed')
        if result['saturation_magnitude']!=1.0:raise RuntimeError('Unit-variance saturation failed')
        if floor_result<=0 or not math.isfinite(5.0/denominator):raise RuntimeError('Consumption floor assertion failed')
        if any(x!=0.0 for x in result['early_returns'].values()):raise RuntimeError('Early return changed')
    if VIOLATIONS:raise RuntimeError('WRITE SCOPE HALT: '+repr(VIOLATIONS))
    print(json.dumps({'phase':phase,'positive_control_passed':control,'amplitudes':rows,'preservation':preserve,
                      'largest_absolute_shape_deviation':result.get('largest_absolute_shape_deviation')}),flush=True)

def suite(phase):
    import numpy as np
    np.random.seed(20260908)
    stdout=io.StringIO();stderr=io.StringIO();code=0;started=time.perf_counter()
    with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
        try:runpy.run_path(str(ROOT/'simulation/test_refactor_1x.py'),run_name='__main__')
        except SystemExit as e:code=int(e.code or 0)
        except BaseException:code=2;traceback.print_exc()
    result={'phase':phase,'exit_code':code,'stdout':stdout.getvalue(),'stderr':stderr.getvalue(),'elapsed_seconds':time.perf_counter()-started,
            'initial_numpy_seed':20260908,'test_path':'simulation/test_refactor_1x.py',**metadata(np)}
    write('estimator_repair_'+phase+'_suite.json',result)
    textfile('estimator_repair_'+phase+'_suite.txt',stdout.getvalue().replace('\u2014','-')+stderr.getvalue().replace('\u2014','-'))
    if VIOLATIONS:raise RuntimeError('WRITE SCOPE HALT: '+repr(VIOLATIONS))
    if code!=0:raise RuntimeError('test_refactor_1x.py failed '+phase+' edit')
    print(json.dumps({'phase':phase,'suite_exit_code':code,'output':stdout.getvalue(),'elapsed_seconds':result['elapsed_seconds']}),flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=['pre','post','suite-pre','suite-post']);args=parser.parse_args()
    try:
        if args.operation in ('pre','post'):measure(args.operation)
        else:suite(args.operation.split('-')[1])
    except BaseException as e:
        write('estimator_repair_failure_'+args.operation+'.json',{'halt':str(e),'utc':now(),'violations':VIOLATIONS,'traceback':traceback.format_exc()})
        print('HALT: '+str(e),flush=True);raise SystemExit(2)
if __name__=='__main__':main()
