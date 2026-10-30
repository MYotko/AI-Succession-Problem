"""The post-update requalification harness, on fixtures only.

Every archived output here is produced by the real producer functions at this
checkout's identity on toy settings, then replayed by the harness at the same
identity. No registered root, output or reading is read. The harness lives
outside the source manifest, so these tests also pin that boundary."""
from copy import deepcopy
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from test_v3_paths import tmp_path
from test_v3_a13 import durable
from v3 import artifacts as a
from v3 import tables_a10 as tables
from v3 import production_runner as runner

from requalification import harness, worker

CAL_PATH = 'v3/runs/registered/v3_rerun_calibration.json'
TOY = dict(groups=3, runs_per_group=2, particles=2, burn=30, measure=8)


@pytest.fixture(autouse=True)
def clean_scratch():
    yield
    shutil.rmtree(a.ROOT / '_requalification', ignore_errors=True)


@pytest.fixture
def in_process(monkeypatch):
    """In-process replays run inside pytest, whose numpy was imported before any
    thread limit; the separate-interpreter path verifies the real limit."""
    monkeypatch.setattr(a, 'runtime', lambda threads: dict(threads_configured=threads, threads_verified=[],
                                                           in_process_fixture=True))


def a14_source(plan, **fields):
    """The frozen A14 binding a source must supply: its original jobs, plan hash
    and seed manifest hash."""
    return dict(fields, a14_binding=dict(job_ids=[j['id'] for j in plan['jobs']], plan_hash=plan['plan_hash'],
                                         seed_manifest_sha256=a.digest(plan['seed_manifest']), job_count=len(plan['jobs'])))


def launch_root(root, spec):
    """The durable launch records freeze_sample verifies."""
    a.atomic_json(root / 'identity.json', dict(code_hash=spec['code_hash'], spec_hash=a.digest(spec)))
    a.atomic_json(root / 'manifest.json', a.seal(spec))
    a.atomic_json(root / 'launches.json', [dict(complete=True)])


def fixture_jobs(count=9):
    jobs = []
    for i in range(count):
        cfg = dict(phase='fixture', category=('R1', 'R2', 'refinement')[i % 3], steps=5, seconds=.001,
                   model=dict(alpha=1., successor_capability=1.5))
        jobs.append(a.stable_job('fixture', cfg, 'validation', i))
    return jobs


def source(tmp_path, name, jobs, *, selection, group='runs'):
    """A completed toy launch: executed by the real execute() and recorded durably."""
    spec = dict(schema='toy', code_hash=a.code_identity(), registered=False, jobs=jobs)
    root = tmp_path / name
    for job in jobs:
        phase_root = root / job['config'].get('phase', job['kind'])
        durable(phase_root, job, runner.execute(job, root=phase_root))
    launch_root(root, spec)
    spec_path = tmp_path / (name + '_spec.json')
    a.atomic_json(spec_path, a.seal(spec))
    return dict(name=name, group=group, selection=selection, producing_code_hash=a.code_identity(),
                checkout=str(a.SIMULATION.parent), original_simulation=str(a.SIMULATION),
                spec=str(spec_path), root=str(root))


def perturb_output(root, job, mutate):
    """Alter an archived output's scientific bytes and re-bind its completion
    record, so completed() still accepts it and only the comparison can tell."""
    phase_root = Path(root) / job['config'].get('phase', job['kind'])
    path = phase_root / 'outputs' / (job['id'] + '.json')
    document = a.read(path)
    mutate(document['result'])
    a.atomic_json(path, document)
    record = a.read(phase_root / 'records' / (job['id'] + '.json'))
    record['output_hash'] = a.file_hash(path)
    a.atomic_json(phase_root / 'records' / (job['id'] + '.json'), record)


# ---------------------------------------------------------------------------
# Boundary and selection
# ---------------------------------------------------------------------------

def test_harness_is_outside_the_source_manifest():
    manifest = a.source_manifest()
    assert not any('requalification' in name for name in manifest)
    for name in ('harness.py', 'worker.py', '__init__.py'):
        assert (Path(harness.HERE) / name).is_file()
    assert set(harness.harness_hashes()) == {'__init__.py', 'harness.py', 'worker.py'}


def test_comparison_convention_matches_the_a11_helper_plus_code_hash():
    from v3.compatibility_a10 import comparison_bytes as a11_bytes
    job = fixture_jobs(1)[0]
    result = dict(seed=1, fixture=True, seconds=3., trajectory_seconds=1., nested=dict(seconds=2., value=[1, 2]))
    ours = json.loads(worker.comparison_bytes(job, result))
    assert ours == json.loads(a11_bytes(job, result))
    with_code = dict(result, code_hash='p' * 64)
    assert json.loads(worker.comparison_bytes(job, with_code))['result']['code_hash'] == 'p' * 64
    assert 'code_hash' not in json.loads(a11_bytes(job, with_code))['result']
    assert 'seconds' not in ours['result'] and ours['result']['nested']['seconds'] == 2.


def test_selection_is_deterministic_stratified_and_outcome_free():
    jobs = fixture_jobs(12)
    chosen, strata = harness.select('toy', 'a15', jobs)
    assert len(strata) == 3 and all(len(s['selected']) == 2 and s['population'] == 4 for s in strata)
    assert chosen == [jid for s in strata for jid in s['selected']]
    again, _ = harness.select('toy', 'a15', list(reversed(jobs)))
    assert again == chosen
    expected = sorted(strata[0]['job_ids'], key=lambda jid: (a.digest([harness.A15_TAG, strata[0]['stratum'], jid]), jid))[:2]
    assert strata[0]['selected'] == expected
    everything, _ = harness.select('toy', 'all', jobs)
    assert sorted(everything) == sorted(j['id'] for j in jobs)
    a11, s11 = harness.select('toy', 'a11', jobs)
    assert len(s11) == 1 and len(a11) == 2
    # Arms that differ only in the instrument never share a stratum.
    k15 = a.stable_job('fixture', dict(phase='fixture', category='R2', model=dict(alpha=1., successor_capability=1.5,
                       instrument=dict(mapping='A10', k_star=1.5, g='linear'))), 'validation', 0)
    k23 = a.stable_job('fixture', dict(phase='fixture', category='R2', model=dict(alpha=1., successor_capability=1.5,
                       instrument=dict(mapping='A10', k_star=2.3, g='linear'))), 'validation', 1)
    assert harness.a15_stratum('arm', k15) != harness.a15_stratum('arm', k23)
    _, two = harness.select('arm', 'a15', [k15, k23])
    assert len(two) == 2
    assert a11 == sorted((j['id'] for j in jobs), key=lambda jid: (a.digest([harness.A11_TAG, 'fixture', jid]), jid))[:2]
    with pytest.raises(worker.RequalificationError, match='unknown selection'):
        harness.select('toy', 'outcome', jobs)


def test_fit_job_id_restatement_matches_the_producer():
    from v3 import table_validation_a4 as a4
    from v3 import continuation_validation as cv
    c = dict(a1_source_root='r', a1_job=dict(id='x', seed=12345, config={}), a1_source_code_hash='h', plan_hash='p',
             route='plain', stage='validate', replicate=1, seed=cv.validate_seed(12345, 1), settings_override=TOY)
    assert harness._fit_job_id(c) == a4._fit_job_id(c)
    del c['settings_override']
    assert harness._fit_job_id(c) == a4._fit_job_id(c)


def test_freeze_is_write_once_and_verifies_the_launch(tmp_path):
    src = source(tmp_path, 'fx', fixture_jobs(6), selection='a15')
    sample_path = tmp_path / 'sample.json'
    document = harness.freeze_sample([src], sample_path)
    sample = harness.unseal(document)
    assert sample['schema'] == harness.SAMPLE_SCHEMA and sample['item_count'] == 6 == len(sample['items'])
    assert sample['harness_sha256'] == harness.harness_hashes()
    assert sample['sources'][0]['registration'] == {'registered': False, 'pin': None, 'verified': False,
                                                    'note': 'non-registered spec; no registration pin to verify'}
    assert harness.freeze_sample([src], sample_path) == document
    with pytest.raises(worker.RequalificationError, match='frozen'):
        harness.write_once(sample_path, harness.seal(dict(sample, item_count=7)))
    for item in sample['items']:
        assert item['producing_code_hash'] == a.code_identity()
        assert {r['path'] for r in item['inputs']} == {str((Path(src['root']) / 'fixture' / d / (item['job']['id'] + '.json')).resolve())
                                                        for d in ('records', 'outputs')}
    bad = dict(src, producing_code_hash='0' * 64)
    with pytest.raises(worker.RequalificationError, match='producing identity'):
        harness.freeze_sample([bad], tmp_path / 'other.json')
    # An archived selection list must be reproduced exactly.
    expected = [i['job']['id'] for i in sample['items']]
    assert harness.freeze_sample([dict(src, expected_job_ids=expected)], tmp_path / 'expected.json')
    with pytest.raises(worker.RequalificationError, match='differs from the expected'):
        harness.freeze_sample([dict(src, expected_job_ids=expected[:-1])], tmp_path / 'short.json')
    a.atomic_json(Path(src['root']) / 'launches.json', [dict(complete=False)])
    with pytest.raises(worker.RequalificationError, match='completed launch'):
        harness.freeze_sample([src], tmp_path / 'other.json')


