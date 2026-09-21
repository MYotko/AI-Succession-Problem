# In-loop drift defense, gate 3: recovery confirmation, quiet period 20

This is gate 3 of the promotion plan. The recovery rule, its three quiet periods, the selection rule and the criterion were fixed before any run.
This is not a promotion decision and selects no parameter. No ratio of two measured counts was computed.
Applying the Section 6 selection rule and criterion and the Section 8 interpretation is reserved for the operator.

## R1

Negative: the recovered arm spent more steps past the threshold.

| Attack | Contrast | Pairs | Mean difference | Paired standard error | t | Harm direction | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A3 | LATCHED_minus_RECOVER-20 | 20 | -3.3 | 1.1587198017412872 | -2.8479706612770963 | Negative: the recovered arm spent more steps past the threshold. | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | OFF_minus_LATCHED | 20 | 3.8 | 1.4896131606632148 | 2.5509978700162264 | Negative: the recovered arm spent more steps past the threshold. | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | OFF_minus_RECOVER-20 | 20 | 0.5 | 1.42256255065509 | 0.3514783935298662 | Negative: the recovered arm spent more steps past the threshold. | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | LATCHED_minus_RECOVER-20 | 20 | -3.3 | 2.037929806135835 | -1.6192903161160417 | Negative: the recovered arm spent more steps past the threshold. | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | OFF_minus_LATCHED | 20 | 3.55 | 1.2106435869969503 | 2.932324623141908 | Negative: the recovered arm spent more steps past the threshold. | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | OFF_minus_RECOVER-20 | 20 | 0.25 | 1.972008060194908 | 0.12677432970293775 | Negative: the recovered arm spent more steps past the threshold. | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | LATCHED_minus_RECOVER-20 | 20 | -7.35 | 2.3700710626699073 | -3.1011728364465814 | Negative: the recovered arm spent more steps past the threshold. | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | OFF_minus_LATCHED | 20 | 98.65 | 6.748986278655016 | 14.617010011118241 | Negative: the recovered arm spent more steps past the threshold. | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | OFF_minus_RECOVER-20 | 20 | 91.3 | 5.665268145277392 | 16.115742037048737 | Negative: the recovered arm spent more steps past the threshold. | Known-pathway design; constants calibrated on the drift mapping construction. |

Section 6 condition arithmetic for LATCHED minus RECOVER-20. Undefined t leaves the comparison undefined. No adoption ruling is made.

| Attack | Pairs | Mean difference | Paired standard error | t | Harm threshold | Threshold reached | Selection condition holds | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A3 | 20 | -3.3 | 1.1587198017412872 | -2.8479706612770963 | t <= -2.0 | True | False | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | 20 | -3.3 | 2.037929806135835 | -1.6192903161160417 | t <= -2.0 | False | True | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | 20 | -7.35 | 2.3700710626699073 | -3.1011728364465814 | t <= -2.0 | True | False | Known-pathway design; constants calibrated on the drift mapping construction. |

## R2

Positive: the recovered arm ended with fewer people.

| Attack | Contrast | Pairs | Mean difference | Paired standard error | t | Harm direction | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A3 | LATCHED_minus_RECOVER-20 | 20 | 2.2 | 15.723365114577597 | 0.13991915750657696 | Positive: the recovered arm ended with fewer people. | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | OFF_minus_LATCHED | 20 | -20.8 | 11.69583821617533 | -1.7784103726087477 | Positive: the recovered arm ended with fewer people. | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | OFF_minus_RECOVER-20 | 20 | -18.6 | 15.069907274537487 | -1.2342478066488871 | Positive: the recovered arm ended with fewer people. | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | LATCHED_minus_RECOVER-20 | 20 | 0.0 | 8.82669396296198 | 0.0 | Positive: the recovered arm ended with fewer people. | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | OFF_minus_LATCHED | 20 | -24.35 | 12.574258375117417 | -1.9364959167838496 | Positive: the recovered arm ended with fewer people. | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | OFF_minus_RECOVER-20 | 20 | -24.35 | 12.30923380402311 | -1.9781897385068374 | Positive: the recovered arm ended with fewer people. | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | LATCHED_minus_RECOVER-20 | 20 | 31.2 | 17.245685959408117 | 1.8091481007735342 | Positive: the recovered arm ended with fewer people. | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | OFF_minus_LATCHED | 20 | -268.55 | 11.463781639305774 | -23.4259521377505 | Positive: the recovered arm ended with fewer people. | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | OFF_minus_RECOVER-20 | 20 | -237.35 | 13.099472669177423 | -18.119049979658783 | Positive: the recovered arm ended with fewer people. | Known-pathway design; constants calibrated on the drift mapping construction. |

Section 6 condition arithmetic for LATCHED minus RECOVER-20. Undefined t leaves the comparison undefined. No adoption ruling is made.

| Attack | Pairs | Mean difference | Paired standard error | t | Harm threshold | Threshold reached | Selection condition holds | Basis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A3 | 20 | 2.2 | 15.723365114577597 | 0.13991915750657696 | t >= 2.0 | False | True | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | 20 | 0.0 | 8.82669396296198 | 0.0 | t >= 2.0 | False | True | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | 20 | 31.2 | 17.245685959408117 | 1.8091481007735342 | t >= 2.0 | False | True | Known-pathway design; constants calibrated on the drift mapping construction. |

| Attack | Defense | Runs | Extinctions | Basis |
| --- | --- | --- | --- | --- |
| A3 | LATCHED | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | OFF | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | RECOVER-20 | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | LATCHED | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | OFF | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | RECOVER-20 | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | LATCHED | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | OFF | 20 | 20 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | RECOVER-20 | 20 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |

## R3

