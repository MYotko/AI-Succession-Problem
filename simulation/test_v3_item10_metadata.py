"""Executor side-file failures cannot change scientific work or proof finality."""
import json
import hashlib
from pathlib import Path
import subprocess
import pytest
from test_v3_paths import tmp_path
from v3 import artifacts as a, worker_safety as safety, production_runner as runner
from v3 import host_a11 as host, compatibility_a10 as compatibility
from v3 import compatibility_shards_a11 as proof, service


ORIGINAL_RETURNED = safety._returned


def metadata_failed_returned(path, function, args):
    """Spawn-safe injection, restricted to the informational OOM sidecar."""
    original = safety.atomic_json
    def write(target, value):
        if str(target).endswith('.oom.json'):
            raise ValueError('injected extended-path metadata refusal')
        return original(target, value)
    safety.atomic_json = write
    try:
        return ORIGINAL_RETURNED(path, function, args)
    finally:
        safety.atomic_json = original


def journal_failed_returned(path, function, args):
    original = safety.atomic_json
    def write(target, value):
        if str(target) == path:
            raise OSError('injected correctness journal failure')
        return original(target, value)
    safety.atomic_json = write
    try:
        return ORIGINAL_RETURNED(path, function, args)
    finally:
        safety.atomic_json = original


@pytest.mark.parametrize('error', [OSError, ValueError])
def test_metadata_bounded_attempts_and_stderr(tmp_path, monkeypatch, capsys, error):
    calls = []
    def fail(path, value):
        calls.append(path)
        raise error('injected metadata write')
    monkeypatch.setattr(safety, 'atomic_json', fail)
    target = tmp_path / 'status.json'
    assert safety.metadata_json(target, {}) is False
    assert calls == [target, target]
    records = [json.loads(line) for line in capsys.readouterr().err.splitlines()]
    assert len(records) == 2
    assert all(r['path'] == str(target) and r['error_class'] == error.__name__ and r['epoch'] > 0 for r in records)
    assert not target.exists()


@pytest.mark.parametrize('kind', ['runner', 'host', 'qualification_return'])
def test_worker_metadata_failure_keeps_result_bytes(tmp_path, monkeypatch, kind):
    job = a.stable_job('fixture', {'seconds': .001}, 'validation', 0)
    code = a.code_identity()
    expected = a.canonical(dict(seed=job['seed'], fixture=True))
    def fail(*args, **kwargs):
        raise ValueError('injected side-file scope failure')
    original = safety.atomic_json
    def only_metadata(path, value):
        if str(path).endswith('.oom.json') or Path(path).parent.name == 'worker_metadata':
            return fail()
        return original(path, value)
    monkeypatch.setattr(safety, 'atomic_json', only_metadata)
    if kind == 'runner':
        runner.worker(str(tmp_path), job, code, 1, False, None)
        result = runner.completed(tmp_path, job, code)['result']
    elif kind == 'host':
        path = tmp_path / 'output.json'
        host.execute_scratch(path, job, code, tmp_path, {}, False, None, 'toy', 'lease')
        result = a.read(path)['result']
    else:
        from v3.qualification_a11 import _run_one
        path = tmp_path / 'output.json'
        result = safety._returned(str(tmp_path / 'return.json'), _run_one,
            ((str(path), job, code, str(tmp_path), {}, 'toy'),))
        assert result['canonical_sha256'] == hashlib.sha256(compatibility.comparison_bytes(
            job, dict(seed=job['seed'], fixture=True))).hexdigest()
        result = a.read(path)['result']
    assert a.canonical(result) == expected


@pytest.mark.parametrize('kind', ['runner', 'host', 'return_journal'])
def test_scientific_and_return_journal_writes_remain_strict(tmp_path, monkeypatch, kind):
    job = a.stable_job('fixture', {'seconds': .001}, 'validation', 0)
    def fail(*args, **kwargs):
        raise OSError('injected scientific write failure')
    if kind == 'runner':
        monkeypatch.setattr(runner, 'atomic_json', fail)
        call = lambda: runner.worker(str(tmp_path), job, a.code_identity(), 1, False, None)
    elif kind == 'host':
        monkeypatch.setattr(host, 'atomic_json', fail)
        call = lambda: host.execute_scratch(tmp_path / 'output.json', job, a.code_identity(), tmp_path,
                                          {}, False, None, 'toy', 'lease')
    else:
        monkeypatch.setattr(safety, 'atomic_json', fail)
        call = lambda: safety._returned(str(tmp_path / 'return.json'), dict, ())
    with pytest.raises(OSError, match='scientific write'):
        call()
    assert not (tmp_path / 'records' / (job['id'] + '.json')).exists()


def test_retry_bound_write_waits_until_durable(tmp_path, monkeypatch, capsys):
    events = []
    safety.restart(events, 'toy', 9)
    writes, sleeps = [], []
    def write(path, value):
        writes.append(list(value))
        if len(writes) < 3:
            raise OSError('temporary restart journal outage')
        a.atomic_json(path, value)
    monkeypatch.setattr(safety.time, 'sleep', sleeps.append)
    path = tmp_path / 'restarts.json'
    safety.persist_restarts(path, events, writer=write)
    assert sleeps == [1., 1.]
    assert len(writes) == 3 and all(value == events for value in writes)
    assert a.read(path) == events
    assert json.loads(capsys.readouterr().err)['path'] == str(path)
    for _ in range(3): safety.restart(events, 'toy', 9)
    safety.persist_restarts(path, events)
    with pytest.raises(RuntimeError, match='three signal reruns'):
        safety.require_retry_budget(a.read(path), 'toy')


