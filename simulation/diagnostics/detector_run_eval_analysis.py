"""Registered E1 through E6 from stage 2 raw logs and completion records."""
import sys
sys.dont_write_bytecode=True
import detector_run_eval_executor as h
import numpy as np
import csv,json
from collections import Counter

CATEGORIES=('DETECTED_BEFORE_OR_AT','DETECTED_AFTER','CROSSED_UNDETECTED','NO_CROSSING')
PRIMARY='PRIMARY_2_0'

def category(crossing,detection):
    if crossing is None:return 'NO_CROSSING'
    if detection is None:return 'CROSSED_UNDETECTED'
    return 'DETECTED_BEFORE_OR_AT' if detection<=crossing else 'DETECTED_AFTER'

def grouped(runs,label=PRIMARY,channel=None):
    counts={key:0 for key in CATEGORIES};margins=[]
    for r in runs:
        crossing=r['t_star'][label]
        detection=r['detection_alarm_step'] if channel is None else r['first_detection_steps'][channel]
        c=category(crossing,detection);counts[c]+=1
        if c=='DETECTED_BEFORE_OR_AT':margins.append(crossing-detection)
    return {'n_runs':len(runs),'counts':counts,'margin_steps':{'count':len(margins),
            'minimum':min(margins) if margins else None,'median':float(np.median(margins)) if margins else None,
            'maximum':max(margins) if margins else None}}

def before(detection,crossing):return crossing is not None and detection is not None and detection<=crossing

