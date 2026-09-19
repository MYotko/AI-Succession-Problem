# Measurement Tampering: paired characterization, stage A'

This is not a containment evaluation, not a defense rate, and reinstates no withdrawn figure. No ratio of two measured counts was computed by the registered analysis. The pinned runner computed and recorded its legacy capture_rate field verbatim for provenance; that field was not used by any registered quantity and is absent from report tables. The Section 10 interpretation is reserved for the operator.

## P1': ratified yields, primary

Counted from these runs using the committed paired_difference, treatment production branch minus control branch disabled, paired exactly by seed within each defense state.

| Defense | Pairs | Mean difference | Paired standard error | t statistic |
| --- | --- | --- | --- | --- |
| off | 30 | -1.0 | 0.0 | undefined |
| on | 30 | 0.0 | 0.0 | undefined |

## P2': met yield conditions

| Defense | Pairs | Mean difference | Paired standard error | t statistic |
| --- | --- | --- | --- | --- |
| off | 30 | -1.0 | 0.0 | undefined |
| on | 30 | 0.0 | 0.0 | undefined |

An undefined t statistic means paired standard error is exactly zero.

## P3': integer yield-counter totals

All entries below are counted totals.

| Arm | Defense | Branch active | Runs | evaluated_yield_opportunities | honest_yield_opportunities | ratified_yields | yield_checks | yield_condition_blocked_count | yield_condition_met_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B0_D0 | off | off | 30 | 30 | 30 | 30 | 7500 | 0 | 30 |
| B1_D0 | off | on | 30 | 0 | 7252 | 0 | 7500 | 0 | 0 |
| B0_D1 | on | off | 30 | 30 | 30 | 30 | 7500 | 0 | 30 |
| B1_D1 | on | on | 30 | 30 | 30 | 30 | 7500 | 0 | 30 |

## P4': action-modified counts

| Arm | Runs | Recorded action_modified true |
| --- | --- | --- |
| B0_D0 | 30 | 0 |
| B1_D0 | 30 | 0 |
| B0_D1 | 30 | 0 |
| B1_D1 | 30 | 0 |
| All | 120 | 0 |

## Execution and gate record

Stage A targeted the legacy apply_measurement_corruption method. Amendment 3 replaced that control with the v2 model-module adapt_yield_evaluation binding and moved the secondary quantity to yield_condition_met_count. Earlier stage A artifacts were retained.

The analysis exclusion assertion passed: zero registered reads of the legacy field. The restricted mapping permits only the seed, arm labels, action_modified, and six declared integer counters. No difference of differences was computed and no other transition cost was run.

T0 passed in full. The known CRLF worktree against LF blobs was not repaired. The expected global Git ignore permission warning is recorded below.

T1 control inertness passed over 24 synthetic input sets with NumPy seed 20260918. The pass-through returned the two input values and the production honest_fires expression exactly and changed no model or event field in all 24 sets. Production with defense off changed both evaluated values in all 24 sets; production with defense on returned the inputs exactly in all 24 sets. All measured synthetic values are recorded in the gates artifact. Both construction cells matched the pinned runner build path field by field without model steps.

The separate 60-step binding probe at seed 1835087060, defense off, recorded 10 pass-through calls. The production binding was restored by identity afterward. All recorder and fallback checks passed on that probe.

All 120 runs were executed through the unmodified run_single. A transparent factory observer delegated to the original factory and observed the original step return after each step. The copied recorder recomputed raw entropy, checked exact cache equality, and verified unchanged NumPy random state. Per-step fallback increases were checked under Amendment 2. These recorder checks do not apply the drift-specific honest-arm adapter-inactivity requirement to the branch-disabled measurement arm, which retains the configured measurement adapter.

The pass-through had the production signature and read or wrote no model state or event field. It returned the incumbent and successor as floats and honest_fires from the pinned expression. It was bound only in the model module, inside each control worker, with a call counter outside the model. Restoration to the production binding was verified after every run; control call counts are in the run records and runs CSV. The original factory reference was restored after every run.

Configuration: measurement_tampering, full mode, base_transition_cost 1.5, 300 requested steps, attack onset 50, 300 candidates and 20 rollout steps; seeds 1835087060 through 1835087089, each used once in each of the four cells. Every runner row field was preserved.

Recorded end reasons: {"step_limit": 120}.

Configured CPU budget: operator-specified 16 cores. Actual peak concurrent workers: 15. Normal cap 15; work cap 12. The synthetic scheduler checks covered caps, graceful mode transitions, deterministic job assignment, and skipping completed jobs on resumption. The runtime control is vector_paired_run_ap_control.json. The effective numerical-library thread count was verified as one in every worker. These worker limits are not an operating-system CPU reservation.

Mode changes: [{"mode": "normal", "utc": "2026-09-19T01:11:09.812922+00:00"}].

Resumed jobs: []. Preserved earlier completions: 0.

Continuous checks passed for every completed run. Non-permitted fallback increases: 0. Exact entropy checks and unchanged-random-state recorder calls: 36000 each.

The write guard permits only the stage A prime artifact prefix and the explicit os.devnull exemption. Bytecode writes were disabled. No production file was edited.

Transient permission errors on JSON reads and atomic replacement had a five-second bounded retry. Retry events recorded: 0. Operational layer LF-normalized SHA256: 79df5662faf21bc0c20ba58b92bae461f6104af9ab36bb24e1e211e1281d4b1e.

Machine: YOTKOTEST. HEAD: cc8790e90f013c631141c47003e2784c46107cc0. Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]. NumPy: 2.4.4.

## Source pins, start and completion

Hashes below use LF-normalized bytes. Both committed blobs and working-tree readings matched at start and completion; committed blob identities and per-module raw/LF hashes are included in the manifest.

| Path | Start SHA256 | Completion SHA256 |
| --- | --- | --- |
| simulation/diagnostics/per_vector_paired_design_note.md | 780e2238ff34a6fbe4df141ebf3e921be7819954329f9f570165da1c5bc2dbfa | 780e2238ff34a6fbe4df141ebf3e921be7819954329f9f570165da1c5bc2dbfa |
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
| simulation/diagnostics/vector_paired_run_a2_executor.py | e63aa052d1267ca5328af686edb439e23c605f699794c936b272488e7a6f3a55 | e63aa052d1267ca5328af686edb439e23c605f699794c936b272488e7a6f3a55 |
| simulation/diagnostics/vector_paired_run_a2_analysis.py | ae6a82e42b3d1355751ff93129b9da7ad6248c6cdf75973bfeabf1efaf1e3b90 | ae6a82e42b3d1355751ff93129b9da7ad6248c6cdf75973bfeabf1efaf1e3b90 |

## T0 stderr warnings

- warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied

## Tool-layer workarounds

None.

No exploratory analysis was performed.
