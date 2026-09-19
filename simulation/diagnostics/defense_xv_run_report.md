# Cross-vector evaluation: halted before T1

Status: HALTED. T0 passed. No T1 probe and no evaluation run was launched: 0 of 720 runs.
The promotion gate criterion was not applied. No gate pass or failure decision is made.

## Halt reason

Specification conflict: cross-vector note Section 2 prohibits computing any ratio of two measured counts, while Section 3 and the dispatch require the unmodified pinned runner run_single. That function computes capture_rate as blocked / met when met is nonzero, using yield_condition_blocked_count and yield_condition_met_count. The cross-vector note supplies no exception for that legacy computation.

Section 2 of the committed cross-vector note states:

> It corrects no published figure, and no ratio of two measured counts is computed.

Section 3 and the dispatch require the pinned runner unchanged through run_single(task). At simulation/run_attack_vector_revalidation_v2.py:435, that function constructs the runner row with:

```python
'capture_rate': blocked / met if met else 0.0,
```

Here blocked is model.yield_condition_blocked_count and met is model.yield_condition_met_count. This is a source observation only. The function was not called. No exception was inferred from another pre-registration, and the required runner was not changed.

## Registered quantities

| Quantity | Status |
| --- | --- |
| X1 | Not measured |
| X2 | Not measured |
| X3 | Not measured |
| X4 | Not measured |
| X5 | Not measured |
| X6 | Not measured |

This dispatch is gate 1 of the promotion plan. It is intended to measure harm, not containment of these vectors. It is not a promotion decision and does not test input corruption. No ratio of two measured counts was computed. Applying the Section 6 criterion and the Section 7 interpretation is reserved for the operator.

Known-pathway qualification: the allocation channel was chosen knowing how the reallocation attack works. The channel constants were calibrated on the drift mapping construction. There are no headline measurement numbers or false-alarm counts in this halted attempt.

## Source pins

| Path | Start blob SHA256 LF | Start working-tree SHA256 LF | End blob SHA256 LF | End working-tree SHA256 LF |
| --- | --- | --- | --- | --- |
| simulation/diagnostics/defense_cross_vector_design_note.md | 963a741926daaf3d8792af4cf04fd154813d36255326bf70169b184bec7bd444 | 963a741926daaf3d8792af4cf04fd154813d36255326bf70169b184bec7bd444 | 963a741926daaf3d8792af4cf04fd154813d36255326bf70169b184bec7bd444 | 963a741926daaf3d8792af4cf04fd154813d36255326bf70169b184bec7bd444 |
| simulation/diagnostics/drift_defense_design_note.md | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 |
| simulation/diagnostics/drift_defense_run_executor.py | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 |
| simulation/diagnostics/vector_paired_run_ap_executor.py | 79df5662faf21bc0c20ba58b92bae461f6104af9ab36bb24e1e211e1281d4b1e | 79df5662faf21bc0c20ba58b92bae461f6104af9ab36bb24e1e211e1281d4b1e | 79df5662faf21bc0c20ba58b92bae461f6104af9ab36bb24e1e211e1281d4b1e | 79df5662faf21bc0c20ba58b92bae461f6104af9ab36bb24e1e211e1281d4b1e |
| simulation/diagnostics/detector_run_cal_constants.json | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 |
| simulation/diagnostics/detector_run_r3_a3_constants.json | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 |
| simulation/cusum_detector_v2.py | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 |
| simulation/attack_metrics_v2.py | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b |

## Execution provenance

Machine: YOTKOTEST. HEAD: d0d4c72bbb7bdebf7f057224eaae3b200be4ceca.
Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]. NumPy: 2.4.4.
Simulation workers: 0. Resumed seeds: none. Retry events: none.
The known CRLF working-tree condition was not changed.

T0 stderr warnings: ["warning: unable to access 'C:\\Users\\matty/.config/git/ignore': Permission denied"].

Tool-layer workaround: The prior-turn encoding helper was unavailable; an in-memory base64 encoder was recreated before rerunning the unchanged preflight.
