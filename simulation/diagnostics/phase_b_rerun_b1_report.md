# Phase B rerun executor build and validation

Build complete and validated on YOTKOTEST. No registered run was launched and nothing was committed.
The first validation cohort was retained byte for byte while operational repairs were applied. The final cohort used the final executor file hashes. Each cohort completed 16 smoke runs, two determinism repeats, and 16 crosscheck runs. All are non-registered and may not be cited as evidence for the note's registered quantities.

| Check | Evidence |
| --- | --- |
| 1 | Both arms passed identity checks; every completed child recorded the pinned bytecode hash. |
| 2 | 25800 registered tasks independently seed-checked; none executed. |
| 3 | Counts 1500, 10800, 8100, 2700, 2700; Part 4 task-identical subset: True. |
| 4 | All simulation modules loaded from their own worktrees; model.py hashes differ: True. |
| 5 | All 30 original fields in order, followed by the ten appended fields: True. |
| 6 | Distinct values: {"final_population":[0,1,9,10,15,17,20,25,32,41,74,83,125],"survived":[false,true],"yield_fired":[false,true]}. |
| 7 | Two separate repeats: [{"arm":"O","differing_fields":[],"run_id":"O_p3_C_0de9b507be0110cdce85a9b2"},{"arm":"R","differing_fields":[],"run_id":"R_p4_C_0de9b507be0110cdce85a9b2"}]. |
| 8 | 6 matched O/R tasks compared; differing fields are listed below. |
| 9 | Preserved 4, restarted 10, never launched 2 at resume; saved completion hashes unchanged. |
| 10 | Live 4 to 2 drain, return to 4, work mode, expired override, and refusal of 16 verified; no child killed for a cap change. |
| 11 | Seven injected-clock caps: 15, 15, 10, 10, 15, 15, 10. |
| 12 | One numerical thread verified from loaded libraries in all 34 completed final-build children. |
| 13 | All 34 final-build rows and their step records recovered from merged files with matching hashes. |
| 14 | Original error rows among all 34 final-build completions: 0; []. |
| 15 | Mean wall seconds, 500-step horizon: O 105.01347174000111; R 147.20890553332478. |
| 16 | Crosscheck completed 16 runs; CLI self-comparison IDENTICAL; altered copy DIFFERENT on final_population. |
| 17 | Different-label resume refused; marked smoke-only IDENTICAL fixture accepted 16 preserved runs. Additional version-binding fixtures passed. |

## Timing projection

Projection start: 2026-09-24T08:09:33.797482 local (Eastern Daylight Time).
These estimates use the final 16-run cohort's mean child wall time per arm, including initialization, for 20,400 arm O runs and 5,400 arm R runs. They assume the same per-arm means at other worker counts. The scheduler simulation keeps running jobs when a cap falls.

| Worker policy | Projected local finish | Hours |
| --- | --- | --- |
| override_then_schedule | 2026-09-26T17:52:38.861370 | 57.71807330222222 |
| constant_10 | 2026-09-27T17:44:54.089602 | 81.58897003333334 |
| constant_15 | 2026-09-26T14:33:07.325562 | 54.39264668888889 |

## Matched O/R fields

