"""A11 pull coordinator. SSH transports JSON; this module owns the one root.

All transactions take runner.lock. coordinator.lock excludes a second monitor,
not RPCs. A completed record, never a lease or an output alone, is authoritative.
"""
import argparse
import base64
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
import uuid
from .dispatch_store_a11 import Store, OPEN_STORES, read_state, warm_connection
from .artifacts import (SIMULATION, atomic_json, canonical, code_identity, digest,
                        file_hash, lease, read, scoped, seal, stable_job, unseal)

SCHEMA = 'v3-A11-pull-1'
ALLOWED_KINDS = {'table', 'rerun', 'a4_fit', 'a4_validate', 'a4_census', 'a5_fvplain'}


def positive(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and value > 0


def cost_keys(job):
    """P2 means are bundle costs, used as ordering classes, not new timings."""
    c = job['config']
    if job['kind'] == 'rerun':
        inst = c['model']['instrument']
        category = c.get('category', c['phase'])
        return [f"runs.{category}.{inst['g']}.{inst['k_star']}"]
    source = c.get('a1_job', job)['config']
    family = source['a10_family']
    prefix = f"{family}.{float(source['kernel']['capability'])}.{source['setting_name']}."
    if job['kind'] == 'table':
        kinds = ['estimate']
    elif job['kind'] == 'a5_fvplain':
        kinds = ['labels']
    elif job['kind'] == 'a4_census':
        # No result is read to infer a route. The larger of the two declared
        # bundle means is the census class, including for auto-route sources.
        kinds = ['validate_plain', 'validate_fv']
    else:
        kinds = ['validate_fv' if c['route'] == 'fv' else 'validate_plain']
    return [prefix + kind for kind in kinds]


def freeze(spec, projection_document, *, code_commit, extra_inputs=(), lease_seconds=120):
    """Non-registered builder: add a sealed scheduling extension, no job edits."""
    if spec.get('instrument',{}).get('mapping') != 'A10' or (spec.get('registered') and not spec.get('registered_a10')):
        raise ValueError('R4 and legacy registered schemas refuse remote hosts')
    projection = unseal(projection_document)
    result = deepcopy(spec)
    if 'pull_dispatch' in result:
        raise ValueError('pull scheduling is already frozen')
    costs = projection['per_phase_capability']
    classes, assignments = {}, {}
    for job in result['jobs']:
        keys = cost_keys(job)
        means = [costs[k]['mean_worker_seconds'] for k in keys]
        memory = result.get('memory_estimate_gb', {}).get(job['config']['phase'])
        if memory is None:
            memory = max(costs[k]['memory_estimate_gb'] for k in keys)
        value = {'source_strata': keys, 'worker_seconds': max(means), 'memory_gb': memory}
        key = digest(value)
        classes[key] = value
        assignments[job['id']] = key
    result['pull_dispatch'] = {'schema': SCHEMA, 'projection_sha256': projection_document['sha256'],
        'code_commit': code_commit, 'lease_seconds': lease_seconds, 'cost_classes': classes,
        'job_classes': assignments, 'extra_inputs': list(extra_inputs),
        'order': 'descending frozen bundle mean worker seconds, then job id',
        'census_class': 'maximum of plain and FV bundle means; no result consulted'}
    validate_extension(result)
    return result


def validate_extension(spec):
    p = spec.get('pull_dispatch', {})
    if p.get('schema') != SCHEMA or spec.get('instrument', {}).get('mapping') != 'A10':
        raise ValueError('remote hosts require an explicit A11 pull A10 manifest')
    if spec.get('registered') and not spec.get('registered_a10'):
        raise ValueError('legacy registered schemas refuse remote hosts')
    if spec.get('publication') or spec.get('completion_screen') or spec.get('tag') == 'pilot':
        raise ValueError('unsupported automatic publication, repair or pilot in pull mode')
    if not positive(spec.get('x2_equivalent_hours')) or not positive(spec.get('wall_seconds')):
        raise ValueError('pull launch requires explicit positive wall and X2-equivalent ceilings')
    if not positive(p.get('lease_seconds')) or not p.get('code_commit'):
        raise ValueError('pull launch needs a lease duration and implementation commit')
    if set(p['job_classes']) != {j['id'] for j in spec['jobs']}:
        raise ValueError('every job needs exactly one frozen cost class')
    for job in spec['jobs']:
        if job['kind'] not in ALLOWED_KINDS and not (not spec['registered'] and job['kind'] == 'fixture'):
            raise ValueError('unsupported pull job kind')
        cls = p['cost_classes'][p['job_classes'][job['id']]]
        if not positive(cls['worker_seconds']) or not positive(cls['memory_gb']):
            raise ValueError('invalid frozen job cost or memory')


@contextmanager
def transaction(root):
    # Separate SSH processes contend briefly. No network or simulation runs
    # inside this lock. Failure to acquire is retryable by the host.
    until = time.monotonic() + 30
    while True:
        lock = lease(scoped(root) / 'runner.lock')
        try:
            lock.__enter__()
            break
        except RuntimeError as exc:
            if str(exc) != 'lease already held' or time.monotonic() >= until:
                raise
            time.sleep(.025)
    opened = []
    token = OPEN_STORES.set(opened)
    try:
        yield
    finally:
        for store in opened:
            store.close()
        OPEN_STORES.reset(token)
        lock.__exit__(None, None, None)


def append(root, directory, payload):
    """Immutable sequence of individually sealed entries, fsynced by writer."""
    folder = scoped(root) / directory
    entries = sorted(folder.glob('*.json'))
    previous = file_hash(entries[-1]) if entries else None
    path = folder / ('%08d.json' % len(entries))
    if path.exists():
        raise RuntimeError('append-only record collision')
    atomic_json(path, seal({'sequence': len(entries), 'previous_sha256': previous, **payload}))
    return path


def register_entries(root):
    result, previous = {}, None
    for i, path in enumerate(sorted((Path(root) / 'machine_register').glob('*.json'))):
        raw = path.read_bytes()
        row = unseal(json.loads(raw))
        if row['sequence'] != i or row['previous_sha256'] != previous or row['host'] in result:
            raise ValueError('machine register chain or duplicate approval')
        previous = hashlib.sha256(raw).hexdigest()
        result[row['host']] = row
    return result


def approve_host(root, evidence_document, operator, when):
    from .qualification_a11 import validate_evidence
    with transaction(root):
        spec = unseal(read(Path(root) / 'manifest.json'))
        e = validate_evidence(evidence_document, spec['code_hash'])
        if not operator.strip() or not when.strip():
            raise ValueError('operator and approval timestamp required')
        if e['candidate']['host'] in register_entries(root):
            raise ValueError('host already approved for this launch')
        if not set(e['kinds']) <= {j['kind'] for j in spec['jobs']}:
            raise ValueError('qualification includes unrelated job kinds')
        target = Path(root) / 'qualifications' / (evidence_document['sha256'] + '.json')
        atomic_json(target, evidence_document)
        return append(root, 'machine_register', {'host': e['candidate']['host'],
            'code_hash': e['code_hash'], 'qualification_sha256': evidence_document['sha256'],
            'relative_throughput': e['relative_throughput'], 'memory_gb': e['candidate']['memory_gb'],
            'fingerprint': e['candidate']['fingerprint'], 'kinds': e['kinds'],
            'operator_approval': {'operator': operator, 'when': when}})


def prepare(spec_path, root, settings):
    from .production_runner import caps, validate_spec
    spec = unseal(read(spec_path))
    validate_extension(spec)
    settings = dict(settings, caps=caps(settings['profile'], settings['cpu_budget']))
    preflight = validate_spec(spec, settings)
    root = scoped(root)
    with transaction(root):
        identity = {'spec_hash': digest(spec), 'code_hash': code_identity()}
        if (root / 'identity.json').exists() and read(root / 'identity.json') != identity:
            raise RuntimeError('incompatible resumption')
        atomic_json(root / 'identity.json', identity)
        atomic_json(root / 'manifest.json', seal(spec))
        atomic_json(root / 'context_preflight.json', preflight)
        if not (root / 'pull_state.json').exists():
            atomic_json(root / 'pull_state.json', seal({'epoch': 0, 'started': None, 'phase_index': 0,
                'sessions': {}, 'leases': {}, 'checks': {}, 'halt': None, 'complete': False,
                'control': {'stop_dispatch': False, 'interrupt_now': False}, 'projections': {}, 'completions': {}}))
    return spec


class Coordinator:
    """Construct only under transaction(). Clock injection is for loopback tests."""
    def __init__(self, root, now=None, current_code=None):
        self.root, self.now = scoped(root), time.time() if now is None else now
        self.store = Store(self.root, validate_extension)
        self.spec = self.store.spec
        self.code = code_identity() if current_code is None else current_code
        if self.spec['code_hash'] != self.code:
            raise RuntimeError('incompatible resumption; root identity stays strict')
        self.state = self.store.state
        self.register = register_entries(self.root)
        self.jobs = self.store.jobs
        self.done = self.store.done
        failure = self.root / 'nondeterminism_failure.json'
        if failure.exists():
            self.state['halt'] = 'nondeterminism'
        self.expire()

    @property
    def ttl(self):
        return self.spec['pull_dispatch']['lease_seconds']

    @property
    def phase(self):
        i = self.state['phase_index']
        return self.spec['phases'][i] if i < len(self.spec['phases']) else None

    def save(self, force=False):
        # Only touched rows enter the durable chained log. Status is a bounded
        # rate diagnostic snapshot, never dispatch's source of truth.
        terminal = [self.state['halt'], self.state['complete'], self.state.get('stop_reason'),
                    self.phase, self.state['epoch']]
        previous = self.store.get('status')
        due = force or previous['epoch'] is None or self.now - previous['epoch'] >= 2 or terminal != previous['terminal']
        self.store.commit()
        if due:
            status = self.status()
            atomic_json(self.root / 'status.json', status)
            for phase in self.spec['phases']:
                total, done = self.store.counts(phase)
                running = sum(l['phase'] == phase for l in self.active())
                atomic_json(self.root / phase / 'status.json', {'phase': phase, 'total': total, 'completed': done,
                    'running': running, 'pending': total - done, 'hosts': status['hosts'],
                    'started_epoch': self.state['started'], 'updated_epoch': self.now,
                    'complete': done == total and (not total or self.state['checks'].get(phase, {}).get('matched', False)) and not self.state['halt'],
                    'reason': self.state['halt'] or self.state.get('stop_reason') or ('complete' if self.state['complete'] else 'pull')})
            if force or terminal != previous['terminal']:
                atomic_json(self.root / 'pull_state.json', seal(dict(self.store.small_state(),
                    operational_store='dispatch.sqlite', checkpoint_only=True)))
            self.store.set('status',dict(epoch=self.now,terminal=terminal))
            self.store.commit()

    def active(self, session=None):
        return self.store.active(session)

    def close(self, sid, end, reason):
        s = self.state['sessions'][sid]
        if s['end'] is None:
            s.update(end=max(s['joined'], end), end_reason=reason)

    def expire(self):
        for l in self.active():
            if l['expires'] <= self.now:
                token = next(r[0] for r in self.store.db.execute("SELECT id FROM leases WHERE job=? AND session=? AND status='active' AND expires=?", (l['job_id'], l['session'], l['expires'])))
                l['status'] = 'expired'
                append(self.root, 'protocol_events', {'event': 'lease_expired', 'lease': token, 'epoch': self.now})
        for sid, s in self.state['sessions'].items():
            if s['end'] is None and s['heartbeat'] + self.ttl <= self.now:
                self.close(sid, s['heartbeat'] + self.ttl, 'heartbeat expired')

    def charged_seconds(self):
        return sum(
            max(0, (self.now if s['end'] is None else s['end']) - s['joined']) * s['relative_throughput']
            for s in self.state['sessions'].values())

    def stops(self):
        reserve = self.spec.get('cleanup_reserve_seconds', 180)
        started = self.state['started']
        return {'halt': bool(self.state['halt']), 'projection': self.state.get('stop_reason') == 'projection_exceeds_budget', 'not_started': started is None,
                'control': self.state['control']['stop_dispatch'],
                'wall': started is not None and self.now >= started + self.spec['wall_seconds'] - reserve,
                'x2': self.charged_seconds() >= self.spec['x2_equivalent_hours'] * 3600 - reserve,
                'coordinator': self.state.get('monitor_required', False) and self.now - self.state.get('monitor_epoch', 0) >= self.ttl}

    def status(self):
        hosts = {}
        for sid, s in self.state['sessions'].items():
            row = hosts.setdefault(s['host'], {'completed': 0, 'running': 0, 'sessions': [], 'worker_seconds': 0})
            row['sessions'].append({'id': sid, **s})
            row['worker_seconds'] += s['worker_seconds'] + sum(s.get('configuration_worker_seconds', {}).values())
        self.done.flush()
        for host, count in self.store.db.execute('SELECT host,n FROM host_counts'):
            hosts.setdefault(host, {'completed': 0, 'running': 0, 'sessions': [], 'worker_seconds': 0})['completed'] = count
        for l in self.active():
            hosts[l['host']]['running'] += 1
        return {'phase': self.phase, 'complete': self.state['complete'], 'halt': self.state['halt'],
                'completed': len(self.done), 'pending': len(self.jobs) - len(self.done), 'hosts': hosts, 'reason': self.state.get('stop_reason'),
                'x2_equivalent_hours': self.charged_seconds() / 3600, 'stops': self.stops(), 'epoch': self.now,
                'hard_stop': self.state['control']['interrupt_now'] or self.stops()['coordinator'] or (self.state['started'] is not None and
                    self.now >= self.state['started'] + self.spec['wall_seconds'])}

    def start(self):
        from .production_runner import completed
        self.store.verify_journal()
        # Rebuild from validated durable records after every coordinator restart.
        # Normal RPCs use this cache, not thousands of scientific-output reads.
        self.done.clear()
        for job in self.jobs.values():
            value = completed(self.root / job['config']['phase'], job, self.code)
            if value is not None:
                self.done[job['id']] = {'host': value['host'], 'phase': job['config']['phase']}
        for phase in self.spec['phases']:
            path = self.root / phase / 'nondeterminism_check.json'
            if path.exists():
                self.state['checks'][phase] = read(path)
        if self.state['started'] is None:
            self.state['started'] = self.now
            reserve = self.spec.get('cleanup_reserve_seconds', 180)
            atomic_json(self.root / 'budget.json', {'start_epoch': self.now,
                'deadline_epoch': self.now + self.spec['wall_seconds'] - reserve,
                'overall_deadline_epoch': self.now + self.spec['wall_seconds'], 'cleanup_reserve_seconds': reserve,
                'x2_equivalent_hours': self.spec['x2_equivalent_hours']})
        self.state.setdefault('sample_jobs', {})
        for phase in self.spec['phases']:
            if phase not in self.state['sample_jobs']:
                jobs = self.jobs.phase(phase)
                if jobs:
                    self.state['sample_jobs'][phase] = self.sampled_check(jobs, phase)['id']
        self.state['epoch'] += 1
        for l in self.active():
            l['status'] = 'void_on_resume'
        for sid, s in self.state['sessions'].items():
            if s['end'] is None:
                self.close(sid, min(self.now, s['heartbeat'] + self.ttl), 'coordinator resume')
        self.state['projections'] = {}
        self.state.pop('stop_reason', None)
        append(self.root, 'protocol_events', {'event': 'coordinator_start', 'epoch': self.now, 'generation': self.state['epoch']})

    def member(self, host):
        if host not in self.register:
            raise ValueError('unregistered host')
        row = self.register[host]
        if row['code_hash'] != self.code or not row.get('operator_approval'):
            raise ValueError('unapproved host identity')
        return row

    def session(self, request):
        s = self.state['sessions'].get(request.get('session'))
        self.member(request['host'])
        if not s or s['host'] != request['host'] or s['end'] is not None:
            raise ValueError('inactive or wrong host session')
        return s

    def join(self, r):
        from .production_runner import caps
        entry = self.member(r['host'])
        if self.state['started'] is None or self.state['complete'] or self.state['halt'] or self.state.get('stop_reason'):
            raise ValueError('coordinator is not accepting joins')
        if r['fingerprint'] != entry['fingerprint'] or r['code_hash'] != self.code or r['code_commit'] != self.spec['pull_dispatch']['code_commit']:
            raise ValueError('host fingerprint or code identity mismatch')
        settings = r['settings']
        limits = caps(settings['profile'], settings['cpu_budget'])
        if settings['threads'] != 1 or settings['mode'] not in ('normal', 'work') or not 1 <= settings['workers'] <= limits[settings['mode']]:
            raise ValueError('invalid host caps')
        if settings['profile'] == 'x2' and r['host'].lower() != 'yotko-evo-x2':
            raise ValueError('X2 profile needs the X2 host')
        if settings['profile'] == 'x2' and (r.get('service') or {}).get('down_exit_code') != 0:
            raise ValueError('X2 worker needs its active service supervisor')
        if any(s['host'] == r['host'] and s['end'] is None for s in self.state['sessions'].values()):
            raise ValueError('host is already joined')
        sid = uuid.uuid4().hex
        control = self.state.setdefault('host_controls', {}).setdefault(r['host'],
            {'mode': settings['mode'], 'max_workers': settings['workers'], 'drain': False})
        self.state['sessions'][sid] = {'host': r['host'], 'joined': self.now, 'end': None, 'heartbeat': self.now,
            'relative_throughput': entry['relative_throughput'], 'worker_seconds': 0.,
            'settings': dict(settings, caps=limits), 'control': dict(control),
            'configuration': {}, 'chosen': {}, 'ready': {}, 'service': r.get('service')}
        return {'session': sid, 'spec': self.store.full_spec(), 'phase_roots': {p: str(self.root / p) for p in self.spec['phases']},
                'lease_seconds': self.ttl, 'qualified_kinds': entry['kinds']}

    def snapshot(self, phase, configuration=False):
        from .snapshot_a11 import inventory
        if phase not in self.spec['phases']:
            raise ValueError('unknown phase')
        name = ('configuration_' if configuration else 'phase_') + phase
        path = self.root / 'input_manifests' / (name + '.json')
        if not path.exists():
            if configuration:
                profile = self.spec['configuration'][phase]
                jobs = [stable_job(profile['kind'], c, 'configuration', i) for i, c in enumerate(profile.get('configs', [profile['config']]))]
            else:
                if phase != self.phase:
                    raise ValueError('phase inputs unavailable before its barrier')
                jobs = self.jobs.phase(phase)
            atomic_json(path, inventory(jobs, self.root / phase, self.spec['pull_dispatch']['extra_inputs']))
        return read(path)

    def configure(self, r):
        from .production_runner import choose
        s = self.session(r)
        phase = r['phase']
        if phase == 'validate_plain' and 'fit' not in s['configuration']:
            raise ValueError('plain projection requires measured fit configuration')
        if r['input_sha256'] != self.snapshot(phase, True)['sha256']:
            raise ValueError('configuration input snapshot mismatch')
        measurements = r['measurements']
        if not measurements or any(not m.get('valid') or not positive(m['wall_seconds']) or not m.get('job_seconds') for m in measurements):
            raise ValueError('configuration test incomplete')
        settings = s['settings']
        cap = min(settings['caps'][s['control']['mode']], s['control']['max_workers'])
        selected = choose(measurements, cap, settings['cpu_budget'], 1)
        s['configuration'][phase] = measurements
        s['chosen'][phase] = selected
        s['last_work_end'] = self.now
        # Configuration is excluded from results but included in operational
        # worker-seconds. Retry of an identical acknowledgement is idempotent.
        s.setdefault('configuration_worker_seconds', {})[phase] = sum(sum(m['job_seconds']) for m in measurements)
        self.state['projections'] = {}
        return selected

    def projection(self):
        """Keep A4's per-cell and fit-subtraction arithmetic; sum host rates."""
        if self.spec['schema'] not in ('v3-A4-validation-1', 'v3-A5-labels-1'):
            return True
        from .production_runner import a4_projection
        present = [s for s in self.state['sessions'].values() if s['end'] is None and not s['control']['drain'] and s['chosen']]
        present.sort(key=lambda s: s['host'])
        if not present:
            return False
        key = digest([self.phase, [(s['host'], s['configuration'], s['control']) for s in present]])
        if key in self.state['projections']:
            return self.state['projections'][key]['fits']
        deadline = self.state['started'] + self.spec['wall_seconds'] - self.spec.get('cleanup_reserve_seconds', 180)
        per_host = []
        for s in present:
            workers = {p: min(s['chosen'][p]['workers'], s['settings']['caps'][s['control']['mode']], s['control']['max_workers'])
                       for p in s['chosen']}
            per_host.append(a4_projection(dict(self.spec, jobs=list(self.jobs.values())), s['configuration'], workers, self.root, self.code,
                                          self.state['phase_index'], self.now, deadline))
        total, phases = 0., {}
        for phase in self.spec['phases'][self.state['phase_index']:]:
            eligible = [(s, p) for s, p in zip(present, per_host) if phase in s['chosen']]
            rows = [p['phases'][phase] for s, p in eligible]
            rows = [r for r in rows if r['remaining']]
            if not rows:
                if any(j['config']['phase'] == phase and j['id'] not in self.done for j in self.jobs.values()):
                    return False
                continue
            if any(r['per_cell_rate'] <= 0 for r in rows):
                return False
            # Each old wall = total_cells * rate / workers + shortest_cells * rate.
            # Re-evaluate at one worker and recover cells from the declared jobs.
            jobs = [j for j in self.jobs.values() if j['config']['phase'] == phase and j['id'] not in self.done]
            cells = []
            for j in jobs:
                c = j['config']; st = c['a1_job']['config']['settings']
                count = st['particles' if c['route'] == 'fv' else 'runs_per_group']
                length = 519 if phase == 'census' else st['burn'] + st['measure']
                cells.append(32 * count * length)
            rate = sum(r['workers'] / r['per_cell_rate'] for r in rows)
            wall = sum(cells) / rate + min(cells) * max(r['per_cell_rate'] for r in rows)
            phases[phase] = {'wall_seconds': wall, 'cells_per_second': rate, 'hosts': [s['host'] for s, p in eligible]}
            total += wall
        result = {'phases': phases, 'total_seconds': total, 'remaining_budget_seconds': deadline - self.now, 'fits': total <= deadline - self.now}
        self.state['projections'][key] = result
        append(self.root, 'phase_projections', {'epoch': self.now, **result})
        return result['fits']

    def sampled_check(self, jobs, phase=None):
        def cost(job):
            c = job['config']; s = c.get('a1_job', {}).get('config', {}).get('settings', {})
            count = s.get('particles' if c.get('route') == 'fv' else 'runs_per_group', 1)
            length = 519 if c.get('stage') == 'census' else s.get('burn', 0) + s.get('measure', 0)
            ov = c.get('settings_override', {}) or {}
            if ov:
                length = ov.get('census_measure', length) if c.get('stage') == 'census' else ov.get('burn', 0) + ov.get('measure', 0)
            return count * length
        minimum = min(map(cost, jobs))
        shortest = sorted((j for j in jobs if cost(j) == minimum), key=lambda j: j['id'])
        draw = int(digest(['A4-nondeterminism', phase or self.phase, [j['id'] for j in shortest]]), 16)
        return shortest[draw % len(shortest)]

    def phase_hosts(self, phase):
        self.store.sync()
        return {r[0] for r in self.store.db.execute('SELECT host FROM participants WHERE phase=?',(phase,))}

    def advance(self):
        while self.phase is not None:
            total, done = self.store.counts(self.phase)
            if done != total:
                break
            if total and not self.state['checks'].get(self.phase, {}).get('matched'):
                break
            if any(l['phase'] == self.phase for l in self.active()):
                break  # Drain speculative duplicates before crossing a barrier.
            self.state['phase_index'] += 1
        if self.phase is None and not self.state['halt']:
            self.state['complete'] = True
            for sid, s in self.state['sessions'].items():
                if s['end'] is None:
                    self.close(sid, s.get('last_work_end', self.now), 'last work at launch completion')

    def projection_ready(self):
        present = [s for s in self.state['sessions'].values() if s['end'] is None and not s['control']['drain']]
        if not present:
            return False
        for s in present:
            required = {p for p, profile in self.spec['configuration'].items()
                        if profile['kind'] in self.member(s['host'])['kinds']}
            if not s.get('configuration_done') and not required <= set(s['chosen']):
                return False
        return True

    def check_projection(self):
        if self.state.get('stop_reason') or self.state['halt'] or self.state['complete']:
            return False
        if self.spec['schema'] not in ('v3-A4-validation-1', 'v3-A5-labels-1'):
            return True
        if not self.projection_ready():
            return None
        if self.projection():
            return True
        reason = 'projection_exceeds_budget'
        self.state['stop_reason'] = reason
        for sid in self.state['sessions']:
            self.close(sid, self.now, reason)
        append(self.root, 'protocol_events', dict(event=reason, epoch=self.now, phase=self.phase))
        history_path = self.root / 'launches.json'
        if history_path.exists():
            history = read(history_path)
            history[-1].update(reason=reason, stopped=reason, complete=False, finished_epoch=self.now)
            atomic_json(history_path, history)
        return False

    def claim(self, r):
        from .production_runner import choose
        s = self.session(r)
        self.advance()
        if self.state['complete'] or any(self.stops().values()) or s['control']['drain']:
            return {'job': None, 'status': self.status()}
        phase = self.phase
        if phase not in s['chosen'] or s['ready'].get(phase) != self.snapshot(phase)['sha256']:
            return {'job': None, 'waiting': 'inputs or configuration', 'phase': phase}
        projection = self.check_projection()
        if projection is not True:
            return {'job': None, 'waiting': 'host configurations' if projection is None else None, 'status': self.status()}
        occupied = self.active(r['session'])
        limit = min(s['settings']['caps'][s['control']['mode']], s['control']['max_workers'])
        selected = choose(s['configuration'][phase], limit, s['settings']['cpu_budget'], 1)
        cap = selected['workers']
        if len(occupied) >= cap:
            return {'job': None, 'waiting': 'worker cap'}
        entry = self.member(r['host'])
        memory = min(float(r['memory_available_gb']) * .8,
                     entry['memory_gb'] * .8 - sum(l['memory_gb'] for l in occupied))
        observed = self.state.get('observed_memory_gb', {})
        job = self.store.candidate(phase, entry['kinds'], memory, observed)
        purpose = 'work'
        total, done = self.store.counts(phase)
        if job is None and total == done and not self.state['checks'].get(phase, {}).get('matched'):
            sample = self.jobs[self.state['sample_jobs'][phase]]
            participants = self.phase_hosts(phase)
            original = self.done[sample['id']]['host']
            leased = {l['job_id'] for l in self.active()}
            key, cost = self.store.cost(sample)
            if (sample['id'] not in leased and (len(participants) == 1 or original != r['host'])
                    and sample['kind'] in entry['kinds'] and max(cost['memory_gb'], observed.get(key,0)) <= memory):
                job, purpose = sample, 'check'
        if job is None:
            return {'job': None, 'waiting': 'jobs, cross-host check or memory'}
        token = uuid.uuid4().hex
        key, cost = self.store.cost(job)
        self.state['leases'][token] = {'host': r['host'], 'session': r['session'], 'job_id': job['id'], 'phase': phase,
            'start': self.now, 'expires': self.now + self.ttl, 'heartbeat': self.now, 'status': 'active',
            'purpose': purpose, 'memory_gb': max(cost['memory_gb'], observed.get(key,0))}
        return {'job': job, 'lease': token, 'expires': self.now + self.ttl, 'phase_root': str(self.root / phase), 'purpose': purpose}

    def claim_many(self, r):
        k = r.get('max_jobs', 1)
        if isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= 32:
            raise ValueError('claim batch must be between 1 and 32')
        claims, last = [], None
        remaining = float(r['memory_available_gb'])
        for _ in range(k):
            last = self.claim(dict(r, memory_available_gb=remaining))
            if not last.get('job'):
                break
            claims.append(last)
            # The .8 headroom applies once to the reported free memory. Each
            # provisional lease then consumes its full estimate within the batch.
            remaining -= self.state['leases'][last['lease']]['memory_gb'] / .8
        return {'claims': claims, 'status': self.status(), 'waiting': (last or {}).get('waiting')}

    def complete(self, r):
        from .compatibility_a10 import comparison_bytes
        from .production_runner import completed
        self.member(r['host'])
        l = self.state['leases'].get(r['lease'])
        if not l or l['host'] != r['host']:
            raise ValueError('unknown or wrong-host lease')
        if self.state['halt']:
            raise ValueError('launch halted')
        raw = base64.b64decode(r['data'], validate=True)
        if hashlib.sha256(raw).hexdigest() != r['sha256']:
            raise ValueError('corrupt output transfer')
        value = json.loads(raw)
        job = self.jobs[l['job_id']]
        if (value['job'] != job or value['code_hash'] != self.code or value.get('host') != r['host']
                or value.get('lease') != r['lease'] or value.get('result', {}).get('code_hash', self.code) != self.code
                or not positive(value.get('seconds'))):
            raise ValueError('output job, host, code or lease mismatch')
        # Handles a crash after output+record publication but before cache save.
        original = completed(self.root / l['phase'], job, self.code)
        if original is not None:
            self.done[job['id']] = {'host': original['host'], 'phase': l['phase']}
        matched = original is not None and comparison_bytes(job, original['result']) == comparison_bytes(job, value['result'])
        if original is not None and not matched:
            failure = {'job_id': job['id'], 'epoch': self.now, 'original_host': original['host'], 'other_host': r['host'],
                'original_sha256': hashlib.sha256(comparison_bytes(job, original['result'])).hexdigest(),
                'other_sha256': hashlib.sha256(comparison_bytes(job, value['result'])).hexdigest(), 'lease': r['lease']}
            atomic_json(self.root / 'nondeterminism_failure.json', seal(failure))
            self.state['halt'] = 'nondeterminism'
            self.state['complete'] = False
            history_path = self.root / 'launches.json'
            if history_path.exists():
                history = read(history_path)
                history[-1].update(complete=False, nondeterminism_halt_epoch=self.now)
                atomic_json(history_path, history)
            return {'accepted': False, 'halt': 'nondeterminism'}
        # Once the wall ceiling has passed, a first completion is never counted.
        # Late duplicates are still compared, including after a coordinator resume.
        if original is None and self.now >= self.state['started'] + self.spec['wall_seconds']:
            l['status'] = 'past_wall_ceiling'
            return {'accepted': False, 'reason': 'wall ceiling'}
        if original is None:
            output = self.root / l['phase'] / 'outputs' / (job['id'] + '.json')
            atomic_json(output, value)
            atomic_json(self.root / l['phase'] / 'records' / (job['id'] + '.json'),
                {'job': job, 'code_hash': self.code, 'status': 'complete', 'output_hash': file_hash(output),
                 'completed_epoch': self.now, 'worker_seconds': value['seconds'], 'host': r['host'], 'lease': r['lease']})
            self.done[job['id']] = {'host': r['host'], 'phase': l['phase']}
        elif l['status'] != 'completed':
            append(self.root, 'incidental_cross_checks', {'job_id': job['id'], 'original_host': original['host'],
                'other_host': r['host'], 'lease': r['lease'], 'matched': True, 'epoch': self.now})
        if l['status'] != 'completed':
            session = self.state['sessions'][l['session']]
            session['worker_seconds'] += value['seconds']
            session['last_work_end'] = self.now
            if session.get('end_reason') == 'coordinator resume':
                # A void lease may finish after the monitor restarts. Charge its
                # remaining possible interval, without overlapping a new join.
                next_join = min((s['joined'] for s in self.state['sessions'].values()
                                 if s['host'] == r['host'] and s['joined'] > session['joined']), default=self.now)
                session['end'] = max(session['end'], min(self.now, session['heartbeat'] + self.ttl, next_join))
        l['status'] = 'completed'
        l['finished'] = self.now
        peak = value.get('peak_rss_bytes')
        if positive(peak):
            key, _ = self.store.cost(job)
            observed = self.state.setdefault('observed_memory_gb', {})
            observed[key] = max(observed.get(key, 0), peak * 1.2 / 1e9)
        if l['purpose'] == 'check':
            participants = self.phase_hosts(l['phase'])
            if matched and (len(participants) == 1 or original['host'] != r['host']):
                check = {'checked': job['id'], 'matched': True, 'original_host': original['host'], 'recheck_host': r['host']}
                atomic_json(self.root / l['phase'] / 'nondeterminism_check.json', check)
                self.state['checks'][l['phase']] = check
        self.advance()
        return {'accepted': True, 'duplicate': original is not None, 'phase': self.phase,
                'status': self.status(), 'control': self.state['sessions'][l['session']]['control']}

    def request(self, r):
        op = r['op']
        if op == 'inspect':
            return {'status': self.status(), 'spec': self.store.full_spec()}
        if op == 'join':
            return self.join(r)
        if op == 'complete':
            return self.complete(r)
        if (self.state['complete'] or self.state.get('stop_reason')) and op in ('heartbeat', 'claim'):
            self.member(r['host'])
            return {'job': None, 'claims': [], 'phase': None, 'control': {'drain': True}, 'status': self.status()}
        s = self.session(r)
        if op == 'heartbeat':
            s['heartbeat'] = self.now
            if not self.stops()['coordinator']:
                for l in self.active(r['session']):
                    l.update(heartbeat=self.now, expires=self.now + self.ttl)
            return {'status': self.status(), 'control': s['control'], 'phase': self.phase}
        if op == 'inputs':
            return self.snapshot(r['phase'], r.get('configuration', False))
        if op == 'fetch':
            from .snapshot_a11 import fetch
            return fetch(self.snapshot(r['phase'], r.get('configuration', False)), r['path'], r.get('offset', 0))
        if op == 'configure':
            return self.configure(r)
        if op == 'configured':
            s['configuration_done'] = True
            return {'configured': True}
        if op == 'ready':
            if r['input_sha256'] != self.snapshot(r['phase'])['sha256']:
                raise ValueError('phase input snapshot mismatch')
            s['ready'][r['phase']] = r['input_sha256']
            return {'ready': True}
        if op == 'claim':
            execute = lambda: self.claim_many(r) if 'max_jobs' in r else self.claim(r)
            return self.store.replay_claim(r, execute) if 'request_id' in r else execute()
        if op == 'release':
            l = self.state['leases'].get(r['lease'])
            if not l or l['session'] != r['session']:
                raise ValueError('wrong lease release')
            if l['status'] == 'active':
                l['status'] = 'released'
                if r.get('reason') == 'worker failed':
                    failures = self.state.setdefault('failed_attempts', {})
                    failures[l['job_id']] = failures.get(l['job_id'], 0) + 1
                    if failures[l['job_id']] >= 3:
                        self.state['halt'] = 'job failed three times'
                        atomic_json(self.root / 'execution_failure.json', seal({'job_id': l['job_id'], 'epoch': self.now, 'reason': self.state['halt']}))
            append(self.root, 'protocol_events', {'event': 'release', 'host': r['host'], 'lease': r['lease'], 'reason': r.get('reason'), 'epoch': self.now})
            return {'released': True}
        if op == 'leave':
            if self.active(r['session']):
                raise ValueError('drain first; host still has leases')
            self.close(r['session'], self.now, 'left')
            return {'left': True}
        raise ValueError('unknown coordinator command')


def rpc(root, request, *, now=None, local_only=False):
    if request.get('op') not in {'join', 'claim', 'heartbeat', 'complete', 'release', 'leave', 'inspect', 'inputs', 'fetch', 'configure', 'configured', 'ready'}:
        raise ValueError('unknown coordinator command')
    # Source hashing reads only immutable checkout files. Do it before taking
    # the root lock; every request still compares the full running identity.
    current_code = code_identity()
    warm_connection(root)
    with transaction(root):
        if local_only:
            path = scoped(root) / 'launches.json'
            history = read(path) if path.exists() else []
            machine = platform.node()
            if not history or not history[-1].get('machine'):
                raise ValueError('local transport requires a recorded coordinator machine')
            if history[-1]['machine'] != machine or request.get('host', machine) != machine:
                raise ValueError('local transport host does not match the recorded coordinator machine')
        c = Coordinator(root, now, current_code)
        try:
            return c.request(request)
        finally:
            c.save()


def control(root, host=None, *, mode=None, max_workers=None, stop=None):
    with transaction(root):
        c = Coordinator(root)
        if host is None:
            if mode or max_workers:
                raise ValueError('pull mode and worker controls require --host')
            if stop is not None:
                c.state['control'].update(stop_dispatch=stop != 'clear', interrupt_now=stop == 'now')
        else:
            c.member(host)
            sessions = [s for s in c.state['sessions'].values() if s['host'] == host and s['end'] is None]
            if not sessions:
                raise ValueError('host is not joined')
            for s in sessions:
                if mode:
                    if mode not in ('normal', 'work'):
                        raise ValueError('invalid mode')
                    s['control']['mode'] = mode
                if max_workers is not None:
                    if max_workers < 1:
                        raise ValueError('positive worker cap required')
                    s['control']['max_workers'] = min(max_workers, s['settings']['caps'][s['control']['mode']])
                if stop:
                    s['control']['drain'] = stop != 'clear'
                    s['control']['interrupt_now'] = stop == 'now'
                c.state.setdefault('host_controls', {})[host] = dict(s['control'])
        append(c.root, 'protocol_events', {'event': 'control', 'host': host, 'mode': mode, 'max_workers': max_workers, 'stop': stop, 'epoch': c.now})
        c.save(force=True)
        return c.status()


def coordinate(spec_path, root, settings):
    prepare(spec_path, root, settings)
    with lease(Path(root) / 'coordinator.lock'):
        with transaction(root):
            c = Coordinator(root)
            c.start()
            c.state.update(monitor_required=True, monitor_epoch=c.now)
            c.save()
            history = read(Path(root) / 'launches.json') if (Path(root) / 'launches.json').exists() else []
            history.append({'epoch': c.now, 'machine': platform.node(), 'settings': settings,
                            'code_hash': c.code, 'pull': True, 'complete': False})
            atomic_json(Path(root) / 'launches.json', history)
        try:
            last_checkpoint = time.monotonic()
            while True:
                with transaction(root):
                    c = Coordinator(root)
                    c.state['monitor_epoch'] = c.now
                    c.advance()
                    if not any(c.stops().values()):
                        c.check_projection()
                    c.save()
                    status = c.status()
                    stopped = any(c.stops().values())
                    if c.state['halt'] or c.state['complete'] or c.state.get('stop_reason') or (stopped and not c.active()):
                        break
                    if c.now >= c.state['started'] + c.spec['wall_seconds']:
                        break
                if time.monotonic() - last_checkpoint >= 30:
                    from .dispatch_store_a11 import checkpoint
                    checkpoint(root)
                    last_checkpoint = time.monotonic()
                time.sleep(1)
        finally:
            with transaction(root):
                c = Coordinator(root)
                c.save()
                history[-1].update(complete=c.state['complete'] and not c.state['halt'], finished_epoch=c.now, status=c.status(), reason=c.state.get('stop_reason'), stopped=c.state.get('stop_reason'))
                atomic_json(Path(root) / 'launches.json', history)
        return status


def main():
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest='command', required=True)
    s = commands.add_parser('freeze'); s.add_argument('spec'); s.add_argument('projection'); s.add_argument('output')
    s.add_argument('--code-commit', required=True); s.add_argument('--extra-input', action='append', default=[])
    s.add_argument('--lease-seconds', type=float, default=120)
    s = commands.add_parser('rpc'); s.add_argument('root'); s.add_argument('--stream', action='store_true')
    s.add_argument('--local', action='store_true', help='require the recorded coordinator machine on every request')
    s = commands.add_parser('prepare'); s.add_argument('spec'); s.add_argument('root')
    s = commands.add_parser('approve'); s.add_argument('root'); s.add_argument('evidence')
    s.add_argument('--operator', required=True); s.add_argument('--when', required=True)
    args = p.parse_args()
    if args.command == 'freeze':
        document = seal(freeze(unseal(read(args.spec)), read(args.projection), code_commit=args.code_commit,
                               extra_inputs=args.extra_input, lease_seconds=args.lease_seconds))
        if Path(args.output).exists() and read(args.output) != document:
            raise ValueError('frozen pull spec already exists')
        atomic_json(args.output, document)
        print({'sha256': file_hash(args.output), 'jobs': len(document['payload']['jobs'])})
    elif args.command == 'approve':
        print(approve_host(args.root, read(args.evidence), args.operator, args.when))
    elif args.command == 'prepare':
        prepare(args.spec, args.root, {'profile': 'local', 'cpu_budget': 1, 'workers': 1, 'threads': 1, 'mode': 'work'})
        print('prepared; no work dispatched')
    else:
        def respond(request):
            try:
                result = rpc(args.root, request, local_only=args.local)
                response = {'ok': True, 'result': result}
            except Exception as exc:
                response = {'ok': False, 'error': str(exc), 'type': type(exc).__name__}
            sys.stdout.buffer.write(canonical(response) + b'\n')
            sys.stdout.buffer.flush()
            return response['ok']
        if args.stream:
            for line in sys.stdin.buffer:
                respond(json.loads(line))
        elif not respond(json.load(sys.stdin)):
            raise SystemExit(1)


if __name__ == '__main__':
    main()
