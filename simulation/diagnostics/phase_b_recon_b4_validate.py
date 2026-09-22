
"""Non-registered smoke validation controller. Never invokes the measured grid."""
import sys
sys.dont_write_bytecode=True
import ast, json, os, runpy, signal, subprocess, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'simulation'/'diagnostics'
EXEC=D/'phase_b_recon_executor.py'
ast.parse(EXEC.read_text(encoding='utf-8'))
ns=runpy.run_path(str(EXEC),run_name='smoke_controller')
ns['install_guard']('phase_b_recon_')
# This controller additionally limits all its output names to smoke and attempt 4.
v20='C:/Users/matty/Dev/phase-b-recon-v20'
prefix='phase_b_recon_smoke_'
args=[sys.executable,'-B',str(EXEC),'--test-mode','--substrate','both','--v20-worktree',v20]
def start(extra,name):
    f=(D/('phase_b_recon_b4_'+name+'.txt')).open('wb')
    p=subprocess.Popen(args+extra,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,
                       creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    return p,f
p,f=start(['--workers','2'],'interrupt_console')
interruption=None
while p.poll() is None:
    progress=D/'phase_b_recon_progress.json'
    if progress.exists():
        v=ns['read_json'](progress)
        if v.get('parent_pid')==p.pid and v['completed']>=1 and v['active']:
            target=v['active'][0]
            initial=D/(prefix+'job_'+target['key']+'_progress.json')
            if initial.exists() and ns['read_json'](initial)['steps_completed']>0:
                completed={}
                for path in D.glob(prefix+'job_*_completion.json'):
                    completed[path.name]=ns['digest'](path.read_bytes())
                os.kill(target['pid'],signal.SIGTERM)
                interruption={'utc':ns['utc'](),'killed_worker':target,'progress_before':v,
                              'completed_file_hashes_before':completed}
                break
    time.sleep(.5)
if interruption is None:
    p.wait(); f.close()
    ns['atomic_json'](D/'phase_b_recon_b4_validation_state.json',
                     {'status':'initial_run_stopped_before_interrupt','exit_code':p.returncode})
    print('VALIDATION STOPPED BEFORE INTERRUPTION; inspect interrupt_console',flush=True)
    sys.exit(2)
p.wait();f.close()
interruption['initial_exit_code']=p.returncode
ns['atomic_json'](D/'phase_b_recon_b4_interruption.json',interruption)
assert p.returncode==2
p,f=start(['--workers','8','--resume'],'resume_console')
rc=p.wait();f.close()
ns['atomic_json'](D/'phase_b_recon_b4_validation_state.json',
                 {'status':'smoke_complete' if rc==0 else 'resume_stopped','exit_code':rc})
print('SMOKE CONTROLLER: resume exit '+str(rc),flush=True)
sys.exit(rc)
