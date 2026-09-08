# CUSUM arc, Stage 1: honest baseline and timing pilot

Instrument characterization of an existing mechanism. No hypothesis about the framework is under test. These outputs are not registered characterization data and do not cross the pre-registration boundary.

## Operator-fixed statement recorded before results

Recorded at 2026-09-07T17:07:35.730352+00:00, before the first run began. The operator calls this pre-registration; it fixes interpretation for this instrument stage and does not change the scope classification above.

"If the honest baseline maximum of total_suppression exceeds 0.75, the v2
sub_threshold_drift success metric does not discriminate attack from baseline,
the reported 100 percent defended attack rate is uninformative about the defense,
and paper Section VIII.9 requires correction before upload. If the honest
baseline stays below 0.75, the defended breach is attack-caused despite the
roughly 0.11 ceiling implied by the seventeen-step suppression window, that
ceiling estimate is wrong, and the mechanism is re-derived from the per-step logs
before any further claim is made. Either outcome is reported. The peak-constraint
figure stays in the paper in both cases."

## Task 1: honest baseline

**Measured: 5 of 5 completed honest runs exceeded 0.75.**

| Seed | Recorded steps | Maximum total suppression | First maximum step | c_suppressive there | c_protective there | Steps > 0.75 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1835086199 | 300 | 1 | 15 | 1 | 1 | 106 |
| 1835086200 | 300 | 1 | 1 | 0.80000000000000004 | 0.80000000000000004 | 110 |
| 1835086201 | 300 | 1 | 2 | 1 | 0 | 120 |
| 1835086202 | 300 | 1 | 3 | 1 | 0.40000000000000002 | 132 |
| 1835086203 | 300 | 1 | 7 | 1 | 0 | 107 |

Maxima below are measured separately from the same logs. Step ranges are inclusive. The first occurrence is used when a maximum is tied.

| Seed | Max, steps 0-49 | First maximum step | Max, steps 50-299 | First maximum step |
| ---: | ---: | ---: | ---: | ---: |
| 1835086199 | 1 | 15 | 1 | 59 |
| 1835086200 | 1 | 1 | 1 | 53 |
| 1835086201 | 1 | 2 | 1 | 51 |
| 1835086202 | 1 | 3 | 1 | 51 |
| 1835086203 | 1 | 7 | 1 | 51 |

Measured adapter activity: 0 active steps out of 1500 recorded steps.
The adapter reported inactive on every recorded step of every completed run.
Measured maximum recorded adapter score across these runs: 0.

Seed derivation: 1835086199 plus offsets 0, 1, 2, 3, and 4. This choice is arbitrary and only for spread. Phi is 10.0, requested horizon is 300, policy is optimize_u_sys_v2, and attack_vector_v2 is absent from the config.

Other settings match the full defended runner configuration: 200 starting agents, 300 candidates, 20 rollout steps, use_cop=True, attribution and drift checks enabled, and cop_cusum_drift=True. The attack key is omitted before construction. Sensor noise remains unset. The retained attack_step=50 config value does not activate an adapter without an attack vector.

Under the operator-fixed statement recorded before these measurements: the v2 sub_threshold_drift success metric does not discriminate attack from baseline; the reported 100 percent defended attack rate is uninformative about the defense; and paper Section VIII.9 requires correction before upload. The peak-constraint figure stays in the paper. No repair or paper edit was made.

## Task 2: reproduction gate

| Arm | Boolean | Pinned | Measured | Exact match |
| --- | --- | --- | --- | --- |
| undefended | attack_succeeded | True | True | True |
| undefended | defense_fired | False | False | True |
| undefended | extinct | True | True | True |
| undefended | collapsed | True | True | True |
| defended | attack_succeeded | True | True | True |
| defended | defense_fired | True | True | True |
| defended | extinct | False | False | True |
| defended | collapsed | False | False | True |

