"""Registered X1 through X6 analysis and artifact manifest."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import defense_xv_run_a2_executor as ex
import csv,io,json,statistics,hashlib,os,traceback
import numpy as np
from attack_metrics_v2 import paired_difference
P=ex.P
OUT=ex.OUT
BIAS='Known-pathway bias: the allocation channel was chosen knowing how reallocation works. Channel constants were calibrated on the drift mapping construction.'

def stats(values):
    return {'minimum':min(values),'median':statistics.median(values),'maximum':max(values)} if values else {'minimum':None,'median':None,'maximum':None}

def table(lines,headers,rows):
    lines.append('| '+' | '.join(headers)+' |')
    lines.append('| '+' | '.join(['---']*len(headers))+' |')
    for row in rows:lines.append('| '+' | '.join(str(v) for v in row)+' |')
    lines.append('')

def manifest(end_pins,extra):
    plan=ex.read(P+'plan.json')
    outputs=[]
    manifest_name=P+'manifest.json'
    for path in sorted(OUT.glob(P+'*')):
        if path.name==manifest_name or not path.is_file():continue
        raw=path.read_bytes();normalized=ex.lf(raw)
        count=None
        if path.suffix=='.csv':
            count=sum(1 for _ in csv.DictReader(io.StringIO(normalized.decode('utf-8'))))
        outputs.append({'path':path.relative_to(ex.ROOT).as_posix(),'sha256_lf':ex.sha(normalized),'csv_rows':count})
    outputs.append({'path':'simulation/diagnostics/'+manifest_name,'sha256_lf':None,'csv_rows':None,
                    'hash_note':'Self-entry is excluded from recursive hashing; every other output is hashed.'})
    retries=[]
    for path in sorted(OUT.glob(P+'io_events_*.jsonl')):
        retries.extend(json.loads(line) for line in path.read_text(encoding='utf-8').splitlines())
    payload={'status':extra['status'],'outputs':outputs,'hash_basis':'LF-normalized bytes',
             'head':plan['head'],'machine':os.environ.get('COMPUTERNAME'),'python':sys.version,'numpy':np.__version__,
             'source_pins_start':plan['pins'],'source_pins_end':end_pins,
             'committed_evidence':plan['committed_evidence'],'copied_functions':plan['copied_functions'],
             'runtime':ex.metadata(np),'worker_counts':extra.get('worker_counts'),
             'worker_runtimes':[{key:value for key,value in ex.read(path.name)['runtime'].items()} for path in sorted(OUT.glob(P+'*_complete.json'))],
             'resumed_seeds':extra.get('resumed_seeds',[]),'retry_events':retries,
             'tool_layer_workarounds':plan['tool_layer_workarounds'],'T0_stderr_warnings':plan['T0_stderr_warnings'],
             'operational_layer_sha256_lf':ex.sha(ex.lf((OUT/(P+'executor.py')).read_bytes())),
             'no_interpretation':True}
    ex.write(manifest_name,payload)


class RegisteredRow:
    def __init__(self,raw,accesses):
        self.raw=raw;self.accesses=accesses
    def __getitem__(self,key):
        assert key!='capture_rate','Registered quantity attempted to read excluded legacy field'
        self.accesses.add(key)
        return self.raw[key]

def main():
    plan=ex.read(P+'plan.json');end_pins=ex.pins(full=True)
    if '--halt' in sys.argv:
        stop=ex.read(P+'stop.json')
        results={'status':'HALTED','halt':stop,'completed_runs':len(list(OUT.glob(P+'*_complete.json'))),
                 'registered_results':None}
        ex.write(P+'results.json',results)
        lines=['# Cross-vector evaluation attempt 2: halted','',str(stop['error']),'',
               'No registered analysis was performed. Applying the Section 6 criterion and the Section 7 interpretation is reserved for the operator.','']
        (OUT/(P+'report.md')).write_text('\n'.join(lines),encoding='utf-8',newline='\n')
        manifest(end_pins,results)
        return
    gates=ex.read(P+'gates.json');assert gates['passed']
    records=[];audits=[];accesses=set()
    for job in plan['jobs']:
        completion=ex.validate_completion(job)
        rows=ex.log_rows(completion['raw_log']);audit=ex.read(completion['audit_file'])
        raw=RegisteredRow(ex.read(completion['raw_row']),accesses)
        assert len(rows)==completion['steps_completed']==len(audit['steps'])==len(audit['heartbeats'])
        assert [r['step'] for r in rows]==list(range(len(rows)))
        assert all(r['incumbent_calls']==1 for r in audit['steps'])
        assert all(r['action_modified']==s['adapter_event_action_modified'] for r,s in zip(rows,audit['steps']))
        entries={state:next((v for v in audit['transitions'] if v['to']==state),None) for state in ('VETO','CONSENSUS')}
        for transition in audit['transitions']:
            if transition['to']=='VETO':
                previous=audit['steps'][transition['step']-1]
                assert transition['held_action_attack_modified']==previous['adapter_event_action_modified']
                assert transition['held_action']==previous['committed_action']
        counters={key:raw[key] for key in ('ratified_yields','yield_condition_blocked_count')}
        assert all(type(value) is int for value in counters.values())
        modified=raw['action_modified'];assert type(modified) is bool
        population=rows[-1]['population'];assert type(population) is int
        run={'job':job['job'],'vector':job['vector'],'own_defense':job['own_defense'],
             'defense_arm':job['defense_arm'],'seed':job['seed'],'onset':completion['onset'],
             'steps_completed':len(rows),'end_reason':completion['end_reason'],
             'steps_at_or_after_onset_above_g_star':sum(int(r['step']>=completion['onset'] and r['g']>=1.0965735902799727) for r in rows),
             'final_population':population,**counters,'action_modified':int(modified),
             'veto_entry_step':entries['VETO']['step'] if entries['VETO'] else None,
             'consensus_entry_step':entries['CONSENSUS']['step'] if entries['CONSENSUS'] else None,
             'veto_held_action_attack_modified':int(entries['VETO']['held_action_attack_modified']) if entries['VETO'] else 0,
             'recorded_steps':len(rows),'heartbeat_count':len(audit['heartbeats']),
             'raw_log':completion['raw_log'],'raw_row':completion['raw_row'],'audit_file':completion['audit_file']}
        records.append(run)
        audits.append({'job':job['job'],'audit_file':completion['audit_file'],
                       'sha256_lf':completion['audit_sha256_lf'],'alarm_records':len(audit['alarms']),
                       'transition_records':len(audit['transitions']),
                       'incumbent_action_records':len(audit['incumbent_actions'])})
    assert len(records)==720
    assert 'capture_rate' not in accesses
    assert accesses=={'ratified_yields','yield_condition_blocked_count','action_modified'}
    exclusion={'passed':True,'registered_runner_fields_read':sorted(accesses),
               'capture_rate_recorded_verbatim_in_raw_rows':True,'capture_rate_read_by_registered_quantity':False}
    X1=[];X2=[];X2_extinctions=[];X3=[];X4=[];X4_own_on=[];X5=[]
    binary=set(ex.VECTORS)-{'measurement_tampering','biological_veto_capture'}
    proposal_note='The wrapper runs the production adapter first, so action_modified records what the attack did to the proposal, not what was committed.'
    for vector in ex.VECTORS:
        for own_defense in (False,True):
            cells={d:[r for r in records if r['vector']==vector and r['own_defense']==own_defense and r['defense_arm']==d] for d in ('OFF','GRADED')}
            assert all(len(v)==20 for v in cells.values())
            def pair(field):
                assert all(type(r[field]) is int for rows in cells.values() for r in rows)
                value=paired_difference(cells['OFF'],cells['GRADED'],field)
                assert value['n_pairs']==20
                return {'vector':vector,'own_defense':own_defense,'field':field,'contrast':'OFF minus GRADED',
                        **value,'qualification':BIAS}
            X1.append(pair('steps_at_or_after_onset_above_g_star'))
            X2.append(pair('final_population'))
            if vector in ('measurement_tampering','successor_contamination','biological_veto_capture'):
                X3.append(pair('ratified_yields'))
            field='action_modified' if vector in binary else ('yield_condition_blocked_count' if vector=='biological_veto_capture' else 'ratified_yields')
            X4.append({**pair(field),'proposal_note':proposal_note})
            for defense,runs in cells.items():
                common={'vector':vector,'own_defense':own_defense,'defense_arm':defense,'runs':20,'qualification':BIAS}
                X2_extinctions.append({**common,'extinction_runs':sum(int(r['end_reason']=='extinction') for r in runs)})
                if vector in binary and own_defense:
                    X4_own_on.append({**common,'action_modified_true_runs':sum(r['action_modified'] for r in runs),'proposal_note':proposal_note})
                X5.append({**common,'entered_VETO':sum(r['veto_entry_step'] is not None for r in runs),
                           'VETO_entry_steps':stats([r['veto_entry_step'] for r in runs if r['veto_entry_step'] is not None]),
                           'entered_CONSENSUS':sum(r['consensus_entry_step'] is not None for r in runs),
                           'CONSENSUS_entry_steps':stats([r['consensus_entry_step'] for r in runs if r['consensus_entry_step'] is not None]),
                           'VETO_entries_with_attack_modified_held_action':sum(r['veto_held_action_attack_modified'] for r in runs)})
    X6={'runs':720,'matching_runs':sum(r['recorded_steps']==r['steps_completed']==r['heartbeat_count'] for r in records),
        'mismatches':[],'per_run_audits':audits,'qualification':BIAS}
    execution=ex.read(P+'batch_execution.json')
    results={'status':'COMPLETE','registered':{'X1':X1,'X2':{'paired_population':X2,'extinction_counts':X2_extinctions},
             'X3':X3,'X4':{'paired':X4,'own_defense_on_counts':X4_own_on,'proposal_note':proposal_note},
             'X5':X5,'X6':X6},'capture_rate_exclusion_assertion':exclusion,'qualification':BIAS,
             'head':plan['head'],'worker_counts':{'batch':execution,'gates':ex.read(P+'gates_execution.json')},
             'resumed_seeds':execution['resumed'],'source_pins_end':end_pins}
    ex.csv_output(P+'runs.csv',records,list(records[0]))
    ex.write(P+'results.json',results)
    lines=['# In-loop drift defense cross-vector evaluation, attempt 2','',
           'This is gate 1 of the promotion plan. It measures harm, not containment of these vectors. It is not a promotion decision and does not test input corruption. No ratio of two measured counts was computed in the quantities this note derives, reports, or cites. Applying the Section 6 criterion and the Section 7 interpretation is reserved for the operator.','',
           'Attempt 1 halted on the ratio conflict before any evaluation run. Amendment 1 resolved it. The pinned runner legacy capture_rate field was recorded verbatim in raw rows and was not used in any registered quantity. The analysis exclusion assertion passed.','',
           '## X1. Paired steps past the threshold','',BIAS,'']
    headers=['Vector','Own defense','Field','Pairs','Mean difference','Paired standard error','t statistic','Qualification']
    def pair_rows(items):
        return [[r['vector'],r['own_defense'],r['field'],r['n_pairs'],repr(r['mean_difference']),
                 repr(r['paired_standard_error']),'undefined (zero standard error)' if r['t_statistic'] is None else repr(r['t_statistic']),BIAS] for r in items]
    table(lines,headers,pair_rows(X1))
    lines.extend(['## X2. Paired final population and extinction counts','',BIAS,''])
    table(lines,headers,pair_rows(X2))
    table(lines,['Vector','Own defense','Drift defense','Runs','Extinction runs','Qualification'],
          [[r['vector'],r['own_defense'],r['defense_arm'],r['runs'],r['extinction_runs'],BIAS] for r in X2_extinctions])
    lines.extend(['## X3. Paired ratified yield counts','',BIAS,''])
    table(lines,headers,pair_rows(X3))
    lines.extend(['## X4. Paired vector outcome counts','',proposal_note,'',BIAS,''])
    table(lines,headers,pair_rows(X4))
    table(lines,['Vector','Own defense','Drift defense','Runs','Action-modified true runs','Qualification'],
          [[r['vector'],r['own_defense'],r['defense_arm'],r['runs'],r['action_modified_true_runs'],BIAS] for r in X4_own_on])
    lines.extend(['## X5. Intervention counts and entry steps','',BIAS,''])
    table(lines,['Vector','Own defense','Drift defense','Runs','Entered VETO','VETO min, median, max',
                 'Entered CONSENSUS','CONSENSUS min, median, max','Attack-modified held actions','Qualification'],
          [[r['vector'],r['own_defense'],r['defense_arm'],r['runs'],r['entered_VETO'],list(r['VETO_entry_steps'].values()),
            r['entered_CONSENSUS'],list(r['CONSENSUS_entry_steps'].values()),r['VETO_entries_with_attack_modified_held_action'],BIAS] for r in X5])
    lines.extend(['## X6. Liveness and auditability','',BIAS,'',
                  'Recorded steps and heartbeat records equal completed steps in '+str(X6['matching_runs'])+' of 720 runs. Mismatches: '+json.dumps(X6['mismatches'])+'.','',
                  'Every run has a per-step CSV, verbatim runner row, completion record, and audit JSON. Audits contain every channel alarm, transition, applied action, committed snapshot, and event action-modified flag. Both the production binding and runner factory were restored and verified by identity.','',
                  '## Pre-run check evidence','',
                  'The required technical pre-run checks passed. This statement does not apply the promotion criterion. Measured evidence is recorded below and in the gate files.','',
                  chr(96)*3+'json',json.dumps(gates,indent=2),chr(96)*3,'',
                  '## Source pins',''])
    table(lines,['Path','Start committed SHA256 (LF)','Start working-tree SHA256 (LF)','End committed SHA256 (LF)','End working-tree SHA256 (LF)'],
          [[r['path'],r['start_blob_sha256_lf'],r['start_worktree_sha256_lf'],r['end_blob_sha256_lf'],r['end_worktree_sha256_lf']] for r in end_pins])
    lines.extend(['## Execution provenance','',
                  'Machine: '+str(os.environ.get('COMPUTERNAME'))+'. HEAD: '+plan['head']+'.',
                  'Python: '+sys.version+'. NumPy: '+np.__version__+'.',
                  'Numerical-library threads were fixed to one and verified per worker. Normal cap: 15. Work cap: 12. Runtime control: '+P+'control.json.',
                  'Maximum batch concurrency: '+str(execution['maximum_concurrent_workers'])+'.',
                  'Resumed seeds: '+json.dumps(execution['resumed'])+'.',
                  'Tool-layer workarounds: '+json.dumps(plan['tool_layer_workarounds'])+'.',
                  'T0 stderr warnings: '+json.dumps(plan['T0_stderr_warnings'])+'.',
                  'The CRLF working-tree condition was left unchanged. Every bounded I/O retry is listed in the manifest.',
                  'Analysis field-access assertion: '+json.dumps(exclusion)+'.',''])
    text='\n'.join(lines);assert chr(0x2014) not in text
    (OUT/(P+'report.md')).write_text(text,encoding='utf-8',newline='\n')
    manifest(end_pins,results)

if __name__=='__main__':
    try:main()
    except BaseException as error:
        ex.mark_halt('analysis',error)
        raise
