"""Summarize recorded current-substrate trajectories; no simulation is run."""
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent))
import drift_char_probe as p
import csv,json,math,statistics
import numpy as np


def csv_rows(job):
    with (p.OUT/p.log_name(job)).open(encoding='utf-8',newline='') as f:
        raw=list(csv.DictReader(f))
    rows=[]
    for item in raw:
        row={}
        for k,v in item.items():
            if v=='':row[k]=None
            elif v in ('True','False'):row[k]=v=='True'
            elif k in ('kind',):row[k]=v
            elif k in ('step','seed','population','novelty_vector_count','incumbent_generation'):row[k]=int(v)
            else:row[k]=float(v)
        rows.append(row)
    if [r['step'] for r in rows]!=list(range(len(rows))):raise RuntimeError('Step sequence mismatch')
    return rows

def dist(values):
    a=np.asarray(values,dtype=float)
    if len(a)==0:return {'count':0}
    if not np.isfinite(a).all():raise RuntimeError('Nonfinite summary input')
    q=np.quantile(a,[0,.05,.25,.5,.75,.9,.95,1],method='linear')
    return dict(count=len(a),mean=float(a.mean()),**dict(zip(['min','p05','p25','median','p75','p90','p95','max'],map(float,q))))

def fmt(value):
    if value is None:return 'none'
    if isinstance(value,bool):return str(value).lower()
    if isinstance(value,float):return f'{value:.12g}'
    return str(value)

def source_quote(path,lo,hi):
    lines=(p.ROOT/path).read_text(encoding='utf-8').splitlines()
    return '\n'.join(lines[lo-1:hi])

def condition_summary(rows,field,onset):
    yes=[r for r in rows if r[field]]
    post=[r for r in yes if r['step']>=onset]
    entries=[r['step'] for i,r in enumerate(rows) if r[field] and (i==0 or not rows[i-1][field])]
    exits=[r['step'] for i,r in enumerate(rows) if i>0 and not r[field] and rows[i-1][field]]
    first=yes[0]['step'] if yes else None
    first_post=post[0]['step'] if post else None
    return {'count':len(yes),'denominator':len(rows),'first_logged_step':first,'entries':entries,'exits':exits,
            'first_step_minus_attack_onset':first-onset if first is not None else None,
            'count_at_or_after_onset':len(post),'first_at_or_after_onset':first_post,
            'elapsed_steps_from_onset':first_post-onset if first_post is not None else None,
            'at_attack_onset':next((r[field] for r in rows if r['step']==onset),None)}

def delta_summary(rows,onset=None):
    pairs=[(rows[i],rows[i]['g']-rows[i-1]['g']) for i in range(1,len(rows)) if onset is None or rows[i]['step']>=onset]
    if not pairs:return {'count':0}
    high=max(pairs,key=lambda x:x[1]);low=min(pairs,key=lambda x:x[1])
    return {'distribution':dist([d for _,d in pairs]),'max':high[1],'max_to_step':high[0]['step'],'max_from_step':high[0]['step']-1,
            'min':low[1],'min_to_step':low[0]['step'],'positive_changes':sum(d>0 for _,d in pairs),'negative_changes':sum(d<0 for _,d in pairs),'zero_changes':sum(d==0 for _,d in pairs),'count':len(pairs)}

