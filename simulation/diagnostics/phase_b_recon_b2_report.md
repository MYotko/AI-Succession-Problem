# Phase B reconstruction executor validation, attempt 2: halted

T0 passed. The corrected test grid contains 20 runs per substrate and 40 total.
No executor was built, no v20 worktree was created, and no test or measured run was launched.

Pinned v20 worktree creation failed three times: Git could not create leading directories of '.git/worktrees/phase-b-recon-v20': Permission denied.

| Required check | Status and evidence |
| --- | --- |
| 1. Substrate HEADs | Not tested. v21 HEAD is 6c3bcb60ec9496adca8cd1f0d56e4950c8de2532; pinned v20 worktree creation failed. |
| 2. Recorded fields and types | Not tested; no rows produced. |
| 3. Live outcome fields | Not tested; no rows produced. |
| 4. Determinism | Not tested. |
| 5. Interruption and resume | Not tested; zero test runs launched. |
| 6. Merge and hashes | Not tested; no run artifacts produced. |
| 7. Two worker settings | Not tested; zero workers launched. |
| 8. Substrate differences | Not tested. |

Mean seconds per run for v21 and v20 are unavailable.
Full-batch wall-clock projections at 8, 12, and 16 workers are unavailable.
Full-batch launch and resume commands are unavailable because the executor was not built or validated.

The failed prerequisite command, from the repository, is:

    git worktree add --detach C:/Users/matty/Dev/phase-b-recon-v20 2044f50a8cf71874f259e74fd05ec495169b9ae4

The planned progress file is simulation/diagnostics/phase_b_recon_progress.json. It was not created.
A healthy future reading would update at least every 30 seconds, include completed, running and pending counts per category and substrate, elapsed time, and a mean seconds-per-run estimate.

Tool-layer workaround 1: Retried worktree creation using an explicit git -C repository path; the same permission error remained.
Tool-layer workaround 2: Retried the original worktree command; the third identical failure triggered the tool-layer halt rule.
Executor self-fixes: none.
