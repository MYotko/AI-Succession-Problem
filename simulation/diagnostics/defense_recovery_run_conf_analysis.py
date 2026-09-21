"""Compute the registered recovery counts without selecting a quiet period."""
import sys
sys.dont_write_bytecode=True
import defense_recovery_run_conf_executor as ex
import csv,json,io,statistics
from pathlib import Path
from attack_metrics_v2 import paired_difference
P=ex.P
OUT=ex.OUT
BIAS='Known-pathway design; constants calibrated on the drift mapping construction.'
DIRECTION={'R1':'Negative: the recovered arm spent more steps past the threshold.',
           'R2':'Positive: the recovered arm ended with fewer people.'}
TRANSITIONS=('NORMAL_to_VETO','VETO_to_CONSENSUS','CONSENSUS_to_VETO','VETO_to_NORMAL')
def stats(values):
    return {'minimum':min(values) if values else None,
            'median':statistics.median(values) if values else None,
            'maximum':max(values) if values else None}
def pair(first,second,field):
    for row in first+second:assert type(row[field]) is int,(field,row[field])
    return paired_difference(first,second,field)
def fixture_criterion(quantity,value):
    t=value['t_statistic'];mean=value['mean_difference']
    if t is None:return False
    if quantity=='R1':return mean<0 and t<=-2.0
    return mean>0 and t>=2.0
def sign_fixture():
    latched=[];recovered=[]
    for seed in range(4):
        latched.append({'seed':seed,'final_population':1000,'g_steps':10})
        recovered.append({'seed':seed,'final_population':900-seed,'g_steps':20+seed})
    result={}
    for q,field in [('R1','g_steps'),('R2','final_population')]:
        value=pair(latched,recovered,field)
        passed=fixture_criterion(q,value)
        result[q]={'paired_value':value,'harm_direction':DIRECTION[q],'fixture_labeled_harm':passed}
        assert passed,('Sign fixture failed',q,value)
    return {'passed':True,'synthetic_latched':latched,'synthetic_recovered':recovered,'quantities':result}
def attack_validity():
    groups={'H':[],'A3':[]}
    with (OUT/(P+'steps.csv')).open(encoding='utf-8',newline='') as stream:
        for row in csv.DictReader(stream):
            if row['defense_arm']!='OFF' or row['step']!='149' or row['arm'] not in groups:continue
            groups[row['arm']].append({'seed':int(row['seed']),'resilience_stock':float(row['resilience_stock'])})
    for rows in groups.values():
        assert sorted(r['seed'] for r in rows)==list(range(1835088100,1835088120))
    result={'contrast':'H OFF minus A3 OFF','step':149,
            'H_median_stock':statistics.median(r['resilience_stock'] for r in groups['H']),
            'A3_median_stock':statistics.median(r['resilience_stock'] for r in groups['A3']),
            'paired':paired_difference(groups['H'],groups['A3'],'resilience_stock'),
            'per_run_stock':groups,'validity_ruling':None,'bias':BIAS}
    ex.write(P+'attack_validity.json',result)
    return result
