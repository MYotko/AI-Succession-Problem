# Measurement Tampering: paired characterization, stage A, attempt 2

This is not a containment evaluation, not a defense rate, and reinstates no withdrawn figure. No ratio of two measured counts was computed by the registered analysis. The pinned runner computed and recorded its legacy capture_rate field verbatim for provenance; that field was not used by any registered quantity and is absent from report tables. The Section 10 interpretation is reserved for the operator.

## P1: ratified yields, primary

Counted from these runs using the committed paired_difference, treatment corruption active minus control corruption disabled, paired exactly by seed within each defense state.

| Defense | Pairs | Mean difference | Paired standard error | t statistic |
| --- | --- | --- | --- | --- |
| off | 60 | 0.0 | 0.0 | undefined |
| on | 60 | 0.0 | 0.0 | undefined |

## P2: blocked yield conditions

| Defense | Pairs | Mean difference | Paired standard error | t statistic |
| --- | --- | --- | --- | --- |
| off | 60 | 0.0 | 0.0 | undefined |
| on | 60 | 0.0 | 0.0 | undefined |

An undefined t statistic means paired standard error is exactly zero.

## P3: integer yield-counter totals

All entries below are counted totals.

| Arm | Defense | Corruption | Runs | evaluated_yield_opportunities | honest_yield_opportunities | ratified_yields | yield_checks | yield_condition_blocked_count | yield_condition_met_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C0_D0 | off | off | 60 | 0 | 14763 | 0 | 15000 | 0 | 0 |
| C1_D0 | off | on | 60 | 0 | 14763 | 0 | 15000 | 0 | 0 |
| C0_D1 | on | off | 60 | 60 | 60 | 60 | 15000 | 0 | 60 |
| C1_D1 | on | on | 60 | 60 | 60 | 60 | 15000 | 0 | 60 |

## P4: action-modified counts

| Arm | Runs | Recorded action_modified true |
| --- | --- | --- |
| C0_D0 | 60 | 0 |
| C1_D0 | 60 | 0 |
| C0_D1 | 60 | 0 |
| C1_D1 | 60 | 0 |
| All | 240 | 0 |

## Execution and gate record

Attempt 1 halted before T1 on the ratio-prohibition conflict, with zero of 240 runs launched. Committed Amendment 2 resolved that conflict by permitting verbatim provenance retention while excluding the legacy field from registered analysis.

The analysis exclusion assertion passed: zero registered reads of the legacy field. The restricted mapping permits only the seed, arm labels, action_modified, and six declared integer counters. No difference of differences was computed and no other transition cost was run.

T0 passed in full. The known CRLF worktree against LF blobs was not repaired. The expected global Git ignore permission warning is recorded below.

T1 control inertness passed over 24 synthetic states with NumPy seed 20260917: all 24 control states were exactly unchanged; all 24 production states changed well-being; all 8 states with a nonempty entropy history changed its last entry. Both construction cells matched the pinned runner build path field by field without stepping a model.

All 240 runs were executed through the unmodified run_single. A transparent factory observer delegated to the original factory and observed the original step return after each step. The copied recorder recomputed raw entropy, checked exact cache equality, and verified unchanged NumPy random state. Per-step fallback increases were checked under Amendment 2. These recorder checks do not apply the drift-specific honest-arm adapter-inactivity requirement to the corruption-disabled measurement arm, which retains the configured measurement adapter.

The no-op replacement had the production method signature, returned None, and was installed only inside each control worker. Method restoration was verified after every run. The original factory reference was restored after every run.

Configuration: measurement_tampering, full mode, base_transition_cost 1.5, 300 requested steps, attack onset 50, 300 candidates and 20 rollout steps; seeds 1835087000 through 1835087059, each used once in each of the four cells. Every runner row field was preserved.

Recorded end reasons: {"step_limit": 240}.

