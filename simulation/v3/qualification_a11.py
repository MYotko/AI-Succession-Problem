"""Non-registered A11 machine qualification, with deterministic short jobs.

Export a bundle on X2. Candidates pull that bundle over SSH. No qualification
output is registered, and no result values are printed by this tool.
"""
import argparse
import base64
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
import hashlib
import multiprocessing as mp
from pathlib import Path
import platform
import shutil
import time
from .artifacts import (SIMULATION, atomic_json, canonical, code_identity, configure_threads, digest,
                        file_hash, read, scoped, seal, stable_job, unseal)
from .worker_safety import persist_restarts

SCHEMA = 'v3-A11-qualification-1'


def build(spec_path, source_root, output, kinds=None):
    """Prefer shortest completed same-identity reference jobs in each kind.

    If a kind has no registered outputs, use its actual configuration profile,
    with deterministic validation stream seeds and at least 20 distinct jobs.
    The selection and canonical reference hashes are frozen before execution.
    """
    from .production_runner import completed
    from .multihost_a11 import ALLOWED_KINDS
    from .snapshot_a11 import inventory
    from .compatibility_a10 import comparison_bytes
    spec = unseal(read(spec_path))
    if spec['code_hash'] != code_identity() or spec.get('instrument', {}).get('mapping') != 'A10':
        raise ValueError('qualification needs the current A10 launch identity')
    available = {j['kind'] for j in spec['jobs']}
    kinds = sorted(kinds or available)
    if not set(kinds) <= available or not set(kinds) <= ALLOWED_KINDS:
        raise ValueError('unsupported qualification kind')
    target = scoped(output)
    if target.exists():
        raise ValueError('qualification plan is frozen')
    jobs, references, phase_roots = [], {}, {}
    for kind in kinds:
        candidates = [j for j in spec['jobs'] if j['kind'] == kind]
        def cost(j):
            c = j['config']; cfg = c.get('a1_job', j)['config']; s = cfg.get('settings', {})
            return s.get('particles', 1) * (s.get('burn', 0) + s.get('measure', c.get('steps', 1)))
        candidates.sort(key=lambda j: (cost(j), digest(['A11-qualification', j['id']]), j['id']))
        done = []
        if spec.get('registered') and kind != 'a13_validate_plain_ext':
            for j in candidates:
                value = completed(Path(source_root) / j['config']['phase'], j, spec['code_hash'])
                if value is not None:
                    done.append((j, value))
                if len(done) >= max(20, (20 + len(kinds) - 1) // len(kinds)):
                    break
        if done:
            for j, value in done:
                jobs.append(j)
                references[j['id']] = hashlib.sha256(comparison_bytes(j, value['result'])).hexdigest()
                phase_roots[j['id']] = str(Path(source_root).resolve() / j['config']['phase'])
            if len(done) >= 20:
                continue
        profiles = [(phase, p) for phase, p in spec['configuration'].items() if p['kind'] == kind]
        if not profiles:
            raise ValueError('no short configuration profile for ' + kind)
        configs = [dict(c, phase=phase) for phase, p in profiles for c in p.get('configs', [p['config']])]
        configs.sort(key=lambda c: digest(['A11-qualification-short', c]))
        for index in range(max(20 - len(done), len(configs))):
            cfg = deepcopy(configs[index % len(configs)])
            # A4/A5 consume config.seed, rather than the outer seed. These are
            # disjoint, explicitly non-registered fixture streams on both hosts.
            if kind.startswith(('a4_', 'a5_', 'a13_')):
                cfg['seed'] = (1 << 128) | int(digest(['A11-qualification-stream', kind, cfg, index])[:32], 16)
            job = stable_job(kind, cfg, 'validation', index)
            jobs.append(job)
            phase_roots[job['id']] = str(Path(source_root).resolve() / cfg['phase'])
    if len(jobs) < 20:
        # Never manufacture independence by duplicating a registered result.
        raise ValueError('fewer than 20 distinct reference jobs; qualify after more outputs or before registration with fixture profiles')
    files = {}
    simulation = str(SIMULATION)
    for job in jobs:
        snapshot = unseal(inventory([job], phase_roots[job['id']], spec.get('pull_dispatch', {}).get('extra_inputs', [])))
        for row in snapshot['files']:
            files[row['path']] = row
    snapshot = seal({'schema': 'v3-A11-inputs-1', 'simulation': simulation, 'files': [files[k] for k in sorted(files)]})
    bundle = target.parent / (target.stem + '_files')
    for row in snapshot['payload']['files']:
        path = scoped(bundle / row['path']); path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SIMULATION / row['path'], path)
        if file_hash(path) != row['sha256']:
            raise ValueError('qualification input changed during copy')
    plan = {'schema': SCHEMA + '-plan', 'non_registered': True, 'code_hash': code_identity(),
        'jobs': jobs, 'kinds': kinds, 'phase_roots': phase_roots, 'inputs': snapshot,
        'references': references, 'bundle_directory': bundle.name,
        'selection': 'shortest registered outputs then A11-qualification hash; otherwise deterministically ordered short profiles',
        'comparison': 'A11 canonical job plus result'}
    from . import worker_control as wc
    resources = wc.configuration_resources(jobs, spec['jobs'], wc.resources(spec), spec=spec)
    resources.update(wc.trial_resources([j for j in jobs if j['id'] not in references]))
    plan['memory_estimate_gb'] = {j['id']: wc.reservation(resources[j['id']], {}) for j in jobs}
    plan['memory_estimate_known'] = {j['id']: resources[j['id']]['memory_known'] for j in jobs}
    plan['memory_classes'] = {j['id']: resources[j['id']]['memory_class'] for j in jobs}
    atomic_json(target, seal(plan))
    return plan


