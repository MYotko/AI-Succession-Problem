"""Executor-only A11 proof shards. Signal retries preserve every job and comparison.

The original host freezes the one attempt after qualification. Each host runs
its shard once after preflight; an interrupted proof spends it. Only comparison hashes
return. Scheduling metadata never enters a job or comparison_bytes().
"""
import argparse
import base64
from concurrent.futures import wait, FIRST_COMPLETED
from copy import deepcopy
import hashlib
import json
import math
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

from . import worker_control as wc
from .worker_safety import metadata_json, persist_restarts

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


def memory_budget(limit_gb=None, headroom=.8):
    # production_runner.memory_worker_cap and multihost_a11.Coordinator.claim:
    # 80% of available memory, bounded by the host's qualified memory.
    from .production_runner import mem_available_bytes
    available = mem_available_bytes()
    _require(available is not None and available > 0, 'proof needs measured available memory')
    if limit_gb is not None:
        _require(positive(limit_gb), 'invalid qualified memory')
    _require(positive(headroom) and headroom <= .95, "invalid memory headroom")
    return headroom * min(available / 1e9, limit_gb if limit_gb is not None else math.inf)


def wait_for_memory(required, limit_gb=None, *, timeout=MEMORY_WAIT_SECONDS, headroom=.8):
    """Bound the idle wait separately for repeatable setup and final proof work."""
    _require(positive(required), 'invalid required memory')
    _require(positive(timeout), 'invalid memory wait bound')
    _require(limit_gb is None or required <= headroom * limit_gb, 'proof job exceeds qualified memory budget')
    deadline = time.monotonic() + timeout
    while True:
        budget = memory_budget(limit_gb, headroom)
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
        resource = wc.resources(spec, [job])[job['id']]
        seconds, memory = cls['worker_seconds'], wc.reservation(resource, {})
        _require(positive(seconds) and positive(memory), 'invalid registered cost class')
    else:
        _require(not spec.get('registered'), 'registered proof needs its registered cost classes')
        resource = wc.resources(spec, [job])[job['id']]
        key, seconds, memory = resource['memory_class'], 1., wc.reservation(resource, {})
    _require(positive(memory), 'invalid phase memory estimate')
    return dict(worker_seconds=seconds, memory_gb=memory, planning_memory_gb=resource['memory_gb'],
                memory_known=resource['memory_known'], memory_class=digest([spec['code_hash'], pull.get('projection_sha256') if pull else None, key]))


def worker_cap(settings):
    _require(settings['threads'] == 1 and settings['mode'] in ('work', 'normal'), 'proof requires one thread and normal or work mode')
    return wc.selection(wc.settings(settings, local=False))['workers']



def informational_status(path, value):
    """Status is not proof evidence. At most two attempts, never spend a round."""
    return metadata_json(path, value, writer=atomic_json)