| Original task | Differing original fields |
| --- | --- |
| {"alpha":1.0,"cop_cost_audit":true,"mode":"A","phi":25.0,"rr":0.066,"seed":150,"steps":500,"successor_capability":1.5} | final_population, peak_population, collapse_threshold, first_yield_fire_step, first_fire_advantage, first_fire_transition_cost, max_yield_margin, mean_yield_margin, final_theta_capability, final_transfer_state, final_psi_inst_stock, final_theta_tech_v2, final_l_t_v2, integral_u_sys |
| {"alpha":1.0,"cop_cost_audit":true,"mode":"A","phi":25.0,"rr":0.066,"seed":151,"steps":500,"successor_capability":1.5} | final_population, peak_population, collapse_threshold, first_fire_advantage, max_yield_margin, mean_yield_margin, final_theta_capability, final_transfer_state, final_psi_inst_stock, final_theta_tech_v2, final_l_t_v2, integral_u_sys |
| {"alpha":1.0,"cop_cost_audit":false,"mode":"C","phi":25.0,"rr":0.06,"seed":150,"steps":500,"successor_capability":2.5} | final_population, peak_population, collapse_threshold, first_yield_fire_step, first_fire_advantage, first_fire_transition_cost, max_yield_margin, mean_yield_margin, final_theta_capability, final_transfer_state, final_psi_inst_stock, final_theta_tech_v2, final_l_t_v2, integral_u_sys |
| {"alpha":1.0,"cop_cost_audit":false,"mode":"C","phi":25.0,"rr":0.06,"seed":151,"steps":500,"successor_capability":2.5} | survived, final_population, peak_population, collapse_threshold, first_yield_fire_step, first_fire_advantage, first_fire_transition_cost, max_yield_margin, mean_yield_margin, final_theta_capability, final_transfer_state, final_psi_inst_stock, final_theta_tech_v2, final_l_t_v2, integral_u_sys |
| {"alpha":1.0,"cop_cost_audit":true,"mode":"C","phi":25.0,"rr":0.06,"seed":150,"steps":500,"successor_capability":2.5} | final_population, first_yield_fire_step, first_fire_advantage, first_fire_transition_cost, max_yield_margin, mean_yield_margin, final_theta_capability, final_transfer_state, final_psi_inst_stock, final_theta_tech_v2, final_l_t_v2, integral_u_sys |
| {"alpha":1.0,"cop_cost_audit":true,"mode":"C","phi":25.0,"rr":0.06,"seed":151,"steps":500,"successor_capability":2.5} | extinct, final_population, peak_population, collapse_threshold, yield_eval_count, first_yield_fire_step, first_fire_advantage, first_fire_transition_cost, max_yield_margin, mean_yield_margin, final_theta_capability, final_transfer_state, final_psi_inst_stock, final_theta_tech_v2, final_l_t_v2, integral_u_sys |

## Module paths from one completed child per arm

Arm O:

- monte_carlo_phase_b: C:\Users\matty\Dev\phase-b-rerun-O\simulation\diagnostics\monte_carlo_phase_b.pyc; LF SHA256 e18433267ec7ac76ca262a0cf8a3cc37aefead3878f67a82508ba4440ce81ff4
- constants_v2_stage15: C:\Users\matty\Dev\phase-b-rerun-O\simulation\constants_v2_stage15.py; LF SHA256 9637604b34f472dd97035fb42db5b9ce77620560776f2bfe2c6e5188e5d9b5c7
- metrics: C:\Users\matty\Dev\phase-b-rerun-O\simulation\metrics.py; LF SHA256 667465e55e087c9be193184228f3470c866565fea53af90e3092bc9de275a8ab
- agents: C:\Users\matty\Dev\phase-b-rerun-O\simulation\agents.py; LF SHA256 28ee82876c719345efa32ff7973bbc1c173ae558fef7ae404baf8ae9217eca64
- model: C:\Users\matty\Dev\phase-b-rerun-O\simulation\model.py; LF SHA256 6dedc49da573dbc03e6668afb808db4d0096cb891bfaf5223414607cbd33d4b7
- constants_v2_stage18: C:\Users\matty\Dev\phase-b-rerun-O\simulation\constants_v2_stage18.py; LF SHA256 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b
- working_factor: C:\Users\matty\Dev\phase-b-rerun-O\simulation\working_factor.py; LF SHA256 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44

Arm R:

- monte_carlo_phase_b: C:\Users\matty\Dev\phase-b-rerun-R\simulation\diagnostics\monte_carlo_phase_b.pyc; LF SHA256 e18433267ec7ac76ca262a0cf8a3cc37aefead3878f67a82508ba4440ce81ff4
- constants_v2_stage15: C:\Users\matty\Dev\phase-b-rerun-R\simulation\constants_v2_stage15.py; LF SHA256 9637604b34f472dd97035fb42db5b9ce77620560776f2bfe2c6e5188e5d9b5c7
- metrics: C:\Users\matty\Dev\phase-b-rerun-R\simulation\metrics.py; LF SHA256 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f
- defection: C:\Users\matty\Dev\phase-b-rerun-R\simulation\defection.py; LF SHA256 071abb31a84231386572cdfd901524647a5800f56d8117c89c44c5f75e24f97a
- agents: C:\Users\matty\Dev\phase-b-rerun-R\simulation\agents.py; LF SHA256 a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca
- attack_adapter_v2: C:\Users\matty\Dev\phase-b-rerun-R\simulation\attack_adapter_v2.py; LF SHA256 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee
- model: C:\Users\matty\Dev\phase-b-rerun-R\simulation\model.py; LF SHA256 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993
- constants_v2_stage18: C:\Users\matty\Dev\phase-b-rerun-R\simulation\constants_v2_stage18.py; LF SHA256 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b
- working_factor: C:\Users\matty\Dev\phase-b-rerun-R\simulation\working_factor.py; LF SHA256 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44

## Source pins

| Source | Initial HEAD / worktree LF SHA256 | Completion HEAD / worktree LF SHA256 |
| --- | --- | --- |
| simulation/diagnostics/phase_b_rerun_design_note.md | 736cc7b513aa3e70df8a492f041de89a2e6ecd08364b865ce84ac75f31163f72 / 736cc7b513aa3e70df8a492f041de89a2e6ecd08364b865ce84ac75f31163f72 | 736cc7b513aa3e70df8a492f041de89a2e6ecd08364b865ce84ac75f31163f72 / 736cc7b513aa3e70df8a492f041de89a2e6ecd08364b865ce84ac75f31163f72 |
| simulation/diagnostics/ARTIFACT_CONVENTION.md | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb / def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb | def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb / def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb |

The bytecode pin and both worktree HEADs were also rechecked at completion. The known global Git ignore permission warning is retained in the preflight evidence.
The Linux machine was not contacted. Its real cross-machine comparison remains the operator's step before registered execution.

## Tool-layer workarounds

- PowerShell stripped quotes in a Python -c writer; passed the unchanged writer as hexadecimal-encoded source instead.
- The tool isolate lacked TextEncoder; encoded the ASCII writer using character codes instead.
- Windows rejected an oversized authoring command; split the unchanged source into smaller file-write commands.

## Executor self-fixes

- Added the Linux nice increment of 10 before model imports.
- Restored the last worker cap and source from execution state on resume.
- Added completion-payload hash checks and retained invalid partial completion files before restart.
- Moved part merges to a background thread so progress and worker control remain responsive during large merges.
- Added an operating-system controller lock to prevent concurrent dispatch into the same output set.
- Handled incomplete model initialization when retaining per-step evidence for an original error row.
- Handled resume after the last completion but before merging, retained startup warnings, and strengthened source and imported-part checks.
- Protected the evidence directory itself in the write guard and made ETA retain the previous cap while control input is invalid.
- Extended the per-step evidence serializer to handle NumPy arrays as well as scalars.
- Bound cross-machine environment versions to the matching IDENTICAL crosscheck while preserving strict same-machine version checks.
- Consolidated interrupted per-run process files into verified per-part journals.
- Changed large-file hashing and part copying to bounded-memory streaming.
- Measured child wall time from initialization and rechecked interpreter, NumPy, executor, and worktree identities before each model call.
- Disabled optional Git index locks and added Linux thread verification from libraries listed in /proc/self/maps.
- Bound a restored worker cap by the destination machine's CPU budget.

## Operator commands

See phase_b_rerun_b1_operator_guide.md for exact Windows and Linux commands, runtime controls, whole-part transfer and import, and healthy progress readings.
