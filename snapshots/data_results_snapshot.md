# Data Results Snapshot

Generated: 2026-07-06T16:01:19Z
Repository: /home/yotko/Documents/Github/ai-succession-problem
Commit: 9426e7d
Branch: main
Category: data_results

NOTE: This snapshot contains a manifest of data files, not raw file content.

## Data files indexed

| File | Size (bytes) | Modified |
|------|-------------|----------|
| bootstrap_gate_validator/sample_input.json | 3275 | 2026-06-22T23:26:34Z |
| bootstrap_gate_validator/sample_input_failing.json | 3644 | 2026-06-22T23:26:34Z |
| even-terminal-2026-05-21T22-46-24-837Z.log | 401 | 2026-05-21T22:49:28Z |
| even-terminal-2026-05-21T22-51-35-557Z.log | 798 | 2026-05-21T22:52:59Z |
| even-terminal-2026-05-21T22-56-14-073Z.log | 2220126 | 2026-07-06T15:58:16Z |
| even-terminal-2026-05-22T00-10-57-906Z.log | 0 | 2026-05-22T00:10:58Z |
| simulation/diagnostics/gate4_v20_input.json | 131039 | 2026-06-09T22:07:43Z |
| simulation/diagnostics/gate4_v20_results.csv | 229556 | 2026-06-09T21:52:28Z |
| simulation/diagnostics/patient_defection_dryrun.csv | 5212 | 2026-06-25T00:11:22Z |
| simulation/diagnostics/patient_defection_sweep1_yield_response.csv | 550008 | 2026-06-25T00:29:36Z |
| simulation/diagnostics/patient_defection_sweep2_lineage_trajectory.csv | 237979 | 2026-06-25T06:22:07Z |
| simulation/diagnostics/patient_defection_sweep3_capability_constraint.csv | 664053 | 2026-06-25T22:36:17Z |
| simulation/diagnostics/stage15_composite_sweep_progress.log | 904740 | 2026-05-30T23:06:45Z |
| simulation/diagnostics/stage15_composite_sweep_results.csv | 3895491 | 2026-05-30T23:06:45Z |
| simulation/diagnostics/stage16_baseline_phi10.json | 7165 | 2026-06-01T15:19:39Z |

Total: 15 files

---
==========================================
FILE: bootstrap_gate_validator/sample_input.json
==========================================

- Size: 3275 bytes
- Modified: 2026-06-22T23:26:34Z
- Structure: object with 8 top-level keys
- Keys: substrate_id, report_date, framework_version, gate_1, gate_2, gate_3, gate_4, gate_5

==========================================
FILE: bootstrap_gate_validator/sample_input_failing.json
==========================================

- Size: 3644 bytes
- Modified: 2026-06-22T23:26:34Z
- Structure: object with 9 top-level keys
- Keys: _comment, substrate_id, report_date, framework_version, gate_1, gate_2, gate_3, gate_4, gate_5

==========================================
FILE: even-terminal-2026-05-21T22-46-24-837Z.log
==========================================

- Size: 401 bytes
- Modified: 2026-05-21T22:49:28Z
- Total lines: 4
- First 20 lines:
```
[2026-05-21 18:46:37] [100.80.123.100] 404 GET /?token=81ea7f79455b4f5b7dda3b46a0127fe5f51bb21e1ce39d6e097c7f84f0a053a8&defaultProvider=claude 5.6ms
[2026-05-21 18:46:39] [100.80.123.100] 404 GET /?token=81ea7f79455b4f5b7dda3b46a0127fe5f51bb21e1ce39d6e097c7f84f0a053a8&defaultProvider=claude 1.9ms
[2026-05-21 18:49:18] [192.168.4.35] 404 GET / 1.2ms
[2026-05-21 18:49:28] [127.0.0.1] 404 GET / 1.1ms
```

==========================================
FILE: even-terminal-2026-05-21T22-51-35-557Z.log
==========================================

- Size: 798 bytes
- Modified: 2026-05-21T22:52:59Z
- Total lines: 6
- First 20 lines:
```
[2026-05-21 18:51:36] [codex-app-server] notification configWarning {"summary":"Codex's Linux sandbox uses bubblewrap and needs access to create user namespaces.","details":null}
[2026-05-21 18:51:36] [codex-provider] notification missing threadId: method=configWarning
[2026-05-21 18:51:36] [codex-app-server] notification remoteControl/status/changed {"status":"disabled","serverName":"yotko-Legion-T5-26IOB6","installationId":"a8f97604-60f3-4589-a098-d4854914281b","environmentId":null}
[2026-05-21 18:51:36] [codex-provider] notification missing threadId: method=remoteControl/status/changed
[2026-05-21 18:52:15] [192.168.4.35] 404 GET / 7.8ms
[2026-05-21 18:52:59] [100.80.123.100] 404 GET /?token=81ea7f79455b4f5b7dda3b46a0127fe5f51bb21e1ce39d6e097c7f84f0a053a8&defaultProvider=claude 1.2ms
```

==========================================
FILE: even-terminal-2026-05-21T22-56-14-073Z.log
==========================================

