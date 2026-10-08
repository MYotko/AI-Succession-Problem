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
        if spec.get('registered'):
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
            if kind.startswith(('a4_', 'a5_')):
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
    estimates = {}
    for phase in spec['phases']:
        values = [spec.get('memory_estimate_gb', {}).get(phase, .25)]
        pull = spec.get('pull_dispatch')
        if pull:
            values += [pull['cost_classes'][pull['job_classes'][j['id']]]['memory_gb'] for j in spec['jobs'] if j['config']['phase'] == phase]
        estimates[phase] = max(values)
    plan['memory_estimate_gb'] = {j['id']: estimates[j['config']['phase']] for j in jobs}
    atomic_json(target, seal(plan))
    return plan


def _run_one(args):
    from .host_a11 import execute_scratch
    from .compatibility_a10 import comparison_bytes
    target, job, code, phase_root, view, host = args
    execute_scratch(target, job, code, phase_root, view, False, None, host, 'qualification')
    result = read(target)
    return {'job_id': job['id'], 'kind': job['kind'], 'job_sha256': digest(job),
            'canonical_sha256': hashlib.sha256(comparison_bytes(job, result['result'])).hexdigest(),
            'output_sha256': file_hash(target), 'worker_seconds': result['seconds']}


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
    settings = dict(settings, caps=caps(settings['profile'], settings['cpu_budget']))
    configure_threads(1)
    memory = mem_available_bytes()
    if memory is None:
        raise ValueError('qualification needs measured memory')
    worker_limit = min(settings['workers'], settings['caps'][settings['mode']])
    if not 1 <= settings['workers'] <= settings['caps'][settings['mode']] or settings['threads'] != 1 or settings['cpu_budget'] > available_cpus():
        raise ValueError('qualification worker caps')
    memory_cap = int(memory * .8 / 1e9 / max(plan['memory_estimate_gb'].values()))
    if memory_cap < 1:
        raise ValueError('qualification job does not fit measured memory')
    worker_limit = min(worker_limit, memory_cap)
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
    with ProcessPoolExecutor(max_workers=min(worker_limit, len(tasks)), mp_context=mp.get_context('spawn')) as pool:
        proofs = list(pool.map(_run_one, tasks))
    elapsed = time.perf_counter() - before
    result = {'schema': SCHEMA + '-run', 'non_registered': True, 'plan_sha256': digest(plan), 'code_hash': code_identity(),
        'host': host, 'fingerprint': environment, 'memory_gb': memory / 1e9, 'elapsed_seconds': elapsed,
        'settings': settings, 'workers': min(worker_limit, len(tasks)), 'memory_cap': memory_cap,
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


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    s = sub.add_parser('build'); s.add_argument('spec'); s.add_argument('source_root'); s.add_argument('output')
    s.add_argument('--kind', action='append')
    s = sub.add_parser('run'); s.add_argument('plan'); s.add_argument('output')
    s.add_argument('--profile', choices=('x2', 'local'), required=True)
    s.add_argument('--workers', type=int, required=True); s.add_argument('--cpu-budget', type=int, required=True)
    s.add_argument('--mode', choices=('work', 'normal'), default='work')
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
        settings['threads'] = 1
        with host_service(root, args.profile):
            result = run(args.plan, args.output, settings)
        print({'passed': result['passed'], 'jobs': len(result['proofs']), 'sha256': file_hash(args.output)})


if __name__ == '__main__':
    main()