def run_items(items, workers, budget, *, memory_floor_gb=0., idle_wait_seconds=PROOF_MEMORY_WAIT_SECONDS, control_path=None, host_settings=None, class_peaks=None, headroom=.8, fixed_workers=None, measurements_by_profile=None):
    """Longest fitting job first; only absent results after signal death retry.

    Registered estimates plus each class's own measured peak are reservations.
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
        estimates[r['memory_class']] = max(estimates.get(r['memory_class'], 0), r['memory_gb'], (class_peaks or {}).get(r['memory_class'], 0.))
    _require(wc.top_weighted(estimates[i['resources']['memory_class']] for i in pending) <= budget, 'proof job exceeds host memory budget')
    active, results, trace, idle_since = {}, {}, [], None
    next_status = 0.
    authority_peaks = {i['resources']['memory_class']: i['resources'].get('measured_memory_gb', 0.) for i in items}
    for key, value in (class_peaks or {}).items():
        authority_peaks[key] = max(authority_peaks.get(key, 0.), value)
    configure_threads(1)
    from .worker_safety import IsolatedPools, KilledWorker, restart, require_retry_budget
    journal = (Path(control_path).parent if control_path else ROOT / '_proof_worker_metadata') / 'worker_metadata'
    events_path = journal / 'restarts.json'
    events = read(events_path) if events_path.exists() else []
    with IsolatedPools(journal / 'returns') as pool:
        while pending or active:
            if control_path is not None:
                control = read(control_path)
                selected = wc.selection(host_settings, control, fixed=dict(workers=fixed_workers, threads=1) if fixed_workers else None)
                workers = wc.memory_safe_selection(host_settings, control,
                    {i['job']['id']: i['resources'] for i in items}, authority_peaks, selected,
                    configuration_trial=fixed_workers is not None and all(i['job']['tag'] == 'configuration' for i in items))['workers']
            unfinished = pending + [i for i, _ in active.values()]
            weight = wc.top_weighted(estimates[i['resources']['memory_class']] for i in unfinished)
            def charge(item): return min(estimates[item['resources']['memory_class']], weight)
            occupied = sum(charge(i) for i, _ in active.values())
            while len(active) < workers and pending:
                free = min(budget - occupied, memory_budget(None, headroom))
                index = next((i for i, item in enumerate(pending)
                              if charge(item) <= free and (not measurements_by_profile or wc.profile_slots(
                                  host_settings, control if control_path else None, item['profile_key'],
                                  [i['profile_key'] for i, _ in active.values()],
                                  measurements_by_profile.get(item['profile_key'], {}).get('measurements')) > 0)), None)
                if index is None:
                    break
                item = pending.pop(index)
                require_retry_budget(events, item['job']['id'])
                needed = charge(item)
                active[pool.submit(_execute_proof, item)] = (item, needed)
                occupied += needed
                trace.append(dict(job_id=item['job']['id'], reserved_gb=needed,
                                  running_gb=occupied, running=len(active), budget_gb=budget, top_weighted_gb=weight))
            if control_path is not None and time.monotonic() >= next_status:
                informational_status(Path(control_path).with_name('scheduling.json'), dict(target=workers, running=len(active),
                    pending=len(pending), active_job_ids=[i['job']['id'] for i, _ in active.values()]))
                next_status = time.monotonic() + 1.
            if not active and pending:
                if workers == 0:
                    idle_since = None
                    time.sleep(.1)
                    continue
                required = min(charge(i) for i in pending)
                _require(required <= budget, 'observed proof memory exceeds frozen budget; attempt spent')
                if idle_since is None: idle_since = time.monotonic()
                _require(time.monotonic() - idle_since < idle_wait_seconds,
                         f'memory not released within {idle_wait_seconds:g} seconds')
                time.sleep(1.)
                continue
            idle_since = None
            if not active:
                break
            finished, _ = wait(active, timeout=.1, return_when=FIRST_COMPLETED)
            for future in finished:
                item, _ = active.pop(future)
                try:
                    result = pool.result(future)
                except KilledWorker as exc:
                    event = restart(events, item['job']['id'], exc.signal)
                    persist_restarts(journal / 'restarts.json', events)
                    _require(event['allowed'], 'worker exhausted three signal reruns')
                    pending.append(item)
                    pending.sort(key=lambda x: (-x['resources']['worker_seconds'], x['job']['id']))
                    continue
                results[item['job']['id']] = result
                peak = result.get('_peak_rss_bytes')
                if peak:
                    key = item['resources']['memory_class']
                    estimates[key] = max(estimates[key], 1.2 * peak / 1e9)
                    authority_peaks[key] = max(authority_peaks.get(key, 0.), 1.2 * peak / 1e9)
                    if class_peaks is not None: class_peaks[key] = max(class_peaks.get(key, 0.), 1.2 * peak / 1e9)
    if control_path is not None:
        informational_status(Path(control_path).with_name('scheduling.json'),
                             dict(target=workers, running=0, pending=0, active_job_ids=[]))
    return results, trace


def assign(items, hosts):
    """Deterministic LPT to least projected finish, cost / measured host rate.

    Packing uses each class reservation with the unfinished top-quarter charge.
    Runtime controls affect dispatch only and never change this partition.
    """
    shards = {h: [] for h in hosts}
    for jid in sorted(items, key=lambda j: (-items[j]['resources']['worker_seconds'], j)):
        projections = {}
        for h, entry in hosts.items():
            rows = [dict(key=j, seconds=items[j]['resources']['worker_seconds'], memory=items[j]['resources']['memory_gb'])
                    for j in shards[h] + [jid]]
            wall, _ = wc.packed_wall(rows, entry['worker_cap'],
                entry['settings'].get('memory_headroom', .8) * entry['memory_gb'] if 'settings' in entry else .8 * entry['memory_gb'],
                entry.get('per_job_relative_throughput', entry['relative_throughput']))
            projections[h] = wall if wall is not None else math.inf
        h = min(hosts, key=lambda name: (projections[name], name))
        _require(math.isfinite(projections[h]), 'host cannot admit a proof job')
        shards[h].append(jid)
    _require(all(shards.values()), 'empty proof shard')
    return shards


def source_historical_roots(sources):
    """Explicit input roots, frozen into the proof/qualification snapshots."""
    from .snapshot_a11 import historical_roots, normalize_historical_roots
    roots = set()
    for source in sources:
        roots.update(historical_roots(unseal(read(source['spec']))))
        roots.update(normalize_historical_roots(source.get('historical_roots', [])))
    return sorted(roots)


def portable_inventory(items, *, historical_roots=()):
    """Same execute dependencies as snapshot_a11, including old-checkout reads.

    Blob paths are local and safe; absolute aliases preserve original job bytes.
    No source output is copied unless execute needs it (e.g. A4's A1 and fit).
    """
    from .snapshot_a11 import dependencies, normalize_historical_roots, verify_historical_scope
    roots = normalize_historical_roots(historical_roots)
    files = {}
    for item in items:
        for path in dependencies([item['job']], item['phase_root']):
            _require(path.is_relative_to(ROOT) or any(path.is_relative_to(Path(r)) for r in roots),
                     'proof input outside declared historical roots')
            key = digest(str(path))
            files[key] = dict(path='v3/proof_inputs/' + key + '/' + path.name,
                              source=str(path), aliases=[str(path)], sha256=file_hash(path), bytes=path.stat().st_size)
    payload = dict(schema='v3-A11-inputs-1', simulation=str(SIMULATION), files=[files[k] for k in sorted(files)])
    if roots:
        payload.update(historical_roots=roots, historical_roots_sha256=digest(roots), checkout_root=str(ROOT))
    verify_historical_scope(payload)
    return seal(payload)


def stage_inputs(document, bundle):
    from .snapshot_a11 import verify_historical_scope
    payload = unseal(document)
    verify_historical_scope(payload)
    for row in payload['files']:
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
            for cfg in profile.get('configs', [profile['config']]):
                prototype = stable_job(profile['kind'], dict(cfg, phase=phase), 'configuration', 0)
                resource = wc.trial_resources([prototype])[prototype['id']]
                by_kind.setdefault(profile['kind'], []).append((dict(cfg, phase=phase), source['root'], resource))
    jobs, items, roots, estimates, memory_classes, memory_known = [], [], {}, {}, {}, {}
    for kind in sorted(by_kind):
        configs = sorted(by_kind[kind], key=lambda c: digest(['A11-qualification-short', c[0]]))
        for index in range(max(20, len(configs))):
            cfg, root, resource = configs[index % len(configs)]
            cfg = deepcopy(cfg)
            if kind.startswith(('a4_', 'a5_', 'a13_')):
                cfg['seed'] = (1 << 128) | int(digest(['A11-qualification-stream', kind, cfg, index])[:32], 16)
            job = stable_job(kind, cfg, 'validation', index)
            jobs.append(job)
            roots[job['id']] = str(Path(root).resolve() / cfg['phase'])
            estimates[job['id']] = wc.reservation(resource, {})
            memory_known[job['id']] = resource['memory_known']
            memory_classes[job['id']] = resource['memory_class']
            items.append(dict(job=job, phase_root=roots[job['id']]))
    _require(jobs, 'no qualification profiles')
    snapshot = portable_inventory(items, historical_roots=source_historical_roots(sources))
    bundle = output.parent / (output.stem + '_files')
    plan = dict(schema=QSCHEMA + '-plan', non_registered=True, code_hash=code_identity(), jobs=jobs,
                kinds=sorted(by_kind), phase_roots=roots, inputs=snapshot, references={},
                bundle_directory=bundle.name, memory_estimate_gb=estimates, memory_classes=memory_classes,
                memory_estimate_known=memory_known,
                selection='A11 deterministic short configuration profiles, at least 20 per kind',
                comparison='A11 canonical job plus result')
    stage_inputs(snapshot, bundle)
    write_once(output, seal(plan))
    return plan


def validate_hosts(hosts, code, items, original):
    from .qualification_a11 import validate_evidence, scheduling_rate
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
        _require(settings['threads'] == 1 and settings['mode'] in ('work', 'normal')
                 and type(settings['workers']) is int and settings['workers'] > 0, 'invalid proof settings')
        entry['worker_cap'] = worker_cap(settings)
        entry['relative_throughput'] = evidence['relative_throughput']
        entry['per_job_relative_throughput'] = scheduling_rate(evidence)
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
    roots = source_historical_roots(sources)
    for name, ids in assignments.items():
        configs = configuration_items([items[j] for j in ids], profiles)
        snapshots[name] = dict(proof=portable_inventory([items[j] for j in ids], historical_roots=roots),
                               configuration=portable_inventory(configs, historical_roots=roots))
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
        sources = [i['job'] for i in p['items'].values() if i['profile_key'] == key]
        resources = {i['job']['id']: dict(i['resources'], estimated_seconds=i['resources']['worker_seconds']) for i in p['items'].values()}
        requested = worker_cap(settings)
        cap = caps(settings['profile'], settings['cpu_budget'])[settings['mode']]
        _require(cap >= 1, 'configuration job exceeds memory budget')
        listed = profile['workers_x2' if settings['profile'] == 'x2' else 'workers_local']
        if settings['profile'] == 'x2':
            _require({8, 12, 16, 24, 32} <= set(listed), 'missing required X2 configuration candidates')
        # Fixed-size sealed profiles cannot fill more slots than their jobs.
        cap = min(cap, configuration_job_count(profile, cap, settings['profile'] == 'x2'))
        # Test through the usable CPU cap, with short-trial memory measurements.
        candidates = sorted(set(configuration_candidates(listed, cap)) | {cap, min(requested, cap)})
        measurements, peaks = [], {}
        for round_index in range(profile.get('rounds', 2)):
            for count in candidates if round_index % 2 == 0 else reversed(candidates):
                if count > cap:
                    continue
                number = configuration_job_count(profile, count, settings['profile'] == 'x2')
                _require(number >= count, 'configuration work must occupy every tested worker')
                configs = profile.get('configs', [profile['config']])
                tasks = []
                for index in range(number):
                    # fixture is the runner's explicitly non-scientific test kind.
                    tag = 'validation' if profile['kind'] == 'fixture' else 'configuration'
                    job = stable_job(profile['kind'], configs[index % len(configs)], tag, round_index * number + index)
                    resource = wc.trial_resources([job])[job['id']]
                    tasks.append(dict(job=job, phase_root=info['phase_root'], producing_code_hash=info['producing_code_hash'],
                                      input_view=view, resources=dict(resource, worker_seconds=1.)))
                before = time.perf_counter()
                control_path = root / 'control.json'
                results, trace = run_items(tasks, count, budget, class_peaks=peaks, headroom=settings.get('memory_headroom', .8),
                    control_path=control_path if control_path.exists() else None, host_settings=settings, fixed_workers=count,
                    idle_wait_seconds=MEMORY_WAIT_SECONDS)
                valid = all(r['after_sha256'] is not None for r in results.values())
                measurements.append(dict(workers=max((t['running'] for t in trace), default=count), requested_workers=count, threads=1, completed=len(results), valid=valid, round=round_index,
                    wall_seconds=time.perf_counter() - before, job_seconds=[r.get('_worker_seconds', 0) for r in results.values()], admission=trace))
                metadata_json(root / 'configuration' / (key + '.json'), seal(measurements))
                _require(valid, 'configuration test failed before proof start; shard remains retryable')
        configured[key] = dict(measurements=measurements, class_peaks_gb=peaks,
                               chosen=wc.selection(settings, measurements=measurements))
    return configured


def preflight(p, host, root):
    entry = p['hosts'][host]
    from .worker_safety import swap_preflight
    swap_preflight(entry['settings'], root / 'worker_metadata' / 'swap_preflight.json')
    items = [p['items'][j] for j in p['assignments'][host]]
    views = {kind: receive_inputs(snapshot, root / (kind + '_files'), root / (kind + '_snapshot'))
             for kind, snapshot in p['snapshots'][host].items()}
    check_input_paths(items, views['proof'])
    check_input_paths(configuration_items(items, p['profiles']), views['configuration'])
    control_path = root / 'control.json'
    wc.require_memory_authority(entry['settings'], read(control_path) if control_path.exists() else None,
        {i['job']['id']: i['resources'] for i in items},
        {i['resources']['memory_class']: i['resources'].get('measured_memory_gb', 0.) for i in items})
    required = wc.top_weighted(i['resources']['memory_gb'] for i in items)
    budget = wait_for_memory(required, entry.get('memory_gb'), headroom=entry['settings'].get('memory_headroom', .8))
    configuration = configure_host(p, host, root, budget, views['configuration'])
    peaks = {}
    for cfg in configuration.values():
        for key, value in cfg.get('class_peaks_gb', {}).items(): peaks[key] = max(peaks.get(key, 0.), value)
    required = wc.top_weighted(max(i['resources']['memory_gb'], peaks.get(i['resources']['memory_class'], 0.)) for i in items)
    budget = min(budget, wait_for_memory(required, entry.get('memory_gb'), headroom=entry['settings'].get('memory_headroom', .8)))
    return views, configuration, 0., budget


def single_preflight(record, items, profiles, target, workers, floor, settings=None, historical_roots=()):
    """The legacy one-host API has the same preconditions before reservation."""
    from .production_runner import available_cpus
    profiles = deepcopy(profiles)
    for item in items.values():
        if item['profile_key'] not in profiles:
            _require(item['job']['kind'] == 'fixture', 'missing pre-launch configuration profile')
            profiles[item['profile_key']] = dict(phase_root=item['phase_root'],
                producing_code_hash=item['producing_code_hash'], profile=dict(kind='fixture',
                    config=dict(seconds=.001), workers_local=[1, 2], rounds=1, jobs_per_worker=1))
    settings = settings or dict(profile='local', workers=workers, cpu_budget=min(16, available_cpus()), threads=1, mode='work')
    name = platform.node()
    p = dict(items=items, profiles=profiles, assignments={name: list(items)},
             hosts={name: dict(settings=settings, memory_floor_gb=floor)}, snapshots={name: dict(
                 proof=portable_inventory(list(items.values()), historical_roots=historical_roots),
                 configuration=portable_inventory(configuration_items(list(items.values()), profiles),
                                                  historical_roots=historical_roots))})
    root = target.with_suffix('.workers')
    for kind, snapshot in p['snapshots'][name].items():
        stage_inputs(snapshot, root / (kind + '_files'))
    views, configuration, floor, budget = preflight(p, name, root)
    _require(source_manifest() == record['new_source_manifest'], 'source changed during preflight')
    # Preserve the legacy caller's worker cap; live memory admission may use
    # fewer slots. Configuration remains a prerequisite, not a new API default.
    return views['proof'], configuration, floor, budget, workers


def run_shard(path, host, *, workers=None, override_reason=None, operator=None, memory_headroom=None):
    from .host_a11 import fingerprint
    p = load_attempt(path)
    _require(host in p['hosts'] and platform.node() == host, 'shard must run on its recorded host')
    entry = p['hosts'][host]
    execution = deepcopy(p)
    runtime_settings = dict(entry['settings'])
    if workers is not None and not override_reason:
        raise ValueError('initial proof worker override requires --override-reason')
    if workers is not None: runtime_settings['workers'] = workers
    if override_reason is not None:
        runtime_settings.update(override_reason=override_reason, operator=operator)
        runtime_settings.pop('operator_override', None)
    if memory_headroom is not None: runtime_settings['memory_headroom'] = memory_headroom
    runtime_settings = wc.settings(runtime_settings)
    execution['hosts'][host]['settings'] = runtime_settings
    root = host_directory(path, host)
    control_path = root / 'control.json'
    result_path = root / 'result.json'
    _require(not result_path.exists() and not (root / 'started.json').exists(), 'shard attempt is final')
    wc.initial_control(root, runtime_settings)
    before = dict(attempt_sha256=digest(p), host=host, passed=False, memory_wait_seconds=MEMORY_WAIT_SECONDS)
    try:
        environment = fingerprint()
        _require(environment == entry['fingerprint'], 'qualified host fingerprint changed')
        cap = worker_cap(runtime_settings)
        views, configuration, floor, budget = preflight(execution, host, root)
        # Recheck the binding and code after repeatable configuration work.
        load_attempt(path)
        _require(fingerprint() == environment, 'qualified host fingerprint changed during preflight')
        workers = cap  # Profile choices constrain only their own active jobs.
        wc.configuration_target(root, workers)
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
                  started_epoch=started, memory_budget_gb=budget, settings=runtime_settings, passed=False, proofs=[])
    try:
        result['configuration'] = configuration
        # Each admitted job has its own disposable pool. Its profile's measured
        # choice applies unless the operator selected an explicit target.
        tasks = [dict(p['items'][j], input_view=views['proof']) for j in p['assignments'][host]]
        peaks = {}
        for cfg in configuration.values():
            for key, value in cfg.get('class_peaks_gb', {}).items(): peaks[key] = max(peaks.get(key, 0.), value)
        fresh, trace = run_items(tasks, workers, budget, control_path=control_path, host_settings=runtime_settings,
                                 class_peaks=peaks, headroom=runtime_settings.get('memory_headroom', .8), measurements_by_profile=configuration)
        result.update(workers=workers, admission=trace,
                      proofs=[proof_row(p['items'][j], fresh[j]) for j in p['assignments'][host]])
        _require(source_manifest() == p['record']['new_source_manifest'], 'source changed during shard')
        verify_code(p['code_commit'])
        result['passed'] = all(r['passed'] for r in result['proofs'])
    except BaseException as exc:
        result['error'] = type(exc).__name__ + ': ' + str(exc)
        raise
    finally:
        result['worker_control'] = read(control_path)
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
    found.update(f for f in root.glob('*/*.json') if f.name not in ('preflight.json', 'control.json', 'scheduling.json'))
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

    Uses item 10 charges and registered class rates. It is conditional on each
    host's subsequent configuration test selecting that count.
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
    times, slots = {}, {}
    for name, ids in assignments.items():
        h = hosts[name]
        slots[name] = h['worker_cap']
        rows = [dict(key=j, seconds=items[j]['resources']['worker_seconds'], memory=items[j]['resources']['memory_gb']) for j in ids]
        times[name], _ = wc.packed_wall(rows, slots[name], h['settings'].get('memory_headroom', .8) * h['memory_gb'], h.get('per_job_relative_throughput', h['relative_throughput']))
        _require(times[name] is not None, 'host cannot admit a proof job')
    return dict(selected_jobs=len(items), selection_sha256=digest(list(items)), assignment_sha256=digest(assignments),
                registered_worker_hours=sum(i['resources']['worker_seconds'] for i in items.values()) / 3600,
                wall_hours=max(times.values()) / 3600,
                x2_equivalent_hours=sum(times[h] * hosts[h]['relative_throughput'] for h in times) / 3600,
                relative_throughputs={h: e['relative_throughput'] for h, e in hosts.items()},
                conditional_worker_counts=slots, condition='configuration test selects these counts; overhead excluded')


def control_attempt(path, host, workers, reason=None):
    p = load_attempt(path)
    _require(host in p['hosts'], 'foreign shard host')
    root = host_directory(path, host)
    _require(not (root / 'result.json').exists(), 'shard attempt is final')
    runtime_settings = dict(p['hosts'][host]['settings'])
    items = [p['items'][j] for j in p['assignments'][host]]
    estimates = {i['job']['id']: i['resources'] for i in items}
    peaks = {i['resources']['memory_class']: i['resources'].get('measured_memory_gb', 0.) for i in items}
    if (root / 'preflight.json').exists():
        for cfg in unseal(read(root / 'preflight.json')).get('configuration', {}).values():
            for key, value in cfg.get('class_peaks_gb', {}).items():
                peaks[key] = max(peaks.get(key, 0.), value)
    return wc.control(root, runtime_settings, workers=workers, reason=reason, estimates=estimates, peaks=peaks)


def attempt_load_sheet(path, host=None, *, workers=None, override_reason=None, operator=None, memory_headroom=None, historical=False):
    # Pure projection of a sealed old attempt. This path never enables staging,
    # control, execution or combining at another identity, and writes nothing.
    p = unseal(read(path)) if historical else load_attempt(path)
    if historical:
        _require(p['schema'] == SCHEMA and set(p['assignments']) == set(p['hosts']), 'invalid frozen attempt')
        ids = sum(p['assignments'].values(), [])
        _require(len(ids) == len(set(ids)) and sorted(ids) == sorted(p['selected_job_ids'])
                 and set(ids) == set(p['items']), 'invalid frozen partition')
    names = [host] if host else sorted(p['hosts'])
    result = {}
    for name in names:
        _require(name in p['hosts'], 'foreign shard host')
        entry = p['hosts'][name]
        planned = dict(entry['settings'])
        if workers is not None:
            if not override_reason: raise ValueError('initial proof worker override requires --override-reason')
            planned['workers'] = workers
        if override_reason:
            planned.update(override_reason=override_reason, operator=operator)
            planned.pop('operator_override', None)
        if memory_headroom is not None: planned['memory_headroom'] = memory_headroom
        planned = wc.settings(planned, local=False)
        items = [p['items'][j] for j in p['assignments'][name]]
        estimates = {i['job']['id']: dict(memory_class=i['resources']['memory_class'], memory_known=i['resources'].get('memory_known', True),
            memory_gb=i['resources'].get('registered_memory_gb', i['resources']['memory_gb']),
            estimated_seconds=i['resources']['worker_seconds'], measured_seconds=i['resources'].get('measured_worker_seconds')) for i in items}
        peaks = {i['resources']['memory_class']: i['resources'].get('measured_memory_gb', 0.) for i in items}
        control_path = None if historical else host_directory(path, name) / 'control.json'
        preflight_path = None if historical else host_directory(path, name) / 'preflight.json'
        configurations = unseal(read(preflight_path)).get('configuration', {}) if preflight_path is not None and preflight_path.exists() else {}
        result[name] = wc.load_sheet([i['job'] for i in items], estimates, planned, entry['memory_gb'],
            peaks=peaks, measured_rate=entry.get('per_job_relative_throughput', entry['relative_throughput']),
            job_profiles={i['job']['id']: i.get('profile_key', i['job']['kind']) for i in items},
            measurements_by_profile={key: cfg['measurements'] for key,cfg in configurations.items()},
            control_value=read(control_path) if control_path is not None and control_path.exists() and workers is None and not override_reason else None)
    return result


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
        if command == 'run':
            s.add_argument('--workers', type=int); wc.options(s); s.set_defaults(memory_headroom=None)
    s = sub.add_parser('control'); s.add_argument('attempt'); s.add_argument('--host', required=True)
    s.add_argument('--workers', type=int, required=True); s.add_argument('--reason')
    s = sub.add_parser('load-sheet'); s.add_argument('attempt'); s.add_argument('--host')
    s.add_argument('--historical', action='store_true', help='read-only projection of a sealed attempt at another identity')
    s.add_argument('--workers', type=int); wc.options(s); s.set_defaults(memory_headroom=None)
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
    elif args.command == 'control':
        print(control_attempt(args.attempt, args.host, args.workers, args.reason))
    elif args.command == 'load-sheet':
        print(attempt_load_sheet(args.attempt, args.host, workers=args.workers, historical=args.historical, **wc.arguments(args)))
    elif args.command == 'run':
        result = run_shard(args.attempt, args.host, workers=args.workers, **wc.arguments(args))
        print(dict(passed=result['passed'], jobs=len(result['proofs']), x2_equivalent_hours=result['x2_equivalent_hours']))
        return 0 if result['passed'] else 1
    else:
        result = combine(args.attempt, args.shard)
        print(dict(passed=result['passed'], jobs=len(result['proofs'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