def _run_one(args):
    from .host_a11 import execute_scratch
    from .compatibility_a10 import comparison_bytes
    target, job, code, phase_root, view, host = args
    # A signal can arrive after the durable result but before this hash returns.
    # Recover that result on resubmission; never execute the returned job twice.
    if not Path(target).exists():
        execute_scratch(target, job, code, phase_root, view, False, None, host, 'qualification')
    result = read(target)
    if result['job'] != job or result['code_hash'] != code or result['host'] != host:
        raise ValueError('qualification returned result identity mismatch')
    return {'job_id': job['id'], 'kind': job['kind'], 'job_sha256': digest(job),
            'canonical_sha256': hashlib.sha256(comparison_bytes(job, result['result'])).hexdigest(),
            'output_sha256': file_hash(target), 'worker_seconds': result['seconds'], 'peak_rss_bytes': result.get('peak_rss_bytes')}


def run(plan_path, output, settings, *, environment=None, host=None):
    from .host_a11 import fingerprint
    from .production_runner import caps, mem_available_bytes, available_cpus
    from .snapshot_a11 import receive
    plan = unseal(read(plan_path))
    if plan['code_hash'] != code_identity() or not plan['non_registered']:
        raise ValueError('qualification source identity mismatch')
    target = scoped(output)
    if target.exists():
        raise ValueError('qualification run is frozen')
    root = target.parent / (target.stem + '_scratch')
    from . import worker_control as wc
    settings = wc.settings(settings)
    from .worker_safety import swap_preflight
    swap = swap_preflight(settings, root / 'worker_metadata' / 'swap_preflight.json')
    configure_threads(1)
    memory = mem_available_bytes()
    if memory is None:
        raise ValueError('qualification needs measured memory')
    worker_limit = wc.selection(settings)['workers']
    resources = wc.resources(plan)
    wc.require_memory_authority(settings, None, resources, {})
    memory_budget = settings.get('memory_headroom', .8) * memory / 1e9
    if wc.top_weighted(wc.reservation(r, {}) for r in resources.values()) > memory_budget:
        raise ValueError('qualification job does not fit measured memory')
    bundle = Path(plan_path).parent / plan['bundle_directory']
    def reader(name, offset):
        with (bundle / name).open('rb') as stream:
            stream.seek(offset); data = stream.read(4 * 1024 * 1024)
        return {'data': base64.b64encode(data).decode('ascii'), 'offset': offset, 'sha256': hashlib.sha256(data).hexdigest()}
    view = receive(plan['inputs'], root / 'snapshots', reader)
    before = time.perf_counter()
    host = host or platform.node()
    environment = environment or fingerprint()
    # Same declared short work on each machine. The launch still performs its
    # own configuration test after join; qualification throughput describes this
    # reproducible parallel workload, including the selected worker count.
    tasks = [(str(root / 'unpublished' / (j['id'] + '.json')), j, plan['code_hash'], plan['phase_roots'][j['id']], view, host)
             for j in plan['jobs']]
    from concurrent.futures import wait, FIRST_COMPLETED
    pending, active, results, peaks, admission = list(tasks), {}, {}, {}, []
    from .worker_safety import IsolatedPools, KilledWorker, restart, require_retry_budget
    restarts_path = root / 'worker_metadata' / 'restarts.json'
    restarts = read(restarts_path) if restarts_path.exists() else []
    with IsolatedPools(root / 'worker_metadata' / 'returns') as pool:
        while pending or active:
            charges, weight = wc.admission_charges({t[1]['id']: resources[t[1]['id']] for t in pending + list(active.values())}, peaks)
            occupied = sum(charges[t[1]['id']] for t in active.values())
            while pending and len(active) < worker_limit:
                available = mem_available_bytes()
                free = min(memory_budget - occupied, settings['memory_headroom'] * available / 1e9) if available else 0.
                index = next((i for i,t in enumerate(pending) if charges[t[1]['id']] <= free), None)
                if index is None: break
                task = pending.pop(index)
                if not Path(task[0]).exists(): require_retry_budget(restarts, task[1]['id'])
                occupied += charges[task[1]['id']]
                active[pool.submit(_run_one, task)] = task
                admission.append(dict(running=len(active), reserved_gb=occupied, budget_gb=memory_budget, top_weighted_gb=weight))
            if not active:
                raise ValueError('qualification memory unavailable; no proof work admitted')
            completed, _ = wait(active, return_when=FIRST_COMPLETED)
            for future in completed:
                task = active.pop(future)
                try:
                    result = pool.result(future)
                except KilledWorker as exc:
                    event = restart(restarts, task[1]['id'], exc.signal)
                    persist_restarts(restarts_path, restarts)
                    if not event['allowed']: raise RuntimeError('worker exhausted three signal reruns')
                    pending.append(task)
                    continue
                results[task[1]['id']] = result
                wc.observe(peaks, resources[task[1]['id']], result.get('peak_rss_bytes'))
    proofs = [results[j['id']] for j in plan['jobs']]
    elapsed = time.perf_counter() - before
    result = {'schema': SCHEMA + '-run', 'non_registered': True, 'plan_sha256': digest(plan), 'code_hash': code_identity(),
        'host': host, 'fingerprint': environment, 'memory_gb': memory / 1e9, 'elapsed_seconds': elapsed,
        'settings': settings, 'workers': min(worker_limit, len(tasks)), 'memory_cap': worker_limit,
        'memory_budget_gb': memory_budget, 'admission': admission, 'swap': swap, 'restarts': restarts,
        'proofs': proofs, 'kinds': plan['kinds'],
        'passed': all(plan['references'].get(p['job_id'], p['canonical_sha256']) == p['canonical_sha256'] for p in proofs)}
    atomic_json(target, seal(result))
    return result


