"""A19 draft 3: a time budget may refuse to start and never stops running work.

T1 the dispatch stop drains instead of killing; T2 a worker never discards a
finished result because of time; T3 a projection refuses only before any
scientific dispatch of its launch; T4 the configuration window is a planning
target; T5 the nondeterminism recheck never manufactures a failure from time;
T6 the multihost wall ceiling is a dispatch stop with drain; P1 to P3 the A11
proof-path fixes. Every runner test here spawns real worker processes.
"""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import threading
import time

import pytest
from test_v3_paths import tmp_path
from test_v3_multihost_a11 import (SETTINGS, FINGERPRINT, initialize, spec_fixture, join, ready, claim, finish)
from v3 import artifacts as a, production_runner as pr, multihost_a11 as m, host_a11 as h
from v3 import compatibility_a10 as c, worker_control as wc, tables_a10 as tables


def local_settings(workers=1, budget=4):
    # A four-CPU budget admits the three-worker control target the dispatch
    # tests write; fixed or measured selections keep each test's worker count.
    return dict(profile='local', workers=workers, threads=1, cpu_budget=budget, mode='normal', caps=pr.caps('local', budget))


def control(root, **extra):
    a.atomic_json(root / 'control.json', dict(mode='normal', max_workers=3, stop_dispatch=False, interrupt_now=False, **extra))


def events(root):
    path = root / 'events.jsonl'
    if not path.exists():
        return []
    rows = []
    for line in path.read_text().splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue  # A line still being appended by the dispatcher.
    return rows


# --------------------------------------------------------------------------
# T1: the dispatch stop drains
# --------------------------------------------------------------------------

def test_deadline_drains_the_running_job_and_leaves_the_pending_job_unstarted(tmp_path):
    control(tmp_path)
    jobs = [a.stable_job('fixture', {'seconds': 4.}, 'validation', i) for i in range(2)]
    code = a.code_identity()
    deadline = time.time() + 1.5
    result = pr.dispatch(tmp_path, jobs, code, local_settings(), deadline, fixed={'workers': 1, 'threads': 1})
    assert result['reason'] == 'deadline'
    assert (result['total'], result['completed'], result['running'], result['pending']) == (2, 1, 0, 1)
    rows = events(tmp_path)
    dispatched = [e['job'] for e in rows if e['event'] == 'dispatch']
    assert len(dispatched) == 1
    first = next(j for j in jobs if j['id'] == dispatched[0])
    other = next(j for j in jobs if j['id'] != dispatched[0])
    # The job running at the deadline finished after it and was recorded exactly
    # as any other completion: output, completion record and a complete event.
    output = pr.completed(tmp_path, first, code)
    assert output is not None and output['result'] == dict(seed=first['seed'], fixture=True)
    assert output['finished_epoch'] > deadline
    assert a.read(tmp_path / 'records' / (first['id'] + '.json'))['status'] == 'complete'
    assert [e['job'] for e in rows if e['event'] == 'complete'] == [first['id']]
    assert not any(e['event'] == 'restart_required' for e in rows)
    # The pending job was never dispatched and has no output.
    assert pr.completed(tmp_path, other, code) is None
    assert not (tmp_path / 'outputs' / (other['id'] + '.json')).exists()
    # One deadline_drain event at the start, the overrun at the end.
    drain = next(e for e in rows if e['event'] == 'deadline_drain')
    assert drain['active'] == [first['id']] and drain['pending'] == 1 and drain['deadline_epoch'] == deadline
    end = next(e for e in rows if e['event'] == 'deadline_drain_end')
    assert end['overrun_seconds'] > 1. and end['completed_during_drain'] == 1 and end['pending'] == 1
    assert result['deadline_drain']['active'] == [first['id']] and result['deadline_drain']['pending'] == 1
    assert a.read(tmp_path / 'status.json')['reason'] == 'deadline'
    assert not a.read(tmp_path / 'active.json')['pids']
    # Resumption completes the pending job and keeps the drained one as is.
    preserved = a.file_hash(tmp_path / 'outputs' / (first['id'] + '.json'))
    resumed = pr.dispatch(tmp_path, jobs, code, local_settings(), time.time() + 60, fixed={'workers': 1, 'threads': 1})
    assert resumed['reason'] == 'complete' and resumed['completed'] == 2
    assert a.file_hash(tmp_path / 'outputs' / (first['id'] + '.json')) == preserved
    assert not any(e['event'] == 'restart_required' for e in events(tmp_path))


def test_deadline_already_passed_dispatches_nothing_and_ends_with_reason_deadline(tmp_path):
    control(tmp_path)
    jobs = [a.stable_job('fixture', {'seconds': .01}, 'validation', i) for i in range(2)]
    result = pr.dispatch(tmp_path, jobs, a.code_identity(), local_settings(), time.time() - 1, fixed={'workers': 1, 'threads': 1})
    assert result['reason'] == 'deadline' and result['completed'] == 0 and result['pending'] == 2
    rows = events(tmp_path)
    assert not any(e['event'] == 'dispatch' for e in rows)
    assert next(e for e in rows if e['event'] == 'deadline_drain')['active'] == []
    assert next(e for e in rows if e['event'] == 'deadline_drain_end')['completed_during_drain'] == 0


def ordered_jobs(seconds, pending_seconds):
    """Fixture jobs whose dispatch order (equal estimates sort by id) puts the
    pending job last, so the first len(seconds) start before the deadline."""
    running = [a.stable_job('fixture', {'seconds': s}, 'validation', i) for i, s in enumerate(seconds)]
    index = len(seconds)
    while True:
        pending = a.stable_job('fixture', {'seconds': pending_seconds}, 'validation', index)
        if pending['id'] > max(j['id'] for j in running):
            return running, pending
        index += 1


def test_a_screen_failure_during_a_deadline_drain_still_stops_at_once(tmp_path):
    # Two jobs running at the deadline. The short one finishes during the drain
    # and is recorded and screened exactly as any completion; its screen fails,
    # which is a scientific first-failure stop: the long one is stopped at once.
    control(tmp_path)
    (short, long_), pending = ordered_jobs((2., 30.), .01)
    code = a.code_identity()
    screened = []

    def screen(job, output):
        screened.append(job['id'])
        return 'injected failure' if job['id'] == short['id'] else None

    began = time.time()
    result = pr.dispatch(tmp_path, [short, long_, pending], code, local_settings(workers=2, budget=4), time.time() + 1.,
                         fixed={'workers': 2, 'threads': 1}, completion_screen=screen)
    assert time.time() - began < 25  # Not the 30 s job.
    assert result['reason'] == 'screen_failure' and result['completed'] == 1
    rows = events(tmp_path)
    assert sorted(e['job'] for e in rows if e['event'] == 'dispatch') == sorted([short['id'], long_['id']])
    drain = next(e for e in rows if e['event'] == 'deadline_drain')
    assert sorted(drain['active']) == sorted([short['id'], long_['id']]) and drain['pending'] == 1
    # The drained job: output, completion record, complete event, memory
    # observation and completion screen, as any other completion.
    assert pr.completed(tmp_path, short, code)['finished_epoch'] > drain['deadline_epoch']
    assert a.read(tmp_path / 'records' / (short['id'] + '.json'))['status'] == 'complete'
    assert [e['job'] for e in rows if e['event'] == 'complete'] == [short['id']]
    assert (tmp_path / 'memory_reservations.json').exists()
    assert screened == [short['id']]
    assert a.read(tmp_path / 'screen_failure.json')['job'] == short['id']
    assert [e['job'] for e in rows if e['event'] == 'restart_required'] == [long_['id']]
    assert next(e for e in rows if e['event'] == 'restart_required')['reason'] == 'screen_failure'
    assert pr.completed(tmp_path, long_, code) is None and pr.completed(tmp_path, pending, code) is None
    # A19 (F4): the drain record says when and why it ended early.
    end = next(e for e in rows if e['event'] == 'deadline_drain_end')
    assert end['ended_by'] == 'screen_failure' and end['completed_during_drain'] == 1
    assert result['deadline_drain']['ended_by'] == 'screen_failure' and result['deadline_drain']['overrun_seconds'] > 0


def test_interrupt_now_during_a_deadline_drain_still_stops_live_workers(tmp_path):
    control(tmp_path)
    jobs = [a.stable_job('fixture', {'seconds': 30.}, 'validation', i) for i in range(2)]

    def interrupt():
        end = time.time() + 30
        while time.time() < end:
            if any(e['event'] == 'deadline_drain' for e in events(tmp_path)):
                a.atomic_json(tmp_path / 'control.json', dict(a.read(tmp_path / 'control.json'), interrupt_now=True))
                return
            time.sleep(.05)

    thread = threading.Thread(target=interrupt)
    thread.start()
    began = time.time()
    result = pr.dispatch(tmp_path, jobs, a.code_identity(), local_settings(), time.time() + 1., fixed={'workers': 1, 'threads': 1})
    thread.join(5)
    assert result['reason'] == 'interrupted' and result['completed'] == 0
    assert time.time() - began < 25  # Not the 30 s job: the interruption was immediate.
    rows = events(tmp_path)
    assert any(e['event'] == 'deadline_drain' for e in rows)
    assert any(e['event'] == 'restart_required' and e['reason'] == 'interrupted' for e in rows)
    # A19 (F4): the drain record says when and why it ended early.
    drain = result['deadline_drain']
    assert drain['ended_by'] == 'interrupted' and drain['ended_epoch'] >= drain['epoch'] and drain['overrun_seconds'] > 0
    assert drain['completed_during_drain'] == 0
    assert next(e for e in rows if e['event'] == 'deadline_drain_end')['ended_by'] == 'interrupted'