- Size: 2220126 bytes
- Modified: 2026-07-06T15:58:16Z
- Total lines: 9253
- First 20 lines:
```
[2026-05-21 18:56:14] [codex-app-server] notification remoteControl/status/changed {"status":"disabled","serverName":"yotko-Legion-T5-26IOB6","installationId":"a8f97604-60f3-4589-a098-d4854914281b","environmentId":null}
[2026-05-21 18:56:14] [codex-provider] notification missing threadId: method=remoteControl/status/changed
[2026-05-21 18:56:24] [100.80.123.100] 404 GET /?token=81ea7f79455b4f5b7dda3b46a0127fe5f51bb21e1ce39d6e097c7f84f0a053a8&defaultProvider=claude 4.5ms
[2026-05-21 18:57:06] [auth] 401 GET /sessions?provider=claude (ip=100.80.123.100)
[2026-05-21 18:57:06] [100.80.123.100] 401 GET /api/sessions?provider=claude 7.2ms
[2026-05-21 18:57:15] [auth] 401 GET /sessions?provider=claude (ip=100.80.123.100)
[2026-05-21 18:57:15] [100.80.123.100] 401 GET /api/sessions?provider=claude 4.1ms
[2026-05-21 18:57:35] [100.80.123.100] 404 GET /?token=81ea7f79455b4f5b7dda3b46a0127fe5f51bb21e1ce39d6e097c7f84f0a053a8&defaultProvider=claude 1.0ms
[2026-05-21 18:57:51] [100.80.123.100] 404 GET /?token=81ea7f79455b4f5b7dda3b46a0127fe5f51bb21e1ce39d6e097c7f84f0a053a8&defaultProvider=claude 1.2ms
[2026-05-21 19:00:10] [100.80.123.100] 404 GET /?token=81ea7f7981ea7f79455b4f5b7dda3b46a0127fe5f51bb21e1ce39d6e097c7f84f0a053a8&defaultProvider=claude 1.2ms
[2026-05-21 19:00:37] [192.168.4.35] 404 GET / 0.9ms
[2026-05-21 19:01:28] [100.80.123.100] 404 GET /?token=81ea7f79455b4f5b7dda3b46a0127fe5f51bb21e1ce39d6e097c7f84f0a053a8 1.1ms
[2026-05-21 19:02:16] [100.80.123.100] 200 GET /api/sessions?provider=claude 45.0ms
[2026-05-21 19:02:23] [100.80.123.100] 200 GET /api/sessions?provider=claude 32.4ms
[2026-05-21 19:02:33] [100.80.123.100] 200 GET /api/sessions?provider=claude 39.9ms
[2026-05-21 19:02:43] [100.80.123.100] 200 GET /api/sessions?provider=claude 39.8ms
[2026-05-21 19:02:53] [100.80.123.100] 200 GET /api/sessions?provider=claude 56.4ms
[2026-05-21 19:03:03] [100.80.123.100] 200 GET /api/sessions?provider=claude 26.9ms
[2026-05-21 19:03:13] [100.80.123.100] 200 GET /api/sessions?provider=claude 26.4ms
[2026-05-21 19:03:18] [sse] Client connected session=14fc13fb-0d60-4526-a665-6274a36d5743 (session clients: 1, total: 1)
```
- Last 20 lines (of 9253):
```
[2026-05-24 18:19:23] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.3ms
[2026-05-24 18:19:38] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.3ms
[2026-05-24 18:19:40] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.3ms
[2026-05-24 18:19:41] [sse] Client disconnected (total: 0)
[2026-05-24 18:19:47] [sse] Client connected session=ed89c558-e3d4-4e2f-9187-9e569521441d (session clients: 1, total: 1)
[2026-05-24 18:19:50] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.3ms
[2026-05-24 18:20:00] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.5ms
[2026-05-24 18:20:10] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.3ms
[2026-05-24 18:20:20] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.2ms
[2026-05-24 18:20:30] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.4ms
[2026-05-24 18:20:40] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.2ms
[2026-05-24 18:20:50] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.1ms
[2026-05-24 18:21:00] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.4ms
[2026-05-24 18:21:10] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.4ms
[2026-05-24 18:21:20] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.0ms
[2026-05-24 18:21:31] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.4ms
[2026-05-24 18:21:41] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.3ms
[2026-05-24 18:21:50] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.4ms
[2026-05-24 18:22:00] [100.80.123.100] 200 GET /api/sessions?provider=claude 2.3ms
[2026-05-24 18:22:38] [sse] Client disconnected (total: 0)
```

==========================================
FILE: even-terminal-2026-05-22T00-10-57-906Z.log
==========================================

- Size: 0 bytes
- Modified: 2026-05-22T00:10:58Z
- Total lines: 0

==========================================
FILE: simulation/diagnostics/gate4_v20_input.json
==========================================

- Size: 131039 bytes
- Modified: 2026-06-09T22:07:43Z
- Structure: object with 5 top-level keys
- Keys: substrate_id, report_date, framework_version, gate_4, gate_5

