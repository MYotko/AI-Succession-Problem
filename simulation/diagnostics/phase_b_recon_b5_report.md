# Phase B reconstruction attempt 5 validation

The attempt 4 executor was kept and repaired. This is a reimplementation, not a rerun. Validation is non-registered and may not be cited as evidence for any registered quantity or fidelity target.
Measured runs launched: 0. Unique smoke runs: 40. Additional determinism repeat runs: 2. Two interrupted attempts restarted from step 0; their partial evidence is retained.

| Check | Demonstrated | Evidence |
| --- | --- | --- |
| 1. Both substrates and pinned HEADs | Yes | 20 runs per substrate; HEADs 1a5fa6505fa079906b2df2a97e1f965b3e0f8713 and 2044f50a8cf71874f259e74fd05ec495169b9ae4 match. |
| 2. Required recorded fields and types | Yes | 40 rows; all 18 required fields correctly typed. |
| 3. Computed and nonconstant fields | Yes | Recomputed from step logs; unique values {"final_ai_generation": [1, 2, 3], "survived": [false, true], "yield_fired": [false, true]}. |
| 4. Repeat determinism | Yes | One repeat per substrate; recorded fields excluding elapsed time/PID and all step hashes match. |
| 5. Worker termination and resume | Yes | 2 preserved, 2 restarted, 36 never launched at resume; completed-record content hashes unchanged on verification resume; preserved jobs never relaunched. |
| 6. Merge recovery | Yes | 40 run rows and 12000 step rows recovered with matching hashes. |
| 7. Worker settings honored | Yes | Requested/actual peak workers: [[2, 2], [8, 8]]. |
| 8. Matched substrate differences | Yes | 20 of 20 matched cell/seed pairs differ on required scientific fields. |

No scientific parameter was adjusted using smoke outputs. Test results are reported without fidelity interpretation.

## Operational checks

Full-grid assertions: A 2,700, B 2,800, C 1,620, phi 420 per substrate; 7,540 per substrate, 15,080 total. Smoke: 20 per substrate, 40 total.
A worker was terminated after completed steps were recorded. The parent stopped remaining workers and retained complete records and partial logs. Resume preserved work mode, then applied normal mode without changing seeds.
The final executor streams its merge. Synthetic checks covered initial merge, adding a second substrate, and repeat merge with identical hashes. The final executor resumed the completed smoke batch without launching another model.
AST comparisons confirmed that the streaming repair left the worker, grid, recorder helpers and prior global assignments unchanged. Original completions retain their actual executor hash; the manifest records compatible versions and source snapshots.
Every completed worker verified one OpenBLAS thread through its exported getter. Numerical-library environment variables were also set to one. Imported project modules were verified against their selected worktree.

## Timing

| Substrate | Mean recorded seconds per run |
| --- | ---: |
| v20 | 90.66294694000389 |
| v21 | 107.7183212050004 |

| Ideal workers | Projected full-batch hours |
| --- | ---: |
| 8 | 51.93731811851848 |
| 12 | 34.624878745678984 |
| 16 | 25.96865905925924 |

7540 * (mean v20 seconds + mean v21 seconds) / workers; excludes startup and merge overhead; assumes smoke timing represents the full grid.
Recorded elapsed time covers model construction and stepping, excluding interpreter startup, imports and merging. These are linear operational estimates.
YotkoTest CPU budget: 16. Normal mode caps active workers at 15; work mode caps them at 12. A request for 16 therefore uses at most 15, projected at 27.69990299654319 hours. No operating-system CPU reservation is claimed.

## Operator commands

Run from C:/Users/matty/Dev/AI-Succession-Problem. These measured-batch commands were not executed during validation.

```powershell
python -B simulation/diagnostics/phase_b_recon_executor.py --workers 8 --category A B C phi --substrate both --v20-worktree "C:/Users/matty/Dev/phase-b-recon-v20"
```

Resume:

```powershell
python -B simulation/diagnostics/phase_b_recon_executor.py --workers 8 --category A B C phi --substrate both --v20-worktree "C:/Users/matty/Dev/phase-b-recon-v20" --resume
```

## Progress and runtime control

Progress: simulation/diagnostics/phase_b_recon_progress.json. While running, the timestamp updates every two seconds, within the 30-second requirement. Completed/running/pending counts reconcile to the selected grid per category and substrate. Completed increases, pending decreases, and running becomes zero at complete or stopped status. Elapsed time is for the current invocation; the mean uses completed records.
Full-batch control: simulation/diagnostics/phase_b_recon_runtime_control.json. Set mode to work or normal to change the cap. Existing jobs finish during a reduction, and mode persists on resume. The smoke control file is separate under phase_b_recon_smoke_.
Keyboard interruption or a terminated worker leaves durable completions and partial files for --resume. Completed categories resume from verified merged records. Incompatible code or source identity is rejected.

## Construction fixed before tests

Unvaried parameters retain production defaults: phi 25, alpha 1, successor capability 1. The initial successor is generation 2. Peak population is the maximum recorded population. Survival uses 0.65 without integer truncation. Collapsed means positive final population below that threshold; extinct means zero. Knowledge transfer follows Amendment 1.

## Provenance and fixes

T0 passed. The five pins matched at initial and final readings. The v20 worktree was read only. Both substrate snapshots and imported-module hashes are recorded. Committed halt artifacts were unchanged.
The write guard was updated to the corrected whole-prefix scope, including temporary files, with committed-file exclusions.
Tool-layer workaround: Extracted the JSON line from shell output after a leading tool warning prevented JSON parsing; repeated read-only T0 commands.
Tool-layer workaround: Used command-scoped safe.directory after Git rejected the operator-owned v20 worktree; no Git configuration changed.
Tool-layer workaround: Constructed Markdown fences from character codes after literal backticks caused a JavaScript tool-payload parse error.
Executor self-fix: Gave repeat probes their own console filenames so they cannot overwrite a normal run console.
Executor self-fix: Replaced the validation controller PID kill with a minimal-rights Windows process handle after os.kill returned access denied.
Executor self-fix: Streamed category merging and hash verification to bound memory, preserving prior completions from the verified identical worker code.
Executor self-fix: Compared canonical completion content across a no-work resume because merging changes JSON key order; reused completed repeat probes.