class _SlowStarts:
    """A stand-in for production_runner.mp whose contexts record each process
    construction (immediately after the pre-start deadline check) and whose
    starts can be made to cost time, with real spawned workers underneath."""

    def __init__(self, real, starts):
        self.real, self.starts = real, starts

    def get_context(self, method=None):
        outer = self
        context = self.real.get_context(method)

        class Context:
            def Process(self, *args, **kwargs):
                outer.starts.append(time.time())
                return context.Process(*args, **kwargs)

            def __getattr__(self, name):
                return getattr(context, name)

        return Context()


@pytest.mark.parametrize('cost', ['after_start', 'before_start'])
def test_no_pending_job_starts_after_the_deadline_inside_one_fill_cycle(tmp_path, monkeypatch, cost):
    # A19 (F3): the reviewer's case. Three slots, a one-second stop, and starts
    # that cost 0.6 s: formerly the third start came at 1.2 s, after the stop.
    # "after_start" puts the cost after each start (the dispatch event);
    # "before_start" puts it in the admission work before each start (the
    # memory read), which a check at the top of the fill cycle would miss.
    control(tmp_path)
    jobs = [a.stable_job('fixture', {'seconds': .01}, 'validation', i) for i in range(5)]
    starts = []
    monkeypatch.setattr(pr, 'mp', _SlowStarts(pr.mp, starts))
    if cost == 'after_start':
        real_event = pr.event

        def slow_event(root, kind, **fields):
            real_event(root, kind, **fields)
            if kind == 'dispatch':
                time.sleep(.6)

        monkeypatch.setattr(pr, 'event', slow_event)
    else:
        real_memory = pr.mem_available_bytes

        def slow_memory():
            time.sleep(.6)
            return real_memory()

        monkeypatch.setattr(pr, 'mem_available_bytes', slow_memory)
    deadline = time.time() + 1.
    result = pr.dispatch(tmp_path, jobs, a.code_identity(), local_settings(workers=3, budget=4), deadline,
                         fixed={'workers': 3, 'threads': 1})
    assert result['reason'] == 'deadline'
    assert all(started < deadline for started in starts), [round(x - deadline, 3) for x in starts]
    rows = events(tmp_path)
    dispatched = [e['job'] for e in rows if e['event'] == 'dispatch']
    assert len(dispatched) == len(starts) < 3 and result['completed'] == len(starts)
    drain = next(e for e in rows if e['event'] == 'deadline_drain')
    assert drain['pending'] == len(jobs) - len(starts) and result['pending'] == len(jobs) - len(starts)
    assert all(pr.completed(tmp_path, j, a.code_identity()) is None for j in jobs if j['id'] not in dispatched)


def test_a_signal_during_a_deadline_drain_still_stops_live_workers(tmp_path):
    # dispatch installs its own SIGINT/SIGTERM handlers. Delivering SIGTERM to
    # the handler it installed (what the interpreter does on a real signal)
    # during the drain stops the running job at once.
    import signal
    control(tmp_path)
    jobs = [a.stable_job('fixture', {'seconds': 30.}, 'validation', i) for i in range(2)]
    original = signal.getsignal(signal.SIGTERM)

    def deliver():
        end = time.time() + 30
        while time.time() < end:
            handler = signal.getsignal(signal.SIGTERM)
            if handler is not original and any(e['event'] == 'deadline_drain' for e in events(tmp_path)):
                handler(signal.SIGTERM, None)
                return
            time.sleep(.05)

    thread = threading.Thread(target=deliver)
    thread.start()
    began = time.time()
    result = pr.dispatch(tmp_path, jobs, a.code_identity(), local_settings(), time.time() + 1., fixed={'workers': 1, 'threads': 1})
    thread.join(5)
    assert result['reason'] == 'interrupted' and result['completed'] == 0
    assert time.time() - began < 25
    rows = events(tmp_path)
    assert any(e['event'] == 'deadline_drain' for e in rows)
    assert [e['reason'] for e in rows if e['event'] == 'restart_required'] == ['interrupted']
    assert signal.getsignal(signal.SIGTERM) is original  # Restored on exit.


# --------------------------------------------------------------------------
# T2: a worker never discards a finished result because of time
# --------------------------------------------------------------------------

def test_worker_records_a_completion_after_a_past_completion_deadline(tmp_path):
    job = a.stable_job('fixture', {'seconds': 0}, 'validation', 0)
    code = a.code_identity()
    pr.worker(str(tmp_path), job, code, 1, False, None, time.time() - 1)
    output = pr.completed(tmp_path, job, code)
    assert output is not None and output['result'] == dict(seed=job['seed'], fixture=True)
    assert a.read(tmp_path / 'records' / (job['id'] + '.json'))['status'] == 'complete'


# --------------------------------------------------------------------------
# T3 and T5 on the single-host launch, T4 on both launch paths
# --------------------------------------------------------------------------

def a4_fixture_spec(phases=('fit',), seconds=.05, wall_seconds=300, configuration_seconds=60):
    base = dict(route='plain', a1_job={'config': {'settings': dict(runs_per_group=2, particles=2, burn=30, measure=8)}})
    jobs = [a.stable_job('fixture', dict(phase=p, seconds=seconds, **base), 'validation', i) for p in phases for i in range(1)]
    profiles = {p: dict(kind='fixture', config=dict(phase=p, seconds=.005, **base), workers_local=[1],
                        workers_x2=[8, 12, 16, 24, 32], threads=[1], rounds=1, jobs_per_worker=1) for p in phases}
    return dict(schema='v3-A4-validation-1', registered=False, instrument=tables.NOMINAL.declaration(),
                code_hash=a.code_identity(), tag='validation', jobs=jobs, phases=list(phases), configuration=profiles,
                wall_seconds=wall_seconds, cleanup_reserve_seconds=0, configuration_seconds=configuration_seconds,
                publication=None)


def canned_configuration(monkeypatch):
    """One valid one-worker measurement per phase, without dispatch. Fixture
    jobs are validation-only (execute refuses them under the configuration tag),
    and these tests are about the launch, not the configuration test."""
    def configuration_test(root, phase, profile, settings, deadline, launch_number, **kwargs):
        return [dict(workers=1, requested_workers=1, threads=1, completed=1, wall_seconds=.1, valid=True, round=0,
                     job_seconds=[.05], class_peaks_gb={})]

    monkeypatch.setattr(pr, 'configuration_test', configuration_test)


def scripted_projection(monkeypatch, fits):
    calls = []
    script = list(fits)

    def projection(spec, configuration, effective_workers, run_root, code, from_index, now, deadline):
        value = script.pop(0)
        calls.append(spec['phases'][from_index])
        return {'total_seconds': 1. if value else 1e9, 'remaining_budget_seconds': deadline - now, 'phases': {}, 'fits': value}

    monkeypatch.setattr(pr, 'a4_projection', projection)
    return calls


def test_projection_refuses_before_dispatch_and_is_advisory_after_it(tmp_path, monkeypatch):
    spec = a4_fixture_spec(phases=('fit', 'census'))
    path = tmp_path / 'spec.json'
    a.atomic_json(path, a.seal(spec))
    root = tmp_path / 'run'
    # Launch 1: the projection fits before fit, then fails before census, after
    # fit has dispatched a scientific job: advisory, and the launch completes.
    canned_configuration(monkeypatch)
    calls = scripted_projection(monkeypatch, [True, False])
    result = pr.launch(path, root, local_settings())
    assert result['complete'] and calls == ['fit', 'census']
    record = a.read(root / 'launches.json')[-1]
    assert record['complete'] and record['first_scientific_dispatch']['phase'] == 'fit'
    assert record['first_scientific_dispatch']['by'] == 'phase dispatch'
    assert [p['disposition'] for p in record['projections']] == ['fits', 'advisory']
    assert record['projections'][1]['scientific_dispatched'] is True and record['projections'][1]['fits'] is False
    assert record['projections'][1]['total_seconds'] == 1e9 and record['projections'][1]['remaining_budget_seconds'] > 0
    advisory = [e for e in events(root) if e['event'] == 'projection_exceeds_budget']
    assert len(advisory) == 1 and advisory[0]['advisory'] is True and advisory[0]['before_phase'] == 'census'
    assert all(a.read(root / p / 'nondeterminism_check.json')['matched'] for p in spec['phases'])
    assert all(pr.completed(root / j['config']['phase'], j, a.code_identity()) for j in spec['jobs'])
    # Launch 2 is a new launch record: its first projection is pre-dispatch
    # again and may refuse, even though every job is already complete.
    calls = scripted_projection(monkeypatch, [False])
    again = pr.launch(path, root, local_settings())
    assert again['reason'] == 'projection_exceeds_budget' and not again['complete'] and calls == ['fit']
    last = a.read(root / 'launches.json')[-1]
    assert last['stopped'] == 'projection_exceeds_budget' and 'first_scientific_dispatch' not in last
    assert last['projections'][0]['disposition'] == 'refused' and last['projections'][0]['scientific_dispatched'] is False
    assert len(a.read(root / 'launches.json')) == 2


