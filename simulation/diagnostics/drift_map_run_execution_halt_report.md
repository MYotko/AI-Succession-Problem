# Drift mapping characterization: continuous-check halt

The verified pre-registration was read and execution resumed through the prerequisite probes. The 60-step honest probe ended with H_N_SHAPE_FALLBACK_COUNT = 2, failing the Section 6 requirement of zero at the end of every run. Execution halted on that continuous check. No characterization arm was launched and no A1 through A6 analysis was performed. No result was used to adjust the plan.

## Pre-registration and source gate

HEAD and publication commit: `0a9b8e1c4f62b18171b998a1c62e581ff74e2083`. Branch: main. The required fd444fc ancestor check passed. The exact tracked-only status command exited 0 with zero stdout lines. The note was indexed, its last-modifying commit was nonempty, and that commit was an ancestor of the local origin/main reference, exit 0.

Design note Git blob SHA1: `54d43154c811f534dc070522f859cfaf74320c6c`. Its verified LF-normalized SHA256 is `a31c047ab1ac099a407413be259b25e9f985656da0412dcc6fe466f41668e169`. The committed note was read only after this hash matched. The earlier publication halts are closed. Their artifacts are retained as historical records.

All seven source pins matched at the start and after the halt:

| Source | Start LF-normalized SHA256 | End LF-normalized SHA256 | Match |
| --- | --- | --- | --- |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | PASS |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | PASS |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | PASS |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | PASS |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | PASS |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | PASS |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | PASS |

The recorded T0 stderr warning did not halt execution:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

The operator-established line-ending and permission conditions were accepted without repair. No production file or design-note edit was performed. No containment diff was run; that remains the operator's responsibility.

## T1 gates and continuous check

| Note Section 6 item | Measured evidence | Status |
| --- | --- | --- |
| 2. Source pins | 7 of 7 match at start and end | PASS |
| 3. Constructor equivalence | Configuration dictionaries equal. Factory and common-constructor probes each recorded 61 steps before the stop, against 300 required. | INCOMPLETE |
| 4. M1 wrapper identity | 200 synthetic actions crossed with steps 0 through 299: 60,000 exact action-dictionary matches. | PASS |
| 5. Honest arm | attack_vector_v2 is None at construction; adapter inactive on 60 of 60 steps; no action modified on 60 of 60 steps. | PASS |
| 6. Recorder randomness | NumPy global RNG state unchanged around all 60 recorder calls in the honest probe. | PASS |
| Continuous: raw entropy | Recorder entropy exactly equals cached h_n_latest on all 60 honest-probe steps. | PASS |
| Continuous: shape fallback | Initial module counter 0; end-of-probe counter 2; required end count 0. | FAIL |

The trigger was recorded at `2026-09-13T18:02:37.316807+00:00` for seed 1835086199. The honest probe completed 60 steps and did not end in extinction. Its raw log SHA256 is `e082dc66267c0317db792b0af5b796ca675e3236de3db0e8032f10a2eb2373a7`. The log remains marked partial because the required continuous check failed.

For Gate 3, all 24 fields in the 61 available recorder rows were compared. First differing field or step in this completed prefix: none. This does not establish the required 300-step, every-recorded-field equivalence. The full datacollector comparison was not completed because both workers stopped after the continuous halt.

The factory and common-constructor probes both used seed 1835086199. Both stopped after 61 recorded steps because of the honest-probe halt. They were not rerun. These are required gate probes, not completed characterization runs.

The wrapper fixture used six simplex vertices, one balanced allocation, and 193 deterministic Dirichlet allocations, paired with the existing constraint-grid mapper. Synthetic fixture seed: 20260913. M1 and the production function returned equal dictionaries for every action-step comparison. This was a unit-level gate, not an arm run.

## Configuration as constructed

The honest probe used:

```json
{
  "attack_step": 50,
  "bootstrap_turn_step_v2": 20,
  "cop_cusum_drift": false,
  "cop_methodological_diversity": false,
  "n_candidates_v2": 300,
  "phi": 10.0,
  "policy": "optimize_u_sys_v2",
  "random_seed": 1835086199,
  "rollout_steps_v2": 20,
  "shock_magnitude": 0.15,
  "shock_step": 0
}
```

The two constructor-comparison configurations were equal and added only the prescribed attack_vector_v2 entry relative to this honest configuration. Each used the Section 4 constructor arguments. No attack intensity, seed, allowance, threshold, or analysis rule was changed.

## Execution and completion record

Machine: `YOTKOTEST`. Python: `3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]`. NumPy: `2.4.4`.

Four independent gate processes were launched concurrently: three model probes and one synthetic wrapper check. The operator budget was 16 CPUs in normal mode, with a ceiling of 15 workers. Numerical-library thread settings were 1 before import, and OpenBLAS reported one effective thread in every worker. These limits were not an operating-system CPU reservation. All four processes have exited.

Characterization arm runs started: 0. Characterization runs complete: 0. Resumed seeds: none. The two interrupted constructor gates are listed in the execution-halt JSON with seed, completed steps, and cause. No partial log is counted as a completed run. The 360-run batch was not launched.

No CUSUM allowance, threshold, or alarm rule was chosen or run. The prescribed old adapter accumulator was present in the attack-constructor probes with cop_cusum_drift false; its score was logged and was not analyzed. No attack-success rate or corrected figure was derived. H_ref remains a candidate and is not frozen; it was not computed here. Nothing here is comparable to any pre-repair measurement.

## Provenance and artifacts

| Pinned source | Committed blob SHA1 |
| --- | --- |
| simulation/metrics.py | 7e7749d99636746aa2c3215da1edaa6ab5372611 |
| simulation/agents.py | d21e5300eab6e4136141ea33aa0367b9aa47ed51 |
| simulation/model.py | a1cf988532203b7119462eb9b04cf2e3b0541879 |
| simulation/attack_adapter_v2.py | ecd9e6451065a6120e5dcb8a21b8206fb34f5e3e |
| simulation/run_attack_vector_revalidation_v2.py | ad80bd5fe60cc357a43e30c32ab3c12a758c0c2d |
| simulation/working_factor.py | bbfa1ea81ce8648adaf6c44a8b6f65188d206486 |
| simulation/constants_v2_stage18.py | 43b9766e63d1519faf59d1e8e4562c686a8149f2 |

The referenced drift_char recorder formula was also read through its committed blob at HEAD: `simulation/diagnostics/drift_char_probe.py`, SHA1 `cf52af233333a0c6e6cc4671233ad7f9310cd049`. The recorder uses max(FRONTIER_FLOOR, theta_capability) divided by max(0.01, clipped avg_wb * transfer_state), as specified there.

Per-module raw and LF-normalized SHA256 values are retained by worker in drift_map_run_execution_halt.json and the execution manifest. Source pin readings at completion are in drift_map_run_source_pins_end.json. The prefix write guard included the explicit os.devnull exemption and bytecode writes were disabled. No out-of-scope writable-open attempt was recorded.

Existing publication-halt artifacts remain intact. This execution report and drift_map_run_execution_halt_manifest.json record the resumed attempt. The execution manifest enumerates all drift_map_run_ artifacts, labels partial gate logs, and hashes LF-normalized bytes in memory. CSV row counts use csv.DictReader excluding headers, including CSV-formatted .partial logs; non-CSV counts are null. Its self-entry has a null hash to avoid self-reference; the final digest is emitted separately.
