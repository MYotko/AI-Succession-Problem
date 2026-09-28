"""D24 A3: one fixed independent repair, with no retry or screen waiver.

The unchanged runner executes a prepared manifest only after a committed
registration pin. Publication verifies both source families explicitly.
No A1 result is relabeled as an A3 worker output. Importing this module
does not change A1/A2 defaults, allocation, gates or table compatibility.
"""
import argparse
from copy import deepcopy
import math
from pathlib import Path
import numpy as np
from .artifacts import (read, unseal, seal, file_hash, digest, atomic_json,
                        code_identity, stable_job, verify_registration, SIMULATION)

A1_FILE_SHA256 = '56db71633a0f4710692e3354e3bc2fb5829286abbfa59e61609bd3f8cf6fcb3c'
POPULATION_FACTOR = 8
AMENDMENT = 'A3 adopted by D24, 2026-09-28; committed pin required'


def difficulty(audit):
    """Maximum signed excess / positive screen limit; FV survival is excluded."""
    result = {}
    for row in audit['rows']:
        ratios = [v / row['limits'][k] for k, v in row['excess'].items() if v is not None]
        if not ratios or not all(math.isfinite(v) for v in ratios):
            raise ValueError('A1 normalized excess unavailable')
        key = row['job_id']
        result[key] = max(result.get(key, -math.inf), max(ratios))
    identities = {(j['rule'], j['rr'], j['setting']): j['id'] for j in audit['jobs']
                  if all(k in j for k in ('rule', 'rr', 'setting'))}
    for contrast in audit.get('contrasts', []):
        if not contrast.get('computable'):
            raise ValueError('A1 sensitivity contrast unavailable for difficulty ordering')
        ratio = contrast['excess'] / contrast['limit']
        for name in ('primary', contrast['setting']):
            key = identities[contrast['rule'], contrast['rr'], name]
            result[key] = max(result[key], ratio)
    return result


def selected_pairs(audit):
    from .offline_estimator import SENSITIVITY_RULES, SENSITIVITY_RR
    failed = {(r['rule'], r['rr']) for r in audit['rows'] if r['status'] != 'estimated'}
    return failed | {(rule, rr) for rule in SENSITIVITY_RULES for rr in SENSITIVITY_RR}


def enlarged(settings):
    result = dict(settings)
    for name in ('particles', 'runs_per_group'):
        result[name] *= POPULATION_FACTOR
    return result


def prepare(audit, source_spec, calibration_path, registration=None, prior_seconds=773.771, source_root=None):
    """Pure manifest construction. Never launches estimation or reads reruns."""
    if audit['source_file_sha256'] != A1_FILE_SHA256 or digest(source_spec) != audit['source_manifest_sha256']:
        raise ValueError('repair source is not the reviewed A1 family')
    from .study import registered_spec
    spec = registered_spec('table', registration, calibration_path, publication_path='UNUSED')
    pairs = selected_pairs(audit)
    jobs, replacements = [], {}
    for old in source_spec['jobs']:
        c = old['config']
        if (c['rule_id'], c['kernel']['reproduction_rate']) not in pairs:
            continue
        config = deepcopy(c)
        config.update(settings=enlarged(c['settings']), calibration_path=calibration_path,
                      repair_round='A3-fixed-once-20260928', source_job_id=old['id'])
        new = stable_job('table', config, 'v3_tables', 0)
        jobs.append(new)
        replacements[old['id']] = new['id']
    spent = audit['service']['finished_epoch'] - audit['service']['started_epoch'] + prior_seconds
    scores = difficulty(audit)
    jobs.sort(key=lambda j: (-scores[j['config']['source_job_id']], j['config']['source_job_id']))
    spec.update(jobs=jobs, publication=None, wall_seconds=math.floor(86400 - spent))
    spec['completion_screen'] = {'kind': 'A3-first-failure', 'source_root': str(source_root) if source_root else None}
    # Configuration uses the enlarged populations and both routes. Its
    # short jobs are discarded. The actual launch still chooses workers.
    profile = spec['configuration']['table']
    def configuration(config):
        config = deepcopy(config)
        config['settings'] = enlarged(config['settings'])
        return config
    profile['config'] = configuration(profile['config'])
    profile['configs'] = [configuration(c) for c in profile.get('configs', [])]
    spec['repair'] = {
        'schema': 'v3-A3-repair-1', 'amendment': AMENDMENT,
        'source_file_sha256': A1_FILE_SHA256, 'source_payload_sha256': audit['source_payload_sha256'],
        'source_manifest_sha256': audit['source_manifest_sha256'], 'source_code_hash': audit['source_code_hash'],
        'calibration_sha256': audit['calibration_sha256'],
        'source_outputs': {j['id']: j['output_sha256'] for j in audit['jobs']},
        'pairs': [list(p) for p in sorted(pairs)], 'replacements': replacements,
        'population_factor': POPULATION_FACTOR, 'prior_service_seconds': spent,
        'dispatch_order': [{'source_job_id': j['config']['source_job_id'], 'maximum_normalized_excess': scores[j['config']['source_job_id']]} for j in jobs],
        'order_rule': 'descending maximum signed excess divided by limit; ascending source job ID breaks ties',
        'decision': 'one independent replacement per selected job; replace every scoring context; no best-of or retry',
        'selection_consequence': 'adaptive effort and conditional publication; empirical intervals do not acquire selective or simultaneous coverage',
        'additional_screen': 'old versus replacement Lambda_F contrast uses the existing 90-percent interval and five-percent span limit',
    }
    return spec


class CompletionScreen:
    """Parent-process screen. All completed artifacts are already hash verified."""
    def __init__(self, originals, family_policy=None, run_root=None):
        self.originals, self.outputs = originals, {}
        self.family_policy, self.run_root = family_policy, run_root

    def __call__(self, job, output):
        failure = self.evaluate(job, output)
        if failure and self.family_policy is not None:
            from .table_compatibility_a3 import record_family_failure
            record_family_failure(self.family_policy, failure, self.run_root)
        return failure

    def family_failed(self):
        from .table_compatibility_a3 import family_directory
        return self.family_policy is not None and (family_directory(self.family_policy) / 'failure.json').exists()

    def evaluate(self, job, output):
        from .production_tables import row_key
        old_id = job['config']['source_job_id']
        old_rows = {row_key(r): r for r in self.originals[old_id]['result']['rows']}
        rows = {row_key(r): r for r in output['result']['rows']}
        if set(rows) != set(old_rows) or len(rows) != len(output['result']['rows']):
            return {'reason': 'scoring contexts changed', 'job': job['id']}
        for key, row in rows.items():
            if row['status'] != 'estimated' or not row.get('screens') or not all(row['screens'].values()):
                return {'reason': 'row screen failed', 'job': job['id'], 'row': key, 'screens': row.get('screens')}
            contrast = numerical_contrast(old_rows[key], row)
            if not contrast['passed']:
                return {'reason': 'original versus replacement contrast failed', 'job': job['id'], 'row': key, 'contrast': contrast}
        self.outputs[old_id] = output
        c = job['config']
        for other in self.outputs.values():
            oc = other['job']['config']
            if (oc['rule_id'], oc['kernel']['reproduction_rate']) != (c['rule_id'], c['kernel']['reproduction_rate']):
                continue
            if (oc['setting_name'] == 'primary') == (c['setting_name'] == 'primary'):
                continue
            primary, sensitivity = (output, other) if c['setting_name'] == 'primary' else (other, output)
            reference = {row_key(r): r for r in primary['result']['rows']}
            for row in sensitivity['result']['rows']:
                key = row_key(row)
                contrast = numerical_contrast(reference[key], row)
                if not contrast['passed']:
                    return {'reason': 'sensitivity contrast failed', 'job': job['id'], 'paired_job': other['job']['id'], 'row': key, 'contrast': contrast}
        return None


def completion_screen(spec, run_root):
    from .production_runner import completed
    from .table_compatibility_a3 import validate_plan, refuse_family_failure
    p = validate_plan(spec)
    refuse_family_failure(p)
    root = Path(spec['completion_screen']['source_root'])
    plan = spec['repair']
    if file_hash(root / 'v3_rerun_tables_A1.json') != plan['source_file_sha256']:
        raise ValueError('A1 source publication changed')
    source = unseal(read(root / 'tables_A1_manifest.json'))
    if digest(source) != plan['source_manifest_sha256']:
        raise ValueError('A1 source manifest changed')
    originals = {}
    for job in source['jobs']:
        if job['id'] not in plan['replacements']:
            continue
        output = completed(root / 'tables_A1/table', job, plan['source_code_hash'])
        if output is None or file_hash(root / 'tables_A1/table/outputs' / (job['id'] + '.json')) != plan['source_outputs'][job['id']]:
            raise ValueError('A1 source job changed')
        originals[job['id']] = output
    return CompletionScreen(originals, p, run_root)


def numerical_contrast(primary, other):
    """Same arithmetic and threshold as study.assemble_tables."""
    a, b = primary.get('lambda_f'), other.get('lambda_f')
    if not a or not b or a['mean'] is None or b['mean'] is None:
        return {'passed': False, 'reason': 'contrast unavailable'}
    av, bv = np.asarray(a['replicates']), np.asarray(b['replicates'])
    half = 2.015 * math.sqrt(float(av.var(ddof=1) / len(av) + bv.var(ddof=1) / len(bv)))
    difference = b['mean'] - a['mean']
    threshold = .05 * primary['flow_range']
    return {'passed': bool(abs(difference) + half <= threshold), 'difference': difference,
            'interval90': [difference - half, difference + half], 'threshold': threshold,
            'excess': abs(difference) + half - threshold}


def assemble_rows(originals, replacements, plan):
    """Merge by frozen job identity, not by outcomes. Input outputs stay intact."""
    from .production_tables import row_key
    from .offline_estimator import SENSITIVITY_RULES, SENSITIVITY_RR
    expected = plan['replacements']
    if set(replacements) != set(expected):
        raise ValueError('repair jobs missing or extra')
    primary, sensitivity, rates = {}, {}, {}
    for job_id, original in originals.items():
        output = replacements.get(job_id, original)
        old_rows = {row_key(r): r for r in original['result']['rows']}
        new_rows = {row_key(r): r for r in output['result']['rows']}
        if len(new_rows) != len(output['result']['rows']) or set(new_rows) != set(old_rows):
            raise ValueError('replacement scoring contexts differ')
        config = original['job']['config']
        name = config['setting_name']
        for key, value in new_rows.items():
            row = deepcopy(value)
            if job_id in replacements:
                screen = numerical_contrast(old_rows[key], row)
                row['repair_original_contrast'] = screen
                if not screen['passed']:
                    row['status'] = 'not_estimable'
                    row['reason'] = 'A3 independent replacement contrast failed'
            if name == 'primary':
                if key in primary:
                    raise ValueError('duplicate primary row')
                primary[key] = row
                rates[key] = config['kernel']['reproduction_rate']
            else:
                if name in sensitivity.setdefault(key, {}):
                    raise ValueError('duplicate sensitivity row')
                sensitivity[key][name] = row
    statuses = []
    for key, row in primary.items():
        row['primary_status'], row['primary_reason'] = row['status'], row.get('reason')
        selected = row['rule_id'] in SENSITIVITY_RULES and rates[key] in SENSITIVITY_RR
        passed, contrasts = True, []
        if selected:
            others = sensitivity.get(key, {})
            passed = set(others) == {'double_population', 'double_length'}
            for name, other in sorted(others.items()):
                check = numerical_contrast(row, other)
                numeric = check['passed']
                check.update(setting=name, numerical_contrast_passed=numeric, other_status=other['status'],
                             other_screens=other.get('screens', {}), passed=numeric and other['status'] == 'estimated')
                passed &= check['passed']
                contrasts.append(check)
            statuses.append(bool(passed))
        row['sensitivity'] = {'selected': selected, 'passed': bool(passed) if selected else None, 'contrasts': contrasts}
        if selected and not passed:
            row['status'] = 'not_estimable'
            row['reason'] = 'declared sensitivity subset failed or is incomplete'
    return primary, bool(statuses) and all(statuses)


def publish(spec, run_root, source_root, calibration, target):
    """Explicit hybrid provenance, with all unchanged production gates."""
    from .production_runner import completed
    from .production_tables import write_tables, ProductionTables
    from .study import table_design
    from .calibration import validate_calibration
    if spec['code_hash'] != code_identity():
        raise ValueError('repair worker source changed')
    from .table_compatibility_a3 import validate_plan, publication_receipt, refuse_family_failure, record_family_failure
    policy = validate_plan(spec)
    refuse_family_failure(policy)
    verify_registration(spec['registration'])
    validate_calibration(calibration, registered=True)
    plan = spec['repair']
    source_root, run_root = Path(source_root), Path(run_root)
    if (run_root / 'table/screen_failure.json').exists():
        record_family_failure(policy, read(run_root / 'table/screen_failure.json'), run_root)
        raise RuntimeError('A3 screen failure is latched; publication refused')
    path = source_root / 'v3_rerun_tables_A1.json'
    if file_hash(path) != plan['source_file_sha256'] or plan['source_file_sha256'] != A1_FILE_SHA256:
        raise ValueError('A1 publication changed')
    source_spec = unseal(read(source_root / 'tables_A1_manifest.json'))
    if digest(source_spec) != plan['source_manifest_sha256'] or calibration['sha256'] != plan['calibration_sha256']:
        raise ValueError('source manifest or frozen calibration changed')
    # Reconstruct the complete selection, settings and seeds from the pinned
    # original family before accepting any replacement. The plan itself is
    # sealed by the runner and bound to the committed code and registration.
    originals, replacements = {}, {}
    for job in source_spec['jobs']:
        output = completed(source_root / 'tables_A1/table', job, plan['source_code_hash'])
        original_path = source_root / 'tables_A1/table/outputs' / (job['id'] + '.json')
        if output is None or file_hash(original_path) != plan['source_outputs'].get(job['id']):
            raise ValueError('A1 job missing or changed')
        if output['result']['calibration_hash'] != calibration['sha256']:
            raise ValueError('original calibration mismatch')
        originals[job['id']] = output
    from .offline_estimator import SENSITIVITY_RULES, SENSITIVITY_RR
    pairs = {(rule, rr) for rule in SENSITIVITY_RULES for rr in SENSITIVITY_RR}
    for output in originals.values():
        if any(r['status'] != 'estimated' for r in output['result']['rows']):
            c = output['job']['config']
            pairs.add((c['rule_id'], c['kernel']['reproduction_rate']))
    required = {job['id'] for job in source_spec['jobs']
                if (job['config']['rule_id'], job['config']['kernel']['reproduction_rate']) in pairs}
    if set(plan['source_outputs']) != set(originals) or set(plan['replacements']) != required or {tuple(p) for p in plan['pairs']} != pairs:
        raise ValueError('fixed selection or source family changed')
    expected_ids = set(plan['replacements'].values())
    if {j['id'] for j in spec['jobs']} != expected_ids or len(spec['jobs']) != len(expected_ids):
        raise ValueError('repair specification job set changed')
    source_jobs = {j['id']: j for j in source_spec['jobs']}
    for job in spec['jobs']:
        old_id = job['config']['source_job_id']
        expected = deepcopy(source_jobs[old_id]['config'])
        expected.update(settings=enlarged(expected['settings']), calibration_path=job['config']['calibration_path'],
                        repair_round='A3-fixed-once-20260928', source_job_id=old_id)
        if job != stable_job('table', expected, 'v3_tables', 0) or plan['replacements'].get(old_id) != job['id']:
            raise ValueError('replacement configuration or seed changed')
        output = completed(run_root / 'table', job, spec['code_hash'])
        if output is None or output['result']['calibration_hash'] != calibration['sha256'] or output['result']['fixture_calibration']:
            raise ValueError('replacement incomplete or invalid calibration')
        replacements[old_id] = output
    rows, passed = assemble_rows(originals, replacements, plan)
    if not passed or any(r['status'] != 'estimated' for r in rows.values()):
        record_family_failure(policy, {'reason': 'publication row or sensitivity contrast failed',
                                      'failed_rows': [key for key, row in rows.items() if row['status'] != 'estimated']}, run_root)
        raise RuntimeError('A3 row or contrast failed; nothing published')
    source_publication = unseal(read(path))
    if set(rows) != set(source_publication['manifest']['required_row_keys']):
        raise ValueError('incomplete full family')
    manifest = {'tag': 'v3_tables', 'calibration_hash': calibration['sha256'], 'design': table_design(),
                'repair': plan, 'required_row_keys': sorted(rows), 'complete_family': True,
                'sensitivity_status': 'passed' if passed else 'incomplete_or_failed',
                'source_family': {'file_sha256': A1_FILE_SHA256, 'code_hash': plan['source_code_hash']},
                'replacement_output_hashes': {old_id: file_hash(run_root / 'table/outputs' / (o['job']['id'] + '.json')) for old_id, o in replacements.items()}}
    manifest['design'] = dict(manifest['design'], amendment=AMENDMENT, fixed_repair=plan)
    # Validate a distinctly named candidate before publishing final bytes.
    candidate = run_root / 'candidate_unpublished_tables.json'
    document = write_tables(candidate, list(rows.values()), manifest, fixture=False)
    publication_receipt(candidate, document, spec, replacements, run_root)
    ProductionTables(candidate, calibration_hash=calibration['sha256'], registered=True)
    target = Path(target)
    if target.exists() and read(target) != document:
        raise RuntimeError('table is frozen')
    atomic_json(target.with_suffix('.compatibility.json'), read(candidate.with_suffix('.compatibility.json')))
    atomic_json(target, document)
    return document


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('audit'); p.add_argument('source_manifest'); p.add_argument('calibration_path'); p.add_argument('output')
    p.add_argument('--pin')
    p.add_argument('--source-root', required=True)
    p = sub.add_parser('publish')
    p.add_argument('spec'); p.add_argument('run_root'); p.add_argument('source_root'); p.add_argument('calibration'); p.add_argument('target')
    args = parser.parse_args()
    if args.command == 'prepare':
        spec = prepare(read(args.audit), unseal(read(args.source_manifest)), args.calibration_path, read(args.pin) if args.pin else None, source_root=args.source_root)
        atomic_json(args.output, seal(spec))
        print({'jobs': len(spec['jobs']), 'launched': False, 'registration_supplied': bool(spec['registration'])})
    else:
        publish(unseal(read(args.spec)), args.run_root, args.source_root, read(args.calibration), SIMULATION / args.target)


if __name__ == '__main__':
    main()
