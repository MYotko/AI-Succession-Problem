"""Executor scheduling controls and per-class reservations. No scientific reads."""
from copy import deepcopy
import getpass
import math
from pathlib import Path
import time

from .artifacts import atomic_json, digest, lease, read, scoped

# Operator policy: flip this one setting only if the operator selects override precedence.
MODE_CAPS_TARGET = True


def positive(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def options(parser):
    parser.add_argument('--override-reason', help='operator justification for exact workers or memory headroom')
    parser.add_argument('--operator', default=None)
    parser.add_argument('--memory-headroom', type=float, default=.8)


def arguments(args):
    return {key: getattr(args, key) for key in ('override_reason', 'operator', 'memory_headroom')}


def settings(value, *, local=True):
    """Record an intentional initial override once, without changing job settings."""
    from .production_runner import caps, available_cpus
    s = deepcopy(value)
    s['caps'] = caps(s['profile'], s['cpu_budget'])
    if (type(s['workers']) is not int or s['workers'] < 1 or s['threads'] not in (1, 2)
            or type(s['cpu_budget']) is not int or s['cpu_budget'] < 1
            or (local and s['cpu_budget'] > available_cpus())
            or s['workers'] * s['threads'] > s['cpu_budget'] or s['mode'] not in ('normal', 'work')):
        raise ValueError('workers times threads must fit the host CPU budget')
    fraction = s.get('memory_headroom', .8)
    if not positive(fraction) or fraction > .95:
        raise ValueError('memory headroom must be positive and at most 0.95')
    reason = s.get('override_reason')
    if reason is not None and (not isinstance(reason, str) or not reason.strip()):
        raise ValueError('override requires a nonempty reason')
    if (fraction != .8 or s['workers'] > s['caps'][s['mode']]) and not reason:
        raise ValueError('override requires --override-reason')
    s['memory_headroom'] = fraction
    content = dict(operator=s.get('operator') or getpass.getuser(), reason=reason,
                   workers=s['workers'], memory_headroom=fraction)
    if reason and override_content(s.get('operator_override')) != content:
        s['operator_override'] = dict(content, epoch=time.time())
    return s


def override_content(value):
    return {k: value.get(k) for k in ('workers', 'memory_headroom', 'reason', 'operator')} if value else None


def apply_initial_override(value, s):
    override = s.get('operator_override')
    if override and override_content(value.get('initial_override')) != override_content(override):
        value = change(value, s, workers=s['workers'], reason=override['reason'], operator=override['operator'])
        value['initial_override'] = deepcopy(override)
    return value


def initial_control(root, s):
    """Identical flags preserve a live target, regardless of invocation time."""
    path = Path(root) / 'control.json'
    with lease(Path(root) / 'control.lock'):
        value = read(path) if path.exists() else dict(mode=s['mode'], max_workers=s['workers'],
                                                     stop_dispatch=False, interrupt_now=False)
        value = apply_initial_override(value, s)
        atomic_json(path, value)
    return value


def configuration_target(root, workers):
    """Do not overwrite an operator control racing with configuration completion."""
    with lease(Path(root) / 'control.lock'):
        path = Path(root) / 'control.json'
        value = read(path)
        if not value.get('target_set') and not value.get('worker_override'):
            value['max_workers'] = workers
            atomic_json(path, value)
        return value


def selection(s, control=None, measurements=None, fixed=None, default_cap=None):
    from .production_runner import choose, caps
    control = control or {}
    mode = control.get('mode', s.get('mode', 'normal'))
    if mode not in ('normal', 'work'):
        raise ValueError('invalid live mode')
    threads = fixed['threads'] if fixed else s['threads']
    cpu_cap = s['cpu_budget'] // threads
    requested = control.get('max_workers', s['workers'])
    if type(requested) is not int or not 0 <= requested <= cpu_cap:
        raise ValueError('worker target must fit the host CPU budget')
    explicit = control.get('worker_override', bool(s.get('operator_override')))
    directed = control.get('target_set', False)
    if not explicit and not directed:
        requested = min(requested, s['workers'])
    if fixed:
        limit = min(fixed['workers'], cpu_cap)
        if default_cap is not None and not explicit and not directed: limit = min(limit, default_cap)
        if control.get('worker_override') or directed: limit = min(limit, requested)
        return dict(fixed, workers=limit)
    limit = requested if explicit and not MODE_CAPS_TARGET else min(requested, caps(s['profile'], s['cpu_budget'])[mode])
    if default_cap is not None and not explicit and not directed: limit = min(limit, default_cap)
    if explicit or directed or limit == 0 or not measurements:
        return dict(workers=limit, threads=threads)
    return choose(measurements, limit, s['cpu_budget'], threads)


def change(value, s, *, workers=None, mode=None, reason=None, operator=None):
    from .production_runner import caps
    result = deepcopy(value)
    previous = result.get('max_workers', s['workers'])
    if reason is not None and (not isinstance(reason, str) or not reason.strip()):
        raise ValueError('worker override requires a nonempty reason')
    if mode is not None:
        if mode not in ('normal', 'work'): raise ValueError('invalid mode')
        result['mode'] = mode
    effective_mode = result.get('mode', s['mode'])
    if workers is not None:
        if type(workers) is not int or not 0 <= workers <= s['cpu_budget'] // s['threads']:
            raise ValueError('worker target must fit the host CPU budget')
        if workers > caps(s['profile'], s['cpu_budget'])[effective_mode] and not reason:
            raise ValueError('live target above the mode cap requires --reason')
        result.update(max_workers=workers, worker_override=True, target_set=True)
    result.setdefault('history', []).append(dict(epoch=time.time(), operator=operator or getpass.getuser(),
        workers=workers, mode=mode, reason=reason, previous_target=previous,
        target=result.get('max_workers', previous), effective_workers=selection(s, result)['workers'],
        mode_caps_target=MODE_CAPS_TARGET))
    return result


def control(root, s, *, workers=None, mode=None, reason=None, immediate=False, stop=None, estimates=None, peaks=None):
    root = scoped(root)
    with lease(root / 'control.lock'):
        path = root / 'control.json'
        value = read(path) if path.exists() else dict(mode=s['mode'], max_workers=s['workers'])
        value = change(value, s, workers=workers, mode=mode, reason=reason)
        if workers is not None:
            from .production_runner import caps
            if workers > caps(s['profile'], s['cpu_budget'])[value.get('mode', s['mode'])]:
                if estimates is None:
                    estimates, peaks = control_memory(root)
                require_memory_authority(s, value, estimates, peaks or {}, dict(workers=workers))
        if immediate or stop:
            value.update(stop_dispatch=immediate or stop != 'clear', interrupt_now=immediate or stop == 'now')
        atomic_json(path, value)
    return value


def control_memory(root):
    """Read sealed plans and executor memory metadata only, never results."""
    from .artifacts import unseal
    root = Path(root)
    if (root / 'manifest.json').exists():
        spec = unseal(read(root / 'manifest.json'))
        estimates = resources(spec)
        _, peaks = completion_measurements(root, spec['jobs'], estimates)
    elif (root / 'memory_authority.json').exists():
        value = read(root / 'memory_authority.json')
        estimates, peaks = value['estimates'], value['peaks']
    else:
        raise ValueError('above-mode worker target requires sealed memory estimates or measured peaks')
    for path in sorted(root.glob('*/memory_reservations.json')):
        for key, value in read(path).items():
            if positive(value): peaks[key] = max(peaks.get(key, 0.), value)
    if (root / 'launches.json').exists():
        for launch in read(root / 'launches.json'):
            for measurements in launch.get('configuration', {}).values():
                for measurement in measurements:
                    for key, value in measurement.get('class_peaks_gb', {}).items():
                        if positive(value): peaks[key] = max(peaks.get(key, 0.), value)
    return estimates, peaks


def resources(spec, jobs=None):
    """Frozen class estimates take precedence over a phase-wide fallback."""
    result = {}
    for j in jobs if jobs is not None else spec['jobs']:
        phase = j['config'].get('phase', j['kind'])
        cost_known = True
        memory_known = True
        unmeasured = None
        pull = spec.get('pull_dispatch', {})
        if j['id'] in pull.get('job_classes', {}):
            key = pull['job_classes'][j['id']]
            c = pull['cost_classes'][key]
            memory, seconds = c['memory_gb'], c['worker_seconds']
            # Earlier freeze() copied the phase maximum into every cost class.
            # Reconstruct that executor estimate from the same per-job formula;
            # the historical sealed plan and its cost/seed fields stay untouched.
            if (pull.get('memory_basis') is None
                    and memory == spec.get('memory_estimate_gb', {}).get(phase)):
                own = arithmetic_class(spec, j)
                if own is not None: unmeasured, memory = memory, own[1]
        elif j['id'] in spec.get('memory_estimate_gb', {}):
            key = spec.get('memory_classes', {}).get(j['id'], j['id'])
            memory, seconds = spec['memory_estimate_gb'][j['id']], 1.
            memory_known = spec.get('memory_estimate_known', {}).get(j['id'], True)
            cost_known = False
        elif j['id'] in spec.get('pooled_job_estimates', {}):
            c = spec['pooled_job_estimates'][j['id']]
            key, memory, seconds = c['memory_class'], c['memory_gb'], c['estimated_seconds']
        else:
            sealed = spec.get('memory_estimate_gb', {}).get(phase)
            memory_known = positive(sealed)
            key, memory, seconds = phase, sealed if memory_known else .25, 1.
            cost_known = False
            own = arithmetic_class(spec, j)
            if own is not None:
                if memory_known: unmeasured = memory
                key, memory = own
        if not positive(memory) or not positive(seconds): raise ValueError('invalid registered resource estimate')
        result[j['id']] = dict(memory_class=key, memory_gb=memory, estimated_seconds=seconds, cost_known=cost_known,
                                memory_known=memory_known, unmeasured_memory_gb=unmeasured)
    return result


def arithmetic_class(spec, job):
    """Apply the existing planning formula to this declared job, not a phase max.

    No output is used to infer an auto route. Table planning keeps its existing
    FV bound; continuation jobs declare their own route in the sealed config.
    """
    if spec.get('schema') not in ('v3-A10-estimation-1', 'v3-A4-validation-1', 'v3-A5-labels-1', 'v3-A13-extension-1'):
        return None
    from .table_validation_a4 import estimate_memory_gb, CENSUS_MEASURE
    from .continuation_validation import GROUPS
    c = job['config']; source = c.get('a1_job', job)['config']
    if 'settings' not in source: return None  # Explicit synthetic fixtures.
    values = dict(source['settings'])
    if job['kind'] == 'table':
        route = 'fv'
        memory = max(.25, estimate_memory_gb(route, values) * 9 / 8)
    else:
        values['groups'] = GROUPS
        route = c.get('route', 'plain')
        if job['kind'] == 'a4_census':
            values.update(groups=source['settings'].get('groups', GROUPS), burn=0, measure=CENSUS_MEASURE)
        memory = estimate_memory_gb(route, values)
        if job['kind'] == 'a5_fvplain':
            from .table_labels_a5 import P4_PLAIN_ANCHOR_GB
            memory = max(memory, P4_PLAIN_ANCHOR_GB)
    key = digest([job['kind'], c.get('phase'), route, source.get('setting_name'),
                  source.get('kernel', {}).get('capability'), values])
    return key, memory


def reservation(resource, peaks):
    peak = peaks.get(resource['memory_class'], 0.)
    if not positive(peak) and positive(resource.get('unmeasured_memory_gb')):
        return resource['unmeasured_memory_gb']
    return max(resource['memory_gb'], peak)


def require_memory_authority(s, control, estimates, peaks, selected=None, *, configuration_trial=False):
    from .production_runner import caps
    mode = (control or {}).get('mode', s.get('mode', 'normal'))
    explicit = (control or {}).get('worker_override', bool(s.get('operator_override')))
    count = (selected['workers'] if selected is not None else
             (control or {}).get('max_workers', s['workers']) if explicit else selection(s, control)['workers'])
    # Ordinary registered configuration candidates have their own CPU cap.
    # They are not operator overrides of the scientific work-mode target.
    if configuration_trial and not explicit:
        return
    if count > caps(s['profile'], s['cpu_budget'])[mode]:
        if any(not r.get('memory_known', True) and not positive(peaks.get(r['memory_class'])) for r in estimates.values()):
            raise ValueError('above-mode worker target requires a sealed memory estimate or measured peak for every class')


def memory_safe_selection(s, control, estimates, peaks, selected, *, configuration_trial=False):
    """A stale/unvalidated control cannot spend a running attempt."""
    from .production_runner import caps
    try:
        require_memory_authority(s, control, estimates, peaks, selected, configuration_trial=configuration_trial)
    except ValueError:
        return dict(selected, workers=min(selected['workers'], caps(s['profile'], s['cpu_budget'])[(control or {}).get('mode', s['mode'])]))
    return selected


def configuration_resources(jobs, sources, estimates, *, phase=None, spec=None):
    from .multihost_a11 import cost_keys
    def key(job):
        try:
            return job['kind'], tuple(cost_keys(job))
        except (KeyError, TypeError):
            c = job['config']
            return job['kind'], c.get('phase', phase or job['kind']), c.get('route'), digest(c.get('kernel', {}))
    groups = {}
    for source in sources or []:
        groups.setdefault(key(source), []).append(estimates[source['id']])
    result = {}
    for job in jobs:
        values = groups.get(key(job), [])
        if values and len({reservation(v, {}) for v in values}) == 1:
            result[job['id']] = min(values, key=lambda r: str(r['memory_class']))
            continue
        # Historical A4/A5 profiles omit phase; absent-route A4 profiles also
        # use a declared census prototype with no corresponding scientific job.
        # Resolve executor resources from that sealed phase or declared job.
        declared = dict(spec or {})
        declared['jobs'] = [job]
        declared.pop('pull_dispatch', None)
        if 'schema' not in declared:
            declared['schema'] = ('v3-A4-validation-1' if job['kind'].startswith('a4_') else
                                  'v3-A5-labels-1' if job['kind'].startswith('a5_') else
                                  'v3-A13-extension-1' if job['kind'].startswith('a13_') else '')
        effective_phase = job['config'].get('phase', phase or job['kind'])
        phase_values = [estimates[j['id']] for j in sources or []
                        if j['config'].get('phase', j['kind']) == effective_phase]
        memories = dict(declared.get('memory_estimate_gb', {}))
        if effective_phase not in memories and phase_values:
            known = [r for r in phase_values if r.get('memory_known', True)]
            if known: memories[effective_phase] = max(reservation(r, {}) for r in known)
        # A calculation-only copy; the dispatched config, seed and job id stay intact.
        proxy = dict(job, config=dict(job['config'], phase=effective_phase))
        declared['memory_estimate_gb'] = memories
        resource = resources(declared, [proxy])[job['id']]
        if not resource['memory_known'] and arithmetic_class(declared, proxy) is None and job['kind'] != 'fixture':
            raise ValueError('configuration profile has no declared memory class')
        result[job['id']] = resource
    return result


def profile_memory_limit(profile, sources, estimates, budget, pooled=None, *, phase=None, spec=None):
    """A uniform profile may use its own class cap; a mixed profile must pack.

    This is never the largest reservation applied to unrelated classes.
    """
    from .artifacts import stable_job
    jobs = [stable_job(profile['kind'], c, 'configuration', i)
            for i, c in enumerate(profile.get('configs', [profile['config']]))]
    if pooled is not None:
        members = [pooled[j['config']['phase']] for j in jobs]
    elif estimates is not None:
        matched = configuration_resources(jobs, sources, estimates, phase=phase, spec=spec)
        members = list(matched.values())
    else:
        return None
    sizes = {reservation(r, {}) for r in members}
    if len(sizes) != 1: return None
    return int(budget / sizes.pop())


def observe(peaks, resource, peak_bytes):
    if positive(peak_bytes):
        key = resource['memory_class']
        peaks[key] = max(peaks.get(key, 0.), 1.2 * peak_bytes / 1e9)


def completion_peaks(root, jobs, estimates):
    """Only metadata under records/. Never inspect an output for memory sizing."""
    peaks = {}
    for j in jobs:
        path = Path(root) / 'records' / (j['id'] + '.json')
        if path.exists():
            r = read(path)
            if r.get('status') == 'complete' and r.get('job') == j:
                observe(peaks, estimates[j['id']], r.get('peak_rss_bytes'))
    return peaks


def completion_measurements(root, jobs, estimates):
    """Class timing and RSS from durable executor records only."""
    peaks, seconds = {}, {}
    for job in jobs:
        phase = job['config'].get('phase', job['kind'])
        path = Path(root) / phase / 'records' / (job['id'] + '.json')
        if not path.exists(): continue
        record = read(path)
        if record.get('job') != job or record.get('status') != 'complete':
            raise ValueError('load-sheet completion metadata mismatch')
        resource = estimates[job['id']]
        observe(peaks, resource, record.get('peak_rss_bytes'))
        if positive(record.get('worker_seconds')):
            seconds.setdefault(resource['memory_class'], []).append(record['worker_seconds'])
    result = deepcopy(estimates)
    for resource in result.values():
        samples = seconds.get(resource['memory_class'], [])
        if samples: resource['measured_seconds'] = sum(samples) / len(samples)
    return result, peaks


def packed_wall(items, workers, budget, speed=1.):
    """Deterministic scheduling projection, using each reservation separately."""
    import heapq
    pending = sorted(items, key=lambda r: (-r['seconds'], r['key']))
    active, now, occupied, maximum = [], 0., 0., 0.
    if workers < 1 or any(i['memory'] > budget for i in pending):
        return None, 0.
    sequence = 0
    while pending or active:
        while pending and len(active) < workers:
            index = next((k for k, item in enumerate(pending) if item['memory'] + occupied <= budget + 1e-12), None)
            if index is None: break
            item = pending.pop(index); sequence += 1
            occupied += item['memory']; maximum = max(maximum, occupied)
            heapq.heappush(active, (now + item['seconds'] / speed, sequence, item['memory']))
        now, _, memory = heapq.heappop(active)
        occupied -= memory
    return now, maximum


def load_sheet(jobs, estimates, host_settings, available_gb, *, peaks=None, measured_rate=1., control_value=None, measurements=None, default_cap=None):
    """Output-blind totals/rates, with anonymous class memory rows only."""
    peaks = peaks or {}
    s = settings(host_settings, local=False)
    target = selection(s, control_value, measurements, default_cap=default_cap)['workers']
    require_memory_authority(s, control_value, estimates, peaks)
    budget = available_gb * s['memory_headroom']
    items = [dict(key=j['id'], seconds=estimates[j['id']]['estimated_seconds'],
                  memory=reservation(estimates[j['id']], peaks)) for j in jobs]
    wall, maximum = packed_wall(items, target, budget, measured_rate)
    measured_items = [dict(item, seconds=estimates[j['id']].get('measured_seconds')) for item,j in zip(items,jobs)]
    measured_wall = None
    if all(positive(item['seconds']) for item in measured_items):
        measured_wall, _ = packed_wall(measured_items, target, budget, measured_rate)
    seconds = sum(i['seconds'] for i in items)
    cost_known = all(r.get('cost_known', True) for r in estimates.values())
    explicit = (control_value or {}).get('worker_override', bool(s.get('operator_override')))
    mode = (control_value or {}).get('mode', s['mode'])
    classes = {r['memory_class']: dict(class_id=digest(r['memory_class']), registered_gb=r['memory_gb'],
               measured_peak_gb=peaks.get(r['memory_class'], 0.) / 1.2,
               reservation_gb=reservation(r, peaks), workers_if_all_this_class=min(target, int(budget / reservation(r, peaks)))) for r in estimates.values()}
    return dict(planned_workers=target, cpu_budget=s['cpu_budget'], threads=s['threads'],
                binding_cap=('mode/operator target' if MODE_CAPS_TARGET else 'operator/CPU') if explicit else 'mode/live target' if (control_value or {}).get('target_set') else 'configuration/mode/request/default ceiling' if default_cap is not None else 'configuration/mode/request' if measurements else 'mode/request (configuration pending)',
                memory_budget_gb=budget, available_memory_gb=available_gb, memory_headroom=s['memory_headroom'],
                cpu_worker_cap=s['cpu_budget']//s['threads'], mode_cap=s['caps'][mode], classes=list(classes.values()),
                projected_cpu_fraction=seconds * s['threads'] / (measured_rate * wall * s['cpu_budget']) if wall else None,
                projected_peak_memory_fraction=maximum / available_gb,
                class_wall_hours=wall / 3600 if wall is not None and cost_known else None,
                measured_wall_hours=measured_wall / 3600 if measured_wall is not None else None,
                relative_measured_rate=measured_rate, total_worker_hours=seconds / 3600 if cost_known else None)


def distributed_load_sheet(jobs, estimates, hosts):
    """Forecast an LPT partition, not a dispatch assignment or scientific input."""
    groups = {name: [] for name in hosts}
    for job in sorted(jobs, key=lambda j: (-estimates[j['id']]['estimated_seconds'], j['id'])):
        finish = {}
        for name, entry in hosts.items():
            if entry.get('kinds') and job['kind'] not in entry['kinds']:
                finish[name] = math.inf
                continue
            s = settings(entry['settings'], local=False)
            rows = [dict(key=j['id'], seconds=estimates[j['id']]['estimated_seconds'],
                         memory=reservation(estimates[j['id']], entry.get('peaks', {}))) for j in groups[name] + [job]]
            wall, _ = packed_wall(rows, selection(s)['workers'], entry['memory_gb'] * s['memory_headroom'], entry['rate'])
            finish[name] = wall if wall is not None else math.inf
        name = min(finish, key=lambda n: (finish[n], n))
        if not math.isfinite(finish[name]): raise ValueError('load sheet: no host can admit a job')
        groups[name].append(job)
    return {name: dict(load_sheet(group, {j['id']: estimates[j['id']] for j in group}, hosts[name]['settings'],
        hosts[name]['memory_gb'], peaks=hosts[name].get('peaks'), measured_rate=hosts[name]['rate']),
        forecast_jobs=len(group), forecast_only=True) for name, group in groups.items()}