def observations():
    with (OUT/(P+'completions.jsonl')).open(encoding='utf-8') as stream:
        summaries=[json.loads(line) for line in stream]
    grouped={}
    with (OUT/(P+'steps.csv')).open(encoding='utf-8',newline='') as stream:
        for raw in csv.DictReader(stream):
            row={k:ex.parsed(v) for k,v in raw.items()}
            grouped.setdefault((row['arm'],row['defense_arm'],row['seed']),[]).append(row)
    runs=[]
    for completion in summaries:
        rows=grouped.pop((completion['arm'],completion['defense_arm'],completion['seed']))
        audit=ex.read(completion['audit_file'])
        assert ex.sha(ex.lf((OUT/completion['audit_file']).read_bytes()))==completion['audit_sha256_lf']
        assert len(rows)==completion['steps_completed']==len(audit['heartbeats'])==len(audit['steps'])
        assert [row['step'] for row in rows]==list(range(len(rows)))
        transitions=audit['transitions']
        counts={name:sum(t['from']+'_to_'+t['to']==name for t in transitions) for name in TRANSITIONS}
        counts['re_escalations_after_recovery']=sum(t['re_escalation_after_recovery'] for t in transitions)
        states=audit['steps']
        first_normal=next((s['step'] for s in states if s['step']>=150 and s['state_after_step']=='NORMAL'),None)
        row={'arm':completion['arm'],'defense_arm':completion['defense_arm'],'seed':completion['seed'],
             'steps_completed':len(rows),'last_completed_step':rows[-1]['step'],
             'end_reason':completion['end_reason'],'final_population':rows[-1]['population'],
             'g_steps':sum(r['step']>=50 and r['g']>=1.0965735902799727 for r in rows),
             'VETO_steps':sum(s['state_in_force']=='VETO' for s in states),
             'CONSENSUS_steps':sum(s['state_in_force']=='CONSENSUS' for s in states),
             'non_NORMAL_steps':sum(s['state_in_force']!='NORMAL' for s in states),
             'state_after_last_completed_step':states[-1]['state_after_step'],
             'state_in_force_at_last_step':states[-1]['state_in_force'],
             'transition_counts':counts,
             'H_first_NORMAL_step_at_or_after_shock':first_normal if completion['arm']=='H' else None,
             'H_steps_from_shock_to_NORMAL':(first_normal-150 if first_normal is not None else None) if completion['arm']=='H' else None,
             'H_never_returned_to_NORMAL':first_normal is None if completion['arm']=='H' else None,
             'normal_at_shock_completion':next((s['state_after_step']=='NORMAL' for s in states if s['step']==150),None),
             'audit_file':completion['audit_file'],'audit_sha256_lf':completion['audit_sha256_lf'],
             'recorded_steps_equal_completed':True,'binding_restored_by_identity':completion['binding_restored_by_identity'],
             'attack_binding_restored_by_identity':completion['attack_binding_restored_by_identity'],
             'elapsed_seconds':completion['elapsed_seconds']}
        assert row['VETO_steps']+row['CONSENSUS_steps']==row['non_NORMAL_steps']
        runs.append(row)
    assert len(runs)==180 and not grouped
    return runs,summaries
def calculate(runs):
    result={q:{} for q in ('R1','R2','R3','R4','R5','R6')}
    for arm in ex.ARMS:
        cells={d:[r for r in runs if r['arm']==arm and r['defense_arm']==d] for d in ex.DEFENSE_ARMS}
        for cell in cells.values():
            assert sorted(r['seed'] for r in cell)==list(range(1835088100,1835088120))
        for q,field in [('R1','g_steps'),('R2','final_population')]:
            contrasts={}
            for first,second in [('LATCHED',d) for d in ex.DEFENSE_ARMS if d.startswith('RECOVER-')]+[('OFF',d) for d in ex.DEFENSE_ARMS if d!='OFF']:
                contrasts[first+'_minus_'+second]={'paired':pair(cells[first],cells[second],field),
                    'harm_direction':DIRECTION[q],'bias':BIAS}
            result[q][arm]={'contrasts':contrasts,'cells':{}}
        for d,cell in cells.items():
            result['R1'][arm]['cells'][d]={'runs':[{'seed':r['seed'],'g_steps':r['g_steps']} for r in cell]}
            result['R2'][arm]['cells'][d]={'n_runs':len(cell),'extinction_count':sum(r['end_reason']=='extinction' for r in cell),
                'runs':[{'seed':r['seed'],'final_population':r['final_population'],'end_reason':r['end_reason']} for r in cell],'bias':BIAS}
            result['R3'].setdefault(arm,{})[d]={'n_runs':len(cell),'non_NORMAL_at_last_completed_step_count':sum(r['state_after_last_completed_step']!='NORMAL' for r in cell),
                'VETO_steps_total':sum(r['VETO_steps'] for r in cell),'CONSENSUS_steps_total':sum(r['CONSENSUS_steps'] for r in cell),
                'runs':[{k:r[k] for k in ('seed','VETO_steps','CONSENSUS_steps','non_NORMAL_steps','state_after_last_completed_step')} for r in cell],'bias':BIAS}
            result['R4'].setdefault(arm,{})[d]={'counts':{name:stats([r['transition_counts'][name] for r in cell]) for name in TRANSITIONS+('re_escalations_after_recovery',)},
                'runs':[{'seed':r['seed'],**r['transition_counts']} for r in cell],'bias':BIAS}
            if arm=='H':
                result['R5'][d]={'never_return_count':sum(r['H_never_returned_to_NORMAL'] for r in cell),
                    'latency_steps':stats([r['H_steps_from_shock_to_NORMAL'] for r in cell if r['H_steps_from_shock_to_NORMAL'] is not None]),
                    'runs':[{k:r[k] for k in ('seed','H_first_NORMAL_step_at_or_after_shock','H_steps_from_shock_to_NORMAL','H_never_returned_to_NORMAL','normal_at_shock_completion','last_completed_step')} for r in cell],
                    'definition':'First post-update NORMAL state at or after step 150 minus 150; zero when already NORMAL at step 150; undefined when no return is observed.',
                    'bias':BIAS}
    result['R6']={'runs':len(runs),'recorded_steps':sum(r['steps_completed'] for r in runs),
        'recorded_steps_equal_completed_in_every_run':all(r['recorded_steps_equal_completed'] for r in runs),
        'audits':[{k:r[k] for k in ('arm','defense_arm','seed','steps_completed','audit_file','audit_sha256_lf','binding_restored_by_identity','attack_binding_restored_by_identity')} for r in runs]}
    return result

def confirmation_arithmetic(registered):
    comparisons={}
    for arm in ex.ARMS:
        comparisons[arm]={}
        for q in ('R1','R2'):
            value=registered[q][arm]['contrasts']['LATCHED_minus_RECOVER-20']['paired']
            t=value['t_statistic']
            harm=None if t is None else fixture_criterion(q,value)
            comparisons[arm][q]={
                'contrast':'LATCHED minus RECOVER-20','paired':value,
                'harm_direction':DIRECTION[q],
                'harm_comparison':'t <= -2.0' if q=='R1' else 't >= 2.0',
                'harm_threshold_reached':harm,
                'selection_condition_holds':None if harm is None else not harm,
                'undefined_note':'Paired t is undefined; no numerical comparison is made.' if t is None else None,
                'bias':BIAS}
    return {'per_attack_arm':comparisons,
            'H_non_NORMAL_at_last_completed_step_counts':{
                d:registered['R3']['H'][d]['non_NORMAL_at_last_completed_step_count']
                for d in ('LATCHED','RECOVER-20')},
            'adoption_ruling':None,'parameter_selected':None,
            'basis':'Arithmetic comparisons only; adoption remains reserved for the operator.'}

def report_complete(results,runs):
    lines=['# In-loop drift defense, gate 3: recovery confirmation, quiet period 20','',
           'This is gate 3 of the promotion plan. The recovery rule, its three quiet periods, the selection rule and the criterion were fixed before any run.',
           'This is not a promotion decision and selects no parameter. No ratio of two measured counts was computed.',
           'Applying the Section 6 selection rule and criterion and the Section 8 interpretation is reserved for the operator.','']
    r=results['registered']
    def table(headers,rows):
        lines.append('| '+' | '.join(headers)+' |')
        lines.append('| '+' | '.join('---' for _ in headers)+' |')
        for row in rows:lines.append('| '+' | '.join('undefined' if v is None else str(v) for v in row)+' |')
        lines.append('')
    for q in ('R1','R2'):
        lines+=['## '+q,'',DIRECTION[q],'']
        values=[]
        for arm in ex.ARMS:
            for contrast,value in r[q][arm]['contrasts'].items():
                p=value['paired'];values.append([arm,contrast,p['n_pairs'],p['mean_difference'],p['paired_standard_error'],p['t_statistic'],DIRECTION[q],BIAS])
        table(['Attack','Contrast','Pairs','Mean difference','Paired standard error','t','Harm direction','Basis'],values)
        values=[]
        for arm,c in results['confirmation_arithmetic']['per_attack_arm'].items():
            value=c[q];p=value['paired']
            values.append([arm,p['n_pairs'],p['mean_difference'],p['paired_standard_error'],
                           p['t_statistic'],value['harm_comparison'],value['harm_threshold_reached'],
                           value['selection_condition_holds'],BIAS])
        lines+=['Section 6 condition arithmetic for LATCHED minus RECOVER-20. Undefined t leaves the comparison undefined. No adoption ruling is made.','']
        table(['Attack','Pairs','Mean difference','Paired standard error','t','Harm threshold','Threshold reached','Selection condition holds','Basis'],values)
        if q=='R2':
            table(['Attack','Defense','Runs','Extinctions','Basis'],[[arm,d,v['n_runs'],v['extinction_count'],BIAS] for arm in ex.ARMS for d,v in r[q][arm]['cells'].items()])
    lines+=['## R3','','Counts with no harm direction. Steps use the state in force for that step; final state uses the state after the last completed step update.',
            'Per-run counts are retained in results.json and runs.csv.','']
    table(['Attack','Defense','VETO steps','CONSENSUS steps','Runs non-NORMAL at last completion','Basis'],
          [[arm,d,v['VETO_steps_total'],v['CONSENSUS_steps_total'],v['non_NORMAL_at_last_completed_step_count'],BIAS] for arm in ex.ARMS for d,v in r['R3'][arm].items()])
    lines+=['## R4','','No harm direction. Every transition is dated at its completed step and acts from the next step.',
            'Re-escalation counts each escalation after an earlier recovery transition. Per-run counts are retained in results.json and runs.csv.','']
    table(['Attack','Defense','Direction or count','Minimum','Median','Maximum','Basis'],
          [[arm,d,name,v['minimum'],v['median'],v['maximum'],BIAS] for arm in ex.ARMS for d,c in r['R4'][arm].items() for name,v in c['counts'].items()])
    lines+=['## R5','','H only. No harm direction. The first post-update NORMAL step at or after 150 minus 150 is the release latency.',
            'A run already NORMAL at shock completion has latency zero. A run with no observed return has undefined latency.','']
    table(['Defense','Never returned','Latency minimum','Median','Maximum','Basis'],
          [[d,v['never_return_count'],v['latency_steps']['minimum'],v['latency_steps']['median'],v['latency_steps']['maximum'],BIAS] for d,v in r['R5'].items()])
    table(['Defense','Seed','First NORMAL step at or after shock','Latency','Never returned'],
          [[x['defense_arm'],x['seed'],x['H_first_NORMAL_step_at_or_after_shock'],x['H_steps_from_shock_to_NORMAL'],x['H_never_returned_to_NORMAL']] for x in runs if x['arm']=='H'])
    lines+=['## R6','','No harm direction. Recorded steps equal completed steps in every run: '+str(r['R6']['recorded_steps_equal_completed_in_every_run'])+'.',
            'Runs: '+str(r['R6']['runs'])+'. Recorded steps: '+str(r['R6']['recorded_steps'])+'.',
            'Every alarm, state transition with its direction, and applied action is retained in the per-run audit referenced by results.json and runs.csv.','',
            '## Sign fixture','','Assertion passed: '+str(results['sign_fixture']['passed'])+'.',
            'The synthetic recovered arm is worse on both quantities. The fixture labels R1 negative and R2 positive as harm.','',
            '## Reduced attack-validity check','','Numbers only; no validity ruling. Resilience stock is a continuous value in this separately requested check.','']
    v=results['attack_validity'];p=v['paired']
    table(['H OFF median at 149','A3 OFF median at 149','Pairs','Mean H OFF minus A3 OFF','Paired standard error','t','Basis'],
          [[v['H_median_stock'],v['A3_median_stock'],p['n_pairs'],p['mean_difference'],p['paired_standard_error'],p['t_statistic'],BIAS]])
    lines+=['No exploratory analysis was performed.','']
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
    lines += ['', 'Executor fixes before any model run:'] + plan['executor_fixes']
    lines += ['', 'T1 numeric tolerance rules: '+json.dumps(plan['gate_tolerances'],sort_keys=True)]
    lines += ['', '## T1 evidence', '']
    if (OUT/(P+'gates.json')).exists():
        evidence=ex.read(P+'gates.json')
        for key,value in evidence.items():
            if key in ('source_pins_start','10_source_pins_end','runtime','3_attack_arithmetic'):continue
            lines += [key+': '+json.dumps(value,sort_keys=True), '']
    if (OUT/(P+'attack_arithmetic_gate.json')).exists():
        arithmetic=ex.read(P+'attack_arithmetic_gate.json')
        lines += ['Attack arithmetic evidence: '+P+'attack_arithmetic_gate.json',
                  'Full synthetic inputs, outputs, expected values and pre-onset outputs are retained in that file.', '',
                  '| Arm | Case | Resilience category | Moved | Maximum share error | Share sum | Constraints exact | Pre-onset exact | Passed |',
                  '| --- | ---: | --- | ---: | ---: | ---: | --- | --- | --- |']
        for c in arithmetic['cases']:
            fields=[c['arm'],c['case'],c['resilience_category'],c['moved'],
                    max(c['share_absolute_differences'].values()),c['share_sum'],
                    c['constraints_unchanged_exactly'],c['pre_onset_unchanged_exactly'],c['passed']]
            lines.append('| '+' | '.join(map(str,fields))+' |')
    if (OUT/(P+'attack_effect_gate.json')).exists():
        trajectory=ex.read(P+'attack_effect_gate.json')
        lines += ['', 'Trajectory evidence: '+json.dumps({k:v for k,v in trajectory.items() if k!='comparisons'},sort_keys=True)]
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
             'tool_layer_workarounds':plan['tool_layer_workarounds'],'executor_fixes':plan['executor_fixes'],
             'gate_tolerances':plan['gate_tolerances'],
             'T0_stderr_warnings':preflight['stderr_warnings'],'merge':merge})


