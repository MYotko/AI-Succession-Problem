"""A13 compatibility replay, authorized only by A14's isolated proof adapter."""
from contextvars import ContextVar
from copy import deepcopy
from pathlib import Path
import tempfile

from .artifacts import ROOT, canonical, code_identity, digest, read, scoped, stable_job, unseal
from . import validation_extension_a13 as a13

_replay = ContextVar('a14_a13_compatibility_replay', default=None)


def binding(plan, job, result, checkpoint_documents):
    from .validation_extension_a14 import APPROVED_A13_PLAN
    a13.require(plan['schema'] == a13.SCHEMA and a13.plan_hash(plan) == plan['plan_hash']
                and job in plan['jobs'] and job['config']['plan_hash'] == plan['plan_hash'],
                'A13 replay is outside its frozen plan')
    a13.require(plan['jobs'] == [stable_job(a13.KIND, dict(c, plan_hash=plan['plan_hash']), 'v3_tables', i)
                                 for i, c in enumerate(plan['job_skeletons'])], 'A13 replay job skeleton differs')
    a13.require(not plan['registered'] or plan['plan_hash'] == APPROVED_A13_PLAN,
                'A13 replay requires the approved plan')
    a13.validate_replicates(job, result['replicates'])
    a13.require(len(checkpoint_documents) == len(result['replicates']), 'replay checkpoint inventory incomplete')
    for checkpoint, replica in zip(checkpoint_documents, result['replicates']):
        a13.require(unseal(checkpoint) == dict(job_sha256=digest(job), replicate=replica),
                    'recorded A13 checkpoint/output mismatch')
    return dict(plan=plan, job=job, result=result, checkpoints=checkpoint_documents)


def authorized_replay(job, root):
    from .compatibility_a10 import _proof_producer
    value = _replay.get()
    return bool(value and _proof_producer.get() == value['plan']['code_hash']
                and value['job'] == job and Path(root) == value['scratch'])


def execute_replay(job, root):
    a13.require(authorized_replay(job, root), 'A13 reserved replay not authorized')
    value, c = _replay.get(), job['config']
    scratch = scoped(root)
    a13.require(not any(scratch.iterdir()), 'A13 replay scratch is not empty')
    a1 = a13.a4._load_a1(c['a1_source_root'], c['a1_job'], c['a1_source_code_hash'])
    fit = unseal(c['fit'])
    replicas = []
    for recorded, checkpoint in zip(value['result']['replicates'], value['checkpoints']):
        # The recorded seed/order alone determines the work. No old checkpoint
        # becomes completed work, and no statistic or stop is computed anew.
        fresh = a13.extension_stage(a1, fit, c['eligible_rows'], recorded['seed'], c.get('settings_override'))
        fresh.update(replicate=recorded['replicate'], seed=recorded['seed'])
        replicas.append(fresh)
        from .artifacts import seal
        a13.require(canonical(seal(dict(job_sha256=digest(job), replicate=fresh))) == canonical(checkpoint),
                    'A13 replay checkpoint byte mismatch')
    result = deepcopy(value['result'])
    result.update(replicates=replicas, code_hash=code_identity())
    return result


def replay(item):
    value = item['a13_replay']
    verified = binding(value['plan'], item['job'], value['result'], value['checkpoints'])
    directory = scoped(ROOT / '_a14_replay_scratch')
    directory.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix='job_', dir=directory))
    token = _replay.set(dict(verified, scratch=scratch))
    try:
        from .production_runner import execute
        return execute(item['job'], registered=False, root=scratch)
    finally:
        _replay.reset(token)
