"""Required synthetic cases against the committed detector."""
import sys
sys.dont_write_bytecode=True
import detector_run_r3_eval_a2_executor as h
import numpy as np
import cusum_detector_v2 as detector
import csv,json

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

if __name__=='__main__':
    try:
        unit_gate()
        h.constants_gate()
    except BaseException as error:
        h.mark_halt('unit_gate',error)
        raise
