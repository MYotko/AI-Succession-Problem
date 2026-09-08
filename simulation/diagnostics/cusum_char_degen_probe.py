"""Known-defective instrument probe using the existing Stage 1 recorder."""
import sys
sys.dont_write_bytecode = True
import argparse
import bisect
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import time
import traceback

import cusum_char_stage1 as stage1

OUT = Path(__file__).resolve().parent
PREFIX = 'cusum_char_degen_'
EXPECTED_HEAD = '1261c9f430411b9fa0060a7384bf4ec5175e4f4e'
FIRST_SEED = 1835086199
N_RUNS = 40
HORIZON = 300
MAX_TOL = 1e-6
SCOPE = ('These runs characterize a known-defective entropy estimator and planner. '
         'They are not framework evidence, not archived evidence, and not a replacement '
         'for the unarchived Phase B or phi data. Nothing produced here may be cited '
         'as a characterization of the framework. These outputs are not registered '
         'characterization data and do not cross the pre-registration boundary.')
EXTRA_FIELDS = ['H_N', 'H_eff', 'c_avg', 'zero_novelty_agents', 'novelty_vector_count',
                'all_zero_novelty', 'H_N_at_maximum', 'avg_well_being', 'U_sys', 'L_t',
                'h_n_estimator_cached']

# Tighten the existing audit hook before any simulation imports or output opens.
stage1.PREFIX = PREFIX

def output(name):
    p = OUT / name
    if p.resolve().parent != OUT or not p.name.startswith(PREFIX):
        raise stage1.StageHalt('Output path outside probe scope: ' + str(p))
    return p


def recorder_output(name):
    # Redirect only the existing recorder's filename; never open a Stage 1 artifact.
    expected = 'cusum_char_stage1_degen_seed'
    if not name.startswith(expected) or not name.endswith('_steps.csv'):
        raise stage1.StageHalt('Unexpected inherited recorder output: ' + name)
    return output(name.replace('cusum_char_stage1_degen_', PREFIX, 1))


stage1.output_path = recorder_output


def write_json(name, obj):
    output(name).write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')


def write_report(text):
    if '\u2014' in text:
        raise stage1.StageHalt('Em dash in report')
    output(PREFIX + 'report.md').write_text(text, encoding='utf-8')


class ExtendedRowWriter:
    def __init__(self, handle, fields, recorder):
        self.writer = csv.DictWriter(handle, fieldnames=fields)
        self.recorder = recorder

    def writeheader(self):
        self.writer.writeheader()

    def writerow(self, row):
        row.update(self.recorder.extra_values)
        self.writer.writerow(row)


class ExtendedRecorder(stage1.Recorder):
    """Inherit Stage 1 row collection, sequencing, flushing, and benign guard."""
    def __init__(self, seed):
        super().__init__(f'degen_seed{seed}', seed, True)
        self.filename = self.handle.name
        self.extra_values = {}
        fields = list(self.writer.fieldnames) + EXTRA_FIELDS
        # The inherited constructor wrote only a header to this new probe file.
        self.handle.seek(0)
        self.handle.truncate()
        self.writer = ExtendedRowWriter(self.handle, fields, self)
        self.writer.writeheader()
        self.handle.flush()

    def record(self, model):
        dc = model.datacollector
        vectors = model.novelty_log
        vector_count = len(vectors)
        if not vector_count:
            raise stage1.StageHalt('No novelty vectors after a completed model step')
        if any(len(v) != 10 or any(not math.isfinite(float(x)) for x in v) for v in vectors):
            raise stage1.StageHalt('Invalid novelty vector shape or nonfinite coordinate')
        zero_count = sum(all(float(x) == 0.0 for x in v) for v in vectors)
        all_zero = zero_count == vector_count
        if not isinstance(model.constraint_level, (float, int)):
            raise stage1.StageHalt('Expected a scalar committed constraint_level')
        c_avg = float(model.constraint_level)
        if not 0.0 <= c_avg <= 1.0:
            raise stage1.StageHalt('Constraint outside the existing action bounds')
        if c_avg != float(dc['constraint_level'][-1]) or c_avg != float(dc['total_suppression'][-1]):
            raise stage1.StageHalt('Committed constraint/collector mismatch')
        if vector_count != len(model.schedule) + len(model.deaths_this_step) - model.births_this_step:
            raise stage1.StageHalt('Novelty vector cohort count does not reconcile')
        if 'attack_vector_v2' in model.config or model.attack_vector_v2 is not None:
            raise stage1.StageHalt('Attack configured in benign probe')
        if float(dc['v2_adapter_cusum_score'][-1]) != 0.0:
            raise stage1.StageHalt('Nonzero adapter score in benign probe')
        hn = float(dc['H_N'][-1])
        self.extra_values = {
            'H_N': hn, 'H_eff': float(dc['h_eff_v2'][-1]), 'c_avg': c_avg,
            'zero_novelty_agents': zero_count, 'novelty_vector_count': vector_count,
            'all_zero_novelty': all_zero, 'H_N_at_maximum': abs(hn - 1.0) <= MAX_TOL,
            'avg_well_being': float(dc['avg_well_being'][-1]),
            'U_sys': float(dc['U_sys'][-1]), 'L_t': float(dc['L_t'][-1]),
            'h_n_estimator_cached': float(model.h_n_latest),
        }
        if any(not math.isfinite(v) for v in self.extra_values.values() if isinstance(v, float)):
            raise stage1.StageHalt('Nonfinite requested observable')
        super().record(model)


