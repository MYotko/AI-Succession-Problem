"""Authorized operational resumption after a provider usage limit."""
import sys
sys.dont_write_bytecode=True
import detector_run_r2_eval_executor as h
import argparse,csv,io,json,subprocess
from pathlib import Path

ORIGINAL_READ=h.read
ORIGINAL_WRITE=h.write
P=h.P
PRE=ORIGINAL_READ(P+'resume_preflight.json')
INTERRUPTED={r['job']:r for r in PRE['interrupted']}
ORIGINAL_EXECUTION=ORIGINAL_READ(P+'execution.json')
ATTEMPTS={job:ORIGINAL_EXECUTION['attempts'][job]+1 for job in INTERRUPTED}


def route(name):
    if name==P+'execution.json':return P+'resume_execution.json'
    if name==P+'control.json':return P+'resume_control.json'
    if name==P+'unit_gate.json':return P+'resume_unit_gate.json'
    for job in INTERRUPTED:
        for kind in ('initial','progress'):
            if name==P+job+'_'+kind+'.json':return P+job+'_'+kind+'_attempt'+str(ATTEMPTS[job])+'.json'
    return name

def read(name):return ORIGINAL_READ(route(name))

def write(name,obj):
    if name==P+'execution.json':
        obj['resumption_reason']='provider usage limit'
        obj['resumption_counts']={'preserved':len(PRE['preserved']),'restarted':len(PRE['interrupted']),'newly_run':len(PRE['never_launched'])}
        obj['never_launched_at_interruption']=PRE['never_launched']
        for row in obj.get('resumed_seeds',[]):row['reason']='provider usage limit'
    return ORIGINAL_WRITE(route(name),obj)

def operation_record(event):
    row={'utc':h.now(),'pid':h.os.getpid(),**event}
    with(h.OUT/(P+'resume_io_events_'+str(h.os.getpid())+'.jsonl')).open('a',encoding='utf-8',newline='\n') as f:
        f.write(json.dumps(row,sort_keys=True)+'\n');f.flush();h.os.fsync(f.fileno())

h.read=read;h.write=write;h.operation_record=operation_record

# Preserve every earlier completed-run artifact and all prior gate outputs.
PROTECTED=set()
preserved_prefixes=tuple(P+r['job']+'_' for r in PRE['preserved'])
for path in h.OUT.iterdir():
    if path.name.startswith(preserved_prefixes):PROTECTED.add(path.resolve())
for name in ('executor.py','plan.json','analysis.py','report.py','unit_gate.py','unit_gate.json','unit_sequences.csv',
             'gates.json','recorder_conformance.json','constants_gate.json','derivation_gate.json','code_identity.json',
             'execution.json','control.json'):
    PROTECTED.add((h.OUT/(P+name)).resolve())
for job in INTERRUPTED:
    for kind in ('initial','progress'):PROTECTED.add((h.OUT/(P+job+'_'+kind+'.json')).resolve())

def protect(event,args):
    if event=='open':
        path,mode,flags=args
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or(isinstance(flags,int) and flags&(h.os.O_WRONLY|h.os.O_RDWR|h.os.O_CREAT|h.os.O_APPEND|h.os.O_TRUNC))
        if writing and not isinstance(path,int) and Path(path).resolve() in PROTECTED:
            raise RuntimeError('Preserved artifact writable open rejected: '+str(path))
    elif event=='os.rename' and (Path(args[0]).resolve() in PROTECTED or Path(args[1]).resolve() in PROTECTED):
        raise RuntimeError('Preserved artifact rename rejected')
sys.addaudithook(protect)


