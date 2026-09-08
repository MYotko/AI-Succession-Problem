"""Read-only model execution and bounded output for the veto floor probe."""
import sys
sys.dont_write_bytecode = True
import os
THREAD_ENV = ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','BLIS_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']
for key in THREAD_ENV:
    os.environ[key] = '1'
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parent.parent

def allowed(path):
    p = Path(path).resolve()
    return p.parent == OUT and p.name.startswith('veto_floor_')


def audit(event, args):
    if event == 'open':
        path, mode, flags = args
        writing = (isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_APPEND|os.O_CREAT|os.O_TRUNC))
        if writing and not isinstance(path,int) and not allowed(path):
            raise RuntimeError('WRITE SCOPE HALT: ' + str(path))
    elif event == 'os.rename':
        if not allowed(args[0]) or not allowed(args[1]):
            raise RuntimeError('WRITE SCOPE HALT: rename outside prefix')
    elif event in ('os.remove','os.rmdir','os.mkdir','os.link','os.symlink'):
        raise RuntimeError('WRITE SCOPE HALT: ' + event)

sys.addaudithook(audit)
sys.path.insert(0,str(ROOT/'simulation'))
import argparse
import ctypes
import hashlib
import json
import math
import subprocess
import time
import traceback
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(name, obj):
    p = OUT/name
    if not allowed(p):
        raise RuntimeError('WRITE SCOPE HALT: ' + name)
    temp = OUT/(name+'.tmp')
    with temp.open('w',encoding='utf-8',newline='\n') as handle:
        json.dump(obj,handle,indent=2,sort_keys=True,allow_nan=False)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp,p)


