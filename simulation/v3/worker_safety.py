"""Executor-only Linux preflight and isolated, restartable spawn pools."""
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
import multiprocessing as mp
import os
from pathlib import Path
import platform
import json
import sys
import time
import uuid

from .artifacts import atomic_json, read, scoped

MAX_RERUNS = 3
MIN_X2_SWAP_FREE_BYTES = 16_000_000_000


def metadata_failure(path, exc):
    """Diagnostics must not replace the outcome, even if stderr is unavailable."""
    record = dict(event='executor_metadata_write_failed', path=str(path),
                  error_class=type(exc).__name__, error=str(exc), epoch=time.time())
    try:
        print(json.dumps(record, sort_keys=True), file=sys.stderr, flush=True)
    except (OSError, ValueError):
        pass
    return record


def best_effort(path, action):
    """Two bounded attempts for informational side files; report every miss."""
    for attempt in range(2):
        try:
            action()
            return True
        except (OSError, ValueError) as exc:
            metadata_failure(path, exc)
            if attempt == 0:
                time.sleep(.01)
    return False


def metadata_json(path, value, *, writer=None):
    return best_effort(path, lambda: (writer or atomic_json)(path, value))


def persist_restarts(path, events, *, writer=None):
    """Pause resubmission until its durable rerun bound is saved.

    I/O failure alone never spends a proof. There is no timeout: continuing
    without this journal could reset the bound after resume. An operator
    interruption retains the existing interruption/finality semantics.
    """
    attempt = 0
    while True:
        try:
            (writer or atomic_json)(path, events)
            return
        except (OSError, ValueError) as exc:
            if attempt == 0 or attempt % 30 == 0:
                metadata_failure(path, exc)
            attempt += 1
            time.sleep(1.)


def prefer_worker_oom():
    """Call only in the simulation child, never in a supervisor."""
    record = dict(pid=os.getpid(), epoch=time.time(), applicable=platform.system() == 'Linux',
                  requested=1000, success=False)
    if mp.parent_process() is None:
        record['skipped'] = 'not a spawned simulation worker'
        return record
    if record['applicable']:
        try:
            path = Path('/proc/self/oom_score_adj')
            path.write_text('1000', encoding='ascii')
            record['success'] = path.read_text(encoding='ascii').strip() == '1000'
        except OSError as exc:
            record['error'] = str(exc)
    return record


def swap_status():
    values = {}
    if platform.system() == 'Linux':
        for line in Path('/proc/meminfo').read_text().splitlines():
            key, _, value = line.partition(':')
            if key in ('SwapTotal', 'SwapFree'):
                values[key] = int(value.split()[0]) * 1024
    return dict(total_bytes=values.get('SwapTotal'), free_bytes=values.get('SwapFree'))


def swap_preflight(settings, path):
    value = dict(epoch=time.time(), profile=settings['profile'], **swap_status())
    value['required_free_bytes'] = MIN_X2_SWAP_FREE_BYTES if settings['profile'] == 'x2' else 0
    value['passed'] = (settings['profile'] != 'x2' or
                       value['free_bytes'] is not None and value['free_bytes'] >= value['required_free_bytes'])
    metadata_json(path, value)
    if not value['passed']:
        raise ValueError('X2 launch requires at least 16 GB swap free')
    return value


def killed_signal(exitcode):
    # POSIX multiprocessing reports -signal. Windows can emulate that exit
    # status in synthetic tests; normal Windows exception codes are not signals.
    if exitcode is not None and -64 < exitcode < 0:
        return -exitcode
    return None


def restart(events, job, signal, reason='worker killed by signal; restart from original seed'):
    count = sum(e['job'] == job for e in events) + 1
    event = dict(epoch=time.time(), job=job, signal=signal, reason=reason, rerun=count,
                 allowed=count <= MAX_RERUNS)
    events.append(event)
    return event


def require_retry_budget(events, job):
    if sum(e['job'] == job for e in events) > MAX_RERUNS:
        raise RuntimeError('worker exhausted three signal reruns')


class KilledWorker(RuntimeError):
    def __init__(self, signal):
        super().__init__('simulation worker killed by signal %s' % signal)
        self.signal = signal


def _returned(path, function, args):
    oom = prefer_worker_oom()
    metadata_json(Path(path).with_suffix('.oom.json'), oom)
    result = function(*args)
    # A returned value survives a pool transport failure and is never rerun.
    atomic_json(path, dict(value=result, oom_score_adj=oom))
    return result


class IsolatedPools:
    """One single-use spawn executor per admitted job.

    A signal breaks only that job's pool. The scheduler rebuilds that pool on
    resubmission, after memory admission, leaving other in-flight jobs intact.
    Durable return journals distinguish a lost transport from absent results.
    """
    def __init__(self, root):
        self.root = scoped(Path(root) / uuid.uuid4().hex)
        self.active = {}

    def submit(self, function, *args):
        path = self.root / (uuid.uuid4().hex + '.json')
        pool = ProcessPoolExecutor(max_workers=1, mp_context=mp.get_context('spawn'), max_tasks_per_child=1)
        future = pool.submit(_returned, str(path), function, args)
        self.active[future] = (pool, path, list(pool._processes.values()))
        return future

    def result(self, future):
        pool, path, children = self.active.pop(future)
        try:
            try:
                return future.result()
            except BrokenProcessPool:
                if path.exists():
                    return read(path)['value']
                signals = [killed_signal(p.exitcode) for p in children]
                if any(signals):
                    raise KilledWorker(next(s for s in signals if s)) from None
                raise  # Startup/serialization/non-signal failures remain failures.
        finally:
            pool.shutdown(wait=True, cancel_futures=True)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        for pool, _, children in self.active.values():
            for process in children:
                if process.is_alive(): process.terminate()
            pool.shutdown(wait=True, cancel_futures=True)
