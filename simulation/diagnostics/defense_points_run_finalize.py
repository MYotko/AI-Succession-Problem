import sys,os
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path.cwd().resolve()
OUT=ROOT/'simulation'/'diagnostics'
PREFIX='defense_points_run_'
def allowed(path):
    if isinstance(path,int):return True
    value=os.fspath(path)
    if os.path.normcase(value)==os.path.normcase(os.devnull):return True
    resolved=Path(value).resolve()
    return resolved.parent==OUT and resolved.name.startswith(PREFIX)
def require(path):
    if not allowed(path):raise PermissionError('write outside authorized prefix: '+str(path))
def guard(event,args):
    if event=='open':
        path,mode,flags=args
        if (isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):
            require(path)
    elif event in ('os.rename','os.replace'):
        require(args[0]);require(args[1])
    elif event in ('os.remove','os.rmdir','os.mkdir','os.chmod','os.utime','os.truncate'):
        require(args[0])
    elif event in ('os.link','os.symlink'):
        raise PermissionError('links not authorized')
sys.addaudithook(guard)

import json,hashlib,subprocess,platform,datetime,csv,io,time,importlib.metadata
os.environ['GIT_OPTIONAL_LOCKS']='0'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(raw):return hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()
retry_events=[]
def read_json(path):
    start=time.monotonic();count=0
    while True:
        try:return json.loads(path.read_text(encoding='utf-8'))
        except PermissionError as exc:
            count+=1
            elapsed=time.monotonic()-start
            event={'utc':now(),'operation':'JSON read','path':str(path),'retry':count,'elapsed_seconds':elapsed,'error':repr(exc),'exhausted':elapsed>=5}
            retry_events.append(event)
            with (OUT/(PREFIX+'io_events.jsonl')).open('a',encoding='utf-8',newline='\n') as handle:
                handle.write(json.dumps(event,sort_keys=True)+'\n')
            if elapsed>=5:raise
            time.sleep(min(0.05,5-elapsed))
def write_text(name,value):
    with (OUT/(PREFIX+name)).open('x',encoding='utf-8',newline='\n') as handle:
        handle.write(value);handle.flush();os.fsync(handle.fileno())
def write_json(name,value):write_text(name,json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')
preflight=read_json(OUT/(PREFIX+'preflight.json'))
reason="Specification conflict between dispatch T1 gate 1 and the committed note Section 5: T1 requires a synthetic sequence producing four suspensions. Section 5 defines entering CONSENSUS as a suspension and permanently prohibits de-escalation after the third suspension. After the third entry, the state cannot leave CONSENSUS and therefore cannot enter it a fourth time. The required four-suspension sequence cannot be produced under the registered rule."
completion=[]
warnings=list(preflight['stderr_warnings'])
completion_failures=[]
for item in preflight['source_readings']:
    path=item['path']
    result=subprocess.run(['git','cat-file','blob','HEAD:'+path],capture_output=True)
    if result.stderr:warnings.append({'stderr':result.stderr.decode('utf-8',errors='replace')})
    final_blob=digest(result.stdout) if result.returncode==0 else None
    final_work=digest((ROOT/path).read_bytes())
    current={**item,'end_blob_sha256_lf':final_blob,'end_worktree_sha256_lf':final_work,'completion_passed':result.returncode==0 and final_blob==final_work==item['expected_sha256_lf']}
    completion.append(current)
    if not current['completion_passed']:completion_failures.append(path)
head=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True).stdout.strip()
if head!=preflight['head']:completion_failures.append('HEAD changed')
if completion_failures:reason+=' Completion pin verification also failed: '+repr(completion_failures)
halt={'status':'HALTED','stage':'after T0, before T1 execution','reason':reason,'gate_model_runs_launched':0,'batch_runs_launched':0,'batch_runs_completed':0,'registered_batch_runs':240,'utc':now(),'tool_layer_workarounds':[],'executor_self_fixes':[]}
write_json('halt.json',halt)
results={'status':'HALTED','halt_reason':reason,'registered_batch_runs':240,'batch_runs_launched':0,'batch_runs_completed':0,'registered':{key:{'status':'not measured','value':None} for key in ('P1','P2','P3','P4','P5','P6')},'sign_fixture':{'status':'not run'},'A4_attack_validity':{'status':'not measured','void':None},'A3_reference_check':{'status':'not measured'},'criterion_arithmetic':{'status':'not measured'},'adoption_ruling':None}
write_json('results.json',results)
lines=['# Gate 3b points design: halt report','','## Registered results','','A4 attack-validity gate: not measured. No validity or void ruling was made. A3 reference check: not measured.','','P1 through P6: not measured. Batch runs launched: 0. Batch runs completed: 0. Registered batch runs: 240. Gate model runs launched: 0.','','Sign fixture: not run. Criterion-condition comparisons: not measured.','','## Halt reason','',reason,'','Dispatch T1 gate 1 requires a sequence producing four suspensions. The note Section 5 defines suspension as entering CONSENSUS and states that after the third suspension no further de-escalation occurs. CONSENSUS is the highest of the three states, so a fourth entry would require leaving it after permanence. No registered procedure was changed to resolve the conflict.','','T0: passed. T1 and execution were not started. This is a specification halt, not a gate 3b adoption ruling.','','This is gate 3b of the promotion plan. Its held-out attack was committed before its defense existed. This is not a promotion decision and adopts nothing. No ratio of two measured counts was computed. Applying the Section 8 criterion and the Section 9 interpretation is reserved for the operator.','','## Source readings','','SHA256 values below use LF-normalized bytes. Both committed blobs and working-tree files were checked at T0 and completion.','','| File | Pin | T0 blob | T0 worktree | Completion blob | Completion worktree |','| --- | --- | --- | --- | --- | --- |']
for item in completion:
    lines.append('| '+ ' | '.join(str(item[key]) for key in ('path','expected_sha256_lf','committed_sha256_lf','working_tree_sha256_lf','end_blob_sha256_lf','end_worktree_sha256_lf'))+' |')
