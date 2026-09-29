"""Synthetic fixtures for A1 diagnosis and the proposed, unlaunched A3 repair."""
from copy import deepcopy
import pytest
from v3.artifacts import digest, stable_job, verify_registration
from v3.a1_screen_diagnosis import summarize
from v3.table_repair_a3 import (A1_FILE_SHA256, enlarged, prepare, numerical_contrast,
                               assemble_rows, selected_pairs)
from v3.production_tables import row_key


def row(rule='balanced', status='estimated', mean=0.):
    return {'rule_id': rule, 'kernel_hash': 'fixture-kernel', 'calibration_hash': 'fixture-cal',
            'scoring': {'alpha': 1., 'capability': 1., 'kappa': 8.}, 'status': status,
            'reason': None, 'flow_range': 100., 'screens': {'continuation': status == 'estimated'},
            'lambda_f': {'mean': mean, 'replicates': [mean] * 6},
            'continuation': {'entries': [{'bin': [0] * 6, 'value': 0., 'error': 100.}]}}


def inputs():
    from v3.study import table_jobs
    jobs = table_jobs('fixture-calibration.json')
    spec = {'jobs': jobs}
    audit = {'source_file_sha256': A1_FILE_SHA256, 'source_payload_sha256': 'fixture-payload',
             'source_manifest_sha256': digest(spec), 'source_code_hash': 'fixture-source',
             'calibration_sha256': 'fixture-cal',
             'service': {'started_epoch': 0., 'finished_epoch': 20000.},
             'rows': [{'job_id': j['id'], 'limits': {'fixture': 1.}, 'excess': {'fixture': float(i)},
                       'rule': j['config']['rule_id'], 'rr': j['config']['kernel']['reproduction_rate'],
                       'status': 'not_estimable' if j['config']['rule_id'] == 'w1_p1_t1_g3' and j['config']['kernel']['reproduction_rate'] == .066 else 'estimated'} for i, j in enumerate(jobs)],
             'jobs': [{'id': j['id'], 'output_sha256': 'fixture-' + j['id']} for j in jobs]}
    return audit, spec


def test_repair_selection_is_kernel_closed_and_renews_all_nine_pairs():
    audit, source = inputs()
    pairs = selected_pairs(audit)
    assert len(pairs) == 10
    result = prepare(audit, source, 'fixture-calibration.json')
    assert len(result['jobs']) == 28  # nine complete triples plus one kernel
    assert result['publication'] is None
    assert result['registration'] is None
    with pytest.raises((ValueError, RuntimeError)):
        verify_registration(result['registration'])
    assert result['wall_seconds'] < 86400 - 20000
    old = {j['id']: j for j in source['jobs']}
    for job in result['jobs']:
        parent = old[job['config']['source_job_id']]
        assert job['seed'] != parent['seed']
        assert job['config']['scoring'] == parent['config']['scoring']
        assert job['config']['settings'] == enlarged(parent['config']['settings'])
    # The profile's config and configs[-1] used to alias one dictionary.
    profile = result['configuration']['table']
    assert profile['config']['settings']['particles'] == 256 * 8
    assert profile['configs'][-1]['settings']['particles'] == 256 * 8


def test_review_manifest_deterministic_and_source_frozen():
    audit, source = inputs()
    before = deepcopy((audit, source))
    a = prepare(audit, source, 'cal.json')
    b = prepare(audit, source, 'cal.json')
    assert a == b and (audit, source) == before
    audit['source_file_sha256'] = 'wrong'
    with pytest.raises(ValueError, match='reviewed A1'):
        prepare(audit, source, 'cal.json')


def test_lengths_groups_and_sensitivity_ratios_unchanged():
    from v3.offline_estimator import settings_for
    a, b, c = [enlarged(settings_for(s)) for s in ('primary', 'double_population', 'double_length')]
    assert a == {'groups': 6, 'runs_per_group': 512, 'particles': 2048, 'burn': 1024, 'measure': 2048}
    assert b['particles'] == 2 * a['particles'] and b['runs_per_group'] == 2 * a['runs_per_group']
    assert c['burn'] == 2 * a['burn'] and c['measure'] == 2 * a['measure']
    assert a['groups'] == b['groups'] == c['groups'] == 6


