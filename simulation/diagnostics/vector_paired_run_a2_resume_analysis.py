"""Registered P1 through P4 analysis for Measurement Tampering attempt 2."""
import sys
sys.dont_write_bytecode=True
import vector_paired_run_a2_executor as e
import csv,json,hashlib,traceback
from pathlib import Path
import numpy as np
import attack_metrics_v2 as metrics

COUNTERS=('evaluated_yield_opportunities','honest_yield_opportunities','ratified_yields',
          'yield_checks','yield_condition_blocked_count','yield_condition_met_count')
ALLOWED={'seed','corruption_active','defense_active','action_modified',*COUNTERS}

class RegisteredRecord:
    """Allow only declared analysis fields; record every registered access."""
    def __init__(self,row,accesses):
        self.__row={field:row[field] for field in ALLOWED}
        self.__accesses=accesses
    def __getitem__(self,key):
        assert key!='capture_rate', 'Legacy provenance field entered registered analysis'
        assert key in ALLOWED, 'Undeclared field entered registered analysis'
        self.__accesses.append(key)
        return self.__row[key]

def pretty(value):
    if value is None:return 'undefined'
    if isinstance(value,bool):return 'on' if value else 'off'
    return repr(value) if isinstance(value,float) else str(value)

def table(headers,rows):
    return ['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |']+[
        '| '+' | '.join(pretty(v) for v in row)+' |' for row in rows]+['']

def final_pins():
    records=e.pins()
    for item in records:
        actual=e.sha(e.lf(e.git('cat-file','blob','HEAD:'+item['path'])))
        if actual!=item['expected_sha256_lf']:raise RuntimeError('Committed pin changed: '+item['path'])
        item['end_blob_sha256_lf']=actual
        item['end_worktree_sha256_lf']=item['actual_sha256_lf']
        item['end_blob_sha1']=e.git('rev-parse','HEAD:'+item['path']).decode().strip()
    return records

def output_manifest(names,meta):
    target=e.P+'manifest.json'
    outputs=[]
    for name in sorted(set(names)):
        path=e.OUT/name
        count=None
        if path.suffix=='.csv' or '.csv.' in path.name:
            with path.open(encoding='utf-8',newline='') as f:count=sum(1 for _ in csv.DictReader(f))
        outputs.append({'path':path.relative_to(e.ROOT).as_posix(),
                        'sha256_lf':e.sha(e.lf(path.read_bytes())),'csv_rows':count})
    outputs.append({'path':(e.OUT/target).relative_to(e.ROOT).as_posix(),
                    'sha256_lf':None,'csv_rows':None,
                    'hash_note':'The manifest is listed but its self-hash is omitted to avoid recursive hashing.'})
    e.write(target,dict(meta,outputs=outputs,hash_basis='SHA256 of LF-normalized bytes; CSV counts use csv.DictReader excluding headers'))

