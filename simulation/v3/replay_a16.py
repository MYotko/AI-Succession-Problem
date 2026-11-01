"""Explicit empty-scratch replay adapters for the A14 and A16 extension kinds
(A14 step 2; A16 item 2 of the order of steps; feasibility row
compatibility_a10.py / replay_a14.py).

A compatibility proof re-simulates every recorded replicate of a selected job
from its recorded seed, in an empty scratch root, with the producer's unchanged
``extension_stage``. Recorded checkpoints are read for comparison only and are
never installed as completed work; the ordinary execution path would load them
and return the recorded data, which matches itself. Nothing here can latch or
write a family record, and nothing is computed from replay outputs beyond the
byte comparison. The authorization is the only exception to the reserved-seed
guards, limited to the bound plan's own jobs and seeds. replay_a14.py (the
A13-kind adapter) is unchanged.
"""
from contextvars import ContextVar
from copy import deepcopy
from pathlib import Path
import tempfile

from .artifacts import ROOT, canonical, code_identity, digest, read, scoped, seal, stable_job, unseal

_replay = ContextVar('a16_scratch_replay', default=None)


def _module(kind):
    if kind == 'a14_validate_plain_ext2':
        from . import validation_extension_a14 as module
        return module, module.KIND, 'a14_checkpoints'
    from . import validation_extension_a16 as module
    if kind not in module.KIND_ROUNDS:
        raise ValueError('no replay adapter for job kind ' + str(kind))
    return module, kind, 'a16_checkpoints'


KINDS = ('a14_validate_plain_ext2', 'a16_validate_plain_r1', 'a16_validate_plain_r2')


def checkpoint_directory(kind):
    return _module(kind)[2]


def binding(plan, job, result, checkpoint_documents):
    """Bind a recorded job, its result and its checkpoints to the frozen plan."""
    module, kind, _ = _module(job['kind'])
    require = module.require
    require(plan.get('schema') == module.SCHEMA and module.plan_hash(plan) == plan['plan_hash']
            and job in plan['jobs'] and job['config']['plan_hash'] == plan['plan_hash'], 'extension replay is outside its frozen plan')
    require(plan['jobs'] == [stable_job(kind, dict(c, plan_hash=plan['plan_hash']), 'v3_tables', i)
                             for i, c in enumerate(plan['job_skeletons'])], 'extension replay job skeleton differs')
    module.validate_replicates(job, result['replicates'])
    require(len(checkpoint_documents) == len(result['replicates']), 'replay checkpoint inventory incomplete')
    for checkpoint, replica in zip(checkpoint_documents, result['replicates']):
        require(unseal(checkpoint) == dict(job_sha256=digest(job), replicate=replica), 'recorded extension checkpoint/output mismatch')
    return dict(plan=plan, job=job, result=result, checkpoints=checkpoint_documents)


def authorized_replay(job, root):
    from .compatibility_a10 import _proof_producer
    value = _replay.get()
    return bool(value and _proof_producer.get() == value['plan']['code_hash']
                and value['job'] == job and Path(root) == value['scratch'])


def execute_replay(job, root):
    module, _, _ = _module(job['kind'])
    require = module.require
    require(authorized_replay(job, root), 'extension reserved replay not authorized')
    value, c = _replay.get(), job['config']
    scratch = scoped(root)
    require(not any(scratch.iterdir()), 'extension replay scratch is not empty')
    from . import validation_extension_a13 as a13
    with module.execution_inputs([job]):
        a1 = a13.a4._load_a1(c['a1_source_root'], c['a1_job'], c['a1_source_code_hash'])
        fit = unseal(c['fit'])
        replicas = []
        for recorded, checkpoint in zip(value['result']['replicates'], value['checkpoints']):
            # The recorded seed and order alone determine the work. No recorded
            # checkpoint becomes completed work, and no stop is computed anew.
            fresh = module.extension_stage(a1, fit, c['eligible_rows'], recorded['seed'], c.get('settings_override'))
            fresh.update(replicate=recorded['replicate'], seed=recorded['seed'])
            replicas.append(fresh)
            require(canonical(seal(dict(job_sha256=digest(job), replicate=fresh))) == canonical(checkpoint),
                    'extension replay checkpoint byte mismatch')
    result = deepcopy(value['result'])
    result.update(replicates=replicas, code_hash=code_identity())
    return result


def replay(item):
    value = item['extension_replay']
    verified = binding(value['plan'], item['job'], value['result'], value['checkpoints'])
    directory = scoped(ROOT / '_a16_replay_scratch')
    directory.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix='job_', dir=directory))
    token = _replay.set(dict(verified, scratch=scratch))
    try:
        from .production_runner import execute
        return execute(item['job'], registered=False, root=scratch)
    finally:
        _replay.reset(token)


def original_validation_plan(spec):
    """The sealed original A4 validation plan a registered single-host A14 or A16
    plan descends from, for the proof's scheduling class (A13's R_max / 3 rule)."""
    if spec.get('schema') == 'v3-A16-extension-1':
        from .history_a16 import History
        h = History(spec['history'])
        path = Path(spec['original_plan_path'])
        original = unseal(h.read(path))
        if spec['original_plan_hash'] != original['plan_hash']:
            raise ValueError('A16 replay original plan binding differs')
        return original
    from .history_a14 import History
    h = History(spec['history'])
    old = unseal(h.read(h.role('a13_plan')))
    return unseal(h.read(old['original_plan_path']))
