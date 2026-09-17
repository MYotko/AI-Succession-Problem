"""Record the specification conflict without running a model."""
import os,sys
sys.dont_write_bytecode=True
os.environ['PYTHONDONTWRITEBYTECODE']='1'
os.environ['GIT_OPTIONAL_LOCKS']='0'
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
P='vector_paired_run_a_'
NULL=Path(os.devnull).resolve()
def allowed(path):
    q=Path(path).resolve()
    return q==NULL or (q.parent==OUT and q.name.startswith(P))
def audit(event,args):
    if event=='open':
        path,mode,flags=args
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if writing and not isinstance(path,int) and not allowed(path):raise RuntimeError('WRITE SCOPE HALT: '+str(path))
    elif event=='os.rename':
        if not allowed(args[0]) or not allowed(args[1]):raise RuntimeError('WRITE SCOPE HALT: rename')
    elif event in ('os.mkdir','os.remove','os.rmdir','os.link','os.symlink'):raise RuntimeError('WRITE SCOPE HALT: '+event)
sys.addaudithook(audit)
import hashlib,json,csv,io,subprocess,time
from datetime import datetime,timezone
import numpy as np
def now():return datetime.now(timezone.utc).isoformat()
def lf(raw):return raw.replace(b'\r\n',b'\n')
def sha(raw):return hashlib.sha256(raw).hexdigest()
events=[]
def read_json(path):
    start=time.monotonic()
    while True:
        try:return json.loads(path.read_bytes())
        except PermissionError as error:
            if time.monotonic()-start>=5:raise
            events.append({'utc':now(),'operation':'JSON read','path':str(path),'error':str(error)})
            time.sleep(min(0.05,max(0,5-time.monotonic()+start)))
def git(*args):
    r=subprocess.run(['git',*args],cwd=ROOT,capture_output=True)
    if r.returncode:raise RuntimeError('Read-only Git failed: '+repr(args))
    return r.stdout
def save(name,value):
    raw=(json.dumps(value,indent=2,ensure_ascii=True)+'\n').encode('utf-8')
    with (OUT/(P+name)).open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
pre=read_json(OUT/(P+'preflight.json'))
head=git('rev-parse','HEAD').decode().strip()
readings=[]
for pin in pre['pins']:
    path=pin['path'];blob=git('cat-file','blob','HEAD:'+path);work=(ROOT/path).read_bytes()
    readings.append({**pin,'completion_blob_sha256_lf':sha(lf(blob)),
       'completion_worktree_sha256_lf':sha(lf(work)),
       'completion_blob_sha1':git('rev-parse','HEAD:'+path).decode().strip(),
       'matched':sha(lf(blob))==sha(lf(work))==pin['expected_sha256_lf']})
path='simulation/diagnostics/detector_design_note.md'
wanted='6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad'
blob=git('cat-file','blob','HEAD:'+path);work=(ROOT/path).read_bytes()
inherited={'path':path,'expected_sha256_lf':wanted,'blob_sha256_lf':sha(lf(blob)),
           'worktree_sha256_lf':sha(lf(work)),'blob_sha1':git('rev-parse','HEAD:'+path).decode().strip(),
           'matched':sha(lf(blob))==sha(lf(work))==wanted,
           'basis':'Section 3 inherited pin, read at halt before model execution'}
reason=("Specification conflict: the committed note Section 2 line 39 prohibits any function "
        "from computing or returning a ratio of two measured counts, while the dispatch requires "
        "unchanged run_single(task) and retention of every returned field. The pinned runner "
        "at line 435 computes and returns capture_rate as blocked / met if met else 0.0.")
workarounds=['Halt-recorder authoring had a tool-layer syntax error before any shell ran; removed nested backtick quoting and authored through a base64 shell command.']
additional=[]
if not all(r['matched'] for r in readings) or not inherited['matched']:additional.append('A source pin changed.')
if head!=pre['head']:additional.append('HEAD changed.')
halt={'status':'HALTED','reason':reason,'additional_findings':additional,
      'phase':'Specification reading after T0, before T1','t0_passed':True,
      'gate_model_steps':0,'evaluation_runs_launched':0,'evaluation_runs_completed':0,
      'registered_analysis_computed':False,'tool_layer_workarounds':workarounds,'utc':now()}
save('halt.json',halt)
save('results.json',{**halt,'P1':None,'P2':None,'P3':None,'P4':None,'planned_runs':240})
runtime={'machine':os.environ.get('COMPUTERNAME'),'head':head,'python':sys.version,'numpy':np.__version__,
         'operator_cpu_budget':16,'operating_mode':'normal','planned_worker_limit':15,'simulation_workers_used':0,
         'numerical_worker_threads_verified':False,'reason_threads_not_verified':'No worker launched',
         'resumed_seeds':[],'retry_events':events,'tool_layer_workarounds':workarounds}
modules={Path(__file__).relative_to(ROOT).as_posix():{
    'sha256_lf':sha(lf(Path(__file__).read_bytes())),'basis':'LF-normalized bytes','executed':True}}
