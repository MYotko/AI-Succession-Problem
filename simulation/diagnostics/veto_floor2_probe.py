"""Bounded veto floor Run 2 execution. No scientific functions are modified."""
import sys
sys.dont_write_bytecode = True
import os
THREAD_ENV = ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'BLIS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS']
for key in THREAD_ENV:
    os.environ[key] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parent.parent
SELF = Path(__file__).resolve()
NULL = Path(os.devnull).resolve()
VIOLATIONS = []

def allowed(path):
    p = Path(path).resolve()
    return p.parent == OUT and p.name.startswith('veto_floor2_')

def writable(path):
    return Path(path).resolve() == NULL or allowed(path)

def audit(event, args):
    problem = None
    if event == 'open':
        path, mode, flags = args
        writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC))
        if writing and not isinstance(path, int) and not writable(path):
            problem = 'writable open: ' + str(path)
    elif event == 'os.rename':
        if not allowed(args[0]) or not allowed(args[1]):
            problem = 'rename outside prefix'
    elif event in ('os.remove', 'os.rmdir', 'os.mkdir', 'os.link', 'os.symlink'):
        problem = event
    if problem:
        VIOLATIONS.append(problem)
        raise RuntimeError('WRITE SCOPE HALT: ' + problem)

sys.addaudithook(audit)
sys.path.insert(0, str(ROOT / 'simulation'))
import argparse
import copy
import csv
import ctypes
import hashlib
import json
import math
import statistics
import subprocess
import time
import traceback
from datetime import datetime, timezone

ARMS = ['ZERO_STRENGTH', 'ZERO_DEPENDENCY', 'AS_PUBLISHED']
SEEDS = list(range(700000000, 700000300))
FIELDS = ['arm', 'seed', 'steps_completed', 'yield_condition_met_count', 'yield_condition_blocked_count', 'extinct', 'collapsed', 'final_population', 'final_validator_dependency_mean', 'final_validator_dependency_max']

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))

def write(name, value):
    target = OUT / name
    if not allowed(target):
        raise RuntimeError('WRITE SCOPE HALT: output name')
    temp = OUT / (name + '.tmp')
    with temp.open('w', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, target)

def write_text(name, value):
    if not allowed(OUT / name):
        raise RuntimeError('WRITE SCOPE HALT: text output name')
    with (OUT / name).open('w', encoding='utf-8', newline='\n') as f:
        f.write(value)
        f.flush()
        os.fsync(f.fileno())

def assert_guard():
    if VIOLATIONS:
        raise RuntimeError('WRITE SCOPE HALT: ' + repr(VIOLATIONS))

def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=False)

def jobs():
    return [arm + '_' + str(seed) for seed in SEEDS for arm in ARMS]

def decode(job):
    arm, seed = job.rsplit('_', 1)
    seed = int(seed)
    if arm not in ARMS or seed not in SEEDS:
        raise RuntimeError('Invalid job: ' + job)
    return arm, seed

def task_config(plan, job):
    arm, seed = decode(job)
    task = copy.deepcopy(plan['base_task'])
    task['seed'] = seed
    task['replicate'] = seed - SEEDS[0]
    cfg = dict(plan['base_config'], random_seed=seed)
    if arm == 'ZERO_STRENGTH':
        task['parameters']['capture_strength'] = cfg['capture_strength'] = 0.0
    elif arm == 'ZERO_DEPENDENCY':
        task['parameters']['dependency_rate'] = cfg['dependency_rate'] = 0.0
    return task, cfg

def budget(mode):
    if mode not in ('normal', 'work'):
        raise RuntimeError('Invalid CPU mode')
    return 15 if mode == 'normal' else 12

def dispatch_slots(mode, active, pending):
    return min(pending, max(0, budget(mode) - active))

def fingerprint(plan):
    return hashlib.sha256(json.dumps({k:v for k,v in plan.items() if k != 'fingerprint'}, sort_keys=True).encode()).hexdigest()

def result_name(job):
    return 'veto_floor2_result_' + job + '.json'

