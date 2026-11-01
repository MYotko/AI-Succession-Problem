"""Stage 2 successor build, phase 2: the post-phase-1 fixes, A16's single-host
orchestration for the four stage 2 families, the receipts, the family-path
clause, the reader interface, and the rehearsal fixtures of A16 item 3.

Fixtures only. No registered output is read; the only registered input is the
committed nominal calibration, and every simulated stream is a rehearsal stream
in [2^128, 2^129) outside every reserve. No fixture reserves or mutates a
registered family anchor."""
from copy import deepcopy
import hashlib
import math
import os
from pathlib import Path
import subprocess
import sys

import pytest
from test_v3_paths import tmp_path
from test_v3_a13 import row_fixture, parameters, source_job, durable
from v3 import artifacts as a
from v3 import validation_extension_a13 as a13
from v3 import validation_extension_a14 as a14
from v3 import validation_extension_a16 as a16
from v3 import history_a16 as h16
from v3 import forecast_a16 as f16
from v3 import replay_a16 as r16
from v3 import admission_a13 as admit
from v3 import tables_a10 as tables
from v3 import continuation_validation as cv
from v3.policies import execution_policy_class
from v3.production_tables import ProductionTables, row_key

A17_COMMIT = "3b8d8261c47b436a95fe831bd7192ede08460d1e"
A10 = {'mapping': 'A10', 'k_star': 1.8, 'g': 'linear'}
CAL_PATH = 'v3/runs/registered/v3_rerun_calibration.json'
SETTINGS = dict(groups=3, runs_per_group=2, particles=2, burn=30, measure=8, census_measure=38)


def inventory_document(seeds_by_category, *, root=None, sources=None, statements=True):
    """A fixture global seed inventory carrying the same bindings as a
    registered one: per category its seeds, its source bindings (path relative
    to simulation/, SHA-256, declared count) and, when empty, the sealed
    statement naming the source checked and why it is empty. A category with
    seeds and no explicit binding gets a sealed seed-source record under
    ``root``, which the validator reads and reconciles exactly."""
    categories = {}
    for name in a16.INVENTORY_CATEGORIES:
        seeds = sorted(seeds_by_category.get(name, []))
        bound = (sources or {}).get(name)
        if bound is None:
            bound = []
            if seeds:
                assert root is not None, 'a fixture category with seeds needs a root for its seed-source record'
                path = Path(root) / 'inventory_sources' / (name + '.json')
                a.atomic_json(path, a.seal(dict(schema=a16.SEED_SOURCE_SCHEMA, category=name, seeds=seeds)))
                bound = [dict(path=path.resolve().relative_to(a.SIMULATION).as_posix(), sha256=a.file_hash(path), count=len(seeds))]
        entry = dict(seeds=seeds, sources=bound)
        if not seeds and statements:
            entry['empty'] = dict(source_checked='fixture inventory for %s' % name, reason='no fixture seeds in this category')
        categories[name] = entry
    return a.seal(dict(schema=a16.INVENTORY_SCHEMA, categories=categories))


# ---------------------------------------------------------------------------
# Part 2a: the Windows containment race (artifacts.scoped)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(os.name != 'nt', reason='the extended-length prefix race is a Windows ntpath.realpath mechanism')
def test_scoped_survives_the_windows_containment_race(tmp_path, monkeypatch):
    """Round 6's deterministic reproduction: a sibling spawn worker creates the
    parent between ntpath.realpath's two _getfinalpathname calls on the exact
    path (winerror 3, then 2), so realpath keeps the \\\\?\\ prefix; the old check
    read that as outside simulation/v3."""
    import ntpath
    target = tmp_path / 'spawned_parent' / 'output.json'
    assert not target.parent.exists()
    real, calls, state = ntpath._getfinalpathname, [], {'first': True}

    def racing(path):
        # realpath asks for the exact path three times: its initial call (winerror
        # 3, the parent is absent), the non-strict first iteration and the
        # prefix-strip check (winerror 2 each: the sibling has created the parent).
        if os.fspath(path) == str(target):
            calls.append(path)
            code = 3 if state['first'] else 2
            state['first'] = False
            raise OSError(code, 'synthetic race', os.fspath(path), code)
        return real(path)
    monkeypatch.setattr(ntpath, '_getfinalpathname', racing)
    raw = Path(os.path.realpath(target))
    assert len(calls) == 3 and os.fspath(raw).startswith('\\\\?\\') and not raw.is_relative_to(a.ROOT)
    expected = tmp_path.resolve() / 'spawned_parent' / 'output.json'
    state['first'], calls[:] = True, []
    assert a.scoped(target) == expected and len(calls) == 3  # the same race, now contained
    monkeypatch.undo()
    assert a.scoped(target) == expected


def test_scoped_unchanged_on_ordinary_paths(tmp_path):
    assert a.scoped(tmp_path / 'ordinary.json') == (tmp_path / 'ordinary.json').resolve()
    with pytest.raises(ValueError, match='outside simulation/v3'):
        a.scoped(a.SIMULATION / 'elsewhere.json')


# ---------------------------------------------------------------------------
# Part 2c: the per-kind qualification validator (A17 sections 2(b) and 6 item 2)
# ---------------------------------------------------------------------------

def _pooled_evidence(code, kinds, per_kind):
    from test_v3_multihost_a11 import FINGERPRINT, SETTINGS as Q_SETTINGS
    from v3 import qualification_a11 as q
    jobs = [a.stable_job(kind, {'phase': 'fixture'}, 'validation', i) for kind in kinds for i in range(per_kind)]
    plan = a.seal(dict(schema=q.SCHEMA + '-plan', non_registered=True, jobs=jobs, kinds=list(kinds), code_hash=code))
    proofs = [dict(job_id=j['id'], kind=j['kind'], job_sha256=a.digest(j), canonical_sha256=a.digest([j, 'result']), worker_seconds=1.)
              for j in jobs]
    ref = dict(schema=q.SCHEMA + '-run', non_registered=True, host='yotko-evo-x2', code_hash=code, plan_sha256=plan['sha256'],
               proofs=proofs, passed=True, elapsed_seconds=20., memory_gb=40., fingerprint=FINGERPRINT, kinds=list(kinds),
               settings=dict(Q_SETTINGS), workers=Q_SETTINGS['workers'])
    return q.compare(plan, a.seal(ref), a.seal(dict(ref, host='alpha')))


def test_qualification_evidence_requires_twenty_distinct_jobs_per_kind():
    from v3 import qualification_a11 as q
    code = a.code_identity()
    assert q.validate_evidence(_pooled_evidence(code, ('fixture', 'a16_validate_plain_r1'), 20), code)['passed']
    # Historical evidence that met the pooled rule (20 distinct jobs over two
    # kinds, 10 each) now fails the per-kind rule.
    pooled = _pooled_evidence(code, ('fixture', 'table'), 10)
    assert len(a.unseal(pooled)['proofs']) == 20
    with pytest.raises(ValueError, match='per kind'):
        q.validate_evidence(pooled, code)
    with pytest.raises(ValueError, match='at least 20 distinct jobs'):
        q.validate_evidence(_pooled_evidence(code, ('fixture',), 19), code)
    assert q.A16_KINDS == {'a16_validate_plain_r1', 'a16_validate_plain_r2'} and q.A16_KINDS <= q.EXTENSION_KINDS


# ---------------------------------------------------------------------------
# Part 3: A16 primitives
# ---------------------------------------------------------------------------

def test_a16_blocks_ordinals_seeds_and_reserve():
    bases = [a16.block_base(f, q) for f in a16.FAMILIES for q in a16.ROUNDS]
    assert bases == [(1 << 62) + (2 * i + q - 1) * (1 << 60) for i in range(4) for q in (1, 2)]
    assert a16.RESERVED == (1 << 62, 12 << 60) and bases[-1] + (1 << 60) == a16.RESERVED[1]
    assert a16.block_base('sigma_squared_x10', 1) == 1 << 63  # the sigma blocks begin at 2^63
    assert a16.ORDINALS[1] == tuple(range(4, 36)) and a16.ORDINALS[2] == tuple(range(36, 68))
    source = source_job()
    for family in a16.FAMILIES:
        for q in a16.ROUNDS:
            manifest = a16.seed_manifest(family, q, [source], 32, [])
            low, high = a16.block_range(family, q)
            assert [m['replicate'] for m in manifest] == list(a16.ORDINALS[q])
            assert all(low <= m['seed'] < high and type(m['seed']) is int for m in manifest)
            assert manifest[0]['seed'] == low + cv._truncated_sha('v3_A16_ext/', family, '/', q, '/', int(source['seed']), '/', a16.ORDINALS[q][0])
    blocks = {(f, q): {m['seed'] for m in a16.seed_manifest(f, q, [source], 32, [])} for f in a16.FAMILIES for q in a16.ROUNDS}
    keys = list(blocks)
    assert all(blocks[x].isdisjoint(blocks[y]) for i, x in enumerate(keys) for y in keys[i + 1:])
    older = {m['seed'] for m in a13.seed_manifest([source], 16, [])} | {m['seed'] for m in a14.seed_manifest([source], 32, [])}
    assert all(s not in older and a16.reserved(s) for seeds in blocks.values() for s in seeds)
    assert a16.reserved(1 << 60) and a16.reserved(1 << 61) and not a16.reserved((1 << 60) - 1) and not a16.reserved(12 << 60)
    with pytest.raises(ValueError, match='ordinals'):
        a16.ext_seed('sqrt', 1, 1, 36)
    with pytest.raises(ValueError, match='ordinals'):
        a16.ext_seed('sqrt', 2, 1, 35)
    with pytest.raises(ValueError):
        a16.ext_seed('nominal', 1, 1, 4)
    with pytest.raises(ValueError, match='exactly two rounds'):
        a16.ext_seed('sqrt', 3, 1, 4)
    rehearsal = a16.seed_manifest('sqrt', 2, [source], 32, [], rehearsal=True)
    assert all((1 << 128) <= m['seed'] < (1 << 129) and not a16.reserved(m['seed']) for m in rehearsal)
    with pytest.raises(a16.Finding, match='collision'):
        a16.seed_manifest('sqrt', 1, [source], 32, [blocks[('sqrt', 1)].pop()])
    assert a16.check_seed_manifest(own := a16.seed_manifest('sqrt', 1, [source], 32, []), [(12 << 60), (1 << 62) - 1],
                                   family='sqrt', q=1)['reserve_occupied_by_history'] is False
    with pytest.raises(a16.Finding, match='collision'):
        a16.check_seed_manifest([manifest[0], manifest[0]], [], family=family, q=q)
    with pytest.raises(ValueError, match='family block'):
        a16.check_seed_manifest(a16.seed_manifest('sqrt', 1, [source], 4, []), [], family='crowding', q=1)
    assert own


def test_a16_occupancy_rule_is_defined_once_for_preparation_and_the_worker(tmp_path, monkeypatch):
    """A16 item 3's occupancy rule: a seed inside this round's own block is a
    finding unless it is this round's own deterministic manifest; a seed
    elsewhere in the reserve is a finding unless a recorded A16 manifest of any
    family and either round holds it; the worker applies the same rule to the
    same inputs."""
    from v3.production_runner import execute
    source = source_job()
    sqrt1 = [m['seed'] for m in a16.seed_manifest('sqrt', 1, [source], 32, [])]
    # A registered round-2 check whose forbidden seeds hold its own round-1 manifest passes.
    sqrt2 = a16.seed_manifest('sqrt', 2, [source], 32, sqrt1, recorded=sqrt1)
    check = a16.check_seed_manifest(sqrt2, sqrt1, family='sqrt', q=2, recorded=sqrt1)
    assert check['passed'] and check['recorded_in_reserve'] == 32 and check['repeated_preparation'] is False
    # Round 1's own manifest in the inventory (a repeated preparation) is not a collision.
    repeated = a16.check_seed_manifest(a16.seed_manifest('sqrt', 1, [source], 32, sqrt1, recorded=sqrt1), sqrt1, family='sqrt', q=1, recorded=sqrt1)
    assert repeated['repeated_preparation'] is True
    # Completed sqrt A16 seeds in crowding's inventory are not a finding when recorded.
    assert a16.seed_manifest('crowding', 1, [source], 32, sqrt1, recorded=sqrt1)
    # The same seeds, recorded by no A16 manifest, are a finding.
    with pytest.raises(a16.Finding, match='no recorded A16 manifest'):
        a16.seed_manifest('crowding', 1, [source], 32, sqrt1)
    # A manual seed inside crowding's round-1 block is a finding for crowding
    # (not its deterministic manifest) and for sqrt (recorded nowhere).
    stray = a16.block_base('crowding', 1) + 12345
    with pytest.raises(a16.Finding, match="own A16 block"):
        a16.seed_manifest('crowding', 1, [source], 32, [stray])
    with pytest.raises(a16.Finding, match="own A16 block"):
        a16.seed_manifest('crowding', 1, [source], 32, [stray], recorded=[stray])
    with pytest.raises(a16.Finding, match='no recorded A16 manifest'):
        a16.seed_manifest('sqrt', 1, [source], 32, [stray])
    with pytest.raises(a16.Finding, match='no recorded A16 manifest'):
        a16.seed_manifest('sqrt', 1, [source], 32, [stray], rehearsal=True)
    # An unrecorded reserve seed is a finding even from a rehearsal's view;
    # a recorded one inside another family's block passes.
    assert a16.seed_manifest('sqrt', 1, [source], 32, [stray], recorded=[stray], rehearsal=True)
    # A round-1 manifest with fewer replicates than the recorded one leaves
    # recorded seeds inside the own block outside the deterministic manifest.
    with pytest.raises(a16.Finding, match="own A16 block"):
        a16.seed_manifest('sqrt', 1, [source], 16, sqrt1, recorded=sqrt1)
    # The worker's check receives the same inputs: a registered round-2
    # configuration whose forbidden seeds hold its own round-1 manifest runs.
    monkeypatch.setattr(a13.a4, '_load_a1', lambda *args: {})
    monkeypatch.setattr(a16, 'extension_stage', lambda source, fit, rows, seed, override: dict(count=6, rows={k: [[0., 1]] * 6 for k in rows}))
    job = a16_job(2, non_registered_rehearsal=False, full_seed_manifest=sqrt2, stream_seeds=[m['seed'] for m in sqrt2],
                  forbidden_seeds=sorted(sqrt1), recorded_a16_seeds=sorted(sqrt1))
    result = execute(job, registered=True, root=tmp_path / a16.PHASES[2])
    assert result['a16_round'] == 2 and result['replicates'][0]['seed'] == sqrt2[0]['seed']
    unrecorded = a.stable_job(a16.KINDS[2], dict(job['config'], recorded_a16_seeds=[]), 'v3_tables', 0)
    with pytest.raises(a16.Finding, match='no recorded A16 manifest'):
        execute(unrecorded, registered=True, root=tmp_path / 'unrecorded')
    colliding = a.stable_job(a16.KINDS[2], dict(job['config'], forbidden_seeds=sorted(sqrt1) + [sqrt2[0]['seed']]), 'v3_tables', 0)
    with pytest.raises(a16.Finding, match='collision'):
        execute(colliding, registered=True, root=tmp_path / 'colliding')


def test_a16_pricing_cap_floor_and_stratum_finding():
    j = source_job()
    j['config']['a10_family'] = 'sqrt'
    projection = a.seal({'per_phase_capability': {'sqrt.1.0.primary.validate_plain': {'jobs': 10, 'x2_hours_max': 3.}}})
    original = {'pull_dispatch': {'projection_sha256': projection['sha256']}}
    price = a16.price_round(original, projection, [j], family='sqrt', registered=False, projection_file_hash=None)
    assert price['R_max'] == 32 and price['projected_x2_hours'] == pytest.approx(3.2) and price['price_cap_x2_hours'] == 15
    assert a13.price_extension(dict(original), projection, [j], registered=False)['R_max'] == 16
    costly = a.seal({'per_phase_capability': {'sqrt.1.0.primary.validate_plain': {'jobs': 1, 'x2_hours_max': 9.}}})
    assert a16.price_round({'projection_sha256': costly['sha256']}, costly, [j], family='sqrt', registered=False,
                           projection_file_hash=None)['R_max'] == 5
    with pytest.raises(ValueError, match='payload seal'):
        a16.price_round({'pull_dispatch': {'projection_sha256': 'bad' * 21 + 'b'}}, projection, [j], family='sqrt', registered=False, projection_file_hash=None)
    with pytest.raises(a16.Finding, match='does not bind'):
        a16.price_round({}, projection, [j], family='sqrt', registered=False, projection_file_hash=None)
    with pytest.raises(a16.Finding, match='stratum price'):
        a16.price_round(original, projection, [dict(j, config=dict(j['config'], setting_name='double_length'))], family='sqrt',
                        registered=False, projection_file_hash=None)
    with pytest.raises(ValueError, match='another family'):
        a16.price_round(original, projection, [j], family='crowding', registered=False, projection_file_hash=None)
    with pytest.raises(ValueError, match='identity'):
        a16.price_round(original, projection, [j], family='sqrt', registered=True, projection_file_hash='wrong')


def test_a16_test_rebases_round2_ordinals_only():
    p = parameters(8)
    data = [dict(replicate=36, trajectories=[[0., 1]] * 7)]
    assert a16.extension_test(data, p, 2)['reason'] == 'N* not reached'
    data.append(dict(replicate=37, trajectories=[[0., 1]] * 7))
    assert a16.extension_test(data, p, 2) == a13.extension_test([dict(r, replicate=r['replicate'] - 32) for r in data], p)
    assert a16.extension_test([dict(r, replicate=r['replicate'] - 32) for r in data], p, 1) == a13.extension_test(
        [dict(r, replicate=r['replicate'] - 32) for r in data], p)
    with pytest.raises(ValueError, match='order'):
        a16.extension_test(data, p, 1)
    with pytest.raises(ValueError, match='order'):
        a16.extension_test([dict(data[0], replicate=20)], p, 2)


def a16_job(q, family='sqrt', r_max=32, **extra):
    source = source_job()
    manifest = a16.seed_manifest(family, q, [source], r_max, [], rehearsal=True)
    config = dict(phase=a16.PHASES[q], a16_family=family, a16_round=q, route='plain', a1_job=source, a1_source_root='unused',
                  a1_source_code_hash=a.code_identity(), eligible_rows={'a': parameters(8), 'b': parameters(9)},
                  M=20, R_max=r_max, full_seed_manifest=manifest, forbidden_seeds=[], recorded_a16_seeds=[],
                  stream_seeds=[m['seed'] for m in manifest], trajectory_count=6, plan_hash='toy',
                  non_registered_rehearsal=True, fit=a.seal(dict(a1_job_id=source['id'], rows=[])), a16_inputs=[])
    config.update(extra)
    return a.stable_job(a16.KINDS[q], config, 'v3_tables', 0)