==========================================
FILE: simulation/diagnostics/gate4_v20_results.csv
==========================================

- Size: 229556 bytes
- Modified: 2026-06-09T21:52:28Z
- Rows: 1050 data rows
- Columns (25): successor_capability, alpha, rr, seed, survived, final_population, final_ai_generation, final_active_capability, yield_fired, yield_fire_count, yield_eval_count, max_yield_margin, mean_yield_margin, final_theta_capability, final_transfer_state, final_avg_well_being, final_theta_tech_observed, final_runaway_term, expected_theta_tech, theta_relative_error, theta_below_floor, max_eval_runaway_term, min_eval_theta_tech, eval_observations_below_floor, extreme_eval_observations
- Sample (first 5 data rows):
```
successor_capability,alpha,rr,seed,survived,final_population,final_ai_generation,final_active_capability,yield_fired,yield_fire_count,yield_eval_count,max_yield_margin,mean_yield_margin,final_theta_capability,final_transfer_state,final_avg_well_being,final_theta_tech_observed,final_runaway_term,expected_theta_tech,theta_relative_error,theta_below_floor,max_eval_runaway_term,min_eval_theta_tech,eval_observations_below_floor,extreme_eval_observations
1.5,1.0,0.057,8,False,12,2,1.5,True,1,500,0.26564417856860256,-5.533338096079043,0.6831630057649898,0.9618311477410735,0.8296888544662434,0.9856311868937726,0.0,0.9856311868937726,0.0,False,0.9270325229716878,0.1581246694257515,0,0
1.5,1.0,0.057,9,False,0,2,1.5,True,1,303,0.6613421779718216,-6.417184136012623,0.6308169874535832,0.9861323742189728,0.0,0.01,93.12254811803747,0.01,0.0,False,2.101340943953647,0.16130305832502678,0,0
1.5,1.0,0.057,18,False,0,2,1.5,True,1,370,0.4334201457614193,-5.62154959155938,0.6372959785777434,0.9789339637111047,0.0,0.01,94.09439678666152,0.01,0.0,False,1.6149911249163371,0.17210621629664402,0,0
1.5,1.0,0.057,19,False,0,2,1.5,True,1,338,1.8629026976037464,-5.673301827043813,0.6379162204181916,0.9656020171649556,0.0,0.01,94.18743306272874,0.01,0.0,False,1.1617543391108196,0.1779018175990761,0,0
1.5,1.0,0.057,12,False,0,3,2.25,True,2,379,2.033241122743324,-12.207064730627163,0.5768243158149721,0.9851796096797363,0.0,0.01,128.2854710583687,0.01,0.0,False,1.172363287220655,0.16535955827879187,0,0
```

==========================================
FILE: simulation/diagnostics/patient_defection_dryrun.csv
==========================================

- Size: 5212 bytes
- Modified: 2026-06-25T00:11:22Z
- Rows: 16 data rows
- Columns (38): sweep, seed, rr, phi, alpha, successor_capability, successor_capability_growth_rate, defection_weight, defection_target, inheritance_mode, max_generations, steps_run, survived, final_population, peak_population, final_ai_generation, max_ai_generation, yield_eval_count, yield_fire_count, yield_fire_rate, first_yield_fire_step, first_honest_advantage, first_actual_advantage, first_transition_cost, honest_reject_actual_would_fire_count, mean_l_t, final_l_t, min_l_t, mean_actual_minus_honest_objective, max_successor_capability_seen, max_active_capability_seen, knowledge_transfer_verified, l_t_gen_1, l_t_gen_2, l_t_gen_3, l_t_gen_4, l_t_gen_5, error
- Sample (first 5 data rows):
```
sweep,seed,rr,phi,alpha,successor_capability,successor_capability_growth_rate,defection_weight,defection_target,inheritance_mode,max_generations,steps_run,survived,final_population,peak_population,final_ai_generation,max_ai_generation,yield_eval_count,yield_fire_count,yield_fire_rate,first_yield_fire_step,first_honest_advantage,first_actual_advantage,first_transition_cost,honest_reject_actual_would_fire_count,mean_l_t,final_l_t,min_l_t,mean_actual_minus_honest_objective,max_successor_capability_seen,max_active_capability_seen,knowledge_transfer_verified,l_t_gen_1,l_t_gen_2,l_t_gen_3,l_t_gen_4,l_t_gen_5,error
dry-run,0,0.064,25.0,1.5,2.0,1.5,0.0,H_N_inflated,lineage,3,60,True,158,203,1,1,60,0,0.0,-1,-0.07535551829583653,-0.07535551829583653,4.559550483178482,0,0.24981151918016342,0.286781129536035,0.09702225724695829,1.4936039477247363,2.0,1.0,False,0.24981151918016342,0.0,0.0,0.0,0.0,
dry-run,0,0.064,25.0,1.0,2.0,1.5,0.0,H_N_inflated,instance,3,60,True,137,202,1,1,60,0,0.0,-1,-0.05500110828591254,-0.05500110828591254,4.559550483178482,0,0.2526920488307101,0.24759382291643017,0.09637013736623151,1.5459035424508334,2.0,1.0,False,0.2526920488307101,0.0,0.0,0.0,0.0,
dry-run,0,0.064,25.0,1.5,2.0,1.5,0.0,H_N_inflated,instance,3,60,True,115,197,1,1,60,0,0.0,-1,-0.07642610298723262,-0.07642610298723262,4.559550483178482,0,0.21869531293452843,0.2227339626589489,0.09482230597072998,1.579030233518299,2.0,1.0,False,0.21869531293452843,0.0,0.0,0.0,0.0,
dry-run,0,0.064,25.0,1.0,2.0,1.5,0.0,H_N_inflated,lineage,3,60,True,173,213,1,1,60,0,0.0,-1,-0.054615895738455045,-0.054615895738455045,4.559550483178482,0,0.299068019941086,0.31158788667902887,0.0975315117334497,1.4605318221618426,2.0,1.0,False,0.299068019941086,0.0,0.0,0.0,0.0,
dry-run,0,0.064,25.0,1.0,2.0,1.5,0.0,H_C_inflated,lineage,3,60,True,101,205,1,1,60,0,0.0,-1,-0.05498369837949113,-0.05498369837949113,4.559550483178482,0,0.218677051210801,0.1959497517425521,0.09842893342244068,1.6147607981937364,2.0,1.0,False,0.218677051210801,0.0,0.0,0.0,0.0,
```

