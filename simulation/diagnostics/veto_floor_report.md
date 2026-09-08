# Veto ratification floor characterization

This is characterization of a known-defective measurement. These outputs are not registered characterization data, are not framework evidence, and do not cross the pre-registration boundary.

**Status: HALTED after the reproduction gate passed. No floor-arm runs started.** During validation of the authorized snapshot prefix edit, the existing snapshot Git helper attempted a writable open of the Windows NUL device outside the permitted artifact prefix. The write guard rejected the open. The task requires a halt on any such attempt, so Tasks 2 through 4 were not executed.

The helper uses `subprocess.DEVNULL` at `scripts/generate_project_knowledge_snapshots.py:133,137`. The installed Python implementation of `subprocess.Popen._get_devnull` calls `os.open(os.devnull, os.O_RDWR)`. The helper catches exceptions at lines 140-142, emitted `WARNING: git introspection failed; using placeholder values`, and continued with commit and branch both `unknown`. Its printed dry-run completion is not a successful validation. No separate guard traceback was retained because the helper swallowed the exception; the rejected open was identified by reading these sources. No retry, exemption for NUL, or helper repair was attempted.

## Preconditions

All four preconditions passed before simulation execution. The initial HEAD was `84943819db1de028f6ef7d26f6926756856a1351`. During preparation, the operator advanced HEAD to the allowed descendant below; the gates were checked again before the reproduction. That commit changed only `docs/v2_0_instrument_validation_record.md` and `essays/site-update-2026-09-07-instrument-correction.md`.

| Gate | Result | Recorded evidence |
| --- | --- | --- |
| HEAD is 8494381 or a descendant | PASS | Execution HEAD `dc1b7c4567cbf194f9bf893f7f2a5d66681683bb`; `git merge-base --is-ancestor 8494381 HEAD` returned 0. |
| Root advisor exists and is unindexed | PASS | `LINEAGE_IMPERATIVE_ADVISOR.md` present; `git ls-files --error-unmatch -- LINEAGE_IMPERATIVE_ADVISOR.md` returned 1. |
| Runner validator settings | PASS | `simulation/run_attack_vector_revalidation_v2.py:315` reads `'n_validators': 5,`; line 316 reads `'base_validator_accuracy': 0.8,`. |
| Sole v2-reachable blocked-count increment | PASS | `simulation/attack_adapter_v2.py:435`. Source search also found the legacy increment at `simulation/model.py:838`; `model.py:702-704` returns through `_step_v2` before it. The v2 call is at `model.py:1351-1356`, with the increment in `attack_adapter_v2.py:433-437`. `model.py:351` initializes the counter. |

## Authoritative input and row selection

The manifest was `simulation/diagnostics/attack_vector_revalidation_manifest.md`, SHA256 `e69c75747567aa0758049014c954b7a60be590876fb9bb3f65dc431da2c8a103`. Its four biological-veto entries selected the exact result directories below. No glob selected the evidence. Each file was read through `attack-v2-revalidation-evidence`, which peeled to `6d33c905db18842f68e59b4148f65c5e6a1a62a3`. Git blob hashes of the retrieved bytes were verified before CSV row parsing. Row counts below were counted in Python with `csv.DictReader`, excluding the header. All hashes and row counts matched the manifest.

| Manifest line | CSV path | Counted rows | Verified Git blob SHA |
| --- | --- | ---: | --- |
| 26 | `data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard0of4/results.csv` | 2164 | `3334d7b4ffcac08c708ac3e43f48c4efeb38e9a2` |
| 27 | `data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard1of4/results.csv` | 2102 | `4d6c83821bad99368bd94c6b1469202d2ca51bb9` |
| 28 | `data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard2of4/results.csv` | 2321 | `330369c806bc1db05ceb385afe177fe8d252c63a` |
| 33 | `data/attack_vector_revalidation_v2/linux/biological_veto_capture/full_5ac6a2e_veto_shard3of4/results.csv` | 2113 | `a790f7569e6a27581a2ef78424376d0bf108743f` |

Selection rule: Lowest replicate across defended rows with defense_mode=both; ties by authoritative manifest order, then CSV data-row order. The selected file was `data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard0of4/results.csv`, data row 367 excluding the header. It is defended, `defense_mode='both'`, replicate 0, seed 594254024. The pinned `machine='laptop'` label was retained in the task; the actual execution machine was YOTKOTEST.

## Reproduction gate

The unmodified runner factory `run_attack_vector_revalidation_v2._make_model(task)` constructed the model. The harness then used the model's own step loop and the runner's existing collapse expression. No production function was patched or replaced.

| Required quantity | Pinned | Measured reproduction | Exact match |
| --- | ---: | ---: | --- |
| `yield_condition_met_count` | 1 | 1 | PASS |
| `yield_condition_blocked_count` | 0 | 0 | PASS |
| `extinct` | false | false | PASS |
| `collapsed` | false | false | PASS |

All four comparisons passed. Measured steps completed: 300; final population: 465; final validator dependency mean and maximum: 0.0 and 0.0. Measured elapsed time: 72.149484 seconds. The complete reproduction record is in `veto_floor_reproduction.json`.

