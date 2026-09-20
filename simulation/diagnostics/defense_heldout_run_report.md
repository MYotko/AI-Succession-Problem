# Held-out attacks: execution halt

Status: HALTED after T0 and committed-note reading, before T1.
Planned runs: 160. Launched runs: 0. Completed runs: 0. Model steps: 0.

This is gate 2 of the promotion plan. The attacks were specified before any run.
This is not a promotion decision. This does not test input corruption, which the note defers to stage B. No ratio of two measured counts was computed.
Applying the Section 6 criterion and the Section 8 interpretation is reserved for the operator.

## Registered quantities

| Quantity | Status |
| --- | --- |
| Y1 | Not computed |
| Y2 | Not computed |
| Y3 | Not computed |
| Y4 | Not computed |
| Y5 | Not computed |

## Sign fixture

Not run. No assertion result is claimed. The specification conflict was identified before T1 or analysis.

## Halt reasons

1. Section 6 defines Y3 as OFF minus GRADED for population at step 149 minus population at step 160 and states that positive Y3 is harm. The required fixture has a larger defended shock loss, producing a negative OFF-minus-GRADED difference, and must be labeled harm. Both requirements cannot be met unchanged.
2. Section 6 says: "Registered predictions, written before any run and reported as right or wrong." The dispatch prohibits saying whether a prediction was right or wrong beyond reporting its named number. The dispatch requires a halt on conflicts with the note.

No requirement was changed. No model was constructed or stepped. No attack, defense, registered quantity, criterion, or prediction was evaluated.

## Preconditions and source readings

T0a through T0e passed. The three governing notes were read by git cat-file after verification of their committed and working-tree hashes.
Inherited pins and declared source identities were recorded for halt evidence. All hashes in the following table use LF-normalized bytes.

| Source | Start committed | Start working tree | Halt committed | Halt working tree |
| --- | --- | --- | --- | --- |
| simulation/diagnostics/defense_heldout_design_note.md | 9bf462a95667994b97d7cb4fb2d14f541a04aed595600d4a58a2061f4fb592e4 | 9bf462a95667994b97d7cb4fb2d14f541a04aed595600d4a58a2061f4fb592e4 | 9bf462a95667994b97d7cb4fb2d14f541a04aed595600d4a58a2061f4fb592e4 | 9bf462a95667994b97d7cb4fb2d14f541a04aed595600d4a58a2061f4fb592e4 |
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

Source identities changed: [].
HEAD: 282b54fd5ce7d0ba507529131a03fe31deb599ca.

## Operational record

Workers launched: 0. No resumption, merge, or per-run deletion occurred.
No code was copied or imported from the committed executors. Their hashes identify declared source provenance.
Manifest hashes cover every generated artifact other than the manifest itself, whose self-hash would be recursive.

Machine: YotkoTest.
Python: 3.14.3.
NumPy: 2.4.4 (installed distribution metadata).

T0 stderr warnings:

    warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied

Tool-layer workarounds:

The initial T0 results were unavailable after context truncation; the same read-only checks were repeated and captured as structured evidence.
The halt-recorder authoring call failed during JavaScript parsing before any shell ran; embedded Markdown fence delimiters were removed and the authoring call was retried.

Permission retry events: 0.
