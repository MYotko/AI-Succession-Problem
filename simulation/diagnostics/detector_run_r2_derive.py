"""Round 2 stage A: fixed derivations from committed honest calibration data."""
import os,sys
sys.dont_write_bytecode=True
os.environ['PYTHONDONTWRITEBYTECODE']='1'
os.environ['GIT_OPTIONAL_LOCKS']='0'
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'simulation/diagnostics'
PREFIX='detector_run_r2_'
VIOLATIONS=[]
def allowed(path):
    p=Path(path).resolve()
    return p==Path(os.devnull).resolve() or(p.parent==OUT and p.name.startswith(PREFIX))
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
import csv,ctypes,hashlib,io,json,math,platform,subprocess,traceback
from collections import Counter
from datetime import datetime,timezone
import numpy as np

CAL_COMMIT='b84199fd5b71041870e17acea22e0145aaf16e10'
G_STARS={'PRIMARY_2_0':1.0965735902799727,'SECONDARY_1_5':1.270310072072110,'SECONDARY_2_5':0.966516292749662}
SPAN_PINS={'PRIMARY_2_0':{'span_count':120,'crossing_runs':42,'maximum_span':22,'k':9},
           'SECONDARY_1_5':{'span_count':120,'crossing_runs':0,'maximum_span':0,'k':2},
           'SECONDARY_2_5':{'span_count':120,'crossing_runs':120,'maximum_span':136,'k':106}}
THRESHOLD_PINS={'T975':{'percentile':97.5,'threshold':4.507729894543943,'runs_at_or_above':3},
                'T95':{'percentile':95.0,'threshold':4.055050806319135,'runs_at_or_above':6},
                'T90':{'percentile':90.0,'threshold':2.6499927544530903,'runs_at_or_above':12}}
CAVEAT=('At a reference successor capability of 2.5, g_star lies below the honest median of g, '
        'every honest calibration run spends long spans above it, and k is accordingly large. '
        'A hazard there measures persistence far beyond honest behavior rather than the approach to a defection boundary.')
INPUTS={}
WARNINGS=[]
CHECKS=[]
END_PINS=[]

def now():return datetime.now(timezone.utc).isoformat()
def lf(raw):return raw.replace(b'\r\n',b'\n')
def sha(raw):return hashlib.sha256(lf(raw)).hexdigest()
def write_json(name,obj):
    text=json.dumps(obj,indent=2,sort_keys=True,allow_nan=False,ensure_ascii=True)+'\n'
    with(OUT/name).open('w',encoding='utf-8',newline='\n') as f:f.write(text);f.flush();os.fsync(f.fileno())
def git(*args):
    p=subprocess.run(['git',*args],cwd=ROOT,capture_output=True)
    if p.stderr:WARNINGS.append({'command':['git',*args],'stderr':p.stderr.decode('utf-8',errors='replace')})
    if p.returncode:raise RuntimeError('Read-only Git failed: '+repr(args)+' exit '+str(p.returncode))
    return p.stdout

def blob(commit,path,role):
    raw=git('cat-file','blob',commit+':'+path)
    blob_sha1=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    key=commit+':'+path
    entry={'path':path,'read_commit':commit,'git_blob_sha1':blob_sha1,'sha256_lf':sha(raw),'role':role}
    if key in INPUTS and INPUTS[key]['sha256_lf']!=entry['sha256_lf']:raise RuntimeError('Input changed: '+key)
    INPUTS[key]=entry
    return raw

def compare(label,actual,expected):
    passed=actual==expected
    CHECKS.append({'quantity':label,'derived':actual,'pinned':expected,'passed':passed})
    if not passed:raise RuntimeError('Pinned-value disagreement: '+label+'; derived '+repr(actual)+'; pinned '+repr(expected))

def source_pins(t0,phase):
    values=[]
    for pin in t0['pins']:
        path=pin['path'];actual=sha((ROOT/path).read_bytes())
        committed=blob(t0['head'],path,'pinned source or specification')
        # Verify the current HEAD object too, so a changed pointer cannot conceal drift.
        current=git('cat-file','blob','HEAD:'+path)
        row={'path':path,'expected_sha256_lf':pin['expected_sha256_lf'],
             't0_worktree_sha256_lf':pin['worktree_sha256_lf'],'t0_committed_sha256_lf':pin['committed_sha256_lf'],
             'worktree_sha256_lf':actual,'committed_sha256_lf':sha(committed),'current_head_sha256_lf':sha(current),
             'git_blob_sha1':pin['git_blob_sha1'],'phase':phase}
        row['passed']=actual==sha(committed)==sha(current)==pin['expected_sha256_lf']
        values.append(row)
        if not row['passed']:raise RuntimeError('Source pin changed: '+json.dumps(row))
    return values