def module_sources():
    result = {}
    for module in list(sys.modules.values()):
        value = getattr(module,'__file__',None)
        if not value:
            continue
        path = Path(value).resolve()
        if path.suffix == '.py' and path.is_relative_to(ROOT/'simulation'):
            result[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def thread_runtime(np):
    records = []
    for dll in (Path(np.__file__).resolve().parent.parent/'numpy.libs').iterdir():
        if dll.suffix.lower() == '.dll' and 'openblas' in dll.name.lower():
            lib = ctypes.CDLL(str(dll))
            for name in ['scipy_openblas_get_num_threads64_','openblas_get_num_threads64_','scipy_openblas_get_num_threads','openblas_get_num_threads']:
                try:
                    query = getattr(lib,name)
                except AttributeError:
                    continue
                query.argtypes = []
                query.restype = ctypes.c_int
                records.append({'library':str(dll),'query':name,'effective_threads':query()})
    if not records or any(r['effective_threads'] != 1 for r in records):
        raise RuntimeError('Numerical-library thread limit was not verified as one')
    return records


def run(job):
    plan = json.loads((OUT/'veto_floor_plan.json').read_text(encoding='utf-8'))
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    if head != plan['head']:
        raise RuntimeError('HEAD changed after the precondition gate')
    worker_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if worker_hash != plan['worker_sha256']:
        raise RuntimeError('Worker changed after plan creation')
    task = json.loads(json.dumps(plan['base_task']))
    if job == 'reproduction':
        arm = 'REPRODUCTION'
        filename = 'veto_floor_reproduction.json'
    else:
        gate = json.loads((OUT/'veto_floor_reproduction.json').read_text(encoding='utf-8'))
        if not gate.get('reproduction_passed'):
            raise RuntimeError('Reproduction gate has not passed')
        arm, seed_text = job.rsplit('_',1)
        seed = int(seed_text)
        if arm not in ['ZERO_STRENGTH','ZERO_DEPENDENCY','AS_PUBLISHED'] or not 1835086199 <= seed <= 1835086238:
            raise RuntimeError('Invalid floor job')
        task['seed'] = seed
        task['replicate'] = seed - 1835086199
        if arm == 'ZERO_STRENGTH':
            task['parameters']['capture_strength'] = 0.0
        elif arm == 'ZERO_DEPENDENCY':
            task['parameters']['dependency_rate'] = 0.0
        filename = 'veto_floor_result_'+job+'.json'
    if (OUT/filename).exists():
        raise RuntimeError('Completed job exists; worker refuses to rerun it')
    import numpy as np
    import run_attack_vector_revalidation_v2 as runner
    threads = thread_runtime(np)
    started = time.perf_counter()
    model, settings = runner._make_model(task)
    if settings != plan['runtime_settings']:
        raise RuntimeError('Factory runtime settings differ from pinned row')
    cfg = dict(model.config)
    if cfg['n_validators'] != 5 or cfg['base_validator_accuracy'] != 0.8 or cfg['reproduction_rate'] != 0.09:
        raise RuntimeError('Protected configuration mismatch')
    if job != 'reproduction':
        expected = dict(gate['constructed_config'],random_seed=task['seed'])
        if arm == 'ZERO_STRENGTH':
            expected['capture_strength'] = 0.0
        elif arm == 'ZERO_DEPENDENCY':
            expected['dependency_rate'] = 0.0
        if cfg != expected:
            raise RuntimeError('Arm changed a setting outside its permitted variation')
    for _ in range(settings['steps']):
        if not model.step():
            break
    dc = model.datacollector
    met = int(model.yield_condition_met_count)
    blocked = int(model.yield_condition_blocked_count)
    if not 0 <= blocked <= met:
        raise RuntimeError('Blocked/met count inconsistency')
    population = len(model.schedule)
    peak = max(dc['population']) if dc['population'] else population
    collapse_threshold = max(model.min_viable_population,int(0.65*peak))
    row = {'arm':arm,'seed':task['seed'],'steps_completed':len(dc['population']),
           'yield_condition_met_count':met,'yield_condition_blocked_count':blocked,
           'blocked_over_met':blocked/met if met else None,
           'extinct':population == 0,'collapsed':population < collapse_threshold,
           'final_population':population,
           'final_validator_dependency_mean':float(dc['avg_validator_dependency'][-1]),
           'final_validator_dependency_max':float(dc['max_validator_dependency'][-1])}
    if any(not math.isfinite(x) for x in row.values() if isinstance(x,float)):
        raise RuntimeError('Nonfinite run result')
    touched = module_sources()
    for path,digest in touched.items():
        expected = plan['production_source_sha256'].get(path)
        if path == Path(__file__).relative_to(ROOT).as_posix():
            expected = plan['worker_sha256']
        if expected != digest:
            raise RuntimeError('Unverified or changed simulation source: '+path)
    result = {'complete':True,'job':job,'row':row,'task':task,'constructed_config':cfg,
              'runtime_settings':settings,'machine':os.environ['COMPUTERNAME'],'head':head,
              'python':sys.version,'numpy':np.__version__,'worker_pid':os.getpid(),
              'thread_environment':{k:os.environ[k] for k in THREAD_ENV},'thread_runtime':threads,
              'simulation_source_sha256':touched,'worker_sha256':worker_hash,
              'elapsed_seconds':time.perf_counter()-started,'finished_utc':now()}
    if job == 'reproduction':
        result['expected'] = plan['expected_reproduction']
        result['reproduction_comparison'] = {k:{'pinned':v,'observed':row[k],'match':row[k] == v} for k,v in plan['expected_reproduction'].items()}
        result['reproduction_passed'] = all(v['match'] for v in result['reproduction_comparison'].values())
    write_json(filename,result)
    print(json.dumps({'job':job,'row':row,'reproduction_passed':result.get('reproduction_passed'),'elapsed_seconds':result['elapsed_seconds']}),flush=True)
    if job == 'reproduction' and not result['reproduction_passed']:
        raise RuntimeError('Reproduction mismatch; no floor measurement is authorized')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job',required=True)
    args = parser.parse_args()
    try:
        run(args.job)
    except Exception as error:
        write_json('veto_floor_failure_'+args.job+'.json',{'job':args.job,'halt':str(error),'utc':now(),'traceback':traceback.format_exc()})
        print('HALT: '+str(error),flush=True)
        raise SystemExit(2)


if __name__ == '__main__':
    main()
