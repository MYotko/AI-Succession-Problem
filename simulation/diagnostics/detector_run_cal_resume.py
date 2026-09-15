"""Operational resumption after the operator-authorized Windows I/O test.

The pinned executor, recorder, model, detector, plan, and calibration code remain
unchanged. This layer changes bounded JSON-read and atomic-replace retries and
child launch routing only. It is recorded separately in execution metadata.
"""
import sys
sys.dont_write_bytecode = True
import detector_run_cal_executor as h
import threading

SELF = h.Path(__file__).resolve()
SELF_HASH = h.sha(h.lf(SELF.read_bytes()))
ORIGINAL_WRITE = h.write
ORIGINAL_METADATA = h.metadata
ORIGINAL_PINS = h.pins


def operation_record(event):
    row = {'utc': h.now(), 'pid': h.os.getpid(), **event}
    name = h.P + 'io_events_' + str(h.os.getpid()) + '.jsonl'
    with (h.OUT / name).open('a', encoding='utf-8', newline='\n') as f:
        f.write(h.json.dumps(row, ensure_ascii=True, default=h.encode) + '\n')
        f.flush()
        h.os.fsync(f.fileno())


def open_read_retry(path, timeout=5.0):
    started = h.time.monotonic()
    errors = []
    while True:
        try:
            handle = path.open('r', encoding='utf-8')
            if errors:
                operation_record({'event': 'read_retry_succeeded', 'path': str(path),
                                  'error_count': len(errors), 'errors': errors,
                                  'elapsed_seconds': h.time.monotonic() - started})
            return handle
        except PermissionError as error:
            code = getattr(error, 'winerror', None)
            if code not in (5, 32, 33) and not (code is None and error.errno == 13):
                raise
            errors.append({'winerror': code, 'errno': error.errno})
            if h.time.monotonic() - started >= timeout:
                operation_record({'event': 'read_retry_exhausted', 'path': str(path),
                                  'errors': errors, 'timeout_seconds': timeout})
                raise
            h.time.sleep(0.025)


def read_json_retry(name):
    with open_read_retry(h.OUT / name) as handle:
        return h.json.load(handle)


def replace_with_retry(source, destination, timeout=5.0):
    started = h.time.monotonic()
    errors = []
    while True:
        try:
            h.os.replace(source, destination)
            if errors:
                operation_record({'event': 'replace_retry_succeeded', 'destination': str(destination),
                                  'winerrors': errors, 'elapsed_seconds': h.time.monotonic() - started})
            return len(errors)
        except PermissionError as error:
            code = getattr(error, 'winerror', None)
            if code not in (5, 32, 33):
                raise
            errors.append(code)
            if h.time.monotonic() - started >= timeout:
                operation_record({'event': 'replace_retry_exhausted', 'destination': str(destination),
                                  'winerrors': errors, 'timeout_seconds': timeout})
                raise
            h.time.sleep(0.025)


def durable_write(name, obj):
    if name.endswith(('_initial.json', '_complete.json')) and isinstance(obj, dict):
        obj = {**obj, 'operational_layer': {'path': SELF.relative_to(h.ROOT).as_posix(),
                                          'sha256_lf': SELF_HASH}}
    payload = h.json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=True,
                          allow_nan=False, default=h.encode) + '\n'
    temp = h.OUT / (name + '.' + str(h.os.getpid()) + '.tmp')
    with temp.open('w', encoding='utf-8', newline='\n') as f:
        f.write(payload)
        f.flush()
        h.os.fsync(f.fileno())
    replace_with_retry(temp, h.OUT / name)


def operational_pins():
    if h.sha(h.lf(SELF.read_bytes())) != SELF_HASH:
        raise RuntimeError('Operational resumption source changed')
    return ORIGINAL_PINS()


def operational_metadata(np):
    result = ORIGINAL_METADATA(np)
    result['operational_layer'] = {'path': SELF.relative_to(h.ROOT).as_posix(),
                                   'sha256_lf': SELF_HASH}
    return result


def operational_spawn(job, arm=None, seed=None, attempt=1):
    cmd = [sys.executable, '-B', str(SELF), 'worker', '--job', job, '--attempt', str(attempt)]
    if arm is not None:
        cmd += ['--arm', arm, '--seed', str(seed)]
    return h.subprocess.Popen(cmd, cwd=h.ROOT, stdin=h.subprocess.DEVNULL,
                              stdout=h.subprocess.DEVNULL, stderr=h.subprocess.DEVNULL)


def install():
    h.read = read_json_retry
    h.write = durable_write
    h.pins = operational_pins
    h.metadata = operational_metadata
    h.spawn = operational_spawn


