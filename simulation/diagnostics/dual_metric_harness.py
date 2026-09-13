"""Guarded committed-evidence and synthetic validation, with no simulation imports."""
import sys
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8')
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS'): os.environ[key]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
os.environ['GIT_OPTIONAL_LOCKS']='0'
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent
NEW_MODULE=ROOT/'simulation/attack_metrics_v2.py'
NULL=Path(os.devnull).resolve()
VIOLATIONS=[]
def allowed(path):
    p=Path(path).resolve()
    return p in (NEW_MODULE,NULL) or (p.parent==OUT and p.name.startswith('dual_metric_'))
def audit(event,args):
    bad=None
    if event=='open':
        path,mode,flags=args
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_APPEND|os.O_CREAT|os.O_TRUNC))
        if writing and not isinstance(path,int) and not allowed(path): bad='writable open: '+str(path)
    elif event=='os.rename':
        if not allowed(args[0]) or not allowed(args[1]): bad='rename outside scope'
    elif event in ('os.remove','os.mkdir','os.rmdir','os.link','os.symlink'): bad=event
    if bad:
        VIOLATIONS.append(bad)
        raise RuntimeError('WRITE SCOPE HALT: '+bad)
sys.addaudithook(audit)
import argparse,csv,hashlib,io,json,math,re,statistics,subprocess,traceback
from datetime import datetime,timezone

def now(): return datetime.now(timezone.utc).isoformat()
def lf(raw): return raw.replace(b'\r\n',b'\n')
def digest(raw): return hashlib.sha256(raw).hexdigest()
def read(name): return json.loads((OUT/name).read_text(encoding='utf-8'))
def textfile(name,text):
    if '\u2014' in text: raise RuntimeError('Em dash in authored artifact')
    with (OUT/name).open('w',encoding='utf-8',newline='\n') as f:
        f.write(text);f.flush();os.fsync(f.fileno())
def write(name,obj): textfile(name,json.dumps(obj,indent=2,ensure_ascii=True,allow_nan=False,sort_keys=True)+'\n')
def csvfile(name,rows):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
        f.flush();os.fsync(f.fileno())
def git(*args):
    p=subprocess.run(['git',*args],cwd=ROOT,capture_output=True)
    if p.returncode: raise RuntimeError('Read-only Git command failed: '+repr(args)+' '+p.stderr.decode('utf-8',errors='replace'))
    return p.stdout

def blob(commit,path,expected=None):
    raw=git('cat-file','blob',commit+':'+path)
    sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    if expected is not None and sha!=expected: raise RuntimeError('Evidence blob SHA mismatch: '+path)
    return raw,{'commit':commit,'path':path,'blob_sha1':sha,'sha256_lf':digest(lf(raw))}
def csv_blob(commit,path,expected=None):
    raw,provenance=blob(commit,path,expected)
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    rows=list(reader)
    provenance.update(row_count=len(rows),columns=reader.fieldnames)
    return rows,provenance