Constructed configuration, read from the factory-created model:

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

Runner settings: full mode, 300 requested steps, 300 candidates, and 20 rollout steps. The selected cell uses `defense_mode=both`, capture strength 1.0, dependency rate 0.05, and rotation interval 10. The factory constructed phi 25.0.

## Floor-arm status

ZERO_STRENGTH, ZERO_DEPENDENCY, and AS_PUBLISHED were not started. The planned 40 seed-paired replicates per arm remain unexecuted. The selected reproduction is stored separately and is not a floor-arm observation.

`veto_floor_runs.csv` contains the requested header and zero data rows, counted with Python `csv.DictReader`. No pooled rates, per-run rate means, standard errors, paired differences, or comparisons with the operator-supplied reference values were computed. Yield-event and zero-denominator sufficiency gates cannot be assessed without the floor arms.

## Runtime and source provenance

Machine: `YOTKOTEST`. Execution HEAD: `dc1b7c4567cbf194f9bf893f7f2a5d66681683bb`. Python: `3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]`. NumPy: `2.4.4`.

Actual worker count: one worker for the serial prerequisite reproduction; zero floor workers. The standing normal CPU budget would allow 15 workers from the operator's 16-core allocation, but the floor pool was never launched. OpenBLAS reported one effective thread through its runtime getter. The six numerical-library thread environment variables and the runtime library path are recorded in the reproduction JSON.

SHA256 values below were recorded for every loaded simulation Python module touched by the reproduction, including the diagnostic harness. They matched the preparation source catalog.

| Source module | SHA256 |
| --- | --- |
| `simulation/agents.py` | `d5bad24dc9dafb6e4d374c0ff68b74c73f24a41fbef3a6ddcaa75f8ec6d408d5` |
| `simulation/attack_adapter_v2.py` | `e4dd5a436ab33b348691b8c777608a655147610603181705694dcb3b2c35dcfe` |
| `simulation/constants_v2_stage15.py` | `808ac150f51ae33acbbc326e108451e9ac9d54b3c0f4ccc7adc537c58254cc70` |
| `simulation/constants_v2_stage18.py` | `68c3c8fd29c451079496b9e44b2fe5892932cf1b431358ad549f45419a15873d` |
| `simulation/defection.py` | `20466e6fd4a592f24c5c6fe07a40bc683b243b3939e3b69a94a1fcfc4ae269dd` |
| `simulation/diagnostics/veto_floor_worker.py` | `3c27502436bf976385baabf0500587252ce228b81f7698e01f12fac73bb3540e` |
| `simulation/metrics.py` | `536a77fb5e45d6d167480ab7af6ea9f5a0e56b9927be0d09713400aa873fae63` |
| `simulation/model.py` | `a4e5e95a49cea534cd02c8f412981797fd6dfa0e6c8de77aa3d5a6aa31f37c67` |
| `simulation/run_attack_vector_revalidation_v2.py` | `da7913799d0d4e11f52f770e313875764d27b20ad33157a7aa9c1fa00df418e2` |
| `simulation/working_factor.py` | `0afde923081fe34d1ada86e2928286d45c905441053f643968ea9b13007b683d` |

## Snapshot prefix edit and write containment

The task's final sentence explicitly authorized adding `veto_floor` to the snapshot prefix filter. That was treated as a narrow exception to the earlier general write restriction. The only authorized edit outside the artifact prefix was at `scripts/generate_project_knowledge_snapshots.py:89`:

```python
NEVER_INGEST_BASENAME_PREFIXES = ("cusum_char_", "veto_floor")
```

The previous value was `NEVER_INGEST_BASENAME_PREFIXES = ("cusum_char_",)`. Line endings were preserved. Source SHA256 before: `76490d662e2ddbd5af911d9c90cc0763b608c1d3535bee49aee9b8994cacd73c`; after: `821a4eb8e0754e4f06d1348d68099b0f123a747a8ff7f72a26087042ec2c6efc`.

The actual dry-run and collector output selected no `veto_floor` artifacts in any collector group. However, the writable NUL open described above makes the overall validation HALTED. The collector results do not override that halt. The stdout transcript is `veto_floor_snapshot_dry_run.txt`; the warning and source-based diagnosis are recorded in `veto_floor_snapshot_check.json`. No authoritative snapshot was generated.

Bytecode writes were disabled. The Python write guard rejected the out-of-scope writable open before it completed. No floor run or workaround followed the halt. No Git write operation, production simulation edit, runner edit, or paper edit was performed. The operator retains the containment diff responsibility.

## Artifacts

`veto_floor_manifest.json` enumerates the outputs, their SHA256 values, and CSV row counts. Non-CSV row counts are null. Its own hash is supplied separately in the completion message to avoid a self-referential digest. `veto_floor_plan.json` is the preparation record; pending statuses in that record describe preparation time and are superseded by this halt report and the final manifest. These artifacts are not authoritative framework evidence.

Stopped after recording the halt. No floor measurement or interpretation is reported.