def spawn(job,arm=None,seed=None,attempt=1):
    cmd=[sys.executable,'-B',str(Path(__file__).resolve()),'worker','--job',job,'--attempt',str(attempt)]
    if arm is not None:cmd+=['--arm',arm,'--seed',str(seed)]
    return subprocess.Popen(cmd,cwd=h.ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
h.spawn=spawn


def unit():
    import detector_run_r2_eval_unit_gate as u
    original_csv=u.csv_output
    def output(name,rows,fields=None):
        if name==P+'unit_sequences.csv':name=P+'resume_unit_sequences.csv'
        return original_csv(name,rows,fields)
    u.csv_output=output
    u.unit_gate()
    # No other gate function is called during resumption.


def prepare():
    if not read(P+'unit_gate.json')['passed']:raise RuntimeError('Resumption unit gate failed')
    h.pins()
    renames=[]
    for job,record in INTERRUPTED.items():
        old_attempt=ORIGINAL_EXECUTION['attempts'][job]
        base=P+job+'_steps_attempt'+str(old_attempt)+'.csv'
        candidates=[h.OUT/(base+'.partial'),h.OUT/base]
        found=[path for path in candidates if path.exists()]
        if len(found)!=1:raise RuntimeError('Expected one interrupted log: '+job)
        source=found[0].resolve()
        target=(h.OUT/(P+job+'_steps_attempt'+str(old_attempt)+'_provider_usage_limit.csv.partial')).resolve()
        if source.parent!=h.OUT or target.parent!=h.OUT or not h.allowed(source) or not h.allowed(target):
            raise RuntimeError('Interrupted log rename is outside scope')
        if target.exists():raise RuntimeError('Interrupted log retention target exists: '+target.name)
        raw=source.read_bytes();before=h.sha(h.lf(raw))
        h.replace_with_retry(source,target)
        after=h.sha(h.lf(target.read_bytes()))
        if after!=before:raise RuntimeError('Interrupted log changed during retention')
        renames.append({**record,'old_path':source.name,'retained_partial_path':target.name,
                        'sha256_lf':after,'partial_csv_rows':sum(1 for unused in csv.DictReader(io.StringIO(raw.decode('utf-8')))),
                        'old_attempt':old_attempt,'new_attempt':ATTEMPTS[job],'restart_step':0,'reason':'provider usage limit'})
    h.write(P+'execution.json',ORIGINAL_EXECUTION)
    h.write(P+'control.json',ORIGINAL_READ(P+'control.json'))
    accounting={'reason':'provider usage limit','preserved_count':len(PRE['preserved']),'restarted_count':len(INTERRUPTED),
                'newly_run_count':len(PRE['never_launched']),'preserved':PRE['preserved'],'restarted':renames,
                'never_launched':PRE['never_launched'],'gate_evidence_reused':PRE['gate_evidence'],
                'synthetic_gate_rerun':P+'resume_unit_gate.json','executor_and_plan_identity':h.identity(),
                'operational_helper_sha256_lf':h.sha(h.lf(Path(__file__).read_bytes())),
                'operational_decision':'Only the synthetic detector gate was rerun. Passing model, recorder, constants, and derivation gates from the same interrupted batch were verified and reused without repetition.',
                'created_utc':h.now()}
    h.write(P+'resume_accounting.json',accounting)
    print(json.dumps({'prepared':True,'preserved':len(PRE['preserved']),'restarted':len(INTERRUPTED),'never_launched':len(PRE['never_launched'])}),flush=True)


def batch():
    account=read(P+'resume_accounting.json')
    if account['operational_helper_sha256_lf']!=h.sha(h.lf(Path(__file__).read_bytes())):raise RuntimeError('Resumption helper changed')
    h.batch()


def finalize():
    import detector_run_r2_eval_analysis as analysis
    import detector_run_r2_eval_report as report
    account=read(P+'resume_accounting.json')
    for r in PRE['preserved']:
        path=h.OUT/r['completion']
        if h.sha(h.lf(path.read_bytes()))!=r['completion_sha256_lf']:raise RuntimeError('Preserved completion changed: '+r['job'])
        if h.sha(h.lf((h.OUT/r['raw_log']).read_bytes()))!=r['raw_log_sha256_lf']:raise RuntimeError('Preserved raw log changed: '+r['job'])
    for evidence in PRE['gate_evidence']:
        if h.sha(h.lf((h.ROOT/evidence['path']).read_bytes()))!=evidence['sha256_lf']:raise RuntimeError('Reused gate evidence changed')
    for group,expected_attempt in ((account['restarted'],2),(account['never_launched'],1)):
        for item in group:
            r=h.completed(item['job'],item['arm'],item['seed'])
            if r is None or r['attempt']!=expected_attempt:raise RuntimeError('Resumed attempt accounting mismatch: '+item['job'])
    analysis.analyze()
    report.finalize()
    report_path=h.OUT/(P+'report.md')
    appendix=['','## Authorized resumption after the provider usage limit','',
              'Interruption reason: provider usage limit. This was an operational interruption, not a gate, continuous-check, or model exception.','',
              f"Preserved completed runs: {account['preserved_count']}. Interrupted runs restarted from step 0: {account['restarted_count']}. Previously unlaunched jobs run: {account['newly_run_count']}.",'',
              account['operational_decision'],'',
              'Every preserved completion record parsed and matched its arm and seed; its raw log matched the recorded LF-normalized SHA256. Preserved completion records, raw logs, and reused gate evidence were revalidated at completion. Earlier initial, progress, execution, control, and gate outputs were retained. New operational state is in resume_execution.json and resume_control.json under the governed prefix.','',
              '### Restarted jobs','',report.table(['Arm','Seed','Prior attempt','New attempt','Restart step','Retained partial log'],
              [[r['arm'],r['seed'],r['old_attempt'],r['new_attempt'],r['restart_step'],r['retained_partial_path']] for r in account['restarted']]),
              '### Previously unlaunched jobs','',report.table(['Arm','Seed','Attempt'],[[r['arm'],r['seed'],1] for r in account['never_launched']]),
              '### Gate evidence relied upon','',report.table(['Path','LF-normalized SHA256','Passed'],[[r['path'],r['sha256_lf'],r['passed']] for r in account['gate_evidence_reused']]),
              'Executor LF-normalized SHA256: '+account['executor_and_plan_identity']['executor_sha256_lf']+'.',
              'Plan LF-normalized SHA256: '+account['executor_and_plan_identity']['plan_sha256_lf']+'.',
              'Resumption helper LF-normalized SHA256: '+account['operational_helper_sha256_lf']+'.','',
              'Resumption T0 stderr warnings:','', '```text',
              '\n'.join(r['stderr'] for r in PRE['checks'] if r.get('stderr')) or 'None.','```','',
              'A read-only CIM process query returned Access denied. A direct query of the recorded worker PIDs confirmed that none remained active; this environment probe is recorded in resume_process_check.json.','']
    with report_path.open('a',encoding='utf-8',newline='\n') as f:f.write('\n'.join(appendix))
    manifest=read(P+'manifest.json');manifest['resumption_accounting']=account
    manifest['resumption_t0']=PRE
    retry_events=[]
    for path in h.OUT.iterdir():
        if path.name.startswith(P+'resume_io_events_') and path.suffix=='.jsonl':
            with path.open(encoding='utf-8') as f:retry_events.extend(json.loads(line) for line in f if line.strip())
    manifest['resumption_retry_events']=retry_events
    outputs=[]
    for path in sorted(h.OUT.iterdir()):
        if not path.is_file() or not path.name.startswith(P) or path.name==P+'manifest.json':continue
        raw=path.read_bytes();count=None
        if path.suffix=='.csv' or path.name.endswith('.csv.partial'):count=sum(1 for unused in csv.DictReader(io.StringIO(raw.decode('utf-8'))))
        outputs.append({'path':path.relative_to(h.ROOT).as_posix(),'sha256_lf':h.sha(h.lf(raw)),'csv_rows':count,'partial':path.name.endswith('.partial')})
    manifest['outputs']=outputs;manifest['finalized_after_resumption_utc']=h.now()
    h.write(P+'manifest.json',manifest)
    print(json.dumps({'status':manifest['status'],'preserved':account['preserved_count'],'restarted':account['restarted_count'],'newly_run':account['newly_run_count'],'resumption_retry_events':len(retry_events)}),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['unit','prepare','batch','worker','finalize'])
    parser.add_argument('--job');parser.add_argument('--arm');parser.add_argument('--seed',type=int);parser.add_argument('--attempt',type=int,default=1)
    args=parser.parse_args()
    try:
        if args.command=='worker':h.worker(args)
        elif args.command=='unit':unit()
        elif args.command=='prepare':prepare()
        elif args.command=='batch':batch()
        else:finalize()
    except BaseException as error:
        h.mark_halt('resume_'+args.command,error)
        raise
if __name__=='__main__':main()