def main():
    if '--halt' in sys.argv:
        failures=[ex.read(p.name) for p in sorted(OUT.glob(P+'failure_*.json'))]
        summaries=[ex.read(p.name) for p in sorted(OUT.glob(P+'gate_*_result.json'))]
        results={'status':'HALTED','runs_planned':180,
                 'batch_runs_completed':len(list(OUT.glob(P+'run_*_complete.json'))),
                 'gate_runs_completed':len(summaries),'failures':failures,
                 'registered':{q:None for q in ('R1','R2','R3','R4','R5','R6')},
                 'sign_fixture':{'status':'NOT_RUN'},'attack_validity':{'status':'NOT_RUN'},
                 'criterion_applied_to_experimental_results':False,'selected_k':None}
        lines=['# Recovery confirmation, quiet period 20: halt','',
               'This is gate 3 of the promotion plan. The recovery rule, its three quiet periods, selection rule and criterion were fixed before any run.',
               'This is not a promotion decision and selects no parameter. No ratio of two measured counts was computed.',
               'Applying the Section 6 selection rule and criterion and Section 8 interpretation is reserved for the operator.','',
               'Status: HALTED. R1 through R6 were not computed. Sign fixture not run.','',
               'Halt evidence: '+json.dumps(failures,sort_keys=True)]
        finalize(results,lines,summaries)
        return
    fixture=sign_fixture()
    validity=attack_validity()
    runs,summaries=observations()
    results={'status':'COMPLETE','runs':len(runs),'registered':calculate(runs),
             'sign_fixture':fixture,'attack_validity':validity,
             'criterion_applied_to_experimental_results':False,'selected_k':None}
    results['confirmation_arithmetic']=confirmation_arithmetic(results['registered'])
    results['selection_condition_arithmetic_reported']=True
    flat=[]
    for row in runs:
        value={k:v for k,v in row.items() if k!='transition_counts'}
        value.update(row['transition_counts'])
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