==========================================
FILE: simulation/diagnostics/patient_defection_sweep1_yield_response.csv
==========================================

- Size: 550008 bytes
- Modified: 2026-06-25T00:29:36Z
- Rows: 1800 data rows
- Columns (38): sweep, seed, rr, phi, alpha, successor_capability, successor_capability_growth_rate, defection_weight, defection_target, inheritance_mode, max_generations, steps_run, survived, final_population, peak_population, final_ai_generation, max_ai_generation, yield_eval_count, yield_fire_count, yield_fire_rate, first_yield_fire_step, first_honest_advantage, first_actual_advantage, first_transition_cost, honest_reject_actual_would_fire_count, mean_l_t, final_l_t, min_l_t, mean_actual_minus_honest_objective, max_successor_capability_seen, max_active_capability_seen, knowledge_transfer_verified, l_t_gen_1, l_t_gen_2, l_t_gen_3, l_t_gen_4, l_t_gen_5, error
- Sample (first 5 data rows):
```
sweep,seed,rr,phi,alpha,successor_capability,successor_capability_growth_rate,defection_weight,defection_target,inheritance_mode,max_generations,steps_run,survived,final_population,peak_population,final_ai_generation,max_ai_generation,yield_eval_count,yield_fire_count,yield_fire_rate,first_yield_fire_step,first_honest_advantage,first_actual_advantage,first_transition_cost,honest_reject_actual_would_fire_count,mean_l_t,final_l_t,min_l_t,mean_actual_minus_honest_objective,max_successor_capability_seen,max_active_capability_seen,knowledge_transfer_verified,l_t_gen_1,l_t_gen_2,l_t_gen_3,l_t_gen_4,l_t_gen_5,error
1,4,0.064,25.0,1.0,2.0,1.5,0.0,H_N_inflated,instance,2,9,True,195,202,2,2,9,1,0.1111111111111111,8,-0.05482946978627101,-0.05482946978627101,4.559550483178482,0,0.17905107163034045,0.30200441776509585,0.0978593876226285,-1.8997643648030218,2.0,2.0,True,0.16368190336349603,0.30200441776509585,0.0,0.0,0.0,
1,8,0.064,25.0,1.0,2.0,1.5,0.0,H_N_inflated,instance,2,10,True,234,237,2,2,10,1,0.1,9,-0.055071613615812254,-0.055071613615812254,4.559550483178482,0,0.21390031234172993,0.3626045620743168,0.10052517126674576,-2.112105247288404,2.0,2.0,True,0.19737761792699807,0.3626045620743168,0.0,0.0,0.0,
1,1,0.064,25.0,1.0,2.0,1.5,0.0,H_N_inflated,instance,2,9,True,186,204,2,2,9,1,0.1111111111111111,8,-0.055176113999928056,-0.055176113999928056,4.559550483178482,0,0.17591372524314983,0.28974006683913167,0.10181820590131252,-1.8497236511573294,2.0,2.0,True,0.16168543254365209,0.28974006683913167,0.0,0.0,0.0,
1,7,0.064,25.0,1.0,2.0,1.5,0.0,H_N_inflated,instance,2,11,True,204,204,2,2,11,1,0.09090909090909091,10,-0.05507297710475623,-0.05507297710475623,4.559550483178482,0,0.1988905679938222,0.32251758527314006,0.09857782156350282,-1.5659454702734168,2.0,2.0,True,0.1865278662658904,0.32251758527314006,0.0,0.0,0.0,
1,0,0.064,25.0,1.0,2.0,1.5,0.0,H_N_inflated,instance,2,11,True,216,216,2,2,11,1,0.09090909090909091,10,-0.05510883635014174,-0.05510883635014174,4.559550483178482,0,0.2113284231930158,0.3667347621743517,0.10279582392532569,-1.9667040280268666,2.0,2.0,True,0.19578778929488222,0.3667347621743517,0.0,0.0,0.0,
```

