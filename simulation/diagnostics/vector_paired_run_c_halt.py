"""Record the stage C specification halt without importing simulation modules."""
import sys,os
sys.dont_write_bytecode=True
os.environ['PYTHONDONTWRITEBYTECODE']='1'
os.environ['GIT_OPTIONAL_LOCKS']='0'
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
PREFIX='vector_paired_run_c_'
NULL=Path(os.devnull).resolve()
def allowed(path):
    p=Path(path).resolve()
    return p==NULL or (p.parent==OUT and p.name.startswith(PREFIX))
def guard(event,args):
    if event=='open':
        path,mode,flags=args
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_APPEND|os.O_TRUNC))
        if writing and not isinstance(path,int) and not allowed(path):raise RuntimeError('Write outside scope: '+str(path))
    elif event=='os.rename':
        if not allowed(args[0]) or not allowed(args[1]):raise RuntimeError('Rename outside scope')
    elif event in ('os.remove','os.rmdir','os.mkdir','os.link','os.symlink'):
        raise RuntimeError('Unexpected filesystem mutation: '+event)
sys.addaudithook(guard)
import csv,json,hashlib,subprocess,time,importlib.metadata
from datetime import datetime,timezone
RETRIES=[]
def now():return datetime.now(timezone.utc).isoformat()
def digest(raw):return hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()
def retry(operation,path,call):
    started=time.monotonic()
    while True:
        try:return call()
        except PermissionError as error:
            elapsed=time.monotonic()-started
            event={'utc':now(),'operation':operation,'path':str(path),'elapsed_seconds':elapsed,'error':str(error),'exhausted':elapsed>=5.0}
            RETRIES.append(event)
            with (OUT/(PREFIX+'io_events.jsonl')).open('a',encoding='utf-8',newline='\n') as stream:
                stream.write(json.dumps(event)+'\n');stream.flush();os.fsync(stream.fileno())
            if elapsed>=5.0:raise
            time.sleep(min(0.025,5.0-elapsed))
def read(name):
    return retry('JSON read',name,lambda:json.loads((OUT/name).read_text(encoding='utf-8')))
def write(name,data):
    path=OUT/name
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n')
        stream.flush();os.fsync(stream.fileno())
def git(*args):
    p=subprocess.run(['git',*args],cwd=ROOT,capture_output=True)
    if p.returncode:raise RuntimeError(p.stderr.decode('utf-8',errors='replace'))
    return p.stdout