def committed_note_pin():
    """A real historical pin for this worktree: its HEAD and the committed note."""
    repo = a.SIMULATION.parent
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=repo, capture_output=True, text=True, check=True).stdout.strip()
    path = 'simulation/diagnostics/v3_rerun_design_note.md'
    committed = subprocess.run(['git', 'show', head + ':' + path], cwd=repo, capture_output=True, check=True).stdout
    import hashlib
    return dict(commit=head, path=path, sha256=hashlib.sha256(committed).hexdigest())


def test_registered_source_pin_is_verified_by_the_producer_in_historical_mode(tmp_path, monkeypatch):
    pin = committed_note_pin()
    jobs = fixture_jobs(2)
    spec = dict(schema='toy', code_hash=a.code_identity(), registered=True, registration=pin,
                instrument=tables.NOMINAL.declaration(), jobs=jobs)
    root = tmp_path / 'reg'
    for job in jobs:
        durable(root / 'fixture', job, runner.execute(job, root=root / 'fixture'))
    launch_root(root, spec)
    spec_path = tmp_path / 'reg_spec.json'
    a.atomic_json(spec_path, a.seal(spec))
    src = dict(name='reg', group='runs', selection='all', producing_code_hash=a.code_identity(),
               checkout=str(a.SIMULATION.parent), original_simulation=str(a.SIMULATION), spec=str(spec_path), root=str(root))
    sample = harness.unseal(harness.freeze_sample([src], tmp_path / 'sample.json'))
    record = sample['sources'][0]['registration']
    assert record['verified'] and record['mode'] == 'historical' and record['pin'] == pin
    assert record['verifier_code_identity'] == a.code_identity()
    # The frozen source record carries the mode the worker actually ran.
    real_run = harness.subprocess.run
    def equivalent(command, **kw):
        completed = real_run(command, **kw)
        if '--verify-pin' in command:
            path = Path(command[command.index('--result') + 1])
            result = json.loads(path.read_text())
            result['mode'] = 'historical-equivalent; producer has no historical mode'
            path.write_bytes(worker.canonical(result) + b'\n')
        return completed
    monkeypatch.setattr(harness.subprocess, 'run', equivalent)
    sample = harness.unseal(harness.freeze_sample([src], tmp_path / 'sample_mode.json'))
    assert sample['sources'][0]['registration']['mode'].startswith('historical-equivalent')
    monkeypatch.setattr(harness.subprocess, 'run', real_run)
    # A stale or absent pin refuses the freeze.
    bad = dict(spec, registration=dict(pin, sha256='0' * 64))
    bad_root = tmp_path / 'bad'
    for job in jobs:
        durable(bad_root / 'fixture', job, runner.execute(job, root=bad_root / 'fixture'))
    launch_root(bad_root, bad)
    a.atomic_json(tmp_path / 'bad_spec.json', a.seal(bad))
    with pytest.raises(worker.RequalificationError, match='could not be verified'):
        harness.freeze_sample([dict(src, spec=str(tmp_path / 'bad_spec.json'), root=str(bad_root))], tmp_path / 'bad.json')
    absent = {k: v for k, v in spec.items() if k != 'registration'}
    absent_root = tmp_path / 'absent'
    for job in jobs:
        durable(absent_root / 'fixture', job, runner.execute(job, root=absent_root / 'fixture'))
    launch_root(absent_root, absent)
    a.atomic_json(tmp_path / 'absent_spec.json', a.seal(absent))
    with pytest.raises(worker.RequalificationError, match='without a registration pin'):
        harness.freeze_sample([dict(src, spec=str(tmp_path / 'absent_spec.json'), root=str(absent_root))], tmp_path / 'absent.json')


def test_pin_verification_for_a_producer_without_historical_mode(in_process, tmp_path, monkeypatch):
    """Producers before 2026-10-17 have no ``historical`` keyword; the worker
    then performs the equivalent ancestry and committed-bytes checks itself and
    says so, never falling back to the producer's strict mode."""
    pin = committed_note_pin()
    spec = dict(schema='toy', code_hash=a.code_identity(), registered=True, registration=pin,
                instrument=tables.NOMINAL.declaration(), jobs=fixture_jobs(1))
    spec_path = tmp_path / 'old_spec.json'
    a.atomic_json(spec_path, a.seal(spec))
    calls = []
    def old_verify(pin, repository=None, *, instrument=None):
        calls.append('strict')
        raise AssertionError('strict mode must not be used as a fallback')
    monkeypatch.setattr(a, 'verify_registration', old_verify)
    record = worker.verify_pin(a.SIMULATION.parent, spec_path)
    assert record['verified'] and record['mode'].startswith('historical-equivalent') and record['pin'] == pin
    assert not calls
    stale = dict(spec, registration=dict(pin, sha256='0' * 64))
    a.atomic_json(tmp_path / 'stale_spec.json', a.seal(stale))
    with pytest.raises(worker.RequalificationError, match='stale'):
        worker.verify_pin(a.SIMULATION.parent, tmp_path / 'stale_spec.json')
    orphan = dict(spec, registration=dict(pin, commit='0' * 40))
    a.atomic_json(tmp_path / 'orphan_spec.json', a.seal(orphan))
    with pytest.raises(subprocess.CalledProcessError):
        worker.verify_pin(a.SIMULATION.parent, tmp_path / 'orphan_spec.json')


# ---------------------------------------------------------------------------
# Replay in a separate interpreter at the checkout
# ---------------------------------------------------------------------------

def toy_table_job():
    jobs = tables.build_jobs('sqrt', CAL_PATH, settings_override=TOY,
                             kernel_override={'n_agents': 16, 'carrying_capacity': 160},
                             rule_ids=['balanced'], physical_contexts=[(.064, 1.)])
    primary = [j for j in jobs if j['config']['setting_name'] == 'primary']
    assert len(primary) == 1
    return primary[0]


def test_subprocess_replay_passes_then_detects_altered_result_bytes(tmp_path):
    jobs = fixture_jobs(3) + [toy_table_job()]
    src = source(tmp_path, 'mixed', jobs, selection='all', group='table')
    sample_path = tmp_path / 'sample.json'
    document = harness.freeze_sample([src], sample_path)
    acceptance = harness.replay(sample_path, tmp_path / 'clean', workers=2)
    assert acceptance['passed'] and acceptance['complete'] and acceptance['executed'] == 4
    assert all(r['passed'] and r['exit_code'] == 0 and r['before_sha256'] == r['after_sha256'] for r in acceptance['items'])
    table_record = next(r for r in acceptance['items'] if r['kind'] == 'table')
    assert table_record['runtime']['threads_configured'] == 1 and table_record['runtime']['threads_verified']
    assert table_record['checkout'] == str(a.SIMULATION.parent.resolve())
    assert not (a.ROOT / '_requalification').exists() or not any((a.ROOT / '_requalification').rglob('*.json'))
    sealed = a.read(tmp_path / 'clean' / 'acceptance.json')
    assert a.unseal(sealed)['sample_sha256'] == document['sha256']
    with pytest.raises(worker.RequalificationError, match='already exists'):
        harness.replay(sample_path, tmp_path / 'clean')
    assert acceptance['attempt_environment']['packages_sha256'] == acceptance['items'][0]['runtime']['packages_sha256']
    assert acceptance['exit_codes_zero'] and acceptance['checkout_order'] == [str(a.SIMULATION.parent.resolve())]
    assert all(r['item_id'] for r in acceptance['admissions']) and len(acceptance['admissions']) == 4
    # Forced mismatch: alter one archived result's scientific bytes and rebind
    # its record. Against the earlier frozen sample the changed archive is
    # refused before anything runs: the record and output are hashed inputs.
    table = jobs[-1]
    perturb_output(src['root'], table, lambda result: result['rows'][0].__setitem__('flow_range', 1e-9))
    stale = harness.replay(sample_path, tmp_path / 'stale', workers=1)
    assert not stale['passed']
    failed = next(r for r in stale['items'] if r['job_id'] == table['id'])
    assert 'input changed' in failed['error'] or 'frozen sample' in failed['error']
    # Re-freeze over the altered archive: the comparison itself must fail.
    document = harness.freeze_sample([src], tmp_path / 'sample2.json')
    altered = harness.replay(tmp_path / 'sample2.json', tmp_path / 'altered', workers=2)
    assert not altered['passed'] and altered['first_failure']['job_id'] == table['id']
    failed = next(r for r in altered['items'] if r['job_id'] == table['id'])
    assert failed['before_sha256'] != failed['after_sha256'] and failed['exit_code'] == 1
    # Dispatch stopped after the mismatch, and every item is accounted for.
    assert {r['item_id'] for r in altered['items']} == {i['item_id'] for i in harness.unseal(document)['items']}
    assert sum(1 for r in altered['items'] if r.get('error', '').startswith('not executed')) + altered['executed'] == 4


