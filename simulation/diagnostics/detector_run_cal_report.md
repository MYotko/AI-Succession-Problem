# Detector calibration, stage 1

Stage 1 is complete: 120 honest calibration runs. No attack arm was run. The detector was not evaluated against an attack or on stage 2 data. No corrected figure was derived.

No calibrated constant has been consumed by a model or by stage 2. The only application of the calibrated thresholds was the descriptive replay on calibration records required by Section 6. Stage 2 is a separate dispatch and may begin only after these outputs and the detector module are committed and pushed and its publication gate passes.

## Calibration measurements

The following nine constants were computed by the committed Section 6 rule. All available records at steps 10 and up entered each channel. References are medians, allowances are half the sample standard deviation with ddof 1, and thresholds are NumPy linear percentiles of the 120 unthresholded per-run maxima. No threshold and no reset were used to obtain those maxima. No value was adjusted from a result.

| Channel | Reference | Allowance | Threshold | Records | Percentile |
| --- | ---: | ---: | ---: | ---: | ---: |
| entropy | 0.98909517853363649 | 0.0035491735533230962 | 0.17319485850717864 | 34800 | 97.5 |
| g | 0.97864460546155874 | 0.022160874873702576 | 4.5077298945439432 | 34800 | 97.5 |
| L | 0.73606744215607522 | 0.056644201005884506 | 15.04497999532887 | 34800 | 95.0 |

| Channel | Sample standard deviation, ddof 1 | Calibration runs with at least one alarm after applying thresholds and resets |
| --- | ---: | ---: |
| entropy | 0.0070983471066461924 | 3 of 120 |
| g | 0.044321749747405152 | 3 of 120 |
| L | 0.11328840201176901 | 6 of 120 |

The full-precision constants, per-channel record counts, and all 120 maxima per channel are in `detector_run_cal_constants.json`. The same maxima are in `detector_run_cal_maxima.csv`. Alarm counts above are descriptive calibration counts only.

## Execution and continuous checks

Constructed configuration: `GardenModel(n_agents=200, ai_policy="sub_threshold_drift", use_cop=True, cop_attribution_check=True, cop_drift_check=True, cop_cusum_drift=False)` with the configuration below. Every completion record carries its concrete seed and configuration.

```json
{
  "attack_step": 50,
  "bootstrap_turn_step_v2": 20,
  "cop_cusum_drift": false,
  "cop_methodological_diversity": false,
  "n_candidates_v2": 300,
  "phi": 10.0,
  "policy": "optimize_u_sys_v2",
  "random_seed": 1835086300,
  "rollout_steps_v2": 20,
  "shock_magnitude": 0.15,
  "shock_step": 0
}
```

The `attack_vector_v2` key is absent. Seeds are the 120 consecutive integers 1835086300 through 1835086419, assigned independently of scheduling. Runs stop at 300 steps or when the model returns false. End reasons, not imputed continuations, are recorded per run.

- Counted completed runs: 120.
- Counted completed steps: 36000.
- Counted end reasons: {"step_limit": 120}.
- Counted heartbeat records in descriptive calibration replay: 36000, exactly one per completed step in each run.
- Counted steps with an active honest adapter: 0; action-modified honest steps: 0.
- Counted exact raw-entropy matches: 36000.
- Counted recorder calls preserving NumPy state: 36000.
- Counted step 0 fallback increase distribution: {"2": 120}.
- Counted total permitted fallback increase after step 0: 0.
- Counted non-permitted fallback increases: 0.
- Counted honest runs reaching fewer than two novelty vectors: 0.

Every step records its novelty vector count and its own fallback increase. After step 0, an increase is permitted only when the current or preceding novelty matrix has fewer than two vectors. No end-of-run module total is used as the check. On degenerate steps, raw entropy is the returned scalar, while V and shape are literal `null` in CSV. No step is dropped. First degenerate steps and the three fallback summary quantities are in `detector_run_cal_runs.csv`.

The recorder adds exactly the appended `model.datacollector["L_t"][-1]` value for each step. The detector runs only offline. Heartbeat records carry post-reset statistics, and separate alarm records also retain the statistic before reset. Steps 0 through 9 remain zero and do not alarm.

## T0

