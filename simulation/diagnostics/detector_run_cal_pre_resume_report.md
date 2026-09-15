# Detector calibration, stage 1: halt report

**Status: HALTED. 97 of 120 honest runs completed; 13 jobs are incomplete and 10 were not launched. Calibration was not performed.**

The detector module was created and all T0 and T1 gates passed. During the honest batch, the coordinator raised a Windows PermissionError while replacing its progress file. The closed halt rule was applied. No seed was rerun. All workers and the coordinator have exited.

No attack arm was run. The detector was not evaluated against an attack or on stage 2 data. No calibrated constant has been consumed: no calibration constants file exists. No corrected figure was derived. Stage 2 remains a separate dispatch and may begin only after completed stage 1 outputs are committed and pushed and its publication gate passes.

## Recorded halt

UTC: 2026-09-15T18:12:19.092510+00:00.

```text
[WinError 5] Access is denied: 'C:\\Users\\matty\\Dev\\AI-Succession-Problem\\simulation\\diagnostics\\detector_run_cal_execution.json.37400.tmp' -> 'C:\\Users\\matty\\Dev\\AI-Succession-Problem\\simulation\\diagnostics\\detector_run_cal_execution.json'
```

The traceback identifies `detector_run_cal_executor.py:456`, which persists the active-job ledger before dispatch, and the `os.replace` call at line 160. The failure occurred on an authorized artifact path. Its underlying Windows cause was not diagnosed or worked around. No replacement retry or batch restart was launched.

The coordinator subsequently wrote its HALTED status during shutdown. Its retained progress fields show 94 completed and an active-job list from dispatch time; these are stale progress fields, not live worker counts. Completion records are the primary record: 97 validate by seed, configuration, code identity, row count, and raw-log SHA256. Three additional completion records existed by shutdown. The coordinator waited for its worker processes before exiting.

## Preserved runs

- Counted completed runs: 97.
- Counted completed-run steps: 29100.
- Counted partial jobs, including one zero-row partial log: 13.
- Counted jobs not launched: 10.
- Resumed or rerun seeds: none.

`detector_run_cal_runs.csv` enumerates the 97 completed runs. `detector_run_cal_incomplete.csv` enumerates all 23 incomplete or unlaunched jobs. Partial logs are not completion records and do not enter calibration.

| Seed | Status | Recorded partial rows |
| ---: | --- | ---: |
| 1835086396 | PARTIAL_NOT_COMPLETE | 299 |
| 1835086398 | PARTIAL_NOT_COMPLETE | 296 |
| 1835086399 | PARTIAL_NOT_COMPLETE | 299 |
| 1835086400 | PARTIAL_NOT_COMPLETE | 294 |
| 1835086401 | PARTIAL_NOT_COMPLETE | 291 |
| 1835086402 | PARTIAL_NOT_COMPLETE | 297 |
| 1835086403 | PARTIAL_NOT_COMPLETE | 294 |
| 1835086404 | PARTIAL_NOT_COMPLETE | 284 |
| 1835086405 | PARTIAL_NOT_COMPLETE | 18 |
| 1835086406 | PARTIAL_NOT_COMPLETE | 12 |
| 1835086407 | PARTIAL_NOT_COMPLETE | 5 |
| 1835086408 | PARTIAL_NOT_COMPLETE | 5 |
| 1835086409 | PARTIAL_NOT_COMPLETE | 0 |
| 1835086410 | NOT_LAUNCHED | 0 |
| 1835086411 | NOT_LAUNCHED | 0 |
| 1835086412 | NOT_LAUNCHED | 0 |
| 1835086413 | NOT_LAUNCHED | 0 |
| 1835086414 | NOT_LAUNCHED | 0 |
| 1835086415 | NOT_LAUNCHED | 0 |
| 1835086416 | NOT_LAUNCHED | 0 |
| 1835086417 | NOT_LAUNCHED | 0 |
| 1835086418 | NOT_LAUNCHED | 0 |
| 1835086419 | NOT_LAUNCHED | 0 |

The 120 intended seeds were 1835086300 through 1835086419. No subset calibration, percentile, per-run maximum, or descriptive alarm replay was computed. `detector_run_cal_constants.json` was not created, and its SHA256 is unavailable for that reason. The nine constants remain unmeasured in this attempt.

## T0

| Check | Recorded result |
| --- | --- |
| Branch | main |
| Required fd444fc ancestor | merge-base exit 0 |
| Exact tracked-status command | exit 0; zero stdout lines |
| Detector note indexed | ls-files exit 0 |
| Last note commit | 76f81cd83e0db6ff5031070e54f2f908502b8632 |
| Note publication | merge-base against origin/main exit 0 |
| Committed detector-note LF SHA256 | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad; matched |
| Section 3 pins | Seven of seven matched |
| New module and namespace before writes | Module absent; no detector_run_* artifact existed |

T0 stderr, recorded and non-halting:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

Known conditions were retained: CRLF worktree against LF blobs and unreadable pytest-cache/global-ignore warnings. They were not repaired. The notes and recorder reference were retrieved from committed Git objects. The detector note was read only after its pinned hash passed.

## T1 detector unit gate

All listed synthetic cases passed before any model probe. Parameters were reference 10, sigma 2, allowance 1, and threshold 3 over 30 steps. The lower-channel harmful value was 8 and upper-channel harmful value 12; harmless values reversed the shift. The measured cases follow.

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

