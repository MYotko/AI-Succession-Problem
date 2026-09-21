# Per-vector paired characterization, stage C: halt

This is a post-repair re-measurement of a quantity banked pre-repair. The two measure different substrates and neither supersedes the other.
No ratio of two measured counts was computed. No capture_rate values were recorded or used because no runs were launched. Section 10 interpretation is reserved for the operator.

Status: HALTED after T0, before T1 and before model construction. Runs launched: 0. Runs completed: 0. Planned runs: 900.

## Registered results

### C1

Not computed.

### C2

Not computed.

### C3

Not computed.

### C4

Not computed.

### C5

Not computed.

### C6

Not computed.

## Halt reason

C5 requires comparing the two zero-capture arms on every recorded field, including the pinned runner's capture_rate field. Amendment 2 (Section 14) excludes capture_rate from every registered quantity and requires asserting that no registered quantity reads it. C5 is a registered quantity, so both requirements cannot be satisfied without changing the specified comparison.

C5 cannot compare every returned field while satisfying Amendment 2. Excluding the field from C5 would change the specified comparison; including it would violate the amendment. Neither change was made.

The pinned runner source confirms that run_single returns the legacy field. The runner was read through its committed blob and was not imported or executed.

Capture-rate exclusion assertion: not run. No analysis was launched.
T0: all enumerated checks passed. T1: not run. Merge: not run. No exploratory analysis was performed.

## Source readings

| File | Start committed SHA256, LF | Start working-tree SHA256, LF | Completion committed SHA256, LF | Completion working-tree SHA256, LF |
| --- | --- | --- | --- | --- |
| simulation/diagnostics/per_vector_paired_design_note.md | 780e2238ff34a6fbe4df141ebf3e921be7819954329f9f570165da1c5bc2dbfa | 780e2238ff34a6fbe4df141ebf3e921be7819954329f9f570165da1c5bc2dbfa | 780e2238ff34a6fbe4df141ebf3e921be7819954329f9f570165da1c5bc2dbfa | 780e2238ff34a6fbe4df141ebf3e921be7819954329f9f570165da1c5bc2dbfa |
| simulation/attack_metrics_v2.py | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b |

## Execution metadata

HEAD: eac4f0e2799af5baeb21a49c9be7c0b581005783
Machine: YOTKOTEST
Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]
NumPy distribution version: 2.4.4
Simulation modules imported: 0. Workers launched: 0. Configured worker cap: 15. Numerical thread verification: not run because no workers were launched.
Resumed seeds: none. Tool-layer workarounds: none. Executor self-fixes: none.
Known line-ending condition: working-tree CRLF is LF-normalized for hashing; committed blobs are the evidence source.

T0 stderr warnings:
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied

Permission retry events: []
