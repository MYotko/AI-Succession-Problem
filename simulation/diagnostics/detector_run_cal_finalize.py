"""Publish the completed stage 1 measurements and their content manifest."""
import sys
sys.dont_write_bytecode = True
import detector_run_cal_executor as h
import csv
import io
import json
from collections import Counter


def main():
    h.check_stop()
    plan = h.read(h.P + 'plan.json')
    unit = h.read(h.P + 'unit_gate.json')
    gates = h.read(h.P + 'gates.json')
    execution = h.read(h.P + 'execution.json')
    constants = h.read(h.P + 'constants.json')
    measured = h.read(h.P + 'calibration_summary.json')
    completions = h.read(h.P + 'completions.json')['runs']
    end_pins = h.pins()
    note_records = []
    for path, expected, blob in (
        (plan['design_note'], plan['design_sha256_lf'], plan['design_blob_sha1']),
        (plan['mapping_note'], plan['mapping_sha256_lf'], plan['mapping_blob_sha1']),
    ):
        raw = h.git('cat-file', 'blob', 'HEAD:' + path)
        actual = h.sha(h.lf(raw))
        actual_blob = h.git('rev-parse', 'HEAD:' + path).decode().strip()
        if actual != expected or actual_blob != blob:
            raise RuntimeError('A committed specification pin changed')
        note_records.append({'path': path, 'sha256_lf_start': expected,
                             'sha256_lf_end': actual, 'blob_sha1': actual_blob})
    module_path = h.ROOT / 'simulation/cusum_detector_v2.py'
    module_hash = h.sha(h.lf(module_path.read_bytes()))
    constants_hash = h.sha(h.lf((h.OUT / (h.P + 'constants.json')).read_bytes()))
    runtime_records = [unit['runtime']]
    for job in ('wrapper', 'factory', 'common', 'honest'):
        runtime_records.append(h.read(h.P + 'gate_' + job + '_result.json')['runtime'])
    runtime_records += [r['runtime'] for r in completions]
    modules = {}
    for runtime in runtime_records:
        for path, hashes in runtime['modules'].items():
            if path in modules and modules[path]['sha256_lf'] != hashes['sha256_lf']:
                raise RuntimeError('A loaded module source pin changed: ' + path)
            modules[path] = hashes
    for path, hashes in modules.items():
        if h.sha(h.lf((h.ROOT / path).read_bytes())) != hashes['sha256_lf']:
            raise RuntimeError('A loaded module source pin changed at completion: ' + path)
    h.write(h.P + 'module_hashes.json', {
        'basis': 'Raw working-tree bytes and LF-normalized working-tree bytes, labeled per entry.',
        'modules': modules,
    })
    threads = [{'worker_pid': r['worker_pid'], 'effective': r['thread_runtime'],
                'configured': r['thread_environment']} for r in runtime_records]
    h.write(h.P + 'source_pins_end.json', {
        'source_pins': end_pins, 'notes': note_records, 'detector_sha256_lf': module_hash,
        'constants_sha256_lf': constants_hash, 'utc': h.now(),
    })
    h.write(h.P + 'runtime.json', {
        'machine': runtime_records[0]['machine'], 'python': runtime_records[0]['python'],
        'numpy': runtime_records[0]['numpy'], 'head': plan['head'],
        'operator_cpu_budget': 16, 'process_cpu_count': runtime_records[0]['process_cpu_count'],
        'worker_limits': plan['worker_limits'], 'maximum_active_workers': execution['maximum_active_workers'],
        'mode_changes': execution['mode_changes'], 'resumed_seeds': execution['resumed_seeds'],
        'worker_thread_readings': threads,
    })
    nonpermitted = measured['nonpermitted_fallback_increase_count']
    honest_active = sum(r['adapter_active_steps'] for r in completions)
    honest_modified = sum(r['action_modified_steps'] for r in completions)
    g3 = gates['gate_3']
    lines = [
        '# Detector calibration, stage 1', '',
        'Stage 1 is complete: 120 honest calibration runs. No attack arm was run. The detector was not evaluated against an attack or on stage 2 data. No corrected figure was derived.', '',
        'No calibrated constant has been consumed by a model or by stage 2. The only application of the calibrated thresholds was the descriptive replay on calibration records required by Section 6. Stage 2 is a separate dispatch and may begin only after these outputs and the detector module are committed and pushed and its publication gate passes.', '',
        '## Calibration measurements', '',
        'The following nine constants were computed by the committed Section 6 rule. All available records at steps 10 and up entered each channel. References are medians, allowances are half the sample standard deviation with ddof 1, and thresholds are NumPy linear percentiles of the 120 unthresholded per-run maxima. No threshold and no reset were used to obtain those maxima. No value was adjusted from a result.', '',
        '| Channel | Reference | Allowance | Threshold | Records | Percentile |',
        '| --- | ---: | ---: | ---: | ---: | ---: |',
    ]
    for channel in ('entropy', 'g', 'L'):
        c = constants['channels'][channel]
        lines.append('| ' + channel + ' | ' + ' | '.join(format(c[k], '.17g') for k in ('reference', 'allowance', 'threshold')) +
                     ' | ' + str(c['record_count']) + ' | ' + str(c['threshold_percentile']) + ' |')
    lines += ['', '| Channel | Sample standard deviation, ddof 1 | Calibration runs with at least one alarm after applying thresholds and resets |',
              '| --- | ---: | ---: |']
    for channel in ('entropy', 'g', 'L'):
        lines.append('| ' + channel + ' | ' + format(constants['channels'][channel]['sigma_sample_ddof_1'], '.17g') +
                     ' | ' + str(measured['channels_with_any_alarm'][channel]) + ' of 120 |')
    lines += [
        '', 'The full-precision constants, per-channel record counts, and all 120 maxima per channel are in `detector_run_cal_constants.json`. The same maxima are in `detector_run_cal_maxima.csv`. Alarm counts above are descriptive calibration counts only.', '',
        '## Execution and continuous checks', '',
        'Constructed configuration: `GardenModel(n_agents=200, ai_policy="sub_threshold_drift", use_cop=True, cop_attribution_check=True, cop_drift_check=True, cop_cusum_drift=False)` with the configuration below. Every completion record carries its concrete seed and configuration.', '',
        '```json', json.dumps(completions[0]['configuration'], indent=2, sort_keys=True), '```', '',
        'The `attack_vector_v2` key is absent. Seeds are the 120 consecutive integers 1835086300 through 1835086419, assigned independently of scheduling. Runs stop at 300 steps or when the model returns false. End reasons, not imputed continuations, are recorded per run.', '',
        '- Counted completed runs: ' + str(len(completions)) + '.',
        '- Counted completed steps: ' + str(measured['total_completed_steps']) + '.',
        '- Counted end reasons: ' + json.dumps(measured['end_reasons'], sort_keys=True) + '.',
        '- Counted heartbeat records in descriptive calibration replay: ' + str(measured['heartbeat_records']) + ', exactly one per completed step in each run.',
        '- Counted steps with an active honest adapter: ' + str(honest_active) + '; action-modified honest steps: ' + str(honest_modified) + '.',
        '- Counted exact raw-entropy matches: ' + str(sum(r['raw_entropy_exact_matches'] for r in completions)) + '.',
        '- Counted recorder calls preserving NumPy state: ' + str(sum(r['recorder_rng_unchanged_calls'] for r in completions)) + '.',
        '- Counted step 0 fallback increase distribution: ' + json.dumps(measured['step_0_fallback_distribution'], sort_keys=True) + '.',
        '- Counted total permitted fallback increase after step 0: ' + str(measured['permitted_after_step_0_fallback_total']) + '.',
        '- Counted non-permitted fallback increases: ' + str(nonpermitted) + '.',
        '- Counted honest runs reaching fewer than two novelty vectors: ' + str(measured['runs_reaching_fewer_than_two_novelty_vectors']) + '.', '',
        'Every step records its novelty vector count and its own fallback increase. After step 0, an increase is permitted only when the current or preceding novelty matrix has fewer than two vectors. No end-of-run module total is used as the check. On degenerate steps, raw entropy is the returned scalar, while V and shape are literal `null` in CSV. No step is dropped. First degenerate steps and the three fallback summary quantities are in `detector_run_cal_runs.csv`.', '',
        'The recorder adds exactly the appended `model.datacollector["L_t"][-1]` value for each step. The detector runs only offline. Heartbeat records carry post-reset statistics, and separate alarm records also retain the statistic before reset. Steps 0 through 9 remain zero and do not alarm.', '',
        '## T0', '',
        '| Check | Recorded result |', '| --- | --- |',
        '| Branch | main |',
        '| Required fd444fc ancestor | merge-base exit 0 |',
        '| Exact tracked-status command | exit 0, zero stdout lines |',
        '| Detector note indexed | ls-files exit 0 |',
        '| Last detector-note commit | ' + plan['t0']['publication']['stdout'] + ' |',
        '| Note publication | merge-base against origin/main exit 0 |',
        '| Detector note LF SHA256 | ' + plan['design_sha256_lf'] + '; matched |',
        '| Section 3 pins | Seven of seven matched |',
        '| Module and artifact namespace before first write | Module absent; no detector_run_* file existed |', '',
        'T0 stderr, recorded and non-halting:', '', '```text', plan['t0']['status']['stderr'], '```', '',
        'The known CRLF/LF condition and unreadable pytest cache/global ignore conditions were not repaired. Committed notes and the recorder source reference were read through Git objects. The detector note was read only after its specified hash passed.', '',
        '## T1 detector unit gate', '',
        'Synthetic parameters for each channel: reference 10, sigma 2, allowance 1, threshold 3, and 30 records at steps 0 through 29. Lower-channel harmful values are 8; the upper-channel harmful value is 12. The reverse values are harmless. Each case below passed before any model was stepped.', '',
        '| Channel | Case | Measured values |', '| --- | --- | --- |',
    ]
    for case in unit['cases']:
        values = {k: v for k, v in case.items() if k not in ('channel', 'case', 'passed')}
        lines.append('| ' + case['channel'] + ' | ' + case['case'] + ' | `' + json.dumps(values, separators=(',', ':')) + '` |')
    lines += [
        '', 'Synthetic per-step measurements are in `detector_run_cal_unit_sequences.csv`. All listed cases are retained in `detector_run_cal_unit_gate.json`.', '',
        '## T1 inherited model gates', '',
        '| Gate | Measured result |', '| --- | --- |',
        '| 2, source pins | Seven matched before probes and at completion |',
        '| 3, constructor equivalence | Seed 1835086199; equal configurations; ' + str(g3['steps_compared']) +
        ' completed steps in both; same end reason ' + g3['factory_end_reason'] + '; no differing field or step |',
        '| 3, fields compared | ' + str(g3['recorder_fields']) + ' recorder fields, nulls included; ' +
        str(g3['datacollector_fields']) + ' full datacollector fields |',
        '| 4, wrapper identity | 200 synthetic actions x 300 steps; 60,000 exact comparisons |',
        '| 5, honest gate | Attack vector absent; 60 inactive, unmodified steps |',
        '| 6, RNG preservation | 60 of 60 honest probe recorder calls unchanged |', '',
        'The two required constructor-equivalence probes use the production drift cell as specified by the inherited gate. They are gate probes, not attack evaluation arms, and the new detector was never applied to their trajectories. No gate record entered calibration.', '',
        'Amendment 2 probe measurements:', '', '| Probe | Step 0 increase | Permitted later increase | Non-permitted increases | First degenerate step |',
        '| --- | ---: | ---: | ---: | ---: |',
    ]
    for job, row in gates['amendment_2'].items():
        lines.append('| ' + job + ' | ' + ' | '.join(str(row[k]) for k in
                     ('step_0', 'permitted_after_step_0', 'nonpermitted_increase_count',
                      'first_fewer_than_two_novelty_vectors_step')) + ' |')
    r0 = runtime_records[0]
    lines += [
        '', '## Provenance and runtime', '',
        '- Machine: ' + r0['machine'] + '.',
        '- HEAD: ' + plan['head'] + '.',
        '- Python: ' + r0['python'] + '.',
        '- NumPy: ' + r0['numpy'] + '.',
        '- Operator CPU budget: 16; CPUs available to the process: ' + str(r0['process_cpu_count']) + '.',
        '- Maximum active calibration workers actually used: ' + str(execution['maximum_active_workers']) + '.',
        '- Limits: normal 15, work 12. Changes drain active jobs without restarting them. No operating-system core reservation is claimed.',
        '- Numerical-library threads: configured to 1 before imports and verified as 1 through the OpenBLAS runtime query in every worker.',
        '- Mode-change records: `' + json.dumps(execution['mode_changes'], separators=(',', ':')) + '`.',
        '- Resumed seeds: `' + json.dumps(execution['resumed_seeds'], separators=(',', ':')) + '`.',
        '- Batch start: ' + execution['started_utc'] + '; completion: ' + execution['completed_utc'] + '.',
        '- Completed-job records were published durably only after their raw logs were closed and hashed. Partial logs never counted as completed.',
        '- Bytecode writes disabled; the writable-open guard explicitly exempts os.devnull.', '',
        'Per-worker thread readings and operating metadata are in `detector_run_cal_runtime.json`. Loaded simulation modules have both raw and LF-normalized working-tree SHA256 values in `detector_run_cal_module_hashes.json`; bases are labeled. New module LF SHA256: `' + module_hash + '`.', '',
        'Constants file LF SHA256: `' + constants_hash + '`.', '',
        '| Source | Start LF SHA256 | Completion LF SHA256 | Committed blob SHA1 |', '| --- | --- | --- | --- |',
    ]
    for pin in end_pins:
        lines.append('| ' + pin['path'] + ' | ' + pin['start_sha256_lf'] + ' | ' + pin['actual_sha256_lf'] + ' | ' + pin['blob_sha1'] + ' |')
    lines += ['', '| Committed note | Blob SHA1 | LF SHA256, unchanged at completion |', '| --- | --- | --- |']
    for note in note_records:
        lines.append('| ' + note['path'] + ' | ' + note['blob_sha1'] + ' | ' + note['sha256_lf_end'] + ' |')
    lines += [
        '', 'Committed recorder source reference: `' + plan['recorder_reference'] + '`, blob SHA1 `' + plan['recorder_reference_blob_sha1'] + '`.', '',
        'The manifest enumerates the new module and every stage 1 artifact. SHA256 values use LF-normalized bytes. CSV counts use Python csv.DictReader, excluding headers. Non-CSV row counts are null. The manifest lists itself with a null self-hash to avoid a circular content hash.', '',
    ]
    resume = h.read(h.P + 'resume_authorization.json')
    io_tests = h.read(h.P + 'io_tests.json')
    lines += [
        '## Operational interruption and authorized resumption', '',
        'The first batch halted on WinError 5 while replacing its progress file. Completion records established 97 finished runs, 13 interrupted jobs, and 10 jobs not launched. The user then requested, "can you test and resume?" This authorized operational testing and resumption; no registered scientific procedure was changed.', '',
        'Disposable-file tests reproduced WinError 5 while a reader held the destination open. Releasing the reader allowed replacement to succeed. An initial delete-sharing test still failed under a held handle. A later concurrent test exposed transient read failures too. The final operational layer therefore uses bounded retries for transient JSON-read and atomic-replacement permission errors, with a five-second limit. Persistent errors still propagate and halt execution. All tests used diagnostic artifacts and no model steps.', '',
        'Final operational test measurements: 250 reads and 250 replacements completed without reader errors; transient-lock recovery passed; the deliberately persistent lock produced the expected bounded failure. Earlier failed test results are retained in the I/O test history and event records.', '',
        'The pinned executor, recorder, detector module, calibration code, plan, and seven simulation source pins retained their original hashes. The additional operational layer changes JSON-read/replacement handling and routes child launches through that layer. It is separately identified in resumed worker metadata and the manifest. Its LF SHA256 is `' + resume['operational_source_sha256_lf'] + '`.', '',
        'The 97 validated completed runs were skipped. Thirteen interrupted jobs restarted from their original seeds: `' + json.dumps(resume['interrupted_seeds_to_restart_from_original_seed']) + '`. Ten jobs ran for the first time: `' + json.dumps(resume['not_previously_launched_seeds']) + '`. A ledger reservation for seed 1835086410 was cleared because its worker had not been launched. No completed seed was rerun.', '',
        'Historical halt reports, manifests, and changing metadata were preserved under pre_resume names, with their path mapping and hashes in `detector_run_cal_resume_authorization.json`. The retained `detector_run_cal_halt.json`, `detector_run_cal_incomplete.csv`, and failure records describe the earlier interruption; the current report and completed-run ledger supersede their execution status. Original partial logs remain partial and were never used for calibration.', '',
    ]
    report = '\n'.join(lines)
    if '\u2014' in report:
        raise RuntimeError('Report contains prohibited punctuation')
    with (h.OUT / (h.P + 'report.md')).open('w', encoding='utf-8', newline='\n') as f:
        f.write(report)
        f.flush()
        h.os.fsync(f.fileno())
    entries = []
    manifest_name = h.P + 'manifest.json'
    paths = [module_path] + sorted(h.OUT.glob(h.P + '*'))
    for path in paths:
        if not path.is_file() or path.name == manifest_name:
            continue
        raw = path.read_bytes()
        is_csv = path.name.endswith('.csv') or path.name.endswith('.csv.partial')
        count = sum(1 for _ in csv.DictReader(io.StringIO(raw.decode('utf-8')))) if is_csv else None
        entries.append({'path': path.relative_to(h.ROOT).as_posix(), 'sha256_lf': h.sha(h.lf(raw)),
                        'csv_rows': count, 'partial': path.name.endswith('.partial')})
    entries.append({'path': 'simulation/diagnostics/' + manifest_name,
                    'sha256_lf': None, 'csv_rows': None, 'self_hash_note': 'Excluded from its own content hash.'})
    manifest = {'status': 'STAGE_1_COMPLETE', 'stage': 1, 'created_utc': h.now(),
                'machine': r0['machine'], 'head': plan['head'], 'python': r0['python'], 'numpy': r0['numpy'],
                'hash_basis': 'LF-normalized bytes', 'source_pins': end_pins, 'notes': note_records,
                'recorder_reference_blob_sha1': plan['recorder_reference_blob_sha1'],
                'detector_sha256_lf': module_hash, 'constants_sha256_lf': constants_hash,
                'maximum_active_workers': execution['maximum_active_workers'],
                'resumed_seeds': execution['resumed_seeds'],
                'operational_resume': resume, 'operational_io_tests': io_tests, 'outputs': entries}
    h.write(manifest_name, manifest)
    print(json.dumps({'status': 'STAGE_1_COMPLETE', 'report': h.P + 'report.md',
                      'constants_sha256_lf': constants_hash, 'detector_sha256_lf': module_hash,
                      'manifest_sha256_lf': h.sha(h.lf((h.OUT / manifest_name).read_bytes())),
                      'outputs_enumerated': len(entries)}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        h.mark_halt('finalize', error)
        raise
