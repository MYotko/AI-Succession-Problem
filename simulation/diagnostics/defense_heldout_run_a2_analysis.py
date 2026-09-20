"""Compute registered held-out quantities, or record a pre-execution halt."""
import sys
sys.dont_write_bytecode=True
import defense_heldout_run_a2_executor as ex
import csv,json,io,statistics
from pathlib import Path
from attack_metrics_v2 import paired_difference

P=ex.P
OUT=ex.OUT
BIAS='Known-pathway design; constants calibrated on the drift mapping construction.'
DIRECTION={'Y1':'Positive: defended final population is lower.',
           'Y2':'Negative: defended time past the threshold is greater.',
           'Y3':'Negative: defended shock loss is larger.'}

def stats(values):
    return {'minimum':min(values) if values else None,
            'median':statistics.median(values) if values else None,
            'maximum':max(values) if values else None}

def pair(off,graded,field):
    for row in off+graded:assert type(row[field]) is int,(field,row[field])
    if len(off)<2:
        return {'n_pairs':len(off),'mean_difference':None,'paired_standard_error':None,
                't_statistic':None,'t_statistic_note':'Fewer than two defined pairs.'}
    return paired_difference(off,graded,field)

def fixture_criterion(quantity,value):
    t=value['t_statistic'];mean=value['mean_difference']
    if t is None:return False
    if quantity=='Y1':return mean>0 and t>=2.0
    return mean<0 and t<=-2.0

def sign_fixture():
    off=[];graded=[]
    for seed in range(4):
        off.append({'seed':seed,'final_population':1000,'g_steps':10,'shock_loss':5})
        graded.append({'seed':seed,'final_population':900-seed,'g_steps':20+seed,'shock_loss':15+seed})
    result={}
    for q,field in [('Y1','final_population'),('Y2','g_steps'),('Y3','shock_loss')]:
        value=pair(off,graded,field)
        passed=fixture_criterion(q,value)
        result[q]={'paired_value':value,'harm_direction':DIRECTION[q],
                   'fixture_labeled_harm':passed}
        assert passed,('Sign fixture failed',q,value)
    return {'passed':True,'synthetic_off':off,'synthetic_graded':graded,'quantities':result}

def observations():
    summaries=[]
    with (OUT/(P+'completions.jsonl')).open(encoding='utf-8') as stream:
        summaries=[json.loads(line) for line in stream]
    grouped={}
    with (OUT/(P+'steps.csv')).open(encoding='utf-8',newline='') as stream:
        for raw in csv.DictReader(stream):
            row={k:ex.parsed(v) for k,v in raw.items()}
            grouped.setdefault((row['arm'],row['defense_arm'],row['seed']),[]).append(row)
    result=[]
    for c in summaries:
        rows=grouped.pop((c['arm'],c['defense_arm'],c['seed']))
        audit=ex.read(c['audit_file'])
        assert len(rows)==c['steps_completed']==len(audit['heartbeats'])
        assert ex.sha(ex.lf((OUT/c['audit_file']).read_bytes()))==c['audit_sha256_lf']
        assert [r['step'] for r in rows]==list(range(len(rows)))
        first={name:next((a['step'] for a in audit['alarms'] if a['channel']==name),None) for name in ('entropy','g','A')}
        baseline=rows[49]['resilience_stock'] if len(rows)>49 else None
        depletion=next((r['step'] for r in rows if baseline is not None and r['resilience_stock']<0.5*baseline),None)
        loss=rows[149]['population']-rows[160]['population'] if len(rows)>160 else None
        transitions=audit['transitions']
        resilience=[]
        for action in audit['incumbent_actions']:
            if action['applied_action'] is not None:
                resilience.append({'step':action['step'],'state':action['state'],
                                   'x_resilience':action['applied_action']['x_resilience']})
        result.append({'arm':c['arm'],'defense_arm':c['defense_arm'],'seed':c['seed'],
                       'steps_completed':len(rows),'last_completed_step':rows[-1]['step'],
                       'end_reason':c['end_reason'],'final_population':rows[-1]['population'],
                       'g_steps':sum(r['step']>=50 and r['g']>=1.0965735902799727 for r in rows),
                       'population_step_149':rows[149]['population'] if len(rows)>149 else None,
                       'population_step_160':rows[160]['population'] if len(rows)>160 else None,
                       'shock_loss':loss,'first_alarm_steps':first,
                       'resilience_stock_step_49':baseline,'depletion_step':depletion,
                       'alarm_minus_depletion':{k:(v-depletion if v is not None and depletion is not None else None) for k,v in first.items()},
                       'no_alarm_before_150':not any(a['step']<150 for a in audit['alarms']),
                       'VETO_entry_step':next((t['step'] for t in transitions if t['to']=='VETO'),None),
                       'CONSENSUS_entry_step':next((t['step'] for t in transitions if t['to']=='CONSENSUS'),None),
                       'held_action_attack_modified':any(t.get('held_action_attack_modified',False) for t in transitions if t['to']=='VETO'),
                       'imposed_resilience':resilience,'audit_file':c['audit_file'],
                       'recorded_steps_equal_completed':len(rows)==c['steps_completed'],
                       'elapsed_seconds':c['elapsed_seconds']})
    assert len(result)==160 and not grouped
    return result,summaries