@pytest.mark.parametrize('difference,passed', [(0., True), (5., True), (5.000001, False)])
def test_contrast_boundary_preserves_existing_threshold(difference, passed):
    assert numerical_contrast(row(), row(mean=difference))['passed'] == passed


def family():
    originals = {}
    for name in ('primary', 'double_population', 'double_length'):
        originals[name] = {'job': {'config': {'setting_name': name, 'kernel': {'reproduction_rate': .064}}},
                           'result': {'rows': [row()]}}
    return originals, deepcopy(originals), {'replacements': {k: 'new-' + k for k in originals}}


def test_complete_repair_passes_without_mutating_original_outputs():
    old, new, plan = family()
    before = deepcopy((old, new))
    rows, passed = assemble_rows(old, new, plan)
    assert passed and rows[row_key(row())]['status'] == 'estimated'
    assert (old, new) == before


@pytest.mark.parametrize('setting', ['primary', 'double_population', 'double_length'])
def test_failed_replacement_is_never_replaced_by_old_passing_value(setting):
    old, new, plan = family()
    new[setting]['result']['rows'][0] = row(status='not_estimable')
    rows, passed = assemble_rows(old, new, plan)
    assert rows[row_key(row())]['status'] == 'not_estimable'
    if setting != 'primary':
        assert not passed


def test_failed_old_new_contrast_keeps_gate_closed():
    old, new, plan = family()
    new['primary']['result']['rows'][0] = row(mean=10.)
    rows, _ = assemble_rows(old, new, plan)
    assert rows[row_key(row())]['status'] == 'not_estimable'
    assert not rows[row_key(row())]['repair_original_contrast']['passed']


@pytest.mark.parametrize('defect', ['missing', 'extra', 'context'])
def test_incomplete_or_changed_replacement_refused(defect):
    old, new, plan = family()
    if defect == 'missing':
        del new['double_length']
    elif defect == 'extra':
        new['extra'] = new['primary']
    else:
        new['primary']['result']['rows'][0]['scoring']['alpha'] = .5
    with pytest.raises(ValueError):
        assemble_rows(old, new, plan)


def test_sparse_residual_remains_binding_with_high_coverage():
    import numpy as np
    from v3.continuation import fit_transitions
    # One rare source has four training visits and one held-out visit.
    # Additional common-source transitions cannot repair its residual.
    before = np.zeros((100, 6, 6), dtype=int)
    after = before.copy()
    before[0, :4, 0] = 1
    before[0, 4, 0] = 1
    after[0, :4, 0] = 1
    rewards = np.zeros((100, 6))
    rewards[0, :4] = 100.
    c = fit_transitions(before, after, rewards, np.zeros_like(rewards, bool), np.arange(6), 0., 100.)
    assert c['heldout_coverage'] == 1.
    assert c['bellman_residual_empirical'] > .05 * 100.
    assert c['largest_residual_bins'][0]['heldout_visits'] == 1


def test_existing_a2_compatibility_dependencies_still_match():
    from v3.table_compatibility import verified_record
    from v3.calibration_compatibility import dependency_hash
    from v3.artifacts import SIMULATION
    record = verified_record()
    assert record['producer_commit'].startswith('34ffbfe9')
    # A4 re-established the boundary: production_tables.py and production_runner.py
    # were re-pinned to their A4 hashes, and the a4 note records the extension.
    # verified_record already raises on any unapproved dependency change, so its
    # success proves every pinned boundary and unchanged dependency still matches.
    assert 'a4' in record
    boundary = record['approved_boundary_sha256']
    for name in ('v3/production_tables.py', 'v3/production_runner.py'):
        assert dependency_hash(SIMULATION / name) == boundary[name]


