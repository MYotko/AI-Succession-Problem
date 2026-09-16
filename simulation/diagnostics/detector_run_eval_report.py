"""Render registered counts, provenance, and the stage 2 output manifest."""
import sys
sys.dont_write_bytecode=True
import detector_run_eval_executor as h
import numpy as np
import csv,io,json
from collections import Counter

def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join('none' if x is None else str(x).replace('|','/') for x in row)+' |' for row in rows])+'\n'

def e1_table(groups):
    rows=[]
    for arm,r in groups.items():
        c=r['counts'];m=r['margin_steps']
        rows.append([arm+(' (descriptive)' if arm=='H' else ''),r['n_runs'],*[c[k] for k in ('DETECTED_BEFORE_OR_AT','DETECTED_AFTER','CROSSED_UNDETECTED','NO_CROSSING')],m['minimum'],m['median'],m['maximum']])
    return table(['Arm','Runs','Before or at','After','Crossed undetected','No crossing','Margin min','Margin median','Margin max'],rows)

def finalize():
    plan=h.read(h.P+'plan.json');execution=h.read(h.P+'execution.json') if (h.OUT/(h.P+'execution.json')).exists() else {}
    halted=(h.OUT/(h.P+'stop.json')).exists()
    if not halted:
        try:
            h.pins()
            for pin in plan['pins']:
                committed=h.git('cat-file','blob','HEAD:'+pin['path'])
                if h.sha(h.lf(committed))!=pin['expected_sha256_lf']:raise RuntimeError('Completion committed source pin changed: '+pin['path'])
        except BaseException as error:
            h.mark_halt('completion_pins',error);halted=True
    readings=[]
    for pin in plan['pins']:
        current=h.sha(h.lf((h.ROOT/pin['path']).read_bytes()))
        committed=h.git('cat-file','blob','HEAD:'+pin['path'])
        readings.append({**pin,'completion_sha256_lf':current,'completion_committed_sha256_lf':h.sha(h.lf(committed)),
                         'completion_blob_sha1':h.git('rev-parse','HEAD:'+pin['path']).decode().strip(),
                         'matched':current==pin['expected_sha256_lf']==h.sha(h.lf(committed))})
    h.write(h.P+'source_readings.json',readings)
    runtime=h.metadata(np);runs=[]
    for a in plan['arms']:
        for seed in plan['seeds']:
            path=h.OUT/(h.P+a+'_'+str(seed)+'_complete.json')
            if path.exists():runs.append(h.read(path.name))
    modules=dict(runtime['modules'])
    gate_runs=[]
    for job in ('gate_factory','gate_common','gate_honest','gate_recorder','gate_wrapper'):
        path=h.OUT/(h.P+job+'_result.json')
        if path.exists():gate_runs.append(h.read(path.name))
    for r in runs+gate_runs:modules.update(r.get('runtime',{}).get('modules',{}))
    retries=[]
    for path in sorted(h.OUT.iterdir()):
        if path.name.startswith(h.P+'io_events_') and path.suffix=='.jsonl':
            with path.open(encoding='utf-8') as f:retries.extend(json.loads(line) for line in f if line.strip())
    warnings=[r['stderr'] for r in plan['t0_checks'] if r.get('stderr')]
    doc=['# v2.1 detector evaluation, stage 2','',
         'This is a detection characterization, not a containment evaluation. No constant was recomputed. No corrected figure was derived. The detector note Section 7 interpretation is reserved for the operator.','']
    if halted:
        failure=h.read(h.P+'stop.json')
        doc+=['Status: HALTED. '+failure['halt'],'',f'Completed evaluation runs: {len(runs)} of 360. No further runs were dispatched after the halt.','']
        results_path=h.OUT/(h.P+'results.json')
        if not results_path.exists():h.write(results_path.name,{'status':'HALTED','reason':failure['halt'],'completed_runs':len(runs),'registered_results_computed':False})
    else:
        r=h.read(h.P+'results.json')
        doc+=['Status: COMPLETE. All 360 evaluation runs have completion records. Counts below are computed from their recorded data.','',
              '## E1. Primary','',f"Primary g_star = {plan['g_stars']['PRIMARY_2_0']!r}. Margins are crossing step minus first operational detection step, in steps. A missing crossing is NO_CROSSING regardless of alarms. The honest row is descriptive.",'',e1_table(r['E1']),
              '## E1a. SECONDARY','',
              'Restricted to attack crossings whose paired honest crossing is absent or strictly later. All counts and margins in this section are SECONDARY.','',e1_table(r['E1a_SECONDARY']),
              '## E2. First operational channel','',
              table(['Arm','Runs','With detection','Entropy first','g first','Same step','Neither from step 50'],[[a,x['n_runs'],x['with_operational_detection'],x['entropy_first'],x['g_first'],x['same_step'],x['neither_at_or_after_50']] for a,x in r['E2'].items()]),
              '## E3. Honest and pre-onset operational alarms','',
              table(['Group','Window','Runs with alarm','Denominator'],[['H','step >= 10',r['E3']['honest']['count'],r['E3']['honest']['denominator']]]+[[a,'10 <= step < 50',x['count'],x['denominator']] for a,x in r['E3']['attack_pre_onset'].items()])]
        if r['E3']['honest']['calibration_shortfall']:doc+=['Calibration shortfall: the honest count exceeds the pre-registered target of about 5 percent. No constant was adjusted.','']
        doc+=['## E4. L comparison channel','',e1_table(r['E4']['L_channel']),
              table(['Arm','Denominator','L before or at, g not','g before or at, L not'],[[a,x['denominator'],x['L_before_or_at_g_not'],x['g_before_or_at_L_not']] for a,x in r['E4']['paired_channel_counts'].items()]),
              '## E5. SECONDARY sweep','']
        for label,x in r['E5_SECONDARY'].items():doc+=['### '+label,'',f"SECONDARY g_star = {x['g_star']!r}. Every count and margin in this table is SECONDARY.",'',e1_table(x['arms'])]
        doc+=['## E6. Heartbeat counts','',f"Matching runs: {r['E6']['runs_matching']} of {r['E6']['runs']}. Completed steps: {r['E6']['completed_steps']}. Heartbeats: {r['E6']['heartbeat_count']}. Mismatching runs: {json.dumps(r['E6']['mismatching_runs'])}.",'']
    doc+=['## Gates and continuous checks','',
          'The recorder was copied from the committed stage 1 executor. No stage 1 diagnostic module was imported. The stage 2 guard permits only detector_run_eval_ artifacts and os.devnull; the null-device exemption is present. Bytecode writes are disabled. JSON reads and atomic replacement use a five-second permission-error retry limit. Each retry is recorded.','']
    upath=h.OUT/(h.P+'unit_gate.json')
    if upath.exists():
        unit=h.read(upath.name)
        doc+=[table(['Channel','Synthetic case','Passed','Measured values'],[[c['channel'],c['case'],c['passed'],json.dumps({k:v for k,v in c.items() if k not in ('channel','case','passed')},sort_keys=True)] for c in unit['cases']])]
    gp=h.OUT/(h.P+'gates.json')
    if gp.exists():
        gates=h.read(gp.name)
        doc+=['```json',json.dumps(gates,indent=2,sort_keys=True),'```','']
    fallback=Counter(x['shape_fallback_increase_step_0'] for x in runs)
    doc+=[f'Step 0 fallback increase distribution: {json.dumps(dict(fallback),sort_keys=True)}.',
          f"Permitted fallback increase after step 0: {sum(x['shape_fallback_permitted_increase_after_step_0'] for x in runs)}. Non-permitted increase count: {sum(x['shape_fallback_nonpermitted_increase_count'] for x in runs)}.",'',
          'Amendment 2 descriptive recording, without additional registered analysis:','',
          table(['Arm','Runs with fewer than two novelty vectors','Completed runs'],[[a,sum(x['first_fewer_than_two_novelty_vectors_step'] is not None for x in runs if x['arm']==a),sum(x['arm']==a for x in runs)] for a in plan['arms']]),
          'The first such step for each run is recorded in detector_run_eval_runs.csv and its completion record.','',
          '## Execution and provenance','',
          f"Machine: {runtime['machine']}. HEAD: {plan['head']}. Python: {runtime['python']}. NumPy: {runtime['numpy']}.",'',
          f"Operator CPU budget: 16. Maximum active evaluation workers: {execution.get('maximum_active_workers',0)}. Normal limit: 15; work limit: 12. These are worker limits, not operating-system core reservations. Numerical-library threads were configured to one and verified per worker using the loaded OpenBLAS runtime query.",'',
          'Mode changes: '+json.dumps(execution.get('mode_changes',[]),sort_keys=True),
          'Resumed seeds and reasons: '+json.dumps(execution.get('resumed_seeds',[]),sort_keys=True),
          f'Retry events: {len(retries)}. Full events are in the manifest and per-process io_events JSONL files.','',
          'T0 passed all enumerated checks before artifact creation. T0 command evidence is in detector_run_eval_plan.json. The CRLF worktree and LF blob condition was retained without normalization. T0 stderr warnings:','',
          '```text','\n'.join(warnings) if warnings else 'None.','```','',
          '### Pinned hashes, start and completion','',
          table(['Path','Expected LF SHA256','Start LF SHA256','Completion LF SHA256','Completion blob LF SHA256','Match'],[[x['path'],x['expected_sha256_lf'],x['start_sha256_lf'],x['completion_sha256_lf'],x['completion_committed_sha256_lf'],x['matched']] for x in readings]),
          'Committed blob SHA1 values for both notes, the constants, detector, and source files are recorded in the manifest and detector_run_eval_source_readings.json.','',
          '### Module provenance','',
          'Hash bases are raw working-tree bytes and LF-normalized working-tree bytes, labeled separately.','',
          table(['Module','Raw SHA256','LF-normalized SHA256'],[[path,x['sha256_raw'],x['sha256_lf']] for path,x in sorted(modules.items())]),
          'Operational retry implementation: detector_run_eval_executor.py, LF-normalized SHA256 '+h.sha(h.lf((h.OUT/(h.P+'executor.py')).read_bytes()))+'.','',
          'All artifact SHA256 entries use LF-normalized bytes. CSV row counts use csv.DictReader and exclude headers. The manifest lists itself separately without a recursive self-hash. No attack-success rate or corrected published figure was computed.','']
    text='\n'.join(doc)
    if '\u2014' in text:raise RuntimeError('Report contains a forbidden em dash')
    with(h.OUT/(h.P+'report.md')).open('w',encoding='utf-8',newline='\n') as f:f.write(text)
    outputs=[]
    manifest_name=h.P+'manifest.json'
    for path in sorted(h.OUT.iterdir()):
        if not path.name.startswith(h.P) or not path.is_file() or path.name==manifest_name:continue
        raw=path.read_bytes();count=None
        if path.suffix=='.csv' or path.name.endswith('.csv.partial'):
            count=sum(1 for unused in csv.DictReader(io.StringIO(raw.decode('utf-8'))))
        outputs.append({'path':path.relative_to(h.ROOT).as_posix(),'sha256_lf':h.sha(h.lf(raw)),'csv_rows':count,'partial':path.name.endswith('.partial')})
    reference=h.read(h.P+'recorder_conformance.json') if(h.OUT/(h.P+'recorder_conformance.json')).exists() else None
    manifest={'status':'HALTED' if halted else 'COMPLETE','outputs':outputs,
              'manifest_self':{'path':'simulation/diagnostics/'+manifest_name,'sha256_lf':None,'csv_rows':None,'reason':'Self-hash excluded to avoid circular hashing'},
              'sha256_basis':'LF-normalized bytes','csv_count_method':'csv.DictReader excluding header',
              'head':plan['head'],'runtime':runtime,'worker_execution':execution,'module_hashes':modules,
              'source_pins_start_and_end':readings,'recorder_conformance_evidence':reference,
              'retry_events':retries,'t0_stderr_warnings':warnings,'created_utc':h.now()}
    h.write(manifest_name,manifest)
    print(json.dumps({'status':manifest['status'],'report':h.P+'report.md','results':h.P+'results.json','manifest':manifest_name,'outputs':len(outputs)}),flush=True)

if __name__=='__main__':finalize()