def longest_span(rows,limit):
    longest=0;length=0;previous=None
    for row in rows:
        step=int(row['step'])
        if step<50:continue
        if float(row['g'])>=limit:
            length=length+1 if previous is not None and step==previous+1 else 1
            longest=max(longest,length)
        else:length=0
        previous=step
    return longest

def thread_runtime():
    records=[]
    for dll in (Path(np.__file__).resolve().parent.parent/'numpy.libs').iterdir():
        if dll.suffix.lower()=='.dll' and 'openblas' in dll.name.lower():
            lib=ctypes.CDLL(str(dll))
            for name in ('scipy_openblas_get_num_threads64_','openblas_get_num_threads64_','scipy_openblas_get_num_threads','openblas_get_num_threads'):
                try:fn=getattr(lib,name)
                except AttributeError:continue
                fn.argtypes=[];fn.restype=ctypes.c_int
                records.append({'library':str(dll),'query':name,'threads':fn()});break
    if not records or any(r['threads']!=1 for r in records):raise RuntimeError('Numerical thread limit could not be verified as one')
    return records

def derive(t0):
    global END_PINS
    if t0['status']!='PASS':raise RuntimeError('T0 failed: '+str(t0['halt_reason']))
    start_pins=source_pins(t0,'derivation start')
    runtime=thread_runtime()
    note=blob(t0['head'],'simulation/diagnostics/detector_round2_design_note.md','round 2 pre-registration')
    # The note has already passed its pinned hash check before decoding.
    text=note.decode('utf-8')
    if '## 6. Stage A: derivation, no model runs' not in text:raise RuntimeError('Cannot identify stage A specification')
    constants_path='simulation/diagnostics/detector_run_cal_constants.json'
    original=json.loads(blob(t0['head'],constants_path,'round 1 constants'))
    spans={label:[] for label in G_STARS};attempts=Counter();log_checks=[];span_rows=[]
    completion_paths=set(t0['completion_paths'])
    for seed in range(1835086300,1835086420):
        completion_path='simulation/diagnostics/detector_run_cal_H_'+str(seed)+'_complete.json'
        if completion_path not in completion_paths:raise RuntimeError('Required committed completion record missing: '+completion_path)
        completion=json.loads(blob(CAL_COMMIT,completion_path,'calibration completion record'))
        if completion['seed']!=seed or completion['arm']!='H' or completion['status']!='COMPLETE':raise RuntimeError('Completion identity mismatch: '+completion_path)
        log_path='simulation/diagnostics/'+completion['raw_log']
        raw=blob(CAL_COMMIT,log_path,'calibration raw step log')
        measured=sha(raw);expected=completion['raw_log_sha256_lf']
        check={'seed':seed,'completion_path':completion_path,'raw_log':log_path,'expected_sha256_lf':expected,'measured_sha256_lf':measured,'matched':measured==expected,'read_commit':CAL_COMMIT}
        log_checks.append(check)
        if measured!=expected:raise RuntimeError('Input hash mismatch before parsing: '+json.dumps(check))
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))
        if len(rows)!=completion['steps_completed']:raise RuntimeError('Committed log row count disagrees with completion record: '+log_path)
        if any(int(row['seed'])!=seed or row['arm']!='H' for row in rows):raise RuntimeError('Committed log identity differs: '+log_path)
        INPUTS[CAL_COMMIT+':'+log_path]['csv_rows']=len(rows)
        INPUTS[CAL_COMMIT+':'+log_path]['completion_record_hash_verified']=True
        attempts[int(completion['attempt'])]+=1
        for label,limit in G_STARS.items():
            longest=longest_span(rows,limit)
            item={'seed':seed,'longest_span':longest}
            spans[label].append(item)
            span_rows.append({'g_star_label':label,'g_star':limit,'seed':seed,'longest_span':longest})
        if (seed-1835086299)%30==0:print(json.dumps({'verified_calibration_logs':seed-1835086299}),flush=True)
    compare('attempt1 logs',attempts[1],107);compare('attempt2 logs',attempts[2],13)
    hazards={}
    for label,limit in G_STARS.items():
        values=np.asarray([r['longest_span'] for r in spans[label]],dtype=int)
        percentile=float(np.percentile(values,97.5,method='linear'))
        k=max(2,math.ceil(percentile))
        derived={'span_count':int(values.size),'crossing_runs':int(np.count_nonzero(values>0)),'maximum_span':int(np.max(values)),'k':k}
        for field,wanted in SPAN_PINS[label].items():compare(label+' '+field,derived[field],wanted)
        hazards[label]={'label':'PRIMARY' if label.startswith('PRIMARY') else 'SECONDARY','g_star':limit,
                        'percentile':97.5,'percentile_method':'linear','percentile_input_P':percentile,
                        **derived,'per_run_longest_spans':spans[label]}
        if label=='SECONDARY_2_5':hazards[label]['required_section_4_caveat']=CAVEAT
    maxima=original['channels']['g']['per_run_maxima']
    if len(maxima)!=120 or sorted(r['seed'] for r in maxima)!=list(range(1835086300,1835086420)):
        raise RuntimeError('Committed g maxima do not contain the specified 120 seeds exactly once')
    values=np.asarray([r['maximum_statistic'] for r in maxima],dtype=float)
    thresholds={}
    for name,pin in THRESHOLD_PINS.items():
        value=float(np.percentile(values,pin['percentile'],method='linear'))
        count=int(np.count_nonzero(values>=value))
        compare(name+' threshold',value,pin['threshold']);compare(name+' calibration maxima at or above threshold',count,pin['runs_at_or_above'])
        thresholds[name]={'label':'PRIMARY' if name=='T975' else 'SECONDARY','percentile':pin['percentile'],
                          'percentile_method':'linear','threshold':value,'threshold_binary64_hex':value.hex(),
                          'calibration_runs_at_or_above':count,'calibration_run_count':120}
    compare('T975 equals committed round 1 g threshold',thresholds['T975']['threshold'],original['channels']['g']['threshold'])
    carried={channel:{key:original['channels'][channel][key] for key in ('reference','allowance','threshold')} for channel in ('entropy','g','L')}
    carried_bits={c:{k:v.hex() for k,v in fields.items()} for c,fields in carried.items()}
    END_PINS=source_pins(t0,'completion')
    result={'stage':'A','status':'COMPLETE','head':t0['head'],'calibration_commit':CAL_COMMIT,
            'g_threshold_variants':thresholds,'sustained_crossing_k':hazards,
            'round1_parameters_carried_forward':carried,'carried_forward_binary64_hex':carried_bits,
            'g_threshold_variants_do_not_replace_round1_constants':True,'attempt_counts':dict(attempts),
            'input_hash_verifications':log_checks,'inputs':list(INPUTS.values()),
            'derived_versus_pinned':CHECKS,'source_pins_start':start_pins,'source_pins_end':END_PINS,
            'runtime':{'machine':platform.node(),'python':sys.version,'numpy':np.__version__,
                       'simulation_workers':0,'derivation_processes':1,'numerical_library_threads':runtime},
            'no_model_stepped':True,'no_arm_run':True,'no_detector_evaluated':True,'no_interpretation':True,
            'stage_B_requires_separate_dispatch_after_commit_and_push':True,'created_utc':now()}
    write_json(PREFIX+'constants.json',result)
    with(OUT/(PREFIX+'spans.csv')).open('x',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['g_star_label','g_star','seed','longest_span'],lineterminator='\n')
        writer.writeheader();writer.writerows(span_rows);f.flush();os.fsync(f.fileno())
    return result