def test_no_false_pass_from_prior_results_or_a_failed_worker(tmp_path, monkeypatch):
    """Fix 1: results are never overwritten, a non-zero worker exit is a failure
    whatever the result file says, and an attempt over prior results is refused."""
    jobs = fixture_jobs(3)
    src = source(tmp_path, 'fp', jobs, selection='all')
    sample_path = tmp_path / 'sample.json'
    document = harness.freeze_sample([src], sample_path)
    items = harness.unseal(document)['items']
    out = tmp_path / 'attempt'
    first = harness.run_item(items[0], document['sha256'], out)
    assert first['passed'] and first['exit_code'] == 0
    # A second launch for the same item never overwrites its result.
    with pytest.raises(worker.RequalificationError, match='never overwritten'):
        harness.run_item(items[0], document['sha256'], out)
    # An attempt without resume refuses a directory holding prior results.
    with pytest.raises(worker.RequalificationError, match='prior per-item results'):
        harness.replay(sample_path, out, workers=1)
    assert not (out / 'acceptance.json').exists()
    # A worker that exits non-zero fails the item even if its result file says passed.
    real_run = harness.subprocess.run
    def failing(command, **kw):
        completed = real_run(command, **kw)
        return subprocess.CompletedProcess(command, 1, completed.stdout, 'injected worker failure')
    monkeypatch.setattr(harness.subprocess, 'run', failing)
    acceptance = harness.replay(sample_path, tmp_path / 'failed', workers=1)
    assert not acceptance['passed'] and not acceptance['exit_codes_zero']
    first_failure = acceptance['first_failure']
    assert first_failure['exit_code'] == 1 and first_failure['item_id'] == items[0]['item_id']
    failed = acceptance['items'][0]
    assert failed['passed'] is False and failed['exit_code'] == 1 and 'injected' in failed['stderr_tail']
    assert failed['before_sha256'] == failed['after_sha256']  # the comparison agreed; the exit code still fails it
    assert acceptance['items'][1]['error'].startswith('not executed')
    stored = json.loads((tmp_path / 'failed' / 'results' / (items[0]['item_id'] + '.json')).read_text())
    assert stored['passed'] is False and stored['exit_code'] == 1
    # The failed attempt is final: a resume over it is refused.
    monkeypatch.setattr(harness.subprocess, 'run', real_run)
    with pytest.raises(worker.RequalificationError, match='already exists'):
        harness.replay(sample_path, tmp_path / 'failed', workers=1, resume=True)


def test_failed_worker_file_survives_a_resume_and_refuses_it(tmp_path):
    """Fix 1 of round 2: a worker that finished with a mismatch before the
    harness recorded it is a recorded failure. The resume writes the per-item
    result from it, deletes nothing, and refuses."""
    jobs = fixture_jobs(2)
    src = source(tmp_path, 'wf', jobs, selection='all')
    sample_path = tmp_path / 'sample.json'
    document = harness.freeze_sample([src], sample_path)
    items = harness.unseal(document)['items']
    out = tmp_path / 'attempt'
    harness.run_item(items[0], document['sha256'], out)
    failed = harness.result_path_for(items[1], out).with_suffix('.worker.json')
    failed.write_text(json.dumps(dict(item_id=items[1]['item_id'], job_id=items[1]['job']['id'], passed=False,
                                      before_sha256='a' * 64, after_sha256='b' * 64)))
    bytes_before = failed.read_bytes()
    with pytest.raises(worker.RequalificationError, match='stays final'):
        harness.replay(sample_path, out, workers=1, resume=True)
    assert failed.read_bytes() == bytes_before
    written = json.loads(harness.result_path_for(items[1], out).read_text())
    assert written['passed'] is False and written['harness_interrupted'] and written['exit_code'] is None
    assert written['before_sha256'] == 'a' * 64 and written['sample_sha256'] == document['sha256']
    assert not (out / 'acceptance.json').exists()
    with pytest.raises(worker.RequalificationError, match='stays final'):
        harness.replay(sample_path, out, workers=1, resume=True)


def test_resume_is_safe_against_a_surviving_worker_and_refuses_under_a_lock(tmp_path, monkeypatch):
    """Round 3 fix 1: a failure a surviving worker writes between the pre-scan
    and preservation is refused, never renamed or rerun; a worker file that
    appears during the resume refuses it; attempt.lock refuses any attempt."""
    jobs = fixture_jobs(3)
    src = source(tmp_path, 'surv', jobs, selection='all')
    sample_path = tmp_path / 'sample.json'
    document = harness.freeze_sample([src], sample_path)
    items = harness.unseal(document)['items']
    out = tmp_path / 'attempt'
    harness.run_item(items[0], document['sha256'], out)
    stale = harness.result_path_for(items[1], out).with_suffix('.worker.json')
    stale.write_text('{"passed": true, "marker": "still running at the pre-scan"}')
    failure = json.dumps(dict(item_id=items[1]['item_id'], job_id=items[1]['job']['id'], passed=False,
                              before_sha256='a' * 64, after_sha256='b' * 64))
    real_clear = harness.clear_interrupted_scratch
    def surviving_worker(item, sample_sha256):
        # The prior attempt's worker finishes with a failure after the pre-scan.
        if item['item_id'] == items[1]['item_id']:
            stale.write_text(failure)
        return real_clear(item, sample_sha256)
    monkeypatch.setattr(harness, 'clear_interrupted_scratch', surviving_worker)
    with pytest.raises(worker.RequalificationError, match='appeared or changed since the pre-scan'):
        harness.replay(sample_path, out, workers=1, resume=True)
    assert stale.read_text() == failure and not list((out / 'results').glob('*.interrupted.*'))
    assert not harness.result_path_for(items[1], out).exists() and not (out / 'acceptance.json').exists()
    assert not (out / 'attempt.lock').exists()
    # A second resume sees the recorded failure and refuses it as final.
    monkeypatch.setattr(harness, 'clear_interrupted_scratch', real_clear)
    with pytest.raises(worker.RequalificationError, match='stays final'):
        harness.replay(sample_path, out, workers=1, resume=True)
    # A worker file that appears for a later item during preservation is
    # caught at that item's own preservation check.
    appearing = tmp_path / 'appearing'
    harness.run_item(items[0], document['sha256'], appearing)
    late = harness.result_path_for(items[2], appearing).with_suffix('.worker.json')
    def appearing_worker(item, sample_sha256):
        if item['item_id'] == items[1]['item_id']:
            late.write_text('{"passed": false}')
        return real_clear(item, sample_sha256)
    monkeypatch.setattr(harness, 'clear_interrupted_scratch', appearing_worker)
    with pytest.raises(worker.RequalificationError, match='appeared or changed'):
        harness.replay(sample_path, appearing, workers=1, resume=True)
    assert late.read_text() == '{"passed": false}'
    # A worker file that is rewritten for an item the resume reuses (never
    # preserved) is caught only by the re-scan after all preservations.
    rescan = tmp_path / 'rescan'
    harness.run_item(items[0], document['sha256'], rescan)
    reused = harness.result_path_for(items[0], rescan).with_suffix('.worker.json')
    def rewriting_worker(item, sample_sha256):
        if item['item_id'] == items[1]['item_id']:
            reused.write_text('{"passed": false, "rewritten": true}')
        return real_clear(item, sample_sha256)
    monkeypatch.setattr(harness, 'clear_interrupted_scratch', rewriting_worker)
    with pytest.raises(worker.RequalificationError, match='appeared or changed during the resume'):
        harness.replay(sample_path, rescan, workers=1, resume=True)
    assert json.loads(reused.read_text())['rewritten']
    monkeypatch.setattr(harness, 'clear_interrupted_scratch', real_clear)
    # The lock refuses both a fresh attempt and a resume, and is removed when an attempt ends.
    locked = tmp_path / 'locked'
    locked.mkdir()
    (locked / 'attempt.lock').write_text('{"pid": 1}')
    with pytest.raises(worker.RequalificationError, match='attempt.lock exists'):
        harness.replay(sample_path, locked, workers=1)
    with pytest.raises(worker.RequalificationError, match='attempt.lock exists'):
        harness.replay(sample_path, locked, workers=1, resume=True)
    (locked / 'attempt.lock').unlink()
    seen = {}
    real_run_item = harness.run_item
    def observe_lock(item, sample_sha256, output_dir, *args, **kw):
        seen['lock'] = json.loads((Path(output_dir) / 'attempt.lock').read_text())
        return real_run_item(item, sample_sha256, output_dir, *args, **kw)
    monkeypatch.setattr(harness, 'run_item', observe_lock)
    acceptance = harness.replay(sample_path, locked, workers=1)
    assert acceptance['passed'] and seen['lock']['pid'] == os.getpid() and seen['lock']['sample_sha256'] == document['sha256']
    assert not (locked / 'attempt.lock').exists()
    # An interrupt that escapes the pool with a worker possibly alive keeps the lock.
    monkeypatch.setattr(harness, 'run_item', real_run_item)
    def interrupted_pool(*args, **kw):
        pending = args[3]
        from concurrent.futures import Future
        pending[Future()] = {'item_id': 'alive'}  # a worker that never finished
        raise KeyboardInterrupt()
    monkeypatch.setattr(harness, '_dispatch_pool', interrupted_pool)
    interrupted = tmp_path / 'interrupted'
    with pytest.raises(KeyboardInterrupt):
        harness.replay(sample_path, interrupted, workers=1)
    assert (interrupted / 'attempt.lock').is_file()
    with pytest.raises(worker.RequalificationError, match='attempt.lock exists'):
        harness.replay(sample_path, interrupted, workers=1, resume=True)