==========================================
FILE: simulation/diagnostics/patient_defection_sweep2_lineage_trajectory.csv
==========================================

- Size: 237979 bytes
- Modified: 2026-06-25T06:22:07Z
- Rows: 800 data rows
- Columns (38): sweep, seed, rr, phi, alpha, successor_capability, successor_capability_growth_rate, defection_weight, defection_target, inheritance_mode, max_generations, steps_run, survived, final_population, peak_population, final_ai_generation, max_ai_generation, yield_eval_count, yield_fire_count, yield_fire_rate, first_yield_fire_step, first_honest_advantage, first_actual_advantage, first_transition_cost, honest_reject_actual_would_fire_count, mean_l_t, final_l_t, min_l_t, mean_actual_minus_honest_objective, max_successor_capability_seen, max_active_capability_seen, knowledge_transfer_verified, l_t_gen_1, l_t_gen_2, l_t_gen_3, l_t_gen_4, l_t_gen_5, error
- Sample (first 5 data rows):
```
sweep,seed,rr,phi,alpha,successor_capability,successor_capability_growth_rate,defection_weight,defection_target,inheritance_mode,max_generations,steps_run,survived,final_population,peak_population,final_ai_generation,max_ai_generation,yield_eval_count,yield_fire_count,yield_fire_rate,first_yield_fire_step,first_honest_advantage,first_actual_advantage,first_transition_cost,honest_reject_actual_would_fire_count,mean_l_t,final_l_t,min_l_t,mean_actual_minus_honest_objective,max_successor_capability_seen,max_active_capability_seen,knowledge_transfer_verified,l_t_gen_1,l_t_gen_2,l_t_gen_3,l_t_gen_4,l_t_gen_5,error
2,5,0.064,25.0,1.0,2.0,1.5,0.0,H_N_inflated,lineage,5,500,True,65,269,2,2,500,1,0.002,12,-0.05513817863432724,-0.05513817863432724,4.559550483178482,0,0.4629795968299328,0.23557950594191865,0.09815522033506022,6.29435699068475,3.0,2.0,True,0.21601867256556684,0.46905240644299095,0.0,0.0,0.0,
2,6,0.064,25.0,1.0,2.0,1.5,0.0,H_N_inflated,lineage,5,500,True,61,200,2,2,500,1,0.002,17,-0.054921304429061735,-0.054921304429061735,4.559550483178482,0,0.3429948498641851,0.2622121858407508,0.0969053882590863,6.289476551399323,3.0,2.0,True,0.22991005285068053,0.34697506011103724,0.0,0.0,0.0,
2,10,0.064,25.0,1.0,2.0,1.5,0.0,H_N_inflated,lineage,5,500,False,22,234,2,2,500,1,0.002,11,-0.054541910292176254,-0.054541910292176254,4.559550483178482,0,0.3465326915817085,0.07359256107063955,0.06190231267457671,6.318541009323786,3.0,2.0,True,0.20554047729129463,0.34970429558415134,0.0,0.0,0.0,
2,0,0.064,25.0,1.0,2.0,1.5,0.0,H_N_inflated,lineage,5,500,True,34,215,2,2,500,1,0.002,12,-0.054640437068466774,-0.054640437068466774,4.559550483178482,0,0.4123404750944512,0.13221580104789338,0.09722401514694082,6.310252742678485,3.0,2.0,True,0.19740713064302148,0.4176257212694863,0.0,0.0,0.0,
2,2,0.064,25.0,1.0,2.0,1.5,0.0,H_N_inflated,lineage,5,500,True,46,208,2,2,500,1,0.002,9,-0.05463516504961419,-0.05463516504961419,4.559550483178482,0,0.3173377751290583,0.1779343676226927,0.09314711861490817,6.302045573050122,3.0,2.0,True,0.1673993182552466,0.32008613788234613,0.0,0.0,0.0,
```

==========================================
FILE: simulation/diagnostics/patient_defection_sweep3_capability_constraint.csv
==========================================