def t1():
    state=read('dual_metric_state.json')
    rows,source=csv_blob(state['head'],'simulation/diagnostics/veto_floor2_runs.csv')
    arms={name:[r for r in rows if r['arm']==name] for name in ('AS_PUBLISHED','ZERO_STRENGTH','ZERO_DEPENDENCY')}
    checks={'rows_900':len(rows)==900,'three_arms_300_each':set(r['arm'] for r in rows)==set(arms) and all(len(r)==300 for r in arms.values())}
    exceptions=[r for r in rows if int(r['yield_condition_met_count'])!=1+int(r['yield_condition_blocked_count'])]
    checks['D6_identity_all_900']=not exceptions
    indexed={name:{r['seed']:r for r in arm} for name,arm in arms.items()}
    checks['unique_seed_each_arm']=all(len(indexed[name])==len(arms[name]) for name in arms)
    checks['total_exact_pairing']=all(set(indexed[name])==set(indexed['AS_PUBLISHED']) for name in arms)
    if not all(checks.values()):
        write('dual_metric_t1.json',{'status':'HALTED','checks':checks,'source':source,'exceptions':exceptions})
        raise RuntimeError('T1 corpus cardinality, pairing, or identity gate failed')
    comparison={};pair_rows=[]
    for control in ('ZERO_STRENGTH','ZERO_DEPENDENCY'):
        differences=[]
        for seed in sorted(indexed['AS_PUBLISHED']):
            tr=int(indexed['AS_PUBLISHED'][seed]['yield_condition_blocked_count']);cr=int(indexed[control][seed]['yield_condition_blocked_count'])
            differences.append(tr-cr)
            pair_rows.append({'control':control,'seed':seed,'treatment_blocks':tr,'control_blocks':cr,'difference':tr-cr})
        n=len(differences);mean=statistics.fmean(differences);se=statistics.stdev(differences)/math.sqrt(n);statistic=mean/se if se else None
        result={'n_pairs':n,'mean_difference':mean,'paired_standard_error':se,'t_statistic':statistic,'t_statistic_note':None if se else 'Paired standard error is exactly zero; t statistic is undefined.','treatment_block_total':sum(int(r['yield_condition_blocked_count']) for r in arms['AS_PUBLISHED']),'control_block_total':sum(int(r['yield_condition_blocked_count']) for r in arms[control]),'treatment_vote_total':sum(int(r['yield_condition_met_count']) for r in arms['AS_PUBLISHED']),'control_vote_total':sum(int(r['yield_condition_met_count']) for r in arms[control])}
        comparison[control]=result
        checks[control+'_pairs_300']=n==300
        checks[control+'_mean_6dp']=format(mean,'.6f')=='0.060000'
        checks[control+'_se_6dp']=format(se,'.6f')=='0.015272'
        checks[control+'_t_4dp']=statistic is not None and format(statistic,'.4f')=='3.9289'
        checks[control+'_blocks']=result['treatment_block_total']==43 and result['control_block_total']==25
        checks[control+'_votes']=result['treatment_vote_total']==343 and result['control_vote_total']==325
    checks['both_controls_identical']=comparison['ZERO_STRENGTH']==comparison['ZERO_DEPENDENCY']
    result={'status':'PASS' if all(checks.values()) else 'HALTED','utc':now(),'source':source,'checks':checks,'arm_counts':{name:len(arm) for name,arm in arms.items()},'D6_identity_exceptions':exceptions,'comparison':comparison,'method':'statistics.fmean and statistics.stdev (sample ddof=1), divided by math.sqrt(n). Inputs parsed directly from the committed blob. No new module imported.'}
    csvfile('dual_metric_t1_pairs.csv',pair_rows)
    write('dual_metric_t1.json',result)
    state.update(status='T1_PASSED' if all(checks.values()) else 'HALTED',T1_completed_utc=now(),T1_source=source)
    write('dual_metric_state.json',state)
    print(json.dumps({k:v for k,v in result.items() if k!='source'},ensure_ascii=True),flush=True)
    if not all(checks.values()): raise RuntimeError('T1 reproduction gate failed')

