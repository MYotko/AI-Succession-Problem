"""Compute only the registered A1 through A6 and required descriptive counts."""
import sys
sys.dont_write_bytecode = True
import drift_map_run_a3_executor as run
import csv
import io
import json
from collections import Counter
from pathlib import Path
import numpy as np

P = run.P
OUT = run.OUT
SHARES = ('x_compute', 'x_bio_welfare', 'x_novelty_agency',
          'x_institutional_capacity', 'x_transfer_comprehension', 'x_resilience')
STATEMENTS = (
    'No CUSUM allowance, threshold, or alarm rule was chosen or run. '
    'The production adapter accumulator score was recorded only, with cop_cusum_drift false. '
    'No attack-success rate or corrected figure was derived. '
    'H_ref is a candidate and is not frozen. '
    'Nothing here is comparable to any pre-repair measurement.'
)


def load_rows(completion):
    with (OUT / completion['raw_log']).open(encoding='utf-8', newline='') as handle:
        result = []
        for row in csv.DictReader(handle):
            parsed = {}
            for key, value in row.items():
                if key == 'arm':
                    parsed[key] = value
                elif value == 'null':
                    parsed[key] = None
                elif value in ('True', 'False'):
                    parsed[key] = value == 'True'
                elif key in ('seed', 'step', 'novelty_vector_count', 'population', 'shape_fallback_increase'):
                    parsed[key] = int(value)
                else:
                    parsed[key] = float(value)
            result.append(parsed)
        return result


def save_csv(name, fields, rows):
    with (OUT / name).open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({key: 'null' if row.get(key) is None else row[key] for key in fields})
        handle.flush()
        run.os.fsync(handle.fileno())


def span(values):
    return {'count': len(values),
            'minimum': float(np.min(values)) if values else None,
            'median': float(np.median(values)) if values else None,
            'maximum': float(np.max(values)) if values else None}