def compare(plan_document, reference_document, candidate_document):
    plan, ref, candidate = map(unseal, (plan_document, reference_document, candidate_document))
    if ref['host'].lower() != 'yotko-evo-x2':
        raise ValueError('qualification reference must be the X2')
    if any(r['plan_sha256'] != plan_document['sha256'] or r['code_hash'] != plan['code_hash'] for r in (ref, candidate)):
        raise ValueError('qualification plan or code mismatch')
    proofs = []
    left, right = ({p['job_id']: p for p in r['proofs']} for r in (ref, candidate))
    if set(left) != set(right) or set(left) != {j['id'] for j in plan['jobs']}:
        raise ValueError('qualification job population mismatch')
    for job in plan['jobs']:
        a, b = left[job['id']], right[job['id']]
        proofs.append({'job_id': job['id'], 'kind': job['kind'], 'job_sha256': digest(job),
            'reference_sha256': a['canonical_sha256'], 'candidate_sha256': b['canonical_sha256'],
            'passed': a['job_sha256'] == b['job_sha256'] == digest(job)
                      and a['canonical_sha256'] == b['canonical_sha256']
                      and plan.get('references', {}).get(job['id'], a['canonical_sha256']) == a['canonical_sha256']})
    result = {'schema': SCHEMA, 'non_registered': True, 'code_hash': plan['code_hash'], 'plan': plan_document,
        'reference': ref, 'candidate': candidate, 'reference_record_sha256': reference_document['sha256'],
        'candidate_record_sha256': candidate_document['sha256'], 'kinds': plan['kinds'], 'proofs': proofs,
        'relative_throughput': 1. if ref['host'] == candidate['host'] else ref['elapsed_seconds'] / candidate['elapsed_seconds'],
        'passed': ref['passed'] and candidate['passed'] and all(p['passed'] for p in proofs)}
    return seal(result)