Configured CPU budget: operator-specified 16 cores. Actual peak concurrent workers: 15. Normal cap 15; work cap 12. The synthetic scheduler checks covered caps, graceful mode transitions, deterministic job assignment, and skipping completed jobs on resumption. The runtime control is vector_paired_run_a2_control.json. The effective numerical-library thread count was verified as one in every worker. These worker limits are not an operating-system CPU reservation.

Mode changes: [{"mode": "normal", "resumption": true, "utc": "2026-09-18T02:45:28.552742+00:00"}].

Resumed jobs: [{"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087030", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087030}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087031", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087031}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087032", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087032}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087033", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087033}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087034", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087034}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087035", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087035}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087036", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087036}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087037", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087037}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087038", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087038}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087039", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087039}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087040", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087040}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087041", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087041}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087042", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087042}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087043", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087043}, {"arm": {"corruption_active": false, "defense_active": true, "name": "C0_D1"}, "attempt": 2, "job": "C0_D1_1835087044", "reason": "provider usage limit", "restart_step": 0, "seed": 1835087044}]. Preserved earlier completions: 150.

Continuous checks passed for every completed run. Non-permitted fallback increases: 0. Exact entropy checks and unchanged-random-state recorder calls: 72000 each.

The write guard permits only the attempt 2 artifact prefix and the explicit os.devnull exemption. Bytecode writes were disabled. No production file was edited.

Transient permission errors on JSON reads and atomic replacement had a five-second bounded retry. Retry events recorded: 2. Operational layer LF-normalized SHA256: e63aa052d1267ca5328af686edb439e23c605f699794c936b272488e7a6f3a55.

Machine: YOTKOTEST. HEAD: b23674db031bf647d6b0d3c04cd051699d2ec8f1. Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]. NumPy: 2.4.4.

## Source pins, start and completion

Hashes below use LF-normalized bytes. Both committed blobs and working-tree readings matched at start and completion; committed blob identities and per-module raw/LF hashes are included in the manifest.

| Path | Start SHA256 | Completion SHA256 |
| --- | --- | --- |
| simulation/diagnostics/per_vector_paired_design_note.md | b63a552d7bc7cee1ba892b3079964ef9fe06e6592ad65bb4d61575550518b0a3 | b63a552d7bc7cee1ba892b3079964ef9fe06e6592ad65bb4d61575550518b0a3 |
| simulation/attack_metrics_v2.py | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b |
| simulation/diagnostics/detector_design_note.md | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad |
| simulation/diagnostics/drift_mapping_design_note.md | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 |
| simulation/diagnostics/detector_run_eval_executor.py | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff |

## Authorized resumption

The interruption reason was the provider usage limit. Counted at resumption: 150 preserved completions, 15 restarted runs, and 75 previously unlaunched runs. Preserved completion records, row hashes, log hashes, arm labels, and seeds validated. No preserved run was rerun or altered. Interrupted runs restarted from step 0 with the original seed and arm, with their prior initial, progress, and step artifacts retained under .partial names.

The saved T1 gates were not rerun. Their passing results and recorded source pins were verified against the current pins before resumption. Gate evidence LF-normalized SHA256: f44d131d3072ed1cbc42775c3fa65eaec63b9b2da32fb3ce2d6ed98af6bd3e4a. This operational resumption changed no registered procedure.

Restarted runs, each due to the provider usage limit:

| Arm | Seed | New attempt |
| --- | --- | --- |
| C0_D1 | 1835087030 | 2 |
| C0_D1 | 1835087031 | 2 |
| C0_D1 | 1835087032 | 2 |
| C0_D1 | 1835087033 | 2 |
| C0_D1 | 1835087034 | 2 |
| C0_D1 | 1835087035 | 2 |
| C0_D1 | 1835087036 | 2 |
| C0_D1 | 1835087037 | 2 |
| C0_D1 | 1835087038 | 2 |
| C0_D1 | 1835087039 | 2 |
| C0_D1 | 1835087040 | 2 |
| C0_D1 | 1835087041 | 2 |
| C0_D1 | 1835087042 | 2 |
| C0_D1 | 1835087043 | 2 |
| C0_D1 | 1835087044 | 2 |