lines+=['','## Execution metadata','', 'Machine: '+platform.node()+'. HEAD: '+head+'. Python: '+platform.python_version()+'. NumPy installed version: '+importlib.metadata.version('numpy')+'.','', 'Simulation workers launched: 0. Numerical-library thread limits: not exercised. Resumed seeds: none. Tool-layer workarounds: none. Executor self-fixes: none.','', 'T0 stderr warnings:']
lines+=['','> '+''.join(w['stderr'] for w in warnings).strip().replace('\n','\n> '),'', 'Operational I/O retry events: '+str(len(retry_events))+'.','', 'No exploratory analysis was performed.']
report='\n'.join(lines)+'\n'
assert chr(0x2014) not in report
write_text('report.md',report)
outputs=[]
for path in sorted(OUT.glob(PREFIX+'*')):
    if path.name==PREFIX+'manifest.json':continue
    raw=path.read_bytes()
    outputs.append({'path':path.relative_to(ROOT).as_posix(),'sha256_lf':digest(raw),'hash_basis':'LF-normalized bytes','csv_row_count':sum(1 for _ in csv.DictReader(io.StringIO(raw.decode('utf-8')))) if path.suffix=='.csv' else None,'jsonl_row_count':len(raw.splitlines()) if path.suffix=='.jsonl' else None})
manifest={'status':'HALTED','halt_reason':reason,'outputs':outputs,'manifest_self_hash':'Excluded because a manifest cannot contain its own final byte hash.','source_readings':completion,'committed_blob_sha1':{x['path']:x['committed_blob_sha1'] for x in completion},'per_module_sha256':[{'path':x['path'],'sha256':x['committed_sha256_lf'],'basis':'LF-normalized committed blob bytes'} for x in completion if x['path'].endswith('.py')],'machine':platform.node(),'head':head,'python_version':platform.python_version(),'numpy_version':importlib.metadata.version('numpy'),'numpy_version_basis':'installed distribution metadata; numerical library not initialized','worker_counts':{'gate':0,'batch':0},'worker_limits':{'normal':15,'work':12,'operator_cpu_budget':16},'effective_thread_limits':{'status':'not exercised; no worker launched'},'resumed_seeds':[],'retry_events':retry_events,'tool_layer_workarounds':[],'executor_self_fixes':[],'T0_stderr_warnings':preflight['stderr_warnings'],'merge':{'status':'not applicable; no runs launched','per_run':[],'deleted_file_counts':{}},'copied_executors':[]}
write_json('manifest.json',manifest)
print(json.dumps({'status':'HALTED','batch_runs_launched':0,'report':PREFIX+'report.md','results':PREFIX+'results.json','manifest':PREFIX+'manifest.json','completion_pins_match':not completion_failures}))
