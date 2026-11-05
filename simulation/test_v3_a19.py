"""A19: a proof-only guard authority for registered reruns, and live thread limits."""
import pytest
import numpy  # noqa: F401  imported first on purpose: the pool is already up

from v3 import artifacts as a, compatibility_a10 as c, production_runner as pr


JOB = {'id': 'rerun_a19_bound', 'kind': 'rerun', 'seed': 7, 'tag': 'v3_tables', 'config': {'steps': 1}}
AUTHORITY = {'a19_proof': True, 'job_id': JOB['id'], 'registration': {'commit': 'x', 'path': 'p', 'sha256': '0' * 64},
             'spec_sha256': '1' * 64}


def test_proof_authority_exists_only_inside_a_proof_and_only_for_its_job():
    assert c.proof_authority(JOB) is None
    granted = c._proof_authority.set(AUTHORITY)
    try:
        assert c.proof_authority(JOB) is None  # no producer context: not a proof
        producer = c._proof_producer.set('f' * 64)
        try:
            assert c.proof_authority(JOB) == AUTHORITY
            assert c.proof_authority(dict(JOB, id='rerun_other')) is None
        finally:
            c._proof_producer.reset(producer)
    finally:
        c._proof_authority.reset(granted)
    assert c.proof_authority(JOB) is None


class _Seen(Exception):
    pass


def _capture_model(monkeypatch):
    seen = {}

    class Model:
        def __init__(self, **kwargs):
            seen['registered'] = kwargs.get('registered')
            self.guards = type('Guards', (), {'authority': 'from-construction' if kwargs.get('registered') else None})()

        def run(self, steps):
            seen['authority'] = self.guards.authority
            raise _Seen

    import v3.recording as recording
    monkeypatch.setattr(recording, 'RecordedV3Model', Model)
    return seen


def test_the_rerun_branch_takes_the_bound_authority_inside_a_proof(monkeypatch):
    seen = _capture_model(monkeypatch)
    producer, granted = c._proof_producer.set('f' * 64), c._proof_authority.set(AUTHORITY)
    try:
        with pytest.raises(_Seen):
            pr.execute(JOB, registered=False, registration=None)
    finally:
        c._proof_authority.reset(granted)
        c._proof_producer.reset(producer)
    assert seen == {'registered': False, 'authority': AUTHORITY}


def test_the_rerun_branch_is_unchanged_outside_a_proof(monkeypatch):
    seen = _capture_model(monkeypatch)
    with pytest.raises(_Seen):
        pr.execute(JOB, registered=False, registration=None)
    assert seen == {'registered': False, 'authority': None}
    # A bound authority for another job grants nothing, even inside a proof.
    producer, granted = c._proof_producer.set('f' * 64), c._proof_authority.set(dict(AUTHORITY, job_id='rerun_other'))
    try:
        with pytest.raises(_Seen):
            pr.execute(JOB, registered=False, registration=None)
    finally:
        c._proof_authority.reset(granted)
        c._proof_producer.reset(producer)
    assert seen['authority'] is None


def test_execute_proof_binds_the_authority_for_one_job_and_resets_it(monkeypatch):
    seen = {}

    def fake_execute(job, registered=False, registration=None, root=None):
        seen['authority'] = c.proof_authority(job)
        return {'value': 1}

    monkeypatch.setattr(pr, 'execute', fake_execute)
    item = {'job': JOB, 'producing_code_hash': 'f' * 64, 'phase_root': '.', 'proof_authority': AUTHORITY}
    fresh = c._execute_proof(item)
    assert fresh.get('error') is None and seen['authority'] == AUTHORITY
    assert c._proof_authority.get() is None and c._proof_producer.get() is None
    c._execute_proof(dict(item, proof_authority=None))
    assert seen['authority'] is None


def test_configure_threads_sets_the_live_limit_after_numpy_is_imported():
    a.configure_threads(2)
    assert all(v['effective'] == 2 for v in a.runtime(2)['threads_verified'])
    a.configure_threads(1)
    assert all(v['effective'] == 1 for v in a.runtime(1)['threads_verified'])
