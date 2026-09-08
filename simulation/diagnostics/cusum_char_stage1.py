"""Stage 1 measurement harness. No production behavior is replaced."""

import sys

sys.dont_write_bytecode = True

import argparse
import csv
import hashlib
import inspect
import io
import json
import os
from pathlib import Path
import subprocess
import time
import traceback
from datetime import datetime, timezone

OUTPUT_DIR = Path(__file__).resolve().parent
REPO_ROOT = OUTPUT_DIR.parent.parent
PREFIX = 'cusum_char_'
REPORT_NAME = 'cusum_char_stage1_report.md'
BASELINE_NAME = 'cusum_char_stage1_baseline_summary.json'
PILOT_NAME = 'cusum_char_stage1_pilot_summary.json'
MANIFEST_NAME = 'cusum_char_stage1_manifest.json'
HORIZON = 300
FIRST_SEED = 1835086199
MACHINE = os.environ['COMPUTERNAME']
EXPECTED_HEAD = '1261c9f430411b9fa0060a7384bf4ec5175e4f4e'
EVIDENCE_TAG = 'attack-v2-revalidation-evidence'
PINNED_PATH = (
    'data/attack_vector_revalidation_v2/linux/sub_threshold_drift/'
    'full_5ac6a2e_sub_threshold_drift/results.csv'
)
EXPECTED_BLOB = 'f628fb81c29104368d99977bf88ea82faee9f881'
ACTION_KEYS = (
    'x_compute', 'x_bio_welfare', 'x_novelty_agency',
    'x_institutional_capacity', 'x_transfer_comprehension', 'x_resilience',
    'c_protective', 'c_suppressive',
)
OUTCOMES = ('attack_succeeded', 'defense_fired', 'extinct', 'collapsed')
OPERATOR_STATEMENT = '''"If the honest baseline maximum of total_suppression exceeds 0.75, the v2
sub_threshold_drift success metric does not discriminate attack from baseline,
the reported 100 percent defended attack rate is uninformative about the defense,
and paper Section VIII.9 requires correction before upload. If the honest
baseline stays below 0.75, the defended breach is attack-caused despite the
roughly 0.11 ceiling implied by the seventeen-step suppression window, that
ceiling estimate is wrong, and the mechanism is re-derived from the per-step logs
before any further claim is made. Either outcome is reported. The peak-constraint
figure stays in the paper in both cases."'''


class StageHalt(RuntimeError):
    pass


def allowed_output(path):
    resolved = Path(path).resolve()
    return resolved.parent == OUTPUT_DIR and resolved.name.startswith(PREFIX)


def audit_writes(event, args):
    if event == 'open':
        path, mode, flags = args
        writing = (
            isinstance(mode, str) and any(c in mode for c in 'wax+')
        ) or (isinstance(flags, int) and flags & (
            os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC
        ))
        if writing and not isinstance(path, int) and not allowed_output(path):
            raise StageHalt(f'Write scope rejected before opening: {path}')
    elif event in ('os.remove', 'os.rmdir', 'os.mkdir'):
        raise StageHalt(f'Unneeded filesystem mutation rejected: {event}')
    elif event in ('os.rename', 'os.link', 'os.symlink'):
        raise StageHalt(f'Unneeded filesystem mutation rejected: {event}')


sys.addaudithook(audit_writes)
sys.path.insert(0, str(REPO_ROOT / 'simulation'))


def now():
    return datetime.now(timezone.utc).isoformat()


def output_path(name):
    path = OUTPUT_DIR / name
    if not allowed_output(path):
        raise StageHalt(f'Invalid output path: {path}')
    return path


def write_json(name, value):
    output_path(name).write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n',
        encoding='utf-8',
    )


def read_json(name):
    path = output_path(name)
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None


def write_report(text):
    if '\u2014' in text:
        raise StageHalt('An em dash was found in the proposed report')
    output_path(REPORT_NAME).write_text(text, encoding='utf-8')


def git_read(*args):
    return subprocess.check_output(['git', *args], cwd=REPO_ROOT)