def validate_result(plan, job, obj):
    task, cfg = task_config(plan, job)
    if not obj.get('complete') or obj.get('job') != job or obj.get('plan_fingerprint') != plan['fingerprint']:
        raise RuntimeError('Invalid completion identity: ' + job)
    if obj.get('task') != task or obj.get('constructed_config') != cfg or obj.get('runtime_settings') != plan['runtime_settings']:
        raise RuntimeError('Invalid completion configuration: ' + job)
    if obj.get('head') != plan['head'] or obj.get('script_sha256') != plan['script_sha256']:
        raise RuntimeError('Invalid completion code identity: ' + job)
    row = obj['row']
    if set(row) != set(FIELDS) or (row['arm'], row['seed']) != decode(job):
        raise RuntimeError('Invalid completion row: ' + job)
    if not 0 <= row['yield_condition_blocked_count'] <= row['yield_condition_met_count']:
        raise RuntimeError('Invalid event counts: ' + job)
    if not 0 < row['steps_completed'] <= plan['runtime_settings']['steps']:
        raise RuntimeError('Invalid completed steps: ' + job)
    for p, digest in obj['simulation_source_sha256'].items():
        expected = plan['script_sha256'] if p == SELF.relative_to(ROOT).as_posix() else plan['source_catalog'].get(p)
        if digest != expected:
            raise RuntimeError('Invalid completion source: ' + p)
    if not obj['thread_runtime'] or any(x['effective_threads'] != 1 for x in obj['thread_runtime']):
        raise RuntimeError('Invalid numerical thread count: ' + job)
    return row

def self_check(plan):
    order = jobs()
    assert len(order) == 900 and len(set(order)) == 900
    for arm in ARMS:
        assert [decode(j)[1] for j in order if decode(j)[0] == arm] == SEEDS
    assert dispatch_slots('normal', 0, 900) == 15
    assert dispatch_slots('work', 15, 900) == 0
    assert dispatch_slots('work', 13, 900) == 0
    assert dispatch_slots('work', 12, 900) == 0
    assert dispatch_slots('work', 11, 900) == 1
    assert dispatch_slots('normal', 12, 900) == 3
    assert dispatch_slots('normal', 0, 2) == 2
    assert writable(os.devnull)
    assert not writable(ROOT / 'forbidden.tmp')
    assert writable(OUT / 'veto_floor2_check.tmp')
    for job in order:
        task, cfg = task_config(plan, job)
        arm, seed = decode(job)
        assert task['seed'] == cfg['random_seed'] == seed
        changed = {k for k in cfg if cfg[k] != plan['base_config'][k]}
        expected = {'random_seed'} | ({'capture_strength'} if arm == 'ZERO_STRENGTH' else {'dependency_rate'} if arm == 'ZERO_DEPENDENCY' else set())
        assert changed == expected
    return {'passed':True, 'simulation_runs':0, 'checks':['job uniqueness and seed pairing', 'configuration variations', 'normal/work dispatch and draining', 'null-device exemption and scope predicate']}