@pytest.mark.parametrize('q', [1, 2])
def test_a16_stop_checkpoint_resume_and_recheck(tmp_path, monkeypatch, q):
    from v3.production_runner import execute
    job, calls, interrupted = a16_job(q), [], []
    monkeypatch.setattr(a13.a4, '_load_a1', lambda *args: {})

    def stage(source, fit, rows, seed, override):
        calls.append(seed)
        if len(calls) == 2 and not interrupted:
            interrupted.append(seed)
            raise OSError('synthetic interruption')
        return dict(count=6, rows={k: [[0., 1]] * 6 for k in rows})
    monkeypatch.setattr(a16, 'extension_stage', stage)
    with pytest.raises(OSError):
        execute(job, root=tmp_path / a16.PHASES[q])
    assert len(a16.durable_checkpoints(tmp_path, job)) == 1
    result = execute(job, root=tmp_path / a16.PHASES[q])
    first = a16.ORDINALS[q][0]
    assert result['stopped_on_visits'] and [r['replicate'] for r in result['replicates']] == [first, first + 1]
    assert result['a16_family'] == 'sqrt' and result['a16_round'] == q and result['stage'] == a16.PHASES[q]
    seeds = job['config']['stream_seeds']
    assert calls == [seeds[0], seeds[1], seeds[1]]
    assert execute(job, root=tmp_path / a16.PHASES[q]) == result
    with a16.checkpoint_context(tmp_path / 'check', result['replicates'], recheck=True):
        calls.clear()
        assert execute(job, root=tmp_path / a16.PHASES[q]) == result
    assert calls == seeds[:2]
    changed = deepcopy(result['replicates'])
    changed[1]['replicate'] += 1
    with pytest.raises(ValueError, match='seed/order'):
        a16.validate_replicates(job, changed)
    changed = deepcopy(result['replicates'])
    changed.append(deepcopy(changed[-1]))
    with pytest.raises(ValueError, match='past stop'):
        a16.validate_replicates(job, changed)
    with pytest.raises(ValueError, match='round or M'):
        execute(a16_job(q, a16_round=3 - q), root=tmp_path / 'other')


def test_a16_shared_source_stopping(tmp_path, monkeypatch):
    """A source job stops after the first replicate in which every one of its
    eligible rows reaches its own N*; no row is truncated because another finished."""
    from v3.production_runner import execute
    job = a16_job(1, eligible_rows={'fast': parameters(3), 'slow': parameters(3)})
    monkeypatch.setattr(a13.a4, '_load_a1', lambda *args: {})
    seeds = job['config']['stream_seeds']

    def stage(source, fit, rows, seed, override):
        index = seeds.index(seed)
        return dict(count=6, rows={'fast': [[0., 1]] * 6, 'slow': [[0., int(index >= 2)]] * 6})
    monkeypatch.setattr(a16, 'extension_stage', stage)
    result = execute(job, root=tmp_path / a16.PHASES[1])
    assert result['stopped_on_visits'] and len(result['replicates']) == 3
    assert not a16.stop_reached(result['replicates'][:2], job['config']['eligible_rows'])
    assert a16.stop_reached(result['replicates'], job['config']['eligible_rows'])


def test_a16_execute_requires_rehearsal_or_configuration_and_refuses_every_reserve(tmp_path, monkeypatch):
    from v3.production_runner import execute
    monkeypatch.setattr(a16, 'run_stage_job', lambda *args: 'executed')
    job = a16_job(1)
    c = dict(job['config'], non_registered_rehearsal=False)
    with pytest.raises(ValueError, match='requires rehearsal'):
        execute(a.stable_job(a16.KINDS[1], c, 'v3_tables', 0))
    assert execute(job) == 'executed'
    for seed in (1 << 60, 1 << 61, 1 << 62, (12 << 60) - 1):
        c = dict(job['config'], stream_seeds=[seed] + job['config']['stream_seeds'][1:])
        with pytest.raises(ValueError, match='reserved'):
            execute(a.stable_job(a16.KINDS[1], c, 'v3_tables', 0))
    c = dict(job['config'], configuration_test=True, seed=a16.RESERVED[0])
    with pytest.raises(ValueError, match='reserved'):
        execute(a.stable_job(a16.KINDS[1], c, 'configuration', 0))
    c['seed'] = 1 << 128
    assert execute(a.stable_job(a16.KINDS[1], c, 'configuration', 0)) == 'executed'
    assert execute(job, registered=True) == 'executed'


def test_runner_reserved_range_guards_cover_the_a16_reserve(monkeypatch):
    """A non-A16 job whose seed lies in [2^62, 12 x 2^60) is refused by the
    frozen-manifest guard; an A16 job is refused from the A13 and A14 ranges."""
    from v3 import production_runner as pr
    job = a.stable_job('fixture', {'seconds': .01}, 'validation', 0)
    spec = dict(schema='v3-validation-1', registered=False, code_hash=a.code_identity(), tag='validation', jobs=[job],
                phases=['fixture'], configuration={'fixture': dict(kind='fixture', config={}, workers_local=[1], workers_x2=[8, 12, 16, 24, 32], threads=[1])},
                wall_seconds=10, cleanup_reserve_seconds=0, configuration_seconds=1, publication=None)
    settings = dict(profile='local', workers=1, threads=1, cpu_budget=2, mode='normal', caps=pr.caps('local', 2))
    for seed in (1 << 62, (1 << 63) + 7, (12 << 60) - 1):
        forged = dict(spec, jobs=[dict(job, config=dict(job['config'], seed=seed))])
        with pytest.raises(ValueError, match='A16 reserved seed range'):
            pr.validate_spec(forged, settings)
    extension = a16_job(1)
    phase = extension['config']['phase']
    for seed, match in ((1 << 60, 'A13 reserved'), (1 << 61, 'A14 reserved')):
        forged = dict(spec, phases=[phase], jobs=[dict(extension, config=dict(extension['config'], seed=seed))],
                      configuration={phase: dict(spec['configuration']['fixture'], kind=extension['kind'])})
        with pytest.raises(ValueError, match=match):
            pr.validate_spec(forged, settings)


# ---------------------------------------------------------------------------
# The stage 2 toy family: original validation, Part 2 refusal and inventory
# ---------------------------------------------------------------------------

def stage2_toy_original(base, family, *, rule_index=2, cal_path=CAL_PATH):
    """Synthetic A1 and A4 durable records for a stage 2 family, processed by
    the real assemblers, then the original Part 2 refusal through the unchanged
    binding (A16 item 1 starts from this refused candidate)."""
    from v3 import table_validation_a4 as a4
    from v3.offline_estimator import estimate
    from v3.context import Context
    calibration = a.read(a.SIMULATION / cal_path)
    settings = dict(SETTINGS)
    jobs = tables.build_jobs(family, cal_path, settings_override={k: v for k, v in settings.items() if k != 'census_measure'},
                             kernel_override={'n_agents': 16, 'carrying_capacity': 160},
                             rule_ids=[execution_policy_class()[rule_index].rule_id], physical_contexts=[(.064, 1.), (.064, 1.5)])
    jobs = [a.stable_job('table', dict(j['config'], route='plain' if j['config']['kernel']['capability'] == 1 else 'fv'), j['tag'], j['index'])
            for j in jobs]
    source, run = base / 'source', base / 'original'
    outputs = []
    for j in jobs:
        result = estimate(j['config'], j['seed'], calibration)
        lower = Context.build(result['kernel'], calibration).parameters.extinction_flow
        for row in result['rows']:
            row['screens'] = dict(row.get('screens') or {}, route_applicable=True, flow_half_width=True, half_window_drift=True)
            row['continuation'] = {'entries': [{'bin': [1, 0, 0, 0, 0, 0], 'value': lower, 'error': row['flow_range']}],
                                   'heldout_coverage': 1., 'training_fixed_point_converged': True}
            row['lambda_f'] = {'mean': lower, 'replicates': [lower] * 6, 'half_width': 0.}
        result['route'] = j['config']['route']
        for row in result['rows']:
            row['route'] = result['route']
        durable(source / 'tables_A1/table', j, result)
        outputs.append(dict(job=j, result=result, code_hash=a.code_identity()))
    a.atomic_json(source / 'tables_A1_manifest.json', a.seal(dict(jobs=jobs, code_hash=a.code_identity(),
                  source_family={'code_hash': a.code_identity()}, tag='pilot', registered=False)))
    tables.assemble(outputs, calibration, source / 'v3_rerun_tables_A1.json', family, jobs=jobs)
    probe = base / 'probe'
    a.atomic_json(probe / 'seeds.json', {'non_registered': True, 'seed': 84737})
    plan = tables.prepare_validation(source, cal_path, probe_root=probe, settings_override=settings)
    assert plan['a10_family'] == family and plan['a10_stage'] == 2  # the family-path clause fields of a stage 2 plan
    by_id = {o['job']['id']: o for o in outputs}
    for j in plan['jobs']:
        c = j['config']
        source_result = by_id[c['a1_job']['id']]['result']
        common = dict(a1_job_id=c['a1_job']['id'], stream_seed=c['seed'], plan_hash=plan['plan_hash'], code_hash=a.code_identity(), route=c['route'])
        if c['stage'] == 'fit':
            result = dict(common, stage='fit', rows=[{'scoring': r['scoring'], 'c0': {'value': r['lambda_f']['mean'], 'published': True}}
                                                     for r in source_result['rows']])
        elif c['stage'] == 'validate':
            stats = dict.fromkeys(cv.STAT_KEYS, 0.)
            cells = ([dict(stats, cell=1, n_traj=100000, sum_N=100000), dict(stats, cell=cv.POP0_CELL, n_traj=1, sum_N=1)]
                     if c['route'] == 'plain' else [{'cell': 1, 'S_g': [0.] * 32, 'N_g': [100.] * 32}])
            result = dict(common, stage='validate', replicate=c['replicate'], rows=[{'cells': cells, 'scoring': r['scoring']} for r in source_result['rows']])
        else:
            plain = source_result['route'] == 'plain'
            result = dict(common, stage='census', total_living=10000, total_low=50 if plain else 0,
                          cell_counts={1: 9950, 0: 50} if plain else {1: 10000})
        durable(run / c['phase'], j, result)
    projection = a.seal({'per_phase_capability': {family + '.1.0.primary.validate_plain': {
        'jobs': 10, 'x2_hours_max': 3., 'mean_worker_seconds': 30., 'memory_estimate_gb': .1}}})
    plan['pull_dispatch'] = {'projection_sha256': projection['sha256']}
    plan_path = base / 'original_plan.json'
    a.atomic_json(plan_path, a.seal(plan))
    a4.publish(plan, run, source, calibration, base / 'original_family.json', registered=False)
    candidate = run / 'candidate_unpublished_tables.json'
    payload = a.unseal(a.read(candidate))
    rows = {k: a.unseal(v) for k, v in payload['rows'].items()}
    details = a.unseal(a.read(candidate.with_suffix('.cell_results.json')))['rows']
    with pytest.raises(ValueError, match='cap exceeded'):
        admit.checked_binding(rows, details, 'validation_launched_under_A13', run / 'a13_admission_check.json', plan['plan_hash'])
    projection_path = base / 'projection.json'
    a.atomic_json(projection_path, projection)
    seeds = base / 'seeds.json'
    a.atomic_json(seeds, inventory_document({'probe': [84737]}, root=base))
    return dict(family=family, plan_path=plan_path, run=run, candidate=candidate, projection=projection_path, seeds=seeds,
                source=source, cal_path=cal_path, probe=probe, settings=settings, calibration=calibration, plan=plan)


def write_roles(toy, path, *, round1=None):
    roles = dict(original_plan=str(toy['plan_path']), original_root=str(toy['run']), candidate=str(toy['candidate']),
                 original_sidecar=str(toy['candidate'].with_suffix('.cell_results.json')),
                 original_receipt=str(toy['candidate'].with_suffix('.compatibility.json')),
                 original_admission=str(toy['run'] / 'a13_admission_check.json'), a1_root=str(toy['source']),
                 calibration=str(a.SIMULATION / toy['cal_path']), projection=str(toy['projection']))
    if round1 is not None:
        plan, plan_path, root = round1
        roles.update(round1_plan=str(plan_path), round1_public=str(plan_path.with_suffix('.public.json')), round1_root=str(root),
                     round1_record=plan['round_record_path'], round1_admission=plan['admission_record_path'],
                     family_record=plan['family_record_path'])
    # Every toy input lives under simulation/v3, so no historical root is declared.
    a.atomic_json(path, a.seal(dict(roles=roles, compatibility_records=[], historical_roots=[], aliases={})))
    return path


def build_history(toy, base, q, round1=None):
    """Build the round's inventory once; a repeated preparation reuses it."""
    output = base / ('history_r%d.json' % q)
    if output.exists():
        return a.read(output), output
    roles = write_roles(toy, base / ('roles_r%d.json' % q), round1=round1)
    return h16.build_inventory(roles, base / ('copies_r%d' % q), output, round=q), output


def toy_stage(settings, *, value=0., visit=1, slow_from=None, seeds=None):
    def stage(source, fit, rows, seed, override):
        visits = visit
        if slow_from is not None and seeds is not None:
            visits = int(seeds.index(seed) >= slow_from)
        return dict(count=6, settings=settings, rows={k: [[value * p['tau'] if value else 0., visits]] * 6 for k, p in rows.items()})
    return stage


def run_round(plan, plan_path, root, stage, monkeypatch):
    from v3.production_runner import execute
    q = plan['round']
    monkeypatch.setattr(a16, 'extension_stage', stage)
    a16.begin_round(plan, plan_path, root)
    result = None
    for job in plan['jobs']:
        result = execute(job, root=root / a16.PHASES[q])
        durable(root / a16.PHASES[q], job, result)
        record = root / a16.PHASES[q] / 'records' / (job['id'] + '.json')
        a.atomic_json(record, dict(a.read(record), worker_seconds=1.))
    a.atomic_json(root / 'identity.json', dict(code_hash=plan['code_hash'], spec_hash=a.digest(plan)))
    a.atomic_json(root / 'launches.json', [dict(complete=True)])
    checked = plan['jobs'][0]
    a.atomic_json(root / a16.PHASES[q] / 'nondeterminism_check.json', dict(checked=checked['id'], matched=True))
    durable(root / ('_nd_' + a16.PHASES[q]), checked, a.read(root / a16.PHASES[q] / 'outputs' / (checked['id'] + '.json'))['result'])
    record = root / ('_nd_' + a16.PHASES[q]) / 'records' / (checked['id'] + '.json')
    a.atomic_json(record, dict(a.read(record), worker_seconds=1.))
    return result


def prepare_round(toy, base, q, *, round1=None, draws=40, anchor_base=None, **extra):
    _, history_path = build_history(toy, base, q, round1=round1)
    output = base / ('plan_r%d.json' % q)
    plan = a16.prepare(history_path, toy['projection'], toy['seeds'], output, round=q, rehearsal=True,
                       rehearsal_anchor=(anchor_base or base) / 'anchors' / (toy['family'] + '.json'), rehearsal_root=anchor_base or base,
                       draws=draws, **extra)
    return plan, output


# ---------------------------------------------------------------------------
# A16 rounds on the toy families
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('family', a16.FAMILIES)
def test_a16_round1_for_every_family_prepares_publishes_and_forecloses_round2(tmp_path, monkeypatch, family):
    from v3 import table_labels_a5 as labels
    toy = stage2_toy_original(tmp_path, family)
    plan, plan_path = prepare_round(toy, tmp_path, 1)
    assert plan['a16_family'] == family and plan['round'] == 1 and plan['labels_policy'] == a16.LABELS_POLICY[family]
    assert plan['E'] == plan['P'] > 0 and plan['M'] >= plan['P'] and plan['R_max'] == 32 and plan['E2'] is None
    # The launch allowance is the 48 h round ceiling less the non-launch reserve
    # and incurred charges (6 and 0 here), never A14's 15 + 6.
    assert plan['x2_equivalent_hours'] == 42. and plan['round_ceiling_x2_hours'] == 48 and plan['non_launch_reserve_x2_hours'] == 6.
    assert plan['target'] == a16.TARGETS[family] and 'pull_dispatch' not in plan and plan['round1_seed_manifest'] is None
    assert a16.validate_plan(plan) == plan
    # The allowance is inside the hashed plan: an edited allowance is a changed plan.
    with pytest.raises(ValueError, match='plan or source changed'):
        a16.validate_plan(dict(plan, x2_equivalent_hours=21.))
    with pytest.raises(ValueError, match='allowance differs'):
        edited = dict(plan, x2_equivalent_hours=21.)
        edited['plan_hash'] = a16.plan_hash(edited)
        a16.validate_plan(dict(edited, jobs=[a.stable_job(a16.KINDS[1], dict(c, plan_hash=edited['plan_hash']), 'v3_tables', i)
                                            for i, c in enumerate(edited['job_skeletons'])]))
    expected_sizes = {'sqrt': 5, 'crowding': 5, 'sigma_squared_x10': 1, 'sigma_squared_x0.1': 1}
    assert plan['E'] == expected_sizes[family]
    public = a16.public_record(plan)
    assert all(word not in str(public) for word in ('prices', 'n_star', 'width', 'visits', 'original_visits'))
    assert public['family_error_bound_given_fit'] == .05 * (1 + plan['P'] / plan['M'])
    assert public['extension_error_bound'] == .05 * plan['E'] / plan['M']
    assert 0 <= public['forecast']['p_all_part2'] <= 1 and public['forecast']['rates']['basis'].startswith('assumed 1/0')
    # Anchors: the family record and the round record exist before the plan,
    # output-relative for a rehearsal, and bind the family and original hashes.
    stem = (tmp_path / 'anchors' / (family + '.json')).resolve()
    family_record = a.unseal(a.read(a16.family_record_path(stem)))
    round_record = a.unseal(a.read(a16.round_record_path_of(stem, 1)))
    assert family_record['family'] == family and family_record['terminal'] is None and family_record['original'] == plan['original_hashes']
    assert round_record['state'] == 'prepared' and round_record['plan_hash'] == plan['plan_hash'] and round_record['root'] is None
    # The large-integer rehearsal: every rehearsal seed is at or above 2^128 and
    # survives every serialization boundary with exact integer and text equality.
    manifest = plan['seed_manifest']
    assert all(type(m['seed']) is int and (1 << 128) <= m['seed'] < (1 << 129) for m in manifest)
    assert a.unseal(a.read(plan_path))['seed_manifest'] == manifest
    assert all(str(m['seed']).encode() in a.canonical(plan) for m in manifest)
    for job in plan['jobs']:
        assert job['config']['stream_seeds'] == [m['seed'] for m in manifest if m['source_job_id'] == job['config']['a1_job']['id']]
        assert type(job['seed']) is int and job['seed'] >= 1 << 128
    root = tmp_path / 'root_r1'
    result = run_round(plan, plan_path, root, toy_stage(toy['settings']), monkeypatch)
    assert result['stopped_on_visits'] and len(result['replicates']) < plan['R_max']
    for job in plan['jobs']:
        for path in sorted((root / a16.PHASES[1] / 'a16_checkpoints' / job['id']).glob('*.json')):
            replica = a.unseal(a.read(path))['replicate']
            assert type(replica['seed']) is int and replica['seed'] == job['config']['stream_seeds'][replica['replicate'] - 4]
        record = a.read(root / a16.PHASES[1] / 'records' / (job['id'] + '.json'))
        assert record['job']['config']['stream_seeds'] == job['config']['stream_seeds']
    target = tmp_path / 'published.json'
    document, receipt = a16.publish(plan, root, target, registered=False)
    assert receipt['plan_hash'] == a.unseal(a.read(toy['candidate'].with_suffix('.compatibility.json')))['plan_hash']
    assert receipt['stream_seeds'] == a.unseal(a.read(toy['candidate'].with_suffix('.compatibility.json')))['stream_seeds']
    assert set(receipt['a16_rounds']) == {'r1'} and receipt['extension_seed_manifest'] == manifest
    assert all(type(m['seed']) is int for m in receipt['extension_seed_manifest'])
    assert receipt['refusals']['original']['admission_record_sha256'] == plan['original_hashes']['admission_record_sha256']
    assert receipt['labels_policy'] == a16.LABELS_POLICY[family]
    admission = document['payload']['manifest']['a13_admission']
    assert admission['scope'] == 'A10_stage2_after_A16_r1' and admission['a16']['family'] == family and admission['a16']['round'] == 1
    assert admission['rows'] == {}  # every eligible row certified: no residual row
    # The provenance binds the item-10 records (A16 item 8): the family anchor
    # identity, the round identity, the plan hash and the admission record's
    # identity, each cross-checked against the on-disk records.
    bound = admission['a16']
    assert bound['plan_hash'] == plan['plan_hash'] and bound['family_record_sha256'] == a16.family_identity(family_record)
    assert bound['round_record_sha256'] == a16.round_identity(a.unseal(a.read(a16.round_record_path_of(stem, 1))))
    on_disk = a.unseal(a.read(plan['admission_record_path']))
    assert bound['admission_record_sha256'] == a16.admission_identity(on_disk) and 'round1' not in bound
    assert on_disk['classifications_sha256'] == a.digest(on_disk['classifications']) and len(on_disk['classifications']) == plan['E']
    assert all(c['decision'] == 'estimated' and c['test_status'] == 'certified' and c['safeguard'] and c['round'] == 1 for c in on_disk['classifications'])
    assert a16.verify_provenance_records(plan, admission) == on_disk
    with pytest.raises(ValueError, match='on-disk'):
        a16.verify_provenance_records(plan, dict(admission, a16=dict(bound, admission_record_sha256='0' * 64)))
    with pytest.raises(ValueError, match='record identities'):
        admit.verify({k: a.unseal(v) for k, v in document['payload']['rows'].items()},
                     dict(admission, a16={k: v for k, v in bound.items() if k != 'round_record_sha256'}))
    rows = {k: a.unseal(v) for k, v in document['payload']['rows'].items()}
    assert all('a13' not in r for r in rows.values())
    marked = [r for r in rows.values() if 'a16' in r]
    assert len(marked) == plan['E'] and all(r['a16']['rounds']['r1']['retest']['status'] == 'certified' and r['a16']['tested_round'] == 1
                                          and r['a16']['family'] == family and 'n' not in r['a16']['rounds']['r1']['retest'] for r in marked)
    assert all(r['status'] == 'estimated' for r in marked)
    loaded = ProductionTables(target, calibration_hash=toy['calibration']['sha256'])
    assert loaded.fixture and len(loaded.rows) == len(rows)
    # Publication forecloses round 2 and the family record says so.
    family_record = a.unseal(a.read(a16.family_record_path(stem)))
    assert family_record['published_round'] == 1
    with pytest.raises(ValueError, match='already published'):
        prepare_round(toy, tmp_path, 2, round1=(plan, plan_path, root))
    with pytest.raises(ValueError, match='frozen'):
        a.atomic_json(target, a.seal({'changed': True}))
        a16.publish(plan, root, target, registered=False)
    a.atomic_json(target, document)
    if family == 'sqrt':
        identity_path = tmp_path / 'identity.json'
        a.atomic_json(identity_path, dict(family_file_sha256=a.file_hash(target), table_seal_sha256=document['sha256'],
                      receipt_file_sha256=a.file_hash(target.with_suffix('.compatibility.json')),
                      sidecar_file_sha256=a.file_hash(target.with_suffix('.cell_results.json')), producing_commit='toy', code_hash=a.code_identity()))
        label_plan = labels.prepare(target, toy['run'], toy['plan_path'], toy['source'], toy['cal_path'], identity_path, wall_hours=1.,
                                    a3_probe_root=toy['probe'], settings_override=toy['settings'], instrument=tables.family_instrument('sqrt'))
        assert label_plan['jobs'] and not {j['config']['seed'] for j in label_plan['jobs']} & {m['seed'] for m in receipt['extension_seed_manifest']}


