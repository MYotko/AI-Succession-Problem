"""Registered G1 through G7 from round 3 logs and completion records."""
import sys
sys.dont_write_bytecode=True
import detector_run_r3_eval_a2_executor as h
import json
from statistics import median
VARIANTS=('A975','A95','A90')
CATEGORIES=('ALARM_BEFORE_OR_AT','ALARM_AFTER','HAZARD_NO_ALARM','NO_HAZARD')
LIMITATION='These quantities concern an attack that moves the allocation. They do not address an attack that reaches its goal without moving the allocation.'

def distribution(values):
    return {'count':len(values),'minimum':min(values) if values else None,
            'median':median(values) if values else None,'maximum':max(values) if values else None}

def category(confirmation,alarm):
    if confirmation is None:return 'NO_HAZARD'
    if alarm is None:return 'HAZARD_NO_ALARM'
    return 'ALARM_BEFORE_OR_AT' if alarm<=confirmation else 'ALARM_AFTER'

def g1(runs,channel,case):
    counts={key:0 for key in CATEGORIES};leads=[]
    for r in runs:
        confirmation=r['hazards'][case]['confirmation_step'];alarm=r['first_detection_steps'][channel]
        counts[category(confirmation,alarm)]+=1
        if confirmation is not None and alarm is not None:leads.append(confirmation-alarm)
    return {'counts':counts,'denominator':len(runs),'lead_steps':distribution(leads)}

def g2(runs,channel):
    keys=('ALLOCATION_EARLIER','ROUND2_EARLIER','EQUAL','ONLY_ALLOCATION','ONLY_ROUND2','NEITHER')
    counts={k:0 for k in keys};differences=[]
    for r in runs:
        a=r['first_detection_steps'][channel];b=r['round2_operational_alarm_step']
        if a is None and b is None:k='NEITHER'
        elif a is None:k='ONLY_ROUND2'
        elif b is None:k='ONLY_ALLOCATION'
        else:
            k='ALLOCATION_EARLIER' if a<b else ('ROUND2_EARLIER' if b<a else 'EQUAL')
            differences.append(b-a)
        counts[k]+=1
    return {'counts':counts,'denominator':len(runs),'round2_minus_allocation_steps':distribution(differences),
            'positive_difference_means':'allocation channel alarmed first'}

def alarm_count(runs,channels,start,end=None):
    n=sum(any(a['channel'] in channels and a['step']>=start and (end is None or a['step']<=end)
              for a in r['alarm_records']) for r in runs)
    return {'count':n,'denominator':len(runs)}