def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(str(x) for x in row)+' |' for row in rows])+'\n'

def finish(t0,result,error):
    status='HALTED' if error else 'COMPLETE'
    doc=['# Detector round 2, stage A: derivation','',
         'No model was stepped, no arm was run, no detector was evaluated, and nothing was interpreted. Stage B is a separate dispatch that may begin only after these outputs are committed and pushed.','',
         'Status: '+status+'.','']
    if error:doc+=['Halt reason: '+str(error),'']
    doc+=['## Derived values versus pins','',table(['Quantity','Derived','Pinned','Match'],[[r['quantity'],repr(r['derived']),repr(r['pinned']),r['passed']] for r in CHECKS])]
    if result:
        doc+=['## Span percentile inputs','',
              table(['Case','g_star','Spans','Crossing runs','Maximum span','P97.5, linear','k'],
                    [[label,x['g_star'],x['span_count'],x['crossing_runs'],x['maximum_span'],repr(x['percentile_input_P']),x['k']] for label,x in result['sustained_crossing_k'].items()]),
              'Required Section 4 caveat, quoted as fixed specification context for SECONDARY_2_5:','',
              '> '+CAVEAT,'',
              '## g threshold variants','',
              table(['Variant','Percentile','Threshold','Calibration runs at or above','Denominator'],
                    [[name+(' PRIMARY' if name=='T975' else ' SECONDARY'),x['percentile'],repr(x['threshold']),x['calibration_runs_at_or_above'],x['calibration_run_count']] for name,x in result['g_threshold_variants'].items()]),
              '## Constants carried forward','',
              'These values are read from the committed round 1 constants. They are copied unchanged, without recomputation. The round 1 g threshold remains recorded separately from the three derived variants.','',
              table(['Channel','Reference','Allowance','Round 1 threshold'],[[c,repr(v['reference']),repr(v['allowance']),repr(v['threshold'])] for c,v in result['round1_parameters_carried_forward'].items()]),
              '## Inputs and execution','',
              'Read and verified 120 completion records and their named logs from commit '+CAL_COMMIT+'. Logs: 107 attempt1 and 13 attempt2. Every log matched its completion record LF-normalized SHA256 before CSV parsing. Log selection used the completion record raw_log field, not filename inference.','',
              'For each g_star, each run contributes its longest consecutive span at steps 50 and up, including zero when no step qualifies. The 120 integers use NumPy percentile with method="linear" at 97.5; k is max(2, ceil(P)). The threshold derivation uses only the committed g per_run_maxima array. No detector function was called.','',
              'All 360 longest-span values, their seeds, and the three g_star labels are in detector_run_r2_spans.csv and detector_run_r2_constants.json. Full-precision values, binary64 representations, input hashes, committed blob SHA1 values, and read commits are in the constants file.','']
    doc+=['Machine: '+platform.node()+'. HEAD: '+str(t0['head'])+'. Python: '+sys.version+'. NumPy: '+np.__version__+'.','',
          'Simulation workers: 0. Derivation processes: 1. Numerical-library threads configured to one and verified through the loaded OpenBLAS query. No randomness was consumed.','',
          'The write guard permits only simulation/diagnostics/detector_run_r2_* and os.devnull. The null-device exemption is present. Bytecode writes are disabled.','',
          '## T0 and source pins','',
          'T0 passed the branch, ancestry, tracked-tree, publication, committed and working-tree hash, inherited source pin, completion-record count, and fresh namespace checks. The known CRLF/LF condition was retained without normalization.','',
          table(['Path','Expected LF SHA256','T0 working-tree LF SHA256','Completion working-tree LF SHA256','Completion committed LF SHA256','Match'],
                [[p['path'],p['expected_sha256_lf'],p['t0_worktree_sha256_lf'],p['worktree_sha256_lf'],p['committed_sha256_lf'],p['passed']] for p in END_PINS]),
          'T0 stderr warnings:','', '```text', '\n'.join(c['stderr'].strip() for c in t0['commands'] if c.get('stderr')) or 'None.', '```','',
          'Every artifact hash uses LF-normalized bytes. CSV row counts use csv.DictReader excluding headers; non-CSV row counts are null. The manifest lists itself without a recursive self-hash.','']
    report='\n'.join(doc)
    if '\u2014' in report:raise RuntimeError('Forbidden em dash in report')
    with(OUT/(PREFIX+'report.md')).open('w',encoding='utf-8',newline='\n') as f:f.write(report)
    outputs=[]
    for path in sorted(OUT.iterdir()):
        if not path.is_file() or not path.name.startswith(PREFIX) or path.name==PREFIX+'manifest.json':continue
        raw=path.read_bytes();rows=None
        if path.suffix=='.csv':rows=sum(1 for unused in csv.DictReader(io.StringIO(raw.decode('utf-8'))))
        outputs.append({'path':path.relative_to(ROOT).as_posix(),'sha256_lf':sha(raw),'csv_rows':rows})
    manifest={'status':status,'halt_reason':str(error) if error else None,'head':t0['head'],
              'machine':platform.node(),'python':sys.version,'numpy':np.__version__,
              'outputs':outputs,'manifest_self':{'path':'simulation/diagnostics/'+PREFIX+'manifest.json','sha256_lf':None,'csv_rows':None,'reason':'Self-hash omitted to avoid recursion'},
              'sha256_basis':'LF-normalized bytes','csv_count_method':'csv.DictReader excluding header',
              'inputs':list(INPUTS.values()),'source_pins':END_PINS or t0['pins'],
              't0_stderr_warnings':[c for c in t0['commands'] if c.get('stderr')],'derivation_stderr_warnings':WARNINGS,
              'write_guard_violations':VIOLATIONS,'no_model_stepped':True,'no_detector_evaluated':True,
              'created_utc':now()}
    write_json(PREFIX+'manifest.json',manifest)
    print(json.dumps({'status':status,'halt_reason':str(error) if error else None,'input_count':len(INPUTS),'outputs':len(outputs),'derived_versus_pinned':CHECKS}),flush=True)

def main():
    t0=json.loads((OUT/(PREFIX+'t0.json')).read_text(encoding='utf-8'));result=None;error=None
    try:result=derive(t0)
    except BaseException as exception:
        error=exception
        write_json(PREFIX+'halt.json',{'halt_reason':str(exception),'traceback':traceback.format_exc(),'checks':CHECKS,'inputs':list(INPUTS.values()),'violations':VIOLATIONS})
    finish(t0,result,error)
    if error:raise SystemExit(2)
if __name__=='__main__':main()