def test_a16_launch_allowance_follows_the_round_ceiling():
    assert a16.launch_allowance(6., 0., 3.2) == 42. and a16.launch_allowance(10., 5., 15.) == 33.
    with pytest.raises(ValueError, match='exhausted'):
        a16.launch_allowance(40., 8., 1.)
    with pytest.raises(ValueError, match='below the frozen class price'):
        a16.launch_allowance(40., 0., 9.)
    with pytest.raises(ValueError, match='finite and non-negative'):
        a16.launch_allowance(-1., 0., 1.)


@pytest.mark.parametrize('family', a16.FAMILIES)
def test_a16_round1_refusal_admits_round2_which_decides_finally(tmp_path, monkeypatch, family):
    toy = stage2_toy_original(tmp_path, family)
    plan, plan_path = prepare_round(toy, tmp_path, 1)
    root = tmp_path / 'root_r1'
    result = run_round(plan, plan_path, root, toy_stage(toy['settings'], visit=0), monkeypatch)
    assert not result['stopped_on_visits'] and len(result['replicates']) == plan['R_max']
    target = tmp_path / 'published.json'
    with pytest.raises(ValueError, match='cap exceeded'):
        a16.publish(plan, root, target, registered=False)
    admission_path = Path(plan['admission_record_path'])
    refusal = a.unseal(a.read(admission_path))
    assert refusal['outcome'] == 'refused' and refusal['scope'] == 'A10_stage2_after_A16_r1' and refusal['family'] == family
    assert refusal['tests_round1'] == 0 and refusal['residual_count'] == plan['E'] and not target.exists()
    before = admission_path.read_bytes()
    with pytest.raises(ValueError):
        a16.publish(plan, root, target, registered=False)
    assert admission_path.read_bytes() == before
    stem = (tmp_path / 'anchors' / (family + '.json')).resolve()
    assert a.unseal(a.read(a16.round_record_path_of(stem, 1)))['state'] == 'refused_admission'
    assert a.unseal(a.read(a16.family_record_path(stem)))['terminal'] is None
    # Round 2: every unreached row is eligible again; constants are recomputed and must agree.
    plan2, plan2_path = prepare_round(toy, tmp_path, 2, round1=(plan, plan_path, root), non_launch_reserve_x2_hours=10., incurred_x2_hours=5.)
    assert plan2['round'] == 2 and plan2['E2'] == plan['E'] and plan2['round1_plan_hash'] == plan['plan_hash']
    assert plan2['round1_seed_manifest'] == plan['seed_manifest'] and plan2['x2_equivalent_hours'] == 33.
    assert plan2['forecast']['rates']['basis'].startswith('assumed 1/0') and plan2['forecast']['round'] == 2
    assert {m['seed'] for m in plan2['seed_manifest']}.isdisjoint({m['seed'] for m in plan['seed_manifest']})
    assert [m['replicate'] for m in plan2['seed_manifest'] if m['source_job_id'] == plan2['seed_manifest'][0]['source_job_id']] == list(a16.ORDINALS[2][:plan2['R_max']])
    assert set(plan['forbidden_seeds']) <= set(plan2['forbidden_seeds']) and all(m['seed'] in plan2['forbidden_seeds'] for m in plan['seed_manifest'])
    root2 = tmp_path / 'root_r2'
    result2 = run_round(plan2, plan2_path, root2, toy_stage(toy['settings']), monkeypatch)
    assert result2['stopped_on_visits'] and [r['replicate'] for r in result2['replicates']][0] == 36
    document, receipt = a16.publish(plan2, root2, target, registered=False)
    assert set(receipt['a16_rounds']) == {'r1', 'r2'}
    assert receipt['extension_seed_manifest'] == plan['seed_manifest'] + plan2['seed_manifest']
    assert receipt['refusals']['round1_admission_record_sha256'] == a.file_hash(admission_path)
    assert receipt['a16_rounds']['r1']['admission_record_sha256'] == a.file_hash(admission_path)
    rows = {k: a.unseal(v) for k, v in document['payload']['rows'].items()}
    marked = [r for r in rows.values() if 'a16' in r]
    assert all(set(r['a16']['rounds']) == {'r1', 'r2'} and r['a16']['rounds']['r1']['reason'] == 'N* not reached'
               and r['a16']['rounds']['r2']['retest']['status'] == 'certified' and r['a16']['tested_round'] == 2 for r in marked)
    admission = document['payload']['manifest']['a13_admission']
    assert admission['scope'] == 'A10_stage2_after_A16_r2' and admission['a16']['round1_plan_hash'] == plan['plan_hash']
    # Round 2's provenance binds round 1's plan, sealed admission record and
    # tested set (empty here: round 1 reached no row), and the loader holds the
    # rows carrying round-1 test markers to that set.
    assert admission['a16']['round1'] == dict(plan_hash=plan['plan_hash'], admission_record_sha256=a.file_hash(admission_path),
                                              classifications_sha256=refusal['classifications_sha256'], tested_rows=[])
    assert all(c['round'] is None and c['test_status'] == 'unresolved' for c in refusal['classifications'])
    with pytest.raises(ValueError, match='sealed round-1 tested set'):
        admit.verify(rows, dict(admission, a16=dict(admission['a16'], round1=dict(admission['a16']['round1'], tested_rows=[next(iter(rows))]))))
    hidden = deepcopy(rows)
    for row in hidden.values():
        if 'a16' in row:
            row['a16']['rounds'].pop('r1')
    with pytest.raises(ValueError, match='hide a round-1 marker'):
        admit.verify(hidden, admission)
    assert a.unseal(a.read(a16.family_record_path(stem)))['published_round'] == 2
    assert admission_path.read_bytes() == before  # round 1's records are never rewritten by round 2
    assert a.unseal(a.read(a16.round_record_path_of(stem, 1)))['state'] == 'refused_admission'
    # There is no third round.
    with pytest.raises(ValueError, match='exactly two rounds'):
        prepare_round(toy, tmp_path, 3, round1=(plan2, plan2_path, root2))


@pytest.mark.parametrize('outcome', ['violation', 'unreached', 'halt'])
def test_a16_round2_refusal_halt_or_violation_is_final(tmp_path, monkeypatch, outcome):
    toy = stage2_toy_original(tmp_path, 'sigma_squared_x10')
    plan, plan_path = prepare_round(toy, tmp_path, 1)
    root = tmp_path / 'root_r1'
    run_round(plan, plan_path, root, toy_stage(toy['settings'], visit=0), monkeypatch)
    target = tmp_path / 'published.json'
    with pytest.raises(ValueError, match='cap exceeded'):
        a16.publish(plan, root, target, registered=False)
    plan2, plan2_path = prepare_round(toy, tmp_path, 2, round1=(plan, plan_path, root))
    stem = (tmp_path / 'anchors' / 'sigma_squared_x10.json').resolve()
    old_records = {str(p): a.file_hash(p) for p in (Path(plan['round_record_path']), Path(plan['admission_record_path']))}
    root2 = tmp_path / 'root_r2'
    real_verify, real_test = h16.verify_history, a16.extension_test
    if outcome == 'violation':
        # A real round-2 numerical violation reaching Part 2: pad the verified
        # family with certified rows so the cap admits one residual row, and
        # the violation marker alone refuses admission (A16 item 8).
        verified = h16.verify_history(a.unseal(a.read(plan2_path))['history'], round=2, registered=False)
        template = deepcopy(next(iter(verified['rows'].values())))
        template.update(status='estimated', primary_status='estimated')
        template.pop('reason', None)
        while len(verified['rows']) < 1000:
            key = 'synthetic_padding_' + str(len(verified['rows']))
            verified['rows'][key] = deepcopy(template)
            verified['details'].append(dict(row=key, setting='primary', cell_tests=[]))
        monkeypatch.setattr(h16, 'verify_history', lambda *args, **kw: verified)
        run_round(plan2, plan2_path, root2, toy_stage(toy['settings'], value=3.), monkeypatch)
        with pytest.raises(ValueError, match='violation'):
            a16.publish(plan2, root2, target, registered=False)
        refusal = a.unseal(a.read(plan2['admission_record_path']))
        assert refusal['residual_count'] == refusal['cap'] == 1 and refusal['tests_round2'] == 1 and refusal['outcome'] == 'refused'
    elif outcome == 'unreached':
        run_round(plan2, plan2_path, root2, toy_stage(toy['settings'], visit=0), monkeypatch)
        with pytest.raises(ValueError, match='cap exceeded'):
            a16.publish(plan2, root2, target, registered=False)
        assert a.unseal(a.read(plan2['admission_record_path']))['outcome'] == 'refused'
    else:
        run_round(plan2, plan2_path, root2, toy_stage(toy['settings']), monkeypatch)
        a16.latch_round_halt(root2, 'synthetic scientific halt')
        # Round 1's classifications may be recomputed; the halted round's data may not.
        monkeypatch.setattr(a16, 'extension_test', lambda records, p, q: pytest.fail('halted data were tested') if q == 2
                            else real_test(records, p, q))
        with pytest.raises(ValueError, match='certifies nothing'):
            a16.publish(plan2, root2, target, registered=False)
        assert a.unseal(a.read(a16.round_record_path_of(stem, 2)))['state'] == 'halted'
        assert not Path(plan2['admission_record_path']).exists()
    monkeypatch.setattr(h16, 'verify_history', real_verify)
    monkeypatch.setattr(a16, 'extension_test', real_test)
    assert not target.exists()
    family_record = a.unseal(a.read(a16.family_record_path(stem)))
    assert family_record['terminal'] is not None and family_record['terminal']['round'] == 2 and family_record['published_round'] is None
    assert {str(p): a.file_hash(p) for p in (Path(plan['round_record_path']), Path(plan['admission_record_path']))} == old_records
    # Final: no further preparation on this family, with a new output on the same
    # anchor, or through a different anchor (the verified records refuse it).
    with pytest.raises(ValueError, match='final'):
        prepare_round(toy, tmp_path / 'again', 2, round1=(plan, plan_path, root), anchor_base=tmp_path)
    with pytest.raises(ValueError, match='terminal, published or another realization'):
        prepare_round(toy, tmp_path / 'elsewhere', 2, round1=(plan, plan_path, root))
    with pytest.raises(ValueError):
        a16.begin_round(plan2, plan2_path, tmp_path / 'fresh_root')


def test_a16_never_retests_a_tested_row(tmp_path, monkeypatch):
    """A row tested in round 1 keeps that decision at round 2 whatever its
    outcome; only never-tested unreached rows are eligible (A16 item 7). A
    round-1 violation is a carried-forward defect no later round can repair, so
    round 2 ends as a mechanical no-launch finding (A16 item 10)."""
    toy = stage2_toy_original(tmp_path, 'sqrt')
    plan, plan_path = prepare_round(toy, tmp_path, 1)
    keys = sorted(k for j in plan['jobs'] for k in j['config']['eligible_rows'])
    assert len(keys) == 5

    def stage(source, fit, rows, seed, override):
        # Two rows reach and certify; three never visit.
        return dict(count=6, settings=toy['settings'], rows={k: [[0., 1 if k in keys[:2] else 0]] * 6 for k in rows})
    root = tmp_path / 'root_r1'
    run_round(plan, plan_path, root, stage, monkeypatch)
    with pytest.raises(ValueError, match='cap exceeded'):
        a16.publish(plan, root, tmp_path / 'published.json', registered=False)
    assert a.unseal(a.read(plan['admission_record_path']))['tests_round1'] == 2
    plan2, plan2_path = prepare_round(toy, tmp_path, 2, round1=(plan, plan_path, root))
    eligible = [r['row'] for r in plan2['eligibility'] if r['eligible']]
    assert sorted(eligible) == keys[2:] and plan2['E2'] == 3 and plan2['E'] == 5
    assert plan2['forecast']['rates'] == dict(certification=1., violation=0., tests=2, basis='empirical round-1 test rates')
    history2 = a.unseal(a.read(plan2_path))['history']
    verified = h16.verify_history(history2, round=2, registered=False)
    assert all(verified['tests'][k]['status'] == 'certified' for k in keys[:2])
    assert all(verified['tests'][k]['reason'] == 'N* not reached' for k in keys[2:])
    # The sealed round-1 admission record carries the per-row classifications
    # that round-2 preparation recomputed row by row (A16 item 7).
    sealed = a.unseal(a.read(plan['admission_record_path']))['classifications']
    assert [c['row'] for c in sealed] == keys and [c['round'] for c in sealed] == [1, 1, None, None, None]
    assert [c['test_status'] for c in sealed] == ['certified'] * 2 + ['unresolved'] * 3
    assert [c['decision'] for c in sealed] == ['estimated'] * 2 + ['not_estimable'] * 3 and [c['safeguard'] for c in sealed] == [True] * 2 + [False] * 3
    assert verified['round1']['tested_rows'] == keys[:2]
    # A recomputed classification that differs from the sealed record is a finding.
    real_test = a16.extension_test

    def flipped(records, p, q):
        test = real_test(records, p, q)
        return dict(test, status='unresolved', visit_weighted_ok=False) if test['status'] == 'certified' else test
    monkeypatch.setattr(a16, 'extension_test', flipped)
    with pytest.raises(a16.Finding, match='classification differs from the sealed admission record'):
        h16.verify_history(history2, round=2, registered=False)
    monkeypatch.setattr(a16, 'extension_test', real_test)
    rows, details, tests = a16.reassemble(verified, {k: dict(status='certified', visit_weighted_ok=True, n=8) for k in keys[2:]}, 2, 'sqrt')
    assert rows[keys[0]]['a16']['rounds'] == {'r1': dict(retest=dict(status='certified', visit_weighted_ok=True), reason=None, tested=True)}
    assert rows[keys[0]]['a16']['tested_round'] == 1 and rows[keys[2]]['a16']['tested_round'] == 2
    assert set(rows[keys[2]]['a16']['rounds']) == {'r1', 'r2'} and rows[keys[2]]['a16']['rounds']['r1']['tested'] is False
    assert tests[keys[0]] == verified['tests'][keys[0]]
    with pytest.raises(ValueError, match='exactly the eligible set'):
        a16.reassemble(verified, {k: dict(status='certified', visit_weighted_ok=True, n=8) for k in keys}, 2, 'sqrt')
    # A round-1 violation: the tested row keeps its violation marker, so Part 2
    # can never pass and the family's round 2 ends before entry.
    base = tmp_path / 'violating'
    toy2 = stage2_toy_original(base, 'sqrt')
    plan_v, path_v = prepare_round(toy2, base, 1)
    keys_v = sorted(k for j in plan_v['jobs'] for k in j['config']['eligible_rows'])

    def violating(source, fit, rows, seed, override):
        return dict(count=6, settings=toy2['settings'],
                    rows={k: [[3. * p['tau'] if k == keys_v[0] else 0., 1 if k == keys_v[0] else 0]] * 6 for k, p in rows.items()})
    root_v = base / 'root_r1'
    run_round(plan_v, path_v, root_v, violating, monkeypatch)
    with pytest.raises(ValueError):
        a16.publish(plan_v, root_v, base / 'published.json', registered=False)
    with pytest.raises(a16.Finding, match='carried-forward'):
        prepare_round(toy2, base, 2, round1=(plan_v, path_v, root_v))
    stem = (base / 'anchors' / 'sqrt.json').resolve()
    assert a.unseal(a.read(a16.family_record_path(stem)))['terminal']['round'] == 2
    assert a.unseal(a.read(a16.round_record_path_of(stem, 2)))['state'] == 'refused'
    verified_v = h16.verify_history(a.read(base / 'history_r2.json'), round=2, registered=False)
    assert verified_v['tests'][keys_v[0]]['status'] == 'violation' and verified_v['eligible'][keys_v[0]] is False
    rows_v, _, _ = a16.reassemble(verified_v, {k: dict(status='certified', visit_weighted_ok=True, n=8) for k in keys_v[1:]}, 2, 'sqrt')
    assert rows_v[keys_v[0]]['a16']['rounds'] == {'r1': dict(retest=dict(status='violation', visit_weighted_ok=False), reason=None, tested=True)}
    assert rows_v[keys_v[0]]['status'] == 'not_estimable' and rows_v[keys_v[0]]['a16']['tested_round'] == 1


def test_a16_exact_unchanged_rows_and_sidecar(tmp_path, monkeypatch):
    toy = stage2_toy_original(tmp_path, 'sqrt')
    plan, plan_path = prepare_round(toy, tmp_path, 1)
    verified = h16.verify_history(a.unseal(a.read(plan_path))['history'], round=1, registered=False)
    tests = {k: dict(status='certified', visit_weighted_ok=True, n=8) for k in verified['selected']}
    rows, details, _ = a16.reassemble(verified, tests, 1, 'sqrt')
    for key, row in verified['rows'].items():
        if key not in verified['selected']:
            assert a.canonical(rows[key]) == a.canonical(row)
    before = deepcopy(verified['rows'])
    tampered = deepcopy(rows)
    ineligible = next(k for k in rows if k not in verified['selected'])
    tampered[ineligible]['lambda_f'] = dict(tampered[ineligible]['lambda_f'], mean=123.)
    with pytest.raises(ValueError, match='byte-identical'):
        a13.assert_ineligible_identity(before, tampered, verified['details'], details, set(verified['selected']))


