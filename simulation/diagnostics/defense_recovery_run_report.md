# Recovery evaluation: pre-execution halt

Status: HALTED after T0 and before T1. T0 passed. Zero of 300 batch runs were launched.
Gate runs: 0. Completed batch runs: 0. Model steps: 0.

## Specification conflicts

- Dispatch: T4 requires computing Y1 through Y5; T5 requires registered results Y1 through Y5 in order.
  Committed note: defense_recovery_design_note.md Section 5 registers R1 through R6. Section 8 requires analysis beyond R1 through R6 to be labeled exploratory and placed after registered results.
  Conflict: The required registered analysis and report quantities do not agree.

- Dispatch: T5 requires the report to state that this is gate 2 of the promotion plan.
  Committed note: defense_recovery_design_note.md title and Sections 1 and 6 identify this recovery evaluation as gate 3.
  Conflict: The required report gate identifier does not agree.

- Dispatch: THE SPECIFICATION names defense_heldout_design_note.md as the committed pre-registration.
  Committed note: defense_recovery_design_note.md governs defense_recovery_run_ and specifies recovery, fifteen cells and 300 runs; defense_heldout_design_note.md governs defense_heldout_run_ and registers Y1 through Y5.
  Conflict: The named governing note does not agree with the task's recovery design and output prefix.

The dispatch requires a halt when it conflicts with a committed note. No requirement was corrected or selected.

## Registered results

R1 through R6 were not measured. The attack-validity check and sign fixture were not run.
No paired value, ratio of two measured counts, prediction threshold result, parameter selection, or promotion decision was computed.
Sections 6 and 8 remain reserved for the operator.

## Source pins at start and completion

Basis: SHA256 of LF-normalized bytes. Each reading covers the committed HEAD blob and the working-tree file.

| File | Start committed | Start working tree | Completion committed | Completion working tree | Match |
| --- | --- | --- | --- | --- | --- |
| simulation/diagnostics/defense_recovery_design_note.md | b342866ea8618330e579f9f0151c0a7b01dbd6338627297c83d38d5fefc7aed5 | b342866ea8618330e579f9f0151c0a7b01dbd6338627297c83d38d5fefc7aed5 | b342866ea8618330e579f9f0151c0a7b01dbd6338627297c83d38d5fefc7aed5 | b342866ea8618330e579f9f0151c0a7b01dbd6338627297c83d38d5fefc7aed5 | true |
| simulation/diagnostics/defense_heldout_design_note.md | f1140c037528c3503ceddd56b6e780238b8bf2e78e183af757171900663f37dd | f1140c037528c3503ceddd56b6e780238b8bf2e78e183af757171900663f37dd | f1140c037528c3503ceddd56b6e780238b8bf2e78e183af757171900663f37dd | f1140c037528c3503ceddd56b6e780238b8bf2e78e183af757171900663f37dd | true |
| simulation/diagnostics/ARTIFACT_CONVENTION.md | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | true |
| simulation/diagnostics/drift_defense_design_note.md | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | true |
| simulation/diagnostics/drift_defense_run_executor.py | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | true |
| simulation/diagnostics/detector_run_cal_constants.json | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | true |
| simulation/diagnostics/detector_run_r3_a3_constants.json | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | true |
| simulation/cusum_detector_v2.py | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | true |
| simulation/attack_metrics_v2.py | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | true |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | true |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | true |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | true |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | true |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | true |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | true |

## Execution and artifacts

Machine: YotkoTest. HEAD: 1a0b167067d711d6158d10d1d84f06e72247f093.
Python: 3.14.3. NumPy package version: 2.4.4 (package metadata; NumPy was not imported).
CPU budget: 16, operator-stated for YOTKOTEST. Mode: normal. Worker limit: 15. Workers launched: 0.
Numerical-library thread environment: 1. Effective per-worker limits were not verified because no worker was launched.
No execution, artifact merge, per-run deletion, or registered analysis took place.
No simulation module or committed executor was imported or copied.
Resumed seeds: none. Tool-layer workarounds: none.
JSON permission retry events: 0.

## T0 stderr warnings

- warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied

The expected global git ignore permission warning was recorded without repair.