def gate():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=OUT.parent.parent).decode().strip()
    advisor = OUT.parent.parent / 'LINEAGE_IMPERATIVE_ADVISOR.md'
    index = subprocess.run(['git', 'ls-files', '--error-unmatch', '--', advisor.name],
                           cwd=OUT.parent.parent, capture_output=True, text=True)
    if head != EXPECTED_HEAD or not advisor.is_file() or index.returncode != 1 or index.stdout.strip():
        raise stage1.StageHalt('Precondition gate failed')
    if not Path(stage1.__file__).is_file():
        raise stage1.StageHalt('Stage 1 instrument is absent')
    return {'head': head, 'advisor_present': True, 'advisor_index_exit': index.returncode,
            'stage1_instrument': str(Path(stage1.__file__).resolve()), 'passed': True}


def sources():
    names = ['model.py', 'agents.py', 'metrics.py', 'attack_adapter_v2.py',
             'working_factor.py', 'constants_v2_stage18.py', 'defection.py']
    paths = [OUT.parent / n for n in names] + [Path(stage1.__file__), Path(__file__)]
    return {str(p.relative_to(OUT.parent.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def load_rows(manifest):
    all_rows = []
    for run in manifest['runs']:
        p = output(run['log'])
        with p.open(newline='', encoding='utf-8') as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        if len(rows) != run['steps']:
            raise stage1.StageHalt('CSV count mismatch: ' + run['log'])
        for i, r in enumerate(rows):
            if int(r['step']) != i or int(r['seed']) != run['seed']:
                raise stage1.StageHalt('CSV sequence or seed mismatch')
            for key in ['step', 'seed', 'population', 'zero_novelty_agents', 'novelty_vector_count']:
                r[key] = int(r[key])
            for key in ['adapter_active', 'all_zero_novelty', 'H_N_at_maximum']:
                if r[key] not in ['True', 'False']:
                    raise stage1.StageHalt('Invalid recorded boolean')
                r[key] = r[key] == 'True'
            for key in ['total_suppression', 'c_suppressive', 'c_protective', 'adapter_score',
                        'H_N', 'H_eff', 'c_avg', 'avg_well_being', 'U_sys', 'L_t', 'h_n_estimator_cached']:
                r[key] = float(r[key])
            if r['adapter_active'] or r['adapter_score'] != 0.0:
                raise stage1.StageHalt('Benign readback guard failed')
            if r['H_N_at_maximum'] != (abs(r['H_N'] - 1.0) <= MAX_TOL):
                raise stage1.StageHalt('Entropy flag readback mismatch')
            if r['all_zero_novelty'] != (r['zero_novelty_agents'] == r['novelty_vector_count']):
                raise stage1.StageHalt('All-zero flag readback mismatch')
        all_rows.extend(rows)
    return all_rows


def dist(values):
    if not values:
        return {'count': 0, 'mean': None, 'median': None, 'min': None, 'max': None}
    return {'count': len(values), 'mean': statistics.fmean(values),
            'median': statistics.median(values), 'min': min(values), 'max': max(values)}


def frac(num, den):
    return {'numerator': num, 'denominator': den, 'fraction': num / den if den else None}


def analyze(manifest):
    rows = load_rows(manifest)
    n = len(rows)
    hnmax = [r for r in rows if r['H_N_at_maximum']]
    az = [r for r in rows if r['all_zero_novelty']]
    joint = [r for r in hnmax if r['all_zero_novelty']]
    result = {'complete': manifest['complete'], 'steps': n, 'run_count': len(manifest['runs']),
              'frequencies': {'H_N_maximum': frac(len(hnmax), n), 'all_zero': frac(len(az), n),
                              'maximum_and_all_zero': frac(len(joint), n),
                              'maximum_and_not_all_zero': frac(len(hnmax) - len(joint), n)},
              'per_run': [], 'bins': [], 'downstream': [], 'correlations': {}}
    for run in manifest['runs']:
        rr = [r for r in rows if r['seed'] == run['seed']]
        zz = [r for r in rr if r['all_zero_novelty']]
        first = zz[0]['step'] if zz else None
        result['per_run'].append({'seed': run['seed'], 'steps': len(rr), 'first_all_zero_step': first,
                                  'all_zero_steps': len(zz),
                                  'ever_leaves_after_entering': any(not r['all_zero_novelty'] and r['step'] > first for r in rr) if first is not None else None})
    edges = [i / 20 for i in range(21)]
    groups = [[] for _ in range(20)]
    for r in rows:
        idx = min(19, bisect.bisect_right(edges, r['c_avg']) - 1)
        if idx < 0:
            raise stage1.StageHalt('Negative bin index')
        groups[idx].append(r)
    for i, group in enumerate(groups):
        item = {'lower': edges[i], 'upper': edges[i+1], 'upper_inclusive': i == 19,
                **dist([r['H_N'] for r in group]),
                'maximum': frac(sum(r['H_N_at_maximum'] for r in group), len(group)),
                'observed_c_avg_min': min((r['c_avg'] for r in group), default=None),
                'observed_c_avg_max': max((r['c_avg'] for r in group), default=None)}
        result['bins'].append(item)
    occupied = [b for b in result['bins'] if b['count']]
    min_mean = min(b['mean'] for b in occupied)
    minima = [b for b in occupied if b['mean'] == min_mean]
    first_min_idx = occupied.index(minima[0])
    tail = occupied[first_min_idx:]
    decreases = [{'from_lower': a['lower'], 'to_lower': b['lower'], 'from_mean': a['mean'], 'to_mean': b['mean']}
                 for a, b in zip(tail, tail[1:]) if b['mean'] < a['mean']]
    result['curve'] = {'minimum_mean': min_mean, 'minimum_bins': minima,
                       'nondecreasing_after_first_minimum': len(decreases) == 0,
                       'strictly_increasing_after_first_minimum': all(b['mean'] > a['mean'] for a,b in zip(tail,tail[1:])),
                       'decreases_after_minimum': decreases,
                       'highest_c_avg_not_all_zero': max((r['c_avg'] for r in rows if not r['all_zero_novelty']), default=None),
                       'lowest_c_avg_all_zero': min((r['c_avg'] for r in az), default=None),
                       'all_zero_below_one': frac(sum(r['c_avg'] < 1.0 for r in az), len(az)),
                       'at_one': frac(sum(r['c_avg'] == 1.0 for r in rows), n)}
    for condition in [True, False]:
        subset = [r for r in rows if r['H_N_at_maximum'] == condition]
        for quantity in ['U_sys', 'L_t']:
            result['downstream'].append({'H_N_at_maximum': condition, 'quantity': quantity,
                                         **dist([r[quantity] for r in subset])})
    for quantity in ['U_sys', 'L_t']:
        try:
            corr = statistics.correlation([r['H_N'] for r in rows], [r[quantity] for r in rows])
        except statistics.StatisticsError:
            corr = None
        result['correlations'][quantity] = {'paired_records': n, 'pearson_r': corr}
    return result


def fmt(x):
    if x is None:
        return 'none'
    if isinstance(x, bool):
        return 'yes' if x else 'no'
    return format(x, '.12g') if isinstance(x, float) else str(x)


def fraction_text(x):
    return f"{x['numerator']}/{x['denominator']} = {fmt(x['fraction'])}"


def render(manifest, result=None):
    lines = ['# Degenerate-frequency probe', '', SCOPE, '',
             '## Execution status', '',
             f"Status: {'complete' if manifest['complete'] else 'in progress'}. Machine: {manifest['machine']}. HEAD: `{manifest['gate']['head']}`.",
             '', 'The precondition gate passed before runs. The root advisor is present and absent from the index. The existing Stage 1 instrument is imported and its Recorder.record method is reused unchanged. A subclass extends its post-step fields through a row writer; only filenames are redirected to the probe prefix. The original Stage 1 script and outputs remain unopened for writing.',
             '', 'All cusum_char_ artifacts are excluded from the authoritative manifest by prefix and are not authoritative evidence. The operator runs the containment diff.',
             '', '## Observable definitions derived from source', '',
             '- Recorded H_N: datacollector[H_N], simulation/model.py:1556. This is components[h_n_v2], with the existing state/metric floor in simulation/metrics.py:645. The cached raw estimator output is also logged as h_n_estimator_cached, model.py:1530-1532.',
             '- Recorded H_eff: datacollector[h_eff_v2], model.py:1598. Recorded U_sys and L(t): datacollector[U_sys] and datacollector[L_t], model.py:1559-1562. No utility is recomputed by the instrument.',
             '- c_avg: read from the committed scalar model.constraint_level. model.py:1455-1471 assigns total_suppression and passes that same scalar to every acting agent. agents.py:791-795 sets c_avg=float(constraint_level). The local variable itself is not retained; its exact scalar value is reachable after the step without a model change.',
             '- zero_novelty_agents counts exactly all-zero vectors in model.novelty_log. agents.py:799-805 appends one vector per acting agent. model.py:1461-1476 resets the log, steps humans, then applies deaths and births. novelty_vector_count is therefore the generation cohort size, while population and avg_well_being are recorded after demographic updates. All-zero means zero_novelty_agents equals the nonempty novelty_vector_count, not the final population.',
             '- Every requested observable is reachable through committed state. The logger reads and counts only; it does not call the estimator, planner, novelty generator, or utility function. No random draws are added.',
             '', '## Constructed configuration and run controls', '',
             'Run controls are operator-fixed: benign policy optimize_u_sys_v2, horizon 300, 40 seeds from 1835086199 through 1835086238 inclusive. These are seed values, not a new seed function. Constructor arguments are derived from the existing Stage 1 baseline source, cusum_char_stage1.py:447-460. Each constructed model is checked against the previously recorded Stage 1 baseline configuration with only random_seed varied.',
             '', 'The configuration below is read back from the first constructed model in these runs. All per-run constructed configurations and selected runtime attributes are in cusum_char_degen_manifest.json. No attack_vector_v2 key is allowed.']
    if manifest['runs']:
        lines += ['', '```json', json.dumps(manifest['runs'][0]['constructed_config'], indent=2, sort_keys=True), '```',
                  '', 'Constructor kwargs, read from this probe invocation:', '', '```json',
                  json.dumps(manifest['constructor_kwargs'], indent=2, sort_keys=True), '```']
    if manifest.get('halt'):
        lines += ['', '## HALT', '', manifest['halt'], '', 'No later run or analysis was started after the anomaly.']
    if result:
        lines += ['', '## Task 1: counted from these runs', '',
                  'All statistics in Tasks 1-3 are counted or calculated only from the saved per-step logs of these runs. No source-derived value is used as an observed outcome. CSV counts use Python csv.DictReader and exclude headers.',
                  '', f"Counted: {result['run_count']} completed runs and {result['steps']} logged steps. H_N at maximum means abs(recorded H_N - 1.0) <= 1e-6, as specified by the operator.",
                  '', '| Condition | Count / all logged steps = fraction |', '| --- | --- |']
        for key, val in result['frequencies'].items():
            lines.append(f'| {key} | {fraction_text(val)} |')
        lines += ['', '| Seed | Logged steps | First all-zero step | All-zero steps | Ever leaves after entering |', '| --- | ---: | ---: | ---: | --- |']
        for r in result['per_run']:
            lines.append('| ' + ' | '.join(fmt(r[k]) for k in ['seed','steps','first_all_zero_step','all_zero_steps','ever_leaves_after_entering']) + ' |')
        lines += ['', 'Step indices are zero-based recorded collector indices. A run with no all-zero step has no entry/exit classification.',
                  '', '## Task 2: counted curve from these runs', '',
                  'Bins are [lower, upper), except the final bin [0.95, 1.0], which includes 1.0. Empty bins retain count zero and undefined summaries. Monotonicity is assessed between successive occupied bins using the recorded means, without interpolation or smoothing. A bin does not identify a unique c_avg value.',
                  '', '| c_avg bin | Count | Mean H_N | Median H_N | Min H_N | Max H_N | At maximum / bin count = fraction |', '| --- | ---: | ---: | ---: | ---: | ---: | --- |']
        for b in result['bins']:
            label = f"[{b['lower']:.2f}, {b['upper']:.2f}{']' if b['upper_inclusive'] else ')'}"
            lines.append('| ' + ' | '.join([label] + [fmt(b[k]) for k in ['count','mean','median','min','max']] + [fraction_text(b['maximum'])]) + ' |')
        c = result['curve']
        minima = ', '.join(f"[{b['lower']:.2f}, {b['upper']:.2f}{']' if b['upper_inclusive'] else ')'}" for b in c['minimum_bins'])
        lines += ['', f"Counted minimum bin mean H_N: {fmt(c['minimum_mean'])}, in bin(s) {minima}.",
                  f"Counted highest observed c_avg without all-zero novelty: {fmt(c['highest_c_avg_not_all_zero'])}. Counted lowest observed c_avg with all-zero novelty: {fmt(c['lowest_c_avg_all_zero'])}.",
                  f"Counted all-zero steps with c_avg strictly below 1.0, among all-zero steps: {fraction_text(c['all_zero_below_one'])}.",
                  f"Counted steps with c_avg exactly 1.0, among all logged steps: {fraction_text(c['at_one'])}."]
        if c['lowest_c_avg_all_zero'] is None:
            lines.append('No all-zero condition was observed; an observed onset is unavailable.')
        elif c['all_zero_below_one']['numerator'] == 0:
            lines.append('In these runs, all-zero novelty was reached only at c_avg exactly 1.0. No onset strictly below 1.0 was observed; unsampled values are not estimated.')
        else:
            lines.append(f"The condition occurred strictly below 1.0. Its lowest observed occurrence was c_avg={fmt(c['lowest_c_avg_all_zero'])}; this is an observed onset, not an inferred universal cutoff.")
        if c['nondecreasing_after_first_minimum']:
            lines.append('Mean H_N is nondecreasing across occupied bins after the minimum. The rise begins at the minimum bin boundary, subject to the reported bin resolution. Strict increase at every adjacent occupied-bin transition: ' + fmt(c['strictly_increasing_after_first_minimum']) + '.')
        else:
            lines += ['Mean H_N does not rise monotonically after its minimum. No monotonic rise onset is assigned. Counted downward transitions after the minimum:', '', '| From bin lower | To bin lower | From mean | To mean |', '| ---: | ---: | ---: | ---: |']
            for d in c['decreases_after_minimum']:
                lines.append('| ' + ' | '.join(fmt(d[k]) for k in ['from_lower','to_lower','from_mean','to_mean']) + ' |')
        lines += ['', '## Task 3: counted downstream association from these runs', '',
                  '| H_N at maximum | Recorded quantity | Count | Mean | Median | Min | Max |', '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
        for d in result['downstream']:
            lines.append('| ' + ' | '.join(fmt(d[k]) for k in ['H_N_at_maximum','quantity','count','mean','median','min','max']) + ' |')
        lines += ['', '| Recorded pair | Paired steps | Pearson correlation |', '| --- | ---: | ---: |']
        for k, v in result['correlations'].items():
            lines.append(f"| H_N and {k} | {v['paired_records']} | {fmt(v['pearson_r'])} |")
        lines += ['', 'These are pooled associations among logged steps. Steps within a run share state and history; no independence claim, causal effect, significance test, or hypothetical corrected-utility calculation is made.']
    lines += ['', '## Artifacts and scope', '',
              'Per-step logs: one cusum_char_degen_seed<seed>_steps.csv per started run, enumerated exactly in cusum_char_degen_manifest.json. Summary outputs: cusum_char_degen_summary.json and cusum_char_degen_bins.csv when analysis completes. The extension is cusum_char_degen_probe.py. Source SHA256 hashes, versions, constructed settings, and completion status are recorded in the manifest.',
              '', 'Only probe-prefixed artifacts in simulation/diagnostics/ are opened for writing. Python bytecode writes are disabled and the reused audit hook rejects writes outside that prefix. No Git writes, production edits, repairs, or containment diff are performed. These probe outputs are not authoritative evidence.', '']
    write_report('\n'.join(lines))


def save_analysis(manifest):
    result = analyze(manifest)
    write_json(PREFIX + 'summary.json', result)
    fields = ['lower','upper','upper_inclusive','count','mean','median','min','max',
              'maximum_count','maximum_denominator','maximum_fraction','observed_c_avg_min','observed_c_avg_max']
    with output(PREFIX + 'bins.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for b in result['bins']:
            row = {k:b[k] for k in fields if k in b}
            row.update(maximum_count=b['maximum']['numerator'], maximum_denominator=b['maximum']['denominator'], maximum_fraction=b['maximum']['fraction'])
            writer.writerow(row)
    render(manifest, result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--analyze-only', action='store_true')
    args = parser.parse_args()
    gate_result = gate()
    manifest_path = output(PREFIX + 'manifest.json')
    if args.analyze_only:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if not manifest['complete'] or manifest.get('halt'):
            raise stage1.StageHalt('Analysis requires completed unhalted runs')
        save_analysis(manifest)
        return
    if manifest_path.exists():
        raise stage1.StageHalt('Probe manifest exists; no unrequested reruns are allowed')
    kwargs = {'n_agents': 200, 'ai_policy': 'optimize_u_sys_v2', 'use_cop': True,
              'cop_attribution_check': True, 'cop_drift_check': True, 'cop_cusum_drift': True}
    manifest = {'scope': SCOPE, 'gate': gate_result, 'machine': os.environ['COMPUTERNAME'],
                'python': sys.version, 'started_utc': stage1.now(), 'complete': False,
                'runs': [], 'constructor_kwargs': kwargs, 'source_sha256': sources(),
                'run_controls': {'first_seed':FIRST_SEED, 'run_count':N_RUNS, 'horizon':HORIZON}}
    write_json(PREFIX + 'manifest.json', manifest)
    render(manifest)
    try:
        import numpy as np
        import run_attack_vector_revalidation_v2 as runner
        manifest['numpy'] = np.__version__
        template = json.loads((OUT / 'cusum_char_stage1_baseline_summary.json').read_text(encoding='utf-8'))['runs'][0]['config']
        for seed in range(FIRST_SEED, FIRST_SEED + N_RUNS):
            recorder = ExtendedRecorder(seed)
            config = {'policy':'optimize_u_sys_v2', 'random_seed':seed, 'phi':10.0, 'attack_step':50,
                      'n_candidates_v2':300, 'rollout_steps_v2':20, 'bootstrap_turn_step_v2':20,
                      'shock_step':0, 'shock_magnitude':0.15}
            run = {'seed':seed, 'log':Path(recorder.filename).name, 'complete':False, 'steps':0}
            manifest['runs'].append(run)
            write_json(PREFIX + 'manifest.json', manifest)
            started = time.perf_counter()
            try:
                model = runner.GardenModel(config=config, **kwargs)
                run['constructed_config'] = dict(model.config)
                run['runtime_attributes'] = {k:getattr(model,k) for k in ['is_v2_mode','hn_composite_method','reproduction_rate','min_viable_population','use_cop','cop_attribution_check','cop_drift_check','cop_cusum_drift']}
                expected = dict(template, random_seed=seed)
                if model.config != expected or 'attack_vector_v2' in model.config:
                    raise stage1.StageHalt('Constructed config differs from Stage 1 baseline')
                if model.hn_composite_method != 'spectral':
                    raise stage1.StageHalt('Unexpected entropy mode')
                write_json(PREFIX + 'manifest.json', manifest)
                for step in range(HORIZON):
                    alive = model.step()
                    recorder.record(model)
                    run['steps'] = len(recorder.rows)
                    if not alive:
                        break
                run['complete'] = True
                run['final_population'] = len(model.schedule)
                run['elapsed_seconds'] = time.perf_counter() - started
            finally:
                recorder.close()
            write_json(PREFIX + 'manifest.json', manifest)
            print(json.dumps({'completed_runs':len(manifest['runs']), 'seed':seed, 'steps':run['steps'], 'elapsed_seconds':run['elapsed_seconds']}), flush=True)
        if sources() != manifest['source_sha256']:
            raise stage1.StageHalt('Instrument or source changed during probe')
        manifest['complete'] = True
        manifest['completed_utc'] = stage1.now()
        write_json(PREFIX + 'manifest.json', manifest)
        result = save_analysis(manifest)
        print(json.dumps({'probe_complete':True, 'steps':result['steps'], 'frequencies':result['frequencies'], 'curve':result['curve']}), flush=True)
    except Exception as error:
        manifest['complete'] = False
        manifest['halt'] = f'{type(error).__name__}: {error}'
        manifest['halt_utc'] = stage1.now()
        write_json(PREFIX + 'manifest.json', manifest)
        render(manifest)
        print('HALT: ' + manifest['halt'], flush=True)
        traceback.print_exc()
        raise SystemExit(2)


if __name__ == '__main__':
    main()