def test_exposure_refuses_registered_manifest_before_reading_outputs(tmp_path):
    from v3.a1_screen_diagnosis import exposure
    from v3.artifacts import atomic_json, seal
    atomic_json(tmp_path / 'manifest.json', seal({'registered': True, 'jobs': []}))
    with pytest.raises(ValueError, match='before opening outputs'):
        exposure({'published': []}, tmp_path)


@pytest.mark.parametrize('defect', [None, 'bad_new_row', 'missing_record', 'changed_selection', 'changed_output',
                                  'restamped_table', 'retained', 'new_producer', 'extra_replacement',
                                  'producer_commit', 'no_receipt', 'failed_screen', 'later_commit'])
def test_publisher_verifies_both_durable_families(tmp_path, monkeypatch, defect):
    """Synthetic table artifacts only. No estimator or registered run executes."""
    import v3.table_repair_a3 as repair
    import v3.calibration as calibration
    from v3.artifacts import atomic_json, seal, file_hash, code_identity
    from v3.offline_estimator import settings_for
    source_root, run_root = tmp_path / 'fixture_source', tmp_path / 'fixture_repair'
    jobs, audit_rows = [], []
    for rule, rr, names in [('balanced', .064, ('primary', 'double_population', 'double_length')),
                            ('w1_p1_t1_g3', .066, ('primary',))]:
        for name in names:
            config = {'phase': 'table', 'rule_id': rule, 'kernel': {'reproduction_rate': rr},
                      'setting_name': name, 'settings': settings_for(name), 'route': 'auto',
                      'scoring': [row()['scoring']], 'calibration_path': 'fixture-cal.json'}
            job = stable_job('table', config, 'v3_tables', 0)
            jobs.append(job)
            audit_rows.append({'rule': rule, 'rr': rr, 'status': 'not_estimable' if rule != 'balanced' else 'estimated',
                               'job_id': job['id'], 'limits': {'fixture': 1.}, 'excess': {'fixture': 0.}})
    source_spec = {'jobs': jobs}
    atomic_json(source_root / 'tables_A1_manifest.json', seal(source_spec))
    source_publication = seal({'manifest': {'required_row_keys': [row_key(row(r)) for r in ('balanced', 'w1_p1_t1_g3')]}})
    atomic_json(source_root / 'v3_rerun_tables_A1.json', source_publication)
    source_sha = file_hash(source_root / 'v3_rerun_tables_A1.json')
    monkeypatch.setattr(repair, 'A1_FILE_SHA256', source_sha)
    # These two validations concern real committed pins/calibrations, which
    # fixtures cannot supply. All job/output/record checks run unmocked.
    monkeypatch.setattr(repair, 'verify_registration', lambda pin: None)
    monkeypatch.setattr(calibration, 'validate_calibration', lambda *a, **k: None)
    def save(root, job, code, failed=False):
        r = row(job['config']['rule_id'], 'not_estimable' if failed else 'estimated')
        out = {'job': job, 'code_hash': code, 'result': {'rows': [r], 'fixture_calibration': False, 'calibration_hash': 'fixture-cal'}}
        path = root / 'outputs' / (job['id'] + '.json')
        atomic_json(path, out)
        atomic_json(root / 'records' / (job['id'] + '.json'), {'status': 'complete', 'job': job, 'code_hash': code, 'output_hash': file_hash(path)})
        return file_hash(path)
    hashes = {j['id']: save(source_root / 'tables_A1/table', j, 'fixture-original') for j in jobs}
    audit = {'source_file_sha256': source_sha, 'source_payload_sha256': source_publication['sha256'],
             'source_manifest_sha256': digest(source_spec), 'source_code_hash': 'fixture-original',
             'calibration_sha256': 'fixture-cal', 'service': {'started_epoch': 0., 'finished_epoch': 20000.},
             'rows': audit_rows, 'jobs': [{'id': k, 'output_sha256': v} for k, v in hashes.items()]}
    # Make the source failure agree with the frozen selection and hashes.
    j = jobs[-1]
    audit['jobs'][-1]['output_sha256'] = save(source_root / 'tables_A1/table', j, 'fixture-original', True)
    spec = prepare(audit, source_spec, 'fixture-cal.json', {'fixture': True}, source_root=source_root)
    # Same provenance validator, with a clearly synthetic frozen policy.
    import v3.table_compatibility_a3 as compatibility
    policy = {k: spec['repair'][k] for k in ('source_file_sha256', 'source_payload_sha256', 'source_manifest_sha256',
               'source_code_hash', 'calibration_sha256', 'source_outputs', 'dispatch_order')}
    policy.update(replacement_source_ids=list(spec['repair']['replacements']), maximum_remaining_seconds=spec['wall_seconds'],
                  source_config_hashes={j['id']: compatibility.config_identity(j['config']) for j in jobs},
                  canonical_calibration_path='fixture-cal.json',
                  replacement_jobs={j['config']['source_job_id']:{'id':j['id'],'seed':j['seed']} for j in spec['jobs']})
    monkeypatch.setattr(compatibility, 'policy', lambda: policy)
    monkeypatch.setattr(compatibility, 'FAMILY_ROOT', tmp_path/'fixture_families')
    for i, j in enumerate(spec['jobs']):
        save(run_root / 'table', j, code_identity(), defect == 'bad_new_row' and i == 0)
    first = spec['jobs'][0]
    if defect == 'missing_record':
        (run_root / 'table/records' / (first['id'] + '.json')).unlink()
    elif defect == 'changed_selection':
        spec['repair']['pairs'].pop()
    elif defect == 'changed_output':
        atomic_json(run_root / 'table/outputs' / (first['id'] + '.json'), {'fixture': 'tampered'})
    call = lambda: repair.publish(spec, run_root, source_root, {'sha256': 'fixture-cal'}, tmp_path / 'fixture_publication.json')
    if defect in ('bad_new_row', 'missing_record', 'changed_selection', 'changed_output'):
        with pytest.raises((ValueError, RuntimeError)):
            call()
        assert not (tmp_path / 'fixture_publication.json').exists()
    else:
        document = call()
        assert document['payload']['manifest']['source_family']['code_hash'] == 'fixture-original'
        assert len(document['payload']['rows']) == 2
        if defect:
            from v3.artifacts import unseal
            from v3.production_tables import ProductionTables
            target = tmp_path / 'fixture_publication.json'
            receipt_path = target.with_suffix('.compatibility.json')
            receipt = unseal(__import__('v3.artifacts', fromlist=['read']).read(receipt_path))
            if defect == 'later_commit':
                old_commit = receipt['producer_commit']
                monkeypatch.setattr(compatibility,'producer_commit',lambda:'f'*40)
                monkeypatch.setattr(compatibility,'producer_is_ancestor',lambda commit:commit==old_commit)
                assert not ProductionTables(target,calibration_hash='fixture-cal',registered=True).fixture
                return
            if defect == 'restamped_table':
                document['payload']['extra'] = 're-stamped'
                atomic_json(target, seal(document['payload']))
            elif defect == 'retained':
                receipt['retained_A1_outputs']['unapproved'] = '0' * 64
            elif defect == 'new_producer':
                next(iter(receipt['replacement_outputs'].values()))['code_hash'] = 'wrong'
            elif defect == 'extra_replacement':
                receipt['replacement_outputs']['unapproved'] = next(iter(receipt['replacement_outputs'].values()))
            elif defect == 'producer_commit':
                receipt['producer_commit'] = '0' * 40
            elif defect == 'failed_screen':
                document['payload']['manifest']['sensitivity_status'] = 'incomplete_or_failed'
                document['payload']['manifest_hash'] = digest(document['payload']['manifest'])
                document = seal(document['payload'])
                atomic_json(target, document)
                receipt['table_file_sha256'] = file_hash(target)
                receipt['table_seal_sha256'] = document['sha256']
            atomic_json(receipt_path, seal(receipt))
            if defect == 'no_receipt':
                receipt_path.unlink()
            with pytest.raises((ValueError, RuntimeError, FileNotFoundError)):
                ProductionTables(target, calibration_hash='fixture-cal', registered=True)


# Artifacts stay inside the authorized tree even with default pytest options.
from test_v3_paths import tmp_path