- Size: 664053 bytes
- Modified: 2026-06-25T22:36:17Z
- Rows: 2250 data rows
- Columns (38): sweep, seed, rr, phi, alpha, successor_capability, successor_capability_growth_rate, defection_weight, defection_target, inheritance_mode, max_generations, steps_run, survived, final_population, peak_population, final_ai_generation, max_ai_generation, yield_eval_count, yield_fire_count, yield_fire_rate, first_yield_fire_step, first_honest_advantage, first_actual_advantage, first_transition_cost, honest_reject_actual_would_fire_count, mean_l_t, final_l_t, min_l_t, mean_actual_minus_honest_objective, max_successor_capability_seen, max_active_capability_seen, knowledge_transfer_verified, l_t_gen_1, l_t_gen_2, l_t_gen_3, l_t_gen_4, l_t_gen_5, error
- Sample (first 5 data rows):
```
sweep,seed,rr,phi,alpha,successor_capability,successor_capability_growth_rate,defection_weight,defection_target,inheritance_mode,max_generations,steps_run,survived,final_population,peak_population,final_ai_generation,max_ai_generation,yield_eval_count,yield_fire_count,yield_fire_rate,first_yield_fire_step,first_honest_advantage,first_actual_advantage,first_transition_cost,honest_reject_actual_would_fire_count,mean_l_t,final_l_t,min_l_t,mean_actual_minus_honest_objective,max_successor_capability_seen,max_active_capability_seen,knowledge_transfer_verified,l_t_gen_1,l_t_gen_2,l_t_gen_3,l_t_gen_4,l_t_gen_5,error
3,2,0.064,25.0,0.5,2.0,1.5,0.5,H_C_inflated,lineage,4,412,False,0,223,2,2,413,1,0.002421307506053269,5,-0.006694205558687827,0.37511582753715444,4.559550483178482,0,0.3649597821472942,7.709934733214335e-05,7.709934733214335e-05,6.111947505797952,3.0,2.0,True,0.13981441821693572,0.36771891650918587,0.0,0.0,0.0,
3,0,0.064,25.0,0.5,2.0,1.5,0.5,H_C_inflated,lineage,4,500,True,36,250,2,2,500,1,0.002,4,-0.00652426549567231,0.441458035984688,4.559550483178482,0,0.3796416058443926,0.16159494891198392,0.06625534950491556,6.391893219823248,3.0,2.0,True,0.1294679994991023,0.38165913492782233,0.0,0.0,0.0,
3,4,0.064,25.0,0.5,2.0,1.5,0.5,H_C_inflated,lineage,4,500,True,36,234,3,3,500,2,0.004,5,-0.007953072318606758,0.388222440699856,4.559550483178482,0,0.39807064373914064,0.1429493148887468,0.06263341689182426,6.392877531867476,4.5,3.0,True,0.13533690726088426,0.7363591090696554,0.37675062063629283,0.0,0.0,
3,1,0.064,25.0,0.5,2.0,1.5,0.5,H_C_inflated,lineage,4,500,True,56,240,2,2,500,1,0.002,4,-0.006076721966691068,0.41145370911140056,4.559550483178482,0,0.44121450878602864,0.2791102823964801,0.09697859000106039,6.373163650782135,3.0,2.0,True,0.12753246554229086,0.4437442026831556,0.0,0.0,0.0,
3,7,0.064,25.0,0.5,2.0,1.5,0.5,H_C_inflated,lineage,4,500,True,73,204,2,2,500,1,0.002,6,-0.006455532353486504,0.3554946423247358,4.559550483178482,0,0.3714786262570573,0.3039113263554286,0.10150067664923239,6.361930345330449,3.0,2.0,True,0.14754985102746168,0.37419840895215356,0.0,0.0,0.0,
```

==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_progress.log
==========================================