def prepare():
    if (OUT / 'veto_floor2_plan.json').exists():
        raise RuntimeError('Plan already exists; use run to resume')
    prior_path = OUT / 'veto_floor_reproduction.json'
    prior = json.loads(prior_path.read_text(encoding='utf-8'))
    h = git('rev-parse', 'HEAD')
    anc = git('merge-base', '--is-ancestor', 'dc1b7c4', 'HEAD')
    advisor = git('ls-files', '--error-unmatch', '--', 'LINEAGE_IMPERATIVE_ADVISOR.md')
    lines = (ROOT / 'simulation/run_attack_vector_revalidation_v2.py').read_text(encoding='utf-8').splitlines()
    gates = [
        {'number':1, 'passed':h.returncode == 0 and anc.returncode == 0, 'head':h.stdout.strip(), 'merge_base_exit':anc.returncode},
        {'number':2, 'passed':(ROOT / 'LINEAGE_IMPERATIVE_ADVISOR.md').is_file() and advisor.returncode != 0, 'advisor_present':(ROOT / 'LINEAGE_IMPERATIVE_ADVISOR.md').is_file(), 'git_ls_files_exit':advisor.returncode},
        {'number':3, 'passed':lines[314].strip() == "'n_validators': 5," and lines[315].strip() == "'base_validator_accuracy': 0.8,", 'lines':{'315':lines[314], '316':lines[315]}}
    ]
    if not all(g['passed'] for g in gates):
        write('veto_floor2_precondition_failure.json', {'gates':gates, 'utc':now()})
        raise RuntimeError('Precondition gate failed')
    catalog = {p:sha(ROOT / p) for p in prior['simulation_source_sha256'] if not p.startswith('simulation/diagnostics/')}
    for p,digest in catalog.items():
        if digest != prior['simulation_source_sha256'][p]:
            raise RuntimeError('Simulation source differs from saved reproduction: ' + p)
    plan = {'created_utc':now(), 'head':h.stdout.strip(), 'machine':os.environ['COMPUTERNAME'], 'gates':gates,
            'prior_reproduction_path':prior_path.relative_to(ROOT).as_posix(), 'prior_reproduction_sha256':sha(prior_path),
            'prior_reproduction_pass_carried_forward':True, 'reproduction_repeated':False,
            'base_task':prior['task'], 'base_config':prior['constructed_config'], 'runtime_settings':prior['runtime_settings'],
            'source_catalog':catalog, 'script_sha256':sha(SELF), 'arms':ARMS, 'seeds':SEEDS,
            'cpu_budget':16, 'normal_worker_limit':15, 'work_worker_limit':12,
            'null_device_exemption':True, 'snapshot_generator_out_of_scope':True,
            'superseded_out_of_scope_instruction':'The prior task authorized a snapshot prefix edit. Run 2 supersedes that authorization. It is ignored here, and no snapshot operation is performed.'}
    plan['operational_checks'] = self_check(plan)
    plan['fingerprint'] = fingerprint(plan)
    write('veto_floor2_plan.json', plan)
    write('veto_floor2_control.json', {'mode':'normal', 'updated_utc':now()})
    write_text('veto_floor2_report.md', 'This is characterization of a known-defective measurement, not registered characterization data or framework evidence. No pre-registration boundary is crossed.\n\nStatus: preconditions passed; 900 floor runs pending. The prior reproduction pass is carried forward without rerunning it.\n')
    print(json.dumps({'preconditions':'PASS', 'head':plan['head'], 'operational_checks':plan['operational_checks'], 'worker_limit':15}), flush=True)

def module_sources():
    result = {}
    for module in list(sys.modules.values()):
        value = getattr(module, '__file__', None)
        if value:
            path = Path(value).resolve()
            if path.suffix == '.py' and path.is_relative_to(ROOT / 'simulation'):
                result[path.relative_to(ROOT).as_posix()] = sha(path)
    return result

def thread_runtime(np):
    records = []
    for dll in (Path(np.__file__).resolve().parent.parent / 'numpy.libs').iterdir():
        if dll.suffix.lower() == '.dll' and 'openblas' in dll.name.lower():
            lib = ctypes.CDLL(str(dll))
            for name in ['scipy_openblas_get_num_threads64_', 'openblas_get_num_threads64_', 'scipy_openblas_get_num_threads', 'openblas_get_num_threads']:
                try:
                    query = getattr(lib, name)
                except AttributeError:
                    continue
                query.argtypes = []
                query.restype = ctypes.c_int
                records.append({'library':str(dll), 'query':name, 'effective_threads':query()})
    if not records or any(x['effective_threads'] != 1 for x in records):
        raise RuntimeError('Numerical-library thread limit not verified')
    return records

def load_plan():
    plan = read('veto_floor2_plan.json')
    if fingerprint(plan) != plan['fingerprint'] or sha(SELF) != plan['script_sha256']:
        raise RuntimeError('Plan or harness identity changed')
    if git('rev-parse', 'HEAD').stdout.strip() != plan['head']:
        raise RuntimeError('HEAD changed after preparation')
    for p,digest in plan['source_catalog'].items():
        if sha(ROOT / p) != digest:
            raise RuntimeError('Source changed: ' + p)
    return plan