def test_double_fault_in_the_handler_still_leaves_a_failed_record_and_acceptance(tmp_path, monkeypatch):
    """Round 3 fix 2: the handler calls nothing that can raise; a failed
    canonical write falls back to a minimal record; a task that raises inside
    the pool is recorded by collect; the acceptance is always written and fails."""
    jobs = fixture_jobs(2)
    src = source(tmp_path, 'dbl', jobs, selection='all')
    sample_path = tmp_path / 'sample.json'
    document = harness.freeze_sample([src], sample_path)
    items = harness.unseal(document)['items']
    def exploding(item, sample_sha256, output_dir, *args, **kw):
        raise RuntimeError('double fault origin')
    monkeypatch.setattr(harness, 'run_item', exploding)
    real_canonical = harness.canonical
    def failing_canonical(value):
        if isinstance(value, dict) and str(value.get('error', '')).startswith('RuntimeError: double fault'):
            raise OSError('canonical write failed')
        return real_canonical(value)
    monkeypatch.setattr(harness, 'canonical', failing_canonical)
    acceptance = harness.replay(sample_path, tmp_path / 'minimal', workers=1)
    assert not acceptance['passed'] and acceptance['first_failure']['error'].startswith('RuntimeError: double fault')
    minimal = json.loads(harness.result_path_for(items[0], tmp_path / 'minimal').read_text())
    assert minimal['passed'] is False and 'minimal record' in minimal['error'] and set(minimal) == {'item_id', 'job_id', 'passed', 'error'}
    assert 'minimal record' in acceptance['items'][0]['note']
    monkeypatch.setattr(harness, 'canonical', real_canonical)
    # A task that raises past the handler is recorded by collect, and the acceptance is still written.
    def raising_task(*args, **kw):
        raise RuntimeError('escaped the handler')
    monkeypatch.setattr(harness, 'guarded_run_item', raising_task)
    acceptance = harness.replay(sample_path, tmp_path / 'escaped', workers=1)
    assert not acceptance['passed'] and 'escaped the handler' in acceptance['first_failure']['error']
    stored = json.loads(harness.result_path_for(items[0], tmp_path / 'escaped').read_text())
    assert stored['passed'] is False and 'escaped the handler' in stored['error']
    assert (tmp_path / 'escaped' / 'acceptance.json').is_file() and not (tmp_path / 'escaped' / 'attempt.lock').exists()
    # Even a failure of the dispatcher itself leaves a failed acceptance.
    monkeypatch.setattr(harness, '_dispatch', lambda *a, **k: (_ for _ in ()).throw(RuntimeError('dispatcher fault')))
    acceptance = harness.replay(sample_path, tmp_path / 'dispatcher', workers=1)
    assert not acceptance['passed'] and acceptance['dispatch_error'] == 'RuntimeError: dispatcher fault'
    assert (tmp_path / 'dispatcher' / 'acceptance.json').is_file()


def test_admission_counts_running_futures_and_rechecks_at_the_limit(monkeypatch):
    """Round 3 fix 3: a future that finished since the last collection holds no
    reservation, and the wait limit ends with one final collection and re-check."""
    from concurrent.futures import Future
    item = dict(kind='fixture', job=dict(id='x', config={}))
    reservation = harness.reservation_bytes(item, harness.DEFAULT_RESERVATIONS_GB)
    monkeypatch.setattr(harness, 'mem_available_bytes', lambda: int(1.5 * reservation))
    finished = Future()
    finished.set_result({})
    admitted = harness.admit(item, harness.DEFAULT_RESERVATIONS_GB, 0, {finished: item}, wait_seconds=.05, poll_seconds=.01)
    assert admitted['pending_reserved_bytes'] == 0
    running = Future()
    calls = []
    def collect_at_the_limit():
        calls.append(1)
        if len(calls) >= 4:
            running.set_result({})
    admitted = harness.admit(item, harness.DEFAULT_RESERVATIONS_GB, 0, {running: item}, wait_seconds=.02, poll_seconds=.01,
                             collect=collect_at_the_limit)
    assert admitted['pending_reserved_bytes'] == 0 and admitted['waited_seconds'] >= .02
    stuck = Future()
    with pytest.raises(worker.RequalificationError, match='timed out'):
        harness.admit(item, harness.DEFAULT_RESERVATIONS_GB, 0, {stuck: item}, wait_seconds=.02, poll_seconds=.01)


def test_fingerprint_mismatch_is_recorded_on_disk_before_any_resume(tmp_path, monkeypatch):
    """Fix 2 of round 2: run_item compares the worker's fingerprint with the
    attempt's before writing the per-item result, so the rejection is on disk."""
    jobs = fixture_jobs(2)
    src = source(tmp_path, 'fpd', jobs, selection='all')
    sample_path = tmp_path / 'sample.json'
    document = harness.freeze_sample([src], sample_path)
    items = harness.unseal(document)['items']
    real_run = harness.subprocess.run
    def foreign(command, **kw):
        completed = real_run(command, **kw)
        path = Path(command[command.index('--result') + 1])
        record = json.loads(path.read_text())
        record['runtime']['uname'] = dict(record['runtime']['uname'], release='other-kernel')
        path.write_bytes(worker.canonical(record) + b'\n')
        return completed
    monkeypatch.setattr(harness.subprocess, 'run', foreign)
    expected = {k: worker.host_fingerprint().get(k) for k in harness.HOST_KEYS}
    record = harness.run_item(items[0], document['sha256'], tmp_path / 'direct', expected_host=expected)
    assert record['passed'] is False and 'fingerprint' in record['error'] and record['exit_code'] == 0
    on_disk = json.loads(harness.result_path_for(items[0], tmp_path / 'direct').read_text())
    assert on_disk['passed'] is False and on_disk['host_fingerprint_mismatch']['record']['uname']['release'] == 'other-kernel'
    acceptance = harness.replay(sample_path, tmp_path / 'attempt', workers=1)
    assert not acceptance['passed'] and acceptance['first_failure']['item_id'] == items[0]['item_id']
    stored = json.loads(harness.result_path_for(items[0], tmp_path / 'attempt').read_text())
    assert stored['passed'] is False
    # Without an acceptance (an interruption after that write), a resume in
    # the worker's environment cannot reuse it: the failure is on disk.
    (tmp_path / 'attempt' / 'acceptance.json').unlink()
    monkeypatch.setattr(harness.subprocess, 'run', real_run)
    real_fingerprint = worker.host_fingerprint
    monkeypatch.setattr(harness, 'host_fingerprint',
                        lambda: dict(real_fingerprint(), uname=dict(expected['uname'], release='other-kernel')))
    with pytest.raises(worker.RequalificationError, match='stays final'):
        harness.replay(sample_path, tmp_path / 'attempt', workers=1, resume=True)
    # A passing worker record with no runtime cannot pass either.
    monkeypatch.setattr(harness, 'host_fingerprint', real_fingerprint)
    def no_runtime(command, **kw):
        completed = real_run(command, **kw)
        path = Path(command[command.index('--result') + 1])
        record = json.loads(path.read_text())
        record.pop('runtime')
        path.write_bytes(worker.canonical(record) + b'\n')
        return completed
    monkeypatch.setattr(harness.subprocess, 'run', no_runtime)
    record = harness.run_item(items[1], document['sha256'], tmp_path / 'noruntime', expected_host=expected)
    assert record['passed'] is False and record['error'] == 'worker recorded no runtime'


def test_truncated_worker_file_and_any_exception_leave_a_failed_record(tmp_path, monkeypatch):
    """Fix 3 of round 2: an unreadable worker file is a failure with the exit
    code recorded, and any exception in the pool leaves a failed record."""
    jobs = fixture_jobs(2)
    src = source(tmp_path, 'trunc', jobs, selection='all')
    sample_path = tmp_path / 'sample.json'
    document = harness.freeze_sample([src], sample_path)
    items = harness.unseal(document)['items']
    real_run = harness.subprocess.run
    def truncating(command, **kw):
        completed = real_run(command, **kw)
        path = Path(command[command.index('--result') + 1])
        path.write_text(path.read_text()[:20])
        return subprocess.CompletedProcess(command, 1, completed.stdout, 'killed mid-write')
    monkeypatch.setattr(harness.subprocess, 'run', truncating)
    acceptance = harness.replay(sample_path, tmp_path / 'truncated', workers=1)
    assert not acceptance['passed']
    failed = acceptance['items'][0]
    assert failed['passed'] is False and failed['error'] == 'unreadable worker result' and failed['exit_code'] == 1
    assert json.loads(harness.result_path_for(items[0], tmp_path / 'truncated').read_text())['error'] == 'unreadable worker result'
    monkeypatch.setattr(harness.subprocess, 'run', real_run)
    def exploding(item, sample_sha256, output_dir, *args, **kw):
        raise RuntimeError('injected failure before the result was written')
    monkeypatch.setattr(harness, 'run_item', exploding)
    acceptance = harness.replay(sample_path, tmp_path / 'exploded', workers=1)
    assert not acceptance['passed'] and acceptance['first_failure']['error'].startswith('RuntimeError: injected')
    stored = json.loads(harness.result_path_for(items[0], tmp_path / 'exploded').read_text())
    assert stored['passed'] is False and stored['exit_code'] is None and stored['error'].startswith('RuntimeError')
    # If the per-item result already exists when the exception is caught, it
    # is not overwritten and the error still halts.
    def late(item, sample_sha256, output_dir, *args, **kw):
        harness.result_path_for(item, output_dir).parent.mkdir(parents=True, exist_ok=True)
        harness.result_path_for(item, output_dir).write_text('{"passed": true, "kept": true}')
        raise RuntimeError('after the write')
    monkeypatch.setattr(harness, 'run_item', late)
    acceptance = harness.replay(sample_path, tmp_path / 'late', workers=1)
    assert not acceptance['passed'] and 'not overwritten' in acceptance['items'][0]['note']
    assert json.loads(harness.result_path_for(items[0], tmp_path / 'late').read_text()) == {"passed": True, "kept": True}