def main():
    e.check_stop();e.check_identity()
    plan=e.read(e.P+'plan.json')
    resume=e.read(e.P+'resume_preflight.json')
    accounting=e.read(e.P+'resume_accounting.json')
    workarounds=plan['tool_layer_workarounds']+resume['tool_layer_workarounds']
    gate=e.read(e.P+'gates.json')
    execution=e.read(e.P+'execution.json')
    assert gate['passed'] is True and execution['status']=='COMPLETE'
    completions=[]
    for arm,seed in e.all_jobs():
        completion=e.completed(arm,seed)
        if completion is None:raise RuntimeError('Missing completed run')
        completions.append(completion)
    assert len(completions)==240
    rows=[c['row'] for c in completions]
    fields=list(rows[0])
    assert all(set(row)==set(fields) for row in rows)
    # Verbatim provenance export is separate from the restricted analysis interface.
    e.csv_output(e.P+'runs.csv',rows,fields)
    with (e.OUT/(e.P+'runs.csv')).open(encoding='utf-8',newline='') as f:
        csv_count=sum(1 for _ in csv.DictReader(f))
    assert csv_count==240
    accesses=[]
    registered=[RegisteredRecord(row,accesses) for row in rows]
    for row in registered:
        assert type(row['seed']) is int
        for field in COUNTERS:assert type(row[field]) is int
        assert type(row['action_modified']) is bool
    results={'status':'COMPLETE','runs_counted':csv_count,'P1':[],'P2':[],'P3':[],'P4':{}}
    for defense in (False,True):
        treatment=[r for r in registered if r['defense_active']==defense and r['corruption_active']]
        control=[r for r in registered if r['defense_active']==defense and not r['corruption_active']]
        assert len(treatment)==len(control)==60
        for number,field in [('P1','ratified_yields'),('P2','yield_condition_blocked_count')]:
            value=metrics.paired_difference(treatment,control,field)
            assert value['n_pairs']==60
            results[number].append({'defense_active':defense,'field':field,
                                    'sign':'corruption active minus disabled',**value})
    p4=[]
    for arm in plan['arms']:
        group=[r for r in registered if r['defense_active']==arm['defense_active']
               and r['corruption_active']==arm['corruption_active']]
        assert len(group)==60
        totals={field:sum(r[field] for r in group) for field in COUNTERS}
        results['P3'].append({'arm':arm['name'],'defense_active':arm['defense_active'],
                              'corruption_active':arm['corruption_active'],'n_runs':len(group),
                              'totals':totals})
        n,modified=metrics.action_change_count(group)
        p4.append({'arm':arm['name'],'defense_active':arm['defense_active'],
                   'corruption_active':arm['corruption_active'],'n_runs':n,'n_action_modified':modified})
    n,modified=metrics.action_change_count(registered)
    results['P4']={'n_runs':n,'n_action_modified':modified,'by_arm':p4}
    assert 'capture_rate' not in accesses and 'capture_rate' not in ALLOWED
    results['legacy_field_exclusion_assertion']={
        'passed':True,'registered_access_count':len(accesses),'fields_read':sorted(set(accesses)),
        'legacy_field_registered_reads':0,
        'method':'Restricted mapping refuses legacy and undeclared fields; all P1 through P4 accesses are logged.'}
    end_pins=final_pins()
    e.write(e.P+'source_pins_end.json',end_pins)
    e.write(e.P+'results.json',results)
    retries=[]
    for path in sorted(e.OUT.glob(e.P+'io_events_*.jsonl')):
        retries.extend(json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line)
    preflight=e.read(e.P+'preflight.json')
    warnings=[r for r in preflight['checks']+resume['checks'] if r.get('stderr')]
    modules={}
    for c in completions:
        for path,hashes in c['runtime']['modules'].items():
            modules.setdefault(path,[])
            if hashes not in modules[path]:modules[path].append(hashes)
    analysis_runtime=e.metadata(np)
    for path,hashes in analysis_runtime['modules'].items():
        modules.setdefault(path,[])
        if hashes not in modules[path]:modules[path].append(hashes)
    report=[
        '# Measurement Tampering: paired characterization, stage A, attempt 2','',
        'This is not a containment evaluation, not a defense rate, and reinstates no withdrawn figure. '
        'No ratio of two measured counts was computed by the registered analysis. '
        'The pinned runner computed and recorded its legacy capture_rate field verbatim for provenance; '
        'that field was not used by any registered quantity and is absent from report tables. '
        'The Section 10 interpretation is reserved for the operator.','',
        '## P1: ratified yields, primary','',
        'Counted from these runs using the committed paired_difference, treatment corruption active minus '
        'control corruption disabled, paired exactly by seed within each defense state.','']
    for key,title in [('P1',None),('P2','P2: blocked yield conditions')]:
        if title:report+=['## '+title,'']
        report+=table(['Defense','Pairs','Mean difference','Paired standard error','t statistic'],
                      [[r['defense_active'],r['n_pairs'],r['mean_difference'],
                        r['paired_standard_error'],r['t_statistic']] for r in results[key]])
    report+=['An undefined t statistic means paired standard error is exactly zero.','',
             '## P3: integer yield-counter totals','','All entries below are counted totals.','']
    report+=table(['Arm','Defense','Corruption','Runs',*COUNTERS],[
        [r['arm'],r['defense_active'],r['corruption_active'],r['n_runs'],
         *[r['totals'][field] for field in COUNTERS]] for r in results['P3']])
    report+=['## P4: action-modified counts','']
    report+=table(['Arm','Runs','Recorded action_modified true'],[
        [r['arm'],r['n_runs'],r['n_action_modified']] for r in p4]+[
        ['All',results['P4']['n_runs'],results['P4']['n_action_modified']]])
    report+=['## Execution and gate record','',
        'Attempt 1 halted before T1 on the ratio-prohibition conflict, with zero of 240 runs launched. '
        'Committed Amendment 2 resolved that conflict by permitting verbatim provenance retention '
        'while excluding the legacy field from registered analysis.','',
        'The analysis exclusion assertion passed: zero registered reads of the legacy field. '
        'The restricted mapping permits only the seed, arm labels, action_modified, and six declared integer counters. '
        'No difference of differences was computed and no other transition cost was run.','',
        'T0 passed in full. The known CRLF worktree against LF blobs was not repaired. '
        'The expected global Git ignore permission warning is recorded below.','',
        'T1 control inertness passed over 24 synthetic states with NumPy seed 20260917: '
        'all 24 control states were exactly unchanged; all 24 production states changed well-being; '
        'all 8 states with a nonempty entropy history changed its last entry. '
        'Both construction cells matched the pinned runner build path field by field without stepping a model.','',
        'All 240 runs were executed through the unmodified run_single. A transparent factory observer delegated '
        'to the original factory and observed the original step return after each step. '
        'The copied recorder recomputed raw entropy, checked exact cache equality, and verified unchanged NumPy '
        'random state. Per-step fallback increases were checked under Amendment 2. '
        'These recorder checks do not apply the drift-specific honest-arm adapter-inactivity requirement '
        'to the corruption-disabled measurement arm, which retains the configured measurement adapter.','',
        'The no-op replacement had the production method signature, returned None, and was installed only '
        'inside each control worker. Method restoration was verified after every run. '
        'The original factory reference was restored after every run.','',
        'Configuration: measurement_tampering, full mode, base_transition_cost 1.5, 300 requested steps, '
        'attack onset 50, 300 candidates and 20 rollout steps; seeds 1835087000 through 1835087059, '
        'each used once in each of the four cells. Every runner row field was preserved.','',
        'Recorded end reasons: '+json.dumps({reason:sum(c['end_reason']==reason for c in completions)
                    for reason in sorted({c['end_reason'] for c in completions})},sort_keys=True)+'.','',
        'Configured CPU budget: operator-specified 16 cores. Actual peak concurrent workers: '
        +str(execution['peak_active_workers'])+'. Normal cap 15; work cap 12. '
        'The synthetic scheduler checks covered caps, graceful mode transitions, deterministic job assignment, '
        'and skipping completed jobs on resumption. The runtime control is '+e.P+'control.json. '
        'The effective numerical-library thread count was verified as one in every worker. '
        'These worker limits are not an operating-system CPU reservation.','',
        'Mode changes: '+json.dumps(execution['mode_events'],sort_keys=True)+'.','',
        'Resumed jobs: '+json.dumps(execution['resumed_jobs'],sort_keys=True)+'. '
        'Preserved earlier completions: '+str(len(execution['preserved_jobs']))+'.','',
        'Continuous checks passed for every completed run. Non-permitted fallback increases: '
        +str(sum(c['shape_fallback_nonpermitted_increase_count'] for c in completions))+'. '
        'Exact entropy checks and unchanged-random-state recorder calls: '
        +str(sum(c['steps_completed'] for c in completions))+' each.','',
        'The write guard permits only the attempt 2 artifact prefix and the explicit os.devnull exemption. '
        'Bytecode writes were disabled. No production file was edited.','',
        'Transient permission errors on JSON reads and atomic replacement had a five-second bounded retry. '
        'Retry events recorded: '+str(len(retries))+'. '
        'Operational layer LF-normalized SHA256: '+e.sha(e.lf(Path(e.__file__).read_bytes()))+'.','',
        'Machine: '+str(completions[0]['runtime']['machine'])+'. HEAD: '+plan['head']+'. '
        'Python: '+completions[0]['runtime']['python']+'. NumPy: '+np.__version__+'.','',
        '## Source pins, start and completion','',
        'Hashes below use LF-normalized bytes. Both committed blobs and working-tree readings matched at start '
        'and completion; committed blob identities and per-module raw/LF hashes are included in the manifest.','']
    report+=table(['Path','Start SHA256','Completion SHA256'],[
        [r['path'],r['start_worktree_sha256_lf'],r['end_worktree_sha256_lf']] for r in end_pins])
    report+=['## Authorized resumption','',
        'The interruption reason was the provider usage limit. Counted at resumption: '
        +str(accounting['counts']['preserved'])+' preserved completions, '
        +str(accounting['counts']['interrupted'])+' restarted runs, and '
        +str(accounting['counts']['never_launched'])+' previously unlaunched runs. '
        'Preserved completion records, row hashes, log hashes, arm labels, and seeds validated. '
        'No preserved run was rerun or altered. Interrupted runs restarted from step 0 with the original seed '
        'and arm, with their prior initial, progress, and step artifacts retained under .partial names.','',
        'The saved T1 gates were not rerun. Their passing results and recorded source pins were verified '
        'against the current pins before resumption. Gate evidence LF-normalized SHA256: '
        +accounting['gate_evidence_sha256_lf']+'. This operational resumption changed no registered procedure.','',
        'Restarted runs, each due to the provider usage limit:','']
    report+=table(['Arm','Seed','New attempt'],[
        [r['arm']['name'],r['seed'],r['attempt']] for r in accounting['restarted']])
    report+=['Previously unlaunched runs, now completed:','']
    report+=table(['Arm','Seed'],[
        [r['arm']['name'],r['seed']] for r in accounting['never_launched']])
    report+=['Resumption source-pin readings:','']
    report+=table(['Path','Resumption SHA256'],[
        [r['path'],r['resumption_worktree_sha256_lf']] for r in resume['pins']])
    report+=['## T0 stderr warnings','']
    for item in warnings:report+=['- '+item['stderr'].strip().replace('\n',' ')]
    if not warnings:report+=['None.']
    report+=['','## Tool-layer workarounds','']
    report+=['- '+w for w in workarounds] or ['None.']
    report+=['','No exploratory analysis was performed.','']
    text='\n'.join(report)
    assert '\u2014' not in text
    with (e.OUT/(e.P+'report.md')).open('x',encoding='utf-8',newline='\n') as f:
        f.write(text);f.flush();e.os.fsync(f.fileno())
    meta={'status':'COMPLETE','head':plan['head'],'completion_head':e.git('rev-parse','HEAD').decode().strip(),
          'machine':completions[0]['runtime']['machine'],'python':sys.version,'numpy':np.__version__,
          'pins_start_and_end':end_pins,'per_module_hashes':modules,
          'module_hash_bases':'sha256_raw: raw working-tree bytes; sha256_lf: LF-normalized working-tree bytes',
          'worker_counts':{'operator_budget':16,'normal_cap':15,'work_cap':12,
                           'peak_actual':execution['peak_active_workers'],'completed_runs':240},
          'thread_verifications':{c['job']:c['runtime']['thread_runtime'] for c in completions},
          'mode_events':execution['mode_events'],'resumed_jobs':execution['resumed_jobs'],
          'preserved_jobs':execution['preserved_jobs'],'retry_events':retries,
          'tool_layer_workarounds':workarounds,'t0_stderr_warnings':warnings,
          'null_device_write_exemption':True,'bytecode_disabled':True,
          'legacy_field_exclusion_assertion':results['legacy_field_exclusion_assertion'],
          'operational_layer_sha256_lf':e.sha(e.lf(Path(e.__file__).read_bytes())),
          'csv_row_count':csv_count,'resumption_accounting':accounting,
          'resumption_preflight_pins':resume['pins'],
          'gate_evidence_relied_upon':{'path':e.P+'gates.json','sha256_lf':accounting['gate_evidence_sha256_lf']},
          'resumption_executor_sha256_lf':e.sha(e.lf((e.OUT/(e.P+'resume_executor.py')).read_bytes()))}
    outputs=[p.name for p in e.OUT.iterdir() if p.is_file() and p.name.startswith(e.P) and p.name!=e.P+'manifest.json']
    output_manifest(outputs,meta)
    print(json.dumps({'status':'COMPLETE','runs':csv_count,'report':e.P+'report.md',
                      'results':e.P+'results.json','manifest':e.P+'manifest.json'}),flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as error:
        e.mark_halt('analysis',error)
        print(traceback.format_exc(),file=sys.stderr)
        raise