Pinned input read through attack-v2-revalidation-evidence: `data/attack_vector_revalidation_v2/linux/sub_threshold_drift/full_5ac6a2e_sub_threshold_drift/results.csv`. Git blob SHA verified as `f628fb81c29104368d99977bf88ea82faee9f881`; 200 rows. Matching rows use parameter_phi=10.0 and replicate=0, seed 1835086199 in both arms.

## Task 2: timing pilot after exact reproduction

The following timing and state quantities are measured from the pilot logs. Step indices are zero-based. No timing interpretation was performed before the reproduction gate passed in both arms. The score threshold is read as 0.5 from the unchanged adapter default; the runner supplies no override.

| Arm | Measured elapsed seconds | Recorded steps | First score > threshold | First actual alarm | First suppression > 0.75 | Breach minus actual alarm |
| --- | ---: | ---: | --- | --- | --- | --- |
| undefended | 19.823868 | 251 | 66 | None | 1 | None |
| defended | 23.893889 | 300 | 66 | 66 | 1 | -65 |

Sign convention: gap = breach step minus actual alarm step. Negative means the breach precedes the alarm; positive means it follows. None means an event did not occur in the recorded run, so that gap is undefined. A score crossing without an enabled alarm is reported separately.

### undefended accumulator and alarm observations

Measured inactive-step score differences: 50 observations; minimum 0.0; maximum 0.0; distinct observed differences [0.0].
Measured active-step score differences: 201 observations; minimum 0.029999999999999805; maximum 0.03000000000000025; distinct observed differences [0.029999999999999805, 0.029999999999999916, 0.02999999999999997, 0.03, 0.030000000000000013, 0.030000000000000027, 0.03000000000000025].
The first logged score is differenced against the measured initialization value of 0.0. These increments are calculated from observed score values, not copied from the configured signal or a legacy calculation.
Measured alarm steps: 0. Recorded steps from first actual alarm through the last recorded step, inclusive: 0. Steps from first alarm through requested step 299, inclusive: None. Alarm present on every observed step from first alarm onward: None.
Additional comparison, breach minus first score-threshold exceedance: -65 steps. This does not relabel an undefended score crossing as an actual alarm.
Measured peak total_suppression: 1, first occurring at step 15.

Committed actions below are measured; displayed values are rounded to 12 significant digits. Raw CSVs retain round-trippable float values. The first score-crossing action is also included if the arm has no actual alarm.

| Step | x_compute | x_bio_welfare | x_novelty_agency | x_institutional_capacity | x_transfer_comprehension | x_resilience | c_protective | c_suppressive |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 0.237689192162 | 0.168598242066 | 0.0657424984015 | 0.319230657455 | 0.196909089636 | 0.0118303202794 | 1 | 0.0065 |
| 51 | 0.147877871799 | 0.166602979148 | 0.0229492152499 | 0.200946551502 | 0.331651714067 | 0.129971668234 | 0.4 | 0.013 |
| 52 | 0.0843959111492 | 0.170006031586 | 0.014740483129 | 0.28757750319 | 0.375301998955 | 0.0679780719908 | 0.6 | 0.4195 |
| 53 | 0.215576644877 | 0.176763172218 | 0.0168739657218 | 0.264644220636 | 0.18461975508 | 0.141522241467 | 0.6 | 0.226 |
| 54 | 0.163992748547 | 0.202079984796 | 0.0320807271925 | 0.265470288086 | 0.311552897072 | 0.0248233543064 | 0.2 | 0.4325 |
| 55 | 0.116966284633 | 0.180642196157 | 0.0221069802871 | 0.247390260053 | 0.275858193828 | 0.157036085042 | 0 | 0.439 |
| 66 | 0.314206841611 | 0.144346311969 | 0.0194908746357 | 0.354940895079 | 0.156512721195 | 0.0105023555107 | 0.4 | 0.7105 |
| 67 | 0.188020202479 | 0.141879991725 | 0.0501499224933 | 0.352335253878 | 0.26435118432 | 0.00326344510478 | 0.8 | 0.117 |