def test_admission_proceeds_once_a_completed_job_is_collected(tmp_path, monkeypatch):
    """Fix 4 of round 2: a finished job's reservation is released before the
    next admission check, so the next item admits instead of timing out."""
    jobs = fixture_jobs(2)
    src = source(tmp_path, 'coll', jobs, selection='all')
    sample_path = tmp_path / 'sample.json'
    document = harness.freeze_sample([src], sample_path)
    items = harness.unseal(document)['items']
    fingerprint = {k: worker.host_fingerprint().get(k) for k in harness.HOST_KEYS}
    def fake_run_item(item, sample_sha256, output_dir, *args, **kw):
        import time as t
        t.sleep(.3)
        return dict(item_id=item['item_id'], job_id=item['job']['id'], passed=True, exit_code=0, checkout=item['checkout'],
                    runtime=dict(fingerprint, code_identity='x', source_manifest={'f': 'h'}))
    monkeypatch.setattr(harness, 'run_item', fake_run_item)
    reservation = harness.reservation_bytes(items[0], harness.DEFAULT_RESERVATIONS_GB)
    monkeypatch.setattr(harness, 'mem_available_bytes', lambda: int(1.5 * reservation))
    acceptance = harness.replay(sample_path, tmp_path / 'collected', workers=2, headroom_gb=0., admission_wait_seconds=5.)
    assert acceptance['passed'] and acceptance['executed'] == 2
    second = acceptance['admissions'][1]
    assert second['pending_reserved_bytes'] == 0 and second['waited_seconds'] > 0
    # A failure collected during the wait is the first failure, even when the
    # waiting item's admission is then refused for lack of memory.
    def failing_run_item(item, sample_sha256, output_dir, *args, **kw):
        import time as t
        t.sleep(.3)
        return dict(item_id=item['item_id'], job_id=item['job']['id'], passed=False, exit_code=1, checkout=item['checkout'],
                    error='injected mismatch', runtime=dict(fingerprint, code_identity='x', source_manifest={'f': 'h'}))
    monkeypatch.setattr(harness, 'run_item', failing_run_item)
    acceptance = harness.replay(sample_path, tmp_path / 'precedence', workers=2, headroom_gb=0., admission_wait_seconds=5.)
    assert not acceptance['passed'] and acceptance['first_failure']['item_id'] == items[0]['item_id']
    assert acceptance['first_failure']['error'] == 'injected mismatch'


def test_resume_refuses_a_record_from_another_environment(tmp_path):
    """Fix 2: a resumed record must carry this attempt's host fingerprint,
    compared before any scratch is touched."""
    jobs = fixture_jobs(2)
    src = source(tmp_path, 'env', jobs, selection='all')
    sample_path = tmp_path / 'sample.json'
    document = harness.freeze_sample([src], sample_path)
    items = harness.unseal(document)['items']
    out = tmp_path / 'attempt'
    record = harness.run_item(items[0], document['sha256'], out)
    assert record['runtime']['uname']['release'] == worker.host_fingerprint()['uname']['release']
    record['runtime']['uname'] = dict(record['runtime']['uname'], release='other-kernel')
    (out / 'results' / (items[0]['item_id'] + '.json')).write_bytes(worker.canonical(record) + b'\n')
    leftover = harness.scratch_for(items[1], document['sha256'])
    leftover.mkdir(parents=True)
    (leftover / 'partial.json').write_text('{}')
    with pytest.raises(worker.RequalificationError, match='different environment'):
        harness.replay(sample_path, out, workers=1, resume=True)
    assert (leftover / 'partial.json').exists() and not (out / 'acceptance.json').exists()
    fingerprint = worker.host_fingerprint()
    assert set(harness.HOST_KEYS) <= set(fingerprint)
    assert fingerprint['numpy'] and fingerprint['packages_sha256'] and fingerprint['uname']['release']


def test_worker_cap_group_barrier_and_memory_admission(tmp_path, monkeypatch):
    """Fix 5: the worker cap, one checkout at a time in order, and MemAvailable admission."""
    jobs = fixture_jobs(4)
    src = source(tmp_path, 'adm', jobs, selection='all')
    sample_path = tmp_path / 'sample.json'
    document = harness.freeze_sample([src], sample_path)
    cap = harness.worker_cap()
    assert 1 <= cap <= 31
    with pytest.raises(worker.RequalificationError, match='workers must be between'):
        harness.replay(sample_path, tmp_path / 'toomany', workers=cap + 1)
    with pytest.raises(worker.RequalificationError, match='no memory reservation'):
        harness.reservation_bytes(dict(kind='unknown'), harness.DEFAULT_RESERVATIONS_GB)
    # Reservations are keyed by kind, route and setting: a plain primary
    # validate reserves its own class, not the FV doubled class.
    plain = dict(kind='a4_validate', job=dict(config=dict(route='plain', a1_job=dict(config=dict(setting_name='primary')))))
    fv = dict(kind='a4_validate', job=dict(config=dict(route='fv', a1_job=dict(config=dict(setting_name='double_population')))))
    assert harness.reservation_bytes(plain, harness.DEFAULT_RESERVATIONS_GB) == int(3.35 * harness.GB)
    assert harness.reservation_bytes(fv, harness.DEFAULT_RESERVATIONS_GB) == int(26.8 * harness.GB)
    assert harness.reservation_key(plain)[0] == 'a4_validate.plain.primary'
    # Only the attempt's own interpreter may run the workers.
    with pytest.raises(worker.RequalificationError, match="attempt's own interpreter"):
        harness._worker_command(a.SIMULATION.parent, python=str(tmp_path / 'other-python'))
    # Two fake checkouts in a hand-sealed sample: every item of the first
    # finishes before any of the second starts, whatever the worker count.
    sample = harness.unseal(document)
    items = []
    for index, item in enumerate(sample['items']):
        items.append(dict(item, checkout='checkout-' + ('A' if index < 2 else 'B'), item_id=item['item_id']))
    two = dict(sample, items=items)
    two_path = tmp_path / 'two.json'
    a.atomic_json(two_path, harness.seal(two))
    fingerprint = {k: worker.host_fingerprint().get(k) for k in harness.HOST_KEYS}
    events = []
    def fake_run_item(item, sample_sha256, output_dir, *args, **kw):
        import time as t
        events.append((item['checkout'], 'start', t.perf_counter()))
        t.sleep(.2)
        events.append((item['checkout'], 'end', t.perf_counter()))
        return dict(item_id=item['item_id'], job_id=item['job']['id'], passed=True, exit_code=0, checkout=item['checkout'],
                    runtime=dict(fingerprint, code_identity='x', source_manifest={'f': 'h'}))
    monkeypatch.setattr(harness, 'run_item', fake_run_item)
    acceptance = harness.replay(two_path, tmp_path / 'barrier', workers=4)
    assert acceptance['passed'] and acceptance['checkout_order'] == ['checkout-A', 'checkout-B']
    last_a_end = max(t for c, e, t in events if c == 'checkout-A' and e == 'end')
    first_b_start = min(t for c, e, t in events if c == 'checkout-B' and e == 'start')
    assert last_a_end <= first_b_start
    assert acceptance['checkouts']['checkout-A']['source_manifest'] == {'f': 'h'}
    # Memory admission: below headroom plus reservation with nothing pending refuses, never hangs.
    monkeypatch.setattr(harness, 'mem_available_bytes', lambda: 1)
    events.clear()
    refused = harness.replay(two_path, tmp_path / 'lowmem', workers=2, headroom_gb=1.)
    assert not refused['passed'] and 'memory admission refused' in refused['first_failure']['error'] and not events
    # Admission waits while something is pending, then proceeds once memory frees.
    values = iter([1, 1, 10 ** 12])
    monkeypatch.setattr(harness, 'mem_available_bytes', lambda: next(values, 10 ** 12))
    waited = harness.admit(items[0], harness.DEFAULT_RESERVATIONS_GB, 0, {'f': items[1]}, wait_seconds=5., poll_seconds=.01)
    assert waited['waited_seconds'] > 0 and waited['available_bytes'] == 10 ** 12
    # A burst is bounded: pending items' reservations count against the
    # available memory before they have allocated, so a second item that does
    # not fit beside the first waits instead of being admitted.
    reservation = harness.reservation_bytes(items[0], harness.DEFAULT_RESERVATIONS_GB)
    monkeypatch.setattr(harness, 'mem_available_bytes', lambda: int(1.5 * reservation))
    assert harness.admit(items[0], harness.DEFAULT_RESERVATIONS_GB, 0, {})['pending_reserved_bytes'] == 0
    with pytest.raises(worker.RequalificationError, match='timed out'):
        harness.admit(items[1], harness.DEFAULT_RESERVATIONS_GB, 0, {'f': items[0]}, wait_seconds=.05, poll_seconds=.01)


