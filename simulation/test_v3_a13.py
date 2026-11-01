"""A13 mechanics on synthetic records only. No registered outcomes are read."""
from copy import deepcopy
from types import SimpleNamespace
import hashlib
import math
import subprocess

import numpy as np
import pytest
from test_v3_paths import tmp_path
from v3 import artifacts as a
from v3 import validation_extension_a13 as ext
from v3 import admission_a13 as admit
from v3 import continuation_validation as cv
from v3.production_tables import ProductionTables, row_key
from v3.policies import execution_policy_class
from v3.host_a11 import Loopback as _Loopback


def row_fixture(rule=None, context=0):
    rule = rule or execution_policy_class()[1]
    row = {'rule_id': rule.rule_id, 'rule_hash': a.digest(rule.__dict__), 'kernel_hash': str(context),
           'calibration_hash': 'toy', 'scoring': {'alpha': 1., 'capability': 1., 'kappa': 8.},
           'initial_population': 200, 'route': 'plain', 'status': 'not_estimable',
           'reason': 'A4 availability floor failed', 'primary_status': 'not_estimable',
           'primary_reason': 'A4 availability floor failed', 'flow_range': 10., 'lambda_f': {'mean': 0.},
           'lambda_b': None, 'LS': None, 'c0': None,
           'continuation': {'entries': [{'bin': [1, 0, 0, 0, 0, 0], 'value': -10., 'error': 10.}],
                            'heldout_coverage': 1., 'training_fixed_point_converged': True},
           'screens': {'route_applicable': True, 'flow_half_width': True, 'half_window_drift': True},
           'sensitivity': {'selected': False, 'passed': None, 'contrasts': []},
           'a4': {'base_screens_ok': True, 'validated_support_size': 1, 'tau': .5,
                  'floor': {'passed': False, 'assessed': True, 'living_ok': True, 'low_assessed': True,
                            'low_ok': False, 'living_fraction': .01, 'low_fraction': 1.},
                  'census': {'fraction_among_living_endpoints': .01, 'fraction_among_low_population_living_endpoints': 1.}}}
    detail = {'row': row_key(row), 'setting': 'primary', 'route': 'plain', 'status': 'not_estimable',
              'floor': {}, 'cell_tests': [{'cell': cv.POP0_CELL, 'eb': 'unresolved', 'visit_weighted_ok': True},
                                         {'cell': 1, 'eb': 'certified', 'visit_weighted_ok': True}]}
    fit = {'c0': {'value': -10., 'published': True}}
    return row, detail, fit


@pytest.mark.parametrize('n', [0, 1, 2])
def test_eligibility_small_counts_and_none_sensitivity(n):
    row, detail, fit = row_fixture()
    if n == 0:
        detail['cell_tests'] = detail['cell_tests'][1:]
    ok, params = ext.eligible(row, detail, row, fit, {cv.POP0_CELL: {'n_traj': n}}, 20, -10., 0.)
    assert ok and params['n_star'] == 1 + math.ceil(14 * params['width'] * math.log(4 * 20 / .05) / (3 * .5))
    assert cv.empirical_bernstein(0., 0., params['n_star'], params['width'], 20, .5)['rho'] <= .25
    assert 7 * params['width'] * math.log(4 * 20 / .05) / (3 * (params['n_star'] - 2)) > .25


@pytest.mark.parametrize('change', ['route', 'status', 'reason', 'base', 'support', 'sensitivity', 'living', 'low_assessed',
                                    'low_ok', 'classification', 'violation', 'fit', 'arithmetic', 'sibling'])
def test_every_eligibility_boundary(change):
    row, detail, fit = row_fixture()
    count, primary = 1, True
    if change == 'route': row['route'] = 'fv'
    if change == 'status': row['status'] = 'estimated'
    if change == 'reason': row['reason'] = 'another failure'
    if change == 'base': row['screens']['flow_half_width'] = False
    if change == 'support': row['a4']['validated_support_size'] = 0
    if change == 'sensitivity': row['sensitivity']['passed'] = False
    if change == 'living': row['a4']['floor']['living_ok'] = False
    if change == 'low_assessed': row['a4']['floor']['low_assessed'] = False
    if change == 'low_ok': row['a4']['floor']['low_ok'] = True
    if change == 'classification': detail['cell_tests'][0]['eb'] = 'certified'
    if change == 'violation': detail['cell_tests'][1]['eb'] = 'violation'
    if change == 'fit': fit['c0']['published'] = False
    if change == 'arithmetic': count = 10**8
    if change == 'sibling': primary = False
    assert ext.eligible(row, detail, row, fit, {cv.POP0_CELL: {'n_traj': count}}, 20, -10., 0., primary=primary) == (False, None)


def source_job(index=0):
    return a.stable_job('table', {'a10_family': 'nominal', 'kernel': {'capability': 1.}, 'setting_name': 'primary'}, 'v3_tables', index)


@pytest.mark.parametrize('price,expected', [(.1, 16), (1., 15), (2.5, 6), (3., 5), (16., 0)])
def test_pricing_exact_cap_floor_and_projection_binding(price, expected):
    doc = a.seal({'per_phase_capability': {'nominal.1.0.primary.validate_plain': {'x2_hours_max': price * 3 * 10, 'jobs': 10}}})
    plan = {'pull_dispatch': {'projection_sha256': doc['sha256']}}
    result = ext.price_extension(plan, doc, [source_job()], registered=False)
    assert result['R_max'] == expected and result['projected_x2_hours'] == pytest.approx(expected * price)
    assert result['projected_x2_hours'] <= 15
    with pytest.raises(ValueError, match='payload seal'):
        ext.price_extension({'pull_dispatch': {'projection_sha256': 'wrong'}}, doc, [], registered=False)
    with pytest.raises(ValueError, match='identity'):
        ext.price_extension(plan, doc, [], registered=True, projection_file_hash='wrong')
    with pytest.raises(ValueError, match='duplicate'):
        ext.price_extension(plan, doc, [source_job(), source_job()], registered=False)


def test_seed_range_tag_delimiter_global_collisions(monkeypatch):
    jobs = [source_job(i) for i in range(3)]
    manifest = ext.seed_manifest(jobs, 16, [1, 2, 3])
    assert len(manifest) == 48 and len({r['seed'] for r in manifest}) == 48
    assert all(ext.RESERVED[0] <= r['seed'] < ext.RESERVED[1] for r in manifest)
    assert ext.ext_seed(12, 34) != ext.ext_seed(123, 4)
    assert ext.ext_seed(12, 4) == (1 << 60) + cv._truncated_sha('v3_R_validate_ext', 12, '/', 4)
    with pytest.raises(cv.SeedCollision): ext.seed_manifest(jobs, 16, [manifest[0]['seed']])
    monkeypatch.setattr(cv, '_truncated_sha', lambda *args: 5)
    with pytest.raises(cv.SeedCollision): ext.seed_manifest(jobs, 16, [])


def parameters(n=20):
    return dict(n_star=n, width=.01, tau=.5, M=20, alpha=.05, lower=-10., upper=0., row_index=0)


def test_extension_uses_first_visitors_only_and_safeguard():
    p = parameters()
    records = [{'replicate': 4, 'trajectories': [[0., 0]] + [[0., 1]] * 20 + [[10000., 1]]}]
    test = ext.extension_test(records, p)
    assert test['status'] == 'certified' and test['visit_weighted_ok'] and test['n'] == 20
    assert ext.extension_test([{'replicate': 4, 'trajectories': [[0., 0]] * 100}], p)['reason'] == 'N* not reached'
    with pytest.raises(ValueError, match='order'):
        ext.extension_test([{'replicate': 5, 'trajectories': []}], p)
    weighted = [[.4 * 1000, 1000]] + [[-.4, 1]] * 19
    test = ext.extension_test([{'replicate': 4, 'trajectories': weighted}], dict(p, tau=.38))
    assert not test['visit_weighted_ok']
    test = ext.extension_test([{'replicate': 4, 'trajectories': [[20., 1]] * 20}], p)
    assert test['status'] == 'violation'


def test_stop_counts_only_all_rows_and_batch_order():
    rows = {'fast': parameters(1), 'slow': parameters(3)}
    first = dict(replicate=4, rows={'fast': [[999., 1]] * 4, 'slow': [[0., 1]] + [[0., 0]] * 3})
    second = dict(replicate=5, rows={'fast': [[0., 0]] * 4, 'slow': [[999., 1]] * 4})
    assert not ext.stop_reached([first], rows)
    assert ext.stop_reached([first, second], rows)
    first['rows']['fast'][0][0] = -100000.
    assert ext.stop_reached([first, second], rows)


def test_reassembly_only_eligible_c0_and_ineligible_bytes():
    row, detail, fit = row_fixture()
    other, other_detail, _ = row_fixture(context=1)
    key, other_key = row_key(row), row_key(other)
    rows = {key: row, other_key: other}
    sibling = dict(deepcopy(detail), setting='double_length')
    details = [detail, sibling, other_detail]
    after, sidecar = ext.reassemble(rows, details, {key: parameters()},
                                    {key: {'status': 'certified', 'visit_weighted_ok': True, 'n': 20}},
                                    {key: fit['c0']}, {key: {0: 50, 1: 4950}})
    assert after[key]['status'] == 'estimated' and after[key]['a13']['certified_by_extension']
    assert after[key]['a4']['validated_support_size'] == 2 and after[key]['a4']['floor']['passed']
    assert after[key]['continuation'] == row['continuation'] and after[key]['sensitivity'] == row['sensitivity']
    assert a.canonical(after[other_key]) == a.canonical(other)
    assert a.canonical(sidecar[1:]) == a.canonical(details[1:])
    after[other_key]['new'] = True
    with pytest.raises(ValueError, match='ineligible row'):
        ext.assert_ineligible_identity(rows, after, details, sidecar, {key})
    after[other_key].pop('new'); sidecar[1]['new'] = True
    with pytest.raises(ValueError, match='ineligible sidecar'):
        ext.assert_ineligible_identity(rows, after, details, sidecar, {key})


