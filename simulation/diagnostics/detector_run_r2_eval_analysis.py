"""Registered round 2 F1 through F7, computed from recorded trajectories."""
import sys
sys.dont_write_bytecode=True
import detector_run_r2_eval_executor as h
import numpy as np
import csv,json

CATEGORIES=('ALARM_BEFORE_OR_AT','ALARM_AFTER','HAZARD_NO_ALARM','NO_HAZARD')
PRIMARY='PRIMARY_2_0'

def category(confirmation,alarm):
    if confirmation is None:return 'NO_HAZARD'
    if alarm is None:return 'HAZARD_NO_ALARM'
    return 'ALARM_BEFORE_OR_AT' if alarm<=confirmation else 'ALARM_AFTER'

def before(alarm,confirmation):return confirmation is not None and alarm is not None and alarm<=confirmation

def grouped(runs,variant,case=PRIMARY,channel=None):
    counts={c:0 for c in CATEGORIES};leads=[]
    for r in runs:
        confirmation=r['hazards'][case]['confirmation_step'];v=r['variants'][variant]
        alarm=v['detection_alarm_step'] if channel is None else v['first_detection_steps'][channel]
        counts[category(confirmation,alarm)]+=1
        if confirmation is not None and alarm is not None:leads.append(confirmation-alarm)
    result={'n_runs':len(runs),'counts':counts,'lead_steps':{'count':len(leads),'minimum':min(leads) if leads else None,
             'median':float(np.median(leads)) if leads else None,'maximum':max(leads) if leads else None}}
    if case=='SECONDARY_2_5':result['section_4_caveat']=h.CAVEAT
    return result