Counts with no harm direction. Steps use the state in force for that step; final state uses the state after the last completed step update.
Per-run counts are retained in results.json and runs.csv.

| Attack | Defense | VETO steps | CONSENSUS steps | Runs non-NORMAL at last completion | Basis |
| --- | --- | --- | --- | --- | --- |
| A3 | LATCHED | 524 | 3513 | 20 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | OFF | 0 | 0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | RECOVER-20 | 1156 | 1710 | 10 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | LATCHED | 226 | 2900 | 20 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | OFF | 0 | 0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | RECOVER-20 | 881 | 837 | 3 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | LATCHED | 682 | 3867 | 20 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | OFF | 0 | 0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | RECOVER-20 | 2529 | 1850 | 20 | Known-pathway design; constants calibrated on the drift mapping construction. |

## R4

No harm direction. Every transition is dated at its completed step and acts from the next step.
Re-escalation counts each escalation after an earlier recovery transition. Per-run counts are retained in results.json and runs.csv.

| Attack | Defense | Direction or count | Minimum | Median | Maximum | Basis |
| --- | --- | --- | --- | --- | --- | --- |
| A3 | LATCHED | NORMAL_to_VETO | 1 | 1.0 | 1 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | LATCHED | VETO_to_CONSENSUS | 1 | 1.0 | 1 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | LATCHED | CONSENSUS_to_VETO | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | LATCHED | VETO_to_NORMAL | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | LATCHED | re_escalations_after_recovery | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | OFF | NORMAL_to_VETO | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | OFF | VETO_to_CONSENSUS | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | OFF | CONSENSUS_to_VETO | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | OFF | VETO_to_NORMAL | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | OFF | re_escalations_after_recovery | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | RECOVER-20 | NORMAL_to_VETO | 1 | 2.5 | 4 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | RECOVER-20 | VETO_to_CONSENSUS | 1 | 3.0 | 5 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | RECOVER-20 | CONSENSUS_to_VETO | 1 | 2.0 | 5 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | RECOVER-20 | VETO_to_NORMAL | 1 | 2.0 | 3 | Known-pathway design; constants calibrated on the drift mapping construction. |
| A3 | RECOVER-20 | re_escalations_after_recovery | 1 | 4.0 | 6 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | LATCHED | NORMAL_to_VETO | 1 | 1.0 | 1 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | LATCHED | VETO_to_CONSENSUS | 1 | 1.0 | 1 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | LATCHED | CONSENSUS_to_VETO | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | LATCHED | VETO_to_NORMAL | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | LATCHED | re_escalations_after_recovery | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | OFF | NORMAL_to_VETO | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | OFF | VETO_to_CONSENSUS | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | OFF | CONSENSUS_to_VETO | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | OFF | VETO_to_NORMAL | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | OFF | re_escalations_after_recovery | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | RECOVER-20 | NORMAL_to_VETO | 1 | 2.0 | 5 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | RECOVER-20 | VETO_to_CONSENSUS | 0 | 1.0 | 4 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | RECOVER-20 | CONSENSUS_to_VETO | 0 | 1.0 | 4 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | RECOVER-20 | VETO_to_NORMAL | 1 | 2.0 | 5 | Known-pathway design; constants calibrated on the drift mapping construction. |
| H | RECOVER-20 | re_escalations_after_recovery | 0 | 1.0 | 5 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | LATCHED | NORMAL_to_VETO | 1 | 1.0 | 1 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | LATCHED | VETO_to_CONSENSUS | 1 | 1.0 | 1 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | LATCHED | CONSENSUS_to_VETO | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | LATCHED | VETO_to_NORMAL | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | LATCHED | re_escalations_after_recovery | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | OFF | NORMAL_to_VETO | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | OFF | VETO_to_CONSENSUS | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | OFF | CONSENSUS_to_VETO | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | OFF | VETO_to_NORMAL | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | OFF | re_escalations_after_recovery | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | RECOVER-20 | NORMAL_to_VETO | 4 | 6.0 | 7 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | RECOVER-20 | VETO_to_CONSENSUS | 1 | 3.0 | 4 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | RECOVER-20 | CONSENSUS_to_VETO | 1 | 3.0 | 4 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | RECOVER-20 | VETO_to_NORMAL | 3 | 5.0 | 6 | Known-pathway design; constants calibrated on the drift mapping construction. |
| M1 | RECOVER-20 | re_escalations_after_recovery | 5 | 8.0 | 9 | Known-pathway design; constants calibrated on the drift mapping construction. |

## R5

H only. No harm direction. The first post-update NORMAL step at or after 150 minus 150 is the release latency.
A run already NORMAL at shock completion has latency zero. A run with no observed return has undefined latency.

| Defense | Never returned | Latency minimum | Median | Maximum | Basis |
| --- | --- | --- | --- | --- | --- |
| LATCHED | 2 | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| OFF | 0 | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |
| RECOVER-20 | 0 | 0 | 0.0 | 0 | Known-pathway design; constants calibrated on the drift mapping construction. |

