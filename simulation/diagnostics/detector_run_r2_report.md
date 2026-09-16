# Detector round 2, stage A: derivation

No model was stepped, no arm was run, no detector was evaluated, and nothing was interpreted. Stage B is a separate dispatch that may begin only after these outputs are committed and pushed.

Status: COMPLETE.

## Derived values versus pins

| Quantity | Derived | Pinned | Match |
| --- | --- | --- | --- |
| attempt1 logs | 107 | 107 | True |
| attempt2 logs | 13 | 13 | True |
| PRIMARY_2_0 span_count | 120 | 120 | True |
| PRIMARY_2_0 crossing_runs | 42 | 42 | True |
| PRIMARY_2_0 maximum_span | 22 | 22 | True |
| PRIMARY_2_0 k | 9 | 9 | True |
| SECONDARY_1_5 span_count | 120 | 120 | True |
| SECONDARY_1_5 crossing_runs | 0 | 0 | True |
| SECONDARY_1_5 maximum_span | 0 | 0 | True |
| SECONDARY_1_5 k | 2 | 2 | True |
| SECONDARY_2_5 span_count | 120 | 120 | True |
| SECONDARY_2_5 crossing_runs | 120 | 120 | True |
| SECONDARY_2_5 maximum_span | 136 | 136 | True |
| SECONDARY_2_5 k | 106 | 106 | True |
| T975 threshold | 4.507729894543943 | 4.507729894543943 | True |
| T975 calibration maxima at or above threshold | 3 | 3 | True |
| T95 threshold | 4.055050806319135 | 4.055050806319135 | True |
| T95 calibration maxima at or above threshold | 6 | 6 | True |
| T90 threshold | 2.6499927544530903 | 2.6499927544530903 | True |
| T90 calibration maxima at or above threshold | 12 | 12 | True |
| T975 equals committed round 1 g threshold | 4.507729894543943 | 4.507729894543943 | True |

## Span percentile inputs

| Case | g_star | Spans | Crossing runs | Maximum span | P97.5, linear | k |
| --- | --- | --- | --- | --- | --- | --- |
| PRIMARY_2_0 | 1.0965735902799727 | 120 | 42 | 22 | 8.049999999999983 | 9 |
| SECONDARY_1_5 | 1.27031007207211 | 120 | 0 | 0 | 0.0 | 2 |
| SECONDARY_2_5 | 0.966516292749662 | 120 | 120 | 136 | 105.17499999999994 | 106 |

Required Section 4 caveat, quoted as fixed specification context for SECONDARY_2_5:

> At a reference successor capability of 2.5, g_star lies below the honest median of g, every honest calibration run spends long spans above it, and k is accordingly large. A hazard there measures persistence far beyond honest behavior rather than the approach to a defection boundary.

## g threshold variants

| Variant | Percentile | Threshold | Calibration runs at or above | Denominator |
| --- | --- | --- | --- | --- |
| T975 PRIMARY | 97.5 | 4.507729894543943 | 3 | 120 |
| T95 SECONDARY | 95.0 | 4.055050806319135 | 6 | 120 |
| T90 SECONDARY | 90.0 | 2.6499927544530903 | 12 | 120 |

## Constants carried forward

These values are read from the committed round 1 constants. They are copied unchanged, without recomputation. The round 1 g threshold remains recorded separately from the three derived variants.

| Channel | Reference | Allowance | Round 1 threshold |
| --- | --- | --- | --- |
| entropy | 0.9890951785336365 | 0.003549173553323096 | 0.17319485850717864 |
| g | 0.9786446054615587 | 0.022160874873702576 | 4.507729894543943 |
| L | 0.7360674421560752 | 0.056644201005884506 | 15.04497999532887 |

## Inputs and execution

Read and verified 120 completion records and their named logs from commit b84199fd5b71041870e17acea22e0145aaf16e10. Logs: 107 attempt1 and 13 attempt2. Every log matched its completion record LF-normalized SHA256 before CSV parsing. Log selection used the completion record raw_log field, not filename inference.

For each g_star, each run contributes its longest consecutive span at steps 50 and up, including zero when no step qualifies. The 120 integers use NumPy percentile with method="linear" at 97.5; k is max(2, ceil(P)). The threshold derivation uses only the committed g per_run_maxima array. No detector function was called.

All 360 longest-span values, their seeds, and the three g_star labels are in detector_run_r2_spans.csv and detector_run_r2_constants.json. Full-precision values, binary64 representations, input hashes, committed blob SHA1 values, and read commits are in the constants file.

Machine: YotkoTest. HEAD: 684fa7006155fb81349f6f59c11be22a5f59d2cb. Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]. NumPy: 2.4.4.

Simulation workers: 0. Derivation processes: 1. Numerical-library threads configured to one and verified through the loaded OpenBLAS query. No randomness was consumed.

The write guard permits only simulation/diagnostics/detector_run_r2_* and os.devnull. The null-device exemption is present. Bytecode writes are disabled.

## T0 and source pins

T0 passed the branch, ancestry, tracked-tree, publication, committed and working-tree hash, inherited source pin, completion-record count, and fresh namespace checks. The known CRLF/LF condition was retained without normalization.

| Path | Expected LF SHA256 | T0 working-tree LF SHA256 | Completion working-tree LF SHA256 | Completion committed LF SHA256 | Match |
| --- | --- | --- | --- | --- | --- |
| simulation/diagnostics/detector_round2_design_note.md | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 | True |
| simulation/diagnostics/detector_design_note.md | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | True |
| simulation/diagnostics/detector_run_cal_constants.json | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | True |
| simulation/cusum_detector_v2.py | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | True |
| simulation/diagnostics/detector_run_eval_executor.py | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | True |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | True |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | True |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | True |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | True |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | True |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | True |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | True |

T0 stderr warnings:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

Every artifact hash uses LF-normalized bytes. CSV row counts use csv.DictReader excluding headers; non-CSV row counts are null. The manifest lists itself without a recursive self-hash.