def pinned_rows():
    blob = git_read('show', f'{EVIDENCE_TAG}:{PINNED_PATH}')
    digest = hashlib.sha1(
        b'blob ' + str(len(blob)).encode('ascii') + b'\0' + blob
    ).hexdigest()
    if digest != EXPECTED_BLOB:
        raise StageHalt(f'Pinned blob mismatch: {digest}')
    rows = list(csv.DictReader(io.StringIO(blob.decode('utf-8'))))
    if len(rows) != 200:
        raise StageHalt(f'Unexpected pinned row count: {len(rows)}')
    return rows


def expected_row(rows, defended):
    selected = [row for row in rows if (
        float(row['parameter_phi']) == 10.0
        and int(row['replicate']) == 0
        and row['defense_active'] == str(defended)
    )]
    if len(selected) != 1 or int(selected[0]['seed']) != FIRST_SEED:
        raise StageHalt('Pinned phi=10 replicate=0 selection did not resolve uniquely')
    return {key: selected[0][key] == 'True' for key in OUTCOMES}


class Recorder:
    def __init__(self, run_id, seed, benign):
        self.run_id = run_id
        self.seed = seed
        self.benign = benign
        self.rows = []
        self.filename = f'cusum_char_stage1_{run_id}_steps.csv'
        self.handle = output_path(self.filename).open('x', newline='', encoding='utf-8')
        fields = [
            'run_id', 'seed', 'step', 'total_suppression', 'c_suppressive',
            'c_protective', 'population', 'adapter_active', 'adapter_score',
        ]
        if not benign:
            fields += ['alarm', 'defense_fired'] + list(ACTION_KEYS[:6])
        self.writer = csv.DictWriter(self.handle, fieldnames=fields)
        self.writer.writeheader()
        self.handle.flush()

    def record(self, model):
        dc = model.datacollector
        step = len(dc['population']) - 1
        if step != len(self.rows):
            raise StageHalt(f'Nonsequential collector index in {self.run_id}: {step}')
        row = {
            'run_id': self.run_id,
            'seed': self.seed,
            'step': step,
            'total_suppression': float(dc['total_suppression'][-1]),
            'c_suppressive': float(dc['c_suppressive'][-1]),
            'c_protective': float(dc['c_protective'][-1]),
            'population': int(dc['population'][-1]),
            'adapter_active': bool(dc['v2_attack_active'][-1]),
            'adapter_score': float(dc['v2_adapter_cusum_score'][-1]),
        }
        if not self.benign:
            # For this vector the event flag is set directly from local alarm.
            # No other defense event can set it in the runner's incumbent path.
            row['alarm'] = bool(model.v2_adapter_step_event['defense_fired'])
            row['defense_fired'] = bool(dc['v2_defense_fired'][-1])
            for key in ACTION_KEYS:
                value = float(model._last_v2_action[key])
                if key in row and row[key] != value:
                    raise StageHalt(f'Committed action/collector mismatch: {key}')
                row[key] = value
        self.rows.append(row)
        self.writer.writerow(row)
        self.handle.flush()
        if self.benign and row['adapter_active']:
            raise StageHalt(f'Adapter active in benign run {self.run_id}, step {step}')
        if (step + 1) % 25 == 0:
            print(json.dumps({'run': self.run_id, 'steps_logged': step + 1}), flush=True)

    def close(self):
        self.handle.close()


def peak(rows):
    return max(rows, key=lambda row: row['total_suppression']) if rows else None


def baseline_summary(recorder, model, elapsed):
    rows = recorder.rows
    return {
        'run_id': recorder.run_id,
        'seed': recorder.seed,
        'steps': len(rows),
        'peak': peak(rows),
        'pre50_peak': peak([row for row in rows if row['step'] < 50]),
        'from50_peak': peak([row for row in rows if row['step'] >= 50]),
        'steps_above_075': sum(row['total_suppression'] > 0.75 for row in rows),
        'adapter_active_steps': sum(row['adapter_active'] for row in rows),
        'max_adapter_score': max(row['adapter_score'] for row in rows),
        'elapsed_seconds': elapsed,
        'raw_log': recorder.filename,
        'config': dict(model.config),
    }