def test_a_recheck_this_launch_dispatched_makes_a_later_projection_advisory(tmp_path, monkeypatch):
    # The fit job completed before this launch, so the launch's fit dispatch
    # starts nothing; the fit recheck is the launch's first scientific dispatch
    # (a re-execution of a manifest job), and the projection before census,
    # which fails, is advisory.
    spec = a4_fixture_spec(phases=('fit', 'census'))
    path = tmp_path / 'spec.json'
    a.atomic_json(path, a.seal(spec))
    root = tmp_path / 'run'
    fit = next(j for j in spec['jobs'] if j['config']['phase'] == 'fit')
    pr.worker(str(root / 'fit'), fit, a.code_identity(), 1, False, None)
    canned_configuration(monkeypatch)
    calls = scripted_projection(monkeypatch, [True, False])
    result = pr.launch(path, root, local_settings())
    assert result['complete'] and calls == ['fit', 'census']
    record = a.read(root / 'launches.json')[-1]
    assert record['outcomes']['fit']['maximum_active'] == 0 and record['outcomes']['census']['maximum_active'] == 1
    first = record['first_scientific_dispatch']
    assert (first['phase'], first['by'], first['job']) == ('fit', 'nondeterminism recheck', fit['id'])
    assert [p['disposition'] for p in record['projections']] == ['fits', 'advisory']
    assert a.read(root / 'fit' / 'nondeterminism_check.json')['matched'] is True


def test_configuration_trials_dispatch_against_the_launch_deadline_and_record_the_planning_figure(tmp_path, monkeypatch):
    spec = a4_fixture_spec(configuration_seconds=1, wall_seconds=300)
    path = tmp_path / 'spec.json'
    a.atomic_json(path, a.seal(spec))
    root = tmp_path / 'run'
    seen = {}

    def configuration_test(root_, phase, profile, settings, deadline, launch_number, **kwargs):
        seen['deadline'] = deadline
        time.sleep(1.2)  # Past the one-second planning target: nothing aborts.
        raise RuntimeError('stop after the deadline was observed')

    monkeypatch.setattr(pr, 'configuration_test', configuration_test)
    with pytest.raises(RuntimeError, match='after the deadline was observed'):
        pr.launch(path, root, local_settings())
    budget = a.read(root / 'budget.json')
    assert seen['deadline'] == budget['deadline_epoch'] == budget['start_epoch'] + 300
    assert seen['deadline'] - time.time() > 200  # Not time.time() + configuration_seconds.
    planning = a.read(root / 'launches.json')[-1]['configuration_planning']
    assert planning['planning_seconds'] == 1 and planning['elapsed_seconds'] >= 1.2
    assert planning['within_planning_target'] is False and planning['finished_epoch'] >= planning['started_epoch']


def test_recheck_reached_by_the_deadline_ends_the_launch_incomplete_without_a_failure(tmp_path, monkeypatch):
    # One eight-second job in a six-second launch: the job is running at the
    # deadline, drains to completion, and the recheck then cannot run because
    # the dispatch stop has passed. Nothing is written as a failure or as a
    # passed check; the launch ends incomplete with reason deadline.
    spec = a4_fixture_spec(seconds=8., wall_seconds=6)
    path = tmp_path / 'spec.json'
    a.atomic_json(path, a.seal(spec))
    root = tmp_path / 'run'
    canned_configuration(monkeypatch)
    result = pr.launch(path, root, local_settings())
    assert not result['complete'] and result['reason'] == 'deadline'
    assert result['nondeterminism_check_not_run']['phase'] == 'fit'
    job = spec['jobs'][0]
    assert pr.completed(root / 'fit', job, a.code_identity()) is not None
    outcome = result['outcomes']['fit']
    assert outcome['reason'] == 'deadline' and outcome['completed'] == 1
    assert outcome['deadline_drain']['active'] == [job['id']] and outcome['deadline_drain']['overrun_seconds'] > 0
    assert any(e['event'] == 'deadline_drain' and e['active'] == [job['id']] for e in events(root / 'fit'))
    not_run = a.read(root / 'fit' / 'nondeterminism_check_not_run.json')
    assert not_run['not_run'] and not_run['reason'] == 'deadline' and not_run['candidate'] == job['id']
    assert not_run['dispatched'] is False and 'matched' not in not_run
    assert not (root / 'fit' / 'nondeterminism_check.json').exists()
    assert not (root / 'fit' / 'nondeterminism_failure.json').exists()
    assert not any(root.glob('*scientific_halt.json'))
    record = a.read(root / 'launches.json')[-1]
    assert record['complete'] is False and record['stopped'] == 'deadline'
    assert record['nondeterminism_check_not_run']['phase'] == 'fit'
    assert record['configuration_planning']['within_planning_target'] is True
    # A resumption after the frozen deadline is a refusal to start, as before.
    with pytest.raises(RuntimeError, match='expired'):
        pr.launch(path, root, local_settings())


def test_host_configuration_trials_use_the_coordinator_deadline(tmp_path, monkeypatch):
    spec = spec_fixture(2)
    spec['configuration_seconds'] = 1
    _, root, spec = initialize(tmp_path, spec)
    seen = {}

    class Observed(Exception):
        pass

    def configuration_test(root_, phase, profile, settings, deadline, launch_number, **kwargs):
        seen['deadline'] = deadline
        raise Observed

    monkeypatch.setattr(pr, 'configuration_test', configuration_test)
    with pytest.raises(Observed):
        h.run_host(h.Loopback(root), tmp_path / 'host_alpha', SETTINGS, host='alpha', environment=FINGERPRINT)
    # A19 (F4): the failure path records its elapsed time and the failure.
    planning = a.read(tmp_path / 'host_alpha' / 'configuration_planning.json')
    assert 'Observed' in planning['failure'] and planning['current_phase'] == 'toy' and planning['elapsed_seconds'] >= 0
    budget = a.read(root / 'budget.json')
    assert seen['deadline'] == budget['deadline_epoch']
    assert seen['deadline'] - time.time() > 200
    assert m.rpc(root, {'op': 'inspect'})['status']['deadline_epoch'] == budget['deadline_epoch']


def test_host_records_its_configuration_time_against_the_planning_target(tmp_path):
    # Real configuration trials need a kind execute admits under the
    # configuration tag; a zero-step rerun is the loopback tests' choice.
    spec = spec_fixture(2)
    cfg = dict(phase='toy', steps=0, model=dict(n_agents=8, carrying_capacity=80, instrument=tables.NOMINAL.declaration()))
    spec['jobs'] = [a.stable_job('rerun', cfg, 'validation', i) for i in range(2)]
    spec['pull_dispatch']['job_classes'] = {j['id']: str(i) for i, j in enumerate(spec['jobs'])}
    spec['configuration']['toy'].update(kind='rerun', config=cfg)
    spec['configuration_seconds'] = 1
    _, root, spec = initialize(tmp_path, spec)
    scratch = tmp_path / 'host_alpha'
    h.run_host(h.Loopback(root), scratch, SETTINGS, host='alpha', environment=FINGERPRINT, max_seconds=60)
    planning = a.read(scratch / 'configuration_planning.json')
    assert planning['planning_seconds'] == 1 and planning['elapsed_seconds'] > 0 and set(planning['phases']) == {'toy'}
    assert planning['deadline_epoch'] <= a.read(root / 'budget.json')['deadline_epoch']
    session = next(iter(m.read_state(root)['sessions'].values()))
    assert session['configuration_planning']['toy']['planning_seconds'] == 1
    assert session['configuration_planning']['toy']['elapsed_seconds'] == planning['phases']['toy']


# --------------------------------------------------------------------------
# T5: the recheck itself
# --------------------------------------------------------------------------

def recheck_fixture(tmp_path, deadline_epoch, seconds=None):
    config = dict(phase='toy') if seconds is None else dict(phase='toy', seconds=seconds)
    job = a.stable_job('fixture', config, 'validation', 0)
    s = wc.settings(dict(profile='local', workers=1, threads=1, cpu_budget=8, mode='work'))
    a.atomic_json(tmp_path / 'manifest.json', a.seal(dict(jobs=[job])))
    a.atomic_json(tmp_path / 'launches.json', [dict(settings=s)])
    a.atomic_json(tmp_path / 'budget.json', dict(deadline_epoch=deadline_epoch))
    pr.worker(str(tmp_path / 'toy'), job, a.code_identity(), 1, False, None)
    wc.initial_control(tmp_path, s)
    return job, s