| Defense | Seed | First NORMAL step at or after shock | Latency | Never returned |
| --- | --- | --- | --- | --- |
| LATCHED | 1835088100 | undefined | undefined | True |
| LATCHED | 1835088101 | 150 | 0 | False |
| LATCHED | 1835088102 | 150 | 0 | False |
| LATCHED | 1835088103 | 150 | 0 | False |
| LATCHED | 1835088104 | 150 | 0 | False |
| LATCHED | 1835088105 | 150 | 0 | False |
| LATCHED | 1835088106 | 150 | 0 | False |
| LATCHED | 1835088107 | 150 | 0 | False |
| LATCHED | 1835088108 | undefined | undefined | True |
| LATCHED | 1835088109 | 150 | 0 | False |
| LATCHED | 1835088110 | 150 | 0 | False |
| LATCHED | 1835088111 | 150 | 0 | False |
| LATCHED | 1835088112 | 150 | 0 | False |
| LATCHED | 1835088113 | 150 | 0 | False |
| LATCHED | 1835088114 | 150 | 0 | False |
| LATCHED | 1835088115 | 150 | 0 | False |
| LATCHED | 1835088116 | 150 | 0 | False |
| LATCHED | 1835088117 | 150 | 0 | False |
| LATCHED | 1835088118 | 150 | 0 | False |
| LATCHED | 1835088119 | 150 | 0 | False |
| OFF | 1835088100 | 150 | 0 | False |
| OFF | 1835088101 | 150 | 0 | False |
| OFF | 1835088102 | 150 | 0 | False |
| OFF | 1835088103 | 150 | 0 | False |
| OFF | 1835088104 | 150 | 0 | False |
| OFF | 1835088105 | 150 | 0 | False |
| OFF | 1835088106 | 150 | 0 | False |
| OFF | 1835088107 | 150 | 0 | False |
| OFF | 1835088108 | 150 | 0 | False |
| OFF | 1835088109 | 150 | 0 | False |
| OFF | 1835088110 | 150 | 0 | False |
| OFF | 1835088111 | 150 | 0 | False |
| OFF | 1835088112 | 150 | 0 | False |
| OFF | 1835088113 | 150 | 0 | False |
| OFF | 1835088114 | 150 | 0 | False |
| OFF | 1835088115 | 150 | 0 | False |
| OFF | 1835088116 | 150 | 0 | False |
| OFF | 1835088117 | 150 | 0 | False |
| OFF | 1835088118 | 150 | 0 | False |
| OFF | 1835088119 | 150 | 0 | False |
| RECOVER-20 | 1835088100 | 150 | 0 | False |
| RECOVER-20 | 1835088101 | 150 | 0 | False |
| RECOVER-20 | 1835088102 | 150 | 0 | False |
| RECOVER-20 | 1835088103 | 150 | 0 | False |
| RECOVER-20 | 1835088104 | 150 | 0 | False |
| RECOVER-20 | 1835088105 | 150 | 0 | False |
| RECOVER-20 | 1835088106 | 150 | 0 | False |
| RECOVER-20 | 1835088107 | 150 | 0 | False |
| RECOVER-20 | 1835088108 | 150 | 0 | False |
| RECOVER-20 | 1835088109 | 150 | 0 | False |
| RECOVER-20 | 1835088110 | 150 | 0 | False |
| RECOVER-20 | 1835088111 | 150 | 0 | False |
| RECOVER-20 | 1835088112 | 150 | 0 | False |
| RECOVER-20 | 1835088113 | 150 | 0 | False |
| RECOVER-20 | 1835088114 | 150 | 0 | False |
| RECOVER-20 | 1835088115 | 150 | 0 | False |
| RECOVER-20 | 1835088116 | 150 | 0 | False |
| RECOVER-20 | 1835088117 | 150 | 0 | False |
| RECOVER-20 | 1835088118 | 150 | 0 | False |
| RECOVER-20 | 1835088119 | 150 | 0 | False |

## R6

No harm direction. Recorded steps equal completed steps in every run: True.
Runs: 180. Recorded steps: 52244.
Every alarm, state transition with its direction, and applied action is retained in the per-run audit referenced by results.json and runs.csv.

## Sign fixture

Assertion passed: True.
The synthetic recovered arm is worse on both quantities. The fixture labels R1 negative and R2 positive as harm.

## Reduced attack-validity check

Numbers only; no validity ruling. Resilience stock is a continuous value in this separately requested check.

| H OFF median at 149 | A3 OFF median at 149 | Pairs | Mean H OFF minus A3 OFF | Paired standard error | t | Basis |
| --- | --- | --- | --- | --- | --- | --- |
| 0.39095707397566704 | 0.2000005551106584 | 20 | 0.20236498774830786 | 0.007907840346536531 | 25.59042404503519 | Known-pathway design; constants calibrated on the drift mapping construction. |

No exploratory analysis was performed.

## Source verification