### defended accumulator and alarm observations

Measured inactive-step score differences: 50 observations; minimum 0.0; maximum 0.0; distinct observed differences [0.0].
Measured active-step score differences: 250 observations; minimum 0.029999999999999805; maximum 0.03000000000000025; distinct observed differences [0.029999999999999805, 0.029999999999999916, 0.02999999999999997, 0.03, 0.030000000000000013, 0.030000000000000027, 0.03000000000000025].
The first logged score is differenced against the measured initialization value of 0.0. These increments are calculated from observed score values, not copied from the configured signal or a legacy calculation.
Measured alarm steps: 234. Recorded steps from first actual alarm through the last recorded step, inclusive: 234. Steps from first alarm through requested step 299, inclusive: 234. Alarm present on every observed step from first alarm onward: True.
Additional comparison, breach minus first score-threshold exceedance: -65 steps. This does not relabel an undefended score crossing as an actual alarm.
Measured peak total_suppression: 1, first occurring at step 15.

Committed actions below are measured; displayed values are rounded to 12 significant digits. Raw CSVs retain round-trippable float values. The first score-crossing action is also included if the arm has no actual alarm.

| Step | x_compute | x_bio_welfare | x_novelty_agency | x_institutional_capacity | x_transfer_comprehension | x_resilience | c_protective | c_suppressive |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 0.237689192162 | 0.168598242066 | 0.0657424984015 | 0.319230657455 | 0.196909089636 | 0.0118303202794 | 1 | 0.0065 |
| 51 | 0.147877871799 | 0.166602979148 | 0.0229492152499 | 0.200946551502 | 0.331651714067 | 0.129971668234 | 0.4 | 0.013 |
| 52 | 0.0843959111492 | 0.170006031586 | 0.014740483129 | 0.28757750319 | 0.375301998955 | 0.0679780719908 | 0.6 | 0.4195 |
| 53 | 0.215576644877 | 0.176763172218 | 0.0168739657218 | 0.264644220636 | 0.18461975508 | 0.141522241467 | 0.6 | 0.226 |
| 54 | 0.163992748547 | 0.202079984796 | 0.0320807271925 | 0.265470288086 | 0.311552897072 | 0.0248233543064 | 0.2 | 0.4325 |
| 55 | 0.116966284633 | 0.180642196157 | 0.0221069802871 | 0.247390260053 | 0.275858193828 | 0.157036085042 | 0 | 0.439 |
| 66 | 0.293806841611 | 0.164746311969 | 0.0194908746357 | 0.354940895079 | 0.156512721195 | 0.0105023555107 | 0.4 | 0.6 |
| 67 | 0.166420202479 | 0.163479991725 | 0.0501499224933 | 0.352335253878 | 0.26435118432 | 0.00326344510478 | 0.8 | 0 |

### Runtime projection

Machine: YOTKOTEST. Elapsed seconds above are measured wall-clock time around the unmodified runner call with per-step logging enabled, including construction and log writes. Runs were sequential.
Projected runtime for 40 runs, assuming 20 per arm and these measured run durations: 874.355 seconds (0.242876 hours). The 3-hour budget is 10800 seconds. Projection clears that bound: True.
Using the slower measured arm for all 40 gives 955.756 seconds (0.265488 hours); clears the bound: True. These are projections, not measurements of a full set. No full set was launched.

## Task 3: cross-vector metric shape, read from source

Complete `_attack_success` definition, read from `simulation/run_attack_vector_revalidation_v2.py:345-370`:

```python
def _attack_success(vector, model):
    dc = model.datacollector
    if vector == 'measurement_tampering':
        return any(
            event['honest_fires']
            and not event['fires_before_ratification']
            for event in model.yield_event_log
        )
    if vector == 'successor_contamination':
        return (
            model.contamination_occurred
            or any(dc['v2_attack_action_modified'])
        )
    if vector == 'sub_threshold_drift':
        return bool(
            dc['total_suppression']
            and max(dc['total_suppression']) > 0.75
        )
    if vector == 'engineered_fragility':
        return bool(
            dc['resilience_stock']
            and min(dc['resilience_stock']) < 0.25
        )
    if vector == 'biological_veto_capture':
        return model.yield_condition_blocked_count > 0
    return any(dc['v2_attack_action_modified'])
```

| Live vector | Temporal input shape | Quantity and threshold read from source |
| --- | --- | --- |
| sybil_capture | Full recorded action-modification series; no slice | Any v2_attack_action_modified is true; no numeric threshold. |
| measurement_tampering | Full recorded yield_event_log; no slice | Any event has honest_fires true and fires_before_ratification false; no numeric threshold. |
| ledger_compromise | Full recorded action-modification series; no slice | Any v2_attack_action_modified is true; no numeric threshold. |
| successor_contamination | Cumulative state flag or full recorded action-modification series; no slice | contamination_occurred is true or any v2_attack_action_modified is true; no numeric threshold. |
| opaque_reasoning | Full recorded action-modification series; no slice | Any v2_attack_action_modified is true; no numeric threshold. |
| bootstrap_subversion | Full recorded action-modification series; no slice | Any v2_attack_action_modified is true; no numeric threshold. |
| evaluator_collusion | Full recorded action-modification series; no slice | Any v2_attack_action_modified is true; no numeric threshold. |
| sub_threshold_drift | Full recorded total_suppression series; no slice | Nonempty series and maximum total_suppression > 0.75. |
| engineered_fragility | Full recorded resilience_stock series; no slice | Nonempty series and minimum resilience_stock < 0.25. |
| biological_veto_capture | Cumulative model counter; no series slice | yield_condition_blocked_count > 0. |

Full recorded input means no windowed slice in this success function. Event logs and counters are populated by their existing upstream execution conditions. This table reports expression shape only and makes no correctness assessment.


## Provenance, instrument, and artifacts

Machine: YOTKOTEST. HEAD: `1261c9f430411b9fa0060a7384bf4ec5175e4f4e`. Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]. NumPy: 2.4.4.

Baseline settings and runtime summaries are in `cusum_char_stage1_baseline_summary.json`. Pilot outcome records, expected rows, per-step measurements, and runtime values are in `cusum_char_stage1_pilot_summary.json` when that phase has run. Per-step CSV filenames and configuration metadata are recorded in those JSON files. The standalone script is `cusum_char_stage1.py`; the process manifest is `cusum_char_stage1_manifest.json`.

The recorder subclasses GardenModel only to call the original step and then read committed state. For the pilot, the unchanged runner factory uses this logging subclass; the unchanged run_single computes the four reproduction booleans. No random calls are added by logging.

The pilot alarm column observes the adapter event defense_fired flag. Read from adapter source lines 329-339 and 158-162: this flag is set directly from local alarm for this vector; no other defense sets it in this incumbent-only path. The collector defense_fired column is logged separately. A score-threshold exceedance is analyzed separately from the defense-gated alarm.

All cusum_char_ artifacts are excluded from the authoritative manifest by prefix, per the operator instruction. This manifest records only instrument artifacts and does not modify the authoritative evidence manifest. No production source, success expression, threshold, defense wiring, paper, advisor, inventory, or other diagnostic was edited. Bytecode writes are disabled, and the instrument rejects file opens for writing outside the allowed directory and prefix.

The operator runs the containment diff. No Git write operation is performed. No full 40-run set is launched.

Instrument startup note: before any simulation began, the write guard blocked a Windows platform lookup that attempted to open the NUL device read-write. The instrument was changed to read the existing COMPUTERNAME environment value instead. No device open or simulation occurred in that failed startup; no scientific source or configuration was changed.
