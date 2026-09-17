"""Registered round 3 offline channels; committed constants are never recomputed."""
import sys
sys.dont_write_bytecode=True
import json
import numpy as np
AXES=('x_compute','x_bio_welfare','x_novelty_agency','x_institutional_capacity','x_transfer_comprehension','x_resilience')
VARIANTS=('A975','A95','A90')

def allocation_distance(row,medians):
    x=np.asarray([row[a] for a in AXES],dtype=np.float64)
    m=np.asarray([medians[a] for a in AXES],dtype=np.float64)
    return float(np.sum(np.abs(x-m)))

def constants(h):
    stage=json.loads(h.pinned_blob('simulation/diagnostics/detector_run_r3_a3_constants.json'))
    old=json.loads(h.pinned_blob('simulation/diagnostics/detector_run_cal_constants.json'))
    r2=json.loads(h.pinned_blob('simulation/diagnostics/detector_run_r2_constants.json'))
    checks=[];channels={}
    def compare(name,actual,expected):
        checks.append({'quantity':name,'actual_binary64_hex':float(actual).hex(),
                       'expected_binary64_hex':float(expected).hex(),
                       'passed':float(actual).hex()==float(expected).hex()})
    medians={a:stage['median_allocation'][a] for a in AXES}
    for a in AXES:
        compare('median '+a,medians[a],float.fromhex(stage['binary64_hex']['median_allocation'][a]))
    ap=stage['channels']['A']
    for variant,pct in zip(VARIANTS,(97.5,95.0,90.0)):
        entry=next(r for r in ap['thresholds'] if r['percentile']==pct)
        channels[variant]={'reference':ap['reference'],'allowance':ap['allowance'],
                           'threshold':entry['threshold'],'direction':'upper','field':'A',
                           'label':entry['label'],'threshold_percentile':pct}
    for name,field in [('transfer_share','x_transfer_comprehension'),('compute_share','x_compute')]:
        p=stage['channels'][name]
        channels[name]={'reference':p['reference'],'allowance':p['allowance'],
                        'threshold':p['thresholds'][0]['threshold'],'direction':p['direction'],
                        'field':field,'label':'SECONDARY, attack-specific','threshold_percentile':97.5}
    for name,field,direction in [('entropy','h_n_latest','lower'),('g','g','upper'),('L','L_t','lower')]:
        p=stage['round1_constants_carried_forward'][name]
        channels[name]={**p,'direction':direction,'field':field,'label':'comparison'}
        for key in ('reference','allowance','threshold'):
            compare(name+' '+key,p[key],old['channels'][name][key])
            compare(name+' stage A hex '+key,p[key],float.fromhex(stage['binary64_hex']['round1_constants_carried_forward'][name][key]))
    for name in VARIANTS+('transfer_share','compute_share'):
        src='A' if name in VARIANTS else name
        p=stage['channels'][src]
        for key in ('reference','allowance'):
            compare(name+' '+key,channels[name][key],p[key])
            compare(name+' stage A hex '+key,channels[name][key],float.fromhex(stage['binary64_hex']['channels'][src][key]))
        idx=next(i for i,r in enumerate(p['thresholds']) if r['percentile']==channels[name]['threshold_percentile'])
        compare(name+' threshold',channels[name]['threshold'],p['thresholds'][idx]['threshold'])
        compare(name+' threshold hex',channels[name]['threshold'],float.fromhex(stage['binary64_hex']['channels'][src]['thresholds'][idx]['threshold']))
    hazards={}
    for case,p in stage['round2_hazards_carried_forward'].items():
        hazards[case]={'g_star':p['g_star'],'k':p['k'],'label':p['label']}
        for key in ('g_star','k'):
            compare(case+' '+key,p[key],r2['sustained_crossing_k'][case][key])
            compare(case+' stage A hex '+key,p[key],float.fromhex(stage['binary64_hex']['round2_hazards_carried_forward'][case][key]))
        if case=='SECONDARY_2_5':
            hazards[case]['section_4_caveat']=p['required_section_4_caveat']
    if not all(c['passed'] for c in checks):raise RuntimeError('Constants conformance failed: '+json.dumps(checks))
    return channels,hazards,medians,checks