| Path | Start blob | Start working tree | Completion blob | Completion working tree |
| --- | --- | --- | --- | --- |
| simulation/diagnostics/defense_recovery_design_note.md | 23f07aeff3953c237f5ea71101791e00b54f258371082075fc0afe77a2453250 | 23f07aeff3953c237f5ea71101791e00b54f258371082075fc0afe77a2453250 | 23f07aeff3953c237f5ea71101791e00b54f258371082075fc0afe77a2453250 | 23f07aeff3953c237f5ea71101791e00b54f258371082075fc0afe77a2453250 |
| simulation/diagnostics/defense_heldout_design_note.md | f1140c037528c3503ceddd56b6e780238b8bf2e78e183af757171900663f37dd | f1140c037528c3503ceddd56b6e780238b8bf2e78e183af757171900663f37dd | f1140c037528c3503ceddd56b6e780238b8bf2e78e183af757171900663f37dd | f1140c037528c3503ceddd56b6e780238b8bf2e78e183af757171900663f37dd |
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
| simulation/diagnostics/defense_heldout_run_a3s_executor.py | 5ddec0d9c3df7ad919557fb4cd54972f3a70e1a7e4d1c90603ba83f5ccbb9e37 | 5ddec0d9c3df7ad919557fb4cd54972f3a70e1a7e4d1c90603ba83f5ccbb9e37 | 5ddec0d9c3df7ad919557fb4cd54972f3a70e1a7e4d1c90603ba83f5ccbb9e37 | 5ddec0d9c3df7ad919557fb4cd54972f3a70e1a7e4d1c90603ba83f5ccbb9e37 |
| simulation/diagnostics/defense_heldout_run_a3s_analysis.py | cc7f8aef601fd86d15f68e866c0a46fa8c0a7b269b0e04f8cabe306e27e3e49a | cc7f8aef601fd86d15f68e866c0a46fa8c0a7b269b0e04f8cabe306e27e3e49a | cc7f8aef601fd86d15f68e866c0a46fa8c0a7b269b0e04f8cabe306e27e3e49a | cc7f8aef601fd86d15f68e866c0a46fa8c0a7b269b0e04f8cabe306e27e3e49a |
| simulation/diagnostics/defense_heldout_run_a3s_plan.json | 70c1ff75797335da27330767f1242e3636d3d34364b2272d29c0e46175d20b46 | 70c1ff75797335da27330767f1242e3636d3d34364b2272d29c0e46175d20b46 | 70c1ff75797335da27330767f1242e3636d3d34364b2272d29c0e46175d20b46 | 70c1ff75797335da27330767f1242e3636d3d34364b2272d29c0e46175d20b46 |
| simulation/diagnostics/defense_recovery_run_a3_executor.py | 6d84c5137373ed2951416de9c4adae121533e747648a1934ead800efc3dc7ba5 | 6d84c5137373ed2951416de9c4adae121533e747648a1934ead800efc3dc7ba5 | 6d84c5137373ed2951416de9c4adae121533e747648a1934ead800efc3dc7ba5 | 6d84c5137373ed2951416de9c4adae121533e747648a1934ead800efc3dc7ba5 |
| simulation/diagnostics/defense_recovery_run_a3_analysis.py | c70c2d731ec893620b1802ff3e77443de828dc5132edd61b6fb830fea62c7bce | c70c2d731ec893620b1802ff3e77443de828dc5132edd61b6fb830fea62c7bce | c70c2d731ec893620b1802ff3e77443de828dc5132edd61b6fb830fea62c7bce | c70c2d731ec893620b1802ff3e77443de828dc5132edd61b6fb830fea62c7bce |
| simulation/diagnostics/defense_recovery_run_a3_plan.json | 75b00aa1461a64b7bb01cb0e8d176fb8a8cd4036b5ae8ea12905c08c8c1ccdce | 75b00aa1461a64b7bb01cb0e8d176fb8a8cd4036b5ae8ea12905c08c8c1ccdce | 75b00aa1461a64b7bb01cb0e8d176fb8a8cd4036b5ae8ea12905c08c8c1ccdce | 75b00aa1461a64b7bb01cb0e8d176fb8a8cd4036b5ae8ea12905c08c8c1ccdce |

## Execution evidence

HEAD: 3d9d0ce5d29a28d628e25f65b344a6b90e5db094
Machine: YOTKOTEST
Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]
NumPy: 2.4.4

No source pin changed. No completed run was rerun.

Tool-layer workarounds:
Replaced unavailable structuredClone in the tooling with a JSON round-trip copy; no model code ran and the plan data was unchanged.

T0 stderr warnings:
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied

Executor fixes before any model run:

T1 numeric tolerance rules: {"alarm_steps": "exact", "attack_arithmetic_absolute": 1e-12, "computed_floats_absolute": 1e-09, "consensus": "bitwise", "constants": "bitwise", "inertness": "exact", "registered_counts": "not tolerance-adjusted", "share_sum_absolute": 1e-12, "wrapper_identity": "exact"}

## T1 evidence

1_inertness: {"exact_recorded_field_comparisons": 1111, "first_recorded_model_field_divergence": {"field": "h_n_latest", "latched": 0.9867364909351616, "recover_20": 0.9868227133503724, "step": 41}, "first_recovery": {"consensus_fields": null, "direction": "recovery", "effective_from_step": 41, "from": "VETO", "held_action": null, "quiet_count_after": 0, "re_escalation_after_recovery": false, "step": 40, "to": "NORMAL"}, "first_state_divergence": {"latched": "VETO", "recover_20": "NORMAL", "step": 40}, "passed": true, "recorded_fields_exact_until_recovery": true, "timing": "State transition after step t affects actions from step t+1."}

2_recovery_mechanics: {"case_count": 5, "evidence_file": "defense_recovery_run_conf_recovery_mechanics_gate.json", "passed": true}

4_m1_identity: {"checks": [{"actual": "optimize_u_sys_v2", "field": "policy", "passed": true, "reference_with_registered_shock": "optimize_u_sys_v2"}, {"actual": 1835088100, "field": "random_seed", "passed": true, "reference_with_registered_shock": 1835088100}, {"actual": 10.0, "field": "phi", "passed": true, "reference_with_registered_shock": 10.0}, {"actual": 50, "field": "attack_step", "passed": true, "reference_with_registered_shock": 50}, {"actual": 300, "field": "n_candidates_v2", "passed": true, "reference_with_registered_shock": 300}, {"actual": 20, "field": "rollout_steps_v2", "passed": true, "reference_with_registered_shock": 20}, {"actual": 20, "field": "bootstrap_turn_step_v2", "passed": true, "reference_with_registered_shock": 20}, {"actual": 150, "field": "shock_step", "passed": true, "reference_with_registered_shock": 150}, {"actual": 0.6, "field": "shock_magnitude", "passed": true, "reference_with_registered_shock": 0.6}, {"actual": "sub_threshold_drift", "field": "attack_vector_v2", "passed": true, "reference_with_registered_shock": "sub_threshold_drift"}, {"actual": false, "field": "cop_methodological_diversity", "passed": true, "reference_with_registered_shock": false}, {"actual": false, "field": "cop_cusum_drift", "passed": true, "reference_with_registered_shock": false}], "passed": true, "reference_configuration": {"attack_step": 50, "attack_vector_v2": "sub_threshold_drift", "bootstrap_turn_step_v2": 20, "cop_cusum_drift": false, "cop_methodological_diversity": false, "n_candidates_v2": 300, "phi": 10.0, "policy": "optimize_u_sys_v2", "random_seed": 1835088100, "rollout_steps_v2": 20, "shock_magnitude": 0.15, "shock_step": 0}, "reference_constructor_basis": "Copied verbatim from committed drift_defense_run_executor.py", "registered_shock_overrides": {"shock_magnitude": 0.6, "shock_step": 150}, "seed": 1835088100}

