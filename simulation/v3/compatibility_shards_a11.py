"""Executor-only A11 proof shards. No retries, changed jobs, or scientific output.

The original host freezes the one attempt after qualification. Each host runs
its shard once after preflight; an interrupted proof spends it. Only comparison hashes
return. Scheduling metadata never enters a job or comparison_bytes().
"""
import argparse
import base64
from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
from copy import deepcopy
import hashlib
import json
import math
import multiprocessing as mp
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time

from .artifacts import (ROOT, SIMULATION, atomic_json, canonical, code_identity,
                        configure_threads, digest, file_hash, read, scoped, seal,
                        source_manifest, stable_job, unseal)
from .compatibility_a10 import _require, _selected, _stratum, collect_record, proof_row, _execute_proof

SCHEMA = 'v3-A11-proof-shards-1'
MEMORY_WAIT_SECONDS = 180.
PROOF_MEMORY_WAIT_SECONDS = 1800.
MEMORY_POLL_SECONDS = 1.


def reservation_path(record):
    """One exclusive reservation per identity pair, independent of output."""
    from .compatibility_a10 import RECORD_DIRECTORY
    return scoped(RECORD_DIRECTORY / '.a11_attempts' /
                  (digest([record['producing_code_hash'], record['new_code_hash']]) + '.json'))


def reserve_attempt(record, payload, path):
    reservation = dict(schema=SCHEMA + '-reservation', producing_code_hash=record['producing_code_hash'],
                       new_code_hash=record['new_code_hash'], attempt_sha256=digest(payload),
                       attempt_path=scoped(path).relative_to(SIMULATION).as_posix())
    write_once(reservation_path(record), seal(reservation))
    check_reservation(record, payload, path)


def check_reservation(record, payload, path):
    saved = unseal(read(reservation_path(record)))
    _require(saved == dict(schema=SCHEMA + '-reservation', producing_code_hash=record['producing_code_hash'],
                          new_code_hash=record['new_code_hash'], attempt_sha256=digest(payload),
                          attempt_path=scoped(path).relative_to(SIMULATION).as_posix()),
             'different compatibility attempt reserved for this identity pair; attempt is final')