def test_io():
    h.pins()
    name = h.P + 'io_test_target.json'
    target = h.OUT / name
    h.write(name, {'version': 0})
    baseline_error = None
    with target.open('rb') as held:
        try:
            ORIGINAL_WRITE(name, {'version': 1})
        except PermissionError as error:
            baseline_error = {'winerror': error.winerror, 'message': str(error)}
    if baseline_error is None:
        raise RuntimeError('The intended ordinary-reader replacement test did not reject replacement')
    held = target.open('rb')
    release = threading.Timer(0.2, held.close)
    release.start()
    try:
        h.write(name, {'version': 2})
    finally:
        release.join()
        held.close()
    transient_pass = h.read(name) == {'version': 2}
    reader_errors = []
    reader_versions = []
    def concurrent_reader():
        try:
            for unused in range(250):
                with open_read_retry(target) as f:
                    reader_versions.append(h.json.load(f)['version'])
                    h.time.sleep(0.002)
                h.time.sleep(0.002)
        except BaseException as error:
            reader_errors.append(repr(error))
    reader = threading.Thread(target=concurrent_reader)
    reader.start()
    try:
        for version in range(3, 253):
            h.write(name, {'version': version})
    finally:
        reader.join()
    concurrent_pass = (h.read(name) == {'version': 252} and not reader_errors
                       and len(reader_versions) == 250)
    source = h.OUT / (h.P + 'io_test_timeout.tmp')
    with source.open('w', encoding='utf-8') as f:
        f.write('{}\n')
    exhausted = False
    with target.open('rb') as held:
        try:
            replace_with_retry(source, target, timeout=0.1)
        except PermissionError:
            exhausted = True
    result = {'passed': transient_pass and concurrent_pass and exhausted,
              'ordinary_reader_expected_failure': baseline_error,
              'transient_lock_recovery': transient_pass,
              'concurrent_reader_replacements': 250,
              'concurrent_reads': len(reader_versions),
              'concurrent_reader_errors': reader_errors,
              'concurrent_reader_test_passed': concurrent_pass,
              'earlier_test_finding': 'A held delete-sharing reader still prevented replacement; this layer does not rely on delete-sharing.',
              'persistent_lock_bounded_failure_observed': exhausted,
              'production_retry_limit_seconds': 5.0,
              'model_steps_executed': 0, 'utc': h.now(),
              'operational_source_sha256_lf': SELF_HASH}
    with (h.OUT / (h.P + 'io_test_history.jsonl')).open('a', encoding='utf-8', newline='\n') as history:
        history.write(h.json.dumps(result, ensure_ascii=True) + '\n')
        history.flush()
        h.os.fsync(history.fileno())
    h.write(h.P + 'io_tests.json', result)
    print(h.json.dumps(result), flush=True)
    if not result['passed']:
        raise RuntimeError('Operational I/O tests failed')


def preserve(path, records):
    if not path.exists():
        return
    destination = h.OUT / (h.P + 'pre_resume_' + path.name.removeprefix(h.P))
    raw = path.read_bytes()
    if destination.exists():
        if destination.read_bytes() != raw:
            raise RuntimeError('A historical archive already exists with different contents')
    else:
        with destination.open('xb') as f:
            f.write(raw)
            f.flush()
            h.os.fsync(f.fileno())
    records.append({'original': path.name, 'preserved': destination.name,
                    'sha256_lf': h.sha(h.lf(raw))})


def prepare():
    test = h.read(h.P + 'io_tests.json')
    if not test['passed'] or test['operational_source_sha256_lf'] != SELF_HASH:
        raise RuntimeError('Operational tests must pass before resumption')
    h.pins()
    plan = h.read(h.P + 'plan.json')
    state = h.read(h.P + 'execution.json')
    if state['status'] != 'HALTED':
        raise RuntimeError('Expected the recorded halted execution')
    if not (h.OUT / (h.P + 'stop.json')).exists():
        raise RuntimeError('Expected the historical stop marker')
    records = []
    for suffix in ('report.md', 'manifest.json', 'execution.json', 'runs.csv',
                   'runtime.json', 'module_hashes.json', 'source_pins_end.json'):
        preserve(h.OUT / (h.P + suffix), records)
    complete = []
    restart = []
    pending = []
    cleared_unlaunched = []
    for seed in plan['seeds']:
        job = 'H_' + str(seed)
        result = h.completed(job, 'H', seed)
        if result is not None:
            complete.append(seed)
            continue
        initial = h.OUT / (h.P + job + '_initial.json')
        partial = h.OUT / (h.P + job + '_steps_attempt1.csv.partial')
        if initial.exists() or partial.exists():
            restart.append(seed)
            for suffix in ('_initial.json', '_progress.json', '_failure.json'):
                preserve(h.OUT / (h.P + job + suffix), records)
        else:
            pending.append(seed)
            if job in state['attempts']:
                cleared_unlaunched.append(job)
                del state['attempts'][job]
    decision = {'authorization': 'User requested: can you test and resume?',
                'utc': h.now(), 'completed_seeds_validated_and_skipped': complete,
                'interrupted_seeds_to_restart_from_original_seed': restart,
                'not_previously_launched_seeds': pending,
                'unlaunched_dispatch_reservations_cleared': cleared_unlaunched,
                'reason': 'Coordinator stopped after Windows progress-file replacement failure',
                'scientific_identity_unchanged': h.identity(),
                'operational_source_sha256_lf': SELF_HASH,
                'retained_mode': h.read(h.P + 'control.json')['mode'],
                'preserved_artifacts': records}
    h.write(h.P + 'resume_authorization.json', decision)
    stop = h.OUT / (h.P + 'stop.json')
    archived_stop = h.OUT / (h.P + 'pre_resume_stop.json')
    if archived_stop.exists():
        raise RuntimeError('Historical stop archive already exists')
    replace_with_retry(stop, archived_stop)
    state.update(status='INTERRUPTED', active_jobs=[], completed=len(complete), running=0,
                 pending=len(restart) + len(pending), operator_authorized_resume_utc=h.now())
    h.write(h.P + 'execution.json', state)
    print(h.json.dumps({'validated_complete': len(complete), 'restart_seeds': restart,
                       'new_seeds': pending, 'mode': decision['retained_mode']}), flush=True)


def main():
    install()
    command = sys.argv[1]
    if command == 'test':
        test_io()
    elif command == 'prepare':
        prepare()
    elif command == 'calibrate':
        import detector_run_cal_analysis as analysis
        analysis.calibration()
    else:
        h.main()


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        if not isinstance(error, SystemExit):
            h.mark_halt('operational_resume', error)
        raise