for r in readings:
    if r['path'].endswith('.py'):
        modules[r['path']]={'sha256_lf':r['completion_worktree_sha256_lf'],
                           'basis':'LF-normalized working-tree bytes','executed':False}
warnings=[r['stderr'].strip() for r in pre['checks'] if r.get('stderr')]
fence=chr(96)*3
lines=['# Per-vector paired characterization, stage A: HALTED','',reason,'',
       'T0 passed all enumerated checks. T1 was not run. Zero of the planned 240 evaluation runs launched. No model was constructed or stepped. No paired value was computed.','',
       '## Registered quantities','',
       '| Quantity | Status |','| --- | --- |',
       '| P1 | Not computed |','| P2 | Not computed |','| P3 | Not computed |','| P4 | Not computed |','',
       '## Conflict evidence','',
       'Read from the committed blobs at '+pre['head']+'.','',
       'The pre-registration, Section 2, line 39, states:','',
       '> No function computes or returns a ratio of two measured counts. D5 and D6 are why.','',
       'The pinned runner reads the measured counters at lines 389-390 and builds the returned row with this expression at line 435:','',
       fence+'python',"'capture_rate': blocked / met if met else 0.0,",fence,'',
       'The dispatch requires calling run_single(task) unchanged and keeping every field it returns. Section 13 changes the arm design but does not exempt this ratio from Section 2. Neither the runner nor any recorded field was changed to resolve the conflict.','',
       'This is not a containment evaluation, not a defense rate, and reinstates no withdrawn figure. No ratio of two measured counts was computed in this halted attempt. The Section 10 interpretation is reserved for the operator.','',
       '## Provenance','',
       'Machine: '+str(runtime['machine'])+'. HEAD: '+head+'.',
       'Python: '+sys.version+'. NumPy: '+np.__version__+'.',
       'Simulation workers used: 0. Planned normal-mode limit: 15 from the operator budget of 16. No worker thread verification was applicable.',
       'Resumed seeds: none. JSON read retry events: '+str(len(events))+'.','',
       'Tool-layer workaround: '+workarounds[0],'',
       'The write guard permits only vector_paired_run_a_ files directly under simulation/diagnostics/ and os.devnull. The null-device exemption is present. Bytecode writes are disabled.','',
       '| Pinned file | Expected LF SHA256 | Start blob / worktree | Completion blob / worktree | Match |',
       '| --- | --- | --- | --- | --- |']
for r in readings:
    lines.append('| '+r['path']+' | '+r['expected_sha256_lf']+' | '+r['start_blob_sha256_lf']+' / '+r['start_worktree_sha256_lf']+' | '+r['completion_blob_sha256_lf']+' / '+r['completion_worktree_sha256_lf']+' | '+str(r['matched'])+' |')
lines+=['','The inherited detector-note pin also matched: '+wanted+'.',
        'The manifest records committed blob SHA1 values and module hashes, labeled by basis. No simulation module was executed.','',
        'T0 stderr warnings:','',fence+'text','\n'.join(warnings) if warnings else 'None.',fence,'',
        'Known CRLF/LF differences were preserved. No snapshot generator was invoked. No Git write operation was run.','',
        'The manifest hashes output files on LF-normalized bytes, counts CSV rows with csv.DictReader excluding headers, and excludes its own recursive self-hash.','']
if additional:lines+=['Additional halt findings: '+json.dumps(additional),'']
report='\n'.join(lines)
if chr(0x2014) in report:raise RuntimeError('Forbidden em dash')
with (OUT/(P+'report.md')).open('x',encoding='utf-8',newline='\n') as f:f.write(report);f.flush();os.fsync(f.fileno())
outputs=[]
for path in sorted(OUT.iterdir()):
    if path.is_file() and path.name.startswith(P) and path.name!=P+'manifest.json':
        raw=path.read_bytes()
        count=sum(1 for row in csv.DictReader(io.StringIO(raw.decode('utf-8')))) if path.suffix=='.csv' else None
        outputs.append({'path':path.relative_to(ROOT).as_posix(),'sha256_lf':sha(lf(raw)),'csv_rows':count})
save('manifest.json',{'status':'HALTED','halt':halt,'outputs':outputs,
      'source_pins_start_and_completion':readings,'inherited_source_pin':inherited,'runtime':runtime,
      'per_module_sha256':modules,'t0_stderr_warnings':warnings,'sha256_basis':'LF-normalized bytes',
      'csv_count_method':'csv.DictReader excluding header, null for non-CSV',
      'manifest_self':{'path':'simulation/diagnostics/'+P+'manifest.json','sha256_lf':None,'csv_rows':None,
                       'reason':'Recursive self-hash excluded'},'created_utc':now()})
print(json.dumps({'status':'HALTED','runs_launched':0,
      'pins_matched':all(r['matched'] for r in readings) and inherited['matched'],
      'report':P+'report.md','results':P+'results.json','manifest':P+'manifest.json'}))
