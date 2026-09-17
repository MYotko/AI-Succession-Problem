"""Render round 3 attempt 2 registered results and provenance without interpretation."""
import sys
sys.dont_write_bytecode=True
import detector_run_r3_eval_a2_executor as h
import numpy as np
import csv,io,json,re
from collections import Counter

def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join('none' if x is None else str(x).replace('|','/') for x in row)+' |' for row in rows])+'\n'

def f1_table(groups):
    rows=[]
    for arm,r in groups.items():
        c=r['counts'];lead=r['lead_steps']
        rows.append([arm+(' (descriptive)' if arm=='H' else ''),r['denominator'],
                     *[c[k] for k in ('ALARM_BEFORE_OR_AT','ALARM_AFTER','HAZARD_NO_ALARM','NO_HAZARD')],
                     lead['count'],lead['minimum'],lead['median'],lead['maximum']])
    return table(['Arm','Runs','Alarm before or at','Alarm after','Hazard, no alarm','No hazard','Lead count','Lead min','Lead median','Lead max'],rows)

def variant_title(name):return name+(' PRIMARY' if name=='A975' else ' SECONDARY')


def g2_table(groups):
    rows=[]
    for arm,r in groups.items():
        c=r['counts'];d=r['round2_minus_allocation_steps']
        rows.append([arm+(' (descriptive)' if arm=='H' else ''),r['denominator'],
          *[c[k] for k in ('ALLOCATION_EARLIER','ROUND2_EARLIER','EQUAL','ONLY_ALLOCATION','ONLY_ROUND2','NEITHER')],
          d['count'],d['minimum'],d['median'],d['maximum']])
    return table(['Arm','Runs','Allocation earlier','Round 2 earlier','Equal','Only allocation','Only round 2','Neither','Difference count','Difference min','Difference median','Difference max'],rows)