def test_proof_metadata_failure_after_marker_still_passes(tmp_path, monkeypatch):
    from test_v3_compatibility_shards_a11 import prepared, ORIGINAL, FINGERPRINT
    monkeypatch.setattr(proof, 'verify_code', lambda _: None)
    monkeypatch.setattr(proof.platform, 'node', lambda: ORIGINAL)
    monkeypatch.setattr(host, 'fingerprint', lambda: FINGERPRINT)
    monkeypatch.setattr(compatibility, 'RECORD_DIRECTORY', tmp_path / 'reservation')
    path, plan, _, _ = prepared(tmp_path, two=False)
    proof.stage(path, ORIGINAL)
    root = proof.host_directory(path, ORIGINAL)
    monkeypatch.setattr(safety, '_returned', metadata_failed_returned)
    original = proof.atomic_json
    failures = []
    def write(target, value):
        if Path(target).name == 'scheduling.json' and (root / 'started.json').exists():
            failures.append(str(target))
            raise ValueError('injected scheduler metadata failure after start')
        return original(target, value)
    monkeypatch.setattr(proof, 'atomic_json', write)
    result = proof.run_shard(path, ORIGINAL)
    assert failures
    assert result['passed'] and len(result['proofs']) == len(plan['selected_job_ids'])
    assert all(r['before_sha256'] == r['after_sha256'] for r in result['proofs'])
    assert proof.combine(path)['passed']
    with pytest.raises(ValueError, match='final'):
        proof.run_shard(path, ORIGINAL)


def test_proof_correctness_write_failure_stays_final(tmp_path, monkeypatch):
    from test_v3_compatibility_shards_a11 import prepared, ORIGINAL, FINGERPRINT
    monkeypatch.setattr(proof, 'verify_code', lambda _: None)
    monkeypatch.setattr(proof.platform, 'node', lambda: ORIGINAL)
    monkeypatch.setattr(host, 'fingerprint', lambda: FINGERPRINT)
    monkeypatch.setattr(compatibility, 'RECORD_DIRECTORY', tmp_path / 'reservation')
    path, _, _, _ = prepared(tmp_path, two=False)
    proof.stage(path, ORIGINAL)
    root = proof.host_directory(path, ORIGINAL)
    original = proof.run_items
    def run(*args, **kwargs):
        if (root / 'started.json').exists():
            monkeypatch.setattr(safety, '_returned', journal_failed_returned)
        return original(*args, **kwargs)
    monkeypatch.setattr(proof, 'run_items', run)
    with pytest.raises(OSError, match='correctness journal failure'):
        proof.run_shard(path, ORIGINAL)
    assert not a.unseal(a.read(root / 'result.json'))['passed']
    with pytest.raises(ValueError, match='final'):
        proof.run_shard(path, ORIGINAL)


def test_diagnostic_event_and_swap_failures_are_best_effort(tmp_path, monkeypatch):
    def fail(*args, **kwargs): raise ValueError('injected metadata scope refusal')
    monkeypatch.setattr(runner, 'scoped', fail)
    runner.event(tmp_path, 'signal_restart', job='toy', signal=9)
    monkeypatch.setattr(safety, 'atomic_json', fail)
    monkeypatch.setattr(safety, 'swap_status', lambda: dict(total_bytes=32e9, free_bytes=32e9))
    assert safety.swap_preflight(dict(profile='x2'), tmp_path / 'swap.json')['passed']
    monkeypatch.setattr(safety, 'swap_status', lambda: dict(total_bytes=32e9, free_bytes=0))
    with pytest.raises(ValueError, match='16 GB'):
        safety.swap_preflight(dict(profile='x2'), tmp_path / 'swap.json')


def test_service_log_failure_never_skips_or_repeats_action(tmp_path, monkeypatch):
    actions = []
    def run(argv, **kwargs):
        actions.append(argv)
        return subprocess.CompletedProcess(argv, 0, stdout=b'toy service output')
    monkeypatch.setattr(service.subprocess, 'run', run)
    def fail(*args, **kwargs): raise OSError('injected log failure')
    monkeypatch.setattr(service, 'scoped', fail)
    assert service.command(tmp_path, 'down') == 0
    assert service.command(tmp_path, 'up') == 0
    assert actions == [['llm', 'down'], ['llm', 'up']]


def test_pull_diagnostic_writes_do_not_prevent_durable_state(tmp_path, monkeypatch):
    from test_v3_multihost_a11 import initialize, spec_fixture, join
    from v3 import multihost_a11 as multihost
    _, root, _ = initialize(tmp_path, spec_fixture(1), hosts=('alpha',))
    def fail(*args, **kwargs): raise ValueError('injected status refusal')
    monkeypatch.setattr(safety, 'atomic_json', fail)
    identity = join(root, 'alpha')
    with multihost.transaction(root):
        coordinator = multihost.Coordinator(root)
        assert identity['session'] in coordinator.state['sessions']
        coordinator.save(force=True)
    with multihost.transaction(root):
        coordinator = multihost.Coordinator(root)
        assert identity['session'] in coordinator.state['sessions']


def test_pull_publication_fallback_snapshot_write_stays_strict(tmp_path, monkeypatch):
    from test_v3_multihost_a11 import initialize, spec_fixture
    from v3 import multihost_a11 as multihost
    _, root, _ = initialize(tmp_path, spec_fixture(1), hosts=('alpha',))
    original = multihost.atomic_json
    def write(path, value):
        if Path(path).name == 'pull_state.json':
            raise OSError('injected publication snapshot failure')
        return original(path, value)
    monkeypatch.setattr(multihost, 'atomic_json', write)
    with multihost.transaction(root):
        coordinator = multihost.Coordinator(root)
        with pytest.raises(OSError, match='publication snapshot'):
            coordinator.save(force=True)