5_composition: [{"comparisons": 8100, "first": "gate_H_OFF", "first_difference": null, "identity_columns_not_observables": ["arm", "defense_arm"], "passed": true, "second": "gate_H_NORMAL"}, {"comparisons": 8100, "first": "gate_A3_OFF", "first_difference": null, "identity_columns_not_observables": ["arm", "defense_arm"], "passed": true, "second": "gate_A3_NORMAL"}]

6_online_equivalence: {"gate_A3_LATCHED": {"A": {"alarm_steps": [20], "computed_float_absolute_tolerance": 1e-09, "passed": true, "steps": 300}, "entropy": {"alarm_steps": [151, 153, 156, 162, 176, 191, 206], "computed_float_absolute_tolerance": 1e-09, "passed": true, "steps": 300}, "g": {"alarm_steps": [155], "computed_float_absolute_tolerance": 1e-09, "passed": true, "steps": 300}}, "gate_M1_LATCHED": {"A": {"alarm_steps": [20], "computed_float_absolute_tolerance": 1e-09, "passed": true, "steps": 300}, "entropy": {"alarm_steps": [151, 153, 156, 162, 176, 191, 206], "computed_float_absolute_tolerance": 1e-09, "passed": true, "steps": 300}, "g": {"alarm_steps": [155], "computed_float_absolute_tolerance": 1e-09, "passed": true, "steps": 300}}}

7_no_oracle: {"evidence_file": "defense_recovery_run_conf_recovery_no_oracle_gate.json", "passed": true}

8_incumbent_calls: {"passed": true, "per_step_counts": {"0": 1, "1": 1, "10": 1, "100": 1, "101": 1, "102": 1, "103": 1, "104": 1, "105": 1, "106": 1, "107": 1, "108": 1, "109": 1, "11": 1, "110": 1, "111": 1, "112": 1, "113": 1, "114": 1, "115": 1, "116": 1, "117": 1, "118": 1, "119": 1, "12": 1, "120": 1, "121": 1, "122": 1, "123": 1, "124": 1, "125": 1, "126": 1, "127": 1, "128": 1, "129": 1, "13": 1, "130": 1, "131": 1, "132": 1, "133": 1, "134": 1, "135": 1, "136": 1, "137": 1, "138": 1, "139": 1, "14": 1, "140": 1, "141": 1, "142": 1, "143": 1, "144": 1, "145": 1, "146": 1, "147": 1, "148": 1, "149": 1, "15": 1, "150": 1, "151": 1, "152": 1, "153": 1, "154": 1, "155": 1, "156": 1, "157": 1, "158": 1, "159": 1, "16": 1, "160": 1, "161": 1, "162": 1, "163": 1, "164": 1, "165": 1, "166": 1, "167": 1, "168": 1, "169": 1, "17": 1, "170": 1, "171": 1, "172": 1, "173": 1, "174": 1, "175": 1, "176": 1, "177": 1, "178": 1, "179": 1, "18": 1, "180": 1, "181": 1, "182": 1, "183": 1, "184": 1, "185": 1, "186": 1, "187": 1, "188": 1, "189": 1, "19": 1, "190": 1, "191": 1, "192": 1, "193": 1, "194": 1, "195": 1, "196": 1, "197": 1, "198": 1, "199": 1, "2": 1, "20": 1, "200": 1, "201": 1, "202": 1, "203": 1, "204": 1, "205": 1, "206": 1, "207": 1, "208": 1, "209": 1, "21": 1, "210": 1, "211": 1, "212": 1, "213": 1, "214": 1, "215": 1, "216": 1, "217": 1, "218": 1, "219": 1, "22": 1, "220": 1, "221": 1, "222": 1, "223": 1, "224": 1, "225": 1, "226": 1, "227": 1, "228": 1, "229": 1, "23": 1, "230": 1, "231": 1, "232": 1, "233": 1, "234": 1, "235": 1, "236": 1, "237": 1, "238": 1, "239": 1, "24": 1, "240": 1, "241": 1, "242": 1, "243": 1, "244": 1, "245": 1, "246": 1, "247": 1, "248": 1, "249": 1, "25": 1, "250": 1, "251": 1, "252": 1, "253": 1, "254": 1, "255": 1, "256": 1, "257": 1, "258": 1, "259": 1, "26": 1, "260": 1, "261": 1, "262": 1, "263": 1, "264": 1, "265": 1, "266": 1, "267": 1, "268": 1, "269": 1, "27": 1, "270": 1, "271": 1, "272": 1, "273": 1, "274": 1, "275": 1, "276": 1, "277": 1, "278": 1, "279": 1, "28": 1, "280": 1, "281": 1, "282": 1, "283": 1, "284": 1, "285": 1, "286": 1, "287": 1, "288": 1, "289": 1, "29": 1, "290": 1, "291": 1, "292": 1, "293": 1, "294": 1, "295": 1, "296": 1, "297": 1, "298": 1, "299": 1, "3": 1, "30": 1, "31": 1, "32": 1, "33": 1, "34": 1, "35": 1, "36": 1, "37": 1, "38": 1, "39": 1, "4": 1, "40": 1, "41": 1, "42": 1, "43": 1, "44": 1, "45": 1, "46": 1, "47": 1, "48": 1, "49": 1, "5": 1, "50": 1, "51": 1, "52": 1, "53": 1, "54": 1, "55": 1, "56": 1, "57": 1, "58": 1, "59": 1, "6": 1, "60": 1, "61": 1, "62": 1, "63": 1, "64": 1, "65": 1, "66": 1, "67": 1, "68": 1, "69": 1, "7": 1, "70": 1, "71": 1, "72": 1, "73": 1, "74": 1, "75": 1, "76": 1, "77": 1, "78": 1, "79": 1, "8": 1, "80": 1, "81": 1, "82": 1, "83": 1, "84": 1, "85": 1, "86": 1, "87": 1, "88": 1, "89": 1, "9": 1, "90": 1, "91": 1, "92": 1, "93": 1, "94": 1, "95": 1, "96": 1, "97": 1, "98": 1, "99": 1}}

