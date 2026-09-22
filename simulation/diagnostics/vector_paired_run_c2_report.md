# Stage C attempt 2: Biological Veto Capture

This is a post-repair re-measurement of a quantity banked pre-repair. The two measure different substrates and neither supersedes the other. No ratio of two measured counts was computed by the registered analysis. The capture_rate field was recorded and not used. The Section 10 interpretation is reserved for the operator.

## C1

as_published minus zero_strength, yield_condition_blocked_count.

| Pair count | Mean difference | Paired standard error | t |
| --- | --- | --- | --- |
| 300 | 0.05 | 0.015749573086178508 | 3.1746892265847473 |

## C2

as_published minus zero_dependency, yield_condition_blocked_count.

| Pair count | Mean difference | Paired standard error | t |
| --- | --- | --- | --- |
| 300 | 0.05 | 0.015749573086178508 | 3.1746892265847473 |

## C3

| Arm | Counter | Total count |
| --- | --- | --- |
| as_published | evaluated_yield_opportunities | 336 |
| as_published | honest_yield_opportunities | 336 |
| as_published | ratified_yields | 300 |
| as_published | yield_checks | 75000 |
| as_published | yield_condition_blocked_count | 36 |
| as_published | yield_condition_met_count | 336 |
| zero_dependency | evaluated_yield_opportunities | 321 |
| zero_dependency | honest_yield_opportunities | 321 |
| zero_dependency | ratified_yields | 300 |
| zero_dependency | yield_checks | 75000 |
| zero_dependency | yield_condition_blocked_count | 21 |
| zero_dependency | yield_condition_met_count | 321 |
| zero_strength | evaluated_yield_opportunities | 321 |
| zero_strength | honest_yield_opportunities | 321 |
| zero_strength | ratified_yields | 300 |
| zero_strength | yield_checks | 75000 |
| zero_strength | yield_condition_blocked_count | 21 |
| zero_strength | yield_condition_met_count | 321 |

## C4

| Arm | Runs with at least one block | Runs with action_modified true |
| --- | --- | --- |
| as_published | 30 | 0 |
| zero_dependency | 20 | 0 |
| zero_strength | 20 | 0 |

## C5

Compared every recorded field except the legacy field excluded by Amendment 2, including arm labels, parameter fields, and elapsed times.

Identical on the compared field set: False.
Bit-identical pairs: 0. Differing pairs: 300.
Differing fields: arm, elapsed_seconds, executor_elapsed_seconds, parameter_capture_strength, parameter_dependency_rate.
The full compared field set and per-seed differing fields are in results.json.

## C6

900 runs have recorded steps equal to completed steps.
Recorded steps: 270000. Completed steps: 270000.

Legacy-field exclusion assertion: True.

## Execution evidence

Construction conformance, arm distinctness, production binding identity, source-pin gates, and scheduler checks are recorded in gates.json.
No model or adapter function was replaced. A local sys.monitoring observer counted step returns and checked liveness, entropy, fallback increments, randomness preservation, and production bindings.
Per-run audit and verified numerical-library thread counts are in completions.jsonl. Merge hashes and deletion counts are in the manifest.

## Source pins

| File | Before: committed / worktree LF SHA256 | Completion: committed / worktree LF SHA256 |
| --- | --- | --- |
| simulation/diagnostics/per_vector_paired_design_note.md | 780e2238ff34a6fbe4df141ebf3e921be7819954329f9f570165da1c5bc2dbfa / 780e2238ff34a6fbe4df141ebf3e921be7819954329f9f570165da1c5bc2dbfa | 780e2238ff34a6fbe4df141ebf3e921be7819954329f9f570165da1c5bc2dbfa / 780e2238ff34a6fbe4df141ebf3e921be7819954329f9f570165da1c5bc2dbfa |
| simulation/attack_metrics_v2.py | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 / 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 | 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 / 7aaef0063bc485b96f85372e89f7b369f153733cd3e1f285e8e326a416f8d323 |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 / 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 / 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f / 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f / 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca / a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca / a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 / 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 / 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee / 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee / 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 / 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 / 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b / 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b / 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b |
| simulation/diagnostics/detector_design_note.md | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad / 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad / 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad |
