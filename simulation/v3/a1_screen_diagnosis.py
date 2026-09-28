"""Read-only A1 audit. Never opens registered rerun artifacts."""
import argparse
from collections import Counter, defaultdict
from pathlib import Path
from .artifacts import read, unseal, file_hash, digest, atomic_json
from .diagnose_tables import row_metrics, contrast
from .production_tables import row_key


def breakdown(rows, field):
    groups = defaultdict(list)
    for row in rows:
        groups[str(row.get(field, row['context'].get(field)))].append(row)
    return {k: {'rows': len(v), 'failed': sum(r['status'] != 'estimated' for r in v)}
            for k, v in sorted(groups.items())}


def summarize(rows):
    failed = [r for r in rows if r['status'] != 'estimated']
    names = ('flow_half_width', 'half_window_drift', 'bellman_residual', 'continuation_coverage', 'survival_fraction')
    return {'rows': len(rows), 'failed': len(failed),
            'screens': dict(Counter(k for r in rows for k, v in r['screens'].items() if not v)),
            'exceeded': {k: sum(r['excess'][k] is not None and r['excess'][k] > 0 for r in rows) for k in names},
            'rule_kernels': len({(r['rule'], r['rr']) for r in failed}),
            'breakdowns': {f: breakdown(rows, f) for f in ('rule', 'rr', 'alpha', 'capability', 'kappa', 'route')},
            'worst': {k: sorted((r for r in rows if r['excess'][k] is not None), key=lambda r: r['excess'][k], reverse=True)[:5] for k in names}}


def audit(root):
    root = Path(root)
    publication = root / 'v3_rerun_tables_A1.json'
    document = read(publication)
    table = unseal(document)
    spec = unseal(read(root / 'tables_A1_manifest.json'))
    published = {k: unseal(v) for k, v in table['rows'].items()}
    if set(published) != set(table['manifest']['required_row_keys']):
        raise ValueError('publication keys differ from required family')
    rows, jobs, primary, others = [], [], {}, defaultdict(dict)
    for job in spec['jobs']:
        path = root / 'tables_A1/table/outputs' / (job['id'] + '.json')
        output = read(path)
        record = read(root / 'tables_A1/table/records' / (job['id'] + '.json'))
        if record['status'] != 'complete' or file_hash(path) != record['output_hash'] or output['job'] != job or record['job'] != job:
            raise ValueError('completion or job mismatch')
        if output['code_hash'] != table['code_hash'] or record['code_hash'] != table['code_hash']:
            raise ValueError('producer mismatch')
        result, config = output['result'], job['config']
        if result['calibration_hash'] != table['manifest']['calibration_hash']:
            raise ValueError('calibration mismatch')
        rr, setting = config['kernel']['reproduction_rate'], config['setting_name']
        for row in result['rows']:
            key = row_key(row)
            metric = row_metrics(row)
            c = row.get('continuation') or {}
            computed = {
                'route_applicable': row['route'] == 'fv' or row['surviving_fraction'] >= .5,
                'flow_half_width': row['lambda_f']['half_width'] <= .05 * row['flow_range'],
                'half_window_drift': metric['values']['half_window_drift'] is not None and metric['values']['half_window_drift'] <= .05 * row['flow_range'],
                'continuation': c['heldout_coverage'] >= .9 and c['bellman_residual_empirical'] <= .05 * row['flow_range'] and bool(c['entries']) and c['training_fixed_point_converged'],
            }
            if row['screens'] != computed or (row['status'] == 'estimated') != all(computed.values()):
                raise ValueError('stored screen status disagrees with recomputed metrics')
            metric.update(rr=rr, setting=setting, job_id=job['id'],
                          largest_residual_bins=c.get('largest_residual_bins', []),
                          heldout_transitions=c.get('heldout_transitions'),
                          bellman_rmse=c.get('bellman_rmse'),
                          unpublished_source_heldout=c.get('unpublished_source_heldout'),
                          unpublished_successor_heldout=c.get('unpublished_successor_heldout'))
            rows.append(metric)
            # Retain only fields needed for contrast recomputation.
            short = {k: row.get(k) for k in ('lambda_f', 'flow_range', 'status', 'screens')}
            short['scientific_sha256'] = digest({k: v for k, v in row.items() if k not in ('status', 'reason', 'ranking_flag')})
            if setting == 'primary':
                if key in primary:
                    raise ValueError('duplicate primary')
                primary[key] = short
            else:
                if setting in others[key]:
                    raise ValueError('duplicate sensitivity')
                others[key][setting] = short
        jobs.append({'id': job['id'], 'rule': config['rule_id'], 'rr': rr, 'setting': setting,
                     'route': result['route'], 'settings': result['settings'], 'seed': job['seed'],
                     'seconds': record['worker_seconds'], 'trajectory_seconds': result['trajectory_seconds'],
                     'rescore_seconds': result['rescore_seconds'], 'output_sha256': record['output_hash'],
                     'population_mean': result['population_mean'], 'population_max': result['population_max'],
                     'plain_final_survivors': result['plain_survivor_counts'][-1],
                     'collapsed': result['ensemble_collapses'], 'rows': len(result['rows'])})
    if set(primary) != set(published):
        raise ValueError('published family differs from completed primary jobs')
    metrics = {r['row_key']: r for r in rows if r['setting'] == 'primary'}
    contrasts, final = [], []
    for key, row in published.items():
        kept = {k: v for k, v in row.items() if k not in ('status', 'reason', 'ranking_flag', 'primary_status', 'primary_reason', 'sensitivity')}
        if digest(kept) != primary[key]['scientific_sha256'] or row['primary_status'] != primary[key]['status']:
            raise ValueError('publication changed primary scientific values')
        metric = dict(metrics[key], primary_status=primary[key]['status'], status=row['status'], sensitivity=row['sensitivity'])
        final.append(metric)
        if row['sensitivity']['selected']:
            recomputed_pass = True
            for setting in ('double_population', 'double_length'):
                comparison = others.get(key, {}).get(setting)
                info = contrast(primary[key], comparison) if comparison else {'computable': False, 'missing': True}
                recomputed_pass &= info.get('contrast_passed', False) and info.get('other_status') == 'estimated'
                contrasts.append({'row_key': key, 'rule': row['rule_id'], 'rr': metric['rr'], 'context': row['scoring'], 'setting': setting, **info})
            if recomputed_pass != row['sensitivity']['passed']:
                raise ValueError('stored sensitivity status disagrees with recomputation')
        expected_status = 'estimated' if primary[key]['status'] == 'estimated' and row['sensitivity']['passed'] is not False else 'not_estimable'
        if row['status'] != expected_status:
            raise ValueError('published row classification disagrees with recomputation')
    run = root / 'tables_A1'
    return {'schema': 'v3-A1-diagnosis-1', 'source_file_sha256': file_hash(publication),
            'source_payload_sha256': document['sha256'], 'source_manifest_sha256': digest(spec),
            'source_code_hash': table['code_hash'], 'calibration_sha256': table['manifest']['calibration_hash'],
            'verified_jobs': len(jobs), 'manifest_design': table['manifest']['design'],
            'summaries': {s: summarize([r for r in rows if r['setting'] == s]) for s in ('primary', 'double_population', 'double_length')},
            'published_summary': summarize(final), 'contrasts': contrasts, 'rows': rows, 'published': final, 'jobs': jobs,
            'execution': read(run / 'launches.json')[-1]['outcomes']['table'], 'service': read(run / 'service.json')}