9_constants: {"channels": {"A": {"allowance": 0.045310678652355926, "direction": "upper", "reference": 0.27535941373839806, "threshold": 0.7701182670542909}, "entropy": {"allowance": 0.003549173553323096, "direction": "lower", "reference": 0.9890951785336365, "threshold": 0.17319485850717864}, "g": {"allowance": 0.022160874873702576, "direction": "upper", "reference": 0.9786446054615587, "threshold": 4.507729894543943}}, "checks": [{"actual": 0.9890951785336365, "binary64_hex": "0x1.fa6aaee8ddd2fp-1", "expected": 0.9890951785336365, "passed": true, "quantity": "entropy.reference"}, {"actual": 0.003549173553323096, "binary64_hex": "0x1.d13280adbf63bp-9", "expected": 0.003549173553323096, "passed": true, "quantity": "entropy.allowance"}, {"actual": 0.17319485850717864, "binary64_hex": "0x1.62b3fc68fd4bcp-3", "expected": 0.17319485850717864, "passed": true, "quantity": "entropy.threshold"}, {"actual": 0.9786446054615587, "binary64_hex": "0x1.f510e7ddba7acp-1", "expected": 0.9786446054615587, "passed": true, "quantity": "g.reference"}, {"actual": 0.022160874873702576, "binary64_hex": "0x1.6b15723554cc7p-6", "expected": 0.022160874873702576, "passed": true, "quantity": "g.allowance"}, {"actual": 4.507729894543943, "binary64_hex": "0x1.207ea58711231p+2", "expected": 4.507729894543943, "passed": true, "quantity": "g.threshold"}, {"actual": 0.27535941373839806, "binary64_hex": "0x1.19f7d1729bcdfp-2", "expected": 0.27535941373839806, "passed": true, "quantity": "A.reference"}, {"actual": 0.045310678652355926, "binary64_hex": "0x1.732f615f15fcep-5", "expected": 0.045310678652355926, "passed": true, "quantity": "A.allowance"}, {"actual": 0.7701182670542909, "binary64_hex": "0x1.8a4cf10619ca9p-1", "expected": 0.7701182670542909, "passed": true, "quantity": "A.threshold"}, {"actual": 0.13058054663961136, "binary64_hex": "0x1.0b6dd04a7ccabp-3", "expected": 0.13058054663961136, "passed": true, "quantity": "median.x_compute"}, {"actual": 0.19789308864393101, "binary64_hex": "0x1.9548f8bea4122p-3", "expected": 0.19789308864393101, "passed": true, "quantity": "median.x_bio_welfare"}, {"actual": 0.050694324487428735, "binary64_hex": "0x1.9f49b43885ae2p-5", "expected": 0.050694324487428735, "passed": true, "quantity": "median.x_novelty_agency"}, {"actual": 0.25643120498706085, "binary64_hex": "0x1.0695e6dc5f89ap-2", "expected": 0.25643120498706085, "passed": true, "quantity": "median.x_institutional_capacity"}, {"actual": 0.27322100367503155, "binary64_hex": "0x1.17c73f2d754e4p-2", "expected": 0.27322100367503155, "passed": true, "quantity": "median.x_transfer_comprehension"}, {"actual": 0.051169013866533296, "binary64_hex": "0x1.a32d332402b63p-5", "expected": 0.051169013866533296, "passed": true, "quantity": "median.x_resilience"}, {"actual": 0.1360229355155997, "binary64_hex": "0x1.1693315c5d03fp-3", "expected": 0.1360229355155997, "passed": true, "quantity": "consensus.x_compute"}, {"actual": 0.2061409568906703, "binary64_hex": "0x1.a62d3ae1b14e2p-3", "expected": 0.2061409568906703, "passed": true, "quantity": "consensus.x_bio_welfare"}, {"actual": 0.052807183062202334, "binary64_hex": "0x1.b098b087df980p-5", "expected": 0.052807183062202334, "passed": true, "quantity": "consensus.x_novelty_agency"}, {"actual": 0.26711884854035045, "binary64_hex": "0x1.11879a7a81019p-2", "expected": 0.26711884854035045, "passed": true, "quantity": "consensus.x_institutional_capacity"}, {"actual": 0.2846084192537951, "binary64_hex": "0x1.237063b371fa6p-2", "expected": 0.2846084192537951, "passed": true, "quantity": "consensus.x_transfer_comprehension"}, {"actual": 0.053301656737382165, "binary64_hex": "0x1.b4a5ad104f40dp-5", "expected": 0.053301656737382165, "passed": true, "quantity": "consensus.x_resilience"}, {"actual": 0.4, "binary64_hex": "0x1.999999999999ap-2", "expected": 0.4, "passed": true, "quantity": "consensus.c_protective"}, {"actual": 0.2, "binary64_hex": "0x1.999999999999ap-3", "expected": 0.2, "passed": true, "quantity": "consensus.c_suppressive"}], "medians": [0.13058054663961136, 0.19789308864393101, 0.050694324487428735, 0.25643120498706085, 0.27322100367503155, 0.051169013866533296], "passed": true}

