# Gate 3 recovery confirmation: halt report

## Registered results

R1 through R6: not measured. Batch runs launched: 0. Batch runs completed: 0. Registered batch runs: 180. Gate model runs launched: 0.

Sign fixture: not run. Reduced attack-validity check: not measured. Selection-condition comparisons: not measured.

## Halt reason

Specification conflict: the committed defense_recovery_design_note.md governs simulation/diagnostics/defense_recovery_run_ (line 7), and Section 9 restricts writes to that governed prefix and os.devnull (line 166). Amendment 1 does not authorize a different output prefix. The dispatch requires all outputs under simulation/diagnostics/defense_recovery_conf_run_, which is outside the note's governed prefix. The dispatch requires a halt on any conflict with the note.

The committed note names its governed prefix at line 7 and restricts writes to that prefix in Section 9, line 166. Section 10 declares the confirmation but does not amend that write scope. The dispatch requires the distinct defense_recovery_conf_run_ prefix and requires a halt on a conflict with the note.

T0: passed. T1 and execution were not started.

This is gate 3 of the promotion plan. The recovery rule, its three quiet periods, the selection rule and the criterion were fixed before any run. This is not a promotion decision and selects no parameter. No ratio of two measured counts was computed. Applying the Section 6 selection rule and criterion and the Section 8 interpretation is reserved for the operator.

## Source readings

SHA256 values below use LF-normalized bytes. Both committed blobs and working-tree files were checked at T0 and completion.

| File | Pin | T0 blob | T0 worktree | Completion blob | Completion worktree |
| --- | --- | --- | --- | --- | --- |
| simulation/diagnostics/defense_recovery_design_note.md | 23f07aeff3953c237f5ea71101791e00b54f258371082075fc0afe77a2453250 | 23f07aeff3953c237f5ea71101791e00b54f258371082075fc0afe77a2453250 | 23f07aeff3953c237f5ea71101791e00b54f258371082075fc0afe77a2453250 | 23f07aeff3953c237f5ea71101791e00b54f258371082075fc0afe77a2453250 | 23f07aeff3953c237f5ea71101791e00b54f258371082075fc0afe77a2453250 |
| simulation/diagnostics/defense_heldout_design_note.md | f1140c037528c3503ceddd56b6e780238b8bf2e78e183af757171900663f37dd | f1140c037528c3503ceddd56b6e780238b8bf2e78e183af757171900663f37dd | f1140c037528c3503ceddd56b6e780238b8bf2e78e183af757171900663f37dd | f1140c037528c3503ceddd56b6e780238b8bf2e78e183af757171900663f37dd | f1140c037528c3503ceddd56b6e780238b8bf2e78e183af757171900663f37dd |
| simulation/diagnostics/ARTIFACT_CONVENTION.md | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb |
| simulation/diagnostics/drift_defense_design_note.md | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 | cb39f08611759d9f9ac5b350af8bbbe267cff857f7d3ced01f67c16f76e4e920 |
| simulation/diagnostics/drift_defense_run_executor.py | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 | 75ce4846ce1d9730d0a3e37ae2c880e14ee058b45cbd1b1fd2e875791d3896b9 |
| simulation/diagnostics/detector_run_cal_constants.json | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 |
| simulation/diagnostics/detector_run_r3_a3_constants.json | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 | 0bcb751e667af145ab6e36d85780e81ff3bc8dcc757d72ba923e4341cc16ec35 |
| simulation/cusum_detector_v2.py | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 |
| simulation/attack_metrics_v2.py | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b |

## Execution metadata

Machine: YotkoTest. HEAD: c74f5f2e43ca3bdf21c89fee8c79932517852efb. Python: 3.14.3. NumPy installed version: 2.4.4.

Simulation workers launched: 0. Numerical-library thread limits: not exercised. Resumed seeds: none. Executor self-fixes: none.

Tool-layer workarounds:

- Rewrote the finalizer-authoring tool call without unescaped backticks after a tooling parse error; no project code ran.

T0 stderr warnings:

> warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied

Operational I/O retry events: 0.

No exploratory analysis was performed.
