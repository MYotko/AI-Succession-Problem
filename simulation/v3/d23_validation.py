"""D23 non-registered evidence: identical jobs, observer isolation and scope.

This does not read or generate registered rerun output. The original six
validation job identities, seeds, calibration and probe tables are reused.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys
from .artifacts import ROOT, SIMULATION, read, unseal, seal, atomic_json, canonical, digest, code_identity, file_hash

ORIGINAL = ROOT / 'runs/a2_recording_validation'
WORK = ROOT / 'runs/a2_review_validation/final'


def prepare():
    original = unseal(read(ORIGINAL / 'spec.json'))
    if original['registered'] or any(j['tag'] != 'validation' for j in original['jobs']):
        raise ValueError('non-registered validation jobs required')
    baseline = read(ORIGINAL / 'baseline_source.json')
    for name, expected in baseline['sha256'].items():
        if file_hash(ORIGINAL / 'baseline' / name) != expected:
            raise ValueError('34ffbfe9 snapshot changed')
    spec = deepcopy(original)
    spec['schema'] = 'v3-D23-validation-1'
    spec['code_hash'] = code_identity()
    atomic_json(WORK / 'spec.json', seal(spec))
    atomic_json(WORK / 'inputs.json', {'registered': False, 'baseline': baseline,
                'original_spec_sha256': file_hash(ORIGINAL / 'spec.json'),
                'probe_table_sha256': file_hash(ORIGINAL / 'A1_probe_tables.json'),
                'job_identities_preserved': True, 'source_identity': spec['code_hash']})
    return {'jobs': len(spec['jobs']), 'spec': str(WORK / 'spec.json'), 'launched': False}


SCRIPT = r'''
import hashlib, time
import numpy as np
from pathlib import Path
from v3.artifacts import read, canonical, runtime
from v3.integration import V3Model
from v3.production_runner import execute
if VARIANT == 'off':
    import v3.recording as recording
    recording.RecordedV3Model = V3Model
    recording.pack_evidence = lambda result: result
job = read(JOB_PATH)
trace = hashlib.sha256(); calls = [0]; choices = []; steps = []
original_rng, original_eligible = V3Model._rng, V3Model._eligible
original_choose, original_step = V3Model._choose, V3Model.step
def state_hash(model):
    value = hashlib.sha256()
    for name in ('ages','welfare','traits','bank','stocks','window','counts','h_n'):
        array = np.asarray(getattr(model.state,name))
        value.update(canonical([name,str(array.dtype),array.shape])); value.update(array.tobytes())
    return value.hexdigest()
class Audited:
    def __init__(self,rng,identity): self.rng,self.identity = rng,identity
    def __getattr__(self,name):
        target = getattr(self.rng,name)
        def draw(*args,**kwargs):
            value = target(*args,**kwargs); array=np.asarray(value)
            trace.update(canonical([self.identity,name,str(array.dtype),array.shape]))
            trace.update(array.tobytes()); calls[0]+=1
            return value
        return draw
def eligible(self, actions):
    result = original_eligible(self, actions)
    self._diagnostic_eligibility = (result[0].copy(),result[1].copy(),result[2])
    return result
def choose(self, evaluation):
    pre = state_hash(self)
    selected = original_choose(self,evaluation)
    mask,risks,survival_first = self._diagnostic_eligibility
    minimum = risks == risks.min()
    qualifying = bool(survival_first and not np.any(minimum & evaluation.available))
    if survival_first: mask &= minimum
    mask &= evaluation.available
    old_choice = int(np.argmax(np.where(mask,evaluation.scores,-np.inf))) if mask.any() else 0
    choices.append({'time':self.time,'qualifying':qualifying,'chosen':selected[0],
                    'legacy_choice_on_same_state':old_choice,'survival_first':bool(survival_first),
                    'minimum_indices':np.flatnonzero(minimum).tolist(),'available':evaluation.available.tolist(),
                    'risks':risks.tolist(),'prestate_sha256':pre})
    if VARIANT != 'baseline' and selected[0] != old_choice and not qualifying:
        raise AssertionError('selection changed outside D23 trigger')
    if VARIANT != 'baseline' and survival_first and not minimum[selected[0]]:
        raise AssertionError('survival-first selected a nonminimum bound')
    return selected
def step(self):
    value = original_step(self)
    steps.append({'time':value['time'],'state_sha256':state_hash(self),
                  'draw_sha256':trace.hexdigest(),'draw_calls':calls[0]})
    return value
V3Model._rng = lambda self, channel: Audited(original_rng(self,channel),[self.time,channel])
V3Model._eligible, V3Model._choose, V3Model.step = eligible, choose, step
metadata = runtime(1)
started = time.perf_counter(); result = execute(job,False,None)
Path(OUT_PATH).write_bytes(canonical({'result':result,'seconds':time.perf_counter()-started,
    'draw_sha256':trace.hexdigest(),'draw_calls':calls[0],'choices':choices,'steps':steps,'runtime':metadata})+b'\n')
'''


ADDED_STEP_FIELDS = {'survival_first_scores_unavailable', 'selection_reason', 'minimum_bound_unavailable_count'}


def legacy_step(step):
    return {k: v for k, v in step.items() if k not in ADDED_STEP_FIELDS and k != 'gate_evidence'}


def compare(workers=4):
    if not 1 <= workers <= 12:
        raise ValueError('at most twelve local workers')
    spec = unseal(read(WORK / 'spec.json'))
    if spec['registered'] or spec['code_hash'] != code_identity():
        raise ValueError('validation mode or source changed')
    measured = read(WORK / 'runner/launches.json')[-1]['outcomes']['rerun']['selection']
    workers = min(workers, measured['workers'])
    tasks = []
    for job in spec['jobs']:
        path = WORK / 'pairs' / (job['id'] + '.job.json')
        atomic_json(path, job)
        tasks.extend((job, path, variant) for variant in ('baseline', 'off', 'on'))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
    def run(item):
        job, path, variant = item
        target = WORK / 'pairs' / (job['id'] + '.' + variant + '.json')
        body = f'JOB_PATH={str(path)!r}\nOUT_PATH={str(target)!r}\nVARIANT={variant!r}\n' + SCRIPT
        source = ORIGINAL / 'baseline/simulation' if variant == 'baseline' else SIMULATION
        result = subprocess.run([sys.executable, '-B', '-c', body], cwd=source, env=dict(env, PYTHONPATH=str(source)),
                                capture_output=True, timeout=900)
        if result.returncode:
            raise RuntimeError(result.stderr.decode(errors='replace'))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(run, tasks))
    report = []
    from .production_runner import completed
    for job in spec['jobs']:
        base, off, on = [read(WORK / 'pairs' / (job['id'] + '.' + v + '.json')) for v in ('baseline','off','on')]
        observed = deepcopy(on['result']); observed.pop('gate_evidence')
        if canonical(observed) != canonical(off['result']) or on['draw_sha256'] != off['draw_sha256'] or on['draw_calls'] != off['draw_calls'] or on['steps'] != off['steps'] or on['choices'] != off['choices']:
            raise AssertionError('observer changed scientific output, state or original draws')
        real = completed(WORK / 'runner/rerun', job, spec['code_hash'])
        if canonical(real['result']) != canonical(on['result']):
            raise AssertionError('paired observer differs from real runner')
        a_events = {e['time']: e for e in base['result']['yield_events']}
        b_events = {e['time']: e for e in observed['yield_events']}
        first = None
        for a, b in zip(base['result']['diagnostics'], observed['diagnostics']):
            t = a['time']
            if canonical(a) != canonical(legacy_step(b)) or canonical(a_events.get(t)) != canonical(b_events.get(t)) or base['steps'][t] != on['steps'][t]:
                first = t
                break
        old_choices, new_choices = [{c['time']: c for c in p['choices']} for p in (base,on)]
        trigger = None
        if first is not None:
            trigger = new_choices[first]
            if not trigger['qualifying'] or trigger['prestate_sha256'] != old_choices[first]['prestate_sha256'] or trigger['risks'] != old_choices[first]['risks'] or trigger['available'] != old_choices[first]['available']:
                raise AssertionError('first difference not explained by D23 on identical inputs')
        else:
            old_result = deepcopy(observed)
            old_result.pop('override_records')
            old_result['continuation_availability'].pop('survival_first_scores_unavailable_steps')
            old_result['diagnostics'] = [legacy_step(s) for s in old_result['diagnostics']]
            if canonical(old_result) != canonical(base['result']):
                raise AssertionError('unexplained aggregate difference')
        report.append({'job':job,'observer_scientific_bytes_identical':True,'observer_draws_identical':True,
                       'observer_states_identical':True,'matches_real_runner':True,'first_34ffbfe9_difference':first,
                       'first_difference_evidence':trigger,'qualifying_steps':sum(c['qualifying'] for c in on['choices']),
                       'choices_differing_from_legacy_on_same_state':sum(c['chosen']!=c['legacy_choice_on_same_state'] for c in on['choices']),
                       'changed_choices_outside_trigger':0,'original_draw_calls':on['draw_calls'],
                       'on_scientific_sha256':digest(observed),'off_scientific_sha256':digest(off['result']),
                       'pair_file_sha256':{v:file_hash(WORK / 'pairs' / (job['id']+'.'+v+'.json')) for v in ('baseline','off','on')},
                       'seconds':{v:p['seconds'] for v,p in zip(('baseline','off','on'),(base,off,on))},
                       'fired':sum(e['transition_count'] for e in observed['yield_events'])})
    result = {'registered':False,'source_identity':spec['code_hash'],'baseline_commit':'34ffbfe99e79ea9f546f1ed353a251ef8aede08e',
              'tables':'identical existing non-registered sparse probes and FixtureTables; no registered table repair',
              'workers':workers,'measured_configuration':measured,'jobs':report}
    atomic_json(WORK / 'comparison.json',result)
    return {'jobs':len(report),'observer_identical':True,'first_differences':[r['first_34ffbfe9_difference'] for r in report]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('prepare','compare')); p.add_argument('--workers',type=int,default=4)
    a = p.parse_args()
    print(prepare() if a.command == 'prepare' else compare(a.workers))


if __name__ == '__main__':
    main()
