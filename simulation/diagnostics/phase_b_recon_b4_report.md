# Phase B reconstruction attempt 4 validation report

Status: halted during initialization. Smoke runs launched: 0. Measured runs launched: 0.

The executor atomic-write helper attempted to create phase_b_recon_progress.json.tmp.7300. The exhaustive scope permits phase_b_recon_progress.json, but not a temporary file with that name. The write guard rejected the attempt before file creation and before any worker launched. The explicit halt rule for any attempted write outside scope applies even to an executor defect.

The executor exists and parses, but is unvalidated. No measured batch was launched. The controller and child executor have exited. Existing committed halt artifacts were not modified.

## Requested validation checks

| Check | Requirement | Evidence |
| --- | --- | --- |
| 1 | Both substrates ran and HEADs match | HEADs verified: v21 20a6327a289b94fade04c915c6e38ff495cf3468; v20 2044f50a8cf71874f259e74fd05ec495169b9ae4. Neither substrate ran. |
| 2 | Required fields and types | Schema implemented and parsed; no rows exist to validate. |
| 3 | Survival, yield and generation liveness | Not tested; zero model runs. |
| 4 | Determinism | Grid and job assignment static checks passed; model repetition not tested. |
| 5 | Kill and resume | Not reached. Preserved 0, restarted 0, never launched 40. |
| 6 | Merge recovery and hashes | Implemented but not exercised. No run rows or step logs exist. |
| 7 | Two worker settings | Requested 2; actual peak 0. The 8-worker invocation was never launched. |
| 8 | Matched substrate differences | Source files and HEADs differ; scientific output comparison not run. |

## Grid checks

Static assertions succeeded: A 2,700, B 2,800, C 1,620 and phi 420 per substrate; 7,540 per substrate and 15,080 total. Smoke: 20 per substrate and 40 total.
Static scheduling checks succeeded for normal and work caps of 15 and 12 at CPU budget 16, and deterministic grid assignment. Runtime mode transitions were not tested.

## Timing and operator commands

Mean seconds per run: unavailable for v20 and v21 because no run launched.
Full-batch projections at 8, 12 and 16 workers: unavailable without smoke measurements.
No launch or resume command is approved by this validation. The executor is unvalidated and retains the defect that triggered the required halt. Do not launch a measured batch from this attempt.
The standing CPU budget caps normal mode at 15 active workers on YotkoTest; the implemented limit would cap a request for 16 at 15.

## Progress

Intended path: simulation/diagnostics/phase_b_recon_progress.json. It was not created.
A healthy running implementation would publish timestamps at least every 30 seconds, completed/running/pending counts per category and substrate summing to the selected grid, elapsed time and mean seconds per completed run, with completed counts advancing.
The smoke manifest records initial counts of 0 preserved, 0 restarted and 40 never launched.

## Source readings and definitions

T0 passed. All five pinned source hashes matched at initial and final readings. Both substrate source snapshots were rechecked at completion and were unchanged.
The amended knowledge_transfer_verified Boolean is implemented as specified. Unvaried parameters use production defaults phi=25, alpha=1 and successor capability=1; the initial successor is generation 2. These construction choices were made before any model run.
No scientific result or fidelity interpretation is reported.

## Operational record

Tool-layer workaround: Used command-scoped safe.directory after Git rejected the operator-owned v20 worktree; no Git configuration file changed.
Tool-layer workaround: Bounded a committed-source excerpt to the actual file length after the read helper raised IndexError.
Tool-layer workaround: Checked progress-file existence after a read found it absent; initialization had stopped before publishing it.
Executor self-fixes: none.
Executor defect, not repaired after the halt: the temporary progress filename fell outside the exhaustive write scope.
Known T0 warning: permission denied reading the global Git ignore file.
This report is a non-registered build and validation record.