def test_a16_no_launch_floor_and_cannot_be_repaired_are_terminal_findings(tmp_path, monkeypatch):
    toy = stage2_toy_original(tmp_path, 'sqrt')
    monkeypatch.setattr(a16, 'price_round', lambda *args, **kw: dict(R_max=5, projected_x2_hours=1., prices={}))
    with pytest.raises(a16.Finding, match='floor'):
        prepare_round(toy, tmp_path, 1)
    stem = (tmp_path / 'anchors' / 'sqrt.json').resolve()
    record = a.unseal(a.read(a16.round_record_path_of(stem, 1)))
    assert record['state'] == 'refused' and record['failures'][0]['classification'] == 'substantive' and record['plan_hash'] is None
    assert a.unseal(a.read(a16.family_record_path(stem)))['terminal']['round'] == 1
    assert not (tmp_path / 'plan_r1.json').exists()
    monkeypatch.undo()
    with pytest.raises(ValueError, match='final'):
        prepare_round(toy, tmp_path, 1)
    # Carried-forward defects that no certification can repair end the sequence
    # mechanically: a residual row that fails item 12(b) through its sensitivity.
    toy2 = stage2_toy_original(tmp_path / 'second', 'sqrt')
    real = h16.verify_history

    def defective(*args, **kw):
        verified = real(*args, **kw)
        ineligible = next(k for k in verified['rows'] if k not in verified['selected'])
        # A residual row outside the eligible set that fails item 12(b): no C0
        # certification of any eligible row can make Part 2 pass.
        verified['rows'][ineligible].update(status='not_estimable', primary_status='not_estimable',
                                           reason='declared sensitivity subset failed or is incomplete',
                                           sensitivity=dict(selected=True, passed=False, contrasts=[]))
        return verified
    monkeypatch.setattr(h16, 'verify_history', defective)
    with pytest.raises(a16.Finding, match='cannot|carried-forward'):
        prepare_round(toy2, tmp_path / 'second', 1)


def test_a16_tooling_failure_is_logged_classified_and_repeated(tmp_path, monkeypatch):
    toy = stage2_toy_original(tmp_path, 'sigma_squared_x0.1')
    monkeypatch.setattr(f16, 'forecast', lambda *args, **kw: (_ for _ in ()).throw(RuntimeError('synthetic tooling defect')))
    with pytest.raises(RuntimeError, match='tooling defect'):
        prepare_round(toy, tmp_path, 1)
    stem = (tmp_path / 'anchors' / 'sigma_squared_x0.1.json').resolve()
    record = a.unseal(a.read(a16.round_record_path_of(stem, 1)))
    assert record['state'] == 'preparing' and record['failures'][0]['classification'] is None and record['plan_hash'] is None
    assert a.unseal(a.read(a16.family_record_path(stem)))['terminal'] is None
    monkeypatch.undo()
    # A repeat is a resume of the same request, and an unclassified failure
    # blocks it until the interpreter classifies it.
    with pytest.raises(ValueError, match='already reserved'):
        prepare_round(toy, tmp_path, 1)
    with pytest.raises(ValueError, match='unclassified'):
        prepare_round(toy, tmp_path, 1, resume=True)
    a16.classify_failure(stem, 1, 0, 'tooling', 'interpreter')
    plan, _ = prepare_round(toy, tmp_path, 1, resume=True)
    record = a.unseal(a.read(a16.round_record_path_of(stem, 1)))
    assert record['state'] == 'prepared' and record['plan_hash'] == plan['plan_hash'] and record['failures'][0]['reviewer'] == 'interpreter'
    assert record['superseded_plan_hashes'] == []
    # The family anchor logs the failure and the interpreter's classification.
    log = a.unseal(a.read(a16.family_record_path(stem)))['log']
    assert [(e['event'], e.get('classification')) for e in log] == [('failure_recorded', None), ('failure_classified', 'tooling')]
    assert log[1]['reviewer'] == 'interpreter'
    # A substantive classification is terminal for the family.
    toy2 = stage2_toy_original(tmp_path / 'second', 'sigma_squared_x0.1')
    monkeypatch.setattr(f16, 'forecast', lambda *args, **kw: (_ for _ in ()).throw(RuntimeError('synthetic')))
    with pytest.raises(RuntimeError):
        prepare_round(toy2, tmp_path / 'second', 1)
    monkeypatch.undo()
    stem2 = (tmp_path / 'second' / 'anchors' / 'sigma_squared_x0.1.json').resolve()
    a16.classify_failure(stem2, 1, 0, 'substantive', 'interpreter')
    assert a.unseal(a.read(a16.round_record_path_of(stem2, 1)))['state'] == 'refused'
    assert a.unseal(a.read(a16.family_record_path(stem2)))['terminal'] is not None
    with pytest.raises(ValueError, match='final'):
        prepare_round(toy2, tmp_path / 'second', 1, resume=True)


def test_a16_anchors_are_immutable_and_exclusive(tmp_path, monkeypatch):
    from v3 import production_runner as runner
    toy = stage2_toy_original(tmp_path, 'crowding')
    plan, plan_path = prepare_round(toy, tmp_path, 1)
    stem = (tmp_path / 'anchors' / 'crowding.json').resolve()
    # A second preparation output for the same round is another request.
    with pytest.raises(ValueError, match='another request'):
        a16.prepare(tmp_path / 'history_r1.json', toy['projection'], toy['seeds'], tmp_path / 'elsewhere.json', round=1,
                    rehearsal=True, rehearsal_anchor=stem, rehearsal_root=tmp_path, draws=10)
    # The family anchor refuses another realization of the original records.
    with pytest.raises(ValueError, match='another realization'):
        a16.reserve_family(stem, 'crowding', dict(plan['original_hashes'], candidate_file_sha256='0' * 64), registered=False)
    with pytest.raises(ValueError, match='another realization'):
        a16.reserve_family(stem, 'sqrt', plan['original_hashes'], registered=False)
    # Launch binds the round once to its plan and root through the runner.
    monkeypatch.setattr(runner, 'validate_spec', lambda *args: None)
    monkeypatch.setattr(runner, 'configuration_test', lambda *args, **kw: (_ for _ in ()).throw(RuntimeError('synthetic interruption')))
    settings = dict(profile='local', cpu_budget=2, mode='normal', workers=1, threads=1)
    root = tmp_path / 'launched'
    with pytest.raises(RuntimeError, match='synthetic interruption'):
        runner.launch(plan_path, root, settings)
    record = a.unseal(a.read(a16.round_record_path_of(stem, 1)))
    assert record['state'] == 'launched' and record['root'] == str(root.resolve()) and record['spec_hash'] == a.digest(plan)
    with pytest.raises(ValueError, match='different root'):
        runner.launch(plan_path, tmp_path / 'fresh_root', settings)
    copied = tmp_path / 'copied_plan.json'
    a.atomic_json(copied, a.seal(plan))
    with pytest.raises(ValueError, match='different root'):
        runner.launch(copied, tmp_path / 'copied_root', settings)
    a16.latch_round_halt(root, 'synthetic nondeterminism')
    with pytest.raises(ValueError, match='final'):
        runner.launch(plan_path, root, settings)
    assert a.unseal(a.read(a16.round_record_path_of(stem, 1)))['state'] == 'halted'
    assert a.unseal(a.read(a16.family_record_path(stem)))['terminal']['reason'].startswith('round 1 scientific halt')
    # No later round can reserve on the terminal family anchor.
    with pytest.raises(ValueError, match='final'):
        a16.reserve_family(stem, 'crowding', plan['original_hashes'], registered=False)
    # Rehearsal anchors never sit in the registered tree; registered anchors are the family target.
    with pytest.raises(ValueError, match='registered tree'):
        a16.anchor_stem('sqrt', registered=False, rehearsal_anchor=a.ROOT / 'runs' / 'a10_stage2' / 'sqrt' / 'x.json')
    assert a16.anchor_stem('sqrt', registered=True) == a.scoped(a.SIMULATION / a16.TARGETS['sqrt'])
    assert a16.family_record_path(a16.anchor_stem('sqrt', registered=True)).name == 'v3_rerun_tables_A10.a16_family.json'
    assert a16.round_record_path_of(a16.anchor_stem('sqrt', registered=True), 2).name == 'v3_rerun_tables_A10.a16_round2.json'
    assert a16.admission_record_path_of(a16.anchor_stem('sqrt', registered=True), 1).name == 'v3_rerun_tables_A10.a16_round1.admission.json'
    with pytest.raises(ValueError, match='explicit output-relative anchor'):
        a16.anchor_stem('sqrt', registered=False)


def test_a16_worker_scientific_halt_latches_the_family(tmp_path, monkeypatch):
    from v3 import production_runner as runner
    toy = stage2_toy_original(tmp_path, 'sqrt')
    plan, plan_path = prepare_round(toy, tmp_path, 1)
    root = tmp_path / 'root'
    a16.begin_round(plan, plan_path, root)
    monkeypatch.setattr(a16, 'extension_stage', lambda *args: (_ for _ in ()).throw(a16.ScientificHalt('truncated extension trajectory')))
    monkeypatch.setattr(runner, 'runtime', lambda threads: {'threads_configured': threads})
    job = plan['jobs'][0]
    with pytest.raises(a16.ScientificHalt):
        runner.worker(str(root / a16.PHASES[1]), job, a.code_identity(), 1, False, None)
    assert (root / 'a16_scientific_halt.json').exists()
    stem = (tmp_path / 'anchors' / 'sqrt.json').resolve()
    assert a.unseal(a.read(a16.round_record_path_of(stem, 1)))['halt']['kind'] == 'scientific_halt'
    assert a.unseal(a.read(a16.family_record_path(stem)))['terminal'] is not None
    with pytest.raises(ValueError, match='certifies nothing'):
        a16.publication_round(plan, root)
    # The launch refuses at the round binding (the family is terminal) before the
    # runner's own halt-file guard, as A13's and A14's launches do.
    with pytest.raises(ValueError, match='final'):
        runner.launch(plan_path, root, dict(profile='local', cpu_budget=2, mode='normal', workers=1, threads=1))


def test_a16_decline_before_launch_is_terminal(tmp_path, monkeypatch):
    toy = stage2_toy_original(tmp_path, 'sigma_squared_x10')
    plan, plan_path = prepare_round(toy, tmp_path, 1)
    stem = (tmp_path / 'anchors' / 'sigma_squared_x10.json').resolve()
    with pytest.raises(ValueError, match='operator and reason'):
        a16.decline(stem, 1, operator=' ', reason='x')
    a16.decline(stem, 1, operator='operator', reason='scheduling is not a decline; this is one')
    record = a.unseal(a.read(a16.round_record_path_of(stem, 1)))
    assert record['state'] == 'refused' and record['halt']['operator'] == 'operator'
    assert a.unseal(a.read(a16.family_record_path(stem)))['terminal']['round'] == 1
    with pytest.raises(ValueError, match='final'):
        a16.begin_round(plan, plan_path, tmp_path / 'root')
    with pytest.raises(ValueError, match='before launch'):
        a16.decline(stem, 1, operator='operator', reason='again')


# ---------------------------------------------------------------------------
# History verification, forecast and replay adapters
# ---------------------------------------------------------------------------

