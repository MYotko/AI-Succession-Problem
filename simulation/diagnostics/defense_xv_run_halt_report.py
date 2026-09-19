"""Record the specification conflict without executing project code or models."""
import sys
sys.dont_write_bytecode=True
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
os.environ['GIT_OPTIONAL_LOCKS']='0'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'simulation/diagnostics'
P='defense_xv_run_'
NULL=Path(os.devnull).resolve()

def allowed(path):
    value=Path(path).resolve()
    return value==NULL or(value.parent==OUT and value.name.startswith(P))

def guard(event,args):
    if event=='open':
        path,mode,flags=args
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or(isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_APPEND|os.O_TRUNC))
        if writing and not isinstance(path,int) and not allowed(path):
            raise RuntimeError('Write outside scope: '+str(path))
    elif event=='os.rename':
        if not allowed(args[0]) or not allowed(args[1]):raise RuntimeError('Rename outside scope')
    elif event in ('os.remove','os.rmdir','os.mkdir','os.link','os.symlink'):
        raise RuntimeError('Unneeded filesystem mutation: '+event)
sys.addaudithook(guard)
import csv,hashlib,io,json,subprocess
from datetime import datetime,timezone
import numpy as np

def lf(data):return data.replace(b'\r\n',b'\n')
def sha(data):return hashlib.sha256(lf(data)).hexdigest()
def git(*args):
    result=subprocess.run(['git',*args],cwd=ROOT,capture_output=True)
    if result.returncode:raise RuntimeError('Read-only Git failed: '+repr(args))
    return result.stdout
def write(name,value):
    data=json.dumps(value,indent=2,ensure_ascii=True,allow_nan=False)+'\n'
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as handle:
        handle.write(data);handle.flush();os.fsync(handle.fileno())

preflight=json.loads((OUT/(P+'preflight.json')).read_text(encoding='utf-8'))
pins=[]
for pin in preflight['pins']:
    raw=git('cat-file','blob','HEAD:'+pin['path'])
    end=dict(pin,end_blob_sha256_lf=sha(raw),end_worktree_sha256_lf=sha((ROOT/pin['path']).read_bytes()))
    assert end['end_blob_sha256_lf']==end['end_worktree_sha256_lf']==pin['expected_sha256_lf'],pin['path']
    pins.append(end)
note_path='simulation/diagnostics/defense_cross_vector_design_note.md'
runner_path='simulation/run_attack_vector_revalidation_v2.py'
note=git('cat-file','blob','HEAD:'+note_path).decode('utf-8')
runner=git('cat-file','blob','HEAD:'+runner_path).decode('utf-8')
ratio_line=next(i for i,line in enumerate(runner.splitlines(),1) if "'capture_rate': blocked / met if met else 0.0" in line)
note_line=next(i for i,line in enumerate(note.splitlines(),1) if 'It corrects no published figure, and no ratio of two measured counts is computed.' in line)
reason=('Specification conflict: cross-vector note Section 2 prohibits computing any ratio of two measured counts, '
        'while Section 3 and the dispatch require the unmodified pinned runner run_single. That function computes '
        'capture_rate as blocked / met when met is nonzero, using yield_condition_blocked_count and '
        'yield_condition_met_count. The cross-vector note supplies no exception for that legacy computation.')
runtime={'machine':os.environ.get('COMPUTERNAME'),'head':preflight['head'],'python':sys.version,
         'numpy':np.__version__,'simulation_workers':0,'runs_launched':0,'planned_runs':720,
         'operator_cpu_budget':16,'bytecode_disabled':True,
         'numerical_threads_configured':1,'per_worker_thread_verifications':[],
         'module_hashes':{str(Path(__file__).relative_to(ROOT)).replace('\\','/'):
                          {'sha256_lf':sha(Path(__file__).read_bytes()),'basis':'LF-normalized working-tree bytes'}}}
halt={'status':'HALTED','phase':'Specification reconciliation after T0, before T1',
      'reason':reason,'T0':'PASSED','T1':'NOT RUN','runs_launched':0,'planned_runs':720,
      'cross_vector_gate_criterion':'NOT APPLIED','interpretation':'RESERVED FOR OPERATOR',
      'evidence':{'note_path':note_path,'note_section':2,'note_line':note_line,
                  'note_text':'It corrects no published figure, and no ratio of two measured counts is computed.',
                  'required_call':'run_single(task), unchanged','runner_path':runner_path,
                  'runner_line':ratio_line,'runner_expression':"'capture_rate': blocked / met if met else 0.0",
                  'numerator_source':'model.yield_condition_blocked_count',
                  'denominator_source':'model.yield_condition_met_count'},
      'utc':datetime.now(timezone.utc).isoformat(),'source_pins_start':preflight['pins'],
      'source_pins_end':pins,'runtime':runtime,'tool_layer_workarounds':preflight['tool_layer_workarounds']}