def worker(job):
    plan = load_plan()
    if (OUT / result_name(job)).exists():
        raise RuntimeError('Worker refuses to repeat a completed job')
    task, expected = task_config(plan, job)
    import numpy as np
    import run_attack_vector_revalidation_v2 as runner
    threads = thread_runtime(np)
    started = time.perf_counter()
    model, settings = runner._make_model(task)
    cfg = dict(model.config)
    if cfg != expected or settings != plan['runtime_settings']:
        raise RuntimeError('Constructed configuration differs outside authorized arm variation')
    for _ in range(settings['steps']):
        alive = model.step()
        assert_guard()
        if not alive:
            break
    dc = model.datacollector
    population = len(model.schedule)
    peak = max(dc['population']) if dc['population'] else population
    collapse_threshold = max(model.min_viable_population, int(0.65 * peak))
    arm, seed = decode(job)
    row = {'arm':arm, 'seed':seed, 'steps_completed':len(dc['population']),
           'yield_condition_met_count':int(model.yield_condition_met_count), 'yield_condition_blocked_count':int(model.yield_condition_blocked_count),
           'extinct':population == 0, 'collapsed':population < collapse_threshold, 'final_population':population,
           'final_validator_dependency_mean':float(dc['avg_validator_dependency'][-1]),
           'final_validator_dependency_max':float(dc['max_validator_dependency'][-1])}
    if any(not math.isfinite(v) for v in row.values() if isinstance(v, float)):
        raise RuntimeError('Nonfinite run result')
    obj = {'complete':True, 'job':job, 'plan_fingerprint':plan['fingerprint'], 'row':row, 'task':task, 'constructed_config':cfg,
           'runtime_settings':settings, 'head':plan['head'], 'script_sha256':sha(SELF), 'machine':os.environ['COMPUTERNAME'],
           'python':sys.version, 'numpy':np.__version__, 'worker_pid':os.getpid(), 'thread_environment':{k:os.environ[k] for k in THREAD_ENV},
           'thread_runtime':threads, 'simulation_source_sha256':module_sources(), 'elapsed_seconds':time.perf_counter()-started, 'finished_utc':now()}
    validate_result(plan, job, obj)
    assert_guard()
    write(result_name(job), obj)

def save_csv(completed):
    temp = OUT / 'veto_floor2_runs.csv.tmp'
    with temp.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(completed[j]['row'] for j in jobs() if j in completed)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, OUT / 'veto_floor2_runs.csv')

def sufficiency(completed):
    values = {}
    for arm in ARMS:
        rows = [x['row'] for x in completed.values() if x['row']['arm'] == arm]
        met = sum(r['yield_condition_met_count'] for r in rows)
        zeros = sum(r['yield_condition_met_count'] == 0 for r in rows)
        values[arm] = {'runs':len(rows), 'yield_events':met, 'zero_event_runs':zeros}
        if zeros > 30:
            raise RuntimeError('HALT: more than 30 zero-yield runs in ' + arm)
        if len(rows) == 300 and met < 250:
            raise RuntimeError('HALT: fewer than 250 total yield events in ' + arm)
    return values