| Check | Recorded result |
| --- | --- |
| Branch | main |
| Required fd444fc ancestor | merge-base exit 0 |
| Exact tracked-status command | exit 0, zero stdout lines |
| Detector note indexed | ls-files exit 0 |
| Last detector-note commit | 76f81cd83e0db6ff5031070e54f2f908502b8632 |
| Note publication | merge-base against origin/main exit 0 |
| Detector note LF SHA256 | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad; matched |
| Section 3 pins | Seven of seven matched |
| Module and artifact namespace before first write | Module absent; no detector_run_* file existed |

T0 stderr, recorded and non-halting:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

The known CRLF/LF condition and unreadable pytest cache/global ignore conditions were not repaired. Committed notes and the recorder source reference were read through Git objects. The detector note was read only after its specified hash passed.

## T1 detector unit gate

Synthetic parameters for each channel: reference 10, sigma 2, allowance 1, threshold 3, and 30 records at steps 0 through 29. Lower-channel harmful values are 8; the upper-channel harmful value is 12. The reverse values are harmless. Each case below passed before any model was stepped.

| Channel | Case | Measured values |
| --- | --- | --- |
| entropy | at_reference | `{"measured_alarm_count":0,"measured_maximum":0.0}` |
| entropy | one_sigma_harmful_shift | `{"allowance":1.0,"expected_alarm_steps":[12,15,18,21,24,27],"expected_increment":1.0,"measured_alarm_steps":[12,15,18,21,24,27],"measured_increments":[1.0],"sigma":2.0}` |
| entropy | harmless_shift | `{"measured_alarm_count":0,"measured_maximum":0.0}` |
| entropy | reset_after_alarm | `{"measured_next_start_statistics":[0.0,0.0,0.0,0.0,0.0,0.0],"measured_post_alarm_statistics":[0.0,0.0,0.0,0.0,0.0,0.0]}` |
| entropy | burn_in | `{"measured_alarm_count":0,"measured_statistics":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],"steps":[0,1,2,3,4,5,6,7,8,9]}` |
| entropy | heartbeat | `{"expected_count_each":30,"measured_counts":{"harmful":30,"harmless":30,"reference":30}}` |
| g | at_reference | `{"measured_alarm_count":0,"measured_maximum":0.0}` |
| g | one_sigma_harmful_shift | `{"allowance":1.0,"expected_alarm_steps":[12,15,18,21,24,27],"expected_increment":1.0,"measured_alarm_steps":[12,15,18,21,24,27],"measured_increments":[1.0],"sigma":2.0}` |
| g | harmless_shift | `{"measured_alarm_count":0,"measured_maximum":0.0}` |
| g | reset_after_alarm | `{"measured_next_start_statistics":[0.0,0.0,0.0,0.0,0.0,0.0],"measured_post_alarm_statistics":[0.0,0.0,0.0,0.0,0.0,0.0]}` |
| g | burn_in | `{"measured_alarm_count":0,"measured_statistics":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],"steps":[0,1,2,3,4,5,6,7,8,9]}` |
| g | heartbeat | `{"expected_count_each":30,"measured_counts":{"harmful":30,"harmless":30,"reference":30}}` |
| L | at_reference | `{"measured_alarm_count":0,"measured_maximum":0.0}` |
| L | one_sigma_harmful_shift | `{"allowance":1.0,"expected_alarm_steps":[12,15,18,21,24,27],"expected_increment":1.0,"measured_alarm_steps":[12,15,18,21,24,27],"measured_increments":[1.0],"sigma":2.0}` |
| L | harmless_shift | `{"measured_alarm_count":0,"measured_maximum":0.0}` |
| L | reset_after_alarm | `{"measured_next_start_statistics":[0.0,0.0,0.0,0.0,0.0,0.0],"measured_post_alarm_statistics":[0.0,0.0,0.0,0.0,0.0,0.0]}` |
| L | burn_in | `{"measured_alarm_count":0,"measured_statistics":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],"steps":[0,1,2,3,4,5,6,7,8,9]}` |
| L | heartbeat | `{"expected_count_each":30,"measured_counts":{"harmful":30,"harmless":30,"reference":30}}` |
| L | comparison_channel_separation | `{"measured_L_alarm_steps":[12,15,18,21,24,27],"measured_operational_alarm_steps":[]}` |

Synthetic per-step measurements are in `detector_run_cal_unit_sequences.csv`. All listed cases are retained in `detector_run_cal_unit_gate.json`.

## T1 inherited model gates