def positive(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def write_once(path, document):
    """An exclusive create spends the attempt, including an interrupted write."""
    path = scoped(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('xb') as stream:
            stream.write(canonical(document) + b'\n')
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise ValueError('compatibility attempt is final; selection or shard already exists') from exc


def memory_budget(limit_gb=None):
    # production_runner.memory_worker_cap and multihost_a11.Coordinator.claim:
    # 80% of available memory, bounded by the host's qualified memory.
    from .production_runner import mem_available_bytes
    available = mem_available_bytes()
    _require(available is not None and available > 0, 'proof needs measured available memory')
    if limit_gb is not None:
        _require(positive(limit_gb), 'invalid qualified memory')
    return .8 * min(available / 1e9, limit_gb if limit_gb is not None else math.inf)


def wait_for_memory(required, limit_gb=None, *, timeout=MEMORY_WAIT_SECONDS):
    """Bound the idle wait separately for repeatable setup and final proof work."""
    _require(positive(required), 'invalid required memory')
    _require(positive(timeout), 'invalid memory wait bound')
    _require(limit_gb is None or required <= .8 * limit_gb, 'proof job exceeds qualified memory budget')
    deadline = time.monotonic() + timeout
    while True:
        budget = memory_budget(limit_gb)
        if budget >= required:
            return budget
        remaining = deadline - time.monotonic()
        _require(remaining > 0, f'available memory did not recover within {timeout:g} seconds')
        time.sleep(min(MEMORY_POLL_SECONDS, remaining))


def resource_estimate(spec, job):
    phase = job['config'].get('phase', job['kind'])
    pull = spec.get('pull_dispatch')
    if pull:
        key = pull['job_classes'][job['id']]
        cls = pull['cost_classes'][key]
        seconds, memory = cls['worker_seconds'], cls['memory_gb']
        _require(positive(seconds) and positive(memory), 'invalid registered cost class')
    else:
        _require(not spec.get('registered'), 'registered proof needs its registered cost classes')
        key, seconds, memory = phase, 1., .25
    memory = max(memory, spec.get('memory_estimate_gb', {}).get(phase, memory))
    _require(positive(memory), 'invalid phase memory estimate')
    return dict(worker_seconds=seconds, memory_gb=memory,
                memory_class=digest([spec['code_hash'], pull.get('projection_sha256') if pull else None, key]))


def worker_cap(settings):
    from .production_runner import caps, available_cpus
    _require(settings['threads'] == 1 and settings['mode'] == 'work', 'proof requires one thread and work mode')
    _require(type(settings['workers']) is int and settings['workers'] > 0, 'invalid requested workers')
    _require(0 < settings['cpu_budget'] <= available_cpus(), 'CPU budget exceeds this host')
    return min(settings['workers'], caps(settings['profile'], settings['cpu_budget'])['work'])


def run_items(items, workers, budget, *, memory_floor_gb=0., idle_wait_seconds=PROOF_MEMORY_WAIT_SECONDS):
    """Longest fitting job first, one submission per job, no worker retries.

    Registered estimates plus the observed full-job floor are reservations.
    Completed peak RSS raises its class estimate by the runner's 1.2 margin.
    The current MemAvailable check also protects against unrelated allocations.
    """
    _require(positive(budget) and type(workers) is int and workers > 0, 'invalid proof resources')
    _require(type(memory_floor_gb) in (int, float) and math.isfinite(memory_floor_gb) and memory_floor_gb >= 0,
             'invalid observed memory floor')
    pending = sorted(items, key=lambda x: (-x['resources']['worker_seconds'], x['job']['id']))
    _require(len({x['job']['id'] for x in pending}) == len(pending), 'duplicate scheduled job')
    estimates = {}
    for item in pending:
        r = item['resources']
        _require(positive(r['memory_gb']) and positive(r['worker_seconds']), 'invalid scheduling estimate')
        estimates[r['memory_class']] = max(estimates.get(r['memory_class'], 0), r['memory_gb'], memory_floor_gb)
    _require(all(m <= budget for m in estimates.values()), 'proof job exceeds host memory budget')
    active, results, trace = {}, {}, []
    configure_threads(1)
    with ProcessPoolExecutor(max_workers=workers, mp_context=mp.get_context('spawn'), max_tasks_per_child=1) as pool:
        while pending or active:
            occupied = sum(max(m, estimates[i['resources']['memory_class']]) for i, m in active.values())
            while len(active) < workers and pending:
                free = min(budget - occupied, memory_budget())
                index = next((i for i, item in enumerate(pending)
                              if estimates[item['resources']['memory_class']] <= free), None)
                if index is None:
                    break
                item = pending.pop(index)
                needed = estimates[item['resources']['memory_class']]
                active[pool.submit(_execute_proof, item)] = (item, needed)
                occupied += needed
                trace.append(dict(job_id=item['job']['id'], reserved_gb=needed,
                                  running_gb=occupied, running=len(active), budget_gb=budget))
            if not active and pending:
                required = min(estimates[i['resources']['memory_class']] for i in pending)
                _require(required <= budget, 'observed proof memory exceeds frozen budget; attempt spent')
                wait_for_memory(required, timeout=idle_wait_seconds)
                continue
            if not active:
                break
            finished, _ = wait(active, return_when=FIRST_COMPLETED)
            for future in finished:
                item, _ = active.pop(future)
                result = future.result()
                results[item['job']['id']] = result
                peak = result.get('_peak_rss_bytes')
                if peak:
                    key = item['resources']['memory_class']
                    estimates[key] = max(estimates[key], 1.2 * peak / 1e9)
    return results, trace


def assign(items, hosts):
    """Deterministic LPT to least projected finish, cost / measured host rate.

    The conservative slots use each host's largest admitted estimate. Runtime
    admission may fit additional smaller jobs; neither changes this partition.
    """
    loads = {h: 0. for h in hosts}
    slots, shards = {}, {h: [] for h in hosts}
    for h, entry in hosts.items():
        maximum = max(max(i['resources']['memory_gb'], entry['memory_floor_gb']) for i in items.values())
        slots[h] = min(entry['worker_cap'], int(.8 * entry['memory_gb'] / maximum))
        _require(slots[h] >= 1 and positive(entry['relative_throughput']), 'host cannot admit a proof job')
    for jid in sorted(items, key=lambda j: (-items[j]['resources']['worker_seconds'], j)):
        cost = items[jid]['resources']['worker_seconds']
        h = min(hosts, key=lambda h: ((loads[h] + cost) / (slots[h] * hosts[h]['relative_throughput']), h))
        shards[h].append(jid)
        loads[h] += cost
    _require(all(shards.values()), 'empty proof shard')
    return shards


def portable_inventory(items):
    """Same execute dependencies as snapshot_a11, including old-checkout reads.

    Blob paths are local and safe; absolute aliases preserve original job bytes.
    No source output is copied unless execute needs it (e.g. A4's A1 and fit).
    """
    from .snapshot_a11 import dependencies
    files = {}
    for item in items:
        for path in dependencies([item['job']], item['phase_root']):
            key = digest(str(path))
            files[key] = dict(path='v3/proof_inputs/' + key + '/' + path.name,
                              source=str(path), aliases=[str(path)], sha256=file_hash(path), bytes=path.stat().st_size)
    return seal(dict(schema='v3-A11-inputs-1', simulation=str(SIMULATION), files=[files[k] for k in sorted(files)]))


def stage_inputs(document, bundle):
    for row in unseal(document)['files']:
        path = scoped(Path(bundle) / row['path'])
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            _require(file_hash(row['source']) == row['sha256'], 'source input changed')
            shutil.copyfile(row['source'], path)
        _require(file_hash(path) == row['sha256'], 'staged input hash mismatch')
        path.chmod(0o444)


def receive_inputs(document, bundle, scratch):
    from .snapshot_a11 import receive
    def reader(name, offset):
        with (Path(bundle) / name).open('rb') as stream:
            stream.seek(offset)
            data = stream.read(4 * 1024 * 1024)
        return dict(data=base64.b64encode(data).decode('ascii'), offset=offset,
                    sha256=hashlib.sha256(data).hexdigest())
    # Verify every bundled file even if a previous local snapshot exists.
    for row in unseal(document)['files']:
        _require(file_hash(Path(bundle) / row['path']) == row['sha256'], 'staged input hash mismatch')
    return receive(document, scratch, reader)


def check_input_paths(items, view):
    """Resolve every required read, including plain validation's fit sibling."""
    from .artifacts import input_path, input_view
    from .snapshot_a11 import dependencies
    mapped = {Path(v).resolve() for v in view['paths'].values()}
    with input_view(view):
        for item in items:
            for path in dependencies([item['job']], item['phase_root']):
                resolved = Path(input_path(path)).resolve()
                _require(resolved in mapped and resolved != path and resolved.is_file(),
                         'proof dependency does not map into the verified snapshot')


def configuration_items(items, profiles):
    configs = []
    for key in sorted({i['profile_key'] for i in items}):
        p = profiles[key]
        for index, cfg in enumerate(p['profile'].get('configs', [p['profile']['config']])):
            configs.append(dict(job=stable_job(p['profile']['kind'], cfg, 'configuration', index), phase_root=p['phase_root']))
    return configs


def verify_code(commit):
    from .host_a11 import verify_commit
    head = subprocess.run(['git', '-C', str(SIMULATION.parent), 'rev-parse', 'HEAD'],
                          check=True, capture_output=True, text=True).stdout.strip()
    _require(head == commit, 'proof checkout is not at the frozen commit')
    verify_commit(commit)


def qualification_bundle(sources, output):
    """Short, non-registered profiles only, at Y before the proof is frozen.

    Uses qualification_a11's 20 distinct jobs per kind and disjoint short seed
    construction, its executor, comparison, and validate_evidence unchanged.
    """
    from .qualification_a11 import SCHEMA as QSCHEMA
    output = scoped(output)
    _require(not output.exists(), 'qualification plan is frozen')
    by_kind = {}
    for source in sources:
        spec = unseal(read(source['spec']))
        for phase, profile in spec['configuration'].items():
            memory = max([spec.get('memory_estimate_gb', {}).get(phase, .25)] +
                         [resource_estimate(spec, j)['memory_gb'] for j in spec['jobs']
                          if j['config'].get('phase', j['kind']) == phase])
            for cfg in profile.get('configs', [profile['config']]):
                by_kind.setdefault(profile['kind'], []).append((dict(cfg, phase=phase), source['root'], memory))
    jobs, items, roots, estimates = [], [], {}, {}
    for kind in sorted(by_kind):
        configs = sorted(by_kind[kind], key=lambda c: digest(['A11-qualification-short', c[0]]))
        for index in range(max(20, len(configs))):
            cfg, root, memory = configs[index % len(configs)]
            cfg = deepcopy(cfg)
            if kind.startswith(('a4_', 'a5_', 'a13_')):
                cfg['seed'] = (1 << 128) | int(digest(['A11-qualification-stream', kind, cfg, index])[:32], 16)
            job = stable_job(kind, cfg, 'validation', index)
            jobs.append(job)
            roots[job['id']] = str(Path(root).resolve() / cfg['phase'])
            estimates[job['id']] = memory
            items.append(dict(job=job, phase_root=roots[job['id']]))
    _require(jobs, 'no qualification profiles')
    snapshot = portable_inventory(items)
    bundle = output.parent / (output.stem + '_files')
    plan = dict(schema=QSCHEMA + '-plan', non_registered=True, code_hash=code_identity(), jobs=jobs,
                kinds=sorted(by_kind), phase_roots=roots, inputs=snapshot, references={},
                bundle_directory=bundle.name, memory_estimate_gb=estimates,
                selection='A11 deterministic short configuration profiles, at least 20 per kind',
                comparison='A11 canonical job plus result')
    stage_inputs(snapshot, bundle)
    write_once(output, seal(plan))
    return plan


def validate_hosts(hosts, code, items, original):
    from .qualification_a11 import validate_evidence
    from .production_runner import caps
    _require(hosts and original in hosts, 'missing original proof host')
    for name, entry in hosts.items():
        _require(name and name.replace('-', '').replace('_', '').replace('.', '').isalnum(), 'unsafe host name')
        evidence = validate_evidence(entry['qualification'], code)
        _require(entry.get('qualification_plan_sha256') == evidence['plan']['sha256'],
                 'qualification bundle plan hash is required and must match')
        _require(evidence['candidate']['host'] == name, 'qualification host mismatch')
        _require(evidence['reference']['host'].lower() == original.lower() == 'yotko-evo-x2',
                 'proof qualification must use X2-1 as reference')
        settings = entry['settings']
        _require(settings == evidence['candidate']['settings'], 'qualification settings mismatch')
        _require(settings['threads'] == 1 and settings['mode'] == 'work'
                 and type(settings['workers']) is int and settings['workers'] > 0, 'invalid proof settings')
        entry['worker_cap'] = min(settings['workers'], caps(settings['profile'], settings['cpu_budget'])['work'])
        entry['relative_throughput'] = evidence['relative_throughput']
        entry['memory_gb'] = evidence['candidate']['memory_gb']
        entry['fingerprint'] = evidence['candidate']['fingerprint']
        floor = entry.setdefault('memory_floor_gb', 0.)
        _require(type(floor) in (int, float) and math.isfinite(floor) and floor >= 0, 'invalid observed memory floor')
    assignments = assign(items, hosts)
    for name, ids in assignments.items():
        kinds = {items[j]['job']['kind'] for j in ids}
        evidence = unseal(hosts[name]['qualification'])
        _require(kinds <= set(evidence['kinds']), 'qualification lacks proof kind coverage')
        _require(all(sum(p['kind'] == kind and p['passed'] is True for p in evidence['proofs']) >= 20 for kind in kinds),
                 'qualification requires at least 20 matching jobs per assigned kind')
    return assignments


def freeze(sources, reasons, target, hosts, commit):
    target = scoped(target)
    attempt = target.with_suffix('.attempt.json')
    _require(not target.exists() and not attempt.exists(), 'compatibility attempt is final; selection already exists')
    verify_code(commit)
    record, items, profiles = collect_record(sources, reasons)
    _require(not reservation_path(record).exists(), 'identity pair already reserved; compatibility attempt is final')
    hosts = deepcopy(hosts)
    original = platform.node()
    assignments = validate_hosts(hosts, record['new_code_hash'], items, original)
    _require(all(i['profile_key'] in profiles for i in items.values()), 'missing pre-launch configuration profile')
    snapshots = {}
    for name, ids in assignments.items():
        configs = configuration_items([items[j] for j in ids], profiles)
        snapshots[name] = dict(proof=portable_inventory([items[j] for j in ids]), configuration=portable_inventory(configs))
    payload = dict(schema=SCHEMA, record=record, items=items, profiles=profiles, selected_job_ids=_selected(record['populations']),
                   assignments=assignments, hosts=hosts, original_host=original, code_commit=commit,
                   new_code_hash=record['new_code_hash'], target=str(target), snapshots=snapshots,
                   attempt_path=attempt.relative_to(SIMULATION).as_posix())
    reserve_attempt(record, payload, attempt)
    write_once(attempt, seal(payload))
    return payload


def load_attempt(path):
    p = unseal(read(path))
    _require(p['schema'] == SCHEMA and p['new_code_hash'] == code_identity() == p['record']['new_code_hash'], 'proof identity mismatch')
    _require(Path(path).resolve() == scoped(SIMULATION / p['attempt_path']), 'frozen compatibility attempt location changed')
    verify_code(p['code_commit'])
    expected = _selected(p['record']['populations'])
    assigned = [j for ids in p['assignments'].values() for j in ids]
    _require(p['selected_job_ids'] == expected and set(p['items']) == set(expected)
             and len(assigned) == len(expected) and set(assigned) == set(expected), 'shards do not partition frozen selection')
    verified_hosts = deepcopy(p['hosts'])
    _require(validate_hosts(verified_hosts, p['new_code_hash'], p['items'], p['original_host']) == p['assignments']
             and verified_hosts == p['hosts'], 'frozen shard assignment or host measurements changed')
    _require(p['record']['new_source_manifest'] == source_manifest(), 'frozen source manifest changed')
    check_reservation(p['record'], p, path)
    return p


def host_directory(path, host):
    return scoped(Path(path).parent / (Path(path).stem + '_shards') / host)


def stage(path, host):
    p = load_attempt(path)
    _require(platform.node() == p['original_host'], 'stage on the original host')
    _require(host in p['hosts'], 'foreign shard host')
    root = host_directory(path, host)
    for kind, snapshot in p['snapshots'][host].items():
        stage_inputs(snapshot, root / (kind + '_files'))
    return root


def configure_host(p, host, root, budget, view):
    from .production_runner import configuration_candidates, configuration_job_count, choose, caps
    entry = p['hosts'][host]
    settings = entry['settings']
    configured = {}
    for key in sorted({p['items'][j]['profile_key'] for j in p['assignments'][host]}):
        info = p['profiles'][key]
        profile = info['profile']
        memory = max(entry['memory_floor_gb'], max(i['resources']['memory_gb'] for i in p['items'].values() if i['profile_key'] == key))
        requested = worker_cap(settings)
        cap = min(caps(settings['profile'], settings['cpu_budget'])[settings['mode']], int(budget / memory))
        _require(cap >= 1, 'configuration job exceeds memory budget')
        listed = profile['workers_x2' if settings['profile'] == 'x2' else 'workers_local']
        if settings['profile'] == 'x2':
            _require({8, 12, 16, 24, 32} <= set(listed), 'missing required X2 configuration candidates')
        # Cover the usable mode cap, including it when absent from the profile.
        candidates = sorted(set(configuration_candidates(listed, cap)) | {cap, min(requested, cap)})
        measurements, observed = [], memory
        for round_index in range(profile.get('rounds', 2)):
            for count in candidates if round_index % 2 == 0 else reversed(candidates):
                if count > cap:
                    continue
                count = min(count, int(budget / observed))
                _require(count >= 1, 'observed configuration memory exceeds host budget')
                number = configuration_job_count(profile, count, settings['profile'] == 'x2')
                _require(number >= count, 'configuration work must occupy every tested worker')
                configs = profile.get('configs', [profile['config']])
                tasks = []
                for index in range(number):
                    # fixture is the runner's explicitly non-scientific test kind.
                    tag = 'validation' if profile['kind'] == 'fixture' else 'configuration'
                    job = stable_job(profile['kind'], configs[index % len(configs)], tag, round_index * number + index)
                    tasks.append(dict(job=job, phase_root=info['phase_root'], producing_code_hash=info['producing_code_hash'],
                                      input_view=view, resources=dict(worker_seconds=1., memory_gb=memory, memory_class=key)))
                before = time.perf_counter()
                results, trace = run_items(tasks, count, budget, memory_floor_gb=observed,
                                           idle_wait_seconds=MEMORY_WAIT_SECONDS)
                observed = max(observed, *(1.2 * (r.get('_peak_rss_bytes') or 0) / 1e9 for r in results.values()))
                valid = all(r['after_sha256'] is not None for r in results.values())
                measurements.append(dict(workers=count, threads=1, completed=len(results), valid=valid, round=round_index,
                    wall_seconds=time.perf_counter() - before, job_seconds=[r.get('_worker_seconds', 0) for r in results.values()], admission=trace))
                atomic_json(root / 'configuration' / (key + '.json'), seal(measurements))
                _require(valid, 'configuration test failed before proof start; shard remains retryable')
        configured[key] = dict(measurements=measurements, observed_memory_gb=observed,
                               chosen=choose(measurements, min(requested, cap), settings['cpu_budget'], 1))
    return configured


def preflight(p, host, root):
    entry = p['hosts'][host]
    items = [p['items'][j] for j in p['assignments'][host]]
    views = {kind: receive_inputs(snapshot, root / (kind + '_files'), root / (kind + '_snapshot'))
             for kind, snapshot in p['snapshots'][host].items()}
    check_input_paths(items, views['proof'])
    check_input_paths(configuration_items(items, p['profiles']), views['configuration'])
    required = max(entry['memory_floor_gb'], *(i['resources']['memory_gb'] for i in items))
    budget = wait_for_memory(required, entry.get('memory_gb'))
    configuration = configure_host(p, host, root, budget, views['configuration'])
    floor = max(entry['memory_floor_gb'], *(c['observed_memory_gb'] for c in configuration.values()))
    budget = min(budget, wait_for_memory(max(required, floor), entry.get('memory_gb')))
    return views, configuration, floor, budget


def single_preflight(record, items, profiles, target, workers, floor):
    """The legacy one-host API has the same preconditions before reservation."""
    from .production_runner import available_cpus
    profiles = deepcopy(profiles)
    for item in items.values():
        if item['profile_key'] not in profiles:
            _require(item['job']['kind'] == 'fixture', 'missing pre-launch configuration profile')
            profiles[item['profile_key']] = dict(phase_root=item['phase_root'],
                producing_code_hash=item['producing_code_hash'], profile=dict(kind='fixture',
                    config=dict(seconds=.001), workers_local=[1, 2], rounds=1, jobs_per_worker=1))
    settings = dict(profile='local', workers=workers, cpu_budget=min(16, available_cpus()), threads=1, mode='work')
    name = platform.node()
    p = dict(items=items, profiles=profiles, assignments={name: list(items)},
             hosts={name: dict(settings=settings, memory_floor_gb=floor)}, snapshots={name: dict(
                 proof=portable_inventory(list(items.values())),
                 configuration=portable_inventory(configuration_items(list(items.values()), profiles)))})
    root = target.with_suffix('.preflight')
    for kind, snapshot in p['snapshots'][name].items():
        stage_inputs(snapshot, root / (kind + '_files'))
    views, configuration, floor, budget = preflight(p, name, root)
    _require(source_manifest() == record['new_source_manifest'], 'source changed during preflight')
    # Preserve the legacy caller's worker cap; live memory admission may use
    # fewer slots. Configuration remains a prerequisite, not a new API default.
    return views['proof'], configuration, floor, budget, workers


def run_shard(path, host):
    from .host_a11 import fingerprint
    p = load_attempt(path)
    _require(host in p['hosts'] and platform.node() == host, 'shard must run on its recorded host')
    entry = p['hosts'][host]
    root = host_directory(path, host)
    result_path = root / 'result.json'
    _require(not result_path.exists() and not (root / 'started.json').exists(), 'shard attempt is final')
    before = dict(attempt_sha256=digest(p), host=host, passed=False, memory_wait_seconds=MEMORY_WAIT_SECONDS)
    try:
        environment = fingerprint()
        _require(environment == entry['fingerprint'], 'qualified host fingerprint changed')
        cap = worker_cap(entry['settings'])
        views, configuration, floor, budget = preflight(p, host, root)
        # Recheck the binding and code after repeatable configuration work.
        load_attempt(path)
        _require(fingerprint() == environment, 'qualified host fingerprint changed during preflight')
        before.update(passed=True, memory_budget_gb=budget, configuration=configuration)
    except BaseException as exc:
        before['error'] = type(exc).__name__ + ': ' + str(exc)
        raise
    finally:
        atomic_json(root / 'preflight.json', seal(before))
    started = time.time()
    write_once(root / 'started.json', seal(dict(attempt_sha256=digest(p), host=host, started_epoch=started,
                                               preflight_sha256=digest(before))))
    result = dict(schema=SCHEMA + '-result', attempt_sha256=digest(p), host=host, fingerprint=environment,
                  code_commit=p['code_commit'], code_hash=p['new_code_hash'], job_ids=p['assignments'][host],
                  started_epoch=started, memory_budget_gb=budget, passed=False, proofs=[])
    try:
        result['configuration'] = configuration
        # One process pool shares the most conservative measured count across
        # mixed phases. LPT still uses each original job's registered class.
        workers = min(cap, *(c['chosen']['workers'] for c in configuration.values()))
        tasks = [dict(p['items'][j], input_view=views['proof']) for j in p['assignments'][host]]
        fresh, trace = run_items(tasks, workers, budget, memory_floor_gb=floor)
        result.update(workers=workers, admission=trace,
                      proofs=[proof_row(p['items'][j], fresh[j]) for j in p['assignments'][host]])
        _require(source_manifest() == p['record']['new_source_manifest'], 'source changed during shard')
        verify_code(p['code_commit'])
        result['passed'] = all(r['passed'] for r in result['proofs'])
    except BaseException as exc:
        result['error'] = type(exc).__name__ + ': ' + str(exc)
        raise
    finally:
        result['finished_epoch'] = time.time()
        result['x2_equivalent_hours'] = (result['finished_epoch'] - started) * entry['relative_throughput'] / 3600
        atomic_json(result_path, seal(result))
    return result


def combine_inputs(path, p, shard_paths=None):
    """Read the exact frozen locations before any combine write, including a lock.

    Optional caller paths only cross-check this inventory. Transfer/argument
    errors leave no binding or final record, so the same files can be restored.
    """
    expected = {host: host_directory(path, host) / 'result.json' for host in p['hosts']}
    paths = sorted(str(result) for result in expected.values())
    if shard_paths is not None:
        supplied = sorted(str(scoped(s)) for s in shard_paths)
        _require(supplied == paths, 'shard path cross-check differs from frozen attempt')
    required = {result for result in expected.values()} | {result.with_name('started.json') for result in expected.values()}
    root = scoped(path).parent / (Path(path).stem + '_shards')
    found = {f for f in root.rglob('*.json') if f.name in ('result.json', 'started.json')}
    # Also refuse stray JSON copies beside the records, while permitting the
    # documented preflight record and configuration/input subdirectories.
    found.update(f for f in root.glob('*/*.json') if f.name != 'preflight.json')
    _require(found == required and all(f.is_file() for f in required),
             'missing, duplicate or extra shard result/start files')
    files, documents = {}, {}
    for f in sorted(required):
        raw = f.read_bytes()
        documents[str(f)] = unseal(json.loads(raw))
        files[str(f)] = hashlib.sha256(raw).hexdigest()
    return dict(shard_paths=paths, files=files), documents


def combine(path, shard_paths=None):
    from .artifacts import lease
    p = load_attempt(path)
    _require(platform.node() == p['original_host'], 'combine on the original host')
    _require(not scoped(p['target']).exists(), 'compatibility attempt is final; target already exists')
    combine_inputs(path, p, shard_paths)
    with lease(scoped(p['target']).with_suffix('.combine.lock')):
        return _combine(path, p, shard_paths)


def _combine(path, p, shard_paths):
    target = scoped(p['target'])
    _require(not target.exists(), 'compatibility attempt is final; target already exists')
    inputs, documents = combine_inputs(path, p, shard_paths)
    binding = dict(attempt_sha256=digest(p), **inputs)
    marker = target.with_suffix('.combine.json')
    if marker.exists():
        _require(unseal(read(marker)) == binding, 'combine inputs changed; only the frozen shard files may be retried')
    else:
        # The combine lease serializes creation. Atomic replacement means a
        # crash cannot leave a partially written binding that blocks recovery.
        atomic_json(marker, seal(binding))
    record = deepcopy(p['record'])
    record['execution'].update(code_commit=p['code_commit'], attempt_sha256=digest(p), shards=[], combine_inputs=inputs)
    try:
        shards = [documents[name] for name in inputs['shard_paths']]
        proofs = {}
        for host in sorted(p['hosts']):
            result_path = host_directory(path, host) / 'result.json'
            start_path = result_path.with_name('started.json')
            shard, start = documents[str(result_path)], documents[str(start_path)]
            _require(isinstance(shard, dict) and isinstance(start, dict), 'invalid shard record content')
            _require(shard.get('host') == host, 'missing, duplicate or foreign shard host')
            _require(start.get('attempt_sha256') == digest(p) and start.get('host') == host
                     and start.get('started_epoch') == shard['started_epoch'], 'shard start record mismatch')
            _require(shard['schema'] == SCHEMA + '-result' and shard['attempt_sha256'] == digest(p), 'foreign shard attempt')
            _require(shard['code_commit'] == p['code_commit'] and shard['code_hash'] == p['new_code_hash'], 'shard code mismatch')
            _require(shard['fingerprint'] == p['hosts'][host]['fingerprint'], 'shard fingerprint mismatch')
            ids = p['assignments'][host]
            _require(shard['job_ids'] == ids and [r['job_id'] for r in shard['proofs']] == ids, 'shard job partition mismatch')
            _require(shard.get('configuration') and shard.get('finished_epoch', 0) >= shard['started_epoch'], 'incomplete shard')
            for row in shard['proofs']:
                item = p['items'][row['job_id']]
                _require(row['job_sha256'] == digest(item['job']) and row['before_sha256'] == item['before_sha256']
                         and row['source_output_sha256'] == item['output_file_sha256'], 'shard changed original comparison')
                _require(row['job_id'] not in proofs, 'duplicate proof job')
                _require(row['passed'] == (row['before_sha256'] == row['after_sha256']), 'shard pass flag mismatch')
                proofs[row['job_id']] = row
            _require(shard['passed'] is True and all(r['passed'] for r in shard['proofs']), 'failed shard is final')
            record['execution']['shards'].append(dict(host=host, result_sha256=digest(shard),
                started_file_sha256=inputs['files'][str(start_path)],
                result_file_sha256=inputs['files'][str(start_path.with_name('result.json'))],
                qualification_sha256=p['hosts'][host]['qualification']['sha256'],
                fingerprint=shard['fingerprint'], started_epoch=shard['started_epoch'], finished_epoch=shard['finished_epoch'],
                x2_equivalent_hours=shard['x2_equivalent_hours']))
        record['proofs'] = [proofs[j] for j in p['selected_job_ids']]
        record['execution']['workers'] = sum(shard['workers'] for shard in shards)
        record['passed'] = True
    except (ValueError, KeyError, TypeError) as exc:
        record['passed'] = False
        record['error'] = type(exc).__name__ + ': ' + str(exc)
        atomic_json(target, seal(record))
        raise
    # An infrastructure interruption before this atomic write can be retried
    # with the identical bound files. No timestamps are recomputed here.
    _require(combine_inputs(path, p, shard_paths)[0] == inputs, 'shard files changed during combine')
    atomic_json(target, seal(record))
    return record


def project(sources, hosts):
    """Scheduling-only projection before freezing; reads specs, never results.

    Uses conservative full-job memory slots, so the projection is conditional
    on each host's subsequent configuration test selecting that count.
    """
    grouped, items = {}, {}
    for source in sources:
        spec = unseal(read(source['spec']))
        for job in spec['jobs']:
            _require(job['id'] not in items, 'duplicate source job')
            grouped.setdefault(_stratum(job), []).append(job['id'])
            items[job['id']] = dict(job=job, resources=resource_estimate(spec, job))
    populations = [dict(phase=p, capability=c, setting=t, job_ids=sorted(ids)) for (p, c, t), ids in sorted(grouped.items())]
    items = {j: items[j] for j in _selected(populations)}
    hosts = deepcopy(hosts)
    assignments = validate_hosts(hosts, code_identity(), items, platform.node())
    import heapq
    times, slots = {}, {}
    for name, ids in assignments.items():
        h = hosts[name]
        memory = max(max(i['resources']['memory_gb'], h['memory_floor_gb']) for i in items.values())
        slots[name] = min(h['worker_cap'], int(.8 * h['memory_gb'] / memory))
        free = [0.] * slots[name]
        for jid in ids:  # assign() has already ordered each shard by registered cost.
            start = heapq.heappop(free)
            heapq.heappush(free, start + items[jid]['resources']['worker_seconds'] / h['relative_throughput'])
        times[name] = max(free)
    return dict(selected_jobs=len(items), selection_sha256=digest(list(items)), assignment_sha256=digest(assignments),
                registered_worker_hours=sum(i['resources']['worker_seconds'] for i in items.values()) / 3600,
                wall_hours=max(times.values()) / 3600,
                x2_equivalent_hours=sum(times[h] * hosts[h]['relative_throughput'] for h in times) / 3600,
                relative_throughputs={h: e['relative_throughput'] for h, e in hosts.items()},
                conditional_worker_counts=slots, condition='configuration test selects these counts; overhead excluded')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    q = sub.add_parser('qualification'); q.add_argument('--sources', required=True); q.add_argument('--output', required=True)
    f = sub.add_parser('freeze'); f.add_argument('--sources', required=True); f.add_argument('--reasons', required=True)
    f.add_argument('--output', required=True); f.add_argument('--hosts', required=True); f.add_argument('--commit', required=True)
    f = sub.add_parser('project'); f.add_argument('--sources', required=True); f.add_argument('--hosts', required=True)
    f.add_argument('--output', required=True)
    for command in ('stage', 'run'):
        s = sub.add_parser(command); s.add_argument('attempt'); s.add_argument('--host', required=True)
    c = sub.add_parser('combine'); c.add_argument('attempt')
    c.add_argument('--shard', action='append', help='optional exact cross-check of frozen result paths')
    args = parser.parse_args()
    if args.command == 'qualification':
        result = qualification_bundle(read(args.sources), args.output)
        print(dict(jobs=len(result['jobs']), kinds=result['kinds'], plan_sha256=digest(result)))
    elif args.command in ('freeze', 'project'):
        hosts = read(args.hosts)
        for entry in hosts.values():
            entry['qualification'] = read(entry['qualification'])
        if args.command == 'project':
            result = project(read(args.sources), hosts)
            write_once(args.output, seal(result))
            print(result)
        else:
            result = freeze(read(args.sources), args.reasons, args.output, hosts, args.commit)
            print(dict(selected=len(result['selected_job_ids']), attempt_sha256=digest(result)))
    elif args.command == 'stage':
        print(str(stage(args.attempt, args.host)))
    elif args.command == 'run':
        result = run_shard(args.attempt, args.host)
        print(dict(passed=result['passed'], jobs=len(result['proofs']), x2_equivalent_hours=result['x2_equivalent_hours']))
        return 0 if result['passed'] else 1
    else:
        result = combine(args.attempt, args.shard)
        print(dict(passed=result['passed'], jobs=len(result['proofs'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
