
"""Non-registered smoke controller. All model invocations explicitly use --test-mode."""
import sys
sys.dont_write_bytecode=True
import ast,ctypes,json,os,runpy,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'simulation'/'diagnostics'
EXEC=D/'phase_b_recon_executor.py'
ast.parse(EXEC.read_text(encoding='utf-8'))
ns=runpy.run_path(str(EXEC),run_name='smoke_controller')
ns['install_guard']('phase_b_recon_')
prefix='phase_b_recon_smoke_'
args=[sys.executable,'-B',str(EXEC),'--test-mode','--substrate','both',
      '--v20-worktree','C:/Users/matty/Dev/phase-b-recon-v20']
def start(extra,name):
 f=(D/('phase_b_recon_b5_'+name+'.txt')).open('wb')
 p=subprocess.Popen(args+extra,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 return p,f
def read_progress(pid):
 path=D/'phase_b_recon_progress.json'
 if not path.exists(): return None
 v=ns['read_json'](path)
 return v if v.get('parent_pid')==pid else None
p,f=start(['--workers','2'],'interrupt_console')
interruption=None
mode_events=[]
work_requested=False
while p.poll() is None:
 v=read_progress(p.pid)
 if v:
  if v['active'] and not work_requested:
   ns['atomic_json'](D/(prefix+'runtime_control.json'),{'mode':'work'})
   mode_events.append({'event':'work_requested','utc':ns['utc']()})
   work_requested=True
  if v['completed']>=1 and v['active'] and v['mode']=='work':
   target=v['active'][0]
   heartbeat=D/(prefix+'job_'+target['key']+'_progress.json')
   if heartbeat.exists() and 0<ns['read_json'](heartbeat)['steps_completed']<290:
    completed={}
    for path in D.glob(prefix+'job_*_completion.json'):
     completed[path.name]=ns['digest'](path.read_bytes())
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
    kernel.OpenProcess.restype=ctypes.c_void_p
    kernel.TerminateProcess.argtypes=[ctypes.c_void_p,ctypes.c_uint]
    kernel.TerminateProcess.restype=ctypes.c_int
    kernel.CloseHandle.argtypes=[ctypes.c_void_p]
    handle=kernel.OpenProcess(1,False,target['pid'])
    if not handle:
     time.sleep(.5)
     continue
    terminated=kernel.TerminateProcess(handle,99)
    kernel.CloseHandle(handle)
    if not terminated:
     time.sleep(.5)
     continue
    interruption={'utc':ns['utc'](),'killed_worker':target,'progress_before':v,
                  'partial_heartbeat':ns['read_json'](heartbeat),
                  'completed_file_hashes_before':completed}
    break
 time.sleep(.5)
if interruption is None:
 p.wait();f.close()
 ns['atomic_json'](D/'phase_b_recon_b5_validation_state.json',
                  {'status':'initial_run_stopped_before_interrupt','exit_code':p.returncode})
 print('VALIDATION STOPPED BEFORE INTERRUPTION; inspect interrupt_console',flush=True)
 sys.exit(2)
p.wait();f.close()
interruption['initial_exit_code']=p.returncode
ns['atomic_json'](D/'phase_b_recon_b5_interruption.json',interruption)
assert p.returncode==2
p,f=start(['--workers','8','--resume'],'resume_console')
normal_requested=False
normal_seen=False
while p.poll() is None:
 v=read_progress(p.pid)
 if v:
  if not normal_requested and v['mode']=='work' and v['active']:
   mode_events.append({'event':'work_preserved_on_resume','utc':ns['utc'](),'progress':v})
   ns['atomic_json'](D/(prefix+'runtime_control.json'),{'mode':'normal'})
   mode_events.append({'event':'normal_requested','utc':ns['utc']()})
   normal_requested=True
  if normal_requested and not normal_seen and v['mode']=='normal':
   mode_events.append({'event':'normal_applied','utc':ns['utc'](),'progress':v})
   normal_seen=True
 time.sleep(.5)
rc=p.wait();f.close()
ns['atomic_json'](D/'phase_b_recon_b5_modes.json',mode_events)
ns['atomic_json'](D/'phase_b_recon_b5_validation_state.json',
                 {'status':'smoke_complete' if rc==0 else 'resume_stopped','exit_code':rc})
print('SMOKE CONTROLLER: resume exit '+str(rc),flush=True)
sys.exit(rc)
