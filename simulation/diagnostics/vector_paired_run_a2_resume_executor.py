"""Resume the authorized interrupted batch without altering its scientific executor."""
import sys
sys.dont_write_bytecode=True
import vector_paired_run_a2_executor as e
import json,subprocess,time,traceback
from pathlib import Path

def main():
    e.check_stop();e.check_identity();e.pins()
    pre=e.read(e.P+'resume_preflight.json')
    assert pre['status']=='PASSED' and pre['gate_evidence_verified']
    gates=e.read(e.P+'gates.json')
    assert gates['passed'] and gates['identity']==e.identity()
    assert e.sha(e.lf((e.OUT/(e.P+'gates.json')).read_bytes()))==pre['gate_evidence_sha256_lf']
    expected={p['path']:p['expected_sha256_lf'] for p in pre['pins']}
    for key in ('source_pins_start','source_pins_end'):
        assert {p['path']:p['actual_sha256_lf'] for p in gates[key]}==expected
    for item in pre['preserved']:
        c=e.completed(item['arm'],item['seed'])
        assert c is not None
        assert e.sha(e.lf((e.OUT/(e.P+item['job']+'_complete.json')).read_bytes()))==item['completion_sha256_lf']
    pending=[];restarted=[];retained=[]
    for item in pre['interrupted']:
        assert e.completed(item['arm'],item['seed']) is None
        attempt=1
        for name in item['files']:
            path=(e.OUT/name).resolve()
            assert path.parent==e.OUT and path.name.startswith(e.P+item['job']+'_')
            if name.endswith('.json'):
                old=e.read(name)
                assert old['arm']==item['arm'] and old['seed']==item['seed']
                attempt=max(attempt,int(old.get('attempt',1)))
            dest=(e.OUT/(name+'.retained.partial')).resolve()
            assert dest.parent==e.OUT and dest.name.startswith(e.P) and not dest.exists()
            before=e.sha(e.lf(path.read_bytes()))
            e.replace_with_retry(path,dest)
            retained.append({'original':name,'retained':dest.name,'sha256_lf':before})
        entry={'job':item['job'],'arm':item['arm'],'seed':item['seed'],
               'attempt':attempt+1,'reason':'provider usage limit','restart_step':0}
        restarted.append(entry);pending.append(entry)
    for item in pre['never_launched']:
        assert e.completed(item['arm'],item['seed']) is None
        pending.append({'job':item['job'],'arm':item['arm'],'seed':item['seed'],'attempt':1})
    accounting={'interruption_reason':'provider usage limit','counts':pre['counts'],
                'preserved':pre['preserved'],'restarted':restarted,'never_launched':pre['never_launched'],
                'partial_artifacts_retained':retained,'gates_rerun':False,
                'gate_evidence_sha256_lf':pre['gate_evidence_sha256_lf'],
                'gate_evidence_and_recorded_pins_verified':True}
    e.write(e.P+'resume_accounting.json',accounting)
    mode=e.read(e.P+'control.json')['mode']
    active={};finished=len(pre['preserved']);peak=0;events=[{'utc':e.now(),'mode':mode,'resumption':True}]
    while pending or active:
        e.check_stop()
        requested=e.read(e.P+'control.json')['mode']
        assert requested in ('normal','work')
        if requested!=mode:
            mode=requested;events.append({'utc':e.now(),'mode':mode,'active_workers':len(active)})
        for job,(proc,item) in list(active.items()):
            rc=proc.poll()
            if rc is None:continue
            if rc!=0:raise RuntimeError('Worker exited nonzero: '+job+' exit '+str(rc))
            assert e.completed(item['arm'],item['seed']) is not None
            del active[job];finished+=1
        for _ in range(e.dispatch_slots(mode,len(active),len(pending))):
            item=pending.pop(0)
            cmd=[sys.executable,'-B',str(Path(e.__file__).resolve()),'worker',
                 '--arm',item['arm']['name'],'--seed',str(item['seed']),'--attempt',str(item['attempt'])]
            proc=subprocess.Popen(cmd,cwd=e.ROOT,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                 stderr=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            active[item['job']]=(proc,item)
        peak=max(peak,len(active))
        e.write(e.P+'resume_status.json',{'state':'RUNNING' if pending or active else 'COMPLETE',
                'utc':e.now(),'completed':finished,'running':len(active),'pending':len(pending),
                'running_jobs':list(active),'mode':mode,'peak_active_workers':peak,'mode_events':events})
        if pending or active:time.sleep(1)
    assert finished==240
    for item in pre['preserved']:
        assert e.completed(item['arm'],item['seed']) is not None
        assert e.sha(e.lf((e.OUT/(e.P+item['job']+'_complete.json')).read_bytes()))==item['completion_sha256_lf']
    e.write(e.P+'execution.json',{'status':'COMPLETE','runs':finished,'peak_active_workers':max(e.read(e.P+'status.json')['peak_active_workers'],peak),
            'resumption_peak_active_workers':peak,'mode_events':events,
            'preserved_jobs':[i['job'] for i in pre['preserved']],'resumed_jobs':restarted,
            'never_launched_jobs':pre['never_launched'],'resumption_counts':pre['counts'],
            'interruption_reason':'provider usage limit','completed_utc':e.now(),
            'source_pins_end':e.pins(),'identity':e.identity(),
            'gate_evidence_sha256_lf':pre['gate_evidence_sha256_lf'],'gates_rerun':False})
    result=subprocess.run([sys.executable,'-B',str(e.OUT/(e.P+'resume_analysis.py'))],cwd=e.ROOT,
                          capture_output=True,text=True)
    if result.returncode:
        raise RuntimeError('Analysis failed: '+result.stdout+' '+result.stderr)
    print(result.stdout.strip(),flush=True)

if __name__=='__main__':
    try:main()
    except BaseException as error:
        e.mark_halt('resumption',error)
        print(traceback.format_exc(),file=sys.stderr,flush=True)
        raise