def analyze():
    h.check_stop();h.pins()
    plan=h.read(h.P+'plan.json');execution=h.read(h.P+'execution.json')
    if execution['status']!='COMPLETE':raise RuntimeError('Registered analysis requires a complete batch')
    runs=[];rawcounts={};hb_mismatches=[]
    for arm in plan['arms']:
        for seed in plan['seeds']:
            r=h.completed(arm+'_'+str(seed),arm,seed)
            if r is None:raise RuntimeError('Missing completion record')
            rows=h.log_rows(r['raw_log']);rawcounts[r['job']]=len(rows)
            # Re-read the raw series to verify the recorded crossing and detection bookkeeping.
            for label,value in plan['g_stars'].items():
                expected=next((x['step'] for x in rows if x['step']>=50 and x['g']>=value),None)
                if r['t_star'][label]!=expected:raise RuntimeError('Crossing bookkeeping differs from raw log')
            op=[a['step'] for a in r['alarm_records'] if a['operational_channel']]
            expected=next((step for step in op if step>=50),None)
            if r['detection_alarm_step']!=expected:raise RuntimeError('Operational alarm bookkeeping differs')
            for channel in ('entropy','g','L'):
                expected=next((a['step'] for a in r['alarm_records'] if a['channel']==channel and a['step']>=50),None)
                if r['first_detection_steps'][channel]!=expected:raise RuntimeError('Channel alarm bookkeeping differs')
            hbfile=next(name for name in r['detector_logs'] if '_heartbeats_' in name)
            with(h.OUT/hbfile).open(encoding='utf-8',newline='') as f:heartbeats=list(csv.DictReader(f))
            if len(heartbeats)!=len(rows) or r['heartbeat_count']!=len(rows):hb_mismatches.append(r['job'])
            if [int(x['heartbeat_counter']) for x in heartbeats]!=list(range(1,len(rows)+1)):
                raise RuntimeError('Heartbeat sequence mismatch')
            runs.append(r)
    byarm={a:[r for r in runs if r['arm']==a] for a in plan['arms']}
    honest={r['seed']:r for r in byarm['H']};attacks=plan['arms'][1:]
    e1={a:{'label':'descriptive honest' if a=='H' else 'PRIMARY',**grouped(byarm[a])} for a in plan['arms']}
    e1a={}
    for a in attacks:
        selected=[r for r in byarm[a] if r['t_star'][PRIMARY] is not None and
                  (honest[r['seed']]['t_star'][PRIMARY] is None or honest[r['seed']]['t_star'][PRIMARY]>r['t_star'][PRIMARY])]
        e1a[a]={'label':'SECONDARY','eligible_seeds':[r['seed'] for r in selected],**grouped(selected)}
    e2={}
    for a in attacks:
        counts={'entropy_first':0,'g_first':0,'same_step':0,'neither_at_or_after_50':0}
        for r in byarm[a]:
            entropy=r['first_detection_steps']['entropy'];g=r['first_detection_steps']['g']
            if entropy is None and g is None:key='neither_at_or_after_50'
            elif entropy==g:key='same_step'
            elif g is None or(entropy is not None and entropy<g):key='entropy_first'
            else:key='g_first'
            counts[key]+=1
        e2[a]={'n_runs':len(byarm[a]),'with_operational_detection':len(byarm[a])-counts['neither_at_or_after_50'],**counts}
    honest_alarm=sum(any(x['operational_channel'] and x['step']>=10 for x in r['alarm_records']) for r in byarm['H'])
    e3={'honest':{'count':honest_alarm,'denominator':len(byarm['H']),
                 'calibration_shortfall':honest_alarm>0.05*len(byarm['H'])},
        'attack_pre_onset':{a:{'count':sum(any(x['operational_channel'] and 10<=x['step']<50 for x in r['alarm_records']) for r in byarm[a]),'denominator':len(byarm[a])} for a in attacks}}
    e4={'L_channel':{a:{'label':'descriptive honest' if a=='H' else 'PRIMARY',**grouped(byarm[a],channel='L')} for a in plan['arms']},'paired_channel_counts':{}}
    for a in attacks:
        pairs=[(before(r['first_detection_steps']['L'],r['t_star'][PRIMARY]),before(r['first_detection_steps']['g'],r['t_star'][PRIMARY])) for r in byarm[a]]
        e4['paired_channel_counts'][a]={'denominator':len(pairs),'L_before_or_at_g_not':sum(l and not g for l,g in pairs),'g_before_or_at_L_not':sum(g and not l for l,g in pairs)}
    e5={label:{'label':'SECONDARY','g_star':value,'arms':{a:{'label':'SECONDARY descriptive honest' if a=='H' else 'SECONDARY',**grouped(byarm[a],label=label)} for a in plan['arms']}} for label,value in plan['g_stars'].items() if label.startswith('SECONDARY')}
    e6={'runs':len(runs),'runs_matching':len(runs)-len(hb_mismatches),'mismatching_runs':hb_mismatches,
        'completed_steps':sum(rawcounts.values()),'heartbeat_count':sum(r['heartbeat_count'] for r in runs)}
    result={'status':'COMPLETE','E1':e1,'E1a_SECONDARY':e1a,'E2':e2,'E3':e3,'E4':e4,'E5_SECONDARY':e5,'E6':e6,
            'identity':h.identity(),'g_stars':plan['g_stars'],'no_constants_recomputed':True,'no_corrected_figure':True,
            'interpretation_reserved_for_operator':True,'created_utc':h.now()}
    h.write(h.P+'results.json',result)
    summaries=[]
    for r in runs:
        row={k:r[k] for k in ('arm','seed','steps_completed','end_reason','extinct','heartbeat_count','detection_alarm_step',
             'shape_fallback_increase_step_0','shape_fallback_permitted_increase_after_step_0',
             'shape_fallback_nonpermitted_increase_count','first_fewer_than_two_novelty_vectors_step',
             'adapter_active_steps','action_modified_steps','elapsed_seconds','raw_log','raw_log_sha256')}
        for label,crossing in r['t_star'].items():row['t_star_'+label]=crossing;row['E1_'+label]=category(crossing,r['detection_alarm_step'])
        for channel,detection in r['first_detection_steps'].items():row['first_detection_'+channel]=detection
        row['E4_L_category']=category(r['t_star'][PRIMARY],r['first_detection_steps']['L'])
        summaries.append(row)
    h.csv_output(h.P+'runs.csv',summaries,list(summaries[0]))
    if hb_mismatches:raise RuntimeError('E6 heartbeat mismatch: '+repr(hb_mismatches))
    print(json.dumps({'analysis':'COMPLETE','runs':len(runs),'steps':e6['completed_steps']}),flush=True)

if __name__=='__main__':
    try:analyze()
    except BaseException as error:
        h.mark_halt('analysis',error)
        raise