def run_batch():
    plan = load_plan()
    prior_progress = read('veto_floor2_progress.json') if (OUT / 'veto_floor2_progress.json').exists() else {}
    completed = {}
    for job in jobs():
        if (OUT / result_name(job)).exists():
            obj = read(result_name(job))
            validate_result(plan, job, obj)
            completed[job] = obj
    pending = [j for j in jobs() if j not in completed]
    active = {}
    mode = read('veto_floor2_control.json')['mode']
    budget(mode)
    history = prior_progress.get('mode_history', [])
    history.append({'utc':now(), 'mode':mode, 'event':'start_or_resume', 'validated_completed':len(completed)})
    peak_workers = prior_progress.get('peak_active_workers', 0)
    starts = prior_progress.get('batch_starts', []) + [{'utc':now(), 'completed_skipped':len(completed), 'incomplete_jobs_restart_from_seed':prior_progress.get('active_jobs', [])}]
    started = time.perf_counter()
    elapsed_prior = prior_progress.get('elapsed_seconds', 0.0)
    last_print = -100.0
    last_save = -100.0
    save_csv(completed)
    try:
        sufficiency(completed)
        while pending or active:
            assert_guard()
            new_mode = read('veto_floor2_control.json')['mode']
            budget(new_mode)
            if new_mode != mode:
                mode = new_mode
                history.append({'utc':now(), 'mode':mode, 'event':'mode_change_requested', 'active':len(active)})
            changed = False
            for job, proc in list(active.items()):
                code = proc.poll()
                if code is None:
                    continue
                del active[job]
                if code != 0:
                    detail = read('veto_floor2_failure_' + job + '.json') if (OUT / ('veto_floor2_failure_' + job + '.json')).exists() else {'halt':'worker exit ' + str(code)}
                    raise RuntimeError('Worker failed: ' + job + ': ' + str(detail))
                obj = read(result_name(job))
                validate_result(plan, job, obj)
                completed[job] = obj
                changed = True
            counts = sufficiency(completed)
            if changed:
                save_csv(completed)
            for _ in range(dispatch_slots(mode, len(active), len(pending))):
                job = pending.pop(0)
                active[job] = subprocess.Popen([sys.executable, '-B', str(SELF), '--job', job], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                peak_workers = max(peak_workers, len(active))
            elapsed = time.perf_counter() - started
            progress = {'status':'running', 'updated_utc':now(), 'completed':len(completed), 'running':len(active), 'pending':len(pending),
                        'active_jobs':list(active), 'mode':mode, 'worker_limit':budget(mode), 'peak_active_workers':peak_workers,
                        'mode_reduction_effective':len(active) <= budget(mode), 'mode_history':history, 'batch_starts':starts,
                        'elapsed_seconds':elapsed_prior+elapsed, 'by_arm':counts}
            if changed or elapsed-last_save >= 10:
                write('veto_floor2_progress.json', progress)
                last_save = elapsed
            if elapsed-last_print >= 30 or not active and not pending:
                print(json.dumps({k:progress[k] for k in ['status','completed','running','pending','mode','elapsed_seconds','by_arm']}), flush=True)
                last_print = elapsed
            if pending or active:
                time.sleep(1)
        progress.update(status='complete', active_jobs=[], completed=900, running=0, pending=0, updated_utc=now())
        write('veto_floor2_progress.json', progress)
        finalize()
    except BaseException as error:
        for proc in active.values():
            if proc.poll() is None:
                proc.terminate()
        for proc in active.values():
            proc.wait()
        save_csv(completed)
        write('veto_floor2_halt.json', {'halt':str(error), 'utc':now(), 'completed':len(completed), 'interrupted_jobs':list(active), 'violations':VIOLATIONS, 'traceback':traceback.format_exc()})
        write_text('veto_floor2_report.md', 'This is characterization of a known-defective measurement, not registered characterization data or framework evidence.\n\nHALTED: ' + str(error) + '\n\nCompleted floor runs: ' + str(len(completed)) + '. No further run was dispatched after detection. See veto_floor2_halt.json and veto_floor2_plan.json.\n')
        raise

def wilson(blocks, events):
    z = statistics.NormalDist().inv_cdf(0.975)
    p = blocks / events
    denom = 1 + z*z/events
    center = (p + z*z/(2*events))/denom
    half = z*math.sqrt(p*(1-p)/events + z*z/(4*events*events))/denom
    return [max(0.0, center-half), min(1.0, center+half)]

def finalize():
    plan = load_plan()
    completed = {j:read(result_name(j)) for j in jobs()}
    for j,obj in completed.items():
        validate_result(plan, j, obj)
    sufficiency(completed)
    save_csv(completed)
    with (OUT / 'veto_floor2_runs.csv').open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 900:
        raise RuntimeError('Final CSV count differs from 900')
    stats = {}
    for arm in ARMS:
        selected = [r for r in rows if r['arm'] == arm]
        met = sum(int(r['yield_condition_met_count']) for r in selected)
        blocks = sum(int(r['yield_condition_blocked_count']) for r in selected)
        stats[arm] = {'runs':len(selected), 'total_yield_events':met, 'total_blocks':blocks, 'pooled_rate':blocks/met,
                      'wilson_95':wilson(blocks,met), 'mean_yield_events_per_run':met/len(selected),
                      'zero_yield_runs':sum(int(r['yield_condition_met_count'])==0 for r in selected)}
    keyed = {(r['arm'],int(r['seed'])):int(r['yield_condition_blocked_count']) for r in rows}
    differences = [keyed['AS_PUBLISHED',s]-keyed['ZERO_STRENGTH',s] for s in SEEDS]
    paired = {'pairs':len(differences), 'quantity':'AS_PUBLISHED minus ZERO_STRENGTH per-run block counts',
              'mean_difference':statistics.mean(differences), 'paired_standard_error':statistics.stdev(differences)/math.sqrt(len(differences))}
    progress = read('veto_floor2_progress.json')
    first = completed[jobs()[0]]
    sources = {}
    for obj in completed.values():
        for p,d in obj['simulation_source_sha256'].items():
            if p in sources and sources[p] != d:
                raise RuntimeError('Mixed source identity')
            sources[p] = d
    summary = {'arms':stats, 'paired_block_count_difference':paired, 'analytic_reference':0.057920, 'csv_rows_counted':len(rows)}
    write('veto_floor2_summary.json', summary)
    lines = ['# Veto ratification floor characterization, Run 2', '',
             'This characterizes a known-defective measurement. These outputs are not registered characterization data, are not framework evidence, and do not cross the pre-registration boundary.', '',
             'Status: complete. All 900 floor runs completed. The prior reproduction gate was carried forward without repeating it.', '',
             '## Measurements', '',
             'Counts below were counted from the recorded run CSV in Python with csv.DictReader, excluding the header. Rates and intervals were calculated from those counts. No per-run ratio was recorded or calculated.', '',
             '| Arm | Runs | Total yield events | Total blocks | Pooled block rate | Wilson 95% interval | Mean yield events/run | Zero-yield runs |',
             '| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |']
    for arm in ARMS:
        s=stats[arm]
        lines.append(f"| {arm} | {s['runs']} | {s['total_yield_events']} | {s['total_blocks']} | {s['pooled_rate']:.9f} | [{s['wilson_95'][0]:.9f}, {s['wilson_95'][1]:.9f}] | {s['mean_yield_events_per_run']:.9f} | {s['zero_yield_runs']} |")
    lines += ['', 'Pooled rate = total blocks / total yield events. Wilson intervals use the two-sided standard normal 0.975 quantile and yield events as the binomial denominator.', '',
              '| Arm | Measured pooled rate | Operator-supplied analytic reference |', '| --- | ---: | ---: |']
    for arm in ARMS[:2]:
        lines.append(f"| {arm} | {stats[arm]['pooled_rate']:.9f} | 0.057920 |")
    lines += ['', f"Seed-paired AS_PUBLISHED minus ZERO_STRENGTH per-run block-count difference: mean {paired['mean_difference']:.9f} blocks/run; paired standard error {paired['paired_standard_error']:.9f}, from {paired['pairs']} pairs. The standard error is the sample standard deviation of the 300 paired block-count differences divided by sqrt(300).", '',
              'All arm event totals were at least 250, and no arm had more than 30 zero-yield runs.', '', '## Preconditions and configuration', '']
    for gate in plan['gates']:
        lines.append('- Gate ' + str(gate['number']) + ': PASS. ' + json.dumps(gate,sort_keys=True))
    lines += ['', 'Prior reproduction record: `' + plan['prior_reproduction_path'] + '`, SHA256 `' + plan['prior_reproduction_sha256'] + '`. Its pass was accepted as instructed; it was not rerun.', '',
              'Each cell used the unmodified runner factory and its own model step loop. The complete constructed configuration was checked against the saved reproduction for every run, allowing the seed and only the arm-specific field to change. All constructed configurations are retained in the per-run completion JSON files.', '',
              'Base configuration from the saved reproduction (random_seed is replaced by each prescribed seed):', '', '```json',json.dumps(plan['base_config'],indent=2,sort_keys=True),'```','',
              'Task parameters remain defended with defense_mode both and rotation_interval 10. ZERO_STRENGTH changes capture_strength to 0.0; ZERO_DEPENDENCY changes dependency_rate to 0.0; AS_PUBLISHED changes neither. Each arm uses exactly seeds 700000000 through 700000299. Requested horizon: 300 steps; candidates: 300; rollout steps: 20. No seed function was used.', '',
              '## Execution provenance', '',
              f"Machine: `{first['machine']}`. HEAD: `{plan['head']}`. Python: `{first['python']}`. NumPy: `{first['numpy']}`.", '',
              f"Actual maximum concurrent simulation workers: {progress['peak_active_workers']}. Operator CPU budget: 16; normal cap: 15; work cap: 12. These are worker limits, not an operating-system core reservation. Elapsed batch time: {progress['elapsed_seconds']:.3f} seconds. Mode history and any resume events are retained in veto_floor2_progress.json.", '',
              'All workers set the six numerical-library thread environment variables to one before importing NumPy. Each run verified one effective OpenBLAS thread through the runtime getter recorded in its completion JSON. Completed jobs were atomically saved after validation. Resumption validates exact job, seed, configuration, source identity, and thread limits before skipping a completed result.', '',
              'SHA256 for every simulation Python module loaded by these runs:', '', '| Module | SHA256 |', '| --- | --- |']
    lines += [f'| `{p}` | `{d}` |' for p,d in sorted(sources.items())]
    lines += ['', '## Write scope and artifacts', '',
              'The write guard explicitly exempts os.devnull in any mode. All other writable opens are restricted to simulation/diagnostics/veto_floor2_ filenames. Bytecode writes were disabled. No other writable-open violation was recorded. No Git write operation was performed.', '',
              plan['superseded_out_of_scope_instruction'], '',
              'The snapshot generator was not run, validated, dry-run, or edited. Prior artifacts were retained. All new artifacts use the veto_floor2_ prefix. The manifest lists SHA256 and CSV row counts for outputs; non-CSV row counts are null. The manifest itself has no embedded self-hash because that would be self-referential; its exact digest is emitted separately on completion.', '',
              'No corrected figure, published-number adjustment, or interpretation was computed. Stopped after this report.', '']
    report='\n'.join(lines)
    assert '\u2014' not in report
    write_text('veto_floor2_report.md',report)
    manifest={'status':'complete','scope':'Known-defective measurement characterization; not framework evidence or registered characterization data.',
              'created_utc':now(),'head':plan['head'],'machine':first['machine'],'python':first['python'],'numpy':first['numpy'],
              'preconditions':plan['gates'],'worker_count_actually_used':progress['peak_active_workers'],'cpu_budget':16,
              'null_device_exemption':True,'simulation_source_sha256':sources,'summary':summary,'outputs':[],
              'row_count_convention':'csv.DictReader excluding header; null for non-CSV outputs.',
              'self_hash_convention':'Manifest sha256 is null to avoid self-reference. Exact digest is emitted separately on completion.'}
    names = [p for p in OUT.iterdir() if p.is_file() and p.name.startswith('veto_floor2_')]
    manifest_path = OUT/'veto_floor2_manifest.json'
    if manifest_path not in names:
        names.append(manifest_path)
    for p in sorted(names):
        count=None
        if p.suffix.lower()=='.csv':
            with p.open(encoding='utf-8',newline='') as f:
                count=sum(1 for _ in csv.DictReader(f))
        manifest['outputs'].append({'path':p.relative_to(ROOT).as_posix(),'sha256':None if p==manifest_path else sha(p),'row_count':count})
    write('veto_floor2_manifest.json',manifest)
    for item in manifest['outputs']:
        if item['sha256'] is not None and sha(ROOT/item['path']) != item['sha256']:
            raise RuntimeError('Final artifact hash mismatch')
    print(json.dumps({'status':'complete','summary':summary,'manifest_sha256':sha(manifest_path),'outputs':len(manifest['outputs'])}),flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--job')
    parser.add_argument('--mode',choices=['normal','work'])
    parser.add_argument('--finalize',action='store_true')
    args=parser.parse_args()
    try:
        if args.prepare: prepare()
        elif args.run: run_batch()
        elif args.job: worker(args.job)
        elif args.mode:
            write('veto_floor2_control.json',{'mode':args.mode,'updated_utc':now()})
            print('CPU mode requested: '+args.mode,flush=True)
        elif args.finalize: finalize()
        else: parser.error('Specify an operation')
        assert_guard()
    except BaseException as error:
        name='veto_floor2_failure_'+(args.job or 'controller')+'.json'
        write(name,{'halt':str(error),'utc':now(),'violations':VIOLATIONS,'traceback':traceback.format_exc()})
        print('HALT: '+str(error),flush=True)
        raise SystemExit(2)

if __name__=='__main__':
    main()
