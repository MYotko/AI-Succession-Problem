# Phase B reconstruction attempt 3

Status: halted after T0 and committed-source review, before implementation.
Smoke runs launched: 0. Measured runs launched: 0. No executor was created.

## Halt reason

The required per-run transfer_verified_fraction has no computation defined in Section 5 or in the committed consuming script. The surviving transfer verification references describe a Boolean knowledge_transfer_verified or aggregate fractions, not this per-run field. Choosing a numerator, denominator, threshold, time basis, or no-succession value would require clarification. The dispatch requires a halt where a question would otherwise be necessary.

Section 5 names the required field but supplies no per-run definition. The committed consuming script does not read it. The existing Boolean examples use different time bases: final transfer allocation in part_ix_draft.md:235 and maximum transfer allocation in patient_defection_sweeps.py:361. Neither establishes the required per-run fraction. No formula was selected and no output was inspected to select one.

## Requested validation checks

| Check | Requirement | Evidence |
| --- | --- | --- |
| 1 | Both substrates and HEADs | Not run. Read-only HEAD checks match v21 52de0f9055d1c384866d5badcef6b64956eabbb0 and v20 2044f50a8cf71874f259e74fd05ec495169b9ae4. |
| 2 | Recorded field types | Not run. Blocked by undefined per-run transfer_verified_fraction. |
| 3 | Live survival, yield, generation fields | Not run. No model was constructed or stepped. |
| 4 | Determinism | Not run. |
| 5 | Kill and resume | Not run. Preserved 0, restarted 0, never launched 40 smoke runs. |
| 6 | Merge count and hash recovery | Not run. No run rows exist. |
| 7 | Two worker settings | Not run. Active simulation workers: 0. |
| 8 | Matched substrate differences | Not run. No scientific outputs exist. |

## Timing, launch, and progress

Mean test seconds per run: unavailable for both substrates; no runs launched.
Full-batch wall-clock projections at 8, 12, and 16 workers: unavailable without test measurements.
No runnable launch or resume command is supplied because the executor has not been built or validated.
The intended progress path is simulation/diagnostics/phase_b_recon_progress.json; it was not created. For a future implemented runner, healthy progress requires current timestamps no more than 30 seconds apart while active, completed/running/pending counts per category and substrate that reconcile to the selected grid, and completed counts advancing.

## Provenance

T0 passed. Every pinned source matched at the initial and final readings. Both readings are in the preflight and manifest.
The operator-owned v20 worktree was read only and its HEAD matched the pin.
Known warning observed: permission denied reading the global Git ignore file. CRLF was observed in the three pinned production modules.

## Operational record

Tool-layer workaround: Used a command-scoped safe.directory setting for the operator-owned v20 worktree after Git rejected its ownership; no Git configuration file was changed.
Executor self-fixes: none.

This halt report contains no scientific result or fidelity ruling.