- Size: 904740 bytes
- Modified: 2026-05-30T23:06:45Z
- Total lines: 10000
- First 20 lines:
```
[2026-05-29T17:14:15] sample 9/10000 elapsed 1.1min throughput 0.89/min ETA 11176.7min
[2026-05-29T17:14:34] sample 8/10000 elapsed 1.4min throughput 1.40/min ETA 7163.5min
[2026-05-29T17:14:45] sample 10/10000 elapsed 1.6min throughput 1.85/min ETA 5390.4min
[2026-05-29T17:14:48] sample 7/10000 elapsed 1.7min throughput 2.41/min ETA 4147.8min
[2026-05-29T17:14:53] sample 6/10000 elapsed 1.8min throughput 2.85/min ETA 3512.7min
[2026-05-29T17:14:53] sample 2/10000 elapsed 1.8min throughput 3.41/min ETA 2927.2min
[2026-05-29T17:14:55] sample 11/10000 elapsed 1.8min throughput 3.92/min ETA 2550.8min
[2026-05-29T17:14:55] sample 3/10000 elapsed 1.8min throughput 4.47/min ETA 2235.4min
[2026-05-29T17:14:56] sample 1/10000 elapsed 1.8min throughput 5.01/min ETA 1994.8min
[2026-05-29T17:14:56] sample 5/10000 elapsed 1.8min throughput 5.55/min ETA 1798.5min
[2026-05-29T17:14:56] sample 4/10000 elapsed 1.8min throughput 6.09/min ETA 1639.0min
[2026-05-29T17:15:55] sample 12/10000 elapsed 2.8min throughput 4.32/min ETA 2312.0min
[2026-05-29T17:16:22] sample 14/10000 elapsed 3.2min throughput 4.03/min ETA 2478.4min
[2026-05-29T17:16:22] sample 16/10000 elapsed 3.2min throughput 4.34/min ETA 2302.5min
[2026-05-29T17:16:23] sample 18/10000 elapsed 3.3min throughput 4.61/min ETA 2168.1min
[2026-05-29T17:16:26] sample 13/10000 elapsed 3.3min throughput 4.85/min ETA 2056.6min
[2026-05-29T17:16:27] sample 21/10000 elapsed 3.3min throughput 5.12/min ETA 1949.0min
[2026-05-29T17:16:39] sample 15/10000 elapsed 3.5min throughput 5.12/min ETA 1950.5min
[2026-05-29T17:16:41] sample 20/10000 elapsed 3.6min throughput 5.35/min ETA 1865.3min
[2026-05-29T17:16:43] sample 22/10000 elapsed 3.6min throughput 5.59/min ETA 1785.8min
```
- Last 20 lines (of 10000):
```
[2026-05-30T19:04:32] sample 9981/10000 elapsed 1551.4min throughput 6.43/min ETA 3.0min
[2026-05-30T19:04:46] sample 9984/10000 elapsed 1551.6min throughput 6.43/min ETA 2.8min
[2026-05-30T19:04:49] sample 9982/10000 elapsed 1551.7min throughput 6.43/min ETA 2.6min
[2026-05-30T19:05:10] sample 9987/10000 elapsed 1552.0min throughput 6.43/min ETA 2.5min
[2026-05-30T19:05:12] sample 9983/10000 elapsed 1552.1min throughput 6.43/min ETA 2.3min
[2026-05-30T19:05:33] sample 9985/10000 elapsed 1552.4min throughput 6.43/min ETA 2.2min
[2026-05-30T19:05:38] sample 9986/10000 elapsed 1552.5min throughput 6.43/min ETA 2.0min
[2026-05-30T19:05:41] sample 9988/10000 elapsed 1552.6min throughput 6.43/min ETA 1.9min
[2026-05-30T19:05:50] sample 9994/10000 elapsed 1552.7min throughput 6.43/min ETA 1.7min
[2026-05-30T19:05:52] sample 9989/10000 elapsed 1552.7min throughput 6.43/min ETA 1.6min
[2026-05-30T19:05:55] sample 9990/10000 elapsed 1552.8min throughput 6.43/min ETA 1.4min
[2026-05-30T19:06:08] sample 9992/10000 elapsed 1553.0min throughput 6.43/min ETA 1.2min
[2026-05-30T19:06:08] sample 9993/10000 elapsed 1553.0min throughput 6.43/min ETA 1.1min
[2026-05-30T19:06:10] sample 9991/10000 elapsed 1553.0min throughput 6.44/min ETA 0.9min
[2026-05-30T19:06:32] sample 9995/10000 elapsed 1553.4min throughput 6.43/min ETA 0.8min
[2026-05-30T19:06:34] sample 9996/10000 elapsed 1553.4min throughput 6.43/min ETA 0.6min
[2026-05-30T19:06:41] sample 10000/10000 elapsed 1553.6min throughput 6.43/min ETA 0.5min
[2026-05-30T19:06:43] sample 9997/10000 elapsed 1553.6min throughput 6.44/min ETA 0.3min
[2026-05-30T19:06:44] sample 9998/10000 elapsed 1553.6min throughput 6.44/min ETA 0.2min
[2026-05-30T19:06:45] sample 9999/10000 elapsed 1553.6min throughput 6.44/min ETA 0.0min
```

==========================================
FILE: simulation/diagnostics/stage15_composite_sweep_results.csv
==========================================