def finalize():
    plan=h.read(h.P+'plan.json');execution=h.read(h.P+'execution.json') if (h.OUT/(h.P+'execution.json')).exists() else {}
    halted=(h.OUT/(h.P+'stop.json')).exists()
    if not halted:
        try:
            h.pins()
            for pin in plan['pins']:
                if h.sha(h.lf(h.git('cat-file','blob','HEAD:'+pin['path'])))!=pin['expected_sha256_lf']:
                    raise RuntimeError('Completion committed pin changed: '+pin['path'])
        except BaseException as error:h.mark_halt('completion_pins',error);halted=True
    readings=[]
    for pin in plan['pins']:
        actual=h.sha(h.lf((h.ROOT/pin['path']).read_bytes()));raw=h.git('cat-file','blob','HEAD:'+pin['path'])
        readings.append({**pin,'completion_sha256_lf':actual,'completion_committed_sha256_lf':h.sha(h.lf(raw)),
                         'completion_blob_sha1':h.git('rev-parse','HEAD:'+pin['path']).decode().strip(),
                         'matched':actual==h.sha(h.lf(raw))==pin['expected_sha256_lf']})
    h.write(h.P+'source_readings.json',readings)
    runtime=h.metadata(np);runs=[];modules=dict(runtime['modules']);gate_runs=[]
    for arm in plan['arms']:
        for seed in plan['seeds']:
            name=h.P+arm+'_'+str(seed)+'_complete.json'
            if(h.OUT/name).exists():runs.append(h.read(name))
    for job in ('gate_factory','gate_common','gate_honest','gate_recorder','gate_wrapper'):
        name=h.P+job+'_result.json'
        if(h.OUT/name).exists():gate_runs.append(h.read(name))
    for r in runs+gate_runs:modules.update(r.get('runtime',{}).get('modules',{}))
    retries=[]
    for p in sorted(h.OUT.iterdir()):
        if p.name.startswith(h.P+'io_events_') and p.suffix=='.jsonl':
            with p.open(encoding='utf-8') as f:retries.extend(json.loads(line) for line in f if line.strip())
    warnings=[x['stderr'] for x in plan['t0_checks'] if x.get('stderr')]
    doc=['# Detector round 3, stage B evaluation','',
         'This is a detection characterization, not a containment evaluation. No constant was derived or recomputed for use. No corrected figure was derived. Comparison with rounds 1 and 2 is descriptive. The round 3 note Section 7 interpretation is reserved for the operator.','']
    doc+=['Attempt 1 halted at the A-definition gate with zero evaluation runs launched. Amendment 1 pins A to numpy.sum(numpy.abs(x - m)) over the six-element float64 vectors in the registered order. No constant changed or was re-derived.','']
    if halted:
        failure=h.read(h.P+'stop.json');doc+=['Status: HALTED. '+failure['halt'],'',f'Completed evaluation runs: {len(runs)} of 360.','']
        if not(h.OUT/(h.P+'results.json')).exists():h.write(h.P+'results.json',{'status':'HALTED','halt_reason':failure['halt'],'completed_runs':len(runs),'registered_analysis_computed':False})
    else:
        results=h.read(h.P+'results.json');variants=results['registered_results']
        note=h.pinned_blob('simulation/diagnostics/detector_round3_design_note.md').decode('utf-8')
        bias=re.search(r'This observable was chosen knowing how the attack\s+works\.',note).group(0)
        limitation=results['limitation']
        doc+=['Status: COMPLETE. All 360 runs have completion records. Counts and values below are computed from recorded data.','',
              '## G1. Primary hazard','',
              '\n'.join('> '+line for line in bias.splitlines()),'',limitation,'',
              'Lead is confirmation step minus the first allocation alarm step at or after step 50. Negative leads are retained. Lead summaries include every run with both a hazard and an alarm. NO_HAZARD applies regardless of alarms. Honest rows are descriptive.','']
        for v in ('A975','A95','A90'):
            doc+=['### '+variant_title(v),'',f"Threshold: {variants[v]['threshold']!r}.",'',f1_table(variants[v]['G1'])]
        doc+=['## G2. Paired alarm comparison','',limitation,'',
              'The difference is round 2 operational alarm step minus allocation alarm step, over runs where both exist. Positive means the allocation channel alarmed first.','']
        for v in ('A975','A95','A90'):
            doc+=['### '+variant_title(v),'',g2_table(variants[v]['G2'])]
        doc+=['## G3. Honest and pre-onset alarms','',
              'Counts above about 5 percent of honest runs are labeled calibration shortfalls. Nothing is adjusted.','']
        for v in ('A975','A95','A90'):
            x=variants[v]['G3'];a=x['honest_allocation_alarms'];b=x['honest_round2_operational_alarms']
            rows=[['H','Allocation alarm, steps >= 10',a['count'],a['denominator']],
                  ['H','Round 2 operational alarm, steps >= 10',b['count'],b['denominator']]]
            rows += [[arm,'Allocation alarm, steps 10 through 49',q['count'],q['denominator']] for arm,q in x['attack_pre_onset_allocation'].items()]
            rows += [[arm,'Round 2 operational alarm, steps 10 through 49',q['count'],q['denominator']] for arm,q in x['attack_pre_onset_round2_operational'].items()]
            doc+=['### '+variant_title(v),'',table(['Arm','Quantity','Count','Denominator'],rows)]
            if a['calibration_shortfall']:doc+=['Calibration shortfall: honest allocation alarm count exceeds the stated target.','']
            if b['calibration_shortfall']:doc+=['Calibration shortfall: honest round 2 operational alarm count exceeds the stated target.','']
        doc+=['## G4. SECONDARY, attack-specific directed channels','',limitation,'',
              'Every number in this section is SECONDARY and attack-specific. The directed channels are reported for each allocation-threshold context.','']
        for v in ('A975','A95','A90'):
            for channel,x in variants[v]['G4'].items():
                doc+=['### '+v+' '+channel+' SECONDARY, attack-specific','',
                      f"SECONDARY, attack-specific threshold: {x['threshold']!r}.",
                      '',f1_table(x['G1']),g2_table(x['G2'])]
        doc+=['## G5. SECONDARY hazard sweep','',
              'Every number in this section is SECONDARY.','']
        for v in ('A975','A95','A90'):
            for case,x in variants[v]['G5'].items():
                doc+=['### '+v+' '+case+' SECONDARY','']
                if case=='SECONDARY_2_5':doc+=['> '+x['section_4_caveat'],'']
                doc+=[f"SECONDARY g_star = {x['g_star']!r}; SECONDARY k = {x['k']}. Every number in the table is SECONDARY.",'',f1_table(x['arms'])]
        x=results['G6']
        doc+=['## G6. Heartbeats','',
              table(['Runs','Channels','Run-channel pairs','Completed steps','Heartbeat records'],
                    [[x['runs'],len(x['channels']),x['run_channel_pairs'],x['completed_steps'],x['heartbeat_records']]]),
              'Per-run, per-channel heartbeat mismatches: '+json.dumps(x['mismatches'])+'.','']
        x=results['G7']
        doc+=['## G7. Auditability','',
              'The audit CSV carries every alarm step and its channel and threshold, every hazard span with start and end steps, and each run maximum of A with its first occurrence step. Empty alarm and span sets remain explicit in completion records. The allocation series CSV and per-run allocation logs record A on every completed step. No result at another threshold or k was computed.','',
              table(['Artifact','Rows'],[[x['audit_csv'],x['audit_rows']],
                    [x['allocation_series_csv'],x['allocation_series_rows']]]),
              table(['Alarm rows','Span rows','A maximum rows'],[[x['alarm_rows'],x['span_rows'],x['maximum_rows']]]),'']
    doc+=['## Gates and continuous checks','',
          'All gate probes were run for this stage. The recorder and operational retry functions were copied from committed round 1 source; no module with a different write guard was imported. The stage B write guard permits only detector_run_r3_eval_a2_ artifacts and os.devnull. The null-device exemption is present; bytecode writes are disabled.','']
    name=h.P+'unit_gate.json'
    if(h.OUT/name).exists():
        unit=h.read(name);doc+=[table(['Channel','Case','Passed','Measured values'],[[c['channel'],c['case'],c['passed'],json.dumps({k:v for k,v in c.items() if k not in ('channel','case','passed')},sort_keys=True)] for c in unit['cases']])]
    name=h.P+'gates.json'
    if(h.OUT/name).exists():
        gates=h.read(name)
        for key in ('gate_2','gate_3','gate_4','gate_5','gate_6','recorder_conformance','constants_conformance','allocation_definition'):
            doc+=[key+': '+str(gates[key]['passed'])+'.','']
        g=gates['gate_3'];c=gates['recorder_conformance']
        doc+=[f"Constructor comparison: {g['steps_compared']} completed steps, {g['recorder_fields']} recorded fields, {g['field_value_comparisons']} field comparisons; first difference: {g['first_difference']}. Factory and common end reasons: {g['factory_end_reason']}, {g['common_end_reason']}.",'',
              f"Wrapper identity comparisons: {gates['gate_4']['comparisons']}. Honest probe: {gates['gate_5']['steps']} steps. Recorder conformance: {c['field_comparisons']} exact field comparisons across {c['steps_compared']} steps; first difference: {c['first_difference']}.",'',
              'Every channel constant, allocation median, threshold, and hazard parameter is checked bitwise against the committed stage A and earlier files. No constant was recomputed. Details are in detector_run_r3_eval_a2_constants_gate.json.','',
              f"A-definition gate: {gates['allocation_definition']['steps']} exact comparisons; first difference: {gates['allocation_definition']['first_difference']}.",
              'The raw recorder schema is unchanged. A is recorded in a separate per-step allocation CSV.','']
    doc+=['Exploratory descriptive recording required by Amendment 2:','',
          table(['Arm','Runs','Runs reaching fewer than two novelty vectors'],[[a,sum(r['arm']==a for r in runs),sum(r['arm']==a and r['first_fewer_than_two_novelty_vectors_step'] is not None for r in runs)] for a in plan['arms']]),
          'The first such step is recorded per run in the runs CSV and completion records.','',
          'Step 0 fallback increase distribution: '+json.dumps(dict(Counter(r['shape_fallback_increase_step_0'] for r in runs)),sort_keys=True)+'.',
          f"Permitted fallback increase after step 0: {sum(r['shape_fallback_permitted_increase_after_step_0'] for r in runs)}. Non-permitted increase count: {sum(r['shape_fallback_nonpermitted_increase_count'] for r in runs)}.",'',
          '## Execution and provenance','',
          f"Machine: {runtime['machine']}. HEAD: {plan['head']}. Python: {runtime['python']}. NumPy: {runtime['numpy']}.",'',
          f"Operator CPU budget: 16. Maximum active evaluation workers: {execution.get('maximum_active_workers',0)}. Limits are 15 in normal mode and 12 in work mode. These are worker limits, not operating-system core reservations. Numerical-library threads were set to one before import and verified per worker through the loaded OpenBLAS runtime.",'',
          'Mode changes: '+json.dumps(execution.get('mode_changes',[]),sort_keys=True),
          'Resumed seeds and reasons: '+json.dumps(execution.get('resumed_seeds',[]),sort_keys=True),
          f'Retry events: {len(retries)}. JSON reads and atomic replacement use the five-second bound; all retry events are in the manifest and per-process JSONL files.','',
          'T0 passed every enumerated check before the fresh namespace was created. The known CRLF/LF condition was retained without normalization. T0 stderr warnings:','',
          '```text','\n'.join(warnings) if warnings else 'None.','```','',
          '### Source pins, start and completion','',
          table(['Path','Expected LF SHA256','Start LF SHA256','Completion LF SHA256','Completion blob LF SHA256','Match'],[[x['path'],x['expected_sha256_lf'],x['start_sha256_lf'],x['completion_sha256_lf'],x['completion_committed_sha256_lf'],x['matched']] for x in readings]),
          'Committed blob SHA1 values for all four notes, all three constants files, the detector, and every pinned source are in the manifest and source_readings JSON.','',
          '### Module hashes','',
          'Bases: raw working-tree bytes and LF-normalized working-tree bytes.','',
          table(['Module','Raw SHA256','LF-normalized SHA256'],[[path,x['sha256_raw'],x['sha256_lf']] for path,x in sorted(modules.items())]),
          'Operational retry implementation: detector_run_r3_eval_a2_executor.py, LF-normalized SHA256 '+h.sha(h.lf((h.OUT/(h.P+'executor.py')).read_bytes()))+'.','',
          'Artifact hashes use LF-normalized bytes. CSV row counts use csv.DictReader excluding headers, with null for non-CSV outputs. The manifest lists itself separately without a recursive self-hash.','']
    report='\n'.join(doc)
    if '\u2014' in report:raise RuntimeError('Forbidden em dash in report')
    with(h.OUT/(h.P+'report.md')).open('w',encoding='utf-8',newline='\n') as f:f.write(report)
    outputs=[]
    for path in sorted(h.OUT.iterdir()):
        if not path.is_file() or not path.name.startswith(h.P) or path.name==h.P+'manifest.json':continue
        raw=path.read_bytes();count=None
        if path.suffix=='.csv' or path.name.endswith('.csv.partial'):count=sum(1 for unused in csv.DictReader(io.StringIO(raw.decode('utf-8'))))
        outputs.append({'path':path.relative_to(h.ROOT).as_posix(),'sha256_lf':h.sha(h.lf(raw)),'csv_rows':count,'partial':path.name.endswith('.partial')})
    manifest={'status':'HALTED' if halted else 'COMPLETE','outputs':outputs,
              'manifest_self':{'path':'simulation/diagnostics/'+h.P+'manifest.json','sha256_lf':None,'csv_rows':None,'reason':'Self-hash excluded to avoid circular hashing'},
              'sha256_basis':'LF-normalized bytes','csv_count_method':'csv.DictReader excluding header','head':plan['head'],
              'runtime':runtime,'worker_execution':execution,'module_hashes':modules,'source_pins_start_and_end':readings,
              'retry_events':retries,'t0_stderr_warnings':warnings,'created_utc':h.now()}
    h.write(h.P+'manifest.json',manifest)
    print(json.dumps({'status':manifest['status'],'report':h.P+'report.md','results':h.P+'results.json','manifest':h.P+'manifest.json','outputs':len(outputs)}),flush=True)

if __name__=='__main__':finalize()
