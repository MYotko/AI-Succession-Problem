# Per-vector paired characterization, stage A: HALTED

Specification conflict: the committed note Section 2 line 39 prohibits any function from computing or returning a ratio of two measured counts, while the dispatch requires unchanged run_single(task) and retention of every returned field. The pinned runner at line 435 computes and returns capture_rate as blocked / met if met else 0.0.

T0 passed all enumerated checks. T1 was not run. Zero of the planned 240 evaluation runs launched. No model was constructed or stepped. No paired value was computed.

## Registered quantities

| Quantity | Status |
| --- | --- |
| P1 | Not computed |
| P2 | Not computed |
| P3 | Not computed |
| P4 | Not computed |

## Conflict evidence

Read from the committed blobs at 3494cb9276629a2fde18aedea505de8b674b0fef.

The pre-registration, Section 2, line 39, states:

> No function computes or returns a ratio of two measured counts. D5 and D6 are why.

The pinned runner reads the measured counters at lines 389-390 and builds the returned row with this expression at line 435:

```python
'capture_rate': blocked / met if met else 0.0,
```

The dispatch requires calling run_single(task) unchanged and keeping every field it returns. Section 13 changes the arm design but does not exempt this ratio from Section 2. Neither the runner nor any recorded field was changed to resolve the conflict.

This is not a containment evaluation, not a defense rate, and reinstates no withdrawn figure. No ratio of two measured counts was computed in this halted attempt. The Section 10 interpretation is reserved for the operator.

## Provenance

Machine: YOTKOTEST. HEAD: 3494cb9276629a2fde18aedea505de8b674b0fef.
Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]. NumPy: 2.4.4.
Simulation workers used: 0. Planned normal-mode limit: 15 from the operator budget of 16. No worker thread verification was applicable.
Resumed seeds: none. JSON read retry events: 0.

Tool-layer workaround: Halt-recorder authoring had a tool-layer syntax error before any shell ran; removed nested backtick quoting and authored through a base64 shell command.

The write guard permits only vector_paired_run_a_ files directly under simulation/diagnostics/ and os.devnull. The null-device exemption is present. Bytecode writes are disabled.

| Pinned file | Expected LF SHA256 | Start blob / worktree | Completion blob / worktree | Match |
| --- | --- | --- | --- | --- |
| simulation/diagnostics/per_vector_paired_design_note.md | 592401276ee736900a58c3ff3c8a6a93055b9a890a14ba3becffa7017766c307 | 592401276ee736900a58c3ff3c8a6a93055b9a890a14ba3becffa7017766c307 / 592401276ee736900a58c3ff3c8a6a93055b9a890a14ba3becffa7017766c307 | 592401276ee736900a58c3ff3c8a6a93055b9a890a14ba3becffa7017766c307 / 592401276ee736900a58c3ff3c8a6a93055b9a890a14ba3becffa7017766c307 | True |
| simulation/attack_metrics_v2.py | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 / 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 / 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | True |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 / 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 / 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | True |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f / 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f / 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | True |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca / a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca / a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | True |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 / 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 / 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | True |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee / 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee / 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | True |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 / 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 / 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | True |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b / 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b / 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | True |

The inherited detector-note pin also matched: 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad.
The manifest records committed blob SHA1 values and module hashes, labeled by basis. No simulation module was executed.

T0 stderr warnings:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

Known CRLF/LF differences were preserved. No snapshot generator was invoked. No Git write operation was run.

The manifest hashes output files on LF-normalized bytes, counts CSV rows with csv.DictReader excluding headers, and excludes its own recursive self-hash.
