
"""Continue the planned smoke interruption/resume validation after Windows PID termination denial."""
import sys
sys.dont_write_bytecode=True
import ast,json,runpy,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'simulation'/'diagnostics';EXEC=D/'phase_b_recon_executor.py'
ast.parse(EXEC.read_text())
ns=runpy.run_path(str(EXEC),run_name='resume_validation')
ns['install_guard']('phase_b_recon_')
deadline=time.monotonic()+60
while True:
 v=ns['read_json'](D/'phase_b_recon_progress.json')
 if v['status']=='stopped' and not v['active']:break
 if time.monotonic()>deadline:raise RuntimeError('Parent did not stop after worker termination')
 time.sleep(.5)
interruption=ns['read_json'](D/'phase_b_recon_b5_interruption.json')
interruption['initial_exit_code']=2
interruption['parent_stopped_progress']=v
ns['atomic_json'](D/'phase_b_recon_b5_interruption.json',interruption)
f=(D/'phase_b_recon_b5_resume_console.txt').open('wb')
args=[sys.executable,'-B',str(EXEC),'--test-mode','--substrate','both','--v20-worktree',
      'C:/Users/matty/Dev/phase-b-recon-v20','--workers','8','--resume']
p=subprocess.Popen(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,
                   creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
events=[];normal_requested=False;normal_seen=False
while p.poll() is None:
 v=ns['read_json'](D/'phase_b_recon_progress.json')
 if v.get('parent_pid')==p.pid:
  if not normal_requested and v['mode']=='work' and v['active']:
   events.append({'event':'work_preserved_on_resume','utc':ns['utc'](),'progress':v})
   ns['atomic_json'](D/'phase_b_recon_smoke_runtime_control.json',{'mode':'normal'})
   events.append({'event':'normal_requested','utc':ns['utc']()});normal_requested=True
  if normal_requested and not normal_seen and v['mode']=='normal':
   events.append({'event':'normal_applied','utc':ns['utc'](),'progress':v});normal_seen=True
 time.sleep(.5)
rc=p.wait();f.close()
ns['atomic_json'](D/'phase_b_recon_b5_modes.json',events)
ns['atomic_json'](D/'phase_b_recon_b5_validation_state.json',
                 {'status':'smoke_complete' if rc==0 else 'resume_stopped','exit_code':rc})
print('SMOKE CONTROLLER: resume exit '+str(rc),flush=True)
sys.exit(rc)