def registered_analysis(plan, completions):
    trajectories = {(c['arm'], c['seed']): load_rows(c) for c in completions}
    baseline = [r for seed in plan['seeds'] for r in trajectories[('H', seed)] if r['step'] >= 10]
    entropy = [r['h_n_latest'] for r in baseline]
    suppression = [r['total_suppression'] for r in baseline]
    p05, p25, p50, p75, p95 = [float(x) for x in np.percentile(entropy, [5, 25, 50, 75, 95], method='linear')]
    a1 = {
        'records': len(baseline), 'candidate_H_ref': p50, 'H_ref_frozen': False,
        'raw_entropy_p05': p05, 'raw_entropy_p25': p25,
        'raw_entropy_p75': p75, 'raw_entropy_p95': p95,
        'raw_entropy_exactly_zero_records': sum(x == 0.0 for x in entropy),
        'coupled_suppression_median': float(np.median(suppression)),
        'coupled_suppression_p95': float(np.percentile(suppression, 95, method='linear')),
        'coupled_suppression_at_or_above_0_75_records': sum(x >= 0.75 for x in suppression),
        'coupled_suppression_exactly_1_0_records': sum(x == 1.0 for x in suppression),
        'allocation_share_medians': {k: float(np.median([r[k] for r in baseline])) for k in SHARES},
        'g_at_or_above_g_star_records': sum(r['g'] >= plan['g_star'] for r in baseline),
        'g_at_or_above_g_star_runs': len({r['seed'] for r in baseline if r['g'] >= plan['g_star']}),
    }
    a2 = {'p05_H': p05, 'basis': 'A1 raw entropy p05, computed once and applied unchanged to all attack arms'}
    a3, a4, a5, a6 = {}, {}, {}, {}
    per_run = []
    paired_rows = []
    paired_run_means = []
    for arm in plan['arms']:
        if arm == 'H':
            continue
        crossings = []
        noncrossings = []
        for seed in plan['seeds']:
            completion = next(c for c in completions if c['arm'] == arm and c['seed'] == seed)
            rows = trajectories[(arm, seed)]
            attack_window = [r for r in rows if r['step'] >= 50]
            t_star = next((r['step'] for r in attack_window if r['g'] >= plan['g_star']), None)
            deficit_window = attack_window if t_star is None else [r for r in attack_window if r['step'] <= t_star]
            deficit = sum(max(0.0, p50 - r['h_n_latest']) for r in deficit_window)
            classification = 'not_crossing' if t_star is None else (
                'silent' if all(r['h_n_latest'] >= p05 for r in deficit_window) else 'loud')
            item = {'arm': arm, 'seed': seed, 'steps_completed': completion['steps_completed'],
                    'end_reason': completion['end_reason'], 'extinct': completion['extinct'],
                    't_star': t_star, 't_star_minus_50': None if t_star is None else t_star - 50,
                    'crossing_classification': classification, 'entropy_deficit_sum': deficit,
                    'deficit_quantity': 'not_a_pre_crossing_quantity' if t_star is None else 'before_crossing_inclusive'}
            per_run.append(item)
            (noncrossings if t_star is None else crossings).append(item)
            honest = {r['step']: r for r in trajectories[('H', seed)]}
            last_common = min(rows[-1]['step'], trajectories[('H', seed)][-1]['step'])
            paired = []
            for r in rows:
                step = r['step']
                if 50 <= step <= last_common:
                    h = honest[step]
                    difference = {'arm': arm, 'seed': seed, 'step': step,
                                  'raw_entropy_attack_minus_honest': r['h_n_latest'] - h['h_n_latest'],
                                  'g_attack_minus_honest': r['g'] - h['g']}
                    paired.append(difference)
                    paired_rows.append(difference)
            if paired:
                paired_run_means.append({
                    'arm': arm, 'seed': seed, 'paired_steps': len(paired),
                    'mean_raw_entropy_difference': float(np.mean([r['raw_entropy_attack_minus_honest'] for r in paired])),
                    'mean_g_difference': float(np.mean([r['g_attack_minus_honest'] for r in paired])),
                })
        a3[arm] = {'runs_crossing': len(crossings), 'runs_not_crossing': len(noncrossings),
                   'runs_ending_by_extinction_before_any_crossing': sum(r['extinct'] for r in noncrossings),
                   't_star_minus_50': span([r['t_star_minus_50'] for r in crossings])}
        a4[arm] = {'silent_crossings': sum(r['crossing_classification'] == 'silent' for r in crossings),
                   'loud_crossings': sum(r['crossing_classification'] == 'loud' for r in crossings),
                   'runs_not_crossing': len(noncrossings)}
        a5[arm] = {'crossing_runs_pre_crossing_inclusive': span([r['entropy_deficit_sum'] for r in crossings]),
                   'noncrossing_runs_not_a_pre_crossing_quantity': span([r['entropy_deficit_sum'] for r in noncrossings])}
        means = [r for r in paired_run_means if r['arm'] == arm]
        a6[arm] = {'seeds_contributing': len(means)}
        for key in ('mean_raw_entropy_difference', 'mean_g_difference'):
            values = [r[key] for r in means]
            a6[arm][key] = {'across_seed_mean': float(np.mean(values)) if values else None,
                            'across_seed_median': float(np.median(values)) if values else None}
    save_csv(P+'A3_A5_per_run.csv', list(per_run[0]), per_run)
    save_csv(P+'A6_paired_steps.csv', ['arm', 'seed', 'step', 'raw_entropy_attack_minus_honest', 'g_attack_minus_honest'], paired_rows)
    save_csv(P+'A6_run_means.csv', ['arm', 'seed', 'paired_steps', 'mean_raw_entropy_difference', 'mean_g_difference'], paired_run_means)
    descriptive = {}
    for arm in plan['arms']:
        affected = [{'seed': c['seed'], 'first_step': c['first_fewer_than_two_novelty_vectors_step']}
                    for c in completions if c['arm'] == arm and c['first_fewer_than_two_novelty_vectors_step'] is not None]
        descriptive[arm] = {'runs_reaching_fewer_than_two_novelty_vectors': len(affected), 'first_step_for_each_run': affected}
    fallback = {
        'step_0_increase_distribution': dict(sorted(Counter(c['shape_fallback_increase_step_0'] for c in completions).items())),
        'total_permitted_increase_after_step_0': sum(c['shape_fallback_permitted_increase_after_step_0'] for c in completions),
        'nonpermitted_increase_count_by_run': {c['job']: c['shape_fallback_nonpermitted_increase_count'] for c in completions},
        'nonpermitted_increase_count_zero_in_every_run': all(c['shape_fallback_nonpermitted_increase_count'] == 0 for c in completions),
    }
    results = {'A1': a1, 'A2': a2, 'A3': a3, 'A4': a4, 'A5': a5, 'A6': a6,
               'primary_quantity': 'A4', 'amendment_2_descriptive_counts': descriptive,
               'fallback_descriptive_counts': fallback, 'statements': STATEMENTS,
               'quantile_method': 'numpy.percentile, linear', 'exploratory_analyses': [],
               'created_utc': run.now()}
    run.write(P+'registered_results.json', results)
    summary_fields = ['arm', 'seed', 'steps_completed', 'end_reason', 'extinct',
                      'shape_fallback_increase_step_0', 'shape_fallback_permitted_increase_after_step_0',
                      'shape_fallback_nonpermitted_increase_count', 'first_fewer_than_two_novelty_vectors_step',
                      'raw_log', 'raw_log_sha256_lf']
    save_csv(P+'runs.csv', summary_fields, completions)
    return results


