"""Synthetic detector gates and the fixed stage 1 calibration procedure."""
import sys
sys.dont_write_bytecode = True
import detector_run_cal_executor as h
import numpy as np
import cusum_detector_v2 as detector
import csv
import io
import json
from collections import Counter


def csv_output(name, rows, fields=None):
    if fields is None:
        fields = list(rows[0])
    with (h.OUT / name).open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({k: 'null' if v is None else v for k, v in row.items()})
        f.flush()
        h.os.fsync(f.fileno())


def unit_gate():
    h.pins()
    parameters = {c: {'reference': 10.0, 'allowance': 1.0, 'threshold': 3.0}
                  for c in ('entropy', 'g', 'L')}
    cases = []
    sequences = []
    sigma = 2.0
    for channel, field, direction, harmful, harmless in (
        ('entropy', 'h_n_latest', 'lower', 8.0, 12.0),
        ('g', 'g', 'upper', 12.0, 8.0),
        ('L', 'L_t', 'lower', 8.0, 12.0),
    ):
        measured = {}
        for kind, value in (('reference', 10.0), ('harmful', harmful), ('harmless', harmless)):
            records = [{'step': step, 'h_n_latest': 10.0, 'g': 10.0, 'L_t': 10.0}
                       for step in range(30)]
            for row in records:
                row[field] = value
            result = detector.detect(records, parameters)
            curve = result['channels'][channel]
            measured[kind] = result
            for i, row in enumerate(records):
                sequences.append({'case': kind, 'channel': channel, 'step': row['step'],
                                  'value': value, 'start_statistic': curve['start_statistics'][i],
                                  'candidate_statistic': curve['candidate_statistics'][i],
                                  'statistic': curve['statistics'][i], 'alarm': curve['alarms'][i],
                                  'heartbeat_counter': result['heartbeats'][i]['heartbeat_counter']})
        ref = measured['reference']['channels'][channel]
        harm = measured['harmful']['channels'][channel]
        harmless_curve = measured['harmless']['channels'][channel]
        unthresholded = detector.channel_cusum(
            range(30), [harmful] * 30, reference=10.0, allowance=1.0,
            direction=direction, threshold=None)
        increments = [unthresholded['statistics'][i] - unthresholded['start_statistics'][i]
                      for i in range(10, 30)]
        alarm_steps = [i for i, alarm in enumerate(harm['alarms']) if alarm]
        expected_alarms = list(range(12, 30, 3))
        cases.extend([
            {'channel': channel, 'case': 'at_reference',
             'measured_maximum': max(ref['statistics']), 'measured_alarm_count': sum(ref['alarms']),
             'passed': max(ref['statistics']) == 0.0 and not any(ref['alarms'])},
            {'channel': channel, 'case': 'one_sigma_harmful_shift', 'sigma': sigma, 'allowance': 1.0,
             'measured_increments': sorted(set(increments)), 'expected_increment': sigma - 1.0,
             'measured_alarm_steps': alarm_steps, 'expected_alarm_steps': expected_alarms,
             'passed': all(x == 1.0 for x in increments) and alarm_steps == expected_alarms},
            {'channel': channel, 'case': 'harmless_shift',
             'measured_maximum': max(harmless_curve['statistics']),
             'measured_alarm_count': sum(harmless_curve['alarms']),
             'passed': max(harmless_curve['statistics']) == 0.0 and not any(harmless_curve['alarms'])},
            {'channel': channel, 'case': 'reset_after_alarm',
             'measured_post_alarm_statistics': [harm['statistics'][i] for i in alarm_steps],
             'measured_next_start_statistics': [harm['start_statistics'][i + 1] for i in alarm_steps],
             'passed': all(harm['statistics'][i] == 0.0 and harm['start_statistics'][i + 1] == 0.0
                           for i in alarm_steps)},
            {'channel': channel, 'case': 'burn_in', 'steps': list(range(10)),
             'measured_statistics': list(harm['statistics'][:10]),
             'measured_alarm_count': sum(harm['alarms'][:10]),
             'passed': all(x == 0.0 for x in harm['statistics'][:10]) and not any(harm['alarms'][:10])},
            {'channel': channel, 'case': 'heartbeat',
             'measured_counts': {kind: len(value['heartbeats']) for kind, value in measured.items()},
             'expected_count_each': 30,
             'passed': all(len(v['heartbeats']) == 30 and
                           [r['heartbeat_counter'] for r in v['heartbeats']] == list(range(1, 31)) and
                           all(r['record_type'] == 'heartbeat' for r in v['heartbeats']) and
                           all(r['record_type'] == 'alarm' for r in v['alarm_records'])
                           for v in measured.values())},
        ])
        if channel == 'L':
            cases.append({'channel': 'L', 'case': 'comparison_channel_separation',
                          'measured_L_alarm_steps': alarm_steps,
                          'measured_operational_alarm_steps': list(measured['harmful']['operational_alarm_steps']),
                          'passed': bool(alarm_steps) and not measured['harmful']['operational_alarm_steps']})
    csv_output(h.P + 'unit_sequences.csv', sequences)
    result = {'passed': all(c['passed'] for c in cases), 'cases': cases,
              'identity': h.identity(), 'runtime': h.metadata(np), 'utc': h.now(),
              'model_steps_executed': 0}
    h.write(h.P + 'unit_gate.json', result)
    print(json.dumps(result), flush=True)
    if not result['passed']:
        raise RuntimeError('Detector synthetic unit gate failed')


