# Recovery evaluation, attempt 2: pre-execution halt

Status: HALTED after T0 and before T1. T0 passed.
Batch runs launched: 0 of 300. Completed batch runs: 0. Gate runs: 0. Model steps: 0.

## Halt reason

The dispatch names the held-out pre-registration as its specification, but requires the recovery design and quantities.

- Dispatch: THE SPECIFICATION names simulation/diagnostics/defense_heldout_design_note.md as the committed pre-registration.
  Committed evidence: The held-out note governs defense_heldout_run_ and registers Y1 through Y5 with OFF and GRADED. The recovery note governs defense_recovery_run_ and its Sections 3 through 5 specify the recovery rule, 300 runs, five defense arms, and R1 through R6.
  Conflict: The named governing specification does not agree with this dispatch's recovery design and registered quantities.
  Handling: Where anything in this prompt appears to conflict with a note, HALT and report the conflict.

- Dispatch: The attempt context says this attempt writes under defense_recovery_run_a2_a2_. WRITE SCOPE and T3 through T5 specify defense_recovery_run_a2_* and filenames beginning defense_recovery_run_a2_.
  Committed evidence: The recovery note's broad governed prefix is defense_recovery_run_; both attempt prefixes fit it.
  Conflict: The attempt context and required artifact filenames use different prefixes.
  Handling: Additional dispatch inconsistency recorded with the governing-specification halt. Halt artifacts use the exact T4 and T5 filenames inside WRITE SCOPE.

Attempt 2 corrects the earlier T4 and T5 quantity labels and gate number. The governing-specification mismatch remains.

## Registered results

This dispatch requests gate 3 of the promotion plan. The recovery rule, its three quiet periods, selection rule and criterion are committed in the recovery note.
This halt record is not a promotion decision and selects no parameter.
No ratio of two measured counts was computed. Applying the Section 6 selection rule and criterion and Section 8 interpretation is reserved for the operator.

- R1: not measured. Harm direction: negative.
- R2: not measured. Harm direction: positive.
- R3: not measured. No harm direction.
- R4: not measured. No harm direction specified.
- R5: not measured. No harm direction specified.
- R6: not measured. Liveness and auditability.

Sign fixture: not run. Attack-validity check: not run. Predictions: not evaluated.
No exploratory analysis was performed.

## Source pins at start and completion

Basis: SHA256 on LF-normalized bytes. Committed blobs were read with git cat-file only after T0 verified their hashes.

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

## Execution metadata

Machine: YotkoTest. HEAD: b5f7683bf4c83c8888da9a96a85af2181b4cadbd.
Python: 3.14.3. NumPy: 2.4.4 (package metadata; not imported).
Operator-stated CPU budget: 16. Mode: normal. Worker limit: 15. Workers launched: 0.
Numerical-library thread environment: 1. No effective per-worker limit was verified because no worker was launched.
No simulation module or committed executor was imported or copied.
No execution, merge or per-run deletion occurred. No resumed seeds. No tool-layer workarounds.
JSON permission retry events: 0.

## T0 stderr warnings

- warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied

The expected warning was recorded without repair.