def test_relative_output_and_sample_paths_resolve_before_any_write(tmp_path, monkeypatch):
    """Fix 6: a relative output directory and sample path work from any cwd."""
    jobs = fixture_jobs(2)
    src = source(tmp_path, 'rel', jobs, selection='all')
    sample_abs = tmp_path / 'sample.json'
    harness.freeze_sample([src], sample_abs)
    monkeypatch.chdir(tmp_path)
    acceptance = harness.replay(Path('sample.json'), Path('relative_out'), workers=1)
    assert acceptance['passed'] and acceptance['sample_path'] == str(sample_abs.resolve())
    assert (tmp_path / 'relative_out' / 'acceptance.json').is_file()
    assert all(r['exit_code'] == 0 for r in acceptance['items'])


def test_resume_keeps_passed_results_and_clears_an_interrupted_scratch(tmp_path):
    jobs = fixture_jobs(4)
    src = source(tmp_path, 'resume', jobs, selection='all')
    sample_path = tmp_path / 'sample.json'
    document = harness.freeze_sample([src], sample_path)
    items = harness.unseal(document)['items']
    out = tmp_path / 'attempt'
    # The interrupted attempt: one item completed and recorded, another left a
    # non-empty scratch behind, no acceptance record yet.
    first = harness.run_item(items[0], document['sha256'], out)
    assert first['passed']
    leftover = harness.scratch_for(items[1], document['sha256'])
    leftover.mkdir(parents=True)
    (leftover / 'partial.json').write_text('{}')
    without = harness.replay(sample_path, tmp_path / 'no_resume', workers=1)
    assert not without['passed'] and without['first_failure']['item_id'] == items[1]['item_id']
    assert any('not empty' in (r.get('error') or '') for r in without['items'])
    resumed = harness.replay(sample_path, out, workers=1, resume=True)
    assert resumed['passed'] and resumed['complete']
    assert resumed['resumed'] == [items[0]['item_id']]
    assert resumed['attempt_environment']['python'] == first['runtime']['python']
    # Every re-executed item is a restart event; only the interrupted one had scratch to clear.
    assert [r['item_id'] for r in resumed['restarts']] == [i['item_id'] for i in items[1:]]
    assert resumed['restarts'][0]['cleared_scratch'] == str(leftover) and resumed['restarts'][1]['cleared_scratch'] is None
    assert {k: resumed['items'][0][k] for k in ('item_id', 'before_sha256', 'after_sha256', 'passed')} ==         {k: first[k] for k in ('item_id', 'before_sha256', 'after_sha256', 'passed')}
    assert not leftover.exists()
    # A worker file left by a killed worker, with no per-item result, that
    # reports a pass is preserved by rename, never deleted, and the item is
    # re-executed; a refusal inside the pool becomes a failed record and a
    # halt, never an unhandled exception.
    killed = tmp_path / 'killed'
    harness.run_item(items[0], document['sha256'], killed)
    stale = harness.result_path_for(items[1], killed).with_suffix('.worker.json')
    stale.write_text('{"passed": true, "marker": "interrupted pass"}')
    before = stale.read_text()
    recovered = harness.replay(sample_path, killed, workers=1, resume=True)
    assert recovered['passed']
    preserved = stale.with_name(stale.stem.replace('.worker', '') + '.worker.interrupted.0.json')
    assert preserved.is_file() and preserved.read_text() == before
    assert any(r['preserved_worker_file'] == str(preserved) for r in recovered['restarts'])
    assert json.loads(stale.read_text())['before_sha256']  # the re-executed worker's own fresh file
    # A worker file that does not parse is preserved the same way.
    unparsed = tmp_path / 'unparsed'
    harness.run_item(items[0], document['sha256'], unparsed)
    garbage = harness.result_path_for(items[1], unparsed).with_suffix('.worker.json')
    garbage.write_text('{"passed": tr')
    recovered = harness.replay(sample_path, unparsed, workers=1, resume=True)
    assert recovered['passed'] and garbage.with_name(garbage.stem.replace('.worker', '') + '.worker.interrupted.0.json').read_text() == '{"passed": tr'
    blocked = tmp_path / 'blocked'
    (harness.result_path_for(items[0], blocked)).parent.mkdir(parents=True)
    harness.result_path_for(items[0], blocked).with_suffix('.worker.json').write_text('{}')
    with pytest.raises(worker.RequalificationError, match='worker files'):
        harness.replay(sample_path, blocked, workers=1)
    # A prior record for another sample is never reused, and a reported
    # failure in a prior attempt is final: resume refuses to run over it.
    with pytest.raises(worker.RequalificationError, match='another sample'):
        harness.resumable_record(items[0], 'x' * 64, out)
    failed = tmp_path / 'failed_attempt'
    record = harness.run_item(items[2], document['sha256'], failed)
    record.update(passed=False, after_sha256='0' * 64)
    (failed / 'results' / (items[2]['item_id'] + '.json')).write_bytes(worker.canonical(record) + b'\n')
    kept = harness.scratch_for(items[2], document['sha256'])
    kept.mkdir(parents=True, exist_ok=True)
    (kept / 'preserved.json').write_text('{}')
    with pytest.raises(worker.RequalificationError, match='stays final'):
        harness.replay(sample_path, failed, workers=1, resume=True)
    assert (kept / 'preserved.json').exists()
    assert not (failed / 'acceptance.json').exists()
    assert json.loads((failed / 'results' / (items[2]['item_id'] + '.json')).read_text())['after_sha256'] == '0' * 64
    assert resumed['checkouts'] and all('source_manifest' not in (r.get('runtime') or {}) for r in resumed['items'])
    assert all(r['runtime']['source_manifest_sha256'] == a.code_identity() for r in resumed['items'])


def test_worker_refuses_another_identity_and_a_dirty_scratch(in_process, tmp_path):
    src = source(tmp_path, 'one', fixture_jobs(1), selection='all')
    item = harness.unseal(harness.freeze_sample([src], tmp_path / 's.json'))['items'][0]
    scratch = tmp_path / 'scratch'
    with pytest.raises(worker.RequalificationError, match='producing identity'):
        worker.replay_item(dict(item, producing_code_hash='1' * 64), scratch=scratch)
    scratch.mkdir(parents=True)
    (scratch / 'leftover.json').write_text('{}')
    with pytest.raises(worker.RequalificationError, match='not empty'):
        worker.replay_item(item, scratch=scratch)
    with pytest.raises(worker.RequalificationError, match='inside the checkout'):
        worker.replay_item(item, scratch=Path(a.SIMULATION.parent) / 'elsewhere')
    # A sibling directory sharing the prefix is refused and never created.
    sibling = Path(str(a.ROOT) + '_other') / 'x'
    with pytest.raises(worker.RequalificationError, match='inside the checkout'):
        worker.replay_item(item, scratch=sibling)
    assert not sibling.exists() and not sibling.parent.exists()
    result = subprocess.run([sys.executable, '-B', '-E', str(harness.HERE / 'worker.py'), '--checkout', str(tmp_path),
                             '--item', 'x', '--scratch', 'y', '--result', str(tmp_path / 'r.json')],
                            capture_output=True, text=True)
    assert result.returncode != 0


# ---------------------------------------------------------------------------
# The A4 chain in-process, with the fit sibling mapped and fail-closed inputs
# ---------------------------------------------------------------------------

def a4_chain(tmp_path):
    from v3.offline_estimator import estimate
    calibration = a.read(a.SIMULATION / CAL_PATH)
    job = toy_table_job()
    job = a.stable_job(job['kind'], dict(job['config'], route='plain'), job['tag'], job['index'])
    src = tmp_path / 'source'
    result = estimate(job['config'], job['seed'], calibration)
    durable(src / 'tables_A1/table', job, result)
    a.atomic_json(src / 'tables_A1_manifest.json', a.seal(dict(jobs=[job], code_hash=a.code_identity(),
                  source_family={'code_hash': a.code_identity()}, tag='pilot', registered=False)))
    tables.assemble([dict(job=job, result=result, code_hash=a.code_identity())], calibration,
                    src / 'v3_rerun_tables_A1.json', 'sqrt', jobs=[job])
    probe = tmp_path / 'probe'
    a.atomic_json(probe / 'seeds.json', {'non_registered': True, 'seed': 76347036432783642})
    plan = tables.prepare_validation(src, CAL_PATH, probe_root=probe, settings_override=dict(TOY, census_measure=38))
    run = tmp_path / 'a4'
    for phase in plan['phases']:
        for j in [j for j in plan['jobs'] if j['config']['phase'] == phase]:
            durable(run / phase, j, runner.execute(j, root=run / phase))
    launch_root(run, plan)
    spec_path = tmp_path / 'a4_plan.json'
    a.atomic_json(spec_path, a.seal(plan))
    return plan, run, spec_path


