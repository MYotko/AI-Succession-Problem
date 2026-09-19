"""Registered C1 through C6 analysis and artifact manifest."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import drift_defense_run_executor as ex
import csv,io,json,statistics,hashlib,os,traceback
import numpy as np
from attack_metrics_v2 import paired_difference
P=ex.P
OUT=ex.OUT
BIAS='Known pathways only: the allocation channel was chosen knowing how the reallocation attack works; these values apply to the named attack arms on this substrate and are not evidence about attacks the architecture was not designed against.'

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
             'resumed_seeds':extra.get('resumed_seeds',[]),'retry_events':retries,
             'tool_layer_workarounds':plan['tool_layer_workarounds'],'T0_stderr_warnings':plan['T0_stderr_warnings'],
             'operational_layer_sha256_lf':ex.sha(ex.lf((OUT/(P+'executor.py')).read_bytes())),
             'no_interpretation':True}
    ex.write(manifest_name,payload)

def main():
    plan=ex.read(P+'plan.json');end_pins=ex.pins(full=True)
    halted='--halt' in sys.argv
    if halted:
        stop=ex.read(P+'stop.json')
        results={'status':'HALTED','halt':stop,'completed_runs':len(list(OUT.glob(P+'*_complete.json'))),
                 'registered_results':None}
        ex.write(P+'results.json',results)
        lines=['# Drift defense run: halted','',str(stop['error']),'',
               'No registered analysis was performed. The Section 8 interpretation is reserved for the operator.','']
        (OUT/(P+'report.md')).write_text('\n'.join(lines),encoding='utf-8',newline='\n')
        manifest(end_pins,results)
        return
    gates=ex.read(P+'gates.json');assert gates['passed']
    records=[];C6=[];exploratory=[]
    for job in plan['jobs']:
        completion=ex.validate_completion(job)
        rows=ex.log_rows(completion['raw_log']);audit=ex.read(completion['audit_file'])
        assert len(rows)==completion['steps_completed']==len(audit['steps'])==len(audit['heartbeats'])
        assert [r['step'] for r in rows]==list(range(len(rows)))
        assert all(r['incumbent_calls']==1 for r in audit['steps'])
        count=sum(int(r['step']>=50 and r['g']>=plan['hazard']['g_star']) for r in rows)
        span=0;sustained=False;confirmation=None
        for row in rows:
            span=span+1 if row['step']>=50 and row['g']>=plan['hazard']['g_star'] else 0
            if span>=plan['hazard']['k']:
                sustained=True
                if confirmation is None:confirmation=row['step']
        final_population=rows[-1]['population']
        assert isinstance(final_population,int)
        entries={state:next((v['step'] for v in audit['transitions'] if v['to']==state),None) for state in ('VETO','CONSENSUS')}
        run={'job':job['job'],'arm':job['arm'],'defense_arm':job['defense_arm'],'seed':job['seed'],
             'steps_completed':len(rows),'end_reason':completion['end_reason'],'steps_ge_50_above_g_star':count,
             'sustained_hazard':sustained,'hazard_confirmation_step':confirmation,
             'veto_entry_step':entries['VETO'],'consensus_entry_step':entries['CONSENSUS'],'final_population':final_population,
             'recorded_steps':len(rows),'heartbeat_count':len(audit['heartbeats']),
             'raw_log':completion['raw_log'],'audit_file':completion['audit_file'],
             'defended_successor_commits_exploratory':sum(int(v['defended_successor_commit_exploratory']) for v in audit['steps'])}
        records.append(run)
        C6.append({'job':job['job'],'audit_file':completion['audit_file'],'sha256_lf':completion['audit_sha256_lf'],
                   'alarm_records':len(audit['alarms']),'transition_records':len(audit['transitions']),
                   'incumbent_action_records':len(audit['incumbent_actions'])})
        exploratory.append({k:run[k] for k in ('job','arm','defense_arm','seed','defended_successor_commits_exploratory')})
    assert len(records)==360
    C1=[];C2=[];C3=[];C4=[]
    for arm in plan['arms']:
        cells={d:[r for r in records if r['arm']==arm and r['defense_arm']==d] for d in plan['defenses']}
        assert all(len(v)==20 for v in cells.values())
        for treatment,control in [('OFF','VETO'),('OFF','GRADED'),('VETO','GRADED')]:
            value=paired_difference(cells[treatment],cells[control],'steps_ge_50_above_g_star')
            assert value['n_pairs']==20
            C1.append({'arm':arm,'contrast':treatment+' minus '+control,**value,'known_pathway_bias':BIAS})
        for defense,runs in cells.items():
            C2.append({'arm':arm,'defense_arm':defense,'runs':20,'sustained_hazard_runs':sum(int(r['sustained_hazard']) for r in runs)})
            C3.append({'arm':arm,'defense_arm':defense,'runs':20,
                       'entered_VETO':sum(r['veto_entry_step'] is not None for r in runs),
                       'VETO_entry_steps':stats([r['veto_entry_step'] for r in runs if r['veto_entry_step'] is not None]),
                       'entered_CONSENSUS':sum(r['consensus_entry_step'] is not None for r in runs),
                       'CONSENSUS_entry_steps':stats([r['consensus_entry_step'] for r in runs if r['consensus_entry_step'] is not None])})
        for defense in ('VETO','GRADED'):
            value=paired_difference(cells['OFF'],cells[defense],'final_population')
            assert value['n_pairs']==20
            C4.append({'arm':arm,'contrast':'OFF minus '+defense,**value,'known_pathway_bias':BIAS})
    C5={'runs':360,'matching_runs':sum(r['recorded_steps']==r['steps_completed'] for r in records),'mismatches':[]}
    execution=ex.read(P+'batch_execution.json')
    results={'status':'COMPLETE','registered':{'C1':C1,'C2':C2,'C3':C3,'C4':C4,'C5':C5,'C6':C6},
             'exploratory':exploratory,'known_pathway_bias':BIAS,'head':plan['head'],
             'worker_counts':execution,'resumed_seeds':execution['resumed'],'source_pins_end':end_pins}
    ex.csv_output(P+'runs.csv',records,list(records[0]))
    ex.write(P+'results.json',results)
    lines=['# In-loop drift defense: containment evaluation','',
           'This is a containment evaluation of named pathways under a named defense. It is not the published consensus override, not a change to production code, and not a correction of any published figure. No ratio of two measured counts was computed. The Section 8 interpretation is reserved for the operator.','',
           BIAS,'','## C1. Primary paired count of steps past the threshold','',BIAS,'']
    pair_headers=['Arm','Contrast','Pairs','Mean difference','Paired standard error','t statistic','Known-pathway qualification']
    def pair_rows(items):
        return [[v['arm'],v['contrast'],v['n_pairs'],repr(v['mean_difference']),repr(v['paired_standard_error']),
                 'undefined (zero standard error)' if v['t_statistic'] is None else repr(v['t_statistic']),BIAS] for v in items]
    table(lines,pair_headers,pair_rows(C1))
    lines.extend(['## C2. Sustained hazard counts','',BIAS,''])
    table(lines,['Arm','Defense','Runs','Runs with registered sustained hazard'],[[r['arm'],r['defense_arm'],r['runs'],r['sustained_hazard_runs']] for r in C2])
    lines.extend(['## C3. Intervention counts and entry steps','',BIAS,''])
    table(lines,['Arm','Defense','Entered VETO','VETO min, median, max','Entered CONSENSUS','CONSENSUS min, median, max'],
          [[r['arm'],r['defense_arm'],r['entered_VETO'],list(r['VETO_entry_steps'].values()),r['entered_CONSENSUS'],list(r['CONSENSUS_entry_steps'].values())] for r in C3])
    lines.extend(['## C4. Paired final population counts','',BIAS,''])
    table(lines,pair_headers,pair_rows(C4))
    lines.extend(['## C5. Liveness','',json.dumps(C5),'','## C6. Auditability','',
                  'Every run has a per-step CSV and per-run audit JSON, named and hashed in the results and manifest. Audit records include every alarm, every state transition with its effective step, incumbent replacement actions, committed snapshots, heartbeat statistics, and incumbent call counts. Production bindings were restored and verified by identity in every run.','',
                  '## Exploratory: ratified successor commits during defense','',
                  'These are exploratory counts, not registered results.',''])
    table(lines,['Arm','Defense','Seed','Exploratory count'],[[r['arm'],r['defense_arm'],r['seed'],r['defended_successor_commits_exploratory']] for r in exploratory])
    lines.extend(['## Gate evidence','',
                  'All nine gates and the additional incumbent-call gate passed. Full measured evidence is in '+P+'gates.json and the gate artifacts enumerated in the manifest.','',
                  'Online equivalence covered M1 and R10 under OFF, VETO and GRADED. Wrapper identity covered M1 and H. The no-oracle synthetic gate reached all three states and checked the pinned consensus fields bitwise.','',
                  '## Source pins',''])
    lines.extend(['Measured gate evidence:', '', chr(96)*3+'json', json.dumps(gates,indent=2), chr(96)*3, ''])
    table(lines,['Path','Start committed SHA256 (LF)','Start working-tree SHA256 (LF)','End committed SHA256 (LF)','End working-tree SHA256 (LF)'],
          [[r['path'],r['start_blob_sha256_lf'],r['start_worktree_sha256_lf'],r['end_blob_sha256_lf'],r['end_worktree_sha256_lf']] for r in end_pins])
    lines.extend(['## Execution provenance','',
                  'Machine: '+str(os.environ.get('COMPUTERNAME'))+'. HEAD: '+plan['head']+'.',
                  'Python: '+sys.version+'. NumPy: '+np.__version__+'.',
                  'Numerical-library threads were fixed to one and verified in every worker. The configured normal cap was 15 and work cap was 12, with runtime control in '+P+'control.json.',
                  'Maximum batch concurrency: '+str(execution['maximum_concurrent_workers'])+'.',
                  'Resumed seeds: '+json.dumps(execution['resumed'])+'.',
                  'Tool-layer workarounds: '+json.dumps(plan['tool_layer_workarounds'])+'.',
                  'T0 stderr warnings: '+json.dumps(plan['T0_stderr_warnings'])+'.',
                  'Known CRLF working-tree and LF blob condition was left unchanged.',
                  'Every bounded permission-error retry is recorded in the manifest and per-process I/O event files.',''])
    text='\n'.join(lines)
    assert chr(0x2014) not in text
    (OUT/(P+'report.md')).write_text(text,encoding='utf-8',newline='\n')
    manifest(end_pins,results)

if __name__=='__main__':
    try:main()
    except BaseException as error:
        ex.mark_halt('analysis',error)
        raise