passed: true

scheduler: {"normal_cap": 15, "passed": true, "seed_assignment_independent_of_dispatch_order": true, "slot_measurements": [15, 0, 0, 0, 1, 3, 2], "synthetic_resume_pending": 178, "synthetic_resume_preserved": 2, "work_cap": 12}

status: "COMPLETE"

Attack arithmetic evidence: defense_recovery_run_conf_attack_arithmetic_gate.json
Full synthetic inputs, outputs, expected values and pre-onset outputs are retained in that file.

| Arm | Case | Resilience category | Moved | Maximum share error | Share sum | Constraints exact | Pre-onset exact | Passed |
| --- | ---: | --- | ---: | ---: | ---: | --- | --- | --- |
| A3 | 0 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A3 | 1 | small | 0.0005 | 0.0 | 1.0 | True | True | True |
| A3 | 2 | large | 0.19999999999999996 | 0.0 | 1.0 | True | True | True |
| A3 | 3 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A3 | 4 | small | 0.0004999999999999999 | 0.0 | 1.0 | True | True | True |
| A3 | 5 | large | 0.2 | 0.0 | 1.0 | True | True | True |
| A3 | 6 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A3 | 7 | small | 0.0005 | 0.0 | 0.9999999999999998 | True | True | True |
| A3 | 8 | large | 0.2 | 0.0 | 1.0 | True | True | True |
| A3 | 9 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A3 | 10 | small | 0.0005 | 0.0 | 1.0 | True | True | True |
| A3 | 11 | large | 0.2 | 0.0 | 1.0 | True | True | True |
| A3 | 12 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A3 | 13 | small | 0.0005 | 0.0 | 1.0 | True | True | True |
| A3 | 14 | large | 0.2 | 0.0 | 1.0 | True | True | True |
| A3 | 15 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A3 | 16 | small | 0.0005 | 0.0 | 1.0 | True | True | True |
| A3 | 17 | large | 0.19999999999999996 | 0.0 | 1.0 | True | True | True |
| A3 | 18 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A3 | 19 | small | 0.0004999999999999999 | 0.0 | 1.0 | True | True | True |
| A3 | 20 | large | 0.2 | 0.0 | 1.0 | True | True | True |
| A3 | 21 | zero | 0.0 | 0.0 | 1.0 | True | True | True |
| A3 | 22 | small | 0.0005 | 0.0 | 0.9999999999999998 | True | True | True |
| A3 | 23 | large | 0.2 | 0.0 | 1.0 | True | True | True |