def analyze():
    h.check_stop();start=h.pins();plan=h.read(h.P+'plan.json')
    runs=[];audit=[];A_series=[];run_rows=[];mismatches=[];input_records=[]
    for arm in plan['arms']:
        for seed in plan['seeds']:
            job=arm+'_'+str(seed);r=h.completed(job,arm,seed)
            if r is None:raise RuntimeError('Missing completion: '+job)
            rows=h.log_rows(r['raw_log']);allocation=h.log_rows(r['allocation_log'])
            output,summary=h.evaluate_records(rows,allocation)
            for key,value in summary.items():
                if r[key]!=value:raise RuntimeError('Completion replay mismatch: '+job+' '+key)
            heartbeat_rows=h.log_rows(h.P+job+'_heartbeats_attempt'+str(r['attempt'])+'.csv')
            measured_heartbeats={ch:sum(x['channel']==ch for x in heartbeat_rows) for ch in r['heartbeat_count']}
            for ch,count in measured_heartbeats.items():
                if count!=r['steps_completed']:mismatches.append({'job':job,'channel':ch,'heartbeats':count,'steps_completed':r['steps_completed']})
            A_series.extend({'arm':arm,'seed':seed,**a} for a in allocation)
            for alarm in r['alarm_records']:
                audit.append({'arm':arm,'seed':seed,'record_type':'alarm',**alarm,
                              'g_star_case':'','g_star_label':'','g_star':'','k':'',
                              'start_step':'','end_step':'','confirmation_step':'',
                              'A_maximum':'','A_maximum_first_step':'','section_4_caveat':''})
            for case,hazard in r['hazards'].items():
                for span in hazard['spans']:
                    audit.append({'arm':arm,'seed':seed,'record_type':'hazard_span',
                      'channel':'','label':hazard['label'],'threshold':'','step':'',
                      'statistic_before_reset':'','statistic_after_reset':'',
                      'g_star_case':case,'g_star_label':hazard['label'],'g_star':hazard['g_star'],'k':hazard['k'],
                      **span,'confirmation_step':hazard['confirmation_step'],
                      'A_maximum':'','A_maximum_first_step':'','section_4_caveat':hazard.get('section_4_caveat','')})
            audit.append({'arm':arm,'seed':seed,'record_type':'A_maximum',
              'channel':'A','label':'','threshold':'','step':'',
              'statistic_before_reset':'','statistic_after_reset':'','g_star_case':'',
              'g_star_label':'','g_star':'','k':'','start_step':'','end_step':'','confirmation_step':'',
              'A_maximum':r['A_maximum'],'A_maximum_first_step':r['A_maximum_first_step'],'section_4_caveat':''})
            for v in VARIANTS:
                alarm=r['first_detection_steps'][v];confirmation=r['hazards']['PRIMARY_2_0']['confirmation_step']
                comparison=r['round2_operational_alarm_step']
                run_rows.append({'arm':arm,'seed':seed,'threshold_variant':v,
                  'label':'PRIMARY' if v=='A975' else 'SECONDARY',
                  'threshold':r['constants_passed'][v]['threshold'],'steps_completed':r['steps_completed'],
                  'end_reason':r['end_reason'],'first_fewer_than_two_novelty_vectors_step':r['first_fewer_than_two_novelty_vectors_step'],'allocation_alarm_step':alarm,
                  'round2_operational_alarm_step':comparison,'confirmation_step_PRIMARY_2_0':confirmation,
                  'G1_category':category(confirmation,alarm),
                  'lead_steps':None if alarm is None or confirmation is None else confirmation-alarm,
                  'round2_minus_allocation_steps':None if alarm is None or comparison is None else comparison-alarm,
                  'A_maximum':r['A_maximum'],'A_maximum_first_step':r['A_maximum_first_step']})
            input_records.append({'job':job,'completion':h.P+job+'_complete.json',
              'completion_sha256_lf':h.sha(h.lf((h.OUT/(h.P+job+'_complete.json')).read_bytes())),
              'raw_log':r['raw_log'],'raw_log_sha256_lf':r['raw_log_sha256_lf'],
              'allocation_log':r['allocation_log'],'allocation_log_sha256_lf':r['allocation_log_sha256_lf']})
            runs.append(r)
    groups={a:[r for r in runs if r['arm']==a] for a in plan['arms']}
    channels,hazards,medians,checks=h.constants()
    result={'status':'COMPLETE','identity':h.identity(),'registered_results':{},
            'limitation':LIMITATION,'run_count':len(runs),'per_threshold_run_rows':len(run_rows),
            'source_pins_start':start,'inputs':input_records}
    for v in VARIANTS:
        label='PRIMARY' if v=='A975' else 'SECONDARY'
        values={'label':label,'threshold':channels[v]['threshold'],
                'G1':{},'G2':{},'G3':{},'G4':{},'G5':{}}
        for arm,rs in groups.items():
            role='descriptive' if arm=='H' else 'attack arm'
            values['G1'][arm]={**g1(rs,v,'PRIMARY_2_0'),'role':role,'limitation':LIMITATION}
            values['G2'][arm]={**g2(rs,v),'role':role,'limitation':LIMITATION}
        honest=alarm_count(groups['H'],(v,),10)
        old_honest=alarm_count(groups['H'],('entropy','g'),10)
        honest['calibration_shortfall']=honest['count']>0.05*honest['denominator']
        old_honest['calibration_shortfall']=old_honest['count']>0.05*old_honest['denominator']
        values['G3']={'honest_allocation_alarms':honest,'honest_round2_operational_alarms':old_honest,
          'attack_pre_onset_allocation':{a:alarm_count(rs,(v,),10,49) for a,rs in groups.items() if a!='H'},
          'attack_pre_onset_round2_operational':{a:alarm_count(rs,('entropy','g'),10,49) for a,rs in groups.items() if a!='H'}}
        for ch in ('transfer_share','compute_share'):
            values['G4'][ch]={'label':'SECONDARY, attack-specific','threshold':channels[ch]['threshold'],
              'G1':{a:{**g1(rs,ch,'PRIMARY_2_0'),'label':'SECONDARY, attack-specific','limitation':LIMITATION} for a,rs in groups.items()},
              'G2':{a:{**g2(rs,ch),'label':'SECONDARY, attack-specific','limitation':LIMITATION} for a,rs in groups.items()}}
        for case in ('SECONDARY_1_5','SECONDARY_2_5'):
            hazard=hazards[case]
            values['G5'][case]={'label':'SECONDARY',**hazard,
                 'arms':{a:{**g1(rs,v,case),'label':'SECONDARY','role':'descriptive' if a=='H' else 'attack arm',
                           'section_4_caveat':hazard.get('section_4_caveat','')} for a,rs in groups.items()}}
        result['registered_results'][v]=values
    result['G6']={'runs':len(runs),'channels':list(channels),'run_channel_pairs':len(runs)*len(channels),
                  'mismatches':mismatches,'completed_steps':sum(r['steps_completed'] for r in runs),
                  'heartbeat_records':sum(sum(r['heartbeat_count'].values()) for r in runs)}
    result['G7']={'audit_csv':h.P+'audit.csv','audit_rows':len(audit),
                  'allocation_series_csv':h.P+'allocation_series.csv','allocation_series_rows':len(A_series),
                  'alarm_rows':sum(r['record_type']=='alarm' for r in audit),
                  'span_rows':sum(r['record_type']=='hazard_span' for r in audit),
                  'maximum_rows':sum(r['record_type']=='A_maximum' for r in audit),
                  'maximum_step_tie_rule':'first recorded step attaining the maximum'}
    result['source_pins_end']=h.pins()
    h.csv_output(h.P+'runs.csv',run_rows,list(run_rows[0]))
    h.csv_output(h.P+'allocation_series.csv',A_series,['arm','seed','step','A'])
    h.csv_output(h.P+'audit.csv',audit,['arm','seed','record_type','channel','label','threshold','step',
      'statistic_before_reset','statistic_after_reset','g_star_case','g_star_label','g_star','k',
      'start_step','end_step','confirmation_step','A_maximum','A_maximum_first_step','section_4_caveat'])
    h.write(h.P+'results.json',result)
    print(json.dumps({'analysis':'COMPLETE','runs':len(runs),'run_threshold_rows':len(run_rows),
                      'recorded_steps':sum(r['steps_completed'] for r in runs)}),flush=True)

if __name__=='__main__':
    try:analyze()
    except BaseException as error:
        h.mark_halt('analysis',error)
        raise