Previously unlaunched runs, now completed:

| Arm | Seed |
| --- | --- |
| C0_D1 | 1835087045 |
| C0_D1 | 1835087046 |
| C0_D1 | 1835087047 |
| C0_D1 | 1835087048 |
| C0_D1 | 1835087049 |
| C0_D1 | 1835087050 |
| C0_D1 | 1835087051 |
| C0_D1 | 1835087052 |
| C0_D1 | 1835087053 |
| C0_D1 | 1835087054 |
| C0_D1 | 1835087055 |
| C0_D1 | 1835087056 |
| C0_D1 | 1835087057 |
| C0_D1 | 1835087058 |
| C0_D1 | 1835087059 |
| C1_D1 | 1835087000 |
| C1_D1 | 1835087001 |
| C1_D1 | 1835087002 |
| C1_D1 | 1835087003 |
| C1_D1 | 1835087004 |
| C1_D1 | 1835087005 |
| C1_D1 | 1835087006 |
| C1_D1 | 1835087007 |
| C1_D1 | 1835087008 |
| C1_D1 | 1835087009 |
| C1_D1 | 1835087010 |
| C1_D1 | 1835087011 |
| C1_D1 | 1835087012 |
| C1_D1 | 1835087013 |
| C1_D1 | 1835087014 |
| C1_D1 | 1835087015 |
| C1_D1 | 1835087016 |
| C1_D1 | 1835087017 |
| C1_D1 | 1835087018 |
| C1_D1 | 1835087019 |
| C1_D1 | 1835087020 |
| C1_D1 | 1835087021 |
| C1_D1 | 1835087022 |
| C1_D1 | 1835087023 |
| C1_D1 | 1835087024 |
| C1_D1 | 1835087025 |
| C1_D1 | 1835087026 |
| C1_D1 | 1835087027 |
| C1_D1 | 1835087028 |
| C1_D1 | 1835087029 |
| C1_D1 | 1835087030 |
| C1_D1 | 1835087031 |
| C1_D1 | 1835087032 |
| C1_D1 | 1835087033 |
| C1_D1 | 1835087034 |
| C1_D1 | 1835087035 |
| C1_D1 | 1835087036 |
| C1_D1 | 1835087037 |
| C1_D1 | 1835087038 |
| C1_D1 | 1835087039 |
| C1_D1 | 1835087040 |
| C1_D1 | 1835087041 |
| C1_D1 | 1835087042 |
| C1_D1 | 1835087043 |
| C1_D1 | 1835087044 |
| C1_D1 | 1835087045 |
| C1_D1 | 1835087046 |
| C1_D1 | 1835087047 |
| C1_D1 | 1835087048 |
| C1_D1 | 1835087049 |
| C1_D1 | 1835087050 |
| C1_D1 | 1835087051 |
| C1_D1 | 1835087052 |
| C1_D1 | 1835087053 |
| C1_D1 | 1835087054 |
| C1_D1 | 1835087055 |
| C1_D1 | 1835087056 |
| C1_D1 | 1835087057 |
| C1_D1 | 1835087058 |
| C1_D1 | 1835087059 |

Resumption source-pin readings:

| Path | Resumption SHA256 |
| --- | --- |
| simulation/diagnostics/per_vector_paired_design_note.md | b63a552d7bc7cee1ba892b3079964ef9fe06e6592ad65bb4d61575550518b0a3 |
| simulation/attack_metrics_v2.py | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b |
| simulation/diagnostics/detector_design_note.md | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad |
| simulation/diagnostics/drift_mapping_design_note.md | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 |
| simulation/diagnostics/detector_run_eval_executor.py | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff |

## T0 stderr warnings

- warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
- warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied

## Tool-layer workarounds

- Authoring command exceeded the Windows command-length limit before execution; split payloads into separate shorter shell writes without changing their content.
- CIM process inspection was denied before project code ran; used Get-Process to check for active Python workers.

No exploratory analysis was performed.