The full unit record is `detector_run_cal_unit_gate.json`, with per-step sequences in `detector_run_cal_unit_sequences.csv`. The L channel did not contribute to the operational alarm.

## T1 inherited model gates

| Gate | Measured result |
| --- | --- |
| 2, source pins | All seven matched |
| 3, constructor equivalence | Equal configurations; both completed 280 steps and ended by extinction |
| 3, recorded comparisons | 7560 recorder values across 27 fields; 21560 datacollector values across 77 fields; no difference |
| 4, wrapper | 200 synthetic actions x 300 steps; 60,000 exact comparisons |
| 5, honest arm | No attack key; adapter inactive and action unmodified on all 60 probe steps |
| 6, recorder | NumPy state unchanged across all 60 honest probe calls |

The required constructor-equivalence probes used the production drift cell at seed 1835086199. They were gate probes, not attack evaluation arms. The new detector was not applied to them, and none of their records entered calibration.

| Probe | Step 0 fallback increase | Permitted later increase | Non-permitted increases | First fewer-than-two-vector step |
| --- | ---: | ---: | ---: | ---: |
| common | 2 | 46 | 0 | 264 |
| factory | 2 | 46 | 0 | 264 |
| honest | 2 | 0 | 0 | None |

## Honest configuration and continuous-check records

All calibration models used the inherited honest constructor with n_agents=200, ai_policy=sub_threshold_drift, use_cop=True, cop_attribution_check=True, cop_drift_check=True, and cop_cusum_drift=False. The concrete configuration of the first completed run is below; only random_seed changes between runs.

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

The attack_vector_v2 key is absent. The recorder includes the model-appended L_t value on every recorded step. It records novelty vector count and per-step fallback increase. On a step with fewer than two novelty vectors, raw entropy is the returned scalar and V and shape are literal null; neither is substituted. Only per-step counter differences are checked.

Counted among completed runs:

- Step 0 fallback increase distribution: {"2": 97}.
- Total permitted later fallback increase: 0.
- Non-permitted fallback increase count: 0.
- Exact raw-entropy comparisons: 29100.
- Recorder calls preserving NumPy state: 29100.
- Honest adapter-active steps: 0.
- Honest action-modified steps: 0.

Incomplete jobs retain their per-step counter records but have no completion summary. Their worker failures report stopping after the coordinator halt. No statistics from a partial trajectory were substituted for completed-run measurements.

## Provenance and runtime

- Machine: YOTKOTEST.
- HEAD: 76f81cd83e0db6ff5031070e54f2f908502b8632.
- Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)].
- NumPy: 2.4.4.
- Operator CPU budget: 16; process CPU availability: 16.
- Maximum active calibration workers actually used: 15.
- Mode: normal, limit 15. Work-mode limit is 12; no mode change was requested during this batch.
- Numerical-library threads were configured before import and verified as one through the OpenBLAS runtime query in each launched worker.
- No operating-system core reservation is claimed.
- Batch start: 2026-09-15T18:01:06.568284+00:00; halt: 2026-09-15T18:12:19.092510+00:00.
- Bytecode writes were disabled. The guard explicitly exempts os.devnull.
- Runtime controller: detector_run_cal_control.json. Scheduler tests covered caps, draining, normal-mode expansion, deterministic seed assignment, and synthetic completion skipping without model steps.

New detector module LF-normalized SHA256: `6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9`.

Per-module raw and LF-normalized hashes are labeled in `detector_run_cal_module_hashes.json`. Per-worker thread readings and runtime metadata are in `detector_run_cal_runtime.json`. Source pins were read again at close-out and all matched:

| Source | Start LF SHA256 | Close-out LF SHA256 | Committed blob SHA1 |
| --- | --- | --- | --- |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 7e7749d99636746aa2c3215da1edaa6ab5372611 |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | d21e5300eab6e4136141ea33aa0367b9aa47ed51 |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | a1cf988532203b7119462eb9b04cf2e3b0541879 |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | ecd9e6451065a6120e5dcb8a21b8206fb34f5e3e |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | ad80bd5fe60cc357a43e30c32ab3c12a758c0c2d |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | bbfa1ea81ce8648adaf6c44a8b6f65188d206486 |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 43b9766e63d1519faf59d1e8e4562c686a8149f2 |

| Committed note | Blob SHA1 | Start and close-out LF SHA256 |
| --- | --- | --- |
| simulation/diagnostics/detector_design_note.md | 4e95b1c80214de480fc9e9e2520bd4dc1a5ab400 | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad |
| simulation/diagnostics/drift_mapping_design_note.md | 0ddb02e4960948bc8f925ca77480f607370f0b2c | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 |

Committed recorder reference: `simulation/diagnostics/drift_map_run_a3_executor.py`, blob SHA1 `29b666af9655d2099dcd4fda8755c3f8a3edb1b5`.

## Artifacts

The manifest enumerates the new module and every detector_run_cal_ artifact, including partial logs. SHA256 values use LF-normalized bytes. CSV and CSV-formatted partial-log rows are counted with Python csv.DictReader excluding headers. Non-CSV row counts are null. The manifest lists itself with a null self-hash to avoid a circular hash. The prepared success finalizer and calibration routine were not executed after the halt.