def calibration():
    h.check_stop()
    h.pins()
    plan = h.read(h.P + 'plan.json')
    execution = h.read(h.P + 'execution.json')
    if execution['status'] != 'COMPLETE':
        raise RuntimeError('Calibration requires a completed honest batch')
    runs = []
    records = {}
    for seed in plan['seeds']:
        result = h.completed('H_' + str(seed), 'H', seed)
        if result is None:
            raise RuntimeError('A calibration completion record is missing')
        runs.append(result)
        with (h.OUT / result['raw_log']).open(encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
        records[seed] = [{'step': int(r['step']), 'h_n_latest': float(r['h_n_latest']),
                          'g': float(r['g']), 'L_t': float(r['L_t'])} for r in rows]
    channels = {}
    maxima_rows = []
    for channel, field, direction in (('entropy', 'h_n_latest', 'lower'),
                                      ('g', 'g', 'upper'), ('L', 'L_t', 'lower')):
        values = np.asarray([row[field] for seed in plan['seeds'] for row in records[seed]
                             if row['step'] >= 10], dtype=float)
        reference = float(np.median(values))
        sigma = float(np.std(values, ddof=1))
        allowance = 0.5 * sigma
        maxima = []
        per_run = []
        for seed in plan['seeds']:
            rows = records[seed]
            curve = detector.channel_cusum(
                [r['step'] for r in rows], [r[field] for r in rows],
                reference=reference, allowance=allowance, direction=direction, threshold=None)
            maximum = max(curve['statistics'], default=0.0)
            maxima.append(maximum)
            count = sum(r['step'] >= 10 for r in rows)
            per_run.append({'seed': seed, 'maximum_statistic': maximum,
                            'post_burn_in_records': count})
            maxima_rows.append({'channel': channel, 'seed': seed,
                                'post_burn_in_records': count, 'maximum_statistic': maximum})
        percentile = plan['calibration']['threshold_percentiles'][channel]
        threshold = float(np.percentile(maxima, percentile, method='linear'))
        channels[channel] = {'reference': reference, 'allowance': allowance, 'threshold': threshold,
                             'sigma_sample_ddof_1': sigma, 'record_count': int(values.size),
                             'threshold_percentile': percentile, 'percentile_method': 'linear',
                             'per_run_maxima': per_run}
    constants = {'stage': 1, 'channels': channels, 'calibration_run_count': len(runs),
                 'seeds': plan['seeds'], 'burn_in_steps': 10, 'head': plan['head'],
                 'detector_note_blob_sha1': plan['design_blob_sha1'], 'identity': h.identity(),
                 'created_utc': h.now(), 'publication_status': 'Not consumed by stage 2; operator publication required'}
    h.write(h.P + 'constants.json', constants)
    csv_output(h.P + 'maxima.csv', maxima_rows)
    heartbeats = []
    alarms = []
    descriptive = []
    for seed in plan['seeds']:
        output = detector.detect(records[seed], channels)
        if len(output['heartbeats']) != len(records[seed]):
            raise RuntimeError('Detector heartbeat count differs from completed steps')
        heartbeats.extend({'seed': seed, **row} for row in output['heartbeats'])
        alarms.extend({'seed': seed, **row} for row in output['alarm_records'])
        for channel in channels:
            sequence = output['channels'][channel]['alarms']
            descriptive.append({'seed': seed, 'channel': channel, 'alarm_count': sum(sequence),
                                'any_alarm': any(sequence), 'completed_steps': len(records[seed])})
    csv_output(h.P + 'heartbeats.csv', heartbeats)
    csv_output(h.P + 'alarms.csv', alarms,
               ['seed', 'record_type', 'step', 'channel', 'statistic_before_reset',
                'statistic_after_reset', 'operational_channel'])
    csv_output(h.P + 'descriptive_alarms.csv', descriptive)
    summaries = []
    for r in runs:
        summaries.append({key: r[key] for key in (
            'arm', 'seed', 'steps_completed', 'end_reason', 'extinct',
            'shape_fallback_increase_step_0', 'shape_fallback_permitted_increase_after_step_0',
            'shape_fallback_nonpermitted_increase_count', 'first_fewer_than_two_novelty_vectors_step',
            'adapter_active_steps', 'action_modified_steps', 'recorder_rng_unchanged_calls',
            'raw_entropy_exact_matches', 'elapsed_seconds', 'raw_log', 'raw_log_sha256')})
    csv_output(h.P + 'runs.csv', summaries)
    result = {'channels_with_any_alarm': {channel: sum(row['any_alarm'] for row in descriptive
                                                      if row['channel'] == channel) for channel in channels},
              'calibration_runs': len(runs), 'total_completed_steps': sum(r['steps_completed'] for r in runs),
              'heartbeat_records': len(heartbeats), 'alarm_records': len(alarms),
              'step_0_fallback_distribution': dict(Counter(r['shape_fallback_increase_step_0'] for r in runs)),
              'permitted_after_step_0_fallback_total': sum(r['shape_fallback_permitted_increase_after_step_0'] for r in runs),
              'nonpermitted_fallback_increase_count': sum(r['shape_fallback_nonpermitted_increase_count'] for r in runs),
              'runs_reaching_fewer_than_two_novelty_vectors': sum(r['first_fewer_than_two_novelty_vectors_step'] is not None for r in runs),
              'end_reasons': dict(Counter(r['end_reason'] for r in runs)),
              'no_attack_arm_executed': True, 'stage_2_started': False, 'utc': h.now(),
              'source_pins_end': h.pins(), 'identity': h.identity()}
    h.write(h.P + 'calibration_summary.json', result)
    print(json.dumps({'calibration': 'COMPLETE', **result}), flush=True)


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'unit':
            unit_gate()
        elif sys.argv[1] == 'calibrate':
            calibration()
        else:
            raise ValueError('Expected unit or calibrate')
    except BaseException as error:
        h.mark_halt('analysis_' + sys.argv[1], error)
        raise
