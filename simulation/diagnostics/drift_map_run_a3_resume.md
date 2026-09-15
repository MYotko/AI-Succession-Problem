# Attempt 3 resumption after reboot

Status: interrupted at the operator's request. All worker processes exited.

Completed runs: 263. Remaining runs: 97. Work mode is retained at 12 workers.

The completed records were validated for identity, configuration, raw-log SHA256, row count, seed, arm, and step sequence. Partial logs remain partial and do not count as completed runs.

Restart the interrupted R05 runs from their original seeds: 1835086222, 1835086223, 1835086224, 1835086225, 1835086226, 1835086227, 1835086228, 1835086229, 1835086230, 1835086231, 1835086232, 1835086233. Their partial logs are preserved. No seed has been resumed yet.

From `C:/Users/matty/Dev/AI-Succession-Problem`, run these commands in order:

```powershell
python -B simulation/diagnostics/drift_map_run_a3_executor.py control --mode work
python -B simulation/diagnostics/drift_map_run_a3_executor.py batch
```

Continue this attempt using its existing plan, executor, and passed T1 gates. Do not recreate the plan or rerun the fresh-namespace gate. The runner verifies source pins, validates and skips completed jobs, and records resumed seeds. The first command clears the interruption request and preserves work mode.

After all 360 runs are complete:

```powershell
python -B simulation/diagnostics/drift_map_run_a3_analyze.py
```

T3 has not been executed. No A1 through A6 results have been computed.

No CUSUM allowance, threshold, or alarm rule was chosen or run. The production adapter accumulator score was recorded only, with cop_cusum_drift false. No attack-success rate or corrected figure was derived. H_ref is a candidate and is not frozen. Nothing here is comparable to any pre-repair measurement.