def main():
    preflight=read(PREFIX+'preflight.json')
    assert preflight['status']=='PASS'
    reason="C5 requires comparing the two zero-capture arms on every recorded field, including the pinned runner's capture_rate field. Amendment 2 (Section 14) excludes capture_rate from every registered quantity and requires asserting that no registered quantity reads it. C5 is a registered quantity, so both requirements cannot be satisfied without changing the specified comparison."
    readings=[]
    for item in preflight['source_readings']:
        blob=git('cat-file','blob','HEAD:'+item['path'])
        worktree=(ROOT/item['path']).read_bytes()
        row=dict(item,completion_committed_sha256_lf=digest(blob),completion_working_tree_sha256_lf=digest(worktree))
        assert row['completion_committed_sha256_lf']==row['completion_working_tree_sha256_lf']==item['expected_sha256_lf'],item['path']
        readings.append(row)
    assert git('rev-parse','HEAD').decode().strip()==preflight['head']
    evidence=[
        {'source':'dispatch C5','requirement':'The two zero-capture arms are compared field by field at every seed; report whether they are bit-identical on every recorded field.'},
        {'source':'committed pre-registration Section 14, lines 260 through 264','requirement':'The legacy field is retained verbatim in raw rows, excluded from every registered quantity, and the analysis must assert no registered quantity reads it.'},
        {'source':'committed pinned runner run_single, line 435','requirement':'The returned row includes capture_rate.'}]
    results={'status':'HALTED','stage':'C','halt_phase':'after T0, before T1 and model construction',
             'halt_reason':reason,'specification_evidence':evidence,
             'runs_planned':900,'runs_launched':0,'runs_completed':0,'model_steps_completed':0,
             'registered':{name:{'status':'NOT_COMPUTED','value':None} for name in ('C1','C2','C3','C4','C5','C6')},
             'capture_rate_exclusion_assertion':{'status':'NOT_RUN','reason':'Analysis was not launched; the C5 specification conflicts with the required exclusion.'},
             'capture_rate_values_recorded':0,'capture_rate_values_used':0,
             'interpretation_applied':False,'pre_repair_comparison_drawn':False}
    write(PREFIX+'results.json',results)
    lines=['# Per-vector paired characterization, stage C: halt','',
        'This is a post-repair re-measurement of a quantity banked pre-repair. The two measure different substrates and neither supersedes the other.',
        'No ratio of two measured counts was computed. No capture_rate values were recorded or used because no runs were launched. Section 10 interpretation is reserved for the operator.','',
        'Status: HALTED after T0, before T1 and before model construction. Runs launched: 0. Runs completed: 0. Planned runs: 900.','',
        '## Registered results','']
    for name in ('C1','C2','C3','C4','C5','C6'):
        lines.extend(['### '+name,'','Not computed.',''])
    lines.extend(['## Halt reason','',reason,'',
        'C5 cannot compare every returned field while satisfying Amendment 2. Excluding the field from C5 would change the specified comparison; including it would violate the amendment. Neither change was made.','',
        'The pinned runner source confirms that run_single returns the legacy field. The runner was read through its committed blob and was not imported or executed.','',
        'Capture-rate exclusion assertion: not run. No analysis was launched.',
        'T0: all enumerated checks passed. T1: not run. Merge: not run. No exploratory analysis was performed.','',
        '## Source readings','',
        '| File | Start committed SHA256, LF | Start working-tree SHA256, LF | Completion committed SHA256, LF | Completion working-tree SHA256, LF |',
        '| --- | --- | --- | --- | --- |'])
    for r in readings:
        lines.append('| '+' | '.join([r['path'],r['committed_sha256_lf'],r['working_tree_sha256_lf'],r['completion_committed_sha256_lf'],r['completion_working_tree_sha256_lf']])+' |')
    numpy_version=importlib.metadata.version('numpy')
    lines.extend(['','## Execution metadata','',
        'HEAD: '+preflight['head'],'Machine: '+str(preflight['machine']),
        'Python: '+sys.version.replace('\n',' '),'NumPy distribution version: '+numpy_version,
        'Simulation modules imported: 0. Workers launched: 0. Configured worker cap: 15. Numerical thread verification: not run because no workers were launched.',
        'Resumed seeds: none. Tool-layer workarounds: none. Executor self-fixes: none.',
        'Known line-ending condition: working-tree CRLF is LF-normalized for hashing; committed blobs are the evidence source.','',
        'T0 stderr warnings:'])
    lines.extend(w['stderr'].rstrip() for w in preflight['stderr_warnings'])
    lines.extend(['','Permission retry events: '+json.dumps(RETRIES,sort_keys=True),''])
    report='\n'.join(lines)
    assert chr(0x2014) not in report
    with (OUT/(PREFIX+'report.md')).open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(report);stream.flush();os.fsync(stream.fileno())
    outputs=[]
    for path in sorted(OUT.glob(PREFIX+'*')):
        if not path.is_file() or path.name==PREFIX+'manifest.json':continue
        count=None
        if path.suffix=='.csv':
            with path.open(encoding='utf-8',newline='') as stream:count=sum(1 for _ in csv.DictReader(stream))
        outputs.append({'path':path.relative_to(ROOT).as_posix(),'sha256_lf':digest(path.read_bytes()),'hash_basis':'LF-normalized bytes','csv_row_count':count})
    metadata={'machine':preflight['machine'],'head':preflight['head'],'python':sys.version,'numpy_version':numpy_version,
              'numpy_version_basis':'Installed distribution metadata; NumPy was not imported.',
              'workers_launched':0,'maximum_concurrent_workers':0,'normal_worker_cap':15,'work_worker_cap':12,
              'operator_cpu_budget':16,'operating_mode':'normal','numerical_threads_configured_per_worker':1,
              'effective_threads_verified_per_worker':[],'thread_verification_status':'NOT_RUN'}
    manifest={'status':'HALTED','halt_reason':reason,'created_utc':now(),'runtime':metadata,
        'outputs':outputs,'manifest_self_hash':'Excluded to avoid a recursive self-hash.',
        'source_readings':readings,'committed_blob_sha1':{r['path']:r['committed_blob_sha1'] for r in readings},
        'read_committed_sources':preflight['read_committed_sources'],
        'per_module_sha256':{},'per_module_hash_basis':'No simulation module was imported. Source pins and artifact hashes are recorded separately.',
        'runs_planned':900,'runs_launched':0,'runs_completed':0,'resumed_seeds':[],'retry_events':RETRIES,
        'tool_layer_workarounds':[],'executor_self_fixes':[],'T0_stderr_warnings':preflight['stderr_warnings'],
        'merge':{'status':'NOT_RUN','recorded_row_hashes':[],'merged_row_count':0,'deleted_file_counts':{}}}
    write(PREFIX+'manifest.json',manifest)
    print(json.dumps({'status':'HALTED','runs_launched':0,'halt_reason':reason,
          'report':PREFIX+'report.md','results':PREFIX+'results.json','manifest':PREFIX+'manifest.json'}))
if __name__=='__main__':main()