def render_report(plan, gates, completions, end_pins, results, execution):
    lines = ['# Drift mapping characterization, attempt 3', '',
             'Status: '+('completed, 360 of 360 runs.' if results else 'halted before completion.'), '',
             STATEMENTS, '', '## Preconditions and gates', '',
             'T0 passed on operator-authorized retry. The preceding dispatch halted at T0(c) before any probe or run. '
             'The note was read from its committed blob only after its pinned LF-normalized SHA256 passed.', '',
             'HEAD: `'+plan['head']+'`. Design blob SHA1: `'+plan['design_blob_sha1']+'`.', '',
             'Design LF-normalized SHA256: `'+plan['design_sha256_lf']+'`.', '',
             'T0 stderr warnings are retained in the T0 record and manifest. CRLF working-tree bytes matched the LF-normalized source pins.', '']
    if gates:
        g3 = gates['gate_3']
        lines += ['| Gate | Measured evidence | Passed |', '| --- | --- | --- |',
                  '| 2 | All seven source pins match | '+str(gates['gate_2']['passed'])+' |',
                  '| 3 | Seed 1835086199; factory '+str(g3['factory_steps_completed'])+' steps, '+g3['factory_end_reason']+
                  '; common '+str(g3['common_steps_completed'])+' steps, '+g3['common_end_reason']+
                  '; '+str(g3['field_value_comparisons'])+' field comparisons; first difference '+str(g3['first_difference'])+' | '+str(g3['passed'])+' |',
                  '| 4 | '+str(gates['gate_4']['synthetic_actions'])+' actions by 300 steps; '+str(gates['gate_4']['comparisons'])+' comparisons; maximum key difference '+str(gates['gate_4']['maximum_key_difference'])+' | '+str(gates['gate_4']['passed'])+' |',
                  '| 5 | Attack vector null; '+str(gates['gate_5']['steps'])+' steps; '+str(gates['gate_5']['adapter_active_steps'])+' active, '+str(gates['gate_5']['action_modified_steps'])+' modified | '+str(gates['gate_5']['passed'])+' |',
                  '| 6 | '+str(gates['gate_6']['identical_rng_calls'])+' recorder calls with exactly unchanged NumPy global state | '+str(gates['gate_6']['passed'])+' |', '',
                  'Amendment 2 gate evidence:', '', '```json', json.dumps(gates['amendment_2'], indent=2), '```', '']
    if results:
        lines += ['## Registered results', '', '### A1. Repaired honest baseline', '',
                  'Steps 10 and up. H_ref is a candidate and is not frozen. Suppression counts describe the repaired honest planner; no D1 statement is derived.', '',
                  '```json', json.dumps(results['A1'], indent=2), '```', '',
                  '### A2. Honest entropy band', '', 'p05_H = '+repr(results['A2']['p05_H'])+'. Computed once from arm H and applied unchanged.', '',
                  '### A3. Approach to g_star', '',
                  '| Arm | Crossing | Not crossing | Extinction before crossing | t_star minus 50: min, median, max |',
                  '| --- | ---: | ---: | ---: | --- |']
        for arm, item in results['A3'].items():
            s = item['t_star_minus_50']
            lines.append('| '+arm+' | '+str(item['runs_crossing'])+' | '+str(item['runs_not_crossing'])+' | '+str(item['runs_ending_by_extinction_before_any_crossing'])+' | '+', '.join(str(s[k]) for k in ('minimum','median','maximum'))+' |')
        lines += ['', '### A4. Silent crossings, primary quantity', '',
                  '| Arm | Silent crossings | Loud crossings | Runs not crossing |', '| --- | ---: | ---: | ---: |']
        for arm, item in results['A4'].items():
            lines.append('| '+arm+' | '+str(item['silent_crossings'])+' | '+str(item['loud_crossings'])+' | '+str(item['runs_not_crossing'])+' |')
        lines += ['', '### A5. Entropy deficit', '',
                  'Each sum uses steps 50 through the first crossing, inclusive. Noncrossing sums use steps 50 through the last completed step and are not pre-crossing quantities.', '',
                  '| Arm | Crossing sum: min, median, max | Noncrossing sum, not pre-crossing: min, median, max |', '| --- | --- | --- |']
        for arm, item in results['A5'].items():
            s = item['crossing_runs_pre_crossing_inclusive']; n = item['noncrossing_runs_not_a_pre_crossing_quantity']
            lines.append('| '+arm+' | '+', '.join(str(s[k]) for k in ('minimum','median','maximum'))+' | '+', '.join(str(n[k]) for k in ('minimum','median','maximum'))+' |')
        lines += ['', '### A6. Paired trajectories', '',
                  'Across-seed summaries of each run\'s mean paired difference, attack minus honest. No t statistic or standard error was computed.', '',
                  '| Arm | Seeds | Raw entropy: mean, median | g: mean, median |', '| --- | ---: | --- | --- |']
        for arm, item in results['A6'].items():
            h = item['mean_raw_entropy_difference']; g = item['mean_g_difference']
            lines.append('| '+arm+' | '+str(item['seeds_contributing'])+' | '+str(h['across_seed_mean'])+', '+str(h['across_seed_median'])+' | '+str(g['across_seed_mean'])+', '+str(g['across_seed_median'])+' |')
        fallback = results['fallback_descriptive_counts']
        lines += ['', '## Amendment 2 descriptive counts', '',
                  'Across all 360 runs, the step 0 fallback-increase distribution, increase to run count, was '+json.dumps(fallback['step_0_increase_distribution'], sort_keys=True)+'.', '',
                  'Total permitted fallback increase after step 0: '+str(fallback['total_permitted_increase_after_step_0'])+'. '
                  'Non-permitted increase count was zero in every run: '+str(fallback['nonpermitted_increase_count_zero_in_every_run'])+'.', '',
                  'Steps with fewer than two novelty vectors entered A1 through A6 exactly as recorded. No step was dropped or imputed.', '',
                  '| Arm | Runs reaching fewer than two novelty vectors | First such step for each affected run, seed: step |', '| --- | ---: | --- |']
        for arm, item in results['amendment_2_descriptive_counts'].items():
            entries = ', '.join(str(x['seed'])+': '+str(x['first_step']) for x in item['first_step_for_each_run']) or 'None'
            lines.append('| '+arm+' | '+str(item['runs_reaching_fewer_than_two_novelty_vectors'])+' | '+entries+' |')
    else:
        lines += ['Halt record:', '', '```json', json.dumps(run.read(P+'stop.json'), indent=2), '```', '']
    lines += ['', '## Execution and final source readings', '',
              'Machine: '+str(completions[0]['runtime']['machine'] if completions else run.os.environ.get('COMPUTERNAME'))+'. '
              'Maximum active batch workers: '+str(execution.get('maximum_active_workers', 0))+'. '
              'Numerical-library threads were fixed to one and queried per worker. '
              'The runtime mode control supports normal, 15 workers, and work, 12 workers, with draining on reductions.', '',
              'Resumed seeds: '+json.dumps(execution.get('resumed_seeds', []))+'.', '',
              '| Source | Start SHA256, LF-normalized working-tree bytes | End SHA256, same basis | Committed blob SHA1 |', '| --- | --- | --- | --- |']
    for item in end_pins:
        lines.append('| `'+item['path']+'` | `'+item['initial_sha256_lf']+'` | `'+item['actual_sha256_lf']+'` | `'+item['committed_blob_sha1']+'` |')
    lines += ['', 'Per-worker configurations, source readings, Python and NumPy versions, effective thread queries, and raw-log hashes are retained in completion records. '
              'The manifest inventories attempt artifacts. The operator performs the containment diff.', '']
    with (OUT/(P+'report.md')).open('w', encoding='utf-8', newline='\n') as handle:
        handle.write('\n'.join(lines))


def manifest(plan, completions, execution, end_pins):
    module_catalog = {}
    runtime_records = list(completions)
    for name in ('gate_factory_result.json','gate_common_result.json','gate_honest_result.json','gate_wrapper_result.json'):
        if (OUT/(P+name)).exists():
            runtime_records.append(run.read(P+name))
    for record in runtime_records:
        for path, readings in record['runtime']['modules'].items():
            if path not in module_catalog:
                module_catalog[path] = {'readings': []}
            if readings not in module_catalog[path]['readings']:
                module_catalog[path]['readings'].append(readings)
    for path in module_catalog:
        p = run.subprocess.run(['git','rev-parse','--verify','HEAD:'+path], cwd=run.ROOT, capture_output=True)
        module_catalog[path]['committed_blob_sha1'] = p.stdout.decode().strip() if p.returncode == 0 else None
    run.write(P+'module_hashes.json', module_catalog)
    outputs = []
    for path in sorted(OUT.glob(P+'*')):
        if path.name == P+'manifest.json' or not path.is_file():
            continue
        raw = path.read_bytes()
        count = None
        if path.name.endswith('.csv') or '.csv.partial' in path.name:
            count = sum(1 for row in csv.DictReader(io.StringIO(raw.decode('utf-8'), newline='')))
        outputs.append({'path': path.relative_to(run.ROOT).as_posix(),
                        'sha256_lf': run.sha(run.lf(raw)), 'basis': 'LF-normalized bytes',
                        'csv_data_rows': count})
    result = {
        'created_utc': run.now(), 'head_start': plan['head'],
        'head_end': run.git('rev-parse','HEAD').decode().strip(),
        'machine': run.os.environ.get('COMPUTERNAME'), 'python': sys.version, 'numpy': np.__version__,
        'design_note': {'path': plan['design_note'], 'committed_blob_sha1': plan['design_blob_sha1'],
                        'sha256_lf': plan['design_sha256_lf'], 'basis': 'LF-normalized committed blob'},
        'pinned_sources_start_and_end': end_pins, 'modules': module_catalog,
        'cpu_budget': 16, 'worker_limits': plan['worker_limits'],
        'maximum_active_batch_workers': execution.get('maximum_active_workers',0),
        'gate_execution': run.read(P+'gate_execution.json') if (OUT/(P+'gate_execution.json')).exists() else None,
        'worker_runtime_records': [{'job': r.get('job','gate_wrapper'), 'runtime': r['runtime']} for r in runtime_records],
        'mode_changes': execution.get('mode_changes',[]), 'resumed_seeds': execution.get('resumed_seeds',[]),
        't0_stderr_warnings': plan['t0_stderr_warnings'], 'outputs': outputs,
        'manifest_self_entry': 'This manifest is excluded from its own inventory to avoid a recursive digest. Its LF-normalized SHA256 is emitted on completion.',
        'csv_row_count_method': 'csv.DictReader excluding the header; null for non-CSV artifacts',
        'completed_run_count': len(completions), 'statements': STATEMENTS,
    }
    run.write(P+'manifest.json', result)
    return run.sha(run.lf((OUT/(P+'manifest.json')).read_bytes()))


def main():
    plan = run.read(P+'plan.json')
    end_pins = run.pins()
    run.write(P+'source_pins_end.json', {'utc': run.now(), 'readings': end_pins})
    execution = run.read(P+'execution.json') if (OUT/(P+'execution.json')).exists() else {}
    gates = run.read(P+'gates.json') if (OUT/(P+'gates.json')).exists() else None
    completions = []
    for arm in plan['arms']:
        for seed in plan['seeds']:
            c = run.completed(arm+'_'+str(seed), arm, seed)
            if c is not None:
                completions.append(c)
    results = None
    if not (OUT/(P+'stop.json')).exists() and len(completions) == 360:
        results = registered_analysis(plan, completions)
    render_report(plan, gates, completions, end_pins, results, execution)
    digest = manifest(plan, completions, execution, end_pins)
    print(json.dumps({'completed_runs': len(completions), 'registered_analysis_completed': results is not None,
                      'manifest_sha256_lf': digest, 'A4': results['A4'] if results else None}), flush=True)


if __name__ == '__main__':
    main()