def analyze():
    h.check_stop();h.pins();plan=h.read(h.P+'plan.json');execution=h.read(h.P+'execution.json')
    if execution['status']!='COMPLETE':raise RuntimeError('Analysis requires a completed batch')
    params,hazards,unused=h.constants();runs=[];span_rows=[];alarm_rows=[];mismatches={v:[] for v in params}
    for arm in plan['arms']:
        for seed in plan['seeds']:
            r=h.completed(arm+'_'+str(seed),arm,seed)
            if r is None:raise RuntimeError('Completion record missing')
            rows=h.log_rows(r['raw_log'])
            if h.hazard_records(rows,hazards)!=r['hazards']:raise RuntimeError('Recorded hazard differs from raw log')
            heartbeats=h.log_rows(next(name for name in r['detector_logs'] if '_heartbeats_' in name))
            recorded_alarms=h.log_rows(next(name for name in r['detector_logs'] if '_alarms_' in name))
            # Blank caveat cells stay blank in the audit CSV.
            span_path=next(name for name in r['detector_logs'] if '_spans_' in name)
            with(h.OUT/span_path).open(encoding='utf-8',newline='') as f:recorded_spans=list(csv.DictReader(f))
            for row in recorded_spans:span_rows.append({'arm':arm,'seed':seed,**row})
            for row in recorded_alarms:alarm_rows.append({'arm':arm,'seed':seed,**row})
            for variant in params:
                v=r['variants'][variant];hb=[x for x in heartbeats if x['variant']==variant]
                if len(hb)!=len(rows) or r['heartbeat_count'][variant]!=len(rows):mismatches[variant].append(r['job'])
                if [x['heartbeat_counter'] for x in hb]!=list(range(1,len(rows)+1)):raise RuntimeError('Heartbeat counter sequence mismatch')
                if [x['step'] for x in hb]!=list(range(len(rows))):raise RuntimeError('Heartbeat step sequence mismatch')
                actual=[a for a in recorded_alarms if a['variant']==variant]
                if actual!=v['alarm_records']:raise RuntimeError('Alarm CSV differs from completion record')
                expected=next((x['step'] for x in actual if x['operational_channel'] and x['step']>=50),None)
                if expected!=v['detection_alarm_step']:raise RuntimeError('Operational alarm bookkeeping differs')
                for channel in ('entropy','g','L'):
                    expected=next((x['step'] for x in actual if x['channel']==channel and x['step']>=50),None)
                    if expected!=v['first_detection_steps'][channel]:raise RuntimeError('Channel alarm bookkeeping differs')
            runs.append(r)
    byarm={a:[r for r in runs if r['arm']==a] for a in plan['arms']};honest={r['seed']:r for r in byarm['H']};attack_arms=plan['arms'][1:]
    results={}
    for variant in params:
        label='PRIMARY' if variant=='T975' else 'SECONDARY'
        f1={a:{'variant_label':label,'arm_label':'descriptive honest' if a=='H' else 'attack',**grouped(byarm[a],variant)} for a in plan['arms']}
        f1a={}
        for arm in attack_arms:
            selected=[r for r in byarm[arm] if r['hazards'][PRIMARY]['confirmation_step'] is not None and
                      (honest[r['seed']]['hazards'][PRIMARY]['confirmation_step'] is None or
                       honest[r['seed']]['hazards'][PRIMARY]['confirmation_step']>r['hazards'][PRIMARY]['confirmation_step'])]
            f1a[arm]={'label':'SECONDARY','eligible_seeds':[r['seed'] for r in selected],**grouped(selected,variant)}
        f2={}
        for arm in attack_arms:
            counts={'entropy_first':0,'g_first':0,'same_step':0,'neither_at_or_after_50':0}
            for r in byarm[arm]:
                first=r['variants'][variant]['first_detection_steps'];e=first['entropy'];g=first['g']
                if e is None and g is None:key='neither_at_or_after_50'
                elif e==g:key='same_step'
                elif g is None or(e is not None and e<g):key='entropy_first'
                else:key='g_first'
                counts[key]+=1
            f2[arm]={'denominator':len(byarm[arm]),**counts}
        alarm_count=sum(any(x['operational_channel'] and x['step']>=10 for x in r['variants'][variant]['alarm_records']) for r in byarm['H'])
        hazard_count=sum(r['hazards'][PRIMARY]['confirmation_step'] is not None for r in byarm['H'])
        f3={'honest_operational_alarm':{'count':alarm_count,'denominator':len(byarm['H']),
             'calibration_shortfall':alarm_count>0.05*len(byarm['H']),'registered_target':'about 5 percent'},
            'honest_PRIMARY_2_0_hazard':{'count':hazard_count,'denominator':len(byarm['H']),
             'calibration_shortfall':hazard_count>0.025*len(byarm['H']),'registered_target':'about 2.5 percent, round 2 note Section 7 F3'},
            'attack_pre_onset':{a:{'count':sum(any(x['operational_channel'] and 10<=x['step']<50 for x in r['variants'][variant]['alarm_records']) for r in byarm[a]),'denominator':len(byarm[a])} for a in attack_arms}}
        f4={'L_channel':{a:{'variant_label':label,'arm_label':'descriptive honest' if a=='H' else 'attack',**grouped(byarm[a],variant,channel='L')} for a in plan['arms']},'paired_channel_counts':{}}
        for arm in attack_arms:
            pairs=[(before(r['variants'][variant]['first_detection_steps']['L'],r['hazards'][PRIMARY]['confirmation_step']),
                    before(r['variants'][variant]['first_detection_steps']['g'],r['hazards'][PRIMARY]['confirmation_step'])) for r in byarm[arm]]
            f4['paired_channel_counts'][arm]={'denominator':len(pairs),'L_before_or_at_g_not':sum(l and not g for l,g in pairs),'g_before_or_at_L_not':sum(g and not l for l,g in pairs)}
        f5={case:{'label':'SECONDARY',**values,'arms':{a:{'label':'SECONDARY descriptive honest' if a=='H' else 'SECONDARY',**grouped(byarm[a],variant,case)} for a in plan['arms']}} for case,values in hazards.items() if case.startswith('SECONDARY')}
        f6={'runs':len(runs),'matching_runs':len(runs)-len(mismatches[variant]),'mismatching_runs':mismatches[variant],
            'completed_steps':sum(r['steps_completed'] for r in runs),'heartbeat_count':sum(r['heartbeat_count'][variant] for r in runs)}
        f7={'run_count':len(runs),'spans_csv':h.P+'spans.csv','alarms_csv':h.P+'alarms.csv',
            'spans_by_case':{case:{'label':values['label'],'span_row_count':sum(row['variant']==variant and row['g_star_case']==case for row in span_rows),
                                   **({'section_4_caveat':h.CAVEAT} if case=='SECONDARY_2_5' else {})} for case,values in hazards.items()},
            'alarm_rows':sum(row['variant']==variant for row in alarm_rows)}
        results[variant]={'variant_label':label,'F1':f1,'F1a_SECONDARY':f1a,'F2':f2,'F3':f3,'F4':f4,'F5_SECONDARY':f5,'F6':f6,'F7':f7}
    h.csv_output(h.P+'spans.csv',span_rows,['arm','seed','variant','variant_label','g_star_case','g_star_label','g_star','k','start_step','end_step','section_4_caveat'])
    h.csv_output(h.P+'alarms.csv',alarm_rows,['arm','seed','variant','variant_label','record_type','step','channel','statistic_before_reset','statistic_after_reset','operational_channel'])
    summaries=[]
    for r in runs:
        for variant,v in r['variants'].items():
            row={k:r[k] for k in ('arm','seed','steps_completed','end_reason','extinct','shape_fallback_increase_step_0',
                  'shape_fallback_permitted_increase_after_step_0','shape_fallback_nonpermitted_increase_count',
                  'first_fewer_than_two_novelty_vectors_step','elapsed_seconds','raw_log','raw_log_sha256')}
            row.update(variant=variant,variant_label=v['variant_label'],heartbeat_count=v['heartbeat_count'],detection_alarm_step=v['detection_alarm_step'])
            for case,values in r['hazards'].items():
                confirmation=values['confirmation_step'];alarm=v['detection_alarm_step']
                row['confirmation_'+case]=confirmation;row['category_'+case]=category(confirmation,alarm)
                row['lead_steps_'+case]=confirmation-alarm if confirmation is not None and alarm is not None else None
            row['SECONDARY_2_5_section_4_caveat']=h.CAVEAT
            for channel,alarm in v['first_detection_steps'].items():row['first_detection_'+channel]=alarm
            summaries.append(row)
    h.csv_output(h.P+'runs.csv',summaries,list(summaries[0]))
    result={'status':'COMPLETE','variants':results,'hazards':hazards,'identity':h.identity(),'created_utc':h.now(),
            'no_constants_recomputed_for_use':True,'no_corrected_figure':True,'interpretation_reserved_for_operator':True}
    h.write(h.P+'results.json',result)
    if any(mismatches.values()):raise RuntimeError('F6 heartbeat mismatch')
    print(json.dumps({'analysis':'COMPLETE','runs':len(runs),'run_variant_rows':len(summaries),'recorded_steps':sum(r['steps_completed'] for r in runs)}),flush=True)

if __name__=='__main__':
    try:analyze()
    except BaseException as error:
        h.mark_halt('analysis',error)
        raise