def calculate(runs):
    r={q:{} for q in ('Y1','Y2','Y3','Y4','Y5')}
    for arm in ex.ARMS:
        off=[x for x in runs if x['arm']==arm and x['defense_arm']=='OFF']
        graded=[x for x in runs if x['arm']==arm and x['defense_arm']=='GRADED']
        assert len(off)==len(graded)==20
        for q,field in [('Y1','final_population'),('Y2','g_steps')]:
            r[q][arm]={'harm_direction':DIRECTION[q],'paired':pair(off,graded,field),'bias':BIAS}
        defined={x['seed'] for x in off if x['shock_loss'] is not None}&{x['seed'] for x in graded if x['shock_loss'] is not None}
        r['Y3'][arm]={'harm_direction':DIRECTION['Y3'],
                     'paired':pair([x for x in off if x['seed'] in defined],
                                   [x for x in graded if x['seed'] in defined],'shock_loss'),
                     'undefined_pair_count':20-len(defined),
                     'undefined_pair_seeds':[s for s in range(1835087800,1835087820) if s not in defined],
                     'bias':BIAS}
        for q in r:r[q].setdefault(arm,{}).setdefault('cells',{})
        for defense,cell in [('OFF',off),('GRADED',graded)]:
            r['Y1'][arm]['cells'][defense]={'n_runs':len(cell),'extinction_count':sum(x['end_reason']=='extinction' for x in cell),'bias':BIAS}
            r['Y2'][arm]['cells'][defense]={'per_run_counts':[{'seed':x['seed'],'g_steps':x['g_steps']} for x in cell]}
            r['Y3'][arm]['cells'][defense]={'runs':[{'seed':x['seed'],'shock_loss':x['shock_loss'],'last_completed_step':x['last_completed_step']} for x in cell]}
            r['Y4'][arm]['cells'][defense]={'n_runs':len(cell),'no_alarm_before_150_count':sum(x['no_alarm_before_150'] for x in cell),'bias':BIAS,
                'runs':[{k:x[k] for k in ('seed','first_alarm_steps','resilience_stock_step_49','depletion_step','alarm_minus_depletion')} for x in cell]}
            value={'n_runs':len(cell),'held_action_attack_modified_count':sum(x['held_action_attack_modified'] for x in cell),'bias':BIAS}
            for state in ('VETO','CONSENSUS'):
                entries=[x[state+'_entry_step'] for x in cell if x[state+'_entry_step'] is not None]
                value[state]={'run_count':len(entries),'entry_steps':stats(entries),
                              'imposed_resilience_shares':sorted({a['x_resilience'] for x in cell for a in x['imposed_resilience'] if a['state']==state})}
            value['runs']=[{k:x[k] for k in ('seed','VETO_entry_step','CONSENSUS_entry_step','imposed_resilience','audit_file')} for x in cell]
            r['Y5'][arm]['cells'][defense]=value
    predictions={}
    count=r['Y4']['A1-low']['cells']['OFF']['no_alarm_before_150_count']
    predictions['1']={'number':count,'threshold':15,'comparison':'>=','meets_numeric_threshold':count>=15,'bias':BIAS}
    predictions['2']={}
    for arm in ('A1-low','A1-high'):
        predictions['2'][arm]={}
        for q in ('Y1','Y2'):
            t=r[q][arm]['paired']['t_statistic']
            predictions['2'][arm][q]={'t':t,'absolute_t_threshold':2.0,
                'meets_numeric_threshold':None if t is None else abs(t)<=2.0,'bias':BIAS}
    count=r['Y5']['A2']['cells']['GRADED']['CONSENSUS']['run_count']
    predictions['3']={'number':count,'threshold':18,'comparison':'>=','meets_numeric_threshold':count>=18,'bias':BIAS}
    value=r['Y1']['A2']['paired'];t=value['t_statistic']
    predictions['4']={'mean_difference':value['mean_difference'],'t':t,'t_threshold':2.0,
                      'meets_numeric_threshold':None if t is None else value['mean_difference']>0 and t>=2.0,'bias':BIAS}
    return r,predictions