write(P+'halt.json',halt)
results={'status':'HALTED','halt_reason':reason,'runs_launched':0,'planned_runs':720,
         'X1':None,'X2':None,'X3':None,'X4':None,'X5':None,'X6':None,
         'registered_quantities_computed':False,'promotion_gate_criterion_applied':False,
         'interpretation_applied':False}
write(P+'results.json',results)
warnings=sorted(set(c['stderr'].strip() for c in preflight['checks'] if c['stderr']))
lines=['# Cross-vector evaluation: halted before T1','',
       'Status: HALTED. T0 passed. No T1 probe and no evaluation run was launched: 0 of 720 runs.',
       'The promotion gate criterion was not applied. No gate pass or failure decision is made.','',
       '## Halt reason','',reason,'',
       'Section 2 of the committed cross-vector note states:', '',
       '> It corrects no published figure, and no ratio of two measured counts is computed.','',
       'Section 3 and the dispatch require the pinned runner unchanged through run_single(task). At '+
       runner_path+':'+str(ratio_line)+', that function constructs the runner row with:',
       '',chr(96)*3+'python',"'capture_rate': blocked / met if met else 0.0,",chr(96)*3,'',
       'Here blocked is model.yield_condition_blocked_count and met is model.yield_condition_met_count. '
       'This is a source observation only. The function was not called. No exception was inferred from another pre-registration, '
       'and the required runner was not changed.','',
       '## Registered quantities','',
       '| Quantity | Status |','| --- | --- |',
       '| X1 | Not measured |','| X2 | Not measured |','| X3 | Not measured |',
       '| X4 | Not measured |','| X5 | Not measured |','| X6 | Not measured |','',
       'This dispatch is gate 1 of the promotion plan. It is intended to measure harm, not containment of these vectors. '
       'It is not a promotion decision and does not test input corruption. No ratio of two measured counts was computed. '
       'Applying the Section 6 criterion and the Section 7 interpretation is reserved for the operator.','',
       'Known-pathway qualification: the allocation channel was chosen knowing how the reallocation attack works. '
       'The channel constants were calibrated on the drift mapping construction. There are no headline measurement numbers '
       'or false-alarm counts in this halted attempt.','',
       '## Source pins','',
       '| Path | Start blob SHA256 LF | Start working-tree SHA256 LF | End blob SHA256 LF | End working-tree SHA256 LF |',
       '| --- | --- | --- | --- | --- |']
for pin in pins:
    lines.append('| '+' | '.join(pin[k] for k in ('path','start_blob_sha256_lf','start_worktree_sha256_lf','end_blob_sha256_lf','end_worktree_sha256_lf'))+' |')
lines+=['','## Execution provenance','',
        'Machine: '+str(runtime['machine'])+'. HEAD: '+preflight['head']+'.',
        'Python: '+sys.version+'. NumPy: '+np.__version__+'.',
        'Simulation workers: 0. Resumed seeds: none. Retry events: none.',
        'The known CRLF working-tree condition was not changed.','',
        'T0 stderr warnings: '+json.dumps(warnings)+'.','',
        'Tool-layer workaround: '+preflight['tool_layer_workarounds'][0],'']
report='\n'.join(lines)
assert chr(0x2014) not in report
with (OUT/(P+'report.md')).open('x',encoding='utf-8',newline='\n') as handle:
    handle.write(report);handle.flush();os.fsync(handle.fileno())
outputs=[]
for path in sorted(OUT.glob(P+'*')):
    if not path.is_file():continue
    data=path.read_bytes()
    rows=None
    if path.suffix=='.csv':rows=sum(1 for _ in csv.DictReader(io.StringIO(lf(data).decode('utf-8'))))
    outputs.append({'path':path.relative_to(ROOT).as_posix(),'sha256_lf':sha(data),'csv_rows':rows})
outputs.append({'path':'simulation/diagnostics/'+P+'manifest.json','sha256_lf':None,'csv_rows':None,
                'hash_note':'The manifest self-entry is excluded from recursive hashing; every other output is hashed.'})
manifest={'status':'HALTED','halt_reason':reason,'head':preflight['head'],'runtime':runtime,
          'hash_basis':'LF-normalized bytes','outputs':outputs,
          'committed_evidence':[{'path':p['path'],'commit':preflight['head'],'blob_sha1':p['blob_sha1'],
                                 'sha256_lf':p['start_blob_sha256_lf']} for p in preflight['pins']],
          'source_pins_start':preflight['pins'],'source_pins_end':pins,
          'worker_counts':{'launched':0,'completed':0,'planned_runs':720},
          'resumed_seeds':[],'retry_events':[],'tool_layer_workarounds':preflight['tool_layer_workarounds'],
          'T0_stderr_warnings':warnings,'promotion_gate_criterion_applied':False,'interpretation_applied':False}
write(P+'manifest.json',manifest)
print(json.dumps({'status':'HALTED','phase':'before T1','runs_launched':0,'reason':reason,
                  'report':P+'report.md','results':P+'results.json','manifest':P+'manifest.json'}))