def baseline_section(data):
    if not data or not data['runs']:
        return '## Task 1: honest baseline\n\nNot yet measured.\n'
    runs = data['runs']
    above = sum(run['peak']['total_suppression'] > 0.75 for run in runs)
    text = [
        '## Task 1: honest baseline\n',
        f'**Measured: {above} of {len(runs)} completed honest runs exceeded 0.75.**\n',
        '| Seed | Recorded steps | Maximum total suppression | First maximum step | c_suppressive there | c_protective there | Steps > 0.75 |',
        '| ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for run in runs:
        p = run['peak']
        text.append(f"| {run['seed']} | {run['steps']} | {p['total_suppression']:.17g} | {p['step']} | {p['c_suppressive']:.17g} | {p['c_protective']:.17g} | {run['steps_above_075']} |")
    text += [
        '', 'Maxima below are measured separately from the same logs. Step ranges are inclusive. The first occurrence is used when a maximum is tied.',
        '', '| Seed | Max, steps 0-49 | First maximum step | Max, steps 50-299 | First maximum step |',
        '| ---: | ---: | ---: | ---: | ---: |',
    ]
    for run in runs:
        a, b = run['pre50_peak'], run['from50_peak']
        bvalue = f"{b['total_suppression']:.17g}" if b else 'none recorded'
        bstep = b['step'] if b else 'none'
        text.append(f"| {run['seed']} | {a['total_suppression']:.17g} | {a['step']} | {bvalue} | {bstep} |")
    active = sum(run['adapter_active_steps'] for run in runs)
    total = sum(run['steps'] for run in runs)
    text += ['', f'Measured adapter activity: {active} active steps out of {total} recorded steps.']
    if active == 0:
        text.append('The adapter reported inactive on every recorded step of every completed run.')
    text.append(f"Measured maximum recorded adapter score across these runs: {max(run['max_adapter_score'] for run in runs):.17g}.")
    text += [
        '', 'Seed derivation: 1835086199 plus offsets 0, 1, 2, 3, and 4. This choice is arbitrary and only for spread. Phi is 10.0, requested horizon is 300, policy is optimize_u_sys_v2, and attack_vector_v2 is absent from the config.',
        '', 'Other settings match the full defended runner configuration: 200 starting agents, 300 candidates, 20 rollout steps, use_cop=True, attribution and drift checks enabled, and cop_cusum_drift=True. The attack key is omitted before construction. Sensor noise remains unset. The retained attack_step=50 config value does not activate an adapter without an attack vector.',
    ]
    if data['complete']:
        if above:
            text += ['', 'Under the operator-fixed statement recorded before these measurements: the v2 sub_threshold_drift success metric does not discriminate attack from baseline; the reported 100 percent defended attack rate is uninformative about the defense; and paper Section VIII.9 requires correction before upload. The peak-constraint figure stays in the paper. No repair or paper edit was made.']
        else:
            text += ['', 'The honest baseline maximum stayed at or below 0.75 in all five runs. The other branch of the recorded operator statement governs subsequent interpretation of a reproduced defended breach.']
    return '\n'.join(text) + '\n'


def reproduction_section(data):
    text = ['## Task 2: reproduction gate\n', '| Arm | Boolean | Pinned | Measured | Exact match |', '| --- | --- | --- | --- | --- |']
    for run in data['runs']:
        for key in OUTCOMES:
            expected, actual = run['expected'][key], run['observed'][key]
            text.append(f"| {run['arm']} | {key} | {expected} | {actual} | {expected == actual} |")
    text += ['', f"Pinned input read through {EVIDENCE_TAG}: `{PINNED_PATH}`. Git blob SHA verified as `{EXPECTED_BLOB}`; 200 rows. Matching rows use parameter_phi=10.0 and replicate=0, seed 1835086199 in both arms."]
    return '\n'.join(text) + '\n'


def timing_analysis(run):
    rows = run['rows']
    threshold = run['threshold']
    first = lambda condition: next((row['step'] for row in rows if condition(row)), None)
    cross = first(lambda row: row['adapter_score'] > threshold)
    alarm = first(lambda row: row['alarm'])
    breach = first(lambda row: row['total_suppression'] > 0.75)
    previous = run['initial_score']
    increments = {'inactive': [], 'active': []}
    for row in rows:
        increments['active' if row['adapter_active'] else 'inactive'].append(row['adapter_score'] - previous)
        previous = row['adapter_score']
    after = [row for row in rows if alarm is not None and row['step'] >= alarm]
    return {
        'first_score_exceedance': cross,
        'first_alarm': alarm,
        'first_breach': breach,
        'breach_minus_alarm': breach - alarm if breach is not None and alarm is not None else None,
        'breach_minus_score_exceedance': breach - cross if breach is not None and cross is not None else None,
        'alarm_steps': sum(row['alarm'] for row in rows),
        'observed_steps_from_alarm': len(after),
        'requested_steps_from_alarm': HORIZON - alarm if alarm is not None else None,
        'every_observed_step_from_alarm': all(row['alarm'] for row in after) if after else None,
        'increments': {key: {'count': len(values), 'minimum': min(values) if values else None, 'maximum': max(values) if values else None, 'distinct': sorted(set(values))} for key, values in increments.items()},
        'peak': peak(rows),
    }


def timing_section(data):
    text = ['## Task 2: timing pilot after exact reproduction\n', 'The following timing and state quantities are measured from the pilot logs. Step indices are zero-based. No timing interpretation was performed before the reproduction gate passed in both arms. The score threshold is read as 0.5 from the unchanged adapter default; the runner supplies no override.\n']
    text += ['| Arm | Measured elapsed seconds | Recorded steps | First score > threshold | First actual alarm | First suppression > 0.75 | Breach minus actual alarm |', '| --- | ---: | ---: | --- | --- | --- | --- |']
    for run in data['runs']:
        a = run['analysis']
        text.append(f"| {run['arm']} | {run['elapsed_seconds']:.6f} | {len(run['rows'])} | {a['first_score_exceedance']} | {a['first_alarm']} | {a['first_breach']} | {a['breach_minus_alarm']} |")
    text += ['', 'Sign convention: gap = breach step minus actual alarm step. Negative means the breach precedes the alarm; positive means it follows. None means an event did not occur in the recorded run, so that gap is undefined. A score crossing without an enabled alarm is reported separately.']
    for run in data['runs']:
        a = run['analysis']
        text += ['', f"### {run['arm']} accumulator and alarm observations", '']
        for status in ('inactive', 'active'):
            inc = a['increments'][status]
            text.append(f"Measured {status}-step score differences: {inc['count']} observations; minimum {inc['minimum']!r}; maximum {inc['maximum']!r}; distinct observed differences {inc['distinct']!r}.")
        text += [
            f"The first logged score is differenced against the measured initialization value of {run['initial_score']!r}. These increments are calculated from observed score values, not copied from the configured signal or a legacy calculation.",
            f"Measured alarm steps: {a['alarm_steps']}. Recorded steps from first actual alarm through the last recorded step, inclusive: {a['observed_steps_from_alarm']}. Steps from first alarm through requested step 299, inclusive: {a['requested_steps_from_alarm']}. Alarm present on every observed step from first alarm onward: {a['every_observed_step_from_alarm']}.",
            f"Additional comparison, breach minus first score-threshold exceedance: {a['breach_minus_score_exceedance']} steps. This does not relabel an undefended score crossing as an actual alarm.",
            f"Measured peak total_suppression: {a['peak']['total_suppression']:.17g}, first occurring at step {a['peak']['step']}.",
            '', 'Committed actions below are measured; displayed values are rounded to 12 significant digits. Raw CSVs retain round-trippable float values. The first score-crossing action is also included if the arm has no actual alarm.',
            '', '| Step | x_compute | x_bio_welfare | x_novelty_agency | x_institutional_capacity | x_transfer_comprehension | x_resilience | c_protective | c_suppressive |',
            '| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
        ]
        selected = set(range(50, 56))
        for index in (a['first_alarm'], a['first_score_exceedance']):
            if index is not None:
                selected.update((index, index + 1))
        for row in run['rows']:
            if row['step'] in selected:
                text.append('| ' + str(row['step']) + ' | ' + ' | '.join(f'{row[key]:.12g}' for key in ACTION_KEYS) + ' |')
    elapsed = [run['elapsed_seconds'] for run in data['runs']]
    balanced = 20 * sum(elapsed)
    conservative = 40 * max(elapsed)
    text += [
        '', '### Runtime projection', '',
        f"Machine: {data['machine']}. Elapsed seconds above are measured wall-clock time around the unmodified runner call with per-step logging enabled, including construction and log writes. Runs were sequential.",
        f'Projected runtime for 40 runs, assuming 20 per arm and these measured run durations: {balanced:.3f} seconds ({balanced / 3600:.6f} hours). The 3-hour budget is 10800 seconds. Projection clears that bound: {balanced <= 10800}.',
        f'Using the slower measured arm for all 40 gives {conservative:.3f} seconds ({conservative / 3600:.6f} hours); clears the bound: {conservative <= 10800}. These are projections, not measurements of a full set. No full set was launched.',
    ]
    return '\n'.join(text) + '\n'


def metric_section(runner):
    source = inspect.getsource(runner._attack_success)
    text = ['## Task 3: cross-vector metric shape, read from source\n', 'Complete `_attack_success` definition, read from `simulation/run_attack_vector_revalidation_v2.py:345-370`:\n', '```python\n' + source.rstrip() + '\n```\n', '| Live vector | Temporal input shape | Quantity and threshold read from source |', '| --- | --- | --- |']
    entries = [
        ('sybil_capture', 'Full recorded action-modification series; no slice', 'Any v2_attack_action_modified is true; no numeric threshold.'),
        ('measurement_tampering', 'Full recorded yield_event_log; no slice', 'Any event has honest_fires true and fires_before_ratification false; no numeric threshold.'),
        ('ledger_compromise', 'Full recorded action-modification series; no slice', 'Any v2_attack_action_modified is true; no numeric threshold.'),
        ('successor_contamination', 'Cumulative state flag or full recorded action-modification series; no slice', 'contamination_occurred is true or any v2_attack_action_modified is true; no numeric threshold.'),
        ('opaque_reasoning', 'Full recorded action-modification series; no slice', 'Any v2_attack_action_modified is true; no numeric threshold.'),
        ('bootstrap_subversion', 'Full recorded action-modification series; no slice', 'Any v2_attack_action_modified is true; no numeric threshold.'),
        ('evaluator_collusion', 'Full recorded action-modification series; no slice', 'Any v2_attack_action_modified is true; no numeric threshold.'),
        ('sub_threshold_drift', 'Full recorded total_suppression series; no slice', 'Nonempty series and maximum total_suppression > 0.75.'),
        ('engineered_fragility', 'Full recorded resilience_stock series; no slice', 'Nonempty series and minimum resilience_stock < 0.25.'),
        ('biological_veto_capture', 'Cumulative model counter; no series slice', 'yield_condition_blocked_count > 0.'),
    ]
    for vector, shape, expression in entries:
        text.append(f'| {vector} | {shape} | {expression} |')
    text += ['', 'Full recorded input means no windowed slice in this success function. Event logs and counters are populated by their existing upstream execution conditions. This table reports expression shape only and makes no correctness assessment.']
    return '\n'.join(text) + '\n'


def render_report(manifest, baseline=None, pilot=None, runner=None, halt=None):
    parts = [
        '# CUSUM arc, Stage 1: honest baseline and timing pilot\n',
        'Instrument characterization of an existing mechanism. No hypothesis about the framework is under test. These outputs are not registered characterization data and do not cross the pre-registration boundary.\n',
        '## Operator-fixed statement recorded before results\n',
        f"Recorded at {manifest['statement_recorded_utc']}, before the first run began. The operator calls this pre-registration; it fixes interpretation for this instrument stage and does not change the scope classification above.\n",
        OPERATOR_STATEMENT + '\n',
        baseline_section(baseline),
    ]
    if halt:
        parts += ['\n## HALT\n', halt + '\n']
    if pilot and pilot['runs']:
        parts.append(reproduction_section(pilot))
        if pilot.get('complete') and pilot.get('reproduction_passed') and not halt:
            parts.append(timing_section(pilot))
            parts.append(metric_section(runner))
        else:
            parts.append('Timing is not interpreted because the two-arm reproduction gate has not passed. Task 3 is not completed after a reproduction failure.\n')
    parts += [
        '\n## Provenance, instrument, and artifacts\n',
        f"Machine: {manifest['machine']}. HEAD: `{manifest['head']}`. Python: {manifest.get('python', 'not yet imported')}. NumPy: {manifest.get('numpy', 'not yet imported')}.\n",
        'Baseline settings and runtime summaries are in `cusum_char_stage1_baseline_summary.json`. Pilot outcome records, expected rows, per-step measurements, and runtime values are in `cusum_char_stage1_pilot_summary.json` when that phase has run. Per-step CSV filenames and configuration metadata are recorded in those JSON files. The standalone script is `cusum_char_stage1.py`; the process manifest is `cusum_char_stage1_manifest.json`.\n',
        'The recorder subclasses GardenModel only to call the original step and then read committed state. For the pilot, the unchanged runner factory uses this logging subclass; the unchanged run_single computes the four reproduction booleans. No random calls are added by logging.\n',
        'The pilot alarm column observes the adapter event defense_fired flag. Read from adapter source lines 329-339 and 158-162: this flag is set directly from local alarm for this vector; no other defense sets it in this incumbent-only path. The collector defense_fired column is logged separately. A score-threshold exceedance is analyzed separately from the defense-gated alarm.\n',
        'All cusum_char_ artifacts are excluded from the authoritative manifest by prefix, per the operator instruction. This manifest records only instrument artifacts and does not modify the authoritative evidence manifest. No production source, success expression, threshold, defense wiring, paper, advisor, inventory, or other diagnostic was edited. Bytecode writes are disabled, and the instrument rejects file opens for writing outside the allowed directory and prefix.\n',
        'The operator runs the containment diff. No Git write operation is performed. No full 40-run set is launched.\n',
        'Instrument startup note: before any simulation began, the write guard blocked a Windows platform lookup that attempted to open the NUL device read-write. The instrument was changed to read the existing COMPUTERNAME environment value instead. No device open or simulation occurred in that failed startup; no scientific source or configuration was changed.\n',
    ]
    write_report('\n'.join(parts))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=('baseline', 'pilot'), required=True)
    args = parser.parse_args()
    manifest = read_json(MANIFEST_NAME)
    baseline = read_json(BASELINE_NAME)
    pilot = read_json(PILOT_NAME)
    if args.phase == 'baseline':
        if manifest is not None:
            raise StageHalt('Stage 1 manifest already exists; refusing an unrequested rerun')
        manifest = {
            'statement_recorded_utc': now(),
            'machine': MACHINE,
            'head': git_read('rev-parse', 'HEAD').decode().strip(),
            'python': sys.version.replace('\n', ' '),
            'scope': 'instrument characterization; not registered characterization data',
            'authoritative_manifest_exclusion': 'all cusum_char_ artifacts excluded by prefix',
            'phases': {},
        }
        write_json(MANIFEST_NAME, manifest)
        render_report(manifest)
    if manifest is None:
        raise StageHalt('Baseline must be recorded before the pilot')
    try:
        if git_read('rev-parse', 'HEAD').decode().strip() != EXPECTED_HEAD:
            raise StageHalt('HEAD differs from the resolved Stage 0 substrate')
        import numpy as np
        import run_attack_vector_revalidation_v2 as runner
        manifest['numpy'] = np.__version__
        manifest['source_sha256'] = {
            name: hashlib.sha256((REPO_ROOT / 'simulation' / name).read_bytes()).hexdigest()
            for name in ('model.py', 'agents.py', 'attack_adapter_v2.py', 'run_attack_vector_revalidation_v2.py')
        }
        write_json(MANIFEST_NAME, manifest)
        original_model = runner.GardenModel
        current_recorder = None

        class RecordedModel(original_model):
            def __init__(self, *model_args, **model_kwargs):
                super().__init__(*model_args, **model_kwargs)
                current_recorder.initial_score = float(self.v2_adapter_cusum_score)
                current_recorder.model_config = dict(self.config)

            def step(self):
                alive = super().step()
                current_recorder.record(self)
                return alive

        if args.phase == 'baseline':
            baseline = {'complete': False, 'runs': [], 'started_utc': now()}
            render_report(manifest, baseline)
            write_json(BASELINE_NAME, baseline)
            for offset in range(5):
                seed = FIRST_SEED + offset
                run_id = f'baseline_seed{seed}'
                current_recorder = Recorder(run_id, seed, True)
                config = {
                    'policy': 'optimize_u_sys_v2', 'random_seed': seed,
                    'phi': 10.0, 'attack_step': 50,
                    'n_candidates_v2': 300, 'rollout_steps_v2': 20,
                    'bootstrap_turn_step_v2': 20, 'shock_step': 0,
                    'shock_magnitude': 0.15,
                }
                started = time.perf_counter()
                try:
                    model = RecordedModel(
                        n_agents=200, ai_policy='optimize_u_sys_v2', use_cop=True,
                        config=config, cop_attribution_check=True,
                        cop_drift_check=True, cop_cusum_drift=True,
                    )
                    if 'attack_vector_v2' in model.config:
                        raise StageHalt('Attack key exists in honest baseline config')
                    for step in range(HORIZON):
                        if not model.step():
                            break
                    elapsed = time.perf_counter() - started
                    baseline['runs'].append(baseline_summary(current_recorder, model, elapsed))
                finally:
                    current_recorder.close()
                write_json(BASELINE_NAME, baseline)
                render_report(manifest, baseline)
                print(json.dumps({'baseline_run_complete': run_id, 'max_total_suppression': baseline['runs'][-1]['peak']['total_suppression']}), flush=True)
            baseline['complete'] = True
            baseline['reported_utc'] = now()
            manifest['phases']['baseline'] = 'complete and reported'
            write_json(BASELINE_NAME, baseline)
            write_json(MANIFEST_NAME, manifest)
            render_report(manifest, baseline)
            print(json.dumps({'baseline_complete': True, 'runs_above_075': sum(run['peak']['total_suppression'] > 0.75 for run in baseline['runs']), 'report': REPORT_NAME}), flush=True)
            return

        if not baseline or not baseline['complete'] or len(baseline['runs']) != 5:
            raise StageHalt('All five baseline runs must complete and be reported first')
        if any(run['adapter_active_steps'] for run in baseline['runs']):
            raise StageHalt('Baseline activity gate failed')
        if pilot is not None:
            raise StageHalt('Pilot artifact already exists; refusing an unrequested rerun')
        pinned = pinned_rows()
        pilot = {'complete': False, 'reproduction_passed': False, 'machine': MACHINE, 'runs': [], 'started_utc': now()}
        write_json(PILOT_NAME, pilot)
        runner.GardenModel = RecordedModel
        for defended, arm in ((False, 'undefended'), (True, 'defended')):
            task = {
                'vector': 'sub_threshold_drift', 'mode': 'full', 'machine': MACHINE,
                'parameters': {'phi': 10.0, 'defense_active': defended},
                'replicate': 0, 'seed': FIRST_SEED,
            }
            expected = expected_row(pinned, defended)
            current_recorder = Recorder(f'pilot_{arm}_seed{FIRST_SEED}', FIRST_SEED, False)
            started = time.perf_counter()
            try:
                row = runner.run_single(task)
                elapsed = time.perf_counter() - started
            finally:
                current_recorder.close()
            observed = {key: bool(row[key]) for key in OUTCOMES}
            run = {
                'arm': arm, 'task': task, 'expected': expected, 'observed': observed,
                'elapsed_seconds': elapsed, 'runner_elapsed_seconds': row['elapsed_seconds'],
                'threshold': 0.5, 'initial_score': current_recorder.initial_score,
                'config': current_recorder.model_config,
                'raw_log': current_recorder.filename, 'rows': current_recorder.rows,
                'runner_row': row,
            }
            pilot['runs'].append(run)
            write_json(PILOT_NAME, pilot)
            mismatches = [key for key in OUTCOMES if observed[key] != expected[key]]
            if mismatches:
                raise StageHalt(f"Substrate anomaly: {arm} reproduction mismatch in {', '.join(mismatches)}. Timing is not interpreted; no later run or task is started.")
            print(json.dumps({'pilot_run_complete': arm, 'reproduction_exact': True}), flush=True)
        pilot['reproduction_passed'] = True
        for run in pilot['runs']:
            run['analysis'] = timing_analysis(run)
        pilot['complete'] = True
        pilot['reported_utc'] = now()
        manifest['phases']['pilot'] = 'complete; exact reproduction in both arms'
        write_json(PILOT_NAME, pilot)
        write_json(MANIFEST_NAME, manifest)
        render_report(manifest, baseline, pilot, runner)
        print(json.dumps({'pilot_complete': True, 'reproduction_exact_both_arms': True, 'report': REPORT_NAME}), flush=True)
    except Exception as error:
        message = f'{type(error).__name__}: {error}'
        manifest['halt'] = {'utc': now(), 'phase': args.phase, 'message': message}
        write_json(MANIFEST_NAME, manifest)
        if pilot is not None:
            pilot['halt'] = message
            write_json(PILOT_NAME, pilot)
        render_report(manifest, baseline, pilot, halt=message)
        print('HALT: ' + message, flush=True)
        traceback.print_exc()
        raise SystemExit(2)


if __name__ == '__main__':
    main()
