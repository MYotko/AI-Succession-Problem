# Veto ratification floor characterization, Run 2

This characterizes a known-defective measurement. These outputs are not registered characterization data, are not framework evidence, and do not cross the pre-registration boundary.

Status: complete. All 900 floor runs completed. The prior reproduction gate was carried forward without repeating it.

## Measurements

Counts below were counted from the recorded run CSV in Python with csv.DictReader, excluding the header. Rates and intervals were calculated from those counts. No per-run ratio was recorded or calculated.

| Arm | Runs | Total yield events | Total blocks | Pooled block rate | Wilson 95% interval | Mean yield events/run | Zero-yield runs |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| ZERO_STRENGTH | 300 | 325 | 25 | 0.076923077 | [0.052643757, 0.111086993] | 1.083333333 | 0 |
| ZERO_DEPENDENCY | 300 | 325 | 25 | 0.076923077 | [0.052643757, 0.111086993] | 1.083333333 | 0 |
| AS_PUBLISHED | 300 | 343 | 43 | 0.125364431 | [0.094419134, 0.164608316] | 1.143333333 | 0 |

Pooled rate = total blocks / total yield events. Wilson intervals use the two-sided standard normal 0.975 quantile and yield events as the binomial denominator.

| Arm | Measured pooled rate | Operator-supplied analytic reference |
| --- | ---: | ---: |
| ZERO_STRENGTH | 0.076923077 | 0.057920 |
| ZERO_DEPENDENCY | 0.076923077 | 0.057920 |

Seed-paired AS_PUBLISHED minus ZERO_STRENGTH per-run block-count difference: mean 0.060000000 blocks/run; paired standard error 0.015271603, from 300 pairs. The standard error is the sample standard deviation of the 300 paired block-count differences divided by sqrt(300).

All arm event totals were at least 250, and no arm had more than 30 zero-yield runs.

## Preconditions and configuration

- Gate 1: PASS. {"head": "2368660f2f97a2de7be4f18f6cb478e3424d044b", "merge_base_exit": 0, "number": 1, "passed": true}
- Gate 2: PASS. {"advisor_present": true, "git_ls_files_exit": 1, "number": 2, "passed": true}
- Gate 3: PASS. {"lines": {"315": "                'n_validators': 5,", "316": "                'base_validator_accuracy': 0.8,"}, "number": 3, "passed": true}

Prior reproduction record: `simulation/diagnostics/veto_floor_reproduction.json`, SHA256 `a6ac39eec9676b149878d58a4f43de268bb28c20dbe36f610f2f0361afc6ba79`. Its pass was accepted as instructed; it was not rerun.

Each cell used the unmodified runner factory and its own model step loop. The complete constructed configuration was checked against the saved reproduction for every run, allowing the seed and only the arm-specific field to change. All constructed configurations are retained in the per-run completion JSON files.

Base configuration from the saved reproduction (random_seed is replaced by each prescribed seed):

```json
{
  "attack_step": 50,
  "attack_vector_v2": "biological_veto_capture",
  "base_validator_accuracy": 0.8,
  "bootstrap_turn_step_v2": 20,
  "capture_strength": 1.0,
  "cop_cusum_drift": false,
  "cop_independence_monitoring": true,
  "cop_methodological_diversity": false,
  "cop_veto_capture": true,
  "dependency_rate": 0.05,
  "n_candidates_v2": 300,
  "n_validators": 5,
  "phi": 25.0,
  "policy": "optimize_u_sys_v2",
  "random_seed": 594254024,
  "reproduction_rate": 0.09,
  "rollout_steps_v2": 20,
  "rotation_interval": 10,
  "shock_magnitude": 0.15,
  "shock_step": 0
}
```

Task parameters remain defended with defense_mode both and rotation_interval 10. ZERO_STRENGTH changes capture_strength to 0.0; ZERO_DEPENDENCY changes dependency_rate to 0.0; AS_PUBLISHED changes neither. Each arm uses exactly seeds 700000000 through 700000299. Requested horizon: 300 steps; candidates: 300; rollout steps: 20. No seed function was used.

## Execution provenance

Machine: `YOTKOTEST`. HEAD: `2368660f2f97a2de7be4f18f6cb478e3424d044b`. Python: `3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]`. NumPy: `2.4.4`.

Actual maximum concurrent simulation workers: 15. Operator CPU budget: 16; normal cap: 15; work cap: 12. These are worker limits, not an operating-system core reservation. Elapsed batch time: 5243.645 seconds. Mode history and any resume events are retained in veto_floor2_progress.json.

All workers set the six numerical-library thread environment variables to one before importing NumPy. Each run verified one effective OpenBLAS thread through the runtime getter recorded in its completion JSON. Completed jobs were atomically saved after validation. Resumption validates exact job, seed, configuration, source identity, and thread limits before skipping a completed result.

SHA256 for every simulation Python module loaded by these runs:

| Module | SHA256 |
| --- | --- |
| `simulation/agents.py` | `d5bad24dc9dafb6e4d374c0ff68b74c73f24a41fbef3a6ddcaa75f8ec6d408d5` |
| `simulation/attack_adapter_v2.py` | `e4dd5a436ab33b348691b8c777608a655147610603181705694dcb3b2c35dcfe` |
| `simulation/constants_v2_stage15.py` | `808ac150f51ae33acbbc326e108451e9ac9d54b3c0f4ccc7adc537c58254cc70` |
| `simulation/constants_v2_stage18.py` | `68c3c8fd29c451079496b9e44b2fe5892932cf1b431358ad549f45419a15873d` |
| `simulation/defection.py` | `20466e6fd4a592f24c5c6fe07a40bc683b243b3939e3b69a94a1fcfc4ae269dd` |
| `simulation/diagnostics/veto_floor2_probe.py` | `d8c75d60ae641680f212bfb14f5b1c7a2d20b697eefffc497c4056c167e8b346` |
| `simulation/metrics.py` | `536a77fb5e45d6d167480ab7af6ea9f5a0e56b9927be0d09713400aa873fae63` |
| `simulation/model.py` | `a4e5e95a49cea534cd02c8f412981797fd6dfa0e6c8de77aa3d5a6aa31f37c67` |
| `simulation/run_attack_vector_revalidation_v2.py` | `da7913799d0d4e11f52f770e313875764d27b20ad33157a7aa9c1fa00df418e2` |
| `simulation/working_factor.py` | `0afde923081fe34d1ada86e2928286d45c905441053f643968ea9b13007b683d` |

## Write scope and artifacts

The write guard explicitly exempts os.devnull in any mode. All other writable opens are restricted to simulation/diagnostics/veto_floor2_ filenames. Bytecode writes were disabled. No other writable-open violation was recorded. No Git write operation was performed.

The prior task authorized a snapshot prefix edit. Run 2 supersedes that authorization. It is ignored here, and no snapshot operation is performed.

The snapshot generator was not run, validated, dry-run, or edited. Prior artifacts were retained. All new artifacts use the veto_floor2_ prefix. The manifest lists SHA256 and CSV row counts for outputs; non-CSV row counts are null. The manifest itself has no embedded self-hash because that would be self-referential; its exact digest is emitted separately on completion.

No corrected figure, published-number adjustment, or interpretation was computed. Stopped after this report.