def exposure(audit_result, validation_root):
    """Overlay row statuses on existing non-registered paths, without rescoring.

    All candidate rules query the same scoring context. Endpoint occupancy
    is irrelevant to a row-wide rejection. N=40 paths are reported only as
    standardized N=200 context overlays, not matching registered initial law.
    """
    lookup = {(r['rr'], r['context']['alpha'], r['context']['capability'], r['context']['kappa'], r['rule']): r
              for r in audit_result['published']}
    rules = sorted({r['rule'] for r in audit_result['published']})
    root = Path(validation_root)
    specification = unseal(read(root / 'manifest.json'))
    if specification.get('registered') is not False or any(j['tag'] not in ('pilot', 'validation') for j in specification['jobs']):
        raise ValueError('refusing registered rerun root before opening outputs')
    expected = {j['id']: j for j in specification['jobs']}
    results = []
    for path in sorted((root / 'rerun/outputs').glob('*.json')):
        output = read(path)
        job = output['job']
        if job['tag'] not in ('pilot', 'validation'):
            raise ValueError('refusing to inspect registered rerun results')
        record = read(root / 'rerun/records' / path.name)
        if record['status'] != 'complete' or record['job'] != job or expected.get(job['id']) != job or record['output_hash'] != file_hash(path) or record['code_hash'] != output['code_hash']:
            raise ValueError('validation completion mismatch')
        config, result = job['config'], output['result']
        model = config.get('model', {})
        rr, alpha, kappa = model.get('reproduction_rate', .08), model.get('alpha', 1.), model.get('kappa', 8.)
        candidate_counts, chosen_counts = Counter(), Counter()
        live = affected = all_failed = unmatched = 0
        for step in result['diagnostics']:
            if not step['allocation_evaluated']:
                continue
            # These archived six jobs have no succession. Fail closed if a
            # future input needs pre-yield capability reconstruction.
            if any(e.get('transition_count', 0) for e in result['yield_events']):
                raise ValueError('overlay requires pre-yield capability reconstruction')
            live += 1
            bad = []
            for rule in rules:
                row = lookup.get((rr, alpha, step['capability'], kappa, rule))
                if row is None:
                    unmatched += 1
                elif row['status'] != 'estimated':
                    candidate_counts[rule] += 1
                    bad.append(rule)
            affected += bool(bad)
            all_failed += len(bad) == len(rules)
            if step['chosen_rule'] in bad:
                chosen_counts[step['chosen_rule']] += 1
        results.append({'job_id': job['id'], 'output_sha256': record['output_hash'], 'category': config['category'],
                        'rr': rr, 'alpha': alpha, 'initial_population': model.get('n_agents', 200),
                        'matches_registered_initial_population': model.get('n_agents', 200) == 200,
                        'steps': result['steps'], 'allocation_steps': live, 'rule_queries': live * len(rules),
                        'failed_rule_queries': sum(candidate_counts.values()), 'steps_affected': affected,
                        'steps_all_rows_failed': all_failed, 'unmatched_context_queries': unmatched,
                        'failed_query_fraction': sum(candidate_counts.values()) / max(1, live * len(rules)),
                        'by_rule': dict(candidate_counts), 'chosen_failed_by_rule': dict(chosen_counts),
                        'population_mean': result['population_mean'], 'population_max': result['population_max']})
    return {'registered': False, 'method': 'status overlay on existing pilot/fixture decisions; no counterfactual W decisions or joint missing-bin fallback estimate',
            'jobs': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input'); parser.add_argument('output')
    args = parser.parse_args()
    result = audit(args.input)
    atomic_json(args.output, result)
    print({'jobs': result['verified_jobs'], 'file_sha256': result['source_file_sha256'],
           'summaries': {s: {k: v for k, v in x.items() if k not in ('worst', 'breakdowns')} for s, x in result['summaries'].items()},
           'published_failed': result['published_summary']['failed']})


if __name__ == '__main__':
    main()