def validate_evidence(document, code):
    from .multihost_a11 import positive
    e = unseal(document)
    if e['schema'] != SCHEMA or not e['non_registered'] or not e['passed'] or e['code_hash'] != code:
        raise ValueError('failed or wrong-identity qualification')
    if len(e['proofs']) < 20 or len({p['job_id'] for p in e['proofs']}) != len(e['proofs']):
        raise ValueError('qualification requires at least 20 distinct jobs')
    plan = unseal(e['plan'])
    if plan.get('schema') != SCHEMA + '-plan' or plan.get('non_registered') is not True or plan.get('code_hash') != code:
        raise ValueError('qualification selection is not a sealed current plan')
    if any(stable_job(j['kind'], j['config'], j['tag'], j['index']) != j for j in plan['jobs']):
        raise ValueError('qualification job or seed was modified')
    if set(e['kinds']) != {p['kind'] for p in e['proofs']} or not all(p['passed'] and p['reference_sha256'] == p['candidate_sha256'] for p in e['proofs']):
        raise ValueError('qualification failed or lacks kind coverage')
    if (not positive(e['relative_throughput']) or not positive(e['candidate']['memory_gb'])
            or not e['candidate']['host'] or not e['candidate']['fingerprint']):
        raise ValueError('missing machine qualification measurements')
    keys = {'python', 'numpy', 'numpy_cpu_baseline', 'numpy_cpu_dispatch', 'numpy_cpu_features',
            'conda_packages_sha256', 'threads_configured', 'threads_verified'}
    for run in (e['reference'], e['candidate']):
        if (run.get('schema') != SCHEMA + '-run' or run.get('non_registered') is not True
                or set(run['fingerprint']) != keys or run['fingerprint']['threads_configured'] != 1
                or not run['fingerprint']['threads_verified']
                or any(v['effective'] != 1 for v in run['fingerprint']['threads_verified'])):
            raise ValueError('incomplete environment fingerprint or thread verification')
    rebuilt = compare(e['plan'], seal(e['reference']), seal(e['candidate']))
    if rebuilt != document:
        raise ValueError('qualification evidence was modified')
    return e



def scheduling_rate(evidence):
    """Per-job speed only; keep the existing elapsed participation rate intact."""
    from .worker_control import positive
    left, right = evidence['reference'], evidence['candidate']
    if left['host'] == right['host']: return 1.
    maps = [{p['job_id']: p.get('worker_seconds') for p in run['proofs']} for run in (left, right)]
    if set(maps[0]) == set(maps[1]) and maps[0] and all(positive(x) for row in maps for x in row.values()):
        return sum(maps[0].values()) / sum(maps[1].values())
    # Older evidence without per-job timings can only compare equal concurrency.
    workers = [r.get('workers', r.get('settings', {}).get('workers')) for r in (left, right)]
    if not all(positive(n) for n in workers) or workers[0] != workers[1]:
        raise ValueError('scheduling needs per-job timing or equal qualification worker counts')
    return evidence['relative_throughput']

def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('build'); s.add_argument('spec'); s.add_argument('source_root'); s.add_argument('output')
    s.add_argument('--kind', action='append')
    s = sub.add_parser('run'); s.add_argument('plan'); s.add_argument('output')
    s.add_argument('--profile', choices=('x2', 'local'), required=True)
    s.add_argument('--model-service', choices=('llm', 'none'), help='default llm for X2, none for local')
    s.add_argument('--workers', type=int, required=True); s.add_argument('--cpu-budget', type=int, required=True)
    s.add_argument('--mode', choices=('work', 'normal'))
    from . import worker_control as wc
    wc.options(s)
    s = sub.add_parser('compare'); s.add_argument('plan'); s.add_argument('reference'); s.add_argument('candidate'); s.add_argument('output')
    args = p.parse_args()
    if args.command == 'build':
        result = build(args.spec, args.source_root, args.output, args.kind)
        print({'jobs': len(result['jobs']), 'kinds': result['kinds'], 'sha256': file_hash(args.output)})
    elif args.command == 'compare':
        document = compare(read(args.plan), read(args.reference), read(args.candidate))
        if Path(args.output).exists():
            raise ValueError('qualification evidence is final')
        atomic_json(args.output, document)
        print({'passed': document['payload']['passed'], 'sha256': file_hash(args.output)})
    else:
        from .host_a11 import host_service
        root = scoped(args.output).parent; root.mkdir(parents=True, exist_ok=True)
        settings = {k: getattr(args, k) for k in ('profile', 'workers', 'cpu_budget', 'mode')}
        settings['mode'] = settings['mode'] or ('normal' if settings['profile'] == 'x2' else 'work')
        settings['threads'] = 1
        settings.update(wc.arguments(args))
        settings = wc.settings(settings)
        from .service import model_service
        if args.model_service is not None:
            settings['model_service'] = args.model_service
        settings['model_service'] = model_service(settings)
        with host_service(root, args.profile, settings['model_service']):
            result = run(args.plan, args.output, settings)
        print({'passed': result['passed'], 'jobs': len(result['proofs']), 'sha256': file_hash(args.output)})


if __name__ == '__main__':
    main()
