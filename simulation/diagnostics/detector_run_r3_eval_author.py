"""Author round 3 executor copies through the shell; no scientific execution."""
import sys
sys.dont_write_bytecode=True
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'simulation'/'diagnostics'
P='detector_run_r3_eval_'
def allowed(path):
    if isinstance(path,int):return path in (0,1,2)
    p=Path(path).resolve()
    return p==Path(os.devnull).resolve() or (p.parent==OUT and p.name.startswith(P))
def guard(event,args):
    if event=='open':
        path,mode,flags=args
        if (any(c in (mode or '') for c in 'wax+') or flags&(os.O_WRONLY|os.O_RDWR|os.O_APPEND|os.O_CREAT|os.O_TRUNC)) and not allowed(path):
            raise PermissionError('Out-of-scope writable open')
    elif event=='os.rename' and (not allowed(args[0]) or not allowed(args[1])):
        raise PermissionError('Out-of-scope rename')
sys.addaudithook(guard)
import ast,subprocess,json,hashlib
def get(name):
    return subprocess.run(['git','cat-file','blob','HEAD:simulation/diagnostics/'+name],capture_output=True,check=True).stdout
def replace_once(text,old,new):
    if text.count(old)!=1:raise RuntimeError('Authoring anchor count differs: '+repr(old[:100]))
    return text.replace(old,new,1)
def replace_function(text,name,new):
    nodes=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name]
    if len(nodes)!=1:raise RuntimeError('Function authoring anchor differs: '+name)
    node=nodes[0];lines=text.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1])+new+'\n'+''.join(lines[node.end_lineno:])
raw=get('detector_run_r2_eval_executor.py')
text=raw.decode('utf-8').replace('detector_run_r2_eval_','detector_run_r3_eval_')
text=replace_function(text,'derivation_gate','')
text=replace_function(text,'constants',"""def constants():
    return registered.constants(sys.modules[__name__])
""")
text=replace_function(text,'constants_gate',"""def constants_gate():
    return registered.constants_gate(sys.modules[__name__])
""")
text=replace_function(text,'evaluate_records',"""def evaluate_records(rows,allocation_rows):
    return registered.evaluate_records(sys.modules[__name__],rows,allocation_rows)

def allocation_definition_gate():
    return registered.allocation_gate(sys.modules[__name__])
""")
text=replace_once(text,"    runtime=metadata(np)\n    write(P+job+'_initial.json'", "    channels,hazards,medians,constant_checks=constants()\n    allocation_rows=[]\n    runtime=metadata(np)\n    write(P+job+'_initial.json'")
text=replace_once(text,"            count=row['novelty_vector_count']",
"""            allocation_rows.append({'arm':arm,'seed':seed,'step':step,'A':registered.allocation_distance(row,medians)})
            count=row['novelty_vector_count']""")
text=replace_once(text,"    if gate:result['datacollector']=model.datacollector",
"""    allocation_name=P+job+'_allocation_attempt'+str(attempt)+'.csv'
    csv_output(allocation_name,allocation_rows,['arm','seed','step','A'])
    result['allocation_log']=allocation_name
    result['allocation_log_sha256_lf']=sha(lf((OUT/allocation_name).read_bytes()))
    if gate:result['datacollector']=model.datacollector""")
text=replace_once(text,"evaluate_records(log_rows(final))","evaluate_records(log_rows(final),allocation_rows)")
text=replace_once(text,"['variant','variant_label','record_type','step','heartbeat_counter','S_H','S_g','S_L']",
"['record_type','channel','label','threshold','step','heartbeat_counter','start_statistic','candidate_statistic','statistic']")
text=replace_once(text,"['variant','variant_label','record_type','step','channel','statistic_before_reset','statistic_after_reset','operational_channel']",
"['record_type','channel','label','threshold','step','statistic_before_reset','statistic_after_reset']")
text=replace_once(text,"['variant','variant_label','g_star_case','g_star_label','g_star','k','start_step','end_step','section_4_caveat']",
"['g_star_case','g_star_label','g_star','k','start_step','end_step','section_4_caveat']")
text=replace_once(text,"    for name,wanted in r['detector_logs'].items():",
"""    if sha(lf((OUT/r['allocation_log']).read_bytes()))!=r['allocation_log_sha256_lf']:
        raise RuntimeError('Completed allocation log hash mismatch: '+job)
    for name,wanted in r['detector_logs'].items():""")
text=text.replace("results['derivation_conformance']=read(P+'derivation_gate.json')","results['allocation_definition']=read(P+'allocation_gate.json')")
text=text.replace("results['derivation_conformance']['passed']","results['allocation_definition']['passed']")
text=text.replace("'derivation_conformance':result['derivation_conformance']['passed']","'allocation_definition':result['allocation_definition']['passed']")
text=replace_once(text,"    derivation_gate()\n","")
text=replace_once(text,"        recorder_conformance()\n        result=compare_gates()",
"        recorder_conformance()\n        allocation_definition_gate()\n        result=compare_gates()")
text=replace_once(text,"                attempt=state['attempts'].get(job,0)+1;state['attempts'][job]=attempt",
"""                prior_attempt=state['attempts'].get(job,0)
                if prior_attempt:
                    for suffix in ('.csv.partial','.csv'):
                        partial=OUT/(P+job+'_steps_attempt'+str(prior_attempt)+suffix)
                        if partial.exists():
                            retained=OUT/(P+job+'_steps_attempt'+str(prior_attempt)+'_interrupted.csv.partial')
                            if retained.exists():raise RuntimeError('Retained partial path already exists')
                            replace_with_retry(partial,retained)
                            state.setdefault('retained_partial_logs',[]).append({'job':job,'path':retained.name})
                            break
                attempt=prior_attempt+1;state['attempts'][job]=attempt""")
text=replace_once(text,"if __name__=='__main__':main()",
"""import detector_run_r3_eval_channels as registered

if __name__=='__main__':
    try:main()
    except Exception as error:
        mark_halt('executor',error)
        raise
""")
compile(text,str(OUT/(P+'executor.py')),'exec')
with (OUT/(P+'executor.py')).open('x',encoding='utf-8',newline='\n') as f:f.write(text)
unit_raw=get('detector_run_r2_eval_unit_gate.py')
unit=unit_raw.decode('utf-8').replace('detector_run_r2_eval_','detector_run_r3_eval_')
compile(unit,str(OUT/(P+'unit_gate.py')),'exec')
with (OUT/(P+'unit_gate.py')).open('x',encoding='utf-8',newline='\n') as f:f.write(unit)
provenance=[]
for name,data in [('detector_run_r2_eval_executor.py',raw),('detector_run_r2_eval_unit_gate.py',unit_raw)]:
    provenance.append({'path':'simulation/diagnostics/'+name,
        'read_commit':subprocess.run(['git','rev-parse','HEAD'],capture_output=True,check=True).stdout.decode().strip(),
        'sha256_lf':hashlib.sha256(data.replace(b'\r\n',b'\n')).hexdigest(),
        'blob_sha1':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()})
with (OUT/(P+'authoring.json')).open('x',encoding='utf-8',newline='\n') as f:
    json.dump({'source_copies':provenance,'executor_parse_passed':True,'unit_parse_passed':True,
               'recorder_function_copied_without_change':True,
               'retry_layer_copied_without_change':True},f,indent=2);f.write('\n')
print('Executor and synthetic gate authored and parsed; no model stepped')