| Gate | Measured result |
| --- | --- |
| 2, source pins | Seven matched before probes and at completion |
| 3, constructor equivalence | Seed 1835086199; equal configurations; 280 completed steps in both; same end reason extinction; no differing field or step |
| 3, fields compared | 27 recorder fields, nulls included; 77 full datacollector fields |
| 4, wrapper identity | 200 synthetic actions x 300 steps; 60,000 exact comparisons |
| 5, honest gate | Attack vector absent; 60 inactive, unmodified steps |
| 6, RNG preservation | 60 of 60 honest probe recorder calls unchanged |

The two required constructor-equivalence probes use the production drift cell as specified by the inherited gate. They are gate probes, not attack evaluation arms, and the new detector was never applied to their trajectories. No gate record entered calibration.

Amendment 2 probe measurements:

| Probe | Step 0 increase | Permitted later increase | Non-permitted increases | First degenerate step |
| --- | ---: | ---: | ---: | ---: |
| common | 2 | 46 | 0 | 264 |
| factory | 2 | 46 | 0 | 264 |
| honest | 2 | 0 | 0 | None |

## Provenance and runtime

- Machine: YOTKOTEST.
- HEAD: 76f81cd83e0db6ff5031070e54f2f908502b8632.
- Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)].
- NumPy: 2.4.4.
- Operator CPU budget: 16; CPUs available to the process: 16.
- Maximum active calibration workers actually used: 15.
- Limits: normal 15, work 12. Changes drain active jobs without restarting them. No operating-system core reservation is claimed.
- Numerical-library threads: configured to 1 before imports and verified as 1 through the OpenBLAS runtime query in every worker.
- Mode-change records: `[{"active_workers":0,"limit":15,"mode":"normal","utc":"2026-09-15T18:01:06.570833+00:00"},{"active_workers":0,"limit":15,"mode":"normal","utc":"2026-09-15T18:24:00.131040+00:00"}]`.
- Resumed seeds: `[{"arm":"H","job":"H_1835086396","reason":"In-flight job interrupted without a completion record","seed":1835086396,"utc":"2026-09-15T18:24:00.130766+00:00"},{"arm":"H","job":"H_1835086398","reason":"In-flight job interrupted without a completion record","seed":1835086398,"utc":"2026-09-15T18:24:00.130781+00:00"},{"arm":"H","job":"H_1835086399","reason":"In-flight job interrupted without a completion record","seed":1835086399,"utc":"2026-09-15T18:24:00.130784+00:00"},{"arm":"H","job":"H_1835086400","reason":"In-flight job interrupted without a completion record","seed":1835086400,"utc":"2026-09-15T18:24:00.130786+00:00"},{"arm":"H","job":"H_1835086401","reason":"In-flight job interrupted without a completion record","seed":1835086401,"utc":"2026-09-15T18:24:00.130788+00:00"},{"arm":"H","job":"H_1835086402","reason":"In-flight job interrupted without a completion record","seed":1835086402,"utc":"2026-09-15T18:24:00.130790+00:00"},{"arm":"H","job":"H_1835086403","reason":"In-flight job interrupted without a completion record","seed":1835086403,"utc":"2026-09-15T18:24:00.130791+00:00"},{"arm":"H","job":"H_1835086404","reason":"In-flight job interrupted without a completion record","seed":1835086404,"utc":"2026-09-15T18:24:00.130793+00:00"},{"arm":"H","job":"H_1835086405","reason":"In-flight job interrupted without a completion record","seed":1835086405,"utc":"2026-09-15T18:24:00.130794+00:00"},{"arm":"H","job":"H_1835086406","reason":"In-flight job interrupted without a completion record","seed":1835086406,"utc":"2026-09-15T18:24:00.130795+00:00"},{"arm":"H","job":"H_1835086407","reason":"In-flight job interrupted without a completion record","seed":1835086407,"utc":"2026-09-15T18:24:00.130797+00:00"},{"arm":"H","job":"H_1835086408","reason":"In-flight job interrupted without a completion record","seed":1835086408,"utc":"2026-09-15T18:24:00.130798+00:00"},{"arm":"H","job":"H_1835086409","reason":"In-flight job interrupted without a completion record","seed":1835086409,"utc":"2026-09-15T18:24:00.130799+00:00"}]`.
- Batch start: 2026-09-15T18:01:06.568284+00:00; completion: 2026-09-15T18:26:47.250673+00:00.
- Completed-job records were published durably only after their raw logs were closed and hashed. Partial logs never counted as completed.
- Bytecode writes disabled; the writable-open guard explicitly exempts os.devnull.

