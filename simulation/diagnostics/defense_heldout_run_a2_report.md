# Held-out attacks, attempt 2: halt

This is gate 2 of the promotion plan. The attacks were specified before any run.
It is not a promotion decision and does not test input corruption, deferred to stage B.
No ratio of two measured counts was computed. The Section 6 criterion and Section 8 interpretation are reserved for the operator.

Attempt 1 halted before T1. Amendment 1 changed Y3 harm to negative.

Status: HALTED. Registered quantities Y1 through Y5 were not computed.
Sign fixture: not run because execution halted before analysis.

Halt evidence: [{"error": "", "status": "HALTED", "traceback": "Traceback (most recent call last):\n  File \"C:\\Users\\matty\\Dev\\AI-Succession-Problem\\simulation\\diagnostics\\defense_heldout_run_a2_executor.py\", line 746, in main\n    if args.command=='all':gates()\n                           ~~~~~^^\n  File \"C:\\Users\\matty\\Dev\\AI-Succession-Problem\\simulation\\diagnostics\\defense_heldout_run_a2_executor.py\", line 562, in gates\n    evidence={'source_pins_start':pins(full=True),'scheduler':scheduler_checks()}\n                                                              ~~~~~~~~~~~~~~~~^^\n  File \"C:\\Users\\matty\\Dev\\AI-Succession-Problem\\simulation\\diagnostics\\defense_heldout_run_a2_executor.py\", line 612, in scheduler_checks\n    assert all(j['seed'] in range(1835087800,1835087160) for j in pending)\n           ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nAssertionError\n", "utc": "2026-09-20T12:26:33.380565+00:00", "where": "all:None"}]
## Source verification

| Path | Start blob | Start working tree | Completion blob | Completion working tree |
| --- | --- | --- | --- | --- |
| simulation/diagnostics/defense_heldout_design_note.md | 555fdba674139aebcaa7377daf1f19e3278e2c00f13ec742d729983f212be6b9 | 555fdba674139aebcaa7377daf1f19e3278e2c00f13ec742d729983f212be6b9 | 555fdba674139aebcaa7377daf1f19e3278e2c00f13ec742d729983f212be6b9 | 555fdba674139aebcaa7377daf1f19e3278e2c00f13ec742d729983f212be6b9 |
| simulation/diagnostics/ARTIFACT_CONVENTION.md | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb |
| simulation/diagnostics/drift_defense_design_note.md | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 |
| simulation/diagnostics/drift_defense_run_executor.py | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 |
| simulation/diagnostics/detector_run_cal_constants.json | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 |
| simulation/diagnostics/detector_run_r3_a3_constants.json | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 |
| simulation/cusum_detector_v2.py | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 |
| simulation/attack_metrics_v2.py | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b |
| simulation/diagnostics/detector_design_note.md | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad |
| simulation/diagnostics/detector_round3_design_note.md | 47ea6fdd6bd4191fb262d1923c367a143c4fd279b94473497f595c7bc2ea5293 | 47ea6fdd6bd4191fb262d1923c367a143c4fd279b94473497f595c7bc2ea5293 | 47ea6fdd6bd4191fb262d1923c367a143c4fd279b94473497f595c7bc2ea5293 | 47ea6fdd6bd4191fb262d1923c367a143c4fd279b94473497f595c7bc2ea5293 |
| simulation/diagnostics/detector_run_r2_constants.json | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 |
| simulation/diagnostics/detector_run_eval_executor.py | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 |
| simulation/diagnostics/defense_cross_vector_design_note.md | 70cb496651610f8e13b7c793854efb3a6d79754f2f19725701a8f41c3c9a05e7 | 70cb496651610f8e13b7c793854efb3a6d79754f2f19725701a8f41c3c9a05e7 | 70cb496651610f8e13b7c793854efb3a6d79754f2f19725701a8f41c3c9a05e7 | 70cb496651610f8e13b7c793854efb3a6d79754f2f19725701a8f41c3c9a05e7 |
| simulation/diagnostics/defense_xv_run_a2_executor.py | 25b544872c1b23ea96432e566a43a6483ca6bd9707318ade80ba12cd85a85b4a | 25b544872c1b23ea96432e566a43a6483ca6bd9707318ade80ba12cd85a85b4a | 25b544872c1b23ea96432e566a43a6483ca6bd9707318ade80ba12cd85a85b4a | 25b544872c1b23ea96432e566a43a6483ca6bd9707318ade80ba12cd85a85b4a |

## Execution evidence

HEAD: 939d4242101fcea06f84d892e5d38f2a0b7ed93a
Machine: YOTKOTEST
Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]
NumPy: 2.4.4

No source pin changed. No completed run was rerun.

Tool-layer workarounds:
A prior-turn in-memory helper was unavailable before any shell ran; the helper was rebuilt and the unchanged read-only preflight checks were repeated.

T0 stderr warnings:
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied

Worker execution metadata: []
Resumed runs: []
Permission retry events: []