def assert_not_run(tmp_path, result, job, *, paused):
    assert result['not_run'] is True and result['reason'] == 'deadline' and result['candidate'] == job['id']
    assert result['paused'] is paused and result['dispatched'] is False and 'matched' not in result
    assert a.read(tmp_path / 'toy' / 'nondeterminism_check_not_run.json') == result
    assert not (tmp_path / 'toy' / 'nondeterminism_check.json').exists()
    assert not (tmp_path / 'toy' / 'nondeterminism_failure.json').exists()
    assert not list((tmp_path / '_nd_toy').glob('records/*.json'))


def test_recheck_is_not_run_when_the_deadline_passed_before_dispatch(tmp_path):
    job, _ = recheck_fixture(tmp_path, time.time() - 1)
    result = pr.nondeterminism_check(tmp_path / 'toy', [job])
    assert_not_run(tmp_path, result, job, paused=False)


def test_recheck_is_not_run_when_the_deadline_passes_while_paused(tmp_path):
    job, s = recheck_fixture(tmp_path, time.time() + 60)
    wc.control(tmp_path, s, workers=0, reason='pause before check')
    deadline = time.time() + 1.
    a.atomic_json(tmp_path / 'budget.json', dict(deadline_epoch=deadline))
    result = pr.nondeterminism_check(tmp_path / 'toy', [job])  # Formerly raised RuntimeError('deadline while ... paused').
    assert time.time() >= deadline  # It waited while paused until the stop, then returned.
    assert_not_run(tmp_path, result, job, paused=True)


@pytest.mark.parametrize('flag, reason', [('stop_dispatch', 'drained'), ('interrupt_now', 'interrupted')])
@pytest.mark.parametrize('paused', [False, True])
def test_the_launch_stop_before_the_recheck_starts_is_not_run_not_a_raise(tmp_path, flag, reason, paused):
    # A19 (F2): formerly RuntimeError('nondeterminism dispatch stopped by
    # operator'). Now a not-run outcome: no failure, no latch, nothing started.
    job, s = recheck_fixture(tmp_path, time.time() + 60)
    if paused:
        wc.control(tmp_path, s, workers=0, reason='pause before check')

        def stop_later():
            time.sleep(.5)
            a.atomic_json(tmp_path / 'control.json', dict(a.read(tmp_path / 'control.json'), **{flag: True}))

        thread = threading.Thread(target=stop_later)
        thread.start()
    else:
        a.atomic_json(tmp_path / 'control.json', dict(a.read(tmp_path / 'control.json'), **{flag: True}))
    result = pr.nondeterminism_check(tmp_path / 'toy', [job])
    if paused:
        thread.join(5)
    assert result['not_run'] is True and result['reason'] == reason and result['dispatched'] is False
    assert result['paused'] is paused and 'matched' not in result
    assert a.read(tmp_path / 'toy' / 'nondeterminism_check_not_run.json') == result
    assert not (tmp_path / 'toy' / 'nondeterminism_check.json').exists()
    assert not (tmp_path / 'toy' / 'nondeterminism_failure.json').exists()
    assert not (tmp_path / '_nd_toy' / 'events.jsonl').exists()  # The recheck dispatch never began.


@pytest.mark.parametrize('name', ['SIGINT', 'SIGTERM'])
def test_a_signal_during_the_paused_recheck_is_not_run_interrupted(tmp_path, name):
    # A19 (G3): formerly a KeyboardInterrupt (SIGINT) or the process's end
    # (SIGTERM) escaped the pause with no not-run record. Delivering the
    # signal to the handler the pause installed is what the interpreter does.
    import signal
    number = getattr(signal, name)
    job, s = recheck_fixture(tmp_path, time.time() + 60)
    wc.control(tmp_path, s, workers=0, reason='pause before check')
    original = signal.getsignal(number)

    def deliver():
        end = time.time() + 20
        while time.time() < end:
            if signal.getsignal(number) is not original:
                time.sleep(.3)  # Into the pause.
                signal.getsignal(number)(number, None)
                return
            time.sleep(.02)

    thread = threading.Thread(target=deliver)
    thread.start()
    result = pr.nondeterminism_check(tmp_path / 'toy', [job])
    thread.join(5)
    assert result['not_run'] is True and result['reason'] == 'interrupted' and result['paused'] is True
    assert result['dispatched'] is False and result['signal'] == int(number) and 'matched' not in result
    assert a.read(tmp_path / 'toy' / 'nondeterminism_check_not_run.json') == result
    assert not (tmp_path / 'toy' / 'nondeterminism_check.json').exists()
    assert not (tmp_path / 'toy' / 'nondeterminism_failure.json').exists()
    assert not (tmp_path / '_nd_toy' / 'events.jsonl').exists()
    assert signal.getsignal(number) is original  # The previous handler is back.


def test_the_launch_interrupt_now_reaches_a_running_recheck_on_the_final_phase(tmp_path, monkeypatch):
    # A19 (F2): the parent control's interrupt_now stops the recheck worker as
    # its own control would. On the final phase nothing later would see the
    # flag, so without this the launch completed with the flag set.
    spec = a4_fixture_spec(seconds=3.)
    path = tmp_path / 'spec.json'
    a.atomic_json(path, a.seal(spec))
    root = tmp_path / 'run'
    canned_configuration(monkeypatch)

    def interrupt_the_recheck():
        end = time.time() + 60
        while time.time() < end:
            if any(e['event'] == 'dispatch' for e in events(root / '_nd_fit')):
                a.atomic_json(root / 'control.json', dict(a.read(root / 'control.json'), interrupt_now=True))
                return
            time.sleep(.05)

    thread = threading.Thread(target=interrupt_the_recheck)
    thread.start()
    began = time.time()
    result = pr.launch(path, root, local_settings())
    thread.join(5)
    assert not result['complete'] and result['reason'] == 'interrupted'
    assert time.time() - began < 12  # Phase job 3 s, recheck stopped at once rather than run to its end.
    not_run = a.read(root / 'fit' / 'nondeterminism_check_not_run.json')
    assert not_run['reason'] == 'interrupted' and not_run['dispatched'] is True
    assert [e['reason'] for e in events(root / '_nd_fit') if e['event'] == 'restart_required'] == ['interrupted']
    assert not (root / 'fit' / 'nondeterminism_check.json').exists()
    assert not (root / 'fit' / 'nondeterminism_failure.json').exists() and not (root / 'nondeterminism_failure.json').exists()
    record = a.read(root / 'launches.json')[-1]
    assert record['complete'] is False and record['stopped'] == 'interrupted'


def test_recheck_dispatched_before_the_deadline_drains_and_is_compared(tmp_path):
    # A three-second job and a deadline 1.5 s out: the recheck is running at
    # the deadline, drains to completion under T1 and is compared as before.
    job, _ = recheck_fixture(tmp_path, time.time() + 60, seconds=3.)
    output = a.read(tmp_path / 'toy/outputs' / (job['id'] + '.json'))
    deadline = time.time() + 1.5  # Set after the original was produced in-process (three seconds).
    a.atomic_json(tmp_path / 'budget.json', dict(deadline_epoch=deadline))
    dispatched = []
    result = pr.nondeterminism_check(tmp_path / 'toy', [job], dispatched=dispatched)
    assert dispatched == [job['id']]
    assert result['matched'] is True and result['checked'] == job['id']
    assert a.read(tmp_path / 'toy/nondeterminism_check.json') == result
    fresh = pr.completed(tmp_path / '_nd_toy', job, a.code_identity())
    assert fresh['result'] == output['result'] and fresh['finished_epoch'] > deadline
    assert any(e['event'] == 'deadline_drain' and e['active'] == [job['id']] for e in events(tmp_path / '_nd_toy'))
    assert not (tmp_path / 'toy/nondeterminism_check_not_run.json').exists()


