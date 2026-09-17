"""Author attempt 2 from committed attempt 1 scripts under the amended specification."""
import sys
sys.dont_write_bytecode=True
import os
from pathlib import Path
ROOT=Path.cwd().resolve()
OUT=ROOT/'simulation'/'diagnostics'
P='detector_run_r3_eval_a2_'
OLD='detector_run_r3_eval_'
NULL=Path(os.devnull).resolve()
def allowed(path):
    p=Path(path).resolve()
    return p==NULL or (p.parent==OUT and p.name.startswith(P))
def audit(event,args):
    if event=='open':
        path,mode,flags=args
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_APPEND|os.O_TRUNC))
        if writing and not isinstance(path,int) and not allowed(path):
            raise RuntimeError('WRITE SCOPE HALT: '+str(path))
    elif event=='os.rename':
        if not allowed(args[0]) or not allowed(args[1]):raise RuntimeError('WRITE SCOPE HALT: rename')
    elif event in ('os.remove','os.rmdir','os.mkdir','os.link','os.symlink'):
        raise RuntimeError('WRITE SCOPE HALT: '+event)
sys.addaudithook(audit)
os.environ['PYTHONDONTWRITEBYTECODE']='1'
os.environ['GIT_OPTIONAL_LOCKS']='0'
import json,hashlib,subprocess
def lf(b):return b.replace(b'\r\n',b'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args):
    r=subprocess.run(['git',*args],capture_output=True,check=True)
    return r.stdout
def save(name,value):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,indent=2);f.write('\n')
def swap(s,old,new):
    if s.count(old)!=1:raise RuntimeError('Authoring replacement is not unique: '+old[:70])
    return s.replace(old,new)
pre=json.loads((OUT/(P+'preflight.json')).read_bytes())
plan=json.loads(git('cat-file','blob',pre['head']+':simulation/diagnostics/'+OLD+'plan.json'))
plan['head']=pre['head']
plan['pins']=pre['readings']
plan['t0_checks']=pre['checks']
plan['t0_passed']=True
plan['attempt']=2
plan['prior_attempt']={'halt':'A-definition last-bit disagreement','evaluation_runs_launched':0,'commit':'9d4aa64'}
plan['amendment']='Amendment 1 pins numpy.sum(numpy.abs(x - m)) on six float64 shares in registered order.'
plan['write_guard']['allowed_prefix']='simulation/diagnostics/'+P
plan['fresh_namespace_verified']=pre['fresh_namespace']
plan['prior_artifacts_tracked_unmodified']=pre['prior_artifacts']
sources=[];scripts={}
for name in ('executor','channels','unit_gate','analysis','report'):
    path='simulation/diagnostics/'+OLD+name+'.py'
    raw=git('cat-file','blob',pre['head']+':'+path)
    s=raw.decode('utf-8').replace(OLD,P)
    sources.append({'path':path,'commit':pre['head'],'sha256_lf':sha(lf(raw)),
                    'blob_sha1':git('rev-parse',pre['head']+':'+path).decode().strip()})
    if name=='channels':
        s=swap(s,'import json\n','import json\nimport numpy as np\n')
        s=swap(s,'    return sum(abs(float(row[a])-medians[a]) for a in AXES)',
        "    x=np.asarray([row[a] for a in AXES],dtype=np.float64)\n    m=np.asarray([medians[a] for a in AXES],dtype=np.float64)\n    return float(np.sum(np.abs(x-m)))")
        s=swap(s,'        value=0.0\n        for axis in AXES:value+=abs(row[axis]-medians[axis])',
        "        x=np.asarray([row[axis] for axis in AXES],dtype=np.float64)\n        m=np.asarray([medians[axis] for axis in AXES],dtype=np.float64)\n        value=float(np.sum(np.abs(x-m)))")
    if name=='report':
        s=swap(s,'"""Render round 2 registered results and provenance without interpretation."""',
                 '"""Render round 3 attempt 2 registered results and provenance without interpretation."""')
        s=swap(s,"    if halted:\n        failure=",
        "    doc+=['Attempt 1 halted at the A-definition gate with zero evaluation runs launched. Amendment 1 pins A to numpy.sum(numpy.abs(x - m)) over the six-element float64 vectors in the registered order. No constant changed or was re-derived.','']\n    if halted:\n        failure=")
    compile(s,str(OUT/(P+name+'.py')),'exec')
    if '\u2014' in s:raise RuntimeError('Forbidden em dash')
    scripts[name]=s
save(P+'plan.json',plan)
for name,s in scripts.items():
    with (OUT/(P+name+'.py')).open('x',encoding='utf-8',newline='\n') as f:f.write(s)
save(P+'authoring.json',{'sources':sources,'all_scripts_parsed_before_execution':True,
                        'amendment':plan['amendment'],'bytecode_writes':False,
                        'guard_prefix':P,'os_devnull_exempt':True})
paths=[OUT/(P+n+'.py') for n in scripts]+[Path(__file__).resolve()]
save(P+'code_identity.json',{'files':{p.relative_to(ROOT).as_posix():sha(lf(p.read_bytes())) for p in paths},
                             'all_scripts_parse':True,'bytecode_written':False})
save(P+'control.json',{'mode':'normal','interrupt':False})
print(json.dumps({'authored':list(scripts),'parsed':True,'plan_head':plan['head']}))