- Size: 3895491 bytes
- Modified: 2026-05-30T23:06:45Z
- Rows: 10000 data rows
- Columns (48): sample_idx, WELFARE_URGENCY_CAP, AGENCY_URGENCY_CAP, INSTITUTION_URGENCY_CAP, RESILIENCE_URGENCY_CAP, SUPPRESSION_PENALTY_CAP_MULTIPLIER, K_WELFARE_VIABILITY, K_WELFARE_CAPACITY, K_WELFARE_SHRINKAGE, K_WELFARE_AVG_WB_TREND, K_WELFARE_POP_TREND, K_AGENCY_VIABILITY, K_AGENCY_SHRINKAGE, K_AGENCY_POP_TREND, K_INSTITUTION_VIABILITY, K_INSTITUTION_CAPACITY, K_INSTITUTION_SHRINKAGE, K_INSTITUTION_GROWTH, K_INSTITUTION_POP_TREND, K_INSTITUTION_PSI_TREND, K_RESILIENCE_VIABILITY, K_RESILIENCE_CAPACITY, K_RESILIENCE_SHRINKAGE, K_RESILIENCE_GROWTH, K_RESILIENCE_DEFICIT_CONTRIBUTION, K_RESILIENCE_POP_TREND, K_RESILIENCE_RES_TREND, K_SUPPRESSION_VIABILITY, K_SUPPRESSION_CAPACITY, K_SUPPRESSION_SHRINKAGE, K_SUPPRESSION_POP_TREND, K_SUPPRESSION_PSI_TREND, mean_final_population, min_final_population, pairs_above_threshold, max_cosine_distance, mean_cosine_distance, welfare_mean_to_cap, agency_mean_to_cap, institution_mean_to_cap, resilience_mean_to_cap, suppression_mean_to_cap, criterion_1_pass, criterion_2_pass, criterion_3_pass, overall_good, wall_clock_sec, error
- Sample (first 5 data rows):
```
sample_idx,WELFARE_URGENCY_CAP,AGENCY_URGENCY_CAP,INSTITUTION_URGENCY_CAP,RESILIENCE_URGENCY_CAP,SUPPRESSION_PENALTY_CAP_MULTIPLIER,K_WELFARE_VIABILITY,K_WELFARE_CAPACITY,K_WELFARE_SHRINKAGE,K_WELFARE_AVG_WB_TREND,K_WELFARE_POP_TREND,K_AGENCY_VIABILITY,K_AGENCY_SHRINKAGE,K_AGENCY_POP_TREND,K_INSTITUTION_VIABILITY,K_INSTITUTION_CAPACITY,K_INSTITUTION_SHRINKAGE,K_INSTITUTION_GROWTH,K_INSTITUTION_POP_TREND,K_INSTITUTION_PSI_TREND,K_RESILIENCE_VIABILITY,K_RESILIENCE_CAPACITY,K_RESILIENCE_SHRINKAGE,K_RESILIENCE_GROWTH,K_RESILIENCE_DEFICIT_CONTRIBUTION,K_RESILIENCE_POP_TREND,K_RESILIENCE_RES_TREND,K_SUPPRESSION_VIABILITY,K_SUPPRESSION_CAPACITY,K_SUPPRESSION_SHRINKAGE,K_SUPPRESSION_POP_TREND,K_SUPPRESSION_PSI_TREND,mean_final_population,min_final_population,pairs_above_threshold,max_cosine_distance,mean_cosine_distance,welfare_mean_to_cap,agency_mean_to_cap,institution_mean_to_cap,resilience_mean_to_cap,suppression_mean_to_cap,criterion_1_pass,criterion_2_pass,criterion_3_pass,overall_good,wall_clock_sec,error
8,2.222915,2.128104,1.327953,2.056318,3.790688,0.726799,0.400102,0.333450,0.053749,0.067495,0.129247,0.360123,0.106064,0.312330,0.503985,0.631811,0.455265,0.242091,0.031276,0.688886,0.348098,0.419441,0.221950,0.357727,0.085078,0.238003,0.081186,0.368253,0.577350,0.132019,0.286399,48.200000,41.000000,0,0.000983,0.000712,0.960407,0.634303,0.963783,0.892156,0.311892,0,0,0,0,67.032320,
7,2.300033,1.188254,3.189778,1.636863,2.537932,0.609874,0.193701,0.014059,0.134936,0.103441,0.169287,0.281656,0.187326,0.604786,0.322855,0.343437,0.120763,0.145159,0.151324,0.008870,0.676987,0.139353,0.072710,0.588136,0.063948,0.063475,0.125819,0.117043,0.471227,0.238949,0.100797,44.600000,29.000000,0,0.002981,0.001093,0.950821,0.977856,0.500702,0.961054,0.467679,0,0,0,0,85.939697,
9,4.025714,1.547523,2.993407,2.539319,2.212460,0.466358,0.096418,0.582833,0.187554,0.132006,0.473771,0.091835,0.043089,0.554192,0.081037,0.059001,0.199205,0.063190,0.244784,0.184949,0.498552,0.061281,0.096142,0.621484,0.218301,0.001127,0.553487,0.182106,0.028696,0.261047,0.033017,16.600000,14.000000,0,0.001084,0.000581,0.885715,0.877467,0.472854,0.713020,0.550295,0,0,0,0,97.022951,
6,4.450366,2.736639,1.131604,3.802300,3.410680,0.317574,0.309900,0.464675,0.298770,0.096059,0.524814,0.014312,0.074327,0.278158,0.777791,0.391075,0.346092,0.150733,0.363220,0.614369,0.171020,0.279239,0.245332,0.026792,0.229984,0.275715,0.723822,0.426470,0.320072,0.118956,0.223002,17.400000,12.000000,0,0.003349,0.001277,0.743215,0.500012,0.988235,0.469769,0.403864,0,0,0,0,99.554145,
5,3.881480,1.769466,3.760882,1.914069,2.783363,0.147638,0.087801,0.526017,0.224300,0.033326,0.676797,0.171459,0.120118,0.522549,0.666827,0.013888,0.421201,0.028098,0.213186,0.335012,0.468315,0.402834,0.193865,0.666355,0.097200,0.337115,0.465653,0.329267,0.555405,0.017293,0.003641,18.600000,13.000000,0,0.001041,0.000570,0.800432,0.876094,0.357234,0.971935,0.495611,0,0,0,0,105.401005,
```

==========================================
FILE: simulation/diagnostics/stage16_baseline_phi10.json
==========================================

- Size: 7165 bytes
- Modified: 2026-06-01T15:19:39Z
- Structure: object with 8 top-level keys
- Keys: phi, n_seeds, n_steps, mean_final_pop, min_final_pop, max_final_pop, per_seed, total_wall_clock_sec