def test_an_interrupted_recheck_latches_nothing_and_the_next_launch_runs_it_again(tmp_path, monkeypatch):
    # A19 (R2): a signal while the recheck runs is the operator's supported
    # interruption. The launch ends incomplete with reason interrupted, with no
    # failure file and no halt; a later launch in the same root, before the
    # deadline, runs the recheck again and records the passed check.
    import signal
    spec = a4_fixture_spec(seconds=3.)
    path = tmp_path / 'spec.json'
    a.atomic_json(path, a.seal(spec))
    root = tmp_path / 'run'
    job = spec['jobs'][0]
    canned_configuration(monkeypatch)
    original = signal.getsignal(signal.SIGTERM)

    def interrupt_the_recheck():
        end = time.time() + 60
        while time.time() < end:
            handler = signal.getsignal(signal.SIGTERM)
            if handler is not original and any(e['event'] == 'dispatch' for e in events(root / '_nd_fit')):
                handler(signal.SIGTERM, None)  # What the interpreter does on a real SIGTERM.
                return
            time.sleep(.05)

    thread = threading.Thread(target=interrupt_the_recheck)
    thread.start()
    first = pr.launch(path, root, local_settings())
    thread.join(5)
    assert not first['complete'] and first['reason'] == 'interrupted'
    assert first['nondeterminism_check_not_run']['reason'] == 'interrupted'
    assert first['nondeterminism_check_not_run']['dispatched'] is True
    assert [e['reason'] for e in events(root / '_nd_fit') if e['event'] == 'restart_required'] == ['interrupted']
    not_run = a.read(root / 'fit' / 'nondeterminism_check_not_run.json')
    assert not_run['reason'] == 'interrupted' and not_run['launch_number'] == 1 and 'matched' not in not_run
    assert not_run['launch_epoch'] == a.read(root / 'launches.json')[0]['epoch']
    for name in ('nondeterminism_failure.json', 'fit/nondeterminism_failure.json', 'fit/nondeterminism_check.json'):
        assert not (root / name).exists()
    assert not any(root.glob('*scientific_halt.json')) and not any(root.glob('*round*.json'))
    assert a.read(root / 'launches.json')[-1]['stopped'] == 'interrupted'
    # The next launch, same root, before the deadline: the recheck runs again.
    second = pr.launch(path, root, local_settings())
    assert second['complete']
    history = a.read(root / 'launches.json')
    assert len(history) == 2 and history[-1]['complete'] is True
    assert history[-1]['first_scientific_dispatch']['by'] == 'nondeterminism recheck'
    check = a.read(root / 'fit' / 'nondeterminism_check.json')
    # What the A13/A14/A16 publication readers and history_a14 require of it.
    assert check['matched'] is True and check['checked'] in {j['id'] for j in spec['jobs']} and check['checked'] == job['id']
    record = a.read(root / '_nd_fit' / 'records' / (check['checked'] + '.json'))
    assert record['status'] == 'complete' and record['job'] == job and record['code_hash'] == a.code_identity()
    assert not (root / 'nondeterminism_failure.json').exists() and not (root / 'fit' / 'nondeterminism_failure.json').exists()
    # The earlier not-run record stays, and names the launch that wrote it.
    assert a.read(root / 'fit' / 'nondeterminism_check_not_run.json')['launch_number'] == 1 < len(history)


def test_real_mismatch_still_halts(tmp_path):
    job, _ = recheck_fixture(tmp_path, time.time() + 60)
    path = tmp_path / 'toy/outputs' / (job['id'] + '.json')
    output = a.read(path)
    output['result'] = dict(output['result'], seed=output['result']['seed'] + 1)
    a.atomic_json(path, output)
    record = a.read(tmp_path / 'toy/records' / (job['id'] + '.json'))
    a.atomic_json(tmp_path / 'toy/records' / (job['id'] + '.json'), dict(record, output_hash=a.file_hash(path)))
    with pytest.raises(RuntimeError, match='nondeterminism'):
        pr.nondeterminism_check(tmp_path / 'toy', [job])
    failure = a.read(tmp_path / 'toy/nondeterminism_failure.json')
    assert failure['job'] == job['id'] and failure['recomputed'] is True
    assert not (tmp_path / 'toy/nondeterminism_check_not_run.json').exists()


# --------------------------------------------------------------------------
# T6: the multihost wall ceiling drains
# --------------------------------------------------------------------------

def test_wall_ceiling_is_a_dispatch_stop_not_a_hard_stop_and_charges_the_drain(tmp_path):
    t = time.time()
    spec = spec_fixture(2)
    _, root, spec = initialize(tmp_path, spec, start=t)
    alpha = join(root, 'alpha', t); ready(root, alpha, 'toy', t)
    leased = claim(root, alpha, t)
    assert leased['job']
    ceiling = t + spec['wall_seconds']
    for when in range(20, int(spec['wall_seconds']) + 40, 20):
        m.rpc(root, dict(op='heartbeat', **alpha), now=t + when)
    status = m.rpc(root, dict(op='heartbeat', **alpha), now=ceiling + 5)['status']
    # A19 (F4): the clock stop is the recorded reason, never None.
    assert status['stops']['wall'] is True and status['hard_stop'] is False and status['reason'] == 'deadline'
    drain = status['deadline_drain']
    assert (drain['stop'], drain['epoch'], drain['deadline_epoch']) == ('deadline', ceiling, ceiling)
    assert drain['active_job_ids'] == [leased['job']['id']] and drain['pending'] == 1 and 'ended_epoch' not in drain
    assert claim(root, alpha, ceiling + 5)['job'] is None
    # The job leased before the stop finishes after the ceiling and is recorded.
    reply = finish(root, alpha, leased, ceiling + 10)
    assert reply['accepted'] is True and not reply['duplicate']
    # A19 (G1): the drain lasts while alpha's session is open, not only its lease.
    assert 'ended_epoch' not in m.read_state(root)['deadline_drain']
    assert pr.completed(root / 'toy', leased['job'], spec['code_hash']) is not None
    assert m.read_state(root)['leases'][leased['lease']]['status'] == 'completed'
    m.rpc(root, dict(op='leave', **alpha), now=ceiling + 11)
    session = m.read_state(root)['sessions'][alpha['session']]
    assert session['end'] == ceiling + 11  # Charged until it left, after its last job (A11, A17).
    drain = m.read_state(root)['deadline_drain']
    assert (drain['ended_epoch'], drain['overrun_seconds'], drain['completed_during_drain'], drain['ended_by']) == (
        ceiling + 11, 11, 1, 'no lease active and no session open')
    assert m.rpc(root, {'op': 'inspect'}, now=ceiling + 11)['status']['x2_equivalent_hours'] == pytest.approx((ceiling + 11 - t) / 3600)


def test_coordinator_stays_through_the_wall_ceiling_until_the_last_lease_ends(tmp_path):
    spec = spec_fixture(2)
    spec['wall_seconds'] = 1.5
    path, root, _ = initialize(tmp_path, spec)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(m.coordinate, path, root, SETTINGS)
        for _ in range(200):
            if (root / 'launches.json').exists():
                break
            time.sleep(.02)
        alpha = join(root, 'alpha'); ready(root, alpha, 'toy')
        leased = claim(root, alpha)
        assert leased['job']
        time.sleep(2.5)
        assert not future.done()  # Past the ceiling with a live lease: the monitor waits.
        heartbeat = m.rpc(root, dict(alpha, op='heartbeat'))
        assert heartbeat['status']['stops']['wall'] and not heartbeat['status']['hard_stop']
        assert claim(root, alpha)['job'] is None
        assert finish(root, alpha, leased)['accepted']
        m.rpc(root, dict(alpha, op='leave'))
        result = future.result(timeout=10)
    assert result['stops']['wall'] and not result['hard_stop'] and not result['complete']
    assert pr.completed(root / 'toy', leased['job'], a.code_identity()) is not None
    history = a.read(root / 'launches.json')[-1]
    assert history['complete'] is False and history['finished_epoch'] >= a.read(root / 'budget.json')['overall_deadline_epoch']
    # A19 (F4): the launch record carries the reason and the drain.
    assert history['reason'] == history['stopped'] == 'deadline'
    drain = history['deadline_drain']
    assert drain['stop'] == 'deadline' and drain['active_job_ids'] == [leased['job']['id']]
    assert drain['completed_during_drain'] == 1 and drain['overrun_seconds'] > 0
    assert drain['ended_by'] == 'no lease active and no session open'


def test_the_charged_allowance_stop_is_recorded_as_such(tmp_path):
    t = time.time()
    spec = spec_fixture(2)
    spec['x2_equivalent_hours'] = .05  # 180 X2-equivalent seconds, before the 300 s wall.
    _, root, spec = initialize(tmp_path, spec, start=t)
    alpha = join(root, 'alpha', t); ready(root, alpha, 'toy', t)
    leased = claim(root, alpha, t)
    for when in range(20, 200, 20):
        status = m.rpc(root, dict(op='heartbeat', **alpha), now=t + when)['status']
    assert status['stops']['x2'] and not status['stops']['wall'] and status['reason'] == 'charged_allowance'
    drain = status['deadline_drain']
    assert drain['stop'] == 'charged_allowance' and drain['epoch'] == t + 180 and drain['active_job_ids'] == [leased['job']['id']]
    finish(root, alpha, leased, t + 190)
    m.rpc(root, dict(op='leave', **alpha), now=t + 195)
    drain = m.read_state(root)['deadline_drain']
    assert drain['overrun_seconds'] == pytest.approx(15) and drain['completed_during_drain'] == 1


def test_the_drain_lasts_until_the_last_configuring_session_ends(tmp_path):
    # A19 (G1a), the reviewer's numbers: deadline at 10, configuration ending
    # at 30. Formerly the record ended at 10 with overrun 0.
    t = time.time()
    spec = spec_fixture(2)
    spec['wall_seconds'] = 10.
    _, root, spec = initialize(tmp_path, spec, start=t)
    alpha = join(root, 'alpha', t, configure=False)  # Configuring: a session, no lease.
    for when in (5, 10, 15, 20, 25):
        m.rpc(root, dict(op='heartbeat', **alpha), now=t + when)
    drain = m.read_state(root)['deadline_drain']
    assert drain['epoch'] == t + 10 and drain['active_job_ids'] == [] and 'ended_epoch' not in drain
    m.rpc(root, dict(op='leave', **alpha), now=t + 30)
    drain = m.read_state(root)['deadline_drain']
    assert drain['ended_epoch'] == t + 30 and drain['overrun_seconds'] == pytest.approx(20)
    assert drain['ended_by'] == 'no lease active and no session open'
    assert drain['x2_equivalent_hours_at_end'] == pytest.approx(30 / 3600)  # Charged to the session's end.


