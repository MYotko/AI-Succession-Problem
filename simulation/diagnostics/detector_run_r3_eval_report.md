# Detector round 3, stage B evaluation

This is a detection characterization, not a containment evaluation. No constant was derived or recomputed for use. No corrected figure was derived. Comparison with rounds 1 and 2 is descriptive. The round 3 note Section 7 interpretation is reserved for the operator.

Status: HALTED. A-definition gate failed: {"step": 2, "recorded_A": 0.36201162103876716, "recomputed_A": 0.3620116210387671, "passed": false}

Completed evaluation runs: 0 of 360.

## Gates and continuous checks

All gate probes were run for this stage. The recorder and operational retry functions were copied from committed round 1 source; no module with a different write guard was imported. The stage B write guard permits only detector_run_r3_eval_ artifacts and os.devnull. The null-device exemption is present; bytecode writes are disabled.

| Channel | Case | Passed | Measured values |
| --- | --- | --- | --- |
| entropy | at_reference | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| entropy | one_sigma_harmful_shift | True | {"allowance": 1.0, "expected_alarm_steps": [12, 15, 18, 21, 24, 27], "expected_increment": 1.0, "measured_alarm_steps": [12, 15, 18, 21, 24, 27], "measured_increments": [1.0], "sigma": 2.0} |
| entropy | harmless_shift | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| entropy | reset_after_alarm | True | {"measured_next_start_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "measured_post_alarm_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]} |
| entropy | burn_in | True | {"measured_alarm_count": 0, "measured_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "steps": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]} |
| entropy | heartbeat | True | {"expected_count_each": 30, "measured_counts": {"harmful": 30, "harmless": 30, "reference": 30}} |
| g | at_reference | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| g | one_sigma_harmful_shift | True | {"allowance": 1.0, "expected_alarm_steps": [12, 15, 18, 21, 24, 27], "expected_increment": 1.0, "measured_alarm_steps": [12, 15, 18, 21, 24, 27], "measured_increments": [1.0], "sigma": 2.0} |
| g | harmless_shift | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| g | reset_after_alarm | True | {"measured_next_start_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "measured_post_alarm_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]} |
| g | burn_in | True | {"measured_alarm_count": 0, "measured_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "steps": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]} |
| g | heartbeat | True | {"expected_count_each": 30, "measured_counts": {"harmful": 30, "harmless": 30, "reference": 30}} |
| L | at_reference | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| L | one_sigma_harmful_shift | True | {"allowance": 1.0, "expected_alarm_steps": [12, 15, 18, 21, 24, 27], "expected_increment": 1.0, "measured_alarm_steps": [12, 15, 18, 21, 24, 27], "measured_increments": [1.0], "sigma": 2.0} |
| L | harmless_shift | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| L | reset_after_alarm | True | {"measured_next_start_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "measured_post_alarm_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]} |
| L | burn_in | True | {"measured_alarm_count": 0, "measured_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "steps": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]} |
| L | heartbeat | True | {"expected_count_each": 30, "measured_counts": {"harmful": 30, "harmless": 30, "reference": 30}} |
| L | comparison_channel_separation | True | {"measured_L_alarm_steps": [12, 15, 18, 21, 24, 27], "measured_operational_alarm_steps": []} |

Exploratory descriptive recording required by Amendment 2:

| Arm | Runs | Runs reaching fewer than two novelty vectors |
| --- | --- | --- |
| H | 0 | 0 |
| M05 | 0 | 0 |
| M1 | 0 | 0 |
| M2 | 0 | 0 |
| M4 | 0 | 0 |
| R02 | 0 | 0 |
| R05 | 0 | 0 |
| R10 | 0 | 0 |
| R20 | 0 | 0 |

The first such step is recorded per run in the runs CSV and completion records.

Step 0 fallback increase distribution: {}.
Permitted fallback increase after step 0: 0. Non-permitted increase count: 0.

## Execution and provenance

Machine: YOTKOTEST. HEAD: 7a588b6737a1d0d9bb6cbbfd1ae60ee3f4eac237. Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]. NumPy: 2.4.4.

Operator CPU budget: 16. Maximum active evaluation workers: 0. Limits are 15 in normal mode and 12 in work mode. These are worker limits, not operating-system core reservations. Numerical-library threads were set to one before import and verified per worker through the loaded OpenBLAS runtime.

Mode changes: []
Resumed seeds and reasons: []
Retry events: 0. JSON reads and atomic replacement use the five-second bound; all retry events are in the manifest and per-process JSONL files.