def constants_gate(h):
    channels,hazards,medians,checks=constants(h)
    r={'passed':True,'channels_passed':channels,'hazards_passed':hazards,
       'medians_passed':medians,'checks':checks,'identity':h.identity(),'utc':h.now(),
       'no_constant_derived_or_recomputed':True}
    h.write(h.P+'constants_gate.json',r)
    return r

def allocation_gate(h):
    result=h.read(h.P+'gate_recorder_result.json')
    rows=h.log_rows(result['raw_log']);values=h.log_rows(result['allocation_log'])
    channels,hazards,medians,checks=constants(h)
    comparisons=[];first=None
    if len(rows)!=25 or len(values)!=25:first={'field':'row_count','rows':len(rows),'A_rows':len(values)}
    for row,saved in zip(rows,values):
        x=np.asarray([row[axis] for axis in AXES],dtype=np.float64)
        m=np.asarray([medians[axis] for axis in AXES],dtype=np.float64)
        value=float(np.sum(np.abs(x-m)))
        passed=value==saved['A'] and row['step']==saved['step']
        comparisons.append({'step':row['step'],'recorded_A':saved['A'],'recomputed_A':value,'passed':passed})
        if not passed and first is None:first=comparisons[-1]
    output={'passed':first is None,'first_difference':first,'comparisons':comparisons,
            'steps':len(rows),'identity':h.identity(),'allocation_log':result['allocation_log'],
            'raw_log':result['raw_log'],'utc':h.now()}
    h.write(h.P+'allocation_gate.json',output)
    if first is not None:raise RuntimeError('A-definition gate failed: '+json.dumps(first))
    return output

def evaluate_records(h,rows,allocation_rows):
    import cusum_detector_v2 as detector
    channels,hazards,medians,checks=constants(h)
    if len(rows)!=len(allocation_rows):raise RuntimeError('Allocation log length mismatch')
    for r,a in zip(rows,allocation_rows):
        if r['step']!=a['step'] or allocation_distance(r,medians)!=a['A']:
            raise RuntimeError('Recorded A differs from recorded shares at step '+str(r['step']))
    steps=[r['step'] for r in rows]
    heartbeats=[];alarms=[];first={};counts={}
    for name,p in channels.items():
        values=[a['A'] for a in allocation_rows] if p['field']=='A' else [r[p['field']] for r in rows]
        output=detector.channel_cusum(steps,values,reference=p['reference'],allowance=p['allowance'],
                                      direction=p['direction'],threshold=p['threshold'])
        counts[name]=len(output['statistics'])
        if counts[name]!=len(rows):raise RuntimeError('Heartbeat count mismatch for '+name)
        first[name]=None
        for i,step in enumerate(steps):
            heartbeats.append({'record_type':'heartbeat','channel':name,'label':p['label'],
              'threshold':p['threshold'],'step':step,'heartbeat_counter':i+1,
              'start_statistic':output['start_statistics'][i],
              'candidate_statistic':output['candidate_statistics'][i],'statistic':output['statistics'][i]})
            if output['alarms'][i]:
                alarms.append({'record_type':'alarm','channel':name,'label':p['label'],
                  'threshold':p['threshold'],'step':step,
                  'statistic_before_reset':output['candidate_statistics'][i],
                  'statistic_after_reset':output['statistics'][i]})
                if step>=50 and first[name] is None:first[name]=step
    operational=min((s for c,s in first.items() if c in ('entropy','g') and s is not None),default=None)
    recorded=h.hazard_records(rows,hazards)
    span_rows=[]
    for case,p in recorded.items():
        for span in p['spans']:
            span_rows.append({'g_star_case':case,'g_star_label':p['label'],'g_star':p['g_star'],
                              'k':p['k'],**span,'section_4_caveat':p.get('section_4_caveat','')})
    peak=max(allocation_rows,key=lambda r:r['A'])
    summary={'heartbeat_count':counts,'alarm_records':alarms,'hazards':recorded,
             'allocation_alarm_steps':{v:first[v] for v in VARIANTS},
             'round2_operational_alarm_step':operational,'first_detection_steps':first,
             'constants_passed':channels,'medians_passed':medians,'constants_bitwise_checks':checks,
             'A_maximum':peak['A'],'A_maximum_first_step':peak['step']}
    return {'heartbeats':heartbeats,'alarm_records':alarms,'span_records':span_rows},summary