def test_a_running_recheck_lease_is_not_counted_as_pending(tmp_path):
    # A19 (G1b): one manifest job, done, with its recheck lease running at the
    # deadline. Formerly pending = -1.
    t = time.time()
    _, root, spec = initialize(tmp_path, spec_fixture(1), start=t)
    alpha = join(root, 'alpha', t); ready(root, alpha, 'toy', t)
    work = claim(root, alpha, t)
    finish(root, alpha, work, t + 1)
    check = claim(root, alpha, t + 2)
    assert check['purpose'] == 'check' and check['job']['id'] == work['job']['id']
    for when in range(20, 301, 20):
        m.rpc(root, dict(op='heartbeat', **alpha), now=t + when)
    drain = m.read_state(root)['deadline_drain']
    assert drain['active_job_ids'] == [work['job']['id']] and drain['pending'] == 0 and drain['completed_before'] == 1


def test_no_drain_record_opens_after_the_launch_completed(tmp_path):
    # A19 (G1c), the reviewer's numbers: complete at 5, deadline 10, inspected
    # at 20. Formerly a drain record appeared with a ten-second overrun.
    t = time.time()
    spec = spec_fixture(1)
    spec['wall_seconds'] = 10.
    _, root, spec = initialize(tmp_path, spec, start=t)
    alpha = join(root, 'alpha', t); ready(root, alpha, 'toy', t)
    work = claim(root, alpha, t)
    finish(root, alpha, work, t + 1)
    check = claim(root, alpha, t + 2)
    finish(root, alpha, check, t + 5)
    assert m.read_state(root)['complete']
    status = m.rpc(root, {'op': 'inspect'}, now=t + 20)['status']
    assert status['complete'] and status['deadline_drain'] is None and status['reason'] is None
    assert m.read_state(root).get('deadline_drain') is None
    journal = [a.unseal(a.read(p)) for p in sorted((root / 'protocol_events').glob('*.json'))]
    assert not any(e.get('event', '').startswith('deadline_drain') for e in journal)


def test_a_join_after_the_drain_is_over_is_refused_and_one_during_it_is_admitted(tmp_path):
    # A19 (G2): a refusal to start for a join that can do nothing.
    t = time.time()
    spec = spec_fixture(2)
    spec['wall_seconds'] = 10.
    _, root, spec = initialize(tmp_path, spec, start=t)
    alpha = join(root, 'alpha', t, configure=False)
    m.rpc(root, dict(op='heartbeat', **alpha), now=t + 12)
    beta = join(root, 'beta', t + 12)  # Admitted: alpha's session is still open.
    ready(root, beta, 'toy', t + 12)
    assert claim(root, beta, t + 12)['job'] is None  # It takes no new claim.
    m.rpc(root, dict(op='leave', **alpha), now=t + 13)
    m.rpc(root, dict(op='leave', **beta), now=t + 14)
    with pytest.raises(ValueError, match='not accepting joins: the deadline stop is in effect and its drain is over'):
        join(root, 'alpha', t + 20)


# --------------------------------------------------------------------------
# F1: a deadline during host configuration kills nothing
# --------------------------------------------------------------------------

def monitor_tick(root, now):
    """One iteration of coordinate()'s monitor loop at a simulated time."""
    with m.transaction(root):
        c = m.Coordinator(root, now)
        c.state['monitor_epoch'] = now
        c.advance()
        c.save()
        return c.monitor_finished(), c.status()


def test_the_monitor_stays_while_a_session_is_open_and_a_vanished_host_still_ends(tmp_path):
    t = time.time()
    spec = spec_fixture(2)
    _, root, spec = initialize(tmp_path, spec, start=t)
    with m.transaction(root):
        c = m.Coordinator(root, t)
        c.state.update(monitor_required=True, monitor_epoch=t)
        c.save()
    # Alpha is configuring (a session, no lease); beta heartbeats, then vanishes.
    alpha = join(root, 'alpha', t, configure=False)
    beta = join(root, 'beta', t, configure=False)
    ceiling = t + spec['wall_seconds']
    for when in range(20, 401, 20):
        m.rpc(root, dict(op='heartbeat', **alpha), now=t + when)  # The watcher, while trials run.
        if when <= 300:
            m.rpc(root, dict(op='heartbeat', **beta), now=t + when)
        finished, status = monitor_tick(root, t + when)
        assert not finished  # Formerly finished once the wall passed: a stop and no active lease.
        assert status['hard_stop'] is False and status['stops']['coordinator'] is False
    assert status['stops']['wall'] and status['reason'] == 'deadline'
    assert status['deadline_drain']['active_job_ids'] == [] and status['deadline_drain']['epoch'] == ceiling
    state = m.read_state(root)
    # Beta's heartbeat expired 30 s after its last one, so its session ended by expiry.
    assert state['sessions'][beta['session']]['end'] == t + 330 and state['sessions'][beta['session']]['end_reason'] == 'heartbeat expired'
    assert state['sessions'][alpha['session']]['end'] is None
    m.rpc(root, dict(op='leave', **alpha), now=t + 405)
    assert monitor_tick(root, t + 406)[0]


def test_a_vanished_configuring_host_ends_the_monitor_by_expiry(tmp_path):
    spec = spec_fixture(2)
    spec['wall_seconds'] = 1.
    spec['pull_dispatch']['lease_seconds'] = 3.
    path, root, _ = initialize(tmp_path, spec)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(m.coordinate, path, root, SETTINGS)
        for _ in range(200):
            if (root / 'launches.json').exists():
                break
            time.sleep(.02)
        alpha = join(root, 'alpha', configure=False)  # Joins, then never heartbeats.
        result = future.result(timeout=20)
    session = m.read_state(root)['sessions'][alpha['session']]
    assert session['end_reason'] == 'heartbeat expired' and result['stops']['wall']
    assert a.read(root / 'launches.json')[-1]['stopped'] == 'deadline'
    # A19 (G2): the coordinator has gone; a late host is refused, not left to
    # configure until a manufactured coordinator loss.
    with pytest.raises(ValueError, match='not accepting joins'):
        join(root, 'beta', configure=False)


def test_a_deadline_during_host_configuration_kills_no_trial_and_the_session_ends(tmp_path, monkeypatch):
    # The deadline arrives while the host's configuration trial runs. The trial
    # has no lease. The monitor stays, its epoch stays fresh, the watcher never
    # reports coordinator loss and never writes interrupt_now; it announces the
    # dispatch stop (stop_dispatch), the trial finishes, the host reports
    # configured, sees the stop and leaves, and the monitor then retires.
    spec = spec_fixture(2)
    spec['wall_seconds'] = 2.
    ttl = spec['pull_dispatch']['lease_seconds'] = 3.
    path, root, _ = initialize(tmp_path, spec)
    seen = dict(interrupt_now=False, stop_dispatch=False, finished=False)

    def configuration_test(root_, phase, profile, settings, deadline, launch_number, **kwargs):
        end = deadline + 3 * ttl + 1  # Well past the point a retired monitor's epoch went stale.
        while time.time() < end:
            control = a.read(Path(root_) / 'control.json')
            seen['interrupt_now'] |= bool(control.get('interrupt_now'))
            seen['stop_dispatch'] |= bool(control.get('stop_dispatch'))
            time.sleep(.1)
        seen['finished'] = True
        return [dict(workers=2, threads=1, completed=2, wall_seconds=1., valid=True, round=0, job_seconds=[.5, .5])]

    monkeypatch.setattr(pr, 'configuration_test', configuration_test)
    scratch = tmp_path / 'host_alpha'
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(m.coordinate, path, root, SETTINGS)
        for _ in range(200):
            if (root / 'launches.json').exists():
                break
            time.sleep(.02)
        hosted = h.run_host(h.Loopback(root), scratch, SETTINGS, host='alpha', environment=FINGERPRINT)
        result = future.result(timeout=20)
    assert hosted['stopped'] and seen == dict(interrupt_now=False, stop_dispatch=True, finished=True)
    session = next(iter(m.read_state(root)['sessions'].values()))
    assert session['end_reason'] == 'left' and 'toy' in session['configuration']
    assert result['stops']['wall'] and not result['hard_stop']
    assert a.read(root / 'launches.json')[-1]['stopped'] == 'deadline'
    planning = a.read(scratch / 'configuration_planning.json')
    assert planning['failure'] is None and planning['elapsed_seconds'] > spec['wall_seconds']
    assert a.read(scratch / 'host_exit.json')['error'] is None


# --------------------------------------------------------------------------
# P1: assembly hashes each spec once, byte-identical to draft 2
# --------------------------------------------------------------------------