T0 passed every enumerated check before the fresh namespace was created. The known CRLF/LF condition was retained without normalization. T0 stderr warnings:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

### Source pins, start and completion

| Path | Expected LF SHA256 | Start LF SHA256 | Completion LF SHA256 | Completion blob LF SHA256 | Match |
| --- | --- | --- | --- | --- | --- |
| simulation/diagnostics/detector_round3_design_note.md | b1309a7463b1d7b1f277fd4dd56e997f90fecf2386411871be22ccfabed6db83 | b1309a7463b1d7b1f277fd4dd56e997f90fecf2386411871be22ccfabed6db83 | b1309a7463b1d7b1f277fd4dd56e997f90fecf2386411871be22ccfabed6db83 | b1309a7463b1d7b1f277fd4dd56e997f90fecf2386411871be22ccfabed6db83 | True |
| simulation/diagnostics/detector_run_r3_a3_constants.json | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | True |
| simulation/diagnostics/detector_round2_design_note.md | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 | True |
| simulation/diagnostics/detector_run_r2_constants.json | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | True |
| simulation/diagnostics/detector_run_cal_constants.json | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | True |
| simulation/cusum_detector_v2.py | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | True |
| simulation/diagnostics/detector_run_eval_executor.py | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | True |
| simulation/diagnostics/detector_design_note.md | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | True |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | True |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | True |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | True |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | True |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | True |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | True |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | True |
| simulation/diagnostics/drift_mapping_design_note.md | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 | True |

Committed blob SHA1 values for all four notes, all three constants files, the detector, and every pinned source are in the manifest and source_readings JSON.

### Module hashes

Bases: raw working-tree bytes and LF-normalized working-tree bytes.

| Module | Raw SHA256 | LF-normalized SHA256 |
| --- | --- | --- |
| simulation/agents.py | de5f196f4732808d3bba99026f618564505ea4cf557bd2167358a524fe7850c0 | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca |
| simulation/attack_adapter_v2.py | e4dd5a436ab33b348691b8c777608a655147610603181705694dcb3b2c35dcfe | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee |
| simulation/constants_v2_stage15.py | 808ac150f51ae33acbbc326e108451e9ac9d54b3c0f4ccc7adc537c58254cc70 | 9637604b34f472dd97035fb42db5b9ce77620560776f2bfe2c6e5188e5d9b5c7 |
| simulation/constants_v2_stage18.py | 68c3c8fd29c451079496b9e44b2fe5892932cf1b431358ad549f45419a15873d | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b |
| simulation/defection.py | 20466e6fd4a592f24c5c6fe07a40bc683b243b3939e3b69a94a1fcfc4ae269dd | 071abb31a84231386572cdfd901524647a5800f56d8117c89c44c5f75e24f97a |
| simulation/diagnostics/detector_run_r3_eval_channels.py | 4fd5c1588b9940489d935588666e0df81b8114ff6bfaae5c604f4541ed6dd4c6 | 4fd5c1588b9940489d935588666e0df81b8114ff6bfaae5c604f4541ed6dd4c6 |
| simulation/diagnostics/detector_run_r3_eval_executor.py | 301684b83bb155daf745f03bf0f0ccf50a35c11ee911e66dd5e46b39ab0d8338 | 301684b83bb155daf745f03bf0f0ccf50a35c11ee911e66dd5e46b39ab0d8338 |
| simulation/diagnostics/detector_run_r3_eval_report.py | dc8a93e337d8598b8f950be79bc98c7c101a014062078be39828cf978448db92 | dc8a93e337d8598b8f950be79bc98c7c101a014062078be39828cf978448db92 |
| simulation/metrics.py | 8fdbb78c5ddf41bb5deeb49fe11adfd9db55d323d68d6b5feb24d9e83439c2f7 | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f |
| simulation/model.py | e2c9ea91b5b182915d4db00ea09ba896ec3f85a5d92a7aea7329bc3cce5c2945 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 |
| simulation/run_attack_vector_revalidation_v2.py | da7913799d0d4e11f52f770e313875764d27b20ad33157a7aa9c1fa00df418e2 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 |
| simulation/working_factor.py | 0afde923081fe34d1ada86e2928286d45c905441053f643968ea9b13007b683d | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 |

Operational retry implementation: detector_run_r3_eval_executor.py, LF-normalized SHA256 301684b83bb155daf745f03bf0f0ccf50a35c11ee911e66dd5e46b39ab0d8338.

Artifact hashes use LF-normalized bytes. CSV row counts use csv.DictReader excluding headers, with null for non-CSV outputs. The manifest lists itself separately without a recursive self-hash.