def validate():
    import importlib.util
    from collections import Counter,defaultdict
    from fractions import Fraction
    from importlib.metadata import version
    state=read('dual_metric_state.json');baseline=read('dual_metric_t1.json')
    spec=importlib.util.spec_from_file_location('attack_metrics_v2',NEW_MODULE)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    rows,source=csv_blob(state['head'],'simulation/diagnostics/veto_floor2_runs.csv',baseline['source']['blob_sha1'])
    arms={name:[r for r in rows if r['arm']==name] for name in ('AS_PUBLISHED','ZERO_STRENGTH','ZERO_DEPENDENCY')}
    comparisons={};checks={}
    for control in ('ZERO_STRENGTH','ZERO_DEPENDENCY'):
        result=module.paired_difference(arms['AS_PUBLISHED'],arms[control],'yield_condition_blocked_count')
        expected={key:baseline['comparison'][control][key] for key in result}
        checks['T3a_'+control+'_exact_match']=result==expected
        comparisons[control]=result
    control=[{'seed':seed,'count':count} for seed,count in zip((11,22,33,44),(0,2,5,11))]
    treatment=[{'seed':r['seed'],'count':r['count']+4} for r in control]
    positive=module.paired_difference(treatment,list(reversed(control)),'count')
    negative=module.paired_difference(control,list(reversed(control)),'count')
    checks['T3b_constant_offset']=positive['mean_difference']==4.0 and positive['paired_standard_error']==0.0
    checks['T3b_null_t_with_note']=positive['t_statistic'] is None and bool(positive['t_statistic_note'])
    checks['T3c_identical_arms']=negative['mean_difference']==0.0
    guards={}
    for label,tr,co in [('treatment_only',treatment+[{'seed':55,'count':8}],control),('control_only',treatment,control+[{'seed':55,'count':4}]),('duplicate_seed',treatment+[treatment[0]],control),('seed_type_mismatch',[dict(r,seed=str(r['seed'])) for r in treatment],control)]:
        try: module.paired_difference(tr,co,'count')
        except ValueError as e: guards[label]={'raised':True,'exception':type(e).__name__,'message':str(e)}
        else: guards[label]={'raised':False}
    checks['T3d_unmatched_treatment_seed_raises']=guards['treatment_only']['raised']
    checks['total_pairing_extra_guards']=all(r['raised'] for r in guards.values())
    bool_fixture=[{'action_modified':value} for value in (True,False,'True','False',1,0,'1','0')]
    checks['action_count_boolean_parsing']=module.action_change_count(bool_fixture)==(8,4)
    checks['action_count_empty'] = module.action_change_count([])==(0,0)
    try: module.action_change_count([{'action_modified':'unknown'}])
    except ValueError: checks['action_count_rejects_invalid_flag']=True
    else: checks['action_count_rejects_invalid_flag']=False
    preliminary={'status':'PASS' if all(checks.values()) else 'HALTED','comparison':comparisons,'positive':positive,'negative':negative,'guards':guards,'checks':checks,'source':source,'utc':now()}
    write('dual_metric_module_controls.json',preliminary)
    if not all(checks.values()): raise RuntimeError('T3a-d module validation failed')
    ladder=Counter(Fraction(int(r['yield_condition_blocked_count']),int(r['yield_condition_met_count'])) for r in arms['AS_PUBLISHED'])
    expected_ladder={Fraction(0):263,Fraction(1,2):32,Fraction(2,3):4,Fraction(3,4):1}
    checks['T3e_retired_ladder_matches']=dict(ladder)==expected_ladder
    checks['T3e_no_value_between_zero_and_half']=not any(0<value<Fraction(1,2) for value in ladder)
    ladder_rows=[{'retired_blocked_over_met_exact':str(value),'retired_blocked_over_met':float(value),'n_runs':count} for value,count in sorted(ladder.items())]
    csvfile('dual_metric_retired_ladder.csv',ladder_rows)
    if not checks['T3e_retired_ladder_matches'] or not checks['T3e_no_value_between_zero_and_half']: raise RuntimeError('T3e retired-quantity ladder mismatch')
    z=statistics.NormalDist().inv_cdf(.975)
    wilson=[]
    for name in ('AS_PUBLISHED','ZERO_STRENGTH'):
        blocks=sum(int(r['yield_condition_blocked_count']) for r in arms[name]);votes=sum(int(r['yield_condition_met_count']) for r in arms[name])
        rate=blocks/votes;denom=1+z*z/votes
        center=(rate+z*z/(2*votes))/denom
        half=z*math.sqrt(rate*(1-rate)/votes+z*z/(4*votes*votes))/denom
        wilson.append({'arm':name,'blocks':blocks,'votes':votes,'per_vote_rate':rate,'wilson_95_lower':center-half,'wilson_95_upper':center+half})
    overlap=max(r['wilson_95_lower'] for r in wilson)<=min(r['wilson_95_upper'] for r in wilson)
    csvfile('dual_metric_wilson.csv',wilson)
    write('dual_metric_contrasts.json',{'ladder':ladder_rows,'paired_difference':comparisons,'wilson':wilson,'wilson_z':z,'wilson_intervals_overlap':overlap,'retired_quantity_note':'The discrete ladder is a property of the retired blocked/met quantity. Ratios and Wilson intervals are calculated only in this diagnostic, not by attack_metrics_v2.','utc':now()})
    manifest_raw,manifest_source=blob(state['head'],'simulation/diagnostics/attack_vector_revalidation_manifest.md')
    manifest_text=manifest_raw.decode('utf-8')
    tag=re.search(r'Evidence tag: `([^`]+)`',manifest_text).group(1)
    evidence_commit=git('rev-parse',tag+'^{}').decode('utf-8').strip()
    section=manifest_text.split('## Authoritative files',1)[1].split('## Excluded artifacts',1)[0]
    selections=[];excluded=[]
    for line in section.splitlines():
        if not line.startswith('|'): continue
        cells=[c.strip().strip('`') for c in line.strip().strip('|').split('|')]
        if len(cells)!=4 or cells[0] in ('Vector','---'): continue
        if not cells[2].isdigit():
            excluded.append({'vector':cells[0],'run_directory':cells[1],'manifest_row_count':cells[2],'reason':'Manifest labels this as analytic, 0 MC; not a live vector.'})
            continue
        selections.append({'vector':cells[0],'run_directory':cells[1],'expected_rows':int(cells[2]),'expected_blob':cells[3]})
    paths=git('ls-tree','-r','--name-only',evidence_commit,'data/attack_vector_revalidation_v2').decode('utf-8').splitlines()
    evidence=[source,manifest_source];grouped=defaultdict(list);veto_modes=defaultdict(list)
    for selection in selections:
        candidates=[path for path in paths if Path(path).name=='results.csv' and Path(path).parent.name==selection['run_directory'] and Path(path).parent.parent.name==selection['vector']]
        if len(candidates)!=1: raise RuntimeError('Manifest entry did not resolve uniquely: '+selection['run_directory'])
        path=candidates[0]
        parsed,provenance=csv_blob(evidence_commit,path,selection['expected_blob'])
        provenance['manifest_run_directory']=selection['run_directory']
        provenance['manifest_expected_rows']=selection['expected_rows']
        evidence.append(provenance)
        write('dual_metric_evidence.json',{'evidence_tag':tag,'evidence_commit':evidence_commit,'selection_manifest':manifest_source,'evidence_files':evidence,'excluded_analytic':excluded})
        if len(parsed)!=selection['expected_rows']: raise RuntimeError('Manifest row count mismatch: '+path)
        if 'action_modified' not in provenance['columns'] or 'defense_active' not in provenance['columns']: raise RuntimeError('Comparable-metric fields not recorded: '+path)
        for row in parsed:
            if row['vector']!=selection['vector']: raise RuntimeError('Recorded vector differs from manifest: '+path)
            defense_text=row['defense_active'].strip().lower()
            if defense_text not in ('true','false'): raise RuntimeError('Unknown recorded defense state: '+path)
            defense=defense_text=='true'
            grouped[(selection['vector'],defense)].append(row)
            if selection['vector']=='biological_veto_capture':
                mode=row.get('defense_mode','')
                if not mode:
                    params=json.loads(row.get('parameters_json','{}'))
                    mode=params.get('defense_mode','')
                if mode: veto_modes[(defense,mode)].append(row)
    vector_rows=[]
    for (vector,defense),records in sorted(grouped.items()):
        n,modified=module.action_change_count(records)
        vector_rows.append({'vector':vector,'defense_active':defense,'n_runs':n,'n_action_modified':modified})
    csvfile('dual_metric_vector_counts.csv',vector_rows)
    mode_rows=[]
    for (defense,mode),records in sorted(veto_modes.items()):
        n,modified=module.action_change_count(records)
        mode_rows.append({'vector':'biological_veto_capture','defense_active':defense,'defense_mode':mode,'n_runs':n,'n_action_modified':modified})
    if mode_rows: csvfile('dual_metric_veto_mode_counts.csv',mode_rows)
    checks['T3g_ten_live_vectors']=len({r['vector'] for r in vector_rows})==10
    checks['T3g_two_defense_arms_each']=len(vector_rows)==20
    checks['T3g_manifest_live_rows_9900']=sum(r['n_runs'] for r in vector_rows)==9900
    result={'status':'PASS' if all(checks.values()) else 'HALTED','utc':now(),'checks':checks,'comparison':comparisons,'positive_control':positive,'negative_control':negative,'guard_controls':guards,'retired_ladder':ladder_rows,'wilson':wilson,'wilson_z':z,'wilson_intervals_overlap':overlap,'vector_counts':vector_rows,'veto_mode_counts':mode_rows,'evidence_tag':tag,'evidence_commit':evidence_commit,'evidence_files':evidence,'excluded_analytic':excluded,'machine':os.environ['COMPUTERNAME'],'python':sys.version,'numpy_installed_version':version('numpy'),'numpy_execution':'Version read from installed package metadata; no NumPy computation needed.','module_sha256_lf':digest(lf(NEW_MODULE.read_bytes())),'model_steps':0,'simulation_imports':0}
    write('dual_metric_t3.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('evidence_files','guard_controls','vector_counts','veto_mode_counts','excluded_analytic','retired_ladder')},ensure_ascii=True),flush=True)
    print(json.dumps({'vector_counts':vector_rows,'veto_mode_counts':mode_rows},ensure_ascii=True),flush=True)
    if not all(checks.values()): raise RuntimeError('T3 corpus validation failed')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('operation',choices=['t1','validate']);args=parser.parse_args()
    try:
        if args.operation=='t1': t1()
        else: validate()
    except BaseException as e:
        write('dual_metric_failure_'+args.operation+'.json',{'halt':str(e),'utc':now(),'violations':VIOLATIONS,'traceback':traceback.format_exc()})
        print('HALT: '+str(e),flush=True);raise SystemExit(2)
if __name__=='__main__': main()