DRAFT2_COLLECT_RECORD = r'''
def collect_record(sources, reasons_path):
    """Read the original populations and comparisons without executing a job."""
    from .instrument import declaration
    from .production_runner import completed
    from .snapshot_a11 import historical_root_provenance
    provenance = historical_root_provenance(sources)
    history_view = sorted(set(provenance['specification']) | set(provenance['sources_document']))
    reason_doc = read(reasons_path)
    before = reason_doc["producing_source_manifest"]
    old, new = digest(before), code_identity()
    after = source_manifest()
    changes = changed_files(before, after)
    reasons = reason_doc["reasons"]
    _require(old != new and changes, "compatibility needs two different source identities")
    _require(set(reasons) == set(changes) and all(isinstance(v, str) and v.strip() for v in reasons.values()),
             "every changed file needs its reason")
    grouped, selected_jobs, inputs, profiles = {}, {}, [], {}
    class_peaks, class_seconds = {}, {}
    for source in sources:
        root, spec_path = Path(source["root"]).resolve(), Path(source["spec"]).resolve()
        spec = unseal(read(spec_path))
        _require(spec["code_hash"] == old and declaration(spec.get("instrument")).a10, "source is not the producing A10 identity")
        registration = None
        if spec.get('registered'):
            from .artifacts import verify_registration
            registration = verify_registration(spec['registration'], instrument=spec['instrument'], historical=True)
        _require(read(root / "identity.json") == {"code_hash": old, "spec_hash": digest(spec)}, "source root identity mismatch")
        _require(unseal(read(root / "manifest.json")) == spec, "source root manifest mismatch")
        _require(read(root / "launches.json")[-1].get("complete") is True, "compatibility needs a completed launch")
        for job in spec["jobs"]:
            _require(job["id"] not in selected_jobs, "duplicate source job")
            phase_root = root / job["config"].get("phase", job["kind"])
            output = completed(phase_root, job, old)
            _require(output is not None, "missing durable source output")
            _require(output["result"].get("code_hash", old) == old, "source result has wrong producer metadata")
            group = _stratum(job)
            grouped.setdefault(group, []).append(job["id"])
            selected_jobs[job["id"]] = {"job": job, "phase_root": str(phase_root), "producing_code_hash": old,
                                        "before_sha256": hashlib.sha256(comparison_bytes(job, output["result"])).hexdigest(),
                                        "output_file_sha256": file_hash(phase_root / "outputs" / (job["id"] + ".json"))}
            if job['kind'] == 'rerun' and registration is not None:
                selected_jobs[job['id']]['proof_authority'] = {
                    "a19_proof": True, "job_id": job["id"], "registration": registration,
                    "spec_sha256": file_hash(spec_path)}
            if job['kind'] == 'a13_validate_plain_ext':
                from .replay_a14 import binding
                checkpoints = [read(phase_root / 'a13_checkpoints' / job['id'] / f'{r["replicate"]:02d}.json')
                               for r in output['result']['replicates']]
                selected_jobs[job['id']]['a13_replay'] = binding(spec, job, output['result'], checkpoints)
            if job['kind'] in EXTENSION_REPLAY_KINDS:
                from .replay_a16 import binding as extension_binding, checkpoint_directory
                checkpoints = [read(phase_root / checkpoint_directory(job['kind']) / job['id'] / f'{r["replicate"]:02d}.json')
                               for r in output['result']['replicates']]
                selected_jobs[job['id']]['extension_replay'] = extension_binding(spec, job, output['result'], checkpoints)
            from .compatibility_shards_a11 import resource_estimate
            extension = job['kind'] == 'a13_validate_plain_ext' or job['kind'] in EXTENSION_REPLAY_KINDS
            if extension and spec['registered'] and 'pull_dispatch' not in spec:
                from .table_validation_a4 import _recompute_plan_hash
                if job['kind'] == 'a13_validate_plain_ext':
                    _require(file_hash(spec['original_plan_path']) == spec['original_plan_file_sha256'],
                             'A13 replay original plan changed')
                    original = unseal(read(spec['original_plan_path']))
                    _require(_recompute_plan_hash(original) == original['plan_hash']
                             and original['plan_hash'] == spec['original_plan_hash'], 'A13 replay original plan binding differs')
                else:
                    from .replay_a16 import original_validation_plan
                    original = original_validation_plan(spec, history_view)
                    _require(_recompute_plan_hash(original) == original['plan_hash'], 'extension replay original plan binding differs')
                source = next(j for j in original['jobs'] if j['config']['phase'] == 'validate_plain'
                              and j['config']['a1_job']['id'] == job['config']['a1_job']['id'])
                resource = resource_estimate(original, source)
                resource['worker_seconds'] *= job['config']['R_max'] / 3
            else:
                resource = resource_estimate(spec, job)
            selected_jobs[job['id']]['resources'] = resource
            from .worker_control import observe
            completion_path = phase_root / 'records' / (job['id'] + '.json')
            completion = read(completion_path)
            for peak in (completion.get('peak_rss_bytes'), output.get('peak_rss_bytes')):
                observe(class_peaks, resource, peak)
            from .worker_control import positive
            if positive(completion.get('worker_seconds')):
                class_seconds.setdefault(resource['memory_class'], []).append(completion['worker_seconds'])
            phase = job['config'].get('phase', job['kind'])
            profile_key = digest([str(spec_path), phase])
            selected_jobs[job['id']]['profile_key'] = profile_key
            if phase in spec.get('configuration', {}):
                profiles[profile_key] = dict(profile=spec['configuration'][phase], phase=phase,
                    phase_root=str(phase_root), producing_code_hash=old)
        inputs.append({"spec": str(spec_path), "root": str(root), "spec_sha256": file_hash(spec_path)})
    populations = [{"phase": p, "capability": c, "setting": s, "job_ids": sorted(ids)}
                   for (p, c, s), ids in sorted(grouped.items())]
    for item in selected_jobs.values():
        r = item['resources']
        timings = class_seconds.get(r['memory_class'], [])
        r['measured_worker_seconds'] = sum(timings) / len(timings) if timings else None
        if class_peaks.get(r['memory_class']):
            r['memory_gb'] = r.get('planning_memory_gb', r['memory_gb'])
        r['registered_memory_gb'] = r['memory_gb']
        r['measured_memory_gb'] = class_peaks.get(r['memory_class'], 0.)
        r['memory_gb'] = max(r['memory_gb'], r['measured_memory_gb'])
    sample = _selected(populations)
    _require(sample, "empty compatibility sample")
    record = {"schema": SCHEMA, "non_registered": True, "producing_code_hash": old, "new_code_hash": new,
              "producing_source_manifest": before, "new_source_manifest": after, "changed_files": changes,
              "reasons": reasons, "inputs": inputs, "populations": populations,
              "selection_rule": 'two smallest digest(["A11-compatibility", phase, job_id]) per capability/setting',
              "comparison": COMPARISON,
              "operator_approval": None, "passed": False, "proofs": [],
              "execution": {"mode": "work", "workers": 1, "threads": 1, "historical_view": history_view,
                            "historical_view_provenance": provenance}}
    return record, {jid: selected_jobs[jid] for jid in sample}, profiles
'''


def draft2_collect_record(namespace_source):
    """Draft 2's collect_record, run in a copy of the live module namespace so it
    uses the same helpers (and the same counted file_hash) as the new one."""
    namespace = dict(vars(namespace_source))
    namespace['__name__'] = c.__name__
    exec(DRAFT2_COLLECT_RECORD, namespace)
    return namespace['collect_record']


def registered_rerun_sources(root, monkeypatch, *, reruns=5):
    before = a.source_manifest()
    before['v3/artifacts.py'] = '0' * 64
    old = a.digest(before)
    instrument = tables.NOMINAL.declaration()
    cfg = dict(phase='toy', steps=1, category='R1', model=dict(instrument=instrument, capability=1.))
    jobs = [a.stable_job('rerun', cfg, 'v3_rerun', i) for i in range(reruns)]
    jobs += [a.stable_job('fixture', dict(phase='toy', seconds=.001, kernel={'capability': 2.}), 'validation', i) for i in range(3)]
    profile = dict(kind='fixture', config={'phase': 'toy', 'seconds': .001}, workers_local=[2],
                   workers_x2=[8, 12, 16, 24, 32], threads=[1], rounds=1, jobs_per_worker=1)
    registration = dict(commit='c' * 40, path='registered/plan.md', sha256='1' * 64)
    spec = dict(code_hash=old, registered=True, registration=registration, instrument=instrument, jobs=jobs,
                phases=['toy'], configuration={'toy': profile}, memory_estimate_gb={'toy': .25},
                pull_dispatch=dict(projection_sha256='p' * 64, memory_basis='registered-stratum',
                                   job_classes={j['id']: str(i) for i, j in enumerate(jobs)},
                                   cost_classes={str(i): dict(worker_seconds=i + 1., memory_gb=.25) for i in range(len(jobs))}))
    source, spec_path, reasons = root / 'old', root / 'spec.json', root / 'reasons.json'
    a.atomic_json(spec_path, a.seal(spec))
    a.atomic_json(source / 'identity.json', dict(code_hash=old, spec_hash=a.digest(spec)))
    a.atomic_json(source / 'manifest.json', a.seal(spec))
    a.atomic_json(source / 'launches.json', [{'complete': True}])
    for job in jobs:
        output = source / 'toy/outputs' / (job['id'] + '.json')
        a.atomic_json(output, dict(job=job, code_hash=old, result=dict(seed=job['seed'], fixture=True), peak_rss_bytes=10 ** 8))
        a.atomic_json(source / 'toy/records' / (job['id'] + '.json'),
                      dict(job=job, code_hash=old, status='complete', output_hash=a.file_hash(output), worker_seconds=1.5))
    a.atomic_json(reasons, dict(producing_source_manifest=before, reasons={'v3/artifacts.py': 'Synthetic producing identity.'}))
    monkeypatch.setattr(a, 'verify_registration', lambda pin, **kwargs: dict(pin, verified=True, historical=kwargs.get('historical')))
    return [dict(spec=str(spec_path), root=str(source))], reasons, spec_path