def test_a4_chain_replays_through_mapped_inputs_and_fails_closed(in_process, tmp_path):
    plan, run, spec_path = a4_chain(tmp_path)
    kinds = {j['kind'] for j in plan['jobs']}
    assert {'a4_fit', 'a4_validate', 'a4_census'} <= kinds
    src = dict(name='a4', group='table', selection='all', producing_code_hash=a.code_identity(),
               checkout=str(a.SIMULATION.parent), original_simulation=str(a.SIMULATION),
               spec=str(spec_path), root=str(run))
    sample = harness.unseal(harness.freeze_sample([src], tmp_path / 'sample.json'))
    items = {i['job']['id']: i for i in sample['items']}
    validate = next(i for i in sample['items'] if i['kind'] == 'a4_validate' and i['job']['config']['route'] == 'plain')
    assert any('relative_to_scratch' in r for r in validate['inputs'])
    a1_root = str(Path(plan['jobs'][0]['config']['a1_source_root']).resolve())
    assert a1_root in validate['protected']
    for index, item in enumerate(sample['items']):
        record = worker.replay_item(item, scratch=tmp_path / 'scratch' / str(index))
        assert record['passed'], record
        assert not (tmp_path / 'scratch' / str(index)).exists()
    # Missing dependency: the plain validate job's fit sibling is not mapped,
    # so the producer cannot find it and the replay fails instead of passing.
    without_fit = deepcopy(validate)
    without_fit['inputs'] = [r for r in without_fit['inputs'] if 'relative_to_scratch' not in r]
    with pytest.raises((FileNotFoundError, ValueError, worker.RequalificationError)):
        worker.replay_item(without_fit, scratch=tmp_path / 'scratch' / 'nofit')
    # Unmapped-path access under a protected root fails closed in input_path.
    unmapped = deepcopy(validate)
    unmapped['inputs'] = [r for r in unmapped['inputs']
                          if not ('tables_A1' in r.get('path', '') and 'outputs' in r.get('path', ''))]
    with pytest.raises(ValueError, match='not in the verified snapshot'):
        worker.replay_item(unmapped, scratch=tmp_path / 'scratch' / 'unmapped')
    # A changed input is refused before anything runs.
    changed = deepcopy(validate)
    changed['inputs'][0]['sha256'] = '0' * 64
    with pytest.raises(worker.RequalificationError, match='input changed'):
        worker.replay_item(changed, scratch=tmp_path / 'scratch' / 'changed')
    # A perturbed census output with a rebound record is a reported mismatch.
    census = next(j for j in plan['jobs'] if j['kind'] == 'a4_census')
    perturb_output(run, census, lambda result: result.__setitem__('total_living', result['total_living'] + 1))
    sample = harness.unseal(harness.freeze_sample([src], tmp_path / 'sample2.json'))
    item = next(i for i in sample['items'] if i['job']['id'] == census['id'])
    record = worker.replay_item(item, scratch=tmp_path / 'scratch' / 'census', keep_scratch=True)
    assert not record['passed'] and record['before_sha256'] != record['after_sha256']
    assert (tmp_path / 'scratch' / 'census').exists()


# ---------------------------------------------------------------------------
# Extension replays: fresh replicates from recorded seeds, checkpoints compared
# ---------------------------------------------------------------------------

def test_a13_physical_replay_and_joint_checkpoint_output_perturbation(in_process, tmp_path, monkeypatch):
    from test_v3_a14 import history_fixture
    from test_v3_a13 import durable as make_durable
    from v3 import validation_extension_a13 as a13
    physical = a13.extension_stage
    *_, plan = history_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(a13, 'extension_stage', physical)
    job = plan['jobs'][0]
    original = tmp_path / 'fresh_original'
    result = a13.run_stage_job(job, original / a13.PHASE)
    assert result['replicates']
    make_durable(original / a13.PHASE, job, result)
    spec = dict(plan, jobs=[job])  # one executed job of the rehearsal plan
    launch_root(original, spec)
    spec_path = tmp_path / 'a13_plan.json'
    a.atomic_json(spec_path, a.seal(spec))
    src = dict(name='a13', group='a13', selection='all', producing_code_hash=a.code_identity(),
               checkout=str(a.SIMULATION.parent), original_simulation=str(a.SIMULATION),
               spec=str(spec_path), root=str(original))
    sample = harness.unseal(harness.freeze_sample([src], tmp_path / 'sample.json'))
    item = next(i for i in sample['items'] if i['job']['id'] == job['id'])
    checkpoint_paths = sorted((original / a13.PHASE / 'a13_checkpoints' / job['id']).glob('*.json'))
    assert len(checkpoint_paths) == len(result['replicates'])
    assert {r.get('path') for r in item['inputs']} >= {str(p.resolve()) for p in checkpoint_paths}
    before = {str(p): a.file_hash(p) for p in checkpoint_paths}
    record = worker.replay_item(item, scratch=tmp_path / 'scratch' / 'clean')
    assert record['passed'] and len(record['checkpoints']) == len(result['replicates'])
    assert all(c['passed'] and c['archived_sha256'] == c['fresh_sha256'] for c in record['checkpoints'])
    # Perturb the last recorded checkpoint and the recorded output together.
    # The replay recomputes from the seed, so both comparisons report a mismatch.
    changed = deepcopy(result)
    pair = next(iter(changed['replicates'][-1]['rows'].values()))[0]
    pair[0] += .01
    pair[1] += 1
    last = checkpoint_paths[-1]
    a.atomic_json(last, a.seal(dict(job_sha256=a.digest(job), replicate=changed['replicates'][-1])))
    perturb_output(original, job, lambda r: r.__setitem__('replicates', changed['replicates']))
    sample = harness.unseal(harness.freeze_sample([src], tmp_path / 'sample2.json'))
    item = next(i for i in sample['items'] if i['job']['id'] == job['id'])
    record = worker.replay_item(item, scratch=tmp_path / 'scratch' / 'perturbed', keep_scratch=True)
    assert not record['passed']
    assert record['before_sha256'] != record['after_sha256']
    assert not record['checkpoints'][-1]['passed'] and all(c['passed'] for c in record['checkpoints'][:-1])
    # Nothing was written back into the original root, and the family records
    # were never touched: the harness compares only.
    assert a.file_hash(last) != before[str(last)]
    for p in checkpoint_paths[:-1]:
        assert a.file_hash(p) == before[str(p)]
    assert not (original / 'a13_scientific_halt.json').exists()
    assert not list((tmp_path / 'scratch' / 'perturbed').rglob('*.json'))