def family(count=1000, failed=1, same_context=False, balanced=False):
    rows, details = {}, []
    for i in range(count):
        rule = execution_policy_class()[i + 1] if same_context and i < failed else execution_policy_class()[0 if balanced and i == 0 else 1]
        row, detail, _ = row_fixture(rule, 0 if same_context and i < failed else i)
        if i >= failed:
            row['status'] = 'estimated'; row.pop('reason')
        rows[row_key(row)] = row; details.append(detail)
    return rows, details


def document(rows, binding=None):
    manifest = dict(tag='v3_tables', calibration_hash='toy', complete_family=True, sensitivity_status='passed', required_row_keys=sorted(rows))
    if binding is not None: manifest['a13_admission'] = binding
    return a.seal(dict(schema='v3-tables-1', code_hash=a.code_identity(), fixture=False, manifest=manifest,
                       manifest_hash=a.digest(manifest), rows={k: a.seal(v) for k, v in rows.items()}))


def test_loader_admission_binding_unavailable_status_and_empty_behavior():
    rows, details = family()
    details[0]['cell_tests'][0]['n_traj'] = 123456
    bound = admit.binding(rows, details, 'A10_nominal_after_A13')
    assert 'n_traj' not in str(bound)
    tables = ProductionTables(document(rows, bound), calibration_hash='toy', registered=True)
    assert sum(r['status'] == 'not_estimable' for r in tables.rows.values()) == 1
    with pytest.raises(RuntimeError, match='not_estimable'):
        ProductionTables(document(rows), calibration_hash='toy', registered=True)
    good, good_details = family(3, 0)
    old = ProductionTables(document(good), calibration_hash='toy', registered=True)
    new = ProductionTables(document(good, admit.binding(good, good_details, 'validation_launched_under_A13')), calibration_hash='toy', registered=True)
    assert old.rows == new.rows and not admit.enabled(old) and not admit.enabled(new)


@pytest.mark.parametrize('defect', ['small', 'cap', 'context', 'balanced', 'violation', 'base', 'sensitivity', 'support', 'outside', 'hash', 'scope'])
def test_loader_limits_and_evidence(defect):
    # Start from a valid producer binding, then independently challenge the loader.
    count = 2000 if defect == 'context' else 1000
    valid_rows, valid_details = family(count, 2 if defect == 'context' else 1)
    bound = admit.binding(valid_rows, valid_details, 'A10_nominal_after_A13')
    assert admit.verify(valid_rows, bound) == set(bound['rows'])
    rows, details = family(999 if defect == 'small' else 2000 if defect == 'context' else 1000,
                           2 if defect in ('cap', 'context') else 1, defect == 'context', defect == 'balanced')
    key = next(k for k, r in rows.items() if r['status'] == 'not_estimable')
    if defect == 'violation': details[0]['cell_tests'][0]['eb'] = 'violation'
    if defect == 'base': rows[key]['a4']['base_screens_ok'] = False
    if defect == 'sensitivity': rows[key]['sensitivity']['passed'] = False
    if defect == 'support': rows[key]['a4']['validated_support_size'] = 0
    if defect not in ('outside', 'hash', 'scope'):
        with pytest.raises(ValueError):
            admit.binding(rows, details, 'A10_nominal_after_A13')
        # Rebind the deliberately invalid evidence without invoking the producer
        # gate, to ensure the loader itself enforces each condition.
        bound['primary_rows'] = len(rows)
        bound['rows'] = {}
        for d in details:
            if rows[d['row']]['status'] == 'not_estimable':
                tests = [{'cell': t['cell'], 'eb': t['eb']} for t in d['cell_tests']]
                bound['rows'][d['row']] = dict(row_sha256=a.digest(rows[d['row']]), cell_tests=tests, cell_tests_sha256=a.digest(tests))
    if defect == 'outside': bound['rows'] = {}
    if defect == 'hash': bound['rows'][key]['row_sha256'] = 'wrong'
    if defect == 'scope': bound['scope'] = 'other_already_validated'
    bound['admitted_set_sha256'] = a.digest(bound['rows'])
    with pytest.raises(ValueError):
        ProductionTables(document(rows, bound), calibration_hash='toy', registered=True)


def evaluation(reasons):
    return SimpleNamespace(available=np.array([r is None for r in reasons]), lookup=SimpleNamespace(unavailable_reasons=reasons))


def test_incidence_all_branches_and_unscored_unique_minimum():
    missing, bin_missing = admit.MISSING, 'unpublished_continuation_bin'
    ordinary = admit.allocation_decision(evaluation([None, missing, bin_missing]), [1, 1, 1], False, 0, None)
    unique = admit.allocation_decision(evaluation([None, missing]), [0, 1], True, 1, None)
    assert unique['affected'] and not unique['excluded_by_reason']
    filtered = admit.allocation_decision(evaluation([None, missing]), [1, 1], True, 0, None)
    no_incidence = admit.allocation_decision(evaluation([None, bin_missing]), [1, 1], False, 0, None)
    fallback = admit.allocation_decision(evaluation([missing, missing]), [1, 1], False, 0, 'all_rule_scores_unavailable')
    review = admit.yield_decision({missing: 3, bin_missing: 2})
    blank_review = admit.yield_decision({})
    summary = admit.summarize([ordinary, unique, filtered, no_incidence, fallback, review, blank_review])
    assert summary['ordinary_allocation']['numerator'] == 2 and summary['ordinary_allocation']['denominator'] == 3
    assert summary['survival_first']['numerator'] == summary['survival_first']['denominator'] == 2
    assert summary['yield_review']['numerator'] == 1 and summary['yield_review']['denominator'] == 2
    assert summary['ordinary_allocation']['balanced_fallbacks_by_reason'] == {'all_rule_scores_unavailable': 1}
    assert summary['survival_first']['survival_first_unavailable_selections_by_reason'] == {missing: 1}
    assert admit.pooled_incidence([summary])['affected_by_table_unavailability']
    assert all(r['rate'] is None and not r['assessed'] for r in admit.summarize([]).values())


def test_historical_pins_use_committed_bytes_not_working_note(tmp_path, monkeypatch):
    # The unset successor state: every current check is the A14 check.
    monkeypatch.setattr(a, 'STAGE2_COMMIT', None)
    monkeypatch.setattr(a, 'STAGE2_AMENDMENT_MARKER', None)
    text = b'Amendment A10\nAmendment A11\n'
    pin = dict(commit='old', path='note.md', sha256=hashlib.sha256(text).hexdigest())
    (tmp_path / 'note.md').write_bytes(b'different')
    def git(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 0, stdout=text if 'show' in cmd else b'')
    monkeypatch.setattr(a.subprocess, 'run', git)
    assert a.verify_registration(pin, tmp_path, instrument={'mapping': 'A10', 'k_star': 1.8, 'g': 'linear'}, historical=True) == pin
    with pytest.raises(RuntimeError, match='17f17ef9'):
        a.verify_registration(pin, tmp_path, instrument={'mapping': 'A10', 'k_star': 1.8, 'g': 'linear'})
    with pytest.raises(RuntimeError, match='stale'):
        a.verify_registration(dict(pin, sha256='bad'), tmp_path, historical=True)
    def not_ancestor(cmd, **kwargs): raise subprocess.CalledProcessError(1, cmd)
    monkeypatch.setattr(a.subprocess, 'run', not_ancestor)
    with pytest.raises(RuntimeError, match='locally'):
        a.verify_registration(pin, tmp_path, historical=True)


def test_current_pin_is_exact_and_clean(tmp_path, monkeypatch):
    # The unset successor state: every current check is the A14 check.
    monkeypatch.setattr(a, 'STAGE2_COMMIT', None)
    monkeypatch.setattr(a, 'STAGE2_AMENDMENT_MARKER', None)
    text = b'Amendment A10\nAmendment A11\nClarified, 2026-10-16: pricing R_max\n### Amendment A14\n'
    path = tmp_path / 'simulation/diagnostics/v3_rerun_design_note.md'; path.parent.mkdir(parents=True); path.write_bytes(text)
    pin = dict(commit=a.A14_COMMIT, path=path.relative_to(tmp_path).as_posix(), sha256=hashlib.sha256(text).hexdigest())
    monkeypatch.setattr(a.subprocess, 'run', lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, stdout=text if 'show' in cmd else b''))
    assert a.verify_registration(pin, tmp_path, instrument={'mapping': 'A10', 'k_star': 1.8, 'g': 'linear'}) == pin
    path.write_bytes(text + b'changed')
    with pytest.raises(RuntimeError, match='stale'): a.verify_registration(pin, tmp_path, instrument={'mapping': 'A10', 'k_star': 1.8, 'g': 'linear'})


