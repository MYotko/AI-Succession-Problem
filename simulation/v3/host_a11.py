"""A11 worker host. Explicit SSH or local stdio; never publishes a root."""
import argparse
import base64
from contextlib import contextmanager
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import platform
import queue
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
import traceback
import uuid
from .artifacts import (ROOT, SIMULATION, atomic_json, canonical, code_identity, configure_threads,
                        digest, input_view, lease, read, runtime, scoped, source_manifest, unseal)
from .worker_safety import metadata_json


class Rejected(RuntimeError):
    """Coordinator replied, but refused the operation. This is not a timeout."""


class Stdio:
    """Shared framing and process lifetime for both explicit transports."""
    def __init__(self, argv, *, cwd=None, timeout=20, label):
        self.argv, self.cwd, self.timeout, self.label = argv, cwd, timeout, label
        self._lock = threading.Lock()
        self._process = None
        self._responses = None

    def _start(self):
        options = dict(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if self.cwd is not None:
            options['cwd'] = self.cwd
        self._process = subprocess.Popen(self.argv, **options)
        self._responses = queue.Queue()
        process, responses = self._process, self._responses
        def reader():
            try:
                for line in iter(process.stdout.readline, b''):
                    responses.put(line)
            finally:
                responses.put(None)
        threading.Thread(target=reader, daemon=True).start()

    def _close(self):
        if self._process is not None:
            if self._process.poll() is None:
                self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill(); self._process.wait()
            self._process.stdin.close(); self._process.stdout.close()
            self._process = None

    def close(self):
        with self._lock:
            self._close()

    def call(self, request):
        # One host's heartbeats and claims share a framed stdio stream. A
        # reconnect starts a new command, never a listener or coordinator service.
        with self._lock:
            if self._process is None or self._process.poll() is not None:
                self._close(); self._start()
            try:
                self._process.stdin.write(canonical(request) + b'\n')
                self._process.stdin.flush()
                line = self._responses.get(timeout=self.timeout)
                if line is None:
                    raise ConnectionError(self.label + ' coordinator command ended')
                response = json.loads(line)
            except (OSError, ValueError, queue.Empty) as exc:
                self._close()
                raise ConnectionError(self.label + ' coordinator unavailable') from exc
            if not response['ok']:
                raise Rejected(response['error'])
            return response['result']


class SSH(Stdio):
    def __init__(self, target, checkout, root, timeout=20):
        if target.startswith('-') or any(x in target for x in ('\n', '\r')):
            raise ValueError('invalid SSH destination')
        self.target = target
        # A fixed executable command with quoted paths. The operation and all
        # untrusted values travel as JSON on stdin, never as shell fragments.
        self.command = ('cd ' + shlex.quote(checkout + '/simulation') +
            ' && export PATH="$HOME/miniforge3/envs/phaseb/bin:$HOME/.local/bin:$PATH" && '
            '"$HOME/miniforge3/envs/phaseb/bin/python3.13" -B -m v3.multihost_a11 rpc ' + shlex.quote(root) + ' --stream')
        super().__init__(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', target, self.command],
                         timeout=timeout, label='SSH')


class Local(Stdio):
    def __init__(self, root, timeout=20):
        root = scoped(SIMULATION / root)
        super().__init__([sys.executable, '-B', '-m', 'v3.multihost_a11', 'rpc', str(root), '--stream', '--local'],
                         cwd=SIMULATION, timeout=timeout, label='local')


class Loopback:
    """Same transactions as SSH, with separate host scratch directories."""
    def __init__(self, root, clock=None):
        self.root, self.clock, self.connected = root, clock, True

    def call(self, request):
        from .multihost_a11 import rpc
        if not self.connected:
            raise ConnectionError('loopback network drop')
        try:
            return rpc(self.root, request, now=self.clock() if self.clock else None)
        except (ValueError, RuntimeError) as exc:
            raise Rejected(str(exc)) from exc


def fingerprint():
    configure_threads(1)
    info = runtime(1)
    import numpy as np
    core = np._core._multiarray_umath
    conda = os.environ.get('CONDA_EXE') or shutil.which('conda') or str(Path.home() / 'miniforge3/bin/conda')
    packages = json.loads(subprocess.run([conda, 'list', '--prefix', sys.prefix, '--json'], check=True, capture_output=True).stdout)
    normalized = sorted([{k: p.get(k) for k in ('name', 'version', 'build_string', 'channel')}
                         for p in packages], key=lambda p: p['name'])
    return {'python': info['python'], 'numpy': info['numpy'],
            'numpy_cpu_baseline': list(core.__cpu_baseline__), 'numpy_cpu_dispatch': list(core.__cpu_dispatch__),
            'numpy_cpu_features': dict(core.__cpu_features__), 'conda_packages_sha256': digest(normalized),
            'threads_configured': 1, 'threads_verified': info['threads_verified']}


def verify_commit(commit):
    # Record-only commits may follow the implementation commit, as A11 item 2
    # explicitly allows. All source-manifest bytes must still match that commit.
    for name, expected in source_manifest().items():
        data = subprocess.run(['git', '-C', str(SIMULATION.parent), 'show', commit + ':simulation/' + name],
                              check=True, capture_output=True).stdout
        if hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest() != expected:
            raise ValueError('implementation commit differs from running source: ' + name)


def execute_scratch(target, job, code, phase_root, view, registered, registration, host, token, a13_checkpoints=None, a13_recheck=False, a14_checkpoints=None):
    """Spawn target: ordinary execute path, one output blob, no completion record."""
    from .production_runner import execute, peak_rss_bytes
    configure_threads(1)
    target = scoped(target)
    from .worker_safety import prefer_worker_oom
    oom = prefer_worker_oom()
    metadata_json(target.with_suffix('.oom.json'), oom)
    try:
        if code_identity() != code:
            raise ValueError('worker source changed')
        info = runtime(1)
        before, epoch = time.perf_counter(), time.time()
        with input_view(view):
            if job['kind'] == 'a13_validate_plain_ext':
                from .validation_extension_a13 import checkpoint_context
                with checkpoint_context(target.with_suffix('.a13'), a13_checkpoints or [], recheck=a13_recheck):
                    result = execute(job, registered, registration, root=Path(phase_root))
            elif job['kind'] == 'a14_validate_plain_ext2':
                from .validation_extension_a14 import checkpoint_context
                with checkpoint_context(target.with_suffix('.a14'), a14_checkpoints or [], recheck=a13_recheck):
                    result = execute(job, registered, registration, root=Path(phase_root))
            else:
                result = execute(job, registered, registration, root=Path(phase_root))
        atomic_json(target, {'job': job, 'code_hash': code, 'runtime': info, 'result': result,
            'seconds': time.perf_counter() - before, 'started_epoch': epoch, 'finished_epoch': time.time(),
            'peak_rss_bytes': peak_rss_bytes(), 'oom_score_adj': oom, 'host': host, 'lease': token})
    except BaseException as exc:
        from .validation_extension_a13 import ScientificHalt
        from .continuation_validation import OutOfRange
        if job['kind'] == 'a13_validate_plain_ext' and isinstance(exc, (ScientificHalt, OutOfRange)):
            atomic_json(target.with_suffix('.scientific_halt.json'), {'scientific_halt': True})
        if job['kind'] == 'a14_validate_plain_ext2' and isinstance(exc, (ScientificHalt, OutOfRange)):
            atomic_json(target.with_suffix('.scientific_halt.json'), {'scientific_halt': True, 'round': 2})
        metadata_json(target.with_suffix('.failure.json'), {'job_id': job['id'], 'traceback': traceback.format_exc(),
                    'target': str(target), 'resolved_target': str(target.resolve()), 'scope_root': str(ROOT)})
        raise


class Client:
    def __init__(self, transport, host, session, ttl):
        self.transport, self.host, self.session, self.ttl = transport, host, session, ttl
        self.last_contact = time.monotonic()
        self.stop = threading.Event()
        self.lost = threading.Event()
        self.latest = {}
        self.error = None

    def call(self, op, **fields):
        started = time.monotonic()
        if op in ('heartbeat', 'ready'):
            from .production_runner import mem_available_bytes
            available = mem_available_bytes()
            if available is not None:
                fields['memory_available_gb'] = available / 1e9
        request = {'op':op,'host':self.host,'session':self.session,**fields}
        if op == 'claim':
            request['request_id'] = uuid.uuid4().hex
        while not self.lost.is_set():
            try:
                result = self.transport.call(request)
                self.last_contact = time.monotonic()
                return result
            except (OSError, subprocess.TimeoutExpired):
                if time.monotonic() - self.last_contact >= self.ttl or time.monotonic() - started >= self.ttl:
                    self.lost.set()
                else:
                    self.stop.wait(min(.2, self.ttl / 6))
        raise ConnectionError('coordinator lease contact lost; host stopped')

    def watch(self, scratch):
        while not self.stop.wait(self.ttl / 3):
            try:
                self.latest = self.call('heartbeat')
                control = self.latest.get('control', {})
                status = self.latest.get('status', {})
                path = scratch / 'control.json'
                current = read(path) if path.exists() else {}
                atomic_json(path, current | control | dict(stop_dispatch=bool(control.get('drain') or any(status.get('stops', {}).values()))))
                if control.get('interrupt_now') or status.get('halt') or status.get('hard_stop'):
                    self.lost.set()
            except Rejected as exc:
                self.error = exc
                self.lost.set()
            except (OSError, subprocess.TimeoutExpired):
                if time.monotonic() - self.last_contact >= self.ttl:
                    self.lost.set()
            if self.lost.is_set():
                # Existing configuration dispatcher sees this control and
                # terminates its children. Scientific children are stopped below.
                atomic_json(scratch / 'control.json', {'mode': 'work', 'max_workers': 1,
                    'stop_dispatch': True, 'interrupt_now': True})
                return


def synchronize(client, scratch, phase, configuration=False):
    from .snapshot_a11 import receive
    document = client.call('inputs', phase=phase, configuration=configuration)
    return receive(document, scratch / 'snapshots', lambda path, offset: client.call('fetch', phase=phase,
        configuration=configuration, path=path, offset=offset))


def run_host(transport, scratch, settings, *, host=None, environment=None, service=None, max_seconds=None):
    """Production uses platform.node/fingerprint. Tests inject loopback identities."""
    from .production_runner import configuration_test, caps, mem_available_bytes, available_cpus, choose
    scratch = scoped(scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    if (host is not None or environment is not None) and not isinstance(transport, Loopback):
        raise ValueError('host identity injection is loopback only')
    host = host or platform.node()
    environment = environment or fingerprint()
    from . import worker_control as wc
    settings = wc.settings(settings)
    if settings['cpu_budget'] > available_cpus() or settings['threads'] != 1:
        raise ValueError('worker CPU or thread budget invalid')
    from .worker_safety import swap_preflight, killed_signal
    swap = swap_preflight(settings, scratch / 'swap_preflight.json')
    spec = transport.call({'op': 'inspect'})['spec']
    if not isinstance(transport, Loopback):
        verify_commit(spec['pull_dispatch']['code_commit'])
    joined = transport.call({'op': 'join', 'host': host, 'fingerprint': environment, 'code_hash': code_identity(),
        'code_commit': spec['pull_dispatch']['code_commit'], 'settings': settings, 'service': service, 'swap': swap})
    client = Client(transport, host, joined['session'], joined['lease_seconds'])
    heartbeat = threading.Thread(target=client.watch, args=(scratch,), daemon=True)
    atomic_json(scratch / 'control.json', dict(mode=settings['mode'], max_workers=settings['workers'],
        stop_dispatch=False, interrupt_now=False) | joined.get('control', {}))
    heartbeat.start()
    active, views, measurements_by_phase = {}, {}, {}
    context = mp.get_context('spawn')
    started = time.monotonic()
    error = None
    try:
        metadata_json(scratch / 'host_session.json', {'host': host, 'session': joined['session'], 'code_hash': code_identity(), 'settings': settings})
        # Run all phase profiles on join, just as the existing runner does.
        # Inputs for configuration plain validation are self-contained.
        deadline = min(time.time() + spec.get('configuration_seconds', 900),
                       time.time() + (max_seconds or spec['wall_seconds']))
        for phase, profile in spec['configuration'].items():
            if profile['kind'] not in joined['qualified_kinds']:
                metadata_json(scratch / 'configuration_skipped' / (phase + '.json'), {'reason': 'job kind not qualified'})
                continue
            if phase == 'validate_plain' and 'fit' not in measurements_by_phase:
                metadata_json(scratch / 'configuration_skipped' / (phase + '.json'), {'reason': 'plain projection requires measured fit configuration'})
                continue
            view = synchronize(client, scratch, phase, True)
            measurements = configuration_test(scratch, phase, profile, settings, deadline, joined['session'],
                                               input_snapshot=view, job_resources=wc.resources(spec), source_jobs=spec['jobs'], memory_spec=spec)
            client.call('configure', phase=phase, measurements=measurements, input_sha256=view['snapshot_sha256'])
            measurements_by_phase[phase] = measurements
        client.call('configured')
        if not measurements_by_phase:
            raise RuntimeError('no qualified phase fits this host; no scientific jobs taken')
        while not client.lost.is_set():
            for token, (process, target, claim) in list(active.items()):
                if claim['job']['kind'] == 'a14_validate_plain_ext2' and claim['purpose'] == 'work':
                    sent = claim.setdefault('_a14_sent', set())
                    for checkpoint in sorted(target.with_suffix('.a14').glob('*.json')):
                        if checkpoint.name not in sent:
                            client.call('a14_checkpoint', lease=token, checkpoint=read(checkpoint))
                            sent.add(checkpoint.name)
                if claim['job']['kind'] == 'a13_validate_plain_ext' and claim['purpose'] == 'work':
                    sent = claim.setdefault('_a13_sent', set())
                    for checkpoint in sorted(target.with_suffix('.a13').glob('*.json')):
                        if checkpoint.name not in sent:
                            client.call('a13_checkpoint', lease=token, checkpoint=read(checkpoint))
                            sent.add(checkpoint.name)
                if process.is_alive():
                    continue
                process.join()
                if not target.exists() and killed_signal(process.exitcode):
                    reply = client.call('release', lease=token, reason='worker signal kill', signal=killed_signal(process.exitcode))
                    del active[token]
                    if reply.get('halt'): raise RuntimeError('worker exhausted three signal reruns')
                    continue  # A fresh claim performs both memory guards again.
                if (process.exitcode and not killed_signal(process.exitcode)) or not target.exists():
                    if target.with_suffix('.scientific_halt.json').exists():
                        if claim['job']['kind'] == 'a14_validate_plain_ext2':
                            client.call('a14_halt', lease=token)
                        else:
                            client.call('a13_halt', lease=token)
                    client.call('release', lease=token, reason='worker failed')
                    failure_path = target.with_suffix('.failure.json')
                    detail = read(failure_path).get('traceback', '') if failure_path.exists() else 'no child failure record'
                    raise RuntimeError('remote worker failed: ' + claim['job']['id'] + '\n' + detail)
                raw = target.read_bytes()
                reply = client.call('complete', lease=token, sha256=hashlib.sha256(raw).hexdigest(), data=base64.b64encode(raw).decode('ascii'))
                del active[token]
                if 'status' in reply:
                    client.latest = reply
                if reply.get('halt'):
                    raise RuntimeError('coordinator recorded nondeterminism')
            status = client.latest.get('status', {})
            if not status:
                client.latest = client.call('heartbeat')
                status = client.latest['status']
            if status.get('complete') or status.get('halt'):
                break
            control = client.latest.get('control', {})
            stopping = any(status.get('stops', {}).values()) or control.get('drain')
            if max_seconds is not None and time.monotonic() - started >= max_seconds:
                stopping = True
            if stopping and not active:
                client.call('leave')
                break
            phase = client.latest.get('phase')
            if phase and not active and not any(p in measurements_by_phase for p in spec['phases'][spec['phases'].index(phase):]):
                client.call('leave')
                break
            if phase and not stopping:
                if phase not in measurements_by_phase:
                    time.sleep(min(1., client.ttl / 6))
                    continue
                if phase not in views:
                    views[phase] = synchronize(client, scratch, phase)
                    client.call('ready', phase=phase, input_sha256=views[phase]['snapshot_sha256'])
                slots = wc.profile_slots(settings, control, phase,
                    [claim['job']['config']['phase'] for _, _, claim in active.values()], measurements_by_phase[phase])
                if not slots:
                    time.sleep(.1)
                    continue  # Pull only when a measured worker slot is free.
                available = mem_available_bytes()
                if available is None:
                    raise RuntimeError('cannot measure host memory headroom')
                reply = client.call('claim', memory_available_gb=available / 1e9,
                                    max_jobs=min(32, slots))
                if 'status' in reply:
                    client.latest['status'] = reply['status']
                    client.latest['phase'] = reply['status']['phase']
                for claim in reply['claims']:
                    token = claim['lease']
                    target = scratch / 'unpublished' / (token + '.json')
                    process = context.Process(target=execute_scratch, args=(str(target), claim['job'], spec['code_hash'],
                        claim['phase_root'], views[claim['job']['config']['phase']], spec['registered'], spec.get('registration'), host, token,
                        claim.get('a13_checkpoints'), claim['purpose'] == 'check', claim.get('a14_checkpoints')))
                    process.start()
                    active[token] = (process, target, claim)
                if reply['claims']:
                    continue
                # A memory/qualification/barrier wait must not flood SSH with
                # requests. Heartbeats remain independent of this backoff.
                time.sleep(min(1., client.ttl / 6))
            time.sleep(.1)
        if client.lost.is_set():
            # A normal completion closes all sessions before their next heartbeat.
            try:
                final = transport.call({'op': 'inspect'})['status']
            except (OSError, Rejected, subprocess.TimeoutExpired):
                final = {}
            if not final.get('complete'):
                raise ConnectionError('worker stopped after coordinator contact/session loss')
    except BaseException as exc:
        error = exc
    finally:
        for process, _, _ in active.values():
            if process.is_alive():
                process.terminate()
            process.join()
        client.stop.set()
        heartbeat.join(timeout=min(30, client.ttl))
        try:
            if not client.lost.is_set():
                for token in active:
                    client.call('release', lease=token, reason='host stopping; restart from seed')
                client.call('leave')
        except (OSError, Rejected, subprocess.TimeoutExpired):
            pass  # Coordinator expiry is authoritative; no local completion.
        if hasattr(transport, 'close'):
            transport.close()
        metadata_json(scratch / 'host_exit.json', {'host': host, 'epoch': time.time(), 'error': repr(error) if error else None,
                                               'unpublished_inflight': list(active), 'contact_lost': client.lost.is_set()})
    if error:
        raise error
    return {'host': host, 'stopped': True}


@contextmanager
def host_service(scratch, profile, model_service=None):
    from .service import command, model_service as selected_service, without_service
    settings = dict(profile=profile)
    if model_service is not None:
        settings['model_service'] = model_service
    selected = selected_service(settings)
    if profile == 'x2' and platform.system() != 'Linux':
        raise ValueError('X2 worker profile requires Linux')
    if selected == 'none':
        with without_service(scratch) as record:
            yield record
        return
    with lease(ROOT / 'service.lock'):
        record = {'host': platform.node(), 'model_service': selected,
                  'started_epoch': time.time(), 'down_exit_code': None, 'up_exit_code': None}
        def interrupt(number, frame):
            raise KeyboardInterrupt('worker supervisor interrupted')
        previous = {s: signal.signal(s, interrupt) for s in (signal.SIGINT, signal.SIGTERM)}
        try:
            record['down_exit_code'] = command(scratch, 'down')
            metadata_json(scratch / 'service.json', record)
            if record['down_exit_code']:
                raise RuntimeError('llm down failed')
            yield record
        finally:
            for s in previous:
                signal.signal(s, signal.SIG_IGN)
            try:
                record['up_exit_code'] = command(scratch, 'up')
                record['finished_epoch'] = time.time()
                metadata_json(scratch / 'service.json', record)
                if record['up_exit_code']:
                    raise RuntimeError('llm up failed; operator must restore it')
            finally:
                for s, handler in previous.items():
                    signal.signal(s, handler)


def main():
    from . import worker_control as wc
    p = argparse.ArgumentParser(description=__doc__)
    transport = p.add_mutually_exclusive_group(required=True)
    transport.add_argument('--coordinator')
    transport.add_argument('--local', action='store_true', help='use a child RPC process on the recorded coordinator machine')
    p.add_argument('--checkout')
    p.add_argument('--root', required=True); p.add_argument('--scratch', required=True)
    p.add_argument('--profile', choices=('local', 'x2'), required=True)
    p.add_argument('--model-service', choices=('llm', 'none'), help='default llm for X2, none for local')
    p.add_argument('--workers', type=int, required=True); p.add_argument('--cpu-budget', type=int, required=True)
    p.add_argument('--mode', choices=('normal', 'work'))
    wc.options(p)
    args = p.parse_args()
    args.mode = args.mode or ('normal' if args.profile == 'x2' else 'work')
    if args.local and args.checkout is not None:
        p.error('--local uses the current checkout; omit --checkout')
    if not args.local and not args.checkout:
        p.error('--checkout is required with --coordinator')
    configure_threads(1)
    scratch = scoped(args.scratch); scratch.mkdir(parents=True, exist_ok=True)
    settings = {'profile': args.profile, 'workers': args.workers, 'cpu_budget': args.cpu_budget, 'threads': 1, 'mode': args.mode, **wc.arguments(args)}
    settings = wc.settings(settings)
    from .service import model_service
    if args.model_service is not None:
        settings['model_service'] = args.model_service
    settings['model_service'] = model_service(settings)
    with lease(scratch / 'host.lock'), host_service(scratch, args.profile, settings['model_service']) as service:
        selected = Local(args.root) if args.local else SSH(args.coordinator, args.checkout, args.root)
        try:
            print(run_host(selected, scratch, settings, service=service))
        finally:
            selected.close()


if __name__ == '__main__':
    main()