def test_collect_record_hashes_each_spec_once_and_is_byte_identical_to_draft_2(tmp_path, monkeypatch):
    sources, reasons, spec_path = registered_rerun_sources(tmp_path, monkeypatch)
    calls = []
    real = a.file_hash

    def counted(path):
        calls.append(str(path))
        return real(path)

    monkeypatch.setattr(c, 'file_hash', counted)
    old = draft2_collect_record(c)
    expected = old(sources, reasons)
    old_spec_hashes = calls.count(str(spec_path.resolve()))
    del calls[:]
    actual = c.collect_record(sources, reasons)
    new_spec_hashes = calls.count(str(spec_path.resolve()))
    record, selected, profiles = actual
    assert a.canonical(actual) == a.canonical(expected)
    assert a.canonical(record) == a.canonical(expected[0])
    assert all(a.canonical(selected[jid]) == a.canonical(expected[1][jid]) for jid in expected[1]) and set(selected) == set(expected[1])
    assert a.canonical(profiles) == a.canonical(expected[2])
    # Draft 2 hashed the spec once per registered rerun job plus once for inputs.
    reruns = sum(j['kind'] == 'rerun' for j in a.unseal(a.read(spec_path))['jobs'])
    assert old_spec_hashes == reruns + 1 == 6
    assert new_spec_hashes == 1
    authority = {i['proof_authority']['spec_sha256'] for i in selected.values() if 'proof_authority' in i}
    assert authority == {real(spec_path)} == {record['inputs'][0]['spec_sha256']}
    assert any('proof_authority' in i for i in selected.values())


def registered_extension_sources(root, monkeypatch, kind, *, count=4):
    """A registered single-host extension source (no pull_dispatch), whose
    scheduling class comes from its original validation plan. The replay
    bindings and plan-hash checks are stubbed identically for both versions;
    what is compared is collect_record's own assembly."""
    from v3 import replay_a14, replay_a16, table_validation_a4
    before = a.source_manifest()
    before['v3/artifacts.py'] = '0' * 64
    old = a.digest(before)
    instrument = tables.NOMINAL.declaration()
    # One stratum per job (distinct capability), so every job is selected and
    # every selected item is compared.
    jobs = [a.stable_job(kind, dict(phase='ext', R_max=6, a1_job=dict(id='a1_%d' % i, config=dict(kernel=dict(capability=1. + i)))),
                         'v3_tables', i) for i in range(count)]
    original = dict(plan_hash='original-plan', code_hash='original-code', jobs=[
        dict(id='v_%d' % i, kind='a4_validate', seed=i, config=dict(phase='validate_plain', a1_job=dict(id='a1_%d' % i)))
        for i in range(count)])
    plan_path = root / 'original_plan.json'
    a.atomic_json(plan_path, a.seal(original))
    registration = dict(commit='c' * 40, path='registered/plan.md', sha256='1' * 64)
    spec = dict(code_hash=old, registered=True, registration=registration, instrument=instrument, jobs=jobs, phases=['ext'],
                original_plan_path=str(plan_path), original_plan_file_sha256=a.file_hash(plan_path), original_plan_hash='original-plan')
    source, spec_path, reasons = root / 'old', root / 'spec.json', root / 'reasons.json'
    a.atomic_json(spec_path, a.seal(spec))
    a.atomic_json(source / 'identity.json', dict(code_hash=old, spec_hash=a.digest(spec)))
    a.atomic_json(source / 'manifest.json', a.seal(spec))
    a.atomic_json(source / 'launches.json', [{'complete': True}])
    for job in jobs:
        output = source / 'ext/outputs' / (job['id'] + '.json')
        a.atomic_json(output, dict(job=job, code_hash=old, result=dict(seed=job['seed'], replicates=[]), peak_rss_bytes=10 ** 8))
        a.atomic_json(source / 'ext/records' / (job['id'] + '.json'),
                      dict(job=job, code_hash=old, status='complete', output_hash=a.file_hash(output), worker_seconds=2.5))
    a.atomic_json(reasons, dict(producing_source_manifest=before, reasons={'v3/artifacts.py': 'Synthetic producing identity.'}))
    monkeypatch.setattr(a, 'verify_registration', lambda pin, **kwargs: dict(pin, verified=True, historical=kwargs.get('historical')))
    monkeypatch.setattr(replay_a14, 'binding', lambda plan, job, result, checkpoints: dict(bound=job['id'], kind='a13'))
    monkeypatch.setattr(replay_a16, 'binding', lambda plan, job, result, checkpoints: dict(bound=job['id'], kind='extension'))
    monkeypatch.setattr(table_validation_a4, '_recompute_plan_hash', lambda plan: plan['plan_hash'])
    reads = []

    def original_validation_plan(spec_, history_view=()):
        reads.append(spec_['original_plan_hash'])
        return a.unseal(a.read(plan_path))  # A fresh object per call, as the real reader returns.

    monkeypatch.setattr(replay_a16, 'original_validation_plan', original_validation_plan)
    return [dict(spec=str(spec_path), root=str(source))], reasons, plan_path, reads


@pytest.mark.parametrize('kind', ['a13_validate_plain_ext', 'a14_validate_plain_ext2', 'a16_validate_plain_r1'])
def test_collect_record_reads_the_original_plan_once_per_spec_and_is_byte_identical_to_draft_2(tmp_path, monkeypatch, kind):
    sources, reasons, plan_path, reads = registered_extension_sources(tmp_path, monkeypatch, kind)
    hashed = []
    real = a.file_hash

    def counted(path):
        hashed.append(str(path))
        return real(path)

    monkeypatch.setattr(c, 'file_hash', counted)
    expected = draft2_collect_record(c)(sources, reasons)
    old_plan_hashes, old_reads = hashed.count(str(plan_path)), len(reads)
    del hashed[:], reads[:]
    actual = c.collect_record(sources, reasons)
    assert a.canonical(actual) == a.canonical(expected)
    record, selected, _ = actual
    assert set(selected) == {j['id'] for j in a.unseal(a.read(sources[0]['spec']))['jobs']}  # Every item compared.
    # The scheduling class was not compounded by sharing the plan object.
    assert {i['resources']['worker_seconds'] for i in selected.values()} == {2.}
    if kind == 'a13_validate_plain_ext':
        assert (old_plan_hashes, hashed.count(str(plan_path))) == (4, 1) and old_reads == len(reads) == 0
    else:
        assert (old_reads, len(reads)) == (4, 1) and old_plan_hashes == hashed.count(str(plan_path)) == 0


# --------------------------------------------------------------------------
# P2: context variables
# --------------------------------------------------------------------------

def test_execute_proof_resets_the_producer_when_the_authority_set_fails(monkeypatch):
    class Broken:
        def set(self, value):
            raise RuntimeError('injected between the two sets')

    job = {'id': 'rerun_p2', 'kind': 'rerun', 'seed': 1, 'tag': 'v3_tables', 'config': {'steps': 1}}
    monkeypatch.setattr(c, '_proof_authority', Broken())
    with pytest.raises(RuntimeError, match='injected'):
        c._execute_proof({'job': job, 'producing_code_hash': 'f' * 64, 'phase_root': '.'})
    assert c._proof_producer.get() is None


# --------------------------------------------------------------------------
# P3: execution metadata in A11 records
# --------------------------------------------------------------------------

@pytest.mark.parametrize('mode', ['normal', 'work'])
def test_build_record_records_the_actual_mode_workers_and_threads(tmp_path, monkeypatch, mode):
    from test_v3_compatibility_shards_a11 import source_fixture
    monkeypatch.setattr(c, 'RECORD_DIRECTORY', tmp_path / 'registered')
    sources, reasons = source_fixture(tmp_path)
    record = c.build_record(sources, reasons, tmp_path / 'proof.json', workers=2, mode=mode)
    assert record['passed']
    execution = record['execution']
    assert (execution['mode'], execution['workers'], execution['threads']) == (mode, 2, 1)
    assert execution['settings']['mode'] == mode and execution['settings']['threads'] == 1
    assert execution['worker_control']['mode'] == mode
    assert a.unseal(a.read(tmp_path / 'proof.json'))['execution']['mode'] == mode