def test_a16_history_verifier_is_read_only_and_binds_the_refusal(tmp_path, monkeypatch):
    toy = stage2_toy_original(tmp_path, 'sqrt')
    document, history_path = build_history(toy, tmp_path, 1)
    before = {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    verified = h16.verify_history(document, round=1, registered=False)
    assert verified['family'] == 'sqrt' and verified['E'] == 5 and verified['tests'] == {} and verified['round1'] is None
    assert all(v['original_visits'] == 3 and v['original_trajectories'] == 18 for v in verified['visits'].values())
    assert before == {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    with pytest.raises(ValueError, match='another round'):
        h16.verify_history(document, round=2, registered=False)
    nominal = deepcopy(a.unseal(document))
    nominal['family'] = 'nominal'
    with pytest.raises(ValueError, match='four stage 2 families'):
        h16.verify_history(a.seal(nominal), round=1, registered=False)
    payload = deepcopy(a.unseal(document))
    row = next(r for r in payload['files'] if r['source'].endswith('a13_admission_check.json'))
    copy = Path(row['copy'])
    refusal = a.unseal(a.read(copy))
    refusal['outcome'] = 'passed'
    copy.chmod(0o600)
    a.atomic_json(copy, a.seal(refusal))
    copy.chmod(0o444)
    with pytest.raises(ValueError, match='copy changed'):
        h16.verify_history(document, round=1, registered=False)
    row.update(sha256=a.file_hash(copy), bytes=copy.stat().st_size)
    with pytest.raises(ValueError, match='Part 2 refusal'):
        h16.verify_history(a.seal(payload), round=1, registered=False)
    with pytest.raises(ValueError, match='every declared role'):
        h16.build_inventory(write_roles(toy, tmp_path / 'roles_bad.json'), tmp_path / 'c', tmp_path / 'h.json', round=2)


def test_a16_forecast_model_determinism_and_disclosure(tmp_path, monkeypatch):
    assert f16.reach_probability(18, 18, 1, 6) == 1.
    assert f16.reach_probability(0, 100, 50, 6) < 1e-6
    assert 0 < f16.reach_probability(3, 18, 10, 192) < 1
    with pytest.raises(ValueError):
        f16.reach_probability(19, 18, 1, 6)
    with pytest.raises(ValueError):
        f16.reach_probability(3.0, 18, 1, 6)
    assert f16.prior_rates({}) == dict(certification=1., violation=0., tests=0, basis='assumed 1/0: no prior extension test')
    assert f16.forecast_seed('sqrt', 1, 32) == int(hashlib.sha256(a.canonical(['A16-admission-forecast', 'sqrt', 1, 32])).hexdigest(), 16) & ((1 << 60) - 1)
    toy = stage2_toy_original(tmp_path, 'sqrt')
    document, _ = build_history(toy, tmp_path, 1)
    verified = h16.verify_history(document, round=1, registered=False)
    eligible = sorted(verified['selected'])
    first = f16.forecast(verified, 32, family='sqrt', round=1, eligible=eligible, draws=30)
    second = f16.forecast(verified, 32, family='sqrt', round=1, eligible=eligible, draws=30)
    assert first == second and first['draws'] == 30 and first['R_max'] == 32 and first['eligible_rows'] == 5
    assert 0 <= first['p_all_part2'] <= 1 and 0 <= first['p_all_part2_certification_0_9'] <= 1
    assert first['p_all_part2_certification_0_9'] <= first['p_all_part2'] + 1e-12
    assert all(word not in str({k: v for k, v in first.items() if k != 'model'}) for word in ('n_star', 'original_visits', 'width', 'value'))
    assert first['tooling']['source_sha256'] == a.file_hash(a.ROOT / 'forecast_a16.py') and 'admission_a13.py' in first['tooling']['repository_imports']
    with pytest.raises(ValueError, match='frozen eligible set'):
        f16.forecast(verified, 32, family='sqrt', round=1, eligible=eligible[:-1], draws=5)


def test_replay_adapters_reexecute_in_empty_scratch_and_detect_joint_perturbation(tmp_path, monkeypatch):
    """Both the A14 and the A16 adapters re-simulate every recorded replicate
    from its seed into empty scratch; a perturbed checkpoint and output together
    mismatch, so an adapter that loaded checkpoints would fail the drill."""
    from test_v3_a14 import job_fixture
    from v3 import compatibility_a10 as compat
    monkeypatch.setattr(a13.a4, '_load_a1', lambda *args: {})
    calls = []
    for module, job in ((a14, job_fixture()), (a16, a16_job(1)), (a16, a16_job(2))):
        def stage(source, fit, rows, seed, override):
            calls.append(seed)
            return dict(count=6, rows={k: [[0., 1]] * 6 for k in rows})
        monkeypatch.setattr(module, 'extension_stage', stage)
        config = {k: v for k, v in job['config'].items() if k != 'plan_hash'}
        plan = dict(schema=module.SCHEMA, registered=False, code_hash=a.code_identity(), job_skeletons=[config])
        plan['plan_hash'] = module.plan_hash(plan)
        job = a.stable_job(job['kind'], dict(config, plan_hash=plan['plan_hash']), 'v3_tables', 0)
        plan['jobs'] = [job]
        result = module.run_stage_job(job, tmp_path / job['kind'])
        directory = r16.checkpoint_directory(job['kind'])
        checkpoints = [a.read(tmp_path / job['kind'] / directory / job['id'] / f'{r["replicate"]:02d}.json') for r in result['replicates']]
        bound = r16.binding(plan, job, result, checkpoints)
        item = dict(job=job, extension_replay=bound)
        assert not r16.authorized_replay(job, tmp_path)
        monkeypatch.setattr(r16, 'ROOT', tmp_path / ('isolated_' + job['kind']))
        token = compat._proof_producer.set(plan['code_hash'])
        try:
            calls.clear()
            assert r16.replay(item) == result
            assert calls == job['config']['stream_seeds'][:len(result['replicates'])]
            changed = deepcopy(result)
            pair = next(iter(changed['replicates'][-1]['rows'].values()))[0]
            pair[0] += .01
            pair[1] += 1
            altered = [a.seal(dict(job_sha256=a.digest(job), replicate=r)) for r in changed['replicates']]
            item['extension_replay'] = r16.binding(plan, job, changed, altered)
            with pytest.raises(ValueError, match='byte mismatch'):
                r16.replay(item)
            with pytest.raises(ValueError, match='checkpoint/output mismatch'):
                r16.binding(plan, job, result, altered)
        finally:
            compat._proof_producer.reset(token)
    with pytest.raises(ValueError, match='no replay adapter'):
        r16.checkpoint_directory('a13_validate_plain_ext')


def test_a16_pull_dispatch_is_refused_at_this_identity(tmp_path):
    from v3 import multihost_a11 as multi
    job = a16_job(1)
    spec = dict(schema=a16.SCHEMA, registered=False, instrument=A10, code_hash=a.code_identity(), tag='v3_tables', jobs=[job],
                phases=[a16.PHASES[1]], configuration={}, wall_seconds=100, x2_equivalent_hours=1., publication=None)
    costs = {key: dict(mean_worker_seconds=1., memory_estimate_gb=.1) for key in multi.cost_keys(job)}
    with pytest.raises(ValueError, match='unsupported pull job kind'):
        multi.freeze(spec, a.seal(dict(per_phase_capability=costs)), code_commit='fixture')
    assert not set(a16.KINDS.values()) & multi.ALLOWED_KINDS


def test_a16_qualification_builds_non_reserved_short_streams_per_kind(tmp_path, monkeypatch):
    from v3 import qualification_a11 as q
    toy = stage2_toy_original(tmp_path, 'sqrt')
    plan, plan_path = prepare_round(toy, tmp_path, 1)
    built = q.build(plan_path, tmp_path / 'root_r1', tmp_path / 'qualification.json', kinds=[a16.KINDS[1]])
    assert built['kinds'] == [a16.KINDS[1]] and len(built['jobs']) >= 20 and len({j['id'] for j in built['jobs']}) == len(built['jobs'])
    assert all(j['tag'] == 'validation' and j['config']['configuration_test'] and (1 << 128) <= j['config']['seed'] < (1 << 129)
               and not a16.reserved(j['config']['seed']) for j in built['jobs'])
    assert all(j['id'] in built['memory_estimate_gb'] for j in built['jobs'])
    with pytest.raises(ValueError, match='unsupported qualification kind'):
        q.build(plan_path, tmp_path / 'root_r1', tmp_path / 'other.json', kinds=['a16_validate_plain_r2'])


# ---------------------------------------------------------------------------
# Part 2b: the A4 refusal-write clause and admission at the A17 pin
# ---------------------------------------------------------------------------

def test_a4_publish_at_the_a17_pin_writes_the_refused_candidate_and_admits_positive_cases(tmp_path, monkeypatch):
    from v3 import table_validation_a4 as a4, calibration as cal
    toy = stage2_toy_original(tmp_path, 'sqrt')
    plan = deepcopy(toy['plan'])
    plan['registration'] = {'commit': A17_COMMIT}
    monkeypatch.setattr(a4, 'registered_publish_guard', lambda p: None)
    monkeypatch.setattr(a4, '_recompute_plan_hash', lambda p: p['plan_hash'])
    monkeypatch.setattr(tables, 'verify_estimation_source', lambda *args, **kw: None)
    monkeypatch.setattr(a, 'verify_registration', lambda *args, **kw: None)
    monkeypatch.setattr(cal, 'validate_calibration', lambda document, **kw: a.unseal(document))
    for suffix in ('.json', '.cell_results.json', '.compatibility.json'):
        toy['candidate'].with_suffix(suffix).unlink()
    (toy['run'] / 'a13_admission_check.json').unlink()
    target = tmp_path / 'never.json'
    # The family-path clause holds a registered stage 2 plan to its fixed target;
    # this fixture redirects sqrt's fixed target to the test path.
    monkeypatch.setattr(tables, 'STAGE2_PATHS', dict(tables.STAGE2_PATHS, sqrt=(CAL_PATH, target.relative_to(a.SIMULATION).as_posix())))
    with pytest.raises(ValueError, match='cap exceeded'):
        a4.publish(plan, toy['run'], toy['source'], toy['calibration'], target, registered=True)
    assert not target.exists()
    refused = a.unseal(a.read(toy['candidate']))
    assert refused['fixture'] is False and 'a13_admission' not in refused['manifest']
    assert a.unseal(a.read(toy['run'] / 'a13_admission_check.json'))['outcome'] == 'refused'
    # The preserved refusal feeds A16 item 1 unchanged.
    document, _ = build_history(toy, tmp_path, 1)
    assert h16.verify_history(document, round=1, registered=False)['E'] == 5
    # Positive and no-op original admissions at the new pin, through the real
    # binding, write and loader paths (synthetic rows; assembly substituted).
    source = tmp_path / 'synthetic_source'
    a.atomic_json(source / 'v3_rerun_tables_A1.json', a.seal({'manifest': {'a10': {'family': 'crowding'}}}))
    a.atomic_json(source / 'tables_A1_manifest.json', a.seal({'jobs': []}))
    monkeypatch.setattr(cal, 'validate_calibration', lambda document, **kw: document)
    for residual in (1, 0):
        rows, details = {}, []
        for i in range(1000 + residual):
            row, detail, _ = row_fixture(context=i)
            row['calibration_hash'] = 'c'
            if i >= residual:
                row.update(status='estimated', primary_status='estimated')
                row.pop('reason', None)
                row['primary_reason'] = None
            key = row_key(row)
            rows[key], detail['row'], detail['status'] = row, key, row['status']
            details.append(detail)
        monkeypatch.setattr(a4, 'assemble_family', lambda *args, **kw: (rows, 'passed', details))
        monkeypatch.setattr(a4, 'counts_from_job_outputs', lambda *args, **kw: {'M': 1, 'M_FV': 0})
        monkeypatch.setattr(a4, '_verify_stage_outputs', lambda plan, root: ({}, {}))
        synthetic = dict(registered=True, registration={'commit': A17_COMMIT[:8]}, instrument=A10, calibration_path='unused', jobs=[],
                         source_file_sha256=a.file_hash(source / 'v3_rerun_tables_A1.json'),
                         source_manifest_sha256=a.digest(a.unseal(a.read(source / 'tables_A1_manifest.json'))),
                         code_hash=a.code_identity(), plan_hash='p%d' % residual, M=1, M_FV=0, source_code_hash='s', stream_tags=[])
        run = tmp_path / ('run_%d' % residual)
        out = tmp_path / ('admitted_%d.json' % residual)
        a4.publish(synthetic, run, source, {'sha256': 'c'}, out, registered=True)
        admission = a.unseal(a.read(out))['manifest']['a13_admission']
        assert admission['scope'] == 'validation_launched_under_A13' and len(admission['rows']) == residual
        loaded = ProductionTables(out, calibration_hash='c', registered=True)
        assert sum(r['status'] == 'not_estimable' for r in loaded.rows.values()) == residual
        assert admit.enabled(loaded) == bool(residual)


# ---------------------------------------------------------------------------
# Part 4: receipts, the family-path clause and the reader interface
# ---------------------------------------------------------------------------

def synthetic_a10_family(path, family, *, fv=True):
    """A registered-loadable synthetic family document for one stage 2 family,
    with its A4 compatibility receipt beside it."""
    from v3.instrument import CONSTANTS_SHA256
    rows = {}
    for i in range(3):
        row, _, _ = row_fixture(context=i)
        row.update(status='estimated', primary_status='estimated', calibration_hash='c',
                   scoring=dict(alpha=1., capability=1., kappa=8., **tables.family_instrument(family).declaration()))
        row.pop('reason', None)
        if fv and i == 0:
            row.update(route='fv', fv_label='asymptotic, not certified')
            row.pop('c0', None)
        rows[row_key(row)] = row
    manifest = dict(tag='v3_tables', calibration_hash='c', required_row_keys=sorted(rows), complete_family=True,
                    sensitivity_status='passed', a10=dict(family=family, producer_code_hash=a.code_identity(),
                    constants_sha256=CONSTANTS_SHA256, instruments=[tables.family_instrument(family).declaration()]))
    payload = dict(schema='v3-tables-1', fixture=False, code_hash=a.code_identity(), manifest=manifest,
                   manifest_hash=a.digest(manifest), rows={k: a.seal(r) for k, r in rows.items()})
    document = a.seal(payload)
    a.atomic_json(path, document)
    receipt = a.seal(dict(schema='v3-A4-receipt-1', table_seal_sha256=document['sha256'], table_file_sha256=a.file_hash(path),
                          producer_code_hash=a.code_identity(), calibration_sha256='c', M=1, M_FV=1, plan_hash='p', stream_seeds={}))
    a.atomic_json(path.with_suffix('.compatibility.json'), receipt)
    return document


@pytest.mark.parametrize('family', tables.NO_LABEL_FAMILIES)
def test_authenticated_no_label_receipt_per_variant_family(tmp_path, family):
    path = tmp_path / 'family.json'
    document = synthetic_a10_family(path, family)
    receipt = tables.finalize_no_label_receipt(path)
    payload = a.unseal(receipt)
    assert payload['schema'] == tables.NO_LABEL_RECEIPT_SCHEMA and payload['family'] == family
    assert 'labels' not in payload and 'labels_sha256' not in payload and payload['labels_policy'] == tables.NO_LABEL_AUTHORITY
    assert payload['table_sha256'] == document['sha256'] and payload['validation_receipt_sha256'] == a.file_hash(path.with_suffix('.compatibility.json'))
    loaded = ProductionTables(path, calibration_hash='c', registered=True)
    loaded.require_a10(tables.family_instrument(family))
    fv = next(r for r in loaded.rows.values() if r['route'] == 'fv')
    assert fv['fv_label'] == 'asymptotic, not certified' and fv['status'] == 'estimated'
    # The same receipt is frozen; a labels receipt is refused for this family.
    assert tables.finalize_no_label_receipt(path) == receipt
    with pytest.raises(ValueError, match='makes no A5 labels'):
        tables.finalize_receipt(path, tmp_path / 'labels.json')
    # Negative cases: a forged strict labels receipt, another family's receipt,
    # a receipt carrying a labels hash, and a changed authority all refuse.
    receipt_path = path.with_suffix('.a10_receipt.json')
    for change in ('schema', 'family', 'labels_sha256', 'authority', 'table'):
        forged = deepcopy(payload)
        if change == 'schema':
            forged['schema'] = 'v3-A10-table-receipt-1'
        elif change == 'family':
            forged['family'] = next(f for f in tables.NO_LABEL_FAMILIES if f != family)
        elif change == 'labels_sha256':
            forged['labels_sha256'] = 'f' * 64
        elif change == 'authority':
            forged['labels_policy'] = dict(tables.NO_LABEL_AUTHORITY, authority='unsigned flag')
        else:
            forged['table_sha256'] = '0' * 64
        a.atomic_json(receipt_path, a.seal(forged))
        with pytest.raises(ValueError, match='mismatch'):
            ProductionTables(path, calibration_hash='c', registered=True).require_a10(tables.family_instrument(family))
    receipt_path.unlink()
    with pytest.raises(ValueError, match='requires its producer receipt'):
        ProductionTables(path, calibration_hash='c', registered=True).require_a10(tables.family_instrument(family))


def test_sqrt_keeps_the_strict_a5_receipt_and_refuses_the_exemption(tmp_path):
    from v3.table_labels_a5 import label_for
    path = tmp_path / 'sqrt.json'
    document = synthetic_a10_family(path, 'sqrt')
    with pytest.raises(ValueError, match='keeps A5'):
        tables.finalize_no_label_receipt(path)
    # The positive sqrt case: an A5 label record covering every estimated FV
    # row's validated cells builds the strict receipt, which the loader accepts.
    rows = {k: a.unseal(v) for k, v in document['payload']['rows'].items()}
    labels_doc = dict(schema='v3-A5-label-1', code_hash=a.code_identity(),
                      a4_family=dict(table_seal_sha256=document['sha256'], family_file_sha256=a.file_hash(path)),
                      rows=[dict(row_key=k, scoring=r['scoring'], cells=[dict(cell=int(c), status='unresolved', label=label_for('unresolved'))
                                                                        for c in cv.fine_codes([e['bin'] for e in r['continuation']['entries']])])
                            for k, r in rows.items() if r['route'] == 'fv' and r['status'] == 'estimated'])
    labels_path = tmp_path / 'labels.json'
    a.atomic_json(labels_path, a.seal(labels_doc))
    receipt = a.unseal(tables.finalize_receipt(path, labels_path))
    assert receipt['schema'] == 'v3-A10-table-receipt-1' and receipt['labels_sha256'] == a.file_hash(labels_path)
    loaded = ProductionTables(path, calibration_hash='c', registered=True)
    loaded.require_a10(tables.family_instrument('sqrt'))
    with pytest.raises(ValueError, match='A5 labels'):
        a.atomic_json(labels_path, a.seal(dict(labels_doc, rows=[])))
        a.atomic_json(path.with_suffix('.a10_receipt.json'), a.seal(dict(receipt, labels=a.read(labels_path), labels_sha256=a.file_hash(labels_path))))
        ProductionTables(path, calibration_hash='c', registered=True).require_a10(tables.family_instrument('sqrt'))
    path.with_suffix('.a10_receipt.json').unlink()
    # A no-label receipt forged onto the sqrt family never selects the exempt branch.
    forged = dict(schema=tables.NO_LABEL_RECEIPT_SCHEMA, family='sqrt', table_sha256=a.read(path)['sha256'],
                  producer_code_hash=a.code_identity(), constants_sha256=tables.CONSTANTS_SHA256, calibration_sha256='c',
                  validation_receipt_sha256=a.file_hash(path.with_suffix('.compatibility.json')),
                  validation_receipt=a.read(path.with_suffix('.compatibility.json')), labels_policy=tables.NO_LABEL_AUTHORITY)
    a.atomic_json(path.with_suffix('.a10_receipt.json'), a.seal(forged))
    with pytest.raises(ValueError, match='missing validation/labels'):
        ProductionTables(path, calibration_hash='c', registered=True).require_a10(tables.family_instrument('sqrt'))
    # The nominal family is untouched by the policy too.
    nominal = tmp_path / 'nominal.json'
    synthetic_a10_family(nominal, 'nominal')
    with pytest.raises(ValueError, match='keeps A5'):
        tables.finalize_no_label_receipt(nominal)
    assert tables.STAGE2_LABELS_POLICY == a16.LABELS_POLICY and tables.NO_LABEL_FAMILIES == a16.NO_LABEL_FAMILIES


def test_family_path_clause_strings_and_builder_assertion(monkeypatch):
    assert {f: tables.STAGE2_PATHS[f][1] for f in a16.FAMILIES} == a16.TARGETS
    assert {f: tables.STAGE2_PATHS[f][0] for f in a16.FAMILIES} == a16.CALIBRATIONS
    assert tables.STAGE2_PATHS['nominal'][1] == a13.TARGET and a13.TARGET == 'v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.json'
    assert all(not p.startswith('/') and '\\' not in p for pair in tables.STAGE2_PATHS.values() for p in pair)
    monkeypatch.setattr(a, 'verify_registration', lambda pin, **kwargs: pin)
    from test_v3_stage2_phase1 import PATHS, CEILINGS, history_inputs, reserved_ranges
    assert PATHS == tables.STAGE2_PATHS
    stage1 = tables.stage1_run_specs(PATHS['nominal'][0], PATHS['nominal'][1], {'fixture': True},
                                     dict(main=50.49, k1p5=10.94, k2p3=10.93, weight_corner=44.34, horizon=10.27))
    history = tables.stage2_history_seeds(PATHS['nominal'][0], **history_inputs(stage1))
    ranges = reserved_ranges() + [a16.RESERVED]
    registry = tables.stage2_seed_registry(PATHS, history, reserved_ranges=ranges)
    specs = tables.stage2_run_specs(PATHS, {'fixture': True}, CEILINGS, registry)
    for name, spec in specs.items():
        assert spec['a10_labels_policy'] == a16.LABELS_POLICY[name]
        assert spec['a10_family_paths'] == dict(calibration_path=PATHS[name][0], tables_path=PATHS[name][1])
    other = dict(PATHS, sqrt=(PATHS['sqrt'][0], 'v3/runs/elsewhere/sqrt.json'))
    foreign = tables.stage2_seed_registry(other, history, reserved_ranges=ranges)
    with pytest.raises(ValueError, match='canonical family paths'):
        tables.stage2_run_specs(other, {'fixture': True}, CEILINGS, foreign)
    # No stage 2 seed falls in the A16 reserve, and the registry records it.
    assert registry['reserved_ranges'][-1] == [1 << 62, 12 << 60]


def test_metadata_only_sigma_block_values_cross_every_serializer_exactly(tmp_path):
    """Exact seeds at or above 2^63 through the record, manifest and receipt
    serializers, without drawing from the reserved streams."""
    source = source_job()
    values = {}
    for family in ('sigma_squared_x10', 'sigma_squared_x0.1'):
        for q in a16.ROUNDS:
            manifest = a16.seed_manifest(family, q, [source], 32, [])
            assert all(m['seed'] >= 1 << 63 for m in manifest)
            check = a16.check_seed_manifest(manifest, [], family=family, q=q)
            assert check['block'][0] >= 1 << 63 and check['seeds'] == 32
            values[(family, q)] = manifest
    boundary = [(1 << 63) - 1, 1 << 63, (1 << 63) + 1, a16.block_base('sigma_squared_x0.1', 2) + (1 << 60) - 1, a16.RESERVED[1] - 1]
    record = dict(manifests={'%s/%d' % k: v for k, v in values.items()}, boundary=boundary,
                  receipt=dict(extension_seed_manifest=[m for v in values.values() for m in v]))
    path = tmp_path / 'sigma_blocks.json'
    a.atomic_json(path, a.seal(record))
    back = a.unseal(a.read(path))
    assert back == record and all(type(s) is int for s in back['boundary']) and back['boundary'] == boundary
    assert all(type(m['seed']) is int and m['seed'] == original['seed'] for key, v in values.items()
               for m, original in zip(back['manifests']['%s/%d' % key], v))
    for seed in boundary[1:]:
        assert str(seed).encode() in a.canonical(record) and int(str(seed)) == seed
        assert float(seed) != seed or int(float(seed)) != seed or seed % 2 == 0  # a float path would not round-trip odd values
    assert int(float((1 << 63) + 1)) != (1 << 63) + 1


def test_a5_seed_exclusion_covers_the_a16_reserve():
    from unittest.mock import patch
    from v3.table_labels_a5 import assert_a5_seeds
    for value in (1 << 60, 1 << 61, 1 << 62, (1 << 63) + 5, (12 << 60) - 1):
        with pytest.raises(cv.SeedCollision):
            with patch('v3.table_labels_a5.fvplain_seed', return_value=value):
                assert_a5_seeds([42], set())
    # The first integer past the reserve is admissible again.
    with patch('v3.table_labels_a5.fvplain_seed', side_effect=lambda seed, r: (12 << 60) + r):
        assert assert_a5_seeds([42], set()) == {(42, r): (12 << 60) + r for r in (1, 2, 3)}


def test_reader_tail_parameter_default_unchanged_and_actual_threshold_recorded():
    import numpy as np
    from v3 import reading_a6 as r6
    grid = list(r6.R1_GRID)
    # The audit's between-threshold case: survivors only at rr 0.066, 58 of 100
    # in the arm and 219 of 400 in the comparator, seed 20261011, alpha 0.05/18.
    arm = {rr: (np.array([50] * 58 + [5] * 42) if rr == grid[-1] else np.full(100, 5)) for rr in grid}
    nominal = {rr: (np.array([50] * 219 + [5] * 181) if rr == grid[-1] else np.full(400, 5)) for rr in grid}
    default = r6.compare_boundary(arm, nominal, grid=grid, seed=20261011, alpha=.05 / 18)
    assert default['undefined_resample_tail'] == r6.UNDEFINED_RESAMPLE_TAIL == .05 / 66
    assert default['verdict'] == 'undetermined' and '%.5f' % (.05 / 66) in default['reason']
    assert default == r6.compare_boundary(arm, nominal, grid=grid, seed=20261011, alpha=.05 / 18, undefined_resample_tail=r6.UNDEFINED_RESAMPLE_TAIL)
    a10 = r6.compare_boundary(arm, nominal, grid=grid, seed=20261011, alpha=.05 / 18, undefined_resample_tail=.05 / 36)
    assert a10['undefined_resample_tail'] == .05 / 36 and a10['verdict'] != 'undetermined'
    assert a10['undefined_resample_fraction'] == default['undefined_resample_fraction']
    assert r6.UNDEFINED_RESAMPLE_TAIL < default['undefined_resample_fraction'] <= .05 / 36
    # Equality is allowed: a share equal to the tail is not undetermined.
    equal = r6.compare_boundary(arm, nominal, grid=grid, seed=20261011, alpha=.05 / 18, undefined_resample_tail=default['undefined_resample_fraction'])
    assert equal['verdict'] != 'undetermined'
    tight = r6.compare_boundary(arm, nominal, grid=grid, seed=20261011, alpha=.05 / 18, undefined_resample_tail=default['undefined_resample_fraction'] / 2)
    assert tight['verdict'] == 'undetermined' and '%.5f' % (default['undefined_resample_fraction'] / 2) in tight['reason']
    for bad in (-.1, 1., True):
        with pytest.raises(ValueError):
            r6.compare_boundary(arm, nominal, grid=grid, seed=20261011, alpha=.05 / 18, undefined_resample_tail=bad)
    # The default arithmetic is pinned: the robust A6 case reads as before.
    cells = {rr: np.full(200, 50 if i > 4 else 5) for i, rr in enumerate(grid)}
    robust = r6.compare_boundary(cells, {k: v.copy() for k, v in cells.items()}, grid=grid)
    assert robust['verdict'] == 'robust' and robust['undefined_resample_tail'] == .05 / 66
    assert len(r6.headline_comparisons()) == 33


def test_reader_state_contract_enabled_and_pooled_incidence():
    from types import SimpleNamespace
    zero = SimpleNamespace(payload={'manifest': {'a13_admission': {'rows': {}}}})
    assert admit.enabled(zero) is False
    assert admit.enabled(SimpleNamespace(payload={'manifest': {}})) is False
    assert admit.enabled(SimpleNamespace(payload={'manifest': {'a13_admission': {'rows': {'k': {}}}}})) is True
    admitted = admit.summarize([dict(branch='ordinary_allocation', evaluated=True, affected=True, excluded_by_reason={admit.MISSING: 1},
                                     balanced_fallback_reason=None, selected_score_unavailable_reason=None),
                                dict(branch='yield_review', evaluated=True, affected=False, excluded_by_reason={},
                                     balanced_fallback_reason=None, selected_score_unavailable_reason=None)])
    # The separately frozen reader normalizes a verified no-admitted family from
    # its recorded decisions: structural zero numerators over derived denominators.
    normalized = {b: dict(numerator=0, denominator=d, rate=0. if d else None, assessed=bool(d),
                          provenance=dict(numerator='structural_zero_from_verified_family', denominator='derived_from_recorded_decisions'))
                  for b, d in (('ordinary_allocation', 7), ('survival_first', 0), ('yield_review', 2))}
    pooled = admit.pooled_incidence([admitted, normalized])
    assert pooled['branches']['ordinary_allocation'] == dict(numerator=1, denominator=8, rate=1 / 8, assessed=True, per_run_rates=[1., 0.])
    assert pooled['branches']['survival_first'] == dict(numerator=0, denominator=0, rate=None, assessed=False, per_run_rates=[None, None])
    assert pooled['branches']['yield_review']['denominator'] == 3 and pooled['affected_by_table_unavailability'] is True
    unaffected = admit.pooled_incidence([normalized])
    assert not unaffected['affected_by_table_unavailability'] and unaffected['branches']['survival_first']['assessed'] is False
    with pytest.raises(KeyError):
        admit.pooled_incidence([{}])  # a missing field is an integrity failure for the reader, never a zero


def test_pilot_a7_comparison_is_scoped_and_r4_builders_refuse_a10_stage_paths():
    from v3 import pilot_a10, sensitivity_a6 as s6
    assert 'A15' in pilot_a10.A7_CEILING_SCOPE and 'R4' in pilot_a10.A7_CEILING_SCOPE
    import inspect
    text = inspect.getsource(pilot_a10)
    assert '"a6_ceiling_x2_hours"' not in text and '"a6_within_ceiling"' not in text
    with pytest.raises(ValueError, match='refuse A10 stage table paths'):
        s6.crowding_run_spec('HEAD', {}, crowding_paths=(CAL_PATH, a16.TARGETS['crowding']), a1_source_root=None, probe_root=None,
                             rerun_manifest=None, seed_registry={})
    with pytest.raises(ValueError, match='refuse A10 stage table paths'):
        s6.sigma_run_spec('HEAD', {}, 'sigma_squared_x10', (CAL_PATH, a16.TARGETS['sigma_squared_x10']), a1_source_root=None,
                          probe_root=None, rerun_manifest=None, seed_registry={})
    with pytest.raises(ValueError, match='refuse A10 stage table paths'):
        s6.nominal_run_spec('HEAD', {}, a1_source_root=None, probe_root=None, rerun_manifest=None, seed_registry={},
                            tables_path=a13.TARGET)


# ---------------------------------------------------------------------------
# Fix round 1: admission provenance and markers, history staging, resume at a
# changed identity, the registered inventory, the sigma closure, the family-path
# clause at A4 publication, forecast draws, the explicit reserve arguments and
# launch-time kind coverage
# ---------------------------------------------------------------------------

def _marked_rows(count, family='sqrt', **marker):
    """Synthetic estimated rows, each carrying an A16 marker; no residual row,
    so the admitted set is empty and the marker checks alone decide."""
    rows, details = {}, []
    for i in range(count):
        row, detail, _ = row_fixture(context=i)
        row.update(status='estimated', primary_status='estimated', primary_reason=None, calibration_hash='c')
        row.pop('reason', None)
        row['a16'] = deepcopy(dict(family=family, certified_by_extension=True, tested_round=1,
                                   rounds={'r1': dict(retest=dict(status='certified', visit_weighted_ok=True), reason=None, tested=True)}, **marker))
        key = row_key(row)
        rows[key], detail['row'], detail['status'] = row, key, row['status']
        details.append(detail)
    return rows, details


def test_a16_admission_provenance_requires_record_identities_and_checks_every_row():
    rows, details = _marked_rows(3)
    scope1, scope2 = a16.SCOPES[1], a16.SCOPES[2]
    # Provenance without the record hashes is refused; the hypothetical form is
    # accepted by the binding and refused by the loader.
    with pytest.raises(ValueError, match='record identities'):
        admit.binding(rows, details, scope1, provenance=dict(family='sqrt', round=1))
    with pytest.raises(ValueError, match='record identities'):
        admit.binding(rows, details, scope1, provenance=dict(family='sqrt', round=1, plan_hash='a' * 64, family_record_sha256='b' * 64,
                                                             round_record_sha256='c' * 64))
    full = dict(family='sqrt', round=1, plan_hash='a' * 64, family_record_sha256='b' * 64, round_record_sha256='c' * 64,
                admission_record_sha256='d' * 64)
    bound = admit.binding(rows, details, scope1, provenance=full)
    assert bound['a16'] == full and admit.verify(rows, bound) == set()
    hypothetical = admit.binding(rows, details, scope1, provenance=dict(family='sqrt', round=1, hypothetical=True))
    with pytest.raises(ValueError, match='never admitted'):
        admit.verify(rows, hypothetical)
    with pytest.raises(ValueError, match='True only'):
        admit.binding(rows, details, scope1, provenance=dict(full, hypothetical=False))
    # An estimated row retaining a round-1 violation is refused, whatever its status.
    violating = deepcopy(rows)
    next(iter(violating.values()))['a16']['rounds']['r1']['retest']['status'] = 'violation'
    with pytest.raises(ValueError, match='violation cannot be admitted'):
        admit.binding(violating, details, scope1, provenance=full)
    with pytest.raises(ValueError, match='violation cannot be admitted'):
        admit.verify(violating, bound)
    # A row of another family, or a nominal marker on a stage 2 row, refuses.
    foreign = deepcopy(rows)
    next(iter(foreign.values()))['a16']['family'] = 'crowding'
    with pytest.raises(ValueError, match='another family'):
        admit.verify(foreign, bound)
    nominal = deepcopy(rows)
    next(iter(nominal.values()))['a13'] = dict(certified_by_extension=True)
    with pytest.raises(ValueError, match='nominal-round marker'):
        admit.verify(nominal, bound)
    # Round 2: round 1's tested set is bound; a residual (or any) row without its
    # round-1 marker refuses; the rows carrying round-1 test markers equal the set.
    keys = sorted(rows)
    full2 = dict(full, round=2, round1=dict(plan_hash='e' * 64, admission_record_sha256='f' * 64, classifications_sha256='1' * 64,
                                            tested_rows=keys))
    rows2 = deepcopy(rows)
    for key in keys:
        rows2[key]['a16']['rounds']['r2'] = dict(retest=dict(status='unresolved', visit_weighted_ok=False), reason='N* not reached', tested=False)
    assert admit.verify(rows2, admit.binding(rows2, details, scope2, provenance=full2)) == set()
    with pytest.raises(ValueError, match="round 1's record identities"):
        admit.binding(rows2, details, scope2, provenance=dict(full2, round1=dict(tested_rows=keys)))
    with pytest.raises(ValueError, match="round 1's tested set"):
        admit.binding(rows2, details, scope2, provenance=dict(full, round=2))
    residual = deepcopy(rows2)
    hidden_key = keys[0]
    residual[hidden_key].update(status='not_estimable', primary_status='not_estimable', reason='A4 availability floor failed',
                                primary_reason='A4 availability floor failed')
    residual[hidden_key]['a16']['rounds'] = {'r2': residual[hidden_key]['a16']['rounds']['r2']}
    residual_details = [dict(d, status=residual[d['row']]['status']) for d in details]
    with pytest.raises(ValueError, match='hide a round-1 marker'):
        admit.binding(residual, residual_details, scope2, provenance=full2)
    with pytest.raises(ValueError, match='sealed round-1 tested set'):
        admit.binding(rows2, details, scope2, provenance=dict(full2, round1=dict(full2['round1'], tested_rows=keys[1:])))
    # Hypothetical round-2 provenance carries the tested set too.
    admit.binding(rows2, details, scope2, provenance=dict(family='sqrt', round=2, hypothetical=True, round1=dict(tested_rows=keys)))
    with pytest.raises(ValueError, match='sealed round-1 tested set'):
        admit.binding(rows2, details, scope2, provenance=dict(family='sqrt', round=2, hypothetical=True, round1=dict(tested_rows=[])))
    # The nominal scopes refuse any A16 marker on any row and any provenance.
    with pytest.raises(ValueError, match='outside an A16 admission scope'):
        admit.binding(rows, details, 'A10_nominal_after_A13')
    with pytest.raises(ValueError, match='A16 scopes only'):
        admit.binding({}, [], 'A10_nominal_after_A13', provenance=full)


def test_a16_history_staging_refuses_anchor_destinations_before_any_filesystem_write(tmp_path, monkeypatch):
    import shutil
    import tempfile
    toy = stage2_toy_original(tmp_path, 'sqrt')
    document, _ = build_history(toy, tmp_path, 1)
    payload = a.unseal(document)
    view_root = Path(payload['view_root'])
    assert view_root == (tmp_path / 'copies_r1').resolve()
    # Every write primitive the copy loop uses is intercepted.
    for target, name in ((os, 'replace'), (os, 'fdopen'), (os, 'fsync'), (tempfile, 'mkstemp'), (shutil, 'copyfileobj'),
                         (Path, 'mkdir'), (Path, 'chmod'), (Path, 'write_bytes'), (Path, 'open')):
        monkeypatch.setattr(target, name, lambda *args, **kw: pytest.fail('filesystem write before the destination check'))
    crowding = a.SIMULATION / a16.TARGETS['crowding']
    cases = [(a16.family_record_path(crowding), 'anchor'), (crowding, 'anchor'), (crowding.parent / 'loose.json', 'registered tree'),
             (a.ROOT / 'runs' / 'registered' / 'loose.json', 'registered tree'), (tmp_path / 'outside_view' / 'x.json', 'view root'),
             (a16.admission_record_path_of(a.SIMULATION / a16.TARGETS['sigma_squared_x0.1'], 2), 'anchor'),
             ((a.SIMULATION / a13.TARGET).with_suffix('.a14_round.json'), 'anchor')]
    for destination, kind in cases:
        forged = deepcopy(payload)
        forged['files'][0]['copy'] = str(destination)
        with pytest.raises(ValueError, match='outside the declared history view root'):
            h16.stage_history(a.seal(forged), view_root)
        if kind != 'view root':
            # Under a wide view root (simulation/v3 itself) the anchor and tree checks refuse.
            with pytest.raises(ValueError, match='registered tree or an anchor'):
                h16.stage_history(a.seal(forged), a.ROOT)
    # A view root inside the registered trees, or missing, refuses before anything.
    for bad in (a.ROOT / 'runs' / 'a10_stage2' / 'view', a.ROOT / 'runs' / 'registered'):
        with pytest.raises(ValueError, match='inside the registered tree'):
            h16.stage_history(document, bad)
    with pytest.raises(ValueError, match='declared absolute history view root'):
        h16.stage_history(document, None)
    with pytest.raises(TypeError):
        h16.stage_history(document)
    assert a16.protected_anchors() >= {(a.SIMULATION / a16.TARGETS[f]).resolve() for f in a16.FAMILIES} | {(a.SIMULATION / a13.TARGET).resolve()}
    assert len(a16.protected_anchors()) == 4 * 6 + 5
    monkeypatch.undo()
    # The declared view root stages the same inventory without change.
    before = {str(p): a.file_hash(p) for p in view_root.rglob('*') if p.is_file()}
    h16.stage_history(document, view_root)
    assert {str(p): a.file_hash(p) for p in view_root.rglob('*') if p.is_file()} == before


def test_a16_fixture_publication_refuses_registered_targets_and_anchors(tmp_path, monkeypatch):
    toy = stage2_toy_original(tmp_path, 'crowding')
    plan, plan_path = prepare_round(toy, tmp_path, 1)
    root = tmp_path / 'root_r1'
    run_round(plan, plan_path, root, toy_stage(toy['settings']), monkeypatch)
    for target in (a.SIMULATION / a16.TARGETS['crowding'], a.SIMULATION / a16.TARGETS['sqrt'], a.SIMULATION / a13.TARGET,
                   a16.family_record_path(a.SIMULATION / a16.TARGETS['crowding']), a.ROOT / 'runs' / 'registered' / 'fixture.json',
                   a.ROOT / 'runs' / 'a10_stage2' / 'crowding' / 'fixture.json'):
        with pytest.raises(ValueError, match='fixture publication refuses'):
            a16.publish(plan, root, target, registered=False)
        assert not Path(target).exists()
    assert not Path(plan['admission_record_path']).exists()  # refused before any record
    document, _ = a16.publish(plan, root, tmp_path / 'published.json', registered=False)
    assert document['payload']['fixture'] is True


def test_a16_resume_at_a_changed_identity_needs_a_direct_compatibility_record(tmp_path, monkeypatch):
    from v3 import compatibility_a10 as compat
    stem = (tmp_path / 'anchors' / 'sqrt.json').resolve()
    original = dict(plan_file_sha256='1' * 64, candidate_file_sha256='2' * 64, sidecar_file_sha256='3' * 64,
                    receipt_file_sha256='4' * 64, admission_record_sha256='5' * 64)
    a16.reserve_family(stem, 'sqrt', original, registered=False)
    recorded = a.code_identity()
    request = dict(family='sqrt', round=1, history_sha256='h' * 64, output=str(tmp_path / 'plan.json'), code_hash=recorded, registered=False)
    path = a16.reserve_round(stem, 'sqrt', 1, request)
    a16.record_failure(stem, 1, 'synthetic tooling defect', classification='tooling')
    changed = 'f' * 64
    monkeypatch.setattr(a16, 'code_identity', lambda: changed)
    moved = dict(request, code_hash=changed)
    # Everything but the code identity must be equal; a changed identity needs the record.
    with pytest.raises(ValueError, match='another request'):
        a16.reserve_round(stem, 'sqrt', 1, dict(moved, output='elsewhere'), resume=True)
    with pytest.raises(ValueError, match='needs a direct A11 compatibility record'):
        a16.reserve_round(stem, 'sqrt', 1, moved, resume=True)
    record_path = tmp_path / 'A11_compatibility_fixture.json'
    a.atomic_json(record_path, a.seal(dict(producing_code_hash=recorded, new_code_hash=changed)))
    calls = []

    def validate_record(p):
        calls.append(str(p))
        value = a.unseal(a.read(p))
        return value['producing_code_hash']
    monkeypatch.setattr(compat, 'validate_record', validate_record)
    # A record from another identity, or one not ending at the current identity, refuses.
    a.atomic_json(tmp_path / 'other.json', a.seal(dict(producing_code_hash='0' * 64, new_code_hash=changed)))
    with pytest.raises(ValueError, match='recorded identity to the current one'):
        a16.reserve_round(stem, 'sqrt', 1, moved, resume=True, compatibility_record=tmp_path / 'other.json')
    with pytest.raises(ValueError, match='recorded identity to the current one'):
        a16.reserve_round(stem, 'sqrt', 1, dict(request, code_hash='e' * 64), resume=True, compatibility_record=record_path)
    assert a.unseal(a.read(path))['request'] == request  # refusals changed nothing
    assert a16.reserve_round(stem, 'sqrt', 1, moved, resume=True, compatibility_record=record_path) == path
    record = a.unseal(a.read(path))
    assert record['request'] == moved and record['state'] == 'preparing' and calls[-1] == str(record_path) and len(calls) == 3
    assert record['log'] == [dict(event='identity_changed', prior_code_hash=recorded, new_code_hash=changed, prior_plan_hash=None,
                                  prior_superseded_plan_hashes=[], compatibility_record_sha256=a.file_hash(record_path), epoch=record['log'][0]['epoch'])]
    assert record['failures'][0]['classification'] == 'tooling'
    # A round with no logged failure cannot change identity even with a record.
    second = a16.reserve_round(stem, 'sqrt', 2, dict(request, round=2))
    with pytest.raises(ValueError, match='follows a logged, tooling-classified failure'):
        a16.reserve_round(stem, 'sqrt', 2, dict(moved, round=2), resume=True, compatibility_record=record_path)
    assert a.unseal(a.read(second))['request'] == dict(request, round=2)
    # The same request resumes again without a record; a bound root refuses regardless.
    assert a16.reserve_round(stem, 'sqrt', 1, moved, resume=True) == path
    a16._update(path, lambda r: r.update(root=str(tmp_path / 'launched'), plan_hash='p' * 64, spec_hash='s' * 64, state='launched'))
    with pytest.raises(ValueError, match='already launched'):
        a16.reserve_round(stem, 'sqrt', 1, dict(moved, code_hash='9' * 64), resume=True, compatibility_record=record_path)
    monkeypatch.setattr(a16, 'code_identity', lambda: '9' * 64)
    with pytest.raises(ValueError, match='already launched'):
        a16.reserve_round(stem, 'sqrt', 1, dict(moved, code_hash='9' * 64), resume=True, compatibility_record=record_path)
    # prepare passes the record through to the reservation.
    monkeypatch.undo()
    toy = stage2_toy_original(tmp_path / 'toy', 'sqrt')
    monkeypatch.setattr(f16, 'forecast', lambda *args, **kw: (_ for _ in ()).throw(RuntimeError('synthetic tooling defect')))
    with pytest.raises(RuntimeError):
        prepare_round(toy, tmp_path / 'toy', 1)
    monkeypatch.undo()
    toy_stem = (tmp_path / 'toy' / 'anchors' / 'sqrt.json').resolve()
    a16.classify_failure(toy_stem, 1, 0, 'tooling', 'interpreter')
    monkeypatch.setattr(a16, 'code_identity', lambda: changed)
    with pytest.raises(ValueError, match='needs a direct A11 compatibility record'):
        prepare_round(toy, tmp_path / 'toy', 1, resume=True)
    assert a.unseal(a.read(a16.round_record_path_of(toy_stem, 1)))['failures'][-1]['classification'] == 'tooling'  # refused before any new failure record


def test_a16_registered_inventory_binds_sources_and_reconciles_to_frozen_records(tmp_path, monkeypatch):
    import subprocess
    from v3 import tables_a10, compatibility_a10 as compat
    relative = tmp_path.relative_to(a.SIMULATION).as_posix()
    # The committed stage 2 seed registry: this fixture stands in for HEAD.
    monkeypatch.setattr(compat, '_committed_bytes', lambda p: Path(p).read_bytes())
    # An all-empty inventory in registered mode is a finding: without statements
    # at the statement, with statements at the reconciled categories.
    with pytest.raises(a16.Finding, match='lacks its sealed statement'):
        a16.validate_inventory(inventory_document({}, statements=False), registered=True)
    with pytest.raises(a16.Finding, match='binds no frozen source record'):
        a16.validate_inventory(inventory_document({}), registered=True)
    empty = a16.validate_inventory(inventory_document({}), registered=False)
    assert empty == dict(seeds={k: [] for k in a16.INVENTORY_CATEGORIES}, recorded_a16_seeds=[])
    # Sources are hash-verified files under simulation/ in both modes; the
    # listed seeds equal exactly what the sources contribute, and in registered
    # mode the reconciled categories bind their frozen records.
    registry = dict(schema=tables_a10.STAGE2_REGISTRY_SCHEMA, table_jobs={'sqrt': [11, 12]}, a4_streams={'sqrt': [13]},
                    a5_streams={'sqrt': [14]}, runs={'sqrt': [15, 16]})
    a13_plan = dict(schema=a13.SCHEMA, registered=True, seed_manifest=[dict(seed=21), dict(seed=22)], forbidden_seeds=[23])
    a14_plan = dict(schema=a14.SCHEMA, registered=True, seed_manifest=[dict(seed=31)], forbidden_seeds=[32, 33])
    a16_public = dict(schema=a16.SCHEMA + '-public', seed_manifest=[dict(seed=a16.block_base('sqrt', 1) + 1)],
                      seed_check=dict(non_registered_rehearsal=False))
    files = dict(stage2=registry, a13_manifest=a13_plan, a13_forbidden=a13_plan, a14_manifest=a14_plan, a14_forbidden=a14_plan,
                 a16_manifests=a16_public, probe=dict(schema=a16.SEED_SOURCE_SCHEMA, category='probe', seeds=[84737]))
    sources = {}
    for name, payload in files.items():
        path = tmp_path / (name + '.json')
        a.atomic_json(path, a.seal(payload))
        sources[name] = [dict(path=relative + '/' + name + '.json', sha256=a.file_hash(path), count=0)]
    seeds = dict(stage2=[11, 12, 13, 14, 15, 16], a13_manifest=[21, 22], a13_forbidden=[23], a14_manifest=[31], a14_forbidden=[32, 33],
                 a16_manifests=[a16.block_base('sqrt', 1) + 1], probe=[84737])
    for name in seeds:
        sources[name][0]['count'] = len(seeds[name])
    good = inventory_document(seeds, sources=sources)
    verified = a16.validate_inventory(good, registered=True)
    flat = verified['seeds']
    assert flat['stage2'] == seeds['stage2'] and flat['a16_manifests'] == seeds['a16_manifests'] and flat['rehearsal'] == []
    assert verified['recorded_a16_seeds'] == seeds['a16_manifests']
    # A category whose listed seeds differ from what its bound source contributes
    # is a finding in both modes: one missing, or one extra.
    short = dict(seeds, stage2=seeds['stage2'][:-1])
    for registered in (True, False):
        with pytest.raises(a16.Finding, match=r'lists 5 seed\(s\) against the 6 its bound sources contribute \(0 extra, 1 missing\)'):
            a16.validate_inventory(inventory_document(short, sources=sources), registered=registered)
        extra = dict(seeds, a16_manifests=seeds['a16_manifests'] + [a16.block_base('sqrt', 1) + 2])
        with pytest.raises(a16.Finding, match=r'lists 2 seed\(s\) against the 1 its bound sources contribute \(1 extra, 0 missing\)'):
            a16.validate_inventory(inventory_document(extra, sources=sources), registered=registered)
    # A declared count that differs from the source's contribution is a finding.
    fewer = {**sources, 'stage2': [dict(sources['stage2'][0], count=5)]}
    with pytest.raises(a16.Finding, match='declares 5 seeds against the 6 it contributes'):
        a16.validate_inventory(inventory_document(short, sources=fewer), registered=True)
    with pytest.raises(a16.Finding, match='declares 5 seeds against the 6 it contributes'):
        a16.validate_inventory(inventory_document(seeds, sources=fewer), registered=False)
    # An operator category bound to anything but a seed-source record for it is a finding.
    mislabeled = {**sources, 'planning': sources['probe']}
    with pytest.raises(a16.Finding, match='not a sealed seed-source record for it'):
        a16.validate_inventory(inventory_document(dict(seeds, planning=[84737]), sources=mislabeled), registered=False)
    # A changed source file, a wrong record schema and a non-relative path are findings.
    changed = {**sources, 'stage2': [dict(sources['stage2'][0], sha256='0' * 64)]}
    with pytest.raises(a16.Finding, match='missing or changed'):
        a16.validate_inventory(inventory_document(seeds, sources=changed), registered=True)
    swapped = {**sources, 'stage2': [dict(sources['a13_manifest'][0], count=6)]}
    with pytest.raises(a16.Finding, match='not the stage 2 seed registry'):
        a16.validate_inventory(inventory_document(seeds, sources=swapped), registered=True)
    absolute = {**sources, 'probe': [dict(sources['probe'][0], path=str(tmp_path / 'probe.json'))]}
    with pytest.raises(a16.Finding, match='simulation-relative path'):
        a16.validate_inventory(inventory_document(seeds, sources=absolute), registered=False)
    with pytest.raises(a16.Finding, match='unknown category'):
        a16.validate_inventory(a.seal(dict(schema=a16.INVENTORY_SCHEMA, categories={})), registered=False)
    with pytest.raises(a16.Finding, match='not empty but carries'):
        doc = a.unseal(inventory_document(seeds, sources=sources))
        doc['categories']['probe']['empty'] = dict(source_checked='x', reason='y')
        a16.validate_inventory(a.seal(doc), registered=False)
    # Registered mode reconciles to the committed registry and to registered plans.
    a.atomic_json(tmp_path / 'a13_rehearsal.json', a.seal(dict(a13_plan, registered=False)))
    rehearsal_plan = {**sources, 'a13_manifest': [dict(path=relative + '/a13_rehearsal.json', sha256=a.file_hash(tmp_path / 'a13_rehearsal.json'), count=2)]}
    with pytest.raises(a16.Finding, match='non-registered plan'):
        a16.validate_inventory(inventory_document(seeds, sources=rehearsal_plan), registered=True)
    assert a16.validate_inventory(inventory_document(seeds, sources=rehearsal_plan), registered=False)['seeds']['a13_manifest'] == [21, 22]
    # A rehearsal's public record is no recorded manifest for a registered inventory.
    a.atomic_json(tmp_path / 'a16_rehearsal_public.json', a.seal(dict(a16_public, seed_check=dict(non_registered_rehearsal=True))))
    rehearsal_public = {**sources, 'a16_manifests': [dict(path=relative + '/a16_rehearsal_public.json',
                                                           sha256=a.file_hash(tmp_path / 'a16_rehearsal_public.json'), count=1)]}
    with pytest.raises(a16.Finding, match='rehearsal public record'):
        a16.validate_inventory(inventory_document(seeds, sources=rehearsal_public), registered=True)
    assert a16.validate_inventory(inventory_document(seeds, sources=rehearsal_public), registered=False)['recorded_a16_seeds'] == seeds['a16_manifests']
    monkeypatch.setattr(compat, '_committed_bytes', lambda p: b'other bytes')
    with pytest.raises(a16.Finding, match='differs from its committed bytes'):
        a16.validate_inventory(good, registered=True)
    monkeypatch.setattr(compat, '_committed_bytes', lambda p: (_ for _ in ()).throw(subprocess.CalledProcessError(1, 'git')))
    with pytest.raises(a16.Finding, match='not committed'):
        a16.validate_inventory(good, registered=True)
    assert a16.validate_inventory(good, registered=False)['seeds']['stage2'] == seeds['stage2']  # a rehearsal binds without commitment


def test_recorded_exemption_comes_from_verified_sources_only(tmp_path):
    """The reviewer's scenario: an extra listed A16 seed that collides with the
    proposed manifest. The extra is a finding at the inventory, the recorded
    exemption is derived from the verified sources alone, and the collision is
    refused as a collision."""
    source = source_job()
    sqrt1 = a16.seed_manifest('sqrt', 1, [source], 32, [])
    colliding, other = sqrt1[0]['seed'], a16.block_base('crowding', 1) + 7
    a.atomic_json(tmp_path / 'a16_public.json', a.seal(dict(schema=a16.SCHEMA + '-public', seed_manifest=[dict(seed=other)])))
    manifests = [dict(path=(tmp_path / 'a16_public.json').resolve().relative_to(a.SIMULATION).as_posix(),
                      sha256=a.file_hash(tmp_path / 'a16_public.json'), count=1)]
    forged = inventory_document(dict(a16_manifests=[other, colliding], planning=[colliding]), root=tmp_path, sources=dict(a16_manifests=manifests))
    with pytest.raises(a16.Finding, match=r'a16_manifests lists 2 seed\(s\) against the 1 its bound sources contribute \(1 extra'):
        a16.validate_inventory(forged, registered=False)
    honest = inventory_document(dict(a16_manifests=[other], planning=[colliding]), root=tmp_path, sources=dict(a16_manifests=manifests))
    verified = a16.validate_inventory(honest, registered=False)
    assert verified['recorded_a16_seeds'] == [other] and verified['seeds']['planning'] == [colliding]
    forbidden = {s for values in verified['seeds'].values() for s in values}
    with pytest.raises(a16.Finding, match='collision'):
        a16.check_seed_manifest(sqrt1, forbidden, family='sqrt', q=1, recorded=verified['recorded_a16_seeds'])
    # The false exemption the fix removes: a listed value in the recorded set would have hidden it.
    assert a16.check_seed_manifest(sqrt1, forbidden, family='sqrt', q=1, recorded=[other, colliding])['passed']
    # Through preparation: planning seeds equal to the rehearsal manifest's refuse as a collision.
    toy = stage2_toy_original(tmp_path / 'toy', 'sqrt')
    jobs = a.unseal(a.read(toy['source'] / 'tables_A1_manifest.json'))['jobs']
    planning = [a16.rehearsal_seed('sqrt', 1, int(j['seed']), 4) for j in jobs]
    a.atomic_json(toy['seeds'], inventory_document({'probe': [84737], 'planning': planning}, root=tmp_path / 'toy'))
    with pytest.raises(a16.Finding, match='collision'):
        prepare_round(toy, tmp_path / 'toy', 1)
    stem = (tmp_path / 'toy' / 'anchors' / 'sqrt.json').resolve()
    assert a.unseal(a.read(a16.family_record_path(stem)))['terminal'] is not None


def test_a16_rehearsal_outputs_stay_under_their_declared_root(tmp_path, monkeypatch):
    """A rehearsal's plan, public record and anchors lie under the declared
    rehearsal output root, outside the registered trees and never on an
    anchor, checked before any filesystem write; a registered preparation's
    plan path is never an anchor."""
    import shutil
    import tempfile
    toy = stage2_toy_original(tmp_path, 'sqrt')
    _, history = build_history(toy, tmp_path, 1)
    crowding = a16.family_record_path(a.SIMULATION / a16.TARGETS['crowding'])
    real_open = Path.open

    def guarded_open(self, mode='r', *args, **kwargs):
        if any(flag in mode for flag in 'wax+'):
            pytest.fail('filesystem write before the output check: ' + str(self))
        return real_open(self, mode, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', guarded_open)
    real_os_open = os.open

    def guarded_os_open(path, flags, *args, **kwargs):
        if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC):
            pytest.fail('filesystem write before the output check: ' + str(path))
        return real_os_open(path, flags, *args, **kwargs)
    monkeypatch.setattr(os, 'open', guarded_os_open)
    for target, name in ((os, 'replace'), (os, 'fdopen'), (os, 'mkdir'), (os, 'makedirs'), (tempfile, 'mkstemp'), (shutil, 'copyfileobj'),
                         (Path, 'mkdir'), (Path, 'chmod'), (Path, 'write_bytes'), (Path, 'write_text'), (Path, 'touch')):
        monkeypatch.setattr(target, name, lambda *args, **kw: pytest.fail('filesystem write before the output check'))
    anchor = tmp_path / 'anchors' / 'sqrt.json'
    cases = [dict(output=crowding, rehearsal_anchor=anchor, rehearsal_root=tmp_path, match='on a registered tree or anchor'),
             dict(output=a.ROOT / 'runs' / 'registered' / 'plan.json', rehearsal_anchor=anchor, rehearsal_root=tmp_path, match='on a registered tree or anchor'),
             dict(output=tmp_path / 'plan.json', rehearsal_anchor=anchor, rehearsal_root=a.ROOT / 'runs' / 'a10_stage2' / 'root', match='inside the registered tree'),
             dict(output=tmp_path.parent / 'outside_plan.json', rehearsal_anchor=anchor, rehearsal_root=tmp_path, match='outside its declared root'),
             dict(output=tmp_path / 'plan.json', rehearsal_anchor=tmp_path.parent / 'elsewhere' / 'sqrt.json', rehearsal_root=tmp_path, match='outside its declared root'),
             dict(output=tmp_path / 'plan.json', rehearsal_anchor=anchor, rehearsal_root=None, match='explicit rehearsal output root')]
    for case in cases:
        match = case.pop('match')
        with pytest.raises(ValueError, match=match):
            a16.prepare(history, toy['projection'], toy['seeds'], case['output'], round=1, rehearsal=True, draws=10,
                        rehearsal_anchor=case['rehearsal_anchor'], rehearsal_root=case['rehearsal_root'])
    # The reviewer's round 3 scenario: the history view root (and so every
    # history copy) must lie under the rehearsal root. Here the inventory's view
    # root is tmp/copies_r1 while the declared rehearsal root is tmp/sub.
    sub = tmp_path / 'sub'
    payload = a.unseal(a.read(history))
    assert Path(payload['view_root']) == (tmp_path / 'copies_r1').resolve()
    with pytest.raises(ValueError, match='history view root outside its declared rehearsal root'):
        a16.prepare(history, toy['projection'], toy['seeds'], sub / 'plan.json', round=1, rehearsal=True, draws=10,
                    rehearsal_anchor=sub / 'anchors' / 'sqrt.json', rehearsal_root=sub)
    # A copy destination outside the root, with the view root inside it, refuses too.
    forged = deepcopy(payload)
    forged['view_root'] = str(sub)
    forged['files'][0]['copy'] = str(tmp_path / 'elsewhere' / 'copy.json')
    forged_path = tmp_path / 'history_forged.json'
    monkeypatch.undo()  # the forged inventory is written outside the interception window
    a.atomic_json(forged_path, a.seal(forged))
    monkeypatch.setattr(Path, 'open', guarded_open)
    monkeypatch.setattr(os, 'open', guarded_os_open)
    for target, name in ((os, 'replace'), (os, 'fdopen'), (os, 'mkdir'), (os, 'makedirs'), (tempfile, 'mkstemp'), (shutil, 'copyfileobj'),
                         (Path, 'mkdir'), (Path, 'chmod'), (Path, 'write_bytes'), (Path, 'write_text'), (Path, 'touch')):
        monkeypatch.setattr(target, name, lambda *args, **kw: pytest.fail('filesystem write before the output check'))
    with pytest.raises(ValueError, match='history copy destination outside its declared rehearsal root'):
        a16.prepare(forged_path, toy['projection'], toy['seeds'], sub / 'plan.json', round=1, rehearsal=True, draws=10,
                    rehearsal_anchor=sub / 'anchors' / 'sqrt.json', rehearsal_root=sub)
    assert not sub.exists()
    # A registered preparation's history view is unaffected: outside the
    # registered trees is all preparation_outputs asks (stage_history keeps its own check).
    registered_stem = a16.anchor_stem('sqrt', registered=True)
    assert a16.preparation_outputs(a.ROOT / 'runs' / 'a10_stage2' / 'sqrt' / 'a16_round1_plan.json', registered_stem, family='sqrt',
                                   registered=True, rehearsal_root=None, history=payload)[1] is None
    with pytest.raises(ValueError, match='registered plan path is an anchor'):
        a16.prepare(history, toy['projection'], toy['seeds'], a16.family_record_path(a.SIMULATION / a16.TARGETS['sqrt']), round=1,
                    registration={'commit': A17_COMMIT}, non_launch_reserve_x2_hours=6., incurred_x2_hours=0.)
    with pytest.raises(ValueError, match='declares no rehearsal output root'):
        a16.prepare(history, toy['projection'], toy['seeds'], tmp_path / 'registered.json', round=1,
                    registration={'commit': A17_COMMIT}, non_launch_reserve_x2_hours=6., incurred_x2_hours=0., rehearsal_root=tmp_path)
    # A registered plan path in its own family's directory is accepted (no write
    # happens here); another family's directory, a publication sibling and the
    # nominal directory are refused.
    registered_stem = a16.anchor_stem('sqrt', registered=True)
    assert a16.preparation_outputs(a.ROOT / 'runs' / 'a10_stage2' / 'sqrt' / 'a16_round1_plan.json', registered_stem, family='sqrt',
                                   registered=True, rehearsal_root=None)[1] is None
    for bad in (a.ROOT / 'runs' / 'a10_stage2' / 'crowding' / 'plan.json', (a.SIMULATION / a16.TARGETS['sqrt']).with_suffix('.compatibility.json'),
                (a.SIMULATION / a16.TARGETS['crowding']).with_suffix('.a10_receipt.json'), a.ROOT / 'runs' / 'a10_stage1' / 'nominal' / 'plan.json'):
        with pytest.raises(ValueError, match="anchor, a publication sibling or another family's registered directory"):
            a16.preparation_outputs(bad, registered_stem, family='sqrt', registered=True, rehearsal_root=None)
    assert not crowding.exists() and not (tmp_path / 'anchors').exists()
    monkeypatch.undo()
    # A rehearsal whose view root lies under its rehearsal root still prepares.
    plan, plan_path = prepare_round(toy, tmp_path, 1)
    assert plan['rehearsal_root'] == str(tmp_path.resolve()) and Path(plan['anchor_stem']).is_relative_to(tmp_path.resolve())
    assert Path(a.unseal(plan['history'])['view_root']).is_relative_to(tmp_path.resolve())
    assert plan_path.is_relative_to(tmp_path) and a16.preparation_outputs(plan_path, plan['anchor_stem'], family='sqrt', registered=False,
                                                                           rehearsal_root=tmp_path, history=payload)[1] == tmp_path.resolve()


def test_loader_refuses_hypothetical_admission_provenance_in_both_modes(tmp_path):
    path = tmp_path / 'family.json'
    document = synthetic_a10_family(path, 'sqrt')
    payload = deepcopy(document['payload'])
    admission = dict(schema=admit.SCHEMA, scope=a16.SCOPES[1], primary_rows=len(payload['rows']), rows={},
                     a16=dict(family='sqrt', round=1, hypothetical=True), admitted_set_sha256=a.digest({}))

    def write(value):
        payload['manifest']['a13_admission'] = value
        payload['manifest_hash'] = a.digest(payload['manifest'])
        a.atomic_json(path, a.seal(payload))
    write(admission)
    for kwargs in ({}, dict(registered=True)):
        with pytest.raises(ValueError, match='never loadable'):
            ProductionTables(path, calibration_hash='c', **kwargs)
    write(dict(admission, a16=dict(admission['a16'], hypothetical=False)))
    with pytest.raises(ValueError, match='never loadable'):
        ProductionTables(path, calibration_hash='c')
    # A bound provenance loads in the default mode and passes the registered verification.
    write(dict(admission, a16=dict(family='sqrt', round=1, plan_hash='a' * 64, family_record_sha256='b' * 64,
                                   round_record_sha256='c' * 64, admission_record_sha256='d' * 64)))
    assert ProductionTables(path, calibration_hash='c').payload['manifest']['a13_admission']['a16']['plan_hash'] == 'a' * 64
    assert ProductionTables(path, calibration_hash='c', registered=True).rows
    # A document without an A16 field is untouched by the check.
    write(dict(schema=admit.SCHEMA, scope='validation_launched_under_A13', primary_rows=len(payload['rows']), rows={}, admitted_set_sha256=a.digest({})))
    assert ProductionTables(path, calibration_hash='c', registered=True).rows


def _variant_calibration(tmp_path, monkeypatch, variant='sigma_squared_x10', factor=10.):
    """A synthetic A6 variant calibration of the frozen nominal parent whose
    validation runs calibration._validate_a10_variant in full, with the pinned
    A6 record redirected to this document's identities."""
    from v3 import instrument
    from v3.instrument import CALIBRATION_SHA256
    parent_doc = a.read(a.SIMULATION / CAL_PATH)
    parent = a.unseal(parent_doc)
    assert parent_doc['sha256'] == CALIBRATION_SHA256
    constants = instrument.validate_constants()
    record = constants['a6_calibrations']
    blocks = [[row[0] * 1.5] + row[1:] for row in parent['block_lower_levels']]
    level = min(row[0] for row in blocks if row[0] > 0)
    payload = dict(parent, code_hash='variant-producer-fixture', a6_variant=variant, a6_sigma_factor=factor, a6_parent_sha256=CALIBRATION_SHA256,
                   a6_note=record['variant_note'], block_lower_levels=blocks,
                   reliable_positive_lower_levels=[level] + parent['reliable_positive_lower_levels'][1:],
                   values=dict(parent['values'], sigma_squared=parent['values']['sigma_squared'] * factor, epsilon_n=.01 * level))
    document = a.seal(payload)
    path = tmp_path / 'variant_calibration.json'
    a.atomic_json(path, document)
    approved = dict(byte_sha256=a.file_hash(path), payload_sha256=document['sha256'], producer_code_hash='variant-producer-fixture', sigma_factor=factor)
    patched = deepcopy(constants)
    patched['a6_calibrations']['variants'][variant] = approved
    monkeypatch.setattr(instrument, 'validate_constants', lambda document=None: deepcopy(patched))
    return path.relative_to(a.SIMULATION).as_posix(), document


def test_a16_sigma_worker_closure_carries_the_nominal_calibration_parent(tmp_path, monkeypatch):
    """A sigma family whose source ran on a variant calibration: the worker's
    isolated view holds only the inventoried copies, the variant's validation
    reads the nominal parent through that view, and the same view without the
    parent fails closed (calibration._validate_a10_variant reads the parent)."""
    from v3 import calibration as cal, snapshot_a11
    from v3.context import Context
    from v3.production_runner import execute
    cal_path, variant = _variant_calibration(tmp_path, monkeypatch)
    # The synthetic variant passes the real variant validation.
    cal.validate_calibration(variant, registered=False, instrument=tables.family_instrument('sigma_squared_x10').declaration())
    toy = stage2_toy_original(tmp_path, 'sigma_squared_x10', cal_path=cal_path)
    plan, plan_path = prepare_round(toy, tmp_path, 1)
    parent = (a.SIMULATION / a16.NOMINAL_CALIBRATION).resolve()
    job = plan['jobs'][0]
    inputs = {Path(r['source']).resolve(): r for r in job['config']['a16_inputs']}
    assert parent in inputs and (a.SIMULATION / cal_path).resolve() in inputs
    assert a.file_hash(inputs[parent]['copy']) == inputs[parent]['sha256'] == a.file_hash(parent)
    assert str(parent) in inputs[parent]['aliases'] + [inputs[parent]['source']]
    assert len(inputs) == 4  # the A1 output and record, the variant and its parent
    # snapshot_a11.dependencies enumerates the parent copy.
    dependencies = snapshot_a11.dependencies([job], tmp_path / 'root' / a16.PHASES[1])
    assert Path(inputs[parent]['copy']).resolve() in dependencies
    # The worker in an isolated view: the stage performs exactly the calibration
    # reads of the real stage (the A1 config's calibration and, through
    # Context.build, the variant validation's parent read) without simulating.
    reads = []
    real_input_path = a.input_path

    def recording_input_path(path):
        reads.append(str(Path(path).resolve()))
        return real_input_path(path)
    monkeypatch.setattr(a, 'input_path', recording_input_path)
    monkeypatch.setattr(a16, 'extension_stage', lambda source, fit, rows, seed, override: (
        Context.build(source['result']['kernel'], a.read(a.SIMULATION / Path(source['job']['config']['calibration_path']))),
        dict(count=6, settings=toy['settings'], rows={k: [[0., 1]] * 6 for k in rows}))[1])
    # The isolated view holds only the inventoried copies; every other path
    # under the registered calibration directory or this fixture is protected.
    closure = {str(Path(r['copy']).resolve()) for r in job['config']['a16_inputs']}
    isolated = dict(paths={c: c for c in closure}, protected=[str(a.ROOT / 'runs' / 'registered'), str(tmp_path.resolve())])
    root = tmp_path / 'root' / a16.PHASES[1]
    with a.input_view(isolated):
        result = execute(job, root=root)
    assert result['stopped_on_visits'] and result['a16_family'] == 'sigma_squared_x10'
    protected = [p for p in reads if any(Path(p).is_relative_to(Path(t)) for t in isolated['protected'])]
    outside = {p for p in protected if p not in closure and not Path(p).is_relative_to(root.resolve())}
    assert str(parent) in protected and str((a.SIMULATION / cal_path).resolve()) in protected
    assert outside <= {str(Path(r['source']).resolve()) for r in job['config']['a16_inputs']}  # declared sources, mapped to copies
    # The same view without the parent fails closed at the parent read.
    without = a.stable_job(job['kind'], dict(job['config'], a16_inputs=[r for r in job['config']['a16_inputs']
                                                                         if Path(r['source']).resolve() != parent]), 'v3_tables', 0)
    with a.input_view(isolated):
        with pytest.raises(ValueError, match='not in the verified snapshot.*v3_rerun_calibration'):
            execute(without, root=tmp_path / 'without' / a16.PHASES[1])
    # A sqrt round carries no parent; the inventory builder adds it for the sigma families only.
    sqrt = stage2_toy_original(tmp_path / 'sqrt', 'sqrt')
    sqrt_plan, _ = prepare_round(sqrt, tmp_path / 'sqrt', 1)
    assert len(sqrt_plan['jobs'][0]['config']['a16_inputs']) == 3


def test_stage2_family_plans_publish_only_to_their_fixed_paths(tmp_path, monkeypatch):
    from v3 import table_validation_a4 as a4
    # Historical plan shapes (nominal, stage 1) carry neither field and never enter the check.
    for plan in ({}, dict(calibration_path=CAL_PATH), dict(instrument=A10, registered=True, calibration_path=CAL_PATH)):
        assert a4.stage2_publication_guard(plan, tmp_path / 'anywhere.json') is None
        assert a4.stage2_publication_guard(plan, tmp_path / 'anywhere.json', 'nominal') is None
        # The hash-bound source family enters the check: a stage 2 source with the
        # plan fields stripped cannot bypass it.
        with pytest.raises(ValueError, match='requires a plan naming that family and stage 2'):
            a4.stage2_publication_guard(plan, a.SIMULATION / tables.STAGE2_PATHS['sqrt'][1], 'sqrt')
    with pytest.raises(ValueError, match='requires a plan naming that family and stage 2'):
        a4.stage2_publication_guard(dict(a10_stage=2, a10_family='sqrt', calibration_path=CAL_PATH), a.SIMULATION / tables.STAGE2_PATHS['sqrt'][1], 'crowding')
    with pytest.raises(ValueError, match='names no stage 2 family and stage'):
        a4.stage2_publication_guard(dict(a10_stage=2), a.SIMULATION / tables.STAGE2_PATHS['sqrt'][1])
    with pytest.raises(ValueError, match='names no stage 2 family and stage'):
        a4.stage2_publication_guard(dict(a10_family='sqrt'), a.SIMULATION / tables.STAGE2_PATHS['sqrt'][1])
    for family in tables.STAGE2_FAMILIES:
        calibration_path, tables_path = tables.STAGE2_PATHS[family]
        plan = dict(a10_stage=2, a10_family=family, calibration_path=calibration_path)
        assert a4.stage2_publication_guard(plan, a.SIMULATION / tables_path) == family
        with pytest.raises(ValueError, match='target differs from the family-path clause'):
            a4.stage2_publication_guard(plan, tmp_path / 'elsewhere.json')
        with pytest.raises(ValueError, match='target differs from the family-path clause'):
            a4.stage2_publication_guard(plan, a.SIMULATION / tables.STAGE2_PATHS['nominal'][1])
        with pytest.raises(ValueError, match='calibration string differs'):
            a4.stage2_publication_guard(dict(plan, calibration_path='v3/elsewhere/calibration.json'), a.SIMULATION / tables_path)
    # End to end: a registered stage 2 family plan publishing elsewhere is
    # refused before any write; the same plan as a fixture publishes.
    toy = stage2_toy_original(tmp_path, 'crowding')
    plan = deepcopy(toy['plan'])
    plan['registration'] = {'commit': A17_COMMIT}
    for suffix in ('.json', '.cell_results.json', '.compatibility.json'):
        toy['candidate'].with_suffix(suffix).unlink()
    (toy['run'] / 'a13_admission_check.json').unlink()
    before = {str(p) for p in tmp_path.rglob('*')}
    with pytest.raises(ValueError, match='target differs from the family-path clause'):
        a4.publish(plan, toy['run'], toy['source'], toy['calibration'], tmp_path / 'elsewhere.json', registered=True)
    assert {str(p) for p in tmp_path.rglob('*')} == before
    with pytest.raises(ValueError, match='target differs from the family-path clause'):
        a4.publish(plan, toy['run'], toy['source'], toy['calibration'], a.SIMULATION / tables.STAGE2_PATHS['sqrt'][1], registered=True)
    assert not (a.SIMULATION / tables.STAGE2_PATHS['sqrt'][1]).exists()
    # Stripping the plan fields (outside the plan hash) does not bypass the clause:
    # the verified source family names crowding, so the fieldless plan is refused.
    stripped = {k: v for k, v in plan.items() if k not in ('a10_family', 'a10_stage')}
    assert a4._recompute_plan_hash(stripped) == a4._recompute_plan_hash(plan)  # the fields are outside the plan hash
    # The toy source is a subset, so the registered source check and the
    # settings-override guard are stood in for; the verified family is crowding.
    monkeypatch.setattr(tables, 'verify_estimation_source', lambda *args, **kw: {'family': 'crowding'})
    monkeypatch.setattr(a4, 'registered_publish_guard', lambda p: None)
    with pytest.raises(ValueError, match='requires a plan naming that family and stage 2'):
        a4.publish(stripped, toy['run'], toy['source'], toy['calibration'], tmp_path / 'elsewhere.json', registered=True)
    assert {str(p) for p in tmp_path.rglob('*')} == before
    monkeypatch.undo()
    a4.publish(toy['plan'], toy['run'], toy['source'], toy['calibration'], tmp_path / 'fixture_family.json', registered=False)
    assert toy['candidate'].exists()


def test_registered_forecast_and_preparation_fix_the_draw_count(tmp_path, monkeypatch):
    toy = stage2_toy_original(tmp_path, 'sqrt')
    document, _ = build_history(toy, tmp_path, 1)
    verified = h16.verify_history(document, round=1, registered=False)
    eligible = sorted(verified['selected'])
    rehearsal = f16.forecast(verified, 32, family='sqrt', round=1, eligible=eligible, draws=30)
    assert rehearsal['draws'] == 30 and rehearsal['registered'] is False
    with pytest.raises(ValueError, match='exactly 4000 draws'):
        f16.forecast(verified, 32, family='sqrt', round=1, eligible=eligible, draws=30, registered=True)
    with pytest.raises(ValueError, match='exactly 4000 draws'):
        f16.forecast(verified, 32, family='sqrt', round=1, eligible=eligible, draws=4001, registered=True)
    monkeypatch.setattr(f16, '_scenario', lambda *args, **kw: .5)
    registered = f16.forecast(verified, 32, family='sqrt', round=1, eligible=eligible, draws=4000, registered=True)
    assert registered['draws'] == f16.DRAWS == 4000 and registered['registered'] is True
    assert f16.forecast(verified, 32, family='sqrt', round=1, eligible=eligible, registered=True)['draws'] == 4000
    monkeypatch.undo()
    # Registered preparation refuses another count before it touches any anchor.
    history = tmp_path / 'history_r1.json'
    with pytest.raises(ValueError, match='exactly 4000 forecast draws'):
        a16.prepare(history, toy['projection'], toy['seeds'], tmp_path / 'registered_plan.json', round=1, registration={'commit': A17_COMMIT},
                    non_launch_reserve_x2_hours=6., incurred_x2_hours=0., draws=30)
    assert not a16.family_record_path(a16.anchor_stem('sqrt', registered=True)).exists()
    # A rehearsal plan records its count as a non-registered forecast.
    plan, _ = prepare_round(toy, tmp_path, 1, draws=25)
    assert plan['forecast']['draws'] == 25 and plan['forecast']['registered'] is False and plan['non_registered_rehearsal']
    assert a.unseal(a.read(tmp_path / 'plan_r1.public.json'))['forecast']['registered'] is False


def test_registered_preparation_requires_explicit_reserve_and_incurred_arguments(tmp_path):
    toy = stage2_toy_original(tmp_path, 'sqrt')
    _, history = build_history(toy, tmp_path, 1)
    registered_anchor = a16.family_record_path(a16.anchor_stem('sqrt', registered=True))
    for kwargs in ({}, dict(non_launch_reserve_x2_hours=6.), dict(incurred_x2_hours=0.)):
        with pytest.raises(ValueError, match='explicitly'):
            a16.prepare(history, toy['projection'], toy['seeds'], tmp_path / 'registered_plan.json', round=1,
                        registration={'commit': A17_COMMIT}, **kwargs)
        assert not registered_anchor.exists() and not (tmp_path / 'registered_plan.json').exists()
    # A rehearsal defaults both and records them in the plan and the public record.
    plan, plan_path = prepare_round(toy, tmp_path, 1)
    public = a.unseal(a.read(plan_path.with_suffix('.public.json')))
    assert (plan['non_launch_reserve_x2_hours'], plan['incurred_x2_hours']) == (6., 0.) == (public['non_launch_reserve_x2_hours'], public['incurred_x2_hours'])
    import inspect
    signature = inspect.signature(a16.prepare)
    assert signature.parameters['non_launch_reserve_x2_hours'].default is None and signature.parameters['incurred_x2_hours'].default is None
    assert signature.parameters['draws'].default is None


def test_launch_time_qualification_covers_every_kind_the_spec_runs(tmp_path, monkeypatch):
    from v3 import production_runner as pr, qualification_a11 as q
    code = a.code_identity()
    evidence = _pooled_evidence(code, ('fixture', 'table'), 20)
    assert q.validate_evidence(evidence, code, kinds=['fixture'])['passed']
    assert q.validate_evidence(evidence, code, kinds=['fixture', 'table'])['passed']
    with pytest.raises(ValueError, match='kind.s. the candidate will run: a16_validate_plain_r1'):
        q.validate_evidence(evidence, code, kinds=['fixture', 'a16_validate_plain_r1'])
    assert q.validate_evidence(evidence, code)['passed']  # the other call sites are unchanged
    path = tmp_path / 'qualification.json'
    a.atomic_json(path, evidence)
    hosts = tmp_path / 'hosts.json'
    a.atomic_json(hosts, {'alpha': dict(qualification=str(path), settings=dict(workers=4, threads=1))})
    monkeypatch.setattr(q, 'scheduling_rate', lambda e: 1.)
    covered = dict(jobs=[a.stable_job('fixture', {'seconds': .01}, 'validation', 0), a.stable_job('table', {'phase': 'table'}, 'v3_tables', 0)])
    assert pr.qualified_hosts(hosts, covered, {})['alpha']['kinds'] == ['fixture', 'table']
    uncovered = dict(jobs=covered['jobs'] + [a16_job(1)])
    with pytest.raises(ValueError, match='a16_validate_plain_r1'):
        pr.qualified_hosts(hosts, uncovered, {})
    import inspect
    assert 'qualified_hosts(args.hosts, spec, peaks)' in inspect.getsource(pr.main)


# ---------------------------------------------------------------------------
# Equivalence and unchanged modules
# ---------------------------------------------------------------------------

def test_a13_a14_and_numerical_modules_unchanged_since_the_a17_commit():
    for name in ('validation_extension_a13.py', 'validation_extension_a14.py', 'history_a14.py', 'forecast_a14.py',
                 'replay_a14.py', 'continuation_validation.py', 'offline_estimator.py', 'integration.py', 'engine.py',
                 'context.py', 'cohort.py', 'calibration.py', 'instrument.py', 'study.py', 'tables_a6.py', 'budget_a6.py'):
        before = subprocess.check_output(['git', 'show', '74460801:simulation/v3/' + name])
        assert before.replace(b'\r\n', b'\n') == (a.ROOT / name).read_bytes().replace(b'\r\n', b'\n'), name


def test_run_result_and_unadmitted_loader_equivalence_at_the_phase1_identity(tmp_path):
    """Sampled run jobs at the phase 1 identity (the committed tree at 74460801)
    and at this tree agree byte for byte on every existing result field, and the
    loader behaves identically on a family with no admitted rows."""
    repo = a.SIMULATION.parent
    names = subprocess.run(['git', '-C', str(repo), 'ls-tree', '-r', '--name-only', '74460801', 'simulation'],
                           check=True, capture_output=True, text=True).stdout.splitlines()
    names = [n for n in names if (n.endswith('.py') and not Path(n).name.startswith('test_')
             and len(Path(n).parts) == (3 if n.startswith('simulation/v3/') else 2))
             or n in ('simulation/v3/a10_constants.json', 'simulation/v3/calibration_compatibility_A1.json',
                      'simulation/v3/table_compatibility_A2.json', 'simulation/v3/table_compatibility_A3.json')]
    source = tmp_path / 'phase1_source'
    for name in names:
        data = subprocess.run(['git', '-C', str(repo), 'show', '74460801:' + name], check=True, capture_output=True).stdout
        target = source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    script = r'''
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
sys.path.append(sys.argv[2])
from v3 import artifacts as a, recording, production_runner as runner, calibration
from v3.instrument import EPSILON_L
from v3.tables_a10 import NOMINAL
from v3.policies import execution_policy_class
from test_v3_unpublished_bins import sparse_tables
validate = calibration.validate_calibration
def fixture_calibration(doc, **kw):
    payload = a.unseal(doc)
    validate(a.seal(dict(payload, code_hash=a.code_identity())), registered=False)
    return payload
calibration.validate_calibration = fixture_calibration
cal = a.seal(dict(schema='v3-calibration-1', fixture=True, code_hash='equivalence-fixture',
    values=dict(center=[0.]*10, sigma_squared=.02, n_ref=200., epsilon_n=1e-6,
                epsilon_e=1e-6, epsilon_l=EPSILON_L, c_e=2.5)))
real_model = recording.RecordedV3Model
if sys.argv[4] != 'current':
    assert a.code_identity() == sys.argv[4]
results = []
for index, (seed, reviews, missing) in enumerate(((200,False,()),(201,True,()),(202,True,(1,)))):
    model = sparse_tables(real_model(seed, rules=execution_policy_class()[:3], calibration=cal,
        instrument=NOMINAL.declaration(), rollout_steps=1, successor_capability=None),
        a.ROOT / '_pytest_v3' / ('equivalence_' + sys.argv[3]) / str(index), missing_rows=missing)
    availability = model.evaluate().available.tolist()
    if reviews: model.successor_capability = 1.5
    recording.RecordedV3Model = lambda **kwargs: model
    result = runner.execute(a.stable_job('rerun', {'steps': 3}, 'validation', index))
    results.append(dict(result=result, available=availability, fixture=model.tables.fixture, enabled=getattr(model, '_a13_enabled', None)))
print(a.canonical(results).decode())
'''
    outputs = [subprocess.check_output([sys.executable, '-B', '-c', script, str(root), str(a.SIMULATION), tmp_path.name + str(i), expected])
               for i, (root, expected) in enumerate(((source / 'simulation', '57141a5731dfe3dbf334e4c9374559afe873c12e5c6c354b5869e0ffbdff777e'),
                                                     (a.SIMULATION, 'current')))]
    assert outputs[0] == outputs[1]
    import json
    for record in json.loads(outputs[1]):
        assert record['enabled'] is False and 'a13_decision_incidence' not in record['result']