def report_complete(results,runs):
    lines=['# Held-out attacks, attempt 2','',
       'This is gate 2 of the promotion plan. The attacks were specified before any run.',
       'This is not a promotion decision. It does not test input corruption, which the note defers to stage B.',
       'No ratio of two measured counts was computed. Applying the Section 6 criterion and the Section 8 interpretation is reserved for the operator.',
       'Attempt 1 halted before T1 with zero runs launched. Amendment 1 fixes the Y3 harm direction; this dispatch permits only numeric prediction checks.','']
    r=results['registered']
    for q in ('Y1','Y2','Y3','Y4','Y5'):
        lines+=['## '+q,'']
        if q in DIRECTION:
            lines +=[DIRECTION[q], '', '| Arm | Pairs | Mean OFF minus GRADED | Paired standard error | t | Harm direction | Basis |',
                     '| --- | ---: | ---: | ---: | ---: | --- | --- |']
            for arm in ex.ARMS:
                p=r[q][arm]['paired']
                lines.append('| '+ ' | '.join(map(str,[arm,p['n_pairs'],p['mean_difference'],p['paired_standard_error'],
                      'undefined' if p['t_statistic'] is None else p['t_statistic'],DIRECTION[q],BIAS]))+' |')
        else:lines+=['Harm direction: no directional paired harm quantity is defined for '+q+'.','']
        if q=='Y1':
            lines+=['','| Arm | Defense | Runs | Extinctions | Basis |','| --- | --- | ---: | ---: | --- |']
            for arm in ex.ARMS:
                for d,c in r[q][arm]['cells'].items():lines.append(f"| {arm} | {d} | {c['n_runs']} | {c['extinction_count']} | {BIAS} |")
        if q=='Y3':
            lines+=['','| Arm | Undefined pairs |','| --- | ---: |']
            for arm in ex.ARMS:lines.append(f"| {arm} | {r[q][arm]['undefined_pair_count']} |")
            lines+=['','| Arm | Defense | Seed | Last step | Shock loss | Harm direction |','| --- | --- | ---: | ---: | ---: | --- |']
            for x in runs:lines.append(f"| {x['arm']} | {x['defense_arm']} | {x['seed']} | {x['last_completed_step']} | {x['shock_loss']} | {DIRECTION[q]} |")
        if q=='Y4':
            lines+=['','Lead is alarm step minus depletion step. Null indicates an undefined value.','',
              '| Arm | Defense | Runs without alarm before 150 | Basis |','| --- | --- | ---: | --- |']
            for arm in ex.ARMS:
                for d,c in r[q][arm]['cells'].items():lines.append(f"| {arm} | {d} | {c['no_alarm_before_150_count']} | {BIAS} |")
            lines+=['','| Arm | Defense | Seed | Entropy alarm | g alarm | A alarm | Depletion | Entropy lead | g lead | A lead |','| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
            for x in runs:
                vals=[x['arm'],x['defense_arm'],x['seed']]+[x['first_alarm_steps'][c] for c in ('entropy','g','A')]+[x['depletion_step']]+[x['alarm_minus_depletion'][c] for c in ('entropy','g','A')]
                lines.append('| '+' | '.join('null' if v is None else str(v) for v in vals)+' |')
        if q=='Y5':
            lines+=['','| Arm | Defense | State | Runs | Entry min | Median | Max | Imposed resilience shares | Basis |','| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |']
            for arm in ex.ARMS:
                for d,c in r[q][arm]['cells'].items():
                    for state in ('VETO','CONSENSUS'):
                        v=c[state];s=v['entry_steps']
                        lines.append('| '+' | '.join(map(str,[arm,d,state,v['run_count'],s['minimum'],s['median'],s['maximum'],v['imposed_resilience_shares'],BIAS]))+' |')
            lines+=['','Every per-run alarm, transition, applied action, and imposed resilience share is in the referenced audit files and results JSON.',
                    'Recorded steps equal completed steps in every run: '+str(all(x['recorded_steps_equal_completed'] for x in runs))+'.']
        lines.append('')
    lines+=['## Sign fixture','','Assertion passed: '+str(results['sign_fixture']['passed'])+'.',
             'The synthetic defended arm has lower final population, more steps past the threshold, and greater shock loss.',
             'Its criterion labels Y1 positive, Y2 negative, and Y3 negative as harm.','',
             '## Registered prediction numeric checks','',BIAS,'']
    for key,value in results['prediction_numeric_checks'].items():
        lines+=['Prediction '+key+': '+json.dumps(value,sort_keys=True), '']
    return lines

def finalize(results,lines,summaries):
    import numpy as np
    ending=ex.pins(full=True)
    plan=ex.read(P+'plan.json');preflight=ex.read(P+'preflight.json')
    lines+=['## Source verification','','| Path | Start blob | Start working tree | Completion blob | Completion working tree |',
            '| --- | --- | --- | --- | --- |']
    for p in ending:
        lines.append('| '+' | '.join([p['path'],p['committed_sha256_lf'],p['working_tree_sha256_lf'],p['end_blob_sha256_lf'],p['end_worktree_sha256_lf']])+' |')
    lines+=['','## Execution evidence','',
            'HEAD: '+plan['head'], 'Machine: '+str(ex.os.environ.get('COMPUTERNAME')),
            'Python: '+sys.version.replace('\n',' '),'NumPy: '+np.__version__,'',
            'No source pin changed. No completed run was rerun.','',
            'Tool-layer workarounds:']+plan['tool_layer_workarounds']+['','T0 stderr warnings:']
    lines += [w['stderr'].rstrip() for w in preflight['stderr_warnings']]
    runtime=ex.metadata(np)
    executions=[ex.read(p.name) for p in sorted(OUT.glob(P+'*_execution.json'))]
    retries=[]
    for path in sorted(OUT.glob(P+'io_events_*.jsonl')):
        with path.open(encoding='utf-8') as stream:retries.extend(json.loads(line) for line in stream)
    resumes=[r for e in executions for r in e.get('resumed',[])]
    lines+=['','Worker execution metadata: '+json.dumps(executions,sort_keys=True),
            'Resumed runs: '+json.dumps(resumes,sort_keys=True),
            'Permission retry events: '+json.dumps(retries,sort_keys=True),'']
    ex.write(P+'results.json',results)
    report='\n'.join(lines)
    assert chr(0x2014) not in report
    with (OUT/(P+'report.md')).open('w',encoding='utf-8',newline='\n') as stream:
        stream.write(report);stream.flush();ex.os.fsync(stream.fileno())
    outputs=[]
    for path in sorted(OUT.glob(P+'*')):
        if not path.is_file() or path.name==P+'manifest.json':continue
        rows=None;jsonl_rows=None
        if path.suffix=='.csv':
            with path.open(encoding='utf-8',newline='') as stream:rows=sum(1 for _ in csv.DictReader(stream))
        if path.suffix=='.jsonl':
            with path.open(encoding='utf-8') as stream:jsonl_rows=sum(1 for line in stream if line.strip())
        outputs.append({'path':path.relative_to(ex.ROOT).as_posix(),'sha256_lf':ex.sha(ex.lf(path.read_bytes())),
                        'hash_basis':'LF-normalized bytes','csv_row_count':rows,'jsonl_row_count':jsonl_rows})
    merge=ex.read(P+'merge.json') if (OUT/(P+'merge.json')).exists() else {
        'status':'NOT_RUN','merged_files':[],'per_run':[],
        'deleted_file_counts':{k:0 for k in ('step_logs','completion_records','progress','initial','console')}}
    ex.write(P+'manifest.json',{'status':results['status'],'head':plan['head'],'runtime':runtime,
             'outputs':outputs,'manifest_self_hash':'Excluded to avoid a recursive self-hash.',
             'source_readings':ending,'committed_blob_sha1':{p['path']:p['committed_blob_sha1'] for p in plan['pins']},
             'copied_sources':plan['copied_sources'],'code_identity':ex.identity(),
             'operational_retry_layer_sha256_lf':ex.identity()[P+'executor.py'],
             'operational_retry_layer_basis':'LF-normalized executor bytes',
             'per_module_sha256':runtime['modules'],'worker_executions':executions,
             'worker_limits':{'normal':15,'work':12,'operator_cpu_budget':16},
             'numerical_threads_per_worker':1,'worker_runtime_evidence':{
                 c['job']:c['runtime'] for c in summaries},
             'resumed_runs':resumes,'retry_events':retries,
             'tool_layer_workarounds':plan['tool_layer_workarounds'],
             'T0_stderr_warnings':preflight['stderr_warnings'],'merge':merge})

def main():
    if '--halt' in sys.argv:
        failures=[ex.read(p.name) for p in sorted(OUT.glob(P+'failure_*.json'))]
        results={'status':'HALTED','runs_planned':160,
                 'batch_runs_completed':len(list(OUT.glob(P+'run_*_complete.json'))),
                 'failures':failures,'registered':{q:None for q in ('Y1','Y2','Y3','Y4','Y5')},
                 'sign_fixture':{'status':'NOT_RUN'}}
        lines=['# Held-out attacks, attempt 2: halt','',
               'This is gate 2 of the promotion plan. The attacks were specified before any run.',
               'It is not a promotion decision and does not test input corruption, deferred to stage B.',
               'No ratio of two measured counts was computed. The Section 6 criterion and Section 8 interpretation are reserved for the operator.','',
               'Attempt 1 halted before T1. Amendment 1 changed Y3 harm to negative.','',
               'Status: HALTED. Registered quantities Y1 through Y5 were not computed.',
               'Sign fixture: not run because execution halted before analysis.','',
               'Halt evidence: '+json.dumps(failures,sort_keys=True)]
        summaries=[ex.read(p.name) for p in OUT.glob(P+'gate_*_result.json')]
        for name in ('constants_gate.json','no_oracle_gate.json','gates.json','attack_effect_gate.json','burst_gate.json'):
            if (OUT/(P+name)).exists():
                value=ex.read(P+name)
                if name=='attack_effect_gate.json':value={k:v for k,v in value.items() if k!='comparisons'}
                lines+=['',name+': '+json.dumps(value,sort_keys=True)]
        finalize(results,lines,summaries)
        return
    fixture=sign_fixture()
    runs,summaries=observations()
    registered,predictions=calculate(runs)
    results={'status':'COMPLETE','runs':len(runs),'registered':registered,
             'sign_fixture':fixture,'prediction_numeric_checks':predictions,
             'criterion_applied_to_experimental_results':False}
    flat=[]
    for row in runs:
        value={k:v for k,v in row.items() if k not in ('imposed_resilience','first_alarm_steps','alarm_minus_depletion')}
        value.update({name+'_first_alarm_step':row['first_alarm_steps'][name] for name in ('entropy','g','A')})
        value.update({name+'_alarm_minus_depletion':row['alarm_minus_depletion'][name] for name in ('entropy','g','A')})
        value['imposed_resilience_audit']=row['audit_file']
        flat.append(value)
    ex.csv_output(P+'runs.csv',flat,list(flat[0]))
    finalize(results,report_complete(results,runs),summaries)

if __name__=='__main__':
    try:main()
    except BaseException as error:
        ex.mark_halt('analysis',error)
        if '--halt' not in sys.argv:
            sys.argv.append('--halt')
            main()
        raise SystemExit(2)