Worker execution metadata: [{"complete": 180, "maximum_concurrent_workers": 15, "mode_changes": [{"active_at_request": 0, "cap": 15, "mode": "normal", "utc": "2026-09-21T02:59:40.098775+00:00"}], "new": ["run_A3_LATCHED_1835088100", "run_A3_LATCHED_1835088101", "run_A3_LATCHED_1835088102", "run_A3_LATCHED_1835088103", "run_A3_LATCHED_1835088104", "run_A3_LATCHED_1835088105", "run_A3_LATCHED_1835088106", "run_A3_LATCHED_1835088107", "run_A3_LATCHED_1835088108", "run_A3_LATCHED_1835088109", "run_A3_LATCHED_1835088110", "run_A3_LATCHED_1835088111", "run_A3_LATCHED_1835088112", "run_A3_LATCHED_1835088113", "run_A3_LATCHED_1835088114", "run_A3_LATCHED_1835088115", "run_A3_LATCHED_1835088116", "run_A3_LATCHED_1835088117", "run_A3_LATCHED_1835088118", "run_A3_LATCHED_1835088119", "run_A3_OFF_1835088100", "run_A3_OFF_1835088101", "run_A3_OFF_1835088102", "run_A3_OFF_1835088103", "run_A3_OFF_1835088104", "run_A3_OFF_1835088105", "run_A3_OFF_1835088106", "run_A3_OFF_1835088107", "run_A3_OFF_1835088108", "run_A3_OFF_1835088109", "run_A3_OFF_1835088110", "run_A3_OFF_1835088111", "run_A3_OFF_1835088112", "run_A3_OFF_1835088113", "run_A3_OFF_1835088114", "run_A3_OFF_1835088115", "run_A3_OFF_1835088116", "run_A3_OFF_1835088117", "run_A3_OFF_1835088118", "run_A3_OFF_1835088119", "run_A3_RECOVER-20_1835088100", "run_A3_RECOVER-20_1835088101", "run_A3_RECOVER-20_1835088102", "run_A3_RECOVER-20_1835088103", "run_A3_RECOVER-20_1835088104", "run_A3_RECOVER-20_1835088105", "run_A3_RECOVER-20_1835088106", "run_A3_RECOVER-20_1835088107", "run_A3_RECOVER-20_1835088108", "run_A3_RECOVER-20_1835088109", "run_A3_RECOVER-20_1835088110", "run_A3_RECOVER-20_1835088111", "run_A3_RECOVER-20_1835088112", "run_A3_RECOVER-20_1835088113", "run_A3_RECOVER-20_1835088114", "run_A3_RECOVER-20_1835088115", "run_A3_RECOVER-20_1835088116", "run_A3_RECOVER-20_1835088117", "run_A3_RECOVER-20_1835088118", "run_A3_RECOVER-20_1835088119", "run_H_LATCHED_1835088100", "run_H_LATCHED_1835088101", "run_H_LATCHED_1835088102", "run_H_LATCHED_1835088103", "run_H_LATCHED_1835088104", "run_H_LATCHED_1835088105", "run_H_LATCHED_1835088106", "run_H_LATCHED_1835088107", "run_H_LATCHED_1835088108", "run_H_LATCHED_1835088109", "run_H_LATCHED_1835088110", "run_H_LATCHED_1835088111", "run_H_LATCHED_1835088112", "run_H_LATCHED_1835088113", "run_H_LATCHED_1835088114", "run_H_LATCHED_1835088115", "run_H_LATCHED_1835088116", "run_H_LATCHED_1835088117", "run_H_LATCHED_1835088118", "run_H_LATCHED_1835088119", "run_H_OFF_1835088100", "run_H_OFF_1835088101", "run_H_OFF_1835088102", "run_H_OFF_1835088103", "run_H_OFF_1835088104", "run_H_OFF_1835088105", "run_H_OFF_1835088106", "run_H_OFF_1835088107", "run_H_OFF_1835088108", "run_H_OFF_1835088109", "run_H_OFF_1835088110", "run_H_OFF_1835088111", "run_H_OFF_1835088112", "run_H_OFF_1835088113", "run_H_OFF_1835088114", "run_H_OFF_1835088115", "run_H_OFF_1835088116", "run_H_OFF_1835088117", "run_H_OFF_1835088118", "run_H_OFF_1835088119", "run_H_RECOVER-20_1835088100", "run_H_RECOVER-20_1835088101", "run_H_RECOVER-20_1835088102", "run_H_RECOVER-20_1835088103", "run_H_RECOVER-20_1835088104", "run_H_RECOVER-20_1835088105", "run_H_RECOVER-20_1835088106", "run_H_RECOVER-20_1835088107", "run_H_RECOVER-20_1835088108", "run_H_RECOVER-20_1835088109", "run_H_RECOVER-20_1835088110", "run_H_RECOVER-20_1835088111", "run_H_RECOVER-20_1835088112", "run_H_RECOVER-20_1835088113", "run_H_RECOVER-20_1835088114", "run_H_RECOVER-20_1835088115", "run_H_RECOVER-20_1835088116", "run_H_RECOVER-20_1835088117", "run_H_RECOVER-20_1835088118", "run_H_RECOVER-20_1835088119", "run_M1_LATCHED_1835088100", "run_M1_LATCHED_1835088101", "run_M1_LATCHED_1835088102", "run_M1_LATCHED_1835088103", "run_M1_LATCHED_1835088104", "run_M1_LATCHED_1835088105", "run_M1_LATCHED_1835088106", "run_M1_LATCHED_1835088107", "run_M1_LATCHED_1835088108", "run_M1_LATCHED_1835088109", "run_M1_LATCHED_1835088110", "run_M1_LATCHED_1835088111", "run_M1_LATCHED_1835088112", "run_M1_LATCHED_1835088113", "run_M1_LATCHED_1835088114", "run_M1_LATCHED_1835088115", "run_M1_LATCHED_1835088116", "run_M1_LATCHED_1835088117", "run_M1_LATCHED_1835088118", "run_M1_LATCHED_1835088119", "run_M1_OFF_1835088100", "run_M1_OFF_1835088101", "run_M1_OFF_1835088102", "run_M1_OFF_1835088103", "run_M1_OFF_1835088104", "run_M1_OFF_1835088105", "run_M1_OFF_1835088106", "run_M1_OFF_1835088107", "run_M1_OFF_1835088108", "run_M1_OFF_1835088109", "run_M1_OFF_1835088110", "run_M1_OFF_1835088111", "run_M1_OFF_1835088112", "run_M1_OFF_1835088113", "run_M1_OFF_1835088114", "run_M1_OFF_1835088115", "run_M1_OFF_1835088116", "run_M1_OFF_1835088117", "run_M1_OFF_1835088118", "run_M1_OFF_1835088119", "run_M1_RECOVER-20_1835088100", "run_M1_RECOVER-20_1835088101", "run_M1_RECOVER-20_1835088102", "run_M1_RECOVER-20_1835088103", "run_M1_RECOVER-20_1835088104", "run_M1_RECOVER-20_1835088105", "run_M1_RECOVER-20_1835088106", "run_M1_RECOVER-20_1835088107", "run_M1_RECOVER-20_1835088108", "run_M1_RECOVER-20_1835088109", "run_M1_RECOVER-20_1835088110", "run_M1_RECOVER-20_1835088111", "run_M1_RECOVER-20_1835088112", "run_M1_RECOVER-20_1835088113", "run_M1_RECOVER-20_1835088114", "run_M1_RECOVER-20_1835088115", "run_M1_RECOVER-20_1835088116", "run_M1_RECOVER-20_1835088117", "run_M1_RECOVER-20_1835088118", "run_M1_RECOVER-20_1835088119"], "phase": "batch", "preserved": [], "resumed": []}, {"complete": 10, "maximum_concurrent_workers": 10, "mode_changes": [{"active_at_request": 0, "cap": 15, "mode": "normal", "utc": "2026-09-21T02:50:49.586043+00:00"}], "new": ["gate_H_OFF", "gate_A3_OFF", "gate_M1_OFF", "gate_H_NORMAL", "gate_A3_NORMAL", "gate_H_LATCHED", "gate_H_RECOVER20", "gate_M1_LATCHED", "gate_A3_LATCHED", "gate_M1_RECOVER20"], "phase": "gates", "preserved": [], "resumed": []}]
Resumed runs: []
Permission retry events: []


Supervision tool-layer workarounds recorded after executor startup:

- Corrected a malformed yield_time_ms property in the supervision tool call after a tooling parse error; the running executor was unaffected.