def main():
    plan=p.load_plan();attack_obj=p.read(p.result_name('attack'))
    p.validate_result(plan,'attack',attack_obj)
    if not attack_obj.get('reproduction_passed'):raise RuntimeError('T0 did not pass')
    objs={j:p.read(p.result_name(j)) for j in p.jobs()}
    for j,o in objs.items():p.validate_result(plan,j,o)
    attack=csv_rows('attack');runs={j:csv_rows(j) for j in p.jobs()};allrows=[r for j in p.jobs() for r in runs[j]]
    if len(allrows)!=12000 or any(len(r)!=300 for r in runs.values()):raise RuntimeError('Requested baseline horizon/count not completed')
    if any(r['adapter_active'] for r in allrows):raise RuntimeError('Baseline adapter active')
    windows={'all_logged_steps':allrows,'steps_ge_10':[r for r in allrows if r['step']>=10]}
    calibration={};cal_rows=[]
    for name,rows in windows.items():
        V=[r['V'] for r in rows];ds=dist(V)
        candidates=[]
        for label,key in [('median','median'),('75th_percentile','p75'),('90th_percentile','p90')]:
            anchor=ds[key]
            values=[-math.expm1(-3.0*v/anchor) for v in V] if anchor>0 else None
            item={'candidate':label,'V_ref':anchor,'magnitude_factor':dist(values) if values is not None else None,'defined':anchor>0,'selected':False}
            candidates.append(item)
            flat={'window':name,'candidate':label,'records':len(V),'V_ref':anchor,'defined':anchor>0,'selected':False}
            if values is not None:flat.update({'magnitude_'+k:v for k,v in item['magnitude_factor'].items()})
            cal_rows.append(flat)
        calibration[name]={'V':ds,'V_zero_count':sum(v==0 for v in V),'denominator':len(V),'candidates':candidates}
    tmp=p.OUT/'drift_char_calibration_candidates.csv'
    with tmp.open('w',encoding='utf-8',newline='') as f:
        fields=list(dict.fromkeys(k for r in cal_rows for k in r));w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(cal_rows)
    constants=plan['read_constants'];R=constants['RUNAWAY_THRESHOLD'];A=constants['ALPHA_DEFAULT']*constants['CONVERGENCE_STRENGTH']
    table=[]
    for cs in [1.5,2.0,2.5,3.0]:
        gst=(R+math.log(cs)/A)/cs
        T=lambda c,g:c*math.exp(-A*max(0.0,c*g-R))
        table.append({'c_i':1.0,'c_s':cs,'g_star':gst,'incumbent_cg':gst,'successor_cg':cs*gst,'incumbent_unpenalized':gst<R,'successor_penalized':cs*gst>R,'T_difference_at_root':T(cs,gst)-T(1.0,gst),'T_difference_0_0001_below':T(cs,gst-.0001)-T(1.0,gst-.0001),'T_difference_0_0001_above':T(cs,gst+.0001)-T(1.0,gst+.0001)})
    gst=next(r['g_star'] for r in table if r['c_s']==2.0)
    onset=attack_obj['constructed_config']['attack_step'];post=[r for r in attack if r['step']>=onset]
    peak=max(attack,key=lambda r:r['g']);postpeak=max(post,key=lambda r:r['g'])
    conditions={k:condition_summary(attack,f,onset) for k,f in [('reference_soft','reference_soft_condition'),('reference_hard','reference_hard_condition'),('reference_soft_only','reference_soft_only')]}
    baseline_pair=runs['baseline_'+str(attack_obj['row']['seed'])]
    paired=[{'step':r['step'],'attack_g':r['g'],'honest_g':b['g'],'difference':r['g']-b['g']} for r,b in zip(attack,baseline_pair)]
    with (p.OUT/'drift_char_paired_g.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(paired[0]));w.writeheader();w.writerows(paired)
    pre_diffs=[r['difference'] for r in paired if r['step']<onset];post_diffs=[r['difference'] for r in paired if r['step']>=onset]
    pair_summary={'seed':attack_obj['row']['seed'],'pre_attack_max_absolute_g_difference':max(map(abs,pre_diffs)),
                  'post_attack_g_difference':dist(post_diffs),'post_attack_positive_count':sum(v>0 for v in post_diffs),'post_attack_negative_count':sum(v<0 for v in post_diffs),'post_attack_equal_count':sum(v==0 for v in post_diffs),'post_attack_denominator':len(post_diffs),
                  'final_g_difference':paired[-1]['difference'],'max_difference_step':max(paired,key=lambda r:r['difference'])['step']}
    modified=[r['step'] for r in attack if r['action_modified']];alarms=[r['step'] for r in attack if r['defense_fired']]
    trajectory={'initial_pre_step_g':attack_obj['initial_state']['g'],'max_g':peak['g'],'max_g_step':peak['step'],'min_g':min(r['g'] for r in attack),
                'post_attack_max_g':postpeak['g'],'post_attack_max_g_step':postpeak['step'],'post_attack_gap_below_g_star':gst-postpeak['g'],
                'attack_onset':onset,'g_at_step_before_onset':attack[onset-1]['g'],'g_at_onset':attack[onset]['g'],'final_g':attack[-1]['g'],'conditions':conditions,
                'yield_event_count':attack_obj['yield_event_count'],'live_soft_condition_observable':False,'source_denominator_floor_steps':sum(r['avg_wb']*r['transfer_state']<.01 for r in attack),
                'reference_technology_floor_steps':sum(r['reference_theta_incumbent']==.01 or r['reference_theta_successor']==.01 for r in attack),
                'modified_steps':modified,'alarm_steps':alarms,'deltas_all_adjacent':delta_summary(attack),'deltas_at_or_after_onset':delta_summary(attack,onset),
                'paired_honest_comparison':pair_summary}
    summary={'scope':'Current-substrate characterization before implementation; not registered characterization data or framework evidence.',
             'baseline_runs':len(runs),'baseline_steps_counted':len(allrows),'baseline_adapter_active_steps':sum(r['adapter_active'] for r in allrows),
             'calibration':calibration,'anchor_selected':False,'threshold_derivation':table,'trajectory':trajectory,'reproduction':attack_obj['reproduction_comparison']}
    p.write('drift_char_summary.json',summary)
    progress=p.read('drift_char_progress.json')
    sources={}
    for obj in [attack_obj,*objs.values()]:
        for path,digest in obj['simulation_source_sha256'].items():
            if path in sources and sources[path]!=digest:raise RuntimeError('Mixed simulation source identity')
            sources[path]=digest
    lines=['# V2.1 drift repair: pre-implementation characterization','','This is current-substrate characterization and constant measurement before implementation. It is not registered characterization data, is not framework evidence, and does not implement the repair. No calibration anchor or alarm constant is selected.','','Status: complete. T0 passed; 40 honest-baseline runs and one defended reproduction trajectory completed. T2 and T3 reuse the recorded T0 trajectory.','','## Fixed design decisions, verbatim context','','```text',plan['fixed_design_decisions'],'```','','## Preconditions and evidence selection','']
    for gate in plan['gates']:lines.append('- Gate '+str(gate['number'])+': PASS. '+json.dumps(gate,sort_keys=True))
    e=plan['evidence']
    lines += ['',f"Read authoritative manifest: `{e['manifest']}`, line {e['manifest_line']}, SHA256 `{e['manifest_sha256']}`. Its exact directory entry resolved uniquely through `git ls-tree`; no glob selected the result. Read CSV through `{e['tag']}` at commit `{e['tag_commit']}`: `{e['path']}`.",'',f"Expected Git blob SHA: `{e['expected_blob']}`. Hash of retrieved blob bytes: `{e['actual_blob']}`. MATCH, verified before CSV parsing. Counted {e['rows_counted']} rows with Python csv.DictReader, excluding the header. CSV SHA256: `{e['sha256']}`.",'',f"Selection: {e['selection_rule']} Data row {e['selected_data_row']} excluding the header; defended, phi 10, replicate 0, seed {attack_obj['row']['seed']}.",'','The pinned run directory contains only results.csv and environment_manifest.json. The results CSV contains run summaries and has no novelty matrix, avg_wb, theta_capability, or transfer_state series. The required trajectory was therefore recorded during the T0 rerun, with no additional attack run.','','## T0: reproduction gate','','| Boolean | Pinned | Measured | Match |','| --- | --- | --- | --- |']
    for k,v in attack_obj['reproduction_comparison'].items():lines.append(f"| {k} | {fmt(v['pinned'])} | {fmt(v['measured'])} | {fmt(v['match'])} |")
    lines += ['',f"Measured reproduction steps: {attack_obj['row']['steps_completed']}; elapsed time: {attack_obj['row']['elapsed_seconds']:.6f} seconds. The unmodified runner factory constructed a recorder subclass through a temporary worker-local class binding. The subclass calls super().step() and then reads committed state. No production file or factory function body changed; all four outcome booleans matched.",'','## Source verification and symbolic derivation','','The exact absorption expression read at simulation/metrics.py:660-667 is:','','```python',source_quote('simulation/metrics.py',660,667),'```','','Derived source definition: `g = max(0.02, theta_capability) / max(0.01, clip(avg_wb, 0, 1) * transfer_state)`. The avg_wb clipping is read at metrics.py:647. The bare product denominator in the prompt omits the source floor. The bare ratio agrees with the source-defined g only where that floor is inactive. The logs retain both quantities; undefined bare ratios are empty fields.','','Let `A = ALPHA * CONVERGENCE_STRENGTH`, `R = RUNAWAY_THRESHOLD`, and `B = theta_capability * transfer_state`. Read capability-bearing technology factor: `theta(c) = max(0.01, B * c * exp(-A * max(0, c*g - R)))`. Thus the unfloored factor `T(c)` in the prompt is recovered, but the full implementation also retains the outer floor.','','Derived algebra in the stipulated regime `c_i*g < R < c_s*g`:', '', '```text', 'c_s * exp(-A * (c_s*g - R)) = c_i', '-A * (c_s*g - R) = ln(c_i/c_s)', 'g* = [R - ln(c_i/c_s)/A] / c_s', 'A = 1; c_i = 1; c_s = 2:', 'g* = (1.5 + ln(2))/2', '```','',f'Derived numeric value: `g* = {gst:.15f}`. The incumbent product is {gst:.15f}, below 1.5; the successor product is {2*gst:.15f}, above 1.5. The stated regime holds. At equality the utilities are equal under the shared-action assumptions, not strictly ordered.','','| c_i | c_s | Derived g* | c_i*g* | c_s*g* | Incumbent unpenalized | Numeric T(c_s)-T(c_i) at root |','| ---: | ---: | ---: | ---: | ---: | --- | ---: |']
    for r in table:lines.append(f"| 1 | {r['c_s']} | {r['g_star']:.15f} | {r['incumbent_cg']:.12f} | {r['successor_cg']:.12f} | {fmt(r['incumbent_unpenalized'])} | {r['T_difference_at_root']:.4g} |")
    lines += ['','The constants and regime-specific root are verified. The unconditional structural claim in the prompt is not established by that algebra alone. The technology floor can make both capability factors equal above the root, and the actual yield code evaluates separately proposed actions, not necessarily a shared action (model.py:1299-1325). The action-dependent H_E term and finite epsilon remain in the utility prefactor (metrics.py:675-686). With a shared action, nonnegative state factors, and positive transition cost, g >= g* removes the reference capability advantage; this is the conditional reference boundary tabulated here.','','The pinned drift factory supplies no successor: run_attack_vector_revalidation_v2.py:322-333 creates capability 2.0 successors only for three other vectors. GardenModel defaults successor_ai to None (model.py:164-166,250). Yield evaluation requires a successor (model.py:1287), and the event log is empty without one (model.py:353-357). Consequently, no actual succession feasibility or live soft-region crossing was measured in this drift cell.','','The source-derived soft diagnostic uses the operator-specified capability pair 1.0 and 2.0, holds each logged post-step state and its committed action fixed, and applies the current source floors. It does not create a successor, optimize another action, or alter the model. The common discount cancels in the difference:', '', '```text', 'Q = lambda_n*H_N/(H_N+epsilon) + lambda_e*H_E/(H_E+epsilon)', 'delta_U_ref = Q * LAMBDA_LINEAGE_COUPLING * H_eff * psi_inst', '              * [theta(2) - theta(1)]', 'cost_ref = (1+beta_transition)', '           * [k1_transition*ln(1+1)*ln(generation+1)', '              + k2_transition/max(0.01, psi_inst_stock)]', 'soft_reference = delta_U_ref <= cost_ref', 'hard_reference = g >= g*', 'soft_only_reference = soft_reference and g < g*', '```','',f"Read transition coefficients on the constructed cell: k1={attack_obj['runtime_attributes']['k1_transition']}, k2={attack_obj['runtime_attributes']['k2_transition']}, beta={attack_obj['runtime_attributes']['beta_transition']}. The cost expression is read at agents.py:882-889 and its live call arguments at model.py:1333-1344. Utility components and difference follow metrics.py:645-686. The logs keep the absent live margin/cost empty and label the computed reference quantities separately.",'','## T1: honest-baseline calibration','','Measured and counted: 40 runs, 300 logged steps each, 12,000 step records. Each uses the Stage 1 baseline constructor (cusum_char_stage1.py:447-460), phi 10, prescribed seeds 1835086199 through 1835086238, no attack_vector_v2 key, and the defended COP settings. The adapter was inactive on every logged baseline step.','','V is the trace of the covariance of the actual per-step novelty matrix before eigenvalue flooring or normalization. The recorder follows metrics.py:772-792: N by 10 matrix, mean centering, then np.cov(rowvar=False), using the sample denominator N-1. Recorded H_N is the model datacollector value, which carries the existing 0.01 floor; h_n_spectral separately logs the cached estimator value (model.py:1530-1532,1556; metrics.py:645). No magnitude factor is fed back into the model.','','Rows are indexed after the model completes each step. Novelty is generated before demographic updates (model.py:1461-1476); avg_wb and stocks are the post-update state (model.py:1494-1499,1522-1524). Every recorder call verified that NumPy RNG state was unchanged by logging. The initial pre-step g is retained separately.','','| Calibration window | Counted steps | Measured median V | Measured p75 V | Measured p90 V | Counted V=0 steps |','| --- | ---: | ---: | ---: | ---: | ---: |']
    for name,c in calibration.items():lines.append(f"| {name} | {c['denominator']} | {fmt(c['V']['median'])} | {fmt(c['V']['p75'])} | {fmt(c['V']['p90'])} | {c['V_zero_count']} |")
    lines += ['','Percentiles use linear interpolation, NumPy quantile method=linear. The window steps_ge_10 contains steps 10 through 299 of every baseline run. Both window definitions are reported, with no anchor selected.','','Derived magnitude-factor distributions from measured V, using the stated expression `1 - exp(-3*V/V_ref)` (computed as `-expm1(-3*V/V_ref)` for numerical stability):','','| Window | Candidate anchor | V_ref | Records | Mean factor | Median factor | Min | p05 | p95 | Max |','| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for name,c in calibration.items():
        for item in c['candidates']:
            d=item['magnitude_factor']
            if d is None:lines.append(f"| {name} | {item['candidate']} | {fmt(item['V_ref'])} | {c['denominator']} | undefined | undefined | undefined | undefined | undefined | undefined |")
            else:lines.append(f"| {name} | {item['candidate']} | {fmt(item['V_ref'])} | {d['count']} | {fmt(d['mean'])} | {fmt(d['median'])} | {fmt(d['min'])} | {fmt(d['p05'])} | {fmt(d['p95'])} | {fmt(d['max'])} |")
    lines += ['','Full V and factor distributions are in drift_char_summary.json; the six candidate rows are also in drift_char_calibration_candidates.csv. These are candidate calibration measurements awaiting the operator; no anchor was frozen, selected, or consumed by a repaired estimator.','','## T2: g trajectory and reference regions','',f"Measured initial pre-step g: {fmt(trajectory['initial_pre_step_g'])}. Measured maximum over logged steps: {fmt(peak['g'])}, at step {peak['step']}. Measured maximum at or after attack onset: {fmt(postpeak['g'])}, at step {postpeak['step']}. Derived signed gap g* minus that post-onset maximum: {fmt(gst-postpeak['g'])}.",'',f"Counted live yield evaluations: {attack_obj['yield_event_count']}. The soft and hard columns below classify the specified fixed-state reference, not observed decisions by an instantiated successor. Counted source denominator-floor activations: {trajectory['source_denominator_floor_steps']} of {len(attack)} steps; reference technology-floor activations: {trajectory['reference_technology_floor_steps']} of {len(attack)} steps.",'','| Reference condition | Counted steps / total | First logged true step | First true step at/after onset | Condition true at onset | Exit steps |','| --- | --- | ---: | ---: | --- | --- |']
    for label,c in conditions.items():lines.append(f"| {label} | {c['count']} / {c['denominator']} | {fmt(c['first_logged_step'])} | {fmt(c['first_at_or_after_onset'])} | {fmt(c['at_attack_onset'])} | {', '.join(map(str,c['exits'])) or 'none'} |")
    lines += ['','The initial state is already above the reference root. Step 0 is the first logged occurrence, not an observed entry from below. The recorded exits refute permanent residence above g* in this trajectory. Source working_factor updates remain responsive to later allocations (working_factor.py:70-94); no irreversible g-crossing rule is implemented.','','Read attack action rule, attack_adapter_v2.py:211-223:','','```python',source_quote('simulation/attack_adapter_v2.py',211,223),'```','','Derived direction: a positive welfare transfer reduces the welfare share and increases compute by the same amount. The welfare bridge is nondecreasing in the welfare share (model.py:125-134), and the per-agent well-being update increases with that bridged resource level (agents.py:799-802). Compute raises or saturates the theta-capability target (constants_v2_stage18.py, STATE_ALLOCATION_MAPPING theta_capability entry); working_factor applies rate*(target-current) (working_factor.py:75-79). Thus the immediate direct channels push g upward or leave it unchanged at the relevant floors/caps, holding the other state and cohort effects fixed. They do not prove a monotonic or irreversible aggregate trajectory under changing policy, demography, and defense.', '',f"Counted action-modified steps: {len(modified)}; first {fmt(modified[0] if modified else None)}, last {fmt(modified[-1] if modified else None)}. Counted defense-fired steps: {len(alarms)}; first {fmt(alarms[0] if alarms else None)}. The existing adapter returns the honest action when its alarm fires (attack_adapter_v2.py:321-339).",'',f"The measured seed-paired honest g trajectory has maximum absolute pre-attack difference {fmt(pair_summary['pre_attack_max_absolute_g_difference'])}. After onset, attack minus honest g is positive on {pair_summary['post_attack_positive_count']} of {pair_summary['post_attack_denominator']} steps, negative on {pair_summary['post_attack_negative_count']}, and equal on {pair_summary['post_attack_equal_count']}. Its measured mean is {fmt(pair_summary['post_attack_g_difference']['mean'])}, maximum {fmt(pair_summary['post_attack_g_difference']['max'])}, and final difference {fmt(pair_summary['final_g_difference'])}. The upward direct allocation channel is confirmed by source. In this defended cell the measured post-onset paired mean is positive, but g is lower than the honest counterpart on {pair_summary['post_attack_negative_count']} of {pair_summary['post_attack_denominator']} post-onset steps and at the final step. The realized effect is therefore mixed rather than monotonic or permanent. Neither reference region is reached after attack onset. The per-step paired differences are in drift_char_paired_g.csv.",'','| Step | g | avg_wb | theta_capability | transfer_state | Reference margin | Reference cost | Soft | Hard |','| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |']
    selected=sorted(set([0,5,9,10,onset-1,onset,onset+5,65,66,postpeak['step'],len(attack)-1]))
    for i in selected:
        r=attack[i];lines.append('| '+' | '.join(fmt(r[k]) for k in ['step','g','avg_wb','theta_capability','transfer_state','reference_margin','reference_transition_cost','reference_soft_condition','reference_hard_condition'])+' |')
    lines += ['','## T3: realized approach rates and elapsed steps','','Per-step changes use g[t] minus g[t-1], so a positive change means movement toward larger g. The per-step CSV carries g_pre_step and g_change_within_step, including the separately identified initial-state-to-step-0 change. Adjacent-record summaries below start at step 1; the post-onset summary includes the step 49 to 50 transition.','','| Window | Counted changes | Measured maximum delta g | Transition | Measured minimum delta g | Positive changes | Negative changes |','| --- | ---: | ---: | --- | ---: | ---: | ---: |']
    for name,key in [('all adjacent records','deltas_all_adjacent'),('at or after attack onset','deltas_at_or_after_onset')]:
        d=trajectory[key];lines.append(f"| {name} | {d['count']} | {fmt(d['max'])} | {d['max_from_step']} to {d['max_to_step']} | {fmt(d['min'])} | {d['positive_changes']} | {d['negative_changes']} |")
    lines += ['','| Reference condition | First logged step minus onset | Elapsed steps from onset to first qualifying post-onset record |','| --- | ---: | ---: |']
    for label,c in conditions.items():lines.append(f"| {label} | {fmt(c['first_step_minus_attack_onset'])} | {fmt(c['elapsed_steps_from_onset'])} |")
    lines += ['','Signed timing convention: first logged qualifying step minus attack onset. A negative number denotes a pre-attack occurrence; it is not a post-attack response window. The last column reports an actual nonnegative elapsed-step count only when a qualifying record exists at or after onset; none means it was not reached in the observed post-onset trajectory. The soft timing is a derived reference classification because no live yield evaluation occurs.', '',
              'These are realized rates and passage times for one defended trajectory. They do not establish a global worst-case approach rate, a loop response time, or a conversion between g distance and accumulated alarm-score distance. No numerical D_alarm or response margin is fixed by this report.', '',
              '## Configuration, execution, and source provenance','',
              'Baseline configuration as constructed (random_seed varies over the prescribed 40 seeds):','','```json',json.dumps(objs[p.jobs()[0]]['constructed_config'],indent=2,sort_keys=True),'```','',
              'Attack configuration as constructed:','','```json',json.dumps(attack_obj['constructed_config'],indent=2,sort_keys=True),'```','',
              f"Machine: `{attack_obj['machine']}`. HEAD: `{plan['head']}` on main. Python: `{attack_obj['python']}`. NumPy: `{attack_obj['numpy']}`. Actual maximum concurrent baseline workers: {progress['peak_active_workers']}; T0 used one serial gate worker. CPU budget: 16, normal cap 15, work cap 12. These are worker limits, not a hard operating-system core reservation. Measured baseline batch elapsed time: {progress['elapsed_seconds']:.6f} seconds.",'',
              'All workers set numerical-library thread limits to one before library initialization and verified one effective OpenBLAS thread through the recorded runtime getter. Mode history and start/resume events are in drift_char_progress.json. Operational checks covered dispatch, normal/work draining, seed assignment, write-scope predicates, and rejection of mismatched completion records. Completion JSON files retain configuration, source identity, raw-log SHA256, and completion status; partial logs never count as completed results.','','SHA256 for every simulation Python module loaded by the runs:','','| Source module | SHA256 |','| --- | --- |']
    lines += [f'| `{path}` | `{digest}` |' for path,digest in sorted(sources.items())]
    lines += ['','## Write scope and artifact record','','The guard explicitly permits os.devnull in any mode. All other writable opens were limited to simulation/diagnostics/drift_char_ filenames. Bytecode writes were disabled. No out-of-prefix writable-open violation was recorded. No Git write operation, snapshot-generator operation, production change, runner edit, or prior-diagnostic edit was performed. The operator runs the containment diff.','','Ignored instructions that would conflict with the present write scope:']
    lines += ['- '+x for x in plan['out_of_scope_instructions_ignored']]
    lines += ['','drift_char_manifest.json enumerates every output, SHA256, and CSV row count. CSV counts use csv.DictReader excluding headers; non-CSV row counts are null. The manifest itself has no embedded self-hash to avoid self-reference; its completed-file hash is emitted separately. The report and all outputs are characterization artifacts, not authoritative framework evidence. No repair, anchor selection, recommendation, or published-number change was made.','']
    report='\n'.join(lines)
    if '\u2014' in report:raise RuntimeError('Em dash in authored report')
    p.write_text('drift_char_report.md',report)
    manifest={'status':'complete','scope':summary['scope'],'created_utc':p.now(),'head':plan['head'],'machine':attack_obj['machine'],'python':attack_obj['python'],'numpy':attack_obj['numpy'],'preconditions':plan['gates'],'reproduction':attack_obj['reproduction_comparison'],'simulation_runs':41,'baseline_workers_actually_used':progress['peak_active_workers'],'gate_workers_actually_used':1,'null_device_exemption':True,'simulation_source_sha256':sources,'anchor_selected':False,'outputs':[],'self_hash_convention':'Manifest has null self-hash. Completed-file SHA256 is emitted separately.','row_count_convention':'csv.DictReader excluding header; null for non-CSV outputs.'}
    target=p.OUT/'drift_char_manifest.json'
    paths=[x for x in p.OUT.iterdir() if x.is_file() and x.name.startswith('drift_char_')]
    if target not in paths:paths.append(target)
    for path in sorted(paths):
        count=None
        if path.suffix=='.csv':
            with path.open(encoding='utf-8',newline='') as f:count=sum(1 for _ in csv.DictReader(f))
        manifest['outputs'].append({'path':path.relative_to(p.ROOT).as_posix(),'sha256':None if path==target else p.sha(path),'row_count':count})
    p.write('drift_char_manifest.json',manifest)
    for obj in manifest['outputs']:
        if obj['sha256'] is not None and p.sha(p.ROOT/obj['path'])!=obj['sha256']:raise RuntimeError('Final output hash mismatch')
    print(json.dumps({'status':'complete','calibration':calibration,'trajectory':trajectory,'manifest_sha256':p.sha(target),'artifacts':len(manifest['outputs'])}),flush=True)

if __name__=='__main__':main()