Per-worker thread readings and operating metadata are in `detector_run_cal_runtime.json`. Loaded simulation modules have both raw and LF-normalized working-tree SHA256 values in `detector_run_cal_module_hashes.json`; bases are labeled. New module LF SHA256: `6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9`.

Constants file LF SHA256: `61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488`.

| Source | Start LF SHA256 | Completion LF SHA256 | Committed blob SHA1 |
| --- | --- | --- | --- |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 7e7749d99636746aa2c3215da1edaa6ab5372611 |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | d21e5300eab6e4136141ea33aa0367b9aa47ed51 |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | a1cf988532203b7119462eb9b04cf2e3b0541879 |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | ecd9e6451065a6120e5dcb8a21b8206fb34f5e3e |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | ad80bd5fe60cc357a43e30c32ab3c12a758c0c2d |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | bbfa1ea81ce8648adaf6c44a8b6f65188d206486 |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 43b9766e63d1519faf59d1e8e4562c686a8149f2 |

| Committed note | Blob SHA1 | LF SHA256, unchanged at completion |
| --- | --- | --- |
| simulation/diagnostics/detector_design_note.md | 4e95b1c80214de480fc9e9e2520bd4dc1a5ab400 | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad |
| simulation/diagnostics/drift_mapping_design_note.md | 0ddb02e4960948bc8f925ca77480f607370f0b2c | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 |

Committed recorder source reference: `simulation/diagnostics/drift_map_run_a3_executor.py`, blob SHA1 `29b666af9655d2099dcd4fda8755c3f8a3edb1b5`.

The manifest enumerates the new module and every stage 1 artifact. SHA256 values use LF-normalized bytes. CSV counts use Python csv.DictReader, excluding headers. Non-CSV row counts are null. The manifest lists itself with a null self-hash to avoid a circular content hash.

## Operational interruption and authorized resumption

The first batch halted on WinError 5 while replacing its progress file. Completion records established 97 finished runs, 13 interrupted jobs, and 10 jobs not launched. The user then requested, "can you test and resume?" This authorized operational testing and resumption; no registered scientific procedure was changed.

Disposable-file tests reproduced WinError 5 while a reader held the destination open. Releasing the reader allowed replacement to succeed. An initial delete-sharing test still failed under a held handle. A later concurrent test exposed transient read failures too. The final operational layer therefore uses bounded retries for transient JSON-read and atomic-replacement permission errors, with a five-second limit. Persistent errors still propagate and halt execution. All tests used diagnostic artifacts and no model steps.

Final operational test measurements: 250 reads and 250 replacements completed without reader errors; transient-lock recovery passed; the deliberately persistent lock produced the expected bounded failure. Earlier failed test results are retained in the I/O test history and event records.

The pinned executor, recorder, detector module, calibration code, plan, and seven simulation source pins retained their original hashes. The additional operational layer changes JSON-read/replacement handling and routes child launches through that layer. It is separately identified in resumed worker metadata and the manifest. Its LF SHA256 is `b23600acd60ea3cb7930e23a7f8ab8be191fb8b31759cf6445e1f68285d01e53`.

The 97 validated completed runs were skipped. Thirteen interrupted jobs restarted from their original seeds: `[1835086396, 1835086398, 1835086399, 1835086400, 1835086401, 1835086402, 1835086403, 1835086404, 1835086405, 1835086406, 1835086407, 1835086408, 1835086409]`. Ten jobs ran for the first time: `[1835086410, 1835086411, 1835086412, 1835086413, 1835086414, 1835086415, 1835086416, 1835086417, 1835086418, 1835086419]`. A ledger reservation for seed 1835086410 was cleared because its worker had not been launched. No completed seed was rerun.

Historical halt reports, manifests, and changing metadata were preserved under pre_resume names, with their path mapping and hashes in `detector_run_cal_resume_authorization.json`. The retained `detector_run_cal_halt.json`, `detector_run_cal_incomplete.csv`, and failure records describe the earlier interruption; the current report and completed-run ledger supersede their execution status. Original partial logs remain partial and were never used for calibration.