def test_a14_physical_replay_maps_the_calibration_and_detects_perturbation(in_process, tmp_path, monkeypatch):
    """An A14 job built on the rehearsal A13 plan's real A1 output and fit, run
    by the producer's own stage through execute(), then replayed physically:
    the calibration TableTrace reads must be mapped, or the replay fails closed."""
    from test_v3_a14 import history_fixture
    from v3 import validation_extension_a13 as a13
    from v3 import validation_extension_a14 as a14
    physical = a13.extension_stage
    *_, plan = history_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr(a13, 'extension_stage', physical)
    old_config = plan['jobs'][0]['config']
    manifest = a14.seed_manifest([old_config['a1_job']], 24, [], rehearsal=True)
    config = {k: deepcopy(old_config[k]) for k in ('route', 'a1_source_root', 'a1_job', 'a1_source_code_hash', 'fit',
                                                   'trajectory_count', 'eligible_rows', 'M', 'settings_override')
              if k in old_config}
    config.update(phase=a14.PHASE, R_max=24, full_seed_manifest=manifest, forbidden_seeds=[], non_registered_rehearsal=True,
                  stream_seeds=[r['seed'] for r in manifest], plan_hash='rehearsal-a14', a14_inputs=[])
    job = a.stable_job(a14.KIND, config, 'v3_tables', 0)
    root = tmp_path / 'a14_physical'
    result = runner.execute(job, root=root / a14.PHASE)
    assert (result['stopped_on_visits'] or len(result['replicates']) == 24) and result['replicates'][0]['replicate'] == 20
    durable(root / a14.PHASE, job, result)
    spec = dict(schema='toy', code_hash=a.code_identity(), registered=False, jobs=[job], plan_hash='rehearsal-a14',
                seed_manifest=manifest)
    launch_root(root, spec)
    spec_path = tmp_path / 'a14_physical_spec.json'
    a.atomic_json(spec_path, a.seal(spec))
    src = a14_source(spec, name='a14p', group='a14', selection='all', producing_code_hash=a.code_identity(),
                     checkout=str(a.SIMULATION.parent), original_simulation=str(a.SIMULATION), spec=str(spec_path), root=str(root))
    item = harness.unseal(harness.freeze_sample([src], tmp_path / 'a14p.json'))['items'][0]
    assert item['plan_binding']['plan_hash'] == 'rehearsal-a14' and item['plan_binding']['job_ids'] == [job['id']]
    # Fix 3: the A14 source is bound to its original jobs, plan hash and seed
    # manifest hash; anything else is refused at freeze, and the worker refuses
    # a job outside the binding.
    with pytest.raises(worker.RequalificationError, match='needs a14_binding'):
        harness.freeze_sample([{k: v for k, v in src.items() if k != 'a14_binding'}], tmp_path / 'nobind.json')
    other = dict(src, a14_binding=dict(src['a14_binding'], job_ids=['a14_validate_plain_ext2_other']))
    with pytest.raises(worker.RequalificationError, match='differs from the bound original jobs'):
        harness.freeze_sample([other], tmp_path / 'otherjobs.json')
    with pytest.raises(worker.RequalificationError, match='bound plan hash'):
        harness.freeze_sample([dict(src, a14_binding=dict(src['a14_binding'], plan_hash='x'))], tmp_path / 'plan.json')
    with pytest.raises(worker.RequalificationError, match='seed manifest'):
        harness.freeze_sample([dict(src, a14_binding=dict(src['a14_binding'], seed_manifest_sha256='0' * 64))], tmp_path / 'sm.json')
    with pytest.raises(worker.RequalificationError, match='exactly its 4 original jobs'):
        harness.freeze_sample([dict(src, a14_binding={k: v for k, v in src['a14_binding'].items() if k != 'job_count'})],
                              tmp_path / 'count.json')
    unbound = deepcopy(item)
    unbound['plan_binding'] = dict(item['plan_binding'], plan_hash='another')
    with pytest.raises(worker.RequalificationError, match='outside the bound'):
        worker.replay_item(unbound, scratch=tmp_path / 'scratch' / 'a14p_unbound')
    relative = {r['relative_to_simulation'] for r in item['inputs'] if 'relative_to_simulation' in r}
    assert old_config['a1_job']['config']['calibration_path'] in relative
    # Declared input copies are verified against their declared hash and size
    # at freeze, as the producer's own execution_inputs verifies them.
    a1_output = Path(config['a1_source_root']) / 'tables_A1/table/outputs' / (config['a1_job']['id'] + '.json')
    copy = tmp_path / 'copy' / a1_output.name
    copy.parent.mkdir(parents=True)
    copy.write_bytes(a1_output.read_bytes())
    row = dict(source=str(a1_output), copy=str(copy), sha256=a.file_hash(copy), bytes=copy.stat().st_size)
    declared = a.stable_job(a14.KIND, dict(config, a14_inputs=[row]), 'v3_tables', 1)
    assert any(r['source'] == str(copy.resolve()) for r in harness.job_inputs(declared, root / a14.PHASE, a.SIMULATION))
    with pytest.raises(worker.RequalificationError, match='copy changed'):
        harness.job_inputs(a.stable_job(a14.KIND, dict(config, a14_inputs=[dict(row, sha256='0' * 64)]), 'v3_tables', 2),
                           root / a14.PHASE, a.SIMULATION)
    record = worker.replay_item(item, scratch=tmp_path / 'scratch' / 'a14p')
    assert record['passed'] and all(c['passed'] for c in record['checkpoints'])
    # Without the calibration mapping the producer's own input guard refuses.
    # The toy calibration sits outside v3/runs, so its directory is protected
    # here explicitly, as the registered layout under v3/runs protects it.
    cal_path = old_config['a1_job']['config']['calibration_path']
    stripped = deepcopy(item)
    stripped['inputs'] = [r for r in stripped['inputs'] if r.get('relative_to_simulation') != cal_path]
    stripped['protected'] = stripped['protected'] + [str((a.SIMULATION / cal_path).resolve().parent)]
    with pytest.raises(ValueError, match='not in the verified snapshot'):
        worker.replay_item(stripped, scratch=tmp_path / 'scratch' / 'a14p_nocal')
    changed = deepcopy(result)
    pair = next(iter(changed['replicates'][-1]['rows'].values()))[0]
    pair[0] += .01
    pair[1] += 1
    last = root / a14.PHASE / 'a14_checkpoints' / job['id'] / f"{changed['replicates'][-1]['replicate']:02d}.json"
    a.atomic_json(last, a.seal(dict(job_sha256=a.digest(job), replicate=changed['replicates'][-1])))
    perturb_output(root, job, lambda r: r.__setitem__('replicates', changed['replicates']))
    item = harness.unseal(harness.freeze_sample([src], tmp_path / 'a14p2.json'))['items'][0]
    record = worker.replay_item(item, scratch=tmp_path / 'scratch' / 'a14p2')
    assert not record['passed'] and not record['checkpoints'][-1]['passed']


def a14_job(tmp_path, monkeypatch, count=6):
    """A minimal A14 job, run by the producer's own stage function with a
    deterministic stub for the trajectory computation."""
    from test_v3_a13 import source_job, parameters
    from v3 import validation_extension_a14 as a14
    src = source_job()
    manifest = a14.seed_manifest([src], 24, [], rehearsal=True)
    a1_root = tmp_path / 'a1_root'
    for directory in ('outputs', 'records'):
        a.atomic_json(a1_root / 'tables_A1/table' / directory / (src['id'] + '.json'), dict(placeholder=directory))
    config = dict(phase=a14.PHASE, a1_job=src, a1_source_root=str(a1_root), a1_source_code_hash=a.code_identity(),
                  eligible_rows={'a': parameters(3), 'b': parameters(2)}, M=20, R_max=24, route='plain',
                  full_seed_manifest=manifest, forbidden_seeds=[], stream_seeds=[m['seed'] for m in manifest],
                  trajectory_count=count, plan_hash='test', fit=a.seal({'a1_job_id': src['id'], 'rows': []}),
                  a14_inputs=[], non_registered_rehearsal=True)
    job = a.stable_job(a14.KIND, config, 'v3_tables', 0)
    def stage(a1, fit, rows, seed, override=None):
        # Deterministic in the seed: one visit per trajectory whose weight is the seed's low bits.
        return dict(count=count, settings={}, rows={k: [[float(seed % 97) / 100., 1]] * count for k in rows})
    monkeypatch.setattr(a14, 'extension_stage', stage)
    monkeypatch.setattr(a14.a13.a4, '_load_a1', lambda *args: {})
    return job


def test_a14_replay_recomputes_from_recorded_seeds(in_process, tmp_path, monkeypatch):
    from v3 import validation_extension_a14 as a14
    job = a14_job(tmp_path, monkeypatch)
    root = tmp_path / 'a14_root'
    result = runner.execute(job, root=root / a14.PHASE)
    assert result['stopped_on_visits'] and 1 <= len(result['replicates']) < job['config']['R_max']
    durable(root / a14.PHASE, job, result)
    spec = dict(schema='toy', code_hash=a.code_identity(), registered=False, jobs=[job], plan_hash='test',
                seed_manifest=job['config']['full_seed_manifest'])
    launch_root(root, spec)
    spec_path = tmp_path / 'a14_spec.json'
    a.atomic_json(spec_path, a.seal(spec))
    src = a14_source(spec, name='a14', group='a14', selection='all', producing_code_hash=a.code_identity(),
                     checkout=str(a.SIMULATION.parent), original_simulation=str(a.SIMULATION),
                     spec=str(spec_path), root=str(root))
    item = harness.unseal(harness.freeze_sample([src], tmp_path / 'sample.json'))['items'][0]
    seen = []
    original_stage = a14.extension_stage
    monkeypatch.setattr(a14, 'extension_stage', lambda *args, **kw: (seen.append(args[3]), original_stage(*args, **kw))[1])
    record = worker.replay_item(item, scratch=tmp_path / 'scratch' / 'a14')
    assert record['passed'] and seen == [r['seed'] for r in result['replicates']]
    assert all(c['passed'] for c in record['checkpoints']) and len(record['checkpoints']) == len(result['replicates'])
    # Joint perturbation of the recorded checkpoint and output is detected.
    changed = deepcopy(result)
    changed['replicates'][0]['rows']['a'][0][0] += .5
    checkpoint = root / a14.PHASE / 'a14_checkpoints' / job['id'] / '20.json'
    a.atomic_json(checkpoint, a.seal(dict(job_sha256=a.digest(job), replicate=changed['replicates'][0])))
    perturb_output(root, job, lambda r: r.__setitem__('replicates', changed['replicates']))
    item = harness.unseal(harness.freeze_sample([src], tmp_path / 'sample2.json'))['items'][0]
    record = worker.replay_item(item, scratch=tmp_path / 'scratch' / 'a14b')
    assert not record['passed'] and not record['checkpoints'][0]['passed']
    # A recorded replicate sequence that continues past the registered stop is
    # refused by the producer's own validate_replicates, never replayed.
    extended = deepcopy(result)
    extended['replicates'].append(dict(extended['replicates'][-1], replicate=extended['replicates'][-1]['replicate'] + 1,
                                       seed=job['config']['stream_seeds'][len(extended['replicates'])]))
    perturb_output(root, job, lambda r: r.__setitem__('replicates', extended['replicates']))
    item = harness.unseal(harness.freeze_sample([src], tmp_path / 'sample3.json'))['items'][0]
    with pytest.raises(ValueError, match='past stop'):
        worker.replay_item(item, scratch=tmp_path / 'scratch' / 'a14c')