def test_no_original_scientific_function_edited():
    import ast
    from pathlib import Path
    for name, functions in {'table_validation_a4.py': ['fit_stage', 'validate_stage', 'census_stage',
                            'assemble_family', 'assemble_plain_row', '_combine_plain', '_index_phase'],
                            'offline_estimator.py': ['simulate', 'estimate']}.items():
        path = 'simulation/v3/' + name
        old = subprocess.run(['git', 'show', '48815a65:' + path], capture_output=True, check=True).stdout.decode()
        current = (a.ROOT / name).read_text()
        def selected(source):
            return {n.name: ast.get_source_segment(source, n) for n in ast.parse(source).body
                    if isinstance(n, ast.FunctionDef) and n.name in functions}
        assert selected(old) == selected(current)
        assert set(selected(old)) == set(functions)
    for name in ('continuation_validation.py', 'offline_estimator.py'):
        old = subprocess.run(['git', 'show', '48815a65:simulation/v3/' + name], capture_output=True, check=True).stdout
        assert hashlib.sha256(old.replace(b'\r\n', b'\n')).hexdigest() == hashlib.sha256(
            (a.ROOT / name).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def durable(root, job, result):
    path = root / 'outputs' / (job['id'] + '.json')
    a.atomic_json(path, dict(job=job, code_hash=a.code_identity(), result=result))
    a.atomic_json(root / 'records' / (job['id'] + '.json'),
                  dict(status='complete', job=job, code_hash=a.code_identity(), output_hash=a.file_hash(path)))


def round_evidence(plan, root, *, plan_path=None, complete=True, checked=True):
    from pathlib import Path
    record_path = Path(plan['round_record_path'])
    path = plan_path or record_path.with_name(record_path.name.removesuffix('.round.json') + '.json')
    ext.begin_round(plan, path, root)
    a.atomic_json(root / 'identity.json', dict(spec_hash=a.digest(plan), code_hash=plan['code_hash']))
    a.atomic_json(root / 'launches.json', [dict(complete=complete)])
    if checked:
        a.atomic_json(root / ext.PHASE / 'nondeterminism_check.json', dict(matched=True, checked=plan['jobs'][0]['id']))


def toy_original(base):
    """Synthetic A1 and A4 durable records, processed by the real assemblers."""
    from v3 import tables_a10 as tables, table_validation_a4 as a4
    from v3.offline_estimator import estimate
    from v3.context import Context
    cal_path = 'v3/runs/registered/v3_rerun_calibration.json'
    calibration = a.read(a.SIMULATION / cal_path)
    settings = dict(groups=3, runs_per_group=2, particles=2, burn=30, measure=8, census_measure=38)
    jobs = tables.build_jobs('nominal', cal_path, settings_override={k: v for k, v in settings.items() if k != 'census_measure'},
                            kernel_override={'n_agents': 16, 'carrying_capacity': 160},
                            rule_ids=[execution_policy_class()[2].rule_id], physical_contexts=[(.064, 1.), (.064, 1.5)])
    jobs = [a.stable_job('table', dict(j['config'], route='plain' if j['config']['kernel']['capability'] == 1 else 'fv'), j['tag'], j['index']) for j in jobs]
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
        for row in result['rows']: row['route'] = result['route']
        durable(source / 'tables_A1/table', j, result)
        outputs.append(dict(job=j, result=result, code_hash=a.code_identity()))
    a.atomic_json(source / 'tables_A1_manifest.json', a.seal(dict(jobs=jobs, code_hash=a.code_identity(), source_family={'code_hash': a.code_identity()}, tag='pilot', registered=False)))
    tables.assemble(outputs, calibration, source / 'v3_rerun_tables_A1.json', 'nominal', jobs=jobs)
    probe = base / 'probe'; a.atomic_json(probe / 'seeds.json', {'non_registered': True, 'seed': 84737})
    plan = tables.prepare_validation(source, cal_path, probe_root=probe, settings_override=settings)
    source_by_id = {o['job']['id']: o for o in outputs}
    for j in plan['jobs']:
        c = j['config']; source_result = source_by_id[c['a1_job']['id']]['result']
        common = dict(a1_job_id=c['a1_job']['id'], stream_seed=c['seed'], plan_hash=plan['plan_hash'], code_hash=a.code_identity(), route=c['route'])
        if c['stage'] == 'fit':
            rows = [{'scoring': r['scoring'], 'c0': {'value': r['lambda_f']['mean'], 'published': True}}
                    for r in source_result['rows']]
            result = dict(common, rows=rows, stage='fit')
        elif c['stage'] == 'validate':
            stats = dict.fromkeys(cv.STAT_KEYS, 0.)
            cells = [dict(stats, cell=1, n_traj=100000, sum_N=100000), dict(stats, cell=cv.POP0_CELL, n_traj=1, sum_N=1)] if c['route'] == 'plain' else [{'cell': 1, 'S_g': [0.] * 32, 'N_g': [100.] * 32}]
            result = dict(common, stage='validate', replicate=c['replicate'], rows=[{'cells': cells, 'scoring': r['scoring']} for r in source_result['rows']])
        else:
            result = dict(common, stage='census', total_living=10000, total_low=50 if source_result['route'] == 'plain' else 0, cell_counts={1: 9950, 0: 50} if source_result['route'] == 'plain' else {1: 10000})
        durable(run / c['phase'], j, result)
    projection = a.seal({'per_phase_capability': {'nominal.1.0.primary.validate_plain': {
        'jobs': 10, 'x2_hours_max': 3., 'mean_worker_seconds': 30., 'memory_estimate_gb': .1}}})
    plan['pull_dispatch'] = {'projection_sha256': projection['sha256']}
    plan_path = base / 'original_plan.json'; a.atomic_json(plan_path, a.seal(plan))
    a4.publish(plan, run, source, calibration, base / 'original_family.json', registered=False)
    candidate = run / 'candidate_unpublished_tables.json'
    projection_path = base / 'projection.json'; a.atomic_json(projection_path, projection)
    inventory_path = base / 'seeds.json'; a.atomic_json(inventory_path, a.seal({k: [84737] if k == 'probe' else [] for k in ('registered', 'planning', 'probe', 'rehearsal', 'qualification')}))
    return plan_path, run, candidate, projection_path, inventory_path, source, cal_path, probe, settings


def test_toy_end_to_end_publication_a5_receipt_and_resume(tmp_path, monkeypatch):
    from v3 import production_runner as runner, table_labels_a5 as labels, tables_a10
    original, original_root, candidate, projection, inventory, source, cal_path, probe, settings = toy_original(tmp_path)
    plan = ext.prepare(original, original_root, candidate, projection, inventory, tmp_path / 'extension_plan.json', rehearsal=True)
    assert plan['E'] == plan['P'] > 0 and plan['M'] >= plan['P'] and plan['R_max'] == 16
    assert ext.validate_plan(plan) == plan
    public = ext.public_record(plan)
    assert 'prices' not in str(public) and 'n_star' not in str(public) and 'width' not in str(public)
    assert public['family_error_bound_given_fit'] == .05 * (1 + plan['P'] / plan['M'])
    assert public['conditional_additional_error_bound'] == .05 * plan['E'] / plan['M']
    job = plan['jobs'][0]
    root = tmp_path / 'extension'
    calls = []
    def trajectories(a1, fit, rows, seed, override=None):
        calls.append(seed)
        return dict(count=6, settings=settings, rows={k: [[0., 1]] * 6 for k in rows})
    monkeypatch.setattr(ext, 'extension_stage', trajectories)
    result = runner.execute(job, root=root / ext.PHASE)
    assert result['stopped_on_visits'] and len(result['replicates']) < plan['R_max']
    durable(root / ext.PHASE, job, result)
    calls.clear()
    assert runner.execute(job, root=root / ext.PHASE) == result and not calls
    # A check must recompute, not reuse its completion checkpoints.
    with ext.checkpoint_context(tmp_path / 'check', result['replicates'], recheck=True):
        assert runner.execute(job, root=root / ext.PHASE) == result
    assert calls
    target = tmp_path / 'amended.json'
    round_evidence(plan, root)
    ext.publish(plan, root, target, registered=False)
    receipt = a.unseal(a.read(target.with_suffix('.compatibility.json')))
    old = a.unseal(a.read(candidate.with_suffix('.compatibility.json')))
    assert receipt['plan_hash'] == old['plan_hash'] and receipt['stream_seeds'] == old['stream_seeds']
    assert receipt['extension_plan_hash'] == plan['plan_hash'] and receipt['extension_stage_output_sha256']
    assert 'extension_stream_seeds' not in receipt and receipt['extension_seed_manifest'] == plan['seed_manifest']
    published = a.read(target)
    identity = dict(family_file_sha256=a.file_hash(target), table_seal_sha256=published['sha256'],
                    receipt_file_sha256=a.file_hash(target.with_suffix('.compatibility.json')),
                    sidecar_file_sha256=a.file_hash(target.with_suffix('.cell_results.json')), producing_commit='toy', code_hash=a.code_identity())
    identity_path = tmp_path / 'family_identity.json'; a.atomic_json(identity_path, identity)
    label_plan = labels.prepare(target, original_root, original, source, cal_path, identity_path,
                                wall_hours=1., a3_probe_root=probe, settings_override=settings,
                                instrument=tables_a10.NOMINAL)
    assert label_plan['jobs'] and len(label_plan['jobs']) == 3
    assert all(not ext.RESERVED[0] <= j['config']['seed'] < ext.RESERVED[1] for j in label_plan['jobs'])
    with pytest.raises(ValueError, match='frozen'):
        ext.prepare(original, original_root, candidate, projection, inventory, tmp_path / 'extension_plan.json', rehearsal=True)
    a.atomic_json(target, a.seal({'changed': True}))
    with pytest.raises(RuntimeError, match='frozen'):
        ext.publish(plan, root, target, registered=False)


def minimal_extension_job():
    source = source_job()
    manifest = ext.seed_manifest([source], 6, [])
    config = dict(phase=ext.PHASE, a1_job=source, a1_source_root='unused', a1_source_code_hash=a.code_identity(),
                  eligible_rows={'a': parameters(8), 'b': parameters(9)}, M=20, R_max=6,
                  full_seed_manifest=manifest, forbidden_seeds=[], stream_seeds=[m['seed'] for m in manifest],
                  trajectory_count=6, plan_hash='test', fit=a.seal({'a1_job_id': source['id'], 'rows': []}))
    return a.stable_job(ext.KIND, config, 'v3_tables', 0)


def test_interruption_keeps_complete_replicates_and_checkpoint_binding(tmp_path, monkeypatch):
    job = minimal_extension_job()
    monkeypatch.setattr(ext.a4, '_load_a1', lambda *args: {})
    calls = []
    def stage(*args):
        calls.append(args[3])
        if len(calls) == 2: raise OSError('injected infrastructure interruption')
        return dict(count=6, rows={'a': [[0., 1]] * 6, 'b': [[0., 1]] * 6})
    monkeypatch.setattr(ext, 'extension_stage', stage)
    with pytest.raises(OSError): ext.run_stage_job(job, tmp_path / ext.PHASE)
    assert len(ext.durable_checkpoints(tmp_path, job)) == 1
    result = ext.run_stage_job(job, tmp_path / ext.PHASE)
    assert len(result['replicates']) == 2
    assert calls == [job['config']['stream_seeds'][0], job['config']['stream_seeds'][1], job['config']['stream_seeds'][1]]
    broken = deepcopy(result['replicates']); broken[0]['seed'] += 1
    with pytest.raises(ValueError, match='seed/order'): ext.validate_replicates(job, broken)
    broken = deepcopy(result['replicates']); broken.append(deepcopy(broken[-1]))
    with pytest.raises(ValueError, match='after registered stop'): ext.validate_replicates(job, broken)
    with pytest.raises(ValueError, match='M differs'):
        changed = deepcopy(job); changed['config']['M'] += 1; ext.run_stage_job(changed, tmp_path)


def test_coordinator_checkpoints_are_durable_and_wrong_lease_rejected(tmp_path):
    job = minimal_extension_job()
    coordinator = SimpleNamespace(root=tmp_path, jobs={job['id']: job}, session=lambda r: None,
        state={'halt': None, 'leases': {'lease': {'host': 'toy', 'session': 'one', 'job_id': job['id'], 'purpose': 'work'}}})
    replica = dict(replicate=4, seed=job['config']['stream_seeds'][0], count=6,
                   rows={'a': [[0., 1]] * 6, 'b': [[0., 1]] * 6})
    request = dict(host='toy', session='one', lease='lease', checkpoint=a.seal({'job_sha256': a.digest(job), 'replicate': replica}))
    assert ext.accept_checkpoint(coordinator, request)['accepted']
    assert ext.durable_checkpoints(tmp_path, job) == [replica]
    assert ext.accept_checkpoint(coordinator, request)['accepted']
    with pytest.raises(ValueError, match='lease'): ext.accept_checkpoint(coordinator, dict(request, host='other'))
    changed = deepcopy(replica); changed['rows']['a'][0][0] = 1
    with pytest.raises(ext.ScientificHalt):
        ext.accept_checkpoint(coordinator, dict(request, checkpoint=a.seal({'job_sha256': a.digest(job), 'replicate': changed})))
    assert (tmp_path / 'a13_scientific_halt.json').exists() and coordinator.state['halt']


def test_rehearsal_seeds_and_configuration_outside_reservation():
    jobs = [source_job(i) for i in range(4)]
    manifest = ext.seed_manifest(jobs, 16, [], rehearsal=True)
    assert all(r['seed'] >= 1 << 128 for r in manifest)
    with pytest.raises(ValueError, match='range'): ext.check_seed_manifest(manifest, [])
    from v3.table_labels_a5 import assert_a5_seeds
    with pytest.raises(cv.SeedCollision):
        from unittest.mock import patch
        with patch('v3.table_labels_a5.fvplain_seed', return_value=1 << 60):
            assert_a5_seeds([42], set())


@pytest.mark.parametrize('survival,available,risks,expected,affected', [
    (False, [True, False, True], [0, 0, 0], 2, True),
    (False, [False, False, False], [0, 0, 0], 0, True),
    (True, [True, False, True], [2, 0, 1], 1, True),
    (True, [True, False, True], [0, 0, 1], 0, True),
    (True, [True, False, True], [0, 1, 2], 0, False),
])
def test_controller_actual_allocation_branches(monkeypatch, survival, available, risks, expected, affected):
    from v3.integration import V3Model
    model = V3Model(2, rules=execution_policy_class()[:3], successor_capability=None)
    evaluation = SimpleNamespace(actions=np.ones((3, 6)), available=np.array(available),
        scores=np.array([1., 2., 3.]), errors=np.zeros(3),
        lookup=SimpleNamespace(unavailable_reasons=tuple(None if x else admit.MISSING for x in available)))
    monkeypatch.setattr(model, '_eligible', lambda _: (np.ones(3, bool), np.array(risks), survival))
    before = model._choose(evaluation)
    model._a13_enabled = True; model.a13_decisions = []
    after = model._choose(evaluation)
    assert before[:3] == after[:3] and np.array_equal(before[3], after[3]) and after[0] == expected
    recorded = model.a13_decisions[0]
    assert recorded['affected'] == affected
    assert recorded['branch'] == ('survival_first' if survival else 'ordinary_allocation')
    if survival and not available[expected]:
        assert recorded['selected_score_unavailable_reason'] == admit.MISSING
        assert not recorded['excluded_by_reason']


@pytest.mark.parametrize('all_missing', [False, True])
def test_actual_yield_review_incidence_and_absorbed_padding(all_missing):
    from test_v3_unpublished_bins import model, SelectivePlans
    from v3.production_tables import AvailableLookup
    m = model(); m.successor_capability = 1.5
    class MissingRows(SelectivePlans):
        def lookup_available(self, *args, **kwargs):
            value = super().lookup_available(*args, **kwargs)
            return AvailableLookup(value.continuation, value.continuation_error, value.lambda_f, value.lambda_error,
                value.lambda_b, value.lifetime_surplus, value.fixture, value.available,
                tuple(None if x else admit.MISSING for x in value.available))
    m.tables = MissingRows(m.tables, all_missing=all_missing)
    m._a13_enabled = True; m.a13_decisions = []
    m.step()
    incidence = admit.summarize(m.a13_decisions)
    assert incidence['yield_review']['numerator'] == incidence['yield_review']['denominator'] == 1
    assert incidence['yield_review']['excluded_by_reason'][admit.MISSING] == (12 if all_missing else 4)
    assert m.yield_events[0]['yield_held_no_admissible_plan'] == all_missing
    before = deepcopy(incidence)
    m.state.ages[:] = -1
    record = m.step()
    assert record['allocation_evaluated'] is False and admit.summarize(m.a13_decisions) == before


def test_extension_stage_records_ordered_pairs_without_validation_index(monkeypatch):
    row, _, fit = row_fixture()
    # Time-major transitions for three trajectories: counts 2, 0, 1.
    before = np.array([[0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]] * 2)
    trace = SimpleNamespace(before=before, after=before, source_alive=np.array([1, 1, 1, 1, 1, 0], bool),
        dead=np.zeros(6, bool), lower=-10., upper=0., traj=np.tile(np.arange(3), 2), count=3,
        truncated=False, settings={'burn': 500, 'measure': 1000}, flows=lambda _: np.array([-9., -10., -8., -7., -10., -10.]))
    monkeypatch.setattr(ext.a4, 'TableTrace', lambda *args: trace)
    for name in ('_index_phase', '_combine_plain'):
        monkeypatch.setattr(ext.a4, name, lambda *args: pytest.fail('extension entered original validation index'))
    result = ext.extension_stage({'result': {'route': 'plain', 'rows': [row]}}, {'rows': [fit]}, {'row': parameters()}, 42)
    factor = 1 - math.exp(-.01)
    assert np.asarray(result['rows']['row']) == pytest.approx(np.array([[4. * factor, 2], [0., 0], [2. * factor, 1]]))
    trace.truncated = True
    with pytest.raises(ext.ScientificHalt):
        ext.extension_stage({'result': {'route': 'plain', 'rows': [row]}}, {'rows': [fit]}, {'row': parameters()}, 42)


def test_no_launch_floor_and_impossible_flags(tmp_path):
    original, run, candidate, projection, inventory, *_ = toy_original(tmp_path)
    document = a.seal({'per_phase_capability': {'nominal.1.0.primary.validate_plain': {'jobs': 1, 'x2_hours_max': 48.}}})
    a.atomic_json(projection, document)
    original_plan = a.unseal(a.read(original)); original_plan['pull_dispatch']['projection_sha256'] = document['sha256']
    a.atomic_json(original, a.seal(original_plan))
    plan = ext.prepare(original, run, candidate, projection, inventory, tmp_path / 'no_launch.json', rehearsal=True)
    assert plan['R_max'] == 0 and not plan['launch_allowed'] and all(plan['impossible_rows'].values())
    with pytest.raises(ValueError, match='no-launch'): ext.validate_plan(plan, launching=True)
    target = tmp_path / 'no_family.json'
    with pytest.raises(ValueError, match='cap exceeded'):
        ext.publish(plan, tmp_path / 'never_launched', target, registered=False)
    assert not target.exists()  # Part 2 runs even when no simulation can launch.


def test_scientific_halt_certifies_nothing_and_checks_admission(tmp_path):
    original, run, candidate, projection, inventory, *_ = toy_original(tmp_path)
    plan = ext.prepare(original, run, candidate, projection, inventory, tmp_path / 'plan.json', rehearsal=True)
    root = tmp_path / 'extension'
    round_evidence(plan, root, complete=False, checked=False)
    a.atomic_json(root / 'a13_scientific_halt.json', a.seal({'reason': 'synthetic halt'}))
    with pytest.raises(ValueError, match='cap exceeded'):
        ext.publish(plan, root, tmp_path / 'forbidden_family.json', registered=False)
    assert not (tmp_path / 'forbidden_family.json').exists()
    assert a.unseal(a.read(tmp_path / 'plan.round.json'))['halt']
    refusal = a.unseal(a.read(tmp_path / 'plan.round.admission.json'))
    assert refusal['outcome'] == 'refused' and refusal['residual_count'] >= plan['E']


def test_plan_m_bound_before_launch_and_qualification_profiles(tmp_path):
    from v3 import qualification_a11 as q, multihost_a11 as multi, snapshot_a11
    original, run, candidate, projection, inventory, *_ = toy_original(tmp_path)
    path = tmp_path / 'plan.json'
    plan = ext.prepare(original, run, candidate, projection, inventory, path, rehearsal=True)
    assert ext.validate_plan(plan, launching=True)
    qplan = q.build(path, tmp_path / 'empty_root', tmp_path / 'qualification.json')
    assert len(qplan['jobs']) >= 20 and qplan['kinds'] == [ext.KIND]
    assert all(j['config']['configuration_test'] and j['config']['seed'] >= 1 << 128 for j in qplan['jobs'])
    assert not any('/validate_plain/' in r['path'] for r in qplan['inputs']['payload']['files'])
    projection_doc = a.read(projection)
    frozen = multi.freeze(plan, projection_doc, code_commit='toy')
    assert frozen['jobs'] == plan['jobs'] and ext.validate_plan(frozen)
    assert ext.KIND in multi.ALLOWED_KINDS
    changed_projection = deepcopy(frozen); changed_projection['pull_dispatch']['projection_sha256'] = 'wrong'
    with pytest.raises(ValueError, match='dispatch projection'): ext.validate_plan(changed_projection)
    changed = a.unseal(a.read(original)); changed['M'] += 1; a.atomic_json(original, a.seal(changed))
    with pytest.raises(ValueError, match='original plan changed'): ext.validate_plan(plan, launching=True)


def test_registered_publication_requires_exact_target_and_current_pin(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(ext, 'validate_plan', lambda plan: plan)
    monkeypatch.setattr(a, 'verify_registration', lambda *args, **kwargs: calls.append((args, kwargs)))
    plan = dict(registered=True, registration={'commit': a.A13_COMMIT}, instrument={'mapping': 'A10'})
    with pytest.raises(ValueError, match='exact configured publication target'):
        ext.publish(plan, tmp_path, tmp_path / 'wrong_target.json')
    assert calls and not calls[0][1].get('historical', False)
    with pytest.raises(ValueError, match='registered plan'):
        ext.publish(dict(plan, registered=False), tmp_path, tmp_path / 'wrong_target.json')


@pytest.mark.parametrize('yield_reviews', [False, True])
def test_run_summary_contains_branch_counts_only_when_enabled(tmp_path, monkeypatch, yield_reviews):
    from v3 import production_runner as runner, recording
    from test_v3_unpublished_bins import sparse_tables
    def run(enabled):
        model = sparse_tables(recording.RecordedV3Model(200, rules=execution_policy_class()[:3],
            rollout_steps=1, successor_capability=None), tmp_path / str(enabled), missing_rows=(1,))
        model._a13_enabled = enabled
        if yield_reviews: model.successor_capability = 1.5
        if enabled: model.a13_decisions = []
        monkeypatch.setattr(recording, 'RecordedV3Model', lambda **kwargs: model)
        return runner.execute(a.stable_job('rerun', {'steps': 3}, 'validation', 0))
    real_class = recording.RecordedV3Model
    old = run(False)
    monkeypatch.setattr(recording, 'RecordedV3Model', real_class)
    new = run(True)
    incidence = new.pop('a13_decision_incidence')
    assert a.canonical(old) == a.canonical(new)
    assert incidence['ordinary_allocation']['numerator'] == incidence['ordinary_allocation']['denominator'] == 3
    assert incidence['survival_first']['rate'] is None and not incidence['survival_first']['assessed']
    assert incidence['yield_review']['denominator'] == (1 if yield_reviews else 0)
    if yield_reviews:
        assert new['yield_events'] and all('a13_decision' not in e for e in new['yield_events'])


def test_real_toy_extension_trace_and_host_checkpoint_transport(tmp_path):
    from v3 import host_a11, snapshot_a11
    original, run, candidate, projection, inventory, *_ = toy_original(tmp_path)
    plan = ext.prepare(original, run, candidate, projection, inventory, tmp_path / 'plan.json', rehearsal=True)
    job = plan['jobs'][0]
    root = tmp_path / 'extension'
    inputs = snapshot_a11.inventory([job], root / ext.PHASE)
    view = snapshot_a11.receive(inputs, tmp_path / 'snapshot', lambda name, offset: snapshot_a11.fetch(inputs, name, offset))
    target = tmp_path / 'host' / 'unpublished.json'
    host_a11.execute_scratch(str(target), job, a.code_identity(), str(root / ext.PHASE), view,
                             False, None, 'synthetic-host', 'synthetic-lease')
    result = a.read(target)['result']
    replicas = result['replicates']
    assert 1 <= len(replicas) <= plan['R_max']
    assert ext.validate_replicates(job, replicas) == replicas
    assert len(list(target.with_suffix('.a13').glob('*.json'))) == len(replicas)
    for replica in replicas:
        assert replica['count'] == 6
        assert replica['settings']['burn'] == 30 and replica['settings']['measure'] == 8
    # Resume from coordinator-provided full replicas on a different scratch root.
    resumed = tmp_path / 'other_host' / 'unpublished.json'
    host_a11.execute_scratch(str(resumed), job, a.code_identity(), str(root / ext.PHASE), view,
                             False, None, 'other-synthetic-host', 'other-lease', replicas)
    assert a.canonical(a.read(resumed)['result']) == a.canonical(result)


class A13HostTransport(_Loopback):
    """Record real RPC traffic; local stdio retains fixture host qualification."""
    def __init__(self, root, route, *, drain=False):
        from v3.host_a11 import Local
        super().__init__(root)
        self.local = Local(root) if route == 'local' else None
        self.ops, self.claims, self.first_hashes = [], [], {}
        self.drain = drain

    def call(self, request):
        from v3 import multihost_a11 as multi
        result = self.local.call(request) if self.local else super().call(request)
        self.ops.append(request['op'])
        if request['op'] == 'claim':
            self.claims.extend(result['claims'])
        if request['op'] == 'a13_checkpoint' and self.drain:
            self.drain = False
            self.first_hashes = checkpoint_hashes(self.root)
            assert self.first_hashes
            multi.control(self.root, stop='drain')
        return result

    def close(self):
        if self.local:
            self.local.close()


def checkpoint_hashes(root):
    return {p.relative_to(root).as_posix(): a.file_hash(p)
            for p in (root / ext.PHASE / 'a13_checkpoints').glob('*/*.json')}


def a13_scientific_halt_worker(*args):
    """Spawned real executor, with a scientific failure after one real replica."""
    from v3.host_a11 import execute_scratch
    original_stage = ext.extension_stage
    calls = 0
    def fail_second_replica(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ext.ScientificHalt('synthetic host scientific halt')
        return original_stage(*args, **kwargs)
    ext.extension_stage = fail_second_replica
    execute_scratch(*args)


def prepare_host_extension(tmp_path):
    from v3 import multihost_a11 as multi, host_a11 as host
    from test_v3_multihost_a11 import evidence
    original, run, candidate, projection, inventory, *_ = toy_original(tmp_path)
    path, root = tmp_path / 'host_plan.json', tmp_path / 'coordinator'
    plan = ext.prepare(original, run, candidate, projection, inventory, path, rehearsal=True)
    for profile in plan['configuration'].values():
        profile.update(workers_local=[1], jobs_local=1, jobs_per_worker=1, rounds=1)
    plan = multi.freeze(plan, a.read(projection), code_commit='fixture', lease_seconds=6)
    a.atomic_json(path, a.seal(plan))
    settings = dict(profile='local', workers=1, threads=1, cpu_budget=2, mode='work')
    multi.prepare(path, root, settings)
    multi.approve_host(root, evidence(host.platform.node(), plan['code_hash'], (ext.KIND,), settings=settings),
                       'synthetic operator', '2026-10-17')
    return plan, path, root, settings


def host_loop_attempt(path, root, settings, scratch, transport):
    """Run the real coordinator monitor and host loop, including spawned workers."""
    from concurrent.futures import ThreadPoolExecutor
    import time
    from v3 import multihost_a11 as multi, host_a11 as host
    from test_v3_multihost_a11 import FINGERPRINT
    epoch = multi.read_state(root)['epoch']
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(multi.coordinate, path, root, settings)
        try:
            until = time.monotonic() + 30
            while True:
                # Respect the initialization transaction before reading SQLite.
                with multi.transaction(root):
                    started = multi.read_state(root)['epoch'] > epoch and (root / 'launches.json').exists()
                if started:
                    break
                if future.done():
                    future.result()
                assert time.monotonic() < until, 'coordinator did not start'
                time.sleep(.05)
            result = host.run_host(transport, scratch, settings, host=host.platform.node(),
                                   environment=FINGERPRINT, max_seconds=120)
            return result, future.result(timeout=30)
        finally:
            if not future.done():
                multi.control(root, stop='now')
                future.result(timeout=30)


@pytest.mark.parametrize('route', ['loopback', 'local'])
def test_a13_real_host_rpc_checkpoint_drain_and_resume(tmp_path, route):
    from v3 import multihost_a11 as multi, production_runner as runner
    plan, path, root, settings = prepare_host_extension(tmp_path)
    first = A13HostTransport(root, route, drain=True)
    result, status = host_loop_attempt(path, root, settings, tmp_path / 'first_host', first)
    assert result['stopped'] and not status['complete'] and not status['halt']
    assert first.first_hashes and 'a13_checkpoint' in first.ops
    hashes = checkpoint_hashes(root)
    assert all(hashes[p] == value for p, value in first.first_hashes.items())
    assert all(ext.durable_checkpoints(root, job) for job in plan['jobs'])
    assert all(runner.completed(root / ext.PHASE, job, plan['code_hash']) for job in plan['jobs'])
    before = a.unseal(a.read(ext.round_record_path(plan)))
    multi.control(root, stop='clear')
    second = A13HostTransport(root, route)
    result, status = host_loop_attempt(path, root, settings, tmp_path / 'resumed_host', second)
    assert result['stopped'] and status['complete'] and not status['halt']
    assert checkpoint_hashes(root) == hashes
    assert a.unseal(a.read(ext.round_record_path(plan))) == before
    assert [c['purpose'] for c in second.claims] == ['check']
    assert a.read(root / ext.PHASE / 'nondeterminism_check.json')['matched']
    assert [r['complete'] for r in a.read(root / 'launches.json')] == [False, True]
    assert not ext.publication_round(plan, root)
    assert set(first.ops + second.ops) >= {'inspect', 'join', 'inputs', 'fetch', 'configure', 'configured',
                                         'heartbeat', 'ready', 'claim', 'a13_checkpoint', 'complete', 'leave'}


@pytest.mark.parametrize('route', ['loopback', 'local'])
def test_a13_real_host_scientific_halt_through_rpc_certifies_nothing(tmp_path, monkeypatch, route):
    from v3 import host_a11 as host, multihost_a11 as multi, production_runner as runner
    plan, path, root, settings = prepare_host_extension(tmp_path)
    monkeypatch.setattr(host, 'execute_scratch', a13_scientific_halt_worker)
    transport = A13HostTransport(root, route)
    with pytest.raises(RuntimeError, match='remote worker failed'):
        host_loop_attempt(path, root, settings, tmp_path / 'failed_host', transport)
    assert {'a13_checkpoint', 'a13_halt', 'release'} <= set(transport.ops)
    # A halt can mark contact lost before host cleanup, which then skips leave.
    assert 'leave' in transport.ops or a.read(tmp_path / 'failed_host' / 'host_exit.json')['contact_lost'] is True
    assert checkpoint_hashes(root)
    assert multi.read_state(root)['halt'] == 'A13 scientific halt'
    assert a.unseal(a.read(ext.round_record_path(plan)))['halt']
    assert all(runner.completed(root / ext.PHASE, job, plan['code_hash']) is None for job in plan['jobs'])
    assert ext.publication_round(plan, root) is True
    monkeypatch.setattr(ext, 'extension_test', lambda *args: pytest.fail('halted trajectory was tested'))
    target = tmp_path / 'must_not_publish.json'
    with pytest.raises(ValueError, match='cap'):
        ext.publish(plan, root, target, registered=False)
    assert not target.exists()
    with pytest.raises(ValueError, match='round spent'):
        multi.prepare(path, root, settings)


def test_host_operations_all_cross_rpc_allowlist_and_ssh_has_no_operation_filter(monkeypatch, tmp_path):
    import ast
    import inspect
    from v3 import host_a11 as host, multihost_a11 as multi
    # Every literal host operation, including Client.call and direct transport calls.
    tree = ast.parse(inspect.getsource(host))
    invoked = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'call' and node.args:
            argument = node.args[0]
            if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                invoked.add(argument.value)
            elif isinstance(argument, ast.Dict):
                invoked.update(v.value for k, v in zip(argument.keys, argument.values)
                               if isinstance(k, ast.Constant) and k.value == 'op' and isinstance(v, ast.Constant))
    accepted = set(ast.literal_eval(ast.parse(inspect.getsource(multi.rpc)).body[0].body[0].test.comparators[0]))
    assert invoked == accepted
    dispatched = []
    class StubCoordinator:
        def __init__(self, *args): pass
        def request(self, request): dispatched.append(request['op']); return request
        def save(self): pass
    monkeypatch.setattr(multi, 'Coordinator', StubCoordinator)
    for op in sorted(invoked):
        assert multi.rpc(tmp_path, {'op': op}) == {'op': op}
    assert set(dispatched) == invoked
    with pytest.raises(ValueError, match='unknown coordinator command'):
        multi.rpc(tmp_path, {'op': 'arbitrary_shell'})
    ssh = host.SSH('synthetic-host', '/synthetic/checkout', '/synthetic/root')
    assert isinstance(ssh, host.Stdio) and ssh.argv[-1] == ssh.command
    assert 'v3.multihost_a11 rpc /synthetic/root --stream' in ssh.command
    assert 'a13_checkpoint' not in ssh.command and 'a13_halt' not in ssh.command


def test_compatibility_checks_carried_registered_plan_pin_before_outputs(tmp_path, monkeypatch):
    from v3 import compatibility_a10 as compat
    before = a.source_manifest(); before['v3/service.py'] = '0' * 64
    original_code = a.digest(before)
    reasons = tmp_path / 'reasons.json'
    a.atomic_json(reasons, dict(producing_source_manifest=before, reasons={'v3/service.py': 'synthetic change'}))
    pin = dict(commit='historical', path='note.md', sha256='0' * 64)
    spec = tmp_path / 'source_plan.json'
    instrument = dict(mapping='A10', k_star=1.8, g='linear')
    a.atomic_json(spec, a.seal(dict(code_hash=original_code, registered=True, registration=pin, instrument=instrument)))
    calls = []
    monkeypatch.setattr(a, 'verify_registration', lambda *args, **kwargs: calls.append((args, kwargs)))
    with pytest.raises(FileNotFoundError):
        compat.build_record([dict(spec=str(spec), root=str(tmp_path / 'no_outputs'))], reasons, tmp_path / 'proof.json', workers=1)
    assert calls == [((pin,), dict(instrument=instrument, historical=True))]


@pytest.mark.parametrize('registered,rehearsal', [(False, False), (True, True)])
def test_prepare_requires_exactly_one_launch_mode(tmp_path, registered, rehearsal):
    with pytest.raises(ValueError, match='exactly one'):
        ext.prepare('unused', 'unused', 'unused', 'unused', 'unused', tmp_path / 'plan.json',
                    registration={} if registered else None, rehearsal=rehearsal)


@pytest.mark.parametrize('registered,rehearsal', [(False, False), (True, True)])
def test_plan_requires_exactly_one_launch_mode(tmp_path, registered, rehearsal):
    original, run, candidate, projection, inventory, *_ = toy_original(tmp_path)
    plan = ext.prepare(original, run, candidate, projection, inventory, tmp_path / 'plan.json', rehearsal=True)
    plan.update(registered=registered, non_registered_rehearsal=rehearsal)
    plan['plan_hash'] = ext.plan_hash(plan)
    with pytest.raises(ValueError, match='exactly one'):
        ext.validate_plan(plan)


def test_execute_extension_requires_registration_or_unreserved_test(monkeypatch):
    from v3 import production_runner as runner
    job = minimal_extension_job()
    monkeypatch.setattr(ext, 'run_stage_job', lambda *args: 'executed')
    with pytest.raises(ValueError, match='requires rehearsal'):
        runner.execute(job)
    assert runner.execute(job, registered=True) == 'executed'
    c = dict(job['config'], non_registered_rehearsal=True)
    with pytest.raises(ValueError, match='reserved seed range'):
        runner.execute(a.stable_job(ext.KIND, c, 'v3_tables', 0))
    c.update(full_seed_manifest=ext.seed_manifest([c['a1_job']], 6, [], rehearsal=True))
    c['stream_seeds'] = [r['seed'] for r in c['full_seed_manifest']]
    assert runner.execute(a.stable_job(ext.KIND, c, 'v3_tables', 0)) == 'executed'
    c = dict(job['config'], configuration_test=True, seed=ext.RESERVED[0])
    with pytest.raises(ValueError, match='reserved seed range'):
        runner.execute(a.stable_job(ext.KIND, c, 'configuration', 0))
    c['seed'] = 1 << 128
    assert runner.execute(a.stable_job(ext.KIND, c, 'configuration', 0)) == 'executed'
    with pytest.raises(ValueError, match='requires rehearsal'):
        runner.execute(a.stable_job(ext.KIND, c, 'v3_tables', 0))


@pytest.mark.parametrize('pull', [False, True])
def test_launch_binds_only_one_root_and_latched_round(tmp_path, monkeypatch, pull):
    from v3 import production_runner as runner, multihost_a11 as multi
    original, run, candidate, projection, inventory, *_ = toy_original(tmp_path)
    path, root = tmp_path / 'plan.json', tmp_path / 'round'
    plan = ext.prepare(original, run, candidate, projection, inventory, path, rehearsal=True)
    if pull:
        plan = multi.freeze(plan, a.read(projection), code_commit='toy')
        a.atomic_json(path, a.seal(plan))
    monkeypatch.setattr(runner, 'validate_spec', lambda *args: None)
    monkeypatch.setattr(runner, 'configuration_test', lambda *args, **kw: (_ for _ in ()).throw(RuntimeError('synthetic interruption')))
    settings = dict(profile='local', cpu_budget=2, mode='normal', workers=1, threads=1)
    if pull:
        multi.prepare(path, root, settings)
    else:
        with pytest.raises(RuntimeError, match='synthetic interruption'):
            runner.launch(path, root, settings)
    record = a.unseal(a.read(tmp_path / 'plan.round.json'))
    assert record['root'] == str(root.resolve()) and record['spec_hash'] == a.digest(plan)
    launch = multi.prepare if pull else runner.launch
    with pytest.raises(ValueError, match='another root'):
        launch(path, tmp_path / 'fresh_root', settings)
    copied = tmp_path / 'copied_plan.json'; a.atomic_json(copied, a.seal(plan))
    with pytest.raises(ValueError, match='another root'):
        launch(copied, tmp_path / 'copied_root', settings)
    ext.latch_round_halt(root, 'synthetic nondeterminism')
    with pytest.raises(ValueError, match='round spent'):
        launch(path, root, settings)
    with pytest.raises(ValueError, match='another root'):
        launch(path, tmp_path / 'fresh_root', settings)


def registered_prepare_inputs(tmp_path, monkeypatch):
    """Registered preparation on synthetic original records and projection only."""
    args = toy_original(tmp_path)[:5]
    original = list(ext.original_inputs(*args[:3], registered=False))
    original[0] = deepcopy(original[0])
    original[0].pop('settings_override')
    monkeypatch.setattr(ext, 'original_inputs', lambda *args, **kw: tuple(original))
    monkeypatch.setattr(a, 'verify_registration', lambda *args, **kw: None)
    monkeypatch.setattr(ext, 'PROJECTION_FILE_SHA256', a.file_hash(args[3]))
    monkeypatch.setattr(ext, 'PROJECTION_SEAL', a.read(args[3])['sha256'])
    target = tmp_path / 'synthetic_nominal.json'
    monkeypatch.setattr(ext, 'TARGET', target.relative_to(a.SIMULATION).as_posix())
    return args, target


@pytest.mark.parametrize('stage', ['prepared', 'local', 'pull', 'halted'])
def test_registered_prepare_reserves_one_family_round(tmp_path, monkeypatch, stage):
    from v3 import production_runner as runner, multihost_a11 as multi
    args, target = registered_prepare_inputs(tmp_path, monkeypatch)
    path, root = tmp_path / 'first.json', tmp_path / 'first_root'
    registration = {'commit': a.A13_COMMIT}
    plan = ext.prepare(*args, path, registration=registration)
    anchor = target.with_suffix('.a13_round.json')
    record = a.unseal(a.read(anchor))
    assert ext.round_record_path(plan) == anchor and ext.validate_plan(plan) == plan
    assert record['plan_hash'] == plan['plan_hash'] and record['prepared_plan_path'] == str(path)
    assert record['root'] is None and record['spec_hash'] is None and record['halt'] is None
    monkeypatch.setattr(runner, 'validate_spec', lambda *args: None)
    monkeypatch.setattr(runner, 'configuration_test', lambda *args, **kw: (_ for _ in ()).throw(RuntimeError('synthetic interruption')))
    settings = dict(profile='local', cpu_budget=2, mode='normal', workers=1, threads=1)
    if stage == 'pull':
        plan = multi.freeze(plan, a.read(args[3]), code_commit='toy')
        path = tmp_path / 'pull.json'; a.atomic_json(path, a.seal(plan))
        multi.prepare(path, root, settings)
    elif stage in ('local', 'halted'):
        with pytest.raises(RuntimeError, match='synthetic interruption'):
            runner.launch(path, root, settings)
    if stage != 'prepared':
        record = a.unseal(a.read(anchor))
        assert record['root'] == str(root) and record['spec_hash'] == a.digest(plan)
        with pytest.raises(ValueError, match='another root'):
            ext.begin_round(plan, path, tmp_path / 'fresh_root')
    if stage == 'halted':
        ext.latch_round_halt(root, 'synthetic nondeterminism')
        with pytest.raises(ValueError, match='round spent'):
            ext.begin_round(plan, path, root)
    before = anchor.read_bytes()
    second_path = tmp_path / 'elsewhere' / 'second.json'
    # Identical plans also cannot acquire a second preparation filename.
    with pytest.raises(ValueError, match='another output'):
        ext.prepare(*args, second_path, registration=registration)
    # A changed plan hash cannot replace the reserved family round.
    with pytest.raises(ValueError, match='another plan'):
        ext.prepare(*args, second_path, registration=registration, wall_hours=17.)
    assert not second_path.exists() and anchor.read_bytes() == before


@pytest.mark.parametrize('no_launch', [False, True])
def test_registered_second_plan_cannot_publish(tmp_path, monkeypatch, no_launch):
    args, target = registered_prepare_inputs(tmp_path, monkeypatch)
    path, root = tmp_path / 'first.json', tmp_path / 'first_root'
    plan = ext.prepare(*args, path, registration={'commit': a.A13_COMMIT})
    round_evidence(plan, root, plan_path=path)
    ext.latch_round_halt(root, 'synthetic nondeterminism')
    anchor = ext.round_record_path(plan)
    before = anchor.read_bytes()
    second = deepcopy(plan)
    second.update(wall_seconds=plan['wall_seconds'] + 1, launch_allowed=not no_launch)
    def rehash():
        second['plan_hash'] = ext.plan_hash(second)
        second['jobs'] = [a.stable_job(ext.KIND, dict(c, plan_hash=second['plan_hash']), 'v3_tables', i)
                          for i, c in enumerate(second['job_skeletons'])]
    rehash()
    assert ext.validate_plan(second) == second
    fresh = tmp_path / 'second_root'
    # Even forged completion evidence for a fresh plan/root cannot supersede the family anchor.
    a.atomic_json(fresh / 'identity.json', dict(spec_hash=a.digest(second), code_hash=second['code_hash']))
    a.atomic_json(fresh / 'launches.json', [{'complete': True}])
    a.atomic_json(fresh / ext.PHASE / 'nondeterminism_check.json', dict(matched=True, checked=second['jobs'][0]['id']))
    with pytest.raises(ValueError, match='round plan mismatch'):
        ext.publish(second, fresh, target, registered=True)
    if not no_launch:
        with pytest.raises(ValueError, match='recorded root'):
            ext.publish(plan, fresh, target, registered=True)
    second['round_record_path'] = str(tmp_path / 'second.round.json')
    rehash()
    with pytest.raises(ValueError, match='family anchor'):
        ext.publish(second, fresh, target, registered=True)
    assert not target.exists() and anchor.read_bytes() == before


def test_rehearsal_rounds_unaffected_by_registered_family_halt(tmp_path, monkeypatch):
    args, target = registered_prepare_inputs(tmp_path, monkeypatch)
    path, root = tmp_path / 'registered.json', tmp_path / 'registered_root'
    registered = ext.prepare(*args, path, registration={'commit': a.A13_COMMIT})
    ext.begin_round(registered, path, root)
    ext.latch_round_halt(root, 'synthetic nondeterminism')
    anchor = target.with_suffix('.a13_round.json')
    before = anchor.read_bytes()
    for name in ('rehearsal_one', 'rehearsal_two'):
        path, root = tmp_path / (name + '.json'), tmp_path / name
        plan = ext.prepare(*args, path, rehearsal=True)
        assert ext.round_record_path(plan) == path.with_suffix('.round.json')
        assert all(not ext.RESERVED[0] <= r['seed'] < ext.RESERVED[1] for r in plan['seed_manifest'])
        round_evidence(plan, root, plan_path=path)
        assert not ext.publication_round(plan, root)
    assert anchor.read_bytes() == before


@pytest.mark.parametrize('defect,match', [('unrecorded', 'recorded round'), ('root', 'recorded root'),
    ('identity', 'identity mismatch'), ('incomplete', 'not complete'), ('last_incomplete', 'not complete'),
    ('unchecked', 'passed nondeterminism'), ('failed_check', 'passed nondeterminism')])
def test_publish_requires_recorded_complete_checked_round(tmp_path, defect, match):
    original, run, candidate, projection, inventory, *_ = toy_original(tmp_path)
    plan = ext.prepare(original, run, candidate, projection, inventory, tmp_path / 'plan.json', rehearsal=True)
    root = tmp_path / 'round'
    if defect != 'unrecorded':
        round_evidence(plan, root, complete=defect != 'incomplete', checked=defect != 'unchecked')
    if defect == 'root': root = tmp_path / 'unrecorded_root'
    if defect == 'identity': a.atomic_json(root / 'identity.json', dict(spec_hash='wrong', code_hash=plan['code_hash']))
    if defect == 'last_incomplete': a.atomic_json(root / 'launches.json', [dict(complete=True), dict(complete=False)])
    if defect == 'failed_check': a.atomic_json(root / ext.PHASE / 'nondeterminism_check.json', dict(matched=False, checked=plan['jobs'][0]['id']))
    target = tmp_path / 'unpublished.json'
    with pytest.raises(ValueError, match=match):
        ext.publish(plan, root, target, registered=False)
    assert not target.exists()


@pytest.mark.parametrize('stage', ['a4', 'a5'])
@pytest.mark.parametrize('commit', [a.A14_COMMIT, a.A14_COMMIT[:8], a.A13_COMMIT, a.A13_COMMIT[:8], 'historical'])
def test_publication_current_pins_stay_strict(tmp_path, monkeypatch, stage, commit):
    from v3 import table_labels_a5 as a5, table_validation_a4 as a4, tables_a10
    # The unset successor state: the A14 pin is the current one.
    monkeypatch.setattr(a, 'STAGE2_COMMIT', None)
    monkeypatch.setattr(a, 'STAGE2_AMENDMENT_MARKER', None)
    calls = []
    def verify(*args, **kwargs):
        calls.append(kwargs)
        raise RuntimeError('pin checked before outputs')
    monkeypatch.setattr(a, 'verify_registration', verify)
    monkeypatch.setattr(a5, 'verify_registration', verify)
    monkeypatch.setattr(tables_a10, 'verify_estimation_source', lambda *args, **kw: None)
    plan = dict(registered=True, registration={'commit': commit}, instrument=tables_a10.NOMINAL,
                calibration_path='unused', jobs=[])
    with pytest.raises(RuntimeError, match='pin checked'):
        if stage == 'a4': a4.publish(plan, tmp_path, tmp_path, {}, tmp_path / 'never.json')
        else: a5.publish(plan, tmp_path, tmp_path, tmp_path, {}, tmp_path / 'never.json')
    assert calls[0]['historical'] == (commit not in (a.A14_COMMIT, a.A14_COMMIT[:8]))


@pytest.mark.parametrize('halted', [False, True])
def test_registered_publication_admission_receipt_loader_and_run(tmp_path, monkeypatch, halted):
    """Registered code paths on synthetic records, never registered trajectories."""
    from v3 import tables_a10, table_labels_a5 as labels
    from v3.integration import V3Model
    from v3.instrument import declaration
    original, run, candidate, projection, inventory, source, cal_path, *_ = toy_original(tmp_path)
    plan_path, root = tmp_path / 'plan.json', tmp_path / 'round'
    plan = ext.prepare(original, run, candidate, projection, inventory, plan_path, rehearsal=True)
    old_plan, old_doc, old_sidecar, old_receipt, calibration = ext.original_inputs(original, run, candidate, registered=False)
    payload = deepcopy(a.unseal(old_doc)); rows = {k: a.unseal(v) for k, v in payload['rows'].items()}
    details = deepcopy(old_sidecar['rows'])
    # Choose a real eligible row from the source job.
    selected = next(iter(plan['jobs'][0]['config']['eligible_rows']))
    plan['E'] = 1
    for record in plan['eligibility']:
        record['eligible'] = record['row'] == selected and record['setting'] == 'primary'
    plan['impossible_rows'] = {selected: plan['impossible_rows'][selected]}
    plan['job_skeletons'] = [c for c in plan['job_skeletons'] if selected in c['eligible_rows']]
    for c in plan['job_skeletons']:
        c['eligible_rows'] = {selected: c['eligible_rows'][selected]}
    for key, row in rows.items():
        if key != selected:
            row.update(status='estimated', primary_status='estimated')
            row.pop('reason', None)
    admitted = rows[selected]
    model_args = dict(n_agents=16, carrying_capacity=160, reproduction_rate=.064,
                      alpha=admitted['scoring']['alpha'], kappa=admitted['scoring']['kappa'], capability=1., successor_capability=None,
                      rules=execution_policy_class()[:3], rollout_steps=1, instrument=tables_a10.NOMINAL,
                      calibration=calibration)
    probe_model = V3Model(**model_args)
    assert probe_model.kernel_hash == admitted['kernel_hash'] and probe_model.calibration_hash == admitted['calibration_hash']
    endpoint = probe_model.evaluate().terminal.summary_bins(probe_model.capacity)
    for i, rule in enumerate(probe_model.rules[:2]):
        row = deepcopy(admitted)
        row.update(rule_id=rule.rule_id, rule_hash=a.digest(rule.__dict__), status='estimated', primary_status='estimated')
        row.pop('reason', None)
        row['continuation']['entries'] = [{'bin': endpoint[i].tolist(), 'value': 0., 'error': 10.}]
        key = row_key(row); rows[key] = row
        details.append(dict(deepcopy(details[0]), row=key, route='plain', setting='primary', status='estimated'))
    i = 0
    while len(rows) < 3000:
        row = deepcopy(admitted); row.update(kernel_hash='synthetic-extra-' + str(i), status='estimated', primary_status='estimated')
        row.pop('reason', None)
        key = row_key(row); rows[key] = row
        details.append(dict(deepcopy(details[0]), row=key, setting='primary', status='estimated'))
        i += 1
    payload['rows'] = {k: a.seal(r) for k, r in rows.items()}
    payload['manifest'].update(required_row_keys=sorted(rows), complete_family=True, sensitivity_status='passed')
    payload['manifest_hash'] = a.digest(payload['manifest'])
    synthetic_doc = a.seal(payload)
    synthetic_sidecar = dict(old_sidecar, rows=details, table_seal_sha256=synthetic_doc['sha256'])
    a.atomic_json(candidate, synthetic_doc)
    a.atomic_json(candidate.with_suffix('.cell_results.json'), a.seal(synthetic_sidecar))
    # Only the original-input verifier and the clean committed-pin requirement
    # are substituted. Plan, round, stage, assembly, admission, loader, receipt
    # and controller validation below use their production implementations.
    monkeypatch.setattr(ext, 'original_inputs', lambda *args, **kw: (old_plan, synthetic_doc, synthetic_sidecar, old_receipt, calibration))
    monkeypatch.setattr(a, 'verify_registration', lambda *args, **kw: None)
    target = tmp_path / 'registered_mode_synthetic.json'
    monkeypatch.setattr(ext, 'TARGET', target.relative_to(a.SIMULATION).as_posix())
    plan.update(registered=True, registered_a10=True, non_registered_rehearsal=False,
                round_record_path=str(target.with_suffix('.a13_round.json')),
                registration={'commit': a.A13_COMMIT}, candidate_file_sha256=a.file_hash(candidate),
                candidate_sidecar_sha256=a.file_hash(candidate.with_suffix('.cell_results.json')))
    manifest = ext.seed_manifest([c['a1_job'] for c in plan['job_skeletons']], plan['R_max'], plan['forbidden_seeds'])
    plan['seed_manifest'] = manifest
    plan['seed_check'] = ext.check_seed_manifest(manifest, plan['forbidden_seeds'])
    for c in plan['job_skeletons']:
        c.update(non_registered_rehearsal=False, full_seed_manifest=manifest,
                 stream_seeds=[r['seed'] for r in manifest if r['source_job_id'] == c['a1_job']['id']])
    plan['plan_hash'] = ext.plan_hash(plan)
    plan['jobs'] = [a.stable_job(ext.KIND, dict(c, plan_hash=plan['plan_hash']), 'v3_tables', i)
                    for i, c in enumerate(plan['job_skeletons'])]
    ext.reserve_registered_round(plan, plan_path)
    a.atomic_json(plan_path, a.seal(plan))
    round_evidence(plan, root, plan_path=plan_path, complete=not halted, checked=not halted)
    if halted:
        ext.latch_round_halt(root, 'synthetic scientific halt')
    else:
        for job in plan['jobs']:
            c = job['config']
            replicas = [dict(replicate=r, seed=ext.ext_seed(c['a1_job']['seed'], r), count=c['trajectory_count'], settings={},
                             rows={k: [[0., 0]] * c['trajectory_count'] for k in c['eligible_rows']})
                        for r in range(4, 4 + c['R_max'])]
            durable(root / ext.PHASE, job, dict(plan_hash=plan['plan_hash'], a1_job_id=c['a1_job']['id'], replicates=replicas))
    summary = ext.publish(plan, root, target, registered=True)
    assert summary['outcome'] == ('scientific_halt' if halted else 'completed')
    loaded = ProductionTables(target, calibration_hash=calibration['sha256'], registered=True)
    residual = [r for r in loaded.rows.values() if r['status'] == 'not_estimable']
    assert len(loaded.rows) == 3000 and len(residual) == 1
    assert all(not r['a13']['certified_by_extension'] for r in residual)
    receipt = a.unseal(a.read(target.with_suffix('.compatibility.json')))
    assert receipt['plan_hash'] == old_receipt['plan_hash'] and receipt['stream_seeds'] == old_receipt['stream_seeds']
    assert 'extension_stream_seeds' not in receipt
    labels_doc = dict(schema='v3-A5-label-1', code_hash=a.code_identity(),
                      a4_family=dict(table_seal_sha256=loaded.document_hash, family_file_sha256=a.file_hash(target)),
                      rows=[dict(row_key=k, scoring=r['scoring'], cells=[dict(cell=int(cell), status='unresolved', label=labels.label_for('unresolved'))
                             for cell in cv.fine_codes([e['bin'] for e in r['continuation']['entries']])])
                            for k, r in loaded.rows.items() if r['route'] == 'fv' and r['status'] == 'estimated'])
    labels_path = tmp_path / 'toy_labels.json'; a.atomic_json(labels_path, a.seal(labels_doc))
    tables_a10.finalize_receipt(target, labels_path)
    loaded = ProductionTables(target, calibration_hash=calibration['sha256'], registered=True)
    loaded.require_a10(declaration(tables_a10.NOMINAL))
    model = V3Model(**model_args, tables=loaded)
    evaluated = model.evaluate()
    assert evaluated.lookup.unavailable_reasons[2] == admit.MISSING and not evaluated.available[2]
    step = model.step()
    assert step['unavailable_rules'][model.rules[2].rule_id] == admit.MISSING
    incidence = admit.summarize(model.a13_decisions)
    branch = 'survival_first' if model.a13_decisions[0]['branch'] == 'survival_first' else 'ordinary_allocation'
    assert incidence[branch]['denominator'] == incidence[branch]['numerator'] == 1


def test_a4_failed_part2_is_sealed_before_publication(tmp_path, monkeypatch):
    from v3 import table_validation_a4 as a4, tables_a10, calibration as cal
    original, run, candidate, _, _, source, cal_path, *_ = toy_original(tmp_path)
    plan = a.unseal(a.read(original)); plan['registration'] = {'commit': a.A13_COMMIT}
    monkeypatch.setattr(a4, 'registered_publish_guard', lambda p: None)
    monkeypatch.setattr(a4, '_recompute_plan_hash', lambda p: p['plan_hash'])
    monkeypatch.setattr(tables_a10, 'verify_estimation_source', lambda *args, **kw: None)
    monkeypatch.setattr(a, 'verify_registration', lambda *args, **kw: None)
    monkeypatch.setattr(cal, 'validate_calibration', lambda document, **kw: a.unseal(document))
    target = tmp_path / 'refused.json'
    # The toy fixture published this run root non-registered; the registered
    # attempt below is the first publication of this run root under its pin.
    for suffix in ('.json', '.cell_results.json', '.compatibility.json'):
        candidate.with_suffix(suffix).unlink()
    with pytest.raises(ValueError, match='cap exceeded'):
        a4.publish(plan, run, source, a.read(a.SIMULATION / cal_path), target, registered=True)
    record = a.unseal(a.read(run / 'a13_admission_check.json'))
    assert record['outcome'] == 'refused' and record['residual_count'] > record['cap']
    assert all(k not in str(record) for k in ('n_traj', 'visits', 'width', 'cell_tests', 'n_star'))
    # A16's coordinated-change clause: the refused candidate, its cell results
    # and its compatibility receipt are preserved in the run root; the target is
    # never touched, and the refused manifest carries no admission binding.
    assert not target.exists()
    refused = a.unseal(a.read(candidate))
    assert 'a13_admission' not in refused['manifest'] and refused['fixture'] is False
    sidecar = a.unseal(a.read(candidate.with_suffix('.cell_results.json')))
    receipt = a.unseal(a.read(candidate.with_suffix('.compatibility.json')))
    assert sidecar['table_seal_sha256'] == receipt['table_seal_sha256'] == a.read(candidate)['sha256']
    assert receipt['table_file_sha256'] == a.file_hash(candidate) and receipt['plan_hash'] == plan['plan_hash']
    assert ext.original_inputs(original, run, candidate, registered=False)[0]['plan_hash'] == plan['plan_hash']


def test_report_separates_extension_cells_and_preserves_ordinary_report(tmp_path):
    from v3 import table_validation_a4 as a4
    original, run, candidate, *_ = toy_original(tmp_path)
    out = tmp_path / 'report.json'
    a4.report(candidate, out)
    before = a.read(out)
    assert 'a13_extension' not in before
    side = a.unseal(a.read(candidate.with_suffix('.cell_results.json')))
    entry = next(d for d in side['rows'] if d['route'] == 'plain')
    entry['cell_tests'].append(dict(a13_extension=True, cell=999, eb='certified', visit_weighted_ok=True, n_traj=9999))
    a.atomic_json(candidate.with_suffix('.cell_results.json'), a.seal(side))
    receipt = a.unseal(a.read(candidate.with_suffix('.compatibility.json')))
    receipt['cell_results_sha256'] = a.file_hash(candidate.with_suffix('.cell_results.json'))
    a.atomic_json(candidate.with_suffix('.compatibility.json'), a.seal(receipt))
    a4.report(candidate, out)
    after = a.read(out)
    assert after.pop('a13_extension') == [dict(row=entry['row'], setting=entry['setting'], cell=999, eb='certified', visit_weighted_ok=True)]
    assert a.canonical(before) == a.canonical(after)


def test_pull_round_requires_durable_completion_and_matching_check(tmp_path):
    from v3 import multihost_a11 as multi
    original, run, candidate, projection, inventory, *_ = toy_original(tmp_path)
    path, root = tmp_path / 'plan.json', tmp_path / 'round'
    plan = ext.prepare(original, run, candidate, projection, inventory, path, rehearsal=True)
    plan = multi.freeze(plan, a.read(projection), code_commit='synthetic')
    a.atomic_json(path, a.seal(plan))
    round_evidence(plan, root)
    check = a.read(root / ext.PHASE / 'nondeterminism_check.json')
    for state in (dict(complete=False, checks={ext.PHASE: check}), dict(complete=True, checks={})):
        a.atomic_json(root / 'pull_state.json', a.seal(state))
        with pytest.raises(ValueError, match='completed pull-dispatch check'):
            ext.publication_round(plan, root)
    a.atomic_json(root / 'pull_state.json', a.seal(dict(complete=True, checks={ext.PHASE: check})))
    assert ext.publication_round(plan, root) is False
    a.atomic_json(root / 'pull_state.json', a.seal(dict(complete=True, checks={ext.PHASE: check}, halt='synthetic halt')))
    assert ext.publication_round(plan, root) is True
    assert a.unseal(a.read(tmp_path / 'plan.round.json'))['halt']
